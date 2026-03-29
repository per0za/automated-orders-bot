import os
import time
import gspread
from google.oauth2.service_account import Credentials

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

        linha_inicial = len(self.sheet.col_values(2)) + 1

        celulas_para_atualizar = self._preparar_celulas(lista_de_dicionarios, linha_inicial)
        
        if not celulas_para_atualizar:
            return []
            
        self.sheet.update_cells(celulas_para_atualizar, value_input_option="USER_ENTERED") #type: ignore

        return self._gerar_relatorio_com_ids(lista_de_dicionarios, linha_inicial)

    def _preparar_celulas(self, lista_de_dicionarios: list, linha_inicial: int) -> list:
        celulas = []
        colunas_ignoradas = ["VALOR TOTAL", "ID"]
        
        for i, dados_dict in enumerate(lista_de_dicionarios):
            linha_atual = linha_inicial + i
            
            for index_coluna, nome_coluna in enumerate(self.cabecalhos_normalizados):
                if nome_coluna in colunas_ignoradas:
                    continue
                    
                valor = dados_dict.get(nome_coluna, "")
                celula = gspread.Cell(row=linha_atual, col=index_coluna + 1, value=valor)
                celulas.append(celula)
                
        return celulas

    def _gerar_relatorio_com_ids(self, lista_de_dicionarios: list, linha_inicial: int) -> list:
        if "ID" not in self.cabecalhos_normalizados:
            return [{
                "id": "N/A", 
                "cliente": d.get("CLIENTE", "Desconhecido"), 
                "data": d.get("DATA DO PEDIDO", "Desconhecida")
            } for d in lista_de_dicionarios]

        time.sleep(2)
        
        index_id = self.cabecalhos_normalizados.index("ID") + 1
        valores_id = self.sheet.col_values(index_id)
        
        relatorio = []
        for i, dados_dict in enumerate(lista_de_dicionarios):
            linha_atual = linha_inicial + i
            id_gerado = "N/A"
            
            if len(valores_id) >= linha_atual:
                id_gerado = valores_id[linha_atual - 1]
                
            relatorio.append({
                "id": id_gerado,
                "cliente": dados_dict.get("CLIENTE", "Desconhecido"),
                "data": dados_dict.get("DATA DA ENTREGA", "Desconhecida")
            })
            
        return relatorio