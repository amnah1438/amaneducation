// تصوير عرض ترويجي للكتاب التفاعلي إطاراً إطاراً بساعة وهمية (حتمي): node capture.js
// يحتاج خادماً محلياً على المنفذ 8765 من جذر المشروع:  python3 -m http.server 8765
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const FPS = 30, DUR = +(process.env.DUR || 48), W = 1280, H = 720;
const ease = x => { x = Math.min(1, Math.max(0, x)); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };

(async () => {
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: W, height: H } });
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.clock.install({ time: 0 });
  await p.addInitScript(() => { window.__sfxLog = []; window.__manual = true; });
  await p.goto('http://localhost:8765/static/tools/book/index.html#1');
  for (let i = 0; i < 200; i++) { await p.clock.runFor(100); if (await p.evaluate(() => !!window.__book)) break; await new Promise(r => setTimeout(r, 100)); }
  // طبقة العناوين
  await p.evaluate(() => {
    const css = document.createElement('style'); css.textContent = `#ov{position:fixed;inset:0;z-index:50;pointer-events:none;display:grid;place-items:center;direction:rtl;font-family:Tajawal,sans-serif;opacity:0}
    #ov .box{text-align:center;padding:26px 44px;border-radius:26px;background:rgba(20,26,32,.62);backdrop-filter:blur(10px);color:#fff}
    #ov h1{font-size:60px;line-height:1.3}#ov p{font-size:30px;margin-top:8px;opacity:.9}#ov small{display:block;margin-top:18px;font-size:24px;opacity:.85;line-height:1.8}`;
    document.head.appendChild(css);
    const ov = document.createElement('div'); ov.id = 'ov'; ov.innerHTML = '<div class="box"></div>'; document.body.appendChild(ov);
    window.__ov = (html, o) => { const el = document.querySelector('#ov'); if (html !== null) el.firstChild.innerHTML = html; el.style.opacity = o; };
  });
  const TITLE = '<h1>كتاب تفاعلي ثلاثي الأبعاد</h1><p>الدرس ٣ - ٢ · معادلات الجمع والطرح</p>';
  const END = '<h1>جرّب الكتاب بنفسك</h1><p>الميزان · المكعبات · الغطاء السرّي</p><small>تصميم الطالب: يوسف فايز العنزي<br>إشراف المعلم: حمود غصن العنزي</small>';
  const ev = [
    [4.0, () => { const B = window.__book; B.CH[0].tap({ item: B.panL.items_.find(i => i.kind === 'x') }); }],
    [6.6, () => window.__book.go(1)],
    [9.6, () => document.querySelectorAll('#opts .opt')[1].click()],
    [12.6, () => { const B = window.__book; B.removeItem(B.panL, B.panL.items_.find(i => i.kind === 'unit' && !i.dying)); setTimeout(B.onChange, 700); }],
    [14.8, () => { const B = window.__book; B.removeItem(B.panR, B.panR.items_.filter(i => i.kind === 'unit' && !i.dying)[0]); setTimeout(B.onChange, 700); }],
    [16.4, () => { const B = window.__book; B.removeItem(B.panL, B.panL.items_.find(i => i.kind === 'unit' && !i.dying)); B.removeItem(B.panR, B.panR.items_.filter(i => i.kind === 'unit' && !i.dying)[0]); setTimeout(B.onChange, 900); }],
    [20.6, () => window.__book.liftFlap()],
    [25.6, () => window.__book.go(2)],
    [28.6, () => document.querySelectorAll('#opts .opt')[1].click()],
    [31.0, () => window.__book.applyOp('add', 2)],
    [35.0, () => window.__book.go(3)],
    [38.0, () => document.querySelectorAll('#opts .opt')[0].click()],
    [40.4, () => { const B = window.__book; B.subBlock(B.panL, B.panL.items_.find(i => i.kind === 'blk')); }],
    [41.6, () => { const B = window.__book; B.subBlock(B.panR, B.panR.items_.find(i => i.kind === 'blk')); }]
  ].sort((a, c) => a[0] - c[0]);
  const out = process.env.OUT || __dirname + '/_silent.mp4';
  const ff = spawn('ffmpeg', ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const t0 = Date.now(); let k = 0;
  for (let f = 0; f < DUR * FPS; f++) {
    const t = f / FPS;
    while (k < ev.length && t >= ev[k][0]) { await p.evaluate(ev[k][1]); k++; }
    const o = t < 3.9 ? Math.min(1, t / .6) * (1 - ease((t - 3.2) / .7)) : t >= 44.2 ? ease((t - 44.2) / .8) : 0;
    await p.evaluate(([h, op]) => window.__ov(h, op), [t >= 44 ? END : TITLE, o]);
    const B_ty = t < 6.6 ? .55 * (1 - ease(t / 6.4)) : .16 * Math.sin((t - 6.6) * .55);
    await p.evaluate(v => { window.__book.orbit.ty = v; }, B_ty);
    await p.clock.runFor(1000 / FPS);
    await p.evaluate(() => window.__tick(performance.now()));
    const buf = await p.screenshot({ type: 'jpeg', quality: 93 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 60 === 0) console.log(`frame ${f}/${DUR * FPS}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  fs.writeFileSync(__dirname + '/sfx_log.json', JSON.stringify(await p.evaluate(() => window.__sfxLog)));
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close();
})();
