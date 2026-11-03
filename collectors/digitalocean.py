"""DigitalOcean: listino pubblico (digitalocean.com/pricing/droplets), prezzi in USD convertiti in EUR col cambio del giorno
(DigitalOcean fattura in dollari). Tabella locale letta dal listino il VERIFIED; a ogni run check_page() controlla che la
pagina riporti ancora i prezzi. Mese = prezzo del piano (tetto mensile, 672 ore). Solo Droplet: le altre voci
(GPU, storage, traffico, Kubernetes, database) sono ancora da raccogliere, vedi TODO.md."""
from common import vm, usd_eur, check_page

URL = "https://www.digitalocean.com/pricing/droplets"
VERIFIED = "2026-11-02"
WARNINGS = []

# (famiglia, slug, vCPU, RAM GiB, USD/mese, nota)
DROPLETS = [
    ("Basic", "s-2vcpu-4gb", 2, 4, 24.0, "vCPU condivise"),
    ("Basic", "s-4vcpu-8gb", 4, 8, 48.0, "vCPU condivise"),
    ("Basic", "s-8vcpu-16gb", 8, 16, 96.0, "vCPU condivise"),
    ("General Purpose", "g-2vcpu-8gb", 2, 8, 63.0, "vCPU dedicate"),
    ("General Purpose", "g-4vcpu-16gb", 4, 16, 126.0, "vCPU dedicate; fonte secondaria, verificare"),
    ("General Purpose", "g-8vcpu-32gb", 8, 32, 252.0, "vCPU dedicate; fonte secondaria, verificare"),
    ("CPU-Optimized", "c-2", 2, 4, 42.0, "vCPU dedicate"),
    ("Memory-Optimized", "m-2vcpu-16gb", 2, 16, 84.0, "vCPU dedicate"),
]


def collect():
    WARNINGS.clear()
    fx, out = usd_eur(), []
    for fam, slug, v, ram, usd, note in DROPLETS:
        monthly = round(usd * fx, 2)
        out.append(vm("DigitalOcean", "globale", f"{fam} {slug}", v, ram, usd * fx / 672, monthly=monthly, source=URL, term="On-demand",
                      note=f"{note}; {usd:.0f} USD/mese al cambio del giorno; verificato {VERIFIED}"))
    w = check_page(URL, [24, 48, 96, 63, 42, 84])
    if w:
        WARNINGS.append(w)
    return out
