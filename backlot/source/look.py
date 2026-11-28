"""Backlot looks: render settings, skies, light presets (DAY / GOLDEN / NIGHT), cameras, marks, scenes.

House look: Cycles, View transform Standard + look 'Medium High Contrast' (punchy, not pastel),
bright saturated daylight; night = cool moonlight + warm practicals.
"""
import bpy, math, os
from mathutils import Vector, Euler
import mats

M = 3.3
PRESETS = ('DAY', 'GOLDEN', 'NIGHT')
EXPOSURE = {'DAY': -0.55, 'GOLDEN': -0.35, 'NIGHT': 0.6}


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = 'NONE'
    return sc


def lin(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)


def render_settings(sc, quality='preview', samples=None, preset='DAY'):
    r = sc.render
    r.engine = 'CYCLES'
    c = sc.cycles
    c.device = 'CPU'
    c.samples = samples or (24 if quality == 'preview' else 96)
    c.use_adaptive_sampling = True
    c.adaptive_threshold = 0.02 if quality == 'preview' else 0.01
    c.use_denoising = True
    try:
        c.denoiser = 'OPENIMAGEDENOISE'
        c.denoising_input_passes = 'RGB_ALBEDO_NORMAL'
        c.denoising_prefilter = 'ACCURATE'
    except Exception:
        pass
    c.max_bounces = 8
    c.diffuse_bounces = 3
    c.glossy_bounces = 3
    c.transmission_bounces = 8
    c.transparent_max_bounces = 12
    c.volume_bounces = 0
    c.sample_clamp_direct = 0.0
    c.sample_clamp_indirect = 8.0
    c.caustics_reflective = False
    c.caustics_refractive = False
    try:
        c.blur_glossy = 0.6
    except Exception:
        pass
    c.dicing_rate = 1.0 if quality != 'preview' else 1.5
    c.offscreen_dicing_scale = 6.0
    c.max_subdivisions = 10
    c.use_light_tree = True
    r.resolution_x, r.resolution_y = (1080, 1920)
    r.resolution_percentage = 100 if quality != 'preview' else 50
    r.fps = 24
    r.film_transparent = False
    r.use_persistent_data = True
    sc.display_settings.display_device = 'sRGB'
    vs = sc.view_settings
    vs.view_transform = 'Standard'
    try:
        vs.look = 'Medium High Contrast'
    except Exception:
        vs.look = 'None'
    vs.exposure = EXPOSURE.get(preset, 0.0)
    vs.gamma = 1.0
    r.image_settings.file_format = 'JPEG'
    r.image_settings.quality = 92
    return sc


# ----------------------------------------------------------------------------------------------
# Skies
# ----------------------------------------------------------------------------------------------
SKY = {
    # zenith, horizon, sun glow colour, lighting strength, cloud amount
    'DAY': ('#1f5fd0', '#9cc4f0', '#fff4dc', 1.0, 0.55),
    'GOLDEN': ('#2a4f9a', '#ffb070', '#ffcf8a', 0.75, 0.5),
    'NIGHT': ('#04081a', '#16244a', '#a8c0ff', 0.22, 0.35),
    'INTERIOR': ('#1f5fd0', '#9cc4f0', '#fff4dc', 0.6, 0.0),
}


def world_sky(sc, preset='DAY', name=None, sun_dir=None, cam_strength=None, hdri=None):
    """Procedural gradient sky with soft clouds and a sun/moon glow.  The camera sees the colours at
    `cam_strength` (compensating exposure so the sky reads saturated) and the lighting uses SKY[...][3]."""
    zen, hor, glow, light, cloud = SKY[preset]
    name = name or 'BL Sky ' + preset
    w = bpy.data.worlds.get(name) or bpy.data.worlds.new(name)
    nt = w.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    nb = mats.NB(nt)
    out = nb.node('ShaderNodeOutputWorld')
    if hdri:
        tc = nb.texco('Generated')
        env = nb.node('ShaderNodeTexEnvironment')
        env.image = bpy.data.images.load(hdri, check_existing=True)
        nb.L.new(tc, env.inputs[0])
        bg = nb.node('ShaderNodeBackground')
        nb.L.new(env.outputs[0], bg.inputs[0])
        bg.inputs[1].default_value = 1.0
        nb.L.new(bg.outputs[0], out.inputs[0])
        sc.world = w
        return w
    d = nb.texco('Generated')                 # view direction for world shaders
    dn = nb.vmath('NORMALIZE', d)
    dx, dy, dz = nb.sep(dn)
    t = nb.math('POWER', nb.clamp01(dz), 0.55)
    col = nb.mix(t, lin(hor), lin(zen))
    below = nb.smooth(dz, -0.25, 0.0)       # below horizon: darker ground bounce colour
    col = nb.mix(below, nb.cmul(nb.rgb(lin(hor)), (0.25, 0.22, 0.18)), col)
    if cloud > 0:
        # clouds projected on a dome
        proj = nb.vscale(nb.comb(dx, dy, 0.0), 1.0)
        proj = nb.vmath('DIVIDE', proj, nb.comb(nb.add(dz, 0.08), nb.add(dz, 0.08), 1.0))
        cn = nb.noise(proj, 1.2, 8, 0.62, 0.0)
        cn2 = nb.noise(proj, 4.0, 4, 0.6)
        cm = nb.mul(nb.smooth(nb.add(cn, nb.mul(cn2, 0.25)), 0.56 - cloud * 0.1, 0.78 - cloud * 0.1),
                    nb.smooth(dz, 0.02, 0.25))
        if preset == 'NIGHT':
            ccol = nb.rgb(lin('#2a3a66'))
        elif preset == 'GOLDEN':
            ccol = nb.mix(cn2, lin('#ffd2a0'), lin('#ff9a70'))
        else:
            ccol = nb.mix(cn2, (1.0, 1.0, 1.0), lin('#c8d4e8'))
        col = nb.mix(nb.mul(cm, 0.9), col, ccol)
    if sun_dir is not None:
        sd = Vector(sun_dir).normalized()
        dot = nb.vmath('DOT_PRODUCT', dn, tuple(sd), out='Value')
        halo = nb.math('POWER', nb.clamp01(dot), 60.0 if preset != 'NIGHT' else 400.0)
        disc = nb.smooth(dot, 0.9994, 0.9997) if preset != 'NIGHT' else nb.smooth(dot, 0.9992, 0.9995)
        gcol = lin(glow)
        col = nb.mix(nb.mul(halo, 0.6), col, gcol)
        col = nb.mix(disc, col, nb.cmul(nb.rgb(gcol), (4.0, 4.0, 4.0)))
    if preset == 'NIGHT':
        st = nb.voronoi(nb.vscale(dn, 1.0), 220.0, 'F1', 'Distance', 1.0, '3D')
        stars = nb.mul(nb.inv(nb.smooth(st, 0.0, 0.05)), nb.smooth(dz, 0.05, 0.3))
        tw = nb.noise(dn, 80.0, 1, 0.5)
        col = nb.mix(nb.mul(stars, nb.maprange(tw, 0.3, 0.7, 0.2, 1.0)), col, (0.9, 0.92, 1.0))
    if cam_strength is None:
        cam_strength = 2.0 ** (-EXPOSURE.get(preset, 0.0)) * (0.95 if preset == 'DAY' else 1.0)
    bg_cam = nb.node('ShaderNodeBackground')
    nb.L.new(col, bg_cam.inputs['Color'])
    bg_cam.inputs['Strength'].default_value = cam_strength
    bg_l = nb.node('ShaderNodeBackground')
    nb.L.new(col, bg_l.inputs['Color'])
    bg_l.inputs['Strength'].default_value = light
    bg_l.name = 'SKYLIGHT'
    lp = nb.node('ShaderNodeLightPath')
    mx = nb.node('ShaderNodeMixShader')
    nb.L.new(lp.outputs['Is Camera Ray'], mx.inputs[0])
    nb.L.new(bg_l.outputs[0], mx.inputs[1])
    nb.L.new(bg_cam.outputs[0], mx.inputs[2])
    nb.L.new(mx.outputs[0], out.inputs['Surface'])
    w['bl_preset'] = preset
    sc.world = w
    return w


# ----------------------------------------------------------------------------------------------
# Lights
# ----------------------------------------------------------------------------------------------
SUN = {
    # elevation deg, colour, strength, angle deg
    'DAY': (52, '#fff1dc', 4.2, 1.2),
    'GOLDEN': (13, '#ffad5c', 4.0, 1.5),
    'NIGHT': (38, '#9db8ff', 0.55, 0.8),
}


def sun_obj(col, preset, azimuth_deg, name=None, strength=None, elevation=None):
    el, hexc, st, ang = SUN[preset]
    el = elevation if elevation is not None else el
    d = bpy.data.lights.new(name or ('Sun ' + preset), 'SUN')
    d.energy = strength if strength is not None else st
    d.color = lin(hexc)
    d.angle = math.radians(ang)
    o = bpy.data.objects.new(d.name, d)
    o.rotation_euler = Euler((math.radians(90 - el), 0, math.radians(azimuth_deg)), 'XYZ')
    col.objects.link(o)
    return o


def sun_direction(o):
    """Unit vector pointing TOWARDS the sun (for the sky glow)."""
    return (o.matrix_world.to_3x3() @ Vector((0, 0, 1))).normalized()


def point(col, name, loc, watts, hexc='#ffa040', radius=0.08):
    d = bpy.data.lights.new(name, 'POINT')
    d.energy = watts * M * M
    d.color = lin(hexc)
    d.shadow_soft_size = radius * M
    o = bpy.data.objects.new(name, d)
    o.location = loc
    col.objects.link(o)
    return o


def area(col, name, loc, rot, size, watts, hexc='#ffffff', shape='RECTANGLE', size_y=None, spread=180):
    d = bpy.data.lights.new(name, 'AREA')
    d.shape = shape
    d.size = size * M
    if size_y is not None:
        d.size_y = size_y * M
    d.energy = watts * M * M
    d.color = lin(hexc)
    try:
        d.spread = math.radians(spread)
    except Exception:
        pass
    o = bpy.data.objects.new(name, d)
    o.location = loc
    o.rotation_euler = rot
    col.objects.link(o)
    return o


def spot(col, name, loc, target, watts, hexc='#ffffff', angle=40, blend=0.5, radius=0.1):
    d = bpy.data.lights.new(name, 'SPOT')
    d.energy = watts * M * M
    d.color = lin(hexc)
    d.spot_size = math.radians(angle)
    d.spot_blend = blend
    d.shadow_soft_size = radius * M
    o = bpy.data.objects.new(name, d)
    o.location = loc
    look_at(o, target)
    col.objects.link(o)
    return o


# ----------------------------------------------------------------------------------------------
# Cameras and marks
# ----------------------------------------------------------------------------------------------
def look_at(obj, target, roll=0.0):
    d = Vector(target) - Vector(obj.location)
    q = d.to_track_quat('-Z', 'Y')
    obj.rotation_euler = q.to_euler()
    if roll:
        obj.rotation_euler.rotate_axis('Z', math.radians(roll))


def camera(col, name, loc, target, lens, note='', dof_target=None, fstop=None, clip_end=4000.0):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.sensor_width = 36.0
    cd.sensor_fit = 'AUTO'
    cd.clip_start = 0.1
    cd.clip_end = clip_end
    if dof_target is not None and fstop:
        cd.dof.use_dof = True
        cd.dof.focus_distance = (Vector(dof_target) - Vector(loc)).length
        cd.dof.aperture_fstop = fstop
    o = bpy.data.objects.new(name, cd)
    o.location = loc
    look_at(o, target)
    o['lens_mm'] = lens
    o['note'] = note
    col.objects.link(o)
    return o


def mark(col, name, loc, facing_deg=0.0, parent=None, size=1.2):
    """Character mark: an ARROWS empty.  Cast roots copy location + rotation.  facing_deg is the yaw of
    the character's FRONT (-Y = 0 deg, i.e. facing the default camera), counter-clockwise from above."""
    e = bpy.data.objects.new(name, None)
    e.empty_display_type = 'ARROWS'
    e.empty_display_size = size
    e.location = loc
    e.rotation_euler = (0, 0, math.radians(facing_deg))
    col.objects.link(e)
    if parent:
        e.parent = parent
    return e


def face_towards(src, dst):
    """Yaw (deg) for a character at src whose front (-Y) should face dst."""
    d = Vector(tuple(dst)[:2]) - Vector(tuple(src)[:2])
    return math.degrees(math.atan2(d.x, -d.y))


# ----------------------------------------------------------------------------------------------
# Scenes per light preset
# ----------------------------------------------------------------------------------------------
def make_preset_scenes(base, master, set_title, light_cols, worlds, default_cam, quality='final'):
    """base: the scene the set was built in.  master: the set collection (contains the light
    collections).  Creates/renames scenes '<title> DAY/GOLDEN/NIGHT' that share every object and
    differ in light collection, world and exposure."""
    scenes = {}
    for p in PRESETS:
        if p == 'DAY':
            sc = base
            sc.name = set_title + ' DAY'
        else:
            sc = bpy.data.scenes.get(set_title + ' ' + p) or bpy.data.scenes.new(set_title + ' ' + p)
            if master.name not in sc.collection.children:
                sc.collection.children.link(master)
        render_settings(sc, quality, preset=p)
        sc.world = worlds[p]
        sc.camera = default_cam
        sc['bl_preset'] = p
        scenes[p] = sc
    for p, sc in scenes.items():
        vl = sc.view_layers[0]
        vl.update()
        lc_master = _find_lc(vl.layer_collection, master.name)
        for q, lcol in light_cols.items():
            lc = _find_lc(lc_master, lcol.name)
            if lc:
                lc.exclude = (q != p)
    return scenes


def _find_lc(lc, name):
    if lc.name == name:
        return lc
    for ch in lc.children:
        r = _find_lc(ch, name)
        if r:
            return r
    return None


def apply_preset(scene, master_name, preset):
    """For films: after appending a set collection, switch its light preset in `scene`:
       apply_preset(bpy.context.scene, 'Backlot | Town Square', 'NIGHT')"""
    master = bpy.data.collections[master_name]
    vl = scene.view_layers[0]
    vl.update()
    lcm = _find_lc(vl.layer_collection, master_name)
    code = master.get('bl_code', '')
    for p in PRESETS:
        lc = _find_lc(lcm, '%s Light %s' % (code, p))
        if lc:
            lc.exclude = (p != preset)
    w = master.get('world_' + preset)
    if w is not None:
        scene.world = w
    scene.view_settings.view_transform = 'Standard'
    try:
        scene.view_settings.look = 'Medium High Contrast'
    except Exception:
        pass
    scene.view_settings.exposure = master.get('exposure_' + preset, EXPOSURE[preset])
