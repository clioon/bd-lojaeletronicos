// variaveis globais
export const state = {
    role: "home", // "home" | "cliente" | "loja"
    page: "produtos", // Página atual
    cart: [], // IDs dos produtos
    user: null, // Dados do cliente logado
    activeDiscount: null
};

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

export const filters = {
    produto: { nome: "", tipo: "" },
    cliente: { nome: "" }
};