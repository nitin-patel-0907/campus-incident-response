#!/usr/bin/env python3
import sys, os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
"""
Sync recent incidents from real_incidents.json to RL system
"""
import json
from datetime import datetime, timedelta

def sync_incidents_to_rl():
    """Sync recent incidents to RL system for performance analysis"""
    print("🔄 Syncing Recent Incidents to RL System")
    print("=" * 50)
    
    try:
        # Load real incidents
        with open('real_incidents.json', 'r') as f:
            real_incidents = json.load(f)
        
        print(f"Found {len(real_incidents)} incidents in real_incidents.json")
        
        # Load RL system data
        try:
            with open('rl_system_data.json', 'r') as f:
                rl_data = json.load(f)
        except FileNotFoundError:
            rl_data = {
                "incidents": [],
                "spam_patterns": [],
                "performance_metrics": [],
                "learning_stats": {
                    "total_incidents": 0,
                    "spam_detected": 0,
                    "false_positives": 0,
                    "ai_vs_human_comparisons": 0,
                    "system_accuracy": 0.0,
                    "last_updated": datetime.now().isoformat(),
                    "gibberish_detected": 0
                },
                "confidence_improvements": {},
                "decision_rewards": {}
            }
        
        print(f"Current RL system has {len(rl_data['incidents'])} incidents")
        
        # Get recent incidents (last 24 hours)
        cutoff_time = datetime.now() - timedelta(hours=24)
        recent_incidents = []
        
        for incident in real_incidents:
            created_at = datetime.fromisoformat(incident['created_at'].replace('Z', '+00:00').replace('+00:00', ''))
            if created_at > cutoff_time:
                recent_incidents.append(incident)
        
        print(f"Found {len(recent_incidents)} recent incidents to sync")
        
        # Convert and add recent incidents to RL system
        autonomous_count = 0
        supervised_count = 0
        human_count = 0
        
        for incident in recent_incidents:
            # Check if already in RL system
            incident_id = incident['incident_id']
            already_exists = any(rl_inc['incident_id'] == incident_id for rl_inc in rl_data['incidents'])
            
            if already_exists:
                print(f"   ⏭️  Skipping {incident_id} (already in RL system)")
                continue
            
            # Extract confidence data
            evaluation_report = incident.get('evaluation_report', {})
            confidence_index = evaluation_report.get('confidence_index', {})
            
            confidence = confidence_index.get('overall_confidence', 0)
            recommendation = confidence_index.get('resolution_recommendation', 'supervised')
            
            # Create RL incident entry
            rl_incident = {
                "incident_id": incident_id,
                "incident_type": incident.get('incident_data', {}).get('incident_type', 'unknown'),
                "severity": incident.get('incident_data', {}).get('severity', 'unknown'),
                "original_report": incident.get('original_report', ''),
                "stages": {
                    "evaluator": {
                        "confidence_index": confidence_index
                    }
                },
                "rl_metadata": {
                    "added_at": incident['created_at'],
                    "incident_number": len(rl_data['incidents']) + 1,
                    "processing_time": 2.0,  # Estimated processing time
                    "resources_used": 1.5,   # Estimated resources
                    "confidence_analysis": confidence_index,
                    "learning_applied": True,
                    "similar_incidents_count": 0,
                    "historical_context": {
                        "message": "Synced from real incidents"
                    }
                }
            }
            
            # Add resolution data for performance analysis
            if recommendation == 'autonomous':
                rl_incident["resolution_data"] = {
                    "resolved_by_ai": True,
                    "ai_processing_time": 2.0,
                    "ai_resources_used": 1.5,
                    "ai_accuracy": confidence / 100.0,
                    "resolution_status": "resolved"
                }
                autonomous_count += 1
            elif recommendation == 'supervised':
                rl_incident["resolution_data"] = {
                    "resolved_by_ai": True,
                    "requires_supervision": True,
                    "ai_processing_time": 2.5,
                    "ai_resources_used": 2.0,
                    "ai_accuracy": confidence / 100.0,
                    "resolution_status": "under_review"
                }
                supervised_count += 1
            else:
                rl_incident["resolution_data"] = {
                    "resolved_by_human": True,
                    "human_processing_time": 15.0,
                    "human_resources_used": 5.0,
                    "human_accuracy": 0.85,
                    "resolution_status": "pending_human"
                }
                human_count += 1
            
            rl_data['incidents'].append(rl_incident)
            print(f"   ✅ Added {incident_id} ({recommendation})")
        
        # Update learning stats
        rl_data['learning_stats']['total_incidents'] = len(rl_data['incidents'])
        rl_data['learning_stats']['ai_vs_human_comparisons'] = autonomous_count + supervised_count + human_count
        rl_data['learning_stats']['last_updated'] = datetime.now().isoformat()
        
        # Save updated RL data
        with open('rl_system_data.json', 'w') as f:
            json.dump(rl_data, f, indent=2, default=str)
        
        print(f"\n📊 Sync Results:")
        print(f"   🤖 Autonomous AI: {autonomous_count}")
        print(f"   👥 Supervised AI: {supervised_count}")
        print(f"   👤 Human Required: {human_count}")
        print(f"   📈 Total RL Incidents: {len(rl_data['incidents'])}")
        
        print(f"\n✅ RL system updated successfully!")
        print(f"   Performance tab should now show AI vs Human data")
        
    except Exception as e:
        print(f"❌ Error syncing incidents: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    sync_incidents_to_rl()