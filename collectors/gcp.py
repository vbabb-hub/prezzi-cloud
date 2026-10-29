from common import vm, TIERS

URL_GCP = "https://cloud.google.com/pricing"

def collect():
    records = []

    # 1. Compute Engine N2 Standard
    n2_plans = [
        ("n2-standard-2", 2, 8, 0.097, 70.81),
        ("n2-standard-4", 4, 16, 0.194, 141.62),
        ("n2-standard-8", 8, 32, 0.388, 283.24),
        ("n2-standard-16", 16, 64, 0.776, 566.48),
    ]
    for sku, vcpu, ram, hourly, monthly in n2_plans:
        if vcpu in TIERS:
            records.append(vm("GCP", "europe-west8 (Milan)", sku, vcpu, ram, hourly, monthly=monthly, source=URL_GCP, note="N2 Standard"))

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

    # 3. Rete / Egress Internet
    records.append({
        "provider": "GCP",
        "region": "europe-west8 (Milan)",
        "kind": "rete",
        "sku": "Egress Internet Standard",
        "unit": "EUR/TB",
        "price": 85.00,
        "source": URL_GCP
    })

    # 4. Managed Kubernetes (GKE)
    records.append({
        "provider": "GCP",
        "region": "europe-west8 (Milan)",
        "kind": "k8s",
        "sku": "GKE Cluster Control Plane (Autopilot / Standard)",
        "unit": "EUR/mese",
        "price": 73.00,
        "source": "https://cloud.google.com/kubernetes-engine/pricing",
        "note": "$0.10/ora per cluster ($74/mo sconto sul primo cluster per account)"
    })

    # 5. Database Gestito (Cloud SQL for PostgreSQL)
    records.append({
        "provider": "GCP",
        "region": "europe-west8 (Milan)",
        "kind": "dbaas",
        "sku": "Cloud SQL PostgreSQL (2vCPU / 8GB RAM)",
        "unit": "EUR/mese",
        "price": 142.00,
        "source": "https://cloud.google.com/sql/pricing",
        "note": "Istanza gestita db-custom-2-8192"
    })

    return records

if __name__ == "__main__":
    import json
    print(json.dumps(collect(), indent=2, ensure_ascii=False))
