// تصوير الإطارات ثم دمج المؤثرات الصوتية:  python3 sounds.py && node render.js
const { chromium } = require('playwright');
const { spawn, execFileSync } = require('child_process');
const FPS = 30;
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
  await p.goto('file://' + __dirname + '/index.html');
  await p.evaluate(() => document.fonts.ready);
  const dur = await p.evaluate(() => window.DURATION);
  const ff = spawn('ffmpeg', ['-y', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'mjpeg', '-i', '-',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', __dirname + '/_silent.mp4'], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < dur * FPS; i++) {
    await p.evaluate(t => render(t), i / FPS);
    const buf = await p.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r)); await b.close();
  execFileSync('ffmpeg', ['-y', '-i', __dirname + '/_silent.mp4', '-i', __dirname + '/sounds.wav', '-map', '0:v', '-map', '1:a',
    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '128k', '-t', String(dur), '-movflags', '+faststart', __dirname + '/warmup_lesson_3_2.mp4']);
  require('fs').unlinkSync(__dirname + '/_silent.mp4');
})();
