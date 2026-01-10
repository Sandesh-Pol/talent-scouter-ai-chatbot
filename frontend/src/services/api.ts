/**
 * TalentScout API Service
 * 
 * Handles all communication with the Django REST Framework backend.
 */

import type {
    StartSessionRequest,
    StartSessionResponse,
    ChatRequest,
    ChatResponse,
    SessionStatusResponse,
    SessionListItem,
    PaginatedResponse,
    HealthCheckResponse,
    APIError,
} from '@/types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
const API_TIMEOUT = import.meta.env.VITE_API_TIMEOUT || 30000;

class TalentScoutAPI {
    private baseURL: string;
    private timeout: number;

    constructor(baseURL: string = API_BASE_URL, timeout: number = API_TIMEOUT) {
        this.baseURL = baseURL;
        this.timeout = timeout;
    }

    /**
     * Generic fetch wrapper with error handling
     */
    private async fetchWithTimeout<T>(
        url: string,
        options: RequestInit = {}
    ): Promise<T> {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.timeout);

        try {
            const response = await fetch(`${this.baseURL}${url}`, {
                ...options,
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers,
                },
                signal: controller.signal,
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                const errorData: APIError = await response.json().catch(() => ({
                    error: response.statusText,
                    detail: `HTTP ${response.status}`,
                    error_code: 'HTTP_ERROR',
                }));

                const error = new Error(errorData.detail || errorData.error);
                // Attach status code to error for better handling
                (error as any).status = response.status;
                throw error;
            }

            return await response.json();
        } catch (error) {
            clearTimeout(timeoutId);

            if (error instanceof Error) {
                if (error.name === 'AbortError') {
                    throw new Error('Request timeout - please try again');
                }
                throw error;
            }

            throw new Error('An unexpected error occurred');
        }
    }

    /**
     * Health check endpoint
     */
    async healthCheck(): Promise<HealthCheckResponse> {
        return this.fetchWithTimeout<HealthCheckResponse>('/health/');
    }

    /**
     * Start a new interview session
     */
    async startSession(data?: StartSessionRequest): Promise<StartSessionResponse> {
        return this.fetchWithTimeout<StartSessionResponse>('/sessions/start/', {
            method: 'POST',
            body: data ? JSON.stringify(data) : undefined,
        });
    }

    /**
     * Send a chat message
     */
    async sendMessage(data: ChatRequest): Promise<ChatResponse> {
        return this.fetchWithTimeout<ChatResponse>('/chat/', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    /**
     * Get session status
     */
    async getSessionStatus(sessionId: string): Promise<SessionStatusResponse> {
        return this.fetchWithTimeout<SessionStatusResponse>(
            `/sessions/${sessionId}/status/`
        );
    }

    /**
     * List all sessions (paginated)
     */
    async listSessions(page: number = 1): Promise<PaginatedResponse<SessionListItem>> {
        return this.fetchWithTimeout<PaginatedResponse<SessionListItem>>(
            `/sessions/?page=${page}`
        );
    }

    /**
     * Get detailed session information
     */
    async getSession(sessionId: string): Promise<SessionStatusResponse> {
        return this.fetchWithTimeout<SessionStatusResponse>(`/sessions/${sessionId}/`);
    }
}

// Export singleton instance
export const api = new TalentScoutAPI();

// Export class for testing
export { TalentScoutAPI };
