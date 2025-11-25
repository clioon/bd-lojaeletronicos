import { state } from '../state.js';

export function renderNavbar(container, onNavigate) {
    const cartCount = state.cart.length;
    const isLoja = state.role === 'loja';

    // 1. Define os botões baseado no perfil
    let menuHtml = '';

    if (isLoja) {
        // === MENU DO LOJISTA ===
        menuHtml = `
            <button data-page="admin" class="btn-nav ${state.page === 'admin' ? 'active' : ''}">Dashboard</button>
            <button data-page="logout" class="btn-nav" style="color: #ff6b6b;">Sair da Loja</button>
        `;
    } else {
        // === MENU DO CLIENTE ===
        menuHtml = `
            <button data-page="produtos" class="btn-nav ${state.page === 'produtos' ? 'active' : ''}">Loja</button>
            <button data-page="carrinho" class="btn-nav ${state.page === 'carrinho' ? 'active' : ''}">Carrinho (${cartCount})</button>
            <button data-page="logout" class="btn-nav" style="border-left:1px solid #444; margin-left:10px; padding-left:15px">Sair</button>
        `;
    }

    // 2. Renderiza o HTML
    const html = `
        <nav class="navbar" style="background-color: ${isLoja ? '#1a1a1a' : '#1a1a1a'}">
            <div class="logo" style="cursor:pointer; color: ${isLoja ? '#3498db' : '#ff6600'}">
                ${isLoja ? 'KABOM ADMIN' : 'Kabom!'}
            </div>
            
            <div class="menu-items">
                ${menuHtml}
                <span class="user-info">
                    ${state.user ? `Olá, ${state.user.nome.split(' ')[0]}` : 'Visitante'}
                </span>
            </div>
        </nav>
    `;

    container.innerHTML = html;

    // 3. Eventos de Clique
    container.querySelectorAll('.btn-nav').forEach(btn => {
        btn.addEventListener('click', () => {
            const targetPage = btn.dataset.page;
            if (onNavigate) onNavigate(targetPage); 
        });
    });
    
    // Clique no Logo
    container.querySelector('.logo').addEventListener('click', () => {
        onNavigate(isLoja ? 'admin' : 'produtos');
    });
}