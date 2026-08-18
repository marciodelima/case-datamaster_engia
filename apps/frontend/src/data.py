"""
Data Models and Static Configurations for Meu Copiloto Financeiro
Client profiles, portfolios, and market sector mappings
"""

# Client profiles and portfolios
CLIENTS = {
    "Marcio": {
        "perfil": "conservador",
        "objetivo": "Ganho de patrimônio menor, mas com baixo risco.",
        "portfolio": [
            {"ticker": "ITUB4.SA", "quantidade": 300, "preco_medio": 31.2, "preco_teto": 34.0},
            {"ticker": "BBAS3.SA", "quantidade": 350, "preco_medio": 42.4, "preco_teto": 46.0},
            {"ticker": "ABEV3.SA", "quantidade": 500, "preco_medio": 14.5, "preco_teto": 16.2},
            {"ticker": "EGIE3.SA", "quantidade": 200, "preco_medio": 43.5, "preco_teto": 48.0},
            {"ticker": "SAPR4.SA", "quantidade": 400, "preco_medio": 10.8, "preco_teto": 12.5},
            {"ticker": "BBSE3.SA", "quantidade": 250, "preco_medio": 33.5, "preco_teto": 37.0},
            {"ticker": "VIVT3.SA", "quantidade": 180, "preco_medio": 48.2, "preco_teto": 52.0},
            {"ticker": "TAEE4.SA", "quantidade": 220, "preco_medio": 37.8, "preco_teto": 41.5},
            {"ticker": "CSMG3.SA", "quantidade": 300, "preco_medio": 16.2, "preco_teto": 18.5},
            {"ticker": "KLBN4.SA", "quantidade": 150, "preco_medio": 4.5, "preco_teto": 5.2},
        ],
    },
    "Lima": {
        "perfil": "moderado",
        "objetivo": "Ganho de patrimônio equilibrado, mas com mais risco.",
        "portfolio": [
            {"ticker": "ITUB4.SA", "quantidade": 230, "preco_medio": 30.9, "preco_teto": 35.5},
            {"ticker": "BBAS3.SA", "quantidade": 240, "preco_medio": 40.7, "preco_teto": 48.4},
            {"ticker": "PETR4.SA", "quantidade": 200, "preco_medio": 34.7, "preco_teto": 41.5},
            {"ticker": "VALE3.SA", "quantidade": 120, "preco_medio": 66.2, "preco_teto": 75.5},
            {"ticker": "WEGE3.SA", "quantidade": 150, "preco_medio": 37.1, "preco_teto": 46.0},
            {"ticker": "B3SA3.SA", "quantidade": 300, "preco_medio": 12.0, "preco_teto": 14.8},
            {"ticker": "CMIG4.SA", "quantidade": 260, "preco_medio": 10.4, "preco_teto": 12.8},
            {"ticker": "RENT3.SA", "quantidade": 180, "preco_medio": 28.8, "preco_teto": 36.0},
            {"ticker": "LREN3.SA", "quantidade": 140, "preco_medio": 38.5, "preco_teto": 45.0},
            {"ticker": "RADL3.SA", "quantidade": 200, "preco_medio": 32.5, "preco_teto": 38.0},
        ],
    },
    "Ian": {
        "perfil": "agressivo",
        "objetivo": "Ganho de patrimônio mais elevado, mas com mais risco.",
        "portfolio": [
            {"ticker": "MGLU3.SA", "quantidade": 800, "preco_medio": 2.9, "preco_teto": 4.8},
            {"ticker": "PRIO3.SA", "quantidade": 400, "preco_medio": 38.5, "preco_teto": 52.0},
            {"ticker": "CSAN3.SA", "quantidade": 500, "preco_medio": 15.8, "preco_teto": 21.5},
            {"ticker": "RAIZ4.SA", "quantidade": 600, "preco_medio": 3.8, "preco_teto": 5.5},
            {"ticker": "LREN3.SA", "quantidade": 350, "preco_medio": 39.2, "preco_teto": 48.0},
            {"ticker": "VBBR3.SA", "quantidade": 450, "preco_medio": 18.5, "preco_teto": 24.0},
            {"ticker": "GGBR4.SA", "quantidade": 380, "preco_medio": 22.8, "preco_teto": 29.5},
            {"ticker": "SUZB3.SA", "quantidade": 200, "preco_medio": 56.5, "preco_teto": 68.0},
            {"ticker": "HAPV3.SA", "quantidade": 900, "preco_medio": 4.2, "preco_teto": 6.5},
            {"ticker": "COGN3.SA", "quantidade": 700, "preco_medio": 2.5, "preco_teto": 4.0},
        ],
    },
}

# Sector mapping
SECTOR_BY_TICKER = {
    "PETR4.SA": "Energia",
    "VALE3.SA": "Mineração",
    "ITUB4.SA": "Financeiro",
    "B3SA3.SA": "Financeiro",
    "BBAS3.SA": "Financeiro",
    "ELET3.SA": "Utilities",
    "CMIG4.SA": "Utilities",
    "ABEV3.SA": "Consumo",
    "RENT3.SA": "Imobiliário",
    "MGLU3.SA": "Varejo",
    "WEGE3.SA": "Indústria",
    "EGIE3.SA": "Utilities",
    "SAPR4.SA": "Utilities",
    "BBSE3.SA": "Financeiro",
    "VIVT3.SA": "Telecom",
    "TAEE4.SA": "Utilities",
    "CSMG3.SA": "Utilities",
    "KLBN4.SA": "Materiais",
    "LREN3.SA": "Varejo",
    "RADL3.SA": "Saúde",
    "PRIO3.SA": "Energia",
    "CSAN3.SA": "Energia",
    "RAIZ4.SA": "Energia",
    "VBBR3.SA": "Financeiro",
    "GGBR4.SA": "Materiais",
    "SUZB3.SA": "Materiais",
    "HAPV3.SA": "Saúde",
    "COGN3.SA": "Educação",
}

COMPANY_BY_TICKER = {
    "PETR4.SA": "Petrobras",
    "VALE3.SA": "Vale",
    "ITUB4.SA": "Itaú Unibanco",
    "B3SA3.SA": "B3",
    "BBAS3.SA": "Banco do Brasil",
    "ELET3.SA": "Eletrobras",
    "ABEV3.SA": "Ambev",
    "RENT3.SA": "Localiza",
    "MGLU3.SA": "Magazine Luiza",
    "WEGE3.SA": "WEG",
    "EGIE3.SA": "Engie Brasil",
    "SAPR4.SA": "Sanepar",
    "BBSE3.SA": "BB Seguridade",
    "VIVT3.SA": "Vivo",
    "TAEE4.SA": "Taesa",
    "CSMG3.SA": "Copasa",
    "KLBN4.SA": "Klabin",
    "LREN3.SA": "Lojas Renner",
    "RADL3.SA": "Raia Drogasil",
    "PRIO3.SA": "Prio",
    "CSAN3.SA": "Cosan",
    "RAIZ4.SA": "Raízen",
    "VBBR3.SA": "Vibra Energia",
    "GGBR4.SA": "Gerdau",
    "SUZB3.SA": "Suzano",
    "HAPV3.SA": "Hapvida",
    "COGN3.SA": "Cogna",
    "CMIG4.SA": "Cemig",
}

# Financial news feed
FAKE_NEWS = [
    {"title": "Mercado local mostra recuperação de juros e expectativa de fluxo de investimentos em ações brasileiras.", "source": "Valor Econômico", "time": "Há 1h"},
    {"title": "Setor de energia segue em foco com alta de petróleo e disputa por margem nas distribuidoras.", "source": "Estadão", "time": "Há 3h"},
    {"title": "Analistas ajustam projeções de empresas financeiras após aumento de crédito no varejo.", "source": "Bloomberg", "time": "Hoje"},
    {"title": "Commodities e mineração sustentam expectativa de ganhos para carteira nacional em julho.", "source": "Exame", "time": "Ontem"},
]
