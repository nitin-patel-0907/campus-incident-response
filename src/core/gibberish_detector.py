"""
Gibberish Detection System for Campus Incident Response
Automatically detects nonsensical text and marks it as spam
"""
import re
import string
from typing import Dict, Any, List, Tuple
from collections import Counter
import math


class GibberishDetector:
    """
    Advanced gibberish detection system that identifies nonsensical text
    using multiple linguistic and statistical analysis methods
    """
    
    def __init__(self):
        # Common English words for validation
        self.common_words = {
            'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it', 'for', 'not', 'on', 'with',
            'he', 'as', 'you', 'do', 'at', 'this', 'but', 'his', 'by', 'from', 'they', 'she', 'or', 'an',
            'will', 'my', 'one', 'all', 'would', 'there', 'their', 'what', 'so', 'up', 'out', 'if', 'about',
            'who', 'get', 'which', 'go', 'me', 'when', 'make', 'can', 'like', 'time', 'no', 'just', 'him',
            'know', 'take', 'people', 'into', 'year', 'your', 'good', 'some', 'could', 'them', 'see', 'other',
            'than', 'then', 'now', 'look', 'only', 'come', 'its', 'over', 'think', 'also', 'back', 'after',
            'use', 'two', 'how', 'our', 'work', 'first', 'well', 'way', 'even', 'new', 'want', 'because',
            'any', 'these', 'give', 'day', 'most', 'us', 'is', 'was', 'are', 'been', 'has', 'had', 'were',
            'said', 'each', 'which', 'their', 'time', 'will', 'about', 'if', 'up', 'out', 'many', 'then',
            'them', 'these', 'so', 'some', 'her', 'would', 'make', 'like', 'into', 'him', 'has', 'two',
            'more', 'very', 'what', 'know', 'just', 'first', 'get', 'over', 'think', 'where', 'much',
            'go', 'well', 'were', 'been', 'have', 'had', 'has', 'said', 'each', 'which', 'she', 'do',
            'how', 'their', 'if', 'will', 'up', 'other', 'about', 'out', 'many', 'then', 'them', 'these',
            'so', 'some', 'her', 'would', 'make', 'like', 'into', 'him', 'has', 'two', 'more', 'very',
            'what', 'know', 'just', 'first', 'get', 'over', 'think', 'where', 'much', 'go', 'well'
        }
        
        # Campus-specific words
        self.campus_words = {
            'student', 'campus', 'dorm', 'dormitory', 'class', 'professor', 'teacher', 'library', 'cafeteria',
            'building', 'room', 'hall', 'parking', 'security', 'safety', 'incident', 'report', 'emergency',
            'help', 'problem', 'issue', 'concern', 'harassment', 'bullying', 'theft', 'vandalism', 'assault',
            'medical', 'health', 'counseling', 'administration', 'staff', 'faculty', 'academic', 'residence',
            'dining', 'meal', 'food', 'study', 'exam', 'test', 'grade', 'course', 'semester', 'quarter',
            'university', 'college', 'school', 'education', 'learning', 'classroom', 'lecture', 'lab',
            'laboratory', 'office', 'hours', 'appointment', 'meeting', 'event', 'activity', 'club',
            'organization', 'sports', 'recreation', 'gym', 'fitness', 'pool', 'field', 'court'
        }
        
        # Combine all valid words
        self.valid_words = self.common_words.union(self.campus_words)
        
        # Gibberish patterns
        self.gibberish_patterns = [
            r'[a-zA-Z]{15,}',  # Very long words without spaces
            r'(.)\1{4,}',      # Repeated characters (aaaaa, bbbbb)
            r'[bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ]{6,}',  # Too many consonants
            r'[aeiouAEIOU]{5,}',  # Too many vowels
            r'[0-9]{10,}',     # Very long numbers
            r'[!@#$%^&*()]{3,}',  # Repeated special characters
        ]
        
        # Keyboard mashing patterns
        self.keyboard_patterns = [
            'qwerty', 'asdf', 'zxcv', 'qwertyuiop', 'asdfghjkl', 'zxcvbnm',
            'abcdef', '123456', '111111', '000000', 'aaaaaa', 'bbbbbb',
            'qqqqqq', 'wwwwww', 'eeeeee', 'rrrrrr', 'tttttt', 'yyyyyy'
        ]
        
        # Minimum thresholds
        self.min_word_length = 2
        self.min_sentence_length = 10
        self.min_valid_word_ratio = 0.3
        self.max_gibberish_score = 0.5  # Lowered from 0.7 to be more sensitive
    
    def detect_gibberish(self, text: str) -> Dict[str, Any]:
        """
        Comprehensive gibberish detection analysis
        
        Returns:
        {
            "is_gibberish": bool,
            "gibberish_score": float (0-1, higher = more gibberish),
            "confidence": float (0-1),
            "reasons": list of strings,
            "analysis": dict with detailed breakdown
        }
        """
        if not text or len(text.strip()) < 5:
            return {
                "is_gibberish": True,
                "gibberish_score": 1.0,
                "confidence": 0.95,
                "reasons": ["Text too short to be meaningful"],
                "analysis": {"text_length": len(text.strip())}
            }
        
        # Clean text for analysis
        cleaned_text = self._clean_text(text)
        
        # Run all detection methods
        analysis = {
            "original_length": len(text),
            "cleaned_length": len(cleaned_text),
            "word_count": len(cleaned_text.split()),
            "character_analysis": self._analyze_characters(cleaned_text),
            "word_analysis": self._analyze_words(cleaned_text),
            "pattern_analysis": self._analyze_patterns(cleaned_text),
            "linguistic_analysis": self._analyze_linguistics(cleaned_text),
            "keyboard_analysis": self._analyze_keyboard_mashing(cleaned_text),
            "repetition_analysis": self._analyze_repetition(cleaned_text)
        }
        
        # Calculate overall gibberish score
        gibberish_score, reasons = self._calculate_gibberish_score(analysis)
        
        # Determine if it's gibberish
        is_gibberish = gibberish_score > self.max_gibberish_score
        
        # Calculate confidence based on multiple factors
        confidence = self._calculate_confidence(analysis, gibberish_score)
        
        return {
            "is_gibberish": is_gibberish,
            "gibberish_score": round(gibberish_score, 3),
            "confidence": round(confidence, 3),
            "reasons": reasons,
            "analysis": analysis
        }
    
    def _clean_text(self, text: str) -> str:
        """Clean text for analysis"""
        # Remove extra whitespace and normalize
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove excessive punctuation but keep some
        text = re.sub(r'[!@#$%^&*()]{3,}', '***', text)
        return text.lower()
    
    def _analyze_characters(self, text: str) -> Dict[str, Any]:
        """Analyze character distribution"""
        if not text:
            return {"valid": False}
        
        total_chars = len(text)
        letters = sum(1 for c in text if c.isalpha())
        digits = sum(1 for c in text if c.isdigit())
        spaces = sum(1 for c in text if c.isspace())
        punctuation = sum(1 for c in text if c in string.punctuation)
        
        return {
            "total_chars": total_chars,
            "letter_ratio": letters / total_chars if total_chars > 0 else 0,
            "digit_ratio": digits / total_chars if total_chars > 0 else 0,
            "space_ratio": spaces / total_chars if total_chars > 0 else 0,
            "punctuation_ratio": punctuation / total_chars if total_chars > 0 else 0,
            "valid": letters > 0 and letters / total_chars > 0.5
        }
    
    def _analyze_words(self, text: str) -> Dict[str, Any]:
        """Analyze word structure and validity"""
        words = text.split()
        if not words:
            return {"valid": False, "valid_word_ratio": 0}
        
        valid_words = 0
        long_words = 0
        very_long_words = 0
        
        for word in words:
            # Remove punctuation for word analysis
            clean_word = re.sub(r'[^\w]', '', word)
            if len(clean_word) < self.min_word_length:
                continue
                
            if clean_word in self.valid_words:
                valid_words += 1
            
            if len(clean_word) > 12:
                long_words += 1
            if len(clean_word) > 20:
                very_long_words += 1
        
        valid_word_ratio = valid_words / len(words) if words else 0
        
        return {
            "total_words": len(words),
            "valid_words": valid_words,
            "valid_word_ratio": valid_word_ratio,
            "long_words": long_words,
            "very_long_words": very_long_words,
            "avg_word_length": sum(len(w) for w in words) / len(words) if words else 0,
            "valid": valid_word_ratio >= self.min_valid_word_ratio
        }
    
    def _analyze_patterns(self, text: str) -> Dict[str, Any]:
        """Analyze for gibberish patterns"""
        pattern_matches = []
        
        for pattern in self.gibberish_patterns:
            matches = re.findall(pattern, text)
            if matches:
                pattern_matches.extend(matches)
        
        return {
            "pattern_matches": len(pattern_matches),
            "patterns_found": pattern_matches[:5],  # First 5 matches
            "has_suspicious_patterns": len(pattern_matches) > 0
        }
    
    def _analyze_linguistics(self, text: str) -> Dict[str, Any]:
        """Analyze linguistic structure"""
        # Check for basic sentence structure
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Check for vowel/consonant balance
        vowels = sum(1 for c in text if c in 'aeiou')
        consonants = sum(1 for c in text if c.isalpha() and c not in 'aeiou')
        
        vowel_ratio = vowels / (vowels + consonants) if (vowels + consonants) > 0 else 0
        
        return {
            "sentence_count": len(sentences),
            "avg_sentence_length": sum(len(s) for s in sentences) / len(sentences) if sentences else 0,
            "vowel_ratio": vowel_ratio,
            "consonant_ratio": 1 - vowel_ratio if vowel_ratio > 0 else 0,
            "has_sentence_structure": len(sentences) > 0 and any(len(s) > self.min_sentence_length for s in sentences),
            "vowel_balance_ok": 0.2 <= vowel_ratio <= 0.6
        }
    
    def _analyze_keyboard_mashing(self, text: str) -> Dict[str, Any]:
        """Detect keyboard mashing patterns"""
        keyboard_matches = []
        
        for pattern in self.keyboard_patterns:
            if pattern in text:
                keyboard_matches.append(pattern)
        
        # Check for sequential characters
        sequential_count = 0
        for i in range(len(text) - 2):
            if text[i:i+3] in ['abc', 'bcd', 'cde', 'def', 'efg', 'fgh', 'ghi', 'hij', 'ijk', 'jkl', 'klm', 'lmn', 'mno', 'nop', 'opq', 'pqr', 'qrs', 'rst', 'stu', 'tuv', 'uvw', 'vwx', 'wxy', 'xyz']:
                sequential_count += 1
        
        return {
            "keyboard_patterns": keyboard_matches,
            "keyboard_pattern_count": len(keyboard_matches),
            "sequential_chars": sequential_count,
            "likely_keyboard_mashing": len(keyboard_matches) > 0 or sequential_count > 2
        }
    
    def _analyze_repetition(self, text: str) -> Dict[str, Any]:
        """Analyze character and word repetition"""
        # Character repetition
        char_counts = Counter(text.replace(' ', ''))
        max_char_count = max(char_counts.values()) if char_counts else 0
        repeated_chars = sum(1 for count in char_counts.values() if count > len(text) * 0.2)
        
        # Word repetition
        words = text.split()
        word_counts = Counter(words)
        max_word_count = max(word_counts.values()) if word_counts else 0
        repeated_words = sum(1 for count in word_counts.values() if count > 3)
        
        return {
            "max_char_repetition": max_char_count,
            "repeated_char_types": repeated_chars,
            "max_word_repetition": max_word_count,
            "repeated_word_types": repeated_words,
            "excessive_repetition": max_char_count > len(text) * 0.3 or repeated_chars > 3
        }
    
    def _calculate_gibberish_score(self, analysis: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Calculate overall gibberish score and reasons"""
        score = 0.0
        reasons = []
        
        # Character analysis (weight: 0.15)
        char_analysis = analysis["character_analysis"]
        if not char_analysis["valid"]:
            score += 0.15
            reasons.append("Invalid character distribution")
        elif char_analysis["letter_ratio"] < 0.5:
            score += 0.1
            reasons.append("Too few letters in text")
        
        # Word analysis (weight: 0.25)
        word_analysis = analysis["word_analysis"]
        if word_analysis["valid_word_ratio"] < 0.05:  # Very strict for obvious gibberish
            score += 0.25
            reasons.append("Very few recognizable words")
        elif word_analysis["valid_word_ratio"] < 0.2:  # More sensitive threshold
            score += 0.20
            reasons.append("Low ratio of recognizable words")
        elif word_analysis["valid_word_ratio"] < 0.4:
            score += 0.10
            reasons.append("Below average word recognition")
        
        if word_analysis["very_long_words"] > 0:
            score += 0.1
            reasons.append("Contains extremely long words")
        elif word_analysis["long_words"] > word_analysis["total_words"] * 0.3:
            score += 0.05
            reasons.append("Many unusually long words")
        
        # Pattern analysis (weight: 0.2)
        pattern_analysis = analysis["pattern_analysis"]
        if pattern_analysis["has_suspicious_patterns"]:
            pattern_score = min(0.2, pattern_analysis["pattern_matches"] * 0.05)
            score += pattern_score
            reasons.append(f"Contains {pattern_analysis['pattern_matches']} suspicious patterns")
        
        # Linguistic analysis (weight: 0.2)
        linguistic_analysis = analysis["linguistic_analysis"]
        if not linguistic_analysis["has_sentence_structure"]:
            score += 0.1
            reasons.append("Lacks proper sentence structure")
        
        if not linguistic_analysis["vowel_balance_ok"]:
            score += 0.1
            reasons.append("Unusual vowel/consonant balance")
        
        # Keyboard mashing (weight: 0.1)
        keyboard_analysis = analysis["keyboard_analysis"]
        if keyboard_analysis["likely_keyboard_mashing"]:
            score += 0.1
            reasons.append("Appears to be keyboard mashing")
        
        # Repetition analysis (weight: 0.1)
        repetition_analysis = analysis["repetition_analysis"]
        if repetition_analysis["excessive_repetition"]:
            score += 0.1
            reasons.append("Excessive character or word repetition")
        
        return min(score, 1.0), reasons
    
    def _calculate_confidence(self, analysis: Dict[str, Any], gibberish_score: float) -> float:
        """Calculate confidence in the gibberish detection"""
        confidence = 0.5  # Base confidence
        
        # Higher confidence for clear cases
        if gibberish_score > 0.8:
            confidence += 0.3
        elif gibberish_score < 0.2:
            confidence += 0.3
        
        # Text length affects confidence
        text_length = analysis["cleaned_length"]
        if text_length > 50:
            confidence += 0.1
        elif text_length < 10:
            confidence += 0.1  # Very short text is easier to classify
        
        # Word count affects confidence
        word_count = analysis["word_analysis"]["total_words"]
        if word_count > 10:
            confidence += 0.1
        
        return min(confidence, 1.0)


# Global instance
gibberish_detector = GibberishDetector()


def test_gibberish_detector():
    """Test the gibberish detector with various examples"""
    test_cases = [
        # Normal text
        ("I saw someone acting suspiciously near the library yesterday evening", False),
        ("There was a safety issue in the dormitory that needs attention", False),
        ("A student was harassed in the parking lot after class", False),
        
        # Gibberish text
        ("asdfghjkl qwerty zxcvbnm", True),
        ("aaaaaaaaaa bbbbbbbbbb cccccccccc", True),
        ("123456789012345678901234567890", True),
        ("qwertyuiopasdfghjklzxcvbnm", True),
        ("jfkdlsjfkldsjfkldsjfkldsjfklds", True),
        ("!!!!!!!!!!! @@@@@@@@@@ #########", True),
        
        # Edge cases
        ("a", True),  # Too short
        ("", True),   # Empty
        ("help help help help help help", False),  # Repetitive but valid
        ("very very very important emergency", False),  # Repetitive but meaningful
    ]
    
    print("🧪 Testing Gibberish Detector:")
    print("=" * 50)
    
    for text, expected in test_cases:
        result = gibberish_detector.detect_gibberish(text)
        status = "✅" if result["is_gibberish"] == expected else "❌"
        
        print(f"{status} Text: '{text[:30]}{'...' if len(text) > 30 else ''}'")
        print(f"   Expected: {expected}, Got: {result['is_gibberish']}")
        print(f"   Score: {result['gibberish_score']:.3f}, Confidence: {result['confidence']:.3f}")
        if result["reasons"]:
            print(f"   Reasons: {', '.join(result['reasons'][:2])}")
        print()


if __name__ == "__main__":
    test_gibberish_detector()