import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "@/hooks/useTheme";
import LandingPage from "./pages/LandingPage";
import Dashboard from "./pages/Dashboard";
import ReportIncident from "./pages/ReportIncident";
import IncidentHistory from "./pages/IncidentHistory";
import AIInsights from "./pages/AIInsights";
import HumanReview from "./pages/HumanReview";
import PerformanceInsights from "./pages/PerformanceInsights";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <ThemeProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/report" element={<ReportIncident />} />
            <Route path="/history" element={<IncidentHistory />} />
            <Route path="/insights" element={<AIInsights />} />
            <Route path="/performance" element={<PerformanceInsights />} />
            <Route path="/review" element={<HumanReview />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </ThemeProvider>
  </QueryClientProvider>
);

export default App;
