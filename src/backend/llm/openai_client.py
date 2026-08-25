"""
OpenAI LLM Client for intelligent incident analysis
"""
import os
from typing import Dict, Any, List, Optional
from openai import OpenAI
import json

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv not installed, try to read .env manually
    try:
        with open('.env', 'r') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value.strip('"')
    except FileNotFoundError:
        pass

class OpenAIClient:
    """OpenAI client for intelligent incident analysis"""
    
    def __init__(self):
        # Initialize OpenAI client
        api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key or api_key == "your-openai-api-key-here":
            print("⚠️  OpenAI API key not configured. Using fallback responses.")
            print("   Set OPENAI_API_KEY environment variable for AI-powered responses.")
            self.client = None
            self.api_available = False
        else:
            try:
                self.client = OpenAI(api_key=api_key)
                # Test the API with a simple call
                test_response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Test"}],
                    max_tokens=5
                )
                self.api_available = True
                print("✅ OpenAI API configured and tested successfully")
            except Exception as e:
                print(f"⚠️  OpenAI API key provided but not working: {e}")
                print("   Using intelligent fallback responses instead.")
                self.client = None
                self.api_available = False
        
        self.model = "gpt-3.5-turbo"
    
    def analyze_incident(self, incident_report: str, incident_type: str, severity: str) -> Dict[str, Any]:
        """Analyze incident using OpenAI and return structured data"""
        
        # Return fallback immediately if API not available
        if not self.api_available:
            return self._create_fallback_analysis(incident_report, incident_type, severity)
        
        prompt = f"""
        You are an expert incident response analyst. Analyze the following incident report and provide a comprehensive analysis.

        Incident Report:
        {incident_report}

        Incident Type: {incident_type}
        Severity: {severity}

        Please provide a detailed analysis in the following JSON format:
        {{
            "incident_analysis": {{
                "description": "Detailed analysis of what happened",
                "key_factors": ["factor1", "factor2", "factor3"],
                "risk_assessment": "Assessment of risks involved",
                "urgency_level": "immediate/urgent/standard/routine"
            }},
            "entities": {{
                "people": ["person1", "person2"],
                "locations": ["location1", "location2"],
                "objects": ["object1", "object2"],
                "times": ["time1", "time2"],
                "organizations": ["org1", "org2"]
            }},
            "confidence_score": 85.5
        }}

        Provide realistic and contextually appropriate analysis based on the incident details.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert incident response analyst. Provide detailed, accurate analysis in valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Parse the JSON response
            content = response.choices[0].message.content
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return self._create_fallback_analysis(incident_report, incident_type, severity)
                
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._create_fallback_analysis(incident_report, incident_type, severity)
    
    def generate_response_plan(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate response plan using OpenAI"""
        
        # Return fallback immediately if API not available
        if not self.api_available:
            return self._create_fallback_plan(incident_data)
        
        prompt = f"""
        Based on the following incident analysis, create a comprehensive response plan.

        Incident Analysis:
        - Type: {incident_data.get('incident_type', 'unknown')}
        - Severity: {incident_data.get('severity', 'unknown')}
        - Description: {incident_data.get('description', 'No description')}
        - Location: {incident_data.get('location', 'Unknown location')}

        Create a detailed response plan in the following JSON format:
        {{
            "plan_type": "emergency_response/investigation/security/facilities",
            "priority_level": "critical/urgent/standard/routine",
            "immediate_actions": [
                {{
                    "description": "Detailed action description",
                    "responsible_party": "Who should do this",
                    "priority": "critical/high/medium/low",
                    "estimated_duration": "Time estimate"
                }}
            ],
            "stakeholders": [
                {{
                    "role": "Stakeholder role",
                    "department": "Department name",
                    "notification_priority": "immediate/urgent/standard",
                    "contact_method": "phone/email/radio"
                }}
            ],
            "success_criteria": ["criterion1", "criterion2"],
            "risk_factors": ["risk1", "risk2"]
        }}

        Provide realistic, actionable response plans appropriate for the incident type and severity.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert emergency response planner. Create detailed, actionable response plans in valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1200
            )
            
            content = response.choices[0].message.content
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return self._create_fallback_plan(incident_data)
                
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._create_fallback_plan(incident_data)
    
    def evaluate_response(self, incident_data: Dict[str, Any], response_plan: Dict[str, Any], 
                         execution_summary: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate response effectiveness using OpenAI"""
        
        # Return fallback immediately if API not available
        if not self.api_available:
            return self._create_fallback_evaluation()
        
        prompt = f"""
        Evaluate the effectiveness of this incident response based on the following information:

        Incident: {incident_data.get('incident_type', 'unknown')} - {incident_data.get('severity', 'unknown')}
        Response Plan: {len(response_plan.get('immediate_actions', []))} immediate actions planned
        Execution: {execution_summary.get('success_rate', 0)}% success rate

        Provide an evaluation in the following JSON format:
        {{
            "overall_score": 85,
            "effectiveness_rating": "Excellent/Good/Satisfactory/Needs Improvement/Poor",
            "response_quality": "Detailed assessment of response quality",
            "strengths": ["strength1", "strength2", "strength3"],
            "weaknesses": ["weakness1", "weakness2"],
            "lessons_learned": [
                {{
                    "lesson": "Key lesson learned",
                    "category": "process_improvement/communication/resource_management",
                    "priority": "high/medium/low"
                }}
            ],
            "improvement_recommendations": [
                {{
                    "title": "Recommendation title",
                    "description": "Detailed recommendation",
                    "priority": "high/medium/low",
                    "estimated_effort": "Time/resource estimate"
                }}
            ]
        }}

        Provide constructive, actionable feedback for improving future incident responses.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert incident response evaluator. Provide constructive, detailed evaluations in valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return self._create_fallback_evaluation()
                
        except Exception as e:
            print(f"OpenAI API error: {e}")
            return self._create_fallback_evaluation()
    
    def _create_fallback_analysis(self, incident_report: str, incident_type: str, severity: str) -> Dict[str, Any]:
        """Create fallback analysis when OpenAI is unavailable"""
        return {
            "incident_analysis": {
                "description": f"Analysis of {incident_type} incident with {severity} severity. Incident requires immediate attention and proper response coordination.",
                "key_factors": ["Incident severity", "Location factors", "Response time requirements"],
                "risk_assessment": "Moderate risk requiring standard response protocols",
                "urgency_level": "urgent" if severity in ["high", "critical"] else "standard"
            },
            "entities": {
                "people": ["Reporter", "Affected parties"],
                "locations": ["Incident location"],
                "objects": ["Incident-related items"],
                "times": ["Incident time"],
                "organizations": ["Campus Security", "Administration"]
            },
            "confidence_score": 75.0
        }
    
    def _create_fallback_plan(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create fallback response plan"""
        return {
            "plan_type": "standard_response",
            "priority_level": "standard",
            "immediate_actions": [
                {
                    "description": "Assess situation and ensure immediate safety of all parties",
                    "responsible_party": "Campus Security",
                    "priority": "critical",
                    "estimated_duration": "15 minutes"
                },
                {
                    "description": "Notify appropriate authorities and stakeholders",
                    "responsible_party": "Security Dispatcher",
                    "priority": "high",
                    "estimated_duration": "10 minutes"
                }
            ],
            "stakeholders": [
                {
                    "role": "Security Supervisor",
                    "department": "Campus Security",
                    "notification_priority": "immediate",
                    "contact_method": "radio"
                }
            ],
            "success_criteria": ["Situation stabilized", "Proper documentation completed"],
            "risk_factors": ["Time sensitivity", "Resource availability"]
        }
    
    def _create_fallback_evaluation(self) -> Dict[str, Any]:
        """Create fallback evaluation"""
        return {
            "overall_score": 75,
            "effectiveness_rating": "Good",
            "response_quality": "Response completed successfully with standard effectiveness",
            "strengths": ["Timely response", "Proper coordination", "Complete documentation"],
            "weaknesses": ["Could improve communication speed"],
            "lessons_learned": [
                {
                    "lesson": "Response workflow completed successfully",
                    "category": "process_improvement",
                    "priority": "medium"
                }
            ],
            "improvement_recommendations": [
                {
                    "title": "Enhance response time tracking",
                    "description": "Implement better time tracking for response activities",
                    "priority": "medium",
                    "estimated_effort": "2-3 weeks"
                }
            ]
        }

# Global instance
openai_client = OpenAIClient()