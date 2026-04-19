import os
import gspread
from google.oauth2.service_account import Credentials

from modules.logger_config  import logger
from modules.parser import converter_para_float, formatar_moeda


class SheetsService:
    def __init__(self):
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        
        json_path = os.getenv("GOOGLE_SHEETS_JSON_PATH")
        nome_planilha = os.getenv("NOME_DA_PLANILHA")
        nome_aba = os.getenv("NOME_DA_ABA")
        
        creds = Credentials.from_service_account_file(json_path, scopes=scopes)
        self.client = gspread.authorize(creds)
        
        arquivo = self.client.open(nome_planilha) #type: ignore
        self.sheet = arquivo.worksheet(nome_aba) #type: ignore
        
        self.cabecalhos = self.sheet.row_values(1)
        self.cabecalhos_normalizados = [c.strip().upper() for c in self.cabecalhos]

    def salvar(self, lista_de_dicionarios: list) -> list:
        if not lista_de_dicionarios:
            return []
        
        logger.debug(f"[salvar] Registro de salvamento de pedidos: {lista_de_dicionarios}")

        novo_id = self._obter_proximo_id()

        for produto in lista_de_dicionarios:
            produto["ID"] = novo_id

        linha_inicial = len(self.sheet.col_values(2)) + 1
        
        celulas_para_atualizar = self._preparar_celulas(lista_de_dicionarios, linha_inicial)
        
        if not celulas_para_atualizar:
            return []

        self.sheet.update_cells(celulas_para_atualizar, value_input_option="USER_ENTERED") #type: ignore
        
        self.atualizar_status_novo_pedido(novo_id)
        
        return [{
            "id": novo_id,
            "cliente": lista_de_dicionarios[0].get("CLIENTE", "Desconhecido"),
            "data": lista_de_dicionarios[0].get("DATA DO PEDIDO", "Desconhecida"),
            "qtd_produtos": len(lista_de_dicionarios)
        }]


    def atualizar_pagamento(self, id_pedido: str, novo_valor_entrada: str) -> dict | None:        
        dados = self._obter_dados_base_planilha(id_pedido)
        if not dados:
            return None
            
        linhas_do_pedido, indices, soma_valor_total, entrada_atual = dados
            
        valor_pago_nesta_mensagem = converter_para_float(novo_valor_entrada)
        entrada_acumulada = entrada_atual + valor_pago_nesta_mensagem
        novo_status = "Pago" if entrada_acumulada >= soma_valor_total else "Adiantamento"

        entrada_acumulada_formatada = formatar_moeda(str(entrada_acumulada))
        celulas = self._preparar_celulas_pagamento(linhas_do_pedido, indices, novo_status, entrada_acumulada_formatada)
        self.sheet.update_cells(celulas, value_input_option="USER_ENTERED") #type: ignore
        
        return {"id": id_pedido, "status": novo_status, "valor": entrada_acumulada_formatada}
    

    def atualizar_status_novo_pedido(self, id_pedido: str) -> dict | None:        
        dados = self._obter_dados_base_planilha(id_pedido)
        if not dados:
            return None
            
        linhas_do_pedido, indices, soma_valor_total, entrada_atual = dados

        logger.debug(f"Valor entrada: {entrada_atual}")
        logger.debug(f"Valor total: {soma_valor_total}")
        
        if entrada_atual >= soma_valor_total:
            novo_status = "Pago"
        elif entrada_atual <= 0:
            novo_status = "Devendo"
        else:
            novo_status = "Adiantamento"

        entrada_acumulada_formatada = formatar_moeda(str(entrada_atual))
        celulas = self._preparar_celulas_pagamento(linhas_do_pedido, indices, novo_status, entrada_acumulada_formatada)
        self.sheet.update_cells(celulas, value_input_option="USER_ENTERED") #type: ignore
        
        return {"id": id_pedido, "status": novo_status, "valor": entrada_acumulada_formatada}
    

    def buscar_ids_abertos_com_saldo(self, nome_cliente):
        dados = self.sheet.get_all_records(expected_headers=self.cabecalhos_normalizados[:12])
        logger.debug(f"Quantidade de dados coletados: {len(dados)}")

        pedidos_pendentes = {}  # Vai guardar no formato: {"teste 02": 50.00, "teste 03": 120.00}

        # Primeiro, agrupamos tudo que é desse cliente
        for linha in dados:
            nome_planilha = str(linha.get('CLIENTE', '')).lower().strip()
            nome_busca = nome_cliente.lower().strip()
            status = str(linha.get('STATUS', '')).strip()

            logger.debug(f"Pedidos do cliente {nome_busca} com o status {status} sendo processado...")

            if nome_planilha == nome_busca and status != "Pago":
                id_pedido = str(linha.get('ID', ''))
                
                valor_item = converter_para_float(str(linha.get('VALOR TOTAL', '0')))
                valor_entrada = converter_para_float(str(linha.get('VALOR ENTRADA', '0')))

                if id_pedido not in pedidos_pendentes:
                    pedidos_pendentes[id_pedido] = {"total": 0.0, "pago": 0.0}
                
                pedidos_pendentes[id_pedido]["total"] += valor_item
                pedidos_pendentes[id_pedido]["pago"] += valor_entrada

        saldos_devedores = {}
        for id_pedido, valores in pedidos_pendentes.items():
            falta_pagar = valores["total"] - valores["pago"]
            if falta_pagar > 0:
                saldos_devedores[id_pedido] = falta_pagar

        return saldos_devedores
        

    def _obter_dados_base_planilha(self, id_pedido: str) -> tuple | None:
        todos_os_dados = self.sheet.get_all_values()

        if not todos_os_dados or len(todos_os_dados) < 2:
            logger.info(f"Nenhuma informação recebida para o pedido {id_pedido}!")
            return None
            
        cabecalhos = [c.strip().upper() for c in todos_os_dados[0]]
        indices = self._obter_indices_financeiros(cabecalhos)
        
        if not indices:
            logger.warning("Faltam colunas vitais na planilha (ID, VALOR TOTAL, VALOR ENTRADA ou STATUS)!")
            return None
            
        linhas_do_pedido, soma_valor_total, entrada_atual = self._buscar_linhas_e_total(todos_os_dados, id_pedido, indices)
        
        if not linhas_do_pedido:
            logger.warning("Não foi possível realizar a busca pela atualização...")
            return None
        
        logger.debug(f"[_obter_dados_base_planilha] Resumo dos dados: {linhas_do_pedido, indices, soma_valor_total, entrada_atual}")

        return linhas_do_pedido, indices, soma_valor_total, entrada_atual


    def _obter_indices_financeiros(self, cabecalhos: list) -> dict | None:
        colunas_necessarias = ["ID", "VALOR TOTAL", "VALOR ENTRADA", "STATUS"]
        
        if not all(col in cabecalhos for col in colunas_necessarias):
            return None
            
        logger.debug(f"[_obter_indices_financeiros] Colunas: {cabecalhos}")    
        return {
            "id": cabecalhos.index("ID"),
            "total": cabecalhos.index("VALOR TOTAL"),
            "entrada": cabecalhos.index("VALOR ENTRADA"),
            "status": cabecalhos.index("STATUS")
        }

    def _buscar_linhas_e_total(self, todos_os_dados: list, id_pedido: str, indices: dict) -> tuple:
        linhas_encontradas = []
        soma_total = 0.0
        entrada_atual = 0.0
        id_limpo = id_pedido.strip().upper()
        
        for num_linha, linha_dados in enumerate(todos_os_dados):
            if num_linha == 0: continue
            
            if len(linha_dados) > indices["id"] and linha_dados[indices["id"]].strip().upper() == id_limpo:
                linhas_encontradas.append(num_linha + 1)
                
                if len(linha_dados) > indices["total"]:
                    soma_total += converter_para_float(linha_dados[indices["total"]])
                    
                if len(linhas_encontradas) == 1 and len(linha_dados) > indices["entrada"]:
                    entrada_atual = converter_para_float(linha_dados[indices["entrada"]])

        logger.debug(f"[_buscar_linhas_e_total] Resumo: {linhas_encontradas, soma_total, entrada_atual}")
                    
        return linhas_encontradas, soma_total, entrada_atual


    def _preparar_celulas_pagamento(self, linhas: list, indices: dict, status: str, valor: str) -> list:
        celulas = []
        for num_linha in linhas:
            logger.debug(f"[_preparar_celulas_pagamento] Dados das células: {linhas}")
            celulas.append(gspread.Cell(row=num_linha, col=indices["status"] + 1, value=status))
            celulas.append(gspread.Cell(row=num_linha, col=indices["entrada"] + 1, value=valor))
        return celulas


    def _obter_proximo_id(self) -> str:
        if "ID" not in self.cabecalhos_normalizados:
            return "DDL-00001"
            
        index_id = self.cabecalhos_normalizados.index("ID") + 1
        valores_id = self.sheet.col_values(index_id)
        
        if len(valores_id) <= 1:
            return "DDL-00001"
            
        ultimo_id_texto = str(valores_id[-1]).strip()
        
        try:
            numero = int(ultimo_id_texto.replace("DDL-", ""))
            return f"DDL-{numero + 1:05d}"
        except ValueError:
            return f"DDL-{len(valores_id):05d}"
            

    def _preparar_celulas(self, lista_de_dicionarios: list, linha_inicial: int) -> list:
        celulas = []
        colunas_ignoradas = ["VALOR TOTAL"]
        
        for i, dados_dict in enumerate(lista_de_dicionarios):
            linha_atual = linha_inicial + i
            
            logger.debug(f"[_preparar_celulas] Linha atual: {dados_dict}")

            for index_coluna, nome_coluna in enumerate(self.cabecalhos_normalizados):
                if nome_coluna in colunas_ignoradas:
                    continue
                    
                valor = dados_dict.get(nome_coluna, "")
                celula = gspread.Cell(row=linha_atual, col=index_coluna + 1, value=valor)
                celulas.append(celula)
                
        return celulas