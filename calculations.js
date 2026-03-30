// calculations.js — Popup builders for Sonic FiberComp
// Compact property names: b=bsls, h=hu100, p=pop100, c=coveragePct

function buildBdcPopup(feature, providerName, providerColor) {
  const p = feature.properties;
  const hu = p.h || p.hu100 || 0;
  const pop = p.p || p.pop100 || 0;
  const bsls = p.b || p.bsls || 0;
  const covPct = p.c || p.coveragePct || 0;
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
