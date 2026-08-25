"""
CLI Interface for Campus Incident Report Analysis System
"""
import sys
import os
from datetime import datetime


from app.orchestrator import IncidentResponseOrchestrator


def print_banner():
    """Print application banner"""
    print("\n" + "="*80)
    print("🚨 CAMPUS INCIDENT REPORT ANALYSIS SYSTEM - CLI")
    print("="*80)
    print("\nMulti-Agent AI System for Incident Response and Analysis")
    print("="*80 + "\n")


def print_menu():
    """Print main menu"""
    print("\n📋 MAIN MENU:")
    print("  1. Analyze new incident report")
    print("  2. View incident history")
    print("  3. View statistics")
    print("  4. Export incident report")
    print("  5. Load example incident")
    print("  6. About the system")
    print("  7. Exit")
    print()


def get_example_reports():
    """Get example incident reports"""
    return {
        "1": {
            "title": "Theft in Library",
            "report": """On January 28, 2025, at approximately 2:30 PM, a student reported that their laptop was stolen from the 3rd floor study room of the Main Library. The student, Sarah Johnson, left her MacBook Pro unattended for about 15 minutes while she went to get coffee. Upon returning, she discovered the laptop was missing. The laptop was a silver 2023 MacBook Pro valued at approximately $2,500. Security footage is being reviewed."""
        },
        "2": {
            "title": "Harassment Case",
            "report": """On January 29, 2025, a freshman student, Alex Chen, filed a complaint about ongoing harassment by another student in their dormitory. The complainant reports receiving threatening text messages and experiencing verbal harassment in common areas over the past two weeks. The harassment includes derogatory comments about their ethnicity and religion. Alex feels unsafe in the dormitory and has requested immediate intervention. A witness has come forward corroborating some of the incidents."""
        },
        "3": {
            "title": "Medical Emergency",
            "report": """On January 30, 2025, at 4:15 PM, during an intramural basketball game at the Recreation Center, a student athlete, Michael Torres, suffered an ankle injury after landing awkwardly following a jump. The student is experiencing severe pain and cannot bear weight on the affected foot. The game was immediately stopped. Campus EMT was called, and the student is currently being evaluated. Other team members witnessed the incident."""
        },
        "4": {
            "title": "Vandalism in Dormitory",
            "report": """On January 30, 2025, around 11:00 PM, vandalism was discovered in the East Wing dormitory common area. Multiple walls were spray-painted with graffiti, and furniture was overturned. The damage is estimated at $3,000. No witnesses have come forward yet, but the building has security cameras that may have captured the incident. Residents are concerned about safety and security."""
        },
        "5": {
            "title": "Policy Violation - Unauthorized Party",
            "report": """On January 27, 2025, at 1:30 AM, campus security responded to noise complaints at West Residence Hall. Upon arrival, they discovered an unauthorized party with approximately 50 students in a single dorm room. Alcohol was present, and several attendees appeared to be underage. The party violated multiple campus policies including quiet hours, room capacity limits, and alcohol regulations. Residents were dispersed, and the room occupants will face disciplinary action."""
        }
    }


def analyze_incident_interactive(orchestrator):
    """Interactive incident analysis"""
    print("\n" + "="*80)
    print("📝 NEW INCIDENT ANALYSIS")
    print("="*80 + "\n")
    
    print("Enter the incident report (press Enter twice when done):")
    print("-" * 80)
    
    lines = []
    empty_lines = 0
    while empty_lines < 2:
        line = input()
        if not line.strip():
            empty_lines += 1
        else:
            empty_lines = 0
        lines.append(line)
    
    report = "\n".join(lines).strip()
    
    if not report or len(report) < 20:
        print("\n❌ Error: Please provide a detailed incident report (at least 20 characters)")
        return
    
    print("\n" + "-"*80)
    print("Execution Mode:")
    print("  1. Simulate (test the response plan)")
    print("  2. Execute (perform actual actions)")
    mode_choice = input("Select mode (1 or 2) [default: 1]: ").strip() or "1"
    
    execution_mode = "simulate" if mode_choice == "1" else "execute"
    
    print("\n" + "="*80)
    print(f"Processing in {execution_mode.upper()} mode...")
    print("="*80 + "\n")
    
    results = orchestrator.process_incident(
        raw_report=report,
        metadata={
            "source": "cli",
            "submitted_at": datetime.now().isoformat()
        },
        execution_mode=execution_mode
    )
    
    if results.get("status") == "success":
        print("\n✅ Analysis completed successfully!")
        print(f"📁 Incident ID: {results['incident_id']}")
        input("\nPress Enter to continue...")
    else:
        print(f"\n❌ Error: {results.get('error', 'Unknown error')}")
        input("\nPress Enter to continue...")


def view_history(orchestrator):
    """View incident history"""
    print("\n" + "="*80)
    print("📚 INCIDENT HISTORY")
    print("="*80 + "\n")
    
    history = orchestrator.workflow_history
    
    if not history:
        print("No incidents processed yet.")
    else:
        for i, incident in enumerate(history, 1):
            status_symbol = "✅" if incident.get("status") == "success" else "❌"
            evaluator = incident.get("stages", {}).get("evaluator", {})
            score = evaluator.get("overall_score", 0)
            rating = evaluator.get("effectiveness_rating", "N/A")
            
            print(f"{i}. {status_symbol} {incident['incident_id']}")
            print(f"   Score: {score}/100 | Rating: {rating}")
            print(f"   Time: {incident['workflow_start']}")
            print()
    
    input("Press Enter to continue...")


def view_statistics(orchestrator):
    """View statistics"""
    print("\n" + "="*80)
    print("📊 SYSTEM STATISTICS")
    print("="*80 + "\n")
    
    stats = orchestrator.get_workflow_statistics()
    
    print(f"Total Incidents Processed: {stats['total_incidents']}")
    print(f"Successful: {stats['successful']}")
    print(f"Failed: {stats['failed']}")
    print(f"Average Score: {stats['average_score']}/100")
    
    if stats.get('incident_types'):
        print("\nIncident Types:")
        for itype, count in stats['incident_types'].items():
            print(f"  • {itype}: {count}")
    
    print()
    input("Press Enter to continue...")


def export_incident(orchestrator):
    """Export incident report"""
    print("\n" + "="*80)
    print("💾 EXPORT INCIDENT REPORT")
    print("="*80 + "\n")
    
    history = orchestrator.workflow_history
    
    if not history:
        print("No incidents to export.")
        input("\nPress Enter to continue...")
        return
    
    print("Available incidents:")
    for i, incident in enumerate(history, 1):
        print(f"{i}. {incident['incident_id']}")
    
    choice = input("\nSelect incident number: ").strip()
    
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(history):
            incident_id = history[idx]['incident_id']
            
            print("\nExport format:")
            print("  1. JSON")
            print("  2. Text Summary")
            format_choice = input("Select format (1 or 2) [default: 2]: ").strip() or "2"
            
            format_type = "json" if format_choice == "1" else "summary"
            report = orchestrator.export_report(incident_id, format_type)
            
            filename = f"{incident_id}_{format_type}.{'json' if format_type == 'json' else 'txt'}"
            with open(filename, 'w') as f:
                f.write(report)
            
            print(f"\n✅ Report exported to: {filename}")
        else:
            print("\n❌ Invalid selection")
    except ValueError:
        print("\n❌ Invalid input")
    
    input("\nPress Enter to continue...")


def load_example(orchestrator):
    """Load and analyze example incident"""
    print("\n" + "="*80)
    print("📖 EXAMPLE INCIDENTS")
    print("="*80 + "\n")
    
    examples = get_example_reports()
    
    for key, example in examples.items():
        print(f"{key}. {example['title']}")
    
    choice = input("\nSelect example (1-5): ").strip()
    
    if choice in examples:
        example = examples[choice]
        print(f"\n📄 Loading: {example['title']}")
        print("="*80)
        print(example['report'])
        print("="*80)
        
        confirm = input("\nAnalyze this incident? (y/n) [default: y]: ").strip().lower() or "y"
        
        if confirm == "y":
            results = orchestrator.process_incident(
                raw_report=example['report'],
                metadata={
                    "source": "cli_example",
                    "example_type": example['title'],
                    "submitted_at": datetime.now().isoformat()
                },
                execution_mode="simulate"
            )
            
            if results.get("status") == "success":
                print("\n✅ Analysis completed successfully!")
                print(f"📁 Incident ID: {results['incident_id']}")
    else:
        print("\n❌ Invalid selection")
    
    input("\nPress Enter to continue...")


def show_about():
    """Show about information"""
    print("\n" + "="*80)
    print("ℹ️  ABOUT THE SYSTEM")
    print("="*80 + "\n")
    
    print("Campus Incident Report Analysis System")
    print("Multi-Agent AI System for Incident Response")
    print("\nAgents:")
    print("  1. 📝 Prompt Agent - Processes and structures incident reports")
    print("  2. 📋 Planner Agent - Creates comprehensive action plans")
    print("  3. ⚙️  Executor Agent - Executes actions and coordinates resources")
    print("  4. 🔒 Safety & Policy Agent - Validates compliance and safety")
    print("  5. 📊 Evaluator Agent - Evaluates response effectiveness")
    
    print("\nFeatures:")
    print("  • Automated incident analysis and response planning")
    print("  • Policy compliance validation")
    print("  • Safety checks and risk assessment")
    print("  • Performance evaluation and scoring")
    print("  • Detailed reporting and recommendations")
    
    print("\nVersion: 1.0.0")
    print("Developed for: Agentathon 2025")
    print()
    input("Press Enter to continue...")


def main():
    """Main CLI application"""
    orchestrator = IncidentResponseOrchestrator()
    
    while True:
        print_banner()
        print_menu()
        
        choice = input("Enter your choice (1-7): ").strip()
        
        if choice == "1":
            analyze_incident_interactive(orchestrator)
        elif choice == "2":
            view_history(orchestrator)
        elif choice == "3":
            view_statistics(orchestrator)
        elif choice == "4":
            export_incident(orchestrator)
        elif choice == "5":
            load_example(orchestrator)
        elif choice == "6":
            show_about()
        elif choice == "7":
            print("\n👋 Thank you for using the Campus Incident Report Analysis System!")
            print("="*80 + "\n")
            break
        else:
            print("\n❌ Invalid choice. Please enter a number between 1 and 7.")
            input("Press Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ An error occurred: {str(e)}")