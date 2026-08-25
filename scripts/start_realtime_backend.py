#!/usr/bin/env python3
"""
Startup script for the Real-time Campus Incident Response Backend
"""
import sys
import os
import asyncio
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

try:
    import uvicorn
    from backend.api.realtime_api import app
    from backend.api.data_simulator import create_data_simulator
    from backend.graph.incident_workflow import create_incident_workflow
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install required dependencies:")
    print("pip install fastapi uvicorn websockets langgraph langchain langchain-core")
    sys.exit(1)


def main():
    """Main startup function"""
    print("🚀 Campus Incident Response - Real-time Backend")
    print("=" * 60)
    
    # Test imports and initialization
    print("📦 Testing system components...")
    
    try:
        # Test workflow creation
        workflow = create_incident_workflow()
        print("   ✅ LangGraph workflow initialized")
        
        # Test data simulator
        simulator = create_data_simulator()
        print("   ✅ Data simulator initialized")
        
        # Test incident generation
        test_incident = simulator.generate_incident_report()
        print(f"   ✅ Test incident generated: {test_incident['metadata']['incident_type']}")
        
    except Exception as e:
        print(f"   ❌ Component test failed: {e}")
        return 1
    
    print("\n🌐 Starting FastAPI server...")
    print("📊 Real-time API: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔌 WebSocket: ws://localhost:8000/ws/realtime")
    print("💡 Health Check: http://localhost:8000/health")
    
    print("\n🎯 Available Endpoints:")
    print("   POST /api/v1/incidents/process - Process incident reports")
    print("   GET  /api/v1/workflows/{id}/status - Get workflow status")
    print("   POST /api/v1/simulation/run - Run incident simulation")
    print("   GET  /api/v1/analytics/realtime - Real-time analytics")
    print("   WS   /ws/realtime - Real-time updates")
    
    print("\n🔧 Example Usage:")
    print("""
    # Process an incident
    curl -X POST "http://localhost:8000/api/v1/incidents/process" \\
         -H "Content-Type: application/json" \\
         -d '{
           "report": "Student injured in gymnasium during basketball game",
           "execution_mode": "simulate"
         }'
    
    # Run simulation
    curl -X POST "http://localhost:8000/api/v1/simulation/run" \\
         -H "Content-Type: application/json" \\
         -d '{
           "scenario_type": "campus_emergency",
           "incident_count": 5,
           "time_acceleration": 2.0
         }'
    """)
    
    print("\n" + "=" * 60)
    print("Press Ctrl+C to stop the server")
    print("=" * 60 + "\n")
    
    # Start the server
    try:
        uvicorn.run(
            "backend.api.realtime_api:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped")
        return 0
    except Exception as e:
        print(f"❌ Server error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())