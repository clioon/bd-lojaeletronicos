// js/components/productList.js
import { formatCurrency } from '../utils.js';
import { showModal } from './modal.js';

export function renderProductList(container, produtos, onAddToCart) {
    
    // === 1. Estrutura fixa: Barra de Filtros + Container do Grid ===
    const filterHTML = `
        <div class="filters-bar" style="margin-bottom: 20px; display: flex; gap: 10px; flex-wrap: wrap;">
            <input type="text" id="search-input" placeholder="Buscar produto..." style="padding: 10px; flex: 1; border: 1px solid #ccc; border-radius: 4px;">
            
            <select id="type-select" style="padding: 10px; border: 1px solid #ccc; border-radius: 4px;">
                <option value="">Todos os Tipos</option>
                <option value="Hardware">Hardware</option>
                <option value="Dispositivo">Dispositivo</option>
                <option value="Periférico">Periférico</option>
            </select>
        </div>
        <div id="grid-container"></div>
    `;
    
    // Define o HTML base apenas uma vez para não perder o foco do input ao digitar
    container.innerHTML = filterHTML;
    
    const gridContainer = container.querySelector('#grid-container');
    const searchInput = container.querySelector('#search-input');
    const typeSelect = container.querySelector('#type-select');

    // === 2. Função que desenha os cards ===
    const desenharGrid = (listaFiltrada) => {
        // Limpa o grid atual
        gridContainer.innerHTML = '';

        if (listaFiltrada.length === 0) {
            gridContainer.innerHTML = '<div style="text-align:center; padding:20px; color:#666;">Nenhum produto encontrado.</div>';
            return;
        }
        
        const grid = document.createElement('div');
        grid.className = 'product-grid';
        
        listaFiltrada.forEach(p => {
            const card = document.createElement('div');
            card.className = 'product-card';

            // --- Lógica Visual de Estoque ---
            const estoque = p.estoqueAtual || 0;
            const btnClass = estoque > 0 ? 'btn-add' : 'btn-disabled';
            const btnText = estoque > 0 ? 'Adicionar' : 'Sem Estoque';
            const disabledAttr = estoque > 0 ? '' : 'disabled';
            
            // Texto do estoque (Vermelho se < 5)
            let stockHtml = '';
            if (estoque === 0) {
                stockHtml = '<span style="color:red; font-weight:bold">Esgotado</span>';
            } else if (estoque < 6) {
                stockHtml = `<span style="color:red">Restam: <strong>${estoque}</strong></span>`;
            } else {
                stockHtml = `<span style="color:#666">Restam: <strong>${estoque}</strong></span>`;
            }

            // --- Proteção para o Tipo (evita erro toLowerCase) ---
            const tipoSafe = p.tipo || 'Outro';

            // --- HTML do Card ---
            card.innerHTML = `
                <div class="card-header">
                    <h3>${p.nome}</h3>
                    <span class="tag ${tipoSafe.toLowerCase()}">${tipoSafe}</span>
                </div>
                <div class="card-body">
                    <p class="desc">${p.descricao || 'Sem descrição disponível.'}</p>
                    
                    <div style="font-size:0.85rem; color:#888; margin-bottom:10px">
                        ${p.specs_hardware ? `Specs: ${p.specs_hardware}` : ''}
                        ${p.cor_dispositivo ? `Cor: ${p.cor_dispositivo}` : ''}
                    </div>

                    <div class="price-row">
                        <span class="price">${formatCurrency(p.preco)}</span>
                        <small style="font-size: 0.9rem;">${stockHtml}</small>
                    </div>
                </div>
                <div class="card-footer">
                    <button class="${btnClass}" ${disabledAttr}>${btnText}</button>
                    <button class="btn-details">Detalhes</button>
                </div>
            `;

            // --- Eventos dos Botões ---
            
            // 1. Botão Adicionar (só adiciona evento se tiver estoque)
            if(estoque > 0) {
                const btnAdd = card.querySelector(`.${btnClass}`);
                btnAdd.addEventListener('click', () => onAddToCart(p));
            }

            // 2. Botão Detalhes (Abre Modal)
            const btnDetails = card.querySelector('.btn-details');
            btnDetails.addEventListener('click', () => {
                showModal(p.nome, `
                    <p><strong>Categoria:</strong> ${p.categoria || tipoSafe}</p>
                    <p><strong>Descrição:</strong> ${p.descricao || '-'}</p>
                    <p><strong>Preço:</strong> ${formatCurrency(p.preco)}</p>
                    <hr>
                    <h4>Detalhes Técnicos:</h4>
                    <ul>
                        ${p.specs_hardware ? `<li>Hardware: ${p.specs_hardware}</li>` : ''}
                        ${p.cor_dispositivo ? `<li>Cor: ${p.cor_dispositivo}</li>` : ''}
                        ${p.conexao_periferico ? `<li>Conexão: ${p.conexao_periferico}</li>` : ''}
                        <li>Estoque disponível: ${estoque} unidades</li>
                    </ul>
                `);
            });

            grid.appendChild(card);
        });

        gridContainer.appendChild(grid);
    };

    // === 3. Renderização Inicial ===
    desenharGrid(produtos);

    // === 4. Lógica de Filtragem ===
    const aplicarFiltros = () => {
        const termo = searchInput.value.toLowerCase();
        const tipoSelecionado = typeSelect.value;

        const filtrados = produtos.filter(p => {
            // Filtro por nome
            const matchNome = p.nome.toLowerCase().includes(termo);
            
            // Filtro por tipo (se vazio, traz todos)
            const tipoItem = p.tipo || ""; // Proteção se tipo for null
            const matchTipo = tipoSelecionado === "" || tipoItem === tipoSelecionado;
            
            return matchNome && matchTipo;
        });

        desenharGrid(filtrados);
    };

    // Escuta eventos de digitação e mudança de select
    searchInput.addEventListener('input', aplicarFiltros);
    typeSelect.addEventListener('change', aplicarFiltros);
}