import { motion } from "framer-motion";
import { supplierData } from "@/data/mockData";
import { AlertTriangle } from "lucide-react";
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip } from "recharts";

const ChartTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload) return null;
  return (
    <div className="bg-card border border-border rounded-xl px-3 py-2 shadow-lg">
      <p className="text-xs text-muted-foreground">{label}</p>
      {payload.map((p: any, i: number) => (
        <p key={i} className="text-sm font-medium text-foreground">{p.name}: {p.value}</p>
      ))}
    </div>
  );
};

export default function Suppliers() {
  const s = supplierData;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Supplier Profile</h1>
        <p className="text-sm text-muted-foreground mt-1">{s.name}</p>
      </div>

      {/* Summary */}
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card p-6">
        {s.isAbnormal && (
          <div className="flex items-center gap-2 p-3 rounded-xl bg-risk-high/10 border border-risk-high/20 mb-4">
            <AlertTriangle className="h-4 w-4 text-risk-high" />
            <span className="text-sm text-risk-high">Revenue ratio {s.revenueRatio}x — abnormally high financing vs revenue</span>
          </div>
        )}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            ["Tier Level", `T${s.tier}`],
            ["Annual Revenue", `$${(s.annualRevenue / 1000000).toFixed(1)}M`],
            ["Total Financed", `$${(s.totalFinancedValue / 1000000).toFixed(1)}M`],
            ["Revenue Ratio", `${s.revenueRatio}x`],
          ].map(([label, value]) => (
            <div key={label} className="text-center">
              <p className="text-xs text-muted-foreground">{label}</p>
              <p className="text-xl font-bold text-foreground mt-1">{value}</p>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass-card p-5">
          <h3 className="text-sm font-semibold text-foreground mb-4">Invoice Frequency</h3>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={s.invoiceFrequency}>
              <defs><linearGradient id="freqGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="hsl(217, 91%, 60%)" stopOpacity={0.2} /><stop offset="100%" stopColor="hsl(217, 91%, 60%)" stopOpacity={0} /></linearGradient></defs>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(220, 20%, 16%)" />
              <XAxis dataKey="month" tick={{ fontSize: 11, fill: "hsl(215, 15%, 55%)" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: "hsl(215, 15%, 55%)" }} axisLine={false} tickLine={false} />
              <Tooltip content={<ChartTooltip />} />
              <Area type="monotone" dataKey="count" stroke="hsl(217, 91%, 60%)" fill="url(#freqGrad)" strokeWidth={2} name="Invoices" />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="glass-card p-5">
          <h3 className="text-sm font-semibold text-foreground mb-4">Risk Score Trend</h3>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={s.riskScoreTrend}>
              <defs><linearGradient id="riskGrad" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="hsl(0, 72%, 51%)" stopOpacity={0.2} /><stop offset="100%" stopColor="hsl(0, 72%, 51%)" stopOpacity={0} /></linearGradient></defs>
              <CartesianGrid strokeDasharray="3 3" stroke="hsl(220, 20%, 16%)" />
              <XAxis dataKey="month" tick={{ fontSize: 11, fill: "hsl(215, 15%, 55%)" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: "hsl(215, 15%, 55%)" }} axisLine={false} tickLine={false} />
              <Tooltip content={<ChartTooltip />} />
              <Area type="monotone" dataKey="score" stroke="hsl(0, 72%, 51%)" fill="url(#riskGrad)" strokeWidth={2} name="Risk Score" />
            </AreaChart>
          </ResponsiveContainer>
        </motion.div>
      </div>
    </div>
  );
}
