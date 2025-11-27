DOMAIN = "tholz"
DEFAULT_PORT = 4000
CONF_HOST = "host"

# Mapeamento de IDs de Produtos Tholz
PRODUCT_MODELS = {
    1356: "SmartPlus 1ª Geração",
    1354: "Basic SmartPool 1ª Geração",
    11355: "SmartPool 1ª Geração",
    1392: "SmartHeat 1ª Geração",
    1516: "TLZ Smart 2ª Geração",
    1527: "Trocador de Calor LuxPool",
    1537: "Trocador Tholz TurboSilence",
    1524: "THC30",
    1528: "THC45",
    1529: "THC60",
    1530: "THC80",
    21505: "SmartHeat 2ª Geração",
    21534: "Basic SmartHeat",
    21562: "Basic SmartHeat Porta de Painel",
    31569: "TLS Smart",
    1551: "SmartLux",
    1512: "Basic SmartPool 2ª Geração",
    11462: "SmartPool 2ª Geração"
}

# Mapeamento de Erros Tholz
ERROR_CODES = {
    0: "Normal",
    1: "Sobreaquecimento (Solar)",
    2: "Anticongelamento",
    3: "Falta de Água",
    4: "Resfriamento da Resistência",
    5: "Erro de temperatura (Sensor)",
    6: "Termostato Desarmado",
    8: "Pressão Alta",
    9: "Pressão Baixa",
    10: "Baixo fluxo de água",
    11: "Ciclo de degelo",
    12: "Erro de Alimentação",
    13: "Parâmetro Inconsistente",
    14: "Erro Sensor T1",
    15: "Erro Sensor T2",
    16: "Erro Sensor T3",
    20: "Dados inconsistentes",
    21: "Temp. da água elevada",
    22: "Temp. da água baixa",
    24: "Erro sobrecorrente",
    25: "Erro de alimentação",
    26: "Célula desconectada",
    27: "Erro de fluxo",
    36: "Porta aberta"
    # Adicione os outros códigos se desejar a lista completa
}

# Mapa de Efeitos (ID -> Nome)
# ATENÇÃO: Verifique na sua documentação quais são os nomes corretos para cada ID
THOLZ_EFFECTS = {
    255: "Cor Fixa (RGB)", # Geralmente 255 é quando usamos a cor customizada
    0: "Efeito 0",
    1: "Efeito 1",
    2: "Efeito 2",
    # Adicione os outros aqui...
}

# Inverso para enviar comando (Nome -> ID)
THOLZ_EFFECTS_NAMED = {v: k for k, v in THOLZ_EFFECTS.items()}

def get_output_info(output_id):
    """Retorna (Nome Padrão, Ícone) baseado no ID da saída."""
    if output_id == 0:
        return "Filtro", "mdi:filter"
    elif output_id == 1:
        return "Apoio Elétrico", "mdi:lightning-bolt"
    elif output_id == 2:
        return "Apoio a Gás", "mdi:fire"
    elif output_id == 3:
        return "Recirculação", "mdi:sync"
    elif output_id == 4:
        return "Borbulhador", "mdi:bubbles"
    elif output_id == 5:
        return "Circulação", "mdi:pump"
    
    # Faixas de IDs
    if 10 <= output_id <= 19:
        return "Auxiliar", "mdi:light-switch"
    elif 20 <= output_id <= 29:
        return "Cascata", "mdi:waterfall"
    elif 30 <= output_id <= 39:
        return "Hidro", "mdi:hot-tub"
    elif 40 <= output_id <= 59:
        return "Interruptor", "mdi:toggle-switch"
        
    return "Saída", "mdi:power"