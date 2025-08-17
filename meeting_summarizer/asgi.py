"""
ASGI config for meeting_summarizer project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meeting_summarizer.settings')

application = get_asgi_application()
