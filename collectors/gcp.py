from common import vm, TIERS

URL_GCP = "https://cloud.google.com/pricing"

def collect():
    records = []
    
    # Flavor ampliati (N2 e C2 Standard)
    n2_plans = [
        ("n2-standard-2", 2, 8, 0.097, 70.81),
        ("n2-standard-4", 4, 16, 0.194, 141.62),
        ("n2-standard-8", 8, 32, 0.388, 283.24),
        ("n2-standard-16", 16, 64, 0.776, 566.48),
        ("n2-standard-32", 32, 128, 1.552, 1132.96),
        ("c2-standard-4", 4, 16, 0.214, 156.22),
        ("c2-standard-8", 8, 32, 0.428, 312.44),
        ("c2-standard-16", 16, 64, 0.856, 624.88),
    ]
    for sku, vcpu, ram, hourly, monthly in n2_plans:
        if vcpu in TIERS:
            records.append(vm("GCP", "europe-west8 (Milan)", sku, vcpu, ram, hourly, monthly=monthly, source=URL_GCP, note="GCP Compute Engine"))

    # Storage
    records.append({"provider": "GCP", "region": "europe-west8 (Milan)", "kind": "storage", "sku": "Persistent Disk Balanced (SSD)", "unit": "EUR/GB/mese", "price": 0.095, "source": URL_GCP})
    records.append({"provider": "GCP", "region": "europe-west8 (Milan)", "kind": "storage", "sku": "Cloud Storage Standard", "unit": "EUR/GB/mese", "price": 0.023, "source": URL_GCP})

    # Networking (Interconnect in RETE, non colocation)
    records.append({"provider": "GCP", "region": "europe-west8 (Milan)", "kind": "rete", "sku": "Egress Internet Standard", "unit": "EUR/TB", "price": 85.00, "source": URL_GCP})
    records.append({"provider": "GCP", "region": "europe-west8 (Milan)", "kind": "rete", "sku": "Partner Interconnect Circuit (1Gbps)", "unit": "EUR/mese", "price": 180.00, "source": URL_GCP})

    # GPU
    records.append({"provider": "GCP", "region": "europe-west8 (Milan)", "kind": "gpu", "sku": "NVIDIA L4 GPU attachment", "unit": "EUR/mese", "price": 540.00, "source": URL_GCP})

    # Licenze
    records.append({"provider": "GCP", "region": "europe-west8 (Milan)", "kind": "licenses", "sku": "Red Hat Enterprise Linux (RHEL)", "unit": "EUR/mese", "price": 45.00, "source": URL_GCP})

    # Kubernetes & DBaaS
    records.append({"provider": "GCP", "region": "europe-west8 (Milan)", "kind": "k8s", "sku": "GKE Cluster Control Plane", "unit": "EUR/mese", "price": 73.00, "source": URL_GCP})
    records.append({"provider": "GCP", "region": "europe-west8 (Milan)", "kind": "dbaas", "sku": "Cloud SQL PostgreSQL (2vCPU)", "unit": "EUR/mese", "price": 142.00, "source": URL_GCP})

    return records

def extra(): return []
def cud(): return []
def gcs(): return []
def gpu(): return []
