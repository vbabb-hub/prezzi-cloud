from common import TIERS

URL_AWS = "https://aws.amazon.com/pricing/"

def collect():
    records = []
    
    # Famiglie EC2 estese (General Purpose, Compute Optimized, Memory Optimized)
    families = [
        # (Famiglia, vcpu, ram_gb, prezzo_on_demand_orario)
        ("m6i.large", 2, 8, 0.1016),
        ("m6i.xlarge", 4, 16, 0.2032),
        ("m6i.2xlarge", 8, 32, 0.4064),
        ("m6i.4xlarge", 16, 64, 0.8128),
        ("m6i.8xlarge", 32, 128, 1.6256),
        ("c6i.large", 2, 4, 0.0903),
        ("c6i.xlarge", 4, 8, 0.1806),
        ("c6i.2xlarge", 8, 16, 0.3612),
        ("c6i.4xlarge", 16, 32, 0.7224),
        ("c6i.8xlarge", 32, 64, 1.4448),
        ("r6i.large", 2, 16, 0.1260),
        ("r6i.xlarge", 4, 32, 0.2520),
        ("r6i.2xlarge", 8, 64, 0.5040),
        ("r6i.4xlarge", 16, 128, 1.0080),
    ]

    for sku, vcpu, ram, od_hourly in families:
        if vcpu not in TIERS:
            continue
        od_monthly = od_hourly * 730
        
        # 1. On-demand
        records.append({
            "provider": "AWS", "region": "eu-south-1 (Milan)", "kind": "compute",
            "sku": sku, "vcpus": vcpu, "ram": ram, "unit": "EUR/mese",
            "price": round(od_monthly, 2), "hourly": round(od_hourly, 4),
            "term": None, "source": URL_AWS, "note": "AWS EC2 On-Demand"
        })
        # 2. Impegno 1 anno (~30% sconto)
        records.append({
            "provider": "AWS", "region": "eu-south-1 (Milan)", "kind": "compute",
            "sku": sku, "vcpus": vcpu, "ram": ram, "unit": "EUR/mese",
            "price": round(od_monthly * 0.70, 2), "hourly": round(od_hourly * 0.70, 4),
            "term": "Impegno 1 anno", "source": URL_AWS, "note": "AWS EC2 1-Year Reserved"
        })
        # 3. Impegno 3 anni (~50% sconto)
        records.append({
            "provider": "AWS", "region": "eu-south-1 (Milan)", "kind": "compute",
            "sku": sku, "vcpus": vcpu, "ram": ram, "unit": "EUR/mese",
            "price": round(od_monthly * 0.50, 2), "hourly": round(od_hourly * 0.50, 4),
            "term": "Impegno 3 anni", "source": URL_AWS, "note": "AWS EC2 3-Year Reserved"
        })

    # Altre categorie (Storage, Rete, GPU, Licenze, K8s, DBaaS)
    records.extend([
        {"provider": "AWS", "region": "eu-south-1 (Milan)", "kind": "storage", "sku": "EBS gp3 (Block Storage)", "unit": "EUR/GB/mese", "price": 0.088, "source": URL_AWS},
        {"provider": "AWS", "region": "eu-south-1 (Milan)", "kind": "storage", "sku": "S3 Standard (Object Storage)", "unit": "EUR/GB/mese", "price": 0.023, "source": URL_AWS},
        {"provider": "AWS", "region": "eu-south-1 (Milan)", "kind": "rete", "sku": "Egress Internet (primi 10TB)", "unit": "EUR/TB", "price": 90.00, "source": URL_AWS},
        {"provider": "AWS", "region": "eu-south-1 (Milan)", "kind": "rete", "sku": "AWS Direct Connect Port (1Gbps)", "unit": "EUR/mese", "price": 220.00, "source": URL_AWS},
        {"provider": "AWS", "region": "eu-south-1 (Milan)", "kind": "gpu", "sku": "g5.2xlarge (1x NVIDIA A10G)", "unit": "EUR/mese", "price": 950.00, "source": URL_AWS},
        {"provider": "AWS", "region": "eu-south-1 (Milan)", "kind": "licenses", "sku": "Windows Server Standard (per vCPU)", "unit": "EUR/mese", "price": 23.00, "source": URL_AWS},
        {"provider": "AWS", "region": "eu-south-1 (Milan)", "kind": "k8s", "sku": "EKS Cluster Control Plane", "unit": "EUR/mese", "price": 73.00, "source": URL_AWS},
        {"provider": "AWS", "region": "eu-south-1 (Milan)", "kind": "dbaas", "sku": "RDS PostgreSQL (db.m6i.large)", "unit": "EUR/mese", "price": 145.00, "source": URL_AWS},
    ])

    return records

def extra(): return []
def s3(): return []
