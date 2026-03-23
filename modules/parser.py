def parse_pedido(texto_bruto: str) -> list:
    linhas = texto_bruto.split('\n')
    dados = []
    
    for linha in linhas:
        if linha.strip() != "" and ":" in linha:
            partes = linha.split(":", 1)
            chave = partes[0].strip()
            
            if len(chave) > 2:
                valor = partes[1].strip()
                dados.append(valor)
            
    return dados