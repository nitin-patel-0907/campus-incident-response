#!/usr/bin/env python3
import sys, os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
"""
Create diverse human review test cases
"""
import requests
import time

def create_diverse_review_cases():
    """Create various types of incidents that should trigger human review"""
    base_url = "http://localhost:8080"
    
    print("👤 Creating Diverse Human Review Test Cases")
    print("=" * 60)
    
    # Test cases designed to trigger different review reasons
    test_cases = [
        {
            "name": "Anonymous Harassment Report",
            "data": {
                "report": "I saw a student being bullied and harassed in the cafeteria. The victim was being called names and had food thrown at them. Multiple students were involved in the harassment. I want to report this but I'm scared to give my name because I might become a target too.",
                "metadata": {
                    "incident_type": "harassment",
                    "severity": "high",
                    "location": "Student Cafeteria",
                    "anonymous": True,
                    "contact_info": "",
                    "priority": "urgent"
                }
            }
        },
        {
            "name": "Anonymous Drug Activity Report",
            "data": {
                "report": "There's been ongoing drug dealing in the dormitory parking lot. I've seen the same people meeting there late at night, exchanging money and small packages. It's been happening for weeks. I live in the dorm and I'm afraid to report this with my name because these people know where I live.",
                "metadata": {
                    "incident_type": "illegal_activity",
                    "severity": "critical",
                    "location": "Dormitory Parking Lot",
                    "anonymous": True,
                    "contact_info": "",
                    "priority": "critical"
                }
            }
        },
        {
            "name": "High-Risk Self-Harm Report",
            "data": {
                "report": "My roommate has been talking about wanting to hurt themselves. They mentioned having pills and said they've been looking up methods online. They seem really depressed and hopeless. I found some concerning notes in their room. I'm really scared for them and don't know what to do. This seems like an emergency.",
                "metadata": {
                    "incident_type": "mental_health",
                    "severity": "critical",
                    "location": "Student Dormitory Room 204",
                    "anonymous": False,
                    "contact_info": "worried.roommate@university.edu",
                    "priority": "critical"
                }
            }
        },
        {
            "name": "Threat of Violence Report",
            "data": {
                "report": "A student in my engineering class made threats against another student today. They said they were going to 'make them pay' and mentioned knowing where they live. The threatened student looked genuinely scared. The person making threats seemed very angry and mentioned having access to tools and weapons through their family's business.",
                "metadata": {
                    "incident_type": "threat",
                    "severity": "critical",
                    "location": "Engineering Building - Lab 3",
                    "anonymous": False,
                    "contact_info": "lab.witness@university.edu",
                    "priority": "critical"
                }
            }
        },
        {
            "name": "Anonymous Faculty Misconduct",
            "data": {
                "report": "A professor in the Business School has been making inappropriate comments to female students and creating a hostile environment. Multiple students have mentioned this but are afraid to report it officially because they're worried about their grades. The behavior includes personal questions about relationships and inappropriate touching during office hours.",
                "metadata": {
                    "incident_type": "faculty_misconduct",
                    "severity": "high",
                    "location": "Business School Faculty Offices",
                    "anonymous": True,
                    "contact_info": "",
                    "priority": "high"
                }
            }
        },
        {
            "name": "Hate Crime with Evidence",
            "data": {
                "report": "I found hate graffiti in the library bathroom that targets specific ethnic groups with threatening language and symbols. I took photos before cleaning it off. This is clearly a hate crime and needs to be investigated. The graffiti was fresh and appeared to be done recently.",
                "metadata": {
                    "incident_type": "hate_crime",
                    "severity": "critical",
                    "location": "Main Library - 3rd Floor Restroom",
                    "anonymous": False,
                    "contact_info": "library.staff@university.edu",
                    "priority": "critical",
                    "has_evidence_files": True,
                    "file_description": "Photos of hate graffiti"
                }
            }
        },
        {
            "name": "Research Ethics Violation",
            "data": {
                "report": "I'm a graduate student and my advisor is pressuring me to falsify data in my research to get better results for publication. They said that 'everyone does it' and that I need to 'be more creative' with my data analysis. This involves federal grant money and could have serious consequences. I'm afraid to speak up because they control my funding and graduation.",
                "metadata": {
                    "incident_type": "research_misconduct",
                    "severity": "critical",
                    "location": "Graduate Research Lab",
                    "anonymous": True,
                    "contact_info": "",
                    "priority": "critical"
                }
            }
        },
        {
            "name": "Discrimination Case",
            "data": {
                "report": "I believe I'm being discriminated against by my department chair based on my race. They consistently give me the worst teaching assignments, exclude me from important meetings, and make comments about my 'cultural fit' in the department. Other faculty have noticed the different treatment. I have documentation of these incidents over the past semester.",
                "metadata": {
                    "incident_type": "racial_discrimination",
                    "severity": "high",
                    "location": "Academic Department Office",
                    "anonymous": False,
                    "contact_info": "faculty.member@university.edu",
                    "priority": "high"
                }
            }
        }
    ]
    
    results = {
        "submitted": 0,
        "human_review_triggered": 0,
        "errors": 0
    }
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Submitting: {test_case['name']}")
        print(f"   Type: {test_case['data']['metadata']['incident_type']}")
        print(f"   Severity: {test_case['data']['metadata']['severity']}")
        print(f"   Anonymous: {test_case['data']['metadata'].get('anonymous', False)}")
        
        try:
            response = requests.post(
                f"{base_url}/api/v1/incidents/process",
                json=test_case['data'],
                timeout=30
            )
            
            results["submitted"] += 1
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('success'):
                    result = data.get('result', {})
                    print(f"   ✅ Success: {result.get('status', 'N/A')}")
                    
                    # Check for human review
                    if result.get('human_review_required'):
                        results["human_review_triggered"] += 1
                        print(f"   👤 HUMAN REVIEW TRIGGERED!")
                        print(f"   Reasons: {', '.join(result.get('review_reasons', []))}")
                        print(f"   Priority: {result.get('review_priority', 'N/A')}")
                    else:
                        print(f"   🤖 AI Processing")
                        if 'confidence_index' in result:
                            conf = result['confidence_index']
                            print(f"   Confidence: {conf.get('overall_confidence', 0):.1f}%")
                else:
                    results["errors"] += 1
                    print(f"   ❌ Failed: {data.get('error', 'Unknown error')}")
            else:
                results["errors"] += 1
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            results["errors"] += 1
            print(f"   ❌ Error: {e}")
        
        time.sleep(2)  # Delay between submissions
    
    # Check final queue status
    print(f"\n" + "=" * 60)
    print(f"📊 SUBMISSION RESULTS")
    print(f"=" * 60)
    print(f"📤 Total Submitted: {results['submitted']}")
    print(f"👤 Human Review Triggered: {results['human_review_triggered']}")
    print(f"❌ Errors: {results['errors']}")
    
    # Get final queue status
    print(f"\n📋 FINAL REVIEW QUEUE STATUS:")
    try:
        response = requests.get(f"{base_url}/api/v1/review/queue", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            queue = data.get('queue', [])
            summary = data.get('summary', {})
            
            print(f"   📊 Queue Summary:")
            print(f"   Total Items: {len(queue)}")
            print(f"   Pending Review: {summary.get('total_pending', 0)}")
            print(f"   High Priority: {summary.get('high_priority', 0)}")
            print(f"   Medium Priority: {summary.get('medium_priority', 0)}")
            print(f"   Anonymous Reports: {summary.get('anonymous_reports', 0)}")
            print(f"   Suspicious Files: {summary.get('suspicious_files', 0)}")
            
            if queue:
                print(f"\n   📋 Queue Items:")
                for item in queue:
                    print(f"   • {item.get('incident_id', 'N/A')} - {item.get('priority', 'N/A')} priority")
                    print(f"     Type: {item.get('incident_data', {}).get('incident_type', 'N/A')}")
                    print(f"     Reasons: {', '.join(item.get('reasons', []))}")
                    print(f"     Status: {item.get('status', 'N/A')}")
                    print()
            
        else:
            print(f"   ❌ Error getting queue: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n" + "=" * 60)
    print(f"🌐 ACCESS HUMAN REVIEW DASHBOARD:")
    print(f"=" * 60)
    print(f"📱 Main App: {base_url}")
    print(f"👤 Human Review: {base_url}/review")
    print(f"\n✨ The dashboard now includes diverse test cases:")
    print(f"   • Anonymous harassment and illegal activity reports")
    print(f"   • High-risk mental health and threat situations")
    print(f"   • Faculty misconduct and research ethics violations")
    print(f"   • Hate crimes with evidence files")
    print(f"   • Discrimination cases requiring investigation")
    print("=" * 60)

if __name__ == "__main__":
    create_diverse_review_cases()