import os
import re
import requests

class Skip(Exception):
    """Fonte saltata di proposito (per esempio secret mancante): non è un errore."""

HOURS = 730
TIERS = {2, 4, 8, 16}  # vCPU considerate nel confronto

_SECRET_ENV = ("GCP_API_KEY", "HCLOUD_TOKEN")


def sanitize(text):
    """Maschera chiavi API, token e credenziali in log, errori e file pubblicati (status.json)."""
    if not isinstance(text, str):
        text = str(text)
    for name in _SECRET_ENV:                       # il valore esatto dei secret, ovunque compaia
        v = os.environ.get(name)
        if v and len(v) >= 8:
            text = text.replace(v, "***")
    text = re.sub(r"AIza[0-9A-Za-z\-_]{20,}", "AIza***", text)
    text = re.sub(r"(?i)\bbearer\s+[A-Za-z0-9._\-]{16,}", "Bearer ***", text)
    return re.sub(r"(?i)(key|token|secret|password|apikey|api_key|authorization)=([^\s&'\"]+)", r"\1=***", text)


def get(url, **kw):
    try:
        r = requests.get(url, timeout=180, **kw)
        r.raise_for_status()
        return r
    except Exception as e:
        # from None: l'eccezione originale (con l'URL e la chiave) non resta nel traceback
        raise RuntimeError(sanitize(str(e))) from None


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


def check_page(url, values, decimals=2, min_ratio=0.8):
    """Controlla online che il listino ufficiale riporti ancora i prezzi della tabella locale.
    Restituisce un avviso (stringa) se meno dell'80% dei prezzi viene ritrovato, altrimenti None."""
    try:
        text = get(url, headers={"User-Agent": "Mozilla/5.0"}).text
    except Exception as e:
        return f"verifica online non riuscita ({sanitize(str(e))[:80]})"
    found = 0
    for v in values:
        s = f"{v:.{decimals}f}"
        for cand in (s, s.replace(".", ",")):
            if re.search(rf"(?<![\d.,]){re.escape(cand)}(?!\d)", text):
                found += 1
                break
    if values and found / len(values) < min_ratio:
        return f"listino online cambiato? ritrovati {found}/{len(values)} prezzi in {url}"
    return None
