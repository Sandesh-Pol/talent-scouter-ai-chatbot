"""
Django REST Framework Views

API endpoints for the TalentScout hiring assistant.

Endpoints:
- POST /api/chat/ - Send a chat message
- GET /api/sessions/ - List all sessions
- GET /api/sessions/<id>/ - Get session details
- POST /api/sessions/start/ - Start a new session
- GET /api/sessions/<id>/status/ - Get session status
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404
import logging
import uuid

from talent_scout.models import CandidateSession, ChatMessage, InterviewPhase
from talent_scout.serializers import (
    CandidateSessionSerializer,
    CandidateSessionListSerializer,
    ChatMessageSerializer,
    ChatRequestSerializer,
    ChatResponseSerializer,
    SessionStatusSerializer
)
from talent_scout.services.state_machine import get_state_machine
from talent_scout.services.groq_service import GroqServiceError
from talent_scout.utils.data_privacy import DataPrivacyManager

logger = logging.getLogger(__name__)


class CandidateSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing candidate interview sessions.
    
    Provides CRUD operations and custom actions for sessions.
    """
    
    queryset = CandidateSession.objects.all()
    serializer_class = CandidateSessionSerializer
    permission_classes = [AllowAny]  # For demo; use proper auth in production
    
    def get_serializer_class(self):
        """Use simplified serializer for list view"""
        if self.action == 'list':
            return CandidateSessionListSerializer
        return CandidateSessionSerializer
    
    @action(detail=False, methods=['post'])
    def start(self, request):
        """
        Start a new interview session.
        
        POST /api/sessions/start/
        
        Optional body:
        {
            "ip_address": "127.0.0.1",
            "user_agent": "Mozilla/5.0..."
        }
        
        Returns:
        {
            "session_id": "uuid",
            "message": "Welcome message",
            "current_phase": "onboarding"
        }
        """
        try:
            # Get client metadata
            ip_address = request.data.get('ip_address') or self._get_client_ip(request)
            user_agent = request.data.get('user_agent') or request.META.get('HTTP_USER_AGENT', '')
            
            # Create new session
            session = CandidateSession.objects.create(
                ip_address=ip_address,
                user_agent=user_agent,
                current_phase=InterviewPhase.ONBOARDING
            )
            
            # Get initial message from state machine
            state_machine = get_state_machine()
            initial_message = state_machine.get_initial_message()
            
            # Create initial system message
            ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=initial_message
            )
            
            logger.info(f"Started new session: {session.session_id}")
            
            return Response({
                'session_id': str(session.session_id),
                'message': initial_message,
                'current_phase': session.current_phase,
                'profile_completeness': 0.0
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Error starting session: {str(e)}", exc_info=True)
            return Response({
                'error': 'Failed to start session',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """
        Get current status of a session.
        
        GET /api/sessions/<id>/status/
        
        Returns:
        {
            "session_id": "uuid",
            "current_phase": "information_gathering",
            "profile_completeness": 75.0,
            "is_active": true,
            "candidate_profile": {...},
            "message_count": 10,
            "messages": [...]
        }
        """
        session = self.get_object()
        
        # Log data access for GDPR compliance
        if settings.DATA_ACCESS_LOGGING:
            DataPrivacyManager.log_data_access(
                session_id=str(session.session_id),
                access_type='read',
                user=request.user.username if request.user.is_authenticated else 'anonymous'
            )
        
        # Get messages (last N for buffer)
        messages = session.messages.all().order_by('timestamp')
        
        # Build candidate profile
        candidate_profile = {
            'full_name': session.full_name,
            'email': session.email,
            'phone': session.phone,
            'location': session.location,
            'years_experience': session.years_experience,
            'tech_stack': session.tech_stack,
            'position_applied': session.position_applied,
            'experience_level': session.experience_level,
            'skill_ratings': session.skill_ratings  # Include skill ratings
        }
        
        # Anonymize data if in demo mode
        if settings.ANONYMIZE_API_RESPONSES and settings.DEMO_MODE:
            candidate_profile = DataPrivacyManager.anonymize_session_data(candidate_profile)
        
        response_data = {
            'session_id': str(session.session_id),
            'current_phase': session.current_phase,
            'profile_completeness': session.get_profile_completeness(),
            'is_active': session.is_active,
            'candidate_profile': candidate_profile,
            'message_count': messages.count(),
            'messages': ChatMessageSerializer(messages, many=True).data,
            'created_at': session.created_at,
            'updated_at': session.updated_at
        }
        
        serializer = SessionStatusSerializer(data=response_data)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.data)
    
    def _get_client_ip(self, request):
        """Extract client IP from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


@api_view(['POST'])
@permission_classes([AllowAny])
def chat_message(request):
    """
    Process a chat message from the candidate.
    
    POST /api/chat/
    
    Body:
    {
        "message": "User's message",
        "session_id": "uuid-optional"
    }
    
    Returns:
    {
        "message": "Assistant's response",
        "role": "assistant",
        "session_id": "uuid",
        "current_phase": "information_gathering",
        "profile_completeness": 60.0,
        "needs_intervention": false,
        "metadata": {...}
    }
    """
    # Validate request
    request_serializer = ChatRequestSerializer(data=request.data)
    
    if not request_serializer.is_valid():
        return Response({
            'error': 'Validation Error',
            'detail': request_serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    user_message = request_serializer.validated_data['message']
    session_id = request_serializer.validated_data.get('session_id')
    
    try:
        # Get or create session
        if session_id:
            try:
                session = CandidateSession.objects.get(session_id=session_id)
                
                # Check if session is still active
                if not session.is_active:
                    return Response({
                        'error': 'Session Closed',
                        'detail': 'This interview session has been completed.'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            except CandidateSession.DoesNotExist:
                return Response({
                    'error': 'Session Not Found',
                    'detail': f'Session {session_id} does not exist.'
                }, status=status.HTTP_404_NOT_FOUND)
        else:
            # Create new session if none provided
            session = CandidateSession.objects.create(
                current_phase=InterviewPhase.ONBOARDING
            )
            logger.info(f"Created new session: {session.session_id}")
        
        # Save user message
        user_msg_obj = ChatMessage.objects.create(
            session=session,
            role='user',
            content=user_message
        )
        
        # Get conversation history (buffer - last N messages)
        buffer_size = settings.CHAT_HISTORY_BUFFER_SIZE
        recent_messages = session.messages.order_by('-timestamp')[:buffer_size]
        
        # Convert to history format (reverse order)
        conversation_history = [
            {'role': msg.role, 'content': msg.content}
            for msg in reversed(list(recent_messages))
        ]
        
        # Process message through state machine
        state_machine = get_state_machine()
        
        assistant_response, metadata = state_machine.process_user_message(
            session=session,
            user_message=user_message,
            conversation_history=conversation_history[:-1]  # Exclude current message
        )
        
        # Save assistant response
        assistant_msg_obj = ChatMessage.objects.create(
            session=session,
            role='assistant',
            content=assistant_response,
            tokens_used=metadata.get('extraction', {}).get('tokens_used'),
            response_time_ms=metadata.get('extraction', {}).get('response_time_ms'),
            sentiment_score=metadata.get('sentiment', {}).get('score')
        )
        
        # Update technical responses if in technical screening phase
        if session.current_phase == InterviewPhase.TECHNICAL_SCREENING:
            responses = session.technical_responses or {}
            question_index = len(responses)
            responses[f'question_{question_index}'] = {
                'question_index': question_index,
                'response': user_message,
                'timestamp': str(timezone.now())
            }
            session.technical_responses = responses
            session.save(update_fields=['technical_responses'])
        
        # Build response
        response_data = {
            'message': assistant_response,
            'role': 'assistant',
            'session_id': str(session.session_id),
            'current_phase': session.current_phase,
            'profile_completeness': session.get_profile_completeness(),
            'needs_intervention': session.needs_intervention,
            'metadata': metadata
        }
        
        response_serializer = ChatResponseSerializer(data=response_data)
        response_serializer.is_valid(raise_exception=True)
        
        logger.info(
            f"Processed message for session {session.session_id}. "
            f"Phase: {session.current_phase}"
        )
        
        return Response(response_serializer.data, status=status.HTTP_200_OK)
    
    except GroqServiceError as e:
        logger.error(f"Groq service error: {str(e)}", exc_info=True)
        
        # Get fallback response
        from talent_scout.services.groq_service import get_groq_service
        groq_service = get_groq_service()
        fallback_response = groq_service.get_fallback_response(
            context=session.current_phase if session else 'general'
        )
        
        # Save fallback response
        if session:
            ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=fallback_response
            )
        
        return Response({
            'message': fallback_response,
            'role': 'assistant',
            'session_id': str(session.session_id) if session else None,
            'current_phase': session.current_phase if session else 'onboarding',
            'profile_completeness': session.get_profile_completeness() if session else 0.0,
            'needs_intervention': False,
            'metadata': {'error': 'Groq API temporarily unavailable, using fallback'}
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Unexpected error in chat_message: {str(e)}", exc_info=True)
        
        return Response({
            'error': 'Internal Server Error',
            'detail': 'An unexpected error occurred. Please try again.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint.
    
    GET /api/health/
    
    Returns:
    {
        "status": "healthy",
        "timestamp": "2026-01-09T02:00:00Z",
        "groq_configured": true
    }
    """
    groq_configured = bool(settings.GROQ_API_KEY)
    
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'groq_configured': groq_configured,
        'version': '1.0.0'
    })
