window.__app = "v9";
const $ = s => document.querySelector(s);
const KINDS = [["compute","Compute"],["storage","Storage"],["rete","Rete"],["gpu","GPU"],["licenza","Licenze"]];
const TIERS = [2, 4, 8, 16];
const TERMS = [["od","On-demand"],["1y","Impegno 1 anno"],["3y","Impegno 3 anni"]];
const GROUPS = [
  ["Hyperscaler", [["AWS","aws"],["Azure","azure"],["GCP","gcp"],["Oracle Cloud","oracle"]]],
  ["Europei", [["OVHcloud","ovh"],["Hetzner","hetzner"],["Scaleway","scaleway"],["STACKIT","stackit"],["IONOS","ionos"]]],
  ["Italiani", [["Aruba Cloud","aruba"],["Seeweb","seeweb"],["Fastweb","fastweb"],["Noovle","noovle"]]],
  ["Altri", [["Vultr","vultr"],["Akamai Linode","linode"]]],
  ["Virtualizzazione", [["Proxmox VE","proxmox"],["VMware","vmware"],["Nutanix","nutanix"]]]
];

const S = { view: "compare", kind: "compute", term: "od", ratio: 4, sort: 4, pv: "", recs: [], series: {}, status: {}, updated: "" };

const num = (n, d = 2) => n.toLocaleString("it-IT", { minimumFractionDigits: d, maximumFractionDigits: d });
const eur = n => num(n, n >= 100 ? 0 : 2);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const initials = n => n.replace(/[^A-Za-z0-9 ]/g, "").split(/\s+/).filter(Boolean).map(w => w[0]).join("").slice(0, 2).toUpperCase();
const mono = n => `<i class="mono">${esc(initials(n))}</i>`;

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
}

function cells(term) {
  const c = {};
  S.recs.filter(r => r.kind === "compute" && r.vcpu && r.ram_gb && (r.term || "od") === term && Math.round(r.ram_gb / r.vcpu) === S.ratio && TIERS.includes(+r.vcpu))
    .forEach(r => {
      const p = (c[r.provider] ??= {});
      if (!p[r.vcpu] || r.price < p[r.vcpu].price) p[r.vcpu] = r;
    });
  return c;
}

function matrix() {
  const cell = cells(S.term);
  const rows = Object.keys(cell).sort((a, b) => (cell[a][S.sort]?.price ?? 1e12) - (cell[b][S.sort]?.price ?? 1e12));
  if (!rows.length) return `<p class="empty">Nessuna configurazione disponibile per questo filtro.</p>`;
  
  const head = TIERS.map(t => `<th><button type="button" data-sort="${t}">${t} vCPU</button></th>`).join("");
  const body = rows.map(p => `<tr><th scope="row">${mono(p)} ${esc(p)}</th>` + TIERS.map(t => {
    const r = cell[p][t];
    if (!r) return `<td class="na">–</td>`;
    return `<td><button type="button" class="cell" data-key="${esc(r.key)}"><b>${eur(r.price)}</b></button></td>`;
  }).join("") + `</tr>`).join("");

  return `<div class="mx"><table class="matrix"><thead><tr><th>Provider</th>${head}</tr></thead><tbody>${body}</tbody></table></div>`;
}

function compareView() {
  const tabs = `<div class="tabs">${KINDS.map(([k, l]) => `<button type="button" data-k="${k}" aria-pressed="${k === S.kind}">${l}</button>`).join("")}</div>`;
  const chips = S.kind === "compute" ? `<div class="chips">${TERMS.map(([k, l]) => `<button type="button" class="chip" data-t="${k}" aria-pressed="${k === S.term}">${l}</button>`).join("")}</div>` : "";
  return tabs + chips + (S.kind === "compute" ? matrix() : `<p class="empty">Categoria in fase di aggiornamento.</p>`);
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
  $("#view").innerHTML = S.view === "compare" ? compareView() : `<p class="empty">Vista provider ${esc(S.view)}</p>`;
}

document.addEventListener("click", e => {
  const b = e.target.closest("button"); if (!b) return;
  if (b.dataset.v) go(b.dataset.v);
  else if (b.dataset.k) { S.kind = b.dataset.k; render(); }
  else if (b.dataset.t) { S.term = b.dataset.t; render(); }
  else if (b.dataset.sort) { S.sort = +b.dataset.sort; render(); }
  else if (b.id === "burger") document.body.classList.toggle("nav");
});

$("#scrim").onclick = () => document.body.classList.remove("nav");
window.addEventListener("hashchange", () => { readHash(); render(); });
load();
