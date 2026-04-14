import React, { useState, useCallback } from "react";
import { usePokemon } from "./hooks/usePokemon";
import { useSort } from "./hooks/useSort";
import { runSort, getAlgorithms } from "./services/api";
import { shuffle } from "./utils/shuffle";
import BarChart from "./components/BarChart";
import CardGrid from "./components/CardGrid";
import StatsPanel from "./components/StatsPanel";
import CompareModal from "./components/CompareModal";

const ALGO_NAMES = {
  bubble:    "🫧 Bubble Sort",
  selection: "🎯 Selection Sort",
  insertion: "📥 Insertion Sort",
  merge:     "🔀 Merge Sort",
  quick:     "⚡ Quick Sort",
};

export default function App() {
  const { pokemon, loading: pokeLoading, progress: pokeProgress, error: pokeError, start: startLoad } = usePokemon();
  const sorter = useSort();

  const [algorithm,    setAlgorithm]    = useState("bubble");
  const [complexity,   setComplexity]   = useState(null);
  const [view,         setView]         = useState("bars");
  const [speed,        setSpeedState]   = useState(50);
  const [soundOn,      setSoundOn]      = useState(false);
  const [shuffled,     setShuffled]     = useState([]);
  const [status,       setStatus]       = useState("Clique em 'Carregar Pokémon' para começar.");
  const [loadingSort,  setLoadingSort]  = useState(false);
  const [showCompare,  setShowCompare]  = useState(false);

  // ─── Load Pokémon ───────────────────────────────────────────────
  async function handleLoad() {
    setStatus("Carregando Pokémon da PokéAPI... isso leva ~2min.");
    await startLoad();
  }

  // Whenever pokemon data arrives, auto-shuffle
  React.useEffect(() => {
    if (pokemon.length > 0) {
      const s = shuffle(pokemon);
      setShuffled(s);
      sorter.reset(s);
      setStatus("Pokémon carregados! Escolha um algoritmo e clique em Start.");
    }
  }, [pokemon]); // eslint-disable-line

  // ─── Shuffle ────────────────────────────────────────────────────
  function handleShuffle() {
    if (sorter.running) return;
    const s = shuffle(pokemon);
    setShuffled(s);
    sorter.reset(s);
    setStatus("Embaralhado! Pronto para ordenar.");
  }

  // ─── Start Sort ─────────────────────────────────────────────────
  async function handleStart() {
    if (pokemon.length === 0 || sorter.running) return;
    setLoadingSort(true);
    setStatus(`Gerando steps para ${ALGO_NAMES[algorithm]}...`);
    try {
      const result = await runSort(algorithm, shuffled);
      setComplexity(result.complexity);
      sorter.load(shuffled, result.steps, () => {
        setStatus(`✓ Concluído! ${(result.stats.total).toLocaleString()} operações no total.`);
      });
      setLoadingSort(false);
      setStatus(`Executando ${result.complexity.name}... ${result.total_steps.toLocaleString()} steps`);
      sorter.start();
    } catch (e) {
      setStatus(`Erro: ${e.message}`);
      setLoadingSort(false);
    }
  }

  // ─── Pause ──────────────────────────────────────────────────────
  function handlePause() {
    sorter.pause();
    setStatus(sorter.paused ? `Executando ${ALGO_NAMES[algorithm]}...` : "⏸ Pausado.");
  }

  // ─── Reset ──────────────────────────────────────────────────────
  function handleReset() {
    sorter.reset(shuffled);
    setStatus("Resetado. Pronto para ordenar.");
  }

  // ─── Speed ──────────────────────────────────────────────────────
  function handleSpeed(e) {
    const v = Number(e.target.value);
    setSpeedState(v);
    sorter.setSpeed(v);
  }

  // ─── Sound ──────────────────────────────────────────────────────
  function handleSound() {
    const next = !soundOn;
    setSoundOn(next);
    sorter.setSound(next);
  }

  const isReady    = pokemon.length > 0 && !loadingSort;
  const canStart   = isReady && !sorter.running;
  const canControl = isReady && sorter.running;

  return (
    <div style={{ fontFamily: "'Nunito', sans-serif", background: "#1a1a2e", color: "#f0f0f0", minHeight: "100vh", display: "flex", flexDirection: "column" }}>

      {/* ── Header ── */}
      <header style={{ background: "linear-gradient(135deg,#e94560 0%,#0f3460 100%)", padding: "12px 20px", display: "flex", alignItems: "center", gap: 12, borderBottom: "3px solid #f5c518" }}>
        <Pokeball size={36} />
        <div>
          <div style={{ fontFamily: "'Press Start 2P',monospace", fontSize: 11, color: "#f5c518" }}>Pokédex Sort Visualizer</div>
          <div style={{ fontSize: 11, color: "rgba(255,255,255,0.7)", marginTop: 2 }}>151 Pokémon • 5 Algoritmos • Backend Flask</div>
        </div>
      </header>

      <div style={{ display: "grid", gridTemplateColumns: "260px 1fr", flex: 1, minHeight: 0 }}>

        {/* ── Sidebar ── */}
        <aside style={{ background: "#16213e", borderRight: "1px solid rgba(255,255,255,0.08)", padding: 16, display: "flex", flexDirection: "column", gap: 16, overflowY: "auto" }}>

          {/* Load */}
          <Section title="Dados">
            {!pokeLoading && pokemon.length === 0 && (
              <Btn onClick={handleLoad} color="#22c55e" textColor="#052e16">
                ⬇ Carregar Pokémon
              </Btn>
            )}
            {pokeLoading && (
              <div>
                <div style={{ fontSize: 12, color: "#9ca3af", marginBottom: 6 }}>
                  Carregando… {pokeProgress.loaded}/{pokeProgress.total}
                </div>
                <ProgressBar value={pokeProgress.loaded} max={pokeProgress.total} color="#f5c518" />
              </div>
            )}
            {pokeError && <div style={{ color: "#f87171", fontSize: 12 }}>{pokeError}</div>}
            {pokemon.length > 0 && (
              <div style={{ fontSize: 12, color: "#4ade80", fontWeight: 700 }}>✓ {pokemon.length} Pokémon carregados</div>
            )}
          </Section>

          {/* Algorithm */}
          <Section title="Algoritmo">
            <select
              value={algorithm}
              onChange={(e) => setAlgorithm(e.target.value)}
              disabled={sorter.running}
              style={selectStyle}
            >
              {Object.entries(ALGO_NAMES).map(([k, v]) => (
                <option key={k} value={k}>{v}</option>
              ))}
            </select>
          </Section>

          {/* Controls */}
          <Section title="Controles">
            <div style={{ display: "flex", gap: 6, marginBottom: 6 }}>
              <Btn onClick={handleStart} disabled={!canStart || loadingSort} color="#22c55e" textColor="#052e16" flex>
                {loadingSort ? "..." : "▶ Start"}
              </Btn>
              <Btn onClick={handlePause} disabled={!canControl} color="#f5c518" textColor="#1c1917" flex>
                {sorter.paused ? "▶ Resume" : "⏸ Pause"}
              </Btn>
            </div>
            <div style={{ display: "flex", gap: 6 }}>
              <Btn onClick={handleReset} disabled={sorter.running && !sorter.paused} color="#e94560" textColor="white" flex>
                ↺ Reset
              </Btn>
              <Btn onClick={handleShuffle} disabled={sorter.running || !isReady} color="#a78bfa" textColor="#1e1b4b" flex>
                🔀 Shuffle
              </Btn>
            </div>
          </Section>

          {/* Speed */}
          <Section title="Velocidade">
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, color: "#9ca3af", marginBottom: 4 }}>
              <span>Delay</span><span style={{ color: "#f5c518", fontWeight: 700 }}>{speed}ms</span>
            </div>
            <input type="range" min="5" max="300" step="5" value={speed} onChange={handleSpeed} style={{ width: "100%", accentColor: "#e94560" }} />
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: "#6b7280" }}>
              <span>Rápido</span><span>Lento</span>
            </div>
          </Section>

          {/* Sound */}
          <Section title="Som">
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <span style={{ fontSize: 13, fontWeight: 600 }}>Efeitos Sonoros</span>
              <div
                onClick={handleSound}
                style={{ width: 40, height: 22, background: soundOn ? "#4ade80" : "#0f3460", borderRadius: 11, border: "1px solid rgba(255,255,255,0.15)", position: "relative", cursor: "pointer", transition: "background 0.2s" }}
              >
                <div style={{ position: "absolute", left: soundOn ? 20 : 2, top: 2, width: 16, height: 16, background: "white", borderRadius: "50%", transition: "left 0.2s" }} />
              </div>
            </div>
          </Section>

          {/* Stats */}
          <StatsPanel stats={sorter.stats} elapsed={sorter.elapsed} complexity={complexity} />

          {/* Compare */}
          <Section title="Ferramentas">
            <Btn onClick={() => setShowCompare(true)} disabled={pokemon.length === 0} color="#0f3460" textColor="#60a5fa" border="1px solid #60a5fa">
              📊 Comparar Algoritmos
            </Btn>
          </Section>

        </aside>

        {/* ── Main View ── */}
        <main style={{ background: "#1a1a2e", padding: 16, overflowY: "auto" }}>

          {/* View toggle */}
          <div style={{ display: "flex", gap: 6, marginBottom: 12 }}>
            {["bars", "cards"].map((v) => (
              <button
                key={v}
                onClick={() => setView(v)}
                style={{ padding: "6px 16px", borderRadius: 20, border: "1px solid rgba(255,255,255,0.12)", background: view === v ? "#e94560" : "#16213e", color: view === v ? "white" : "#9ca3af", fontSize: 12, fontWeight: 700, cursor: "pointer", fontFamily: "'Nunito',sans-serif" }}
              >
                {v === "bars" ? "📊 Barras" : "🃏 Cards"}
              </button>
            ))}
          </div>

          {/* Status */}
          <div style={{ fontFamily: "'Press Start 2P',monospace", fontSize: 8, color: "#f5c518", background: "#16213e", borderRadius: 6, padding: "7px 10px", marginBottom: 10, minHeight: 28 }}>
            {status}
          </div>

          {/* Progress */}
          <div style={{ marginBottom: 10 }}>
            <ProgressBar value={sorter.progress} max={100} color="linear-gradient(90deg,#e94560,#f5c518)" />
          </div>

          {/* Legend */}
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginBottom: 12, fontSize: 11, fontWeight: 600 }}>
            {[["#60a5fa","Normal"],["#fbbf24","Comparando"],["#f87171","Trocando"],["#a78bfa","Pivot"],["#4ade80","Ordenado"]].map(([c,l]) => (
              <div key={l} style={{ display: "flex", alignItems: "center", gap: 4 }}>
                <div style={{ width: 10, height: 10, borderRadius: 2, background: c }} />
                {l}
              </div>
            ))}
          </div>

          {/* Visualization */}
          {sorter.array.length === 0
            ? <EmptyState loading={pokeLoading} onLoad={handleLoad} loaded={pokemon.length > 0} />
            : view === "bars"
              ? <BarChart  array={sorter.array} highlights={sorter.highlights} sorted={sorter.sorted} />
              : <CardGrid  array={sorter.array} highlights={sorter.highlights} sorted={sorter.sorted} />
          }

        </main>
      </div>

      {showCompare && <CompareModal pokemon={pokemon} onClose={() => setShowCompare(false)} />}
    </div>
  );
}

// ── Small helper components ──────────────────────────────────────

function Section({ title, children }) {
  return (
    <div>
      <div style={{ fontSize: 9, fontWeight: 700, color: "#e94560", textTransform: "uppercase", letterSpacing: 1, marginBottom: 8, paddingBottom: 5, borderBottom: "1px solid rgba(255,255,255,0.08)", fontFamily: "'Press Start 2P',monospace" }}>
        {title}
      </div>
      {children}
    </div>
  );
}

function Btn({ children, onClick, disabled, color, textColor, flex, border }) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      style={{ flex: flex ? 1 : undefined, padding: "8px 6px", borderRadius: 8, border: border || "1px solid rgba(255,255,255,0.1)", background: disabled ? "rgba(255,255,255,0.05)" : color, color: disabled ? "#6b7280" : textColor, fontFamily: "'Nunito',sans-serif", fontSize: 12, fontWeight: 700, cursor: disabled ? "not-allowed" : "pointer", transition: "all 0.15s" }}
    >
      {children}
    </button>
  );
}

function ProgressBar({ value, max, color }) {
  const pct = max > 0 ? Math.round((value / max) * 100) : 0;
  return (
    <div style={{ height: 4, background: "#16213e", borderRadius: 2, overflow: "hidden" }}>
      <div style={{ height: "100%", width: `${pct}%`, background: color, borderRadius: 2, transition: "width 0.1s" }} />
    </div>
  );
}

function Pokeball({ size }) {
  return (
    <div style={{ width: size, height: size, background: "linear-gradient(180deg,#e94560 50%,white 50%)", borderRadius: "50%", border: "3px solid #222", position: "relative", flexShrink: 0 }}>
      <div style={{ position: "absolute", left: "50%", top: "50%", transform: "translate(-50%,-50%)", width: size * 0.28, height: size * 0.28, background: "white", borderRadius: "50%", border: "3px solid #222" }} />
    </div>
  );
}

function EmptyState({ loading, onLoad, loaded }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minHeight: 300, gap: 16 }}>
      <div style={{ animation: "spin 1s linear infinite", width: 60, height: 60, background: "linear-gradient(180deg,#e94560 50%,white 50%)", borderRadius: "50%", border: "4px solid #333", position: "relative" }}>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
        <div style={{ position: "absolute", left: "50%", top: "50%", transform: "translate(-50%,-50%)", width: 14, height: 14, background: "white", borderRadius: "50%", border: "4px solid #333" }} />
      </div>
      {loading
        ? <div style={{ fontFamily: "'Press Start 2P',monospace", fontSize: 9, color: "#f5c518" }}>Carregando Pokémon...</div>
        : !loaded
          ? <div style={{ textAlign: "center" }}>
              <div style={{ fontFamily: "'Press Start 2P',monospace", fontSize: 9, color: "#f5c518", marginBottom: 12 }}>Nenhum Pokémon carregado</div>
              <button onClick={onLoad} style={{ background: "#22c55e", color: "#052e16", border: "none", borderRadius: 8, padding: "10px 20px", fontFamily: "'Nunito',sans-serif", fontWeight: 700, fontSize: 13, cursor: "pointer" }}>
                ⬇ Carregar da PokéAPI
              </button>
            </div>
          : null
      }
    </div>
  );
}

const selectStyle = {
  width: "100%",
  background: "#0f3460",
  color: "#f0f0f0",
  border: "1px solid rgba(255,255,255,0.1)",
  borderRadius: 8,
  padding: "8px 10px",
  fontFamily: "'Nunito',sans-serif",
  fontSize: 13,
  fontWeight: 600,
  cursor: "pointer",
};
