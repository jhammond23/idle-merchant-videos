# Tiny Seed: assemble the preview stills from the _pv_*.png renders (labels in Fredoka One).
import json, os, sys
ONLY = sys.argv[1].split(',') if len(sys.argv) > 1 else ['lineup', 'stages', 'faces', 'hero']
from PIL import Image, ImageDraw, ImageFont
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
FONT = '/tmp/claude-0/tv/fonts/FredokaOne-Regular.ttf'
def font(sz):
    try: return ImageFont.truetype(FONT, sz)
    except Exception: return ImageFont.load_default()
def text(d, xy, s, sz=24, anchor='ma', fill=(255, 255, 255)):
    d.text(xy, s, font=font(sz), fill=fill, anchor=anchor, stroke_width=max(2, sz // 8), stroke_fill=(17, 17, 17))
def panel(name, title=None, labels=True, sz=22):
    im = Image.open(os.path.join(D, f'_pv_{name}.png')).convert('RGB')
    d = ImageDraw.Draw(im)
    jp = os.path.join(D, f'_pv_{name}.json')
    if labels and os.path.exists(jp):
        rows = {}
        f = font(sz)
        for (t, x, y) in sorted(json.load(open(jp)), key=lambda q: q[1]):
            w = d.textlength(t, font=f) + 14
            x = min(max(x, w / 2 + 4), im.width - w / 2 - 4)
            r = 0
            while any(abs(x - ox) < (w + ow) / 2 for (ox, ow) in rows.get(r, [])):
                r += 1
            rows.setdefault(r, []).append((x, w))
            yy = min(y + 8, im.height - (sz + 8) * 3 - 6) + r * (sz + 8)
            if r:
                d.line([(x, y + 4), (x, yy)], fill=(17, 17, 17), width=2)
            text(d, (x, yy), t, sz)
    if title:
        text(d, (16, 12), title, 28, anchor='la', fill=(236, 230, 72))
    return im
def stack(rows, out):
    W = 1080; H = sum(r.height for r in rows)
    c = Image.new('RGB', (W, H))
    y = 0
    for r in rows:
        c.paste(r, (0, y)); y += r.height
    c.save(os.path.join(D, out)); print(out, c.size)
def hjoin(a, b):
    c = Image.new('RGB', (a.width + b.width, max(a.height, b.height))); c.paste(a, (0, 0)); c.paste(b, (a.width, 0)); return c
if 'lineup' in ONLY:
    stack([panel('lineup_big', 'LINEUP  (sizes in BU, 1 m = 3.3 BU)'), panel('lineup_small', 'SMALL ASSETS'), panel('mother', 'TROLL MOTHER  450 BU')], 'lineup.png')
    stack([panel('mother', 'TROLL MOTHER  450 BU, next to the 100 BU tree and the town')], 'lineup-mother.png')
if 'stages' in ONLY:
    a = panel('stage_a', 'A  the dot  0.3 BU'); b = panel('stage_b', 'B  shooting up  40 BU')
    r2 = panel('stage_cde'); d = ImageDraw.Draw(r2)
    for i, t in enumerate(('C  full giant  100 BU', 'D  + blossoms', 'E  + golden apples')):
        text(d, (180 + i * 360, 12), t, 28, fill=(236, 230, 72))
    r3 = panel('stage_poses'); d = ImageDraw.Draw(r3)
    for i, t in enumerate(('TS_TREE_HUG', 'TS_TREE_GIVE', 'TS_TREE_PROTECT')):
        text(d, (190 + i * 345, 12), t, 28, fill=(236, 230, 72))
    stack([hjoin(a, b), r2, r3], 'tree-stages.png')
if 'faces' in ONLY:
    stack([panel('faces_baby', 'BABY ROCK TROLL  16 BU', sz=26), panel('faces_mother', 'TROLL MOTHER  450 BU', sz=26)], 'troll-faces.png')
if 'hero' in ONLY:
    Image.open(os.path.join(D, '_pv_hero.png')).convert('RGB').save(os.path.join(D, 'hero.png')); print('hero.png')
