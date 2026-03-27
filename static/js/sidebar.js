document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar') || document.querySelector('.sidebar') || document.querySelector('.customer-sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const mainContent = document.querySelector('.main-content');
    
    if (!sidebar || !sidebarToggle) return;
    
    let sidebarOpen = !sidebar.classList.contains('closed');
    
    sidebarToggle.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        sidebarOpen = !sidebarOpen;
        
        if (sidebarOpen) {
            sidebar.classList.remove('closed');
            sidebar.style.left = '0';
            if (mainContent) {
                mainContent.classList.remove('sidebar-closed');
                mainContent.style.marginLeft = '250px';
            }
        } else {
            sidebar.classList.add('closed');
            sidebar.style.left = '-250px';
            if (mainContent) {
                mainContent.classList.add('sidebar-closed');
                mainContent.style.marginLeft = '0';
            }
        }
    });
    
    // Close sidebar on mobile when clicking outside
    document.addEventListener('click', function(event) {
        if (window.innerWidth <= 768 && sidebarOpen) {
            if (!sidebar.contains(event.target) && !sidebarToggle.contains(event.target)) {
                sidebarOpen = false;
                sidebar.classList.add('closed');
                sidebar.style.left = '-250px';
                if (mainContent) {
                    mainContent.classList.add('sidebar-closed');
                    mainContent.style.marginLeft = '0';
                }
            }
        }
    });
});