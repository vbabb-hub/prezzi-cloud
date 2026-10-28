import re
import urllib.request
from common import Skip

URL_PVE = "https://www.proxmox.com/en/products/proxmox-virtual-environment/pricing"
URL_PBS = "https://www.proxmox.com/en/products/proxmox-backup-server/pricing"

def fetch_html(url):
    req = urllib.request.Request(
        url, 
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8")

def collect():
    records = []

    # 1. Proxmox VE (Scraping automatico dal sito ufficiale)
    try:
        html_pve = fetch_html(URL_PVE)
        # Cerca i prezzi in EUR per socket/anno (es. Community 110/120€, Basic 340/370€, ecc.)
        prices = [float(p.replace(",", ".")) for p in re.findall(r"€\s*([\d\.\,]+)", html_pve)]
        
        # Mappatura dei piani Proxmox VE
        pve_tiers = [
            ("Proxmox VE Subscription (Community)", 120.0),
            ("Proxmox VE Subscription (Basic)", 370.0),
            ("Proxmox VE Subscription (Standard)", 1020.0),
            ("Proxmox VE Subscription (Premium)", 2040.0),
        ]
        
        for idx, (sku, default_price) in enumerate(pve_tiers):
            price = prices[idx] if idx < len(prices) else default_price
            records.append({
                "provider": "Proxmox VE",
                "region": "Globale",
                "kind": "licenza",
                "sku": sku,
                "unit": "EUR/socket/anno",
                "price": price,
                "source": URL_PVE,
                "note": "Prezzo ufficiale per CPU socket/anno"
            })
    except Exception as e:
        print(f"[proxmox] Errore scraping PVE: {e}")
        # Fallback Proxmox VE Basic
        records.append({
            "provider": "Proxmox VE",
            "region": "Globale",
            "kind": "licenza",
            "sku": "Proxmox VE Subscription (Basic)",
            "unit": "EUR/socket/anno",
            "price": 370.0,
            "source": URL_PVE
        })

    # 2. Proxmox Backup Server (PBS)
    try:
        html_pbs = fetch_html(URL_PBS)
        prices_pbs = [float(p.replace(",", ".")) for p in re.findall(r"€\s*([\d\.\,]+)", html_pbs)]
        pbs_price = prices_pbs[0] if prices_pbs else 560.0
        records.append({
            "provider": "Proxmox VE",
            "region": "Globale",
            "kind": "licenza",
            "sku": "Proxmox Backup Server (PBS Basic)",
            "unit": "EUR/server/anno",
            "price": pbs_price,
            "source": URL_PBS,
            "note": "Licenza per backup server illimitato"
        })
    except Exception as e:
        print(f"[proxmox] Errore scraping PBS: {e}")

    # 3. VMware / Broadcom (Listino di riferimento statico in USD/EUR)
    vmware_plans = [
        ("VMware vSphere Foundation (VVF)", 190.0, "EUR/core/anno", "Prezzo di listino per core"),
        ("VMware Cloud Foundation (VCF)", 350.0, "EUR/core/anno", "Prezzo di listino completo VCF per core"),
        ("VMware vDefend", 200.0, "EUR/core/anno", "Add-on sicurezza NSX / vDefend"),
    ]

    for sku, price, unit, note in vmware_plans:
        records.append({
            "provider": "VMware",
            "region": "Globale",
            "kind": "licenza",
            "sku": sku,
            "unit": unit,
            "price": price,
            "source": "https://www.broadcom.com/",
            "note": note
        })

    if not records:
        raise Skip("Nessuna licenza recuperata")

    return records

if __name__ == "__main__":
    import json
    print(json.dumps(collect(), indent=2, ensure_ascii=False))
