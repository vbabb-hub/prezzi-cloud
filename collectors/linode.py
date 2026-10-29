from common import get, vm, usd_eur, TIERS

URL = "https://api.linode.com/v4/linode/types?page_size=500"

def collect():
    fx, out = usd_eur(), []
    data = get(URL).json().get("data", [])
    for t in data:
        if t.get("class") not in ("standard", "dedicated", "highmem") or t["vcpus"] not in TIERS:
            continue
        
        price_info = t.get("price") or {}
        hourly_val = price_info.get("hourly")
        monthly_val = price_info.get("monthly")
        
        # Salta i record senza prezzi validi o uguali a zero
        if hourly_val is None or monthly_val is None or hourly_val <= 0 or monthly_val <= 0:
            continue
            
        hourly = hourly_val * fx
        monthly = monthly_val * fx
        
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
