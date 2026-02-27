"""
network_service.py
───────────────────
Builds the supply chain graph for GET /api/graph.
"""
from __future__ import annotations

import logging
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invoice import Invoice
from app.models.supplier import Supplier
from app.models.buyer import Buyer
from app.fraud_engine.graph_builder import SupplyChainGraph
from app.schemas.network import NetworkResponse, NetworkNode, NetworkEdge

logger = logging.getLogger(__name__)


async def get_network_graph(db: AsyncSession) -> NetworkResponse:
    # Fetch all invoices with supplier + buyer
    stmt = select(Invoice)
    result = await db.execute(stmt)
    invoices = result.scalars().all()

    # Fetch supplier risk levels
    sup_stmt = select(Supplier)
    sup_result = await db.execute(sup_stmt)
    suppliers = {str(s.id): s for s in sup_result.scalars().all()}

    buyer_stmt = select(Buyer)
    buyer_result = await db.execute(buyer_stmt)
    buyers = {str(b.id): b for b in buyer_result.scalars().all()}

    graph = SupplyChainGraph()

    for inv in invoices:
        sup = suppliers.get(str(inv.supplier_id))
        if not sup:
            continue
        graph.add_invoice(
            invoice_id=inv.id,
            supplier_id=str(inv.supplier_id),
            buyer_id=str(inv.buyer_id),
            lender_id=str(inv.lender_id) if inv.lender_id else None,
            tier=sup.tier_level,
        )

    # Compute risk per supplier
    supplier_risk_map: dict[str, str] = {}
    for sid, sup in suppliers.items():
        features = graph.extract_features_for_supplier(sid)
        # Derive risk from avg fraud score for this supplier's invoices
        sup_invoices = [i for i in invoices if str(i.supplier_id) == sid]
        scores = [i.fraud_score for i in sup_invoices if i.fraud_score is not None]
        avg = (sum(scores) / len(scores)) if scores else 0.0
        if avg >= 71 or features.cycle_flag:
            supplier_risk_map[sid] = "high"
        elif avg >= 41 or features.cascade_depth >= 2:
            supplier_risk_map[sid] = "medium"
        else:
            supplier_risk_map[sid] = "low"

    buyer_risk_map = {bid: "low" for bid in buyers}

    raw_nodes, raw_edges = graph.to_frontend_format(supplier_risk_map, buyer_risk_map)

    # Enrich node labels with real names
    nodes: list[NetworkNode] = []
    for n in raw_nodes:
        raw_id = n["id"][2:]  # strip "s_" / "b_"
        if n["type"] == "supplier":
            label = suppliers.get(raw_id, type("", (), {"name": raw_id})()).name  # type: ignore
        else:
            label = buyers.get(raw_id, type("", (), {"name": raw_id})()).name  # type: ignore
        nodes.append(NetworkNode(
            id=n["id"], label=label, type=n["type"],
            risk=n["risk"], x=n["x"], y=n["y"],
        ))

    edges: list[NetworkEdge] = [
        NetworkEdge(from_=e["from"], to=e["to"], type=e["type"])
        for e in raw_edges
    ]

    return NetworkResponse(nodes=nodes, edges=edges)
