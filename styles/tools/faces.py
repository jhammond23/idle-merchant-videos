# Our own face decals for each character kit (drawn from the kits' written specs; no source pixels).
# 1024x1024 RGBA, features centred, eye line ~42%, mouth ~68% (head_mat2 maps image centre = head centre).
import math, os, sys
from PIL import Image, ImageDraw

N = 1024
OUT = sys.argv[1] if len(sys.argv) > 1 else '/tmp/claude-0/kits/faces'
os.makedirs(OUT, exist_ok=True)
SS = 2  # supersample

def canvas():
    im = Image.new('RGBA', (N * SS, N * SS), (0, 0, 0, 0)); return im, ImageDraw.Draw(im)
def S(v): return int(v * SS)
def save(im, name):
    im.resize((N, N), Image.LANCZOS).save(os.path.join(OUT, name + '.png'))

def taper_line(d, pts, w0, w1, col):
    """polyline whose width tapers from w0 (middle) to w1 (ends)"""
    n = len(pts)
    for i in range(n - 1):
        t = i / (n - 2) if n > 2 else 0.5
        w = w1 + (w0 - w1) * math.sin(math.pi * t)
        d.line([S(pts[i][0]), S(pts[i][1]), S(pts[i + 1][0]), S(pts[i + 1][1])], fill=col, width=max(2, S(w)))
        r = S(w) / 2; x, y = S(pts[i + 1][0]), S(pts[i + 1][1])
        d.ellipse([x - r, y - r, x + r, y + r], fill=col)

def arc_pts(cx, cy, rx, ry, a0, a1, k=24):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / k)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / k))) for i in range(k + 1)]

def ell(d, cx, cy, rx, ry, fill=None, outline=None, w=0):
    d.ellipse([S(cx - rx), S(cy - ry), S(cx + rx), S(cy + ry)], fill=fill, outline=outline, width=S(w) if w else 0)

# ---------------- Sunny Block Folk (bright-cut): line faces + comic close-up faces ----------------
INK = (19, 18, 27, 255)
PINK = (240, 108, 143, 255)
def sunny_line(expr):
    im, d = canvas(); ex, ey, sp = 512, 430, 150; w = 26
    def dots(r=26, ry=34):
        for s in (-1, 1): ell(d, ex + s * sp, ey, r, ry, fill=INK)
    def brows(ang, y=330, L=70):
        for s in (-1, 1):
            a = math.radians(ang) * s
            x0, y0 = ex + s * sp - L * math.cos(a) * s, y - L * math.sin(a) * (-1)
            d.line([S(ex + s * sp - L), S(y + s * 0), S(ex + s * sp + L), S(y)], fill=INK, width=S(w))
    my = 690
    if expr == 'neutral': dots(); d.line([S(440), S(my), S(584), S(my)], fill=INK, width=S(w))
    elif expr == 'happy':
        for s in (-1, 1): taper_line(d, arc_pts(ex + s * sp, ey + 20, 46, 40, 200, 340), w, w * 0.6, INK)
        taper_line(d, arc_pts(512, my - 40, 120, 70, 15, 165), w, w * 0.6, INK)
    elif expr == 'smug':
        for s in (-1, 1): d.line([S(ex + s * sp - 50), S(ey), S(ex + s * sp + 50), S(ey)], fill=INK, width=S(w)); ell(d, ex + s * sp + 14, ey + 18, 16, 16, fill=INK)
        taper_line(d, [(430, my + 10), (500, my + 18), (560, my + 6), (610, my - 26)], w, w * 0.6, INK)
    elif expr == 'shocked':
        for s in (-1, 1): ell(d, ex + s * sp, ey, 34, 44, outline=INK, w=w * 0.8); ell(d, ex + s * sp, ey, 9, 9, fill=INK)
        ell(d, 512, my + 10, 44, 60, fill=INK)
    elif expr == 'scared':
        dots(22, 30)
        for s in (-1, 1): d.line([S(ex + s * sp - 55), S(ey - 95 + 25 * (s < 0)), S(ex + s * sp + 55), S(ey - 95 + 25 * (s > 0))], fill=INK, width=S(w * 0.8))
        pts = [(420 + 23 * i, my + (14 if i % 2 else -14)) for i in range(9)]; taper_line(d, pts, w * 0.8, w * 0.6, INK)
    elif expr == 'angry':
        dots(24, 30)
        for s in (-1, 1): d.line([S(ex + s * sp - 60), S(ey - 110), S(ex + s * sp + 60), S(ey - 70)] if s < 0 else [S(ex + s * sp - 60), S(ey - 70), S(ex + s * sp + 60), S(ey - 110)], fill=INK, width=S(w))
        taper_line(d, arc_pts(512, my + 60, 100, 50, 200, 340), w, w * 0.6, INK)
    elif expr == 'crying':
        for s in (-1, 1): taper_line(d, arc_pts(ex + s * sp, ey - 10, 44, 30, 20, 160), w, w * 0.6, INK); d.rectangle([S(ex + s * sp - 14), S(ey + 30), S(ex + s * sp + 14), S(ey + 170)], fill=(90, 170, 240, 255))
        taper_line(d, arc_pts(512, my + 60, 100, 50, 200, 340), w, w * 0.6, INK)
    elif expr == 'determined':
        dots(24, 32)
        for s in (-1, 1): d.line([S(ex + s * sp - 60), S(ey - 100)] + [S(ex + s * sp + 60), S(ey - 78)] if s < 0 else [S(ex + s * sp - 60), S(ey - 78), S(ex + s * sp + 60), S(ey - 100)], fill=INK, width=S(w))
        taper_line(d, [(440, my + 6), (512, my), (590, my - 14)], w, w * 0.7, INK)
    save(im, 'sunny_line_' + expr)

def sunny_comic(expr):
    im, d = canvas(); ex, ey, sp = 512, 420, 160; R = 120; w = 26; my = 720
    WHITE = (255, 255, 255, 255)
    def eyes(pup=26, dy=0, lid=False):
        for s in (-1, 1):
            ell(d, ex + s * sp, ey, R * 0.95, R, fill=WHITE, outline=INK, w=w)
            ell(d, ex + s * sp, ey + dy, pup, pup, fill=INK)
            if lid: d.rectangle([S(ex + s * sp - R), S(ey - R - 4), S(ex + s * sp + R), S(ey - 20)], fill=(0, 0, 0, 0)); d.line([S(ex + s * sp - R + 10), S(ey - 20), S(ex + s * sp + R - 10), S(ey - 20)], fill=INK, width=S(w))
    if expr == 'shocked':
        eyes(12); ell(d, 512, my + 30, 80, 100, fill=INK); ell(d, 512, my + 80, 50, 34, fill=PINK)
    elif expr == 'angry':
        eyes(30, 10)
        for s in (-1, 1): d.polygon([(S(ex + s * sp - 140 * s), S(ey - 150)), (S(ex + s * sp + 120 * s), S(ey - 60)), (S(ex + s * sp + 120 * s), S(ey - 20)), (S(ex + s * sp - 140 * s), S(ey - 110))], fill=INK)
        d.rounded_rectangle([S(380), S(my - 10), S(644), S(my + 80)], radius=S(20), fill=WHITE, outline=INK, width=S(w))
        for x in (446, 512, 578): d.line([S(x), S(my - 6), S(x), S(my + 76)], fill=INK, width=S(10))
        d.line([S(384), S(my + 35), S(640), S(my + 35)], fill=INK, width=S(10))
    elif expr == 'happy':
        for s in (-1, 1): taper_line(d, arc_pts(ex + s * sp, ey + 30, 90, 70, 200, 340), w * 1.3, w * 0.7, INK)
        d.chord([S(380), S(my - 110), S(644), S(my + 110)], 0, 180, fill=INK); ell(d, 512, my + 60, 70, 40, fill=PINK)
    elif expr == 'scared':
        eyes(14, -8)
        pts = [(380 + 33 * i, my + (18 if i % 2 else -18)) for i in range(9)]; taper_line(d, pts, w, w * 0.7, INK)
        for s in (-1, 1): d.line([S(ex + s * sp - 80), S(ey - 140 + 40 * (s < 0)), S(ex + s * sp + 80), S(ey - 140 + 40 * (s > 0))], fill=INK, width=S(w))
    save(im, 'sunny_comic_' + expr)

# ---------------- Toybox Blockfolk (craftee-style): thick tapered ink line art ----------------
TINK = (30, 20, 14, 255)
TONG = (242, 160, 168, 255)
def toybox(expr):
    im, d = canvas(); ex, ey, sp = 512, 430, 165; w = 40; my = 700
    WHITE = (255, 255, 255, 255)
    def bigeyes(pr=44, dy=0, rx=105, ry=112):
        for s in (-1, 1): ell(d, ex + s * sp, ey, rx, ry, fill=WHITE, outline=TINK, w=w * 0.75); ell(d, ex + s * sp, ey + dy, pr, pr, fill=TINK)
    def doteyes():
        for s in (-1, 1): ell(d, ex + s * sp, ey, 40, 56, fill=TINK)
    def brow(s, a, y=ey - 150, L=110):
        dx, dy = L * math.cos(math.radians(a)), L * math.sin(math.radians(a))
        taper_line(d, [(ex + s * sp - dx, y - dy * s * -1), (ex + s * sp, y), (ex + s * sp + dx, y + dy * s * -1)], w * 1.1, w * 0.45, TINK)
    if expr == 'neutral':
        doteyes(); taper_line(d, [(450, my), (512, my + 4), (574, my)], w, w * 0.5, TINK)
    elif expr == 'happy':
        doteyes(); taper_line(d, arc_pts(512, my - 50, 120, 80, 20, 160), w, w * 0.5, TINK)
    elif expr == 'grin':
        for s in (-1, 1): taper_line(d, arc_pts(ex + s * sp, ey + 40, 80, 70, 200, 340), w, w * 0.5, TINK)
        d.chord([S(370), S(my - 120), S(654), S(my + 110)], 0, 180, fill=TINK); ell(d, 512, my + 60, 80, 40, fill=TONG)
    elif expr == 'innocent':
        bigeyes(40, -55)
        taper_line(d, arc_pts(512, my - 30, 60, 40, 20, 160), w * 0.9, w * 0.5, TINK)
    elif expr == 'shocked':
        bigeyes(22)
        ell(d, 512, my + 30, 70, 90, fill=WHITE, outline=TINK, w=w * 0.7)
    elif expr == 'terrified':
        bigeyes(16); brow(-1, -25); brow(1, -25)
        d.rounded_rectangle([S(372), S(my - 40), S(652), S(my + 130)], radius=S(40), fill=TINK)
        d.rectangle([S(400), S(my - 26), S(624), S(my + 10)], fill=WHITE); d.rectangle([S(400), S(my + 84), S(624), S(my + 118)], fill=WHITE); ell(d, 512, my + 70, 70, 26, fill=TONG)
    elif expr == 'angry':
        doteyes(); brow(-1, 28); brow(1, 28)
        taper_line(d, arc_pts(512, my + 70, 110, 60, 200, 340), w, w * 0.5, TINK)
    elif expr == 'smug':
        for s in (-1, 1): taper_line(d, [(ex + s * sp - 70, ey), (ex + s * sp + 70, ey)], w, w * 0.6, TINK); ell(d, ex + s * sp + 20, ey + 26, 22, 22, fill=TINK)
        taper_line(d, [(420, my + 20), (480, my + 34), (560, my + 10), (620, my - 30)], w, w * 0.5, TINK)
    elif expr == 'sad':
        doteyes(); brow(-1, -22); brow(1, -22)
        taper_line(d, arc_pts(512, my + 70, 100, 50, 200, 340), w, w * 0.5, TINK)
    elif expr == 'crying':
        taper_line(d, [(ex - sp - 55, ey - 45), (ex - sp + 45, ey), (ex - sp - 55, ey + 45)], w, w * 0.5, TINK)
        taper_line(d, [(ex + sp + 55, ey - 45), (ex + sp - 45, ey), (ex + sp + 55, ey + 45)], w, w * 0.5, TINK)
        d.chord([S(390), S(my - 40), S(634), S(my + 160)], 180, 360, fill=(192, 40, 46, 255))
        for s in (-1, 1): d.rounded_rectangle([S(ex + s * sp - 26), S(ey + 50), S(ex + s * sp + 26), S(ey + 260)], radius=S(26), fill=(120, 190, 250, 255))
    save(im, 'toybox_' + expr)


# ---------------- Inkface Blockfolk (gneef-style): solid black ovals, thick tapered brows, red open mouths ----------------
IINK = (17, 17, 17, 255); IRED = (215, 38, 43, 255); IPINK = (240, 106, 106, 255)
def inkface(expr):
    im, d = canvas(); ex, ey, sp = 512, 460, 135; w = 34; my = 716
    WHITE = (255, 255, 255, 255)
    def ovals(rx=46, ry=72):
        for s in (-1, 1): ell(d, ex + s * sp, ey, rx, ry, fill=IINK)
    def brows(a, y=ey - 130):
        for s in (-1, 1):
            dx, dy = 85 * math.cos(math.radians(a)), 85 * math.sin(math.radians(a))
            taper_line(d, [(ex + s * sp - dx, y + dy * s), (ex + s * sp, y), (ex + s * sp + dx, y - dy * s)], w * 1.2, w * 0.5, IINK)
    def openD(wd=120, ht=110):
        d.chord([S(512 - wd), S(my - ht), S(512 + wd), S(my + ht)], 0, 180, fill=IRED, outline=IINK, width=S(w * 0.6)); ell(d, 512, my + ht * 0.55, wd * 0.5, ht * 0.28, fill=IPINK)
    if expr == 'neutral': ovals(); taper_line(d, [(460, my), (564, my)], w, w * 0.6, IINK)
    elif expr == 'smug':
        ovals(42, 52); brows(-8); taper_line(d, [(440, my + 10), (520, my + 18), (590, my - 20)], w, w * 0.5, IINK)
    elif expr == 'happy':
        for s in (-1, 1): taper_line(d, arc_pts(ex + s * sp, ey + 30, 60, 55, 200, 340), w * 1.1, w * 0.5, IINK)
        openD()
    elif expr == 'shocked':
        ovals(40, 66); brows(-25, ey - 150)
        ell(d, 512, my + 20, 70, 84, fill=IINK); ell(d, 512, my + 34, 44, 54, fill=IRED)
    elif expr == 'scared':
        ovals(38, 60); brows(-28)
        pts = [(420 + 23 * i, my + (16 if i % 2 else -16)) for i in range(9)]; taper_line(d, pts, w * 0.9, w * 0.6, IINK)
    elif expr == 'angry':
        ovals(44, 58); brows(26)
        d.rectangle([S(400), S(my - 40), S(624), S(my + 40)], fill=WHITE, outline=IINK, width=S(w * 0.7))
        for x in (456, 512, 568): d.line([S(x), S(my - 36), S(x), S(my + 36)], fill=IINK, width=S(10))
    elif expr == 'crying':
        for s in (-1, 1): taper_line(d, arc_pts(ex + s * sp, ey - 10, 56, 36, 200, 340), w, w * 0.5, IINK); d.rounded_rectangle([S(ex + s * sp - 22), S(ey + 30), S(ex + s * sp + 22), S(ey + 230)], radius=S(22), fill=(110, 195, 244, 255))
        brows(-24); openD(100, 80)
    elif expr == 'terror':
        for s in (-1, 1): ell(d, ex + s * sp, ey, 80, 96, fill=WHITE, outline=IINK, w=w * 0.7); ell(d, ex + s * sp, ey, 14, 14, fill=IINK)
        brows(-30, ey - 160); ell(d, 512, my + 30, 90, 100, fill=IINK); ell(d, 512, my + 46, 60, 64, fill=IRED)
    save(im, 'ink_' + expr)


# ---------------- Sticker Saga Cast (fourth-style): thin ink line faces + anime-lite faces ----------------
SINK = (20, 18, 22, 255)
def sticker(expr):
    im, d = canvas(); ex, ey, sp = 512, 560, 205; w = 16; my = 800
    WHITE = (255, 255, 255, 255)
    if expr == 'calm':
        for s in (-1, 1): ell(d, ex + s * sp, ey, 18, 24, fill=SINK)
        taper_line(d, arc_pts(512, my - 30, 50, 26, 30, 150), w, w * 0.6, SINK)
    elif expr == 'alarmed':
        for s in (-1, 1): ell(d, ex + s * sp, ey, 70, 74, fill=WHITE, outline=SINK, w=w); ell(d, ex + s * sp, ey, 12, 12, fill=SINK)
        ell(d, 512, my + 10, 40, 50, fill=SINK)
    elif expr == 'happy':
        for s in (-1, 1): taper_line(d, arc_pts(ex + s * sp, ey + 20, 52, 44, 200, 340), w * 1.2, w * 0.6, SINK)
        d.chord([S(430), S(my - 70), S(594), S(my + 70)], 0, 180, fill=SINK); ell(d, 512, my + 40, 40, 18, fill=(240, 120, 140, 255))
    elif expr == 'nervous':
        for s in (-1, 1): ell(d, ex + s * sp, ey, 16, 22, fill=SINK); taper_line(d, [(ex + s * sp - 50, ey - 80 + 16 * s), (ex + s * sp + 50, ey - 80 - 16 * s)], w, w * 0.6, SINK)
        pts = [(450 + 16 * i, my + (10 if i % 2 else -10)) for i in range(9)]; taper_line(d, pts, w, w * 0.6, SINK)
        d.polygon([(S(790), S(330)), (S(760), S(420)), (S(820), S(420))], fill=(110, 190, 250, 255)); ell(d, 790, 430, 30, 30, fill=(110, 190, 250, 255))
    elif expr == 'smug':   # anime-lite: half-lid eyes with a coloured iris, lash line, highlight dot, thin arched brows, tiny mouth
        for s in (-1, 1):
            ell(d, ex + s * sp, ey + 10, 62, 62, fill=WHITE)
            ell(d, ex + s * sp, ey + 18, 40, 46, fill=(70, 120, 190, 255)); ell(d, ex + s * sp, ey + 18, 18, 22, fill=SINK); ell(d, ex + s * sp + 14 * s, ey + 2, 9, 9, fill=WHITE)
            d.rectangle([S(ex + s * sp - 80), S(ey - 70), S(ex + s * sp + 80), S(ey - 6)], fill=(0, 0, 0, 0))
            taper_line(d, [(ex + s * sp - 72, ey - 2), (ex + s * sp, ey - 10), (ex + s * sp + 72, ey + 4)], w * 2.0, w * 0.8, SINK)
            taper_line(d, arc_pts(ex + s * sp, ey - 60, 70, 24, 200, 340), w * 0.8, w * 0.4, SINK)
        taper_line(d, [(480, my + 6), (530, my + 10), (556, my - 8)], w, w * 0.5, SINK)
    elif expr == 'shouting':
        for s in (-1, 1): ell(d, ex + s * sp, ey, 20, 26, fill=SINK); taper_line(d, [(ex + s * sp - 60, ey - 90 - 20 * s), (ex + s * sp + 60, ey - 70 + 20 * s)] if s < 0 else [(ex + s * sp - 60, ey - 70 - 20), (ex + s * sp + 60, ey - 90 + 20 - 40)], w * 1.3, w * 0.6, SINK)
        d.chord([S(410), S(my - 70), S(614), S(my + 120)], 0, 180, fill=SINK)
    elif expr == 'blank':
        for s in (-1, 1): ell(d, ex + s * sp, ey, 12, 12, fill=SINK)
        d.line([S(470), S(my), S(554), S(my)], fill=SINK, width=S(w))
    elif expr == 'determined':
        for s in (-1, 1): ell(d, ex + s * sp, ey, 20, 26, fill=SINK); taper_line(d, [(ex + s * sp - 62, ey - 74 - 14 * s), (ex + s * sp + 62, ey - 74 + 14 * s)] if s < 0 else [(ex + s * sp - 62, ey - 88), (ex + s * sp + 62, ey - 60)][::-1], w * 1.3, w * 0.6, SINK)
        d.rectangle([S(450), S(my - 18), S(574), S(my + 18)], fill=WHITE, outline=SINK, width=S(w * 0.8))
    save(im, 'stk_' + expr)

if __name__ == '__main__':
    for e in ['neutral', 'happy', 'smug', 'shocked', 'scared', 'angry', 'crying', 'determined']: sunny_line(e)
    for e in ['shocked', 'angry', 'happy', 'scared']: sunny_comic(e)
    for e in ['neutral', 'happy', 'grin', 'innocent', 'shocked', 'terrified', 'angry', 'smug', 'sad', 'crying']: toybox(e)
    for e in ['neutral', 'smug', 'happy', 'shocked', 'scared', 'angry', 'crying', 'terror']: inkface(e)
    for e in ['calm', 'alarmed', 'happy', 'nervous', 'smug', 'shouting', 'blank', 'determined']: sticker(e)
    print('ok', len(os.listdir(OUT)))
