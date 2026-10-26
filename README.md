# Prezzi cloud: confronto giornaliero

GitHub Actions raccoglie i prezzi ogni giorno e li salva in `docs/data/`; GitHub Pages serve la PWA da `docs/`. Tutto gratuito.

## Attivazione (una tantum)
1. Crea un repo su GitHub e fai push di questa cartella.
2. Settings → Pages → *Deploy from a branch* → `main`, cartella `/docs`.
3. Settings → Actions → General → Workflow permissions → *Read and write*.
4. Settings → Secrets → Actions: `HCLOUD_TOKEN` = token API (sola lettura) di un progetto Hetzner gratuito.
5. Secret `GCP_API_KEY`: in Google Cloud Console crea un progetto (gratuito), abilita *Cloud Billing API* e crea una API key.
6. Actions → *Aggiorna prezzi* → Run workflow. Poi gira da solo ogni giorno (04:17 UTC).

## Storico
- `latest.json`: prezzi correnti. `series.json`: per ogni voce solo i punti in cui il prezzo cambia. `history/AAAA-MM-GG.json`: snapshot giornaliero. In più c'è la cronologia git.
- Se una fonte fallisce restano gli ultimi dati noti, marcati "non aggiornato"; lo stato è in `status.json`.

## Fonti
Automatiche, compute + storage + rete: Azure (Retail Prices API), AWS (bulk Price List), GCP (Cloud Billing Catalog), OVHcloud (catalogo IT, rete esclusa), Hetzner (API + token).
Storage non omogeneo: AWS = EBS gp3 (block), Azure = Blob Hot LRS (object), GCP = PD Balanced (block), OVH/Hetzner = block. Il nome della voce lo dice.
Manuali (`manual/*.yml`): Aruba, IONOS, Proxmox, VMware, Nutanix, GPUaaS. Compila `price`, `source`, `verified`.
Object storage: AWS S3 Standard, GCP Cloud Storage Standard, Azure Blob Hot LRS e OVH (automatici); Hetzner, Aruba e IONOS da compilare in `manual/`. Non ancora presente: block storage Azure (i managed disk costano a taglia, non per GB). La rete OVH è esclusa (traffico in genere incluso: da inserire a mano).

## Da verificare al primo run
I collector non sono stati provati contro le API reali: controlla i log di Actions. Punti fragili: formato prezzi del catalogo OVH, RAM Azure (stimata: D=4, E=8, F=2 GB/vCPU), SKU GCP N2 (nomi delle descrizioni) e scaglioni egress GCP/AWS/Azure, conversione OVH dei volumi, peso del file AWS (oltre 100 MB per regione).
Prezzi in EUR di listino, IVA esclusa; AWS convertito da USD col cambio del giorno; mese = 730 ore.
