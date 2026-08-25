#!/usr/bin/env python3
import sys, os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
"""
Simulate human review processing for incidents that require human intervention
"""
import json
import random
from datetime import datetime, timedelta

def simulate_human_review():
    """Simulate human review processing for low-confidence incidents"""
    print("👤 Simulating Human Review Processing")
    print("=" * 50)
    
    try:
        # Load RL system data
        with open('rl_system_data.json', 'r') as f:
            rl_data = json.load(f)
        
        incidents = rl_data.get('incidents', [])
        print(f"Found {len(incidents)} incidents in RL system")
        
        # Find incidents that need human review (supervised or human intervention)
        human_review_candidates = []
        
        for incident in incidents:
            # Check confidence data in both locations
            confidence_data = incident.get("confidence_analysis", {})
            if not confidence_data:
                stages = incident.get("stages", {})
                evaluator = stages.get("evaluator", {})
                confidence_data = evaluator.get("confidence_index", {})
            
            recommendation = confidence_data.get("resolution_recommendation", "")
            
            # Add human processing for supervised incidents (simulate human oversight)
            if recommendation == "supervised" and not incident.get("resolution_data", {}).get("human_reviewed", False):
                human_review_candidates.append(incident)
        
        print(f"Found {len(human_review_candidates)} incidents needing human review")
        
        # Simulate human review processing
        human_processed = 0
        
        for incident in human_review_candidates:
            incident_id = incident.get('incident_id', 'N/A')
            incident_type = incident.get('incident_type', 'unknown')
            
            print(f"\n👤 Processing human review for {incident_id}")
            print(f"   Type: {incident_type}")
            
            # Simulate human processing time (longer than AI)
            human_processing_time = random.uniform(300, 900)  # 5-15 minutes
            human_resources_used = random.uniform(3.0, 8.0)   # More resources than AI
            human_accuracy = random.uniform(0.85, 0.95)       # High human accuracy
            
            # Add human resolution data
            if "resolution_data" not in incident:
                incident["resolution_data"] = {}
            
            incident["resolution_data"].update({
                "human_reviewed": True,
                "resolved_by_human": True,
                "human_processing_time": human_processing_time,
                "human_resources_used": human_resources_used,
                "human_accuracy": human_accuracy,
                "human_review_date": datetime.now().isoformat(),
                "human_decision": "approved_with_modifications",
                "human_notes": f"Human review completed for {incident_type} incident. Additional oversight applied.",
                "resolution_status": "resolved_by_human"
            })
            
            print(f"   ⏱️  Processing Time: {human_processing_time/60:.1f} minutes")
            print(f"   📊 Resources Used: {human_resources_used:.1f}")
            print(f"   🎯 Accuracy: {human_accuracy*100:.1f}%")
            print(f"   ✅ Status: Resolved by Human")
            
            human_processed += 1
        
        # Create some additional human-only incidents (complex cases)
        print(f"\n👤 Creating Complex Human-Only Incidents...")
        
        complex_human_incidents = [
            {
                "incident_id": f"HUMAN-{datetime.now().strftime('%Y%m%d%H%M%S')}-001",
                "incident_type": "legal",
                "severity": "high",
                "original_report": "Complex legal matter requiring expert human judgment and institutional policy review.",
                "stages": {
                    "evaluator": {
                        "confidence_index": {
                            "overall_confidence": 25.0,
                            "confidence_level": "low",
                            "resolution_recommendation": "human_required"
                        }
                    }
                },
                "resolution_data": {
                    "resolved_by_human": True,
                    "human_processing_time": random.uniform(1800, 3600),  # 30-60 minutes
                    "human_resources_used": random.uniform(8.0, 15.0),
                    "human_accuracy": random.uniform(0.90, 0.98),
                    "human_review_date": datetime.now().isoformat(),
                    "human_decision": "escalated_to_administration",
                    "human_notes": "Complex case requiring administrative review and legal consultation.",
                    "resolution_status": "resolved_by_human"
                },
                "rl_metadata": {
                    "added_at": datetime.now().isoformat(),
                    "incident_number": len(incidents) + 1,
                    "processing_time": 0,
                    "resources_used": 0,
                    "confidence_analysis": {
                        "overall_confidence": 25.0,
                        "resolution_recommendation": "human_required"
                    },
                    "learning_applied": True,
                    "similar_incidents_count": 0,
                    "historical_context": {
                        "message": "Complex human-only incident"
                    }
                }
            },
            {
                "incident_id": f"HUMAN-{datetime.now().strftime('%Y%m%d%H%M%S')}-002",
                "incident_type": "crisis",
                "severity": "critical",
                "original_report": "Emergency situation requiring immediate human intervention and crisis management protocols.",
                "stages": {
                    "evaluator": {
                        "confidence_index": {
                            "overall_confidence": 15.0,
                            "confidence_level": "very_low",
                            "resolution_recommendation": "human_required"
                        }
                    }
                },
                "resolution_data": {
                    "resolved_by_human": True,
                    "human_processing_time": random.uniform(600, 1200),   # 10-20 minutes
                    "human_resources_used": random.uniform(10.0, 20.0),
                    "human_accuracy": random.uniform(0.95, 0.99),
                    "human_review_date": datetime.now().isoformat(),
                    "human_decision": "emergency_protocols_activated",
                    "human_notes": "Emergency response protocols activated. Multiple departments coordinated.",
                    "resolution_status": "resolved_by_human"
                },
                "rl_metadata": {
                    "added_at": datetime.now().isoformat(),
                    "incident_number": len(incidents) + 2,
                    "processing_time": 0,
                    "resources_used": 0,
                    "confidence_analysis": {
                        "overall_confidence": 15.0,
                        "resolution_recommendation": "human_required"
                    },
                    "learning_applied": True,
                    "similar_incidents_count": 0,
                    "historical_context": {
                        "message": "Critical human-only incident"
                    }
                }
            }
        ]
        
        # Add complex human incidents
        for incident in complex_human_incidents:
            rl_data['incidents'].append(incident)
            human_processed += 1
            
            print(f"   ✅ Added {incident['incident_id']}")
            print(f"      Confidence: {incident['stages']['evaluator']['confidence_index']['overall_confidence']}%")
            print(f"      Processing Time: {incident['resolution_data']['human_processing_time']/60:.1f} minutes")
        
        # Update learning stats
        rl_data['learning_stats']['total_incidents'] = len(rl_data['incidents'])
        rl_data['learning_stats']['ai_vs_human_comparisons'] += human_processed
        rl_data['learning_stats']['last_updated'] = datetime.now().isoformat()
        
        # Save updated data
        with open('rl_system_data.json', 'w') as f:
            json.dump(rl_data, f, indent=2, default=str)
        
        print(f"\n📊 Human Review Summary:")
        print(f"   👤 Human Processed: {human_processed}")
        print(f"   📈 Total Incidents: {len(rl_data['incidents'])}")
        print(f"   🔄 AI vs Human Comparisons: {rl_data['learning_stats']['ai_vs_human_comparisons']}")
        
        print(f"\n✅ Human review simulation complete!")
        print(f"   Performance tab will now show AI vs Human comparisons")
        print(f"   Time and resource savings will be calculated")
        
    except Exception as e:
        print(f"❌ Error simulating human review: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simulate_human_review()