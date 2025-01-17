// Atualização do relógio
function atualizarRelogio() {
    const agora = new Date();
    const relogio = document.getElementById('currentTime');
    relogio.textContent = agora.toLocaleTimeString();
}

setInterval(atualizarRelogio, 1000);

// Drag and Drop
function drag(ev) {
    ev.dataTransfer.setData("pedido_id", ev.target.dataset.id);
}

function allowDrop(ev) {
    ev.preventDefault();
}

function drop(ev) {
    ev.preventDefault();
    const pedidoId = ev.dataTransfer.getData("pedido_id");
    iniciarPreparo(pedidoId);
}

// Gerenciamento de Pedidos
function iniciarPreparo(pedidoId) {
    fetch(`/api/pedidos/${pedidoId}/iniciar`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            atualizarInterface();
        }
    });
}

function marcarPronto(pedidoId) {
    fetch(`/api/pedidos/${pedidoId}/pronto`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            atualizarInterface();
            notificarGarcom(pedidoId);
        }
    });
}

// Temporizadores
function iniciarTemporizadores() {
    document.querySelectorAll('.pedido-timer').forEach(timer => {
        const dataCriacao = new Date(timer.dataset.created);
        
        setInterval(() => {
            const agora = new Date();
            const diferenca = Math.floor((agora - dataCriacao) / 1000 / 60);
            timer.querySelector('.tempo-espera').textContent = 
                `${diferenca}:${String(Math.floor((agora - dataCriacao) / 1000 % 60)).padStart(2, '0')}`;
        }, 1000);
    });
}

// Atualização em tempo real
function atualizarInterface() {
    fetch('/api/pedidos/cozinha')
        .then(response => response.json())
        .then(data => {
            atualizarListaPedidos('listaPedidosAguardando', data.aguardando);
            atualizarListaPedidos('listaPedidosPreparando', data.preparando);
            atualizarListaPedidos('listaPedidosProntos', data.prontos);
            atualizarTimeline(data.timeline);
        });
}

function atualizarListaPedidos(containerId, pedidos) {
    const container = document.getElementById(containerId);
    // Implementação da atualização visual
}

// Notificações
function notificarGarcom(pedidoId) {
    if ('Notification' in window) {
        Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                new Notification('Pedido Pronto!', {
                    body: `O pedido #${pedidoId} está pronto para entrega`,
                    icon: '/static/img/logo.png'
                });
            }
        });
    }
}

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    iniciarTemporizadores();
    setInterval(atualizarInterface, 30000);
}); 