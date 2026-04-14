import React from "react";

function getClass(i, highlights, sorted) {
  if (sorted.has(i))                                              return "sorted";
  if (highlights.swapping  && highlights.swapping.includes(i))  return "swapping";
  if (highlights.pivot     === i)                                return "pivot";
  if (highlights.comparing && highlights.comparing.includes(i)) return "comparing";
  return "";
}

const STATE_STYLES = {
  sorted:    { border: "2px solid #4ade80", background: "rgba(74,222,128,0.1)" },
  swapping:  { border: "2px solid #f87171", background: "rgba(248,113,113,0.15)" },
  pivot:     { border: "2px solid #a78bfa", background: "rgba(167,139,250,0.15)" },
  comparing: { border: "2px solid #fbbf24", background: "rgba(251,191,36,0.15)" },
  "":        { border: "2px solid transparent", background: "#1e293b" },
};

export default function CardGrid({ array, highlights, sorted }) {
  return (
    <div style={{
      display: "grid",
      gridTemplateColumns: "repeat(auto-fill, minmax(64px, 1fr))",
      gap: "4px",
      maxHeight: "420px",
      overflowY: "auto",
    }}>
      {array.map((p, i) => {
        const state = getClass(i, highlights, sorted);
        const style = STATE_STYLES[state];
        return (
          <div key={i} style={{
            borderRadius: "8px",
            padding: "4px",
            textAlign: "center",
            transition: "border-color 0.12s, background 0.12s",
            ...style,
          }}>
            {p.img
              ? <img src={p.img} alt={p.name} style={{ width: 48, height: 48, imageRendering: "pixelated" }} />
              : <div style={{ width: 48, height: 48, margin: "0 auto", background: "#334155", borderRadius: 6 }} />
            }
            <div style={{ fontSize: 9, color: "#94a3b8", fontWeight: 700 }}>#{String(p.id).padStart(3, "0")}</div>
            <div style={{ fontSize: 8, color: "#e2e8f0", fontWeight: 600, textTransform: "capitalize", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{p.name}</div>
          </div>
        );
      })}
    </div>
  );
}
