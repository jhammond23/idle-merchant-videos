"""Toybox Fable (style id `craftee-style`): builder helper module for Blender 5.3 (bpy).

The module copies the method of Craftee Films (Instagram) only. It contains none of their characters,
lines, names or footage. Every default below comes from the 6-video teardown in ../STYLE.md
(sections are written as "S<n>" and techniques as "T<n>" from the STYLE.md section 14 catalogue).

Units and conventions (used everywhere below):
    * OUR SCENE SCALE: 1 m = UNITS_PER_M = 3.3 Blender units (BU). Cast v2 people are R6 blocks about 6 BU tall
      (kid ~5, adult ~6.3; this style puts everyone at s=1.0, so CHAR_H = 6.0 BU including hair). Town models
      (cottages 12-16, lamp 11, fountain 7) use the same units. "H" in a docstring means CHAR_H. HEAD_W = 1.3 BU.
      Light energies are given for a 1 m = 1 unit world and multiplied by UNITS_PER_M**2 (inverse-square falloff);
      depth-of-field f-stops are divided by UNITS_PER_M.
    * 30 fps, 1080x1920. Pixel sizes are measured at 1080 px wide.
    * Lenses: the sensor is fitted vertically at 36 mm, so 26 mm gives a 69.4 deg vertical FOV
      (the Roblox default of 70). At 26 mm, 1 deg of yaw moves the picture about 24 px at its centre.
    * Every camera function keys the camera RELATIVE to the pose it has when you call it.
      Aim the camera first (e.g. with look_at()), then call the technique.

Use it like this:
    import sys; sys.path.insert(0, r'<...>/styles/craftee-style/pack')
    import style_craftee_style as tf
    tf.apply_look(bpy.context.scene, mode='day')
    tf.light_rig('day', cam=cam)
    tf.setup_camera(cam, 'standard'); tf.look_at(cam, (0, 0, 3.5))
    tf.whip_in(cam, f0=1)
    plan = tf.cut_plan('/path/story-word-timings.json', fmt='short')
"""
import math
import json
import os
import re

try:
    import bpy
    from mathutils import Vector, Matrix, Euler
except ImportError:  # cut_plan()/caption_cards()/measure() also work in plain Python
    bpy = None
    Vector = Matrix = Euler = None

# ----------------------------------------------------------------------------------------------
# Constants (measured; see STYLE.md)
# ----------------------------------------------------------------------------------------------
STYLE_ID = 'craftee-style'
STYLE_NAME = 'Toybox Fable'
FPS = 30
RES = (1080, 1920)
UNITS_PER_M = 3.3      # our scenes: 1 metre = 3.3 Blender units
CHAR_H = 6.0           # BU, Cast v2 person at s=1.0 incl. hair (kid at 0.85 ~5, adult ~6.3)
HEAD_W = 1.3           # BU, Cast v2 classic head width
HEAD_H = 1.3           # BU
SENSOR_V = 36.0        # mm, sensor fit VERTICAL
SENSOR_H = SENSOR_V * RES[0] / RES[1]   # 20.25 mm horizontal
LENS = {               # S4 / S15
    'standard': 26.0,  # 69.4 deg vertical FOV, the Roblox default 70
    'comic': 18.0,     # comic close-up inside one head-width of the face
    'two_shot': 35.0,
    'insert': 50.0,    # T18 prop insert
}
PALETTE = {            # S2 (hex, sRGB)
    'sky_top': '#5D8CD0', 'sky_horizon': '#A4AEC0', 'wall_white': '#E4E7E2', 'plaster': '#D3B78B',
    'timber': '#A98758', 'wood_dark': '#6B5A41', 'cobble': '#7C7C7E', 'shade': '#48546D',
    'interior': '#362B27', 'night': '#0B060A', 'hero': '#CF3D13', 'hero_stripe2': '#F3E6C8',
    'key_green': '#2ECE30', 'key_cyan': '#42B4C7', 'key_amber': '#E6B872', 'key_yellow_cinematic': '#ECE648',
    'sun': '#FFF4E0', 'moon': '#9DB4FF', 'night_world': '#1A2440', 'lamp': '#FFB060', 'fire': '#FF8A2A',
    'face_ink': '#1E140E',
}
TARGETS = {            # S3, measured with the same method as measure() below
    # luma_sd: pass 1 measured 55-65 over whole films (probably pooled across shots and dark beats); one daytime
    # still of our town square reaches 44-47 at the calibrated settings, so a still passes at 42+.
    'day':   {'luma': (106, 125), 'sat': (0.38, 0.46), 'luma_sd': (42, 65), 'corner_ratio_min': 0.95, 'clip_max_pct': 1.0},
    'dusk':  {'luma': (70, 105), 'sat': (0.40, 0.52), 'corner_ratio_min': 0.95},   # estimated: Town dusk shots 85-98
    'night': {'luma': (30, 60), 'corner_ratio_min': 0.90},
    'black': {'luma': (0, 12)},
}
# Face set order for the Blockfolk image sequence face_001.png ... face_017.png (CHARACTERS.md S3)
EXPRESSIONS = ['neutral', 'happy', 'grin', 'innocent', 'shocked', 'terrified', 'scream', 'angry', 'furious',
               'smug', 'sad', 'crying', 'sleepy', 'sneeze', 'talk_open', 'talk_round', 'blink']

_TF_COLLECTION = 'TF lights'


# ----------------------------------------------------------------------------------------------
# Small helpers
# ----------------------------------------------------------------------------------------------
def hex_to_linear(h):
    """'#RRGGBB' (sRGB) -> linear RGB tuple for Blender colour sockets."""
    h = h.lstrip('#')
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        out.append(((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92)
    return tuple(out)


def focal_px(lens=26.0):
    """Focal length in pixels at 1080 px wide (sensor fit vertical 36 mm). 26 mm -> 1387 px."""
    return lens * RES[0] / SENSOR_H


def px_to_deg(px, lens=26.0):
    """Yaw angle that moves the picture centre by `px` pixels (at 1080 wide)."""
    return math.degrees(math.atan(px / focal_px(lens)))


def _scene(scene=None):
    return scene or bpy.context.scene


def _fcurves(idb):
    """All F-curves of an ID, for Blender 5.x slotted actions (falls back to the old API)."""
    ad = getattr(idb, 'animation_data', None)
    if not ad or not ad.action:
        return []
    act = ad.action
    try:
        from bpy_extras import anim_utils
        cb = anim_utils.action_get_channelbag_for_slot(act, ad.action_slot)
        if cb is not None:
            return list(cb.fcurves)
    except Exception:
        pass
    try:
        return list(act.fcurves)
    except Exception:
        return []


def _key(idb, path, frame, index=-1, interp='BEZIER', easing='AUTO'):
    """Insert a key on idb.<path> at `frame` (value already set) and set that key's interpolation.
    The interpolation of a key controls the segment that STARTS at that key."""
    idb.keyframe_insert(data_path=path, index=index, frame=frame)
    for fc in _fcurves(idb):
        if fc.data_path == path and (index < 0 or fc.array_index == index):
            for kp in fc.keyframe_points:
                if abs(kp.co.x - frame) < 0.01:
                    kp.interpolation = interp
                    kp.easing = easing
            fc.update()


def _key_pose(cam, frame, loc, rot, interp='BEZIER', easing='AUTO'):
    cam.location = loc
    cam.rotation_euler = rot
    _key(cam, 'location', frame, interp=interp, easing=easing)
    _key(cam, 'rotation_euler', frame, interp=interp, easing=easing)


def _base(cam):
    return cam.location.copy(), cam.rotation_euler.copy()


def _yawed(rot, deg):
    """World-Z yaw (pan). For an XYZ Euler, adding to .z rotates about world Z."""
    e = rot.copy()
    e.z += math.radians(deg)
    return e


def _rolled(rot, deg):
    """Roll about the camera's own view axis (local Z)."""
    m = rot.to_matrix() @ Matrix.Rotation(math.radians(deg), 3, 'Z')
    return m.to_euler('XYZ', rot)


def _pitched(rot, deg):
    m = rot.to_matrix() @ Matrix.Rotation(math.radians(deg), 3, 'X')
    return m.to_euler('XYZ', rot)


def _look_rot(loc, at, roll=0.0, compat=None):
    d = Vector(at) - Vector(loc)
    e = d.to_track_quat('-Z', 'Y').to_euler('XYZ', compat) if compat else d.to_track_quat('-Z', 'Y').to_euler('XYZ')
    return _rolled(e, roll) if roll else e


def _axes(rot):
    R = rot.to_matrix()
    return R @ Vector((1, 0, 0)), R @ Vector((0, 1, 0)), R @ Vector((0, 0, -1))   # right, up, forward


def _pos(x):
    """Object, Vector or tuple -> world-space Vector."""
    if hasattr(x, 'matrix_world'):
        bpy.context.view_layer.update()   # make matrix_world current after edits
        return x.matrix_world.translation.copy()
    return Vector(x)


def look_at(cam, at, roll=0.0):
    """Aim the camera at a point (no keys). Roll in degrees about the view axis."""
    cam.rotation_euler = _look_rot(cam.location, _pos(at), roll)
    return cam


def _blur_window(scene, f0, f1, shutter):
    """Motion blur only on frames f0..f1 (use_motion_blur is not animatable, so the SHUTTER is keyed:
    `shutter` inside the window, 0 outside, CONSTANT)."""
    scene.render.use_motion_blur = True
    for f, v in ((f0 - 1, 0.0), (f0, shutter), (f1 + 1, 0.0)):
        scene.render.motion_blur_shutter = v
        _key(scene, 'render.motion_blur_shutter', f, interp='CONSTANT')


# ----------------------------------------------------------------------------------------------
# Look, world and lights (S3, S15)
# ----------------------------------------------------------------------------------------------
def _world(scene, top_hex, horizon_hex, light_strength, cam_strength=1.0, name='TF world'):
    """Gradient sky. Camera rays see the exact hex colours (cam_strength compensates exposure);
    lighting rays use `light_strength` so the ambient level is set independently of the sky colour."""
    w = bpy.data.worlds.get(name) or bpy.data.worlds.new(name)
    scene.world = w
    w.use_nodes = True
    nt = w.node_tree
    N, L = nt.nodes, nt.links
    for n in list(N):
        N.remove(n)
    out = N.new('ShaderNodeOutputWorld')
    tc = N.new('ShaderNodeTexCoord')
    sep = N.new('ShaderNodeSeparateXYZ')
    L.new(tc.outputs['Generated'], sep.inputs[0])
    mr = N.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value = 0.0
    mr.inputs['From Max'].default_value = 0.6
    L.new(sep.outputs['Z'], mr.inputs['Value'])
    ramp = N.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*hex_to_linear(horizon_hex), 1)
    ramp.color_ramp.elements[1].color = (*hex_to_linear(top_hex), 1)
    L.new(mr.outputs['Result'], ramp.inputs['Fac'])
    bg_cam = N.new('ShaderNodeBackground')
    bg_cam.inputs['Strength'].default_value = cam_strength
    bg_light = N.new('ShaderNodeBackground')
    bg_light.inputs['Strength'].default_value = light_strength
    L.new(ramp.outputs['Color'], bg_cam.inputs['Color'])
    L.new(ramp.outputs['Color'], bg_light.inputs['Color'])
    lp = N.new('ShaderNodeLightPath')
    mix = N.new('ShaderNodeMixShader')
    L.new(lp.outputs['Is Camera Ray'], mix.inputs['Fac'])
    L.new(bg_light.outputs['Background'], mix.inputs[1])
    L.new(bg_cam.outputs['Background'], mix.inputs[2])
    L.new(mix.outputs['Shader'], out.inputs['Surface'])
    return w


def apply_look(scene=None, mode='day', engine='CYCLES', samples=24, exposure=None, look='High Contrast'):
    """Render and colour settings for Toybox Fable (S3, S15).

    * View transform Standard + look 'High Contrast', gamma 1: a neutral tone curve (no tint) standing in for the
      game engine's punchy curve; white stays white.
    * CALIBRATED on our town square (Cast v2 cast, a1_* town models, 26-30 mm, Cycles) in pass 3:
      day = exposure -0.75 with light_rig('day') (sun 6.0, sky fill 0.3) -> luma ~117, saturation ~0.43.
      (Look None, sun 3.0, fill 0.9, exposure -0.3 gave luma 117 but saturation 0.29 and flat shadows.)
      Night/black: exposure 0 (not calibrated on our scene yet). For a new set, measure() one small still and
      add suggest_exposure() until mean luma is 106-125 (day).
    * 1080x1920, 30 fps, motion blur OFF (only T1/T8 switch it on for their frames).
    * No vignette, grain, chromatic aberration, lens distortion or compositor (bloom() only for VFX).
    * engine 'CYCLES' (house pipeline; samples 24, 48 for hero closes, OpenImageDenoise) or 'EEVEE'
      (Blender 5 EEVEE with ray tracing and soft shadows, if the machine has a GPU).
    """
    s = _scene(scene)
    if engine.upper().startswith('EEVEE') or engine.upper() == 'BLENDER_EEVEE':
        s.render.engine = 'BLENDER_EEVEE'
        ev = s.eevee
        for attr, val in (('use_raytracing', True), ('use_shadows', True), ('shadow_ray_count', 2),
                          ('shadow_step_count', 6), ('use_fast_gi', True), ('taa_render_samples', 32)):
            if hasattr(ev, attr):
                try:
                    setattr(ev, attr, val)
                except Exception:
                    pass
    else:
        s.render.engine = 'CYCLES'
        c = s.cycles
        c.samples = samples
        c.use_denoising = True
        try:
            c.denoiser = 'OPENIMAGEDENOISE'
        except Exception:
            pass
        c.max_bounces = 4
        c.diffuse_bounces = 2
        c.glossy_bounces = 2
    s.render.resolution_x, s.render.resolution_y = RES
    s.render.resolution_percentage = 100
    s.render.fps = FPS
    s.render.fps_base = 1.0
    s.render.film_transparent = False
    s.render.use_motion_blur = False
    s.render.motion_blur_shutter = 0.5
    s.display_settings.display_device = 'sRGB'
    vs = s.view_settings
    vs.view_transform = 'Standard'
    try:
        vs.look = look
    except Exception:
        vs.look = 'None'
    vs.gamma = 1.0
    vs.use_curve_mapping = False
    if exposure is None:
        exposure = {'day': -1.0, 'dusk': -0.75}.get(mode, 0.0)
    vs.exposure = exposure
    return s


def bloom(scene=None, on=True, threshold=1.0, strength=0.15, size=0.5):
    """Compositor bloom, ONLY while emissive VFX (fire, fireworks, magic) are in frame (S3, S15).
    Translated from the Blender 4 settings 'threshold 1.0, size 6, mix -0.85' to Blender 5 Glare sockets
    (Strength 0.15 ~ mix -0.85). Check by eye: the glow should hug the emitter, the set must not haze."""
    s = _scene(scene)
    if not on:
        try:
            s.compositing_node_group = None
        except Exception:
            pass
        s.render.use_compositing = False
        return None
    ng = bpy.data.node_groups.new('TF bloom', 'CompositorNodeTree')
    ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    rl = ng.nodes.new('CompositorNodeRLayers')
    g = ng.nodes.new('CompositorNodeGlare')
    for k, v in (('Type', 'Bloom'), ('Threshold', threshold), ('Strength', strength), ('Size', size)):
        if k in g.inputs:
            g.inputs[k].default_value = v
    out = ng.nodes.new('NodeGroupOutput')
    ng.links.new(rl.outputs['Image'], g.inputs['Image'])
    ng.links.new(g.outputs['Image'], out.inputs[0])
    s.compositing_node_group = ng
    s.render.use_compositing = True
    return ng


def _lights_collection(scene, clear=True):
    col = bpy.data.collections.get(_TF_COLLECTION)
    if col is None:
        col = bpy.data.collections.new(_TF_COLLECTION)
        scene.collection.children.link(col)
    if clear:
        for o in list(col.objects):
            bpy.data.objects.remove(o, do_unlink=True)
    return col


def _sun(col, name, strength, hex_col, elevation, azimuth, angle=1.5):
    d = bpy.data.lights.new(name, 'SUN')
    d.energy = strength
    d.color = hex_to_linear(hex_col)
    d.angle = math.radians(angle)
    o = bpy.data.objects.new(name, d)
    col.objects.link(o)
    o.rotation_euler = (math.radians(90 - elevation), 0, math.radians(azimuth))
    return o


def practical(loc, watts=100, hex_col='#FFB060', radius=0.3, name='TF lamp', scene=None):
    """A warm practical (lamp, window, lantern): #FFB060, 50-200 W (S3, S15). `watts` and `radius` (m) are for a
    1 m = 1 unit world; the light gets watts * UNITS_PER_M**2 and radius * UNITS_PER_M in our scenes."""
    s = _scene(scene)
    col = _lights_collection(s, clear=False)
    d = bpy.data.lights.new(name, 'POINT')
    d.energy = watts * UNITS_PER_M ** 2
    d.color = hex_to_linear(hex_col)
    d.shadow_soft_size = radius * UNITS_PER_M
    o = bpy.data.objects.new(name, d)
    col.objects.link(o)
    o.location = loc
    return o


def light_rig(kind='day', cam=None, scene=None, az_off=35.0, clear=True):
    """The style's light set-ups (S3, S15, T14, T16). Returns the list of created light objects.

    kind:
      'day'     noon sun #FFF4E0, strength 6.0, angle 1.5 deg, elevation 50 deg, 35 deg off the camera axis
                (so faces get light) + gradient sky #5D8CD0 -> #A4AEC0, lighting fill 0.3 (camera sees the exact
                hex). Crisp, slightly soft shadows. Calibrated with apply_look(mode='day') in pass 3.
      'dusk'    (T14 beat 2, Roblox ClockTime ~18.5) low warm sun #FFB070 at 8 deg, 3.0; sky #48546D -> #E8A070, fill 0.2.
                Estimated, not calibrated: check luma 70-105.
      'evening' (T14 beat 3, ClockTime ~21, lamps on) moon #9DB4FF 0.4 + sky #1A2440 -> #3A4A7A at 0.3;
                add practical() lamps #FFB060 50-200 W.
      'night'   moon sun #9DB4FF 0.6 + world #1A2440 at 0.3; practicals #FFB060; glowing eyes are the brightest
                thing in frame. Target shot luma 30-60.
      'interior' no sun; warm ambient #362B27 at 0.25; add practical() lamps 100-200 W.
      'black'   (T16 black beat) world black; add ONE small practical (30 W). Target luma < 12.
    The sun's azimuth is set from the camera's yaw + az_off when `cam` is given.
    """
    s = _scene(scene)
    col = _lights_collection(s, clear=clear)
    cam_yaw = 90.0   # house convention: camera at -Y looking +Y, people face -Y
    if cam is not None:
        _, _, fwd = _axes(cam.rotation_euler)
        cam_yaw = math.degrees(math.atan2(fwd.y, fwd.x))
    # A Blender sun with rotation (90-el, 0, a) sends light along heading a+90 deg (from +X). We want the light
    # to travel the way the camera looks, az_off to one side, so faces turned to camera are lit.
    sun_az = cam_yaw + az_off - 90.0
    exp = s.view_settings.exposure
    cam_strength = 2.0 ** (-exp)   # the sky shows its exact hex whatever the exposure
    lights = []
    if kind == 'day':
        _world(s, PALETTE['sky_top'], PALETTE['sky_horizon'], 0.3, cam_strength)
        lights.append(_sun(col, 'TF sun', 6.0, PALETTE['sun'], 50, sun_az, 1.5))
    elif kind == 'dusk':
        _world(s, '#48546D', '#E8A070', 0.2, cam_strength)
        lights.append(_sun(col, 'TF dusk sun', 3.0, '#FFB070', 8, sun_az, 2.0))
    elif kind == 'evening':
        _world(s, PALETTE['night_world'], '#3A4A7A', 0.3, cam_strength)
        lights.append(_sun(col, 'TF moon', 0.4, PALETTE['moon'], 35, sun_az, 1.0))
    elif kind == 'night':
        _world(s, PALETTE['night_world'], PALETTE['night_world'], 0.3, cam_strength)
        lights.append(_sun(col, 'TF moon', 0.6, PALETTE['moon'], 40, sun_az, 1.0))
    elif kind == 'interior':
        _world(s, PALETTE['interior'], PALETTE['interior'], 0.25, cam_strength)
    elif kind == 'black':
        _world(s, '#000000', '#000000', 0.0, 0.0)
    else:
        raise ValueError('kind must be day, dusk, evening, night, interior or black')
    return lights


TIME_SKIP_BEATS = ('day', 'dusk', 'evening', 'night')


def time_skip(cam, f0, beat_frames=30, scene=None):
    """T14 locked-off time-skip montage: 3-4 beats of 0.8-1.2 s (default 30 f = 1.0 s) with IDENTICAL
    framing. Keys nothing on the lights (each beat is its own render: call light_rig(kind) per beat);
    locks the camera and returns [(kind, f_start, f_end), ...]. Thin the crowd beat by beat."""
    lock(cam, f0, f0 + beat_frames * len(TIME_SKIP_BEATS) - 1)
    return [(k, f0 + i * beat_frames, f0 + (i + 1) * beat_frames - 1) for i, k in enumerate(TIME_SKIP_BEATS)]


# ----------------------------------------------------------------------------------------------
# Camera set-up and techniques (S4, S14)
# ----------------------------------------------------------------------------------------------
def setup_camera(cam, kind='standard', dof_fstop=None):
    """Sensor fit vertical 36 mm, lens by kind (standard 26, comic 18, two_shot 35, insert 50).
    Depth of field off (long-film closes only: dof_fstop=4 with focus on the face; the f-stop is divided by
    UNITS_PER_M because our scenes are 3.3x real size)."""
    c = cam.data
    c.sensor_fit = 'VERTICAL'
    c.sensor_height = SENSOR_V
    c.sensor_width = SENSOR_V
    c.lens = LENS[kind] if isinstance(kind, str) else float(kind)
    c.clip_start = 0.1
    c.clip_end = 5000
    c.dof.use_dof = bool(dof_fstop)
    if dof_fstop:
        c.dof.aperture_fstop = dof_fstop / UNITS_PER_M
    return cam


def lock(cam, f0, f1):
    """T3 locked-off shot (the default: 82-90% of in-shot frames in short films, 54-70% in long).
    Keys the current pose at f0 and f1 with CONSTANT interpolation. Life comes from idles, crowds, faces."""
    loc, rot = _base(cam)
    _key_pose(cam, f0, loc, rot, 'CONSTANT')
    _key_pose(cam, f1, loc, rot, 'CONSTANT')
    return cam


def whip_in(cam, f0=1, swing_deg=30.0, axis='yaw', overshoot_deg=2.0, shutter=1.5, scene=None):
    """T1 whip-in opening (4 of 6 films). The current pose is the landed pose.
    Frame f0 is a full motion-blur frame (the camera is mid-swing), it lands on f0+3, overshoots by
    overshoot_deg (2 deg = ~48 px at 26 mm; measured 30-60 px) at f0+5 and is settled on f0+8.
    swing 25-35 deg (default 30). axis 'yaw' (pan) or 'roll'. Motion blur shutter 1.5 on f0..f0+3 only.
    Sound: whoosh + low boom peaking on f0+4..f0+6 (post script `sfx`). First caption is already up on f0."""
    loc, rot = _base(cam)
    turn = _yawed if axis == 'yaw' else _rolled
    _key_pose(cam, f0 - 3, loc, turn(rot, swing_deg))            # Bezier auto-clamped: passes f0+3 at speed
    _key_pose(cam, f0 + 3, loc, rot)
    _key_pose(cam, f0 + 5, loc, turn(rot, -overshoot_deg))
    _key_pose(cam, f0 + 8, loc, rot)
    cam.location, cam.rotation_euler = loc, rot
    _blur_window(_scene(scene), f0, f0 + 3, shutter)
    return cam


def drift(cam, f0, f1, px_per_s=200.0, direction='truck_left', subject=None, dist=10.0, push_pct=8.0):
    """T4 slow drift (15-30% of in-shot frames in long films; establishing, aerials, tension). LINEAR.

    direction 'truck_left'/'truck_right'/'rise'/'sink': the picture moves px_per_s (measured 150-300 px/s
    at 1080 wide, default 200) at the subject's distance. Camera speed = px_per_s * dist / focal_px.
    direction 'push'/'pull': the picture scales by push_pct over the shot (default 8%). The push rate was NOT
    measured separately (estimate from the 1.08x 2D recipe); the 150-300 px/s figure is for lateral drift.
    subject: an object/point to measure the distance to (else `dist` BU)."""
    loc, rot = _base(cam)
    right, up, fwd = _axes(rot)
    if subject is not None:
        dist = max(0.5, (_pos(subject) - loc).dot(fwd))
    secs = (f1 - f0) / FPS
    if direction in ('truck_left', 'truck_right', 'rise', 'sink'):
        v = px_per_s * dist / focal_px(cam.data.lens)
        vec = {'truck_left': -right, 'truck_right': right, 'rise': up, 'sink': -up}[direction]
        end = loc + vec * v * secs
    elif direction in ('push', 'pull'):
        k = 1.0 + push_pct / 100.0
        travel = dist - dist / k
        end = loc + fwd * (travel if direction == 'push' else -dist * (k - 1.0))
    else:
        raise ValueError('direction: truck_left, truck_right, rise, sink, push or pull')
    _key_pose(cam, f0, loc, rot, 'LINEAR')
    _key_pose(cam, f1, end, rot, 'LINEAR')
    return cam


def _catmull(points, n):
    """n points evenly spaced by arc length along a Catmull-Rom curve through `points`."""
    P = [Vector(p) for p in points]
    P = [P[0]] + P + [P[-1]]
    dense = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for j in range(40):
            t = j / 40
            t2, t3 = t * t, t * t * t
            dense.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    dense.append(P[-2])
    acc = [0.0]
    for a, b in zip(dense, dense[1:]):
        acc.append(acc[-1] + (b - a).length)
    total = acc[-1]
    out, k = [], 0
    for i in range(n):
        s = total * i / (n - 1)
        while k < len(acc) - 2 and acc[k + 1] < s:
            k += 1
        seg = max(1e-9, acc[k + 1] - acc[k])
        out.append(dense[k].lerp(dense[k + 1], (s - acc[k]) / seg))
    return out, total


def fly_through(cam, points, f0, frames=24, occluder=None, look_ahead=3):
    """T5 fly-through with a foreground wipe (long films, part of ~21 fast moves a minute).
    A 0.6-1.0 s move (default 24 f) along a smooth path through `points` (world BU), baked one key per
    frame (LINEAR, constant speed), looking along the path. Target speed 4-6 H/s (24-36 BU/s), passing
    within 1.7 BU (0.5 m) of a tree, lamp post or pillar (`occluder`) so it covers the frame for 3-5 frames;
    objects cross the frame in ~9 frames (~120 px a frame).
    Returns {'speed_bu_s', 'speed_h_s', 'cut_window': (fa, fb) or None}: hide the next cut inside cut_window."""
    pts, total = _catmull(points, frames + 1 + look_ahead)
    rot = cam.rotation_euler.copy()
    best = (1e9, None)
    for i in range(frames + 1):
        loc = pts[i]
        rot = _look_rot(loc, pts[i + look_ahead], compat=rot)
        _key_pose(cam, f0 + i, loc, rot, 'LINEAR')
        if occluder is not None:
            d = (_pos(occluder) - loc).length
            if d < best[0]:
                best = (d, f0 + i)
    speed = total * (frames / (frames + look_ahead)) / (frames / FPS)
    window = (best[1] - 2, best[1] + 2) if best[1] is not None else None
    return {'speed_bu_s': round(speed, 1), 'speed_h_s': round(speed / CHAR_H, 2), 'cut_window': window}


def crane_out(cam, target, f0, frames=18, h0=1.2 * CHAR_H, h1=18 * CHAR_H, roll0=40.0):
    """T6 crane-out reveal with roll (~1 per long film, at the 'world rule' reveal; seen in 1-2 films only).
    18 frames, fast first half then ease-out (CUBIC EASE_OUT): from h0 (1.2 H) above the kid looking down with a
    40 deg roll, to h1 (18 H = 108 BU, about 30 m) with the roll level. The kid shrinks ~15x."""
    t = _pos(target)
    aim = t + Vector((0, 0, 0.5 * CHAR_H))
    a = t + Vector((0, -0.35 * h0, h0))
    b = t + Vector((0, -0.35 * h1, h1))
    ra = _look_rot(a, aim, roll0, compat=cam.rotation_euler)
    rb = _look_rot(b, aim, 0.0, compat=ra)
    _key_pose(cam, f0, a, ra, 'CUBIC', 'EASE_OUT')
    _key_pose(cam, f0 + frames, b, rb, 'CUBIC', 'EASE_OUT')
    return cam


def snap_pull(cam, f0, frames=9, factor=2.5, subject=None, mode='dolly'):
    """T7 snap pull-out (1-2 per film): close -> medium-wide (picture scale x2.5) in 9 frames, ease-out.
    mode 'dolly' moves the camera back along the subject line (distance x factor);
    mode 'zoom' keys the lens from lens*factor down to lens (e.g. 65 -> 26 mm)."""
    loc, rot = _base(cam)
    if mode == 'zoom':
        lens = cam.data.lens
        cam.data.lens = lens * factor
        _key(cam.data, 'lens', f0, interp='CUBIC', easing='EASE_OUT')
        cam.data.lens = lens
        _key(cam.data, 'lens', f0 + frames, interp='CUBIC', easing='EASE_OUT')
        lock(cam, f0, f0 + frames)
        return cam
    _, _, fwd = _axes(rot)
    s = _pos(subject) if subject is not None else loc + fwd * 3.0
    end = s + (loc - s) * factor
    _key_pose(cam, f0, loc, rot, 'CUBIC', 'EASE_OUT')
    _key_pose(cam, f0 + frames, end, rot, 'CUBIC', 'EASE_OUT')
    return cam


def swish(cam, f0, frames=10, deg=90.0, shutter=0.5, scene=None):
    """T8 swish pan inside a shot (long films, ~1 a minute): ~90 deg yaw over 9-12 frames (default 10),
    SINE ease-in-out, motion blur shutter 0.5 on those frames only; 60+ px a frame at the peak.
    Trigger: following a runner, boat or projectile to a new composition. deg<0 pans the other way."""
    loc, rot = _base(cam)
    _key_pose(cam, f0, loc, rot, 'SINE', 'EASE_IN_OUT')
    _key_pose(cam, f0 + frames, loc, _yawed(rot, deg), 'SINE', 'EASE_IN_OUT')
    _blur_window(_scene(scene), f0, f0 + frames, shutter)
    return cam


def follow_prop(cam, prop, f0, f1, offset=(0.8, -0.6, 0.3), roll_deg=15.0, scene=None):
    """T9 follow-the-prop (~1 per long film; seen in 1 film): a note, letter or coin travels somewhere
    secret (~20 frames). Animate the prop first. The camera rides ~1 BU (0.3 m) from it (world offset), looking at it,
    rolling 0 -> roll_deg (15) at the middle -> 0 as it squeezes through a gap. Baked per frame, LINEAR."""
    s = _scene(scene)
    keep = s.frame_current
    off = Vector(offset)
    rot = cam.rotation_euler.copy()
    n = max(1, f1 - f0)
    for f in range(f0, f1 + 1):
        s.frame_set(f)
        p = _pos(prop)
        u = (f - f0) / n
        roll = roll_deg * math.sin(math.pi * u)
        loc = p + off
        rot = _look_rot(loc, p, roll, compat=rot)
        _key_pose(cam, f, loc, rot, 'LINEAR')
    s.frame_set(keep)
    return cam


def track_runner(cam, runner, f0, f1, side=2.4 * CHAR_H, height=0.7 * CHAR_H, scene=None):
    """T10 tracking truck with a runner (long films, ~1 a minute, 1-2 s): the camera moves at the runner's
    speed, side-on, `side` (2.4 H = 14.4 BU, ~4 m) away at chest height (0.7 H). Animate the runner's root first;
    baked per frame, LINEAR. Pass a pillar between camera and runner to wipe out of the shot."""
    s = _scene(scene)
    keep = s.frame_current
    s.frame_set(f0)
    a = _pos(runner)
    s.frame_set(f1)
    b = _pos(runner)
    d = b - a
    d.z = 0
    d = d.normalized() if d.length > 1e-6 else Vector((1, 0, 0))
    perp = Vector((d.y, -d.x, 0))
    rot = cam.rotation_euler.copy()
    for f in range(f0, f1 + 1):
        s.frame_set(f)
        p = _pos(runner)
        loc = p + perp * side + Vector((0, 0, height))
        rot = _look_rot(loc, p + Vector((0, 0, 0.6 * CHAR_H)), compat=rot)
        _key_pose(cam, f, loc, rot, 'LINEAR')
    s.frame_set(keep)
    return cam


def dutch(cam, f0, f1, deg=15.0):
    """T17 Dutch tilt: a static roll of 10-30 deg (default 15) for a whole shot. Long films only
    (~18% of shots in the 'wrong world' film, 0 in short films). Never on the hero's triumph shot."""
    loc, rot = _base(cam)
    r = _rolled(rot, deg)
    _key_pose(cam, f0, loc, r, 'CONSTANT')
    _key_pose(cam, f1, loc, r, 'CONSTANT')
    return cam


def prop_insert(cam, prop, f0, f1, fill=0.7, lens=50.0):
    """T18 prop insert (ECU), long films ~10-15% of shots, 0.8-1.5 s: the prop (scaled 1.3x, lit flat and
    readable) fills 60-80% of the frame (default 70%). Keeps the camera's direction, sets lens 50 mm and the
    distance from the prop's size. Keys lens and pose CONSTANT on f0 and f1."""
    _, rot = _base(cam)
    _, _, fwd = _axes(rot)
    dims = prop.dimensions
    h = max(dims.z, 1e-3)
    w = max(dims.x, dims.y, 1e-3)
    d = max(h * lens / (SENSOR_V * fill), w * lens / (SENSOR_H * fill))
    centre = prop.matrix_world @ Vector((0, 0, 0))
    if prop.type == 'MESH' and prop.data.vertices:
        bb = [prop.matrix_world @ Vector(c) for c in prop.bound_box]
        centre = sum(bb, Vector()) / 8
    loc = centre - fwd * d
    cam.data.lens = lens
    _key(cam.data, 'lens', f0, interp='CONSTANT')
    _key(cam.data, 'lens', f1, interp='CONSTANT')
    _key_pose(cam, f0, loc, rot, 'CONSTANT')
    _key_pose(cam, f1, loc, rot, 'CONSTANT')
    return cam


def zoom_through(cam, screen, f_end, frames=6, factor=1.4):
    """T19 zoom-through loop ending (1 per long film; seen in 1 film): over the last 6 frames push the
    camera at an in-world screen/frame until it is x1.4 bigger and its border leaves the frame (LINEAR).
    The screen shows frame 0's image, so the last frame matches frame 0 (check with `post ... loopcheck`).
    Write the last line so it flows into the first line."""
    loc, rot = _base(cam)
    c = _pos(screen)
    end = c + (loc - c) / factor
    _key_pose(cam, f_end - frames, loc, rot, 'LINEAR')
    _key_pose(cam, f_end, end, rot, 'LINEAR')
    return cam


def swing_settle(cam, f0, frames=20, deg=25.0, overshoot=0.10, settle=6):
    """T21 swing and settle. CINEMATIC VARIANT ONLY (1 film): a 10-30 frame yaw following something huge,
    overshooting 10% and settling in 6 frames (about 38 direction reversals a minute in that film)."""
    loc, rot = _base(cam)
    _key_pose(cam, f0, loc, rot, 'SINE', 'EASE_IN_OUT')
    _key_pose(cam, f0 + frames, loc, _yawed(rot, deg * (1 + overshoot)), 'SINE', 'EASE_IN_OUT')
    _key_pose(cam, f0 + frames + settle, loc, _yawed(rot, deg), 'SINE', 'EASE_IN_OUT')
    return cam


def impact_shake(cam, f, px=8.0, hz=12.0, frames=8):
    """OFF-STYLE. The teardown measured NO shake (0 direction reversals a minute in the short films).
    Only if Jake asks for it: one impact, 8 px at 1080 wide, 12 Hz, decaying linearly to 0 in 8 frames.
    Keyed per frame (yaw + half-size pitch), LINEAR."""
    loc, rot = _base(cam)
    amp = px_to_deg(px, cam.data.lens)
    for i in range(frames + 1):
        t = i / FPS
        env = 1.0 - i / frames
        y = amp * env * math.sin(2 * math.pi * hz * t + math.pi / 2)
        p = 0.5 * amp * env * math.sin(2 * math.pi * hz * t)
        _key_pose(cam, f + i, loc, _pitched(_yawed(rot, y), p), 'LINEAR')
    cam.location, cam.rotation_euler = loc, rot
    return cam


# ----------------------------------------------------------------------------------------------
# Characters, VFX and light pulses (S10, T11-T13, T15, T26)
# ----------------------------------------------------------------------------------------------
def walk_to_camera(person, cam, f0, frames=24, step_frames=6, swing_deg=40.0, start_fill=0.6, end_head_frac=0.4):
    """T26 walk-to-camera reframe (1-3 per film): a LOCKED camera, the character walks straight at the lens
    for 24 frames (0.8 s), a step every 6 frames, limbs swinging +/-40 deg in opposition (rigid, LINEAR).
    Starts where the whole body fills 60% of the frame height, ends where the head is 40% of the frame width
    (cut there). At 26 mm that is 7.2 BU -> 4.2 BU from the lens. Framing measured on 1 walk; estimate.
    person: the dict returned by cast_v2.person() (keys root, armL, armR, legL, legR) or a root object."""
    P = person if isinstance(person, dict) else {'root': person}
    root = P['root']
    lens = cam.data.lens
    d0 = CHAR_H * lens / (SENSOR_V * start_fill)
    d1 = HEAD_W * lens / (SENSOR_H * end_head_frac)
    c = _pos(cam)
    _, _, fwd = _axes(cam.rotation_euler)
    g = Vector((fwd.x, fwd.y, 0))
    g = g.normalized() if g.length > 1e-6 else Vector((0, 1, 0))
    z = root.location.z
    a = c + g * d0
    b = c + g * d1
    a.z = b.z = z
    face = -g
    yaw = math.atan2(face.x, -face.y)   # Cast v2 people face -Y
    root.rotation_euler = (0, 0, yaw)
    for f, p in ((f0, a), (f0 + frames, b)):
        root.location = p
        _key(root, 'location', f, interp='LINEAR')
        _key(root, 'rotation_euler', f, interp='LINEAR')
    limbs = [(P.get('legL'), 1), (P.get('legR'), -1), (P.get('armL'), -1), (P.get('armR'), 1)]
    for i, f in enumerate(range(f0, f0 + frames + 1, step_frames)):
        sgn = 1 if i % 2 == 0 else -1
        for piv, side in limbs:
            if piv is None:
                continue
            r = piv.rotation_euler.copy()
            r.x = math.radians(swing_deg) * sgn * side
            piv.rotation_euler = r
            _key(piv, 'rotation_euler', f, index=0, interp='LINEAR')
    return {'start_dist': round(d0, 2), 'end_dist': round(d1, 2), 'speed_bu_s': round((d0 - d1) / (frames / FPS), 2)}


def face_set(material, first_png, node_name=None):
    """Point a head material's face Image Texture at the Blockfolk image sequence (face_001.png ...
    face_017.png in EXPRESSIONS order) so face_swaps() can key it. Returns the texture node."""
    nt = material.node_tree
    tex = nt.nodes.get(node_name) if node_name else next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeTexImage')
    img = bpy.data.images.load(first_png, check_existing=True)
    img.source = 'SEQUENCE'
    tex.image = img
    iu = tex.image_user
    iu.use_auto_refresh = True
    iu.use_cyclic = False
    iu.frame_start = -100000     # with duration 1 the picture never depends on the scene frame,
    iu.frame_duration = 1        # only on frame_offset (keyed below)
    iu.frame_offset = 0
    return tex


def face_swaps(material, swaps, node_name=None):
    """T11 face-swap punch: instant (CONSTANT, 1 frame, no in-betweens) expression swaps.
    swaps: [(frame, 'shocked'), (frame, 7), ...]: names from EXPRESSIONS or 1-based indices.
    Swap on the cut or on the stressed word (frame from the word timings), on ~70% of face shots,
    and always on the punchline. Holds 0.5-2 s."""
    nt = material.node_tree
    tex = nt.nodes.get(node_name) if node_name else next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeTexImage')
    path = 'nodes["%s"].image_user.frame_offset' % tex.name
    for frame, e in swaps:
        idx = EXPRESSIONS.index(e) + 1 if isinstance(e, str) else int(e)
        tex.image_user.frame_offset = idx - 1
        _key(nt, path, frame, interp='CONSTANT')
    return tex


def hat_pop(obj, f0, rise=2 * HEAD_H, spin_deg=180.0, frames=6):
    """T12 prop physics gag: a hat (or any prop) flies up 2 head-heights (2.6 BU) spinning 180 deg in
    6 frames (0.2 s), ease-out (QUAD). Seen once; treat as a starting value."""
    loc = obj.location.copy()
    rot = obj.rotation_euler.copy()
    _key(obj, 'location', f0, interp='QUAD', easing='EASE_OUT')
    _key(obj, 'rotation_euler', f0, interp='QUAD', easing='EASE_OUT')
    obj.location = loc + Vector((0, 0, rise))
    r = rot.copy()
    r.y += math.radians(spin_deg)
    obj.rotation_euler = r
    _key(obj, 'location', f0 + frames, interp='QUAD', easing='EASE_OUT')
    _key(obj, 'rotation_euler', f0 + frames, interp='QUAD', easing='EASE_OUT')
    return obj


def puff_rings(loc, f0, count=4, stagger=3, frames=15, r0=0.15 * CHAR_H, r1=0.45 * CHAR_H, facing=(0, -1, 0)):
    """T13 puff rings (1-3 per creature film; seen in 1 film): 3-5 white emissive torus rings (strength 2.0)
    grow from 0.3 H to 0.9 H across (r0 -> r1 radius) and fade alpha 1 -> 0 over 15 frames, staggered 3 frames
    apart, travelling away from the creature along `facing`. Returns the ring objects."""
    m = bpy.data.materials.new('TF puff')
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (1, 1, 1, 1)
    b.inputs['Emission Color'].default_value = (1, 1, 1, 1)
    b.inputs['Emission Strength'].default_value = 2.0
    try:
        m.surface_render_method = 'BLENDED'
    except Exception:
        pass
    rings = []
    face = Vector(facing).normalized()
    q = face.to_track_quat('Z', 'Y').to_euler()
    for i in range(count):
        bpy.ops.mesh.primitive_torus_add(major_radius=1.0, minor_radius=0.12, location=loc)
        o = bpy.context.active_object
        o.name = 'TF ring %d' % i
        o.rotation_euler = q
        mi = m.copy()
        o.data.materials.append(mi)
        fa = f0 + i * stagger
        bsdf = mi.node_tree.nodes['Principled BSDF']
        for f, sc, al, dist in ((fa, r0, 1.0, 0.0), (fa + frames, r1, 0.0, 0.6 * CHAR_H)):
            o.scale = (sc, sc, sc)
            o.location = Vector(loc) + face * dist
            _key(o, 'scale', f, interp='QUAD', easing='EASE_OUT')
            _key(o, 'location', f, interp='QUAD', easing='EASE_OUT')
            bsdf.inputs['Alpha'].default_value = al
            _key(mi.node_tree, 'nodes["Principled BSDF"].inputs[%d].default_value' % list(bsdf.inputs).index(bsdf.inputs['Alpha']), f, interp='LINEAR')
        rings.append(o)
    return rings


def light_pulse(f, loc=(0, 0, 10), peak_w=2000.0, hex_col='#FFB060', rise=2, decay=4, light=None, scene=None):
    """T15 light pulse (1-2 per long film; fireworks, magic, an off-screen explosion; seen in 1-2 films):
    a point light 0 -> peak_w in `rise` frames (2), back to 0 over `decay` frames (4), 6 frames in all,
    lifting the environment about +30 luma. Same curve as `post_craftee-style.py pulse`. peak_w is for a 1 m = 1 unit
    world and is multiplied by UNITS_PER_M**2 (not calibrated by render: check the +30 luma lift on one frame)."""
    if light is None:
        light = practical(loc, 0.0, hex_col, radius=1.0, name='TF pulse', scene=scene)
    d = light.data
    for fr, w, ip, ea in ((f, 0.0, 'LINEAR', 'AUTO'), (f + rise, peak_w, 'QUAD', 'EASE_OUT'), (f + rise + decay, 0.0, 'LINEAR', 'AUTO')):
        d.energy = w * UNITS_PER_M ** 2
        _key(d, 'energy', fr, interp=ip, easing=ea)
    return light


# ----------------------------------------------------------------------------------------------
# Cutting plan and caption cards (S5, S11, T2)
# ----------------------------------------------------------------------------------------------
FORMATS = {
    # target/min/max shot length in seconds (S5): short p10-p90 0.62-1.70, longest 2.1; long 0.6-2.3
    'short': {'target': 1.2, 'min': 0.6, 'max': 2.1, 'card_words': (1, 4), 'card_target': 2.7},
    'long': {'target': 1.4, 'min': 0.6, 'max': 2.3, 'card_words': (1, 3), 'card_target': 1.8},
    'cinematic': {'target': 3.0, 'min': 0.5, 'max': 7.0, 'card_words': (1, 1), 'card_target': 1.0},
}
_FUNCTION_WORDS = set('a an the to of in on at by for and or but so my your his her our their its is was are were be '
                      'with from as that this than then i you he she we they it me him us them'.split())
_SENTENCE_END = re.compile(r'[.!?…]["”’)]*$')
_CLAUSE_END = re.compile(r'[,;:—–-]["”’)]*$')


def _norm(w):
    return re.sub(r"[^a-z0-9']", '', w.lower().replace('’', "'"))


def load_word_timings(word_timings):
    """Accepts a path, the dict {'words': [[w, s, e], ...], 'lines': [[s, e, text], ...]} or a plain list.
    Returns (words, lines)."""
    d = word_timings
    if isinstance(d, str):
        with open(d) as fh:
            d = json.load(fh)
    if isinstance(d, dict):
        words = [(str(w[0]), float(w[1]), float(w[2])) for w in d['words']]
        lines = d.get('lines') or []
    else:
        words = [(str(w[0]), float(w[1]), float(w[2])) for w in d]
        lines = []
    return words, lines


def _boundary_costs(words, lines):
    """Cost of cutting BEFORE word i: 0 = sentence start, 0.15 = clause start or a pause >= 0.25 s,
    0.35 = pause >= 0.12 s, 1.0 = mid-phrase, 1.6 = right after a function word ('the', 'my' ...)."""
    n = len(words)
    end_kind = [None] * n
    toks = []
    for ln in lines:
        text = ln[2] if len(ln) > 2 else ''
        toks += re.findall(r"[\w'’-]+[^\s\w]*", text)
    j = 0
    for i, (w, _, _) in enumerate(words):
        nw = _norm(w)
        for k in range(j, min(j + 4, len(toks))):
            if _norm(re.sub(r'[^\w\'’-]', '', toks[k])) == nw:
                t = toks[k]
                end_kind[i] = 'S' if _SENTENCE_END.search(t) else ('C' if _CLAUSE_END.search(t) else None)
                j = k + 1
                break
    cost = [0.0] * (n + 1)
    for i in range(1, n):
        gap = words[i][1] - words[i - 1][2]
        if end_kind[i - 1] == 'S':
            c = 0.0
        elif end_kind[i - 1] == 'C' or gap >= 0.25:
            c = 0.15
        elif gap >= 0.12:
            c = 0.35
        elif _norm(words[i - 1][0]) in _FUNCTION_WORDS:
            c = 1.6
        else:
            c = 1.0
        cost[i] = c
    return cost, end_kind


def cut_plan(word_timings, fmt='short', fps=FPS, tail=0.4, target=None, min_len=None, max_len=None):
    """T2 hard cut on the phrase: one shot per spoken phrase (~5-6 words), the cut ON the first word's onset
    (tolerance +/-3 frames), no dissolves. Shot lengths (S5): short target 1.2 s within 0.6-2.1 s, long 1.4 s
    within 0.6-2.3 s, cinematic 3.0 s within 0.5-7 s. Dynamic programming over word onsets that prefers
    sentence and clause starts and pauses, and stays near the target length.

    Returns a list of shots: {'shot', 'start', 'end', 'f0', 'f1', 'dur', 'words', 'text', 'cut_cost',
    'technique', 'framing', 'face_swap_frame'} where f0/f1 are inclusive frames at `fps` and frame 0 is the
    first frame. Shot 1 is the whip-in (T1). 'framing' is a suggestion that reproduces the measured mix
    (short: ~18% wide, 15% medium-wide, 50% medium, 17% close). Caption cards: caption_cards(plan, fmt)."""
    P = dict(FORMATS[fmt])
    tgt = target or P['target']
    lo = min_len or P['min']
    hi = max_len or P['max']
    words, lines = load_word_timings(word_timings)
    n = len(words)
    if n == 0:
        return []
    bcost, _ = _boundary_costs(words, lines)
    t_end = words[-1][2] + tail
    onset = [w[1] for w in words] + [t_end]
    onset[0] = 0.0
    INF = float('inf')
    best = [INF] * (n + 1)
    prev = [-1] * (n + 1)
    best[0] = 0.0
    for i in range(1, n + 1):
        for j in range(i - 1, -1, -1):
            dur = onset[i] - onset[j]
            if dur > hi * 1.6 and j < i - 1:
                break
            if best[j] == INF:
                continue
            last = (i == n)
            pen = 0.0
            if dur < lo:
                pen += 25.0 * (lo - dur) / lo + (0.0 if last else 5.0)
            if dur > hi:
                pen += 10.0 + 20.0 * (dur - hi) / hi
            c = best[j] + ((dur - tgt) / tgt) ** 2 * 2.0 + pen + (0.0 if last else bcost[i])
            if c < best[i]:
                best[i], prev[i] = c, j
    cuts = []
    i = n
    while i > 0:
        cuts.append(i)
        i = prev[i]
    cuts = [0] + sorted(cuts)
    framing_cycle = {'short': ['M', 'C', 'W', 'M', 'MW', 'M', 'C', 'M', 'W', 'M', 'MW', 'M'],
                     'long': ['W', 'M', 'C', 'MW', 'M', 'INSERT', 'W', 'C', 'M', 'MW', 'M', 'C'],
                     'cinematic': ['W', 'M', 'C', 'W', 'MW', 'C']}[fmt]
    shots = []
    for k in range(len(cuts) - 1):
        a, b = cuts[k], cuts[k + 1]
        st, en = onset[a], onset[b]
        ws = words[a:b]
        content = [w for w in ws if _norm(w[0]) not in _FUNCTION_WORDS] or ws
        stress = max(content, key=lambda w: (w[2] - w[1]))
        shots.append({
            'shot': k + 1,
            'start': round(st, 3), 'end': round(en, 3), 'dur': round(en - st, 3),
            'f0': int(math.floor(st * fps + 1e-6)), 'f1': int(math.floor(en * fps + 1e-6)) - 1,
            'words': [w[0] for w in ws], 'text': ' '.join(w[0] for w in ws),
            'times': [[round(w[1], 3), round(w[2], 3)] for w in ws],
            'cut_cost': round(bcost[a], 2),
            'technique': 'T1 whip-in' if k == 0 else 'T3 locked',
            'framing': 'M' if k == 0 else framing_cycle[k % len(framing_cycle)],
            'face_swap_frame': int(math.floor(stress[1] * fps)),
        })
    shots[-1]['technique'] = 'T3 locked, punchline: face swap on the last word' if fmt == 'short' else 'ending: T19 zoom-through loop or an emotional close'
    shots[-1]['framing'] = 'C/two-shot'
    shots[-1]['f1'] = int(math.ceil(t_end * fps)) - 1
    return shots


def plan_stats(shots):
    """Quick check of a plan against S5: mean/median/min/max shot length and cuts a minute."""
    d = sorted(s['dur'] for s in shots)
    total = shots[-1]['end'] - shots[0]['start']
    return {'shots': len(d), 'mean': round(sum(d) / len(d), 2), 'median': round(d[len(d) // 2], 2),
            'min': d[0], 'max': d[-1], 'cuts_per_min': round(60.0 * (len(d) - 1) / total, 1),
            'words_per_shot': round(sum(len(s['words']) for s in shots) / len(shots), 1)}


def _chunk(words, lo, hi, target, kw):
    """Split one shot's words into cards (DP): sizes lo..hi near `target`, never ending a card on a function
    word, and closing a card on a marked keyword when there is one."""
    n = len(words)
    INF = float('inf')
    best = [0.0] + [INF] * n
    prev = [0] * (n + 1)
    for i in range(1, n + 1):
        for j in range(max(0, i - hi), i):
            sz = i - j
            if sz < lo or best[j] == INF:
                continue
            last = _norm(words[i - 1])
            c = best[j] + (sz - target) ** 2
            if i < n and last in _FUNCTION_WORDS:
                c += 3.0
            if kw and i < n and last not in kw and any(_norm(w) in kw for w in words[j:i]):
                c += 2.0
            if c < best[i]:
                best[i], prev[i] = c, j
    cuts, i = [], n
    while i > 0:
        cuts.append((prev[i], i))
        i = prev[i]
    return sorted(cuts)


def caption_cards(shots, fmt='short', keywords=None, keyword_colour=None):
    """Caption cards that never cross a cut (the cut lands on a card change, S5/S11).
    short: 1-4 words (mean ~2.7). Line 1 = the white words, line 2 = the KEYWORD in UPPERCASE and the keyword
      colour. The card ends on its keyword, so the reading order never changes ("every kid gets / ONE WISH").
    long: 1-3 words (mean ~1.8, mostly 2), sentence case; keyword cards show the keyword ALONE in the keyword
      colour (~1 card in 3).
    cinematic: 1 word a card, all yellow #ECE648.
    keywords: words to treat as keywords (best: the writer marks them in the script). Without it the last content
    word of a short card is its keyword, and in long films every 3rd single content-word card is a keyword card.
    Times come from the word onsets; a card ends where the next one starts, the last card of a shot at the cut.
    Returns [{'start','end','shot','lines':[{'text','role'}],'keyword_colour'}]; roles map to captions_craftee-style.json."""
    P = FORMATS[fmt]
    kw = set(_norm(k) for k in (keywords or []))
    colour = keyword_colour or (PALETTE['key_yellow_cinematic'] if fmt == 'cinematic' else PALETTE['key_green'])
    lo, hi = P['card_words']
    groups = []
    for s in shots:
        times = [t[0] for t in s.get('times', [])] or [s['start']] * len(s['words'])
        ws = list(zip(s['words'], times))
        for a, b in _chunk(s['words'], lo, hi, P['card_target'], kw):
            g = ws[a:b]
            if fmt == 'long' and kw and len(g) > 1 and any(_norm(w) in kw for w, _ in g):
                groups += [(s, [one]) for one in g]     # a keyword card shows the keyword alone
            else:
                groups.append((s, g))
    cards = []
    for gi, (s, g) in enumerate(groups):
        first_in_shot = gi == 0 or groups[gi - 1][0] is not s
        last_in_shot = gi == len(groups) - 1 or groups[gi + 1][0] is not s
        cs = s['start'] if first_in_shot else g[0][1]
        ce = s['end'] if last_in_shot else groups[gi + 1][1][0][1]
        ws = [w for w, _ in g]
        content_idx = [i for i, w in enumerate(ws) if _norm(w) not in _FUNCTION_WORDS]
        hit_idx = [i for i, w in enumerate(ws) if _norm(w) in kw]
        if fmt == 'short':
            k = hit_idx[-1] if hit_idx else (content_idx[-1] if content_idx else len(ws) - 1)
            white, key = ws[:k], ws[k:]
            lines = ([{'text': ' '.join(white), 'role': 'white'}] if white else []) + \
                    [{'text': ' '.join(key).upper(), 'role': 'keyword'}]
        elif fmt == 'long':
            is_key = (len(ws) == 1 and bool(hit_idx)) if kw else (len(ws) == 1 and bool(content_idx) and len(cards) % 3 == 2)
            lines = [{'text': ws[0].upper(), 'role': 'keyword'}] if is_key else [{'text': ' '.join(ws), 'role': 'white'}]
        else:
            lines = [{'text': ' '.join(ws), 'role': 'keyword'}]
        cards.append({'start': round(cs, 3), 'end': round(ce, 3), 'shot': s['shot'], 'lines': lines, 'keyword_colour': colour})
    return cards


# ----------------------------------------------------------------------------------------------
# Measuring a test still (S3) -- no rendering here; run on a still the builder already rendered
# ----------------------------------------------------------------------------------------------
def _load_rgb(path):
    try:
        from PIL import Image
        import numpy as np
        im = Image.open(path).convert('RGB')
        return np.asarray(im).astype('float32')
    except ImportError:
        import numpy as np
        img = bpy.data.images.load(path, check_existing=False)
        w, h = img.size
        a = np.array(img.pixels[:], dtype='float32').reshape(h, w, 4)[::-1, :, :3] * 255.0
        bpy.data.images.remove(img)
        return a


def measure(path, mode='day'):
    """Measure a rendered still the way the teardown did (S3): mean luma (Rec.601, 0-255) and mean HSV
    saturation at 72x128, luma SD, corner-to-centre luma ratio (vignette check), % clipped pixels.
    Returns the numbers plus pass/fail against TARGETS[mode]."""
    import numpy as np
    a = _load_rgb(path)
    h, w = a.shape[:2]
    ys = (np.arange(128) * h / 128).astype(int)
    xs = (np.arange(72) * w / 72).astype(int)
    s = a[ys][:, xs]
    Y = 0.299 * s[..., 0] + 0.587 * s[..., 1] + 0.114 * s[..., 2]
    mx = s.max(axis=2)
    mn = s.min(axis=2)
    sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-6), 0.0)
    ch, cw = int(128 * 0.15), int(72 * 0.15)
    corners = np.concatenate([Y[:ch, :cw].ravel(), Y[:ch, -cw:].ravel(), Y[-ch:, :cw].ravel(), Y[-ch:, -cw:].ravel()])
    centre = Y[int(128 * 0.35):int(128 * 0.65), int(72 * 0.35):int(72 * 0.65)]
    Yf = 0.299 * a[..., 0] + 0.587 * a[..., 1] + 0.114 * a[..., 2]
    clip = float((Yf >= 250).mean() * 100.0)   # blown whites (a saturated red shirt may clip one channel; fine)
    r = {'luma': round(float(Y.mean()), 1), 'sat': round(float(sat.mean()), 3), 'luma_sd': round(float(Y.std()), 1),
         'corner_ratio': round(float(corners.mean() / max(centre.mean(), 1e-6)), 2), 'clip_pct': round(clip, 2)}
    t = TARGETS.get(mode, {})
    checks = {}
    for k in ('luma', 'sat', 'luma_sd'):
        if k in t:
            checks[k] = t[k][0] <= r[k] <= t[k][1]
    if 'corner_ratio_min' in t:
        checks['no_vignette'] = r['corner_ratio'] >= t['corner_ratio_min']
    if 'clip_max_pct' in t:
        checks['clip'] = r['clip_pct'] <= t['clip_max_pct']
    r['pass'] = checks
    if 'luma' in t:
        r['exposure_change'] = suggest_exposure(r['luma'], sum(t['luma']) / 2)
    return r


def suggest_exposure(measured_luma, target_luma=115.5):
    """Exposure change (stops) that moves a measured mean luma to the target (sRGB -> linear ratio).
    Day target 115.5 (range 106-125). Example: measured 90 -> about +0.75."""
    def lin(v):
        c = max(v, 1.0) / 255.0
        return ((c + 0.055) / 1.055) ** 2.4 if c > 0.04045 else c / 12.92
    return round(math.log2(lin(target_luma) / lin(measured_luma)), 2)


def write_json(obj, path):
    with open(path, 'w') as fh:
        json.dump(obj, fh, indent=1)
    return path
