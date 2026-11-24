"""Make new face expressions (shocked, scared, angry, and talk/blink variants) from the hero face set by
recombining and redrawing parts. Output: /tmp/claude-0/tv/faces_new/png/<name>.png (1254x1254 RGBA, same layout).
usage: python3 mkfaces.py [base ...]   (default bases: calm bright fierce)"""
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
D = '/mnt/user-data/uploads/roblox/buildDefend/assets/last-caravan-hero-faces/20261031-r001/catalog/png/'
OUT = '/tmp/claude-0/tv/faces_new/png/'; os.makedirs(OUT, exist_ok=True)
BROW = (375, 452); EYE = (452, 610); MOUTH = (860, 1000)
def load(n): return Image.open(D + n + '.png').convert('RGBA')
def region(im, y0, y1, x0=0, x1=1254):
    out = Image.new('RGBA', im.size, (0, 0, 0, 0)); out.paste(im.crop((x0, y0, x1, y1)), (x0, y0)); return out
def blank(im, y0, y1, x0=0, x1=1254):
    a = np.array(im); a[y0:y1, x0:x1] = 0; return Image.fromarray(a)
def xform(layer, cx, cy, ang=0.0, dx=0, dy=0, sx=1.0, sy=1.0):
    """rotate (deg, ccw) and scale a layer about (cx, cy), then shift"""
    w, h = layer.size
    a = math.radians(ang); ca, sa = math.cos(a), math.sin(a)
    # inverse map: output (x,y) -> input
    # forward: p' = R*S*(p-c) + c + d   =>   p = S^-1 R^-1 (p'-c-d) + c
    m00, m01 = ca / sx, -sa / sx; m10, m11 = sa / sy, ca / sy
    ox, oy = cx + dx, cy + dy
    # PIL affine uses rows: x_in = a*x + b*y + c ; y_in = d*x + e*y + f   (y down; flip angle sign for ccw on screen)
    A = (ca / sx, sa / sx, 0, -sa / sy, ca / sy, 0)
    c0 = cx - (A[0] * ox + A[1] * oy); c1 = cy - (A[3] * ox + A[4] * oy)
    return layer.transform((w, h), Image.AFFINE, (A[0], A[1], c0, A[3], A[4], c1), resample=Image.BICUBIC)
def brows(im, mode):
    L = region(im, *BROW, 0, 627); R = region(im, *BROW, 627, 1254)
    if mode == 'shocked': L = xform(L, 380, 415, 4, 0, -42); R = xform(R, 880, 415, -4, 0, -42)
    if mode == 'scared': L = xform(L, 380, 415, -13, 0, -26); R = xform(R, 880, 415, 13, 0, -26)
    if mode == 'angry': L = xform(L, 380, 415, 16, 8, 22); R = xform(R, 880, 415, -16, -8, 22)
    return L, R
def iris_fit(im, x0, x1):
    """find the iris circle in one eye: best dark ring along the lower half"""
    a = np.array(im).astype(float); lum = a[:, :, :3].mean(2); dark = (a[:, :, 3] > 100) & (lum < 90)
    best = None
    for cy in range(500, 560, 3):
        for cx in range(x0 + 120, x1 - 120, 3):
            for r in range(52, 84, 3):
                th = np.linspace(0.15 * math.pi, 0.85 * math.pi, 40)
                xs = (cx + r * np.cos(th)).astype(int); ys = (cy + r * np.sin(th)).astype(int)
                ok = (ys < 1254) & (xs < 1254)
                s = dark[ys[ok], xs[ok]].mean()
                if best is None or s > best[0]: best = (s, cx, cy, r)
    return best[1:]
IRIS = {}
def eyes(im, base, mode):
    lay = region(im, *EYE)
    if mode in ('shocked', 'scared'):
        key = base
        if key not in IRIS: IRIS[key] = [iris_fit(im, 190, 570), iris_fit(im, 700, 1080)]
        d = ImageDraw.Draw(lay)
        src = np.array(im).astype(float); lum = src[:, :, :3].mean(2); white = (src[:, :, 3] > 100) & (lum > 200)
        for (cx, cy, r) in IRIS[key]:
            # the eye opening: per column, the white sclera's top and bottom, interpolated across the iris
            xs = np.arange(int(cx - 2.6 * r), int(cx + 2.6 * r)); top = {}; bot = {}
            for x in xs:
                ys = np.nonzero(white[EYE[0]:EYE[1], x])[0]
                if len(ys) > 6: top[x] = EYE[0] + ys.min(); bot[x] = EYE[0] + ys.max()
            kx = np.array(sorted(top)); 
            if len(kx) < 10: continue
            far = kx[np.abs(kx - cx) > r * 1.08]
            tf = np.polyfit(far, [top[x] for x in far], 2); bf = np.polyfit(far, [bot[x] for x in far], 2)
            arr = np.array(lay); H, W = arr.shape[:2]
            yy, xx = np.mgrid[0:H, 0:W]
            disc = (xx - cx) ** 2 + (yy - cy) ** 2 <= (r + 5) ** 2
            opening = (yy >= np.polyval(tf, xx) + 3) & (yy <= np.polyval(bf, xx) - 3)
            paint = disc & opening
            arr[paint] = (250, 250, 250, 255)
            lay = Image.fromarray(arr); d = ImageDraw.Draw(lay)
            k = 0.42 if mode == 'shocked' else 0.36
            rr = r * k; icx = cx; icy = (np.polyval(tf, cx) + np.polyval(bf, cx)) / 2 + 2
            d.ellipse((icx - rr, icy - rr, icx + rr, icy + rr), fill=(30, 30, 34, 255))
            d.ellipse((icx - rr * 0.55, icy - rr * 0.55, icx + rr * 0.55, icy + rr * 0.55), fill=(8, 8, 10, 255))
            d.ellipse((icx + rr * 0.15, icy - rr * 0.75, icx + rr * 0.15 + rr * 0.5, icy - rr * 0.75 + rr * 0.5), fill=(255, 255, 255, 255))
    return lay
def mouth(base_im, mode, talk=None):
    if mode == 'shocked':
        rnd = load('face_calm_talk_round'); m = region(rnd, 860, 1000, 520, 740)
        return xform(m, 627, 928, 0, 0, 40, 1.9, 2.1 if talk != 'round' else 1.8)
    if mode == 'scared':
        rnd = load('face_calm_talk_round'); m = region(rnd, 860, 1000, 520, 740)
        return xform(m, 627, 928, 0, 0, 10, 1.35, 1.15 if talk is None else 1.6)
    if mode == 'angry':
        if talk:
            rnd = load('face_calm_talk_round'); m = region(rnd, 860, 1000, 520, 740)
            return xform(m, 627, 928, 0, 0, 30, 2.3 if talk == 'open' else 1.7, 1.35 if talk == 'open' else 1.2)
        m = region(base_im, 860, 1000)
        return xform(m.transpose(Image.FLIP_TOP_BOTTOM), 627, 1254 - 930, 0, 0, 930 - (1254 - 930) + 6, 0.85, 0.75)
def sweat(lay):
    d = ImageDraw.Draw(lay)
    for (x, y, s) in ((1050, 330, 1.0), (1095, 420, 0.75)):
        pts = [(x, y - 40 * s), (x - 18 * s, y + 6 * s), (x, y + 24 * s), (x + 18 * s, y + 6 * s)]
        d.polygon(pts, fill=(205, 232, 255, 235), outline=(30, 40, 60, 255))
        d.ellipse((x - 18 * s, y - 8 * s, x + 18 * s, y + 26 * s), fill=(205, 232, 255, 235), outline=(30, 40, 60, 255), width=3)
        d.ellipse((x - 8 * s, y + 2 * s, x - 2 * s, y + 10 * s), fill=(255, 255, 255, 255))
    return lay
def build(base, mode, talk=None, blink=False):
    im = load('face_' + base + ('_blink' if blink else ''))
    out = Image.new('RGBA', im.size, (0, 0, 0, 0))
    nose = region(im, 680, 860)
    L, R = brows(im, mode)
    EYEBASE = {'bright': 'calm', 'grin': 'calm', 'cheeky': 'calm', 'cool': 'calm', 'shy': 'calm', 'starry': 'calm', 'wink': 'calm'}
    eb = EYEBASE.get(base, base)
    ey = region(im, *EYE) if blink else eyes(load('face_' + eb), eb, mode)
    if mode == 'angry' and not blink:
        f = load('face_fierce'); ey = region(f, *EYE)
    mo = mouth(load('face_' + base), mode, talk)
    for lay in (ey, nose, mo, L, R): out.alpha_composite(lay)
    if mode == 'scared': out = sweat(out)
    return out
bases = sys.argv[1:] or ['calm', 'bright', 'fierce']
for b in bases:
    for mode in ('shocked', 'scared', 'angry'):
        nm = 'face_%s_%s' % (b, mode)
        build(b, mode).save(OUT + nm + '.png')
        build(b, mode, talk='open').save(OUT + nm + '_talk_open.png')
        build(b, mode, talk='round').save(OUT + nm + '_talk_round.png')
        try: build(b, mode, blink=True).save(OUT + nm + '_blink.png')
        except FileNotFoundError: pass
        print('made', nm, flush=True)
