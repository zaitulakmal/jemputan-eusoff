import os
Z=os.path.expanduser('~/Documents/GitHub/jemputan-eusoff-zaitul')
E=os.path.expanduser('~/Documents/GitHub/jemputan-eusoff')
FOTO=f'file://{E}/assets/gambar/1.jpg'

TEMA = {
 'zaitul': dict(
   bg='#5e161c', bg2='#4a1016', kad='#efe7dc', tinta='#2e1b18', halus='#6b5449',
   emas='#a8823c', emas2='#e0bd7a', garis='rgba(107,39,55,.30)',
   skrip="'SnellRoundhand','Snell Roundhand','Apple Chancery',cursive",
   serif="'Arapey',Georgia,serif", sans="'LibreFranklin','Helvetica Neue',Arial,sans-serif",
   fonts=[('Arapey',f'{Z}/assets/21ff46d8ff78a3504f1133eabf422513.woff'),
          ('SnellRoundhand',f'{Z}/assets/2a0b5f90f195029a3b22e69462e34243.woff'),
          ('LibreFranklin',f'{Z}/assets/fb9187b07b309ec842bc6f18a7af7838.woff')],
   sisi=f'file://{Z}/assets/8badf53d222d.png', sisi_lebar=300, sisi_op=1,
   url='eusoff-zaitul.web.app', skrip_saiz=140, nama_atas=4, sisi_x=-40, sisi_putar=0),
 'eusoff': dict(
   bg='#3d5577', bg2='#33465f', kad='#f4efe7', tinta='#22303f', halus='#5d6b7d',
   emas='#8d6f3f', emas2='#d8bb84', garis='rgba(61,85,119,.30)',
   skrip="'kad-alexbrush',cursive",
   serif="'kad-bodoni',Didot,Georgia,serif", sans="'kad-cormorant',Georgia,serif",
   fonts=[('kad-alexbrush',f'{E}/assets/kad/19126e9a4ea037168bea3a9575c93aff.woff'),
          ('kad-bodoni',f'{E}/assets/kad/83280613fc66ab173d1ee86c8ca899a0.woff'),
          ('kad-cormorant',f'{E}/assets/kad/2883edd9004d7019bbfccbdb94743f24.woff')],
   sisi=f'file://{E}/assets/taman-kiri.svg', sisi_lebar=620, sisi_op=1,
   url='majlis-eusoff.web.app', skrip_saiz=150, nama_atas=4, sisi_x=-250, sisi_putar=90),
}

def poster(t):
    c=TEMA[t]
    faces=''.join(f"@font-face{{font-family:'{n}';src:url('file://{p}') format('woff');font-display:block}}" for n,p in c['fonts'])
    return f'''<!doctype html><meta charset="utf-8"><style>
{faces}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:1080px;height:1920px;overflow:hidden}}
body{{background:radial-gradient(120% 80% at 50% 12%, {c['bg']} 0%, {c['bg2']} 100%);position:relative;
  font-family:{c['serif']};-webkit-font-smoothing:antialiased}}
.sisi{{position:absolute;top:50%;transform:translateY(-50%);width:{c['sisi_lebar']}px;opacity:{c['sisi_op']};pointer-events:none}}
.sisi.kiri{{left:{c['sisi_x']}px;transform:translateY(-50%) rotate({c['sisi_putar']}deg)}}
.sisi.kanan{{right:{c['sisi_x']}px;transform:translateY(-50%) scaleX(-1) rotate({c['sisi_putar']}deg)}}
.kad{{position:absolute;left:96px;right:96px;top:150px;background:{c['kad']};
  box-shadow:0 30px 80px rgba(0,0,0,.35);display:flex;flex-direction:column;align-items:center;
  padding:84px 70px 74px;text-align:center;justify-content:flex-start}}
.kad::after{{content:"";position:absolute;inset:16px;border:1px solid {c['garis']};pointer-events:none}}
.tagline{{font-family:{c['serif']};font-size:39px;line-height:1.45;color:{c['tinta']};letter-spacing:.01em}}
.nama{{font-family:{c['skrip']};font-size:{c['skrip_saiz']}px;line-height:1.18;margin-top:{c['nama_atas']}px;white-space:nowrap;
  background:linear-gradient(180deg,{c['emas2']} 0%,{c['emas']} 55%,{c['emas2']} 100%);
  -webkit-background-clip:text;background-clip:text;color:transparent;
  filter:drop-shadow(0 2px 1px rgba(0,0,0,.18));padding:0 10px 14px}}
.bingkai{{position:relative;width:560px;height:660px;margin-top:6px}}
.bingkai svg{{position:absolute;inset:0;width:100%;height:100%}}
.bingkai img{{position:absolute;left:50%;top:50%;transform:translate(-50%,-50%);
  width:470px;height:570px;object-fit:cover;clip-path:ellipse(50% 50% at 50% 50%)}}
.ajak{{font-family:{c['serif']};font-size:35px;line-height:1.5;color:{c['tinta']};max-width:780px;margin-top:54px}}
.rsvp{{margin-top:56px;font-family:{c['sans']};font-size:34px;letter-spacing:.16em;color:{c['tinta']};
  text-transform:uppercase;border-bottom:2px solid {c['tinta']};padding-bottom:8px}}
.pautan{{margin-top:22px;font-family:{c['sans']};font-size:26px;letter-spacing:.06em;color:{c['halus']}}}
.tarikh{{position:absolute;left:0;right:0;bottom:104px;text-align:center;font-family:{c['sans']};
  font-size:30px;letter-spacing:.34em;text-transform:uppercase;color:{c['kad']};opacity:.92}}
</style>
<img class="sisi kiri" src="{c['sisi']}"><img class="sisi kanan" src="{c['sisi']}">
<div class="kad">
  <p class="tagline">Two hearts, and<br>an unforgettable day.</p>
  <h1 class="nama">Eusoff &amp; Zaitul</h1>
  <div class="bingkai">
    <img src="{FOTO}" alt="">
    <svg viewBox="0 0 560 660" fill="none">
      <ellipse cx="280" cy="330" rx="243" ry="293" stroke="{c['emas']}" stroke-width="2.5"/>
      <ellipse cx="280" cy="330" rx="252" ry="302" stroke="{c['emas']}" stroke-width="1" opacity=".6"/>
      <g fill="{c['kad']}" stroke="{c['emas']}" stroke-width="1.6">{{RENDA}}</g>
    </svg>
  </div>
  <p class="ajak">We would be honoured to have you join us in<br>celebrating this beautiful beginning of our forever.</p>
  <p class="rsvp">Click for RSVP</p>
  <p class="pautan">{c['url']}</p>
</div>
<p class="tarikh">12 . 12 . 2026</p>
<script>
  /* kecilkan nama sehingga muat satu baris dalam kad */
  var n=document.querySelector('.nama'), had=720, s=parseFloat(getComputedStyle(n).fontSize);
  while (n.scrollWidth > had && s > 60) {{ s -= 2; n.style.fontSize = s + 'px'; }}
</script>'''

import math
def renda(n=46, rx=252, ry=302, r=15):
    out=[]
    for i in range(n):
        a=2*math.pi*i/n
        x=280+rx*math.cos(a); y=330+ry*math.sin(a)
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}"/>')
    return ''.join(out)

for t in TEMA:
    open(f'poster-{t}.html','w').write(poster(t).replace('{RENDA}', renda()))
print('ok')
