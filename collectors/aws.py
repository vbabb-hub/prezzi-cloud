from common import vm, TIERS

URL_AWS = "https://aws.amazon.com/pricing/"

def collect():
    records = []
    
    # Flavor ampliati (General Purpose m6i, Compute c6i, Memory r6i)
    ec2_plans = [
        ("m6i.large", 2, 8, 0.1016, 74.17),
        ("m6i.xlarge", 4, 16, 0.2032, 148.34),
        ("m6i.2xlarge", 8, 32, 0.4064, 296.67),
        ("m6i.4xlarge", 16, 64, 0.8128, 593.34),
        ("m6i.8xlarge", 32, 128, 1.6256, 1186.68),
        ("c6i.large", 2, 4, 0.0903, 65.92),
        ("c6i.xlarge", 4, 8, 0.1806, 131.84),
        ("c6i.2xlarge", 8, 16, 0.3612, 263.68),
        ("c6i.4xlarge", 16, 32, 0.7224, 527.36),
        ("r6i.large", 2, 16, 0.126, 91.98),
        ("r6i.xlarge", 4, 32, 0.252, 183.96),
        ("r6i.2xlarge", 8, 64, 0.504, 367.92),
    ]
    for sku, vcpu, ram, hourly, monthly in ec2_plans:
        if vcpu in TIERS:
            records.append(vm("AWS", "eu-south-1 (Milan)", sku, vcpu, ram, hourly, monthly=monthly, source=URL_AWS, note="AWS EC2 Istanza Cloud"))

    # Storage
    records.append({"provider": "AWS", "region": "eu-south-1 (Milan)", "kind": "storage", "sku": "EBS gp3 (Block Storage)", "unit": "EUR/GB/mese", "price": 0.088, "source": URL_AWS})
    records.append({"provider": "AWS", "region": "eu-south-1 (Milan)", "kind": "storage", "sku": "S3 Standard (Object Storage)", "unit": "EUR/GB/mese", "price": 0.023, "source": URL_AWS})

    # Networking (Direct Connect in RETE, non colocation)
    records.append({"provider": "AWS", "region": "eu-south-1 (Milan)", "kind": "rete", "sku": "Egress Internet (primi 10TB)", "unit": "EUR/TB", "price": 90.00, "source": URL_AWS})
    records.append({"provider": "AWS", "region": "eu-south-1 (Milan)", "kind": "rete", "sku": "AWS Direct Connect Port (1Gbps)", "unit": "EUR/mese", "price": 220.00, "source": URL_AWS})

    # GPU
    records.append({"provider": "AWS", "region": "eu-south-1 (Milan)", "kind": "gpu", "sku": "g5.2xlarge (1x NVIDIA A10G)", "unit": "EUR/mese", "price": 950.00, "source": URL_AWS, "note": "GPU NVIDIA A10G"})

    # Licenze
    records.append({"provider": "AWS", "region": "eu-south-1 (Milan)", "kind": "licenses", "sku": "Windows Server Standard (per vCPU)", "unit": "EUR/mese", "price": 23.00, "source": URL_AWS})

    # Kubernetes & DBaaS
    records.append({"provider": "AWS", "region": "eu-south-1 (Milan)", "kind": "k8s", "sku": "EKS Cluster Control Plane", "unit": "EUR/mese", "price": 73.00, "source": URL_AWS})
    records.append({"provider": "AWS", "region": "eu-south-1 (Milan)", "kind": "dbaas", "sku": "RDS PostgreSQL (db.m6i.large)", "unit": "EUR/mese", "price": 145.00, "source": URL_AWS})

    return records

def extra(): return []
def s3(): return []
