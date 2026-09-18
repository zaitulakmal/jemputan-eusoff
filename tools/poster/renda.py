import math

def _rosette(cx, cy, r=26, w=9, n=8, warna='#f2e2e3', tebal=1.8):
    p=[f'<circle cx="{cx}" cy="{cy}" r="5" fill="{warna}"/>']
    for i in range(n):
        a = 180*i/n
        p.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{w}" ry="{r}" fill="none" stroke="{warna}" '
                 f'stroke-width="{tebal}" transform="rotate({a:.1f} {cx} {cy})"/>')
    return ''.join(p)

def tiang(w=300, h=460, warna='#f2e2e3', tebal=2.0):
    """Unit tiang renda: rel nipis, bingkai ogee, rosette, sulur dan mutiara."""
    cx, half = w*0.5, 104
    p=[]
    for s in (-1,1):                                   # rel menegak nipis
        p.append(f'<line x1="{cx+s*half}" y1="0" x2="{cx+s*half}" y2="{h}" stroke="{warna}" stroke-width="{tebal*0.8}" opacity=".85"/>')
    # bingkai ogee (dua lengkung bercermin bertemu di atas & bawah)
    for s in (-1,1):
        p.append(f'<path d="M {cx} 4 C {cx+s*96} {h*0.16}, {cx+s*96} {h*0.34}, {cx} {h*0.5} '
                 f'C {cx+s*96} {h*0.66}, {cx+s*96} {h*0.84}, {cx} {h-4}" fill="none" stroke="{warna}" stroke-width="{tebal}"/>')
        p.append(f'<path d="M {cx} 26 C {cx+s*70} {h*0.19}, {cx+s*70} {h*0.31}, {cx} {h*0.5} '
                 f'C {cx+s*70} {h*0.69}, {cx+s*70} {h*0.81}, {cx} {h-26}" fill="none" stroke="{warna}" stroke-width="{tebal*0.7}" opacity=".8"/>')
        # sulur berpusing keluar dari pinggang
        p.append(f'<path d="M {cx+s*60} {h*0.5} C {cx+s*112} {h*0.44}, {cx+s*126} {h*0.52}, {cx+s*96} {h*0.58} '
                 f'C {cx+s*80} {h*0.60}, {cx+s*82} {h*0.52}, {cx+s*96} {h*0.51}" fill="none" stroke="{warna}" stroke-width="{tebal}"/>')
        # daun halus atas & bawah
        for yy in (0.22, 0.78):
            p.append(f'<path d="M {cx} {h*yy} C {cx+s*46} {h*(yy-0.045)}, {cx+s*74} {h*(yy+0.01)}, {cx+s*40} {h*(yy+0.05)}" fill="none" stroke="{warna}" stroke-width="{tebal*0.8}"/>')
    p.append(_rosette(cx, h*0.5, warna=warna, tebal=tebal*0.9))
    # mutiara pada paksi dan rel
    for i in range(10):
        y = h*(0.05+i*0.1)
        p.append(f'<circle cx="{cx}" cy="{y:.1f}" r="3.2" fill="{warna}" opacity=".9"/>')
    for i in range(7):
        y = h*(0.07+i*0.145)
        for s in (-1,1):
            p.append(f'<circle cx="{cx+s*half}" cy="{y:.1f}" r="4.2" fill="{warna}"/>')
    # skalop pada tepi dalam
    n=9
    for i in range(n):
        y = h*i/n
        p.append(f'<path d="M {cx+half} {y:.1f} A 26 26 0 0 1 {cx+half} {y+h/n:.1f}" fill="none" stroke="{warna}" stroke-width="{tebal*0.75}" opacity=".9"/>')
    return ''.join(p)

def pillar_svg(tinggi, w=300, unit_h=460, **kw):
    n = math.ceil(tinggi/unit_h)
    body = ''.join(f'<g transform="translate(0 {i*unit_h})">{tiang(w, unit_h, **kw)}</g>' for i in range(n))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{tinggi}" viewBox="0 0 {w} {tinggi}">{body}</svg>')

def renda_bujur(rx, ry, cx, cy, warna='#ffffff', garis='#e3d3cf'):
    out=[f'<ellipse cx="{cx}" cy="{cy}" rx="{rx+30}" ry="{ry+30}" fill="{warna}"/>']
    n=46
    for i in range(n):                                  # skalop luar
        a=2*math.pi*i/n
        out.append(f'<circle cx="{cx+(rx+30)*math.cos(a):.1f}" cy="{cy+(ry+30)*math.sin(a):.1f}" r="17" fill="{warna}"/>')
    for i in range(n):                                  # lubang renda
        a=2*math.pi*i/n+math.pi/n
        out.append(f'<circle cx="{cx+(rx+15)*math.cos(a):.1f}" cy="{cy+(ry+15)*math.sin(a):.1f}" r="6.5" fill="none" stroke="{garis}" stroke-width="1.6"/>')
    out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx+2}" ry="{ry+2}" fill="none" stroke="{garis}" stroke-width="1.8"/>')
    return ''.join(out)
