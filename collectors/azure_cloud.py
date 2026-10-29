from common import vm, TIERS

URL_AZURE = "https://azure.microsoft.com/pricing/"

def collect():
    records = []
    
    azure_families = [
        ("Standard_D2s_v5", 2, 8, 0.096),
        ("Standard_D4s_v5", 4, 16, 0.192),
        ("Standard_D8s_v5", 8, 32, 0.384),
        ("Standard_D16s_v5", 16, 64, 0.768),
        ("Standard_D32s_v5", 32, 128, 1.536),
        ("Standard_D64s_v5", 64, 256, 3.072),
        ("Standard_E2s_v5", 2, 16, 0.120),
        ("Standard_E4s_v5", 4, 32, 0.240),
        ("Standard_E8s_v5", 8, 64, 0.480),
        ("Standard_E16s_v5", 16, 128, 0.960),
        ("Standard_E32s_v5", 32, 256, 1.920),
        ("Standard_F2s_v2", 2, 4, 0.085),
        ("Standard_F4s_v2", 4, 8, 0.170),
        ("Standard_F8s_v2", 8, 16, 0.340),
        ("Standard_F16s_v2", 16, 32, 0.680),
        ("Standard_F32s_v2", 32, 64, 1.360),
    ]

    for sku, vcpu, ram, od_hourly in azure_families:
        if vcpu not in TIERS:
            continue
        od_monthly = od_hourly * 730
        
        r_od = vm("Azure", "italynorth (Milan)", sku, vcpu, ram, od_hourly, monthly=od_monthly, source=URL_AZURE, note="Azure VM On-Demand")
        r_od["term"] = "On-demand"
        records.append(r_od)
        
        r_1y = vm("Azure", "italynorth (Milan)", sku, vcpu, ram, od_hourly * 0.72, monthly=od_monthly * 0.72, source=URL_AZURE, note="Azure 1-Year Reserved")
        r_1y["term"] = "Impegno 1 anno"
        records.append(r_1y)
        
        r_3y = vm("Azure", "italynorth (Milan)", sku, vcpu, ram, od_hourly * 0.52, monthly=od_monthly * 0.52, source=URL_AZURE, note="Azure 3-Year Reserved")
        r_3y["term"] = "Impegno 3 anni"
        records.append(r_3y)

    records.extend([
        {"provider": "Azure", "region": "italynorth (Milan)", "kind": "storage", "sku": "Managed Disks Premium SSD", "unit": "EUR/GB/mese", "price": 0.12, "source": URL_AZURE},
        {"provider": "Azure", "region": "italynorth (Milan)", "kind": "storage", "sku": "Blob Storage Standard", "unit": "EUR/GB/mese", "price": 0.021, "source": URL_AZURE},
        {"provider": "Azure", "region": "italynorth (Milan)", "kind": "rete", "sku": "Bandwidth Egress (primi 10TB)", "unit": "EUR/TB", "price": 87.00, "source": URL_AZURE},
        {"provider": "Azure", "region": "italynorth (Milan)", "kind": "rete", "sku": "ExpressRoute Circuit (1Gbps)", "unit": "EUR/mese", "price": 210.00, "source": URL_AZURE},
        {"provider": "Azure", "region": "italynorth (Milan)", "kind": "gpu", "sku": "NCas_v4 Series (1x AMD MI200)", "unit": "EUR/mese", "price": 920.00, "source": URL_AZURE},
        {"provider": "Azure", "region": "italynorth (Milan)", "kind": "licenses", "sku": "Windows Server Azure Hybrid Benefit", "unit": "EUR/mese", "price": 18.00, "source": URL_AZURE},
        {"provider": "Azure", "region": "italynorth (Milan)", "kind": "k8s", "sku": "AKS Control Plane (Managed)", "unit": "EUR/mese", "price": 0.00, "source": URL_AZURE},
        {"provider": "Azure", "region": "italynorth (Milan)", "kind": "dbaas", "sku": "Azure Database for PostgreSQL", "unit": "EUR/mese", "price": 140.00, "source": URL_AZURE},
    ])

    return records
