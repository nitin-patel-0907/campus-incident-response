import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FileInput, Brain, Shield, Zap, CheckCircle, ArrowRight } from "lucide-react";

const agents = [
  { name: "Intake Agent", icon: FileInput, status: "active" },
  { name: "Planner Agent", icon: Brain, status: "active" },
  { name: "Safety Agent", icon: Shield, status: "active" },
  { name: "Executor Agent", icon: Zap, status: "active" },
  { name: "Evaluator Agent", icon: CheckCircle, status: "active" },
];

export function AgentFlowDiagram() {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg font-medium">AI Agent Pipeline</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap items-center justify-center gap-2">
          {agents.map((agent, index) => (
            <div key={agent.name} className="flex items-center">
              <div className="flex flex-col items-center gap-2">
                <div className="relative">
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                    <agent.icon className="h-5 w-5" />
                  </div>
                  <div className="absolute -bottom-1 -right-1 h-3 w-3 rounded-full bg-success border-2 border-card animate-pulse" />
                </div>
                <span className="text-xs font-medium text-center max-w-[80px]">
                  {agent.name}
                </span>
              </div>
              {index < agents.length - 1 && (
                <ArrowRight className="mx-2 h-4 w-4 text-muted-foreground" />
              )}
            </div>
          ))}
        </div>
        <div className="mt-6 flex justify-center">
          <div className="flex items-center gap-2 rounded-lg bg-primary/10 px-4 py-2">
            <div className="h-2 w-2 rounded-full bg-success animate-pulse" />
            <span className="text-xs font-medium text-primary">
              All agents operational
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
