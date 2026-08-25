"""
Reinforcement Learning System for Campus Incident Response
Learns from historical data to improve decision making and detect spam
"""
import json
import os
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict, deque

@dataclass
class PerformanceMetric:
    """Performance metric for AI vs Human comparison"""
    ai_time: float
    human_time: float
    ai_resources: int
    human_resources: int
    ai_accuracy: float
    human_accuracy: float
    incident_type: str
    severity: str
    timestamp: str

@dataclass
class SpamPattern:
    """Spam detection pattern"""
    pattern_id: str
    text_hash: str
    similarity_threshold: float
    keywords: List[str]
    marked_spam_count: int
    false_positive_count: int
    confidence: float
    created_at: str
    last_seen: str

class ReinforcementLearningSystem:
    """
    Reinforcement Learning System that:
    1. Maintains persistent incident history
    2. Learns from AI vs Human performance
    3. Detects and prevents spam reports
    4. Provides performance insights
    """
    
    def __init__(self, data_file: str = "rl_system_data.json"):
        if not os.path.exists(data_file):
            alt_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", data_file)
            if os.path.exists(alt_path):
                data_file = alt_path
            elif os.path.exists(os.path.join("data", data_file)):
                data_file = os.path.join("data", data_file)
        self.data_file = data_file
        self.data = self._load_data()
        
        # Learning parameters
        self.learning_rate = 0.1
        self.discount_factor = 0.95
        self.exploration_rate = 0.1
        
        # Spam detection parameters
        self.spam_similarity_threshold = 0.85
        self.spam_confidence_threshold = 0.7
        self.max_spam_patterns = 1000
        
        # Performance tracking
        self.performance_window = 30  # days
        
    def _load_data(self) -> Dict[str, Any]:
        """Load persistent data from file"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                print(f"📚 Loaded RL system data: {len(data.get('incidents', []))} incidents, {len(data.get('spam_patterns', []))} spam patterns")
                return data
            except Exception as e:
                print(f"Error loading RL data: {e}")
        
        # Initialize empty data structure
        return {
            "incidents": [],
            "spam_patterns": [],
            "performance_metrics": [],
            "learning_stats": {
                "total_incidents": 0,
                "spam_detected": 0,
                "false_positives": 0,
                "ai_vs_human_comparisons": 0,
                "system_accuracy": 0.0,
                "last_updated": datetime.now().isoformat()
            },
            "confidence_improvements": {},
            "decision_rewards": {}
        }
    
    def _save_data(self):
        """Save data to persistent storage"""
        try:
            self.data["learning_stats"]["last_updated"] = datetime.now().isoformat()
            with open(self.data_file, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
        except Exception as e:
            print(f"Error saving RL data: {e}")
    
    def add_incident(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add incident to persistent history and learn from it
        
        Returns enhanced incident data with RL insights
        """
        try:
            # Check for spam first
            spam_result = self.detect_spam(incident_data)
            if spam_result["is_spam"]:
                print(f"🚫 Spam detected: {spam_result['reason']}")
                return {
                    "status": "spam_detected",
                    "spam_result": spam_result,
                    "incident_id": incident_data.get("incident_id", "unknown"),
                    "action": "rejected"
                }
            
            # Add to persistent history
            enhanced_incident = self._enhance_incident_with_rl(incident_data)
            self.data["incidents"].append(enhanced_incident)
            
            # Update learning statistics
            self._update_learning_stats(enhanced_incident)
            
            # Learn from this incident
            self._learn_from_incident(enhanced_incident)
            
            # Save data
            self._save_data()
            
            print(f"📈 Added incident to RL system: {enhanced_incident.get('incident_id', 'unknown')}")
            
            return {
                "status": "added",
                "enhanced_incident": enhanced_incident,
                "rl_insights": self._generate_rl_insights(enhanced_incident)
            }
            
        except Exception as e:
            print(f"Error adding incident to RL system: {e}")
            return {"status": "error", "error": str(e)}
    
    def detect_spam(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect if incident report is spam based on learned patterns and gibberish detection
        """
        try:
            report_text = incident_data.get("original_report", "")
            if not report_text:
                return {"is_spam": False, "confidence": 0.0, "reason": "No text to analyze"}
            
            # First, check for gibberish/nonsensical text
            gibberish_result = self._detect_gibberish_internal(report_text)
            if gibberish_result["is_gibberish"]:
                print(f"🚫 Gibberish detected: {gibberish_result['reason']}")
                return {
                    "is_spam": True,
                    "confidence": gibberish_result["confidence"],
                    "reason": f"Gibberish detected: {gibberish_result['reason']}",
                    "detection_type": "gibberish",
                    "gibberish_analysis": gibberish_result,
                    "requires_human_assessment": True  # Flag for human review
                }
            
            # Generate text hash for exact duplicate detection
            text_hash = hashlib.md5(report_text.lower().strip().encode()).hexdigest()
            
            # Check for exact duplicates
            for pattern in self.data["spam_patterns"]:
                if pattern["text_hash"] == text_hash:
                    confidence = min(pattern["confidence"] + 0.1, 1.0)  # Increase confidence
                    pattern["marked_spam_count"] += 1
                    pattern["last_seen"] = datetime.now().isoformat()
                    pattern["confidence"] = confidence
                    
                    return {
                        "is_spam": confidence > self.spam_confidence_threshold,
                        "confidence": confidence,
                        "reason": f"Exact duplicate of known spam (seen {pattern['marked_spam_count']} times)",
                        "pattern_id": pattern["pattern_id"],
                        "detection_type": "duplicate"
                    }
            
            # Check for similar patterns
            similarity_results = []
            for pattern in self.data["spam_patterns"]:
                similarity = self._calculate_text_similarity(report_text, pattern["keywords"])
                if similarity > pattern["similarity_threshold"]:
                    similarity_results.append({
                        "pattern_id": pattern["pattern_id"],
                        "similarity": similarity,
                        "confidence": pattern["confidence"],
                        "reason": f"Similar to known spam pattern (similarity: {similarity:.2f})"
                    })
            
            # Return highest confidence match
            if similarity_results:
                best_match = max(similarity_results, key=lambda x: x["confidence"] * x["similarity"])
                return {
                    "is_spam": best_match["confidence"] > self.spam_confidence_threshold,
                    "confidence": best_match["confidence"],
                    "reason": best_match["reason"],
                    "pattern_id": best_match["pattern_id"],
                    "detection_type": "pattern_match"
                }
            
            return {"is_spam": False, "confidence": 0.0, "reason": "No spam patterns matched", "detection_type": "clean"}
            
        except Exception as e:
            print(f"Error in spam detection: {e}")
            return {"is_spam": False, "confidence": 0.0, "reason": f"Detection error: {e}", "detection_type": "error"}
    
    def _detect_gibberish_internal(self, text: str) -> Dict[str, Any]:
        """
        Internal method to detect gibberish/nonsensical text
        """
        try:
            # Import gibberish detector
            from gibberish_detector import gibberish_detector
            
            result = gibberish_detector.detect_gibberish(text)
            
            if result["is_gibberish"]:
                # Format reason for user display
                primary_reason = result["reasons"][0] if result["reasons"] else "Text appears to be nonsensical"
                
                return {
                    "is_gibberish": True,
                    "confidence": result["confidence"],
                    "reason": primary_reason,
                    "gibberish_score": result["gibberish_score"],
                    "detailed_analysis": result["analysis"],
                    "all_reasons": result["reasons"]
                }
            else:
                return {
                    "is_gibberish": False,
                    "confidence": result["confidence"],
                    "reason": "Text appears to be meaningful",
                    "gibberish_score": result["gibberish_score"]
                }
                
        except ImportError:
            print("⚠️ Gibberish detector not available")
            return {
                "is_gibberish": False,
                "confidence": 0.5,
                "reason": "Gibberish detection unavailable"
            }
        except Exception as e:
            print(f"Error in gibberish detection: {e}")
            return {
                "is_gibberish": False,
                "confidence": 0.5,
                "reason": f"Gibberish detection error: {e}"
            }
    
    def mark_as_spam(self, incident_id: str, report_text: str, reason: str = "Manual review", 
                     is_gibberish: bool = False, human_assessment: str = None) -> Dict[str, Any]:
        """
        Mark an incident as spam and learn from it
        Enhanced to handle gibberish detection and human assessment
        """
        try:
            # Create spam pattern
            text_hash = hashlib.md5(report_text.lower().strip().encode()).hexdigest()
            keywords = self._extract_keywords(report_text)
            
            pattern_id = f"SPAM-{datetime.now().strftime('%Y%m%d%H%M%S')}-{text_hash[:8]}"
            
            # Determine initial confidence based on detection type
            if is_gibberish:
                initial_confidence = 0.9  # High confidence for gibberish
                pattern_type = "gibberish"
            elif human_assessment:
                initial_confidence = 0.85  # High confidence for human-verified spam
                pattern_type = "human_verified"
            else:
                initial_confidence = 0.8   # Standard confidence for manual marks
                pattern_type = "manual"
            
            spam_pattern = {
                "pattern_id": pattern_id,
                "text_hash": text_hash,
                "similarity_threshold": self.spam_similarity_threshold,
                "keywords": keywords,
                "marked_spam_count": 1,
                "false_positive_count": 0,
                "confidence": initial_confidence,
                "created_at": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "reason": reason,
                "pattern_type": pattern_type,
                "is_gibberish": is_gibberish,
                "human_assessment": human_assessment,
                "original_text": report_text[:200] + "..." if len(report_text) > 200 else report_text
            }
            
            # Add to spam patterns
            self.data["spam_patterns"].append(spam_pattern)
            
            # Limit spam patterns to prevent memory issues
            if len(self.data["spam_patterns"]) > self.max_spam_patterns:
                # Remove oldest patterns with lowest confidence
                self.data["spam_patterns"].sort(key=lambda x: (x["confidence"], x["created_at"]))
                self.data["spam_patterns"] = self.data["spam_patterns"][-self.max_spam_patterns:]
            
            # Update statistics
            self.data["learning_stats"]["spam_detected"] += 1
            if is_gibberish:
                if "gibberish_detected" not in self.data["learning_stats"]:
                    self.data["learning_stats"]["gibberish_detected"] = 0
                self.data["learning_stats"]["gibberish_detected"] += 1
            
            # Save data
            self._save_data()
            
            detection_type = "gibberish" if is_gibberish else "spam"
            print(f"🚫 Marked incident {incident_id} as {detection_type}: {pattern_id}")
            
            return {
                "status": "marked_spam",
                "pattern_id": pattern_id,
                "confidence": spam_pattern["confidence"],
                "keywords_extracted": len(keywords),
                "pattern_type": pattern_type,
                "is_gibberish": is_gibberish
            }
            
        except Exception as e:
            print(f"Error marking spam: {e}")
            return {"status": "error", "error": str(e)}
    
    def mark_false_positive(self, pattern_id: str) -> Dict[str, Any]:
        """
        Mark a spam detection as false positive and adjust learning
        """
        try:
            for pattern in self.data["spam_patterns"]:
                if pattern["pattern_id"] == pattern_id:
                    pattern["false_positive_count"] += 1
                    # Reduce confidence based on false positives
                    pattern["confidence"] = max(0.1, pattern["confidence"] - 0.2)
                    
                    self.data["learning_stats"]["false_positives"] += 1
                    self._save_data()
                    
                    print(f"📉 Marked {pattern_id} as false positive, reduced confidence to {pattern['confidence']:.2f}")
                    
                    return {
                        "status": "marked_false_positive",
                        "new_confidence": pattern["confidence"],
                        "false_positive_count": pattern["false_positive_count"]
                    }
            
            return {"status": "pattern_not_found"}
            
        except Exception as e:
            print(f"Error marking false positive: {e}")
            return {"status": "error", "error": str(e)}
    
    def get_performance_insights(self) -> Dict[str, Any]:
        """
        Generate performance insights comparing AI vs Human performance
        """
        try:
            recent_incidents = self._get_recent_incidents(days=self.performance_window)
            
            if not recent_incidents:
                return {
                    "status": "no_data",
                    "message": "No recent incidents for analysis"
                }
            
            # Analyze AI vs Human performance
            ai_metrics = []
            human_metrics = []
            
            for incident in recent_incidents:
                # Check both locations for confidence data
                confidence_data = incident.get("confidence_analysis", {})
                if not confidence_data:
                    # Try the stages location
                    stages = incident.get("stages", {})
                    evaluator = stages.get("evaluator", {})
                    confidence_data = evaluator.get("confidence_index", {})
                
                resolution_data = incident.get("resolution_data", {})
                
                if confidence_data.get("resolution_recommendation") == "autonomous":
                    ai_metrics.append({
                        "processing_time": incident.get("processing_time", 0),
                        "resources_used": incident.get("resources_used", 0),
                        "accuracy": confidence_data.get("overall_confidence", 0) / 100,
                        "incident_type": incident.get("incident_type", "unknown"),
                        "severity": incident.get("severity", "unknown")
                    })
                elif resolution_data.get("resolved_by_human", False):
                    human_metrics.append({
                        "processing_time": resolution_data.get("human_processing_time", 0),
                        "resources_used": resolution_data.get("human_resources_used", 0),
                        "accuracy": resolution_data.get("human_accuracy", 85) / 100,
                        "incident_type": incident.get("incident_type", "unknown"),
                        "severity": incident.get("severity", "unknown")
                    })
            
            # Calculate comparative statistics
            insights = self._calculate_performance_comparison(ai_metrics, human_metrics)
            
            # Add spam detection statistics
            spam_stats = self._get_spam_statistics()
            insights["spam_detection"] = spam_stats
            
            # Add learning progress
            learning_progress = self._get_learning_progress()
            insights["learning_progress"] = learning_progress
            
            return {
                "status": "success",
                "insights": insights,
                "data_period": f"Last {self.performance_window} days",
                "total_incidents_analyzed": len(recent_incidents)
            }
            
        except Exception as e:
            print(f"Error generating performance insights: {e}")
            return {"status": "error", "error": str(e)}
    
    def clear_history(self, confirm: bool = False) -> Dict[str, Any]:
        """
        Clear all historical data (use with caution)
        """
        if not confirm:
            return {
                "status": "confirmation_required",
                "message": "This will delete all learning data. Call with confirm=True to proceed."
            }
        
        try:
            # Backup current data
            backup_file = f"rl_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(backup_file, 'w') as f:
                json.dump(self.data, f, indent=2, default=str)
            
            # Reset data
            self.data = {
                "incidents": [],
                "spam_patterns": [],
                "performance_metrics": [],
                "learning_stats": {
                    "total_incidents": 0,
                    "spam_detected": 0,
                    "false_positives": 0,
                    "ai_vs_human_comparisons": 0,
                    "system_accuracy": 0.0,
                    "last_updated": datetime.now().isoformat()
                },
                "confidence_improvements": {},
                "decision_rewards": {}
            }
            
            self._save_data()
            
            print(f"🗑️ Cleared all RL history (backup saved as {backup_file})")
            
            return {
                "status": "cleared",
                "backup_file": backup_file,
                "message": "All learning data cleared successfully"
            }
            
        except Exception as e:
            print(f"Error clearing history: {e}")
            return {"status": "error", "error": str(e)}
    
    def _enhance_incident_with_rl(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance incident data with RL insights"""
        enhanced = incident_data.copy()
        
        # Add RL metadata
        enhanced["rl_metadata"] = {
            "added_at": datetime.now().isoformat(),
            "incident_number": len(self.data["incidents"]) + 1,
            "processing_time": enhanced.get("total_duration", 0),
            "resources_used": self._calculate_resources_used(enhanced),
            "confidence_analysis": enhanced.get("confidence_index", {}),
            "learning_applied": True
        }
        
        # Add historical context
        similar_incidents = self._find_similar_incidents(enhanced)
        enhanced["rl_metadata"]["similar_incidents_count"] = len(similar_incidents)
        enhanced["rl_metadata"]["historical_context"] = self._generate_historical_context(similar_incidents)
        
        return enhanced
    
    def _calculate_resources_used(self, incident_data: Dict[str, Any]) -> int:
        """Calculate resources used for incident processing"""
        resources = 0
        
        # Count stakeholders
        stages = incident_data.get("stages", {})
        if "planner" in stages:
            planner_result = stages["planner"]
            stakeholders = planner_result.get("action_plan", {}).get("stakeholders", [])
            resources += len(stakeholders)
        
        # Count immediate actions
        if "planner" in stages:
            planner_result = stages["planner"]
            actions = planner_result.get("action_plan", {}).get("immediate_actions", [])
            resources += len(actions)
        
        # Add base processing resource
        resources += 1
        
        return resources
    
    def _find_similar_incidents(self, incident_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find similar incidents from history"""
        similar = []
        
        incident_type = incident_data.get("incident_type", "")
        severity = incident_data.get("severity", "")
        
        for historical in self.data["incidents"]:
            if (historical.get("incident_type") == incident_type and 
                historical.get("severity") == severity):
                similar.append(historical)
        
        return similar[-10:]  # Return last 10 similar incidents
    
    def _generate_historical_context(self, similar_incidents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate historical context from similar incidents"""
        if not similar_incidents:
            return {"message": "No similar incidents in history"}
        
        # Calculate average confidence
        confidences = []
        resolutions = []
        
        for incident in similar_incidents:
            rl_meta = incident.get("rl_metadata", {})
            confidence_data = rl_meta.get("confidence_analysis", {})
            if confidence_data.get("overall_confidence"):
                confidences.append(confidence_data["overall_confidence"])
            
            # Track resolution types
            if confidence_data.get("resolution_recommendation"):
                resolutions.append(confidence_data["resolution_recommendation"])
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        return {
            "similar_count": len(similar_incidents),
            "average_confidence": avg_confidence,
            "common_resolution": max(set(resolutions), key=resolutions.count) if resolutions else "unknown",
            "trend": "improving" if len(confidences) > 1 and confidences[-1] > confidences[0] else "stable"
        }
    
    def _calculate_text_similarity(self, text1: str, keywords: List[str]) -> float:
        """Calculate similarity between text and keywords"""
        if not keywords:
            return 0.0
        
        text1_lower = text1.lower()
        matches = sum(1 for keyword in keywords if keyword.lower() in text1_lower)
        
        return matches / len(keywords)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for spam pattern matching"""
        # Simple keyword extraction (can be enhanced with NLP)
        words = text.lower().split()
        
        # Filter out common words
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "is", "are", "was", "were", "be", "been", "have", "has", "had", "do", "does", "did", "will", "would", "could", "should", "may", "might", "can", "this", "that", "these", "those", "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them"}
        
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        
        # Return top 10 most relevant keywords
        return keywords[:10]
    
    def _get_recent_incidents(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get incidents from the last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent = []
        
        for incident in self.data["incidents"]:
            rl_meta = incident.get("rl_metadata", {})
            added_at = rl_meta.get("added_at")
            
            if added_at:
                try:
                    incident_date = datetime.fromisoformat(added_at.replace('Z', '+00:00')).replace(tzinfo=None)
                    if incident_date >= cutoff_date:
                        recent.append(incident)
                except:
                    continue
        
        return recent
    
    def _calculate_performance_comparison(self, ai_metrics: List[Dict], human_metrics: List[Dict]) -> Dict[str, Any]:
        """Calculate AI vs Human performance comparison"""
        if not ai_metrics and not human_metrics:
            return {"message": "No performance data available"}
        
        comparison = {
            "ai_incidents": len(ai_metrics),
            "human_incidents": len(human_metrics),
            "total_incidents": len(ai_metrics) + len(human_metrics)
        }
        
        if ai_metrics:
            ai_avg_time = sum(m["processing_time"] for m in ai_metrics) / len(ai_metrics)
            ai_avg_resources = sum(m["resources_used"] for m in ai_metrics) / len(ai_metrics)
            ai_avg_accuracy = sum(m["accuracy"] for m in ai_metrics) / len(ai_metrics)
            
            comparison["ai_performance"] = {
                "average_processing_time": ai_avg_time,
                "average_resources_used": ai_avg_resources,
                "average_accuracy": ai_avg_accuracy,
                "efficiency_score": (ai_avg_accuracy / max(ai_avg_time, 0.1)) * 100
            }
        
        if human_metrics:
            human_avg_time = sum(m["processing_time"] for m in human_metrics) / len(human_metrics)
            human_avg_resources = sum(m["resources_used"] for m in human_metrics) / len(human_metrics)
            human_avg_accuracy = sum(m["accuracy"] for m in human_metrics) / len(human_metrics)
            
            comparison["human_performance"] = {
                "average_processing_time": human_avg_time,
                "average_resources_used": human_avg_resources,
                "average_accuracy": human_avg_accuracy,
                "efficiency_score": (human_avg_accuracy / max(human_avg_time, 0.1)) * 100
            }
        
        # Calculate improvements
        if ai_metrics and human_metrics:
            time_improvement = ((human_avg_time - ai_avg_time) / human_avg_time) * 100
            resource_improvement = ((human_avg_resources - ai_avg_resources) / human_avg_resources) * 100
            
            comparison["ai_improvements"] = {
                "time_saved_percentage": max(0, time_improvement),
                "resources_saved_percentage": max(0, resource_improvement),
                "overall_efficiency_gain": (comparison["ai_performance"]["efficiency_score"] - 
                                          comparison["human_performance"]["efficiency_score"])
            }
        
        return comparison
    
    def _get_spam_statistics(self) -> Dict[str, Any]:
        """Get spam detection statistics"""
        total_patterns = len(self.data["spam_patterns"])
        total_spam_detected = sum(p["marked_spam_count"] for p in self.data["spam_patterns"])
        total_false_positives = sum(p["false_positive_count"] for p in self.data["spam_patterns"])
        
        accuracy = ((total_spam_detected - total_false_positives) / max(total_spam_detected, 1)) * 100
        
        return {
            "total_spam_patterns": total_patterns,
            "total_spam_detected": total_spam_detected,
            "false_positives": total_false_positives,
            "detection_accuracy": accuracy,
            "active_patterns": len([p for p in self.data["spam_patterns"] if p["confidence"] > 0.5])
        }
    
    def _get_learning_progress(self) -> Dict[str, Any]:
        """Get learning progress statistics"""
        total_incidents = len(self.data["incidents"])
        
        if total_incidents < 10:
            return {"message": "Insufficient data for learning analysis"}
        
        # Analyze confidence trends over time
        recent_confidences = []
        for incident in self.data["incidents"][-20:]:  # Last 20 incidents
            rl_meta = incident.get("rl_metadata", {})
            confidence_data = rl_meta.get("confidence_analysis", {})
            if confidence_data.get("overall_confidence"):
                recent_confidences.append(confidence_data["overall_confidence"])
        
        if len(recent_confidences) > 5:
            early_avg = sum(recent_confidences[:5]) / 5
            recent_avg = sum(recent_confidences[-5:]) / 5
            improvement = recent_avg - early_avg
        else:
            improvement = 0
        
        return {
            "total_incidents_learned": total_incidents,
            "confidence_improvement": improvement,
            "learning_trend": "improving" if improvement > 0 else "stable" if improvement == 0 else "declining",
            "system_maturity": min(100, (total_incidents / 100) * 100)  # Mature at 100 incidents
        }
    
    def _update_learning_stats(self, incident_data: Dict[str, Any]):
        """Update learning statistics"""
        self.data["learning_stats"]["total_incidents"] += 1
        
        # Update system accuracy based on confidence
        rl_meta = incident_data.get("rl_metadata", {})
        confidence_data = rl_meta.get("confidence_analysis", {})
        
        if confidence_data.get("overall_confidence"):
            current_accuracy = self.data["learning_stats"]["system_accuracy"]
            new_confidence = confidence_data["overall_confidence"] / 100
            
            # Update running average
            total = self.data["learning_stats"]["total_incidents"]
            self.data["learning_stats"]["system_accuracy"] = (
                (current_accuracy * (total - 1) + new_confidence) / total
            )
    
    def _learn_from_incident(self, incident_data: Dict[str, Any]):
        """Learn from incident to improve future decisions"""
        # This is where reinforcement learning logic would go
        # For now, we'll implement basic pattern recognition
        
        incident_type = incident_data.get("incident_type", "unknown")
        severity = incident_data.get("severity", "unknown")
        
        rl_meta = incident_data.get("rl_metadata", {})
        confidence_data = rl_meta.get("confidence_analysis", {})
        
        # Store decision patterns
        decision_key = f"{incident_type}_{severity}"
        
        if decision_key not in self.data["decision_rewards"]:
            self.data["decision_rewards"][decision_key] = {
                "total_incidents": 0,
                "successful_resolutions": 0,
                "average_confidence": 0.0,
                "preferred_resolution": "supervised"
            }
        
        pattern = self.data["decision_rewards"][decision_key]
        pattern["total_incidents"] += 1
        
        if confidence_data.get("overall_confidence"):
            current_avg = pattern["average_confidence"]
            new_confidence = confidence_data["overall_confidence"]
            pattern["average_confidence"] = (
                (current_avg * (pattern["total_incidents"] - 1) + new_confidence) / 
                pattern["total_incidents"]
            )
            
            # Update preferred resolution based on success
            if confidence_data.get("resolution_recommendation"):
                pattern["preferred_resolution"] = confidence_data["resolution_recommendation"]
    
    def _generate_rl_insights(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate RL insights for the incident"""
        try:
            rl_meta = incident_data.get("rl_metadata", {})
            historical_context = rl_meta.get("historical_context", {})
            
            insights = {
                "learning_applied": True,
                "historical_context": historical_context,
                "incident_number": rl_meta.get("incident_number", 0),
                "similar_incidents": rl_meta.get("similar_incidents_count", 0),
                "processing_efficiency": {
                    "time": rl_meta.get("processing_time", 0),
                    "resources": rl_meta.get("resources_used", 0)
                }
            }
            
            # Add learning recommendations
            if historical_context.get("trend") == "improving":
                insights["recommendation"] = "System confidence is improving for this incident type"
            elif historical_context.get("similar_count", 0) > 5:
                insights["recommendation"] = "Sufficient historical data available for reliable processing"
            else:
                insights["recommendation"] = "Limited historical data - human oversight recommended"
            
            return insights
            
        except Exception as e:
            print(f"Error generating RL insights: {e}")
            return {
                "learning_applied": False,
                "error": str(e),
                "recommendation": "RL insights unavailable"
            }

# Global instance
rl_system = ReinforcementLearningSystem()