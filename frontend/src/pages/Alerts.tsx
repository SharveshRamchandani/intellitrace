import { useState } from "react";
import { motion } from "framer-motion";
import { alertsData } from "@/data/mockData";
import { useNavigate } from "react-router-dom";
import { RiskLevel } from "@/components/RiskBadge";
import { cn } from "@/lib/utils";

const filters = ["All", "High Risk", "Cascade", "Duplicate", "Revenue Mismatch", "Carousel"];

export default function Alerts() {
  const [filter, setFilter] = useState("All");
  const navigate = useNavigate();

  const filtered = filter === "All" ? alertsData : alertsData.filter((a) => {
    if (filter === "High Risk") return a.severity === "high";
    return a.type === filter;
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Alerts</h1>
        <p className="text-sm text-muted-foreground mt-1">Real-time fraud detection alerts</p>
      </div>

      <div className="flex gap-2 flex-wrap">
        {filters.map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={cn(
              "px-3 py-1.5 rounded-xl text-xs font-medium transition-colors",
              filter === f ? "bg-primary text-primary-foreground" : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
            )}
          >
            {f}
          </button>
        ))}
      </div>

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border">
              {["Alert Type", "Supplier", "Invoice", "Severity", "Timestamp", "Status"].map((h) => (
                <th key={h} className="text-left text-xs font-medium text-muted-foreground px-5 py-3">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.map((a) => (
              <tr
                key={a.id}
                onClick={() => navigate(`/invoices/${a.invoice}`)}
                className="border-b border-border last:border-0 hover:bg-secondary/40 transition-colors cursor-pointer"
              >
                <td className="px-5 py-3 text-sm text-foreground">{a.type}</td>
                <td className="px-5 py-3 text-sm text-foreground">{a.supplier}</td>
                <td className="px-5 py-3 text-sm font-mono text-muted-foreground">{a.invoice}</td>
                <td className="px-5 py-3"><RiskLevel level={a.severity} /></td>
                <td className="px-5 py-3 text-sm text-muted-foreground">{a.timestamp}</td>
                <td className="px-5 py-3">
                  <span className={cn(
                    "text-xs font-medium px-2 py-1 rounded-lg",
                    a.status === "Open" && "bg-risk-high/10 text-risk-high",
                    a.status === "Reviewed" && "bg-risk-medium/10 text-risk-medium",
                    a.status === "Resolved" && "bg-risk-low/10 text-risk-low"
                  )}>{a.status}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </motion.div>
    </div>
  );
}
