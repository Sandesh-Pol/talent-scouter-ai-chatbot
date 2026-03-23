import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { User, Briefcase, Code, Sparkles, MapPin, Mail, Phone, Download } from "lucide-react";
import { Button } from "@/components/ui/button";
import { SkillRatings } from "./SkillRatings";
import { useToast } from "@/hooks/use-toast";
import { getApiBaseUrl } from "@/utils/api";

interface CandidateData {
  fullName: string;
  email: string;
  phone: string;
  location: string;
  experience: string;
  techStack: string[];
  position: string;
}

interface CandidateSidebarProps {
  candidate: CandidateData;
  sessionId?: string;
  currentPhase?: string;
}

const ProfileCard = ({
  icon: Icon,
  label,
  value,
  delay
}: {
  icon: React.ElementType;
  label: string;
  value: string | string[];
  delay: number;
}) => {
  const isEmpty = !value || (Array.isArray(value) && value.length === 0);

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay, duration: 0.4 }}
      className="glass-card group hover:border-primary/30 transition-all duration-300"
    >
      <div className="flex items-start gap-3">
        <div className="p-2 rounded-lg bg-primary/10 text-primary">
          <Icon className="w-4 h-4" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-xs text-muted-foreground uppercase tracking-wider mb-1">
            {label}
          </p>
          {isEmpty ? (
            <p className="text-sm text-muted-foreground/50 italic">
              [Waiting for input...]
            </p>
          ) : Array.isArray(value) ? (
            <div className="flex flex-wrap gap-1.5">
              {value.map((item, i) => (
                <span
                  key={i}
                  className="px-2 py-0.5 text-xs rounded-full bg-primary/15 text-primary border border-primary/20"
                >
                  {item}
                </span>
              ))}
            </div>
          ) : (
            <p className="text-sm font-medium text-foreground truncate">
              {value}
            </p>
          )}
        </div>
      </div>
    </motion.div>
  );
};

export const CandidateSidebar = ({ candidate, sessionId, currentPhase }: CandidateSidebarProps) => {
  const [skillRatings, setSkillRatings] = useState<Record<string, any>>({});
  const [isDownloading, setIsDownloading] = useState(false);
  const { toast } = useToast();

  // Fetch skill ratings when session is available and on mount
  useEffect(() => {
    if (sessionId) {
      console.log('CandidateSidebar mounted with sessionId:', sessionId, 'phase:', currentPhase);
      fetchSkillRatings();
    }
  }, [sessionId]);

  // Also fetch when phase changes to closing
  useEffect(() => {
    if (sessionId && currentPhase === 'closing') {
      console.log('Phase is closing, fetching skill ratings');
      // Add a small delay to ensure backend has saved the data
      setTimeout(() => {
        fetchSkillRatings();
      }, 500);
    }
  }, [sessionId, currentPhase]);

  const fetchSkillRatings = async () => {
    if (!sessionId) return;

    try {
      console.log('Fetching skill ratings for session:', sessionId);
      const base = getApiBaseUrl();
      const response = await fetch(
        `${base}/api/sessions/${sessionId}/status/`
      );

      if (response.ok) {
        const data = await response.json();
        console.log('Full session data received:', data);
        console.log('Candidate profile:', data.candidate_profile);
        console.log('Skill ratings in profile:', data.candidate_profile?.skill_ratings);
        
        if (data.candidate_profile?.skill_ratings) {
          const ratings = data.candidate_profile.skill_ratings;
          console.log('Setting skill ratings:', ratings);
          console.log('Number of skills:', Object.keys(ratings).length);
          setSkillRatings(ratings);
        } else {
          console.warn('No skill ratings found in response');
        }
      } else {
        console.error('Failed to fetch session status:', response.status);
      }
    } catch (error) {
      console.error('Failed to fetch skill ratings:', error);
    }
  };

  const handleDownloadReport = async () => {
    if (!sessionId) {
      toast({
        title: 'Error',
        description: 'No session ID available',
        variant: 'destructive'
      });
      return;
    }

    setIsDownloading(true);

    try {
      const base = getApiBaseUrl();
      const response = await fetch(
        `${base}/api/sessions/${sessionId}/download-report/`
      );

      if (!response.ok) {
        throw new Error('Failed to generate report');
      }

      // Create blob and download
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `screening_report_${candidate.fullName || 'candidate'}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      toast({
        title: 'Report Downloaded',
        description: 'Your screening report has been downloaded successfully',
      });

    } catch (error) {
      console.error('Failed to download report:', error);
      toast({
        title: 'Download Failed',
        description: 'Failed to generate PDF report',
        variant: 'destructive'
      });
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <aside className="w-72 h-screen glass-panel border-r border-border/50 flex flex-col overflow-hidden">
      {/* Logo Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="p-6 border-b border-border/30"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center accent-glow">
            <Sparkles className="w-5 h-5 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-gradient">TalentScout</h1>
            <p className="text-xs text-muted-foreground">AI Hiring Assistant</p>
          </div>
        </div>
      </motion.div>

      {/* Candidate Dashboard */}
      <div className="flex-1 overflow-y-auto scrollbar-thin p-4 space-y-3">
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="mb-4"
        >
          <h2 className="text-xs uppercase tracking-widest text-muted-foreground font-medium flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-primary animate-pulse-glow" />
            Live Candidate Profile
          </h2>
        </motion.div>

        <ProfileCard
          icon={User}
          label="Full Name"
          value={candidate.fullName}
          delay={0.3}
        />
        <ProfileCard
          icon={Mail}
          label="Email"
          value={candidate.email}
          delay={0.35}
        />
        <ProfileCard
          icon={Phone}
          label="Phone Number"
          value={candidate.phone}
          delay={0.375}
        />
        <ProfileCard
          icon={MapPin}
          label="Current Location"
          value={candidate.location}
          delay={0.4}
        />
        <ProfileCard
          icon={Briefcase}
          label="Experience Level"
          value={candidate.experience}
          delay={0.45}
        />
        <ProfileCard
          icon={Briefcase}
          label="Position Applied"
          value={candidate.position}
          delay={0.5}
        />
        <ProfileCard
          icon={Code}
          label="Tech Stack"
          value={candidate.techStack}
          delay={0.55}
        />

        {/* Skill Ratings - Show when available */}
        {Object.keys(skillRatings).length > 0 ? (
          <div className="pt-4 border-t border-border/30">
            <SkillRatings skillRatings={skillRatings} />
          </div>
        ) : (
          currentPhase === 'closing' && (
            <div className="pt-4 border-t border-border/30 p-3 glass-card">
              <p className="text-xs text-muted-foreground text-center">
                Loading skill ratings...
              </p>
            </div>
          )
        )}
      </div>

      {/* Footer with PDF Download */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.6 }}
        className="border-t border-border/30"
      >
        {/* PDF Download Button - Show when interview is complete */}
        {currentPhase === 'closing' && sessionId && (
          <div className="p-4 border-b border-border/30">
            <Button
              onClick={handleDownloadReport}
              disabled={isDownloading}
              className="w-full bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 gap-2"
            >
              {isDownloading ? (
                <>
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  >
                    <Download className="w-4 h-4" />
                  </motion.div>
                  Generating...
                </>
              ) : (
                <>
                  <Download className="w-4 h-4" />
                  Download Report
                </>
              )}
            </Button>
          </div>
        )}

        {/* User Info */}
        <div className="p-4">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center">
              <User className="w-4 h-4 text-muted-foreground" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium truncate">
                {candidate.fullName || "New Candidate"}
              </p>
              <p className="text-xs text-muted-foreground">
                {currentPhase === 'closing' ? 'Interview Complete' : 'Interview in progress'}
              </p>
            </div>
            <div className={`w-2 h-2 rounded-full ${currentPhase === 'closing' ? 'bg-green-500' : 'bg-primary animate-pulse'}`} />
          </div>
        </div>
      </motion.div>
    </aside>
  );
};
