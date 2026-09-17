#!/usr/bin/env python3
"""Laporan RSVP — berapa hadir, berapa tidak, siapa belum jawab.

Membaca rekod RSVP terus daripada Firestore menggunakan kelayakan gcloud
anda sendiri (koleksi rsvp_eusoff). Peraturan keselamatan menghalang sesiapa membaca data ini
dari pelayar; permintaan bertanda pemilik projek seperti ini dibenarkan.

    python3 tools/laporan.py              # ringkasan + senarai
    python3 tools/laporan.py --csv fail.csv   # eksport untuk Excel/Sheets
"""
import json, re, subprocess, sys, urllib.request, os
from collections import OrderedDict

HERE = os.path.dirname(os.path.abspath(__file__))
KAD = os.path.join(HERE, "..", "index.html")
PROJECT = "project-50fca4c2-1177-4292-916"
KOLEKSI = "rsvp_eusoff"          # kad Zaitul guna "rsvp"


def token():
    try:
        return subprocess.run(["gcloud", "auth", "print-access-token"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        sys.exit("Tidak dapat kelayakan gcloud. Jalankan: gcloud auth login")


def ambil_rekod():
    tok, rekod, page = token(), [], None
    while True:
        url = (f"https://firestore.googleapis.com/v1/projects/{PROJECT}"
               f"/databases/(default)/documents/{KOLEKSI}?pageSize=300")
        if page:
            url += "&pageToken=" + page
        req = urllib.request.Request(url, headers={"Authorization": "Bearer " + tok})
        try:
            with urllib.request.urlopen(req) as r:
                data = json.load(r)
        except urllib.error.HTTPError as e:
            sys.exit(f"Firestore menolak permintaan ({e.code}): {e.read().decode()[:200]}")
        for d in data.get("documents", []):
            f = d.get("fields", {})
            rekod.append({
                "nama":      f.get("nama", {}).get("stringValue", ""),
                "kehadiran": f.get("kehadiran", {}).get("stringValue", ""),
                "bilangan":  int(f.get("bilangan", {}).get("integerValue", 0) or 0),
                "ucapan":    f.get("ucapan", {}).get("stringValue", ""),
                "masa":      f.get("masa", {}).get("stringValue", ""),
            })
        page = data.get("nextPageToken")
        if not page:
            return rekod


def normal(s):
    s = re.sub(r"[^a-z0-9 ]+", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


def senarai_jemputan():
    """Baca window.TETAMU daripada kad jemputan."""
    try:
        html = open(KAD, encoding="utf-8").read()
    except OSError:
        return []
    m = re.search(r"window\.TETAMU\s*=\s*\[(.*?)\];", html, re.S)
    if not m:
        return []
    blok = re.sub(r"//[^\n]*", "", m.group(1))          # buang komen
    nama = re.findall(r'nama:\s*"([^"]+)"', blok)
    nama += [s for s in re.findall(r'"([^"]+)"', blok)
             if s not in nama and not re.match(r"^\d+$", s)]
    return list(OrderedDict.fromkeys(nama))


def main():
    rekod = ambil_rekod()

    # satu rekod terkini bagi setiap nama
    terkini = {}
    for r in rekod:
        k = normal(r["nama"])
        if k and (k not in terkini or r["masa"] > terkini[k]["masa"]):
            terkini[k] = r
    unik = sorted(terkini.values(), key=lambda r: r["nama"].lower())

    hadir = [r for r in unik if r["kehadiran"] == "Hadir"]
    tidak = [r for r in unik if r["kehadiran"] != "Hadir"]
    pax = sum(r["bilangan"] for r in hadir)

    jemputan = senarai_jemputan()
    belum = [n for n in jemputan if normal(n) not in terkini]

    W = 66
    print("\n" + "═" * W)
    print("  RSVP — Walimatul Urus Eusoff".ljust(W))
    print("═" * W)
    print(f"  Hadir           : {len(hadir):>4} jemputan  ({pax} orang)")
    print(f"  Tidak hadir     : {len(tidak):>4} jemputan")
    if jemputan:
        print(f"  Belum jawab     : {len(belum):>4} daripada {len(jemputan)} dijemput")
    if len(rekod) != len(unik):
        print(f"  (nota: {len(rekod) - len(unik)} penghantaran berulang diabaikan)")
    print("═" * W)

    if hadir:
        print("\n  HADIR")
        for r in hadir:
            print(f"    {r['nama'][:38]:<38} {r['bilangan']:>2} orang")
    if tidak:
        print("\n  TIDAK HADIR")
        for r in tidak:
            print(f"    {r['nama'][:38]}")
    if belum:
        print("\n  BELUM JAWAB")
        for n in belum:
            print(f"    {n[:38]}")

    ucapan = [r for r in unik if r["ucapan"].strip()]
    if ucapan:
        print("\n  UCAPAN")
        for r in ucapan:
            print(f"    {r['nama']}:")
            print(f"      “{r['ucapan'][:200]}”")
    print()

    if "--csv" in sys.argv:
        import csv
        path = sys.argv[sys.argv.index("--csv") + 1]
        with open(path, "w", newline="", encoding="utf-8-sig") as fh:
            w = csv.writer(fh)
            w.writerow(["Nama", "Kehadiran", "Bilangan", "Ucapan", "Masa"])
            for r in unik:
                w.writerow([r["nama"], r["kehadiran"], r["bilangan"], r["ucapan"], r["masa"]])
            for n in belum:
                w.writerow([n, "Belum jawab", "", "", ""])
        print(f"  Disimpan ke {path}\n")


if __name__ == "__main__":
    main()
