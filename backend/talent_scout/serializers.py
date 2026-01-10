"""
Django REST Framework Serializers

Serializers for converting Django models to/from JSON
for the React frontend.
"""

from rest_framework import serializers
from talent_scout.models import CandidateSession, ChatMessage, TechnicalQuestion
from django.utils import timezone


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages"""
    
    class Meta:
        model = ChatMessage
        fields = [
            'message_id',
            'role',
            'content',
            'timestamp',
            'sentiment_score',
            'tokens_used',
            'response_time_ms'
        ]
        read_only_fields = [
            'message_id',
            'timestamp',
            'sentiment_score',
            'tokens_used',
            'response_time_ms'
        ]


class TechnicalQuestionSerializer(serializers.ModelSerializer):
    """Serializer for technical questions"""
    
    class Meta:
        model = TechnicalQuestion
        fields = [
            'question_id',
            'question_text',
            'tech_stack',
            'experience_level',
            'difficulty_level',
            'created_at'
        ]
        read_only_fields = ['question_id', 'created_at']


class CandidateSessionSerializer(serializers.ModelSerializer):
    """Serializer for candidate sessions"""
    
    messages = ChatMessageSerializer(many=True, read_only=True)
    questions = TechnicalQuestionSerializer(many=True, read_only=True)
    profile_completeness = serializers.SerializerMethodField()
    
    class Meta:
        model = CandidateSession
        fields = [
            'session_id',
            'created_at',
            'updated_at',
            'completed_at',
            'current_phase',
            'full_name',
            'email',
            'phone',
            'location',
            'years_experience',
            'tech_stack',
            'position_applied',
            'experience_level',
            'generated_questions',
            'technical_responses',
            'is_active',
            'sentiment_score',
            'needs_intervention',
            'messages',
            'questions',
            'profile_completeness'
        ]
        read_only_fields = [
            'session_id',
            'created_at',
            'updated_at',
            'completed_at',
            'experience_level',
            'sentiment_score',
            'needs_intervention',
            'profile_completeness'
        ]
    
    def get_profile_completeness(self, obj):
        """Calculate profile completion percentage"""
        return obj.get_profile_completeness()


class CandidateSessionListSerializer(serializers.ModelSerializer):
    """Simplified serializer for session lists"""
    
    profile_completeness = serializers.SerializerMethodField()
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CandidateSession
        fields = [
            'session_id',
            'created_at',
            'updated_at',
            'current_phase',
            'full_name',
            'email',
            'position_applied',
            'is_active',
            'profile_completeness',
            'message_count'
        ]
    
    def get_profile_completeness(self, obj):
        return obj.get_profile_completeness()
    
    def get_message_count(self, obj):
        return obj.messages.count()


class ChatRequestSerializer(serializers.Serializer):
    """Serializer for incoming chat messages"""
    
    message = serializers.CharField(max_length=5000, required=True)
    session_id = serializers.UUIDField(required=False, allow_null=True)
    
    def validate_message(self, value):
        """Validate message is not empty"""
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty")
        return value.strip()


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat responses"""
    
    message = serializers.CharField()
    role = serializers.CharField(default='assistant')
    session_id = serializers.UUIDField()
    current_phase = serializers.CharField()
    profile_completeness = serializers.FloatField()
    needs_intervention = serializers.BooleanField(default=False)
    metadata = serializers.DictField(required=False)


class SessionStatusSerializer(serializers.Serializer):
    """Serializer for session status responses"""
    
    session_id = serializers.UUIDField()
    current_phase = serializers.CharField()
    profile_completeness = serializers.FloatField()
    is_active = serializers.BooleanField()
    candidate_profile = serializers.DictField()
    message_count = serializers.IntegerField()
    messages = ChatMessageSerializer(many=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
