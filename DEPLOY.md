# Pubblicazione su Cloud Run

La pagina (`docs/`) è servita da nginx senza privilegi, sulla porta 8080 richiesta da Cloud Run. Ci sono due modi di pubblicarla: GitHub Pages (già attivo, si aggiorna da solo) e questo container.

## Cosa fa il container
- Immagine `nginxinc/nginx-unprivileged` (non gira come root), versione fissata.
- Intestazioni di sicurezza su ogni risposta: Content-Security-Policy restrittiva (solo file della stessa origine), HSTS, `nosniff`, `X-Frame-Options`, `Referrer-Policy`, `Permissions-Policy`.
- Cache sempre da rivalidare per pagina, dati e `sw.js` (si usa l'ETag): i dati giornalieri e il service worker non restano vecchi nel browser. Solo `icon.svg` resta in cache un giorno.
- gzip per testo, JSON e SVG; manifest con il tipo giusto; file nascosti non raggiungibili; solo GET e HEAD.
- Nell'immagine non entra `docs/data/history` (la pagina non lo usa e cresce ogni giorno).

## Il punto importante: i dati sono dentro l'immagine
Il workflow aggiorna ogni giorno `docs/data/` su GitHub, ma Cloud Run continua a servire i dati dell'ultima immagine costruita. Serve quindi ricostruire l'immagine dopo ogni aggiornamento. Due modi, entrambi con Cloud Build.

### A. Trigger a ogni push su `main` (consigliato)
1. Console Google Cloud → Cloud Build → Trigger → Crea trigger.
2. Evento: push su un ramo; repository: collega `prezzi-cloud` da GitHub; ramo `^main$`.
3. Configurazione: file di Cloud Build, percorso `cloudbuild.yaml`.
4. Filtro file inclusi: `docs/**, Dockerfile, nginx/**, cloudbuild.yaml` (così non si ricostruisce per modifiche al solo codice dei collector).
5. Se cambiano i nomi, correggi le variabili `_REGION`, `_SERVICE`, `_REPO` del trigger.

**Verifica dopo il primo run del workflow giornaliero**: in Cloud Build → Cronologia deve comparire una build. I commit fatti dal workflow di GitHub non fanno ripartire altri workflow di GitHub, ma dovrebbero far partire il trigger di Cloud Build; non l'ho potuto verificare. Se la build non parte, usa il modo B.

### B. Ricostruzione programmata ogni giorno
Crea un trigger manuale con la stessa configurazione e fallo eseguire da Cloud Scheduler un'ora dopo il workflow (che gira alle 04:17 UTC), per esempio alle 06:00 UTC. Non dipende dagli eventi di GitHub.

## Prerequisiti
- Un repository di Artifact Registry nella regione (`_REPO`, di solito `cloud-run-source-deploy` se hai già pubblicato da sorgente). Altrimenti: `gcloud artifacts repositories create NOME --repository-format=docker --location=europe-west1`.
- L'account di servizio di Cloud Build deve avere i ruoli *Cloud Run Admin*, *Service Account User* e *Artifact Registry Writer*.
- `cloudbuild.yaml` pubblica con `--allow-unauthenticated` (sito pubblico, come ora). Toglilo se vuoi un accesso privato.

## Prova in locale
```
docker build -t prezzi-cloud .
docker run --rm -p 8080:8080 prezzi-cloud
```
Poi apri http://localhost:8080 (il service worker richiede HTTPS o localhost).

## Aggiornare subito a mano
```
gcloud builds submit --config cloudbuild.yaml .
```
