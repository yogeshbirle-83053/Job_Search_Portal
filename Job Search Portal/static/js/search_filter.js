/**
 * Job Search Portal - Dynamic Search & Filter Enhancements
 */

document.addEventListener('DOMContentLoaded', function () {
  const searchInputs = document.querySelectorAll('input[name="q"], input[name="location"]');

  searchInputs.forEach(function (input) {
    // Add clear 'x' button inside input when text is entered
    if (input.value.length > 0) {
      input.classList.add('has-content');
    }

    input.addEventListener('input', function () {
      if (this.value.length > 0) {
        this.classList.add('has-content');
      } else {
        this.classList.remove('has-content');
      }
    });
  });

  // Filter form auto-submit on select change (for sort_by dropdowns)
  const autoSubmitSelects = document.querySelectorAll('.auto-submit-select');
  autoSubmitSelects.forEach(function (select) {
    select.addEventListener('change', function () {
      if (this.form) {
        this.form.submit();
      }
    });
  });
});
