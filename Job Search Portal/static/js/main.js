/**
 * Job Search Portal - Global Master JavaScript
 */

document.addEventListener('DOMContentLoaded', function () {
  // 1. Auto-dismiss flash alerts after 5 seconds
  const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) {
        bsAlert.close();
      }
    }, 5000);
  });

  // 2. Initialize Bootstrap Tooltips & Popovers
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });

  // 3. Confirm destructive actions (e.g., delete job, withdraw application)
  const confirmActions = document.querySelectorAll('[data-confirm]');
  confirmActions.forEach(function (element) {
    element.addEventListener('click', function (e) {
      const message = this.getAttribute('data-confirm') || 'Are you sure you want to proceed with this action?';
      if (!confirm(message)) {
        e.preventDefault();
      }
    });
  });

  // 4. Role selection visual cards in registration form
  const roleCards = document.querySelectorAll('.role-card-option');
  const roleSelect = document.getElementById('id_role');
  if (roleCards.length > 0 && roleSelect) {
    roleCards.forEach(function (card) {
      card.addEventListener('click', function () {
        const selectedRole = this.getAttribute('data-role');
        roleSelect.value = selectedRole;
        roleCards.forEach(c => c.classList.remove('border-primary', 'bg-light'));
        this.classList.add('border-primary', 'bg-light');
      });
    });
  }

  // 5. Scroll-to-top button
  const scrollTopBtn = document.createElement('button');
  scrollTopBtn.innerHTML = '<i class="bi bi-arrow-up"></i>';
  scrollTopBtn.className = 'btn btn-primary rounded-circle shadow-lg position-fixed d-none';
  scrollTopBtn.style.bottom = '24px';
  scrollTopBtn.style.right = '24px';
  scrollTopBtn.style.width = '45px';
  scrollTopBtn.style.height = '45px';
  scrollTopBtn.style.zIndex = '1000';
  scrollTopBtn.title = 'Back to top';
  document.body.appendChild(scrollTopBtn);

  window.addEventListener('scroll', function () {
    if (window.scrollY > 300) {
      scrollTopBtn.classList.remove('d-none');
    } else {
      scrollTopBtn.classList.add('d-none');
    }
  });

  scrollTopBtn.addEventListener('click', function () {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
});
