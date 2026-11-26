"""Polo Strategico Nazionale (PSN): listino ufficiale, canoni ANNUALI in EUR per le PA italiane.
I dati stanno in collectors/psn_listino.json, generato da tools/import_psn.py dal file Excel del PSN (ogni release si importa con un solo
comando). Si leggono tre fogli: il catalogo "Industry Standard-Integrazione" (housing, hosting, compute, GPU, Kubernetes, storage, sistemi
operativi, rete, sicurezza, database, middleware, protezione dati, infrastruttura e operations, big data, AI, VDI, collaboration, supporto),
"Hybrid Cloud on PSN site" e i servizi professionali. Il prezzo mostrato è il canone annuale diviso 12 (per le GPU, diviso 8.760 ore; per
lo storage con quantità in GB, per GB al mese); il canone annuale originale è nella nota. Le voci "non appena disponibili" non hanno prezzo e non
sono incluse. Non letti: i cataloghi dei grandi provider rivenduti dal PSN (Secure Public Cloud) e Public Cloud PSN Managed."""
import json
import pathlib
import re
from collections import Counter
from common import vm

DATA = pathlib.Path(__file__).with_name("psn_listino.json")
PROVIDER, REGION = "Polo Strategico Nazionale", "IT"
URL = "https://www.polostrategiconazionale.it/"
HOURS_YEAR = 8760
WARNINGS = []


def _it(x, d=2):
    return f"{x:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def kind_of(fam, sub):
    f, s = (fam or "")[:2], (sub or "").upper()
    if f == "00":
        return "colocation"
    if f == "01":
        return {"SECURITY": "servizi", "STORAGE": "storage"}.get(s, "compute")
    if f == "02":
        if "GPU" in s:
            return "gpu"
        return "k8s" if (s.startswith("CAAS") or "KUBERNETES" in s) else "compute"
    return {"03": "storage", "04": "licenza", "05": "rete", "07": "dbaas"}.get(f, "servizi")


def _gb(row):
    """Quantità in GB a cui si riferisce il canone di una voce di storage, se ricavabile."""
    m = re.match(r"^(\d+(?:[.,]\d+)?)\s*(GB|TB)\b", str(row.get("mu") or ""), re.I)
    if m:
        q = float(m.group(1).replace(",", ".")) * (1000 if m.group(2).upper() == "TB" else 1) * (float(row["mv"]) if _num(row.get("mv")) else 1)
        return q or None
    m = re.search(r"\((\d+)\s*GB\)", str(row.get("el") or ""))
    if m:
        return float(m.group(1))
    st = row.get("storage")
    return float(st) if _num(st) and not row.get("mu") else None


def _tier(t):
    return re.sub(r"^\d+\.\s*", "", t or "").title()


def collect():
    WARNINGS.clear()
    d = json.loads(DATA.read_text(encoding="utf-8"))
    rel = d.get("release", "")
    entries, n_na = [], 0
    for row in d["industry"]:
        canone, ut = row.get("canone"), row.get("ut")
        if not _num(canone):
            n_na += 1
            continue
        kind = kind_of(row.get("fam"), row.get("sub"))
        el, tip, listino = row.get("el") or "", row.get("tip") or "", row.get("listino") or ""
        partenza = listino.upper().startswith("LISTINO DI PARTENZA")
        sku = f"{tip} - {el}" if partenza and tip and tip.lower() not in el.lower() else el
        mu, mv = row.get("mu"), row.get("mv")
        if kind == "gpu" and mu:                                   # il nome della GPU è nella metrica ("GPU H100", "GPU H100 condivisa (25%)")
            sku = f"{mu} (dedicata)" if "condivisa" not in str(mu).lower() else str(mu)
        if "(HA)" in str(row.get("sub") or "") and "(HA)" not in sku:
            sku += " (HA)"
        metric = f"{mv:g} {mu}"[:44] if mu and _num(mv) else (str(mu)[:44] if mu else "")
        term = "Impegno 1 anno"
        if canone == 0 and _num(ut) and ut > 0:
            unit, price, term = "EUR una tantum", ut, "On-demand"
        elif kind == "gpu":
            unit, price = "EUR/ora", canone / HOURS_YEAR
        elif kind == "storage" and _gb(row):
            unit, price = "EUR/GB/mese", canone / 12 / _gb(row)
        else:
            unit, price = "EUR/mese", canone / 12
        note = "; ".join(x for x in (
            "listino di partenza" if partenza else "prima integrazione", f"{row.get('fam')} / {row.get('sub')}", f"tier {_tier(row.get('tier'))}" if row.get("tier") else "",
            f"metrica: {metric}" if metric else "", f"canone annuale {_it(canone)} EUR" if unit != "EUR una tantum" else f"una tantum {_it(ut)} EUR",
            f"PSN {rel}", (row.get("desc") or "")[:120]) if x)
        entries.append(dict(kind=kind, sku=sku, unit=unit, price=price, term=term, note=note, tier=_tier(row.get("tier")), metric=metric,
                            vcpu=row.get("vcpu") if _num(row.get("vcpu")) and _num(row.get("vram")) else None, ram=row.get("vram")))
    for row in d.get("hybrid", []):
        if not _num(row.get("canone")):
            continue
        kind = {"Compute": "compute", "Kubernetes": "k8s", "SQL Data services": "dbaas"}.get(row["tip"], "servizi")
        extra = "; ".join(str(x) for x in (f"storage {row['storage']} GB" if row.get("storage") else "", row.get("desc") or "") if x)
        entries.append(dict(kind=kind, sku=f"Hybrid Cloud on PSN site - {row['tip']}: {row['el']}", unit="EUR/mese", price=row["canone"] / 12, term="Impegno 1 anno",
                            note=f"Hybrid Cloud on PSN site; canone annuale {_it(row['canone'])} EUR; PSN {rel}" + (f"; {extra}" if extra else ""), tier="", metric="", vcpu=None, ram=None))
    for row in d.get("servizi", []):
        entries.append(dict(kind="servizi", sku=f"Servizi professionali - {row['fig']}", unit="EUR/giorno", price=row["ut"], term="On-demand",
                            note=f"tariffa a giornata per persona; attività: {row.get('att') or 'n.d.'}; PSN {rel}", tier="", metric="", vcpu=None, ram=None))
    # nomi unici: se due voci hanno lo stesso nome si aggiunge prima la metrica, poi il tier, poi un numero
    for stage in ("metric", "tier", "n"):
        cnt = Counter((e["kind"], e["sku"], e["term"]) for e in entries)
        seen = Counter()
        for e in entries:
            k = (e["kind"], e["sku"], e["term"])
            if cnt[k] > 1:
                seen[k] += 1
                add = e["metric"] if stage == "metric" else e["tier"] if stage == "tier" else f"#{seen[k]}"
                if add:
                    e["sku"] = f"{e['sku']} ({add})"
    out = []
    for e in entries:
        price = round(e["price"], 4 if e["price"] < 1 else 2)
        if e["vcpu"] and e["kind"] == "compute":
            out.append(vm(PROVIDER, REGION, e["sku"], int(e["vcpu"]), float(e["ram"]), price / 730, monthly=price, source=URL, term=e["term"], note=e["note"]))
        else:
            out.append(dict(provider=PROVIDER, region=REGION, kind=e["kind"], sku=e["sku"], unit=e["unit"], price=price, term=e["term"], source=URL, note=e["note"]))
    if n_na:
        WARNINGS.append(f"{n_na} voci 'non appena disponibili' senza prezzo non incluse (release {rel})")
    return out
