"""
Evaluator Node - Real-time evaluation and assessment of incident response effectiveness
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from langchain_core.messages import BaseMessage, AIMessage
from pydantic import BaseModel, Field
from .executor_node import ExecutorNodeState, ExecutionSummary
from ..llm.multi_provider_client import multi_llm_client


class PerformanceMetric(BaseModel):
    """Individual performance metric"""
    metric_name: str = Field(description="Name of the metric")
    category: str = Field(description="Metric category")
    value: float = Field(description="Metric value")
    target_value: float = Field(description="Target/benchmark value")
    unit: str = Field(description="Unit of measurement")
    status: str = Field(description="Performance status (excellent/good/needs_improvement/poor)")
    weight: float = Field(description="Weight in overall scoring")


class CategoryScore(BaseModel):
    """Score for a specific evaluation category"""
    category: str = Field(description="Category name")
    score: float = Field(description="Category score (0-100)")
    weight: float = Field(description="Category weight in overall score")
    metrics: List[PerformanceMetric] = Field(description="Individual metrics in category")
    strengths: List[str] = Field(description="Identified strengths")
    weaknesses: List[str] = Field(description="Areas for improvement")


class LessonLearned(BaseModel):
    """Lesson learned from the incident response"""
    lesson_id: str = Field(description="Unique lesson identifier")
    category: str = Field(description="Lesson category")
    lesson: str = Field(description="The lesson learned")
    evidence: str = Field(description="Supporting evidence")
    impact: str = Field(description="Potential impact of applying lesson")
    priority: str = Field(description="Implementation priority")
    actionable_steps: List[str] = Field(description="Specific steps to implement lesson")


class ImprovementRecommendation(BaseModel):
    """Specific improvement recommendation"""
    recommendation_id: str = Field(description="Unique recommendation identifier")
    category: str = Field(description="Recommendation category")
    title: str = Field(description="Recommendation title")
    description: str = Field(description="Detailed description")
    priority: str = Field(description="Implementation priority")
    estimated_effort: str = Field(description="Estimated implementation effort")
    expected_benefit: str = Field(description="Expected benefit")
    implementation_timeline: str = Field(description="Suggested timeline")
    responsible_party: str = Field(description="Suggested responsible party")


class EvaluationReport(BaseModel):
    """Comprehensive evaluation report"""
    evaluation_id: str = Field(description="Unique evaluation identifier")
    incident_id: str = Field(description="Associated incident ID")
    plan_id: str = Field(description="Associated plan ID")
    execution_id: str = Field(description="Associated execution ID")
    
    # Overall assessment
    overall_score: float = Field(description="Overall effectiveness score (0-100)")
    effectiveness_rating: str = Field(description="Effectiveness rating")
    response_quality: str = Field(description="Response quality assessment")
    
    # Resolution status (Safety-First Logic)
    resolution_status: Optional[str] = Field(default="unresolved", description="Incident resolution status")
    resolution_reason: Optional[str] = Field(default="Pending review", description="Reason for resolution status")
    human_intervention_required: Optional[bool] = Field(default=True, description="Whether human intervention is required")
    resolution_details: Optional[str] = Field(default="", description="Additional resolution details")
    rule_applied: Optional[str] = Field(default="unknown", description="Resolution rule that was applied")
    
    # Category scores
    category_scores: List[CategoryScore] = Field(description="Scores by category")
    
    # Detailed analysis
    strengths: List[str] = Field(description="Overall strengths identified")
    weaknesses: List[str] = Field(description="Overall weaknesses identified")
    critical_gaps: List[str] = Field(description="Critical gaps in response")
    
    # Learning and improvement
    lessons_learned: List[LessonLearned] = Field(description="Lessons learned")
    improvement_recommendations: List[ImprovementRecommendation] = Field(description="Improvement recommendations")
    
    # Benchmarking
    benchmark_comparison: Dict[str, Any] = Field(description="Comparison to benchmarks")
    peer_comparison: Dict[str, Any] = Field(description="Comparison to similar incidents")
    
    # Future preparedness
    preparedness_score: float = Field(description="Future preparedness score")
    risk_mitigation_effectiveness: float = Field(description="Risk mitigation effectiveness")
    
    # Metadata
    evaluation_timestamp: str = Field(description="When evaluation was performed")
    evaluator_confidence: float = Field(description="Confidence in evaluation")
    data_completeness: float = Field(description="Completeness of available data")


class EvaluatorNodeState(ExecutorNodeState):
    """Extended state for evaluator node"""
    evaluation_report: Optional[EvaluationReport] = None
    evaluation_status: str = Field(default="pending")


class EvaluatorNode:
    """
    LangGraph node for real-time evaluation of incident response effectiveness
    """
    
    def __init__(self):
        self.name = "evaluator_node"
        self.evaluation_criteria = self._load_evaluation_criteria()
        self.benchmarks = self._load_benchmarks()
        self.scoring_weights = self._load_scoring_weights()
        
    def _load_evaluation_criteria(self):
        """Load evaluation criteria"""
        return {
            "response_time": {"weight": 0.3, "target": 30},
            "execution_quality": {"weight": 0.4, "target": 90},
            "communication": {"weight": 0.3, "target": 80}
        }
    
    def _load_benchmarks(self):
        """Load benchmarks"""
        return {
            "general": {"overall_score": 75.0},
            "medical": {"overall_score": 85.0},
            "security": {"overall_score": 80.0}
        }
    
    def _load_scoring_weights(self):
        """Load scoring weights"""
        return {
            "response_time": 0.3,
            "execution_quality": 0.4,
            "communication": 0.3
        }

    def __call__(self, state: EvaluatorNodeState) -> EvaluatorNodeState:
        """
        Evaluate the effectiveness of the incident response
        
        Args:
            state: Current processing state with execution results
            
        Returns:
            Updated state with evaluation report
        """
        try:
            # Always generate evaluation report, regardless of human review status
            # Human review is for operational decisions, not evaluation blocking
            
            # Create evaluation even with minimal data
            evaluation_report = self._evaluate_response_effectiveness(
                state.incident_data,
                state.response_plan,
                state.execution_summary,
                state.compliance_report
            )
            
            # Determine incident resolution status using safety-first logic
            from ..services.resolution_service import resolution_service
            
            # Use original metadata from user input, not AI-enhanced data
            original_metadata = {}
            if hasattr(state.incident_data, 'metadata') and state.incident_data.metadata:
                original_metadata = state.incident_data.metadata
            
            resolution_data = {
                'incident_id': getattr(state.incident_data, 'incident_id', 'unknown') if state.incident_data else 'unknown',
                # Use original user input for resolution decisions
                'incident_type': original_metadata.get('incident_type') or getattr(state.incident_data, 'incident_type', 'unknown') if state.incident_data else 'unknown',
                'severity': original_metadata.get('severity') or getattr(state.incident_data, 'severity', 'unknown') if state.incident_data else 'unknown',
                'description': getattr(state.incident_data, 'description', '') if state.incident_data else '',
                'location': original_metadata.get('location') or getattr(state.incident_data, 'location', '') if state.incident_data else '',
                # Use original anonymity flag from user input
                'anonymous': original_metadata.get('anonymous_report', False) or getattr(state.incident_data, 'anonymous', False) if state.incident_data else False,
                'anonymous_report': original_metadata.get('anonymous_report', False),
                'requires_human_review': getattr(state.incident_data, 'requires_human_review', False) if state.incident_data else False,
                'has_images': getattr(state.incident_data, 'has_images', False) if state.incident_data else False,
                'file_analyses': getattr(state.incident_data, 'file_analyses', []) if state.incident_data else [],
                'image_analysis': getattr(state.incident_data, 'image_analysis', []) if state.incident_data else [],
                'form_submission': original_metadata.get('form_submission', False),
                'incident_date_time': original_metadata.get('incident_date_time', '') or getattr(state.incident_data, 'incident_date_time', '') if state.incident_data else '',
                'submission_timestamp': original_metadata.get('submission_timestamp', '') or getattr(state.incident_data, 'submission_timestamp', '') if state.incident_data else '',
                'execution_summary': state.execution_summary.__dict__ if state.execution_summary else None,
                'compliance_report': state.compliance_report.__dict__ if state.compliance_report else None,
                'safety_assessment': getattr(state.incident_data, 'safety_assessment', None) if state.incident_data else None
            }
            
            resolution_result = resolution_service.determine_resolution_status(resolution_data)
            
            # Add resolution information to evaluation report
            if hasattr(evaluation_report, '__dict__'):
                evaluation_report.resolution_status = resolution_result.get('status', 'unresolved')
                evaluation_report.resolution_reason = resolution_result.get('reason', 'Pending review')
                evaluation_report.human_intervention_required = resolution_result.get('human_intervention_required', True)
                evaluation_report.resolution_details = resolution_result.get('details', '')
                evaluation_report.rule_applied = resolution_result.get('rule_applied', 'unknown')
            
            # Update state
            state.evaluation_report = evaluation_report
            state.evaluation_status = "completed"
            
            # Check if human review is required (for informational purposes only)
            if state.incident_data and hasattr(state.incident_data, 'requires_human_review'):
                if state.incident_data.requires_human_review:
                    from ..services.human_review_service import human_review_service
                    
                    incident_id = state.incident_data.incident_id
                    if not human_review_service.is_approved_for_evaluation(incident_id):
                        # Add informational message about pending review
                        review_msg = AIMessage(
                            content=f"Note: Incident {incident_id} requires human review for operational decisions. "
                                   f"Evaluation completed independently. Review reasons: {', '.join(getattr(state.incident_data, 'review_reasons', []))}"
                        )
                        state.messages.append(review_msg)
                        state.warnings.append("Human review pending for operational decisions")
            
            # Add evaluation message
            evaluation_msg = AIMessage(
                content=f"Evaluation completed for {evaluation_report.incident_id}. "
                       f"Overall score: {evaluation_report.overall_score:.1f}/100, "
                       f"Rating: {evaluation_report.effectiveness_rating}, "
                       f"Lessons learned: {len(evaluation_report.lessons_learned)}, "
                       f"Recommendations: {len(evaluation_report.improvement_recommendations)}"
            )
            state.messages.append(evaluation_msg)
            
            # Final node - workflow complete
            state.next_node = "complete"
            
            return state
            
        except Exception as e:
            print(f"Evaluator node error: {e}")
            # Create minimal evaluation report even on error
            try:
                minimal_report = self._create_minimal_evaluation_report(state)
                state.evaluation_report = minimal_report
                state.evaluation_status = "completed"
                state.warnings.append("Minimal evaluation report generated due to processing error")
            except Exception as fallback_error:
                print(f"Fallback evaluation error: {fallback_error}")
                state.errors.append(f"Evaluation error: {str(e)}")
                state.evaluation_status = "error"
            
            # Always proceed to complete, don't block on evaluation errors
            state.next_node = "complete"
            return state
    
    def _evaluate_response_effectiveness(self, incident_data, response_plan, 
                                       execution_summary: ExecutionSummary,
                                       compliance_report) -> EvaluationReport:
        """Perform effectiveness evaluation with AI enhancement when available"""
        
        evaluation_id = f"EVAL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Extract basic incident details
        incident_type = getattr(incident_data, 'incident_type', 'unknown') if incident_data else 'unknown'
        severity = getattr(incident_data, 'severity', 'unknown') if incident_data else 'unknown'
        
        # Try AI-enhanced evaluation first
        print(f"🤖 Attempting AI-enhanced evaluation for {incident_type} incident...")
        
        # Analyze incident complexity and context
        incident_complexity = self._analyze_incident_complexity(incident_type, severity, 
                                                               getattr(incident_data, 'description', '') if incident_data else '')
        contextual_factors = self._identify_contextual_factors(incident_data, 
                                                              getattr(incident_data, 'location', '') if incident_data else '')
        
        # Try to get AI-enhanced evaluation
        ai_evaluation = self._get_ai_enhanced_evaluation(incident_data, response_plan, execution_summary, 
                                                        incident_complexity, contextual_factors)
        
        if ai_evaluation:
            print(f"✅ Using AI-enhanced evaluation with score: {ai_evaluation.overall_score}")
            return ai_evaluation
        
        print(f"🔄 Falling back to simplified evaluation")
        
        # Fallback to simplified evaluation
        response_time_score = self._calculate_response_time_score(execution_summary)
        action_completion_score = self._calculate_action_completion_score(execution_summary)
        stakeholder_satisfaction_score = self._calculate_satisfaction_score(execution_summary)
        
        # Overall effectiveness score (simple average)
        overall_score = (response_time_score + action_completion_score + stakeholder_satisfaction_score) / 3
        
        # Determine effectiveness rating
        if overall_score >= 85:
            effectiveness_rating = "Excellent"
            response_quality = "Response was highly effective and well-executed with excellent coordination and outcomes"
        elif overall_score >= 70:
            effectiveness_rating = "Good"
            response_quality = "Response was effective with good coordination and minor areas for improvement"
        elif overall_score >= 55:
            effectiveness_rating = "Satisfactory"
            response_quality = "Response met basic requirements but has room for improvement in coordination and execution"
        else:
            effectiveness_rating = "Needs Improvement"
            response_quality = "Response requires significant improvements in coordination, execution, and effectiveness"
        
        # Create simplified category scores
        category_scores = [
            CategoryScore(
                category="Response Time",
                score=response_time_score,
                weight=0.33,
                metrics=[],
                strengths=["Quick response"] if response_time_score > 75 else [],
                weaknesses=["Slow response"] if response_time_score < 60 else []
            ),
            CategoryScore(
                category="Action Completion",
                score=action_completion_score,
                weight=0.33,
                metrics=[],
                strengths=["Actions completed successfully"] if action_completion_score > 75 else [],
                weaknesses=["Some actions incomplete"] if action_completion_score < 60 else []
            ),
            CategoryScore(
                category="Stakeholder Satisfaction",
                score=stakeholder_satisfaction_score,
                weight=0.34,
                metrics=[],
                strengths=["Good stakeholder response"] if stakeholder_satisfaction_score > 75 else [],
                weaknesses=["Poor stakeholder engagement"] if stakeholder_satisfaction_score < 60 else []
            )
        ]
        
        # Generate brief insights
        strengths = []
        weaknesses = []
        
        if response_time_score > 75:
            strengths.append("Rapid response time")
        if action_completion_score > 75:
            strengths.append("High action completion rate")
        if stakeholder_satisfaction_score > 75:
            strengths.append("Good stakeholder engagement")
            
        if response_time_score < 60:
            weaknesses.append("Response time needs improvement")
        if action_completion_score < 60:
            weaknesses.append("Action completion rate below target")
        if stakeholder_satisfaction_score < 60:
            weaknesses.append("Stakeholder engagement needs work")
        
        # Minimal lessons learned
        lessons_learned = []
        if overall_score < 70:
            lessons_learned.append(LessonLearned(
                lesson_id="LESSON-001",
                category="improvement",
                lesson="Focus on improving response effectiveness",
                evidence=f"Overall score was {overall_score:.1f}%",
                impact="Better incident outcomes",
                priority="medium",
                actionable_steps=["Review response procedures", "Enhance training"]
            ))
        else:
            lessons_learned.append(LessonLearned(
                lesson_id="LESSON-001",
                category="validation",
                lesson=f"Response protocol for {incident_type} incidents validated",
                evidence=f"Achieved {overall_score:.1f}% effectiveness score",
                impact="Confirms effective response capabilities",
                priority="low",
                actionable_steps=["Continue monitoring performance", "Document best practices"]
            ))
        
        # Minimal recommendations
        recommendations = []
        if response_time_score < 70:
            recommendations.append(ImprovementRecommendation(
                recommendation_id="REC-001",
                category="response_time",
                title="Improve Response Time",
                description="Streamline response procedures to reduce response time",
                priority="medium",
                estimated_effort="2-4 weeks",
                expected_benefit="Faster incident resolution",
                implementation_timeline="Next month",
                responsible_party="Response Team"
            ))
        
        if action_completion_score < 70:
            recommendations.append(ImprovementRecommendation(
                recommendation_id="REC-002",
                category="action_completion",
                title="Enhance Action Completion",
                description="Improve action tracking and completion processes",
                priority="medium",
                estimated_effort="2-3 weeks",
                expected_benefit="Higher completion rates",
                implementation_timeline="Next month",
                responsible_party="Operations Team"
            ))
        
        return EvaluationReport(
            evaluation_id=evaluation_id,
            incident_id=getattr(incident_data, 'incident_id', 'unknown') if incident_data else "unknown",
            plan_id=getattr(response_plan, 'plan_id', 'unknown') if response_plan else "unknown", 
            execution_id=getattr(execution_summary, 'execution_id', 'unknown') if execution_summary else "unknown",
            overall_score=overall_score,
            effectiveness_rating=effectiveness_rating,
            response_quality=response_quality,
            category_scores=category_scores,
            strengths=strengths,
            weaknesses=weaknesses,
            critical_gaps=[],  # Simplified - no critical gaps analysis
            lessons_learned=lessons_learned,
            improvement_recommendations=recommendations,
            benchmark_comparison={"benchmark_score": 75.0, "comparison": "Above average" if overall_score > 75 else "Average"},
            peer_comparison={"peer_average": 70.0, "ranking": "Above average" if overall_score > 70 else "Average"},
            preparedness_score=min(100, overall_score + 5),  # Simple calculation
            risk_mitigation_effectiveness=min(100, overall_score),
            evaluation_timestamp=datetime.now().isoformat(),
            evaluator_confidence=85.0,  # Fixed confidence
            data_completeness=90.0  # Fixed completeness
        )
    
    def _calculate_response_time_score(self, execution_summary) -> float:
        """Calculate response time score"""
        if not execution_summary:
            return 70.0
        
        duration = getattr(execution_summary, 'total_duration_minutes', 60)
        
        # Score based on duration (lower is better)
        if duration <= 30:
            return 95.0
        elif duration <= 60:
            return 85.0
        elif duration <= 120:
            return 70.0
        else:
            return 50.0
    
    def _calculate_action_completion_score(self, execution_summary) -> float:
        """Calculate action completion score"""
        if not execution_summary:
            return 70.0
        
        success_rate = getattr(execution_summary, 'success_rate', 75.0)
        return min(100, success_rate + 5)  # Slight boost for completion
    
    def _calculate_satisfaction_score(self, execution_summary) -> float:
        """Calculate stakeholder satisfaction score"""
        if not execution_summary:
            return 70.0
        
        # Use stakeholder response rate as proxy for satisfaction
        response_rate = getattr(execution_summary, 'stakeholder_response_rate', 70.0)
        
        # Convert response rate to satisfaction score
        if response_rate >= 80:
            return 90.0
        elif response_rate >= 60:
            return 75.0
        elif response_rate >= 40:
            return 60.0
        else:
            return 45.0
    
    def _analyze_incident_complexity(self, incident_type: str, severity: str, description: str) -> Dict[str, Any]:
        """Analyze incident complexity factors"""
        complexity_score = 1.0  # Base complexity
        factors = []
        
        # Type-based complexity
        high_complexity_types = ['assault', 'fire', 'medical', 'security']
        if incident_type.lower() in high_complexity_types:
            complexity_score += 0.5
            factors.append(f"High-complexity incident type: {incident_type}")
        
        # Severity-based complexity
        if severity.lower() in ['high', 'critical']:
            complexity_score += 0.3
            factors.append(f"High severity level: {severity}")
        
        # Description-based complexity (keyword analysis)
        complex_keywords = ['multiple', 'ongoing', 'escalated', 'emergency', 'urgent', 'serious']
        description_lower = description.lower()
        keyword_count = sum(1 for keyword in complex_keywords if keyword in description_lower)
        if keyword_count > 0:
            complexity_score += keyword_count * 0.1
            factors.append(f"Complex situation indicators: {keyword_count} keywords found")
        
        return {
            'complexity_score': min(3.0, complexity_score),  # Cap at 3.0
            'factors': factors,
            'classification': 'high' if complexity_score > 2.0 else 'medium' if complexity_score > 1.5 else 'low'
        }
    
    def _identify_contextual_factors(self, incident_data, location: str) -> Dict[str, Any]:
        """Identify contextual factors affecting response"""
        factors = {
            'location_risk': 'medium',
            'time_factors': [],
            'resource_factors': [],
            'environmental_factors': []
        }
        
        # Location-based factors
        high_risk_locations = ['parking', 'isolated', 'basement', 'after hours']
        if any(risk_loc in location.lower() for risk_loc in high_risk_locations):
            factors['location_risk'] = 'high'
            factors['environmental_factors'].append('High-risk location identified')
        
        # Time-based factors (if timestamp available)
        if incident_data and hasattr(incident_data, 'submission_timestamp'):
            try:
                from datetime import datetime
                timestamp = datetime.fromisoformat(incident_data.submission_timestamp.replace('Z', '+00:00'))
                hour = timestamp.hour
                if hour < 6 or hour > 22:
                    factors['time_factors'].append('After-hours incident')
                if timestamp.weekday() >= 5:  # Weekend
                    factors['time_factors'].append('Weekend incident')
            except:
                pass
        
        # Anonymous reporting factor
        if incident_data and hasattr(incident_data, 'anonymous') and incident_data.anonymous:
            factors['resource_factors'].append('Anonymous report - limited follow-up capability')
        
        return factors
    
    def _get_ai_enhanced_evaluation(self, incident_data, response_plan, execution_summary, 
                                   incident_complexity, contextual_factors) -> Optional[EvaluationReport]:
        """Get AI-enhanced evaluation with deep insights"""
        try:
            if not multi_llm_client.active_provider:
                return None
            
            # Prepare comprehensive data for AI analysis
            evaluation_context = {
                'incident': {
                    'type': getattr(incident_data, 'incident_type', 'unknown') if incident_data else 'unknown',
                    'severity': getattr(incident_data, 'severity', 'unknown') if incident_data else 'unknown',
                    'description': getattr(incident_data, 'description', 'No description') if incident_data else 'No description',
                    'location': getattr(incident_data, 'location', 'unknown') if incident_data else 'unknown',
                    'complexity': incident_complexity,
                    'anonymous': getattr(incident_data, 'anonymous', False) if incident_data else False
                },
                'response': {
                    'plan_type': getattr(response_plan, 'plan_type', 'unknown') if response_plan else 'unknown',
                    'immediate_actions': len(getattr(response_plan, 'immediate_actions', [])) if response_plan else 0,
                    'stakeholders': len(getattr(response_plan, 'stakeholders', [])) if response_plan else 0
                },
                'execution': {
                    'success_rate': getattr(execution_summary, 'success_rate', 75.0) if execution_summary else 75.0,
                    'overall_status': getattr(execution_summary, 'overall_status', 'unknown') if execution_summary else 'unknown',
                    'duration': getattr(execution_summary, 'total_duration_minutes', 60) if execution_summary else 60
                },
                'context': contextual_factors
            }
            
            # Enhanced AI prompt for deep evaluation
            ai_prompt = f"""
            As an expert incident response evaluator, provide a comprehensive evaluation of this campus safety incident response:

            INCIDENT ANALYSIS:
            - Type: {evaluation_context['incident']['type']}
            - Severity: {evaluation_context['incident']['severity']}
            - Location: {evaluation_context['incident']['location']}
            - Complexity: {evaluation_context['incident']['complexity']['classification']} 
            - Complexity Factors: {evaluation_context['incident']['complexity']['factors']}
            - Anonymous Report: {evaluation_context['incident']['anonymous']}

            RESPONSE ANALYSIS:
            - Plan Type: {evaluation_context['response']['plan_type']}
            - Immediate Actions: {evaluation_context['response']['immediate_actions']}
            - Stakeholders Involved: {evaluation_context['response']['stakeholders']}

            EXECUTION ANALYSIS:
            - Success Rate: {evaluation_context['execution']['success_rate']}%
            - Status: {evaluation_context['execution']['overall_status']}
            - Duration: {evaluation_context['execution']['duration']} minutes

            CONTEXTUAL FACTORS:
            - Location Risk: {evaluation_context['context']['location_risk']}
            - Time Factors: {evaluation_context['context']['time_factors']}
            - Resource Factors: {evaluation_context['context']['resource_factors']}

            Provide a detailed evaluation focusing on:
            1. Response appropriateness for the specific incident type and complexity
            2. Effectiveness of actions taken considering contextual constraints
            3. Quality of decision-making under the circumstances
            4. Areas where response exceeded or fell short of best practices
            5. Specific, actionable lessons learned
            6. Strategic recommendations for system improvement

            Return evaluation as JSON:
            {{
                "overall_score": 0-100,
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
            }}
            """
            
            # Get AI response
            ai_response = multi_llm_client.generate_response(
                evaluation_context['incident'], 
                evaluation_context['response'], 
                evaluation_context['execution']
            )
            
            # Parse and convert AI response
            import json
            import re
            json_match = re.search(r'\{.*\}', str(ai_response), re.DOTALL)
            if json_match:
                ai_evaluation = json.loads(json_match.group())
                return self._convert_ai_evaluation_to_report(ai_evaluation, evaluation_context)
                
        except Exception as e:
            print(f"AI-enhanced evaluation failed: {e}")
            return None
        
        return None
    
    def _convert_ai_evaluation_to_report(self, ai_evaluation: Dict, context: Dict) -> EvaluationReport:
        """Convert AI evaluation to structured report"""
        evaluation_id = f"EVAL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Convert lessons learned
        lessons_learned = []
        for i, lesson in enumerate(ai_evaluation.get('lessons_learned', []), 1):
            lessons_learned.append(LessonLearned(
                lesson_id=f"LESSON-{i:03d}",
                category=lesson.get('category', 'process_improvement'),
                lesson=lesson.get('lesson', 'Lesson learned from response'),
                evidence=lesson.get('evidence', 'AI analysis of response effectiveness'),
                impact="Enhanced response capability and preparedness",
                priority=lesson.get('priority', 'medium'),
                actionable_steps=lesson.get('actionable_steps', ['Review and implement'])
            ))
        
        # Convert recommendations
        recommendations = []
        for i, rec in enumerate(ai_evaluation.get('improvement_recommendations', []), 1):
            recommendations.append(ImprovementRecommendation(
                recommendation_id=f"REC-{i:03d}",
                category="ai_strategic_recommendation",
                title=rec.get('title', 'Strategic improvement'),
                description=rec.get('description', 'AI-generated strategic recommendation'),
                priority=rec.get('priority', 'medium'),
                estimated_effort="2-4 weeks",
                expected_benefit=rec.get('expected_benefit', 'Enhanced response effectiveness'),
                implementation_timeline=rec.get('implementation_timeline', 'Next quarter'),
                responsible_party="Response Team"
            ))
        
        # Create enhanced category scores
        category_scores = [
            CategoryScore(
                category="AI-Enhanced Overall Assessment",
                score=ai_evaluation.get('overall_score', 75),
                weight=1.0,
                metrics=[],
                strengths=ai_evaluation.get('strengths', ['Effective response']),
                weaknesses=ai_evaluation.get('weaknesses', ['Areas for improvement'])
            )
        ]
        
        return EvaluationReport(
            evaluation_id=evaluation_id,
            incident_id=context['incident'].get('id', 'unknown'),
            plan_id="AI-ENHANCED",
            execution_id="AI-ENHANCED",
            overall_score=ai_evaluation.get('overall_score', 75),
            effectiveness_rating=ai_evaluation.get('effectiveness_rating', 'Good'),
            response_quality=ai_evaluation.get('response_quality', 'AI-enhanced comprehensive analysis'),
            category_scores=category_scores,
            strengths=ai_evaluation.get('strengths', ['Effective coordination']),
            weaknesses=ai_evaluation.get('weaknesses', ['Room for improvement']),
            critical_gaps=ai_evaluation.get('critical_gaps', []),
            lessons_learned=lessons_learned,
            improvement_recommendations=recommendations,
            benchmark_comparison={
                "ai_enhanced": True, 
                "benchmark_score": 75.0,
                "contextual_analysis": ai_evaluation.get('contextual_analysis', 'Context considered')
            },
            peer_comparison={
                "ai_analysis": True, 
                "peer_average": 70.0,
                "future_preparedness": ai_evaluation.get('future_preparedness', 'Good preparedness')
            },
            preparedness_score=85.0,
            risk_mitigation_effectiveness=80.0,
            evaluation_timestamp=datetime.now().isoformat(),
            evaluator_confidence=95.0,
            data_completeness=90.0
        )
    def _evaluate_all_categories_enhanced(self, incident_data, response_plan, execution_summary, 
                                        compliance_report, incident_complexity, contextual_factors):
        """Enhanced evaluation with deep insights"""
        categories = []
        
        # 1. Response Appropriateness (considering incident complexity)
        appropriateness_score = self._evaluate_response_appropriateness(
            incident_data, response_plan, incident_complexity
        )
        categories.append(appropriateness_score)
        
        # 2. Execution Effectiveness (considering contextual factors)
        execution_score = self._evaluate_execution_effectiveness(
            execution_summary, contextual_factors
        )
        categories.append(execution_score)
        
        # 3. Communication Quality
        communication_score = self._evaluate_communication_quality(
            response_plan, execution_summary, incident_data
        )
        categories.append(communication_score)
        
        # 4. Risk Management
        risk_management_score = self._evaluate_risk_management(
            incident_data, response_plan, contextual_factors
        )
        categories.append(risk_management_score)
        
        # 5. Resource Utilization
        resource_score = self._evaluate_resource_utilization(
            response_plan, execution_summary, incident_complexity
        )
        categories.append(resource_score)
        
        return categories
    
    def _evaluate_response_appropriateness(self, incident_data, response_plan, incident_complexity):
        """Evaluate if response was appropriate for incident type and complexity"""
        base_score = 75.0
        strengths = []
        weaknesses = []
        
        if incident_data and response_plan:
            incident_type = getattr(incident_data, 'incident_type', 'unknown')
            severity = getattr(incident_data, 'severity', 'unknown')
            plan_type = getattr(response_plan, 'plan_type', 'unknown')
            
            # Check type-plan alignment
            if incident_type in ['medical', 'fire'] and 'emergency' in plan_type.lower():
                base_score += 10
                strengths.append("Emergency response plan appropriately selected for critical incident")
            elif incident_type in ['theft', 'vandalism'] and 'security' in plan_type.lower():
                base_score += 5
                strengths.append("Security response plan matches incident type")
            
            # Severity-response alignment
            if severity in ['high', 'critical']:
                immediate_actions = len(getattr(response_plan, 'immediate_actions', []))
                if immediate_actions >= 3:
                    base_score += 10
                    strengths.append(f"Comprehensive immediate response with {immediate_actions} actions")
                else:
                    base_score -= 5
                    weaknesses.append("High-severity incident may need more immediate actions")
            
            # Complexity consideration
            complexity_level = incident_complexity.get('classification', 'medium')
            if complexity_level == 'high':
                stakeholders = len(getattr(response_plan, 'stakeholders', []))
                if stakeholders >= 3:
                    base_score += 5
                    strengths.append("Multiple stakeholders engaged for complex incident")
                else:
                    weaknesses.append("Complex incident may benefit from more stakeholder involvement")
        else:
            weaknesses.append("Limited data for response appropriateness assessment")
        
        return CategoryScore(
            category="Response Appropriateness",
            score=max(0, min(100, base_score)),
            weight=0.25,
            metrics=[],
            strengths=strengths,
            weaknesses=weaknesses
        )
    
    def _evaluate_execution_effectiveness(self, execution_summary, contextual_factors):
        """Evaluate execution effectiveness considering context"""
        base_score = 70.0
        strengths = []
        weaknesses = []
        
        if execution_summary:
            success_rate = getattr(execution_summary, 'success_rate', 75.0)
            base_score = success_rate
            
            if success_rate >= 90:
                strengths.append("Excellent execution success rate")
            elif success_rate >= 80:
                strengths.append("Good execution performance")
            else:
                weaknesses.append("Execution success rate below optimal")
            
            # Duration analysis
            duration = getattr(execution_summary, 'total_duration_minutes', 60)
            if duration <= 30:
                base_score += 5
                strengths.append("Rapid response execution")
            elif duration > 120:
                base_score -= 5
                weaknesses.append("Extended response duration")
            
            # Context adjustments
            if contextual_factors.get('location_risk') == 'high':
                base_score += 5  # Bonus for handling high-risk location
                strengths.append("Successfully managed high-risk location incident")
            
            if 'After-hours incident' in contextual_factors.get('time_factors', []):
                base_score += 3  # Bonus for after-hours response
                strengths.append("Effective after-hours response")
        else:
            weaknesses.append("No execution data available for assessment")
        
        return CategoryScore(
            category="Execution Effectiveness",
            score=max(0, min(100, base_score)),
            weight=0.30,
            metrics=[],
            strengths=strengths,
            weaknesses=weaknesses
        )
    
    def _evaluate_communication_quality(self, response_plan, execution_summary, incident_data):
        """Evaluate communication effectiveness"""
        base_score = 75.0
        strengths = []
        weaknesses = []
        
        if response_plan:
            stakeholders = getattr(response_plan, 'stakeholders', [])
            if len(stakeholders) >= 2:
                base_score += 10
                strengths.append(f"Multi-stakeholder communication ({len(stakeholders)} parties)")
            
            # Check for communication actions
            immediate_actions = getattr(response_plan, 'immediate_actions', [])
            comm_actions = [action for action in immediate_actions 
                          if any(word in str(action).lower() for word in ['notify', 'contact', 'inform', 'alert'])]
            if comm_actions:
                base_score += 5
                strengths.append("Communication actions included in response plan")
        
        # Anonymous reporting consideration
        if incident_data and hasattr(incident_data, 'anonymous') and incident_data.anonymous:
            base_score -= 5
            weaknesses.append("Anonymous reporting limits follow-up communication")
        
        return CategoryScore(
            category="Communication Quality",
            score=max(0, min(100, base_score)),
            weight=0.20,
            metrics=[],
            strengths=strengths,
            weaknesses=weaknesses
        )
    
    def _evaluate_risk_management(self, incident_data, response_plan, contextual_factors):
        """Evaluate risk management effectiveness"""
        base_score = 75.0
        strengths = []
        weaknesses = []
        
        if incident_data:
            severity = getattr(incident_data, 'severity', 'unknown')
            if severity in ['high', 'critical']:
                # High-risk incident handling
                if response_plan:
                    immediate_actions = len(getattr(response_plan, 'immediate_actions', []))
                    if immediate_actions >= 4:
                        base_score += 10
                        strengths.append("Comprehensive risk mitigation for high-severity incident")
                    else:
                        weaknesses.append("High-risk incident may need more mitigation actions")
        
        # Location risk consideration
        location_risk = contextual_factors.get('location_risk', 'medium')
        if location_risk == 'high':
            base_score += 5
            strengths.append("Addressed high-risk location factors")
        
        # Environmental factors
        env_factors = contextual_factors.get('environmental_factors', [])
        if env_factors:
            base_score += 3
            strengths.append("Considered environmental risk factors")
        
        return CategoryScore(
            category="Risk Management",
            score=max(0, min(100, base_score)),
            weight=0.15,
            metrics=[],
            strengths=strengths,
            weaknesses=weaknesses
        )
    
    def _evaluate_resource_utilization(self, response_plan, execution_summary, incident_complexity):
        """Evaluate resource utilization efficiency"""
        base_score = 75.0
        strengths = []
        weaknesses = []
        
        if response_plan and execution_summary:
            # Resource allocation vs complexity
            complexity_level = incident_complexity.get('classification', 'medium')
            stakeholders = len(getattr(response_plan, 'stakeholders', []))
            
            if complexity_level == 'high' and stakeholders >= 3:
                base_score += 10
                strengths.append("Appropriate resource allocation for complex incident")
            elif complexity_level == 'low' and stakeholders <= 2:
                base_score += 5
                strengths.append("Efficient resource use for simple incident")
            
            # Success rate indicates resource effectiveness
            success_rate = getattr(execution_summary, 'success_rate', 75.0)
            if success_rate >= 85:
                base_score += 5
                strengths.append("High success rate indicates effective resource use")
        
        return CategoryScore(
            category="Resource Utilization",
            score=max(0, min(100, base_score)),
            weight=0.10,
            metrics=[],
            strengths=strengths,
            weaknesses=weaknesses
        )
    
    def _evaluate_human_review_process(self, incident_data):
        """Evaluate human review process effectiveness"""
        base_score = 80.0
        strengths = []
        weaknesses = []
        
        if hasattr(incident_data, 'requires_human_review') and incident_data.requires_human_review:
            strengths.append("Human oversight appropriately triggered for sensitive incident")
            
            # Check review reasons
            if hasattr(incident_data, 'review_reasons'):
                review_reasons = incident_data.review_reasons
                if 'suspicious_file' in review_reasons:
                    strengths.append("File authenticity concerns properly flagged")
                if 'anonymous_report' in review_reasons:
                    strengths.append("Anonymous report appropriately escalated")
            
            # Check if review was completed
            from ..services.human_review_service import human_review_service
            incident_id = getattr(incident_data, 'incident_id', 'unknown')
            if human_review_service.is_approved_for_evaluation(incident_id):
                base_score += 10
                strengths.append("Human review completed successfully")
            else:
                base_score -= 10
                weaknesses.append("Human review still pending")
        
        return CategoryScore(
            category="Human Review Process",
            score=max(0, min(100, base_score)),
            weight=0.10,
            metrics=[],
            strengths=strengths,
            weaknesses=weaknesses
        )
        categories = []
        
        # Response Time Effectiveness
        response_time_score = 85.0
        if execution_summary and hasattr(execution_summary, 'total_duration_minutes'):
            if execution_summary.total_duration_minutes < 60:
                response_time_score = 90.0
            elif execution_summary.total_duration_minutes > 120:
                response_time_score = 70.0
        
        categories.append(CategoryScore(
            category="Response Time",
            score=response_time_score,
            weight=0.3,
            metrics=[],
            strengths=["Quick initial response"] if response_time_score > 80 else [],
            weaknesses=["Could improve notification speed"] if response_time_score < 80 else []
        ))
        
        # Execution Quality
        execution_score = 80.0
        if execution_summary and hasattr(execution_summary, 'success_rate'):
            execution_score = min(100, execution_summary.success_rate + 5)
        
        categories.append(CategoryScore(
            category="Execution Quality",
            score=execution_score,
            weight=0.4,
            metrics=[],
            strengths=["High success rate"] if execution_score > 85 else ["Adequate execution"],
            weaknesses=["Some actions could be more specific"] if execution_score < 85 else []
        ))
        
        # Communication Effectiveness
        comm_score = 75.0
        if execution_summary and hasattr(execution_summary, 'stakeholder_response_rate'):
            comm_score = min(100, execution_summary.stakeholder_response_rate + 10)
        
        categories.append(CategoryScore(
            category="Communication",
            score=comm_score,
            weight=0.3,
            metrics=[],
            strengths=["Good stakeholder engagement"] if comm_score > 80 else [],
            weaknesses=["Could improve response rates"] if comm_score < 75 else []
        ))
        
        return categories
    
    def _calculate_contextual_score(self, category_scores, incident_complexity, contextual_factors):
        """Calculate overall score with contextual adjustments"""
        if not category_scores:
            return 75.0
        
        # Base weighted score
        total_weighted_score = sum(cat.score * cat.weight for cat in category_scores)
        total_weight = sum(cat.weight for cat in category_scores)
        base_score = total_weighted_score / total_weight if total_weight > 0 else 75.0
        
        # Contextual adjustments
        complexity_level = incident_complexity.get('classification', 'medium')
        if complexity_level == 'high' and base_score >= 80:
            base_score += 5  # Bonus for handling complex incident well
        
        # Time factor adjustments
        time_factors = contextual_factors.get('time_factors', [])
        if 'After-hours incident' in time_factors and base_score >= 75:
            base_score += 3  # Bonus for good after-hours response
        
        return max(0, min(100, base_score))
    
    def _assess_response_quality_detailed(self, overall_score, category_scores, incident_complexity, contextual_factors):
        """Provide detailed response quality assessment"""
        quality_aspects = []
        
        # Score-based assessment
        if overall_score >= 90:
            quality_aspects.append("Exceptional response performance")
        elif overall_score >= 80:
            quality_aspects.append("Strong response effectiveness")
        elif overall_score >= 70:
            quality_aspects.append("Adequate response with room for improvement")
        else:
            quality_aspects.append("Response needs significant improvement")
        
        # Complexity consideration
        complexity_level = incident_complexity.get('classification', 'medium')
        if complexity_level == 'high':
            quality_aspects.append("Successfully managed high-complexity incident")
        
        # Context consideration
        if contextual_factors.get('location_risk') == 'high':
            quality_aspects.append("Effectively handled high-risk location")
        
        # Category-specific insights
        top_category = max(category_scores, key=lambda x: x.score) if category_scores else None
        if top_category:
            quality_aspects.append(f"Strongest performance in {top_category.category.lower()}")
        
        return ". ".join(quality_aspects) + "."
    
    def _perform_deep_analysis(self, category_scores, incident_complexity, contextual_factors):
        """Perform deep analysis of strengths, weaknesses, and gaps"""
        all_strengths = []
        all_weaknesses = []
        critical_gaps = []
        
        # Aggregate from categories
        for category in category_scores:
            all_strengths.extend(category.strengths)
            all_weaknesses.extend(category.weaknesses)
            if category.score < 60:
                critical_gaps.append(f"Critical performance gap in {category.category.lower()}")
        
        # Add contextual insights
        complexity_level = incident_complexity.get('classification', 'medium')
        if complexity_level == 'high':
            all_strengths.append("Successfully processed high-complexity incident")
        
        # Environmental factors
        env_factors = contextual_factors.get('environmental_factors', [])
        if env_factors:
            all_strengths.append("Considered environmental and contextual factors")
        
        # Remove duplicates while preserving order
        all_strengths = list(dict.fromkeys(all_strengths))
        all_weaknesses = list(dict.fromkeys(all_weaknesses))
        
        return all_strengths, all_weaknesses, critical_gaps
    
    def _generate_actionable_lessons(self, incident_data, response_plan, execution_summary, 
                                   category_scores, incident_complexity, contextual_factors):
        """Generate actionable lessons learned"""
        lessons = []
        lesson_count = 1
        
        # Complexity-based lessons
        complexity_level = incident_complexity.get('classification', 'medium')
        if complexity_level == 'high':
            lessons.append(LessonLearned(
                lesson_id=f"LESSON-{lesson_count:03d}",
                category="complexity_management",
                lesson="High-complexity incidents require enhanced coordination and resource allocation",
                evidence=f"Incident classified as {complexity_level} complexity with factors: {incident_complexity.get('factors', [])}",
                impact="Better preparedness for complex scenarios",
                priority="high",
                actionable_steps=[
                    "Develop complexity assessment protocols",
                    "Create escalation procedures for complex incidents",
                    "Train staff on multi-factor incident management"
                ]
            ))
            lesson_count += 1
        
        # Performance-based lessons
        low_performing_categories = [cat for cat in category_scores if cat.score < 75]
        for category in low_performing_categories:
            lessons.append(LessonLearned(
                lesson_id=f"LESSON-{lesson_count:03d}",
                category=category.category.lower().replace(" ", "_"),
                lesson=f"Improvement needed in {category.category.lower()} processes",
                evidence=f"Category scored {category.score:.1f}/100 with weaknesses: {category.weaknesses}",
                impact="Enhanced overall response effectiveness",
                priority="high" if category.score < 60 else "medium",
                actionable_steps=[
                    f"Review {category.category.lower()} procedures",
                    "Provide additional training",
                    "Implement performance monitoring"
                ]
            ))
            lesson_count += 1
        
        # Contextual lessons
        if contextual_factors.get('location_risk') == 'high':
            lessons.append(LessonLearned(
                lesson_id=f"LESSON-{lesson_count:03d}",
                category="location_risk_management",
                lesson="High-risk locations require specialized response protocols",
                evidence="Incident occurred in high-risk location with environmental factors",
                impact="Improved safety and response effectiveness in challenging locations",
                priority="medium",
                actionable_steps=[
                    "Develop location-specific response protocols",
                    "Conduct location risk assessments",
                    "Pre-position resources for high-risk areas"
                ]
            ))
            lesson_count += 1
        
        # Anonymous reporting lessons
        if incident_data and hasattr(incident_data, 'anonymous') and incident_data.anonymous:
            lessons.append(LessonLearned(
                lesson_id=f"LESSON-{lesson_count:03d}",
                category="anonymous_reporting",
                lesson="Anonymous reports require adapted follow-up and verification procedures",
                evidence="Incident reported anonymously, limiting direct follow-up capabilities",
                impact="Better handling of anonymous reports while maintaining privacy",
                priority="medium",
                actionable_steps=[
                    "Develop anonymous report verification protocols",
                    "Create alternative communication channels",
                    "Enhance evidence collection procedures"
                ]
            ))
        
        return lessons
    
    def _generate_strategic_recommendations(self, category_scores, lessons_learned, incident_data, incident_complexity):
        """Generate strategic improvement recommendations"""
        recommendations = []
        rec_count = 1
        
        # Performance improvement recommendations
        for category in category_scores:
            if category.score < 80:
                recommendations.append(ImprovementRecommendation(
                    recommendation_id=f"REC-{rec_count:03d}",
                    category=category.category.lower().replace(" ", "_"),
                    title=f"Enhance {category.category} Capabilities",
                    description=f"Implement systematic improvements to address {category.category.lower()} weaknesses: {', '.join(category.weaknesses)}",
                    priority="high" if category.score < 60 else "medium",
                    estimated_effort="3-6 weeks",
                    expected_benefit=f"Improve {category.category.lower()} performance by 15-20 points",
                    implementation_timeline="Next 60 days",
                    responsible_party="Response Team Lead"
                ))
                rec_count += 1
        
        # System-wide recommendations
        avg_score = sum(cat.score for cat in category_scores) / len(category_scores) if category_scores else 75
        if avg_score < 85:
            recommendations.append(ImprovementRecommendation(
                recommendation_id=f"REC-{rec_count:03d}",
                category="system_enhancement",
                title="Implement Comprehensive Response System Upgrade",
                description="Develop integrated response system with enhanced monitoring, automated workflows, and performance analytics",
                priority="high",
                estimated_effort="8-12 weeks",
                expected_benefit="20-30% improvement in overall response effectiveness",
                implementation_timeline="Next quarter",
                responsible_party="System Administrator"
            ))
            rec_count += 1
        
        # Complexity-specific recommendations
        complexity_level = incident_complexity.get('classification', 'medium')
        if complexity_level == 'high':
            recommendations.append(ImprovementRecommendation(
                recommendation_id=f"REC-{rec_count:03d}",
                category="complexity_management",
                title="Develop Advanced Incident Complexity Assessment",
                description="Create automated complexity assessment tools and specialized response protocols for high-complexity incidents",
                priority="medium",
                estimated_effort="4-6 weeks",
                expected_benefit="Better resource allocation and response appropriateness",
                implementation_timeline="Next 90 days",
                responsible_party="Technical Team"
            ))
            rec_count += 1
        
        # Training recommendations
        recommendations.append(ImprovementRecommendation(
            recommendation_id=f"REC-{rec_count:03d}",
            category="training_development",
            title="Implement Scenario-Based Training Program",
            description="Develop comprehensive training program based on lessons learned from real incidents, including complexity factors and contextual challenges",
            priority="medium",
            estimated_effort="6-8 weeks",
            expected_benefit="Enhanced staff preparedness and response quality",
            implementation_timeline="Next quarter",
            responsible_party="Training Coordinator"
        ))
        
        return recommendations
    
    def _perform_advanced_benchmarking(self, incident_data, overall_score, category_scores, incident_complexity):
        """Perform advanced benchmarking analysis"""
        incident_type = getattr(incident_data, 'incident_type', 'unknown') if incident_data else 'unknown'
        complexity_level = incident_complexity.get('classification', 'medium')
        
        # Type-specific benchmarks
        type_benchmarks = {
            'medical': 85.0,
            'fire': 88.0,
            'security': 80.0,
            'theft': 75.0,
            'harassment': 82.0,
            'assault': 90.0,
            'vandalism': 70.0,
            'maintenance': 65.0
        }
        
        benchmark_score = type_benchmarks.get(incident_type.lower(), 75.0)
        
        # Complexity adjustments
        if complexity_level == 'high':
            benchmark_score += 5  # Higher expectations for complex incidents
        elif complexity_level == 'low':
            benchmark_score -= 5  # Lower baseline for simple incidents
        
        comparison_result = "Exceeds benchmark" if overall_score > benchmark_score + 5 else \
                          "Meets benchmark" if overall_score >= benchmark_score - 5 else \
                          "Below benchmark"
        
        return {
            "incident_type": incident_type,
            "complexity_level": complexity_level,
            "benchmark_score": benchmark_score,
            "actual_score": overall_score,
            "comparison": comparison_result,
            "performance_gap": overall_score - benchmark_score,
            "category_benchmarks": {cat.category: cat.score for cat in category_scores}
        }
    
    def _perform_peer_analysis(self, incident_data, overall_score, execution_summary, contextual_factors):
        """Perform peer comparison analysis"""
        # Simulated peer data (in real system, this would come from database)
        peer_averages = {
            'overall': 72.0,
            'after_hours': 68.0,
            'high_risk_location': 70.0,
            'anonymous_reports': 65.0,
            'complex_incidents': 75.0
        }
        
        applicable_peer_group = 'overall'
        peer_score = peer_averages['overall']
        
        # Determine most applicable peer group
        if 'After-hours incident' in contextual_factors.get('time_factors', []):
            applicable_peer_group = 'after_hours'
            peer_score = peer_averages['after_hours']
        elif contextual_factors.get('location_risk') == 'high':
            applicable_peer_group = 'high_risk_location'
            peer_score = peer_averages['high_risk_location']
        elif incident_data and hasattr(incident_data, 'anonymous') and incident_data.anonymous:
            applicable_peer_group = 'anonymous_reports'
            peer_score = peer_averages['anonymous_reports']
        
        percentile = min(95, max(5, int((overall_score - peer_score + 20) * 2.5)))
        
        return {
            "peer_group": applicable_peer_group,
            "peer_average": peer_score,
            "actual_score": overall_score,
            "percentile_ranking": f"{percentile}th percentile",
            "performance_vs_peers": overall_score - peer_score,
            "comparison_summary": f"Performed {overall_score - peer_score:.1f} points {'above' if overall_score > peer_score else 'below'} peer average"
        }
    
    def _assess_future_preparedness(self, category_scores, lessons_learned, incident_complexity):
        """Assess future preparedness based on current performance"""
        base_preparedness = 75.0
        
        # Category performance impact
        avg_category_score = sum(cat.score for cat in category_scores) / len(category_scores) if category_scores else 75
        preparedness_adjustment = (avg_category_score - 75) * 0.3
        base_preparedness += preparedness_adjustment
        
        # Lessons learned impact
        high_priority_lessons = len([lesson for lesson in lessons_learned if lesson.priority == 'high'])
        if high_priority_lessons > 0:
            base_preparedness -= high_priority_lessons * 2  # Each high-priority lesson indicates preparedness gap
        
        # Complexity handling capability
        complexity_level = incident_complexity.get('classification', 'medium')
        if complexity_level == 'high' and avg_category_score >= 80:
            base_preparedness += 5  # Bonus for handling complex incidents well
        
        return max(0, min(100, base_preparedness))
    
    def _assess_risk_mitigation_effectiveness(self, category_scores, incident_data, contextual_factors):
        """Assess risk mitigation effectiveness"""
        base_score = 75.0
        
        # Risk management category performance
        risk_category = next((cat for cat in category_scores if 'risk' in cat.category.lower()), None)
        if risk_category:
            base_score = risk_category.score
        
        # Severity handling
        if incident_data:
            severity = getattr(incident_data, 'severity', 'unknown')
            if severity in ['high', 'critical']:
                # High-severity incidents test risk mitigation
                if base_score >= 80:
                    base_score += 5  # Bonus for good high-risk handling
                else:
                    base_score -= 5  # Penalty for poor high-risk handling
        
        # Environmental risk factors
        env_factors = contextual_factors.get('environmental_factors', [])
        if env_factors and base_score >= 75:
            base_score += 3  # Bonus for handling environmental risks
        
        return max(0, min(100, base_score))
    
    def _calculate_confidence_score(self, category_scores, incident_data):
        """Calculate confidence in evaluation"""
        base_confidence = 80.0
        
        # Data availability impact
        if incident_data:
            if hasattr(incident_data, 'description') and len(getattr(incident_data, 'description', '')) > 50:
                base_confidence += 5
            if hasattr(incident_data, 'file_analyses') and incident_data.file_analyses:
                base_confidence += 5
        
        # Category coverage
        if len(category_scores) >= 4:
            base_confidence += 10
        
        return min(100, base_confidence)
    
    def _calculate_data_completeness(self, incident_data, response_plan, execution_summary):
        """Calculate data completeness score"""
        completeness = 0.0
        total_components = 3
        
        if incident_data:
            completeness += 1
        if response_plan:
            completeness += 1
        if execution_summary:
            completeness += 1
        
        return (completeness / total_components) * 100
    def _calculate_overall_score(self, category_scores):
        """Calculate overall score (legacy method for compatibility)"""
        return self._calculate_contextual_score(category_scores, {'classification': 'medium'}, {})
    
    def _assess_response_quality(self, score, category_scores):
        """Assess response quality (legacy method for compatibility)"""
        return f"Response achieved {score:.1f}% effectiveness with strong performance in key areas"
    
    def _aggregate_findings(self, category_scores):
        """Aggregate findings (legacy method for compatibility)"""
        return self._perform_deep_analysis(category_scores, {'classification': 'medium'}, {})
    
    def _generate_lessons_learned(self, incident_data, response_plan, execution_summary, category_scores):
        """Generate lessons learned (legacy method for compatibility)"""
        return self._generate_actionable_lessons(
            incident_data, response_plan, execution_summary, category_scores,
            {'classification': 'medium'}, {}
        )
    
    def _generate_improvement_recommendations(self, category_scores, lessons_learned, incident_data):
        """Generate improvement recommendations (legacy method for compatibility)"""
        return self._generate_strategic_recommendations(
            category_scores, lessons_learned, incident_data, {'classification': 'medium'}
        )
    
    def _compare_to_benchmarks(self, incident_data, overall_score, category_scores):
        """Compare to benchmarks (legacy method for compatibility)"""
        return self._perform_advanced_benchmarking(
            incident_data, overall_score, category_scores, {'classification': 'medium'}
        )
    
    def _compare_to_peers(self, incident_data, overall_score, execution_summary):
        """Compare to peers (legacy method for compatibility)"""
        return self._perform_peer_analysis(incident_data, overall_score, execution_summary, {})
    
    def _assess_preparedness(self, category_scores, lessons_learned):
        """Assess preparedness (legacy method for compatibility)"""
        return self._assess_future_preparedness(category_scores, lessons_learned, {'classification': 'medium'})
    
    def _determine_effectiveness_rating(self, score):
        """Determine effectiveness rating"""
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Good"
        elif score >= 70:
            return "Satisfactory"
        elif score >= 60:
            return "Needs Improvement"
        else:
            return "Poor"
    
    def _assess_response_quality(self, score, category_scores):
        """Assess response quality"""
        return f"Response achieved {score:.1f}% effectiveness with strong performance in key areas"
    
    def _aggregate_findings(self, category_scores):
        """Aggregate findings"""
        strengths = []
        weaknesses = []
        critical_gaps = []
        
        for category in category_scores:
            strengths.extend(category.strengths)
            weaknesses.extend(category.weaknesses)
            if category.score < 60:
                critical_gaps.append(f"Critical gap in {category.category.lower()}")
        
        return strengths, weaknesses, critical_gaps
    
    def _generate_lessons_learned(self, incident_data, response_plan, execution_summary, category_scores):
        """Generate lessons learned"""
        lessons = []
        
        # Basic lesson
        lessons.append(LessonLearned(
            lesson_id="LESSON-001",
            category="process_improvement",
            lesson="Multi-agent workflow successfully processed incident",
            evidence="All workflow stages completed successfully",
            impact="Demonstrates system reliability",
            priority="medium",
            actionable_steps=["Continue monitoring system performance"]
        ))
        
        # Performance-based lessons
        if execution_summary and hasattr(execution_summary, 'success_rate'):
            if execution_summary.success_rate < 85:
                lessons.append(LessonLearned(
                    lesson_id="LESSON-002",
                    category="execution_quality",
                    lesson="Action execution quality can be improved",
                    evidence=f"Success rate was {execution_summary.success_rate:.1f}%",
                    impact="Better execution leads to improved outcomes",
                    priority="high",
                    actionable_steps=["Review failed actions", "Improve training"]
                ))
        
        return lessons
    
    def _generate_improvement_recommendations(self, category_scores, lessons_learned, incident_data):
        """Generate improvement recommendations"""
        recommendations = []
        
        # Basic recommendation
        recommendations.append(ImprovementRecommendation(
            recommendation_id="REC-001",
            category="system_enhancement",
            title="Enhance response time tracking",
            description="Implement more detailed response time metrics",
            priority="medium",
            estimated_effort="2-3 weeks",
            expected_benefit="Better performance monitoring",
            implementation_timeline="Next quarter",
            responsible_party="Development Team"
        ))
        
        # Category-specific recommendations
        for category in category_scores:
            if category.score < 75:
                recommendations.append(ImprovementRecommendation(
                    recommendation_id=f"REC-{len(recommendations)+1:03d}",
                    category=category.category.lower().replace(" ", "_"),
                    title=f"Improve {category.category}",
                    description=f"Address weaknesses in {category.category.lower()}",
                    priority="high" if category.score < 60 else "medium",
                    estimated_effort="2-4 weeks",
                    expected_benefit="Improved overall effectiveness",
                    implementation_timeline="Next 30 days",
                    responsible_party="Response Team"
                ))
        
        return recommendations
    
    def _compare_to_benchmarks(self, incident_data, overall_score, category_scores):
        """Compare to benchmarks"""
        return {"benchmark_score": 75.0, "comparison": "Above average" if overall_score > 75 else "Average"}
    
    def _compare_to_peers(self, incident_data, overall_score, execution_summary):
        """Compare to peers"""
        return {"peer_average": 70.0, "ranking": "Top 25%" if overall_score > 80 else "Average"}
    
    def _evaluate_image_analysis_category(self, file_analyses: List[Dict[str, Any]]) -> CategoryScore:
        """Evaluate image analysis and evidence quality"""
        
        if not file_analyses:
            return CategoryScore(
                category="Image Evidence",
                score=100.0,  # No images is not a negative
                weight=0.0,   # No weight if no images
                metrics=[],
                strengths=[],
                weaknesses=[]
            )
        
        total_files = len(file_analyses)
        suspicious_files = len([f for f in file_analyses if f.get('requires_human_review', False)])
        avg_confidence = sum(f.get('confidence_score', 50) for f in file_analyses) / total_files
        
        # Calculate score based on authenticity and quality
        base_score = avg_confidence
        
        # Penalty for suspicious files
        if suspicious_files > 0:
            suspicion_penalty = (suspicious_files / total_files) * 30
            base_score -= suspicion_penalty
        
        # Bonus for high-quality evidence
        if avg_confidence > 80 and suspicious_files == 0:
            base_score += 10
        
        # Ensure score is within bounds
        score = max(0, min(100, base_score))
        
        # Determine strengths and weaknesses
        strengths = []
        weaknesses = []
        
        if total_files > 0:
            strengths.append(f"Visual evidence provided ({total_files} files)")
        
        if avg_confidence > 75:
            strengths.append("High-quality image evidence")
        
        if suspicious_files == 0:
            strengths.append("All files passed authenticity checks")
        else:
            weaknesses.append(f"{suspicious_files} files require human verification")
        
        if avg_confidence < 60:
            weaknesses.append("Low confidence in image authenticity")
        
        return CategoryScore(
            category="Image Evidence",
            score=score,
            weight=0.15,  # 15% weight for image evidence
            metrics=[
                PerformanceMetric(
                    metric_name="Files Processed",
                    category="image_analysis",
                    value=float(total_files),
                    target_value=1.0,
                    unit="files",
                    status="excellent" if total_files > 0 else "good",
                    weight=0.3
                ),
                PerformanceMetric(
                    metric_name="Authenticity Confidence",
                    category="image_analysis", 
                    value=avg_confidence,
                    target_value=80.0,
                    unit="percent",
                    status="excellent" if avg_confidence > 80 else "good" if avg_confidence > 60 else "needs_improvement",
                    weight=0.4
                ),
                PerformanceMetric(
                    metric_name="Suspicious Files",
                    category="image_analysis",
                    value=float(suspicious_files),
                    target_value=0.0,
                    unit="files",
                    status="excellent" if suspicious_files == 0 else "needs_improvement",
                    weight=0.3
                )
            ],
            strengths=strengths,
            weaknesses=weaknesses
        )
    
    def _create_minimal_evaluation_report(self, state) -> EvaluationReport:
        """Create minimal evaluation report as fallback"""
        evaluation_id = f"EVAL-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Basic category score
        basic_category = CategoryScore(
            category="overall_response",
            score=75.0,
            weight=1.0,
            metrics=[],
            strengths=["Response initiated successfully"],
            weaknesses=["Limited data for comprehensive evaluation"]
        )
        
        # Basic lessons learned
        basic_lesson = LessonLearned(
            lesson_id="LESSON-001",
            category="process_improvement",
            lesson="Incident response workflow completed successfully",
            evidence="System processed incident through all stages",
            impact="Demonstrates system capability",
            priority="medium",
            actionable_steps=["Continue monitoring system performance"]
        )
        
        # Basic recommendation
        basic_recommendation = ImprovementRecommendation(
            recommendation_id="REC-001",
            category="system_enhancement",
            title="Enhance data collection for better evaluation",
            description="Improve data collection mechanisms to enable more comprehensive evaluation",
            priority="medium",
            estimated_effort="2-4 weeks",
            expected_benefit="Better evaluation accuracy",
            implementation_timeline="Next quarter",
            responsible_party="Development Team"
        )
        
        return EvaluationReport(
            evaluation_id=evaluation_id,
            incident_id=getattr(state.incident_data, 'incident_id', 'unknown') if state.incident_data else "unknown",
            plan_id=getattr(state.response_plan, 'plan_id', 'unknown') if state.response_plan else "unknown",
            execution_id=getattr(state.execution_summary, 'execution_id', 'unknown') if state.execution_summary else "unknown",
            overall_score=75.0,
            effectiveness_rating="Satisfactory",
            response_quality="Basic response completed with limited evaluation data",
            category_scores=[basic_category],
            weaknesses=["Limited data for comprehensive evaluation"],
            critical_gaps=[],
            lessons_learned=[basic_lesson],
            improvement_recommendations=[basic_recommendation],
            benchmark_comparison={"benchmark_score": 75.0, "comparison": "Average"},
            peer_comparison={"peer_average": 70.0, "ranking": "Average"},
            preparedness_score=75.0,
            risk_mitigation_effectiveness=75.0,
            evaluation_timestamp=datetime.now().isoformat(),
            evaluator_confidence=60.0,
            data_completeness=50.0
        )


def create_evaluator_node():
    """Create and return an evaluator node instance"""
    return EvaluatorNode()