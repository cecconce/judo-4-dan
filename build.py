#!/usr/bin/env python3
"""Genera il sito statico dai file Markdown in content/.

Uso:  python3 build.py
Output: index.html, c/*.html, search.json, sw.js (nella radice del repo).
"""
import html
import json
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
OUT = ROOT / "c"
SITE = "Judo 4° Dan"
VERSION = "v1"


def slugify_title(md_text):
    m = re.search(r"^#\s+(.+)$", md_text, re.M)
    return m.group(1).strip() if m else "Senza titolo"


def load_chapters():
    chapters = []
    for p in sorted(CONTENT.glob("*.md")):
        text = p.read_text(encoding="utf-8")
        title = slugify_title(text)
        chapters.append({"file": p, "slug": p.stem, "title": title, "text": text})
    return chapters


def render(md_text):
    md = markdown.Markdown(
        extensions=["tables", "toc", "sane_lists"],
        extension_configs={"toc": {"toc_depth": "2-3", "permalink": False}},
    )
    # Il titolo H1 è già mostrato nell'header: lo togliamo dal corpo.
    body = re.sub(r"^#\s+.+\n", "", md_text, count=1, flags=re.M)
    body_html = md.convert(body)
    # tabelle scrollabili su telefono
    body_html = body_html.replace("<table>", '<div class="tw"><table>').replace(
        "</table>", "</table></div>"
    )
    return body_html, md.toc_tokens


def flatten_toc(tokens, level=0):
    for t in tokens:
        yield t["id"], t["name"], t["level"]
        yield from flatten_toc(t.get("children", []), level + 1)


PAGE = """<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#1f3a5f">
<title>{title} · {site}</title>
<link rel="manifest" href="{base}manifest.webmanifest">
<link rel="icon" href="{base}icon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="{base}icon.svg">
<link rel="stylesheet" href="{base}assets/style.css">
<script>try{{var t=localStorage.getItem('theme');if(t)document.documentElement.dataset.theme=t}}catch(e){{}}</script>
</head>
<body data-base="{base}">
<header class="top">
  <button id="menu-btn" aria-label="Menu" aria-expanded="false">☰</button>
  <a class="brand" href="{base}index.html">柔道 <span>{site}</span></a>
  <a class="icon-btn" href="{base}index.html#cerca" aria-label="Cerca">🔍</a>
  <button id="theme-btn" class="icon-btn" aria-label="Tema chiaro/scuro">◐</button>
</header>
<nav id="drawer" aria-label="Capitoli">
  <ol>
{nav}
  </ol>
</nav>
<div id="scrim" hidden></div>
<main>
{main}
</main>
<footer class="foot">
  Manuale di studio Pierluigi Ceccon · strumento di studio personale: la pratica sul tatami con il maestro resta il riferimento.
  Per date, quote e requisiti verifica sempre le circolari FIJLKAM dell'anno in corso.
</footer>
<script src="{base}assets/app.js"></script>
</body>
</html>
"""


def build():
    chapters = load_chapters()
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.html"):
        old.unlink()

    def nav_html(base, current=None):
        items = []
        for c in chapters:
            cls = ' class="cur"' if c["slug"] == current else ""
            items.append(
                f'    <li><a{cls} href="{base}c/{c["slug"]}.html">{html.escape(c["title"])}</a></li>'
            )
        return "\n".join(items)

    search = []
    for i, c in enumerate(chapters):
        body, toc = render(c["text"])
        c["body"] = body
        # indice di ricerca: una voce per sezione (h2)
        parts = re.split(r"(?m)^(##\s+.+)$", re.sub(r"^#\s+.+\n", "", c["text"], count=1, flags=re.M))
        intro = parts[0]
        sections = [("", intro)]
        for j in range(1, len(parts), 2):
            sections.append((parts[j].lstrip("# ").strip(), parts[j + 1] if j + 1 < len(parts) else ""))
        ids = {name: sid for sid, name, lvl in flatten_toc(toc)}
        for name, txt in sections:
            clean = re.sub(r"[*_`|#>-]+", " ", txt)
            clean = re.sub(r"\s+", " ", clean).strip()
            if not clean and not name:
                continue
            search.append(
                {
                    "c": c["slug"],
                    "ct": c["title"],
                    "s": name,
                    "id": ids.get(name, ""),
                    "t": clean,
                }
            )

    for i, c in enumerate(chapters):
        prev_c = chapters[i - 1] if i > 0 else None
        next_c = chapters[i + 1] if i < len(chapters) - 1 else None
        pager = '<div class="pager">'
        pager += (
            f'<a href="{prev_c["slug"]}.html">← {html.escape(prev_c["title"])}</a>'
            if prev_c
            else "<span></span>"
        )
        pager += (
            f'<a href="{next_c["slug"]}.html">{html.escape(next_c["title"])} →</a>'
            if next_c
            else "<span></span>"
        )
        pager += "</div>"
        main = f'<article>\n<h1>{html.escape(c["title"])}</h1>\n{c["body"]}\n</article>\n{pager}'
        (OUT / f'{c["slug"]}.html').write_text(
            PAGE.format(title=html.escape(c["title"]), site=SITE, base="../", nav=nav_html("../", c["slug"]), main=main),
            encoding="utf-8",
        )

    # home
    cards = "\n".join(
        f'<li><a href="c/{c["slug"]}.html"><b>{html.escape(c["title"])}</b></a></li>' for c in chapters
    )
    home = f"""<section class="hero">
<h1>柔道 · Manuale di studio per il 4° Dan</h1>
<p>Storia, filosofia e tecniche del judo, Gokyō completo, Katame-waza, Renraku, Gaeshi e Difese, glossario.
Pensato per lo studio da telefono, anche offline.</p>
</section>
<section id="cerca">
<input id="q" type="search" placeholder="Cerca (es. uchi-mata, kuzushi, 1895…)" autocomplete="off" aria-label="Cerca nel manuale">
<ul id="results" class="results"></ul>
</section>
<section>
<h2>Capitoli</h2>
<ol class="chapters">
{cards}
</ol>
</section>
<section class="note">
<p><b>Come usarlo sul telefono.</b> Apri il sito, poi dal menu del browser scegli «Aggiungi a schermata Home»:
si comporta come un'app e, dopo la prima visita, funziona anche senza rete.</p>
</section>"""
    (ROOT / "index.html").write_text(
        PAGE.format(title="Home", site=SITE, base="", nav=nav_html("", None), main=home),
        encoding="utf-8",
    )

    (ROOT / "search.json").write_text(json.dumps(search, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")

    precache = (
        ["./", "index.html", "search.json", "assets/style.css", "assets/app.js", "manifest.webmanifest", "icon.svg"]
        + [f"c/{c['slug']}.html" for c in chapters]
        + sorted(f"assets/img/{f.name}" for f in (ROOT / "assets" / "img").glob("*") if f.is_file())
    )
    sw = f"""const CACHE = 'judo4dan-{VERSION}-{len(chapters)}-{sum(len(c['text']) for c in chapters)}';
const FILES = {json.dumps(precache)};
self.addEventListener('install', e => {{
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
}});
self.addEventListener('activate', e => {{
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
}});
self.addEventListener('fetch', e => {{
  if (e.request.method !== 'GET') return;
  e.respondWith(
    caches.match(e.request).then(hit => hit || fetch(e.request).then(r => {{
      const copy = r.clone();
      caches.open(CACHE).then(c => c.put(e.request, copy));
      return r;
    }}))
  );
}});
"""
    (ROOT / "sw.js").write_text(sw, encoding="utf-8")
    print(f"OK: {len(chapters)} capitoli, {len(search)} voci di ricerca")


if __name__ == "__main__":
    build()
