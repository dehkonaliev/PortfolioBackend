from django.core.exceptions import ValidationError


def validate_cover_image_size(file):
    max_bytes = 5 * 1024 * 1024
    if file.size > max_bytes:
        raise ValidationError("Cover image size must be under 5MB.")


def validate_certification_size(file):
    max_bytes = 10 * 1024 * 1024
    if file.size > max_bytes:
        raise ValidationError("Certification file size must be under 10MB.")
