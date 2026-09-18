import os, renda
Z=os.path.expanduser('~/Documents/GitHub/jemputan-eusoff-zaitul')
E=os.path.expanduser('~/Documents/GitHub/jemputan-eusoff')
FOTO=f'file://{E}/assets/gambar/1.jpg'

TEMA = {
 'zaitul': dict(
   bg='#5e161c', kad='#efe9df', tinta='#2f1c19',
   emas='#a8823c', emas2='#e3c185', renda='#f2e2e3', renda_dalam='#dcc9c5', bujur='#ffffff',
   skrip="'SnellRoundhand','Snell Roundhand','Apple Chancery',cursive", skrip_saiz=140,
   serif="'Arapey',Georgia,serif", sans="'LibreFranklin','Helvetica Neue',Arial,sans-serif",
   fonts=[('Arapey',f'{Z}/assets/21ff46d8ff78a3504f1133eabf422513.woff'),
          ('SnellRoundhand',f'{Z}/assets/2a0b5f90f195029a3b22e69462e34243.woff'),
          ('LibreFranklin',f'{Z}/assets/fb9187b07b309ec842bc6f18a7af7838.woff')]),
 'eusoff': dict(
   bg='#3d5577', kad='#f4efe7', tinta='#22303f',
   emas='#8d6f3f', emas2='#d8bb84', renda='#efe4da', renda_dalam='#cfc2b4', bujur='#ffffff',
   skrip="'kad-alexbrush',cursive", skrip_saiz=152,
   serif="'kad-bodoni',Didot,Georgia,serif", sans="'kad-cormorant',Georgia,serif",
   fonts=[('kad-alexbrush',f'{E}/assets/kad/19126e9a4ea037168bea3a9575c93aff.woff'),
          ('kad-bodoni',f'{E}/assets/kad/83280613fc66ab173d1ee86c8ca899a0.woff'),
          ('kad-cormorant',f'{E}/assets/kad/2883edd9004d7019bbfccbdb94743f24.woff')]),
}

W,H = 1080,1920
KAD_X, KAD_ATAS, KAD_BAWAH = 74, 196, 232      # inset panel krim
TIANG_W = 232

def poster(t):
    c=TEMA[t]
    faces=''.join(f"@font-face{{font-family:'{n}';src:url('file://{p}') format('woff');font-display:block}}"
                  for n,p in c['fonts'])
    tinggi_kad = H-KAD_ATAS-KAD_BAWAH
    tiang = renda.pillar_svg(tinggi_kad, w=TIANG_W, warna=c['renda'])
    import base64
    tiang_uri = 'data:image/svg+xml;base64,' + base64.b64encode(tiang.encode()).decode()
    bujur = renda.renda_bujur(rx=232, ry=282, cx=280, cy=330, warna=c['bujur'], garis=c['renda_dalam'])
    return f'''<!doctype html><meta charset="utf-8"><style>
{faces}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px;height:{H}px;overflow:hidden}}
body{{background:{c['bg']};position:relative;font-family:{c['serif']};-webkit-font-smoothing:antialiased}}
.kad{{position:absolute;left:{KAD_X}px;right:{KAD_X}px;top:{KAD_ATAS}px;bottom:{KAD_BAWAH}px;
  background:{c['kad']};display:flex;flex-direction:column;align-items:center;
  padding:74px 66px 84px;text-align:center;justify-content:center}}
.tiang{{position:absolute;top:{KAD_ATAS}px;height:{tinggi_kad}px;width:{TIANG_W}px;z-index:2}}
.tiang.kiri{{left:{KAD_X-TIANG_W//2}px}}
.tiang.kanan{{right:{KAD_X-TIANG_W//2}px;transform:scaleX(-1)}}
.tagline{{font-size:41px;line-height:1.42;color:{c['tinta']};letter-spacing:.005em}}
.nama{{font-family:{c['skrip']};font-size:{c['skrip_saiz']}px;line-height:1.16;margin-top:6px;white-space:nowrap;
  background:linear-gradient(180deg,{c['emas2']} 0%,{c['emas']} 58%,{c['emas2']} 100%);
  -webkit-background-clip:text;background-clip:text;color:transparent;
  filter:drop-shadow(0 2px 1px rgba(0,0,0,.16));padding:0 12px 16px}}
.bingkai{{position:relative;width:560px;height:660px;margin-top:-6px}}
.bingkai svg{{position:absolute;inset:0;width:100%;height:100%}}
.bingkai img{{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);
  width:464px;height:564px;object-fit:cover;clip-path:ellipse(50% 50% at 50% 50%)}}
.ajak{{font-size:33px;line-height:1.5;color:{c['tinta']};margin-top:44px;max-width:700px}}
.rsvp{{margin-top:44px;font-family:{c['serif']};font-size:37px;letter-spacing:.09em;color:{c['tinta']};
  text-transform:uppercase;border-bottom:2px solid {c['tinta']};padding-bottom:9px}}
</style>
<div class="kad">
  <p class="tagline">Two hearts, and<br>an unforgettable day.</p>
  <h1 class="nama">Eusoff &amp; Zaitul</h1>
  <div class="bingkai">
    <svg viewBox="0 0 560 660">{bujur}</svg>
    <img src="{FOTO}" alt="">
  </div>
  <p class="ajak">We would be honoured to have you join us in<br>celebrating this beautiful beginning of our forever.</p>
  <p class="rsvp">Click for RSVP</p>
</div>
<img class="tiang kiri" src="{tiang_uri}"><img class="tiang kanan" src="{tiang_uri}">
<script>
  var n=document.querySelector('.nama'), had={W-2*KAD_X-264}, s=parseFloat(getComputedStyle(n).fontSize);
  while (n.scrollWidth > had && s > 60) {{ s -= 2; n.style.fontSize = s + 'px'; }}
</script>'''

for t in TEMA:
    open(f'poster-{t}.html','w').write(poster(t))
print('ok')
