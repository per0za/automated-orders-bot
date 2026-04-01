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

        novo_id = self._obter_proximo_id()

        for produto in lista_de_dicionarios:
            produto["ID"] = novo_id

        linha_inicial = len(self.sheet.col_values(2)) + 1
        
        celulas_para_atualizar = self._preparar_celulas(lista_de_dicionarios, linha_inicial)
        
        if not celulas_para_atualizar:
            return []

        self.sheet.update_cells(celulas_para_atualizar, value_input_option="USER_ENTERED") #type: ignore
        
        return [{
            "id": novo_id,
            "cliente": lista_de_dicionarios[0].get("CLIENTE", "Desconhecido"),
            "data": lista_de_dicionarios[0].get("DATA DO PEDIDO", "Desconhecida"),
            "qtd_produtos": len(lista_de_dicionarios)
        }]
    

    def atualizar_pagamento(self, id_pedido: str, novo_valor_entrada: str) -> dict | None:        
        todos_os_dados = self.sheet.get_all_values()
        if not todos_os_dados or len(todos_os_dados) < 2:
            return None
            
        cabecalhos = [c.strip().upper() for c in todos_os_dados[0]]
        indices = self._obter_indices_financeiros(cabecalhos)
        
        if not indices:
            logger.warning("Faltam colunas vitais na planilha (ID, VALOR TOTAL, VALOR ENTRADA ou STATUS)!")
            return None
            
        linhas_do_pedido, soma_valor_total, entrada_atual = self._buscar_linhas_e_total(todos_os_dados, id_pedido, indices)
        
        if not linhas_do_pedido:
            return None
            
        valor_pago_nesta_mensagem = converter_para_float(novo_valor_entrada)
        entrada_acumulada = entrada_atual + valor_pago_nesta_mensagem

        novo_status = "Pago" if entrada_acumulada >= soma_valor_total else "Adiantamento"

        entrada_acumulada_formatada = formatar_moeda(str(entrada_acumulada))

        celulas = self._preparar_celulas_pagamento(linhas_do_pedido, indices, novo_status, entrada_acumulada_formatada)
        self.sheet.update_cells(celulas, value_input_option="USER_ENTERED") #type: ignore
        
        return {"id": id_pedido, "status": novo_status, "valor": entrada_acumulada_formatada}
    

    def _obter_indices_financeiros(self, cabecalhos: list) -> dict | None:
        colunas_necessarias = ["ID", "VALOR TOTAL", "VALOR ENTRADA", "STATUS"]
        
        if not all(col in cabecalhos for col in colunas_necessarias):
            return None
            
        return {
            "id": cabecalhos.index("ID"),
            "total": cabecalhos.index("VALOR TOTAL"),
            "entrada": cabecalhos.index("VALOR ENTRADA"),
            "status": cabecalhos.index("STATUS")
        }

    def _buscar_linhas_e_total(self, todos_os_dados: list, id_pedido: str, indices: dict) -> tuple:
        from modules.parser import converter_para_float
        
        linhas_encontradas = []
        soma_total = 0.0
        entrada_atual = 0.0
        id_limpo = id_pedido.strip().upper()
        
        for num_linha, linha_dados in enumerate(todos_os_dados):
            if num_linha == 0: continue # Pula o cabeçalho
            
            if len(linha_dados) > indices["id"] and linha_dados[indices["id"]].strip().upper() == id_limpo:
                linhas_encontradas.append(num_linha + 1)
                
                if len(linha_dados) > indices["total"]:
                    soma_total += converter_para_float(linha_dados[indices["total"]])
                    
                if len(linhas_encontradas) == 1 and len(linha_dados) > indices["entrada"]:
                    entrada_atual = converter_para_float(linha_dados[indices["entrada"]])
                    
        return linhas_encontradas, soma_total, entrada_atual

    def _preparar_celulas_pagamento(self, linhas: list, indices: dict, status: str, valor: str) -> list:
        celulas = []
        for num_linha in linhas:
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
            
            for index_coluna, nome_coluna in enumerate(self.cabecalhos_normalizados):
                if nome_coluna in colunas_ignoradas:
                    continue
                    
                valor = dados_dict.get(nome_coluna, "")
                celula = gspread.Cell(row=linha_atual, col=index_coluna + 1, value=valor)
                celulas.append(celula)
                
        return celulas