"use strict";
const $ = id => document.getElementById(id);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"}[c]));
const safeUrl = u => { try { const x = new URL(String(u)); return x.protocol === "https:" ? x.href : ""; } catch { return ""; } };

const state = {records: [], series: {}, status: {}, updated: "", category: "compute", term: "all", provider: "all",
               storageType: "all", gpuType: "all", vcpuType: "all", unit: "auto", sortField: "price", sortAsc: true, view: [],
               mode: "table", mterm: "on-demand", ratio: 4, msort: 4, mcells: []};

const categories = [["compute", "Compute"], ["storage", "Storage"], ["rete", "Rete"], ["gpu", "GPU"], ["colocation", "Colocation"],
                    ["licenses", "Licenze"], ["k8s", "Kubernetes"], ["dbaas", "Database"]];
const terms = [["all", "Tutti"], ["on-demand", "On-demand"], ["1 anno", "Impegno 1 anno"], ["3 anni", "Impegno 3 anni"]];
const storageTypes = [["all", "Tutti i tipi"], ["object", "Object / S3"], ["block-std", "Blocco Standard"], ["block-hp", "Blocco High Performance / SSD"], ["file", "File / NAS / Unified"]];
const gpuTypes = [["all", "Tutte le GPU"], ["h200", "NVIDIA H200"], ["h100", "NVIDIA H100"], ["a100", "NVIDIA A100"], ["l4", "NVIDIA L4 / L40S"],
                  ["a10g", "NVIDIA A10 / T4"], ["rtx", "GeForce RTX"], ["other", "Altre"]];
const vcpuTypes = [["all", "Tutte le taglie"], ["1", "1 vCPU"], ["2", "2 vCPU"], ["4", "4 vCPU"], ["8", "8 vCPU"], ["16", "16+ vCPU"]];
const modes = [["table", "Elenco"], ["matrix", "Confronto per taglia"]];
const TIERS = [2, 4, 8, 16];
const matrixTerms = [["on-demand", "On-demand"], ["1 anno", "Impegno 1 anno"], ["3 anni", "Impegno 3 anni"]];
const matrixRatios = [2, 4, 8];
const matrixOn = () => state.category === "compute" && state.mode === "matrix";

const flags = {"aruba cloud": "🇮🇹", "aruba cloud enterprise": "🇮🇹", "polo strategico nazionale": "🇮🇹", "seeweb": "🇮🇹", "enter cloud suite": "🇮🇹",
               "aws": "🇺🇸", "azure": "🇺🇸", "gcp": "🇺🇸", "digitalocean": "🇺🇸", "vultr": "🇺🇸", "oracle cloud": "🇺🇸", "akamai linode": "🇺🇸",
               "vmware": "🇺🇸", "nutanix": "🇺🇸", "hetzner": "🇩🇪", "stackit": "🇩🇪", "ionos": "🇩🇪", "proxmox ve": "🇦🇹", "ovhcloud": "🇫🇷",
               "scaleway": "🇫🇷", "exoscale": "🇨🇭"};
const flagOf = p => flags[String(p || "").toLowerCase().trim()] || "🌐";

const kindOf = r => String(r.kind || r.categoria || "").toLowerCase();
const vcpuOf = r => r.vcpu ?? r.vcpus;
const ramOf = r => r.ram_gb ?? r.ram;
const termOf = r => r.term || r.impegno || "On-demand";
const termKey = r => { const t = termOf(r).toLowerCase(); return t.includes("1 anno") ? "1 anno" : t.includes("3 anni") ? "3 anni" : "on-demand"; };

function matchCategory(k, cat) {
  if (cat === "rete") return k === "rete" || k === "network";
  if (cat === "licenses") return k === "licenses" || k === "licenze" || k === "licenza";
  if (cat === "dbaas") return k === "dbaas" || k === "database";
  return k === cat;
}
function storageTypeOf(sku) {
  const s = String(sku || "").toLowerCase();
  if (/s3|object|blob|cloud storage|archive/.test(s)) return "object";
  if (/unified|nas|file/.test(s)) return "file";
  if (/performance|premium|ssd|nvme/.test(s)) return "block-hp";
  if (/block|disk|disco|volume|standard|gp3|balanced/.test(s)) return "block-std";
  return "other";
}
function gpuTypeOf(sku) {
  const s = String(sku || "").toLowerCase();
  if (s.includes("h200")) return "h200";
  if (s.includes("h100")) return "h100";
  if (s.includes("a100")) return "a100";
  if (/l40s|\bl4\b/.test(s)) return "l4";
  if (/a10|t4|v100|p100/.test(s)) return "a10g";
  if (/rtx|geforce/.test(s)) return "rtx";
  return "other";
}
function vcpuGroup(v) {
  v = Number(v || 0);
  return v === 1 ? "1" : v === 2 ? "2" : v === 4 ? "4" : v === 8 ? "8" : v >= 16 ? "16" : "all";
}
function fmtPrice(p) {
  if (p === null || p === undefined || p === "") return "Da compilare";
  const n = Number(p), d = n === 0 ? 2 : n < 1 ? 4 : 2;
  return n.toLocaleString("it-IT", {minimumFractionDigits: d, maximumFractionDigits: d});
}

const inCategory = r => matchCategory(kindOf(r), state.category);
function effectiveUnit() {
  if (state.unit !== "auto") return state.unit;
  const c = {};
  state.records.filter(inCategory).forEach(r => { c[r.unit || "?"] = (c[r.unit || "?"] || 0) + 1; });
  return Object.entries(c).sort((a, b) => b[1] - a[1])[0]?.[0] || "all";
}
function filtered({ignoreUnit = false} = {}) {
  const unit = ignoreUnit ? "all" : effectiveUnit();
  return state.records.filter(r => {
    if (!inCategory(r)) return false;
    if (state.provider !== "all" && r.provider !== state.provider) return false;
    if (unit !== "all" && (r.unit || "?") !== unit) return false;
    if (state.category === "storage" && state.storageType !== "all" && storageTypeOf(r.sku) !== state.storageType) return false;
    if (state.category === "gpu" && state.gpuType !== "all" && gpuTypeOf(r.sku) !== state.gpuType) return false;
    if (state.category === "compute" && state.vcpuType !== "all" && vcpuGroup(vcpuOf(r)) !== state.vcpuType) return false;
    if (state.term !== "all" && termKey(r) !== state.term) return false;
    return true;
  });
}

const chip = (attr, id, label, active, on) =>
  `<button type="button" data-${attr}="${esc(id)}" class="px-3.5 py-1.5 rounded-xl text-xs font-semibold transition cursor-pointer ${active ? on : "bg-slate-800 text-slate-300 hover:bg-slate-700"}">${esc(label)}</button>`;

function renderFilters() {
  const count = {};
  state.records.forEach(r => { const c = categories.find(x => matchCategory(kindOf(r), x[0])); if (c) count[c[0]] = (count[c[0]] || 0) + 1; });
  $("category-buttons").innerHTML = categories.map(([id, name]) =>
    chip("cat", id, `${name} (${count[id] || 0})`, state.category === id, "bg-indigo-600 text-white shadow-lg shadow-indigo-600/30")).join("");
  const show = (id, on) => { $(id).hidden = !on; };
  show("storage-type-container", state.category === "storage");
  show("gpu-type-container", state.category === "gpu");
  show("vcpu-type-container", state.category === "compute" && !matrixOn());
  show("mode-container", state.category === "compute");
  show("term-container", !matrixOn());
  show("unit-container", !matrixOn());
  $("storage-type-buttons").innerHTML = storageTypes.map(([id, n]) => chip("storage", id, n, state.storageType === id, "bg-amber-600 text-white shadow")).join("");
  $("gpu-type-buttons").innerHTML = gpuTypes.map(([id, n]) => chip("gpu", id, n, state.gpuType === id, "bg-purple-600 text-white shadow")).join("");
  $("vcpu-type-buttons").innerHTML = vcpuTypes.map(([id, n]) => chip("vcpu", id, n, state.vcpuType === id, "bg-indigo-600 text-white shadow")).join("");
  $("mode-buttons").innerHTML = modes.map(([id, n]) => chip("mode", id, n, state.mode === id, "bg-indigo-600 text-white shadow")).join("");
  $("term-buttons").innerHTML = terms.map(([id, n]) => chip("term", id, n, state.term === id, "bg-emerald-600 text-white shadow")).join("");
  const units = {};
  state.records.filter(inCategory).forEach(r => { const u = r.unit || "?"; units[u] = (units[u] || 0) + 1; });
  const eff = effectiveUnit();
  $("unit-buttons").innerHTML = [["all", "Tutte le unità"], ...Object.entries(units).sort((a, b) => b[1] - a[1]).map(([u, n]) => [u, `${u} (${n})`])]
    .map(([id, n]) => chip("unit", id, n, eff === id, "bg-sky-600 text-white shadow")).join("");
}

function renderProviders() {
  const inCat = state.records.filter(inCategory);
  const providers = [...new Set(inCat.map(r => r.provider))].filter(Boolean).sort();
  const btn = (id, html, n, active) => `<button type="button" data-prov="${esc(id)}" class="w-full flex justify-between items-center px-3.5 py-2 rounded-xl text-xs font-semibold transition cursor-pointer ${active ? "bg-indigo-600 text-white shadow-lg shadow-indigo-600/30" : "bg-slate-800/60 text-slate-300 hover:bg-slate-800"}">
      <span class="truncate">${html}</span><span class="bg-slate-900/50 px-2 py-0.5 rounded-full text-[10px]">${n}</span></button>`;
  $("provider-list").innerHTML = btn("all", "🌐 Tutti i Provider", inCat.length, state.provider === "all")
    + providers.map(p => btn(p, `${flagOf(p)} ${esc(p)}`, inCat.filter(r => r.provider === p).length, state.provider === p)).join("");
}

function renderTable() {
  const cat = categories.find(c => c[0] === state.category);
  $("table-title").textContent = `Listino ${cat ? cat[1] : ""}`;
  const key = state.sortField;
  const val = r => key === "vcpu" ? Number(vcpuOf(r) || 0) : key === "price" ? Number(r.price ?? 0) : String(key === "region" ? r.region || r.regione || "" : key === "term" ? termOf(r) : r[key] || "").toLowerCase();
  state.view = filtered().sort((a, b) => { const x = val(a), y = val(b); return (x < y ? -1 : x > y ? 1 : 0) * (state.sortAsc ? 1 : -1); });
  const others = filtered({ignoreUnit: true}).length - state.view.length;
  $("result-count").textContent = `${state.view.length} elementi trovati${others > 0 ? ` (altri ${others} con unità di prezzo diversa)` : ""}`;
  if (!state.view.length) {
    $("table-body").innerHTML = `<tr><td colspan="7" class="py-16 text-center text-slate-500 text-sm font-medium">Nessun record trovato per i filtri selezionati.</td></tr>`;
    return;
  }
  const badge = {"on-demand": "bg-emerald-500/10 text-emerald-400 border-emerald-500/20", "1 anno": "bg-sky-500/10 text-sky-400 border-sky-500/20", "3 anni": "bg-violet-500/10 text-violet-400 border-violet-500/20"};
  $("table-body").innerHTML = state.view.map((r, i) => {
    const href = safeUrl(r.source || r.fonte), v = vcpuOf(r), ram = ramOf(r);
    return `<tr class="hover:bg-slate-800/50 transition cursor-pointer" data-i="${i}" tabindex="0">
      <td class="py-3.5 px-4 font-semibold text-white"><span>${flagOf(r.provider)}</span> <span>${esc(r.provider)}</span>${r.stale ? ` <span class="ml-1 text-[10px] text-amber-400 border border-amber-500/30 rounded px-1">non aggiornato</span>` : ""}</td>
      <td class="py-3.5 px-4 max-w-xs"><div class="text-slate-300 font-mono text-xs break-words">${esc(r.sku)}</div>${r.note ? `<div class="text-[11px] text-slate-500 mt-1 line-clamp-2" title="${esc(r.note)}">${esc(r.note)}</div>` : ""}</td>
      <td class="py-3.5 px-4 text-slate-400 text-xs">${esc(r.region || r.regione || "-")}</td>
      <td class="py-3.5 px-4 text-slate-300 text-xs font-medium whitespace-nowrap">${v || ram ? `${v ? esc(v) + " vCPU" : "–"}${ram ? " / " + esc(ram) + " GB" : ""}` : "–"}</td>
      <td class="py-3.5 px-4"><span class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold border ${badge[termKey(r)]}">${esc(termOf(r))}</span></td>
      <td class="py-3.5 px-4 text-right font-bold text-emerald-400 whitespace-nowrap">${esc(fmtPrice(r.price))} <span class="text-[11px] text-slate-400 font-normal">${esc(r.unit || "")}</span></td>
      <td class="py-3.5 px-4">${href ? `<a href="${esc(href)}" target="_blank" rel="noopener noreferrer" class="text-indigo-400 hover:text-indigo-300 text-xs underline font-medium">Link</a>` : ""}</td>
    </tr>`;
  }).join("");
}

// ---- Confronto per taglia: provider in riga, 2/4/8/16 vCPU in colonna, prezzo più basso di ogni colonna evidenziato
const diskInfo = r => { const n = String(r.note || ""); return /senza (storage|disco)/i.test(n) ? "senza disco" : /incl\.?\s*\d+\s*GB|disco e traffico|include disco|\d+\s*GB (NVMe|SSD)/i.test(n) ? "disco incluso" : ""; };

function matrixCells(wanted) {
  const cells = {};
  state.records.forEach(r => {
    if (kindOf(r) !== "compute" || (r.unit || "") !== "EUR/mese") return;
    const v = Number(vcpuOf(r)), ram = Number(ramOf(r)), price = Number(r.price);
    if (!TIERS.includes(v) || !(ram > 0) || !(price > 0) || Math.round(ram / v) !== state.ratio || termKey(r) !== wanted) return;
    const row = (cells[r.provider] ??= {});
    if (!row[v] || price < Number(row[v].price)) row[v] = r;
  });
  return cells;
}

function renderMatrix() {
  $("matrix-term-buttons").innerHTML = matrixTerms.map(([id, n]) => chip("mterm", id, n, state.mterm === id, "bg-emerald-600 text-white shadow")).join("");
  $("matrix-ratio-buttons").innerHTML = matrixRatios.map(x => chip("ratio", x, `${x} GB per vCPU`, state.ratio === x, "bg-indigo-600 text-white shadow")).join("");
  const cells = matrixCells(state.mterm);
  if (state.mterm !== "on-demand") {            // senza sconto per impegno si mostra il prezzo on-demand, segnalato con (OD)
    const od = matrixCells("on-demand");
    for (const p in od) for (const t in od[p]) if (!cells[p]?.[t]) (cells[p] ??= {})[t] = {...od[p][t], __od: true};
  }
  const min = {};
  TIERS.forEach(t => { const v = Object.values(cells).map(c => c[t] && Number(c[t].price)).filter(x => x > 0); min[t] = v.length ? Math.min(...v) : null; });
  const price = (p, t) => cells[p][t] ? Number(cells[p][t].price) : Infinity;
  const rows = Object.keys(cells).sort((a, b) => price(a, state.msort) - price(b, state.msort) || a.localeCompare(b));
  const all = [...new Set(state.records.filter(r => kindOf(r) === "compute" && r.provider).map(r => r.provider))];
  const missing = all.filter(p => !cells[p]).sort();
  $("matrix-count").textContent = `${rows.length} provider a confronto`;
  state.mcells = [];
  if (!rows.length) {
    $("matrix-body").innerHTML = `<p class="py-16 text-center text-slate-500 text-sm font-medium">Nessuna configurazione con ${state.ratio} GB per vCPU.</p>`;
  } else {
    const head = TIERS.map(t => `<th class="py-3 px-2 text-right"><button type="button" data-msort="${t}" aria-pressed="${state.msort === t}" class="px-3 py-1 rounded-lg text-right cursor-pointer transition ${state.msort === t ? "text-white" : "text-slate-400 hover:text-indigo-300"}">${t} vCPU<span class="block text-[11px] font-normal text-slate-500">${t * state.ratio} GB${state.msort === t ? " ↓" : ""}</span></button></th>`).join("");
    const body = rows.map(p => `<tr><th scope="row" class="py-2 px-4 text-left sticky left-0 bg-slate-900 whitespace-nowrap"><button type="button" data-mprov="${esc(p)}" class="font-semibold text-white hover:text-indigo-300 cursor-pointer text-left">${flagOf(p)} ${esc(p)}</button></th>${TIERS.map(t => {
      const r = cells[p][t];
      if (!r) return `<td class="py-3 px-4 text-right text-slate-600">–</td>`;
      const idx = state.mcells.push(r) - 1, pr = Number(r.price), isMin = pr === min[t], d = min[t] > 0 ? (pr / min[t] - 1) * 100 : null;
      const label = (isMin ? "più basso" : d == null ? "" : `+${Math.round(d)}%`) + (r.__od ? " (OD)" : ""), disk = diskInfo(r);
      return `<td class="py-2 px-2"><button type="button" data-m="${idx}" class="w-full text-right px-3 py-2 rounded-lg transition cursor-pointer ${isMin ? "bg-emerald-500/15 text-emerald-300 ring-1 ring-emerald-500/40" : "text-slate-200 hover:bg-slate-800"}"><span class="block font-bold">${esc(fmtPrice(pr))}</span><span class="block text-[11px] ${isMin ? "text-emerald-300/80" : "text-slate-400"}">${esc(label)}</span>${disk ? `<span class="block text-[10px] text-slate-500">${esc(disk)}</span>` : ""}</button></td>`;
    }).join("")}</tr>`).join("");
    $("matrix-body").innerHTML = `<table class="w-full text-sm border-collapse min-w-[520px]"><thead><tr class="border-b border-slate-800 bg-slate-950/70 text-xs font-bold uppercase tracking-wider"><th class="py-3 px-4 text-left text-slate-400">Provider</th>${head}</tr></thead><tbody class="divide-y divide-slate-800">${body}</tbody></table>`;
  }
  $("matrix-note").textContent = `Euro al mese, listino IVA esclusa. Ogni cella è la configurazione più economica del provider con ${state.ratio} GB di RAM per vCPU, tra tutte le regioni raccolte; la cella evidenziata è la più bassa della colonna. `
    + `I prezzi non sono tutti omogenei: alcuni includono disco e traffico, altri no (la nota sotto il prezzo lo dice: tocca una cella per il dettaglio, la fonte e lo storico). `
    + (state.mterm !== "on-demand" ? "OD indica che per quel provider non c'è (o non è stato trovato) uno sconto per impegno e si mostra il prezzo on-demand. " : "")
    + "Il Polo Strategico Nazionale ha solo canoni annuali, quindi compare con l'impegno a 1 anno. "
    + (missing.length ? `Senza configurazioni a ${state.ratio} GB per vCPU: ${missing.join(", ")}.` : "");
}

function renderStatus() {
  const rows = Object.entries(state.status).map(([name, s]) => {
    const bad = s.ok === false, pend = s.pending;
    const text = pend ? "da raccogliere" : bad ? `errore: ${s.error || ""}` : `${s.count ?? ""} voci${s.note ? `, ${s.note}` : ""}`;
    return {bad, pend, html: `<div class="${bad ? "text-rose-400" : pend ? "text-slate-500" : "text-slate-300"}"><span class="font-semibold">${esc(name)}</span>: ${esc(text)}</div>`};
  }).sort((a, b) => Number(b.bad) - Number(a.bad));
  $("status-list").innerHTML = rows.map(r => r.html).join("") || `<div class="text-slate-500">Stato non disponibile.</div>`;
}

function renderHeader() {
  const el = $("update-info");
  if (!state.updated) { el.textContent = "Dati non disponibili"; return; }
  const days = Math.floor((Date.now() - new Date(state.updated).getTime()) / 864e5);
  el.textContent = `Dati del ${state.updated.split("-").reverse().join("/")}, ${state.records.length} voci${days > 3 ? `, non aggiornati da ${days} giorni` : ""}`;
  el.className = `text-xs ${days > 3 ? "text-amber-400" : "text-slate-400"}`;
}

function renderAll() {
  renderFilters(); renderProviders();
  $("table-panel").classList.toggle("hidden", matrixOn());
  $("matrix-panel").classList.toggle("hidden", !matrixOn());
  if (matrixOn()) renderMatrix(); else renderTable();
}

function sparkPath(p, w, h) {
  if (p.length < 2) return `M0,${h / 2}H${w}`;
  const xs = p.map(q => +new Date(q[0])), ys = p.map(q => q[1]), lo = Math.min(...ys), hi = Math.max(...ys);
  const X = t => (t - xs[0]) / ((xs.at(-1) - xs[0]) || 1) * w, Y = v => h - 3 - (v - lo) / ((hi - lo) || 1) * (h - 6);
  let d = `M${X(xs[0])},${Y(ys[0])}`;
  for (let i = 1; i < p.length; i++) d += `H${X(xs[i])}V${Y(ys[i])}`;
  return d + `H${w}`;
}

function openDetail(r) {
  const s = (state.series[r.key] || []).slice();
  if (s.length && state.updated && s.at(-1)[0] < state.updated) s.push([state.updated, s.at(-1)[1]]);
  const href = safeUrl(r.source || r.fonte), v = vcpuOf(r), ram = ramOf(r);
  const spec = [v ? `${v} vCPU` : "", ram ? `${ram} GB` : "", r.region || r.regione || "", termOf(r)].filter(Boolean).join("  ·  ");
  $("detail").innerHTML = `
    <h3 class="text-lg font-bold">${flagOf(r.provider)} ${esc(r.provider)}</h3>
    <p class="font-mono text-sm text-slate-300 mt-1 break-words">${esc(r.sku)}</p>
    <p class="text-xs text-slate-400 mt-1">${esc(spec)}</p>
    <p class="text-2xl font-bold text-emerald-400 mt-4">${esc(fmtPrice(r.price))} <span class="text-sm text-slate-400 font-normal">${esc(r.unit || "")}</span></p>
    ${r.note ? `<p class="text-xs text-slate-400 mt-3 leading-relaxed">${esc(r.note)}</p>` : ""}
    ${r.stale ? `<p class="text-xs text-amber-400 mt-2">Dato non aggiornato: l'ultima raccolta di questa fonte è fallita.</p>` : ""}
    <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider mt-5 mb-2">Storico</h4>
    ${s.length ? `<svg viewBox="0 0 300 80" class="w-full h-20 text-indigo-400" preserveAspectRatio="none" aria-hidden="true"><path d="${sparkPath(s, 300, 80)}" fill="none" stroke="currentColor" stroke-width="2" vector-effect="non-scaling-stroke"/></svg>
      <table class="w-full text-xs mt-2">${s.slice().reverse().map(q => `<tr class="border-t border-slate-800"><td class="py-1 text-slate-400">${esc(String(q[0]).split("-").reverse().join("/"))}</td><td class="py-1 text-right">${esc(fmtPrice(q[1]))} ${esc(r.unit || "")}</td></tr>`).join("")}</table>`
      : `<p class="text-xs text-slate-500">Storico non disponibile.</p>`}
    <div class="flex justify-between items-center mt-5">
      ${href ? `<a href="${esc(href)}" target="_blank" rel="noopener noreferrer" class="text-indigo-400 hover:text-indigo-300 text-xs underline font-medium">Fonte</a>` : "<span></span>"}
      <button type="button" data-close class="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-xs font-semibold cursor-pointer">Chiudi</button>
    </div>`;
  $("detail").showModal();
}

function exportCsv() {
  const q = v => `"${String(v ?? "").replace(/"/g, '""')}"`;
  const lines = [["provider", "categoria", "regione", "sku", "vcpu", "ram_gb", "impegno", "unita", "prezzo", "nota", "fonte"].join(";")];
  state.records.forEach(r => lines.push([r.provider, kindOf(r), r.region || r.regione, r.sku, vcpuOf(r), ramOf(r), termOf(r), r.unit, r.price, r.note, r.source || r.fonte].map(q).join(";")));
  const a = document.createElement("a");
  a.href = URL.createObjectURL(new Blob(["\ufeff" + lines.join("\n")], {type: "text/csv;charset=utf-8;"}));
  a.download = `prezzi-cloud-${state.updated || "dati"}.csv`;
  a.click();
}

document.addEventListener("click", e => {
  const t = e.target;
  if (t === $("detail")) { $("detail").close(); return; }               // clic sullo sfondo
  const b = t.closest("[data-close],[data-cat],[data-storage],[data-gpu],[data-vcpu],[data-term],[data-unit],[data-prov],[data-sort],[data-mode],[data-mterm],[data-ratio],[data-msort],[data-mprov],[data-m],#btn-csv");
  if (b) {
    const d = b.dataset;
    if ("close" in d) { $("detail").close(); return; }
    if (b.id === "btn-csv") { exportCsv(); return; }
    if (d.cat) Object.assign(state, {category: d.cat, storageType: "all", gpuType: "all", vcpuType: "all", unit: "auto", provider: "all"});
    else if (d.storage) state.storageType = d.storage;
    else if (d.gpu) state.gpuType = d.gpu;
    else if (d.vcpu) state.vcpuType = d.vcpu;
    else if (d.term) state.term = d.term;
    else if (d.unit) state.unit = d.unit;
    else if (d.mode) state.mode = d.mode;
    else if (d.mterm) state.mterm = d.mterm;
    else if (d.ratio) state.ratio = Number(d.ratio);
    else if (d.msort) state.msort = Number(d.msort);
    else if (d.mprov) Object.assign(state, {mode: "table", provider: d.mprov, vcpuType: "all", term: "all", unit: "auto"});
    else if (d.m !== undefined) { const r = state.mcells[Number(d.m)]; if (r) openDetail(r); return; }
    else if (d.prov) { state.provider = d.prov; if (matrixOn()) state.mode = "table"; }
    else if (d.sort) { state.sortAsc = state.sortField === d.sort ? !state.sortAsc : true; state.sortField = d.sort; renderTable(); return; }
    renderAll();
    return;
  }
  const tr = t.closest("tr[data-i]");
  if (tr && !t.closest("a")) { const r = state.view[Number(tr.dataset.i)]; if (r) openDetail(r); }
});
document.addEventListener("keydown", e => {
  const tr = e.target.closest?.("tr[data-i]");
  if (tr && e.key === "Enter") { const r = state.view[Number(tr.dataset.i)]; if (r) openDetail(r); }
});

async function getJson(path) {
  try { const r = await fetch(path, {cache: "no-cache"}); return r.ok ? await r.json() : null; } catch { return null; }
}
async function loadData() {
  renderFilters(); renderProviders();
  const [latest, series, status] = await Promise.all([getJson("data/latest.json"), getJson("data/series.json"), getJson("data/status.json")]);
  state.series = series || {}; state.status = status || {};
  if (!latest || !Array.isArray(latest.records)) {
    $("table-body").innerHTML = `<tr><td colspan="7" class="py-16 text-center text-rose-400 text-sm font-medium">Impossibile caricare i dati (data/latest.json). Controlla che il workflow abbia prodotto i file.</td></tr>`;
    renderHeader(); renderStatus();
    return;
  }
  state.records = latest.records; state.updated = latest.updated || "";
  renderHeader(); renderStatus(); renderAll();
}

if ("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js");
loadData();
