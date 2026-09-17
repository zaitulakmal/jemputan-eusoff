#!/usr/bin/env python3
"""Jana hiasan taman untuk kad — dahan zaitun, eukaliptus dan bunga putih.

    python3 tools/taman.py

Menulis tiga fail ke assets/:
  taman-kiri.svg   gugusan dahan dari penjuru atas kiri
  taman-kanan.svg  gugusan dari penjuru bawah kanan (benih rawak lain)
  ranting.svg      ranting kecil pemisah bahagian

Benih rawak ditetapkan, jadi hasilnya sama setiap kali dijalankan.
"""
import math, os, random

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "assets")

DAUN = ["#6a82a3", "#7d93b2", "#94a8c4", "#5c7394", "#a9b9d0"]   # biru berdebu
TANGKAI = "#6a7f9c"


def bez(p, t):
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = p
    u = 1 - t
    x = u**3 * x0 + 3 * u * u * t * x1 + 3 * u * t * t * x2 + t**3 * x3
    y = u**3 * y0 + 3 * u * u * t * y1 + 3 * u * t * t * y2 + t**3 * y3
    dx = 3 * u * u * (x1 - x0) + 6 * u * t * (x2 - x1) + 3 * t * t * (x3 - x2)
    dy = 3 * u * u * (y1 - y0) + 6 * u * t * (y2 - y1) + 3 * t * t * (y3 - y2)
    return x, y, math.degrees(math.atan2(dy, dx))


def daun(x, y, sudut, L, W, warna, legap, urat=True):
    d = (f"M0 0C{L*.28:.1f} {-W:.1f} {L*.72:.1f} {-W*.85:.1f} {L:.1f} 0"
         f"C{L*.72:.1f} {W*.85:.1f} {L*.28:.1f} {W:.1f} 0 0Z")
    s = (f'<g transform="translate({x:.1f} {y:.1f}) rotate({sudut:.1f})">'
         f'<path d="{d}" fill="{warna}" fill-opacity="{legap:.2f}"/>')
    if urat and L > 28:
        s += (f'<path d="M{L*.08:.1f} 0Q{L*.5:.1f} {-W*.08:.1f} {L*.9:.1f} 0" fill="none" '
              f'stroke="#fff" stroke-opacity=".32" stroke-width=".9"/>')
    return s + "</g>"


def dahan(rng, p, n, L0, L1, nisbah, lebar=2.2, legap=(0.78, 1.0), mula=0.08):
    x0, y0 = p[0]
    s = [f'<path d="M{x0} {y0}C{p[1][0]} {p[1][1]} {p[2][0]} {p[2][1]} {p[3][0]} {p[3][1]}" '
         f'fill="none" stroke="{TANGKAI}" stroke-width="{lebar}" stroke-linecap="round"/>']
    for i in range(n):
        t = mula + (1 - mula) * i / max(1, n - 1)
        x, y, a = bez(p, t)
        L = L0 + (L1 - L0) * t
        sisi = 1 if i % 2 == 0 else -1
        sudut = a + sisi * rng.uniform(34, 52)
        s.append(daun(x, y, sudut, L * rng.uniform(.9, 1.08), L * nisbah,
                      rng.choice(DAUN), rng.uniform(*legap)))
    x, y, a = bez(p, 1)                                   # daun hujung
    s.append(daun(x, y, a, L1 * 1.05, L1 * nisbah, rng.choice(DAUN), legap[1]))
    return "".join(s)


def bunga(x, y, r, putar=0):
    s = [f'<g transform="translate({x:.1f} {y:.1f}) rotate({putar})">']
    for k in range(5):
        s.append(f'<ellipse cx="0" cy="{-r*.55:.1f}" rx="{r*.42:.1f}" ry="{r*.6:.1f}" '
                 f'fill="#fffaf5" fill-opacity=".94" transform="rotate({k*72})"/>')
    s.append(f'<circle r="{r*.2:.1f}" fill="#d4b08c"/></g>')
    return "".join(s)


def gugusan(benih, lentur):
    """Satu gugusan penjuru atas kiri; `lentur` mengubah bentuk dahan."""
    rng = random.Random(benih)
    b = lentur
    s = []
    # eukaliptus — daun bulat, warna lebih cerah
    s.append(dahan(rng, [(20, -30), (60 + b, 120), (40, 280 + b), (130 + b, 470)],
                   11, 46, 26, .5, lebar=1.8, legap=(.7, .92)))
    # zaitun utama — daun panjang dan tirus
    s.append(dahan(rng, [(-30, 40), (150, 40 + b), (300 + b, 150), (470, 330 + b)],
                   15, 72, 36, .19, lebar=2.4))
    # ranting kecil
    s.append(dahan(rng, [(-20, 210), (80, 225), (160 + b, 262), (225, 335 + b)],
                   9, 40, 22, .22, lebar=1.6, legap=(.62, .85)))
    for t, r in ((.42, 17), (.7, 12)):
        x, y, _ = bez([(-30, 40), (150, 40 + b), (300 + b, 150), (470, 330 + b)], t)
        s.append(bunga(x + 6, y + 14, r, rng.uniform(0, 72)))
    x, y, _ = bez([(20, -30), (60 + b, 120), (40, 280 + b), (130 + b, 470)], .55)
    s.append(bunga(x + 14, y, 14, rng.uniform(0, 72)))
    x, y, _ = bez([(-20, 210), (80, 225), (160 + b, 262), (225, 335 + b)], .8)
    s.append(bunga(x, y + 10, 9, rng.uniform(0, 72)))
    return "".join(s)


def svg(badan, w=600, h=640):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}">{badan}</svg>\n')


def ranting():
    rng = random.Random(7)
    s = ['<path d="M8 20Q60 14 112 20" fill="none" stroke="#6a7f9c" stroke-width="1.1" '
         'stroke-linecap="round"/>']
    for i, x in enumerate((22, 34, 46, 74, 86, 98)):
        kiri = x < 60
        L = 13 - abs(60 - x) * .08
        a = (200 if kiri else -20) + (-38 if i % 2 else 38)
        s.append(daun(x, 17.4 + abs(60 - x) * .04, a, L, L * .3, "#7d93b2", .9, urat=False))
    s.append(bunga(60, 16.5, 7.5, rng.uniform(0, 72)))
    return svg("".join(s), 120, 32)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, "taman-kiri.svg"), "w").write(svg(gugusan(11, 0)))
    kanan = f'<g transform="translate(600 640) rotate(180)">{gugusan(23, 30)}</g>'
    open(os.path.join(OUT, "taman-kanan.svg"), "w").write(svg(kanan))
    open(os.path.join(OUT, "ranting.svg"), "w").write(ranting())
    for f in ("taman-kiri.svg", "taman-kanan.svg", "ranting.svg"):
        print(f, os.path.getsize(os.path.join(OUT, f)), "bait")
