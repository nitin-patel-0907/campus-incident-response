import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { cn } from "@/lib/utils";
import { format } from "date-fns";
import {
  CalendarIcon,
  Upload,
  Send,
  CheckCircle,
  RotateCcw,
  MapPin,
  X,
  Shield,
  User,
  FileText,
  Clock,
  AlertCircle,
} from "lucide-react";
import { apiClient, WorkflowResult } from "@/lib/api";
import { AnalysisResultsModal } from "./AnalysisResultsModal";
import { useToast } from "@/hooks/use-toast";

interface IncidentFormProps {
  onSubmit: () => void;
  isSubmitted: boolean;
  onReset: () => void;
}

interface FormData {
  name: string;
  universityId: string;
  role: string;
  incidentType: string;
  severity: string;
  location: string;
  description: string;
  isAnonymous: boolean;
  consentFollowUp: boolean;
}

interface UploadedImage {
  file: File;
  preview: string;
  analysis?: any;
  authenticity_analysis?: any;
  uploading?: boolean;
  requires_human_review?: boolean;
}

export function IncidentForm({ onSubmit, isSubmitted, onReset }: IncidentFormProps) {
  const [date, setDate] = useState<Date>();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showAnalysisModal, setShowAnalysisModal] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<WorkflowResult | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [showLoadingAnimation, setShowLoadingAnimation] = useState(false);
  const [uploadedImages, setUploadedImages] = useState<UploadedImage[]>([]);
  const [formData, setFormData] = useState<FormData>({
    name: "",
    universityId: "",
    role: "",
    incidentType: "",
    severity: "",
    location: "",
    description: "",
    isAnonymous: false,
    consentFollowUp: false,
  });
  const { toast } = useToast();

  const handleInputChange = (field: keyof FormData, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleImageUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files) return;

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      
      // Validate file type
      if (!file.type.startsWith('image/')) {
        toast({
          title: "Invalid File Type",
          description: "Please upload only image files.",
          variant: "destructive",
        });
        continue;
      }

      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        toast({
          title: "File Too Large",
          description: "Please upload images smaller than 10MB.",
          variant: "destructive",
        });
        continue;
      }

      // Create preview
      const preview = URL.createObjectURL(file);
      const newImage: UploadedImage = {
        file,
        preview,
        uploading: true,
      };

      setUploadedImages(prev => [...prev, newImage]);

      try {
        // Upload and analyze image
        const result = await apiClient.uploadIncidentImage(file, `Incident scene image - ${file.name}`);
        
        // Update image with analysis and authenticity check
        setUploadedImages(prev => 
          prev.map(img => 
            img.file === file 
              ? { 
                  ...img, 
                  analysis: result.ai_analysis, 
                  authenticity_analysis: result.authenticity_analysis,
                  requires_human_review: result.requires_human_review,
                  uploading: false 
                }
              : img
          )
        );

        // Show appropriate toast based on authenticity
        if (result.requires_human_review) {
          toast({
            title: "File Uploaded - Review Required",
            description: `Image uploaded but requires human verification due to authenticity concerns.`,
            variant: "destructive",
          });
        } else {
          toast({
            title: "Image Analyzed",
            description: "Image uploaded and analyzed successfully.",
          });
        }

      } catch (error) {
        console.error("Error uploading image:", error);
        
        // Remove failed upload
        setUploadedImages(prev => prev.filter(img => img.file !== file));
        
        toast({
          title: "Upload Failed",
          description: error instanceof Error ? error.message : "Failed to upload image.",
          variant: "destructive",
        });
      }
    }
  };

  const removeImage = (index: number) => {
    setUploadedImages(prev => {
      const newImages = [...prev];
      URL.revokeObjectURL(newImages[index].preview);
      newImages.splice(index, 1);
      return newImages;
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      // Capture submission timestamp automatically
      const submissionTimestamp = new Date().toISOString();
      
      // Prepare the incident report for the LangGraph API
      const incidentReport = {
        report: `Incident Report:
        
${formData.isAnonymous ? 'Reporter: Anonymous (Pseudonymous ID will be generated)' : `Reporter: ${formData.name} (${formData.universityId})`}
Role: ${formData.role}
Incident Type: ${formData.incidentType}
Severity: ${formData.severity}
Location: ${formData.location}
Incident Date/Time: ${date ? format(date, "PPP") : "Not specified"}
Report Submitted: ${new Date(submissionTimestamp).toLocaleString()}

Description:
${formData.description}

${uploadedImages.length > 0 ? `

Image Analysis:
${uploadedImages.map((img, index) => {
  if (img.analysis) {
    return `Image ${index + 1} (${img.file.name}):
- Scene Description: ${img.analysis.scene_description}
- Suggested Incident Type: ${img.analysis.suggested_incident_type}
- Severity Assessment: ${img.analysis.severity_assessment}
- Safety Concerns: ${img.analysis.safety_concerns?.join(', ') || 'None identified'}
- Recommended Actions: ${img.analysis.recommended_actions?.join(', ') || 'Standard response'}`;
  }
  return `Image ${index + 1} (${img.file.name}): Analysis pending...`;
}).join('\n\n')}` : ''}`,
        execution_mode: "simulate" as const,
        reporter_info: formData.isAnonymous ? {
          anonymous: true,
          role: formData.role,
        } : {
          name: formData.name,
          university_id: formData.universityId,
          role: formData.role,
          anonymous: false,
        },
        metadata: {
          incident_type: formData.incidentType,
          severity: formData.severity,
          location: formData.location,
          incident_date_time: date ? date.toISOString() : "", // When incident occurred
          submission_timestamp: submissionTimestamp, // When report was submitted
          form_submission: true,
          has_images: uploadedImages.length > 0,
          image_analysis: uploadedImages.map(img => img.analysis).filter(Boolean),
          file_analyses: uploadedImages.map(img => img.authenticity_analysis).filter(Boolean),
          anonymous_report: formData.isAnonymous,
        },
      };

      // Show loading animation first
      setShowLoadingAnimation(true);
      setIsAnalyzing(true);
      
      // Wait a bit to show the loading animation
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Submit to LangGraph API
      const result = await apiClient.processIncident(incidentReport);
      
      // Hide loading animation
      setShowLoadingAnimation(false);
      setIsAnalyzing(false);
      
      // Check if this is a spam detection response
      if (result.status === "spam_detected" || result.error_type === "spam_detected") {
        // Show spam detection popup instead of analysis modal
        const spamDetails = result.spam_detection || result.details || {};
        
        toast({
          title: "Report Rejected",
          description: result.user_message || `Your report has been flagged as ${spamDetails.category || 'inappropriate'} content and cannot be processed.`,
          variant: "destructive",
          duration: 8000, // Show longer for spam notifications
        });
        
        // Show detailed spam popup
        const spamMessage = `
Report Status: Rejected
Category: ${spamDetails.category || 'Inappropriate Content'}
Reason: ${spamDetails.reason || 'Content flagged by automated detection'}
Confidence: ${spamDetails.confidence || 'High'}

Your report has been automatically flagged and will not be processed. If you believe this is an error, please contact support directly.
        `.trim();
        
        // Use browser alert for immediate visibility
        alert(`❌ Report Rejected\n\n${spamMessage}`);
        
        // Reset form without setting analysisResult or showing modal
        // DO NOT set analysisResult for spam - this prevents the destructuring error
        setAnalysisResult(null);
        setShowAnalysisModal(false);
        handleReset();
        return;
      }
      
      // Only show analysis modal for successful legitimate reports
      if (result.success && result.result) {
        // Only set analysisResult for legitimate reports with proper result structure
        setAnalysisResult(result);
        setShowAnalysisModal(true);
        
        // Show success toast
        toast({
          title: "Report Processed",
          description: "Your incident has been processed by our response system.",
        });
        
        onSubmit();
      } else {
        // Handle other error cases without setting analysisResult
        setAnalysisResult(null);
        setShowAnalysisModal(false);
        throw new Error(result.message || "Failed to process incident");
      }
      
    } catch (error) {
      console.error("Error submitting incident:", error);
      setIsAnalyzing(false);
      setShowAnalysisModal(false);
      setShowLoadingAnimation(false);
      
      // Check if this is a spam detection error
      if (error instanceof Error && error.message.includes('spam')) {
        toast({
          title: "Report Rejected",
          description: "Your report has been flagged as inappropriate content and cannot be processed.",
          variant: "destructive",
          duration: 8000,
        });
        
        // Show spam popup
        alert("❌ Report Rejected\n\nYour report has been flagged as inappropriate content and cannot be processed. If you believe this is an error, please contact support directly.");
        
        // Reset form
        handleReset();
        return;
      }
      
      toast({
        title: "Submission Error",
        description: error instanceof Error ? error.message : "Failed to process incident. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReset = () => {
    setFormData({
      name: "",
      universityId: "",
      role: "",
      incidentType: "",
      severity: "",
      location: "",
      description: "",
      isAnonymous: false,
      consentFollowUp: false,
    });
    setDate(undefined);
    setAnalysisResult(null);
    setShowAnalysisModal(false);
    setShowLoadingAnimation(false);
    setIsAnalyzing(false);
    
    // Clean up image previews
    uploadedImages.forEach(img => URL.revokeObjectURL(img.preview));
    setUploadedImages([]);
    
    onReset();
  };

  if (showLoadingAnimation) {
    return (
      <div className="card-professional">
        <div className="card-content-professional">
          <div className="loading-professional">
            <div className="loading-spinner-professional"></div>
            
            <h3 className="heading-4-professional mb-2">Processing Your Report</h3>
            <p className="body-small-professional mb-8 max-w-md">
              Your report is being processed through our secure system. This may take a few moments.
            </p>
            
            {/* Professional Processing Steps */}
            <div className="w-full max-w-md space-y-3">
              <div className="flex items-center gap-3 p-3 rounded-md bg-muted/30 border border-border">
                <div className="status-dot status-dot-success animate-pulse-subtle" />
                <span className="text-sm font-medium">Validating details</span>
              </div>
              <div className="flex items-center gap-3 p-3 rounded-md bg-muted/30 border border-border">
                <div className="status-dot status-dot-info animate-pulse-subtle" />
                <span className="text-sm font-medium">Processing report</span>
              </div>
              <div className="flex items-center gap-3 p-3 rounded-md bg-muted/30 border border-border">
                <div className="status-dot status-dot-warning animate-pulse-subtle" />
                <span className="text-sm font-medium">Reviewing information</span>
              </div>
              <div className="flex items-center gap-3 p-3 rounded-md bg-muted/30 border border-border">
                <div className="status-dot status-dot-neutral animate-pulse-subtle" />
                <span className="text-sm font-medium">Finalizing submission</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (isSubmitted) {
    return (
      <>
        <div className="card-professional">
          <div className="card-content-professional">
            <div className="loading-professional">
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-success/20 mb-4">
                <CheckCircle className="h-6 w-6 text-success" />
              </div>
              <h3 className="heading-4-professional mb-2">Report Submitted</h3>
              <p className="body-small-professional mb-6 max-w-md">
                Your incident report has been received and is being processed by our response team.
                {analysisResult && " You can view the processing details below."}
              </p>
              <div className="flex gap-3">
                {analysisResult && (
                  <Button 
                    onClick={() => setShowAnalysisModal(true)} 
                    className="btn-primary-professional"
                  >
                    <FileText className="h-4 w-4" />
                    View Details
                  </Button>
                )}
                <Button onClick={handleReset} variant="outline">
                  <RotateCcw className="h-4 w-4" />
                  Submit Another Report
                </Button>
              </div>
            </div>
          </div>
        </div>

        <AnalysisResultsModal
          isOpen={showAnalysisModal}
          onClose={() => setShowAnalysisModal(false)}
          result={analysisResult}
          isLoading={isAnalyzing}
        />
      </>
    );
  }

  return (
    <>
      <div className="card-professional">
        <div className="card-header-professional">
          <h2 className="card-title-professional">Report an Incident</h2>
          <p className="card-subtitle-professional">
            Provide details about the incident to help our response team take appropriate action
          </p>
        </div>
        <div className="card-content-professional">
          <form onSubmit={handleSubmit} className="form-professional">
            {/* Anonymous Reporting Toggle */}
            <div className="flex items-center justify-between p-4 bg-muted/30 rounded-lg border border-border">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-accent/10">
                  {formData.isAnonymous ? (
                    <Shield className="h-5 w-5 text-accent" />
                  ) : (
                    <User className="h-5 w-5 text-muted-foreground" />
                  )}
                </div>
                <div>
                  <Label htmlFor="anonymous-toggle" className="form-label-professional text-base font-medium cursor-pointer">
                    Report this incident anonymously
                  </Label>
                  <p className="form-help-professional">
                    {formData.isAnonymous 
                      ? "Your identity will be protected. A secure identifier will be assigned to your report." 
                      : "Your contact information will be included with this report for follow-up purposes."}
                  </p>
                </div>
              </div>
              <Switch
                id="anonymous-toggle"
                checked={formData.isAnonymous}
                onCheckedChange={(checked) => handleInputChange("isAnonymous", checked)}
              />
            </div>

            {/* Personal Information - Hidden when anonymous */}
            {!formData.isAnonymous && (
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="form-group-professional">
                  <Label htmlFor="name" className="form-label-professional form-label-required">
                    Full Name
                  </Label>
                  <Input
                    id="name"
                    placeholder="Enter your full name"
                    required
                    className="form-input-professional"
                    value={formData.name}
                    onChange={(e) => handleInputChange("name", e.target.value)}
                  />
                </div>
                <div className="form-group-professional">
                  <Label htmlFor="universityId" className="form-label-professional form-label-required">
                    University ID
                  </Label>
                  <Input
                    id="universityId"
                    placeholder="e.g., STU-2024-1234"
                    required
                    className="form-input-professional"
                    value={formData.universityId}
                    onChange={(e) => handleInputChange("universityId", e.target.value)}
                  />
                  <p className="form-help-professional">
                    Your ID is used for verification and will be kept confidential
                  </p>
                </div>
              </div>
            )}

            {/* Role and Incident Type */}
            <div className="grid gap-4 sm:grid-cols-2">
              <div className="form-group-professional">
                <Label className="form-label-professional form-label-required">Role</Label>
                <Select required value={formData.role} onValueChange={(value) => handleInputChange("role", value)}>
                  <SelectTrigger className="form-select-professional">
                    <SelectValue placeholder="Select your role" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="student">Student</SelectItem>
                    <SelectItem value="faculty">Faculty</SelectItem>
                    <SelectItem value="staff">Staff</SelectItem>
                    <SelectItem value="visitor">Visitor</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="form-group-professional">
                <Label className="form-label-professional form-label-required">Incident Type</Label>
                <Select required value={formData.incidentType} onValueChange={(value) => handleInputChange("incidentType", value)}>
                  <SelectTrigger className="form-select-professional">
                    <SelectValue placeholder="Select incident type" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="medical">Medical Emergency</SelectItem>
                    <SelectItem value="theft">Theft</SelectItem>
                    <SelectItem value="harassment">Harassment</SelectItem>
                    <SelectItem value="assault">Violence/Assault</SelectItem>
                    <SelectItem value="fire">Fire/Emergency</SelectItem>
                    <SelectItem value="security">Security/Suspicious Activity</SelectItem>
                    <SelectItem value="vandalism">Vandalism</SelectItem>
                    <SelectItem value="substance">Substance Related</SelectItem>
                    <SelectItem value="maintenance">Maintenance Issue</SelectItem>
                    <SelectItem value="academic">Academic Misconduct</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>

            {/* Severity */}
            <div className="form-group-professional">
              <Label className="form-label-professional form-label-required">Severity Level</Label>
              <p className="form-help-professional">
                Select the urgency level that best describes this incident
              </p>
              <Select required value={formData.severity} onValueChange={(value) => handleInputChange("severity", value)}>
                <SelectTrigger className="form-select-professional">
                  <SelectValue placeholder="Select severity level" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">
                    <div className="flex items-center gap-3">
                      <div className="status-dot status-dot-success" />
                      <div>
                        <div className="font-medium">Low Priority</div>
                        <div className="text-xs text-muted-foreground">Non-urgent situation</div>
                      </div>
                    </div>
                  </SelectItem>
                  <SelectItem value="medium">
                    <div className="flex items-center gap-3">
                      <div className="status-dot status-dot-warning" />
                      <div>
                        <div className="font-medium">Medium Priority</div>
                        <div className="text-xs text-muted-foreground">Needs attention</div>
                      </div>
                    </div>
                  </SelectItem>
                  <SelectItem value="high">
                    <div className="flex items-center gap-3">
                      <div className="status-dot status-dot-error" />
                      <div>
                        <div className="font-medium">High Priority</div>
                        <div className="text-xs text-muted-foreground">Urgent response required</div>
                      </div>
                    </div>
                  </SelectItem>
                  <SelectItem value="critical">
                    <div className="flex items-center gap-3">
                      <div className="status-dot bg-red-600" />
                      <div>
                        <div className="font-medium">Critical Priority</div>
                        <div className="text-xs text-muted-foreground">Emergency response needed</div>
                      </div>
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Location */}
            <div className="form-group-professional">
              <Label htmlFor="location" className="form-label-professional form-label-required">Location</Label>
              <p className="form-help-professional">
                Provide the specific location where the incident occurred
              </p>
              <div className="relative">
                <Input
                  id="location"
                  placeholder="e.g., Science Building, Room 204"
                  required
                  className="form-input-professional pr-10"
                  value={formData.location}
                  onChange={(e) => handleInputChange("location", e.target.value)}
                />
                <MapPin className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              </div>
            </div>

            {/* Date & Time */}
            <div className="form-group-professional">
              <Label className="form-label-professional">Date & Time of Incident</Label>
              <p className="form-help-professional">
                When did this incident occur? If not specified, the submission time will be used.
              </p>
              <Popover>
                <PopoverTrigger asChild>
                  <Button
                    variant="outline"
                    className={cn(
                      "w-full justify-start text-left font-normal form-input-professional h-auto py-3",
                      !date && "text-muted-foreground"
                    )}
                  >
                    <CalendarIcon className="mr-2 h-4 w-4" />
                    {date ? format(date, "PPP") : "Select date and time (optional)"}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-0" align="start">
                  <Calendar
                    mode="single"
                    selected={date}
                    onSelect={setDate}
                    initialFocus
                    className="pointer-events-auto"
                  />
                </PopoverContent>
              </Popover>
              <div className="flex items-center gap-2 mt-2 p-2 bg-muted/30 rounded-md border border-border">
                <Clock className="h-4 w-4 text-muted-foreground" />
                <span className="text-xs text-muted-foreground">
                  Report submission time: {new Date().toLocaleString()}
                </span>
              </div>
            </div>

            {/* Description */}
            <div className="form-group-professional">
              <Label htmlFor="description" className="form-label-professional form-label-required">Detailed Description</Label>
              <p className="form-help-professional">
                Provide a clear, detailed account of what happened. Include relevant information such as people involved, sequence of events, and any other important details.
              </p>
              <Textarea
                id="description"
                placeholder="Please describe the incident in detail..."
                rows={5}
                required
                className="form-textarea-professional"
                value={formData.description}
                onChange={(e) => handleInputChange("description", e.target.value)}
              />
              <div className="flex justify-between items-center mt-1">
                <span className="form-help-professional">
                  Be as specific as possible to help our response team
                </span>
                <span className="text-xs text-muted-foreground">
                  {formData.description.length}/1000
                </span>
              </div>
            </div>

            {/* File Upload */}
            <div className="form-group-professional">
              <Label className="form-label-professional">Supporting Documentation</Label>
              <p className="form-help-professional">
                Upload images or documents that provide additional context about the incident (optional)
              </p>
              <div className="file-upload-professional">
                <label
                  htmlFor="dropzone-file"
                  className="flex flex-col items-center justify-center w-full h-32 cursor-pointer"
                >
                  <div className="flex flex-col items-center justify-center pt-5 pb-6">
                    <Upload className="h-8 w-8 text-muted-foreground mb-2" />
                    <p className="mb-1 text-sm text-muted-foreground">
                      <span className="font-medium text-foreground">Click to upload</span> or drag and drop
                    </p>
                    <p className="text-xs text-muted-foreground">
                      Images (MAX. 10MB) - Files will be analyzed for authenticity
                    </p>
                  </div>
                  <input 
                    id="dropzone-file" 
                    type="file" 
                    className="hidden" 
                    accept="image/*"
                    multiple
                    onChange={handleImageUpload}
                  />
                </label>
              </div>
              {/* Uploaded Images */}
              {uploadedImages.length > 0 && (
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 mt-4">
                  {uploadedImages.map((image, index) => (
                    <div key={index} className="relative group">
                      <div className="aspect-video rounded-lg overflow-hidden bg-muted border border-border">
                        <img
                          src={image.preview}
                          alt={`Upload ${index + 1}`}
                          className="w-full h-full object-cover"
                        />
                        {image.uploading && (
                          <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                            <div className="flex items-center gap-2 text-white text-sm">
                              <div className="loading-spinner-professional w-4 h-4 border-white/30 border-t-white" />
                              Processing...
                            </div>
                          </div>
                        )}
                      </div>
                      
                      {/* Remove button */}
                      <Button
                        type="button"
                        variant="destructive"
                        size="sm"
                        className="absolute top-2 right-2 h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                        onClick={() => removeImage(index)}
                      >
                        <X className="h-3 w-3" />
                      </Button>
                      
                      {/* Analysis results */}
                      {image.analysis && (
                        <div className="mt-2 p-3 bg-muted/50 rounded-lg text-xs border border-border">
                          <div className="font-medium mb-1 text-foreground">Analysis Complete:</div>
                          <div className="text-muted-foreground space-y-1">
                            <div>Type: {image.analysis.content_type || 'Unknown'}</div>
                            <div>Real-world Score: {image.analysis.real_world_score || 0}%</div>
                            <div className="mt-1">{image.analysis.scene_description?.substring(0, 100)}...</div>
                          </div>
                        </div>
                      )}
                      
                      {/* File Status */}
                      {image.authenticity_analysis && (
                        <div className={`mt-2 p-3 rounded-lg text-xs border ${
                          image.requires_human_review 
                            ? 'bg-red-50 border-red-200 text-red-700 dark:bg-red-950/20 dark:border-red-800 dark:text-red-300' 
                            : 'bg-green-50 border-green-200 text-green-700 dark:bg-green-950/20 dark:border-green-800 dark:text-green-300'
                        }`}>
                          <div className="font-medium mb-1 flex items-center gap-1">
                            {image.requires_human_review ? (
                              <AlertCircle className="h-3 w-3" />
                            ) : (
                              <CheckCircle className="h-3 w-3" />
                            )} 
                            File Status: {image.requires_human_review ? 'Review Required' : 'Verified'}
                          </div>
                          <div className="text-xs opacity-75">
                            {image.authenticity_analysis.real_world_assessment ? (
                              <>
                                {image.authenticity_analysis.real_world_assessment.is_real_world 
                                  ? 'Real-world content detected' 
                                  : 'Non-real-world content detected'}
                                <br />
                                Score: {image.authenticity_analysis.real_world_assessment.score}%
                              </>
                            ) : (
                              `Authenticity: ${image.authenticity_analysis.authenticity_score}%`
                            )}
                          </div>
                          {image.authenticity_analysis.real_world_assessment && 
                           !image.authenticity_analysis.real_world_assessment.is_real_world && (
                            <div className="text-xs mt-1 font-medium">
                              ⚠️ This may affect incident resolution
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Submit Button */}
            <div className="flex gap-3 pt-4">
              <Button 
                type="submit" 
                disabled={isSubmitting}
                className="btn-primary-professional flex-1"
              >
                {isSubmitting ? (
                  <>
                    <div className="loading-spinner-professional w-4 h-4 border-white/30 border-t-white mr-2" />
                    Processing...
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4" />
                    Submit Report
                  </>
                )}
              </Button>
              <Button 
                type="button" 
                variant="outline" 
                onClick={handleReset}
                disabled={isSubmitting}
              >
                <RotateCcw className="h-4 w-4" />
                Reset
              </Button>
            </div>
          </form>
        </div>
      </div>

      <AnalysisResultsModal
        isOpen={showAnalysisModal}
        onClose={() => setShowAnalysisModal(false)}
        result={analysisResult}
        isLoading={isAnalyzing}
      />
    </>
  );
}