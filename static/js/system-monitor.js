// System Health Monitor
class SystemMonitor {
    constructor() {
        this.checkInterval = 60000; // 1 minute
        this.init();
    }
    
    init() {
        this.checkHealth();
        setInterval(() => this.checkHealth(), this.checkInterval);
    }
    
    async checkHealth() {
        try {
            const response = await fetch('/health/');
            const data = await response.json();
            
            if (data.status === 'healthy') {
                this.updateStatus('online', 'System Online');
            } else {
                this.updateStatus('warning', 'System Issues Detected');
            }
        } catch (error) {
            this.updateStatus('offline', 'Connection Lost');
        }
    }
    
    updateStatus(status, message) {
        const indicator = document.getElementById('system-status-indicator');
        if (indicator) {
            indicator.className = `status-${status}`;
            indicator.title = message;
        }
    }
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => new SystemMonitor());
} else {
    new SystemMonitor();
}
