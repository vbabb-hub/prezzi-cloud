from common import get, vm, TIERS

URL = "https://api.ovh.com/1.0/order/catalog/public/cloud?ovhSubsidiary=IT"
FAMILIES = ("b3", "b2")   # general purpose
GPU_MODEL = (("L40S", "NVIDIA L40S 48GB"), ("L4", "NVIDIA L4 24GB"), ("H200", "NVIDIA H200 141GB"), ("H100", "NVIDIA H100 80GB"),
             ("A100", "NVIDIA A100 80GB"), ("A10", "NVIDIA A10 24GB"))


_EXTRA = []


def collect():
    out = []
    _EXTRA.clear()
    for a in get(URL).json().get("addons", []):
        plan = a.get("planCode", "")
        gp = ((a.get("blobs") or {}).get("technical") or {}).get("gpu") or {}
        if plan.endswith(".consumption") and gp.get("number"):
            model = next((v for k, v in GPU_MODEL if k in str(gp.get("model", "")).upper().replace(" ", "")), None)
            for p in a.get("pricings", []):
                if model and "consumption" in (p.get("capacities") or []) and p.get("price"):
                    _EXTRA.append(dict(provider="OVHcloud", region="catalogo IT", kind="gpu", sku=model, unit="EUR/ora",
                                       price=round(p["price"] / 1e8 / int(gp["number"]), 4), source=URL,
                                       note=f"{plan.replace('.consumption', '')}: {gp['number']} GPU, include vCPU e RAM"))
                    break
            continue
        if plan.startswith("volume.") and plan.endswith(".consumption"):
            for p in a.get("pricings", []):
                if p.get("price"):
                    v = p["price"] / 1e8
                    v = v * 730 if v < 0.005 else v   # il catalogo può esprimere il prezzo orario: lo porto a mese
                    _EXTRA.append(dict(provider="OVHcloud", region="catalogo IT", kind="storage",
                                       sku="Block " + plan.split(".")[1], unit="EUR/GB/mese", price=round(v, 5), source=URL))
                    break
            continue
        if plan.startswith("storage.") and plan.endswith(".consumption") and "archive" not in plan:
            for p in a.get("pricings", []):
                if p.get("price"):
                    v = p["price"] / 1e8
                    v = v * 730 if v < 0.005 else v
                    if 0.001 < v < 1:
                        _EXTRA.append(dict(provider="OVHcloud", region="catalogo IT", kind="storage",
                                           sku="Object " + plan.split(".")[1], unit="EUR/GB/mese", price=round(v, 5), source=URL))
                    break
            continue
        if not plan.endswith(".consumption") or plan.split("-")[0] not in FAMILIES:
            continue
        t = (a.get("blobs") or {}).get("technical") or {}
        try:
            vcpu, ram = int(t["cpu"]["cores"]), float(t["memory"]["size"])
        except (KeyError, TypeError, ValueError):
            continue
        if vcpu not in TIERS:
            continue
        for p in a.get("pricings", []):
            if "consumption" in (p.get("capacities") or []) and p.get("price"):
                hr = p["price"] / 1e8   # il catalogo OVH esprime i prezzi in 1e-8 EUR
                if 0.001 < hr < 5:
                    out.append(vm("OVHcloud", "catalogo IT", plan.replace(".consumption", ""), vcpu, ram, hr, source=URL))
                break
    return out


def extra():
    return list(_EXTRA)
