"""Use a backlot set inside a film scene (Blender 5.1+).

    import sys; sys.path.insert(0, '/path/to/backlot/source')
    import backlot_api as bl
    master = bl.append_set('town_square', bpy.context.scene, preset='DAY')   # links 'Backlot | Town Square'
    bl.use_preset(bpy.context.scene, 'town_square', 'NIGHT')                 # switch lights + sky + exposure
    cam = bl.camera('town_square', 'LOW_HERO'); bpy.context.scene.camera = cam
    bl.drop_on_mark(hero_root, 'town_square', 'MARK_HERO')                  # put a Cast v2 root on a mark

Everything (lights, cameras, marks, night practicals, plaques) lives inside the one collection, so a
plain File > Append > Collection > 'Backlot | <Set>' also works; then call use_preset() once.
"""
import os
import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SETS = {
    'town_square': ('TS', 'Backlot | Town Square'),
    'bridge_river': ('BR', 'Backlot | Bridge and River'),
    'throne_hall': ('TH', 'Backlot | Throne Hall'),
    'castle_courtyard': ('CC', 'Backlot | Castle Courtyard'),
    'forest_edge': ('FE', 'Backlot | Forest Edge'),
    'harbor': ('HB', 'Backlot | Harbor'),
}
PRESETS = ('DAY', 'GOLDEN', 'NIGHT')


def append_set(name, scene, preset='DAY', blend=None, link=False):
    code, coll = SETS[name]
    path = blend or os.path.join(ROOT, name, name + '.blend')
    with bpy.data.libraries.load(path, link=link) as (src, dst):
        dst.collections = [coll]
    c = dst.collections[0]
    if c.name not in scene.collection.children:
        scene.collection.children.link(c)
    use_preset(scene, name, preset)
    return c


def _find_lc(lc, name):
    if lc.name == name:
        return lc
    for ch in lc.children:
        r = _find_lc(ch, name)
        if r:
            return r
    return None


def use_preset(scene, name, preset):
    """Show only '<CODE> Light <preset>' (sun/moon, practicals, glow meshes), set the matching sky and exposure."""
    code, coll = SETS[name]
    master = bpy.data.collections[coll]
    vl = scene.view_layers[0]
    vl.update()
    lcm = _find_lc(vl.layer_collection, master.name)
    for p in PRESETS:
        lc = _find_lc(lcm, '%s Light %s' % (code, p))
        if lc:
            lc.exclude = (p != preset)
    w = master.get('world_' + preset)
    if w is not None:
        scene.world = w
    vs = scene.view_settings
    vs.view_transform = 'Standard'
    try:
        vs.look = 'Medium High Contrast'
    except Exception:
        pass
    vs.exposure = master.get('exposure_' + preset, 0.0)


def camera(name, bookmark):
    code, _ = SETS[name]
    return bpy.data.objects['%s_%s' % (code, bookmark)]


def mark(name, mk):
    code, _ = SETS[name]
    return bpy.data.objects['%s_%s' % (code, mk)]


def drop_on_mark(root, name, mk):
    m = mark(name, mk)
    root.location = m.location.copy()
    root.rotation_euler = (0.0, 0.0, m.rotation_euler.z)


def render_settings(scene, quality='final'):
    """The settings the previews were made with (see BACKLOT.md for costs)."""
    c = scene.cycles
    scene.render.engine = 'CYCLES'
    c.samples = 96 if quality == 'final' else 32
    c.use_adaptive_sampling = True
    c.adaptive_threshold = 0.01 if quality == 'final' else 0.02
    c.use_denoising = True
    try:
        c.denoiser = 'OPENIMAGEDENOISE'
    except Exception:
        pass
    c.max_bounces, c.diffuse_bounces, c.glossy_bounces = 8, 3, 3
    c.transmission_bounces, c.transparent_max_bounces = 8, 12
    c.sample_clamp_indirect = 8.0
    c.caustics_reflective = c.caustics_refractive = False
    c.dicing_rate = 1.5
    c.offscreen_dicing_scale = 6.0
    scene.render.resolution_x, scene.render.resolution_y = 1080, 1920


def use_texture_proxies(keep=(), proxy_root=None):
    """Render-time memory saver: point every CC0 scan image at its 1K proxy (backlot/textures_1k, built by
    source/tex_proxy.py), except files whose path contains a string in `keep` (e.g. 'cobblestone_02' for a
    low ground hero shot).  Not saved: call it in the render script after opening/appending the set.
    The sets link the full 2K maps; Cycles holds textures uncompressed (2K RGB = 16 MB), so on a small box
    the proxies save roughly 0.3-0.6 GB per set.  Returns the number of images switched."""
    import sys
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    import tex_proxy
    kw = {'proxy': proxy_root} if proxy_root else {}
    n = 0
    for img in bpy.data.images:
        if img.source != 'FILE' or img.packed_file:
            continue
        fp = bpy.path.abspath(img.filepath, library=img.library)
        if any(k in fp for k in keep):
            continue
        pp = tex_proxy.proxy_path(fp, **kw)
        if pp:
            img.filepath = pp
            n += 1
    return n
