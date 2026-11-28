"""Painted word boards for signposts (PIL, transparent background over the board's wood).
python3 -I art2.py  ->  source/art/word_<word>.png   (big bold capitals: readable by a 3rd grader on a phone)"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'art')
WORDS = {'TOWN': (250, 236, 200), 'FOREST': (250, 236, 200), 'CASTLE': (250, 236, 200), 'HARBOR': (250, 236, 200),
         'FISH': (250, 236, 200)}
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'


def word(w, col, W=1024, H=300):
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    size = 200
    while size > 40:
        f = ImageFont.truetype(FONT, size)
        x0, y0, x1, y1 = d.textbbox((0, 0), w, font=f, stroke_width=14)
        if x1 - x0 < W * 0.58 and y1 - y0 < H * 0.8:
            break
        size -= 6
    # centred with wide margins: the arrow tip (last ~19% of the board) is at the right on one face and at
    # the left on the other (that face is mirrored so the word still reads left to right)
    tx = (W - (x1 - x0)) / 2 - x0
    ty = (H - (y1 - y0)) / 2 - y0
    d.text((tx, ty), w, font=f, fill=col + (255,), stroke_width=14, stroke_fill=(40, 24, 12, 255))
    p = os.path.join(OUT, 'word_%s.png' % w.lower())
    im.save(p)
    return p


def path(w):
    p = os.path.join(OUT, 'word_%s.png' % w.lower())
    if not os.path.exists(p):
        word(w, WORDS.get(w, (250, 236, 200)))
    return p


if __name__ == '__main__':
    for w, c in WORDS.items():
        print(word(w, c))
