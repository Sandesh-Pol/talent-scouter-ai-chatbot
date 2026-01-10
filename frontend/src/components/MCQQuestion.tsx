import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Button } from "@/components/ui/button";
import { Check, X, ChevronRight, Award } from "lucide-react";

interface MCQOption {
    text: string;
    index: number;
}

interface MCQQuestionProps {
    question: string;
    options: string[];
    questionNumber: number;
    totalQuestions: number;
    skill: string;
    difficulty?: string;
    onAnswer: (answer: string) => void;
    isLoading?: boolean;
    result?: {
        is_correct: boolean;
        correct_answer: string;
        explanation: string;
    };
}

export const MCQQuestion = ({
    question,
    options,
    questionNumber,
    totalQuestions,
    skill,
    difficulty = "medium",
    onAnswer,
    isLoading = false,
    result
}: MCQQuestionProps) => {
    const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
    const [showResult, setShowResult] = useState(false);

    const handleSelectAnswer = (answer: string) => {
        if (!result && !isLoading) {
            setSelectedAnswer(answer);
        }
    };

    const handleSubmit = () => {
        if (selectedAnswer) {
            onAnswer(selectedAnswer);
            setShowResult(true);
        }
    };

    const getDifficultyColor = () => {
        switch (difficulty) {
            case 'easy': return 'text-green-500';
            case 'medium': return 'text-yellow-500';
            case 'hard': return 'text-red-500';
            default: return 'text-blue-500';
        }
    };

    const getOptionLetter = (index: number) => {
        return String.fromCharCode(65 + index); // A, B, C, D
    };

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="glass-card p-6 space-y-6 max-w-3xl mx-auto"
        >
            {/* Header */}
            <div className="flex items-start justify-between">
                <div className="space-y-1">
                    <div className="flex items-center gap-2">
                        <span className="text-xs font-medium text-primary bg-primary/10 px-2 py-1 rounded">
                            {skill}
                        </span>
                        <span className={`text-xs font-medium ${getDifficultyColor()}`}>
                            {difficulty}
                        </span>
                    </div>
                    <p className="text-sm text-muted-foreground">
                        Question {questionNumber} of {totalQuestions}
                    </p>
                </div>
                <div className="flex items-center gap-2 text-sm font-medium text-Primary">
                    <Award className="w-4 h-4" />
                    <span>{questionNumber}/{totalQuestions}</span>
                </div>
            </div>

            {/* Progress Bar */}
            <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
                <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(questionNumber / totalQuestions) * 100}%` }}
                    className="h-full bg-gradient-to-r from-primary to-primary/60"
                />
            </div>

            {/* Question */}
            <div className="space-y-4">
                <h3 className="text-lg font-semibold text-foreground leading-relaxed">
                    {question}
                </h3>

                {/* Options */}
                <div className="space-y-3">
                    {options.map((option, index) => {
                        const optionLetter = getOptionLetter(index);
                        const isSelected = selectedAnswer === option;
                        const isCorrect = result && option === result.correct_answer;
                        const isWrong = result && isSelected && !result.is_correct;

                        return (
                            <motion.button
                                key={index}
                                whileHover={!result ? { scale: 1.02 } : {}}
                                whileTap={!result ? { scale: 0.98 } : {}}
                                onClick={() => handleSelectAnswer(option)}
                                disabled={!!result || isLoading}
                                className={`
                  w-full p-4 rounded-xl border-2 transition-all text-left
                  flex items-center gap-4 relative overflow-hidden
                  ${!result && !isSelected ? 'border-border hover:border-primary/50 bg-card' : ''}
                  ${!result && isSelected ? 'border-primary bg-primary/10' : ''}
                  ${isCorrect ? 'border-green-500 bg-green-500/10' : ''}
                  ${isWrong ? 'border-red-500 bg-red-500/10' : ''}
                  ${result ? 'cursor-not-allowed' : 'cursor-pointer'}
                `}
                            >
                                {/* Option Letter */}
                                <div className={`
                  w-10 h-10 rounded-lg flex items-center justify-center font-bold flex-shrink-0
                  ${!result && !isSelected ? 'bg-muted text-muted-foreground' : ''}
                  ${!result && isSelected ? 'bg-primary text-primary-foreground' : ''}
                  ${isCorrect ? 'bg-green-500 text-white' : ''}
                  ${isWrong ? 'bg-red-500 text-white' : ''}
                `}>
                                    {optionLetter}
                                </div>

                                {/* Option Text */}
                                <span className="flex-1 text-sm font-medium text-foreground">
                                    {option}
                                </span>

                                {/* Result Icon */}
                                <AnimatePresence>
                                    {result && (
                                        <motion.div
                                            initial={{ scale: 0 }}
                                            animate={{ scale: 1 }}
                                            className="flex-shrink-0"
                                        >
                                            {isCorrect && (
                                                <div className="w-6 h-6 rounded-full bg-green-500 flex items-center justify-center">
                                                    <Check className="w-4 h-4 text-white" />
                                                </div>
                                            )}
                                            {isWrong && (
                                                <div className="w-6 h-6 rounded-full bg-red-500 flex items-center justify-center">
                                                    <X className="w-4 h-4 text-white" />
                                                </div>
                                            )}
                                        </motion.div>
                                    )}
                                </AnimatePresence>
                            </motion.button>
                        );
                    })}
                </div>
            </div>

            {/* Explanation (shown after answer) */}
            <AnimatePresence>
                {result && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: 'auto' }}
                        exit={{ opacity: 0, height: 0 }}
                        className="space-y-3"
                    >
                        <div className={`p-4 rounded-lg ${result.is_correct
                                ? 'bg-green-500/10 border border-green-500/20'
                                : 'bg-red-500/10 border border-red-500/20'
                            }`}>
                            <p className={`text-sm font-semibold mb-1 ${result.is_correct ? 'text-green-500' : 'text-red-500'
                                }`}>
                                {result.is_correct ? '✓ Correct!' : '✗ Incorrect'}
                            </p>
                            {!result.is_correct && (
                                <p className="text-sm text-foreground mb-2">
                                    Correct answer: <span className="font-medium">{result.correct_answer}</span>
                                </p>
                            )}
                            <p className="text-sm text-muted-foreground leading-relaxed">
                                <strong>Explanation:</strong> {result.explanation}
                            </p>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Submit Button */}
            {!result && (
                <div className="flex justify-end">
                    <Button
                        onClick={handleSubmit}
                        disabled={!selectedAnswer || isLoading}
                        className="bg-primary hover:bg-primary/90 gap-2"
                    >
                        {isLoading ? 'Checking...' : 'Submit Answer'}
                        {!isLoading && <ChevronRight className="w-4 h-4" />}
                    </Button>
                </div>
            )}
        </motion.div>
    );
};
