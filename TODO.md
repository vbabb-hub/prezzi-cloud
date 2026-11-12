# Prezzi cloud: piano di correzione

Si procede un passo alla volta. Ogni passo concluso viene segnato qui e i punti ancora aperti restano in elenco.
Ultimo aggiornamento: 2026-11-10 (passo 7: materiali pronti, restano le azioni sulle chiavi).

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

- [x] **Passo 3B: provider locali.**
  - `stackit.py`: listino ufficiale STACKIT (EU01, singola zona): 7 famiglie di VM (28 voci), storage, 10 tipi di server GPU con modelli confermati dalla pagina ufficiale (n1 = A100 80GB, n2 = L40S, n3 = H100 NVL; n3.104d.g8 = 8x HGX H100). Controllo online `check_page()` sui prezzi GPU. Eliminato `manual/stackit.yml` (valori già presenti nel collector).
  - `exoscale.py`: 4 istanze Standard, storage a blocchi, Object Storage (0,0184 EUR/GB da pagina ufficiale) e traffico (20 EUR/TB). Istanze e block storage da fonti secondarie coerenti tra loro: segnalato nelle note.
  - `ovh.py`: **corretto un errore**: i dati del catalogo OVH su storage, object storage e GPU (lista `_EXTRA`) non venivano mai inclusi perché `run.py` chiamava solo `collect()`; ora sono inclusi. Tolta la voce inventata "traffico extra 10 EUR/TB".
  - `entersuite.py` e `proxmox.py`: tabelle fisse non verificate disattivate (sostituite da uno stub); le licenze Proxmox e VMware stanno in `manual/onprem.yml` (Proxmox Community 120 EUR ufficiale; le altre fasce da fonti secondarie; VMware in USD, stima non ufficiale).
  - Già a posto, non toccati: `manual/ionos.yml` (listino ufficiale EUR), `manual/scaleway.yml` (pagine ufficiali), `manual/hetzner.yml` (tabella ufficiale 15/06/2026), `manual/fastweb.yml` e `manual/noovle.yml` (solo segnaposto: nessun listino pubblico).
  - **Mai provato su rete reale.** Da controllare al primo run: righe `stackit`, `exoscale`, `ovh` in `docs/data/status.json`; in `latest.json` ora devono comparire GPU e storage OVHcloud.

- [x] **Passo 3C: Aruba Enterprise e Polo Strategico Nazionale.**
  - `aruba_enterprise.py`: provider **"Aruba Cloud Enterprise"** dal "Listino per il Mercato Enterprise" ARB-11740-1 (valido dal 03/08/2026): Cloud Server PRO (12 taglie, on-demand e 1 anno), Cloud VPS, Virtual Data Center, Kubernetes gestito, DBaaS, server con GPU (on-demand, 1 e 3 anni), storage, rete, licenze. Ogni voce riporta versione del listino e qualifica ACN. Provider separato dal pubblico "Aruba Cloud" (`aruba.py`, note ora con "Listino pubblico cloud.it"). Confronto in `ARUBA_LISTINI.md`.
  - `psn.py`: **"Polo Strategico Nazionale"**, listino Industry Standard dal 30/04/2026 (canone annuale, 36 voci): IaaS Shared VM (da Tiny a X-Large) e Pool con e senza HA, risorse aggiuntive, IaaS Private Blade, CaaS (Kubernetes), database PaaS, licenze (Windows Server, Red Hat). Compaiono come "Impegno 1 anno" (canone annuale). **Location `IT`** sia per PSN sia per Aruba Cloud Enterprise.
  - Verifica dei prezzi PSN: le voci IaaS Shared, Blade e CaaS Licensed Medium hanno tutte un rapporto costante di +0,89% rispetto alla release di maggio 2025: conferma che l'abbinamento è giusto (prima erano 5 voci non confermate). Restano **11 voci abbinate solo per posizione** (nota "da verificare"): CaaS Licensed Large, i 7 database PaaS e le 3 licenze.
  - **Correzione**: nel messaggio del passo 3B avevo scritto che il listino Enterprise dava "VPS O2A4 a 41,70 EUR/mese": era una lettura sbagliata del risultato di ricerca. 41,70 è il Cloud Server PRO **O4A8** (0,05712 EUR/h); il VPS O2A4 costa 9,21 EUR/mese. I confronti corretti sono in `ARUBA_LISTINI.md`.
  - **Mai provato su rete reale.** Da controllare al primo run: righe `aruba-enterprise` e `psn` in `docs/data/status.json` (per Aruba Enterprise l'avviso `note` dice se i prezzi non sono più sulla pagina).

- [x] **Passo 4: `run.py`, workflow e sicurezza.**
  - `common.py`: `sanitize()` ora maschera anche il valore esatto dei secret (`GCP_API_KEY`, `HCLOUD_TOKEN`), i token Bearer, le chiavi Google e i parametri `key=`, `token=`, `authorization=`. `get()` usa `raise ... from None`: l'URL con la chiave non resta più nel traceback.
  - `run.py`: `sanitize()` su `status.json`, note, errori e `print`/traceback. Rimesso il controllo sui cali di record **come avviso** (nota in `status.json`: "record calati da X a Y") senza scartare i dati nuovi. Aggiunto il riepilogo delle fonti nella pagina del run su GitHub Actions.
  - Workflow: un solo run alla volta (`concurrency`) e limite di 45 minuti. I secret `GCP_API_KEY` e `HCLOUD_TOKEN` restano (passo 7).
  - Da eliminare dal repo: `update.yml` nella radice (duplicato di `.github/workflows/update.yml`).
  - Provato con una chiave finta in un messaggio di errore: non compare né nel log, né in `status.json`, né nel riepilogo.

- [x] **Passo 5: pagina `docs/index.html`.** Mantenuti il tuo layout, i filtri e la barra dei provider.
  - Tolti i 4 record di prova con prezzi inventati: se i dati non si caricano compare un errore, non dati falsi.
  - **Tailwind**: niente più `cdn.tailwindcss.com` (non fissato a una versione e inutilizzabile offline). Il CSS è compilato in `docs/tailwind.css` (13 KB, Tailwind 3.4.17). Dopo ogni modifica alle classi di `index.html` o `app.js` va rigenerato: `npx tailwindcss@3.4.17 -c tailwind/tailwind.config.js -i tailwind/input.css -o docs/tailwind.css --minify` (dalla radice del repo).
  - **PWA ripristinata**: manifest, icona, registrazione del service worker (`sw.js` v9 con i file giusti), `theme-color`.
  - **Sicurezza**: nessun codice o stile in linea; la logica è in `docs/app.js`. Tutti i testi dei dati sono protetti (escape) e i link ammettono solo `https`. Content-Security-Policy restrittiva nella pagina. I nomi dei provider non passano più dentro `onclick`.
  - **Correzioni**: prezzi sotto 1 EUR con 4 decimali (0,0365 non diventa più 0,04); tabella con la colonna vCPU/RAM sempre presente (prima le colonne si sfalsavano fuori da Compute); "Performance" ora è storage ad alte prestazioni; filtri GPU con H200, RTX e "Altre"; `licenses` e `licenza` contate insieme; esportazione CSV con virgolette corrette e colonna note.
  - **Unità di prezzo**: nuovo filtro, perché confrontare "EUR/GB/mese" con "EUR/mese per pacchetto" non ha senso. Di default si vede l'unità più frequente della categoria; "Tutte le unità" mostra il resto, e il contatore indica quante voci sono nascoste.
  - **Recuperato dalla versione precedente**: nota di ogni voce sotto lo SKU (così si legge "Listino Enterprise" o "fonte secondaria"), clic su una riga per il dettaglio con lo **storico dei prezzi**, avviso "non aggiornato", pannello **Stato delle fonti** (con le note di `status.json`) e segnalazione se i dati hanno più di 3 giorni.
  - Da eliminare dal repo: `docs/style.css` (non più usato).
  - La matrice di confronto per taglia è stata aggiunta nel passo 5B.

- [x] **Passo 6: Docker e Cloud Run.**
  - `Dockerfile`: immagine `nginxinc/nginx-unprivileged:1.27-alpine` (non gira come root, porta 8080); `.dockerignore`: nel contesto di build solo `docs` e `nginx`, senza `docs/data/history`. Il vecchio Dockerfile scriveva la configurazione con `echo`, senza intestazioni di sicurezza né regole di cache, e con nginx come root.
  - `nginx/default.conf` e `nginx/security-headers.conf`: Content-Security-Policy, HSTS e altre intestazioni; `Cache-Control: no-cache` per pagina, dati e `sw.js` (solo `icon.svg` in cache un giorno); gzip; manifest col tipo giusto; solo GET e HEAD; file nascosti bloccati; versione di nginx nascosta. **Provata con un nginx reale**: la prima versione dava 404 su `/` e serviva il manifest come `text/plain`, entrambi corretti.
  - `cloudbuild.yaml` e `DEPLOY.md`: ricostruzione dell'immagine e deploy su Cloud Run. Il problema è che i dati stanno nell'immagine: serve un trigger Cloud Build a ogni push su `main` (filtro sui file) oppure una ricostruzione giornaliera programmata.
  - **Non provati** (non disponibili nella sandbox): `docker build` e Cloud Build. Da controllare: che la build parta dopo il commit del workflow giornaliero (se no, usare la ricostruzione programmata), l'esistenza del repository di Artifact Registry e i ruoli dell'account di servizio di Cloud Build.

- [x] **Passo 5B: confronto per taglia nella pagina.** In Compute compare la scelta "Vista": *Elenco* (la tabella di prima) oppure *Confronto per taglia*.
  - Matrice con i provider in riga e 2, 4, 8, 16 vCPU in colonna: ogni cella è la configurazione più economica del provider (tra tutte le regioni) con il rapporto RAM/vCPU scelto (2, 4 o 8 GB); la più bassa di ogni colonna è evidenziata e le altre mostrano la differenza percentuale. Si ordina cliccando l'intestazione di una colonna.
  - Scelta dell'impegno (on-demand, 1 anno, 3 anni): dove un provider non ha lo sconto compare il prezzo on-demand con "(OD)". Il Polo Strategico Nazionale ha solo canone annuale, quindi compare con l'impegno a 1 anno.
  - Cliccando una cella si apre il dettaglio con nota, fonte e storico; cliccando il nome di un provider si passa all'elenco filtrato su di lui. Sotto il prezzo compare "disco incluso" o "senza disco" quando la nota lo dice.
  - Limite noto: i prezzi non sono tutti omogenei (alcuni provider includono disco e traffico, altri no); la nota sotto la matrice lo avverte, ma il confronto va letto con il dettaglio. Si considerano solo voci in EUR/mese con vCPU e RAM esatte, non i prezzi per risorsa.
  - Dopo aver cambiato le classi di `index.html` o `app.js` va rigenerato `docs/tailwind.css` (comando nel passo 5). `sw.js` è passato a v10.

## Da fare, in ordine
- [ ] **Punti aperti emersi dal passo 3** (da decidere)
  - Exoscale: verificare istanze e block storage su una fonte ufficiale; GPU (7 modelli), sconto con impegno a 12 mesi, Kubernetes, database.
  - Enter: nessun listino pubblico trovato, da richiedere.
  - Proxmox: verificare Standard e Premium sul sito ufficiale (valori usati 550 e 1.100 da fonti secondarie; il vecchio collector aveva 1.020 e 2.040).
  - VMware: nessun listino pubblico Broadcom, i valori restano indicativi. Nutanix: nessun prezzo.
  - IONOS: server con core dedicati e Savings Plan, object storage, traffico. Scaleway: storage e traffico. Hetzner: object storage.
- [ ] **Passo 3C bis: completamenti PSN e Aruba Enterprise** (da decidere)
  - PSN, non incluso perché il PDF non permette un abbinamento affidabile (etichette e prezzi sono in colonne separate e molte righe non hanno nome): tipologie Premium, IaaS Private a nodi, GPU H100 (dedicata e condivisa), storage a blocchi/NAS/object, sicurezza, backup e DR, AI, big data, housing, connettività, Secure Public Cloud (Oracle, Azure, Google), Hybrid Cloud. **Per completarlo serve il PDF o l'Excel originale del listino: se lo carichi, estraggo le tabelle per intero.**
  - PSN: VM Tiny con HA non incluso (valore non confermato). Il listino ha molte versioni (2024, 2025, gennaio e aprile 2026): riverificare a ogni release.
  - Aruba Enterprise: non incluse le voci Windows del Virtual Data Center, VPC 2.0 e Private Cloud VMware HPC, server dedicati senza GPU, backup (Commvault, Veeam), sicurezza (KMS), Plesk.
- [ ] **Passo 7 (ultimo): chiavi GCP e Hetzner.** Materiali pronti; restano le azioni tue (guida passo per passo in `GUIDA_CHIAVI.md`).
  - Pronti: `GUIDA_CHIAVI.md`; workflow **Verifica chiavi** (`.github/workflows/check-keys.yml` e `collectors/check_keys.py`) che controlla che i secret funzionino, senza mai stamparli, e spiega gli errori (chiave non valida, API non abilitata, restrizioni sbagliate, token revocato). Provato con risposte simulate, non con chiavi vere.
  - [ ] **Revocare la vecchia chiave Google** comparsa in passato in `status.json` (resta nella cronologia pubblica del repo): console Google → API e servizi → Credenziali → elimina.
  - [ ] Creare la nuova chiave Google limitata alla sola Cloud Billing API e salvarla come secret `GCP_API_KEY`.
  - [ ] (facoltativo) Token Hetzner di sola lettura come secret `HCLOUD_TOKEN`; poi eliminare `manual/hetzner.yml` per non avere doppioni. Senza token restano i 6 prezzi ufficiali del 15/06/2026, che non si aggiornano da soli.
  - [ ] Lanciare **Verifica chiavi**, poi **Aggiorna prezzi**, e controllare in `docs/data/status.json` le righe `gcp` e `hetzner`. Per GCP il punto meno sicuro sono i nomi delle SKU: se `gcp` risulta con 0 voci o con un errore, serve guardare il messaggio.
  - [ ] Dopo il primo run con GCP e OVHcloud: se OVHcloud mostra le GPU dal catalogo, eliminare `manual/gpuaas.yml` (fonti terze, doppioni).

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

## Voci rimosse al passo 3B (non verificabili: restano qui per traccia)
**Exoscale** (tabella fissa, Francoforte/Zurigo): Standard Medium 2/4 0,024 EUR/h (17,50/mese), Large 4/8 35,00, Extra-Large 8/16 70,00, Huge 16/32 140,00; Object Storage 0,011 EUR/GB/mese (valori diversi da quelli trovati: Medium 0,04666 EUR/h, Large 0,09333, Extra-large 0,18667, Huge 0,37334).
**Enter Cloud Suite**: OpenStack Standard 2/8 0,045 EUR/h (32,85/mese), 4/16 65,70, 8/32 131,40, 16/64 262,80; Block Storage SSD 0,08 EUR/GB/mese.
**Proxmox/VMware** (vecchio collector con ripiego): Community 120, Basic 370, Standard 1.020, Premium 2.040 EUR/socket/anno; PBS Basic; VMware VVF 190, VCF 350 e vDefend 200 "EUR"/core/anno (sono dollari, secondo le fonti).
