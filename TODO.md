# Prezzi cloud: piano di correzione

Si procede un passo alla volta. Ogni passo concluso viene segnato qui e i punti ancora aperti restano in elenco.
Ultimo aggiornamento: 2026-11-02 (passo 3, blocco A).

## Fatto
- [x] **Passo 1: Aruba e Seeweb allineati ai listini ufficiali.**
  - `collectors/aruba.py`: OpenStack Cloud Server (7 configurazioni, on-demand e annuale), GPU on Demand (L40S, RTX 4080 Super), Block Storage, disco aggiuntivo, traffico incluso. Fonte: cloud.it/prezzi, verificato il 2026-10-27.
  - `collectors/seeweb.py`: Cloud Shared CPU (7 taglie), High Memory (4), GPU (H100, A100, L40S, L4), on-demand e impegno 12 mesi (= "Impegno 1 anno"). Fonte: seeweb.it, verificato il 2026-11-02.
  - Eliminato il ripiego silenzioso `0,019 x vCPU` di Seeweb, che produceva prezzi inventati senza segnalarlo.
  - Nuovo `check_page()` in `common.py`: a ogni run controlla che la pagina ufficiale riporti ancora i prezzi della tabella; se no, lascia un avviso in `docs/data/status.json` (campo `note`). **Mai provato su rete reale: guardare il primo run.**
  - Rimossi i vecchi sconti a percentuale su Aruba (-20% e -35%): i prezzi annuali sono ora quelli ufficiali. Il 3 anni non esiste nel listino pubblico.
- [x] **Passo 2: AWS, Azure, GCP e Hetzner senza prezzi stimati né sconti inventati.**
  - `aws.py`: legge la Price List ufficiale (on-demand, Reserved Standard senza anticipo 1 e 3 anni, GPU per GPU, EBS gp3, S3, traffico) in 3 regioni (Milano, Francoforte, Irlanda).
  - `azure_cloud.py`: Retail Prices API (on-demand, Reservation 1 e 3 anni, Blob, traffico, GPU) a Milano e nei Paesi Bassi. La RAM è quella della famiglia (D v5 = 4, E v5 = 8, F v2 = 2 GB/vCPU).
  - `gcp.py`: Cloud Billing Catalog API (N2 on-demand e Committed Use 1/3 anni, disco, Cloud Storage, GPU, traffico). **Serve il secret `GCP_API_KEY`**: senza, GCP resta vuoto, con una nota in `status.json`.
  - `hetzner.py`: API ufficiale con `HCLOUD_TOKEN`. Senza token si saltano le chiamate e restano i prezzi verificati di `manual/hetzner.yml`.
  - `run.py`: i dati salvati prima della correzione non vengono più usati come ripiego (`verified_schema` in `status.json`).
  - Cancellato `manual/gcp.yml` (valori senza riscontro). Cancellate le categorie k8s, dbaas, colocation e licenze di questi 4 provider (valori inventati, elenco sotto).
  - **Mai provato su rete reale.** Da controllare al primo run: righe `aws`, `azure`, `gcp`, `hetzner` in `docs/data/status.json` (campo `note` per gli avvisi parziali) e che in `latest.json` ci siano record compute per ogni provider.

- [x] **Passo 3A: hyperscaler e cloud globali.**
  - `oracle.py`: Price List API pubblica di Oracle (anonima, in EUR): E4 ed E5 Flex (1 OCPU = 2 vCPU), Block Volume, Object Storage, traffico in uscita, GPU. Le voci non trovate nel listino non si inventano: finiscono nelle note di `status.json`.
  - `digitalocean.py`: 8 Droplet dal listino ufficiale (USD convertiti in EUR col cambio del giorno) con controllo online `check_page()`. Vecchi prezzi errati: Basic 2 vCPU/4 GB era 20 USD, ora 24.
  - `vultr.py` e `linode.py`: già leggevano le API ufficiali; tolta la voce inventata "traffico extra 10 EUR/TB".
  - `aws.py`: GPU con una voce per istanza ("g5.12xlarge (4x NVIDIA A10G 24GB)", prezzo per GPU nel campo prezzo), famiglie p5en/p5e/p5/p4d/p4de/p3/g6e/g6/g5/g5g/g4dn, più la regione eu-north-1 (Stoccolma). `azure_cloud.py`: stesso schema per le VM GPU.
  - **Mai provato su rete reale.** Da controllare al primo run: righe `oracle`, `digitalocean`, `vultr`, `linode` in `docs/data/status.json` e che in `latest.json` ci siano record compute per ciascuno; il formato dell'API Oracle è il punto meno sicuro.

## Da fare, in ordine
- [ ] **Passo 3B: provider locali** (europei, italiani, virtualizzazione)
  - STACKIT, Exoscale, Enter, Proxmox/VMware/Nutanix (`manual/onprem.yml`), IONOS, Scaleway, OVHcloud, Hetzner (`manual/hetzner.yml`), Fastweb, Noovle, `manual/gpuaas.yml`.
  - Per ognuno: fonte ufficiale, data di verifica, niente voci senza riscontro. Su OVHcloud tolta la voce inventata "traffico extra 10 EUR/TB".
- [ ] **Passo 4: `run.py`, workflow e sicurezza**
  - Rimettere il controllo sui cali di record, come avviso e senza scartare i dati.
  - Applicare `sanitize()` anche a `status.json` e ai `print`; in `common.get` usare `raise ... from None`.
  - Cancellare `update.yml` nella radice (duplicato di `.github/workflows/update.yml`).
- [ ] **Passo 5: `docs/index.html`**
  - Togliere i 4 record di prova con prezzi inventati.
  - Ripristinare la PWA (manifest, registrazione del service worker) e sostituire Tailwind da `cdn.tailwindcss.com` con CSS locale: senza versione fissata, non funziona offline.
  - Escape dei testi inseriti con `innerHTML` e link solo `https`.
  - Prezzi sotto 1 EUR con 4 decimali (oggi 0,0365 diventa "0,04").
  - Storage: "Performance" finisce in "Blocco Standard"; categorie `licenses` e `licenza` duplicate nei dati.
  - Funzioni perse rispetto alla versione precedente: matrice di confronto per taglia, dettaglio con storico, stato delle fonti (serve per mostrare le note di `status.json`).
- [ ] **Passo 6: Docker e Cloud Run**
  - I dati sono nell'immagine: serve un trigger Cloud Build a ogni push su `main`, altrimenti gli aggiornamenti giornalieri non arrivano.
  - nginx: `Cache-Control: no-cache` su `/data/` e `sw.js`, gzip, intestazioni di sicurezza, immagine `nginx-unprivileged`.
- [ ] **Passo 7 (ultimo): chiavi GCP e Hetzner** (rimandate su richiesta)
  - Oggi GCP è vuoto e Hetzner usa solo i 6 prezzi manuali.
  - GCP: creare una chiave API nuova, limitata alla sola Cloud Billing API, e salvarla come secret `GCP_API_KEY`. **Revocare la vecchia chiave** comparsa in passato in `status.json` (resta nella cronologia pubblica del repo).
  - Hetzner: token di sola lettura come secret `HCLOUD_TOKEN` (facoltativo; poi eliminare `manual/hetzner.yml` per non avere doppioni).
  - Dopo il primo run controllare `status.json` e le SKU GCP.

## Voci rimosse al passo 1 (non verificabili: restano qui per traccia)
**Aruba** (valori che erano nel collector):
- Cloud VPS: Small 1 vCPU/1 GB 2,79; Medium 1/2 4,99; Large 2/4 9,99; Extra Large 4/8 19,99; Maxi 8/16 39,99 EUR/mese.
- Cloud Server Pro "stimati": 2/4 27,74; 4/8 55,48; 8/16 110,96; 16/32 221,92 (i valori ufficiali sono 20,10; 31,20; 55,50; 152,60).
- GPU L4 520, A10G 850, A100 1450 EUR/mese (non esistono nel listino; ufficiali: L40S e RTX 4080 Super).
- Colocation 1U 75, 1/4 rack 350, 1/2 rack 650, rack intero 1100 EUR/mese.
- Storage: block SSD 0,05, NVMe 0,12, object 0,018 EUR/GB/mese; egress 10 EUR/TB; licenza Windows 4,50/core; Kubernetes 0 (gratuito); DBaaS 29 EUR/mese.

**Seeweb**:
- Colocation 1U 50 e rack 42U 900 EUR/mese; traffico extra 40 EUR/TB.
- `manual/seeweb.yml`: Cloud Server 2/8 45, 4/16 85, 8/32 160, 16/64 310 EUR/mese, marcati "verificati" ma senza riscontro sulla pagina ufficiale.
- Cloud Shared "stimati": 13,87; 27,74; 55,48; 110,96; 221,92 EUR/mese (ufficiali, per esempio 4 vCPU/8 GB: 45,99).

**Ancora da raccogliere per Aruba e Seeweb**: Aruba Cloud VPS, object storage, colocation, Kubernetes, DBaaS, licenze; Seeweb Cloud Server non condiviso, Object Storage, Kubernetes, housing, e verifica se i prezzi sono IVA esclusa.

## Voci rimosse al passo 2 (non verificabili: restano qui per traccia)
**AWS** (tabella fissa "stimata", eu-south-1): m6i/c6i/r6i/m7i con prezzo orario fisso (per esempio m6i.large 0,1016 EUR/h); impegno 1 anno -30%, 3 anni -50%; EBS gp3 0,088 e S3 0,023 EUR/GB/mese; egress 90 EUR/TB; Direct Connect 1 Gbps 220 EUR/mese; g5.2xlarge 950 EUR/mese; Windows Server 23 EUR/vCPU/mese; EKS 73 EUR/mese; RDS PostgreSQL db.m6i.large 145 EUR/mese.
**Azure** (italynorth): D/E/F con prezzo orario fisso (per esempio D2s_v5 0,096 EUR/h); impegno -28% e -48%; Premium SSD 0,12 e Blob 0,021 EUR/GB/mese; egress 87 EUR/TB; ExpressRoute 1 Gbps 210 EUR/mese; "NCas_v4 (1x AMD MI200)" 920 EUR/mese; Windows Hybrid Benefit 18; AKS 0; Azure Database for PostgreSQL 140 EUR/mese.
**GCP** (europe-west8): N2/C2/E2 con prezzo orario fisso (per esempio n2-standard-2 0,097 EUR/h); impegno -30% e -55%; PD Balanced 0,095 e Cloud Storage 0,023 EUR/GB/mese; egress 85 EUR/TB; Partner Interconnect 180; GPU L4 540 EUR/mese; RHEL 45; GKE 73; Cloud SQL PostgreSQL 142. `manual/gcp.yml`: n2-standard-2/4/8/16 a 75,40; 150,80; 301,60; 603,20 EUR/mese (europe-west3), PD Balanced 0,10.
**Hetzner**: server dedicati AX41 44, AX51 53, AX101 79, AX161 109, EX44 54, EX101 89 EUR/mese con impegno 1 anno -10%; server GPU 239 e 450 EUR/mese; Storage Box BX11 3,81 e BX21 12,97, Storage Share 5,10; volume 0,047 EUR/GB/mese; colocation 1U 39 e rack 520; extra traffico 1,19 EUR/TB; Windows Server 25; Kubernetes 0.
**Da raccogliere con fonti ufficiali** per questi provider: Kubernetes gestito, database gestiti, licenze, colocation e collegamenti dedicati (Direct Connect, ExpressRoute, Interconnect).

## Voci rimosse al passo 3A (non verificabili: restano qui per traccia)
**Oracle** (tabella fissa, eu-milan-1): VM.Standard.E4.Flex 2/8 0,054 EUR/h (39,42/mese), 4/16 78,84, 8/32 157,68, 16/64 315,36; Block Volume Performance Balanced 0,025 e Object Storage 0,023 EUR/GB/mese; egress 8,50 EUR/TB; OKE Basic 0; OCI Database with PostgreSQL (2 vCPU/8 GB) 68 EUR/mese.
**DigitalOcean** (tabella fissa, Francoforte/Amsterdam): Basic 1/1 4, 1/2 10, 2/4 20, 4/8 40, 8/16 80 EUR/mese; DOKS 0; PostgreSQL gestito 2 vCPU/8 GB 110; Spaces 5 EUR/mese (250 GB + 1 TB di traffico).
**Vultr e Akamai Linode**: "traffico extra (oltre bundle)" 10 USD/TB convertito in EUR, senza riscontro.
**Da raccogliere con fonti ufficiali**: DigitalOcean 16 vCPU, altre taglie CPU/Memory-Optimized, GPU Droplet, Volumes, Spaces, traffico, Kubernetes, database; Oracle Kubernetes, database, GPU verificate sul listino, impegno (Universal Credits).
