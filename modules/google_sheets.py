import os
import gspread
from google.oauth2.service_account import Credentials  # <-- A nova biblioteca aqui

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

        arquivo = self.client.open(nome_planilha) # type: ignore
        self.sheet = arquivo.worksheet(nome_aba) #type: ignore

    def salvar(self, dados_lista):
        self.sheet.append_row(dados_lista)
        print("✅ Pedido salvo na planilha com sucesso!")