/**
 * Face Forge - Module 4 Global Client Utilities (Plain JavaScript)
 */

document.addEventListener('DOMContentLoaded', () => {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach((alert) => {
        setTimeout(() => {
            if (alert && alert.parentElement) {
                alert.style.transition = 'opacity 0.4s ease';
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 400);
            }
        }, 5000);
    });
});
