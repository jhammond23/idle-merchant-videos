"""Render backlot previews.
python3 -I render.py <set_dir_name> <PRESET> <CAMERA_SUFFIX[,CAMERA_SUFFIX...]> <res_percent> <samples> [cast:0|1] [outdir] [tex]
e.g. python3 -I render.py town_square DAY WIDE_ESTABLISH,LOW_HERO 100 48 1
tex: 'full' = the linked 2K scans; '1k' = 1K proxies (textures_1k, tex_proxy.py); '1k:a,b' = proxies except
files whose path contains a or b (default '1k:cobblestone_02').  Prints render time and peak memory.
denoise (9th arg): 'cycles' (default) = OIDN inside the render; 'split' = render the noisy image + denoising
passes to <outdir>/exr/ in <parts> horizontal bands (10th arg, default 2) and stop; then run
denoise_exr.py <outdir>/exr/*.json in a separate process (denoises each band, stitches, writes the JPG).  OIDN on a
1080x1920 frame needs ~1 GB on top of the scene, so 'split' keeps the town finals near 1.7 GB instead of 3 GB."""
import sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, '..', 'materials')]
import bpy
import castref


def peak_mb():
    for l in open('/proc/self/status'):
        if l.startswith('VmHWM'):
            return int(l.split()[1]) // 1024
    return -1


a = sys.argv[1:]
setname, preset, cams = a[0], a[1], a[2].split(',')
pct = int(a[3]) if len(a) > 3 else 50
samples = int(a[4]) if len(a) > 4 else 24
cast = (a[5] == '1') if len(a) > 5 else True
outdir = a[6] if len(a) > 6 else '/tmp/claude-0/backlot/previews'
tex = a[7] if len(a) > 7 else '1k:cobblestone_02'
denoise = a[8] if len(a) > 8 else 'cycles'
nparts = int(a[9]) if len(a) > 9 else 2
blend = '/tmp/claude-0/backlot/%s/%s.blend' % (setname, setname)
bpy.ops.wm.open_mainfile(filepath=blend)
sc = [s for s in bpy.data.scenes if s.get('bl_preset') == preset][0]
try:
    bpy.context.window.scene = sc
except Exception:
    pass
code = [c for c in bpy.data.collections if c.name.startswith('Backlot |')][0]['bl_code']
CAST = {
    'MARK_HERO': 'Hero kid', 'MARK_RIVAL': 'Rich kid', 'MARK_SIBLING': 'Little sister', 'MARK_RULER': 'Queen',
    'MARK_CROWD_1': 'Newbie', 'MARK_CROWD_2': 'Bacon kid', 'MARK_CROWD_3': 'Big kid', 'MARK_CROWD_4': 'Girl hero',
    'MARK_CROWD_5': 'Slender teen', 'MARK_CROWD_6': 'Wizard', 'MARK_CROWD_7': 'Goofy guard', 'MARK_CROWD_8': 'Villain',
    'MARK_GUARD_1': 'Knight', 'MARK_GUARD_2': 'Goofy guard',
}
if tex.startswith('1k'):
    import backlot_api
    n = backlot_api.use_texture_proxies(keep=[k for k in tex[3:].split(',') if k])
    print('texture proxies: %d images at 1K (%s)' % (n, tex), flush=True)
if cast:
    castref.stage(sc, None, {'%s_%s' % (code, k): v for k, v in CAST.items()})
    # Cast v2's Wizard and Villain carry staff orbs (materials 'orbm' blue, 'glowp' purple) that emit at 5-6:
    # by day they clip to white and read as floating lamp globes.  Previews dim them by day (a coloured gem),
    # a soft glow at golden hour, full glow at night.  Preview-only; the cast package is unchanged.
    ORB_GLOW = {'DAY': 0.25, 'GOLDEN': 1.0}
    if preset in ORB_GLOW:
        for m in bpy.data.materials:
            if m.name.split('.')[0] in ('orbm', 'glowp') and m.node_tree:
                for nd in m.node_tree.nodes:
                    if nd.type == 'BSDF_PRINCIPLED':
                        nd.inputs['Emission Strength'].default_value = ORB_GLOW[preset]
sc.render.resolution_percentage = pct
sc.cycles.samples = samples
sc.cycles.adaptive_threshold = 0.015
sc.cycles.dicing_rate = 3.0 if pct >= 100 else 2.0     # 540x960 extras: 2 px (close-ups at 1.5 px peaked 1.85 GB)
sc.cycles.offscreen_dicing_scale = 16.0     # geometry off screen diced 16x coarser (memory)
sc.cycles.max_subdivisions = 8
sc.render.use_persistent_data = False
try:
    sc.cycles.use_auto_tile = True
    sc.cycles.tile_size = 512
except Exception:
    pass
os.makedirs(outdir, exist_ok=True)
if denoise == 'split':
    import json
    vl = sc.view_layers[0]
    sc.cycles.use_denoising = True              # passes need the scene switch on ...
    vl.cycles.use_denoising = False             # ... but this layer is not denoised here
    vl.cycles.denoising_store_passes = True
    vl.use_pass_vector = True                   # the standalone denoiser insists on a vector pass
    ims = sc.render.image_settings
    jpg_q = ims.quality
    ims.media_type = 'MULTI_LAYER_IMAGE'
    ims.file_format = 'OPEN_EXR_MULTILAYER'
    ims.color_depth = '16'
    ims.exr_codec = 'ZIP'
    os.makedirs(os.path.join(outdir, 'exr'), exist_ok=True)
base_dicing = sc.cycles.dicing_rate
for c in cams:
    # wides see the displaced ground from far away: coarser dicing there keeps the town wide under ~1.7 GB
    sc.cycles.dicing_rate = 4.0 if (pct >= 100 and c.startswith('WIDE')) else base_dicing
    cam = bpy.data.objects['%s_%s' % (code, c)]
    sc.camera = cam
    out = os.path.join(outdir, '%s_%s_%s.jpg' % (setname, c, preset))
    t = time.time()
    if denoise == 'split':
        # render in horizontal bands (overlapping 120 px; band edges on exact k/128 fractions of the height)
        # so the separate denoiser only ever holds a part of the frame
        vs = sc.view_settings
        base = os.path.join(outdir, 'exr', '%s_%s_%s' % (setname, c, preset))
        W, H = sc.render.resolution_x * pct // 100, sc.render.resolution_y * pct // 100
        grid = H / 128.0
        parts = []
        for i in range(nparts):
            k0 = 0 if i == 0 else int(round(128.0 * i / nparts)) - 4
            k1 = 128 if i == nparts - 1 else int(round(128.0 * (i + 1) / nparts)) + 4
            parts.append(dict(exr='%s_part%d.exr' % (base, i), y0=int(round(k0 * grid)), y1=int(round(k1 * grid)),
                              k0=k0, k1=k1))
        json.dump(dict(jpg=out, quality=jpg_q, view_transform=vs.view_transform, look=vs.look, exposure=vs.exposure,
                       gamma=vs.gamma, display=sc.display_settings.display_device,
                       prefilter=sc.cycles.denoising_prefilter, dn_quality=sc.cycles.denoising_quality,
                       res=(W, H), parts=parts), open(base + '.json', 'w'))
        r = sc.render
        r.use_border = nparts > 1
        r.use_crop_to_border = True
        r.border_min_x, r.border_max_x = 0.0, 1.0
        for pt in parts:
            r.border_min_y, r.border_max_y = pt['k0'] / 128.0, pt['k1'] / 128.0
            r.filepath = pt['exr']
            bpy.ops.render.render(write_still=True, scene=sc.name)
        r.use_border = False
        out = base + '.json'
    else:
        sc.render.filepath = out
        bpy.ops.render.render(write_still=True, scene=sc.name)
    print('RENDERED %s %.0fs peak %d MB' % (out, time.time() - t, peak_mb()), flush=True)
