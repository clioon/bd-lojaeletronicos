from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from collections import Counter

app = Flask(__name__)
CORS(app) 

# CONFIGURAÇÃO DO BANCO
DB_CONFIG = {
    'dbname': 'TESTE',
    'user': 'postgres',
    'password': 'abc123',  # <--- COLOQUE SUA SENHA AQUI
    'host': 'localhost',
    'port': '5432'
}


def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Erro de conexão com o Banco: {e}")
        return None

# =================================================================
# ROTA 1: Listar Produtos
# =================================================================
@app.route('/api/produtos', methods=['GET'])
def get_produtos():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Erro ao conectar no banco"}), 500
    
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Query inteligente: Pega dados da tabela PAI (Produto) e junta com as FILHAS
    # Usamos COALESCE para pegar o 'tipo' da tabela específica que não for nula
    query = """
        SELECT 
            p.id_produto as id,
            p.nome_produto as nome,
            p.preco_unitario as preco,
            p.estoque_atual as estoque,
            p.categoria,
            -- Tenta pegar caracteristicas específicas de cada tabela filha
            d.cor as cor_dispositivo,
            h.especificacao_tecnica as specs_hardware,
            per.conexao as conexao_periferico,
            -- Define um tipo para o front saber como tratar
            CASE 
                WHEN d.id_produto IS NOT NULL THEN 'Dispositivo'
                WHEN h.id_produto IS NOT NULL THEN 'Hardware'
                WHEN per.id_produto IS NOT NULL THEN 'Periférico'
                ELSE 'Outro'
            END as tipo_produto
        FROM Produto p
        LEFT JOIN Dispositivo d ON p.id_produto = d.id_produto
        LEFT JOIN Hardware h ON p.id_produto = h.id_produto
        LEFT JOIN Periferico per ON p.id_produto = per.id_produto
        ORDER BY p.id_produto;
    """
    
    cursor.execute(query)
    produtos = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    # O retorno será uma lista de JSONs prontinha para o JS
    return jsonify(produtos)

# =================================================================
# ROTA 2: Listar Clientes
# =================================================================
@app.route('/api/clientes', methods=['GET'])
def get_clientes():
    conn = get_db_connection()
    if not conn: return jsonify({"error": "Erro conexão"}), 500

    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # ATUALIZAÇÃO: Fazemos um LEFT JOIN com a tabela Pedido e usamos COUNT
    # para saber quantas vezes esse cliente já comprou.
    query = """
        SELECT 
            c.id_cliente as id,  
            c.nome_cliente as nome,
            c.cidade || ' - ' || c.estado as local,
            f.pontos_acumulados as pontos,
            COUNT(p.id_pedido) as total_pedidos
        FROM Cliente c
        LEFT JOIN Fidelidade_Cliente f ON c.id_cliente = f.id_cliente
        LEFT JOIN Pedido p ON c.id_cliente = p.id_cliente
        GROUP BY c.id_cliente, c.nome_cliente, c.cidade, c.estado, f.pontos_acumulados;
    """
    cursor.execute(query)
    clientes = cursor.fetchall()
    
    conn.close()
    return jsonify(clientes)

# =================================================================
# ROTA 3: Criar Pedido (Simulação de Checkout)
# =================================================================
@app.route('/api/checkout', methods=['POST'])
def checkout():
    dados = request.json
    conn = get_db_connection()
    
    if not conn:
        return jsonify({"message": "Erro de conexão com o banco"}), 500

    cursor = conn.cursor()

    try:
        # =================================================================
        # 0. PREPARAÇÃO DOS DADOS
        # =================================================================
        id_cliente = dados.get('cliente_id')
        items_recebidos = dados.get('items') # Lista de objetos {id_produto, preco}
        total_front = dados.get('total')
        metodo_pagamento = dados.get('metodo_pagamento') # ex: 'pix', 'cartao_credito'
        dados_desconto = dados.get('desconto') # Pode ser None ou objeto
        
        # Agrupa itens iguais para definir quantidade (Ex: 2x Mouse)
        # Cria um dicionario: { id_produto: {qtd: 2, preco: 100} }
        carrinho_processado = {}
        for item in items_recebidos:
            pid = item['id_produto']
            preco = item['preco']
            if pid in carrinho_processado:
                carrinho_processado[pid]['qtd'] += 1
            else:
                carrinho_processado[pid] = {'qtd': 1, 'preco': preco}

        # Calcula pontos (Exemplo: 1 ponto a cada R$ 10 gastos)
        pontos_ganhos = int(total_front / 10)
        
        # Datas
        data_hoje = datetime.now().date()
        prazo_entrega = datetime.now().date() # Em um sistema real, somaria dias

        # =================================================================
        # 1. INSERIR PEDIDO
        # =================================================================
        sql_pedido = """
            INSERT INTO Pedido (data_pedido, prazo_estimado, status_pedido, prioridade_pedido, modo_envio, id_cliente, pontos_fidelidade_gerados)
            VALUES (%s, %s, 'concluido', 'media', 'entrega', %s, %s)
            RETURNING id_pedido;
        """
        cursor.execute(sql_pedido, (data_hoje, prazo_entrega, id_cliente, pontos_ganhos))
        id_pedido = cursor.fetchone()[0] # Pega o ID gerado

        # =================================================================
        # 2. INSERIR ITENS E BAIXAR ESTOQUE
        # =================================================================
        subtotal_calculado = 0
        
        for pid, info in carrinho_processado.items():
            qtd = info['qtd']
            preco_unit = info['preco']
            total_item = qtd * preco_unit
            subtotal_calculado += total_item
            
            # A) Inserir na tabela de junção
            cursor.execute("""
                INSERT INTO Item_Pedido (id_pedido, id_produto, quantidade, preco_unitario, valor_total_item)
                VALUES (%s, %s, %s, %s, %s)
            """, (id_pedido, pid, qtd, preco_unit, total_item))
            
            # B) Baixar estoque na tabela Produto
            # Verifica se tem estoque antes
            cursor.execute("SELECT estoque_atual FROM Produto WHERE id_produto = %s", (pid,))
            estoque_atual = cursor.fetchone()[0]
            
            if estoque_atual < qtd:
                raise Exception(f"Produto ID {pid} sem estoque suficiente!")
                
            cursor.execute("""
                UPDATE Produto SET estoque_atual = estoque_atual - %s 
                WHERE id_produto = %s
            """, (qtd, pid))

        # =================================================================
        # 3. INSERIR VENDA (Financeiro)
        # =================================================================
        # Definindo valores fixos para simplificar (num sistema real seriam calculados)
        custo_envio = 20.00 
        imposto_loja = total_front * 0.10 # 10%
        taxa_pagamento = 5.00
        frete_cobrado = 20.00
        
        valor_desconto = 0
        if dados_desconto:
            # Se for porcentagem, calcula. Aqui assumo que o front ja mandou o total com desconto
            # Então calculamos a diferença do subtotal
            valor_desconto = (subtotal_calculado + frete_cobrado) - total_front

        sql_venda = """
            INSERT INTO Venda (id_pedido, custo_envio, custo_imposto_loja, custo_taxa_pagamento, valor_frete, valor_imposto_cliente, subtotal, valor_desconto, valor_total)
            VALUES (%s, %s, %s, %s, %s, 0, %s, %s, %s)
        """
        cursor.execute(sql_venda, (id_pedido, custo_envio, imposto_loja, taxa_pagamento, frete_cobrado, subtotal_calculado, valor_desconto, total_front))

        # # =================================================================
        # # 4. REGISTRAR DESCONTO (Se houver)
        # # =================================================================
        # if dados_desconto:
        #     cursor.execute("""
        #         INSERT INTO Desconto_Aplicado (id_pedido, tipo, porcentagem, descricao)
        #         VALUES (%s, 'promocional', %s, %s)
        #     """, (id_pedido, dados_desconto.get('valor', 0), dados_desconto.get('tipo', 'Cupom')))

        # =================================================================
        # 5. INSERIR PAGAMENTO
        # =================================================================
        # Mapear string do front para ENUM do banco se necessário
        # Assumindo que o front manda: 'pix', 'cartao_credito', etc iguais ao ENUM
        
        sql_pagamento = """
            INSERT INTO Pagamento (id_pedido, forma_pagamento, parcelas, data_pagamento, valor_pago)
            VALUES (%s, %s, 1, %s, %s)
        """
        cursor.execute(sql_pagamento, (id_pedido, metodo_pagamento, data_hoje, total_front))

        # =================================================================
        # 6. ATUALIZAR FIDELIDADE DO CLIENTE
        # =================================================================
        # Verifica se cliente ja tem registro na tabela fidelidade
        cursor.execute("SELECT id_cliente FROM Fidelidade_Cliente WHERE id_cliente = %s", (id_cliente,))
        if cursor.fetchone():
            cursor.execute("""
                UPDATE Fidelidade_Cliente 
                SET pontos_acumulados = pontos_acumulados + %s 
                WHERE id_cliente = %s
            """, (pontos_ganhos, id_cliente))
        else:
            cursor.execute("""
                INSERT INTO Fidelidade_Cliente (id_cliente, pontos_acumulados)
                VALUES (%s, %s)
            """, (id_cliente, pontos_ganhos))

        # =================================================================
        # SUCESSO TOTAL: CONFIRMA A TRANSAÇÃO
        # =================================================================
        conn.commit()
        print(f"Venda {id_pedido} realizada com sucesso!")
        
        return jsonify({
            "message": "Compra realizada com sucesso!",
            "id_pedido": id_pedido,
            "pontos_ganhos": pontos_ganhos
        }), 201

    except Exception as e:
        # Se DEU ERRO em qualquer etapa acima, desfaz tudo!
        conn.rollback()
        print(f"Erro na transação: {e}")
        return jsonify({"message": f"Erro ao processar compra: {str(e)}"}), 500
    
    finally:
        cursor.close()
        conn.close()

# =================================================================
# ROTA 4: Listar Descontos
# =================================================================
@app.route('/api/descontos', methods=['GET'])
def get_descontos():
    conn = get_db_connection()
    if not conn: return jsonify([]), 500

    cursor = conn.cursor(cursor_factory=RealDictCursor)
    # Busca apenas descontos que estão marcados como ativos
    cursor.execute("SELECT * FROM desconto_aplicado")
    descontos = cursor.fetchall()

    conn.close()
    return jsonify(descontos)

# =================================================================
# ROTA 5: Clientes com mais de 100 pontos
# =================================================================
@app.route('/api/clientes/fidelidade', methods=['GET'])
def get_clientes_fidelidade():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Busca clientes que tenham > 100 pontos na tabela fidelidade
    query = """
        SELECT c.id_cliente, c.nome_cliente 
        FROM Cliente c
        JOIN Fidelidade_Cliente f ON c.id_cliente = f.id_cliente
        WHERE f.pontos_acumulados > 100
    """
    cursor.execute(query)
    clientes_vip = cursor.fetchall()
    
    conn.close()
    return jsonify(clientes_vip)
    
# =================================================================
# ROTA 6: Clientes com pelo menos 2 compras de periféricos
# =================================================================
@app.route('/api/clientes/promocional', methods=['GET'])
def get_clientes_promocional():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Query um pouco mais complexa: Conta quantos itens do tipo 'Periferico' cada um comprou
    # e usa HAVING para filtrar só quem tem >= 2
    query = """
        SELECT c.id_cliente, c.nome_cliente
        FROM Cliente c
        JOIN Pedido p ON c.id_cliente = p.id_cliente
        JOIN Item_Pedido i ON p.id_pedido = i.id_pedido
        JOIN Periferico per ON i.id_produto = per.id_produto
        GROUP BY c.id_cliente, c.nome_cliente
        HAVING COUNT(*) >= 2
    """
    cursor.execute(query)
    clientes_promo = cursor.fetchall()
    
    conn.close()
    return jsonify(clientes_promo)

# =================================================================
# ROTA 7: Clientes sem pedidos
# =================================================================
@app.route('/api/clientes/primeira-compra', methods=['GET'])
def get_clientes_primeira_compra():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Seleciona Clientes onde NÃO existe correspondência na tabela Pedidos
    query = """
        SELECT c.id_cliente, c.nome_cliente
        FROM Cliente c
        LEFT JOIN Pedido p ON c.id_cliente = p.id_cliente
        WHERE p.id_pedido IS NULL
    """
    cursor.execute(query)
    clientes_novos = cursor.fetchall()
    
    conn.close()
    return jsonify(clientes_novos)


# =================================================================
# ROTA 8: Recomendacoes de produtos
# =================================================================
@app.route('/api/produtos/<int:id_produto>/recomendacoes', methods=['GET'])
def get_recomendacoes(id_produto):
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    query = """
        SELECT 
            p.id_produto,
            p.nome_produto as nome,
            p.preco_unitario as preco,
            p.categoria,
            COUNT(*) as relevancia
        FROM Item_Pedido item_A
        JOIN Item_Pedido item_B ON item_A.id_pedido = item_B.id_pedido
        JOIN Produto p ON item_B.id_produto = p.id_produto
        WHERE item_A.id_produto = %s
          AND item_B.id_produto != %s
        GROUP BY p.id_produto, p.nome_produto, p.preco_unitario, p.categoria
        ORDER BY relevancia DESC
        LIMIT 3;
    """
    
    cursor.execute(query, (id_produto, id_produto))
    sugestoes = cursor.fetchall()

    # FALLBACK (Plano B)
    # Se a query acima não retornar nada (produto novo ou poucas vendas),
    # retornamos 3 produtos da mesma categoria para não deixar vazio.
    if not sugestoes:
        cursor.execute("""
            SELECT id_produto, nome_produto as nome, preco_unitario as preco, tipo
            FROM Produto 
            WHERE id_produto != %s 
            ORDER BY RANDOM() 
            LIMIT 3
        """, (id_produto,))
        sugestoes = cursor.fetchall()

    conn.close()
    return jsonify(sugestoes)





if __name__ == '__main__':
    print("Servidor rodando na porta 5000...")
    app.run(debug=True, port=5000)