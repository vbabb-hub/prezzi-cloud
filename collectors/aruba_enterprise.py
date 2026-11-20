"""Aruba Enterprise: "Listino per il Mercato Enterprise" (enterprise.aruba.it), IVA esclusa. NON è il listino pubblico di cloud.it
(quello è in aruba.py, provider "Aruba Cloud"): è il listino dei servizi con qualifica ACN per enterprise e PA, con impegni (1 anno circa -10%,
3 anni solo sui server dedicati) e SLA propri. Confronto tra i due: ARUBA_LISTINI.md.

Il listino viene aggiornato ogni mese e a ogni versione cambia il numero del documento (ARB-xxxxx-n): la vecchia versione sparisce (404).
Per questo il collector (1) prova l'ultima versione nota, (2) se non c'è più cerca in avanti la nuova, (3) legge i prezzi dal documento
per codice servizio (Cep-0002, Stp-0012...). Le tabelle sotto sono il ripiego: valori letti da ARB-11761-1 (valida dal 24/08/2026), usati
solo per le voci che il documento online non permette di leggere, con un avviso in status.json."""
import re, time, html as htmllib
import requests
from common import vm, sanitize

LAST_KNOWN = 11761                 # numero dell'ultima versione vista (ARB-11761-1)
STATIC_VERSION, STATIC_VALID = "ARB-11761-1", "24/08/2026"
BASE = "https://enterprise.aruba.it/documents/tc-files/it/arb-{}-{}_cloud_listino.aspx"
PROVIDER, REGION = "Aruba Enterprise", "IT"
SEARCH_AHEAD = 120                 # quanti numeri provare in avanti se l'ultima versione nota non esiste più
WARNINGS = []

# (codice servizio, codice taglia, vCPU, RAM GB, NVMe GB, EUR/ora, EUR/mese on-demand, EUR/mese impegno 1 anno)
CLOUD_SERVER = [
    ("Cep-0001", "O1A2", 1, 2, 20, 0.01847, 13.48, 12.13), ("Cep-0002", "O2A4", 2, 4, 80, 0.03151, 23.00, 20.70), ("Cep-0003", "O4A8", 4, 8, 120, 0.05712, 41.70, 37.53),
    ("Cep-0004", "O8A16", 8, 16, 160, 0.10442, 76.23, 68.61), ("Cep-0005", "O12A24", 12, 24, 240, 0.15564, 113.62, 102.26), ("Cep-0006", "O16A32", 16, 32, 360, 0.21078, 153.87, 138.48),
    ("Cep-0007", "O24A48", 24, 48, 480, 0.31327, 228.69, 205.82), ("Cep-0008", "O32A64", 32, 64, 480, 0.46164, 337.00, 303.30), ("Cep-0009", "O1A4R", 1, 4, 40, 0.02466, 18.00, 16.20),
    ("Cep-0010", "O2A8R", 2, 8, 80, 0.05017, 36.63, 32.96), ("Cep-0011", "O4A16R", 4, 16, 120, 0.08904, 65.00, 58.50), ("Cep-0012", "O8A32R", 8, 32, 160, 0.16301, 119.00, 107.10)]
# (codice servizio, codice taglia, S.O., vCPU, RAM GB, disco, traffico incluso TB/mese, EUR/mese)
VPS = [("Vps-0001", "O1I1", "Linux", 1, 1, "20 GB SSD", 2, 5.77), ("Vps-0002", "O1I2", "Linux", 1, 2, "40 GB SSD", 5, 7.59), ("Vps-0003", "O2A4", "Linux", 2, 4, "40 GB NVMe", 25, 9.21),
       ("Vps-0004", "O4A8", "Linux", 4, 8, "80 GB NVMe", 50, 16.97), ("Vps-0005", "O8A16", "Linux", 8, 16, "160 GB NVMe", 100, 32.50), ("Vps-0006", "O16A32", "Linux", 16, 32, "320 GB NVMe", 100, 63.56),
       ("Vps-0007", "O2A4", "Windows", 2, 4, "40 GB NVMe", 25, 38.17), ("Vps-0008", "O4A8", "Windows", 4, 8, "80 GB NVMe", 50, 74.90),
       ("Vps-0009", "O8A16", "Windows", 8, 16, "160 GB NVMe", 100, 148.36), ("Vps-0010", "O16A32", "Windows", 16, 32, "320 GB NVMe", 100, 295.28)]
# Virtual Data Center, Linux: (codice servizio, codice taglia, vCPU, RAM GB, EUR/ora, EUR/mese)
VDC = [("Cpt-0051", "O1A2", 1, 2, 0.01429, 10.43), ("Cpt-0052", "O2A4", 2, 4, 0.02771, 20.23), ("Cpt-0053", "O4A8", 4, 8, 0.05716, 41.72), ("Cpt-0054", "O8A16", 8, 16, 0.10681, 77.97),
       ("Cpt-0055", "O12A24", 12, 24, 0.16021, 116.96), ("Cpt-0056", "O16A32", 16, 32, 0.22863, 166.90), ("Cpt-0057", "O24A48", 24, 48, 0.34294, 250.35), ("Cpt-0058", "O32A64", 32, 64, 0.45726, 333.80),
       ("Cpt-0059", "O1A4", 1, 4, 0.02000, 14.60), ("Cpt-0060", "O2A8", 2, 8, 0.04001, 29.21), ("Cpt-0061", "O4A16", 4, 16, 0.08002, 58.41), ("Cpt-0062", "O8A32", 8, 32, 0.16004, 116.83),
       ("Cpt-0063", "O16A64", 16, 64, 0.35145, 256.56)]
# Kubernetes gestito: (codice servizio, nome, vCPU, RAM GB, EUR/ora, EUR/mese)
K8S = [("Cnt-0002", "general purpose K2A4", 2, 4, 0.03209, 23.42), ("Cnt-0003", "general purpose K4A8", 4, 8, 0.05893, 43.02), ("Cnt-0004", "general purpose K8A16", 8, 16, 0.10820, 78.99),
       ("Cnt-0005", "general purpose K12A24", 12, 24, 0.16089, 117.45), ("Cnt-0006", "general purpose K16A32", 16, 32, 0.21700, 158.41), ("Cnt-0007", "general purpose K24A48", 24, 48, 0.31896, 232.84),
       ("Cnt-0008", "general purpose K32A64", 32, 64, 0.41066, 299.78), ("Cnt-0009", "memory K2A8R", 2, 8, 0.04006, 29.25), ("Cnt-0010", "memory K4A16R", 4, 16, 0.07388, 53.93),
       ("Cnt-0011", "memory K8A32R", 8, 32, 0.13810, 100.81), ("Cnt-0013", "memory K16A64R", 16, 64, 0.27679, 202.06), ("Cnt-0014", "memory K32A128R", 32, 128, 0.53023, 387.07)]
# DBaaS: (codice servizio, motore, codice taglia, vCPU, RAM GB, EUR/ora, EUR/mese)
DBAAS = [("Dtb-0001", "MySQL", "O1A2", 1, 2, 0.02261, 16.51), ("Dtb-0002", "MySQL", "O2A4", 2, 4, 0.04091, 29.86), ("Dtb-0003", "MySQL", "O4A8", 4, 8, 0.07750, 56.57),
         ("Dtb-0004", "MySQL", "O8A16", 8, 16, 0.15068, 110.00), ("Dtb-0005", "MySQL", "O12A24", 12, 24, 0.22329, 163.00), ("Dtb-0006", "MySQL", "O16A32", 16, 32, 0.29628, 216.29),
         ("Dtb-0007", "MySQL", "O24A48", 24, 48, 0.44227, 322.86), ("Dtb-0008", "MySQL", "O32A64", 32, 64, 0.58826, 429.43), ("Dtb-0009", "MySQL", "O1A4", 1, 4, 0.02985, 21.79),
         ("Dtb-0010", "MySQL", "O2A8", 2, 8, 0.05540, 40.44), ("Dtb-0011", "MySQL", "O4A16", 4, 16, 0.10650, 77.74), ("Dtb-0012", "MySQL", "O8A32", 8, 32, 0.20869, 152.34),
         ("Dtb-0013", "MySQL", "O16A64", 16, 64, 0.38498, 281.04), ("Dtb-0014", "MSSQL Server Web", "O4A8", 4, 8, 0.10868, 79.34), ("Dtb-0015", "MSSQL Server Web", "O4A16", 4, 16, 0.12818, 93.57),
         ("Dtb-0016", "MSSQL Server Standard", "O4A8", 4, 8, 0.95364, 696.16), ("Dtb-0017", "MSSQL Server Standard", "O4A16", 4, 16, 0.97313, 710.39),
         ("Dtb-0018", "MSSQL Server Enterprise", "O4A8", 4, 8, 3.44781, 2516.90), ("Dtb-0022", "MSSQL Server Enterprise", "O4A16", 4, 16, 3.46731, 2531.13),
         ("Dtb-0019", "MSSQL Server Enterprise", "O8A16", 8, 16, 6.89275, 5031.71), ("Dtb-0023", "MSSQL Server Enterprise", "O8A32", 8, 32, 6.93174, 5060.17),
         ("Dtb-0020", "MSSQL Server Enterprise", "O12A24", 12, 24, 10.33769, 7546.52), ("Dtb-0021", "MSSQL Server Enterprise", "O16A32", 16, 32, 13.78263, 10061.32)]
# Server dedicati con GPU (1 GPU): (codice servizio, codice server, GPU, configurazione, EUR/mese on-demand, 1 anno, 3 anni)
GPU_SERVERS = [("Srv-0015", "AI-A108", "NVIDIA GeForce RTX 4070 Super 12GB", "Ryzen 7 7700X 8C, 64 GB DDR5, 2x NVMe 2 TB", 648.23, 583.41, 525.07),
               ("Srv-0016", "AI-A109", "NVIDIA GeForce RTX 4080 Super 16GB", "Ryzen 9 7900X 12C, 128 GB DDR5, 2x NVMe 2 TB", 1011.38, 910.24, 819.22),
               ("Srv-0017", "AI-A110", "NVIDIA L40S 48GB", "Dell R7625, 2x EPYC 9124 (32 core), 128 GB DDR5, 2x SSD 480 GB", 2942.66, 2648.40, 2383.56),
               ("Srv-0018", "AI-A110E.64", "NVIDIA L40S 48GB", "Dell R7625, 2x EPYC 9354 (64 core), 128 GB DDR5, 2x SSD 480 GB", 3077.39, 2769.65, 2492.69)]
# Storage per 100 GB (codice servizio, nome, EUR/mese per 100 GB)
BLOCK = [("Stp-0012", "Block Storage Standard (Availability Zone)", 4.38), ("Stp-0013", "Block Storage Performance (Availability Zone)", 8.03),
         ("Stp-0014", "Block Storage Standard (Regional)", 7.30), ("Stp-0015", "Block Storage Performance (Regional)", 11.68), ("Stp-0016", "Block Storage Snapshot", 4.38)]
ACN = {"cs": "IA-418 QC1", "vps": "IA-4350 QC1", "vdc": "IA-7024 QC1", "vmw": "IA-4253 QC1", "blk": "IA-4041 QC1", "obj": "IA-137 QC1",
       "k8s": "PA-4039 QC1", "db": "PA-2828 QC1", "srv": "IN-6469 AI1", "net": "IA-418 QC1"}

# ---- lettura del listino online ------------------------------------------------------------------------------------------------------
_TOK = r"(?:NA|-\s*€|\d{1,3}(?:\.\d{3})*,\d+\s*€)"
_ROW = re.compile(rf"\b(?:Ora|Mese)\s+({_TOK})\s+({_TOK})\s+({_TOK})\s+({_TOK})")
_CODE = re.compile(r"\b([A-Z][a-z]{2}-\d{4})\b")


def _num(tok):
    tok = tok.strip()
    if tok == "NA":
        return None
    return float(tok.replace("€", "").replace("-", "0").replace(".", "").replace(",", ".").strip() or 0)


def parse_listino(raw):
    """Restituisce (versione, valido dal, {codice servizio: [ora, mese, 1 anno, 3 anni]}) dal testo del documento."""
    text = htmllib.unescape(re.sub(r"<[^>]+>", " ", raw))
    text = re.sub(r"\s+", " ", text)
    m = re.search(r"v\.\s*(ARB-+\d+-\d+)\s+Valido dal\s+([0-9/]+)", text)
    ver, valid = (m.group(1).replace("--", "-"), m.group(2)) if m else (None, None)
    spots = [(x.start(), x.group(1)) for x in _CODE.finditer(text)]
    rows = {}
    for i, (pos, code) in enumerate(spots):
        seg = text[pos: spots[i + 1][0] if i + 1 < len(spots) else len(text)]
        found = _ROW.findall(seg)
        if found and code not in rows:
            rows[code] = [_num(t) for t in found[-1]]
    return ver, valid, rows


KNOWN = [11761, 11740, 11707]     # versioni già viste online (dalla più recente)
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
           "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "Accept-Language": "it-IT,it;q=0.9,en;q=0.8",
           "Referer": "https://enterprise.aruba.it/"}


def _probe(n, s=1):
    """Una richiesta al documento: (codice HTTP, testo, diagnosi). Un 404 o un 403 non sono eccezioni: servono a capire cosa risponde il sito."""
    try:
        r = requests.get(BASE.format(n, s), headers=HEADERS, timeout=40)
    except requests.RequestException as e:
        return None, "", f"rete: {type(e).__name__}"
    return r.status_code, r.text, f"HTTP {r.status_code}, server {r.headers.get('server', '?')}, {len(r.text)} caratteri"


def _fetch_listino():
    """Legge la versione corrente del listino. Restituisce (url, versione, valido dal, righe) o solleva RuntimeError con la diagnosi."""
    status, raw, diag = _probe(KNOWN[0])
    if status == 200:
        ver, valid, rows = parse_listino(raw)
        if rows:
            return BASE.format(KNOWN[0], 1), ver, valid, rows
        inizio = re.sub(r"\s+", " ", htmllib.unescape(re.sub(r"<[^>]+>", " ", raw)))[:90]
        raise RuntimeError(f"documento ricevuto ({diag}) ma tabella dei prezzi non riconosciuta; inizio testo: {inizio}")
    # la versione più recente non risponde: il sito è raggiungibile? (provo le versioni precedenti, già viste online)
    older = None
    for n in KNOWN[1:]:
        st, rw, dg = _probe(n)
        if st == 200:
            ver, valid, rows = parse_listino(rw)
            if rows:
                older = (BASE.format(n, 1), ver, valid, rows)
                break
    if older is None:
        if "rete:" in diag:
            raise RuntimeError(f"sito non raggiungibile ({diag})")
        raise RuntimeError(f"il sito non fornisce il documento ai server di GitHub ({diag}; anche le versioni precedenti non rispondono): probabile blocco, verifica a mano")
    for n in range(KNOWN[0] + 1, KNOWN[0] + SEARCH_AHEAD + 1):      # c'è una versione più recente di quella nota?
        for s in (1, 2):
            st, rw, dg = _probe(n, s)
            if st == 200:
                ver, valid, rows = parse_listino(rw)
                if rows:
                    return BASE.format(n, s), ver, valid, rows
        time.sleep(0.05)
    return older


class _Prices:
    """Prezzo per codice servizio: dal documento online se leggibile e plausibile, altrimenti dalla tabella locale (con conteggio)."""
    def __init__(self, rows):
        self.rows, self.fallback = rows or {}, []

    def get(self, code, idx, static):
        live = (self.rows.get(code) or [None] * 4)[idx]
        if live is not None and live >= 0 and (static in (None, 0) or 0.2 <= live / static <= 5 or live == 0 == static):
            return live
        if static is not None and code not in self.fallback:
            self.fallback.append(code)
        return static


def collect():
    WARNINGS.clear()
    url, ver, valid, rows, err = None, STATIC_VERSION, STATIC_VALID, {}, None
    try:
        url, ver, valid, rows = _fetch_listino()
        ver, valid = ver or STATIC_VERSION, valid or STATIC_VALID
    except Exception as e:
        err = sanitize(str(e))[:230]
    P = _Prices(rows)
    src = url or BASE.format(LAST_KNOWN, 1)

    def n(extra, acn):
        return f"Listino Enterprise {ver} dal {valid}; qualifica ACN {ACN[acn]}; {extra}"

    def rec(kind, sku, unit, price, acn, extra="", term="On-demand"):
        return dict(provider=PROVIDER, region=REGION, kind=kind, sku=sku, unit=unit, price=price, term=term, source=src, note=n(extra, acn))

    out = []
    for c, code, v, ram, nvme, h, m, m1 in CLOUD_SERVER:
        note = f"{nvme} GB NVMe, traffico illimitato, 1 Gb/s; SLA 99,95%"
        hh, mm, yy = P.get(c, 0, h), P.get(c, 1, m), P.get(c, 2, m1)
        out.append(vm(PROVIDER, REGION, f"Cloud Server PRO {code}", v, ram, hh, monthly=mm, source=src, term="On-demand", note=n(note, "cs")))
        out.append(vm(PROVIDER, REGION, f"Cloud Server PRO {code}", v, ram, yy / 730, monthly=yy, source=src, term="Impegno 1 anno", note=n(note + "; 3 anni non previsto", "cs")))
    for c, code, os_, v, ram, disk, tb, m in VPS:
        mm = P.get(c, 1, m)
        out.append(vm(PROVIDER, REGION, f"Cloud VPS {code} {os_}", v, ram, mm / 730, monthly=mm, source=src, term="On-demand",
                      note=n(f"{disk}, {tb} TB/mese di traffico, fatturazione a mese intero; SLA 99,80%", "vps")))
    for c, code, v, ram, h, m in VDC:
        out.append(vm(PROVIDER, REGION, f"Virtual Data Center CS {code} Linux", v, ram, P.get(c, 0, h), monthly=P.get(c, 1, m), source=src, term="On-demand", note=n("senza storage; SLA 99,95%", "vdc")))
    out.append(rec("compute", "VMware Cloud Server: 1 vCPU", "EUR/mese per vCPU", P.get("Cev-0001", 1, 21.64), "vmw", f"1 anno {P.get('Cev-0001', 2, 19.48):.2f}"))
    out.append(rec("compute", "VMware Cloud Server: 1 GB RAM", "EUR/mese per GB", P.get("Cev-0002", 1, 2.63), "vmw", f"1 anno {P.get('Cev-0002', 2, 2.37):.2f}"))
    for c, name, v, ram, h, m in K8S:
        out.append(vm(PROVIDER, REGION, f"Managed Kubernetes {name}", v, ram, P.get(c, 0, h), monthly=P.get(c, 1, m), source=src, term="On-demand", note=n("nodo worker; SLA 99,95% (HA 99,98%)", "k8s")) | dict(kind="k8s"))
    out.append(rec("k8s", "Managed Kubernetes Master Node HA", "EUR/mese", P.get("Cnt-0012", 1, 57.69), "k8s", "SLA 99,98%"))
    for c, eng, code, v, ram, h, m in DBAAS:
        out.append(vm(PROVIDER, REGION, f"DBaaS {eng} {code}", v, ram, P.get(c, 0, h), monthly=P.get(c, 1, m), source=src, term="On-demand", note=n("istanza gestita; SLA 99,95%", "db")) | dict(kind="dbaas"))
    for c, code, gpu, cfg, m, m1, m3 in GPU_SERVERS:
        for term, idx, st in (("On-demand", 1, m), ("Impegno 1 anno", 2, m1), ("Impegno 3 anni", 3, m3)):
            mm = P.get(c, idx, st)
            out.append(rec("gpu", f"{gpu} ({code})", "EUR/ora", round(mm / 730, 4), "srv", f"server dedicato {code} con 1 GPU ({cfg}); canone {mm:.2f} EUR/mese su 730 h", term))
    for c, sku, m in BLOCK:
        mm = P.get(c, 1, m)
        out.append(rec("storage", sku, "EUR/GB/mese", round(mm / 100, 4), "blk", f"{mm:.2f} EUR/mese ogni 100 GB; SLA 99,95% (Regional 99,98%)"))
    obj = P.get("Stp-0010", 1, 0.28)
    pkg = P.get("Stp-0001", 1, 54.76)
    out.append(rec("storage", "Object Storage a consumo (object)", "EUR/GB/mese", round(obj / 10, 4), "obj", f"{obj:.2f} EUR ogni 10 GB/mese; ingresso illimitato"))
    out.append(rec("storage", "Object Storage pacchetti 4-256 TB (object)", "EUR/GB/mese", round(pkg / 4000, 5), "obj", f"{pkg:.2f} EUR/mese per 4 TB, 40 TB di traffico in uscita incluso"))
    for c, sku, m in (("Stv-0001", "Cloud Unified Storage VMware Standard", 73.53), ("Stv-0002", "Cloud Unified Storage VMware Plus", 220.60)):
        mm = P.get(c, 1, m)
        out.append(rec("storage", sku, "EUR/GB/mese", round(mm / 1000, 4), "vmw", f"{mm:.2f} EUR/mese per 1 TB"))
    egr = P.get("Stp-0011", 1, 0.66)
    out.append(rec("rete", "Traffico in uscita Object Storage a consumo", "EUR/TB", round(egr * 100, 2), "obj", f"{egr:.2f} EUR ogni 10 GB"))
    out.append(rec("rete", "Traffico (illimitato nei Cloud Server)", "EUR/TB", 0.0, "cs", "incluso nel prezzo del server"))
    out.append(rec("rete", "Elastic IP / IP pubblico Cloud Server", "EUR/mese", P.get("Nwc-0008", 1, 3.30), "net"))
    out.append(rec("rete", "Load Balancer Cloud Server", "EUR/mese", P.get("Nwc-0011", 1, 7.50), "net"))
    out.append(rec("rete", "VPN Tunnel (max 10 route)", "EUR/mese", P.get("Nwc-0007", 1, 48.00), "net"))
    out.append(rec("licenza", "Windows Server per vCPU (Cloud Server PRO)", "EUR/vCPU/mese", P.get("Cep-0022", 1, 13.01), "cs", "importo soggetto a variazione (art. 18.1)"))
    out.append(rec("licenza", "Remote Desktop Services 5 SAL (min. 5)", "EUR/mese", P.get("Cep-0025", 1, 65.49), "cs", "importo soggetto a variazione (art. 18.1)"))
    if err:
        WARNINGS.append(f"listino online non letto ({err}); uso la tabella {STATIC_VERSION} del {STATIC_VALID}")
    else:
        if ver != STATIC_VERSION:
            WARNINGS.append(f"letta la versione {ver} dal {valid} (la tabella di ripiego è {STATIC_VERSION}): aggiornare LAST_KNOWN")
        if P.fallback:
            WARNINGS.append(f"{len(P.fallback)} voci non leggibili dal documento, usata la tabella locale: {', '.join(P.fallback[:6])}")
    return out
