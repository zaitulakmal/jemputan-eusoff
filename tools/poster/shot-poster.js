const { chromium } = require('playwright-core');
(async () => {
  const b = await chromium.launch({ executablePath:'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome', headless:true });
  for (const t of ['zaitul','eusoff']) {
    const p = await b.newPage({ viewport:{width:1080,height:1920} });
    const errs=[]; p.on('requestfailed', r => errs.push(r.url().split('/').pop()));
    await p.goto('file://' + process.cwd() + `/poster-${t}.html`);
    await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(1200);
    await p.screenshot({ path:`poster-${t}.png` });
    console.log(t, 'gagal muat:', errs.length ? errs.join(',') : 'tiada');
    await p.close();
  }
  await b.close();
})();
