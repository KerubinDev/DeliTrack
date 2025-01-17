// Configurações globais do Chart.js
Chart.defaults.font.family = "'Poppins', sans-serif";
Chart.defaults.color = '#666';
Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(0, 0, 0, 0.8)';

// Variáveis globais
let vendasChart, produtosChart, mapaCalor;
let dadosAtuais = {};
let periodoAtual = 'hoje';
let intervaloAtualizacao;

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    inicializarGraficos();
    inicializarMapa();
    configurarEventListeners();
    carregarDados('hoje');
    
    // Atualização automática
    if (localStorage.getItem('atualizacaoAutomatica') === 'true') {
        iniciarAtualizacaoAutomatica();
    }
});

// Configuração de eventos
function configurarEventListeners() {
    // Botões de período
    document.querySelectorAll('.btn-periodo').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.btn-periodo').forEach(b => 
                b.classList.remove('active'));
            e.target.classList.add('active');
            periodoAtual = e.target.dataset.periodo;
            carregarDados(periodoAtual);
        });
    });

    // Configurações
    document.getElementById('darkMode').addEventListener('change', alternarTema);
    document.getElementById('atualizacaoAutomatica')
        .addEventListener('change', alternarAtualizacaoAutomatica);
}

// Carregamento de dados
async function carregarDados(periodo) {
    try {
        const response = await fetch(`/api/dashboard/metricas?periodo=${periodo}`);
        dadosAtuais = await response.json();
        
        atualizarMetricas(dadosAtuais.metricas);
        atualizarGraficos(dadosAtuais.graficos);
        atualizarMapa(dadosAtuais.entregas);
        atualizarTabelaDesempenho(dadosAtuais.desempenho);
    } catch (error) {
        console.error('Erro ao carregar dados:', error);
        mostrarNotificacao('Erro ao carregar dados', 'error');
    }
}

// Inicialização dos gráficos
function inicializarGraficos() {
    // Gráfico de Vendas
    const ctxVendas = document.getElementById('graficoVendas').getContext('2d');
    vendasChart = new Chart(ctxVendas, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Vendas',
                data: [],
                borderColor: '#4caf50',
                backgroundColor: 'rgba(76, 175, 80, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grid: {
                        drawBorder: false
                    }
                },
                x: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });

    // Gráfico de Produtos
    const ctxProdutos = document.getElementById('graficoProdutos').getContext('2d');
    produtosChart = new Chart(ctxProdutos, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [
                    '#4caf50',
                    '#2196f3',
                    '#ff9800',
                    '#f44336',
                    '#9c27b0'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    });
}

// Inicialização do mapa de calor
function inicializarMapa() {
    const mapa = L.map('mapaCalor').setView([-23.5505, -46.6333], 12);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(mapa);
    
    mapaCalor = L.heatLayer([], {
        radius: 25,
        blur: 15,
        maxZoom: 10
    }).addTo(mapa);
}

// Atualização das visualizações
function atualizarMetricas(metricas) {
    Object.entries(metricas).forEach(([chave, valor]) => {
        const elemento = document.querySelector(`.metrica-card.${chave} .valor`);
        if (elemento) {
            if (typeof valor === 'number') {
                elemento.textContent = valor.toLocaleString('pt-BR', {
                    style: 'currency',
                    currency: 'BRL'
                });
            } else {
                elemento.textContent = valor;
            }
        }
    });
}

function atualizarGraficos(dados) {
    // Atualiza gráfico de vendas
    vendasChart.data.labels = dados.vendas.labels;
    vendasChart.data.datasets[0].data = dados.vendas.valores;
    vendasChart.update();

    // Atualiza gráfico de produtos
    produtosChart.data.labels = dados.produtos.labels;
    produtosChart.data.datasets[0].data = dados.produtos.valores;
    produtosChart.update();
}

function atualizarMapa(entregas) {
    const pontos = entregas.map(e => [e.lat, e.lng, e.intensidade]);
    mapaCalor.setLatLngs(pontos);
}

// Exportação de dados
function exportarRelatorio() {
    const dados = {
        periodo: periodoAtual,
        metricas: dadosAtuais.metricas,
        graficos: dadosAtuais.graficos,
        desempenho: dadosAtuais.desempenho
    };

    const blob = new Blob([JSON.stringify(dados, null, 2)], 
        { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `relatorio_${periodoAtual}_${new Date().toISOString()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Configurações e temas
function alternarTema(e) {
    const isDark = e.target.checked;
    document.body.classList.toggle('dark-mode', isDark);
    localStorage.setItem('darkMode', isDark);
    
    // Atualiza cores dos gráficos
    atualizarTemasGraficos(isDark);
}

function alternarAtualizacaoAutomatica(e) {
    const isAuto = e.target.checked;
    localStorage.setItem('atualizacaoAutomatica', isAuto);
    
    if (isAuto) {
        iniciarAtualizacaoAutomatica();
    } else {
        clearInterval(intervaloAtualizacao);
    }
}

function iniciarAtualizacaoAutomatica() {
    intervaloAtualizacao = setInterval(() => {
        carregarDados(periodoAtual);
    }, 300000); // Atualiza a cada 5 minutos
}

// Utilitários
function mostrarNotificacao(mensagem, tipo) {
    const notification = document.createElement('div');
    notification.className = `notification ${tipo}`;
    notification.textContent = mensagem;
    
    document.body.appendChild(notification);
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

function formatarMoeda(valor) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(valor);
}

// Manipulação da tabela
function ordenarTabela(coluna) {
    const tabela = document.querySelector('table');
    const linhas = Array.from(tabela.querySelectorAll('tbody tr'));
    const direcao = tabela.dataset.direcao === 'asc' ? -1 : 1;
    
    linhas.sort((a, b) => {
        const valorA = a.children[coluna].textContent;
        const valorB = b.children[coluna].textContent;
        return valorA.localeCompare(valorB) * direcao;
    });
    
    tabela.dataset.direcao = direcao === 1 ? 'asc' : 'desc';
    
    const tbody = tabela.querySelector('tbody');
    tbody.innerHTML = '';
    linhas.forEach(linha => tbody.appendChild(linha));
}

// Exportação de gráficos
function exportarGrafico(tipo) {
    const canvas = document.getElementById(`grafico${tipo.charAt(0).toUpperCase() + tipo.slice(1)}`);
    const url = canvas.toDataURL('image/png');
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `grafico_${tipo}_${new Date().toISOString()}.png`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
} 