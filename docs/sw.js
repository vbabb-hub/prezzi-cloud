const V = "v4";
self.addEventListener("install", e => e.waitUntil(caches.open(V).then(c => c.addAll(["./","index.html","app.js","style.css","manifest.webmanifest","icon.svg"])).then(() => self.skipWaiting())));
self.addEventListener("activate", e => e.waitUntil(caches.keys().then(k => Promise.all(k.filter(x => x !== V).map(x => caches.delete(x)))).then(() => clients.claim())));
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET" || new URL(e.request.url).origin !== location.origin) return;
  // rete prima, cache se offline: i prezzi sono sempre quelli più recenti disponibili
  e.respondWith(fetch(e.request).then(r => { const c = r.clone(); caches.open(V).then(x => x.put(e.request, c)); return r; }).catch(() => caches.match(e.request)));
});
