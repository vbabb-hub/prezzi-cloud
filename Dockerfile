FROM nginx:alpine

# Copia i file della PWA nella cartella standard di Nginx
COPY docs /usr/share/nginx/html

# Scriviamo direttamente una configurazione Nginx pulita che ascolta sulla porta 8080
RUN echo 'server { \
    listen 8080; \
    server_name localhost; \
    location / { \
        root /usr/share/nginx/html; \
        index index.html index.htm; \
    } \
}' > /etc/nginx/conf.d/default.conf

# Esponi la porta 8080 richiesta da Cloud Run
EXPOSE 8080

# Avvia Nginx
CMD ["nginx", "-g", "daemon off;"]
