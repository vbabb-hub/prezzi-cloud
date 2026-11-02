"""Hetzner Cloud: API ufficiale, serve un token di sola lettura nel secret HCLOUD_TOKEN (gratuito, da un progetto Hetzner).
Senza token la fonte viene saltata: restano i prezzi verificati a mano in manual/hetzner.yml. Prezzi netti (IVA esclusa),
location fsn1, solo x86 non deprecati, senza IPv4 (+0,50 EUR/mese). Nessun prezzo stimato nel codice."""
import os
from common import get, vm, Skip, TIERS

API = "https://api.hetzner.cloud/v1"
LOC = "fsn1"
WARNINGS = []


def collect():
    WARNINGS.clear()
    tok = os.environ.get("HCLOUD_TOKEN")
    if not tok:
        raise Skip("HCLOUD_TOKEN non impostato: uso i prezzi manuali di manual/hetzner.yml")
    h = {"Authorization": f"Bearer {tok}"}
    out = []
    for st in get(f"{API}/server_types", headers=h, params={"per_page": 50}).json()["server_types"]:
        if st.get("deprecated") or st.get("deprecation") or st.get("architecture") != "x86" or st["cores"] not in TIERS:
            continue
        for p in st["prices"]:
            if p["location"] == LOC:
                out.append(vm("Hetzner", f"{LOC} (Falkenstein)", st["name"].upper(), st["cores"], st["memory"], float(p["price_hourly"]["net"]),
                              monthly=float(p["price_monthly"]["net"]), source=API, term="On-demand",
                              note="senza IPv4 (+0,50 EUR/mese)" + ("; vCPU dedicate" if st.get("cpu_type") == "dedicated" else "")))
    if not out:
        raise RuntimeError("Hetzner: nessun tipo di server restituito dall'API")
    try:
        pr = get(f"{API}/pricing", headers=h).json()["pricing"]
        out.append(dict(provider="Hetzner", region="EU", kind="storage", sku="Volume (block)", unit="EUR/GB/mese",
                        price=float(pr["volume"]["price_per_gb_month"]["net"]), term="On-demand", source=API))
        out.append(dict(provider="Hetzner", region="EU", kind="rete", sku="Traffico extra", unit="EUR/TB",
                        price=float(pr["traffic"]["price_per_tb"]["net"]), term="On-demand", source=API))
    except Exception as e:
        WARNINGS.append(f"pricing: {str(e)[:80]}")
    return out
