# موسيقى هادئة + مؤثرات تتبع أحداث الصوت التي سجّلها الكتاب أثناء التصوير (sfx_log.json)
# الاستعمال: python3 audio.py  ← ينتج trailer_audio.wav
import numpy as np, wave, json, os
MODE = os.environ.get('MODE', 'h'); SR = 44100; D = float(os.environ.get('D', 60 if MODE == 'v' else 49)); N = int(SR * D)
def save(path, x):
    w = wave.open(path, 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.clip(x, -1, 1) * 32000).astype(np.int16).tobytes()); w.close()
def note(f, dur, kind):
    n = int(dur * SR); t = np.arange(n) / SR
    if kind == 'pluck':
        return (np.sin(2*np.pi*f*t) + .35*np.sin(2*np.pi*2*f*t)*np.exp(-t*14) + .15*np.sin(2*np.pi*4*f*t)*np.exp(-t*30)) * np.minimum(1, t/.004) * np.exp(-t*7)
    if kind == 'pad':
        return (np.sin(2*np.pi*f*t) + .5*np.sin(2*np.pi*f*1.003*t) + .25*np.sin(2*np.pi*2*f*t)) * np.minimum(1, t/.9) * np.minimum(1, (dur - t)/.9)
    return (np.sin(2*np.pi*f*t) + .3*np.sin(2*np.pi*2*f*t)) * np.minimum(1, t/.01) * np.exp(-t*3.2)
def music():
    m = np.zeros(N + 5*SR); bpm = 108; beat = 60/bpm; bar = 4*beat
    hz = lambda x: 440 * 2 ** ((x - 69) / 12)
    chords = [(48, [60, 64, 67]), (45, [57, 60, 64]), (53, [57, 60, 65]), (43, [55, 59, 62])]
    pent = {0: [72, 76, 79, 76, 84, 79, 76, 79], 1: [69, 72, 76, 72, 81, 76, 72, 76], 2: [72, 77, 81, 77, 84, 81, 77, 81], 3: [71, 74, 79, 74, 83, 79, 74, 79]}
    for b in range(int(D / bar) + 2):
        t0 = b * bar; ci = b % 4; root, tri = chords[ci]
        def put(at, sig, v):
            i = int(at * SR)
            if i < len(m): m[i:i+len(sig)] += sig[:len(m)-i] * v
        for p in tri: put(t0, note(hz(p - 12), bar, 'pad'), .10)
        put(t0, note(hz(root - 12), beat*1.9, 'bass'), .30); put(t0 + 2*beat, note(hz(root - 12), beat*1.9, 'bass'), .24)
        for k, p in enumerate(pent[ci]): put(t0 + k*beat/2, note(hz(p), beat, 'pluck'), .13)
    m = m[:N]; fade = np.ones(N); fade[:int(1.5*SR)] = np.linspace(0, 1, int(1.5*SR)); fade[-int(3*SR):] = np.linspace(1, 0, int(3*SR))
    return m * fade * .55
def sfx(log):
    x = np.zeros(N + 2*SR)
    def put(at, sig, v):
        i = int(at * SR)
        if 0 <= i < N: x[i:i+len(sig)] += sig[:len(x)-i] * v
    for kind, f, ms in log:
        at = ms / 1000
        if kind == 'pop':
            n = int(.14*SR); t = np.arange(n)/SR; put(at, np.sin(2*np.pi*np.cumsum(f*1.6 - 5000*t*(f/600))/SR) * np.minimum(1, t/.003) * np.exp(-t*22), .35)
        elif kind == 'ding':
            n = int(1.2*SR); t = np.arange(n)/SR; put(at, sum(np.sin(2*np.pi*q*t)*a for q, a in [(784, 1), (988, .8), (1319, .7), (1568, .4)]) * np.minimum(1, t/.004) * np.exp(-t*4.5)/3, .6)
        elif kind == 'bad':
            n = int(.25*SR); t = np.arange(n)/SR; put(at, np.sin(2*np.pi*np.cumsum(190 - 240*t)/SR) * np.exp(-t*12), .25)
        elif kind == 'flap':
            n = int(.3*SR); t = np.arange(n)/SR; put(at, np.sin(2*np.pi*np.cumsum(220 + 1900*t)/SR) * np.exp(-t*9), .22)
    return x[:N]
log = json.load(open(f'sfx_log_{MODE}.json'))
save(f'trailer_audio_{MODE}.wav', music() + sfx(log)); print(len(log), 'sfx')
