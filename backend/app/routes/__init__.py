from app.routes.invoices import router as invoices_router
from app.routes.dashboard import router as dashboard_router
from app.routes.suppliers import router as suppliers_router
from app.routes.network import router as network_router
from app.routes.alerts import router as alerts_router

__all__ = [
    "invoices_router", "dashboard_router", "suppliers_router",
    "network_router", "alerts_router",
]
