"""
Multi-Provider LLM Client supporting various free AI APIs
"""
import os
import json
import requests
from typing import Dict, Any, List, Optional

class MultiProviderLLMClient:
    """LLM client supporting multiple free AI providers"""
    
    def __init__(self):
        self.providers = {
            'groq': self._init_groq()
        }
        
        # Find the first available provider
        self.active_provider = None
        self.client = None
        
        for provider_name, provider_info in self.providers.items():
            if provider_info['available']:
                self.active_provider = provider_name
                self.client = provider_info['client']
                print(f"✅ Using {provider_name.upper()} API for AI responses")
                break
        
        if not self.active_provider:
            print("⚠️  Groq API key not configured. Using intelligent fallback responses.")
            print("\n🔑 Get your free Groq API key at: https://console.groq.com/keys")
    
    def _init_groq(self):
        """Initialize Groq (Very fast, generous free tier)"""
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            try:
                # Test Groq API
                response = requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "llama-3.1-8b-instant",
                        "messages": [{"role": "user", "content": "test"}],
                        "max_tokens": 5
                    },
                    timeout=10
                )
                if response.status_code == 200:
                    return {
                        'available': True,
                        'client': 'groq',
                        'model': 'llama-3.1-8b-instant',
                        'api_key': api_key
                    }
            except Exception as e:
                print(f"Groq API test failed: {e}")
        
        return {'available': False, 'client': None}
    
    def analyze_incident(self, incident_report: str, incident_type: str, severity: str) -> Dict[str, Any]:
        """Analyze incident using available AI provider"""
        
        if not self.active_provider:
            return self._create_fallback_analysis(incident_report, incident_type, severity)
        
        prompt = f"""Analyze this incident report and provide a JSON response:

Incident: {incident_report}
Type: {incident_type}
Severity: {severity}

Respond with valid JSON only:
{{
    "incident_analysis": {{
        "description": "Brief analysis of what happened",
        "key_factors": ["factor1", "factor2"],
        "risk_assessment": "Risk level assessment",
        "urgency_level": "standard"
    }},
    "entities": {{
        "people": ["person1"],
        "locations": ["location1"],
        "objects": ["object1"],
        "times": ["time1"],
        "organizations": ["org1"]
    }},
    "confidence_score": 85.0
}}"""

        try:
            if self.active_provider == 'groq':
                return self._call_groq(prompt)
            else:
                return self._create_fallback_analysis(incident_report, incident_type, severity)
        except Exception as e:
            print(f"AI API call failed: {e}")
            return self._create_fallback_analysis(incident_report, incident_type, severity)
    
    def _call_groq(self, prompt: str) -> Dict[str, Any]:
        """Call Groq API"""
        provider_info = self.providers['groq']
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {provider_info['api_key']}",
                "Content-Type": "application/json"
            },
            json={
                "model": provider_info['model'],
                "messages": [
                    {"role": "system", "content": "You are an expert incident analyst. Respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 800,
                "temperature": 0.3
            }
        )
        
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Extract JSON from response if wrapped in text
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
        
        raise Exception(f"Groq API error: {response.status_code}")
    
    def _create_fallback_analysis(self, incident_report: str, incident_type: str, severity: str) -> Dict[str, Any]:
        """Create intelligent fallback analysis"""
        
        # Enhanced fallback with more contextual responses
        urgency_map = {
            'critical': 'immediate',
            'high': 'urgent', 
            'medium': 'standard',
            'low': 'routine'
        }
        
        # Extract key information from the report
        report_lower = incident_report.lower()
        
        # Smart entity extraction
        people = []
        locations = []
        objects = []
        times = []
        organizations = ['Campus Security']
        
        # Extract people mentions
        if 'student' in report_lower:
            people.append('Student')
        if 'faculty' in report_lower or 'professor' in report_lower:
            people.append('Faculty member')
        if 'staff' in report_lower:
            people.append('Staff member')
        
        # Extract locations
        location_keywords = ['library', 'dormitory', 'parking', 'gymnasium', 'cafeteria', 'classroom', 'lab', 'office']
        for keyword in location_keywords:
            if keyword in report_lower:
                locations.append(keyword.title())
        
        # Extract objects based on incident type
        if incident_type == 'theft':
            if 'laptop' in report_lower:
                objects.append('Laptop')
            if 'phone' in report_lower:
                objects.append('Phone')
            if 'wallet' in report_lower:
                objects.append('Wallet')
            if 'bike' in report_lower or 'bicycle' in report_lower:
                objects.append('Bicycle')
        elif incident_type == 'medical':
            objects.extend(['First aid kit', 'Medical supplies'])
        
        # Generate contextual description
        descriptions = {
            'medical': f"Medical emergency requiring immediate attention. {severity.title()} severity incident involving potential injury or health crisis.",
            'theft': f"Security incident involving stolen property. {severity.title()} priority case requiring investigation and recovery efforts.",
            'harassment': f"Behavioral incident requiring careful investigation. {severity.title()} severity case needing immediate intervention and support services.",
            'assault': f"Critical safety incident requiring immediate response. {severity.title()} severity case demanding emergency protocols and law enforcement coordination.",
            'fire': f"Emergency situation requiring immediate evacuation and fire response. {severity.title()} severity incident with potential property and safety risks.",
            'vandalism': f"Property damage incident requiring investigation and repair coordination. {severity.title()} severity case needing security review.",
            'maintenance': f"Facilities issue requiring prompt attention and repair. {severity.title()} priority maintenance request affecting campus operations."
        }
        
        description = descriptions.get(incident_type, f"Campus incident requiring appropriate response protocols. {severity.title()} severity case needing coordinated action.")
        
        # Generate key factors based on incident type and severity
        key_factors = [
            f"{severity.title()} severity level",
            f"{incident_type.title()} incident type",
            "Response time requirements"
        ]
        
        if severity in ['critical', 'high']:
            key_factors.append("Emergency response protocols")
        if incident_type in ['medical', 'assault', 'fire']:
            key_factors.append("Safety and security concerns")
        if incident_type in ['theft', 'vandalism']:
            key_factors.append("Investigation requirements")
        
        return {
            "incident_analysis": {
                "description": description,
                "key_factors": key_factors,
                "risk_assessment": f"{severity.title()} risk level requiring {urgency_map.get(severity, 'standard')} response protocols",
                "urgency_level": urgency_map.get(severity, 'standard')
            },
            "entities": {
                "people": people,
                "locations": locations,
                "objects": objects,
                "times": times,
                "organizations": organizations
            },
            "confidence_score": 75.0
        }
    
    def generate_response_plan(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response plan using available AI provider"""
        
        if not self.active_provider:
            return self._create_fallback_plan(incident_data)
        
        prompt = f"""Create a response plan for this incident in JSON format:

Incident Type: {incident_data.get('incident_type', 'unknown')}
Severity: {incident_data.get('severity', 'unknown')}
Location: {incident_data.get('location', 'unknown')}
Description: {incident_data.get('description', 'No description')}

IMPORTANT: Use campus security and medical services contacts, not 911.

Respond with valid JSON only:
{{
    "plan_type": "emergency_response",
    "priority_level": "standard",
    "immediate_actions": [
        {{
            "description": "Specific action to take immediately",
            "responsible_party": "Who should do this",
            "priority": "high",
            "estimated_duration": "15 minutes"
        }}
    ],
    "stakeholders": [
        {{
            "role": "Security Officer",
            "department": "Campus Security",
            "notification_priority": "immediate",
            "contact_method": "radio"
        }}
    ],
    "success_criteria": ["Situation stabilized", "Safety ensured"],
    "risk_factors": ["Time sensitivity", "Safety concerns"]
}}"""

        try:
            if self.active_provider == 'groq':
                return self._call_groq_plan(prompt)
            else:
                return self._create_fallback_plan(incident_data)
        except Exception as e:
            print(f"AI plan generation failed: {e}")
            return self._create_fallback_plan(incident_data)
    
    def _call_groq_plan(self, prompt: str) -> Dict[str, Any]:
        """Call Groq API for plan generation"""
        provider_info = self.providers['groq']
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {provider_info['api_key']}",
                "Content-Type": "application/json"
            },
            json={
                "model": provider_info['model'],
                "messages": [
                    {"role": "system", "content": "You are an expert emergency response planner for a university campus. Use campus security and medical services, never reference 911. Respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1000,
                "temperature": 0.3
            }
        )
        
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
        
        raise Exception(f"Groq plan API error: {response.status_code}")
    
    def _create_fallback_plan(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create intelligent fallback response plan"""
        incident_type = incident_data.get('incident_type', 'unknown')
        severity = incident_data.get('severity', 'medium')
        
        # Enhanced action templates based on incident type
        action_templates = {
            'medical': [
                {
                    "description": "Provide immediate medical assistance and contact medical services if needed",
                    "responsible_party": "First Responder",
                    "priority": "critical",
                    "estimated_duration": "Immediate"
                },
                {
                    "description": "Secure the area and ensure safe access for emergency personnel",
                    "responsible_party": "Campus Security",
                    "priority": "high",
                    "estimated_duration": "10 minutes"
                }
            ],
            'theft': [
                {
                    "description": "Secure the scene and preserve any evidence",
                    "responsible_party": "Campus Security",
                    "priority": "high",
                    "estimated_duration": "20 minutes"
                },
                {
                    "description": "Review security footage and gather witness statements",
                    "responsible_party": "Security Team",
                    "priority": "high",
                    "estimated_duration": "30 minutes"
                }
            ],
            'fire': [
                {
                    "description": "Activate fire alarm and initiate evacuation procedures",
                    "responsible_party": "Fire Safety Officer",
                    "priority": "critical",
                    "estimated_duration": "Immediate"
                },
                {
                    "description": "Contact fire department and coordinate emergency response",
                    "responsible_party": "Emergency Coordinator",
                    "priority": "critical",
                    "estimated_duration": "5 minutes"
                }
            ],
            'assault': [
                {
                    "description": "Ensure immediate safety of all parties and secure the area",
                    "responsible_party": "Campus Security",
                    "priority": "critical",
                    "estimated_duration": "Immediate"
                },
                {
                    "description": "Contact campus security and provide medical assistance if needed",
                    "responsible_party": "Security Supervisor",
                    "priority": "critical",
                    "estimated_duration": "5 minutes"
                }
            ]
        }
        
        # Get actions for incident type or use generic ones
        actions = action_templates.get(incident_type, [
            {
                "description": "Assess the situation and ensure immediate safety",
                "responsible_party": "Campus Security",
                "priority": "high",
                "estimated_duration": "15 minutes"
            },
            {
                "description": "Notify appropriate authorities and stakeholders",
                "responsible_party": "Security Dispatcher",
                "priority": "medium",
                "estimated_duration": "10 minutes"
            }
        ])
        
        # Determine plan type and priority
        plan_types = {
            'medical': 'emergency_response',
            'fire': 'emergency_response',
            'assault': 'emergency_response',
            'theft': 'security_response',
            'harassment': 'investigation_response',
            'vandalism': 'security_response'
        }
        
        priority_levels = {
            'critical': 'critical',
            'high': 'urgent',
            'medium': 'standard',
            'low': 'routine'
        }
        
        return {
            "plan_type": plan_types.get(incident_type, 'standard_response'),
            "priority_level": priority_levels.get(severity, 'standard'),
            "immediate_actions": actions,
            "stakeholders": [
                {
                    "role": "Security Supervisor",
                    "department": "Campus Security",
                    "notification_priority": "immediate",
                    "contact_method": "radio"
                },
                {
                    "role": "Emergency Coordinator",
                    "department": "Emergency Management",
                    "notification_priority": "urgent",
                    "contact_method": "phone"
                }
            ],
            "success_criteria": [
                "Immediate safety ensured",
                "Situation stabilized",
                "Proper documentation completed",
                "All stakeholders notified"
            ],
            "risk_factors": [
                "Time sensitivity",
                "Safety concerns",
                "Resource availability",
                "Communication coordination"
            ]
        }

    def generate_response(self, incident_context: Dict[str, Any], response_context: Dict[str, Any], execution_context: Dict[str, Any]) -> str:
        """Generate AI response for evaluation using available provider"""
        
        print(f"🤖 Generating AI evaluation response using {self.active_provider or 'fallback'}")
        
        if not self.active_provider:
            print("⚠️  No AI provider available - using intelligent fallback")
            return self._create_fallback_evaluation_response(incident_context, response_context, execution_context)
        
        prompt = f"""As an expert incident response evaluator, provide a comprehensive evaluation of this campus safety incident response:

INCIDENT ANALYSIS:
- Type: {incident_context.get('type', 'unknown')}
- Severity: {incident_context.get('severity', 'unknown')}
- Location: {incident_context.get('location', 'unknown')}
- Description: {incident_context.get('description', 'No description available')}

RESPONSE ANALYSIS:
- Plan Type: {response_context.get('plan_type', 'unknown')}
- Actions Taken: {response_context.get('immediate_actions', 0)} immediate actions
- Stakeholders: {response_context.get('stakeholders', 0)} stakeholders involved

EXECUTION ANALYSIS:
- Success Rate: {execution_context.get('success_rate', 75.0)}%
- Status: {execution_context.get('overall_status', 'unknown')}
- Duration: {execution_context.get('duration', 60)} minutes

Provide a detailed evaluation focusing on:
1. Response appropriateness for the specific incident type
2. Effectiveness of actions taken
3. Quality of decision-making
4. Areas where response exceeded or fell short
5. Specific, actionable lessons learned
6. Strategic recommendations for improvement

Return evaluation as JSON:
{{
    "overall_score": 85.0,
    "effectiveness_rating": "Excellent/Good/Satisfactory/Needs Improvement/Poor",
    "response_quality": "detailed assessment with specific insights",
    "key_insights": ["insight1", "insight2", "insight3"],
    "strengths": ["specific strength1", "specific strength2"],
    "weaknesses": ["specific weakness1", "specific weakness2"],
    "critical_gaps": ["gap1", "gap2"],
    "lessons_learned": [
        {{
            "category": "category",
            "lesson": "specific lesson",
            "evidence": "supporting evidence",
            "priority": "high/medium/low",
            "actionable_steps": ["step1", "step2"]
        }}
    ],
    "improvement_recommendations": [
        {{
            "title": "specific title",
            "description": "detailed description",
            "priority": "high/medium/low",
            "expected_benefit": "specific benefit",
            "implementation_timeline": "timeframe"
        }}
    ],
    "contextual_analysis": "how context affected response effectiveness",
    "future_preparedness": "assessment of preparedness for similar incidents"
}}"""

        try:
            if self.active_provider == 'groq':
                print(f"📡 Calling Groq API for evaluation...")
                result = self._call_groq_evaluation(prompt)
                print(f"✅ Received response from Groq API ({len(result)} characters)")
                return result
            else:
                print(f"🔄 Using fallback evaluation")
                return self._create_fallback_evaluation_response(incident_context, response_context, execution_context)
        except Exception as e:
            print(f"❌ AI evaluation generation failed: {e}")
            print(f"🔄 Falling back to intelligent evaluation")
            return self._create_fallback_evaluation_response(incident_context, response_context, execution_context)
    
    def _call_groq_evaluation(self, prompt: str) -> str:
        """Call Groq API for evaluation generation"""
        provider_info = self.providers['groq']
        
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {provider_info['api_key']}",
                "Content-Type": "application/json"
            },
            json={
                "model": provider_info['model'],
                "messages": [
                    {"role": "system", "content": "You are an expert incident response evaluator for a university campus. Provide detailed, actionable evaluations. Respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 1500,
                "temperature": 0.3
            }
        )
        
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            return content
        
        raise Exception(f"Groq evaluation API error: {response.status_code}")
    
    def _create_fallback_evaluation_response(self, incident_context: Dict[str, Any], response_context: Dict[str, Any], execution_context: Dict[str, Any]) -> str:
        """Create intelligent fallback evaluation response"""
        
        incident_type = incident_context.get('type', 'unknown')
        severity = incident_context.get('severity', 'medium')
        success_rate = execution_context.get('success_rate', 75.0)
        
        # Calculate overall score based on context
        base_score = success_rate
        if severity == 'critical' and success_rate > 80:
            base_score += 10  # Bonus for handling critical incidents well
        elif severity == 'low' and success_rate < 70:
            base_score -= 5   # Penalty for poor handling of simple incidents
        
        overall_score = min(100, max(0, base_score))
        
        # Determine effectiveness rating
        if overall_score >= 90:
            effectiveness_rating = "Excellent"
        elif overall_score >= 80:
            effectiveness_rating = "Good"
        elif overall_score >= 70:
            effectiveness_rating = "Satisfactory"
        elif overall_score >= 60:
            effectiveness_rating = "Needs Improvement"
        else:
            effectiveness_rating = "Poor"
        
        # Generate contextual response quality assessment
        response_quality = f"Response achieved {overall_score:.1f}% effectiveness for this {severity} severity {incident_type} incident. "
        
        if overall_score >= 85:
            response_quality += "Demonstrated strong coordination, appropriate resource allocation, and effective stakeholder communication."
        elif overall_score >= 70:
            response_quality += "Showed good response capabilities with some areas for optimization in coordination and resource management."
        else:
            response_quality += "Indicates need for improved response protocols, better resource coordination, and enhanced stakeholder communication."
        
        # Generate contextual insights
        key_insights = [
            f"Response effectiveness for {incident_type} incidents: {effectiveness_rating.lower()}",
            f"Stakeholder coordination achieved {execution_context.get('stakeholder_response_rate', 70):.1f}% engagement rate",
            f"Response time performance: {'excellent' if execution_context.get('duration', 60) < 30 else 'good' if execution_context.get('duration', 60) < 60 else 'needs improvement'}"
        ]
        
        # Generate strengths based on performance
        strengths = []
        if success_rate >= 85:
            strengths.append("High action completion rate demonstrates effective execution capabilities")
        if execution_context.get('stakeholder_response_rate', 70) >= 80:
            strengths.append("Strong stakeholder engagement and communication coordination")
        if execution_context.get('duration', 60) <= 30:
            strengths.append("Rapid response time meets emergency response standards")
        if severity in ['high', 'critical'] and overall_score >= 80:
            strengths.append(f"Effective handling of {severity} severity incident under pressure")
        
        if not strengths:
            strengths = ["Response protocols were followed according to standard procedures"]
        
        # Generate weaknesses based on gaps
        weaknesses = []
        if success_rate < 75:
            weaknesses.append("Action completion rate below optimal standards")
        if execution_context.get('stakeholder_response_rate', 70) < 70:
            weaknesses.append("Stakeholder engagement could be improved for better coordination")
        if execution_context.get('duration', 60) > 60:
            weaknesses.append("Response time exceeds recommended standards for this incident type")
        
        # Generate lessons learned
        lessons_learned = [
            {
                "category": "response_effectiveness",
                "lesson": f"Response protocol for {incident_type} incidents validated with {effectiveness_rating.lower()} performance",
                "evidence": f"Achieved {overall_score:.1f}% effectiveness score with {success_rate:.1f}% action completion",
                "priority": "medium",
                "actionable_steps": ["Continue monitoring response metrics", "Document successful procedures"]
            }
        ]
        
        if overall_score < 80:
            lessons_learned.append({
                "category": "improvement_opportunity",
                "lesson": "Response coordination and execution efficiency can be enhanced",
                "evidence": f"Performance gap identified in {', '.join(weaknesses[:2]) if weaknesses else 'coordination areas'}",
                "priority": "high",
                "actionable_steps": ["Review response procedures", "Enhance training programs", "Improve resource allocation"]
            })
        
        # Generate improvement recommendations
        improvement_recommendations = []
        
        if success_rate < 85:
            improvement_recommendations.append({
                "title": "Enhance Action Execution Efficiency",
                "description": "Implement systematic improvements to increase action completion rates and response effectiveness",
                "priority": "high" if success_rate < 70 else "medium",
                "expected_benefit": "15-20% improvement in response effectiveness",
                "implementation_timeline": "30-60 days"
            })
        
        if execution_context.get('duration', 60) > 45:
            improvement_recommendations.append({
                "title": "Optimize Response Time Performance",
                "description": "Streamline response procedures and improve coordination to reduce response times",
                "priority": "medium",
                "expected_benefit": "Faster incident resolution and improved safety outcomes",
                "implementation_timeline": "60-90 days"
            })
        
        if not improvement_recommendations:
            improvement_recommendations.append({
                "title": "Maintain Response Excellence",
                "description": "Continue current effective practices while monitoring for optimization opportunities",
                "priority": "low",
                "expected_benefit": "Sustained high performance and continuous improvement",
                "implementation_timeline": "Ongoing"
            })
        
        # Create JSON response
        evaluation_json = {
            "overall_score": overall_score,
            "effectiveness_rating": effectiveness_rating,
            "response_quality": response_quality,
            "key_insights": key_insights,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "critical_gaps": [],
            "lessons_learned": lessons_learned,
            "improvement_recommendations": improvement_recommendations,
            "contextual_analysis": f"Response effectiveness was influenced by {severity} severity level and {incident_type} incident characteristics, requiring appropriate resource allocation and stakeholder coordination",
            "future_preparedness": f"System demonstrates {'strong' if overall_score >= 85 else 'adequate' if overall_score >= 70 else 'developing'} preparedness for similar {incident_type} incidents"
        }
        
        return json.dumps(evaluation_json, indent=2)

# Global instance
multi_llm_client = MultiProviderLLMClient()