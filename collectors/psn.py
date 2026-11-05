"""Polo Strategico Nazionale (PSN): listino ufficiale "Industry Standard", validità dal 30/04/2026, canone ANNUALE in EUR (PA italiane).
Solo IaaS Shared (VM e Pool, con e senza HA) e risorse aggiuntive per pool, prezzi letti il VERIFIED. Il PDF ha le colonne di prezzo
separate dalle etichette: i valori sono stati abbinati per posizione e confermati con altre versioni del listino (gennaio, aprile 2026);
5 voci dipendono solo dalla posizione (vedi TODO.md). Sistema operativo escluso; le VM includono 100 GB di storage; over-commit 1:2.
Il listino PSN cambia spesso: la tabella va riletta a ogni nuova versione. Non è un listino pubblico: è il prezzo di partenza della convenzione."""
from common import vm

URL = "https://www.polostrategiconazionale.it/app/uploads/2026/04/Listino-Polo-Strategico-Nazionale_v30_04_2026.pdf"
PROVIDER, REGION = "Polo Strategico Nazionale", "Italia (Region PSN)"
VERSION, VALID_FROM, VERIFIED = "v30/04/2026", "30/04/2026", "2026-11-04"
WARNINGS = []

# (elemento, vCPU, RAM GB, storage GB, canone annuo EUR senza HA, canone annuo EUR con HA)
IAAS_SHARED = [("VM Small", 2, 4, 100, 302.3593007, 451.3381970), ("VM Medium", 4, 8, 100, 592.9471102, 872.2825408),
               ("VM Large", 8, 16, 100, 1101.7024323, 1610.7136614), ("VM X-Large", 16, 32, 100, 3436.3094778, 5006.7225968),
               ("Pool Small", 8, 32, None, 1032.3113612, 1572.6820272), ("Pool Medium", 16, 64, None, 1875.4929892, 2875.1787214),
               ("Pool Large", 32, 128, None, 3315.8057605, 4963.8025369), ("Pool XLarge", 64, 256, None, 7400.3265713, 11126.6303936)]
EXTRA = [("1 vCPU aggiuntiva", "EUR/mese per vCPU", 46.5571998, 66.6614452), ("1 GB RAM aggiuntivo", "EUR/mese per GB", 23.8076590, 33.8597817)]


def collect():
    WARNINGS.clear()
    out = []
    for name, v, ram, disk, plain, ha in IAAS_SHARED:
        for label, annual in (("IaaS Shared", plain), ("IaaS Shared (HA)", ha)):
            note = (f"canone annuale {annual:,.2f} EUR; Industry Standard, listino di partenza {VERSION}; "
                    + (f"{disk} GB di storage inclusi; " if disk else "pool di risorse; ") + "SO escluso")
            out.append(vm(PROVIDER, REGION, f"{label} {name}", v, ram, annual / 12 / 730, monthly=round(annual / 12, 2), source=URL,
                          term="Impegno 1 anno", note=note))
    for name, unit, plain, ha in EXTRA:
        for label, annual in (("IaaS Shared", plain), ("IaaS Shared (HA)", ha)):
            out.append(dict(provider=PROVIDER, region=REGION, kind="compute", sku=f"{label} Pool: {name}", unit=unit, price=round(annual / 12, 2),
                            term="Impegno 1 anno", source=URL, note=f"canone annuale {annual:.2f} EUR; Industry Standard {VERSION}"))
    return out
