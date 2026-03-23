def parse_pedido(texto_bruto: str) -> list:
    linhas = texto_bruto.split('\n')
    dados = []
    
    for linha in linhas:
        if linha.strip() != "" and ":" in linha:
            valor = linha.split(":", 1)[1].strip()
            dados.append(valor)
            
    return dados