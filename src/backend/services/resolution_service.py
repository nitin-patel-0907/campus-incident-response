"""
Safety-First Incident Resolution Service

Implements comprehensive resolution logic based on threat level, authenticity,
anonymity, and safety validation to ensure incidents are only resolved when
it's safe and appropriate to do so.
"""

from typing import Dict, Any, Optional, Tuple
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ThreatLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuthenticityLevel(Enum):
    HIGH_CONFIDENCE = "high_confidence"
    MEDIUM_CONFIDENCE = "medium_confidence"
    LOW_CONFIDENCE = "low_confidence"
    SUSPICIOUS_OR_UNVERIFIABLE = "suspicious_or_unverifiable"


class SafetyValidationStatus(Enum):
    APPROVED = "approved"
    MODIFIED = "modified"
    BLOCKED = "blocked"


class ExecutorStatus(Enum):
    COMPLETED = "completed"
    PARTIAL = "partial"
    BLOCKED = "blocked"
    NOT_STARTED = "not_started"


class IncidentStatus(Enum):
    RESOLVED = "resolved"
    UNRESOLVED = "unresolved"
    UNDER_REVIEW = "under_review"


class ResolutionReason(Enum):
    LOW_RISK_CREDIBLE = "Low risk, credible report, no further action required"
    ACTION_COMPLETED = "Action completed successfully"
    HIGH_RISK_HUMAN_REQUIRED = "High-risk incidents require human confirmation"
    ANONYMOUS_VERIFICATION = "Anonymous report requires verification"
    EVIDENCE_VERIFICATION = "Evidence requires human verification"
    HIGH_RISK_LOW_CONFIDENCE = "High risk with low confidence requires human judgment"
    SAFETY_VALIDATION_FAILED = "Safety or policy validation failed"
    PENDING_HUMAN_REVIEW = "Under Review – Awaiting Verification"


class IncidentResolutionService:
    """
    Service for determining incident resolution status based on safety-first principles
    """
    
    def __init__(self):
        self.name = "incident_resolution_service"
    
    def determine_resolution_status(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine incident resolution status based on comprehensive safety rules
        
        Args:
            incident_data: Complete incident information
            
        Returns:
            Dict containing resolution status, reason, and metadata
        """
        try:
            # Extract core data signals
            signals = self._extract_core_signals(incident_data)
            
            # Apply resolution rules in priority order
            resolution_result = self._apply_resolution_rules(signals)
            
            # Add metadata and timestamps
            resolution_result.update({
                'determined_at': datetime.now().isoformat(),
                'signals_used': signals,
                'rule_applied': resolution_result.get('rule_applied', 'unknown')
            })
            
            logger.info(f"Resolution determined for incident {incident_data.get('incident_id', 'unknown')}: "
                       f"{resolution_result['status']} - {resolution_result['reason']}")
            
            return resolution_result
            
        except Exception as e:
            logger.error(f"Error determining resolution status: {e}")
            # Default to unresolved for safety
            return {
                'status': IncidentStatus.UNRESOLVED.value,
                'reason': "Error in resolution determination - defaulting to human review",
                'human_intervention_required': True,
                'rule_applied': 'error_fallback',
                'determined_at': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def _extract_core_signals(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize core data signals from incident data"""
        
        # Extract threat level
        threat_level = self._determine_threat_level(incident_data)
        
        # Extract authenticity level
        authenticity_level = self._determine_authenticity_level(incident_data)
        
        # Extract anonymous flag
        anonymous_flag = self._extract_anonymous_flag(incident_data)
        
        # Extract safety validation status
        safety_validation_status = self._extract_safety_validation_status(incident_data)
        
        # Extract executor status
        executor_status = self._extract_executor_status(incident_data)
        
        # Check for human intervention requirement
        human_intervention_required = self._check_human_intervention_required(incident_data)
        
        return {
            'threat_level': threat_level,
            'authenticity_level': authenticity_level,
            'anonymous_flag': anonymous_flag,
            'safety_validation_status': safety_validation_status,
            'executor_status': executor_status,
            'human_intervention_required': human_intervention_required,
            'has_files': self._has_uploaded_files(incident_data),
            'file_authenticity': self._assess_file_authenticity(incident_data)
        }
    
    def _determine_threat_level(self, incident_data: Dict[str, Any]) -> str:
        """Determine threat level based on incident type and severity"""
        
        severity = incident_data.get('severity', '').lower()
        incident_type = incident_data.get('incident_type', '').lower()
        
        # Critical threats
        if severity == 'critical':
            return ThreatLevel.CRITICAL.value
        
        # High threat incidents - be more specific about what constitutes high threat
        high_threat_types = ['assault', 'fire', 'medical', 'violence']
        if (severity == 'high' or 
            any(threat_type in incident_type for threat_type in high_threat_types)):
            return ThreatLevel.HIGH.value
        
        # Medium threat incidents - be more specific
        medium_threat_types = ['harassment', 'security', 'substance']
        if (severity == 'medium' and 
            any(threat_type in incident_type for threat_type in medium_threat_types)):
            return ThreatLevel.MEDIUM.value
        
        # Theft is medium only if severity is medium or high
        if 'theft' in incident_type and severity in ['medium', 'high']:
            return ThreatLevel.MEDIUM.value
        
        # Low threat: maintenance, academic misconduct, minor issues
        low_threat_types = ['maintenance', 'academic', 'other']
        if (severity == 'low' or 
            any(threat_type in incident_type for threat_type in low_threat_types)):
            return ThreatLevel.LOW.value
        
        # Default to medium for safety (conservative approach)
        return ThreatLevel.MEDIUM.value
    
    def _determine_authenticity_level(self, incident_data: Dict[str, Any]) -> str:
        """Determine authenticity level based on report consistency and confidence"""
        
        # Check for file authenticity issues
        file_authenticity = self._assess_file_authenticity(incident_data)
        if file_authenticity == 'suspicious_or_unverifiable':
            return AuthenticityLevel.SUSPICIOUS_OR_UNVERIFIABLE.value
        
        # Check report consistency factors
        description = incident_data.get('description', '')
        has_detailed_description = len(description) > 50
        has_location = bool(incident_data.get('location', '').strip())
        has_timestamp = bool(incident_data.get('incident_date_time') or 
                           incident_data.get('submission_timestamp'))
        
        # Calculate confidence score
        confidence_factors = [
            has_detailed_description,
            has_location,
            has_timestamp,
            not incident_data.get('anonymous', False),  # Non-anonymous adds confidence
            incident_data.get('form_submission', False)  # Form submission adds structure
        ]
        
        confidence_score = sum(confidence_factors) / len(confidence_factors)
        
        if confidence_score >= 0.8:
            return AuthenticityLevel.HIGH_CONFIDENCE.value
        elif confidence_score >= 0.6:
            return AuthenticityLevel.MEDIUM_CONFIDENCE.value
        elif confidence_score >= 0.4:
            return AuthenticityLevel.LOW_CONFIDENCE.value
        else:
            return AuthenticityLevel.SUSPICIOUS_OR_UNVERIFIABLE.value
    
    def _extract_anonymous_flag(self, incident_data: Dict[str, Any]) -> bool:
        """Extract anonymous flag from incident data"""
        return incident_data.get('anonymous', False) or incident_data.get('anonymous_report', False)
    
    def _extract_safety_validation_status(self, incident_data: Dict[str, Any]) -> str:
        """Extract safety validation status"""
        # Check if safety node has processed this incident
        if hasattr(incident_data, 'safety_assessment'):
            safety_assessment = incident_data.safety_assessment
            if safety_assessment.get('blocked', False):
                return SafetyValidationStatus.BLOCKED.value
            elif safety_assessment.get('modified', False):
                return SafetyValidationStatus.MODIFIED.value
            else:
                return SafetyValidationStatus.APPROVED.value
        
        # Check for compliance report
        compliance_report = incident_data.get('compliance_report')
        if compliance_report:
            if compliance_report.get('violations'):
                return SafetyValidationStatus.BLOCKED.value
            elif compliance_report.get('warnings'):
                return SafetyValidationStatus.MODIFIED.value
            else:
                return SafetyValidationStatus.APPROVED.value
        
        # Default to approved if no safety concerns detected
        return SafetyValidationStatus.APPROVED.value
    
    def _extract_executor_status(self, incident_data: Dict[str, Any]) -> str:
        """Extract executor status from execution summary"""
        execution_summary = incident_data.get('execution_summary')
        if not execution_summary:
            return ExecutorStatus.NOT_STARTED.value
        
        overall_status = execution_summary.get('overall_status', '').lower()
        success_rate = execution_summary.get('success_rate', 0)
        
        if overall_status == 'completed' and success_rate >= 90:
            return ExecutorStatus.COMPLETED.value
        elif overall_status == 'completed' and success_rate >= 50:
            return ExecutorStatus.PARTIAL.value
        elif overall_status in ['blocked', 'failed']:
            return ExecutorStatus.BLOCKED.value
        else:
            return ExecutorStatus.NOT_STARTED.value
    
    def _check_human_intervention_required(self, incident_data: Dict[str, Any]) -> bool:
        """Check if human intervention is already required"""
        return incident_data.get('requires_human_review', False)
    
    def _has_uploaded_files(self, incident_data: Dict[str, Any]) -> bool:
        """Check if incident has uploaded files"""
        return (incident_data.get('has_images', False) or 
                bool(incident_data.get('file_analyses')) or
                bool(incident_data.get('image_analysis')))
    
    def _assess_file_authenticity(self, incident_data: Dict[str, Any]) -> str:
        """Assess authenticity of uploaded files"""
        if not self._has_uploaded_files(incident_data):
            return 'no_files'
        
        file_analyses = incident_data.get('file_analyses', [])
        if not file_analyses:
            return 'no_analysis'
        
        # Check if any files require human review
        suspicious_files = [f for f in file_analyses if f.get('requires_human_review', False)]
        if suspicious_files:
            return 'suspicious_or_unverifiable'
        
        # Check confidence scores
        confidence_scores = [f.get('confidence_score', 50) for f in file_analyses]
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            if avg_confidence >= 80:
                return 'high_confidence'
            elif avg_confidence >= 60:
                return 'medium_confidence'
            else:
                return 'low_confidence'
        
        return 'medium_confidence'
    
    def _apply_resolution_rules(self, signals: Dict[str, Any]) -> Dict[str, Any]:
        """Apply resolution rules in priority order"""
        
        # RULE 7: Safety Agent Override (Highest Priority)
        if signals['safety_validation_status'] != SafetyValidationStatus.APPROVED.value:
            return {
                'status': IncidentStatus.UNRESOLVED.value,
                'reason': ResolutionReason.SAFETY_VALIDATION_FAILED.value,
                'human_intervention_required': True,
                'rule_applied': 'rule_7_safety_override',
                'details': f"Safety validation status: {signals['safety_validation_status']}"
            }
        
        # RULE 5: File/Image Authenticity Check
        if (signals['has_files'] and 
            signals['file_authenticity'] == 'suspicious_or_unverifiable'):
            return {
                'status': IncidentStatus.UNRESOLVED.value,
                'reason': ResolutionReason.EVIDENCE_VERIFICATION.value,
                'human_intervention_required': True,
                'rule_applied': 'rule_5_file_authenticity',
                'details': "Uploaded files require human verification"
            }
        
        # RULE 3: High or Critical Threat (Default)
        if signals['threat_level'] in [ThreatLevel.HIGH.value, ThreatLevel.CRITICAL.value]:
            return {
                'status': IncidentStatus.UNRESOLVED.value,
                'reason': ResolutionReason.HIGH_RISK_HUMAN_REQUIRED.value,
                'human_intervention_required': True,
                'rule_applied': 'rule_3_high_critical_threat',
                'details': f"Threat level: {signals['threat_level']}"
            }
        
        # RULE 6: Low Authenticity + High Threat (already covered by Rule 3, but keep for completeness)
        if (signals['threat_level'] in [ThreatLevel.HIGH.value, ThreatLevel.CRITICAL.value] and
            signals['authenticity_level'] in [AuthenticityLevel.LOW_CONFIDENCE.value, 
                                            AuthenticityLevel.SUSPICIOUS_OR_UNVERIFIABLE.value]):
            return {
                'status': IncidentStatus.UNRESOLVED.value,
                'reason': ResolutionReason.HIGH_RISK_LOW_CONFIDENCE.value,
                'human_intervention_required': True,
                'rule_applied': 'rule_6_low_auth_high_threat',
                'details': f"Threat: {signals['threat_level']}, Authenticity: {signals['authenticity_level']}"
            }
        
        # RULE 4: Anonymous Report Handling
        if (signals['anonymous_flag'] and 
            signals['threat_level'] in [ThreatLevel.MEDIUM.value, ThreatLevel.HIGH.value, ThreatLevel.CRITICAL.value]):
            return {
                'status': IncidentStatus.UNRESOLVED.value,
                'reason': ResolutionReason.ANONYMOUS_VERIFICATION.value,
                'human_intervention_required': True,
                'rule_applied': 'rule_4_anonymous_handling',
                'details': f"Anonymous report with {signals['threat_level']} threat level"
            }
        
        # RULE 2: Medium Threat + Credible Report
        if (signals['threat_level'] == ThreatLevel.MEDIUM.value and
            signals['authenticity_level'] in [AuthenticityLevel.HIGH_CONFIDENCE.value, 
                                            AuthenticityLevel.MEDIUM_CONFIDENCE.value] and
            signals['executor_status'] == ExecutorStatus.COMPLETED.value and
            signals['safety_validation_status'] == SafetyValidationStatus.APPROVED.value and
            not signals['anonymous_flag']):  # Add anonymous check here too
            return {
                'status': IncidentStatus.RESOLVED.value,
                'reason': ResolutionReason.ACTION_COMPLETED.value,
                'human_intervention_required': False,
                'rule_applied': 'rule_2_medium_credible',
                'details': "Medium threat with credible report and completed actions"
            }
        
        # RULE 1: Low Threat + High Authenticity
        if (signals['threat_level'] == ThreatLevel.LOW.value and
            signals['authenticity_level'] == AuthenticityLevel.HIGH_CONFIDENCE.value and
            signals['safety_validation_status'] == SafetyValidationStatus.APPROVED.value):
            return {
                'status': IncidentStatus.RESOLVED.value,
                'reason': ResolutionReason.LOW_RISK_CREDIBLE.value,
                'human_intervention_required': False,
                'rule_applied': 'rule_1_low_threat_high_auth',
                'details': "Low risk, credible report with safety approval"
            }
        
        # Default: Unresolved for safety
        return {
            'status': IncidentStatus.UNRESOLVED.value,
            'reason': ResolutionReason.PENDING_HUMAN_REVIEW.value,
            'human_intervention_required': True,
            'rule_applied': 'default_safety_first',
            'details': "Does not meet criteria for automatic resolution"
        }
    
    def get_resolution_explanation(self, resolution_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate detailed explanation for resolution decision"""
        
        rule_applied = resolution_result.get('rule_applied', 'unknown')
        signals = resolution_result.get('signals_used', {})
        
        explanation = {
            'status': resolution_result['status'],
            'reason': resolution_result['reason'],
            'rule_applied': rule_applied,
            'factors_considered': [],
            'why_unresolved': None,
            'next_steps': []
        }
        
        # Add factors considered
        explanation['factors_considered'] = [
            f"Threat Level: {signals.get('threat_level', 'unknown')}",
            f"Authenticity: {signals.get('authenticity_level', 'unknown')}",
            f"Anonymous Report: {'Yes' if signals.get('anonymous_flag') else 'No'}",
            f"Safety Validation: {signals.get('safety_validation_status', 'unknown')}",
            f"Executor Status: {signals.get('executor_status', 'unknown')}"
        ]
        
        if signals.get('has_files'):
            explanation['factors_considered'].append(
                f"File Authenticity: {signals.get('file_authenticity', 'unknown')}"
            )
        
        # Add explanation for unresolved status
        if resolution_result['status'] == IncidentStatus.UNRESOLVED.value:
            explanation['why_unresolved'] = self._get_unresolved_explanation(rule_applied, signals)
            explanation['next_steps'] = self._get_next_steps(rule_applied)
        
        return explanation
    
    def _get_unresolved_explanation(self, rule_applied: str, signals: Dict[str, Any]) -> str:
        """Get detailed explanation for why incident is unresolved"""
        
        explanations = {
            'rule_7_safety_override': "The safety validation process identified policy or safety concerns that require human review.",
            'rule_5_file_authenticity': "Uploaded files require human verification to ensure authenticity and prevent misuse.",
            'rule_3_high_critical_threat': "High-risk incidents always require human confirmation to ensure appropriate response.",
            'rule_6_low_auth_high_threat': "High-risk incidents with low confidence reports need human judgment to verify authenticity.",
            'rule_4_anonymous_handling': "Anonymous reports for medium or higher threats require verification to prevent false escalation.",
            'default_safety_first': "The incident does not meet all criteria for automatic resolution, so human review is required for safety."
        }
        
        return explanations.get(rule_applied, "Human review required to ensure appropriate handling.")
    
    def _get_next_steps(self, rule_applied: str) -> list:
        """Get next steps for unresolved incidents"""
        
        next_steps = {
            'rule_7_safety_override': [
                "Review safety and policy compliance",
                "Verify incident details",
                "Determine appropriate response"
            ],
            'rule_5_file_authenticity': [
                "Verify authenticity of uploaded files",
                "Review file metadata and content",
                "Confirm incident details"
            ],
            'rule_3_high_critical_threat': [
                "Assess threat level and urgency",
                "Coordinate appropriate response",
                "Verify all safety measures"
            ],
            'rule_4_anonymous_handling': [
                "Verify incident through alternative means",
                "Assess credibility of anonymous report",
                "Determine response without compromising anonymity"
            ],
            'default_safety_first': [
                "Review all incident details",
                "Verify authenticity and threat level",
                "Determine appropriate resolution"
            ]
        }
        
        return next_steps.get(rule_applied, [
            "Review incident details",
            "Verify information",
            "Determine appropriate action"
        ])


# Global service instance
resolution_service = IncidentResolutionService()