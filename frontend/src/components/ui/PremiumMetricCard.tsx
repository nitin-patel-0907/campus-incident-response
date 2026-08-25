import React from 'react';
import { motion } from 'framer-motion';
import { ShieldAlert, TrendingUp, TrendingDown, Activity } from 'lucide-react';
import { cn } from '@/lib/utils'; // Assuming Shadcn utility is present

export interface PremiumMetricCardProps {
  title: string;
  value: string | number;
  trend?: number;
  trendDirection?: 'up' | 'down';
  isCritical?: boolean;
  icon?: React.ReactNode;
  className?: string;
}

export function PremiumMetricCard({ 
  title, 
  value, 
  trend, 
  trendDirection = 'up', 
  isCritical = false,
  icon,
  className
}: PremiumMetricCardProps) {
  return (
    <motion.div 
      whileHover={{ y: -4, scale: 1.01 }}
      transition={{ type: "spring", stiffness: 300 }}
      className={cn(
        "relative p-6 rounded-2xl bg-card border border-white/10 backdrop-blur-xl overflow-hidden shadow-lg",
        isCritical && "shadow-[0_0_20px_rgba(244,63,94,0.15)] border-destructive/20",
        className
      )}
    >
      {/* Subtle background glow for critical items */}
      {isCritical && (
        <div className="absolute top-0 right-0 w-32 h-32 bg-destructive/10 blur-3xl rounded-full" />
      )}
      
      <div className="flex justify-between items-start mb-4 relative z-10">
        <h3 className="text-muted-foreground font-medium text-sm tracking-wide">{title}</h3>
        <div className={cn(
          "p-2 rounded-lg",
          isCritical ? "bg-destructive/20 text-destructive" : "bg-primary/20 text-primary"
        )}>
          {icon || <Activity size={18} />}
        </div>
      </div>
      
      <div className="flex items-end gap-3 relative z-10">
        <h2 className="text-4xl font-bold text-foreground font-sora">{value}</h2>
        
        {trend !== undefined && (
          <span className={cn(
            "flex items-center text-sm font-medium mb-1",
            trendDirection === 'up' ? (isCritical ? "text-destructive" : "text-success") : "text-muted-foreground"
          )}>
            {trendDirection === 'up' ? (
              <TrendingUp size={14} className="mr-1" />
            ) : (
              <TrendingDown size={14} className="mr-1" />
            )}
            {trend}%
          </span>
        )}
      </div>
    </motion.div>
  );
}
