# 📦 **Geração e População de Banco de Dados -- Loja de Vendas**

Este projeto cria automaticamente um **banco de dados PostgreSQL
completo** representando uma loja fictícia de vendas. Ele inclui a
criação das tabelas, tipos ENUM e toda a população de dados necessários
para simular um ambiente transacional realista --- incluindo clientes,
produtos, pedidos, itens, vendas, pagamentos, descontos e fidelidade.

O objetivo é servir como base para estudos de **SQL**, **modelagem de
dados**, **ETL**, **análise de dados** e construir narrativas de BI com
um banco de dados funcional e coerente.

------------------------------------------------------------------------

## 📂 **Resumo do Projeto**

-   **Criação Automática do Banco**: O banco de dados é criado caso não
    exista.
-   **Criação de Tabelas e ENUMs**: Todas as entidades necessárias são
    criadas via script SQL estruturado.
-   **População Realista**:
    -   Produtos, dispositivos, hardware e periféricos
    -   Clientes simulados com dados do Faker
    -   Pedidos e itens de pedido com lógicas de sazonalidade e
        descontos
    -   Vendas com cálculos de impostos, custos e frete
    -   Pagamentos com regras realistas de parcelamento
    -   Descontos aplicados seguindo porcentagens derivadas dos itens
    -   Pontos de fidelidade acumulados dinamicamente
-   **Modularização**: Cada parte do processo está organizada em um
    arquivo próprio.
-   **Executável com um único comando**.

------------------------------------------------------------------------

## ⚙️ **Tecnologias e Bibliotecas Utilizadas**

-   **Python 3.x**
-   **PostgreSQL**
-   **Bibliotecas Python:**
    -   `SQLAlchemy`
    -   `psycopg2`
    -   `Faker`
    -   `random`, `datetime`, `decimal`

------------------------------------------------------------------------

## 📁 **Estrutura do Projeto**

    📦 Banco de Dados/
    │
    ├── criacao_banco.py          # Criação do banco e das tabelas
    ├── funcoes_populacao.py      # População de todas as tabelas
    ├── Criador_e_Populador.py    # Arquivo principal que executa tudo
    ├── README.md                 # Documentação do projeto

------------------------------------------------------------------------

## 🚀 **Como Executar o Projeto**

### 1. Instale as dependências

``` bash
pip install sqlalchemy psycopg2 faker
```

------------------------------------------------------------------------

### 2. Configure o arquivo `main.py`

Insira as credenciais do seu PostgreSQL:

``` python
usuario = 'postgres'
senha = '123'
host = 'localhost'
porta = '5432'
banco = 'loja_vendas'
```

![Exemplo de uso](Materiais%20Videos/screencast.gif)


Defina os tamanhos do dataset a ser gerado:

``` python
qtd_clientes = 50
qtd_pedidos = 200
```

------------------------------------------------------------------------

### 3. Execute o script principal

``` bash
python Criador_e_Populador.py
```

Ele irá:

1.  Criar o banco de dados\
2.  Criar todas as tabelas\
3.  Popular todas as tabelas na ordem correta

No final, o banco estará totalmente pronto para consultas e análises.

------------------------------------------------------------------------

## 🛠️ **Funcionalidades em Detalhe**

### ✔️ Produto

Criação de catálogo fixo com dispositivos, hardware e periféricos.

### ✔️ Tabelas Específicas

-   Dispositivo: cor, dimensão, tipo\
-   Hardware: consumo, especificação, tipo\
-   Periférico: cor, conexão, tipo

### ✔️ Cliente

Gerado com Faker (nome, cidade, estado, data de cadastro).

### ✔️ Pedido

-   Datas coerentes\
-   Status e prazos realistas\
-   Clientes aleatórios

### ✔️ Item_Pedido

-   Quantidade de itens por pedido\
-   Descontos com limites\
-   Cálculo automático de valor total

### ✔️ Venda

-   Subtotal e descontos\
-   Impostos variados\
-   Frete quando aplicável\
-   Valor total final

### ✔️ Pagamento

-   Métodos reais\
-   Parcelamento inteligente\
-   Datas próximas ao pedido

### ✔️ Desconto_Aplicado

-   Relacionado aos descontos reais dos itens\
-   Porcentagem calculada automaticamente

### ✔️ Fidelidade_Cliente

Cálculo escalonado:\
- ≤ 500 → 1%\
- 500--2000 → 2%\
- \> 2000 → 3%

------------------------------------------------------------------------

## 📊 **Exemplos de Consultas**

``` sql
SELECT * FROM cliente LIMIT 10;
SELECT * FROM pedido WHERE status_pedido = 'concluido';
SELECT categoria, COUNT(*) FROM produto GROUP BY categoria;
SELECT id_pedido, valor_total FROM venda ORDER BY valor_total DESC LIMIT 10;
```
