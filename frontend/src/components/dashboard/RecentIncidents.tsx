import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Clock, MapPin, Eye, RefreshCw } from "lucide-react";
import { apiClient } from "@/lib/api";

interface RecentIncident {
  id: string;
  type: string;
  location: string;
  time: string;
  status: string;
  severity: string;
  workflow_id: string;
}

const statusStyles = {
  resolved: "bg-success/10 text-success border-success/30",
  "in-progress": "bg-warning/10 text-warning border-warning/30",
  blocked: "bg-destructive/10 text-destructive border-destructive/30",
};

const severityStyles = {
  low: "bg-success/10 text-success",
  medium: "bg-warning/10 text-warning",
  high: "bg-destructive/10 text-destructive",
  critical: "bg-red-500/10 text-red-500",
};

export function RecentIncidents() {
  const [incidents, setIncidents] = useState<RecentIncident[]>([]);
  const [loading, setLoading] = useState(true);

  const loadRecentIncidents = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getDashboardAnalytics();
      if (response.success) {
        setIncidents(response.recent_incidents);
      }
    } catch (error) {
      console.error("Error loading recent incidents:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadRecentIncidents();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(loadRecentIncidents, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleViewIncident = (workflowId: string) => {
    // Navigate to incident history with this incident highlighted
    window.location.href = `/history?highlight=${workflowId}`;
  };

  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-lg font-medium">Recent Incidents</CardTitle>
        <Button
          variant="ghost"
          size="sm"
          onClick={loadRecentIncidents}
          disabled={loading}
          className="gap-2"
        >
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </Button>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {loading ? (
            <div className="space-y-3">
              {[1, 2, 3].map((i) => (
                <div key={i} className="animate-pulse">
                  <div className="h-16 bg-muted/30 rounded-lg"></div>
                </div>
              ))}
            </div>
          ) : incidents.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground">No recent incidents found.</p>
              <p className="text-sm text-muted-foreground mt-1">
                Submit an incident report to see it appear here.
              </p>
            </div>
          ) : (
            incidents.map((incident, index) => (
              <div
                key={`${incident.id}-${index}`}
                className="flex items-center justify-between rounded-lg bg-muted/30 p-3 transition-all duration-200 hover:bg-muted/50"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-sm truncate max-w-[120px]" title={incident.type}>
                      {incident.type}
                    </span>
                    <Badge
                      variant="outline"
                      className={`${severityStyles[incident.severity as keyof typeof severityStyles]} flex-shrink-0`}
                    >
                      {incident.severity}
                    </Badge>
                  </div>
                  <div className="mt-1 flex items-center gap-3 text-xs text-muted-foreground">
                    <span className="flex items-center gap-1 truncate max-w-[100px]" title={incident.location}>
                      <MapPin className="h-3 w-3 flex-shrink-0" />
                      <span className="truncate">{incident.location}</span>
                    </span>
                    <span className="flex items-center gap-1 flex-shrink-0">
                      <Clock className="h-3 w-3" />
                      {incident.time}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge
                    variant="outline"
                    className={statusStyles[incident.status as keyof typeof statusStyles]}
                  >
                    {incident.status}
                  </Badge>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleViewIncident(incident.workflow_id)}
                    className="gap-1 px-2"
                  >
                    <Eye className="h-3 w-3" />
                    View
                  </Button>
                </div>
              </div>
            ))
          )}
          
          {incidents.length > 0 && (
            <div className="pt-2 border-t border-border">
              <Button
                variant="outline"
                size="sm"
                onClick={() => window.location.href = '/history'}
                className="w-full"
              >
                View All Incidents
              </Button>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
