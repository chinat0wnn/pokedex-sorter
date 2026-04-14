import { useState, useEffect, useRef } from "react";
import { loadPokemon, getPokemonProgress, getAllPokemon } from "../services/api";

export function usePokemon() {
  const [pokemon,  setPokemon]  = useState([]);
  const [loading,  setLoading]  = useState(false);
  const [progress, setProgress] = useState({ loaded: 0, total: 151, done: false });
  const [error,    setError]    = useState(null);
  const pollRef = useRef(null);

  async function start() {
    setLoading(true);
    setError(null);
    try {
      await loadPokemon();
      pollRef.current = setInterval(async () => {
        try {
          const prog = await getPokemonProgress();
          setProgress(prog);
          if (prog.done) {
            clearInterval(pollRef.current);
            const data = await getAllPokemon();
            setPokemon(data);
            setLoading(false);
          }
        } catch (e) {
          setError("Erro ao verificar progresso.");
          clearInterval(pollRef.current);
          setLoading(false);
        }
      }, 500);
    } catch (e) {
      setError("Erro ao iniciar carregamento.");
      setLoading(false);
    }
  }

  useEffect(() => () => clearInterval(pollRef.current), []);

  return { pokemon, loading, progress, error, start };
}
