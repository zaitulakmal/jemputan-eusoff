# Kad Jemputan — Walimatul Urus Eusoff

Kad sebelah pengantin lelaki. Klon tepat templat Canva **Ain & Aiman**
(jemputku), diwarnakan semula **nude + biru** ikut warna dewan.

**Link tetamu:** <https://majlis-eusoff.web.app> · senarai RSVP: `/senarai-<kod rahsia>`

```
index.html        kad (DIJANA — jangan sunting terus)
senarai.html      papan RSVP untuk pemilik (log masuk Google)
assets/kad/       imej + fon hasil bina
tools/            skrip bina (lihat di bawah)
versi-taman.html  reka bentuk sebelumnya (taman + kaca), tidak di-deploy
```

## Tukar maklumat

| Apa | Di mana |
|---|---|
| Teks pada kad (nama, tarikh, tempat, telefon, ibu bapa) | `GANTI` dalam `tools/bina.py` |
| Tarikh kalendar | `TARIKH` dalam `tools/bina.py` |
| Kiraan detik, pautan Google Maps, lagu, WhatsApp | `window.CONFIG` dalam `tools/shell.html` |
| Senarai jemputan | `window.TETAMU` dalam `tools/shell.html` |
| Aturcara | `ATURCARA` dalam `tools/bina.py` (kosong = kad aturcara disembunyikan) |
| Gambar jalur | `GAMBAR` dalam `tools/bina.py` — fail dalam `assets/gambar/`, `fokus` 0–1 menetapkan titik potongan mendatar |

Selepas menukar apa-apa:

```
python3 tools/bina.py
firebase deploy            # hosting + firestore.rules
```

Kali pertama di mesin baharu, ambil data templat dahulu:

```
python3 tools/ambil.py
```

Ini memuat turun data reka bentuk dan media Canva ke `tools/cache/` (tidak
di-commit). Gambar peribadi pasangan asal templat sengaja tidak dimuat turun.

## Senarai jemputan

```js
window.TETAMU = [
  "Siti binti Osman",                    // tiada had orang
  { nama: "Ahmad bin Ali", pax: 2 },     // maksimum 2 orang
];
```

Kosongkan senarai kalau nak sesiapa sahaja boleh RSVP.

## Data RSVP

Projek Firebase sendiri `project-50fca4c2-1177-4292-916` ("Majlis Eusoff"), tidak dikongsi
dengan kad Zaitul. Koleksi: `rsvp_eusoff` dan `ucapan_eusoff` (dipaparkan pada kad).

```
python3 tools/laporan.py                  # ringkasan + senarai
python3 tools/laporan.py --csv rsvp.csv   # eksport
```

### Laporan PDF

Dalam `/senarai-<kod rahsia>`, tekan **Muat turun PDF**. Data disegarkan dahulu, kemudian
laporan A4 dibuka dalam dialog cetak — pilih **Simpan sebagai PDF**
(iPhone: Kongsi → Cetak → Kongsi → Simpan ke Fail).

Isi laporan: butiran majlis, ringkasan (jumlah orang hadir, jemputan hadir,
tidak hadir, belum jawab), jadual bernombor bagi setiap kumpulan, dan ucapan.
Tiada pustaka luar. Butiran majlis dalam laporan ada dalam `MAJLIS` di
`senarai.html` — mesti sama dengan kad.

**Peraturan Firestore** ada dalam `firestore.rules` repo ini. Lihat `AGENTS.md`.

## Warna

Imej hiasan templat ialah raster dengan warna yang dibakar terus. `tools/warna.py`
menganjak rona setiap piksel: maroon pekat -> biru tua, hijau zaitun -> biru
berdebu. Krim, putih dan merah jambu lembut tidak disentuh.
