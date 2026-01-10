import { useMemo, useState, useEffect } from "react";
import { NavigationSidebar } from "@/components/NavigationSidebar";
import { CandidateSidebar } from "@/components/CandidateSidebar";
import { ProgressStepper } from "@/components/ProgressStepper";
import { ChatInterface } from "@/components/ChatInterface";
import { CompletionAnimation } from "@/components/CompletionAnimation";
import { MCQPhase } from "@/components/MCQPhase";
import { ObjectivePhase } from "@/components/ObjectivePhase";
import { useInterviewSession } from "@/hooks/useInterviewSession";
import { Loader2, WifiOff, List, User } from "lucide-react";
import { Button } from "@/components/ui/button";

interface CandidateData {
  fullName: string;
  email: string;
  phone: string;
  location: string;
  experience: string;
  techStack: string[];
  position: string;
}

interface Message {
  id: string;
  role: "assistant" | "user";
  content: string;
  timestamp: Date;
}

const Index = () => {
  const [showMobileNav, setShowMobileNav] = useState(false);
  const [showMobileProfile, setShowMobileProfile] = useState(false);
  const [showCompletion, setShowCompletion] = useState(false);

  // Interview flow state - restore from localStorage if available
  const [interviewFlow, setInterviewFlow] = useState<'chat' | 'mcq' | 'subjective' | 'complete'>(() => {
    const stored = localStorage.getItem('talentscout_interview_flow');
    return (stored as 'chat' | 'mcq' | 'subjective' | 'complete') || 'chat';
  });

  // Use the custom hook for backend integration
  const {
    sessionId,
    currentPhase,
    profileCompleteness,
    candidateProfile,
    messages: apiMessages,
    isInitializing,
    isSending,
    sendMessage,
    needsIntervention,
  } = useInterviewSession();

  // Transform backend data to component format
  const candidate = useMemo<CandidateData>(() => ({
    fullName: candidateProfile.full_name || "",
    email: candidateProfile.email || "",
    phone: candidateProfile.phone || "",
    location: candidateProfile.location || "",
    experience: candidateProfile.experience_level || "",
    techStack: candidateProfile.tech_stack || [],
    position: candidateProfile.position_applied || "",
  }), [candidateProfile]);

  // Transform backend messages to component format
  const messages = useMemo<Message[]>(() =>
    apiMessages.map(msg => ({
      id: msg.message_id,
      role: msg.role as "assistant" | "user",
      content: msg.content,
      timestamp: new Date(msg.timestamp),
    })),
    [apiMessages]
  );

  // Map phase to step number
  const currentStep = useMemo(() => {
    switch (currentPhase) {
      case 'onboarding':
        return 1;
      case 'information_gathering':
        return 2;
      case 'technical_screening':
        return 3;
      case 'closing':
        return 3;
      default:
        return 1;
    }
  }, [currentPhase]);

  // Initialize interview flow based on backend phase (on session restore)
  useEffect(() => {
    if (!sessionId || !currentPhase) return;

    // Determine the correct interview flow based on the current phase
    if (currentPhase === 'closing') {
      // Interview is complete - show completion screen
      console.log('Setting interview flow to complete, phase:', currentPhase);
      setInterviewFlow('complete');
      setShowCompletion(false); // Don't show animation on refresh
      localStorage.setItem('talentscout_interview_flow', 'complete');
    } else if (currentPhase === 'technical_screening' && profileCompleteness >= 80) {
      // Check if MCQ has been completed by checking if skill_ratings exist
      // If already in 'subjective' or 'complete' state, maintain that
      const storedFlow = localStorage.getItem('talentscout_interview_flow');
      if (storedFlow === 'subjective' || storedFlow === 'complete') {
        // Keep the stored flow
        setInterviewFlow(storedFlow as 'subjective' | 'complete');
        return;
      }
      // Otherwise, start with MCQ
      if (interviewFlow === 'chat') {
        setInterviewFlow('mcq');
        localStorage.setItem('talentscout_interview_flow', 'mcq');
      }
    } else if (currentPhase === 'onboarding' || currentPhase === 'information_gathering') {
      // Still in chat phase
      if (interviewFlow !== 'chat') {
        setInterviewFlow('chat');
        localStorage.setItem('talentscout_interview_flow', 'chat');
      }
    }
  }, [sessionId, currentPhase, profileCompleteness]);

  // Handle manual phase transitions (when user completes a phase)
  useEffect(() => {
    // Save interview flow to localStorage whenever it changes
    localStorage.setItem('talentscout_interview_flow', interviewFlow);
  }, [interviewFlow]);

  // Handle message sending
  const handleSendMessage = async (content: string) => {
    await sendMessage(content);
  };

  // Loading state
  if (isInitializing) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
          <p className="text-muted-foreground">Initializing interview session...</p>
        </div>
      </div>
    );
  }

  // Error state (no session)
  if (!sessionId) {
    return (
      <div className="flex h-screen items-center justify-center bg-background">
        <div className="flex flex-col items-center gap-4 text-center">
          <WifiOff className="h-12 w-12 text-destructive" />
          <div>
            <h2 className="text-xl font-semibold mb-2">Connection Failed</h2>
            <p className="text-muted-foreground">
              Unable to connect to the interview server.
              <br />
              Please check your connection and refresh the page.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="flex h-screen overflow-hidden bg-background">
        {/* Left Navigation Sidebar - Hidden on mobile, shown with burger menu */}
        <div className="hidden lg:block">
          <NavigationSidebar />
        </div>

        {/* Mobile Navigation Overlay */}
        {showMobileNav && (
          <div className="lg:hidden fixed inset-0 z-50">
            <div
              className="absolute inset-0 bg-background/80 backdrop-blur-sm"
              onClick={() => setShowMobileNav(false)}
            />
            <div className="relative">
              <NavigationSidebar isMobile={true} onClose={() => setShowMobileNav(false)} />
            </div>
          </div>
        )}

        {/* Main Content */}
        <main className="flex-1 flex flex-col overflow-hidden">
          {/* Mobile Header with Burger Menus */}
          <div className="lg:hidden flex items-center justify-between p-4 border-b border-border/30">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setShowMobileNav(true)}
              className="hover:bg-primary/10"
            >
              <List className="w-5 h-5" />
            </Button>
            <h1 className="text-lg font-semibold text-gradient">TalentScout</h1>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setShowMobileProfile(true)}
              className="hover:bg-primary/10"
            >
              <User className="w-5 h-5" />
            </Button>
          </div>

          {/* Progress Header */}
          <header className="border-b border-border/30 p-4 glow-effect">
            <ProgressStepper currentStep={currentStep} />
          </header>

          {/* Chat Area */}
          <div className="flex-1 overflow-hidden">
            {interviewFlow === 'chat' && (
              <ChatInterface
                messages={messages}
                onSendMessage={handleSendMessage}
                isTyping={isSending}
              />
            )}

            {interviewFlow === 'mcq' && sessionId && (
              <MCQPhase
                sessionId={sessionId}
                onComplete={() => setInterviewFlow('subjective')}
              />
            )}

            {interviewFlow === 'subjective' && sessionId && (
              <ObjectivePhase
                sessionId={sessionId}
                onComplete={() => {
                  setInterviewFlow('complete');
                  setShowCompletion(true);
                }}
              />
            )}

            {interviewFlow === 'complete' && (
              <div className="flex flex-col items-center justify-center h-full space-y-6 p-8">
                <div className="text-center space-y-4">
                  <div className="w-20 h-20 mx-auto rounded-full bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center">
                    <svg
                      className="w-10 h-10 text-primary-foreground"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                  </div>
                  <h2 className="text-3xl font-bold text-gradient">Interview Complete!</h2>
                  <p className="text-muted-foreground max-w-md">
                    Thank you for completing the technical screening. Your responses have been evaluated and your report is ready for download.
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Check the sidebar to download your detailed screening report.
                  </p>
                </div>
              </div>
            )}
          </div>
        </main>

        {/* Right Candidate Profile Sidebar - Hidden on mobile, shown with menu */}
        <div className="hidden lg:block">
          <CandidateSidebar
            candidate={candidate}
            sessionId={sessionId || undefined}
            currentPhase={currentPhase}
          />
        </div>

        {/* Mobile Profile Overlay */}
        {showMobileProfile && (
          <div className="lg:hidden fixed inset-0 z-50">
            <div
              className="absolute inset-0 bg-background/80 backdrop-blur-sm"
              onClick={() => setShowMobileProfile(false)}
            />
            <div className="absolute right-0 top-0 h-full">
              <CandidateSidebar
                candidate={candidate}
                sessionId={sessionId || undefined}
                currentPhase={currentPhase}
              />
            </div>
          </div>
        )}
      </div>

      {/* Completion Animation */}
      <CompletionAnimation
        isVisible={showCompletion}
        candidateName={candidate.fullName}
        performance={profileCompleteness}
        onClose={() => setShowCompletion(false)}
      />
    </>
  );
};

export default Index;
