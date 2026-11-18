import { useCallback, useEffect, useState } from 'react';

// The caller memoizes loader so only a resource change, reload or poll fetches.
export function useApi(loader, { poll = 0 } = {}) {
  const [state, setState] = useState({ data: null, error: null, loader: null, tick: -1 });
  const [tick, setTick] = useState(0);
  const reload = useCallback(() => setTick((t) => t + 1), []);

  useEffect(() => {
    let alive = true;
    loader()
      .then((data) => { if (alive) setState({ data, error: null, loader, tick }); })
      .catch((error) => { if (alive) setState({ data: null, error, loader, tick }); });
    return () => { alive = false; };
  }, [loader, tick]);

  useEffect(() => {
    if (!poll) return undefined;
    const id = setInterval(() => setTick((t) => t + 1), poll);
    return () => clearInterval(id);
  }, [poll]);

  // Preserve loaded data during refreshes. A pending request shows loading only
  // when no data exists, including a retry after a failed request.
  const pending = state.loader !== loader || state.tick !== tick;
  return { data: state.data, error: state.error, loading: pending && state.data === null, reload };
}
