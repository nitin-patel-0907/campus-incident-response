#!/usr/bin/env python3
import sys, os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
"""
Generate comprehensive test data for Human Review Dashboard
Creates incidents requiring human oversight for safety and authenticity
"""
import requests
import json
import time
import random
from datetime import datetime, timedelta

def generate_human_review_test_data():
    """Generate test incidents that require human review for various reasons"""
    base_url = "http://localhost:8080"
    
    print("👤 Generating Human Review Test Data")
    print("=" * 60)
    print("🎯 Creating incidents requiring human oversight:")
    print("   • Anonymous reports with sensitive content")
    print("   • High-risk content requiring verification")
    print("   • Suspicious file uploads")
    print("   • Policy violation concerns")
    print("   • Critical incidents needing human judgment")
    print("=" * 60)
    
    # 1. ANONYMOUS REPORTS (Require human review due to anonymity)
    anonymous_reports = [
        {
            "report": "I witnessed harassment in the library yesterday evening. A student was being verbally abused by another student near the study area. The victim appeared distressed and left quickly. I didn't intervene because I was scared, but I think someone should know about this. The harasser was wearing a red jacket and seemed to be targeting the victim specifically.",
            "metadata": {
                "incident_type": "harassment",
                "severity": "high",
                "location": "Main Library Study Area",
                "anonymous": True,
                "contact_info": "",
                "priority": "urgent"
            },
            "expected": "Human Review - Anonymous Report"
        },
        {
            "report": "There's a professor in the Chemistry Department who has been making inappropriate comments to female students during office hours. Multiple students have mentioned this but are afraid to report it officially. The behavior includes personal questions about relationships and uncomfortable physical proximity. This needs to be investigated but students are worried about retaliation.",
            "metadata": {
                "incident_type": "misconduct",
                "severity": "high",
                "location": "Chemistry Department",
                "anonymous": True,
                "contact_info": "",
                "priority": "urgent"
            },
            "expected": "Human Review - Anonymous Report"
        },
        {
            "report": "I saw someone dealing drugs behind the dormitory last night around 11 PM. There were multiple people involved and money was exchanging hands. I took a photo but I'm afraid to come forward with my name because I live in the same building. The activity has been going on for weeks.",
            "metadata": {
                "incident_type": "illegal_activity",
                "severity": "critical",
                "location": "Student Dormitory - Rear Area",
                "anonymous": True,
                "contact_info": "",
                "priority": "critical"
            },
            "expected": "Human Review - Anonymous Report"
        }
    ]
    
    # 2. HIGH-RISK CONTENT (Require human review due to sensitive nature)
    high_risk_reports = [
        {
            "report": "A student in my psychology class has been talking about feeling hopeless and mentioned having thoughts of self-harm. They said they have access to their parent's medication and have been researching methods online. I'm really worried about them but they made me promise not to tell anyone. I don't know what to do but I think they need help immediately.",
            "metadata": {
                "incident_type": "mental_health",
                "severity": "critical",
                "location": "Psychology Building",
                "anonymous": False,
                "contact_info": "concerned.student@university.edu",
                "priority": "critical"
            },
            "expected": "Human Review - High-Risk Content"
        },
        {
            "report": "There was a heated argument in the engineering lab today that escalated to threats of violence. One student threatened to 'bring something to settle this' and mentioned knowing where the other student lives. The threatened student seemed genuinely scared. Security should be aware of this situation as it could escalate further.",
            "metadata": {
                "incident_type": "threat",
                "severity": "critical",
                "location": "Engineering Lab Building",
                "anonymous": False,
                "contact_info": "lab.supervisor@university.edu",
                "priority": "critical"
            },
            "expected": "Human Review - High-Risk Content"
        }
    ]
    
    # 3. SUSPICIOUS FILE SCENARIOS (Would require human review if files were uploaded)
    suspicious_file_reports = [
        {
            "report": "I'm reporting an incident of academic dishonesty. A student submitted work that appears to be AI-generated for their final project. I have screenshots of the original AI output and the submitted work side by side. The similarity is undeniable and this violates our academic integrity policy. This needs investigation.",
            "metadata": {
                "incident_type": "academic_dishonesty",
                "severity": "medium",
                "location": "Computer Science Department",
                "anonymous": False,
                "contact_info": "professor.smith@university.edu",
                "priority": "medium",
                "has_evidence_files": True,
                "file_description": "Screenshots comparing AI output to submitted work"
            },
            "expected": "Human Review - Evidence Files"
        },
        {
            "report": "I found disturbing graffiti in the bathroom that includes hate symbols and threatening language directed at specific minority groups. I took photos of the graffiti before reporting it. This appears to be a hate crime and needs immediate attention from administration and possibly law enforcement.",
            "metadata": {
                "incident_type": "hate_crime",
                "severity": "critical",
                "location": "Student Union Building - 2nd Floor Restroom",
                "anonymous": False,
                "contact_info": "security@university.edu",
                "priority": "critical",
                "has_evidence_files": True,
                "file_description": "Photos of hate graffiti"
            },
            "expected": "Human Review - Evidence Files"
        }
    ]
    
    # 4. POLICY VIOLATION CONCERNS (Complex cases requiring human judgment)
    policy_violation_reports = [
        {
            "report": "A faculty member has been consistently showing up to class intoxicated. Students have complained about the smell of alcohol, slurred speech, and inappropriate behavior during lectures. This has been ongoing for several weeks and is affecting the quality of education. Students are afraid to report this directly due to potential grade retaliation.",
            "metadata": {
                "incident_type": "faculty_misconduct",
                "severity": "high",
                "location": "Business School",
                "anonymous": False,
                "contact_info": "department.chair@university.edu",
                "priority": "high"
            },
            "expected": "Human Review - Policy Violation"
        },
        {
            "report": "There's a research ethics violation happening in the biology lab. A graduate student is being pressured by their advisor to falsify data in their thesis research. The student is afraid to speak up because their advisor controls their funding and graduation timeline. This involves federal research grants and could have serious consequences.",
            "metadata": {
                "incident_type": "research_misconduct",
                "severity": "critical",
                "location": "Biology Research Lab",
                "anonymous": True,
                "contact_info": "",
                "priority": "critical"
            },
            "expected": "Human Review - Research Ethics"
        }
    ]
    
    # 5. COMPLEX DISCRIMINATION CASES (Require careful human assessment)
    discrimination_reports = [
        {
            "report": "I believe I'm being discriminated against in my graduate program based on my religion. My advisor makes comments about my religious practices, schedules important meetings during my prayer times despite knowing my schedule, and has made remarks about my 'commitment' to science. Other students in the lab have noticed the different treatment. I have documentation of these incidents.",
            "metadata": {
                "incident_type": "religious_discrimination",
                "severity": "high",
                "location": "Graduate Research Building",
                "anonymous": False,
                "contact_info": "grad.student@university.edu",
                "priority": "high"
            },
            "expected": "Human Review - Discrimination Case"
        }
    ]
    
    all_test_cases = [
        ("Anonymous Reports", anonymous_reports),
        ("High-Risk Content", high_risk_reports),
        ("Evidence Files", suspicious_file_reports),
        ("Policy Violations", policy_violation_reports),
        ("Discrimination Cases", discrimination_reports)
    ]
    
    results = {
        "submitted": 0,
        "human_review_triggered": 0,
        "spam_blocked": 0,
        "processing_errors": 0
    }
    
    # Submit all test cases
    for category, test_cases in all_test_cases:
        print(f"\n📋 Submitting {category}:")
        print("-" * 40)
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{i}. {test_case['expected']}:")
            print(f"   Type: {test_case['metadata']['incident_type']}")
            print(f"   Severity: {test_case['metadata']['severity']}")
            print(f"   Location: {test_case['metadata']['location']}")
            print(f"   Anonymous: {test_case['metadata']['anonymous']}")
            
            try:
                response = requests.post(
                    f"{base_url}/api/v1/incidents/process",
                    json=test_case,
                    timeout=30
                )
                
                results["submitted"] += 1
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('success'):
                        result = data.get('result', {})
                        status = result.get('status', 'N/A')
                        
                        print(f"   ✅ Success: {status}")
                        
                        # Check if it triggered human review
                        if 'confidence_index' in result:
                            conf = result['confidence_index']
                            confidence_score = conf.get('overall_confidence', 0)
                            resolution = conf.get('resolution_recommendation', 'N/A')
                            
                            print(f"   📊 Confidence: {confidence_score:.1f}%")
                            print(f"   🎯 Resolution: {resolution}")
                            
                            if resolution in ["supervised", "human_required"]:
                                results["human_review_triggered"] += 1
                                print(f"   👤 HUMAN REVIEW TRIGGERED")
                            else:
                                print(f"   🤖 AI Processing: {resolution}")
                        
                        # Check for human review indicators in the result
                        if result.get('requires_human_review') or 'human_review' in str(result).lower():
                            results["human_review_triggered"] += 1
                            print(f"   👤 HUMAN REVIEW REQUIRED")
                        
                    else:
                        # Check if it's spam
                        if data.get('status') == 'spam_detected':
                            results["spam_blocked"] += 1
                            print(f"   🛡️  SPAM BLOCKED: {data.get('reason', 'Detected as spam')}")
                        else:
                            results["processing_errors"] += 1
                            print(f"   ❌ Failed: {data.get('error', 'Unknown error')}")
                else:
                    results["processing_errors"] += 1
                    print(f"   ❌ HTTP Error: {response.status_code}")
                    
            except Exception as e:
                results["processing_errors"] += 1
                print(f"   ❌ Error: {e}")
            
            # Delay between submissions
            time.sleep(2)
    
    print(f"\n" + "=" * 60)
    print(f"📊 TEST DATA GENERATION SUMMARY")
    print(f"=" * 60)
    print(f"📤 Total Submitted: {results['submitted']}")
    print(f"👤 Human Review Triggered: {results['human_review_triggered']}")
    print(f"🛡️  Spam Blocked: {results['spam_blocked']}")
    print(f"❌ Processing Errors: {results['processing_errors']}")
    
    # Wait for processing
    print(f"\n⏳ Waiting for human review queue to populate...")
    time.sleep(5)
    
    # Check human review queue
    print(f"\n📋 CHECKING HUMAN REVIEW QUEUE:")
    print("-" * 40)
    try:
        response = requests.get(f"{base_url}/api/v1/review/queue", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                queue = data.get('queue', [])
                summary = data.get('summary', {})
                
                print(f"📊 Queue Summary:")
                print(f"   ⏳ Pending Review: {summary.get('total_pending', 0)}")
                print(f"   👁️  In Review: {summary.get('total_in_review', 0)}")
                print(f"   ✅ Approved: {summary.get('total_approved', 0)}")
                print(f"   ❌ Rejected: {summary.get('total_rejected', 0)}")
                print(f"   🔒 Anonymous Reports: {summary.get('anonymous_reports', 0)}")
                print(f"   ⚠️  Suspicious Files: {summary.get('suspicious_files', 0)}")
                print(f"   🚨 High Priority: {summary.get('high_priority', 0)}")
                
                if queue:
                    print(f"\n📋 Recent Queue Items:")
                    for item in queue[:5]:  # Show first 5
                        print(f"   • {item.get('incident_id', 'N/A')} - {item.get('priority', 'N/A')} priority")
                        print(f"     Reasons: {', '.join(item.get('reasons', []))}")
                        print(f"     Status: {item.get('status', 'N/A')}")
                else:
                    print(f"   ℹ️  No items currently in review queue")
                    
            else:
                print(f"❌ API Error: {data.get('error', 'Unknown error')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking review queue: {e}")
    
    print(f"\n" + "=" * 60)
    print(f"🌐 HUMAN REVIEW DASHBOARD ACCESS:")
    print(f"=" * 60)
    print(f"📱 Main App: {base_url}")
    print(f"👤 Human Review: {base_url}/review")
    print(f"🎯 Direct Link: {base_url} → Click 'Human Review' in sidebar")
    print(f"\n✨ The Human Review Dashboard now includes:")
    print(f"   • Anonymous reports requiring verification")
    print(f"   • High-risk content needing human judgment")
    print(f"   • Evidence files requiring authenticity review")
    print(f"   • Policy violation cases needing investigation")
    print(f"   • Discrimination cases requiring careful assessment")
    print(f"   • Priority-based queue management")
    print(f"   • Comprehensive review workflow")
    print("=" * 60)

if __name__ == "__main__":
    generate_human_review_test_data()