import { MainLayout } from "@/components/layout/MainLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { PolicyComplianceStatus } from "@/components/dashboard/PolicyComplianceStatus";
import { useState, useEffect } from "react";
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import {
  TrendingUp,
  CheckCircle,
  AlertTriangle,
  Lightbulb,
  Shield,
  Target,
  Clock,
  Users,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
  Activity,
} from "lucide-react";

// Types for analytics data
interface AnalyticsData {
  overall_score: number;
  trend: number;
  performance_metrics: Array<{
    subject: string;
    score: number;
    fullMark: number;
  }>;
  strengths: Array<{
    label: string;
    score: number;
  }>;
  improvements: Array<{
    label: string;
    priority: string;
    description: string;
  }>;
  lessons_learned: Array<{
    title: string;
    insight: string;
    impact: string;
  }>;
  total_incidents: number;
  total_evaluations: number;
  last_updated: string;
}

interface TrendsData {
  incident_types: Record<string, number>;
  severity_distribution: Record<string, number>;
  location_hotspots: Record<string, number>;
  day_of_week: Record<string, number>;
  anonymous_reporting_rate: number;
  total_incidents: number;
  period: string;
}

interface PolicyData {
  compliance_rate: number;
  items: Array<{
    label: string;
    status: boolean;
    description: string;
  }>;
  total_incidents: number;
  resolved_incidents: number;
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

export default function AIInsights() {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const [trendsData, setTrendsData] = useState<TrendsData | null>(null);
  const [policyData, setPolicyData] = useState<PolicyData | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());

  const fetchAnalyticsData = async () => {
    try {
      setLoading(true);
      
      // Fetch analytics overview
      const analyticsResponse = await fetch('/api/analytics/overview');
      if (analyticsResponse.ok) {
        const analytics = await analyticsResponse.json();
        setAnalyticsData(analytics);
      }

      // Fetch trends data
      const trendsResponse = await fetch('/api/analytics/trends');
      if (trendsResponse.ok) {
        const trends = await trendsResponse.json();
        setTrendsData(trends);
      }

      // Fetch policy compliance
      const policyResponse = await fetch('/api/analytics/policies');
      if (policyResponse.ok) {
        const policy = await policyResponse.json();
        setPolicyData(policy);
      }

      setLastRefresh(new Date());
    } catch (error) {
      console.error('Error fetching analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalyticsData();
    
    // Set up auto-refresh every 30 seconds
    const interval = setInterval(fetchAnalyticsData, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleRefresh = () => {
    fetchAnalyticsData();
  };

  if (loading && !analyticsData) {
    return (
      <MainLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <Activity className="h-8 w-8 animate-spin mx-auto mb-4 text-primary" />
            <p className="text-muted-foreground">Loading AI insights...</p>
          </div>
        </div>
      </MainLayout>
    );
  }

  // Prepare chart data
  const incidentTypesChart = trendsData ? Object.entries(trendsData.incident_types).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value
  })) : [];

  const severityChart = trendsData ? Object.entries(trendsData.severity_distribution).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value
  })) : [];

  const dayOfWeekChart = trendsData ? Object.entries(trendsData.day_of_week).map(([name, value]) => ({
    day: name.substring(0, 3),
    incidents: value
  })) : [];

  return (
    <MainLayout>
      <div className="space-y-6 animate-fade-in">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">AI Insights & Evaluation</h1>
            <p className="text-muted-foreground">
              Real-time performance analysis and recommendations based on recent trends
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">
              Last updated: {lastRefresh.toLocaleTimeString()}
            </span>
            <button
              onClick={handleRefresh}
              disabled={loading}
              className="p-2 rounded-lg border border-border hover:bg-muted/50 transition-colors"
            >
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
          </div>
        </div>

        {/* Real-time Stats */}
        <div className="grid gap-4 md:grid-cols-4">
          <Card className="glass-card border-0">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Incidents</p>
                  <p className="text-2xl font-bold">{analyticsData?.total_incidents || 0}</p>
                </div>
                <Activity className="h-8 w-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="glass-card border-0">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Evaluations</p>
                  <p className="text-2xl font-bold">{analyticsData?.total_evaluations || 0}</p>
                </div>
                <Target className="h-8 w-8 text-green-500" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="glass-card border-0">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Anonymous Rate</p>
                  <p className="text-2xl font-bold">{trendsData?.anonymous_reporting_rate.toFixed(1) || 0}%</p>
                </div>
                <Shield className="h-8 w-8 text-purple-500" />
              </div>
            </CardContent>
          </Card>
          
          <Card className="glass-card border-0">
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Compliance</p>
                  <p className="text-2xl font-bold">{policyData?.compliance_rate.toFixed(1) || 0}%</p>
                </div>
                <CheckCircle className="h-8 w-8 text-orange-500" />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Overall Score */}
        <div className="grid gap-6 lg:grid-cols-3">
          <Card className="glass-card border-0 lg:col-span-1">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5 text-primary" />
                Overall Quality Score
              </CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col items-center">
              <div className="relative mb-6">
                <svg width="180" height="180" className="transform -rotate-90">
                  <circle
                    cx="90"
                    cy="90"
                    r="70"
                    stroke="hsl(var(--muted))"
                    strokeWidth="12"
                    fill="none"
                  />
                  <circle
                    cx="90"
                    cy="90"
                    r="70"
                    stroke="url(#insightGradient)"
                    strokeWidth="12"
                    fill="none"
                    strokeDasharray={2 * Math.PI * 70}
                    strokeDashoffset={(1 - (analyticsData?.overall_score || 75) / 100) * 2 * Math.PI * 70}
                    strokeLinecap="round"
                    className="transition-all duration-1000 ease-out"
                  />
                  <defs>
                    <linearGradient id="insightGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                      <stop offset="0%" stopColor="hsl(var(--primary))" />
                      <stop offset="100%" stopColor="hsl(var(--accent))" />
                    </linearGradient>
                  </defs>
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-4xl font-bold">{analyticsData?.overall_score.toFixed(1) || '75.0'}</span>
                  <span className="text-sm text-muted-foreground">out of 100</span>
                </div>
              </div>
              <div className="flex items-center gap-2 text-sm">
                {(analyticsData?.trend || 0) >= 0 ? (
                  <ArrowUpRight className="h-4 w-4 text-success" />
                ) : (
                  <ArrowDownRight className="h-4 w-4 text-destructive" />
                )}
                <span className={`font-medium ${(analyticsData?.trend || 0) >= 0 ? 'text-success' : 'text-destructive'}`}>
                  {analyticsData?.trend >= 0 ? '+' : ''}{analyticsData?.trend.toFixed(1) || '0.0'}%
                </span>
                <span className="text-muted-foreground">vs last week</span>
              </div>
            </CardContent>
          </Card>

          {/* Radar Chart */}
          <Card className="glass-card border-0 lg:col-span-2">
            <CardHeader>
              <CardTitle>Performance Metrics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="h-[280px]">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={analyticsData?.performance_metrics || []}>
                    <PolarGrid stroke="hsl(var(--border))" />
                    <PolarAngleAxis
                      dataKey="subject"
                      tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }}
                    />
                    <PolarRadiusAxis
                      angle={30}
                      domain={[0, 100]}
                      tick={{ fontSize: 10, fill: "hsl(var(--muted-foreground))" }}
                    />
                    <Radar
                      name="Performance"
                      dataKey="score"
                      stroke="hsl(var(--primary))"
                      fill="hsl(var(--primary))"
                      fillOpacity={0.3}
                      strokeWidth={2}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Trends Analysis */}
        <Tabs defaultValue="trends" className="space-y-4">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="trends">Incident Trends</TabsTrigger>
            <TabsTrigger value="performance">Performance</TabsTrigger>
            <TabsTrigger value="insights">AI Insights</TabsTrigger>
          </TabsList>

          <TabsContent value="trends" className="space-y-4">
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
              {/* Incident Types */}
              <Card className="glass-card border-0">
                <CardHeader>
                  <CardTitle className="text-base">Incident Types</CardTitle>
                  <p className="text-sm text-muted-foreground">{trendsData?.period || 'Recent trends'}</p>
                </CardHeader>
                <CardContent>
                  <div className="h-[200px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={incidentTypesChart}
                          cx="50%"
                          cy="50%"
                          innerRadius={40}
                          outerRadius={80}
                          paddingAngle={5}
                          dataKey="value"
                        >
                          {incidentTypesChart.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip />
                      </PieChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="mt-4 space-y-2">
                    {incidentTypesChart.slice(0, 3).map((item, index) => (
                      <div key={item.name} className="flex items-center justify-between text-sm">
                        <div className="flex items-center gap-2">
                          <div 
                            className="w-3 h-3 rounded-full" 
                            style={{ backgroundColor: COLORS[index % COLORS.length] }}
                          />
                          <span>{item.name}</span>
                        </div>
                        <span className="font-medium">{item.value}</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Severity Distribution */}
              <Card className="glass-card border-0">
                <CardHeader>
                  <CardTitle className="text-base">Severity Levels</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {severityChart.map((item, index) => (
                      <div key={item.name} className="space-y-2">
                        <div className="flex items-center justify-between text-sm">
                          <span className="capitalize">{item.name}</span>
                          <span className="font-medium">{item.value}</span>
                        </div>
                        <Progress 
                          value={(item.value / Math.max(...severityChart.map(s => s.value))) * 100} 
                          className="h-2" 
                        />
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              {/* Day of Week Pattern */}
              <Card className="glass-card border-0">
                <CardHeader>
                  <CardTitle className="text-base">Weekly Pattern</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-[200px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={dayOfWeekChart}>
                        <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" />
                        <XAxis 
                          dataKey="day" 
                          tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }}
                        />
                        <YAxis 
                          tick={{ fontSize: 12, fill: "hsl(var(--muted-foreground))" }}
                        />
                        <Tooltip 
                          contentStyle={{
                            backgroundColor: 'hsl(var(--background))',
                            border: '1px solid hsl(var(--border))',
                            borderRadius: '8px'
                          }}
                        />
                        <Bar dataKey="incidents" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="performance" className="space-y-4">

        {/* Strengths & Improvements */}
        <div className="grid gap-6 md:grid-cols-2">
          {/* Strengths */}
          <Card className="glass-card border-0">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-success">
                <TrendingUp className="h-5 w-5" />
                Identified Strengths
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {(analyticsData?.strengths || []).map((strength, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span>{strength.label}</span>
                    <span className="font-medium text-success">{strength.score}%</span>
                  </div>
                  <Progress value={strength.score} className="h-2" />
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Improvements */}
          <Card className="glass-card border-0">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-warning">
                <Lightbulb className="h-5 w-5" />
                Areas for Improvement
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {(analyticsData?.improvements || []).map((item, index) => (
                <div
                  key={index}
                  className="rounded-lg bg-muted/30 p-3 transition-all duration-200 hover:bg-muted/50"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-medium text-sm">{item.label}</span>
                    <Badge
                      variant="outline"
                      className={
                        item.priority === "high"
                          ? "bg-destructive/10 text-destructive border-destructive/30"
                          : item.priority === "medium"
                          ? "bg-warning/10 text-warning border-warning/30"
                          : "bg-muted text-muted-foreground"
                      }
                    >
                      {item.priority}
                    </Badge>
                  </div>
                  <p className="text-xs text-muted-foreground">{item.description}</p>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>

          </TabsContent>

          <TabsContent value="insights" className="space-y-4">
            {/* Lessons Learned */}
            <Card className="glass-card border-0">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Lightbulb className="h-5 w-5 text-accent" />
                  AI-Generated Insights
                </CardTitle>
                <p className="text-sm text-muted-foreground">
                  Based on analysis of {analyticsData?.total_incidents || 0} recent incidents
                </p>
              </CardHeader>
              <CardContent className="space-y-4">
                {(analyticsData?.lessons_learned || []).map((lesson, index) => (
                  <div
                    key={index}
                    className="rounded-lg border border-border/50 p-4 transition-all duration-200 hover:border-primary/30 hover:shadow-glow"
                  >
                    <h4 className="font-medium text-sm mb-1">{lesson.title}</h4>
                    <p className="text-xs text-muted-foreground mb-2">{lesson.insight}</p>
                    <Badge className="bg-accent/10 text-accent border-accent/30">
                      {lesson.impact}
                    </Badge>
                  </div>
                ))}
                
                {(!analyticsData?.lessons_learned || analyticsData.lessons_learned.length === 0) && (
                  <div className="text-center py-8 text-muted-foreground">
                    <Lightbulb className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p className="text-sm">No insights available yet</p>
                    <p className="text-xs">Process more incidents to generate AI insights</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Policy Compliance */}
        <Card className="glass-card border-0">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-primary" />
              Policy Compliance Status
            </CardTitle>
            <p className="text-sm text-muted-foreground">
              Real-time compliance monitoring based on recent incidents
            </p>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {(policyData?.items || []).map((item, index) => (
                <div
                  key={index}
                  className={`rounded-lg border p-4 transition-all duration-200 ${
                    item.status
                      ? 'border-success/30 bg-success/5'
                      : 'border-destructive/30 bg-destructive/5'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    {item.status ? (
                      <CheckCircle className="h-4 w-4 text-success" />
                    ) : (
                      <AlertTriangle className="h-4 w-4 text-destructive" />
                    )}
                    <span className="font-medium text-sm">{item.label}</span>
                  </div>
                  <p className="text-xs text-muted-foreground">{item.description}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Footer */}
        <footer className="mt-8 border-t border-border pt-6 text-center">
          <p className="text-sm text-muted-foreground">
            Built with <span className="text-primary font-medium">Agentic AI</span> for Campus Safety
          </p>
        </footer>
      </div>
    </MainLayout>
  );
}
