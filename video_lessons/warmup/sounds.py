# يبني الصوت النهائي: صوت المعلّم (مضبوط) + موسيقى خلفية هادئة تنخفض عند الكلام + مؤثرات صغيرة
# الاستعمال: python3 sounds.py   ← ينتج final_audio.wav
import numpy as np, wave, subprocess
SR = 44100
D = 110.0
N = int(SR * D)

def save(path, x):
    x = np.clip(x, -1, 1)
    w = wave.open(path, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((x * 32000).astype(np.int16).tobytes()); w.close()

def note(f, dur, kind):
    n = int(dur * SR); t = np.arange(n) / SR
    if kind == 'pluck':   # نغمة شبيهة بالماريمبا
        s = np.sin(2*np.pi*f*t) + .35*np.sin(2*np.pi*2*f*t)*np.exp(-t*14) + .15*np.sin(2*np.pi*4*f*t)*np.exp(-t*30)
        return s * np.minimum(1, t/.004) * np.exp(-t*7)
    if kind == 'pad':
        s = np.sin(2*np.pi*f*t) + .5*np.sin(2*np.pi*f*1.003*t) + .25*np.sin(2*np.pi*2*f*t)
        e = np.minimum(1, t/.9) * np.minimum(1, (dur - t)/.9)
        return s * e
    if kind == 'bass':
        s = np.sin(2*np.pi*f*t) + .3*np.sin(2*np.pi*2*f*t)
        return s * np.minimum(1, t/.01) * np.exp(-t*3.2)

def music():
    m = np.zeros(N + 5*SR)
    bpm = 104; beat = 60 / bpm; bar = 4 * beat
    hz = lambda midi: 440 * 2 ** ((midi - 69) / 12)
    # دورة هادئة: دو - لا - فا - صول
    chords = [(48, [60, 64, 67]), (45, [57, 60, 64]), (53, [57, 60, 65]), (43, [55, 59, 62])]
    pent = {0: [72, 76, 79, 76, 84, 79, 76, 79], 1: [69, 72, 76, 72, 81, 76, 72, 76],
            2: [72, 77, 81, 77, 84, 81, 77, 81], 3: [71, 74, 79, 74, 83, 79, 74, 79]}
    nbars = int(D / bar) + 2
    for b in range(nbars):
        t0 = b * bar; ci = b % 4
        root, tri = chords[ci]
        def put(at, sig, v):
            i = int(at * SR)
            if i < len(m): m[i:i+len(sig)] += sig[:len(m)-i] * v
        for p in tri: put(t0, note(hz(p - 12), bar, 'pad'), .10)
        put(t0, note(hz(root - 12), beat * 1.9, 'bass'), .30)
        put(t0 + 2 * beat, note(hz(root - 12), beat * 1.9, 'bass'), .24)
        for k, p in enumerate(pent[ci]):
            if (b // 2) % 2 == 1 and k % 2 == 1: continue   # تنويع خفيف كل عدة موازير
            put(t0 + k * beat / 2, note(hz(p), beat, 'pluck'), .12)
    m = m[:N]
    fade = np.ones(N); fade[:int(2*SR)] = np.linspace(0, 1, int(2*SR)); fade[-int(3*SR):] = np.linspace(1, 0, int(3*SR))
    return m * fade

def sfx():
    x = np.zeros(N + 2*SR)
    def put(at, sig, v=1.0):
        i = int(at * SR); x[i:i+len(sig)] += sig[:len(x)-i] * v
    def pop():
        n = int(.14*SR); t = np.arange(n)/SR
        return np.sin(2*np.pi*np.cumsum(900 - 5000*t)/SR) * np.minimum(1, t/.003) * np.exp(-t*22)
    def ding():
        n = int(1.2*SR); t = np.arange(n)/SR
        s = sum(np.sin(2*np.pi*f*t)*a for f, a in [(784, 1), (988, .8), (1319, .7), (1568, .4)])
        return s * np.minimum(1, t/.004) * np.exp(-t*4.5) / 3
    def chord(at):
        for f, d in [(523, 0), (659, .12), (784, .24), (1047, .4)]:
            n = int(1.0*SR); t = np.arange(n)/SR
            put(at + d, np.sin(2*np.pi*f*t) * np.minimum(1, t/.004) * np.exp(-t*4), .30)
    for at in [.3, 3.45, 5.8, 34.6, 37.5, 58.2, 61.9, 66.0, 69.4, 75.7, 79.4, 84.0, 91.7, 106.2]: put(at, pop(), .35)
    for at in [24.5, 51.2]: put(at, ding(), .6)
    chord(107.4)
    return x[:N]

# 1) تنظيف صوت المعلّم: قص الترددات المنخفضة، ضغط خفيف، توحيد الشدة، ثم تمديده لطول الفيديو
subprocess.run(['ffmpeg', '-y', '-i', 'voice.wav', '-af',
    'highpass=f=90,lowpass=f=11000,acompressor=threshold=-21dB:ratio=3:attack=8:release=120:makeup=3,'
    'loudnorm=I=-16:TP=-1.5:LRA=8,aresample=%d,apad=whole_dur=%s' % (SR, D), '-t', str(D), '-ac', '1', 'voice_clean.wav'], check=True, capture_output=True)
save('music.wav', music()); save('sfx.wav', sfx())

# 2) المزج: الموسيقى تنخفض تلقائياً أثناء الكلام (sidechain)
subprocess.run(['ffmpeg', '-y', '-i', 'voice_clean.wav', '-i', 'music.wav', '-i', 'sfx.wav', '-filter_complex',
    '[0:a]asplit=2[v][vs];[1:a]volume=0.55[m];[m][vs]sidechaincompress=threshold=0.02:ratio=9:attack=15:release=450[md];'
    '[v][md][2:a]amix=inputs=3:normalize=0:duration=first,alimiter=limit=0.95[out]',
    '-map', '[out]', '-t', str(D), 'final_audio.wav'], check=True, capture_output=True)
for f in ['music.wav', 'sfx.wav', 'voice_clean.wav']:
    import os; os.remove(f)
print('ok')
