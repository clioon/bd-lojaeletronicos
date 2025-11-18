# backend/mock_data.py

import datetime

# --- Variáveis de Controle de ID (Simulação de Auto-Incremento) ---
next_client_id = 4
next_produto_id = 4
next_desconto_id = 3

def get_next_id(entity):
    """Função para simular o auto-incremento de ID para cada entidade."""
    global next_client_id, next_produto_id, next_desconto_id
    
    if entity == 'cliente':
        current_id = next_client_id
        next_client_id += 1
        return current_id
    elif entity == 'produto':
        current_id = next_produto_id
        next_produto_id += 1
        return current_id
    elif entity == 'desconto':
        current_id = next_desconto_id
        next_desconto_id += 1
        return current_id
    return None

# --- Mock Data para Clientes ---
CLIENTES_MOCK = [
    {"id": 1, "nome": "Ana Souza", "email": "ana.souza@email.com", "telefone": "11988887777", "data_cadastro": "2024-01-15"},
    {"id": 2, "nome": "Bruno Costa", "email": "bruno.costa@email.com", "telefone": "21999996666", "data_cadastro": "2024-03-01"},
    {"id": 3, "nome": "Carla Lima", "email": "carla.lima@email.com", "telefone": "31977775555", "data_cadastro": "2024-05-20"}
]

# --- Mock Data para Produtos ---
PRODUTOS_MOCK = [
    {"id": 1, "nome": "Tênis Esportivo", "descricao": "Tênis leve para corrida", "preco_atual": 249.90, "data_criacao": "2024-01-10"},
    {"id": 2, "nome": "Camiseta Básica", "descricao": "Camiseta 100% algodão", "preco_atual": 59.90, "data_criacao": "2024-01-10"},
    {"id": 3, "nome": "Mochila de Couro", "descricao": "Mochila para notebook", "preco_atual": 450.00, "data_criacao": "2024-03-25"}
]

# --- Mock Data para Estoque ---
# Relaciona o produto com a quantidade em estoque
ESTOQUE_MOCK = [
    {"produto_id": 1, "quantidade": 50, "ultima_atualizacao": "2025-11-18 10:00:00"},
    {"produto_id": 2, "quantidade": 200, "ultima_atualizacao": "2025-11-17 09:30:00"},
    {"produto_id": 3, "quantidade": 15, "ultima_atualizacao": "2025-11-18 12:45:00"}
]

# --- Mock Data para Histórico de Preços ---
# Simula a tabela de histórico (para a funcionalidade "Gerenciar preço")
HISTORICO_PRECOS_MOCK = [
    {"produto_id": 1, "preco": 200.00, "data_registro": "2023-12-01"},
    {"produto_id": 1, "preco": 249.90, "data_registro": "2024-01-10"},
    {"produto_id": 3, "preco": 400.00, "data_registro": "2024-03-01"},
    {"produto_id": 3, "preco": 450.00, "data_registro": "2024-03-25"}
]


# --- Mock Data para Descontos ---
DESCONTOS_MOCK = [
    {"id": 1, "nome": "Black Friday", "tipo": "porcentagem", "valor": 0.25, "ativo": True, "validade": "2025-11-29"}, # 25% off
    {"id": 2, "nome": "Liquidação Verão", "tipo": "valor", "valor": 50.00, "ativo": False, "validade": "2025-02-28"} # R$ 50 off
]