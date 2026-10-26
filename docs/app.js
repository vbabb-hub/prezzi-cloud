const $ = s => document.querySelector(s);
const KINDS = [["compute","Compute"],["storage","Storage"],["rete","Rete"],["gpu","GPU"],["licenza","Licenze"]];
const TIERS = [2, 4, 8, 16];
const S = {kind:"compute", ratio:4, sort:4, recs:[], series:{}, status:{}, updated:""};
const num = (n,d=2) => n.toLocaleString("it-IT",{minimumFractionDigits:d,maximumFractionDigits:d});
const eur = n => num(n, n >= 100 ? 0 : 2);
const hue = p => [...p].reduce((h,c)=>(h*31+c.charCodeAt(0))%360,7);
const esc = s => String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const pct = (p,m) => m > 0 ? (p/m-1)*100 : null;
const isObj = r => /object|s3|blob|cloud storage/i.test(r.sku);

async function load(){
  const j = u => fetch(u,{cache:"no-cache"}).then(r=>r.ok?r.json():null).catch(()=>null);
  const [l,s,st] = await Promise.all([j("data/latest.json"),j("data/series.json"),j("data/status.json")]);
  S.recs = l?.records||[]; S.updated = l?.updated||""; S.series = s||{}; S.status = st||{};
  render();
}
const pts = r => { const s=(S.series[r.key]||[]).slice(); if(s.length && s.at(-1)[0]<S.updated) s.push([S.updated,s.at(-1)[1]]); return s; };
function path(p,w,h){
  if(p.length<2) return `M0,${h/2}H${w}`;
  const xs=p.map(q=>+new Date(q[0])), ys=p.map(q=>q[1]), lo=Math.min(...ys), hi=Math.max(...ys);
  const X=t=>(t-xs[0])/((xs.at(-1)-xs[0])||1)*w, Y=v=>h-3-(v-lo)/((hi-lo)||1)*(h-6);
  let d=`M${X(xs[0])},${Y(ys[0])}`; for(let i=1;i<p.length;i++) d+=`H${X(xs[i])}V${Y(ys[i])}`;
  return d+`H${w}`;
}
const specOf = r => [r.vcpu&&`${r.vcpu} vCPU`, r.ram_gb&&`${num(+r.ram_gb,0)} GB`, r.region, r.note].filter(Boolean).join(" · ");

function matrix(){
  const all = S.recs.filter(r=>r.kind==="compute" && r.vcpu && r.ram_gb);
  const provs = [...new Set(all.map(r=>r.provider))];
  const cell = {};
  all.filter(r=>Math.round(r.ram_gb/r.vcpu)===S.ratio && TIERS.includes(+r.vcpu)).forEach(r=>{
    const c = (cell[r.provider] ??= {});
    if(!c[r.vcpu] || r.price < c[r.vcpu].price) c[r.vcpu] = r;
  });
  const min = {};
  TIERS.forEach(t=>{ const v=Object.values(cell).map(c=>c[t]?.price).filter(x=>x!=null); min[t]=v.length?Math.min(...v):null; });
  const rows = Object.keys(cell).sort((a,b)=>(cell[a][S.sort]?.price??1e12)-(cell[b][S.sort]?.price??1e12));
  if(!rows.length) return `<p class="empty">${all.length?`Nessuna configurazione con ${S.ratio} GB per vCPU.`:"Nessun dato di compute."}</p>`;
  const head = TIERS.map(t=>`<th><button type="button" data-sort="${t}" aria-pressed="${t===S.sort}">${t} vCPU<small>${t*S.ratio} GB${t===S.sort?" ↓":""}</small></button></th>`).join("");
  const body = rows.map(p=>`<tr><th scope="row"><i style="background:hsl(${hue(p)} 55% 45%)"></i>${esc(p)}</th>`+TIERS.map(t=>{
    const r = cell[p][t]; if(!r) return `<td class="na">–</td>`;
    const isMin = r.price===min[t], d = pct(r.price,min[t]);
    return `<td><button type="button" class="cell${isMin?" min":""}" data-key="${esc(r.key)}"><b>${eur(r.price)}</b><small>${isMin?"più basso":d==null?"":"+"+num(d,0)+"%"}</small></button></td>`;
  }).join("")+`</tr>`).join("");
  const missing = provs.filter(p=>!cell[p]);
  return `<div class="mx"><table class="matrix"><thead><tr><th></th>${head}</tr></thead><tbody>${body}</tbody></table></div>
    <p class="note">€ al mese, listino IVA esclusa. Ogni cella è la configurazione più economica del provider con ${S.ratio} GB per vCPU, tra tutte le regioni raccolte. Tocca una cella per modello, regione e storico; tocca l'intestazione di una colonna per ordinare.${missing.length?` Senza configurazioni a ${S.ratio} GB/vCPU: ${missing.map(esc).join(", ")}.`:""}</p>`;
}

function ranked(){
  const g = {};
  S.recs.filter(r=>r.kind===S.kind).forEach(r=>{
    const sub = S.kind==="storage" ? (isObj(r)?"Object storage":"Block storage")+" · " : "";
    const grp = (g[S.kind==="gpu" ? r.sku : sub+r.unit] ??= {}), k = r.provider+"|"+r.sku;
    if(!grp[k] || r.price < grp[k].price) grp[k] = r;
  });
  const out = Object.entries(g).map(([t,grp])=>{
    const rows = Object.values(grp).sort((a,b)=>a.price-b.price), m = rows[0].price;
    return `<h2>${esc(t)}</h2>`+rows.map((r,i)=>{
      const d = i ? pct(r.price,m) : null;
      return `<button type="button" class="row" data-key="${esc(r.key)}"><span class="rk">${i+1}</span>
        <span><b>${esc(r.provider)}</b> ${esc(r.sku)}<small>${esc(specOf(r))}</small></span>
        <span class="price">${num(r.price, r.price<1?4:2)}<small>${i===0?(rows.length>1?"più basso":""):d==null?"":"+"+num(d,0)+"%"}</small></span>
        <svg class="sp" viewBox="0 0 64 20"><path d="${path(pts(r),64,20)}"/></svg></button>`;
    }).join("");
  }).join("");
  return out || `<p class="empty">Nessuna voce in questa categoria. Le voci manuali compaiono dopo aver compilato i file in <code>manual/</code>.</p>`;
}

function render(){
  $("#meta").textContent = S.updated ? `Dati del ${S.updated.split("-").reverse().join("/")} · listino IVA esclusa` : "Nessun dato: esegui il workflow su GitHub Actions";
  $("#kinds").innerHTML = KINDS.map(([k,l])=>`<button type="button" data-k="${k}" aria-pressed="${k===S.kind}">${l}</button>`).join("");
  $("#chips").innerHTML = S.kind==="compute" ? [2,4,8].map(x=>`<button type="button" class="chip" data-r="${x}" aria-pressed="${x===S.ratio}">${x} GB per vCPU</button>`).join("") : "";
  $("#list").innerHTML = S.kind==="compute" ? matrix() : ranked();
  $("#status").innerHTML = Object.entries(S.status).map(([n,s])=>s.pending?`${n}: da raccogliere`:s.ok?`${n}: ${s.count} voci${s.da_compilare?` (${s.da_compilare} da compilare)`:""}`:`<span class="bad">${n}: errore, dati del ${s.date||"?"}</span>`).join("<br>");
}
function detail(key){
  const r = S.recs.find(x=>x.key===key); if(!r) return; const p = pts(r);
  $("#dlg").innerHTML = `<h3>${esc(r.provider)} ${esc(r.sku)}</h3><small>${esc(specOf(r))}</small>${r.stale?` <small class="stale">· dato non aggiornato</small>`:""}
    <svg class="big" viewBox="0 0 300 150" preserveAspectRatio="none"><path d="${path(p,300,150)}" vector-effect="non-scaling-stroke"/></svg>
    <table>${p.slice().reverse().map(q=>`<tr><td>${q[0].split("-").reverse().join("/")}</td><td>${num(q[1],q[1]<1?4:2)} ${esc(r.unit)}</td></tr>`).join("")}</table>
    ${r.source?`<p><a href="${esc(r.source)}" target="_blank" rel="noopener">Fonte</a></p>`:""}<button type="button" id="x">Chiudi</button>`;
  $("#dlg").showModal(); $("#x").onclick = ()=>$("#dlg").close();
}
document.addEventListener("click",e=>{
  const b = e.target.closest("button"); if(!b) return;
  if(b.dataset.k){ S.kind=b.dataset.k; render(); }
  else if(b.dataset.r){ S.ratio=+b.dataset.r; render(); }
  else if(b.dataset.sort){ S.sort=+b.dataset.sort; render(); }
  else if(b.dataset.key) detail(b.dataset.key);
  else if(b.id==="csv"){
    const rows = S.recs.filter(r=>r.kind===S.kind);
    const c = [["provider","regione","sku","vcpu","ram_gb","unita","prezzo","fonte"],...rows.map(r=>[r.provider,r.region,r.sku,r.vcpu??"",r.ram_gb??"",r.unit,r.price,r.source])]
      .map(l=>l.map(v=>`"${String(v).replace(/"/g,'""')}"`).join(";")).join("\n");
    const a = document.createElement("a"); a.href = URL.createObjectURL(new Blob(["\ufeff"+c],{type:"text/csv"})); a.download = `prezzi-${S.kind}-${S.updated}.csv`; a.click();
  }
});
if("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js");
load();
