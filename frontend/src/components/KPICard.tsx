import { motion } from "framer-motion";
import { ArrowUp, ArrowDown } from "lucide-react";
import { Area, AreaChart, ResponsiveContainer } from "recharts";

interface KPICardProps {
  title: string;
  value: string;
  trend: number;
  direction: "up" | "down";
  sparkline: number[];
  index: number;
}

export function KPICard({ title, value, trend, direction, sparkline, index }: KPICardProps) {
  const isPositiveTrend = (direction === "up" && title !== "High-Risk Invoices" && title !== "Suspicious Suppliers") ||
    (direction === "down" && (title === "High-Risk Invoices" || title === "Suspicious Suppliers"));
  const trendColor = isPositiveTrend ? "text-risk-low" : "text-risk-high";
  const data = sparkline.map((v, i) => ({ v, i }));

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      className="glass-card p-5 relative overflow-hidden"
    >
      <p className="text-sm text-muted-foreground mb-1">{title}</p>
      <div className="flex items-end justify-between">
        <div>
          <p className="text-2xl font-bold text-foreground">{value}</p>
          <div className={`flex items-center gap-1 mt-1 text-xs font-medium ${trendColor}`}>
            {direction === "up" ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />}
            {Math.abs(trend)}%
          </div>
        </div>
        <div className="w-20 h-10">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
              <defs>
                <linearGradient id={`spark-${index}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="hsl(217, 91%, 60%)" stopOpacity={0.3} />
                  <stop offset="100%" stopColor="hsl(217, 91%, 60%)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <Area
                type="monotone"
                dataKey="v"
                stroke="hsl(217, 91%, 60%)"
                fill={`url(#spark-${index})`}
                strokeWidth={1.5}
                dot={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </motion.div>
  );
}
