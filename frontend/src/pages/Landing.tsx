import { motion } from "framer-motion";
import { ArrowRight, Sparkles, Code, BrainCircuit, ShieldCheck, Zap } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";

const FeatureCard = ({ icon: Icon, title, description, delay }: any) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay, duration: 0.5 }}
    className="glass-card flex flex-col items-center text-center space-y-4 p-8 hover:border-primary/50 transition-all duration-300 group"
  >
    <div className="w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
      <Icon className="w-7 h-7 text-primary" />
    </div>
    <h3 className="text-xl font-semibold text-foreground">{title}</h3>
    <p className="text-muted-foreground leading-relaxed">{description}</p>
  </motion.div>
);

const Landing = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background text-foreground overflow-hidden selection:bg-primary/30 scroll-smooth">
      {/* Background decoration */}
      <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/20 blur-[120px] rounded-full pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-primary/10 blur-[120px] rounded-full pointer-events-none" />

      {/* Navigation */}
      <nav className="relative z-10 flex items-center justify-between px-6 py-6 max-w-7xl mx-auto">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center accent-glow">
            <Sparkles className="w-5 h-5 text-primary-foreground" />
          </div>
          <span className="font-bold text-xl text-gradient tracking-tight">TalentScout AI</span>
        </div>
        <div className="hidden md:flex gap-8 items-center">
            <a href="#features" className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">Features</a>
            <Button onClick={() => navigate('/interview')} className="bg-primary/10 hover:bg-primary/20 text-primary border border-primary/30 font-medium px-6 rounded-full transition-colors">
              Access Demo
            </Button>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="relative z-10 flex flex-col items-center justify-center px-4 pt-24 pb-32 max-w-5xl mx-auto text-center">
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5 }}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-panel border-primary/20 mb-8"
        >
          <span className="flex h-2 w-2 rounded-full bg-primary animate-pulse-glow" />
          <span className="text-sm font-medium text-primary">Powered by LLaMA 3.3 Engine</span>
        </motion.div>

        <motion.h1 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.6 }}
          className="text-5xl md:text-7xl font-bold tracking-tight mb-8 leading-[1.1]"
        >
          Hire the top 1% with <br className="hidden md:block" />
          <span className="text-gradient hover:drop-shadow-[0_0_15px_rgba(20,184,166,0.5)] transition-all duration-500">Autonomous Technical Screening</span>
        </motion.h1>

        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="text-lg md:text-xl text-muted-foreground mb-12 max-w-2xl leading-relaxed"
        >
          Conduct deep, adaptive technical interviews at scale. TalentScout AI combines real-time conversations, subjective evaluations, and targeted MCQ testing to find your best engineers automatically.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.6 }}
          className="flex flex-col sm:flex-row gap-4 items-center justify-center w-full sm:w-auto"
        >
          <Button 
            onClick={() => navigate('/interview')} 
            size="lg" 
            className="w-full sm:w-auto h-14 px-8 text-lg font-medium bg-gradient-to-r from-primary to-primary/80 hover:from-primary/90 hover:to-primary/70 rounded-full gap-2 shadow-[0_0_40px_-10px_rgba(20,184,166,0.6)] transition-all hover:scale-105"
          >
            Start Interactive Demo <ArrowRight className="w-5 h-5 ml-1" />
          </Button>
          <Button 
            variant="outline"
            size="lg" 
            className="w-full sm:w-auto h-14 px-8 text-lg font-medium rounded-full glass-panel hover:bg-white/5 border-white/10"
            onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}
          >
            Explore Features
          </Button>
        </motion.div>
      </main>

      {/* Features Grid */}
      <section id="features" className="relative z-10 max-w-7xl mx-auto px-6 py-24 border-t border-border/30 bg-background/50">
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">The Future of Technical Hiring</h2>
          <p className="text-muted-foreground max-w-2xl mx-auto text-lg">Stop wasting engineering time on first-round checks. Let our state-of-the-art AI conduct deep-dive technical validations.</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <FeatureCard 
            icon={BrainCircuit}
            title="Adaptive Questioning"
            description="Our AI engine creates questions on-the-fly based on the candidate's exact tech stack, experience level, and real-time conversation context."
            delay={0.1}
          />
          <FeatureCard 
            icon={Code}
            title="Comprehensive Testing"
            description="A rigorous multi-stage pipeline: Natural conversation extraction, specialized MCQ testing, and open-ended architectural theory questions."
            delay={0.2}
          />
          <FeatureCard 
            icon={ShieldCheck}
            title="Detailed Skill Matrix"
            description="Get instantly generated professional PDF reports grading candidates across precise 5-star dimensions for every tool they claim to possess."
            delay={0.3}
          />
        </div>
      </section>

      {/* Footer CTA */}
      <section className="relative z-10 py-24 text-center px-6">
        <div className="glass-panel max-w-4xl mx-auto p-12 lg:p-16 rounded-[2.5rem] glow-effect border-primary/20 bg-gradient-to-b from-background/50 to-primary/5">
            <Zap className="w-12 h-12 text-primary mx-auto mb-6" />
            <h2 className="text-3xl md:text-5xl font-bold mb-6">Ready to scale your engineering team?</h2>
            <p className="text-muted-foreground mb-8 text-lg max-w-xl mx-auto leading-relaxed">Experience how TalentScout AI evaluates candidates just like a senior engineer would—in a fully interactive simulation.</p>
            <Button onClick={() => navigate('/interview')} size="lg" className="h-14 px-10 rounded-full text-lg bg-primary hover:bg-primary/90 hover:scale-105 transition-all shadow-[0_0_30px_-5px_rgba(20,184,166,0.4)]">
                Launch Platform
            </Button>
        </div>
      </section>
      
      {/* Footer */}
      <footer className="border-t border-border/20 py-8 text-center text-sm text-muted-foreground/60">
        © {new Date().getFullYear()} TalentScout AI. Built with React, Vite & LLaMA 3.
      </footer>
    </div>
  );
};

export default Landing;
