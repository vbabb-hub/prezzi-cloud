from common import vm, TIERS

URL_AWS = "https://aws.amazon.com/pricing/"

def collect():
    records = []
    
    # 1. Compute EC2 (m6i e c6i)
    ec2_plans = [
        ("m6i.large", 2, 8, 0.1016, 74.17),
        ("m6i.xlarge", 4, 16, 0.2032, 148.34),
        ("m6i.2xlarge", 8, 32, 0.4064, 296.67),
        ("m6i.4xlarge", 16, 64, 0.8128, 593.34),
        ("c6i.large", 2, 4, 0.0903, 65.92),
        ("c6i.xlarge", 4, 8, 0.1806, 131.84),
    ]
    for sku, vcpu, ram, hourly, monthly in ec2_plans:
        if vcpu in TIERS:
            records.append(vm("AWS", "eu-south-1 (Milan)", sku, vcpu, ram, hourly, monthly=monthly, source=URL_AWS, note="Compute Ottimizzato / General Purpose"))

    # 2. Storage EBS & S3
    records.append({
        "provider": "AWS",
        "region": "eu-south-1 (Milan)",
        "kind": "storage",
        "sku": "EBS gp3 (Block Storage)",
        "unit": "EUR/GB/mese",
        "price": 0.088,
        "source": URL_AWS
    })
    records.append({
        "provider": "AWS",
        "region": "eu-south-1 (Milan)",
        "kind": "storage",
        "sku": "S3 Standard (Object Storage)",
        "unit": "EUR/GB/mese",
        "price": 0.023,
        "source": URL_AWS
    })

    # 3. Networking / Egress Internet & Direct Connect (Spostato in rete)
    records.append({
        "provider": "AWS",
        "region": "eu-south-1 (Milan)",
        "kind": "rete",
        "sku": "Egress Internet (primi 10TB)",
        "unit": "EUR/TB",
        "price": 90.00,
        "source": URL_AWS
    })
    records.append({
        "provider": "AWS",
        "region": "eu-south-1 (Milan)",
        "kind": "rete",
        "sku": "AWS Direct Connect Port (1Gbps)",
        "unit": "EUR/mese",
        "price": 220.00,
        "source": URL_AWS
    })

    # 4. GPU Instances (g5.2xlarge)
    records.append({
        "provider": "AWS",
        "region": "eu-south-1 (Milan)",
        "kind": "gpu",
        "sku": "g5.2xlarge (1x NVIDIA A10G)",
        "unit": "EUR/mese",
        "price": 950.00,
        "source": URL_AWS,
        "note": "Istanza accelerata con GPU NVIDIA"
    })

    # 5. Licenses (Windows Server on AWS)
    records.append({
        "provider": "AWS",
        "region": "eu-south-1 (Milan)",
        "kind": "licenses",
        "sku": "Windows Server Standard (per vCPU)",
        "unit": "EUR/mese",
        "price": 23.00,
        "source": URL_AWS
    })

    # 6. Managed Kubernetes (EKS)
    records.append({
        "provider": "AWS",
        "region": "eu-south-1 (Milan)",
        "kind": "k8s",
        "sku": "EKS Cluster Control Plane",
        "unit": "EUR/mese",
        "price": 73.00,
        "source": "https://aws.amazon.com/eks/pricing/",
        "note": "$0.10/ora fissa per cluster control plane"
    })

    # 7. Managed Database (RDS PostgreSQL)
    records.append({
        "provider": "AWS",
        "region": "eu-south-1 (Milan)",
        "kind": "dbaas",
        "sku": "RDS PostgreSQL (db.m6i.large - 2vCPU / 8GB)",
        "unit": "EUR/mese",
        "price": 145.00,
        "source": "https://aws.amazon.com/rds/postgresql/pricing/",
        "note": "Single-AZ Managed Database"
    })

    return records

def extra():
    return []

def s3():
    return []

if __name__ == "__main__":
    import json
    print(json.dumps(collect(), indent=2, ensure_ascii=False))
