#!/usr/bin/env python3
"""Ambil data reka bentuk templat Canva 'ainaiman' ke tools/cache/.

    python3 tools/ambil.py

Menulis:
  cache/design.json   data reka bentuk (page.A = dokumen, page.I = manifes)
  cache/raw/          media + fon (varian terbesar sahaja)

Data reka bentuk ada dalam `window['bootstrap'] = JSON.parse('…')` pada HTML
halaman. Skrip itu dijalankan dalam `vm` node yang terasing dengan objek
`window` palsu — tiada kod Canva lain yang dijalankan.

Gambar peribadi pasangan asal (jalur gambar) SENGAJA tidak dimuat turun.
Cache ini tidak di-commit (lihat .gitignore).
"""
import json, os, subprocess, sys, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
RAW = os.path.join(CACHE, "raw")
URL = "https://jemputku.my.canva.site/ainaiman/page-2"
BASE = "https://jemputku.my.canva.site/ainaiman/"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/126 Safari/537.36"}

# jalur gambar pasangan asal (3 foto + 1 foto sejambak bertulis nama mereka)
PERIBADI = {"MAHM5R-uEKA", "MAHM5ZniLWU", "MAHM5eat8aU", "MAHM5et3WHQ"}

EKSTRAK_JS = r"""
const fs = require('fs'), vm = require('vm');
const h = fs.readFileSync(process.argv[1], 'utf8');
const s = [...h.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g)].map(x => x[1])
          .find(x => x.includes("window['bootstrap']"));
if (!s) { console.error('bootstrap tiada'); process.exit(1); }
const ctx = { window: {} }; vm.createContext(ctx);
vm.runInContext(s, ctx, { timeout: 5000 });
process.stdout.write(JSON.stringify({ page: ctx.window.bootstrap.page }));
"""


def main():
    os.makedirs(RAW, exist_ok=True)
    html = urllib.request.urlopen(urllib.request.Request(URL, headers=UA), timeout=60).read()
    hp = os.path.join(CACHE, "page.html")
    open(hp, "wb").write(html)
    out = subprocess.run(["node", "-e", EKSTRAK_JS, hp], capture_output=True, check=True).stdout
    open(os.path.join(CACHE, "design.json"), "wb").write(out)
    D = json.loads(out)
    MAN = D["page"]["I"]

    urls = set()
    for e in MAN["B"] + D["page"].get("E", []):
        if not (isinstance(e, dict) and e.get("id") and e.get("files")) or e["id"] in PERIBADI:
            continue
        urls.add(max(e["files"], key=lambda f: f.get("width") or 0)["url"])
    for fe in MAN["A"]:
        for s in fe["D"]:
            for f in s.get("files", []):
                urls.add(f["url"])

    # Rama-rama templat ialah video; gambar posternya PNG lutsinar dan itulah
    # yang dipakai (bina.py: render_kupu). Disimpan dengan nama tetap.
    for v in D["page"].get("F", []):
        if isinstance(v, dict) and v.get("posterframes"):
            poster = urllib.parse.urljoin(BASE, v["posterframes"][0]["A"])
            data = urllib.request.urlopen(urllib.request.Request(poster, headers=UA), timeout=60).read()
            open(os.path.join(RAW, "kupu-poster.png"), "wb").write(data)

    def ambil(u):
        full = urllib.parse.urljoin(BASE, u)
        dst = os.path.join(RAW, os.path.basename(urllib.parse.urlparse(full).path))
        if os.path.exists(dst):
            return "ada"
        data = urllib.request.urlopen(urllib.request.Request(full, headers=UA), timeout=60).read()
        open(dst, "wb").write(data)
        return "ok"

    with ThreadPoolExecutor(8) as ex:
        hasil = list(ex.map(ambil, sorted(urls)))
    print(f"design.json + {hasil.count('ok')} fail baharu ({hasil.count('ada')} sedia ada) -> {RAW}")


if __name__ == "__main__":
    sys.exit(main())
