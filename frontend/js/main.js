// js/main.js
import { buscarProdutos, buscarClientes, enviarPedido, buscarDescontos, buscarClientesFidelidade, buscarClientesPromocionais, buscarClientesPrimeiraCompra, buscarClientesInativos, buscarClientesHighTicket} from './api.js';
import { state, cache } from './state.js';
import { formatCurrency } from './utils.js';

import { renderHome } from './components/home.js';
import { renderAdminDashboard } from './components/adminDashboard.js';

// Importando Componentes
import { renderNavbar } from './components/navbar.js';
import { renderProductList } from './components/productList.js';
import { setupModalListeners, showModal, hideModal } from './components/modal.js';

// Elemento raiz
const app = document.getElementById('app');

async function init() {
    console.log("Inicializando sistema...");
    setupModalListeners(); // Ativa fechar modal

    // 1. Busca dados do Backend
    try {
        const [prods, clis, descs, vips, promos, novatos, inativos, highTickets] = await Promise.all([
            buscarProdutos(),
            buscarClientes(),
            buscarDescontos(),
            buscarClientesFidelidade(),
            buscarClientesPromocionais(),
            buscarClientesPrimeiraCompra(),
            buscarClientesInativos(),
            buscarClientesHighTicket()
        ]);
        
        // Formata os preços que vêm como string do Python (Decimal) para Float
        cache.produtos = prods.map(p => ({
            ...p,
            preco: parseFloat(p.preco),
            tipo: p.tipo_produto || "Outro",
            estoqueAtual: p.estoque
        }));
        
        cache.clientes = clis;
        cache.descontos = descs;
        cache.listaFidelidade = vips;
        cache.listaPromocional = promos;
        cache.listaPrimeiraCompra = novatos;
        cache.listaInativos = inativos;
        cache.listaHighTicket = highTickets;

        console.log(`Carregado: ${vips.length} VIPs, ${promos.length} Promocionais, ${novatos.length} Primeira Compra, ${inativos.length} Inativos e ${highTickets.length} High Tickets.`);
        
        // Simula login com o primeiro cliente do banco
        if (cache.clientes.length > 0) {
            state.user = cache.clientes[35];
        }

        renderApp();

    } catch (err) {
        app.innerHTML = `<h1>Erro crítico</h1><p>${err.message}</p>`;
    }
}

// Função Central de Renderização
function renderApp() {
    app.innerHTML = ''; 

    // ROTA 1: HOME (Seleção de Perfil)
    if (state.role === 'home') {
        renderHome(app, (targetPage) => {
            // Callback de navegação
            if (targetPage === 'produtos') state.page = 'produtos';
            if (targetPage === 'admin') state.page = 'admin';
            renderApp();
        });
        return; // Para aqui, não renderiza navbar na home
    }

    // Se passou da home, renderiza Navbar
    const headerContainer = document.createElement('header');
    
    // Navbar inteligente: Se for LOJA, mostra botão de sair
    renderNavbar(headerContainer, (targetPage) => {
        if(targetPage === 'logout') {
            state.role = 'home';
            state.cart = [];
        } else {
            state.page = targetPage;
        }
        renderApp();
    });
    app.appendChild(headerContainer);

    // Renderiza Conteúdo Principal
    const mainContainer = document.createElement('main');
    mainContainer.className = 'container';

    // ROTA 2: LOJA / PRODUTOS
    if (state.page === 'produtos') {
        renderProductList(mainContainer, cache.produtos, adicionarAoCarrinho);
    } 
    // ROTA 3: CARRINHO
    else if (state.page === 'carrinho') {
        renderCarrinho(mainContainer);
    }
    // ROTA 4: ADMIN (NOVO)
    else if (state.page === 'admin') {
        // Só renderiza admin se o role for loja
        if (state.role === 'loja') {
            renderAdminDashboard(mainContainer, cache.clientes, cache.produtos);
        } else {
            mainContainer.innerHTML = '<h2>Acesso Negado</h2>';
        }
    }

    app.appendChild(mainContainer);
}

// Lógica: Adicionar ao Carrinho
function adicionarAoCarrinho(produto) {
    state.cart.push(produto);
    alert(`${produto.nome} adicionado!`);
    renderApp(); // Atualiza contador na navbar
}

// Lógica: Renderizar tela de Carrinho (Simples, direto no main por enquanto)
function renderCarrinho(container) {
    if (state.cart.length === 0) {
        container.innerHTML = `
            <div style="text-align:center; margin-top:50px;">
                <h2>Seu carrinho está vazio.</h2>
                <button id="back-shop" class="btn-primary" style="margin-top:20px; padding:10px 20px;">Voltar às compras</button>
            </div>
        `;
        container.querySelector('#back-shop').onclick = () => {
            state.page = 'produtos';
            renderApp();
        };
        return;
    }

    // 1. Cálculos Matemáticos
    const subtotal = state.cart.reduce((acc, p) => acc + p.preco, 0);
    
    // Se tiver desconto ativo, calcula o valor a subtrair
    let valorDesconto = 0;
    if (state.activeDiscount) {
        // Ex: 10% de 100 = 10
        valorDesconto = subtotal * (state.activeDiscount.porcentagem / 100);
    }
    
    const totalFinal = subtotal - valorDesconto;

    // 2. Lista de Itens HTML
    const listaHtml = state.cart.map(item => `
        <div style="display:flex; justify-content:space-between; padding: 15px; border-bottom:1px solid #eee; align-items:center;">
            <div>
                <strong style="display:block">${item.nome}</strong>
                <small style="color:#888">${item.tipo || 'Item'}</small>
            </div>
            <div style="font-weight:bold">${formatCurrency(item.preco)}</div>
        </div>
    `).join('');

    // 3. HTML do Painel de Totais e Botões
    // Se tiver desconto, mostra o botão "Remover", senão mostra "Adicionar"
    const btnDescontoHtml = state.activeDiscount 
        ? `<button id="btn-rm-cupom" style="color:red; background:none; border:1px solid red; padding:5px 10px; font-size:0.8rem; cursor:pointer;">Remover Cupom</button>`
        : `<button id="btn-add-cupom" style="color:green; background:none; border:1px solid green; padding:5px 10px; font-size:0.8rem; cursor:pointer;">Adicionar Cupom</button>`;

    const linhaDescontoHtml = state.activeDiscount
        ? `<div style="display:flex; justify-content:space-between; color:green; margin-bottom:5px;">
               <span>Desconto (${state.activeDiscount.tipo}):</span>
               <span>- ${formatCurrency(valorDesconto)}</span>
           </div>`
        : '';

    container.innerHTML = `
        <h2>Seu Carrinho</h2>
        <div class="cart-list" style="background:white; border-radius:8px; box-shadow:0 2px 5px rgba(0,0,0,0.05);">${listaHtml}</div>
        
        <div class="cart-summary" style="background:white; padding:20px; margin-top:20px; border-radius:8px; text-align:right;">
            
            <div style="margin-bottom:15px; padding-bottom:15px; border-bottom:1px solid #eee;">
               ${btnDescontoHtml}
            </div>

            <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
                <span>Subtotal:</span>
                <span>${formatCurrency(subtotal)}</span>
            </div>
            
            ${linhaDescontoHtml}

            <div style="display:flex; justify-content:space-between; font-size: 1.5em; font-weight:bold; margin-top:10px; color:#333;">
                <span>Total:</span>
                <span>${formatCurrency(totalFinal)}</span>
            </div>
            
            <button id="btn-checkout" class="btn-primary" style="width:100%; margin-top:20px; padding:15px; font-size:1.1rem;">Finalizar Compra</button>
        </div>
    `;

    // 4. Eventos
    
    // Botão Adicionar Cupom
    const btnAdd = container.querySelector('#btn-add-cupom');
    if (btnAdd) {
        btnAdd.onclick = () => abrirModalDescontos();
    }

    // Botão Remover Cupom
    const btnRm = container.querySelector('#btn-rm-cupom');
    if (btnRm) {
        btnRm.onclick = () => {
            state.activeDiscount = null; // Remove do estado
            renderApp(); // Atualiza a tela
        };
    }

    // Botão Finalizar
    container.querySelector('#btn-checkout').onclick = () => abrirModalCheckout(totalFinal);
}

// Modal de Seleção de Descontos
function abrirModalDescontos() {
    const usuario = state.user; 
    const idUsuario = usuario ? usuario.id : -1;

    // 1. VERIFICA ELEGIBILIDADE (Checa se o ID está nas listas baixadas do Python)
    const ehFidelidade = cache.listaFidelidade.some(c => c.id_cliente === idUsuario);
    const ehPromocional = cache.listaPromocional.some(c => c.id_cliente === idUsuario);
    const ehPrimeiraCompra = cache.listaPrimeiraCompra.some(c => c.id_cliente === idUsuario);
    const ehInativo = cache.listaInativos.some(c => c.id_cliente === idUsuario);
    const ehHighTicket = cache.listaHighTicket.some(c => c.id_cliente === idUsuario);

    // 2. CONSTRÓI AS OPÇÕES DISPONÍVEIS (Hardcoded no Front)
    let opcoesDisponiveis = [];

    // Opção A: Desconto de Primeira Compra
    if (ehPrimeiraCompra) {
        opcoesDisponiveis.push({
            tipo: 'promocional', // Mapeando para o ENUM do banco (pode ser 'promocional' ou 'outros')
            titulo: 'Primeira Compra',
            descricao: 'Boas-vindas! Ganhe desconto na sua estreia.',
            porcentagem: 10, // Hardcoded: 10%
            estilo: 'azul'
        });
    }

    // Opção B: Desconto Gamer (Promocional)
    if (ehPromocional) {
        opcoesDisponiveis.push({
            tipo: 'promocional', // ENUM do banco
            titulo: 'Desconto Gamer',
            descricao: 'Especial para quem compra periféricos.',
            porcentagem: 15, // Hardcoded: 15%
            estilo: 'laranja'
        });
    }

    // Opção C: Desconto VIP (Fidelidade)
    if (ehFidelidade) {
        opcoesDisponiveis.push({
            tipo: 'fidelidade', // ENUM do banco
            titulo: 'Cliente VIP',
            descricao: 'Recompensa por sua fidelidade.',
            porcentagem: 20, // Hardcoded: 20%
            estilo: 'roxo'
        });
    }

    // Opção D: Comprou faz tempo
    if (ehInativo) {
        opcoesDisponiveis.push({
            tipo: 'cupom',
            titulo: 'Que bom te ver!',
            descricao: 'Estávamos com saudades. Aqui está um presente.',
            porcentagem: 12, // Um valor quebrado para parecer calculado
            estilo: 'verde_agua' // Novo estilo
        });
    }

    // Opção E: Quem comprou muito
    if (ehHighTicket) {
        opcoesDisponiveis.push({
            tipo: 'parceria',
            titulo: 'Membro Elite',
            descricao: 'Seu ticket médio é superior à média da loja.',
            porcentagem: 25, // Desconto agressivo para quem gasta muito
            estilo: 'dourado' // Novo estilo
        });
    }

    // Se não tiver nenhuma opção
    if (opcoesDisponiveis.length === 0) {
        alert("Nenhum desconto disponível para o seu perfil no momento.");
        return;
    }

    // 3. RENDERIZAÇÃO VISUAL
    // Configuração de cores baseada no 'estilo' que definimos acima
    const estilos = {
        'roxo':    { cor: '#6a1b9a', bg: '#f3e5f5', icone: '👑' },
        'laranja': { cor: '#e65100', bg: '#fff3e0', icone: '🔥' },
        'azul':    { cor: '#1565c0', bg: '#e3f2fd', icone: '🎟️' },
        'verde_agua': { cor: '#00695c', bg: '#e0f2f1', icone: '👋' },
        'dourado':    { cor: '#bf9000', bg: '#fff8e1', icone: '💎' }
    };

    const htmlLista = opcoesDisponiveis.map((opcao, index) => {
        // Fallback para 'azul' se o estilo não existir
        const style = estilos[opcao.estilo] || estilos['azul'];
        
        return `
            <div class="cupom-item" data-index="${index}" 
                 style="
                    padding: 15px; 
                    border: 1px solid ${style.cor}; 
                    border-left: 6px solid ${style.cor};
                    background-color: ${style.bg}; 
                    margin-bottom: 12px; 
                    cursor: pointer; 
                    border-radius: 6px; 
                    display: flex; 
                    justify-content: space-between; 
                    align-items: center;
                    transition: transform 0.2s;
                 "
                 onmouseover="this.style.transform='translateX(5px)'"
                 onmouseout="this.style.transform='translateX(0)'"
            >
                <div style="pointer-events: none;">
                    <div style="font-weight:bold; color:${style.cor}; font-size: 0.9rem; text-transform: uppercase; margin-bottom: 4px;">
                        ${style.icone} ${opcao.titulo}
                    </div>
                    <div style="font-size:1.1rem; color:#333; font-weight:bold;">${opcao.descricao}</div>
                </div>
                
                <div style="pointer-events: none; text-align:right;">
                    <span style="
                        background:${style.cor}; 
                        color:white; 
                        padding:5px 10px; 
                        border-radius:20px; 
                        font-weight:bold; 
                        font-size: 0.9rem;
                    ">
                        ${opcao.porcentagem}% OFF
                    </span>
                </div>
            </div>
        `;
    }).join('');

    showModal("Benefícios Disponíveis", `
        <p style="margin-bottom:15px; color:#666;">Selecione um benefício para aplicar:</p>
        <div id="lista-cupons">${htmlLista}</div>
    `);

    // 4. EVENTO DE CLIQUE
    const containerCupons = document.getElementById('lista-cupons');
    if (containerCupons) {
        containerCupons.addEventListener('click', (e) => {
            const itemClicado = e.target.closest('.cupom-item');
            if (itemClicado) {
                const index = parseInt(itemClicado.dataset.index);
                
                // Recupera o objeto completo do array local
                const descontoEscolhido = opcoesDisponiveis[index];
                
                if (descontoEscolhido) {
                    // Atualiza o State Global
                    state.activeDiscount = {
                        tipo: descontoEscolhido.tipo,         // Vai para o banco (ENUM)
                        descricao: descontoEscolhido.descricao,       // Para mostrar na tela
                        porcentagem: descontoEscolhido.porcentagem // Valor matemático
                    };
                    
                    alert(`"${descontoEscolhido.descricao}" aplicado com sucesso!`);
                    hideModal();
                    renderApp(); // Atualiza carrinho
                }
            }
        });
    }
}

// Lógica: Abrir Modal e Enviar Pedido
// js/main.js

function abrirModalCheckout(total) {
    // Pega nome do usuário ou define padrão
    const nomeCliente = state.user ? state.user.nome : 'Cliente Anônimo';

    const htmlForm = `
        <p>Cliente: <strong>${nomeCliente}</strong></p>
        <p>Total a pagar: <strong>${formatCurrency(total)}</strong></p>
        
        ${state.activeDiscount ? `<p style="color:green">Cupom aplicado: ${state.activeDiscount.tipo}</p>` : ''}

        <label>Forma de Pagamento:</label>
        <select id="pagamento-select" style="width:100%; padding:8px; margin-bottom:15px; border:1px solid #ccc; border-radius:4px;">
            <option value="pix">PIX</option>
            <option value="cartao_credito">Cartão de Crédito</option>
            <option value="cartao_debito">Cartão de Débito</option>
            <option value="boleto">Boleto</option>
        </select>
        
        <button id="btn-confirmar-pagamento" style="width:100%; padding:12px; background:#28a745; color:white; border:none; border-radius:4px; font-weight:bold; cursor:pointer;">Confirmar Compra</button>
    `;

    showModal("Finalizar Pedido", htmlForm);

    document.getElementById('btn-confirmar-pagamento').onclick = async () => {
        const btn = document.getElementById('btn-confirmar-pagamento');
        const metodo = document.getElementById('pagamento-select').value;
        
        // Monta o payload (carga de dados) robusto
        const pedido = {
            // Se não tiver user logado, usa ID 1 (ou trate isso no back)
            cliente_id: state.user ? state.user.id : 1, 
            
            // Envia objeto completo, não só ID
            items: state.cart.map(p => ({
                id_produto: p.id,
                preco: p.preco
            })),
            
            total: total,
            metodo_pagamento: metodo,
            
            // Envia dados do desconto se houver
            desconto: state.activeDiscount ? {
                tipo: state.activeDiscount.tipo, // 'promocional', 'cupom', etc
                valor: state.activeDiscount.porcentagem,
                descricao: state.activeDiscount.descricao
            } : null
        };

        try {
            btn.innerText = "Processando...";
            btn.disabled = true;

            // Chama a API Python
            const res = await enviarPedido(pedido);
            
            alert("Sucesso! " + res.message);
            
            // Limpa tudo
            state.cart = []; 
            state.activeDiscount = null;
            hideModal();
            state.page = 'produtos';
            renderApp();
            
        } catch (erro) {
            console.error(erro);
            alert("Erro ao processar: " + erro.message); // message vem do throw no api.js
            btn.innerText = "Confirmar Compra";
            btn.disabled = false;
        }
    };
}

// Inicia
init();