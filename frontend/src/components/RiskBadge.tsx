import { cn } from "@/lib/utils";

interface RiskBadgeProps {
  score: number;
  className?: string;
}

export function RiskBadge({ score, className }: RiskBadgeProps) {
  const level = score >= 70 ? "high" : score >= 40 ? "medium" : "low";
  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold",
        level === "high" && "bg-risk-high/15 text-risk-high",
        level === "medium" && "bg-risk-medium/15 text-risk-medium",
        level === "low" && "bg-risk-low/15 text-risk-low",
        className
      )}
    >
      {score}
    </span>
  );
}

export function RiskLevel({ level }: { level: "high" | "medium" | "low" }) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 text-xs font-medium",
        level === "high" && "text-risk-high",
        level === "medium" && "text-risk-medium",
        level === "low" && "text-risk-low"
      )}
    >
      <span className={cn(
        "h-2 w-2 rounded-full",
        level === "high" && "bg-risk-high",
        level === "medium" && "bg-risk-medium",
        level === "low" && "bg-risk-low"
      )} />
      {level.charAt(0).toUpperCase() + level.slice(1)}
    </span>
  );
}
