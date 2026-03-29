import time

from dotenv import load_dotenv

from modules.whatsapp_bot import WhatsAppBot
from modules.google_sheets import SheetsService
from modules.parser import parse_pedido

MARCADOR_DE_CORTE = "Pedidos processados e enviados para a planilha!"

def processar_pedidos_pendentes(bot: WhatsAppBot, planilha: SheetsService):
    lista_de_pedidos = bot.buscar_pedidos_em_lote(MARCADOR_DE_CORTE)
    
    if not lista_de_pedidos:
        return 

    print(f"\n📦 Opa! Encontrei {len(lista_de_pedidos)} pedido(s) novo(s). Processando...")
    
    todos_recibos = []
    
    for pedido_texto in lista_de_pedidos:
        dados_limpos_lista = parse_pedido(pedido_texto)
        
        if dados_limpos_lista:
            recibos_do_pedido = planilha.salvar(dados_limpos_lista)
            todos_recibos.extend(recibos_do_pedido)
            
    if todos_recibos:
        print("💬 Montando e enviando o relatório dinâmico no WhatsApp...")
        
        linhas_mensagem = [
            MARCADOR_DE_CORTE,
            "",
            f"{len(todos_recibos)} venda(s) registrada(s):"
        ]

        for i, recibo in enumerate(todos_recibos):
            if i == 0:
                linha_info = f"- Pedido {recibo['id']} de {recibo['cliente']} em {recibo['data']}"
                linhas_mensagem.append(linha_info)
            else:
                linha_info = f"Pedido {recibo['id']} de {recibo['cliente']} em {recibo['data']}"
                linhas_mensagem.append(linha_info)

        mensagem_final = "\n".join(linhas_mensagem)

        bot.enviar_mensagem(mensagem_final)
        print("✨ Relatório dinâmico enviado com sucesso!\n")

def main():
    print("🚀 Iniciando a Automação de Leitura Contínua...")
    load_dotenv()
    
    try:
        planilha = SheetsService()
        bot = WhatsAppBot()
    except Exception as e:
        print(f"❌ Erro fatal ao iniciar: {e}")
        return

    bot.iniciar()
    bot.abrir_grupo()
    
    print("👀 Monitoramento contínuo ativado! O robô vai vigiar novos pedidos a cada 15 segundos...")
    print("Pressione 'Ctrl + C' no terminal a qualquer momento para desligar o robô.")
    
    while True:
        try:
            processar_pedidos_pendentes(bot, planilha)
            
            time.sleep(15)
            
        except KeyboardInterrupt:
            print("\n🛑 Robô desligado pelo usuário com sucesso.")
            break
            
        except Exception as e:
            print(f"⚠️ Erro inesperado durante o monitoramento: {e}")
            time.sleep(15)

if __name__ == "__main__":
    main()