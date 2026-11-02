# Prezzi cloud: piano di correzione

Si procede un passo alla volta. Ogni passo concluso viene segnato qui e i punti ancora aperti restano in elenco.
Ultimo aggiornamento: 2026-11-02.

## Fatto
- [x] **Passo 1: Aruba e Seeweb allineati ai listini ufficiali.**
  - `collectors/aruba.py`: OpenStack Cloud Server (7 configurazioni, on-demand e annuale), GPU on Demand (L40S, RTX 4080 Super), Block Storage, disco aggiuntivo, traffico incluso. Fonte: cloud.it/prezzi, verificato il 2026-10-27.
  - `collectors/seeweb.py`: Cloud Shared CPU (7 taglie), High Memory (4), GPU (H100, A100, L40S, L4), on-demand e impegno 12 mesi (= "Impegno 1 anno"). Fonte: seeweb.it, verificato il 2026-11-02.
  - Eliminato il ripiego silenzioso `0,019 x vCPU` di Seeweb, che produceva prezzi inventati senza segnalarlo.
  - Nuovo `check_page()` in `common.py`: a ogni run controlla che la pagina ufficiale riporti ancora i prezzi della tabella; se no, lascia un avviso in `docs/data/status.json` (campo `note`). **Mai provato su rete reale: guardare il primo run.**
  - Rimossi i vecchi sconti a percentuale su Aruba (-20% e -35%): i prezzi annuali sono ora quelli ufficiali. Il 3 anni non esiste nel listino pubblico.

## Da fare, in ordine
- [ ] **Passo 2: prezzi "stimati" e sconti inventati** (AWS, Azure, GCP, Hetzner)
  - `aws.py`, `azure_cloud.py`, `gcp.py`: tabelle fisse, nei commenti AWS "stimato"; impegno 1 e 3 anni ottenuto con percentuali fisse (AWS 30/50%, Azure 28/48%, GCP 30/55%).
  - Obiettivo: tornare a leggere i prezzi reali dalle fonti (AWS Price List, Azure Retail Prices) e per GCP decidere tra Cloud Billing API (serve chiave) e valori verificati a mano.
  - Hetzner: la chiamata all'API prezzi è senza token (con ogni probabilità 401, errore ignorato), il riconoscimento delle taglie cerca nomi vecchi (`11`, `21`...), lo sconto 10% a 1 anno non esiste.
- [ ] **Passo 3: altri provider con tabelle fisse non verificate**: Oracle, Proxmox, DigitalOcean, Exoscale, Enter, STACKIT e i file `manual/` (gcp, ionos, scaleway, hetzner, ovh...). Per ognuno: fonte ufficiale, data di verifica, niente voci senza riscontro.
- [ ] **Passo 4: `run.py`, workflow e sicurezza**
  - Rimettere il controllo sui cali di record, come avviso e senza scartare i dati.
  - Applicare `sanitize()` anche a `status.json` e ai `print`; in `common.get` usare `raise ... from None`.
  - Togliere dal workflow i secret non più usati (`GCP_API_KEY`, `HCLOUD_TOKEN`).
  - **Revocare la chiave API Google** comparsa in passato in `status.json` (resta nella cronologia pubblica del repo).
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
