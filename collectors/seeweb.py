"""Seeweb: listino pubblico (seeweb.it), prezzi orari Linux. Mese = ore x 730.
Tabella locale con i prezzi letti dalle pagine ufficiali il VERIFIED; check_page() controlla a ogni run che la pagina li
riporti ancora. IVA da verificare. Impegno "1 anno" = prezzo orario a 12 mesi. Voci non verificate: vedi TODO.md."""
from common import vm, check_page

URL_SHARED = "https://www.seeweb.it/en/products/cloud-server-shared-cpu"
URL_HM = "https://www.seeweb.it/en/products/cloud-server-high-memory"
URL_GPU = "https://www.seeweb.it/en/products/cloud-server-gpu"
VERIFIED = "2026-11-02"
REGION = "Italia (Milano, Frosinone)"
WARNINGS = []

# (codice, vCPU, RAM GB, disco GB, EUR/h on-demand, 3 mesi, 6 mesi, 12 mesi)
SHARED = [
    ("1G", 1, 1, 20, 0.019, 0.017, 0.016, 0.015),
    ("2G", 2, 2, 40, 0.032, 0.029, 0.027, 0.026),
    ("4G", 4, 4, 80, 0.048, 0.043, 0.041, 0.038),
    ("8G", 4, 8, 160, 0.063, 0.057, 0.054, 0.050),
    ("16G", 8, 16, 320, 0.127, 0.114, 0.108, 0.102),
    ("32G", 16, 32, 500, 0.310, 0.279, 0.264, 0.248),
    ("64G", 16, 64, 1000, 0.630, 0.567, 0.536, 0.504),
]
HIGH_MEMORY = [
    ("ECS1HM", 8, 128, 400, 0.434, 0.391, 0.369, 0.347),
    ("ECS2HM", 16, 256, 800, 0.719, 0.647, 0.611, 0.575),
    ("ECS3HM", 32, 512, 1500, 1.338, 1.204, 1.137, 1.070),
    ("ECS4HM", 32, 1024, 1500, 2.537, 2.283, 2.156, 2.030),
]
GPUS = [("NVIDIA H100 80GB", 1.89, 1.80, 1.70, 1.61), ("NVIDIA A100 80GB", 0.99, 0.94, 0.89, 0.84),
        ("NVIDIA L40S 48GB", 0.85, 0.81, 0.77, 0.72), ("NVIDIA L4 24GB", 0.38, 0.36, 0.34, 0.32)]


def _vm_rows(rows, prefix, url):
    out = []
    for code, v, ram, disk, od, m3, m6, m12 in rows:
        sku = f"{prefix} {code}"
        base = f"incl. {disk} GB SSD e 10 TB di traffico; verificato {VERIFIED}"
        out.append(vm("Seeweb", REGION, sku, v, ram, od, monthly=round(od * 730, 2), source=url, term="On-demand", note=base))
        out.append(vm("Seeweb", REGION, sku, v, ram, m12, monthly=round(m12 * 730, 2), source=url, term="Impegno 1 anno",
                      note=f"impegno 12 mesi (3 mesi: {m3} EUR/h; 6 mesi: {m6} EUR/h); {base}"))
    return out


def collect():
    WARNINGS.clear()
    records = _vm_rows(SHARED, "Cloud Shared CPU", URL_SHARED) + _vm_rows(HIGH_MEMORY, "Cloud High Memory", URL_HM)
    for model, od, m3, m6, m12 in GPUS:
        for term, price, note in (("On-demand", od, "on-demand"), ("Impegno 1 anno", m12, f"impegno 12 mesi (3 mesi: {m3}; 6 mesi: {m6} EUR/h)")):
            records.append(dict(provider="Seeweb", region=REGION, kind="gpu", sku=model, unit="EUR/ora", price=price, term=term,
                                source=URL_GPU, note=f"{note}; 1 GPU; verificato {VERIFIED}"))
    for url, vals, dec in ((URL_SHARED, [r[4] for r in SHARED], 3), (URL_HM, [r[4] for r in HIGH_MEMORY], 3), (URL_GPU, [g[1] for g in GPUS], 2)):
        w = check_page(url, vals, decimals=dec)
        if w:
            WARNINGS.append(w)
    return records
