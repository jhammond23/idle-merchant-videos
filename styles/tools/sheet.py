# Compose a 1080x1920 sample sheet per kit from our own renders.
import json, glob, os
from PIL import Image, ImageDraw, ImageFont
B = '/tmp/claude-0/kits/out/'
APP = '/home/claude/studio-app/img/styles/'
PB = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
KITS = {'sunny': ('bright-cut', ['shocked', 'angry', 'happy', 'scared']), 'ink': ('gneef-style', ['terror', 'angry', 'crying', 'smug']),
        'toybox': ('craftee-style', ['terrified', 'angry', 'crying', 'innocent']), 'sticker': ('fourth-style', ['smug', 'alarmed', 'shouting', 'happy'])}
def f(sz): return ImageFont.truetype(PB, sz)
for kit, (sid, exprs) in KITS.items():
    lineup = B + f'F_{kit}_lineup.png'
    if not os.path.exists(lineup) or not all(os.path.exists(B + f'F_{kit}_f_{e}.png') for e in exprs): print('skip', kit); continue
    d = json.load(open(f'/home/claude/styles/{sid}/characters.json'))
    st = json.load(open(f'/home/claude/styles/{sid}/style.json'))
    W, H = 1080, 1920
    o = Image.new('RGB', (W, H), (24, 22, 30)); g = ImageDraw.Draw(o)
    g.text((40, 26), 'CHARACTER STYLE', font=f(30), fill=(255, 205, 70))
    g.text((40, 62), d['name'].upper(), font=f(64), fill=(255, 255, 255))
    g.text((40, 150), f"New characters of our own, built with our Cast v2 pipeline in the {st['name']} light", font=f(22), fill=(200, 200, 210))
    o.paste(Image.open(lineup).convert('RGB'), (0, 200))
    for i, e in enumerate(exprs):
        im = Image.open(B + f'F_{kit}_f_{e}.png').convert('RGB'); x, y = (i % 2) * 540, 960 + (i // 2) * 460
        o.paste(im, (x, y)); g.rounded_rectangle([x + 16, y + 400, x + 16 + 22 * len(e) + 30, y + 446], radius=12, fill=(24, 22, 30))
        g.text((x + 30, y + 402), e.upper(), font=f(28), fill=(255, 255, 255))
    g.rectangle([0, 958, W, 962], fill=(24, 22, 30)); g.rectangle([538, 960, 542, 1880], fill=(24, 22, 30)); g.rectangle([0, 1418, W, 1422], fill=(24, 22, 30))
    g.text((40, 1886), 'SKIN', font=f(22), fill=(200, 200, 210))
    for i, c in enumerate([c for c in d.get('skinTones', []) if isinstance(c, str)][:10]):
        g.rounded_rectangle([110 + i * 62, 1884, 160 + i * 62, 1912], radius=8, fill=c)
    g.text((760, 1886), 'method only, our own faces', font=f(20), fill=(140, 140, 150))
    o.save(APP + f'{sid}-sample.jpg', quality=86); o.save(B + f'SHEET_{kit}.jpg', quality=90)
    print('sheet', kit)
