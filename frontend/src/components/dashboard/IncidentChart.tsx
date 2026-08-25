import { useState, useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from "recharts";
import { RefreshCw } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiClient } from "@/lib/api";

interface TimeSeriesData {
  name: string;
  incidents: number;
  resolved: number;
}

export function IncidentChart() {
  const [data, setData] = useState<TimeSeriesData[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<string>("");

  const loadChartData = async () => {
    try {
      const response = await apiClient.getDashboardAnalytics();
      if (response.success && response.time_series) {
        setData(response.time_series);
        setLastUpdated(new Date().toLocaleTimeString());
      }
    } catch (error) {
      console.error("Error loading chart data:", error);
      // Fallback to empty data if API fails
      setData([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadChartData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadChartData, 30000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Card className="bg-card border-white/10 backdrop-blur-xl shadow-lg overflow-hidden">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-base font-medium">
          Incidents Over Time
        </CardTitle>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <RefreshCw className={`h-3 w-3 ${loading ? 'animate-spin' : ''}`} />
          {lastUpdated && <span>{lastUpdated}</span>}
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-[280px]">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <div className="flex items-center gap-2 text-muted-foreground">
                <RefreshCw className="h-4 w-4 animate-spin" />
                Loading chart data...
              </div>
            </div>
          ) : data.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-muted-foreground">
                <p className="text-sm">No data yet</p>
                <p className="text-xs">Submit incidents to see trends</p>
              </div>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data}>
                <defs>
                  <linearGradient id="incidentGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="resolvedGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="hsl(var(--success))" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="hsl(var(--success))" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                <XAxis dataKey="name" className="text-xs" stroke="hsl(var(--muted-foreground))" />
                <YAxis className="text-xs" stroke="hsl(var(--muted-foreground))" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "rgba(26, 31, 44, 0.8)",
                    backdropFilter: "blur(12px)",
                    border: "1px solid rgba(255, 255, 255, 0.1)",
                    borderRadius: "12px",
                    color: "hsl(var(--foreground))",
                    boxShadow: "0 8px 32px rgba(0, 0, 0, 0.2)",
                  }}
                  formatter={(value, name) => [
                    <span className="font-medium ml-2">{value}</span>,
                    <span className="text-muted-foreground">{name === 'incidents' ? 'Total Incidents' : 'Resolved'}</span>
                  ]}
                />
                <Area
                  type="monotone"
                  dataKey="incidents"
                  stroke="hsl(var(--primary))"
                  strokeWidth={3}
                  fill="url(#incidentGradient)"
                  animationDuration={1500}
                  animationEasing="ease-in-out"
                />
                <Area
                  type="monotone"
                  dataKey="resolved"
                  stroke="hsl(var(--success))"
                  strokeWidth={3}
                  fill="url(#resolvedGradient)"
                  animationDuration={1500}
                  animationEasing="ease-in-out"
                />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
