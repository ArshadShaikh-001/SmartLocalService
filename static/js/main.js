/**
 * Vanilla JavaScript for Smart Local Service Connect
 * Lightweight, zero dependencies
 */

document.addEventListener('DOMContentLoaded', function () {
  // Mobile Navigation Hamburger Toggle
  const navToggle = document.getElementById('navToggle');
  const navMenu = document.getElementById('navMenu');

  if (navToggle && navMenu) {
    navToggle.addEventListener('click', function () {
      navMenu.classList.toggle('active');
      const expanded = navMenu.classList.contains('active');
      navToggle.setAttribute('aria-expanded', expanded);
    });
  }

  // Auto-dismiss Django flash messages after 6 seconds
  const alerts = document.querySelectorAll('.alert');
  if (alerts.length > 0) {
    setTimeout(function () {
      alerts.forEach(function (alert) {
        alert.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
        alert.style.opacity = '0';
        alert.style.transform = 'translateY(-6px)';
        setTimeout(function () {
          alert.remove();
        }, 400);
      });
    }, 6000);
  }
});
