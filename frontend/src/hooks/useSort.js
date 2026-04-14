import { useState, useRef, useCallback, useEffect } from "react";

export function useSort() {
  const [array,      setArray]      = useState([]);
  const [highlights, setHighlights] = useState({});
  const [sorted,     setSorted]     = useState(new Set());
  const [running,    setRunning]    = useState(false);
  const [paused,     setPaused]     = useState(false);
  const [stats,      setStats]      = useState({ compares: 0, swaps: 0, writes: 0 });
  const [elapsed,    setElapsed]    = useState(0);
  const [progress,   setProgress]   = useState(0);

  const stepsRef      = useRef([]);
  const stepIdxRef    = useRef(0);
  const arrayRef      = useRef([]);
  const timeoutRef    = useRef(null);
  const startTimeRef  = useRef(null);
  const timerRef      = useRef(null);
  const speedRef      = useRef(50);
  const pausedRef     = useRef(false);
  const statsRef      = useRef({ compares: 0, swaps: 0, writes: 0 });
  const onDoneRef     = useRef(null);
  const soundRef      = useRef({ on: false, ctx: null });

  // keep pausedRef in sync
  useEffect(() => { pausedRef.current = paused; }, [paused]);

  const playSound = useCallback((id) => {
    const s = soundRef.current;
    if (!s.on) return;
    if (!s.ctx) s.ctx = new (window.AudioContext || window.webkitAudioContext)();
    try {
      const osc  = s.ctx.createOscillator();
      const gain = s.ctx.createGain();
      osc.connect(gain);
      gain.connect(s.ctx.destination);
      osc.frequency.value = 100 + (id / 151) * 800;
      osc.type = "sine";
      gain.gain.setValueAtTime(0.08, s.ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, s.ctx.currentTime + 0.08);
      osc.start();
      osc.stop(s.ctx.currentTime + 0.08);
    } catch (_) {}
  }, []);

  const applyStep = useCallback((step) => {
    const arr = [...arrayRef.current];
    const hl  = {};
    const st  = { ...statsRef.current };

    if (step.type === "compare") {
      st.compares++;
      hl.comparing = step.indices;
    } else if (step.type === "swap") {
      st.swaps++;
      hl.swapping = step.indices;
      [arr[step.indices[0]], arr[step.indices[1]]] = [arr[step.indices[1]], arr[step.indices[0]]];
      playSound(arr[step.indices[0]].id);
    } else if (step.type === "overwrite") {
      st.writes++;
      hl.swapping = [step.index, step.index];
      arr[step.index] = { ...step.value };
    } else if (step.type === "pivot") {
      hl.pivot = step.index;
    } else if (step.type === "sorted") {
      setSorted((prev) => new Set([...prev, step.index]));
    }

    statsRef.current = st;
    arrayRef.current = arr;
    setArray([...arr]);
    setHighlights(hl);
    setStats({ ...st });
  }, [playSound]);

  const tick = useCallback(() => {
    if (pausedRef.current) return;
    if (stepIdxRef.current >= stepsRef.current.length) {
      // finished
      setRunning(false);
      setHighlights({});
      setSorted(new Set(arrayRef.current.map((_, i) => i)));
      setProgress(100);
      clearInterval(timerRef.current);
      if (onDoneRef.current) onDoneRef.current();
      return;
    }
    const step = stepsRef.current[stepIdxRef.current++];
    applyStep(step);
    setProgress(Math.round((stepIdxRef.current / stepsRef.current.length) * 100));
    timeoutRef.current = setTimeout(tick, speedRef.current);
  }, [applyStep]);

  const load = useCallback((pokemon, steps, onDone) => {
    clearTimeout(timeoutRef.current);
    clearInterval(timerRef.current);

    stepsRef.current   = steps;
    stepIdxRef.current = 0;
    arrayRef.current   = [...pokemon];
    statsRef.current   = { compares: 0, swaps: 0, writes: 0 };
    onDoneRef.current  = onDone;

    setArray([...pokemon]);
    setSorted(new Set());
    setHighlights({});
    setStats({ compares: 0, swaps: 0, writes: 0 });
    setElapsed(0);
    setProgress(0);
  }, []);

  const start = useCallback(() => {
    setRunning(true);
    setPaused(false);
    pausedRef.current = false;
    startTimeRef.current = Date.now();

    timerRef.current = setInterval(() => {
      if (!pausedRef.current) setElapsed(Date.now() - startTimeRef.current);
    }, 100);

    tick();
  }, [tick]);

  const pause = useCallback(() => {
    setPaused((p) => {
      const next = !p;
      pausedRef.current = next;
      if (!next) tick(); // resume
      return next;
    });
  }, [tick]);

  const reset = useCallback((baseArray) => {
    clearTimeout(timeoutRef.current);
    clearInterval(timerRef.current);
    setRunning(false);
    setPaused(false);
    pausedRef.current  = false;
    stepsRef.current   = [];
    stepIdxRef.current = 0;
    statsRef.current   = { compares: 0, swaps: 0, writes: 0 };
    if (baseArray) {
      arrayRef.current = [...baseArray];
      setArray([...baseArray]);
    }
    setSorted(new Set());
    setHighlights({});
    setStats({ compares: 0, swaps: 0, writes: 0 });
    setElapsed(0);
    setProgress(0);
  }, []);

  const setSpeed = useCallback((ms) => { speedRef.current = ms; }, []);
  const setSound = useCallback((on) => { soundRef.current.on = on; }, []);

  return {
    array, highlights, sorted, running, paused,
    stats, elapsed, progress,
    load, start, pause, reset, setSpeed, setSound,
  };
}
