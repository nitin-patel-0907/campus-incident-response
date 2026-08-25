"""
Simple incident storage system for real-time incidents
Stores incidents with their complete analysis including evaluation reports
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

class IncidentStorage:
    """Simple file-based incident storage"""
    
    def __init__(self, storage_file: str = "real_incidents.json"):
        if not os.path.exists(storage_file):
            alt_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", storage_file)
            if os.path.exists(alt_path):
                storage_file = alt_path
            elif os.path.exists(os.path.join("data", storage_file)):
                storage_file = os.path.join("data", storage_file)
        self.storage_file = storage_file
        self.incidents = self._load_incidents()
    
    def _load_incidents(self) -> List[Dict[str, Any]]:
        """Load incidents from storage file"""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading incidents: {e}")
                return []
        return []
    
    def _save_incidents(self):
        """Save incidents to storage file"""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.incidents, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving incidents: {e}")
    
    def store_incident(self, workflow_result: Dict[str, Any]) -> str:
        """Store a processed incident with all its analysis data"""
        try:
            # Extract incident data from workflow result
            incident_data = workflow_result.get("incident_data", {})
            if hasattr(incident_data, '__dict__'):
                incident_data = incident_data.__dict__
            elif hasattr(incident_data, 'dict'):
                incident_data = incident_data.dict()
            
            # Preserve original metadata if available
            original_metadata = workflow_result.get("metadata", {})
            if original_metadata:
                # Use original metadata to override AI-enhanced data where appropriate
                if "incident_type" in original_metadata:
                    incident_data["incident_type"] = original_metadata["incident_type"]
                if "severity" in original_metadata:
                    incident_data["severity"] = original_metadata["severity"]
                if "location" in original_metadata:
                    incident_data["location"] = original_metadata["location"]
                if "anonymous_report" in original_metadata:
                    incident_data["anonymous"] = original_metadata["anonymous_report"]
            
            # Extract evaluation report - handle both raw workflow and transformed data
            evaluation_report = None
            stages = workflow_result.get("stages", {})
            
            if "evaluator" in stages:
                # Raw workflow result format
                evaluation_report = stages["evaluator"]
                if hasattr(evaluation_report, '__dict__'):
                    evaluation_report = evaluation_report.__dict__
                elif hasattr(evaluation_report, 'dict'):
                    evaluation_report = evaluation_report.dict()
            elif workflow_result.get("result", {}).get("evaluation_report"):
                # Transformed result format (from unified server)
                evaluation_report = workflow_result["result"]["evaluation_report"]
            
            # Extract other analysis components
            response_plan = None
            if "planner" in stages:
                response_plan = stages["planner"]
            elif workflow_result.get("result", {}).get("response_plan"):
                response_plan = workflow_result["result"]["response_plan"]
            
            if hasattr(response_plan, '__dict__'):
                response_plan = response_plan.__dict__
            elif hasattr(response_plan, 'dict'):
                response_plan = response_plan.dict()
            
            execution_summary = None
            if "executor" in stages:
                execution_summary = stages["executor"]
            elif workflow_result.get("result", {}).get("execution_summary"):
                execution_summary = workflow_result["result"]["execution_summary"]
            
            if hasattr(execution_summary, '__dict__'):
                execution_summary = execution_summary.__dict__
            elif hasattr(execution_summary, 'dict'):
                execution_summary = execution_summary.dict()
            
            compliance_report = None
            if "safety" in stages:
                compliance_report = stages["safety"]
            elif workflow_result.get("result", {}).get("compliance_report"):
                compliance_report = workflow_result["result"]["compliance_report"]
            
            if hasattr(compliance_report, '__dict__'):
                compliance_report = compliance_report.__dict__
            elif hasattr(compliance_report, 'dict'):
                compliance_report = compliance_report.dict()
            
            # Create stored incident
            stored_incident = {
                "incident_id": workflow_result.get("incident_id", "unknown"),
                "workflow_id": workflow_result.get("incident_id", "unknown"),  # Use incident_id as workflow_id
                "created_at": workflow_result.get("workflow_start", datetime.now().isoformat()),
                "updated_at": datetime.now().isoformat(),
                "status": workflow_result.get("status", "completed"),
                "execution_mode": workflow_result.get("execution_mode", "simulate"),
                "original_report": workflow_result.get("original_report", "No report text available"),  # Store original report
                
                # Core incident data (with original metadata preserved)
                "incident_data": incident_data,
                "original_metadata": original_metadata,  # Store original metadata separately
                
                # Analysis components
                "response_plan": response_plan,
                "execution_summary": execution_summary,
                "compliance_report": compliance_report,
                "evaluation_report": evaluation_report,
                
                # Processing stages
                "processing_stages": {
                    "intake": "completed",
                    "planning": "completed",
                    "safety": "completed", 
                    "execution": "completed",
                    "evaluation": "completed" if evaluation_report else "pending"
                },
                
                # Workflow metadata
                "workflow_metadata": {
                    "workflow_id": workflow_result.get("workflow_id"),
                    "created_at": workflow_result.get("workflow_start"),
                    "updated_at": datetime.now().isoformat(),
                    "execution_mode": workflow_result.get("execution_mode", "simulate"),
                    "stages_completed": list(stages.keys()) if stages else []
                }
            }
            
            # Add to incidents list
            self.incidents.append(stored_incident)
            
            # Save to file
            self._save_incidents()
            
            incident_id = stored_incident["incident_id"]
            
            # Debug: Check if confidence analysis is present
            if evaluation_report and evaluation_report.get("confidence_index"):
                confidence_score = evaluation_report["confidence_index"].get("overall_confidence", "N/A")
                print(f"✅ Stored incident {incident_id} with confidence analysis ({confidence_score}%)")
            else:
                print(f"✅ Stored incident {incident_id} with evaluation report")
            
            return incident_id
            
        except Exception as e:
            print(f"Error storing incident: {e}")
            import traceback
            traceback.print_exc()
            return "error"
    
    def get_incident(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific incident by ID"""
        for incident in self.incidents:
            if incident.get("incident_id") == incident_id or incident.get("workflow_id") == incident_id:
                return incident
        return None
    
    def get_all_incidents(self, limit: int = 50, offset: int = 0, 
                         status_filter: str = None, severity_filter: str = None) -> Dict[str, Any]:
        """Get all incidents with filtering and pagination"""
        filtered_incidents = []
        
        for incident in self.incidents:
            # Apply filters
            if status_filter:
                incident_status = self._get_incident_status(incident)
                if incident_status != status_filter:
                    continue
            
            if severity_filter:
                incident_data = incident.get("incident_data", {})
                severity = incident_data.get("severity", "unknown")
                if severity != severity_filter:
                    continue
            
            filtered_incidents.append(incident)
        
        # Sort by date (newest first)
        filtered_incidents.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Apply pagination
        total_count = len(filtered_incidents)
        paginated_incidents = filtered_incidents[offset:offset + limit]
        
        return {
            "incidents": paginated_incidents,
            "total_count": total_count,
            "has_more": offset + limit < total_count
        }
    
    def _get_incident_status(self, incident: Dict[str, Any]) -> str:
        """Determine incident status for filtering"""
        evaluation_report = incident.get("evaluation_report", {})
        if evaluation_report:
            resolution_status = evaluation_report.get("resolution_status", "unresolved")
            return "resolved" if resolution_status == "resolved" else "unresolved"
        return "unresolved"
    
    def get_analytics_data(self) -> Dict[str, Any]:
        """Get analytics data from stored incidents"""
        if not self.incidents:
            return {
                "total_incidents": 0,
                "resolved_incidents": 0,
                "incident_types": {},
                "severity_distribution": {},
                "recent_incidents": []
            }
        
        # Calculate statistics
        total_incidents = len(self.incidents)
        resolved_incidents = 0
        incident_types = {}
        severity_distribution = {}
        
        for incident in self.incidents:
            # Count resolved incidents
            if self._get_incident_status(incident) == "resolved":
                resolved_incidents += 1
            
            # Count incident types - use original metadata first
            incident_data = incident.get("incident_data", {})
            original_metadata = incident.get("original_metadata", {})
            incident_type = original_metadata.get("incident_type") or incident_data.get("incident_type", "unknown")
            incident_types[incident_type] = incident_types.get(incident_type, 0) + 1
            
            # Count severity distribution - use original metadata first
            severity = original_metadata.get("severity") or incident_data.get("severity", "unknown")
            severity_distribution[severity] = severity_distribution.get(severity, 0) + 1
        
        # Get recent incidents (last 10)
        recent_incidents = []
        sorted_incidents = sorted(self.incidents, key=lambda x: x.get("created_at", ""), reverse=True)
        
        for incident in sorted_incidents[:10]:
            incident_data = incident.get("incident_data", {})
            original_metadata = incident.get("original_metadata", {})
            
            # Use original metadata first, then fall back to processed data
            incident_type = original_metadata.get("incident_type") or incident_data.get("incident_type", "other")
            location = original_metadata.get("location") or incident_data.get("location", "Unknown location")
            
            # Calculate time ago
            try:
                created_time = datetime.fromisoformat(incident.get("created_at", "").replace('Z', '+00:00'))
                time_diff = datetime.now() - created_time.replace(tzinfo=None)
                
                if time_diff.days > 0:
                    time_ago = f"{time_diff.days} days ago"
                elif time_diff.seconds > 3600:
                    hours = time_diff.seconds // 3600
                    time_ago = f"{hours} hours ago"
                elif time_diff.seconds > 60:
                    minutes = time_diff.seconds // 60
                    time_ago = f"{minutes} minutes ago"
                else:
                    time_ago = "Just now"
            except:
                time_ago = "Recently"
            
            recent_incidents.append({
                "id": incident.get("incident_id", "Unknown"),
                "type": (incident_type or "other").title(),
                "location": location,
                "time": time_ago,
                "status": self._get_incident_status(incident),
                "severity": original_metadata.get("severity") or incident_data.get("severity", "medium"),
                "workflow_id": incident.get("workflow_id", "Unknown")
            })
        
        return {
            "total_incidents": total_incidents,
            "resolved_incidents": resolved_incidents,
            "incident_types": incident_types,
            "severity_distribution": severity_distribution,
            "recent_incidents": recent_incidents,
            "overall_score": self._calculate_overall_score(),
            "last_updated": datetime.now().isoformat()
        }
    
    def _calculate_overall_score(self) -> float:
        """Calculate overall system performance score"""
        if not self.incidents:
            return 0.0
        
        total_score = 0
        count = 0
        
        for incident in self.incidents:
            evaluation_report = incident.get("evaluation_report", {})
            if evaluation_report and "overall_score" in evaluation_report:
                total_score += evaluation_report["overall_score"]
                count += 1
        
        return total_score / count if count > 0 else 0.0

# Global instance
incident_storage = IncidentStorage()