"""Tukar palet templat Ain & Aiman (maroon + hijau zaitun + krim) kepada
nude + biru, ikut warna dewan.

Imej hiasan templat ialah foto/raster dengan warna yang dibakar terus, jadi
ia tidak boleh diwarnakan semula melalui peta warna Canva. Sebaliknya rona
setiap piksel dianjak:

  maroon pekat  (rona ~355°, tepu)  -> biru tua
  hijau zaitun  (rona ~75°)         -> biru berdebu
  merah jambu lembut, krim, putih   -> tidak disentuh (jadi blush/nude)

Pemberat berperingkat (bukan potongan tajam) mengelakkan jalur warna pada
tepi kelopak dan ukiran.
"""
import numpy as np
from PIL import Image

BIRU_TUA = "#3d5577"     # teks, panel gelap
BIRU     = "#7d93b2"     # renda, reben, garis hiasan
NUDE     = "#efe4da"     # latar kad

RONA_BIRU = 216.0        # sasaran rona untuk kedua-dua anjakan


def _hsv(rgb):
    mx, mn = rgb.max(-1), rgb.min(-1)
    d = mx - mn
    s = np.where(mx > 0, d / np.maximum(mx, 1e-6), 0)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    dd = np.maximum(d, 1e-6)
    h = np.where(mx == r, ((g - b) / dd) % 6,
                 np.where(mx == g, (b - r) / dd + 2, (r - g) / dd + 4)) * 60.0
    return np.where(d > 1e-6, h, 0.0), s, mx


def _rgb(h, s, v):
    h = (h % 360) / 60.0
    i = np.floor(h).astype(int) % 6
    f = h - np.floor(h)
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    pilih = [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)]
    out = np.zeros(h.shape + (3,), dtype=np.float32)
    for k, (a, b, c) in enumerate(pilih):
        m = i == k
        out[m, 0], out[m, 1], out[m, 2] = a[m], b[m], c[m]
    return out


def _jalur(h, pusat, lebar):
    """1 dalam jalur rona, menurun licin ke 0 di tepinya."""
    jarak = np.abs((h - pusat + 180) % 360 - 180)
    return np.clip((lebar - jarak) / (lebar * 0.35), 0, 1)


def _ramp(x, a, b):
    return np.clip((x - a) / (b - a), 0, 1)


def nude_biru(im):
    """Anjak maroon & hijau zaitun sesuatu imej RGBA kepada biru."""
    arr = np.asarray(im.convert("RGBA")).astype(np.float32) / 255.0
    rgb, alfa = arr[..., :3], arr[..., 3:]
    h, s, v = _hsv(rgb)

    # Diukur pada aset sebenar: bingkai zaitun rona 44–60° (tepu 0.23–0.58),
    # kertas krim rona 30–44° (tepu kebanyakannya < 0.22). Jadi hijau diberi
    # berat penuh dari 47° dan tepu >= 0.24; krim kekal di luar.
    hijau = _ramp(h, 42, 47) * (1 - _ramp(h, 110, 125)) * _ramp(s, 0.16, 0.24)
    merah = _jalur(h, 352, 34) * _ramp(s, 0.30, 0.42)
    w = np.maximum(hijau, merah)[..., None]

    # Warna biru penuh, kemudian dicampur dalam RGB mengikut pemberat.
    # Memutar rona separuh jalan menghasilkan teal (dari hijau) atau ungu
    # (dari maroon) pada tepi; campuran RGB memberi kelabu neutral.
    biru = _rgb(np.full_like(h, RONA_BIRU), s * 0.70,
                np.clip(v * (1 + hijau * 0.06), 0, 1))
    out = rgb * (1 - w) + biru * w
    return Image.fromarray((np.concatenate([out, alfa], -1) * 255).round().astype("uint8"), "RGBA")


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
