from django.contrib import admin
from .models import MeetingTranscript, EmailShare


@admin.register(MeetingTranscript)
class MeetingTranscriptAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_at', 'updated_at']
    search_fields = ['title', 'transcript_text', 'summary']
    list_filter = ['created_at', 'updated_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(EmailShare)
class EmailShareAdmin(admin.ModelAdmin):
    list_display = ['transcript', 'recipient_emails', 'subject', 'sent_at']
    search_fields = ['recipient_emails', 'subject', 'message']
    list_filter = ['sent_at']
    readonly_fields = ['sent_at']
