"""Pemprosesan aset imej Canva.

Canva menyimpan grafik dalam tiga bentuk yang perlu dipasang semula:
  1. Foto  — PNG RGB + PNG topeng berasingan yang membawa saluran alfa.
  2. Vektor PNG — 'spritesheet' berlapis: beberapa petak bersebelahan, satu
     petak bagi setiap lapisan (BACKGROUND_R/G/B/A + lapisan RECOLORABLE).
     Setiap lapisan RECOLORABLE diisi dengan satu warna pepejal.
  3. Vektor SVG — kumpulan id="changeN_M", diwarnakan melalui CSS.
Peta pewarnaan semula setiap elemen ({warna_asal: warna_baharu}) datang
daripada dokumen reka bentuk.
"""
import os, re, math, hashlib
from PIL import Image


def _tiles(im, wide, high):
    tw, th = im.width // wide, im.height // high
    return [im.crop((c * tw, r * th, (c + 1) * tw, (r + 1) * th))
            for r in range(high) for c in range(wide)]


def _hex(rgbstr):
    m = re.match(r"rgb\((\d+),\s*(\d+),\s*(\d+)\)", rgbstr or "")
    if not m:
        return "#000000"
    return "#%02x%02x%02x" % tuple(int(g) for g in m.groups())


def _rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def compose_spritesheet(path, meta, recolor):
    """Pasang semula vektor berlapis menjadi satu imej RGBA."""
    im = Image.open(path).convert("RGBA")
    wide, high = meta["spritesWide"], meta["spritesHigh"]
    ts = _tiles(im, wide, high)
    layers = meta["layers"]
    w, h = ts[0].size
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))

    idx = {l["type"]: i for i, l in enumerate(layers) if not l["type"].startswith("RECOL")}
    if "BACKGROUND_A" in idx:
        a = ts[idx["BACKGROUND_A"]].convert("L")
        if {"BACKGROUND_R", "BACKGROUND_G", "BACKGROUND_B"} <= idx.keys():
            r = ts[idx["BACKGROUND_R"]].convert("L")
            g = ts[idx["BACKGROUND_G"]].convert("L")
            b = ts[idx["BACKGROUND_B"]].convert("L")
            out = Image.merge("RGBA", (r, g, b, a))
        elif a.getextrema()[1] > 0:
            out = Image.merge("RGBA", (a, a, a, a))

    for i, l in enumerate(layers):
        if not l["type"].startswith("RECOL") or i >= len(ts):
            continue
        base = _hex(l.get("color"))
        col = recolor.get(base, base)
        mask = ts[i].convert("L")
        if mask.getextrema()[1] == 0:
            continue
        solid = Image.new("RGBA", (w, h), _rgb(col) + (255,))
        solid.putalpha(mask)
        out = Image.alpha_composite(out, solid)
    return out


def compose_masked(base_path, mask_path):
    """Foto RGB + PNG topeng -> RGBA."""
    base = Image.open(base_path).convert("RGB")
    mk = Image.open(mask_path)
    if mk.size != base.size:
        mk = mk.resize(base.size, Image.LANCZOS)
    alpha = mk.getchannel("A") if "A" in mk.getbands() else mk.convert("L")
    out = base.convert("RGBA")
    out.putalpha(alpha)
    return out


def recolor_svg(text, meta, recolor):
    """Warnakan semula SVG Canva melalui kumpulan id='changeN_M'."""
    recolorables = [l for l in (meta or {}).get("layers", []) if l["type"].startswith("RECOL")]
    ids = sorted(set(re.findall(r'id="(change(\d+)_\d+)"', text)), key=lambda t: t[0])
    css = []
    for full, n in ids:
        k = int(n) - 1
        if k < len(recolorables):
            base = _hex(recolorables[k].get("color"))
            col = recolor.get(base, base)
        elif len(recolorables) == 1:
            base = _hex(recolorables[0].get("color"))
            col = recolor.get(base, base)
        else:
            continue
        css.append(f"#{full},#{full} *{{fill:{col}}}")
    # ganti juga warna heks eksplisit yang disebut dalam peta
    for old, new in (recolor or {}).items():
        short = "#" + "".join(c[0] for c in re.findall(r"..", old.lstrip("#")))
        for form in (old, old.upper(), short, short.upper()):
            text = text.replace(f'"{form}"', f'"{new}"')
    if css:
        text = re.sub(r"(<svg\b[^>]*>)", r"\1<style>" + "".join(css) + "</style>", text, count=1)
    return text


def save_png(im, dst, target_w):
    if im.width > target_w:
        h = max(1, round(im.height * target_w / im.width))
        im = im.resize((target_w, h), Image.LANCZOS)
    im.save(dst, "PNG", optimize=True)


def png_bytes(im, target_w):
    """Hasilkan bait PNG tanpa menulis fail — untuk nama berasaskan isi."""
    import io
    if im.width > target_w:
        h = max(1, round(im.height * target_w / im.width))
        im = im.resize((target_w, h), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "PNG", optimize=True)
    return buf.getvalue()
