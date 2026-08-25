"""
Groq API-based Spam Detection for Campus Incident Response
Uses Groq's Llama model to detect spam and gibberish content
"""
import os
from typing import Dict, Any
import json


class GroqSpamDetector:
    """
    Uses Groq API to detect spam and gibberish content
    """
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            print("⚠️ GROQ_API_KEY not found in environment variables")
    
    def detect_spam(self, text: str) -> Dict[str, Any]:
        """
        Use Groq API to detect if text is spam or gibberish
        
        Returns:
        {
            "is_spam": bool,
            "confidence": float (0-1),
            "reason": str,
            "category": str ("gibberish", "spam", "legitimate"),
            "needs_human_review": bool
        }
        """
        try:
            if not self.api_key:
                return self._fallback_detection(text)
            
            # Import Groq client
            try:
                from groq import Groq
            except ImportError:
                print("⚠️ Groq library not installed. Install with: pip install groq")
                return self._fallback_detection(text)
            
            client = Groq(api_key=self.api_key)
            
            # Create prompt for spam detection
            prompt = f"""
You are a spam detection system for a campus incident reporting system. Analyze the following text and determine if it is:

1. LEGITIMATE: A real incident report that should be processed
2. GIBBERISH: Nonsensical text, keyboard mashing, random characters
3. SPAM: Irrelevant content, advertisements, test messages, or malicious content

Text to analyze: "{text}"

Respond with a JSON object in this exact format:
{{
    "category": "legitimate|gibberish|spam",
    "confidence": 0.95,
    "reason": "Brief explanation of why this is classified as such",
    "is_spam": true/false,
    "needs_human_review": true/false
}}

Guidelines:
- LEGITIMATE: Real incident reports about safety, harassment, emergencies, etc.
- GIBBERISH: Random characters, keyboard mashing (asdfgh, qwerty), repeated characters
- SPAM: Advertisements, irrelevant content, test messages, malicious content
- Set needs_human_review to true for GIBBERISH and SPAM
- Set is_spam to true for both GIBBERISH and SPAM
- Confidence should be 0.8-0.99 for clear cases, 0.5-0.79 for uncertain cases
"""

            # Call Groq API
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system", 
                        "content": "You are a precise spam detection system. Always respond with valid JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            # Parse response
            response_text = response.choices[0].message.content.strip()
            
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                
                # Validate and normalize result
                return {
                    "is_spam": result.get("is_spam", False),
                    "confidence": float(result.get("confidence", 0.5)),
                    "reason": result.get("reason", "AI analysis completed"),
                    "category": result.get("category", "unknown"),
                    "needs_human_review": result.get("needs_human_review", False),
                    "detection_method": "groq_api",
                    "model": "llama-3.1-8b-instant"
                }
            else:
                print(f"⚠️ Could not parse Groq response: {response_text}")
                return self._fallback_detection(text)
                
        except Exception as e:
            print(f"❌ Groq API error: {e}")
            return self._fallback_detection(text)
    
    def _fallback_detection(self, text: str) -> Dict[str, Any]:
        """Enhanced fallback detection when Groq API is not available"""
        text_lower = text.lower().strip()
        
        # Very basic gibberish detection
        if len(text_lower) < 5:
            return {
                "is_spam": True,
                "confidence": 0.9,
                "reason": "Text too short to be meaningful",
                "category": "gibberish",
                "needs_human_review": True,
                "detection_method": "fallback_heuristic"
            }
        
        # Check for obvious gibberish patterns
        gibberish_patterns = ['asdf', 'qwerty', 'zxcv', 'hjkl', 'mnbv', 'uiop']
        gibberish_count = sum(1 for pattern in gibberish_patterns if pattern in text_lower)
        if gibberish_count >= 2:
            return {
                "is_spam": True,
                "confidence": 0.85,
                "reason": "Contains multiple keyboard mashing patterns",
                "category": "gibberish", 
                "needs_human_review": True,
                "detection_method": "fallback_heuristic"
            }
        
        # Check for repeated characters (more aggressive)
        import re
        if re.search(r'(.)\1{4,}', text_lower):  # 5 or more repeated chars
            return {
                "is_spam": True,
                "confidence": 0.8,
                "reason": "Contains excessive character repetition",
                "category": "gibberish",
                "needs_human_review": True,
                "detection_method": "fallback_heuristic"
            }
        
        # Check for spam keywords
        spam_keywords = [
            'buy now', 'click here', 'amazing deals', 'limited time', 'call now',
            'free money', 'make money', 'work from home', 'guaranteed', 'act now',
            'special offer', 'discount', 'sale', 'cheap', 'lowest price'
        ]
        spam_count = sum(1 for keyword in spam_keywords if keyword in text_lower)
        if spam_count >= 2:
            return {
                "is_spam": True,
                "confidence": 0.8,
                "reason": "Contains multiple spam keywords",
                "category": "spam",
                "needs_human_review": True,
                "detection_method": "fallback_heuristic"
            }
        
        # Check for test/placeholder content
        test_patterns = ['test test', 'ignore this', 'just a test', 'testing 123']
        if any(pattern in text_lower for pattern in test_patterns):
            return {
                "is_spam": True,
                "confidence": 0.75,
                "reason": "Appears to be test or placeholder content",
                "category": "spam",
                "needs_human_review": True,
                "detection_method": "fallback_heuristic"
            }
        
        # Check for excessive repetition of words
        words = text_lower.split()
        if len(words) > 3:
            word_counts = {}
            for word in words:
                word_counts[word] = word_counts.get(word, 0) + 1
            
            # If any word appears more than 3 times in a short text, likely spam/gibberish
            max_repetition = max(word_counts.values()) if word_counts else 0
            if max_repetition > 3 and len(words) < 20:
                return {
                    "is_spam": True,
                    "confidence": 0.75,
                    "reason": "Contains excessive word repetition",
                    "category": "gibberish",
                    "needs_human_review": True,
                    "detection_method": "fallback_heuristic"
                }
        
        # Check for non-alphabetic content ratio
        if len(text_lower) > 10:
            alpha_chars = sum(1 for c in text_lower if c.isalpha())
            alpha_ratio = alpha_chars / len(text_lower)
            
            if alpha_ratio < 0.5:  # Less than 50% alphabetic characters
                return {
                    "is_spam": True,
                    "confidence": 0.7,
                    "reason": "Contains too many non-alphabetic characters",
                    "category": "gibberish",
                    "needs_human_review": True,
                    "detection_method": "fallback_heuristic"
                }
        
        # Default to legitimate
        return {
            "is_spam": False,
            "confidence": 0.6,
            "reason": "Appears to be legitimate content",
            "category": "legitimate",
            "needs_human_review": False,
            "detection_method": "fallback_heuristic"
        }


# Global instance
groq_spam_detector = GroqSpamDetector()


def test_groq_spam_detector():
    """Test the Groq spam detector"""
    
    test_cases = [
        # Legitimate reports
        ("I witnessed harassment in the library yesterday evening", "legitimate"),
        ("There was a safety issue in the dormitory that needs attention", "legitimate"),
        ("A student was being bullied in the cafeteria during lunch", "legitimate"),
        ("Fire emergency in building 3, please send help immediately", "legitimate"),
        
        # Gibberish
        ("asdfghjkl qwerty zxcvbnm", "gibberish"),
        ("aaaaaaaaaa bbbbbbbbbb cccccccccc", "gibberish"),
        ("jfkdlsjfkldsjfkldsjfkldsjfklds", "gibberish"),
        ("123456789012345678901234567890", "gibberish"),
        
        # Spam
        ("Buy cheap products now! Click here for amazing deals!", "spam"),
        ("Test test test 123", "spam"),
        ("This is just a test message ignore this", "spam"),
    ]
    
    print("🧪 Testing Groq Spam Detector")
    print("=" * 50)
    
    for text, expected_category in test_cases:
        result = groq_spam_detector.detect_spam(text)
        
        status = "✅" if result["category"] == expected_category else "❌"
        
        print(f"{status} Text: '{text[:40]}{'...' if len(text) > 40 else ''}'")
        print(f"   Expected: {expected_category}")
        print(f"   Got: {result['category']} (confidence: {result['confidence']:.2f})")
        print(f"   Reason: {result['reason']}")
        print(f"   Needs Review: {result['needs_human_review']}")
        print(f"   Method: {result['detection_method']}")
        print()


if __name__ == "__main__":
    test_groq_spam_detector()