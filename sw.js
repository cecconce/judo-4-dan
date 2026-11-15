const CACHE = 'judo4dan-v1-12-197645';
const FILES = ["./", "index.html", "search.json", "assets/style.css", "assets/app.js", "manifest.webmanifest", "icon.svg", "c/01-storia.html", "c/02-filosofia.html", "c/03-fondamenti.html", "c/04-classificazione.html", "c/05-dai-ikkyo.html", "c/06-dai-nikyo.html", "c/07-dai-sankyo.html", "c/08-dai-yonkyo.html", "c/09-dai-gokyo.html", "c/10-katame-waza.html", "c/11-renraku-gaeshi-difese.html", "c/12-glossario.html"];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    caches.match(e.request).then(hit => hit || fetch(e.request).then(r => {
      const copy = r.clone();
      caches.open(CACHE).then(c => c.put(e.request, copy));
      return r;
    }))
  );
});
