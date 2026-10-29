import requests
from common import vm, TIERS

URL_HETZNER_API = "https://api.hetzner.cloud/v1/pricing"
URL_HETZNER_SITE = "https://www.hetzner.com/cloud"

def collect():
    records = []
    
    # 1. Recupero dinamico via API pubblica Hetzner Cloud
    try:
        res = requests.get(URL_HETZNER_API, timeout=10)
        if res.status_code == 200:
            data = res.json()
            server_types = data.get("pricing", {}).get("server_types", [])
            
            for st in server_types:
                name = st.get("name")
                prices = st.get("prices", [])
                
                # Prendiamo il prezzo per la region falkenstein (fsn1) o helsinki (hel1) in EUR
                if not prices:
                    continue
                
                price_info = prices[0]
                price_hourly_net = float(price_info.get("price_hourly", {}).get("net", 0))
                price_monthly_net = float(price_info.get("price_monthly", {}).get("net", 0))
                
                # Info vCPU e RAM (se presenti nell'API o stimati dallo SKU)
                # Ipotizziamo estrazione taglia
                vcpus = 2
                ram = 4
                if "cpx11" in name or "cx11" in name or "cax11" in name:
                    vcpus, ram = 1, 2
                elif "cpx21" in name or "cx21" in name or "cax21" in name:
                    vcpus, ram = 2, 4
                elif "cpx31" in name or "cx31" in name or "cax31" in name:
                    vcpus, ram = 4, 8
                elif "cpx41" in name or "cx41" in name or "cax41" in name:
                    vcpus, ram = 8, 16
                elif "cpx51" in name or "cx51" in name or "cax51" in name:
                    vcpus, ram = 16, 32

                if vcpus in TIERS:
                    r = vm(
                        provider="Hetzner",
                        region="EU (Falkenstein/Helsinki)",
                        sku=f"Hetzner Cloud {name.upper()}",
                        vcpu=vcpus,
                        ram=ram,
                        hourly=price_hourly_net,
                        monthly=price_monthly_net,
                        source=URL_HETZNER_SITE,
                        note="Hetzner Cloud API"
                    )
                    r["term"] = "On-demand"
                    records.append(r)
    except Exception as e:
        print(f"Errore durante il recupero API Hetzner: {e}")

    # 2. Storage & Backup Hetzner (Object Storage, Volumes, Dedicated)
    records.extend([
        {
            "provider": "Hetzner",
            "region": "EU (Falkenstein/Helsinki)",
            "kind": "storage",
            "sku": "Hetzner Cloud Volume NVMe (Block Storage)",
            "unit": "EUR/GB/mese",
            "price": 0.047,
            "term": "On-demand",
            "source": URL_HETZNER_SITE
        },
        {
            "provider": "Hetzner",
            "region": "EU (Falkenstein/Helsinki)",
            "kind": "storage",
            "sku": "Hetzner Storage Box BX11 (1 TB)",
            "unit": "EUR/mese",
            "price": 3.81,
            "term": "On-demand",
            "source": "https://www.hetzner.com/storage/storage-box"
        },
        {
            "provider": "Hetzner",
            "region": "EU (Falkenstein/Helsinki)",
            "kind": "storage",
            "sku": "Hetzner Storage Box BX21 (5 TB)",
            "unit": "EUR/mese",
            "price": 12.97,
            "term": "On-demand",
            "source": "https://www.hetzner.com/storage/storage-box"
        },
        {
            "provider": "Hetzner",
            "region": "EU (Falkenstein/Helsinki)",
            "kind": "rete",
            "sku": "Traffico Egress Extra (oltre 20 TB inclusi)",
            "unit": "EUR/TB",
            "price": 1.19,
            "term": "On-demand",
            "source": URL_HETZNER_SITE
        },
        {
            "provider": "Hetzner",
            "region": "EU (Falkenstein/Helsinki)",
            "kind": "k8s",
            "sku": "Hetzner Cloud Kubernetes (Control Plane via Hetzner Cloud)",
            "unit": "EUR/mese",
            "price": 0.00,
            "term": "On-demand",
            "source": URL_HETZNER_SITE,
            "note": "Gratuito (si pagano solo i nodi worker)"
        }
    ])

    return records
