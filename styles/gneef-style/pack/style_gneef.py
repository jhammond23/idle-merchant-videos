"""Torchlit Blocktale (style id: gneef-style) - Blender 5.3 helper module.

Import in a builder script:
    import sys; sys.path.insert(0, '/path/to/gneef-style/pack')
    import style_gneef as S
    S.apply_look(bpy.context.scene, mood='ember')
    lights = S.light_rig('ember_interior', target=(0, 0, 1.2))
    cam = S.new_camera('wide')
    S.place(cam, loc=(0, -6, 1.5), look_at=(0, 0, 1.4))
    S.push(cam, 1, 45)            # the default move on 3 of 4 shots
    S.wobble(cam, 1, 45)          # always
    plan = S.cut_plan('story-word-timings.json')

Every default below is a measured number from the teardown of 6 videos (5 in the current format,
483 shots, 810 s of footage, 11-26-2026). See STYLE.md section 14 for the catalogue; the catalogue
number of each technique is given in its docstring.

Camera model: every camera gets a parent RIG empty (made by rig()). Moves (push, truck, tilt,
plunge, follow) key the RIG; roll, wobble and the pre-roll snap key the CAMERA's local rotation, so
roll is always about the view axis. Keep your own constraints on the RIG, not the camera.
Frame rate is 30 fps everywhere (FPS).
"""
import math
import json

try:
    import bpy
    from mathutils import Vector, Euler, Matrix
except ImportError:  # lets cut_plan() run in plain Python
    bpy = None

FPS = 30
RES = (1080, 1920)
UNITS_PER_M = 3.3
"""Our scene scale: Cast v2 people are ~6 Blender units tall (kid ~5, adult ~6.3), town models in the
same units, so 1 m = 3.3 units. Every distance default below is written in metres and multiplied by
UNITS_PER_M; point/area light energies are multiplied by UNITS_PER_M**2 (inverse-square falloff).
Set style_gneef.UNITS_PER_M = 1.0 for a metre-scale scene."""


def U(m):
    """metres -> scene units"""
    return m * UNITS_PER_M

# ---------------------------------------------------------------------------------------------
# Measured numbers (pooled over the 5 current-format videos unless noted)
# ---------------------------------------------------------------------------------------------
MEASURED = {
    'shot_avg_s': 1.53, 'shot_median_s': 1.30, 'shot_p10_s': 0.60, 'shot_p90_s': 2.60,
    'first30_avg_s_newest': 0.94, 'cuts_per_min': 39, 'cut_on_word_share': 0.85,
    'words_per_shot_median': (4, 6), 'words_per_s': (3.2, 3.5),
    'push_share': 0.73, 'push_pct_per_s_median': (6.0, 9.0), 'push_pct_per_s_iqr': (1.5, 15.0),
    'pull_share': (0.05, 0.17), 'pull_pct_per_s': -6.0,
    'wobble_px_rms_calm': (1, 3), 'wobble_px_rms_action': (6, 14), 'wobble_hz': (3, 8),
    'roll_share': (0.35, 0.65), 'roll_deg_per_s': (1.5, 4.0),
    'brightness_mean': 82, 'saturation_mean': 0.64, 'shadow_share_below40': (0.30, 0.45),
    'edge_to_centre_luma': (0.72, 0.85),
    'framing': {'wide': .26, 'full': .24, 'medium': .26, 'close': .13, 'ecu': .06, 'insert': .07},
}

LENS = {'wide': 26.0, 'medium': 30.0, 'close': 45.0, 'ecu': 80.0, 'insert': 60.0}
"""Lens per framing with a VERTICAL 36 mm sensor fit. 26 mm = 69.4 deg vertical FOV, the game's
default 70 deg seen on wides and mediums; closes look like 40-50 mm; extreme closes 70-85 mm."""

MOODS = {
    # Calibrated 11-26 on our town-square test scene (Cycles, Cast v2 cast, town models), see STYLE.md
    # "Calibrated on our scene". world = ambient fill colour/strength (never black: the shadows must read
    # as indigo or umber, not dead black-red); grade = HueSat saturation, Colour Balance lift/gain.
    'ember':  dict(world=(0.050, 0.045, 0.110), world_str=0.65, exposure=-0.05, sat=1.18,
                   lift=(1.00, 0.99, 1.02), gain=(1.05, 0.99, 0.92), bloom=0.10,
                   sun=dict(color=(1.0, 0.64, 0.38), strength=3.2, el=16, rot=-35),
                   practical=dict(color=(1.0, 0.66, 0.40), energy=260.0)),
    'moon':   dict(world=(0.040, 0.045, 0.110), world_str=1.15, exposure=0.15, sat=1.10,
                   lift=(0.98, 0.98, 1.05), gain=(0.92, 0.94, 1.08), bloom=0.12,
                   sun=dict(color=(0.55, 0.62, 1.0), strength=1.3, el=38, rot=-40),
                   practical=dict(color=(1.0, 0.66, 0.40), energy=320.0)),
    'day':    dict(world=(0.22, 0.42, 0.95), world_str=0.8, exposure=-0.05, sat=1.38,
                   lift=(1.0, 1.0, 1.0), gain=(1.02, 1.0, 0.97), bloom=0.05,
                   sun=dict(color=(1.0, 0.96, 0.90), strength=3.5, el=35, rot=-30),
                   practical=None),
    'golden': dict(world=(0.25, 0.38, 0.80), world_str=0.7, exposure=0.28, sat=1.32,
                   lift=(1.0, 0.99, 1.0), gain=(1.07, 1.0, 0.88), bloom=0.08,
                   sun=dict(color=(1.0, 0.70, 0.42), strength=4.0, el=14, rot=-35),
                   practical=None),
}
"""Grade + light presets. Measured targets (0-255 sRGB mean luma / HSV saturation): night 60-75,
interior/ember 75-90, day or golden 95-105; saturation 0.60-0.72; 30-45% of pixels below 40;
vignette edges 15-28% darker. Exposure values are for the Standard view + Medium High Contrast."""


# ---------------------------------------------------------------------------------------------
# Look
# ---------------------------------------------------------------------------------------------
def _set_enum(holder, prop, candidates):
    """Set the first candidate the running Blender accepts (colour-management enums are dynamic)."""
    for c in candidates:
        try:
            setattr(holder, prop, c)
            return c
        except (TypeError, ValueError):
            continue
    return getattr(holder, prop)


def apply_look(scene=None, mood='ember', vignette=0.25, compositor=True):
    """Render and colour settings for the style (catalogue: Light and grade, section 3).

    mood: 'ember' (lantern interiors, 77-80% warm hues), 'moon' (lilac-blue nights, 46% cool),
          'day' (clear blue sky, no haze), 'golden' (warm golden hour, newest upload).
    vignette: edge darkening (0.25 = edges 25% darker; measured 15-28%).
    Sets EEVEE, 1080x1920, 30 fps, motion blur off, view Standard + Medium High Contrast,
    exposure, world colour, and a compositor: saturation -> lift/gain -> bloom -> vignette.
    Returns the compositor node group (or None)."""
    scene = scene or bpy.context.scene
    m = MOODS[mood]
    r = scene.render
    _set_enum(r, 'engine', ['BLENDER_EEVEE', 'BLENDER_EEVEE_NEXT', 'CYCLES'])
    r.resolution_x, r.resolution_y, r.resolution_percentage = RES[0], RES[1], 100
    r.fps, r.fps_base = FPS, 1.0
    try:
        r.use_motion_blur = False  # measured: no motion blur in the source
    except Exception:
        pass
    vs = scene.view_settings
    _set_enum(vs, 'view_transform', ['Standard'])
    _set_enum(vs, 'look', ['Medium High Contrast', 'Standard - Medium High Contrast', 'AgX - Medium High Contrast', 'None'])
    vs.exposure = m['exposure']
    vs.gamma = 1.0
    try:
        scene.eevee.use_raytracing = True
    except Exception:
        pass
    # world
    w = scene.world or bpy.data.worlds.new('GNF_world')
    scene.world = w
    w.use_nodes = True
    bg = w.node_tree.nodes.get('Background')
    if bg:
        for lk in list(bg.inputs[0].links):   # drop any sky texture: the mood colour is the fill
            w.node_tree.links.remove(lk)
        bg.inputs[0].default_value = (*m['world'], 1.0)
        bg.inputs[1].default_value = m['world_str']
    if not compositor:
        return None
    return _compositor(scene, m, vignette)


def _compositor(scene, m, vignette):
    ng = bpy.data.node_groups.new('GNF_grade', 'CompositorNodeTree')
    ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    N, L = ng.nodes, ng.links
    rl = N.new('CompositorNodeRLayers')
    hs = N.new('CompositorNodeHueSat')
    hs.inputs['Saturation'].default_value = m['sat']  # 1.0 = unchanged in this node
    hs.inputs['Value'].default_value = 1.0
    cb = N.new('CompositorNodeColorBalance')
    for sock in cb.inputs:
        if sock.identifier == 'Color Lift':
            sock.default_value = (*m['lift'], 1.0)
        if sock.identifier == 'Color Gain':
            sock.default_value = (*m['gain'], 1.0)
    gl = N.new('CompositorNodeGlare')
    gl.inputs['Type'].default_value = 'Bloom'
    gl.inputs['Threshold'].default_value = 0.9
    gl.inputs['Strength'].default_value = m['bloom']
    gl.inputs['Size'].default_value = 0.7
    em = N.new('CompositorNodeEllipseMask')
    em.inputs['Size'].default_value = (0.95, 0.80)
    bl = N.new('CompositorNodeBlur')
    bl.inputs['Size'].default_value = (300, 300)
    mr = N.new('ShaderNodeMapRange')
    mr.inputs['To Min'].default_value = 1.0 - vignette
    mx = N.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'
    mx.inputs['Factor'].default_value = 1.0
    go = N.new('NodeGroupOutput')
    L.new(rl.outputs['Image'], hs.inputs['Image'])
    L.new(hs.outputs['Image'], cb.inputs['Image'])
    L.new(cb.outputs['Image'], gl.inputs['Image'])
    L.new(gl.outputs['Image'], [x for x in mx.inputs if x.identifier == 'A_Color'][0])
    L.new(em.outputs['Mask'], bl.inputs['Image'])
    L.new(bl.outputs['Image'], mr.inputs['Value'])
    L.new(mr.outputs['Result'], [s for s in mx.inputs if s.identifier == 'B_Color'][0])
    L.new([x for x in mx.outputs if x.identifier == 'Result_Color'][0], go.inputs['Image'])
    scene.compositing_node_group = ng
    return ng


# ---------------------------------------------------------------------------------------------
# Lights
# ---------------------------------------------------------------------------------------------
def _light(name, kind, energy, color, loc, radius=0.25, rot=None):
    ld = bpy.data.lights.new(name, kind)
    ld.energy = energy
    ld.color = color
    if kind in ('POINT', 'SPOT'):
        ld.shadow_soft_size = radius
    if kind == 'SUN':
        ld.angle = math.radians(2.0)
    ob = bpy.data.objects.new(name, ld)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    if rot:
        ob.rotation_euler = rot
    return ob


def light_rig(kind='ember_interior', target=(0, 0, 1.2), n_practicals=3, spread=4.0, mood=None):
    """The style's light set-ups; returns the created light objects. Distances in scene units
    (target, spread); energies are scaled by UNITS_PER_M**2. One motivated key per shot, hard
    shadows; the world colour from apply_look() is the only fill.

    'ember_interior' (mood 'ember'): a low warm sun (1.0, 0.70, 0.45) as the lantern-light key +
        n_practicals (2-4) warm point lights (1.0, 0.66, 0.40) at lantern height around the target.
        Put a visible emissive lantern/candle (emission 10-20) on each practical.
    'moon_night' (mood 'moon'): a blue moon sun (0.55, 0.62, 1.0) + one warm window/lantern point.
    'day': sun 3.5 at 35 deg (clear sky, no haze).  'golden': sun 3.2 at 12 deg, (1.0, 0.74, 0.48).
    """
    mood = mood or {'ember_interior': 'ember', 'moon_night': 'moon', 'day': 'day', 'golden': 'golden'}[kind]
    m = MOODS[mood]
    tx, ty, tz = target
    out = []
    sd = m['sun']
    el, rot = math.radians(sd['el']), math.radians(sd['rot'])
    out.append(_light('GNF_key_sun', 'SUN', sd['strength'], sd['color'], (tx, ty, tz + U(6)),
                      rot=Euler((math.pi / 2 - el, 0, rot))))
    pr = m.get('practical')
    if pr and kind in ('ember_interior', 'moon_night'):
        n = max(1, min(4, n_practicals)) if kind == 'ember_interior' else 1
        weights = [1.0, 0.6, 0.4, 0.3][:n]
        for i, wgt in enumerate(weights):
            a = math.radians(-60 + i * 110)
            loc = (tx + spread * math.cos(a), ty + spread * 0.5 * math.sin(a) - spread * 0.2, tz + U(0.6))
            out.append(_light('GNF_practical%d' % i, 'POINT', pr['energy'] * wgt * UNITS_PER_M ** 2,
                              pr['color'], loc, radius=U(0.25)))
    return out


# ---------------------------------------------------------------------------------------------
# Camera basics
# ---------------------------------------------------------------------------------------------
def new_camera(framing='wide', name='GNF_cam'):
    """Camera with a vertical 36 mm sensor fit and the lens for the framing (LENS), inside a RIG."""
    cd = bpy.data.cameras.new(name)
    cd.sensor_fit = 'VERTICAL'
    cd.sensor_height = 36.0
    cd.lens = LENS[framing]
    cam = bpy.data.objects.new(name, cd)
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    rig(cam)
    return cam


def set_lens(cam, framing, frame=None):
    """Set (and optionally key) the lens for a framing: wide 26, medium 30, close 45, ecu 80, insert 60 mm."""
    cam.data.lens = LENS[framing]
    if frame is not None:
        cam.data.keyframe_insert('lens', frame=frame)


def rig(cam):
    """Return the camera's RIG empty, creating it (rig gets the camera's world transform;
    the camera sits at identity under it, so camera-local Z rotation = roll about the view axis)."""
    p = cam.parent
    if p is not None and p.get('gnf_rig'):
        return p
    r = bpy.data.objects.new(cam.name + '_RIG', None)
    r['gnf_rig'] = True
    r.empty_display_size = 0.3
    bpy.context.scene.collection.objects.link(r)
    r.matrix_world = cam.matrix_basis.copy() if cam.parent is None else cam.matrix_world.copy()
    cam.parent = r
    cam.matrix_parent_inverse = Matrix.Identity(4)
    cam.location = (0, 0, 0)
    cam.rotation_euler = (0, 0, 0)
    return r


def place(cam, loc, look_at, frame=None):
    """Put the rig at loc looking at look_at (no roll). Keys it if frame is given."""
    r = rig(cam)
    r.location = Vector(loc)
    d = Vector(look_at) - Vector(loc)
    r.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    if frame is not None:
        _key(r, 'location', frame, 'LINEAR')
        _key(r, 'rotation_euler', frame, 'LINEAR')
    return r


def _fcurves(idb):
    ad = idb.animation_data
    if ad is None or ad.action is None:
        return []
    act = ad.action
    if hasattr(act, 'fcurves'):
        return list(act.fcurves)
    from bpy_extras import anim_utils
    cb = anim_utils.action_get_channelbag_for_slot(act, ad.action_slot)
    return list(cb.fcurves) if cb else []


def _fcurve(idb, path, index):
    for fc in _fcurves(idb):
        if fc.data_path == path and fc.array_index == index:
            return fc
    return None


def _key(ob, path, frame, interp='LINEAR', easing='AUTO', index=-1):
    ob.keyframe_insert(path, index=index, frame=frame)
    for fc in _fcurves(ob):
        if fc.data_path != path or (index >= 0 and fc.array_index != index):
            continue
        for kp in fc.keyframe_points:
            if abs(kp.co[0] - frame) < 1e-3:
                kp.interpolation = interp
                kp.easing = easing


def _upd():
    try:
        bpy.context.view_layer.update()
    except Exception:
        pass


def _view_dir(r):
    # from the rig's own rotation (the rig has no parent), so no depsgraph update is needed and the
    # values just set by place() are used even when the scene sits on another frame
    return (r.rotation_euler.to_matrix() @ Vector((0, 0, -1))).normalized()


def _dist(cam, dist):
    if dist is not None:
        return float(dist)
    cd = cam.data
    if cd.dof.focus_object is not None:
        return (cd.dof.focus_object.matrix_world.translation - cam.matrix_world.translation).length
    if cd.dof.focus_distance > 0.01:
        return cd.dof.focus_distance
    return U(5.0)


def hfov_deg(cam):
    """Horizontal FOV in degrees for a 1080x1920 frame with vertical sensor fit."""
    v = 2 * math.atan(cam.data.sensor_height / 2 / cam.data.lens)
    return math.degrees(2 * math.atan(math.tan(v / 2) * RES[0] / RES[1]))


def px_to_deg(cam, px):
    """Pixels at 1080 wide -> degrees of camera rotation (26 mm: 1 deg = 25.4 px)."""
    return px * hfov_deg(cam) / RES[0]


# ---------------------------------------------------------------------------------------------
# Camera techniques (numbers = catalogue rows in STYLE.md section 14)
# ---------------------------------------------------------------------------------------------
def push(cam, f0, f1, pct_per_s=6.5, dist=None, interp='LINEAR'):
    """#1 Continuous slow push-in (73% of shots; 85% in the newest upload).
    Dolly the RIG along its view axis so the subject grows pct_per_s % per second.
    Measured median +6 to +9 %/s (IQR +1.5 to +15, top decile +25). Linear, no ease, and keep it
    running through the cut (start the next shot already moving). Negative pct = pull-out.
    dist: camera-to-subject distance in scene units (default: DOF focus object/distance, else 5 m = U(5))."""
    r = rig(cam)
    d0 = _dist(cam, dist)
    dur = (f1 - f0) / FPS
    d1 = d0 / ((1 + pct_per_s / 100.0) ** dur)
    start = r.location.copy()
    _key(r, 'location', f0, interp)
    r.location = start + _view_dir(r) * (d0 - d1)
    _key(r, 'location', f1, interp)
    return d0 - d1


def pull_out(cam, f0, f1, pct_per_s=6.0, dist=None):
    """#3 Slow pull-out reveal (5-17% of shots, about -6 %/s, to -10 %/s). Use for scale reveals."""
    return push(cam, f0, f1, -abs(pct_per_s), dist)


def snap_push(cam, f, frames=18, pct=35.0, dist=None):
    """#2 Snap push on a reveal or shock word (1-4 per minute).
    Measured +30 to +85 %/s for 0.5-0.8 s. Default: subject grows 35% in 18 frames, cubic ease-out
    (matches ffmpeg z = 1 + 0.35*(1-(1-x)^3)). Start it on the word onset frame."""
    r = rig(cam)
    d0 = _dist(cam, dist)
    d1 = d0 / (1 + pct / 100.0)
    start = r.location.copy()
    _key(r, 'location', f, 'CUBIC', 'EASE_OUT')
    r.location = start + _view_dir(r) * (d0 - d1)
    _key(r, 'location', f + frames, 'LINEAR')
    return d0 - d1


def _noise_on(ob, path, index, f0, f1, strength, scale, phase, blend=3):
    fc = _fcurve(ob, path, index)
    if fc is None:
        ob.keyframe_insert(path, index=index, frame=f0)
        fc = _fcurve(ob, path, index)
    m = fc.modifiers.new('NOISE')
    m.scale = scale
    m.strength = strength
    m.phase = phase
    m.depth = 1
    m.use_restricted_range = True
    m.frame_start, m.frame_end = f0, f1
    m.blend_in = m.blend_out = blend
    return m


NOISE_RMS_PER_STRENGTH = 0.165
"""Calibrated: a Blender NOISE modifier (depth 1) has an rms of about 0.165 x its strength."""


def wobble(cam, f0, f1, px_rms=2.0, freq_hz=4.3):
    """#4 Handheld micro-wobble on every shot.
    Measured residual shake 1-3 px rms (calm) and 6-14 px rms (action / boat), direction reversals
    every 0.1-0.3 s (3-8 Hz). Adds NOISE modifiers to the CAMERA's local X and Y rotation, limited
    to f0..f1. px_rms is at 1080 wide; converted with the current lens (26 mm: 25.4 px per degree)."""
    deg = px_to_deg(cam, px_rms)
    strength = math.radians(deg) / NOISE_RMS_PER_STRENGTH
    scale = FPS / freq_hz
    a = _noise_on(cam, 'rotation_euler', 0, f0, f1, strength, scale, phase=f0 * 0.37 + 1.0)
    b = _noise_on(cam, 'rotation_euler', 1, f0, f1, strength * 0.9, scale * 0.86, phase=f0 * 0.53 + 7.0)
    return a, b


def roll_drift(cam, f0, f1, deg_per_s=2.0):
    """#5 Roll drift ('Dutch drift') on 35-65% of shots: 1.5-4 deg/s, 2-6 deg per shot, linear.
    Keys the CAMERA's local Z rotation (= roll about the view axis): level at f0, drifted at f1,
    level again at f1+1 (the next shot starts level). Pass a negative value to lean the other way;
    alternate the sign from shot to shot as the source does."""
    cam.rotation_euler[2] = 0.0
    _key(cam, 'rotation_euler', f0, 'LINEAR', index=2)
    cam.rotation_euler[2] = math.radians(deg_per_s * (f1 - f0) / FPS)
    _key(cam, 'rotation_euler', f1, 'CONSTANT', index=2)
    cam.rotation_euler[2] = 0.0
    _key(cam, 'rotation_euler', f1 + 1, 'LINEAR', index=2)


def boat_rock(cam, f0, f1, amp_deg=4.0, period_s=2.5):
    """#6 Boat / storm rock: sine roll +-4 deg with a 2-3 s period (peaks 10-18 deg/s measured).
    Keys a sine on the CAMERA's local Z rotation every 3 frames (Bezier between)."""
    for f in range(int(f0), int(f1) + 1, 3):
        cam.rotation_euler[2] = math.radians(amp_deg) * math.sin(2 * math.pi * (f - f0) / FPS / period_s)
        _key(cam, 'rotation_euler', f, 'BEZIER', index=2)
    _key(cam, 'rotation_euler', int(f0) + ((int(f1) - int(f0)) // 3) * 3, 'CONSTANT', index=2)
    cam.rotation_euler[2] = 0.0
    _key(cam, 'rotation_euler', f1 + 1, 'LINEAR', index=2)


def tilt_up_reveal(cam, f0, frames=72, rise=None, look_at=None):
    """#7 Tilt-up / pedestal reveal (about 1 per video): ~830 px/s for 2-2.5 s, from a cloth or prop
    detail up to the face. Raises the RIG by `rise` scene units (default 1.5 m = U(1.5)) over `frames` and re-aims at look_at each
    6 frames (pass the face position). Seen 1-2 times: treat the numbers as approximate."""
    r = rig(cam)
    rise = U(1.5) if rise is None else rise
    p0 = r.location.copy()
    for k, f in enumerate(range(int(f0), int(f0 + frames) + 1, 6)):
        t = (f - f0) / frames
        r.location = p0 + Vector((0, 0, rise * t))
        if look_at is not None:
            aim_z = Vector(look_at) - Vector((0, 0, rise * (1 - t) * 0.9))
            d = aim_z - r.location
            r.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
            _key(r, 'rotation_euler', f, 'LINEAR')
        _key(r, 'location', f, 'LINEAR')


def lateral_truck(cam, f0, f1, px_per_s=700.0, dist=None, direction=1):
    """#8 Fast lateral truck along corridors / rows of doors (2-4 per minute in openings).
    Measured 650-740 px/s for 1-1.3 s. Converts px/s at 1080 wide to m/s at the subject distance."""
    r = rig(cam)
    d = _dist(cam, dist)
    width_m = 2 * d * math.tan(math.radians(hfov_deg(cam)) / 2)
    mps = px_per_s * width_m / RES[0]
    right = (r.rotation_euler.to_matrix() @ Vector((1, 0, 0))).normalized()
    p0 = r.location.copy()
    _key(r, 'location', f0, 'LINEAR')
    r.location = p0 + right * mps * (f1 - f0) / FPS * direction
    _key(r, 'location', f1, 'LINEAR')


def whip_reframe(cam, f, to_loc, to_look_at, frames=3):
    """#9 Whip re-frame (seen once): a 2-3 frame jump to a tighter framing, then call push().
    Keys the RIG with CONSTANT interpolation at f and the new pose at f+frames.
    Breaks the Studio Bible 'no whips' rule: only with Jake's yes."""
    r = rig(cam)
    _key(r, 'location', f, 'LINEAR')
    _key(r, 'rotation_euler', f, 'LINEAR')
    place(cam, to_loc, to_look_at)
    _key(r, 'location', f + frames, 'LINEAR')
    _key(r, 'rotation_euler', f + frames, 'LINEAR')


def plunge(cam, f0, frames=24, pct_per_frame=2.1, dist=None):
    """#10 Plunge zoom, top-down into a portal or pit (seen once): +2.1 % per frame (~88 %/s) for 0.8 s.
    Put the camera top-down first (top_down())."""
    return push(cam, f0, f0 + frames, pct_per_s=((1 + pct_per_frame / 100) ** FPS - 1) * 100, dist=dist)


def follow_tumble(cam, target, f0, f1, offset=None, roll_deg=8.0):
    """#11 Follow a falling / thrown character (seen once): the frame tracks ~20 px/frame with a slight
    roll. Adds COPY_LOCATION (with offset) + TRACK_TO on the RIG, influence keyed 0->1 at f0 and back
    to 0 after f1, and rolls the camera roll_deg over the move."""
    r = rig(cam)
    offset = offset or (0.0, -U(3.0), U(0.6))
    cl = r.constraints.new('COPY_LOCATION'); cl.target = target; cl.use_offset = True
    tr = r.constraints.new('TRACK_TO'); tr.target = target; tr.track_axis = 'TRACK_NEGATIVE_Z'; tr.up_axis = 'UP_Y'
    r.location = Vector(offset)
    for c in (cl, tr):
        c.influence = 0.0
        c.keyframe_insert('influence', frame=f0 - 1)
        c.influence = 1.0
        c.keyframe_insert('influence', frame=f0)
        c.keyframe_insert('influence', frame=f1)
        c.influence = 0.0
        c.keyframe_insert('influence', frame=f1 + 1)
    roll_drift(cam, f0, f1, roll_deg / max((f1 - f0) / FPS, 0.1))


def low_angle(cam, target, dist=None, height=None, frame=None):
    """#12 Low-angle hero/creature shot (12% of shots): camera at knee height (0.4-0.8 m; default U(0.6)) looking up
    20-35 deg at the target point (pass the creature's head or chest)."""
    dist = U(4.0) if dist is None else dist
    height = U(0.6) if height is None else height
    t = Vector(target)
    loc = t + Vector((0, -dist, 0))
    loc.z = height
    return place(cam, loc, t, frame)


def top_down(cam, target, height=None, frame=None):
    """#13 Straight top-down (6% of shots): maps, beds, crossings, falls."""
    height = U(6.0) if height is None else height
    t = Vector(target)
    r = place(cam, t + Vector((0, 0.001, height)), t, frame)
    return r


def ecu(cam, head_center, dist=None, frame=None):
    """#14 Extreme close-up on a face sticker (6% of shots): eye or mouth fills ~60% of the frame.
    80 mm lens, about 0.3-0.4 m from the head. Still add push() and wobble()."""
    dist = U(0.35) if dist is None else dist
    set_lens(cam, 'ecu', frame)
    h = Vector(head_center)
    return place(cam, h + Vector((0, -dist, 0.02)), h, frame)


def preroll_snap(cam, f_first=1, frames=3, roll_deg=25.0, offset=None):
    """#22 Opening pre-roll snap (5 of 6 videos): frames 0-2 (about 0.07 s) show a 20-30 deg rolled /
    offset framing that snaps level into shot 1. Uses the CAMERA's delta rotation / delta location
    (separate channels from roll_drift and wobble) with CONSTANT keys."""
    offset = offset or (U(0.15), 0.0, 0.0)
    cam.delta_rotation_euler[2] = math.radians(roll_deg)
    cam.delta_location = Vector(offset)
    _key(cam, 'delta_rotation_euler', f_first, 'CONSTANT', index=2)
    _key(cam, 'delta_location', f_first, 'CONSTANT')
    cam.delta_rotation_euler[2] = 0.0
    cam.delta_location = (0, 0, 0)
    _key(cam, 'delta_rotation_euler', f_first + frames, 'CONSTANT', index=2)
    _key(cam, 'delta_location', f_first + frames, 'CONSTANT')


def calendar_flip(page, f0, frames=15, axis=2, angle_deg=-90.0):
    """#16 Calendar page-flip time skip (seen once): the page rotates 90 deg about its hinge edge in
    ~15 frames, ease-in. Put the page's origin on the hinge edge first."""
    a0 = page.rotation_euler[axis]
    _key(page, 'rotation_euler', f0, 'CUBIC', 'EASE_IN', index=axis)
    page.rotation_euler[axis] = a0 + math.radians(angle_deg)
    _key(page, 'rotation_euler', f0 + frames, 'LINEAR', index=axis)


def step_animation(ob, every=3):
    """#24 Stepped 2D stickers ('Z z z', music notes): animate normally, then call this to sample the
    object's curves every 3 frames with CONSTANT interpolation (10 fps feel at 30 fps)."""
    for fc in _fcurves(ob):
        if not fc.keyframe_points:
            continue
        f_a = int(fc.keyframe_points[0].co[0]); f_b = int(fc.keyframe_points[-1].co[0])
        vals = [(f, fc.evaluate(f)) for f in range(f_a, f_b + 1, every)]
        while fc.keyframe_points:
            fc.keyframe_points.remove(fc.keyframe_points[0])
        for f, v in vals:
            kp = fc.keyframe_points.insert(f, v)
            kp.interpolation = 'CONSTANT'


def whiteout(scene, f_cut, frames=3, exposure_boost=1.0):
    """#21 Whiteout glow into magic (about 1 per video): exposure rises +1 stop over the 3 frames
    before a hard cut, then drops back on the cut frame. (Bloom rises with it in the compositor.)"""
    vs = scene.view_settings
    e0 = vs.exposure
    vs.keyframe_insert('exposure', frame=f_cut - frames)
    vs.exposure = e0 + exposure_boost
    vs.keyframe_insert('exposure', frame=f_cut - 1)
    vs.exposure = e0
    vs.keyframe_insert('exposure', frame=f_cut)


# ---------------------------------------------------------------------------------------------
# Cutting
# ---------------------------------------------------------------------------------------------
def _load_words(word_timings):
    if isinstance(word_timings, str):
        word_timings = json.load(open(word_timings))
    if isinstance(word_timings, dict):
        words = word_timings['words']
        lines = word_timings.get('lines', [])
    else:
        words, lines = word_timings, []
    w = [(str(a), float(b), float(c)) for a, b, c in words]
    line_starts = {round(float(l[0]), 3) for l in lines}
    return w, line_starts


VARIETY = [1.0, 0.55, 1.25, 0.8, 1.7, 0.95, 0.65, 1.1]
"""Per-shot multipliers on the target length (mean 1.0) so the plan has the measured spread
(10th/90th percentile 0.6/2.6 s around a 1.3 s median) instead of every shot being the same."""


def cut_plan(word_timings, open_s=30.0, open_target=1.0, rest_target=1.35, min_shot=0.45,
             max_shot=3.0, open_max_words=4, max_words=6, phrase_gap=0.12, variety=True,
             hold_words=None, fps=FPS):
    """Shot boundaries following the style's cutting rule (STYLE.md section 5, catalogue #17).

    Rule (measured on 483 shots): hard cuts on word onsets for the WHOLE video (85%+ of cuts within
    +-0.1 s of a word); 4-6 words per shot; median 1.30 s, average 1.53 s, 10th/90th percentile
    0.6/2.6 s; the newest upload opens at 0.94 s per shot for its first 30 s.
    So: target 1.0 s per shot (max 4 words) until open_s, then 1.35 s (max 6 words), each target
    multiplied by the VARIETY pattern; once the target is reached, cut at the next phrase start
    (pause > phrase_gap or a new script line), or at the next word once 1.2x the target has passed.
    Never shorter than min_shot; never longer than max_shot except a hold.

    word_timings: path or dict from our *-word-timings.json ({'words': [[w, start, end], ...],
                  'lines': [[start, end, text], ...]}) or a plain list of (word, start, end).
    hold_words: optional word indexes where a long 3-8 s reveal may start (about one per video).
    Returns a list of dicts: {shot, start, end, dur, f0, f1, first_word, words, word_range}
    (f0/f1 are 1-based frames at 30 fps). The last shot ends on the last word: no outro."""
    words, line_starts = _load_words(word_timings)
    hold_words = set(hold_words or [])
    shots = []
    s_idx = 0
    t_start = 0.0
    k = 0
    i = 1
    while i < len(words):
        w, ws, we = words[i]
        elapsed = ws - t_start
        opening = t_start < open_s
        target = (open_target if opening else rest_target) * (VARIETY[k % len(VARIETY)] if variety else 1.0)
        target = max(target, min_shot)
        cap_words = open_max_words if opening else max_words
        n_words = i - s_idx
        is_phrase = (ws - words[i - 1][2]) > phrase_gap or round(ws, 3) in line_starts
        if s_idx in hold_words:
            cut = elapsed >= 3.0 and (is_phrase or elapsed >= 8.0)
        else:
            cut = (elapsed >= max_shot or
                   (elapsed >= target and is_phrase) or
                   (elapsed >= target * 1.2) or
                   (n_words >= cap_words and elapsed >= min_shot))
        if cut and elapsed >= min_shot:
            shots.append((s_idx, i))
            s_idx, t_start = i, ws
            k += 1
        i += 1
    shots.append((s_idx, len(words)))
    out = []
    for n, (a, b) in enumerate(shots):
        st = 0.0 if n == 0 else words[a][1]
        en = words[b][1] if b < len(words) else words[-1][2]
        out.append(dict(shot=n + 1, start=round(st, 3), end=round(en, 3), dur=round(en - st, 3),
                        f0=int(round(st * fps)) + 1, f1=int(round(en * fps)),
                        first_word=words[a][0], words=' '.join(x[0] for x in words[a:b]), word_range=[a, b - 1]))
    return out


def plan_stats(plan):
    d = sorted(s['dur'] for s in plan)
    n = len(d)
    return dict(shots=n, avg=round(sum(d) / n, 2), median=round(d[n // 2], 2),
                p10=round(d[int(n * 0.1)], 2), p90=round(d[min(n - 1, int(n * 0.9))], 2),
                cuts_per_min=round((n - 1) / (plan[-1]['end'] / 60), 1))


def assign_moves(plan, reveal_words=(), seed_pattern=None):
    """Suggest one move per shot with the measured mix: push-in on ~3 of 4 shots (+6.5 %/s), pull-out
    on ~1 in 8 (-6 %/s), snap push on shots that start on a reveal word, roll drift on alternate
    shots (+-2 deg/s), wobble everywhere (2 px calm). Returns the plan with a 'moves' list per shot."""
    pattern = seed_pattern or ['push', 'push', 'push', 'pull', 'push', 'push', 'push', 'push']
    reveal = {w.lower() for w in reveal_words}
    for k, s in enumerate(plan):
        mv = pattern[k % len(pattern)]
        first = s['first_word'].lower().strip('.,!?')
        moves = []
        if first in reveal:
            moves.append(('snap_push', dict(pct=35, frames=18)))
        elif mv == 'pull':
            moves.append(('pull_out', dict(pct_per_s=6.0)))
        else:
            moves.append(('push', dict(pct_per_s=6.5)))
        if k % 2 == 0:
            moves.append(('roll_drift', dict(deg_per_s=2.0 if (k // 2) % 2 == 0 else -2.0)))
        moves.append(('wobble', dict(px_rms=2.0)))
        s['moves'] = moves
    return plan


def apply_moves(cam, shot, dist=None):
    """Key the moves assign_moves() chose for one shot on cam (between shot['f0'] and shot['f1'])."""
    fns = {'push': push, 'pull_out': pull_out, 'snap_push': snap_push, 'roll_drift': roll_drift, 'wobble': wobble}
    for name, kw in shot.get('moves', []):
        if name == 'snap_push':
            snap_push(cam, shot['f0'], dist=dist, **kw)
        elif name in ('push', 'pull_out'):
            fns[name](cam, shot['f0'], shot['f1'], dist=dist, **kw)
        else:
            fns[name](cam, shot['f0'], shot['f1'], **kw)
