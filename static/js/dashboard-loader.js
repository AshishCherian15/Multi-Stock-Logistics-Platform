// Dashboard Loading States
document.addEventListener('DOMContentLoaded', function() {
    // Show loading spinner on page load
    const dashboardCards = document.querySelectorAll('.metric-card, .chart-container');
    
    dashboardCards.forEach(card => {
        card.style.opacity = '0.6';
        card.style.transition = 'opacity 0.3s';
    });
    
    // Simulate data loading
    setTimeout(() => {
        dashboardCards.forEach(card => {
            card.style.opacity = '1';
        });
    }, 500);
    
    // Auto-refresh dashboard every 30 seconds
    setInterval(() => {
        refreshDashboardMetrics();
    }, 30000);
});

function refreshDashboardMetrics() {
    fetch('/api/dashboard/metrics/')
        .then(response => response.json())
        .then(data => {
            // Update metrics
            if (data.revenue) document.getElementById('revenue-metric').textContent = formatCurrency(data.revenue);
            if (data.orders) document.getElementById('orders-metric').textContent = data.orders;
            if (data.products) document.getElementById('products-metric').textContent = data.products;
            if (data.low_stock) document.getElementById('low-stock-metric').textContent = data.low_stock;
        })
        .catch(error => console.error('Dashboard refresh error:', error));
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount);
}

// Loading overlay for page transitions
function showLoadingOverlay() {
    const overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.innerHTML = '<div class="spinner-border text-primary" role="status"><span class="sr-only">Loading...</span></div>';
    overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(255,255,255,0.9);display:flex;align-items:center;justify-content:center;z-index:9999;';
    document.body.appendChild(overlay);
}

function hideLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.remove();
}
