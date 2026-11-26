/**
 * Vanilla JavaScript for Smart Local Service Connect
 * Lightweight, zero dependencies (BCA Mini Project)
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Mobile Navigation Hamburger Toggle
  const navToggle = document.getElementById('navToggle');
  const navMenu = document.getElementById('navMenu');

  if (navToggle && navMenu) {
    navToggle.addEventListener('click', function () {
      navMenu.classList.toggle('active');
      const expanded = navMenu.classList.contains('active');
      navToggle.setAttribute('aria-expanded', expanded);
    });
  }

  // 2. Auto-dismiss Django flash messages after 6 seconds
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

  // 3. Client-side Form Validation Helpers
  const formsToValidate = document.querySelectorAll('form');
  formsToValidate.forEach(function (form) {
    form.addEventListener('submit', function (e) {
      // Validate phone input if present
      const phoneInput = form.querySelector('input[type="tel"], input[name="phone"]');
      if (phoneInput && phoneInput.value.trim() !== '') {
        const digits = phoneInput.value.replace(/\D/g, '');
        if (digits.length < 10) {
          e.preventDefault();
          alert('Please enter a valid phone number with at least 10 digits.');
          phoneInput.focus();
          return false;
        }
      }

      // Validate preferred date if present (cannot be in the past)
      const dateInput = form.querySelector('input[name="preferred_date"]');
      if (dateInput && dateInput.value) {
        const selectedDate = new Date(dateInput.value);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        if (selectedDate < today) {
          e.preventDefault();
          alert('The preferred service date cannot be in the past. Please select today or a future date.');
          dateInput.focus();
          return false;
        }
      }

      // Validate minimum 10 characters for description / message / review_text
      const textareas = form.querySelectorAll('textarea[name="description"], textarea[name="message"], textarea[name="review_text"]');
      textareas.forEach(function (ta) {
        if (ta.value && ta.value.trim().length < 10) {
          e.preventDefault();
          alert('Please enter at least 10 characters in your message/description.');
          ta.focus();
          return false;
        }
      });
    });
  });
});
