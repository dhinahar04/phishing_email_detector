// API Base URL
const API_BASE_URL = 'http://localhost:5001/api';

// Chart instances
let iocChart = null;
let timelineChart = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadDashboard();
});

// Section navigation
function showSection(section) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(s => {
        s.style.display = 'none';
    });

    // Remove active class from all menu items
    document.querySelectorAll('.list-group-item').forEach(item => {
        item.classList.remove('active');
    });

    // Show selected section
    document.getElementById(`${section}-section`).style.display = 'block';

    // Add active class to clicked menu item
    event.target.classList.add('active');

    // Load data for section
    if (section === 'dashboard') {
        loadDashboard();
    } else if (section === 'emails') {
        loadEmails();
    } else if (section === 'iocs') {
        loadIOCs();
    }
}

// Load dashboard data
async function loadDashboard() {
    try {
        // Load summary metrics
        const summaryResponse = await fetch(`${API_BASE_URL}/metrics/summary`);
        const summary = await summaryResponse.json();

        document.getElementById('total-emails').textContent = summary.total_emails;
        document.getElementById('phishing-count').textContent = summary.phishing_detected;
        document.getElementById('total-iocs').textContent = summary.total_iocs;
        document.getElementById('legitimate-count').textContent = summary.legitimate_emails;

        // Load IOC distribution
        const iocDistResponse = await fetch(`${API_BASE_URL}/metrics/ioc-distribution`);
        const iocDist = await iocDistResponse.json();
        renderIOCChart(iocDist);

        // Load timeline
        const timelineResponse = await fetch(`${API_BASE_URL}/metrics/timeline`);
        const timeline = await timelineResponse.json();
        renderTimelineChart(timeline);

    } catch (error) {
        console.error('Error loading dashboard:', error);
        showAlert('Error loading dashboard data', 'danger');
    }
}

// Render IOC distribution chart
function renderIOCChart(data) {
    const ctx = document.getElementById('ioc-chart').getContext('2d');

    // Destroy existing chart
    if (iocChart) {
        iocChart.destroy();
    }

    const labels = data.map(item => item.type.toUpperCase());
    const values = data.map(item => item.count);

    iocChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#FF6384',
                    '#36A2EB',
                    '#FFCE56',
                    '#4BC0C0',
                    '#9966FF',
                    '#FF9F40',
                    '#FF6384'
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    });
}

// Render timeline chart
function renderTimelineChart(data) {
    const ctx = document.getElementById('timeline-chart').getContext('2d');

    // Destroy existing chart
    if (timelineChart) {
        timelineChart.destroy();
    }

    const labels = data.map(item => item.date);
    const phishingData = data.map(item => item.phishing);
    const legitimateData = data.map(item => item.legitimate);

    timelineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Phishing',
                    data: phishingData,
                    borderColor: '#dc3545',
                    backgroundColor: 'rgba(220, 53, 69, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Legitimate',
                    data: legitimateData,
                    borderColor: '#28a745',
                    backgroundColor: 'rgba(40, 167, 69, 0.1)',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

// Upload email
async function uploadEmail() {
    const fileInput = document.getElementById('emailFile');
    const file = fileInput.files[0];

    if (!file) {
        showAlert('Please select a file', 'warning');
        return;
    }

    const formData = new FormData();
    formData.append('file', file);

    // Show progress bar
    document.getElementById('upload-progress').style.display = 'block';
    document.getElementById('upload-result').innerHTML = '';

    try {
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        // Hide progress bar
        document.getElementById('upload-progress').style.display = 'none';

        if (response.ok && result.success) {
            displayAnalysisResult(result);
            fileInput.value = '';
        } else {
            showAlert(`Upload failed: ${result.error}`, 'danger');
        }

    } catch (error) {
        document.getElementById('upload-progress').style.display = 'none';
        showAlert(`Error uploading file: ${error.message}`, 'danger');
    }
}

// Display detailed analysis result
function displayAnalysisResult(result) {
    const analysis = result.analysis;
    const isPhishing = analysis.is_phishing;

    // Determine alert type and icon
    const alertType = isPhishing ? 'danger' : 'success';
    const icon = isPhishing ? '⚠️' : '✅';
    const statusText = isPhishing ? 'PHISHING EMAIL DETECTED' : 'Legitimate Email';

    // Build IOC breakdown HTML
    let iocBreakdownHtml = '';
    if (analysis.total_iocs > 0) {
        iocBreakdownHtml = '<div class="mt-3"><h6>IOC Breakdown:</h6><ul class="list-group">';
        for (const [type, iocs] of Object.entries(analysis.ioc_breakdown)) {
            iocBreakdownHtml += `
                <li class="list-group-item d-flex justify-content-between align-items-center">
                    <strong>${type.toUpperCase()}</strong>
                    <span class="badge bg-primary rounded-pill">${iocs.length}</span>
                </li>
            `;
            // Show first 3 IOCs of each type
            iocs.slice(0, 3).forEach(ioc => {
                const severityBadge = getSeverityBadge(ioc.severity);
                iocBreakdownHtml += `
                    <li class="list-group-item ps-4">
                        <code style="font-size: 0.85em;">${ioc.value}</code> ${severityBadge}
                    </li>
                `;
            });
            if (iocs.length > 3) {
                iocBreakdownHtml += `
                    <li class="list-group-item ps-4 text-muted">
                        ... and ${iocs.length - 3} more
                    </li>
                `;
            }
        }
        iocBreakdownHtml += '</ul></div>';
    }

    // Build severity breakdown
    const severityHtml = `
        <div class="mt-3">
            <h6>Severity Distribution:</h6>
            <div class="row">
                <div class="col-4 text-center">
                    <span class="badge bg-success" style="font-size: 1.2em;">${analysis.severity_breakdown.low}</span>
                    <div><small>Low</small></div>
                </div>
                <div class="col-4 text-center">
                    <span class="badge bg-warning" style="font-size: 1.2em;">${analysis.severity_breakdown.medium}</span>
                    <div><small>Medium</small></div>
                </div>
                <div class="col-4 text-center">
                    <span class="badge bg-danger" style="font-size: 1.2em;">${analysis.severity_breakdown.high}</span>
                    <div><small>High</small></div>
                </div>
            </div>
        </div>
    `;

    // Get risk level badge
    const riskLevelBadge = getRiskLevelBadge(analysis.risk_level);

    const resultHtml = `
        <div class="alert alert-${alertType} border-${alertType}" style="border-width: 3px;">
            <h4>${icon} ${statusText}</h4>
            <hr>
            <div class="row">
                <div class="col-md-6">
                    <p><strong>Email ID:</strong> ${result.email_id}</p>
                    <p><strong>Filename:</strong> ${result.filename}</p>
                    <p><strong>Sender:</strong> <code>${result.sender || 'N/A'}</code></p>
                    <p><strong>Subject:</strong> ${result.subject || 'N/A'}</p>
                </div>
                <div class="col-md-6">
                    <p><strong>Risk Level:</strong> ${riskLevelBadge}</p>
                    <p><strong>Confidence Score:</strong>
                        <span class="badge bg-${isPhishing ? 'danger' : 'success'}" style="font-size: 1.1em;">
                            ${analysis.confidence_score}%
                        </span>
                    </p>
                    <p><strong>Total IOCs Found:</strong>
                        <span class="badge bg-info" style="font-size: 1.1em;">
                            ${analysis.total_iocs}
                        </span>
                    </p>
                </div>
            </div>

            ${analysis.total_iocs > 0 ? severityHtml : ''}
            ${analysis.total_iocs > 0 ? iocBreakdownHtml : '<p class="mt-2"><em>No indicators of compromise detected.</em></p>'}

            ${isPhishing ? `
                <div class="alert alert-warning mt-3 mb-0">
                    <strong>⚠️ Warning:</strong> This email has been identified as a phishing attempt.
                    Do not click any links, download attachments, or provide any personal information.
                </div>
            ` : `
                <div class="alert alert-info mt-3 mb-0">
                    <strong>ℹ️ Info:</strong> This email appears to be legitimate. However, always exercise
                    caution when clicking links or downloading attachments.
                </div>
            `}
        </div>
    `;

    document.getElementById('upload-result').innerHTML = resultHtml;
}

// Get risk level badge
function getRiskLevelBadge(riskLevel) {
    const badges = {
        'Critical': '<span class="badge bg-danger" style="font-size: 1.2em;">🔴 CRITICAL</span>',
        'High': '<span class="badge bg-danger" style="font-size: 1.2em;">🔴 HIGH</span>',
        'Medium': '<span class="badge bg-warning" style="font-size: 1.2em;">🟡 MEDIUM</span>',
        'Low': '<span class="badge bg-warning" style="font-size: 1.2em;">🟡 LOW</span>',
        'Safe': '<span class="badge bg-success" style="font-size: 1.2em;">🟢 SAFE</span>'
    };
    return badges[riskLevel] || '<span class="badge bg-secondary">Unknown</span>';
}

// Load emails
async function loadEmails() {
    try {
        const response = await fetch(`${API_BASE_URL}/emails`);
        const emails = await response.json();

        const tbody = document.getElementById('emails-table-body');
        tbody.innerHTML = '';

        if (emails.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center">No emails found</td></tr>';
            return;
        }

        emails.forEach(email => {
            const row = document.createElement('tr');

            const statusBadge = getStatusBadge(email.status);
            const phishingBadge = email.is_phishing ?
                '<span class="badge bg-danger">Phishing</span>' :
                '<span class="badge bg-success">Legitimate</span>';

            row.innerHTML = `
                <td>${email.id}</td>
                <td>${email.filename}</td>
                <td>${email.sender || 'N/A'}</td>
                <td>${email.subject || 'N/A'}</td>
                <td>${new Date(email.upload_date).toLocaleString()}</td>
                <td>${statusBadge}</td>
                <td><span class="badge bg-info">${email.ioc_count}</span></td>
            `;
            tbody.appendChild(row);
        });

    } catch (error) {
        console.error('Error loading emails:', error);
        showAlert('Error loading emails', 'danger');
    }
}

// Load IOCs
async function loadIOCs(page = 1) {
    try {
        const type = document.getElementById('ioc-type-filter').value;
        const search = document.getElementById('ioc-search').value;

        let url = `${API_BASE_URL}/iocs?page=${page}&per_page=50`;
        if (type) url += `&type=${type}`;
        if (search) url += `&search=${search}`;

        const response = await fetch(url);
        const data = await response.json();

        const tbody = document.getElementById('iocs-table-body');
        tbody.innerHTML = '';

        if (data.items.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" class="text-center">No IOCs found</td></tr>';
            return;
        }

        data.items.forEach(ioc => {
            const row = document.createElement('tr');
            const severityBadge = getSeverityBadge(ioc.severity);

            row.innerHTML = `
                <td><span class="badge bg-secondary">${ioc.type.toUpperCase()}</span></td>
                <td><code>${ioc.value}</code></td>
                <td>${severityBadge}</td>
                <td>${new Date(ioc.detection_date).toLocaleString()}</td>
                <td>${ioc.email_id}</td>
            `;
            tbody.appendChild(row);
        });

        // Render pagination
        renderPagination(data.page, data.pages);

    } catch (error) {
        console.error('Error loading IOCs:', error);
        showAlert('Error loading IOCs', 'danger');
    }
}

// Render pagination
function renderPagination(currentPage, totalPages) {
    const pagination = document.getElementById('ioc-pagination');
    pagination.innerHTML = '';

    if (totalPages <= 1) return;

    for (let i = 1; i <= totalPages; i++) {
        const li = document.createElement('li');
        li.className = `page-item ${i === currentPage ? 'active' : ''}`;
        li.innerHTML = `<a class="page-link" href="#" onclick="loadIOCs(${i}); return false;">${i}</a>`;
        pagination.appendChild(li);
    }
}

// Get status badge
function getStatusBadge(status) {
    const badges = {
        'pending': '<span class="badge bg-warning">Pending</span>',
        'analyzing': '<span class="badge bg-info">Analyzing</span>',
        'completed': '<span class="badge bg-success">Completed</span>',
        'error': '<span class="badge bg-danger">Error</span>'
    };
    return badges[status] || '<span class="badge bg-secondary">Unknown</span>';
}

// Get severity badge
function getSeverityBadge(severity) {
    const badges = {
        'low': '<span class="badge bg-success">Low</span>',
        'medium': '<span class="badge bg-warning">Medium</span>',
        'high': '<span class="badge bg-danger">High</span>'
    };
    return badges[severity] || '<span class="badge bg-secondary">Unknown</span>';
}

// Show alert
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.getElementById('upload-result').appendChild(alertDiv);
}
