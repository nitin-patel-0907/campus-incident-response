#!/usr/bin/env python3
"""
Startup script for Analytics-Enhanced Campus Incident Response Backend on port 8082
"""
import sys
import os
import asyncio
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

try:
    import uvicorn
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    from backend.api.realtime_api import app as realtime_app
    from backend.api.analytics_api import analytics_bp
    from backend.api.data_simulator import create_data_simulator
    from backend.graph.incident_workflow import create_incident_workflow
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install required dependencies:")
    print("pip install fastapi uvicorn websockets langgraph langchain langchain-core flask")
    sys.exit(1)

# Create enhanced FastAPI app with analytics
app = FastAPI(
    title="Campus Incident Response System",
    description="AI-powered incident response with real-time analytics",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the existing realtime API
app.mount("/api/v1", realtime_app)

# Add analytics endpoints
@app.get("/api/analytics/overview")
async def analytics_overview():
    """Get analytics overview"""
    from backend.api.analytics_api import get_analytics_overview
    from flask import Flask
    
    # Create temporary Flask app for analytics
    flask_app = Flask(__name__)
    flask_app.register_blueprint(analytics_bp)
    
    with flask_app.test_client() as client:
        response = client.get('/api/analytics/overview')
        if response.status_code == 200:
            return response.get_json()
        else:
            return {"error": "Analytics not available"}

@app.get("/api/analytics/trends")
async def analytics_trends():
    """Get trends analysis"""
    from backend.api.analytics_api import get_trends
    from flask import Flask
    
    flask_app = Flask(__name__)
    flask_app.register_blueprint(analytics_bp)
    
    with flask_app.test_client() as client:
        response = client.get('/api/analytics/trends')
        if response.status_code == 200:
            return response.get_json()
        else:
            return {"error": "Trends not available"}

@app.get("/api/analytics/policies")
async def analytics_policies():
    """Get policy compliance"""
    from backend.api.analytics_api import get_policy_compliance
    from flask import Flask
    
    flask_app = Flask(__name__)
    flask_app.register_blueprint(analytics_bp)
    
    with flask_app.test_client() as client:
        response = client.get('/api/analytics/policies')
        if response.status_code == 200:
            return response.get_json()
        else:
            return {"error": "Policy data not available"}

# Serve frontend static files
if os.path.exists("frontend/dist"):
    app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")
    
    @app.get("/")
    async def serve_frontend():
        return FileResponse("frontend/dist/index.html")
    
    @app.get("/{path:path}")
    async def serve_frontend_routes(path: str):
        # Check if it's an API route
        if path.startswith("api/"):
            return {"error": "API endpoint not found"}
        
        # Try to serve static file
        static_file = f"frontend/dist/{path}"
        if os.path.exists(static_file) and os.path.isfile(static_file):
            return FileResponse(static_file)
        
        # Fallback to index.html for client-side routing
        return FileResponse("frontend/dist/index.html")

def main():
    """Main startup function"""
    print("🚀 Campus Incident Response - Analytics Backend (Port 8082)")
    print("=" * 70)
    
    # Test imports and initialization
    print("📦 Testing system components...")
    
    try:
        # Test workflow creation
        workflow = create_incident_workflow()
        print("   ✅ LangGraph workflow initialized")
        
        # Test data simulator
        simulator = create_data_simulator()
        print("   ✅ Data simulator initialized")
        
        # Test analytics
        from backend.api.analytics_api import load_analytics_data
        analytics_data = load_analytics_data()
        print(f"   ✅ Analytics initialized ({len(analytics_data.get('incidents', []))} incidents)")
        
        # Test incident generation
        test_incident = simulator.generate_incident_report()
        print(f"   ✅ Test incident generated: {test_incident['metadata']['incident_type']}")
        
    except Exception as e:
        print(f"   ❌ Component test failed: {e}")
        return 1
    
    print("\n🌐 Starting Enhanced FastAPI server...")
    print("📊 Main Application: https://localhost:8082")
    print("📚 API Documentation: https://localhost:8082/docs")
    print("🔌 WebSocket: wss://localhost:8082/ws/realtime")
    print("💡 Health Check: https://localhost:8082/health")
    print("📈 Analytics Dashboard: https://localhost:8082 (AI Insights page)")
    
    print("\n🎯 Available Endpoints:")
    print("   POST /api/v1/incidents/process - Process incident reports")
    print("   GET  /api/v1/workflows/{id}/status - Get workflow status")
    print("   POST /api/v1/simulation/run - Run incident simulation")
    print("   GET  /api/v1/analytics/realtime - Real-time analytics")
    print("   GET  /api/analytics/overview - Analytics overview")
    print("   GET  /api/analytics/trends - Trends analysis")
    print("   GET  /api/analytics/policies - Policy compliance")
    print("   WS   /ws/realtime - Real-time updates")
    
    print("\n📊 Analytics Features:")
    print("   • Real-time performance metrics")
    print("   • Incident trend analysis")
    print("   • Policy compliance monitoring")
    print("   • AI-generated insights")
    print("   • Interactive visualizations")
    
    print("\n🔧 Example Usage:")
    print("""
    # Process an incident
    curl -X POST "https://localhost:8082/api/v1/incidents/process" \\
         -H "Content-Type: application/json" \\
         -d '{
           "report": "Student injured in gymnasium during basketball game",
           "execution_mode": "simulate"
         }'
    
    # Get analytics overview
    curl "https://localhost:8082/api/analytics/overview"
    
    # Get trends analysis
    curl "https://localhost:8082/api/analytics/trends"
    """)
    
    print("\n" + "=" * 70)
    print("🎭 DEMO DATA LOADED:")
    print("• 100+ realistic incidents with patterns")
    print("• Friday evening security spikes")
    print("• Monday morning medical incidents")
    print("• Exam period harassment increases")
    print("• Anonymous reporting variations")
    print("• Performance metrics and AI insights")
    print("\n📱 Visit https://localhost:8082 and go to 'AI Insights & Evaluation'")
    print("=" * 70)
    print("Press Ctrl+C to stop the server")
    print("=" * 70 + "\n")
    
    # Start the server
    try:
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=8082,
            ssl_keyfile=None,  # Add SSL if needed
            ssl_certfile=None,
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