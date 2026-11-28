"""Denoise render.py 'split' renders and write the colour-managed JPGs (separate process = low peak memory).
python3 -I denoise_exr.py <shot.json> [...] [--keep]
Each JSON (written by render.py) lists the shot's horizontal band EXRs (noisy image + denoising passes).
Every band is denoised on its own (OIDN memory scales with the pixels: a whole 1080x1920 frame needs ~1.6 GB,
a half ~0.8 GB), colour-managed with the set's view settings, and the bands are cross-faded over their
120 px overlap into the final JPG.  EXRs, sidecar and temporary PNGs are deleted unless --keep."""
import sys, os, json, time
import numpy as np
import bpy
from PIL import Image


def peak_mb():
    for l in open('/proc/self/status'):
        if l.startswith('VmHWM'):
            return int(l.split()[1]) // 1024
    return -1


keep = '--keep' in sys.argv
jobs = [a for a in sys.argv[1:] if not a.startswith('--')]
sc = bpy.context.scene
sc.render.engine = 'CYCLES'
for job in jobs:
    meta = json.load(open(job))
    t = time.time()
    c = sc.cycles
    c.denoiser = 'OPENIMAGEDENOISE'
    c.denoising_prefilter = meta.get('prefilter', 'ACCURATE')
    try:
        c.denoising_quality = meta.get('dn_quality', 'HIGH')
    except Exception:
        pass
    sc.view_layers[0].cycles.denoising_store_passes = True
    vs = sc.view_settings
    sc.display_settings.display_device = meta['display']
    vs.view_transform = meta['view_transform']
    vs.look = meta['look']
    vs.exposure = meta['exposure']
    vs.gamma = meta['gamma']
    ims = sc.render.image_settings
    ims.media_type = 'IMAGE'
    ims.file_format = 'PNG'
    ims.color_mode = 'RGB'
    ims.color_depth = '16'
    W, H = meta['res']
    acc = np.zeros((H, W, 3), np.float64)
    wsum = np.zeros((H, 1, 1), np.float64)
    temps = []
    for pt in meta['parts']:
        dn = pt['exr'][:-4] + '_dn.exr'
        png = pt['exr'][:-4] + '_dn.png'
        bpy.ops.cycles.denoise_animation(input_filepath=pt['exr'], output_filepath=dn)
        img = bpy.data.images.load(dn)
        img.save_render(png, scene=sc)
        bpy.data.images.remove(img)
        temps += [dn, png]
        a = np.asarray(Image.open(png), dtype=np.float64)
        if a.ndim == 3 and a.shape[2] > 3:
            a = a[:, :, :3]
        a = a / (65535.0 if a.max() > 255 else 255.0)
        h = a.shape[0]
        # band rows are counted from the bottom in Blender; image rows from the top
        top = H - pt['y1']
        if h != pt['y1'] - pt['y0']:
            top = H - pt['y0'] - h
        top = max(0, min(H - h, top))
        w = np.ones((h, 1, 1))
        if pt['y1'] < H:                       # fade in from this band's top edge (overlap with the band above)
            n = min(h, 120)
            w[:n, 0, 0] = np.linspace(0.0, 1.0, n + 2)[1:-1]
        if pt['y0'] > 0:                       # fade out towards its bottom edge
            n = min(h, 120)
            w[h - n:, 0, 0] *= np.linspace(1.0, 0.0, n + 2)[1:-1]
        acc[top:top + h] += a[:, :W] * w
        wsum[top:top + h] += w
    out = np.clip(acc / np.maximum(wsum, 1e-9) * 255.0 + 0.5, 0, 255).astype(np.uint8)
    Image.fromarray(out).save(meta['jpg'], quality=meta['quality'], subsampling=0 if meta['quality'] >= 95 else 2)
    print('DENOISED %s %.0fs peak %d MB' % (meta['jpg'], time.time() - t, peak_mb()), flush=True)
    if not keep:
        for p in temps + [pt['exr'] for pt in meta['parts']] + [job]:
            try:
                os.remove(p)
            except OSError:
                pass
