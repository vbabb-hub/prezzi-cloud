from common import vm, TIERS

URL_DO = "https://www.digitalocean.com/pricing"

def collect():
    records = []
    # Droplets Basic (Standard SSD)
    droplets = [
        ("Basic s-1vcpu-1gb", 1, 1, 0.007, 4.00),
        ("Basic s-1vcpu-2gb", 1, 2, 0.015, 10.00),
        ("Basic s-2vcpu-4gb", 2, 4, 0.030, 20.00),
        ("Basic s-4vcpu-8gb", 4, 8, 0.060, 40.00),
        ("Basic s-8vcpu-16gb", 8, 16, 0.119, 80.00),
    ]
    for sku, vcpu, ram, hourly, monthly in droplets:
        if vcpu in TIERS:
            records.append(vm("DigitalOcean", "Frankfurt / Amsterdam", sku, vcpu, ram, hourly, monthly=monthly, source=URL_DO, note="Standard Droplet"))

    # Kubernetes (DOKS) - Control plane gratuito, si pagano solo i nodi worker (stessi prezzi dei droplets)
    records.append({
        "provider": "DigitalOcean",
        "region": "Frankfurt",
        "kind": "k8s",
        "sku": "DOKS Control Plane (Master)",
        "unit": "EUR/mese",
        "price": 0.00,
        "source": URL_DO,
        "note": "Control plane gestito gratuito"
    })

    # Managed Database (PostgreSQL 2vCPU / 8GB)
    records.append({
        "provider": "DigitalOcean",
        "region": "Frankfurt",
        "kind": "dbaas",
        "sku": "Managed PostgreSQL (2vCPU / 8GB RAM)",
        "unit": "EUR/mese",
        "price": 110.00,
        "source": URL_DO,
        "note": "Standalone basic instance"
    })

    # Object Storage (Spaces)
    records.append({
        "provider": "DigitalOcean",
        "region": "Frankfurt",
        "kind": "storage",
        "sku": "Spaces Object Storage (250GB incl. + 1TB egress)",
        "unit": "EUR/mese",
        "price": 5.00,
        "source": URL_DO
    })

    return records

if __name__ == "__main__":
    import json
    print(json.dumps(collect(), indent=2, ensure_ascii=False))
