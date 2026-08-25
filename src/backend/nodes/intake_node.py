"""
Intake Node - Real-time incident data processing and validation with human review controls
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import re
import json
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from pydantic import BaseModel, Field
from ..llm.multi_provider_client import multi_llm_client
from ..services.human_review_service import human_review_service, ReviewReason


class IncidentData(BaseModel):
    """Structured incident data model"""
    incident_id: str = Field(description="Unique incident identifier")
    raw_report: str = Field(description="Original incident report text")
    title: str = Field(description="Incident title")
    description: str = Field(description="Processed incident description")
    location: str = Field(description="Incident location")
    incident_type: str = Field(description="Type of incident")
    severity: str = Field(description="Incident severity level")
    priority: str = Field(description="Response priority")
    reporter_info: Dict[str, Any] = Field(description="Reporter information")
    timestamp: str = Field(description="Incident timestamp")
    entities: Dict[str, List[str]] = Field(description="Extracted entities")
    confidence_score: float = Field(description="Processing confidence score")
    validation_status: str = Field(description="Validation status")
    metadata: Dict[str, Any] = Field(description="Additional metadata")
    processing_timestamp: Optional[str] = Field(default=None, description="Processing timestamp")
    tags: Optional[List[str]] = Field(default_factory=list, description="Incident tags")
    requires_human_review: bool = Field(default=False, description="Whether human review is required")
    review_reasons: List[str] = Field(default_factory=list, description="Reasons for human review")
    file_analyses: List[Dict[str, Any]] = Field(default_factory=list, description="File authenticity analyses")


class IntakeNodeState(BaseModel):
    """State model for intake node processing"""
    messages: List[BaseMessage] = Field(default_factory=list)
    incident_data: Optional[IncidentData] = None
    processing_status: str = Field(default="pending")
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    next_node: str = Field(default="planner")
    original_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Original metadata from request")


class IntakeNode:
    """
    LangGraph node for processing incoming incident reports in real-time
    """
    
    def __init__(self):
        self.name = "intake_node"
        self.incident_types = self._load_incident_types()
        self.severity_keywords = self._load_severity_keywords()
        self.location_patterns = self._load_location_patterns()
        
    def __call__(self, state: IntakeNodeState) -> IntakeNodeState:
        """
        Process incoming incident data
        
        Args:
            state: Current processing state
            
        Returns:
            Updated state with processed incident data
        """
        try:
            # Extract raw report from messages
            raw_report = self._extract_raw_report(state.messages)
            
            if not raw_report:
                state.errors.append("No incident report found in messages")
                state.processing_status = "error"
                return state
            
            # Generate incident ID
            incident_id = self._generate_incident_id()
            
            # Process the incident report (pass state for metadata access)
            incident_data = self._process_incident_report(raw_report, incident_id, state)
            
            # Check if human review is required
            file_analyses = state.original_metadata.get('file_analyses', []) if state.original_metadata else []
            requires_review, review_reasons, review_explanation = human_review_service.requires_human_review(
                incident_data.dict(), file_analyses
            )
            
            # Update incident data with review requirements
            incident_data.requires_human_review = requires_review
            incident_data.review_reasons = [reason.value for reason in review_reasons]
            incident_data.file_analyses = file_analyses
            
            # If human review is required, add to review queue and set status
            if requires_review:
                human_review_service.add_to_review_queue(
                    incident_id, incident_data.dict(), review_reasons, review_explanation, file_analyses
                )
                # Force status to unresolved for human review
                incident_data.validation_status = "unresolved_pending_review"
                
                # Add review information to metadata
                incident_data.metadata.update({
                    "requires_human_review": True,
                    "review_reasons": [reason.value for reason in review_reasons],
                    "review_explanation": review_explanation,
                    "review_status": "pending"
                })
                
                # Set next node to safety for high-priority items, otherwise pause workflow
                if incident_data.severity in ["critical", "high"]:
                    state.next_node = "safety"  # Still do safety check even if pending review
                else:
                    state.next_node = "human_review_pause"  # Custom node to pause workflow
            else:
                # Normal processing flow
                if incident_data.severity in ["critical", "high"]:
                    state.next_node = "safety"
                else:
                    state.next_node = "planner"
            
            # Validate the processed data
            validation_result = self._validate_incident_data(incident_data)
            
            # Update state
            state.incident_data = incident_data
            state.processing_status = "completed"
            state.warnings.extend(validation_result.get("warnings", []))
            
            # Add processing message with review status
            if incident_data.requires_human_review:
                processing_msg = AIMessage(
                    content=f"Incident {incident_id} processed and queued for human review. "
                           f"Type: {incident_data.incident_type}, "
                           f"Severity: {incident_data.severity}, "
                           f"Review required: {', '.join(incident_data.review_reasons)}"
                )
            else:
                processing_msg = AIMessage(
                    content=f"Incident {incident_id} processed successfully. "
                           f"Type: {incident_data.incident_type}, "
                           f"Severity: {incident_data.severity}, "
                           f"Confidence: {incident_data.confidence_score:.2f}"
                )
            state.messages.append(processing_msg)
                
            return state
            
        except Exception as e:
            state.errors.append(f"Intake processing error: {str(e)}")
            state.processing_status = "error"
            return state
    
    def _extract_raw_report(self, messages: List[BaseMessage]) -> str:
        """Extract raw incident report from messages"""
        for message in reversed(messages):  # Check latest messages first
            if isinstance(message, HumanMessage):
                content = message.content
                if isinstance(content, str) and len(content.strip()) > 20:
                    return content.strip()
            # Also check if it's a dict with content
            elif hasattr(message, 'content') and isinstance(message.content, str):
                if len(message.content.strip()) > 20:
                    return message.content.strip()
        
        # If no proper message found, check if there's any text content
        for message in messages:
            if hasattr(message, 'content'):
                content = str(message.content)
                if len(content.strip()) > 20:
                    return content.strip()
        
        return ""
    
    def _generate_incident_id(self) -> str:
        """Generate unique incident ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"INC-{timestamp}"
    
    def _process_incident_report(self, raw_report: str, incident_id: str, state: IntakeNodeState) -> IncidentData:
        """Process raw incident report into structured data using OpenAI"""
        
        # First try to get intelligent analysis from OpenAI
        try:
            # Extract basic info for OpenAI analysis
            incident_type = self._classify_incident_type(raw_report)
            severity = self._classify_severity(raw_report, incident_type)
            
            # Get AI analysis
            ai_analysis = multi_llm_client.analyze_incident(raw_report, incident_type, severity)
            
            # Use AI analysis if available
            if ai_analysis and 'incident_analysis' in ai_analysis:
                analysis = ai_analysis['incident_analysis']
                entities = ai_analysis.get('entities', {})
                confidence_score = ai_analysis.get('confidence_score', 85.0)
                
                # Extract location from AI analysis or fallback to manual extraction
                location = self._extract_location(raw_report)
                
                # Handle anonymous vs identified reporting
                reporter_info = self._extract_reporter_info(raw_report, state)
                
                # Extract timestamps from metadata
                incident_timestamp = self._extract_incident_timestamp(state)
                submission_timestamp = self._extract_submission_timestamp(state)
                
                # Preserve form_submission flag
                form_submission_flag = False
                if state.original_metadata:
                    form_submission_flag = state.original_metadata.get('form_submission', False)
                
                return IncidentData(
                    incident_id=incident_id,
                    raw_report=raw_report,
                    title=self._extract_title(raw_report),
                    description=analysis.get('description', self._clean_description(raw_report)),
                    location=location,
                    incident_type=incident_type,
                    severity=severity,
                    priority=self._determine_priority(severity, incident_type),
                    entities=entities,
                    reporter_info=reporter_info,
                    confidence_score=confidence_score,
                    timestamp=incident_timestamp,  # When incident occurred
                    validation_status="ai_processed",
                    processing_timestamp=datetime.now().isoformat(),  # When processed by system
                    tags=self._generate_tags(incident_type, severity, analysis.get('key_factors', [])),
                    metadata={
                        "ai_enhanced": True,
                        "urgency_level": analysis.get('urgency_level', 'standard'),
                        "risk_assessment": analysis.get('risk_assessment', 'Standard risk level'),
                        "key_factors": analysis.get('key_factors', []),
                        # Preserve original metadata flags
                        "form_submission": form_submission_flag,
                        "anonymous_report": reporter_info.get("anonymous", False),
                        "incident_timestamp": incident_timestamp,  # When incident occurred
                        "submission_timestamp": submission_timestamp,  # When report was submitted
                        "processing_timestamp": datetime.now().isoformat()  # When processed by AI
                    }
                )
        except Exception as e:
            print(f"AI analysis failed, using fallback: {e}")
        
        # Fallback to manual processing if OpenAI fails
        title = self._extract_title(raw_report)
        description = self._clean_description(raw_report)
        location = self._extract_location(raw_report)
        
        # Classify incident
        incident_type = self._classify_incident_type(raw_report)
        severity = self._classify_severity(raw_report, incident_type)
        priority = self._determine_priority(severity, incident_type)
        
        # Extract entities
        entities = self._extract_entities(raw_report)
        
        # Handle anonymous vs identified reporting
        reporter_info = self._extract_reporter_info(raw_report, state)
        
        # Extract timestamps from metadata
        incident_timestamp = self._extract_incident_timestamp(state)
        submission_timestamp = self._extract_submission_timestamp(state)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(
            raw_report, incident_type, severity, location, entities
        )
        
        # Preserve form_submission flag
        form_submission_flag = False
        if state.original_metadata:
            form_submission_flag = state.original_metadata.get('form_submission', False)
        
        return IncidentData(
            incident_id=incident_id,
            raw_report=raw_report,
            title=title,
            description=description,
            location=location,
            incident_type=incident_type,
            severity=severity,
            priority=priority,
            reporter_info=reporter_info,
            timestamp=incident_timestamp,  # When incident occurred
            entities=entities,
            confidence_score=confidence_score,
            validation_status="processed",
            metadata={
                "processing_time": datetime.now().isoformat(),
                "word_count": len(raw_report.split()),
                "character_count": len(raw_report),
                # Preserve original metadata flags
                "form_submission": form_submission_flag,
                "anonymous_report": reporter_info.get("anonymous", False),
                "incident_timestamp": incident_timestamp,  # When incident occurred
                "submission_timestamp": submission_timestamp,  # When report was submitted
                "processing_timestamp": datetime.now().isoformat()  # When processed by system
            }
        )
    
    def _extract_title(self, raw_report: str) -> str:
        """Extract or generate incident title"""
        lines = raw_report.split('\n')
        first_line = lines[0].strip()
        
        # If first line is short and descriptive, use it as title
        if len(first_line) < 100 and len(first_line) > 10:
            return first_line
        
        # Generate title from incident type and key words
        words = raw_report.lower().split()
        key_words = []
        
        # Look for important keywords
        important_keywords = [
            "theft", "stolen", "missing", "assault", "harassment", "injury",
            "fire", "emergency", "vandalism", "damage", "broken", "leak",
            "suspicious", "threat", "violence", "accident"
        ]
        
        for keyword in important_keywords:
            if keyword in words:
                key_words.append(keyword.title())
        
        if key_words:
            return f"{' & '.join(key_words[:2])} Incident"
        else:
            return "Campus Incident Report"
    
    def _clean_description(self, raw_report: str) -> str:
        """Clean and format description"""
        # Remove extra whitespace
        description = ' '.join(raw_report.split())
        
        # Limit length for processing efficiency
        if len(description) > 1000:
            description = description[:1000] + "..."
        
        return description
    
    def _extract_location(self, raw_report: str) -> str:
        """Extract location information using patterns"""
        report_lower = raw_report.lower()
        
        # First, look for explicit location indicators with better parsing
        location_patterns = [
            r'(?:at|in|near|by|outside|inside)\s+(?:the\s+)?([^.!?,]+?)(?:\s+(?:needs|requires|has|is|was|-)|\.|,|$)',
            r'location[:\s]+(?:the\s+)?([^.!?,]+?)(?:\s+(?:needs|requires|has|is|was|-)|\.|,|$)',
            r'(?:building|hall|center|library|room|floor|area)[:\s]*(?:the\s+)?([^.!?,]+?)(?:\s+(?:needs|requires|has|is|was|-)|\.|,|$)',
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, raw_report, re.IGNORECASE)
            for match in matches:
                location = match.strip()
                # Clean up common words that shouldn't be in location
                location = re.sub(r'\s+(needs|requires|has|is|was|repair|attention|help|issue|problem).*$', '', location, flags=re.IGNORECASE)
                if len(location) > 3 and len(location) < 50:  # Reasonable length
                    return location.title()
        
        # Look for specific building/facility names
        building_patterns = [
            r'([A-Z][a-z]+\s+(?:Hall|Building|Center|Library|Gymnasium|Cafeteria|Dormitory))',
            r'(Student\s+Center|Recreation\s+Center|Dining\s+Hall|Administration\s+Building)',
            r'(Room\s+\d+[A-Z]?|Floor\s+\d+|\d+(?:st|nd|rd|th)\s+[Ff]loor)',
        ]
        
        for pattern in building_patterns:
            match = re.search(pattern, raw_report, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Look for outdoor locations
        outdoor_patterns = [
            r'(parking\s+lot)(?:\s+[^.!?,]*)?',
            r'(quad|courtyard|campus\s+grounds)',
            r'(sidewalk|pathway|entrance|exit)',
        ]
        
        for pattern in outdoor_patterns:
            match = re.search(pattern, raw_report, re.IGNORECASE)
            if match:
                return match.group(1).strip().title()
        
        # Look for common location words with context
        location_words = [
            'library', 'cafeteria', 'gymnasium', 'dormitory', 'classroom',
            'laboratory', 'office', 'bathroom', 'restroom', 'elevator',
            'stairwell', 'hallway', 'lobby', 'parking'
        ]
        
        words = raw_report.lower().split()
        for i, word in enumerate(words):
            for loc_word in location_words:
                if loc_word in word:
                    # Get context around the location word (but limit it)
                    start = max(0, i-1)
                    end = min(len(words), i+2)
                    context_words = words[start:end]
                    
                    # Remove common non-location words
                    filtered_words = []
                    for w in context_words:
                        if not any(stop in w for stop in ['needs', 'requires', 'has', 'is', 'was', 'the', 'a', 'an']):
                            filtered_words.append(w)
                    
                    if filtered_words:
                        return ' '.join(filtered_words).title()
        
        # If no specific location found, return a generic message
        return "Campus location (specific location not identified)"
    
    def _classify_incident_type(self, raw_report: str) -> str:
        """Classify incident type using keyword matching"""
        report_lower = raw_report.lower()
        type_scores = {}
        
        for incident_type, keywords in self.incident_types.items():
            score = sum(1 for keyword in keywords if keyword in report_lower)
            if score > 0:
                type_scores[incident_type] = score
        
        if type_scores:
            return max(type_scores, key=type_scores.get)
        else:
            return "general"
    
    def _classify_severity(self, raw_report: str, incident_type: str) -> str:
        """Classify incident severity"""
        report_lower = raw_report.lower()
        
        # Check for explicit severity keywords
        for severity, keywords in self.severity_keywords.items():
            if any(keyword in report_lower for keyword in keywords):
                return severity
        
        # Infer severity from incident type and context
        if incident_type in ["assault", "medical", "fire", "emergency"]:
            return "high"
        elif incident_type in ["harassment", "theft", "vandalism"]:
            return "medium"
        else:
            return "low"
    
    def _determine_priority(self, severity: str, incident_type: str) -> str:
        """Determine response priority"""
        if severity == "critical":
            return "immediate"
        elif severity == "high" or incident_type in ["assault", "medical", "fire"]:
            return "urgent"
        elif severity == "medium":
            return "standard"
        else:
            return "low"
    
    def _extract_entities(self, raw_report: str) -> Dict[str, List[str]]:
        """Extract named entities from the report"""
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
        
        # Extract objects
        object_keywords = ["laptop", "phone", "wallet", "backpack", "car", "bicycle", "equipment"]
        report_lower = raw_report.lower()
        entities["objects"] = [obj for obj in object_keywords if obj in report_lower]
        
        # Extract time references
        time_pattern = r'(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm))'
        entities["times"] = re.findall(time_pattern, raw_report)
        
        # Extract organizations
        org_keywords = ["security", "police", "EMT", "counseling", "administration"]
        entities["organizations"] = [org for org in org_keywords if org.lower() in report_lower]
        
        return entities
    
    def _extract_reporter_info(self, raw_report: str, state: IntakeNodeState = None) -> Dict[str, Any]:
        """Extract reporter information with anonymous reporting support"""
        
        # Check if this is an anonymous report from metadata
        is_anonymous = False
        if state and state.original_metadata:
            is_anonymous = state.original_metadata.get('anonymous_report', False)
            
            # If we have reporter_info in metadata, use it
            if 'reporter_info' in state.original_metadata:
                original_reporter = state.original_metadata['reporter_info']
                if isinstance(original_reporter, dict):
                    if original_reporter.get('anonymous', False):
                        # Generate pseudonymous ID for anonymous reports
                        pseudonymous_id = self._generate_pseudonymous_id()
                        return {
                            "pseudonymous_id": pseudonymous_id,
                            "role": original_reporter.get('role', 'unknown'),
                            "anonymous": True,
                            "contact": "",
                            "witness": False
                        }
                    else:
                        # Return identified reporter info (but this should not be shown in UI)
                        return {
                            "name": original_reporter.get('name', 'Unknown'),
                            "university_id": original_reporter.get('university_id', ''),
                            "role": original_reporter.get('role', 'unknown'),
                            "anonymous": False,
                            "contact": "",
                            "witness": False
                        }
        
        # Fallback: extract from report text (legacy behavior)
        reporter_info = {
            "name": "Anonymous",
            "contact": "",
            "role": "unknown",
            "witness": False,
            "anonymous": True,
            "pseudonymous_id": self._generate_pseudonymous_id()
        }
        
        # Look for name patterns (only if not anonymous)
        if not is_anonymous:
            name_pattern = r'(?:reported by|from|by)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)'
            name_match = re.search(name_pattern, raw_report, re.IGNORECASE)
            if name_match:
                reporter_info["name"] = name_match.group(1)
                reporter_info["anonymous"] = False
                del reporter_info["pseudonymous_id"]  # Remove pseudonymous ID if we have real identity
        
        # Look for email patterns (only if not anonymous)
        if not is_anonymous:
            email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
            email_match = re.search(email_pattern, raw_report)
            if email_match:
                reporter_info["contact"] = email_match.group(1)
        
        # Determine if reporter is a witness
        witness_keywords = ["witnessed", "saw", "observed", "noticed"]
        if any(keyword in raw_report.lower() for keyword in witness_keywords):
            reporter_info["witness"] = True
        
        return reporter_info
    
    def _generate_pseudonymous_id(self) -> str:
        """Generate a pseudonymous ID for anonymous reports"""
        import hashlib
        import uuid
        
        # Generate a unique pseudonymous ID
        unique_data = f"{datetime.now().isoformat()}-{uuid.uuid4().hex}"
        hash_object = hashlib.sha256(unique_data.encode())
        hash_hex = hash_object.hexdigest()
        
        # Create a human-readable pseudonymous ID
        return f"ANON-{hash_hex[:8].upper()}"
    
    def _extract_incident_timestamp(self, state: IntakeNodeState) -> str:
        """Extract the timestamp when the incident occurred"""
        if state and state.original_metadata:
            # Check for incident_date_time first (new field)
            incident_time = state.original_metadata.get('incident_date_time')
            if incident_time:
                return incident_time
            
            # Fallback to old date_time field for backward compatibility
            date_time = state.original_metadata.get('date_time')
            if date_time:
                return date_time
        
        # If no incident time specified, use current time as fallback
        return datetime.now().isoformat()
    
    def _extract_submission_timestamp(self, state: IntakeNodeState) -> str:
        """Extract the timestamp when the report was submitted"""
        if state and state.original_metadata:
            submission_time = state.original_metadata.get('submission_timestamp')
            if submission_time:
                return submission_time
        
        # If no submission timestamp, use current time
        return datetime.now().isoformat()
    
    def _calculate_confidence_score(self, raw_report: str, incident_type: str, 
                                  severity: str, location: str, entities: Dict) -> float:
        """Calculate confidence score for the processing"""
        score = 0.0
        
        # Base score for having a report
        score += 20.0
        
        # Score for incident type classification
        if incident_type != "general":
            score += 20.0
        
        # Score for severity classification
        if severity in ["critical", "high", "medium"]:
            score += 15.0
        
        # Score for location identification
        if "specific location not identified" not in location:
            score += 15.0
        
        # Score for entity extraction
        total_entities = sum(len(entity_list) for entity_list in entities.values())
        score += min(total_entities * 2, 15.0)
        
        # Score for report length and detail
        word_count = len(raw_report.split())
        if word_count > 50:
            score += 10.0
        elif word_count > 20:
            score += 5.0
        
        # Score for structured information
        if any(pattern in raw_report.lower() for pattern in ["time:", "location:", "date:"]):
            score += 5.0
        
        return min(score, 100.0)
    
    def _validate_incident_data(self, incident_data: IncidentData) -> Dict[str, Any]:
        """Validate processed incident data"""
        warnings = []
        
        if incident_data.confidence_score < 60:
            warnings.append("Low confidence score - may need manual review")
        
        if incident_data.incident_type == "general":
            warnings.append("Could not determine specific incident type")
        
        if "specific location not identified" in incident_data.location:
            warnings.append("Location information is incomplete")
        
        if not incident_data.entities["people"]:
            warnings.append("No individuals identified in the report")
        
        if len(incident_data.description.split()) < 20:
            warnings.append("Report may be too brief for complete analysis")
        
        return {
            "status": "validated",
            "warnings": warnings
        }
    
    def _generate_tags(self, incident_type: str, severity: str, key_factors: List[str]) -> List[str]:
        """Generate tags for the incident"""
        tags = [incident_type, severity]
        
        # Add priority tags
        if severity in ['critical', 'high']:
            tags.append('urgent')
        
        # Add type-specific tags
        if incident_type == 'medical':
            tags.extend(['emergency', 'health'])
        elif incident_type == 'fire':
            tags.extend(['emergency', 'evacuation'])
        elif incident_type == 'theft':
            tags.extend(['security', 'investigation'])
        elif incident_type == 'assault':
            tags.extend(['security', 'law_enforcement'])
        
        # Add factor-based tags
        for factor in key_factors:
            if 'emergency' in factor.lower():
                tags.append('emergency_response')
            elif 'safety' in factor.lower():
                tags.append('safety_concern')
        
        return list(set(tags))  # Remove duplicates
    
    def _load_incident_types(self) -> Dict[str, List[str]]:
        """Load incident type classification keywords"""
        return {
            "assault": ["assault", "attack", "fight", "violence", "hit", "punch", "kick", "beaten"],
            "harassment": ["harassment", "bullying", "intimidation", "threatening", "stalking", "harassed"],
            "theft": ["theft", "stolen", "missing", "burglar", "robbery", "taken", "stole", "robbed"],
            "vandalism": ["vandalism", "damage", "graffiti", "destruction", "broken", "destroyed"],
            "medical": ["injury", "medical", "hurt", "pain", "emergency", "ambulance", "hospital", "injured"],
            "substance": ["alcohol", "drugs", "drinking", "intoxicated", "substance", "drunk"],
            "fire": ["fire", "smoke", "burning", "flames", "evacuation"],
            "safety": ["safety", "hazard", "dangerous", "risk", "unsafe", "accident"],
            "discrimination": ["discrimination", "bias", "racist", "sexist", "prejudice"],
            "academic": ["cheating", "plagiarism", "academic", "dishonesty", "exam"],
            "maintenance": ["maintenance", "repair", "broken", "leak", "electrical", "plumbing"]
        }
    
    def _load_severity_keywords(self) -> Dict[str, List[str]]:
        """Load severity classification keywords"""
        return {
            "critical": ["emergency", "critical", "severe", "life-threatening", "urgent", "immediate"],
            "high": ["serious", "significant", "major", "important", "concerning", "dangerous"],
            "medium": ["moderate", "notable", "standard", "typical", "minor concern"],
            "low": ["minor", "small", "slight", "minimal", "routine"]
        }
    
    def _load_location_patterns(self) -> Dict[str, List[str]]:
        """Load location identification patterns"""
        return {
            "buildings": [
                "library", "dormitory", "residence hall", "cafeteria", "gymnasium",
                "student center", "recreation center", "dining hall", "auditorium",
                "classroom", "laboratory", "administration building"
            ],
            "outdoor": [
                "parking lot", "quad", "courtyard", "campus grounds", "sidewalk",
                "entrance", "exit", "pathway", "garden", "field"
            ],
            "facilities": [
                "bathroom", "restroom", "elevator", "stairwell", "hallway",
                "lobby", "office", "study room", "computer lab"
            ]
        }


# Export the node for use in the graph
def create_intake_node() -> IntakeNode:
    """Factory function to create intake node"""
    return IntakeNode()