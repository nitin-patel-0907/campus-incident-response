import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadialBarChart,
  RadialBar,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import {
  Shield,
  CheckCircle,
  AlertTriangle,
  TrendingUp,
  FileText,
  Clock,
  Users,
  AlertCircle,
  RefreshCw,
  Download,
  Eye,
  ChevronRight,
} from "lucide-react";
import { apiClient } from "@/lib/api";

interface ComplianceData {
  overall_score: {
    overall_score: number;
    category_scores: {
      response_time: number;
      documentation: number;
      privacy: number;
      reporting: number;
      follow_up: number;
    };
    grade: string;
    status: string;
  };
  policy_checks: Array<{
    policy: string;
    description: string;
    status: string;
    score: number;
    details: string;
    last_audit: string;
    requirements_met: number;
    total_requirements: number;
  }>;
  compliance_trends: {
    monthly_scores: Array<{
      month: string;
      score: number;
    }>;
    improvement_rate: string;
    trend_direction: string;
    key_improvements: string[];
  };
  risk_assessment: {
    overall_risk: string;
    risk_score: number;
    risk_factors: Array<{
      factor: string;
      level: string;
      count: number;
      mitigation: string;
    }>;
    recommendations: string[];
  };
  audit_trail: Array<{
    timestamp: string;
    incident_id: string;
    action: string;
    compliance_status: string;
    details: string;
    automated: boolean;
    policies_checked: string[];
  }>;
}

const RISK_COLORS = {
  low: "hsl(var(--success))",
  medium: "hsl(var(--warning))",
  high: "hsl(var(--destructive))",
};

const STATUS_COLORS = {
  compliant: "hsl(var(--success))",
  warning: "hsl(var(--warning))",
  non_compliant: "hsl(var(--destructive))",
};

export function PolicyComplianceStatus() {
  const [complianceData, setComplianceData] = useState<ComplianceData | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<string>("");
  const [selectedPolicy, setSelectedPolicy] = useState<string | null>(null);

  const loadComplianceData = async () => {
    try {
      const response = await apiClient.getDashboardAnalytics();
      if (response.success && response.compliance) {
        setComplianceData(response.compliance);
        setLastUpdated(new Date().toLocaleTimeString());
      }
    } catch (error) {
      console.error("Error loading compliance data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadComplianceData();
    
    // Auto-refresh every 60 seconds (less frequent than charts)
    const interval = setInterval(loadComplianceData, 60000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Card className="glass-card border-0">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-primary" />
            Policy Compliance Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-64">
            <div className="flex items-center gap-2 text-muted-foreground">
              <RefreshCw className="h-4 w-4 animate-spin" />
              Loading compliance data...
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!complianceData) {
    return (
      <Card className="glass-card border-0">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-primary" />
            Policy Compliance Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-muted-foreground py-8">
            <p>No compliance data available</p>
            <p className="text-sm">Submit incidents to generate compliance reports</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const categoryData = Object.entries(complianceData.overall_score.category_scores).map(([key, value]) => ({
    name: key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase()),
    value,
    fill: value >= 95 ? RISK_COLORS.low : value >= 85 ? RISK_COLORS.medium : RISK_COLORS.high,
  }));

  const riskData = complianceData.risk_assessment.risk_factors.map(factor => ({
    name: factor.factor,
    value: factor.count,
    fill: RISK_COLORS[factor.level as keyof typeof RISK_COLORS],
  }));

  return (
    <Card className="glass-card border-0">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-primary" />
            Policy Compliance Status
          </CardTitle>
          <div className="flex items-center gap-2">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              {lastUpdated && <span>Updated: {lastUpdated}</span>}
            </div>
            <Button variant="outline" size="sm" className="gap-2">
              <Download className="h-4 w-4" />
              Export Report
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="overview" className="w-full">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="policies">Policies</TabsTrigger>
            <TabsTrigger value="trends">Trends</TabsTrigger>
            <TabsTrigger value="audit">Audit Trail</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            {/* Overall Score */}
            <div className="grid gap-6 md:grid-cols-2">
              <Card className="border border-border/50">
                <CardHeader>
                  <CardTitle className="text-lg">Overall Compliance Score</CardTitle>
                </CardHeader>
                <CardContent className="flex flex-col items-center">
                  <div className="relative mb-4">
                    <svg width="120" height="120" className="transform -rotate-90">
                      <circle
                        cx="60"
                        cy="60"
                        r="45"
                        stroke="hsl(var(--muted))"
                        strokeWidth="8"
                        fill="none"
                      />
                      <circle
                        cx="60"
                        cy="60"
                        r="45"
                        stroke={complianceData.overall_score.overall_score >= 95 ? RISK_COLORS.low : 
                               complianceData.overall_score.overall_score >= 85 ? RISK_COLORS.medium : RISK_COLORS.high}
                        strokeWidth="8"
                        fill="none"
                        strokeDasharray={2 * Math.PI * 45}
                        strokeDashoffset={(1 - complianceData.overall_score.overall_score / 100) * 2 * Math.PI * 45}
                        strokeLinecap="round"
                        className="transition-all duration-1000 ease-out"
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="text-2xl font-bold">
                        {Math.round(complianceData.overall_score.overall_score * 100) / 100}%
                      </span>
                      <Badge 
                        className={`mt-1 ${
                          complianceData.overall_score.status === 'excellent' ? 'bg-success/10 text-success border-success/30' :
                          complianceData.overall_score.status === 'very_good' ? 'bg-primary/10 text-primary border-primary/30' :
                          'bg-warning/10 text-warning border-warning/30'
                        }`}
                      >
                        Grade {complianceData.overall_score.grade}
                      </Badge>
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground text-center">
                    {complianceData.overall_score.status === 'excellent' ? 'Excellent compliance across all areas' :
                     complianceData.overall_score.status === 'very_good' ? 'Very good compliance with minor improvements needed' :
                     'Good compliance with some areas needing attention'}
                  </p>
                </CardContent>
              </Card>

              <Card className="border border-border/50">
                <CardHeader>
                  <CardTitle className="text-lg">Category Breakdown</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="h-[200px]">
                    <ResponsiveContainer width="100%" height="100%">
                      <RadialBarChart cx="50%" cy="50%" innerRadius="20%" outerRadius="80%" data={categoryData}>
                        <RadialBar dataKey="value" cornerRadius={10} fill="#8884d8" />
                        <Tooltip 
                          formatter={(value) => [`${value}%`, 'Score']}
                          contentStyle={{
                            backgroundColor: "hsl(var(--card))",
                            border: "1px solid hsl(var(--border))",
                            borderRadius: "8px",
                            color: "hsl(var(--foreground))",
                          }}
                        />
                      </RadialBarChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Risk Assessment */}
            <Card className="border border-border/50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <AlertTriangle className="h-5 w-5 text-warning" />
                  Risk Assessment
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-4 md:grid-cols-2">
                  <div>
                    <div className="flex items-center gap-2 mb-4">
                      <Badge 
                        className={`${
                          complianceData.risk_assessment.overall_risk === 'low' ? 'bg-success/10 text-success border-success/30' :
                          complianceData.risk_assessment.overall_risk === 'medium' ? 'bg-warning/10 text-warning border-warning/30' :
                          'bg-destructive/10 text-destructive border-destructive/30'
                        }`}
                      >
                        {complianceData.risk_assessment.overall_risk.toUpperCase()} RISK
                      </Badge>
                      <span className="text-sm text-muted-foreground">
                        Risk Score: {complianceData.risk_assessment.risk_score}/100
                      </span>
                    </div>
                    <div className="space-y-3">
                      {complianceData.risk_assessment.risk_factors.map((factor, index) => (
                        <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-muted/30">
                          <div>
                            <p className="font-medium text-sm">{factor.factor}</p>
                            <p className="text-xs text-muted-foreground">{factor.mitigation}</p>
                          </div>
                          <Badge 
                            variant="outline"
                            className={`${
                              factor.level === 'low' ? 'bg-success/10 text-success border-success/30' :
                              factor.level === 'medium' ? 'bg-warning/10 text-warning border-warning/30' :
                              'bg-destructive/10 text-destructive border-destructive/30'
                            }`}
                          >
                            {factor.level}
                          </Badge>
                        </div>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h4 className="font-medium mb-3">Recommendations</h4>
                    <div className="space-y-2">
                      {complianceData.risk_assessment.recommendations.map((rec, index) => (
                        <div key={index} className="flex items-start gap-2 p-2 rounded bg-muted/20">
                          <ChevronRight className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                          <span className="text-sm">{rec}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="policies" className="space-y-4">
            <div className="grid gap-4">
              {complianceData.policy_checks.map((policy, index) => (
                <Card 
                  key={index} 
                  className={`border transition-all duration-200 hover:shadow-glow cursor-pointer ${
                    selectedPolicy === policy.policy ? 'border-primary/50' : 'border-border/50'
                  }`}
                  onClick={() => setSelectedPolicy(selectedPolicy === policy.policy ? null : policy.policy)}
                >
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          {policy.status === 'compliant' ? (
                            <CheckCircle className="h-5 w-5 text-success" />
                          ) : policy.status === 'warning' ? (
                            <AlertTriangle className="h-5 w-5 text-warning" />
                          ) : (
                            <AlertCircle className="h-5 w-5 text-destructive" />
                          )}
                          <h3 className="font-medium">{policy.policy}</h3>
                          <Badge 
                            className={`${
                              policy.status === 'compliant' ? 'bg-success/10 text-success border-success/30' :
                              policy.status === 'warning' ? 'bg-warning/10 text-warning border-warning/30' :
                              'bg-destructive/10 text-destructive border-destructive/30'
                            }`}
                          >
                            {policy.score}%
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mb-3">{policy.description}</p>
                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <span>Requirements: {policy.requirements_met}/{policy.total_requirements}</span>
                          <span>Last Audit: {new Date(policy.last_audit).toLocaleDateString()}</span>
                        </div>
                        <Progress 
                          value={(policy.requirements_met / policy.total_requirements) * 100} 
                          className="h-2 mt-2" 
                        />
                      </div>
                      <ChevronRight className={`h-4 w-4 text-muted-foreground transition-transform ${
                        selectedPolicy === policy.policy ? 'rotate-90' : ''
                      }`} />
                    </div>
                    {selectedPolicy === policy.policy && (
                      <div className="mt-4 pt-4 border-t border-border/50">
                        <p className="text-sm">{policy.details}</p>
                        <div className="flex gap-2 mt-3">
                          <Button variant="outline" size="sm" className="gap-2">
                            <Eye className="h-4 w-4" />
                            View Details
                          </Button>
                          <Button variant="outline" size="sm" className="gap-2">
                            <FileText className="h-4 w-4" />
                            Audit Report
                          </Button>
                        </div>
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="trends" className="space-y-6">
            <Card className="border border-border/50">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-primary" />
                  Compliance Trends
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid gap-6 md:grid-cols-2">
                  <div>
                    <div className="h-[200px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={complianceData.compliance_trends.monthly_scores}>
                          <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                          <XAxis dataKey="month" className="text-xs" stroke="hsl(var(--muted-foreground))" />
                          <YAxis className="text-xs" stroke="hsl(var(--muted-foreground))" domain={[85, 100]} />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: "hsl(var(--card))",
                              border: "1px solid hsl(var(--border))",
                              borderRadius: "8px",
                              color: "hsl(var(--foreground))",
                            }}
                            formatter={(value) => [`${value}%`, 'Compliance Score']}
                          />
                          <Line
                            type="monotone"
                            dataKey="score"
                            stroke="hsl(var(--primary))"
                            strokeWidth={2}
                            dot={{ fill: "hsl(var(--primary))", strokeWidth: 2 }}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>
                  <div>
                    <div className="space-y-4">
                      <div className="flex items-center gap-2">
                        <TrendingUp className="h-4 w-4 text-success" />
                        <span className="text-sm font-medium">Improvement Rate: {complianceData.compliance_trends.improvement_rate}</span>
                      </div>
                      <div>
                        <h4 className="font-medium mb-2">Key Improvements</h4>
                        <div className="space-y-2">
                          {complianceData.compliance_trends.key_improvements.map((improvement, index) => (
                            <div key={index} className="flex items-center gap-2 text-sm">
                              <CheckCircle className="h-4 w-4 text-success flex-shrink-0" />
                              <span>{improvement}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="audit" className="space-y-4">
            <div className="space-y-3">
              {complianceData.audit_trail.map((entry, index) => (
                <Card key={index} className="border border-border/50">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <Badge 
                            className={`${
                              entry.compliance_status === 'Compliant' ? 'bg-success/10 text-success border-success/30' :
                              'bg-warning/10 text-warning border-warning/30'
                            }`}
                          >
                            {entry.compliance_status}
                          </Badge>
                          <span className="font-medium text-sm">{entry.action}</span>
                          {entry.automated && (
                            <Badge variant="outline" className="bg-primary/10 text-primary border-primary/30">
                              Automated
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground mb-2">{entry.details}</p>
                        <div className="flex items-center gap-4 text-xs text-muted-foreground">
                          <span>ID: {entry.incident_id}</span>
                          <span>Time: {new Date(entry.timestamp).toLocaleString()}</span>
                          <span>Policies: {entry.policies_checked?.join(', ') || 'N/A'}</span>
                        </div>
                      </div>
                      <Clock className="h-4 w-4 text-muted-foreground" />
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}