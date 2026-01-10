"""
Sentiment Analysis Service

Lightweight sentiment analysis to detect:
1. Candidate frustration
2. Candidate confusion
3. Need for intervention

Uses TextBlob for simple, fast sentiment analysis without
heavy ML dependencies.
"""

from textblob import TextBlob
from typing import Tuple, Optional
import logging
from django.conf import settings

from talent_scout.schemas import SentimentAnalysisSchema

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Lightweight sentiment analyzer for candidate messages.
    
    Detects emotional states that may require intervention from
    a more empathetic "Helpful Recruiter" response.
    """
    
    def __init__(self):
        """Initialize with configuration from settings"""
        self.frustration_threshold = settings.SENTIMENT_FRUSTRATION_THRESHOLD
        self.confusion_threshold = settings.SENTIMENT_CONFUSION_THRESHOLD
    
    def analyze(self, text: str) -> SentimentAnalysisSchema:
        """
        Analyze sentiment of a text message.
        
        Args:
            text: The message to analyze
        
        Returns:
            SentimentAnalysisSchema with analysis results
        """
        if not text or len(text.strip()) == 0:
            return SentimentAnalysisSchema(
                score=0.0,
                magnitude=0.0,
                is_frustrated=False,
                is_confused=False,
                intervention_needed=False
            )
        
        try:
            # Perform sentiment analysis with TextBlob
            blob = TextBlob(text)
            
            # Polarity: -1 (negative) to 1 (positive)
            polarity = blob.sentiment.polarity
            
            # Subjectivity: 0 (objective) to 1 (subjective)
            subjectivity = blob.sentiment.subjectivity
            
            # Check for frustration keywords
            frustration_keywords = [
                'frustrated', 'annoying', 'irritating', 'confusing',
                'difficult', 'hard', 'stuck', 'problem', 'issue',
                'wrong', 'error', 'fail', 'cant', "can't", 'confused',
                'don\'t understand', 'doesnt make sense', 'unclear'
            ]
            
            text_lower = text.lower()
            has_frustration_keywords = any(
                keyword in text_lower for keyword in frustration_keywords
            )
            
            # Determine emotional state
            is_frustrated = (
                polarity < self.frustration_threshold or 
                has_frustration_keywords
            )
            
            is_confused = (
                polarity < self.confusion_threshold and
                subjectivity > 0.5
            )
            
            # Check if short, negative responses (e.g., "no", "I don't know")
            is_short_negative = (
                len(text.split()) < 5 and
                polarity < 0
            )
            
            # Determine if intervention needed
            intervention_needed = is_frustrated or (is_confused and is_short_negative)
            
            # Generate suggested response if intervention needed
            suggested_response = None
            if intervention_needed:
                suggested_response = self._generate_intervention_response(
                    is_frustrated, is_confused
                )
            
            result = SentimentAnalysisSchema(
                score=polarity,
                magnitude=subjectivity,
                is_frustrated=is_frustrated,
                is_confused=is_confused,
                intervention_needed=intervention_needed,
                suggested_response=suggested_response
            )
            
            logger.info(
                f"Sentiment analysis: score={polarity:.2f}, "
                f"frustrated={is_frustrated}, confused={is_confused}, "
                f"intervention={intervention_needed}"
            )
            
            return result
        
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {str(e)}")
            # Return neutral sentiment on error
            return SentimentAnalysisSchema(
                score=0.0,
                magnitude=0.0,
                is_frustrated=False,
                is_confused=False,
                intervention_needed=False
            )
    
    def _generate_intervention_response(
        self,
        is_frustrated: bool,
        is_confused: bool
    ) -> str:
        """
        Generate empathetic intervention response.
        
        Args:
            is_frustrated: Whether candidate seems frustrated
            is_confused: Whether candidate seems confused
        
        Returns:
            Suggested empathetic response
        """
        if is_frustrated and is_confused:
            return (
                "I sense this might be a bit frustrating. No worries at all! "
                "Let me try to make this clearer. Would you like me to rephrase "
                "my question or approach this differently?"
            )
        elif is_frustrated:
            return (
                "I understand this process can be challenging. "
                "Take your time, and feel free to share your thoughts however "
                "feels most comfortable. There's no rush!"
            )
        elif is_confused:
            return (
                "It seems like that might not have been clear. "
                "Let me ask in a different way that might be easier to answer."
            )
        else:
            return (
                "I want to make sure we're on the same page. "
                "Is there anything I can clarify for you?"
            )
    
    def track_session_sentiment(
        self,
        messages: list,
        window_size: int = 3
    ) -> Tuple[float, bool]:
        """
        Track sentiment across recent messages in a session.
        
        This helps identify if a candidate is becoming increasingly
        frustrated over time.
        
        Args:
            messages: List of recent message dicts with 'content' key
            window_size: Number of recent messages to analyze
        
        Returns:
            Tuple of (average_sentiment, needs_intervention)
        """
        if not messages:
            return 0.0, False
        
        # Get last N messages
        recent_messages = messages[-window_size:]
        
        # Analyze each
        scores = []
        interventions_needed = []
        
        for msg in recent_messages:
            analysis = self.analyze(msg.get('content', ''))
            scores.append(analysis.score)
            interventions_needed.append(analysis.intervention_needed)
        
        # Calculate average sentiment
        avg_sentiment = sum(scores) / len(scores) if scores else 0.0
        
        # Check if multiple recent messages need intervention
        needs_intervention = sum(interventions_needed) >= 2
        
        logger.info(
            f"Session sentiment: avg={avg_sentiment:.2f}, "
            f"intervention_count={sum(interventions_needed)}"
        )
        
        return avg_sentiment, needs_intervention


# Singleton instance
_sentiment_analyzer_instance = None


def get_sentiment_analyzer() -> SentimentAnalyzer:
    """Get singleton instance of SentimentAnalyzer"""
    global _sentiment_analyzer_instance
    
    if _sentiment_analyzer_instance is None:
        _sentiment_analyzer_instance = SentimentAnalyzer()
    
    return _sentiment_analyzer_instance
