"""STACKIT: listino ufficiale (PDF "STACKIT price list", versione 1.0.44), prezzi netti in EUR, regione EU01 (Germany South),
zona singola (le varianti "-m" Metro costano il doppio e non sono incluse). Tabella locale letta dal listino il VERIFIED;
mese = ore x 730 (il listino proietta su 720 ore: indicato nelle note). Server senza storage. Nessun prezzo stimato.
Non incluso: traffico in uscita (non presente nel listino), database e servizi gestiti: vedi TODO.md."""
from common import vm, check_page

WARNINGS = []

URL = "https://stackit.com/en/asset/download/37788/file/STACKIT_price_list.pdf"
URL_GPU = "https://stackit.com/en/products/compute-engine/stackit-compute-engine-gpu"
VERIFIED = "2026-11-02"
REGION = "EU01 (Germania sud)"

# famiglia: (descrizione, {vCPU: (RAM GB, EUR/ora)})
FAMILIES = {
    "g1": ("General Purpose Intel (gen. 1)", {2: (8, 0.07582266667), 4: (16, 0.15164533333), 8: (32, 0.30329066667), 16: (64, 0.58130711111)}),
    "g2i": ("General Purpose Intel (gen. 2)", {2: (8, 0.10229251676), 4: (16, 0.20458503352), 8: (32, 0.40916500000), 16: (64, 0.81833000000)}),
    "g3i": ("General Purpose Intel (gen. 3)", {2: (8, 0.10307512300), 4: (16, 0.20613855300), 8: (32, 0.41228880000), 16: (59, 0.82457760000)}),
    "g2a": ("General Purpose AMD", {2: (8, 0.11853346800), 4: (16, 0.23706693700), 8: (32, 0.47412218100), 16: (60, 0.94824436200)}),
    "c3i": ("Compute Optimized Intel", {2: (4, 0.08693857500), 4: (8, 0.17387715100), 8: (16, 0.34775430100), 16: (32, 0.69550860300)}),
    "m2i": ("Memory Optimized Intel (gen. 2)", {2: (16, 0.13518500000), 4: (32, 0.27037000000), 8: (64, 0.54081608860), 16: (120, 1.08163217721)}),
    "m3i": ("Memory Optimized Intel (gen. 3)", {2: (16, 0.13623689900), 4: (32, 0.27247379700), 8: (59, 0.54493590100), 16: (118, 1.08987180300)}),
}
# (EUR/GB/ora, nome, unità)
STORAGE = [
    (0.00009076380, "Block Storage Premium Capacity (block)"),
    (0.00003697772, "Object Storage Premium (object)"),
    (0.00031135735, "File Storage Standard (NFS)"),
    (0.00050547002, "File Storage Premium (NFS)"),
    (0.00089765684, "File Storage Ultra (NFS)"),
]
# (tipo macchina, vCPU, n. GPU, modello, EUR/ora istanza intera)
GPUS = [
    ("n1.14d.g1", 14, 1, "NVIDIA A100 80GB", 2.65808333333), ("n1.28d.g2", 28, 2, "NVIDIA A100 80GB", 5.31616666667),
    ("n1.56d.g4", 56, 4, "NVIDIA A100 80GB", 16.33806944444),
    ("n2.14d.g1", 14, 1, "NVIDIA L40S 48GB", 1.74290277778), ("n2.28d.g2", 28, 2, "NVIDIA L40S 48GB", 3.48580555556),
    ("n2.56d.g4", 56, 4, "NVIDIA L40S 48GB", 6.97161111111),
    ("n3.14d.g1", 14, 1, "NVIDIA H100 NVL 94GB", 8.04134722222), ("n3.28d.g2", 28, 2, "NVIDIA H100 NVL 94GB", 16.08269444444),
    ("n3.56d.g4", 56, 4, "NVIDIA H100 NVL 94GB", 32.16540277778),
    ("n3.104d.g8", 104, 8, "NVIDIA H100 80GB", 64.33080555556),
]


def collect():
    WARNINGS.clear()
    out = []
    for fam, (label, tiers) in FAMILIES.items():
        for n, (ram, h) in tiers.items():
            out.append(vm("STACKIT", REGION, f"{fam}.{n}", n, ram, h, monthly=round(h * 730, 2), source=URL, term="On-demand",
                          note=f"{label}; senza storage; listino su 720 h: {h * 720:.2f} EUR/mese; verificato {VERIFIED}"))
    for h, sku in STORAGE:
        out.append(dict(provider="STACKIT", region=REGION, kind="storage", sku=sku, unit="EUR/GB/mese", price=round(h * 730, 5),
                        term="On-demand", source=URL, note=f"listino su 720 h: {h * 720:.4f}; verificato {VERIFIED}"))
    for flavor, vcpu, n, model, h in GPUS:
        out.append(dict(provider="STACKIT", region=REGION, kind="gpu", sku=f"{flavor} ({n}x {model})", unit="EUR/ora",
                        price=round(h / n, 4), term="On-demand", source=URL_GPU, vcpu=vcpu,
                        note=f"prezzo per GPU; istanza intera {h:.2f} EUR/ora, {vcpu} vCPU; verificato {VERIFIED}"))
    w = check_page(URL_GPU, [g[4] for g in GPUS], decimals=11)
    if w:
        WARNINGS.append(w)
    return out
