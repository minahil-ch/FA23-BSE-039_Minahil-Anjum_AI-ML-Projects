/**
 * Chart.js visualization renderer
 */

function initCharts(data) {
    if (!data) return;

    renderBarChart('missingChart', data.missing_values);
    renderHeatmap('heatmapChart', data.correlation_heatmap);
    renderChartGrid('histogramContainer', data.histograms || [], 'histogram');
    renderChartGrid('barChartContainer', data.bar_charts || [], 'bar');
    renderChartGrid('pieChartContainer', data.pie_charts || [], 'pie');
}

function renderBarChart(canvasId, chartData) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !chartData) return;

    new Chart(canvas, {
        type: 'bar',
        data: {
            labels: chartData.labels || [],
            datasets: chartData.datasets || [],
        },
        options: {
            responsive: true,
            plugins: { title: { display: true, text: chartData.title || '' } },
            scales: { y: { beginAtZero: true } },
        },
    });
}

function renderHeatmap(canvasId, heatmapData) {
    const canvas = document.getElementById(canvasId);
    if (!canvas || !heatmapData || !heatmapData.matrix || !heatmapData.matrix.length) {
        if (canvas && heatmapData?.message) {
            canvas.parentElement.innerHTML = `<p class="text-muted text-center py-4">${heatmapData.message}</p>`;
        }
        return;
    }

    const labels = heatmapData.labels;
    const matrix = heatmapData.matrix;
    const flat = matrix.flat();
    const min = Math.min(...flat);
    const max = Math.max(...flat);

    const datasets = labels.map((label, i) => ({
        label,
        data: matrix[i],
        backgroundColor: matrix[i].map(v => correlationColor(v, min, max)),
    }));

    new Chart(canvas, {
        type: 'bar',
        data: { labels, datasets },
        options: {
            responsive: true,
            plugins: {
                title: { display: true, text: heatmapData.title || 'Correlation' },
                legend: { display: false },
            },
            scales: {
                x: { stacked: true },
                y: { stacked: true, display: false },
            },
        },
    });
}

function correlationColor(value, min, max) {
    const norm = max === min ? 0.5 : (value - min) / (max - min);
    const r = Math.round(norm < 0.5 ? 255 : 255 - (norm - 0.5) * 2 * 255);
    const g = Math.round(norm < 0.5 ? norm * 2 * 255 : 255 - (norm - 0.5) * 2 * 100);
    const b = Math.round(norm < 0.5 ? (0.5 - norm) * 2 * 255 : 100);
    return `rgba(${r}, ${g}, ${b}, 0.8)`;
}

function renderChartGrid(containerId, charts, type) {
    const container = document.getElementById(containerId);
    if (!container || !charts.length) return;

    charts.forEach((chartData, idx) => {
        const col = document.createElement('div');
        col.className = 'col-lg-6';
        col.innerHTML = `
            <div class="card border-0 shadow-sm">
                <div class="card-header bg-white">${chartData.title || ''}</div>
                <div class="card-body"><canvas id="${containerId}_${idx}" height="200"></canvas></div>
            </div>`;
        container.appendChild(col);

        const canvas = document.getElementById(`${containerId}_${idx}`);
        new Chart(canvas, {
            type: type === 'pie' ? 'pie' : 'bar',
            data: {
                labels: chartData.labels || [],
                datasets: chartData.datasets || [],
            },
            options: {
                responsive: true,
                plugins: { legend: { display: type === 'pie' } },
                scales: type !== 'pie' ? { y: { beginAtZero: true } } : {},
            },
        });
    });
}
