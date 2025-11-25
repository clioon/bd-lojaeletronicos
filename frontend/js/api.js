const API_URL = "http://localhost:5000/api";

export async function buscarProdutos() {
    try {
        const response = await fetch(`${API_URL}/produtos`);
        if (!response.ok) throw new Error("Erro na API");
        return await response.json();
    } catch (error) {
        console.error(error);
        return [];
    }
}

export async function buscarClientes() {
    try {
        const response = await fetch(`${API_URL}/clientes`);
        return await response.json();
    } catch (error) {
        console.error(error);
        return [];
    }
}

export async function enviarPedido(pedido) {
    try {
        const response = await fetch(`${API_URL}/checkout`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(pedido)
        });
        return await response.json();
    } catch (error) {
        throw error;
    }
}

export async function buscarDescontos() {
    try {
        const response = await fetch(`${API_URL}/descontos`);
        return await response.json();
    } catch (error) {
        console.error(error);
        return [];
    }
}

export async function buscarClientesFidelidade() {
    try {
        const res = await fetch(`${API_URL}/clientes/fidelidade`);
        return await res.json();
    } catch (e) { return []; }
}

export async function buscarClientesPromocionais() {
    try {
        const res = await fetch(`${API_URL}/clientes/promocional`);
        return await res.json();
    } catch (e) { return []; }
}

export async function buscarClientesPrimeiraCompra() {
    try {
        const res = await fetch(`${API_URL}/clientes/primeira-compra`);
        return await res.json();
    } catch (e) { return []; }
}

export async function buscarClientesInativos() {
    try {
        const res = await fetch(`${API_URL}/clientes/inativos`);
        return await res.json();
    } catch (e) { return []; }
}

export async function buscarClientesHighTicket() {
    try {
        const res = await fetch(`${API_URL}/clientes/high-ticket`);
        return await res.json();
    } catch (e) { return []; }
}

export async function buscarRecomendacoes(idProduto) {
    try {
        const res = await fetch(`${API_URL}/produtos/${idProduto}/recomendacoes`);
        return await res.json();
    } catch (e) {
        console.error(e);
        return [];
    }
}

export async function criarCliente(dadosCliente) {
    try {
        const response = await fetch(`${API_URL}/clientes`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(dadosCliente)
        });
        return await response.json();
    } catch (error) {
        throw error;
    }
}

export async function criarProduto(dadosProduto) {
    try {
        const response = await fetch(`${API_URL}/produtos`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(dadosProduto)
        });
        return await response.json();
    } catch (error) {
        throw error;
    }
}