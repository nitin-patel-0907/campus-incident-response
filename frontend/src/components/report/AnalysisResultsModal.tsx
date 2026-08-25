import { useState, useEffect } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Separator } from "@/components/ui/separator";
import {
  CheckCircle,
  AlertTriangle,
  Clock,
  Users,
  Target,
  TrendingUp,
  Lightbulb,
  Shield,
  Activity,
  Download,
  X,
} from "lucide-react";
import { WorkflowResult } from "@/lib/api";

interface AnalysisResultsModalProps {
  isOpen: boolean;
  onClose: () => void;
  result: WorkflowResult | null;
  isLoading: boolean;
}

export function AnalysisResultsModal({
  isOpen,
  onClose,
  result,
  isLoading,
}: AnalysisResultsModalProps) {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (isLoading) {
      const interval = setInterval(() => {
        setProgress((prev) => {
          if (prev >= 90) return prev;
          return prev + Math.random() * 10;
        });
      }, 500);

      return () => clearInterval(interval);
    } else if (result) {
      setProgress(100);
    }
  }, [isLoading, result]);

  const getSeverityColor = (severity: string) => {
    switch (severity?.toLowerCase()) {
      case 'critical':
        return 'bg-red-500';
      case 'high':
        return 'bg-orange-500';
      case 'medium':
        return 'bg-yellow-500';
      case 'low':
        return 'bg-green-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'error':
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      default:
        return <Activity className="h-4 w-4 text-blue-500" />;
    }
  };

  if (isLoading) {
    return (
      <Dialog open={isOpen} onOpenChange={onClose}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 animate-pulse text-blue-500" />
              Processing Incident Report
            </DialogTitle>
          </DialogHeader>
          
          <div className="space-y-6 py-4">
            <div className="text-center">
              <div className="mx-auto mb-4 h-16 w-16 animate-pulse rounded-full bg-blue-100 flex items-center justify-center">
                <Activity className="h-8 w-8 text-blue-500" />
              </div>
              <h3 className="text-lg font-semibold mb-2">AI Agents Analyzing Your Report</h3>
              <p className="text-muted-foreground">
                Our multi-agent system is processing your incident through specialized analysis nodes
              </p>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span>Analysis Progress</span>
                <span>{Math.round(progress)}%</span>
              </div>
              <Progress value={progress} className="h-2" />
            </div>

            <div className="grid gap-3">
              <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                <div className="h-2 w-2 rounded-full bg-blue-500 animate-pulse" />
                <span className="text-sm">Intake Agent: Processing incident details...</span>
              </div>
              <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                <div className="h-2 w-2 rounded-full bg-purple-500 animate-pulse" />
                <span className="text-sm">Planner Agent: Generating response plan...</span>
              </div>
              <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                <div className="h-2 w-2 rounded-full bg-green-500 animate-pulse" />
                <span className="text-sm">Safety Agent: Validating compliance...</span>
              </div>
              <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                <div className="h-2 w-2 rounded-full bg-orange-500 animate-pulse" />
                <span className="text-sm">Executor Agent: Coordinating response...</span>
              </div>
              <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                <div className="h-2 w-2 rounded-full bg-yellow-500 animate-pulse" />
                <span className="text-sm">Evaluator Agent: Assessing effectiveness...</span>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    );
  }

  if (!result) return null;

  // Handle spam detection responses that don't have a result property
  if (result.status === "spam_detected" || result.error_type === "spam_detected") {
    // This should not happen as spam reports should not set analysisResult
    // But add safety check to prevent errors
    console.warn("AnalysisResultsModal received spam detection result - this should not happen");
    return null;
  }

  // Ensure result has the expected structure
  if (!result.result) {
    console.warn("AnalysisResultsModal received result without result property");
    return null;
  }

  // Safely destructure with fallbacks
  const resultData = result.result || {};
  const { incident_data, response_plan, execution_summary, evaluation_report } = resultData;

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-green-500" />
            Incident Analysis Complete
          </DialogTitle>
        </DialogHeader>

        <Tabs defaultValue="overview" className="space-y-4">
          <TabsList className="grid w-full grid-cols-6">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="analysis">Analysis</TabsTrigger>
            <TabsTrigger value="response">Response Plan</TabsTrigger>
            <TabsTrigger value="execution">Execution</TabsTrigger>
            <TabsTrigger value="evaluation">Evaluation</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-4">
            <div className="grid gap-4 md:grid-cols-1">
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">Incident Summary</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {incident_data ? (
                    <>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Type</span>
                        <Badge variant="outline" className="capitalize">
                          {incident_data.incident_type || 'Unknown'}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Severity</span>
                        <Badge className={`${getSeverityColor(incident_data.severity)} text-white`}>
                          {incident_data.severity || 'Unknown'}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Priority</span>
                        <Badge variant="secondary" className="capitalize">
                          {incident_data.priority || 'Unknown'}
                        </Badge>
                      </div>
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-muted-foreground">Confidence</span>
                        <span className="text-sm font-medium">
                          {incident_data.confidence_score?.toFixed(1) || '0.0'}%
                        </span>
                      </div>
                    </>
                  ) : (
                    <div className="text-center py-4 text-muted-foreground">
                      <p className="text-sm">Incident data not available</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>

            {evaluation_report ? (
              <>
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center gap-2">
                      <TrendingUp className="h-4 w-4" />
                      Overall Assessment
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="text-lg font-semibold">Effectiveness Score</span>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-green-600">
                            {evaluation_report.overall_score || 0}/100
                          </div>
                          <div className="text-sm text-muted-foreground">
                            {evaluation_report.effectiveness_rating || 'Not Available'}
                          </div>
                        </div>
                      </div>
                      <Progress value={evaluation_report.overall_score || 0} className="h-2" />
                      <p className="text-sm text-muted-foreground">
                        {evaluation_report.response_quality || 'No assessment available'}
                      </p>
                    </div>
                  </CardContent>
                </Card>

                {/* Resolution Status */}
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-base flex items-center gap-2">
                      <Shield className="h-4 w-4" />
                      Resolution Status
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div className="flex items-center justify-between">
                        <span className="font-medium">Status</span>
                        <Badge 
                          variant={
                            evaluation_report.resolution_status === 'resolved' 
                              ? 'default' 
                              : evaluation_report.resolution_status === 'under_review'
                              ? 'secondary'
                              : 'destructive'
                          }
                          className="capitalize"
                        >
                          {evaluation_report.resolution_status?.replace('_', ' ') || 'Unresolved'}
                        </Badge>
                      </div>
                      
                      {evaluation_report.resolution_reason && (
                        <div className="p-3 bg-muted/30 rounded-lg">
                          <p className="text-sm font-medium mb-1">Reason</p>
                          <p className="text-sm text-muted-foreground">
                            {evaluation_report.resolution_reason}
                          </p>
                        </div>
                      )}
                      
                      {evaluation_report.human_intervention_required && (
                        <div className="flex items-center gap-2 p-3 bg-yellow-50 dark:bg-yellow-950/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                          <AlertTriangle className="h-4 w-4 text-yellow-600" />
                          <div>
                            <p className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                              Human Review Required
                            </p>
                            <p className="text-xs text-yellow-700 dark:text-yellow-300">
                              This incident requires human verification before final resolution
                            </p>
                          </div>
                        </div>
                      )}
                      
                      {evaluation_report.resolution_details && (
                        <div className="p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg border border-blue-200 dark:border-blue-800">
                          <p className="text-sm font-medium text-blue-800 dark:text-blue-200 mb-1">
                            Additional Details
                          </p>
                          <p className="text-xs text-blue-700 dark:text-blue-300">
                            {evaluation_report.resolution_details}
                          </p>
                        </div>
                      )}
                      
                      {evaluation_report.rule_applied && (
                        <div className="text-xs text-muted-foreground">
                          Resolution determined by: {evaluation_report.rule_applied.replace(/_/g, ' ')}
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </>
            ) : (
              <Card>
                <CardContent className="text-center py-8">
                  <TrendingUp className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No Evaluation Available</h3>
                  <p className="text-muted-foreground">
                    Evaluation report was not generated for this incident.
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Analysis Tab */}
          <TabsContent value="analysis" className="space-y-4">
            {incident_data && (
              <>
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Target className="h-4 w-4" />
                      Incident Analysis
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <h4 className="font-medium mb-2">Description</h4>
                      <p className="text-sm text-muted-foreground">
                        {incident_data.description}
                      </p>
                    </div>
                    
                    <Separator />
                    
                    <div>
                      <h4 className="font-medium mb-2">Location</h4>
                      <p className="text-sm text-muted-foreground">
                        {incident_data.location}
                      </p>
                    </div>

                    {incident_data.entities && (
                      <>
                        <Separator />
                        <div>
                          <h4 className="font-medium mb-2">Extracted Entities</h4>
                          <div className="grid gap-3 sm:grid-cols-2">
                            {Object.entries(incident_data.entities).map(([type, items]) => (
                              items.length > 0 && (
                                <div key={type}>
                                  <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide">
                                    {type}
                                  </span>
                                  <div className="flex flex-wrap gap-1 mt-1">
                                    {items.map((item, index) => (
                                      <Badge key={index} variant="outline" className="text-xs">
                                        {item}
                                      </Badge>
                                    ))}
                                  </div>
                                </div>
                              )
                            ))}
                          </div>
                        </div>
                      </>
                    )}
                  </CardContent>
                </Card>
              </>
            )}
          </TabsContent>

          {/* Response Plan Tab */}
          <TabsContent value="response" className="space-y-4">
            {response_plan && (
              <>
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Shield className="h-4 w-4" />
                      Response Plan
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid gap-4 sm:grid-cols-2">
                      <div>
                        <span className="text-sm text-muted-foreground">Plan Type</span>
                        <p className="font-medium capitalize">{response_plan.plan_type.replace('_', ' ')}</p>
                      </div>
                      <div>
                        <span className="text-sm text-muted-foreground">Priority Level</span>
                        <Badge className={`${getSeverityColor(response_plan.priority_level)} text-white`}>
                          {response_plan.priority_level}
                        </Badge>
                      </div>
                    </div>

                    <Separator />

                    <div>
                      <h4 className="font-medium mb-3 flex items-center gap-2">
                        <Clock className="h-4 w-4" />
                        Immediate Actions ({response_plan.immediate_actions?.length || 0})
                      </h4>
                      <div className="space-y-2">
                        {response_plan.immediate_actions?.slice(0, 3).map((action, index) => (
                          <div key={index} className="p-3 rounded-lg bg-muted/50">
                            <div className="flex items-start justify-between gap-2">
                              <p className="text-sm flex-1">{action.description}</p>
                              <Badge variant="outline" className="text-xs">
                                {action.priority}
                              </Badge>
                            </div>
                            <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                              <span>👤 {action.responsible_party}</span>
                              <span>⏱️ {action.estimated_duration}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>

                    <Separator />

                    <div>
                      <h4 className="font-medium mb-3 flex items-center gap-2">
                        <Users className="h-4 w-4" />
                        Key Stakeholders
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {response_plan.stakeholders?.slice(0, 6).map((stakeholder, index) => (
                          <Badge key={index} variant="secondary" className="text-xs">
                            {stakeholder.role}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </>
            )}
          </TabsContent>

          {/* Execution Tab */}
          <TabsContent value="execution" className="space-y-4">
            {execution_summary && (
              <>
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Activity className="h-4 w-4" />
                      Execution Summary
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid gap-4 sm:grid-cols-3">
                      <div className="text-center p-3 rounded-lg bg-muted/50">
                        <div className="text-2xl font-bold text-green-600">
                          {execution_summary.success_rate.toFixed(1)}%
                        </div>
                        <div className="text-xs text-muted-foreground">Success Rate</div>
                      </div>
                      <div className="text-center p-3 rounded-lg bg-muted/50">
                        <div className="text-2xl font-bold text-blue-600">
                          {execution_summary.immediate_actions_executed}
                        </div>
                        <div className="text-xs text-muted-foreground">Actions Executed</div>
                      </div>
                      <div className="text-center p-3 rounded-lg bg-muted/50">
                        <div className="text-2xl font-bold text-purple-600">
                          {execution_summary.stakeholder_response_rate.toFixed(1)}%
                        </div>
                        <div className="text-xs text-muted-foreground">Response Rate</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {/* Detailed Execution Steps */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <CheckCircle className="h-4 w-4" />
                      Execution Steps Taken
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {response_plan?.immediate_actions && response_plan.immediate_actions.length > 0 ? (
                      <div className="space-y-3">
                        {response_plan.immediate_actions.map((action, index) => (
                          <div key={index} className="flex items-start gap-3 p-3 rounded-lg border">
                            <div className="flex-shrink-0 mt-1">
                              <div className="h-6 w-6 rounded-full bg-green-100 text-green-600 flex items-center justify-center text-xs font-medium">
                                {index + 1}
                              </div>
                            </div>
                            <div className="flex-1 space-y-2">
                              <div className="flex items-start justify-between gap-2">
                                <h4 className="font-medium text-sm">{action.description}</h4>
                                <Badge variant="outline" className="text-xs">
                                  {action.priority}
                                </Badge>
                              </div>
                              <div className="grid gap-2 sm:grid-cols-2 text-xs text-muted-foreground">
                                <div className="flex items-center gap-1">
                                  <Users className="h-3 w-3" />
                                  <span>{action.responsible_party}</span>
                                </div>
                                <div className="flex items-center gap-1">
                                  <Clock className="h-3 w-3" />
                                  <span>{action.estimated_duration}</span>
                                </div>
                              </div>
                              <div className="flex items-center gap-2">
                                <CheckCircle className="h-3 w-3 text-green-500" />
                                <span className="text-xs text-green-600 font-medium">Executed Successfully</span>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-6 text-muted-foreground">
                        <Activity className="h-8 w-8 mx-auto mb-2 opacity-50" />
                        <p className="text-sm">No specific execution steps recorded</p>
                        <p className="text-xs">Standard incident processing workflow was followed</p>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Stakeholder Notifications */}
                {response_plan?.stakeholders && response_plan.stakeholders.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Users className="h-4 w-4" />
                        Stakeholder Notifications
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid gap-3 sm:grid-cols-2">
                        {response_plan.stakeholders.map((stakeholder, index) => (
                          <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                            <div>
                              <div className="font-medium text-sm">{stakeholder.role}</div>
                              <div className="text-xs text-muted-foreground">{stakeholder.contact_method}</div>
                            </div>
                            <div className="flex items-center gap-1">
                              <CheckCircle className="h-3 w-3 text-green-500" />
                              <span className="text-xs text-green-600">Notified</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Issues and Warnings */}
                {(execution_summary.critical_issues?.length > 0 || execution_summary.warnings?.length > 0) && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <AlertTriangle className="h-4 w-4" />
                        Issues & Warnings
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-4">
                      {execution_summary.critical_issues?.length > 0 && (
                        <div>
                          <h4 className="font-medium mb-2 text-red-600 flex items-center gap-2">
                            <AlertTriangle className="h-4 w-4" />
                            Critical Issues
                          </h4>
                          <ul className="space-y-2">
                            {execution_summary.critical_issues.map((issue, index) => (
                              <li key={index} className="flex items-start gap-2 p-2 rounded bg-red-50 dark:bg-red-950/20">
                                <AlertTriangle className="h-3 w-3 text-red-500 mt-0.5 flex-shrink-0" />
                                <span className="text-sm">{issue}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {execution_summary.warnings?.length > 0 && (
                        <div>
                          <h4 className="font-medium mb-2 text-yellow-600 flex items-center gap-2">
                            <AlertTriangle className="h-4 w-4" />
                            Warnings
                          </h4>
                          <ul className="space-y-2">
                            {execution_summary.warnings.map((warning, index) => (
                              <li key={index} className="flex items-start gap-2 p-2 rounded bg-yellow-50 dark:bg-yellow-950/20">
                                <AlertTriangle className="h-3 w-3 text-yellow-500 mt-0.5 flex-shrink-0" />
                                <span className="text-sm">{warning}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                )}
              </>
            )}

            {!execution_summary && (
              <Card>
                <CardContent className="text-center py-8">
                  <Activity className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No Execution Data Available</h3>
                  <p className="text-muted-foreground">
                    Execution summary was not generated for this incident.
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>

          {/* Evaluation Tab */}
          <TabsContent value="evaluation" className="space-y-4">
            {evaluation_report ? (
              <>
                {/* Simplified Overall Assessment */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="h-4 w-4" />
                      Response Evaluation
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="text-center p-6 rounded-lg bg-gradient-to-br from-green-50 to-green-100 dark:from-green-950/20 dark:to-green-900/20">
                      <div className="text-4xl font-bold text-green-600 mb-2">
                        {evaluation_report.overall_score.toFixed(1)}/100
                      </div>
                      <div className="text-lg font-medium text-green-700 dark:text-green-300 mb-1">
                        {evaluation_report.effectiveness_rating}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Overall Response Effectiveness
                      </div>
                    </div>
                    
                    <div className="p-4 bg-muted/30 rounded-lg">
                      <p className="text-sm text-muted-foreground text-center">{evaluation_report.response_quality}</p>
                    </div>
                  </CardContent>
                </Card>

                {/* Key Performance Metrics */}
                {evaluation_report.category_scores && evaluation_report.category_scores.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Target className="h-4 w-4" />
                        Key Performance Metrics
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="grid gap-4 md:grid-cols-3">
                        {evaluation_report.category_scores.map((category, index) => (
                          <div key={index} className="text-center p-4 rounded-lg bg-muted/50">
                            <div className="text-2xl font-bold mb-1" style={{
                              color: category.score >= 80 ? '#16a34a' : 
                                     category.score >= 60 ? '#ea580c' : '#dc2626'
                            }}>
                              {category.score.toFixed(1)}%
                            </div>
                            <div className="text-sm font-medium mb-2">{category.category}</div>
                            <Progress value={category.score} className="h-2" />
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Brief Insights */}
                <div className="grid gap-4 md:grid-cols-2">
                  {evaluation_report.strengths && evaluation_report.strengths.length > 0 && (
                    <Card>
                      <CardHeader className="pb-3">
                        <CardTitle className="text-base flex items-center gap-2">
                          <CheckCircle className="h-4 w-4 text-green-500" />
                          What Went Well
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ul className="space-y-2">
                          {evaluation_report.strengths.slice(0, 3).map((strength, index) => (
                            <li key={index} className="text-sm flex items-start gap-2">
                              <CheckCircle className="h-3 w-3 text-green-500 mt-0.5 flex-shrink-0" />
                              {strength}
                            </li>
                          ))}
                        </ul>
                      </CardContent>
                    </Card>
                  )}

                  {evaluation_report.weaknesses && evaluation_report.weaknesses.length > 0 && (
                    <Card>
                      <CardHeader className="pb-3">
                        <CardTitle className="text-base flex items-center gap-2">
                          <AlertTriangle className="h-4 w-4 text-yellow-500" />
                          Areas to Improve
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ul className="space-y-2">
                          {evaluation_report.weaknesses.slice(0, 3).map((weakness, index) => (
                            <li key={index} className="text-sm flex items-start gap-2">
                              <AlertTriangle className="h-3 w-3 text-yellow-500 mt-0.5 flex-shrink-0" />
                              {weakness}
                            </li>
                          ))}
                        </ul>
                      </CardContent>
                    </Card>
                  )}
                </div>

                {/* Key Insights */}
                {evaluation_report.lessons_learned && evaluation_report.lessons_learned.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Lightbulb className="h-4 w-4" />
                        Key Insights
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {evaluation_report.lessons_learned.slice(0, 2).map((lesson, index) => (
                          <div key={index} className="p-3 rounded-lg bg-muted/50 border">
                            <p className="text-sm font-medium mb-1">{lesson.lesson}</p>
                            <p className="text-xs text-muted-foreground">{lesson.impact}</p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Simple Recommendations */}
                {evaluation_report.improvement_recommendations && evaluation_report.improvement_recommendations.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Target className="h-4 w-4" />
                        Next Steps
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {evaluation_report.improvement_recommendations.slice(0, 2).map((rec, index) => (
                          <div key={index} className="p-3 rounded-lg bg-muted/50 border">
                            <div className="flex items-start justify-between gap-2 mb-1">
                              <span className="text-sm font-medium">{rec.title}</span>
                              <Badge variant={rec.priority === 'high' ? 'destructive' : 'default'} className="text-xs">
                                {rec.priority}
                              </Badge>
                            </div>
                            <p className="text-xs text-muted-foreground">{rec.expected_benefit}</p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </>
            ) : (
              <Card>
                <CardContent className="text-center py-8">
                  <TrendingUp className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">No Evaluation Report Available</h3>
                  <p className="text-muted-foreground">
                    Evaluation report was not generated for this incident.
                  </p>
                </CardContent>
              </Card>
            )}
          </TabsContent>
        </Tabs>

        <div className="flex justify-between pt-4 border-t">
          <Button variant="outline" className="gap-2">
            <Download className="h-4 w-4" />
            Download Report
          </Button>
          <Button onClick={onClose}>
            Close Analysis
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}