import { motion } from "framer-motion";
import { Star, Award } from "lucide-react";

interface SkillRating {
    stars: number;
    percentage: number;
    grade: string;
    assessment: string;
}

interface SkillRatingsProps {
    skillRatings: Record<string, SkillRating>;
}

const StarRating = ({ rating }: { rating: number }) => {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

    return (
        <div className="flex items-center gap-0.5">
            {/* Full Stars */}
            {Array.from({ length: fullStars }).map((_, i) => (
                <Star
                    key={`full-${i}`}
                    className="w-4 h-4 fill-yellow-400 text-yellow-400"
                />
            ))}

            {/* Half Star */}
            {hasHalfStar && (
                <div className="relative">
                    <Star className="w-4 h-4 text-yellow-400" />
                    <div className="absolute inset-0 overflow-hidden w-1/2">
                        <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    </div>
                </div>
            )}

            {/* Empty Stars */}
            {Array.from({ length: emptyStars }).map((_, i) => (
                <Star
                    key={`empty-${i}`}
                    className="w-4 h-4 text-muted-foreground/30"
                />
            ))}
        </div>
    );
};

const getGradeColor = (grade: string) => {
    switch (grade) {
        case 'A':
            return 'text-green-500 bg-green-500/10 border-green-500/20';
        case 'B':
            return 'text-blue-500 bg-blue-500/10 border-blue-500/20';
        case 'C':
            return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20';
        case 'D':
            return 'text-orange-500 bg-orange-500/10 border-orange-500/20';
        default:
            return 'text-muted-foreground bg-secondary/50 border-border/30';
    }
};

export const SkillRatings = ({ skillRatings }: SkillRatingsProps) => {
    const skills = Object.entries(skillRatings);

    if (skills.length === 0) {
        return null;
    }

    return (
        <div className="space-y-3">
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="mb-4"
            >
                <h2 className="text-xs uppercase tracking-widest text-muted-foreground font-medium flex items-center gap-2">
                    <Award className="w-4 h-4 text-primary" />
                    Skill Ratings
                </h2>
            </motion.div>

            {skills.map(([skillName, rating], index) => (
                <motion.div
                    key={skillName}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 + index * 0.1, duration: 0.4 }}
                    className="glass-card group hover:border-primary/30 transition-all duration-300"
                >
                    <div className="space-y-3">
                        {/* Skill Header */}
                        <div className="flex items-center justify-between">
                            <span className="text-sm font-semibold text-foreground">
                                {skillName}
                            </span>
                            <span className={`px-2 py-0.5 text-xs font-bold rounded border ${getGradeColor(rating.grade)}`}>
                                {rating.grade}
                            </span>
                        </div>

                        {/* Star Rating */}
                        <div className="flex items-center justify-between">
                            <StarRating rating={rating.stars} />
                            <span className="text-xs font-medium text-primary">
                                {rating.percentage.toFixed(0)}%
                            </span>
                        </div>

                        {/* Assessment */}
                        {rating.assessment && (
                            <p className="text-xs text-muted-foreground italic leading-relaxed">
                                {rating.assessment}
                            </p>
                        )}

                        {/* Progress Bar */}
                        <div className="w-full h-1.5 bg-secondary rounded-full overflow-hidden">
                            <motion.div
                                className="h-full bg-gradient-to-r from-primary to-primary/60"
                                initial={{ width: 0 }}
                                animate={{ width: `${rating.percentage}%` }}
                                transition={{ duration: 1, delay: 0.5 + index * 0.1 }}
                            />
                        </div>
                    </div>
                </motion.div>
            ))}
        </div>
    );
};
