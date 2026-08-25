import { useState, useEffect } from "react";
import { MainLayout } from "@/components/layout/MainLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
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
import { 
  Shield, 
  Eye, 
  Clock, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle, 
  FileText,
  RefreshCw,
  User,
  Lock,
  Search,
  Filter
} from "lucide-react";
import { apiClient } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

interface ReviewItem {
  incident_id: string;
  created_at: string;
  status: string;
  reasons: string[];
  explanation: string;
  priority: string;
  incident_data: any;
  file_analyses: any[];
  reviewer_id?: string;
  review_started_at?: string;
}

export default function HumanReview() {
  const [reviewQueue, setReviewQueue] = useState<ReviewItem[]>([]);
  const [selectedItem, setSelectedItem] = useState<ReviewItem | null>(null);
  const [loading, setLoading] = useState(true);
  const [priorityFilter, setPriorityFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("pending");
  const [reviewAction, setReviewAction] = useState("");
  const [reviewNotes, setReviewNotes] = useState("");
  const [reviewerId, setReviewerId] = useState("admin"); // In real app, get from auth
  const [summary, setSummary] = useState<any>({});
  const { toast } = useToast();

  const loadReviewQueue = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getReviewQueue(
        priorityFilter === "all" ? undefined : priorityFilter,
        statusFilter === "all" ? undefined : statusFilter
      );
      
      if (response.success) {
        setReviewQueue(response.queue);
        setSummary(response.summary);
      }
    } catch (error) {
      console.error("Error loading review queue:", error);
      toast({
        title: "Error Loading Review Queue",
        description: error instanceof Error ? error.message : "Failed to load review queue",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadReviewQueue();
  }, [priorityFilter, statusFilter]);

  const handleStartReview = async (item: ReviewItem) => {
    try {
      await apiClient.startReview(item.incident_id, reviewerId);
      setSelectedItem(item);
      toast({
        title: "Review Started",
        description: `Started reviewing incident ${item.incident_id}`,
      });
    } catch (error) {
      toast({
        title: "Error Starting Review",
        description: error instanceof Error ? error.message : "Failed to start review",
        variant: "destructive",
      });
    }
  };

  const handleCompleteReview = async () => {
    if (!selectedItem || !reviewAction || !reviewNotes.trim()) {
      toast({
        title: "Incomplete Review",
        description: "Please select an action and provide notes",
        variant: "destructive",
      });
      return;
    }

    try {
      await apiClient.completeReview(selectedItem.incident_id, reviewAction, reviewNotes);
      
      toast({
        title: "Review Completed",
        description: `Review completed for incident ${selectedItem.incident_id}`,
      });
      
      setSelectedItem(null);
      setReviewAction("");
      setReviewNotes("");
      loadReviewQueue(); // Refresh the queue
      
    } catch (error) {
      toast({
        title: "Error Completing Review",
        description: error instanceof Error ? error.message : "Failed to complete review",
        variant: "destructive",
      });
    }
  };

  const getPriorityBadge = (priority: string) => {
    const styles = {
      high: "bg-destructive/10 text-destructive border-destructive/30",
      medium: "bg-warning/10 text-warning border-warning/30",
      low: "bg-muted/10 text-muted-foreground border-muted/30",
    };
    return styles[priority as keyof typeof styles] || styles.low;
  };

  const getStatusBadge = (status: string) => {
    const styles = {
      pending: "bg-warning/10 text-warning border-warning/30",
      in_review: "bg-blue/10 text-blue border-blue/30",
      approved: "bg-success/10 text-success border-success/30",
      rejected: "bg-destructive/10 text-destructive border-destructive/30",
    };
    return styles[status as keyof typeof styles] || styles.pending;
  };

  const getReasonIcon = (reason: string) => {
    const icons = {
      anonymous_report: <Lock className="h-4 w-4" />,
      suspicious_file: <AlertTriangle className="h-4 w-4" />,
      unverifiable_file: <FileText className="h-4 w-4" />,
      high_risk_content: <Shield className="h-4 w-4" />,
    };
    return icons[reason as keyof typeof icons] || <AlertTriangle className="h-4 w-4" />;
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col gap-2">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold">Human Review Dashboard</h1>
              <p className="text-muted-foreground text-sm">
                Review incidents requiring human oversight for safety and authenticity
              </p>
            </div>
            <Button
              onClick={loadReviewQueue}
              variant="outline"
              size="sm"
              className="gap-2"
              disabled={loading}
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-warning" />
                <div>
                  <div className="text-2xl font-bold">{summary.total_pending || 0}</div>
                  <div className="text-xs text-muted-foreground">Pending Review</div>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <Lock className="h-4 w-4 text-primary" />
                <div>
                  <div className="text-2xl font-bold">{summary.anonymous_reports || 0}</div>
                  <div className="text-xs text-muted-foreground">Anonymous Reports</div>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-destructive" />
                <div>
                  <div className="text-2xl font-bold">{summary.suspicious_files || 0}</div>
                  <div className="text-xs text-muted-foreground">Suspicious Files</div>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <Shield className="h-4 w-4 text-success" />
                <div>
                  <div className="text-2xl font-bold">{summary.high_priority || 0}</div>
                  <div className="text-xs text-muted-foreground">High Priority</div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="p-6">
            <div className="flex flex-col gap-4 sm:flex-row">
              <Select value={priorityFilter} onValueChange={setPriorityFilter}>
                <SelectTrigger className="w-full sm:w-40">
                  <Filter className="mr-2 h-4 w-4" />
                  <SelectValue placeholder="Priority" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Priority</SelectItem>
                  <SelectItem value="high">High</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="low">Low</SelectItem>
                </SelectContent>
              </Select>
              
              <Select value={statusFilter} onValueChange={setStatusFilter}>
                <SelectTrigger className="w-full sm:w-40">
                  <SelectValue placeholder="Status" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Status</SelectItem>
                  <SelectItem value="pending">Pending</SelectItem>
                  <SelectItem value="in_review">In Review</SelectItem>
                  <SelectItem value="approved">Approved</SelectItem>
                  <SelectItem value="rejected">Rejected</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Review Queue */}
        <Card>
          <CardHeader>
            <CardTitle>Review Queue</CardTitle>
          </CardHeader>
          <CardContent className="p-0">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="flex items-center gap-3">
                  <RefreshCw className="h-5 w-5 animate-spin text-primary" />
                  <span className="text-muted-foreground">Loading review queue...</span>
                </div>
              </div>
            ) : reviewQueue.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12">
                <CheckCircle2 className="h-12 w-12 text-green-500 mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Items for Review</h3>
                <p className="text-muted-foreground text-center max-w-md">
                  All incidents have been reviewed or no incidents require human oversight at this time.
                </p>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Incident ID</TableHead>
                    <TableHead>Priority</TableHead>
                    <TableHead>Status</TableHead>
                    <TableHead>Reasons</TableHead>
                    <TableHead>Created</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {reviewQueue.map((item) => (
                    <TableRow key={item.incident_id}>
                      <TableCell className="font-medium">
                        {item.incident_id}
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className={getPriorityBadge(item.priority)}>
                          {item.priority.toUpperCase()}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline" className={getStatusBadge(item.status)}>
                          {item.status.replace('_', ' ').toUpperCase()}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        <div className="flex gap-1">
                          {item.reasons.slice(0, 2).map((reason, index) => (
                            <div key={index} className="flex items-center gap-1 text-xs">
                              {getReasonIcon(reason)}
                              <span className="hidden sm:inline">
                                {reason.replace('_', ' ')}
                              </span>
                            </div>
                          ))}
                          {item.reasons.length > 2 && (
                            <span className="text-xs text-muted-foreground">
                              +{item.reasons.length - 2} more
                            </span>
                          )}
                        </div>
                      </TableCell>
                      <TableCell className="text-muted-foreground">
                        {new Date(item.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleStartReview(item)}
                          className="gap-2"
                        >
                          <Eye className="h-4 w-4" />
                          Review
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* Review Dialog */}
        <Dialog open={!!selectedItem} onOpenChange={() => setSelectedItem(null)}>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            {selectedItem && (
              <>
                <DialogHeader>
                  <DialogTitle className="flex items-center justify-between">
                    <span>Review Incident: {selectedItem.incident_id}</span>
                    <div className="flex gap-2">
                      <Badge variant="outline" className={getPriorityBadge(selectedItem.priority)}>
                        {selectedItem.priority.toUpperCase()}
                      </Badge>
                    </div>
                  </DialogTitle>
                </DialogHeader>

                <div className="space-y-6">
                  {/* Review Reasons */}
                  <div className="rounded-lg bg-warning/10 border border-warning/30 p-4">
                    <h4 className="font-medium mb-2 flex items-center gap-2">
                      <Shield className="h-4 w-4" />
                      Why Human Review is Required
                    </h4>
                    <p className="text-sm mb-3">{selectedItem.explanation}</p>
                    <div className="flex flex-wrap gap-2">
                      {selectedItem.reasons.map((reason, index) => (
                        <Badge key={index} variant="outline" className="text-xs">
                          {getReasonIcon(reason)}
                          <span className="ml-1">{reason.replace('_', ' ')}</span>
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {/* Incident Details */}
                  <div className="grid gap-4 sm:grid-cols-3">
                    <div className="flex items-center gap-2 text-sm">
                      <FileText className="h-4 w-4 text-muted-foreground" />
                      <span className="text-muted-foreground">Type:</span>
                      <span className="font-medium">{selectedItem.incident_data.incident_type}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                      <span className="text-muted-foreground">Severity:</span>
                      <span className="font-medium">{selectedItem.incident_data.severity}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <User className="h-4 w-4 text-muted-foreground" />
                      <span className="text-muted-foreground">Reporter:</span>
                      <span className="font-medium">
                        {selectedItem.incident_data.reporter_info?.anonymous 
                          ? `Anonymous (${selectedItem.incident_data.reporter_info.pseudonymous_id})`
                          : selectedItem.incident_data.reporter_info?.name || 'Unknown'
                        }
                      </span>
                    </div>
                  </div>

                  {/* Incident Description */}
                  <div className="rounded-lg bg-muted/30 p-4">
                    <h4 className="text-sm font-medium mb-2">Incident Description</h4>
                    <p className="text-sm text-muted-foreground">
                      {selectedItem.incident_data.description}
                    </p>
                  </div>

                  {/* File Analyses */}
                  {selectedItem.file_analyses && selectedItem.file_analyses.length > 0 && (
                    <div className="space-y-4">
                      <h4 className="text-sm font-medium">File Authenticity Analysis</h4>
                      {selectedItem.file_analyses.map((analysis, index) => (
                        <div key={index} className={`rounded-lg p-4 border ${
                          analysis.requires_human_review 
                            ? 'bg-destructive/10 border-destructive/30' 
                            : 'bg-success/10 border-success/30'
                        }`}>
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-medium">{analysis.filename}</span>
                            <Badge variant="outline" className={
                              analysis.requires_human_review ? 'text-destructive' : 'text-success'
                            }>
                              {analysis.authenticity_status}
                            </Badge>
                          </div>
                          <p className="text-sm mb-2">{analysis.summary}</p>
                          {analysis.risk_factors && analysis.risk_factors.length > 0 && (
                            <div>
                              <span className="text-xs font-medium">Risk Factors:</span>
                              <ul className="text-xs mt-1 space-y-1">
                                {analysis.risk_factors.map((factor: string, i: number) => (
                                  <li key={i} className="flex items-start gap-1">
                                    <span className="text-destructive">•</span>
                                    <span>{factor}</span>
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Review Actions */}
                  <div className="space-y-4 border-t pt-4">
                    <h4 className="font-medium">Review Decision</h4>
                    
                    <div className="space-y-2">
                      <Label htmlFor="review-action">Action</Label>
                      <Select value={reviewAction} onValueChange={setReviewAction}>
                        <SelectTrigger>
                          <SelectValue placeholder="Select review action" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="approve_and_continue">
                            ✅ Approve and Allow AI Processing
                          </SelectItem>
                          <SelectItem value="approve_with_conditions">
                            ⚠️ Approve with Conditions
                          </SelectItem>
                          <SelectItem value="request_more_info">
                            📋 Request Additional Information
                          </SelectItem>
                          <SelectItem value="mark_invalid">
                            ❌ Mark as Invalid Report
                          </SelectItem>
                          <SelectItem value="escalate_to_admin">
                            🔺 Escalate to Administrator
                          </SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="review-notes">Review Notes (Required)</Label>
                      <Textarea
                        id="review-notes"
                        value={reviewNotes}
                        onChange={(e) => setReviewNotes(e.target.value)}
                        placeholder="Provide detailed notes about your review decision..."
                        rows={4}
                        className="resize-none"
                      />
                    </div>

                    <div className="flex justify-end gap-3 pt-4">
                      <Button
                        variant="outline"
                        onClick={() => setSelectedItem(null)}
                      >
                        Cancel
                      </Button>
                      <Button
                        onClick={handleCompleteReview}
                        disabled={!reviewAction || !reviewNotes.trim()}
                        className="min-w-[140px]"
                      >
                        Complete Review
                      </Button>
                    </div>
                  </div>
                </div>
              </>
            )}
          </DialogContent>
        </Dialog>
      </div>
    </MainLayout>
  );
}