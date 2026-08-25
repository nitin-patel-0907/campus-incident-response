#!/usr/bin/env python3
import sys, os; sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
"""
Demo Script for Campus Incident Report Analysis System
Quick demonstration of the multi-agent workflow
"""
import sys
import os

from app.orchestrator import IncidentResponseOrchestrator


def main():
    """Run demo"""
    print("\n" + "="*80)
    print("🎬 CAMPUS INCIDENT REPORT ANALYSIS SYSTEM - DEMO")
    print("="*80)
    print("\nMulti-Agent AI System Demonstration")
    print("This demo will process sample incidents through all 5 agents")
    print("="*80 + "\n")
    
    # Initialize orchestrator
    orchestrator = IncidentResponseOrchestrator()
    
    # Demo incidents
    demo_incidents = [
        {
            "title": "📚 Theft in Library",
            "report": """On January 28, 2025, at approximately 2:30 PM, a student reported that their laptop was stolen from the 3rd floor study room of the Main Library. The student, Sarah Johnson, left her MacBook Pro unattended for about 15 minutes while she went to get coffee. Upon returning, she discovered the laptop was missing. The laptop was a silver 2023 MacBook Pro valued at approximately $2,500. Security footage is being reviewed."""
        },
        {
            "title": "⚠️ Harassment Case",
            "report": """On January 29, 2025, a freshman student, Alex Chen, filed a complaint about ongoing harassment by another student in their dormitory. The complainant reports receiving threatening text messages and experiencing verbal harassment in common areas over the past two weeks. The harassment includes derogatory comments about their ethnicity and religion. Alex feels unsafe in the dormitory and has requested immediate intervention. A witness has come forward corroborating some of the incidents."""
        }
    ]
    
    # Process each demo incident
    for i, incident in enumerate(demo_incidents, 1):
        print(f"\n{'='*80}")
        print(f"DEMO {i}/{len(demo_incidents)}: {incident['title']}")
        print(f"{'='*80}\n")
        
        print("📄 Incident Report:")
        print("-" * 80)
        print(incident['report'][:200] + "...")
        print("-" * 80 + "\n")
        
        input("Press Enter to start multi-agent analysis...")
        
        # Process incident
        result = orchestrator.process_incident(
            raw_report=incident['report'],
            metadata={"demo": True, "demo_number": i},
            execution_mode="simulate"
        )
        
        if result.get("status") == "success":
            print("\n" + "="*80)
            print("✅ DEMO COMPLETE - Analysis Successful!")
            print("="*80)
            
            evaluator = result["stages"]["evaluator"]
            print(f"\n📊 Quick Results:")
            print(f"   • Overall Score: {evaluator['overall_score']}/100")
            print(f"   • Rating: {evaluator['effectiveness_rating']}")
            print(f"   • Incident ID: {result['incident_id']}")
            print(f"   • Duration: {result['total_duration']:.2f} seconds")
            
            print(f"\n💪 Top Strengths:")
            for strength in evaluator['strengths'][:2]:
                print(f"   • {strength['category']}: {strength['score']}/100")
            
            if evaluator['weaknesses']:
                print(f"\n⚠️ Areas to Improve:")
                for weakness in evaluator['weaknesses'][:2]:
                    print(f"   • {weakness['category']}: {weakness['score']}/100")
        else:
            print(f"\n❌ Error: {result.get('error')}")
        
        if i < len(demo_incidents):
            print("\n" + "-"*80)
            input("\nPress Enter to continue to next demo...")
    
    # Final statistics
    print("\n" + "="*80)
    print("📈 DEMO SESSION STATISTICS")
    print("="*80 + "\n")
    
    stats = orchestrator.get_workflow_statistics()
    print(f"Total Incidents Processed: {stats['total_incidents']}")
    print(f"Success Rate: {stats['successful']}/{stats['total_incidents']}")
    print(f"Average Score: {stats['average_score']}/100")
    
    if stats.get('incident_types'):
        print(f"\nIncident Types Analyzed:")
        for itype, count in stats['incident_types'].items():
            print(f"   • {itype}: {count}")
    
    print("\n" + "="*80)
    print("🎉 DEMO COMPLETE!")
    print("="*80)
    print("\nNext Steps:")
    print("   1. Try the web interface: python app/app.py")
    print("   2. Use the CLI: python app/cli.py")
    print("   3. Run tests: python tests/test_agents.py")
    print("   4. Read the README.md for full documentation")
    print("\n" + "="*80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Demo error: {str(e)}")