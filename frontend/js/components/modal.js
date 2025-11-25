const modalOverlay = document.getElementById("modal-overlay");
const modalTitle = document.getElementById("modal-title");
const modalBody = document.getElementById("modal-body");
const modalCloseBtn = document.getElementById("modal-close");

// Fecha o modal ao clicar no botão X ou fora da janela
export function setupModalListeners() {
    modalCloseBtn.addEventListener("click", hideModal);
    modalOverlay.addEventListener("click", (e) => {
        if (e.target === modalOverlay) hideModal();
    });
}

export function showModal(title, contentHTML) {
    modalTitle.innerText = title;
    modalBody.innerHTML = contentHTML;
    modalOverlay.classList.remove("hidden");
    modalOverlay.classList.add("flex");
}

export function hideModal() {
    modalOverlay.classList.add("hidden");
    modalOverlay.classList.remove("flex");
    modalBody.innerHTML = ""; // Limpa memória
}