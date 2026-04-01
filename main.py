import time

from dotenv import load_dotenv

from modules.whatsapp_bot import WhatsAppBot
from modules.google_sheets import SheetsService
from modules.parser import parse_pedido, parse_pagamento
from modules.logger_config  import logger

MARCADOR_DE_CORTE = "Pedidos processados e enviados para a planilha!"

def processar_pedidos_pendentes(bot: WhatsAppBot, planilha: SheetsService):
    logger.info("Iniciando o processo de registro e processamento de pedidos!")
    lista_de_pedidos = bot.buscar_pedidos_em_lote(MARCADOR_DE_CORTE)
    
    if not lista_de_pedidos: 
        logger.info("Nenhum pedido encontrado...")
        return 

    logger.info(f"Opa! Encontrei {len(lista_de_pedidos)} mensagem(ns) válida(s). Processando...")

    recibos_novos, recibos_pagamentos = _processar_mensagens(lista_de_pedidos, planilha)

    if recibos_novos or recibos_pagamentos:
        logger.info("Montando e enviando o relatório no WhatsApp...")
        mensagem_final = _montar_relatorio_whatsapp(recibos_novos, recibos_pagamentos)
        bot.enviar_mensagem(mensagem_final)
        logger.info("Relatório enviado com sucesso!")


def _processar_mensagens(mensagens: list, planilha: SheetsService) -> tuple:
    recibos_novos = []
    recibos_pagamentos = []
    
    for texto in mensagens:
        texto_upper = texto.upper()
        
        if "CLIENTE:" in texto_upper:
            dados_limpos = parse_pedido(texto)
            if dados_limpos:
                recibos = planilha.salvar(dados_limpos)
                recibos_novos.extend(recibos)
                
        elif "PEDIDO:" in texto_upper and "VALOR ENTRADA:" in texto_upper:
            dados_pagamento = parse_pagamento(texto)
            if dados_pagamento:
                recibo_pagamento = planilha.atualizar_pagamento(dados_pagamento["id_pedido"], dados_pagamento["valor_pago"])
                if recibo_pagamento:
                    recibos_pagamentos.append(recibo_pagamento)
                    
    return recibos_novos, recibos_pagamentos


def _montar_relatorio_whatsapp(recibos_novos: list, recibos_pagamentos: list) -> str:
    linhas = [MARCADOR_DE_CORTE, "Segue a relação atual:"]
    
    if recibos_novos:
        linhas.append(f"\n📝 {len(recibos_novos)} Novo(s) Pedido(s):")
        for i, r in enumerate(recibos_novos):
            if i == 0:
                linhas.append(f"- Pedido {r['id']} ({r.get('qtd_produtos', 1)} itens) de {r['cliente']}.")
            else:
                linhas.append(f"Pedido {r['id']} ({r.get('qtd_produtos', 1)} itens) de {r['cliente']}.")
            
    if recibos_pagamentos:
        linhas.append(f"\n💰 {len(recibos_pagamentos)} Atualização(ões) de Pagamento:")
        for i, r in enumerate(recibos_pagamentos):
            if i == 0:
                linhas.append(f"- Pedido {r['id']} atualizado para: {r['status']} ({r['valor']}).")
            else:
                linhas.append(f"Pedido {r['id']} atualizado para: {r['status']} ({r['valor']}).")
            
    return "\n".join(linhas)
        

def main():
    logger.info("Iniciando a automação de pedidos...")
    load_dotenv()
    
    try:
        planilha = SheetsService()
        bot = WhatsAppBot()
    except Exception as e:
        logger.warning(f"Erro fatal ao iniciar: {e}")
        return

    bot.iniciar()
    bot.abrir_grupo()
    
    logger.info("Monitoramento ativo! O robô vai vigiar novos pedidos a cada 30 segundos...")
    logger.info("Pressione 'Ctrl + C' no terminal a qualquer momento para desligar o robô.")
    
    while True:
        try:
            processar_pedidos_pendentes(bot, planilha)
            
            time.sleep(30)
            
        except KeyboardInterrupt:
            logger.info("Robô desligado pelo usuário com sucesso.")
            break
            
        except Exception as e:
            logger.warning(f"Erro inesperado durante o monitoramento: {e}")
            time.sleep(30)

if __name__ == "__main__":
    main()