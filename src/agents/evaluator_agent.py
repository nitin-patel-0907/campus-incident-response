"""
Evaluator Agent - Evaluates incident handling and provides comprehensive analysis
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent
from datetime import datetime


class EvaluatorAgent(BaseAgent):
    """
    Agent responsible for evaluating the entire incident response process,
    providing analysis, scoring, and recommendations for improvement
    """
    
    def __init__(self):
        super().__init__(
            name="Evaluator Agent",
            description="Evaluates incident response and provides comprehensive analysis"
        )
        self.evaluation_criteria = self._load_evaluation_criteria()
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate incident response process with AI enhancement and confidence index
        
        Args:
            input_data: {
                "structured_report": dict - Original incident
                "action_plan": dict - Planned actions
                "execution_summary": dict - Execution results
                "safety_validation": dict - Safety check results
                "extracted_entities": dict - Extracted entities from prompt agent
                "metadata": dict - Additional metadata including images
            }
        
        Returns:
            {
                "overall_score": float - Overall response quality score (0-100)
                "category_scores": dict - Scores by category
                "strengths": list - Identified strengths
                "weaknesses": list - Areas for improvement
                "recommendations": list - Improvement recommendations
                "compliance_assessment": dict - Policy compliance evaluation
                "effectiveness_rating": str - Overall effectiveness
                "lessons_learned": list - Key takeaways
                "response_quality": str - Detailed response quality assessment
                "confidence_index": dict - Comprehensive confidence analysis
                "resolution_decision": dict - AI vs Human resolution decision
                "resolution_status": str - Final resolution status
                "resolution_reason": str - Reason for resolution decision
                "human_intervention_required": bool - Whether human intervention is needed
                "status": str
            }
        """
        try:
            structured_report = input_data.get("structured_report", {})
            action_plan = input_data.get("action_plan", {})
            execution_summary = input_data.get("execution_summary", {})
            safety_validation = input_data.get("safety_validation", {})
            extracted_entities = input_data.get("extracted_entities", {})
            metadata = input_data.get("metadata", {})
            
            print(f"🤖 Evaluator Agent: Processing {structured_report.get('incident_type', 'unknown')} incident evaluation...")
            
            # Calculate Confidence Index
            print(f"📊 Calculating Confidence Index...")
            confidence_analysis = self._calculate_confidence_index(
                structured_report, extracted_entities, metadata
            )
            
            print(f"   Confidence Score: {confidence_analysis['overall_confidence']:.1f}%")
            print(f"   Confidence Level: {confidence_analysis['confidence_level']}")
            print(f"   Resolution Recommendation: {confidence_analysis['resolution_recommendation']}")
            
            # Make resolution decision based on confidence
            resolution_decision = self._make_resolution_decision(confidence_analysis, structured_report)
            
            print(f"   Resolution Status: {resolution_decision['resolution_status']}")
            print(f"   Human Intervention: {'Required' if resolution_decision['human_intervention_required'] else 'Not Required'}")
            
            # Try AI-enhanced evaluation first
            ai_evaluation = self._try_ai_enhanced_evaluation(
                structured_report, action_plan, execution_summary, safety_validation
            )
            
            if ai_evaluation:
                print(f"✅ Using AI-enhanced evaluation with Groq API")
                # Add confidence index and resolution decision to AI evaluation
                ai_evaluation["confidence_index"] = confidence_analysis
                ai_evaluation["resolution_decision"] = resolution_decision
                ai_evaluation["resolution_status"] = resolution_decision["resolution_status"]
                ai_evaluation["resolution_reason"] = resolution_decision["resolution_reason"]
                ai_evaluation["human_intervention_required"] = resolution_decision["human_intervention_required"]
                ai_evaluation["resolution_details"] = resolution_decision["resolution_details"]
                ai_evaluation["rule_applied"] = resolution_decision["rule_applied"]
                return ai_evaluation
            
            print(f"🔄 Using standard evaluation (AI not available)")
            
            # Fallback to standard evaluation with confidence index
            standard_evaluation = self._perform_standard_evaluation(
                structured_report, action_plan, execution_summary, safety_validation
            )
            
            # Add confidence index and resolution decision to standard evaluation
            standard_evaluation["confidence_index"] = confidence_analysis
            standard_evaluation["resolution_decision"] = resolution_decision
            standard_evaluation["resolution_status"] = resolution_decision["resolution_status"]
            standard_evaluation["resolution_reason"] = resolution_decision["resolution_reason"]
            standard_evaluation["human_intervention_required"] = resolution_decision["human_intervention_required"]
            standard_evaluation["resolution_details"] = resolution_decision["resolution_details"]
            standard_evaluation["rule_applied"] = resolution_decision["rule_applied"]
            
            self.log_execution(input_data, standard_evaluation, "success")
            return standard_evaluation
            
        except Exception as e:
            error_output = {"status": "error", "error": str(e)}
            self.log_execution(input_data, error_output, "error")
            return error_output
    
    def _calculate_confidence_index(self, structured_report: Dict[str, Any], 
                                  extracted_entities: Dict[str, Any],
                                  metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate confidence index using the confidence calculator"""
        try:
            # Import the confidence calculator
            import sys
            from pathlib import Path
            
            # Add root directory to path
            root_path = Path(__file__).parent.parent
            if str(root_path) not in sys.path:
                sys.path.insert(0, str(root_path))
            
            try:
                from core.confidence_index_calculator import confidence_calculator
            except ImportError:
                from confidence_index_calculator import confidence_calculator
            
            # Extract image analyses from metadata
            image_analyses = []
            if metadata.get("uploaded_images"):
                for img_data in metadata["uploaded_images"]:
                    if isinstance(img_data, dict):
                        image_analyses.append(img_data)
            
            # Calculate confidence index
            confidence_analysis = confidence_calculator.calculate_confidence_index(
                structured_report=structured_report,
                extracted_entities=extracted_entities,
                image_analyses=image_analyses,
                metadata=metadata
            )
            
            return confidence_analysis
            
        except Exception as e:
            print(f"⚠️  Confidence index calculation failed: {e}")
            # Return default confidence analysis
            return {
                "overall_confidence": 70.0,
                "confidence_level": "medium",
                "resolution_recommendation": "supervised",
                "factor_scores": {
                    "prompt_quality": 70.0,
                    "image_authenticity": 70.0,
                    "description_completeness": 70.0,
                    "incident_complexity": 70.0,
                    "historical_success": 70.0
                },
                "confidence_reasoning": ["Default confidence analysis due to calculation error"],
                "intervention_triggers": [],
                "threshold_analysis": {
                    "autonomous_threshold": 75.0,
                    "human_intervention_threshold": 50.0,
                    "current_score": 70.0,
                    "can_resolve_autonomously": False,
                    "requires_human_intervention": False
                }
            }
    
    def _make_resolution_decision(self, confidence_analysis: Dict[str, Any], 
                                structured_report: Dict[str, Any]) -> Dict[str, Any]:
        """Make resolution decision based on confidence index"""
        
        overall_confidence = confidence_analysis["overall_confidence"]
        recommendation = confidence_analysis["resolution_recommendation"]
        
        # Determine resolution status and reasoning
        if recommendation == "autonomous":
            resolution_status = "resolved"
            resolution_reason = f"High confidence ({overall_confidence:.1f}%) allows autonomous AI resolution"
            human_intervention_required = False
            resolution_details = "AI system has sufficient confidence to resolve this incident autonomously based on comprehensive analysis of all factors."
            rule_applied = "autonomous_resolution_high_confidence"
            
        elif recommendation == "supervised":
            resolution_status = "under_review"
            resolution_reason = f"Medium confidence ({overall_confidence:.1f}%) requires supervised resolution"
            human_intervention_required = True
            resolution_details = "AI system can provide resolution recommendations but requires human oversight and approval before final resolution."
            rule_applied = "supervised_resolution_medium_confidence"
            
        else:  # human_required
            resolution_status = "unresolved"
            resolution_reason = f"Low confidence ({overall_confidence:.1f}%) requires human intervention"
            human_intervention_required = True
            resolution_details = "AI system lacks sufficient confidence to provide reliable resolution. Human analysis and decision-making required."
            rule_applied = "human_required_low_confidence"
        
        # Add specific intervention triggers
        intervention_triggers = confidence_analysis.get("intervention_triggers", [])
        if intervention_triggers:
            resolution_details += f" Specific concerns: {'; '.join(intervention_triggers)}"
        
        return {
            "resolution_status": resolution_status,
            "resolution_reason": resolution_reason,
            "human_intervention_required": human_intervention_required,
            "resolution_details": resolution_details,
            "rule_applied": rule_applied,
            "confidence_based_decision": True,
            "decision_factors": {
                "overall_confidence": overall_confidence,
                "recommendation": recommendation,
                "intervention_triggers": intervention_triggers,
                "factor_scores": confidence_analysis.get("factor_scores", {})
            }
        }
    
    def _perform_standard_evaluation(self, structured_report: Dict[str, Any],
                                   action_plan: Dict[str, Any],
                                   execution_summary: Dict[str, Any],
                                   safety_validation: Dict[str, Any]) -> Dict[str, Any]:
        """Perform standard evaluation when AI enhancement is not available"""
        
        # Evaluate response timeliness
        timeliness_score = self._evaluate_timeliness(action_plan, execution_summary)
        
        # Evaluate completeness
        completeness_score = self._evaluate_completeness(
            structured_report, action_plan
        )
        
        # Evaluate policy compliance
        compliance_score = self._evaluate_compliance(
            safety_validation, action_plan
        )
        
        # Evaluate resource allocation
        resource_score = self._evaluate_resource_allocation(action_plan)
        
        # Evaluate communication effectiveness
        communication_score = self._evaluate_communication(action_plan)
        
        # Evaluate safety measures
        safety_score = self._evaluate_safety_measures(
            action_plan, safety_validation
        )
        
        # Calculate category scores
        category_scores = {
            "timeliness": timeliness_score,
            "completeness": completeness_score,
            "policy_compliance": compliance_score,
            "resource_allocation": resource_score,
            "communication": communication_score,
            "safety_measures": safety_score
        }
        
        # Calculate overall score
        overall_score = sum(category_scores.values()) / len(category_scores)
        
        # Identify strengths and weaknesses
        strengths = self._identify_strengths(category_scores, action_plan)
        weaknesses = self._identify_weaknesses(category_scores, action_plan)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            category_scores, weaknesses, structured_report
        )
        
        # Assess compliance
        compliance_assessment = self._assess_compliance(safety_validation)
        
        # Determine effectiveness rating
        effectiveness_rating = self._determine_effectiveness_rating(overall_score)
        
        # Generate response quality assessment
        response_quality = self._generate_response_quality_assessment(
            overall_score, effectiveness_rating, structured_report
        )
        
        # Extract lessons learned
        lessons_learned = self._extract_lessons_learned(
            structured_report, action_plan, category_scores
        )
        
        # Generate detailed analysis
        detailed_analysis = self._generate_detailed_analysis(
            structured_report, action_plan, category_scores
        )
        
        # Create improvement plan
        improvement_plan = self._create_improvement_plan(weaknesses, recommendations)
        
        return {
            "overall_score": round(overall_score, 2),
            "category_scores": {k: round(v, 2) for k, v in category_scores.items()},
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "compliance_assessment": compliance_assessment,
            "effectiveness_rating": effectiveness_rating,
            "response_quality": response_quality,
            "lessons_learned": lessons_learned,
            "detailed_analysis": detailed_analysis,
            "improvement_plan": improvement_plan,
            "evaluation_summary": self._create_summary(
                overall_score, effectiveness_rating, len(strengths), len(weaknesses)
            ),
            "status": "success",
            "evaluation_timestamp": datetime.now().isoformat()
        }
    
    def _try_ai_enhanced_evaluation(self, structured_report: Dict[str, Any], 
                                   action_plan: Dict[str, Any], 
                                   execution_summary: Dict[str, Any],
                                   safety_validation: Dict[str, Any]) -> Dict[str, Any]:
        """Try to get AI-enhanced evaluation using Groq API"""
        try:
            # Import the multi-provider client
            import sys
            import os
            from pathlib import Path
            
            # Add backend to path
            backend_path = Path(__file__).parent.parent / "backend"
            if str(backend_path) not in sys.path:
                sys.path.insert(0, str(backend_path))
            
            from llm.multi_provider_client import multi_llm_client
            
            if not multi_llm_client.active_provider:
                print("⚠️  No AI provider available for enhanced evaluation")
                return None
            
            print(f"🤖 Using {multi_llm_client.active_provider.upper()} API for enhanced evaluation")
            
            # Prepare context for AI evaluation
            incident_context = {
                'type': structured_report.get('incident_type', 'unknown'),
                'severity': structured_report.get('severity', 'unknown'),
                'location': structured_report.get('location', 'unknown'),
                'description': structured_report.get('description', 'No description available')
            }
            
            response_context = {
                'plan_type': action_plan.get('plan_type', 'unknown'),
                'immediate_actions': len(action_plan.get('immediate_actions', [])),
                'stakeholders': len(action_plan.get('stakeholders', []))
            }
            
            execution_context = {
                'success_rate': execution_summary.get('success_rate', 75.0),
                'overall_status': execution_summary.get('overall_status', 'unknown'),
                'duration': 60  # Default duration
            }
            
            # Get AI response
            ai_response = multi_llm_client.generate_response(
                incident_context, response_context, execution_context
            )
            
            # Parse AI response
            import json
            import re
            
            json_match = re.search(r'\{.*\}', str(ai_response), re.DOTALL)
            if json_match:
                ai_evaluation = json.loads(json_match.group())
                
                print(f"✅ AI Evaluation Score: {ai_evaluation.get('overall_score', 'N/A')}")
                print(f"📝 AI Response Quality: {ai_evaluation.get('response_quality', 'N/A')[:100]}...")
                
                # Convert AI evaluation to agent format
                return self._convert_ai_evaluation_to_agent_format(
                    ai_evaluation, structured_report, action_plan, execution_summary, safety_validation
                )
            else:
                print("⚠️  Could not parse AI response as JSON")
                return None
                
        except Exception as e:
            print(f"❌ AI-enhanced evaluation failed: {e}")
            return None
    
    def _convert_ai_evaluation_to_agent_format(self, ai_evaluation: Dict[str, Any],
                                              structured_report: Dict[str, Any],
                                              action_plan: Dict[str, Any],
                                              execution_summary: Dict[str, Any],
                                              safety_validation: Dict[str, Any]) -> Dict[str, Any]:
        """Convert AI evaluation to agent output format"""
        
        # Extract AI evaluation data
        overall_score = ai_evaluation.get('overall_score', 75.0)
        effectiveness_rating = ai_evaluation.get('effectiveness_rating', 'Good')
        response_quality = ai_evaluation.get('response_quality', 'AI-enhanced evaluation completed')
        
        # Convert AI strengths to agent format
        ai_strengths = ai_evaluation.get('strengths', [])
        strengths = []
        for i, strength in enumerate(ai_strengths):
            strengths.append({
                "category": f"ai_strength_{i+1}",
                "score": "85.0",  # Default high score for AI-identified strengths
                "description": strength
            })
        
        # Convert AI weaknesses to agent format
        ai_weaknesses = ai_evaluation.get('weaknesses', [])
        weaknesses = []
        for i, weakness in enumerate(ai_weaknesses):
            weaknesses.append({
                "category": f"ai_weakness_{i+1}",
                "score": "60.0",  # Default lower score for AI-identified weaknesses
                "description": weakness,
                "severity": "moderate"
            })
        
        # Convert AI lessons learned to agent format
        ai_lessons = ai_evaluation.get('lessons_learned', [])
        lessons_learned = []
        for lesson in ai_lessons:
            if isinstance(lesson, dict):
                lessons_learned.append({
                    "lesson": lesson.get('lesson', 'AI-generated lesson'),
                    "application": lesson.get('evidence', 'Apply this insight to future incidents')
                })
            else:
                lessons_learned.append({
                    "lesson": str(lesson),
                    "application": "Apply this insight to future incidents"
                })
        
        # Convert AI recommendations to agent format
        ai_recommendations = ai_evaluation.get('improvement_recommendations', [])
        recommendations = []
        for rec in ai_recommendations:
            if isinstance(rec, dict):
                recommendations.append({
                    "area": rec.get('category', 'improvement'),
                    "recommendation": rec.get('title', 'AI-generated recommendation'),
                    "priority": rec.get('priority', 'medium'),
                    "expected_impact": rec.get('expected_benefit', 'Improved response effectiveness')
                })
            else:
                recommendations.append({
                    "area": "improvement",
                    "recommendation": str(rec),
                    "priority": "medium",
                    "expected_impact": "Improved response effectiveness"
                })
        
        # Generate category scores based on AI evaluation
        category_scores = {
            "ai_overall_assessment": overall_score,
            "response_appropriateness": min(100, overall_score + 5),
            "execution_quality": min(100, overall_score),
            "stakeholder_engagement": min(100, overall_score - 5),
            "policy_compliance": 85.0,  # Default good compliance
            "safety_measures": 80.0     # Default good safety
        }
        
        # Assess compliance (use existing method)
        compliance_assessment = self._assess_compliance(safety_validation)
        
        # Generate detailed analysis
        detailed_analysis = {
            "ai_enhanced": True,
            "incident_characteristics": {
                "type": structured_report.get("incident_type", "Unknown"),
                "severity": structured_report.get("severity", "Unknown"),
                "ai_complexity_assessment": ai_evaluation.get('contextual_analysis', 'Standard complexity')
            },
            "response_quality": {
                "ai_assessment": response_quality,
                "future_preparedness": ai_evaluation.get('future_preparedness', 'Good preparedness'),
                "contextual_factors": ai_evaluation.get('contextual_analysis', 'Context considered')
            },
            "ai_insights": ai_evaluation.get('key_insights', [])
        }
        
        # Create improvement plan
        improvement_plan = {
            "ai_generated": True,
            "immediate_actions": [r["recommendation"] for r in recommendations if r.get("priority") == "high"],
            "short_term_actions": [r["recommendation"] for r in recommendations if r.get("priority") == "medium"],
            "long_term_actions": [r["recommendation"] for r in recommendations if r.get("priority") == "low"],
            "success_metrics": [
                f"Achieve overall score above {overall_score + 10}",
                "Implement AI-recommended improvements",
                "Maintain response effectiveness"
            ]
        }
        
        return {
            "overall_score": round(overall_score, 2),
            "category_scores": {k: round(v, 2) for k, v in category_scores.items()},
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendations": recommendations,
            "compliance_assessment": compliance_assessment,
            "effectiveness_rating": effectiveness_rating,
            "response_quality": response_quality,
            "lessons_learned": lessons_learned,
            "detailed_analysis": detailed_analysis,
            "improvement_plan": improvement_plan,
            "evaluation_summary": f"AI-enhanced evaluation rated response as '{effectiveness_rating}' with {overall_score:.1f}/100 score. {len(strengths)} strengths and {len(weaknesses)} areas for improvement identified.",
            "ai_enhanced": True,
            "status": "success",
            "evaluation_timestamp": datetime.now().isoformat()
        }
    
    def _generate_response_quality_assessment(self, overall_score: float, 
                                            effectiveness_rating: str,
                                            structured_report: Dict[str, Any]) -> str:
        """Generate detailed response quality assessment"""
        incident_type = structured_report.get('incident_type', 'unknown')
        severity = structured_report.get('severity', 'unknown')
        
        base_assessment = f"Response to {incident_type} incident achieved {overall_score:.1f}% effectiveness rating of '{effectiveness_rating}'. "
        
        if overall_score >= 90:
            quality_detail = "Demonstrated exceptional coordination, comprehensive planning, and outstanding execution across all response areas."
        elif overall_score >= 80:
            quality_detail = "Showed strong response capabilities with effective coordination and good execution, with minor areas for optimization."
        elif overall_score >= 70:
            quality_detail = "Met standard response requirements with adequate coordination and execution, though some areas need improvement."
        elif overall_score >= 60:
            quality_detail = "Provided basic response coverage but requires significant improvements in coordination and execution effectiveness."
        else:
            quality_detail = "Response fell below acceptable standards and requires comprehensive review and improvement across multiple areas."
        
        context_detail = f"Given the {severity} severity level of this {incident_type} incident, "
        if severity in ['high', 'critical'] and overall_score >= 80:
            context_detail += "the response demonstrated strong capability under pressure."
        elif severity in ['low', 'medium'] and overall_score >= 70:
            context_detail += "the response met expected standards for this incident type."
        else:
            context_detail += "the response indicates need for enhanced protocols and training."
        
        return base_assessment + quality_detail + " " + context_detail
    
    def _load_evaluation_criteria(self) -> Dict[str, Any]:
        """Load evaluation criteria and weights"""
        return {
            "timeliness": {
                "weight": 0.20,
                "excellent": "All immediate actions initiated within 1 hour",
                "good": "Most immediate actions initiated within 2 hours",
                "adequate": "Immediate actions initiated within 4 hours",
                "poor": "Delayed response beyond 4 hours"
            },
            "completeness": {
                "weight": 0.20,
                "excellent": "All required fields documented, comprehensive plan",
                "good": "Most fields documented, solid plan",
                "adequate": "Basic documentation, basic plan",
                "poor": "Incomplete documentation or plan"
            },
            "compliance": {
                "weight": 0.25,
                "excellent": "100% policy compliance",
                "good": "Minor compliance issues",
                "adequate": "Some compliance gaps",
                "poor": "Major compliance violations"
            },
            "resources": {
                "weight": 0.15,
                "excellent": "Optimal resource allocation",
                "good": "Appropriate resources allocated",
                "adequate": "Minimal resources allocated",
                "poor": "Insufficient resources"
            },
            "communication": {
                "weight": 0.10,
                "excellent": "Timely, clear communication to all stakeholders",
                "good": "Good communication with minor gaps",
                "adequate": "Basic communication completed",
                "poor": "Poor or delayed communication"
            },
            "safety": {
                "weight": 0.10,
                "excellent": "All safety protocols followed",
                "good": "Most safety measures in place",
                "adequate": "Basic safety addressed",
                "poor": "Safety concerns not adequately addressed"
            }
        }
    
    def _evaluate_timeliness(self, plan: Dict[str, Any], execution: Dict[str, Any]) -> float:
        """Evaluate response timeliness"""
        immediate_actions = plan.get("immediate_actions", [])
        
        if not immediate_actions:
            return 50.0  # Penalty for no immediate actions
        
        # Check if high-priority actions are scheduled appropriately
        has_immediate_response = len(immediate_actions) > 0
        priority = plan.get("priority_level", "medium")
        
        score = 70.0  # Base score
        
        if has_immediate_response:
            score += 20.0
        
        if priority in ["critical", "high"] and len(immediate_actions) >= 3:
            score += 10.0
        
        return min(score, 100.0)
    
    def _evaluate_completeness(self, report: Dict[str, Any], plan: Dict[str, Any]) -> float:
        """Evaluate completeness of response"""
        score = 0.0
        
        # Check report completeness
        required_fields = ["incident_type", "location", "datetime", "description"]
        filled_fields = sum(1 for field in required_fields if report.get(field) and 
                          report[field] not in ["Unknown", "not specified", ""])
        score += (filled_fields / len(required_fields)) * 40
        
        # Check plan completeness
        has_immediate = len(plan.get("immediate_actions", [])) > 0
        has_short_term = len(plan.get("short_term_actions", [])) > 0
        has_long_term = len(plan.get("long_term_actions", [])) > 0
        has_stakeholders = len(plan.get("stakeholders", [])) > 0
        has_resources = len(plan.get("resources_needed", [])) > 0
        
        completeness_items = [has_immediate, has_short_term, has_long_term, 
                             has_stakeholders, has_resources]
        score += (sum(completeness_items) / len(completeness_items)) * 60
        
        return min(score, 100.0)
    
    def _evaluate_compliance(self, safety: Dict[str, Any], plan: Dict[str, Any]) -> float:
        """Evaluate policy compliance"""
        if not safety:
            return 50.0
        
        score = 0.0
        
        # Check validation result
        validation_result = safety.get("validation_result", "")
        if validation_result == "approved":
            score += 40.0
        elif validation_result == "modified":
            score += 30.0
        elif validation_result == "blocked":
            score += 0.0
        
        # Check policy compliance
        policy_compliance = safety.get("policy_compliance", {})
        if policy_compliance.get("overall_compliant"):
            score += 30.0
        else:
            # Partial credit based on individual checks
            checks = policy_compliance.get("policy_checks", [])
            if checks:
                compliant_checks = sum(1 for c in checks if c.get("status") == "compliant")
                score += (compliant_checks / len(checks)) * 30
        
        # Check safety checks
        safety_checks = safety.get("safety_checks", {})
        if safety_checks.get("all_checks_passed"):
            score += 30.0
        else:
            checks = safety_checks.get("checks", [])
            if checks:
                passed_checks = sum(1 for c in checks if c.get("passed"))
                score += (passed_checks / len(checks)) * 30
        
        return min(score, 100.0)
    
    def _evaluate_resource_allocation(self, plan: Dict[str, Any]) -> float:
        """Evaluate resource allocation"""
        resources = plan.get("resources_needed", [])
        
        if not resources:
            return 40.0  # Minimal score for no resources
        
        score = 50.0  # Base score
        
        # Bonus for diverse resource types
        resource_types = set(r.get("type", "") for r in resources)
        score += len(resource_types) * 10
        
        # Bonus for appropriate availability
        immediate_available = sum(1 for r in resources if r.get("availability") == "immediate")
        if immediate_available > 0:
            score += 15
        
        return min(score, 100.0)
    
    def _evaluate_communication(self, plan: Dict[str, Any]) -> float:
        """Evaluate communication effectiveness"""
        stakeholders = plan.get("stakeholders", [])
        comm_plan = plan.get("communication_plan", {})
        
        score = 0.0
        
        # Check stakeholder identification
        if len(stakeholders) >= 3:
            score += 40.0
        elif len(stakeholders) > 0:
            score += 25.0
        
        # Check communication plan
        if comm_plan:
            has_internal = len(comm_plan.get("internal_notifications", [])) > 0
            has_updates = comm_plan.get("updates_schedule") is not None
            
            if has_internal:
                score += 30.0
            if has_updates:
                score += 30.0
        
        return min(score, 100.0)
    
    def _evaluate_safety_measures(self, plan: Dict[str, Any], safety: Dict[str, Any]) -> float:
        """Evaluate safety measures"""
        score = 0.0
        
        # Check if safety is addressed in immediate actions
        immediate = plan.get("immediate_actions", [])
        has_safety_action = any("safety" in a.get("action", "").lower() for a in immediate)
        if has_safety_action:
            score += 40.0
        
        # Check safety validation
        if safety:
            safety_checks = safety.get("safety_checks", {})
            if safety_checks.get("all_checks_passed"):
                score += 40.0
            
            # Check for recommendations
            recommendations = safety.get("recommendations", [])
            if recommendations:
                score += 20.0
        
        return min(score, 100.0)
    
    def _identify_strengths(self, scores: Dict[str, float], plan: Dict[str, Any]) -> List[Dict[str, str]]:
        """Identify strengths in the response"""
        strengths = []
        
        for category, score in scores.items():
            if score >= 80.0:
                strengths.append({
                    "category": category,
                    "score": f"{score:.1f}",
                    "description": self._get_strength_description(category, score)
                })
        
        return strengths
    
    def _identify_weaknesses(self, scores: Dict[str, float], plan: Dict[str, Any]) -> List[Dict[str, str]]:
        """Identify weaknesses in the response"""
        weaknesses = []
        
        for category, score in scores.items():
            if score < 70.0:
                weaknesses.append({
                    "category": category,
                    "score": f"{score:.1f}",
                    "description": self._get_weakness_description(category, score),
                    "severity": "critical" if score < 50 else "moderate"
                })
        
        return weaknesses
    
    def _get_strength_description(self, category: str, score: float) -> str:
        """Get description for strength"""
        descriptions = {
            "timeliness": "Response time meets or exceeds standards with prompt action initiation",
            "completeness": "Comprehensive documentation and thorough action planning",
            "policy_compliance": "Strong adherence to campus policies and regulatory requirements",
            "resource_allocation": "Effective and appropriate allocation of resources",
            "communication": "Clear and timely communication with all relevant stakeholders",
            "safety_measures": "Robust safety protocols and victim support measures"
        }
        return descriptions.get(category, "Strong performance in this area")
    
    def _get_weakness_description(self, category: str, score: float) -> str:
        """Get description for weakness"""
        descriptions = {
            "timeliness": "Response time needs improvement; delays in action initiation",
            "completeness": "Incomplete documentation or insufficient action planning",
            "policy_compliance": "Gaps in policy adherence; compliance issues identified",
            "resource_allocation": "Insufficient or inappropriate resource allocation",
            "communication": "Communication gaps or delays with stakeholders",
            "safety_measures": "Safety protocols need strengthening"
        }
        return descriptions.get(category, "Area requires improvement")
    
    def _generate_recommendations(self, scores: Dict[str, float], 
                                 weaknesses: List[Dict[str, str]],
                                 report: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate improvement recommendations"""
        recommendations = []
        
        for weakness in weaknesses:
            category = weakness["category"]
            recommendations.append({
                "area": category,
                "recommendation": self._get_recommendation_for_category(category),
                "priority": "high" if float(weakness["score"]) < 50 else "medium",
                "expected_impact": "Significant improvement in response quality"
            })
        
        # Add general recommendations
        if report.get("severity") in ["high", "critical"]:
            recommendations.append({
                "area": "training",
                "recommendation": "Conduct emergency response training for staff",
                "priority": "medium",
                "expected_impact": "Better preparedness for critical incidents"
            })
        
        return recommendations
    
    def _get_recommendation_for_category(self, category: str) -> str:
        """Get specific recommendation for category"""
        recommendations = {
            "timeliness": "Implement automated alert system for faster incident response",
            "completeness": "Use standardized incident report templates with required fields",
            "policy_compliance": "Provide regular policy training and compliance audits",
            "resource_allocation": "Develop resource allocation guidelines for different incident types",
            "communication": "Establish clear communication protocols and stakeholder lists",
            "safety_measures": "Review and update safety protocols; increase safety training"
        }
        return recommendations.get(category, "Review and improve processes in this area")
    
    def _assess_compliance(self, safety: Dict[str, Any]) -> Dict[str, Any]:
        """Assess overall compliance"""
        if not safety:
            return {"status": "not_evaluated", "score": 0}
        
        validation_result = safety.get("validation_result", "")
        violations = safety.get("violations", [])
        
        return {
            "status": validation_result,
            "violations_found": len(violations),
            "critical_violations": sum(1 for v in violations if v.get("severity") == "critical"),
            "compliance_level": "full" if validation_result == "approved" else "partial",
            "requires_action": len(violations) > 0
        }
    
    def _determine_effectiveness_rating(self, score: float) -> str:
        """Determine overall effectiveness rating"""
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Very Good"
        elif score >= 70:
            return "Good"
        elif score >= 60:
            return "Adequate"
        else:
            return "Needs Improvement"
    
    def _extract_lessons_learned(self, report: Dict[str, Any], 
                                 plan: Dict[str, Any],
                                 scores: Dict[str, float]) -> List[Dict[str, str]]:
        """Extract lessons learned"""
        lessons = []
        
        # Lesson from incident type
        incident_type = report.get("incident_type", "")
        lessons.append({
            "lesson": f"Response protocol for {incident_type} incidents validated",
            "application": "Use this response pattern for similar incidents"
        })
        
        # Lessons from high scores
        high_scores = [cat for cat, score in scores.items() if score >= 85]
        if high_scores:
            lessons.append({
                "lesson": f"Strong performance in {', '.join(high_scores)}",
                "application": "Document and replicate these practices"
            })
        
        # Lessons from low scores
        low_scores = [cat for cat, score in scores.items() if score < 65]
        if low_scores:
            lessons.append({
                "lesson": f"Improvement needed in {', '.join(low_scores)}",
                "application": "Develop targeted training and process improvements"
            })
        
        # General lessons
        lessons.append({
            "lesson": "Documented incident response enables continuous improvement",
            "application": "Maintain comprehensive records for all incidents"
        })
        
        return lessons
    
    def _generate_detailed_analysis(self, report: Dict[str, Any],
                                   plan: Dict[str, Any],
                                   scores: Dict[str, float]) -> Dict[str, Any]:
        """Generate detailed analysis"""
        return {
            "incident_characteristics": {
                "type": report.get("incident_type", "Unknown"),
                "severity": report.get("severity", "Unknown"),
                "complexity": self._assess_complexity(report, plan)
            },
            "response_quality": {
                "immediate_response": "Strong" if scores.get("timeliness", 0) >= 75 else "Needs improvement",
                "documentation": "Complete" if scores.get("completeness", 0) >= 75 else "Incomplete",
                "policy_adherence": "Compliant" if scores.get("policy_compliance", 0) >= 75 else "Non-compliant"
            },
            "resource_utilization": {
                "personnel": len(plan.get("stakeholders", [])),
                "tools": len(plan.get("resources_needed", [])),
                "efficiency": "Optimal" if scores.get("resource_allocation", 0) >= 75 else "Suboptimal"
            }
        }
    
    def _assess_complexity(self, report: Dict[str, Any], plan: Dict[str, Any]) -> str:
        """Assess incident complexity"""
        factors = 0
        
        if report.get("severity") in ["high", "critical"]:
            factors += 2
        if len(plan.get("stakeholders", [])) > 5:
            factors += 1
        if len(report.get("involved_parties", [])) > 2:
            factors += 1
        
        if factors >= 3:
            return "High"
        elif factors >= 2:
            return "Medium"
        else:
            return "Low"
    
    def _create_improvement_plan(self, weaknesses: List[Dict[str, str]], 
                                recommendations: List[Dict[str, str]]) -> Dict[str, Any]:
        """Create improvement plan"""
        return {
            "immediate_actions": [
                r["recommendation"] for r in recommendations if r.get("priority") == "high"
            ],
            "short_term_actions": [
                r["recommendation"] for r in recommendations if r.get("priority") == "medium"
            ],
            "long_term_actions": [
                "Establish continuous improvement program",
                "Regular review of incident response effectiveness"
            ],
            "success_metrics": [
                "Increase overall score to above 85",
                "Reduce weaknesses to zero",
                "Achieve full policy compliance"
            ]
        }
    
    def _create_summary(self, score: float, rating: str, 
                       strengths_count: int, weaknesses_count: int) -> str:
        """Create evaluation summary"""
        return (
            f"Overall incident response rated as '{rating}' with a score of {score:.1f}/100. "
            f"Identified {strengths_count} area(s) of strength and {weaknesses_count} area(s) for improvement. "
            f"{'Response meets institutional standards.' if score >= 70 else 'Response requires improvement to meet standards.'}"
        )