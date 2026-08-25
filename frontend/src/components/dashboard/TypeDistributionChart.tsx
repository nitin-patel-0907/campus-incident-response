import { useState, useEffect } from "react";
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from "recharts";
import { RefreshCw } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiClient } from "@/lib/api";

interface TypeData {
  name: string;
  value: number;
}

const COLORS = [
  "hsl(var(--primary))",           // Blue
  "hsl(var(--destructive))",       // Red  
  "hsl(var(--warning))",           // Yellow/Orange
  "hsl(var(--accent))",            // Accent color
  "hsl(221 83% 53%)",              // Royal Blue
  "hsl(280 100% 70%)",             // Purple
  "hsl(200 100% 70%)",             // Light Blue
  "hsl(var(--muted-foreground))",  // Gray for "Other"
];

export function TypeDistributionChart() {
  const [data, setData] = useState<TypeData[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<string>("");

  const groupIncidentTypes = (typesData: Record<string, number>): TypeData[] => {
    // Define type groupings to reduce clutter
    const typeGroups: Record<string, string[]> = {
      "Safety & Security": ["threat", "assault", "weapon", "violence", "security"],
      "Harassment & Discrimination": ["harassment", "discrimination", "racial_discrimination", "sexual_harassment", "bullying"],
      "Academic Issues": ["academic_dishonesty", "research_misconduct", "plagiarism", "cheating"],
      "Health & Wellness": ["mental_health", "medical", "substance_abuse", "self_harm"],
      "Misconduct": ["faculty_misconduct", "misconduct", "ethics_violation", "policy_violation"],
      "Facilities & Property": ["property_damage", "maintenance", "facilities", "vandalism"],
      "Illegal Activity": ["illegal_activity", "drug", "theft", "fraud"]
    };

    // Group types
    const groupedData: Record<string, number> = {};
    const ungroupedTypes: Record<string, number> = {};

    // Initialize groups
    Object.keys(typeGroups).forEach(group => {
      groupedData[group] = 0;
    });

    // Categorize each type
    Object.entries(typesData).forEach(([type, count]) => {
      if (count <= 0) return;

      let grouped = false;
      const lowerType = type.toLowerCase();

      // Check if type belongs to any group
      for (const [groupName, keywords] of Object.entries(typeGroups)) {
        if (keywords.some(keyword => lowerType.includes(keyword) || keyword.includes(lowerType))) {
          groupedData[groupName] += count;
          grouped = true;
          break;
        }
      }

      // If not grouped, keep as individual type
      if (!grouped) {
        const displayName = type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        ungroupedTypes[displayName] = count;
      }
    });

    // Combine grouped and ungrouped data
    const allData: TypeData[] = [
      ...Object.entries(groupedData)
        .filter(([_, count]) => count > 0)
        .map(([name, value]) => ({ name, value })),
      ...Object.entries(ungroupedTypes)
        .map(([name, value]) => ({ name, value }))
    ];

    // Sort by value and limit to top 5 to prevent overflow
    const sortedData = allData.sort((a, b) => b.value - a.value);
    
    if (sortedData.length <= 5) {
      return sortedData;
    }

    // If more than 5 categories, group the smallest ones into "Other"
    const topCategories = sortedData.slice(0, 4);
    const otherCount = sortedData.slice(4).reduce((sum, item) => sum + item.value, 0);
    
    if (otherCount > 0) {
      topCategories.push({ name: "Other", value: otherCount });
    }

    return topCategories;
  };

  const loadChartData = async () => {
    try {
      const response = await apiClient.getDashboardAnalytics();
      if (response.success && response.distributions.types) {
        const typesData = response.distributions.types;
        
        console.log("Raw types data:", typesData);
        
        // Group and limit incident types to prevent overflow
        const chartData = groupIncidentTypes(typesData);
        
        console.log("Grouped chart data:", chartData);
        
        setData(chartData);
        setLastUpdated(new Date().toLocaleTimeString());
      }
    } catch (error) {
      console.error("Error loading type distribution data:", error);
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
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-base font-medium">
          Incident Types
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
                Loading type distribution...
              </div>
            </div>
          ) : data.length === 0 ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center text-muted-foreground">
                <p className="text-sm">No type data</p>
                <p className="text-xs">Submit incidents to see breakdown</p>
              </div>
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="45%"
                  innerRadius={50}
                  outerRadius={75}
                  paddingAngle={3}
                  dataKey="value"
                >
                  {data.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                      className="transition-all duration-300 hover:opacity-80"
                    />
                  ))}
                </Pie>
                <Tooltip
                  content={({ active, payload }) => {
                    if (active && payload && payload.length) {
                      const data = payload[0];
                      return (
                        <div className="bg-card border border-border rounded-lg p-3 shadow-lg">
                          <p className="text-foreground font-medium">{data.name}</p>
                          <p className="text-foreground">
                            <span className="font-medium">Count:</span> {data.value}
                          </p>
                          <p className="text-xs text-muted-foreground mt-1">
                            {data.value === 1 ? '1 incident' : `${data.value} incidents`}
                          </p>
                        </div>
                      );
                    }
                    return null;
                  }}
                />
                <Legend
                  content={({ payload }) => {
                    if (payload && payload.length) {
                      return (
                        <div className="flex flex-wrap gap-2 text-xs mt-2 justify-center">
                          {payload.map((entry, index) => (
                            <div key={index} className="flex items-center gap-1.5 min-w-0">
                              <div 
                                className="w-2.5 h-2.5 rounded-sm flex-shrink-0" 
                                style={{ backgroundColor: entry.color }}
                              />
                              <span className="text-foreground truncate text-xs max-w-[80px]" title={entry.value}>
                                {entry.value}
                              </span>
                            </div>
                          ))}
                        </div>
                      );
                    }
                    return null;
                  }}
                  wrapperStyle={{ paddingTop: '10px' }}
                />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </CardContent>
    </Card>
  );
}