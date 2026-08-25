#!/usr/bin/env python3
import sys, os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
"""
Generate realistic performance data for the Performance tab
"""
import requests
import json
import time
import random
from datetime import datetime, timedelta

def generate_performance_data():
    """Generate realistic incidents with varying confidence levels to create performance data"""
    base_url = "http://localhost:8080"
    
    print("🎯 Generating Performance Data for Performance Tab")
    print("=" * 60)
    
    # Test incidents with different confidence levels and types
    test_incidents = [
        {
            "report": "Emergency: Fire alarm activated in the chemistry building. Students and faculty are evacuating. Fire department has been notified.",
            "metadata": {
                "incident_type": "emergency",
                "severity": "critical",
                "location": "Chemistry Building",
                "anonymous": False,
                "contact_info": "security@university.edu"
            },
            "expected_confidence": "high"
        },
        {
            "report": "A student reported that their laptop was stolen from the library while they were away for 10 minutes. The laptop was left unattended on a table.",
            "metadata": {
                "incident_type": "theft",
                "severity": "medium",
                "location": "Main Library",
                "anonymous": False,
                "contact_info": "student@university.edu"
            },
            "expected_confidence": "medium"
        },
        {
            "report": "Maintenance issue: The elevator in the dormitory has been making strange noises and stopped working properly. Students are having difficulty accessing upper floors.",
            "metadata": {
                "incident_type": "maintenance",
                "severity": "low",
                "location": "Student Dormitory",
                "anonymous": True,
                "contact_info": ""
            },
            "expected_confidence": "high"
        },
        {
            "report": "Suspicious individual was seen loitering around the parking lot late at night. They appeared to be looking into car windows and trying door handles.",
            "metadata": {
                "incident_type": "security",
                "severity": "high",
                "location": "Parking Lot B",
                "anonymous": True,
                "contact_info": ""
            },
            "expected_confidence": "medium"
        },
        {
            "report": "Water leak in the basement of the science building. The leak appears to be getting worse and may affect electrical equipment.",
            "metadata": {
                "incident_type": "maintenance",
                "severity": "high",
                "location": "Science Building Basement",
                "anonymous": False,
                "contact_info": "facilities@university.edu"
            },
            "expected_confidence": "high"
        }
    ]
    
    successful_submissions = 0
    
    for i, incident in enumerate(test_incidents, 1):
        print(f"\n{i}. Submitting {incident['expected_confidence']} confidence incident...")
        print(f"   Type: {incident['metadata']['incident_type']}")
        print(f"   Severity: {incident['metadata']['severity']}")
        print(f"   Location: {incident['metadata']['location']}")
        
        try:
            response = requests.post(
                f"{base_url}/api/v1/incidents/process",
                json=incident,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    result = data.get('result', {})
                    print(f"   ✅ Success: {result.get('status', 'N/A')}")
                    
                    if 'confidence_index' in result:
                        conf = result['confidence_index']
                        print(f"   📊 Confidence: {conf.get('overall_confidence', 0):.1f}%")
                        print(f"   🎯 Resolution: {conf.get('resolution_recommendation', 'N/A')}")
                    
                    successful_submissions += 1
                else:
                    print(f"   ❌ Failed: {data.get('error', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        # Small delay between submissions
        time.sleep(1)
    
    print(f"\n📊 Summary:")
    print(f"   Total Incidents Submitted: {len(test_incidents)}")
    print(f"   Successful Submissions: {successful_submissions}")
    
    # Wait a moment for processing
    print(f"\n⏳ Waiting for processing to complete...")
    time.sleep(3)
    
    # Check performance insights
    print(f"\n📈 Checking Performance Insights...")
    try:
        response = requests.get(f"{base_url}/api/v1/analytics/performance-insights", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                insights = data.get('insights', {})
                print(f"   ✅ Performance Data Available:")
                print(f"   AI Incidents: {insights.get('ai_incidents', 0)}")
                print(f"   Human Incidents: {insights.get('human_incidents', 0)}")
                
                if insights.get('ai_improvements'):
                    ai_imp = insights['ai_improvements']
                    print(f"   Time Saved: {ai_imp.get('time_saved_percentage', 0):.1f}%")
                    print(f"   Resources Saved: {ai_imp.get('resources_saved_percentage', 0):.1f}%")
                
                if insights.get('spam_detection'):
                    spam = insights['spam_detection']
                    print(f"   Spam Patterns: {spam.get('total_spam_patterns', 0)}")
                    print(f"   Detection Accuracy: {spam.get('detection_accuracy', 0):.1f}%")
            else:
                print(f"   ❌ API Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n" + "=" * 60)
    print(f"🌐 Performance Tab Access:")
    print(f"   Main App: {base_url}")
    print(f"   Performance Tab: {base_url}/performance")
    print(f"   Test Page: {base_url}/test_performance.html")
    print(f"\n✨ The Performance tab should now show meaningful data!")
    print(f"   - Performance metrics comparing AI vs Human processing")
    print(f"   - Learning progress and system maturity")
    print(f"   - Spam detection statistics and patterns")
    print("=" * 60)

if __name__ == "__main__":
    generate_performance_data()