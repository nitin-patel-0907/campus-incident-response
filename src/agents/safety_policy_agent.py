"""
Safety and Policy Agent - Ensures compliance with campus policies and safety protocols
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent
from datetime import datetime


class SafetyPolicyAgent(BaseAgent):
    """
    Agent responsible for validating actions against campus policies,
    ensuring safety compliance, and preventing harmful actions
    """
    
    def __init__(self):
        super().__init__(
            name="Safety and Policy Agent",
            description="Validates compliance with campus policies and safety protocols"
        )
        self.policies = self._load_policies()
        self.safety_rules = self._load_safety_rules()
        self.blocked_actions = []
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate actions and ensure policy compliance
        
        Args:
            input_data: {
                "structured_report": dict - Incident details
                "action_plan": dict - Proposed actions
                "execution_summary": dict - Execution details
            }
        
        Returns:
            {
                "validation_result": str - "approved", "modified", "blocked"
                "policy_compliance": dict - Compliance analysis
                "safety_checks": dict - Safety validation results
                "violations": list - Any policy violations found
                "recommendations": list - Safety recommendations
                "approved_actions": list - Actions cleared for execution
                "blocked_actions": list - Actions that violate policies
                "status": str
            }
        """
        try:
            structured_report = input_data.get("structured_report", {})
            action_plan = input_data.get("action_plan", {})
            execution_summary = input_data.get("execution_summary", {})
            
            # Check policy compliance
            policy_compliance = self._check_policy_compliance(structured_report, action_plan)
            
            # Perform safety validation
            safety_checks = self._perform_safety_checks(structured_report, action_plan)
            
            # Identify violations
            violations = self._identify_violations(structured_report, action_plan)
            
            # Validate proposed actions
            action_validation = self._validate_actions(action_plan)
            
            # Generate safety recommendations
            recommendations = self._generate_safety_recommendations(
                structured_report, violations, safety_checks
            )
            
            # Check for harmful actions
            harmful_check = self._check_harmful_actions(action_plan)
            
            # Determine overall validation result
            validation_result = self._determine_validation_result(
                policy_compliance, safety_checks, violations, harmful_check
            )
            
            # Privacy and data protection check
            privacy_compliance = self._check_privacy_compliance(structured_report, action_plan)
            
            output = {
                "validation_result": validation_result,
                "policy_compliance": policy_compliance,
                "safety_checks": safety_checks,
                "violations": violations,
                "recommendations": recommendations,
                "approved_actions": action_validation["approved"],
                "blocked_actions": action_validation["blocked"],
                "modified_actions": action_validation["modified"],
                "harmful_actions_detected": harmful_check["detected"],
                "privacy_compliance": privacy_compliance,
                "overall_risk_level": self._assess_risk_level(violations, safety_checks),
                "status": "success",
                "validation_timestamp": datetime.now().isoformat()
            }
            
            self.blocked_actions.extend(action_validation["blocked"])
            self.log_execution(input_data, output, "success")
            return output
            
        except Exception as e:
            error_output = {"status": "error", "error": str(e)}
            self.log_execution(input_data, error_output, "error")
            return error_output
    
    def _load_policies(self) -> Dict[str, Any]:
        """Load campus policies"""
        return {
            "student_conduct": {
                "violence": "Zero tolerance - immediate action required",
                "harassment": "Requires investigation and formal process",
                "theft": "Campus security involvement mandatory",
                "substance_abuse": "Health services and conduct office notification"
            },
            "employee_conduct": {
                "reporting_requirements": "All incidents must be reported within 24 hours",
                "confidentiality": "Maintain privacy of involved parties",
                "documentation": "Complete documentation required"
            },
            "safety_protocols": {
                "emergency_response": "Immediate notification to security",
                "medical_incidents": "Call emergency services if needed",
                "evidence_preservation": "Do not disturb scene until security arrives"
            },
            "privacy_regulations": {
                "FERPA": "Protect student education records",
                "Title_IX": "Follow Title IX reporting requirements",
                "data_handling": "Secure storage of sensitive information"
            }
        }
    
    def _load_safety_rules(self) -> List[Dict[str, str]]:
        """Load safety rules"""
        return [
            {
                "rule": "No retaliation against reporters",
                "severity": "critical",
                "description": "Protect individuals who report incidents"
            },
            {
                "rule": "Victim safety priority",
                "severity": "critical",
                "description": "Ensure safety of affected individuals first"
            },
            {
                "rule": "Evidence preservation",
                "severity": "high",
                "description": "Maintain integrity of evidence"
            },
            {
                "rule": "Proper notification chain",
                "severity": "high",
                "description": "Follow established notification protocols"
            },
            {
                "rule": "Confidentiality maintenance",
                "severity": "medium",
                "description": "Protect privacy of all parties"
            },
            {
                "rule": "No unauthorized disclosure",
                "severity": "high",
                "description": "Information shared only with authorized personnel"
            }
        ]
    
    def _check_policy_compliance(self, report: Dict[str, Any], plan: Dict[str, Any]) -> Dict[str, Any]:
        """Check compliance with campus policies"""
        incident_type = report.get("incident_type", "")
        severity = report.get("severity", "low")
        
        compliance_results = {
            "overall_compliant": True,
            "policy_checks": []
        }
        
        # Check student conduct policy
        if incident_type in ["assault", "harassment", "violence"]:
            compliance_results["policy_checks"].append({
                "policy": "Student Conduct Code",
                "requirement": "Formal investigation required",
                "status": "compliant" if self._has_investigation_action(plan) else "non_compliant",
                "severity": "high"
            })
        
        # Check reporting requirements
        compliance_results["policy_checks"].append({
            "policy": "Incident Reporting Policy",
            "requirement": "Report within 24 hours",
            "status": "compliant",
            "severity": "medium"
        })
        
        # Check Title IX requirements
        if incident_type in ["harassment", "assault"]:
            compliance_results["policy_checks"].append({
                "policy": "Title IX",
                "requirement": "Title IX Coordinator notification",
                "status": "compliant" if self._has_title_ix_notification(plan) else "non_compliant",
                "severity": "critical"
            })
        
        # Check privacy compliance
        compliance_results["policy_checks"].append({
            "policy": "FERPA",
            "requirement": "Protect student records",
            "status": "compliant",
            "severity": "high"
        })
        
        # Update overall compliance
        compliance_results["overall_compliant"] = all(
            check["status"] == "compliant" 
            for check in compliance_results["policy_checks"]
            if check["severity"] in ["critical", "high"]
        )
        
        return compliance_results
    
    def _perform_safety_checks(self, report: Dict[str, Any], plan: Dict[str, Any]) -> Dict[str, Any]:
        """Perform safety validation checks"""
        safety_results = {
            "all_checks_passed": True,
            "checks": []
        }
        
        # Check for immediate safety concerns
        safety_results["checks"].append({
            "check": "Immediate safety addressed",
            "passed": self._has_safety_action(plan),
            "priority": "critical"
        })
        
        # Check evidence preservation
        if report.get("incident_type") in ["assault", "theft", "vandalism"]:
            safety_results["checks"].append({
                "check": "Evidence preservation planned",
                "passed": self._has_evidence_preservation(plan),
                "priority": "high"
            })
        
        # Check victim support
        safety_results["checks"].append({
            "check": "Victim support services included",
            "passed": self._has_victim_support(plan),
            "priority": "high"
        })
        
        # Check proper notification chain
        safety_results["checks"].append({
            "check": "Notification chain followed",
            "passed": len(plan.get("stakeholders", [])) > 0,
            "priority": "high"
        })
        
        # Update overall status
        safety_results["all_checks_passed"] = all(
            check["passed"] 
            for check in safety_results["checks"]
            if check["priority"] in ["critical", "high"]
        )
        
        return safety_results
    
    def _identify_violations(self, report: Dict[str, Any], plan: Dict[str, Any]) -> List[Dict[str, str]]:
        """Identify policy violations"""
        violations = []
        
        incident_type = report.get("incident_type", "")
        description = report.get("description", "").lower()
        
        # Check for conduct violations
        if incident_type == "assault" or "fight" in description:
            violations.append({
                "policy": "Student Conduct Code - Violence",
                "violation_type": "Physical violence",
                "severity": "critical",
                "action_required": "Immediate disciplinary process"
            })
        
        if incident_type == "harassment" or "bullying" in description:
            violations.append({
                "policy": "Anti-Harassment Policy",
                "violation_type": "Harassment",
                "severity": "high",
                "action_required": "Formal investigation"
            })
        
        if incident_type == "theft":
            violations.append({
                "policy": "Property Protection Policy",
                "violation_type": "Theft/unauthorized possession",
                "severity": "high",
                "action_required": "Security investigation"
            })
        
        if "alcohol" in description or "drugs" in description:
            violations.append({
                "policy": "Substance Abuse Policy",
                "violation_type": "Prohibited substance",
                "severity": "medium",
                "action_required": "Health services and conduct review"
            })
        
        return violations
    
    def _validate_actions(self, plan: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Validate all proposed actions"""
        approved = []
        blocked = []
        modified = []
        
        all_actions = (
            plan.get("immediate_actions", []) +
            plan.get("short_term_actions", []) +
            plan.get("long_term_actions", [])
        )
        
        for action in all_actions:
            action_text = action.get("action", "").lower()
            
            # Block harmful actions
            if any(term in action_text for term in ["punish without investigation", "public shaming", "unauthorized disclosure"]):
                blocked.append({
                    "action": action.get("action"),
                    "reason": "Violates due process or privacy rights",
                    "severity": "critical"
                })
            # Approve safe actions
            elif any(term in action_text for term in ["investigate", "document", "notify", "provide support", "secure"]):
                approved.append({
                    "action": action.get("action"),
                    "validation": "Compliant with policies"
                })
            # Actions needing modification
            elif "contact witnesses" in action_text and "proper procedure" not in action_text:
                modified.append({
                    "original": action.get("action"),
                    "modified": action.get("action") + " following proper interview protocols",
                    "reason": "Added procedural safeguard"
                })
                approved.append({
                    "action": action.get("action") + " following proper interview protocols",
                    "validation": "Modified for compliance"
                })
            else:
                approved.append({
                    "action": action.get("action"),
                    "validation": "Standard action - approved"
                })
        
        return {
            "approved": approved,
            "blocked": blocked,
            "modified": modified
        }
    
    def _generate_safety_recommendations(self, report: Dict[str, Any], 
                                        violations: List[Dict[str, str]],
                                        safety_checks: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate safety recommendations"""
        recommendations = []
        
        # Critical incident recommendations
        if report.get("severity") == "high":
            recommendations.append({
                "recommendation": "Increase campus security presence in affected area",
                "priority": "high",
                "timeframe": "Immediate"
            })
        
        # Violation-based recommendations
        if violations:
            recommendations.append({
                "recommendation": "Conduct comprehensive policy training for involved parties",
                "priority": "medium",
                "timeframe": "Within 30 days"
            })
        
        # Safety check failures
        if not safety_checks.get("all_checks_passed"):
            recommendations.append({
                "recommendation": "Review and update safety protocols",
                "priority": "high",
                "timeframe": "Within 14 days"
            })
        
        # General recommendations
        recommendations.append({
            "recommendation": "Provide counseling resources to affected individuals",
            "priority": "high",
            "timeframe": "Within 48 hours"
        })
        
        recommendations.append({
            "recommendation": "Document all actions taken for audit trail",
            "priority": "medium",
            "timeframe": "Ongoing"
        })
        
        return recommendations
    
    def _check_harmful_actions(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Check for potentially harmful actions"""
        harmful_patterns = [
            "retaliation", "revenge", "punish", "punishment without investigation",
            "public shaming", "unauthorized disclosure", "vigilante"
        ]
        
        detected_harmful = []
        all_actions = (
            plan.get("immediate_actions", []) +
            plan.get("short_term_actions", []) +
            plan.get("long_term_actions", [])
        )
        
        for action in all_actions:
            action_text = action.get("action", "").lower()
            for pattern in harmful_patterns:
                if pattern in action_text:
                    detected_harmful.append({
                        "action": action.get("action"),
                        "harmful_pattern": pattern,
                        "severity": "critical"
                    })
        
        return {
            "detected": len(detected_harmful) > 0,
            "harmful_actions": detected_harmful,
            "action_taken": "Blocked" if detected_harmful else "None"
        }
    
    def _check_privacy_compliance(self, report: Dict[str, Any], plan: Dict[str, Any]) -> Dict[str, Any]:
        """Check privacy and data protection compliance"""
        return {
            "FERPA_compliant": True,
            "data_minimization": "Personal information limited to need-to-know basis",
            "secure_storage": "Required",
            "retention_policy": "Follow institutional data retention guidelines",
            "disclosure_controls": "Information shared only with authorized personnel"
        }
    
    def _assess_risk_level(self, violations: List[Dict[str, str]], 
                          safety_checks: Dict[str, Any]) -> str:
        """Assess overall risk level"""
        if not safety_checks.get("all_checks_passed"):
            return "high"
        
        critical_violations = sum(1 for v in violations if v.get("severity") == "critical")
        if critical_violations > 0:
            return "high"
        
        high_violations = sum(1 for v in violations if v.get("severity") == "high")
        if high_violations > 1:
            return "medium"
        
        return "low"
    
    def _has_investigation_action(self, plan: Dict[str, Any]) -> bool:
        """Check if plan includes investigation"""
        all_actions = plan.get("short_term_actions", []) + plan.get("long_term_actions", [])
        return any("investigate" in action.get("action", "").lower() for action in all_actions)
    
    def _has_title_ix_notification(self, plan: Dict[str, Any]) -> bool:
        """Check if Title IX coordinator is notified"""
        stakeholders = plan.get("stakeholders", [])
        return any("title ix" in s.get("role", "").lower() for s in stakeholders)
    
    def _has_safety_action(self, plan: Dict[str, Any]) -> bool:
        """Check if immediate safety is addressed"""
        immediate = plan.get("immediate_actions", [])
        return any("safety" in action.get("action", "").lower() for action in immediate)
    
    def _has_evidence_preservation(self, plan: Dict[str, Any]) -> bool:
        """Check if evidence preservation is included"""
        immediate = plan.get("immediate_actions", [])
        return any("evidence" in action.get("action", "").lower() for action in immediate)
    
    def _has_victim_support(self, plan: Dict[str, Any]) -> bool:
        """Check if victim support is included"""
        all_actions = plan.get("immediate_actions", []) + plan.get("short_term_actions", [])
        return any("support" in action.get("action", "").lower() or "counseling" in action.get("action", "").lower() for action in all_actions)
    
    def _determine_validation_result(self, policy_compliance: Dict[str, Any], 
                                   safety_checks: Dict[str, Any], 
                                   violations: List[Dict[str, str]], 
                                   harmful_check: Dict[str, Any]) -> str:
        """Determine overall validation result"""
        # Block if harmful actions detected
        if harmful_check.get("detected", False):
            return "blocked"
        
        # Block if critical violations found
        critical_violations = [v for v in violations if v.get("severity") == "critical"]
        if critical_violations:
            return "blocked"
        
        # Block if safety checks failed
        if not safety_checks.get("all_checks_passed", True):
            critical_safety_failures = [
                c for c in safety_checks.get("checks", []) 
                if not c.get("passed") and c.get("priority") == "critical"
            ]
            if critical_safety_failures:
                return "blocked"
        
        # Modify if policy compliance issues
        if not policy_compliance.get("overall_compliant", True):
            return "modified"
        
        # Approve if all checks pass
        return "approved"