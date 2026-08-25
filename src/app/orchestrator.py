"""
Orchestrator - Coordinates the multi-agent workflow for incident analysis
"""
from typing import Dict, Any, Optional
from datetime import datetime
import json

from agents import (
    PromptAgent,
    PlannerAgent,
    ExecutorAgent,
    SafetyPolicyAgent,
    EvaluatorAgent
)

# Import analytics recording function
try:
    from backend.api.analytics_api import record_incident_analytics
except ImportError:
    # Fallback if analytics not available
    def record_incident_analytics(incident_data, evaluation_report=None):
        pass


class IncidentResponseOrchestrator:
    """
    Orchestrates the multi-agent workflow for campus incident report analysis
    
    Workflow:
    1. Prompt Agent: Process raw report → structured data
    2. Planner Agent: Create action plan
    3. Safety & Policy Agent: Validate compliance
    4. Executor Agent: Execute/simulate actions
    5. Evaluator Agent: Evaluate overall response
    """
    
    def __init__(self):
        self.prompt_agent = PromptAgent()
        self.planner_agent = PlannerAgent()
        self.executor_agent = ExecutorAgent()
        self.safety_agent = SafetyPolicyAgent()
        self.evaluator_agent = EvaluatorAgent()
        
        self.workflow_history: list = []
        self.current_incident: Optional[Dict[str, Any]] = None
    
    def process_incident(self, raw_report: str, 
                        metadata: Optional[Dict[str, Any]] = None,
                        execution_mode: str = "simulate") -> Dict[str, Any]:
        """
        Process incident report through complete agent workflow
        
        Args:
            raw_report: Raw incident report text
            metadata: Optional metadata about the report
            execution_mode: "simulate" or "execute"
        
        Returns:
            Complete workflow results from all agents
        """
        workflow_start = datetime.now()
        incident_id = f"INC-{workflow_start.strftime('%Y%m%d%H%M%S')}"
        
        print(f"\n{'='*80}")
        print(f"🚨 INCIDENT RESPONSE WORKFLOW - {incident_id}")
        print(f"{'='*80}\n")
        
        workflow_results = {
            "incident_id": incident_id,
            "workflow_start": workflow_start.isoformat(),
            "execution_mode": execution_mode,
            "stages": {}
        }
        
        try:
            # Stage 1: Prompt Agent - Process raw report
            print("📝 STAGE 1: Processing incident report...")
            prompt_input = {
                "raw_report": raw_report,
                "metadata": metadata or {"incident_id": incident_id}
            }
            prompt_result = self.prompt_agent.execute(prompt_input)
            workflow_results["stages"]["prompt"] = prompt_result
            
            if prompt_result.get("status") != "success":
                raise Exception(f"Prompt Agent failed: {prompt_result.get('error')}")
            
            print(f"   ✓ Incident Type: {prompt_result['structured_report']['incident_type']}")
            print(f"   ✓ Severity: {prompt_result['structured_report']['severity']}")
            print(f"   ✓ Completeness: {prompt_result['completeness_score']:.1f}%\n")
            
            # Stage 2: Planner Agent - Create action plan
            print("📋 STAGE 2: Creating action plan...")
            planner_input = {
                "structured_report": prompt_result["structured_report"],
                "extracted_entities": prompt_result["extracted_entities"],
                "prompt_for_analysis": prompt_result["prompt_for_analysis"],
                "metadata": prompt_result.get("metadata", {})
            }
            planner_result = self.planner_agent.execute(planner_input)
            workflow_results["stages"]["planner"] = planner_result
            
            if planner_result.get("status") != "success":
                raise Exception(f"Planner Agent failed: {planner_result.get('error')}")
            
            action_plan = planner_result["action_plan"]
            print(f"   ✓ Priority Level: {planner_result['priority_level']}")
            print(f"   ✓ Immediate Actions: {len(action_plan['immediate_actions'])}")
            print(f"   ✓ Stakeholders: {len(action_plan['stakeholders'])}")
            print(f"   ✓ Resources Needed: {len(action_plan['resources_needed'])}\n")
            
            # Stage 3: Safety & Policy Agent - Validate compliance
            print("🔒 STAGE 3: Validating safety and policy compliance...")
            safety_input = {
                "structured_report": prompt_result["structured_report"],
                "action_plan": action_plan,
                "execution_summary": {}
            }
            safety_result = self.safety_agent.execute(safety_input)
            workflow_results["stages"]["safety"] = safety_result
            
            if safety_result.get("status") != "success":
                raise Exception(f"Safety Agent failed: {safety_result.get('error')}")
            
            print(f"   ✓ Validation Result: {safety_result['validation_result']}")
            print(f"   ✓ Policy Compliance: {'✓' if safety_result['policy_compliance'].get('overall_compliant') else '✗'}")
            print(f"   ✓ Safety Checks: {'✓' if safety_result['safety_checks'].get('all_checks_passed') else '✗'}")
            print(f"   ✓ Violations Found: {len(safety_result['violations'])}")
            print(f"   ✓ Blocked Actions: {len(safety_result['blocked_actions'])}\n")
            
            # Check if any critical violations prevent execution
            if safety_result["validation_result"] == "blocked":
                print("   ⚠️  CRITICAL: Actions blocked due to policy violations")
                workflow_results["execution_blocked"] = True
                workflow_results["block_reason"] = "Policy violations detected"
            
            # Stage 4: Executor Agent - Execute actions
            print(f"⚙️  STAGE 4: {'Simulating' if execution_mode == 'simulate' else 'Executing'} action plan...")
            executor_input = {
                "action_plan": action_plan,
                "priority_level": planner_result["priority_level"],
                "mode": execution_mode
            }
            executor_result = self.executor_agent.execute(executor_input)
            workflow_results["stages"]["executor"] = executor_result
            
            if executor_result.get("status") != "success":
                raise Exception(f"Executor Agent failed: {executor_result.get('error')}")
            
            exec_summary = executor_result["execution_summary"]
            print(f"   ✓ Execution Status: {exec_summary['overall_status']}")
            print(f"   ✓ Actions Executed: {exec_summary['immediate_actions_executed']}")
            print(f"   ✓ Notifications Sent: {exec_summary['notifications_sent']}")
            print(f"   ✓ Resources Allocated: {exec_summary['resources_allocated']}\n")
            
            # Stage 5: Evaluator Agent - Evaluate response
            print("📊 STAGE 5: Evaluating incident response...")
            evaluator_input = {
                "structured_report": prompt_result["structured_report"],
                "action_plan": action_plan,
                "execution_summary": exec_summary,
                "safety_validation": safety_result,
                "extracted_entities": prompt_result["extracted_entities"],
                "metadata": metadata or {}
            }
            evaluator_result = self.evaluator_agent.execute(evaluator_input)
            workflow_results["stages"]["evaluator"] = evaluator_result
            
            if evaluator_result.get("status") != "success":
                raise Exception(f"Evaluator Agent failed: {evaluator_result.get('error')}")
            
            print(f"   ✓ Overall Score: {evaluator_result['overall_score']}/100")
            print(f"   ✓ Effectiveness Rating: {evaluator_result['effectiveness_rating']}")
            print(f"   ✓ Confidence Index: {evaluator_result.get('confidence_index', {}).get('overall_confidence', 'N/A'):.1f}%")
            print(f"   ✓ Resolution Status: {evaluator_result.get('resolution_status', 'unknown')}")
            print(f"   ✓ Human Intervention: {'Required' if evaluator_result.get('human_intervention_required', False) else 'Not Required'}")
            print(f"   ✓ Strengths Identified: {len(evaluator_result['strengths'])}")
            print(f"   ✓ Areas for Improvement: {len(evaluator_result['weaknesses'])}\n")
            
            # Finalize workflow
            workflow_end = datetime.now()
            workflow_results["workflow_end"] = workflow_end.isoformat()
            workflow_results["total_duration"] = (workflow_end - workflow_start).total_seconds()
            workflow_results["status"] = "success"
            
            # Store in history
            self.workflow_history.append(workflow_results)
            self.current_incident = workflow_results
            
            # Record analytics data
            try:
                incident_data = {
                    "incident_id": incident_id,
                    "incident_type": prompt_result["structured_report"]["incident_type"],
                    "severity": prompt_result["structured_report"]["severity"],
                    "location": prompt_result["structured_report"]["location"],
                    "anonymous": prompt_result["structured_report"].get("anonymous", False),
                    "submission_timestamp": workflow_start.isoformat(),
                    "resolution_status": "resolved" if evaluator_result["overall_score"] > 75 else "unresolved"
                }
                
                evaluation_data = {
                    "overall_score": evaluator_result["overall_score"],
                    "effectiveness_rating": evaluator_result["effectiveness_rating"],
                    "category_scores": evaluator_result.get("category_scores", [])
                }
                
                record_incident_analytics(incident_data, evaluation_data)
            except Exception as e:
                print(f"Warning: Could not record analytics: {e}")
            
            # Print summary
            self._print_summary(workflow_results)
            
            return workflow_results
            
        except Exception as e:
            workflow_results["status"] = "error"
            workflow_results["error"] = str(e)
            workflow_results["workflow_end"] = datetime.now().isoformat()
            
            print(f"\n❌ WORKFLOW ERROR: {str(e)}\n")
            
            return workflow_results
    
    def _print_summary(self, results: Dict[str, Any]):
        """Print workflow summary"""
        print(f"{'='*80}")
        print(f"📋 WORKFLOW SUMMARY")
        print(f"{'='*80}")
        
        evaluator = results["stages"]["evaluator"]
        
        print(f"\n🎯 Overall Performance:")
        print(f"   Score: {evaluator['overall_score']}/100")
        print(f"   Rating: {evaluator['effectiveness_rating']}")
        print(f"   Duration: {results['total_duration']:.2f} seconds")
        
        print(f"\n💪 Strengths:")
        for strength in evaluator["strengths"][:3]:
            print(f"   • {strength['category']}: {strength['description']}")
        
        if evaluator["weaknesses"]:
            print(f"\n⚠️  Areas for Improvement:")
            for weakness in evaluator["weaknesses"][:3]:
                print(f"   • {weakness['category']}: {weakness['description']}")
        
        print(f"\n📚 Key Lessons:")
        for lesson in evaluator["lessons_learned"][:2]:
            print(f"   • {lesson['lesson']}")
        
        print(f"\n{'='*80}\n")
    
    def get_incident_report(self, incident_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get incident report by ID or return current incident"""
        if incident_id:
            for incident in self.workflow_history:
                if incident["incident_id"] == incident_id:
                    return incident
            return None
        return self.current_incident
    
    def export_report(self, incident_id: Optional[str] = None, 
                     format: str = "json") -> str:
        """Export incident report"""
        incident = self.get_incident_report(incident_id)
        if not incident:
            return "Incident not found"
        
        if format == "json":
            return json.dumps(incident, indent=2)
        elif format == "summary":
            return self._generate_text_summary(incident)
        else:
            return "Unsupported format"
    
    def _generate_text_summary(self, incident: Dict[str, Any]) -> str:
        """Generate text summary of incident"""
        prompt_stage = incident["stages"]["prompt"]
        evaluator_stage = incident["stages"]["evaluator"]
        
        summary = f"""
CAMPUS INCIDENT REPORT - {incident['incident_id']}
{'='*80}

INCIDENT DETAILS:
Type: {prompt_stage['structured_report']['incident_type']}
Severity: {prompt_stage['structured_report']['severity']}
Location: {prompt_stage['structured_report']['location']}
Date/Time: {prompt_stage['structured_report']['datetime']}

RESPONSE EVALUATION:
Overall Score: {evaluator_stage['overall_score']}/100
Rating: {evaluator_stage['effectiveness_rating']}
Status: {incident['status']}

DESCRIPTION:
{prompt_stage['structured_report']['description'][:500]}...

{'='*80}
"""
        return summary
    
    def get_workflow_statistics(self) -> Dict[str, Any]:
        """Get statistics about processed incidents"""
        if not self.workflow_history:
            return {"total_incidents": 0}
        
        total = len(self.workflow_history)
        successful = sum(1 for w in self.workflow_history if w["status"] == "success")
        
        avg_score = sum(
            w["stages"]["evaluator"]["overall_score"] 
            for w in self.workflow_history 
            if w["status"] == "success"
        ) / successful if successful > 0 else 0
        
        incident_types = {}
        for w in self.workflow_history:
            if w["status"] == "success":
                itype = w["stages"]["prompt"]["structured_report"]["incident_type"]
                incident_types[itype] = incident_types.get(itype, 0) + 1
        
        return {
            "total_incidents": total,
            "successful": successful,
            "failed": total - successful,
            "average_score": round(avg_score, 2),
            "incident_types": incident_types
        }