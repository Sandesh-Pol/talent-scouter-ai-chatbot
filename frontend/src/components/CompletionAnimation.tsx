import { motion, AnimatePresence } from "framer-motion";
import { Trophy, Sparkles, CheckCircle2, Star, Award, Medal } from "lucide-react";
import confetti from "canvas-confetti";
import { useEffect } from "react";

interface CompletionAnimationProps {
    isVisible: boolean;
    candidateName?: string;
    performance?: number; // Profile completeness percentage
    onClose?: () => void;
}

export const CompletionAnimation = ({
    isVisible,
    candidateName,
    performance = 75,
    onClose
}: CompletionAnimationProps) => {

    // Determine performance level and messaging
    const getPerformanceMessage = () => {
        if (performance >= 95) {
            return {
                title: "Outstanding! 🌟",
                message: "Exceptional performance! You've provided comprehensive information.",
                icon: <Award className="w-12 h-12 text-primary-foreground" />,
                rating: 5,
                color: "from-yellow-400 to-yellow-600"
            };
        } else if (performance >= 85) {
            return {
                title: "Excellent! ⭐",
                message: "Great job! You've completed the interview with excellent detail.",
                icon: <Trophy className="w-12 h-12 text-primary-foreground" />,
                rating: 4,
                color: "from-primary to-primary/60"
            };
        } else if (performance >= 70) {
            return {
                title: "Well Done! 👏",
                message: "Good work! You've successfully completed the interview.",
                icon: <Medal className="w-12 h-12 text-primary-foreground" />,
                rating: 3,
                color: "from-blue-500 to-blue-700"
            };
        } else {
            return {
                title: "Completed! ✓",
                message: "Thank you for completing the interview screening.",
                icon: <CheckCircle2 className="w-12 h-12 text-primary-foreground" />,
                rating: 2,
                color: "from-green-500 to-green-700"
            };
        }
    };

    const performanceData = getPerformanceMessage();

    useEffect(() => {
        if (isVisible) {
            // Trigger confetti animation based on performance
            const duration = performanceData.rating >= 4 ? 4000 : 2000;
            const animationEnd = Date.now() + duration;
            const defaults = {
                startVelocity: 30,
                spread: 360,
                ticks: performanceData.rating >= 4 ? 80 : 60,
                zIndex: 9999
            };

            function randomInRange(min: number, max: number) {
                return Math.random() * (max - min) + min;
            }

            const interval: any = setInterval(function () {
                const timeLeft = animationEnd - Date.now();

                if (timeLeft <= 0) {
                    return clearInterval(interval);
                }

                const particleCount = 50 * (timeLeft / duration);
                confetti({
                    ...defaults,
                    particleCount,
                    origin: { x: randomInRange(0.1, 0.3), y: Math.random() - 0.2 }
                });
                confetti({
                    ...defaults,
                    particleCount,
                    origin: { x: randomInRange(0.7, 0.9), y: Math.random() - 0.2 }
                });
            }, 250);

            return () => clearInterval(interval);
        }
    }, [isVisible, performanceData.rating]);

    return (
        <AnimatePresence>
            {isVisible && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    onClick={onClose} // Click outside to close
                    className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4"
                >
                    <motion.div
                        initial={{ scale: 0.5, opacity: 0 }}
                        animate={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 0.5, opacity: 0 }}
                        transition={{ type: "spring", duration: 0.5 }}
                        onClick={(e) => e.stopPropagation()} // Prevent closing when clicking modal
                        className="glass-card max-w-md w-full p-8 text-center space-y-6 relative"
                    >
                        {/* Close hint */}
                        <p className="text-xs text-muted-foreground absolute top-4 right-4">
                            Click outside to close
                        </p>

                        {/* Icon with Glow */}
                        <motion.div
                            initial={{ scale: 0, rotate: -180 }}
                            animate={{ scale: 1, rotate: 0 }}
                            transition={{ delay: 0.2, type: "spring", stiffness: 200 }}
                            className="flex justify-center"
                        >
                            <div className="relative">
                                <div className="absolute inset-0 bg-primary/30 blur-2xl rounded-full" />
                                <div className={`relative w-24 h-24 rounded-full bg-gradient-to-br ${performanceData.color} flex items-center justify-center accent-glow`}>
                                    {performanceData.icon}
                                </div>
                            </div>
                        </motion.div>

                        {/* Star Rating */}
                        <motion.div
                            initial={{ opacity: 0, y: -10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.3 }}
                            className="flex justify-center gap-1"
                        >
                            {[...Array(5)].map((_, i) => (
                                <Star
                                    key={i}
                                    className={`w-5 h-5 ${i < performanceData.rating
                                            ? "fill-primary text-primary"
                                            : "text-muted-foreground"
                                        }`}
                                />
                            ))}
                        </motion.div>

                        {/* Congratulations Text */}
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.4 }}
                            className="space-y-3"
                        >
                            <h2 className="text-3xl font-bold text-gradient flex items-center justify-center gap-2">
                                <Sparkles className="w-6 h-6 text-primary" />
                                {performanceData.title}
                                <Sparkles className="w-6 h-6 text-primary" />
                            </h2>
                            <p className="text-lg text-foreground">
                                {candidateName ? `${candidateName}!` : "Candidate!"}
                            </p>
                            <p className="text-muted-foreground">
                                {performanceData.message}
                            </p>
                            <p className="text-sm text-primary font-medium">
                                Profile Completeness: {performance}%
                            </p>
                        </motion.div>

                        {/* Check Items */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 0.6 }}
                            className="space-y-2 text-left"
                        >
                            {[
                                "Profile information collected",
                                "Technical questions answered",
                                "Interview session completed"
                            ].map((item, index) => (
                                <motion.div
                                    key={index}
                                    initial={{ opacity: 0, x: -20 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    transition={{ delay: 0.7 + index * 0.1 }}
                                    className="flex items-center gap-3 text-sm"
                                >
                                    <CheckCircle2 className="w-5 h-5 text-primary flex-shrink-0" />
                                    <span className="text-foreground">{item}</span>
                                </motion.div>
                            ))}
                        </motion.div>

                        {/* Next Steps */}
                        <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            transition={{ delay: 1 }}
                            className="pt-4 border-t border-border/30"
                        >
                            <p className="text-sm text-muted-foreground">
                                Our team will review your responses and get back to you soon.
                            </p>
                        </motion.div>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
};
