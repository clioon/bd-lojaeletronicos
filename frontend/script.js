// A URL base do nosso backend Flask
const BACKEND_URL = 'http://127.0.0.1:5000/api';

/**
 * 1. FUNÇÃO PARA LISTAR PRODUTOS
 */
async function carregarProdutos() {
    const listaProdutos = document.getElementById('lista-produtos');
    listaProdutos.innerHTML = ''; // Limpa o "Carregando..."
    
    try {
        // Faz a requisição para o endpoint do backend
        const response = await fetch(`${BACKEND_URL}/produtos`);
        
        // Verifica se a resposta foi bem-sucedida (status 200)
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Converte a resposta JSON em um objeto JavaScript
        const produtos = await response.json();

        // Itera sobre os produtos e os insere no HTML
        produtos.forEach(produto => {
            const li = document.createElement('li');
            li.textContent = `${produto.nome} - R$ ${produto.preco.toFixed(2)} (ID: ${produto.id})`;
            listaProdutos.appendChild(li);
        });

    } catch (error) {
        console.error("Erro ao buscar produtos:", error);
        listaProdutos.innerHTML = '<li>Erro ao carregar o catálogo. Verifique se o Backend está rodando!</li>';
    }
}

/**
 * 2. FUNÇÃO PARA LISTAR O CARRINHO
 */
async function carregarCarrinho() {
    const listaCarrinho = document.getElementById('lista-carrinho');
    listaCarrinho.innerHTML = ''; // Limpa o conteúdo
    
    try {
        const response = await fetch(`${BACKEND_URL}/carrinho`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const carrinho = await response.json();

        if (carrinho.length === 0) {
             listaCarrinho.innerHTML = '<li>Seu carrinho está vazio.</li>';
        } else {
             // Por enquanto, apenas exibimos a contagem, pois o Mock está vazio
             // Em um projeto real, você faria um loop aqui!
             listaCarrinho.innerHTML = `<li>Itens no carrinho: ${carrinho.length}</li>`;
        }

    } catch (error) {
        console.error("Erro ao buscar carrinho:", error);
        listaCarrinho.innerHTML = '<li>Erro ao carregar o carrinho.</li>';
    }
}


// Executa as funções quando a página carrega
carregarProdutos();
carregarCarrinho();