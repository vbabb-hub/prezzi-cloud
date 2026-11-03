"""Oracle Cloud: Price List API pubblica (Cost Estimator, anonima, nessuna chiave), prezzi in EUR. Il listino è globale
(Milano inclusa). Compute Standard E4 ed E5 Flex (1 OCPU = 2 vCPU; prezzo = OCPU/ora + GB di RAM/ora, 4 GB per vCPU,
senza storage), Block Volume, Object Storage, traffico in uscita e GPU. Se una voce non si trova nel listino non viene
inventata: finisce tra gli avvisi di status.json. Verificare il formato al primo run."""
import re
from common import get, vm, usd_eur, sanitize, TIERS

URL = "https://apexapps.oracle.com/pls/apex/cetools/api/v1/products/?currencyCode=EUR"
REGION = "globale (Milano inclusa)"
FLEX = ("E4", "E5")
GPU_KEYS = ("H200", "H100", "A100", "A10", "L40S", "V100", "P100", "B200")
WARNINGS = []


def _tiers(item, fx):
    """[(rangeMin, EUR)] del prezzo pay-as-you-go, in ordine di scaglione."""
    out = []
    for loc in item.get("currencyCodeLocalizations", []):
        for p in loc.get("prices", []):
            if p.get("model") in (None, "", "PAY_AS_YOU_GO") and p.get("value") is not None:
                out.append((float(p.get("rangeMin") or 0), float(p["value"]) * (fx() if loc.get("currencyCode") == "USD" else 1)))
    return sorted(out)


def _first(item, fx):
    t = _tiers(item, fx)
    return t[0][1] if t else None


def collect():
    WARNINGS.clear()
    items = get(URL).json()["items"]
    cache = {}

    def fx():
        if "v" not in cache:
            cache["v"] = usd_eur()
        return cache["v"]

    ocpu, mem, out = {}, {}, []
    found = {"block": None, "object": None, "egress": None}
    for it in items:
        n, metric = it.get("displayName", ""), it.get("metricName", "") or ""
        if "Windows" in n:
            continue
        for f in FLEX:
            if re.search(rf"Standard\s*[-–]\s*{f}\s*[-–]\s*OCPU", n):
                ocpu[f] = _first(it, fx)
            elif re.search(rf"Standard\s*[-–]\s*{f}\s*[-–]\s*Memory", n):
                mem[f] = _first(it, fx)
        if re.match(r"Block Volume\s*[-–]\s*Storage", n):
            found["block"] = _first(it, fx)
        elif re.match(r"Object Storage\s*[-–]\s*Storage", n) and not re.search(r"Infrequent|Archive", n):
            found["object"] = _first(it, fx)
        elif re.search(r"Outbound Data Transfer", n, re.I):
            pos = [v for _, v in _tiers(it, fx) if v > 0]
            found["egress"] = pos[0] * 1000 if pos else found["egress"]
        elif "GPU" in metric.upper() and any(k in n.upper() for k in GPU_KEYS):
            p = _first(it, fx)
            if p and p > 0:
                out.append(dict(provider="Oracle Cloud", region=REGION, kind="gpu", sku=n, unit="EUR/ora", price=round(p, 4),
                                term="On-demand", source=URL, note="prezzo per GPU, include vCPU e RAM dell'istanza"))
    for f in FLEX:
        o, m = ocpu.get(f), mem.get(f)
        if not o or not m or not (0.005 < o < 0.2 and 0.0003 < m < 0.02):
            WARNINGS.append(f"{f} Flex: prezzi OCPU/memoria non trovati o fuori scala")
            continue
        for n in sorted(TIERS):
            out.append(vm("Oracle Cloud", REGION, f"VM.Standard.{f}.Flex {n} vCPU", n, n * 4, (n / 2) * o + n * 4 * m, source=URL,
                          term="On-demand", note="1 OCPU = 2 vCPU; senza storage"))
    if not any(r["kind"] == "compute" for r in out):
        raise RuntimeError("Oracle: nessun prezzo E4/E5 Flex nel listino. " + "; ".join(WARNINGS))
    for key, sku, kind, unit in (("block", "Block Volume", "storage", "EUR/GB/mese"), ("object", "Object Storage Standard", "storage", "EUR/GB/mese"),
                                 ("egress", "Egress Internet (primo scaglione a pagamento)", "rete", "EUR/TB")):
        if found[key]:
            out.append(dict(provider="Oracle Cloud", region=REGION, kind=kind, sku=sku, unit=unit, price=round(found[key], 5), term="On-demand", source=URL))
        else:
            WARNINGS.append(f"{sku}: voce non trovata nel listino")
    return out
