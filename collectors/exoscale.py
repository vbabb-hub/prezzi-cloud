"""Exoscale: listino pubblico (exoscale.com/pricing), prezzi in EUR uguali in tutte le zone. Tabella locale con i valori letti il
VERIFIED. Instance Standard (senza storage locale: va aggiunto), storage a blocchi, Object Storage Standard e traffico in uscita.
Il listino ufficiale è una pagina dinamica (non si può controllare in automatico): i prezzi delle istanze e dello storage a blocchi
vengono da fonti secondarie coerenti tra loro, solo l'Object Storage da pagina ufficiale. Mese = ore x 730."""
from common import vm

URL = "https://www.exoscale.com/pricing/"
URL_SOS = "https://www.exoscale.com/object-storage/classes/"
VERIFIED = "2026-11-03"
REGION = "AT, CH, DE, BG (stessi prezzi)"
WARNINGS = []

# (nome, vCPU, RAM GB, EUR/ora)
STANDARD = [("Medium", 2, 4, 0.04666), ("Large", 4, 8, 0.09333), ("Extra-large", 4, 16, 0.18667), ("Huge", 8, 32, 0.37334)]


def collect():
    WARNINGS.clear()
    out = [vm("Exoscale", REGION, f"Standard {name}", v, ram, h, monthly=round(h * 730, 2), source=URL, term="On-demand",
              note=f"senza storage locale (0,00014 EUR/GiB/ora, min 10 GB); fonte secondaria, verificare; {VERIFIED}")
           for name, v, ram, h in STANDARD]
    out.append(dict(provider="Exoscale", region=REGION, kind="storage", sku="Block Storage (block)", unit="EUR/GB/mese", price=0.1008,
                    term="On-demand", source=URL, note=f"0,00014 EUR/GiB/ora x 720; fonte secondaria, verificare; {VERIFIED}"))
    out.append(dict(provider="Exoscale", region=REGION, kind="storage", sku="Object Storage Standard (object)", unit="EUR/GB/mese", price=0.0184,
                    term="On-demand", source=URL_SOS, note=f"pagina ufficiale; {VERIFIED}"))
    out.append(dict(provider="Exoscale", region=REGION, kind="rete", sku="Traffico in uscita oltre la quota", unit="EUR/TB", price=20.0,
                    term="On-demand", source=URL, note=f"0,02 EUR/GB; 1 TiB al mese incluso per istanza; fonte secondaria; {VERIFIED}"))
    return out
