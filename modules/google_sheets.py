import os
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

    def salvar(self, lista_de_dicionarios: list):   
        valores_clientes = self.sheet.col_values(2)
        primeira_linha_vazia = len(valores_clientes) + 1
        
        celulas_para_atualizar = []

        for i, dados_dict in enumerate(lista_de_dicionarios):
            linha_atual = primeira_linha_vazia + i

            for index_coluna, nome_coluna in enumerate(self.cabecalhos_normalizados):

                if nome_coluna in ["VALOR TOTAL", "ID"]:
                    continue

                valor = dados_dict.get(nome_coluna, "")

                celula = gspread.Cell(row=linha_atual, col=index_coluna + 1, value=valor)
                celulas_para_atualizar.append(celula)
                
        if celulas_para_atualizar:
            self.sheet.update_cells(celulas_para_atualizar, value_input_option="USER_ENTERED") #type: ignore