// Simpan kerangka aplikasi supaya cepat dibuka lagi dan tetap tampil saat sinyal lemah.
// Data buku (/api) dan file media selalu diambil dari server.
const CACHE = "bk-v1";
const KERANGKA = ["/style.css", "/app.js", "/ikon.svg", "/manifest.webmanifest"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(KERANGKA)));
  self.skipWaiting();
});

self.addEventListener("activate", (e) => {
  e.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
  );
  self.clients.claim();
});

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.origin !== location.origin) return;
  if (url.pathname.startsWith("/api/") || url.pathname.startsWith("/media/")) return;
  // Jaringan dulu, cadangan dari cache kalau sedang tidak ada sinyal.
  e.respondWith(
    fetch(e.request)
      .then((res) => {
        if (res.ok) {
          const salinan = res.clone();
          caches.open(CACHE).then((c) => c.put(e.request, salinan));
        }
        return res;
      })
      .catch(() => caches.match(e.request))
  );
});
