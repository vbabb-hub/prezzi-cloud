import json, os, pathlib, sys, datetime as dt, traceback
import yaml
import aws, ovh, hetzner, gcp, linode, vultr, oracle, aruba, seeweb, stackit, proxmox, digitalocean, exoscale, entersuite
import aruba_enterprise, psn, azure_cloud as azure_coll
from common import Skip, sanitize

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "docs" / "data"
(DATA / "history").mkdir(parents=True, exist_ok=True)
today = dt.datetime.now(dt.timezone.utc).date().isoformat()

def load(p, default):
    return json.loads(p.read_text()) if p.exists() else default

prev = load(DATA / "latest.json", {"records": []})["records"]
old_status = load(DATA / "status.json", {})
status, records = {}, []

SOURCES = (
    ("azure", azure_coll.collect),
    ("aws", aws.collect),
    ("ovh", ovh.collect),
    ("gcp", gcp.collect),
    ("hetzner", hetzner.collect),
    ("oracle", oracle.collect),
    ("vultr", vultr.collect),
    ("linode", linode.collect),
    ("aruba", aruba.collect),
    ("aruba-enterprise", aruba_enterprise.collect),
    ("psn", psn.collect),
    ("seeweb", seeweb.collect),
    ("stackit", stackit.collect),
    ("digitalocean", digitalocean.collect),
    ("exoscale", exoscale.collect),
    ("entersuite", entersuite.collect),
    ("proxmox", proxmox.collect)
)

# Collector corretti: i dati salvati prima della correzione (tabelle "stimate") non vanno mai riutilizzati come ripiego.
CORRECTED = {"aws", "azure", "gcp", "hetzner", "aruba", "seeweb", "oracle", "digitalocean", "stackit", "exoscale", "entersuite", "proxmox", "aruba-enterprise", "psn"}

for name, fn in SOURCES:
    old = [r for r in prev if r.get("src") == name]
    if name in CORRECTED and old_status.get(name, {}).get("verified_schema") != 1:
        old = []
    try:
        new = fn()
        if not new:
            raise Skip("nessun record")
        for r in new:
            r["src"] = name
        records += new
        status[name] = dict(ok=True, count=len(new), date=today, **({"verified_schema": 1} if name in CORRECTED else {}))
        notes = list(dict.fromkeys(getattr(sys.modules.get(fn.__module__), "WARNINGS", [])))
        if len(old) > 10 and len(new) < len(old) * 0.5:   # avviso, non scarto: i dati nuovi restano
            notes.append(f"record calati da {len(old)} a {len(new)}: possibile cambio di formato della fonte")
        if notes:
            status[name]["note"] = sanitize("; ".join(notes))[:300]
    except Skip as e:
        records += old
        status[name] = dict(ok=True, count=len(old), note=sanitize(str(e))[:200], date=today, **({"verified_schema": 1} if name in CORRECTED else {}))
    except Exception as e:
        print(f"ERRORE NEL COLLECTOR '{name}': {sanitize(str(e))}")
        print(sanitize(traceback.format_exc()))
        for r in old:
            r["stale"] = True
        records += old
        status[name] = dict(ok=False, error=sanitize(str(e))[:200], count=len(old), date=old_status.get(name, {}).get("date"),
                            **({"verified_schema": old_status.get(name, {}).get("verified_schema")} if name in CORRECTED else {}))

todo, manual = [], 0
for f in sorted((ROOT / "manual").glob("*.yml")):
    for e in (yaml.safe_load(f.read_text()) or {}).get("entries", []):
        if e.get("price") is None:
            todo.append(f"{e['provider']} / {e['sku']}")
            continue
        e["src"] = "manual"
        records.append(e)
        manual += 1
status["manual"] = dict(ok=True, count=manual, date=today, da_compilare=len(todo))

series = load(DATA / "series.json", {})
for r in records:
    r["key"] = "|".join(str(r.get(k, "")) for k in ("provider", "region", "kind", "sku")) + ("|" + r["term"] if r.get("term") else "")
    s = series.setdefault(r["key"], [])
    if not r.get("stale") and (not s or s[-1][1] != r["price"]):
        s.append([today, r["price"]])

dump = lambda o, **k: json.dumps(o, ensure_ascii=False, **k)
(DATA / "latest.json").write_text(dump(dict(updated=today, records=records), separators=(",", ":")))
(DATA / "series.json").write_text(dump(series, separators=(",", ":")))
(DATA / "status.json").write_text(dump(status, indent=1))
(DATA / "history" / f"{today}.json").write_text(dump({r["key"]: r["price"] for r in records}, separators=(",", ":")))
print(f"{today}: {len(records)} record, {len(todo)} voci manuali da compilare")

# Riepilogo leggibile nella pagina del run su GitHub Actions
summary = os.environ.get("GITHUB_STEP_SUMMARY")
if summary:
    rows = ["| Fonte | Stato | Voci | Note |", "|---|---|---|---|"]
    for n, s in status.items():
        rows.append(f"| {n} | {'ok' if s.get('ok') else 'ERRORE'} | {s.get('count', '')} | {str(s.get('note') or s.get('error') or '').replace('|', '/')} |")
    with open(summary, "a", encoding="utf-8") as f:
        f.write("\n".join(rows) + "\n")
