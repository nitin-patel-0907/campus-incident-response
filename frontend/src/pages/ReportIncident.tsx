import { useState } from "react";
import { MainLayout } from "@/components/layout/MainLayout";
import { IncidentForm } from "@/components/report/IncidentForm";
import { AIProcessingPanel } from "@/components/report/AIProcessingPanel";
import { Card, CardContent } from "@/components/ui/card";
import { Shield, Lock } from "lucide-react";

export default function ReportIncident() {
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleSubmit = () => {
    setIsProcessing(true);
    setIsSubmitted(true);
  };

  const handleReset = () => {
    setIsSubmitted(false);
    setIsProcessing(false);
  };

  return (
    <MainLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex flex-col gap-2">
          <h1 className="text-2xl font-semibold">Report Incident</h1>
          <p className="text-muted-foreground text-sm">
            Submit a new campus incident for AI-powered processing and response
          </p>
        </div>

        {/* Safety Note */}
        <Card className="border-primary/20 bg-primary/5">
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="flex h-8 w-8 items-center justify-center rounded-md bg-primary/10">
                <Lock className="h-4 w-4 text-primary" />
              </div>
              <p className="text-sm text-muted-foreground">
                <span className="font-medium text-foreground">Your report is confidential and protected.</span>{" "}
                All submissions are encrypted and handled according to university privacy policies.
              </p>
            </div>
          </CardContent>
        </Card>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Incident Form */}
          <div className={isSubmitted ? "lg:col-span-1" : "lg:col-span-2 max-w-2xl"}>
            <IncidentForm 
              onSubmit={handleSubmit} 
              isSubmitted={isSubmitted}
              onReset={handleReset}
            />
          </div>

          {/* AI Processing Panel */}
          {isSubmitted && (
            <div className="animate-in slide-in-from-right-5 duration-300">
              <AIProcessingPanel isProcessing={isProcessing} />
            </div>
          )}
        </div>

        {/* Footer */}
        <footer className="mt-8 border-t border-border pt-6 text-center">
          <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
            <Shield className="h-4 w-4" />
            <span>Protected by SafeCampus AI Security</span>
          </div>
        </footer>
      </div>
    </MainLayout>
  );
}
