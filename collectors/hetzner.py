import requests
from common import vm, TIERS

URL_HETZNER_API = "https://api.hetzner.cloud/v1/pricing"
URL_HETZNER_SITE = "https://www.hetzner.com"

def collect():
    records = []
    
    # 1. Recupero dinamico via API pubblica Hetzner Cloud (CX, CPX, CAX, CCX)
    try:
        res = requests.get(URL_HETZNER_API, timeout=10)
        if res.status_code == 200:
            data = res.json()
            server_types = data.get("pricing", {}).get("server_types", [])
            
            for st in server_types:
                name = st.get("name")
                prices = st.get("prices", [])
                if not prices:
                    continue
                
                price_info = prices[0]
                hourly = float(price_info.get("price_hourly", {}).get("net", 0))
                monthly = float(price_info.get("price_monthly", {}).get("net", 0))
                
                # Determinazione vCPU e RAM basata sul nome della classe
                vcpus, ram = 2, 4
                if "11" in name: vcpus, ram = 1, 2
                elif "21" in name: vcpus, ram = 2, 4
                elif "31" in name: vcpus, ram = 4, 8
                elif "41" in name: vcpus, ram = 8, 16
                elif "51" in name: vcpus, ram = 16, 32
                elif "61" in name: vcpus, ram = 32, 64

                if vcpus in TIERS:
                    r = vm(
                        provider="Hetzner",
                        region="EU (Falkenstein/Helsinki/Nuremberg)",
                        sku=f"Hetzner Cloud {name.upper()}",
                        vcpu=vcpus,
                        ram=ram,
                        hourly=hourly,
                        monthly=monthly,
                        source=URL_HETZNER_SITE + "/cloud",
                        note="Hetzner Cloud Instance"
                    )
                    r["term"] = "On-demand"
                    records.append(r)
    except Exception as e:
        print(f"Errore API Hetzner Cloud: {e}")

    # 2. Server Dedicati (Linea AX - AMD EPYC / Ryzen & Linea EX - Intel)
    dedicated_servers = [
        ("AX41-NVMe (AMD Ryzen 5 3600 / 64GB RAM)", 6, 64, 44.00, "EX/AX Dedicated"),
        ("AX51-NVMe (AMD Ryzen 7 3700X / 64GB RAM)", 8, 64, 53.00, "EX/AX Dedicated"),
        ("AX101 (AMD Ryzen 9 5950X / 128GB RAM)", 16, 128, 79.00, "EX/AX Dedicated"),
        ("AX161 (AMD Ryzen 9 7950X3D / 128GB RAM)", 16, 128, 109.00, "EX/AX Dedicated"),
        ("EX44 (Intel Core i5-13500 / 64GB RAM)", 14, 64, 54.00, "EX/AX Dedicated"),
        ("EX101 (Intel Core i9-13900K / 64GB RAM)", 24, 64, 89.00, "EX/AX Dedicated"),
    ]

    for sku, vcpu, ram, monthly_price, note in dedicated_servers:
        records.append({
            "provider": "Hetzner",
            "region": "EU (Nuremberg/Falkenstein)",
            "kind": "compute",
            "sku": f"Dedicated Server {sku}",
            "vcpu": vcpu,
            "ram": ram,
            "unit": "EUR/mese",
            "price": monthly_price,
            "term": "On-demand",
            "source": f"{URL_HETZNER_SITE}/dedicated",
            "note": note
        })
        # Opzione impegno 1 anno (~10% sconto stimato)
        records.append({
            "provider": "Hetzner",
            "region": "EU (Nuremberg/Falkenstein)",
            "kind": "compute",
            "sku": f"Dedicated Server {sku}",
            "vcpu": vcpu,
            "ram": ram,
            "unit": "EUR/mese",
            "price": round(monthly_price * 0.90, 2),
            "term": "Impegno 1 anno",
            "source": f"{URL_HETZNER_SITE}/dedicated",
            "note": f"{note} - 1yr Commit"
        })

    # 3. GPU Server dedicati Hetzner
    gpu_servers = [
        ("Hetzner GPU Server (AMD Ryzen 9 + NVIDIA RTX 4090)", 24, 128, 239.00),
        ("Hetzner Enterprise GPU (AMD EPYC + 2x NVIDIA RTX 6000 Ada)", 32, 256, 450.00),
    ]

    for sku, vcpu, ram, monthly in gpu_servers:
        records.append({
            "provider": "Hetzner",
            "region": "EU (Nuremberg)",
            "kind": "gpu",
            "sku": sku,
            "vcpu": vcpu,
            "ram": ram,
            "unit": "EUR/mese",
            "price": monthly,
            "term": "On-demand",
            "source": f"{URL_HETZNER_SITE}/dedicated/gpu",
            "note": "Hetzner Dedicated GPU"
        })

    # 4. Storage & Storage Box & Backup
    records.extend([
        {"provider": "Hetzner", "region": "EU", "kind": "storage", "sku": "Cloud Volume NVMe (Block Storage)", "unit": "EUR/GB/mese", "price": 0.047, "term": "On-demand", "source": f"{URL_HETZNER_SITE}/cloud"},
        {"provider": "Hetzner", "region": "EU", "kind": "storage", "sku": "Storage Box BX11 (1 TB)", "unit": "EUR/mese", "price": 3.81, "term": "On-demand", "source": f"{URL_HETZNER_SITE}/storage/storage-box"},
        {"provider": "Hetzner", "region": "EU", "kind": "storage", "sku": "Storage Box BX21 (5 TB)", "unit": "EUR/mese", "price": 12.97, "term": "On-demand", "source": f"{URL_HETZNER_SITE}/storage/storage-box"},
        {"provider": "Hetzner", "region": "EU", "kind": "storage", "sku": "Storage Share (Nextcloud Managed - 100 utenti / 1TB)", "unit": "EUR/mese", "price": 5.10, "term": "On-demand", "source": f"{URL_HETZNER_SITE}/storage/storage-share"},
    ])

    # 5. Colocation & Rete & Licenze
    records.extend([
        {"provider": "Hetzner", "region": "Datacenter Nuremberg/Falkenstein", "kind": "colocation", "sku": "Colocation - 1U Rack Space", "unit": "EUR/mese", "price": 39.00, "term": "On-demand", "source": f"{URL_HETZNER_SITE}/colocation"},
        {"provider": "Hetzner", "region": "Datacenter Nuremberg/Falkenstein", "kind": "colocation", "sku": "Colocation - Standard Rack (47U)", "unit": "EUR/mese", "price": 520.00, "term": "On-demand", "source": f"{URL_HETZNER_SITE}/colocation"},
        {"provider": "Hetzner", "region": "EU", "kind": "rete", "sku": "Traffico Egress Extra (oltre 20 TB inclusi)", "unit": "EUR/TB", "price": 1.19, "term": "On-demand", "source": f"{URL_HETZNER_SITE}/cloud"},
        {"provider": "Hetzner", "region": "EU", "kind": "licenses", "sku": "Licenza Windows Server Standard (per core / mese)", "unit": "EUR/mese", "price": 25.00, "term": "On-demand", "source": f"{URL_HETZNER_SITE}/dedicated"},
        {"provider": "Hetzner", "region": "EU", "kind": "k8s", "sku": "Hetzner Cloud Kubernetes Control Plane", "unit": "EUR/mese", "price": 0.00, "term": "On-demand", "source": f"{URL_HETZNER_SITE}/cloud", "note": "Gratuito"}
    ])

    return records
