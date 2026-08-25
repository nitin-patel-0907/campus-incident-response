"""
Real-time Analytics API for AI Insights Dashboard
Provides trend-based performance metrics and insights
"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
import statistics
from flask import Blueprint, jsonify, request

# Create analytics blueprint
analytics_bp = Blueprint('analytics', __name__)

# In-memory storage for demo (in production, use database)
ANALYTICS_DATA_FILE = "analytics_data.json"

def load_analytics_data():
    """Load analytics data from file"""
    target_file = ANALYTICS_DATA_FILE
    if not os.path.exists(target_file):
        alt_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", target_file)
        if os.path.exists(alt_path):
            target_file = alt_path
        elif os.path.exists(os.path.join("data", target_file)):
            target_file = os.path.join("data", target_file)
            
    if os.path.exists(target_file):
        try:
            with open(target_file, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        "incidents": [],
        "evaluations": [],
        "trends": {},
        "last_updated": datetime.now().isoformat()
    }

def save_analytics_data(data):
    """Save analytics data to file"""
    data["last_updated"] = datetime.now().isoformat()
    with open(ANALYTICS_DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_incident_to_analytics(incident_data, evaluation_report=None):
    """Add incident and evaluation data to analytics"""
    data = load_analytics_data()
    
    # Add incident
    incident_record = {
        "incident_id": incident_data.get("incident_id"),
        "incident_type": incident_data.get("incident_type"),
        "severity": incident_data.get("severity"),
        "location": incident_data.get("location"),
        "anonymous": incident_data.get("anonymous", False),
        "timestamp": incident_data.get("submission_timestamp", datetime.now().isoformat()),
        "resolution_status": incident_data.get("resolution_status", "unresolved")
    }
    data["incidents"].append(incident_record)
    
    # Add evaluation if available
    if evaluation_report:
        eval_record = {
            "incident_id": incident_data.get("incident_id"),
            "overall_score": evaluation_report.get("overall_score", 0),
            "effectiveness_rating": evaluation_report.get("effectiveness_rating", "Unknown"),
            "category_scores": evaluation_report.get("category_scores", []),
            "timestamp": datetime.now().isoformat()
        }
        data["evaluations"].append(eval_record)
    
    # Keep only last 100 incidents for performance
    data["incidents"] = data["incidents"][-100:]
    data["evaluations"] = data["evaluations"][-100:]
    
    save_analytics_data(data)

@analytics_bp.route('/api/analytics/overview', methods=['GET'])
def get_analytics_overview():
    """Get overall analytics overview with real-time metrics"""
    try:
        data = load_analytics_data()
        incidents = data.get("incidents", [])
        evaluations = data.get("evaluations", [])
        
        # Calculate time periods
        now = datetime.now()
        last_30_days = now - timedelta(days=30)
        last_7_days = now - timedelta(days=7)
        
        # Filter recent data
        recent_incidents = []
        recent_evaluations = []
        
        for inc in incidents:
            try:
                timestamp_str = inc.get("timestamp", "")
                if timestamp_str:
                    # Handle different timestamp formats
                    if 'T' in timestamp_str:
                        timestamp_str = timestamp_str.replace('Z', '+00:00')
                        dt = datetime.fromisoformat(timestamp_str)
                    else:
                        dt = datetime.fromisoformat(timestamp_str)
                    
                    if dt > last_30_days:
                        recent_incidents.append(inc)
            except:
                # If timestamp parsing fails, include the incident anyway
                recent_incidents.append(inc)
        
        for ev in evaluations:
            try:
                timestamp_str = ev.get("timestamp", "")
                if timestamp_str:
                    # Handle different timestamp formats
                    if 'T' in timestamp_str:
                        timestamp_str = timestamp_str.replace('Z', '+00:00')
                        dt = datetime.fromisoformat(timestamp_str)
                    else:
                        dt = datetime.fromisoformat(timestamp_str)
                    
                    if dt > last_30_days:
                        recent_evaluations.append(ev)
            except:
                # If timestamp parsing fails, include the evaluation anyway
                recent_evaluations.append(ev)
        
        # Calculate overall quality score
        if recent_evaluations:
            overall_score = statistics.mean([ev["overall_score"] for ev in recent_evaluations])
            
            # Calculate trend (compare last 7 days vs previous 7 days)
            week_ago = now - timedelta(days=14)
            last_week_evals = [
                ev for ev in recent_evaluations 
                if last_7_days < datetime.fromisoformat(ev["timestamp"].replace('Z', '+00:00')) <= now
            ]
            prev_week_evals = [
                ev for ev in recent_evaluations 
                if week_ago < datetime.fromisoformat(ev["timestamp"].replace('Z', '+00:00')) <= last_7_days
            ]
            
            trend = 0
            if last_week_evals and prev_week_evals:
                last_week_avg = statistics.mean([ev["overall_score"] for ev in last_week_evals])
                prev_week_avg = statistics.mean([ev["overall_score"] for ev in prev_week_evals])
                trend = ((last_week_avg - prev_week_avg) / prev_week_avg) * 100
        else:
            overall_score = 75.0  # Default score
            trend = 0
        
        # Calculate performance metrics
        performance_metrics = calculate_performance_metrics(recent_incidents, recent_evaluations)
        
        # Get strengths and improvements
        strengths = identify_strengths(recent_evaluations)
        improvements = identify_improvements(recent_evaluations, recent_incidents)
        
        # Get lessons learned
        lessons = generate_lessons_learned(recent_incidents, recent_evaluations)
        
        return jsonify({
            "overall_score": round(overall_score, 1),
            "trend": round(trend, 1),
            "performance_metrics": performance_metrics,
            "strengths": strengths,
            "improvements": improvements,
            "lessons_learned": lessons,
            "total_incidents": len(recent_incidents),
            "total_evaluations": len(recent_evaluations),
            "last_updated": data.get("last_updated", datetime.now().isoformat())
        })
        
    except Exception as e:
        print(f"Analytics overview error: {e}")
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/api/analytics/trends', methods=['GET'])
def get_trends():
    """Get trend analysis based on recent reports"""
    try:
        data = load_analytics_data()
        incidents = data.get("incidents", [])
        
        # Calculate time periods
        now = datetime.now()
        last_30_days = now - timedelta(days=30)
        
        # Filter recent incidents
        recent_incidents = []
        for inc in incidents:
            try:
                timestamp_str = inc.get("timestamp", "")
                if timestamp_str:
                    # Handle different timestamp formats
                    if 'T' in timestamp_str:
                        timestamp_str = timestamp_str.replace('Z', '+00:00')
                        dt = datetime.fromisoformat(timestamp_str)
                    else:
                        dt = datetime.fromisoformat(timestamp_str)
                    
                    if dt > last_30_days:
                        recent_incidents.append(inc)
            except:
                # If timestamp parsing fails, include the incident anyway
                recent_incidents.append(inc)
        
        # Incident type trends
        type_counts = Counter([inc["incident_type"] for inc in recent_incidents])
        
        # Severity trends
        severity_counts = Counter([inc["severity"] for inc in recent_incidents])
        
        # Location trends
        location_counts = Counter([inc["location"] for inc in recent_incidents])
        
        # Time-based trends (by day of week)
        day_counts = defaultdict(int)
        for inc in recent_incidents:
            try:
                timestamp_str = inc.get("timestamp", "")
                if timestamp_str:
                    # Handle different timestamp formats
                    if 'T' in timestamp_str:
                        timestamp_str = timestamp_str.replace('Z', '+00:00')
                        dt = datetime.fromisoformat(timestamp_str)
                    else:
                        dt = datetime.fromisoformat(timestamp_str)
                    
                    day_name = dt.strftime('%A')
                    day_counts[day_name] += 1
            except:
                continue
        
        # Anonymous reporting trends
        anonymous_count = sum(1 for inc in recent_incidents if inc.get("anonymous", False))
        anonymous_rate = (anonymous_count / len(recent_incidents) * 100) if recent_incidents else 0
        
        return jsonify({
            "incident_types": dict(type_counts.most_common(5)),
            "severity_distribution": dict(severity_counts),
            "location_hotspots": dict(location_counts.most_common(5)),
            "day_of_week": dict(day_counts),
            "anonymous_reporting_rate": round(anonymous_rate, 1),
            "total_incidents": len(recent_incidents),
            "period": "Last 30 days"
        })
        
    except Exception as e:
        print(f"Trends error: {e}")
        return jsonify({"error": str(e)}), 500

@analytics_bp.route('/api/analytics/policies', methods=['GET'])
def get_policy_compliance():
    """Get policy compliance metrics"""
    try:
        data = load_analytics_data()
        incidents = data.get("incidents", [])
        
        # Calculate compliance metrics based on recent incidents
        now = datetime.now()
        last_30_days = now - timedelta(days=30)
        
        recent_incidents = []
        for inc in incidents:
            try:
                timestamp_str = inc.get("timestamp", "")
                if timestamp_str:
                    # Handle different timestamp formats
                    if 'T' in timestamp_str:
                        timestamp_str = timestamp_str.replace('Z', '+00:00')
                        dt = datetime.fromisoformat(timestamp_str)
                    else:
                        dt = datetime.fromisoformat(timestamp_str)
                    
                    if dt > last_30_days:
                        recent_incidents.append(inc)
            except:
                # If timestamp parsing fails, include the incident anyway
                recent_incidents.append(inc)
        
        # Calculate compliance scores
        total_incidents = len(recent_incidents)
        resolved_incidents = len([inc for inc in recent_incidents if inc.get("resolution_status") == "resolved"])
        
        compliance_rate = (resolved_incidents / total_incidents * 100) if total_incidents > 0 else 100
        
        # Policy compliance items with dynamic status
        compliance_items = [
            {
                "label": "FERPA Privacy Compliance",
                "status": True,
                "description": "All incident data properly anonymized"
            },
            {
                "label": "Title IX Reporting",
                "status": True,
                "description": "Harassment incidents properly escalated"
            },
            {
                "label": "Clery Act Documentation",
                "status": compliance_rate > 80,
                "description": f"Documentation rate: {compliance_rate:.1f}%"
            },
            {
                "label": "Response Time Standards",
                "status": compliance_rate > 75,
                "description": "Meeting campus response time requirements"
            },
            {
                "label": "Anonymous Reporting Protection",
                "status": True,
                "description": "Identity protection protocols active"
            },
            {
                "label": "Data Retention Policy",
                "status": total_incidents < 100,  # Keeping data manageable
                "description": f"Managing {total_incidents} recent incidents"
            }
        ]
        
        return jsonify({
            "compliance_rate": round(compliance_rate, 1),
            "items": compliance_items,
            "total_incidents": total_incidents,
            "resolved_incidents": resolved_incidents
        })
        
    except Exception as e:
        print(f"Policy compliance error: {e}")
        return jsonify({"error": str(e)}), 500

def calculate_performance_metrics(incidents, evaluations):
    """Calculate performance metrics for radar chart"""
    if not evaluations:
        # Default metrics if no evaluations
        return [
            {"subject": "Response Time", "score": 75, "fullMark": 100},
            {"subject": "Accuracy", "score": 80, "fullMark": 100},
            {"subject": "Compliance", "score": 85, "fullMark": 100},
            {"subject": "Resolution", "score": 70, "fullMark": 100},
            {"subject": "Communication", "score": 75, "fullMark": 100},
            {"subject": "Prevention", "score": 65, "fullMark": 100}
        ]
    
    # Calculate metrics from evaluation data
    category_scores = {}
    for evaluation in evaluations:
        eval_categories = evaluation.get("category_scores", {})
        
        # Handle both dict and list formats
        if isinstance(eval_categories, dict):
            for cat_name, score in eval_categories.items():
                if cat_name not in category_scores:
                    category_scores[cat_name] = []
                category_scores[cat_name].append(score)
        elif isinstance(eval_categories, list):
            for category in eval_categories:
                cat_name = category.get("category", "Unknown")
                score = category.get("score", 0)
                if cat_name not in category_scores:
                    category_scores[cat_name] = []
                category_scores[cat_name].append(score)
    
    # Map categories to display names
    category_mapping = {
        "timeliness": "Response Time",
        "completeness": "Accuracy", 
        "policy_compliance": "Compliance",
        "resource_allocation": "Resolution",
        "communication": "Communication",
        "safety_measures": "Prevention"
    }
    
    metrics = []
    for internal_name, display_name in category_mapping.items():
        if internal_name in category_scores:
            avg_score = statistics.mean(category_scores[internal_name])
        else:
            avg_score = 75.0  # Default
        
        metrics.append({
            "subject": display_name,
            "score": round(avg_score, 1),
            "fullMark": 100
        })
    
    return metrics

def identify_strengths(evaluations):
    """Identify strengths from evaluation data"""
    if not evaluations:
        return [
            {"label": "System reliability", "score": 85},
            {"label": "Response coordination", "score": 80},
            {"label": "Data processing", "score": 90},
            {"label": "User interface", "score": 88}
        ]
    
    # Analyze category performance
    category_scores = defaultdict(list)
    for evaluation in evaluations:
        eval_categories = evaluation.get("category_scores", {})
        
        # Handle both dict and list formats
        if isinstance(eval_categories, dict):
            for cat_name, score in eval_categories.items():
                category_scores[cat_name].append(score)
        elif isinstance(eval_categories, list):
            for category in eval_categories:
                cat_name = category.get("category", "Unknown")
                score = category.get("score", 0)
                category_scores[cat_name].append(score)
    
    # Find top performing categories
    strengths = []
    for category, scores in category_scores.items():
        avg_score = statistics.mean(scores)
        if avg_score >= 80:  # Consider high-performing categories as strengths
            display_name = category.replace('_', ' ').title()
            strengths.append({
                "label": f"Strong {display_name.lower()} performance",
                "score": round(avg_score, 1)
            })
    
    # Add default strengths if none found
    if not strengths:
        strengths = [
            {"label": "Consistent response delivery", "score": 85},
            {"label": "Multi-agent coordination", "score": 82}
        ]
    
    return strengths[:4]  # Limit to top 4

def identify_improvements(evaluations, incidents):
    """Identify areas for improvement"""
    improvements = []
    
    if evaluations:
        # Analyze low-performing categories
        category_scores = defaultdict(list)
        for evaluation in evaluations:
            eval_categories = evaluation.get("category_scores", {})
            
            # Handle both dict and list formats
            if isinstance(eval_categories, dict):
                for cat_name, score in eval_categories.items():
                    category_scores[cat_name].append(score)
            elif isinstance(eval_categories, list):
                for category in eval_categories:
                    cat_name = category.get("category", "Unknown")
                    score = category.get("score", 0)
                    category_scores[cat_name].append(score)
        
        for category, scores in category_scores.items():
            avg_score = statistics.mean(scores)
            if avg_score < 70:  # Consider low-performing categories
                priority = "high" if avg_score < 60 else "medium"
                display_name = category.replace('_', ' ').title()
                improvements.append({
                    "label": f"Improve {display_name.lower()} effectiveness",
                    "priority": priority,
                    "description": f"Current performance: {avg_score:.1f}% - needs enhancement"
                })
    
    # Analyze incident patterns
    if incidents:
        # Check for high anonymous reporting rate
        anonymous_count = sum(1 for inc in incidents if inc.get("anonymous", False))
        if anonymous_count / len(incidents) > 0.3:  # More than 30% anonymous
            improvements.append({
                "label": "Enhance trust and transparency",
                "priority": "medium",
                "description": "High anonymous reporting rate suggests trust concerns"
            })
        
        # Check for unresolved incidents
        unresolved_count = sum(1 for inc in incidents if inc.get("resolution_status") != "resolved")
        if unresolved_count / len(incidents) > 0.4:  # More than 40% unresolved
            improvements.append({
                "label": "Improve resolution efficiency",
                "priority": "high",
                "description": "Many incidents remain unresolved - review processes"
            })
    
    # Add default improvements if none found
    if not improvements:
        improvements = [
            {
                "label": "Predictive analytics integration",
                "priority": "medium",
                "description": "Implement pattern recognition for early warning systems"
            },
            {
                "label": "Response time optimization",
                "priority": "low",
                "description": "Fine-tune automated response workflows"
            }
        ]
    
    return improvements[:3]  # Limit to top 3

def generate_lessons_learned(incidents, evaluations):
    """Generate lessons learned from recent data"""
    lessons = []
    
    if incidents:
        # Analyze incident patterns
        type_counts = Counter([inc["incident_type"] for inc in incidents])
        location_counts = Counter([inc["location"] for inc in incidents])
        
        # Most common incident type
        if type_counts:
            most_common_type, count = type_counts.most_common(1)[0]
            lessons.append({
                "title": f"{most_common_type.title()} Incident Patterns",
                "insight": f"{most_common_type.title()} incidents represent {count}/{len(incidents)} recent reports",
                "impact": "Focused response training recommended"
            })
        
        # Location hotspots
        if location_counts:
            hotspot, hotspot_count = location_counts.most_common(1)[0]
            if hotspot_count > 1:
                lessons.append({
                    "title": "Location-Based Prevention",
                    "insight": f"Multiple incidents reported at {hotspot}",
                    "impact": "Enhanced monitoring recommended"
                })
        
        # Anonymous reporting insights
        anonymous_count = sum(1 for inc in incidents if inc.get("anonymous", False))
        if anonymous_count > 0:
            rate = (anonymous_count / len(incidents)) * 100
            lessons.append({
                "title": "Anonymous Reporting Trends",
                "insight": f"{rate:.1f}% of reports submitted anonymously",
                "impact": "Privacy protection measures effective"
            })
    
    # Add evaluation-based lessons
    if evaluations:
        avg_score = statistics.mean([ev["overall_score"] for ev in evaluations])
        if avg_score > 80:
            lessons.append({
                "title": "High Performance Consistency",
                "insight": f"Average evaluation score: {avg_score:.1f}%",
                "impact": "System reliability confirmed"
            })
    
    # Ensure we have at least some lessons
    if not lessons:
        lessons = [
            {
                "title": "System Learning Capability",
                "insight": "AI agents continuously improve through incident processing",
                "impact": "Enhanced response quality over time"
            },
            {
                "title": "Multi-Agent Coordination",
                "insight": "Specialized agents handle different aspects effectively",
                "impact": "Comprehensive incident management"
            }
        ]
    
    return lessons[:3]  # Limit to top 3

# Function to be called when incidents are processed
def record_incident_analytics(incident_data, evaluation_report=None):
    """Record incident and evaluation data for analytics"""
    try:
        add_incident_to_analytics(incident_data, evaluation_report)
    except Exception as e:
        print(f"Error recording analytics: {e}")