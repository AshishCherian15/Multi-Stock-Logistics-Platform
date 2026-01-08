/**
 * Notifications System - Real-time notification management
 */

let notificationCount = 0;

// Load notifications from API
function loadNotifications() {
    Promise.all([
        fetch('/api/notifications/api/recent/?limit=5').then(r => r.json()),
        fetch('/api/notifications/api/unread-count/').then(r => r.json())
    ])
    .then(([notifData, countData]) => {
        notificationCount = countData.count;
        const badge = document.getElementById('notificationBadge');
        if (badge) {
            badge.textContent = notificationCount > 99 ? '99+' : notificationCount;
            badge.style.display = notificationCount > 0 ? 'inline-block' : 'none';
        }
        displayNotifications(notifData.notifications);
    })
    .catch(error => console.error('Notification load error:', error));
}



// Display notifications in dropdown
function displayNotifications(notifications) {
    const dropdown = document.getElementById('notificationDropdown');
    if (!dropdown) return;

    if (!notifications || notifications.length === 0) {
        dropdown.innerHTML = `
            <div class="text-center py-4 text-muted">
                <i class="fas fa-bell-slash fa-2x mb-2"></i>
                <p class="mb-0">No notifications</p>
            </div>
        `;
        return;
    }

    dropdown.innerHTML = notifications.map(notif => {
        const iconClass = getNotificationIcon(notif.type, notif.category);
        const bgClass = notif.is_read ? 'bg-light' : 'bg-white';
        const timeAgo = formatTimeAgo(notif.created_at);
        
        return `
            <a href="${notif.link || '#'}" 
               class="dropdown-item ${bgClass} border-bottom py-3" 
               onclick="markAsRead(${notif.id})"
               style="white-space: normal;">
                <div class="d-flex align-items-start">
                    <div class="me-3">
                        <i class="fas fa-${iconClass} ${getTypeColor(notif.type)}" style="font-size: 1.2rem;"></i>
                    </div>
                    <div class="flex-grow-1">
                        <div class="fw-bold text-dark">${notif.title}</div>
                        <small class="text-muted">${notif.message}</small>
                        <div class="mt-1">
                            <small class="text-muted"><i class="fas fa-clock me-1"></i>${timeAgo}</small>
                        </div>
                    </div>
                    ${!notif.is_read ? '<span class="badge bg-primary rounded-pill">New</span>' : ''}
                </div>
            </a>
        `;
    }).join('') + `
        <div class="dropdown-divider"></div>
        <a href="/api/notifications/" class="dropdown-item text-center text-primary py-2">
            <i class="fas fa-list me-1"></i>View All Notifications
        </a>
        <a href="#" onclick="markAllAsRead(); return false;" class="dropdown-item text-center text-success py-2">
            <i class="fas fa-check-double me-1"></i>Mark All as Read
        </a>
    `;
}

// Get icon based on notification type and category
function getNotificationIcon(type, category) {
    const icons = {
        'order': 'shopping-cart',
        'stock': 'boxes',
        'user': 'user',
        'message': 'envelope',
        'payment': 'credit-card',
        'system': 'cog'
    };
    return icons[category] || 'bell';
}

// Get color class based on type
function getTypeColor(type) {
    const colors = {
        'info': 'text-info',
        'warning': 'text-warning',
        'error': 'text-danger',
        'success': 'text-success',
        'alert': 'text-danger'
    };
    return colors[type] || 'text-primary';
}

// Format time ago
function formatTimeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const seconds = Math.floor((now - date) / 1000);
    
    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
    return date.toLocaleDateString();
}

// Mark notification as read
function markAsRead(notificationId) {
    fetch(`/api/notifications/mark-read/${notificationId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) loadNotifications();
    })
    .catch(error => console.error('Mark read error:', error));
}

// Mark all as read
function markAllAsRead() {
    fetch('/api/notifications/mark-all-read/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            loadNotifications();
            showAlert('All notifications marked as read', 'success');
        }
    })
    .catch(error => console.error('Mark all read error:', error));
}

// Get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Show alert notification
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 80px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);
    setTimeout(() => {
        if (alertDiv.parentNode) alertDiv.parentNode.removeChild(alertDiv);
    }, 3000);
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        loadNotifications();
        setInterval(loadNotifications, 30000);
    });
} else {
    loadNotifications();
    setInterval(loadNotifications, 30000);
}
