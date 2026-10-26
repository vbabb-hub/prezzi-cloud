import os
from common import get, vm, TIERS

API = "https://api.hetzner.cloud/v1"
LOC = "fsn1"


def collect():
    tok = os.environ.get("HCLOUD_TOKEN")
    if not tok:
        raise RuntimeError("HCLOUD_TOKEN non impostato (secret GitHub)")
    h = {"Authorization": f"Bearer {tok}"}
    out = []
    for st in get(f"{API}/server_types", headers=h, params={"per_page": 50}).json()["server_types"]:
        if st.get("deprecated") or st.get("deprecation") or st.get("architecture") != "x86" or st["cores"] not in TIERS:
            continue
        for p in st["prices"]:
            if p["location"] == LOC:
                out.append(vm("Hetzner", LOC, st["name"], st["cores"], st["memory"], float(p["price_hourly"]["net"]),
                              monthly=float(p["price_monthly"]["net"]), source=API))
    pr = get(f"{API}/pricing", headers=h).json()["pricing"]
    out.append(dict(provider="Hetzner", region="EU", kind="storage", sku="Volume (block)", unit="EUR/GB/mese",
                    price=float(pr["volume"]["price_per_gb_month"]["net"]), source=API))
    out.append(dict(provider="Hetzner", region="EU", kind="rete", sku="Traffico extra", unit="EUR/TB",
                    price=float(pr["traffic"]["price_per_tb"]["net"]), source=API))
    return out
