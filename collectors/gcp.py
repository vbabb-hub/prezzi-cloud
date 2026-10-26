import os, re
from common import get, vm, TIERS

SVC = "https://cloudbilling.googleapis.com/v1/services/6F81-5844-456A/skus"   # Compute Engine
REGIONS = {"europe-west8": "Milan", "europe-west3": "Frankfurt"}
BAD = ("Spot", "Preemptible", "Commitment", "Custom", "Sole Tenant", "Extended", "Confidential")
_EXTRA = []


def _tiers(s):
    tr = s["pricingInfo"][0]["pricingExpression"]["tieredRates"]
    return [int(t["unitPrice"].get("units", 0) or 0) + t["unitPrice"].get("nanos", 0) / 1e9 for t in tr]


def _skus(key, svc=SVC):
    tok = None
    while True:
        p = {"key": key, "currencyCode": "EUR", "pageSize": 5000}
        if tok:
            p["pageToken"] = tok
        d = get(svc, params=p).json()
        yield from d.get("skus", [])
        tok = d.get("nextPageToken")
        if not tok:
            break


def collect():
    key = os.environ.get("GCP_API_KEY")
    if not key:
        raise RuntimeError("GCP_API_KEY non impostato (secret GitHub)")
    core, ram, disk, egr = {}, {}, {}, {}
    for s in _skus(key):
        c, desc = s.get("category", {}), s["description"]
        regs = set(s.get("serviceRegions", [])) & set(REGIONS)
        if not regs or c.get("usageType") != "OnDemand" or any(b in desc for b in BAD):
            continue
        r = next(iter(regs))
        p = _tiers(s)
        if desc == f"N2 Instance Core running in {REGIONS[r]}":
            core[r] = p[0]
        elif desc == f"N2 Instance Ram running in {REGIONS[r]}":
            ram[r] = p[0]
        elif desc.startswith("Balanced PD Capacity"):
            disk[r] = p[0]
        elif c.get("resourceGroup") == "PremiumInternetEgress" and "Worldwide" in desc:
            pos = [x for x in p if x > 0]
            if pos:
                egr[r] = min(egr.get(r, 9e9), pos[0])
    out = [vm("GCP", r, f"n2-standard-{n}", n, n * 4, n * core[r] + n * 4 * ram[r], source=SVC)
           for r in core if r in ram for n in sorted(TIERS)]
    _EXTRA[:] = [dict(provider="GCP", region=r, kind="storage", sku="Persistent Disk Balanced", unit="EUR/GB/mese",
                      price=v, source=SVC) for r, v in disk.items()]
    _EXTRA += [dict(provider="GCP", region=r, kind="rete", sku="Egress Internet (primo scaglione a pagamento)",
                    unit="EUR/TB", price=v * 1000, source=SVC) for r, v in egr.items()]
    return out


def extra():
    return list(_EXTRA)


GCS = "https://cloudbilling.googleapis.com/v1/services/95FF-2EF5-5EA1/skus"   # Cloud Storage


def gcs():
    key = os.environ.get("GCP_API_KEY")
    if not key:
        raise RuntimeError("GCP_API_KEY non impostato (secret GitHub)")
    best = {}
    for s in _skus(key, GCS):
        c, d = s.get("category", {}), s["description"]
        regs = set(s.get("serviceRegions", [])) & set(REGIONS)
        if regs and c.get("usageType") == "OnDemand" and c.get("resourceGroup") == "RegionalStorage" \
                and d.startswith("Standard Storage") and "Dual" not in d and "Multi" not in d:
            best[next(iter(regs))] = _tiers(s)[0]
    return [dict(provider="GCP", region=r, kind="storage", sku="Cloud Storage Standard (object)", unit="EUR/GB/mese",
                 price=v, source=GCS) for r, v in best.items() if v > 0]


CUD = re.compile(r"^Commitment v1: N2 (Cpu|Ram) in (.+) for (1|3) Years?$")


def cud():
    key = os.environ.get("GCP_API_KEY")
    if not key:
        raise RuntimeError("GCP_API_KEY non impostato (secret GitHub)")
    core, ram = {}, {}
    for s in _skus(key):
        m = CUD.match(s["description"])
        regs = set(s.get("serviceRegions", [])) & set(REGIONS)
        if m and regs:
            (core if m.group(1) == "Cpu" else ram)[(next(iter(regs)), m.group(3) + "y")] = _tiers(s)[0]
    return [vm("GCP", r, f"n2-standard-{n}", n, n * 4, n * core[(r, t)] + n * 4 * ram[(r, t)], source=SVC, term=t,
               note="Committed Use Discount") for (r, t) in core if (r, t) in ram for n in sorted(TIERS)]
