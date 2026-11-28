"""1K render proxies of the CC0 scan maps the backlot uses (memory saver for small render boxes).

The .blend files link the full 2K maps in the staged pack.  On a machine with little RAM, render with
1K proxies instead: Cycles keeps every texture uncompressed (2K RGB = 16 MB, 2K grey = 4 MB), so the
full pack adds 0.5-0.9 GB per set; the proxies cut that to a quarter.  The swap happens only in memory
at render time (backlot_api.use_texture_proxies); nothing is saved with the proxy paths.

python3 -I tex_proxy.py [pack_root] [proxy_root]     (re)build the proxies for every folder in CC0_PICKS
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PACK = '/mnt/user-data/uploads/3d-models/cc0-textures'
PROXY = os.path.join(HERE, '..', 'textures_1k')
SIZE = 1024
MAPS = ('color', 'normal', 'roughness', 'displacement', 'metalness')


def proxy_path(path, pack=PACK, proxy=PROXY):
    """Proxy file for a pack file, or None."""
    ap = os.path.abspath(path)
    pk = os.path.abspath(pack)
    if not ap.startswith(pk + os.sep):
        return None
    p = os.path.join(os.path.abspath(proxy), os.path.relpath(ap, pk))
    return p if os.path.exists(p) else None


def build(pack=PACK, proxy=PROXY, folders=None):
    from PIL import Image
    if folders is None:
        sys.path.insert(0, os.path.join(HERE, '..', 'materials'))
        try:
            import mats
            folders = set()
            for mode, f, o in mats.CC0_PICKS.values():
                folders.update(f if isinstance(f, tuple) else (f,))
        except Exception:
            folders = [d for d in os.listdir(pack) if os.path.isdir(os.path.join(pack, d))]
    n = 0
    for f in sorted(folders):
        src = os.path.join(pack, f)
        if not os.path.isdir(src):
            continue
        os.makedirs(os.path.join(proxy, f), exist_ok=True)
        for fn in os.listdir(src):
            if os.path.splitext(fn)[0].lower() not in MAPS:
                continue
            dst = os.path.join(proxy, f, fn)
            if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(os.path.join(src, fn)):
                continue
            im = Image.open(os.path.join(src, fn))
            w, h = im.size
            if w <= SIZE:
                continue
            im.draft(im.mode, (SIZE, SIZE * h // w))
            mode = 'L' if fn.startswith(('roughness', 'displacement', 'metalness')) else 'RGB'
            im = im.convert(mode).resize((SIZE, max(1, SIZE * h // w)), Image.LANCZOS)
            im.save(dst, quality=92)
            n += 1
    return n


if __name__ == '__main__':
    a = sys.argv[1:]
    n = build(a[0] if a else PACK, a[1] if len(a) > 1 else PROXY)
    tot = 0
    for r, _, fs in os.walk(a[1] if len(a) > 1 else PROXY):
        tot += sum(os.path.getsize(os.path.join(r, f)) for f in fs)
    print('proxies written: %d, folder size %.1f MB' % (n, tot / 1e6))
