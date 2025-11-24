// funcoes utilitarias

export function formatCurrency(value) {
    return Number(value).toLocaleString("pt-BR", {
        style: "currency",
        currency: "BRL",
    });
}

export function formatDate(dateString) {
    if(!dateString) return "-";
    const date = new Date(dateString);
    return date.toLocaleDateString("pt-BR");
}