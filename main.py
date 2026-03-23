import time
from dotenv import load_dotenv

from modules.whatsapp_bot import WhatsAppBot
from modules.google_sheets import SheetsService
from modules.parser import parse_pedido

def main():
    print("🚀 Iniciando a Automação de Pedidos...")
    
    load_dotenv()
    
    try:
        planilha = SheetsService()
        bot = WhatsAppBot()
    except Exception as e:
        print(f"❌ Erro fatal ao iniciar os serviços. Verifique suas credenciais e o Firefox: {e}")
        return

    bot.iniciar()
    bot.abrir_grupo()
    
    print("👀 Monitoramento ativo. Aguardando novos pedidos no grupo...")

    while True:
        try:
            mensagem_nova = bot.escutar_mensagens()
            
            if mensagem_nova:
                print("\n🔔 Novo pedido detectado!")
                
                dados_limpos = parse_pedido(mensagem_nova)
                
                if dados_limpos:
                    planilha.salvar(dados_limpos)
                else:
                    print("⚠️ A mensagem não retornou dados válidos. Ignorando.")

            time.sleep(5)
            
        except KeyboardInterrupt:
            print("\n🛑 Robô desligado pelo usuário.")
            break
            
        except Exception as e:
            print(f"⚠️ Erro inesperado durante a leitura: {e}")
            time.sleep(5) 

if __name__ == "__main__":
    main()