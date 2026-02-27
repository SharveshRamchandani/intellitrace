"""
routes/network.py
──────────────────
GET /api/graph — supply chain network graph (nodes + edges).
"""
import structlog
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.network import NetworkResponse
from app.services import get_network_graph

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/api/graph", tags=["Network"])


@router.get("", response_model=NetworkResponse)
async def get_graph(db: AsyncSession = Depends(get_db)):
    """
    Returns the live supply chain graph computed from real invoice data.
    Response shape matches frontend networkNodes + networkEdges exactly:
      nodes: [{ id, label, type, risk, x, y }]
      edges: [{ from, to, type }]
    """
    return await get_network_graph(db)
