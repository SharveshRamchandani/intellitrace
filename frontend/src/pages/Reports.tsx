import { motion } from "framer-motion";
import { FileText, Download } from "lucide-react";

const reports = [
  { name: "Fraud Summary Report", desc: "Overview of all detected fraud patterns", date: "Jan 15, 2024" },
  { name: "Exposure Analysis", desc: "Financial exposure across supply chain tiers", date: "Jan 14, 2024" },
  { name: "Supplier Risk Ranking", desc: "All suppliers ranked by composite risk score", date: "Jan 13, 2024" },
  { name: "Regulator-Ready Report", desc: "Compliance-formatted fraud intelligence report", date: "Jan 12, 2024" },
];

export default function Reports() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Reports</h1>
        <p className="text-sm text-muted-foreground mt-1">Generate and export fraud intelligence reports</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {reports.map((r, i) => (
          <motion.div
            key={r.name}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.1 }}
            className="glass-card p-5 flex items-start gap-4"
          >
            <div className="p-2.5 rounded-xl bg-primary/10">
              <FileText className="h-5 w-5 text-primary" />
            </div>
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-foreground">{r.name}</h3>
              <p className="text-xs text-muted-foreground mt-1">{r.desc}</p>
              <p className="text-xs text-muted-foreground mt-2">Generated: {r.date}</p>
              <div className="flex gap-2 mt-3">
                <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-primary/10 text-primary text-xs font-medium hover:bg-primary/20 transition-colors">
                  <Download className="h-3 w-3" /> PDF
                </button>
                <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-secondary text-secondary-foreground text-xs font-medium hover:bg-secondary/80 transition-colors">
                  <Download className="h-3 w-3" /> CSV
                </button>
              </div>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
