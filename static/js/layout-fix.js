// Fix initial layout state on page load
document.addEventListener('DOMContentLoaded', function() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');
    const footer = document.querySelector('.footer');
    
    if (sidebar && mainContent) {
        // Check if sidebar is closed on page load
        if (sidebar.classList.contains('closed')) {
            mainContent.style.left = '0';
            mainContent.classList.add('sidebar-closed');
            if (footer) {
                footer.classList.add('sidebar-closed');
                footer.style.marginLeft = '0';
                footer.style.width = '100%';
            }
        } else {
            mainContent.style.left = '280px';
            mainContent.classList.remove('sidebar-closed');
            if (footer) {
                footer.classList.remove('sidebar-closed');
                footer.style.marginLeft = '280px';
                footer.style.width = 'calc(100% - 280px)';
            }
        }
    }
});