from common import vm

def collect():
    records = []
    # OCI Standard E5 Flex Tiers mappati sui tier di vCPU della PWA (2, 4, 8, 16 vCPU)
    # 1 OCPU = 2 vCPU (con hyperthreading standard su AMD EPYC)
    # Prezzi di listino standard OCI in EUR (circa 0.0138 € / OCPU-ora e 0.0018 € / GB RAM-ora)
    tiers = [
        # Rapporto 4 GB di RAM per vCPU (copre il filtro principale della matrice)
        (1, 2, 8, "VM.Standard.E5.Flex (2 vCPU / 8GB)"),
        (2, 4, 16, "VM.Standard.E5.Flex (4 vCPU / 16GB)"),
        (4, 8, 32, "VM.Standard.E5.Flex (8 vCPU / 32GB)"),
        (8, 16, 64, "VM.Standard.E5.Flex (16 vCPU / 64GB)"),
        
        # Rapporto 2 GB di RAM per vCPU (copre ratio alternativi)
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
    
