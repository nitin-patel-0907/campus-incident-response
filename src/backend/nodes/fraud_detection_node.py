"""
Fraud Detection Node for Campus Incident Response System

This node analyzes incident reports to detect potentially fake or fraudulent submissions
using multiple detection techniques including pattern analysis, content validation,
and behavioral indicators.
"""

from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import re
import json
from dataclasses import dataclass
from pydantic import BaseModel, Field

from ..llm.multi_provider_client import multi_llm_client


@dataclass
class FraudIndicator:
    """Individual fraud indicator with score and explanation"""
    indicator_type: str
    score: float  # 0-100, higher = more suspicious
    confidence: float  # 0-100, confidence in this indicator
    description: str
    evidence: List[str]


class FraudAnalysisResult(BaseModel):
    """Result of fraud detection analysis"""
    is_likely_fake: bool = Field(description="Whether the report is likely fake")
    fraud_score: float = Field(description="Overall fraud score (0-100)")
    confidence_level: str = Field(description="Confidence level: low, medium, high")
    risk_category: str = Field(description="Risk category: low, medium, high, critical")
    indicators: List[Dict[str, Any]] = Field(description="List of fraud indicators found")
    recommendations: List[str] = Field(description="Recommended actions")
    verification_steps: List[str] = Field(description="Steps to verify authenticity")
    analysis_timestamp: str = Field(description="When analysis was performed")


class FraudDetectionNode:
    """
    Advanced fraud detection node that analyzes incident reports for authenticity
    """
    
    def __init__(self):
        self.name = "fraud_detection"
        self.description = "Analyzes incident reports to detect potentially fake submissions"
        
        # Fraud detection patterns and thresholds
        self.suspicious_patterns = {
            "generic_descriptions": [
                r"something happened",
                r"there was an incident",
                r"i saw something",
                r"it was bad",
                r"very serious situation"
            ],
            "vague_locations": [
                r"somewhere on campus",
                r"near the building",
                r"in the area",
                r"around here"
            ],
            "inconsistent_details": [
                r"i think",
                r"maybe",
                r"probably",
                r"not sure"
            ],
            "attention_seeking": [
                r"worst thing ever",
                r"never seen anything like it",
                r"most serious incident",
                r"everyone was shocked"
            ]
        }
        
        # Common fake report indicators
        self.fake_indicators = {
            "timing_patterns": ["submitted at unusual hours", "rapid successive submissions"],
            "content_patterns": ["copy-paste text", "template-like structure", "inconsistent details"],
            "behavioral_patterns": ["anonymous with no verification", "refuses follow-up contact"],
            "technical_patterns": ["same IP multiple reports", "automated submission patterns"]
        }
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing function for fraud detection
        """
        try:
            incident_data = state.get("incident_data", {})
            
            # Perform comprehensive fraud analysis
            fraud_analysis = await self.analyze_for_fraud(incident_data, state)
            
            # Update state with fraud analysis
            state["fraud_analysis"] = fraud_analysis
            state["fraud_score"] = fraud_analysis.fraud_score
            state["is_likely_fake"] = fraud_analysis.is_likely_fake
            
            # Add processing status
            state["fraud_detection_status"] = "completed"
            state["fraud_detection_timestamp"] = datetime.now().isoformat()
            
            return state
            
        except Exception as e:
            state["fraud_detection_status"] = "error"
            state["fraud_detection_error"] = str(e)
            
            # Provide fallback analysis
            state["fraud_analysis"] = FraudAnalysisResult(
                is_likely_fake=False,
                fraud_score=0.0,
                confidence_level="low",
                risk_category="unknown",
                indicators=[],
                recommendations=["Manual review recommended due to analysis error"],
                verification_steps=["Verify reporter identity", "Cross-check incident details"],
                analysis_timestamp=datetime.now().isoformat()
            )
            
            return state
    
    async def analyze_for_fraud(self, incident_data: Dict[str, Any], state: Dict[str, Any]) -> FraudAnalysisResult:
        """
        Comprehensive fraud analysis using multiple detection methods
        """
        indicators = []
        
        # 1. Content Analysis
        content_indicators = await self._analyze_content_authenticity(incident_data)
        indicators.extend(content_indicators)
        
        # 2. Pattern Analysis
        pattern_indicators = self._analyze_suspicious_patterns(incident_data)
        indicators.extend(pattern_indicators)
        
        # 3. Behavioral Analysis
        behavioral_indicators = self._analyze_behavioral_patterns(incident_data, state)
        indicators.extend(behavioral_indicators)
        
        # 4. Consistency Analysis
        consistency_indicators = self._analyze_internal_consistency(incident_data)
        indicators.extend(consistency_indicators)
        
        # 5. Temporal Analysis
        temporal_indicators = self._analyze_temporal_patterns(incident_data, state)
        indicators.extend(temporal_indicators)
        
        # 6. Technical Analysis
        technical_indicators = self._analyze_technical_patterns(state)
        indicators.extend(technical_indicators)
        
        # Calculate overall fraud score
        fraud_score = self._calculate_fraud_score(indicators)
        
        # Determine risk category and confidence
        risk_category, confidence_level = self._assess_risk_and_confidence(fraud_score, indicators)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(fraud_score, indicators)
        
        # Generate verification steps
        verification_steps = self._generate_verification_steps(fraud_score, indicators)
        
        return FraudAnalysisResult(
            is_likely_fake=fraud_score > 60.0,
            fraud_score=fraud_score,
            confidence_level=confidence_level,
            risk_category=risk_category,
            indicators=[{
                "type": ind.indicator_type,
                "score": ind.score,
                "confidence": ind.confidence,
                "description": ind.description,
                "evidence": ind.evidence
            } for ind in indicators],
            recommendations=recommendations,
            verification_steps=verification_steps,
            analysis_timestamp=datetime.now().isoformat()
        )
    
    async def _analyze_content_authenticity(self, incident_data: Dict[str, Any]) -> List[FraudIndicator]:
        """
        Use AI to analyze content authenticity and detect AI-generated or template text
        """
        indicators = []
        
        try:
            description = incident_data.get("description", "")
            if not description:
                return indicators
            
            # AI-powered content analysis
            analysis_prompt = f"""
            Analyze this incident report description for authenticity. Look for signs that it might be:
            1. AI-generated text
            2. Copy-pasted from templates
            3. Overly generic or vague
            4. Inconsistent or contradictory details
            5. Unusual language patterns
            
            Description: "{description}"
            
            Provide analysis in JSON format:
            {{
                "authenticity_score": 0-100,
                "ai_generated_likelihood": 0-100,
                "template_likelihood": 0-100,
                "vagueness_score": 0-100,
                "inconsistency_score": 0-100,
                "language_naturalness": 0-100,
                "specific_concerns": ["list", "of", "concerns"],
                "authentic_indicators": ["list", "of", "authentic", "elements"]
            }}
            """
            
            try:
                response = await multi_llm_client.generate_response(analysis_prompt)
                
                # Try to extract JSON from response
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group())
                    
                    # AI-generated content indicator
                    if analysis.get("ai_generated_likelihood", 0) > 70:
                        indicators.append(FraudIndicator(
                            indicator_type="ai_generated_content",
                            score=analysis["ai_generated_likelihood"],
                            confidence=80.0,
                            description="Content appears to be AI-generated",
                            evidence=analysis.get("specific_concerns", [])
                        ))
                    
                    # Template content indicator
                    if analysis.get("template_likelihood", 0) > 60:
                        indicators.append(FraudIndicator(
                            indicator_type="template_content",
                            score=analysis["template_likelihood"],
                            confidence=75.0,
                            description="Content appears to follow a template pattern",
                            evidence=analysis.get("specific_concerns", [])
                        ))
                    
                    # Vagueness indicator
                    if analysis.get("vagueness_score", 0) > 70:
                        indicators.append(FraudIndicator(
                            indicator_type="vague_content",
                            score=analysis["vagueness_score"],
                            confidence=70.0,
                            description="Content is unusually vague or non-specific",
                            evidence=analysis.get("specific_concerns", [])
                        ))
                    
                    # Inconsistency indicator
                    if analysis.get("inconsistency_score", 0) > 60:
                        indicators.append(FraudIndicator(
                            indicator_type="inconsistent_content",
                            score=analysis["inconsistency_score"],
                            confidence=85.0,
                            description="Content contains inconsistent or contradictory details",
                            evidence=analysis.get("specific_concerns", [])
                        ))
                        
            except Exception as ai_error:
                # Fallback to pattern-based analysis
                pass
            
        except Exception as e:
            pass
        
        return indicators
    
    def _analyze_suspicious_patterns(self, incident_data: Dict[str, Any]) -> List[FraudIndicator]:
        """
        Analyze text for suspicious patterns that indicate fake reports
        """
        indicators = []
        description = incident_data.get("description", "").lower()
        
        if not description:
            return indicators
        
        # Check for generic descriptions
        generic_matches = []
        for pattern in self.suspicious_patterns["generic_descriptions"]:
            if re.search(pattern, description):
                generic_matches.append(pattern)
        
        if generic_matches:
            indicators.append(FraudIndicator(
                indicator_type="generic_description",
                score=min(80.0, len(generic_matches) * 25),
                confidence=70.0,
                description="Description contains generic or template-like phrases",
                evidence=generic_matches
            ))
        
        # Check for vague locations
        vague_location_matches = []
        location = incident_data.get("location", "").lower()
        for pattern in self.suspicious_patterns["vague_locations"]:
            if re.search(pattern, location) or re.search(pattern, description):
                vague_location_matches.append(pattern)
        
        if vague_location_matches:
            indicators.append(FraudIndicator(
                indicator_type="vague_location",
                score=min(60.0, len(vague_location_matches) * 20),
                confidence=65.0,
                description="Location information is unusually vague",
                evidence=vague_location_matches
            ))
        
        # Check for uncertainty indicators
        uncertainty_matches = []
        for pattern in self.suspicious_patterns["inconsistent_details"]:
            matches = re.findall(pattern, description)
            uncertainty_matches.extend(matches)
        
        if len(uncertainty_matches) > 3:
            indicators.append(FraudIndicator(
                indicator_type="excessive_uncertainty",
                score=min(70.0, len(uncertainty_matches) * 10),
                confidence=60.0,
                description="Excessive use of uncertain language",
                evidence=uncertainty_matches
            ))
        
        # Check for attention-seeking language
        attention_seeking_matches = []
        for pattern in self.suspicious_patterns["attention_seeking"]:
            if re.search(pattern, description):
                attention_seeking_matches.append(pattern)
        
        if attention_seeking_matches:
            indicators.append(FraudIndicator(
                indicator_type="attention_seeking",
                score=min(50.0, len(attention_seeking_matches) * 15),
                confidence=55.0,
                description="Language appears designed to seek attention",
                evidence=attention_seeking_matches
            ))
        
        return indicators
    
    def _analyze_behavioral_patterns(self, incident_data: Dict[str, Any], state: Dict[str, Any]) -> List[FraudIndicator]:
        """
        Analyze behavioral patterns that might indicate fake reports
        """
        indicators = []
        
        # Check reporter information completeness
        reporter_info = incident_data.get("reporter_info", {})
        metadata = incident_data.get("metadata", {})
        
        # Anonymous reporting with no verification method
        if not reporter_info.get("name") and not reporter_info.get("university_id"):
            if not metadata.get("contact_method") and not metadata.get("verification_code"):
                indicators.append(FraudIndicator(
                    indicator_type="anonymous_unverifiable",
                    score=40.0,
                    confidence=60.0,
                    description="Anonymous report with no verification method",
                    evidence=["No reporter identification", "No contact method provided"]
                ))
        
        # Check for suspicious reporter patterns
        if reporter_info.get("university_id"):
            uni_id = reporter_info["university_id"]
            # Check for obviously fake IDs
            if re.match(r'^(test|fake|123|000)', uni_id.lower()):
                indicators.append(FraudIndicator(
                    indicator_type="fake_id_pattern",
                    score=85.0,
                    confidence=90.0,
                    description="University ID appears to be fake or test data",
                    evidence=[f"ID pattern: {uni_id}"]
                ))
        
        # Check for rapid successive submissions (would need session/IP tracking)
        submission_time = state.get("created_at")
        if submission_time:
            # This would be enhanced with actual session tracking
            pass
        
        return indicators
    
    def _analyze_internal_consistency(self, incident_data: Dict[str, Any]) -> List[FraudIndicator]:
        """
        Check for internal consistency within the report
        """
        indicators = []
        
        # Check severity vs description consistency
        severity = incident_data.get("severity", "").lower()
        description = incident_data.get("description", "").lower()
        incident_type = incident_data.get("incident_type", "").lower()
        
        # High severity but minimal description
        if severity in ["high", "critical"] and len(description) < 50:
            indicators.append(FraudIndicator(
                indicator_type="severity_description_mismatch",
                score=60.0,
                confidence=70.0,
                description="High severity incident with minimal description",
                evidence=[f"Severity: {severity}", f"Description length: {len(description)} chars"]
            ))
        
        # Incident type vs description consistency
        type_keywords = {
            "medical": ["injury", "hurt", "pain", "sick", "ambulance", "hospital"],
            "fire": ["smoke", "flame", "burn", "fire", "evacuation"],
            "theft": ["stolen", "missing", "took", "theft", "robbed"],
            "harassment": ["harass", "inappropriate", "uncomfortable", "unwanted"],
            "assault": ["attack", "hit", "violence", "assault", "fight"]
        }
        
        if incident_type in type_keywords:
            expected_keywords = type_keywords[incident_type]
            found_keywords = [kw for kw in expected_keywords if kw in description]
            
            if not found_keywords:
                indicators.append(FraudIndicator(
                    indicator_type="type_description_mismatch",
                    score=50.0,
                    confidence=65.0,
                    description=f"Incident type '{incident_type}' doesn't match description content",
                    evidence=[f"Expected keywords: {expected_keywords}", "No matching keywords found"]
                ))
        
        return indicators
    
    def _analyze_temporal_patterns(self, incident_data: Dict[str, Any], state: Dict[str, Any]) -> List[FraudIndicator]:
        """
        Analyze temporal patterns that might indicate fake reports
        """
        indicators = []
        
        # Check submission time vs incident time
        incident_date = incident_data.get("metadata", {}).get("date_time")
        submission_time = state.get("created_at")
        
        if incident_date and submission_time:
            try:
                incident_dt = datetime.fromisoformat(incident_date.replace('Z', '+00:00'))
                submission_dt = datetime.fromisoformat(submission_time.replace('Z', '+00:00'))
                
                # Remove timezone info for comparison
                incident_dt = incident_dt.replace(tzinfo=None)
                submission_dt = submission_dt.replace(tzinfo=None)
                
                time_diff = submission_dt - incident_dt
                
                # Incident reported as happening in the future
                if time_diff.total_seconds() < 0:
                    indicators.append(FraudIndicator(
                        indicator_type="future_incident",
                        score=90.0,
                        confidence=95.0,
                        description="Incident reported as happening in the future",
                        evidence=[f"Incident time: {incident_date}", f"Submission time: {submission_time}"]
                    ))
                
                # Very old incident (more than 30 days) reported now
                elif time_diff.days > 30:
                    indicators.append(FraudIndicator(
                        indicator_type="very_old_incident",
                        score=30.0,
                        confidence=50.0,
                        description="Very old incident being reported now",
                        evidence=[f"Time difference: {time_diff.days} days"]
                    ))
                    
            except Exception:
                pass
        
        # Check for unusual submission times (e.g., 3 AM submissions might be suspicious)
        if submission_time:
            try:
                submit_dt = datetime.fromisoformat(submission_time.replace('Z', '+00:00'))
                hour = submit_dt.hour
                
                # Submissions between 2 AM and 5 AM might be suspicious
                if 2 <= hour <= 5:
                    indicators.append(FraudIndicator(
                        indicator_type="unusual_submission_time",
                        score=20.0,
                        confidence=40.0,
                        description="Report submitted at unusual hours",
                        evidence=[f"Submission hour: {hour}:00"]
                    ))
            except Exception:
                pass
        
        return indicators
    
    def _analyze_technical_patterns(self, state: Dict[str, Any]) -> List[FraudIndicator]:
        """
        Analyze technical patterns that might indicate automated or fake submissions
        """
        indicators = []
        
        # Check for metadata that might indicate automation
        metadata = state.get("incident_data", {}).get("metadata", {})
        
        # Check for suspicious user agent patterns (would need to be passed from frontend)
        user_agent = metadata.get("user_agent", "")
        if user_agent:
            suspicious_agents = ["bot", "crawler", "automated", "script"]
            if any(agent in user_agent.lower() for agent in suspicious_agents):
                indicators.append(FraudIndicator(
                    indicator_type="suspicious_user_agent",
                    score=70.0,
                    confidence=80.0,
                    description="Suspicious user agent indicating automated submission",
                    evidence=[f"User agent: {user_agent}"]
                ))
        
        # Check for form completion time (too fast might indicate automation)
        form_start_time = metadata.get("form_start_time")
        form_submit_time = metadata.get("form_submit_time")
        
        if form_start_time and form_submit_time:
            try:
                start_dt = datetime.fromisoformat(form_start_time)
                submit_dt = datetime.fromisoformat(form_submit_time)
                completion_time = (submit_dt - start_dt).total_seconds()
                
                # Form completed too quickly (less than 30 seconds for a detailed report)
                if completion_time < 30:
                    indicators.append(FraudIndicator(
                        indicator_type="rapid_form_completion",
                        score=60.0,
                        confidence=70.0,
                        description="Form completed unusually quickly",
                        evidence=[f"Completion time: {completion_time} seconds"]
                    ))
            except Exception:
                pass
        
        return indicators
    
    def _calculate_fraud_score(self, indicators: List[FraudIndicator]) -> float:
        """
        Calculate overall fraud score based on indicators
        """
        if not indicators:
            return 0.0
        
        # Weighted scoring based on indicator confidence and severity
        total_weighted_score = 0.0
        total_weight = 0.0
        
        for indicator in indicators:
            weight = indicator.confidence / 100.0
            weighted_score = indicator.score * weight
            total_weighted_score += weighted_score
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        # Average weighted score
        base_score = total_weighted_score / total_weight
        
        # Apply multiplier based on number of indicators
        indicator_multiplier = min(1.5, 1.0 + (len(indicators) - 1) * 0.1)
        
        final_score = min(100.0, base_score * indicator_multiplier)
        return round(final_score, 1)
    
    def _assess_risk_and_confidence(self, fraud_score: float, indicators: List[FraudIndicator]) -> Tuple[str, str]:
        """
        Assess risk category and confidence level
        """
        # Risk category based on fraud score
        if fraud_score >= 80:
            risk_category = "critical"
        elif fraud_score >= 60:
            risk_category = "high"
        elif fraud_score >= 30:
            risk_category = "medium"
        else:
            risk_category = "low"
        
        # Confidence level based on indicator quality
        if not indicators:
            confidence_level = "low"
        else:
            avg_confidence = sum(ind.confidence for ind in indicators) / len(indicators)
            high_confidence_indicators = sum(1 for ind in indicators if ind.confidence >= 80)
            
            if avg_confidence >= 80 and high_confidence_indicators >= 2:
                confidence_level = "high"
            elif avg_confidence >= 60 and high_confidence_indicators >= 1:
                confidence_level = "medium"
            else:
                confidence_level = "low"
        
        return risk_category, confidence_level
    
    def _generate_recommendations(self, fraud_score: float, indicators: List[FraudIndicator]) -> List[str]:
        """
        Generate recommendations based on fraud analysis
        """
        recommendations = []
        
        if fraud_score >= 80:
            recommendations.extend([
                "URGENT: Manual review required before processing",
                "Contact reporter for verification if possible",
                "Flag for security team investigation",
                "Do not take automated actions based on this report"
            ])
        elif fraud_score >= 60:
            recommendations.extend([
                "Manual review recommended",
                "Verify reporter identity before proceeding",
                "Cross-check details with other sources",
                "Proceed with caution on any actions"
            ])
        elif fraud_score >= 30:
            recommendations.extend([
                "Standard verification procedures recommended",
                "Monitor for similar patterns",
                "Document any unusual aspects"
            ])
        else:
            recommendations.append("Report appears authentic, proceed with standard processing")
        
        # Add specific recommendations based on indicators
        indicator_types = [ind.indicator_type for ind in indicators]
        
        if "ai_generated_content" in indicator_types:
            recommendations.append("Verify with reporter that they personally wrote the description")
        
        if "anonymous_unverifiable" in indicator_types:
            recommendations.append("Attempt to establish contact method for verification")
        
        if "future_incident" in indicator_types:
            recommendations.append("Clarify incident timing with reporter")
        
        if "type_description_mismatch" in indicator_types:
            recommendations.append("Request additional details to clarify incident type")
        
        return recommendations
    
    def _generate_verification_steps(self, fraud_score: float, indicators: List[FraudIndicator]) -> List[str]:
        """
        Generate specific verification steps
        """
        steps = []
        
        # Basic verification steps
        steps.extend([
            "Verify reporter identity through university systems",
            "Cross-reference incident details with campus security logs",
            "Check for similar reports in the system"
        ])
        
        if fraud_score >= 60:
            steps.extend([
                "Contact reporter directly for additional information",
                "Verify incident location with facilities management",
                "Check surveillance footage if available",
                "Interview potential witnesses"
            ])
        
        if fraud_score >= 80:
            steps.extend([
                "Escalate to security team for investigation",
                "Document all verification attempts",
                "Consider IP address and device fingerprinting",
                "Review submission patterns for this reporter"
            ])
        
        # Add specific steps based on indicators
        indicator_types = [ind.indicator_type for ind in indicators]
        
        if "vague_location" in indicator_types:
            steps.append("Request specific location details from reporter")
        
        if "severity_description_mismatch" in indicator_types:
            steps.append("Ask reporter to provide more detailed description")
        
        if "rapid_form_completion" in indicator_types:
            steps.append("Verify reporter had sufficient time to provide accurate details")
        
        return steps


# Export the node class
__all__ = ["FraudDetectionNode", "FraudAnalysisResult", "FraudIndicator"]