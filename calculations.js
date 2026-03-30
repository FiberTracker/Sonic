// calculations.js — Popup builders and overlap computation for Sonic FiberComp

function buildBdcPopup(feature, providerName, providerColor) {
  const p = feature.properties;
  const hu = p.hu100 || 0;
  const pop = p.pop100 || 0;
  const bsls = p.bsls || 0;
  const covPct = p.coveragePct || 0;
  const density = p.density || 0;
  const covColor = covPct > 80 ? '#15803D' : covPct > 40 ? '#92400E' : '#DC2626';

  return `<div style="font-family:Inter,-apple-system,sans-serif;min-width:280px;">
    <div style="font-size:10px;color:#64748B;">Census Block Group ${p.id}</div>
    <div style="font-weight:700;font-size:14px;color:${providerColor};margin-bottom:8px;">${providerName} — FCC BDC</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:8px;">
      <div style="background:#F1F5F9;padding:6px 8px;border-radius:6px;">
        <div style="font-size:9px;color:#64748B;">Housing Units</div>
        <div style="font-weight:700;font-size:16px;color:#0F172A;">${hu.toLocaleString()}</div>
      </div>
      <div style="background:#F1F5F9;padding:6px 8px;border-radius:6px;">
        <div style="font-size:9px;color:#64748B;">Population</div>
        <div style="font-weight:700;font-size:16px;color:#0F172A;">${pop.toLocaleString()}</div>
      </div>
      <div style="background:#F1F5F9;padding:6px 8px;border-radius:6px;">
        <div style="font-size:9px;color:#64748B;">FTTP BSLs</div>
        <div style="font-weight:700;font-size:16px;color:${providerColor};">${bsls.toLocaleString()}</div>
      </div>
      <div style="background:#F0FDF4;padding:6px 8px;border-radius:6px;">
        <div style="font-size:9px;color:#64748B;">Coverage</div>
        <div style="font-weight:700;font-size:16px;color:${covColor};">${covPct}%</div>
      </div>
    </div>
    <div style="font-size:9px;color:#94A3B8;margin-top:6px;">Source: FCC BDC J25 (Jun 2025) | Census 2020</div>
  </div>`;
}

function buildProfileHtml(profile, key) {
  const p = profile;
  const isSonic = key === 'sonic';

  let html = `<div class="profile-card ${isSonic ? 'profile-focus' : ''}">
    <h3 style="color:${PROVIDERS[key]?.color || '#333'};margin:0 0 12px 0;">${p.name}</h3>
    <table class="profile-table">
      <tr><td class="label">HQ</td><td>${p.hq}</td></tr>
      <tr><td class="label">Founded</td><td>${p.founded}</td></tr>
      ${p.founder ? `<tr><td class="label">Founder</td><td>${p.founder}</td></tr>` : ''}
      <tr><td class="label">Ownership</td><td>${p.ownership}</td></tr>
      ${p.ceo ? `<tr><td class="label">CEO</td><td>${p.ceo}</td></tr>` : ''}
      ${p.cfo ? `<tr><td class="label">CFO</td><td>${p.cfo}</td></tr>` : ''}
      <tr><td class="label">Technology</td><td>${p.technology}</td></tr>
      <tr><td class="label">Max Speed</td><td>${p.speeds}</td></tr>
      <tr><td class="label">Pricing</td><td>${p.pricing}</td></tr>
      ${p.subscribers ? `<tr><td class="label">Subscribers</td><td>${p.subscribers}</td></tr>` : ''}
      ${p.revenue ? `<tr><td class="label">Revenue</td><td>${p.revenue}</td></tr>` : ''}
      ${p.ebitda ? `<tr><td class="label">EBITDA</td><td>~$${p.ebitda}M <span class="source-tag">${p.ebitdaSource || ''}</span></td></tr>` : ''}
      ${p.homesPassedEst ? `<tr><td class="label">Homes Passed (Est.)</td><td>${p.homesPassedEst}</td></tr>` : ''}
      ${p.fccBdcBsls ? `<tr><td class="label">FCC BDC FTTP BSLs</td><td>${p.fccBdcBsls.toLocaleString()} <span class="source-tag">FCC BDC J25</span></td></tr>` : ''}
      <tr><td class="label">Markets</td><td>${p.markets}</td></tr>
    </table>`;

  if (isSonic && p.keyDiff) {
    html += `<div class="key-diff"><strong>Key Differentiators:</strong> ${p.keyDiff}</div>`;
  }
  if (isSonic && p.growthStrategy) {
    html += `<div class="growth-strategy"><strong>Growth Strategy:</strong> ${p.growthStrategy}</div>`;
  }
  if (isSonic && p.maActivity) {
    html += `<div class="ma-activity"><strong>M&A Activity:</strong> ${p.maActivity}</div>`;
  }
  if (isSonic && p.absHistory) {
    html += `<div class="abs-history"><strong>ABS/Securitization:</strong> ${p.absHistory}</div>`;
  }
  if (isSonic && p.beadStatus) {
    html += `<div class="bead-status"><strong>BEAD:</strong> ${p.beadStatus}</div>`;
  }

  if (p.sources) {
    html += `<div class="sources"><strong>Sources:</strong><ul>`;
    for (const s of p.sources) {
      html += `<li><a href="${s.url}" target="_blank" rel="noopener">${s.text}</a></li>`;
    }
    html += `</ul></div>`;
  }

  html += `</div>`;
  return html;
}

function buildValuationHtml() {
  const v = VALUATION_CONTEXT;
  let html = `<div class="valuation-section">
    <h3>Valuation Context</h3>
    <table class="val-table">
      <tr><td class="label">EBITDA</td><td>~$${v.sonicMetrics.ebitda}M <span class="source-tag">${v.sonicMetrics.ebitdaSource}</span></td></tr>
      <tr><td class="label">Revenue Range</td><td>$${v.sonicMetrics.revenueRange}M <span class="source-tag">${v.sonicMetrics.revenueSource}</span></td></tr>
      <tr><td class="label">Implied Valuation</td><td>$${v.sonicMetrics.impliedValue}M <span class="source-tag">${v.sonicMetrics.impliedSource}</span></td></tr>
    </table>

    <h4>Scenario Analysis (at $${v.sonicMetrics.ebitda}M EBITDA)</h4>
    <table class="scenario-table">
      <thead><tr><th>Scenario</th><th>EV ($M)</th></tr></thead>
      <tbody>`;
  for (const s of v.scenarioAnalysis) {
    html += `<tr><td>${s.label}</td><td>$${s.ev}M</td></tr>`;
  }
  html += `</tbody></table>

    <h4>Recent Fiber Comps</h4>
    <table class="comps-table">
      <thead><tr><th>Transaction</th><th>$/HHP</th><th>Multiple</th><th>Date</th></tr></thead>
      <tbody>`;
  for (const c of v.comps) {
    html += `<tr><td>${c.deal}</td><td>${c.dollarPerHhp ? '$' + c.dollarPerHhp.toLocaleString() : '—'}</td><td>${c.multiple}</td><td>${c.date}</td></tr>`;
  }
  html += `</tbody></table>
    <div class="val-note">Note: Fiber platform valuations have ranged 8-12x EBITDA for scaled operators. At $80M EBITDA, the $475M Getlatka figure implies ~6x — below market, suggesting either stale data or a pre-expansion valuation. All financials are third-party estimates for a private company.</div>
  </div>`;
  return html;
}

function buildCompMatrixHtml() {
  const m = COMP_MATRIX;
  let html = `<table class="comp-matrix"><thead><tr>`;
  for (const h of m.headers) {
    html += `<th>${h}</th>`;
  }
  html += `</tr></thead><tbody>`;
  for (const row of m.rows) {
    html += `<tr>`;
    for (let i = 0; i < row.length; i++) {
      html += i === 0 ? `<td class="label">${row[i]}</td>` : `<td>${row[i]}</td>`;
    }
    html += `</tr>`;
  }
  html += `</tbody></table>`;
  return html;
}

function buildExecHtml() {
  let html = `<div class="exec-section"><h3>Key Executives</h3><table class="exec-table">
    <thead><tr><th>Name</th><th>Title</th><th>Notes</th></tr></thead><tbody>`;
  for (const e of KEY_EXECUTIVES) {
    html += `<tr><td><strong>${e.name}</strong></td><td>${e.title}</td><td>${e.note}</td></tr>`;
  }
  html += `</tbody></table></div>`;
  return html;
}
