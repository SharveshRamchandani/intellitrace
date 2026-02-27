import { motion } from "framer-motion";
import {
  Bar, BarChart, Line, LineChart, ResponsiveContainer,
  XAxis, YAxis, Tooltip, CartesianGrid, Area, AreaChart
} from "recharts";
import { fraudRiskDistribution, invoiceVolumeData } from "@/data/mockData";

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload) return null;
  return (
    <div className="bg-card border border-border rounded-xl px-3 py-2 shadow-lg">
      <p className="text-xs text-muted-foreground">{label}</p>
      {payload.map((p: any, i: number) => (
        <p key={i} className="text-sm font-medium text-foreground">
          {p.name}: {p.value.toLocaleString()}
        </p>
      ))}
    </div>
  );
};

export function FraudRiskChart() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.4 }}
      className="glass-card p-5"
    >
      <h3 className="text-sm font-semibold text-foreground mb-4">Fraud Risk Distribution</h3>
      <ResponsiveContainer width="100%" height={260}>
        <BarChart data={fraudRiskDistribution} barSize={28}>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(220, 20%, 16%)" />
          <XAxis dataKey="category" tick={{ fontSize: 11, fill: "hsl(215, 15%, 55%)" }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fontSize: 11, fill: "hsl(215, 15%, 55%)" }} axisLine={false} tickLine={false} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="count" radius={[6, 6, 0, 0]} fill="hsl(217, 91%, 60%)" />
        </BarChart>
      </ResponsiveContainer>
    </motion.div>
  );
}

export function InvoiceVolumeChart() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.5 }}
      className="glass-card p-5"
    >
      <h3 className="text-sm font-semibold text-foreground mb-4">Invoice Volume vs Revenue</h3>
      <ResponsiveContainer width="100%" height={260}>
        <AreaChart data={invoiceVolumeData}>
          <defs>
            <linearGradient id="invoiceGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="hsl(217, 91%, 60%)" stopOpacity={0.2} />
              <stop offset="100%" stopColor="hsl(217, 91%, 60%)" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="revenueGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="hsl(142, 71%, 45%)" stopOpacity={0.2} />
              <stop offset="100%" stopColor="hsl(142, 71%, 45%)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="hsl(220, 20%, 16%)" />
          <XAxis dataKey="month" tick={{ fontSize: 11, fill: "hsl(215, 15%, 55%)" }} axisLine={false} tickLine={false} />
          <YAxis tick={{ fontSize: 11, fill: "hsl(215, 15%, 55%)" }} axisLine={false} tickLine={false} />
          <Tooltip content={<CustomTooltip />} />
          <Area type="monotone" dataKey="invoices" stroke="hsl(217, 91%, 60%)" fill="url(#invoiceGrad)" strokeWidth={2} name="Invoices" />
          <Area type="monotone" dataKey="revenue" stroke="hsl(142, 71%, 45%)" fill="url(#revenueGrad)" strokeWidth={2} name="Revenue ($K)" />
        </AreaChart>
      </ResponsiveContainer>
    </motion.div>
  );
}
