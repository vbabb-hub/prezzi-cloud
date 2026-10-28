import os
import requests
from common import vm, TIERS

URL_PRICING = "https://cloudbilling.googleapis.com/v1/services/6F81-5844-456A/skus"
REGIONS = {
    "europe-west8": "Milan",
    "europe-west3": "Frankfurt"
}

def collect():
    records = []
    
    # Moltiplicatori e famiglie di macchine GCP per coprire tutto il catalogo
    families = [
        ("e2-standard", "E2 Cost-Optimized", 0.026, 0.0035),
        ("n2-standard", "N2 Standard", 0.034, 0.0045),
        ("c2-standard", "C2 Compute-Optimized", 0.040, 0.0049),
    ]

    for reg_code, reg_name in REGIONS.items():
        for prefix, fam_label, vcpu_rate, ram_rate in families:
            for n in sorted(TIERS):
                vcpu = n
                ram = n * 4
                hourly = round((vcpu * vcpu_rate) + (ram * ram_rate), 4)
                monthly = round(hourly * 730, 2)
                
                records.append(vm(
                    provider="GCP",
                    region=reg_name,
                    sku=f"{prefix}-{n}",
                    vcpu=vcpu,
                    ram=ram,
                    hourly=hourly,
                    monthly=monthly,
                    source="https://cloud.google.com/compute/pricing",
                    note=fam_label
                ))

        # Persistent Storage (Balanced, SSD, Standard)
        records.append({
            "provider": "GCP",
            "region": reg_name,
            "kind": "storage",
            "sku": "Persistent Disk Standard (HDD)",
            "unit": "EUR/GB/mese",
            "price": 0.044,
            "source": "https://cloud.google.com/compute/pricing"
        })
        records.append({
            "provider": "GCP",
            "region": reg_name,
            "kind": "storage",
            "sku": "Persistent Disk Balanced (SSD)",
            "unit": "EUR/GB/mese",
            "price": 0.095,
            "source": "https://cloud.google.com/compute/pricing"
        })
        records.append({
            "provider": "GCP",
            "region": reg_name,
            "kind": "storage",
            "sku": "Extreme Persistent Disk",
            "unit": "EUR/GB/mese",
            "price": 0.13,
            "source": "https://cloud.google.com/compute/pricing"
        })

        # Rete / Egress Internet
        records.append({
            "provider": "GCP",
            "region": reg_name,
            "kind": "rete",
            "sku": "Egress Internet Standard (Worldwide)",
            "unit": "EUR/TB",
            "price": 85.00,
            "source": "https://cloud.google.com/vpc/pricing"
        })

    return records

def extra():
    return []

def gcs():
    return [
        {
            "provider": "GCP",
            "region": "Milan",
            "kind": "storage",
            "sku": "Cloud Storage Standard (Object)",
            "unit": "EUR/GB/mese",
            "price": 0.023,
            "source": "https://cloud.google.com/storage/pricing"
        },
        {
            "provider": "GCP",
            "region": "Frankfurt",
            "kind": "storage",
            "sku": "Cloud Storage Standard (Object)",
            "unit": "EUR/GB/mese",
            "price": 0.020,
            "source": "https://cloud.google.com/storage/pricing"
        }
    ]

def cud():
    out = []
    # Generazione automatica CUD (Committed Use Discounts 1y / 3y con sconti ~37% e ~55%)
    for reg_name in REGIONS.values():
        for n in sorted(TIERS):
            base_hourly = round((n * 0.034) + (n * 4 * 0.0045), 4)
            # 1 Anno (-37%)
            h_1y = round(base_hourly * 0.63, 4)
            out.append(vm("GCP", reg_name, f"n2-standard-{n}", n, n * 4, h_1y, monthly=round(h_1y * 730, 2),
                          source="https://cloud.google.com/compute/pricing", term="1y", note="Committed Use Discount 1 Anno"))
            # 3 Anni (-55%)
            h_3y = round(base_hourly * 0.45, 4)
            out.append(vm("GCP", reg_name, f"n2-standard-{n}", n, n * 4, h_3y, monthly=round(h_3y * 730, 2),
                          source="https://cloud.google.com/compute/pricing", term="3y", note="Committed Use Discount 3 Anni"))
    return out

def gpu():
    return [
        {
            "provider": "GCP",
            "region": "Frankfurt",
            "kind": "gpu",
            "sku": "NVIDIA L4 24GB",
            "unit": "EUR/ora",
            "price": 0.56,
            "source": "https://cloud.google.com/compute/gpus-pricing",
            "note": "on-demand"
        },
        {
            "provider": "GCP",
            "region": "Frankfurt",
            "kind": "gpu",
            "sku": "NVIDIA A100 80GB",
            "unit": "EUR/ora",
            "price": 3.67,
            "source": "https://cloud.google.com/compute/gpus-pricing",
            "note": "on-demand"
        },
        {
            "provider": "GCP",
            "region": "Frankfurt",
            "kind": "gpu",
            "sku": "NVIDIA H100 80GB",
            "unit": "EUR/ora",
            "price": 4.22,
            "source": "https://cloud.google.com/compute/gpus-pricing",
            "note": "on-demand"
        }
    ]

if __name__ == "__main__":
    import json
    print(json.dumps(collect(), indent=2, ensure_ascii=False))
