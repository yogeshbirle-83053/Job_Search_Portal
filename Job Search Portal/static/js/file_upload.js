/**
 * Job Search Portal - File Upload Usability & Validation
 * Provides client-side validation for PDF format, 5MB size limit,
 * and live filename badge display.
 */

document.addEventListener('DOMContentLoaded', function () {
  const fileInputs = document.querySelectorAll('input[type="file"]');
  const MAX_FILE_SIZE_MB = 5;
  const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;

  fileInputs.forEach(function (input) {
    // Container for displaying selected file badge & size
    const parentContainer = input.closest('.mb-3, .mb-4') || input.parentElement;
    
    // Create live feedback badge container
    let feedbackBadge = document.createElement('div');
    feedbackBadge.className = 'file-selected-badge mt-2 d-none small p-2 rounded border';
    parentContainer.appendChild(feedbackBadge);

    input.addEventListener('change', function (e) {
      const file = this.files[0];
      if (!file) {
        feedbackBadge.classList.add('d-none');
        return;
      }

      const fileName = file.name;
      const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
      const isPdfInput = this.getAttribute('accept') && this.getAttribute('accept').includes('.pdf');
      const fileExt = fileName.split('.').pop().toLowerCase();

      // 1. Check PDF format if required
      if (isPdfInput && fileExt !== 'pdf') {
        alert(`Invalid file format: "${fileName}". Please select a valid PDF file (.pdf).`);
        this.value = ''; // Reset input
        feedbackBadge.className = 'file-selected-badge mt-2 small p-2 rounded border bg-danger-subtle text-danger border-danger-subtle';
        feedbackBadge.innerHTML = `<i class="bi bi-x-circle me-1"></i> <strong>Error:</strong> Only PDF files (.pdf) are allowed.`;
        feedbackBadge.classList.remove('d-none');
        return;
      }

      // 2. Check File Size (Max 5MB)
      if (file.size > MAX_FILE_SIZE_BYTES) {
        alert(`File size exceeds ${MAX_FILE_SIZE_MB}MB limit (${fileSizeMB}MB selected). Please upload a smaller file.`);
        this.value = ''; // Reset input
        feedbackBadge.className = 'file-selected-badge mt-2 small p-2 rounded border bg-danger-subtle text-danger border-danger-subtle';
        feedbackBadge.innerHTML = `<i class="bi bi-x-circle me-1"></i> <strong>Error:</strong> File size (${fileSizeMB}MB) exceeds ${MAX_FILE_SIZE_MB}MB limit.`;
        feedbackBadge.classList.remove('d-none');
        return;
      }

      // 3. Valid file: display success indicator
      feedbackBadge.className = 'file-selected-badge mt-2 small p-2 rounded border bg-success-subtle text-success border-success-subtle d-flex align-items-center justify-content-between';
      feedbackBadge.innerHTML = `
        <div>
          <i class="bi bi-check2-circle me-1 fs-6"></i>
          <strong>Selected:</strong> ${fileName} <span class="text-muted">(${fileSizeMB} MB)</span>
        </div>
        <span class="badge bg-success">Ready</span>
      `;
      feedbackBadge.classList.remove('d-none');
    });
  });
});
