"""
Planner Agent - Creates comprehensive action plans for incident response
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent
from datetime import datetime, timedelta


class PlannerAgent(BaseAgent):
    """
    Agent responsible for creating comprehensive action plans based on
    structured incident reports, including immediate, short-term, and long-term actions
    """
    
    def __init__(self):
        super().__init__(
            name="Planner Agent",
            description="Creates comprehensive action plans for incident response"
        )
        self.action_templates = self._load_action_templates()
        self.stakeholder_mapping = self._load_stakeholder_mapping()
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create comprehensive action plan for incident response
        
        Args:
            input_data: {
                "structured_report": dict - From Prompt Agent
                "extracted_entities": dict - Key entities
                "prompt_for_analysis": str - Analysis prompt
                "metadata": dict - Additional metadata
            }
        
        Returns:
            {
                "action_plan": dict - Comprehensive action plan
                "priority_level": str - Overall priority
                "estimated_duration": str - Expected completion time
                "resource_requirements": dict - Required resources
                "status": str
            }
        """
        try:
            structured_report = input_data.get("structured_report", {})
            extracted_entities = input_data.get("extracted_entities", {})
            
            # Determine priority level
            priority_level = self._determine_priority(structured_report)
            
            # Create immediate actions
            immediate_actions = self._create_immediate_actions(structured_report, priority_level)
            
            # Create short-term actions
            short_term_actions = self._create_short_term_actions(structured_report)
            
            # Create long-term actions
            long_term_actions = self._create_long_term_actions(structured_report)
            
            # Identify stakeholders
            stakeholders = self._identify_stakeholders(structured_report, extracted_entities)
            
            # Determine resource needs
            resources_needed = self._determine_resources(structured_report, priority_level)
            
            # Create communication plan
            communication_plan = self._create_communication_plan(stakeholders, priority_level)
            
            # Estimate duration
            estimated_duration = self._estimate_duration(immediate_actions, short_term_actions, long_term_actions)
            
            action_plan = {
                "incident_id": structured_report.get("metadata", {}).get("incident_id", ""),
                "priority_level": priority_level,
                "immediate_actions": immediate_actions,
                "short_term_actions": short_term_actions,
                "long_term_actions": long_term_actions,
                "stakeholders": stakeholders,
                "resources_needed": resources_needed,
                "communication_plan": communication_plan,
                "success_criteria": self._define_success_criteria(structured_report),
                "contingency_plans": self._create_contingency_plans(structured_report)
            }
            
            output = self.create_success_response({
                "action_plan": action_plan,
                "priority_level": priority_level,
                "estimated_duration": estimated_duration,
                "resource_requirements": self._summarize_resource_requirements(resources_needed),
                "planning_notes": self._generate_planning_notes(structured_report, priority_level)
            })
            
            self.log_execution(input_data, output, "success")
            return output
            
        except Exception as e:
            return self.handle_error(e, "Action planning")
    
    def _load_action_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """Load action templates for different incident types"""
        return {
            "assault": {
                "immediate": [
                    "Ensure victim safety and provide immediate medical attention if needed",
                    "Secure the incident scene and preserve evidence",
                    "Contact campus security and local law enforcement",
                    "Notify Title IX Coordinator",
                    "Document all initial observations and statements"
                ],
                "short_term": [
                    "Conduct formal investigation following due process",
                    "Provide counseling and support services to affected parties",
                    "Review security measures in the incident area",
                    "Coordinate with law enforcement investigation"
                ],
                "long_term": [
                    "Implement policy changes if needed",
                    "Provide ongoing support services",
                    "Monitor for retaliation",
                    "Review and update safety protocols"
                ]
            },
            "harassment": {
                "immediate": [
                    "Ensure complainant safety",
                    "Document the complaint thoroughly",
                    "Notify appropriate administrators",
                    "Provide interim protective measures if needed"
                ],
                "short_term": [
                    "Initiate formal investigation process",
                    "Interview all relevant parties",
                    "Provide support resources to complainant",
                    "Implement interim measures as appropriate"
                ],
                "long_term": [
                    "Complete investigation and determine outcomes",
                    "Provide ongoing monitoring and support",
                    "Review policies and training programs",
                    "Follow up on effectiveness of interventions"
                ]
            },
            "theft": {
                "immediate": [
                    "Report to campus security immediately",
                    "Preserve evidence and secure the scene",
                    "Document all missing items and their value",
                    "Review security footage if available"
                ],
                "short_term": [
                    "File police report if value exceeds threshold",
                    "Conduct investigation with security team",
                    "Notify insurance if applicable",
                    "Increase security presence in affected area"
                ],
                "long_term": [
                    "Review and improve security measures",
                    "Provide crime prevention education",
                    "Monitor for patterns or repeat incidents",
                    "Update security protocols as needed"
                ]
            },
            "medical": {
                "immediate": [
                    "Call emergency services if serious injury",
                    "Provide first aid within training limits",
                    "Ensure scene safety for all present",
                    "Contact emergency contacts for injured party"
                ],
                "short_term": [
                    "Complete incident report for insurance/liability",
                    "Follow up on injured party's condition",
                    "Review safety protocols for the activity/area",
                    "Coordinate with health services"
                ],
                "long_term": [
                    "Analyze incident for prevention opportunities",
                    "Update safety training if needed",
                    "Review equipment and facility safety",
                    "Implement preventive measures"
                ]
            },
            "general": {
                "immediate": [
                    "Assess immediate safety concerns",
                    "Document the incident thoroughly",
                    "Notify appropriate supervisors",
                    "Provide initial support to affected parties"
                ],
                "short_term": [
                    "Investigate the incident as appropriate",
                    "Determine if policies were violated",
                    "Provide necessary support services",
                    "Take corrective action if needed"
                ],
                "long_term": [
                    "Monitor for ongoing issues",
                    "Review policies and procedures",
                    "Provide follow-up support",
                    "Document lessons learned"
                ]
            }
        }
    
    def _load_stakeholder_mapping(self) -> Dict[str, List[Dict[str, str]]]:
        """Load stakeholder mapping for different incident types"""
        return {
            "assault": [
                {"role": "Campus Security", "notification_priority": "immediate", "involvement": "primary"},
                {"role": "Title IX Coordinator", "notification_priority": "immediate", "involvement": "primary"},
                {"role": "Student Affairs Dean", "notification_priority": "within_2_hours", "involvement": "secondary"},
                {"role": "Counseling Services", "notification_priority": "within_4_hours", "involvement": "support"},
                {"role": "Legal Counsel", "notification_priority": "within_24_hours", "involvement": "advisory"}
            ],
            "harassment": [
                {"role": "Title IX Coordinator", "notification_priority": "immediate", "involvement": "primary"},
                {"role": "Student Affairs Dean", "notification_priority": "within_2_hours", "involvement": "primary"},
                {"role": "Counseling Services", "notification_priority": "within_4_hours", "involvement": "support"},
                {"role": "Campus Security", "notification_priority": "within_4_hours", "involvement": "secondary"}
            ],
            "theft": [
                {"role": "Campus Security", "notification_priority": "immediate", "involvement": "primary"},
                {"role": "Facilities Management", "notification_priority": "within_4_hours", "involvement": "secondary"},
                {"role": "Risk Management", "notification_priority": "within_24_hours", "involvement": "advisory"}
            ],
            "medical": [
                {"role": "Health Services", "notification_priority": "immediate", "involvement": "primary"},
                {"role": "Risk Management", "notification_priority": "within_2_hours", "involvement": "secondary"},
                {"role": "Facilities Management", "notification_priority": "within_4_hours", "involvement": "secondary"}
            ],
            "general": [
                {"role": "Student Affairs Dean", "notification_priority": "within_4_hours", "involvement": "primary"},
                {"role": "Campus Security", "notification_priority": "within_4_hours", "involvement": "secondary"}
            ]
        }
    
    def _determine_priority(self, structured_report: Dict[str, Any]) -> str:
        """Determine priority level based on incident characteristics"""
        severity = structured_report.get("severity", "low")
        incident_type = structured_report.get("incident_type", "general")
        
        # Critical priority incidents
        if severity == "critical" or incident_type in ["assault", "medical"]:
            return "critical"
        
        # High priority incidents
        if severity == "high" or incident_type in ["harassment", "safety"]:
            return "high"
        
        # Medium priority incidents
        if severity == "medium" or incident_type in ["theft", "vandalism"]:
            return "medium"
        
        # Default to low priority
        return "low"
    
    def _create_immediate_actions(self, structured_report: Dict[str, Any], priority: str) -> List[Dict[str, Any]]:
        """Create immediate actions based on incident type and priority"""
        incident_type = structured_report.get("incident_type", "general")
        template_actions = self.action_templates.get(incident_type, self.action_templates["general"])["immediate"]
        
        actions = []
        for i, action_text in enumerate(template_actions):
            deadline = self._calculate_deadline(priority, "immediate", i)
            actions.append({
                "action": action_text,
                "responsible": self._assign_responsibility(action_text, incident_type),
                "deadline": deadline,
                "priority": priority,
                "status": "pending"
            })
        
        return actions
    
    def _create_short_term_actions(self, structured_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create short-term actions"""
        incident_type = structured_report.get("incident_type", "general")
        template_actions = self.action_templates.get(incident_type, self.action_templates["general"])["short_term"]
        
        actions = []
        for i, action_text in enumerate(template_actions):
            deadline = self._calculate_deadline("medium", "short_term", i)
            actions.append({
                "action": action_text,
                "responsible": self._assign_responsibility(action_text, incident_type),
                "deadline": deadline,
                "priority": "medium",
                "status": "pending"
            })
        
        return actions
    
    def _create_long_term_actions(self, structured_report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create long-term actions"""
        incident_type = structured_report.get("incident_type", "general")
        template_actions = self.action_templates.get(incident_type, self.action_templates["general"])["long_term"]
        
        actions = []
        for i, action_text in enumerate(template_actions):
            deadline = self._calculate_deadline("low", "long_term", i)
            actions.append({
                "action": action_text,
                "responsible": self._assign_responsibility(action_text, incident_type),
                "deadline": deadline,
                "priority": "low",
                "status": "pending"
            })
        
        return actions
    
    def _identify_stakeholders(self, structured_report: Dict[str, Any], entities: Dict[str, Any]) -> List[Dict[str, str]]:
        """Identify relevant stakeholders"""
        incident_type = structured_report.get("incident_type", "general")
        stakeholder_template = self.stakeholder_mapping.get(incident_type, self.stakeholder_mapping["general"])
        
        return stakeholder_template.copy()
    
    def _determine_resources(self, structured_report: Dict[str, Any], priority: str) -> List[Dict[str, str]]:
        """Determine required resources"""
        incident_type = structured_report.get("incident_type", "general")
        resources = []
        
        # Common resources for all incidents
        resources.extend([
            {"resource": "Incident documentation system", "type": "technology", "availability": "immediate"},
            {"resource": "Administrative support", "type": "personnel", "availability": "immediate"}
        ])
        
        # Type-specific resources
        if incident_type in ["assault", "harassment"]:
            resources.extend([
                {"resource": "Trained investigator", "type": "personnel", "availability": "within_24_hours"},
                {"resource": "Counseling services", "type": "support", "availability": "immediate"},
                {"resource": "Legal consultation", "type": "advisory", "availability": "within_48_hours"}
            ])
        
        if incident_type == "theft":
            resources.extend([
                {"resource": "Security personnel", "type": "personnel", "availability": "immediate"},
                {"resource": "Security footage review", "type": "investigation", "availability": "within_4_hours"}
            ])
        
        if incident_type == "medical":
            resources.extend([
                {"resource": "Medical personnel", "type": "personnel", "availability": "immediate"},
                {"resource": "Emergency equipment", "type": "equipment", "availability": "immediate"}
            ])
        
        # Priority-based additional resources
        if priority in ["critical", "high"]:
            resources.append(
                {"resource": "Senior administrator", "type": "personnel", "availability": "immediate"}
            )
        
        return resources
    
    def _create_communication_plan(self, stakeholders: List[Dict[str, str]], priority: str) -> Dict[str, Any]:
        """Create communication plan"""
        return {
            "internal_notifications": [
                {
                    "recipient": stakeholder["role"],
                    "method": "phone" if priority in ["critical", "high"] else "email",
                    "timeline": stakeholder["notification_priority"],
                    "message_type": "incident_alert"
                }
                for stakeholder in stakeholders
            ],
            "external_notifications": self._determine_external_notifications(priority),
            "updates_schedule": self._create_update_schedule(priority),
            "communication_lead": "Student Affairs Dean"
        }
    
    def _calculate_deadline(self, priority: str, phase: str, index: int) -> str:
        """Calculate deadline for actions"""
        base_time = datetime.now()
        
        if phase == "immediate":
            if priority == "critical":
                hours = 1 + (index * 0.5)
            elif priority == "high":
                hours = 2 + (index * 1)
            else:
                hours = 4 + (index * 2)
            return (base_time + timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M")
        
        elif phase == "short_term":
            days = 1 + (index * 2)
            return (base_time + timedelta(days=days)).strftime("%Y-%m-%d")
        
        else:  # long_term
            weeks = 1 + (index * 2)
            return (base_time + timedelta(weeks=weeks)).strftime("%Y-%m-%d")
    
    def _assign_responsibility(self, action_text: str, incident_type: str) -> str:
        """Assign responsibility based on action content"""
        action_lower = action_text.lower()
        
        if "security" in action_lower or "law enforcement" in action_lower:
            return "Campus Security"
        elif "medical" in action_lower or "health" in action_lower:
            return "Health Services"
        elif "counseling" in action_lower or "support" in action_lower:
            return "Counseling Services"
        elif "investigate" in action_lower:
            return "Title IX Coordinator" if incident_type in ["assault", "harassment"] else "Student Affairs"
        elif "notify" in action_lower or "contact" in action_lower:
            return "Student Affairs Dean"
        else:
            return "Student Affairs"
    
    def _define_success_criteria(self, structured_report: Dict[str, Any]) -> List[str]:
        """Define success criteria for the response"""
        incident_type = structured_report.get("incident_type", "general")
        
        criteria = [
            "All immediate safety concerns addressed",
            "Incident properly documented and reported",
            "Appropriate stakeholders notified within required timeframes",
            "Support services provided to affected parties"
        ]
        
        if incident_type in ["assault", "harassment"]:
            criteria.extend([
                "Investigation completed following due process",
                "Appropriate disciplinary action taken if violations found",
                "Ongoing monitoring for retaliation implemented"
            ])
        
        return criteria
    
    def _create_contingency_plans(self, structured_report: Dict[str, Any]) -> List[Dict[str, str]]:
        """Create contingency plans for potential complications"""
        return [
            {
                "scenario": "Media attention",
                "response": "Activate crisis communication protocol, designate single spokesperson",
                "responsible": "Communications Office"
            },
            {
                "scenario": "Legal action threatened",
                "response": "Immediately involve legal counsel, preserve all documentation",
                "responsible": "Legal Counsel"
            },
            {
                "scenario": "Additional victims come forward",
                "response": "Expand investigation scope, provide additional support resources",
                "responsible": "Investigation Lead"
            }
        ]
    
    def _determine_external_notifications(self, priority: str) -> List[Dict[str, str]]:
        """Determine if external notifications are needed"""
        if priority == "critical":
            return [
                {"entity": "Local Law Enforcement", "condition": "if criminal activity suspected"},
                {"entity": "Emergency Services", "condition": "if medical emergency"},
                {"entity": "Legal Counsel", "condition": "immediate consultation"}
            ]
        return []
    
    def _create_update_schedule(self, priority: str) -> Dict[str, str]:
        """Create schedule for progress updates"""
        if priority == "critical":
            return {"frequency": "every 2 hours", "method": "phone/email", "recipients": "all stakeholders"}
        elif priority == "high":
            return {"frequency": "daily", "method": "email", "recipients": "primary stakeholders"}
        else:
            return {"frequency": "weekly", "method": "email", "recipients": "relevant stakeholders"}
    
    def _estimate_duration(self, immediate: List, short_term: List, long_term: List) -> str:
        """Estimate total duration for plan completion"""
        immediate_hours = len(immediate) * 2
        short_term_days = len(short_term) * 3
        long_term_weeks = len(long_term) * 2
        
        return f"Immediate: {immediate_hours} hours, Short-term: {short_term_days} days, Long-term: {long_term_weeks} weeks"
    
    def _summarize_resource_requirements(self, resources: List[Dict[str, str]]) -> Dict[str, int]:
        """Summarize resource requirements by type"""
        summary = {}
        for resource in resources:
            resource_type = resource.get("type", "other")
            summary[resource_type] = summary.get(resource_type, 0) + 1
        return summary
    
    def _generate_planning_notes(self, structured_report: Dict[str, Any], priority: str) -> List[str]:
        """Generate planning notes and considerations"""
        notes = []
        
        if priority == "critical":
            notes.append("High-priority incident requiring immediate senior leadership involvement")
        
        if structured_report.get("datetime") == "Not specified":
            notes.append("Timeline unclear - may affect investigation and evidence preservation")
        
        if len(structured_report.get("involved_parties", [])) == 0:
            notes.append("Limited information about involved parties - may require additional investigation")
        
        notes.append(f"Plan created for {structured_report.get('incident_type', 'general')} incident")
        notes.append("All deadlines are estimates and may need adjustment based on circumstances")
        
        return notes