from common import get, vm, usd_eur, TIERS

URL = "https://api.linode.com/v4/linode/types?page_size=500"


def collect():
    fx, out = usd_eur(), []
    for t in get(URL).json()["data"]:
        if t.get("class") not in ("standard", "dedicated", "highmem") or t["vcpus"] not in TIERS:
            continue
        out.append(vm("Akamai Linode", "globale", t["id"].replace("g6-", ""), t["vcpus"], t["memory"] / 1024,
                      t["price"]["hourly"] * fx, monthly=t["price"]["monthly"] * fx, source=URL,
                      note="include disco e traffico" + (", core dedicati" if t["class"] == "dedicated" else "")))
    return out
