from datetime import datetime
from modules.logger_config  import logger

def formatar_moeda(valor_str: str) -> str:
    if not valor_str or valor_str.strip() == "": return ""
    try:
        numero_limpo = valor_str.upper().replace("R$", "").replace(" ", "")
        if "," in numero_limpo and "." in numero_limpo: numero_limpo = numero_limpo.replace(".", "").replace(",", ".")
        elif "," in numero_limpo: numero_limpo = numero_limpo.replace(",", ".")
        return f"R$ {float(numero_limpo):.2f}".replace(".", ",")
    except ValueError:
        return valor_str


def converter_para_float(valor_str: str) -> float:
    if not valor_str or valor_str.strip() == "": return 0.0
    numero_limpo = valor_str.upper().replace("R$", "").replace(" ", "")
    if "," in numero_limpo and "." in numero_limpo: numero_limpo = numero_limpo.replace(".", "").replace(",", ".")
    elif "," in numero_limpo: numero_limpo = numero_limpo.replace(",", ".")
    try:
        return float(numero_limpo)
    except ValueError:
        return 0.0


def _extrair_dados_base(texto_bruto: str) -> dict:
    dados_base = {}
    
    for linha in texto_bruto.split('\n'):
        if ":" not in linha:
            continue
            
        partes = linha.split(":", 1)
        chave = partes[0].strip().upper()
        valor_bruto = partes[1].strip()

        if chave in ["PRODUTO", "QUANTIDADE"]:
            valor_bruto = valor_bruto.replace(",", ";")
            
        dados_base[chave] = [v.strip() for v in valor_bruto.split(';')]
        
    return dados_base


def _construir_linhas_pedido(dados_base: dict) -> list:
    pedidos_finais = []
    qtd_produtos = len(dados_base.get("PRODUTO", [""]))
    
    for i in range(qtd_produtos):
        linha_atual = {}

        for chave, lista_valores in dados_base.items():
            valor = lista_valores[i] if i < len(lista_valores) else lista_valores[0]
            
            if chave == "VALOR ENTRADA": 
                valor = formatar_moeda(valor)
                
            linha_atual[chave] = valor
            
        valor_num = converter_para_float(linha_atual.get("VALOR ENTRADA", ""))
        linha_atual["STATUS"] = "Adiantamento" if valor_num > 0 else "Devendo"
                
        pedidos_finais.append(linha_atual)
        
    return pedidos_finais


def parse_pedido(texto_bruto: str) -> list:
    dados_base = _extrair_dados_base(texto_bruto)
    
    if "CLIENTE" not in dados_base:
        return []

    dados_base["DATA DO PEDIDO"] = [datetime.now().strftime("%d/%m/%Y")]

    return _construir_linhas_pedido(dados_base)


def parse_pagamento(texto_bruto: str) -> dict | None:
    linhas = texto_bruto.split('\n')
    dados = {}
    for linha in linhas:
        if ":" in linha:
            partes = linha.split(":", 1)
            chave = partes[0].strip().upper()
            valor = partes[1].strip()
            if chave == "VALOR ENTRADA": 
                valor = formatar_moeda(valor)
            dados[chave] = valor

    if "PEDIDO" in dados and "VALOR ENTRADA" in dados:
        return {"id_pedido": dados["PEDIDO"], "valor_pago": dados["VALOR ENTRADA"]}
    return None