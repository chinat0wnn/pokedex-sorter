import React from "react";

export default function StatsPanel({ stats, elapsed, complexity }) {
  const c = complexity || {};
  return (
    <div>
      <div style={{ fontSize: 10, fontWeight: 700, color: "#e94560", textTransform: "uppercase", letterSpacing: 1, marginBottom: 8, paddingBottom: 6, borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
        Operações
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6, marginBottom: 8 }}>
        {[
          { label: "Comparações", value: stats.compares, color: "#fbbf24" },
          { label: "Trocas",      value: stats.swaps,    color: "#f87171" },
          { label: "Escritas",    value: stats.writes,   color: "#a78bfa" },
          { label: "Total Ops",   value: stats.compares + stats.swaps + stats.writes, color: "#60a5fa" },
        ].map(({ label, value, color }) => (
          <div key={label} style={{ background: "#0f3460", borderRadius: 8, padding: "8px", textAlign: "center", border: "1px solid rgba(255,255,255,0.07)" }}>
            <div style={{ fontSize: 16, fontWeight: 800, color }}>{value.toLocaleString()}</div>
            <div style={{ fontSize: 10, color: "#9ca3af", marginTop: 2 }}>{label}</div>
          </div>
        ))}
      </div>

      <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, color: "#9ca3af", marginBottom: 14 }}>
        <span>Tempo decorrido:</span>
        <span style={{ color: "#60a5fa", fontWeight: 700 }}>{elapsed}ms</span>
      </div>

      {c.name && (
        <>
          <div style={{ fontSize: 10, fontWeight: 700, color: "#e94560", textTransform: "uppercase", letterSpacing: 1, marginBottom: 8, paddingBottom: 6, borderBottom: "1px solid rgba(255,255,255,0.1)" }}>
            Complexidade
          </div>
          <div style={{ background: "#0f3460", borderRadius: 8, padding: 10, border: "1px solid rgba(255,255,255,0.07)", fontSize: 11 }}>
            <div style={{ fontWeight: 800, color: "#f0f0f0", marginBottom: 6, fontSize: 12 }}>{c.name}</div>
            {[["Melhor",  c.best], ["Médio", c.average], ["Pior", c.worst], ["Espaço", c.space]].map(([k, v]) => (
              <div key={k} style={{ display: "flex", justifyContent: "space-between", margin: "3px 0" }}>
                <span style={{ color: "#9ca3af" }}>{k}:</span>
                <span style={{ color: "#e94560", fontWeight: 700, fontFamily: "monospace" }}>{v}</span>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
