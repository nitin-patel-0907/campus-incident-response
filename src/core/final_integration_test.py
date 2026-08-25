"""
Final integration test to verify the complete system works end-to-end
"""

import requests
import json
import time

def test_complete_workflow():
    """Test the complete workflow with different incident types"""
    
    test_cases = [
        {
            "name": "High Severity Medical Emergency",
            "data": {
                "report": """Incident Report:
        
Reporter: Emergency Responder (EMS-001)
Role: staff
Incident Type: medical
Severity: critical
Location: Gymnasium, Basketball Court
Date/Time: January 30, 2026

Description:
Student athlete collapsed during basketball practice. Unconscious, not breathing normally. CPR initiated by coach. Ambulance requested. Multiple witnesses present.""",
                "execution_mode": "simulate",
                "reporter_info": {
                    "name": "Emergency Responder",
                    "university_id": "EMS-001",
                    "role": "staff"
                },
                "metadata": {
                    "incident_type": "medical",
                    "severity": "critical",
                    "location": "Gymnasium, Basketball Court",
                    "date_time": "2026-01-30T15:45:00.000Z",
                    "form_submission": True
                }
            }
        },
        {
            "name": "Security Incident",
            "data": {
                "report": """Incident Report:
        
Reporter: Security Guard (SEC-123)
Role: staff
Incident Type: security
Severity: medium
Location: Parking Lot B
Date/Time: January 30, 2026

Description:
Suspicious individual observed taking photos of vehicles and license plates. When approached, person fled the scene. No direct threat but concerning behavior reported by multiple students.""",
                "execution_mode": "simulate",
                "reporter_info": {
                    "name": "Security Guard",
                    "university_id": "SEC-123",
                    "role": "staff"
                },
                "metadata": {
                    "incident_type": "security",
                    "severity": "medium",
                    "location": "Parking Lot B",
                    "date_time": "2026-01-30T15:50:00.000Z",
                    "form_submission": True
                }
            }
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 Test {i}: {test_case['name']}")
        print("-" * 50)
        
        try:
            response = requests.post(
                "http://localhost:8000/api/v1/incidents/process",
                json=test_case['data'],
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                workflow_result = result.get('result', {})
                
                print(f"✅ Workflow ID: {result['workflow_id']}")
                
                # Check incident analysis
                if 'incident_data' in workflow_result:
                    incident = workflow_result['incident_data']
                    print(f"✅ Incident Analysis:")
                    print(f"   Type: {incident.get('incident_type')}")
                    print(f"   Severity: {incident.get('severity')}")
                    print(f"   Priority: {incident.get('priority')}")
                    print(f"   Confidence: {incident.get('confidence_score', 0):.1f}%")
                
                # Check response plan
                if 'response_plan' in workflow_result:
                    plan = workflow_result['response_plan']
                    actions = plan.get('immediate_actions', [])
                    stakeholders = plan.get('stakeholders', [])
                    print(f"✅ Response Plan:")
                    print(f"   Plan Type: {plan.get('plan_type')}")
                    print(f"   Priority Level: {plan.get('priority_level')}")
                    print(f"   Immediate Actions: {len(actions)}")
                    print(f"   Stakeholders: {len(stakeholders)}")
                    
                    # Show first action as example
                    if actions:
                        first_action = actions[0]
                        print(f"   Sample Action: {first_action.get('description', '')[:60]}...")
                
                # Check processing stages
                stages = workflow_result.get('processing_stages', {})
                completed_stages = sum(1 for status in stages.values() if status == 'completed')
                print(f"✅ Processing: {completed_stages}/{len(stages)} stages completed")
                
                results.append({
                    'test_name': test_case['name'],
                    'success': True,
                    'workflow_id': result['workflow_id'],
                    'incident_type': incident.get('incident_type') if 'incident_data' in workflow_result else 'unknown',
                    'confidence': incident.get('confidence_score', 0) if 'incident_data' in workflow_result else 0
                })
                
            else:
                print(f"❌ Test failed: {response.status_code}")
                print(f"   Error: {response.text}")
                results.append({
                    'test_name': test_case['name'],
                    'success': False,
                    'error': f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"❌ Test error: {e}")
            results.append({
                'test_name': test_case['name'],
                'success': False,
                'error': str(e)
            })
    
    return results

def main():
    print("🚀 Final Integration Test")
    print("=" * 60)
    print("Testing complete workflow with multiple incident types")
    
    # Run tests
    results = test_complete_workflow()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    successful_tests = [r for r in results if r['success']]
    failed_tests = [r for r in results if not r['success']]
    
    print(f"✅ Successful Tests: {len(successful_tests)}/{len(results)}")
    print(f"❌ Failed Tests: {len(failed_tests)}/{len(results)}")
    
    if successful_tests:
        print(f"\n🎉 SUCCESSFUL TESTS:")
        for test in successful_tests:
            print(f"   ✅ {test['test_name']}")
            print(f"      Incident Type: {test['incident_type']}")
            print(f"      Confidence: {test['confidence']:.1f}%")
            print(f"      Workflow ID: {test['workflow_id']}")
    
    if failed_tests:
        print(f"\n❌ FAILED TESTS:")
        for test in failed_tests:
            print(f"   ❌ {test['test_name']}: {test['error']}")
    
    if len(successful_tests) == len(results):
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"The system is fully integrated and ready for use!")
        print(f"\n🌐 Access the application:")
        print(f"   Frontend: http://localhost:8080")
        print(f"   Backend API: http://localhost:8000")
        print(f"   API Docs: http://localhost:8000/docs")
    else:
        print(f"\n⚠️  Some tests failed. Please check the backend logs.")

if __name__ == "__main__":
    main()