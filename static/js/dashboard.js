document.addEventListener('DOMContentLoaded', function() {
    // Initialize Chart.js
    const ctx = document.getElementById('traffic-chart').getContext('2d');
    const trafficChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Requests per Minute',
                data: [],
                borderColor: '#2563eb',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Site Configuration Form
    const siteConfigForm = document.getElementById('site-config-form');
    siteConfigForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = {
            site_name: document.getElementById('site-name').value,
            max_requests_per_min: parseInt(document.getElementById('rate-limit').value),
            alert_threshold: parseInt(document.getElementById('alert-threshold').value),
            geo_blocking: document.getElementById('enable-geo').checked,
            email_alerts: document.getElementById('enable-alerts').checked,
            maintenance_mode: document.getElementById('maintenance-mode').checked
        };

        try {
            const response = await fetch('/api/v2/sites', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(formData)
            });

            if (response.ok) {
                showNotification('Site configuration updated successfully', 'success');
                loadSiteStats();
            } else {
                throw new Error('Failed to update configuration');
            }
        } catch (error) {
            showNotification(error.message, 'error');
        }
    });

    // Real-time Stats Update
    let statsInterval;
    function startStatsUpdate() {
        loadSiteStats();
        statsInterval = setInterval(loadSiteStats, 30000); // Update every 30 seconds
    }

    async function loadSiteStats() {
        try {
            const siteName = document.getElementById('site-name').value;
            const [trafficResponse, attacksResponse] = await Promise.all([
                fetch(`/api/v2/traffic/${siteName}`),
                fetch(`/api/v2/attacks/${siteName}`)
            ]);

            if (trafficResponse.ok && attacksResponse.ok) {
                const trafficData = await trafficResponse.json();
                const attacksData = await attacksResponse.json();

                updateDashboardStats(trafficData, attacksData);
                updateTrafficChart(trafficData);
                updateActivityFeed(trafficData.concat(attacksData));
            }
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    function updateDashboardStats(trafficData, attacksData) {
        document.getElementById('total-requests').textContent = trafficData.length;
        document.getElementById('blocked-attacks').textContent = attacksData.length;
        document.getElementById('active-sites').textContent = '1'; // Update with actual count

        const status = attacksData.some(attack => attack.status === 'active')
            ? 'danger'
            : 'normal';
        
        const statusBadge = document.getElementById('system-status');
        statusBadge.className = `status-badge status-${status}`;
        statusBadge.textContent = status === 'danger' ? 'Under Attack' : 'Protected';
    }

    function updateTrafficChart(trafficData) {
        const last10Minutes = trafficData.slice(-10);
        trafficChart.data.labels = last10Minutes.map(item => 
            new Date(item.timestamp).toLocaleTimeString());
        trafficChart.data.datasets[0].data = last10Minutes.map(item => 
            item.request_count);
        trafficChart.update();
    }

    function updateActivityFeed(activities) {
        const feed = document.getElementById('activity-feed');
        feed.innerHTML = '';

        activities
            .sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp))
            .slice(0, 5)
            .forEach(activity => {
                const item = document.createElement('div');
                item.className = 'activity-item';
                item.innerHTML = `
                    <div class="activity-time">${new Date(activity.timestamp).toLocaleTimeString()}</div>
                    <div class="activity-description">${activity.description || activity.status}</div>
                    <div class="status-badge status-${activity.severity || 'normal'}">${activity.type || 'Traffic'}</div>
                `;
                feed.appendChild(item);
            });
    }

    // Notifications
    function showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);

        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Initialize
    document.getElementById('refresh-stats').addEventListener('click', loadSiteStats);
    startStatsUpdate();
});
