from common import vm, TIERS

URL_AWS = "https://aws.amazon.com/pricing/"

def collect():
    records = []
    
    # Ampia gamma di istanze AWS (m6i, c6i, r6i, c7i, m7i in varie taglie)
    families = [
        # (SKU, vCPU, RAM_GB, Prezzo Orario On-Demand stimato EUR)
        ("m6i.large", 2, 8, 0.1016),
        ("m6i.xlarge", 4, 16, 0.2032),
        ("m6i.2xlarge", 8, 32, 0.4064),
        ("m6i.4xlarge", 16, 64, 0.8128),
        ("m6i.8xlarge", 32, 128, 1.6256),
        ("m6i.12xlarge", 48, 192, 2.4384),
        ("m6i.16xlarge", 64, 256, 3.2512),
        ("c6i.large", 2, 4, 0.0903),
        ("c6i.xlarge", 4, 8, 0.1806),
        ("c6i.2xlarge", 8, 16, 0.3612),
        ("c6i.4xlarge", 16, 32, 0.7224),
        ("c6i.8xlarge", 32, 64, 1.4448),
        ("c6i.12xlarge", 48, 96, 2.1672),
        ("c6i.16xlarge", 64, 128, 2.8896),
        ("r6i.large", 2, 16, 0.1260),
        ("r6i.xlarge", 4, 32, 0.2520),
        ("r6i.2xlarge", 8, 64, 0.5040),
        ("r6i.4xlarge", 16, 128, 1.0080),
        ("r6i.8xlarge", 32, 256, 2.0160),
        ("m7i.large", 2, 8, 0.1050),
        ("m7i.xlarge", 4, 16, 0.2100),
        ("m7i.2xlarge", 8, 32, 0.4200),
        ("m7i.4xlarge", 16, 64, 0.8400),
    ]

    for sku, vcpu, ram, od_hourly in families:
        if vcpu not in TIERS:
            continue
        od_monthly = od_hourly * 730
        
        # On-demand
        r_od = vm("AWS", "eu-south-1 (Milan)", sku, vcpu, ram, od_hourly, monthly=od_monthly, source=URL_AWS, note="AWS EC2 On-Demand")
        r_od["term"] = "On-demand"
        records.append(r_od)
        
        # Impegno 1 anno (~30% sconto)
        r_1y = vm("AWS", "eu-south-1 (Milan)", sku, vcpu, ram, od_hourly * 0.70, monthly=od_monthly * 0.70, source=URL_AWS, note="AWS EC2 1-Year Reserved")
        r_1y["term"] = "Impegno 1 anno"
        records.append(r_1y)
        
        # Impegno 3 anni (~50% sconto)
        r_3y = vm("AWS", "eu-south-1 (Milan)", sku, vcpu, ram, od_hourly * 0.50, monthly=od_monthly * 0.50, source=URL_AWS, note="AWS EC2 3-Year Reserved")
        r_3y["term"] = "Impegno 3 anni"
        records.append(r_3y)

    # Categorie complementari
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
