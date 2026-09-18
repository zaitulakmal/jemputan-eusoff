import os, base64, renda
Z=os.path.expanduser('~/Documents/GitHub/jemputan-eusoff-zaitul')
E=os.path.expanduser('~/Documents/GitHub/jemputan-eusoff')
FOTO=f'file://{E}/assets/gambar/1.jpg'

# ── ukuran diambil daripada kad rujukan (kad 373x520 dalam tangkapan skrin) ──
W,H       = 1080,1920
KAD_W     = 810                    # 75% lebar kanvas
KAD_H     = int(KAD_W/0.717)       # nisbah kad rujukan
KAD_X     = (W-KAD_W)//2
KAD_Y     = (H-KAD_H)//2
OVAL_W, OVAL_H = 484, 600          # termasuk gelang renda
OVAL_Y    = int(KAD_H*0.221)       # dari atas kad
NAMA_Y    = int(KAD_H*0.221) + 26  # nama bertindih bahagian atas oval
TIANG_W, TIANG_H = 132, 640

TEMA = {
 'zaitul': dict(bg='#5e161c', kad='#eceae0', tinta='#2f1c19',
   emas='#a8823c', emas2='#e6c68d', renda='#e8cfd2', renda_titik='#ffffff',
   bujur='#ffffff', bujur_garis='#e6d9d4',
   skrip="'SnellRoundhand','Snell Roundhand','Apple Chancery',cursive",
   serif="'Arapey',Georgia,serif",
   fonts=[('Arapey',f'{Z}/assets/21ff46d8ff78a3504f1133eabf422513.woff'),
          ('SnellRoundhand',f'{Z}/assets/2a0b5f90f195029a3b22e69462e34243.woff')]),
 'eusoff': dict(bg='#3d5577', kad='#f2eee6', tinta='#22303f',
   emas='#8d6f3f', emas2='#dcc08c', renda='#dfe6ef', renda_titik='#ffffff',
   bujur='#ffffff', bujur_garis='#dcd3c8',
   skrip="'kad-alexbrush',cursive",
   serif="'kad-bodoni',Didot,Georgia,serif",
   fonts=[('kad-alexbrush',f'{E}/assets/kad/19126e9a4ea037168bea3a9575c93aff.woff'),
          ('kad-bodoni',f'{E}/assets/kad/83280613fc66ab173d1ee86c8ca899a0.woff')]),
}

def poster(t):
    c=TEMA[t]
    faces=''.join(f"@font-face{{font-family:'{n}';src:url('file://{p}') format('woff');font-display:block}}"
                  for n,p in c['fonts'])
    tiang = renda.pillar_svg(TIANG_H, w=TIANG_W, unit_h=160, warna=c['renda'], titik=c['renda_titik'])
    tiang_uri='data:image/svg+xml;base64,'+base64.b64encode(tiang.encode()).decode()
    rx, ry = OVAL_W*0.5/1.16, OVAL_H*0.5/1.16
    bujur = renda.renda_bujur(rx=rx, ry=ry, cx=OVAL_W/2, cy=OVAL_H/2,
                              warna=c['bujur'], garis=c['bujur_garis'])
    tiang_y = KAD_Y + int(KAD_H*0.22)
    return f'''<!doctype html><meta charset="utf-8"><style>
{faces}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}
body{{background:{c['bg']};position:relative;font-family:{c['serif']};-webkit-font-smoothing:antialiased}}
.kad{{position:absolute;left:{KAD_X}px;top:{KAD_Y}px;width:{KAD_W}px;height:{KAD_H}px;background:{c['kad']}}}
.tagline{{position:absolute;left:0;right:0;top:{int(KAD_H*0.100)}px;text-align:center;
  font-size:31px;line-height:1.36;color:{c['tinta']}}}
.bingkai{{position:absolute;left:50%;transform:translateX(-50%);top:{OVAL_Y}px;
  width:{OVAL_W}px;height:{OVAL_H}px}}
.bingkai svg{{position:absolute;inset:0;width:100%;height:100%}}
.bingkai img{{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);
  width:{int(OVAL_W/1.16)-6}px;height:{int(OVAL_H/1.16)-6}px;object-fit:cover;
  clip-path:ellipse(50% 50% at 50% 50%)}}
.nama{{position:absolute;left:50%;transform:translateX(-50%);width:max-content;top:{NAMA_Y}px;z-index:3;
  font-family:{c['skrip']};font-size:150px;line-height:1;white-space:nowrap;
  background:linear-gradient(180deg,{c['emas2']} 0%,{c['emas']} 56%,{c['emas2']} 100%);
  -webkit-background-clip:text;background-clip:text;color:transparent;
  filter:drop-shadow(0 2px 2px rgba(0,0,0,.28)) drop-shadow(0 0 10px rgba(255,255,255,.55));padding:0 10px}}
.ajak{{position:absolute;left:46px;right:46px;top:{int(KAD_H*0.815)}px;text-align:center;
  font-size:27px;line-height:1.34;color:{c['tinta']}}}
.rsvp{{position:absolute;left:0;right:0;top:{int(KAD_H*0.918)}px;text-align:center;color:{c['tinta']};
  font-size:28px;letter-spacing:.03em;text-transform:uppercase}}
.rsvp span{{border-bottom:1.6px solid {c['tinta']};padding-bottom:5px}}
.tiang{{position:absolute;top:{tiang_y}px;width:{TIANG_W}px;height:{TIANG_H}px;z-index:4}}
.tiang.kiri{{left:{KAD_X-int(TIANG_W*0.66)}px}}
.tiang.kanan{{left:{KAD_X+KAD_W-int(TIANG_W*0.34)}px;transform:scaleX(-1)}}
</style>
<div class="kad">
  <p class="tagline">Two hearts, and<br>an unforgettable day.</p>
  <div class="bingkai"><svg viewBox="0 0 {OVAL_W} {OVAL_H}">{bujur}</svg><img src="{FOTO}" alt=""></div>
  <h1 class="nama">Eusoff &amp; Zaitul</h1>
  <p class="ajak">We would be honoured to have you join us in celebrating<br>this beautiful beginning of our forever.</p>
  <p class="rsvp"><span>Click for RSVP</span></p>
</div>
<img class="tiang kiri" src="{tiang_uri}"><img class="tiang kanan" src="{tiang_uri}">
<script>
  var n=document.querySelector('.nama'), had={int(KAD_W*0.88)}, s=parseFloat(getComputedStyle(n).fontSize);
  while (n.scrollWidth > had && s > 60) {{ s -= 2; n.style.fontSize = s + 'px'; }}
  while (n.scrollWidth < had - 40 && s < 190) {{ s += 2; n.style.fontSize = s + 'px'; }}
</script>'''

for t in TEMA:
    open(f'poster-{t}.html','w').write(poster(t))
print('kad', KAD_W, 'x', KAD_H, 'pada', KAD_X, KAD_Y)
