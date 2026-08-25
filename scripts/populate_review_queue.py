#!/usr/bin/env python3
import sys, os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
"""
Directly populate the human review queue with test cases
"""
from datetime import datetime, timedelta
import random

def populate_review_queue_directly():
    """Add test cases directly to the human review service"""
    print("👤 Populating Human Review Queue Directly")
    print("=" * 50)
    
    try:
        from backend.services.human_review_service import human_review_service, ReviewReason
        
        # Test cases for human review queue
        test_cases = [
            {
                "incident_id": f"ANON-{datetime.now().strftime('%Y%m%d%H%M%S')}-001",
                "incident_data": {
                    "incident_type": "harassment",
                    "severity": "high",
                    "location": "Main Library Study Area",
                    "description": "I witnessed harassment in the library yesterday evening. A student was being verbally abused by another student near the study area. The victim appeared distressed and left quickly.",
                    "reporter_info": {
                        "anonymous": True,
                        "contact_info": "",
                        "pseudonymous_id": "ANON-001"
                    }
                },
                "reasons": [ReviewReason.ANONYMOUS_REPORT],
                "explanation": "Report submitted anonymously requiring verification",
                "file_analyses": []
            },
            {
                "incident_id": f"RISK-{datetime.now().strftime('%Y%m%d%H%M%S')}-002",
                "incident_data": {
                    "incident_type": "mental_health",
                    "severity": "critical",
                    "location": "Psychology Building",
                    "description": "A student in my psychology class has been talking about feeling hopeless and mentioned having thoughts of self-harm. They said they have access to medication and have been researching methods online.",
                    "reporter_info": {
                        "anonymous": False,
                        "contact_info": "concerned.student@university.edu",
                        "pseudonymous_id": None
                    }
                },
                "reasons": [ReviewReason.HIGH_RISK_CONTENT],
                "explanation": "Report contains high-risk content requiring careful human assessment",
                "file_analyses": []
            },
            {
                "incident_id": f"FILE-{datetime.now().strftime('%Y%m%d%H%M%S')}-003",
                "incident_data": {
                    "incident_type": "academic_dishonesty",
                    "severity": "medium",
                    "location": "Computer Science Department",
                    "description": "A student submitted work that appears to be AI-generated for their final project. I have screenshots of the original AI output and the submitted work side by side.",
                    "reporter_info": {
                        "anonymous": False,
                        "contact_info": "professor.smith@university.edu",
                        "pseudonymous_id": None
                    }
                },
                "reasons": [ReviewReason.SUSPICIOUS_FILE],
                "explanation": "Uploaded evidence files require authenticity verification",
                "file_analyses": [
                    {
                        "filename": "ai_comparison_screenshots.zip",
                        "authenticity_status": "Suspicious - Requires Verification",
                        "requires_human_review": True,
                        "summary": "Screenshots comparing AI output to submitted work",
                        "risk_factors": ["Potential evidence tampering", "Digital manipulation possible"],
                        "confidence_score": 45
                    }
                ]
            },
            {
                "incident_id": f"ANON-{datetime.now().strftime('%Y%m%d%H%M%S')}-004",
                "incident_data": {
                    "incident_type": "illegal_activity",
                    "severity": "critical",
                    "location": "Student Dormitory - Rear Area",
                    "description": "I saw someone dealing drugs behind the dormitory last night around 11 PM. There were multiple people involved and money was exchanging hands.",
                    "reporter_info": {
                        "anonymous": True,
                        "contact_info": "",
                        "pseudonymous_id": "ANON-004"
                    }
                },
                "reasons": [ReviewReason.ANONYMOUS_REPORT, ReviewReason.HIGH_RISK_CONTENT],
                "explanation": "Anonymous report with high-risk illegal activity content requiring verification",
                "file_analyses": []
            },
            {
                "incident_id": f"HATE-{datetime.now().strftime('%Y%m%d%H%M%S')}-005",
                "incident_data": {
                    "incident_type": "hate_crime",
                    "severity": "critical",
                    "location": "Student Union Building - 2nd Floor Restroom",
                    "description": "I found disturbing graffiti in the bathroom that includes hate symbols and threatening language directed at specific minority groups. I took photos of the graffiti.",
                    "reporter_info": {
                        "anonymous": False,
                        "contact_info": "security@university.edu",
                        "pseudonymous_id": None
                    }
                },
                "reasons": [ReviewReason.HIGH_RISK_CONTENT, ReviewReason.SUSPICIOUS_FILE],
                "explanation": "Hate crime report with photographic evidence requiring verification",
                "file_analyses": [
                    {
                        "filename": "graffiti_evidence_photos.jpg",
                        "authenticity_status": "Unverifiable - Missing Metadata",
                        "requires_human_review": True,
                        "summary": "Photos of alleged hate graffiti",
                        "risk_factors": ["Missing EXIF data", "Potential staging"],
                        "confidence_score": 30
                    }
                ]
            },
            {
                "incident_id": f"DISC-{datetime.now().strftime('%Y%m%d%H%M%S')}-006",
                "incident_data": {
                    "incident_type": "religious_discrimination",
                    "severity": "high",
                    "location": "Graduate Research Building",
                    "description": "I believe I'm being discriminated against in my graduate program based on my religion. My advisor makes comments about my religious practices and schedules meetings during my prayer times.",
                    "reporter_info": {
                        "anonymous": False,
                        "contact_info": "grad.student@university.edu",
                        "pseudonymous_id": None
                    }
                },
                "reasons": [ReviewReason.POLICY_VIOLATION],
                "explanation": "Discrimination case requiring careful policy review and investigation",
                "file_analyses": []
            }
        ]
        
        # Add test cases to review queue
        added_count = 0
        for test_case in test_cases:
            try:
                review_entry = human_review_service.add_to_review_queue(
                    incident_id=test_case["incident_id"],
                    incident_data=test_case["incident_data"],
                    reasons=test_case["reasons"],
                    explanation=test_case["explanation"],
                    file_analyses=test_case["file_analyses"]
                )
                
                print(f"✅ Added {test_case['incident_id']}")
                print(f"   Type: {test_case['incident_data']['incident_type']}")
                print(f"   Priority: {review_entry['priority']}")
                print(f"   Reasons: {', '.join([r.value for r in test_case['reasons']])}")
                
                added_count += 1
                
            except Exception as e:
                print(f"❌ Error adding {test_case['incident_id']}: {e}")
        
        # Get queue summary
        queue = human_review_service.get_review_queue()
        summary = human_review_service.get_review_summary()
        
        print(f"\n📊 Review Queue Summary:")
        print(f"   📋 Total Items: {len(queue)}")
        print(f"   ⏳ Pending: {summary['total_pending']}")
        print(f"   🚨 High Priority: {summary['high_priority']}")
        print(f"   ⚠️  Medium Priority: {summary['medium_priority']}")
        print(f"   ℹ️  Low Priority: {summary['low_priority']}")
        print(f"   🔒 Anonymous Reports: {summary['anonymous_reports']}")
        print(f"   📁 Suspicious Files: {summary['suspicious_files']}")
        
        print(f"\n✅ Successfully populated review queue with {added_count} test cases!")
        
    except Exception as e:
        print(f"❌ Error populating review queue: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    populate_review_queue_directly()