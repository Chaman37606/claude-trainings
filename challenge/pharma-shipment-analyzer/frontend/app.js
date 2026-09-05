/**
 * Pharma Shipment Risk Analyzer - Frontend
 */

const API_BASE = 'http://localhost:8000/api';
let currentFileId = null;
let riskChart = null;

// Upload handling
document.getElementById('fileInput').addEventListener('change', handleFileSelect);

const uploadArea = document.getElementById('uploadArea');
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        // Validate file type
        if (!file.name.endsWith(('.xlsx', '.xls', '.csv'))) {
            showError('Invalid file format. Please upload an Excel file (.xlsx) or CSV.');
            return;
        }
        // Show loading status
        showUploadStatus('loading', `⏳ Processing ${file.name}...`);
        // Upload file directly
        uploadFileDirectly(file);
    }
});

async function uploadFileDirectly(file) {
    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        const data = await response.json();
        currentFileId = data.file_id;

        showUploadStatus('success', `✓ File processed successfully! Found ${data.stats.total_shipments} shipments.`);

        // Show dashboard
        setTimeout(() => {
            loadDashboard();
        }, 1000);

    } catch (error) {
        showError(`Upload Error: ${error.message}`);
    }
}

async function handleFileSelect() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];

    if (!file) return;

    // Validate file type
    if (!file.name.endsWith(('.xlsx', '.xls', '.csv'))) {
        showError('Invalid file format. Please upload an Excel file (.xlsx) or CSV.');
        return;
    }

    // Show loading status
    showUploadStatus('loading', `⏳ Processing ${file.name}...`);

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch(`${API_BASE}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Upload failed');
        }

        const data = await response.json();
        currentFileId = data.file_id;

        showUploadStatus('success', `✓ File processed successfully! Found ${data.stats.total_shipments} shipments.`);

        // Show dashboard
        setTimeout(() => {
            loadDashboard();
        }, 1000);

    } catch (error) {
        showError(`Upload Error: ${error.message}`);
    }
}

function showUploadStatus(type, message) {
    const statusDiv = document.getElementById('uploadStatus');
    statusDiv.className = `upload-status ${type}`;
    statusDiv.textContent = message;
    statusDiv.style.display = 'block';
}

async function fetchWithTimeout(url, options = {}, timeout = 10000) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
        const response = await fetch(url, { ...options, signal: controller.signal });
        clearTimeout(timeoutId);
        return response;
    } catch (error) {
        clearTimeout(timeoutId);
        throw error;
    }
}

async function loadDashboard() {
    try {
        // Hide upload section, show dashboard
        document.getElementById('uploadArea').style.opacity = '0.5';
        document.getElementById('uploadArea').style.pointerEvents = 'none';

        // Load statistics with timeout
        const statsResponse = await fetchWithTimeout(`${API_BASE}/stats/${currentFileId}`, {}, 10000);
        if (!statsResponse.ok) throw new Error(`HTTP ${statsResponse.status}`);
        const stats = await statsResponse.json();

        // Update metric cards
        document.getElementById('totalShipments').textContent = stats.total_shipments;
        document.getElementById('highRiskCount').textContent = stats.high_risk_count;
        document.getElementById('highRiskPercent').textContent = `(${stats.high_risk_percentage}%)`;
        document.getElementById('tempExcursions').textContent = stats.temp_excursions;
        document.getElementById('avgRiskScore').textContent = stats.average_risk_score;

        // Show dashboard section
        document.getElementById('dashboardSection').style.display = 'block';
        document.getElementById('errorSection').style.display = 'none';

        // Load chart data
        await loadChart(stats.risk_distribution);

        // Load top 5 risks
        await loadTopRisks();

        // Load recommendations
        await loadRecommendations();

        // Scroll to dashboard
        document.getElementById('dashboardSection').scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        showError(`Dashboard Error: ${error.message}`);
    }
}

async function loadChart(distribution) {
    try {
        const chartResponse = await fetchWithTimeout(`${API_BASE}/chart-data/${currentFileId}`);
        if (!chartResponse.ok) throw new Error(`HTTP ${chartResponse.status}`);
        const chartData = await chartResponse.json();

        const ctx = document.getElementById('riskChart').getContext('2d');

        if (riskChart) {
            riskChart.destroy();
        }

        riskChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: chartData.labels,
                datasets: [{
                    data: chartData.data,
                    backgroundColor: chartData.colors,
                    borderColor: 'white',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    },
                    tooltip: {
                        callbacks: {
                            label: (context) => {
                                const label = context.label || '';
                                const value = context.parsed;
                                const percentage = ((value / chartData.total) * 100).toFixed(1);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error loading chart:', error);
    }
}

async function loadTopRisks() {
    try {
        const response = await fetchWithTimeout(`${API_BASE}/risks/high/${currentFileId}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const risks = await response.json();

        const risksList = document.getElementById('topRisksList');
        risksList.innerHTML = '';

        risks.forEach((risk) => {
            const riskLevel = risk.risk_level.toLowerCase();
            const riskItem = document.createElement('div');
            riskItem.className = `risk-item ${riskLevel}`;

            riskItem.innerHTML = `
                <div class="risk-rank">#${risk.rank}</div>
                <div class="risk-details">
                    <div class="risk-id">${risk.shipment_id}</div>
                    <div class="risk-score">Risk Score: ${risk.risk_score}/100 (${risk.risk_level})</div>
                    <div class="risk-reason">🌡️ ${risk.temperature}°C | ${risk.reason}</div>
                </div>
            `;

            risksList.appendChild(riskItem);
        });

    } catch (error) {
        console.error('Error loading top risks:', error);
    }
}

async function loadRecommendations() {
    try {
        const response = await fetchWithTimeout(`${API_BASE}/recommendations/${currentFileId}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const recommendations = await response.json();

        const recBox = document.getElementById('recommendationBox');
        recBox.innerHTML = '';

        // Add recommendations
        const recContainer = document.createElement('div');
        if (recommendations.recommendations && recommendations.recommendations.length > 0) {
            recommendations.recommendations.forEach((rec) => {
                const recItem = document.createElement('div');
                recItem.className = 'recommendation-item';
                recItem.innerHTML = `
                    <div class="recommendation-text">✓ ${escapeHtml(rec)}</div>
                `;
                recContainer.appendChild(recItem);
            });
        }

        // Add compliance alerts
        if (recommendations.compliance_alerts && recommendations.compliance_alerts.length > 0) {
            const alertTitle = document.createElement('div');
            alertTitle.className = 'recommendation-title';
            alertTitle.textContent = '⚠️ Compliance Alerts';
            recContainer.appendChild(alertTitle);

            recommendations.compliance_alerts.forEach((alert) => {
                const alertItem = document.createElement('div');
                alertItem.className = 'compliance-alert';
                alertItem.textContent = '• ' + escapeHtml(alert);
                recContainer.appendChild(alertItem);
            });
        }

        recBox.appendChild(recContainer);

    } catch (error) {
        console.error('Error loading recommendations:', error);
        // Show fallback message
        const recBox = document.getElementById('recommendationBox');
        recBox.innerHTML = '<div class="recommendation-item"><div class="recommendation-text">Unable to load recommendations. Please try again.</div></div>';
    }
}

function showError(message) {
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorSection').style.display = 'block';
    document.getElementById('dashboardSection').style.display = 'none';
}

function uploadNew() {
    currentFileId = null;
    document.getElementById('uploadArea').style.opacity = '1';
    document.getElementById('uploadArea').style.pointerEvents = 'auto';
    document.getElementById('dashboardSection').style.display = 'none';
    document.getElementById('errorSection').style.display = 'none';
    document.getElementById('uploadStatus').style.display = 'none';
    document.getElementById('fileInput').value = '';
}

function exportData() {
    alert('Export feature coming soon! PDF/CSV export available in production.');
}
