const CACHE = 'judo4dan-v8-20-380753';
const FILES = ["./", "index.html", "quiz.html", "assets/quiz.js", "assets/quiz.json", "search.json", "assets/style.css", "assets/app.js", "manifest.webmanifest", "icon.svg", "c/01-storia.html", "c/02-filosofia.html", "c/03-fondamenti.html", "c/04-classificazione.html", "c/05-dai-ikkyo.html", "c/06-dai-nikyo.html", "c/07-dai-sankyo.html", "c/08-dai-yonkyo.html", "c/09-dai-gokyo.html", "c/10-katame-waza.html", "c/11-renraku-gaeshi-difese.html", "c/12-glossario.html", "c/13-kime-no-kata.html", "c/14-goshin-jutsu.html", "c/15-fijlkam.html", "c/16-suddivisione-tecnica.html", "c/17-memorizzazione.html", "c/18-difese-go-chowa-yawara.html", "c/19-sen-go-no-sen.html", "c/20-video.html", "assets/img/goshin-rId103.jpg", "assets/img/goshin-rId106.jpg", "assets/img/goshin-rId20.jpg", "assets/img/goshin-rId39.jpg", "assets/img/goshin-rId47.jpg", "assets/img/goshin-rId51.jpg", "assets/img/goshin-rId55.jpg", "assets/img/goshin-rId59.jpg", "assets/img/goshin-rId64.jpg", "assets/img/goshin-rId68.jpg", "assets/img/goshin-rId75.jpg", "assets/img/goshin-rId84.jpg", "assets/img/goshin-rId88.jpg", "assets/img/goshin-rId92.jpg", "assets/img/goshin-rId95.jpg", "assets/img/goshin-rId99.jpg", "assets/img/m-rId10.jpg", "assets/img/m-rId11.jpg", "assets/img/m-rId12.jpg", "assets/img/m-rId13.jpg", "assets/img/m-rId14.jpg", "assets/img/m-rId15.jpg", "assets/img/m-rId16.jpg", "assets/img/m-rId17.jpg", "assets/img/m-rId18.jpg", "assets/img/m-rId19.jpg", "assets/img/m-rId20.jpg", "assets/img/m-rId21.jpg", "assets/img/m-rId22.jpg", "assets/img/m-rId23.jpg", "assets/img/m-rId24.jpg", "assets/img/m-rId25.jpg", "assets/img/m-rId26.jpg", "assets/img/m-rId27.jpg", "assets/img/m-rId28.jpg", "assets/img/m-rId29.jpg", "assets/img/m-rId30.jpg", "assets/img/m-rId31.jpg", "assets/img/m-rId32.jpg", "assets/img/m-rId33.jpg", "assets/img/m-rId34.jpg", "assets/img/m-rId35.jpg", "assets/img/m-rId36.jpg", "assets/img/m-rId37.jpg", "assets/img/m-rId38.jpg", "assets/img/m-rId39.jpg", "assets/img/m-rId40.jpg", "assets/img/m-rId41.jpg", "assets/img/m-rId42.jpg", "assets/img/m-rId43.jpg", "assets/img/m-rId44.jpg", "assets/img/m-rId45.jpg", "assets/img/m-rId46.jpg", "assets/img/m-rId47.jpg", "assets/img/m-rId48.jpg", "assets/img/m-rId49.jpg", "assets/img/m-rId50.jpg", "assets/img/m-rId51.jpg", "assets/img/m-rId52.jpg", "assets/img/m-rId53.jpg", "assets/img/m-rId54.jpg", "assets/img/m-rId55.jpg", "assets/img/m-rId56.jpg", "assets/img/m-rId57.jpg", "assets/img/m-rId58.jpg", "assets/img/m-rId59.jpg", "assets/img/m-rId60.jpg", "assets/img/m-rId61.jpg", "assets/img/m-rId62.jpg", "assets/img/m-rId63.jpg", "assets/img/m-rId64.jpg", "assets/img/m-rId65.jpg", "assets/img/m-rId66.jpg", "assets/img/m-rId67.jpg", "assets/img/m-rId68.jpg", "assets/img/m-rId69.jpg", "assets/img/m-rId7.jpg", "assets/img/m-rId70.jpg", "assets/img/m-rId71.jpg", "assets/img/m-rId72.jpg", "assets/img/m-rId73.jpg", "assets/img/m-rId74.jpg", "assets/img/m-rId75.jpg", "assets/img/m-rId8.jpg", "assets/img/m-rId9.jpg"];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => Promise.all(FILES.map(u => fetch(u, {cache: 'reload'}).then(r => { if (!r.ok) throw new Error(u); return c.put(u, r); })))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  const u = new URL(e.request.url);
  if (u.origin !== location.origin) return;
  const isImg = /\.(jpe?g|png|webp|gif|svg)$/i.test(u.pathname) && u.pathname.includes('/assets/img/');
  if (isImg) {
    e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request).then(r => {
      const copy = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); return r;
    })));
    return;
  }
  // pagine, script, dati: prima la rete (contenuto aggiornato), poi la copia offline
  e.respondWith(
    fetch(e.request, {cache: 'no-cache'}).then(r => {
      if (r.ok) { const copy = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); }
      return r;
    }).catch(() => caches.match(e.request, {ignoreSearch: true}).then(hit => hit || caches.match('index.html')))
  );
});
