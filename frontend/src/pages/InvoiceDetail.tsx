import { useParams, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { invoiceDetail } from "@/data/mockData";
import { ArrowLeft, Check, X, AlertTriangle } from "lucide-react";

function CircularScore({ score }: { score: number }) {
  const radius = 54;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (score / 100) * circumference;
  const color = score >= 70 ? "hsl(0, 72%, 51%)" : score >= 40 ? "hsl(38, 92%, 50%)" : "hsl(142, 71%, 45%)";

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg width="140" height="140" className="-rotate-90">
        <circle cx="70" cy="70" r={radius} fill="none" stroke="hsl(220, 20%, 16%)" strokeWidth="8" />
        <motion.circle
          cx="70" cy="70" r={radius} fill="none" stroke={color} strokeWidth="8"
          strokeLinecap="round" strokeDasharray={circumference}
          initial={{ strokeDashoffset: circumference }}
          animate={{ strokeDashoffset: offset }}
          transition={{ duration: 1.2, ease: "easeOut" }}
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-3xl font-bold text-foreground">{score}</span>
        <span className="text-xs text-muted-foreground">Risk Score</span>
      </div>
    </div>
  );
}

function ProgressBar({ label, value }: { label: string; value: number }) {
  const color = value >= 70 ? "bg-risk-high" : value >= 40 ? "bg-risk-medium" : "bg-risk-low";
  return (
    <div className="space-y-1.5">
      <div className="flex justify-between text-sm">
        <span className="text-muted-foreground">{label}</span>
        <span className="text-foreground font-medium">{value}%</span>
      </div>
      <div className="h-2 rounded-full bg-secondary overflow-hidden">
        <motion.div
          className={`h-full rounded-full ${color}`}
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
        />
      </div>
    </div>
  );
}

export default function InvoiceDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const inv = invoiceDetail;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <button onClick={() => navigate(-1)} className="p-2 rounded-xl hover:bg-secondary transition-colors">
          <ArrowLeft className="h-5 w-5 text-muted-foreground" />
        </button>
        <div>
          <h1 className="text-2xl font-bold text-foreground">{id || inv.id}</h1>
          <p className="text-sm text-muted-foreground">Invoice Detail</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Left – Invoice Info */}
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="glass-card p-6 space-y-4">
          <h3 className="text-sm font-semibold text-foreground mb-4">Invoice Information</h3>
          {[
            ["Invoice ID", inv.id],
            ["Supplier", inv.supplier],
            ["Buyer", inv.buyer],
            ["Tier", `T${inv.tier}`],
            ["Amount", `$${inv.amount.toLocaleString()}`],
            ["Financing Count", inv.financingCount.toString()],
          ].map(([label, value]) => (
            <div key={label} className="flex justify-between py-2 border-b border-border last:border-0">
              <span className="text-sm text-muted-foreground">{label}</span>
              <span className="text-sm font-medium text-foreground">{value}</span>
            </div>
          ))}
          <div className="flex gap-4 pt-2">
            <div className="flex items-center gap-2">
              {inv.poMatch ? <Check className="h-4 w-4 text-risk-low" /> : <X className="h-4 w-4 text-risk-high" />}
              <span className="text-sm text-muted-foreground">PO Match</span>
            </div>
            <div className="flex items-center gap-2">
              {inv.grnMatch ? <Check className="h-4 w-4 text-risk-low" /> : <X className="h-4 w-4 text-risk-high" />}
              <span className="text-sm text-muted-foreground">GRN Match</span>
            </div>
          </div>
          {inv.duplicateStatus && (
            <div className="flex items-center gap-2 p-3 rounded-xl bg-risk-high/10 border border-risk-high/20">
              <AlertTriangle className="h-4 w-4 text-risk-high" />
              <span className="text-sm text-risk-high">{inv.duplicateStatus}</span>
            </div>
          )}
        </motion.div>

        {/* Right – Risk Engine */}
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="glass-card p-6">
          <h3 className="text-sm font-semibold text-foreground mb-6">Risk Engine Output</h3>
          <div className="flex justify-center mb-8">
            <CircularScore score={inv.riskScore} />
          </div>
          <div className="space-y-4">
            <ProgressBar label="Revenue Mismatch" value={inv.riskBreakdown.revenueMismatch} />
            <ProgressBar label="Velocity Anomaly" value={inv.riskBreakdown.velocityAnomaly} />
            <ProgressBar label="Cascade Risk" value={inv.riskBreakdown.cascadeRisk} />
            <ProgressBar label="Carousel Risk" value={inv.riskBreakdown.carouselRisk} />
            <ProgressBar label="Duplicate Risk" value={inv.riskBreakdown.duplicateRisk} />
          </div>
        </motion.div>
      </div>
    </div>
  );
}
