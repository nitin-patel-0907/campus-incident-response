"""
Human Review Service - Manages incidents requiring human oversight
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum
import json

class ReviewReason(Enum):
    """Reasons why an incident requires human review"""
    ANONYMOUS_REPORT = "anonymous_report"
    SUSPICIOUS_FILE = "suspicious_file"
    UNVERIFIABLE_FILE = "unverifiable_file"
    HIGH_RISK_CONTENT = "high_risk_content"
    POLICY_VIOLATION = "policy_violation"
    MANUAL_ESCALATION = "manual_escalation"

class ReviewStatus(Enum):
    """Status of human review"""
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ESCALATED = "escalated"
    ADDITIONAL_INFO_REQUIRED = "additional_info_required"

class ReviewAction(Enum):
    """Actions that can be taken during review"""
    APPROVE_AND_CONTINUE = "approve_and_continue"
    REQUEST_MORE_INFO = "request_more_info"
    MARK_INVALID = "mark_invalid"
    ESCALATE_TO_ADMIN = "escalate_to_admin"
    APPROVE_WITH_CONDITIONS = "approve_with_conditions"

class HumanReviewService:
    """Service for managing human review queue and decisions"""
    
    def __init__(self):
        # In a real implementation, this would use a database
        self.review_queue = {}
        self.review_history = {}
        
    def requires_human_review(self, incident_data: Dict[str, Any], file_analyses: List[Dict[str, Any]] = None) -> Tuple[bool, List[ReviewReason], str]:
        """
        Determine if an incident requires human review
        
        Args:
            incident_data: Incident data from intake
            file_analyses: List of file authenticity analyses
            
        Returns:
            Tuple of (requires_review, reasons, explanation)
        """
        reasons = []
        explanations = []
        
        # Check 1: Anonymous report
        # Handle both direct anonymous flag and reporter_info structure
        is_anonymous = (
            incident_data.get("reporter_info", {}).get("anonymous", False) or
            incident_data.get("anonymous", False)
        )
        
        if is_anonymous:
            reasons.append(ReviewReason.ANONYMOUS_REPORT)
            explanations.append("Report submitted anonymously")
        
        # Check 2: Suspicious or unverifiable files
        if file_analyses:
            for file_analysis in file_analyses:
                if file_analysis.get("requires_human_review", False):
                    status = file_analysis.get("authenticity_status", "")
                    if "Suspicious" in status:
                        reasons.append(ReviewReason.SUSPICIOUS_FILE)
                        explanations.append(f"File '{file_analysis.get('filename', 'unknown')}' shows suspicious patterns")
                    elif "Unverifiable" in status:
                        reasons.append(ReviewReason.UNVERIFIABLE_FILE)
                        explanations.append(f"File '{file_analysis.get('filename', 'unknown')}' cannot be verified")
        
        # Check 3: High-risk content patterns
        # Look for description in multiple possible locations
        description = (
            incident_data.get("description", "") or
            incident_data.get("report", "") or
            ""
        ).lower()
        
        high_risk_keywords = [
            "weapon", "bomb", "threat", "kill", "harm", "violence", 
            "suicide", "self-harm", "drug", "illegal"
        ]
        
        if any(keyword in description for keyword in high_risk_keywords):
            reasons.append(ReviewReason.HIGH_RISK_CONTENT)
            explanations.append("Report contains high-risk content requiring verification")
        
        # Check 4: Severity and type combination
        severity = incident_data.get("severity", "").lower()
        incident_type = incident_data.get("incident_type", "").lower()
        
        if severity == "critical" and incident_type in ["assault", "medical", "fire"]:
            # Critical incidents might need human verification for proper response
            if incident_data.get("reporter_info", {}).get("anonymous", False):
                # Already covered by anonymous check, but add specific note
                explanations.append("Critical anonymous report requires additional verification")
        
        requires_review = len(reasons) > 0
        explanation = "; ".join(explanations) if explanations else "No human review required"
        
        return requires_review, reasons, explanation
    
    def add_to_review_queue(self, incident_id: str, incident_data: Dict[str, Any], 
                           reasons: List[ReviewReason], explanation: str,
                           file_analyses: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Add an incident to the human review queue
        
        Args:
            incident_id: Unique incident identifier
            incident_data: Full incident data
            reasons: List of reasons requiring review
            explanation: Human-readable explanation
            file_analyses: File authenticity analyses if any
            
        Returns:
            Review queue entry
        """
        review_entry = {
            "incident_id": incident_id,
            "created_at": datetime.now().isoformat(),
            "status": ReviewStatus.PENDING.value,
            "reasons": [reason.value for reason in reasons],
            "explanation": explanation,
            "priority": self._calculate_priority(incident_data, reasons),
            "incident_data": incident_data,
            "file_analyses": file_analyses or [],
            "reviewer_id": None,
            "review_started_at": None,
            "review_completed_at": None,
            "review_decision": None,
            "review_notes": "",
            "escalation_level": 0
        }
        
        self.review_queue[incident_id] = review_entry
        
        # Log the review requirement
        print(f"🔍 Incident {incident_id} added to human review queue")
        print(f"   Reasons: {', '.join([r.value for r in reasons])}")
        print(f"   Priority: {review_entry['priority']}")
        
        return review_entry
    
    def _calculate_priority(self, incident_data: Dict[str, Any], reasons: List[ReviewReason]) -> str:
        """Calculate review priority based on incident data and reasons"""
        
        severity = incident_data.get("severity", "").lower()
        incident_type = incident_data.get("incident_type", "").lower()
        
        # High priority conditions
        if (severity == "critical" or 
            incident_type in ["assault", "medical", "fire"] or
            ReviewReason.HIGH_RISK_CONTENT in reasons):
            return "high"
        
        # Medium priority conditions
        if (severity == "high" or
            ReviewReason.SUSPICIOUS_FILE in reasons or
            len(reasons) > 2):
            return "medium"
        
        # Default to low priority
        return "low"
    
    def get_review_queue(self, priority_filter: Optional[str] = None, 
                        status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get incidents in the review queue
        
        Args:
            priority_filter: Filter by priority (high, medium, low)
            status_filter: Filter by status
            
        Returns:
            List of review queue entries
        """
        queue = list(self.review_queue.values())
        
        if priority_filter:
            queue = [entry for entry in queue if entry["priority"] == priority_filter]
        
        if status_filter:
            queue = [entry for entry in queue if entry["status"] == status_filter]
        
        # Sort by priority and creation time
        priority_order = {"high": 0, "medium": 1, "low": 2}
        queue.sort(key=lambda x: (priority_order.get(x["priority"], 3), x["created_at"]))
        
        return queue
    
    def start_review(self, incident_id: str, reviewer_id: str) -> Dict[str, Any]:
        """
        Start reviewing an incident
        
        Args:
            incident_id: Incident to review
            reviewer_id: ID of the reviewer
            
        Returns:
            Updated review entry
        """
        if incident_id not in self.review_queue:
            raise ValueError(f"Incident {incident_id} not found in review queue")
        
        entry = self.review_queue[incident_id]
        entry["status"] = ReviewStatus.IN_REVIEW.value
        entry["reviewer_id"] = reviewer_id
        entry["review_started_at"] = datetime.now().isoformat()
        
        return entry
    
    def complete_review(self, incident_id: str, action: ReviewAction, 
                       notes: str = "", conditions: List[str] = None) -> Dict[str, Any]:
        """
        Complete a review with a decision
        
        Args:
            incident_id: Incident being reviewed
            action: Review action taken
            notes: Reviewer notes
            conditions: Any conditions if approved with conditions
            
        Returns:
            Completed review entry
        """
        if incident_id not in self.review_queue:
            raise ValueError(f"Incident {incident_id} not found in review queue")
        
        entry = self.review_queue[incident_id]
        entry["review_completed_at"] = datetime.now().isoformat()
        entry["review_decision"] = action.value
        entry["review_notes"] = notes
        
        if conditions:
            entry["approval_conditions"] = conditions
        
        # Update status based on action
        if action == ReviewAction.APPROVE_AND_CONTINUE:
            entry["status"] = ReviewStatus.APPROVED.value
        elif action == ReviewAction.APPROVE_WITH_CONDITIONS:
            entry["status"] = ReviewStatus.APPROVED.value
        elif action == ReviewAction.MARK_INVALID:
            entry["status"] = ReviewStatus.REJECTED.value
        elif action == ReviewAction.REQUEST_MORE_INFO:
            entry["status"] = ReviewStatus.ADDITIONAL_INFO_REQUIRED.value
        elif action == ReviewAction.ESCALATE_TO_ADMIN:
            entry["status"] = ReviewStatus.ESCALATED.value
            entry["escalation_level"] += 1
        
        # Move to history if completed
        if entry["status"] in [ReviewStatus.APPROVED.value, ReviewStatus.REJECTED.value]:
            self.review_history[incident_id] = entry.copy()
            # Keep in queue for a while for reference, but mark as completed
        
        return entry
    
    def get_review_status(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Get the review status for an incident"""
        return self.review_queue.get(incident_id)
    
    def is_approved_for_evaluation(self, incident_id: str) -> bool:
        """Check if an incident is approved for automated evaluation"""
        entry = self.review_queue.get(incident_id)
        if not entry:
            return True  # Not in review queue, can proceed
        
        return entry["status"] == ReviewStatus.APPROVED.value
    
    def get_review_summary(self) -> Dict[str, Any]:
        """Get summary statistics of the review queue"""
        queue = list(self.review_queue.values())
        
        summary = {
            "total_pending": len([e for e in queue if e["status"] == ReviewStatus.PENDING.value]),
            "total_in_review": len([e for e in queue if e["status"] == ReviewStatus.IN_REVIEW.value]),
            "total_approved": len([e for e in queue if e["status"] == ReviewStatus.APPROVED.value]),
            "total_rejected": len([e for e in queue if e["status"] == ReviewStatus.REJECTED.value]),
            "high_priority": len([e for e in queue if e["priority"] == "high"]),
            "medium_priority": len([e for e in queue if e["priority"] == "medium"]),
            "low_priority": len([e for e in queue if e["priority"] == "low"]),
            "anonymous_reports": len([e for e in queue if ReviewReason.ANONYMOUS_REPORT.value in e["reasons"]]),
            "suspicious_files": len([e for e in queue if ReviewReason.SUSPICIOUS_FILE.value in e["reasons"]]),
        }
        
        return summary
    
    def generate_review_explanation(self, reasons: List[ReviewReason], 
                                  file_analyses: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generate detailed explanation for why human review is required
        
        Args:
            reasons: List of review reasons
            file_analyses: File analyses if any
            
        Returns:
            Structured explanation
        """
        explanation = {
            "title": "Human Review Required",
            "summary": "This incident requires human verification before automated processing can continue.",
            "reasons": [],
            "next_steps": "A trained reviewer will examine this report and make a determination on how to proceed.",
            "estimated_review_time": "1-4 hours during business hours"
        }
        
        reason_explanations = {
            ReviewReason.ANONYMOUS_REPORT: {
                "title": "Anonymous Submission",
                "description": "This report was submitted anonymously. Our policy requires human verification of anonymous reports to ensure accuracy and prevent misuse while protecting reporter privacy.",
                "icon": "🔒"
            },
            ReviewReason.SUSPICIOUS_FILE: {
                "title": "File Authenticity Concerns",
                "description": "One or more uploaded files show patterns that may indicate AI generation or digital manipulation. Human verification is needed to ensure evidence authenticity.",
                "icon": "🔍"
            },
            ReviewReason.UNVERIFIABLE_FILE: {
                "title": "Unverifiable File Content",
                "description": "Uploaded files cannot be automatically verified for authenticity due to missing metadata or technical issues. Manual review is required.",
                "icon": "❓"
            },
            ReviewReason.HIGH_RISK_CONTENT: {
                "title": "High-Risk Content Detected",
                "description": "The report contains content that requires careful human assessment to ensure appropriate response and safety measures.",
                "icon": "⚠️"
            }
        }
        
        for reason in reasons:
            if reason in reason_explanations:
                explanation["reasons"].append(reason_explanations[reason])
        
        # Add file-specific details
        if file_analyses:
            suspicious_files = [f for f in file_analyses if f.get("requires_human_review", False)]
            if suspicious_files:
                explanation["file_details"] = []
                for file_analysis in suspicious_files:
                    explanation["file_details"].append({
                        "filename": file_analysis.get("filename", "unknown"),
                        "status": file_analysis.get("authenticity_status", "unknown"),
                        "concerns": file_analysis.get("risk_factors", []),
                        "summary": file_analysis.get("summary", "")
                    })
        
        return explanation

# Global service instance
human_review_service = HumanReviewService()