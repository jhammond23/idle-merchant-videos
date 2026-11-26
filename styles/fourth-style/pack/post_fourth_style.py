"""Comic Sticker Saga (style id `fourth-style`): post-processing and the comic sticker layer.

Everything here is drawn by our own code (PIL + numpy); frames go through ffmpeg as raw RGB the same
way the house gcut pipeline does. Numbers are the measured ones from ../STYLE.md (section 12).

PLAN (JSON): {"fps": 30, "events": [ ... ]}. Frames are at 30 fps; f0 is inclusive, f1 exclusive.
  Frame effects (each takes a frame range):
    {"type": "snap_zoom", "f0": 300, "f1": 330}        +5,+5,+5,+2 % (=+17 % in 5 frames), hold to f1.
                                                       Use it here OR keyed in Blender, not both.
    {"type": "reframe", "f0", "f1", "scale": 1.10}     jump-cut reframe of a held render (5-15 %).
    {"type": "ff_jitter", "f0", "f1", "px": 27, "roll": 0.9, "pulse_hz": 2.9, "pulse": 10}
                                                       retime the action 3-4x first; this adds jitter,
                                                       roll blips and the brightness pulse.
    {"type": "flash", "f": 512, "luma": 36}            +36 luma up over 3 frames, down over 3.
    {"type": "bw", "f0", "f1"}                         black-and-white cutaway (saturation ~0.04).
    {"type": "sepia", "f0", "f1", "seed": 1}           old-photo flashback: sepia, rounded white border
                                                       (24 px, radius 40), vignette, floating dust.
    {"type": "dim", "f0", "f1", "frames": 33, "amount": 0.3}   light dim in a held shot (-30 luma / 1.1 s).
    {"type": "dip_black", "f": 2700, "frames": 3}      1-3 black frames before the sponsor segment.
  Sticker layer (pop in over 5 frames: scale 0 -> 110 % -> 100 %; hard off at f1, i.e. on a cut):
    {"type": "name", "f0", "f1", "text": "WREN", "color": "#3FD0C9", "x": 0.5, "y": 0.2}
    {"type": "bubble", "f0", "f1", "text": "NOT AGAIN!", "x": 0.5, "y": 0.22, "tail": [0.36, 0.40]}
    {"type": "time_tag", "f0", "f1", "text": "DAY THREE", "icon": "hourglass|sun|moon|candle|star",
     "x": 0.07, "y": 0.17}                              rotated -5 deg, +-3 deg wiggle while popping.
    {"type": "gag", "f0", "f1", "kind": "stars|question|exclaim|sweat|anger", "x", "y", "size": 1.0,
     "points": [[x, y], ...]}                           stars orbit; badges pop; points = several badges.
    {"type": "caption", "f0", "f1", "text": "HE WAS {FIRST}", "closeup": false}
                                                       reference captions (see captions_fourth-style.json):
                                                       {gold} [red] <magic>, "dialogue" is gold.
    {"type": "card", "f0", "f1", "premise": "...", "part": "PART 1", "question": ["LINE 1", "LINE 2"],
     "keyword": "WORD", "kw_color": "#FFD23F", "vote": ["A  ...", "B  ..."]}
                                                       background dims 35 % + blur over 8 frames, then
                                                       the card pops; stays up across 2-4 cuts.
  Any event may carry "sfx": "pop" | "thump" | "none" (see `cues`).

CLI (python3 -I post_fourth_style.py ...):
  preview OUTDIR                    stills of every sticker, the card and the effects (no video)
  frames PLAN IN_DIR OUT_DIR        process a rendered PNG sequence (sorted by name, frame 0 first)
  run PLAN IN.mp4 OUT.mp4           pipe a video through (decode -> effects + stickers -> x264, audio copied)
  ffmpeg PLAN                       print an ffmpeg -vf chain for the plain frame effects (no stickers)
  cues PLAN                         sound cue list: a pop on every sticker landing, thumps where asked
  check PNG [PNG...]                measure luma/saturation of stills against the style targets
"""
import json
import math
import os
import random
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H, FPS = 1080, 1920, 30
INK = (11, 11, 16)
WHITE = (255, 255, 255)
COL = {'gold': (255, 210, 63), 'red': (255, 71, 87), 'magic': (180, 140, 255), 'teal': (63, 208, 201),
       'coral': (255, 90, 110), 'blue': (47, 125, 246), 'amber': (255, 182, 39), 'sky': (94, 177, 213),
       'grey': (216, 220, 227), 'sweat': (143, 211, 255)}
HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = {  # first one found wins. Put the free OFL fonts in pack/fonts/ (README).
    'caption': ['fonts/Poppins-ExtraBold.ttf', '/usr/share/fonts/truetype/google-fonts/Poppins-ExtraBold.ttf',
                '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf', '/usr/share/fonts/opentype/inter/Inter-Black.otf'],
    'display': ['fonts/LilitaOne-Regular.ttf', '/usr/share/fonts/truetype/google-fonts/LilitaOne-Regular.ttf',
                '/tmp/claude-0/tv/fonts/FredokaOne-Regular.ttf', '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'],
    'bubble': ['fonts/Poppins-Bold.ttf', '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf',
               '/usr/share/fonts/opentype/inter/Inter-Bold.otf'],
}
_fcache = {}


def font(role, size):
    key = (role, int(size))
    if key not in _fcache:
        for p in FONTS[role]:
            p2 = p if os.path.isabs(p) else os.path.join(HERE, p)
            if os.path.exists(p2):
                _fcache[key] = ImageFont.truetype(p2, int(size))
                break
        else:
            _fcache[key] = ImageFont.load_default(size)
    return _fcache[key]


def font_for_cap(role, cap_px):
    """Font size whose capital H is cap_px tall."""
    f = font(role, 100)
    b = f.getbbox('H')
    return font(role, round(100 * cap_px / max(1, b[3] - b[1])))


def hexc(h):
    if isinstance(h, (tuple, list)):
        return tuple(h)
    if h in COL:
        return COL[h]
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


# --------------------------------------------------------------------------- animation curves
POP = [0.0, 0.55, 0.95, 1.10, 1.0]       # sticker scale over its first 5 frames (measured ~5-frame pop, small overshoot)
WIGGLE = [3.0, -3.0, 2.0, -1.0, 0.0]     # extra degrees on time tags during the pop (measured +-3 deg)
CAP_POP = [1.08]                         # captions: 1 frame at 108 %, then 100 % (measured)
SNAP = [1.0, 1.05, 1.10, 1.15, 1.17]     # snap zoom scale per frame (measured +5,+5,+5,+2 %)
FLASH = [1 / 3, 2 / 3, 1.0, 2 / 3, 1 / 3]  # flash pulse envelope (3 frames up, 3 down)


def pop_scale(k, curve=POP):
    return curve[k] if 0 <= k < len(curve) else 1.0


# --------------------------------------------------------------------------- drawing helpers
def text_layer(txt, fnt, fill, stroke=7, stroke_fill=INK, shadow=(0, 6), shadow_a=0.38, tracking=0):
    """Outlined text with a soft drop shadow on its own tight RGBA layer."""
    pad = stroke + 16
    if tracking:
        widths = [fnt.getlength(ch) + tracking for ch in txt]
        tw = int(sum(widths) - tracking)
    else:
        tw = int(fnt.getlength(txt))
    asc, desc = fnt.getmetrics()
    L = Image.new('RGBA', (tw + 2 * pad, asc + desc + 2 * pad), (0, 0, 0, 0))
    S = Image.new('RGBA', L.size, (0, 0, 0, 0))
    d, ds = ImageDraw.Draw(L), ImageDraw.Draw(S)

    def put(dr, x, y, **kw):
        if tracking:
            for ch, w_ in zip(txt, widths):
                dr.text((x, y), ch, font=fnt, **kw)
                x += w_
        else:
            dr.text((x, y), txt, font=fnt, **kw)
    if shadow_a:
        put(ds, pad + shadow[0], pad + shadow[1], fill=(0, 0, 0, int(255 * shadow_a)), stroke_width=stroke,
            stroke_fill=(0, 0, 0, int(255 * shadow_a)))
        S = S.filter(ImageFilter.GaussianBlur(2))
    put(d, pad, pad, fill=fill + (255,) if len(fill) == 3 else fill, stroke_width=stroke, stroke_fill=stroke_fill)
    S.alpha_composite(L)
    return S


def star_pts(cx, cy, r_out, r_in, n=5, rot=-90):
    pts = []
    for i in range(2 * n):
        r = r_out if i % 2 == 0 else r_in
        a = math.radians(rot + i * 180 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def sparkle(d, cx, cy, r, fill=WHITE, ink=INK, width=5):
    """Four-point sparkle (name-sticker corner)."""
    pts = star_pts(cx, cy, r, r * 0.28, n=4, rot=-90)
    d.polygon(pts, fill=fill, outline=ink, width=width)


def swoosh(d, x0, x1, y, thick=24, ink=INK, fill=WHITE):
    """White tapered underline swoosh with an ink edge (rises a little to the right)."""
    top, bot = [], []
    N = 40
    for i in range(N + 1):
        t = i / N
        x = x0 + (x1 - x0) * t
        yc = y - 26 * t + 18 * math.sin(math.pi * t)
        w = thick * math.sin(math.pi * (0.08 + 0.84 * t)) + 3
        top.append((x, yc - w / 2))
        bot.append((x, yc + w / 2))
    poly = top + bot[::-1]
    d.polygon(poly, fill=fill, outline=ink, width=5)


def round_box(d, box, fill, ink=INK, width=6, radius_frac=0.4):
    x0, y0, x1, y1 = box
    d.rounded_rectangle(box, radius=int((y1 - y0) * radius_frac), fill=fill, outline=ink, width=width)


def icon(d, kind, cx, cy, s, ink=INK):
    """Small time-tag icons, our own simple shapes. s = icon height in px."""
    h = s / 2
    if kind == 'hourglass':
        d.rectangle((cx - h * 0.7, cy - h, cx + h * 0.7, cy - h * 0.82), fill=ink)
        d.rectangle((cx - h * 0.7, cy + h * 0.82, cx + h * 0.7, cy + h), fill=ink)
        d.polygon([(cx - h * 0.55, cy - h * 0.82), (cx + h * 0.55, cy - h * 0.82), (cx, cy)], fill=COL['amber'], outline=ink, width=4)
        d.polygon([(cx - h * 0.55, cy + h * 0.82), (cx + h * 0.55, cy + h * 0.82), (cx, cy)], fill=(255, 238, 200), outline=ink, width=4)
    elif kind == 'sun':
        for i in range(8):
            a = math.radians(i * 45)
            d.line((cx + h * 0.62 * math.cos(a), cy + h * 0.62 * math.sin(a), cx + h * math.cos(a), cy + h * math.sin(a)), fill=ink, width=7)
        d.ellipse((cx - h * 0.5, cy - h * 0.5, cx + h * 0.5, cy + h * 0.5), fill=COL['gold'], outline=ink, width=5)
    elif kind == 'moon':
        d.ellipse((cx - h, cy - h, cx + h, cy + h), fill=(255, 238, 190), outline=ink, width=5)
        d.ellipse((cx - h * 0.35, cy - h * 1.05, cx + h * 1.25, cy + h * 0.55), fill=(0, 0, 0, 0))
    elif kind == 'candle':
        d.rounded_rectangle((cx - h * 0.35, cy - h * 0.2, cx + h * 0.35, cy + h), radius=6, fill=(255, 245, 225), outline=ink, width=5)
        d.ellipse((cx - h * 0.22, cy - h * 0.95, cx + h * 0.22, cy - h * 0.3), fill=COL['amber'], outline=ink, width=4)
    else:  # star
        d.polygon(star_pts(cx, cy, h, h * 0.45), fill=COL['gold'], outline=ink, width=5)


# --------------------------------------------------------------------------- sticker sprites
def sprite_name(ev):
    """Name sticker: character-colour display caps 120-160 px high (default 140), 8 px ink outline,
    soft shadow, white swoosh underline, a four-point sparkle at the top-left. Rotated -3 deg."""
    col = hexc(ev.get('color', 'teal'))
    f = font_for_cap('display', ev.get('cap', 140))
    T = text_layer(ev['text'].upper(), f, col, stroke=8)
    w, h = T.size
    base = 24 + f.getmetrics()[0]          # caps baseline inside the text layer (pad 24 + ascent)
    L = Image.new('RGBA', (w + 120, max(h, base + 70)), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    swoosh(d, 80, w + 30, base + 40, thick=34)
    L.alpha_composite(T, (60, 0))
    sparkle(d, 58, 46, 46)
    return L.rotate(ev.get('rot', -3), resample=Image.BICUBIC, expand=True)


def sprite_bubble(ev, anchor):
    """Speech bubble: white rounded box (radius 40 % of its height), 6 px ink, a tail to the speaker,
    2-4 words in black caps (cap height ~80 px), 60-70 % of the frame width. Drawn on a full frame
    because the tail points at a spot in the frame."""
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    maxw = int(W * ev.get('width', 0.66))
    cap = ev.get('cap', 80)
    words = ev['text'].upper().split()
    while True:
        f = font_for_cap('bubble', cap)
        lines, cur = [], ''
        for wd in words:
            t = (cur + ' ' + wd).strip()
            if f.getlength(t) <= maxw - 90 or not cur:
                cur = t
            else:
                lines.append(cur)
                cur = wd
        lines.append(cur)
        if len(lines) <= 2 and all(f.getlength(l) <= maxw - 90 for l in lines) or cap <= 50:
            break
        cap -= 6
    lh = int(cap * 1.45)
    bw = max(int(max(f.getlength(l) for l in lines) + 110), int(W * 0.6))
    bh = lh * len(lines) + 70
    cx, cy = anchor
    box = (cx - bw // 2, cy - bh // 2, cx + bw // 2, cy + bh // 2)
    tx, ty = [int(v * s) for v, s in zip(ev.get('tail', (ev.get('x', 0.5) - 0.12, ev.get('y', 0.22) + 0.14)), (W, H))]
    bx = min(max(tx, box[0] + 90), box[2] - 90)
    # tail (outlined), box (outlined), then white inner fills so the tail joins the box cleanly
    d.polygon([(bx - 40, cy), (bx + 40, cy), (tx, ty)], fill=WHITE, outline=INK, width=6)
    round_box(d, box, WHITE, width=6)
    d.rounded_rectangle((box[0] + 6, box[1] + 6, box[2] - 6, box[3] - 6), radius=int(bh * 0.4) - 6, fill=WHITE)
    sgn = 1 if ty > cy else -1
    d.polygon([(bx - 31, cy), (bx + 31, cy), (tx + (bx - tx) * 0.06, ty - sgn * 16)], fill=WHITE)
    for i, l in enumerate(lines):
        y = box[1] + 35 + i * lh + (lh - cap) // 2 - int(cap * 0.32)
        d.text((cx - f.getlength(l) / 2, y), l, font=f, fill=INK)
    return L


def sprite_tag(ev):
    """Day/time tag: amber display caps (cap ~70 px) with a 7 px ink outline and a small icon,
    rotated -5 deg (measured), top-left."""
    f = font_for_cap('display', ev.get('cap', 70))
    T = text_layer(ev['text'].upper(), f, hexc(ev.get('color', 'amber')), stroke=7)
    s = int(ev.get('cap', 70) * 1.15)
    L = Image.new('RGBA', (T.size[0] + s + 24, max(T.size[1], s + 30)), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    icon(d, ev.get('icon', 'hourglass'), s // 2 + 12, L.size[1] // 2, s)
    L.alpha_composite(T, (s + 12, (L.size[1] - T.size[1]) // 2))
    return L.rotate(ev.get('rot', -5), resample=Image.BICUBIC, expand=True)


def sprite_badge(kind, size=1.0):
    """'?' and '!' badges, a sweat drop, an anger mark: our own simple comic marks."""
    r = int(56 * size)
    L = Image.new('RGBA', (2 * r + 30, 2 * r + 40), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    c = (L.size[0] // 2, L.size[1] // 2)
    if kind in ('question', 'exclaim'):
        fill = WHITE if kind == 'question' else COL['gold']
        d.ellipse((c[0] - r + 3, c[1] - r + 9, c[0] + r + 3, c[1] + r + 9), fill=(0, 0, 0, 90))
        d.ellipse((c[0] - r, c[1] - r, c[0] + r, c[1] + r), fill=fill, outline=INK, width=6)
        f = font_for_cap('caption', r * 1.05)
        ch = '?' if kind == 'question' else '!'
        bb = d.textbbox((0, 0), ch, font=f)
        d.text((c[0] - (bb[0] + bb[2]) / 2, c[1] - (bb[1] + bb[3]) / 2), ch, font=f, fill=INK)
    elif kind == 'sweat':
        pts = []
        for i in range(61):  # teardrop: x = sin t * sin(t/2), y = cos t (point at the top)
            a = math.pi * 2 * i / 60
            pts.append((c[0] + 0.78 * r * math.sin(a) * math.sin(a / 2), c[1] - 1.1 * r * math.cos(a)))
        d.polygon(pts, fill=COL['sweat'], outline=INK, width=6)
        d.ellipse((c[0] - r * 0.28, c[1] + r * 0.05, c[0] - r * 0.05, c[1] + r * 0.45), fill=WHITE)
    elif kind == 'anger':
        for sx, sy, a0 in ((1, 1, 180), (-1, 1, 270), (-1, -1, 0), (1, -1, 90)):
            ox, oy, rr = c[0] + sx * r * 0.8, c[1] + sy * r * 0.8, r * 0.62   # arcs bowing in to the centre
            d.arc((ox - rr, oy - rr, ox + rr, oy + rr), a0 + 8, a0 + 82, fill=INK, width=18)
            d.arc((ox - rr, oy - rr, ox + rr, oy + rr), a0 + 12, a0 + 78, fill=COL['red'], width=9)
    return L


def draw_stars(img, cx, cy, t, size=1.0, n=5, period=1.0):
    """Dizzy stars: n yellow five-point stars orbiting an ellipse over a knocked-down head (measured:
    five stars, orbiting for ~1.5 s). One lap per `period` seconds (our estimate)."""
    L = Image.new('RGBA', img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    rx, ry = 130 * size, 42 * size
    st = []
    for i in range(n):
        a = 2 * math.pi * (t / period + i / n)
        depth = math.sin(a)
        st.append((depth, cx + rx * math.cos(a), cy + ry * depth, (26 + 8 * depth) * size))
    for depth, x, y, r in sorted(st):
        d.polygon(star_pts(x, y, r, r * 0.45, rot=-90 + 40 * math.sin(t * 6)), fill=COL['gold'], outline=INK, width=5)
    img.alpha_composite(L)


# --------------------------------------------------------------------------- captions (reference)
def parse_caption(text):
    """'HE WAS {FIRST}' -> [(word, colour)]. {gold} [red] <magic>; words inside "quotes" are gold."""
    out, quote, mark = [], False, None
    for tok in text.split():
        starts = tok.startswith('"')
        ends = tok.rstrip(',.!?').endswith('"') and (not starts or len(tok.strip(',.!?')) > 1)
        if starts:
            quote = True
        core = tok.strip('"')
        for a, b, c in (('{', '}', 'gold'), ('[', ']', 'red'), ('<', '>', 'magic')):
            if core.startswith(a):
                mark = c
        col = COL[mark] if mark else (COL['gold'] if quote else WHITE)
        for a, b, c in (('{', '}', 'gold'), ('[', ']', 'red'), ('<', '>', 'magic')):
            if core.rstrip(',.!?').endswith(b):
                mark = None
        out.append((''.join(ch for ch in tok if ch not in '{}[]<>').upper(), col))
        if ends:
            quote = False
    return out


def draw_caption(img, text, k=99, closeup=False, cap=78):
    """Captions for this style: heavy rounded caps, ~110 px (cap height 70-95, default 78), white,
    7 px ink outline, 0/6 px 40 % shadow, centred, baseline y 1290 (67 %), or 1515 (79 %) on face
    close-ups; max line width 900; 1 frame at 108 % then 100 %. k = frames since the caption started."""
    segs = parse_caption(text)
    f = font_for_cap('caption', cap)
    layers = [text_layer(w + ' ', f, c, stroke=7, shadow_a=0.40) for w, c in segs]
    lines, cur, cw = [], [], 0
    for l in layers:
        if cur and cw + l.size[0] - 46 > 900 + 46:
            lines.append(cur)
            cur, cw = [], 0
        cur.append(l)
        cw += l.size[0] - 46
    lines.append(cur)
    lh = int(cap * 1.32)
    block = Image.new('RGBA', (W, lh * len(lines) + 80), (0, 0, 0, 0))
    for i, ln in enumerate(lines):
        w = sum(l.size[0] - 46 for l in ln) + 46
        x = (W - w) // 2
        for l in ln:
            block.alpha_composite(l, (x, i * lh))
            x += l.size[0] - 46
    s = pop_scale(k, CAP_POP)
    base = 1515 if closeup else 1290
    asc = f.getmetrics()[0]
    y_top = base - asc - 23 - lh * (len(lines) - 1)
    if s != 1.0:
        bb = block.getbbox() or (0, 0, W, block.size[1])
        crop = block.crop(bb)
        crop = crop.resize((int(crop.size[0] * s), int(crop.size[1] * s)), Image.BICUBIC)
        cx, cy = (bb[0] + bb[2]) / 2, y_top + (bb[1] + bb[3]) / 2
        img.alpha_composite(crop, (int(cx - crop.size[0] / 2), int(cy - crop.size[1] / 2)))
    else:
        img.alpha_composite(block, (0, int(y_top)))
    return img


# --------------------------------------------------------------------------- question card
def card_layer(ev):
    """Closing question card (last 4-8 s): small tracked light-grey caps premise at the top, a red
    rounded PART pill, a 2-line white heavy-caps question with the key word coloured, and on vote
    episodes a red A pill and a blue B pill. Block layout (y 30-66 %) is our choice."""
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    y = int(H * ev.get('y', 0.30))
    if ev.get('premise'):
        fp = font('bubble', 40)
        words, lines, cur = ev['premise'].upper().split(), [], ''
        for wd in words:
            t = (cur + ' ' + wd).strip()
            if fp.getlength(t) + 4 * len(t) <= 880 or not cur:
                cur = t
            else:
                lines.append(cur)
                cur = wd
        lines.append(cur)
        for ln in lines:
            T = text_layer(ln, fp, COL['grey'], stroke=4, shadow_a=0.3, tracking=4)
            L.alpha_composite(T, ((W - T.size[0]) // 2, y))
            y += 58
        y += 30
    if ev.get('part'):
        fpp = font_for_cap('display', 52)
        tw = fpp.getlength(ev['part'].upper())
        box = (int((W - tw) / 2 - 48), y, int((W + tw) / 2 + 48), y + 100)
        round_box(d, box, COL['red'], width=6, radius_frac=0.5)
        T = text_layer(ev['part'].upper(), fpp, WHITE, stroke=5, shadow_a=0)
        L.alpha_composite(T, ((W - T.size[0]) // 2, y + 50 - T.size[1] // 2 + 4))
        y += 140
    kw = (ev.get('keyword') or '').upper()
    for ln in ev.get('question', []):
        segs = [(wd, hexc(ev.get('kw_color', 'gold')) if kw and wd.strip('?!.,') == kw else WHITE) for wd in ln.upper().split()]
        fq = font_for_cap('caption', ev.get('cap', 82))
        layers = [text_layer(w_ + ' ', fq, c, stroke=7, shadow_a=0.4) for w_, c in segs]
        while sum(l.size[0] - 46 for l in layers) > 960 and fq.size > 40:
            fq = font('caption', fq.size - 6)
            layers = [text_layer(w_ + ' ', fq, c, stroke=7, shadow_a=0.4) for w_, c in segs]
        x = (W - (sum(l.size[0] - 46 for l in layers) + 46)) // 2
        for l in layers:
            L.alpha_composite(l, (x, y))
            x += l.size[0] - 46
        y += int(fq.size * 1.12)
    if ev.get('vote'):
        y += 40
        fv = font_for_cap('bubble', 44)
        for i, (txt, col) in enumerate(zip(ev['vote'], ('red', 'blue'))):
            tw = fv.getlength(txt.upper())
            box = (int((W - tw) / 2 - 44), y, int((W + tw) / 2 + 44), y + 92)
            round_box(d, box, COL[col], width=6, radius_frac=0.5)
            T = text_layer(txt.upper(), fv, WHITE, stroke=4, shadow_a=0)
            L.alpha_composite(T, ((W - T.size[0]) // 2, y + 46 - T.size[1] // 2 + 3))
            y += 118
    return L


def vignette_mask(strength=0.28):
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / math.sqrt(2)
    return (1 - strength * np.clip((r - 0.35) / 0.65, 0, 1) ** 1.6)[..., None]


# --------------------------------------------------------------------------- the post engine
class Post:
    GEO = ('snap_zoom', 'reframe', 'ff_jitter')
    STICK = ('gag', 'bubble', 'time_tag', 'name', 'caption')

    def __init__(self, plan):
        if isinstance(plan, str):
            with open(plan) as fh:
                plan = json.load(fh)
        self.fps = plan.get('fps', FPS)
        self.ev = []
        for e in plan['events']:
            e = dict(e)
            if 'f' in e and 'f0' not in e:
                e['f0'] = e['f']
                e['f1'] = e['f'] + (e.get('frames', 3) if e['type'] == 'dip_black' else 6)
            self.ev.append(e)
        self._cache = {}

    def _vmask(self, s):
        if ('vig', s) not in self._cache:
            self._cache[('vig', s)] = vignette_mask(s)
        return self._cache[('vig', s)]

    def active(self, n, types):
        return [e for e in self.ev if e['type'] in types and e['f0'] <= n < e['f1']]

    # ---- frame effects (numpy, float 0-255)
    def _geo(self, img, n):
        for e in self.active(n, self.GEO):
            k = n - e['f0']
            if e['type'] in ('snap_zoom', 'reframe'):
                s = SNAP[min(k, len(SNAP) - 1)] if e['type'] == 'snap_zoom' else e.get('scale', 1.10)
                cw, ch = W / s, H / s
                cx, cy = e.get('cx', 0.5) * W, e.get('cy', 0.5) * H
                x0 = min(max(cx - cw / 2, 0), W - cw)
                y0 = min(max(cy - ch / 2, 0), H - ch)
                img = img.transform((W, H), Image.EXTENT, (x0, y0, x0 + cw, y0 + ch), Image.BICUBIC)
            else:  # ff_jitter: measured +-27 px (crop sin(n*1.9), sin(n*2.3)), roll blips +-0.9 deg
                px = e.get('px', 27)
                dx, dy = px * math.sin(n * 1.9), px * math.sin(n * 2.3)
                rot = e.get('roll', 0.9) * math.sin(n * 3.7)
                img = img.rotate(rot, resample=Image.BICUBIC, translate=(dx, dy))
                m = 1.06  # hide the moved edges (their crop 1040x1850 ~ 1.04-1.05x)
                cw, ch = W / m, H / m
                img = img.transform((W, H), Image.EXTENT, ((W - cw) / 2, (H - ch) / 2, (W + cw) / 2, (H + ch) / 2), Image.BICUBIC)
        return img

    def _colour(self, a, n):
        for e in self.active(n, ('bw', 'sepia', 'dim', 'flash', 'ff_jitter')):
            k = n - e['f0']
            if e['type'] == 'bw':
                g = (a @ np.array([0.299, 0.587, 0.114], np.float32))[..., None]
                a = g + (a - g) * 0.08
            elif e['type'] == 'sepia':
                M = np.array([[.393, .769, .189], [.349, .686, .168], [.272, .534, .131]], np.float32)
                a = np.clip(a @ M.T, 0, 255)
                a = a * self._vmask(0.45)
            elif e['type'] == 'dim':
                p = min(1.0, k / max(1, e.get('frames', 33)))
                p = 0.5 - 0.5 * math.cos(math.pi * p)
                a = a * (1 - e.get('amount', 0.3) * p)
            elif e['type'] == 'flash':
                if k < len(FLASH):
                    a = a + e.get('luma', 36) * FLASH[k]
            elif e['type'] == 'ff_jitter':
                a = a + e.get('pulse', 10) * math.sin(2 * math.pi * e.get('pulse_hz', 2.9) * k / self.fps)
        return np.clip(a, 0, 255)

    def _sepia_overlay(self, img, n):
        for e in self.active(n, ('sepia',)):
            k = n - e['f0']
            key = ('sepia_border',)
            if key not in self._cache:
                B = Image.new('RGBA', (W, H), (244, 236, 220, 255))
                ImageDraw.Draw(B).rounded_rectangle((24, 24, W - 24, H - 24), radius=40, fill=(0, 0, 0, 0))
                self._cache[key] = B
            rnd = random.Random(e.get('seed', 1))
            D = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            d = ImageDraw.Draw(D)
            for i in range(46):
                x = (rnd.random() * W + 9 * k * (rnd.random() - 0.5)) % W
                y = (rnd.random() * H - 6 * k * (0.3 + rnd.random())) % H
                r = 1.5 + 3.5 * rnd.random() ** 2
                d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 245, 225, int(70 + 120 * rnd.random())))
            img.alpha_composite(D.filter(ImageFilter.GaussianBlur(0.8)))
            img.alpha_composite(self._cache[key])
        return img

    def _card_bg(self, img, n):
        for e in self.active(n, ('card',)):
            k = n - e['f0']
            p = min(1.0, (k + 1) / 8.0)       # measured: background dims 35 % over 8 frames, soft blur
            img = img.filter(ImageFilter.GaussianBlur(10 * p))
            v = self._vmask(0.28)          # the only vignette in this style: under the question card
            a = np.asarray(img, np.float32) * (1 - 0.35 * p) * (1 - (1 - v) * p)
            img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
        return img

    # ---- stickers
    def _sprite(self, e):
        key = id(e)
        if key not in self._cache:
            x, y = int(e.get('x', 0.5) * W), int(e.get('y', 0.2) * H)
            t = e['type']
            if t == 'name':
                spr, anchor, mode = sprite_name(e), (x, y), 'center'
            elif t == 'time_tag':
                spr, anchor, mode = sprite_tag(e), (int(e.get('x', 0.07) * W), int(e.get('y', 0.17) * H)), 'left'
            elif t == 'bubble':
                spr, anchor, mode = sprite_bubble(e, (x, int(e.get('y', 0.22) * H))), (x, int(e.get('y', 0.22) * H)), 'full'
            elif t == 'card':
                spr, anchor, mode = card_layer(e), (W // 2, int(H * 0.45)), 'full'
            else:
                spr, anchor, mode = sprite_badge(e.get('kind', 'question'), e.get('size', 1.0)), (x, y), 'center'
            self._cache[key] = (spr, anchor, mode)
        return self._cache[key]

    def _paste(self, img, spr, anchor, mode, s=1.0, rot=0.0):
        if mode == 'full':
            if s == 1.0 and rot == 0.0:
                img.alpha_composite(spr)
                return img
            bb = spr.getbbox()
            if not bb or s <= 0.01:
                return img
            spr = spr.crop(bb)
            anchor = ((bb[0] + bb[2]) // 2, (bb[1] + bb[3]) // 2)
            mode = 'center'
        if s <= 0.01:
            return img
        if s != 1.0:
            spr = spr.resize((max(1, int(spr.size[0] * s)), max(1, int(spr.size[1] * s))), Image.BICUBIC)
        if rot:
            spr = spr.rotate(rot, resample=Image.BICUBIC, expand=True)
        if mode == 'center':
            pos = (int(anchor[0] - spr.size[0] / 2), int(anchor[1] - spr.size[1] / 2))
        else:  # 'left': anchor is the left edge, vertical centre
            pos = (int(anchor[0]), int(anchor[1] - spr.size[1] / 2))
        img.alpha_composite(spr, pos)
        return img

    def _stickers(self, img, n):
        for e in self.active(n, self.STICK):
            k = n - e['f0']
            t = e['type']
            if t == 'caption':
                draw_caption(img, e['text'], k, e.get('closeup', False), e.get('cap', 78))
            elif t == 'gag' and e.get('kind', 'stars') == 'stars':
                draw_stars(img, e.get('x', 0.5) * W, e.get('y', 0.3) * H, k / self.fps, e.get('size', 1.0))
            elif t == 'gag' and e.get('points'):
                spr, _, mode = self._sprite(e)
                for i, (px_, py_) in enumerate(e['points']):
                    self._paste(img, spr, (px_ * W, py_ * H), 'center', pop_scale(k - 2 * i))
            else:
                spr, anchor, mode = self._sprite(e)
                rot = WIGGLE[k] if t == 'time_tag' and k < len(WIGGLE) else 0.0
                self._paste(img, spr, anchor, mode, pop_scale(k), rot)
        for e in self.active(n, ('card',)):
            k = n - e['f0'] - 4  # the card pops 4 frames after the dim starts (our choice)
            if k >= 0:
                spr, anchor, mode = self._sprite(e)
                self._paste(img, spr, anchor, mode, pop_scale(k))
        return img

    def apply(self, img, n):
        """One frame: PIL RGB 1080x1920 in, PIL RGB out. Order: geometry, colour, card background,
        sepia border and dust, stickers and captions, card, dip to black."""
        if img.size != (W, H):
            img = img.resize((W, H), Image.BICUBIC)
        img = self._geo(img.convert('RGB'), n)
        a = self._colour(np.asarray(img, np.float32), n)
        img = Image.fromarray(a.astype(np.uint8))
        img = self._card_bg(img, n).convert('RGBA')
        img = self._sepia_overlay(img, n)
        img = self._stickers(img, n).convert('RGB')
        if self.active(n, ('dip_black',)):
            img = Image.new('RGB', (W, H), (0, 0, 0))
        return img

    # ---- sound cues and plain-ffmpeg chain
    def cues(self):
        out = []
        for e in self.ev:
            s = e.get('sfx')
            if s == 'none':
                continue
            if e['type'] in ('name', 'bubble', 'time_tag', 'gag') or s == 'pop':
                out.append((round(e['f0'] / self.fps, 3), 'pop', e['type']))
            if s == 'thump' or e['type'] == 'card':
                out.append((round(e['f0'] / self.fps, 3), 'thump', e['type']))
        return sorted(out)

    def ffmpeg_chain(self):
        """-vf chain for the plain frame effects with timeline ranges (no stickers, no sepia dust/border,
        no card). For builders who post in ffmpeg only; the Python path is the reference."""
        f = []
        for e in self.ev:
            a, b = e['f0'], e['f1'] - 1
            en = "enable='between(n,%d,%d)'" % (a, b)
            if e['type'] == 'bw':
                f.append('hue=s=0.08:' + en)
            elif e['type'] == 'sepia':
                f.append('colorchannelmixer=.393:.769:.189:0:.349:.686:.168:0:.272:.534:.131:' + en)
                f.append('vignette=angle=PI/4:' + en)
            elif e['type'] == 'flash':
                L = e.get('luma', 36) / 255.0
                f.append("eq=brightness='%.4f*max(0,1-abs(n-%d)/3)':eval=frame:%s" % (L, a + 2, en))
            elif e['type'] == 'dim':
                fr = e.get('frames', 33)
                f.append("eq=brightness='-%.4f*min(1,(n-%d)/%d)':eval=frame:%s" % (e.get('amount', 0.3) * 0.4, a, fr, en))
            elif e['type'] == 'dip_black':
                f.append("drawbox=x=0:y=0:w=iw:h=ih:color=black:t=fill:" + en)
        zs = [e for e in self.ev if e['type'] == 'snap_zoom']
        if zs:
            z = '1'
            for e in zs:
                a, b = e['f0'], e['f1'] - 1
                z = "if(between(in,%d,%d),min(1.17,1+0.05*(in-%d)-0.03*max(0,in-%d-3)),%s)" % (a, b, a, a, z)
            f.insert(0, "zoompan=z='%s':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d=1:s=%dx%d:fps=%d" % (z, W, H, self.fps))
        return ','.join(f) or 'null'


# --------------------------------------------------------------------------- I/O
def run_video(plan, src, dst, crf=17):
    P = Post(plan)
    dec = subprocess.Popen(['ffmpeg', '-v', 'error', '-i', src, '-f', 'rawvideo', '-pix_fmt', 'rgb24',
                            '-vf', 'scale=%d:%d' % (W, H), '-'], stdout=subprocess.PIPE)
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', '%dx%d' % (W, H),
                            '-r', str(P.fps), '-i', '-', '-i', src, '-map', '0:v', '-map', '1:a?', '-c:a', 'copy',
                            '-c:v', 'libx264', '-crf', str(crf), '-preset', 'medium', '-pix_fmt', 'yuv420p', dst],
                           stdin=subprocess.PIPE)
    n, fs = 0, W * H * 3
    while True:
        buf = dec.stdout.read(fs)
        if len(buf) < fs:
            break
        img = Image.frombuffer('RGB', (W, H), buf, 'raw', 'RGB', 0, 1)
        enc.stdin.write(P.apply(img, n).tobytes())
        n += 1
    enc.stdin.close()
    enc.wait()
    dec.wait()
    return n


def run_frames(plan, src_dir, dst_dir):
    P = Post(plan)
    os.makedirs(dst_dir, exist_ok=True)
    names = sorted(x for x in os.listdir(src_dir) if x.lower().endswith(('.png', '.jpg')))
    for n, nm in enumerate(names):
        P.apply(Image.open(os.path.join(src_dir, nm)), n).save(os.path.join(dst_dir, '%05d.png' % n))
    return len(names)


def check(paths):
    """Luma mean/p5/p95 and HSV saturation of stills vs the style targets (95-110 / <15 / 220-232 / 0.40-0.48)."""
    rows = []
    for p in paths:
        a = np.asarray(Image.open(p).convert('RGB'), np.float32)
        y = a @ np.array([0.299, 0.587, 0.114], np.float32)
        mx, mn = a.max(2), a.min(2)
        sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1), 0)
        r = dict(file=os.path.basename(p), luma=round(float(y.mean()), 1), p5=round(float(np.percentile(y, 5)), 1),
                 p95=round(float(np.percentile(y, 95)), 1), sat=round(float(sat.mean()), 3))
        r['ok'] = 95 <= r['luma'] <= 110 and r['p5'] <= 15 and 220 <= r['p95'] <= 232 and 0.40 <= r['sat'] <= 0.48
        rows.append(r)
    return rows


def backdrop(seed=2):
    """Our own neutral test backdrop for previews: a simple stone corridor of flat shapes."""
    rnd = random.Random(seed)
    img = Image.new('RGB', (W, H), (110, 130, 135))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 300), fill=(168, 183, 195))
    for i in range(6):
        x = 40 + i * 180
        d.rectangle((x, 380, x + 120, 980), fill=(47, 67, 86), outline=(8, 8, 15), width=4)
        d.rectangle((x + 15, 420, x + 105, 600), fill=(237, 229, 209))
    d.rectangle((0, 1000, W, H), fill=(142, 96, 58))
    for i in range(14):
        for j in range(7):
            if (i + j) % 2:
                d.rectangle((j * 160, 1000 + i * 70, j * 160 + 160, 1070 + i * 70), fill=(120, 80, 48))
    d.ellipse((380, 600, 700, 920), fill=(8, 8, 15))
    d.rounded_rectangle((400, 700, 680, 1000), radius=40, fill=(226, 180, 140))
    d.rectangle((330, 1000, 750, 1500), fill=(8, 8, 15))
    for _ in range(60):
        x, y = rnd.randrange(W), rnd.randrange(1000, H)
        d.ellipse((x, y, x + 6, y + 3), fill=(100, 70, 40))
    return img


def preview(outdir):
    os.makedirs(outdir, exist_ok=True)
    bg = backdrop()
    # frame A: a character's first appearance (name sticker) after a time skip (tag), with a caption
    A = Post({'fps': 30, 'events': [
        {'type': 'name', 'f0': 0, 'f1': 60, 'text': 'Wren', 'color': '#3FD0C9', 'x': 0.5, 'y': 0.13},
        {'type': 'time_tag', 'f0': 0, 'f1': 60, 'text': 'Day three', 'icon': 'hourglass', 'x': 0.06, 'y': 0.25},
        {'type': 'caption', 'f0': 0, 'f1': 60, 'text': 'SHE RANG THE {GOLD} BELL'}]}).apply(bg.copy(), 20)
    # frame B: a quoted line (bubble with a tail to the speaker), icon gags, a close-up caption
    B = Post({'fps': 30, 'events': [
        {'type': 'bubble', 'f0': 0, 'f1': 60, 'text': 'Not the bell again!', 'x': 0.5, 'y': 0.17, 'tail': [0.47, 0.33]},
        {'type': 'gag', 'f0': 0, 'f1': 60, 'kind': 'stars', 'x': 0.5, 'y': 0.345, 'size': 1.1},
        {'type': 'gag', 'f0': 0, 'f1': 60, 'kind': 'question', 'points': [[0.13, 0.47], [0.87, 0.49]]},
        {'type': 'gag', 'f0': 0, 'f1': 60, 'kind': 'sweat', 'x': 0.69, 'y': 0.39},
        {'type': 'gag', 'f0': 0, 'f1': 60, 'kind': 'anger', 'x': 0.31, 'y': 0.40},
        {'type': 'caption', 'f0': 0, 'f1': 60, 'text': '"NO!"', 'closeup': True}]}).apply(bg.copy(), 20)
    two = Image.new('RGB', (W + 20, H // 2), (20, 20, 26))
    two.paste(A.resize((W // 2, H // 2)), (0, 0))
    two.paste(B.resize((W // 2, H // 2)), (W // 2 + 20, 0))
    two.save(os.path.join(outdir, 'preview_stickers.png'))
    A.save(os.path.join(outdir, 'preview_frameA.png'))
    cardp = {'fps': 30, 'events': [{'type': 'card', 'f0': 0, 'f1': 180, 'premise': 'In this town the bell rings once for every lie',
                                    'part': 'Part 1', 'question': ['WHO RANG THE', 'BELL AT MIDNIGHT?'], 'keyword': 'MIDNIGHT?',
                                    'vote': ['A  The baker', 'B  The squire']}]}
    Post(cardp).apply(bg.copy(), 30).save(os.path.join(outdir, 'preview_card.png'))
    # pop strip: name sticker frames 0-4 + time tag wiggle
    strip = Image.new('RGB', (W, 700), (28, 32, 48))
    d = ImageDraw.Draw(strip)
    for k in range(5):
        P2 = Post({'events': [{'type': 'name', 'f0': 0, 'f1': 9, 'text': 'Wren', 'color': '#FF5A6E', 'x': 0.5, 'y': 0.5}]})
        fr = Image.new('RGBA', (W, H), (60, 70, 90, 255))
        fr = P2._stickers(fr, k).convert('RGB').crop((140, 760, 940, 1160)).resize((200, 100))
        strip.paste(fr, (12 + k * 212, 40))
        d.text((12 + k * 212, 150), 'frame %d  %.0f%%' % (k, 100 * pop_scale(k)), fill=(230, 230, 230), font=font('bubble', 24))
        P3 = Post({'events': [{'type': 'time_tag', 'f0': 0, 'f1': 9, 'text': 'Six hours', 'icon': 'sun', 'x': 0.2, 'y': 0.5}]})
        fr = Image.new('RGBA', (W, H), (60, 70, 90, 255))
        fr = P3._stickers(fr, k).convert('RGB').crop((150, 820, 950, 1100)).resize((200, 70))
        strip.paste(fr, (12 + k * 212, 260))
        d.text((12 + k * 212, 340), 'rot %+.0f deg' % (-5 + WIGGLE[k]), fill=(230, 230, 230), font=font('bubble', 24))
    for k, (txt, ic) in enumerate((('Night one', 'moon'), ('Candle out', 'candle'), ('Spring', 'star'))):
        P4 = Post({'events': [{'type': 'time_tag', 'f0': 0, 'f1': 9, 'text': txt, 'icon': ic, 'x': 0.1, 'y': 0.5}]})
        fr = Image.new('RGBA', (W, H), (60, 70, 90, 255))
        fr = P4._stickers(fr, 6).convert('RGB').crop((60, 840, 1020, 1080)).resize((330, 82))
        strip.paste(fr, (12 + k * 350, 420))
    for k, kind in enumerate(('question', 'exclaim', 'sweat', 'anger')):
        b = sprite_badge(kind)
        strip.paste(b, (60 + k * 250, 560), b)
    strip.save(os.path.join(outdir, 'preview_pop.png'))
    # effects strip
    fx = [('normal', None), ('black and white', {'type': 'bw', 'f0': 0, 'f1': 9}),
          ('sepia flashback', {'type': 'sepia', 'f0': 0, 'f1': 9}), ('flash peak', {'type': 'flash', 'f': 0}),
          ('light dim end', {'type': 'dim', 'f0': 0, 'f1': 99, 'frames': 33}),
          ('snap zoom end', {'type': 'snap_zoom', 'f0': 0, 'f1': 9})]
    sheet = Image.new('RGB', (3 * 360, 2 * 700), (20, 20, 26))
    d = ImageDraw.Draw(sheet)
    for i, (lab, ev) in enumerate(fx):
        n = {'flash peak': 2, 'light dim end': 40, 'snap zoom end': 5}.get(lab, 3)
        P5 = Post({'events': [ev] if ev else []})
        fr = P5.apply(bg.copy(), n).resize((360, 640))
        sheet.paste(fr, ((i % 3) * 360, (i // 3) * 700))
        d.text(((i % 3) * 360 + 12, (i // 3) * 700 + 648), lab, fill=(235, 235, 235), font=font('bubble', 28))
    sheet.save(os.path.join(outdir, 'preview_fx.png'))
    return sorted(os.listdir(outdir))


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a:
        print(__doc__)
    elif a[0] == 'preview':
        print(preview(a[1]))
    elif a[0] == 'frames':
        print(run_frames(a[1], a[2], a[3]), 'frames')
    elif a[0] == 'run':
        print(run_video(a[1], a[2], a[3]), 'frames')
    elif a[0] == 'ffmpeg':
        print(Post(a[1]).ffmpeg_chain())
    elif a[0] == 'cues':
        for c in Post(a[1]).cues():
            print('%.3f %s %s' % c)
    elif a[0] == 'check':
        for r in check(a[1:]):
            print(r)
    else:
        print(__doc__)
