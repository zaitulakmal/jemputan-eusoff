#!/usr/bin/env python3
"""Bina kad Walimatul Urus Eusoff daripada templat Canva 'ainaiman'.

    python3 tools/ambil.py     # sekali: ambil data reka bentuk + media ke tools/cache/
    python3 tools/bina.py      # jana index.html + assets/kad/

Klon tepat: setiap elemen Canva diletakkan pada koordinat asalnya dalam
kanvas 1366px yang diskala mengikut lebar skrin (sama seperti kad Zaitul).
Perbezaan yang disengajakan:
  - palet maroon + hijau zaitun -> nude + biru (tools/warna.py)
  - jalur gambar pasangan asal -> gambar Eusoff & Zaitul (tidak diwarnakan semula)
  - rama-rama video -> rama-rama PNG yang mengepak
  - kiraan detik & kalendar dibina semula secara natif
  - borang RSVP codelet Canva -> borang sendiri (tools/shell.html)
"""
import calendar, hashlib, html as H, io, json, math, os, re, sys

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import images as IMG                                     # noqa: E402
import warna                                             # noqa: E402

CACHE = os.path.join(HERE, "cache")
RAW = os.path.join(CACHE, "raw")
OUTA = os.path.join(ROOT, "assets", "kad")

# ═══ KANDUNGAN ════════════════════════════════════════════════════════════
# Penggantian teks, dikunci pada laluan elemen ("halaman:indeks[.anak]").
# Setiap pasangan (lama, baharu) mesti wujud dalam teks asal — kalau templat
# berubah, pembinaan gagal dengan jelas dan bukan diam-diam tertinggal.
TARIKH = (2027, 3, 20)
GANTI = {
    "0:4":    [("Ain & Aiman", "Eusoff & Zaitul")],
    "1:11":   [("A\nA", "E\nZ")],                               # monogram sampul
    "1:12":   [("Ain \n&\nAiman", "Eusoff\n&\nZaitul")],        # bingkai bujur
    "1:18":   [("Julai", "Mac")],
    "1:19":   [("18", "20")],
    "1:20":   [("11.00 am - 4.00 pm", "11.30 am - 4.00 pm")],
    "1:21":   [("Dataran Gangsa", "Asiana Grand Hall")],
    "1:22.2": [("Ainman", "EusoffZaitul")],
    "1:17.3": [("Adi Sazlizan bin Saklan", "Zainin Bin Shah Bahari"),
               ("Norzalina binti Zainal", "Liza Aryani Binti Sinin")],
    "1:17.9": [("majlis perkahwinan puteri kami.", "Majlis Walimatul Urus putera kami.")],
    # nama penuh pengantin belum diberi — nama pendek dahulu, lelaki dahulu
    "1:17.7": [("Nur Ain binti Adi Sazlizan", "Eusoff"),
               ("Aiman Afzan bin \nMohd Shukri", "Zaitul")],
    "1:9.2":  [("019-7921196 \n(Adi - Bapa pengantin)", "+60 13-505 2077\n(En. Zainin)"),
               ("017-6121165 \n(Zalina - Ibu pengantin)", "+60 19-679 4624\n(En. Azhar)")],
}
# lebar maksimum (px kanvas) bagi teks yang ditukar — dikecilkan pada masa
# jalan kalau melebihi (tools/shell.html, muatTeks)
# 1:21 lebih sempit: bunga kala lili lencana menindih tepi kiri kad tarikh
# 1:16.8 (aturcara): baris terpanjang mesti tidak mencecah ikon di kirinya
MUAT = {"0:4": 560, "1:12": 132, "1:18": 250, "1:20": 250, "1:21": 180, "1:16.8": 185,
        "1:22.2": 150, "1:9.2": 170, "1:17.3": 250, "1:17.7": 330}
# kotak teks yang dilebarkan sama rata dari tengah (kotak asal selebar "Ain")
LEBARKAN = {"1:12": 150}
TEPI = 20          # ruang (px kanvas) di kiri & kanan kandungan pada telefon

# Pelarasan halus kedudukan (px kanvas), diukur daripada render sebenar.
# Nama pengantin kita jauh lebih pendek daripada nama dalam templat, jadi
# "dan pilihan hatinya" tidak lagi jatuh di tengah antara dua nama.
GESER_Y = {"1:24": 19.3}

# Aturcara belum diberi -> kad "Tentatives" (kumpulan 1:16) disembunyikan dan
# segala di bawahnya dinaikkan ke tempatnya.
ATURCARA = [("11.30 am", "Ketibaan tetamu & jamuan"),
            ("12.30 pm", "Ketibaan pengantin"),
            ("1.00 pm", "Bacaan doa"),
            ("1.15 pm", "Memotong kek & sesi bergambar"),
            ("4.00 pm", "Majlis bersurai")]
SEMBUNYI_ATURCARA = "1:16"
# Kad aturcara templat direka untuk 5 acara dan 4 ikon. Satu ikon bagi setiap
# acara (ikut urutan); ikon selebihnya disembunyikan.
TEKS_ATURCARA = "1:16.8"
# ikon bagi setiap acara ikut indeks
IKON_ATURCARA = {0: "1:16.3",                  # kereta   -> ketibaan tetamu
                 1: "1:16.4",                  # pasangan -> ketibaan pengantin
                 3: "1:16.5",                  # kek      -> memotong kek
                 4: "1:16.6"}                  # merpati  -> bersurai
# Templat hanya ada 4 ikon. Ikon tambahan (SVG lukisan sendiri, gaya garis sama)
# diletak di tengah antara dua ikon templat: (fail, ikon atas, ikon bawah, lebar px kanvas).
IKON_TAMBAHAN = [("tools/ikon/doa.svg", "1:16.4", "1:16.5", 44.0)]   # bacaan doa (17 Sep 2026)
IKON_SEMUA = ["1:16.3", "1:16.4", "1:16.5", "1:16.6"]
BARIS_KOSONG_ATURCARA = 1                      # jarak antara acara (sama dengan templat)
# teks yang diganti keseluruhannya (bukan sebahagian) — dijana dalam main()
GANTI_PENUH = {}
# geseran menegak (px kanvas) bagi elemen dalam kumpulan, diukur dari render
# Diukur 17 Sep 2026: teks dipusatkan dalam ruang bawah tajuk "Tentatives";
# setiap ikon dijajarkan dengan titik tengah acaranya.
GESER_ANAK_Y = {"1:16.8": 17.0,                          # 5 acara melimpah kotak asal; turun ke bawah tajuk
                "1:16.3": -16.0, "1:16.4": -15.8,        # ikon -> tengah acara (diukur 17 Sep 2026)
                "1:16.5": 63.9, "1:16.6": 63.4}
# Renda kad aturcara (451..989) lebih lebar daripada kandungan lain. Kalau
# dikira, seluruh kad mengecil ~12% di telefon; biar ia terkeluar sedikit.
TIDAK_DIKIRA_SEMPADAN = {"1:16"}

# ═══ WARNA ═════════════════════════════════════════════════════════════════
NUDE, BIRU_TUA, BIRU = warna.NUDE, warna.BIRU_TUA, warna.BIRU
LATAR_ASAL = "#521d1f"
# warna sasaran peta pewarnaan Canva -> palet baharu
PETA = {"#919359": BIRU, "#521d1f": BIRU_TUA, "#5b191a": BIRU_TUA, "#6c2118": BIRU_TUA,
        "#67282b": BIRU, "#927f61": BIRU, "#42353d": BIRU_TUA}
# hiasan putih yang duduk terus atas latar (kini nude) -> biru tua
PUTIH_JADI_BIRU = {"1:7.0", "1:7.1", "1:14"}
# teks putih yang duduk atas panel gelap (gerbang, skrol RSVP, lencana,
# bingkai "Open") — kekal putih; teks putih lain atas latar -> biru tua
TEKS_KEKAL_PUTIH = {"0:5", "1:11", "1:15.1", "1:15.2", "1:17.3", "1:17.7", "1:17.8",
                    "1:17.9", "1:22.2", "1:23", "1:24"}

# ═══ ELEMEN KHAS ═══════════════════════════════════════════════════════════
LANGKAU = {"1:5",     # butang anak panah lutsinar (tak kelihatan dalam asal)
           "1:25",    # benaman YouTube tersembunyi — piring hitam jadi pemicu
           "0:0",     # bingkai renda butang "Open"
           "0:5"}     # teks "Open" — seluruh muka depan sudah boleh ditekan
KALENDAR = "1:7.2"    # imej kalendar Julai -> kalendar natif bulan majlis
KIRAAN = "1:8"        # benaman kiraan detik luar -> natif
PIRING = "1:3"
RUMAH = "1:14"
PAUTAN_RSVP = "1:15.1"
DEKOR_JALUR = "MAHLS8GHFHg"   # jurai bunga templat (ganti kalau gambar tak cukup)
# Gambar jalur, dari atas ke bawah. `fokus` = titik tengah potongan mendatar
# (0 = tepi kiri, 1 = tepi kanan) supaya muka tidak terpotong bila gambar
# melintang dipotong kepada sel menegak.
GAMBAR = [("assets/gambar/1.jpg", 0.50),
          ("assets/gambar/3.jpg", 0.50),     # tangan bercincin
          ("assets/gambar/2.jpg", 0.50),     # pasangan berdiri
          ("assets/gambar/4.jpg", 0.55)]
KRIM_JALUR = "#f8f1e9"

# ═══ DATA REKA BENTUK ═════════════════════════════════════════════════════
D = json.load(open(os.path.join(CACHE, "design.json")))
DOC, MAN = D["page"]["A"], D["page"]["I"]

MEDIA, SPRITE = {}, {}
for m in MAN["B"] + D["page"].get("E", []):
    if isinstance(m, dict) and m.get("id") and m.get("files"):
        MEDIA.setdefault(m["id"], []).extend(m["files"])
        if m.get("spritesheetMetadata"):
            SPRITE[m["id"]] = m["spritesheetMetadata"]

CSSFONT = {"YAFdJhem5V8": "kad-playfair", "YAFdJhX-538": "kad-cormorant",
           "YAFcf-RMpoo": "kad-snell", "YACgEfb36U4": "kad-bodoni",
           "YAFcf5Qrkvs": "kad-citadel", "YAE2gr0Mbng": "kad-alexbrush",
           "YACgEZ1cb1Q": "kad-arimo"}
SANDARAN = {"kad-playfair": "Georgia,serif", "kad-cormorant": "Georgia,serif",
            "kad-snell": "'Apple Chancery',cursive", "kad-bodoni": "Didot,Georgia,serif",
            "kad-citadel": "cursive", "kad-alexbrush": "cursive", "kad-arimo": "Arial,sans-serif"}
FONFAIL = {fe["A"]: {s["style"]: s["files"][0]["url"] for s in fe["D"] if s.get("files")}
           for fe in MAN["A"]}
METRIK = {}
for fe in MAN["A"]:
    md = fe["D"][0].get("metadata") or {}
    em = (md.get("head") or {}).get("unitsPerEm")
    hh = md.get("hhea") or {}
    if em:
        METRIK[fe["A"]] = (hh.get("ascender", em) - hh.get("descender", 0)) / em
FON_GUNA = {("YAFdJhem5V8", False, False), ("YAFdJhem5V8", True, False),
            ("YAFdJhem5V8", False, True), ("YAFdJhX-538", False, False),
            ("YAFdJhX-538", True, True), ("YAFcf-RMpoo", False, False),
            ("YACgEfb36U4", False, False), ("YACgEfb36U4", False, True)}   # kalendar


def fam(fid):
    n = CSSFONT.get(fid, "kad-cormorant")
    return f"'{n}',{SANDARAN[n]}"


# ═══ ASET IMEJ ═════════════════════════════════════════════════════════════
_aset = {}


def simpan(im, lebar):
    """Simpan WebP bernama hash isi (aset dihantar dengan cache 'immutable')."""
    lebar = max(48, min(im.width, int(math.ceil(lebar))))
    if im.width > lebar:
        im = im.resize((lebar, max(1, round(im.height * lebar / im.width))), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=88, method=6)
    raw = buf.getvalue()
    nama = hashlib.md5(raw).hexdigest()[:12] + ".webp"
    with open(os.path.join(OUTA, nama), "wb") as fh:
        fh.write(raw)
    return nama


def buka_media(mid, peta):
    best = max(MEDIA[mid], key=lambda f: f.get("width") or 0)
    src = os.path.join(RAW, os.path.basename(best["url"]))
    if mid in SPRITE:
        im = IMG.compose_spritesheet(src, SPRITE[mid], peta)
    else:
        im = Image.open(src).convert("RGBA")
    return warna.nude_biru(im)


def aset(mid, peta, lebar_papar):
    kunci = (mid, tuple(sorted(peta.items())))
    ada = _aset.get(kunci)
    if ada and ada[1] >= lebar_papar * 2:
        return ada[0]
    nama = simpan(buka_media(mid, peta), lebar_papar * 2)
    _aset[kunci] = (nama, lebar_papar * 2)
    return nama


def gambar_jalur(spec, nisbah, lebar):
    """Potong gambar pengantin kepada nisbah sel jalur (lebar/tinggi).

    Gambar TIDAK melalui warna.nude_biru — hanya hiasan templat yang
    diwarnakan semula; muka dan baju mesti kekal warna asal.
    """
    fail, fokus = spec
    im = Image.open(os.path.join(ROOT, fail)).convert("RGB")
    lp = min(im.width, im.height * nisbah)
    tp = lp / nisbah
    cx = min(max(im.width * fokus, lp / 2), im.width - lp / 2)
    cy = im.height / 2
    im = im.crop((round(cx - lp / 2), round(cy - tp / 2), round(cx + lp / 2), round(cy + tp / 2)))
    return simpan(im.convert("RGBA"), lebar)


def panel_bunga(nisbah, cermin, lebar):
    """Panel krim bernisbah sel jalur dengan jurai bunga di tengahnya."""
    W = 600
    Hh = round(W * nisbah)
    panel = Image.new("RGBA", (W, Hh), warna.hex_rgb(KRIM_JALUR) + (255,))
    bunga = buka_media(DEKOR_JALUR, {})
    bunga = bunga.crop(bunga.getbbox())
    skala = min(W * 0.92 / bunga.width, Hh * 0.92 / bunga.height)
    bunga = bunga.resize((round(bunga.width * skala), round(bunga.height * skala)), Image.LANCZOS)
    if cermin:
        bunga = bunga.transpose(Image.FLIP_LEFT_RIGHT)
    panel.alpha_composite(bunga, ((W - bunga.width) // 2, (Hh - bunga.height) // 2))
    return simpan(panel, lebar)


def tukar_warna(laluan, sasaran):
    t = (sasaran or "").lower()
    if t in ("#ffffff", "#fff"):
        return BIRU_TUA if laluan in PUTIH_JADI_BIRU else sasaran
    return PETA.get(t, sasaran)


def warna_teks(laluan, c):
    c = (c or "#000000").lower()
    if laluan in TEKS_KEKAL_PUTIH:
        return c
    return BIRU_TUA if c in ("#ffffff", "#faf7f2", "#f5f4f1") or c in PETA else c


# ═══ TEKS ══════════════════════════════════════════════════════════════════
def ambil_runs(a):
    teks = "".join(r["A"] for r in a["A"] if isinstance(r.get("A"), str))
    runs, cur, pos = [], {}, 0
    for s in a.get("B", []):
        if s.get("A?") == "A":
            for k, v in (s.get("A") or {}).items():
                if isinstance(v, dict) and "B" in v:
                    cur[k] = v["B"]
                else:
                    cur.pop(k, None)
        elif s.get("A?") == "B":
            runs.append([teks[pos:pos + s["A"]], dict(cur)])
            pos += s["A"]
    if pos < len(teks):
        runs.append([teks[pos:], dict(cur)])
    return teks, runs


def pecah_lembut(teks, runs, counts):
    """Canva menyimpan bilangan aksara setiap baris. Balutan lembut ditukar
    jadi \\n supaya susunan baris asal kekal walaupun teks diganti."""
    if not counts or sum(counts) != len(teks):
        return runs
    putus, p = set(), 0
    for n in counts[:-1]:
        p += n
        if teks[p - 1] != "\n":
            putus.add(p)
    out, pos = [], 0
    for t, st in runs:
        buf = ""
        for i, ch in enumerate(t):
            if pos + i in putus:
                buf = buf.rstrip(" ") + "\n"
            buf += ch
        out.append([buf, st])
        pos += len(t)
    return out


def gabung(runs):
    out = []
    for t, st in runs:
        if out and out[-1][1] == st:
            out[-1][0] += t
        else:
            out.append([t, dict(st)])
    return out


def render_teks(e, laluan, x, y, k, out):
    teks, runs = ambil_runs(e["a"])
    if laluan in GANTI_PENUH:
        # Canva sering menyimpan sebahagian gaya (cth. leading) dalam bahagian
        # teks yang kemudian sahaja; gabungkan supaya jarak baris kekal.
        gaya = {}
        for _, st in runs:
            for kk, vv in st.items():
                gaya.setdefault(kk, vv)
        runs = [[GANTI_PENUH[laluan], gaya]]
    else:
        runs = gabung(pecah_lembut(teks, runs, (e.get("b") or {}).get("A")))
    for lama, baru in GANTI.get(laluan, []):
        for r in runs:
            if lama in r[0]:
                r[0] = r[0].replace(lama, baru, 1)
                break
        else:
            raise SystemExit(f"{laluan}: teks {lama!r} tiada dalam templat")
    if runs and runs[-1][0].endswith("\n"):
        runs[-1][0] = runs[-1][0][:-1]
    # Buang ruang di hujung BARIS sahaja. Ruang di hujung satu bahagian
    # ("Dengan " + "penuh …") ialah pemisah perkataan dan mesti kekal.
    for i, r in enumerate(runs):
        r[0] = re.sub(r" +\n", "\n", r[0])
        lepas = runs[i + 1][0] if i + 1 < len(runs) else "\n"
        if lepas.startswith("\n"):
            r[0] = r[0].rstrip(" ")
    runs = [r for r in runs if r[0]]
    if not runs:
        return

    uw = e.get("e") or e["D"]
    uh = e.get("f") or e["C"]
    s = (e["D"] / uw if e.get("e") else 1.0) * k
    kiri = x
    if laluan in LEBARKAN:                   # lebarkan kotak dari tengahnya
        baru = LEBARKAN[laluan] / s
        kiri = x + (uw - baru) * s / 2
        uw = baru

    pertama = runs[0][1]
    fid0 = (pertama.get("font-family") or "").split(",")[0]
    lead0 = float(pertama.get("leading") or 1400) / 1000
    baris = "".join(t for t, _ in runs).count("\n") + 1
    saiz_lalai = uh / (baris * lead0 * METRIK.get(fid0, 1.0))

    spans, saiz_lepas, dalam0 = [], None, None
    for t, st in runs:
        fid = (st.get("font-family") or pertama.get("font-family") or "").split(",")[0]
        saiz = float(st["font-size"]) if st.get("font-size") else (saiz_lepas or saiz_lalai)
        saiz_lepas = saiz
        lead = float(st.get("leading") or pertama.get("leading") or 1400) / 1000
        lh = saiz * lead * METRIK.get(fid, 1.0)
        italik = st.get("font-style") == "italic"
        tebal = st.get("font-weight") == "bold"
        # Dalam templat, uppercase hanya kelihatan pada bahagian tegak (nama
        # ibu bapa); bahagian italik bertanda uppercase kekal huruf kecil.
        besar = st.get("text-transform") == "uppercase" and not italik
        jejak = float(st.get("tracking") or 0) / 1000
        css = (f"font-family:{fam(fid)};font-size:{saiz:.3f}px;line-height:{lh:.3f}px;"
               f"color:{warna_teks(laluan, st.get('color'))};font-weight:{700 if tebal else 400};"
               f"font-style:{'italic' if italik else 'normal'}")
        if jejak:
            css += f";letter-spacing:{jejak:.4f}em"
        if besar:
            css += ";text-transform:uppercase"
        dalam0 = dalam0 or (saiz, lh)
        FON_GUNA.add((fid, tebal, italik))
        spans.append(f'<span style="{css}">' + "<br>".join(H.escape(b) for b in t.split("\n")) + "</span>")

    tf = []
    if e.get("E"):
        tf.append(f"rotate({e['E']:.4f}deg)")
    if abs(s - 1) > 1e-6:
        tf.append(f"scale({s:.6f})")
    css = (f"left:{kiri:.2f}px;top:{y:.2f}px;width:{uw:.2f}px;height:{uh:.2f}px;"
           f"text-align:{pertama.get('text-align', 'center')}")
    if tf:
        css += ";transform:" + " ".join(tf) + ";transform-origin:0 0"
    attr = ' id="rsvp-link" role="button" tabindex="0"' if laluan == PAUTAN_RSVP else ""
    if laluan in MUAT:
        attr += f' data-muat="{MUAT[laluan] / s:.1f}"'
    out.append(f'<div class="t"{attr} style="{css}"><span style="font-size:{dalam0[0]:.3f}px;'
               f'line-height:{dalam0[1]:.3f}px">{"".join(spans)}</span></div>')


# ═══ IMEJ, BENTUK, BUTANG ═════════════════════════════════════════════════
_kupu = [0]


def render_kupu(x, y, w, h, out):
    """Rama-rama asal ialah video MP4 (tiada saluran alfa). Gambar poster
    video itu PNG lutsinar, jadi ia diguna terus dan kepakannya dihidupkan
    dengan CSS."""
    _kupu[0] += 1
    im = warna.nude_biru(Image.open(os.path.join(RAW, "kupu-poster.png")).convert("RGBA"))
    nama = simpan(im, w * 2)
    cls = "kupu-diam" + (" k2" if _kupu[0] % 2 == 0 else "")
    out.append(f'<div class="{cls}" style="left:{x:.2f}px;top:{y:.2f}px;width:{w:.2f}px">'
               f'<img src="assets/kad/{nama}" alt=""></div>')


def render_ikon_tambahan(fail, atas, bawah, lebar, out):
    """Ikon SVG sendiri, berpusat di titik tengah antara pusat dua ikon templat."""
    raw = open(os.path.join(ROOT, fail), "rb").read()
    nama = hashlib.md5(raw).hexdigest()[:12] + ".svg"
    with open(os.path.join(OUTA, nama), "wb") as fh:
        fh.write(raw)
    m = re.search(r'viewBox="0 0 ([\d.]+) ([\d.]+)"', raw.decode())
    tinggi = lebar * float(m.group(2)) / float(m.group(1))
    px = (atas[0] + atas[2] / 2 + bawah[0] + bawah[2] / 2) / 2
    py = (atas[1] + atas[3] / 2 + bawah[1] + bawah[3] / 2) / 2
    out.append(f'<div class="im" style="left:{px - lebar / 2:.2f}px;top:{py - tinggi / 2:.2f}px;'
               f'width:{lebar:.2f}px;height:{tinggi:.2f}px"><img src="assets/kad/{nama}" '
               f'style="left:0px;top:0px;width:{lebar:.2f}px;height:{tinggi:.2f}px" alt="" loading="lazy"></div>')


def render_imej(e, laluan, x, y, k, out):
    a = e.get("a") or {}
    b = a.get("B")
    w, h = e["D"] * k, e["C"] * k
    if not isinstance(b, dict):                 # muat naik (rama-rama video)
        render_kupu(x, y, w, h, out)
        return
    ref = b.get("I") or b["A"]
    peta = {kk.lower(): tukar_warna(laluan, v) for kk, v in (b.get("C") or {}).items()}
    kotak = b["B"]
    bx, by, bw, bh = kotak["B"] * k, kotak["A"] * k, kotak["D"] * k, kotak["C"] * k
    nama = aset(ref["A"], peta, bw)
    cls, attr = "im", ""
    if laluan == PIRING:
        cls, attr = "im yt vinyl", ' id="yt-wrap" role="button" tabindex="0" aria-label="Main atau henti muzik"'
    elif laluan == RUMAH:
        cls, attr = "im home-btn", ' id="btn-home" role="button" tabindex="0" aria-label="Kembali ke atas"'
    css = f"left:{x:.2f}px;top:{y:.2f}px;width:{w:.2f}px;height:{h:.2f}px"
    if e.get("E"):
        css += f";transform:rotate({e['E']:.4f}deg);transform-origin:50% 50%"
    out.append(f'<div class="{cls}"{attr} style="{css}"><img src="assets/kad/{nama}" '
               f'style="left:{bx:.2f}px;top:{by:.2f}px;width:{bw:.2f}px;height:{bh:.2f}px" '
               f'alt="" loading="lazy"></div>')


def kotak_laluan(d):
    """Kotak sempadan kasar laluan SVG (titik hujung + titik kawalan)."""
    tok = re.findall(r"[MLHVCSQTZmlhvcsqtz]|-?\d*\.?\d+(?:e-?\d+)?", d)
    xs, ys, cx, cy, i, cmd = [], [], 0.0, 0.0, 0, None
    arg = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "Z": 0}
    while i < len(tok):
        if tok[i].isalpha():
            cmd = tok[i]; i += 1
            if cmd in "Zz":
                continue
        n = arg[cmd.upper()]
        v = [float(t) for t in tok[i:i + n]]; i += n
        rel = cmd.islower()
        if cmd.upper() == "H":
            cx = cx + v[0] if rel else v[0]
        elif cmd.upper() == "V":
            cy = cy + v[0] if rel else v[0]
        else:
            for j in range(0, n, 2):
                px, py = (cx + v[j], cy + v[j + 1]) if rel else (v[j], v[j + 1])
                xs.append(px); ys.append(py)
            cx, cy = xs[-1], ys[-1]
        xs.append(cx); ys.append(cy)
        if cmd == "M": cmd = "L"
        if cmd == "m": cmd = "l"
    return min(xs), min(ys), max(xs), max(ys)


def render_bentuk(e, laluan, x, y, k, out):
    a = e["a"]
    vb = f"{a['A']} {a['B']} {a['D']} {a['C']}"
    defs, isi = [], []
    # Laluan isian gambar tidak tersusun dari atas ke bawah dalam fail reka
    # bentuk, jadi urutannya dikira semula daripada kedudukan y sebenar.
    isian = [(i, kotak_laluan(q["A"])[1]) for i, q in enumerate(e.get("b", []))
             if isinstance(((q.get("B") or {}).get("B")), dict)]
    urutan = {i: r for r, (i, _) in enumerate(sorted(isian, key=lambda x: x[1]))}
    for i, p in enumerate(e.get("b", [])):
        B = p.get("B") or {}
        if isinstance(B.get("B"), dict):
            # Isian gambar = foto pasangan asal. Diganti panel krim dengan
            # jurai bunga templat itu sendiri, berselang cermin supaya jalur
            # tidak nampak berulang.
            x0, y0, x1, y1 = kotak_laluan(p["A"])
            gid = f"jalur{i}"
            papar = (x1 - x0) * e["D"] / a["D"] * k * 2
            r = urutan[i]
            if r < len(GAMBAR):
                nama = gambar_jalur(GAMBAR[r], (x1 - x0) / (y1 - y0), papar)
            else:
                nama = panel_bunga((y1 - y0) / (x1 - x0), cermin=i % 2 == 1, lebar=papar)
            defs.append(f'<clipPath id="{gid}"><path d="{p["A"]}"/></clipPath>')
            isi.append(f'<image href="assets/kad/{nama}" x="{x0:.1f}" y="{y0:.1f}" '
                       f'width="{x1 - x0:.1f}" height="{y1 - y0:.1f}" '
                       f'preserveAspectRatio="xMidYMid slice" clip-path="url(#{gid})"/>')
        else:
            isi.append(f'<path d="{p["A"]}" fill="{tukar_warna(laluan, B.get("C", "none"))}"/>')
    css = f"left:{x:.2f}px;top:{y:.2f}px;width:{e['D'] * k:.2f}px;height:{e['C'] * k:.2f}px"
    out.append(f'<div class="sh" style="{css}"><svg viewBox="{vb}" preserveAspectRatio="none" '
               f'width="100%" height="100%"><defs>{"".join(defs)}</defs>{"".join(isi)}</svg></div>')


def render_butang(e, laluan, x, y, k, out):
    """BC kecil = butang pautan Canva (Google Maps). href diisi pada masa
    jalan daripada CONFIG.peta."""
    yy = e["y"]
    teks = "".join(r["A"] for r in yy["A"]["A"]["A"] if isinstance(r.get("A"), str)).strip()
    stl = {}
    for s in yy["A"]["A"]["B"]:
        if s.get("A?") == "A":
            for kk, v in (s.get("A") or {}).items():
                if isinstance(v, dict) and "B" in v:
                    stl[kk] = v["B"]
    fid = (stl.get("font-family") or "").split(",")[0]
    FON_GUNA.add((fid, stl.get("font-weight") == "bold", False))
    bg = tukar_warna(laluan, yy["C"]["A"]["C"])
    bd = yy["E"]["A"]
    css = (f"left:{x:.2f}px;top:{y:.2f}px;width:{e['D'] * k:.2f}px;height:{e['C'] * k:.2f}px;"
           f"background:{bg};border:{bd['A'] * k}px solid {tukar_warna(laluan, bd['B'])};"
           f"border-radius:{yy['D']['A'] * k}px;color:{stl.get('color', '#fff')};"
           f"font-family:{fam(fid)};font-size:{float(stl.get('font-size', 13)) * k:.3f}px;"
           f"font-weight:{700 if stl.get('font-weight') == 'bold' else 400}")
    out.append(f'<a class="bt" id="btn-peta" href="#" target="_blank" rel="noopener" '
               f'style="{css}">{H.escape(teks)}</a>')


def render_kiraan(x, y, w, h, out):
    out.append(f'<div class="cd" id="countdown" style="left:{x:.2f}px;top:{y:.2f}px;'
               f'width:{w:.2f}px;height:{h:.2f}px"><div class="cd-num"><span>'
               '<b id="cd-d">00</b>:<b id="cd-h">00</b>:<b id="cd-m">00</b>:<b id="cd-s">00</b>'
               '</span></div><div class="cd-lab"><span>DAYS</span><span>HOURS</span>'
               '<span>MINS</span><span>SECS</span></div></div>')


BULAN_EN = ["January", "February", "March", "April", "May", "June", "July", "August",
            "September", "October", "November", "December"]


def render_kalendar(e, x, y, k, out):
    """Kalendar natif pada susun atur imej asal (1122x1402 px)."""
    b = e["a"]["B"]["B"]
    bx, by = x + b["B"] * k, y + b["A"] * k
    sx, sy = b["D"] * k / 1122, b["C"] * k / 1402
    tahun, bulan, hari = TARIKH
    minggu = calendar.Calendar(firstweekday=6).monthdayscalendar(tahun, bulan)
    baris_y = [591 + i * (1265 - 591) / (len(minggu) - 1) for i in range(len(minggu))]
    lajur_x = [137, 283, 427, 570, 715, 856, 996]
    h = [f'<div class="kal" style="left:{bx:.2f}px;top:{by:.2f}px;width:{1122 * sx:.2f}px;'
         f'height:{1402 * sy:.2f}px">']
    h.append(f'<div class="kal-tajuk" style="position:absolute;left:0;right:0;top:{120 * sy:.2f}px;'
             f'font-size:{250 * sx:.2f}px">{BULAN_EN[bulan - 1]}</div>')
    for i, nm in enumerate(["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]):
        h.append(f'<span class="kal-kepala" style="position:absolute;left:{(lajur_x[i] - 70) * sx:.2f}px;'
                 f'width:{140 * sx:.2f}px;top:{(493 - 26) * sy:.2f}px;font-size:{40 * sx:.2f}px;'
                 f'line-height:{52 * sy:.2f}px">{nm}</span>')
    for r, wk in enumerate(minggu):
        for c, d in enumerate(wk):
            if not d:
                continue
            kx, ky = lajur_x[c] * sx, baris_y[r] * sy
            gaya = (f"position:absolute;left:{kx - 70 * sx:.2f}px;width:{140 * sx:.2f}px;"
                    f"top:{ky - 40 * sy:.2f}px;height:{80 * sy:.2f}px;line-height:{80 * sy:.2f}px;"
                    f"font-size:{46 * sx:.2f}px")
            if d == hari:
                h.append(f'<span class="kal-hari kal-hati" style="{gaya}">'
                         f'<svg width="{108 * sx:.2f}" height="{100 * sx:.2f}" viewBox="0 0 24 22" '
                         f'aria-hidden="true"><path fill="{BIRU_TUA}" d="M12 21.4C5.4 16.4 1 12.6 1 7.9 '
                         f'1 4.4 3.7 1.6 7.1 1.6c2 0 3.8 1 4.9 2.6 1.1-1.6 2.9-2.6 4.9-2.6 3.4 0 6.1 2.8 6.1 '
                         f'6.3 0 4.7-4.4 8.5-11 13.5Z"/></svg><b>{d}</b></span>')
            else:
                h.append(f'<span class="kal-hari" style="{gaya}">{d}</span>')
    h.append("</div>")
    out.append("".join(h))


# ═══ SUSUN ATUR ═══════════════════════════════════════════════════════════
def render(e, laluan, x, y, k, out):
    """Ratakan kumpulan (H) terus ke koordinat mutlak — tiada lapisan
    bertransform bagi kumpulan (pengajaran Safari iOS daripada kad Zaitul)."""
    if laluan in LANGKAU:
        return
    t = e.get("A?")
    if laluan == KALENDAR:
        render_kalendar(e, x, y, k, out)
    elif laluan == KIRAAN:
        render_kiraan(x, y, e["D"] * k, e["C"] * k, out)
    elif t == "H":
        kk = k * (e["D"] / e["b"] if e.get("b") else 1.0)
        kotak = {}
        for i, c in enumerate(e.get("c", [])):
            anak = f"{laluan}.{i}"
            cx, cy = x + c.get("B", 0) * kk, y + c.get("A", 0) * kk + GESER_ANAK_Y.get(anak, 0.0)
            kotak[anak] = (cx, cy, c.get("D", 0) * kk, c.get("C", 0) * kk)
            render(c, anak, cx, cy, kk, out)
        for fail, atas, bawah, lebar in IKON_TAMBAHAN:
            if atas in kotak and bawah in kotak:
                render_ikon_tambahan(fail, kotak[atas], kotak[bawah], lebar, out)
    elif t == "K":
        render_teks(e, laluan, x, y, k, out)
    elif t == "I":
        render_imej(e, laluan, x, y, k, out)
    elif t == "J":
        render_bentuk(e, laluan, x, y, k, out)
    elif t == "BC":
        render_butang(e, laluan, x, y, k, out)


def lapisan(items):
    """Kumpulkan elemen atas jadi lapisan yang tidak bertindih menegak
    (sama seperti kad Zaitul) supaya susunan z asal kekal."""
    ikut_y = sorted(items, key=lambda t: t[1]["A"])
    out, cur, bawah = [], [], None
    for i, e in ikut_y:
        if cur and e["A"] > bawah:
            out.append(cur); cur, bawah = [], None
        cur.append((i, e))
        bawah = e["A"] + e["C"] if bawah is None else max(bawah, e["A"] + e["C"])
    if cur:
        out.append(cur)
    return [sorted(b, key=lambda t: t[0]) for b in out]


def render_bingkai(fr, hal, tinggi, berlapis):
    w = fr["C"]["A"]
    out = [f'<div class="frame" style="width:{w}px;height:{tinggi:.0f}px;background:{NUDE}">']
    items = [(i, e) for i, e in enumerate(fr["E"])
             if isinstance(e.get("A"), (int, float)) and f"{hal}:{i}" not in LANGKAU]
    if not berlapis:
        for i, e in items:
            render(e, f"{hal}:{i}", e["B"], e["A"], 1.0, out)
    else:
        for band in lapisan(items):
            x0 = max(0.0, min(e["B"] for _, e in band) - 40)
            y0 = max(0.0, min(e["A"] for _, e in band) - 40)
            x1 = min(w, max(e["B"] + e["D"] for _, e in band) + 40)
            y1 = min(tinggi, max(e["A"] + e["C"] for _, e in band) + 40)
            out.append(f'<div class="band" style="left:{x0:.2f}px;top:{y0:.2f}px;'
                       f'width:{x1 - x0:.2f}px;height:{y1 - y0:.2f}px">')
            for i, e in band:
                render(e, f"{hal}:{i}", e["B"] - x0, e["A"] - y0, 1.0, out)
            out.append("</div>")
    out.append("</div>")
    return "\n".join(out)


def css_fon():
    gaya_nama = {(False, False): "REGULAR", (True, False): "BOLD",
                 (False, True): "ITALICS", (True, True): "BOLD_ITALICS"}
    out, dibuat = [], set()
    for fid, tebal, italik in sorted(FON_GUNA):
        fail = FONFAIL.get(fid, {})
        gaya = gaya_nama[(tebal, italik)]
        if gaya not in fail:
            gaya = "REGULAR" if "REGULAR" in fail else next(iter(fail), None)
        if not gaya or (fid, gaya) in dibuat:
            continue
        dibuat.add((fid, gaya))
        url = fail[gaya]
        nama = os.path.basename(url)
        with open(os.path.join(RAW, nama), "rb") as src, open(os.path.join(OUTA, nama), "wb") as dst:
            dst.write(src.read())
        out.append(f"@font-face{{font-family:'{CSSFONT[fid]}';font-weight:{700 if 'BOLD' in gaya else 400};"
                   f"font-style:{'italic' if 'ITALIC' in gaya else 'normal'};font-display:block;"
                   f"src:url('assets/kad/{nama}') format('woff');}}")
    return "\n".join(out)


def main():
    if os.path.isdir(OUTA):
        for f in os.listdir(OUTA):
            os.remove(os.path.join(OUTA, f))
    os.makedirs(OUTA, exist_ok=True)

    kulit = DOC["A"][0]["t"][0]
    utama = DOC["A"][1]["t"][0]
    tinggi = float(utama["C"]["B"])

    if ATURCARA:
        pemisah = "\n" * (BARIS_KOSONG_ATURCARA + 1)
        GANTI_PENUH[TEKS_ATURCARA] = pemisah.join(f"{m}\n{a}" for m, a in ATURCARA)
        dipakai = {v for i, v in IKON_ATURCARA.items() if i < len(ATURCARA)}
        LANGKAU.update(p for p in IKON_SEMUA if p not in dipakai)
    if not ATURCARA:
        # sembunyikan kad aturcara, naikkan elemen di bawahnya ke tempatnya
        idx = int(SEMBUNYI_ATURCARA.split(":")[1])
        g = utama["E"][idx]
        LANGKAU.add(SEMBUNYI_ATURCARA)
        bawah_g = g["A"] + g["C"]
        seterusnya = min(e["A"] for e in utama["E"]
                         if isinstance(e.get("A"), (int, float)) and e["A"] >= bawah_g)
        anjak = seterusnya - g["A"]
        for e in utama["E"]:
            if isinstance(e.get("A"), (int, float)) and e["A"] >= bawah_g:
                e["A"] -= anjak
        tinggi -= anjak

    for i, e in enumerate(utama["E"]):
        d = GESER_Y.get(f"1:{i}")
        if d and isinstance(e.get("A"), (int, float)):
            e["A"] += d

    # Setiap halaman dipusatkan pada hiasannya sendiri (muka depan ~683,
    # halaman utama ~724 — seperti Canva). Kotak teks tidak dikira: kotak
    # "Julai" selebar 320px walaupun dakwatnya kecil, dan ia memesongkan pusat.
    def sempadan(fr, hal):
        xs = [x for i, e in enumerate(fr["E"])
              if f"{hal}:{i}" not in LANGKAU and f"{hal}:{i}" not in TIDAK_DIKIRA_SEMPADAN
              and e.get("A?") != "K"
              and isinstance(e.get("B"), (int, float))
              for x in (e["B"], e["B"] + e["D"])]
        return min(xs), max(xs)
    k0, k1 = sempadan(kulit, 0)
    u0, u1 = sempadan(utama, 1)
    lebar = (u1 - u0) + 2 * TEPI

    html_kulit = render_bingkai(kulit, 0, float(kulit["C"]["B"]), berlapis=False)
    html_utama = render_bingkai(utama, 1, tinggi, berlapis=True)

    kerangka = open(os.path.join(HERE, "shell.html"), encoding="utf-8").read()
    halaman = (kerangka.replace("/*__FONTS__*/", css_fon())
               .replace("<!--__COVER__-->", html_kulit)
               .replace("<!--__MAIN__-->", html_utama)
               .replace("__CANVAS_W__", str(utama["C"]["A"]))
               .replace("__COVER_H__", str(kulit["C"]["B"]))
               .replace("__MAIN_H__", f"{tinggi:.0f}")
               .replace("__CONTENT_W__", f"{lebar:.2f}")
               .replace("__COVER_CX__", f"{(k0 + k1) / 2:.2f}")
               .replace("__MAIN_CX__", f"{(u0 + u1) / 2:.2f}"))
    baki = re.findall(r"__[A-Z_]+__", halaman)
    if baki:
        raise SystemExit(f"penanda tidak diganti: {baki}")
    with open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(halaman)

    jumlah = sum(os.path.getsize(os.path.join(OUTA, f)) for f in os.listdir(OUTA))
    print(f"index.html {len(halaman) // 1024} KB | assets/kad {len(os.listdir(OUTA))} fail "
          f"{jumlah / 1024 / 1024:.1f} MB | kanvas 1366x{tinggi:.0f} | pusat muka depan "
          f"{(k0 + k1) / 2:.0f}, utama {(u0 + u1) / 2:.0f} | lebar {lebar:.0f}")


if __name__ == "__main__":
    main()
