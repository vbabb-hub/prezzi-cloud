import requests
import re

class Skip(Exception):
    """Fonte saltata di proposito (per esempio secret mancante): non è un errore."""


HOURS = 730
TIERS = {2, 4, 8, 16}  # vCPU considerate nel confronto


def sanitize_url(url):
    """Nasconde la chiave API se presente nell'URL."""
    if not url:
        return url
    return re.sub(r'key=AIzaSy[A-Za-z0-9\-_]{33}', 'key=***', url)


def get(url, **kw):
    try:
        r = requests.get(url, timeout=180, **kw)
        r.raise_for_status()
        return r
    except requests.exceptions.HTTPError as e:
        # Pulisce l'URL dell'eccezione da eventuali chiavi esposte
        safe_url = sanitize_url(e.request.url if e.request else url)
        raise requests.exceptions.HTTPError(
            f"HTTP Error for {safe_url}: {e.response.status_code} {e.response.reason}",
            response=e.response,
            request=e.request
        ) from None
