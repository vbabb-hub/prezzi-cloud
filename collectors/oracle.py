from common import get, vm, usd_eur, TIERS

URL = "https://apexapps.oracle.com/pls/apex/cetools/api/v1/products/?currencyCode=EUR"


def _price(item, fx):
    for loc in item.get("currencyCodeLocalizations", []):
        for p in loc.get("prices", []):
            if p.get("model") == "PAY_AS_YOU_GO" or not p.get("model"):
                return p["value"] * (fx if loc.get("currencyCode") == "USD" else 1)
    return None


def collect():
    fx = usd_eur()
    ocpu = ram = None
    for it in get(URL).json()["items"]:
        n = it.get("displayName", "")
        if "Standard - E4" in n and "Windows" not in n:
            if "OCPU" in n:
                ocpu = _price(it, fx)
            elif "Memory" in n:
                ram = _price(it, fx)
    if not ocpu or not ram:
        raise RuntimeError("prezzi E4 Flex non trovati nel listino Oracle")
    return [vm("Oracle Cloud", "globale (Milano inclusa)", f"E4 Flex {n} vCPU", n, n * 4, (n / 2) * ocpu + n * 4 * ram, source=URL,
               note="1 OCPU = 2 vCPU; senza storage")
            for n in sorted(TIERS)]
