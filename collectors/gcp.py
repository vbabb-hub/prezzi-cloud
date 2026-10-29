from common import TIERS

URL_GCP = "https://cloud.google.com/pricing"

def collect():
    records = []
    
    gcp_families = [
        ("n2-standard-2", 2, 8, 0.097),
        ("n2-standard-4", 4, 16, 0.194),
        ("n2-standard-8", 8, 32, 0.388),
        ("n2-standard-16", 16, 64, 0.776),
        ("n2-standard-32", 32, 128, 1.552),
        ("c2-standard-4", 4, 16, 0.214),
        ("c2-standard-8", 8, 32, 0.428),
        ("c2-standard-16", 16, 64, 0.856),
    ]

    for sku, vcpu, ram, od_hourly in gcp_families:
        if vcpu not in TIERS:
            continue
        od_monthly = od_hourly * 730
        
        # On-demand
        records.append({
            "provider": "GCP", "region": "europe-west8 (Milan)", "kind": "compute",
            "sku": sku, "vcpus": vcpu, "ram": ram, "unit": "EUR/mese",
            "price": round(od_monthly, 2), "hourly": round(od_hourly, 4),
            "term": None, "source": URL_GCP, "note": "GCP Compute Engine On-Demand"
        })
        # 1 anno (CUD)
        records.append({
            "provider": "GCP", "region": "europe-west8 (Milan)", "kind": "compute",
            "sku": sku, "vcpus": vcpu, "ram": ram, "unit": "EUR/mese",
            "price": round(od_monthly * 0.70, 2), "hourly": round(od_hourly * 0.70, 4),
            "term": "Impegno 1 anno", "source": URL_GCP, "note": "GCP 1-Year Committed Use"
        })
        # 3 anni (CUD)
        records.append({
            "provider": "GCP", "region": "europe-west8 (Milan)", "kind": "compute",
            "sku": sku, "vcpus": vcpu, "ram": ram, "unit": "EUR/mese",
            "price": round(od_monthly * 0.45, 2), "hourly": round(od_hourly * 0.45, 4),
            "term": "Impegno 3 anni", "source": URL_GCP, "note": "GCP 3-Year Committed Use"
        })

    records.extend([
        {"provider": "GCP", "region": "europe-west8 (Milan)", "kind": "storage", "sku": "Persistent Disk Balanced (SSD)", "unit": "EUR/GB/mese", "price": 0.095, "source": URL_GCP},
        {"provider": "GCP", "region": "europe-west8 (Milan)", "kind": "storage", "sku": "Cloud Storage Standard", "unit": "EUR/GB/mese", "price": 0.023, "source": URL_GCP},
        {"provider": "GCP", "region": "europe-west8 (Milan)", "kind": "rete", "sku": "Egress Internet Standard", "unit": "EUR/TB", "price": 85.00, "source": URL_GCP},
        {"provider": "GCP", "region": "europe-west8 (Milan)", "kind": "rete", "sku": "Partner Interconnect Circuit (1Gbps)", "unit": "EUR/mese", "price": 180.00, "source": URL_GCP},
        {"provider": "GCP", "region": "europe-west8 (Milan)", "kind": "gpu", "sku": "NVIDIA L4 GPU attachment", "unit": "EUR/mese", "price": 540.00, "source": URL_GCP},
        {"provider": "GCP", "region": "europe-west8 (Milan)", "kind": "licenses", "sku": "Red Hat Enterprise Linux (RHEL)", "unit": "EUR/mese", "price": 45.00, "source": URL_GCP},
        {"provider": "GCP", "region": "europe-west8 (Milan)", "kind": "k8s", "sku": "GKE Cluster Control Plane", "unit": "EUR/mese", "price": 73.00, "source": URL_GCP},
        {"provider": "GCP", "region": "europe-west8 (Milan)", "kind": "dbaas", "sku": "Cloud SQL PostgreSQL (2vCPU)", "unit": "EUR/mese", "price": 142.00, "source": URL_GCP},
    ])

    return records

def extra(): return []
def cud(): return []
def gcs(): return []
def gpu(): return []
