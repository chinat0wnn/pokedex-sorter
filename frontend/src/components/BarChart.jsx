import React from "react";

const COLORS = {
  default:   "#60a5fa",
  comparing: "#fbbf24",
  swapping:  "#f87171",
  pivot:     "#a78bfa",
  sorted:    "#4ade80",
};

function getColor(i, highlights, sorted) {
  if (sorted.has(i))                                                  return COLORS.sorted;
  if (highlights.swapping  && highlights.swapping.includes(i))       return COLORS.swapping;
  if (highlights.pivot     === i)                                     return COLORS.pivot;
  if (highlights.comparing && highlights.comparing.includes(i))      return COLORS.comparing;
  return COLORS.default;
}

export default function BarChart({ array, highlights, sorted }) {
  return (
    <div style={{
      display: "flex",
      alignItems: "flex-end",
      gap: "2px",
      height: "280px",
      padding: "8px 4px 0",
      overflow: "hidden",
    }}>
      {array.map((p, i) => {
        const h = Math.max(4, Math.round((p.id / 151) * 265));
        return (
          <div
            key={i}
            title={`#${p.id} ${p.name}`}
            style={{
              flex: 1,
              minWidth: "3px",
              height: `${h}px`,
              borderRadius: "2px 2px 0 0",
              background: getColor(i, highlights, sorted),
              transition: "background 0.08s",
            }}
          />
        );
      })}
    </div>
  );
}
