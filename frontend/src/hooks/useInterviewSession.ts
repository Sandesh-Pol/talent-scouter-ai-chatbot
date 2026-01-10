/**
 * Custom React hooks for TalentScout API integration
 */

import { useState, useCallback, useEffect } from 'react';
import { api } from '@/services/api';
import type {
    ChatResponse,
    SessionStatusResponse,
    InterviewPhase,
    CandidateProfile,
    ChatMessage,
} from '@/types/api';
import { useToast } from '@/hooks/use-toast';

export interface UseInterviewSessionReturn {
    // Session state
    sessionId: string | null;
    currentPhase: InterviewPhase;
    profileCompleteness: number;
    candidateProfile: CandidateProfile;
    messages: ChatMessage[];

    // Loading states
    isInitializing: boolean;
    isSending: boolean;

    // Actions
    sendMessage: (content: string) => Promise<void>;
    refreshStatus: () => Promise<void>;

    // Computed
    needsIntervention: boolean;
}

/**
 * Main hook for managing interview session
 */
export const useInterviewSession = (): UseInterviewSessionReturn => {
    const { toast } = useToast();

    // State
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [currentPhase, setCurrentPhase] = useState<InterviewPhase>('onboarding');
    const [profileCompleteness, setProfileCompleteness] = useState<number>(0);
    const [candidateProfile, setCandidateProfile] = useState<CandidateProfile>({
        full_name: null,
        email: null,
        phone: null,
        location: null,
        years_experience: null,
        tech_stack: [],
        position_applied: null,
        experience_level: null,
    });
    const [messages, setMessages] = useState<ChatMessage[]>([]);
    const [needsIntervention, setNeedsIntervention] = useState(false);

    // Loading states
    const [isInitializing, setIsInitializing] = useState(true);
    const [isSending, setIsSending] = useState(false);

    /**
     * Initialize session on mount
     */
    useEffect(() => {
        const initializeSession = async () => {
            try {
                setIsInitializing(true);

                // Check if session exists in localStorage
                const storedSessionId = localStorage.getItem('talentscout_session_id');

                if (storedSessionId) {
                    // Try to restore existing session
                    console.log('Found stored session ID:', storedSessionId);
                    try {
                        const status = await api.getSessionStatus(storedSessionId);

                        // Restore session whether it's active or completed
                        // This allows viewing completed interviews
                        setSessionId(status.session_id);
                        setCurrentPhase(status.current_phase);
                        setProfileCompleteness(status.profile_completeness);
                        setCandidateProfile(status.candidate_profile);
                        setMessages(status.messages);
                        console.log('Session restored successfully:', status.session_id, 'Phase:', status.current_phase);
                        setIsInitializing(false);
                        return;
                    } catch (error) {
                        // Only clear localStorage if it's a 404 (session not found)
                        // Don't clear on network errors or rate limiting
                        const isNotFound = (error as any)?.status === 404;
                        
                        if (isNotFound) {
                            console.log('Stored session not found (404), will create new one');
                            localStorage.removeItem('talentscout_session_id');
                            localStorage.removeItem('talentscout_interview_flow');
                        } else {
                            // For other errors (network, rate limiting), keep the session ID
                            // and show an error without trying to create a new session
                            console.error('Failed to restore session:', error);
                            toast({
                                title: 'Connection Error',
                                description: error instanceof Error ? error.message : 'Failed to connect to server. Your session will be restored when connection is available.',
                                variant: 'destructive',
                            });
                            setIsInitializing(false);
                            return;
                        }
                    }
                }

                // Only create new session if no stored session or it was a 404
                console.log('Creating new session...');
                const response = await api.startSession();

                setSessionId(response.session_id);
                setCurrentPhase(response.current_phase);
                setProfileCompleteness(response.profile_completeness);

                // Add initial message
                setMessages([{
                    message_id: '1',
                    role: 'assistant',
                    content: response.message,
                    timestamp: new Date().toISOString(),
                }]);

                // Store session ID
                localStorage.setItem('talentscout_session_id', response.session_id);

            } catch (error) {
                console.error('Failed to initialize session:', error);
                toast({
                    title: 'Connection Error',
                    description: error instanceof Error ? error.message : 'Failed to connect to server',
                    variant: 'destructive',
                });
            } finally {
                setIsInitializing(false);
            }
        };

        initializeSession();
    }, [toast]);

    /**
     * Send a message to the AI interviewer
     */
    const sendMessage = useCallback(async (content: string) => {
        if (!sessionId || !content.trim()) return;

        try {
            setIsSending(true);

            // Add user message to UI immediately
            const userMessage: ChatMessage = {
                message_id: `user-${Date.now()}`,
                role: 'user',
                content,
                timestamp: new Date().toISOString(),
            };

            setMessages(prev => [...prev, userMessage]);

            // Send to backend
            const response: ChatResponse = await api.sendMessage({
                message: content,
                session_id: sessionId,
            });

            // Add assistant response
            const assistantMessage: ChatMessage = {
                message_id: `assistant-${Date.now()}`,
                role: 'assistant',
                content: response.message,
                timestamp: new Date().toISOString(),
            };

            setMessages(prev => [...prev, assistantMessage]);

            // Update session state
            setCurrentPhase(response.current_phase);
            setProfileCompleteness(response.profile_completeness);
            setNeedsIntervention(response.needs_intervention);

            // Refresh profile and phase info after a short delay to ensure backend has updated
            setTimeout(async () => {
                try {
                    const status = await api.getSessionStatus(sessionId);
                    setCandidateProfile(status.candidate_profile);
                    setCurrentPhase(status.current_phase);  // Update phase in case it changed
                } catch (err) {
                    console.error('Failed to refresh profile:', err);
                }
            }, 500);

        } catch (error) {
            console.error('Failed to send message:', error);
            toast({
                title: 'Message Failed',
                description: error instanceof Error ? error.message : 'Failed to send message',
                variant: 'destructive',
            });
        } finally {
            setIsSending(false);
        }
    }, [sessionId, toast]);

    /**
     * Refresh session status from server
     */
    const refreshStatus = useCallback(async () => {
        if (!sessionId) return;

        try {
            const status = await api.getSessionStatus(sessionId);
            setCurrentPhase(status.current_phase);
            setProfileCompleteness(status.profile_completeness);
            setCandidateProfile(status.candidate_profile);
            setMessages(status.messages);
        } catch (error) {
            console.error('Failed to refresh status:', error);
        }
    }, [sessionId]);

    return {
        sessionId,
        currentPhase,
        profileCompleteness,
        candidateProfile,
        messages,
        isInitializing,
        isSending,
        sendMessage,
        refreshStatus,
        needsIntervention,
    };
};

/**
 * Hook for health check
 */
export const useHealthCheck = () => {
    const [isHealthy, setIsHealthy] = useState<boolean | null>(null);
    const [isChecking, setIsChecking] = useState(false);

    const checkHealth = useCallback(async () => {
        try {
            setIsChecking(true);
            const response = await api.healthCheck();
            setIsHealthy(response.status === 'healthy' && response.groq_configured);
        } catch (error) {
            setIsHealthy(false);
            console.error('Health check failed:', error);
        } finally {
            setIsChecking(false);
        }
    }, []);

    useEffect(() => {
        checkHealth();
    }, [checkHealth]);

    return { isHealthy, isChecking, checkHealth };
};
