import re
from common import get, vm, TIERS

REGIONS = ["italynorth", "westeurope"]
GB_PER_VCPU = {"D": 4, "E": 8, "F": 2}   # RAM non presente nelle API retail: stimata per famiglia
RX = re.compile(r"^Standard_([DEF])(\d+)[a-z]*_v(\d)$")
URL = "https://prices.azure.com/api/retail/prices"


def collect():
    best = {}
    for region in REGIONS:
        url = URL
        params = {"api-version": "2023-01-01-preview", "currencyCode": "EUR",
                  "$filter": f"serviceName eq 'Virtual Machines' and armRegionName eq '{region}' and priceType eq 'Consumption'"}
        while url:
            d = get(url, params=params).json()
            params = None
            url = d.get("NextPageLink")
            for i in d["Items"]:
                m = RX.match(i.get("armSkuName", ""))
                if not m or i.get("unitOfMeasure") != "1 Hour":
                    continue
                fam, n, ver = m.group(1), int(m.group(2)), m.group(3)
                if (fam in "DE" and ver != "5") or (fam == "F" and ver != "2") or n not in TIERS:
                    continue
                txt = " ".join([i.get("productName", ""), i.get("skuName", ""), i.get("meterName", "")])
                if any(x in txt for x in ("Windows", "Spot", "Low Priority")):
                    continue
                k = (region, i["armSkuName"])
                if k not in best or i["retailPrice"] < best[k][0]:
                    best[k] = (i["retailPrice"], n, fam)
    return [vm("Azure", r, s.replace("Standard_", ""), n, n * GB_PER_VCPU[f], p, source=URL)
            for (r, s), (p, n, f) in best.items() if p > 0]


def _items(flt):
    url, params, out = URL, {"api-version": "2023-01-01-preview", "currencyCode": "EUR", "$filter": flt}, []
    while url:
        d = get(url, params=params).json()
        params, url = None, d.get("NextPageLink")
        out += d["Items"]
    return out


def extra():
    out = []
    for region in REGIONS:
        it = _items(f"serviceName eq 'Storage' and armRegionName eq '{region}' and priceType eq 'Consumption' and meterName eq 'Hot LRS Data Stored'")
        p = [i["retailPrice"] for i in it if i["unitOfMeasure"] == "1 GB/Month" and "Block Blob" in i["productName"]
             and i["retailPrice"] > 0 and not i.get("tierMinimumUnits")]
        if p:
            out.append(dict(provider="Azure", region=region, kind="storage", sku="Blob Hot LRS (object)", unit="EUR/GB/mese",
                            price=min(p), source=URL))
    it = _items("serviceName eq 'Bandwidth' and priceType eq 'Consumption' and meterName eq 'Standard Data Transfer Out' and armRegionName eq 'Zone 1'")
    p = [i["retailPrice"] for i in it if i["retailPrice"] > 0]
    if p:
        out.append(dict(provider="Azure", region="Zone 1 (Europa)", kind="rete", sku="Data transfer out (Internet)",
                        unit="EUR/TB", price=round(min(p) * 1000, 3), source=URL))
    return out
