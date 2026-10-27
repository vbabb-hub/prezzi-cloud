import json, pathlib, datetime as dt, traceback
import yaml
import azure, aws, ovh, hetzner, gcp, linode, vultr, oracle

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "docs" / "data"
(DATA / "history").mkdir(parents=True, exist_ok=True)
today = dt.datetime.now(dt.timezone.utc).date().isoformat()


def load(p, default):
    return json.loads(p.read_text()) if p.exists() else default


prev = load(DATA / "latest.json", {"records": []})["records"]
old_status = load(DATA / "status.json", {})
status, records = {}, []

SOURCES = (("azure", azure.collect), ("azure+", azure.extra), ("azure-ri", azure.reserved), ("aws", aws.collect), ("aws+", aws.extra), ("aws-s3", aws.s3),
           ("ovh", ovh.collect), ("ovh+", ovh.extra), ("gcp", gcp.collect), ("gcp+", gcp.extra), ("gcp-cud", gcp.cud), ("gcp-gcs", gcp.gcs), ("hetzner", hetzner.collect),
           ("azure-gpu", azure.gpu), ("gcp-gpu", gcp.gpu), ("oracle", oracle.collect), ("vultr", vultr.collect), ("linode", linode.collect))
for name, fn in SOURCES:
    old = [r for r in prev if r.get("src") == name]
    try:
        new = fn()
        if len(old) > 10 and len(new) < len(old) * 0.5:
            raise RuntimeError(f"solo {len(new)} record contro {len(old)}: formato API cambiato?")
        if not new:
            raise RuntimeError("nessun record restituito")
        for r in new:
            r["src"] = name
        records += new
        status[name] = dict(ok=True, count=len(new), date=today)
    except Exception as e:
        traceback.print_exc()
        for r in old:   # mantiene l'ultimo dato noto, segnalato come non aggiornato
            r["stale"] = True
        records += old
        status[name] = dict(ok=False, error=str(e)[:200], count=len(old), date=old_status.get(name, {}).get("date"))

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
