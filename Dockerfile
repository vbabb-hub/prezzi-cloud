# 1. Usa un server Nginx leggero
FROM nginx:alpine

# 2. Copia l'intera cartella 'docs' (che contiene index.html e gli altri asset) nella cartella pubblica di Nginx
COPY docs /usr/share/nginx/html

# 3. Esponi la porta 80 per Cloud Run
EXPOSE 80

# 4. Avvia Nginx
CMD ["nginx", "-g", "daemon off;"]
