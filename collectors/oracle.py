from common import vm, TIERS

URL_OCI = "https://www.oracle.com/cloud/pricing/"

def collect():
    records = []

    # 1. Compute VM.Standard.A1.Flex (ARM) & E4.Flex (x86)
    oci_plans = [
        ("VM.Standard.E4.Flex (2vCPU/8GB)", 2, 8, 0.054, 39.42),
        ("VM.Standard.E4.Flex (4vCPU/16GB)", 4, 16, 0.108, 78.84),
        ("VM.Standard.E4.Flex (8vCPU/32GB)", 8, 32, 0.216, 157.68),
        ("VM.Standard.E4.Flex (16vCPU/64GB)", 16, 64, 0.432, 315.36),
    ]
    for sku, vcpu, ram, hourly, monthly in oci_plans:
        if vcpu in TIERS:
            records.append(vm("Oracle Cloud", "eu-milan-1", sku, vcpu, ram, hourly, monthly=monthly, source=URL_OCI, note="OCI E4 Flex"))

    # 2. Storage Block Volume & Object Storage
    records.append({
        "provider": "Oracle Cloud",
        "region": "eu-milan-1",
        "kind": "storage",
        "sku": "Block Volume (Performance Balanced)",
        "unit": "EUR/GB/mese",
        "price": 0.025,
        "source": URL_OCI
    })
    records.append({
        "provider": "Oracle Cloud",
        "region": "eu-milan-1",
        "kind": "storage",
        "sku": "Object Storage Standard",
        "unit": "EUR/GB/mese",
        "price": 0.023,
        "source": URL_OCI
    })

    # 3. Rete / Egress Internet
    records.append({
        "provider": "Oracle Cloud",
        "region": "eu-milan-1",
        "kind": "rete",
        "sku": "Egress Internet (Oltre 10TB gratuiti incl.)",
        "unit": "EUR/TB",
        "price": 8.50,
        "source": URL_OCI
    })

    # 4. Managed Kubernetes (OKE)
    records.append({
        "provider": "Oracle Cloud",
        "region": "eu-milan-1",
        "kind": "k8s",
        "sku": "OKE Kubernetes Control Plane (Basic)",
        "unit": "EUR/mese",
        "price": 0.00,
        "source": "https://www.oracle.com/cloud/cloud-native/container-engine-kubernetes/pricing/",
        "note": "Control plane gestito gratuito per il tier Basic"
    })

    # 5. Database Gestito (OCI Database with PostgreSQL)
    records.append({
        "provider": "Oracle Cloud",
        "region": "eu-milan-1",
        "kind": "dbaas",
        "sku": "OCI Database with PostgreSQL (2vCPU / 8GB)",
        "unit": "EUR/mese",
        "price": 68.00,
        "source": "https://www.oracle.com/database/postgresql/pricing/",
        "note": "Database gestito ad altissime prestazioni"
    })

    return records

if __name__ == "__main__":
    import json
    print(json.dumps(collect(), indent=2, ensure_ascii=False))
