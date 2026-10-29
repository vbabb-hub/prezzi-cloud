from common import TIERS

URL_AZURE = "https://azure.microsoft.com/pricing/"

def collect():
    records = []
    
    # Famiglie Azure (Dv5, Ev5, Fsv2)
    azure_families = [
        ("Standard_D2s_v5", 2, 8, 0.096),
        ("Standard_D4s_v5", 4, 16, 0.192),
        ("Standard_D8s_v5", 8, 32, 0.384),
        ("Standard_D16s_v5", 16, 64, 0.768),
        ("Standard_E2s_v5", 2, 16, 0.120),
        ("Standard_E4s_v5", 4, 32, 0.240),
        ("Standard_E8s_v5", 8, 64, 0.480),
        ("Standard_F2s_v2", 2, 4, 0.085),
        ("Standard_F4s_v2", 4, 8, 0.170),
        ("Standard_F8s_v2", 8, 16, 0.340),
    ]

    for sku, vcpu, ram, od_hourly in azure_families:
        if vcpu not in TIERS:
            continue
        od_monthly = od_hourly * 730
        
        # On-demand
        records.append({
            "provider": "Azure", "region": "italynorth (Milan)", "kind": "compute",
            "sku": sku, "vcpus": vcpu, "ram": ram, "unit": "EUR/mese",
            "price": round(od_monthly, 2), "hourly": round(od_hourly, 4),
            "term": None, "source": URL_AZURE, "note": "Azure Virtual Machines On-Demand"
        })
        # 1 anno
        records.append({
            "provider": "Azure", "region": "italynorth (Milan)", "kind": "compute",
            "sku": sku, "vcpus": vcpu, "ram": ram, "unit": "EUR/mese",
            "price": round(od_monthly * 0.72, 2), "hourly": round(od_hourly * 0.72, 4),
            "term": "Impegno 1 anno", "source": URL_AZURE, "note": "Azure 1-Year Reserved"
        })
        # 3 anni
        records.append({
            "provider": "Azure", "region": "italynorth (Milan)", "kind": "compute",
            "sku": sku, "vcpus": vcpu, "ram": ram, "unit": "EUR/mese",
            "price": round(od_monthly * 0.52, 2), "hourly": round(od_hourly * 0.52, 4),
            "term": "Impegno 3 anni", "source": URL_AZURE, "note": "Azure 3-Year Reserved"
        })

    # Altre categorie
    records.extend([
        {"provider": "Azure", "region": "italynorth (Milan)", "kind": "storage", "sku": "Managed Disks Premium SSD", "unit": "EUR/GB/mese", "price": 0.12, "source": URL_AZURE},
        {"provider": "Azure", "region": "italynorth (Milan)", "kind": "storage", "sku": "Blob Storage Standard", "unit": "EUR/GB/mese", "price": 0.021, "source": URL_AZURE},
        {"provider": "Azure", "region": "italynorth (Milan)", "kind": "rete", "sku": "Bandwidth Egress (primi 10TB)", "unit": "EUR/TB", "price": 87.00, "source": URL_AZURE},
        {"provider": "Azure", "region": "italynorth (Milan)", "kind": "rete", "sku": "ExpressRoute Circuit (1Gbps)", "unit": "EUR/mese", "price": 210.00, "source": URL_AZURE},
        {"provider": "Azure", "region": "italynorth (Milan)", "kind": "gpu", "sku": "NCas_v4 Series (1x AMD MI200)", "unit": "EUR/mese", "price": 920.00, "source": URL_AZURE},
        {"provider": "Azure", "region": "italynorth (Milan)", "kind": "licenses", "sku": "Windows Server Azure Hybrid Benefit", "unit": "EUR/mese", "price": 18.00, "source": URL_AZURE},
        {"provider": "Azure", "region": "italynorth (Milan)", "kind": "k8s", "sku": "AKS Control Plane (Managed)", "unit": "EUR/mese", "price": 0.00, "source": URL_AZURE, "note": "Gratuito"},
        {"provider": "Azure", "region": "italynorth (Milan)", "kind": "dbaas", "sku": "Azure Database for PostgreSQL (General Purpose)", "unit": "EUR/mese", "price": 140.00, "source": URL_AZURE},
    ])

    return records
