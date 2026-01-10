import { motion } from "framer-motion";
import { Check, UserCircle, Code2, Flag } from "lucide-react";

interface ProgressStepperProps {
  currentStep: number;
}

const steps = [
  { id: 1, label: "Profile Intake", icon: UserCircle },
  { id: 2, label: "Tech Screening", icon: Code2 },
  { id: 3, label: "Completion", icon: Flag },
];

export const ProgressStepper = ({ currentStep }: ProgressStepperProps) => {
  return (
    <motion.div 
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-2xl mx-auto"
    >
      <div className="glass-card p-4">
        <div className="flex items-center justify-between">
          {steps.map((step, index) => {
            const isActive = step.id === currentStep;
            const isCompleted = step.id < currentStep;
            const Icon = step.icon;
            
            return (
              <div key={step.id} className="flex items-center">
                {/* Step */}
                <div className="flex flex-col items-center">
                  <motion.div
                    initial={false}
                    animate={{
                      scale: isActive ? 1.1 : 1,
                      backgroundColor: isCompleted 
                        ? "hsl(160 84% 39%)" 
                        : isActive 
                          ? "hsl(160 84% 39% / 0.2)" 
                          : "hsl(220 15% 18%)",
                    }}
                    className={`
                      w-10 h-10 rounded-full flex items-center justify-center
                      border-2 transition-colors duration-300
                      ${isCompleted ? "border-primary" : isActive ? "border-primary" : "border-muted"}
                    `}
                  >
                    {isCompleted ? (
                      <Check className="w-5 h-5 text-primary-foreground" />
                    ) : (
                      <Icon className={`w-5 h-5 ${isActive ? "text-primary" : "text-muted-foreground"}`} />
                    )}
                  </motion.div>
                  <span className={`
                    mt-2 text-xs font-medium transition-colors
                    ${isActive ? "text-primary" : isCompleted ? "text-foreground" : "text-muted-foreground"}
                  `}>
                    {step.label}
                  </span>
                </div>

                {/* Connector Line */}
                {index < steps.length - 1 && (
                  <div className="flex-1 mx-4 h-0.5 relative overflow-hidden rounded-full bg-muted min-w-[60px]">
                    <motion.div
                      initial={{ width: "0%" }}
                      animate={{ 
                        width: isCompleted ? "100%" : isActive ? "50%" : "0%" 
                      }}
                      transition={{ duration: 0.5, ease: "easeOut" }}
                      className="absolute inset-y-0 left-0 bg-primary rounded-full"
                    />
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
};
