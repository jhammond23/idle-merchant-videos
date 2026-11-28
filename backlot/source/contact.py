"""Contact sheet per set: python3 contact.py <set> [preview_dir]"""
import sys, os, glob
from PIL import Image, ImageDraw, ImageFont

setname = sys.argv[1]
d = sys.argv[2] if len(sys.argv) > 2 else '/tmp/claude-0/backlot/previews'
order = ['WIDE_ESTABLISH', 'LOW_HERO', 'CROWD_MED', 'TWO_SHOT', 'CLOSE_A', 'CLOSE_B']
files = sorted(glob.glob(os.path.join(d, '%s_*.jpg' % setname)))
blend = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', setname, '.cc0_applied')   # written by apply_cc0.py
files = [f for f in files if 'contact' not in f and not f.endswith('_procedural.jpg')]


def key(f):
    b = os.path.basename(f)[len(setname) + 1:-4]
    cam, preset = b.rsplit('_', 1)
    pi = {'DAY': 0, 'GOLDEN': 1, 'NIGHT': 2}.get(preset, 3)
    ci = order.index(cam) if cam in order else 10
    return (ci, cam, pi)


files.sort(key=key)
tw, th = 270, 480
cols = 6
rows = (len(files) + cols - 1) // cols
pad, lab = 8, 26
W = cols * (tw + pad) + pad
H = rows * (th + lab + pad) + pad + 50
sheet = Image.new('RGB', (W, H), (24, 24, 28))
dr = ImageDraw.Draw(sheet)
try:
    font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', 15)
    big = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 26)
except Exception:
    font = big = ImageFont.load_default()
dr.text((pad, 12), 'Backlot | %s' % setname.replace('_', ' ').title(), fill=(240, 240, 240), font=big)
for i, f in enumerate(files):
    r, c = divmod(i, cols)
    im = Image.open(f).convert('RGB').resize((tw, th), Image.LANCZOS)
    x = pad + c * (tw + pad)
    y = 50 + pad + r * (th + lab + pad)
    sheet.paste(im, (x, y))
    b = os.path.basename(f)[len(setname) + 1:-4]
    if os.path.exists(blend) and os.path.getmtime(f) < os.path.getmtime(blend):
        b += '  (v1)'          # rendered before the set's last save (e.g. before the CC0 scans)
    dr.text((x + 2, y + th + 4), b, fill=(220, 220, 220) if '(v1)' not in b else (160, 160, 160), font=font)
out = os.path.join(d, '%s_contact.jpg' % setname)
sheet.save(out, quality=90)
print(out, len(files))
