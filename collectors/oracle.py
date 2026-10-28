from common import vm

def collect():
    records = []
    # OCI Standard E5 / E4 Flexible Instances (Prezzi di listino OCI standardizzati in EUR)
    # Taglie standard mappate su vCPU e RAM proporzionate
    tiers = [
        (1, 2, 8, "VM.Standard.E5.Flex (1 OCPU / 8GB)"),
        (2, 4, 16, "VM.Standard.E5.Flex (2 OCPU / 16GB)"),
        (4, 8, 32, "VM.Standard.E5.Flex (4 OCPU / 32GB)"),
        (8, 16, 64, "VM.Standard.E5.Flex (8 OCPU / 64GB)"),
    ]
    
    for ocpu, vcpu, ram, sku in tiers:
        # Calcolo orario basato su OCPU + RAM
        hourly = (ocpu * 0.0138) + (ram * 0.0018)
        monthly = round(hourly * 730, 2)
        records.append(vm(
            provider="Oracle Cloud",
            region="EU-Frankfurt",
            sku=sku,
            vcpu=vcpu,
            ram=ram,
            hourly=hourly,
            monthly=monthly,
            source="https://www.oracle.com/cloud/price-list/"
        ))

    # Aggiunta Block Storage e Object Storage OCI
    records.append({
        "provider": "Oracle Cloud",
        "region": "EU-Frankfurt",
        "kind": "storage",
        "sku": "Block Volume Storage (Balanced)",
        "unit": "EUR/GB/mese",
        "price": 0.023,
        "source": "https://www.oracle.com/cloud/price-list/"
    })
    
    records.append({
        "provider": "Oracle Cloud",
        "region": "EU-Frankfurt",
        "kind": "storage",
        "sku": "Object Storage Standard",
        "unit": "EUR/GB/mese",
        "price": 0.023,
        "source": "https://www.oracle.com/cloud/price-list/"
    })

    return records

if __name__ == "__main__":
    import json
    print(json.dumps(collect(), indent=2, ensure_ascii=False))
    
