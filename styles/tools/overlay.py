# Burn each style's own caption/title treatment onto its look-test frame (1080x1920), then build the comparison strip.
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
L = '/tmp/claude-0/kits/look/'
APP = '/home/claude/studio-app/img/styles/'
PB = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
def F(sz): return ImageFont.truetype(PB, sz)
def up(s):
    return Image.open(L + f'final_{s}.png').convert('RGB').resize((1080, 1920), Image.LANCZOS)
def text_c(img, parts, y_base, sz, stroke, fill='#FFFFFF', ink='#111111', shadow=(0, 4), line=None):
    """parts: list of (text, colour) on one line, centred, y_base = baseline"""
    d = ImageDraw.Draw(img); f = F(sz)
    widths = [d.textlength(t, font=f) for t, _ in parts]; W = sum(widths); x = (1080 - W) / 2
    asc = f.getmetrics()[0]; y = y_base - asc
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh); xx = x
    for (t, c), w in zip(parts, widths):
        sd.text((xx + shadow[0], y + shadow[1]), t, font=f, fill=(0, 0, 0, 110), stroke_width=stroke, stroke_fill=(0, 0, 0, 110)); xx += w
    img.paste(sh.filter(ImageFilter.GaussianBlur(3)), (0, 0), sh.filter(ImageFilter.GaussianBlur(3)))
    d = ImageDraw.Draw(img); xx = x
    for (t, c), w in zip(parts, widths):
        d.text((xx, y), t, font=f, fill=c or fill, stroke_width=stroke, stroke_fill=ink); xx += w
def handle(img):
    ImageDraw.Draw(img).text((44, 60), '@idlemerchantrng', font=F(34), fill='#FFFFFF', stroke_width=3, stroke_fill='#000000')

out = {}
# house: title band on frame 0 + "IN THIS TOWN," caption
im = up('house'); handle(im)
text_c(im, [('MY EGG WAS', None)], 290, 96, 7); text_c(im, [('TEN YEARS LATE.', '#FFD23C')], 400, 96, 7)
text_c(im, [('IN THIS TOWN,', None)], 1290, 78, 6); out['house'] = im
# bright-cut: no title, small white caps phrase, one red keyword, baseline 1410
im = up('bright-cut'); handle(im)
text_c(im, [('MINE TOOK TEN ', None), ('YEARS', '#E0262A')], 1410, 52, 5); out['bright-cut'] = im
# gneef: one lowercase white word at a time, baseline 1330
im = up('gneef-style'); handle(im)
text_c(im, [('years', None)], 1330, 72, 4, shadow=(3, 3)); out['gneef-style'] = im
# craftee: short format, two-line caption in the upper third, one green keyword
im = up('craftee-style'); handle(im)
text_c(im, [('EVERY EGG HATCHES', None)], 503, 88, 7); text_c(im, [('BY ', None), ('MORNING', '#2ECE30')], 591, 88, 7); out['craftee-style'] = im
# fourth: the pack's own sticker layer (name sticker, time tag, caption)
sys.path.insert(0, '/home/claude/styles/fourth-style/pack')
import post_fourth_style as P
im = up('fourth-style')
plan = {'fps': 30, 'events': [
    {'type': 'name', 'f0': 0, 'f1': 60, 'text': 'Pip', 'color': '#FF7A3D', 'x': 0.40, 'y': 0.30},
    {'type': 'time_tag', 'f0': 0, 'f1': 60, 'text': 'Ten years later', 'icon': 'hourglass', 'x': 0.06, 'y': 0.12},
    {'type': 'caption', 'f0': 0, 'f1': 60, 'text': 'MINE TOOK {TEN YEARS}'}]}
im = P.Post(plan).apply(im.copy(), 20).convert('RGB'); handle(im); out['fourth-style'] = im

names = {'house': 'Town Storybook', 'bright-cut': 'Bright Snap Cut', 'gneef-style': 'Torchlit Blocktale', 'craftee-style': 'Toybox Fable', 'fourth-style': 'Comic Sticker Saga'}
strip = Image.new('RGB', (5 * 360 + 6 * 12, 640 + 90), (24, 22, 30)); d = ImageDraw.Draw(strip)
for i, k in enumerate(names):
    im = out[k]; im.save(L + f'over_{k}.jpg', quality=90)
    t = im.resize((540, 960), Image.LANCZOS); t.save(APP + f'{k}-test.jpg', quality=86)
    strip.paste(im.resize((360, 640), Image.LANCZOS), (12 + i * 372, 12))
    d.text((12 + i * 372, 664), names[k], font=F(30), fill='#FFFFFF')
strip.save(L + 'compare.jpg', quality=90); strip.save(APP + 'compare.jpg', quality=86)
print('ok')
