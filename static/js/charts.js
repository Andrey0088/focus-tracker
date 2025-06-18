// static/js/charts.js

document.addEventListener('DOMContentLoaded', function() {

    // Cores e estilos base do CSS
    const primaryColor = getComputedStyle(document.documentElement).getPropertyValue('--link-color').trim();
    const headerColor = getComputedStyle(document.documentElement).getPropertyValue('--header-color').trim();
    const textColor = getComputedStyle(document.documentElement).getPropertyValue('--text-color').trim();
    const borderColor = getComputedStyle(document.documentElement).getPropertyValue('--border-color').trim();
    
    const chartBackgrounds = [
        'rgba(255, 99, 132, 0.7)', 'rgba(54, 162, 235, 0.7)', 'rgba(255, 206, 86, 0.7)',
        'rgba(75, 192, 192, 0.7)', 'rgba(153, 102, 255, 0.7)', 'rgba(255, 159, 64, 0.7)',
        'rgba(199, 199, 199, 0.7)', 'rgba(83, 102, 255, 0.7)', 'rgba(40, 180, 99, 0.7)',
        'rgba(231, 76, 60, 0.7)'
    ];
    const chartBorders = [
        'rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)', 'rgba(255, 206, 86, 1)',
        'rgba(75, 192, 192, 1)', 'rgba(153, 102, 255, 1)', 'rgba(255, 159, 64, 1)',
        'rgba(199, 199, 199, 1)', 'rgba(83, 102, 255, 1)', 'rgba(40, 180, 99, 1)',
        'rgba(231, 76, 60, 1)'
    ];


    // Função genérica para criar gráficos (sempre lida com dados que podem vir da API)
    function createChart(chartId, type, labels, data, titleText, customOptions = {}) {
        const ctx = document.getElementById(chartId);
        if (!ctx) {
            console.error(`Elemento canvas com ID '${chartId}' não encontrado.`);
            return;
        }

        // Verifica se há dados significativos para plotar o gráfico
        const hasMeaningfulData = data.some(val => val > 0) || (labels.length > 0 && data.length > 0 && (type === 'bar' || type === 'pie'));
        
        if (!hasMeaningfulData) {
            // Se não houver dados, exibe uma mensagem no contêiner pai
            if (ctx.parentElement) {
                ctx.parentElement.innerHTML = '<p class="empty-chart-message-inner">Dados insuficientes para este gráfico.</p>';
            }
            return; // Sai da função
        }

        try {
            const defaultOptions = {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { position: 'top', labels: { color: textColor } },
                    title: { display: true, text: titleText, color: headerColor, font: { size: 18 } }
                },
                scales: {}, // Padrão vazio, será mesclado
                tooltips: {
                    callbacks: {
                        label: function(tooltipItem, chartData) {
                            let label = chartData.datasets[tooltipItem.datasetIndex].label || '';
                            if (label) { label += ': '; }
                            // Formatação específica para duração
                            if (chartId === 'dailyStudyChart' || chartId === 'analyticsWeekdayChart') {
                                const minutes = tooltipItem.raw;
                                const hours = Math.floor(minutes / 60);
                                const remainingMinutes = minutes % 60;
                                if (hours > 0) { return label + `${hours}h ${remainingMinutes}min`; }
                                return label + `${remainingMinutes}min`;
                            }
                            // Formatação para qualidade (arredonda para 1 decimal)
                            if (chartId === 'analyticsQualityChart') {
                                return `Média: ${tooltipItem.raw.toFixed(1)}`;
                            }
                            return label + tooltipItem.raw; // Padrão para outros gráficos
                        }
                    }
                }
            };

            const options = Chart.helpers.merge(defaultOptions, customOptions.chartOptions || {});

            const defaultDataset = {
                label: titleText,
                data: data,
                backgroundColor: chartBackgrounds,
                borderColor: chartBorders,
                borderWidth: 1
            };
            
            const dataset = Chart.helpers.merge(defaultDataset, customOptions.datasetOptions || {});

            new Chart(ctx, {
                type: type,
                data: {
                    labels: labels,
                    datasets: [dataset]
                },
                options: options
            });
        } catch (error) {
            console.error(`Erro ao criar gráfico ${chartId}:`, error);
            if (ctx.parentElement) {
                ctx.parentElement.innerHTML = `<p class="error-message">Erro ao carregar gráfico: ${error.message}</p>`;
            }
        }
    }

    // --- GRÁFICOS DA PÁGINA INICIAL (INDEX.HTML) ---
    // Estes ainda pegam dados dos atributos data-* porque são simples e já funcionavam.
    const subjectChartElement = document.getElementById('subjectStudyChart');
    if (subjectChartElement) {
        const subjectLabelsRaw = subjectChartElement.dataset.labels;
        const subjectDataRaw = subjectChartElement.dataset.data;
        const subjectLabels = subjectLabelsRaw ? JSON.parse(subjectLabelsRaw) : [];
        const subjectData = subjectDataRaw ? JSON.parse(subjectDataRaw) : [];
        createChart('subjectStudyChart', 'pie', subjectLabels, subjectData, 'Distribuição de Tempo de Estudo por Matéria', {
            datasetOptions: { backgroundColor: chartBackgrounds, borderColor: borderColor, borderWidth: 1 },
            chartOptions: { plugins: { legend: { position: 'top' } } }
        });
    }

    const dailyChartElement = document.getElementById('dailyStudyChart');
    if (dailyChartElement) {
        const dailyLabelsRaw = dailyChartElement.dataset.labels;
        const dailyDataRaw = dailyChartElement.dataset.data;
        const dailyLabels = dailyLabelsRaw ? JSON.parse(dailyLabelsRaw) : [];
        const dailyData = dailyDataRaw ? JSON.parse(dailyDataRaw) : [];
        createChart('dailyStudyChart', 'line', dailyLabels, dailyData, 'Tempo de Estudo nos Últimos 30 Dias', {
            datasetOptions: { backgroundColor: 'rgba(0, 188, 212, 0.5)', borderColor: primaryColor, borderWidth: 2, fill: true, tension: 0.3 },
            chartOptions: { plugins: { legend: { display: false } }, scales: { x: { ticks: { color: textColor }, grid: { color: borderColor } }, y: { beginAtZero: true, ticks: { color: textColor }, grid: { color: borderColor } } } }
        });
    }


    // --- GRÁFICOS DA PÁGINA ANALYTICS (analytics.html) ---
    // Estes agora buscarão dados do endpoint API
    if (document.getElementById('analyticsChartsSection')) { // Verifica se estamos na página de analytics
        fetch('/api/analytics_data')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Erro HTTP: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // Gráfico de Qualidade Média por Matéria
                createChart('analyticsQualityChart', 'bar', data.quality.labels, data.quality.data, 'Qualidade Média de Estudo por Matéria', {
                    datasetOptions: { backgroundColor: 'rgba(255, 159, 64, 0.7)', borderColor: 'rgba(255, 159, 64, 1)', borderWidth: 1 },
                    chartOptions: { scales: { x: { ticks: { color: textColor }, grid: { color: borderColor } }, y: { beginAtZero: true, max: 5, ticks: { color: textColor, stepSize: 1 }, grid: { color: borderColor } } } }
                });

                // Gráfico de Tempo de Estudo por Dia da Semana
                createChart('analyticsWeekdayChart', 'bar', data.weekday.labels, data.weekday.data, 'Tempo de Estudo por Dia da Semana', {
                    datasetOptions: { backgroundColor: 'rgba(75, 192, 192, 0.7)', borderColor: 'rgba(75, 192, 192, 1)', borderWidth: 1 },
                    chartOptions: { scales: { x: { ticks: { color: textColor }, grid: { color: borderColor } }, y: { beginAtZero: true, ticks: { color: textColor }, grid: { color: borderColor } } } }
                });

                // Gráfico de Contagem de Sessões por Matéria
                createChart('analyticsSessionsChart', 'bar', data.sessions.labels, data.sessions.data, 'Contagem de Sessões por Matéria', {
                    datasetOptions: { backgroundColor: 'rgba(153, 102, 255, 0.7)', borderColor: 'rgba(153, 102, 255, 1)', borderWidth: 1 },
                    chartOptions: { scales: { x: { ticks: { color: textColor }, grid: { color: borderColor } }, y: { beginAtZero: true, ticks: { color: textColor, stepSize: 1 }, grid: { color: borderColor } } } }
                });
            })
            .catch(error => {
                console.error("Erro ao buscar dados da API para Analytics:", error);
                // Exibe uma mensagem de erro geral se a API não puder ser acessada
                const analyticsSection = document.getElementById('analyticsChartsSection');
                if (analyticsSection) {
                    analyticsSection.innerHTML = '<p class="error-message">Não foi possível carregar os dados de análise. Verifique sua conexão ou tente novamente mais tarde.</p>';
                }
            });
    }
});