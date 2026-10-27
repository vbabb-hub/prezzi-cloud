const V = "v8";
self.addEventListener("install", e => e.waitUntil(caches.open(V).then(c => c.addAll(["./","index.html","app.js","style.css","manifest.webmanifest","icon.svg"])).then(() => self.skipWaiting())));
self.addEventListener("activate", e => e.waitUntil(caches.keys().then(k => Promise.all(k.filter(x => x !== V).map(x => caches.delete(x)))).then(() => clients.claim())));
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET" || new URL(e.request.url).origin !== location.origin) return;
  // rete prima (saltando la cache HTTP, che su GitHub Pages dura 10 minuti), cache solo se offline
  e.respondWith(fetch(e.request.url, {cache: "no-cache"}).then(r => { const c = r.clone(); caches.open(V).then(x => x.put(e.request, c)); return r; }).catch(() => caches.match(e.request)));
});
