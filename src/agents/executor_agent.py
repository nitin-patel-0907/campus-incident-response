"""
Executor Agent - Implements action plans and coordinates response execution
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent
from datetime import datetime


class ExecutorAgent(BaseAgent):
    """
    Agent responsible for executing action plans, coordinating resources,
    and tracking implementation progress
    """
    
    def __init__(self):
        super().__init__(
            name="Executor Agent",
            description="Executes action plans and coordinates incident response"
        )
        self.active_executions: Dict[str, Dict[str, Any]] = {}
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute action plan and coordinate response
        
        Args:
            input_data: {
                "action_plan": dict - From Planner Agent
                "priority_level": str - Priority level
                "mode": str - "simulate" or "execute"
            }
        
        Returns:
            {
                "execution_summary": dict - Summary of execution
                "task_status": dict - Status of all tasks
                "notifications_sent": list - Notifications dispatched
                "resources_allocated": list - Resources assigned
                "status": str
            }
        """
        try:
            action_plan = input_data.get("action_plan", {})
            priority = input_data.get("priority_level", "medium")
            mode = input_data.get("mode", "simulate")
            
            incident_id = action_plan.get("incident_id", f"INC-{datetime.now().strftime('%Y%m%d%H%M%S')}")
            
            # Execute immediate actions
            immediate_results = self._execute_immediate_actions(
                action_plan.get("immediate_actions", []), mode
            )
            
            # Allocate resources
            resource_allocation = self._allocate_resources(
                action_plan.get("resources_needed", []), mode
            )
            
            # Send notifications
            notifications = self._send_notifications(
                action_plan.get("stakeholders", []),
                incident_id, mode
            )
            
            # Schedule actions
            scheduled_actions = self._schedule_actions(
                action_plan.get("short_term_actions", []),
                action_plan.get("long_term_actions", []), mode
            )
            
            execution_summary = {
                "incident_id": incident_id,
                "priority": priority,
                "execution_mode": mode,
                "start_time": datetime.now().isoformat(),
                "immediate_actions_executed": len(immediate_results),
                "resources_allocated": len(resource_allocation),
                "notifications_sent": len(notifications),
                "overall_status": "in_progress" if mode == "execute" else "simulated"
            }
            
            task_status = self._compile_task_status(immediate_results, scheduled_actions)
            
            output = {
                "execution_summary": execution_summary,
                "task_status": task_status,
                "immediate_actions_results": immediate_results,
                "notifications_sent": notifications,
                "resources_allocated": resource_allocation,
                "scheduled_actions": scheduled_actions,
                "status": "success",
                "execution_timestamp": datetime.now().isoformat()
            }
            
            self.active_executions[incident_id] = output
            self.log_execution(input_data, output, "success")
            return output
            
        except Exception as e:
            error_output = {"status": "error", "error": str(e)}
            self.log_execution(input_data, error_output, "error")
            return error_output
    
    def _execute_immediate_actions(self, actions: List[Dict[str, Any]], mode: str) -> List[Dict[str, Any]]:
        """Execute immediate actions"""
        results = []
        for action in actions:
            results.append({
                "action": action.get("action", "Unknown"),
                "responsible": action.get("responsible", "Unassigned"),
                "deadline": action.get("deadline", "No deadline"),
                "initiated_at": datetime.now().isoformat(),
                "status": "initiated" if mode == "execute" else "simulated",
                "tracking_id": f"TASK-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            })
        return results
    
    def _allocate_resources(self, resources: List[Dict[str, str]], mode: str) -> List[Dict[str, Any]]:
        """Allocate resources"""
        allocations = []
        for resource in resources:
            allocations.append({
                "resource": resource.get("resource", "Unknown"),
                "type": resource.get("type", "Unknown"),
                "allocated_at": datetime.now().isoformat(),
                "status": "allocated" if mode == "execute" else "simulated",
                "allocation_id": f"RES-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            })
        return allocations
    
    def _send_notifications(self, stakeholders: List[Dict[str, str]], incident_id: str, mode: str) -> List[Dict[str, Any]]:
        """Send notifications"""
        notifications = []
        for stakeholder in stakeholders:
            notifications.append({
                "recipient": stakeholder.get("role", "Unknown"),
                "priority": stakeholder.get("notification_priority", "standard"),
                "incident_id": incident_id,
                "sent_at": datetime.now().isoformat(),
                "status": "sent" if mode == "execute" else "simulated",
                "notification_id": f"NOTIF-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            })
        return notifications
    
    def _schedule_actions(self, short_term: List[Dict[str, Any]], long_term: List[Dict[str, Any]], mode: str) -> List[Dict[str, Any]]:
        """Schedule actions"""
        scheduled = []
        for action in short_term + long_term:
            scheduled.append({
                "action": action.get("action", "Unknown"),
                "responsible": action.get("responsible", "Unassigned"),
                "deadline": action.get("deadline", "No deadline"),
                "phase": "short_term" if action in short_term else "long_term",
                "scheduled_at": datetime.now().isoformat(),
                "status": "scheduled" if mode == "execute" else "simulated",
                "task_id": f"SCHED-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            })
        return scheduled
    
    def _compile_task_status(self, immediate: List[Dict[str, Any]], scheduled: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compile task status"""
        total = len(immediate) + len(scheduled)
        completed = sum(1 for r in immediate if r.get("status") in ["initiated", "simulated"])
        
        return {
            "total_tasks": total,
            "completed": completed,
            "pending": len(scheduled),
            "completion_percentage": (completed / total * 100) if total > 0 else 0
        }