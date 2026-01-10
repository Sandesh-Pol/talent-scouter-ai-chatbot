import { motion } from "framer-motion";
import { Plus, MessageSquare, History, Menu, X, Sparkles, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useState, useEffect } from "react";

interface NavigationSidebarProps {
    onNewChat?: () => void;
    isMobile?: boolean;
    onClose?: () => void;
}

export const NavigationSidebar = ({ onNewChat, isMobile = false, onClose }: NavigationSidebarProps) => {
    const [isCollapsed, setIsCollapsed] = useState(isMobile);
    const [sessions, setSessions] = useState<any[]>([]);
    const [isLoadingSessions, setIsLoadingSessions] = useState(false);

    const handleNewChat = () => {
        if (onNewChat) {
            onNewChat();
        } else {
            localStorage.removeItem('talentscout_session_id');
            window.location.reload();
        }
    };

    useEffect(() => {
        fetchSessions();
    }, []);

    const fetchSessions = async () => {
        try {
            setIsLoadingSessions(true);
            const response = await fetch('http://localhost:8000/api/sessions/', {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
            });

            if (response.ok) {
                const data = await response.json();

                // FIX: Ensure data is an array before sorting
                // If your Django/FastAPI returns { "sessions": [...] }, use data.sessions
                const sessionsArray = Array.isArray(data) ? data : (data.results || data.sessions || []);

                const sortedSessions = [...sessionsArray]
                    .sort((a: any, b: any) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
                    .slice(0, 15);

                setSessions(sortedSessions);
            } else {
                setSessions([]);
            }
        } catch (error) {
            console.error('Failed to fetch sessions:', error);
            setSessions([]);
        } finally {
            setIsLoadingSessions(false);
        }
    };

    const loadSession = (sessionId: string) => {
        localStorage.setItem('talentscout_session_id', sessionId);
        window.location.reload();
    };

    const formatRelativeTime = (dateString: string) => {
        const date = new Date(dateString);
        const now = new Date();
        const diffMs = now.getTime() - date.getTime();
        const diffMins = Math.floor(diffMs / 60000);
        const diffHours = Math.floor(diffMins / 60);

        if (diffMins < 1) return 'Just now';
        if (diffMins < 60) return `${diffMins}m ago`;
        if (diffHours < 24) return `${diffHours}h ago`;
        return date.toLocaleDateString();
    };

    // --- Collapsed State ---
    if (isCollapsed && !isMobile) {
        return (
            <aside className="h-screen w-16 glass-panel border-r border-border/50 flex flex-col items-center py-4 gap-4 shrink-0">
                <Button variant="ghost" size="icon" onClick={() => setIsCollapsed(false)}>
                    <Menu className="w-5 h-5" />
                </Button>
                <Button variant="ghost" size="icon" onClick={handleNewChat}>
                    <Plus className="w-5 h-5" />
                </Button>
                <div className="flex-1" />
                <Sparkles className="w-5 h-5 text-primary opacity-50 mb-4" />
            </aside>
        );
    }

    return (
        <aside
            className={`h-screen flex flex-col glass-panel border-r border-border/50 overflow-hidden transition-all duration-300 ${isMobile ? "fixed inset-0 z-50 w-full bg-background" : "w-[280px] shrink-0"
                }`}
        >
            {/* 1. Header (Non-scrollable) */}
            <div className="p-4 border-b border-border/30 flex items-center justify-between shrink-0">
                <div className="flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
                        <Sparkles className="w-5 h-5 text-white" />
                    </div>
                    <span className="font-bold text-lg">TalentScout</span>
                </div>
                <Button variant="ghost" size="icon" onClick={isMobile ? onClose : () => setIsCollapsed(true)}>
                    {isMobile ? <X /> : <Menu />}
                </Button>
            </div>

            {/* 2. Action Button (Non-scrollable) */}
            <div className="p-4 shrink-0">
                <Button onClick={handleNewChat} className="w-full justify-start gap-2 shadow-sm">
                    <Plus className="w-4 h-4" /> New Interview
                </Button>
            </div>

            {/* 3. SCROLLABLE AREA */}
            <div className="flex-1 overflow-y-auto min-h-0 px-4 scrollbar-thin scrollbar-thumb-primary/10">
                <div className="flex items-center justify-between mb-4 sticky top-0 bg-background/80 backdrop-blur-sm py-2 z-10">
                    <h3 className="text-[11px] font-bold uppercase tracking-widest text-muted-foreground flex items-center gap-2">
                        <History className="w-3 h-3" /> Recent Sessions
                    </h3>
                    <button onClick={fetchSessions} className="text-muted-foreground hover:text-primary transition-colors">
                        <RefreshCw className={`w-3 h-3 ${isLoadingSessions ? 'animate-spin' : ''}`} />
                    </button>
                </div>

                <div className="flex flex-col gap-2 pb-8">
                    {sessions.length === 0 && !isLoadingSessions ? (
                        <div className="text-center py-10 border border-dashed rounded-xl border-border/50">
                            <p className="text-xs text-muted-foreground">No history yet</p>
                        </div>
                    ) : (
                        sessions.map((session) => (
                            <div
                                key={session.session_id}
                                onClick={() => loadSession(session.session_id)}
                                className="p-3 rounded-xl border border-transparent hover:border-border hover:bg-muted/50 cursor-pointer transition-all group"
                            >
                                <div className="flex items-center gap-3">
                                    <MessageSquare className="w-4 h-4 text-muted-foreground group-hover:text-primary shrink-0" />
                                    <div className="min-w-0">
                                        <p className="text-sm font-medium truncate">
                                            {session.full_name || "Interview Session"}
                                        </p>
                                        <p className="text-[10px] text-muted-foreground">
                                            {formatRelativeTime(session.created_at)}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* 4. Footer (Non-scrollable) */}
            <div className="p-4 border-t border-border/30 shrink-0 bg-muted/10">
                <p className="text-[10px] text-center text-muted-foreground font-medium">
                    Powered by TalentScout AI
                </p>
            </div>
        </aside>
    );
};