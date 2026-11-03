"""Azure: Retail Prices API ufficiale (pubblica, nessuna chiave), prezzi in EUR.
On-demand (pay-as-you-go), Reservation a 1 e 3 anni (prezzo totale del termine / mesi), Blob Hot LRS, traffico in uscita,
VM GPU. La RAM non è nell'API: è quella della famiglia (D v5 = 4, E v5 = 8, F v2 = 2 GB per vCPU). Nessun prezzo stimato."""
import re
from common import get, vm, sanitize, TIERS

URL = "https://prices.azure.com/api/retail/prices"
REGIONS = {"italynorth": "Milano", "westeurope": "Paesi Bassi"}
GB_PER_VCPU = {"D": 4, "E": 8, "F": 2}
RX = re.compile(r"^Standard_([DEF])(\d+)[a-z]*_v(\d)$")
RESERVATION = {"1 Year": ("Impegno 1 anno", 12), "3 Years": ("Impegno 3 anni", 36)}
GPU_SKUS = {"Standard_ND96isr_H100_v5": (8, "NVIDIA H100 80GB"), "Standard_NC40ads_H100_v5": (1, "NVIDIA H100 NVL 94GB"),
            "Standard_NC24ads_A100_v4": (1, "NVIDIA A100 80GB"), "Standard_NC96ads_A100_v4": (4, "NVIDIA A100 80GB"),
            "Standard_ND96amsr_A100_v4": (8, "NVIDIA A100 80GB")}
GPU_REGIONS = {"westeurope": "Paesi Bassi", "italynorth": "Milano", "swedencentral": "Svezia", "francecentral": "Francia"}
WARNINGS = []


def _items(flt):
    url, params, out = URL, {"api-version": "2023-01-01-preview", "currencyCode": "EUR", "$filter": flt}, []
    while url:
        d = get(url, params=params).json()
        params, url = None, d.get("NextPageLink")
        out += d["Items"]
    return out


def _family_ok(m):
    fam, n, ver = m.group(1), int(m.group(2)), m.group(3)
    return n in TIERS and ((fam in "DE" and ver == "5") or (fam == "F" and ver == "2"))


def _compute(region, out):
    label = f"{region} ({REGIONS[region]})"
    best = {}
    for i in _items(f"serviceName eq 'Virtual Machines' and armRegionName eq '{region}' and priceType eq 'Consumption'"):
        m = RX.match(i.get("armSkuName", ""))
        txt = " ".join([i.get("productName", ""), i.get("skuName", ""), i.get("meterName", "")])
        if not m or not _family_ok(m) or i.get("unitOfMeasure") != "1 Hour" or i["retailPrice"] <= 0 or any(x in txt for x in ("Windows", "Spot", "Low Priority")):
            continue
        k = i["armSkuName"]
        if k not in best or i["retailPrice"] < best[k][0]:
            best[k] = (i["retailPrice"], m)
    for sku, (hourly, m) in best.items():
        n = int(m.group(2))
        out.append(vm("Azure", label, sku.replace("Standard_", ""), n, n * GB_PER_VCPU[m.group(1)], hourly, source=URL,
                      term="On-demand", note="pay-as-you-go, Linux"))
    res = {}
    for i in _items(f"serviceName eq 'Virtual Machines' and armRegionName eq '{region}' and priceType eq 'Reservation'"):
        m, t = RX.match(i.get("armSkuName", "")), RESERVATION.get(i.get("reservationTerm"))
        if not m or not t or not _family_ok(m) or i["retailPrice"] <= 0:
            continue
        k, monthly = (i["armSkuName"], t[0]), i["retailPrice"] / t[1]
        if k not in res or monthly < res[k][0]:
            res[k] = (monthly, m)
    for (sku, term), (monthly, m) in res.items():
        n = int(m.group(2))
        out.append(vm("Azure", label, sku.replace("Standard_", ""), n, n * GB_PER_VCPU[m.group(1)], monthly / 730, monthly=monthly,
                      source=URL, term=term, note="Reservation (prezzo del termine / mesi)"))


def _storage_network(out):
    for region in REGIONS:
        it = _items(f"serviceName eq 'Storage' and armRegionName eq '{region}' and priceType eq 'Consumption' and meterName eq 'Hot LRS Data Stored'")
        p = [i["retailPrice"] for i in it if i["unitOfMeasure"] == "1 GB/Month" and "Block Blob" in i["productName"]
             and i["retailPrice"] > 0 and not i.get("tierMinimumUnits")]
        if p:
            out.append(dict(provider="Azure", region=f"{region} ({REGIONS[region]})", kind="storage", sku="Blob Hot LRS (object)",
                            unit="EUR/GB/mese", price=min(p), term="On-demand", source=URL))
    it = _items("serviceName eq 'Bandwidth' and priceType eq 'Consumption' and meterName eq 'Standard Data Transfer Out' and armRegionName eq 'Zone 1'")
    p = [i["retailPrice"] for i in it if i["retailPrice"] > 0]
    if p:
        out.append(dict(provider="Azure", region="Zone 1 (Europa)", kind="rete", sku="Data transfer out (Internet)", unit="EUR/TB",
                        price=round(min(p) * 1000, 3), term="On-demand", source=URL, note="primo scaglione a pagamento"))


def _gpu(out):
    names = " or ".join(f"armSkuName eq '{n}'" for n in GPU_SKUS)
    best = {}
    for region in GPU_REGIONS:
        for i in _items(f"serviceName eq 'Virtual Machines' and armRegionName eq '{region}' and priceType eq 'Consumption' and ({names})"):
            txt = " ".join([i.get("productName", ""), i.get("skuName", ""), i.get("meterName", "")])
            if i.get("unitOfMeasure") != "1 Hour" or i["retailPrice"] <= 0 or any(x in txt for x in ("Windows", "Spot", "Low Priority")):
                continue
            n, model = GPU_SKUS[i["armSkuName"]]
            k = (region, i["armSkuName"])
            if k not in best or i["retailPrice"] / n < best[k]["price"]:
                nm = i["armSkuName"].replace("Standard_", "")
                best[k] = dict(provider="Azure", region=f"{region} ({GPU_REGIONS[region]})", kind="gpu", sku=f"{nm} ({n}x {model})", unit="EUR/ora",
                               price=round(i["retailPrice"] / n, 4), term="On-demand", source=URL,
                               note=f"prezzo per GPU; istanza intera {i['retailPrice']:.2f} EUR/ora, include vCPU e RAM")
    out.extend(best.values())


def collect():
    WARNINGS.clear()
    out = []
    for region in REGIONS:
        try:
            _compute(region, out)
        except Exception as e:
            WARNINGS.append(f"compute {region}: {sanitize(str(e))[:80]}")
    if not any(r["kind"] == "compute" for r in out):
        raise RuntimeError("Azure: nessun prezzo compute letto dalla Retail Prices API. " + "; ".join(WARNINGS))
    for fn in (_storage_network, _gpu):
        try:
            fn(out)
        except Exception as e:
            WARNINGS.append(f"{fn.__name__.strip('_')}: {sanitize(str(e))[:80]}")
    return out
