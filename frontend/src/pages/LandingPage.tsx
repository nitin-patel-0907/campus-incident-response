import { MainLayout } from "@/components/layout/MainLayout";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useNavigate } from "react-router-dom";
import {
  Shield,
  Zap,
  Brain,
  Clock,
  Users,
  FileText,
  AlertTriangle,
  CheckCircle,
  ArrowRight,
  MessageSquare,
  Camera,
  BarChart3,
  Lock,
  Sparkles,
} from "lucide-react";

export default function LandingPage() {
  const navigate = useNavigate();

  const handleReportIncident = () => {
    navigate("/report");
  };

  return (
    <MainLayout>
      <div className="space-y-8">
        {/* Hero Section */}
        <section className="relative overflow-hidden rounded-lg bg-gradient-to-br from-primary/10 via-accent/5 to-background border border-border/50">
          <div className="absolute inset-0" />
          <div className="relative p-8">
            <div className="grid gap-8 lg:grid-cols-2 lg:gap-12 items-center">
              <div className="space-y-6">
                <div className="space-y-4">
                  <Badge className="bg-primary/10 text-primary border-primary/30 px-3 py-1">
                    <Sparkles className="h-3 w-3 mr-1" />
                    AI-Powered Campus Safety
                  </Badge>
                  <h1 className="text-3xl md:text-4xl font-bold">
                    Campus Incident
                    <span className="text-primary"> Response System</span>
                  </h1>
                  <p className="text-base text-muted-foreground leading-relaxed">
                    Advanced AI-powered incident management with real-time analysis, 
                    automated response planning, and comprehensive safety protocols. 
                    Report incidents instantly and get intelligent assistance.
                  </p>
                </div>
                
                <div className="flex flex-col sm:flex-row gap-4">
                  <Button 
                    size="lg" 
                    className="gap-2 h-12 px-8 button-primary-enhanced"
                    onClick={handleReportIncident}
                  >
                    <AlertTriangle className="h-5 w-5" />
                    Report Incident Now
                  </Button>
                </div>

                <div className="grid grid-cols-3 gap-4 pt-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary">24/7</div>
                    <div className="text-sm text-muted-foreground">AI Monitoring</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary">&lt;2min</div>
                    <div className="text-sm text-muted-foreground">Response Time</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold text-primary">95%</div>
                    <div className="text-sm text-muted-foreground">Success Rate</div>
                  </div>
                </div>
              </div>

              <div className="relative">
                <div className="grid grid-cols-2 gap-4">
                  <Card className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-primary/10">
                        <Brain className="h-5 w-5 text-primary" />
                      </div>
                      <div>
                        <div className="font-medium">AI Analysis</div>
                        <div className="text-sm text-muted-foreground">Intelligent Processing</div>
                      </div>
                    </div>
                  </Card>
                  <Card className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-success/10">
                        <Shield className="h-5 w-5 text-success" />
                      </div>
                      <div>
                        <div className="font-medium">Secure</div>
                        <div className="text-sm text-muted-foreground">FERPA Compliant</div>
                      </div>
                    </div>
                  </Card>
                  <Card className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-warning/10">
                        <Zap className="h-5 w-5 text-warning" />
                      </div>
                      <div>
                        <div className="font-medium">Fast</div>
                        <div className="text-sm text-muted-foreground">Instant Response</div>
                      </div>
                    </div>
                  </Card>
                  <Card className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-accent/10">
                        <BarChart3 className="h-5 w-5 text-accent" />
                      </div>
                      <div>
                        <div className="font-medium">Analytics</div>
                        <div className="text-sm text-muted-foreground">Real-time Insights</div>
                      </div>
                    </div>
                  </Card>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section className="space-y-6">
          <div className="text-center space-y-4">
            <h2 className="text-2xl font-bold">How Our AI System Works</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Our advanced AI agents work together to provide comprehensive incident response
            </p>
          </div>
          
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-5">
            <Card className="p-6 text-center">
              <div className="mx-auto w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                <FileText className="h-6 w-6 text-primary" />
              </div>
              <h3 className="font-semibold mb-2">1. Report</h3>
              <p className="text-sm text-muted-foreground">
                Submit incident details through our secure form
              </p>
            </Card>
            
            <Card className="p-6 text-center">
              <div className="mx-auto w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center mb-4">
                <Brain className="h-6 w-6 text-accent" />
              </div>
              <h3 className="font-semibold mb-2">2. AI Analysis</h3>
              <p className="text-sm text-muted-foreground">
                AI agents analyze and categorize the incident
              </p>
            </Card>
            
            <Card className="p-6 text-center">
              <div className="mx-auto w-12 h-12 rounded-lg bg-warning/10 flex items-center justify-center mb-4">
                <Shield className="h-6 w-6 text-warning" />
              </div>
              <h3 className="font-semibold mb-2">3. Safety Check</h3>
              <p className="text-sm text-muted-foreground">
                Compliance and safety protocols verified
              </p>
            </Card>
            
            <Card className="p-6 text-center">
              <div className="mx-auto w-12 h-12 rounded-lg bg-success/10 flex items-center justify-center mb-4">
                <Zap className="h-6 w-6 text-success" />
              </div>
              <h3 className="font-semibold mb-2">4. Response</h3>
              <p className="text-sm text-muted-foreground">
                Automated response plan generated and executed
              </p>
            </Card>
            
            <Card className="p-6 text-center">
              <div className="mx-auto w-12 h-12 rounded-lg bg-destructive/10 flex items-center justify-center mb-4">
                <BarChart3 className="h-6 w-6 text-destructive" />
              </div>
              <h3 className="font-semibold mb-2">5. Evaluate</h3>
              <p className="text-sm text-muted-foreground">
                Performance assessed and lessons learned
              </p>
            </Card>
          </div>
        </section>

        {/* Key Features */}
        <section className="space-y-6">
          <div className="text-center space-y-4">
            <h2 className="text-2xl font-bold">Key Features</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto">
              Comprehensive campus safety management with cutting-edge AI technology
            </p>
          </div>
          
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <Card className="p-6">
              <div className="flex items-start gap-4">
                <div className="p-2 rounded-lg bg-primary/10 flex-shrink-0">
                  <Camera className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold mb-2">Image Analysis</h3>
                  <p className="text-sm text-muted-foreground">
                    AI-powered image analysis for incident scene assessment and evidence documentation
                  </p>
                </div>
              </div>
            </Card>
            
            <Card className="p-6">
              <div className="flex items-start gap-4">
                <div className="p-2 rounded-lg bg-success/10 flex-shrink-0">
                  <Lock className="h-5 w-5 text-success" />
                </div>
                <div>
                  <h3 className="font-semibold mb-2">Privacy Protected</h3>
                  <p className="text-sm text-muted-foreground">
                    FERPA compliant with advanced privacy protection and secure data handling
                  </p>
                </div>
              </div>
            </Card>
            
            <Card className="p-6">
              <div className="flex items-start gap-4">
                <div className="p-2 rounded-lg bg-warning/10 flex-shrink-0">
                  <Clock className="h-5 w-5 text-warning" />
                </div>
                <div>
                  <h3 className="font-semibold mb-2">24/7 Monitoring</h3>
                  <p className="text-sm text-muted-foreground">
                    Round-the-clock AI monitoring with instant response and escalation protocols
                  </p>
                </div>
              </div>
            </Card>
            
            <Card className="p-6">
              <div className="flex items-start gap-4">
                <div className="p-2 rounded-lg bg-accent/10 flex-shrink-0">
                  <MessageSquare className="h-5 w-5 text-accent" />
                </div>
                <div>
                  <h3 className="font-semibold mb-2">Multi-Channel Reporting</h3>
                  <p className="text-sm text-muted-foreground">
                    Report incidents via web, mobile, phone, or anonymous tip systems
                  </p>
                </div>
              </div>
            </Card>
            
            <Card className="p-6">
              <div className="flex items-start gap-4">
                <div className="p-2 rounded-lg bg-destructive/10 flex-shrink-0">
                  <Users className="h-5 w-5 text-destructive" />
                </div>
                <div>
                  <h3 className="font-semibold mb-2">Stakeholder Coordination</h3>
                  <p className="text-sm text-muted-foreground">
                    Automated coordination between security, medical, counseling, and administration
                  </p>
                </div>
              </div>
            </Card>
            
            <Card className="p-6">
              <div className="flex items-start gap-4">
                <div className="p-2 rounded-lg bg-primary/10 flex-shrink-0">
                  <BarChart3 className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold mb-2">Advanced Analytics</h3>
                  <p className="text-sm text-muted-foreground">
                    Comprehensive reporting, trend analysis, and predictive insights
                  </p>
                </div>
              </div>
            </Card>
          </div>
        </section>

        {/* Call to Action */}
        <section className="relative overflow-hidden rounded-lg bg-gradient-to-r from-primary/10 to-accent/10 border border-border/50">
          <div className="absolute inset-0" />
          <div className="relative p-8 text-center space-y-6">
            <div className="space-y-4">
              <h2 className="text-2xl font-bold">Need to Report an Incident?</h2>
              <p className="text-base text-muted-foreground max-w-2xl mx-auto">
                Our AI-powered system is ready to assist you 24/7. Get immediate help and 
                comprehensive incident management with just a few clicks.
              </p>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button 
                size="lg" 
                className="gap-2 h-12 px-8 button-primary-enhanced"
                onClick={handleReportIncident}
              >
                <AlertTriangle className="h-5 w-5" />
                Report Incident
                <ArrowRight className="h-5 w-5" />
              </Button>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 pt-8">
              <div className="flex items-center justify-center gap-2 text-sm">
                <CheckCircle className="h-4 w-4 text-success" />
                <span>Secure & Confidential</span>
              </div>
              <div className="flex items-center justify-center gap-2 text-sm">
                <CheckCircle className="h-4 w-4 text-success" />
                <span>AI-Powered Analysis</span>
              </div>
              <div className="flex items-center justify-center gap-2 text-sm">
                <CheckCircle className="h-4 w-4 text-success" />
                <span>Immediate Response</span>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="mt-12 border-t border-border pt-8 text-center space-y-4">
          <div className="flex items-center justify-center gap-6 text-sm text-muted-foreground">
            <span>Campus Security: (555) 123-4567</span>
            <span>•</span>
            <span>Anonymous Tip Line: (555) 123-TIPS</span>
          </div>
          <p className="text-sm text-muted-foreground">
            Built with <span className="text-primary font-medium">Agentic AI</span> for Campus Safety
          </p>
        </footer>
      </div>
    </MainLayout>
  );
}