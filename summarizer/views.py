from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, TemplateHTMLRenderer
from rest_framework.response import Response
from rest_framework import status
import json
from django.conf import settings
from .models import MeetingTranscript, EmailShare
from .serializers import MeetingTranscriptSerializer, EmailShareSerializer, SummaryGenerationSerializer


def index(request):
    """Main page view."""
    return render(request, 'summarizer/index.html')


@api_view(['POST'])
@renderer_classes([JSONRenderer])
def generate_summary(request):
    """Generate AI summary from transcript."""
    serializer = SummaryGenerationSerializer(data=request.data)
    if serializer.is_valid():
        transcript_text = serializer.validated_data['transcript_text']
        custom_instruction = serializer.validated_data.get('custom_instruction', '')
        
        try:
            # Try multiple AI providers with fallback
            summary = None
            
            # First try Groq (free tier available)
            if settings.GROQ_API_KEY:
                try:
                    import groq
                    client = groq.Groq(api_key=settings.GROQ_API_KEY)
                    
                    prompt = f"""
                    Please provide a structured summary of the following meeting transcript.
                    
                    {f"Custom instruction: {custom_instruction}" if custom_instruction else ""}
                    
                    Transcript:
                    {transcript_text}
                    
                    Please provide a clear, organized summary that follows the custom instruction if provided.
                    """
                    
                    response = client.chat.completions.create(
                        model="llama3-8b-8192",  # Fast and free
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant that creates clear, structured meeting summaries."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=500,
                        temperature=0.7
                    )
                    
                    summary = response.choices[0].message.content
                    print("✅ Summary generated using Groq")
                    
                except Exception as groq_error:
                    print(f"⚠️ Groq failed: {groq_error}")
                    summary = None
            
            # Fallback to OpenAI if Groq fails or not configured
            if not summary and settings.OPENAI_API_KEY:
                try:
                    from openai import OpenAI
                    
                    # Debug: Print API key (first 20 chars for security)
                    api_key = settings.OPENAI_API_KEY
                    print(f"Debug: OpenAI API Key loaded: {api_key[:20] if api_key else 'NOT_FOUND'}...")
                    
                    if not api_key:
                        raise Exception("OpenAI API key not found in settings")
                    
                    client = OpenAI(api_key=api_key)
                    
                    prompt = f"""
                    Please provide a structured summary of the following meeting transcript.
                    
                    {f"Custom instruction: {custom_instruction}" if custom_instruction else ""}
                    
                    Transcript:
                    {transcript_text}
                    
                    Please provide a clear, organized summary that follows the custom instruction if provided.
                    """
                    
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant that creates clear, structured meeting summaries."},
                            {"role": "user", "content": prompt}
                        ],
                        max_tokens=500,
                        temperature=0.7
                    )
                    
                    summary = response.choices[0].message.content
                    print("✅ Summary generated using OpenAI")
                    
                except Exception as openai_error:
                    print(f"⚠️ OpenAI failed: {openai_error}")
                    summary = None
            
            # Final fallback: Simple rule-based summary if all AI providers fail
            if not summary:
                print("⚠️ All AI providers failed, using rule-based fallback")
                summary = generate_fallback_summary(transcript_text, custom_instruction)
            
            # Save to database
            meeting = MeetingTranscript.objects.create(
                transcript_text=transcript_text,
                custom_instruction=custom_instruction,
                summary=summary
            )
            
            return Response({
                'success': True,
                'summary': summary,
                'meeting_id': meeting.id
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@renderer_classes([JSONRenderer])
def save_meeting(request):
    """Save or update meeting with title and edited summary."""
    try:
        data = json.loads(request.body)
        meeting_id = data.get('meeting_id')
        title = data.get('title', '')
        summary = data.get('summary', '')
        
        if meeting_id:
            meeting = get_object_or_404(MeetingTranscript, id=meeting_id)
            meeting.title = title
            meeting.summary = summary
            meeting.save()
        else:
            meeting = MeetingTranscript.objects.create(
                title=title,
                summary=summary,
                transcript_text=''
            )
        
        return Response({
            'success': True,
            'meeting_id': meeting.id
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@renderer_classes([JSONRenderer])
def share_via_email(request):
    """Share summary via email (simulated)."""
    try:
        data = json.loads(request.body)
        meeting_id = data.get('meeting_id')
        recipient_emails = data.get('recipient_emails', '')
        subject = data.get('subject', 'Meeting Summary')
        message = data.get('message', '')
        
        meeting = get_object_or_404(MeetingTranscript, id=meeting_id)
        
        # Save email share record
        email_share = EmailShare.objects.create(
            transcript=meeting,
            recipient_emails=recipient_emails,
            subject=subject,
            message=message
        )
        
        # In a real application, you would send actual emails here
        # For now, we'll just simulate success
        
        return Response({
            'success': True,
            'message': f'Summary shared successfully to {recipient_emails}',
            'share_id': email_share.id
        })
        
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@renderer_classes([JSONRenderer])
def get_meeting(request, meeting_id):
    """Get meeting details by ID."""
    try:
        meeting = get_object_or_404(MeetingTranscript, id=meeting_id)
        serializer = MeetingTranscriptSerializer(meeting)
        return Response(serializer.data)
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def generate_fallback_summary(transcript_text, custom_instruction):
    """Generate a simple rule-based summary when AI providers fail."""
    try:
        # Simple text processing for fallback
        lines = transcript_text.split('\n')
        sentences = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#'):
                sentences.append(line)
        
        # Basic summary logic
        if custom_instruction and 'bullet' in custom_instruction.lower():
            summary = "📋 Meeting Summary (Fallback Mode):\n\n"
            for i, sentence in enumerate(sentences[:10], 1):  # Limit to 10 points
                if sentence:
                    summary += f"• {sentence}\n"
        else:
            summary = "📋 Meeting Summary (Fallback Mode):\n\n"
            summary += "Key Points:\n"
            for i, sentence in enumerate(sentences[:8], 1):  # Limit to 8 points
                if sentence:
                    summary += f"{i}. {sentence}\n"
        
        summary += "\n\n⚠️ Note: This is a fallback summary. For better results, please configure an AI API key."
        return summary
        
    except Exception as e:
        return f"📋 Meeting Summary (Fallback Mode):\n\nUnable to process transcript automatically.\n\n⚠️ Note: This is a fallback summary. For better results, please configure an AI API key.\n\nError: {str(e)}"
