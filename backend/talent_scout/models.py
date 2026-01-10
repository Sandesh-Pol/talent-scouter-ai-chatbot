"""
TalentScout Django Models

These models store candidate interview sessions, messages, and profiles.
All PII (Personally Identifiable Information) is handled securely in-memory
and stored with proper data protection measures.
"""

from django.db import models
from django.utils import timezone
import uuid
import json


class InterviewPhase(models.TextChoices):
    """Interview phase enumeration"""
    ONBOARDING = 'onboarding', 'Onboarding'
    INFORMATION_GATHERING = 'information_gathering', 'Information Gathering'
    TECHNICAL_SCREENING = 'technical_screening', 'Technical Screening'
    CLOSING = 'closing', 'Closing'


class MessageRole(models.TextChoices):
    """Message role enumeration"""
    ASSISTANT = 'assistant', 'Assistant'
    USER = 'user', 'User'
    SYSTEM = 'system', 'System'


class CandidateSession(models.Model):
    """
    Represents a single candidate interview session.
    
    This model tracks the entire interview lifecycle and maintains
    the state machine for phase transitions.
    """
    
    # Primary key - Using UUID for enhanced security and non-sequential IDs
    session_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique session identifier"
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Session creation timestamp"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update timestamp"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Session completion timestamp"
    )
    
    # Phase Management - State Machine
    current_phase = models.CharField(
        max_length=50,
        choices=InterviewPhase.choices,
        default=InterviewPhase.ONBOARDING,
        help_text="Current interview phase"
    )
    
    # Candidate Profile Data (PII - Handle with care)
    # NOTE: In production, consider encrypting these fields
    full_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Candidate's full name"
    )
    email = models.EmailField(
        blank=True,
        null=True,
        help_text="Candidate's email address"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Candidate's phone number"
    )
    location = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Candidate's location"
    )
    years_experience = models.IntegerField(
        null=True,
        blank=True,
        help_text="Years of professional experience"
    )
    
    # Technical Details
    tech_stack = models.JSONField(
        default=list,
        blank=True,
        help_text="List of technologies the candidate knows"
    )
    position_applied = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Position the candidate is applying for"
    )
    experience_level = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        choices=[
            ('junior', 'Junior'),
            ('mid', 'Mid-Level'),
            ('senior', 'Senior'),
            ('lead', 'Lead'),
            ('architect', 'Architect')
        ],
        help_text="Derived experience level based on years"
    )
    
    # Technical Screening Data
    generated_questions = models.JSONField(
        default=list,
        blank=True,
        help_text="AI-generated technical questions for this candidate"
    )
    technical_responses = models.JSONField(
        default=dict,
        blank=True,
        help_text="Candidate's responses to technical questions"
    )
    
    # MCQ Screening Data (5+3 Strategy)
    mcq_questions = models.JSONField(
        default=dict,
        blank=True,
        help_text="Generated MCQ questions per skill (5 per skill)"
    )
    mcq_answers = models.JSONField(
        default=dict,
        blank=True,
        help_text="Candidate's MCQ answers and evaluation results"
    )
    objective_questions = models.JSONField(
        default=list,
        blank=True,
        help_text="Generated objective (open-ended) questions (3 total)"
    )
    objective_evaluations = models.JSONField(
        default=list,
        blank=True,
        help_text="LLM evaluations of objective question answers"
    )
    skill_ratings = models.JSONField(
        default=dict,
        blank=True,
        help_text="5-star ratings for each skill based on MCQ and objective performance"
    )
    
    # Session Metadata
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the session is currently active"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of the candidate (for security audit)"
    )
    user_agent = models.TextField(
        blank=True,
        null=True,
        help_text="Browser user agent"
    )
    
    # Sentiment Tracking
    sentiment_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Overall sentiment score (-1 to 1)"
    )
    needs_intervention = models.BooleanField(
        default=False,
        help_text="Flag if candidate seems frustrated/confused"
    )
    
    class Meta:
        db_table = 'candidate_sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['email']),
            models.Index(fields=['current_phase']),
            models.Index(fields=['is_active']),
        ]
        verbose_name = 'Candidate Session'
        verbose_name_plural = 'Candidate Sessions'
    
    def __str__(self):
        name = self.full_name or f"Anonymous-{str(self.session_id)[:8]}"
        return f"{name} - {self.get_current_phase_display()}"
    
    def get_profile_completeness(self):
        """Calculate profile completion percentage"""
        required_fields = ['full_name', 'email', 'years_experience', 'tech_stack', 'position_applied']
        completed = sum(1 for field in required_fields if getattr(self, field))
        return (completed / len(required_fields)) * 100
    
    def advance_phase(self):
        """Advance to the next interview phase"""
        phases = list(InterviewPhase.values)
        current_index = phases.index(self.current_phase)
        
        if current_index < len(phases) - 1:
            self.current_phase = phases[current_index + 1]
            self.save(update_fields=['current_phase', 'updated_at'])
            return True
        return False
    
    def check_phase_completion(self):
        """
        Check if current phase requirements are met.
        Returns (is_complete, missing_fields)
        """
        if self.current_phase == InterviewPhase.ONBOARDING:
            # Just needs to acknowledge the greeting
            return True, []
        
        elif self.current_phase == InterviewPhase.INFORMATION_GATHERING:
            required = ['full_name', 'email', 'years_experience', 'tech_stack', 'position_applied']
            missing = [f for f in required if not getattr(self, f)]
            return len(missing) == 0, missing
        
        elif self.current_phase == InterviewPhase.TECHNICAL_SCREENING:
            # Check if questions generated and some responses received
            has_questions = len(self.generated_questions) > 0
            has_responses = len(self.technical_responses) > 0
            return has_questions and has_responses, []
        
        elif self.current_phase == InterviewPhase.CLOSING:
            return True, []
        
        return False, []
    
    def derive_experience_level(self):
        """Automatically derive experience level from years"""
        if self.years_experience is None:
            return None
        
        if self.years_experience < 2:
            return 'junior'
        elif self.years_experience < 5:
            return 'mid'
        elif self.years_experience < 8:
            return 'senior'
        elif self.years_experience < 12:
            return 'lead'
        else:
            return 'architect'
    
    def save(self, *args, **kwargs):
        """Override save to auto-derive experience level"""
        if self.years_experience is not None:
            self.experience_level = self.derive_experience_level()
        super().save(*args, **kwargs)


class ChatMessage(models.Model):
    """
    Represents individual chat messages in an interview session.
    
    This model maintains the conversation history for context
    and implements the Summary Buffer Memory pattern.
    """
    
    message_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    session = models.ForeignKey(
        CandidateSession,
        on_delete=models.CASCADE,
        related_name='messages',
        help_text="Associated interview session"
    )
    
    role = models.CharField(
        max_length=20,
        choices=MessageRole.choices,
        help_text="Who sent this message"
    )
    
    content = models.TextField(
        help_text="Message content"
    )
    
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text="When the message was sent"
    )
    
    # Metadata
    tokens_used = models.IntegerField(
        null=True,
        blank=True,
        help_text="Tokens consumed by this message (for cost tracking)"
    )
    
    sentiment_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Sentiment score for this message (-1 to 1)"
    )
    
    # LLM Response Metadata
    llm_model = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="LLM model used for generation"
    )
    
    response_time_ms = models.IntegerField(
        null=True,
        blank=True,
        help_text="LLM response time in milliseconds"
    )
    
    # Extracted data (for information gathering phase)
    extracted_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Structured data extracted from user message"
    )
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['session', 'timestamp']),
            models.Index(fields=['role']),
        ]
        verbose_name = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
    
    def __str__(self):
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"{self.role}: {preview}"


class TechnicalQuestion(models.Model):
    """
    Stores generated technical questions for reusability and tracking.
    
    This allows the system to build a question bank and track
    which questions work best for different experience levels.
    """
    
    question_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    session = models.ForeignKey(
        CandidateSession,
        on_delete=models.CASCADE,
        related_name='questions',
        null=True,
        blank=True,
        help_text="Session this question was generated for"
    )
    
    question_text = models.TextField(
        help_text="The technical question"
    )
    
    tech_stack = models.JSONField(
        default=list,
        help_text="Technologies this question targets"
    )
    
    experience_level = models.CharField(
        max_length=50,
        help_text="Target experience level"
    )
    
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('easy', 'Easy'),
            ('medium', 'Medium'),
            ('hard', 'Hard'),
            ('expert', 'Expert')
        ],
        default='medium'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Quality metrics (optional for future ML improvements)
    quality_score = models.FloatField(
        null=True,
        blank=True,
        help_text="Question quality score (0-1)"
    )
    
    class Meta:
        db_table = 'technical_questions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['experience_level']),
            models.Index(fields=['difficulty_level']),
        ]
        verbose_name = 'Technical Question'
        verbose_name_plural = 'Technical Questions'
    
    def __str__(self):
        preview = self.question_text[:60] + "..." if len(self.question_text) > 60 else self.question_text
        return f"{self.experience_level} - {preview}"
