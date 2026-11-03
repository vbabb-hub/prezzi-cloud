"""AWS: Price List ufficiale (bulk JSON pubblico, nessuna chiave).
Legge on-demand e Reserved Standard senza anticipo (1 e 3 anni), istanze GPU (prezzo per GPU), EBS gp3, S3 Standard
e traffico in uscita. I dollari sono convertiti in euro col cambio del giorno. Nessun prezzo stimato nel codice."""
from common import get, vm, usd_eur, sanitize, TIERS

EC2 = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/{}/index.json"
S3 = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/{}/index.json"
REGIONS = {"eu-south-1": "Milano", "eu-central-1": "Francoforte", "eu-west-1": "Irlanda", "eu-north-1": "Stoccolma"}
S3_REGIONS = ("eu-south-1", "eu-central-1", "eu-west-1")
FAMILIES = ("m6i", "m7i", "c6i", "r6i")   # general purpose 4 GB/vCPU, compute 2, memory 8
GPU_FAM = {"p6-b200": "NVIDIA B200 180GB", "p5en": "NVIDIA H200 141GB", "p5e": "NVIDIA H200 141GB", "p5": "NVIDIA H100 80GB",
           "p4de": "NVIDIA A100 80GB", "p4d": "NVIDIA A100 40GB", "p3dn": "NVIDIA V100 32GB", "p3": "NVIDIA V100 16GB",
           "g6e": "NVIDIA L40S 48GB", "g6": "NVIDIA L4 24GB", "g5g": "NVIDIA T4G 16GB", "g5": "NVIDIA A10G 24GB", "g4dn": "NVIDIA T4 16GB"}
TERM = {"1yr": "Impegno 1 anno", "3yr": "Impegno 3 anni"}
WARNINGS = []


def _dims(d, sku, kind="OnDemand"):
    """[(beginRange, usd/unità)] per l'on-demand."""
    return [(float(pd.get("beginRange") or 0), float(pd["pricePerUnit"]["USD"]))
            for off in d["terms"].get(kind, {}).get(sku, {}).values() for pd in off["priceDimensions"].values()]


def _ec2(region, fx, out):
    d = get(EC2.format(region)).json()
    label, src = f"{region} ({REGIONS[region]})", EC2.format(region)
    for sku, p in d["products"].items():
        a, fam = p.get("attributes", {}), p.get("productFamily")
        if fam == "Storage" and a.get("volumeApiName") == "gp3":
            v = [u for _, u in _dims(d, sku) if u > 0]
            if v:
                out.append(dict(provider="AWS", region=label, kind="storage", sku="EBS gp3 (block)", unit="EUR/GB/mese",
                                price=round(v[0] * fx, 5), term="On-demand", source=src))
            continue
        if fam == "Data Transfer" and a.get("transferType") == "AWS Outbound" and a.get("toLocation") == "External":
            v = sorted((b, u) for b, u in _dims(d, sku) if u > 0)
            if v:
                out.append(dict(provider="AWS", region=label, kind="rete", sku="Data transfer out (Internet)", unit="EUR/TB",
                                price=round(v[0][1] * fx * 1000, 3), term="On-demand", source=src,
                                note="primo scaglione a pagamento"))
            continue
        if fam != "Compute Instance" or (a.get("operatingSystem"), a.get("tenancy"), a.get("preInstalledSw"), a.get("capacitystatus")) != ("Linux", "Shared", "NA", "Used"):
            continue
        it = a.get("instanceType", "")
        f = it.split(".")[0]
        ngpu = int(a["gpu"]) if str(a.get("gpu") or "").isdigit() else 0
        usd = [u for _, u in _dims(d, sku) if u > 0]
        if f in GPU_FAM and ngpu and usd:
            out.append(dict(provider="AWS", region=label, kind="gpu", sku=f"{it} ({ngpu}x {GPU_FAM[f]})", unit="EUR/ora",
                            price=round(usd[0] * fx / ngpu, 4), term="On-demand", source=src,
                            note=f"prezzo per GPU; istanza intera {usd[0] * fx:.2f} EUR/ora, include vCPU e RAM"))
            continue
        if f not in FAMILIES or not a.get("vcpu", "").isdigit() or int(a["vcpu"]) not in TIERS or not usd:
            continue
        v, ram = int(a["vcpu"]), float(a["memory"].split()[0].replace(",", ""))
        out.append(vm("AWS", label, it, v, ram, usd[0] * fx, source=src, term="On-demand", note="EC2 on-demand, Linux"))
        for off in d["terms"].get("Reserved", {}).get(sku, {}).values():
            ta = off.get("termAttributes", {})
            if ta.get("OfferingClass") == "standard" and ta.get("PurchaseOption") == "No Upfront" and ta.get("LeaseContractLength") in TERM:
                hr = [float(pd["pricePerUnit"]["USD"]) for pd in off["priceDimensions"].values() if pd.get("unit") == "Hrs"]
                if hr and hr[0] > 0:
                    out.append(vm("AWS", label, it, v, ram, hr[0] * fx, source=src, term=TERM[ta["LeaseContractLength"]],
                                  note="Reserved Standard, senza anticipo, Linux"))


def _s3(region, fx, out):
    d = get(S3.format(region)).json()
    for sku, p in d["products"].items():
        a = p.get("attributes", {})
        if p.get("productFamily") == "Storage" and a.get("storageClass") == "General Purpose" and a.get("volumeType") == "Standard":
            v = sorted((b, u) for b, u in _dims(d, sku) if u > 0)
            if v:
                out.append(dict(provider="AWS", region=f"{region} ({REGIONS[region]})", kind="storage", sku="S3 Standard (object)",
                                unit="EUR/GB/mese", price=round(v[0][1] * fx, 5), term="On-demand", source=S3.format(region),
                                note="primo scaglione"))
            break


def collect():
    WARNINGS.clear()
    fx, out = usd_eur(), []
    for region in REGIONS:
        for fn in (_ec2, _s3):
            if fn is _s3 and region not in S3_REGIONS:
                continue
            try:
                fn(region, fx, out)
            except Exception as e:
                WARNINGS.append(f"{fn.__name__} {region}: {sanitize(str(e))[:80]}")
    if not any(r["kind"] == "compute" for r in out):
        raise RuntimeError("AWS: nessun prezzo compute letto dalla Price List. " + "; ".join(WARNINGS))
    return out
