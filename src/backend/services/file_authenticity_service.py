"""
File Authenticity Service - AI-based detection of potentially manipulated or synthetic content
"""
import os
import hashlib
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import mimetypes

# Optional imports - graceful fallback if not available
try:
    from PIL import Image, ExifTags
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️  PIL not available - using basic file analysis")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

class FileAuthenticityService:
    """Service for detecting potentially AI-generated or manipulated files"""
    
    def __init__(self):
        self.supported_image_types = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
        self.supported_video_types = {'.mp4', '.avi', '.mov', '.mkv', '.webm'}
        self.supported_document_types = {'.pdf', '.doc', '.docx', '.txt'}
        
    def analyze_file_authenticity(self, file_path: str, original_filename: str) -> Dict[str, Any]:
        """
        Analyze a file for authenticity and potential AI generation
        
        Args:
            file_path: Path to the uploaded file
            original_filename: Original filename from upload
            
        Returns:
            Dict containing authenticity analysis results
        """
        try:
            file_extension = Path(original_filename).suffix.lower()
            file_size = os.path.getsize(file_path)
            
            # Basic file analysis
            analysis = {
                "filename": original_filename,
                "file_size": file_size,
                "file_type": file_extension,
                "upload_timestamp": datetime.now().isoformat(),
                "authenticity_status": "Likely Authentic",  # Default
                "confidence_score": 85.0,  # Default confidence
                "risk_factors": [],
                "metadata_analysis": {},
                "technical_details": {},
                "requires_human_review": False
            }
            
            # Perform type-specific analysis
            if file_extension in self.supported_image_types:
                self._analyze_image_authenticity(file_path, analysis)
            elif file_extension in self.supported_video_types:
                self._analyze_video_authenticity(file_path, analysis)
            elif file_extension in self.supported_document_types:
                self._analyze_document_authenticity(file_path, analysis)
            else:
                analysis["risk_factors"].append("Unsupported file type")
                analysis["authenticity_status"] = "Unverifiable"
                analysis["confidence_score"] = 30.0
            
            # Final risk assessment
            self._assess_overall_risk(analysis)
            
            return analysis
            
        except Exception as e:
            return {
                "filename": original_filename,
                "file_size": 0,
                "file_type": "unknown",
                "upload_timestamp": datetime.now().isoformat(),
                "authenticity_status": "Unverifiable",
                "confidence_score": 0.0,
                "risk_factors": [f"Analysis failed: {str(e)}"],
                "metadata_analysis": {},
                "technical_details": {},
                "requires_human_review": True,
                "error": str(e)
            }
    
    def _analyze_image_authenticity(self, file_path: str, analysis: Dict[str, Any]) -> None:
        """Analyze image for potential AI generation or manipulation"""
        try:
            if not PIL_AVAILABLE:
                # Fallback analysis without PIL
                analysis["technical_details"].update({
                    "note": "Basic analysis - PIL not available for detailed image processing"
                })
                
                # Basic file-based checks
                file_size = analysis["file_size"]
                if file_size < 10000:  # Very small file
                    analysis["risk_factors"].append("Unusually small file size for image")
                    analysis["confidence_score"] -= 15
                elif file_size > 10 * 1024 * 1024:  # Very large file
                    analysis["risk_factors"].append("Unusually large file size")
                    analysis["confidence_score"] -= 10
                
                # Check file extension vs content type
                file_ext = Path(analysis["filename"]).suffix.lower()
                if file_ext not in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']:
                    analysis["risk_factors"].append("Unusual or suspicious file extension")
                    analysis["confidence_score"] -= 20
                
                return
            
            with Image.open(file_path) as img:
                # Basic image properties
                analysis["technical_details"].update({
                    "dimensions": f"{img.width}x{img.height}",
                    "mode": img.mode,
                    "format": img.format
                })
                
                # EXIF data analysis
                exif_data = self._extract_exif_data(img)
                analysis["metadata_analysis"]["exif"] = exif_data
                
                # Check for suspicious patterns
                self._check_image_suspicious_patterns(img, analysis, exif_data)
                
        except Exception as e:
            analysis["risk_factors"].append(f"Image analysis failed: {str(e)}")
            analysis["authenticity_status"] = "Unverifiable"
            analysis["confidence_score"] = 20.0
    
    def _extract_exif_data(self, img) -> Dict[str, Any]:
        """Extract and analyze EXIF metadata"""
        if not PIL_AVAILABLE:
            return {"error": "PIL not available for EXIF extraction"}
            
        exif_data = {}
        
        try:
            if hasattr(img, '_getexif') and img._getexif() is not None:
                exif = img._getexif()
                for tag_id, value in exif.items():
                    tag = ExifTags.TAGS.get(tag_id, tag_id)
                    exif_data[tag] = str(value)
            
            return exif_data
            
        except Exception:
            return {"error": "Could not extract EXIF data"}
    
    def _check_image_suspicious_patterns(self, img, analysis: Dict[str, Any], exif_data: Dict[str, Any]) -> None:
        """Check for patterns that might indicate AI generation or manipulation"""
        
        # Check 1: Missing or suspicious EXIF data
        if not exif_data or "error" in exif_data:
            analysis["risk_factors"].append("Missing or corrupted EXIF metadata")
            analysis["confidence_score"] -= 15
        
        # Check 2: Suspicious camera/software information
        software = exif_data.get("Software", "").lower()
        if any(ai_tool in software for ai_tool in ["midjourney", "dall-e", "stable diffusion", "ai", "generated"]):
            analysis["risk_factors"].append("AI generation software detected in metadata")
            analysis["authenticity_status"] = "Suspicious / Possibly AI-Generated"
            analysis["confidence_score"] = 25.0
            return
        
        if not PIL_AVAILABLE:
            # Basic checks without PIL
            return
        
        # Check 3: Perfect dimensions (common in AI-generated images)
        width, height = img.size
        if width == height and width in [512, 1024, 2048]:  # Common AI generation sizes
            analysis["risk_factors"].append("Suspicious dimensions typical of AI generation")
            analysis["confidence_score"] -= 20
        
        # Check 4: File size vs quality inconsistencies
        file_size = analysis["file_size"]
        pixel_count = width * height
        expected_size_range = (pixel_count * 0.1, pixel_count * 3)  # Rough estimate
        
        if file_size < expected_size_range[0]:
            analysis["risk_factors"].append("Unusually small file size for image dimensions")
            analysis["confidence_score"] -= 10
        elif file_size > expected_size_range[1] * 2:
            analysis["risk_factors"].append("Unusually large file size")
            analysis["confidence_score"] -= 5
        
        # Check 5: Analyze image histogram for unnatural patterns (if numpy available)
        if NUMPY_AVAILABLE:
            try:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img_rgb = img.convert('RGB')
                else:
                    img_rgb = img
                
                # Simple histogram analysis
                import numpy as np
                img_array = np.array(img_rgb)
                
                # Check for unusual color distribution patterns
                for channel in range(3):  # RGB channels
                    channel_data = img_array[:, :, channel].flatten()
                    hist, _ = np.histogram(channel_data, bins=256, range=(0, 256))
                    
                    # Check for suspicious patterns
                    if np.std(hist) < 10:  # Very uniform distribution
                        analysis["risk_factors"].append("Unusual color distribution pattern detected")
                        analysis["confidence_score"] -= 10
                        break
                        
            except Exception as e:
                analysis["risk_factors"].append(f"Histogram analysis failed: {str(e)}")
        
        # Check 6: Missing creation date
        if "DateTime" not in exif_data and "DateTimeOriginal" not in exif_data:
            analysis["risk_factors"].append("Missing creation timestamp")
            analysis["confidence_score"] -= 10
    
    def _analyze_video_authenticity(self, file_path: str, analysis: Dict[str, Any]) -> None:
        """Analyze video for potential deepfake or manipulation"""
        # Basic video analysis (would need video processing libraries for full implementation)
        analysis["technical_details"]["note"] = "Video analysis requires additional processing"
        
        # For now, mark videos as requiring human review due to complexity
        analysis["risk_factors"].append("Video content requires manual verification")
        analysis["authenticity_status"] = "Unverifiable"
        analysis["confidence_score"] = 50.0
    
    def _analyze_document_authenticity(self, file_path: str, analysis: Dict[str, Any]) -> None:
        """Analyze document for potential manipulation"""
        # Basic document analysis
        analysis["technical_details"]["note"] = "Document analysis performed"
        
        # Check file creation patterns
        stat = os.stat(file_path)
        creation_time = datetime.fromtimestamp(stat.st_ctime)
        modification_time = datetime.fromtimestamp(stat.st_mtime)
        
        # If file was modified very recently after creation, might be suspicious
        time_diff = (modification_time - creation_time).total_seconds()
        if time_diff < 5:  # Modified within 5 seconds of creation
            analysis["risk_factors"].append("File modified immediately after creation")
            analysis["confidence_score"] -= 15
    
    def _assess_overall_risk(self, analysis: Dict[str, Any]) -> None:
        """Assess overall risk and determine if human review is required"""
        
        confidence = analysis["confidence_score"]
        risk_factors = analysis["risk_factors"]
        
        # Determine authenticity status based on confidence and risk factors
        if confidence < 40 or len(risk_factors) >= 3:
            analysis["authenticity_status"] = "Suspicious / Possibly AI-Generated"
            analysis["requires_human_review"] = True
        elif confidence < 60 or len(risk_factors) >= 2:
            analysis["authenticity_status"] = "Unverifiable"
            analysis["requires_human_review"] = True
        elif confidence >= 80 and len(risk_factors) == 0:
            analysis["authenticity_status"] = "Likely Authentic"
            analysis["requires_human_review"] = False
        else:
            # Middle ground - likely authentic but with some concerns
            analysis["authenticity_status"] = "Likely Authentic"
            analysis["requires_human_review"] = len(risk_factors) > 0
        
        # Add summary
        analysis["summary"] = self._generate_summary(analysis)
    
    def _generate_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate human-readable summary of the analysis"""
        status = analysis["authenticity_status"]
        confidence = analysis["confidence_score"]
        risk_count = len(analysis["risk_factors"])
        
        if status == "Likely Authentic":
            if risk_count == 0:
                return f"File appears authentic with high confidence ({confidence:.0f}%)"
            else:
                return f"File appears authentic but has {risk_count} minor concern(s) ({confidence:.0f}% confidence)"
        elif status == "Unverifiable":
            return f"File authenticity cannot be verified due to {risk_count} issue(s) ({confidence:.0f}% confidence)"
        else:  # Suspicious
            return f"File shows {risk_count} suspicious pattern(s) that may indicate AI generation or manipulation ({confidence:.0f}% confidence)"

# Global service instance
file_authenticity_service = FileAuthenticityService()