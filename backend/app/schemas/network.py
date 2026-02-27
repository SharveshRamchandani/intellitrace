from pydantic import BaseModel


class NetworkNode(BaseModel):
    """Matches frontend networkNodes shape exactly."""
    id: str
    label: str
    type: str       # "buyer" | "supplier"
    risk: str       # "high" | "medium" | "low"
    x: float
    y: float


class NetworkEdge(BaseModel):
    """Matches frontend networkEdges shape exactly."""
    from_: str      # aliased to "from" in JSON output
    to: str
    type: str       # "normal" | "cascade" | "circular"

    model_config = {"populate_by_name": True}

    def model_dump(self, **kwargs):  # ensure "from" key (not "from_") in output
        d = super().model_dump(**kwargs)
        d["from"] = d.pop("from_")
        return d


class NetworkResponse(BaseModel):
    """GET /api/graph response."""
    nodes: list[NetworkNode]
    edges: list[NetworkEdge]
