window.__app = "v13";
const $ = s => document.querySelector(s);
const KINDS = [["compute","Compute"],["storage","Storage"],["rete","Rete"],["gpu","GPU"],["licenza","Licenze"]];
const TIERS = [2, 4, 8, 16];
const TERMS = [["od","On-demand"],["1y","Impegno 1 anno"],["3y","Impegno 3 anni"]];
const TL = {"1y":"impegno 1 anno","3y":"impegno 3 anni"};
const GROUPS = [
  ["Hyperscaler", [["AWS","aws"],["Azure","azure"],["GCP","gcp"],["Oracle Cloud","oracle"]]],
  ["Europei", [["OVHcloud","ovh"],["Hetzner","hetzner"],["Scaleway","scaleway"],["STACKIT","stackit"],["IONOS","ionos"]]],
  ["Italiani", [["Aruba Cloud","aruba"],["Seeweb","seeweb"],["Fastweb","fastweb"],["Noovle","noovle"]]],
  ["Altri", [["Vultr","vultr"],["Akamai Linode","linode"]]],
  ["Virtualizzazione", [["Proxmox VE","proxmox"],["VMware","vmware"],["Nutanix","nutanix"]]]
];
const HELP = {
  GCP: "Mancano i dati perché non è impostato il secret GCP_API_KEY: serve una chiave API di Google (Cloud Billing API) da salvare nei secret del repository GitHub.",
  Fastweb: "Nessun listino pubblico: si vende su preventivo. Compila manual/fastweb.yml quando hai un'offerta.",
  Noovle: "Nessun listino pubblico: si vende su preventivo. Compila manual/noovle.yml quando hai un'offerta.",
  Nutanix: "Nessun listino pubblico. Compila le voci in manual/onprem.yml."
};

const S = { view: "compare", kind: "compute", term: "od", ratio: 4, sort: 4, pv: "", recs: [], series: {}, status: {}, updated: "" };

const num = (n, d = 2) => n.toLocaleString("it-IT", { minimumFractionDigits: d, maximumFractionDigits: d });
const eur = n => num(n, n >= 100 ? 0 : 2);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const initials = n => n.replace(/[^A-Za-z0-9 ]/g, "").split(/\s+/).filter(Boolean).map(w => w[0]).join("").slice(0, 2).toUpperCase();
const mono = (n, sz = "") => `<i class="mono ${sz}">${esc(initials(n))}</i>`;
const termOf = r => r.term || "od";
const isObj = r => /object|s3|blob|cloud storage/i.test(r.sku);
const KEYOF = Object.fromEntries(GROUPS.flatMap(([, l]) => l));

async function load() {
  const j = u => fetch(u, { cache: "no-cache" }).then(r => r.ok ? r.json() : null).catch(() => null);
  const [l, s, st] = await Promise.all([j("data/latest.json"), j("data/series.json"), j("data/status.json")]);
  S.recs = l?.records || []; S.updated = l?.updated || ""; S.series = s || {}; S.status = st || {};
  readHash(); 
  render();
}

function readHash() { 
  const h = decodeURIComponent(location.hash.slice(1)); 
  S.view = h || "compare"; 
}

function go(v) { 
  S.view = v; 
  S.pv = ""; 
  history.replaceState(null, "", v === "compare" ? location.pathname : "#" + encodeURIComponent(v)); 
  document.body.classList.remove("nav"); 
  render(); 
  window.scrollTo(0, 0);
}

const pts = r => {
  const s = (S.series[r.key] || []).slice();
  if (s.length && s.at(-1)[0] < S.updated) s.push([S.updated, s.at(-1)[1]]);
  return s.length ? s : [[S.updated || "oggi", r.price]];
};

function path(p, w, h) {
  if (p.length < 2) return `M0,${h / 2}H${w}`;
  const xs = p.map(q => +new Date(q[0])), ys = p.map(q => q[1]), lo = Math.min(...ys), hi = Math.max(...ys);
  const X = t => (t - xs[0]) / ((xs.at(-1) - xs[0]) || 1) * w, Y = v => h - 3 - (v - lo) / ((hi - lo) || 1) * (h - 6);
  let d = `M${X(xs[0])},${Y(ys[0])}`; for (let i = 1; i < p.length; i++) d += `H${X(xs[i])}V${Y(ys[i])}`;
  return d + `H${w}`;
}

const specSpans = (r, withProv) => [withProv && r.provider, r.vcpu && `${r.vcpu} vCPU`, r.ram_gb && `${num(+r.ram_gb, 0)} GB`, r.region, TL[r.term], r.note].filter(Boolean).map(x => `<span>${esc(x)}</span>`).join(" · ");

function cells(term) {
  const c = {};
  S.recs.filter(r => r.kind === "compute" && r.vcpu && r.ram_gb && termOf(r) === term && Math.round(r.ram_gb / r.vcpu) === S.ratio && TIERS.includes(+r.vcpu))
    .forEach(r => {
      const p = (c[r.provider] ??= {});
      if (!p[r.vcpu] || r.price < p[r.vcpu].price) p[r.vcpu] = r;
    });
  return c;
}

function matrix() {
  const cell = cells(S.term);
  const rows = Object.keys(cell).sort((a, b) => (cell[a][S.sort]?.price ?? 1e12) - (cell[b][S.sort]?.price ?? 1e12));
  if (!rows.length) return `<p class="empty">Nessuna configurazione con ${S.ratio} GB per vCPU.</p>`;
  
  const colStats = {};
  TIERS.forEach(t => {
    const vals = rows.map(p => cell[p][t]?.price).filter(v => v != null);
    if (vals.length) colStats[t] = { min: Math.min(...vals), max: Math.max(...vals) };
  });

  const head = TIERS.map(t => `<th><button type="button" data-sort="${t}" aria-pressed="${t === S.sort}">${t} vCPU</button></th>`).join("");
  const body = rows.map(p => `<tr><th scope="row"><button type="button" data-v="${esc(p)}">${mono(p)} ${esc(p)}</button></th>` + TIERS.map(t => {
    const r = cell[p][t];
    if (!r) return `<td class="na">–</td>`;
    
    let tClass = "";
    const stats = colStats[t];
    if (stats) {
      const pVal = r.price, range = stats.max - stats.min;
      if (pVal === stats.min) tClass = " t-best";
      else if (range === 0 || pVal <= stats.min + range * 0.33) tClass = " t-good";
      else if (pVal <= stats.min + range * 0.66) tClass = " t-mid";
      else tClass = " t-bad";
    }

    return `<td><button type="button" class="cell${tClass}" data-key="${esc(r.key)}"><b>${eur(r.price)}</b></button></td>`;
  }).join("") + `</tr>`).join("");

  return `<div class="mx"><table class="matrix"><thead><tr><th>Provider</th>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
}

function ranked() {
  const g = {};
  S.recs.filter(r => r.kind === S.kind).forEach(r => {
    const sub = S.kind === "storage" ? (isObj(r) ? "Object storage" : "Block storage") + ", " : "";
    const grp = (g[S.kind === "gpu" ? r.sku + ", " + r.unit + " per GPU" : sub + r.unit] ??= {});
    const k = r.provider + "|" + r.sku;
    if (!grp[k] || r.price < grp[k].price) grp[k] = r;
  });

  const out = Object.entries(g).map(([t, grp]) => {
    const rows = Object.values(grp).sort((a, b) => a.price - b.price), m = rows[0].price;
    return `<h3>${esc(t)}</h3>` + rows.map((r, i) => {
      const d = i ? ((r.price / m - 1) * 100) : null;
      return `<button type="button" class="row" data-key="${esc(r.key)}"><span class="rk">${i + 1}</span>
        <span><b>${esc(r.provider)}</b> ${esc(r.sku)}<span class="sub"><span>${esc(r.region)}</span><span>${esc(r.term ? TL[r.term] || r.term : "")}</span></span></span>
        <span class="price"><b>${num(r.price, r.price < 1 ? 4 : 2)}</b><small>${i === 0 ? (rows.length > 1 ? `<span class="best">più basso</span>` : "") : d == null ? "" : "+" + num(d, 0) + "%"}</small></span>
        <span>→</span></button>`;
    }).join("");
  }).join("");

  return `<div class="rows">${out || `<p class="empty">Nessuna voce in questa categoria.</p>`}</div>`;
}

const prow = r => `<button type="button" class="row" data-key="${esc(r.key)}"><span class="rk">·</span><span><b>${esc(r.sku)}</b><span class="sub"><span>${esc(r.vcpu ? r.vcpu + " vCPU" : "")}</span><span>${esc(r.ram_gb ? r.ram_gb + " GB RAM" : "")}</span><span>${esc(r.region)}</span><span>${esc(r.term ? TL[r.term] || r.term : "")}</span></span></span><span class="price"><b>${num(r.price, r.price < 1 ? 4 : 2)}</b><small>${esc(r.unit)}</small></span><span>→</span></button>`;

function providerView(name) {
  const rs = S.recs.filter(r => r.provider === name), st = statusOf(KEYOF[name] || name.toLowerCase());
  const nk = KINDS.filter(([k]) => rs.some(r => r.kind === k)).length;
  const head = `<section class="phead">${mono(name, "lg")}<div><h2>${esc(name)}</h2><p>${rs.length ? `${rs.length} voci in ${nk} ${nk === 1 ? "categoria" : "categorie"}` : "Nessun dato disponibile"}</p></div></section>`;
  const warn = (HELP[name] && !rs.length ? `<p class="warn">${esc(HELP[name])}</p>` : "") + (st.notes.length ? `<p class="warn">${st.notes.map(esc).join("<br>")}</p>` : "");
  if (!rs.length) return head + (warn || `<p class="empty">Nessuna voce raccolta per questo provider.</p>`);
  
  const vc = rs.some(r => r.kind === "compute" && r.vcpu) ? `<div class="chips">${["", 2, 4, 8, 16].map(x => `<button type="button" class="chip" data-pv="${x}" aria-pressed="${String(x) === String(S.pv)}">${x === "" ? "Tutte le taglie" : x + " vCPU"}</button>`).join("")}</div>` : "";
  const secs = KINDS.map(([k, l]) => {
    let list = rs.filter(r => r.kind === k);
    if (!list.length) return "";
    let inner;
    if (k === "compute") {
      if (S.pv !== "") list = list.filter(r => r.vcpu == S.pv);
      const terms = TERMS.filter(([t]) => list.some(r => termOf(r) === t));
      inner = terms.map(([t, tl]) => `${terms.length > 1 ? `<p class="th">${tl}</p>` : ""}` + list.filter(r => termOf(r) === t).sort((a, b) => a.vcpu - b.vcpu || a.ram_gb - b.ram_gb || a.price - b.price).map(prow).join("")).join("") || `<p class="empty">Nessuna voce con questa taglia.</p>`;
    } else {
      inner = list.slice().sort((a, b) => a.unit.localeCompare(b.unit) || a.price - b.price).map(prow).join("");
    }
    return `<details class="sec" open><summary><h3>${l}</h3><span>${list.length} ${list.length === 1 ? "voce" : "voci"}</span></summary>${inner}</details>`;
  }).join("");
  return head + warn + vc + secs;
}

function statusOf(key) {
  const e = Object.entries(S.status).filter(([k]) => k === key || k.startsWith(key + "-") || k === key + "+");
  const notes = [...new Set(e.map(([, s]) => s.pending ? "da raccogliere" : s.note || (s.ok === false ? "errore nella raccolta automatica" : "")).filter(Boolean))];
  return { notes, bad: e.some(([, s]) => s.ok === false) };
}

function detail(key) {
  const r = S.recs.find(x => x.key === key); 
  if (!r) return; 
  const p = pts(r);

  $("#dlg").innerHTML = `
    <h3>${esc(r.provider)} ${esc(r.sku)}</h3>
    <div class="sub" style="margin-bottom:12px;">${specSpans(r)}</div>
    <svg class="big" viewBox="0 0 300 150" preserveAspectRatio="none">
      <path d="${path(p, 300, 150)}" vector-effect="non-scaling-stroke"/>
    </svg>
    <table>
      ${p.slice().reverse().map(q => `<tr><td>${q[0].split("-").reverse().join("/")}</td><td>${num(q[1], q[1] < 1 ? 4 : 2)} ${esc(r.unit)}</td></tr>`).join("")}
    </table>
    ${r.source ? `<p style="margin-top:12px;font-size:12px;"><a href="${esc(r.source)}" target="_blank" rel="noopener">Fonte ufficiale</a></p>` : ""}
    <button type="button" class="close-btn" id="x">Chiudi</button>
  `;

  $("#dlg").showModal();
  $("#x").onclick = () => $("#dlg").close();
}

function compareView() {
  const tabs = `<div class="tabs">${KINDS.map(([k, l]) => `<button type="button" data-k="${k}" aria-pressed="${k === S.kind}">${l}</button>`).join("")}</div>`;
  const chips = S.kind === "compute" ? `<div class="chips">${TERMS.map(([k, l]) => `<button type="button" class="chip" data-t="${k}" aria-pressed="${k === S.term}">${l}</button>`).join("")}<span class="sep"></span>${[2, 4, 8].map(x => `<button type="button" class="chip" data-r="${x}" aria-pressed="${x === S.ratio}">${x} GB per vCPU</button>`).join("")}</div>` : "";
  return tabs + chips + (S.kind === "compute" ? matrix() : ranked());
}

function sidebar() {
  const cnt = {}; S.recs.forEach(r => cnt[r.provider] = (cnt[r.provider] || 0) + 1);
  $("#provs").innerHTML = GROUPS.map(([g, l]) => `<p class="grp">${g}</p>` + l.map(([n]) => 
    `<button type="button" class="pi" data-v="${esc(n)}" ${S.view === n ? 'aria-current="true"' : ""}>${mono(n)}<span>${esc(n)}</span><em>${cnt[n] || "–"}</em></button>`
  ).join("")).join("");
}

function render() {
  $("#meta").textContent = S.updated ? `Dati del ${S.updated}` : "Caricamento...";
  sidebar();
  $("#title").textContent = S.view === "compare" ? "Confronto prezzi" : S.view;
  $("#view").innerHTML = S.view === "compare" ? compareView() : providerView(S.view);
  
  if ($("#status")) {
    $("#status").innerHTML = Object.entries(S.status).map(([n, s]) => s.pending ? `${esc(n)}: da raccogliere` : s.ok ? `${esc(n)}: ${s.count} voci` : `<span class="bad">${esc(n)}: errore</span>`).join("<br>");
  }
}

document.addEventListener("click", e => {
  const b = e.target.closest("button"); if (!b) return;
  if (b.dataset.v) go(b.dataset.v);
  else if (b.dataset.k) { S.kind = b.dataset.k; render(); }
  else if (b.dataset.t) { S.term = b.dataset.t; render(); }
  else if (b.dataset.r) { S.ratio = +b.dataset.r; render(); }
  else if (b.dataset.sort) { S.sort = +b.dataset.sort; render(); }
  else if (b.dataset.pv !== undefined) { S.pv = b.dataset.pv; render(); }
  else if (b.dataset.key) detail(b.dataset.key);
  else if (b.id === "burger") document.body.classList.toggle("nav");
  else if (b.id === "csv") {
    const rows = S.recs.filter(r => S.view === "compare" ? r.kind === S.kind : r.provider === S.view);
    const c = [["provider","categoria","regione","sku","vcpu","ram_gb","impegno","unita","prezzo","fonte"],...rows.map(r=>[r.provider,r.kind,r.region,r.sku,r.vcpu??"",r.ram_gb??"",r.term||"on-demand",r.unit,r.price,r.source])]
      .map(l=>l.map(v=>`"${String(v).replace(/"/g,'""')}"`).join(";")).join("\n");
    const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob(["\ufeff"+c],{type:"text/csv"})); a.download = `prezzi-${S.view==="compare"?S.kind:S.view}-${S.updated}.csv`; a.click();
  }
});

$("#scrim").onclick = () => document.body.classList.remove("nav");
window.addEventListener("hashchange", () => { readHash(); render(); });
load();
