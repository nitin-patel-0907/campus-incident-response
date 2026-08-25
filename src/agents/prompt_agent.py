"""
Prompt Agent - Processes raw incident reports and extracts structured information
"""
from typing import Dict, Any, List
from .base_agent import BaseAgent
from datetime import datetime
import re


class PromptAgent(BaseAgent):
    """
    Agent responsible for processing raw incident reports and converting them
    into structured data that other agents can work with effectively
    """
    
    def __init__(self):
        super().__init__(
            name="Prompt Agent",
            description="Processes raw incident reports and extracts structured information"
        )
        self.incident_types = self._load_incident_types()
        self.severity_keywords = self._load_severity_keywords()
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw incident report and extract structured information
        
        Args:
            input_data: {
                "raw_report": str - Raw incident report text
                "metadata": dict - Optional metadata about the report
            }
        
        Returns:
            {
                "structured_report": dict - Structured incident data
                "extracted_entities": dict - Key entities found
                "completeness_score": float - Report completeness (0-100)
                "prompt_for_analysis": str - Formatted prompt for other agents
                "status": str
            }
        """
        try:
            raw_report = input_data.get("raw_report", "")
            metadata = input_data.get("metadata", {})
            
            if not raw_report or len(raw_report.strip()) < 10:
                return self.handle_error(
                    ValueError("Raw report is too short or empty"),
                    "Input validation"
                )
            
            # Extract structured information
            structured_report = self._extract_structured_data(raw_report)
            
            # Extract entities (people, locations, etc.)
            extracted_entities = self._extract_entities(raw_report)
            
            # Calculate completeness score
            completeness_score = self._calculate_completeness(structured_report, raw_report)
            
            # Generate analysis prompt
            analysis_prompt = self._generate_analysis_prompt(structured_report, raw_report)
            
            # Add metadata
            structured_report["metadata"] = metadata
            structured_report["processed_at"] = datetime.now().isoformat()
            
            output = self.create_success_response({
                "structured_report": structured_report,
                "extracted_entities": extracted_entities,
                "completeness_score": completeness_score,
                "prompt_for_analysis": analysis_prompt,
                "processing_notes": self._generate_processing_notes(structured_report, completeness_score)
            })
            
            self.log_execution(input_data, output, "success")
            return output
            
        except Exception as e:
            return self.handle_error(e, "Report processing")
    
    def _load_incident_types(self) -> Dict[str, List[str]]:
        """Load incident type classification keywords"""
        return {
            "assault": ["assault", "attack", "fight", "violence", "hit", "punch", "kick"],
            "harassment": ["harassment", "bullying", "intimidation", "threatening", "stalking", "harassed"],
            "theft": ["theft", "stolen", "missing", "burglar", "robbery", "taken", "stole"],
            "vandalism": ["vandalism", "damage", "graffiti", "destruction", "broken"],
            "medical": ["injury", "medical", "hurt", "pain", "emergency", "ambulance", "hospital", "injured", "broken"],
            "substance": ["alcohol", "drugs", "drinking", "intoxicated", "substance"],
            "policy_violation": ["violation", "unauthorized", "prohibited", "against policy"],
            "safety": ["safety", "hazard", "dangerous", "risk", "unsafe"],
            "discrimination": ["discrimination", "bias", "racist", "sexist", "prejudice"],
            "academic": ["cheating", "plagiarism", "academic", "dishonesty", "exam"]
        }
    
    def _load_severity_keywords(self) -> Dict[str, List[str]]:
        """Load severity classification keywords"""
        return {
            "critical": ["emergency", "critical", "severe", "life-threatening", "urgent", "immediate"],
            "high": ["serious", "significant", "major", "important", "concerning"],
            "medium": ["moderate", "notable", "standard", "typical"],
            "low": ["minor", "small", "slight", "minimal"]
        }
    
    def _extract_structured_data(self, raw_report: str) -> Dict[str, Any]:
        """Extract structured data from raw report"""
        report_lower = raw_report.lower()
        
        # Extract incident type
        incident_type = self._classify_incident_type(report_lower)
        
        # Extract severity
        severity = self._classify_severity(report_lower)
        
        # Extract date/time
        datetime_info = self._extract_datetime(raw_report)
        
        # Extract location
        location = self._extract_location(raw_report)
        
        # Extract involved parties
        involved_parties = self._extract_involved_parties(raw_report)
        
        # Extract description
        description = self._clean_description(raw_report)
        
        return {
            "incident_type": incident_type,
            "severity": severity,
            "datetime": datetime_info,
            "location": location,
            "involved_parties": involved_parties,
            "description": description,
            "report_length": len(raw_report),
            "word_count": len(raw_report.split())
        }
    
    def _classify_incident_type(self, report_lower: str) -> str:
        """Classify the type of incident"""
        type_scores = {}
        
        for incident_type, keywords in self.incident_types.items():
            score = sum(1 for keyword in keywords if keyword in report_lower)
            if score > 0:
                type_scores[incident_type] = score
        
        if type_scores:
            return max(type_scores, key=type_scores.get)
        else:
            return "general"
    
    def _classify_severity(self, report_lower: str) -> str:
        """Classify the severity of the incident"""
        for severity, keywords in self.severity_keywords.items():
            if any(keyword in report_lower for keyword in keywords):
                return severity
        
        # Default severity based on incident type
        if any(word in report_lower for word in ["assault", "violence", "emergency", "injury"]):
            return "high"
        elif any(word in report_lower for word in ["harassment", "theft", "vandalism"]):
            return "medium"
        else:
            return "low"
    
    def _extract_datetime(self, raw_report: str) -> str:
        """Extract date and time information"""
        # Look for date patterns
        date_patterns = [
            r'(\w+\s+\d{1,2},\s+\d{4})',  # January 28, 2025
            r'(\d{1,2}/\d{1,2}/\d{4})',   # 1/28/2025
            r'(\d{4}-\d{2}-\d{2})',       # 2025-01-28
        ]
        
        # Look for time patterns
        time_patterns = [
            r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))',  # 2:30 PM
            r'(\d{1,2}:\d{2})',                    # 14:30
            r'(approximately\s+\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))',  # approximately 2:30 PM
        ]
        
        found_dates = []
        found_times = []
        
        for pattern in date_patterns:
            matches = re.findall(pattern, raw_report)
            found_dates.extend(matches)
        
        for pattern in time_patterns:
            matches = re.findall(pattern, raw_report, re.IGNORECASE)
            found_times.extend(matches)
        
        if found_dates and found_times:
            return f"{found_dates[0]} at {found_times[0]}"
        elif found_dates:
            return found_dates[0]
        elif found_times:
            return f"Time: {found_times[0]}"
        else:
            return "Not specified"
    
    def _extract_location(self, raw_report: str) -> str:
        """Extract location information"""
        # Common campus location keywords
        location_keywords = [
            "library", "dormitory", "residence hall", "cafeteria", "gymnasium", 
            "parking lot", "classroom", "laboratory", "auditorium", "student center",
            "recreation center", "dining hall", "quad", "campus", "building"
        ]
        
        report_lower = raw_report.lower()
        
        # Look for specific location mentions
        for keyword in location_keywords:
            if keyword in report_lower:
                # Try to extract more specific location context
                sentences = raw_report.split('.')
                for sentence in sentences:
                    if keyword in sentence.lower():
                        # Extract the relevant part of the sentence
                        words = sentence.strip().split()
                        for i, word in enumerate(words):
                            if keyword in word.lower():
                                # Get surrounding context
                                start = max(0, i-3)
                                end = min(len(words), i+4)
                                location_context = ' '.join(words[start:end])
                                return location_context.strip()
        
        # Look for building names or room numbers
        building_pattern = r'([A-Z][a-z]+\s+(?:Hall|Building|Center|Library))'
        room_pattern = r'(room\s+\d+|floor\s+\d+|\d+(?:st|nd|rd|th)\s+floor)'
        
        building_match = re.search(building_pattern, raw_report)
        room_match = re.search(room_pattern, raw_report, re.IGNORECASE)
        
        if building_match and room_match:
            return f"{building_match.group(1)}, {room_match.group(1)}"
        elif building_match:
            return building_match.group(1)
        elif room_match:
            return room_match.group(1)
        
        return "Campus location not specified"
    
    def _extract_involved_parties(self, raw_report: str) -> List[Dict[str, str]]:
        """Extract information about involved parties"""
        parties = []
        
        # Look for student names (basic pattern)
        name_pattern = r'([A-Z][a-z]+\s+[A-Z][a-z]+)'
        names = re.findall(name_pattern, raw_report)
        
        for name in names:
            parties.append({
                "name": name,
                "role": "student",  # Default assumption
                "type": "individual"
            })
        
        # Look for role mentions
        role_keywords = {
            "student": ["student", "freshman", "sophomore", "junior", "senior"],
            "staff": ["staff", "employee", "worker"],
            "faculty": ["professor", "instructor", "teacher", "faculty"],
            "security": ["security", "officer", "guard"],
            "witness": ["witness", "bystander", "observer"]
        }
        
        report_lower = raw_report.lower()
        for role, keywords in role_keywords.items():
            for keyword in keywords:
                if keyword in report_lower:
                    parties.append({
                        "role": role,
                        "type": "role_mention",
                        "context": keyword
                    })
        
        return parties
    
    def _clean_description(self, raw_report: str) -> str:
        """Clean and format the description"""
        # Remove extra whitespace and normalize
        description = ' '.join(raw_report.split())
        
        # Truncate if too long (keep first 500 characters)
        if len(description) > 500:
            description = description[:500] + "..."
        
        return description
    
    def _extract_entities(self, raw_report: str) -> Dict[str, List[str]]:
        """Extract key entities from the report"""
        entities = {
            "people": [],
            "locations": [],
            "objects": [],
            "times": [],
            "organizations": []
        }
        
        # Extract people (names)
        name_pattern = r'([A-Z][a-z]+\s+[A-Z][a-z]+)'
        entities["people"] = re.findall(name_pattern, raw_report)
        
        # Extract locations
        location_pattern = r'([A-Z][a-z]+\s+(?:Hall|Building|Center|Library|Room))'
        entities["locations"] = re.findall(location_pattern, raw_report)
        
        # Extract objects (valuable items, etc.)
        object_keywords = ["laptop", "phone", "wallet", "backpack", "car", "bicycle", "equipment"]
        report_lower = raw_report.lower()
        entities["objects"] = [obj for obj in object_keywords if obj in report_lower]
        
        # Extract time references
        time_pattern = r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))'
        entities["times"] = re.findall(time_pattern, raw_report)
        
        # Extract organizations/departments
        org_keywords = ["security", "police", "EMT", "counseling", "administration"]
        entities["organizations"] = [org for org in org_keywords if org.lower() in report_lower]
        
        return entities
    
    def _calculate_completeness(self, structured_report: Dict[str, Any], raw_report: str) -> float:
        """Calculate how complete the incident report is"""
        score = 0.0
        max_score = 100.0
        
        # Check required fields
        required_fields = {
            "incident_type": 20,
            "datetime": 20,
            "location": 20,
            "description": 20
        }
        
        for field, points in required_fields.items():
            value = structured_report.get(field, "")
            if value and value not in ["Not specified", "Campus location not specified", "general"]:
                score += points
        
        # Bonus points for additional details
        if len(structured_report.get("involved_parties", [])) > 0:
            score += 10
        
        if structured_report.get("word_count", 0) > 50:
            score += 10
        
        return min(score, max_score)
    
    def _generate_analysis_prompt(self, structured_report: Dict[str, Any], raw_report: str) -> str:
        """Generate a formatted prompt for other agents"""
        return f"""
INCIDENT ANALYSIS REQUEST

Type: {structured_report['incident_type']}
Severity: {structured_report['severity']}
Date/Time: {structured_report['datetime']}
Location: {structured_report['location']}

Description:
{structured_report['description']}

Involved Parties: {len(structured_report['involved_parties'])} identified

Please analyze this incident and provide appropriate response recommendations.
"""
    
    def _generate_processing_notes(self, structured_report: Dict[str, Any], completeness_score: float) -> List[str]:
        """Generate notes about the processing"""
        notes = []
        
        if completeness_score < 60:
            notes.append("Report may be incomplete - consider requesting additional information")
        
        if structured_report['incident_type'] == 'general':
            notes.append("Incident type could not be clearly determined from the report")
        
        if structured_report['datetime'] == 'Not specified':
            notes.append("Date and time information is missing or unclear")
        
        if structured_report['location'] == 'Campus location not specified':
            notes.append("Specific location information is missing")
        
        if len(structured_report['involved_parties']) == 0:
            notes.append("No specific individuals identified in the report")
        
        if structured_report['word_count'] < 30:
            notes.append("Report is very brief - additional details may be needed")
        
        return notes