# Kabom! Eletrônicos
![Status](https://img.shields.io/badge/Status-Finalizado-green)
![Python](https://img.shields.io/badge/Backend-Python%20%7C%20Flask-blue)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791)
![JavaScript](https://img.shields.io/badge/Frontend-ES6%20Modules-yellow)
> Um sistema de e-commerce robusto focado em integridade de dados, Business Intelligence (BI) e arquitetura modular.

O **Kabom** não é apenas uma loja virtual. É um ecossistema completo que simula operações reais de varejo, desde a escolha do produto com **Sistemas de Recomendação** baseados em SQL, até um **Painel Administrativo** com métricas de BI avançadas (Churn Rate, Curva ABC, Ticket Médio).

O diferencial do projeto é o uso intensivo de **SQL Nativo** para regras de negócio, evitando processamento desnecessário no backend e garantindo performance.

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
* Python 3.x instalado.
* PostgreSQL instalado e rodando.

### Passo 1: Configurar o Banco de Dados
Primeiramente é necessário criar e popular o banco de dados. Para isso no diretório ```script_populador``` desse repositório tem toda a explicação para a realização desse passo.

### Passo 2: Configurar o Backend
- Entre na pasta do projeto
```
cd kabom-eletronicos
```

- Instale as dependências
```
pip install -r requirements.txt
```

- Configure a conexão com o BD no arquivo ```app.py```
```
DB_CONFIG = {
    'dbname': 'kabom',
    'user': 'postgres',
    'password': 'senha',  # <--- COLOQUE SUA SENHA AQUI
    'host': 'localhost',
    'port': '5432'
}
```

- Rode a aplicação backend
```
python backend/app.py
```
O servidor iniciará em ```http://localhost:5000```.

### Passo 3: Rodar o Front-end
Como o projeto utiliza JavaScript Modular (ES6), é necessário um servidor local para carregar os arquivos.

Abra um **novo terminal** (mantenha o do backend rodando) na pasta do projeto:

- Crie um servidor simples na porta 8000
```bash
python -m http.server 8000
```
Agora, acesse no seu navegador: 👉 ```http://localhost:8000/frontend/home.html```

---

## ✨ Funcionalidades Principais

### 🛒 Para o Cliente
1.  **Catálogo Dinâmico:** Listagem com filtros em tempo real e controle visual de estoque.
2.  **Sistema de Recomendação:** "Quem comprou isso, também levou..." (Implementado via *Self-Join* no SQL).
3.  **Cupons Inteligentes:**
    * *Primeira Compra:* Detecta automaticamente novos usuários.
    * *VIP:* Usuários com pontuação alta de fidelidade.
    * *Gamer:* Usuários que compram periféricos com frequência.
4.  **Carrinho e Checkout:** Validação de estoque em tempo real e transação segura.

### 💼 Para o Lojista (Admin)
1.  **Dashboard Operacional:** Visão geral de estoque, clientes e vendas.
2.  **CRUD Completo:** Adicionar produtos e clientes via interface modal.
3.  **Relatórios de BI (Analytics):**
    * 🏆 **Ranking de Clientes:** Quem gasta mais.
    * 📉 **Análise de Recorrência:** Tempo médio entre compras (Churn Risk).
    * 💰 **Lucratividade:** Produtos com maior margem de lucro.
    * 🗺️ **Geográfico:** Vendas por estado.
