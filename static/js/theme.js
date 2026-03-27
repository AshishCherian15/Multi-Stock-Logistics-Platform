/**
 * Theme Module
 * Handles dark/light theme toggling and persistence
 */

/**
 * Toggle between light and dark theme
 */
function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';

    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);

    // Update theme icon
    const themeIcon = document.getElementById('themeIcon');
    const themeToggle = document.getElementById('themeToggle');

    if (newTheme === 'dark') {
        themeIcon.className = 'fas fa-moon';
        themeToggle.title = 'Switch to Light Mode';
    } else {
        themeIcon.className = 'fas fa-sun';
        themeToggle.title = 'Switch to Dark Mode';
    }

    // Add animation effect
    themeToggle.style.transform = 'scale(0.9)';
    setTimeout(() => {
        themeToggle.style.transform = 'scale(1)';
    }, 150);
}

/**
 * Initialize theme on page load from localStorage
 */
function initializeTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);

    const themeIcon = document.getElementById('themeIcon');
    const themeToggle = document.getElementById('themeToggle');

    if (themeIcon && themeToggle) {
        if (savedTheme === 'dark') {
            themeIcon.className = 'fas fa-moon';
            themeToggle.title = 'Switch to Light Mode';
        } else {
            themeIcon.className = 'fas fa-sun';
            themeToggle.title = 'Switch to Dark Mode';
        }
    }
}

// Initialize theme on page load
document.addEventListener('DOMContentLoaded', initializeTheme);
