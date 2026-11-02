"""Aruba Cloud: listino pubblico (cloud.it/prezzi), IVA esclusa.
Tabella locale con i prezzi letti dalle pagine ufficiali il VERIFIED; a ogni run check_page() controlla che la pagina
online li riporti ancora e, se no, lascia un avviso in status.json. Voci non verificate: vedi TODO.md."""
from common import vm, check_page

URL_SERVER = "https://www.cloud.it/prezzi/public-cloud/openstack-cloud-server"
URL_BLOCK = "https://www.cloud.it/cloud-storage/cloud-block-storage"
URL_GPU = "https://www.cloud.it/prezzi/bare-metale-vps/gpu-on-demand"
VERIFIED = "2026-10-27"
REGION = "Italia"
WARNINGS = []

# (codice, vCPU, RAM GB, NVMe GB inclusi, EUR/ora, EUR/mese, EUR/anno)
SERVERS = [
    ("PRO O2A4", 2, 4, 80, 0.029, 20.10, 234),
    ("PRO O4A8", 4, 8, 120, 0.045, 31.20, 364),
    ("PRO O8A16", 8, 16, 160, 0.080, 55.50, 647),
    ("PRO O16A32", 16, 32, 360, 0.220, 152.60, 1777),
    ("PRO O2A8R", 2, 8, 80, 0.037, 25.70, 300),
    ("PRO O4A16R", 4, 16, 120, 0.060, 41.60, 485),
    ("PRO O8A32R", 8, 32, 160, 0.110, 76.30, 889),
]
GPUS = [("NVIDIA L40S 48GB", 1979.90), ("NVIDIA GeForce RTX 4080 Super 16GB", 529.90)]  # canone mensile, server con 1 GPU
BLOCK = [("Block Storage Standard (Availability Zone)", 0.0365), ("Block Storage Standard (Regional)", 0.0584),
         ("Block Storage Performance (Availability Zone)", 0.0657), ("Block Storage Performance (Regional)", 0.0949),
         ("Disco aggiuntivo Cloud Server OpenStack", 0.146)]


def collect():
    WARNINGS.clear()
    records = []
    for code, v, ram, nvme, hourly, monthly, yearly in SERVERS:
        note = f"incl. {nvme} GB NVMe e traffico illimitato, escluso IP; verificato {VERIFIED}"
        records.append(vm("Aruba Cloud", REGION, f"OpenStack {code}", v, ram, hourly, monthly=monthly, source=URL_SERVER,
                          term="On-demand", note=note))
        records.append(vm("Aruba Cloud", REGION, f"OpenStack {code}", v, ram, yearly / 12 / 730, monthly=round(yearly / 12, 2),
                          source=URL_SERVER, term="Impegno 1 anno", note=f"prezzo annuale {yearly} EUR/anno; {note}"))
    for sku, monthly in GPUS:
        records.append(dict(provider="Aruba Cloud", region=REGION, kind="gpu", sku=sku, unit="EUR/ora", price=round(monthly / 730, 4),
                            term="On-demand", source=URL_GPU,
                            note=f"GPU on Demand: server dedicato con 1 GPU, canone {monthly:.2f} EUR/mese su 730 h; verificato {VERIFIED}"))
    for sku, price in BLOCK:
        records.append(dict(provider="Aruba Cloud", region=REGION, kind="storage", sku=sku, unit="EUR/GB/mese", price=price,
                            term="On-demand", source=URL_BLOCK if "Block" in sku else URL_SERVER, note=f"verificato {VERIFIED}"))
    records.append(dict(provider="Aruba Cloud", region=REGION, kind="rete", sku="Traffico in uscita (illimitato nei Cloud Server)",
                        unit="EUR/TB", price=0.0, term="On-demand", source=URL_SERVER, note=f"incluso nel prezzo del server; verificato {VERIFIED}"))
    for url, vals in ((URL_SERVER, [s[5] for s in SERVERS]), (URL_GPU, [GPUS[1][1]])):
        w = check_page(url, vals)
        if w:
            WARNINGS.append(w)
    return records
