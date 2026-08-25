"""
Confidence Index Calculator for Campus Incident Response System
Analyzes multiple factors to determine AI confidence in autonomous resolution
"""
from typing import Dict, Any, List, Tuple
from datetime import datetime
import re


class ConfidenceIndexCalculator:
    """
    Calculates confidence index based on multiple factors:
    - Prompt/Report Quality (30%)
    - Image Authenticity (25%) 
    - Description Completeness (20%)
    - Incident Complexity (15%)
    - Historical Success Rate (10%)
    """
    
    def __init__(self):
        self.weights = {
            "prompt_quality": 0.30,
            "image_authenticity": 0.25,
            "description_completeness": 0.20,
            "incident_complexity": 0.15,
            "historical_success": 0.10
        }
        
        # Confidence thresholds (realistic for demonstration)
        self.AUTONOMOUS_THRESHOLD = 65.0  # Above this = AI resolves autonomously
        self.HUMAN_INTERVENTION_THRESHOLD = 45.0  # Below this = Human required
        # Between 45-65 = AI with human oversight
    
    def calculate_confidence_index(self, 
                                 structured_report: Dict[str, Any],
                                 extracted_entities: Dict[str, Any],
                                 image_analyses: List[Dict[str, Any]] = None,
                                 metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Calculate comprehensive confidence index
        
        Returns:
        {
            "overall_confidence": float (0-100),
            "confidence_level": str ("high", "medium", "low"),
            "resolution_recommendation": str ("autonomous", "supervised", "human_required"),
            "factor_scores": dict,
            "confidence_reasoning": list,
            "intervention_triggers": list
        }
        """
        
        # Calculate individual factor scores
        prompt_score = self._analyze_prompt_quality(structured_report, extracted_entities)
        image_score = self._analyze_image_authenticity(image_analyses or [])
        description_score = self._analyze_description_completeness(structured_report)
        complexity_score = self._analyze_incident_complexity(structured_report, extracted_entities)
        historical_score = self._analyze_historical_success(structured_report, metadata)
        
        # Calculate weighted overall confidence
        factor_scores = {
            "prompt_quality": prompt_score,
            "image_authenticity": image_score,
            "description_completeness": description_score,
            "incident_complexity": complexity_score,
            "historical_success": historical_score
        }
        
        overall_confidence = sum(
            score * self.weights[factor] 
            for factor, score in factor_scores.items()
        )
        
        # Determine confidence level and recommendation
        confidence_level = self._determine_confidence_level(overall_confidence)
        resolution_recommendation = self._determine_resolution_recommendation(overall_confidence)
        
        # Generate reasoning and intervention triggers
        confidence_reasoning = self._generate_confidence_reasoning(factor_scores, overall_confidence)
        intervention_triggers = self._identify_intervention_triggers(factor_scores, overall_confidence)
        
        return {
            "overall_confidence": round(overall_confidence, 2),
            "confidence_level": confidence_level,
            "resolution_recommendation": resolution_recommendation,
            "factor_scores": {k: round(v, 2) for k, v in factor_scores.items()},
            "confidence_reasoning": confidence_reasoning,
            "intervention_triggers": intervention_triggers,
            "threshold_analysis": {
                "autonomous_threshold": self.AUTONOMOUS_THRESHOLD,
                "human_intervention_threshold": self.HUMAN_INTERVENTION_THRESHOLD,
                "current_score": overall_confidence,
                "can_resolve_autonomously": overall_confidence >= self.AUTONOMOUS_THRESHOLD,
                "requires_human_intervention": overall_confidence < self.HUMAN_INTERVENTION_THRESHOLD
            }
        }
    
    def _analyze_prompt_quality(self, structured_report: Dict[str, Any], 
                               extracted_entities: Dict[str, Any]) -> float:
        """Analyze quality of the incident report prompt (0-100)"""
        score = 0.0
        
        # Check report completeness
        description = structured_report.get("description", "")
        if len(description) > 100:
            score += 25.0
        elif len(description) > 50:
            score += 15.0
        elif len(description) > 20:
            score += 10.0
        
        # Check for key incident details
        required_fields = ["incident_type", "location", "datetime", "severity"]
        filled_fields = sum(1 for field in required_fields 
                           if structured_report.get(field) and 
                           structured_report[field] not in ["Unknown", "not specified", ""])
        score += (filled_fields / len(required_fields)) * 25.0
        
        # Check entity extraction quality
        total_entities = sum(len(entities) for entities in extracted_entities.values())
        if total_entities >= 10:
            score += 20.0
        elif total_entities >= 5:
            score += 15.0
        elif total_entities >= 2:
            score += 10.0
        
        # Check for specific details and context
        description_lower = description.lower()
        detail_indicators = [
            "time", "date", "location", "person", "witness", "evidence",
            "before", "after", "during", "approximately", "around"
        ]
        detail_count = sum(1 for indicator in detail_indicators if indicator in description_lower)
        score += min(detail_count * 2.5, 15.0)
        
        # Check for emotional context and impact
        impact_indicators = [
            "felt", "scared", "unsafe", "concerned", "worried", "impact",
            "affected", "disturbed", "uncomfortable", "threatened"
        ]
        impact_count = sum(1 for indicator in impact_indicators if indicator in description_lower)
        score += min(impact_count * 3.0, 15.0)
        
        return min(score, 100.0)
    
    def _analyze_image_authenticity(self, image_analyses: List[Dict[str, Any]]) -> float:
        """Analyze authenticity and quality of uploaded images (0-100)"""
        if not image_analyses:
            return 60.0  # Neutral score for no images
        
        total_score = 0.0
        
        for image_analysis in image_analyses:
            image_score = 0.0
            
            # Check authenticity score
            auth_analysis = image_analysis.get("authenticity_analysis", {})
            auth_score = auth_analysis.get("authenticity_score", 50.0)
            image_score += auth_score * 0.4
            
            # Check real-world content score
            ai_analysis = image_analysis.get("ai_analysis", {})
            real_world_score = ai_analysis.get("real_world_score", 50.0)
            image_score += real_world_score * 0.3
            
            # Check for manipulation detection
            if not auth_analysis.get("manipulation_detected", True):
                image_score += 20.0
            
            # Check analysis confidence
            confidence = ai_analysis.get("confidence", 50.0)
            image_score += confidence * 0.1
            
            total_score += min(image_score, 100.0)
        
        return total_score / len(image_analyses)
    
    def _analyze_description_completeness(self, structured_report: Dict[str, Any]) -> float:
        """Analyze completeness and quality of incident description (0-100)"""
        score = 0.0
        description = structured_report.get("description", "")
        
        # Length-based scoring
        if len(description) >= 500:
            score += 30.0
        elif len(description) >= 200:
            score += 25.0
        elif len(description) >= 100:
            score += 20.0
        elif len(description) >= 50:
            score += 15.0
        else:
            score += 5.0
        
        # Check for 5 W's and H (Who, What, When, Where, Why, How)
        description_lower = description.lower()
        
        # Who indicators
        who_indicators = ["person", "student", "staff", "individual", "someone", "they", "he", "she"]
        if any(indicator in description_lower for indicator in who_indicators):
            score += 10.0
        
        # What indicators
        what_indicators = ["incident", "happened", "occurred", "event", "situation"]
        if any(indicator in description_lower for indicator in what_indicators):
            score += 10.0
        
        # When indicators
        when_indicators = ["time", "date", "today", "yesterday", "morning", "afternoon", "evening", "pm", "am"]
        if any(indicator in description_lower for indicator in when_indicators):
            score += 10.0
        
        # Where indicators
        where_indicators = ["location", "building", "room", "area", "place", "at", "in", "near"]
        if any(indicator in description_lower for indicator in where_indicators):
            score += 10.0
        
        # Why/How indicators
        why_how_indicators = ["because", "due to", "caused by", "reason", "how", "why", "resulted"]
        if any(indicator in description_lower for indicator in why_how_indicators):
            score += 10.0
        
        # Check for sequence and timeline
        sequence_indicators = ["first", "then", "next", "after", "before", "finally", "subsequently"]
        if any(indicator in description_lower for indicator in sequence_indicators):
            score += 10.0
        
        # Check for specific details
        detail_indicators = ["approximately", "around", "about", "exactly", "specifically", "particular"]
        if any(indicator in description_lower for indicator in detail_indicators):
            score += 10.0
        
        return min(score, 100.0)
    
    def _analyze_incident_complexity(self, structured_report: Dict[str, Any], 
                                   extracted_entities: Dict[str, Any]) -> float:
        """Analyze incident complexity (lower complexity = higher confidence) (0-100)"""
        complexity_score = 100.0  # Start high, reduce for complexity
        
        # Check incident type complexity
        incident_type = structured_report.get("incident_type", "").lower()
        high_complexity_types = ["assault", "sexual_harassment", "discrimination", "violence"]
        medium_complexity_types = ["harassment", "bullying", "theft", "vandalism"]
        
        if incident_type in high_complexity_types:
            complexity_score -= 30.0
        elif incident_type in medium_complexity_types:
            complexity_score -= 15.0
        
        # Check severity impact
        severity = structured_report.get("severity", "").lower()
        if severity == "critical":
            complexity_score -= 25.0
        elif severity == "high":
            complexity_score -= 15.0
        elif severity == "medium":
            complexity_score -= 5.0
        
        # Check number of involved parties
        people_entities = extracted_entities.get("people", [])
        if len(people_entities) > 5:
            complexity_score -= 20.0
        elif len(people_entities) > 3:
            complexity_score -= 10.0
        
        # Check for multiple locations
        location_entities = extracted_entities.get("locations", [])
        if len(location_entities) > 3:
            complexity_score -= 15.0
        elif len(location_entities) > 1:
            complexity_score -= 5.0
        
        # Check for legal implications
        description = structured_report.get("description", "").lower()
        legal_indicators = ["police", "law", "legal", "court", "lawsuit", "criminal", "illegal"]
        if any(indicator in description for indicator in legal_indicators):
            complexity_score -= 20.0
        
        return max(complexity_score, 0.0)
    
    def _analyze_historical_success(self, structured_report: Dict[str, Any], 
                                  metadata: Dict[str, Any]) -> float:
        """Analyze historical success rate for similar incidents (0-100)"""
        # Placeholder for historical analysis
        # In a real system, this would query historical incident data
        
        incident_type = structured_report.get("incident_type", "").lower()
        severity = structured_report.get("severity", "").lower()
        
        # Simulated historical success rates
        success_rates = {
            "harassment": {"low": 85.0, "medium": 75.0, "high": 60.0, "critical": 45.0},
            "theft": {"low": 90.0, "medium": 85.0, "high": 80.0, "critical": 70.0},
            "safety": {"low": 80.0, "medium": 70.0, "high": 55.0, "critical": 40.0},
            "vandalism": {"low": 95.0, "medium": 90.0, "high": 85.0, "critical": 75.0},
            "general": {"low": 80.0, "medium": 70.0, "high": 60.0, "critical": 50.0}
        }
        
        type_rates = success_rates.get(incident_type, success_rates["general"])
        return type_rates.get(severity, 70.0)
    
    def _determine_confidence_level(self, overall_confidence: float) -> str:
        """Determine confidence level based on score"""
        if overall_confidence >= 80.0:
            return "high"
        elif overall_confidence >= 60.0:
            return "medium"
        else:
            return "low"
    
    def _determine_resolution_recommendation(self, overall_confidence: float) -> str:
        """Determine resolution recommendation based on confidence score"""
        if overall_confidence >= self.AUTONOMOUS_THRESHOLD:
            return "autonomous"
        elif overall_confidence >= self.HUMAN_INTERVENTION_THRESHOLD:
            return "supervised"
        else:
            return "human_required"
    
    def _generate_confidence_reasoning(self, factor_scores: Dict[str, float], 
                                     overall_confidence: float) -> List[str]:
        """Generate human-readable reasoning for confidence score"""
        reasoning = []
        
        # Overall assessment
        if overall_confidence >= 80.0:
            reasoning.append("High confidence: All key factors indicate reliable incident analysis")
        elif overall_confidence >= 60.0:
            reasoning.append("Medium confidence: Most factors are reliable with some areas of concern")
        else:
            reasoning.append("Low confidence: Multiple factors indicate need for human verification")
        
        # Factor-specific reasoning
        for factor, score in factor_scores.items():
            if score >= 80.0:
                reasoning.append(f"Strong {factor.replace('_', ' ')}: {score:.1f}% - Excellent quality")
            elif score < 50.0:
                reasoning.append(f"Weak {factor.replace('_', ' ')}: {score:.1f}% - Requires attention")
        
        return reasoning
    
    def _identify_intervention_triggers(self, factor_scores: Dict[str, float], 
                                      overall_confidence: float) -> List[str]:
        """Identify specific triggers that require human intervention"""
        triggers = []
        
        if overall_confidence < self.HUMAN_INTERVENTION_THRESHOLD:
            triggers.append("Overall confidence below intervention threshold")
        
        if factor_scores["image_authenticity"] < 40.0:
            triggers.append("Image authenticity concerns detected")
        
        if factor_scores["prompt_quality"] < 30.0:
            triggers.append("Insufficient incident details provided")
        
        if factor_scores["incident_complexity"] < 40.0:
            triggers.append("High complexity incident requiring human judgment")
        
        if factor_scores["description_completeness"] < 40.0:
            triggers.append("Incomplete incident description")
        
        return triggers


# Global instance
confidence_calculator = ConfidenceIndexCalculator()