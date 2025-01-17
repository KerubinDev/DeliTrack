// Variáveis globais
let itensSelecionados = new Map();
let totalPedido = 0;

// Funções do Modal
function abrirModalNovoPedido() {
    document.getElementById('modalNovoPedido').style.display = 'block';
    limparFormulario();
}

function fecharModal() {
    document.getElementById('modalNovoPedido').style.display = 'none';
}

function limparFormulario() {
    document.getElementById('formNovoPedido').reset();
    itensSelecionados.clear();
    totalPedido = 0;
    atualizarResumoPedido();
}

// Gerenciamento de Produtos
function selecionarProduto(produtoId) {
    fetch(`/api/produto/${produtoId}`)
        .then(response => response.json())
        .then(produto => {
            if (itensSelecionados.has(produtoId)) {
                const item = itensSelecionados.get(produtoId);
                item.quantidade += 1;
            } else {
                itensSelecionados.set(produtoId, {
                    id: produtoId,
                    nome: produto.nome,
                    preco: produto.preco,
                    quantidade: 1
                });
            }
            atualizarResumoPedido();
        });
}

function atualizarResumoPedido() {
    const container = document.getElementById('itensSelecionados');
    container.innerHTML = '';
    totalPedido = 0;

    itensSelecionados.forEach(item => {
        const itemElement = document.createElement('div');
        itemElement.className = 'item-resumo';
        itemElement.innerHTML = `
            <div class="item-info">
                <span>${item.quantidade}x ${item.nome}</span>
                <span>R$ ${(item.preco * item.quantidade).toFixed(2)}</span>
            </div>
            <div class="item-acoes">
                <button onclick="ajustarQuantidade(${item.id}, -1)">-</button>
                <button onclick="ajustarQuantidade(${item.id}, 1)">+</button>
                <button onclick="removerItem(${item.id})">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        container.appendChild(itemElement);
        totalPedido += item.preco * item.quantidade;
    });

    document.getElementById('totalPedido').textContent = 
        `R$ ${totalPedido.toFixed(2)}`;
}

// Gerenciamento de Pedidos
document.getElementById('formNovoPedido').onsubmit = function(e) {
    e.preventDefault();
    
    const mesa = document.querySelector('input[name="mesa"]').value;
    const itens = Array.from(itensSelecionados.values()).map(item => ({
        produto_id: item.id,
        quantidade: item.quantidade
    }));

    fetch('/api/pedidos', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            mesa: mesa,
            itens: itens
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            fecharModal();
            window.location.reload();
        }
    });
};

// Atualização em tempo real
setInterval(() => {
    fetch('/api/pedidos/atualizacoes')
        .then(response => response.json())
        .then(atualizarPedidosView);
}, 30000);

function atualizarPedidosView(dados) {
    // Atualiza cada coluna de pedidos
    ['aguardando', 'preparando', 'prontos'].forEach(status => {
        const container = document.getElementById(status);
        if (dados[status]) {
            atualizarColunaPedidos(container, dados[status]);
        }
    });
}

// Funções de utilidade
function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
} 