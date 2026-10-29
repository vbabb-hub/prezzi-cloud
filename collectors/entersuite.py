from common import vm, TIERS

URL_ENTER = "https://www.entercloudsuite.com/it/prezzi/"

def collect():
    records = []
    # Taglie Standard OpenStack
    nodes = [
        ("OpenStack Standard 2vCPU", 2, 8, 0.045, 32.85),
        ("OpenStack Standard 4vCPU", 4, 16, 0.090, 65.70),
        ("OpenStack Standard 8vCPU", 8, 32, 0.180, 131.40),
        ("OpenStack Standard 16vCPU", 16, 64, 0.360, 262.80),
    ]
    for sku, vcpu, ram, hourly, monthly in nodes:
        if vcpu in TIERS:
            records.append(vm("Enter Cloud Suite", "Milan / Frankfurt", sku, vcpu, ram, hourly, monthly=monthly, source=URL_ENTER, note="Certificato AGID / OpenStack"))

    # Storage Block
    records.append({
        "provider": "Enter Cloud Suite",
        "region": "Milan",
        "kind": "storage",
        "sku": "Enterprise Block Storage SSD",
        "unit": "EUR/GB/mese",
        "price": 0.08,
        "source": URL_ENTER
    })

    return records

if __name__ == "__main__":
    import json
    print(json.dumps(collect(), indent=2, ensure_ascii=False))
