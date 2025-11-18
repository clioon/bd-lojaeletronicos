# backend/app.py

from flask import Flask, jsonify, request
from flask_cors import CORS
from mock_data import (
    CLIENTES_MOCK, get_next_id,
    PRODUTOS_MOCK, ESTOQUE_MOCK,
    DESCONTOS_MOCK, HISTORICO_PRECOS_MOCK
)
import datetime

app = Flask(__name__)
CORS(app) 

# --- ROTAS CRUD PARA CLIENTES (Mantidas da resposta anterior, mas com novos campos) ---

@app.route('/api/clientes', methods=['GET', 'POST'])
def clientes():
    if request.method == 'GET':
        return jsonify(CLIENTES_MOCK)
    
    elif request.method == 'POST':
        dados = request.get_json() 
        if not all(k in dados for k in ('nome', 'email')):
            return jsonify({"erro": "Dados de cliente incompletos"}), 400
            
        novo_cliente = {
            "id": get_next_id('cliente'),
            "nome": dados['nome'],
            "email": dados['email'],
            "telefone": dados.get('telefone', 'N/A'),
            "data_cadastro": datetime.date.today().isoformat()
        }
        CLIENTES_MOCK.append(novo_cliente)
        return jsonify(novo_cliente), 201

# ROTAS para GET, PUT, DELETE /api/clientes/<id> (Não alteradas, usam o mesmo padrão)
# ... [O código para gerenciar_cliente(cliente_id) continua o mesmo] ...

# ----------------------------------------------------
# 📌 ROTAS CRUD PARA PRODUTOS
# ----------------------------------------------------

@app.route('/api/produtos', methods=['GET', 'POST'])
def produtos():
    if request.method == 'GET':
        # Retorna a lista de produtos
        return jsonify(PRODUTOS_MOCK)
    
    elif request.method == 'POST':
        dados = request.get_json() 
        if not all(k in dados for k in ('nome', 'preco_atual')):
            return jsonify({"erro": "Dados de produto incompletos"}), 400
            
        novo_produto = {
            "id": get_next_id('produto'),
            "nome": dados['nome'],
            "descricao": dados.get('descricao', ''),
            "preco_atual": float(dados['preco_atual']),
            "data_criacao": datetime.date.today().isoformat()
        }
        PRODUTOS_MOCK.append(novo_produto)
        
        # Simula o registro inicial no estoque e histórico de preços
        ESTOQUE_MOCK.append({"produto_id": novo_produto['id'], "quantidade": 0, "ultima_atualizacao": datetime.datetime.now().isoformat()})
        HISTORICO_PRECOS_MOCK.append({"produto_id": novo_produto['id'], "preco": novo_produto['preco_atual'], "data_registro": novo_produto['data_criacao']})
        
        return jsonify(novo_produto), 201

@app.route('/api/produtos/<int:produto_id>', methods=['GET', 'PUT', 'DELETE'])
def gerenciar_produto(produto_id):
    produto = next((p for p in PRODUTOS_MOCK if p['id'] == produto_id), None)
    if produto is None:
        return jsonify({"erro": f"Produto ID {produto_id} não encontrado"}), 404

    if request.method == 'GET':
        return jsonify(produto)
        
    elif request.method == 'PUT':
        dados_atualizados = request.get_json()
        
        # Atualiza campos
        produto['nome'] = dados_atualizados.get('nome', produto['nome'])
        produto['descricao'] = dados_atualizados.get('descricao', produto['descricao'])
        # NOTA: Preço deve ser atualizado via rota de preço, não aqui, mas incluído para simplicidade
        if 'preco_atual' in dados_atualizados:
            produto['preco_atual'] = float(dados_atualizados['preco_atual'])
        
        return jsonify(produto)

    elif request.method == 'DELETE':
        # Simula a exclusão
        global PRODUTOS_MOCK
        PRODUTOS_MOCK = [p for p in PRODUTOS_MOCK if p['id'] != produto_id]
        
        # Simular a remoção de estoque e histórico (opcional, mas limpa o mock)
        global ESTOQUE_MOCK, HISTORICO_PRECOS_MOCK
        ESTOQUE_MOCK = [e for e in ESTOQUE_MOCK if e['produto_id'] != produto_id]
        HISTORICO_PRECOS_MOCK = [h for h in HISTORICO_PRECOS_MOCK if h['produto_id'] != produto_id]
        
        return '', 204 

# ----------------------------------------------------
# 📌 ROTAS PARA ESTOQUE
# ----------------------------------------------------

@app.route('/api/estoque', methods=['GET'])
def listar_estoque():
    """Retorna a lista completa de estoque (relacionado com produtos)."""
    # Para o frontend, é útil retornar o nome do produto junto com o estoque
    estoque_detalhado = []
    for item_estoque in ESTOQUE_MOCK:
        produto = next((p for p in PRODUTOS_MOCK if p['id'] == item_estoque['produto_id']), {"nome": "Produto Removido"})
        estoque_detalhado.append({
            "produto_id": item_estoque['produto_id'],
            "nome_produto": produto['nome'],
            "quantidade": item_estoque['quantidade'],
            "ultima_atualizacao": item_estoque['ultima_atualizacao']
        })
    return jsonify(estoque_detalhado)

@app.route('/api/estoque/<int:produto_id>', methods=['PUT'])
def atualizar_estoque(produto_id):
    """Atualiza a quantidade em estoque de um produto específico."""
    dados = request.get_json()
    if 'quantidade' not in dados:
        return jsonify({"erro": "O campo 'quantidade' é obrigatório"}), 400

    item_estoque = next((e for e in ESTOQUE_MOCK if e['produto_id'] == produto_id), None)

    if item_estoque is None:
        return jsonify({"erro": f"Estoque para Produto ID {produto_id} não encontrado"}), 404
        
    item_estoque['quantidade'] = int(dados['quantidade'])
    item_estoque['ultima_atualizacao'] = datetime.datetime.now().isoformat()
    
    return jsonify(item_estoque)


# ----------------------------------------------------
# 📌 ROTAS PARA DESCONTOS
# ----------------------------------------------------

@app.route('/api/descontos', methods=['GET', 'POST'])
def descontos():
    if request.method == 'GET':
        return jsonify(DESCONTOS_MOCK)
        
    elif request.method == 'POST':
        dados = request.get_json()
        if not all(k in dados for k in ('nome', 'valor')):
             return jsonify({"erro": "Dados de desconto incompletos"}), 400
             
        novo_desconto = {
            "id": get_next_id('desconto'),
            "nome": dados['nome'],
            "tipo": dados.get('tipo', 'porcentagem'),
            "valor": float(dados['valor']),
            "ativo": dados.get('ativo', True),
            "validade": dados.get('validade', '9999-12-31')
        }
        DESCONTOS_MOCK.append(novo_desconto)
        return jsonify(novo_desconto), 201

# ----------------------------------------------------
# 📌 INICIALIZAÇÃO DO SERVIDOR
# ----------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)