#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 19 11:08:13 2025

@author: pablo
"""
from sqlalchemy import text  # para executar SQL com parâmetros
from faker import Faker       # para gerar dados (ex.: clientes) — usar depois
import random                 # útil para gerar quantidades/valores aleatórios
from datetime import datetime, timedelta   # útil para datas aleatórias futuramente
from decimal import Decimal


####################################################################################################################
###                                             CONFIGURACOES INICIAIS                                           ###
####################################################################################################################

fake = Faker("pt_BR")  # inicializa faker apenas uma vez

####################################################################################################################
###                                                   PRODUTO                                                    ###
####################################################################################################################
def popular_produto(engine):
    """
    Popula a tabela Produto com uma lista fixa de produtos predefinidos.
    """

    produtos = [
        
    # DISPOSITIVOS
    ("Samsung Galaxy A54", "Dispositivo", 1999.90, 1200.00, 50, 10),
    ("iPhone 13", "Dispositivo", 3999.90, 2500.00, 30, 5),
    ("Xiaomi Redmi Note 12", "Dispositivo", 1499.90, 900.00, 45, 8),
    ("Motorola Moto G73", "Dispositivo", 1699.90, 1100.00, 40, 8),
    ("iPad 9ª Geração", "Dispositivo", 2499.90, 1600.00, 25, 5),
    ("Samsung Tablet S6 Lite", "Dispositivo", 1599.90, 900.00, 40, 8),

    # HARDWARE
    ("Processador Intel i5 12400F", "Hardware", 899.90, 550.00, 30, 5),
    ("Placa-mãe ASUS B450M", "Hardware", 599.90, 350.00, 20, 3),
    ("Memória RAM 16GB DDR4", "Hardware", 299.90, 150.00, 50, 10),
    ("SSD Kingston 480GB", "Hardware", 229.90, 120.00, 60, 15),
    ("Fonte Corsair 650W", "Hardware", 449.90, 270.00, 25, 5),
    ("Placa de Vídeo RTX 3060", "Hardware", 1999.90, 1350.00, 15, 2),
    ("Cooler Master Airflow", "Hardware", 129.90, 60.00, 40, 10),
    ("Gabinete RGB Mid Tower", "Hardware", 349.90, 180.00, 18, 4),

    # PERIFÉRICOS
    ("Mouse Logitech M90", "Periférico", 49.90, 20.00, 100, 20),
    ("Mouse Razer DeathAdder", "Periférico", 249.90, 120.00, 70, 15),
    ("Teclado Mecânico Redragon Kumara", "Periférico", 299.90, 150.00, 80, 10),
    ("Teclado Logitech K120", "Periférico", 79.90, 30.00, 120, 20),
    ("Headset HyperX Stinger", "Periférico", 399.90, 220.00, 60, 10),
    ("Headset Logitech G332", "Periférico", 349.90, 180.00, 55, 10),
    ("Webcam Logitech C270", "Periférico", 199.90, 80.00, 70, 10),
    ("Controle Xbox Series", "Periférico", 349.90, 200.00, 50, 8)
]

    sql_insert = """
        INSERT INTO Produto
        (nome_produto, categoria, preco_unitario, custo_unitario, estoque_atual, estoque_minimo)
        VALUES (:nome, :categoria, :preco, :custo, :estoque, :estoque_min);
    """

    # Verifica se já existe algo na tabela
    sql_check = "SELECT COUNT(*) FROM Produto;"

    with engine.connect() as conn:
        qtd = conn.execute(text(sql_check)).scalar()

        # Não duplica produtos se já estiver populado
        if qtd > 0:
            print("Produto já populado. Nenhuma inserção feita.")
            return

        # Insere os produtos fixos
        for p in produtos:
            conn.execute(
                text(sql_insert),
                {
                    "nome": p[0],
                    "categoria": p[1],
                    "preco": p[2],
                    "custo": p[3],
                    "estoque": p[4],
                    "estoque_min": p[5]
                }
            )

        conn.commit()

    print(f"Produto populado: {len(produtos)} produtos inseridos.")
    
####################################################################################################################
###                                                 DISPOSITIVO                                                  ###
####################################################################################################################
def popular_dispositivo(engine):
    """
    Popula a tabela Dispositivo para todos os produtos cuja categoria é 'Dispositivo'.
    Não duplica registros caso já existam.
    """

    # Busca todos os produtos da categoria Dispositivo que ainda não existem na tabela Dispositivo
    sql_busca = """
        SELECT id_produto, nome_produto
        FROM Produto
        WHERE categoria = 'Dispositivo'
        AND id_produto NOT IN (SELECT id_produto FROM Dispositivo);
    """

    # Inserção
    sql_insert = """
        INSERT INTO Dispositivo (id_produto, cor, dimensao, tipo)
        VALUES (:id_produto, :cor, :dimensao, :tipo);
    """

    cores = ["Preto", "Branco", "Cinza", "Azul"]
    tipos_dispositivo = {
        "Galaxy": "Smartphone",
        "iPhone": "Smartphone",
        "Xiaomi": "Smartphone",
        "Motorola": "Smartphone",
        "iPad": "Tablet",
        "Tablet": "Tablet"
    }

    with engine.connect() as conn:
        produtos = conn.execute(text(sql_busca)).fetchall()

        for prod in produtos:
            id_produto, nome = prod

            # Determina automaticamente o tipo
            tipo = "Smartphone"  # padrão
            for chave, valor in tipos_dispositivo.items():
                if chave.lower() in nome.lower():
                    tipo = valor
                    break

            conn.execute(
                text(sql_insert),
                {
                    "id_produto": id_produto,
                    "cor": cores[id_produto % len(cores)],
                    "dimensao": "14x7 cm" if tipo == "Smartphone" else "25x17 cm",
                    "tipo": tipo
                }
            )

        conn.commit()

    print(f"Dispositivo populado: {len(produtos)} registros adicionados.")
    
####################################################################################################################
###                                                   HARDWARE                                                   ###
####################################################################################################################
def popular_hardware(engine):
    """
    Popula a tabela Hardware para todos os produtos cuja categoria é 'Hardware'.
    Os tipos são determinados automaticamente com base no nome do produto.
    Não duplica registros caso já existam.
    """

    # Seleciona produtos de Hardware que ainda não foram inseridos na tabela Hardware
    sql_busca = """
        SELECT id_produto, nome_produto
        FROM Produto
        WHERE categoria = 'Hardware'
        AND id_produto NOT IN (SELECT id_produto FROM Hardware);
    """

    # Inserção no Hardware
    sql_insert = """
        INSERT INTO Hardware (id_produto, consumo_energia, especificacao_tecnica, tipo)
        VALUES (:id_produto, :consumo, :especificacao, :tipo);
    """

    # Tipos detectados automaticamente com base no nome
    tipos_hardware = {
        "Processador": "CPU",
        "Placa-mãe": "Placa-mãe",
        "Memória": "RAM",
        "SSD": "SSD",
        "Fonte": "Fonte",
        "Vídeo": "GPU",
        "Cooler": "Cooler",
        "Gabinete": "Gabinete"
    }

    with engine.connect() as conn:
        produtos = conn.execute(text(sql_busca)).fetchall()

        for prod in produtos:
            id_produto, nome = prod

            # Descobre tipo automaticamente
            tipo = "Outro"
            for chave, t in tipos_hardware.items():
                if chave.lower() in nome.lower():
                    tipo = t
                    break

            # Consumo de energia aproximado por tipo (Watts)
            consumo_map = {
                "CPU": 65,
                "Placa-mãe": 50,
                "RAM": 10,
                "SSD": 5,
                "Fonte": 650,
                "GPU": 170,
                "Cooler": 7,
                "Gabinete": 0,
                "Outro": 15
            }

            consumo = consumo_map.get(tipo, 20)

            # Especificação padrão (simples)
            especificacao = f"Componente do tipo {tipo}"

            conn.execute(
                text(sql_insert),
                {
                    "id_produto": id_produto,
                    "consumo": consumo,
                    "especificacao": especificacao,
                    "tipo": tipo
                }
            )

        conn.commit()

    print(f"Hardware populado: {len(produtos)} registros adicionados.")

####################################################################################################################
###                                                  PERIFERICO                                                  ###
####################################################################################################################
def popular_periferico(engine):
    """
    Popula a tabela Periferico para todos os produtos cuja categoria é 'Periférico'.
    O tipo é detectado automaticamente com base no nome do produto.
    Não duplica registros.
    """

    # Seleciona os produtos que são periféricos e ainda não foram inseridos
    sql_busca = """
        SELECT id_produto, nome_produto
        FROM Produto
        WHERE categoria = 'Periférico'
        AND id_produto NOT IN (SELECT id_produto FROM Periferico);
    """

    # Inserção
    sql_insert = """
        INSERT INTO Periferico (id_produto, cor, conexao, tipo)
        VALUES (:id_produto, :cor, :conexao, :tipo);
    """

    cores = ["Preto", "Branco", "Cinza", "Vermelho"]
    conexoes = ["USB", "Bluetooth", "Sem Fio", "P2"]

    # Detectar tipo baseado no nome do produto
    tipos_periferico = {
        "Mouse": "Mouse",
        "Teclado": "Teclado",
        "Headset": "Headset",
        "Webcam": "Webcam",
        "Controle": "Controle",
    }

    with engine.connect() as conn:
        produtos = conn.execute(text(sql_busca)).fetchall()

        for prod in produtos:
            id_produto, nome = prod

            # Detecta tipo
            tipo_detectado = "Outro"
            for palavra, tipo in tipos_periferico.items():
                if palavra.lower() in nome.lower():
                    tipo_detectado = tipo
                    break

            conn.execute(
                text(sql_insert),
                {
                    "id_produto": id_produto,
                    "cor": cores[id_produto % len(cores)],
                    "conexao": conexoes[id_produto % len(conexoes)],
                    "tipo": tipo_detectado
                }
            )

        conn.commit()

    print(f"Periférico populado: {len(produtos)} registros adicionados.")

####################################################################################################################
###                                                   CLIENTE                                                    ###
####################################################################################################################
def popular_cliente(engine, qtd_clientes):
    """
    Popula a tabela Cliente com a quantidade especificada de clientes.
    Usa Faker para gerar dados brasileiros realistas.
    Não duplica registros caso já existam.
    """

    # Verificar se já existe clientes
    sql_check = "SELECT COUNT(*) FROM Cliente;"

    # Inserção
    sql_insert = """
        INSERT INTO Cliente (nome_cliente, cidade, estado, pais, data_cadastro)
        VALUES (:nome, :cidade, :estado, :pais, :data);
    """

    with engine.connect() as conn:
        qtd_atual = conn.execute(text(sql_check)).scalar()

        if qtd_atual > 0:
            print(f"Cliente já populado ({qtd_atual} linhas). Nenhuma inserção realizada.")
            return

        for _ in range(qtd_clientes):
            # Data aleatória de cadastro
            hoje = datetime.now()
            dias_atras = random.randint(0, 1500)  # ~4 anos
            data_cadastro = hoje - timedelta(days=dias_atras)

            conn.execute(
                text(sql_insert),
                {
                    "nome": fake.name(),
                    "cidade": fake.city(),
                    "estado": fake.estado_sigla(),
                    "pais": "Brasil",
                    "data": data_cadastro.date()
                }
            )

        conn.commit()

    print(f"Cliente populado: {qtd_clientes} clientes inseridos.")

####################################################################################################################
###                                                     PEDIDO                                                   ###
####################################################################################################################
def popular_pedido(engine, qtd_pedidos):
    """
    Popula a tabela Pedido com dados realistas.
    - Datas dentro do último ano
    - Status coerente com prazos
    - Prioridade afeta prazo estimado
    - Cancelados têm prazo igual à data do pedido
    - Pontos de fidelidade deixam 0 (serão calculados na etapa de Venda)
    """

    # Probabilidades dos status
    status_lista = ["concluido", "enviando", "pendente", "iniciado", "cancelado"]
    status_prob = [0.50, 0.15, 0.10, 0.15, 0.10]

    # Prioridade
    prioridade_lista = ["baixa", "media", "alta"]
    prioridade_prob = [0.20, 0.60, 0.20]

    # Modo envio
    modo_envio_lista = ["entrega", "retirada"]
    modo_envio_prob = [0.80, 0.20]

    # Buscar clientes existentes
    sql_clientes = "SELECT id_cliente FROM Cliente;"
    sql_insert = """
        INSERT INTO Pedido (
            data_pedido, prazo_estimado, status_pedido, prioridade_pedido, 
            modo_envio, id_cliente, pontos_fidelidade_gerados
        )
        VALUES (
            :data_pedido, :prazo_estimado, :status, :prioridade, 
            :modo_envio, :id_cliente, 0
        );
    """

    with engine.connect() as conn:
        clientes = [c[0] for c in conn.execute(text(sql_clientes)).fetchall()]

        if len(clientes) == 0:
            print("❌ Não há clientes cadastrados. Não é possível gerar pedidos.")
            return

        for _ in range(qtd_pedidos):
            
            # DATA DO PEDIDO
            hoje = datetime.now()
            dias_atras = random.randint(0, 365)
            data_pedido = hoje - timedelta(days=dias_atras)

            # STATUS
            status = random.choices(status_lista, status_prob)[0]

            # PRIORIDADE
            prioridade = random.choices(prioridade_lista, prioridade_prob)[0]

            # MODO ENVIO
            modo_envio = random.choices(modo_envio_lista, modo_envio_prob)[0]

            # PRAZO ESTIMADO
            if status == "cancelado":
                # Cancelado → prazo = data do pedido
                prazo_estimado = data_pedido

            elif status == "concluido":
                # Concluído → prazo deve estar NO PASSADO
                dias = random.randint(5, 10)

                # prioridade alta reduz o prazo
                if prioridade == "alta":
                    dias = max(2, dias - 2)

                prazo_estimado = data_pedido + timedelta(days=dias)

                # Garantir que esteja no passado
                if prazo_estimado > hoje:
                    prazo_estimado = hoje - timedelta(days=random.randint(1, 5))

            elif status == "enviando":
                dias = random.randint(1, 5)

                if prioridade == "alta":
                    dias = max(1, dias - 1)

                prazo_estimado = data_pedido + timedelta(days=dias)

            else:
                # pendente ou iniciado
                dias = random.randint(3, 12)

                if prioridade == "alta":
                    dias = max(2, dias - 2)

                if prioridade == "baixa":
                    dias = dias + 2  # aumenta o prazo

                prazo_estimado = data_pedido + timedelta(days=dias)

            # CLIENTE
            id_cliente = random.choice(clientes)

            # INSERIR PEDIDO
            conn.execute(
                text(sql_insert),
                {
                    "data_pedido": data_pedido.date(),
                    "prazo_estimado": prazo_estimado.date(),
                    "status": status,
                    "prioridade": prioridade,
                    "modo_envio": modo_envio,
                    "id_cliente": id_cliente
                }
            )

        conn.commit()

    print(f"Pedido populado: {qtd_pedidos} pedidos inseridos.")

####################################################################################################################
###                                               ITEM DO PEDIDO                                                ###
####################################################################################################################
def popular_item_pedido(engine):
    """
    Popula a tabela Item_Pedido para todos os pedidos existentes.
    - Cada pedido terá pelo menos 1 item
    - Nº de itens por pedido segue probabilidades realistas
    - Produtos escolhidos aleatoriamente (sem repetição)
    - Quantidade = 1
    - Desconto_unitário permitido (pequeno)
    """

    # Probabilidades do número de itens por pedido
    num_itens_lista = [1, 2, 3, 4]
    num_itens_prob  = [0.60, 0.25, 0.10, 0.05]

    # Probabilidades de desconto
    desconto_categorias = ["sem_desconto", "pequeno", "grande"]
    desconto_prob = [0.80, 0.15, 0.05]

    # Queries
    sql_pedidos = """
    SELECT id_pedido 
    FROM Pedido
    WHERE id_pedido NOT IN (SELECT id_pedido FROM Item_Pedido);
    """
    sql_produtos = "SELECT id_produto, preco_unitario FROM Produto;"

    # Inserção
    sql_insert = """
        INSERT INTO Item_Pedido (
            id_pedido, id_produto, quantidade, preco_unitario, desconto_unitario, valor_total_item
        )
        VALUES (
            :id_pedido, :id_produto, :quantidade, :preco, :desconto, :valor_total
        );
    """

    with engine.connect() as conn:
        pedidos = [p[0] for p in conn.execute(text(sql_pedidos)).fetchall()]
        produtos = conn.execute(text(sql_produtos)).fetchall()

        if len(produtos) == 0:
            print("❌ Não há produtos cadastrados. Não é possível gerar itens de pedido.")
            return

        for id_pedido in pedidos:
            num_itens = random.choices(num_itens_lista, num_itens_prob)[0]
            produtos_escolhidos = random.sample(produtos, k=num_itens)

            for prod in produtos_escolhidos:
                id_produto, preco_decimal = prod
                preco = Decimal(preco_decimal)

                # DESCONTO UNITÁRIO 
                tipo_desc = random.choices(desconto_categorias, desconto_prob)[0]

                if tipo_desc == "sem_desconto":
                    desconto = Decimal("0")
                elif tipo_desc == "pequeno":
                    desconto = Decimal(str(round(random.uniform(5, 30), 2)))
                else:  # grande
                    desconto = Decimal(str(round(random.uniform(30, 80), 2)))

                # Limite de desconto: nunca mais que 75% do preço
                desconto_max = preco * Decimal("0.75")
                desconto = min(desconto, desconto_max)

                # Quantidade sempre 1
                quantidade = 1

                valor_total = (preco - desconto) * quantidade

                conn.execute(
                    text(sql_insert),
                    {
                        "id_pedido": id_pedido,
                        "id_produto": id_produto,
                        "quantidade": quantidade,
                        "preco": preco,
                        "desconto": desconto,
                        "valor_total": valor_total
                    }
                )

        conn.commit()

    print(f"Item_Pedido populado para {len(pedidos)} pedidos.")

####################################################################################################################
###                                                     VENDA                                                    ###
####################################################################################################################
def popular_venda(engine):
    """
    Popula a tabela Venda com base nos itens dos pedidos.
    - Calcula subtotal a partir de Item_Pedido
    - Calcula custos da loja
    - Calcula impostos
    - Calcula frete (se aplicável)
    - Calcula descontos totais
    - Define valor_total
    """

    # Buscar pedidos que ainda não têm venda
    sql_pedidos = """
        SELECT p.id_pedido, p.modo_envio
        FROM Pedido p
        WHERE p.id_pedido NOT IN (SELECT id_pedido FROM Venda);
    """

    # Buscar subtotal e desconto do pedido
    sql_item = """
        SELECT 
            COALESCE(SUM(valor_total_item), 0) AS subtotal,
            COALESCE(SUM(desconto_unitario * quantidade), 0) AS desconto
        FROM Item_Pedido
        WHERE id_pedido = :id_pedido;
    """

    # Inserção
    sql_insert = """
        INSERT INTO Venda (
            id_pedido,
            custo_envio,
            custo_imposto_loja,
            custo_taxa_pagamento,
            valor_frete,
            valor_imposto_cliente,
            subtotal,
            valor_desconto,
            valor_total
        )
        VALUES (
            :id_pedido,
            :custo_envio,
            :custo_imposto_loja,
            :custo_taxa_pagamento,
            :valor_frete,
            :valor_imposto_cliente,
            :subtotal,
            :valor_desconto,
            :valor_total
        );
    """

    with engine.connect() as conn:
        pedidos = conn.execute(text(sql_pedidos)).fetchall()

        if len(pedidos) == 0:
            print("Venda já populada ou não há pedidos para processar.")
            return

        for id_pedido, modo_envio in pedidos:

            # Buscar subtotal e desconto 
            item_info = conn.execute(
                text(sql_item),
                {"id_pedido": id_pedido}
            ).fetchone()

            subtotal = Decimal(item_info[0])
            valor_desconto = Decimal(item_info[1])

            if subtotal == 0:
                # Se não tem item, não cria venda
                continue

            # Custos da loja
            # Custo de envio para a loja (não é cobrado ao cliente)
            if modo_envio == "entrega":
                custo_envio = Decimal(random.uniform(15, 40)).quantize(Decimal("0.01"))
            else:
                custo_envio = Decimal("0.00")

            # imposto interno (3% a 8%)
            custo_imposto_loja = (subtotal * Decimal(random.uniform(0.03, 0.08))).quantize(Decimal("0.01"))

            # taxa de pagamento (1.5% a 3%)
            custo_taxa_pagamento = (subtotal * Decimal(random.uniform(0.015, 0.03))).quantize(Decimal("0.01"))

            # Valores cobrados do cliente 
            if modo_envio == "entrega":
                valor_frete = Decimal(random.uniform(20, 60)).quantize(Decimal("0.01"))
            else:
                valor_frete = Decimal("0.00")

            # imposto cobrado ao cliente (5% a 15%)
            valor_imposto_cliente = (subtotal * Decimal(random.uniform(0.05, 0.15))).quantize(Decimal("0.01"))

            # Valor total final
            valor_total = subtotal - valor_desconto + valor_frete + valor_imposto_cliente

            # Inserção
            conn.execute(
                text(sql_insert),
                {
                    "id_pedido": id_pedido,
                    "custo_envio": custo_envio,
                    "custo_imposto_loja": custo_imposto_loja,
                    "custo_taxa_pagamento": custo_taxa_pagamento,
                    "valor_frete": valor_frete,
                    "valor_imposto_cliente": valor_imposto_cliente,
                    "subtotal": subtotal,
                    "valor_desconto": valor_desconto,
                    "valor_total": valor_total
                }
            )

        conn.commit()

    print(f"Venda populada para {len(pedidos)} pedidos.")

####################################################################################################################
###                                                 PAGAMENTO                                                    ###
####################################################################################################################
def popular_pagamento(engine):
    """
    Popula a tabela Pagamento com uma lógica realista:
    - 1 pagamento por venda
    - Data do pagamento próxima à data do pedido
    - Parcelas apenas para cartão de crédito
    - Valor pago = valor_total da venda
    """

    # Formas de pagamento
    formas = ["pix", "cartao_credito", "cartao_debito", "boleto", "transferencia", "dinheiro"]
    formas_prob = [0.30, 0.40, 0.10, 0.10, 0.05, 0.05]

    # Buscar vendas sem pagamento
    sql_vendas = """
        SELECT v.id_pedido, v.valor_total, p.data_pedido
        FROM Venda v
        JOIN Pedido p ON p.id_pedido = v.id_pedido
        WHERE v.id_pedido NOT IN (SELECT id_pedido FROM Pagamento);
    """

    # Inserção
    sql_insert = """
        INSERT INTO Pagamento (
            id_pedido,
            forma_pagamento,
            parcelas,
            data_pagamento,
            valor_pago
        )
        VALUES (
            :id_pedido,
            :forma,
            :parcelas,
            :data_pagamento,
            :valor_pago
        );
    """

    with engine.connect() as conn:
        vendas = conn.execute(text(sql_vendas)).fetchall()

        if len(vendas) == 0:
            print("Pagamento já populado ou não há vendas.")
            return

        for id_pedido, valor_total, data_pedido in vendas:

            forma = random.choices(formas, formas_prob)[0]

            # PARCELAS
            if forma == "cartao_credito":
                escolha = random.random()

                if escolha <= 0.40:
                    parcelas = 1
                elif escolha <= 0.70:
                    parcelas = random.randint(2, 3)
                elif escolha <= 0.90:
                    parcelas = random.randint(4, 6)
                else:
                    parcelas = random.randint(7, 12)
            else:
                parcelas = 1

            # DATA DO PAGAMENTO
            dias = random.randint(0, 5)
            data_pagamento = data_pedido + timedelta(days=dias)

            conn.execute(
                text(sql_insert),
                {
                    "id_pedido": id_pedido,
                    "forma": forma,
                    "parcelas": parcelas,
                    "data_pagamento": data_pagamento,
                    "valor_pago": Decimal(valor_total)
                }
            )

        conn.commit()

    print(f"Pagamento populado para {len(vendas)} vendas.")
    
####################################################################################################################
###                                             DESCONTO APLICADO                                               ###
####################################################################################################################
def popular_desconto(engine):
    """
    Popula a tabela Desconto_Aplicado com base NOS DESCONTOS DOS ITENS.
    - Apenas pedidos com desconto real entram
    - Apenas 1 tipo de desconto por pedido (via probabilidade)
    - Porcentagem = total_desconto / subtotal_original * 100
    """

    # Tipos de desconto (ENUM)
    tipos = ["promocional", "cupom", "fidelidade", "parceria", "outros"]
    tipos_prob = [0.60, 0.20, 0.10, 0.05, 0.05]

    # Buscar pedidos que ainda NÃO têm registro em Desconto_Aplicado
    sql_pedidos = """
        SELECT DISTINCT p.id_pedido
        FROM Pedido p
        JOIN Item_Pedido ip ON ip.id_pedido = p.id_pedido
        WHERE p.id_pedido NOT IN (
            SELECT id_pedido FROM Desconto_Aplicado
        );
    """

    # Buscar subtotal original e total de desconto
    sql_descontos = """
        SELECT 
            SUM(ip.quantidade * ip.preco_unitario) AS subtotal_original,
            SUM(ip.quantidade * ip.desconto_unitario) AS desconto_total
        FROM Item_Pedido ip
        WHERE ip.id_pedido = :id_pedido;
    """

    # Inserção
    sql_insert = """
        INSERT INTO Desconto_Aplicado (
            id_pedido, tipo, porcentagem, descricao
        )
        VALUES (
            :id_pedido, :tipo, :porcentagem, :descricao
        );
    """

    with engine.connect() as conn:
        pedidos = conn.execute(text(sql_pedidos)).fetchall()

        if len(pedidos) == 0:
            print("Não há novos descontos a aplicar.")
            return

        for (id_pedido,) in pedidos:

            # Buscar valores
            info = conn.execute(
                text(sql_descontos),
                {"id_pedido": id_pedido}
            ).fetchone()

            subtotal_original = Decimal(info[0])
            desconto_total   = Decimal(info[1])

            # Se não houve desconto nos itens → pula
            if desconto_total <= 0:
                continue

            # Porcentagem calculada
            porcentagem = (desconto_total / subtotal_original) * Decimal(100)
            porcentagem = porcentagem.quantize(Decimal("0.01"))

            # Limite máximo de 80%
            if porcentagem > Decimal("80.00"):
                porcentagem = Decimal("80.00")

            # Escolher tipo de desconto
            tipo = random.choices(tipos, tipos_prob)[0]

            descricao = "Desconto calculado com base nos itens do pedido."

            conn.execute(
                text(sql_insert),
                {
                    "id_pedido": id_pedido,
                    "tipo": tipo,
                    "porcentagem": porcentagem,
                    "descricao": descricao
                }
            )

        conn.commit()

    print("Desconto_Aplicado populado com base nos descontos dos itens.")

####################################################################################################################
###                                            FIDELIDADE DO CLIENTE                                             ###
####################################################################################################################
def popular_fidelidade(engine):
    """
    Calcula os pontos de fidelidade com base no valor_total da venda.
    Escalonamento (Modelo A):
      - Até 500        → 1%
      - 500 a 2000     → 2%
      - Acima de 2000  → 3%

    Pontos são:
      1) adicionados no Pedido (pontos_fidelidade_gerados)
      2) acumulados na tabela Fidelidade_Cliente
    """

    # Buscar todas as vendas com o cliente associado
    sql_vendas = """
        SELECT v.id_pedido, v.valor_total, p.id_cliente
        FROM Venda v
        JOIN Pedido p ON p.id_pedido = v.id_pedido;
    """

    # Atualizar pontos no Pedido
    sql_update_pedido = """
        UPDATE Pedido
        SET pontos_fidelidade_gerados = :pontos
        WHERE id_pedido = :id_pedido;
    """

    # Consultar se cliente já tem conta fidelidade
    sql_check_cliente = """
        SELECT pontos_acumulados
        FROM Fidelidade_Cliente
        WHERE id_cliente = :id_cliente;
    """

    # Inserir novo cliente no fidelidade
    sql_insert_fid = """
        INSERT INTO Fidelidade_Cliente (id_cliente, pontos_acumulados)
        VALUES (:id_cliente, :pontos);
    """

    # Atualizar pontos do cliente
    sql_update_fid = """
        UPDATE Fidelidade_Cliente
        SET pontos_acumulados = pontos_acumulados + :pontos
        WHERE id_cliente = :id_cliente;
    """

    with engine.connect() as conn:
        vendas = conn.execute(text(sql_vendas)).fetchall()

        for id_pedido, valor_total, id_cliente in vendas:

            valor = Decimal(valor_total)

            # CALCULAR PONTOS ESCALONADOS
            if valor <= 500:
                pontos = valor * Decimal("0.01")
            elif valor <= 2000:
                pontos = valor * Decimal("0.02")
            else:
                pontos = valor * Decimal("0.03")

            pontos = int(pontos)  # arredondar para inteiro

            # ATUALIZAR PEDIDO
            conn.execute(
                text(sql_update_pedido),
                {"pontos": pontos, "id_pedido": id_pedido}
            )

            # ATUALIZAR / INSERIR NO FIDELIDADE
            existente = conn.execute(
                text(sql_check_cliente),
                {"id_cliente": id_cliente}
            ).fetchone()

            if existente is None:
                # Novo cliente no programa de fidelidade
                conn.execute(
                    text(sql_insert_fid),
                    {"id_cliente": id_cliente, "pontos": pontos}
                )
            else:
                # Atualizar pontos acumulados
                conn.execute(
                    text(sql_update_fid),
                    {"id_cliente": id_cliente, "pontos": pontos}
                )

        conn.commit()

    print("Fidelidade_Cliente populado e pontos atualizados nos pedidos.")

####################################################################################################################
###                                                       MAIN                                                   ###
####################################################################################################################
def main(engine, qtd_clientes=50, qtd_pedidos=200):
    popular_produto(engine)
    popular_dispositivo(engine)
    popular_hardware(engine)
    popular_periferico(engine)
    popular_cliente(engine, qtd_clientes)
    popular_pedido(engine, qtd_pedidos)
    popular_item_pedido(engine)
    popular_venda(engine)
    popular_pagamento(engine)
    popular_desconto(engine)
    popular_fidelidade(engine)

