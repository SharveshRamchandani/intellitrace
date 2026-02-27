"""
graph_builder.py
────────────────
Builds a directed NetworkX graph from invoice data and computes:
  - Cycle detection (carousel fraud)
  - Cascade depth (multi-tier cascades)
  - Degree centrality (hub suppliers)
"""
from __future__ import annotations

import networkx as nx
from dataclasses import dataclass, field


@dataclass
class GraphFeatures:
    cycle_flag: bool = False
    cascade_depth: int = 0
    degree_centrality: float = 0.0
    is_hub: bool = False
    circular_edges: list[tuple[str, str]] = field(default_factory=list)
    cascade_edges: list[tuple[str, str]] = field(default_factory=list)


class SupplyChainGraph:
    """
    Directed graph: Supplier → Invoice → Buyer (+ Supplier → Lender links).
    Node naming convention:
      - suppliers: "s_{supplier_id}"
      - buyers:    "b_{buyer_id}"
      - invoices:  "i_{invoice_id}"
    """

    def __init__(self) -> None:
        self.G: nx.DiGraph = nx.DiGraph()

    # ── Build ─────────────────────────────────────────────────────────────────

    def add_invoice(
        self,
        invoice_id: str,
        supplier_id: str,
        buyer_id: str,
        lender_id: str | None = None,
        tier: int = 1,
    ) -> None:
        s_node = f"s_{supplier_id}"
        b_node = f"b_{buyer_id}"
        i_node = f"i_{invoice_id}"

        self.G.add_node(s_node, type="supplier", tier=tier)
        self.G.add_node(b_node, type="buyer")
        self.G.add_node(i_node, type="invoice")

        # Supplier finances invoice, invoice goes to buyer
        self.G.add_edge(s_node, i_node, edge_type="supplies")
        self.G.add_edge(i_node, b_node, edge_type="delivered_to")

        if lender_id:
            l_node = f"l_{lender_id}"
            self.G.add_node(l_node, type="lender")
            self.G.add_edge(i_node, l_node, edge_type="financed_by")

    def add_supplier_relationship(
        self, upstream_supplier_id: str, downstream_supplier_id: str
    ) -> None:
        """Tier relationship: Tier-2 supplier works for Tier-1 supplier."""
        self.G.add_edge(
            f"s_{upstream_supplier_id}",
            f"s_{downstream_supplier_id}",
            edge_type="tier_link",
        )

    # ── Analysis ─────────────────────────────────────────────────────────────

    def detect_cycles(self) -> list[list[str]]:
        """Return all simple cycles in the graph (carousel indicators)."""
        try:
            return list(nx.simple_cycles(self.G))
        except Exception:
            return []

    def get_cascade_depth(self, supplier_node: str) -> int:
        """
        BFS height of the subgraph reachable from this supplier
        (how many tiers deep the cascade goes).
        """
        if supplier_node not in self.G:
            return 0
        try:
            lengths = nx.single_source_shortest_path_length(self.G, supplier_node)
            return max(lengths.values()) if lengths else 0
        except Exception:
            return 0

    def get_degree_centrality(self, node: str) -> float:
        """Normalized degree centrality of a node."""
        centrality = nx.degree_centrality(self.G)
        return round(centrality.get(node, 0.0), 4)

    # ── Feature Extraction ────────────────────────────────────────────────────

    def extract_features_for_supplier(self, supplier_id: str) -> GraphFeatures:
        s_node = f"s_{supplier_id}"
        cycles = self.detect_cycles()

        # Identify cycles containing this supplier
        supplier_cycles = [c for c in cycles if s_node in c]
        cycle_flag = len(supplier_cycles) > 0

        cascade_depth = self.get_cascade_depth(s_node)
        degree_centrality = self.get_degree_centrality(s_node)
        is_hub = degree_centrality > 0.3

        # Classify edges
        circular_edges: list[tuple[str, str]] = []
        cascade_edges: list[tuple[str, str]] = []

        for cycle in supplier_cycles:
            for i in range(len(cycle) - 1):
                circular_edges.append((cycle[i], cycle[i + 1]))

        # Cascade edges = tier_link edges reachable from supplier
        for u, v, data in self.G.edges(data=True):
            if data.get("edge_type") == "tier_link":
                if nx.has_path(self.G, s_node, u):
                    cascade_edges.append((u, v))

        return GraphFeatures(
            cycle_flag=cycle_flag,
            cascade_depth=cascade_depth,
            degree_centrality=degree_centrality,
            is_hub=is_hub,
            circular_edges=circular_edges,
            cascade_edges=cascade_edges,
        )

    # ── Frontend Graph Serialization ──────────────────────────────────────────

    def to_frontend_format(
        self,
        supplier_risk_map: dict[str, str],
        buyer_risk_map: dict[str, str],
        positions: dict[str, tuple[float, float]] | None = None,
    ) -> tuple[list[dict], list[dict]]:
        """
        Convert graph to { nodes, edges } format the frontend expects.
        Uses spring layout if no positions provided.
        """
        if positions is None:
            pos = nx.spring_layout(self.G, seed=42, k=2.0)
            # Scale to 800×700 canvas (frontend canvas size)
            positions = {
                n: (float(xy[0]) * 400 + 400, float(xy[1]) * 350 + 350)
                for n, xy in pos.items()
            }

        nodes: list[dict] = []
        for node, data in self.G.nodes(data=True):
            node_type = data.get("type", "supplier")
            if node_type == "invoice":
                continue  # don't expose invoice nodes to frontend graph

            raw_id = node[2:]  # strip "s_" / "b_" / "l_" prefix
            x, y = positions.get(node, (400.0, 350.0))

            if node_type == "supplier":
                risk = supplier_risk_map.get(raw_id, "low")
                label = raw_id  # will be overridden by caller with real name
            elif node_type == "buyer":
                risk = buyer_risk_map.get(raw_id, "low")
                label = raw_id
            else:
                continue

            nodes.append({"id": node, "label": label, "type": node_type, "risk": risk, "x": round(x, 1), "y": round(y, 1)})

        edges: list[dict] = []
        cycles = self.detect_cycles()
        cycle_edge_set: set[tuple[str, str]] = set()
        for cycle in cycles:
            for i in range(len(cycle)):
                cycle_edge_set.add((cycle[i], cycle[(i + 1) % len(cycle)]))

        for u, v, data in self.G.edges(data=True):
            edge_type_raw = data.get("edge_type", "normal")
            if edge_type_raw == "financed_by":
                continue
            if (u, v) in cycle_edge_set:
                edge_type = "circular"
            elif edge_type_raw == "tier_link":
                edge_type = "cascade"
            else:
                edge_type = "normal"
            edges.append({"from": u, "to": v, "type": edge_type})

        return nodes, edges
