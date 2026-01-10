"""
Prompt Orchestration Layer

This module contains the three core LLM functions:
1. The Extractor: Parses user input into structured JSON
2. The Recruiter Persona: Generates follow-up questions for missing data
3. The Technical Examiner: Generates technical screening questions

Each function uses carefully crafted prompts to minimize hallucinations
and ensure consistent, high-quality outputs.
"""

from typing import Dict, List, Optional, Tuple, Any
import logging
import json
from pydantic import ValidationError

from talent_scout.services.groq_service import get_groq_service, GroqServiceError
from talent_scout.schemas import (
    CandidateProfileSchema,
    TechnicalQuestionsResponseSchema,
    RecruiterFollowUpSchema,
    sanitize_tech_stack
)

logger = logging.getLogger(__name__)


class PromptOrchestrator:
    """
    Orchestrates all prompt-based LLM operations for the hiring assistant.
    
    This class implements the three core functions with sophisticated
    prompting techniques to prevent hallucinations.
    """
    
    def __init__(self):
        """Initialize with Groq service"""
        self.groq_service = get_groq_service()
    
    # ====================================================================
    # 1. THE EXTRACTOR: Parse user input into structured JSON
    # ====================================================================
    
    def extract_candidate_info(
        self,
        user_message: str,
        current_profile: Dict[str, Any],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Tuple[CandidateProfileSchema, Dict[str, Any]]:
        """
        Extract structured candidate information from user message.
        
        This function uses few-shot prompting and strict JSON schema
        enforcement to prevent hallucinations.
        
        Args:
            user_message: The user's latest message
            current_profile: Current candidate profile dict
            conversation_history: Recent conversation for context
        
        Returns:
            Tuple of (updated_profile_schema, metadata)
        
        Raises:
            GroqServiceError: If extraction fails
        """
        # Build the system prompt
        system_prompt = """You are a highly accurate data extraction AI. Your ONLY job is to extract candidate information from conversation and return it as valid JSON.

CRITICAL RULES:
1. ONLY extract information EXPLICITLY stated by the candidate
2. NEVER make assumptions or infer information
3. If a field is not mentioned, leave it as null or empty
4. Return ONLY valid JSON, no additional text
5. Do NOT ask questions - only extract data

JSON Schema:
{
    "full_name": "string or null",
    "email": "valid email or null",
    "phone": "phone number or null",
    "location": "string or null",
    "years_experience": "integer or null",
    "tech_stack": ["array", "of", "technologies"],
    "position_applied": "string or null"
}

Examples:

User: "Hi, I'm John Doe and I'm applying for the Senior Developer role"
JSON: {"full_name": "John Doe", "email": null, "phone": null, "location": null, "years_experience": null, "tech_stack": [], "position_applied": "Senior Developer"}

User: "I have 5 years of experience with Python, Django, and React"
JSON: {"full_name": null, "email": null, "phone": null, "location": null, "years_experience": 5, "tech_stack": ["Python", "Django", "React"], "position_applied": null}

User: "My email is john@example.com and I'm based in San Francisco"
JSON: {"full_name": null, "email": "john@example.com", "phone": null, "location": "San Francisco", "years_experience": null, "tech_stack": [], "position_applied": null}

Now extract from the following message. Return ONLY the JSON object, nothing else."""

        # Prepare the user prompt with context
        current_profile_str = json.dumps(current_profile, indent=2)
        user_prompt = f"""Current Profile:
{current_profile_str}

New User Message: "{user_message}"

Extract any NEW information from the user message and merge with current profile. Return the complete updated profile as JSON."""

        try:
            # Call Groq with JSON mode
            extracted_json, metadata = self.groq_service.json_completion(
                system_prompt=system_prompt,
                user_message=user_prompt,
                conversation_history=conversation_history,
                temperature=0.1  # Very low for deterministic extraction
            )
            
            # Merge with current profile (preserve existing data)
            merged_profile = {**current_profile}
            
            for key, value in extracted_json.items():
                # Only update if new value is not null/empty
                if value is not None and value != "" and value != []:
                    merged_profile[key] = value
            
            # Sanitize tech_stack
            if 'tech_stack' in merged_profile:
                merged_profile['tech_stack'] = sanitize_tech_stack(
                    merged_profile['tech_stack']
                )
            
            # Validate with Pydantic
            profile_schema = CandidateProfileSchema(**merged_profile)
            
            logger.info(f"Successfully extracted profile data: {profile_schema.model_dump()}")
            
            return profile_schema, metadata
        
        except ValidationError as e:
            logger.error(f"Pydantic validation failed: {str(e)}")
            # Return current profile if validation fails
            return CandidateProfileSchema(**current_profile), {}
        
        except GroqServiceError as e:
            logger.error(f"Groq service error during extraction: {str(e)}")
            # Return current profile if API fails
            return CandidateProfileSchema(**current_profile), {}
    
    # ====================================================================
    # 2. THE RECRUITER PERSONA: Generate follow-up questions
    # ====================================================================
    
    def generate_recruiter_followup(
        self,
        current_profile: CandidateProfileSchema,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Tuple[str, List[str]]:
        """
        Generate a polite, conversational follow-up question for missing data.
        
        This function identifies missing fields and crafts appropriate
        questions to gather that information.
        
        Args:
            current_profile: Current candidate profile
            conversation_history: Recent conversation for context
        
        Returns:
            Tuple of (follow_up_question, list_of_missing_fields)
        """
        # Identify missing fields
        required_fields = {
            'full_name': 'full name',
            'email': 'email address',
            'phone': 'phone number',
            'location': 'current location or city',
            'years_experience': 'years of professional experience',
            'tech_stack': 'technical skills/tech stack',
            'position_applied': 'position you\'re applying for'
        }
        
        profile_dict = current_profile.model_dump()
        missing_fields = []
        
        for field, display_name in required_fields.items():
            value = profile_dict.get(field)
            if value is None or value == [] or value == "":
                missing_fields.append(display_name)
        
        # If nothing is missing, return completion message
        if not missing_fields:
            return "Thank you! I have all the information I need. Let's move forward.", []
        
        # Build system prompt for recruiter persona
        system_prompt = """You are a friendly, professional AI recruiter conducting an interview. Your goal is to gather missing information from the candidate in a warm, conversational manner.

RULES:
1. Ask for ONE missing field at a time (or a maximum of TWO related fields)
2. Be conversational and encouraging
3. Never sound robotic or repetitive
4. Acknowledge what they've already shared
5. Keep questions short and friendly
6. Return ONLY the question, no extra formatting

Examples:

Missing: email, phone
Output: "Great! Before we continue, could you please share your email address with me?"

Missing: years_experience, tech_stack
Output: "Wonderful! Now I'd love to know more about your technical background. How many years of professional experience do you have, and what technologies do you primarily work with?"

Missing: full_name
Output: "Perfect! To get started, may I have your full name?"

Missing: location
Output: "Thanks for that! Just out of curiosity, where are you currently based?"
"""

        user_prompt = f"""Current candidate profile:
{json.dumps(profile_dict, indent=2)}

Missing information: {', '.join(missing_fields)}

Generate a friendly follow-up question to ask for the MOST important missing field(s). Prioritize in this order:
1. full_name
2. email
3. phone
4. location
5. position_applied
6. years_experience
7. tech_stack

Return ONLY the question, nothing else."""

        try:
            # Call Groq
            response, _ = self.groq_service.chat_completion(
                system_prompt=system_prompt,
                user_message=user_prompt,
                conversation_history=conversation_history,
                temperature=0.7  # Higher for more natural conversation
            )
            
            logger.info(f"Generated recruiter follow-up: {response}")
            
            return response.strip(), missing_fields
        
        except GroqServiceError as e:
            logger.error(f"Groq service error during follow-up generation: {str(e)}")
            # Fallback to template-based question
            if 'full_name' in missing_fields:
                return "Could you please tell me your full name?", missing_fields
            elif 'email' in missing_fields:
                return "What's the best email address to reach you at?", missing_fields
            else:
                return "Could you tell me a bit more about yourself?", missing_fields
    
    # ====================================================================
    # 3. THE TECHNICAL EXAMINER: Generate technical screening questions
    # ====================================================================
    
    def generate_technical_questions(
        self,
        tech_stack: List[str],
        experience_level: str,
        position: str,
        count: int = 5
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Generate high-quality technical questions tailored to candidate.
        
        This function uses the candidate's tech stack and experience level
        to create relevant, challenging questions.
        
        Args:
            tech_stack: List of technologies candidate knows
            experience_level: junior/mid/senior/lead/architect
            position: Position they're applying for
            count: Number of questions to generate
        
        Returns:
            Tuple of (list_of_questions, metadata)
        """
        # Build system prompt
        system_prompt = f"""You are an expert technical interviewer with deep knowledge across all technology stacks. Your job is to generate exactly {count} high-quality technical interview questions.

CRITICAL RULES:
1. Generate EXACTLY {count} questions, no more, no less
2. Questions must be relevant to the candidate's tech stack
3. Difficulty must match the experience level
4. Questions should test DEPTH of knowledge, not just surface understanding
5. Avoid generic questions like "What is Python?"
6. Return ONLY valid JSON, no additional text

Experience Level Guidelines:
- junior (0-2 years): Fundamentals, basic concepts, simple problem-solving
- mid (2-5 years): Design patterns, best practices, real-world scenarios
- senior (5-8 years): Architecture decisions, trade-offs, optimization
- lead (8-12 years): System design, team leadership, complex problem-solving
- architect (12+ years): High-level architecture, scalability, strategic decisions

JSON Schema:
{{
    "questions": [
        {{
            "question": "The actual question text",
            "expected_topics": ["topic1", "topic2"],
            "difficulty": "easy|medium|hard|expert"
        }}
    ],
    "rationale": "Brief explanation of why these questions were chosen"
}}

Example for Senior Python Developer:
{{
    "questions": [
        {{
            "question": "Explain how Python's GIL affects multi-threaded performance and describe strategies to work around its limitations.",
            "expected_topics": ["GIL", "threading", "multiprocessing", "asyncio"],
            "difficulty": "hard"
        }},
        {{
            "question": "You need to design a caching layer for a high-traffic Django API. Walk me through your approach, including cache invalidation strategies.",
            "expected_topics": ["caching", "Redis", "cache invalidation", "Django"],
            "difficulty": "hard"
        }}
    ],
    "rationale": "These questions test deep understanding of Python performance and real-world Django architecture decisions."
}}"""

        user_prompt = f"""Generate {count} technical interview questions for:

Position: {position}
Experience Level: {experience_level}
Tech Stack: {', '.join(tech_stack)}

The questions should:
1. Cover different areas of their tech stack
2. Match their experience level
3. Be specific and practical
4. Test real-world knowledge

Return ONLY the JSON object."""

        try:
            # Call Groq with JSON mode
            questions_json, metadata = self.groq_service.json_completion(
                system_prompt=system_prompt,
                user_message=user_prompt,
                temperature=0.6  # Balanced for creativity + consistency
            )
            
            # Validate with Pydantic
            validated = TechnicalQuestionsResponseSchema(**questions_json)
            
            # Convert to list of dicts
            questions_list = [
                {
                    "question": q.question,
                    "expected_topics": q.expected_topics,
                    "difficulty": q.difficulty
                }
                for q in validated.questions
            ]
            
            logger.info(f"Generated {len(questions_list)} technical questions")
            
            return questions_list, metadata
        
        except ValidationError as e:
            logger.error(f"Pydantic validation failed for questions: {str(e)}")
            # Fallback to generic questions
            return self._get_fallback_questions(tech_stack, experience_level, count), {}
        
        except GroqServiceError as e:
            logger.error(f"Groq service error during question generation: {str(e)}")
            # Fallback to generic questions
            return self._get_fallback_questions(tech_stack, experience_level, count), {}
    
    def _get_fallback_questions(
        self,
        tech_stack: List[str],
        experience_level: str,
        count: int
    ) -> List[Dict[str, Any]]:
        """
        Hardcoded fallback questions when API fails.
        
        These are generic but still useful questions.
        """
        fallback_questions = [
            {
                "question": "Can you describe a challenging technical problem you've solved recently and walk me through your approach?",
                "expected_topics": ["problem-solving", "technical depth"],
                "difficulty": "medium"
            },
            {
                "question": f"How do you stay current with {', '.join(tech_stack[:2])} best practices and emerging patterns?",
                "expected_topics": ["learning", "best practices"],
                "difficulty": "easy"
            },
            {
                "question": "Describe a situation where you had to make a trade-off between code quality and delivery speed. How did you handle it?",
                "expected_topics": ["trade-offs", "decision-making"],
                "difficulty": "medium"
            },
            {
                "question": "What's your approach to code review? What do you look for when reviewing others' code?",
                "expected_topics": ["code quality", "collaboration"],
                "difficulty": "medium"
            },
            {
                "question": "Tell me about a time when you had to debug a particularly difficult issue. What was your methodology?",
                "expected_topics": ["debugging", "systematic thinking"],
                "difficulty": "medium"
            }
        ]
        
        return fallback_questions[:count]


# Singleton instance
_prompt_orchestrator_instance = None


def get_prompt_orchestrator() -> PromptOrchestrator:
    """Get singleton instance of PromptOrchestrator"""
    global _prompt_orchestrator_instance
    
    if _prompt_orchestrator_instance is None:
        _prompt_orchestrator_instance = PromptOrchestrator()
    
    return _prompt_orchestrator_instance
