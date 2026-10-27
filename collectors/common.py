import re
import requests

class Skip(Exception):
    """Fonte saltata di proposito (per esempio secret mancante): non è un errore."""

HOURS = 730
TIERS = {2, 4, 8, 16}  # vCPU considerate nel confronto

def sanitize(text):
    """Maschera automaticamente chiavi API, token e credenziali nei log e messaggi di errore."""
    if not isinstance(text, str):
        text = str(text)
    # Maschera chiavi Google (es. AIza...) e token generici lunghi o parametri key=
    text = re.sub(r'AIza[0-9A-Za-z\-_]{35}', 'AIza***[MASCHERATO]', text)
    text = re.sub(r'(key|token|secret|password)=([^\s&]+)', r'\1=***[MASCHERATO]', text, flags=re.IGNORECASE)
    return text

def get(url, **kw):
    try:
        r = requests.get(url, timeout=180, **kw)
        r.raise_for_status()
        return r
    except Exception as e:
        # Pulisce l'eccezione da eventuali chiavi esposte nell'URL
        raise RuntimeError(sanitize(str(e)))

def usd_eur():
    try:
        return float(get("https://api.frankfurter.app/latest?from=USD&to=EUR").json()["rates"]["EUR"])
    except Exception:
        return float(get("https://open.er-api.com/v6/latest/USD").json()["rates"]["EUR"])

def vm(provider, region, sku, vcpu, ram, hourly, monthly=None, source="", term=None, note=None):
    r = dict(provider=provider, region=region, kind="compute", sku=sku, vcpu=vcpu, ram_gb=ram,
                unit="EUR/mese", price=round(monthly if monthly is not None else hourly * HOURS, 4),
                price_hour=round(hourly, 6), source=source)
    if term:
        r["term"] = term
    if note:
        r["note"] = note
    return r
