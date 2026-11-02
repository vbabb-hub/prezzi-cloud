"""GCP: Cloud Billing Catalog API ufficiale. Serve una chiave API gratuita nel secret GCP_API_KEY (limitata alla sola
Cloud Billing API); senza chiave la fonte viene saltata e GCP resta vuoto: nessun prezzo stimato. Prezzi in EUR.
Compute N2 (core + RAM), Committed Use 1 e 3 anni, Persistent Disk Balanced, Cloud Storage Standard, GPU, traffico."""
import os, re
from common import get, vm, sanitize, Skip, TIERS

SVC = "https://cloudbilling.googleapis.com/v1/services/6F81-5844-456A/skus"   # Compute Engine
GCS = "https://cloudbilling.googleapis.com/v1/services/95FF-2EF5-5EA1/skus"   # Cloud Storage
CITY = {"europe-west8": "Milan", "europe-west3": "Frankfurt"}   # nome usato da Google nelle descrizioni delle SKU
REGIONS = set(CITY)
GPU_REGIONS = {"europe-west4", "europe-west3", "europe-west1", "europe-west8"}
LABEL = {"europe-west8": "Milano", "europe-west3": "Francoforte", "europe-west4": "Paesi Bassi", "europe-west1": "Belgio"}
BAD = ("Spot", "Preemptible", "Commitment", "Custom", "Sole Tenant", "Extended", "Confidential")
CUD = re.compile(r"^Commitment v1: N2 (Cpu|Ram) in (.+) for (1|3) Years?$")
GPU_RX = re.compile(r"^Nvidia (?:Tesla )?(A100 80GB|A100|H100 80GB|L4|L40S) GPU running in (.+)$")
GPU_MODEL = {"A100": "NVIDIA A100 40GB", "A100 80GB": "NVIDIA A100 80GB", "H100 80GB": "NVIDIA H100 80GB", "L4": "NVIDIA L4 24GB", "L40S": "NVIDIA L40S 48GB"}
TERM = {"1": "Impegno 1 anno", "3": "Impegno 3 anni"}
WARNINGS = []


def _lab(r):
    return f"{r} ({LABEL[r]})"


def _tiers(s):
    return [int(t["unitPrice"].get("units", 0) or 0) + t["unitPrice"].get("nanos", 0) / 1e9
            for t in s["pricingInfo"][0]["pricingExpression"]["tieredRates"]]


def _skus(key, svc):
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


def _compute(key, out):
    core, ram, cud_core, cud_ram, disk, egr, gpu = {}, {}, {}, {}, {}, {}, {}
    for s in _skus(key, SVC):
        c, desc, regs = s.get("category", {}), s["description"], set(s.get("serviceRegions", []))
        m = CUD.match(desc)
        if m and regs & REGIONS:
            (cud_core if m.group(1) == "Cpu" else cud_ram)[(next(iter(regs & REGIONS)), m.group(3))] = _tiers(s)[0]
            continue
        if any(b in desc for b in BAD) or c.get("usageType") != "OnDemand":
            continue
        p = _tiers(s)
        if regs & REGIONS:
            r = next(iter(regs & REGIONS))
            if desc == f"N2 Instance Core running in {CITY[r]}":
                core[r] = p[0]
            elif desc == f"N2 Instance Ram running in {CITY[r]}":
                ram[r] = p[0]
            elif desc.startswith("Balanced PD Capacity"):
                disk[r] = p[0]
            elif c.get("resourceGroup") == "PremiumInternetEgress" and "Worldwide" in desc:
                pos = [x for x in p if x > 0]
                if pos:
                    egr[r] = min(egr.get(r, 9e9), pos[0])
        mg = GPU_RX.match(desc)
        if mg and regs & GPU_REGIONS and p[0] > 0:
            k = (next(iter(regs & GPU_REGIONS)), mg.group(1))
            gpu[k] = min(gpu.get(k, 9e9), p[0])
    for r in core:
        if r in ram:
            for n in sorted(TIERS):
                out.append(vm("GCP", _lab(r), f"n2-standard-{n}", n, n * 4, n * core[r] + n * 4 * ram[r], source=SVC,
                              term="On-demand", note="Compute Engine on-demand, Linux"))
    for (r, t), c in cud_core.items():
        if (r, t) in cud_ram:
            for n in sorted(TIERS):
                out.append(vm("GCP", _lab(r), f"n2-standard-{n}", n, n * 4, n * c + n * 4 * cud_ram[(r, t)], source=SVC,
                              term=TERM[t], note="Committed Use Discount, Linux"))
    for r, v in disk.items():
        out.append(dict(provider="GCP", region=_lab(r), kind="storage", sku="Persistent Disk Balanced (block)",
                        unit="EUR/GB/mese", price=round(v, 5), term="On-demand", source=SVC))
    for r, v in egr.items():
        out.append(dict(provider="GCP", region=_lab(r), kind="rete", sku="Egress Internet (primo scaglione a pagamento)",
                        unit="EUR/TB", price=round(v * 1000, 3), term="On-demand", source=SVC))
    for (r, model), v in gpu.items():
        out.append(dict(provider="GCP", region=_lab(r), kind="gpu", sku=GPU_MODEL[model], unit="EUR/ora",
                        price=round(v, 4), term="On-demand", source=SVC, note="solo GPU: vCPU e RAM della VM a parte"))


def _gcs(key, out):
    best = {}
    for s in _skus(key, GCS):
        c, d = s.get("category", {}), s["description"]
        regs = set(s.get("serviceRegions", [])) & REGIONS
        if regs and c.get("usageType") == "OnDemand" and c.get("resourceGroup") == "RegionalStorage" and d.startswith("Standard Storage") \
                and "Dual" not in d and "Multi" not in d:
            best[next(iter(regs))] = _tiers(s)[0]
    for r, v in best.items():
        if v > 0:
            out.append(dict(provider="GCP", region=_lab(r), kind="storage", sku="Cloud Storage Standard (object)",
                            unit="EUR/GB/mese", price=round(v, 5), term="On-demand", source=GCS))


def collect():
    WARNINGS.clear()
    key = os.environ.get("GCP_API_KEY")
    if not key:
        raise Skip("GCP_API_KEY non impostato: nessun dato GCP (serve una chiave gratuita per la Cloud Billing API)")
    out = []
    _compute(key, out)
    if not any(r["kind"] == "compute" for r in out):
        raise RuntimeError("GCP: nessun prezzo compute letto dal catalogo")
    try:
        _gcs(key, out)
    except Exception as e:
        WARNINGS.append(f"Cloud Storage: {sanitize(str(e))[:80]}")
    return out
