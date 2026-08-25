import { MainLayout } from "@/components/layout/MainLayout";
import { StatsCards } from "@/components/dashboard/StatsCards";
import { IncidentChart } from "@/components/dashboard/IncidentChart";
import { SeverityChart } from "@/components/dashboard/SeverityChart";
import { TypeDistributionChart } from "@/components/dashboard/TypeDistributionChart";
import { EffectivenessGauge } from "@/components/dashboard/EffectivenessGauge";
import { RecentIncidents } from "@/components/dashboard/RecentIncidents";
import { AgentFlowDiagram } from "@/components/dashboard/AgentFlowDiagram";
import { PolicyComplianceStatus } from "@/components/dashboard/PolicyComplianceStatus";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { useNavigate } from "react-router-dom";
import {
  AlertTriangle,
  Activity,
  TrendingUp,
  Shield,
} from "lucide-react";

export default function Dashboard() {
  const navigate = useNavigate();

  return (
    <MainLayout>
      <div className="space-professional-md">
        {/* Header */}
        <section className="flex items-start justify-between gap-4">
          <div className="space-professional-xs">
            <h1 className="heading-2-professional">Campus Safety Dashboard</h1>
            <p className="body-small-professional">
              Live incident tracking and system status
            </p>
          </div>
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1.5 bg-success/10 border border-success/20 rounded-lg">
              <div className="status-dot status-dot-success animate-pulse-subtle" />
              <span className="text-success text-sm font-medium">System Online</span>
            </div>
            <Button 
              className="btn-primary-professional gap-2"
              onClick={() => navigate("/report")}
            >
              <AlertTriangle className="h-4 w-4" />
              Report Issue
            </Button>
          </div>
        </section>

        {/* Stats Overview */}
        <section className="space-professional-sm">
          <StatsCards />
        </section>

        {/* Charts */}
        <section className="space-professional-sm">
          <div className="flex items-center gap-2 mb-4">
            <TrendingUp className="h-4 w-4 text-primary" />
            <h2 className="heading-4-professional">Incident Analytics</h2>
          </div>
          
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            <div className="md:col-span-2">
              <IncidentChart />
            </div>
            <EffectivenessGauge />
            <TypeDistributionChart />
            <SeverityChart />
          </div>
        </section>

        {/* Policy & Activity */}
        <div className="grid gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 space-professional-sm">
            <div className="flex items-center gap-2 mb-4">
              <Shield className="h-4 w-4 text-primary" />
              <h2 className="heading-4-professional">Compliance Status</h2>
            </div>
            <PolicyComplianceStatus />
          </div>
          
          <div className="space-professional-sm">
            <div className="flex items-center gap-2 mb-4">
              <Activity className="h-4 w-4 text-primary" />
              <h2 className="heading-4-professional">Recent Activity</h2>
            </div>
            <div className="space-professional-sm">
              <RecentIncidents />
              <AgentFlowDiagram />
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
