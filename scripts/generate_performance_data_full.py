#!/usr/bin/env python3
import sys, os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
"""
Generate comprehensive performance data including:
- AI autonomous incidents
- Human review incidents  
- AI vs Human time/resource comparisons
- Real-time spam detection updates
"""
import requests
import json
import time
import random
from datetime import datetime, timedelta

def generate_comprehensive_data():
    """Generate comprehensive performance data for realistic AI vs Human analysis"""
    base_url = "http://localhost:8080"
    
    print("🎯 Generating Comprehensive Performance Data")
    print("=" * 60)
    print("📊 This will create:")
    print("   • AI autonomous incidents (high confidence)")
    print("   • Human review incidents (low confidence)")
    print("   • Mixed supervised incidents")
    print("   • Spam detection examples")
    print("   • Time and resource comparisons")
    print("=" * 60)
    
    # 1. HIGH CONFIDENCE AI INCIDENTS (Autonomous Resolution)
    ai_incidents = [
        {
            "report": "Routine maintenance: Classroom projector bulb replacement needed in Room 101. The projector is displaying a dim image and the bulb replacement indicator is showing. This is standard maintenance that occurs every 6 months. Replacement bulbs are available in the AV equipment room. The classroom can continue to be used with backup equipment until replacement is completed during the next maintenance window.",
            "metadata": {
                "incident_type": "maintenance",
                "severity": "low",
                "location": "Academic Building, Room 101",
                "anonymous": False,
                "contact_info": "av-support@university.edu",
                "priority": "routine",
                "equipment": "Epson PowerLite projector"
            },
            "expected": "AI Autonomous"
        },
        {
            "report": "Standard IT request: Password reset needed for faculty email account. Professor Smith forgot their password and needs access restored. This is a routine IT support request that follows standard verification procedures. The request can be processed through the normal IT helpdesk workflow with identity verification via employee ID and security questions.",
            "metadata": {
                "incident_type": "maintenance",
                "severity": "low", 
                "location": "Faculty Office Building",
                "anonymous": False,
                "contact_info": "prof.smith@university.edu",
                "priority": "routine",
                "department": "Computer Science"
            },
            "expected": "AI Autonomous"
        },
        {
            "report": "Routine cleaning request: Whiteboard markers in Lecture Hall C need replacement. Students reported that several markers are dried out and not writing properly. This is standard classroom maintenance that occurs regularly. Replacement markers are available in the supply closet and can be replaced during the next custodial round.",
            "metadata": {
                "incident_type": "maintenance",
                "severity": "low",
                "location": "Academic Building, Lecture Hall C",
                "anonymous": True,
                "contact_info": "",
                "priority": "routine"
            },
            "expected": "AI Autonomous"
        }
    ]
    
    # 2. LOW CONFIDENCE HUMAN REVIEW INCIDENTS
    human_incidents = [
        {
            "report": "Concerning behavior observed. A student has been acting strangely in recent weeks, making inappropriate comments during class and appearing agitated. Other students have expressed discomfort. The situation seems to be escalating and may require intervention from counseling services or administration. This is a sensitive matter that needs careful handling.",
            "metadata": {
                "incident_type": "behavioral",
                "severity": "high",
                "location": "Psychology Building",
                "anonymous": True,
                "contact_info": "",
                "priority": "urgent"
            },
            "expected": "Human Review"
        },
        {
            "report": "Potential discrimination incident. A student reported feeling targeted by an instructor based on their ethnicity. The student claims the instructor makes inappropriate comments and grades their work more harshly than other students. This requires careful investigation and may involve legal considerations.",
            "metadata": {
                "incident_type": "discrimination",
                "severity": "high",
                "location": "Business School",
                "anonymous": False,
                "contact_info": "student.affairs@university.edu",
                "priority": "urgent"
            },
            "expected": "Human Review"
        }
    ]
    
    # 3. MIXED SUPERVISED INCIDENTS
    supervised_incidents = [
        {
            "report": "Security concern: Unauthorized person was seen in the building after hours. Security cameras captured someone without proper ID badge accessing the research lab area around 11 PM. The person appeared to know the building layout. This may require investigation but could also be a faculty member who forgot their badge.",
            "metadata": {
                "incident_type": "security",
                "severity": "medium",
                "location": "Research Building",
                "anonymous": False,
                "contact_info": "security@university.edu",
                "priority": "medium"
            },
            "expected": "AI Supervised"
        },
        {
            "report": "Equipment malfunction: The HVAC system in the library is making loud noises and the temperature is fluctuating. Students are complaining about the noise during study hours. The system may need professional repair, but it's unclear if this is an emergency or can wait until regular maintenance hours.",
            "metadata": {
                "incident_type": "maintenance",
                "severity": "medium",
                "location": "Main Library",
                "anonymous": False,
                "contact_info": "facilities@university.edu",
                "priority": "medium"
            },
            "expected": "AI Supervised"
        }
    ]
    
    # 4. SPAM EXAMPLES (will be detected and blocked)
    spam_examples = [
        {
            "report": "FREE MONEY!!! Click here now to get rich quick! Amazing opportunity! Don't miss out! Act now!!!",
            "metadata": {
                "incident_type": "spam",
                "severity": "low",
                "location": "Online",
                "anonymous": True,
                "contact_info": ""
            },
            "expected": "Spam Blocked"
        },
        {
            "report": "asdfghjkl qwerty random keyboard mashing text that makes no sense whatsoever",
            "metadata": {
                "incident_type": "gibberish",
                "severity": "low", 
                "location": "Unknown",
                "anonymous": True,
                "contact_info": ""
            },
            "expected": "Gibberish Blocked"
        }
    ]
    
    all_incidents = [
        ("AI Autonomous", ai_incidents),
        ("Human Review", human_incidents), 
        ("AI Supervised", supervised_incidents),
        ("Spam/Gibberish", spam_examples)
    ]
    
    results = {
        "ai_autonomous": 0,
        "human_review": 0,
        "ai_supervised": 0,
        "spam_blocked": 0,
        "total_submitted": 0
    }
    
    # Submit all incidents
    for category, incidents in all_incidents:
        print(f"\n📋 Submitting {category} Incidents:")
        print("-" * 40)
        
        for i, incident in enumerate(incidents, 1):
            print(f"\n{i}. {incident['expected']} Incident:")
            print(f"   Type: {incident['metadata']['incident_type']}")
            print(f"   Severity: {incident['metadata']['severity']}")
            print(f"   Location: {incident['metadata']['location']}")
            
            try:
                response = requests.post(
                    f"{base_url}/api/v1/incidents/process",
                    json=incident,
                    timeout=30
                )
                
                results["total_submitted"] += 1
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('success'):
                        result = data.get('result', {})
                        status = result.get('status', 'N/A')
                        
                        print(f"   ✅ Success: {status}")
                        
                        if 'confidence_index' in result:
                            conf = result['confidence_index']
                            confidence_score = conf.get('overall_confidence', 0)
                            resolution = conf.get('resolution_recommendation', 'N/A')
                            
                            print(f"   📊 Confidence: {confidence_score:.1f}%")
                            print(f"   🎯 Resolution: {resolution}")
                            
                            # Count by actual resolution
                            if resolution == "autonomous":
                                results["ai_autonomous"] += 1
                                print(f"   🤖 AI AUTONOMOUS RESOLUTION")
                            elif resolution == "supervised":
                                results["ai_supervised"] += 1
                                print(f"   👥 AI SUPERVISED RESOLUTION")
                            else:
                                results["human_review"] += 1
                                print(f"   👤 HUMAN REVIEW REQUIRED")
                        else:
                            print(f"   ℹ️  No confidence analysis (likely processed)")
                    else:
                        # Check if it's spam
                        if data.get('status') == 'spam_detected':
                            results["spam_blocked"] += 1
                            print(f"   🛡️  SPAM BLOCKED: {data.get('reason', 'Detected as spam')}")
                        else:
                            print(f"   ❌ Failed: {data.get('error', 'Unknown error')}")
                else:
                    print(f"   ❌ HTTP Error: {response.status_code}")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
            
            # Delay between submissions
            time.sleep(2)
    
    print(f"\n" + "=" * 60)
    print(f"📊 SUBMISSION SUMMARY")
    print(f"=" * 60)
    print(f"🤖 AI Autonomous: {results['ai_autonomous']}")
    print(f"👥 AI Supervised: {results['ai_supervised']}")
    print(f"👤 Human Review: {results['human_review']}")
    print(f"🛡️  Spam Blocked: {results['spam_blocked']}")
    print(f"📈 Total Submitted: {results['total_submitted']}")
    
    # Wait for processing
    print(f"\n⏳ Waiting for performance analysis...")
    time.sleep(5)
    
    # Check final performance insights
    print(f"\n📈 FINAL PERFORMANCE INSIGHTS:")
    print("-" * 40)
    try:
        response = requests.get(f"{base_url}/api/v1/analytics/performance-insights", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                insights = data.get('insights', {})
                
                print(f"🤖 AI Incidents: {insights.get('ai_incidents', 0)}")
                print(f"👤 Human Incidents: {insights.get('human_incidents', 0)}")
                print(f"📊 Total Analyzed: {insights.get('total_incidents', 0)}")
                
                # AI Performance
                if insights.get('ai_performance'):
                    ai_perf = insights['ai_performance']
                    print(f"\n🤖 AI Performance:")
                    print(f"   ⚡ Avg Processing Time: {ai_perf.get('average_processing_time', 0):.1f}s")
                    print(f"   📊 Avg Resources Used: {ai_perf.get('average_resources_used', 0):.1f}")
                    print(f"   🎯 Avg Accuracy: {ai_perf.get('average_accuracy', 0)*100:.1f}%")
                    print(f"   ⭐ Efficiency Score: {ai_perf.get('efficiency_score', 0):.1f}")
                
                # Human Performance (if any)
                if insights.get('human_performance'):
                    human_perf = insights['human_performance']
                    print(f"\n👤 Human Performance:")
                    print(f"   ⏱️  Avg Processing Time: {human_perf.get('average_processing_time', 0):.1f}s")
                    print(f"   📊 Avg Resources Used: {human_perf.get('average_resources_used', 0):.1f}")
                    print(f"   🎯 Avg Accuracy: {human_perf.get('average_accuracy', 0)*100:.1f}%")
                    print(f"   ⭐ Efficiency Score: {human_perf.get('efficiency_score', 0):.1f}")
                
                # Efficiency Improvements
                if insights.get('ai_improvements'):
                    ai_imp = insights['ai_improvements']
                    print(f"\n💰 AI Efficiency Gains:")
                    print(f"   ⚡ Time Saved: {ai_imp.get('time_saved_percentage', 0):.1f}%")
                    print(f"   💎 Resources Saved: {ai_imp.get('resources_saved_percentage', 0):.1f}%")
                    print(f"   🚀 Overall Efficiency Gain: {ai_imp.get('overall_efficiency_gain', 0):.1f}")
                
                # Spam Detection
                if insights.get('spam_detection'):
                    spam = insights['spam_detection']
                    print(f"\n🛡️  Spam Detection:")
                    print(f"   📊 Total Patterns: {spam.get('total_spam_patterns', 0)}")
                    print(f"   🚫 Spam Detected: {spam.get('total_spam_detected', 0)}")
                    print(f"   🎯 Detection Accuracy: {spam.get('detection_accuracy', 0):.1f}%")
                    print(f"   ⚠️  False Positives: {spam.get('false_positives', 0)}")
                
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print(f"\n" + "=" * 60)
    print(f"🌐 PERFORMANCE TAB ACCESS:")
    print(f"=" * 60)
    print(f"📱 Main App: {base_url}")
    print(f"🎯 Performance Tab: {base_url}/performance")
    print(f"🧪 Test Page: {base_url}/test_performance.html")
    print(f"\n✨ The Performance tab now shows:")
    print(f"   • AI vs Human processing comparisons")
    print(f"   • Time and resource savings calculations")
    print(f"   • Real-time spam detection statistics")
    print(f"   • Learning progress and system maturity")
    print(f"   • Interactive performance visualizations")
    print("=" * 60)

if __name__ == "__main__":
    generate_comprehensive_data()