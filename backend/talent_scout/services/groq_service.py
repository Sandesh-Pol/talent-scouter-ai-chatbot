"""
Groq LLM Service

This module handles all interactions with the Groq API including:
1. Connection management with automatic retry logic
2. Error handling and fallback mechanisms
3. Token usage tracking
4. Response time monitoring
"""

from groq import Groq, APIError, RateLimitError, APIConnectionError
from django.conf import settings
import json
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from functools import wraps

logger = logging.getLogger(__name__)


class GroqServiceError(Exception):
    """Custom exception for Groq service errors"""
    pass


def retry_on_failure(max_retries=3, delay=1.0):
    """
    Decorator for automatic retry on API failures.
    
    Args:
        max_retries: Maximum number of retry attempts
        delay: Delay between retries in seconds (exponential backoff)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (APIConnectionError, RateLimitError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        sleep_time = delay * (2 ** attempt)  # Exponential backoff
                        logger.warning(
                            f"Groq API attempt {attempt + 1} failed: {str(e)}. "
                            f"Retrying in {sleep_time}s..."
                        )
                        time.sleep(sleep_time)
                    else:
                        logger.error(f"Groq API failed after {max_retries} attempts")
                except Exception as e:
                    # Don't retry on other exceptions
                    raise e
            
            raise GroqServiceError(f"Max retries exceeded: {str(last_exception)}")
        
        return wrapper
    return decorator


class GroqLLMService:
    """
    Service class for Groq LLM operations.
    
    Handles all LLM calls with proper error handling, retry logic,
    and fallback mechanisms.
    """
    
    def __init__(self):
        """Initialize the Groq client with API key from settings"""
        api_key = settings.GROQ_API_KEY
        
        if not api_key:
            raise GroqServiceError(
                "GROQ_API_KEY not found in settings. Please set it in your .env file."
            )
        
        self.client = Groq(api_key=api_key)
        self.model = settings.GROQ_MODEL
        self.max_tokens = settings.GROQ_MAX_TOKENS
        self.temperature = settings.GROQ_TEMPERATURE
        
        logger.info(f"GroqLLMService initialized with model: {self.model}")
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def _make_api_call(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Internal method to make actual Groq API call.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Override default temperature
            max_tokens: Override default max tokens
            response_format: Optional response format (e.g., {"type": "json_object"})
        
        Returns:
            Tuple of (response_content, metadata)
        
        Raises:
            GroqServiceError: If API call fails
        """
        start_time = time.time()
        
        try:
            # Prepare API call parameters
            api_params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature or self.temperature,
                "max_tokens": max_tokens or self.max_tokens,
            }
            
            # Add response format if specified (for JSON mode)
            if response_format:
                api_params["response_format"] = response_format
            
            # Make the API call
            response = self.client.chat.completions.create(**api_params)
            
            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # Extract response content
            content = response.choices[0].message.content
            
            # Build metadata
            metadata = {
                "model": response.model,
                "tokens_used": response.usage.total_tokens,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "response_time_ms": response_time_ms,
                "finish_reason": response.choices[0].finish_reason
            }
            
            logger.info(
                f"Groq API call successful. Tokens: {metadata['tokens_used']}, "
                f"Time: {response_time_ms}ms"
            )
            
            return content, metadata
        
        except APIError as e:
            logger.error(f"Groq API error: {str(e)}")
            raise GroqServiceError(f"API error: {str(e)}")
        
        except Exception as e:
            logger.error(f"Unexpected error in Groq API call: {str(e)}")
            raise GroqServiceError(f"Unexpected error: {str(e)}")
    
    def chat_completion(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Standard chat completion with conversation history support.
        
        Args:
            system_prompt: System prompt defining behavior
            user_message: Current user message
            conversation_history: Previous messages for context (optional)
            temperature: Override default temperature
            max_tokens: Override default max tokens
        
        Returns:
            Tuple of (assistant_response, metadata)
        """
        # Build messages array
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if provided (implementing buffer memory)
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return self._make_api_call(
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
    
    def json_completion(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.1  # Lower temperature for structured output
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Chat completion that enforces JSON response format.
        
        This is critical for preventing hallucinations in data extraction.
        
        Args:
            system_prompt: System prompt (should instruct to return JSON)
            user_message: Current user message
            conversation_history: Previous messages for context
            temperature: Lower temperature for more deterministic output
        
        Returns:
            Tuple of (parsed_json_dict, metadata)
        
        Raises:
            GroqServiceError: If response is not valid JSON
        """
        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        
        if conversation_history:
            messages.extend(conversation_history)
        
        messages.append({"role": "user", "content": user_message})
        
        # Make API call with JSON response format
        content, metadata = self._make_api_call(
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"}
        )
        
        # Parse JSON
        try:
            parsed_json = json.loads(content)
            return parsed_json, metadata
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {content}")
            raise GroqServiceError(f"Invalid JSON response: {str(e)}")
    
    def get_fallback_response(self, context: str = "general") -> str:
        """
        Hardcoded fallback responses when API fails.
        
        This ensures the system never breaks completely even if Groq is down.
        
        Args:
            context: Context to determine appropriate fallback
        
        Returns:
            Fallback response string
        """
        fallbacks = {
            "onboarding": (
                "Hello! 👋 Welcome to TalentScout. I'm your AI interviewer, "
                "and I'm excited to learn more about you today. Let's start with "
                "a quick introduction. Could you please tell me your full name "
                "and the position you're applying for?"
            ),
            "information_gathering": (
                "Thank you for sharing that! Could you please tell me more about "
                "your technical background? Specifically, I'd love to know about "
                "your years of experience and the technologies you work with."
            ),
            "technical_screening": (
                "Great! Now let's dive into some technical questions. "
                "Can you explain a challenging technical problem you've solved recently?"
            ),
            "closing": (
                "Thank you so much for taking the time to speak with me today! "
                "We'll review your responses and get back to you soon. "
                "Do you have any questions for us?"
            ),
            "general": (
                "I'm having trouble processing that right now. "
                "Could you please rephrase your response?"
            ),
            "error": (
                "I apologize, but I'm experiencing technical difficulties. "
                "Please try again in a moment, or contact support if the issue persists."
            )
        }
        
        return fallbacks.get(context, fallbacks["general"])


# Singleton instance
_groq_service_instance = None


def get_groq_service() -> GroqLLMService:
    """
    Get singleton instance of GroqLLMService.
    
    This ensures we reuse the same client across requests.
    """
    global _groq_service_instance
    
    if _groq_service_instance is None:
        try:
            _groq_service_instance = GroqLLMService()
        except GroqServiceError as e:
            logger.critical(f"Failed to initialize Groq service: {str(e)}")
            raise
    
    return _groq_service_instance
