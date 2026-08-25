#!/usr/bin/env python3
import sys, os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
"""
Generate high-confidence incidents that will trigger autonomous AI resolution
"""
import requests
import json
import time

def generate_high_confidence_data():
    """Generate incidents designed to achieve high confidence scores (>75%)"""
    base_url = "http://localhost:8080"
    
    print("🎯 Generating High-Confidence Incidents for AI Autonomous Resolution")
    print("=" * 70)
    
    # High-confidence incidents with clear, detailed descriptions
    high_confidence_incidents = [
        {
            "report": "Routine maintenance request: The fluorescent light in Room 204 of the Mathematics Building is flickering and needs replacement. This is a standard maintenance issue that occurs regularly. The room number is clearly marked, and the issue is straightforward. Maintenance staff can access the room during normal business hours. No safety hazards are present, and this is a low-priority routine repair that can be scheduled during the next available maintenance window.",
            "metadata": {
                "incident_type": "maintenance",
                "severity": "low",
                "location": "Mathematics Building, Room 204",
                "anonymous": False,
                "contact_info": "facilities@university.edu",
                "priority": "routine",
                "safety_risk": "none"
            }
        },
        {
            "report": "Standard IT support request: A faculty member in the Computer Science Department reports that their office printer (HP LaserJet Pro in Room CS-301) is displaying a 'toner low' warning message. This is a routine maintenance issue that requires toner cartridge replacement. The printer model is HP LaserJet Pro 4025n, and replacement toner cartridges are available in the IT supply room. The printer is still functional but will need toner replacement within the next few days. This is a standard, low-priority maintenance request that can be handled through normal IT support channels.",
            "metadata": {
                "incident_type": "maintenance",
                "severity": "low",
                "location": "Computer Science Building, Room CS-301",
                "anonymous": False,
                "contact_info": "it-support@university.edu",
                "equipment": "HP LaserJet Pro 4025n",
                "priority": "routine"
            }
        },
        {
            "report": "Routine cleaning request: The whiteboard in Lecture Hall B needs cleaning. Students have reported that the whiteboard markers are not erasing properly due to buildup of marker residue. This is a standard cleaning issue that occurs regularly in high-use classrooms. The custodial staff can address this during their regular cleaning schedule using standard whiteboard cleaning solution. No special equipment or urgent response is required. This is a low-priority routine maintenance item that can be completed during the next scheduled cleaning cycle.",
            "metadata": {
                "incident_type": "maintenance",
                "severity": "low",
                "location": "Academic Building, Lecture Hall B",
                "anonymous": False,
                "contact_info": "custodial@university.edu",
                "issue_type": "cleaning",
                "priority": "routine"
            }
        }
    ]
    
    successful_autonomous = 0
    total_submitted = 0
    
    for i, incident in enumerate(high_confidence_incidents, 1):
        print(f"\n{i}. Submitting high-confidence incident...")
        print(f"   Type: {incident['metadata']['incident_type']}")
        print(f"   Location: {incident['metadata']['location']}")
        print(f"   Expected: Autonomous AI resolution")
        
        try:
            response = requests.post(
                f"{base_url}/api/v1/incidents/process",
                json=incident,
                timeout=30
            )
            
            total_submitted += 1
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    result = data.get('result', {})
                    print(f"   ✅ Success: {result.get('status', 'N/A')}")
                    
                    if 'confidence_index' in result:
                        conf = result['confidence_index']
                        confidence_score = conf.get('overall_confidence', 0)
                        resolution = conf.get('resolution_recommendation', 'N/A')
                        
                        print(f"   📊 Confidence: {confidence_score:.1f}%")
                        print(f"   🎯 Resolution: {resolution}")
                        
                        if resolution == "autonomous":
                            successful_autonomous += 1
                            print(f"   🤖 AI AUTONOMOUS RESOLUTION ACHIEVED!")
                        elif confidence_score >= 70:
                            print(f"   ⚡ High confidence but supervised resolution")
                        else:
                            print(f"   ⚠️  Lower confidence - needs optimization")
                    
                else:
                    print(f"   ❌ Failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(2)  # Longer delay for processing
    
    print(f"\n📊 Results Summary:")
    print(f"   Total Incidents: {total_submitted}")
    print(f"   Autonomous AI Resolutions: {successful_autonomous}")
    print(f"   Success Rate: {(successful_autonomous/total_submitted*100) if total_submitted > 0 else 0:.1f}%")
    
    # Wait for processing
    print(f"\n⏳ Waiting for performance analysis...")
    time.sleep(5)
    
    # Check performance insights
    print(f"\n📈 Performance Insights Check:")
    try:
        response = requests.get(f"{base_url}/api/v1/analytics/performance-insights", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                insights = data.get('insights', {})
                
                ai_incidents = insights.get('ai_incidents', 0)
                human_incidents = insights.get('human_incidents', 0)
                
                print(f"   🤖 AI Incidents: {ai_incidents}")
                print(f"   👤 Human Incidents: {human_incidents}")
                
                if ai_incidents > 0:
                    print(f"   ✅ SUCCESS: AI autonomous incidents detected!")
                    
                    if insights.get('ai_performance'):
                        ai_perf = insights['ai_performance']
                        print(f"   ⚡ AI Avg Processing Time: {ai_perf.get('average_processing_time', 0):.1f}s")
                        print(f"   📊 AI Efficiency Score: {ai_perf.get('efficiency_score', 0):.1f}")
                    
                    if insights.get('ai_improvements'):
                        ai_imp = insights['ai_improvements']
                        print(f"   💰 Time Saved: {ai_imp.get('time_saved_percentage', 0):.1f}%")
                        print(f"   🎯 Resources Saved: {ai_imp.get('resources_saved_percentage', 0):.1f}%")
                else:
                    print(f"   ⚠️  No AI autonomous incidents yet - confidence scores may need adjustment")
                
                # Spam detection stats
                if insights.get('spam_detection'):
                    spam = insights['spam_detection']
                    print(f"   🛡️  Spam Patterns: {spam.get('total_spam_patterns', 0)}")
                    print(f"   🎯 Detection Accuracy: {spam.get('detection_accuracy', 0):.1f}%")
                    
            else:
                print(f"   ❌ API Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n" + "=" * 70)
    print(f"🌐 Performance Tab Access:")
    print(f"   Main App: {base_url}")
    print(f"   Performance Tab: {base_url}/performance")
    print(f"\n💡 Tips for Higher Confidence Scores:")
    print(f"   - Use detailed, specific descriptions")
    print(f"   - Include clear location information")
    print(f"   - Specify routine/standard maintenance items")
    print(f"   - Provide contact information")
    print(f"   - Use low-severity, straightforward incidents")
    print("=" * 70)

if __name__ == "__main__":
    generate_high_confidence_data()