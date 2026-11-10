# Pagina statica servita da nginx senza privilegi (non root), pronta per Cloud Run sulla porta 8080.
FROM nginxinc/nginx-unprivileged:1.27-alpine

# I dati (docs/data) sono compresi nell'immagine: serve ricostruirla a ogni aggiornamento, vedi README.md (Cloud Build).
COPY docs/ /usr/share/nginx/html/
COPY nginx/default.conf /etc/nginx/conf.d/default.conf
COPY nginx/security-headers.conf /etc/nginx/security-headers.conf

EXPOSE 8080
