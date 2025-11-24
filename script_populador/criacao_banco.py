from sqlalchemy import create_engine, text
import psycopg2
from psycopg2 import sql

sql_script = """
-- Tipos ENUM
DO $$ BEGIN
    CREATE TYPE status_pedido_t AS ENUM ('iniciado', 'pendente', 'enviando', 'concluido', 'cancelado');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE prioridade_pedido_t AS ENUM ('baixa', 'media', 'alta');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE modo_envio_t AS ENUM ('entrega', 'retirada');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE forma_pagamento_t AS ENUM ('cartao_credito', 'cartao_debito', 'boleto', 'pix', 'transferencia', 'dinheiro');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE tipo_desconto_t AS ENUM ('promocional', 'cupom', 'fidelidade', 'parceria', 'outros');
EXCEPTION WHEN duplicate_object THEN null;
END $$;

-- Criação das tabelas
CREATE TABLE IF NOT EXISTS Cliente (
	id_cliente SERIAL PRIMARY KEY,
	nome_cliente VARCHAR(255) NOT NULL,
	cidade VARCHAR(100) NOT NULL,
	estado VARCHAR(100) NOT NULL,
	pais VARCHAR(100) NOT NULL,
	data_cadastro DATE DEFAULT CURRENT_DATE NOT NULL
);

CREATE TABLE IF NOT EXISTS Produto (
    id_produto SERIAL PRIMARY KEY,
    nome_produto VARCHAR(255) NOT NULL,
    categoria VARCHAR(100) NOT NULL,
    preco_unitario NUMERIC(10,2) NOT NULL,
    custo_unitario NUMERIC(10,2) NOT NULL,
    estoque_atual INT NOT NULL,
    estoque_minimo INT NOT NULL
);

CREATE TABLE IF NOT EXISTS Dispositivo (
    id_produto INT PRIMARY KEY,
    cor VARCHAR(50) NOT NULL,
    dimensao VARCHAR(50) NOT NULL,
    tipo VARCHAR(100) NOT NULL,
    FOREIGN KEY (id_produto) REFERENCES Produto(id_produto) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Hardware (
    id_produto INT PRIMARY KEY,
    consumo_energia INT NOT NULL,
    especificacao_tecnica VARCHAR(255),
    tipo VARCHAR(100) NOT NULL,
    FOREIGN KEY (id_produto) REFERENCES Produto(id_produto) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Periferico (
    id_produto INT PRIMARY KEY,
    cor VARCHAR(50) NOT NULL,
    conexao VARCHAR(50) NOT NULL,
    tipo VARCHAR(100) NOT NULL,
    FOREIGN KEY (id_produto) REFERENCES Produto(id_produto) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Pedido (
    id_pedido SERIAL PRIMARY KEY,
    data_pedido DATE NOT NULL,
    prazo_estimado DATE NOT NULL,
    status_pedido status_pedido_t DEFAULT 'iniciado' NOT NULL,
    prioridade_pedido prioridade_pedido_t DEFAULT 'media' NOT NULL,
    modo_envio modo_envio_t DEFAULT 'entrega' NOT NULL,
    id_cliente INT NOT NULL,
    pontos_fidelidade_gerados INT NOT NULL DEFAULT 0,
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Venda (
    id_pedido INT PRIMARY KEY,
    custo_envio NUMERIC(10,2) NOT NULL,
    custo_imposto_loja NUMERIC(10,2) NOT NULL,
    custo_taxa_pagamento NUMERIC(10,2) NOT NULL,
    valor_frete NUMERIC(10,2) NOT NULL,
    valor_imposto_cliente NUMERIC(10,2) NOT NULL,
    subtotal NUMERIC(10,2) NOT NULL,
    valor_desconto NUMERIC(10,2) NOT NULL,
    valor_total NUMERIC(10,2) NOT NULL,
    FOREIGN KEY (id_pedido) REFERENCES Pedido(id_pedido) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Pagamento (
    id_pedido INT PRIMARY KEY,
    forma_pagamento forma_pagamento_t NOT NULL,
    parcelas INT NOT NULL DEFAULT 1,
    data_pagamento DATE NOT NULL,
    valor_pago NUMERIC(10,2) NOT NULL,
    FOREIGN KEY (id_pedido) REFERENCES Venda(id_pedido) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Desconto_Aplicado (
    id_pedido INT NOT NULL,
    tipo tipo_desconto_t NOT NULL,
    porcentagem NUMERIC(5,2) NOT NULL,
    descricao VARCHAR(200),
    PRIMARY KEY (id_pedido, tipo),
    FOREIGN KEY (id_pedido) REFERENCES Venda(id_pedido) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Item_Pedido (
    id_pedido INT NOT NULL,
    id_produto INT NOT NULL,
    quantidade INT NOT NULL,
    preco_unitario NUMERIC(10,2) NOT NULL,
    desconto_unitario NUMERIC(10,2) NOT NULL DEFAULT 0,
    valor_total_item NUMERIC(10,2) NOT NULL,
    PRIMARY KEY (id_pedido, id_produto),
    FOREIGN KEY (id_pedido) REFERENCES Pedido(id_pedido) ON DELETE CASCADE,
    FOREIGN KEY (id_produto) REFERENCES Produto(id_produto) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Fidelidade_Cliente (
    id_cliente INT PRIMARY KEY,
    pontos_acumulados INT NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES Cliente(id_cliente) ON DELETE CASCADE
);
"""

####################################################################################################################
###                                         FUNÇÃO PARA CRIAR O BANCO                                           ###
####################################################################################################################
def criar_banco(usuario, senha, host, porta, banco):
    """
    Cria o banco de dados caso ele não exista.
    Esta função usa psycopg2, pois o engine só funciona depois que o BD existe.
    """
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=usuario,
            password=senha,
            host=host,
            port=porta
        )
        conn.autocommit = True
        cur = conn.cursor()

        cur.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname = %s;"), [banco])
        existe = cur.fetchone()

        if not existe:
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(banco)))
            print(f"✅ Banco de dados '{banco}' criado com sucesso.")
        else:
            print(f"ℹ️ Banco '{banco}' já existe.")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Erro ao criar banco: {e}")


####################################################################################################################
###                                         FUNÇÃO PARA CRIAR O ENGINE                                           ###
####################################################################################################################
def criar_engine(usuario, senha, host, porta, banco):
    """
    Cria e retorna o engine SQLAlchemy com base nos parâmetros informados.
    """
    engine = create_engine(f'postgresql+psycopg2://{usuario}:{senha}@{host}:{porta}/{banco}')
    return engine


####################################################################################################################
###                                         CRIAR TABELAS UTILIZANDO ENGINE                                      ###
####################################################################################################################
def criar_tabelas(engine, sql_script):
    """
    Executa o script SQL para criar tabelas e tipos no banco selecionado.
    """
    with engine.connect() as conn:
        conn.execute(text(sql_script))
        conn.commit()

    print("📦 Tabelas e tipos criados com sucesso!")


####################################################################################################################
###                                                   MAIN                                                       ###
####################################################################################################################
def main(usuario, senha, host, porta, banco, sql_script=sql_script):
    # 1. Criar banco
    criar_banco(usuario, senha, host, porta, banco)

    # 2. Criar engine
    engine = criar_engine(usuario, senha, host, porta, banco)

    # 3. Criar tabelas
    criar_tabelas(engine, sql_script)

    return engine  # retorna engine para o resto do sistema
