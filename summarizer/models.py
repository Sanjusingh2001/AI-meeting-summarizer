from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class MeetingTranscript(models.Model):
    """Model to store meeting transcripts and their summaries."""
    title = models.CharField(max_length=200, blank=True)
    transcript_text = models.TextField()
    custom_instruction = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title or f"Transcript {self.id}"


class EmailShare(models.Model):
    """Model to store email sharing information."""
    transcript = models.ForeignKey(MeetingTranscript, on_delete=models.CASCADE)
    recipient_emails = models.TextField(help_text="Comma-separated email addresses")
    subject = models.CharField(max_length=200, default="Meeting Summary")
    message = models.TextField(blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Shared {self.transcript.title} to {self.recipient_emails}"
