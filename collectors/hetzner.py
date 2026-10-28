import os
from common import get, vm, TIERS, Skip

API = "https://api.hetzner.cloud/v1"
LOC = "fsn1"

def collect():
    tok = os.environ.get("HCLOUD_TOKEN")
    out = []
    
    # 1. Tentativo tramite API ufficiale se il token è presente
    if tok:
        try:
            h = {"Authorization": f"Bearer {tok}"}
            resp = get(f"{API}/server_types", headers=h, params={"per_page": 50})
            if resp.status_code == 200:
                for st in resp.json().get("server_types", []):
                    if st.get("deprecated") or st.get("deprecation") or st.get("architecture") != "x86" or st["cores"] not in TIERS:
                        continue
                    for p in st["prices"]:
                        if p["location"] == LOC:
                            out.append(vm("Hetzner", LOC, st["name"], st["cores"], st["memory"], float(p["price_hourly"]["net"]),
                                          monthly=float(p["price_monthly"]["net"]), source=API))
                
                pr_resp = get(f"{API}/pricing", headers=h)
                if pr_resp.status_code == 200:
                    pr = pr_resp.json().get("pricing", {})
                    if "volume" in pr:
                        out.append(dict(provider="Hetzner", region="EU", kind="storage", sku="Volume (block)", unit="EUR/GB/mese",
                                        price=float(pr["volume"]["price_per_gb_month"]["net"]), source=API))
                    if "traffic" in pr:
                        out.append(dict(provider="Hetzner", region="EU", kind="rete", sku="Traffico extra", unit="EUR/TB",
                                        price=float(pr["traffic"]["price_per_tb"]["net"]), source=API))
        except Exception as e:
            print(f"[hetzner] Errore chiamata API live: {e}")

    # 2. Fallback con listino ufficiale statico (garantisce che i dati siano sempre presenti)
    if not out:
        static_instances = [
            ("cax11 (ARM / test)", 2, 4, 0.0055, 3.79),
            ("cx22", 2, 4, 0.0051, 3.49),
            ("cx32", 4, 8, 0.0102, 6.99),
            ("cx42", 8, 16, 0.0204, 13.99),
            ("cx52", 16, 32, 0.0408, 27.99),
        ]
        for sku, vcpu, ram, hourly, monthly in static_instances:
            if vcpu in TIERS:
                out.append(vm("Hetzner", "EU-Nuremberg/Falkenstein", sku, vcpu, ram, hourly, monthly=monthly, source="https://www.hetzner.com/cloud", note="Listino ufficiale statico"))

        # Storage e Rete di fallback
        out.append(dict(provider="Hetzner", region="EU", kind="storage", sku="Volume (block SSD)", unit="EUR/GB/mese", price=0.044, source="https://www.hetzner.com/cloud"))
        out.append(dict(provider="Hetzner", region="EU", kind="rete", sku="Traffico extra (oltre 20TB)", unit="EUR/TB", price=1.00, source="https://www.hetzner.com/cloud"))

    return out

def extra():
    return []

if __name__ == "__main__":
    import json
    print(json.dumps(collect(), indent=2, ensure_ascii=False))
    
