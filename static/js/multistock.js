// MultiStock Platform JavaScript
let notificationInterval;
let isPageVisible = true;

document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.querySelector('#globalSearch');
            if (searchInput) searchInput.focus();
        }
    });
    
    // Start notification polling
    startNotificationPolling();
    
    // Handle page visibility changes
    document.addEventListener('visibilitychange', function() {
        isPageVisible = !document.hidden;
        if (isPageVisible) {
            startNotificationPolling();
            refreshNotifications(); // Immediate refresh when page becomes visible
        } else {
            stopNotificationPolling();
        }
    });
});

function startNotificationPolling() {
    if (notificationInterval) clearInterval(notificationInterval);
    notificationInterval = setInterval(() => {
        if (isPageVisible) refreshNotifications();
    }, 120000); // 2 minutes
}

function stopNotificationPolling() {
    if (notificationInterval) {
        clearInterval(notificationInterval);
        notificationInterval = null;
    }
}

function refreshNotifications() {
    if (!isPageVisible) return;
    
    fetch('/api/notifications/api/unread-count/')
        .then(response => response.json())
        .then(data => updateNotificationBadge(data.count))
        .catch(error => console.log('Notification refresh failed'));
}

function updateNotificationBadge(count) {
    const badge = document.querySelector('.notification-badge');
    if (badge) {
        badge.textContent = count;
        badge.style.display = count > 0 ? 'inline' : 'none';
    }
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999;';
    toast.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
    document.body.appendChild(toast);
    setTimeout(() => { if (toast.parentNode) toast.parentNode.removeChild(toast); }, 5000);
}