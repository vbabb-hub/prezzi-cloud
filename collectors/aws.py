from common import vm, TIERS

URL_AWS = "https://aws.amazon.com/pricing/"

def collect():
    records = []
    
    # 1. Compute EC2 (m6i.large, m6i.xlarge, m6i.2xlarge, m6i.4xlarge)
    ec2_plans = [
        ("m6i.large", 2, 8, 0.1016, 74.17),
        ("m6i.xlarge", 4, 16, 0.2032, 148.34),
        ("m6i.2xlarge", 8, 32, 0.4064, 296.67),
        ("m6i.4xlarge", 16, 64, 0.8128, 593.34),
    ]
    for sku, vcpu, ram, hourly, monthly in ec2_plans:
        if vcpu in TIERS:
            records.append(vm("AWS", "eu-south-1 (Milan)", sku, vcpu, ram, hourly, monthly=monthly, source=URL_AWS, note="General Purpose m6i"))

    # 2. Storage EBS & S3
    records.append({
        "provider": "AWS",
        "region": "eu-south-1 (Milan)",
        "kind": "storage",
        "sku": "EBS gp3 (Block)",
        "unit": "EUR/GB/mese",
        "price": 0.088,
        "source": URL_AWS
    })
    records.append({
        "provider": "AWS",
        "region": "eu-south-1 (Milan)",
        "kind": "storage",
        "sku": "S3 Standard (Object)",
        "unit": "EUR/GB/mese",
        "price": 0.023,
        "source": URL_AWS
    })

    # 3. Rete / Egress Internet
    records.append({
        "provider": "AWS",
        "region": "eu-south-1 (Milan)",
        "kind": "rete",
        "sku": "Egress Internet (primi 10TB)",
        "unit": "EUR/TB",
        "price": 90.00,
        "source": URL_AWS
    })

    # 4. Managed Kubernetes (EKS)
    records.append({
        "provider": "AWS",
        "region": "eu-south-1 (Milan)",
        "kind": "k8s",
        "sku": "EKS Cluster Control Plane (Master)",
        "unit": "EUR/mese",
        "price": 73.00,
        "source": "https://aws.amazon.com/eks/pricing/",
        "note": "$0.10/ora fissa per cluster control plane (worker nodes esclusi)"
    })

    # 5. Database Gestito (RDS PostgreSQL)
    records.append({
        "provider": "AWS",
        "region": "eu-south-1 (Milan)",
        "kind": "dbaas",
        "sku": "RDS PostgreSQL (db.m6i.large - 2vCPU / 8GB)",
        "unit": "EUR/mese",
        "price": 145.00,
        "source": "https://aws.amazon.com/rds/postgresql/pricing/",
        "note": "Istanza Single-AZ gestita"
    })

    return records

def extra():
    return []

def s3():
    return []
    
if __name__ == "__main__":
    import json
    print(json.dumps(collect(), indent=2, ensure_ascii=False))
