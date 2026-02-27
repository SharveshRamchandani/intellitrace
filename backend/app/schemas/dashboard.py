from pydantic import BaseModel


class KPIMetric(BaseModel):
    """Matches frontend kpiData metric shape: { value, trend, direction }."""
    value: float
    trend: float        # percentage change vs previous period
    direction: str      # "up" | "down"


class RiskDistributionItem(BaseModel):
    """Matches frontend fraudRiskDistribution shape."""
    category: str
    count: int
    risk: str           # "high" | "medium" | "low"


class VolumeDataPoint(BaseModel):
    """Matches frontend invoiceVolumeData shape."""
    month: str
    invoices: int
    revenue: float      # sum of invoice amounts ($K)


class SparklineData(BaseModel):
    """12-point sparkline arrays for KPI cards."""
    totalInvoices: list[float]
    highRiskInvoices: list[float]
    suspiciousSuppliers: list[float]
    exposureValue: list[float]


class DashboardResponse(BaseModel):
    """
    Full dashboard payload — matches all frontend dashboard data needs.
    GET /api/dashboard
    """
    totalInvoices: KPIMetric
    highRiskInvoices: KPIMetric
    suspiciousSuppliers: KPIMetric
    exposureValue: KPIMetric
    sparklineData: SparklineData
    fraudRiskDistribution: list[RiskDistributionItem]
    invoiceVolumeData: list[VolumeDataPoint]
