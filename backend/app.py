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
    'dbname': 'loja_vendas',
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

        # =================================================================
        # 4. REGISTRAR DESCONTO (Se houver)
        # =================================================================
        if dados_desconto:
            cursor.execute("""
                INSERT INTO Desconto_Aplicado (id_pedido, tipo, porcentagem, descricao)
                VALUES (%s, %s, %s, %s)
            """, (id_pedido, dados_desconto.get('tipo', 'promocional'), dados_desconto.get('valor', 0), dados_desconto.get('descricao', 'desconto aplicado')))

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
# ROTA 8: Clientes que já compraram no passado, mas não fazem pedidos há mais de 6 meses
# =================================================================

@app.route('/api/clientes/inativos', methods=['GET'])
def get_clientes_inativos():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # Seleciona clientes cuja ÚLTIMA compra foi há mais de 6 meses
    # CURRENT_DATE - INTERVAL '6 months' calcula a data limite
    query = """
        SELECT c.id_cliente, c.nome_cliente, MAX(p.data_pedido) as ultima_compra
        FROM Cliente c
        JOIN Pedido p ON c.id_cliente = p.id_cliente
        GROUP BY c.id_cliente, c.nome_cliente
        HAVING MAX(p.data_pedido) < CURRENT_DATE - INTERVAL '6 months'
        ORDER BY ultima_compra ASC
    """
    cursor.execute(query)
    clientes = cursor.fetchall()
    
    conn.close()
    return jsonify(clientes)

# =================================================================
# ROTA 9: Clientes cujo gasto médio por pedido é superior à média geral de todos os pedidos da loja
# =================================================================

@app.route('/api/clientes/high-ticket', methods=['GET'])
def get_clientes_high_ticket():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # 1. Calcula a média de TODAS as vendas da loja (Subquery)
    # 2. Agrupa os pedidos por cliente
    # 3. Filtra (HAVING) apenas quem tem média pessoal maior que a média global
    query = """
        SELECT c.id_cliente, c.nome_cliente, 
               ROUND(AVG(v.valor_total), 2) as ticket_medio_cliente
        FROM Cliente c
        JOIN Pedido p ON c.id_cliente = p.id_cliente
        JOIN Venda v ON p.id_pedido = v.id_pedido
        GROUP BY c.id_cliente, c.nome_cliente
        HAVING AVG(v.valor_total) > (
            SELECT AVG(valor_total) FROM Venda
        )
        ORDER BY ticket_medio_cliente DESC
    """
    cursor.execute(query)
    clientes = cursor.fetchall()
    
    conn.close()
    return jsonify(clientes)

# =================================================================
# ROTA 10: Recomendacoes de produtos
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

# =================================================================
# ROTA: Vendas por categoria
# =================================================================
@app.route('/api/graficos/vendas-por-categoria', methods=['GET'])
def vendas_por_categoria():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT p.categoria, SUM(i.valor_total_item) AS total
        FROM Item_Pedido i
        JOIN Produto p ON p.id_produto = i.id_produto
        GROUP BY p.categoria
        ORDER BY total DESC;
    """

    cursor.execute(query)
    dados = cursor.fetchall()

    conn.close()

    # Converter para formato que o frontend já entende
    resposta = {
        "categorias": [row["categoria"] for row in dados],
        "totais":     [float(row["total"]) for row in dados]
    }

    return jsonify(resposta)

# =================================================================
# ROTA: Pedidos por mês
# =================================================================
@app.route('/api/graficos/pedidos-por-mes', methods=['GET'])
def pedidos_por_mes():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT 
            TO_CHAR(data_pedido, 'YYYY-MM') AS mes,
            COUNT(*) AS total
        FROM Pedido
        GROUP BY mes
        ORDER BY mes;
    """

    cursor.execute(query)
    dados = cursor.fetchall()
    conn.close()

    return jsonify({
        "meses": [row["mes"] for row in dados],
        "total": [row["total"] for row in dados]
    })

# =================================================================
# ROTA: Quantidade de Produtos Vendidos
# =================================================================
@app.route('/api/graficos/top-produtos', methods=['GET'])
def top_produtos():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT p.nome_produto AS nome, SUM(i.quantidade) AS qtd
        FROM Item_Pedido i
        JOIN Produto p ON p.id_produto = i.id_produto
        GROUP BY nome
        ORDER BY qtd DESC
        LIMIT 5;
    """

    cursor.execute(query)
    dados = cursor.fetchall()
    conn.close()

    return jsonify({
        "produtos": [row["nome"] for row in dados],
        "quantidades": [row["qtd"] for row in dados]
    })

# =================================================================
# ROTA: Vendas por Produto (Top 10)
# =================================================================
@app.route('/api/graficos/vendas-por-produto', methods=['GET'])
def vendas_por_produto():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT 
            p.nome_produto,
            SUM(i.quantidade) AS total_vendido
        FROM Item_Pedido i
        JOIN Produto p ON p.id_produto = i.id_produto
        GROUP BY p.nome_produto
        ORDER BY total_vendido DESC
        LIMIT 10;
    """

    cursor.execute(query)
    dados = cursor.fetchall()
    conn.close()

    resposta = {
        "produtos": [row["nome_produto"] for row in dados],
        "quantidades": [int(row["total_vendido"]) for row in dados]
    }

    return jsonify(resposta)

    # =================================================================
# ROTA: Faturamento por Cliente (Top 10)
# =================================================================
@app.route('/api/graficos/faturamento-por-cliente', methods=['GET'])
def faturamento_por_cliente():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT 
            c.nome_cliente,
            SUM(v.valor_total) AS total_gasto
        FROM Venda v
        JOIN Pedido p ON p.id_pedido = v.id_pedido
        JOIN Cliente c ON c.id_cliente = p.id_cliente
        GROUP BY c.nome_cliente
        ORDER BY total_gasto DESC
        LIMIT 10;
    """

    cursor.execute(query)
    dados = cursor.fetchall()
    conn.close()

    resposta = {
        "clientes": [row["nome_cliente"] for row in dados],
        "totais":   [float(row["total_gasto"]) for row in dados]
    }

    return jsonify(resposta)

    # =================================================================
# ROTA: Pedidos por Status
# =================================================================
@app.route('/api/graficos/pedidos-por-status', methods=['GET'])
def pedidos_por_status():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT 
            status_pedido,
            COUNT(*) AS quantidade
        FROM Pedido
        GROUP BY status_pedido
        ORDER BY status_pedido;
    """

    cursor.execute(query)
    dados = cursor.fetchall()
    conn.close()

    resposta = {
        "status":      [row["status_pedido"] for row in dados],
        "quantidades": [int(row["quantidade"]) for row in dados]
    }

    return jsonify(resposta)

# =================================================================
# ROTA: Pedidos por Prioridade
# =================================================================
@app.route('/api/graficos/pedidos-por-prioridade', methods=['GET'])
def pedidos_por_prioridade():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT 
            prioridade_pedido,
            COUNT(*) AS quantidade
        FROM Pedido
        GROUP BY prioridade_pedido
        ORDER BY prioridade_pedido;
    """

    cursor.execute(query)
    dados = cursor.fetchall()
    conn.close()

    resposta = {
        "prioridades": [row["prioridade_pedido"] for row in dados],
        "quantidades": [int(row["quantidade"]) for row in dados]
    }

    return jsonify(resposta)

# =================================================================
# ROTA: Vendas por Forma de Pagamento
# =================================================================
@app.route('/api/graficos/vendas-por-forma-pagamento', methods=['GET'])
def vendas_por_forma_pagamento():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT 
            forma_pagamento,
            COUNT(*) AS quantidade
        FROM Pagamento
        GROUP BY forma_pagamento
        ORDER BY forma_pagamento;
    """

    cursor.execute(query)
    dados = cursor.fetchall()
    conn.close()

    resposta = {
        "formas":      [row["forma_pagamento"] for row in dados],
        "quantidades": [int(row["quantidade"]) for row in dados]
    }

    return jsonify(resposta)

# =================================================================
# ROTA: Estoque Atual x Estoque Mínimo
# =================================================================
@app.route('/api/graficos/estoque-minimo-atual', methods=['GET'])
def estoque_minimo_atual():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT 
            nome_produto,
            estoque_atual,
            estoque_minimo
        FROM Produto
        ORDER BY nome_produto;
    """

    cursor.execute(query)
    dados = cursor.fetchall()
    conn.close()

    resposta = {
        "produtos": [row["nome_produto"] for row in dados],
        "atual":    [int(row["estoque_atual"]) for row in dados],
        "minimo":   [int(row["estoque_minimo"]) for row in dados]
    }

    return jsonify(resposta)

# =================================================================
# ROTA: Pedidos por Estado
# =================================================================
@app.route('/api/graficos/pedidos-por-estado', methods=['GET'])
def pedidos_por_estado():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT 
            c.estado,
            COUNT(*) AS quantidade
        FROM Pedido p
        JOIN Cliente c ON c.id_cliente = p.id_cliente
        GROUP BY c.estado
        ORDER BY quantidade DESC;
    """

    cursor.execute(query)
    dados = cursor.fetchall()
    conn.close()

    resposta = {
        "estados":     [row["estado"] for row in dados],
        "quantidades": [int(row["quantidade"]) for row in dados]
    }

    return jsonify(resposta)

# =================================================================
# ROTA: Ticket Médio por Mês
# =================================================================
@app.route('/api/graficos/ticket-medio-mensal', methods=['GET'])
def ticket_medio_mensal():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT 
            TO_CHAR(DATE_TRUNC('month', p.data_pedido), 'YYYY-MM') AS mes,
            ROUND(SUM(v.valor_total) / COUNT(p.id_pedido), 2) AS ticket_medio
        FROM Pedido p
        JOIN Venda v ON v.id_pedido = p.id_pedido
        GROUP BY DATE_TRUNC('month', p.data_pedido)
        ORDER BY DATE_TRUNC('month', p.data_pedido);
    """

    cursor.execute(query)
    dados = cursor.fetchall()
    conn.close()

    resposta = {
        "meses":  [row["mes"] for row in dados],
        "tickets": [float(row["ticket_medio"]) for row in dados]
    }

    return jsonify(resposta)

# =================================================================
# ROTA: Lucro por Produto (Top 10)
# =================================================================
@app.route('/api/graficos/lucro-por-produto', methods=['GET'])
def lucro_por_produto():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        SELECT 
            p.nome_produto,
            ROUND(SUM((p.preco_unitario - p.custo_unitario) * i.quantidade), 2) AS lucro_total
        FROM Item_Pedido i
        JOIN Produto p ON p.id_produto = i.id_produto
        GROUP BY p.nome_produto
        HAVING SUM(i.quantidade) > 0
        ORDER BY lucro_total DESC
        LIMIT 10;
    """

    cursor.execute(query)
    dados = cursor.fetchall()
    conn.close()

    resposta = {
        "produtos": [row["nome_produto"] for row in dados],
        "lucros":   [float(row["lucro_total"]) for row in dados]
    }

    return jsonify(resposta)

# =================================================================
# ROTA: Curva ABC de Produtos (Pareto)
# =================================================================
# @app.route('/api/graficos/curva-abc', methods=['GET'])
# def curva_abc():
#     conn = get_db_connection()
#     cursor = conn.cursor(cursor_factory=RealDictCursor)

#     query = """
#         WITH faturamento AS (
#             SELECT
#                 p.nome_produto,
#                 SUM(i.valor_total_item) AS receita
#             FROM Item_Pedido i
#             JOIN Produto p ON p.id_produto = i.id_produto
#             GROUP BY p.nome_produto
#         ),
#         acumulado AS (
#             SELECT 
#                 nome_produto,
#                 receita,
#                 receita / SUM(receita) OVER() AS perc_individual,
#                 SUM(receita) OVER(ORDER BY receita DESC) / SUM(receita) OVER() AS perc_acumulado
#             FROM faturamento
#             ORDER BY receita DESC
#         )
#         SELECT
#             nome_produto,
#             ROUND(receita, 2) AS receita,
#             ROUND(perc_individual * 100, 2) AS perc_individual,
#             ROUND(perc_acumulado * 100, 2) AS perc_acumulado,
#             CASE 
#                 WHEN perc_acumulado <= 0.80 THEN 'A'
#                 WHEN perc_acumulado <= 0.95 THEN 'B'
#                 ELSE 'C'
#             END AS classe
#         FROM acumulado;
#     """

#     cursor.execute(query)
#     dados = cursor.fetchall()
#     conn.close()

#     resposta = {
#         "produtos":       [row["nome_produto"] for row in dados],
#         "receitas":       [float(row["receita"]) for row in dados],
#         "perc_acum":      [float(row["perc_acumulado"]) for row in dados],
#         "classes":        [row["classe"] for row in dados]
#     }

#     return jsonify(resposta)

# =================================================================
# ROTA: Dias Médios Entre Compras por Cliente
# =================================================================
@app.route('/api/graficos/recorrencia-clientes', methods=['GET'])
def recorrencia_clientes():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        WITH compras AS (
            SELECT 
                p.id_cliente,
                c.nome_cliente,
                p.data_pedido,
                LAG(p.data_pedido) OVER (
                    PARTITION BY p.id_cliente
                    ORDER BY p.data_pedido
                ) AS compra_anterior
            FROM Pedido p
            JOIN Cliente c ON c.id_cliente = p.id_cliente
        ),
        diffs AS (
            SELECT
                nome_cliente,
                EXTRACT(
                    EPOCH FROM (
                        CAST(data_pedido AS timestamp) 
                        - CAST(compra_anterior AS timestamp)
                    )
                ) / 86400 AS dias
            FROM compras
            WHERE compra_anterior IS NOT NULL
        )
        SELECT 
            nome_cliente,
            ROUND(AVG(dias), 2) AS dias_medio
        FROM diffs
        GROUP BY nome_cliente
        HAVING AVG(dias) IS NOT NULL
        ORDER BY dias_medio ASC
        LIMIT 20;
    """



    cursor.execute(query)
    dados = cursor.fetchall()
    conn.close()

    resposta = {
        "clientes": [row["nome_cliente"] for row in dados],
        "dias":     [float(row["dias_medio"]) for row in dados]
    }

    return jsonify(resposta)

# =================================================================
# ROTA: Média Mensal de Dias Entre Compras
# =================================================================
@app.route('/api/graficos/recorrencia-mensal', methods=['GET'])
def recorrencia_mensal():
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    query = """
        WITH compras AS (
            SELECT 
                p.id_cliente,
                p.data_pedido,
                LAG(p.data_pedido) OVER (
                    PARTITION BY p.id_cliente
                    ORDER BY p.data_pedido
                ) AS compra_anterior
            FROM Pedido p
        ),
        diffs AS (
            SELECT
                DATE_TRUNC('month', data_pedido) AS mes,
                EXTRACT(
                    EPOCH FROM (
                        CAST(data_pedido AS timestamp) 
                        - CAST(compra_anterior AS timestamp)
                    )
                ) / 86400 AS dias
            FROM compras
            WHERE compra_anterior IS NOT NULL
        )
        SELECT
            TO_CHAR(mes, 'YYYY-MM') AS mes_formatado,
            ROUND(AVG(dias), 2) AS dias_medio
        FROM diffs
        GROUP BY mes
        ORDER BY mes;
    """

    cursor.execute(query)
    dados = cursor.fetchall()
    conn.close()

    resposta = {
        "meses": [row["mes_formatado"] for row in dados],
        "dias":  [float(row["dias_medio"]) for row in dados]
    }

    return jsonify(resposta)



if __name__ == '__main__':
    print("Servidor rodando na porta 5000...")
    app.run(debug=True, port=5000)
