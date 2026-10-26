# يولّد المؤثرات الصوتية (نقرات، فقاعات، جرس نجاح) ويكتبها في sounds.wav
import numpy as np, wave
SR = 44100
D = 88
buf = np.zeros(int(SR * D) + SR)

def put(at, sig, vol=1.0):
    i = int(at * SR); buf[i:i + len(sig)] += sig[:len(buf) - i] * vol

def env(n, a=.005, k=8):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t * k)

def pop():
    n = int(.14 * SR); t = np.arange(n) / SR
    f = 900 - 5000 * t
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .003, 22)

def tick():
    n = int(.06 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 1400 * t) * env(n, .002, 60)

def ding():
    n = int(1.1 * SR); t = np.arange(n) / SR
    s = sum(np.sin(2 * np.pi * f * t) * a for f, a in [(784, 1), (988, .8), (1319, .7), (1568, .4)])
    return s * env(n, .004, 4.5) / 3

def ta_da():
    for k, (f, d) in enumerate([(523, 0), (659, .12), (784, .24), (1047, .4)]):
        n = int(.9 * SR); t = np.arange(n) / SR
        put(81.0 + d - 0.0 + 0, np.sin(2 * np.pi * f * t) * env(n, .004, 4) * .25)

E = []
E += [(0.5, 'pop'), (1.0, 'pop')]
for base, ts in [(6, 1), (24, 1)]:
    E += [(base + 1.2, 'pop'), (base + 2.0, 'pop'), (base + 3.0, 'pop')]
    E += [(base + 5 + k, 'tick') for k in range(5)]
    E += [(base + 10.5, 'ding'), (base + 11.2, 'pop')]
E += [(44 + x, 'pop') for x in (2.2, 4.2, 5.0, 9, 12, 13, 13.5, 14)]
E += [(62 + x, 'pop') for x in (1.0, 1.6, 5.4, 7.6, 8.2, 12)]
E += [(76 + x, 'pop') for x in (.5, 1.0, 3.4)]
fn = {'pop': pop, 'tick': tick, 'ding': ding}
for at, k in E: put(at, fn[k](), .8 if k != 'tick' else .5)
ta_da_at = 76 + 5.0
for f, d in [(523, 0), (659, .12), (784, .24), (1047, .4)]:
    n = int(.9 * SR); t = np.arange(n) / SR
    put(ta_da_at + d, np.sin(2 * np.pi * f * t) * env(n, .004, 4) * .28)
buf = np.clip(buf, -1, 1)
w = wave.open('sounds.wav', 'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((buf * 32000).astype(np.int16).tobytes()); w.close()
