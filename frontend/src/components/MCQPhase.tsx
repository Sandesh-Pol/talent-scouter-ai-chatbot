import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { MCQQuestion } from "./MCQQuestion";
import { Button } from "@/components/ui/button";
import { ArrowRight, Trophy, Loader2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface MCQPhaseProps {
    sessionId: string;
    onComplete: () => void;
}

interface MCQData {
    question: string;
    options: string[];
    difficulty?: string;
    skill: string;
}

export const MCQPhase = ({ sessionId, onComplete }: MCQPhaseProps) => {
    const [isLoading, setIsLoading] = useState(true);
    const [mcqQuestions, setMcqQuestions] = useState<Record<string, MCQData[]>>({});
    const [allQuestions, setAllQuestions] = useState<Array<MCQData & { skillName: string, questionIndex: number }>>([]);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [answers, setAnswers] = useState<Array<any>>([]);
    const [currentResult, setCurrentResult] = useState<any>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [totalCorrect, setTotalCorrect] = useState(0);
    const { toast } = useToast();

    // Debug: Log when currentResult changes
    useEffect(() => {
        console.log('Current Result Updated:', currentResult);
        console.log('Should show Next button:', !!currentResult);
    }, [currentResult]);

    // Fetch MCQs on mount
    useEffect(() => {
        fetchMCQs();
    }, [sessionId]);

    const fetchMCQs = async () => {
        try {
            setIsLoading(true);
            const response = await fetch(
                `http://localhost:8000/api/sessions/${sessionId}/generate-mcqs/`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                }
            );

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.error || 'Failed to generate MCQs');
            }

            const data = await response.json();
            setMcqQuestions(data.mcq_questions);

            // Flatten questions for sequential display
            const flattened: Array<MCQData & { skillName: string, questionIndex: number }> = [];
            Object.entries(data.mcq_questions).forEach(([skill, questions]: [string, any]) => {
                questions.forEach((q: MCQData, index: number) => {
                    flattened.push({
                        ...q,
                        skill: skill,
                        skillName: skill,
                        questionIndex: index
                    });
                });
            });
            setAllQuestions(flattened);

        } catch (error) {
            console.error('Failed to fetch MCQs:', error);
            toast({
                title: 'Error',
                description: error instanceof Error ? error.message : 'Failed to load questions',
                variant: 'destructive'
            });
        } finally {
            setIsLoading(false);
        }
    };

    const handleAnswer = async (answer: string) => {
        const currentQuestion = allQuestions[currentQuestionIndex];
        setIsSubmitting(true);

        try {
            const response = await fetch(
                `http://localhost:8000/api/sessions/${sessionId}/submit-mcq/`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        skill: currentQuestion.skillName,
                        question_index: currentQuestion.questionIndex,
                        answer: answer
                    })
                }
            );

            if (!response.ok) {
                throw new Error('Failed to submit answer');
            }

            const result = await response.json();
            console.log('MCQ Result:', result); // Debug log
            setCurrentResult(result);
            setAnswers([...answers, result]);

            if (result.is_correct) {
                setTotalCorrect(result.total_correct);
            }

        } catch (error) {
            console.error('Failed to submit answer:', error);

            // Set a fallback result so the Next button still appears
            const fallbackResult = {
                is_correct: false,
                correct_answer: 'Unable to verify',
                explanation: 'There was an error submitting your answer. Please try again or continue to the next question.',
                score: 0,
                total_answered: answers.length + 1,
                total_correct: totalCorrect
            };
            setCurrentResult(fallbackResult);

            toast({
                title: 'Error',
                description: 'Failed to submit answer, but you can continue',
                variant: 'destructive'
            });
        } finally {
            setIsSubmitting(false);
        }
    };

    const handleNext = () => {
        if (currentQuestionIndex < allQuestions.length - 1) {
            setCurrentQuestionIndex(currentQuestionIndex + 1);
            setCurrentResult(null);
        } else {
            // All questions answered - calculate ratings and complete
            completeMCQPhase();
        }
    };

    const completeMCQPhase = async () => {
        try {
            // Calculate skill ratings
            const response = await fetch(
                `http://localhost:8000/api/sessions/${sessionId}/calculate-ratings/`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' }
                }
            );

            if (response.ok) {
                const data = await response.json();
                console.log('Skill ratings:', data.skill_ratings);

                toast({
                    title: 'MCQ Round Complete!',
                    description: `You answered ${totalCorrect} out of ${allQuestions.length} questions correctly.`,
                });
            }

        } catch (error) {
            console.error('Failed to calculate ratings:', error);
        } finally {
            // Always move forward to next phase
            onComplete();
        }
    };

    if (isLoading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[400px] space-y-4">
                <Loader2 className="w-8 h-8 text-primary animate-spin" />
                <p className="text-muted-foreground">Generating your technical questions...</p>
            </div>
        );
    }

    if (allQuestions.length === 0) {
        return (
            <div className="text-center space-y-4 p-8">
                <p className="text-muted-foreground">No questions available. Please complete your profile first.</p>
            </div>
        );
    }

    const currentQuestion = allQuestions[currentQuestionIndex];
    const progress = ((currentQuestionIndex + 1) / allQuestions.length) * 100;

    return (
        <div className="h-full overflow-y-auto scrollbar-thin">
            <div className="space-y-6 max-w-4xl mx-auto p-6">
                {/* Header */}
                <div className="text-center space-y-2">
                    <div className="flex items-center justify-center gap-2">
                        <Trophy className="w-6 h-6 text-primary" />
                        <h2 className="text-2xl font-bold text-gradient">MCQ Technical Screening</h2>
                    </div>
                    <p className="text-muted-foreground">
                        Answer {allQuestions.length} multiple choice questions to demonstrate your technical knowledge
                    </p>
                    <div className="flex items-center justify-center gap-4 text-sm">
                        <span className="text-foreground">
                            Progress: <span className="font-semibold text-primary">{currentQuestionIndex + 1}/{allQuestions.length}</span>
                        </span>
                        <span className="text-foreground">
                            Score: <span className="font-semibold text-green-500">{totalCorrect}/{answers.length}</span>
                        </span>
                    </div>
                </div>

                {/* Question */}
                <MCQQuestion
                    question={currentQuestion.question}
                    options={currentQuestion.options}
                    questionNumber={currentQuestionIndex + 1}
                    totalQuestions={allQuestions.length}
                    skill={currentQuestion.skill}
                    difficulty={currentQuestion.difficulty}
                    onAnswer={handleAnswer}
                    isLoading={isSubmitting}
                    result={currentResult}
                />

                {/* Next Button (shown after answer) */}
                {currentResult && (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="flex justify-end pb-6"
                    >
                        <Button
                            onClick={handleNext}
                            size="lg"
                            className="bg-primary hover:bg-primary/90 gap-2"
                        >
                            {currentQuestionIndex < allQuestions.length - 1 ? 'Next Question' : 'Complete MCQ Round'}
                            <ArrowRight className="w-4 h-4" />
                        </Button>
                    </motion.div>
                )}
            </div>
        </div>
    );
};
