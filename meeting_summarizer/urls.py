"""
URL configuration for meeting_summarizer project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('summarizer.urls')),
    path('', include('summarizer.urls')),
]
