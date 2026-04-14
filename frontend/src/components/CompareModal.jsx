import React, { useState } from "react";
import { compareAlgorithms } from "../services/api";

const ALGO_COLORS = {
  bubble:    "#60a5fa",
  selection: "#f87171",
  insertion: "#fbbf24",
  merge:     "#4ade80",
  quick:     "#a78bfa",
};

export default function CompareModal({ pokemon, onClose }) {
  const [data,    setData]    = useState(null);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);

  async function run() {
    setLoading(true);
    setError(null);
    try {
      const result = await compareAlgorithms([...pokemon]);
      setData(result);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  const maxOps = data
    ? Math.max(...Object.values(data.results).map((r) => r.stats.total))
    : 1;

  return (
    <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.7)", zIndex: 999, display: "flex", alignItems: "center", justifyContent: "center" }} onClick={onClose}>
      <div style={{ background: "#16213e", border: "1px solid rgba(255,255,255,0.15)", borderRadius: 12, padding: 24, width: "min(600px, 95vw)", maxHeight: "90vh", overflowY: "auto" }} onClick={(e) => e.stopPropagation()}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
          <h2 style={{ fontFamily: "'Press Start 2P', monospace", fontSize: 11, color: "#f5c518" }}>Comparar Algoritmos</h2>
          <button onClick={onClose} style={{ background: "none", border: "none", color: "#9ca3af", fontSize: 20, cursor: "pointer" }}>×</button>
        </div>

        {!data && !loading && (
          <div style={{ textAlign: "center", padding: "20px 0" }}>
            <p style={{ color: "#9ca3af", fontSize: 13, marginBottom: 16 }}>Roda todos os 5 algoritmos no mesmo array embaralhado e compara as operações.</p>
            <button onClick={run} style={{ background: "#e94560", color: "white", border: "none", borderRadius: 8, padding: "10px 24px", fontFamily: "'Nunito',sans-serif", fontWeight: 700, fontSize: 14, cursor: "pointer" }}>
              ▶ Executar Comparação
            </button>
          </div>
        )}

        {loading && (
          <div style={{ textAlign: "center", padding: "40px 0", color: "#f5c518", fontFamily: "'Press Start 2P',monospace", fontSize: 9 }}>Calculando...</div>
        )}

        {error && <div style={{ color: "#f87171", fontSize: 13, padding: 12 }}>{error}</div>}

        {data && (
          <div>
            <p style={{ color: "#9ca3af", fontSize: 12, marginBottom: 16 }}>n = {data.n} Pokémon</p>
            {Object.entries(data.results).map(([name, r]) => (
              <div key={name} style={{ marginBottom: 14 }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 4 }}>
                  <span style={{ color: ALGO_COLORS[name], fontWeight: 700, textTransform: "capitalize" }}>{r.complexity.name}</span>
                  <span style={{ color: "#9ca3af" }}>{r.stats.total.toLocaleString()} ops</span>
                </div>
                <div style={{ height: 10, background: "#0f3460", borderRadius: 5, overflow: "hidden" }}>
                  <div style={{ height: "100%", width: `${Math.round((r.stats.total / maxOps) * 100)}%`, background: ALGO_COLORS[name], borderRadius: 5, transition: "width 0.6s ease" }} />
                </div>
                <div style={{ display: "flex", gap: 12, fontSize: 10, color: "#6b7280", marginTop: 3 }}>
                  <span>Comp: {r.stats.compares.toLocaleString()}</span>
                  <span>Trocas: {r.stats.swaps.toLocaleString()}</span>
                  <span>Escritas: {r.stats.writes.toLocaleString()}</span>
                </div>
              </div>
            ))}
            <button onClick={run} style={{ marginTop: 8, background: "transparent", border: "1px solid rgba(255,255,255,0.15)", color: "#9ca3af", borderRadius: 8, padding: "8px 16px", fontSize: 12, cursor: "pointer", fontFamily: "'Nunito',sans-serif" }}>
              ↺ Novo Shuffle
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
