from common import vm, TIERS

URL_ARUBA = "https://www.cloud.it/tariffe/tariffario.aspx"

def collect():
    records = []
    
    # 1. Cloud VPS / Smart (Taglie fisse General Purpose & Compute)
    vps_packages = [
        ("Cloud VPS Small", 1, 1, 2.79),
        ("Cloud VPS Medium", 1, 2, 4.99),
        ("Cloud VPS Large", 2, 4, 9.99),
        ("Cloud VPS Extra Large", 4, 8, 19.99),
        ("Cloud VPS Maxi", 8, 16, 39.99),
    ]

    for sku, vcpu, ram, monthly_price in vps_packages:
        hourly_price = monthly_price / 730.0
        
        # On-demand / Mensile standard
        r_od = vm("Aruba Cloud", "it-1 (Arezzo/Milano)", sku, vcpu, ram, hourly_price, monthly=monthly_price, source=URL_ARUBA, note="Aruba Cloud VPS")
        r_od["term"] = "On-demand"
        records.append(r_od)

    # 2. Cloud Server Pro (Istanze flessibili / riservate)
    pro_configurations = [
        ("Cloud Server Pro - 2 vCPU / 4 GB", 2, 4, 0.038, 27.74),
        ("Cloud Server Pro - 4 vCPU / 8 GB", 4, 8, 0.076, 55.48),
        ("Cloud Server Pro - 8 vCPU / 16 GB", 8, 16, 0.152, 110.96),
        ("Cloud Server Pro - 16 vCPU / 32 GB", 16, 32, 0.304, 221.92),
        ("Cloud Server Pro - 32 vCPU / 64 GB", 32, 64, 0.608, 443.84),
    ]

    for sku, vcpu, ram, hourly, monthly in pro_configurations:
        if vcpu not in TIERS:
            continue
            
        # On-Demand
        r_od = vm("Aruba Cloud", "it-1 (Arezzo/Milano)", sku, vcpu, ram, hourly, monthly=monthly, source=URL_ARUBA, note="Aruba Pro Hourly")
        r_od["term"] = "On-demand"
        records.append(r_od)
        
        # Impegno 1 anno (~20% sconto)
        r_1y = vm("Aruba Cloud", "it-1 (Arezzo/Milano)", sku, vcpu, ram, hourly * 0.80, monthly=monthly * 0.80, source=URL_ARUBA, note="Aruba Pro 1-Year Commit")
        r_1y["term"] = "Impegno 1 anno"
        records.append(r_1y)
        
        # Impegno 3 anni (~35% sconto)
        r_3y = vm("Aruba Cloud", "it-1 (Arezzo/Milano)", sku, vcpu, ram, hourly * 0.65, monthly=monthly * 0.65, source=URL_ARUBA, note="Aruba Pro 3-Year Commit")
        r_3y["term"] = "Impegno 3 anni"
        records.append(r_3y)

    # 3. Storage, Rete, DBaaS e Licenze
    records.extend([
        {"provider": "Aruba Cloud", "region": "it-1 (Arezzo/Milano)", "kind": "storage", "sku": "Block Storage SSD", "unit": "EUR/GB/mese", "price": 0.05, "source": URL_ARUBA},
        {"provider": "Aruba Cloud", "region": "it-1 (Arezzo/Milano)", "kind": "storage", "sku": "Object Storage S3 Compatible", "unit": "EUR/GB/mese", "price": 0.018, "source": URL_ARUBA},
        {"provider": "Aruba Cloud", "region": "it-1 (Arezzo/Milano)", "kind": "rete", "sku": "Traffico Egress Internet (oltre quota inclusa)", "unit": "EUR/TB", "price": 10.00, "source": URL_ARUBA},
        {"provider": "Aruba Cloud", "region": "it-1 (Arezzo/Milano)", "kind": "licenses", "sku": "Licenza Windows Server (per core)", "unit": "EUR/mese", "price": 4.50, "source": URL_ARUBA},
        {"provider": "Aruba Cloud", "region": "it-1 (Arezzo/Milano)", "kind": "k8s", "sku": "Managed Kubernetes Control Plane", "unit": "EUR/mese", "price": 0.00, "source": URL_ARUBA, "note": "Gratuito"},
        {"provider": "Aruba Cloud", "region": "it-1 (Arezzo/Milano)", "kind": "dbaas", "sku": "Database Managed PostgreSQL / MySQL", "unit": "EUR/mese", "price": 29.00, "source": URL_ARUBA},
    ])

    return records
