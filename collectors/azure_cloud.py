from common import vm, TIERS

URL_AZURE = "https://azure.microsoft.com/pricing/"

def collect():
    records = []
    
    # 1. Compute VM Dsv5-series
    vm_plans = [
        ("Standard_D2s_v5", 2, 8, 0.096, 70.08),
        ("Standard_D4s_v5", 4, 16, 0.192, 140.16),
        ("Standard_D8s_v5", 8, 32, 0.384, 280.32),
        ("Standard_D16s_v5", 16, 64, 0.768, 560.64),
    ]
    for sku, vcpu, ram, hourly, monthly in vm_plans:
        if vcpu in TIERS:
            records.append(vm("Azure", "Italy North (Milan)", sku, vcpu, ram, hourly, monthly=monthly, source=URL_AZURE, note="General Purpose Dsv5"))

    # 2. Storage Managed Disks & Blob
    records.append({
        "provider": "Azure",
        "region": "Italy North (Milan)",
        "kind": "storage",
        "sku": "Premium SSD P10 (128GB)",
        "unit": "EUR/GB/mese",
        "price": 0.11,
        "source": URL_AZURE
    })
    records.append({
        "provider": "Azure",
        "region": "Italy North (Milan)",
        "kind": "storage",
        "sku": "Blob Storage Hot (Object)",
        "unit": "EUR/GB/mese",
        "price": 0.018,
        "source": URL_AZURE
    })

    # 3. Rete / Egress Internet
    records.append({
        "provider": "Azure",
        "region": "Italy North (Milan)",
        "kind": "rete",
        "sku": "Egress Internet (Standard)",
        "unit": "EUR/TB",
        "price": 80.00,
        "source": URL_AZURE
    })

    # 4. Managed Kubernetes (AKS)
    records.append({
        "provider": "Azure",
        "region": "Italy North (Milan)",
        "kind": "k8s",
        "sku": "AKS Control Plane (Free Tier)",
        "unit": "EUR/mese",
        "price": 0.00,
        "source": "https://azure.microsoft.com/pricing/details/kubernetes-service/",
        "note": "Control plane gestito gratuito con SLA base"
    })

    # 5. Database Gestito (Azure Database for PostgreSQL Flexible Server)
    records.append({
        "provider": "Azure",
        "region": "Italy North (Milan)",
        "kind": "dbaas",
        "sku": "PostgreSQL Flexible (D2ds_v5 - 2vCPU / 8GB)",
        "unit": "EUR/mese",
        "price": 138.00,
        "source": "https://azure.microsoft.com/pricing/details/postgresql/flexible-server/",
        "note": "General Purpose Flexible Server"
    })

    return records

def extra():
    return []

def reserved():
    return []

def gpu():
    return []

if __name__ == "__main__":
    import json
    print(json.dumps(collect(), indent=2, ensure_ascii=False))
