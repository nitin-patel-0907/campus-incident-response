"""
Planner Node - Real-time action plan generation for incident response
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from langchain_core.messages import BaseMessage, AIMessage
from pydantic import BaseModel, Field
from .intake_node import IncidentData, IntakeNodeState
from ..llm.multi_provider_client import multi_llm_client


class ActionItem(BaseModel):
    """Individual action item in the response plan"""
    action_id: str = Field(description="Unique action identifier")
    description: str = Field(description="Action description")
    responsible_party: str = Field(description="Who is responsible")
    priority: str = Field(description="Action priority level")
    estimated_duration: str = Field(description="Estimated completion time")
    dependencies: List[str] = Field(default_factory=list, description="Dependent actions")
    resources_needed: List[str] = Field(default_factory=list, description="Required resources")
    status: str = Field(default="pending", description="Action status")


class ResponsePlan(BaseModel):
    """Complete incident response plan"""
    plan_id: str = Field(description="Unique plan identifier")
    incident_id: str = Field(description="Associated incident ID")
    plan_type: str = Field(description="Type of response plan")
    priority_level: str = Field(description="Overall plan priority")
    immediate_actions: List[ActionItem] = Field(description="Actions to take immediately")
    short_term_actions: List[ActionItem] = Field(description="Actions within 24 hours")
    long_term_actions: List[ActionItem] = Field(description="Follow-up actions")
    stakeholders: List[Dict[str, Any]] = Field(description="Involved stakeholders")
    resources_required: List[Dict[str, Any]] = Field(description="Required resources")
    timeline: Dict[str, str] = Field(description="Expected timeline")
    success_criteria: List[str] = Field(description="Success metrics")
    risk_factors: List[str] = Field(description="Identified risks")
    created_at: str = Field(description="Plan creation timestamp")
    estimated_completion: str = Field(description="Estimated completion time")


class PlannerNodeState(IntakeNodeState):
    """Extended state for planner node"""
    response_plan: Optional[ResponsePlan] = None
    planning_status: str = Field(default="pending")
    plan_confidence: float = Field(default=0.0)


class PlannerNode:
    """
    LangGraph node for generating real-time incident response plans
    """
    
    def __init__(self):
        self.name = "planner_node"
        self.action_templates = self._load_action_templates()
        self.stakeholder_mapping = self._load_stakeholder_mapping()
        self.resource_catalog = self._load_resource_catalog()
        
    def __call__(self, state: PlannerNodeState) -> PlannerNodeState:
        """
        Generate comprehensive response plan for the incident
        
        Args:
            state: Current processing state with incident data
            
        Returns:
            Updated state with response plan
        """
        try:
            if not state.incident_data:
                state.errors.append("No incident data available for planning")
                state.planning_status = "error"
                return state
            
            # Generate response plan
            response_plan = self._generate_response_plan(state.incident_data)
            
            # Validate and optimize the plan
            validation_result = self._validate_plan(response_plan, state.incident_data)
            
            # Update state
            state.response_plan = response_plan
            state.planning_status = "completed"
            state.plan_confidence = validation_result["confidence"]
            state.warnings.extend(validation_result.get("warnings", []))
            
            # Add planning message
            planning_msg = AIMessage(
                content=f"Response plan generated for {response_plan.incident_id}. "
                       f"Priority: {response_plan.priority_level}, "
                       f"Actions: {len(response_plan.immediate_actions)} immediate, "
                       f"{len(response_plan.short_term_actions)} short-term, "
                       f"Confidence: {state.plan_confidence:.2f}"
            )
            state.messages.append(planning_msg)
            
            # Always proceed to safety for validation
            state.next_node = "safety"
                
            return state
            
        except Exception as e:
            print(f"Planner node error: {e}")
            # Create a minimal response plan even on error
            try:
                minimal_plan = self._create_minimal_plan(state.incident_data)
                state.response_plan = minimal_plan
                state.planning_status = "completed"
                state.plan_confidence = 50.0
                state.warnings.append("Minimal plan generated due to processing error")
                state.next_node = "safety"
            except:
                state.errors.append(f"Planning error: {str(e)}")
                state.planning_status = "error"
            return state
    
    def _generate_response_plan(self, incident_data: IncidentData) -> ResponsePlan:
        """Generate comprehensive response plan using OpenAI"""
        
        plan_id = f"PLAN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Try to get AI-generated response plan
        try:
            # Prepare incident data for OpenAI
            incident_dict = {
                'incident_type': incident_data.incident_type,
                'severity': incident_data.severity,
                'description': incident_data.description,
                'location': incident_data.location,
                'priority': incident_data.priority
            }
            
            # Get AI-generated plan
            ai_plan = multi_llm_client.generate_response_plan(incident_dict)
            
            if ai_plan and 'immediate_actions' in ai_plan:
                # Convert AI response to our format
                immediate_actions = []
                for i, action in enumerate(ai_plan.get('immediate_actions', []), 1):
                    immediate_actions.append(ActionItem(
                        action_id=f"IMM-{i:03d}",
                        description=action.get('description', 'Action description'),
                        responsible_party=action.get('responsible_party', 'Campus Security'),
                        priority=action.get('priority', 'medium'),
                        estimated_duration=action.get('estimated_duration', '30 minutes'),
                        dependencies=[],
                        resources_needed=[],
                        status="pending"
                    ))
                
                # Convert stakeholders
                stakeholders = []
                for stakeholder in ai_plan.get('stakeholders', []):
                    stakeholders.append({
                        "role": stakeholder.get('role', 'Security Officer'),
                        "department": stakeholder.get('department', 'Security'),
                        "notification_priority": stakeholder.get('notification_priority', 'standard'),
                        "contact_method": stakeholder.get('contact_method', 'phone'),
                        "responsibilities": ["Response coordination"]
                    })
                
                return ResponsePlan(
                    plan_id=plan_id,
                    incident_id=incident_data.incident_id,
                    plan_type=ai_plan.get('plan_type', 'standard_response'),
                    priority_level=ai_plan.get('priority_level', 'standard'),
                    immediate_actions=immediate_actions,
                    short_term_actions=[],  # Can be expanded
                    long_term_actions=[],   # Can be expanded
                    stakeholders=stakeholders,
                    resources_required=[],
                    timeline=self._create_timeline(immediate_actions, [], []),
                    success_criteria=ai_plan.get('success_criteria', ['Situation resolved']),
                    risk_factors=ai_plan.get('risk_factors', ['Time sensitivity']),
                    created_at=datetime.now().isoformat(),
                    estimated_completion=(datetime.now() + timedelta(hours=2)).isoformat()
                )
        except Exception as e:
            print(f"OpenAI plan generation failed, using fallback: {e}")
        
        # Fallback to original method if OpenAI fails
        # Determine plan type and priority
        plan_type = self._determine_plan_type(incident_data)
        priority_level = self._determine_priority_level(incident_data)
        
        # Generate action items
        immediate_actions = self._generate_immediate_actions(incident_data)
        short_term_actions = self._generate_short_term_actions(incident_data)
        long_term_actions = self._generate_long_term_actions(incident_data)
        
        # Identify stakeholders and resources
        stakeholders = self._identify_stakeholders(incident_data)
        resources_required = self._identify_required_resources(incident_data)
        
        # Create timeline
        timeline = self._create_timeline(immediate_actions, short_term_actions, long_term_actions)
        
        # Define success criteria and risks
        success_criteria = self._define_success_criteria(incident_data)
        risk_factors = self._identify_risk_factors(incident_data)
        
        # Calculate estimated completion
        estimated_completion = self._calculate_completion_time(
            immediate_actions, short_term_actions, long_term_actions
        )
        
        return ResponsePlan(
            plan_id=plan_id,
            incident_id=incident_data.incident_id,
            plan_type=plan_type,
            priority_level=priority_level,
            immediate_actions=immediate_actions,
            short_term_actions=short_term_actions,
            long_term_actions=long_term_actions,
            stakeholders=stakeholders,
            resources_required=resources_required,
            timeline=timeline,
            success_criteria=success_criteria,
            risk_factors=risk_factors,
            created_at=datetime.now().isoformat(),
            estimated_completion=estimated_completion
        )
    
    def _determine_plan_type(self, incident_data: IncidentData) -> str:
        """Determine the type of response plan needed"""
        incident_type = incident_data.incident_type
        severity = incident_data.severity
        
        if incident_type in ["assault", "medical", "fire"]:
            return "emergency_response"
        elif incident_type in ["harassment", "discrimination"]:
            return "investigation_and_support"
        elif incident_type in ["theft", "vandalism"]:
            return "security_and_recovery"
        elif incident_type == "maintenance":
            return "facilities_response"
        else:
            return "standard_response"
    
    def _determine_priority_level(self, incident_data: IncidentData) -> str:
        """Determine overall plan priority level"""
        severity = incident_data.severity
        incident_type = incident_data.incident_type
        
        if severity == "critical" or incident_type in ["assault", "medical", "fire"]:
            return "critical"
        elif severity == "high" or incident_type in ["harassment", "theft"]:
            return "urgent"
        elif severity == "medium":
            return "standard"
        else:
            return "routine"
    
    def _generate_immediate_actions(self, incident_data: IncidentData) -> List[ActionItem]:
        """Generate immediate response actions (0-2 hours)"""
        actions = []
        incident_type = incident_data.incident_type
        severity = incident_data.severity
        
        # Get base actions for incident type
        base_actions = self.action_templates.get(incident_type, {}).get("immediate", [])
        
        action_counter = 1
        for action_template in base_actions:
            action = ActionItem(
                action_id=f"IMM-{action_counter:03d}",
                description=action_template["description"].format(
                    location=incident_data.location,
                    incident_type=incident_type
                ),
                responsible_party=action_template["responsible"],
                priority=action_template["priority"],
                estimated_duration=action_template["duration"],
                resources_needed=action_template.get("resources", [])
            )
            actions.append(action)
            action_counter += 1
        
        # Add severity-specific actions
        if severity in ["critical", "high"]:
            actions.append(ActionItem(
                action_id=f"IMM-{action_counter:03d}",
                description="Notify emergency contacts and senior administration",
                responsible_party="Campus Security",
                priority="high",
                estimated_duration="15 minutes",
                resources_needed=["Emergency contact list", "Communication system"]
            ))
            action_counter += 1
        
        # Add location-specific actions
        if "parking" in incident_data.location.lower():
            actions.append(ActionItem(
                action_id=f"IMM-{action_counter:03d}",
                description="Secure parking area and review security footage",
                responsible_party="Security Team",
                priority="medium",
                estimated_duration="30 minutes",
                resources_needed=["Security cameras", "Barrier tape"]
            ))
        
        return actions
    
    def _generate_short_term_actions(self, incident_data: IncidentData) -> List[ActionItem]:
        """Generate short-term actions (2-24 hours)"""
        actions = []
        incident_type = incident_data.incident_type
        
        base_actions = self.action_templates.get(incident_type, {}).get("short_term", [])
        
        action_counter = 1
        for action_template in base_actions:
            action = ActionItem(
                action_id=f"ST-{action_counter:03d}",
                description=action_template["description"],
                responsible_party=action_template["responsible"],
                priority=action_template["priority"],
                estimated_duration=action_template["duration"],
                resources_needed=action_template.get("resources", [])
            )
            actions.append(action)
            action_counter += 1
        
        # Add follow-up investigation
        actions.append(ActionItem(
            action_id=f"ST-{action_counter:03d}",
            description="Conduct detailed investigation and gather additional evidence",
            responsible_party="Investigation Team",
            priority="medium",
            estimated_duration="4 hours",
            resources_needed=["Investigation kit", "Interview rooms"]
        ))
        
        return actions
    
    def _generate_long_term_actions(self, incident_data: IncidentData) -> List[ActionItem]:
        """Generate long-term follow-up actions (1+ days)"""
        actions = []
        incident_type = incident_data.incident_type
        
        base_actions = self.action_templates.get(incident_type, {}).get("long_term", [])
        
        action_counter = 1
        for action_template in base_actions:
            action = ActionItem(
                action_id=f"LT-{action_counter:03d}",
                description=action_template["description"],
                responsible_party=action_template["responsible"],
                priority=action_template["priority"],
                estimated_duration=action_template["duration"],
                resources_needed=action_template.get("resources", [])
            )
            actions.append(action)
            action_counter += 1
        
        # Add standard follow-up actions
        actions.extend([
            ActionItem(
                action_id=f"LT-{action_counter:03d}",
                description="Review and update safety protocols based on incident",
                responsible_party="Safety Committee",
                priority="low",
                estimated_duration="1 week",
                resources_needed=["Policy documents", "Committee meeting"]
            ),
            ActionItem(
                action_id=f"LT-{action_counter + 1:03d}",
                description="Conduct follow-up with affected parties",
                responsible_party="Student Services",
                priority="medium",
                estimated_duration="2 weeks",
                resources_needed=["Contact information", "Support resources"]
            )
        ])
        
        return actions
    
    def _identify_stakeholders(self, incident_data: IncidentData) -> List[Dict[str, Any]]:
        """Identify relevant stakeholders for the incident"""
        stakeholders = []
        incident_type = incident_data.incident_type
        severity = incident_data.severity
        
        # Get base stakeholders
        base_stakeholders = self.stakeholder_mapping.get(incident_type, [])
        
        for stakeholder in base_stakeholders:
            stakeholders.append({
                "role": stakeholder["role"],
                "department": stakeholder["department"],
                "notification_priority": stakeholder["priority"],
                "contact_method": stakeholder["contact_method"],
                "responsibilities": stakeholder["responsibilities"]
            })
        
        # Add severity-based stakeholders
        if severity in ["critical", "high"]:
            stakeholders.extend([
                {
                    "role": "Dean of Students",
                    "department": "Student Affairs",
                    "notification_priority": "immediate",
                    "contact_method": "phone",
                    "responsibilities": ["Oversight", "Policy decisions"]
                },
                {
                    "role": "Legal Counsel",
                    "department": "Legal Affairs",
                    "notification_priority": "urgent",
                    "contact_method": "email",
                    "responsibilities": ["Legal guidance", "Compliance"]
                }
            ])
        
        return stakeholders
    
    def _identify_required_resources(self, incident_data: IncidentData) -> List[Dict[str, Any]]:
        """Identify resources needed for response"""
        resources = []
        incident_type = incident_data.incident_type
        
        # Get base resources
        base_resources = self.resource_catalog.get(incident_type, [])
        
        for resource in base_resources:
            resources.append({
                "resource_type": resource["type"],
                "description": resource["description"],
                "quantity": resource["quantity"],
                "availability": resource["availability"],
                "cost_estimate": resource.get("cost", "N/A")
            })
        
        # Add common resources
        resources.extend([
            {
                "resource_type": "Personnel",
                "description": "Security officers for scene management",
                "quantity": "2-3 officers",
                "availability": "24/7",
                "cost_estimate": "Standard hourly rate"
            },
            {
                "resource_type": "Communication",
                "description": "Emergency communication system",
                "quantity": "1 system",
                "availability": "Always available",
                "cost_estimate": "No additional cost"
            }
        ])
        
        return resources
    
    def _create_timeline(self, immediate: List[ActionItem], 
                        short_term: List[ActionItem], 
                        long_term: List[ActionItem]) -> Dict[str, str]:
        """Create response timeline"""
        now = datetime.now()
        
        return {
            "incident_reported": now.isoformat(),
            "immediate_response_start": now.isoformat(),
            "immediate_response_complete": (now + timedelta(hours=2)).isoformat(),
            "short_term_actions_start": (now + timedelta(hours=2)).isoformat(),
            "short_term_actions_complete": (now + timedelta(hours=24)).isoformat(),
            "long_term_actions_start": (now + timedelta(days=1)).isoformat(),
            "estimated_resolution": (now + timedelta(days=7)).isoformat()
        }
    
    def _define_success_criteria(self, incident_data: IncidentData) -> List[str]:
        """Define success criteria for the response"""
        criteria = [
            "Immediate safety concerns addressed",
            "All stakeholders properly notified",
            "Incident properly documented and reported"
        ]
        
        incident_type = incident_data.incident_type
        
        if incident_type == "medical":
            criteria.extend([
                "Medical attention provided to injured parties",
                "Emergency medical services contacted if needed"
            ])
        elif incident_type == "theft":
            criteria.extend([
                "Security footage reviewed",
                "Police report filed if appropriate",
                "Victim support provided"
            ])
        elif incident_type == "harassment":
            criteria.extend([
                "Formal investigation initiated",
                "Support services offered to affected parties",
                "Appropriate disciplinary action taken"
            ])
        
        return criteria
    
    def _identify_risk_factors(self, incident_data: IncidentData) -> List[str]:
        """Identify potential risk factors"""
        risks = []
        
        if incident_data.severity in ["critical", "high"]:
            risks.append("High severity incident may require external resources")
        
        if incident_data.confidence_score < 70:
            risks.append("Low confidence in incident details may affect response accuracy")
        
        if "parking" in incident_data.location.lower():
            risks.append("Outdoor location may complicate evidence preservation")
        
        if incident_data.incident_type == "harassment":
            risks.append("Sensitive nature requires careful handling to prevent retaliation")
        
        risks.extend([
            "Media attention if incident becomes public",
            "Potential for copycat incidents",
            "Resource availability during peak times"
        ])
        
        return risks
    
    def _calculate_completion_time(self, immediate: List[ActionItem], 
                                 short_term: List[ActionItem], 
                                 long_term: List[ActionItem]) -> str:
        """Calculate estimated completion time"""
        # Simple estimation based on longest action duration
        max_duration_days = 7  # Default
        
        for action in long_term:
            if "week" in action.estimated_duration:
                weeks = int(action.estimated_duration.split()[0])
                max_duration_days = max(max_duration_days, weeks * 7)
        
        completion_time = datetime.now() + timedelta(days=max_duration_days)
        return completion_time.isoformat()
    
    def _validate_plan(self, plan: ResponsePlan, incident_data: IncidentData) -> Dict[str, Any]:
        """Validate the generated response plan"""
        warnings = []
        confidence = 100.0
        
        # Check if plan has sufficient immediate actions
        if len(plan.immediate_actions) < 2:
            warnings.append("Plan may need more immediate actions")
            confidence -= 10
        
        # Check stakeholder coverage
        if len(plan.stakeholders) < 3:
            warnings.append("Consider involving more stakeholders")
            confidence -= 5
        
        # Check resource availability
        if not plan.resources_required:
            warnings.append("No resources identified - may need manual review")
            confidence -= 10
        
        # Adjust confidence based on incident data confidence
        confidence = min(confidence, incident_data.confidence_score + 10)
        
        return {
            "status": "validated",
            "confidence": confidence,
            "warnings": warnings
        }
    
    def _create_minimal_plan(self, incident_data) -> ResponsePlan:
        """Create a minimal response plan as fallback"""
        plan_id = f"PLAN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Create basic immediate actions
        immediate_actions = [
            ActionItem(
                action_id="IMM-001",
                description="Assess situation and ensure immediate safety",
                responsible_party="Campus Security",
                priority="high",
                estimated_duration="15 minutes",
                resources_needed=["Security personnel"]
            ),
            ActionItem(
                action_id="IMM-002", 
                description="Notify appropriate authorities and stakeholders",
                responsible_party="Security Dispatcher",
                priority="high",
                estimated_duration="10 minutes",
                resources_needed=["Communication system"]
            )
        ]
        
        # Basic stakeholders
        stakeholders = [
            {
                "role": "Security Supervisor",
                "department": "Security",
                "notification_priority": "immediate",
                "contact_method": "radio",
                "responsibilities": ["Scene management"]
            }
        ]
        
        return ResponsePlan(
            plan_id=plan_id,
            incident_id=incident_data.incident_id if hasattr(incident_data, 'incident_id') else "unknown",
            plan_type="standard_response",
            priority_level="standard",
            immediate_actions=immediate_actions,
            short_term_actions=[],
            long_term_actions=[],
            stakeholders=stakeholders,
            resources_required=[],
            timeline={
                "incident_reported": datetime.now().isoformat(),
                "estimated_resolution": (datetime.now() + timedelta(hours=2)).isoformat()
            },
            success_criteria=["Situation stabilized", "Proper documentation completed"],
            risk_factors=["Limited information available"],
            created_at=datetime.now().isoformat(),
            estimated_completion=(datetime.now() + timedelta(hours=2)).isoformat()
        )

    def _load_action_templates(self) -> Dict[str, Dict[str, List[Dict]]]:
        """Load action templates for different incident types"""
        return {
            "assault": {
                "immediate": [
                    {
                        "description": "Ensure immediate safety of all parties at {location}",
                        "responsible": "Campus Security",
                        "priority": "critical",
                        "duration": "10 minutes",
                        "resources": ["Security personnel", "First aid kit"]
                    },
                    {
                        "description": "Contact medical services if medical attention needed",
                        "responsible": "Security Dispatcher",
                        "priority": "critical",
                        "duration": "5 minutes",
                        "resources": ["Emergency phone", "Medical information"]
                    }
                ],
                "short_term": [
                    {
                        "description": "Conduct preliminary investigation and gather witness statements",
                        "responsible": "Investigation Team",
                        "priority": "high",
                        "duration": "2 hours",
                        "resources": ["Interview rooms", "Recording equipment"]
                    }
                ],
                "long_term": [
                    {
                        "description": "Provide ongoing support and counseling services",
                        "responsible": "Counseling Services",
                        "priority": "medium",
                        "duration": "Ongoing",
                        "resources": ["Counseling staff", "Support materials"]
                    }
                ]
            },
            "theft": {
                "immediate": [
                    {
                        "description": "Secure the scene at {location} and preserve evidence",
                        "responsible": "Campus Security",
                        "priority": "high",
                        "duration": "20 minutes",
                        "resources": ["Barrier tape", "Evidence bags"]
                    },
                    {
                        "description": "Review security camera footage for the area",
                        "responsible": "Security Team",
                        "priority": "high",
                        "duration": "30 minutes",
                        "resources": ["Security system access", "Video equipment"]
                    }
                ],
                "short_term": [
                    {
                        "description": "File police report and coordinate with local authorities",
                        "responsible": "Security Supervisor",
                        "priority": "medium",
                        "duration": "1 hour",
                        "resources": ["Police contact information", "Incident documentation"]
                    }
                ],
                "long_term": [
                    {
                        "description": "Review and enhance security measures in the area",
                        "responsible": "Security Management",
                        "priority": "low",
                        "duration": "2 weeks",
                        "resources": ["Security assessment team", "Budget approval"]
                    }
                ]
            },
            "medical": {
                "immediate": [
                    {
                        "description": "Provide immediate medical assistance and contact medical services if needed",
                        "responsible": "First Responder",
                        "priority": "critical",
                        "duration": "Immediate",
                        "resources": ["First aid supplies", "Emergency phone"]
                    },
                    {
                        "description": "Clear area and ensure safe access for medical personnel",
                        "responsible": "Campus Security",
                        "priority": "critical",
                        "duration": "10 minutes",
                        "resources": ["Security personnel", "Crowd control barriers"]
                    }
                ],
                "short_term": [
                    {
                        "description": "Document incident and coordinate with medical professionals",
                        "responsible": "Health Services",
                        "priority": "high",
                        "duration": "1 hour",
                        "resources": ["Medical records", "Documentation forms"]
                    }
                ],
                "long_term": [
                    {
                        "description": "Follow up on injured party recovery and support needs",
                        "responsible": "Student Services",
                        "priority": "medium",
                        "duration": "2 weeks",
                        "resources": ["Contact information", "Support services"]
                    }
                ]
            }
        }
    
    def _load_stakeholder_mapping(self) -> Dict[str, List[Dict]]:
        """Load stakeholder mapping for incident types"""
        return {
            "assault": [
                {
                    "role": "Campus Security Chief",
                    "department": "Security",
                    "priority": "immediate",
                    "contact_method": "phone",
                    "responsibilities": ["Scene management", "Investigation oversight"]
                },
                {
                    "role": "Title IX Coordinator",
                    "department": "Compliance",
                    "priority": "urgent",
                    "contact_method": "email",
                    "responsibilities": ["Policy compliance", "Investigation support"]
                }
            ],
            "theft": [
                {
                    "role": "Security Supervisor",
                    "department": "Security",
                    "priority": "immediate",
                    "contact_method": "radio",
                    "responsibilities": ["Scene security", "Evidence preservation"]
                },
                {
                    "role": "Facilities Manager",
                    "department": "Facilities",
                    "priority": "standard",
                    "contact_method": "email",
                    "responsibilities": ["Security system review", "Access control"]
                }
            ],
            "medical": [
                {
                    "role": "Health Services Director",
                    "department": "Health Services",
                    "priority": "immediate",
                    "contact_method": "phone",
                    "responsibilities": ["Medical coordination", "Health records"]
                },
                {
                    "role": "Emergency Coordinator",
                    "department": "Emergency Management",
                    "priority": "urgent",
                    "contact_method": "phone",
                    "responsibilities": ["Emergency response", "External coordination"]
                }
            ]
        }
    
    def _load_resource_catalog(self) -> Dict[str, List[Dict]]:
        """Load resource catalog for incident types"""
        return {
            "assault": [
                {
                    "type": "Medical",
                    "description": "First aid and medical supplies",
                    "quantity": "1 kit",
                    "availability": "Always available",
                    "cost": "No additional cost"
                },
                {
                    "type": "Investigation",
                    "description": "Evidence collection materials",
                    "quantity": "1 kit",
                    "availability": "Business hours",
                    "cost": "$50"
                }
            ],
            "theft": [
                {
                    "type": "Security",
                    "description": "Barrier tape and evidence bags",
                    "quantity": "As needed",
                    "availability": "Always available",
                    "cost": "$25"
                },
                {
                    "type": "Technology",
                    "description": "Security camera system access",
                    "quantity": "System access",
                    "availability": "24/7",
                    "cost": "No additional cost"
                }
            ]
        }


# Export the node for use in the graph
def create_planner_node() -> PlannerNode:
    """Factory function to create planner node"""
    return PlannerNode()