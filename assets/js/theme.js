// Theme Toggle Functionality
(function() {
    const THEME_KEY = 'portfolio-theme';

    // Get saved theme or default to dark
    function getTheme() {
        return localStorage.getItem(THEME_KEY) || 'dark';
    }

    // Save theme preference
    function setTheme(theme) {
        localStorage.setItem(THEME_KEY, theme);
        document.documentElement.setAttribute('data-theme', theme);
    }

    // Toggle between light and dark
    function toggleTheme() {
        const currentTheme = getTheme();
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    }

    // Initialize theme on page load
    function initTheme() {
        const savedTheme = getTheme();
        document.documentElement.setAttribute('data-theme', savedTheme);
    }

    // Apply theme immediately to prevent flash
    initTheme();

    // Expose toggle function globally
    window.toggleTheme = toggleTheme;

    // Also initialize after DOM is ready (for any dynamic elements)
    document.addEventListener('DOMContentLoaded', initTheme);
})();
