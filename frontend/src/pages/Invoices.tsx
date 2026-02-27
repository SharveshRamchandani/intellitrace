import { flaggedInvoices } from "@/data/mockData";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { RiskBadge } from "@/components/RiskBadge";
import { Eye } from "lucide-react";

export default function Invoices() {
  const navigate = useNavigate();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Invoices</h1>
        <p className="text-sm text-muted-foreground mt-1">All monitored invoices</p>
      </div>

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="glass-card overflow-hidden">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border">
              {["Invoice ID", "Supplier", "Tier", "Amount", "Risk Score", "Category", "Action"].map((h) => (
                <th key={h} className="text-left text-xs font-medium text-muted-foreground px-5 py-3">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {flaggedInvoices.map((inv) => (
              <tr
                key={inv.id}
                onClick={() => navigate(`/invoices/${inv.id}`)}
                className="border-b border-border last:border-0 hover:bg-secondary/40 transition-colors cursor-pointer"
              >
                <td className="px-5 py-3 text-sm font-mono text-foreground">{inv.id}</td>
                <td className="px-5 py-3 text-sm text-foreground">{inv.supplier}</td>
                <td className="px-5 py-3 text-sm text-muted-foreground">T{inv.tier}</td>
                <td className="px-5 py-3 text-sm text-foreground">${inv.amount.toLocaleString()}</td>
                <td className="px-5 py-3"><RiskBadge score={inv.riskScore} /></td>
                <td className="px-5 py-3 text-sm text-muted-foreground">{inv.riskCategory}</td>
                <td className="px-5 py-3">
                  <button className="p-1.5 rounded-lg hover:bg-primary/10 text-primary transition-colors">
                    <Eye className="h-4 w-4" />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </motion.div>
    </div>
  );
}
