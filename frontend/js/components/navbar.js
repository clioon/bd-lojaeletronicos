// js/components/navbar.js
import { state } from '../state.js';

export function renderNavbar(container, onNavigate) {
    // Calcula itens no carrinho
    const cartCount = state.cart.length;

    // HTML da Barra
    const html = `
        <nav class="navbar">
            <div class="logo" style="cursor:pointer">Kabom!</div>
            <div class="menu-items">
                <button data-page="produtos" class="btn-nav ${state.page === 'produtos' ? 'active' : ''}">
                    Loja
                </button>
                <button data-page="carrinho" class="btn-nav">
                    Carrinho (${cartCount})
                </button>
                <span class="user-info">
                    ${state.user ? `Olá, ${state.user.nome}` : 'Visitante'}
                </span>
            </div>
        </nav>
    `;

    container.innerHTML = html;

    // Adiciona eventos aos botões recém-criados
    container.querySelectorAll('.btn-nav').forEach(btn => {
        btn.addEventListener('click', () => {
            const targetPage = btn.dataset.page;
            // Chama a função de navegação que passaremos pelo main.js
            if(onNavigate) onNavigate(targetPage); 
        });
    });
    
    // Clique no Logo volta para produtos
    container.querySelector('.logo').addEventListener('click', () => onNavigate('produtos'));
}