const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
// Lámina 90 x 60 cm a 200 ppp = 7087 x 4724 px
const PXW = 7087, PXH = 4724;
(async () => {
  const dir = process.argv[2]; const pdf = process.argv[3] === 'pdf';
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: PXW, height: PXH } });
  for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.svg'))) {
    const svg = fs.readFileSync(path.join(dir, f), 'utf8')
      .replace(/<svg([^>]*?) width="\d+" height="\d+"/, '<svg$1 width="100%" height="100%"');
    const base = path.join(dir, f.replace('.svg', ''));
    await p.setViewportSize({ width: PXW, height: PXH });
    await p.setContent(`<html><head><style>@page{size:90cm 60cm;margin:0}html,body{margin:0;padding:0}
      #w{width:${PXW}px;height:${PXH}px}@media print{#w{width:90cm;height:60cm}}</style></head>
      <body><div id="w">${svg}</div></body></html>`, { waitUntil: 'load' });
    await p.evaluate(() => document.fonts.ready);
    await p.screenshot({ path: base + '.raw.png', clip: { x: 0, y: 0, width: PXW, height: PXH } });
    if (pdf) await p.pdf({ path: base + '.pdf', width: '90cm', height: '60cm', printBackground: true, pageRanges: '1' });
    console.log('ok', f);
  }
  await b.close();
})();
