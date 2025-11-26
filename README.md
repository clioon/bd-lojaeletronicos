# Documentação Técnica e Arquitetura de Dados: Ecossistema de E-commerce Kabom!

## 1. Introdução e Visão Geral da Arquitetura

O presente relatório técnico constitui a documentação definitiva da arquitetura de backend e da camada de persistência de dados do Sistema Kabom!. Este documento foi elaborado para servir como referência central para engenheiros de software, arquitetos de dados e desenvolvedores backend responsáveis pela manutenção, evolução e otimização da lógica de negócios e das estratégias de consulta a banco de dados da plataforma.

A análise aqui apresentada deriva de uma auditoria exaustiva dos artefatos de código fonte disponíveis, especificamente os módulos de interface administrativa (`adminDashboard.js`), a lógica de interação do cliente (`home.js`) e, fundamentalmente, a camada de integração de API (`api.js`), que estabelece os contratos de comunicação vitais entre o frontend e o sistema gerenciador de banco de dados (SGBD).¹

O Sistema Kabom! não opera apenas como um repositório passivo de produtos, mas sim como uma plataforma de comércio eletrônico dual, projetada para atender a duas personas distintas com necessidades de dados diametralmente opostas:

1.  **O Cliente Final:** Cuja interação é pautada pela descoberta de catálogo, filtragem de produtos e eficiência no checkout.
2.  **O Administrador/Gestor:** Cuja interação exige painéis analíticos complexos, monitoramento de inventário em tempo real e segmentação avançada de base de clientes para inteligência de negócios.

Este documento foca estritamente na lógica de backend, modelagem de esquema e engenharia de consultas (Query Engineering). Instruções operacionais de instalação, configuração de ambiente ou provisionamento de servidores estão fora do escopo, assumindo-se que a infraestrutura subjacente já se encontra operacional e estável.

---

## 2. Fundamentos da Modelagem de Dados

A integridade do Sistema Kabom! depende de um esquema relacional robusto. A análise dos endpoints da API (`/produtos`, `/clientes`, `/checkout`) e das estruturas de objetos manipulados no frontend permite a engenharia reversa de um modelo de dados capaz de suportar as regras de negócio implícitas.

### 2.1. Arquitetura da Entidade Cliente (tb_clientes)

A gestão de clientes no Kabom! transcende o cadastro básico. A existência de múltiplos endpoints de segmentação analítica — como `/clientes/fidelidade`, `/clientes/high-ticket`, `/clientes/inativos` e `/clientes/primeira-compra` — impõe requisitos específicos ao modelo de dados. A tabela deve ser otimizada para leituras pesadas e agregações frequentes.

#### 2.1.1. Definição do Esquema e Dicionário de Dados

A tabela `tb_clientes` atua como a espinha dorsal para todas as operações de CRM (Customer Relationship Management).

| Atributo | Tipo de Dado (SQL) | Restrições | Análise Técnica e Justificativa de Negócio |
| :--- | :--- | :--- | :--- |
| `id_cliente` | `BIGINT` | PK, AUTO_INCREMENT | Identificador único. O uso de BIGINT previne o esgotamento de IDs em cenários de hipercrescimento, antecipando uma base de milhões de usuários. |
| `nome_completo` | `VARCHAR(150)` | NOT NULL | Armazena a identidade do cliente conforme capturado no modal de cadastro administrativo, essencial para personalização e logística.¹ |
| `cidade` / `estado` | `VARCHAR(100)` / `CHAR(2)` | INDEX / INDEX | Utilizado para segmentação geográfica. A indexação é crítica para relatórios regionais rápidos. Sigla da Unidade Federativa (UF). O tipo CHAR(2) é mais performático que VARCHAR para dados de comprimento fixo. |
| `total_pedidos` | `INT` | DEFAULT 0 | **Campo Desnormalizado.** Armazena o contador histórico de pedidos para permitir a renderização instantânea no dashboard sem realizar `COUNT()` na tabela de pedidos a cada requisição. |
| `pontos_fidelidade` | `INT` | DEFAULT 0 | Suporta a lógica de gamificação. Este campo é mutável e deve ser protegido por transações durante o acúmulo ou resgate de pontos. |
| `data_cadastro` | `DATETIME` | DEFAULT CURRENT_TIMESTAMP | Fundamental para análises de coorte (Cohort Analysis) e identificação de novos clientes ("Primeira Compra"). |
| `ultimo_pedido` | `DATETIME` | NULLABLE, INDEX | Pilar da estratégia de retenção. Necessário para a consulta de `/clientes/inativos`. Indexado para otimizar queries de intervalo de tempo. |

#### 2.1.2. Estratégia de Desnormalização

O painel administrativo exibe uma tabela de clientes contendo colunas como "Total de Pedidos" e "Pontos". Em uma teoria de normalização estrita (3FN), esses valores seriam calculados em tempo de execução. Contudo, para o Kabom!, recomenda-se a estratégia de **"Calculation on Write"** (Cálculo na Escrita).

* **Mecanismo:** A cada novo pedido finalizado via `/checkout`, um gatilho (Trigger) ou a própria lógica da aplicação atualiza o `total_pedidos` na tabela de clientes.
* **Benefício:** A leitura da lista de clientes (`buscarClientes()`) torna-se uma operação de complexidade $O(1)$ por registro, evitando a complexidade $O(N)$ de juntar e agrupar milhões de linhas de pedidos.

---

### 2.2. Arquitetura da Entidade Produto (tb_produtos)

O inventário representa o ativo financeiro da empresa. O sistema exige monitoramento granular de níveis de estoque e avaliação patrimonial em tempo real (métrica "Valor em Estoque").¹

#### 2.2.1. Definição do Esquema e Dicionário de Dados

| Atributo | Tipo de Dado (SQL) | Restrições | Análise Técnica e Justificativa de Negócio |
| :--- | :--- | :--- | :--- |
| `id_produto` | `INT` | PK, AUTO_INCREMENT | Identificador único do SKU (Stock Keeping Unit). |
| `nome` | `VARCHAR(200)` | NOT NULL, FULLTEXT | Nome descritivo (ex: "Placa de Vídeo RTX 4090"). O índice FULLTEXT é mandatório para permitir buscas textuais eficientes pelo cliente. |
| `categoria` | `VARCHAR(50)` | NOT NULL, INDEX | Categorias taxionômicas: "Periférico", "Hardware", "Dispositivo", "Outro". Indexação facilita a filtragem no frontend. |
| `preco_venda` | `DECIMAL(10, 2)` | NOT NULL | Valor facial para o consumidor. O tipo DECIMAL é imperativo para evitar erros de arredondamento de ponto flutuante comuns em FLOAT. |
| `custo_unitario` | `DECIMAL(10, 2)` | NOT NULL | Custo de aquisição (CMV). Invisível ao cliente, mas essencial para o cálculo de margem no backend. |
| `estoque_atual` | `INT` | NOT NULL, DEFAULT 0 | Quantidade física disponível. Decrementado atomicamente no checkout. |
| `estoque_minimo` | `INT` | NOT NULL, DEFAULT 5 | Ponto de re-pedido. Define a lógica de negócio para o alerta visual de estoque "Baixo". |

#### 2.2.2. Lógica de Status Virtual

O frontend exibe o status do produto como 'OK', 'Baixo' ou 'Esgotado'.¹ Armazenar este status como texto no banco seria um erro arquitetural, pois criaria redundância e risco de inconsistência (ex: estoque muda para 0, mas status continua 'OK').

A arquitetura correta utiliza um Campo Computado (Virtual Generated Column) ou cálculo na query:

```sql
-- Exemplo de lógica de determinação de status
CASE
    WHEN estoque_atual = 0 THEN 'Esgotado'
    WHEN estoque_atual <= estoque_minimo THEN 'Baixo'
    ELSE 'OK'
END

```sql
CASE
    WHEN estoque_atual = 0 THEN 'Esgotado'
    WHEN estoque_atual <= estoque_minimo THEN 'Baixo'
    ELSE 'OK'
END```

Isso garante que a regra de negócio visualizada no dashboard seja sempre um reflexo matemático puro do estado atual do inventário.

## 3. Engenharia de Consultas e Implementação de Backend
A eficiência do backend do Kabom! é medida pela rapidez com que ele responde às requisições da API. Abaixo, detalhamos a implementação SQL para os endpoints críticos listados em `api.js`, focando em performance e correção lógica.

### 3.1. Gestão de Catálogo e Inteligência de Estoque
**Endpoint:** `GET /produtos`
**Contexto:** Utilizado tanto na loja ("Sou Cliente") quanto na gestão ("Produtos").
**Requisito:** Deve retornar dados brutos e métricas derivadas para cálculo de valor patrimonial.

**Implementação SQL:**
```sql
SELECT
    p.id_produto,
    p.nome,
    p.categoria,
    p.preco_venda,
    p.custo_unitario,
    p.estoque_atual,
    p.estoque_minimo,
    -- Cálculo do Status em Tempo de Leitura
    CASE
        WHEN p.estoque_atual = 0 THEN 'Esgotado'
        WHEN p.estoque_atual <= p.estoque_minimo THEN 'Baixo'
        ELSE 'OK'
    END AS status_calculado,
    -- Métrica Financeira: Valor Patrimonial do Item
    (p.preco_venda * p.estoque_atual) AS valor_patrimonial_venda
FROM
    tb_produtos p
WHERE
    p.ativo = 1 -- Assumindo Soft Delete para produtos removidos
ORDER BY
    p.nome ASC;```

**Análise de Impacto:** O cálculo de `valor_patrimonial_venda` permite que o frontend some essa coluna para exibir o card "Valor em Estoque" no dashboard. Realizar essa multiplicação no banco de dados é geralmente mais eficiente do que trafegar dados brutos e iterar no JavaScript, especialmente para catálogos grandes.

**Endpoint:** `POST /produtos`
**Contexto:** O modal de "Novo Produto" envia `{ nome, categoria, preco, custo, estoque_atual, estoque_minimo }`.
**Requisito:** Inserção segura.

**Implementação SQL:**
```sql
INSERT INTO tb_produtos
(nome, categoria, preco_venda, custo_unitario, estoque_atual, estoque_minimo,
data_criacao)
VALUES
(?, ?, ?, ?, ?, ?, NOW());```

**Observação de Segurança:** É vital que o backend valide se `preco_venda` e `custo_unitario` são positivos antes da inserção para manter a integridade contábil.

### 3.2. Analytics e Segmentação de Clientes (BI)
O grande diferencial competitivo do sistema Kabom! reside nos seus endpoints de inteligência de clientes (`/clientes/*`). Estas consultas transformam dados brutos em estratégias de marketing.

#### 3.2.1. Identificação de Clientes de Alto Valor (GET /clientes/high-ticket)
**Definição:** Clientes cujo volume financeiro ou frequência de compra supera significativamente a média.
**Estratégia SQL:** Utilização de agregação (`GROUP BY`) com filtragem posterior (`HAVING`).

```sql
SELECT
    c.id_cliente,
    c.nome_completo,
    c.cidade,
    COUNT(p.id_pedido) as total_pedidos_real,
    SUM(p.valor_total) as LTV -- Lifetime Value
FROM
    tb_clientes c
JOIN
    tb_pedidos p ON c.id_cliente = p.id_cliente
WHERE
    p.status = 'CONCLUIDO' -- Apenas vendas efetivadas
GROUP BY
    c.id_cliente
HAVING
    LTV > 5000 -- Limiar definido pela regra de negócio "High Ticket"
ORDER BY
    LTV DESC;```

**Contexto:** Este endpoint alimenta listas de VIPs para ações promocionais exclusivas. [cite_start]A performance depende de indices na chave estrangeira `id_cliente` na tabela de pedidos. [cite: 107-108]

#### 3.2.2. Recuperação de Clientes Inativos (GET /clientes/inativos)
**Definição:** Clientes com histórico de compra, mas ausentes há um período determinado (Churn Risk).
**Estratégia SQL:** Análise de datas relativas.

```sql
SELECT
    c.id_cliente,
    c.nome_completo,
    c.ultimo_pedido,
    c.total_pedidos,
    DATEDIFF(NOW(), c.ultimo_pedido) as dias_sem_comprar
FROM
    tb_clientes c
WHERE
    c.ultimo_pedido IS NOT NULL
    AND c.ultimo_pedido < DATE_SUB(NOW(), INTERVAL 6 MONTH) -- Definição de Inatividade (6 meses)
ORDER BY
    c.ultimo_pedido ASC; -- Prioriza os inativos há mais tempo [cite: 113-126]```

**Insight:** Esta consulta é vital para campanhas de "Win-back" (reconquista). A dependência do campo `ultimo_pedido` (atualizado na transação de venda) evita uma subquery custosa do tipo `MAX(data_pedido)` na tabela de vendas.

#### 3.2.3. Segmentação de Fidelidade (GET /clientes/fidelidade)
**Contexto:** O dashboard exibe explicitamente pontos de fidelidade.
**Estratégia SQL:** Filtragem direta baseada em pontuação acumulada.

```sql
SELECT
    id_cliente,
    nome_completo,
    pontos_fidelidade,
    cidade
FROM
    tb_clientes
WHERE
    pontos_fidelidade >= 1000 -- Limiar para status "Gold/Fidelidade"
ORDER BY
    pontos_fidelidade DESC;```

#### 3.2.4. Detecção de Oportunidades de Primeira Compra (GET /clientes/primeira-compra)
**Definição:** Usuários cadastrados que ainda não converteram em vendas (Lead Activation).
**Estratégia SQL:** "Anti-Join" (Left Join com verificação de nulidade).

```sql
SELECT
    c.id_cliente,
    c.nome_completo,
    c.data_cadastro,
    DATEDIFF(NOW(), c.data_cadastro) as dias_desde_cadastro
FROM
    tb_clientes c
LEFT JOIN
    tb_pedidos p ON c.id_cliente = p.id_cliente
WHERE
    p.id_pedido IS NULL -- A ausência de correspondência indica zero compras
    AND c.data_cadastro >= DATE_SUB(NOW(), INTERVAL 30 DAY) -- Filtro de recência opcional
ORDER BY
    c.data_cadastro DESC;```

**Relevância:** Identificar estes usuários permite o envio de cupons de boas-vindas, aumentando a taxa de conversão do funil.

### 3.3. O Core Transacional: Checkout
O endpoint `POST /checkout` (enviar Pedido ¹) é o componente mais crítico do sistema. Uma falha aqui resulta em perda direta de receita ou corrupção de estoque (vender o que não existe).

#### 3.3.1. O Desafio da Concorrência
Em um e-commerce como o Kabom!, múltiplos usuários podem tentar comprar o último item de estoque simultaneamente. Se o backend apenas ler o estoque (SELECT), ver que $e > 0$, e depois atualizar (UPDATE), ocorre uma Race Condition. Dois usuários podem "ganhar" o item, deixando o estoque em -1.

#### 3.3.2. Fluxo da Transação (ACID)
A implementação deve usar Transações de Banco de Dados com bloqueio pessimista (`FOR UPDATE`) ou controle de versão otimista.

**Pseudocódigo SQL da Transação de Checkout:**

1.  **Iniciar Transação:**
    `START TRANSACTION;`

2.  **Verificação e Bloqueio (Locking):**
    Selecionar o produto e bloquear a linha para escrita até o fim da transação.
    ```sql
    SELECT estoque_atual FROM tb_produtos WHERE id_produto = ? FOR UPDATE;```

    **Lógica de Aplicação:** Se `estoque_atual < quantidade_solicitada`, lançar exceção e executar `ROLLBACK`.

3.  **Atualização de Inventário:**
    ```sql
    UPDATE tb_produtos
    SET estoque_atual = estoque_atual - ?
    WHERE id_produto = ?;```
   

4.  **Registro do Pedido:**
    Inserir o cabeçalho do pedido.
    ```sql
    INSERT INTO tb_pedidos (id_cliente, data_pedido, valor_total, status)
    VALUES (?, NOW(), ?, 'PENDENTE');```
    Recuperar ID: `SET @id_pedido = LAST_INSERT_ID();`

5.  **Registro dos Itens:**
    Inserir detalhes na tabela de junção `tb_itens_pedido`.
    ```sql
    INSERT INTO tb_itens_pedido (id_pedido, id_produto, quantidade,
    preco_unitario_congelado)
    VALUES (@id_pedido, ?, ?, ?);```
   

6.  **Atualização de Métricas do Cliente (Trigger ou Inline):**
    Atualizar os contadores para manter a consistência dos dashboards analíticos.
    ```sql
    UPDATE tb_clientes
    SET total_pedidos = total_pedidos + 1,
        ultimo_pedido = NOW(),
        pontos_fidelidade = pontos_fidelidade + ? -- Ex: 1 ponto por real gasto
    WHERE id_cliente = ?;```
   

7.  **Finalização:**
    `COMMIT;`

Este fluxo garante a integridade referencial e aritmética dos dados, assegurando que o Dashboard Administrativo ¹ reflita a realidade física do estoque imediatamente após a venda.

### 3.4. Motor de Recomendações
O endpoint `GET /produtos/${idProduto}/recomendacoes` ¹ sugere uma funcionalidade de Cross-Selling.

**Estratégia de Implementação:**
A abordagem mais robusta, dado o esquema relacional, é a Filtragem Colaborativa baseada em itens ("Quem comprou isso, também comprou...").

```sql
SELECT
    p_recom.id_produto,
    p_recom.nome,
    COUNT(*) as forca_relacao
FROM
    tb_itens_pedido ip1
JOIN
    tb_itens_pedido ip2 ON ip1.id_pedido = ip2.id_pedido -- Itens no mesmo carrinho
JOIN
    tb_produtos p_recom ON ip2.id_produto = p_recom.id_produto
WHERE
    ip1.id_produto = ? -- Produto atual (contexto)
    AND ip2.id_produto != ? -- Excluir o próprio produto
GROUP BY
    p_recom.id_produto
ORDER BY
    forca_relacao DESC
LIMIT 4;``` 

Esta consulta analisa o histórico de pedidos passados para encontrar correlações de compra, aumentando o ticket médio automaticamente.

## 4. Análise de Métricas e KPIs do Dashboard
O `adminDashboard.js` define três métricas de alto nível (KPIs) que devem ser alimentadas pelo banco de dados com latência mínima.¹

### 4.1. KPI: Clientes Ativos
Embora o rótulo diga "Ativos", o snippet sugere uma contagem total.
* **Query Rápida:** `SELECT COUNT(*) FROM tb_clientes;`
* **Melhoria Semântica:** Para contar verdadeiramente ativos, cruzaríamos com a tabela de pedidos: `SELECT COUNT(DISTINCT id_cliente) FROM tb_pedidos WHERE data_pedido >= DATE_SUB(NOW(), INTERVAL 90 DAY);`

### 4.2. KPI: Catálogo
Contagem simples de SKUs.
* **Query:** `SELECT COUNT(*) FROM tb_produtos WHERE ativo = 1;`

### 4.3. KPI: Valor em Estoque
Esta é uma métrica crítica de risco financeiro.
* **Query:** `SELECT SUM(estoque_atual * preco_venda) FROM tb_produtos;`
* **Interpretação:** Representa a receita potencial bruta represada no armazém. Uma queda súbita nesta métrica (sem aumento correspondente em vendas) pode indicar perdas ou ajustes de inventário.

## 5. Integrações Externas e Expansão
O sistema possui ganchos para expansão futura, evidenciados pelo botão "Abrir Dashboard de BI" que redireciona para `relatorio.html`.¹

### 5.1. Data Warehousing
Para escalar, recomenda-se que os endpoints analíticos complexos (`high-ticket`, `recomendacoes`) não consultem o banco transacional (OLTP) diretamente em horário de pico.
A arquitetura sugere a futura implementação de uma réplica de leitura ou um processo ETL (Extract, Transform, Load) que popule tabelas de fatos e dimensões dedicadas ao BI externo mencionado no código.

## 6. Considerações Finais
A arquitetura de dados proposta para o Sistema Kabom! demonstra uma dualidade funcional eficaz: ela suporta a velocidade transacional necessária para o checkout do cliente final, ao mesmo tempo que mantém estruturas de dados ricas (como históricos desnormalizados e flags de fidelidade) para empoderar o administrador.

A implementação correta das consultas SQL detalhadas neste relatório, especialmente as transações com bloqueio de estoque e as agregações analíticas de clientes, é fundamental para garantir que a promessa da interface ("Sou Cliente" vs "Sou Admin") seja cumprida com integridade, segurança e performance.
Este documento deve guiar todas as futuras implementações de backend na plataforma.

## Referências citadas
1. `adminDashboard.js`