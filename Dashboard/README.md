# 📊 Dashboard de Vendas e Clientes - Power BI

## 🧩 Visão Geral
Este projeto apresenta um **dashboard interativo desenvolvido no Power BI** conectado a um banco de dados PostgreSQL. O objetivo é consolidar informações sobre **clientes, produtos, pedidos e vendas**, permitindo o acompanhamento de desempenho financeiro e operacional de forma visual e intuitiva.

---

## ⚙️ Estrutura do Banco de Dados
O banco de dados foi criado a partir de um script SQL que define tabelas como:
- **Cliente**: informações cadastrais e localização.
- **Produto**: catálogo de produtos, custos e estoques.
- **Pedido**: registro de pedidos, status e prazos.
- **Venda**: valores financeiros e custos associados.
- **Pagamento**: formas de pagamento, valores e datas.
- **Desconto_Aplicado**: tipos e percentuais de desconto.
- **Fidelidade_Cliente**: pontos acumulados por cliente.

---

## 🗂️ Estrutura do Dashboard (Páginas)

### 1. **Visão Geral**
- Indicadores principais: Total de Vendas, Lucro Total, Ticket Médio, Número de Pedidos, % de Cancelamentos e Clientes Ativos.
- Gráficos: Evolução Mensal de Vendas, Pedidos por Status e Formas de Pagamento.

### 2. **Clientes**
- Análise de perfil, localização e fidelidade.
- Principais indicadores: Total de Clientes, Pontos Médios de Fidelidade, % de Clientes Fidelizados e Ticket Médio por Cliente.
- Gráficos: Top 10 Clientes, Novos Clientes por Mês, Distribuição Geográfica e Pontos Fidelidade.

### 3. **Produtos**
- Acompanhamento de desempenho, margem e estoque.
- Indicadores: Total de Produtos, Receita por Categoria, Margem Média e Produtos com Estoque Crítico.
- Gráficos: Produtos Mais Vendidos, Margem por Categoria e Nível de Estoque.

### 4. **Pedidos**
- Controle operacional e de status.
- Indicadores: Total de Pedidos, % Concluídos, Tempo Médio de Entrega e Pedidos Pendentes.
- Gráficos: Pedidos por Status, Prioridade, Evolução Mensal e Prazo x Valor.

### 5. **Vendas e Pagamentos**
- Consolidação financeira das vendas, descontos e recebimentos.
- Indicadores: Receita Total, Lucro Total, Valor Pago, Descontos Totais e Ticket Médio.
- Gráficos: Vendas por Mês, Descontos por Tipo, Formas de Pagamento e Lucro x Receita.

### 6. **Fidelidade e Retenção**
- Análise do comportamento e engajamento dos clientes.
- Indicadores: Clientes Fidelizados, Pontos Totais, Conversão em Pedidos e Frequência de Recompra.

---

## 💡 Principais Funções DAX Utilizadas
- **Lucro:**
  ```DAX
  Lucro = SUM(Venda[valor_total]) - SUM(Venda[custo_envio]) - SUM(Venda[custo_imposto_loja]) - SUM(Venda[custo_taxa_pagamento])
  ```
- **% de Pedidos Cancelados:**
  ```DAX
  PercentualPedidosCancelados = DIVIDE([PedidosCancelados]; [TotalPedidos]; 0)
  ```
- **Ticket Médio:**
  ```DAX
  TicketMedio = DIVIDE(SUM(Venda[valor_total]); [TotalPedidos]; 0)
  ```
- **Margem Média:**
  ```DAX
  MargemMedia = AVERAGEX(Produto; DIVIDE(Produto[preco_unitario] - Produto[custo_unitario]; Produto[preco_unitario]; 0))
  ```

---

## 📈 Principais Insights Obtidos
- **Clientes:** concentração de receita em poucos clientes e correlação positiva entre pontos de fidelidade e gasto total.
- **Produtos:** categorias mais lucrativas e identificação de produtos com estoque crítico.
- **Pedidos:** monitoramento de atrasos e cancelamentos, melhorando o controle de prazos.
- **Pagamentos:** predominância de certos métodos de pagamento e impacto dos descontos no lucro líquido.
- **Negócio:** evolução mensal de vendas e margens, com visão geral de desempenho consolidado.

---

## 🧠 Conclusão
O dashboard permite acompanhar, de forma integrada, a **saúde financeira, operacional e de relacionamento com clientes**.
Com ele, é possível identificar oportunidades de melhoria, otimizar promoções e reforçar estratégias de fidelização.

---

### 💾 Integração com o Banco
O Power BI foi conectado ao PostgreSQL utilizando o driver **Npgsql** e a string:
```
Servidor: localhost:5432
Banco de dados: teste
Usuário: postgres
```

---

