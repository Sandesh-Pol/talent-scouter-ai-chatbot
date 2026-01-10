"""
MCQ Screening Service

Implements the 5+3 strategy for technical screening:
- Stage 1: 5 Multiple Choice Questions per skill
- Stage 2: 3 Open-ended objective questions
- Skill Rating: 5-star rating calculation

Uses Groq LLM for MCQ generation and evaluation.
"""

import json
import logging
from typing import Dict, List, Any, Tuple
from talent_scout.services.groq_service import get_groq_service, GroqServiceError

logger = logging.getLogger(__name__)


class MCQScreeningService:
    """
    Service for generating and evaluating MCQ-based technical screening.
    
    Features:
    - Generate 5 MCQs per skill
    - Generate 3 objective questions
    - Calculate 5-star skill ratings
    - Track candidate progress
    """
    
    def __init__(self):
        """Initialize the MCQ screening service"""
        self.groq_service = get_groq_service()
        self.mcqs_per_skill = 5
        self.objective_questions_count = 3
    
    def generate_mcqs_for_skill(
        self,
        skill: str,
        experience_level: str = "mid"
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Generate 5 MCQs for a specific technical skill.
        
        Args:
            skill: Technical skill (e.g., "Python", "React", "Django")
            experience_level: Candidate's experience level
        
        Returns:
            Tuple of (list of MCQ dictionaries, metadata)
        
        MCQ Format:
        {
            "question": "Question text",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
            "difficulty": "medium",
            "explanation": "Why this is the correct answer"
        }
        """
        system_prompt = f"""You are a technical interviewer generating multiple-choice questions for {skill}.

Generate exactly 5 MCQs for a {experience_level}-level candidate.

IMPORTANT: Respond with a valid JSON object in this exact format:
{{
    "mcqs": [
        {{
            "question": "Question text here",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_answer": "Option A",
            "difficulty": "easy|medium|hard",
            "explanation": "Brief explanation of the correct answer"
        }}
    ]
}}

Rules:
1. Questions should match the {experience_level} experience level
2. Questions must be technical and specific to {skill}
3. Each question must have exactly 4 options
4. correct_answer must be one of the options (exact match)
5. Mix difficulty levels (2 easy, 2 medium, 1 hard)
6. Focus on practical knowledge, not trivia
7. Avoid questions that are too broad or too narrow"""

        user_message = f"Generate 5 MCQs for {skill} at {experience_level} level."
        
        try:
            response_json, metadata = self.groq_service.json_completion(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.7  # Some creativity for varied questions
            )
            
            mcqs = response_json.get("mcqs", [])
            
            # Validate MCQs
            if len(mcqs) != self.mcqs_per_skill:
                logger.warning(
                    f"Expected {self.mcqs_per_skill} MCQs, got {len(mcqs)}. "
                    f"Padding or truncating."
                )
                # Truncate or repeat to get exactly 5
                if len(mcqs) > self.mcqs_per_skill:
                    mcqs = mcqs[:self.mcqs_per_skill]
                elif len(mcqs) < self.mcqs_per_skill:
                    # Repeat last MCQ if needed (shouldn't happen with good prompt)
                    while len(mcqs) < self.mcqs_per_skill:
                        mcqs.append(mcqs[-1] if mcqs else self._get_fallback_mcq(skill))
            
            # Add skill metadata to each MCQ
            for mcq in mcqs:
                mcq["skill"] = skill
            
            logger.info(f"Generated {len(mcqs)} MCQs for skill: {skill}")
            return mcqs, metadata
        
        except GroqServiceError as e:
            logger.error(f"Failed to generate MCQs for {skill}: {str(e)}")
            # Return fallback MCQs
            return self._get_fallback_mcqs(skill, experience_level), {}
    
    def generate_objective_questions(
        self,
        tech_stack: List[str],
        experience_level: str = "mid"
    ) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
        """
        Generate 3 open-ended objective questions for in-depth assessment.
        
        Args:
            tech_stack: List of technical skills
            experience_level: Candidate's experience level
        
        Returns:
            Tuple of (list of question dictionaries, metadata)
        
        Question Format:
        {
            "question": "Open-ended question text",
            "focus_skill": "Primary skill being assessed",
            "evaluation_criteria": "What to look for in the answer"
        }
        """
        system_prompt = f"""You are a technical interviewer creating open-ended questions to assess depth of knowledge.

Generate exactly 3 objective (open-ended) technical questions for a {experience_level}-level candidate with skills in: {', '.join(tech_stack)}.

IMPORTANT: Respond with a valid JSON object in this exact format:
{{
    "objective_questions": [
        {{
            "question": "Detailed question text",
            "focus_skill": "Primary skill",
            "evaluation_criteria": "Key points to evaluate in the answer"
        }}
    ]
}}

Rules:
1. Questions should be open-ended (no multiple choice)
2. Questions should assess real-world problem-solving
3. Each question should focus on one primary skill from the tech stack
4. Questions should encourage detailed, thoughtful responses
5. Avoid yes/no questions
6. Questions should match {experience_level} experience level
7. Focus on practical scenarios, system design, or best practices"""

        user_message = f"Generate 3 objective questions for skills: {', '.join(tech_stack[:3])}"  # Limit to top 3 skills
        
        try:
            response_json, metadata = self.groq_service.json_completion(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.8  # More creativity for diverse questions
            )
            
            questions = response_json.get("objective_questions", [])
            
            # Validate count
            if len(questions) != self.objective_questions_count:
                logger.warning(
                    f"Expected {self.objective_questions_count} questions, "
                    f"got {len(questions)}"
                )
                # Adjust to exactly 3
                if len(questions) > self.objective_questions_count:
                    questions = questions[:self.objective_questions_count]
                elif len(questions) < self.objective_questions_count:
                    while len(questions) < self.objective_questions_count:
                        questions.append(self._get_fallback_objective_question(tech_stack[0]))
            
            logger.info(f"Generated {len(questions)} objective questions")
            return questions, metadata
        
        except GroqServiceError as e:
            logger.error(f"Failed to generate objective questions: {str(e)}")
            return self._get_fallback_objective_questions(tech_stack), {}
    
    def evaluate_mcq_answer(
        self,
        mcq: Dict[str, Any],
        user_answer: str
    ) -> Dict[str, Any]:
        """
        Evaluate a single MCQ answer.
        
        Args:
            mcq: MCQ dictionary with question and correct_answer
            user_answer: User's selected answer
        
        Returns:
            Evaluation result with is_correct and score
        """
        correct_answer = mcq.get("correct_answer", "").strip()
        user_answer = user_answer.strip()
        
        is_correct = user_answer.lower() == correct_answer.lower()
        
        return {
            "is_correct": is_correct,
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "explanation": mcq.get("explanation", ""),
            "difficulty": mcq.get("difficulty", "medium"),
            "score": 1.0 if is_correct else 0.0
        }
    
    def evaluate_objective_answer(
        self,
        question: Dict[str, str],
        user_answer: str
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Evaluate an open-ended objective answer using LLM.
        
        Args:
            question: Question dictionary with evaluation criteria
            user_answer: User's text response
        
        Returns:
            Tuple of (evaluation result, metadata)
        
        Evaluation Format:
        {
            "score": 0.0 to 1.0,
            "rating": "poor|fair|good|excellent",
            "strengths": ["strength 1", "strength 2"],
            "weaknesses": ["weakness 1", "weakness 2"],
            "feedback": "Detailed feedback"
        }
        """
        system_prompt = f"""You are an expert technical interviewer evaluating a candidate's answer.

Question: {question['question']}
Evaluation Criteria: {question['evaluation_criteria']}

Candidate's Answer: {user_answer}

Evaluate the answer and respond with a valid JSON object in this exact format:
{{
    "score": 0.85,
    "rating": "excellent",
    "strengths": ["point 1", "point 2"],
    "weaknesses": ["point 1", "point 2"],
    "feedback": "Detailed constructive feedback"
}}

Scoring Guide:
- 0.0-0.4: poor (fundamental misunderstandings)
- 0.5-0.6: fair (basic understanding, missing depth)
- 0.7-0.8: good (solid understanding, minor gaps)
- 0.9-1.0: excellent (comprehensive, insightful)

Rating values: "poor", "fair", "good", "excellent"

Be fair and constructive. Give credit for correct concepts even if not perfectly articulated."""

        user_message = "Evaluate the candidate's answer based on the criteria."
        
        try:
            response_json, metadata = self.groq_service.json_completion(
                system_prompt=system_prompt,
                user_message=user_message,
                temperature=0.3  # Lower temperature for consistent evaluation
            )
            
            # Validate score is in range
            score = response_json.get("score", 0.5)
            if not (0.0 <= score <= 1.0):
                logger.warning(f"Invalid score {score}, clamping to [0, 1]")
                score = max(0.0, min(1.0, score))
                response_json["score"] = score
            
            return response_json, metadata
        
        except GroqServiceError as e:
            logger.error(f"Failed to evaluate objective answer: {str(e)}")
            # Return fallback evaluation
            return {
                "score": 0.5,
                "rating": "fair",
                "strengths": ["Answer provided"],
                "weaknesses": ["Unable to fully evaluate due to technical issues"],
                "feedback": "Technical evaluation unavailable. Manual review recommended."
            }, {}
    
    def calculate_skill_rating(
        self,
        mcq_results: List[Dict[str, Any]],
        objective_evaluations: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate 5-star rating for a skill based on MCQ and objective results.
        
        Args:
            mcq_results: List of MCQ evaluation results
            objective_evaluations: List of objective question evaluations (optional)
        
        Returns:
            Rating dictionary with stars, percentage, and breakdown
        
        Rating Format:
        {
            "stars": 4.5,
            "percentage": 85.0,
            "mcq_score": 0.8,
            "objective_score": 0.9,
            "grade": "A",
            "assessment": "Excellent understanding"
        }
        """
        # Calculate MCQ score
        if not mcq_results:
            mcq_score = 0.0
        else:
            mcq_score = sum(r["score"] for r in mcq_results) / len(mcq_results)
        
        # Calculate objective score
        if objective_evaluations:
            objective_score = sum(e["score"] for e in objective_evaluations) / len(objective_evaluations)
        else:
            objective_score = mcq_score  # Use MCQ score if no objectives
        
        # Weighted average: 60% MCQ, 40% Objective
        if objective_evaluations:
            overall_score = (mcq_score * 0.6) + (objective_score * 0.4)
        else:
            overall_score = mcq_score
        
        # Convert to 5-star rating
        stars = overall_score * 5.0
        percentage = overall_score * 100.0
        
        # Determine grade
        if percentage >= 90:
            grade = "A+"
            assessment = "Exceptional expertise"
        elif percentage >= 80:
            grade = "A"
            assessment = "Excellent understanding"
        elif percentage >= 70:
            grade = "B"
            assessment = "Good proficiency"
        elif percentage >= 60:
            grade = "C"
            assessment = "Satisfactory knowledge"
        elif percentage >= 50:
            grade = "D"
            assessment = "Basic familiarity"
        else:
            grade = "F"
            assessment = "Needs improvement"
        
        return {
            "stars": round(stars, 1),
            "percentage": round(percentage, 1),
            "mcq_score": round(mcq_score, 2),
            "objective_score": round(objective_score, 2),
            "grade": grade,
            "assessment": assessment,
            "total_questions": len(mcq_results) + len(objective_evaluations or []),
            "correct_mcqs": sum(1 for r in mcq_results if r["is_correct"])
        }
    
    # Fallback methods for when API fails
    
    def _get_fallback_mcq(self, skill: str) -> Dict[str, Any]:
        """Generate a basic fallback MCQ"""
        return {
            "question": f"What is your experience level with {skill}?",
            "options": ["Beginner", "Intermediate", "Advanced", "Expert"],
            "correct_answer": "Intermediate",
            "difficulty": "easy",
            "explanation": "This is a fallback question",
            "skill": skill
        }
    
    def _get_fallback_mcqs(self, skill: str, experience_level: str) -> List[Dict[str, Any]]:
        """Generate fallback MCQs when API fails"""
        return [self._get_fallback_mcq(skill) for _ in range(self.mcqs_per_skill)]
    
    def _get_fallback_objective_question(self, skill: str) -> Dict[str, str]:
        """Generate a basic fallback objective question"""
        return {
            "question": f"Describe a project where you used {skill} and the challenges you faced.",
            "focus_skill": skill,
            "evaluation_criteria": "Problem-solving ability, technical depth, practical experience"
        }
    
    def _get_fallback_objective_questions(self, tech_stack: List[str]) -> List[Dict[str, str]]:
        """Generate fallback objective questions"""
        return [
            self._get_fallback_objective_question(tech_stack[i % len(tech_stack)])
            for i in range(self.objective_questions_count)
        ]


# Singleton instance
_mcq_service_instance = None


def get_mcq_service() -> MCQScreeningService:
    """
    Get singleton instance of MCQScreeningService.
    """
    global _mcq_service_instance
    
    if _mcq_service_instance is None:
        _mcq_service_instance = MCQScreeningService()
    
    return _mcq_service_instance
