# Kontrak projek — jemputan-eusoff

Kad jemputan digital **Walimatul Urus sebelah Eusoff** (pihak lelaki).
Pasangan kepada repo `jemputan-eusoff-zaitul` (kad sebelah Zaitul, maroon).

`CLAUDE.md` ialah symlink ke fail ini.

## Keputusan yang telah dibuat (oleh Zaitul)

| Tarikh | Perkara | Keputusan |
|---|---|---|
| 11 Sep 2026 | Repo | Repo berasingan `jemputan-eusoff` |
| 11 Sep 2026 | Teknologi | HTML/CSS/JS biasa + skrip bina Python. Tiada framework |
| 11 Sep 2026 | Pangkalan data | Projek Firebase `fir-demo-b08a9`, koleksi `rsvp_eusoff` + `ucapan_eusoff` |
| 11 Sep 2026 | Senarai RSVP | Repo ini ada `senarai.html` + `tools/laporan.py` sendiri |
| 11 Sep 2026 | Jenis majlis | Walimatul Urus Putera |
| 11 Sep 2026 | Warna | Nude + biru, ikut warna dewan (Asiana Grand Hall) |
| 11 Sep 2026 | Reka bentuk | **Klon tepat** templat Canva `jemputku.my.canva.site/ainaiman`, diwarnakan nude + biru |
| 12 Sep 2026 | Jalur gambar | 4 gambar Eusoff & Zaitul dalam jalur, ikut susunan templat. Gambar TIDAK diwarnakan semula; hiasan sahaja |
| 11 Sep 2026 | Lagu | `8_E_IKKnjeY`, sama dengan kad Zaitul |

Versi sebelumnya (reka bentuk taman + kaca) disimpan sebagai `versi-taman.html`
(tidak di-deploy).

## Cara ia dibina

`index.html` DIJANA. Jangan sunting terus.

```
python3 tools/ambil.py    # sekali: data reka bentuk + media Canva -> tools/cache/ (tidak di-commit)
python3 tools/bina.py     # jana index.html + assets/kad/
```

| Fail | Isi |
|---|---|
| `tools/bina.py` | Pembina. `GANTI` (teks), `MUAT`, `TARIKH`, `ATURCARA`, peta warna |
| `tools/shell.html` | Kerangka: `window.CONFIG` (tarikh, peta, lagu, DB), `window.TETAMU`, CSS, JS runtime, borang RSVP |
| `tools/warna.py` | Anjakan rona maroon/hijau zaitun -> biru untuk imej raster |
| `tools/ambil.py` | Ambil `design.json` + media dari laman Canva (dalam `vm` node terasing) |
| `tools/images.py` | Pemasang spritesheet Canva (disalin dari repo Zaitul) |
| `assets/kad/` | Output bina — nama fail = hash isi, dipadam & dijana semula setiap bina |

Teks diganti ikut **laluan elemen** (`"1:17.3"` = halaman 1, elemen 17, anak 3).
Setiap penggantian mesti wujud dalam templat — kalau tidak, bina gagal dengan jelas.

## Peraturan yang mesti dipatuhi

1. **Firestore rules TIDAK di-deploy dari repo ini.** Satu projek, satu fail rules:
   `jemputan-eusoff-zaitul/firestore.rules`. `firebase.json` di sini hanya `hosting`.
2. **Gambar peribadi pasangan asal templat (Ain & Aiman) tidak boleh dimuat turun
   atau digunakan.** `tools/ambil.py` mengecualikan media `PERIBADI`.
3. Kumpulan Canva (`H`) diratakan ke koordinat mutlak — **jangan bungkus elemen
   dalam lapisan bertransform bersaiz kanvas**. Kad Zaitul pernah dibunuh Safari iOS
   kerana itu. Lapisan `.band` hanya sebesar kandungannya dan melepaskan transform
   selepas muncul (`.siap`).
4. Aset `assets/**` dihantar `immutable` (1 tahun). Output bina sudah bernama hash
   isi, jadi selamat. Fail aset bernama tetap (versi taman) perlu `?v=N`.
5. `window.TETAMU` mesti kekal blok tersendiri berakhir `];` — `senarai.html` dan
   `laporan.py` menghuraikannya.
6. Jangan isi kandungan rekaan. Yang belum diberi -> tanya Zaitul.

## Status live

- Link tetamu (17 Sep 2026): https://majlis-eusoff-zaitul.web.app (site `majlis-eusoff-zaitul`).
  Laman lama https://jemputan-eusoff.web.app (site `jemputan-eusoff`) masih kad taman 11 Sep.
- Masih menghidangkan **versi taman**. Klon Ain & Aiman belum dinaikkan ke live.
- Deploy: `firebase deploy --only hosting --project fir-demo-b08a9`
- Rules `rsvp_eusoff`/`ucapan_eusoff` sudah di-deploy dari repo Zaitul dan diuji.
- `/senarai-<kod rahsia>` ada **Muat turun PDF** (17 Sep 2026): laporan cetak A4 tanpa pustaka luar.
  Hanya ada di pratonton sehingga laman live di-deploy. `MAJLIS` dalam `senarai.html`
  mesti diselaraskan kalau tarikh/tempat berubah.
- `/senarai-<kod rahsia>` ada **sunting rekod** (17 Sep 2026): pemilik boleh ubah nama, kehadiran,
  bilangan dan ucapan. Rekod lama tetamu yang sama ikut nama baharu; ucapan pada kad
  (`ucapan_eusoff`) diselaraskan. Masa jawab dikunci oleh rules. Rules yang membenarkan
  ini ada dalam repo Zaitul (sudah di-deploy, diuji 14/14 dengan Rules test API).
  Kad Zaitul sengaja kekal: hanya kehadiran & bilangan boleh diubah di sana.
- **Balas ucapan** (17 Sep 2026): tab Ucapan dalam `/senarai-<kod rahsia>` membaca `ucapan_eusoff`; pemilik
  tulis/ubah/buang balasan (medan `balasan` + `masaBalasan` pada dokumen ucapan). Kad memaparkan
  "Balasan pengantin" di bawah ucapan. Rules: `isUcapanEusoffSah` (update pemilik sahaja); create
  kekal `isUcapanSah`, jadi tetamu tidak boleh mencipta ucapan yang siap berbalasan. Diuji 15/15.
- `authDomain` dalam `senarai.html` = domain laman sendiri (pembetulan "missing initial
  state" di iPhone, dibawa dari kad Zaitul).

## Open questions

- Nama penuh pengantin untuk panel salam (`1:17.7`) — sementara "Eusoff" / "Zaitul".
- Gambar asal ada dalam `assets/gambar/` (tidak disiarkan; hosting menyiarkan salinan WebP terpotong sahaja).
- Tanda pagar lencana (`1:22.2`) — sementara `#TogetherWithEusoffZaitul`
  (ikut corak templat `#TogetherWithAinman`), belum disahkan.
- Label templat dalam Bahasa Inggeris (Open, Counting Days, DAYS/HOURS…, kalendar
  March/Sun–Sat, Tentatives) — kekalkan atau terjemah?
- Aturcara (17 Sep 2026, disahkan Zaitul): 11.30 am Ketibaan tetamu & jamuan · 12.30 pm Ketibaan
  pengantin · 1.00 pm Bacaan doa · 1.15 pm Memotong kek & sesi bergambar · 4.00 pm Majlis bersurai.
  Kad tarikh & laporan PDF: 11.30 am - 4.00 pm. Ikon dijajarkan dengan `GESER_ANAK_Y` (diukur).
- Pin Google Maps tepat (sekarang pautan carian), senarai tetamu.
- Repo GitHub: awam atau peribadi? Belum dicipta. Belum di-commit.

## Akses senarai RSVP (17 Sep 2026)

Keputusan Zaitul, selepas diberitahu risikonya: senarai terbuka kepada **sesiapa**, tanpa log masuk
(baca, sunting, padam, balas). Link: https://majlis-eusoff-zaitul.web.app/senarai-<kod rahsia> (tidak disimpan dalam repo)
- Alamat rawak supaya tetamu tidak boleh meneka dari link kad — tetapi data `rsvp_eusoff` /
  `ucapan_eusoff` tetap boleh dibaca terus melalui API (kunci ada dalam kod kad).
- Rules masih menguatkuasakan: masa jawab dikunci, data mesti sah, ucapan baharu tidak boleh dicipta
  siap berbalasan. Kad Zaitul (`rsvp`, `ucapan`) kekal perlu log masuk pemilik.
- Tiada sandaran automatik: rekod yang dipadam tidak boleh dipulihkan.
