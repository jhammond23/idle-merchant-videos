"""Banner / sign images from the texture pack's custom/ artwork (Jake's own generated art, not CC0).
python3 -I cc0_art.py <custom_dir>     writes source/art/cc0_*.jpg

The square art is laid out for the backlot's banner meshes (UV 0..1 over the whole cloth, so the image
must already have the banner's aspect): bordered art keeps its top + frame, the frame's side strips are
extended down the banner, the bottom band closes it, and the plain cloth of the art fills the middle.
Unbordered art (gold lion) fades into its own cloth.  The tavern mug is widened to the sign board aspect
with mirrored wood from its own edges."""
import os, sys
import numpy as np
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'art')
SRC = sys.argv[1] if len(sys.argv) > 1 else '/mnt/user-data/uploads/3d-models/cc0-textures/custom'
S = 2048
OUT_W = 768

# per art: inner rect to search for plain cloth, side-strip width, straight rows of the side frame, bottom band
ART = {
    'silver_tower': dict(inner=(280, 280, 1768, 1768), side=262, rows=(620, 860), band=262),
    'black_dragon': dict(inner=(285, 285, 1763, 1763), side=270, rows=(560, 1360), band=190),
    'gold_lion': dict(inner=(0, 0, S, S), side=0),
}


def load(name):
    return np.asarray(Image.open(os.path.join(SRC, name + '.jpg')).convert('RGB').resize((S, S), Image.LANCZOS),
                      dtype=np.float32)


def plain_windows(a, inner, size=192, n=10):
    """The n flattest size x size windows inside `inner` (lowest local luminance std, close to the median)."""
    lum = a.mean(axis=2)
    x0, y0, x1, y1 = inner
    # reference cloth colour: median of a column just inside the frame (mostly plain field)
    ref = np.median(a[y0:y1, x0:x0 + 48].reshape(-1, 3), axis=0)
    cand = []
    for y in range(y0, y1 - size, 32):
        for x in range(x0, x1 - size, 32):
            w = lum[y:y + size, x:x + size]
            d = np.abs(a[y:y + size:4, x:x + size:4].reshape(-1, 3) - ref).sum(axis=1)
            cand.append((0.3 * float(w.std()) + float(d.mean()) + 0.5 * float(np.percentile(d, 99.5)), x, y))
    cand.sort()
    out = []
    for sc, x, y in cand:
        if sc > cand[0][0] * 1.6 + 2.0:
            break
        if all(abs(x - ox) > size // 2 or abs(y - oy) > size // 2 for _, ox, oy in out):
            out.append((sc, x, y))
        if len(out) >= n:
            break
    return [a[y:y + size, x:x + size] for _, x, y in out]


def quilt(patches, h, w, seed=3):
    """Fill h x w with randomly chosen, randomly flipped cloth patches, cross-faded where they overlap."""
    rng = np.random.default_rng(seed)
    size = patches[0].shape[0]
    ov = size // 4
    step = size - ov
    acc = np.zeros((h + size, w + size, 3), np.float32)
    wsum = np.zeros((h + size, w + size, 1), np.float32)
    ramp = np.minimum(np.minimum(np.arange(size), np.arange(size)[::-1]) / float(ov), 1.0) + 1e-3
    win = (ramp[:, None] * ramp[None, :])[:, :, None]
    for y in range(0, h, step):
        for x in range(0, w, step):
            p = patches[rng.integers(len(patches))]
            if rng.random() < 0.5:
                p = p[:, ::-1]
            if rng.random() < 0.5:
                p = p[::-1]
            acc[y:y + size, x:x + size] += p * win
            wsum[y:y + size, x:x + size] += win
    out = acc / np.maximum(wsum, 1e-6)
    # keep the cloth's tone even: remove slow variation between patches
    return out[:h, :w]


def vtile(strip, h):
    blk = np.concatenate([strip, strip[::-1]], axis=0)
    return np.tile(blk, (-(-h // blk.shape[0]), 1, 1))[:h]


def banner(name, aspect, out_name, centre=0.37):
    a = load(name)
    cfg = ART[name]
    H = int(round(S * aspect))
    can = quilt(plain_windows(a, cfg['inner']), H, S)
    if cfg['side']:
        sw, band = cfg['side'], cfg['band']
        r0, r1 = cfg['rows']
        can[:, :sw] = vtile(a[r0:r1, :sw], H)
        can[:, S - sw:] = vtile(a[r0:r1, S - sw:], H)
        can[:band] = a[:band]                       # top band of the frame
        can[H - band:] = a[S - band:]               # bottom band
        body = a[band:S - band]                     # the charge with its own side frame
        y0 = int(H * centre - body.shape[0] / 2)
        y0 = max(band, min(H - band - body.shape[0], y0))
        yy = np.linspace(0, 1, body.shape[0])[:, None, None]
        m = np.clip(np.minimum(yy, 1 - yy) / 0.06, 0, 1)    # soften the seams above / below the charge
        can[y0:y0 + body.shape[0]] = body * m + can[y0:y0 + body.shape[0]] * (1 - m)
    else:
        # unbordered: art centred at `centre`, soft fade into its own cloth
        y0 = max(0, int(H * centre - S / 2))
        y = np.linspace(0, 1, S)[:, None]
        x = np.linspace(0, 1, S)[None, :]
        m = (np.clip(np.minimum(y, 1 - y) / 0.12, 0, 1) * np.clip(np.minimum(x, 1 - x) / 0.05, 0, 1))[:, :, None]
        can[y0:y0 + S] = a * m + can[y0:y0 + S] * (1 - m)
    im = Image.fromarray(np.clip(can, 0, 255).astype(np.uint8))
    im = im.resize((OUT_W, int(round(OUT_W * aspect))), Image.LANCZOS)
    p = os.path.join(OUT, out_name)
    im.save(p, quality=90)
    return p


def sign(name, aspect, out_name, strip=(70, 200)):
    """Widen square art to the board aspect: wood from a clean strip near its left edge, stretched along the
    (horizontal) grain, on both sides."""
    a = load(name)
    W = int(round(S * aspect))
    pad = (W - S) // 2
    st = Image.fromarray(a[:, strip[0]:strip[1]].astype(np.uint8))
    lpad = np.asarray(st.resize((pad, S), Image.LANCZOS), np.float32)
    rpad = np.asarray(st.transpose(Image.FLIP_LEFT_RIGHT).resize((W - pad - S, S), Image.LANCZOS), np.float32)
    can = np.concatenate([lpad[:, ::-1], a, rpad[:, ::-1]], axis=1)
    im = Image.fromarray(np.clip(can, 0, 255).astype(np.uint8)).resize((1024, int(round(1024 / aspect))), Image.LANCZOS)
    p = os.path.join(OUT, out_name)
    im.save(p, quality=90)
    return p


# banner meshes: town hall facade 0.90 x 2.55 m, throne hall pillars 1.15 x 4.40 m; sign boards 0.72 x 0.52 m
JOBS = [
    ('banner', 'gold_lion', 2.55 / 0.90, 'cc0_banner_gold_lion_town.jpg'),
    ('banner', 'silver_tower', 2.55 / 0.90, 'cc0_banner_silver_tower_town.jpg'),
    ('banner', 'gold_lion', 4.4 / 1.15, 'cc0_banner_gold_lion_hall.jpg'),
    ('banner', 'silver_tower', 4.4 / 1.15, 'cc0_banner_silver_tower_hall.jpg'),
    ('banner', 'black_dragon', 4.4 / 1.15, 'cc0_banner_black_dragon_hall.jpg'),
    ('sign', 'tavern_mug', 0.72 / 0.52, 'cc0_sign_tavern_mug.jpg'),
]

if __name__ == '__main__':
    for kind, name, asp, out in JOBS:
        p = (banner if kind == 'banner' else sign)(name, asp, out)
        print(p, Image.open(p).size)
