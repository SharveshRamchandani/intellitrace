import { useState, useRef, useEffect } from "react";
import { motion } from "framer-motion";
import { networkNodes, networkEdges } from "@/data/mockData";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";

export default function Network() {
  const [cascadeOn, setCascadeOn] = useState(true);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    canvas.width = canvas.offsetWidth * dpr;
    canvas.height = canvas.offsetHeight * dpr;
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, canvas.offsetWidth, canvas.offsetHeight);

    const w = canvas.offsetWidth;
    const h = canvas.offsetHeight;
    const scaleX = w / 800;
    const scaleY = h / 700;

    // Draw edges
    networkEdges.forEach((edge) => {
      const from = networkNodes.find((n) => n.id === edge.from);
      const to = networkNodes.find((n) => n.id === edge.to);
      if (!from || !to) return;
      if (!cascadeOn && edge.type === "cascade") return;

      ctx.beginPath();
      ctx.moveTo(from.x * scaleX, from.y * scaleY);
      ctx.lineTo(to.x * scaleX, to.y * scaleY);
      ctx.strokeStyle =
        edge.type === "circular" ? "hsl(0, 72%, 51%)" :
        edge.type === "cascade" ? "hsl(38, 92%, 50%)" :
        "hsl(220, 20%, 25%)";
      ctx.lineWidth = edge.type === "normal" ? 1 : 2;
      ctx.stroke();
    });

    // Draw nodes
    networkNodes.forEach((node) => {
      const x = node.x * scaleX;
      const y = node.y * scaleY;
      const r = node.type === "buyer" ? 20 : 14;
      const color =
        node.risk === "high" ? "hsl(0, 72%, 51%)" :
        node.risk === "medium" ? "hsl(38, 92%, 50%)" :
        "hsl(142, 71%, 45%)";

      // Glow for high risk
      if (node.risk === "high") {
        ctx.beginPath();
        ctx.arc(x, y, r + 8, 0, Math.PI * 2);
        ctx.fillStyle = "hsla(0, 72%, 51%, 0.15)";
        ctx.fill();
      }

      ctx.beginPath();
      ctx.arc(x, y, r, 0, Math.PI * 2);
      ctx.fillStyle = hoveredNode === node.id ? color : "hsl(220, 26%, 11%)";
      ctx.fill();
      ctx.strokeStyle = color;
      ctx.lineWidth = 2;
      ctx.stroke();

      // Label
      ctx.fillStyle = "hsl(210, 40%, 93%)";
      ctx.font = "11px Inter, sans-serif";
      ctx.textAlign = "center";
      ctx.fillText(node.label, x, y + r + 16);
    });
  }, [hoveredNode, cascadeOn]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Network Intelligence</h1>
        <p className="text-sm text-muted-foreground mt-1">Interactive supply chain graph</p>
      </div>

      <div className="flex gap-4">
        <div className="flex-1 glass-card p-4 relative" style={{ minHeight: 500 }}>
          <canvas
            ref={canvasRef}
            className="w-full h-full"
            style={{ minHeight: 460 }}
            onMouseMove={(e) => {
              const rect = e.currentTarget.getBoundingClientRect();
              const mx = e.clientX - rect.left;
              const my = e.clientY - rect.top;
              const scaleX = rect.width / 800;
              const scaleY = rect.height / 700;
              const found = networkNodes.find((n) => {
                const dx = n.x * scaleX - mx;
                const dy = n.y * scaleY - my;
                return Math.sqrt(dx * dx + dy * dy) < 20;
              });
              setHoveredNode(found?.id || null);
            }}
          />
          {hoveredNode && (() => {
            const node = networkNodes.find((n) => n.id === hoveredNode);
            if (!node) return null;
            return (
              <div className="absolute bg-card border border-border rounded-xl px-3 py-2 shadow-xl pointer-events-none text-sm" style={{ left: 20, top: 20 }}>
                <p className="font-semibold text-foreground">{node.label}</p>
                <p className="text-muted-foreground capitalize">{node.type} · {node.risk} risk</p>
              </div>
            );
          })()}
        </div>

        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="w-64 glass-card p-5 space-y-5">
          <h3 className="text-sm font-semibold text-foreground">Controls</h3>
          <div className="flex items-center justify-between">
            <Label className="text-sm text-muted-foreground">Cascade Detection</Label>
            <Switch checked={cascadeOn} onCheckedChange={setCascadeOn} />
          </div>
          <div className="flex items-center justify-between">
            <Label className="text-sm text-muted-foreground">Duplicate View</Label>
            <Switch />
          </div>
          <div className="flex items-center justify-between">
            <Label className="text-sm text-muted-foreground">Velocity Alerts</Label>
            <Switch />
          </div>
          <div className="pt-4 border-t border-border space-y-2">
            <h4 className="text-xs font-medium text-muted-foreground">Legend</h4>
            <div className="flex items-center gap-2"><span className="h-3 w-3 rounded-full bg-risk-high" /><span className="text-xs text-muted-foreground">High Risk / Circular</span></div>
            <div className="flex items-center gap-2"><span className="h-3 w-3 rounded-full bg-risk-medium" /><span className="text-xs text-muted-foreground">Medium / Cascade</span></div>
            <div className="flex items-center gap-2"><span className="h-3 w-3 rounded-full bg-risk-low" /><span className="text-xs text-muted-foreground">Low Risk</span></div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
