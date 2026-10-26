const $ = s => document.querySelector(s);
const KINDS = [["compute","Compute"],["storage","Storage"],["rete","Rete"],["gpu","GPU"],["licenza","Licenze"]];
const S = {kind:"compute", prov:new Set(), vcpu:"", recs:[], series:{}, status:{}, updated:""};
const num = (n,d=2) => n.toLocaleString("it-IT",{minimumFractionDigits:d,maximumFractionDigits:d});
const hue = p => [...p].reduce((h,c)=>(h*31+c.charCodeAt(0))%360,7);
const esc = s => String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));

async function load(){
  const j = u => fetch(u,{cache:"no-cache"}).then(r=>r.ok?r.json():null).catch(()=>null);
  const [l,s,st] = await Promise.all([j("data/latest.json"),j("data/series.json"),j("data/status.json")]);
  S.recs = l?.records||[]; S.updated = l?.updated||""; S.series = s||{}; S.status = st||{};
  render();
}
const pts = r => { const s=(S.series[r.key]||[]).slice(); if(s.length && s.at(-1)[0]<S.updated) s.push([S.updated,s.at(-1)[1]]); return s; };
function ago(r,days){
  const t=new Date(S.updated||Date.now()); t.setDate(t.getDate()-days); const lim=t.toISOString().slice(0,10);
  let v=null; for(const [d,p] of S.series[r.key]||[]){ if(d<=lim) v=p; else break; } return v;
}
function path(p,w,h){
  const xs=p.map(q=>+new Date(q[0])), ys=p.map(q=>q[1]), lo=Math.min(...ys), hi=Math.max(...ys);
  const X=t=>(t-xs[0])/((xs.at(-1)-xs[0])||1)*w, Y=v=>h-3-(v-lo)/((hi-lo)||1)*(h-6);
  let d=`M${X(xs[0])},${Y(ys[0])}`; for(let i=1;i<p.length;i++) d+=`H${X(xs[i])}V${Y(ys[i])}`;
  return p.length<2 ? `M0,${h/2}H${w}` : d+`H${w}`;
}
function render(){
  $("#meta").textContent = S.updated ? `Aggiornato al ${S.updated.split("-").reverse().join("/")} · listino IVA esclusa` : "Nessun dato: esegui il workflow su GitHub Actions";
  $("#kinds").innerHTML = KINDS.map(([k,l])=>`<button type="button" data-k="${k}" aria-pressed="${k===S.kind}">${l}</button>`).join("");
  const ofKind = S.recs.filter(r=>r.kind===S.kind);
  const provs = [...new Set(ofKind.map(r=>r.provider))].sort();
  $("#chips").innerHTML = provs.map(p=>`<button type="button" class="chip" data-p="${esc(p)}" style="--c:hsl(${hue(p)} 55% 45%)" aria-pressed="${S.prov.has(p)}"><i></i>${esc(p)}</button>`).join("");
  $("#vc").hidden = S.kind!=="compute";
  const rows = ofKind.filter(r=>(!S.prov.size||S.prov.has(r.provider)) && (!S.vcpu||r.vcpu==S.vcpu));
  const groups = {}; rows.forEach(r=>(groups[r.unit]??=[]).push(r));
  $("#list").innerHTML = Object.entries(groups).map(([u,g])=>{
    g.sort((a,b)=>a.price-b.price); const max=g.at(-1).price||1;
    return `<h2>${esc(u)}</h2>`+g.map(r=>{
      const old=ago(r,30), dl=old&&old!==r.price?(r.price/old-1)*100:null;
      const spec=[r.vcpu&&`${r.vcpu} vCPU`, r.ram_gb&&`${num(+r.ram_gb,0)} GB`, r.region].filter(Boolean).join(" · ");
      return `<button type="button" class="row" data-key="${esc(r.key)}" style="--w:${Math.max(4,r.price/max*100)}">
        <span><b>${esc(r.provider)}</b> ${esc(r.sku)}<small>${esc(spec)}${r.stale?' · <span class="stale">non aggiornato</span>':""}</small></span>
        <span class="price">${num(r.price, r.price<1?4:2)}<small class="${dl>0?"up":"down"}">${dl==null?"":(dl>0?"+":"")+num(dl,1)+"% 30g"}</small></span>
        <svg class="sp" viewBox="0 0 64 20"><path d="${path(pts(r),64,20)}"/></svg></button>`;
    }).join("");
  }).join("") || `<p class="empty">Nessuna voce per questi filtri. Le voci manuali compaiono dopo aver compilato i file in <code>manual/</code>.</p>`;
  $("#status").innerHTML = Object.entries(S.status).map(([n,s])=>s.ok?`${n}: ${s.count} voci${s.da_compilare?` (${s.da_compilare} da compilare)`:""}`:`<span class="bad">${n}: errore, dati del ${s.date||"?"}</span>`).join("<br>");
}
function detail(key){
  const r=S.recs.find(x=>x.key===key); if(!r) return; const p=pts(r);
  $("#dlg").innerHTML = `<h3>${esc(r.provider)} ${esc(r.sku)}</h3><small>${esc([r.vcpu&&r.vcpu+" vCPU", r.ram_gb&&r.ram_gb+" GB", r.region].filter(Boolean).join(" · "))}</small>
    <svg class="big" viewBox="0 0 300 150" preserveAspectRatio="none"><path d="${path(p,300,150)}" vector-effect="non-scaling-stroke"/></svg>
    <table>${p.slice().reverse().map(q=>`<tr><td>${q[0].split("-").reverse().join("/")}</td><td>${num(q[1],q[1]<1?4:2)} ${esc(r.unit)}</td></tr>`).join("")}</table>
    ${r.source?`<p><a href="${esc(r.source)}" target="_blank" rel="noopener">Fonte</a></p>`:""}<button type="button" id="x">Chiudi</button>`;
  $("#dlg").showModal(); $("#x").onclick=()=>$("#dlg").close();
}
document.addEventListener("click",e=>{
  const b=e.target.closest("button"); if(!b) return;
  if(b.dataset.k){S.kind=b.dataset.k;S.prov.clear();S.vcpu="";$("#vcpu").value="";render();}
  else if(b.dataset.p){S.prov.has(b.dataset.p)?S.prov.delete(b.dataset.p):S.prov.add(b.dataset.p);render();}
  else if(b.dataset.key) detail(b.dataset.key);
  else if(b.id==="csv"){
    const rows=S.recs.filter(r=>r.kind===S.kind&&(!S.prov.size||S.prov.has(r.provider))&&(!S.vcpu||r.vcpu==S.vcpu));
    const c=[["provider","regione","sku","vcpu","ram_gb","unita","prezzo","fonte"],...rows.map(r=>[r.provider,r.region,r.sku,r.vcpu??"",r.ram_gb??"",r.unit,r.price,r.source])]
      .map(l=>l.map(v=>`"${String(v).replace(/"/g,'""')}"`).join(";")).join("\n");
    const a=document.createElement("a"); a.href=URL.createObjectURL(new Blob(["\ufeff"+c],{type:"text/csv"})); a.download=`prezzi-${S.kind}-${S.updated}.csv`; a.click();
  }
});
$("#vcpu").onchange=e=>{S.vcpu=e.target.value;render();};
if("serviceWorker" in navigator) navigator.serviceWorker.register("sw.js");
load();
