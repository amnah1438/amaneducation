// تصوير عرض ترويجي للكتاب التفاعلي إطاراً إطاراً بساعة وهمية (حتمي): node capture.js
// يحتاج خادماً محلياً على المنفذ 8765 من جذر المشروع:  python3 -m http.server 8765
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const fs = require('fs');
const MODE = process.env.MODE || 'h';            // h = أفقي ١٢٨٠×٧٢٠ ، v = عمودي ٧٢٠×١٢٨٠
const V = MODE === 'v';
const FPS = 30, DUR = +(process.env.DUR || (V ? 60 : 49)), W = V ? 720 : 1280, H = V ? 1280 : 720;
const ease = x => { x = Math.min(1, Math.max(0, x)); return x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2; };

(async () => {
  const b = await chromium.launch({ args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: W, height: H } });
  p.on('pageerror', e => console.log('PAGEERR', e.message));
  await p.clock.install({ time: 0 });
  await p.clock.pauseAt(1000);                    // الساعة متوقفة: لا يمرّ الوقت إلا بخطوات runFor (تصوير حتمي)
  await p.addInitScript(v => { window.__sfxLog = []; window.__manual = true; window.__V = v; }, V);
  await p.goto('http://localhost:8765/static/tools/book/index.html#1');
  for (let i = 0; i < 200; i++) { await p.clock.runFor(100); if (await p.evaluate(() => !!window.__book)) break; await new Promise(r => setTimeout(r, 100)); }
  // طبقة العناوين
  await p.evaluate(() => {
    const css = document.createElement('style'); css.textContent = `#ov{position:fixed;inset:0;z-index:50;pointer-events:none;display:grid;place-items:center;direction:rtl;font-family:Tajawal,sans-serif;opacity:0}
    #ov .box{text-align:center;padding:26px 44px;border-radius:26px;background:rgba(20,26,32,.62);backdrop-filter:blur(10px);color:#fff}
    #ov h1{font-size:60px;line-height:1.3}#ov p{font-size:30px;margin-top:8px;opacity:.9}#ov small{display:block;margin-top:18px;font-size:24px;opacity:.85;line-height:1.8}`;
    document.head.appendChild(css);
    if (window.__V) { const c2 = document.createElement('style'); c2.textContent = `#card{left:14px!important;right:14px!important;top:max(24px,env(safe-area-inset-top))!important;width:auto!important;padding:18px 22px!important}#card h2{font-size:27px!important}#card p{font-size:21px!important}.opt,.act{font-size:21px!important;padding:12px 16px!important}#card .tag{font-size:16px!important}#card .eqbox{font-size:25px!important}#eqchip{bottom:128px!important;font-size:38px!important}#eqchip .st{font-size:18px!important}#bar{bottom:28px!important;width:calc(100vw - 28px)!important}#bar .ttl{display:block!important;font-size:16px!important}#ov h1{font-size:44px!important}#ov p{font-size:26px!important}#ov .box{padding:22px 30px!important;margin:0 18px}`; document.head.appendChild(c2); }
    const ov = document.createElement('div'); ov.id = 'ov'; ov.innerHTML = '<div class="box"></div>'; document.body.appendChild(ov);
    window.__ov = (html, o) => { const el = document.querySelector('#ov'); if (html !== null) el.firstChild.innerHTML = html; el.style.opacity = o; };
  });
  const TITLE = '<h1>كتاب تفاعلي ثلاثي الأبعاد</h1><p>الدرس ٣ - ٢ · معادلات الجمع والطرح</p>';
  const END = '<h1>جرّب الكتاب بنفسك</h1><p>الميزان · المكعبات · الغطاء السرّي</p>';
const fx = {
    lit: () => { const B = window.__book; B.CH[0].tap({ item: B.panL.items_.find(i => i.kind === 'x') }); },
    go: n => window.__book.go(n),
    pick: k => document.querySelectorAll('#opts .opt')[k].click(),
    remL: () => { const B = window.__book; B.removeItem(B.panL, B.panL.items_.find(i => i.kind === 'unit' && !i.dying)); setTimeout(B.onChange, 700); },
    remR: () => { const B = window.__book; B.removeItem(B.panR, B.panR.items_.filter(i => i.kind === 'unit' && !i.dying)[0]); setTimeout(B.onChange, 700); },
    remBoth: () => { const B = window.__book; B.removeItem(B.panL, B.panL.items_.find(i => i.kind === 'unit' && !i.dying)); B.removeItem(B.panR, B.panR.items_.filter(i => i.kind === 'unit' && !i.dying)[0]); setTimeout(B.onChange, 900); },
    flap: () => window.__book.liftFlap(),
    add2: () => window.__book.applyOp('add', 2),
    blkL: () => { const B = window.__book; B.subBlock(B.panL, B.panL.items_.find(i => i.kind === 'blk')); },
    blkR: () => { const B = window.__book; B.subBlock(B.panR, B.panR.items_.find(i => i.kind === 'blk')); }
  };
  const T = V ? { // عمودي: دقيقة
    end: 55.2, title: 3.9,
    ev: [[4.0, 'lit'], [7.0, 'go', 1], [10.5, 'pick', 1], [13.5, 'remL'], [16.0, 'remR'], [18.2, 'remBoth'], [23.2, 'flap'], [31.4, 'go', 2], [34.4, 'pick', 1], [36.8, 'add2'], [42.6, 'go', 3], [45.6, 'pick', 0], [48.0, 'blkL'], [49.4, 'blkR']]
  } : {
    end: 45.2, title: 3.9,
    ev: [[4.0, 'lit'], [6.6, 'go', 1], [9.6, 'pick', 1], [12.6, 'remL'], [14.8, 'remR'], [16.4, 'remBoth'], [20.6, 'flap'], [27.0, 'go', 2], [30.0, 'pick', 1], [32.4, 'add2'], [36.0, 'go', 3], [39.0, 'pick', 0], [41.4, 'blkL'], [42.6, 'blkR']]
  };
  const ev = T.ev.map(([t, k, a]) => [t, fx[k], a]).sort((a, c) => a[0] - c[0]);
  const out = process.env.OUT || __dirname + `/_silent_${MODE}.mp4`;
  const ff = spawn('ffmpeg', ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  const T0 = await p.evaluate(() => performance.now());   // لحساب أزمنة المؤثرات الصوتية من بداية الفيديو
  const t0 = Date.now(); let k = 0;
  for (let f = 0; f < DUR * FPS; f++) {
    const t = f / FPS;
    while (k < ev.length && t >= ev[k][0]) { await p.evaluate(ev[k][1], ev[k][2]); k++; }
    const o = t < 3.9 ? Math.min(1, t / .6) * (1 - ease((t - 3.2) / .7)) : t >= T.end ? ease((t - T.end) / .8) : 0;
    await p.evaluate(([h, op]) => window.__ov(h, op), [t >= T.end - .4 ? END : TITLE, o]);
    const B_ty = t < 6.6 ? .55 * (1 - ease(t / 6.4)) : .16 * Math.sin((t - 6.6) * .55);
    await p.evaluate(v => { window.__book.orbit.ty = v; }, B_ty);
    await p.clock.runFor(1000 / FPS);
    await p.evaluate(() => window.__tick(performance.now()));
    const buf = await p.screenshot({ type: 'jpeg', quality: 93 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 60 === 0) console.log(`frame ${f}/${DUR * FPS}  ${((Date.now() - t0) / 1000).toFixed(0)}s`);
  }
  fs.writeFileSync(__dirname + `/sfx_log_${MODE}.json`, JSON.stringify((await p.evaluate(() => window.__sfxLog)).map(([kd, f, ms]) => [kd, f, ms - T0])));
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close();
})();
