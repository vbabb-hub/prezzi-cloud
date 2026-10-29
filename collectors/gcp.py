from common import vm, TIERS

URL_GCP = "https://cloud.google.com/pricing"

def collect():
    records = []
    
    # 1. Compute Engine N2 & C2 Standard
    n2_plans = [
        ("n2-standard-2", 2, 8, 0.097, 70.81),
        ("n2-standard-4", 4, 16, 0.194, 141.62),
        ("n2-standard-8", 8, 32, 0.388, 283.24),
        ("n2-standard-16", 16, 64, 0.776, 566.48),
        ("c2-standard-4", 4, 16, 0.214, 156.22),
    ]
    for sku, vcpu, ram, hourly, monthly in n2_plans:
        if vcpu in TIERS:
            records.append(vm("GCP", "europe-west8 (Milan)", sku, vcpu, ram, hourly, monthly=monthly, source=URL_GCP, note="Compute Engine Standard"))

    # 2. Storage Persistent Disk & Cloud Storage
    records.append({
        "provider": "GCP",
        "region": "europe-west8 (Milan)",
        "kind": "storage",
        "sku": "Persistent Disk Balanced (SSD)",
        "unit": "EUR/GB/mese",
        "price": 0.095,
        "source": URL_GCP
    })
    records.append({
        "provider": "GCP",
        "region": "europe-west8 (Milan)",
        "kind": "storage",
        "sku": "Cloud Storage Standard (Object)",
        "unit": "EUR/GB/mese",
        "price": 0.023,
        "source": URL_GCP
    })

    # 3. Networking / Egress Internet
    records.append({
        "provider": "GCP",
        "region": "europe-west8 (Milan)",
        "kind": "rete",
        "sku": "Egress Internet Standard",
        "unit": "EUR/TB",
        "price": 85.00,
        "source": URL_GCP
    })

    # 4. GPU Instances (NVIDIA L4 / T4)
    records.append({
        "provider": "GCP",
        "region": "europe-west8 (Milan)",
        "kind": "gpu",
        "sku": "NVIDIA L4 GPU attachment",
        "unit": "EUR/mese",
        "price": 540.00,
        "source": URL_GCP,
        "note": "acceleratore grafico per IA e rendering"
    })

    # 5. Colocation / Interconnect
    records.append({
        "provider": "GCP",
        "region": "europe-west8 (Milan)",
        "kind": "colocation",
        "sku": "Partner Interconnect Circuit (1Gbps)",
        "unit": "EUR/mese",
        "price": 180.00,
        "source": URL_GCP
    })

    # 6. Licenses (RHEL / Windows su GCP)
    records.append({
        "provider": "GCP",
        "region": "europe-west8 (Milan)",
        "kind": "licenses",
        "sku": "Red Hat Enterprise Linux (RHEL)",
        "unit": "EUR/mese",
        "price": 45.00,
        "source": URL_GCP
    })

    # 7. Managed Kubernetes (GKE)
    records.append({
        "provider": "GCP",
        "region": "europe-west8 (Milan)",
        "kind": "k8s",
        "sku": "GKE Cluster Control Plane",
        "unit": "EUR/mese",
        "price": 73.00,
        "source": "https://cloud.google.com/kubernetes-engine/pricing",
        "note": "$0.10/ora per cluster"
    })

    # 8. Managed Database (Cloud SQL PostgreSQL)
    records.append({
        "provider": "GCP",
        "region": "europe-west8 (Milan)",
        "kind": "dbaas",
        "sku": "Cloud SQL PostgreSQL (2vCPU / 8GB RAM)",
        "unit": "EUR/mese",
        "price": 142.00,
        "source": "https://cloud.google.com/sql/pricing",
        "note": "Managed instance db-custom-2-8192"
    })

    return records

def extra():
    return []

def cud():
    return []

def gcs():
    return []

def gpu():
    return []

if __name__ == "__main__":
    import json
    print(json.dumps(collect(), indent=2, ensure_ascii=False))
