"""
TalentScout URL Configuration

API Endpoints:
- /api/chat/ - Chat with the AI interviewer
- /api/sessions/ - Session management
- /api/sessions/start/ - Start new session
- /api/sessions/<id>/status/ - Get session status
- /api/sessions/<id>/generate-mcqs/ - Generate MCQ questions
- /api/sessions/<id>/submit-mcq/ - Submit MCQ answer
- /api/sessions/<id>/generate-objectives/ - Generate objective questions
- /api/sessions/<id>/submit-objective/ - Submit objective answer
- /api/sessions/<id>/calculate-ratings/ - Calculate skill ratings
- /api/sessions/<id>/download-report/ - Download PDF report
- /api/health/ - Health check
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from talent_scout import views
from talent_scout import views_mcq

# Create router for ViewSets
router = DefaultRouter()
router.register(r'sessions', views.CandidateSessionViewSet, basename='session')

urlpatterns = [
    # ViewSet routes (sessions CRUD)
    path('', include(router.urls)),
    
    # Custom endpoints
    path('chat/', views.chat_message, name='chat'),
    path('health/', views.health_check, name='health'),
    
    # MCQ Screening endpoints
    path('sessions/<uuid:session_id>/generate-mcqs/', 
         views_mcq.generate_mcqs, name='generate-mcqs'),
    path('sessions/<uuid:session_id>/submit-mcq/', 
         views_mcq.submit_mcq_answer, name='submit-mcq'),
    path('sessions/<uuid:session_id>/generate-objectives/', 
         views_mcq.generate_objective_questions, name='generate-objectives'),
    path('sessions/<uuid:session_id>/submit-objective/', 
         views_mcq.submit_objective_answer, name='submit-objective'),
    path('sessions/<uuid:session_id>/calculate-ratings/', 
         views_mcq.calculate_skill_ratings, name='calculate-ratings'),
    path('sessions/<uuid:session_id>/download-report/', 
         views_mcq.download_pdf_report, name='download-report'),
]
