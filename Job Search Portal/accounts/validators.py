import os
from django.core.exceptions import ValidationError


def validate_pdf_file(value):
    """
    Validates that the uploaded file is a PDF and does not exceed 5MB.
    Checks file extension and magic byte header '%PDF-'.
    """
    # 1. Validate file extension
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.pdf']
    if ext not in valid_extensions:
        raise ValidationError("Unsupported file format. Please upload a PDF file (.pdf).")

    # 2. Validate file size (max 5MB)
    max_size_mb = 5
    if value.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"File size exceeds {max_size_mb}MB limit. Please upload a smaller file.")

    # 3. Validate PDF magic bytes (%PDF-)
    initial_pos = value.tell()
    try:
        header = value.read(5)
        value.seek(initial_pos)
        if header != b'%PDF-':
            raise ValidationError("Invalid PDF file. The file content does not match a valid PDF.")
    except Exception:
        value.seek(initial_pos)
        raise ValidationError("Could not verify PDF file integrity.")
