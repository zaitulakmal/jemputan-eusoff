import math

def _pt(cx, cy, r, a): return (cx + r*math.cos(a), cy + r*math.sin(a))

def sabit(cx, cy, R, r, a0, a1, warna):
    """Bentuk sabit (crescent): lengkung luar R, balik dengan lengkung dalam r."""
    x0,y0 = _pt(cx,cy,R,a0); x1,y1 = _pt(cx,cy,R,a1)
    x2,y2 = _pt(cx,cy,r,a1); x3,y3 = _pt(cx,cy,r,a0)
    besar = 1 if (a1-a0) % (2*math.pi) > math.pi else 0
    return (f'<path d="M {x0:.1f} {y0:.1f} A {R} {R} 0 {besar} 1 {x1:.1f} {y1:.1f} '
            f'L {x2:.1f} {y2:.1f} A {r} {r} 0 {besar} 0 {x3:.1f} {y3:.1f} Z" fill="{warna}"/>')

def titis(cx, cy, w, h, warna, putar=0):
    """Kelopak/titisan menegak."""
    return (f'<path d="M {cx} {cy-h/2} C {cx+w/2} {cy-h/6}, {cx+w/2} {cy+h/3}, {cx} {cy+h/2} '
            f'C {cx-w/2} {cy+h/3}, {cx-w/2} {cy-h/6}, {cx} {cy-h/2} Z" fill="{warna}" '
            f'transform="rotate({putar} {cx} {cy})"/>')

def tiang(w=150, h=200, warna='#e8cfd2'):
    cx = w*0.5
    p=[]
    # palmet atas: 5 kelopak berkipas
    for i,(dx,ang,sk) in enumerate(((0,0,1.0),(-1,-26,.85),(1,26,.85),(-1,-50,.62),(1,50,.62))):
        p.append(titis(cx+dx*18*abs(sk), h*0.17, 22*sk, 58*sk, warna, ang))
    # sepasang sabit bercermin (gulungan)
    for s in (-1,1):
        p.append(sabit(cx+s*30, h*0.47, 42, 30, math.radians(-100 if s>0 else -80),
                       math.radians(150 if s>0 else 260), warna))
        p.append(sabit(cx+s*22, h*0.74, 30, 21, math.radians(-120 if s>0 else -60),
                       math.radians(120 if s>0 else 300), warna))
    # berlian & titik paksi
    p.append(f'<path d="M {cx} {h*0.33} L {cx+11} {h*0.395} L {cx} {h*0.46} L {cx-11} {h*0.395} Z" fill="{warna}"/>')
    p.append(f'<circle cx="{cx}" cy="{h*0.60}" r="6" fill="{warna}"/>')
    p.append(titis(cx, h*0.90, 20, 46, warna, 180))
    return ''.join(p)

def pillar_svg(tinggi, w=150, unit_h=200, warna='#e8cfd2', titik='#ffffff'):
    n = math.ceil(tinggi/unit_h)
    body = ''.join(f'<g transform="translate(0 {i*unit_h})">{tiang(w, unit_h, warna)}</g>' for i in range(n))
    rel=''
    for x in (w*0.5-54, w*0.5+54):
        rel += f'<line x1="{x}" y1="0" x2="{x}" y2="{tinggi}" stroke="{warna}" stroke-width="1.6" opacity=".7"/>'
        for i in range(int(tinggi//30)+1):
            rel += f'<circle cx="{x}" cy="{i*30+15}" r="3.6" fill="{titik}"/>'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{tinggi}" viewBox="0 0 {w} {tinggi}">'
            f'{body}{rel}</svg>')

def renda_bujur(rx, ry, cx, cy, warna='#ffffff', garis='#e6d9d4'):
    out=[]; tebal = 0.17*rx
    R1x, R1y = rx+tebal, ry+tebal
    out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{R1x}" ry="{R1y}" fill="{warna}"/>')
    n1=54
    for i in range(n1):
        a=2*math.pi*i/n1
        out.append(f'<circle cx="{cx+R1x*math.cos(a):.1f}" cy="{cy+R1y*math.sin(a):.1f}" r="{tebal*0.5:.1f}" fill="{warna}"/>')
    n2=28
    for i in range(n2):
        a=2*math.pi*i/n2+math.pi/n2
        out.append(f'<circle cx="{cx+(rx+tebal*0.6)*math.cos(a):.1f}" cy="{cy+(ry+tebal*0.6)*math.sin(a):.1f}" '
                   f'r="{tebal*0.19:.1f}" fill="none" stroke="{garis}" stroke-width="1.5"/>')
    out.append(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{garis}" stroke-width="2"/>')
    return ''.join(out)
