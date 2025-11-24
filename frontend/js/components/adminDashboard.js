// js/components/adminDashboard.js
import { formatCurrency } from '../utils.js';
import { showModal, hideModal } from './modal.js';
import { criarCliente } from '../api.js';

console.log("ADMIN DASHBOARD FOI RENDERIZADO");

export function renderAdminDashboard(container, clientes, produtos, onReload) {
    const valorEstoque = produtos.reduce((acc, p) => acc + (p.preco * p.estoqueAtual), 0);

    container.innerHTML = `
        <h2 style="color: #2c3e50; margin-bottom: 20px;">Painel Administrativo</h2>

        <div class="stats-grid" style="margin-bottom: 30px;">
            <div class="stat-card">
                <h3>Clientes Ativos</h3>
                <p class="stat-value">${clientes.length}</p>
            </div>
            <div class="stat-card">
                <h3>Catálogo</h3>
                <p class="stat-value">${produtos.length} itens</p>
            </div>
            <div class="stat-card">
                <h3>Valor em Estoque</h3>
                <p class="stat-value">${formatCurrency(valorEstoque)}</p>
            </div>
        </div>

        <div class="tabs-container">
            <button class="tab-btn active" data-target="clientes">👥 Clientes</button>
            <button class="tab-btn" data-target="produtos">📦 Produtos</button>
            <button class="tab-btn" data-target="vendas">💰 Vendas & Relatórios</button>
        </div>

        <div id="tab-content"></div>
    `;

    const contentDiv = container.querySelector('#tab-content');

    // === ABA 1: CLIENTES (COM LÓGICA DE ADICIONAR) ===
    const renderTabClientes = () => {
        contentDiv.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                <h3 style="margin: 0; margin-right: 10px;">Base de Clientes</h3>
                <button id="btn-add-cliente" class="btn-add" style="padding:8px 15px; font-size:0.9rem; background:#27ae60; color:white; border:none; border-radius:4px; cursor:pointer;">
                    + Novo Cliente
                </button>
            </div>
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Nome</th>
                            <th>Local</th>
                            <th>Pedidos</th>
                            <th>Pontos</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${clientes.map(c => `
                            <tr>
                                <td>#${c.id}</td>
                                <td><strong>${c.nome}</strong></td>
                                <td>${c.local}</td>
                                <td>${c.totalPedidos || 0}</td>
                                <td><span style="background:#e3f2fd; color:#1565c0; padding:2px 8px; border-radius:10px; font-size:0.85rem;">${c.pontos || 0} pts</span></td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;

        // --- LÓGICA DO BOTÃO ADICIONAR ---
        document.getElementById('btn-add-cliente').addEventListener('click', () => {
            const formHtml = `
                <div style="display:grid; gap:15px;">
                    <div>
                        <label style="display:block; margin-bottom:5px; font-weight:bold;">Nome Completo</label>
                        <input type="text" id="input-nome" placeholder="Ex: Maria Silva" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;">
                    </div>
                    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:10px;">
                        <div>
                            <label style="display:block; margin-bottom:5px; font-weight:bold;">Cidade</label>
                            <input type="text" id="input-cidade" placeholder="Ex: São Paulo" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;">
                        </div>
                        <div>
                            <label style="display:block; margin-bottom:5px; font-weight:bold;">Estado (UF)</label>
                            <input type="text" id="input-estado" placeholder="Ex: SP" maxlength="2" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px; text-transform:uppercase;">
                        </div>
                    </div>
                    <button id="btn-salvar-cliente" style="background:#27ae60; color:white; padding:12px; border:none; border-radius:4px; cursor:pointer; font-weight:bold; margin-top:10px;">
                        Salvar Cliente
                    </button>
                </div>
            `;

            showModal("Cadastrar Novo Cliente", formHtml);

            // Ação de Salvar dentro do Modal
            document.getElementById('btn-salvar-cliente').onclick = async () => {
                const btn = document.getElementById('btn-salvar-cliente');
                const nome = document.getElementById('input-nome').value;
                const cidade = document.getElementById('input-cidade').value;
                const estado = document.getElementById('input-estado').value.toUpperCase();

                if(!nome || !cidade || !estado) {
                    alert("Preencha todos os campos!");
                    return;
                }

                try {
                    btn.innerText = "Salvando...";
                    btn.disabled = true;

                    await criarCliente({ nome, cidade, estado });
                    
                    alert("Cliente cadastrado com sucesso!");
                    hideModal();
                    
                    // Chama a função de recarregar a página (Callback)
                    if(onReload) onReload(); 
                    
                } catch (e) {
                    alert("Erro ao salvar: " + e);
                    btn.innerText = "Salvar Cliente";
                    btn.disabled = false;
                }
            };
        });
    };

    // ABA 2: Tabela de Produtos (Nova!)
    const renderTabProdutos = () => {
        contentDiv.innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
                <h3 style="margin: 0; margin-right: 10px;">Estoque de Produtos</h3>
                <button class="btn-add" style="padding:8px 15px; font-size:0.9rem;">+ Novo Produto</button>
            </div>
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Produto</th>
                            <th>Preço</th>
                            <th>Estoque</th>
                            <th>Status</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${produtos.map(p => {
                            // Lógica visual de estoque
                            let stockClass = 'stock-ok';
                            let stockLabel = 'Disponível';
                            if (p.estoqueAtual === 0) { stockClass = 'stock-crit'; stockLabel = 'Esgotado'; }
                            else if (p.estoqueAtual < 5) { stockClass = 'stock-low'; stockLabel = 'Baixo'; }

                            return `
                                <tr>
                                    <td>#${p.id}</td>
                                    <td>
                                        <div style="font-weight:bold;">${p.nome}</div>
                                        <div style="font-size:0.8rem; color:#888;">${p.tipo}</div>
                                    </td>
                                    <td>${formatCurrency(p.preco)}</td>
                                    <td><strong>${p.estoqueAtual}</strong></td>
                                    <td class="${stockClass}">${stockLabel}</td>
                                    <td>
                                        <button style="border:1px solid #ccc; background:white; cursor:pointer; padding:2px 5px;">✏️</button>
                                    </td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            </div>
        `;
    };

    // ABA 3: Vendas e Relatórios
    const renderTabVendas = () => {
        // Aqui movemos aquele botão de Relatório que você tinha antes
        contentDiv.innerHTML = `
            <div style="text-align:center; padding: 40px; background: white; border-radius: 8px; border: 1px dashed #ccc;">
                <h3>Gestão de Vendas</h3>
                <p style="color:#666; margin-bottom:20px;">Visualize métricas detalhadas e histórico de transações.</p>
                
                <div style="display:flex; gap:15px; justify-content:center;">
                    <a href="relatorio.html" style="text-decoration:none;">
                        <button style="background:#007bff; color:white; padding:12px 25px; border:none; border-radius:6px; cursor:pointer; font-size:1rem; display:flex; align-items:center; gap:8px;">
                            📊 Abrir Dashboard de BI
                        </button>
                    </a>
                </div>
            </div>
        `;
    };

    // Lógica de Troca de Abas (Igual ao anterior)
    const tabs = container.querySelectorAll('.tab-btn');
    tabs.forEach(btn => {
        btn.addEventListener('click', () => {
            tabs.forEach(t => t.classList.remove('active'));
            btn.classList.add('active');
            const target = btn.dataset.target;
            if (target === 'clientes') renderTabClientes();
            if (target === 'produtos') renderTabProdutos();
            if (target === 'vendas') renderTabVendas();
        });
    });

    renderTabClientes();
}