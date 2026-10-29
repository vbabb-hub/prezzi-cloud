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
        r_od = vm("Aruba Cloud", "it-1 (Arezzo/Milano)", sku, vcpu, ram, hourly_price, monthly=monthly_price, source=URL_ARUBA, note="Aruba Cloud VPS")
        r_od["term"] = "On-demand"
        records.append(r_od)

    # 2. Cloud Server Pro (Gamma completa da 2 a 64 vCPU con termini di impegno)
    pro_configurations = [
        ("Cloud Server Pro - 2 vCPU / 4 GB", 2, 4, 0.038, 27.74),
        ("Cloud Server Pro - 4 vCPU / 8 GB", 4, 8, 0.076, 55.48),
        ("Cloud Server Pro - 8 vCPU / 16 GB", 8, 16, 0.152, 110.96),
        ("Cloud Server Pro - 16 vCPU / 32 GB", 16, 32, 0.304, 221.92),
        ("Cloud Server Pro - 32 vCPU / 64 GB", 32, 64, 0.608, 443.84),
        ("Cloud Server Pro - 64 vCPU / 128 GB", 64, 128, 1.216, 887.68),
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

    # 3. GPU Cloud (Istanze dedicate con accelerazione hardware)
    gpu_instances = [
        ("Aruba GPU Instance - 1x NVIDIA L4", 16, 64, 520.00),
        ("Aruba GPU Instance - 1x NVIDIA A10G", 24, 96, 850.00),
        ("Aruba GPU Instance - 1x NVIDIA A100", 32, 128, 1450.00),
    ]

    for sku, vcpu, ram, monthly_price in gpu_instances:
        r_gpu = {
            "provider": "Aruba Cloud",
            "region": "it-1 (Arezzo/Milano)",
            "kind": "gpu",
            "sku": sku,
            "vcpu": vcpu,
            "ram": ram,
            "unit": "EUR/mese",
            "price": monthly_price,
            "term": "On-demand",
            "source": URL_ARUBA,
            "note": "Aruba Dedicated GPU"
        }
        records.append(r_gpu)

    # 4. Colocation (Spazio Rack e Armadi Datacenter)
    colocation_items = [
        ("Colocation - 1U Rack Space (1Gbps Dedicato)", "EUR/mese", 75.00),
        ("Colocation - 1/4 Rack (11U) + Power", "EUR/mese", 350.00),
        ("Colocation - Half Rack (22U) + Power", "EUR/mese", 650.00),
        ("Colocation - Full Rack (42U) + Power 3kW", "EUR/mese", 1100.00),
    ]

    for sku, unit, price in colocation_items:
        records.append({
            "provider": "Aruba Cloud",
            "region": "Datacenter IT3 (Arezzo/Bergamo)",
            "kind": "colocation",
            "sku": sku,
            "unit": unit,
            "price": price,
            "term": "On-demand",
            "source": URL_ARUBA
        })

    # 5. Storage, Rete, Licenze, K8s e DBaaS
    records.extend([
        {"provider": "Aruba Cloud", "region": "it-1 (Arezzo/Milano)", "kind": "storage", "sku": "Block Storage SSD Standard", "unit": "EUR/GB/mese", "price": 0.05, "source": URL_ARUBA, "term": "On-demand"},
        {"provider": "Aruba Cloud", "region": "it-1 (Arezzo/Milano)", "kind": "storage", "sku": "Block Storage High Performance NVMe", "unit": "EUR/GB/mese", "price": 0.12, "source": URL_ARUBA, "term": "On-demand"},
        {"provider": "Aruba Cloud", "region": "it-1 (Arezzo/Milano)", "kind": "storage", "sku": "Object Storage S3 Compatible", "unit": "EUR/GB/mese", "price": 0.018, "source": URL_ARUBA, "term": "On-demand"},
        {"provider": "Aruba Cloud", "region": "it-1 (Arezzo/Milano)", "kind": "rete", "sku": "Traffico Egress Internet (oltre quota inclusa)", "unit": "EUR/TB", "price": 10.00, "source": URL_ARUBA, "term": "On-demand"},
        {"provider": "Aruba Cloud", "region": "it-1 (Arezzo/Milano)", "kind": "licenses", "sku": "Licenza Windows Server (per core)", "unit": "EUR/mese", "price": 4.50, "source": URL_ARUBA, "term": "On-demand"},
        {"provider": "Aruba Cloud", "region": "it-1 (Arezzo/Milano)", "kind": "k8s", "sku": "Managed Kubernetes Control Plane", "unit": "EUR/mese", "price": 0.00, "source": URL_ARUBA, "term": "On-demand", "note": "Gratuito"},
        {"provider": "Aruba Cloud", "region": "it-1 (Arezzo/Milano)", "kind": "dbaas", "sku": "Database Managed PostgreSQL / MySQL", "unit": "EUR/mese", "price": 29.00, "source": URL_ARUBA, "term": "On-demand"},
    ])

    return records
