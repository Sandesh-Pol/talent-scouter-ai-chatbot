"""
Interview State Machine

Manages the phase-based state machine for interview sessions:
1. Onboarding
2. Information Gathering
3. Technical Screening
4. Closing

Each phase has specific entry/exit conditions and behaviors.
"""

from typing import Dict, List, Optional, Tuple, Any
import logging
from django.conf import settings

from talent_scout.models import CandidateSession, InterviewPhase, ChatMessage
from talent_scout.schemas import CandidateProfileSchema
from talent_scout.services.prompt_orchestrator import get_prompt_orchestrator
from talent_scout.services.sentiment_service import get_sentiment_analyzer

logger = logging.getLogger(__name__)


class InterviewStateMachine:
    """
    State machine controller for interview flow.
    
    Manages phase transitions and determines appropriate actions
    based on current state and candidate data.
    """
    
    def __init__(self):
        """Initialize with services"""
        self.prompt_orchestrator = get_prompt_orchestrator()
        self.sentiment_analyzer = get_sentiment_analyzer()
        self.phases = settings.INTERVIEW_PHASES
    
    def get_initial_message(self) -> str:
        """
        Get the initial onboarding message.
        
        Returns:
            Welcome message for new candidates
        """
        return (
            "Hello! 👋 Welcome to TalentScout. I'm your AI interviewer, "
            "and I'm excited to learn more about you today.\n\n"
            "Let's start with a quick introduction. Could you please tell me "
            "your full name and the position you're applying for?"
        )
    
    def process_user_message(
        self,
        session: CandidateSession,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Main entry point for processing user messages.
        
        This orchestrates the entire flow:
        1. Analyze sentiment
        2. Extract information
        3. Update session state
        4. Determine next action based on phase
        5. Generate appropriate response
        
        Args:
            session: Current candidate session
            user_message: User's message
            conversation_history: Recent chat history (buffer)
        
        Returns:
            Tuple of (assistant_response, metadata)
        """
        metadata = {}
        
        try:
            # Step 1: Analyze sentiment
            sentiment = self.sentiment_analyzer.analyze(user_message)
            metadata['sentiment'] = sentiment.model_dump()
            
            # Update session sentiment
            session.sentiment_score = sentiment.score
            
            # Check if intervention needed
            if sentiment.intervention_needed:
                session.needs_intervention = True
                logger.warning(f"Intervention needed for session {session.session_id}")
                
                # Return intervention response
                response = sentiment.suggested_response or (
                    "I want to make sure we're on the same page. "
                    "Is there anything I can clarify for you?"
                )
                
                session.save(update_fields=['sentiment_score', 'needs_intervention'])
                return response, metadata
            
            # Reset intervention flag if sentiment improved
            if session.needs_intervention and sentiment.score > 0:
                session.needs_intervention = False
            
            # Step 2: Extract information (in all phases)
            current_profile = self._get_current_profile_dict(session)
            
            extracted_profile, extraction_meta = self.prompt_orchestrator.extract_candidate_info(
                user_message=user_message,
                current_profile=current_profile,
                conversation_history=conversation_history
            )
            
            metadata['extraction'] = extraction_meta
            
            # Step 3: Update session with extracted data
            self._update_session_profile(session, extracted_profile)
            
            # Step 4: Process based on current phase
            response = self._process_by_phase(
                session=session,
                extracted_profile=extracted_profile,
                conversation_history=conversation_history,
                metadata=metadata
            )
            
            # Save session
            session.save()
            
            return response, metadata
        
        except Exception as e:
            logger.error(f"Error processing user message: {str(e)}", exc_info=True)
            return (
                "I apologize, but I encountered an issue processing your response. "
                "Could you please try rephrasing that?"
            ), {"error": str(e)}
    
    def _process_by_phase(
        self,
        session: CandidateSession,
        extracted_profile: CandidateProfileSchema,
        conversation_history: Optional[List[Dict[str, str]]],
        metadata: Dict[str, Any]
    ) -> str:
        """
        Process message based on current interview phase.
        
        Args:
            session: Current session
            extracted_profile: Updated profile
            conversation_history: Chat history
            metadata: Metadata dict to update
        
        Returns:
            Assistant's response
        """
        current_phase = session.current_phase
        
        if current_phase == InterviewPhase.ONBOARDING:
            return self._handle_onboarding(session, extracted_profile, conversation_history)
        
        elif current_phase == InterviewPhase.INFORMATION_GATHERING:
            return self._handle_information_gathering(session, extracted_profile, conversation_history)
        
        elif current_phase == InterviewPhase.TECHNICAL_SCREENING:
            return self._handle_technical_screening(session, extracted_profile, conversation_history, metadata)
        
        elif current_phase == InterviewPhase.CLOSING:
            return self._handle_closing(session)
        
        else:
            logger.error(f"Unknown phase: {current_phase}")
            return "I'm not sure what to ask next. Let me check my notes."
    
    def _handle_onboarding(
        self,
        session: CandidateSession,
        profile: CandidateProfileSchema,
        history: Optional[List[Dict[str, str]]]
    ) -> str:
        """Handle onboarding phase"""
        # Check if we have at least name or position
        if profile.full_name or profile.position_applied:
            # Move to information gathering
            session.advance_phase()
            
            # Generate acknowledgment and transition
            name_part = f"Nice to meet you, {profile.full_name}! " if profile.full_name else "Great! "
            position_part = f"I see you're interested in the {profile.position_applied} position. " if profile.position_applied else ""
            
            response = (
                f"{name_part}{position_part}"
                f"Let's learn more about your background. "
            )
            
            # Ask for missing critical info
            follow_up, _ = self.prompt_orchestrator.generate_recruiter_followup(
                current_profile=profile,
                conversation_history=history
            )
            
            return response + follow_up
        else:
            # Still in onboarding, ask again
            return (
                "Thank you for that! To get started, I'll need your name "
                "and the position you're applying for."
            )
    
    def _handle_information_gathering(
        self,
        session: CandidateSession,
        profile: CandidateProfileSchema,
        history: Optional[List[Dict[str, str]]]
    ) -> str:
        """Handle information gathering phase"""
        # Check if profile is complete
        is_complete, missing_fields = session.check_phase_completion()
        
        if is_complete:
            # Profile complete! Move to technical screening
            session.advance_phase()
            
            # Generate technical questions
            questions, tech_meta = self.prompt_orchestrator.generate_technical_questions(
                tech_stack=session.tech_stack,
                experience_level=session.experience_level or 'mid',
                position=session.position_applied or 'Software Engineer',
                count=settings.TECHNICAL_QUESTIONS_COUNT
            )
            
            # Save questions to session
            session.generated_questions = questions
            session.save(update_fields=['generated_questions'])
            
            # Return transition message with first question
            first_question = questions[0]['question'] if questions else "Tell me about a recent project."
            
            return (
                f"Excellent! Thank you for sharing that information, {profile.full_name}. "
                f"Now let's move on to some technical questions to understand your skills better.\n\n"
                f"**Question 1 of {len(questions)}:** {first_question}"
            )
        else:
            # Generate follow-up for missing fields
            follow_up, _ = self.prompt_orchestrator.generate_recruiter_followup(
                current_profile=profile,
                conversation_history=history
            )
            
            return follow_up
    
    def _handle_technical_screening(
        self,
        session: CandidateSession,
        profile: CandidateProfileSchema,
        history: Optional[List[Dict[str, str]]],
        metadata: Dict[str, Any]
    ) -> str:
        """Handle technical screening phase"""
        # Track responses
        questions = session.generated_questions or []
        responses = session.technical_responses or {}
        
        # Count how many questions answered
        answered_count = len(responses)
        
        if answered_count >= len(questions):
            # All questions answered, move to closing
            session.advance_phase()
            
            return (
                f"Thank you so much for your thoughtful answers, {session.full_name}! "
                f"You've completed the technical portion of our interview.\n\n"
                f"Before we wrap up, do you have any questions for us about the role, "
                f"the team, or the company?"
            )
        else:
            # Ask next question
            next_question_index = answered_count
            next_question = questions[next_question_index]['question']
            
            # Acknowledge previous response
            acknowledgments = [
                "Great answer! ",
                "Interesting perspective! ",
                "Thank you for that detailed response! ",
                "I appreciate the insight! ",
                "Excellent! "
            ]
            
            ack = acknowledgments[answered_count % len(acknowledgments)]
            
            return (
                f"{ack}Let's continue.\n\n"
                f"**Question {next_question_index + 1} of {len(questions)}:** {next_question}"
            )
    
    def _handle_closing(self, session: CandidateSession) -> str:
        """Handle closing phase"""
        # Mark session as completed
        if session.is_active:
            session.is_active = False
            from django.utils import timezone
            session.completed_at = timezone.now()
            session.save(update_fields=['is_active', 'completed_at'])
        
        return (
            f"Thank you so much for your time today, {session.full_name}! "
            f"We really enjoyed learning about your background and experience. "
            f"Our team will review your responses and get back to you within the next few days.\n\n"
            f"If you have any questions in the meantime, feel free to reach out at "
            f"the email you provided. Best of luck, and we hope to speak with you soon! 🎉"
        )
    
    def _get_current_profile_dict(self, session: CandidateSession) -> Dict[str, Any]:
        """Extract current profile as dict from session"""
        return {
            'full_name': session.full_name,
            'email': session.email,
            'phone': session.phone,
            'location': session.location,
            'years_experience': session.years_experience,
            'tech_stack': session.tech_stack or [],
            'position_applied': session.position_applied
        }
    
    def _update_session_profile(
        self,
        session: CandidateSession,
        profile: CandidateProfileSchema
    ) -> None:
        """Update session with extracted profile data"""
        profile_dict = profile.model_dump()
        
        # Only update non-null values
        for field, value in profile_dict.items():
            if value is not None and value != "" and value != []:
                setattr(session, field, value)


# Singleton instance
_state_machine_instance = None


def get_state_machine() -> InterviewStateMachine:
    """Get singleton instance of InterviewStateMachine"""
    global _state_machine_instance
    
    if _state_machine_instance is None:
        _state_machine_instance = InterviewStateMachine()
    
    return _state_machine_instance
