"""finish.py: Claude's standard finishing pass for every "In this town" film (no AI credits).

    python3 -I finish.py IN.mp4 OUT.mp4 [--cues cues.json]

What it adds, on any delivered film (1080x1920, 30 fps):
  picture  a slow push-in with a gentle drift on every shot (alternating sides, never a swing),
           a light punch-in on every 4th cut, more colour and local contrast, light sharpening,
           cool shadows / warm highlights, a soft vignette, slightly soft lens edges, a warm light
           leak from the top right, sunlit dust motes drifting with parallax, and light motion
           smoothing inside shots (never across a cut). The @idlemerchantrng handle stays crisp
           and fixed in the top-left corner.
  sound    a soft wind bed under the whole film, a light whoosh on every 3rd cut, plus any
           story-specific cues from --cues, all ducked under the narrator; loudness -14 LUFS.
  file     sized to stay under 25 MB.
--cues is optional JSON: {"punch": [[t, zoom], ...], "flash": [[t, strength], ...],
                          "sfx": [[t, "boom|whoosh|thud|flap|shimmer|ding|riser", dB], ...]}
Story moments (speed lines, god rays, shadow sweeps) are still done by hand per film.
"""
import sys, os, json, math, subprocess, tempfile, argparse
import numpy as np, cv2, scipy.signal as ss, scipy.io.wavfile as wf

ap = argparse.ArgumentParser(); ap.add_argument('src'); ap.add_argument('dst'); ap.add_argument('--cues')
A = ap.parse_args()
cues = json.load(open(A.cues)) if A.cues else {}
W, H, FPS, R = 1080, 1920, 30, 48000
tmp = tempfile.mkdtemp(prefix='finish_')
rng = np.random.default_rng(11)

def probe(path):
    o = subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries',
                                 'stream=width,height,r_frame_rate:format=duration', '-of', 'json', path])
    d = json.loads(o); s = d['streams'][0]
    return s['width'], s['height'], eval(s['r_frame_rate']), float(d['format']['duration'])
w, h, fps, DUR = probe(A.src)
assert (w, h) == (W, H) and abs(fps - FPS) < 1, f'expected 1080x1920 30fps, got {w}x{h} {fps}'

def frames(path):
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', path, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3: break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)

# ---- cuts ----
o = subprocess.run(['ffmpeg', '-i', A.src, '-vf', "scale=270:-1,select='gt(scene,0.25)',metadata=print", '-an', '-f', 'null', '-'],
                   capture_output=True, text=True).stderr
CUTS = [0.0] + [float(l.split('pts_time:')[1].split()[0]) for l in o.splitlines() if 'pts_time:' in l] + [1e9]
print('cuts', len(CUTS) - 2)
def shot_of(t):
    for k in range(len(CUTS) - 1):
        if CUTS[k] <= t + 1e-3 < CUTS[k + 1]: return k
    return len(CUTS) - 2
def camera(t):
    k = shot_of(t); a, b = CUTS[k], min(CUTS[k + 1], DUR)
    p = min(1, (t - a) / max(0.3, b - a)); e = p * p * (3 - 2 * p) * 0.6 + p * 0.4
    side = 1 if k % 2 == 0 else -1
    return 1.0 + 0.05 * e, side * 16 * e, -8 * e
PUNCH = [(c, 1.04) for i, c in enumerate(CUTS[1:-1]) if i % 4 == 3] + [tuple(x) for x in cues.get('punch', [])]
FLASH = [tuple(x) for x in cues.get('flash', [])]
def punch(t):
    z = 1.0
    for t0, zz in PUNCH:
        if t0 <= t < t0 + 2.0:
            z = max(z, 1 + (zz - 1) * min(1, (t - t0) / 0.07) * math.exp(-max(0, t - t0 - 0.07) / 0.9))
    return z

# ---- static handle mask (top-left) ----
samp = [f[40:130, 20:420].astype(np.float32) for i, f in enumerate(frames(A.src)) if i % 37 == 0]
std = np.stack(samp).std(0).max(-1)
hmask = cv2.GaussianBlur(cv2.dilate((std < 6).astype(np.float32), np.ones((3, 3), np.uint8)), (3, 3), 0)[..., None]
inmask = cv2.dilate((std < 6).astype(np.uint8), np.ones((7, 7), np.uint8))

gy, gx = np.mgrid[0:H, 0:W].astype(np.float32)
vig = np.clip(1 - 0.16 * (((gx - W / 2) / (W / 2)) ** 2 + ((gy - H / 2) / (H / 2)) ** 2) ** 1.4, 0.75, 1)[..., None]
redge = np.clip((np.sqrt(((gx - W / 2) / (W / 2)) ** 2 + ((gy - H / 2) / (H / 2)) ** 2) - 0.75) / 0.45, 0, 1)[..., None]
ly, lx = np.mgrid[0:H // 8, 0:W // 8].astype(np.float32)
leak = cv2.resize(np.exp(-(((lx - W // 8) / (W / 10)) ** 2 + (ly / (H / 9)) ** 2))[..., None] * np.array([[[255, 190, 120]]], np.float32), (W, H))
del gy, gx
ND = 70
dust = dict(x=rng.uniform(0, W, ND), y=rng.uniform(0, H, ND), d=rng.uniform(0.3, 1.0, ND), ph=rng.uniform(0, 6.28, ND))

vbr = int(min(4500, max(1500, (24.0e6 * 8 / DUR - 170e3) / 1000 * 0.93)))
vid = os.path.join(tmp, 'v.mp4')
enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                        '-c:v', 'libx264', '-preset', 'medium', '-b:v', f'{vbr}k', '-maxrate', f'{int(vbr * 1.35)}k', '-bufsize', f'{vbr * 2}k',
                        '-pix_fmt', 'yuv420p', vid], stdin=subprocess.PIPE)
prev, prev_shot = None, -1
for i, f in enumerate(frames(A.src)):
    t = i / FPS
    zc, dx, dy = camera(t); z = zc * punch(t)
    f2 = f.copy(); f2[40:130, 20:420] = cv2.inpaint(np.ascontiguousarray(f[40:130, 20:420]), inmask, 3, cv2.INPAINT_TELEA)
    M = np.float32([[z, 0, (1 - z) * W / 2 + dx], [0, z, (1 - z) * H * 0.55 + dy]])
    x = cv2.warpAffine(f2.astype(np.float32), M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
    L = x.mean(-1, keepdims=True); x = L + (x - L) * 1.08
    x = (x - 128) * 1.04 + 128
    sm = cv2.resize(x, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    x = x + (x - cv2.resize(cv2.GaussianBlur(sm, (0, 0), 6), (W, H))) * 0.22
    x = x + (x - cv2.GaussianBlur(x, (0, 0), 1.2)) * (0.35 + 0.4 * (z - 1) / 0.13)
    lum = np.clip(x.mean(-1, keepdims=True) / 255.0, 0, 1)
    x = x + np.array([5, 2, -6], np.float32) * lum + np.array([-4, 0, 6], np.float32) * (1 - lum)
    x *= vig
    x = x * (1 - redge * 0.8) + cv2.GaussianBlur(x, (0, 0), 3.5) * redge * 0.8
    x += leak * (0.07 + 0.04 * math.sin(t * 1.3))
    ov = np.zeros((H // 2, W // 2, 3), np.float32)
    for j in range(ND):
        d = dust['d'][j]
        px = (dust['x'][j] + 22 * d * t + 30 * math.sin(t * 0.7 + dust['ph'][j]) - dx * d * 1.5) % W
        py = (dust['y'][j] - 14 * d * t + 18 * math.sin(t * 0.5 + dust['ph'][j] * 2)) % H
        al = (0.35 + 0.35 * math.sin(t * 2 + dust['ph'][j])) * d
        cv2.circle(ov, (int(px / 2), int(py / 2)), max(1, int(3.2 * d)), (255 * al, 240 * al, 210 * al), -1, cv2.LINE_AA)
    x += cv2.resize(cv2.GaussianBlur(ov, (0, 0), 1.6), (W, H)) * 0.9
    sh = shot_of(t)
    if prev is not None and sh == prev_shot: x = x * 0.78 + prev * 0.22
    prev, prev_shot = x.copy(), sh
    for t0, s in FLASH:
        if t0 <= t < t0 + 0.4: x += 255 * s * math.exp(-(t - t0) / 0.09)
    x = np.clip(x, 0, 255)
    x[40:130, 20:420] = x[40:130, 20:420] * (1 - hmask) + f[40:130, 20:420].astype(np.float32) * hmask
    enc.stdin.write(x.astype(np.uint8).tobytes())
enc.stdin.close(); enc.wait()

# ---- sound ----
out = np.zeros((int(DUR * R) + R, 2))
def bp(x, lo, hi):
    b, a = ss.butter(2, [lo / (R / 2), hi / (R / 2)], 'band'); return ss.lfilter(b, a, x)
def lp(x, f):
    b, a = ss.butter(2, f / (R / 2)); return ss.lfilter(b, a, x)
def env(n, a, d):
    t = np.arange(n) / R; return np.minimum(1, t / max(a, 1e-4)) * np.exp(-np.maximum(0, t - a) / d)
def nz(y): return y / (np.abs(y).max() + 1e-9)
def whoosh(dur=0.5, f0=300, f1=3000):
    n = int(dur * R); f, tt, Z = ss.stft(rng.standard_normal(n), R, nperseg=1024)
    fc = f0 * (f1 / f0) ** np.clip(tt / dur, 0, 1)
    y = ss.istft(Z * np.exp(-0.5 * (np.log((f[:, None] + 1) / fc[None, :]) / 0.45) ** 2), R, nperseg=1024)[1][:n]
    y = np.pad(y, (0, max(0, n - len(y)))); return nz(lp(y, 9000) * np.sin(np.linspace(0, np.pi, n)) ** 1.5)
def boom(dur=1.8, f=45):
    n = int(dur * R); t = np.arange(n) / R
    y = np.sin(2 * np.pi * np.cumsum(f * (1 + 1.5 * np.exp(-t * 18))) / R) * env(n, 0.005, 0.6)
    return nz(y + lp(rng.standard_normal(n), 400) * env(n, 0.002, 0.12) * 0.5)
def thud(dur=0.45, f=70):
    n = int(dur * R); t = np.arange(n) / R
    return nz(np.sin(2 * np.pi * f * (1 + 0.8 * np.exp(-t * 30)) * t) * env(n, 0.002, 0.09) + lp(rng.standard_normal(n), 900) * env(n, 0.001, 0.03) * 0.6)
def flap():
    tot = np.zeros(int(0.7 * R))
    for k in range(2):
        m = int(0.22 * R); y = bp(rng.standard_normal(m), 150, 1800) * env(m, 0.03, 0.06); s = int(k * 0.2 * R); tot[s:s + m] += y
    return nz(tot)
def shimmer(dur=1.5):
    n = int(dur * R); y = np.zeros(n)
    for _ in range(16):
        f = 1800 * rng.choice([1, 1.26, 1.5, 2, 2.52]); m = int(0.5 * R); s = int(rng.uniform(0, dur * 0.7) * R)
        tone = np.sin(2 * np.pi * f * np.arange(m) / R) * env(m, 0.003, 0.15); e = min(n, s + m); y[s:e] += tone[:e - s]
    return nz(y)
def ding():
    n = int(1.0 * R); t = np.arange(n) / R
    return nz(sum(np.sin(2 * np.pi * 1568 * hh * t) * a for hh, a in [(1, 1), (2.76, .4), (5.4, .2)]) * env(n, 0.002, 0.35))
def riser(dur=3.0):
    n = int(dur * R); t = np.arange(n) / R; fr = 200 * 8 ** (t / dur)
    return nz((np.sin(2 * np.pi * np.cumsum(fr) / R) * 0.5 + whoosh(dur, 6000, 200) * 0.5) * (t / dur) ** 2.2)
SFX = dict(boom=boom, whoosh=whoosh, thud=thud, flap=flap, shimmer=shimmer, ding=ding, riser=riser)
def place(t, sig, db, pan=0.0):
    g = 10 ** (db / 20); s = int(t * R); e = min(len(out), s + len(sig))
    l, r = math.cos((pan + 1) * math.pi / 4), math.sin((pan + 1) * math.pi / 4)
    out[s:e, 0] += sig[:e - s] * g * l * 1.414; out[s:e, 1] += sig[:e - s] * g * r * 1.414
n = int(DUR * R)
for lo, hi, db, pan in ((150, 700, -37, -0.3), (300, 1200, -39, 0.3)):
    y = bp(rng.standard_normal(n), lo, hi) * (0.6 + 0.4 * np.sin(np.linspace(0, DUR * 0.9, n) + 1.3) * np.sin(np.linspace(0, DUR * 0.37, n)))
    place(0, nz(y), db, pan)
for i, c in enumerate(CUTS[1:-1]):
    if i % 3 == 0: place(max(0, c - 0.12), whoosh(0.35, 2000, 400), -29)
for t0, kind, db in cues.get('sfx', []): place(t0, SFX[kind](), db)
out = np.tanh(out[:n] * 1.1) / 1.1
sfxw = os.path.join(tmp, 'sfx.wav'); wf.write(sfxw, R, (out * 32767).astype(np.int16))
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', vid, '-i', A.src, '-i', sfxw, '-filter_complex',
                '[1:a]aresample=48000,asplit=2[v1][v2];[2:a]volume=1.6[s];[s][v1]sidechaincompress=threshold=0.05:ratio=4:attack=15:release=250[sd];'
                '[v2][sd]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=7[a]',
                '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '160k', '-shortest', A.dst], check=True)
size = os.path.getsize(A.dst)
print('done', A.dst, f'{size / 1e6:.1f} MB', 'OK' if size < 25e6 else 'OVER 25 MB')
