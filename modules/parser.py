from datetime import datetime

def formatar_moeda(valor_str: str) -> str:
    if not valor_str or valor_str.strip() == "":
        return ""
    
    try:
        numero_limpo = valor_str.upper().replace("R$", "").replace(" ", "")
        
        if "," in numero_limpo and "." in numero_limpo:
            numero_limpo = numero_limpo.replace(".", "").replace(",", ".")
        elif "," in numero_limpo:
            numero_limpo = numero_limpo.replace(",", ".")
            
        valor_float = float(numero_limpo)
        
        texto_valor = f"R$ {valor_float:.2f}".replace(".", ",")
        return texto_valor
    except ValueError:
        return valor_str

def parse_pedido(texto_bruto: str) -> list:
    linhas = texto_bruto.split('\n')
    dados_base = {}
    
    for linha in linhas:
        if ":" in linha:
            partes = linha.split(":", 1)
            chave = partes[0].strip().upper()
            valor_bruto = partes[1].strip()
            
            valores_separados = [v.strip() for v in valor_bruto.split(';')]
            dados_base[chave] = valores_separados
            
    if "CLIENTE" not in dados_base:
        return []

    data_hoje = datetime.now().strftime("%d/%m/%Y")
    dados_base["DATA DO PEDIDO"] = [data_hoje]

    qtd_linhas = len(dados_base.get("PRODUTO", [""]))
    pedidos_finais = []
    
    for i in range(qtd_linhas):
        linha_atual = {}
        
        for chave, lista_valores in dados_base.items():
            if i < len(lista_valores):
                valor = lista_valores[i]
            else:
                valor = lista_valores[0]

            if chave == "VALOR ENTRADA":
                valor = formatar_moeda(valor)
                
            linha_atual[chave] = valor
                
        pedidos_finais.append(linha_atual)
        
    return pedidos_finais