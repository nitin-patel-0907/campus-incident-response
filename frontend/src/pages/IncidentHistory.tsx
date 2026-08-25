import { useState, useEffect } from "react";
import { MainLayout } from "@/components/layout/MainLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Search, Filter, Eye, MapPin, Clock, User, FileText, RefreshCw, AlertCircle, CheckCircle2, XCircle, MessageSquare, Shield, AlertTriangle } from "lucide-react";
import { apiClient } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

export default function IncidentHistory() {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedIncident, setSelectedIncident] = useState<any | null>(null);
  const [statusFilter, setStatusFilter] = useState("all");
  const [severityFilter, setSeverityFilter] = useState("all");
  const [incidents, setIncidents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [totalCount, setTotalCount] = useState(0);
  const [showResolutionDialog, setShowResolutionDialog] = useState(false);
  const [resolutionFeedback, setResolutionFeedback] = useState("");
  const [resolvingIncident, setResolvingIncident] = useState<any | null>(null);
  const { toast } = useToast();

  // Load incident history
  const loadIncidents = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getIncidentHistory(
        50, // limit
        0,  // offset
        statusFilter === "all" ? undefined : statusFilter,
        severityFilter === "all" ? undefined : severityFilter
      );
      
      if (response.success) {
        setIncidents(response.incidents);
        setTotalCount(response.total_count);
      } else {
        throw new Error("Failed to load incident history");
      }
    } catch (error) {
      console.error("Error loading incidents:", error);
      toast({
        title: "Error Loading History",
        description: error instanceof Error ? error.message : "Failed to load incident history",
        variant: "destructive",
      });
      // Keep empty array if error
      setIncidents([]);
      setTotalCount(0);
    } finally {
      setLoading(false);
    }
  };

  // Load incidents on component mount and when filters change
  useEffect(() => {
    loadIncidents();
  }, [statusFilter, severityFilter]);

  // Handle incident resolution
  const handleResolveIncident = async () => {
    if (!resolvingIncident || !resolutionFeedback.trim()) {
      toast({
        title: "Resolution Failed",
        description: "Please provide feedback for the resolution",
        variant: "destructive",
      });
      return;
    }

    try {
      // Call the API to resolve the incident
      await apiClient.resolveIncident(
        resolvingIncident.id,
        resolutionFeedback,
        "Admin" // In a real app, this would be the current user
      );
      
      // Close the dialog first
      setShowResolutionDialog(false);
      setResolutionFeedback("");
      setResolvingIncident(null);
      
      // Show success message
      toast({
        title: "Incident Resolved",
        description: `Incident ${resolvingIncident.id} has been marked as resolved`,
      });
      
      // Reload the incident list to reflect the changes
      await loadIncidents();
      
    } catch (error) {
      console.error("Resolution error:", error);
      toast({
        title: "Resolution Failed",
        description: error instanceof Error ? error.message : "Failed to resolve the incident. Please try again.",
        variant: "destructive",
      });
    }
  };

  // Handle spam marking
  const markAsSpam = async (incident: any, isGibberish: boolean = false) => {
    try {
      const response = await fetch(`/api/v1/incidents/${incident.id}/mark-spam`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          report_text: incident.description,
          reason: isGibberish ? "Gibberish/nonsensical text" : "Manual admin review",
          is_gibberish: isGibberish,
          human_assessment: isGibberish ? "Human confirmed gibberish text" : "Human marked as spam"
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        const spamType = isGibberish ? "gibberish" : "spam";
        toast({
          title: `Marked as ${spamType.charAt(0).toUpperCase() + spamType.slice(1)}`,
          description: `Incident ${incident.id} has been marked as ${spamType} and will be used for future detection`,
        });
        
        // Remove from current list
        const updatedIncidents = incidents.filter(i => i.id !== incident.id);
        setIncidents(updatedIncidents);
      } else {
        throw new Error(data.error || `Failed to mark as ${isGibberish ? 'gibberish' : 'spam'}`);
      }
    } catch (error) {
      console.error("Error marking spam:", error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : `Failed to mark incident as ${isGibberish ? 'gibberish' : 'spam'}`,
        variant: "destructive",
      });
    }
  };

  // Handle gibberish assessment
  const assessGibberish = async (incident: any, isGibberish: boolean, notes: string = "") => {
    try {
      const response = await fetch(`/api/v1/incidents/${incident.id}/assess-gibberish`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          report_text: incident.description,
          is_gibberish: isGibberish,
          notes: notes,
          reviewer_id: "admin"
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        toast({
          title: isGibberish ? "Confirmed as Gibberish" : "Confirmed as Legitimate",
          description: data.message,
        });
        
        // Remove from current list if confirmed as gibberish
        if (isGibberish) {
          const updatedIncidents = incidents.filter(i => i.id !== incident.id);
          setIncidents(updatedIncidents);
        }
      } else {
        throw new Error(data.error || "Failed to assess gibberish");
      }
    } catch (error) {
      console.error("Error assessing gibberish:", error);
      toast({
        title: "Assessment Error",
        description: error instanceof Error ? error.message : "Failed to assess gibberish",
        variant: "destructive",
      });
    }
  };

  const openResolutionDialog = (incident: any) => {
    setResolvingIncident(incident);
    setShowResolutionDialog(true);
  };

  const filteredIncidents = incidents.filter((incident) => {
    const matchesSearch =
      incident.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
      incident.type.toLowerCase().includes(searchQuery.toLowerCase()) ||
      incident.location.toLowerCase().includes(searchQuery.toLowerCase());

    return matchesSearch;
  });

  // Helper function to get incident status from evaluation report
  const getIncidentStatus = (incident: any) => {
    // Check if evaluation report has resolution status
    if (incident.complete_analysis?.evaluation_report?.resolution_status) {
      return incident.complete_analysis.evaluation_report.resolution_status;
    }
    
    // Fallback to existing status logic
    if (incident.status) {
      return incident.status;
    }
    
    // Default based on processing stages
    const stages = incident.complete_analysis?.processing_stages;
    if (stages && Object.values(stages).every(stage => stage === 'completed')) {
      return 'resolved';
    }
    
    return 'unresolved';
  };

  // Helper function to get resolution reason
  const getResolutionReason = (incident: any) => {
    return incident.complete_analysis?.evaluation_report?.resolution_reason || 'Processing completed';
  };

  // Helper function to check if human intervention is required
  const requiresHumanIntervention = (incident: any) => {
    return incident.complete_analysis?.evaluation_report?.human_intervention_required || false;
  };

  // Separate resolved and unresolved incidents using new logic
  const resolvedIncidents = filteredIncidents.filter(incident => getIncidentStatus(incident) === "resolved");
  const unresolvedIncidents = filteredIncidents.filter(incident => getIncidentStatus(incident) !== "resolved");

  const severityStyles = {
    low: "bg-success/10 text-success border-success/30",
    medium: "bg-warning/10 text-warning border-warning/30",
    high: "bg-destructive/10 text-destructive border-destructive/30",
    critical: "bg-red-500/10 text-red-500 border-red-500/30",
  };

  const statusStyles = {
    resolved: "bg-success/10 text-success border-success/30",
    unresolved: "bg-warning/10 text-warning border-warning/30",
    under_review: "bg-blue-500/10 text-blue-500 border-blue-500/30",
    "in-progress": "bg-blue/10 text-blue border-blue/30",
    blocked: "bg-destructive/10 text-destructive border-destructive/30",
    completed: "bg-success/10 text-success border-success/30",
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="heading-2-professional">Incident Management</h1>
              <p className="body-small-professional">
                Review processed incidents and provide resolution feedback
              </p>
            </div>
            <Button
              onClick={loadIncidents}
              variant="outline"
              size="sm"
              className="btn-secondary-professional gap-2"
              disabled={loading}
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
          
          {totalCount > 0 && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <FileText className="h-4 w-4" />
              <span>{totalCount} total incidents processed</span>
            </div>
          )}
        </div>

        {/* Filters */}
        <div className="card-professional">
          <div className="card-content-professional">
            <div className="flex flex-col gap-4 sm:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search by ID, type, or location..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="form-input-professional pl-10"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-full sm:w-40 form-select-professional">
                <Filter className="mr-2 h-4 w-4" />
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="resolved">Resolved</SelectItem>
                <SelectItem value="in-progress">In Progress</SelectItem>
                <SelectItem value="blocked">Blocked</SelectItem>
              </SelectContent>
            </Select>
            <Select value={severityFilter} onValueChange={setSeverityFilter}>
              <SelectTrigger className="w-full sm:w-40 form-select-professional">
                <SelectValue placeholder="Severity" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Severity</SelectItem>
                <SelectItem value="low">Low</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="high">High</SelectItem>
              </SelectContent>
            </Select>
          </div>
          </div>
        </div>

        {/* Incidents Tabs */}
        <Tabs defaultValue="unresolved" className="space-y-6">
          <div className="flex items-center justify-between">
            <TabsList className="grid w-full max-w-md grid-cols-2">
              <TabsTrigger value="unresolved" className="flex items-center gap-2">
                <AlertCircle className="h-4 w-4" />
                Needs Review ({unresolvedIncidents.length})
              </TabsTrigger>
              <TabsTrigger value="resolved" className="flex items-center gap-2">
                <CheckCircle2 className="h-4 w-4" />
                Resolved ({resolvedIncidents.length})
              </TabsTrigger>
            </TabsList>
          </div>

          {/* Unresolved Incidents */}
          <TabsContent value="unresolved">
            <Card className="overflow-hidden">
              <div className="p-0">
                {loading ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="flex items-center gap-3">
                      <RefreshCw className="h-5 w-5 animate-spin text-primary" />
                      <span className="text-muted-foreground">Loading incident history...</span>
                    </div>
                  </div>
                ) : unresolvedIncidents.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-12">
                    <CheckCircle2 className="h-12 w-12 text-success mb-4" />
                    <h3 className="heading-4-professional mb-2">All Incidents Reviewed</h3>
                    <p className="body-small-professional text-center max-w-md">
                      No incidents are waiting for review. All submitted incidents have been processed and resolved by administrators.
                    </p>
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow className="hover:bg-transparent">
                        <TableHead>Incident ID</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead className="hidden md:table-cell">Location</TableHead>
                        <TableHead>Severity</TableHead>
                        <TableHead>Status</TableHead>
                        <TableHead className="hidden sm:table-cell">Date</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {unresolvedIncidents.map((incident) => (
                        <TableRow
                          key={incident.id}
                          className="cursor-pointer transition-colors hover:bg-muted/50"
                        >
                          <TableCell className="font-medium">
                            <div className="flex items-center gap-2">
                              <span className="truncate max-w-[120px]" title={incident.id}>
                                {incident.id}
                              </span>
                              {incident.ai_enhanced && (
                                <Badge variant="outline" className="text-xs bg-primary/10 text-primary border-primary/30 flex-shrink-0">
                                  AI
                                </Badge>
                              )}
                              {incident.complete_analysis?.incident_data?.gibberish_detected && (
                                <Badge variant="outline" className="text-xs bg-orange-50 text-orange-600 border-orange-200 flex-shrink-0">
                                  🚫 Gibberish
                                </Badge>
                              )}
                              {incident.complete_analysis?.incident_data?.requires_human_review && (
                                <Badge variant="outline" className="text-xs bg-yellow-50 text-yellow-600 border-yellow-200 flex-shrink-0">
                                  👤 Review Required
                                </Badge>
                              )}
                              {incident.metadata?.requires_human_review && (
                                <Badge variant="outline" className="text-xs bg-warning/10 text-warning border-warning/30 flex-shrink-0">
                                  👤 Human Review
                                </Badge>
                              )}
                              {incident.metadata?.review_status === "pending" && (
                                <Badge variant="outline" className="text-xs bg-destructive/10 text-destructive border-destructive/30 flex-shrink-0">
                                  ⏳ Pending Review
                                </Badge>
                              )}
                            </div>
                          </TableCell>
                          <TableCell>
                            <span className="truncate max-w-[100px] block" title={incident.type}>
                              {incident.type}
                            </span>
                          </TableCell>
                          <TableCell className="hidden md:table-cell text-muted-foreground">
                            <span className="truncate max-w-[150px] block" title={incident.location}>
                              {incident.location.split(",")[0]}
                            </span>
                          </TableCell>
                          <TableCell>
                            <Badge
                              variant="outline"
                              className={severityStyles[incident.severity as keyof typeof severityStyles]}
                            >
                              {incident.severity}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <div className="flex items-center gap-2">
                              <Badge
                                variant="outline"
                                className={statusStyles[getIncidentStatus(incident) as keyof typeof statusStyles]}
                              >
                                {getIncidentStatus(incident).replace('_', ' ')}
                              </Badge>
                              {requiresHumanIntervention(incident) && (
                                <Badge variant="outline" className="text-xs bg-yellow-50 text-yellow-600 border-yellow-200">
                                  👤 Review Required
                                </Badge>
                              )}
                            </div>
                          </TableCell>
                          <TableCell className="hidden sm:table-cell text-muted-foreground">
                            {incident.date}
                          </TableCell>
                          <TableCell className="text-right">
                            <div className="flex items-center gap-2 justify-end">
                              <Button
                                variant="ghost"
                                size="sm"
                                onClick={() => setSelectedIncident(incident)}
                                className="gap-2"
                              >
                                <Eye className="h-4 w-4" />
                                <span className="hidden sm:inline">View</span>
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => openResolutionDialog(incident)}
                                className="gap-2 text-green-600 border-green-200 hover:bg-green-50"
                              >
                                <CheckCircle2 className="h-4 w-4" />
                                <span className="hidden sm:inline">Resolve</span>
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => markAsSpam(incident, true)}
                                className="gap-2 text-orange-600 border-orange-200 hover:bg-orange-50"
                                title="Mark as gibberish/nonsensical text"
                              >
                                <AlertTriangle className="h-4 w-4" />
                                <span className="hidden sm:inline">Gibberish</span>
                              </Button>
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => markAsSpam(incident, false)}
                                className="gap-2 text-red-600 border-red-200 hover:bg-red-50"
                                title="Mark as spam"
                              >
                                <XCircle className="h-4 w-4" />
                                <span className="hidden sm:inline">Spam</span>
                              </Button>
                            </div>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </div>
            </Card>
          </TabsContent>

          {/* Resolved Incidents */}
          <TabsContent value="resolved">
            <Card className="overflow-hidden">
              <div className="p-0">
                {loading ? (
                  <div className="flex items-center justify-center py-12">
                    <div className="flex items-center gap-3">
                      <RefreshCw className="h-5 w-5 animate-spin text-primary" />
                      <span className="text-muted-foreground">Loading incident history...</span>
                    </div>
                  </div>
                ) : resolvedIncidents.length === 0 ? (
                  <div className="flex flex-col items-center justify-center py-12">
                    <AlertCircle className="h-12 w-12 text-muted-foreground mb-4" />
                    <h3 className="heading-4-professional mb-2">No Resolved Incidents</h3>
                    <p className="body-small-professional text-center max-w-md">
                      No incidents have been resolved yet. Resolve incidents from the unresolved tab to see them here.
                    </p>
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow className="hover:bg-transparent">
                        <TableHead>Incident ID</TableHead>
                        <TableHead>Type</TableHead>
                        <TableHead className="hidden md:table-cell">Location</TableHead>
                        <TableHead>Severity</TableHead>
                        <TableHead className="hidden sm:table-cell">Resolved Date</TableHead>
                        <TableHead className="hidden lg:table-cell">Resolved By</TableHead>
                        <TableHead className="text-right">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {resolvedIncidents.map((incident) => (
                        <TableRow
                          key={incident.id}
                          className="cursor-pointer transition-colors hover:bg-muted/50"
                        >
                          <TableCell className="font-medium">
                            <div className="flex items-center gap-2">
                              {incident.id}
                              <CheckCircle2 className="h-3 w-3 text-green-500" />
                              {incident.ai_enhanced && (
                                <Badge variant="outline" className="text-xs bg-primary/10 text-primary border-primary/30">
                                  AI
                                </Badge>
                              )}
                              {incident.complete_analysis?.incident_data?.gibberish_detected && (
                                <Badge variant="outline" className="text-xs bg-orange-50 text-orange-600 border-orange-200">
                                  🚫 Was Gibberish
                                </Badge>
                              )}
                              {incident.complete_analysis?.incident_data?.requires_human_review && (
                                <Badge variant="outline" className="text-xs bg-success/10 text-success border-success/30">
                                  ✅ Reviewed
                                </Badge>
                              )}
                              {incident.metadata?.requires_human_review && (
                                <Badge variant="outline" className="text-xs bg-success/10 text-success border-success/30">
                                  ✅ Reviewed
                                </Badge>
                              )}
                            </div>
                          </TableCell>
                          <TableCell>{incident.type}</TableCell>
                          <TableCell className="hidden md:table-cell text-muted-foreground">
                            {incident.location.split(",")[0]}
                          </TableCell>
                          <TableCell>
                            <Badge
                              variant="outline"
                              className={severityStyles[incident.severity as keyof typeof severityStyles]}
                            >
                              {incident.severity}
                            </Badge>
                          </TableCell>
                          <TableCell className="hidden sm:table-cell text-muted-foreground">
                            {incident.resolved_at ? new Date(incident.resolved_at).toLocaleDateString() : incident.date}
                          </TableCell>
                          <TableCell className="hidden lg:table-cell text-muted-foreground">
                            {incident.resolved_by || "System"}
                          </TableCell>
                          <TableCell className="text-right">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => setSelectedIncident(incident)}
                              className="gap-2 "
                            >
                              <Eye className="h-4 w-4" />
                              <span className="hidden sm:inline">View</span>
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </div>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Incident Detail Modal */}
        <Dialog open={!!selectedIncident} onOpenChange={() => setSelectedIncident(null)}>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            {selectedIncident && (
              <>
                <DialogHeader>
                  <DialogTitle className="flex items-center justify-between">
                    <span>{selectedIncident.id}</span>
                    <div className="flex gap-2">
                      <Badge
                        variant="outline"
                        className={severityStyles[selectedIncident.severity as keyof typeof severityStyles]}
                      >
                        {selectedIncident.severity}
                      </Badge>
                      <Badge
                        variant="outline"
                        className={statusStyles[getIncidentStatus(selectedIncident) as keyof typeof statusStyles]}
                      >
                        {getIncidentStatus(selectedIncident).replace('_', ' ')}
                      </Badge>
                      {requiresHumanIntervention(selectedIncident) && (
                        <Badge variant="outline" className="text-xs bg-yellow-50 text-yellow-600 border-yellow-200">
                          👤 Review Required
                        </Badge>
                      )}
                    </div>
                  </DialogTitle>
                </DialogHeader>

                <div className="space-y-6">
                  {/* Meta Info */}
                  <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    <div className="flex items-center gap-2 text-sm">
                      <FileText className="h-4 w-4 text-muted-foreground" />
                      <span className="text-muted-foreground">Type:</span>
                      <span className="font-medium">{selectedIncident.type}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <MapPin className="h-4 w-4 text-muted-foreground" />
                      <span className="text-muted-foreground">Location:</span>
                      <span className="font-medium">{selectedIncident.location}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Clock className="h-4 w-4 text-muted-foreground" />
                      <span className="text-muted-foreground">Incident Date:</span>
                      <span className="font-medium">{selectedIncident.date}</span>
                    </div>
                    {selectedIncident.metadata?.submission_timestamp && (
                      <div className="flex items-center gap-2 text-sm">
                        <Clock className="h-4 w-4 text-muted-foreground" />
                        <span className="text-muted-foreground">Reported:</span>
                        <span className="font-medium">
                          {new Date(selectedIncident.metadata.submission_timestamp).toLocaleString()}
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Spam Detection Alert */}
                  {selectedIncident.complete_analysis?.incident_data?.spam_detected && (
                    <div className="flex items-center gap-2 p-3 bg-red-50 dark:bg-red-950/20 border border-red-200 dark:border-red-800 rounded-lg">
                      <XCircle className="h-4 w-4 text-red-600" />
                      <div className="flex-1">
                        <span className="text-sm font-medium text-red-800 dark:text-red-200">
                          {selectedIncident.complete_analysis.incident_data.spam_category === 'gibberish' ? 'Gibberish Detected' : 'Spam Detected'}
                        </span>
                        <p className="text-xs text-red-700 dark:text-red-300">
                          This report was flagged as potential {selectedIncident.complete_analysis.incident_data.spam_category} and sent for human review.
                        </p>
                      </div>
                      <Badge variant="outline" className="bg-red-100 text-red-700 border-red-300">
                        Human Review Required
                      </Badge>
                    </div>
                  )}

                  {/* Gibberish Detection Alert (legacy support) */}
                  {selectedIncident.complete_analysis?.incident_data?.gibberish_detected && !selectedIncident.complete_analysis?.incident_data?.spam_detected && (
                    <div className="flex items-center gap-2 p-3 bg-orange-50 dark:bg-orange-950/20 border border-orange-200 dark:border-orange-800 rounded-lg">
                      <AlertTriangle className="h-4 w-4 text-orange-600" />
                      <div className="flex-1">
                        <span className="text-sm font-medium text-orange-800 dark:text-orange-200">Gibberish Detected</span>
                        <p className="text-xs text-orange-700 dark:text-orange-300">
                          This report was automatically flagged as potential gibberish and sent for human review.
                        </p>
                      </div>
                      <Badge variant="outline" className="bg-orange-100 text-orange-700 border-orange-300">
                        Human Review Required
                      </Badge>
                    </div>
                  )}

                  {/* AI Enhancement Badge with Confidence - Only for non-spam cases */}
                  {selectedIncident.ai_enhanced && 
                   !selectedIncident.complete_analysis?.incident_data?.spam_detected && 
                   !selectedIncident.complete_analysis?.incident_data?.gibberish_detected && (
                    <div className="flex items-center gap-2 p-3 bg-primary/5 border border-primary/20 rounded-lg">
                      <div className="h-2 w-2 rounded-full bg-primary animate-pulse" />
                      <span className="text-sm font-medium">AI-Enhanced Analysis</span>
                      {selectedIncident.complete_analysis?.evaluation_report?.confidence_analysis ? (
                        <Badge 
                          variant="outline" 
                          className={
                            selectedIncident.complete_analysis.evaluation_report.confidence_analysis.overall_confidence >= 75 
                              ? "bg-green-50 text-green-700 border-green-200" 
                              : selectedIncident.complete_analysis.evaluation_report.confidence_analysis.overall_confidence >= 50
                              ? "bg-yellow-50 text-yellow-700 border-yellow-200"
                              : "bg-red-50 text-red-700 border-red-200"
                          }
                        >
                          Confidence: {selectedIncident.complete_analysis.evaluation_report.confidence_analysis.overall_confidence.toFixed(1)}%
                        </Badge>
                      ) : (
                        <Badge variant="outline" className="bg-primary/10 text-primary border-primary/30">
                          Confidence: {selectedIncident.confidence_score || 'N/A'}%
                        </Badge>
                      )}
                    </div>
                  )}

                  {/* Safety-First Resolution Status */}
                  {selectedIncident.complete_analysis?.evaluation_report && (
                    <div className="rounded-lg bg-muted/30 p-4 border">
                      <h4 className="text-sm font-medium mb-3 flex items-center gap-2">
                        <Shield className="h-4 w-4" />
                        Resolution Assessment
                      </h4>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm text-muted-foreground">Status</span>
                          <Badge 
                            variant="outline"
                            className={statusStyles[getIncidentStatus(selectedIncident) as keyof typeof statusStyles]}
                          >
                            {getIncidentStatus(selectedIncident).replace('_', ' ')}
                          </Badge>
                        </div>
                        
                        <div>
                          <span className="text-xs text-muted-foreground">Reason</span>
                          <p className="text-sm">{getResolutionReason(selectedIncident)}</p>
                        </div>
                        
                        {requiresHumanIntervention(selectedIncident) && (
                          <div className="flex items-center gap-2 p-2 bg-yellow-50 dark:bg-yellow-950/20 rounded border border-yellow-200 dark:border-yellow-800">
                            <AlertTriangle className="h-3 w-3 text-yellow-600" />
                            <span className="text-xs text-yellow-700 dark:text-yellow-300">
                              Human review required for final resolution
                            </span>
                          </div>
                        )}
                        
                        {selectedIncident.complete_analysis.evaluation_report.resolution_details && (
                          <div>
                            <span className="text-xs text-muted-foreground">Details</span>
                            <p className="text-xs text-muted-foreground">
                              {selectedIncident.complete_analysis.evaluation_report.resolution_details}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Resolution Information */}
                  {selectedIncident.status === "resolved" && selectedIncident.resolution_feedback && (
                    <div className="rounded-lg bg-green-50/50 dark:bg-green-950/20 p-4 border border-green-200 dark:border-green-800">
                      <h4 className="text-sm font-medium mb-3 flex items-center gap-2">
                        <CheckCircle2 className="h-4 w-4 text-green-500" />
                        Resolution Details
                      </h4>
                      <div className="space-y-2">
                        <div>
                          <span className="text-xs text-muted-foreground">Resolved By</span>
                          <p className="text-sm font-medium">{selectedIncident.resolved_by || "System"}</p>
                        </div>
                        <div>
                          <span className="text-xs text-muted-foreground">Resolution Date</span>
                          <p className="text-sm">{selectedIncident.resolved_at ? new Date(selectedIncident.resolved_at).toLocaleString() : "N/A"}</p>
                        </div>
                        <div>
                          <span className="text-xs text-muted-foreground">Resolution Feedback</span>
                          <p className="text-sm bg-white dark:bg-gray-900 p-3 rounded border mt-1">
                            {selectedIncident.resolution_feedback}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Original Report */}
                  <div className="rounded-lg bg-muted/30 p-4">
                    <h4 className="text-sm font-medium mb-2">Original Report</h4>
                    <p className="text-sm text-muted-foreground">
                      {selectedIncident.description}
                    </p>
                  </div>

                  {/* AI Entities (if available) */}
                  {selectedIncident.entities && Object.keys(selectedIncident.entities).length > 0 && (
                    <div className="rounded-lg bg-blue-50/50 dark:bg-blue-950/20 p-4">
                      <h4 className="text-sm font-medium mb-3 flex items-center gap-2">
                        <span className="h-2 w-2 rounded-full bg-blue-500" />
                        AI-Extracted Entities
                      </h4>
                      <div className="grid gap-3 sm:grid-cols-2">
                        {Object.entries(selectedIncident.entities).map(([type, items]) => (
                          items && Array.isArray(items) && items.length > 0 && (
                            <div key={type}>
                              <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                                {type}
                              </span>
                              <div className="flex flex-wrap gap-1 mt-1">
                                {items.map((item, index) => (
                                  <Badge key={index} variant="secondary" className="text-xs">
                                    {item}
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Complete Analysis Sections */}
                  {selectedIncident.complete_analysis && (
                    <>
                      {/* Response Plan */}
                      {selectedIncident.complete_analysis.response_plan && (
                        <div className="rounded-lg bg-green-50/50 dark:bg-green-950/20 p-4">
                          <h4 className="text-sm font-medium mb-3 flex items-center gap-2">
                            <span className="h-2 w-2 rounded-full bg-green-500" />
                            AI Response Plan
                          </h4>
                          <div className="space-y-3">
                            <div className="grid gap-2 sm:grid-cols-2">
                              <div>
                                <span className="text-xs text-muted-foreground">Plan Type</span>
                                <p className="font-medium">{selectedIncident.complete_analysis.response_plan.plan_type || 'Standard Response'}</p>
                              </div>
                              <div>
                                <span className="text-xs text-muted-foreground">Priority Level</span>
                                <p className="font-medium">{selectedIncident.complete_analysis.response_plan.priority_level || 'Medium'}</p>
                              </div>
                            </div>
                            
                            {selectedIncident.complete_analysis.response_plan.immediate_actions && (
                              <div>
                                <span className="text-xs text-muted-foreground">Immediate Actions</span>
                                <ul className="mt-1 space-y-1">
                                  {selectedIncident.complete_analysis.response_plan.immediate_actions.map((action, index) => (
                                    <li key={index} className="flex items-start gap-2 text-sm">
                                      <div className="h-1.5 w-1.5 rounded-full bg-green-500 mt-2 flex-shrink-0" />
                                      <span>{action.description || action}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Compliance Report */}
                      {selectedIncident.complete_analysis.compliance_report && (
                        <div className="rounded-lg bg-orange-50/50 dark:bg-orange-950/20 p-4">
                          <h4 className="text-sm font-medium mb-3 flex items-center gap-2">
                            <span className="h-2 w-2 rounded-full bg-orange-500" />
                            Safety & Compliance Analysis
                          </h4>
                          <div className="space-y-2">
                            <div>
                              <span className="text-xs text-muted-foreground">Compliance Status</span>
                              <p className="text-sm">{selectedIncident.complete_analysis.compliance_report.compliance_status || 'Compliant'}</p>
                            </div>
                            <div>
                              <span className="text-xs text-muted-foreground">Safety Assessment</span>
                              <p className="text-sm">{selectedIncident.complete_analysis.compliance_report.compliance_summary || selectedIncident.safetyDecision}</p>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Execution Summary */}
                      {selectedIncident.complete_analysis.execution_summary && (
                        <div className="rounded-lg bg-purple-50/50 dark:bg-purple-950/20 p-4">
                          <h4 className="text-sm font-medium mb-3 flex items-center gap-2">
                            <span className="h-2 w-2 rounded-full bg-purple-500" />
                            Execution Summary
                          </h4>
                          <div className="grid gap-2 sm:grid-cols-2">
                            <div>
                              <span className="text-xs text-muted-foreground">Overall Status</span>
                              <p className="font-medium">{selectedIncident.complete_analysis.execution_summary.overall_status || 'Completed'}</p>
                            </div>
                            <div>
                              <span className="text-xs text-muted-foreground">Success Rate</span>
                              <p className="font-medium">{selectedIncident.complete_analysis.execution_summary.success_rate || 100}%</p>
                            </div>
                          </div>
                        </div>
                      )}

                      {/* Evaluation Report */}
                      {selectedIncident.complete_analysis.evaluation_report && (
                        <div className="rounded-lg bg-indigo-50/50 dark:bg-indigo-950/20 p-4">
                          <h4 className="text-sm font-medium mb-3 flex items-center gap-2">
                            <span className="h-2 w-2 rounded-full bg-indigo-500" />
                            AI Evaluation & Recommendations
                          </h4>
                          <div className="space-y-3">
                            <div className="grid gap-2 sm:grid-cols-2">
                              <div>
                                <span className="text-xs text-muted-foreground">Overall Score</span>
                                <p className="font-medium">{selectedIncident.complete_analysis.evaluation_report.overall_score || 0}/100</p>
                              </div>
                              <div>
                                <span className="text-xs text-muted-foreground">Effectiveness Rating</span>
                                <p className="font-medium">{selectedIncident.complete_analysis.evaluation_report.effectiveness_rating || 'Good'}</p>
                              </div>
                            </div>
                            
                            {selectedIncident.complete_analysis.evaluation_report.improvement_recommendations && (
                              <div>
                                <span className="text-xs text-muted-foreground">Recommendations</span>
                                <ul className="mt-1 space-y-1">
                                  {selectedIncident.complete_analysis.evaluation_report.improvement_recommendations.map((rec, index) => (
                                    <li key={index} className="flex items-start gap-2 text-sm">
                                      <div className="h-1.5 w-1.5 rounded-full bg-indigo-500 mt-2 flex-shrink-0" />
                                      <span>{rec.title || rec.description || rec}</span>
                                    </li>
                                  ))}
                                </ul>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Confidence Index Analysis - Only show for NON-gibberish cases */}
                      {selectedIncident.complete_analysis.evaluation_report?.confidence_analysis && 
                       !selectedIncident.complete_analysis.incident_data?.gibberish_detected && (
                        <div className="rounded-lg bg-gradient-to-r from-blue-50/50 to-purple-50/50 dark:from-blue-950/20 dark:to-purple-950/20 p-4 border border-blue-200/50 dark:border-blue-800/50">
                          <h4 className="text-sm font-medium mb-3 flex items-center gap-2">
                            <span className="h-2 w-2 rounded-full bg-gradient-to-r from-blue-500 to-purple-500" />
                            AI Confidence Index Analysis
                          </h4>
                          
                          {(() => {
                            const confidence = selectedIncident.complete_analysis.evaluation_report.confidence_analysis;
                            const overallConfidence = confidence.overall_confidence || 0;
                            const confidenceLevel = confidence.confidence_level || 'medium';
                            const recommendation = confidence.resolution_recommendation || 'supervised';
                            
                            // Determine confidence color based on level
                            const confidenceColor = overallConfidence >= 75 ? 'text-green-600' : 
                                                   overallConfidence >= 50 ? 'text-yellow-600' : 'text-red-600';
                            const confidenceBg = overallConfidence >= 75 ? 'bg-green-100 dark:bg-green-950/30' : 
                                                overallConfidence >= 50 ? 'bg-yellow-100 dark:bg-yellow-950/30' : 'bg-red-100 dark:bg-red-950/30';
                            
                            return (
                              <div className="space-y-4">
                                {/* Overall Confidence Score */}
                                <div className="flex items-center justify-between">
                                  <div className="flex items-center gap-3">
                                    <div className={`px-3 py-1 rounded-full ${confidenceBg}`}>
                                      <span className={`text-sm font-bold ${confidenceColor}`}>
                                        {overallConfidence.toFixed(1)}%
                                      </span>
                                    </div>
                                    <div>
                                      <p className="text-sm font-medium">Overall Confidence</p>
                                      <p className="text-xs text-muted-foreground capitalize">
                                        {confidenceLevel} confidence • {recommendation.replace('_', ' ')} resolution
                                      </p>
                                    </div>
                                  </div>
                                  
                                  <div className="text-right">
                                    <Badge 
                                      variant="outline" 
                                      className={
                                        recommendation === 'autonomous' ? 'bg-green-50 text-green-700 border-green-200' :
                                        recommendation === 'supervised' ? 'bg-yellow-50 text-yellow-700 border-yellow-200' :
                                        'bg-red-50 text-red-700 border-red-200'
                                      }
                                    >
                                      {recommendation === 'autonomous' ? '🤖 AI Autonomous' :
                                       recommendation === 'supervised' ? '👥 AI + Human' :
                                       '👤 Human Required'}
                                    </Badge>
                                  </div>
                                </div>

                                {/* Factor Scores */}
                                {confidence.factor_scores && (
                                  <div>
                                    <p className="text-xs font-medium text-muted-foreground mb-2">CONFIDENCE FACTORS</p>
                                    <div className="grid gap-2 sm:grid-cols-2">
                                      {Object.entries(confidence.factor_scores).map(([factor, score]) => {
                                        const factorScore = typeof score === 'number' ? score : 0;
                                        const factorColor = factorScore >= 80 ? 'bg-green-500' : 
                                                          factorScore >= 60 ? 'bg-yellow-500' : 'bg-red-500';
                                        
                                        return (
                                          <div key={factor} className="flex items-center justify-between text-xs">
                                            <span className="text-muted-foreground capitalize">
                                              {factor.replace('_', ' ')}
                                            </span>
                                            <div className="flex items-center gap-2">
                                              <div className="w-16 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                                                <div 
                                                  className={`h-full ${factorColor} transition-all duration-300`}
                                                  style={{ width: `${Math.min(factorScore, 100)}%` }}
                                                />
                                              </div>
                                              <span className="font-medium w-8 text-right">
                                                {factorScore.toFixed(0)}%
                                              </span>
                                            </div>
                                          </div>
                                        );
                                      })}
                                    </div>
                                  </div>
                                )}

                                {/* Confidence Reasoning */}
                                {confidence.confidence_reasoning && confidence.confidence_reasoning.length > 0 && (
                                  <div>
                                    <p className="text-xs font-medium text-muted-foreground mb-2">CONFIDENCE REASONING</p>
                                    <ul className="space-y-1">
                                      {confidence.confidence_reasoning.slice(0, 3).map((reason, index) => (
                                        <li key={index} className="flex items-start gap-2 text-xs">
                                          <div className="h-1 w-1 rounded-full bg-blue-500 mt-1.5 flex-shrink-0" />
                                          <span className="text-muted-foreground">{reason}</span>
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                )}

                                {/* Intervention Triggers */}
                                {confidence.intervention_triggers && confidence.intervention_triggers.length > 0 && (
                                  <div className="p-3 bg-yellow-50/50 dark:bg-yellow-950/20 rounded border border-yellow-200/50 dark:border-yellow-800/50">
                                    <p className="text-xs font-medium text-yellow-800 dark:text-yellow-200 mb-2 flex items-center gap-1">
                                      <AlertTriangle className="h-3 w-3" />
                                      INTERVENTION TRIGGERS
                                    </p>
                                    <ul className="space-y-1">
                                      {confidence.intervention_triggers.map((trigger, index) => (
                                        <li key={index} className="flex items-start gap-2 text-xs">
                                          <div className="h-1 w-1 rounded-full bg-yellow-600 mt-1.5 flex-shrink-0" />
                                          <span className="text-yellow-700 dark:text-yellow-300">{trigger}</span>
                                        </li>
                                      ))}
                                    </ul>
                                  </div>
                                )}

                                {/* Threshold Analysis */}
                                {confidence.threshold_analysis && (
                                  <div className="text-xs text-muted-foreground bg-gray-50/50 dark:bg-gray-900/50 p-2 rounded border">
                                    <div className="flex justify-between items-center">
                                      <span>Autonomous Threshold: {confidence.threshold_analysis.autonomous_threshold || 75}%</span>
                                      <span>Human Intervention: {confidence.threshold_analysis.human_intervention_threshold || 50}%</span>
                                    </div>
                                    <div className="mt-1 text-center">
                                      <span className={`font-medium ${confidenceColor}`}>
                                        Current: {overallConfidence.toFixed(1)}% → {
                                          confidence.threshold_analysis.can_resolve_autonomously ? 'Can resolve autonomously' :
                                          confidence.threshold_analysis.requires_human_intervention ? 'Requires human intervention' :
                                          'Requires supervision'
                                        }
                                      </span>
                                    </div>
                                  </div>
                                )}
                              </div>
                            );
                          })()}
                        </div>
                      )}
                    </>
                  )}

                  {/* Legacy Actions (fallback) */}
                  {!selectedIncident.complete_analysis && selectedIncident.actions && selectedIncident.actions.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium mb-3">Actions Taken</h4>
                      <ul className="space-y-2">
                        {selectedIncident.actions.map((action, index) => (
                          <li
                            key={index}
                            className="flex items-center gap-2 text-sm text-muted-foreground"
                          >
                            <div className="h-1.5 w-1.5 rounded-full bg-primary" />
                            {action}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Legacy Feedback (fallback) */}
                  {!selectedIncident.complete_analysis && (
                    <>
                      <div className="rounded-lg bg-success/5 border border-success/20 p-4">
                        <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                          <span className="h-2 w-2 rounded-full bg-success" />
                          Safety & Policy Decision
                        </h4>
                        <p className="text-sm text-muted-foreground">
                          {selectedIncident.safetyDecision}
                        </p>
                      </div>

                      <div className="rounded-lg bg-primary/5 border border-primary/20 p-4">
                        <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
                          <span className="h-2 w-2 rounded-full bg-primary" />
                          Evaluator Feedback
                        </h4>
                        <p className="text-sm text-muted-foreground">
                          {selectedIncident.evaluatorFeedback}
                        </p>
                      </div>
                    </>
                  )}
                </div>
              </>
            )}
          </DialogContent>
        </Dialog>

        {/* Resolution Dialog */}
        <Dialog open={showResolutionDialog} onOpenChange={setShowResolutionDialog}>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-500" />
                Resolve Incident
              </DialogTitle>
            </DialogHeader>

            {resolvingIncident && (
              <div className="space-y-6">
                {/* Incident Summary */}
                <div className="p-4 bg-muted/50 rounded-lg border">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <div className="text-sm font-medium mb-1">{resolvingIncident.id}</div>
                      <div className="text-xs text-muted-foreground mb-2">
                        {resolvingIncident.type} • {resolvingIncident.location}
                      </div>
                      <div className="text-xs bg-white dark:bg-gray-900 p-2 rounded border">
                        {resolvingIncident.description.length > 100 
                          ? `${resolvingIncident.description.substring(0, 100)}...`
                          : resolvingIncident.description
                        }
                      </div>
                    </div>
                    <Badge
                      variant="outline"
                      className={severityStyles[resolvingIncident.severity as keyof typeof severityStyles]}
                    >
                      {resolvingIncident.severity}
                    </Badge>
                  </div>
                </div>

                {/* Resolution Instructions */}
                <div className="p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg border border-blue-200 dark:border-blue-800">
                  <h4 className="text-sm font-medium text-blue-900 dark:text-blue-100 mb-1">
                    Resolution Required
                  </h4>
                  <p className="text-xs text-blue-700 dark:text-blue-300">
                    This incident has been processed by AI but requires admin review and resolution. 
                    Please provide details about the actions taken to resolve this incident.
                  </p>
                </div>

                {/* Resolution Feedback */}
                <div className="space-y-2">
                  <label className="text-sm font-medium">Resolution Details *</label>
                  <Textarea
                    placeholder="Describe the actions taken to resolve this incident...

Examples:
• Contacted campus security and they investigated the area
• Maintenance was notified and fixed the safety hazard
• Student was referred to counseling services
• Policy violation was documented and appropriate measures taken"
                    value={resolutionFeedback}
                    onChange={(e) => setResolutionFeedback(e.target.value)}
                    rows={6}
                    className="resize-none"
                  />
                  <div className="flex items-center justify-between">
                    <p className="text-xs text-muted-foreground">
                      Provide specific details about resolution actions and outcomes.
                    </p>
                    <span className="text-xs text-muted-foreground">
                      {resolutionFeedback.length}/500
                    </span>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex justify-end gap-3 pt-4 border-t">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setShowResolutionDialog(false);
                      setResolutionFeedback("");
                      setResolvingIncident(null);
                    }}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleResolveIncident}
                    disabled={!resolutionFeedback.trim() || resolutionFeedback.length < 20}
                    className="bg-green-600 hover:bg-green-700 min-w-[140px]"
                  >
                    <CheckCircle2 className="h-4 w-4 mr-2" />
                    Mark as Resolved
                  </Button>
                </div>
              </div>
            )}
          </DialogContent>
        </Dialog>

        {/* Footer */}
        <footer className="mt-8 border-t border-border pt-6 text-center">
          <p className="body-small-professional">
            Campus Safety Management System
          </p>
        </footer>
      </div>
    </MainLayout>
  );
}
