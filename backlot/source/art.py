"""Painted art for signs and banners (PIL).  Writes PNGs with alpha to source/art/.
Run: python3 -I art.py"""
import os, math
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'art')
os.makedirs(OUT, exist_ok=True)
S = 512


def canvas(bg=None):
    return Image.new('RGBA', (S, S), bg or (0, 0, 0, 0))


def paint(im, fn, fill, outline=(20, 14, 10, 255), w=10, shade=True):
    """Draw shape fn(draw, fill) with a dark outline and a soft inner highlight."""
    lay = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    fn(d, outline, w)
    lay2 = Image.new('RGBA', im.size, (0, 0, 0, 0))
    fn(ImageDraw.Draw(lay2), fill, 0)
    im.alpha_composite(lay)
    im.alpha_composite(lay2)
    if shade:
        hl = Image.new('RGBA', im.size, (0, 0, 0, 0))
        fn(ImageDraw.Draw(hl), (255, 255, 230, 70), -18)
        hl = hl.transform(im.size, Image.AFFINE, (1, 0, 6, 0, 1, 6))
        im.alpha_composite(hl.filter(ImageFilter.GaussianBlur(6)))
    return im


def ell(box):
    def f(d, col, grow):
        x0, y0, x1, y1 = box
        d.ellipse((x0 - grow, y0 - grow, x1 + grow, y1 + grow), fill=col)
    return f


def polyf(pts):
    def f(d, col, grow):
        cx = sum(p[0] for p in pts) / len(pts)
        cy = sum(p[1] for p in pts) / len(pts)
        q = []
        for x, y in pts:
            dx, dy = x - cx, y - cy
            L = math.hypot(dx, dy) or 1
            q.append((x + dx / L * grow, y + dy / L * grow))
        d.polygon(q, fill=col)
    return f


def multi(*fs):
    def f(d, col, grow):
        for g in fs:
            g(d, col, grow)
    return f


def rect(box, r=0):
    def f(d, col, grow):
        x0, y0, x1, y1 = box
        g = max(grow, -min(x1 - x0, y1 - y0) / 2 + 1)
        d.rounded_rectangle((x0 - g, y0 - g, x1 + g, y1 + g), max(r + min(g, 0), 0) if r else 0, fill=col)
    return f


def save(im, name):
    im.save(os.path.join(OUT, name + '.png'))


# --- shop signs (transparent background, painted on the board) ---------------------------------
def sign_loaf():
    im = canvas()
    paint(im, ell((86, 170, 426, 370)), (196, 118, 44, 255))
    for i in range(4):
        x = 160 + i * 64
        ImageDraw.Draw(im).line((x, 210, x + 40, 330), fill=(120, 60, 20, 255), width=12)
    save(im, 'sign_loaf')


def sign_mug():
    im = canvas()
    paint(im, rect((150, 150, 330, 410), 18), (150, 92, 40, 255))
    paint(im, multi(ell((300, 200, 410, 340))), (150, 92, 40, 255))
    ImageDraw.Draw(im).ellipse((325, 230, 385, 310), fill=(0, 0, 0, 0))
    paint(im, ell((135, 110, 345, 190)), (250, 245, 230, 255))
    for y in (220, 320):
        ImageDraw.Draw(im).rectangle((150, y, 330, y + 16), fill=(60, 40, 20, 255))
    save(im, 'sign_mug')


def sign_horseshoe():
    im = canvas()
    d = ImageDraw.Draw(im)
    d.arc((120, 90, 392, 420), 160, 380, fill=(20, 14, 10, 255), width=92)
    d.arc((130, 100, 382, 410), 160, 380, fill=(170, 170, 178, 255), width=72)
    for a in range(170, 380, 30):
        x = 256 + 108 * math.cos(math.radians(a))
        y = 255 + 125 * math.sin(math.radians(a))
        d.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(40, 40, 44, 255))
    save(im, 'sign_horseshoe')


def sign_boot():
    im = canvas()
    paint(im, polyf([(200, 90), (320, 90), (320, 300), (420, 340), (430, 420), (140, 420), (150, 330), (200, 300)]),
          (110, 60, 30, 255))
    ImageDraw.Draw(im).rectangle((140, 400, 430, 425), fill=(40, 22, 12, 255))
    save(im, 'sign_boot')


def sign_key():
    im = canvas()
    paint(im, ell((90, 180, 230, 320)), (220, 170, 60, 255))
    ImageDraw.Draw(im).ellipse((130, 220, 190, 280), fill=(0, 0, 0, 0))
    paint(im, rect((220, 232, 430, 268), 6), (220, 170, 60, 255))
    paint(im, rect((360, 262, 385, 320), 4), (220, 170, 60, 255))
    paint(im, rect((400, 262, 425, 300), 4), (220, 170, 60, 255))
    save(im, 'sign_key')


def sign_potion():
    im = canvas()
    paint(im, ell((140, 200, 372, 432)), (40, 150, 90, 255))
    paint(im, rect((220, 110, 292, 220), 8), (170, 210, 200, 255))
    paint(im, rect((205, 85, 307, 120), 8), (120, 70, 30, 255))
    save(im, 'sign_potion')


def sign_sword():
    im = canvas()
    paint(im, polyf([(246, 60), (266, 60), (276, 330), (236, 330)]), (200, 205, 215, 255))
    paint(im, rect((170, 320, 342, 350), 8), (200, 150, 50, 255))
    paint(im, rect((240, 348, 272, 430), 6), (90, 50, 25, 255))
    paint(im, ell((232, 425, 280, 470)), (200, 150, 50, 255))
    save(im, 'sign_sword')


# --- heraldic banners (full field) -----------------------------------------------------------------
def banner(name, field, charge_fn, charge_col, border=(230, 180, 60, 255)):
    im = Image.new('RGBA', (S, S * 2), field)
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, S - 1, S * 2 - 1), outline=border, width=26)
    d.rectangle((40, 40, S - 41, S * 2 - 41), outline=border, width=6)
    # swallow-tail is done in geometry; charge centred in the upper half
    sub = canvas()
    paint(sub, charge_fn, charge_col, w=12)
    im.alpha_composite(sub.resize((420, 420)), (46, 260))
    im.save(os.path.join(OUT, name + '.png'))


def crown_fn():
    pts = [(96, 380), (96, 200), (176, 280), (256, 150), (336, 280), (416, 200), (416, 380)]
    return multi(polyf(pts), rect((96, 370, 416, 420), 6), ell((236, 110, 276, 150)), ell((76, 170, 116, 210)), ell((396, 170, 436, 210)))


def sun_fn():
    fs = [ell((166, 166, 346, 346))]
    for i in range(12):
        a = math.radians(i * 30)
        a1, a2 = a - 0.13, a + 0.13
        fs.append(polyf([(256 + 105 * math.cos(a1), 256 + 105 * math.sin(a1)), (256 + 200 * math.cos(a), 256 + 200 * math.sin(a)),
                         (256 + 105 * math.cos(a2), 256 + 105 * math.sin(a2))]))
    return multi(*fs)


def tower_fn():
    fs = [rect((176, 170, 336, 430)), rect((150, 120, 362, 180))]
    for i in range(4):
        fs.append(rect((150 + i * 60, 80, 182 + i * 60, 125)))
    return multi(*fs)


def swords_fn():
    def blade(a):
        c, s = math.cos(a), math.sin(a)
        def rot(x, y):
            return (256 + x * c - y * s, 256 + x * s + y * c)
        return multi(polyf([rot(-14, -200), rot(14, -200), rot(18, 120), rot(-18, 120)]), polyf([rot(-70, 110), rot(70, 110), rot(70, 140), rot(-70, 140)]),
                     polyf([rot(-12, 140), rot(12, 140), rot(12, 220), rot(-12, 220)]))
    return multi(blade(math.radians(40)), blade(math.radians(-40)))


if __name__ == '__main__':
    sign_loaf(); sign_mug(); sign_horseshoe(); sign_boot(); sign_key(); sign_potion(); sign_sword()
    banner('banner_crown', (150, 14, 20, 255), crown_fn(), (240, 190, 60, 255))
    banner('banner_sun', (18, 46, 150, 255), sun_fn(), (250, 200, 60, 255))
    banner('banner_tower', (20, 100, 50, 255), tower_fn(), (235, 230, 215, 255))
    banner('banner_swords', (80, 20, 110, 255), swords_fn(), (230, 230, 240, 255))
    print(sorted(os.listdir(OUT)))
