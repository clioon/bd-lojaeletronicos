// js/components/adminDashboard.js
import { formatCurrency } from '../utils.js';

export function renderAdminDashboard(container, clientes, produtos) {
    
    // Cálculos simples para as estatísticas (igual tinha no original)
    const totalClientes = clientes.length;
    const totalProdutos = produtos.length;
    const valorEstoque = produtos.reduce((acc, p) => acc + (p.preco * p.estoqueAtual), 0);

    const html = `
        <h2>Painel Administrativo</h2>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>Clientes Ativos</h3>
                <p class="stat-value">${totalClientes}</p>
            </div>
            <div class="stat-card">
                <h3>Produtos Cadastrados</h3>
                <p class="stat-value">${totalProdutos}</p>
            </div>
            <div class="stat-card">
                <h3>Valor em Estoque</h3>
                <p class="stat-value">${formatCurrency(valorEstoque)}</p>
            </div>
        </div>

        <hr style="margin: 30px 0; border: 0; border-top: 1px solid #ddd;">

        <h3>Base de Clientes</h3>
        <div class="table-container">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nome</th>
                        <th>Local</th>
                        <th>Pontos Fidelidade</th>
                    </tr>
                </thead>
                <tbody>
                    ${clientes.map(c => `
                        <tr>
                            <td>#${c.id}</td>
                            <td>${c.nome}</td>
                            <td>${c.local}</td>
                            <td>${c.pontos || 0}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        </div>
    `;

    container.innerHTML = html;
}