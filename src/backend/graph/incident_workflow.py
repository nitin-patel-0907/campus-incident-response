"""
LangGraph Workflow for Real-time Incident Response Analysis
"""
from typing import Dict, Any, List, Optional, Literal
from datetime import datetime
import json
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field

# Import all nodes
from ..nodes.intake_node import IntakeNode, IntakeNodeState, create_intake_node
from ..nodes.planner_node import PlannerNode, PlannerNodeState, create_planner_node
from ..nodes.safety_node import SafetyNode, SafetyNodeState, create_safety_node
from ..nodes.executor_node import ExecutorNode, ExecutorNodeState, create_executor_node
from ..nodes.evaluator_node import EvaluatorNode, EvaluatorNodeState, create_evaluator_node


class WorkflowState(BaseModel):
    """Complete workflow state that encompasses all node states"""
    # Core workflow data
    workflow_id: str = Field(description="Unique workflow identifier")
    status: str = Field(default="pending", description="Overall workflow status")
    current_node: str = Field(default="intake", description="Current processing node")
    next_node: str = Field(default="intake", description="Next node to process")
    
    # Messages and communication
    messages: List[BaseMessage] = Field(default_factory=list, description="Conversation messages")
    
    # Processing results from each node
    incident_data: Optional[Any] = None
    response_plan: Optional[Any] = None
    compliance_report: Optional[Any] = None
    execution_summary: Optional[Any] = None
    evaluation_report: Optional[Any] = None
    
    # Status tracking
    processing_status: str = Field(default="pending")
    planning_status: str = Field(default="pending")
    safety_status: str = Field(default="pending")
    execution_status: str = Field(default="pending")
    evaluation_status: str = Field(default="pending")
    
    # Configuration
    execution_mode: str = Field(default="simulate", description="Execution mode")
    requires_approval: bool = Field(default=False)
    
    # Error handling
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    
    # Metadata
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    
    class Config:
        arbitrary_types_allowed = True


class IncidentWorkflow:
    """
    LangGraph workflow for real-time incident response analysis
    """
    
    def __init__(self):
        self.workflow_id = f"WORKFLOW-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Initialize nodes
        self.intake_node = create_intake_node()
        self.planner_node = create_planner_node()
        self.safety_node = create_safety_node()
        self.executor_node = create_executor_node()
        self.evaluator_node = create_evaluator_node()
        
        # Create the workflow graph
        self.graph = self._create_workflow_graph()
        
        # Compile with memory for state persistence
        self.memory = MemorySaver()
        self.compiled_graph = self.graph.compile(checkpointer=self.memory)
        
        # Track active workflows
        self.active_workflows: Dict[str, Dict[str, Any]] = {}
    
    def _create_workflow_graph(self) -> StateGraph:
        """Create the LangGraph workflow"""
        
        # Create the state graph
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("intake", self._intake_wrapper)
        workflow.add_node("planner", self._planner_wrapper)
        workflow.add_node("safety", self._safety_wrapper)
        workflow.add_node("executor", self._executor_wrapper)
        workflow.add_node("evaluator", self._evaluator_wrapper)
        workflow.add_node("manual_review", self._manual_review_node)
        workflow.add_node("approval_queue", self._approval_queue_node)
        workflow.add_node("error_handler", self._error_handler_node)
        
        # Set entry point
        workflow.set_entry_point("intake")
        
        # Add conditional edges based on processing results
        workflow.add_conditional_edges(
            "intake",
            self._route_from_intake,
            {
                "planner": "planner",
                "error": "error_handler"
            }
        )
        
        workflow.add_conditional_edges(
            "planner",
            self._route_from_planner,
            {
                "safety": "safety",
                "executor": "executor",
                "error": "error_handler"
            }
        )
        
        workflow.add_conditional_edges(
            "safety",
            self._route_from_safety,
            {
                "executor": "executor",
                "manual_review": "manual_review",
                "approval_queue": "approval_queue",
                "error": "error_handler"
            }
        )
        
        workflow.add_conditional_edges(
            "executor",
            self._route_from_executor,
            {
                "evaluator": "evaluator",
                "error": "error_handler"
            }
        )
        
        workflow.add_edge("evaluator", END)
        workflow.add_edge("manual_review", END)
        workflow.add_edge("approval_queue", END)
        workflow.add_edge("error_handler", END)
        
        return workflow
    
    def _intake_wrapper(self, state: WorkflowState) -> WorkflowState:
        """Wrapper for intake node processing"""
        try:
            # Convert to intake node state
            intake_state = IntakeNodeState(
                messages=state.messages,
                processing_status=state.processing_status,
                errors=state.errors,
                warnings=state.warnings
            )
            
            # Pass original metadata to intake node if available
            original_metadata = None
            
            # Check if state has metadata attribute directly
            if hasattr(state, 'metadata') and isinstance(state.metadata, dict):
                original_metadata = state.metadata
            
            # Also check for metadata in state attributes
            if not original_metadata and hasattr(state, '__dict__'):
                for attr_name, attr_value in state.__dict__.items():
                    if attr_name not in ['messages', 'processing_status', 'errors', 'warnings'] and isinstance(attr_value, dict):
                        # Check if this looks like metadata (has form_submission key)
                        if isinstance(attr_value, dict) and 'form_submission' in attr_value:
                            original_metadata = attr_value
                            break
            
            # Set the original metadata in intake state
            if original_metadata:
                intake_state.original_metadata = original_metadata
            
            # Process through intake node
            result_state = self.intake_node(intake_state)
            
            # Update workflow state
            state.incident_data = result_state.incident_data
            state.processing_status = result_state.processing_status
            state.next_node = result_state.next_node
            state.messages = result_state.messages
            state.errors = result_state.errors
            state.warnings = result_state.warnings
            state.updated_at = datetime.now().isoformat()
            
            return state
            
        except Exception as e:
            state.errors.append(f"Intake processing error: {str(e)}")
            state.status = "error"
            state.next_node = "error_handler"
            return state
    
    def _planner_wrapper(self, state: WorkflowState) -> WorkflowState:
        """Wrapper for planner node processing"""
        try:
            # Convert to planner node state
            planner_state = PlannerNodeState(
                messages=state.messages,
                incident_data=state.incident_data,
                processing_status=state.processing_status,
                planning_status=state.planning_status,
                errors=state.errors,
                warnings=state.warnings
            )
            
            # Process through planner node
            result_state = self.planner_node(planner_state)
            
            # Update workflow state
            state.response_plan = result_state.response_plan
            state.planning_status = result_state.planning_status
            state.next_node = result_state.next_node
            state.messages = result_state.messages
            state.errors = result_state.errors
            state.warnings = result_state.warnings
            state.updated_at = datetime.now().isoformat()
            
            return state
            
        except Exception as e:
            state.errors.append(f"Planning error: {str(e)}")
            state.status = "error"
            state.next_node = "error_handler"
            return state
    
    def _safety_wrapper(self, state: WorkflowState) -> WorkflowState:
        """Wrapper for safety node processing"""
        try:
            # Convert to safety node state
            safety_state = SafetyNodeState(
                messages=state.messages,
                incident_data=state.incident_data,
                response_plan=state.response_plan,
                processing_status=state.processing_status,
                planning_status=state.planning_status,
                safety_status=state.safety_status,
                errors=state.errors,
                warnings=state.warnings
            )
            
            # Process through safety node
            result_state = self.safety_node(safety_state)
            
            # Update workflow state
            state.compliance_report = result_state.compliance_report
            state.safety_status = result_state.safety_status
            state.requires_approval = result_state.requires_approval
            state.next_node = result_state.next_node
            state.messages = result_state.messages
            state.errors = result_state.errors
            state.warnings = result_state.warnings
            state.updated_at = datetime.now().isoformat()
            
            return state
            
        except Exception as e:
            state.errors.append(f"Safety validation error: {str(e)}")
            state.status = "error"
            state.next_node = "error_handler"
            return state
    
    def _executor_wrapper(self, state: WorkflowState) -> WorkflowState:
        """Wrapper for executor node processing"""
        try:
            # Convert to executor node state
            executor_state = ExecutorNodeState(
                messages=state.messages,
                incident_data=state.incident_data,
                response_plan=state.response_plan,
                compliance_report=state.compliance_report,
                processing_status=state.processing_status,
                planning_status=state.planning_status,
                safety_status=state.safety_status,
                execution_status=state.execution_status,
                execution_mode=state.execution_mode,
                requires_approval=state.requires_approval,
                errors=state.errors,
                warnings=state.warnings
            )
            
            # Process through executor node
            result_state = self.executor_node(executor_state)
            
            # Update workflow state
            state.execution_summary = result_state.execution_summary
            state.execution_status = result_state.execution_status
            state.next_node = result_state.next_node
            state.messages = result_state.messages
            state.errors = result_state.errors
            state.warnings = result_state.warnings
            state.updated_at = datetime.now().isoformat()
            
            return state
            
        except Exception as e:
            state.errors.append(f"Execution error: {str(e)}")
            state.status = "error"
            state.next_node = "error_handler"
            return state
    
    def _evaluator_wrapper(self, state: WorkflowState) -> WorkflowState:
        """Wrapper for evaluator node processing"""
        try:
            # Convert to evaluator node state
            evaluator_state = EvaluatorNodeState(
                messages=state.messages,
                incident_data=state.incident_data,
                response_plan=state.response_plan,
                compliance_report=state.compliance_report,
                execution_summary=state.execution_summary,
                processing_status=state.processing_status,
                planning_status=state.planning_status,
                safety_status=state.safety_status,
                execution_status=state.execution_status,
                evaluation_status=state.evaluation_status,
                execution_mode=state.execution_mode,
                requires_approval=state.requires_approval,
                errors=state.errors,
                warnings=state.warnings
            )
            
            # Process through evaluator node
            result_state = self.evaluator_node(evaluator_state)
            
            # Update workflow state
            state.evaluation_report = result_state.evaluation_report
            state.evaluation_status = result_state.evaluation_status
            state.status = "completed"
            state.messages = result_state.messages
            state.errors = result_state.errors
            state.warnings = result_state.warnings
            state.updated_at = datetime.now().isoformat()
            
            return state
            
        except Exception as e:
            state.errors.append(f"Evaluation error: {str(e)}")
            state.status = "error"
            state.next_node = "error_handler"
            return state
    
    def _manual_review_node(self, state: WorkflowState) -> WorkflowState:
        """Handle cases requiring manual review"""
        state.status = "manual_review_required"
        state.messages.append(AIMessage(
            content="This incident requires manual review due to policy violations or safety concerns. "
                   "Please review the compliance report and take appropriate action."
        ))
        state.updated_at = datetime.now().isoformat()
        return state
    
    def _approval_queue_node(self, state: WorkflowState) -> WorkflowState:
        """Handle cases requiring approval"""
        state.status = "approval_required"
        state.messages.append(AIMessage(
            content="This incident response plan requires supervisory approval before execution. "
                   "The plan has been queued for review."
        ))
        state.updated_at = datetime.now().isoformat()
        return state
    
    def _error_handler_node(self, state: WorkflowState) -> WorkflowState:
        """Handle workflow errors"""
        state.status = "error"
        error_summary = "; ".join(state.errors[-3:])  # Last 3 errors
        state.messages.append(AIMessage(
            content=f"Workflow encountered errors: {error_summary}. "
                   "Please review the incident data and try again."
        ))
        state.updated_at = datetime.now().isoformat()
        return state
    
    def _route_from_intake(self, state: WorkflowState) -> Literal["planner", "error"]:
        """Route from intake node based on processing results"""
        if state.errors:
            return "error"
        else:
            return "planner"
    
    def _route_from_planner(self, state: WorkflowState) -> Literal["safety", "executor", "error"]:
        """Route from planner node based on planning results"""
        if state.errors:
            return "error"
        elif state.next_node == "safety":
            return "safety"
        else:
            return "executor"
    
    def _route_from_safety(self, state: WorkflowState) -> Literal["executor", "manual_review", "approval_queue", "error"]:
        """Route from safety node based on compliance results"""
        if state.errors:
            return "error"
        elif state.next_node == "manual_review":
            return "manual_review"
        elif state.next_node == "approval_queue":
            return "approval_queue"
        else:
            return "executor"
    
    def _route_from_executor(self, state: WorkflowState) -> Literal["evaluator", "error"]:
        """Route from executor node based on execution results"""
        if state.errors:
            return "error"
        else:
            return "evaluator"
    
    async def process_incident_async(self, incident_report: str, 
                                   execution_mode: str = "simulate",
                                   workflow_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process incident through the complete workflow asynchronously
        
        Args:
            incident_report: Raw incident report text
            execution_mode: "simulate" or "execute"
            workflow_config: Optional configuration parameters
            
        Returns:
            Complete workflow results
        """
        try:
            # Create initial state
            workflow_id = f"WF-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            
            initial_state = WorkflowState(
                workflow_id=workflow_id,
                execution_mode=execution_mode,
                messages=[HumanMessage(content=incident_report)]
            )
            
            # Apply any configuration
            if workflow_config:
                for key, value in workflow_config.items():
                    if hasattr(initial_state, key):
                        setattr(initial_state, key, value)
            
            # Create thread configuration for state persistence
            thread_config = {"configurable": {"thread_id": workflow_id}}
            
            # Run the workflow
            final_state = await self.compiled_graph.ainvoke(
                initial_state, 
                config=thread_config
            )
            
            # Store workflow results
            self.active_workflows[workflow_id] = final_state
            
            # Convert to response format
            return self._format_workflow_response(final_state, workflow_id)
            
        except Exception as e:
            return {
                "workflow_id": workflow_id if 'workflow_id' in locals() else "unknown",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def process_incident_sync(self, incident_report: str, 
                            execution_mode: str = "simulate",
                            workflow_config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process incident through the complete workflow synchronously
        
        Args:
            incident_report: Raw incident report text
            execution_mode: "simulate" or "execute"
            workflow_config: Optional configuration parameters
            
        Returns:
            Complete workflow results
        """
        try:
            # Create initial state
            workflow_id = f"WF-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            
            initial_state = WorkflowState(
                workflow_id=workflow_id,
                execution_mode=execution_mode,
                messages=[HumanMessage(content=incident_report)]
            )
            
            # Apply any configuration and preserve metadata
            if workflow_config:
                for key, value in workflow_config.items():
                    if hasattr(initial_state, key):
                        setattr(initial_state, key, value)
                    elif key == 'metadata':
                        # Store metadata for intake node to access
                        initial_state.metadata = value
            
            # Process through each node sequentially to ensure completion
            try:
                # Step 1: Intake
                state = self._intake_wrapper(initial_state)
                if state.errors:
                    print(f"Intake errors: {state.errors}")
                
                # Step 2: Planner (if intake successful)
                if state.processing_status == "completed":
                    state = self._planner_wrapper(state)
                    if state.errors:
                        print(f"Planner errors: {state.errors}")
                
                # Step 3: Safety (if planning successful)
                if state.planning_status == "completed":
                    state = self._safety_wrapper(state)
                    if state.errors:
                        print(f"Safety errors: {state.errors}")
                
                # Step 4: Executor (if safety successful)
                if state.safety_status == "completed":
                    state = self._executor_wrapper(state)
                    if state.errors:
                        print(f"Executor errors: {state.errors}")
                
                # Step 5: Evaluator (if execution successful)
                if state.execution_status == "completed":
                    state = self._evaluator_wrapper(state)
                    if state.errors:
                        print(f"Evaluator errors: {state.errors}")
                
                # Mark as completed if we got through all stages
                if state.evaluation_status == "completed":
                    state.status = "completed"
                else:
                    state.status = "partial_completion"
                
                final_state = state
                
            except Exception as workflow_error:
                print(f"Workflow execution error: {workflow_error}")
                # Fallback: try the original graph method
                thread_config = {"configurable": {"thread_id": workflow_id}}
                final_state = self.compiled_graph.invoke(initial_state, config=thread_config)
            
            # Store workflow results
            self.active_workflows[workflow_id] = final_state
            
            # Convert to response format
            return self._format_workflow_response(final_state, workflow_id)
            
        except Exception as e:
            print(f"Process incident error: {e}")
            return {
                "workflow_id": workflow_id if 'workflow_id' in locals() else "unknown",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific workflow"""
        if workflow_id in self.active_workflows:
            state = self.active_workflows[workflow_id]
            
            # Handle both dict and Pydantic model states
            if hasattr(state, '__dict__'):
                state_dict = state.__dict__
            elif isinstance(state, dict):
                state_dict = state
            else:
                state_dict = {}
            
            return {
                "workflow_id": workflow_id,
                "status": getattr(state, 'status', state_dict.get('status', 'unknown')),
                "current_node": getattr(state, 'current_node', state_dict.get('current_node', 'unknown')),
                "processing_status": getattr(state, 'processing_status', state_dict.get('processing_status', 'unknown')),
                "planning_status": getattr(state, 'planning_status', state_dict.get('planning_status', 'unknown')),
                "safety_status": getattr(state, 'safety_status', state_dict.get('safety_status', 'unknown')),
                "execution_status": getattr(state, 'execution_status', state_dict.get('execution_status', 'unknown')),
                "evaluation_status": getattr(state, 'evaluation_status', state_dict.get('evaluation_status', 'unknown')),
                "errors": getattr(state, 'errors', state_dict.get('errors', [])),
                "warnings": getattr(state, 'warnings', state_dict.get('warnings', [])),
                "updated_at": getattr(state, 'updated_at', state_dict.get('updated_at', 'unknown'))
            }
        return None
    
    def update_workflow_resolution(self, workflow_id: str, resolution_info: Dict[str, Any]):
        """Update workflow with resolution information"""
        if workflow_id in self.active_workflows:
            self.active_workflows[workflow_id]["resolution_info"] = resolution_info
            self.active_workflows[workflow_id]["updated_at"] = datetime.now().isoformat()
            print(f"✅ Updated workflow {workflow_id} with resolution: {resolution_info['status']}")
    
    def list_active_workflows(self) -> List[Dict[str, Any]]:
        """List all active workflows"""
        workflows = []
        for wf_id, state in self.active_workflows.items():
            # Handle both dict and Pydantic model states
            if hasattr(state, '__dict__'):
                state_dict = state.__dict__
            elif isinstance(state, dict):
                state_dict = state
            else:
                state_dict = {}
            
            workflow_info = {
                "workflow_id": wf_id,
                "status": getattr(state, 'status', state_dict.get('status', 'unknown')),
                "created_at": getattr(state, 'created_at', state_dict.get('created_at', 'unknown')),
                "updated_at": getattr(state, 'updated_at', state_dict.get('updated_at', 'unknown')),
                # Include the full state for history endpoint
                "incident_data": getattr(state, 'incident_data', state_dict.get('incident_data')),
                "response_plan": getattr(state, 'response_plan', state_dict.get('response_plan')),
                "evaluation_report": getattr(state, 'evaluation_report', state_dict.get('evaluation_report')),
                "reporter_info": state_dict.get('reporter_info'),  # This might be in metadata
            }
            workflows.append(workflow_info)
        
        return workflows
    
    def _format_workflow_response(self, final_state, workflow_id: str) -> Dict[str, Any]:
        """Format workflow response for API consumption"""
        
        # Handle both dict and object states
        if hasattr(final_state, '__dict__'):
            state_dict = final_state.__dict__
        elif isinstance(final_state, dict):
            state_dict = final_state
        else:
            state_dict = {}
        
        response = {
            "workflow_id": workflow_id,
            "status": state_dict.get("status", "unknown"),
            "execution_mode": state_dict.get("execution_mode", "simulate"),
            "created_at": state_dict.get("created_at"),
            "updated_at": state_dict.get("updated_at"),
            "processing_stages": {
                "intake": state_dict.get("processing_status", "unknown"),
                "planning": state_dict.get("planning_status", "unknown"),
                "safety": state_dict.get("safety_status", "unknown"),
                "execution": state_dict.get("execution_status", "unknown"),
                "evaluation": state_dict.get("evaluation_status", "unknown")
            },
            "errors": state_dict.get("errors", []),
            "warnings": state_dict.get("warnings", [])
        }
        
        # Add results if available
        if state_dict.get("incident_data"):
            response["incident_data"] = self._serialize_pydantic_model(state_dict["incident_data"])
        
        if state_dict.get("response_plan"):
            response["response_plan"] = self._serialize_pydantic_model(state_dict["response_plan"])
        
        if state_dict.get("compliance_report"):
            response["compliance_report"] = self._serialize_pydantic_model(state_dict["compliance_report"])
        
        if state_dict.get("execution_summary"):
            response["execution_summary"] = self._serialize_pydantic_model(state_dict["execution_summary"])
        
        if state_dict.get("evaluation_report"):
            response["evaluation_report"] = self._serialize_pydantic_model(state_dict["evaluation_report"])
        
        return response
    
    def _serialize_pydantic_model(self, model) -> Dict[str, Any]:
        """Serialize Pydantic model to dictionary"""
        if hasattr(model, 'dict'):
            return model.dict()
        elif hasattr(model, '__dict__'):
            return model.__dict__
        else:
            return str(model)
    
    def get_workflow_graph_visualization(self) -> str:
        """Get a text representation of the workflow graph"""
        return """
        Incident Response Workflow Graph:
        
        [START] → [Intake Node] → [Planner Node] → [Safety Node] → [Executor Node] → [Evaluator Node] → [END]
                       ↓              ↓              ↓              ↓
                  [Error Handler] [Error Handler] [Manual Review] [Error Handler]
                                                     ↓
                                               [Approval Queue]
        
        Node Functions:
        - Intake: Process raw incident reports into structured data with anonymous reporting support
        - Planner: Generate comprehensive response plans
        - Safety: Validate compliance and safety requirements
        - Executor: Execute or simulate response actions
        - Evaluator: Assess response effectiveness and generate insights
        - Manual Review: Handle policy violations requiring human intervention
        - Approval Queue: Queue high-risk incidents for supervisory approval
        - Error Handler: Manage workflow errors and exceptions
        
        Note: Fraud detection has been removed to support anonymous reporting with pseudonymous IDs.
        """


# Factory function to create workflow instance
def create_incident_workflow() -> IncidentWorkflow:
    """Factory function to create incident workflow"""
    return IncidentWorkflow()