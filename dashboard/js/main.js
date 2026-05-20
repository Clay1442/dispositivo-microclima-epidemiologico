
// Estado global
const state = {
  historico: { temperatura: [], umidade: [], pressao: [], luminosidade: [], labels: [] },
  logs: [],
  graficoAtivo: 'temperatura',
  chart: null,
  intervalo: null,
  conectado: false
};

// Cores por campo
const cores = {
  temperatura: '#ff6b6b',
  umidade: '#4ecdc4',
  pressao: '#a78bfa',
  luminosidade: '#fbbf24'
};

// Cores por risco
const coresRisco = {
  // Valores do banco atual
  'CRÍTICO':       '#ff4444',
  'ALERTA':        '#ff8800',
  'NORMAL':        '#00cc6a',
  // Valores do mock/ESP32
  'RISCO MAXIMO':  '#ff4444',
  'RISCO ALTO':    '#ff8800',
  'RISCO MODERADO':'#ffb800',
  'RISCO BAIXO':   '#00cc6a',
  'RISCO MINIMO':  '#4ecdc4',
  'INDETERMINADO': '#6a9080'
};

const iconsRisco = {
  // Valores do banco atual
  'CRÍTICO':       '⚠',
  'ALERTA':        '▲',
  'NORMAL':        '●',
  // Valores do mock/ESP32
  'RISCO MAXIMO':  '⚠',
  'RISCO ALTO':    '▲',
  'RISCO MODERADO':'◆',
  'RISCO BAIXO':   '●',
  'RISCO MINIMO':  '○',
  'INDETERMINADO': '⬡'
};

// Inicializa gráfico
function initChart() {
  const ctx = document.getElementById('chart').getContext('2d');
  state.chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        label: 'Temperatura',
        data: [],
        borderColor: cores.temperatura,
        backgroundColor: cores.temperatura + '15',
        borderWidth: 1.5,
        pointRadius: 0,
        tension: 0.4,
        fill: true
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { intersect: false, mode: 'index' },
      plugins: { legend: { display: false }, tooltip: {
        backgroundColor: '#111714',
        borderColor: '#1e2b24',
        borderWidth: 1,
        titleColor: '#6a9080',
        bodyColor: '#c8ddd3',
        titleFont: { family: 'Space Mono', size: 10 },
        bodyFont: { family: 'Space Mono', size: 11 }
      }},
      scales: {
        x: {
          grid: { color: '#1e2b24' },
          ticks: { color: '#3a5045', font: { family: 'Space Mono', size: 9 }, maxTicksLimit: 6 }
        },
        y: {
          grid: { color: '#1e2b24' },
          ticks: { color: '#3a5045', font: { family: 'Space Mono', size: 9 } }
        }
      }
    }
  });
}

function trocarGrafico(campo, btn) {
  state.graficoAtivo = campo;
  document.querySelectorAll('.chart-tab').forEach(t => t.classList.remove('active'));
  btn.classList.add('active');
  atualizarGrafico();
}

function atualizarGrafico() {
  const campo = state.graficoAtivo;
  const dados = state.historico[campo];
  state.chart.data.labels = state.historico.labels.slice(-60);
  state.chart.data.datasets[0].data = dados.slice(-60);
  state.chart.data.datasets[0].borderColor = cores[campo];
  state.chart.data.datasets[0].backgroundColor = cores[campo] + '15';
  state.chart.data.datasets[0].label = campo;
  state.chart.update('none');
}

function atualizarUI(dado) {
  // Métricas
  document.getElementById('val-temp').innerHTML  = `${dado.temperatura.toFixed(1)}<span class="metric-unit">°C</span>`;
  document.getElementById('val-umid').innerHTML  = `${dado.umidade.toFixed(1)}<span class="metric-unit">%</span>`;
  document.getElementById('val-press').innerHTML = `${dado.pressao.toFixed(0)}<span class="metric-unit" style="font-size:10px">hPa</span>`;
  document.getElementById('val-lux').innerHTML   = `${dado.luminosidade.toFixed(0)}<span class="metric-unit" style="font-size:10px">lx</span>`;

  // Risco
  const status = dado.status_risco || 'INDETERMINADO';
  const cor = coresRisco[status] || '#6a9080';
  document.getElementById('risk-value').textContent = status;
  document.getElementById('risk-value').style.color = cor;
  document.getElementById('risk-desc').textContent  = dado.descricao || '';
  document.getElementById('risk-icon').textContent  = iconsRisco[status] || '⬡';
  document.getElementById('risk-banner').style.setProperty('--risk-color', cor);

  // Histórico
  const agora = new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  state.historico.labels.push(agora);
  state.historico.temperatura.push(dado.temperatura);
  state.historico.umidade.push(dado.umidade);
  state.historico.pressao.push(dado.pressao);
  state.historico.luminosidade.push(dado.luminosidade);

  // Limita histórico a 120 pontos
  Object.keys(state.historico).forEach(k => {
    if (state.historico[k].length > 120) state.historico[k].shift();
  });

  atualizarGrafico();

  // Log
  adicionarLog(agora, status, dado, cor);

  // Timestamp
  document.getElementById('last-update').textContent = `Última leitura: ${agora}`;
}

function adicionarLog(hora, status, dado, cor) {
  state.logs.unshift({ hora, status, dado, cor });
  if (state.logs.length > 50) state.logs.pop();

  const lista = document.getElementById('log-list');
  const entry = document.createElement('div');
  entry.className = 'log-entry';
  entry.style.setProperty('--entry-color', cor);
  entry.innerHTML = `
    <span class="log-time">${hora}</span>
    <span class="log-status">${status}</span>
    <span class="log-data">T:${dado.temperatura.toFixed(1)}°C · U:${dado.umidade.toFixed(1)}% · P:${dado.pressao.toFixed(0)}hPa · L:${dado.luminosidade.toFixed(0)}lx</span>
  `;

  if (lista.querySelector('.connecting-msg') || lista.querySelector('.no-data')) {
    lista.innerHTML = '';
  }
  lista.insertBefore(entry, lista.firstChild);
  if (lista.children.length > 20) lista.removeChild(lista.lastChild);

  document.getElementById('log-count').textContent = state.logs.length;
}

// Busca dados reais do InfluxDB via API Flux
async function buscarDadosInflux() {
  const cfg    = window.SAVA_CONFIG || {};
  const url    = cfg.influxUrl;
  const token  = cfg.influxToken;
  const bucket = cfg.influxBucket;
  const org    = encodeURIComponent(cfg.influxOrg);

  if (!url || !token) {
    console.warn('SAVA_CONFIG não carregado — verifique se o container está rodando');
    return;
  }

  const query = `
from(bucket: "${bucket}")
  |> range(start: -30d)
  |> filter(fn: (r) => r._measurement == "clima")
  |> last()
  |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
`;

  try {
    const res = await fetch(`${url}/api/v2/query?org=${org}`, {
      method: 'POST',
      headers: {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/vnd.flux',
        'Accept': 'application/csv'
      },
      body: query
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const csv  = await res.text();
    const dado = parsearCSVInflux(csv);
    if (dado) {
      setConectado(true);
      atualizarUI(dado);
    }
  } catch(e) {
    setConectado(false);
    console.warn('Erro ao buscar InfluxDB:', e.message);
  }
}

function parsearCSVInflux(csv) {
  try {
    const linhas = csv.trim().split('\n').filter(l => l && !l.startsWith('#'));
    if (linhas.length < 2) return null;
    const headers = linhas[0].split(',').map(h => h.trim());
    const valores = linhas[linhas.length - 1].split(',');

    const obj = {};
    headers.forEach((h, i) => { obj[h] = valores[i]?.trim(); });

    return {
      temperatura:  parseFloat(obj.temperatura)  || 0,
      umidade:      parseFloat(obj.umidade)       || 0,
      pressao:      parseFloat(obj.pressao)       || 0,
      luminosidade: parseFloat(obj.luminosidade)  || 0,
      status_risco: obj.status_risco || 'INDETERMINADO',
      descricao:    obj.descricao    || ''
    };
  } catch(e) { return null; }
}

function setConectado(status) {
  state.conectado = status;
  const dot   = document.getElementById('conn-dot');
  const label = document.getElementById('conn-label');
  if (status) {
    dot.classList.remove('offline');
    label.textContent = 'ESP32 ONLINE';
  } else {
    dot.classList.add('offline');
    label.textContent = 'SEM SINAL';
  }
}

function conectar() {
  if (state.intervalo) clearInterval(state.intervalo);
  buscarDadosInflux();
  state.intervalo = setInterval(buscarDadosInflux, 5000);
}

// Modo demo com dados mock
function usarDadosMock() {
  if (state.intervalo) clearInterval(state.intervalo);
  setConectado(true);

  const riscos = ['RISCO MAXIMO', 'RISCO ALTO', 'RISCO MODERADO', 'RISCO BAIXO', 'RISCO MINIMO'];
  const descs  = {
    'RISCO MAXIMO':  'Condições PERFEITAS PARA PROLIFERAÇÃO',
    'RISCO ALTO':    'Ambiente ideal para proliferação',
    'RISCO MODERADO':'Condições favoráveis',
    'RISCO BAIXO':   'Temperatura boa, mas umidade limitante',
    'RISCO MINIMO':  'Condições adversas ao mosquito'
  };

  let i = 0;
  function gerarMock() {
    const base_temp = 26 + Math.sin(i * 0.1) * 3 + (Math.random() - 0.5);
    const base_umid = 72 + Math.sin(i * 0.08) * 10 + (Math.random() - 0.5) * 2;
    const status = riscos[Math.floor(Math.random() * riscos.length)];
    const dado = {
      temperatura:  parseFloat(base_temp.toFixed(1)),
      umidade:      parseFloat(base_umid.toFixed(1)),
      pressao:      parseFloat((1013 + Math.sin(i * 0.05) * 3).toFixed(1)),
      luminosidade: parseFloat((150 + Math.random() * 400).toFixed(0)),
      status_risco: status,
      descricao:    descs[status]
    };
    atualizarUI(dado);
    i++;
  }

  gerarMock();
  state.intervalo = setInterval(gerarMock, 3000);
}

// Init
initChart();

// Tenta conectar automaticamente ao carregar
setTimeout(conectar, 500);
