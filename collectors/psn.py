"""Polo Strategico Nazionale (PSN): listino ufficiale "Industry Standard", validità dal 30/04/2026, canone ANNUALE in EUR (PA italiane).
Dal PDF si leggono le etichette e le colonne dei prezzi separate: i valori sono stati abbinati per posizione. Controllo di coerenza:
tutte le voci IaaS Shared, Blade e CaaS Licensed Medium hanno un rapporto costante di +0,89% rispetto alla release di maggio 2025 (stesso
abbinamento), e le voci "conf." hanno anche un riscontro diretto nel testo. Le voci "pos." sono abbinate solo per posizione: vedi TODO.md.
Non inclusi (abbinamento non affidabile): tipologie Premium, IaaS Private a nodi, GPU H100, storage, sicurezza, backup, AI, housing.
Il listino PSN cambia spesso (2024, 2025, gennaio e aprile 2026): la tabella va riletta a ogni release. Prezzo di partenza della convenzione."""
from common import vm

URL = "https://www.polostrategiconazionale.it/app/uploads/2026/04/Listino-Polo-Strategico-Nazionale_v30_04_2026.pdf"
PROVIDER, REGION = "Polo Strategico Nazionale", "IT"
VERSION, VALID_FROM, VERIFIED = "v30/04/2026", "30/04/2026", "2026-11-05"
WARNINGS = []

# (elemento, vCPU, RAM GB, storage GB, canone annuo senza HA, canone annuo con HA; None = voce non disponibile/non abbinata)
IAAS_SHARED = [("VM Tiny", 1, 2, 100, 184.2384677, None), ("VM Small", 2, 4, 100, 302.3593007, 451.3381970), ("VM Medium", 4, 8, 100, 592.9471102, 872.2825408),
               ("VM Large", 8, 16, 100, 1101.7024323, 1610.7136614), ("VM X-Large", 16, 32, 100, 3436.3094778, 5006.7225968),
               ("Pool Small", 8, 32, None, 1032.3113612, 1572.6820272), ("Pool Medium", 16, 64, None, 1875.4929892, 2875.1787214),
               ("Pool Large", 32, 128, None, 3315.8057605, 4963.8025369), ("Pool XLarge", 64, 256, None, 7400.3265713, 11126.6303936)]
EXTRA = [("1 vCPU aggiuntiva", "EUR/mese per vCPU", 46.5571998, 66.6614452), ("1 GB RAM aggiuntivo", "EUR/mese per GB", 23.8076590, 33.8597817)]
# IaaS Private a blade (host fisico dedicato): (nome, core, RAM GB, canone annuo)
BLADE = [("Blade Medium", 24, 256, 4114.7598807), ("Blade Large", 36, 768, 5910.4649689)]
# CaaS (Kubernetes): (nome, unità, canone annuo, riscontro)
CAAS = [("CaaS Licensed Medium (host 24 core / 256 GB, Tanzu Basic)", "EUR/mese per host", 4702.1464156, "conf."),
        ("CaaS Licensed Large (host 36 core / 768 GB, Tanzu Basic)", "EUR/mese per host", 11166.8715222, "pos."),
        ("CaaS Open Source", "EUR/mese per vCPU", 470.2146415, "conf.")]
# Database PaaS (istanza, licenza inclusa), sistemi operativi e backup: abbinati solo per posizione
DBAAS = [("PaaS SQL MySQL", 1592.1672609), ("PaaS SQL PostgreSQL", 1556.2782447), ("PaaS SQL SQL Server", 4520.3847131),
         ("PaaS SQL Oracle Enterprise", 14004.8728843), ("PaaS SQL Oracle Standard", 6281.5973966), ("PaaS DB MongoDB", 3312.4009194), ("PaaS SQL MariaDB", 1000.6512806)]
LICENSES = [("Windows Server Standard (2 core)", "EUR/mese", 122.0961245), ("Red Hat Enterprise Linux per VM", "EUR/mese", 569.7819147),
            ("Red Hat Enterprise Linux per bare metal (2 socket)", "EUR/mese", 1017.4677047)]


def _r(kind, sku, unit, annual, note, v=None, ram=None):
    d = dict(provider=PROVIDER, region=REGION, kind=kind, sku=sku, unit=unit, price=round(annual / 12, 2), term="Impegno 1 anno", source=URL,
             note=f"canone annuale {annual:,.2f} EUR; Industry Standard, listino di partenza {VERSION}; {note}")
    if v:
        d["vcpu"], d["ram_gb"] = v, ram
    return d


def collect():
    WARNINGS.clear()
    out = []
    for name, v, ram, disk, plain, ha in IAAS_SHARED:
        for label, annual in (("IaaS Shared", plain), ("IaaS Shared (HA)", ha)):
            if annual:
                note = (f"{disk} GB di storage inclusi; " if disk else "pool di risorse; ") + "SO escluso; riscontrato (+0,89% su maggio 2025)"
                out.append(vm(PROVIDER, REGION, f"{label} {name}", v, ram, annual / 12 / 730, monthly=round(annual / 12, 2), source=URL, term="Impegno 1 anno",
                              note=f"canone annuale {annual:,.2f} EUR; Industry Standard, listino di partenza {VERSION}; {note}"))
    for name, unit, plain, ha in EXTRA:
        for label, annual in (("IaaS Shared", plain), ("IaaS Shared (HA)", ha)):
            out.append(_r("compute", f"{label} Pool: {name}", unit, annual, "riscontrato (+0,89% su maggio 2025)"))
    for name, core, ram, annual in BLADE:
        out.append(_r("compute", f"IaaS Private {name} (host {core} core / {ram} GB)", "EUR/mese per host", annual, "host fisico dedicato; riscontrato (+0,89% su maggio 2025)", core, ram))
    for name, unit, annual, conf in CAAS:
        out.append(_r("k8s", name, unit, annual, "riscontrato" if conf == "conf." else "abbinato per posizione, da verificare"))
    for name, annual in DBAAS:
        out.append(_r("dbaas", name, "EUR/mese", annual, "licenza inclusa; abbinato per posizione, da verificare"))
    for name, unit, annual in LICENSES:
        out.append(_r("licenza", name, unit, annual, "abbinato per posizione, da verificare"))
    return out
