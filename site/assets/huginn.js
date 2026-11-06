// Huginn report renderer. Loads a report JSON (schema v1) and renders map + grid + detail.
// ?r=<run-id> loads reports/<run-id>.json, otherwise reports/latest.json.
(function () {
  'use strict';

  const STALE_HOURS = 14;
  const SHOW_MAP = false; // hidden for now; set true to bring the map back
  const RATING_LABEL = { go: 'Go', marginal: 'Marginal', nogo: 'No-go', unknown: '?' };
  const RATING_COLOR = { go: '#16a34a', marginal: '#d97706', nogo: '#dc2626', unknown: '#94a3b8' };
  const CHECK_LABEL = { pass: 'Pass', warn: 'Warn', fail: 'Fail', na: 'N/A' };

  const app = document.getElementById('app');
  const dialog = document.getElementById('detail');
  const dialogBody = document.getElementById('detail-body');

  let report = null;
  let groupIdx = 0;
  let map = null;

  // ---------- helpers ----------
  const esc = (v) => String(v ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const safeUrl = (u) => (/^https?:\/\//i.test(u || '') ? esc(u) : '#');
  const rating = (r) => (r in RATING_LABEL ? r : 'unknown');
  const isPast = (slot) => !!slot.ends_at && new Date(slot.ends_at).getTime() < Date.now();

  function spotSubtitle(spot) {
    const a = spot.flyable_arc_deg;
    const arc = a ? `wind ${a[0]}°–${a[1]}°` : '';
    return [spot.face_deg != null ? `faces ${spot.face_deg}°` : '', arc].filter(Boolean).join(' · ');
  }

  // " 07:02–12:00" in the report's time zone; AM runs sunrise–12:00, PM 12:00–sunset.
  function slotHours(slot) {
    if (!slot.starts_at || !slot.ends_at) return '';
    const t = (iso) => fmtLocal(iso, report.timezone, { hour: '2-digit', minute: '2-digit', hourCycle: 'h23' });
    return ` ${t(slot.starts_at)}–${t(slot.ends_at)}`;
  }

  // Winds aloft are labeled above landing, so say how high the launch is above it.
  function launchHeight(spot) {
    if (spot.elevation_ft == null) return '';
    const fmt = (n) => Math.round(n).toLocaleString('en-US');
    if (spot.landing_elevation_ft == null) return ` · launch ${fmt(spot.elevation_ft)} ft`;
    const above = Math.round((spot.elevation_ft - spot.landing_elevation_ft) / 10) * 10;
    return ` · launch ${fmt(above)} ft above landing (${fmt(spot.elevation_ft)} ft)`;
  }

  function speed(s) {
    if (s == null) return '';
    return Array.isArray(s) ? (s[0] === s[1] ? `${s[0]}` : `${s[0]}–${s[1]}`) : `${s}`;
  }
  const maxOf = (s) => (s == null ? null : Array.isArray(s) ? Math.max(...s) : s);
  const CALM_KT = 3;
  const WINDY_KT = 15;
  const isCalm = (w) => maxOf(w.speed_kt) != null && maxOf(w.speed_kt) <= CALM_KT && (maxOf(w.gust_kt) ?? 0) <= CALM_KT;

  // Arrow points the way the wind blows (downwind), like a streamline on a wind map.
  function arrow(dirDeg) {
    if (dirDeg == null) return '';
    return `<svg class="arrow" viewBox="0 0 16 16" aria-hidden="true" style="transform:rotate(${(dirDeg + 180) % 360}deg)">
      <path d="M8 1.5 13 8h-3.2v6.5H6.2V8H3z" fill="currentColor"/></svg>`;
  }
  // Full wind: arrow, degrees (from), speed, gust. No compass letters — the degrees say it.
  function windText(w) {
    if (!w) return '—';
    if (w.text) return esc(w.text);
    if (w.dir_deg == null && w.speed_kt == null) return '—';
    if (isCalm(w)) return 'calm';
    const dir = w.dir_deg != null ? `${w.dir_deg}° ` : '';
    const gust = w.gust_kt != null ? ` G${speed(w.gust_kt)}` : '';
    return `<span class="wind" title="${w.dir_deg != null ? `from ${w.dir_deg}°` : ''}">${arrow(w.dir_deg)} ${dir}${speed(w.speed_kt)} kt${gust}</span>`;
  }
  // Compact wind for table cells: arrow + speed range (+ gust), units in the legend.
  function windShort(w) {
    if (!w || (w.dir_deg == null && w.speed_kt == null)) return '';
    if (isCalm(w)) return '<span class="wind calm">calm</span>';
    const top = Math.max(maxOf(w.speed_kt) ?? 0, maxOf(w.gust_kt) ?? 0);
    const gust = w.gust_kt != null ? ` G${speed(w.gust_kt)}` : '';
    return `<span class="wind${top >= WINDY_KT ? ' windy' : ''}">${arrow(w.dir_deg)}${speed(w.speed_kt)}${gust}</span>`;
  }
  function links(list) {
    if (!list || !list.length) return '';
    return `<div class="links">${list.map((l) => `<a href="${safeUrl(l.url)}" target="_blank" rel="noopener">${esc(l.label)}</a>`).join('')}</div>`;
  }
  function fmtLocal(iso, tz, opts) {
    try {
      return new Intl.DateTimeFormat('en-US', { timeZone: tz, ...opts }).format(new Date(iso));
    } catch (e) { return iso; }
  }
  function ago(iso) {
    const h = (Date.now() - new Date(iso).getTime()) / 36e5;
    if (h < 1) return `${Math.max(1, Math.round(h * 60))} min ago`;
    if (h < 48) return `${Math.round(h)} h ago`;
    return `${Math.round(h / 24)} days ago`;
  }

  // ---------- loading ----------
  async function load() {
    const params = new URLSearchParams(location.search);
    const runId = params.get('r');
    const path = runId && /^[\w-]+$/.test(runId) ? `reports/${runId}.json` : 'reports/latest.json';
    try {
      const res = await fetch(path, { cache: 'no-cache' });
      if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
      report = await res.json();
    } catch (e) {
      app.innerHTML = `<div class="card"><b>No report available.</b><p class="muted">Could not load ${esc(path)}: ${esc(e.message)}</p></div>`;
      return;
    }
    report._archived = !!runId;
    const gParam = params.get('g');
    const gi = (report.groups || []).findIndex((g) => g.id === gParam);
    groupIdx = gi >= 0 ? gi : 0;
    render();
    loadHistory();
    openFromHash();
  }

  async function loadHistory() {
    const el = document.getElementById('history');
    if (!el) return;
    try {
      const res = await fetch('reports/index.json', { cache: 'no-cache' });
      if (!res.ok) throw new Error(res.statusText);
      const idx = await res.json();
      const tz = report.timezone;
      el.querySelector('ul').innerHTML = (idx.reports || []).slice(0, 60).map((r) => {
        const cur = r.id === report.id ? ' class="cur"' : '';
        const when = fmtLocal(r.generated_at, tz, { weekday: 'short', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit' });
        return `<li${cur}><a href="?r=${encodeURIComponent(r.id)}">${esc(when)}</a><span class="muted">${esc(r.summary || '')}</span></li>`;
      }).join('') || '<li class="muted">No archived reports yet.</li>';
    } catch (e) {
      el.querySelector('ul').innerHTML = '<li class="muted">History unavailable.</li>';
    }
  }

  // ---------- render ----------
  function render() {
    const r = report;
    const tz = r.timezone || 'UTC';
    const group = r.groups[groupIdx];
    document.getElementById('activity').textContent = r.activity ? r.activity[0].toUpperCase() + r.activity.slice(1) : '';
    document.title = `Huginn — ${group ? group.name : ''}`;

    const hours = (Date.now() - new Date(r.generated_at).getTime()) / 36e5;
    const when = fmtLocal(r.generated_at, tz, { weekday: 'short', month: 'short', day: 'numeric', hour: 'numeric', minute: '2-digit', timeZoneName: 'short' });

    const banners = [
      r.sample ? '<div class="banner sample">Sample data — layout preview, not a real forecast.</div>' : '',
      r._archived ? `<div class="banner archive">Archived report. <a href="./">Go to the latest →</a></div>` : '',
      !r._archived && hours > STALE_HOURS ? `<div class="banner stale">This report is ${Math.round(hours)} h old. Conditions have changed — do not rely on it.</div>` : '',
    ].join('');

    // Group selector only once there is more than one group.
    const tabs = r.groups.length > 1
      ? `<div class="tabs" role="tablist">${r.groups.map((g, i) => `<button class="tab" role="tab" aria-selected="${i === groupIdx}" data-group="${i}">${esc(g.name)}</button>`).join('')}</div>`
      : '';

    app.innerHTML = `
      <div class="meta">
        <span class="label">Report generated</span>
        <span class="when">${esc(when)}</span>
        <span class="ago">${esc(ago(r.generated_at))}</span>
      </div>
      ${banners}
      ${tabs}
      ${renderGrid(group)}
      ${SHOW_MAP ? '<div id="map" aria-label="Map of spots"></div>' : ''}
      ${renderSynoptic(group)}
      ${renderObs(group)}
      ${renderSources(r)}
      <section class="card history" id="history">
        <h2 class="card-title">History</h2>
        <ul><li class="muted">Loading…</li></ul>
      </section>`;

    app.querySelectorAll('[data-group]').forEach((b) => b.addEventListener('click', () => {
      groupIdx = Number(b.dataset.group);
      const u = new URL(location.href); u.searchParams.set('g', r.groups[groupIdx].id); u.hash = '';
      history.replaceState(null, '', u);
      render(); loadHistory();
    }));
    app.querySelectorAll('.cell').forEach((c) => c.addEventListener('click', () => openDetail(c.dataset.spot, c.dataset.slot)));
    if (SHOW_MAP) renderMap(group);
  }

  function renderGrid(group) {
    const slots = report.slots;
    // Columns are grouped by day: one day header spanning its AM/PM, a divider before each day.
    const days = [];
    slots.forEach((s) => {
      const last = days[days.length - 1];
      if (last && last.date === s.date) last.slots.push(s); else days.push({ date: s.date, slots: [s] });
    });
    const dayStart = new Set(days.map((d) => d.slots[0].id));
    const colClass = (s) => [dayStart.has(s.id) ? 'day-start' : '', isPast(s) ? 'past' : ''].join(' ').trim();
    // Noon UTC keeps the calendar date stable in any US time zone.
    const dateOf = (d, opts) => fmtLocal(`${d}T12:00:00Z`, 'UTC', opts);

    // Header tooltips are CSS (data-tip), not title=: native tooltips are slow and absent on touch.
    const dayRow = days.map((d) => `<th class="day-start" colspan="${d.slots.length}" scope="colgroup">
        <span class="tip" tabindex="0" data-tip="${esc(dateOf(d.date, { weekday: 'long', month: 'long', day: 'numeric', year: 'numeric' }))}">
        ${esc(dateOf(d.date, { weekday: 'short' }))} <span class="date">${esc(dateOf(d.date, { month: 'short', day: 'numeric' }))}</span></span></th>`).join('');
    const partRow = slots.map((s) => `<th class="part ${colClass(s)}" scope="col">
        <span class="tip" tabindex="0" data-tip="${s.part === 'am' ? 'Morning' : 'Afternoon/evening'}${slotHours(s)} · ${s.basis === 'forecast+obs' ? 'forecast + current observations' : 'forecast only'}${isPast(s) ? ' · already over' : ''}">
        ${esc(s.part === 'am' ? 'AM' : 'PM')}${s.basis === 'forecast+obs' ? ' ●' : ''}</span></th>`).join('');

    const rows = group.spots.map((spot) => {
      const cells = slots.map((s) => {
        const c = (spot.cells || {})[s.id];
        if (!c) return `<td class="${colClass(s)}"><span class="cell r-unknown"><span class="pct">–</span></span></td>`;
        const rt = rating(c.rating);
        const nWarn = (c.warnings || []).filter((w) => w.severity !== 'info').length;
        const abort = (c.warnings || []).some((w) => w.severity === 'abort');
        return `<td class="${colClass(s)}"><button class="cell r-${rt}" data-spot="${esc(spot.id)}" data-slot="${esc(s.id)}"
            aria-label="${esc(spot.name)} ${esc(s.label)}: ${esc(RATING_LABEL[rt])}, ${c.chance ?? '?'} percent">
          <span class="pct">${c.chance != null ? esc(c.chance) + '%' : '?'}</span>
          <span class="lbl">${esc(RATING_LABEL[rt])}</span>
          <span class="cell-foot">${abort ? '⛔' : nWarn ? '⚠' : ''}${windShort((c.wind || {}).launch)}</span>
        </button></td>`;
      }).join('');
      return `<tr id="row-${esc(spot.id)}"><th class="spot" scope="row">${esc(spot.name)}<span class="faces">${esc(spotSubtitle(spot))}</span></th>${cells}</tr>`;
    }).join('');
    return `
      <div class="grid-wrap"><table class="grid">
        <thead>
          <tr><th class="spot" scope="col" rowspan="2">Spot</th>${dayRow}</tr>
          <tr>${partRow}</tr>
        </thead>
        <tbody>${rows}</tbody>
      </table></div>
      <div class="legend">
        <span><i class="sw" style="background:${RATING_COLOR.go}"></i>Go</span>
        <span><i class="sw" style="background:${RATING_COLOR.marginal}"></i>Marginal</span>
        <span><i class="sw" style="background:${RATING_COLOR.nogo}"></i>No-go</span>
        <span>% = est. chance the spot's criteria are met</span>
        <span>● = includes current observations</span>
        <span>Faded = already over</span>
        <span>⚠ warnings · ⛔ abort trigger</span>
        <span>${arrow(180)} wind at launch, kt — arrow points where it blows (this one: from the south)</span>
      </div>`;
  }

  function renderSynoptic(group) {
    const s = group.synoptic;
    if (!s) return '';
    const p = s.pressure;
    return `<section class="card">
      <h2 class="card-title">Big picture</h2>
      ${p ? `<p><span class="pressure">${esc((p.system || '').toUpperCase())}${p.value_mb ? ' · ' + esc(p.value_mb) + ' mb' : ''}${p.trend ? ' · ' + esc(p.trend) : ''}</span>${esc(p.significance || '')}</p>` : ''}
      <p>${esc(s.summary)}</p>
      ${s.afd_excerpt ? `<blockquote>“${esc(s.afd_excerpt)}” <br><small>— NWS Area Forecast Discussion</small></blockquote>` : ''}
      ${links(s.links)}
    </section>`;
  }

  function renderObs(group) {
    const o = group.observations;
    if (!o) return '';
    const tz = report.timezone;
    return `<section class="card">
      <h2 class="card-title">Current observations${o.as_of ? ` <span class="muted">${esc(fmtLocal(o.as_of, tz, { hour: 'numeric', minute: '2-digit' }))}</span>` : ''}</h2>
      ${o.summary ? `<p>${esc(o.summary)}</p>` : ''}
      <div class="chips">${(o.stations || []).map((st) => `
        <a class="chip" href="${safeUrl(st.url)}" target="_blank" rel="noopener"><b>${esc(st.id)} · ${esc(st.name)}</b><span>${st.wind ? windText(st.wind) : ''}${st.wind && st.summary ? ' · ' : ''}${esc(st.summary || (st.wind ? '' : 'view chart ↗'))}</span></a>`).join('')}
      </div>
      ${links(o.links)}
    </section>`;
  }

  function renderSources(r) {
    if (!r.sources || !r.sources.length) return '';
    return `<details class="card">
      <summary class="card-title" style="cursor:pointer">Data fetched for this report (${r.sources.length})</summary>
      <p class="muted">Everything the agent downloaded for this run — forecasts, winds aloft, airport forecasts and
      station observations — and whether each fetch worked.</p>
      <ul class="checks">${r.sources.map((s) => `
        <li><span class="res ${s.ok === false ? 'res-fail' : 'res-pass'}">${s.ok === false ? 'Fail' : 'OK'}</span>
        <span><a href="${safeUrl(s.url)}" target="_blank" rel="noopener">${esc(s.label)}</a>
        <span class="detail">${s.fetched_at ? esc(fmtLocal(s.fetched_at, r.timezone, { hour: 'numeric', minute: '2-digit' })) : ''}</span></span></li>`).join('')}
      </ul>
    </details>`;
  }

  function renderMap(group) {
    if (map) { map.remove(); map = null; }
    const el = document.getElementById('map');
    if (!window.L || !el) { if (el) el.remove(); return; }
    const pts = group.spots.filter((s) => s.lat != null && s.lon != null);
    if (!pts.length) { el.remove(); return; }
    map = L.map(el, { scrollWheelZoom: false });
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 17, attribution: '&copy; OpenStreetMap contributors',
    }).addTo(map);
    const first = report.slots[0].id;
    pts.forEach((s) => {
      const c = (s.cells || {})[first] || {};
      const icon = L.divIcon({ className: '', html: `<div class="pin" style="background:${RATING_COLOR[rating(c.rating)]}"></div>`, iconSize: [18, 18] });
      L.marker([s.lat, s.lon], { icon, title: s.name }).addTo(map)
        .bindTooltip(`${s.name} · ${RATING_LABEL[rating(c.rating)]}`, { direction: 'top', offset: [0, -8] })
        .on('click', () => {
          const row = document.getElementById(`row-${s.id}`);
          if (!row) return;
          row.scrollIntoView({ behavior: 'smooth', block: 'center' });
          row.classList.add('flash'); setTimeout(() => row.classList.remove('flash'), 1200);
        });
    });
    const bounds = L.latLngBounds(pts.map((s) => [s.lat, s.lon])).pad(0.6);
    map.fitBounds(bounds, { maxZoom: 13 });
    // The container may not have its final size yet on first paint; refit once laid out.
    requestAnimationFrame(() => { if (map) { map.invalidateSize(); map.fitBounds(bounds, { maxZoom: 13 }); } });
  }

  // ---------- detail ----------
  function openDetail(spotId, slotId, fromHash) {
    const group = report.groups[groupIdx];
    const spot = group.spots.find((s) => s.id === spotId);
    const slot = report.slots.find((s) => s.id === slotId);
    const c = spot && slot && (spot.cells || {})[slotId];
    if (!c) return;
    const rt = rating(c.rating);
    const w = c.wind || {};

    dialogBody.innerHTML = `
      <div class="detail-head">
        <div><h2 id="detail-title">${esc(spot.name)} · ${esc(slot.label)}</h2>
          <div class="sub">${esc(spotSubtitle(spot))}${launchHeight(spot)} ·${slot.basis === 'forecast+obs' ? 'forecast + current obs' : 'forecast only'}</div></div>
        <button class="close" type="button" aria-label="Close">×</button>
      </div>
      <div class="verdict r-${rt}">
        <div class="pct">${c.chance != null ? esc(c.chance) + '%' : '?'}</div>
        <div><div class="headline">${esc(RATING_LABEL[rt])} — ${esc(c.headline || '')}</div>
          <div class="small">${c.window ? 'Window ' + esc(c.window) + ' · ' : ''}data confidence: ${esc(c.confidence || 'unknown')}</div></div>
      </div>
      <div class="kv">
        <div><small>Wind at launch (est.)</small>${windText(w.launch)}</div>
        ${(w.aloft || []).map((a) => `<div><small>${esc(a.level)}</small>${windText(a)}</div>`).join('')}
      </div>
      ${(c.warnings || []).length ? `<h3>Warnings</h3>${c.warnings.map(renderWarning).join('')}` : ''}
      ${c.explanation ? `<h3>Why</h3><div class="explanation">${esc(c.explanation)}</div>` : ''}
      ${(c.checks || []).length ? `<h3>Rule checks</h3><ul class="checks">${c.checks.map((k) => `
        <li><span class="res res-${esc(k.result)}">${esc(CHECK_LABEL[k.result] || k.result)}</span>
        <span>${esc(k.rule)}<span class="detail">${esc(k.detail || '')}</span></span></li>`).join('')}</ul>` : ''}
      ${(c.sources || []).length ? `<h3>Sources</h3>${links(c.sources)}` : ''}
      ${(spot.links || []).length ? `<h3>Site info</h3>${links(spot.links)}` : ''}`;

    dialogBody.querySelector('.close').addEventListener('click', () => dialog.close());
    if (!fromHash) history.replaceState(null, '', `#${spotId}/${slotId}`);
    if (!dialog.open) dialog.showModal();
    dialogBody.scrollTop = 0;
  }

  function renderWarning(w) {
    const sev = ['abort', 'caution', 'info'].includes(w.severity) ? w.severity : 'caution';
    const icon = sev === 'abort' ? '⛔' : sev === 'info' ? 'ℹ' : '⚠';
    return `<div class="warning ${sev}"><b>${icon} ${esc(w.title)}</b>
      <dl>
        ${w.why ? `<dt>Why</dt><dd>${esc(w.why)}</dd>` : ''}
        ${w.triggered_by ? `<dt>Data</dt><dd>${esc(w.triggered_by)}</dd>` : ''}
        ${w.investigate ? `<dt>Check</dt><dd>${esc(w.investigate)}</dd>` : ''}
      </dl></div>`;
  }

  function openFromHash() {
    const m = location.hash.match(/^#([\w-]+)\/([\w-]+)$/);
    if (m) openDetail(m[1], m[2], true);
  }

  dialog.addEventListener('close', () => {
    if (/^#[\w-]+\/[\w-]+$/.test(location.hash)) history.replaceState(null, '', location.pathname + location.search);
  });
  dialog.addEventListener('click', (e) => { if (e.target === dialog) dialog.close(); });
  window.addEventListener('hashchange', openFromHash);

  // ---------- theme toggle ----------
  const themeBtn = document.getElementById('theme-btn');
  const systemDark = window.matchMedia('(prefers-color-scheme: dark)');
  const currentTheme = () => document.documentElement.dataset.theme || (systemDark.matches ? 'dark' : 'light');
  function syncThemeBtn() {
    if (!themeBtn) return;
    const dark = currentTheme() === 'dark';
    themeBtn.textContent = dark ? '☀' : '☾';
    themeBtn.setAttribute('aria-label', dark ? 'Switch to light theme' : 'Switch to dark theme');
    themeBtn.title = themeBtn.getAttribute('aria-label');
  }
  // Guarded: a cached older index.html may not have the button.
  if (themeBtn) themeBtn.addEventListener('click', () => {
    const next = currentTheme() === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem('huginn-theme', next); } catch (e) { /* storage blocked */ }
    syncThemeBtn();
  });
  systemDark.addEventListener('change', syncThemeBtn);
  syncThemeBtn();

  // ---------- first-visit acknowledgement ----------
  const ack = document.getElementById('ack');
  let acked = false;
  try { acked = localStorage.getItem('huginn-ack') === '1'; } catch (e) { /* storage blocked */ }
  if (!acked) {
    ack.hidden = false;
    document.getElementById('ack-btn').addEventListener('click', () => {
      try { localStorage.setItem('huginn-ack', '1'); } catch (e) { /* ignore */ }
      ack.hidden = true;
    });
  }

  load();
})();
