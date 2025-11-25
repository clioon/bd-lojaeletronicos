import { state } from '../state.js';

export function renderHome(container, onNavigate) {
    container.innerHTML = `
        <div class="home-container">
            <h1>Bem-vindo ao Sistema Kabom</h1>
            <p>Selecione seu perfil de acesso:</p>
            
            <div class="profile-selection">
                <div class="profile-card" id="btn-cliente">
                    <h2>🛒 Sou Cliente</h2>
                    <p>Quero comprar produtos</p>
                </div>

                <div class="profile-card" id="btn-loja">
                    <h2>💼 Sou Loja</h2>
                    <p>Quero gerenciar vendas e clientes</p>
                </div>
            </div>
        </div>
    `;

    // Eventos
    container.querySelector('#btn-cliente').onclick = () => {
        state.role = 'cliente';
        onNavigate('produtos'); // Vai para a loja
    };

    container.querySelector('#btn-loja').onclick = () => {
        state.role = 'loja';
        onNavigate('admin'); // Vai para o dashboard admin
    };
}