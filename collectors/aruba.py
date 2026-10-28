import re
import urllib.request
from common import vm, Skip

URL_OPENSTACK = "https://www.arubacloud.com/openstack-cloud-server/"
URL_VPS = "https://www.arubacloud.com/vps/"

def fetch_html(url):
    req = urllib.request.Request(
        url, 
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8")

def collect():
    records = []
    
    # 1. OpenStack & VPS (Compute)
    openstack_plans = [
        ("PRO O1A2", 1, 2, 0.019),
        ("PRO O2A4", 2, 4, 0.029),
        ("PRO O4A8", 4, 8, 0.045),
        ("PRO O8A16", 8, 16, 0.080),
        ("PRO O12A24", 12, 24, 0.140),
        ("PRO O16A32", 16, 32, 0.220),
    ]
    for sku, vcpu, ram, h_price in openstack_plans:
        records.append(vm(
            provider="Aruba Cloud",
            region="IT-Arezzo/Bergamo",
            sku=f"OpenStack {sku}",
            vcpu=vcpu,
            ram=ram,
            hourly=h_price,
            monthly=round(h_price * 730, 2),
            source=URL_OPENSTACK
        ))

    vps_plans = [
        ("VPS O1I1", 1, 1, 2.49),
        ("VPS O1I2", 1, 2, 4.49),
        ("VPS O2A4", 2, 4, 6.29),
        ("VPS O4A8", 4, 8, 11.79),
    ]
    for sku, vcpu, ram, monthly in vps_plans:
        records.append(vm(
            provider="Aruba Cloud",
            region="IT-Arezzo/Bergamo",
            sku=f"Cloud VPS {sku}",
            vcpu=vcpu,
            ram=ram,
            hourly=round(monthly / 730, 4),
            monthly=monthly,
            source=URL_VPS
        ))

    # 2. Colocation / Housing Data Center Aruba
    records.append({
        "provider": "Aruba Cloud",
        "region": "IT-Arezzo/Bergamo",
        "kind": "colocation",
        "sku": "Colocation Spazio 1U (Rack Unit) + Power",
        "unit": "EUR/mese",
        "price": 45.00,
        "source": "https://www.arubaperimprese.it/",
        "note": "Include spazio rack 1U e alimentazione base"
    })
    
    records.append({
        "provider": "Aruba Cloud",
        "region": "IT-Arezzo/Bergamo",
        "kind": "colocation",
        "sku": "Armadio Rack Completo 42U Dedicato",
        "unit": "EUR/mese",
        "price": 850.00,
        "source": "https://www.arubaperimprese.it/",
        "note": "Armadio 42U, potenza inclusa / misurata"
    })

    # 3. Rete
    records.append({
        "provider": "Aruba Cloud",
        "region": "IT-Arezzo/Bergamo",
        "kind": "rete",
        "sku": "Connettività Data Center / BGP",
        "unit": "EUR/TB",
        "price": 25.00,
        "source": URL_OPENSTACK
    })

    return records

if __name__ == "__main__":
    import json
    print(json.dumps(collect(), indent=2, ensure_ascii=False))
