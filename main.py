import time

from dotenv import load_dotenv

from modules.whatsapp_bot import WhatsAppBot
from modules.google_sheets import SheetsService
from modules.parser import parse_pedido

MARCADOR_DE_CORTE = "Pedidos processados e enviados para a planilha!"

def main():
    print("🚀 Iniciando a Automação de Leitura em Lote...")
    load_dotenv()
    
    try:
        planilha = SheetsService()
        bot = WhatsAppBot()
    except Exception as e:
        print(f"❌ Erro fatal ao iniciar: {e}")
        return

    bot.iniciar()
    bot.abrir_grupo()
    
    print("🔍 Procurando o último marcador e varrendo pedidos novos...")
    time.sleep(3)

    lista_de_pedidos = bot.buscar_pedidos_em_lote(MARCADOR_DE_CORTE)
    
    if len(lista_de_pedidos) > 0:
        print(f"📦 Sucesso! Encontrei {len(lista_de_pedidos)} pedido(s) novo(s).")

        for pedido_texto in lista_de_pedidos:
            dados_limpos = parse_pedido(pedido_texto)
            if dados_limpos:
                planilha.salvar(dados_limpos)

        print("💬 Enviando o marcador no grupo do WhatsApp...")
        bot.enviar_mensagem(MARCADOR_DE_CORTE)
        print("✨ Processo concluído com sucesso!")
        
    else:
        print("🤷 Nenhum pedido novo encontrado depois do último marcador.")
        
    bot.driver.quit()

if __name__ == "__main__":
    main()