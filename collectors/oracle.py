from common import vm

def collect():
    records = []
    tiers = [
        (1, 2, 8, "VM.Standard.E5.Flex (2 vCPU / 8GB)"),
        (2, 4, 16, "VM.Standard.E5.Flex (4 vCPU / 16GB)"),
        (4, 8, 32, "VM.Standard.E5.Flex (8 vCPU / 32GB)"),
        (8, 16, 64, "VM.Standard.E5.Flex (16 vCPU / 64GB)"),
        (1, 2, 4, "VM.Standard.E5.Flex (2 vCPU / 4GB)"),
        (2, 4, 8, "VM.Standard.E5.Flex (4 vCPU / 8GB)"),
        (4, 8, 16, "VM.Standard.E5.Flex (8 vCPU / 16GB)"),
        (8, 16, 32, "VM.Standard.E5.Flex (16 vCPU / 32GB)"),
    ]
    
    for ocpu, vcpu, ram, sku in tiers:
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

    records.append({
        "provider": "Oracle Cloud",
        "region": "EU-Frankfurt",
        "kind": "rete",
        "sku": "Egress Internet (oltre i primi 10TB gratuiti)",
        "unit": "EUR/TB",
        "price": 8.50,
        "source": "https://www.oracle.com/cloud/price-list/"
    })

    return records
