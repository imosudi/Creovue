// ==========================================
// Creovue Global JavaScript
// ==========================================

// Run once DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log("Creovue is loaded and ready.");

    // Example: Highlight active link (basic)
    const current = location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === current) {
            link.classList.add('active');
        }
    });

    // Additional interactivity hooks can be placed here
});