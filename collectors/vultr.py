from common import get, vm, usd_eur, TIERS

URL = "https://api.vultr.com/v2/plans?type=all&per_page=500"
NAMES = {"vc2": "Cloud Compute", "vhf": "High Frequency", "vdc": "Dedicated CPU", "voc": "Optimized"}


def collect():
    fx, out = usd_eur(), []
    for p in get(URL).json()["plans"]:
        kind = p["id"].split("-")[0]
        if kind not in NAMES or p["vcpu_count"] not in TIERS or not p.get("monthly_cost"):
            continue
        out.append(vm("Vultr", "globale", p["id"], p["vcpu_count"], p["ram"] / 1024, p["monthly_cost"] * fx / 730,
                      monthly=p["monthly_cost"] * fx, source=URL, note=f"{NAMES[kind]}, include disco e traffico"))
    return out
