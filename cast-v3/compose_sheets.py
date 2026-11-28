# Compose sheets/<key>.png (turnaround + poses + expressions + specs) and silhouette.png from the renders in scratch/r/.
import os, json, sys
from PIL import Image, ImageDraw, ImageFont, ImageOps
B = '/tmp/claude-0/cast3/'; R = B + 'scratch/r/'
PB = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'; PR = '/usr/share/fonts/truetype/google-fonts/Poppins-Regular.ttf'
def f(sz, bold=True):
    try: return ImageFont.truetype(PB if bold else PR, sz)
    except Exception: return ImageFont.load_default()
META = json.load(open(B + 'scratch/meta.json'))      # written by meta_v3.py from the .blend
BG = (24, 22, 30); FG = (255, 255, 255); SUB = (196, 196, 208); ACC = (255, 205, 70)

def fit(im, w, h=None):
    if h is None: h = int(im.size[1] * w / im.size[0])
    return im.resize((w, h), Image.LANCZOS)

def strip_cells(path, n, labels):
    im = Image.open(path).convert('RGB'); cw = im.size[0] // n
    return [(im.crop((i * cw, 0, (i + 1) * cw, im.size[1])), labels[i]) for i in range(n)]

def sheet(key, W=2000):
    m = META[key]; parts = []
    turn = Image.open(R + key + '_turn.png').convert('RGB') if os.path.exists(R + key + '_turn.png') else None
    poses = Image.open(R + key + '_poses.png').convert('RGB') if os.path.exists(R + key + '_poses.png') else None
    faces = None
    fkey = key if os.path.exists(R + key + '_faces.png') else ('ember_grown' if key.startswith('ember') else None)
    if fkey and os.path.exists(R + fkey + '_faces.png'):
        labels = m['cells'] if fkey == key else META[fkey]['cells']
        faces = strip_cells(R + fkey + '_faces.png', len(labels), labels)
    # layout
    head_h = 320; y = 0
    blocks = []
    if turn: blocks.append(('TURNAROUND  front / 3-4 / side / back / 3-4 back', fit(turn, W)))
    if poses: blocks.append(('POSES  ' + ' / '.join(m['poses']), fit(poses, W)))
    if os.path.exists(R + key + '_variants.png'):     # phase 2 (Boss Giant): skins + per-story switches
        blocks.append((m.get('variants_label', 'VARIANTS'), fit(Image.open(R + key + '_variants.png').convert('RGB'), W)))
    if faces:
        cols = min(len(faces), 7); cw = W // cols; fh = int(faces[0][0].size[1] * cw / faces[0][0].size[0])
        rows = (len(faces) + cols - 1) // cols
        g = Image.new('RGB', (W, rows * (fh + 40)), BG); d = ImageDraw.Draw(g)
        for i, (im, lab) in enumerate(faces):
            x, yy = (i % cols) * cw, (i // cols) * (fh + 40)
            g.paste(fit(im, cw, fh), (x, yy)); d.text((x + 12, yy + fh + 4), lab.upper(), font=f(24), fill=FG)
        blocks.append(('EXPRESSIONS  rig property "face" (+ "mouth" talk set, "blink", "glow")', g))
    H = head_h + sum(b.size[1] + 56 for _, b in blocks) + 20
    o = Image.new('RGB', (W, H), BG); d = ImageDraw.Draw(o)
    d.text((40, 18), 'CAST V3  |  ' + m['role'].upper()[:90], font=f(26), fill=ACC)
    d.text((40, 52), m['name'], font=f(68), fill=FG)
    import textwrap
    lines = ['Height %.2f BU = %.2fx Hero kid = %.2f HH   |   body: %s' % (m['height_BU'], m['height_x_hero'], m['height_HH'], m['body']),
             'Face: ' + m['face_style'], 'Signature: ' + m['signature'], 'Silhouette: ' + m['silhouette']]
    yy = 150
    for ln in lines:
        for part in textwrap.wrap(ln, 150)[:2]:
            d.text((40, yy), part, font=f(21, False), fill=SUB); yy += 27
    sw = m['swatches'][:8]; n_ = len(sw)
    for i, c in enumerate(sw):
        x0 = W - 60 - (n_ - i) * 70
        d.rounded_rectangle([x0, 40, x0 + 58, 98], radius=10, fill=tuple(c), outline=(255, 255, 255), width=4 if i == 0 else 1)
    y = head_h
    for lab, im in blocks:
        d.text((40, y + 10), lab, font=f(26), fill=ACC); y += 50
        o.paste(im, (0, y)); y += im.size[1] + 6
    os.makedirs(B + 'sheets', exist_ok=True)
    o.save(B + 'sheets/%s.png' % key, optimize=True); print('sheet', key, o.size)

def silhouette():
    import numpy as np
    raw = Image.open(R + 'silhouette_raw.png').convert('L')
    order = [n for n in META['_order']]
    bbox = ImageOps.invert(raw).getbbox(); m = 30
    crop = raw.crop((max(0, bbox[0] - m), max(0, bbox[1] - m), min(raw.size[0], bbox[2] + m), min(raw.size[1], bbox[3] + m)))
    W, H = crop.size
    a = np.array(crop) < 128; cols = a.any(axis=0)
    runs = []; st = None
    for x, c in enumerate(cols):
        if c and st is None: st = x
        if not c and st is not None: runs.append([st, x]); st = None
    if st is not None: runs.append([st, W])
    merged = []
    for r in runs:
        if merged and r[0] - merged[-1][1] < 10: merged[-1][1] = r[1]
        else: merged.append(r)
    o = Image.new('RGB', (W, H + 700), (255, 255, 255)); d = ImageDraw.Draw(o)
    d.text((30, 16), 'SILHOUETTE TEST  all Cast v3 characters + Hero kid and Little sister (Cast v2), true scale, solid black', font=f(40), fill=(20, 20, 20))
    o.paste(crop.convert('RGB'), (0, 80))
    rowsum = a.sum(axis=1); feet = max(i for i in range(len(rowsum)) if rowsum[i] > 30)
    ly = 80 + feet + 14
    if len(merged) == len(order):
        last_end = -1e9
        for i, ((x0, x1), n) in enumerate(zip(merged, order)):
            lab = n.replace('Crowd ', '').replace('The ', '').replace(' (hatchling)', ' hatchling').replace(' (grown)', ' grown')
            col = (150, 150, 150) if n in ('Hero kid', 'Little sister') else (20, 20, 20)
            tw = d.textlength(lab, font=f(24)); xs = (x0 + x1) / 2 - tw / 2
            row = 1 if xs < last_end + 8 else 0
            d.text((xs, ly + row * 30), lab, font=f(24), fill=col)
            if row == 0: last_end = xs + tw
    k = 128 / crop.size[1]; th = crop.resize((int(W * k), 128), Image.LANCZOS)
    y0 = ly + 90
    d.text((30, y0), 'Thumbnail test: the whole strip scaled so the tallest figure is 128 px tall (crowd-shot size); below, the same at 2x nearest-neighbour', font=f(26, False), fill=(40, 40, 40))
    o.paste(th.convert('RGB'), (30, y0 + 44))
    th2 = th.resize((th.size[0] * 2, 256), Image.NEAREST)
    o.paste(th2.convert('RGB').crop((0, 0, min(W - 60, th2.size[0]), 256)), (30, y0 + 190))
    o = o.crop((0, 0, W, y0 + 190 + 256 + 20))
    o.save(B + 'silhouette.png', optimize=True); print('silhouette', o.size, 'labels' if len(merged) == len(order) else 'no labels (%d runs)' % len(merged))

def silhouette_rows():
    """phase 2: one block per row (phase 1 row, phase 2 row), each labelled, then the 128 px thumbnail test of every row at ONE common scale"""
    import numpy as np
    rows = [(R + 'silhouette_raw1.png', META['_order'], 'PHASE 1 (rows 1-8)'), (R + 'silhouette_raw2.png', META['_order2'], 'PHASE 2 (rows 9-20)')]
    crops = []
    for path, order, title in rows:
        raw = Image.open(path).convert('L'); bbox = ImageOps.invert(raw).getbbox(); m = 30
        crops.append((raw.crop((max(0, bbox[0] - m), max(0, bbox[1] - m), min(raw.size[0], bbox[2] + m), min(raw.size[1], bbox[3] + m))), order, title))
    W = max(c.size[0] for c, _, _ in crops)
    blocks = []
    for crop, order, title in crops:
        w, h = crop.size; a = np.array(crop) < 128; cols = a.any(axis=0); runs = []; st = None
        for x, c in enumerate(cols):
            if c and st is None: st = x
            if not c and st is not None: runs.append([st, x]); st = None
        if st is not None: runs.append([st, w])
        merged = []
        for r in runs:
            if merged and r[0] - merged[-1][1] < 10: merged[-1][1] = r[1]
            else: merged.append(r)
        b = Image.new('RGB', (W, h + 130), (255, 255, 255)); d = ImageDraw.Draw(b)
        d.text((30, 8), title, font=f(30), fill=(120, 120, 120)); b.paste(crop.convert('RGB'), (0, 50))
        rowsum = a.sum(axis=1); feet = max(i for i in range(len(rowsum)) if rowsum[i] > 30); ly = 50 + feet + 12
        if len(merged) == len(order):
            last_end = -1e9
            for (x0, x1), n in zip(merged, order):
                lab = n.replace('Crowd ', '').replace('The ', '').replace(' (hatchling)', ' hatchling').replace(' (grown)', ' grown')
                col = (150, 150, 150) if n in ('Hero kid', 'Little sister') else (20, 20, 20)
                tw = d.textlength(lab, font=f(22)); xs = (x0 + x1) / 2 - tw / 2; row = 1 if xs < last_end + 8 else 0
                d.text((xs, ly + row * 28), lab, font=f(22), fill=col)
                if row == 0: last_end = xs + tw
        else:
            d.text((30, ly), 'labels skipped: %d outlines touch (%d runs for %d figures)' % (len(order), len(merged), len(order)), font=f(22, False), fill=(160, 60, 60))
        blocks.append((b, crop))
    # thumbnails at one common scale: the tallest figure of either row = 128 px
    H0 = max(c.size[1] for _, c in blocks); k = 128 / H0
    thumbs = [c.resize((int(c.size[0] * k), int(c.size[1] * k)), Image.LANCZOS) for _, c in blocks]
    tw_ = sum(t.size[0] for t in thumbs) + 60; th_h = max(t.size[1] for t in thumbs)
    Ht = sum(b.size[1] for b, _ in blocks) + 80 + 60 + th_h + 20 + th_h * 2 + 30
    o = Image.new('RGB', (max(W, tw_ * 2 // 2 + 60), Ht), (255, 255, 255)); d = ImageDraw.Draw(o)
    d.text((30, 16), 'SILHOUETTE TEST  all Cast v3 characters + Hero kid and Little sister (Cast v2), true scale, solid black', font=f(40), fill=(20, 20, 20))
    y = 80
    for b, _ in blocks: o.paste(b, (0, y)); y += b.size[1]
    d.text((30, y + 10), 'Thumbnail test: both rows at one scale, tallest figure 128 px (crowd-shot size); below, the same at 2x nearest-neighbour', font=f(26, False), fill=(40, 40, 40))
    y += 60; x = 30
    for t in thumbs: o.paste(t.convert('RGB'), (x, y + th_h - t.size[1])); x += t.size[0] + 30
    y += th_h + 20; x = 30
    for t in thumbs:
        t2 = t.resize((t.size[0] * 2, t.size[1] * 2), Image.NEAREST)
        if x + t2.size[0] > o.size[0]: break
        o.paste(t2.convert('RGB'), (x, y + th_h * 2 - t2.size[1])); x += t2.size[0] + 30
    o = o.crop((0, 0, o.size[0], y + th_h * 2 + 20))
    o.save(B + 'silhouette.png', optimize=True); print('silhouette', o.size)

if __name__ == '__main__':
    if sys.argv[1:] == ['silhouette_rows']: silhouette_rows(); sys.exit(0)
    keys = sys.argv[1:] or [k for k in META if not k.startswith('_')]
    for k in keys:
        if k == 'silhouette': silhouette(); continue
        if os.path.exists(R + k + '_turn.png'): sheet(k)
    if not sys.argv[1:] and os.path.exists(R + 'silhouette_raw.png'): silhouette()
