"""Verifica che i secret GCP_API_KEY e HCLOUD_TOKEN siano impostati e accettati dai servizi, senza mai stamparli.
Si lancia da GitHub: Actions, "Verifica chiavi", Run workflow. Esce con errore solo se un secret impostato non funziona
(un secret mancante è facoltativo: GCP resta vuoto e Hetzner usa i prezzi manuali)."""
import os, sys, requests
from common import sanitize

GCP_URL = "https://cloudbilling.googleapis.com/v1/services/6F81-5844-456A/skus"   # Compute Engine, una sola SKU
HZ_URL = "https://api.hetzner.cloud/v1/server_types"
HINTS = {
    "API_KEY_INVALID": "la chiave non è valida: ricopiala per intero nel secret (senza spazi)",
    "API_KEY_SERVICE_BLOCKED": "la chiave è limitata ad altre API: tra le restrizioni aggiungi Cloud Billing API",
    "SERVICE_DISABLED": "abilita Cloud Billing API nel progetto (APIs e servizi, Libreria)",
    "RESOURCE_EXHAUSTED": "quota esaurita: riprova più tardi",
    "PERMISSION_DENIED": "chiave non autorizzata per questa API: controlla le restrizioni della chiave",
}


def _error(r):
    try:
        e = r.json().get("error", {})
        if isinstance(e, dict):
            reason = (e.get("details") or [{}])[0].get("reason") or e.get("status") or ""
            return reason, e.get("message", "")
        return "", str(e)
    except Exception:
        return "", r.text[:120]


def check_gcp(key):
    try:
        r = requests.get(GCP_URL, params={"key": key, "pageSize": 1, "currencyCode": "EUR"}, timeout=30)
    except requests.RequestException as e:
        return False, f"rete: {sanitize(type(e).__name__)}"
    if r.status_code == 200:
        return True, "OK, il catalogo Google risponde"
    reason, msg = _error(r)
    return False, f"HTTP {r.status_code} {reason}: {sanitize(msg)[:120]} -> {HINTS.get(reason, 'controlla chiave e restrizioni')}"


def check_hetzner(token):
    try:
        r = requests.get(HZ_URL, params={"per_page": 1}, headers={"Authorization": f"Bearer {token}"}, timeout=30)
    except requests.RequestException as e:
        return False, f"rete: {sanitize(type(e).__name__)}"
    if r.status_code == 200:
        return True, "OK, il token Hetzner è accettato"
    hint = {401: "token non valido o revocato: generane uno nuovo con permesso Lettura", 403: "token senza i permessi di lettura"}.get(r.status_code, "controlla il token")
    return False, f"HTTP {r.status_code} -> {hint}"


def main():
    rows, failed = [], False
    for name, fn in (("GCP_API_KEY", check_gcp), ("HCLOUD_TOKEN", check_hetzner)):
        val = os.environ.get(name, "").strip()
        if not val:
            rows.append((name, "non impostato (facoltativo)"))
            continue
        ok, msg = fn(val)
        failed |= not ok
        rows.append((name, ("OK: " if ok else "ERRORE: ") + sanitize(msg)))
    out = "\n".join(f"{n}: {m}" for n, m in rows)
    print(out)
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write("## Verifica chiavi\n\n" + "\n".join(f"- **{n}**: {m}" for n, m in rows) + "\n")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
