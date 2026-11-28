# Lightning Arms: montage helper. python3 la_compose.py out.png cols label1=img1 label2=img2 ...
import sys
from PIL import Image, ImageDraw, ImageFont


def sheet(out, cols, items, pad=8, bg=(24, 24, 28)):
    ims = [(lab, Image.open(p).convert('RGB')) for lab, p in items]
    w = max(i.width for _, i in ims); h = max(i.height for _, i in ims)
    rows = (len(ims) + cols - 1) // cols
    S = Image.new('RGB', (cols * w + (cols + 1) * pad, rows * (h + 34) + (rows + 1) * pad), bg)
    d = ImageDraw.Draw(S)
    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf', 22)
    except Exception:
        font = ImageFont.load_default()
    for k, (lab, im) in enumerate(ims):
        x = pad + (k % cols) * (w + pad); y = pad + (k // cols) * (h + 34 + pad)
        S.paste(im, (x, y)); d.text((x + 6, y + h + 3), lab, fill=(255, 255, 255), font=font)
    S.save(out)


if __name__ == '__main__':
    sheet(sys.argv[1], int(sys.argv[2]), [a.split('=', 1) for a in sys.argv[3:]])
