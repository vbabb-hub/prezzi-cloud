from common import get, vm, usd_eur, TIERS

URL = "https://api.linode.com/v4/linode/types?page_size=500"

def collect():
    fx, out = usd_eur(), []
    for t in get(URL).json()["data"]:
        if t.get("class") not in ("standard", "dedicated", "highmem") or t["vcpus"] not in TIERS:
            continue
        
        # Gestione sicura del prezzo mensile con fallback se è None
        price_info = t.get("price", {})
        hourly_val = price_info.get("hourly")
        monthly_val = price_info.get("monthly")
        
        hourly = hourly_val * fx if hourly_val is not None else 0.0
        monthly = monthly_val * fx if monthly_val is not None else 0.0
        
        out.append(vm(
            "Akamai Linode", 
            "globale", 
            t["id"].replace("g6-", ""), 
            t["vcpus"], 
            t["memory"] / 1024,
            hourly, 
            monthly=monthly, 
            source=URL,
            note="include disco e traffico" + (", core dedicati" if t["class"] == "dedicated" else "")
        ))
    
    out.append({
        "provider": "Akamai Linode",
        "region": "globale",
        "kind": "rete",
        "sku": "Traffico extra (oltre bundle)",
        "unit": "EUR/TB",
        "price": round(10.0 * fx, 3),
        "source": URL
    })
    return out

if __name__ == "__main__":
    import json
    print(json.dumps(collect(), indent=2, ensure_ascii=False))
