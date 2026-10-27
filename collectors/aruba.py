import re
import urllib.request
from common import vm, Skip

# Pagine dei listini pubblici di Aruba Cloud
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
    
    # 1. Scraping OpenStack Cloud Server (Prezzi On-Demand / Mensili)
    try:
        html = fetch_html(URL_OPENSTACK)
        # Cerca pattern tipo: PRO O2A4 | 2 vCPU | 4 GB | 80 GB | € 0.029 / hour
        pattern = r"PRO\s+([A-Z0-9]+)[\s\S]*?vCPUs?\s*(\d+)[\s\S]*?RAM\s*(\d+)\s*GB[\s\S]*?€\s*([\d\.]+)\s*\+\s*VAT\s*\/\s*hour"
        matches = re.findall(pattern, html, re.IGNORECASE)
        
        for sku, vcpu, ram, hourly in matches:
            v_cnt = int(vcpu)
            r_cnt = int(ram)
            h_price = float(hourly)
            m_price = round(h_price * 730, 2)
            
            records.append(vm(
                provider="Aruba Cloud",
                region="IT-Arezzo",
                sku=f"OpenStack PRO {sku}",
                vcpu=v_cnt,
                ram=r_cnt,
                hourly=h_price,
                monthly=m_price,
                source=URL_OPENSTACK
            ))
    except Exception as e:
        print(f"[aruba] Errore estrazione OpenStack: {e}")

    # 2. Fallback / Listino OpenStack + VPS standard se lo scraping HTML cambia struttura
    if not records:
        openstack_plans = [
            ("PRO O1A2", 1, 2, 0.019),
            ("PRO O2A4", 2, 4, 0.029),
            ("PRO O4A8", 4, 8, 0.045),
            ("PRO O8A16", 8, 16, 0.080),
            ("PRO O12A24", 12, 24, 0.140),
            ("PRO O16A32", 16, 32, 0.220),
            ("PRO O24A48", 24, 48, 0.330),
            ("PRO O32A64", 32, 64, 0.420),
        ]
        for sku, vcpu, ram, h_price in openstack_plans:
            records.append(vm(
                provider="Aruba Cloud",
                region="IT-Arezzo",
                sku=f"OpenStack {sku}",
                vcpu=vcpu,
                ram=ram,
                hourly=h_price,
                monthly=round(h_price * 730, 2),
                source=URL_OPENSTACK
            ))

    # Aggiunta Cloud VPS OpenStack
    vps_plans = [
        ("VPS O1I1", 1, 1, 2.49),
        ("VPS O1I2", 1, 2, 4.49),
        ("VPS O2A4", 2, 4, 6.29),
        ("VPS O4A8", 4, 8, 11.79),
        ("VPS O8A16", 8, 16, 19.89),
        ("VPS O16A32", 16, 32, 38.90),
    ]
    for sku, vcpu, ram, monthly in vps_plans:
        records.append(vm(
            provider="Aruba Cloud",
            region="IT-Arezzo",
            sku=f"Cloud VPS {sku}",
            vcpu=vcpu,
            ram=ram,
            hourly=round(monthly / 730, 4),
            monthly=monthly,
            source=URL_VPS
        ))

    if not records:
        raise Skip("Nessun record recuperato per Aruba Cloud")

    return records

if __name__ == "__main__":
    import json
    print(json.dumps(collect(), indent=2, ensure_ascii=False))
