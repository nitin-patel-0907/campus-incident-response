"""
Real-time Data Simulator for Campus Incident Response System
"""
from typing import Dict, Any, List, Optional, Generator
from datetime import datetime, timedelta
import random
import json
import asyncio
from dataclasses import dataclass
from enum import Enum


class IncidentType(Enum):
    """Enumeration of incident types"""
    MEDICAL = "medical"
    THEFT = "theft"
    FIRE = "fire"
    SECURITY = "security"
    MAINTENANCE = "maintenance"
    HARASSMENT = "harassment"
    ASSAULT = "assault"
    VANDALISM = "vandalism"
    SUBSTANCE = "substance"
    ACADEMIC = "academic"


class SeverityLevel(Enum):
    """Enumeration of severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SimulationParameters:
    """Parameters for data simulation"""
    incident_rate_per_hour: float = 2.0
    peak_hours: List[int] = None  # Hours with higher incident rates
    seasonal_factors: Dict[str, float] = None
    location_weights: Dict[str, float] = None
    incident_type_distribution: Dict[IncidentType, float] = None
    severity_distribution: Dict[SeverityLevel, float] = None
    
    def __post_init__(self):
        if self.peak_hours is None:
            self.peak_hours = [12, 13, 17, 18, 19, 20, 21]  # Lunch and evening hours
        
        if self.seasonal_factors is None:
            self.seasonal_factors = {
                "spring": 1.2,
                "summer": 0.8,
                "fall": 1.3,
                "winter": 0.9
            }
        
        if self.location_weights is None:
            self.location_weights = {
                "dormitory": 0.25,
                "library": 0.15,
                "dining_hall": 0.12,
                "gymnasium": 0.10,
                "parking_lot": 0.15,
                "classroom": 0.08,
                "laboratory": 0.05,
                "administration": 0.03,
                "outdoor_campus": 0.07
            }
        
        if self.incident_type_distribution is None:
            self.incident_type_distribution = {
                IncidentType.MEDICAL: 0.20,
                IncidentType.THEFT: 0.18,
                IncidentType.MAINTENANCE: 0.15,
                IncidentType.SECURITY: 0.12,
                IncidentType.VANDALISM: 0.10,
                IncidentType.HARASSMENT: 0.08,
                IncidentType.FIRE: 0.05,
                IncidentType.ASSAULT: 0.04,
                IncidentType.SUBSTANCE: 0.04,
                IncidentType.ACADEMIC: 0.04
            }
        
        if self.severity_distribution is None:
            self.severity_distribution = {
                SeverityLevel.LOW: 0.40,
                SeverityLevel.MEDIUM: 0.35,
                SeverityLevel.HIGH: 0.20,
                SeverityLevel.CRITICAL: 0.05
            }


class RealTimeDataSimulator:
    """
    Real-time data simulator for campus incident response system
    """
    
    def __init__(self, parameters: Optional[SimulationParameters] = None):
        self.parameters = parameters or SimulationParameters()
        self.incident_templates = self._load_incident_templates()
        self.location_details = self._load_location_details()
        self.reporter_profiles = self._load_reporter_profiles()
        self.running = False
        
    def _load_incident_templates(self) -> Dict[IncidentType, List[Dict[str, Any]]]:
        """Load incident report templates"""
        return {
            IncidentType.MEDICAL: [
                {
                    "template": "Student {name} collapsed during {activity} in the {location}. {condition_description} {witness_info}",
                    "variables": {
                        "activity": ["basketball game", "study session", "class", "workout", "meeting"],
                        "condition_description": [
                            "Appears to be unconscious and not responding.",
                            "Conscious but complaining of chest pain.",
                            "Difficulty breathing and appears distressed.",
                            "Bleeding from head injury after fall.",
                            "Allergic reaction with visible swelling."
                        ],
                        "witness_info": [
                            "Multiple witnesses present.",
                            "Roommate called for help.",
                            "Faculty member is providing assistance.",
                            "Other students are gathering around.",
                            "Security has been notified."
                        ]
                    }
                },
                {
                    "template": "Faculty member {name} reported {medical_issue} in {location}. {urgency_level} {action_taken}",
                    "variables": {
                        "medical_issue": [
                            "severe headache and dizziness",
                            "chest pains",
                            "difficulty breathing",
                            "allergic reaction",
                            "fall with possible injury"
                        ],
                        "urgency_level": [
                            "Requesting immediate medical assistance.",
                            "Appears stable but needs evaluation.",
                            "Condition seems serious.",
                            "Medical assistance may be needed.",
                            "Conscious and alert but in pain."
                        ],
                        "action_taken": [
                            "Colleague is staying with them.",
                            "First aid has been administered.",
                            "Security is en route.",
                            "Paramedics have been called.",
                            "Moving to health center."
                        ]
                    }
                }
            ],
            
            IncidentType.THEFT: [
                {
                    "template": "Student reports {item} stolen from {location}. {circumstances} {security_info}",
                    "variables": {
                        "item": [
                            "laptop", "backpack", "wallet", "phone", "bicycle",
                            "textbooks", "calculator", "headphones", "tablet", "keys"
                        ],
                        "circumstances": [
                            "Left unattended for approximately 15 minutes.",
                            "Secured in locker but lock was cut.",
                            "Taken from desk while briefly away.",
                            "Stolen from car in parking lot.",
                            "Disappeared during class break."
                        ],
                        "security_info": [
                            "No witnesses observed.",
                            "Security cameras may have captured incident.",
                            "Suspicious individual seen in area earlier.",
                            "Multiple thefts reported in same location recently.",
                            "Door was found unlocked."
                        ]
                    }
                }
            ],
            
            IncidentType.FIRE: [
                {
                    "template": "{fire_type} detected in {location}. {alarm_status} {evacuation_info} {cause_info}",
                    "variables": {
                        "fire_type": [
                            "Smoke", "Small fire", "Electrical fire", "Kitchen fire", "Trash fire"
                        ],
                        "alarm_status": [
                            "Fire alarm activated.",
                            "Smoke detectors triggered.",
                            "Manual alarm pulled.",
                            "Sprinkler system activated.",
                            "No alarm yet - investigating."
                        ],
                        "evacuation_info": [
                            "Students evacuating building.",
                            "Floor being cleared as precaution.",
                            "Building evacuation in progress.",
                            "Area cordoned off.",
                            "Fire department en route."
                        ],
                        "cause_info": [
                            "Cause unknown at this time.",
                            "Appears to be electrical malfunction.",
                            "Possible cooking accident.",
                            "May have been intentionally set.",
                            "Equipment overheating suspected."
                        ]
                    }
                }
            ],
            
            IncidentType.SECURITY: [
                {
                    "template": "{security_concern} observed {location_detail}. {behavior_description} {action_needed}",
                    "variables": {
                        "security_concern": [
                            "Suspicious individual",
                            "Unauthorized person",
                            "Unknown person",
                            "Individual acting strangely",
                            "Person taking photos"
                        ],
                        "location_detail": [
                            "near building entrances after hours",
                            "in restricted area",
                            "following students",
                            "attempting to enter locked building",
                            "loitering in parking area"
                        ],
                        "behavior_description": [
                            "Taking photos of security systems.",
                            "Trying multiple door handles.",
                            "Following female students at distance.",
                            "Asking students about building access.",
                            "Hiding when approached by others."
                        ],
                        "action_needed": [
                            "Security response requested.",
                            "Individual should be approached.",
                            "Police may need to be contacted.",
                            "Increased patrols recommended.",
                            "Students advised to be cautious."
                        ]
                    }
                }
            ],
            
            IncidentType.MAINTENANCE: [
                {
                    "template": "{maintenance_issue} in {location}. {impact_description} {urgency_level}",
                    "variables": {
                        "maintenance_issue": [
                            "Water leak", "Power outage", "Heating system failure",
                            "Broken window", "Plumbing backup", "Elevator malfunction",
                            "Air conditioning failure", "Roof leak", "Electrical problem"
                        ],
                        "impact_description": [
                            "Causing flooding in basement area.",
                            "Affecting multiple classrooms.",
                            "Creating safety hazard for students.",
                            "Disrupting normal operations.",
                            "Damaging equipment and materials."
                        ],
                        "urgency_level": [
                            "Immediate attention required.",
                            "Should be addressed today.",
                            "Needs repair within 24 hours.",
                            "Emergency maintenance needed.",
                            "Can wait until next business day."
                        ]
                    }
                }
            ],
            
            IncidentType.HARASSMENT: [
                {
                    "template": "Student reports {harassment_type} by {perpetrator_description}. {incident_details} {support_info}",
                    "variables": {
                        "harassment_type": [
                            "verbal harassment", "unwanted contact", "intimidation",
                            "cyberbullying", "discriminatory behavior", "stalking behavior"
                        ],
                        "perpetrator_description": [
                            "another student", "unknown individual", "group of students",
                            "person from off-campus", "someone in their class"
                        ],
                        "incident_details": [
                            "Occurred multiple times over past week.",
                            "Happened in public area with witnesses.",
                            "Includes threatening messages.",
                            "Making student feel unsafe on campus.",
                            "Escalating in frequency and intensity."
                        ],
                        "support_info": [
                            "Student requesting counseling support.",
                            "Formal complaint being filed.",
                            "Documentation being gathered.",
                            "Witnesses willing to provide statements.",
                            "Student needs safety planning."
                        ]
                    }
                }
            ]
        }
    
    def _load_location_details(self) -> Dict[str, Dict[str, Any]]:
        """Load detailed location information"""
        return {
            "dormitory": {
                "specific_locations": [
                    "Johnson Hall Room 204", "Smith Residence 3rd Floor", "West Dorm Lobby",
                    "East Hall Common Room", "Graduate Housing Building A"
                ],
                "risk_factors": ["late night incidents", "alcohol-related", "noise complaints"],
                "security_level": "medium"
            },
            "library": {
                "specific_locations": [
                    "Main Library 2nd Floor", "Science Library Study Room", "Library Basement",
                    "Reference Section", "Computer Lab Area"
                ],
                "risk_factors": ["theft of personal items", "noise disturbances", "medical emergencies"],
                "security_level": "high"
            },
            "dining_hall": {
                "specific_locations": [
                    "Central Dining Hall", "Student Union Food Court", "Campus Café",
                    "Faculty Dining Room", "Grab-and-Go Station"
                ],
                "risk_factors": ["food allergies", "slips and falls", "equipment malfunctions"],
                "security_level": "medium"
            },
            "gymnasium": {
                "specific_locations": [
                    "Main Gymnasium", "Fitness Center", "Swimming Pool", "Tennis Courts",
                    "Track and Field Area"
                ],
                "risk_factors": ["sports injuries", "equipment failures", "medical emergencies"],
                "security_level": "medium"
            },
            "parking_lot": {
                "specific_locations": [
                    "North Parking Lot", "Faculty Parking", "Student Lot B",
                    "Visitor Parking", "East Campus Garage"
                ],
                "risk_factors": ["vehicle break-ins", "theft", "accidents", "suspicious activity"],
                "security_level": "low"
            }
        }
    
    def _load_reporter_profiles(self) -> List[Dict[str, Any]]:
        """Load reporter profile templates"""
        return [
            {
                "type": "student",
                "names": ["Alex Johnson", "Sarah Chen", "Michael Rodriguez", "Emma Thompson", "David Kim"],
                "contact_probability": 0.8,
                "detail_level": "medium",
                "response_time": "fast"
            },
            {
                "type": "faculty",
                "names": ["Dr. Patricia Williams", "Prof. Robert Davis", "Dr. Lisa Anderson", "Prof. James Wilson"],
                "contact_probability": 0.95,
                "detail_level": "high",
                "response_time": "medium"
            },
            {
                "type": "staff",
                "names": ["Maria Garcia", "John Smith", "Jennifer Brown", "Thomas Lee"],
                "contact_probability": 0.9,
                "detail_level": "high",
                "response_time": "fast"
            },
            {
                "type": "visitor",
                "names": ["Anonymous", "Campus Visitor", "Unknown Individual"],
                "contact_probability": 0.3,
                "detail_level": "low",
                "response_time": "slow"
            }
        ]
    
    def generate_incident_report(self, 
                               incident_type: Optional[IncidentType] = None,
                               severity: Optional[SeverityLevel] = None,
                               location: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a realistic incident report
        
        Args:
            incident_type: Specific incident type (random if None)
            severity: Specific severity level (random if None)
            location: Specific location (random if None)
            
        Returns:
            Generated incident report data
        """
        
        # Select incident type
        if incident_type is None:
            incident_type = self._weighted_random_choice(self.parameters.incident_type_distribution)
        
        # Select severity
        if severity is None:
            severity = self._weighted_random_choice(self.parameters.severity_distribution)
        
        # Select location
        if location is None:
            location = self._weighted_random_choice(self.parameters.location_weights)
        
        # Get specific location details
        location_info = self.location_details.get(location, {})
        specific_location = random.choice(location_info.get("specific_locations", [location]))
        
        # Select reporter
        reporter_profile = random.choice(self.reporter_profiles)
        reporter_name = random.choice(reporter_profile["names"])
        
        # Generate incident report text
        report_text = self._generate_report_text(incident_type, specific_location, reporter_name)
        
        # Add timestamp with realistic variation
        timestamp = self._generate_realistic_timestamp()
        
        # Generate metadata
        metadata = {
            "incident_type": incident_type.value,
            "severity": severity.value,
            "location": specific_location,
            "location_category": location,
            "reporter_type": reporter_profile["type"],
            "reporter_name": reporter_name if reporter_profile["contact_probability"] > random.random() else "Anonymous",
            "timestamp": timestamp,
            "simulation_generated": True,
            "confidence_factors": {
                "detail_level": reporter_profile["detail_level"],
                "reporter_reliability": reporter_profile["contact_probability"],
                "location_security": location_info.get("security_level", "medium")
            }
        }
        
        return {
            "report": report_text,
            "metadata": metadata,
            "incident_id": f"SIM-{datetime.now().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
        }
    
    def _generate_report_text(self, incident_type: IncidentType, location: str, reporter_name: str) -> str:
        """Generate realistic incident report text"""
        
        templates = self.incident_templates.get(incident_type, [])
        if not templates:
            return f"Incident reported at {location} by {reporter_name}. Details to be determined."
        
        template_data = random.choice(templates)
        template = template_data["template"]
        variables = template_data["variables"]
        
        # Fill in template variables
        filled_template = template
        
        # Replace location
        filled_template = filled_template.replace("{location}", location)
        filled_template = filled_template.replace("{name}", reporter_name)
        
        # Replace other variables
        for var_name, options in variables.items():
            placeholder = f"{{{var_name}}}"
            if placeholder in filled_template:
                replacement = random.choice(options)
                filled_template = filled_template.replace(placeholder, replacement)
        
        return filled_template
    
    def _generate_realistic_timestamp(self) -> str:
        """Generate realistic timestamp based on campus activity patterns"""
        
        now = datetime.now()
        
        # Adjust for peak hours
        current_hour = now.hour
        if current_hour in self.parameters.peak_hours:
            # More likely to be recent during peak hours
            minutes_ago = random.randint(0, 30)
        else:
            # Could be older during off-peak hours
            minutes_ago = random.randint(0, 120)
        
        incident_time = now - timedelta(minutes=minutes_ago)
        return incident_time.isoformat()
    
    def _weighted_random_choice(self, weights: Dict) -> Any:
        """Make weighted random choice from dictionary"""
        items = list(weights.keys())
        probabilities = list(weights.values())
        return random.choices(items, weights=probabilities)[0]
    
    async def generate_continuous_stream(self, 
                                       duration_minutes: int = 60,
                                       callback=None) -> Generator[Dict[str, Any], None, None]:
        """
        Generate continuous stream of incident reports
        
        Args:
            duration_minutes: How long to generate incidents
            callback: Optional callback function for each incident
            
        Yields:
            Generated incident reports
        """
        
        self.running = True
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=duration_minutes)
        
        while self.running and datetime.now() < end_time:
            # Calculate time until next incident
            base_interval = 60 / self.parameters.incident_rate_per_hour  # minutes
            
            # Add randomness (±50%)
            actual_interval = base_interval * (0.5 + random.random())
            
            # Adjust for peak hours
            current_hour = datetime.now().hour
            if current_hour in self.parameters.peak_hours:
                actual_interval *= 0.7  # More frequent during peak hours
            
            # Wait for next incident
            await asyncio.sleep(actual_interval * 60)  # Convert to seconds
            
            if not self.running:
                break
            
            # Generate incident
            incident = self.generate_incident_report()
            
            # Call callback if provided
            if callback:
                await callback(incident)
            
            yield incident
    
    def stop_stream(self):
        """Stop the continuous incident stream"""
        self.running = False
    
    def generate_batch_incidents(self, count: int) -> List[Dict[str, Any]]:
        """
        Generate a batch of incident reports
        
        Args:
            count: Number of incidents to generate
            
        Returns:
            List of generated incident reports
        """
        
        incidents = []
        for _ in range(count):
            incident = self.generate_incident_report()
            incidents.append(incident)
        
        return incidents
    
    def generate_scenario_based_incidents(self, scenario: str, count: int = 5) -> List[Dict[str, Any]]:
        """
        Generate incidents based on specific scenarios
        
        Args:
            scenario: Scenario type (e.g., "emergency", "routine", "security_breach")
            count: Number of incidents to generate
            
        Returns:
            List of scenario-based incidents
        """
        
        scenario_configs = {
            "emergency": {
                "incident_types": [IncidentType.MEDICAL, IncidentType.FIRE, IncidentType.ASSAULT],
                "severity_bias": SeverityLevel.HIGH,
                "locations": ["gymnasium", "dormitory", "laboratory"]
            },
            "routine": {
                "incident_types": [IncidentType.MAINTENANCE, IncidentType.THEFT, IncidentType.SECURITY],
                "severity_bias": SeverityLevel.LOW,
                "locations": ["library", "dining_hall", "parking_lot"]
            },
            "security_breach": {
                "incident_types": [IncidentType.SECURITY, IncidentType.THEFT, IncidentType.VANDALISM],
                "severity_bias": SeverityLevel.MEDIUM,
                "locations": ["parking_lot", "administration", "outdoor_campus"]
            }
        }
        
        config = scenario_configs.get(scenario, scenario_configs["routine"])
        incidents = []
        
        for _ in range(count):
            incident_type = random.choice(config["incident_types"])
            location = random.choice(config["locations"])
            
            # Bias severity towards scenario preference
            if random.random() < 0.7:  # 70% chance to use biased severity
                severity = config["severity_bias"]
            else:
                severity = self._weighted_random_choice(self.parameters.severity_distribution)
            
            incident = self.generate_incident_report(
                incident_type=incident_type,
                severity=severity,
                location=location
            )
            
            # Add scenario metadata
            incident["metadata"]["scenario"] = scenario
            incident["metadata"]["scenario_generated"] = True
            
            incidents.append(incident)
        
        return incidents
    
    def get_simulation_statistics(self) -> Dict[str, Any]:
        """Get statistics about the simulation parameters"""
        
        return {
            "parameters": {
                "incident_rate_per_hour": self.parameters.incident_rate_per_hour,
                "peak_hours": self.parameters.peak_hours,
                "total_incident_types": len(self.parameters.incident_type_distribution),
                "total_locations": len(self.parameters.location_weights)
            },
            "distributions": {
                "incident_types": {k.value: v for k, v in self.parameters.incident_type_distribution.items()},
                "severity_levels": {k.value: v for k, v in self.parameters.severity_distribution.items()},
                "locations": self.parameters.location_weights
            },
            "templates": {
                "total_templates": sum(len(templates) for templates in self.incident_templates.values()),
                "templates_by_type": {k.value: len(v) for k, v in self.incident_templates.items()}
            }
        }


# Factory function
def create_data_simulator(parameters: Optional[SimulationParameters] = None) -> RealTimeDataSimulator:
    """Factory function to create data simulator"""
    return RealTimeDataSimulator(parameters)