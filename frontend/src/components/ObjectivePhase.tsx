import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import {
    Loader2,
    CheckCircle2,
    MessageSquare,
    Sparkles,
    ArrowRight,
    Brain
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import { getApiBaseUrl } from "@/utils/api";

interface ObjectivePhaseProps {
    sessionId: string;
    onComplete: () => void;
}

interface ObjectiveQuestion {
    question: string;
    focus_skill: string;
    evaluation_criteria?: string;
}

interface Evaluation {
    score: number;
    rating: string;
    strengths: string[];
    weaknesses: string[];
    feedback: string;
}

export const ObjectivePhase = ({ sessionId, onComplete }: ObjectivePhaseProps) => {
    const [isLoading, setIsLoading] = useState(true);
    const [questions, setQuestions] = useState<ObjectiveQuestion[]>([]);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [currentAnswer, setCurrentAnswer] = useState("");
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
    const [currentEvaluation, setCurrentEvaluation] = useState<Evaluation | null>(null);
    const { toast } = useToast();

    // Fetch objective questions on mount
    useEffect(() => {
        fetchObjectiveQuestions();
    }, [sessionId]);

    const fetchObjectiveQuestions = async () => {
        try {
            setIsLoading(true);
            const base = getApiBaseUrl();
            const response = await fetch(
                `${base}/api/sessions/${sessionId}/generate-objectives/`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                }
            );

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to generate questions');
            }

            const data = await response.json();
            setQuestions(data.objective_questions);

        } catch (error) {
            console.error('Failed to fetch objective questions:', error);
            toast({
                title: 'Error',
                description: error instanceof Error ? error.message : 'Failed to load questions',
                variant: 'destructive'
            });
        } finally {
            setIsLoading(false);
        }
    };

    const handleSubmitAnswer = async () => {
        if (!currentAnswer.trim()) {
            toast({
                title: 'Answer Required',
                description: 'Please provide an answer before submitting',
                variant: 'destructive'
            });
            return;
        }

        setIsSubmitting(true);

        try {
            const base = getApiBaseUrl();
            const response = await fetch(
                `${base}/api/sessions/${sessionId}/submit-objective/`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        question_index: currentQuestionIndex,
                        answer: currentAnswer
                    })
                }
            );

            if (!response.ok) {
                throw new Error('Failed to submit answer');
            }

            const evaluation: Evaluation = await response.json();
            setCurrentEvaluation(evaluation);
            setEvaluations([...evaluations, evaluation]);

            toast({
                title: 'Answer Evaluated',
                description: `Score: ${(evaluation.score * 100).toFixed(0)}% - ${evaluation.rating}`,
            });

        } catch (error) {
            console.error('Failed to submit answer:', error);
            toast({
                title: 'Error',
                description: 'Failed to submit answer',
                variant: 'destructive'
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleNext = () => {
        if (currentQuestionIndex < questions.length - 1) {
            // Move to next question
            setCurrentQuestionIndex(currentQuestionIndex + 1);
            setCurrentAnswer("");
            setCurrentEvaluation(null);
        } else {
            // All questions answered - calculate final ratings and complete
            completeObjectivePhase();
        }
    };

    const completeObjectivePhase = async () => {
        try {
            // Calculate final skill ratings (combines MCQ + Objective scores)
            const base = getApiBaseUrl();
            const response = await fetch(
                `${base}/api/sessions/${sessionId}/calculate-ratings/`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                }
            );

            if (response.ok) {
                const data = await response.json();
                console.log('Final skill ratings:', data.skill_ratings);

                toast({
                    title: 'Technical Screening Complete! 🎉',
                    description: 'All questions answered. Generating your report...',
                });
            }

            // Move to completion phase
            onComplete();

        } catch (error) {
            console.error('Failed to calculate final ratings:', error);
            // Still move forward even if rating calculation fails
            onComplete();
        }
    };

    if (isLoading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
                <Loader2 className="w-8 h-8 text-primary animate-spin" />
                <p className="text-muted-foreground">Generating personalized questions...</p>
            </div>
        );
    }

    if (questions.length === 0) {
        return (
            <div className="text-center space-y-4 p-8">
                <p className="text-muted-foreground">No questions available. Please complete the MCQ round first.</p>
            </div>
        );
    }

    const currentQuestion = questions[currentQuestionIndex];
    const progress = ((currentQuestionIndex + 1) / questions.length) * 100;

    return (
        <div className="h-full overflow-y-auto scrollbar-thin">
            <div className="space-y-6 max-w-4xl mx-auto p-6">
                {/* Header */}
                <div className="text-center space-y-2">
                    <div className="flex items-center justify-center gap-2">
                        <Brain className="w-6 h-6 text-primary" />
                        <h2 className="text-2xl font-bold text-gradient">Subjective Round</h2>
                    </div>
                    <p className="text-muted-foreground">
                        Answer {questions.length} conceptual questions to demonstrate your understanding
                    </p>
                    <div className="flex items-center justify-center gap-4 text-sm">
                        <span className="text-foreground">
                            Progress: <span className="font-semibold text-primary">{currentQuestionIndex + 1}/{questions.length}</span>
                        </span>
                    </div>
                </div>

                {/* Progress Bar */}
                <div className="w-full h-2 bg-secondary rounded-full overflow-hidden">
                    <motion.div
                        className="h-full bg-gradient-to-r from-primary to-primary/60"
                        initial={{ width: 0 }}
                        animate={{ width: `${progress}%` }}
                        transition={{ duration: 0.5 }}
                    />
                </div>

                {/* Question Card */}
                <AnimatePresence mode="wait">
                    <motion.div
                        key={currentQuestionIndex}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        transition={{ duration: 0.3 }}
                    >
                        <Card className="glass-card p-6 space-y-6">
                            {/* Question Header */}
                            <div className="flex items-start gap-3">
                                <div className="p-3 rounded-lg bg-primary/10 text-primary">
                                    <MessageSquare className="w-5 h-5" />
                                </div>
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-2">
                                        <span className="text-xs font-semibold px-2 py-1 rounded-full bg-primary/20 text-primary">
                                            {currentQuestion.focus_skill}
                                        </span>
                                        <span className="text-xs text-muted-foreground">
                                            Question {currentQuestionIndex + 1} of {questions.length}
                                        </span>
                                    </div>
                                    <p className="text-lg font-medium text-foreground leading-relaxed">
                                        {currentQuestion.question}
                                    </p>
                                </div>
                            </div>

                            {/* Answer Input */}
                            {!currentEvaluation && (
                                <div className="space-y-3">
                                    <label className="text-sm font-medium text-muted-foreground">
                                        Your Answer
                                    </label>
                                    <Textarea
                                        value={currentAnswer}
                                        onChange={(e) => setCurrentAnswer(e.target.value)}
                                        placeholder="Type your detailed answer here..."
                                        className="min-h-[200px] resize-none glass-input"
                                        disabled={isSubmitting}
                                    />
                                    <div className="flex justify-end">
                                        <Button
                                            onClick={handleSubmitAnswer}
                                            disabled={isSubmitting || !currentAnswer.trim()}
                                            className="bg-primary hover:bg-primary/90 gap-2"
                                        >
                                            {isSubmitting ? (
                                                <>
                                                    <Loader2 className="w-4 h-4 animate-spin" />
                                                    Evaluating...
                                                </>
                                            ) : (
                                                <>
                                                    <Sparkles className="w-4 h-4" />
                                                    Submit Answer
                                                </>
                                            )}
                                        </Button>
                                    </div>
                                </div>
                            )}

                            {/* Evaluation Feedback */}
                            {currentEvaluation && (
                                <motion.div
                                    initial={{ opacity: 0, y: 20 }}
                                    animate={{ opacity: 1, y: 0 }}
                                    className="space-y-4 border-t border-border/30 pt-6"
                                >
                                    {/* Score Badge */}
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center gap-2">
                                            <CheckCircle2 className="w-5 h-5 text-green-500" />
                                            <span className="font-semibold text-foreground">Evaluation Complete</span>
                                        </div>
                                        <div className="flex items-center gap-3">
                                            <span className="text-sm text-muted-foreground">Score:</span>
                                            <span className="text-2xl font-bold text-primary">
                                                {(currentEvaluation.score * 100).toFixed(0)}%
                                            </span>
                                            <span className="px-3 py-1 rounded-full bg-primary/20 text-primary text-sm font-medium">
                                                {currentEvaluation.rating}
                                            </span>
                                        </div>
                                    </div>

                                    {/* Feedback */}
                                    <div className="space-y-3">
                                        <div className="p-4 rounded-lg bg-secondary/50">
                                            <p className="text-sm text-muted-foreground mb-1 font-medium">AI Feedback:</p>
                                            <p className="text-sm text-foreground leading-relaxed">
                                                {currentEvaluation.feedback}
                                            </p>
                                        </div>

                                        {/* Strengths & Weaknesses */}
                                        <div className="grid grid-cols-2 gap-4">
                                            {currentEvaluation.strengths.length > 0 && (
                                                <div className="p-3 rounded-lg bg-green-500/10 border border-green-500/20">
                                                    <p className="text-xs font-semibold text-green-600 dark:text-green-400 mb-2">
                                                        ✓ Strengths
                                                    </p>
                                                    <ul className="space-y-1">
                                                        {currentEvaluation.strengths.map((strength, i) => (
                                                            <li key={i} className="text-xs text-foreground/80">• {strength}</li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            )}
                                            {currentEvaluation.weaknesses.length > 0 && (
                                                <div className="p-3 rounded-lg bg-orange-500/10 border border-orange-500/20">
                                                    <p className="text-xs font-semibold text-orange-600 dark:text-orange-400 mb-2">
                                                        ⚠ Areas to Improve
                                                    </p>
                                                    <ul className="space-y-1">
                                                        {currentEvaluation.weaknesses.map((weakness, i) => (
                                                            <li key={i} className="text-xs text-foreground/80">• {weakness}</li>
                                                        ))}
                                                    </ul>
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    {/* Next Button */}
                                    <div className="flex justify-end pt-4 pb-4">
                                        <Button
                                            onClick={handleNext}
                                            size="lg"
                                            className="bg-primary hover:bg-primary/90 gap-2"
                                        >
                                            {currentQuestionIndex < questions.length - 1 ? 'Next Question' : 'Complete Interview'}
                                            <ArrowRight className="w-4 h-4" />
                                        </Button>
                                    </div>
                                </motion.div>
                            )}
                        </Card>
                    </motion.div>
                </AnimatePresence>
            </div>
        </div>
    );
};
