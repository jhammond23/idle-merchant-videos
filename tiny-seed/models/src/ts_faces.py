# Tiny Seed: troll face decals in the Toybox line-art style (our own drawings, PIL).
# Writes one PNG per expression plus an atlas per character into ../faces/.
import math, os
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'faces')
CW, CH = 1024, 824          # cell size (matches the face patch aspect 4.6 : 3.7)
SS = 2
INK = (30, 20, 14, 255)
WHITE = (255, 255, 255, 255)
TONGUE = (242, 160, 168, 255)
TEAR = (79, 168, 232, 255)
BLUSH = (236, 118, 118, 170)


class C:
    def __init__(s, base, edge):
        """base: light stone tone in the middle of the face; edge: the head rock's own tone it melts into."""
        import random
        s.W, s.H = CW * SS, CH * SS
        s.base = base
        # soft-edged superellipse: alpha feather, and the colour drifts from `base` to `edge` toward the rim
        m = Image.new('L', (s.W, s.H), 0)
        md = ImageDraw.Draw(m)
        rng = random.Random(7)
        ph = [rng.uniform(0, 6.28) for _ in range(3)]
        pts = []
        for i in range(360):
            a = 2 * math.pi * i / 360
            ca, sa = math.cos(a), math.sin(a)
            wob = 1 + 0.025 * math.sin(5 * a + ph[0]) + 0.02 * math.sin(9 * a + ph[1]) + 0.012 * math.sin(14 * a + ph[2])
            x = 0.85 * wob * abs(ca) ** (2 / 2.6) * (1 if ca >= 0 else -1)
            y = 0.70 * wob * abs(sa) ** (2 / 2.6) * (1 if sa >= 0 else -1)
            pts.append(s.p(x, y))
        md.polygon(pts, fill=255)
        alpha = m.filter(ImageFilter.GaussianBlur(24 * SS))
        core = m.filter(ImageFilter.GaussianBlur(70 * SS)).point(lambda v: max(0, min(255, int((v - 96) * 255 / 130))))
        col = Image.composite(Image.new('RGB', (s.W, s.H), base[:3]), Image.new('RGB', (s.W, s.H), edge[:3]), core)
        # faint stone variation: soft blotches, facet-like patches and fine speckle (same on every expression)
        import numpy as np
        nr = np.random.RandomState(7)

        def up(arr, how, blur=0.0):
            im = Image.fromarray((arr * 8 + 128).clip(0, 255).astype('uint8'), 'L').resize((s.W, s.H), how)
            if blur:
                im = im.filter(ImageFilter.GaussianBlur(blur))
            return (np.asarray(im, float) - 128) / 8
        var = up(nr.uniform(-6, 6, (10, 12)), Image.BICUBIC)                       # soft blotches
        var += up(nr.uniform(-4.5, 4.5, (7, 9)), Image.NEAREST, 2 * SS)             # facet-like patches
        sp = np.where(nr.rand(s.H // 6, s.W // 6) < 0.04, -nr.uniform(8, 20, (s.H // 6, s.W // 6)), 0.0)
        sp += np.where(nr.rand(s.H // 6, s.W // 6) < 0.02, nr.uniform(5, 10, (s.H // 6, s.W // 6)), 0.0)
        var += up(sp, Image.BICUBIC, 1.0 * SS)                                      # fine speckle
        col = Image.fromarray((np.asarray(col, float) + var[:, :, None]).clip(0, 255).astype('uint8'), 'RGB')
        s.im = col.convert('RGBA'); s.im.putalpha(alpha)
        s.base_im = s.im.copy()
        s.d = ImageDraw.Draw(s.im, 'RGBA')

    def poly_base(s, pts):
        """repaint a polygon with the untouched stone base (used for eyelids)"""
        m = Image.new('L', (s.W, s.H), 0)
        ImageDraw.Draw(m).polygon([s.p(*a) for a in pts], fill=255)
        s.im.paste(s.base_im, (0, 0), m); s.d = ImageDraw.Draw(s.im, 'RGBA')

    def p(s, x, y):
        return (s.W / 2 + x * s.W / 2, s.H / 2 - y * s.W / 2)   # same scale on both axes (units of half-width)

    def px(s, v):
        return v * s.W / 2

    def line(s, pts, w=0.05, col=INK):
        q = [s.p(*a) for a in pts]
        wp = max(1, int(s.px(w)))
        s.d.line(q, fill=col, width=wp, joint='curve')
        for (x, y) in (q[0], q[-1]):
            s.d.ellipse([x - wp / 2, y - wp / 2, x + wp / 2, y + wp / 2], fill=col)

    def arc(s, cx, cy, rx, ry, a0, a1, w=0.05, col=INK, n=40):
        s.line([(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)], w, col)

    def ell(s, cx, cy, rx, ry, fill=None, rim=0.0, rimcol=INK):
        x, y = s.p(cx, cy)
        a, b = s.px(rx), s.px(ry)
        if rim:
            r = s.px(rim)
            s.d.ellipse([x - a - r, y - b - r, x + a + r, y + b + r], fill=rimcol)
        if fill:
            s.d.ellipse([x - a, y - b, x + a, y + b], fill=fill)

    def poly(s, pts, fill):
        s.d.polygon([s.p(*a) for a in pts], fill=fill)

    def brow(s, x0, y0, x1, y1, w=0.085):
        """tapered thick bar from (x0,y0) (thin end) to (x1,y1) (thick end)"""
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy); nx, ny = -dy / L, dx / L
        a, b = w * 0.32, w * 0.5
        s.poly([(x0 + nx * a, y0 + ny * a), (x1 + nx * b, y1 + ny * b), (x1 - nx * b, y1 - ny * b), (x0 - nx * a, y0 - ny * a)], INK)
        s.ell(x0, y0, a, a, INK); s.ell(x1, y1, b, b, INK)

    def blush(s, x, y, rx=0.16, ry=0.09):
        lay = Image.new('RGBA', (s.W, s.H), (0, 0, 0, 0))
        d = ImageDraw.Draw(lay)
        px, py = s.p(x, y)
        d.ellipse([px - s.px(rx), py - s.px(ry), px + s.px(rx), py + s.px(ry)], fill=BLUSH)
        lay = lay.filter(ImageFilter.GaussianBlur(5 * SS))
        s.im = Image.alpha_composite(s.im, lay); s.d = ImageDraw.Draw(s.im, 'RGBA')

    def tear(s, x, y, r=0.07):
        s.poly([(x, y + r * 2.1), (x - r * 0.95, y + r * 0.2), (x + r * 0.95, y + r * 0.2)], INK)
        s.ell(x, y, r * 1.12, r * 1.12, INK)
        s.poly([(x, y + r * 1.65), (x - r * 0.6, y + r * 0.2), (x + r * 0.6, y + r * 0.2)], TEAR)
        s.ell(x, y, r * 0.78, r * 0.78, TEAR)
        s.ell(x - r * 0.25, y + r * 0.2, r * 0.2, r * 0.2, WHITE)

    def out(s):
        return s.im.resize((CW, CH), Image.LANCZOS)


def round_eye(c, x, y, r=0.22, pr=0.11, px=0.0, py=0.0, glint=True, ry=None):
    ry = ry or r * 1.08
    c.ell(x, y, r, ry, WHITE, rim=0.045)
    c.ell(x + px, y + py, pr, pr * 1.08, INK)
    if glint:
        c.ell(x + px - pr * 0.35, y + py + pr * 0.42, pr * 0.3, pr * 0.3, WHITE)


def baby(expr):
    c = C((221, 215, 203, 255), (190, 184, 174, 255))
    ex, ey = 0.40, 0.10
    if expr == 'GRUMPY':
        for sg in (-1, 1):
            round_eye(c, sg * ex, ey, 0.22, 0.10, px=-sg * 0.03, py=-0.03)
            # heavy lid: cover the top third with base colour, ink lid line slanting down to the middle
            c.poly_base([(sg * (ex - 0.34), ey + 0.33), (sg * (ex + 0.34), ey + 0.33), (sg * (ex + 0.34), ey + 0.13), (sg * (ex - 0.34), ey + 0.02)])
            c.line([(sg * (ex + 0.27), ey + 0.14), (sg * (ex - 0.27), ey + 0.045)], 0.05)
            c.brow(sg * (ex + 0.27), ey + 0.36, sg * (ex - 0.25), ey + 0.19, 0.10)
        c.arc(0, -0.60, 0.21, 0.16, 25, 155, 0.055)                      # pouty frown
        c.line([(-0.24, -0.56), (-0.19, -0.50)], 0.045); c.line([(0.24, -0.56), (0.19, -0.50)], 0.045)
        # one blunt baby tooth poking up
        c.d.rounded_rectangle([*c.p(0.03, -0.32), *c.p(0.16, -0.455)], radius=c.px(0.03), fill=WHITE, outline=INK, width=int(c.px(0.028)))
        c.arc(-0.62, -0.30, 0.09, 0.07, 200, 330, 0.035)                 # puffed cheek marks
        c.arc(0.62, -0.30, 0.09, 0.07, 210, 340, 0.035)
    elif expr == 'GIGGLE':
        for sg in (-1, 1):
            c.arc(sg * ex, ey - 0.03, 0.20, 0.19, 20, 160, 0.062)        # ^ ^ eyes
            c.blush(sg * 0.60, -0.20)
        # open grin: black D, tongue, one blunt tooth
        mx, my, mw, mh = 0.0, -0.26, 0.34, 0.33
        pts = [(mx - mw, my), (mx + mw, my)] + [(mx + mw * math.cos(math.radians(a)), my - mh * math.sin(math.radians(a))) for a in range(0, 181, 6)]
        c.poly(pts, INK)
        c.line([(mx - mw, my), (mx + mw, my)], 0.055)
        c.ell(mx, my - mh * 0.72, mw * 0.52, mh * 0.26, TONGUE)
        c.d.rounded_rectangle([*c.p(-0.07, my - 0.012), *c.p(0.07, my - 0.12)], radius=c.px(0.025), fill=WHITE)
        c.line([(-0.52, 0.42), (-0.60, 0.50)], 0.035); c.line([(0.52, 0.42), (0.60, 0.50)], 0.035)   # giggle ticks
    elif expr == 'SNIFFLE':
        for sg in (-1, 1):
            round_eye(c, sg * ex, ey, 0.245, 0.165, py=-0.02, glint=False)
            c.ell(sg * ex - 0.06, ey + 0.06, 0.055, 0.06, WHITE); c.ell(sg * ex + 0.07, ey - 0.08, 0.03, 0.03, WHITE)
            # water pooling on the lower lid
            c.arc(sg * ex, ey + 0.0, 0.205, 0.225, 215, 325, 0.05, TEAR)
            c.brow(sg * (ex + 0.24), ey + 0.30, sg * (ex - 0.22), ey + 0.46, 0.085)   # worried, inner ends up
        c.tear(-ex - 0.20, ey - 0.33, 0.065)
        c.tear(ex + 0.20, ey - 0.33, 0.065)
        # wobbly mouth
        c.line([(-0.19, -0.52), (-0.10, -0.46), (0.0, -0.52), (0.10, -0.46), (0.19, -0.52)], 0.05)
    elif expr == 'SURPRISED':
        for sg in (-1, 1):
            round_eye(c, sg * ex, ey + 0.02, 0.25, 0.075)
            c.arc(sg * ex, ey + 0.34, 0.21, 0.12, 35, 145, 0.065, n=14)        # raised brows
        c.ell(0, -0.50, 0.105, 0.135, WHITE, rim=0.05)
    return c.out()


def mother(expr):
    c = C((198, 192, 180, 255), (154, 149, 140, 255))
    ex, ey = 0.44, 0.16
    if expr == 'STERN':
        for sg in (-1, 1):
            round_eye(c, sg * ex, ey, 0.19, 0.085, px=-sg * 0.02, py=-0.045)
            c.poly_base([(sg * (ex - 0.30), ey + 0.30), (sg * (ex + 0.30), ey + 0.30), (sg * (ex + 0.30), ey + 0.07), (sg * (ex - 0.30), ey + 0.02)])
            c.line([(sg * (ex + 0.24), ey + 0.075), (sg * (ex - 0.24), ey + 0.03)], 0.05)
            c.brow(sg * (ex + 0.30), ey + 0.27, sg * (ex - 0.27), ey + 0.17, 0.125)
            c.arc(sg * ex, ey - 0.20, 0.17, 0.06, 215, 325, 0.03)        # tired line under the eye
        c.line([(-0.30, -0.50), (0.30, -0.50)], 0.06)
        c.line([(-0.30, -0.50), (-0.36, -0.57)], 0.05); c.line([(0.30, -0.50), (0.36, -0.57)], 0.05)
        c.line([(-0.09, 0.50), (-0.05, 0.36)], 0.03); c.line([(0.09, 0.50), (0.05, 0.36)], 0.03)   # brow furrow
    elif expr == 'SOFT':
        for sg in (-1, 1):
            round_eye(c, sg * ex, ey, 0.19, 0.10, px=-sg * 0.01, py=-0.07)
            c.poly_base([(sg * (ex - 0.30), ey + 0.30), (sg * (ex + 0.30), ey + 0.30), (sg * (ex + 0.30), ey + 0.045), (sg * (ex - 0.30), ey + 0.045)])
            c.arc(sg * ex, ey + 0.045, 0.215, 0.07, 0, 180, 0.05)        # soft upper lid
            c.brow(sg * (ex + 0.27), ey + 0.25, sg * (ex - 0.22), ey + 0.36, 0.085)
            c.blush(sg * 0.62, -0.20, 0.15, 0.08)
            c.arc(sg * ex, ey - 0.20, 0.17, 0.06, 215, 325, 0.03)
        c.arc(0, -0.36, 0.25, 0.15, 205, 335, 0.058)                     # small warm smile
    return c.out()


BABY = ['GRUMPY', 'GIGGLE', 'SNIFFLE', 'SURPRISED']
MOTHER = ['STERN', 'SOFT']


def build():
    os.makedirs(OUT, exist_ok=True)
    res = {}
    for who, fn, names in (('TrollBaby', baby, BABY), ('TrollMother', mother, MOTHER)):
        atlas = Image.new('RGBA', (CW * len(names), CH), (0, 0, 0, 0))
        for i, e in enumerate(names):
            im = fn(e)
            im.save(os.path.join(OUT, f'TS_Face_{who}_{e}.png'))
            atlas.paste(im, (i * CW, 0))
        p = os.path.join(OUT, f'TS_Face_{who}_ATLAS.png')
        atlas.save(p)
        res[who] = p
    return res


if __name__ == '__main__':
    print(build())
