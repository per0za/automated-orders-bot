import os
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service  
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager

class WhatsAppBot:
    def __init__(self):
        self.grupo_alvo = os.getenv("WHATSAPP_GROUP_NAME")
        caminho_perfil = os.getenv("FIREFOX_PROFILE_PATH")

        opcoes = Options()

        if caminho_perfil:
            opcoes.add_argument("-profile")
            opcoes.add_argument(caminho_perfil)
        
        service = Service(GeckoDriverManager().install())
        self.driver = webdriver.Firefox(service=service, options=opcoes) # type: ignore

        self.ultima_mensagem_lida = ""

    def iniciar(self):
        print("🌐 Abrindo o WhatsApp Web...")
        self.driver.get("https://web.whatsapp.com/")

        print("⏳ Aguardando login e carregamento (Pode demorar um pouco na primeira vez)...")
        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
        )
        print("✅ WhatsApp carregado!")

    def abrir_grupo(self):
        print(f"🔍 Buscando o grupo: {self.grupo_alvo}")
        try:
            elemento_grupo = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, f"//span[@title='{self.grupo_alvo}']"))
            )
            elemento_grupo.click()
            print(f"✅ Grupo '{self.grupo_alvo}' aberto!")
            time.sleep(2)
        except Exception as e:
            print(f"❌ Erro ao tentar abrir o grupo. Verifique o nome no .env. Erro: {e}")

    def escutar_mensagens(self) -> str | None:
        try:
            mensagens = self.driver.find_elements(By.CSS_SELECTOR, "div.message-in")
            
            if len(mensagens) > 0:
                ultima_bolha = mensagens[-1]
                texto = ultima_bolha.text 

                if "Comprador:" in texto and texto != self.ultima_mensagem_lida:
                    self.ultima_mensagem_lida = texto
                    return texto
                    
        except Exception as e:
            print(f"⚠️ Pequeno erro ao ler mensagens (ignorando): {e}")
        
        return None