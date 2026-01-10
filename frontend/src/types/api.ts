/**
 * TypeScript types matching Django backend API responses
 */

export type InterviewPhase =
    | 'onboarding'
    | 'information_gathering'
    | 'technical_screening'
    | 'closing';

export type MessageRole = 'assistant' | 'user' | 'system';

export type ExperienceLevel = 'junior' | 'mid' | 'senior' | 'lead' | 'architect';

export interface CandidateProfile {
    full_name: string | null;
    email: string | null;
    phone: string | null;
    location: string | null;
    years_experience: number | null;
    tech_stack: string[];
    position_applied: string | null;
    experience_level: ExperienceLevel | null;
}

export interface ChatMessage {
    message_id: string;
    role: MessageRole;
    content: string;
    timestamp: string;
    sentiment_score?: number | null;
    tokens_used?: number | null;
    response_time_ms?: number | null;
}

export interface TechnicalQuestion {
    question: string;
    expected_topics: string[];
    difficulty: 'easy' | 'medium' | 'hard' | 'expert';
}

export interface SentimentAnalysis {
    score: number;
    magnitude: number;
    is_frustrated: boolean;
    is_confused: boolean;
    intervention_needed: boolean;
    suggested_response?: string | null;
}

export interface SessionMetadata {
    sentiment?: SentimentAnalysis;
    extraction?: {
        tokens_used?: number;
        response_time_ms?: number;
        model?: string;
    };
}

// API Request Types
export interface StartSessionRequest {
    ip_address?: string;
    user_agent?: string;
}

export interface ChatRequest {
    message: string;
    session_id?: string;
}

// API Response Types
export interface StartSessionResponse {
    session_id: string;
    message: string;
    current_phase: InterviewPhase;
    profile_completeness: number;
}

export interface ChatResponse {
    message: string;
    role: MessageRole;
    session_id: string;
    current_phase: InterviewPhase;
    profile_completeness: number;
    needs_intervention: boolean;
    metadata?: SessionMetadata;
}

export interface SessionStatusResponse {
    session_id: string;
    current_phase: InterviewPhase;
    profile_completeness: number;
    is_active: boolean;
    candidate_profile: CandidateProfile;
    message_count: number;
    messages: ChatMessage[];
    created_at: string;
    updated_at: string;
}

export interface SessionListItem {
    session_id: string;
    created_at: string;
    updated_at: string;
    current_phase: InterviewPhase;
    full_name: string | null;
    email: string | null;
    position_applied: string | null;
    is_active: boolean;
    profile_completeness: number;
    message_count: number;
}

export interface PaginatedResponse<T> {
    count: number;
    next: string | null;
    previous: string | null;
    results: T[];
}

export interface HealthCheckResponse {
    status: 'healthy' | 'unhealthy';
    timestamp: string;
    groq_configured: boolean;
    version: string;
}

export interface APIError {
    error: string;
    detail?: string;
    error_code?: string;
    timestamp?: string;
}

// Utility type for API responses
export type APIResponse<T> = {
    data: T;
    error: null;
} | {
    data: null;
    error: APIError;
};
