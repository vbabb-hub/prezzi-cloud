from common import vm, TIERS

URL_GCP = "https://cloud.google.com/pricing"

def collect():
    records = []
    
    gcp_families = [
        ("n2-standard-2", 2, 8, 0.097),
        ("n2-standard-4", 4, 16, 0.194),
        ("n2-standard-8", 8, 32, 0.388),
        ("n2-standard-16", 16, 64, 0.776),
        ("n2-standard-32", 32, 128, 1.552),
        ("n2-standard-48", 48, 192, 2.328),
        ("n2-standard-64", 64, 256, 3.104),
        ("c2-standard-4", 4, 16, 0.214),
        ("c2-standard-8", 8, 32, 0.428),
        ("c2-standard-16", 16, 64, 0.856),
        ("c2-standard-30", 30, 120, 1.605),
        ("e2-standard-2", 2, 8, 0.067),
        ("e2-standard-4", 4, 16, 0.134),
        ("e2-standard-8", 8, 32, 0.268),
        ("e2-standard-16", 16, 64, 0.536),
    ]

    for sku, vcpu, ram, od_hourly in gcp_families:
        if vcpu not in TIERS:
            continue
        od_monthly = od_hourly * 730
        
        r_od = vm("GCP", "europe-west8 (Milan)", sku, vcpu, ram, od_hourly, monthly=od_monthly, source=URL_GCP, note="GCP Compute Engine On-Demand")
        r_od["term"] = "On-demand"
        records.append(r_od)
        
        r_1y = vm("GCP", "europe-west8 (Milan)", sku, vcpu, ram, od_hourly * 0.70, monthly=od_monthly * 0.70, source=URL_GCP, note="GCP 1-Year CUD")
        r_1y["term"] = "Impegno 1 anno"
        records.append(r_1y)
        
        r_3y = vm("GCP", "europe-west8 (Milan)", sku, vcpu, ram, od_hourly * 0.45, monthly=od_monthly * 0.45, source=URL_GCP, note="GCP 3-Year CUD")
        r_3y["term"] = "Impegno 3 anni"
        records.append(r_3y)

    records.extend([
        {"provider": "GCP", "region": "europe-west8 (Milan)", "kind": "storage", "sku": "Persistent Disk Balanced (SSD)", "unit": "EUR/GB/mese", "price": 0.095, "source": URL_GCP},
        {"provider": "GCP", "region": "europe-west8 (Milan)", "kind": "storage", "sku": "Cloud Storage Standard", "unit": "EUR/GB/mese", "price": 0.023, "source": URL_GCP},
        {"provider": "GCP", "region": "europe-west8 (Milan)", "kind": "rete", "sku": "Egress Internet Standard", "unit": "EUR/TB", "price": 85.00, "source": URL_GCP},
        {"provider": "GCP", "region": "europe-west8 (Milan)", "kind": "rete", "sku": "Partner Interconnect Circuit (1Gbps)", "unit": "EUR/mese", "price": 180.00, "source": URL_GCP},
        {"provider": "GCP", "region": "europe-west8 (Milan)", "kind": "gpu", "sku": "NVIDIA L4 GPU attachment", "unit": "EUR/mese", "price": 540.00, "source": URL_GCP},
        {"provider": "GCP", "region": "europe-west8 (Milan)", "kind": "licenses", "sku": "Red Hat Enterprise Linux (RHEL)", "unit": "EUR/mese", "price": 45.00, "source": URL_GCP},
        {"provider": "GCP", "region": "europe-west8 (Milan)", "kind": "k8s", "sku": "GKE Cluster Control Plane", "unit": "EUR/mese", "price": 73.00, "source": URL_GCP},
        {"provider": "GCP", "region": "europe-west8 (Milan)", "kind": "dbaas", "sku": "Cloud SQL PostgreSQL", "unit": "EUR/mese", "price": 142.00, "source": URL_GCP},
    ])

    return records

def extra(): return []
def cud(): return []
def gcs(): return []
def gpu(): return []
