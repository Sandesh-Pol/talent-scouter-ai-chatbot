"""
Pydantic Schemas for TalentScout

These schemas enforce strict typing and validation for:
1. LLM responses (preventing hallucinations)
2. User input validation
3. API request/response validation
"""

from pydantic import BaseModel, Field, EmailStr, validator, field_validator
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
import re


class CandidateProfileSchema(BaseModel):
    """
    Pydantic schema for candidate profile extraction.
    
    This ensures the LLM returns valid JSON with proper field types.
    Used by the "Extractor" function.
    """
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')
    location: Optional[str] = Field(None, max_length=255)
    years_experience: Optional[int] = Field(None, ge=0, le=70)
    tech_stack: List[str] = Field(default_factory=list)
    position_applied: Optional[str] = Field(None, max_length=255)
    
    @field_validator('tech_stack')
    @classmethod
    def validate_tech_stack(cls, v):
        """Ensure tech_stack is a list of non-empty strings"""
        if not isinstance(v, list):
            raise ValueError("tech_stack must be a list")
        # Remove empty strings and strip whitespace
        return [tech.strip() for tech in v if tech and tech.strip()]
    
    @field_validator('years_experience')
    @classmethod
    def validate_years(cls, v):
        """Ensure years_experience is reasonable"""
        if v is not None and (v < 0 or v > 70):
            raise ValueError("years_experience must be between 0 and 70")
        return v
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        """Validate phone number format"""
        if v is None:
            return v
        # Remove common separators
        cleaned = re.sub(r'[\s\-\(\)]', '', v)
        # Check if it matches international or local format
        if not re.match(r'^\+?1?\d{9,15}$', cleaned):
            raise ValueError("Invalid phone number format")
        return cleaned
    
    class Config:
        json_schema_extra = {
            "example": {
                "full_name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1234567890",
                "location": "San Francisco, CA",
                "years_experience": 5,
                "tech_stack": ["Python", "Django", "React"],
                "position_applied": "Senior Backend Engineer"
            }
        }


class TechnicalQuestionSchema(BaseModel):
    """Schema for a single technical question"""
    question: str = Field(..., min_length=10)
    expected_topics: List[str] = Field(default_factory=list)
    difficulty: Literal['easy', 'medium', 'hard', 'expert'] = 'medium'
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "Explain the difference between synchronous and asynchronous programming in Python.",
                "expected_topics": ["async/await", "asyncio", "event loop"],
                "difficulty": "medium"
            }
        }


class TechnicalQuestionsResponseSchema(BaseModel):
    """
    Schema for LLM-generated technical questions.
    
    Enforces that the LLM returns exactly the number of questions
    we requested, preventing incomplete responses.
    """
    questions: List[TechnicalQuestionSchema] = Field(..., min_length=3, max_length=10)
    rationale: Optional[str] = Field(None, description="Why these questions were chosen")
    
    @field_validator('questions')
    @classmethod
    def validate_questions(cls, v):
        """Ensure we have unique questions"""
        if len(v) != len(set(q.question for q in v)):
            raise ValueError("Questions must be unique")
        return v


class RecruiterFollowUpSchema(BaseModel):
    """
    Schema for recruiter follow-up questions.
    
    Ensures the LLM identifies missing fields and generates
    appropriate follow-up questions.
    """
    missing_fields: List[str] = Field(default_factory=list)
    follow_up_question: str = Field(..., min_length=10)
    tone: Literal['friendly', 'professional', 'encouraging', 'clarifying'] = 'friendly'
    
    class Config:
        json_schema_extra = {
            "example": {
                "missing_fields": ["email", "years_experience"],
                "follow_up_question": "Great! Before we proceed, could you please share your email address and how many years of professional experience you have?",
                "tone": "friendly"
            }
        }


class SentimentAnalysisSchema(BaseModel):
    """Schema for sentiment analysis results"""
    score: float = Field(..., ge=-1.0, le=1.0)
    magnitude: float = Field(..., ge=0.0, le=1.0)
    is_frustrated: bool = False
    is_confused: bool = False
    intervention_needed: bool = False
    suggested_response: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "score": -0.4,
                "magnitude": 0.7,
                "is_frustrated": True,
                "is_confused": False,
                "intervention_needed": True,
                "suggested_response": "I sense some frustration. Would you like me to clarify anything or approach this differently?"
            }
        }


class ChatMessageSchema(BaseModel):
    """Schema for chat message API requests"""
    message: str = Field(..., min_length=1, max_length=5000)
    session_id: Optional[str] = None
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v):
        """Ensure message is not just whitespace"""
        if not v.strip():
            raise ValueError("Message cannot be empty or just whitespace")
        return v.strip()


class ChatResponseSchema(BaseModel):
    """Schema for chat message API responses"""
    message: str
    role: Literal['assistant', 'user', 'system']
    session_id: str
    current_phase: str
    profile_completeness: float
    needs_intervention: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Thank you for sharing that! Could you tell me more about your technical skills?",
                "role": "assistant",
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "current_phase": "information_gathering",
                "profile_completeness": 60.0,
                "needs_intervention": False
            }
        }


class SessionStatusSchema(BaseModel):
    """Schema for session status responses"""
    session_id: str
    current_phase: str
    profile_completeness: float
    is_active: bool
    candidate_profile: Dict[str, Any]
    message_count: int
    created_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "123e4567-e89b-12d3-a456-426614174000",
                "current_phase": "information_gathering",
                "profile_completeness": 75.0,
                "is_active": True,
                "candidate_profile": {
                    "full_name": "John Doe",
                    "email": "john@example.com",
                    "years_experience": 5,
                    "tech_stack": ["Python", "Django"]
                },
                "message_count": 12,
                "created_at": "2026-01-09T02:00:00Z"
            }
        }


class LLMExtractionRequestSchema(BaseModel):
    """Internal schema for LLM extraction requests"""
    user_message: str
    current_profile: CandidateProfileSchema
    conversation_history: List[Dict[str, str]] = Field(default_factory=list, max_length=10)
    
    class Config:
        json_schema_extra = {
            "example": {
                "user_message": "I'm a senior Python developer with 7 years of experience",
                "current_profile": {
                    "full_name": None,
                    "email": None,
                    "years_experience": None,
                    "tech_stack": []
                },
                "conversation_history": [
                    {"role": "assistant", "content": "What's your background?"},
                    {"role": "user", "content": "I'm a Python developer"}
                ]
            }
        }


class ErrorResponseSchema(BaseModel):
    """Standard error response schema"""
    error: str
    detail: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Validation Error",
                "detail": "Email format is invalid",
                "error_code": "VALIDATION_ERROR",
                "timestamp": "2026-01-09T02:00:00Z"
            }
        }


# Validation utility functions
def validate_email_format(email: str) -> bool:
    """Validate email using regex"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone_format(phone: str) -> bool:
    """Validate phone number using regex"""
    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)]', '', phone)
    pattern = r'^\+?1?\d{9,15}$'
    return bool(re.match(pattern, cleaned))


def sanitize_tech_stack(tech_list: List[str]) -> List[str]:
    """
    Sanitize and deduplicate tech stack list.
    Converts to title case and removes duplicates.
    """
    sanitized = []
    seen = set()
    
    for tech in tech_list:
        # Clean and normalize
        tech_clean = tech.strip()
        tech_lower = tech_clean.lower()
        
        # Skip if empty or already seen
        if not tech_clean or tech_lower in seen:
            continue
        
        seen.add(tech_lower)
        # Convert to title case for consistency
        sanitized.append(tech_clean.title())
    
    return sanitized
