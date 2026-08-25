import { useState, useEffect } from "react";
import { MainLayout } from "@/components/layout/MainLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { 
  TrendingUp, 
  TrendingDown, 
  Clock, 
  Users, 
  Shield, 
  AlertTriangle, 
  CheckCircle2, 
  XCircle,
  RefreshCw,
  Brain,
  Zap,
  Target,
  Activity
} from "lucide-react";
import { apiClient } from "@/lib/api";
import { useToast } from "@/hooks/use-toast";

export default function PerformanceInsights() {
  const [insights, setInsights] = useState<any>(null);
  const [spamPatterns, setSpamPatterns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [spamLoading, setSpamLoading] = useState(false);
  const [selectedPattern, setSelectedPattern] = useState<any>(null);
  const { toast } = useToast();

  // Load performance insights
  const loadInsights = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/analytics/performance-insights');
      const data = await response.json();
      
      if (data.success) {
        setInsights(data.insights);
      } else {
        throw new Error(data.error || "Failed to load insights");
      }
    } catch (error) {
      console.error("Error loading insights:", error);
      toast({
        title: "Error Loading Insights",
        description: error instanceof Error ? error.message : "Failed to load performance insights",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  // Load spam patterns
  const loadSpamPatterns = async () => {
    try {
      setSpamLoading(true);
      const response = await fetch('/api/v1/spam/patterns');
      const data = await response.json();
      
      if (data.success) {
        setSpamPatterns(data.patterns);
      } else {
        throw new Error(data.error || "Failed to load spam patterns");
      }
    } catch (error) {
      console.error("Error loading spam patterns:", error);
      toast({
        title: "Error Loading Spam Patterns",
        description: error instanceof Error ? error.message : "Failed to load spam patterns",
        variant: "destructive",
      });
    } finally {
      setSpamLoading(false);
    }
  };

  // Mark spam pattern as false positive
  const markFalsePositive = async (patternId: string) => {
    try {
      const response = await fetch(`/api/v1/spam/${patternId}/false-positive`, {
        method: 'POST'
      });
      const data = await response.json();
      
      if (data.success) {
        toast({
          title: "Marked as False Positive",
          description: `Pattern confidence reduced to ${safeToFixed((data.new_confidence || 0) * 100)}%`,
        });
        loadSpamPatterns(); // Reload patterns
      } else {
        throw new Error(data.error || "Failed to mark false positive");
      }
    } catch (error) {
      console.error("Error marking false positive:", error);
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to mark false positive",
        variant: "destructive",
      });
    }
  };

  useEffect(() => {
    loadInsights();
    loadSpamPatterns();
  }, []);

  const formatPercentage = (value: number | undefined | null) => {
    if (value === undefined || value === null || isNaN(value)) return "N/A";
    return `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;
  };

  const formatTime = (seconds: number | undefined | null) => {
    if (seconds === undefined || seconds === null || isNaN(seconds)) return "N/A";
    if (seconds < 60) return `${seconds.toFixed(1)}s`;
    if (seconds < 3600) return `${(seconds / 60).toFixed(1)}m`;
    return `${(seconds / 3600).toFixed(1)}h`;
  };

  const safeToFixed = (value: number | undefined | null, decimals: number = 1) => {
    if (value === undefined || value === null || isNaN(value)) return "N/A";
    return value.toFixed(decimals);
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="heading-2-professional">Performance Insights</h1>
            <p className="body-small-professional">
              AI vs Human performance analysis and spam detection statistics
            </p>
          </div>
          <Button
            onClick={() => {
              loadInsights();
              loadSpamPatterns();
            }}
            variant="outline"
            size="sm"
            className="btn-secondary-professional gap-2"
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="flex items-center gap-3">
              <RefreshCw className="h-5 w-5 animate-spin text-primary" />
              <span className="text-muted-foreground">Loading performance insights...</span>
            </div>
          </div>
        ) : (
          <Tabs defaultValue="performance" className="space-y-6">
            <TabsList className="grid w-full max-w-md grid-cols-3">
              <TabsTrigger value="performance" className="flex items-center gap-2">
                <Activity className="h-4 w-4" />
                Performance
              </TabsTrigger>
              <TabsTrigger value="learning" className="flex items-center gap-2">
                <Brain className="h-4 w-4" />
                Learning
              </TabsTrigger>
              <TabsTrigger value="spam" className="flex items-center gap-2">
                <Shield className="h-4 w-4" />
                Spam Detection
              </TabsTrigger>
            </TabsList>

            {/* Performance Analysis */}
            <TabsContent value="performance">
              {insights ? (
                <div className="grid gap-6">
                  {/* Performance Overview Cards */}
                  <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">AI Incidents</CardTitle>
                        <Brain className="h-4 w-4 text-blue-500" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{insights.ai_incidents || 0}</div>
                        <p className="text-xs text-muted-foreground">
                          Autonomous resolutions
                        </p>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Human Incidents</CardTitle>
                        <Users className="h-4 w-4 text-green-500" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{insights.human_incidents || 0}</div>
                        <p className="text-xs text-muted-foreground">
                          Manual resolutions
                        </p>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Time Saved</CardTitle>
                        <Clock className="h-4 w-4 text-orange-500" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">
                          {insights.ai_improvements?.time_saved_percentage 
                            ? formatPercentage(insights.ai_improvements.time_saved_percentage)
                            : "N/A"}
                        </div>
                        <p className="text-xs text-muted-foreground">
                          AI vs Human processing
                        </p>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Resources Saved</CardTitle>
                        <Target className="h-4 w-4 text-purple-500" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">
                          {insights.ai_improvements?.resources_saved_percentage 
                            ? formatPercentage(insights.ai_improvements.resources_saved_percentage)
                            : "N/A"}
                        </div>
                        <p className="text-xs text-muted-foreground">
                          Resource optimization
                        </p>
                      </CardContent>
                    </Card>
                  </div>

                  {/* Detailed Performance Comparison */}
                  {(insights.ai_performance || insights.human_performance) && (
                    <div className="grid gap-6 md:grid-cols-2">
                      {/* AI Performance */}
                      {insights.ai_performance && (
                        <Card>
                          <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                              <Brain className="h-5 w-5 text-blue-500" />
                              AI Performance
                            </CardTitle>
                          </CardHeader>
                          <CardContent className="space-y-4">
                            <div className="space-y-2">
                              <div className="flex justify-between text-sm">
                                <span>Average Processing Time</span>
                                <span className="font-medium">
                                  {formatTime(insights.ai_performance.average_processing_time)}
                                </span>
                              </div>
                              <div className="flex justify-between text-sm">
                                <span>Average Resources Used</span>
                                <span className="font-medium">
                                  {safeToFixed(insights.ai_performance?.average_resources_used)}
                                </span>
                              </div>
                              <div className="flex justify-between text-sm">
                                <span>Average Accuracy</span>
                                <span className="font-medium">
                                  {insights.ai_performance?.average_accuracy 
                                    ? `${safeToFixed(insights.ai_performance.average_accuracy * 100)}%`
                                    : "N/A"}
                                </span>
                              </div>
                              <div className="flex justify-between text-sm">
                                <span>Efficiency Score</span>
                                <span className="font-medium">
                                  {safeToFixed(insights.ai_performance?.efficiency_score)}
                                </span>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      )}

                      {/* Human Performance */}
                      {insights.human_performance && (
                        <Card>
                          <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                              <Users className="h-5 w-5 text-green-500" />
                              Human Performance
                            </CardTitle>
                          </CardHeader>
                          <CardContent className="space-y-4">
                            <div className="space-y-2">
                              <div className="flex justify-between text-sm">
                                <span>Average Processing Time</span>
                                <span className="font-medium">
                                  {formatTime(insights.human_performance.average_processing_time)}
                                </span>
                              </div>
                              <div className="flex justify-between text-sm">
                                <span>Average Resources Used</span>
                                <span className="font-medium">
                                  {safeToFixed(insights.human_performance?.average_resources_used)}
                                </span>
                              </div>
                              <div className="flex justify-between text-sm">
                                <span>Average Accuracy</span>
                                <span className="font-medium">
                                  {insights.human_performance?.average_accuracy 
                                    ? `${safeToFixed(insights.human_performance.average_accuracy * 100)}%`
                                    : "N/A"}
                                </span>
                              </div>
                              <div className="flex justify-between text-sm">
                                <span>Efficiency Score</span>
                                <span className="font-medium">
                                  {safeToFixed(insights.human_performance?.efficiency_score)}
                                </span>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      )}
                    </div>
                  )}

                  {/* Efficiency Gains */}
                  {insights.ai_improvements && (
                    <Card>
                      <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                          <Zap className="h-5 w-5 text-yellow-500" />
                          AI Efficiency Gains
                        </CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="grid gap-4 md:grid-cols-3">
                          <div className="text-center">
                            <div className="text-2xl font-bold text-green-600">
                              {formatPercentage(insights.ai_improvements.time_saved_percentage)}
                            </div>
                            <p className="text-sm text-muted-foreground">Time Saved</p>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-blue-600">
                              {formatPercentage(insights.ai_improvements.resources_saved_percentage)}
                            </div>
                            <p className="text-sm text-muted-foreground">Resources Saved</p>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-purple-600">
                              {insights.ai_improvements?.overall_efficiency_gain !== undefined
                                ? `${insights.ai_improvements.overall_efficiency_gain > 0 ? '+' : ''}${safeToFixed(insights.ai_improvements.overall_efficiency_gain)}`
                                : "N/A"}
                            </div>
                            <p className="text-sm text-muted-foreground">Efficiency Gain</p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  )}
                </div>
              ) : (
                <Card>
                  <CardContent className="flex flex-col items-center justify-center py-12">
                    <Activity className="h-12 w-12 text-muted-foreground mb-4" />
                    <h3 className="heading-4-professional mb-2">No Performance Data</h3>
                    <p className="body-small-professional text-center max-w-md">
                      No recent incidents available for performance analysis. Process some incidents to see AI vs Human performance comparisons.
                    </p>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            {/* Learning Progress */}
            <TabsContent value="learning">
              {insights?.learning_progress ? (
                <div className="grid gap-6">
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Brain className="h-5 w-5 text-blue-500" />
                        Learning Progress
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-6">
                      <div className="grid gap-4 md:grid-cols-2">
                        <div>
                          <div className="text-2xl font-bold">
                            {insights.learning_progress.total_incidents_learned}
                          </div>
                          <p className="text-sm text-muted-foreground">Total Incidents Learned</p>
                        </div>
                        <div>
                          <div className="text-2xl font-bold">
                            {safeToFixed(insights.learning_progress?.system_maturity)}%
                          </div>
                          <p className="text-sm text-muted-foreground">System Maturity</p>
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-sm font-medium">System Maturity</span>
                          <span className="text-sm text-muted-foreground">
                            {safeToFixed(insights.learning_progress?.system_maturity)}%
                          </span>
                        </div>
                        <Progress value={insights.learning_progress?.system_maturity || 0} className="h-2" />
                      </div>

                      <div className="flex items-center gap-2">
                        {insights.learning_progress.learning_trend === 'improving' ? (
                          <TrendingUp className="h-4 w-4 text-green-500" />
                        ) : insights.learning_progress.learning_trend === 'declining' ? (
                          <TrendingDown className="h-4 w-4 text-red-500" />
                        ) : (
                          <Activity className="h-4 w-4 text-blue-500" />
                        )}
                        <span className="text-sm">
                          Learning Trend: <span className="font-medium capitalize">
                            {insights.learning_progress.learning_trend}
                          </span>
                        </span>
                      </div>

                      {insights.learning_progress.confidence_improvement !== 0 && (
                        <div className="p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg">
                          <div className="flex items-center gap-2">
                            {insights.learning_progress.confidence_improvement > 0 ? (
                              <TrendingUp className="h-4 w-4 text-green-500" />
                            ) : (
                              <TrendingDown className="h-4 w-4 text-red-500" />
                            )}
                            <span className="text-sm font-medium">
                              Confidence Improvement: {formatPercentage(insights.learning_progress.confidence_improvement)}
                            </span>
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                </div>
              ) : (
                <Card>
                  <CardContent className="flex flex-col items-center justify-center py-12">
                    <Brain className="h-12 w-12 text-muted-foreground mb-4" />
                    <h3 className="heading-4-professional mb-2">Learning in Progress</h3>
                    <p className="body-small-professional text-center max-w-md">
                      The system is still learning. Process more incidents to see learning progress and improvements.
                    </p>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            {/* Spam Detection */}
            <TabsContent value="spam">
              <div className="grid gap-6">
                {/* Spam Statistics */}
                {insights?.spam_detection && (
                  <div className="grid gap-4 md:grid-cols-5">
                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Total Patterns</CardTitle>
                        <Shield className="h-4 w-4 text-blue-500" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{insights.spam_detection.total_spam_patterns}</div>
                        <p className="text-xs text-muted-foreground">
                          Learned patterns
                        </p>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Spam Detected</CardTitle>
                        <XCircle className="h-4 w-4 text-red-500" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{insights.spam_detection.total_spam_detected}</div>
                        <p className="text-xs text-muted-foreground">
                          Reports blocked
                        </p>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Gibberish Detected</CardTitle>
                        <AlertTriangle className="h-4 w-4 text-orange-500" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">
                          {spamPatterns.filter(p => p.reason?.includes('gibberish') || p.reason?.includes('Gibberish')).length}
                        </div>
                        <p className="text-xs text-muted-foreground">
                          Nonsensical text
                        </p>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">False Positives</CardTitle>
                        <AlertTriangle className="h-4 w-4 text-yellow-500" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">{insights.spam_detection.false_positives}</div>
                        <p className="text-xs text-muted-foreground">
                          Incorrect detections
                        </p>
                      </CardContent>
                    </Card>

                    <Card>
                      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                        <CardTitle className="text-sm font-medium">Accuracy</CardTitle>
                        <CheckCircle2 className="h-4 w-4 text-green-500" />
                      </CardHeader>
                      <CardContent>
                        <div className="text-2xl font-bold">
                          {safeToFixed(insights.spam_detection?.detection_accuracy)}%
                        </div>
                        <p className="text-xs text-muted-foreground">
                          Detection accuracy
                        </p>
                      </CardContent>
                    </Card>
                  </div>
                )}

                {/* Spam Patterns Table */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Shield className="h-5 w-5 text-red-500" />
                      Spam Patterns
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {spamLoading ? (
                      <div className="flex items-center justify-center py-8">
                        <RefreshCw className="h-5 w-5 animate-spin text-primary" />
                        <span className="ml-2 text-muted-foreground">Loading spam patterns...</span>
                      </div>
                    ) : spamPatterns.length > 0 ? (
                      <Table>
                        <TableHeader>
                          <TableRow>
                            <TableHead>Pattern ID</TableHead>
                            <TableHead>Type</TableHead>
                            <TableHead>Confidence</TableHead>
                            <TableHead>Detections</TableHead>
                            <TableHead>False Positives</TableHead>
                            <TableHead>Created</TableHead>
                            <TableHead>Actions</TableHead>
                          </TableRow>
                        </TableHeader>
                        <TableBody>
                          {spamPatterns.map((pattern) => (
                            <TableRow key={pattern.pattern_id}>
                              <TableCell className="font-mono text-xs">
                                {pattern.pattern_id.substring(0, 20)}...
                              </TableCell>
                              <TableCell>
                                <Badge 
                                  variant="outline"
                                  className={
                                    pattern.reason?.includes('gibberish') || pattern.reason?.includes('Gibberish') 
                                      ? "bg-orange-50 text-orange-700 border-orange-200" 
                                      : "bg-red-50 text-red-700 border-red-200"
                                  }
                                >
                                  {pattern.reason?.includes('gibberish') || pattern.reason?.includes('Gibberish') ? 'Gibberish' : 'Spam'}
                                </Badge>
                              </TableCell>
                              <TableCell>
                                <Badge 
                                  variant="outline"
                                  className={
                                    pattern.confidence > 0.8 ? "bg-red-50 text-red-700 border-red-200" :
                                    pattern.confidence > 0.5 ? "bg-yellow-50 text-yellow-700 border-yellow-200" :
                                    "bg-gray-50 text-gray-700 border-gray-200"
                                  }
                                >
                                  {safeToFixed((pattern.confidence || 0) * 100)}%
                                </Badge>
                              </TableCell>
                              <TableCell>{pattern.marked_spam_count}</TableCell>
                              <TableCell>{pattern.false_positive_count}</TableCell>
                              <TableCell className="text-xs text-muted-foreground">
                                {new Date(pattern.created_at).toLocaleDateString()}
                              </TableCell>
                              <TableCell>
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => markFalsePositive(pattern.pattern_id)}
                                  className="text-xs"
                                >
                                  Mark False Positive
                                </Button>
                              </TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    ) : (
                      <div className="text-center py-8">
                        <Shield className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                        <h3 className="heading-4-professional mb-2">No Spam Patterns</h3>
                        <p className="body-small-professional">
                          No spam patterns have been learned yet. Mark incidents as spam to start building detection patterns.
                        </p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          </Tabs>
        )}
      </div>
    </MainLayout>
  );
}