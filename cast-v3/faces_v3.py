# Cast v3 face decals (Claude, 11-27). Our own drawings, made with the faces.py tooling (PIL, tapered ink lines),
# plus composites of the existing packs (storybook, classic-block, toybox, the Hero kid's town-anime set).
# 1024x1024 RGBA (hero-derived sets keep the 1254 canvas), features centred like faces.py: eye line ~42%, mouth ~68%.
# Usage: python3 -I faces_v3.py            -> /tmp/claude-0/cast3/faces/<set>/<expr>.png + contact sheets
import math, os, sys, colorsys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.argv = [sys.argv[0], '/tmp/claude-0/cast3/faces/_toybox']     # faces.py reads its OUT dir from argv[1]
sys.path.insert(0, '/tmp/claude-0/kits')
import faces as F                                                   # taper_line, arc_pts, ell, canvas, S, toybox()

ROOT = '/tmp/claude-0/cast3/faces'
PACKS = '/tmp/claude-0/cast3/dl/faces'
HERO = '/mnt/user-data/uploads/roblox/buildDefend/assets/last-caravan-hero-faces/20261031-r001/catalog/png/'
N, SS, S = F.N, F.SS, F.S
taper_line, arc_pts, ell = F.taper_line, F.arc_pts, F.ell

def out(setname, expr, im):
    d = os.path.join(ROOT, setname); os.makedirs(d, exist_ok=True)
    if im.size[0] != N and im.size[0] == N * SS: im = im.resize((N, N), Image.LANCZOS)
    im.save(os.path.join(d, expr + '.png'))

def layer():
    return F.canvas()

# ------------------------------------------------------------------ SHARP RIVAL SET (new)
# narrow almond eyes with a heavy tapered upper lid that flicks up at the outer corner, small iris, angled brush brows,
# thin sharp mouths. Two variants share the family: 'noble' (First Rank, steel-blue iris) and 'shifty' (Rigger, olive iris).
RINK = (20, 16, 22, 255); WHITE = (255, 255, 255, 255); MOUTH = (110, 26, 34, 255); TONGUE = (196, 72, 80, 255); TEETH = (250, 248, 240, 255)

def qbez(p0, p1, p2, k=24):
    return [((1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t * t * p2[0], (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t * t * p2[1]) for t in [i / k for i in range(k + 1)]]

def sharp_eye(im, cx, cy, s, iris, open_=1.0, look=(0, 0), w=150, shifty=False, lid_drop=0.0, pupil=1.0, squeeze=False, tear=False):
    """one sharp eye. s=-1 left of image, +1 right. open_ scales the eye height; lid_drop (0..1) lowers the upper lid (half-lid)."""
    d = ImageDraw.Draw(im)
    h = 62 * open_
    inner = (cx - s * w * 0.48, cy + 8); outer = (cx + s * w * 0.56, cy - 12 - (8 if shifty else 0))
    top_ctrl = (cx + s * 10, cy - h * 1.9 + lid_drop * h * 1.5)
    bot_ctrl = (cx + s * 6, cy + h * (0.95 if not shifty else 0.75))
    up = qbez(inner, top_ctrl, outer); lo = qbez(inner, bot_ctrl, outer)
    if squeeze:   # eyes squeezed shut (humiliated): two angled strokes
        taper_line(d, [inner, (cx + s * 8, cy - 10), outer], 30, 10, RINK)
        taper_line(d, [(cx - s * w * 0.4, cy + 26), (cx + s * w * 0.45, cy + 18)], 18, 6, RINK)
        return
    poly = up + lo[::-1]
    mask = Image.new('L', im.size, 0); ImageDraw.Draw(mask).polygon([(S(x), S(y)) for x, y in poly], fill=255)
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    ld.polygon([(S(x), S(y)) for x, y in poly], fill=WHITE)
    ir = 44 * (0.9 if shifty else 1.0); ix, iy = cx + look[0], cy - 6 + look[1]
    ell(ld, ix, iy, ir, ir * 1.05, fill=iris)
    ell(ld, ix, iy + 4, ir * 0.62, ir * 0.62, fill=tuple(int(c * 0.55) for c in iris[:3]) + (255,))
    ell(ld, ix, iy + 2, ir * 0.42 * pupil, ir * 0.46 * pupil, fill=RINK)
    ell(ld, ix + 14, iy - 16, 10, 10, fill=WHITE)
    im.alpha_composite(Image.composite(lay, Image.new('RGBA', im.size, (0, 0, 0, 0)), mask))
    # heavy upper lid with an outer flick
    flick = (outer[0] + s * 34, outer[1] - 20)
    taper_line(d, up[2:] + [flick], 38, 10, RINK)
    taper_line(d, up[:5], 18, 8, RINK)
    # lower lid: outer 60 % only
    taper_line(d, lo[10:], 14, 6, RINK)
    if tear:
        d.polygon([(S(cx + s * 20), S(cy + 44)), (S(cx + s * 6), S(cy + 120)), (S(cx + s * 34), S(cy + 120))], fill=(120, 190, 245, 255))
        ell(d, cx + s * 20, cy + 122, 15, 15, fill=(120, 190, 245, 255))

def sharp_brow(im, cx, cy, s, angle, lift=0, w=160, thick=42):
    """brush brow: thick at the inner end, pointed at the outer end. angle>0 = inner end down (anger)."""
    d = ImageDraw.Draw(im)
    a = math.radians(angle)
    y0 = cy - 118 - lift
    inner = (cx - s * w * 0.5, y0 + math.sin(a) * w * 0.45); outer = (cx + s * w * 0.62, y0 - math.sin(a) * w * 0.45 - 10)
    mid = ((inner[0] + outer[0]) / 2, (inner[1] + outer[1]) / 2 - 12)
    top = qbez(inner, mid, outer, 16)
    bot = [(x, y + thick * (1 - i / 16) ** 1.2) for i, (x, y) in enumerate(top)]
    d.polygon([(S(x), S(y)) for x, y in top + bot[::-1]], fill=RINK)

def scale_about(im, k, cx, cy):
    cx, cy = S(cx), S(cy)
    return im.transform(im.size, Image.AFFINE, (1 / k, 0, cx - cx / k, 0, 1 / k, cy - cy / k), resample=Image.BICUBIC)

def sharp_face(expr, iris, shifty=False, freck=False):
    im = sharp_face_raw(expr, iris, shifty, freck)
    return im

def im_draw(im): return ImageDraw.Draw(im)

def freckles(im, ex=512, ey=455, sp=175, col=(178, 104, 74, 230)):
    """Jester's freckles: a loose cluster of soft dots under each eye (drawn before the eye-layer scale)"""
    d = ImageDraw.Draw(im); rnd = __import__('random').Random(11)
    for s in (-1, 1):
        for i in range(7):
            x = ex + s * (sp * 0.55 + rnd.uniform(-60, 70)); y = ey + 92 + rnd.uniform(-14, 34)
            ell(d, x, y, 9 + rnd.uniform(0, 4), 8 + rnd.uniform(0, 3), fill=col)

def sharp_face_raw(expr, iris, shifty=False, freck=False):
    im, de = layer(); mo, d = layer(); ex, ey, sp, my = 512, 455, 175, 715
    if freck: freckles(im, ex, ey, sp)          # on every decal incl. blink / talk, so the swap regions stay continuous
    E = dict(open_=1.0, look=(0, 0), lid=0.0, pupil=1.0)
    br = (12, 12); lift = (0, 0)
    def eyes(**k):
        for s in (-1, 1):
            kk = dict(open_=E['open_'], look=E['look'], lid_drop=E['lid'], pupil=E['pupil']); kk.update(k)
            sharp_eye(im, ex + s * sp, ey, s, iris, shifty=shifty, **kk)
    def brows(al, ar, ll=0, lr=0):
        sharp_brow(im, ex - sp, ey, -1, al, ll); sharp_brow(im, ex + sp, ey, 1, ar, lr)
    if expr == 'neutral':
        eyes(lid_drop=0.15); brows(8, 8)
        taper_line(d, [(462, my), (512, my + 3), (566, my - 2)], 14, 6, RINK)
    elif expr == 'blink':
        for s in (-1, 1): taper_line(de, qbez((ex + s * sp - s * 72, ey + 6), (ex + s * sp, ey + 30), (ex + s * sp + s * 84, ey - 14)), 26, 10, RINK)
        brows(8, 8)
        taper_line(d, [(462, my), (512, my + 3), (566, my - 2)], 14, 6, RINK)
    elif expr == 'smug':
        eyes(lid_drop=0.45, look=(10, 4)); brows(14, -6, 0, 18)
        taper_line(d, [(440, my + 14), (500, my + 20), (560, my + 6), (606, my - 30)], 18, 6, RINK)
        taper_line(d, [(598, my - 40), (616, my - 18)], 10, 4, RINK)
    elif expr == 'sneer':
        eyes(lid_drop=0.35, look=(-6, 0)); brows(22, 2, 0, 10)
        pts = [(430, my + 18), (480, my + 8), (560, my - 22), (612, my - 44), (600, my + 4), (520, my + 22)]
        d.polygon([(S(x), S(y)) for x, y in pts], fill=MOUTH)
        d.polygon([(S(x), S(y)) for x, y in [(486, my + 6), (560, my - 20), (600, my - 36), (598, my - 14), (556, my - 2), (490, my + 14)]], fill=TEETH)
        taper_line(d, [(424, my + 20), (480, my + 8), (560, my - 24), (618, my - 48)], 16, 6, RINK)
        taper_line(d, [(470, my + 18), (530, my + 24), (600, my + 6)], 10, 4, RINK)
    elif expr == 'shocked':
        eyes(open_=1.35, pupil=0.55); brows(-14, -14, 26, 26)
        d.rounded_rectangle([S(462), S(my - 26), S(562), S(my + 70)], radius=S(34), fill=MOUTH, outline=RINK, width=S(12))
        d.rectangle([S(476), S(my - 18), S(548), S(my - 4)], fill=TEETH)
    elif expr == 'furious':
        eyes(open_=0.85, pupil=0.7); brows(34, 34, -6, -6)
        d.polygon([(S(x), S(y)) for x, y in [(396, my - 20), (628, my - 20), (604, my + 70), (420, my + 70)]], fill=MOUTH, outline=RINK, width=S(12))
        d.rectangle([S(410), S(my - 12), S(614), S(my + 14)], fill=TEETH); d.rectangle([S(424), S(my + 44), S(600), S(my + 62)], fill=TEETH)
        for x in (452, 494, 536, 578): d.line([S(x), S(my - 12), S(x), S(my + 14)], fill=RINK, width=S(6))
        taper_line(d, [(396, my - 22), (512, my - 26), (628, my - 22)], 16, 8, RINK)
    elif expr == 'humiliated':
        for s in (-1, 1): sharp_eye(im, ex + s * sp, ey, s, iris, squeeze=True)
        brows(-24, -24, 18, 18)
        pts = [(430 + 21 * i, my + (12 if i % 2 else -10)) for i in range(9)]; taper_line(d, pts, 14, 8, RINK)
        de.polygon([(S(760), S(300)), (S(735), S(380)), (S(785), S(380))], fill=(120, 190, 245, 255)); ell(de, 760, 388, 26, 26, fill=(120, 190, 245, 255))
        for k in range(3): taper_line(de, [(ex - sp - 60 + 40 * k, ey + 86), (ex - sp - 40 + 40 * k, ey + 106)], 10, 5, (200, 60, 70, 255))
    elif expr == 'respect':
        eyes(lid_drop=0.2, look=(-14, 2)); brows(-4, 14, 10, 0)
        taper_line(d, [(470, my + 8), (520, my + 10), (566, my - 6)], 14, 6, RINK)
    elif expr == 'innocence':
        eyes(open_=1.3, look=(4, -16), pupil=1.15); brows(-18, -18, 30, 30)
        taper_line(d, arc_pts(512, my - 18, 34, 20, 20, 160), 14, 6, RINK)
    elif expr == 'gloat':
        eyes(lid_drop=0.55, look=(0, 6)); brows(18, 18, -4, -4)
        d.chord([S(400), S(my - 80), S(624), S(my + 70)], 0, 180, fill=MOUTH, outline=RINK, width=S(12))
        d.chord([S(412), S(my - 66), S(612), S(my + 28)], 0, 180, fill=TEETH)
        taper_line(d, [(388, my - 22), (404, my - 2)], 10, 4, RINK); taper_line(d, [(636, my - 22), (620, my - 2)], 10, 4, RINK)
    elif expr == 'panic':
        eyes(open_=1.4, pupil=0.4, look=(0, 4)); brows(-26, -26, 28, 28)
        pts = [(424 + 22 * i, my + 20 + (16 if i % 2 else -16)) for i in range(9)]
        d.polygon([(S(x), S(y - 26)) for x, y in pts] + [(S(x), S(y + 26)) for x, y in pts[::-1]], fill=MOUTH)
        taper_line(d, [(x, y - 26) for x, y in pts], 12, 6, RINK); taper_line(d, [(x, y + 26) for x, y in pts], 12, 6, RINK)
        for p in ((800, 300), (230, 340)):
            de.polygon([(S(p[0]), S(p[1])), (S(p[0] - 24), S(p[1] + 76)), (S(p[0] + 24), S(p[1] + 76))], fill=(120, 190, 245, 255)); ell(de, p[0], p[1] + 84, 25, 25, fill=(120, 190, 245, 255))
    elif expr == 'caught':
        eyes(open_=1.25, pupil=0.6, look=(36, 0)); brows(-10, -20, 20, 32)
        d.rectangle([S(420), S(my - 24), S(604), S(my + 24)], fill=TEETH, outline=RINK, width=S(12))
        d.line([S(424), S(my), S(600), S(my)], fill=RINK, width=S(6))
        for x in (466, 512, 558): d.line([S(x), S(my - 22), S(x), S(my + 22)], fill=RINK, width=S(6))
        de.polygon([(S(812), S(292)), (S(790), S(360)), (S(834), S(360))], fill=(120, 190, 245, 255)); ell(de, 812, 368, 23, 23, fill=(120, 190, 245, 255))
    elif expr == 'sulk':
        eyes(lid_drop=0.5, look=(-10, 14)); brows(26, 26, -8, -8)
        taper_line(d, arc_pts(512, my + 40, 52, 30, 200, 340), 16, 6, RINK)
    # ---- phase 2 (Jester): sly grin, cackle, wink, serious
    elif expr == 'sly_grin':
        eyes(lid_drop=0.42, look=(18, 4)); brows(16, -10, 0, 26)
        pts = [(410, my - 8), (470, my + 22), (540, my + 26), (600, my + 4), (640, my - 40)]
        d.polygon([(S(x), S(y)) for x, y in pts + [(600, my - 10), (540, my + 2), (470, my)]], fill=MOUTH)
        d.polygon([(S(x), S(y)) for x, y in [(462, my + 2), (540, my + 6), (598, my - 8), (596, my + 2), (540, my + 16), (468, my + 12)]], fill=TEETH)
        taper_line(d, pts, 16, 6, RINK); taper_line(d, [(634, my - 52), (652, my - 26)], 10, 4, RINK)
    elif expr == 'cackle':
        for s in (-1, 1): taper_line(im_draw(im), qbez((ex + s * sp - 76, ey + 14), (ex + s * sp, ey - 52), (ex + s * sp + 80, ey + 10)), 30, 10, RINK)
        brows(-10, -10, 34, 34)
        d.chord([S(404), S(my - 70), S(620), S(my + 96)], 0, 180, fill=MOUTH, outline=RINK, width=S(12))
        d.chord([S(416), S(my - 58), S(608), S(my + 6)], 0, 180, fill=TEETH); ell(d, 512, my + 58, 52, 20, fill=TONGUE)
    elif expr == 'wink':
        sharp_eye(im, ex - sp, ey, -1, iris, lid_drop=0.2, look=(10, 0))
        taper_line(im_draw(im), qbez((ex + sp - 76, ey + 4), (ex + sp, ey + 34), (ex + sp + 84, ey - 16)), 30, 10, RINK)
        brows(6, -14, 0, 20)
        taper_line(d, [(440, my + 14), (500, my + 22), (566, my + 8), (612, my - 26)], 16, 6, RINK)
    elif expr == 'serious':
        eyes(lid_drop=0.08); brows(4, 4, 4, 4)
        taper_line(d, [(456, my + 4), (512, my + 4), (568, my + 4)], 14, 8, RINK)
    elif expr in ('talk_closed', 'talk_half', 'talk_open'):   # mouth-only decals for dialogue
        if expr == 'talk_closed': taper_line(d, [(462, my), (512, my + 4), (566, my - 2)], 16, 6, RINK)
        elif expr == 'talk_half':
            d.chord([S(456), S(my - 30), S(568), S(my + 44)], 0, 180, fill=MOUTH, outline=RINK, width=S(10))
            taper_line(d, [(452, my - 2), (512, my + 2), (572, my - 4)], 14, 6, RINK)
        else:
            d.rounded_rectangle([S(450), S(my - 22), S(574), S(my + 76)], radius=S(40), fill=MOUTH, outline=RINK, width=S(12))
            ell(d, 512, my + 52, 40, 16, fill=TONGUE); d.rectangle([S(468), S(my - 14), S(556), S(my - 2)], fill=TEETH)
    out_ = scale_about(im, 1.22, 512, 470)
    out_.alpha_composite(scale_about(mo, 1.6, 512, my - 40))
    return out_

# ------------------------------------------------------------------ OATHBOUND visor slit (no face)
def visor(state):
    """dark recessed slit with an ice-blue glow line. Colour = glow colour, alpha = coverage. The shader treats the bright
    part as emission (dark frame stays dark)."""
    im = Image.new('RGBA', (N * SS, N * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    y = 440; x0, x1 = 150, 874
    def slit_poly(h, vdip):
        top = [(x, y - h / 2 + vdip * (1 - abs((x - 512) / 362)) ) for x in range(x0, x1 + 1, 16)]
        bot = [(x, y + h / 2 + vdip * 0.4 * (1 - abs((x - 512) / 362))) for x in range(x1, x0 - 1, -16)]
        return [(S(a), S(b)) for a, b in top + bot]
    d.polygon(slit_poly(210, 22), fill=(6, 7, 10, 255))        # recess frame
    core = Image.new('RGBA', im.size, (0, 0, 0, 0)); cd = ImageDraw.Draw(core)
    ICE = (150, 225, 255, 255); WHITEHOT = (225, 248, 255, 255)
    if state == 'dim':
        cd.polygon(slit_poly(70, 22), fill=(80, 150, 200, 255))
    elif state == 'bright':
        cd.polygon(slit_poly(112, 22), fill=ICE); cd.polygon(slit_poly(44, 22), fill=WHITEHOT)
    elif state == 'narrowed':
        cd.polygon(slit_poly(40, 48), fill=ICE)
    elif state == 'flicker':
        for i, (a, b) in enumerate([(160, 300), (330, 470), (500, 560), (590, 720), (750, 870)]):
            seg = Image.new('L', im.size, 0); ImageDraw.Draw(seg).rectangle([S(a), 0, S(b), S(N)], fill=255)
            tmp = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(tmp).polygon(slit_poly(76 + 24 * (i % 2), 22), fill=ICE if i % 2 == 0 else (90, 170, 220, 255))
            core = Image.composite(tmp, core, seg)
    glow = core.filter(ImageFilter.GaussianBlur(S(16)))
    im.alpha_composite(glow); im.alpha_composite(core)
    return im

# ------------------------------------------------------------------ JAILER hood glow (no exposed face)
def hood_eyes(state):
    im = Image.new('RGBA', (N * SS, N * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    AMB = (255, 176, 40, 255); EMBER = (255, 120, 20, 255)
    ex, ey, sp = 512, 470, 150
    core = Image.new('RGBA', im.size, (0, 0, 0, 0)); cd = ImageDraw.Draw(core)
    for s in (-1, 1):
        cx = ex + s * sp
        if state == 'glare':
            ell(cd, cx, ey, 46, 30, fill=AMB); taper_line(cd, [(cx - 66, ey - 66), (cx + 66, ey - 66)], 16, 6, EMBER)
        elif state == 'angry':
            cd.polygon([(S(cx - s * 52), S(ey - 4)), (S(cx + s * 50), S(ey - 34)), (S(cx + s * 46), S(ey + 26)), (S(cx - s * 40), S(ey + 28))], fill=AMB)
            taper_line(cd, [(cx - s * 70, ey - 40), (cx + s * 66, ey - 92)], 18, 6, EMBER)
        elif state == 'surprised':
            ell(cd, cx, ey, 40, 46, fill=AMB); taper_line(cd, arc_pts(cx, ey - 72, 64, 30, 200, 340), 16, 6, EMBER)
        elif state == 'squint':
            cd.rounded_rectangle([S(cx - 50), S(ey - 9), S(cx + 50), S(ey + 9)], radius=S(9), fill=AMB)
            taper_line(cd, [(cx - 66, ey - 40), (cx + 66, ey - 34)], 16, 6, EMBER)
    glow = core.filter(ImageFilter.GaussianBlur(S(9)))
    im.alpha_composite(glow); im.alpha_composite(glow); im.alpha_composite(core)
    return scale_about(im, 1.45, 512, 470)

# ------------------------------------------------------------------ EMBER creature face (storybook family: thin dark ink, amber iris)
SINK = (52, 30, 22, 255)
def ember_face(expr):
    im, d = layer(); ex, ey, sp, my = 512, 440, 185, 710
    IRIS = (255, 196, 40, 255)
    def eye(cx, s, r=104, look=(0, 0), pup=1.0, lid=0.0, brow=0, browlift=0):
        lay = Image.new('RGBA', im.size, (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        ell(ld, cx, ey, r * 0.92, r, fill=WHITE)
        ell(ld, cx + look[0], ey + look[1] + 6, r * 0.6, r * 0.66, fill=IRIS)
        ell(ld, cx + look[0], ey + look[1] + 10, r * 0.36 * pup, r * 0.42 * pup, fill=(30, 18, 12, 255))
        ell(ld, cx + look[0] + 22, ey + look[1] - 22, 17, 17, fill=WHITE); ell(ld, cx + look[0] - 18, ey + look[1] + 30, 7, 7, fill=WHITE)
        if lid > 0: ld.rectangle([S(cx - r - 4), S(ey - r - 4), S(cx + r + 4), S(ey - r + 2 * r * lid)], fill=(0, 0, 0, 0))
        m = Image.new('L', im.size, 0); ImageDraw.Draw(m).ellipse([S(cx - r * 0.92), S(ey - r), S(cx + r * 0.92), S(ey + r)], fill=255)
        im.alpha_composite(Image.composite(lay, Image.new('RGBA', im.size, (0, 0, 0, 0)), m))
        top = ey - r + 2 * r * lid if lid > 0 else None
        if lid > 0: taper_line(d, [(cx - r * 0.95, top + 6), (cx, top - 4), (cx + r * 0.95, top + 6)], 22, 10, SINK)
        else: taper_line(d, arc_pts(cx, ey, r * 0.92, r, 190, 350), 18, 8, SINK)
        taper_line(d, arc_pts(cx, ey, r * 0.92, r, 20, 160), 8, 4, SINK)
        a = math.radians(brow); by = ey - r - 44 - browlift
        taper_line(d, [(cx - s * 70, by + s * s * math.sin(a) * 40), (cx + s * 64, by - math.sin(a) * 40)], 18, 6, SINK)
    if expr == 'happy':
        for s in (-1, 1): taper_line(d, arc_pts(ex + s * sp, ey + 34, 84, 66, 200, 340), 24, 10, SINK)
        d.chord([S(430), S(my - 70), S(594), S(my + 64)], 0, 180, fill=(120, 30, 30, 255), outline=SINK, width=S(10))
        d.polygon([(S(452), S(my - 4)), (S(470), S(my + 30)), (S(488), S(my - 4))], fill=WHITE)
        ell(d, 512, my + 38, 36, 16, fill=(214, 92, 70, 255))
    elif expr == 'curious':
        for s in (-1, 1): eye(ex + s * sp, s, look=(14, -22), brow=-10, browlift=20)
        ell(d, 528, my + 10, 26, 30, fill=(120, 30, 30, 255), outline=SINK, w=10)
    elif expr == 'fierce':
        for s in (-1, 1): eye(ex + s * sp, s, r=96, pup=0.7, lid=0.32, brow=30)
        d.rounded_rectangle([S(424), S(my - 40), S(600), S(my + 60)], radius=S(36), fill=(120, 30, 30, 255), outline=SINK, width=S(10))
        for x in (444, 580):
            d.polygon([(S(x - 16), S(my - 32)), (S(x), S(my + 8)), (S(x + 16), S(my - 32))], fill=WHITE)
        ell(d, 512, my + 34, 46, 16, fill=(214, 92, 70, 255))
    elif expr == 'scared':
        for s in (-1, 1): eye(ex + s * sp, s, r=110, pup=0.45, brow=-26, browlift=24)
        pts = [(424 + 22 * i, my + (16 if i % 2 else -16)) for i in range(9)]; taper_line(d, pts, 20, 10, SINK)
    elif expr == 'proud':
        for s in (-1, 1): eye(ex + s * sp, s, r=100, lid=0.42, look=(0, 10), brow=8)
        taper_line(d, [(436, my - 4), (500, my + 16), (560, my + 6), (600, my - 30)], 18, 8, SINK)
        d.polygon([(S(540), S(my + 6)), (S(552), S(my + 34)), (S(566), S(my + 2))], fill=WHITE)
    return scale_about(im, 1.1, 512, 520)

# ------------------------------------------------------------------ SQUIRE extras in the toybox family
TINK, TONG = F.TINK, F.TONG
def squire_extra(expr):
    im, d = layer(); ex, ey, sp, w, my = 512, 430, 165, 40, 700
    def doteyes(ry=56):
        for s in (-1, 1): ell(d, ex + s * sp, ey, 40, ry, fill=TINK)
    def brow(s, a, y=ey - 150, L=110):
        dx, dy = L * math.cos(math.radians(a)), L * math.sin(math.radians(a))
        taper_line(d, [(ex + s * sp - dx, y - dy * s * -1), (ex + s * sp, y), (ex + s * sp + dx, y + dy * s * -1)], w * 1.1, w * 0.45, TINK)
    if expr == 'relieved':
        for s in (-1, 1): taper_line(d, arc_pts(ex + s * sp, ey - 20, 74, 50, 20, 160), w, w * 0.5, TINK)
        brow(-1, -22); brow(1, -22)
        taper_line(d, arc_pts(512, my - 40, 90, 50, 25, 155), w, w * 0.5, TINK)
        d.polygon([(S(800), S(250)), (S(770), S(340)), (S(830), S(340))], fill=(110, 190, 250, 255)); ell(d, 800, 350, 31, 31, fill=(110, 190, 250, 255))
    elif expr == 'deadpan':
        for s in (-1, 1):
            ell(d, ex + s * sp, ey + 14, 40, 40, fill=TINK)
            d.rectangle([S(ex + s * sp - 70), S(ey - 80), S(ex + s * sp + 70), S(ey + 6)], fill=(0, 0, 0, 0))
            taper_line(d, [(ex + s * sp - 66, ey + 4), (ex + s * sp + 66, ey + 4)], w, w * 0.7, TINK)
        taper_line(d, [(446, my + 4), (578, my + 4)], w, w * 0.8, TINK)
    elif expr == 'awe':
        for s in (-1, 1):
            ell(d, ex + s * sp, ey, 100, 112, fill=(255, 255, 255, 255), outline=TINK, w=w * 0.7)
            ell(d, ex + s * sp, ey + 10, 56, 60, fill=TINK)
            ell(d, ex + s * sp + 22, ey - 18, 20, 20, fill=(255, 255, 255, 255)); ell(d, ex + s * sp - 18, ey + 34, 9, 9, fill=(255, 255, 255, 255))
        brow(-1, -14, y=ey - 175); brow(1, -14, y=ey - 175)
        ell(d, 512, my + 24, 40, 52, fill=TINK)
    elif expr == 'brave':
        doteyes(50); brow(-1, 20); brow(1, 20)
        taper_line(d, [(440, my + 10), (512, my + 4), (590, my - 12)], w, w * 0.6, TINK)
    elif expr == 'blink':
        for s in (-1, 1): taper_line(d, [(ex + s * sp - 60, ey + 6), (ex + s * sp, ey + 14), (ex + s * sp + 60, ey + 6)], w, w * 0.6, TINK)
        taper_line(d, [(450, my), (512, my + 4), (574, my)], w, w * 0.5, TINK)
    elif expr == 'talk_closed':
        taper_line(d, [(450, my), (512, my + 4), (574, my)], w, w * 0.5, TINK)
    elif expr == 'talk_half':
        d.chord([S(440), S(my - 40), S(584), S(my + 60)], 0, 180, fill=TINK); ell(d, 512, my + 30, 40, 16, fill=TONG)
    elif expr == 'talk_open':
        d.rounded_rectangle([S(430), S(my - 40), S(594), S(my + 100)], radius=S(56), fill=TINK); ell(d, 512, my + 66, 54, 26, fill=TONG)
    return im

# ------------------------------------------------------------------ helpers for existing packs
def load(p): return Image.open(p).convert('RGBA')
def splice(top_img, bot_img, cut):
    """top part (eyes/brows) of top_img + bottom part (mouth) of bot_img, cut = fraction of height from the top"""
    a = top_img.copy(); y = int(cut * a.size[1])
    a.paste(Image.new('RGBA', (a.size[0], a.size[1] - y), (0, 0, 0, 0)), (0, y))
    b = bot_img.copy(); b.paste(Image.new('RGBA', (b.size[0], y), (0, 0, 0, 0)), (0, 0))
    a.alpha_composite(b); return a
def recolour_iris(im, hue_deg, sat=None, val=0.8):
    """storybook irises are green: move green, saturated pixels to another hue (grey if sat=0)"""
    a = np.array(im).astype(np.float32) / 255.0
    rgb = a[..., :3]; mx = rgb.max(-1); mn = rgb.min(-1); dl = mx - mn
    g = (rgb[..., 1] >= rgb[..., 0]) & (rgb[..., 1] >= rgb[..., 2]) & (dl > 0.08) & (a[..., 3] > 0.05)
    out_ = a.copy()
    for y, x in zip(*np.nonzero(g)):
        h, s, v = colorsys.rgb_to_hsv(*rgb[y, x])
        r2 = colorsys.hsv_to_rgb(hue_deg / 360.0, s if sat is None else s * sat, min(1.0, v * val))
        out_[y, x, :3] = r2
    return Image.fromarray((out_ * 255).astype(np.uint8), 'RGBA')

def eye_glow_overlay():
    """glowing-iris overlay for the True-Form lead, registered to face_bright's iris positions (found from the image)"""
    base = np.array(load(HERO + 'face_bright.png'))
    H_, W_ = base.shape[:2]; al = base[..., 3]; lum = base[..., :3].mean(-1)
    band = slice(int(0.30 * H_), int(0.48 * H_))
    cen = []
    for half in (slice(0, W_ // 2), slice(W_ // 2, W_)):
        sub_a = al[band, half]; sub_l = lum[band, half]
        m = (sub_a > 200) & (sub_l < 90)   # dark iris/pupil ink
        ys, xs = np.nonzero(m)
        # iris = the densest dark blob near the middle of the eye band
        cy, cx = np.median(ys), np.median(xs)
        cen.append((cx + half.start, cy + band.start))
    im = Image.new('RGBA', (W_, H_), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    for cx, cy in cen:
        r = W_ * 0.042
        d.ellipse([cx - r, cy - r * 1.12, cx + r, cy + r * 1.12], fill=(255, 168, 24, 255))
        d.ellipse([cx - r * 0.62, cy - r * 0.7, cx + r * 0.62, cy + r * 0.7], fill=(255, 214, 90, 255))
        d.ellipse([cx - r * 0.26, cy - r * 0.3, cx + r * 0.26, cy + r * 0.3], fill=(255, 248, 220, 255))
    g = im.filter(ImageFilter.GaussianBlur(W_ * 0.014)); g.alpha_composite(im)
    return g, cen

def hero_new(expr):
    """two new decals for the True-Form lead, cut from the Hero kid's own pack so the style is identical"""
    if expr == 'locked_in':
        top = load(HERO + 'face_fierce.png')                     # narrowed, intent eyes from the same catalogue
        im = splice(top, Image.new('RGBA', top.size, (0, 0, 0, 0)), 0.685)
        d = ImageDraw.Draw(im); Wd = im.size[0]
        y = int(0.735 * Wd)                                        # flat, firm mouth in the pack's grey ink
        for i, (x0, x1, wdt) in enumerate([(0.43, 0.57, 9), (0.415, 0.585, 5)]):
            d.line([(x0 * Wd, y + i * 2), (x1 * Wd, y - 4 + i * 2)], fill=(34, 30, 32, 255), width=wdt)
        return im
    if expr == 'calm_smirk':
        top = load(HERO + 'face_cool.png'); bot = load(HERO + 'face_cool.png')
        return splice(top, bot, 0.685)

def sheet(setname, exprs, bg=(226, 176, 136), cols=6, cell=200):
    rows = (len(exprs) + cols - 1) // cols
    o = Image.new('RGB', (cols * cell, rows * (cell + 26)), (245, 240, 232)); d = ImageDraw.Draw(o)
    for i, e in enumerate(exprs):
        p = os.path.join(ROOT, setname, e + '.png')
        if not os.path.exists(p): continue
        im = load(p).resize((cell - 8, cell - 8), Image.LANCZOS)
        x, y = (i % cols) * cell, (i // cols) * (cell + 26)
        o.paste(Image.new('RGB', (cell - 8, cell - 8), bg), (x + 4, y + 4)); o.paste(im, (x + 4, y + 4), im)
        d.text((x + 8, y + cell - 2), e, fill=(40, 30, 30))
    o.save(os.path.join(ROOT, '_sheet_' + setname + '.png'))

# ================================================================== PHASE 2 (report rows 9-20)
from PIL import ImageOps
HINK = (5, 5, 5, 255)                       # hero catalogue ink (sampled)
def hero(n): return load(HERO + n + '.png')
def blank(sz=1254): return Image.new('RGBA', (sz, sz), (0, 0, 0, 0))

def hero_flat_mouth(im=None, y=0.735, w=0.14):
    """closed mouth in the catalogue's style (two stacked strokes), for talk_closed / locked expressions"""
    im = im or blank(); d = ImageDraw.Draw(im); Wd = im.size[0]; yy = int(y * Wd)
    d.line([((0.5 - w / 2) * Wd, yy), ((0.5 + w / 2) * Wd, yy - 4)], fill=(34, 30, 32, 255), width=9)
    d.line([((0.5 - w / 2 - 0.015) * Wd, yy + 2), ((0.5 + w / 2 + 0.015) * Wd, yy - 2)], fill=(34, 30, 32, 255), width=5)
    return im

def hero_set(top_family, extra=None):
    """blink + talk decals for a catalogue family (e.g. 'bold'): blink = <family>_blink, half = _talk_round, open = _talk_open"""
    return {'blink': hero('face_%s_blink' % top_family), 'talk_half': hero('face_%s_talk_round' % top_family),
            'talk_open': hero('face_%s_talk_open' % top_family), 'talk_closed': hero_flat_mouth()}

def herald_trumpet():
    """puffed trumpet cheeks: eyes squeezed (bold blink top, nose kept), round cheek bulges outlined like the catalogue ink, a pursed 'o' mouth"""
    im = splice(hero('face_bold_blink'), blank(), 0.685); Wd = im.size[0]; d = ImageDraw.Draw(im); INK = (34, 30, 32, 255)
    for s in (-1, 1):
        cx, cy, r = 0.5 + s * 0.2, 0.705, 0.078
        box = [(cx - r) * Wd, (cy - r) * Wd, (cx + r) * Wd, (cy + r) * Wd]
        if s > 0: d.arc(box, 290, 80, fill=INK, width=12)          # outer bulge, right cheek
        else: d.arc(box, 100, 250, fill=INK, width=12)
        for k in (-1, 0, 1):                                       # puff lines
            x0 = cx + s * (r + 0.03); y0 = cy + k * 0.04
            d.line([x0 * Wd, y0 * Wd, (x0 + s * 0.035) * Wd, (y0 + k * 0.012) * Wd], fill=INK, width=7)
    d.ellipse([0.462 * Wd, 0.708 * Wd, 0.538 * Wd, 0.782 * Wd], outline=INK, width=14, fill=(92, 36, 40, 255))
    for k in (-1, 1): d.line([(0.5 + k * 0.05) * Wd, 0.725 * Wd, (0.5 + k * 0.068) * Wd, 0.715 * Wd], fill=INK, width=6)
    return im

def crack(im, seed=3):
    """faint mirror crack: a jagged silver line with a dark hairline beside it, across the whole face"""
    Wd = im.size[0]; rnd = __import__('random').Random(seed)
    pts = [(0.16, 0.2), (0.3, 0.3), (0.4, 0.37), (0.47, 0.5), (0.55, 0.56), (0.6, 0.66), (0.72, 0.74), (0.84, 0.86)]
    pts = [((x + rnd.uniform(-0.012, 0.012)) * Wd, (y + rnd.uniform(-0.012, 0.012)) * Wd) for x, y in pts]
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.line([(x + 3, y + 3) for x, y in pts], fill=(30, 40, 70, 235), width=22, joint='curve')     # dark edge so the crack reads on light skin
    d.line(pts, fill=(232, 242, 255, 255), width=11, joint='curve')
    d.line([pts[3], (pts[3][0] - 0.06 * Wd, pts[3][1] + 0.03 * Wd)], fill=(222, 232, 246, 200), width=4)     # small branch
    d.line([pts[5], (pts[5][0] + 0.05 * Wd, pts[5][1] - 0.035 * Wd)], fill=(222, 232, 246, 200), width=4)
    out_ = im.copy(); out_.alpha_composite(lay); return out_

# storybook helpers (eye centres found from the pack itself)
SB = PACKS + '/storybook/'
def sb(n): return load(SB + n + '.png')
def sb_eye_centres():
    a = np.array(sb('happy')); al = a[..., 3]; W_ = a.shape[1]
    band = slice(int(0.39 * W_), int(0.53 * W_)); cen = []
    for half in (slice(0, W_ // 2), slice(W_ // 2, W_)):
        m = al[band, half] > 128; ys, xs = np.nonzero(m)
        cen.append(((xs.min() + xs.max()) / 2 + half.start, (ys.min() + ys.max()) / 2 + band.start, (xs.max() - xs.min()) / 2, (ys.max() - ys.min()) / 2))
    return cen
SBINK = (40, 30, 24, 255)
def sb_blink(brow_src='happy'):
    """closed storybook eyes (lash arcs) under the source's brows"""
    im = sb(brow_src); a = np.array(im); W_ = a.shape[1]
    for cx, cy, rx, ry in sb_eye_centres():
        a[int(cy - ry - 6):int(cy + ry + 8), int(cx - rx - 10):int(cx + rx + 10), 3] = 0
    im = Image.fromarray(a, 'RGBA'); d = ImageDraw.Draw(im)
    for cx, cy, rx, ry in sb_eye_centres():
        d.arc([cx - rx * 1.05, cy - ry * 0.75, cx + rx * 1.05, cy + ry * 0.75], 12, 168, fill=(26, 18, 14, 255), width=17)
        for k in (-0.6, 0.0, 0.6): d.line([cx + k * rx * 0.8, cy + ry * 0.66, cx + k * rx * 1.05, cy + ry * 1.05], fill=(26, 18, 14, 255), width=7)
    return im
def sb_mouth_only(src):
    im = sb(src); return splice(Image.new('RGBA', im.size, (0, 0, 0, 0)), im, 0.6)
def sb_talk(kind):
    if kind == 'talk_closed': return sb_mouth_only('determined')
    if kind == 'talk_open': return sb_mouth_only('laughing')
    im = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0)); d = ImageDraw.Draw(im)       # half: small open mouth
    d.chord([452, 640, 572, 712], 0, 180, fill=(110, 36, 40, 255), outline=SBINK, width=8)
    d.line([448, 676, 576, 676], fill=SBINK, width=8)
    return im
def stretch_mouth(im, k=2.2, y0=0.6):
    """jaw-drop: stretch the mouth region vertically about its top"""
    W_ = im.size[0]; top = int(y0 * W_)
    low = im.crop((0, top, W_, W_)); low = low.resize((W_, int((W_ - top) * k)), Image.BICUBIC).crop((0, 0, W_, W_ - top))
    out_ = im.copy(); out_.paste(Image.new('RGBA', (W_, W_ - top), (0, 0, 0, 0)), (0, top)); out_.alpha_composite(low, (0, top)); return out_
def elder_lines(im):
    """two small crow's-feet strokes at the outer eye corners + one forehead line (elders)"""
    d = ImageDraw.Draw(im)
    for cx, cy, rx, ry in sb_eye_centres():
        s = -1 if cx < 512 else 1; x0 = cx + s * (rx + 18)
        for k in (-1, 1): d.line([x0, cy + k * 6, x0 + s * 26, cy + k * 18], fill=(70, 46, 34, 200), width=5)
    return im

# horde: glowing dot eyes + carved brows on stone (emissive like the Jailer's hood)
def horde_face(state, glow_rgb):
    im = Image.new('RGBA', (N * SS, N * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    G = glow_rgb + (255,); HOT = tuple(min(255, int(c * 0.4 + 160)) for c in glow_rgb) + (255,); CARVE = (14, 12, 14, 255)
    ex, ey, sp = 512, 450, 165
    core = Image.new('RGBA', im.size, (0, 0, 0, 0)); cd = ImageDraw.Draw(core)
    for s in (-1, 1):
        cx = ex + s * sp
        if state == 'glare':
            ell(cd, cx, ey, 40, 40, fill=G); ell(cd, cx, ey, 18, 18, fill=HOT)
            d.polygon([(S(cx - s * 90), S(ey - 86)), (S(cx + s * 78), S(ey - 132)), (S(cx + s * 84), S(ey - 96)), (S(cx - s * 84), S(ey - 52))], fill=CARVE)
        elif state == 'roar':
            ell(cd, cx, ey, 44, 34, fill=G); ell(cd, cx, ey, 20, 14, fill=HOT)
            d.polygon([(S(cx - s * 90), S(ey - 70)), (S(cx + s * 80), S(ey - 140)), (S(cx + s * 86), S(ey - 102)), (S(cx - s * 86), S(ey - 38))], fill=CARVE)
        elif state == 'stunned':
            ell(cd, cx, ey, 30, 30, fill=G); ell(cd, cx, ey, 12, 12, fill=HOT)
            taper_line(d, arc_pts(cx, ey - 70, 76, 34, 200, 340), 30, 14, CARVE)
    if state == 'roar':
        d.polygon([(S(x), S(y)) for x, y in [(392, 640), (632, 640), (600, 800), (424, 800)]], fill=CARVE)
        inner = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(inner).polygon([(S(x), S(y)) for x, y in [(424, 676), (600, 676), (580, 772), (444, 772)]], fill=tuple(int(c * 0.45) for c in glow_rgb) + (255,))
        im.alpha_composite(inner)
        for x in (432, 560): d.polygon([(S(x), S(640)), (S(x + 32), S(640)), (S(x + 16), S(690))], fill=(200, 196, 186, 255))   # two blocky tusks
    elif state == 'glare':
        d.polygon([(S(x), S(y)) for x, y in [(420, 700), (604, 690), (604, 716), (420, 728)]], fill=CARVE)
    else:
        ell(d, 512, 712, 30, 38, fill=CARVE)
    glow_ = core.filter(ImageFilter.GaussianBlur(S(8)))
    im.alpha_composite(glow_); im.alpha_composite(glow_); im.alpha_composite(core)
    return scale_about(im, 1.35, 512, 560)

def magenta_eye_overlay():
    """Turned Friend: one glowing magenta eye, registered to the toybox right-of-image eye (the character's left)"""
    im = Image.new('RGBA', (N * SS, N * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(im); cx, cy = 512 + 165, 430
    core = Image.new('RGBA', im.size, (0, 0, 0, 0)); cd = ImageDraw.Draw(core)
    ell(cd, cx, cy, 62, 66, fill=(255, 40, 200, 255)); ell(cd, cx, cy, 30, 34, fill=(255, 190, 245, 255))
    g = core.filter(ImageFilter.GaussianBlur(S(14))); im.alpha_composite(g); im.alpha_composite(core)
    return im

def phase2():
    # 17 HERALD: catalogue 'bold' family on medium-brown skin
    for e, src in [('announce', 'face_bold'), ('stern', 'face_bold_angry'), ('shocked', 'face_bold_shocked'), ('nervous', 'face_bold_scared')]:
        out('herald', e, hero(src))
    out('herald', 'trumpet', herald_trumpet())
    for e, im in hero_set('bold').items(): out('herald', e, im)
    # 9 GOLDEN SISTER: the hero's catalogue (starry / sweet family)
    G = {'proud': hero('face_starry'), 'kind': hero('face_sweet'), 'shocked': hero('face_sweet_shocked'), 'scared': hero('face_sweet_scared'),
         'determined': splice(hero('face_fierce'), hero_flat_mouth(), 0.685), 'humbled': splice(hero('face_calm'), hero('face_sweet_angry'), 0.685)}
    for e, im in G.items(): out('golden_sister', e, im)
    for e, im in hero_set('sweet').items(): out('golden_sister', e, im)
    # 18 RIVAL HEIR: catalogue calm / cool family, 8 faces
    R_ = {'cool': hero('face_cool'), 'doubtful': splice(hero('face_calm_angry'), hero('face_cool'), 0.685), 'smile': hero('face_calm'), 'wink': hero('face_wink'),
          'determined': splice(hero('face_fierce'), hero_flat_mouth(), 0.685), 'angry': hero('face_calm_angry'), 'shocked': hero('face_calm_shocked'), 'scared': hero('face_calm_scared')}
    for e, im in R_.items(): out('rival_heir', e, im)
    for e, im in hero_set('calm').items(): out('rival_heir', e, im)
    # 19 MIRROR TWIN: the lead's own set (bright family), mirrored (highlights on the other side), cold smirk, silver crack on every decal
    M = {'cold_smirk': hero('face_cool'), 'bright': hero('face_bright'), 'angry': hero('face_bright_angry'), 'shocked': hero('face_bright_shocked'), 'scared': hero('face_bright_scared')}
    M.update(hero_set('bright'))
    for e, im in M.items(): out('mirror_twin', e, crack(ImageOps.mirror(im)))
    # 16 TURNED FRIEND: the Squire's toybox family + one glowing magenta eye overlay
    F.OUT = os.path.join(ROOT, '_toybox')
    for e in ['angry', 'smug']: F.toybox(e)
    T_ = {'cold': 'squire/deadpan', 'scowl': '_toybox/toybox_angry', 'smirk': '_toybox/toybox_smug', 'sad': 'squire/sad', 'shocked': 'squire/shocked',
          'blink': 'squire/blink', 'talk_closed': 'squire/talk_closed', 'talk_half': 'squire/talk_half', 'talk_open': 'squire/talk_open'}
    for e, src in T_.items(): out('turned_friend', e, load(os.path.join(ROOT, src + '.png')))
    out('turned_friend', 'eye_glow', magenta_eye_overlay())
    # 20 JESTER: sharp rival family, violet iris, freckles
    for e in ['sly_grin', 'cackle', 'wink', 'shocked', 'serious', 'innocence', 'blink', 'talk_closed', 'talk_half', 'talk_open']:
        out('jester', e, sharp_face(e, (128, 84, 196, 255), freck=True))
    # storybook family: elders, trader, smith (iris recoloured per person) + blink + talk mouths in the pack's style
    talk = {k: sb_talk(k) for k in ('talk_closed', 'talk_half', 'talk_open')}
    SBS = {
        'old_legend': ((215, 0.25, 0.75), True, {'sly': sb('smug'), 'fierce': sb('angry'), 'kind': sb('happy'), 'laughing': sb('laughing'), 'shocked': sb('shocked'), 'weary': sb('sad')}),
        'roll_merchant': ((36, 1.0, 0.62), False, {'knowing_grin': splice(sb('smug'), sb('big-grin'), 0.6), 'welcome': sb('happy'), 'jaw_drop': stretch_mouth(splice(sb('terrified'), sb('shocked'), 0.6), 2.3),
                                                   'curious': sb('confused'), 'nervous': sb('nervous'), 'delighted': sb('laughing')}),
        'master_smith': ((22, 0.9, 0.55), False, {'judging': sb('determined'), 'stern': sb('angry'), 'impressed': sb('happy'), 'shocked': sb('shocked'), 'laughing': sb('laughing'), 'doubtful': sb('confused')}),
        'stone_keeper': ((262, 0.7, 0.7), True, {'solemn': sb('determined'), 'stern': sb('angry'), 'approving': sb('happy'), 'stunned': splice(sb('shocked'), sb('sad'), 0.6), 'sorrowful': sb('sad')}),
    }
    for who, ((hue, sat, val), elder, faces) in SBS.items():
        for e, im in list(faces.items()) + [('blink', sb_blink())] + list(talk.items()):
            im = recolour_iris(im, hue, sat, val) if not e.startswith('talk') else im
            if elder and not e.startswith('talk'): im = elder_lines(im)
            out(who, e, im)
    # 10 HORDE: four glow colours
    for who, rgb in [('horde_slate', (255, 170, 40)), ('horde_ash', (255, 70, 30)), ('horde_moss', (200, 240, 60)), ('horde_frost', (40, 150, 255))]:
        for st in ['glare', 'roar', 'stunned']: out(who, st, horde_face(st, rgb))
    for st in ['glare', 'roar', 'hurt']: out('boss_giant', st, horde_face('stunned' if st == 'hurt' else st, (255, 214, 120)))
    for s in ['boss_giant', 'herald', 'golden_sister', 'rival_heir', 'mirror_twin', 'turned_friend', 'jester', 'old_legend', 'roll_merchant', 'master_smith', 'stone_keeper',
              'horde_slate', 'horde_ash', 'horde_moss', 'horde_frost']:
        skin = {'herald': (150, 100, 66), 'golden_sister': (238, 196, 156), 'rival_heir': (214, 168, 128), 'mirror_twin': (238, 196, 156), 'turned_friend': (245, 205, 48),
                'jester': (240, 206, 182), 'old_legend': (96, 62, 42), 'roll_merchant': (196, 150, 108), 'master_smith': (100, 64, 44), 'stone_keeper': (132, 90, 62)}.get(s, (70, 72, 78))
        sheet(s, sorted(x[:-4] for x in os.listdir(os.path.join(ROOT, s))), bg=skin)
    print('faces p2 ok')

if __name__ == '__main__' and os.environ.get('FACES_PHASE') == '2':
    phase2(); sys.exit(0)

if __name__ == '__main__':
    os.makedirs(ROOT, exist_ok=True)
    # sharp rival set, two variants
    for e in ['neutral', 'blink', 'smug', 'sneer', 'shocked', 'furious', 'humiliated', 'respect', 'talk_closed', 'talk_half', 'talk_open']:
        out('first_rank', e, sharp_face(e, (70, 128, 205, 255)))
    for e in ['neutral', 'blink', 'sneer', 'innocence', 'gloat', 'panic', 'caught', 'sulk', 'talk_closed', 'talk_half', 'talk_open']:
        out('rigger', e, sharp_face(e, (128, 150, 40, 255), shifty=True))
    for st in ['dim', 'bright', 'narrowed', 'flicker']: out('oathbound', st, visor(st))
    for st in ['glare', 'angry', 'surprised', 'squint']: out('jailer', st, hood_eyes(st))
    for e in ['happy', 'curious', 'fierce', 'scared', 'proud']: out('ember', e, ember_face(e))
    # Squire: toybox family (regenerated from faces.py) + new expressive extras + blink + talk mouths
    F.OUT = os.path.join(ROOT, '_toybox'); os.makedirs(F.OUT, exist_ok=True)
    for e in ['neutral', 'grin', 'shocked', 'terrified', 'sad']:
        F.toybox(e); out('squire', e, load(os.path.join(F.OUT, 'toybox_' + e + '.png')))
    for e in ['relieved', 'deadpan', 'awe', 'brave', 'blink', 'talk_closed', 'talk_half', 'talk_open']: out('squire', e, squire_extra(e))
    # True-Form lead: the Hero kid's own pack + 2 new + glow overlay + blink + talk shapes
    for src, e in [('face_bright', 'bright'), ('face_bright_angry', 'angry'), ('face_bright_shocked', 'shocked'), ('face_bright_scared', 'scared'),
                   ('face_bright_blink', 'blink'), ('face_bright_talk_round', 'talk_half'), ('face_bright_talk_open', 'talk_open')]:
        out('true_form', e, load(HERO + src + '.png'))
    for e in ['locked_in', 'calm_smirk']: out('true_form', e, hero_new(e))
    out('true_form', 'talk_closed', splice(Image.new('RGBA', (1254, 1254), (0, 0, 0, 0)), hero_new('locked_in'), 0.685))
    g, cen = eye_glow_overlay(); out('true_form', 'eye_glow', g); print('iris centres', cen)
    # Crowd Six: storybook (iris recoloured per person) and classic-block; neutral = happy eyes + determined's flat mouth
    for who, hue, sat, val in [('crowd_pointer', 210, 0.55, 0.85), ('crowd_laugher', 28, 0.9, 0.55), ('crowd_gasper', 32, 1.0, 0.7), ('crowd_dropper', 200, 0.15, 0.8)]:
        P = PACKS + '/storybook/'
        faces = {'neutral': splice(load(P + 'happy.png'), load(P + 'determined.png'), 0.6), 'shocked': load(P + 'shocked.png'), 'laughing': load(P + 'laughing.png')}
        for e, im in faces.items(): out(who, e, recolour_iris(im, hue, sat, val))
    for who in ['crowd_whisperer', 'crowd_cheerer']:
        P = PACKS + '/classic-block/'
        out(who, 'neutral', splice(load(P + 'happy.png'), load(P + 'determined.png'), 0.6))
        out(who, 'shocked', load(P + 'shocked.png')); out(who, 'laughing', load(P + 'laughing.png'))
    for s in sorted(os.listdir(ROOT)):
        if s.startswith('_') or not os.path.isdir(os.path.join(ROOT, s)): continue
        bg = (30, 32, 40) if s in ('oathbound', 'jailer') else (226, 176, 136)
        sheet(s, sorted(x[:-4] for x in os.listdir(os.path.join(ROOT, s))), bg=bg)
    print('faces ok')
