from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/generate-summary/', views.generate_summary, name='generate_summary'),
    path('api/save-meeting/', views.save_meeting, name='save_meeting'),
    path('api/share-email/', views.share_via_email, name='share_via_email'),
    path('api/meeting/<int:meeting_id>/', views.get_meeting, name='get_meeting'),
]
