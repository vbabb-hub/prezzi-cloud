# 1. Usa un server Nginx leggero per i file statici
FROM nginx:alpine

# 2. Copia i file della build della tua PWA nella cartella pubblica di Nginx
# (Assicurati che 'dist' o 'build' sia la cartella generata dal comando di build della tua app)
COPY dist /usr/share/nginx/html

# 3. Esponi la porta 80 (Cloud Run si aspetta traffico su questa porta)
EXPOSE 80

# 4. Avvia Nginx
CMD ["nginx", "-g", "daemon off;"]
