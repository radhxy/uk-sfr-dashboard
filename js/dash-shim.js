// Stand-in for the claude.ai dashboard runtime: loads the JSON files in data/,
// runs calculations, and keeps filter state in memory.
(function () {
  const DATASETS = window.SFR_DATASETS;
  const store = {}, calcs = {}, calcCache = {};
  const callbacks = [];
  const defaults = { region: 'All', developer: 'All' };
  let params = { ...defaults };
  const run = () => { for (const f of callbacks) { try { f(); } catch (e) { console.error(e); } } };
  function load(id) {
    if (store[id]) return;
    store[id] = { status: 'loading', data: [] };
    fetch('data/' + DATASETS[id].file)
      .then((r) => { if (!r.ok) throw new Error(r.status + ' ' + r.statusText); return r.json(); })
      .then((rows) => { store[id] = { status: 'ok', data: rows }; for (const k in calcCache) delete calcCache[k]; run(); })
      .catch((e) => { store[id] = { status: 'error', data: [], message: e.message }; run(); });
  }
  function data(id) {
    if (calcs[id]) {
      const ins = calcs[id].inputs.map(data);
      const bad = ins.find((d) => d.status !== 'ok');
      if (bad) return { status: bad.status, data: [] };
      if (!calcCache[id]) {
        try { calcCache[id] = { status: 'ok', data: calcs[id].fn(...ins.map((d) => d.data)) }; }
        catch (e) { console.error(e); calcCache[id] = { status: 'error', data: [], message: e.message }; }
      }
      return calcCache[id];
    }
    if (!DATASETS[id]) return { status: 'missing', data: [] };
    load(id);
    return store[id];
  }
  let w = window.innerWidth, t;
  window.addEventListener('resize', () => { if (window.innerWidth === w) return; w = window.innerWidth; clearTimeout(t); t = setTimeout(run, 150); });
  window.dash = {
    colors: ['var(--series-1)', 'var(--series-2)', 'var(--series-3)', 'var(--series-4)', 'var(--series-5)', 'var(--series-6)', 'var(--series-7)', 'var(--series-8)'],
    data, calc: (id, o) => { calcs[id] = o; }, loader() {},
    onData: (f) => { callbacks.push(f); f(); },
    params: () => ({ ...params }),
    setParams: (o) => { params = { ...params, ...o }; run(); },
    resetParams: () => { params = { ...defaults }; run(); },
    refresh() {},
    setLink: (name) => { try { history.replaceState(null, '', '#' + name); } catch (e) { /* ignore */ } },
  };
})();
