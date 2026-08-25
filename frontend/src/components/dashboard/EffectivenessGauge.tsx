import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function EffectivenessGauge() {
  const score = 94.2;
  const circumference = 2 * Math.PI * 45;
  const progress = (score / 100) * circumference;

  return (
    <Card className="glass-card border-0">
      <CardHeader>
        <CardTitle className="text-lg font-semibold">
          System Effectiveness
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col items-center justify-center">
        <div className="relative">
          <svg width="140" height="140" className="transform -rotate-90">
            <circle
              cx="70"
              cy="70"
              r="45"
              stroke="hsl(var(--muted))"
              strokeWidth="10"
              fill="none"
            />
            <circle
              cx="70"
              cy="70"
              r="45"
              stroke="url(#gaugeGradient)"
              strokeWidth="10"
              fill="none"
              strokeDasharray={circumference}
              strokeDashoffset={circumference - progress}
              strokeLinecap="round"
              className="transition-all duration-1000 ease-out"
            />
            <defs>
              <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%" stopColor="hsl(var(--primary))" />
                <stop offset="100%" stopColor="hsl(var(--accent))" />
              </linearGradient>
            </defs>
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-3xl font-bold">{score}</span>
            <span className="text-xs text-muted-foreground">Score</span>
          </div>
        </div>
        <div className="mt-4 text-center">
          <p className="text-sm font-medium text-success">Excellent</p>
          <p className="text-xs text-muted-foreground">
            Above target performance
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
