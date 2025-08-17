from rest_framework import serializers
from .models import MeetingTranscript, EmailShare


class MeetingTranscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingTranscript
        fields = ['id', 'title', 'transcript_text', 'custom_instruction', 'summary', 'created_at', 'updated_at']


class EmailShareSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailShare
        fields = ['id', 'transcript', 'recipient_emails', 'subject', 'message', 'sent_at']


class SummaryGenerationSerializer(serializers.Serializer):
    transcript_text = serializers.CharField()
    custom_instruction = serializers.CharField(required=False, allow_blank=True)
