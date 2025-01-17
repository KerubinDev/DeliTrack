let map = null;
let currentPosition = null;

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
    // Solicitar permissão de localização
    if ('geolocation' in navigator) {
        navigator.geolocation.watchPosition(
            position => {
                currentPosition = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude
                };
                atualizarPosicao();
            },
            error => console.error('Erro de localização:', error),
            { enableHighAccuracy: true }
        );
    }

    // Inicializar temporizadores
    iniciarTemporizadores();
    
    // Atualização periódica
    setInterval(atualizarInterface, 30000);
});

// Gerenciamento de Status
document.getElementById('statusToggle').addEventListener('change', function(e) {
    atualizarStatusEntregador(this.checked);
});

function atualizarStatusEntregador(disponivel) {
    fetch('/api/entregador/status', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ disponivel })
    })
    .then(response => response.json())
    .then(data => {
        if (!data.success) {
            // Reverter toggle se falhar
            document.getElementById('statusToggle').checked = !disponivel;
        }
    });
}

// Gerenciamento de Entregas
function aceitarEntrega(pedidoId) {
    fetch(`/api/entregas/${pedidoId}/aceitar`, {
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

function iniciarRota(entregaId) {
    if (!currentPosition) {
        alert('Aguardando localização...');
        return;
    }

    fetch(`/api/entregas/${entregaId}/iniciar-rota`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            latitude: currentPosition.lat,
            longitude: currentPosition.lng
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            atualizarInterface();
        }
    });
}

function confirmarEntrega(entregaId) {
    fetch(`/api/entregas/${entregaId}/confirmar`, {
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

// Mapa e Navegação
function mostrarMapa(lat, lng) {
    const modal = document.getElementById('mapaModal');
    modal.style.display = 'block';

    if (!map) {
        map = L.map('mapa').setView([lat, lng], 15);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
    } else {
        map.setView([lat, lng], 15);
    }

    if (currentPosition) {
        calcularRota(currentPosition, { lat, lng });
    }
}

function calcularRota(origem, destino) {
    // Usando OSRM para cálculo de rota
    const url = `https://router.project-osrm.org/route/v1/driving/` +
                `${origem.lng},${origem.lat};${destino.lng},${destino.lat}` +
                `?overview=full&geometries=geojson`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.routes && data.routes[0]) {
                const rota = data.routes[0];
                
                // Desenhar rota no mapa
                if (map.currentRoute) {
                    map.removeLayer(map.currentRoute);
                }
                
                map.currentRoute = L.geoJSON(rota.geometry).addTo(map);
                map.fitBounds(map.currentRoute.getBounds());

                // Atualizar informações
                document.getElementById('distancia').textContent = 
                    `${(rota.distance / 1000).toFixed(1)} km`;
                document.getElementById('tempo').textContent = 
                    `${Math.round(rota.duration / 60)} min`;
            }
        });
}

function navegarAte(lat, lng) {
    // Abrir no aplicativo de navegação nativo
    if (currentPosition) {
        const url = `https://www.google.com/maps/dir/?api=1` +
                   `&origin=${currentPosition.lat},${currentPosition.lng}` +
                   `&destination=${lat},${lng}`;
        window.open(url, '_blank');
    }
}

// Utilidades
function iniciarTemporizadores() {
    document.querySelectorAll('.tempo-espera').forEach(elemento => {
        const tempo = parseInt(elemento.dataset.tempo);
        atualizarTempo(elemento, tempo);
        
        setInterval(() => {
            atualizarTempo(elemento, tempo);
        }, 60000);
    });
}

function atualizarTempo(elemento, tempoInicial) {
    const agora = new Date();
    const diferenca = Math.floor((agora - new Date(tempoInicial)) / 1000 / 60);
    elemento.textContent = `${diferenca} min`;
}

function atualizarInterface() {
    fetch('/api/entregas/status')
        .then(response => response.json())
        .then(data => {
            atualizarListaEntregas('pedidosProntos', data.prontos);
            atualizarListaEntregas('entregasAndamento', data.andamento);
        });
}

function fecharModal() {
    document.getElementById('mapaModal').style.display = 'none';
} 