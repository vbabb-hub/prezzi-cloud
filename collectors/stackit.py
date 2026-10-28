from common import vm

def collect():
    records = []
    # STACKIT (Germania / EU01) - Listini pubblici ufficiali Compute Engine & General Purpose
    instances = [
        ("General Purpose g3i.1", 1, 4, 0.0585, "EUR/ora"),
        ("General Purpose g3i.2", 2, 8, 0.1031, "EUR/ora"),
        ("General Purpose g3i.4", 4, 16, 0.2061, "EUR/ora"),
        ("General Purpose g3i.8", 8, 32, 0.4123, "EUR/ora"),
        ("General Purpose g3i.16", 16, 59, 0.8246, "EUR/ora"),
        ("Compute Optimized c3i.1", 1, 2, 0.0493, "EUR/ora"),
        ("Compute Optimized c3i.2", 2, 4, 0.0869, "EUR/ora"),
        ("Compute Optimized c3i.4", 4, 8, 0.1739, "EUR/ora"),
        ("Compute Optimized c3i.8", 8, 16, 0.3478, "EUR/ora"),
    ]
    
    for sku, vcpu, ram, hourly, unit in instances:
        monthly = round(hourly * 730, 2)
        records.append(vm(
            provider="STACKIT",
            region="DE-Frankfurt",
            sku=sku,
            vcpu=vcpu,
            ram=ram,
            hourly=hourly,
            monthly=monthly,
            source="https://stackit.com/en/products/compute-engine/stackit-compute-engine"
        ))
        
    # Aggiunta Object Storage STACKIT
    records.append({
        "provider": "STACKIT",
        "region": "DE-Frankfurt",
        "kind": "storage",
        "sku": "Object Storage Standard",
        "unit": "EUR/GB/mese",
        "price": 0.006,
        "source": "https://stackit.com/en/products/object-storage"
    })

    return records

if __name__ == "__main__":
    import json
    print(json.dumps(collect(), indent=2, ensure_ascii=False))
  
