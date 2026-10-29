from common import vm, TIERS

URL_EXO = "https://www.exoscale.com/pricing/"

def collect():
    records = []
    # Istanze Compute "Starfish / OpenStack based" in Europa (Svizzera/DE)
    instances = [
        ("Standard Medium", 2, 4, 0.024, 17.50),
        ("Standard Large", 4, 8, 0.048, 35.00),
        ("Standard Extra-Large", 8, 16, 0.096, 70.00),
        ("Standard Huge", 16, 32, 0.192, 140.00),
    ]
    for sku, vcpu, ram, hourly, monthly in instances:
        if vcpu in TIERS:
            records.append(vm("Exoscale", "Frankfurt / Zurich", sku, vcpu, ram, hourly, monthly=monthly, source=URL_EXO, note="GDPR compliant European Cloud"))

    # Object Storage
    records.append({
        "provider": "Exoscale",
        "region": "Frankfurt",
        "kind": "storage",
        "sku": "Object Storage (S3)",
        "unit": "EUR/GB/mese",
        "price": 0.011,
        "source": URL_EXO
    })

    return records

if __name__ == "__main__":
    import json
    print(json.dumps(collect(), indent=2, ensure_ascii=False))
