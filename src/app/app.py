"""
Flask Web Application for Campus Incident Report Analysis
Integrated with React Frontend
"""
from flask import Flask, request, jsonify, send_from_directory, send_file
from flask_cors import CORS
import sys
import os
from datetime import datetime
import json
import uuid


from orchestrator import IncidentResponseOrchestrator
from backend.api.analytics_api import analytics_bp, record_incident_analytics

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)
app.config['SECRET_KEY'] = 'campus-incident-analysis-2025'

# Register analytics blueprint
app.register_blueprint(analytics_bp)

# Initialize orchestrator
orchestrator = IncidentResponseOrchestrator()

# In-memory storage for demo purposes (in production, use a proper database)
incidents = []
analytics_data = {
    "total_incidents": 0,
    "resolved_incidents": 0,
    "pending_incidents": 0,
    "high_priority_incidents": 0,
    "incident_types": {},
    "monthly_trends": []
}


@app.route('/')
def serve_react_app():
    """Serve the React app"""
    try:
        return send_file('static/index.html')
    except:
        return "React app not built yet. Please run 'npm run build' in the frontend directory."

@app.route('/<path:path>')
def serve_static_files(path):
    """Serve static files from React build"""
    try:
        return send_from_directory('static', path)
    except:
        # If file not found, serve the React app (for client-side routing)
        return send_file('static/index.html')

@app.route('/api/incidents', methods=['GET'])
def get_incidents():
    """Get all incidents"""
    return jsonify({
        "success": True,
        "data": incidents
    })

@app.route('/api/incidents', methods=['POST'])
def create_incident():
    """Create a new incident report"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description', 'location', 'type', 'priority']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({
                    "success": False,
                    "error": f"Missing required field: {field}"
                }), 400
        
        # Create incident object
        incident = {
            "id": str(uuid.uuid4()),
            "title": data['title'],
            "description": data['description'],
            "location": data['location'],
            "type": data['type'],
            "priority": data['priority'],
            "status": "pending",
            "reporter_name": data.get('reporter_name', 'Anonymous'),
            "reporter_contact": data.get('reporter_contact', ''),
            "timestamp": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Add to incidents list
        incidents.append(incident)
        
        # Update analytics
        update_analytics()
        
        # Process with orchestrator (async in background)
        try:
            result = orchestrator.process_incident(data['description'])
            incident['ai_analysis'] = result
        except Exception as e:
            incident['ai_analysis'] = {"error": str(e)}
        
        return jsonify({
            "success": True,
            "data": incident,
            "message": "Incident reported successfully"
        }), 201
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/incidents/<incident_id>', methods=['GET'])
def get_incident(incident_id):
    """Get a specific incident"""
    incident = next((i for i in incidents if i['id'] == incident_id), None)
    if not incident:
        return jsonify({
            "success": False,
            "error": "Incident not found"
        }), 404
    
    return jsonify({
        "success": True,
        "data": incident
    })

@app.route('/api/incidents/<incident_id>', methods=['PUT'])
def update_incident(incident_id):
    """Update an incident"""
    try:
        incident = next((i for i in incidents if i['id'] == incident_id), None)
        if not incident:
            return jsonify({
                "success": False,
                "error": "Incident not found"
            }), 404
        
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = ['title', 'description', 'location', 'type', 'priority', 'status']
        for field in allowed_fields:
            if field in data:
                incident[field] = data[field]
        
        incident['updated_at'] = datetime.now().isoformat()
        
        # Update analytics
        update_analytics()
        
        return jsonify({
            "success": True,
            "data": incident,
            "message": "Incident updated successfully"
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/incidents/<incident_id>', methods=['DELETE'])
def delete_incident(incident_id):
    """Delete an incident"""
    global incidents
    incident = next((i for i in incidents if i['id'] == incident_id), None)
    if not incident:
        return jsonify({
            "success": False,
            "error": "Incident not found"
        }), 404
    
    incidents = [i for i in incidents if i['id'] != incident_id]
    update_analytics()
    
    return jsonify({
        "success": True,
        "message": "Incident deleted successfully"
    })

@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get analytics data"""
    return jsonify({
        "success": True,
        "data": analytics_data
    })

@app.route('/api/process', methods=['POST'])
def process_incident_analysis():
    """Process incident with AI analysis"""
    try:
        data = request.get_json()
        description = data.get('description', '')
        
        if not description:
            return jsonify({
                "success": False,
                "error": "Description is required"
            }), 400
        
        # Process with orchestrator
        result = orchestrator.process_incident(description)
        
        return jsonify({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "success": True,
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

def update_analytics():
    """Update analytics data based on current incidents"""
    global analytics_data
    
    analytics_data["total_incidents"] = len(incidents)
    analytics_data["resolved_incidents"] = len([i for i in incidents if i['status'] == 'resolved'])
    analytics_data["pending_incidents"] = len([i for i in incidents if i['status'] == 'pending'])
    analytics_data["high_priority_incidents"] = len([i for i in incidents if i['priority'] == 'high'])
    
    # Count incident types
    incident_types = {}
    for incident in incidents:
        incident_type = incident['type']
        incident_types[incident_type] = incident_types.get(incident_type, 0) + 1
    analytics_data["incident_types"] = incident_types
    
    # Generate monthly trends (simplified)
    current_month = datetime.now().strftime('%Y-%m')
    monthly_count = len([i for i in incidents if i['created_at'].startswith(current_month)])
    analytics_data["monthly_trends"] = [
        {"month": current_month, "count": monthly_count}
    ]
def get_statistics():
    """Get workflow statistics"""
    try:
        stats = orchestrator.get_workflow_statistics()
        return jsonify({
            'status': 'success',
            'statistics': stats
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/export/<incident_id>', methods=['GET'])
def export_incident(incident_id):
    """Export incident report"""
    try:
        format_type = request.args.get('format', 'json')
        report = orchestrator.export_report(incident_id, format_type)
        
        if report == "Incident not found":
            return jsonify({
                'status': 'error',
                'error': 'Incident not found'
            }), 404
        
        if format_type == 'json':
            return jsonify(json.loads(report))
        else:
            return report, 200, {'Content-Type': 'text/plain'}
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("\n" + "="*80)
    print("🚀 Campus Incident Report Analysis System")
    print("="*80)
    print("\n📍 Server starting on http://localhost:5000")
    print("\n🔧 Multi-Agent System:")
    print("   1. Prompt Agent - Report processing")
    print("   2. Planner Agent - Action planning")
    print("   3. Executor Agent - Action execution")
    print("   4. Safety & Policy Agent - Compliance validation")
    print("   5. Evaluator Agent - Response evaluation")
    print("\n" + "="*80 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == '__main__':
    # Add some sample data for demo
    sample_incidents = [
        {
            "id": str(uuid.uuid4()),
            "title": "Broken Window in Library",
            "description": "Large window on the second floor of the library is cracked and needs repair",
            "location": "Main Library, 2nd Floor",
            "type": "maintenance",
            "priority": "medium",
            "status": "pending",
            "reporter_name": "John Doe",
            "reporter_contact": "john.doe@university.edu",
            "timestamp": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Suspicious Activity Near Parking Lot",
            "description": "Observed individuals loitering near the east parking lot after hours",
            "location": "East Parking Lot",
            "type": "security",
            "priority": "high",
            "status": "resolved",
            "reporter_name": "Jane Smith",
            "reporter_contact": "jane.smith@university.edu",
            "timestamp": datetime.now().isoformat(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
    ]
    
    incidents.extend(sample_incidents)
    update_analytics()
    
    print("🚀 Campus Incident Report System Starting...")
    print("📊 Dashboard: http://localhost:5000")
    print("🔧 API Endpoints: http://localhost:5000/api")
    print("📝 React Frontend: Integrated")
    
    app.run(debug=True, host='0.0.0.0', port=5000)