import { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { RefreshCw } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiClient } from "@/lib/api";

interface SeverityData {
  name: string;
  value: number;
  color: string;
}

export function SeverityChart() {
  const [data, setData] = useState<SeverityData[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<string>("");

  const loadChartData = async () => {
    try {
      const response = await apiClient.getDashboardAnalytics();
      if (response.success && response.distributions.severity) {
        const severityData = response.distributions.severity;
        
        // Convert to chart format with colors
        const chartData: SeverityData[] = [
          { 
            name: "Low", 
            value: severityData.low || 0, 
            color: "hsl(var(--success))" 
          },
          { 
            name: "Medium", 
            value: severityData.medium || 0, 
            color: "hsl(var(--warning))" 
          },
          { 
            name: "High", 
            value: severityData.high || 0, 
            color: "hsl(var(--destructive))" 
          },
          { 
            name: "Critical", 
            value: severityData.critical || 0, 
            color: "hsl(0 84% 60%)" 
          },
        ].filter(item => item.value > 0); // Only show severities with data
        
        setData(chartData);
        setLastUpdated(new Date().toLocaleTimeString());
      }
    } catch (error) {
      console.error("Error loading severity chart data:", error);
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
          Severity Levels
        </CardTitle>
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <RefreshCw className={`h-3 w-3 ${loading ? 'animate-spin' : ''}`} />
          {lastUpdated && <span>{lastUpdated}</span>}
        </div>
      </CardHeader>
      <CardContent>
        <div className="h-[220px]">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <div className="flex items-center gap-2 text-muted-foreground">
                <RefreshCw className="h-4 w-4 animate-spin" />
                Loading severity data...
              </div>
            </div>
          ) : data.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-muted-foreground">
                <p className="text-sm">No severity data</p>
                <p className="text-xs">Submit incidents to see distribution</p>
              </div>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" className="stroke-border" horizontal={false} />
                <XAxis type="number" stroke="hsl(var(--muted-foreground))" />
                <YAxis dataKey="name" type="category" stroke="hsl(var(--muted-foreground))" width={60} />
                <Tooltip
                  cursor={{ fill: 'rgba(255, 255, 255, 0.05)' }}
                  content={({ active, payload, label }) => {
                    if (active && payload && payload.length) {
                      return (
                        <div className="bg-[#1A1F2C]/80 backdrop-blur-xl border border-white/10 rounded-xl p-3 shadow-[0_8px_32px_rgba(0,0,0,0.3)]">
                          <p className="text-muted-foreground font-medium mb-1">{label}</p>
                          {payload.map((entry, index) => (
                            <div key={index} className="flex items-center gap-2">
                              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.payload.color }} />
                              <p className="text-foreground text-lg font-bold">
                                {entry.value} <span className="text-sm font-normal text-muted-foreground ml-1">incidents</span>
                              </p>
                            </div>
                          ))}
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Bar dataKey="value" radius={[0, 8, 8, 0]} animationDuration={1500} animationEasing="ease-out">
                  {data.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
