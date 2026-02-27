export const kpiData = {
  totalInvoices: { value: 1247, trend: 12.5, direction: "up" as const },
  highRiskInvoices: { value: 23, trend: 8.3, direction: "up" as const },
  suspiciousSuppliers: { value: 7, trend: -2.1, direction: "down" as const },
  exposureValue: { value: 4850000, trend: 15.7, direction: "up" as const },
};

export const sparklineData = [
  [30, 40, 35, 50, 49, 60, 70, 61, 80, 75, 90, 85],
  [5, 8, 6, 12, 10, 15, 18, 14, 20, 23, 19, 23],
  [10, 8, 12, 9, 7, 11, 8, 6, 9, 7, 5, 7],
  [2.1, 2.5, 2.3, 3.0, 2.8, 3.5, 3.8, 4.0, 4.2, 4.5, 4.7, 4.85],
];

export const fraudRiskDistribution = [
  { category: "Revenue Mismatch", count: 42, risk: "high" },
  { category: "Velocity Anomaly", count: 35, risk: "medium" },
  { category: "Cascade Risk", count: 28, risk: "high" },
  { category: "Carousel Risk", count: 18, risk: "medium" },
  { category: "Duplicate", count: 12, risk: "low" },
  { category: "PO Mismatch", count: 8, risk: "low" },
];

export const invoiceVolumeData = [
  { month: "Jul", invoices: 890, revenue: 3200 },
  { month: "Aug", invoices: 920, revenue: 3400 },
  { month: "Sep", invoices: 1050, revenue: 3100 },
  { month: "Oct", invoices: 980, revenue: 3600 },
  { month: "Nov", invoices: 1120, revenue: 3800 },
  { month: "Dec", invoices: 1180, revenue: 4100 },
  { month: "Jan", invoices: 1247, revenue: 4500 },
];

export type FlaggedInvoice = {
  id: string;
  supplier: string;
  tier: number;
  amount: number;
  riskScore: number;
  riskCategory: string;
};

export const flaggedInvoices: FlaggedInvoice[] = [
  { id: "INV-2024-0891", supplier: "T1-Alpha Corp", tier: 1, amount: 245000, riskScore: 92, riskCategory: "Revenue Mismatch" },
  { id: "INV-2024-0887", supplier: "T2-Beta Industries", tier: 2, amount: 189000, riskScore: 87, riskCategory: "Cascade Risk" },
  { id: "INV-2024-0883", supplier: "T1-Gamma Ltd", tier: 1, amount: 312000, riskScore: 78, riskCategory: "Velocity Anomaly" },
  { id: "INV-2024-0879", supplier: "T3-Delta Mfg", tier: 3, amount: 95000, riskScore: 71, riskCategory: "Carousel Risk" },
  { id: "INV-2024-0874", supplier: "T2-Epsilon Svcs", tier: 2, amount: 167000, riskScore: 65, riskCategory: "Duplicate" },
  { id: "INV-2024-0870", supplier: "T1-Zeta Corp", tier: 1, amount: 420000, riskScore: 58, riskCategory: "PO Mismatch" },
  { id: "INV-2024-0866", supplier: "T2-Eta Solutions", tier: 2, amount: 134000, riskScore: 45, riskCategory: "Revenue Mismatch" },
  { id: "INV-2024-0861", supplier: "T3-Theta Inc", tier: 3, amount: 78000, riskScore: 34, riskCategory: "Velocity Anomaly" },
];

export const invoiceDetail = {
  id: "INV-2024-0891",
  supplier: "T1-Alpha Corp",
  buyer: "Anchor Industries PLC",
  tier: 1,
  amount: 245000,
  poMatch: false,
  grnMatch: true,
  duplicateStatus: "Possible duplicate detected",
  financingCount: 3,
  riskScore: 92,
  riskBreakdown: {
    revenueMismatch: 95,
    velocityAnomaly: 72,
    cascadeRisk: 88,
    carouselRisk: 45,
    duplicateRisk: 68,
  },
};

export const supplierData = {
  name: "T1-Alpha Corp",
  tier: 1,
  annualRevenue: 2400000,
  totalFinancedValue: 8900000,
  revenueRatio: 3.71,
  isAbnormal: true,
  invoiceFrequency: [
    { month: "Jul", count: 12 },
    { month: "Aug", count: 15 },
    { month: "Sep", count: 18 },
    { month: "Oct", count: 22 },
    { month: "Nov", count: 28 },
    { month: "Dec", count: 35 },
    { month: "Jan", count: 42 },
  ],
  riskScoreTrend: [
    { month: "Jul", score: 45 },
    { month: "Aug", score: 52 },
    { month: "Sep", score: 58 },
    { month: "Oct", score: 67 },
    { month: "Nov", score: 75 },
    { month: "Dec", score: 85 },
    { month: "Jan", score: 92 },
  ],
};

export const alertsData = [
  { id: 1, type: "Revenue Mismatch", supplier: "T1-Alpha Corp", invoice: "INV-2024-0891", severity: "high" as const, timestamp: "2024-01-15 14:32", status: "Open" as const },
  { id: 2, type: "Cascade Risk", supplier: "T2-Beta Industries", invoice: "INV-2024-0887", severity: "high" as const, timestamp: "2024-01-15 13:45", status: "Open" as const },
  { id: 3, type: "Velocity Anomaly", supplier: "T1-Gamma Ltd", invoice: "INV-2024-0883", severity: "medium" as const, timestamp: "2024-01-15 12:18", status: "Reviewed" as const },
  { id: 4, type: "Carousel Risk", supplier: "T3-Delta Mfg", invoice: "INV-2024-0879", severity: "medium" as const, timestamp: "2024-01-15 11:05", status: "Open" as const },
  { id: 5, type: "Duplicate", supplier: "T2-Epsilon Svcs", invoice: "INV-2024-0874", severity: "low" as const, timestamp: "2024-01-14 16:42", status: "Resolved" as const },
  { id: 6, type: "Revenue Mismatch", supplier: "T1-Zeta Corp", invoice: "INV-2024-0870", severity: "medium" as const, timestamp: "2024-01-14 15:30", status: "Reviewed" as const },
  { id: 7, type: "Cascade Risk", supplier: "T2-Eta Solutions", invoice: "INV-2024-0866", severity: "low" as const, timestamp: "2024-01-14 14:12", status: "Resolved" as const },
  { id: 8, type: "Velocity Anomaly", supplier: "T3-Theta Inc", invoice: "INV-2024-0861", severity: "low" as const, timestamp: "2024-01-14 10:55", status: "Resolved" as const },
];

export const networkNodes = [
  { id: "anchor", label: "Anchor Industries", type: "buyer", risk: "low", x: 400, y: 300 },
  { id: "t1-alpha", label: "T1-Alpha Corp", type: "supplier", risk: "high", x: 200, y: 150 },
  { id: "t1-gamma", label: "T1-Gamma Ltd", type: "supplier", risk: "medium", x: 600, y: 150 },
  { id: "t2-beta", label: "T2-Beta Industries", type: "supplier", risk: "high", x: 150, y: 400 },
  { id: "t2-epsilon", label: "T2-Epsilon Svcs", type: "supplier", risk: "medium", x: 650, y: 400 },
  { id: "t3-delta", label: "T3-Delta Mfg", type: "supplier", risk: "medium", x: 100, y: 550 },
  { id: "t3-theta", label: "T3-Theta Inc", type: "supplier", risk: "low", x: 700, y: 550 },
  { id: "t1-zeta", label: "T1-Zeta Corp", type: "supplier", risk: "medium", x: 400, y: 100 },
];

export const networkEdges = [
  { from: "t1-alpha", to: "anchor", type: "normal" },
  { from: "t1-gamma", to: "anchor", type: "normal" },
  { from: "t1-zeta", to: "anchor", type: "normal" },
  { from: "t2-beta", to: "t1-alpha", type: "cascade" },
  { from: "t2-epsilon", to: "t1-gamma", type: "normal" },
  { from: "t3-delta", to: "t2-beta", type: "cascade" },
  { from: "t3-theta", to: "t2-epsilon", type: "normal" },
  { from: "t3-delta", to: "t1-alpha", type: "circular" },
];
