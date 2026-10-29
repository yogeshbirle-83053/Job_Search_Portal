from django.db import models


class ContactMessage(models.Model):
    """
    Model for storing public inquiries, support requests, and user messages.
    """
    name = models.CharField(max_length=120, help_text="Sender's full name.")
    email = models.EmailField(help_text="Sender's contact email address.")
    subject = models.CharField(max_length=200, help_text="Inquiry subject.")
    message = models.TextField(help_text="Full message content.")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"
