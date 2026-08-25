import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import {
  FileInput,
  Brain,
  Shield,
  Zap,
  CheckCircle,
  Clock,
  AlertTriangle,
  HelpCircle,
  User,
} from "lucide-react";
import { cn } from "@/lib/utils";

interface Agent {
  id: string;
  name: string;
  icon: React.ElementType;
  description: string;
  explanation: string;
  status: "pending" | "processing" | "approved" | "completed" | "blocked";
}

const initialAgents: Agent[] = [
  {
    id: "intake",
    name: "Incident Intake Agent",
    icon: FileInput,
    description: "Structuring and validating the report",
    explanation: "This agent parses the incident details, validates required fields, and structures the data for downstream processing.",
    status: "pending",
  },
  {
    id: "planner",
    name: "Planner Agent",
    icon: Brain,
    description: "Creating response action plan",
    explanation: "Based on incident type and severity, this agent creates a prioritized action plan considering available resources and protocols.",
    status: "pending",
  },
  {
    id: "safety",
    name: "Safety & Policy Agent",
    icon: Shield,
    description: "Validating compliance with policies",
    explanation: "Ensures all planned actions comply with university safety policies, legal requirements, and ethical guidelines.",
    status: "pending",
  },
  {
    id: "executor",
    name: "Executor Agent",
    icon: Zap,
    description: "Initiating response actions",
    explanation: "Executes approved actions including notifications, resource dispatching, and coordination with relevant departments.",
    status: "pending",
  },
  {
    id: "evaluator",
    name: "Evaluator Agent",
    icon: CheckCircle,
    description: "Reviewing response effectiveness",
    explanation: "Analyzes the response quality, identifies improvements, and updates learning models for future incidents.",
    status: "pending",
  },
];

interface AIProcessingPanelProps {
  isProcessing: boolean;
}

export function AIProcessingPanel({ isProcessing }: AIProcessingPanelProps) {
  const [agents, setAgents] = useState<Agent[]>(initialAgents);
  const [showHumanLoop, setShowHumanLoop] = useState(false);

  useEffect(() => {
    if (!isProcessing) return;

    const delays = [500, 2000, 3500, 5000, 6500];
    const statuses: Array<"processing" | "completed" | "approved"> = [
      "completed",
      "completed",
      "approved",
      "completed",
      "completed",
    ];

    delays.forEach((delay, index) => {
      setTimeout(() => {
        setAgents((prev) =>
          prev.map((agent, i) => {
            if (i === index) {
              return { ...agent, status: "processing" };
            }
            if (i === index - 1) {
              return { ...agent, status: statuses[i] };
            }
            return agent;
          })
        );

        // Show human loop badge after safety agent
        if (index === 2) {
          setShowHumanLoop(true);
        }
      }, delay);
    });

    // Final completion
    setTimeout(() => {
      setAgents((prev) =>
        prev.map((agent, i) =>
          i === prev.length - 1 ? { ...agent, status: "completed" } : agent
        )
      );
    }, 8000);
  }, [isProcessing]);

  const getStatusIcon = (status: Agent["status"]) => {
    switch (status) {
      case "pending":
        return <Clock className="h-4 w-4 text-muted-foreground" />;
      case "processing":
        return (
          <div className="h-4 w-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
        );
      case "approved":
        return <Shield className="h-4 w-4 text-success" />;
      case "completed":
        return <CheckCircle className="h-4 w-4 text-success" />;
      case "blocked":
        return <AlertTriangle className="h-4 w-4 text-destructive" />;
    }
  };

  const getStatusBadge = (status: Agent["status"]) => {
    const styles = {
      pending: "bg-muted text-muted-foreground",
      processing: "bg-primary/20 text-primary animate-pulse",
      approved: "status-approved",
      completed: "status-completed",
      blocked: "status-blocked",
    };

    const labels = {
      pending: "Pending",
      processing: "Processing",
      approved: "Approved",
      completed: "Completed",
      blocked: "Blocked",
    };

    return (
      <Badge variant="outline" className={cn("text-xs", styles[status])}>
        {labels[status]}
      </Badge>
    );
  };

  return (
    <Card className="glass-card border-0">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>AI Processing Status</span>
          {showHumanLoop && (
            <Badge className="bg-warning text-warning-foreground animate-pulse gap-1">
              <User className="h-3 w-3" />
              Human Review Required
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {agents.map((agent, index) => (
          <div
            key={agent.id}
            className={cn(
              "flex items-start gap-4 rounded-lg p-4 transition-all duration-300",
              agent.status === "processing"
                ? "bg-primary/5 border border-primary/20"
                : "bg-muted/30"
            )}
          >
            <div
              className={cn(
                "flex h-10 w-10 items-center justify-center rounded-lg transition-all duration-300",
                agent.status === "completed" || agent.status === "approved"
                  ? "bg-success/20"
                  : agent.status === "processing"
                  ? "bg-primary/20 animate-pulse"
                  : "bg-muted"
              )}
            >
              <agent.icon
                className={cn(
                  "h-5 w-5",
                  agent.status === "completed" || agent.status === "approved"
                    ? "text-success"
                    : agent.status === "processing"
                    ? "text-primary"
                    : "text-muted-foreground"
                )}
              />
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-sm">{agent.name}</span>
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger>
                        <HelpCircle className="h-3.5 w-3.5 text-muted-foreground hover:text-foreground transition-colors" />
                      </TooltipTrigger>
                      <TooltipContent side="top" className="max-w-xs">
                        <p className="text-xs font-medium mb-1">Why this step?</p>
                        <p className="text-xs text-muted-foreground">
                          {agent.explanation}
                        </p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
                {getStatusBadge(agent.status)}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                {agent.description}
              </p>
            </div>

            <div className="flex items-center">{getStatusIcon(agent.status)}</div>
          </div>
        ))}

        {/* Feedback Loop Indicator */}
        <div className="mt-6 rounded-lg bg-muted/20 p-4 border border-dashed border-border">
          <div className="flex items-center justify-center gap-4 text-xs text-muted-foreground">
            <span className="font-medium">Feedback Loop</span>
            <div className="flex items-center gap-2">
              <span>Planner</span>
              <span className="text-primary">↔</span>
              <span>Executor</span>
              <span className="text-primary">↔</span>
              <span>Evaluator</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
