import { useState, useEffect } from "react";
import {
  FileText,
  CheckCircle,
  AlertTriangle,
  Clock,
  TrendingUp,
  RefreshCw,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { apiClient } from "@/lib/api";
import { PremiumMetricCard } from "@/components/ui/PremiumMetricCard";

interface DashboardStats {
  total_incidents: number;
  resolved: number;
  in_progress: number;
  high_severity: number;
  avg_response_score: number;
}

interface DashboardTrends {
  total_change: string;
  resolved_change: string;
  response_score_change: string;
}

export function StatsCards() {
  const [stats, setStats] = useState<DashboardStats>({
    total_incidents: 0,
    resolved: 0,
    in_progress: 0,
    high_severity: 0,
    avg_response_score: 0,
  });
  const [trends, setTrends] = useState<DashboardTrends>({
    total_change: "+0%",
    resolved_change: "+0%",
    response_score_change: "+0.0",
  });
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<string>("");

  const loadDashboardData = async () => {
    try {
      const response = await apiClient.getDashboardAnalytics();
      if (response.success) {
        setStats(response.stats);
        setTrends(response.trends);
        setLastUpdated(new Date().toLocaleTimeString());
      }
    } catch (error) {
      console.error("Error loading dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const statsConfig = [
    {
      name: "Total Reports",
      value: loading ? "..." : stats.total_incidents.toString(),
      change: trends.total_change,
      changeType: "neutral" as const,
      icon: FileText,
      color: "blue",
    },
    {
      name: "Resolved",
      value: loading ? "..." : stats.resolved.toString(),
      change: trends.resolved_change,
      changeType: "positive" as const,
      icon: CheckCircle,
      color: "green",
    },
    {
      name: "Active",
      value: loading ? "..." : stats.in_progress.toString(),
      change: stats.in_progress > 0 ? `${stats.in_progress}` : "0",
      changeType: "neutral" as const,
      icon: Clock,
      color: "orange",
    },
    {
      name: "High Priority",
      value: loading ? "..." : stats.high_severity.toString(),
      change: stats.high_severity > 0 ? `${stats.high_severity}` : "0",
      changeType: stats.high_severity === 0 ? "positive" : "warning" as const,
      icon: AlertTriangle,
      color: "red",
    },
    {
      name: "Response Score",
      value: loading ? "..." : `${Math.round(stats.avg_response_score * 10) / 10}`,
      change: trends.response_score_change,
      changeType: "positive" as const,
      icon: TrendingUp,
      color: "purple",
    },
  ];

  return (
    <div className="space-y-3">
      {/* Simple header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          {lastUpdated ? `Last updated: ${lastUpdated}` : 'Loading...'}
        </div>
      </div>
      
      {/* Stats Grid - Premium Bento Style */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        {statsConfig.map((stat, index) => {
          let trendNum = undefined;
          let trendDir: 'up' | 'down' = 'up';
          
          if (stat.change && typeof stat.change === 'string' && stat.change.includes('%')) {
             const num = parseFloat(stat.change.replace(/[^0-9.-]+/g,""));
             if (!isNaN(num)) {
                 trendNum = Math.abs(num);
                 trendDir = num >= 0 ? 'up' : 'down';
             }
          }

          return (
            <PremiumMetricCard
              key={stat.name}
              title={stat.name}
              value={stat.value}
              trend={trendNum}
              trendDirection={trendDir}
              isCritical={stat.color === 'red'}
              icon={<stat.icon size={18} />}
            />
          );
        })}
      </div>
      
      {/* No data message - more casual */}
      {!loading && stats.total_incidents === 0 && (
        <div className="human-card human-spacing text-center">
          <p className="text-muted-foreground text-sm">
            No incidents yet. <span className="text-primary">Submit your first report</span> to see live stats.
          </p>
        </div>
      )}
    </div>
  );
}
