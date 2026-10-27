from common import get, vm, usd_eur, TIERS

REGIONS = ["eu-south-1", "eu-central-1", "eu-west-1"]   # Milano, Francoforte, Irlanda (più modelli GPU)
GPU_FAM = {"p5": "NVIDIA H100 80GB", "p4de": "NVIDIA A100 80GB", "p4d": "NVIDIA A100 40GB", "g6e": "NVIDIA L40S 48GB",
           "g6": "NVIDIA L4 24GB", "g5": "NVIDIA A10G 24GB"}
FAMILIES = ("m6i", "m7i")                  # general purpose, 4 GB/vCPU
BASE = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/{}/index.json"


_EXTRA = []


def _usd(d, sku):
    return [(pd.get("beginRange"), float(pd["pricePerUnit"]["USD"])) for t in d["terms"]["OnDemand"].get(sku, {}).values()
            for pd in t["priceDimensions"].values()]


def collect():
    fx, out = usd_eur(), []
    _EXTRA.clear()
    for region in REGIONS:
        d = get(BASE.format(region)).json()
        for sku, p in d["products"].items():
            a = p.get("attributes", {})
            if p.get("productFamily") == "Storage" and a.get("volumeApiName") == "gp3":
                v = [u for _, u in _usd(d, sku) if u > 0]
                if v:
                    _EXTRA.append(dict(provider="AWS", region=region, kind="storage", sku="EBS gp3", unit="EUR/GB/mese",
                                       price=round(v[0] * fx, 5), source=BASE.format(region)))
                continue
            if p.get("productFamily") == "Data Transfer" and a.get("transferType") == "AWS Outbound" and a.get("toLocation") == "External":
                v = sorted((float(b or 0), u) for b, u in _usd(d, sku) if u > 0)
                if v:
                    _EXTRA.append(dict(provider="AWS", region=region, kind="rete", sku="Data transfer out (Internet)",
                                       unit="EUR/TB", price=round(v[0][1] * fx * 1000, 3), source=BASE.format(region)))
                continue
            if p.get("productFamily") != "Compute Instance":
                continue
            if (a.get("operatingSystem"), a.get("tenancy"), a.get("preInstalledSw"), a.get("capacitystatus")) != ("Linux", "Shared", "NA", "Used"):
                continue
            it = a.get("instanceType", "")
            ngpu = int(a.get("gpu") or 0) if str(a.get("gpu") or "0").isdigit() else 0
            if it.split(".")[0] in GPU_FAM and ngpu:
                u = [x for _, x in _usd(d, sku) if x > 0]
                if u:
                    out.append(dict(provider="AWS", region=region, kind="gpu", sku=GPU_FAM[it.split(".")[0]], unit="EUR/ora",
                                    price=round(u[0] * fx / ngpu, 4), source=BASE.format(region),
                                    note=f"{it}: {ngpu} GPU, include vCPU e RAM"))
                continue
            if it.split(".")[0] not in FAMILIES or int(a["vcpu"]) not in TIERS:
                continue
            usd = [float(pd["pricePerUnit"]["USD"]) for t in d["terms"]["OnDemand"].get(sku, {}).values()
                   for pd in t["priceDimensions"].values()]
            usd = [u for u in usd if u > 0]
            if usd:
                out.append(vm("AWS", region, it, int(a["vcpu"]), float(a["memory"].split()[0].replace(",", "")),
                              usd[0] * fx, source=BASE.format(region)))
            for off in d["terms"].get("Reserved", {}).get(sku, {}).values():
                ta = off.get("termAttributes", {})
                term = {"1yr": "1y", "3yr": "3y"}.get(ta.get("LeaseContractLength"))
                if term and ta.get("OfferingClass") == "standard" and ta.get("PurchaseOption") == "No Upfront":
                    hr = [float(pd["pricePerUnit"]["USD"]) for pd in off["priceDimensions"].values() if pd.get("unit") == "Hrs"]
                    if hr and hr[0] > 0:
                        out.append(vm("AWS", region, it, int(a["vcpu"]), float(a["memory"].split()[0].replace(",", "")),
                                      hr[0] * fx, source=BASE.format(region), term=term, note="Reserved Standard, senza anticipo"))
        del d
    return out


def extra():
    return list(_EXTRA)


S3 = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/{}/index.json"


def s3():
    fx, out = usd_eur(), []
    for region in REGIONS:
        d = get(S3.format(region)).json()
        for sku, p in d["products"].items():
            a = p.get("attributes", {})
            if p.get("productFamily") == "Storage" and a.get("storageClass") == "General Purpose" and a.get("volumeType") == "Standard":
                v = sorted((float(b or 0), u) for b, u in _usd(d, sku) if u > 0)
                if v:
                    out.append(dict(provider="AWS", region=region, kind="storage", sku="S3 Standard (object)", unit="EUR/GB/mese",
                                    price=round(v[0][1] * fx, 5), source=S3.format(region)))
                break
        del d
    return out
