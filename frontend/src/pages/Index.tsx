import { KPICard } from "@/components/KPICard";
import { FraudRiskChart, InvoiceVolumeChart } from "@/components/DashboardCharts";
import { RiskTable } from "@/components/RiskTable";
import { kpiData, sparklineData } from "@/data/mockData";

const kpis = [
  { title: "Total Invoices Today", value: kpiData.totalInvoices.value.toLocaleString(), trend: kpiData.totalInvoices.trend, direction: kpiData.totalInvoices.direction },
  { title: "High-Risk Invoices", value: kpiData.highRiskInvoices.value.toString(), trend: kpiData.highRiskInvoices.trend, direction: kpiData.highRiskInvoices.direction },
  { title: "Suspicious Suppliers", value: kpiData.suspiciousSuppliers.value.toString(), trend: kpiData.suspiciousSuppliers.trend, direction: kpiData.suspiciousSuppliers.direction },
  { title: "Exposure Value", value: `$${(kpiData.exposureValue.value / 1000000).toFixed(1)}M`, trend: kpiData.exposureValue.trend, direction: kpiData.exposureValue.direction },
];

const Index = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Dashboard</h1>
        <p className="text-sm text-muted-foreground mt-1">Supply chain fraud intelligence overview</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpis.map((kpi, i) => (
          <KPICard key={kpi.title} {...kpi} sparkline={sparklineData[i]} index={i} />
        ))}
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <FraudRiskChart />
        <InvoiceVolumeChart />
      </div>

      {/* Risk Table */}
      <RiskTable />
    </div>
  );
};

export default Index;
