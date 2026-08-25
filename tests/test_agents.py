"""
Test Suite for Campus Incident Report Analysis System
Comprehensive tests for all agents and the orchestrator
"""
import sys
import os
import unittest
from datetime import datetime

# Add src directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from agents import (
    PromptAgent, PlannerAgent, ExecutorAgent, 
    SafetyPolicyAgent, EvaluatorAgent
)
from app.orchestrator import IncidentResponseOrchestrator


class TestPromptAgent(unittest.TestCase):
    """Test cases for Prompt Agent"""
    
    def setUp(self):
        self.agent = PromptAgent()
        self.sample_report = """
        On January 28, 2025, at approximately 2:30 PM, a student reported that their laptop 
        was stolen from the 3rd floor study room of the Main Library. The student, Sarah Johnson, 
        left her MacBook Pro unattended for about 15 minutes while she went to get coffee. 
        Upon returning, she discovered the laptop was missing.
        """
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        self.assertEqual(self.agent.name, "Prompt Agent")
        self.assertIsNotNone(self.agent.incident_types)
        self.assertIsNotNone(self.agent.severity_keywords)
    
    def test_process_valid_report(self):
        """Test processing a valid incident report"""
        input_data = {
            "raw_report": self.sample_report,
            "metadata": {"test": True}
        }
        
        result = self.agent.execute(input_data)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("structured_report", result)
        self.assertIn("extracted_entities", result)
        self.assertIn("completeness_score", result)
        
        # Check structured report content
        structured = result["structured_report"]
        self.assertEqual(structured["incident_type"], "theft")
        self.assertIn("laptop", structured["description"].lower())
    
    def test_process_empty_report(self):
        """Test processing empty report"""
        input_data = {"raw_report": ""}
        result = self.agent.execute(input_data)
        
        self.assertEqual(result["status"], "error")
        self.assertIn("error", result)
    
    def test_incident_classification(self):
        """Test incident type classification"""
        # Test theft classification
        theft_report = "Someone stole my laptop from the library"
        result = self.agent._classify_incident_type(theft_report.lower())
        self.assertEqual(result, "theft")
        
        # Test harassment classification
        harassment_report = "I am being harassed by another student"
        result = self.agent._classify_incident_type(harassment_report.lower())
        self.assertEqual(result, "harassment")
    
    def test_severity_classification(self):
        """Test severity classification"""
        # Test high severity
        critical_report = "emergency situation with severe injury"
        result = self.agent._classify_severity(critical_report.lower())
        self.assertEqual(result, "critical")
        
        # Test medium severity
        medium_report = "significant property damage occurred"
        result = self.agent._classify_severity(medium_report.lower())
        self.assertEqual(result, "high")


class TestPlannerAgent(unittest.TestCase):
    """Test cases for Planner Agent"""
    
    def setUp(self):
        self.agent = PlannerAgent()
        self.sample_structured_report = {
            "incident_type": "theft",
            "severity": "medium",
            "datetime": "January 28, 2025 at 2:30 PM",
            "location": "Main Library, 3rd floor",
            "description": "Laptop stolen from study room",
            "involved_parties": [{"name": "Sarah Johnson", "role": "student"}]
        }
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        self.assertEqual(self.agent.name, "Planner Agent")
        self.assertIsNotNone(self.agent.action_templates)
        self.assertIsNotNone(self.agent.stakeholder_mapping)
    
    def test_create_action_plan(self):
        """Test action plan creation"""
        input_data = {
            "structured_report": self.sample_structured_report,
            "extracted_entities": {"people": ["Sarah Johnson"]},
            "prompt_for_analysis": "Test prompt"
        }
        
        result = self.agent.execute(input_data)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("action_plan", result)
        self.assertIn("priority_level", result)
        
        # Check action plan structure
        plan = result["action_plan"]
        self.assertIn("immediate_actions", plan)
        self.assertIn("short_term_actions", plan)
        self.assertIn("long_term_actions", plan)
        self.assertIn("stakeholders", plan)
        self.assertIn("resources_needed", plan)
    
    def test_priority_determination(self):
        """Test priority level determination"""
        # Test critical priority
        critical_report = {"severity": "critical", "incident_type": "assault"}
        priority = self.agent._determine_priority(critical_report)
        self.assertEqual(priority, "critical")
        
        # Test medium priority
        medium_report = {"severity": "medium", "incident_type": "theft"}
        priority = self.agent._determine_priority(medium_report)
        self.assertEqual(priority, "medium")
    
    def test_stakeholder_identification(self):
        """Test stakeholder identification"""
        stakeholders = self.agent._identify_stakeholders(self.sample_structured_report, {})
        
        self.assertIsInstance(stakeholders, list)
        self.assertTrue(len(stakeholders) > 0)
        
        # Check stakeholder structure
        for stakeholder in stakeholders:
            self.assertIn("role", stakeholder)
            self.assertIn("notification_priority", stakeholder)


class TestSafetyPolicyAgent(unittest.TestCase):
    """Test cases for Safety Policy Agent"""
    
    def setUp(self):
        self.agent = SafetyPolicyAgent()
        self.sample_report = {
            "incident_type": "harassment",
            "severity": "high",
            "description": "Student harassment case"
        }
        self.sample_plan = {
            "immediate_actions": [
                {"action": "Investigate the incident thoroughly"}
            ],
            "stakeholders": [
                {"role": "Title IX Coordinator"}
            ]
        }
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        self.assertEqual(self.agent.name, "Safety and Policy Agent")
        self.assertIsNotNone(self.agent.policies)
        self.assertIsNotNone(self.agent.safety_rules)
    
    def test_policy_validation(self):
        """Test policy compliance validation"""
        input_data = {
            "structured_report": self.sample_report,
            "action_plan": self.sample_plan,
            "execution_summary": {}
        }
        
        result = self.agent.execute(input_data)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("validation_result", result)
        self.assertIn("policy_compliance", result)
        self.assertIn("safety_checks", result)
    
    def test_harmful_action_detection(self):
        """Test detection of harmful actions"""
        harmful_plan = {
            "immediate_actions": [
                {"action": "Punish the accused without investigation"}
            ]
        }
        
        harmful_check = self.agent._check_harmful_actions(harmful_plan)
        self.assertTrue(harmful_check["detected"])
        self.assertTrue(len(harmful_check["harmful_actions"]) > 0)


class TestExecutorAgent(unittest.TestCase):
    """Test cases for Executor Agent"""
    
    def setUp(self):
        self.agent = ExecutorAgent()
        self.sample_plan = {
            "immediate_actions": [
                {"action": "Contact campus security", "responsible": "Security"}
            ],
            "stakeholders": [
                {"role": "Campus Security", "notification_priority": "immediate"}
            ],
            "resources_needed": [
                {"resource": "Security personnel", "type": "personnel"}
            ]
        }
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        self.assertEqual(self.agent.name, "Executor Agent")
        self.assertIsInstance(self.agent.active_executions, dict)
    
    def test_execute_plan_simulate(self):
        """Test plan execution in simulate mode"""
        input_data = {
            "action_plan": self.sample_plan,
            "priority_level": "medium",
            "mode": "simulate"
        }
        
        result = self.agent.execute(input_data)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("execution_summary", result)
        self.assertIn("notifications_sent", result)
        self.assertIn("resources_allocated", result)
        
        # Check simulation mode
        summary = result["execution_summary"]
        self.assertEqual(summary["execution_mode"], "simulate")
        self.assertEqual(summary["overall_status"], "simulated")


class TestEvaluatorAgent(unittest.TestCase):
    """Test cases for Evaluator Agent"""
    
    def setUp(self):
        self.agent = EvaluatorAgent()
        self.sample_data = {
            "structured_report": {
                "incident_type": "theft",
                "severity": "medium",
                "location": "Library"
            },
            "action_plan": {
                "immediate_actions": [{"action": "Contact security"}],
                "stakeholders": [{"role": "Security"}]
            },
            "execution_summary": {
                "overall_status": "completed",
                "immediate_actions_executed": 1
            },
            "safety_validation": {
                "validation_result": "approved",
                "policy_compliance": {"overall_compliant": True},
                "safety_checks": {"all_checks_passed": True},
                "violations": []
            }
        }
    
    def test_agent_initialization(self):
        """Test agent initialization"""
        self.assertEqual(self.agent.name, "Evaluator Agent")
        self.assertIsNotNone(self.agent.evaluation_criteria)
    
    def test_evaluate_response(self):
        """Test response evaluation"""
        result = self.agent.execute(self.sample_data)
        
        self.assertEqual(result["status"], "success")
        self.assertIn("overall_score", result)
        self.assertIn("category_scores", result)
        self.assertIn("strengths", result)
        self.assertIn("weaknesses", result)
        self.assertIn("effectiveness_rating", result)
        
        # Check score is valid
        score = result["overall_score"]
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
    
    def test_effectiveness_rating(self):
        """Test effectiveness rating determination"""
        # Test excellent rating
        rating = self.agent._determine_effectiveness_rating(95)
        self.assertEqual(rating, "Excellent")
        
        # Test needs improvement rating
        rating = self.agent._determine_effectiveness_rating(45)
        self.assertEqual(rating, "Needs Improvement")


class TestOrchestrator(unittest.TestCase):
    """Test cases for the Orchestrator"""
    
    def setUp(self):
        self.orchestrator = IncidentResponseOrchestrator()
        self.sample_report = """
        On January 28, 2025, at approximately 2:30 PM, a student reported that their laptop 
        was stolen from the 3rd floor study room of the Main Library. The student, Sarah Johnson, 
        left her MacBook Pro unattended for about 15 minutes while she went to get coffee.
        """
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initialization"""
        self.assertIsNotNone(self.orchestrator.prompt_agent)
        self.assertIsNotNone(self.orchestrator.planner_agent)
        self.assertIsNotNone(self.orchestrator.executor_agent)
        self.assertIsNotNone(self.orchestrator.safety_agent)
        self.assertIsNotNone(self.orchestrator.evaluator_agent)
    
    def test_full_workflow_simulation(self):
        """Test complete workflow in simulation mode"""
        result = self.orchestrator.process_incident(
            raw_report=self.sample_report,
            metadata={"test": True},
            execution_mode="simulate"
        )
        
        self.assertEqual(result["status"], "success")
        self.assertIn("incident_id", result)
        self.assertIn("stages", result)
        
        # Check all stages completed
        stages = result["stages"]
        self.assertIn("prompt", stages)
        self.assertIn("planner", stages)
        self.assertIn("safety", stages)
        self.assertIn("executor", stages)
        self.assertIn("evaluator", stages)
        
        # Check each stage succeeded
        for stage_name, stage_result in stages.items():
            self.assertEqual(stage_result["status"], "success", 
                           f"Stage {stage_name} failed: {stage_result.get('error', 'Unknown error')}")
    
    def test_workflow_statistics(self):
        """Test workflow statistics"""
        # Process a test incident first
        self.orchestrator.process_incident(
            raw_report=self.sample_report,
            execution_mode="simulate"
        )
        
        stats = self.orchestrator.get_workflow_statistics()
        
        self.assertIn("total_incidents", stats)
        self.assertIn("successful", stats)
        self.assertIn("average_score", stats)
        self.assertEqual(stats["total_incidents"], 1)
        self.assertEqual(stats["successful"], 1)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        self.orchestrator = IncidentResponseOrchestrator()
    
    def test_multiple_incident_types(self):
        """Test processing different types of incidents"""
        incidents = [
            {
                "report": "Student laptop was stolen from the library",
                "expected_type": "theft"
            },
            {
                "report": "Student is being harassed by another student in the dormitory",
                "expected_type": "harassment"
            },
            {
                "report": "Student injured during basketball game, ankle appears broken",
                "expected_type": "medical"
            }
        ]
        
        for incident in incidents:
            result = self.orchestrator.process_incident(
                raw_report=incident["report"],
                execution_mode="simulate"
            )
            
            self.assertEqual(result["status"], "success")
            
            # Check incident type classification
            prompt_result = result["stages"]["prompt"]
            classified_type = prompt_result["structured_report"]["incident_type"]
            self.assertEqual(classified_type, incident["expected_type"])
    
    def test_error_handling(self):
        """Test error handling throughout the system"""
        # Test with invalid input
        result = self.orchestrator.process_incident(
            raw_report="",  # Empty report
            execution_mode="simulate"
        )
        
        self.assertEqual(result["status"], "error")
        self.assertIn("error", result)


def run_tests():
    """Run all tests and display results"""
    print("\n" + "="*80)
    print("🧪 CAMPUS INCIDENT ANALYSIS SYSTEM - TEST SUITE")
    print("="*80 + "\n")
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test cases
    test_classes = [
        TestPromptAgent,
        TestPlannerAgent,
        TestSafetyPolicyAgent,
        TestExecutorAgent,
        TestEvaluatorAgent,
        TestOrchestrator,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print("\n" + "="*80)
    print("📊 TEST RESULTS SUMMARY")
    print("="*80)
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\n❌ FAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  • {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0]}")
    
    if result.errors:
        print(f"\n🚨 ERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  • {test}: {traceback.split('\\n')[-2]}")
    
    if not result.failures and not result.errors:
        print("\n✅ ALL TESTS PASSED!")
    
    print("="*80 + "\n")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)