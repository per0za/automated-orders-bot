import os
import time

from selenium import webdriver

from selenium.webdriver.firefox.service import Service  
from selenium.webdriver.firefox.options import Options

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from webdriver_manager.firefox import GeckoDriverManager

from modules.logger_config  import logger

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
        logger.info("Abrindo o WhatsApp Web...")
        self.driver.get("https://web.whatsapp.com/")

        logger.info("Aguardando login e carregamento (Pode demorar um pouco na primeira vez)...")
        WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//span[@aria-label='WhatsApp' and @data-icon='wa-wordmark-refreshed']"))
        )
        logger.info("WhatsApp carregado!")
        self.driver.minimize_window()

    def abrir_grupo(self):
        logger.info(f"Buscando o grupo: {self.grupo_alvo}")
        try:
            elemento_grupo = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.XPATH, f"//span[@title='{self.grupo_alvo}']"))
            )
            elemento_grupo.click()
            logger.info(f"Grupo '{self.grupo_alvo}' aberto!")
            time.sleep(2)
        except Exception as e:
            logger.warning(f"Erro ao tentar abrir o grupo. Verifique o nome no .env. Erro: {e}")

    def buscar_pedidos_em_lote(self, marcador: str) -> list:
        logger.info("Iniciando a busca por pedidos...")
        pedidos_encontrados = []

        try:
            bolhas = self.driver.find_elements(By.CSS_SELECTOR, "div.message-in, div.message-out")
            
            indice_do_marcador = -1

            for i, bolha in enumerate(bolhas):
                if marcador in bolha.text:
                    indice_do_marcador = i

            bolhas_novas = bolhas[indice_do_marcador + 1 :] if indice_do_marcador != -1 else bolhas

            for bolha in bolhas_novas:
                try:
                    container = bolha.find_element(By.CSS_SELECTOR, "span.copyable-text")
                    spans = container.find_elements(By.XPATH, "./span")
                    linhas = [span.text.strip() for span in spans if span.text.strip() != ""]
                    texto_limpo = "\n".join(linhas)
                    
                    if "CLIENTE:" in texto_limpo.upper() or "PEDIDO:" in texto_limpo.upper():
                        pedidos_encontrados.append(texto_limpo)

                except Exception as e:
                    logger.warning(f"Algo inesperado aconteceu: {e}")
                    
        except Exception as e:
            logger.warning(f"Erro ao buscar pedidos: {e}")
            
        return pedidos_encontrados

    def enviar_mensagem(self, texto: str):
        try:
            caixa_de_texto = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
            )

            acao = ActionChains(self.driver)
            acao.click(on_element=caixa_de_texto)
            acao.send_keys(texto)
            acao.send_keys(Keys.ENTER)
            acao.perform()

            time.sleep(2)

            logger.info("Mensagem enviada com sucesso!")
            
        except Exception as e:
            logger.warning(f"Erro ao tentar enviar o marcador: {e}")