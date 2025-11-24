// variaveis globais

export const state = {
    role: "home", // "home" | "cliente" | "loja"
    page: "produtos", // Página atual
    cart: [], // IDs dos produtos
    user: null, // Dados do cliente logado
    activeDiscount: null
};

// Dados cacheados para não bater na API toda hora (opcional)
export const cache = {
    produtos: [],
    clientes: [],
    descontos: [],
    listaFidelidade: [],
    listaPromocional: [],
    listaPrimeiraCompra: [],
    listaInativos: [],
    listaHighTicket: []
};

// Filtros globais
export const filters = {
    produto: { nome: "", tipo: "" },
    cliente: { nome: "" }
};