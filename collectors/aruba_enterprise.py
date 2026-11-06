"""Aruba Cloud Enterprise: "Listino per il Mercato Enterprise" v. ARB-11740-1, valido dal 03/08/2026 (enterprise.aruba.it), IVA esclusa.
NON è il listino pubblico di cloud.it (quello è in aruba.py, provider "Aruba Cloud"): è il listino dei servizi con qualifica ACN
usato per enterprise e PA, con prezzi, impegni (1 anno -10%, 3 anni solo sui server dedicati) e SLA propri. Tabella locale con i valori
letti il VERIFIED; a ogni run check_page() verifica che il documento riporti ancora i prezzi principali. Confronto: ARUBA_LISTINI.md."""
from common import vm, check_page

URL = "https://enterprise.aruba.it/documents/tc-files/it/arb-11740-1_cloud_listino.aspx"
VERSION, VALID_FROM, VERIFIED = "ARB-11740-1", "03/08/2026", "2026-11-04"
PROVIDER, REGION = "Aruba Cloud Enterprise", "IT"
WARNINGS = []

# (codice, vCPU, RAM GB, NVMe GB, EUR/ora, EUR/mese on-demand, EUR/mese impegno 1 anno)
CLOUD_SERVER = [
    ("O1A2", 1, 2, 20, 0.01847, 13.48, 12.13), ("O2A4", 2, 4, 80, 0.03151, 23.00, 20.70), ("O4A8", 4, 8, 120, 0.05712, 41.70, 37.53),
    ("O8A16", 8, 16, 160, 0.10442, 76.23, 68.61), ("O12A24", 12, 24, 240, 0.15564, 113.62, 102.26), ("O16A32", 16, 32, 360, 0.21078, 153.87, 138.48),
    ("O24A48", 24, 48, 480, 0.31327, 228.69, 205.82), ("O32A64", 32, 64, 480, 0.46164, 337.00, 303.30), ("O1A4R", 1, 4, 40, 0.02466, 18.00, 16.20),
    ("O2A8R", 2, 8, 80, 0.05017, 36.63, 32.96), ("O4A16R", 4, 16, 120, 0.08904, 65.00, 58.50), ("O8A32R", 8, 32, 160, 0.16301, 119.00, 107.10)]
# VPS: (codice, S.O., vCPU, RAM GB, disco, traffico incluso TB/mese, EUR/mese)
VPS = [("O1I1", "Linux", 1, 1, "20 GB SSD", 2, 5.77), ("O1I2", "Linux", 1, 2, "40 GB SSD", 5, 7.59), ("O2A4", "Linux", 2, 4, "40 GB NVMe", 25, 9.21),
       ("O4A8", "Linux", 4, 8, "80 GB NVMe", 50, 16.97), ("O8A16", "Linux", 8, 16, "160 GB NVMe", 100, 32.50), ("O16A32", "Linux", 16, 32, "320 GB NVMe", 100, 63.56),
       ("O2A4", "Windows", 2, 4, "40 GB NVMe", 25, 38.17), ("O4A8", "Windows", 4, 8, "80 GB NVMe", 50, 74.90),
       ("O8A16", "Windows", 8, 16, "160 GB NVMe", 100, 148.36), ("O16A32", "Windows", 16, 32, "320 GB NVMe", 100, 295.28)]
# Virtual Data Center, Linux: (codice, vCPU, RAM GB, EUR/ora, EUR/mese)
VDC = [("O1A2", 1, 2, 0.01429, 10.43), ("O2A4", 2, 4, 0.02771, 20.23), ("O4A8", 4, 8, 0.05716, 41.72), ("O8A16", 8, 16, 0.10681, 77.97),
       ("O12A24", 12, 24, 0.16021, 116.96), ("O16A32", 16, 32, 0.22863, 166.90), ("O24A48", 24, 48, 0.34294, 250.35), ("O32A64", 32, 64, 0.45726, 333.80),
       ("O1A4", 1, 4, 0.02000, 14.60), ("O2A8", 2, 8, 0.04001, 29.21), ("O4A16", 4, 16, 0.08002, 58.41), ("O8A32", 8, 32, 0.16004, 116.83), ("O16A64", 16, 64, 0.35145, 256.56)]
# Kubernetes gestito: (nome, vCPU, RAM GB, EUR/ora, EUR/mese)
K8S = [("general purpose K2A4", 2, 4, 0.03209, 23.42), ("general purpose K4A8", 4, 8, 0.05893, 43.02), ("general purpose K8A16", 8, 16, 0.10820, 78.99),
       ("general purpose K12A24", 12, 24, 0.16089, 117.45), ("general purpose K16A32", 16, 32, 0.21700, 158.41), ("general purpose K24A48", 24, 48, 0.31896, 232.84),
       ("general purpose K32A64", 32, 64, 0.41066, 299.78), ("memory K2A8R", 2, 8, 0.04006, 29.25), ("memory K4A16R", 4, 16, 0.07388, 53.93),
       ("memory K8A32R", 8, 32, 0.13810, 100.81), ("memory K16A64R", 16, 64, 0.27679, 202.06), ("memory K32A128R", 32, 128, 0.53023, 387.07)]
# DBaaS: (motore, codice, vCPU, RAM GB, EUR/ora, EUR/mese)
DBAAS = [("MySQL", "O1A2", 1, 2, 0.02261, 16.51), ("MySQL", "O2A4", 2, 4, 0.04091, 29.86), ("MySQL", "O4A8", 4, 8, 0.07750, 56.57), ("MySQL", "O8A16", 8, 16, 0.15068, 110.00),
         ("MySQL", "O12A24", 12, 24, 0.22329, 163.00), ("MySQL", "O16A32", 16, 32, 0.29628, 216.29), ("MySQL", "O24A48", 24, 48, 0.44227, 322.86),
         ("MySQL", "O32A64", 32, 64, 0.58826, 429.43), ("MySQL", "O1A4", 1, 4, 0.02985, 21.79), ("MySQL", "O2A8", 2, 8, 0.05540, 40.44), ("MySQL", "O4A16", 4, 16, 0.10650, 77.74),
         ("MySQL", "O8A32", 8, 32, 0.20869, 152.34), ("MySQL", "O16A64", 16, 64, 0.38498, 281.04),
         ("MSSQL Server Web", "O4A8", 4, 8, 0.10868, 79.34), ("MSSQL Server Web", "O4A16", 4, 16, 0.12818, 93.57),
         ("MSSQL Server Standard", "O4A8", 4, 8, 0.95364, 696.16), ("MSSQL Server Standard", "O4A16", 4, 16, 0.97313, 710.39),
         ("MSSQL Server Enterprise", "O4A8", 4, 8, 3.44781, 2516.90), ("MSSQL Server Enterprise", "O4A16", 4, 16, 3.46731, 2531.13),
         ("MSSQL Server Enterprise", "O8A16", 8, 16, 6.89275, 5031.71), ("MSSQL Server Enterprise", "O8A32", 8, 32, 6.93174, 5060.17),
         ("MSSQL Server Enterprise", "O12A24", 12, 24, 10.33769, 7546.52), ("MSSQL Server Enterprise", "O16A32", 16, 32, 13.78263, 10061.32)]
# Server dedicati con GPU (1 GPU): (codice, GPU, configurazione, EUR/mese on-demand, 1 anno, 3 anni)
GPU_SERVERS = [("AI-A108", "NVIDIA GeForce RTX 4070 Super 12GB", "Ryzen 7 7700X 8C, 64 GB DDR5, 2x NVMe 2 TB", 648.23, 583.41, 525.07),
               ("AI-A109", "NVIDIA GeForce RTX 4080 Super 16GB", "Ryzen 9 7900X 12C, 128 GB DDR5, 2x NVMe 2 TB", 1011.38, 910.24, 819.22),
               ("AI-A110", "NVIDIA L40S 48GB", "Dell R7625, 2x EPYC 9124 (32 core), 128 GB DDR5, 2x SSD 480 GB", 2942.66, 2648.40, 2383.56),
               ("AI-A110E.64", "NVIDIA L40S 48GB", "Dell R7625, 2x EPYC 9354 (64 core), 128 GB DDR5, 2x SSD 480 GB", 3077.39, 2769.65, 2492.69)]
ACN = {"cs": "IA-418 QC1", "vps": "IA-4350 QC1", "vdc": "IA-7024 QC1", "vmw": "IA-4253 QC1", "blk": "IA-4041 QC1", "obj": "IA-137 QC1",
       "k8s": "PA-4039 QC1", "db": "PA-2828 QC1", "srv": "IN-6469 AI1", "net": "IA-418 QC1"}


def _n(extra, acn):
    return f"Listino Enterprise {VERSION} dal {VALID_FROM}; qualifica ACN {ACN[acn]}; {extra}"


def _rec(kind, sku, unit, price, acn, extra="", term="On-demand"):
    return dict(provider=PROVIDER, region=REGION, kind=kind, sku=sku, unit=unit, price=price, term=term, source=URL, note=_n(extra, acn))


def collect():
    WARNINGS.clear()
    out = []
    for code, v, ram, nvme, h, m, m1 in CLOUD_SERVER:
        n = f"{nvme} GB NVMe, traffico illimitato, 1 Gb/s; SLA 99,95%"
        out.append(vm(PROVIDER, REGION, f"Cloud Server PRO {code}", v, ram, h, monthly=m, source=URL, term="On-demand", note=_n(n, "cs")))
        out.append(vm(PROVIDER, REGION, f"Cloud Server PRO {code}", v, ram, m1 / 730, monthly=m1, source=URL, term="Impegno 1 anno", note=_n(n + "; 3 anni non previsto", "cs")))
    for code, os_, v, ram, disk, tb, m in VPS:
        out.append(vm(PROVIDER, REGION, f"Cloud VPS {code} {os_}", v, ram, m / 730, monthly=m, source=URL, term="On-demand",
                      note=_n(f"{disk}, {tb} TB/mese di traffico, fatturazione a mese intero; SLA 99,80%", "vps")))
    for code, v, ram, h, m in VDC:
        out.append(vm(PROVIDER, REGION, f"Virtual Data Center CS {code} Linux", v, ram, h, monthly=m, source=URL, term="On-demand", note=_n("senza storage; SLA 99,95%", "vdc")))
    out.append(_rec("compute", "VMware Cloud Server: 1 vCPU", "EUR/mese per vCPU", 21.64, "vmw", "0,02965 EUR/h; 1 anno 19,48"))
    out.append(_rec("compute", "VMware Cloud Server: 1 GB RAM", "EUR/mese per GB", 2.63, "vmw", "0,00361 EUR/h; 1 anno 2,37"))
    for name, v, ram, h, m in K8S:
        out.append(vm(PROVIDER, REGION, f"Managed Kubernetes {name}", v, ram, h, monthly=m, source=URL, term="On-demand", note=_n("nodo worker; SLA 99,95% (HA 99,98%)", "k8s")) | dict(kind="k8s"))
    out.append(_rec("k8s", "Managed Kubernetes Master Node HA", "EUR/mese", 57.69, "k8s", "0,07903 EUR/h"))
    for eng, code, v, ram, h, m in DBAAS:
        out.append(vm(PROVIDER, REGION, f"DBaaS {eng} {code}", v, ram, h, monthly=m, source=URL, term="On-demand", note=_n("istanza gestita; SLA 99,95%", "db")) | dict(kind="dbaas"))
    for code, gpu, cfg, m, m1, m3 in GPU_SERVERS:
        for term, mm in (("On-demand", m), ("Impegno 1 anno", m1), ("Impegno 3 anni", m3)):
            out.append(_rec("gpu", f"{gpu} ({code})", "EUR/ora", round(mm / 730, 4), "srv", f"server dedicato {code} con 1 GPU ({cfg}); canone {mm:.2f} EUR/mese su 730 h", term))
    for sku, m in (("Block Storage Standard (Availability Zone)", 4.38), ("Block Storage Performance (Availability Zone)", 8.03), ("Block Storage Standard (Regional)", 7.30),
                   ("Block Storage Performance (Regional)", 11.68), ("Block Storage Snapshot", 4.38)):
        out.append(_rec("storage", sku, "EUR/GB/mese", round(m / 100, 4), "blk", f"{m:.2f} EUR/mese ogni 100 GB; SLA 99,95% (Regional 99,98%)"))
    out.append(_rec("storage", "Object Storage a consumo (object)", "EUR/GB/mese", 0.028, "obj", "0,28 EUR ogni 10 GB/mese; ingresso illimitato"))
    out.append(_rec("storage", "Object Storage pacchetti 4-256 TB (object)", "EUR/GB/mese", 0.01369, "obj", "54,76 EUR/mese per 4 TB (13,69 EUR/TB), 40 TB di traffico in uscita incluso"))
    out.append(_rec("storage", "Cloud Unified Storage VMware Standard", "EUR/GB/mese", 0.0735, "vmw", "73,53 EUR/mese per 1 TB"))
    out.append(_rec("storage", "Cloud Unified Storage VMware Plus", "EUR/GB/mese", 0.2206, "vmw", "220,60 EUR/mese per 1 TB"))
    out.append(_rec("rete", "Traffico in uscita Object Storage a consumo", "EUR/TB", 66.0, "obj", "0,66 EUR ogni 10 GB"))
    out.append(_rec("rete", "Traffico (illimitato nei Cloud Server)", "EUR/TB", 0.0, "cs", "incluso nel prezzo del server"))
    out.append(_rec("rete", "Elastic IP / IP pubblico Cloud Server", "EUR/mese", 3.30, "net", "0,00453 EUR/h"))
    out.append(_rec("rete", "Load Balancer Cloud Server", "EUR/mese", 7.50, "net"))
    out.append(_rec("rete", "VPN Tunnel (max 10 route)", "EUR/mese", 48.00, "net", "0,06575 EUR/h"))
    out.append(_rec("licenza", "Windows Server per vCPU (Cloud Server PRO)", "EUR/vCPU/mese", 13.01, "cs", "0,01782 EUR/h; importo soggetto a variazione (art. 18.1)"))
    out.append(_rec("licenza", "Remote Desktop Services 5 SAL (min. 5)", "EUR/mese", 65.49, "cs", "importo soggetto a variazione (art. 18.1)"))
    w = check_page(URL, [23.00, 41.70, 76.23, 153.87, 36.63, 119.00, 4.38, 2942.66])
    if w:
        WARNINGS.append(w)
    return out
