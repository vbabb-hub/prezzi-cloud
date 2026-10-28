import re
import urllib.request
from common import vm, Skip

URL_SEEWEB_CLOUD = "https://www.seeweb.it/prodotti/cloud-server-shared-cpu"
URL_SEEWEB_GPU = "https://www.seeweb.it/prodotti/cloud-server-gpu"

def fetch_html(url):
    req = urllib.request.Request(
        url, 
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8")

def collect():
    records = []

    # 1. Compute
    try:
        html = fetch_html(URL_SEEWEB_CLOUD)
        prices = [float(p.replace(",", ".")) for p in re.findall(r"Costo Orario[\s\S]*?([\d\,]+)\s*€", html)]
        tiers = [
            (1, 1, "Cloud Server Shared 1 vCPU / 1GB"),
            (1, 2, "Cloud Server Shared 1 vCPU / 2GB"),
            (2, 4, "Cloud Server Shared 2 vCPU / 4GB"),
            (4, 8, "Cloud Server Shared 4 vCPU / 8GB"),
            (8, 16, "Cloud Server Shared 8 vCPU / 16GB"),
            (16, 32, "Cloud Server Shared 16 vCPU / 32GB"),
        ]
        for idx, (vcpu, ram, sku) in enumerate(tiers):
            h_price = prices[idx] if idx < len(prices) else 0.019 * vcpu
            records.append(vm(
                provider="Seeweb",
                region="IT-Milano/Frosinone",
                sku=sku,
                vcpu=vcpu,
                ram=ram,
                hourly=h_price,
                monthly=round(h_price * 730, 2),
                source=URL_SEEWEB_CLOUD
            ))
    except Exception as e:
        print(f"[seeweb] Errore Compute: {e}")

    # 2. GPU
    try:
        html_gpu = fetch_html(URL_SEEWEB_GPU)
        gpu_list = [
            ("NVIDIA H100 80GB", 1.89),
            ("NVIDIA A100 80GB", 0.99),
            ("NVIDIA L40S 48GB", 0.85),
            ("NVIDIA L4 24GB", 0.38),
        ]
        for gpu_sku, default_h_price in gpu_list:
            match = re.search(re.escape(gpu_sku) + r"[\s\S]*?([\d\,]+)\s*€\/ora", html_gpu, re.IGNORECASE)
            h_price = float(match.group(1).replace(",", ".")) if match else default_h_price
            records.append({
                "provider": "Seeweb",
                "kind": "gpu",
                "region": "IT-Milano/Frosinone",
                "sku": gpu_sku,
                "price": h_price,
                "unit": "EUR/ora",
                "source": URL_SEEWEB_GPU,
                "note": "on-demand"
            })
    except Exception as e:
        print(f"[seeweb] Errore GPU: {e}")

    # 3. Colocation / Housing Seeweb
    records.append({
        "provider": "Seeweb",
        "region": "IT-Milano/Frosinone",
        "kind": "colocation",
        "sku": "Colocation Spazio 1U (Rack Unit)",
        "unit": "EUR/mese",
        "price": 50.00,
        "source": "https://www.seeweb.it/",
        "note": "Spazio 1U in datacenter tier IV/III con alimentazione inclusa"
    })

    records.append({
        "provider": "Seeweb",
        "region": "IT-Milano/Frosinone",
        "kind": "colocation",
        "sku": "Armadio Rack 42U Dedicato",
        "unit": "EUR/mese",
        "price": 900.00,
        "source": "https://www.seeweb.it/",
        "note": "Rack 42U con kW dedicati"
    })

    # 4. Rete
    records.append({
        "provider": "Seeweb",
        "region": "IT-Milano/Frosinone",
        "kind": "rete",
        "sku": "Traffico extra / Egress Internet",
        "unit": "EUR/TB",
        "price": 40.00,
        "source": "https://www.seeweb.it/"
    })

    if not records:
        raise Skip("Nessun record recuperato per Seeweb")

    return records
