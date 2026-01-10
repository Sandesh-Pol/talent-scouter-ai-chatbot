"""
Django Admin Configuration for TalentScout

Provides a clean admin interface for managing interview sessions,
messages, and technical questions.
"""

from django.contrib import admin
from talent_scout.models import CandidateSession, ChatMessage, TechnicalQuestion


class ChatMessageInline(admin.TabularInline):
    """Inline display of chat messages within session"""
    model = ChatMessage
    extra = 0
    readonly_fields = ['message_id', 'role', 'content', 'timestamp', 'sentiment_score']
    fields = ['timestamp', 'role', 'content', 'sentiment_score']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


class TechnicalQuestionInline(admin.TabularInline):
    """Inline display of technical questions within session"""
    model = TechnicalQuestion
    extra = 0
    readonly_fields = ['question_id', 'question_text', 'difficulty_level']
    fields = ['question_text', 'difficulty_level']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(CandidateSession)
class CandidateSessionAdmin(admin.ModelAdmin):
    """Admin interface for candidate sessions"""
    
    list_display = [
        'session_id_short',
        'full_name',
        'email',
        'position_applied',
        'current_phase',
        'profile_completeness_percent',
        'is_active',
        'created_at',
        'message_count'
    ]
    
    list_filter = [
        'current_phase',
        'is_active',
        'experience_level',
        'created_at',
        'needs_intervention'
    ]
    
    search_fields = [
        'full_name',
        'email',
        'position_applied',
        'session_id'
    ]
    
    readonly_fields = [
        'session_id',
        'created_at',
        'updated_at',
        'completed_at',
        'experience_level',
        'profile_completeness_percent',
        'ip_address',
        'user_agent'
    ]
    
    fieldsets = (
        ('Session Info', {
            'fields': (
                'session_id',
                'current_phase',
                'is_active',
                'created_at',
                'updated_at',
                'completed_at'
            )
        }),
        ('Candidate Profile', {
            'fields': (
                'full_name',
                'email',
                'phone',
                'location',
                'years_experience',
                'experience_level',
                'tech_stack',
                'position_applied',
                'profile_completeness_percent'
            )
        }),
        ('Technical Screening', {
            'fields': (
                'generated_questions',
                'technical_responses'
            ),
            'classes': ('collapse',)
        }),
        ('Sentiment & Intervention', {
            'fields': (
                'sentiment_score',
                'needs_intervention'
            )
        }),
        ('Metadata', {
            'fields': (
                'ip_address',
                'user_agent'
            ),
            'classes': ('collapse',)
        })
    )
    
    inlines = [ChatMessageInline, TechnicalQuestionInline]
    
    def session_id_short(self, obj):
        """Display shortened session ID"""
        return str(obj.session_id)[:8] + '...'
    session_id_short.short_description = 'Session ID'
    
    def profile_completeness_percent(self, obj):
        """Display profile completeness as percentage"""
        return f"{obj.get_profile_completeness():.1f}%"
    profile_completeness_percent.short_description = 'Profile Complete'
    
    def message_count(self, obj):
        """Display count of messages"""
        return obj.messages.count()
    message_count.short_description = 'Messages'
    
    def get_queryset(self, request):
        """Optimize queryset with prefetch"""
        qs = super().get_queryset(request)
        return qs.prefetch_related('messages', 'questions')


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """Admin interface for chat messages"""
    
    list_display = [
        'message_id_short',
        'session_short',
        'role',
        'content_preview',
        'timestamp',
        'sentiment_score',
        'tokens_used'
    ]
    
    list_filter = [
        'role',
        'timestamp'
    ]
    
    search_fields = [
        'content',
        'session__full_name',
        'session__email'
    ]
    
    readonly_fields = [
        'message_id',
        'session',
        'role',
        'content',
        'timestamp',
        'tokens_used',
        'sentiment_score',
        'llm_model',
        'response_time_ms'
    ]
    
    fieldsets = (
        ('Message Info', {
            'fields': (
                'message_id',
                'session',
                'role',
                'content',
                'timestamp'
            )
        }),
        ('Analysis', {
            'fields': (
                'sentiment_score',
                'extracted_data'
            )
        }),
        ('LLM Metadata', {
            'fields': (
                'llm_model',
                'tokens_used',
                'response_time_ms'
            ),
            'classes': ('collapse',)
        })
    )
    
    def message_id_short(self, obj):
        return str(obj.message_id)[:8] + '...'
    message_id_short.short_description = 'Message ID'
    
    def session_short(self, obj):
        return str(obj.session.session_id)[:8] + '...'
    session_short.short_description = 'Session'
    
    def content_preview(self, obj):
        """Display preview of content"""
        return obj.content[:60] + '...' if len(obj.content) > 60 else obj.content
    content_preview.short_description = 'Content'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(TechnicalQuestion)
class TechnicalQuestionAdmin(admin.ModelAdmin):
    """Admin interface for technical questions"""
    
    list_display = [
        'question_id_short',
        'question_preview',
        'experience_level',
        'difficulty_level',
        'tech_stack_display',
        'created_at'
    ]
    
    list_filter = [
        'experience_level',
        'difficulty_level',
        'created_at'
    ]
    
    search_fields = [
        'question_text'
    ]
    
    readonly_fields = [
        'question_id',
        'session',
        'created_at'
    ]
    
    fieldsets = (
        ('Question Info', {
            'fields': (
                'question_id',
                'question_text',
                'tech_stack',
                'experience_level',
                'difficulty_level'
            )
        }),
        ('Metadata', {
            'fields': (
                'session',
                'quality_score',
                'created_at'
            )
        })
    )
    
    def question_id_short(self, obj):
        return str(obj.question_id)[:8] + '...'
    question_id_short.short_description = 'Question ID'
    
    def question_preview(self, obj):
        return obj.question_text[:80] + '...' if len(obj.question_text) > 80 else obj.question_text
    question_preview.short_description = 'Question'
    
    def tech_stack_display(self, obj):
        return ', '.join(obj.tech_stack[:3]) + ('...' if len(obj.tech_stack) > 3 else '')
    tech_stack_display.short_description = 'Technologies'


# Customize admin site header
admin.site.site_header = "TalentScout Admin"
admin.site.site_title = "TalentScout"
admin.site.index_title = "Hiring Assistant Administration"
