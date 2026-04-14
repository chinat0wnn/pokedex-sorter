const BASE = "/api";

export async function loadPokemon() {
  const res = await fetch(`${BASE}/pokemon/load`, { method: "POST" });
  if (!res.ok) throw new Error("Failed to trigger load");
  return res.json();
}

export async function getPokemonProgress() {
  const res = await fetch(`${BASE}/pokemon/progress`);
  if (!res.ok) throw new Error("Failed to fetch progress");
  return res.json();
}

export async function getAllPokemon() {
  const res = await fetch(`${BASE}/pokemon/`);
  if (!res.ok) throw new Error("Pokémon not loaded yet");
  return res.json();
}

export async function getAlgorithms() {
  const res = await fetch(`${BASE}/sort/algorithms`);
  if (!res.ok) throw new Error("Failed to fetch algorithms");
  return res.json();
}

/**
 * @param {string} algorithm - bubble | selection | insertion | merge | quick
 * @param {Array}  array     - shuffled pokemon array
 * @returns {{ steps, stats, complexity, total_steps }}
 */
export async function runSort(algorithm, array) {
  const res = await fetch(`${BASE}/sort/${algorithm}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ array }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || "Sort failed");
  }
  return res.json();
}

export async function compareAlgorithms(array) {
  const res = await fetch(`${BASE}/sort/compare`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ array }),
  });
  if (!res.ok) throw new Error("Compare failed");
  return res.json();
}
