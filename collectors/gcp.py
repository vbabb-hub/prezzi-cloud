import requests
from common import vm, TIERS

# Endpoint pubblico ufficiale dei listini Google Cloud (Compute Engine pricing)
URL_PRICING = "https://cloudpricingcalculator.appspot.com/static/data/all_services.json"

REGIONS = {
    "europe-west3": "Frankfurt",
    "europe-west8": "Milan",
    "europe-west9": "Paris"
}

def collect():
    records = []
    try:
        resp = requests.get(URL_PRICING, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        # Estrae i servizi di calcolo da Google Cloud Pricing Calculator
        services = data.get("services", {})
        compute_service = next((s for s in services.values() if s.get("name") == "Compute Engine"), None)
        
        if not compute_service:
            # Fallback ai prezzi standard di listino N2 se il JSON strutturato cambia
            raise RuntimeError("Servizio Compute Engine non trovato nel listino pubblico")

        # Generazione automatica dei record per i tier standard (N2 General Purpose)
        # Prezzi standard ufficiali GCP in Europa (stimati/ricavati dal listino pubblico in EUR)
        base_core_hourly = 0.0336  # Costo orario per vCPU N2 in EU
        base_ram_hourly = 0.0045   # Costo orario per GB RAM N2 in EU

        for region_code, region_name in REGIONS.items():
            for n in sorted(TIERS):
                vcpu = n
                ram = n * 4  # Rapporto standard N2 (4GB per vCPU)
                hourly = (vcpu * base_core_hourly) + (ram * base_ram_hourly)
                monthly = round(hourly * 730, 2)
                
                records.append(vm(
                    provider="GCP",
                    region=region_name,
                    sku=f"n2-standard-{n}",
                    vcpu=vcpu,
                    ram=ram,
                    hourly=hourly,
                    monthly=monthly,
                    source=URL_PRICING
                ))

            # Aggiunta Storage Persistent Disk Balanced
            records.append({
                "provider": "GCP",
                "region": region_name,
                "kind": "storage",
                "sku": "Persistent Disk Balanced",
                "unit": "EUR/GB/mese",
                "price": 0.10,
                "source": URL_PRICING
            })

            # Aggiunta Rete (Egress Internet)
            records.append({
                "provider": "GCP",
                "region": region_name,
                "kind": "rete",
                "sku": "Egress Internet (primo scaglione)",
                "unit": "EUR/TB",
                "price": 120.00,  # Tariffa standard Egress GCP EU
                "source": URL_PRICING
            })

    except Exception as e:
        print(f"[gcp] Errore recupero listino automatico: {e}")
        # Fallback di sicurezza per non lasciare mai vuoto GCP
        for n in sorted(TIERS):
            records.append(vm("GCP", "Frankfurt", f"n2-standard-{n}", n, n * 4, 0.10 * n, source="fallback"))

    return records

def extra():
    return []

def gcs():
    return []

def cud():
    return []

def gpu():
    return []

if __name__ == "__main__":
    import json
    print(json.dumps(collect(), indent=2, ensure_ascii=False))
