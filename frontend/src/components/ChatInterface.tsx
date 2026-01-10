import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Bot, User, Sparkles, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Message {
  id: string;
  role: "assistant" | "user";
  content: string;
  timestamp: Date;
}

interface ChatInterfaceProps {
  messages: Message[];
  onSendMessage: (message: string) => void;
  isTyping?: boolean;
}

const ChatMessage = ({ message, index }: { message: Message; index: number }) => {
  const isAssistant = message.role === "assistant";

  // Enhanced timestamp formatting with relative time
  const formatTime = (timestamp: Date) => {
    try {
      // Ensure we have a valid Date object
      const date = timestamp instanceof Date ? timestamp : new Date(timestamp);

      // Check if date is valid
      if (isNaN(date.getTime())) {
        return "Just now";
      }

      // Calculate time difference
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffSeconds = Math.floor(diffMs / 1000);
      const diffMinutes = Math.floor(diffSeconds / 60);
      const diffHours = Math.floor(diffMinutes / 60);

      // Show relative time for recent messages
      if (diffSeconds < 10) {
        return "Just now";
      } else if (diffSeconds < 60) {
        return `${diffSeconds}s ago`;
      } else if (diffMinutes < 60) {
        return `${diffMinutes}m ago`;
      } else if (diffHours < 24) {
        // Show actual time for messages today
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
      } else {
        // Show date and time for older messages
        return date.toLocaleString([], {
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit'
        });
      }
    } catch (error) {
      return "Just now";
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.3 }}
      className={`flex gap-4 ${isAssistant ? "" : "flex-row-reverse"}`}
    >
      {/* Avatar */}
      <div className={`
        w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0
        ${isAssistant
          ? "bg-gradient-to-br from-primary to-primary/60 accent-glow"
          : "bg-secondary border border-border"
        }
      `}>
        {isAssistant ? (
          <Bot className="w-5 h-5 text-primary-foreground" />
        ) : (
          <User className="w-5 h-5 text-muted-foreground" />
        )}
      </div>

      {/* Message Bubble */}
      <div className={`
        flex-1 max-w-[80%] rounded-2xl px-4 py-3
        ${isAssistant
          ? "glass-card rounded-tl-sm"
          : "bg-primary/10 border border-primary/20 rounded-tr-sm"
        }
      `}>
        <p className="text-sm leading-relaxed text-foreground whitespace-pre-wrap">
          {message.content}
        </p>
        <p className="text-[10px] text-muted-foreground mt-2">
          {formatTime(message.timestamp)}
        </p>
      </div>
    </motion.div>
  );
};

const TypingIndicator = () => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    exit={{ opacity: 0, y: -10 }}
    className="flex gap-4"
  >
    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center accent-glow">
      <Bot className="w-5 h-5 text-primary-foreground" />
    </div>
    <div className="glass-card rounded-2xl rounded-tl-sm px-4 py-3">
      <div className="flex gap-1.5">
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            animate={{ opacity: [0.3, 1, 0.3] }}
            transition={{ duration: 1.2, repeat: Infinity, delay: i * 0.2 }}
            className="w-2 h-2 rounded-full bg-primary"
          />
        ))}
      </div>
    </div>
  </motion.div>
);

const WelcomeState = () => (
  <motion.div
    initial={{ opacity: 0, scale: 0.95 }}
    animate={{ opacity: 1, scale: 1 }}
    className="flex flex-col items-center justify-center py-16"
  >
    <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-primary to-primary/60 flex items-center justify-center mb-6 accent-glow">
      <Sparkles className="w-10 h-10 text-primary-foreground" />
    </div>
    <h2 className="text-2xl font-semibold text-foreground mb-2">
      Where talent meets opportunity
    </h2>
    <p className="text-muted-foreground text-center max-w-md mb-8">
      I'm your AI interviewer. I'll guide you through a quick technical screening to learn about your skills and experience.
    </p>
    <div className="grid grid-cols-3 gap-4 w-full max-w-lg">
      {[
        { title: "Quick Intro", desc: "Tell me about yourself" },
        { title: "Tech Skills", desc: "Share your expertise" },
        { title: "Experience", desc: "Your journey so far" },
      ].map((item, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 + i * 0.1 }}
          className="glass-card text-center hover:border-primary/30 transition-colors cursor-default"
        >
          <p className="text-sm font-medium text-foreground">{item.title}</p>
          <p className="text-xs text-muted-foreground mt-1">{item.desc}</p>
        </motion.div>
      ))}
    </div>
  </motion.div>
);

export const ChatInterface = ({ messages, onSendMessage, isTyping = false }: ChatInterfaceProps) => {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Auto-resize textarea as user types
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [input]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      onSendMessage(input.trim());
      setInput("");
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
    // Allow Shift+Enter for new line (default behavior)
  };

  const handleNextQuestion = () => {
    // Send a predefined message to prompt the AI to ask the next question
    onSendMessage("Next question please");
    setInput("");
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto scrollbar-thin px-4 py-6">
        <div className="max-w-3xl mx-auto space-y-6">
          {messages.length === 0 ? (
            <WelcomeState />
          ) : (
            <>
              {messages.map((message, index) => (
                <ChatMessage key={message.id} message={message} index={index} />
              ))}
              <AnimatePresence>
                {isTyping && <TypingIndicator />}
              </AnimatePresence>
            </>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-border/30 p-4">
        <form onSubmit={handleSubmit} className="max-w-3xl mx-auto">
          <div className="glass-card p-2 flex items-end gap-3">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Type your response..."
              rows={1}
              className="flex-1 bg-transparent border-none outline-none text-sm text-foreground placeholder:text-muted-foreground px-2 py-2 resize-none max-h-[200px]"
            />
            <Button
              type="button"
              size="icon"
              onClick={handleNextQuestion}
              disabled={isTyping}
              className="rounded-lg bg-secondary hover:bg-secondary/80 text-foreground disabled:opacity-50 disabled:cursor-not-allowed transition-all flex-shrink-0"
              title="Next Question"
            >
              <ArrowRight className="w-4 h-4" />
            </Button>
            <Button
              type="submit"
              size="icon"
              disabled={!input.trim()}
              className="rounded-lg bg-primary hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex-shrink-0"
            >
              <Send className="w-4 h-4" />
            </Button>
          </div>
          <p className="text-center text-xs text-muted-foreground mt-3">
            TalentScout can make mistakes. Verify important information.
          </p>
        </form>
      </div>
    </div>
  );
};
