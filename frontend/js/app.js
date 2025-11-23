// Estado global básico
const state = {
  role: "home", // "home" | "cliente" | "loja"
  clientePage: "loja",
  lojaPage: "produtos",
};

// Filtros globais
const filters = {
  produtos: {
    nome: "",
    tipo: "",
    precoMin: "",
    precoMax: "",
    desconto: "",
  },
  clientes: {
    nome: "",
    local: "",
    gastoMin: "",
    gastoMax: "",
    fidelidadeMin: "",
  },
};


// controla quantos elementos aparecem por lista
const GLOBAL_PAGE_SIZE = 10;


// Dados de exemplo (dummies) | Trocar dummies por chamadas reais a APIs / SGBD

// Produtos 
const products = Array.from({ length: 23 }).map((_, i) => {
  const id = i + 1;
  const basePrice = 20 + i * 3;
  const discount = (i % 4) * 5; // 0,5,10,15

  const tipos = ["Dispositivo", "Hardware", "Periférico"];
  const tipo = tipos[i % tipos.length]; // alterna entre os tipos

  return {
    id,
    nome: `Produto ${id}`,
    preco: basePrice,
    descontoPercent: discount,
    pontosFidelidade: 10 + (i % 5) * 5,
    estoqueAtual: 5 + (i * 2) % 40,
    estoqueMinimo: 10,
    tipo, // ← IMPORTANTÍSSIMO
    descricao: `Descrição completa do Produto ${id}. Informações adicionais e detalhes técnicos.`,
  };
});

// Descontos
const discounts = [
  {
    id: 1,
    nome: "Desconto Boas-vindas",
    descricao: "10% de desconto na primeira compra.",
    percentual: 10,
    ativo: true,
  },
  {
    id: 2,
    nome: "Semana do Cliente",
    descricao: "5% em toda a loja para clientes cadastrados.",
    percentual: 5,
    ativo: true,
  },
  {
    id: 3,
    nome: "Queima de Estoque",
    descricao: "Até 20% em produtos selecionados.",
    percentual: 20,
    ativo: true,
  },
  {
    id: 4,
    nome: "Cupom Expirado",
    descricao: "Exemplo de desconto desativado.",
    percentual: 15,
    ativo: false,
  },
];

// Clientes
const clientes = Array.from({ length: 18 }).map((_, i) => {
  const id = i + 1;
  const cidades = ["São Paulo", "Rio de Janeiro", "Belo Horizonte", "Curitiba"];
  const nome = `Cliente ${id}`;
  const totalGasto = 100 + i * 47;
  const dataCadastro = new Date(2022, (i % 12), (i % 28) + 1);
  return {
    id,
    nome,
    local: cidades[i % cidades.length],
    totalGasto,
    dataCadastro,
    email: `cliente${id}@email.com`,
    telefone: `(11) 9${id.toString().padStart(3, "0")}-0000`,
  };
});

// Estatísticas (loja/estatísticas)
const estatisticas = [
  { id: 1, metrica: "Faturamento mensal (R$)", valor: "45.230,90" },
  { id: 2, metrica: "Clientes ativos", valor: "1.245" },
  { id: 3, metrica: "Ticket médio (R$)", valor: "145,60" },
  { id: 4, metrica: "Produtos cadastrados", valor: String(products.length) },
  { id: 5, metrica: "Cupons ativos", valor: String(discounts.filter(d => d.ativo).length) },
  { id: 6, metrica: "Pedidos no último mês", valor: "382" },
  { id: 7, metrica: "Taxa de recompra", valor: "27%" },
];

// Carrinho (lista de IDs de produto)
let cart = [];

// Referências DOM
let appRoot;
let modalOverlay;
let modalTitleEl;
let modalBodyEl;
let modalCloseBtn;

document.addEventListener("DOMContentLoaded", () => {
  appRoot = document.getElementById("app");
  modalOverlay = document.getElementById("modal-overlay");
  modalTitleEl = document.getElementById("modal-title");
  modalBodyEl = document.getElementById("modal-body");
  modalCloseBtn = document.getElementById("modal-close");

  modalCloseBtn.addEventListener("click", hideModal);
  modalOverlay.addEventListener("click", (e) => {
    if (e.target === modalOverlay) hideModal();
  });

  render();
});

/* ========== Helpers de formatação ========== */

function formatCurrency(value) {
  return value.toLocaleString("pt-BR", {
    style: "currency",
    currency: "BRL",
  });
}

function formatDate(date) {
  return date.toLocaleDateString("pt-BR");
}

/* ========== Navegação ========== */

function setRole(role) {
  state.role = role;
  render();
}

function setSubpage(role, page) {
  if (role === "cliente") {
    state.clientePage = page;
  } else {
    state.lojaPage = page;
  }
  render();
}

/* ========== Render principal ========== */

function render() {
  appRoot.innerHTML = "";

  if (state.role === "home") {
    renderLanding();
    return;
  }

  renderLayout();
}

/* Página inicial */

function renderLanding() {
  const wrapper = document.createElement("div");
  wrapper.className = "landing";

  const h1 = document.createElement("h1");
  h1.textContent = "Front-end de SGBD - Loja / Cliente";

  const p = document.createElement("p");
  p.textContent =
    "Escolha uma visão para começar: cliente (consumidor) ou loja (administração).";

  const btns = document.createElement("div");
  btns.className = "landing-buttons";

  const btnCliente = document.createElement("button");
  btnCliente.className = "btn btn-primary";
  btnCliente.textContent = "Visão do Cliente";
  btnCliente.onclick = () => setRole("cliente");

  const btnLoja = document.createElement("button");
  btnLoja.className = "btn btn-secondary";
  btnLoja.textContent = "Visão da Loja";
  btnLoja.onclick = () => setRole("loja");

  btns.appendChild(btnCliente);
  btns.appendChild(btnLoja);

  wrapper.appendChild(h1);
  wrapper.appendChild(p);
  wrapper.appendChild(btns);

  appRoot.appendChild(wrapper);
}

/* Layout de cliente / loja */

function renderLayout() {
  const role = state.role;

  const topbar = document.createElement("div");
  topbar.className = "topbar";

  const topLeft = document.createElement("div");
  topLeft.className = "topbar-left";

  const title = document.createElement("h2");
  title.textContent = role === "cliente" ? "Kabom Eletrônicos" : "Kabom Eletrônicos"; // Mesmo título para ambos (pode ser diferente se desejado)

  const modePill = document.createElement("span");
  modePill.className = `mode-pill ${role}`;
  modePill.textContent = role === "cliente" ? "CLIENTE" : "LOJA";

  topLeft.appendChild(title);
  topLeft.appendChild(modePill);

  const topRight = document.createElement("div");

  /* ======= ALTERAÇÃO PEDIDA ======= */
  if (role === "cliente") {
    const homeBtn = document.createElement("button");
    homeBtn.className = "btn btn-secondary btn-small";
    homeBtn.textContent = "Perfil";

    // cliente 1 por enquanto (futuro: cliente logado real)
    const clienteAtual = clientes[0];

    homeBtn.onclick = () => showClienteModal(clienteAtual);

    topRight.appendChild(homeBtn);
  }
  // No modo loja não adicionamos nada → botão removido.
  /* ================================= */

  topbar.appendChild(topLeft);
  topbar.appendChild(topRight);

  const subnav = document.createElement("div");
  subnav.className = "subnav";

  if (role === "cliente") {
    addSubnavButton(subnav, "Loja", "loja", state.clientePage, () =>
      setSubpage("cliente", "loja")
    );
    addSubnavButton(subnav, "Descontos", "descontos", state.clientePage, () =>
      setSubpage("cliente", "descontos")
    );
    addSubnavButton(subnav, "Carrinho", "carrinho", state.clientePage, () =>
      setSubpage("cliente", "carrinho")
    );
  } else {
    addSubnavButton(subnav, "Produtos", "produtos", state.lojaPage, () =>
      setSubpage("loja", "produtos")
    );
    addSubnavButton(subnav, "Estoque", "estoque", state.lojaPage, () =>
      setSubpage("loja", "estoque")
    );
    addSubnavButton(subnav, "Descontos", "descontos", state.lojaPage, () =>
      setSubpage("loja", "descontos")
    );
    addSubnavButton(subnav, "Clientes", "clientes", state.lojaPage, () =>
      setSubpage("loja", "clientes")
    );
    addSubnavButton(
      subnav,
      "Estatísticas",
      "estatisticas",
      state.lojaPage,
      () => setSubpage("loja", "estatisticas")
    );
  }

  const content = document.createElement("div");

  if (role === "cliente") {
    if (state.clientePage === "loja") renderClienteLoja(content);
    else if (state.clientePage === "descontos") renderClienteDescontos(content);
    else renderClienteCarrinho(content);
  } else {
    switch (state.lojaPage) {
      case "produtos": renderLojaProdutos(content); break;
      case "estoque": renderLojaEstoque(content); break;
      case "descontos": renderLojaDescontos(content); break;
      case "clientes": renderLojaClientes(content); break;
      case "estatisticas": renderLojaEstatisticas(content); break;
    }
  }

  appRoot.appendChild(topbar);
  appRoot.appendChild(subnav);
  appRoot.appendChild(content);
}


function addSubnavButton(container, label, key, current, onClick) {
  const btn = document.createElement("button");
  btn.className =
    "subnav-button" + (current === key ? " active" : "");
  btn.textContent = label;
  btn.onclick = onClick;
  container.appendChild(btn);
}

/* ========== Renderizadores de tela (cliente) ========== */

function renderClienteLoja(container) {
  const title = document.createElement("div");
  title.className = "screen-title";
  title.textContent = "Catálogo de produtos";

  const desc = document.createElement("div");
  desc.className = "screen-description";
  desc.textContent =
    "Produtos disponíveis para compra. Clique para mais detalhes e adicione ao carrinho!";

  container.appendChild(title);
  container.appendChild(desc);

  const filtrosBtn = document.createElement("button");
  filtrosBtn.className = "btn btn-secondary";
  filtrosBtn.textContent = "Filtros";
  filtrosBtn.style.marginBottom = "12px";
  filtrosBtn.onclick = () => abrirModalFiltrosProdutos(() => render());
  container.appendChild(filtrosBtn);

  const dataFiltrada = filtrarProdutos(products);


  const columns = [
    {
      header: "Nome",
      renderCell: (p) => p.nome,
    },
    {
      header: "Tipo",
      renderCell: (p) => p.tipo,
    },
    {
      header: "Preço",
      renderCell: (p) => formatCurrency(p.preco),
    },
    {
      header: "Desconto",
      renderCell: (p) =>
        p.descontoPercent > 0 ? `${p.descontoPercent}%` : "-",
    },
    {
      header: "Pontos fidelidade",
      renderCell: (p) => p.pontosFidelidade,
    },
    {
      header: "",
      className: "actions",
      isAction: true,
      renderCell: (p) => {
        const btn = document.createElement("button");

        const isInCart = cart.includes(p.id);

        if (isInCart) {
          btn.className = "btn btn-small btn-success";
          btn.textContent = "Adicionado!";
          btn.disabled = true;
        } else {
          btn.className = "btn btn-small btn-primary";
          btn.textContent = "Adicionar ao carrinho";

          btn.onclick = (e) => {
            e.stopPropagation();
            addToCart(p.id);

            // feedback imediato
            btn.className = "btn btn-small btn-success";
            btn.textContent = "Adicionado!";
            btn.disabled = true;
          };
        }

        return btn;
      },
    },
  ];

  renderPaginatedList(container, {
    data: dataFiltrada,
    columns,
    pageSize: GLOBAL_PAGE_SIZE,
    onRowClick: (p) => showProductModal(p),
  });
}

function renderClienteDescontos(container) {
  const title = document.createElement("div");
  title.className = "screen-title";
  title.textContent = "Descontos disponíveis";

  const desc = document.createElement("div");
  desc.className = "screen-description";
  desc.textContent =
    "Lista de descontos aplicáveis aos produtos da loja.";

  container.appendChild(title);
  container.appendChild(desc);

  const ativos = discounts.filter((d) => d.ativo);

  const columns = [
    {
      header: "Nome",
      renderCell: (d) => d.nome,
    },
    {
      header: "Descrição",
      renderCell: (d) => d.descricao,
    },
  ];

  renderPaginatedList(container, {
    data: ativos,
    columns,
    pageSize: GLOBAL_PAGE_SIZE,
    onRowClick: (d) => showDiscountModal(d),
  });
}

function renderClienteCarrinho(container) {
  const title = document.createElement("div");
  title.className = "screen-title";
  title.textContent = "Carrinho";

  const desc = document.createElement("div");
  desc.className = "screen-description";
  desc.textContent =
    "Produtos adicionados ao carrinho. Clique para mais detalhes e siga para compra!";

  container.appendChild(title);
  container.appendChild(desc);

  const items = cart
    .map((id) => products.find((p) => p.id === id))
    .filter(Boolean);

  const columns = [
    {
      header: "Nome",
      renderCell: (p) => p.nome,
    },
    {
      header: "Tipo",
      renderCell: (p) => p.tipo,
    },  
    {
      header: "Preço",
      renderCell: (p) => formatCurrency(p.preco),
    },
    {
      header: "Desconto",
      renderCell: (p) =>
        p.descontoPercent > 0 ? `${p.descontoPercent}%` : "-",
    },
    {
      header: "Pontos fidelidade",
      renderCell: (p) => p.pontosFidelidade,
    },
    {
      header: "",
      className: "actions",
      isAction: true,
      renderCell: (p) => {
        const btn = document.createElement("button");
        btn.className = "btn btn-small btn-danger";
        btn.textContent = "Remover do carrinho";
        btn.onclick = (e) => {
          e.stopPropagation();
          removeFromCart(p.id);
        };
        return btn;
      },
    },
  ];

  renderPaginatedList(container, {
    data: items,
    columns,
    pageSize: GLOBAL_PAGE_SIZE,
    onRowClick: (p) => showProductModal(p),
  });

  // Botão "Seguir para a compra"
  const checkoutBtn = document.createElement("button");
  checkoutBtn.className = "btn btn-success";
  checkoutBtn.textContent = "Seguir para a compra";
  checkoutBtn.style.marginTop = "16px";
  checkoutBtn.onclick = () => showCheckoutModal(items);

  container.appendChild(checkoutBtn);

}

/* ========== Renderizadores de tela (loja) ========== */

function renderLojaProdutos(container) {

  const filtrosBtn = document.createElement("button");
  filtrosBtn.className = "btn btn-secondary";
  filtrosBtn.textContent = "Filtros";
  filtrosBtn.style.marginBottom = "12px";
  filtrosBtn.onclick = () => abrirModalFiltrosProdutos(() => render());
  container.appendChild(filtrosBtn);

  const dataFiltrada = filtrarProdutos(products);


  const title = document.createElement("div");
  title.className = "screen-title";
  title.textContent = "Produtos (Visão da Loja)";

  const desc = document.createElement("div");
  desc.className = "screen-description";
  desc.textContent =
    "Lista de produtos cadastrados. Clique em um produto para ver mais detalhes.";

  container.appendChild(title);
  container.appendChild(desc);

  const columns = [
    { header: "Nome", renderCell: (p) => p.nome },
    { header: "Tipo", renderCell: (p) => p.tipo,},
    { header: "Preço", renderCell: (p) => formatCurrency(p.preco) },
    {
      header: "Desconto",
      renderCell: (p) =>
        p.descontoPercent > 0 ? `${p.descontoPercent}%` : "-",
    },
    {
      header: "Pontos fidelidade",
      renderCell: (p) => p.pontosFidelidade,
    },
  ];

  renderPaginatedList(container, {
    data: dataFiltrada,
    columns,
    pageSize: GLOBAL_PAGE_SIZE,
    onRowClick: (p) => showProductModal(p),
  });
}

function renderLojaEstoque(container) {
  const title = document.createElement("div");
  title.className = "screen-title";
  title.textContent = "Estoque";

  const desc = document.createElement("div");
  desc.className = "screen-description";
  desc.textContent =
    "Quantidade atual e mínima de estoque por produto.";

  container.appendChild(title);
  container.appendChild(desc);

  const filtrosBtn = document.createElement("button");
  filtrosBtn.className = "btn btn-secondary";
  filtrosBtn.textContent = "Filtros";
  filtrosBtn.style.marginBottom = "12px";
  filtrosBtn.onclick = () => abrirModalFiltrosProdutos(() => render());
  container.appendChild(filtrosBtn);

  const dataFiltrada = filtrarProdutos(products);


  const columns = [
    { header: "Nome", renderCell: (p) => p.nome },
    { header: "Tipo", renderCell: (p) => p.tipo,},

    { header: "Preço", renderCell: (p) => formatCurrency(p.preco) },
    {
      header: "Desconto",
      renderCell: (p) =>
        p.descontoPercent > 0 ? `${p.descontoPercent}%` : "-",
    },
    {
      header: "Estoque",
      renderCell: (p) => {
        const badge =
          p.estoqueAtual < p.estoqueMinimo
            ? `<span class="badge badge-warning">Baixo</span>`
            : `<span class="badge badge-success">OK</span>`;
        return `${p.estoqueAtual} / ${p.estoqueMinimo} ${badge}`;
      },
    },
  ];

  renderPaginatedList(container, {
    data: dataFiltrada,
    columns,
    pageSize: GLOBAL_PAGE_SIZE,
    onRowClick: (p) => showProductModal(p),
  });
}

function renderLojaDescontos(container) {
  const title = document.createElement("div");
  title.className = "screen-title";
  title.textContent = "Descontos (Administração)";

  const desc = document.createElement("div");
  desc.className = "screen-description";
  desc.textContent =
    "Gerenciamento de descontos ativos e inativos. Clique em uma linha para ver detalhes ou desative.";

  container.appendChild(title);
  container.appendChild(desc);

  const columns = [
    {
      header: "Nome",
      renderCell: (d) => d.nome,
    },
    {
      header: "Descrição",
      renderCell: (d) => d.descricao,
    },
    {
      header: "Status",
      renderCell: (d) =>
        d.ativo
          ? '<span class="badge badge-success">Ativo</span>'
          : '<span class="badge badge-muted">Inativo</span>',
    },
    {
      header: "",
      className: "actions",
      isAction: true,
      renderCell: (d) => {
        const btn = document.createElement("button");
        btn.className = "btn btn-small " + (d.ativo ? "btn-danger" : "btn-primary");
        btn.textContent = d.ativo ? "Desativar" : "Ativar";

        btn.onclick = (e) => {
          e.stopPropagation();
          d.ativo = !d.ativo; // alterna
          render(); // re-renderiza lista
        };

        return btn;
      },
    }
  ];

  renderPaginatedList(container, {
    data: discounts,
    columns,
    pageSize: GLOBAL_PAGE_SIZE,
    onRowClick: (d) => showDiscountModal(d),
    rowClass: (d) => (!d.ativo ? "row-inactive" : ""),
  });
}

function renderLojaClientes(container) {

  const filtrosBtn = document.createElement("button");
  filtrosBtn.className = "btn btn-secondary";
  filtrosBtn.textContent = "Filtros";
  filtrosBtn.style.marginBottom = "12px";
  filtrosBtn.onclick = () => abrirModalFiltrosClientes(() => render());
  container.appendChild(filtrosBtn);

  const dataFiltrada = filtrarClientes(clientes);


  const title = document.createElement("div");
  title.className = "screen-title";
  title.textContent = "Clientes";

  const desc = document.createElement("div");
  desc.className = "screen-description";
  desc.textContent =
    "Lista de clientes cadastrados. Clique em um cliente para ver detalhes.";

  container.appendChild(title);
  container.appendChild(desc);

  const columns = [
    { header: "Nome", renderCell: (c) => c.nome },
    { header: "Local", renderCell: (c) => c.local },
    {
      header: "Total gasto",
      renderCell: (c) => formatCurrency(c.totalGasto),
    },
    {
      header: "Data de cadastro",
      renderCell: (c) => formatDate(c.dataCadastro),
    },
  ];

  renderPaginatedList(container, {
    data: dataFiltrada,
    columns,
    pageSize: GLOBAL_PAGE_SIZE,
    onRowClick: (c) => showClienteModal(c),
  });
}

function renderLojaEstatisticas(container) {
  const title = document.createElement("div");
  title.className = "screen-title";
  title.textContent = "Estatísticas";

  const desc = document.createElement("div");
  desc.className = "screen-description";
  desc.textContent =
    "Resumo de métricas da loja. Essa tela também usa uma lista paginada.";

  container.appendChild(title);
  container.appendChild(desc);

  const columns = [
    { header: "Métrica", renderCell: (e) => e.metrica },
    { header: "Valor", renderCell: (e) => e.valor },
  ];

  renderPaginatedList(container, {
    data: estatisticas,
    columns,
    pageSize: GLOBAL_PAGE_SIZE,
    onRowClick: (e) => showStatsModal(e),
  });
}

/* ========== Componente genérico de lista paginada ========== */

function filtrarProdutos(lista) {
  return lista.filter(p => {
    if (filters.produtos.nome && !p.nome.toLowerCase().includes(filters.produtos.nome.toLowerCase()))
      return false;

    if (filters.produtos.tipo && p.tipo !== filters.produtos.tipo)
      return false;

    if (filters.produtos.precoMin && p.preco < Number(filters.produtos.precoMin))
      return false;

    if (filters.produtos.precoMax && p.preco > Number(filters.produtos.precoMax))
      return false;

    if (filters.produtos.desconto && p.descontoPercent < Number(filters.produtos.desconto))
      return false;

    return true;
  });
}

function filtrarClientes(lista) {
  return lista.filter(c => {
    if (filters.clientes.nome && !c.nome.toLowerCase().includes(filters.clientes.nome.toLowerCase()))
      return false;

    if (filters.clientes.local && !c.local.toLowerCase().includes(filters.clientes.local.toLowerCase()))
      return false;

    if (filters.clientes.gastoMin && c.totalGasto < Number(filters.clientes.gastoMin))
      return false;

    if (filters.clientes.gastoMax && c.totalGasto > Number(filters.clientes.gastoMax))
      return false;

    if (filters.clientes.fidelidadeMin && c.pontosFidelidade < Number(filters.clientes.fidelidadeMin))
      return false;

    return true;
  });
}


function renderPaginatedList(
  container,
  { data, columns, pageSize = GLOBAL_PAGE_SIZE, onRowClick, rowClass }
) {
  const wrapper = document.createElement("div");
  wrapper.className = "table-wrapper";

  const table = document.createElement("table");
  const thead = document.createElement("thead");
  const tbody = document.createElement("tbody");

  // Cabeçalho
  const headRow = document.createElement("tr");
  columns.forEach((col) => {
    const th = document.createElement("th");
    th.textContent = col.header;
    headRow.appendChild(th);
  });
  thead.appendChild(headRow);

  table.appendChild(thead);
  table.appendChild(tbody);

  const paginationBar = document.createElement("div");
  paginationBar.className = "pagination";

  wrapper.appendChild(table);
  wrapper.appendChild(paginationBar);

  container.appendChild(wrapper);

  let currentPage = 1;
  const totalPages = Math.max(1, Math.ceil(data.length / pageSize));

  function renderPage() {
    tbody.innerHTML = "";

    if (data.length === 0) {
      const emptyRow = document.createElement("tr");
      const td = document.createElement("td");
      td.colSpan = columns.length;
      td.textContent = "Nenhum registro encontrado.";
      td.style.textAlign = "center";
      td.style.padding = "16px";
      emptyRow.appendChild(td);
      tbody.appendChild(emptyRow);
    } else {
      const start = (currentPage - 1) * pageSize;
      const end = start + pageSize;
      const pageItems = data.slice(start, end);

      pageItems.forEach((item) => {
        const tr = document.createElement("tr");

        if (rowClass) {
          const cls = rowClass(item);
          if (cls) tr.classList.add(cls);
        }

        tr.onclick = () => {
          if (onRowClick) onRowClick(item);
        };

        columns.forEach((col) => {
          const td = document.createElement("td");
          if (col.className) td.className = col.className;

          const cellContent = col.renderCell(item);
          if (cellContent instanceof Node) {
            td.appendChild(cellContent);
          } else {
            td.innerHTML = cellContent;
          }

          tr.appendChild(td);
        });

        tbody.appendChild(tr);
      });
    }

    // Paginação
    paginationBar.innerHTML = "";

    const info = document.createElement("div");
    info.className = "pagination-info";
    info.textContent = `Página ${currentPage} de ${totalPages}`;

    const buttons = document.createElement("div");
    buttons.className = "pagination-buttons";

    const btnPrev = document.createElement("button");
    btnPrev.className = "pagination-btn";
    btnPrev.textContent = "<";
    btnPrev.disabled = currentPage === 1;
    btnPrev.onclick = () => {
      if (currentPage > 1) {
        currentPage--;
        renderPage();
      }
    };
    buttons.appendChild(btnPrev);

    for (let p = 1; p <= totalPages; p++) {
      const btn = document.createElement("button");
      btn.className =
        "pagination-btn" + (p === currentPage ? " active" : "");
      btn.textContent = p;
      btn.onclick = () => {
        currentPage = p;
        renderPage();
      };
      buttons.appendChild(btn);
    }

    const btnNext = document.createElement("button");
    btnNext.className = "pagination-btn";
    btnNext.textContent = ">";
    btnNext.disabled = currentPage === totalPages;
    btnNext.onclick = () => {
      if (currentPage < totalPages) {
        currentPage++;
        renderPage();
      }
    };
    buttons.appendChild(btnNext);

    paginationBar.appendChild(info);
    paginationBar.appendChild(buttons);
  }

  renderPage();
}

/* ========== Carrinho ========== */

function addToCart(productId) {
  if (!cart.includes(productId)) {
    cart.push(productId);
  }
  // Apenas se estiver na tela de carrinho para refletir imediatamente
  if (state.role === "cliente" && state.clientePage === "carrinho") {
    render();
  }
}

function removeFromCart(productId) {
  cart = cart.filter((id) => id !== productId);
  render();
}

/* ========== Modal ========== */

function showModal(title, bodyHTML) {
  modalTitleEl.textContent = title;
  modalBodyEl.innerHTML = bodyHTML;
  modalOverlay.classList.remove("hidden");
}

function hideModal() {
  modalOverlay.classList.add("hidden");
}

function abrirModalFiltrosProdutos(onApply) {
  const tipos = ["", "Dispositivo", "Hardware", "Periférico"];

  const body = `
    <div class="modal-section">
      <label>Nome:</label>
      <input id="f-prod-nome" class="modal-input" value="${filters.produtos.nome}">
    </div>

    <div class="modal-section">
      <label>Tipo:</label>
      <select id="f-prod-tipo" class="modal-input">
        ${tipos.map(t => `<option value="${t}" ${filters.produtos.tipo===t?"selected":""}>${t || "(todos)"}</option>`).join("")}
      </select>
    </div>

    <div class="modal-section">
      <label>Preço mínimo:</label>
      <input id="f-prod-preco-min" type="number" class="modal-input" value="${filters.produtos.precoMin}">
    </div>

    <div class="modal-section">
      <label>Preço máximo:</label>
      <input id="f-prod-preco-max" type="number" class="modal-input" value="${filters.produtos.precoMax}">
    </div>

    <div class="modal-section">
      <label>Desconto mínimo (%):</label>
      <input id="f-prod-desc" type="number" class="modal-input" value="${filters.produtos.desconto}">
    </div>

    <button id="f-prod-apply" class="btn btn-primary" style="width:100%;margin-top:12px;">Aplicar</button>
    <button id="f-prod-clear" class="btn btn-danger" style="width:100%;margin-top:8px;">Limpar filtros</button>
  `;

  showModal("Filtros de Produtos", body);

  document.getElementById("f-prod-apply").onclick = () => {  // TODO: Adicionar rota para Back filtrar produtos
    filters.produtos.nome = document.getElementById("f-prod-nome").value;
    filters.produtos.tipo = document.getElementById("f-prod-tipo").value;
    filters.produtos.precoMin = document.getElementById("f-prod-preco-min").value;
    filters.produtos.precoMax = document.getElementById("f-prod-preco-max").value;
    filters.produtos.desconto = document.getElementById("f-prod-desc").value;

    hideModal();
    onApply();
  };

  document.getElementById("f-prod-clear").onclick = () => {
    filters.produtos = { nome:"", tipo:"", precoMin:"", precoMax:"", desconto:"" };
    hideModal();
    onApply();
  };
}

function abrirModalFiltrosClientes(onApply) {
  const body = `
    <div class="modal-section">
      <label>Nome:</label>
      <input id="f-cli-nome" class="modal-input" value="${filters.clientes.nome}">
    </div>

    <div class="modal-section">
      <label>Local (cidade, estado ou país):</label>
      <input id="f-cli-local" class="modal-input" value="${filters.clientes.local}">
    </div>

    <div class="modal-section">
      <label>Total gasto mínimo:</label>
      <input id="f-cli-gasto-min" type="number" class="modal-input" value="${filters.clientes.gastoMin}">
    </div>

    <div class="modal-section">
      <label>Total gasto máximo:</label>
      <input id="f-cli-gasto-max" type="number" class="modal-input" value="${filters.clientes.gastoMax}">
    </div>

    <div class="modal-section">
      <label>Pontuação fidelidade mínima:</label>
      <input id="f-cli-fid-min" type="number" class="modal-input" value="${filters.clientes.fidelidadeMin}">
    </div>

    <button id="f-cli-apply" class="btn btn-primary" style="width:100%;margin-top:12px;">Aplicar</button>
    <button id="f-cli-clear" class="btn btn-danger" style="width:100%;margin-top:8px;">Limpar filtros</button>
  `;

  showModal("Filtros de Clientes", body);

  document.getElementById("f-cli-apply").onclick = () => {
    filters.clientes.nome = document.getElementById("f-cli-nome").value;
    filters.clientes.local = document.getElementById("f-cli-local").value;
    filters.clientes.gastoMin = document.getElementById("f-cli-gasto-min").value;
    filters.clientes.gastoMax = document.getElementById("f-cli-gasto-max").value;
    filters.clientes.fidelidadeMin = document.getElementById("f-cli-fid-min").value;

    hideModal();
    onApply();
  };

  document.getElementById("f-cli-clear").onclick = () => {
    filters.clientes = { nome:"", local:"", gastoMin:"", gastoMax:"", fidelidadeMin:"" };
    hideModal();
    onApply();
  };
}



/* Específicos */

function showProductModal(p) {
  const desc = `
    <p><span class="label">Nome:</span> ${p.nome}</p>
    <p><span class="label">Preço:</span> ${formatCurrency(p.preco)}</p>
    <p><span class="label">Desconto:</span> ${
      p.descontoPercent > 0 ? p.descontoPercent + "%" : "Nenhum"
    }</p>
    <p><span class="label">Pontos de fidelidade:</span> ${
      p.pontosFidelidade
    }</p>
    <p><span class="label">Estoque:</span> ${
      p.estoqueAtual
    } (mínimo: ${p.estoqueMinimo})</p>
    <p><span class="label">Descrição:</span> ${p.descricao}</p>
  `;
  showModal("Detalhes do produto", desc);
}

function showDiscountModal(d) {
  const status = d.ativo ? "Ativo" : "Inativo";
  const desc = `
    <p><span class="label">Nome:</span> ${d.nome}</p>
    <p><span class="label">Descrição:</span> ${d.descricao}</p>
    <p><span class="label">Percentual:</span> ${d.percentual}%</p>
    <p><span class="label">Status:</span> ${status}</p>
  `;
  showModal("Detalhes do desconto", desc);
}

function showClienteModal(c) {
  const desc = `
    <p><span class="label">Nome:</span> ${c.nome}</p>
    <p><span class="label">Local:</span> ${c.local}</p>
    <p><span class="label">Total gasto:</span> ${formatCurrency(
      c.totalGasto
    )}</p>
    <p><span class="label">Data de cadastro:</span> ${formatDate(
      c.dataCadastro
    )}</p>
    <p><span class="label">E-mail:</span> ${c.email}</p>
    <p><span class="label">Telefone:</span> ${c.telefone}</p>
  `;
  showModal("Detalhes do cliente", desc);
}

function showStatsModal(e) {
  const desc = `
    <p><span class="label">Métrica:</span> ${e.metrica}</p>
    <p><span class="label">Valor:</span> ${e.valor}</p>
  `;
  showModal("Detalhes da métrica", desc);
}

function showCheckoutModal(items) {
  if (items.length === 0) {
    alert("Seu carrinho está vazio!");
    return;
  }

  const total = items.reduce((acc, p) => acc + p.preco, 0);

  const body = `
    <p><strong>Total da compra:</strong> ${formatCurrency(total)}</p>

    <label>Forma de pagamento:</label>
    <select id="payment-method" class="modal-input">
      <option value="pix">PIX</option>
      <option value="debito">Cartão de Débito</option>
      <option value="credito">Cartão de Crédito</option>
    </select>

    <div id="parcelas-container" style="margin-top: 12px; display: none;">
      <label>Número de parcelas:</label>
      <select id="parcelas" class="modal-input">
        <option value="1">1x</option>
        <option value="2">2x</option>
        <option value="3">3x</option>
        <option value="4">4x</option>
        <option value="5">5x</option>
        <option value="6">6x</option>
      </select>
    </div>

    <button id="pagar-btn" class="btn btn-primary" style="margin-top: 20px; width: 100%;">Pagar</button>
  `;

  showModal("Finalizar compra", body);

  // Mostrar parcelas somente se pagamento for crédito
  const paymentSelect = document.getElementById("payment-method");
  const parcelasDiv = document.getElementById("parcelas-container");

  paymentSelect.addEventListener("change", () => {
    parcelasDiv.style.display =
      paymentSelect.value === "credito" ? "block" : "none";
  });

  // Ação do botão pagar
  document.getElementById("pagar-btn").onclick = () => {
    // Fecha modal
    hideModal();

    // Esvazia carrinho
    cart = [];

    // Volta para página da loja
    state.clientePage = "loja";
    render();

    // Notificação ao usuário
    alert("A compra foi realizada com sucesso!");
  };
}
