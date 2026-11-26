"""Comic Sticker Saga (style id `fourth-style`): Blender helper module for builders (bpy 5.3).

Every default below is a number measured on 11-26 from 4 hit reels (see ../STYLE.md, sections 3-5
and the technique catalogue in section 12). Where a value is our own choice and not measured, the
docstring says so.

Use, in a builder's shot script:
    import sys; sys.path.insert(0, '<path>/styles/fourth-style/pack')
    import style_fourth_style as S
    S.apply_look(bpy.context.scene, 'day')          # AgX Punchy, bloom on whites, 1080x1920 @ 30 fps
    S.light_rig('day')                              # one hard sun
    cam = S.camera('s07', 'closeup', loc=(0, -2.2, 1.6), look_at=(0, 0, 1.55))
    S.snap_zoom(cam, f=12)                          # the one shout punch-in of the film
    plan = S.cut_plan('<story>-word-timings.json')  # shot boundaries, cut on caption starts

The style's camera is LOCKED inside a shot (about 90% of shots). Only 1-2 of the moves below are
used per film, each on the biggest beat. There is deliberately NO shake() and NO whip(): the
measured count of camera shakes, whips and swish pans was 0 in all 4 reels. The only noise is
ff_jitter(), and only on a fast-forward repetition beat.

The module imports without bpy (cut_plan and caption_groups are pure Python); the Blender
functions need bpy.
"""
import json
import math
import os

try:
    import bpy
    from mathutils import Vector, Euler
    try:
        from bpy_extras import anim_utils as _anim_utils
    except Exception:  # pragma: no cover
        _anim_utils = None
except ImportError:  # cut_plan() still works without Blender
    bpy = None

STYLE_ID = 'fourth-style'
STYLE_NAME = 'Comic Sticker Saga'
FPS = 30
RES = (1080, 1920)
SENSOR_H = 36.0          # mm, sensor fit VERTICAL (so lens -> vertical FOV)
# OUR scene scale: Cast v2 people are R6 blocks ~6 Blender units tall (kid ~5, adult ~6.3); town models
# are in the same units, so 1 metre ~ 3.3 units. Every distance below is in metres x UNITS_PER_M, and
# point/area light energies scale with UNITS_PER_M ** 2 (inverse-square falloff). Sun strength does not.
UNITS_PER_M = 3.3

# Lens per framing (STYLE.md 4/15): wides ~70 deg vertical FOV (26 mm), close-ups ~40 deg (50 mm).
LENS = {'wide': 26.0, 'medium': 35.0, 'mcu': 42.0, 'closeup': 50.0, 'ecu': 85.0, 'insert': 50.0}
# Measured framing mix (V4, 68 shots). cut_plan() hints follow it.
FRAMING_MIX = {'wide': 0.19, 'medium': 0.35, 'mcu': 0.24, 'closeup': 0.18, 'insert': 0.04}
# What a still from this style should measure (check with post_fourth_style.py check <png>).
TARGETS = {'luma_mean': (95, 110), 'luma_p5_max': 15, 'luma_p95': (220, 232),
           'saturation': (0.40, 0.48), 'avg_shot_s': (1.3, 1.6), 'median_shot_s': 1.3}

PALETTE = {  # scene colours (k-means, 4 reels) -> where they go in our medieval sets
    'ink': '#08080F', 'slate_teal': '#2F4356', 'stone': '#6E8287', 'daylight_grey': '#A8B7C3',
    'sky': '#5EB1D5', 'cream': '#EDE5D1', 'beige': '#C7AE93', 'oak': '#8E603A',
    'torch_amber': '#DF9033', 'grass': '#488F47', 'banner_red': '#5C1D0D', 'rust': '#D05D0F'}


def hex_rgb(h):
    """'#RRGGBB' -> linear RGB tuple (for Blender colour sockets)."""
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return tuple(v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c)


# --------------------------------------------------------------------------- look
# Calibrated on OUR town-square scene (Cycles and EEVEE, Cast v2 cast, physical sky) -- see STYLE.md
# "Calibrated on our scene". Values per kind: AgX look, exposure, sky (world) strength, sun lamp strength.
CAL = {
    'day':      dict(view='AgX', look='High Contrast', exposure=-1.3, sky=0.12, fill=0.04, sun=6.0, sat=0.95),
    'sunset':   dict(view='AgX', look='High Contrast', exposure=-1.0, sky=0.12, fill=0.04, sun=4.0, sat=0.95),
    'interior': dict(view='AgX', look='High Contrast', exposure=0.0, sky=0.30, fill=0.30, sun=None, sat=0.95),
    'night':    dict(view='AgX', look='High Contrast', exposure=0.0, sky=0.15, fill=0.15, sun=None, sat=0.95),
}


SUN = {'el': {'day': 48, 'sunset': 5}, 'rot': 35}   # keep the sky and the sun lamp on the same direction


def sun_rot_for(cam, off=35.0):
    """Sun azimuth (degrees, for apply_look(sun_rot=...) and light_rig(sun_rot=...)) that puts the sun
    behind the camera's shoulder, `off` degrees off the view axis: sunlit fronts, readable faces, crisp
    shadows falling away from camera (this style; measured exteriors are front/three-quarter lit).
    For a camera looking along +Y this is 35, the default. Negative off = the other shoulder."""
    bpy.context.view_layer.update()   # matrix_world is stale right after camera()/aim()
    f = cam.matrix_world.to_3x3() @ Vector((0.0, 0.0, -1.0))
    return math.degrees(math.atan2(f.y, f.x)) + off - 90.0


def apply_look(scene=None, kind='day', exposure=None, bloom=True, look=None, sky_strength=None, sun_disc=False,
               engine='BLENDER_EEVEE', sun_el=None, sun_rot=None, fill_strength=None, view=None, saturation=None):
    """Render and colour settings for this style. kind: 'day' | 'sunset' | 'interior' | 'night'.

    Measured targets (4 reels): mean luma 102 (89-113), luma p5 0-15 (true blacks), p95 222-232,
    HSV saturation 0.42 (0.34-0.46), per-shot luma SD ~60. Natural colour: no saturation boost,
    no haze or fog, no grain, no vignette (a vignette appears only under the question card, in post).
    Settings (defaults in CAL, calibrated on our town square):
      * 1080x1920, 30 fps true frames, motion blur OFF (measured: none). engine 'BLENDER_EEVEE'
        (64 samples, shadows, ray tracing) or 'CYCLES' (our look tests render in Cycles).
      * AgX, look 'Punchy', gamma 1. Exposure -3.0 for day exteriors: the physical sky + a 4.0 sun is
        ~8x brighter than the display range, exactly like the house build (Standard, -3.3).
      * World: exteriors use the physical sky (Nishita = SINGLE_SCATTERING in 5.x) as a WEAK fill
        (strength 0.30) with its sun disc OFF, so the one sun lamp makes the only hard shadow and the
        shade stays dark (true blacks). Turn sun_disc on only when the sun itself is in frame.
        Interiors use #1A2230 at 0.3, night #101828 at 0.15.
      * Compositor: Glare 'Bloom', threshold 0.9 (whites halo a little), then contrast +10.
    Returns a list of warnings (e.g. when this Blender has no AgX config, as in a bare bpy module).
    """
    scene = scene or bpy.context.scene
    cal = CAL.get(kind, CAL['day'])
    warn = []
    r = scene.render
    r.engine = engine
    r.resolution_x, r.resolution_y, r.resolution_percentage = RES[0], RES[1], 100
    r.fps, r.fps_base = FPS, 1.0
    r.use_motion_blur = False
    r.film_transparent = False
    if engine == 'BLENDER_EEVEE':
        ee = scene.eevee
        for attr, val in (('taa_render_samples', 64), ('use_shadows', True), ('use_raytracing', True)):
            try:
                setattr(ee, attr, val)
            except Exception as e:
                warn.append('eevee.%s: %s' % (attr, e))
    # colour management
    vs = scene.view_settings
    want = look or cal['look']
    vt = view or cal.get('view', 'AgX')
    try:
        vs.view_transform = vt
        for lk in (vt + ' - ' + want, want, 'AgX - Medium High Contrast', 'Medium High Contrast'):
            try:
                vs.look = lk          # look names are a dynamic enum: try them, don't list them
                break
            except Exception:
                continue
        else:
            warn.append('no %s look in this OCIO config' % want)
    except Exception as e:
        warn.append('AgX not available here (%s); set View Transform AgX + Look Punchy by hand' % e)
    vs.exposure = cal['exposure'] if exposure is None else exposure
    vs.gamma = 1.0
    try:
        scene.display_settings.display_device = 'sRGB'
    except Exception:
        pass
    # world
    w = bpy.data.worlds.new('SSG_world')
    scene.world = w
    try:
        w.use_nodes = True
    except Exception:
        pass
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld')
    bg = nt.nodes.new('ShaderNodeBackground')      # what the camera sees
    fill = nt.nodes.new('ShaderNodeBackground')    # what lights the set (weaker: dark shade, true blacks)
    lp = nt.nodes.new('ShaderNodeLightPath')
    mix = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(lp.outputs['Is Camera Ray'], mix.inputs[0])
    nt.links.new(fill.outputs[0], mix.inputs[1])
    nt.links.new(bg.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs['Surface'])
    strength = cal['sky'] if sky_strength is None else sky_strength
    fill.inputs['Strength'].default_value = cal['fill'] if fill_strength is None else fill_strength
    if kind in ('day', 'sunset'):
        sky = nt.nodes.new('ShaderNodeTexSky')
        types = [e.identifier for e in sky.bl_rna.properties['sky_type'].enum_items]
        for st in ('MULTIPLE_SCATTERING', 'SINGLE_SCATTERING', 'NISHITA'):
            if st in types:
                sky.sky_type = st      # multiple scattering gives the clear deep-blue sky
                break
        sky.sun_disc = sun_disc
        sky.sun_elevation = math.radians(sun_el if sun_el is not None else SUN['el'][kind if kind == 'sunset' else 'day'])
        sky.sun_rotation = math.radians(sun_rot if sun_rot is not None else SUN['rot'])
        nt.links.new(sky.outputs[0], bg.inputs['Color'])
        nt.links.new(sky.outputs[0], fill.inputs['Color'])
    else:
        bg.inputs['Color'].default_value = (*hex_rgb('#1A2230' if kind == 'interior' else '#101828'), 1)
        fill.inputs['Color'].default_value = bg.inputs['Color'].default_value
    bg.inputs['Strength'].default_value = strength
    # compositor: bloom on whites + contrast +10
    if bloom:
        try:
            _compositor(scene, cal.get('sat', 1.0) if saturation is None else saturation)
        except Exception as e:
            warn.append('compositor: %s' % e)
    return warn


def _compositor(scene, saturation=1.0):
    ng = bpy.data.node_groups.get('SSG_look') or bpy.data.node_groups.new('SSG_look', 'CompositorNodeTree')
    ng.nodes.clear()
    if not any(i.name == 'Image' and getattr(i, 'in_out', '') == 'OUTPUT' for i in ng.interface.items_tree):
        ng.interface.new_socket('Image', in_out='OUTPUT', socket_type='NodeSocketColor')
    rl = ng.nodes.new('CompositorNodeRLayers')
    g = ng.nodes.new('CompositorNodeGlare')
    g.inputs['Type'].default_value = 'Bloom'
    g.inputs['Threshold'].default_value = 0.9   # measured look: halo on every white (paper, plaster)
    g.inputs['Strength'].default_value = 0.4    # = old "mix -0.5"-ish; whites halo, p95 stays 222-232
    g.inputs['Size'].default_value = 0.25       # = old integer size 7 (2^(7-9)); 5.x size is relative
    bc = ng.nodes.new('CompositorNodeBrightContrast')
    bc.inputs['Contrast'].default_value = 10.0
    hs = ng.nodes.new('CompositorNodeHueSat')   # calibration trim only: brings our render to the measured 0.42
    hs.inputs['Saturation'].default_value = saturation
    go = ng.nodes.new('NodeGroupOutput')
    ng.links.new(rl.outputs['Image'], g.inputs['Image'])
    ng.links.new(g.outputs[0], bc.inputs['Image'])
    ng.links.new(bc.outputs[0], hs.inputs['Image'])
    ng.links.new(hs.outputs[0], go.inputs[0])
    scene.compositing_node_group = ng
    scene.render.use_compositing = True
    return ng


# --------------------------------------------------------------------------- lights
def light_rig(kind='day', scene=None, center=(0.0, 0.0, 0.0), scale=UNITS_PER_M, sun=None, energy_mult=1.0,
              sun_el=None, sun_rot=None):
    """Create this style's light set-up and return the light objects.

    Offsets are in metres x `scale` (default UNITS_PER_M = 3.3, our Cast v2 scenes); point/area
    energies are multiplied by scale**2 (inverse-square falloff); Sun strength is not scaled.
    kinds (STYLE.md 3 and 15):
      'day'      one hard Sun, strength 4.0 (CAL), angle 1.5 deg (crisp shadows), #FFF3E2, elevation 48 deg.
      'sunset'   the one golden glare shot per film: Sun 2.5, #FFC27A, elevation 5 deg (colour is ours).
      'interior' daytime hall/corridor: 2 big cool area lights (ceiling panel / tall window) 300 W
                 #EAF2FF, size 2.5 m, plus 1 warm practical (point 100 W, radius 0.1 m, #FFB866).
      'night'    warm practicals only (2 points 120 W #FFB866) + a faint moon Sun 0.3 #9DB4FF.
                 Measured night interiors sit at luma 40-70.
      'insert'   prop/note insert from above: area 500 W #FFF6EA, 1.5 m, 1.6 m above -> luma 175-195.
    Lights are placed relative to `center`; move them to motivate them (a window, a lamp).
    Interior/night/insert energies are physical starting points, not yet calibrated on our sets.
    """
    scene = scene or bpy.context.scene
    cx, cy, cz = center
    k2 = scale * scale * energy_mult
    made = []

    def add(name, ltype, energy, col, loc, rot=(0, 0, 0), **kw):
        ld = bpy.data.lights.new('SSG_' + name, ltype)
        ld.energy = energy
        ld.color = hex_rgb(col)
        for k, v in kw.items():
            setattr(ld, k, v)
        ob = bpy.data.objects.new('SSG_' + name, ld)
        scene.collection.objects.link(ob)
        ob.location = (cx + loc[0] * scale, cy + loc[1] * scale, cz + loc[2] * scale)
        ob.rotation_euler = tuple(math.radians(a) for a in rot)
        made.append(ob)
        return ob

    rot = SUN['rot'] if sun_rot is None else sun_rot
    if kind == 'day':
        el = SUN['el']['day'] if sun_el is None else sun_el
        add('sun', 'SUN', sun or CAL['day']['sun'], '#FFF3E2', (0, 0, 10), (90 - el, 0, rot), angle=math.radians(1.5))
    elif kind == 'sunset':
        el = SUN['el']['sunset'] if sun_el is None else sun_el
        add('sun', 'SUN', sun or CAL['sunset']['sun'], '#FFC27A', (0, 0, 10), (90 - el, 0, rot), angle=math.radians(1.5))
    elif kind == 'interior':
        add('panel', 'AREA', 300 * k2, '#EAF2FF', (0, 0, 3.2), (0, 0, 0), size=2.5 * scale)
        add('window', 'AREA', 300 * k2, '#EAF2FF', (-3.0, 0, 2.2), (0, -70, 0), size=2.5 * scale)
        add('practical', 'POINT', 100 * k2, '#FFB866', (1.8, 1.0, 1.9), shadow_soft_size=0.1 * scale)
    elif kind == 'night':
        add('moon', 'SUN', sun or 0.3, '#9DB4FF', (0, 0, 10), (50, 0, -40), angle=math.radians(1.0))
        add('practical_a', 'POINT', 120 * k2, '#FFB866', (1.5, 0.8, 1.9), shadow_soft_size=0.1 * scale)
        add('practical_b', 'POINT', 120 * k2, '#FFB866', (-1.8, 1.4, 1.6), shadow_soft_size=0.1 * scale)
    elif kind == 'insert':
        add('insert_key', 'AREA', 500 * k2, '#FFF6EA', (0, 0, 1.6), (0, 0, 0), size=1.5 * scale)
    else:
        raise ValueError("kind must be day | sunset | interior | night | insert")
    return made


def light_dim(light, f0, frames=33, to=0.55):
    """Technique 14, light dim inside a held shot (time passing, a lamp going out).
    Measured: luma -30 over 1.1 s (33 frames) at sunset, or -15 over 1.2 s. Under AgX an energy
    factor of ~0.55 gives about -30 luma from a ~100 start (our estimate; check on two stills).
    Keys the light's energy from its current value to value*to, sine ease in-out."""
    ld = light.data if hasattr(light, 'data') and light.type == 'LIGHT' else light
    e0 = ld.energy
    _key(ld, 'energy', None, f0, e0, 'SINE', 'EASE_IN_OUT')
    _key(ld, 'energy', None, f0 + frames, e0 * to, 'LINEAR')
    ld.energy = e0
    return ld


# --------------------------------------------------------------------------- camera
def camera(name, framing='medium', loc=(0, -13.2, 5.3), look_at=(0, 0, 5.0), scene=None, make_active=True):
    """New camera: sensor fit VERTICAL 36 mm, lens from LENS[framing], aimed at look_at, no DOF.
    Measured lenses: wides ~70 deg vertical FOV (26 mm), close-ups ~40 deg (50 mm); no distortion,
    no chromatic aberration, no motion blur, deep focus except over-the-shoulder shots.
    loc/look_at are in scene units (our scenes: 3.3 units a metre; default = 4 m back at eye height)."""
    scene = scene or bpy.context.scene
    cd = bpy.data.cameras.new(name)
    cd.sensor_fit = 'VERTICAL'
    cd.sensor_height = SENSOR_H
    cd.lens = LENS.get(framing, 35.0)
    cd.clip_start, cd.clip_end = 0.1, 5000
    cd.dof.use_dof = False
    cam = bpy.data.objects.new(name, cd)
    scene.collection.objects.link(cam)
    cam.location = loc
    aim(cam, look_at)
    if make_active:
        scene.camera = cam
    return cam


def aim(cam, target):
    d = Vector(target) - Vector(cam.location)
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    return cam


def px_to_m(cam, px, dist):
    """Scene units at distance `dist` (scene units) that move px pixels in a 1080x1920 frame."""
    return px * (SENSOR_H / cam.data.lens * dist) / RES[1]


def ots(cam, focus_obj, fstop=2.8, scale=UNITS_PER_M):
    """Technique 22, over-the-shoulder with a blurred foreground head (1-2 per film): foreground
    hair covers 20-35% of the frame; DOF f/2.8 focused on the far subject (spying, confronting)."""
    cam.data.dof.use_dof = True
    cam.data.dof.focus_object = focus_obj
    cam.data.dof.aperture_fstop = fstop / scale   # Blender treats a unit as a metre: f/2.8 at 3.3 units/m = f/0.85
    return cam


def low_angle(cam, head_loc, dist=2.0 * UNITS_PER_M, up_deg=20.0, azimuth_deg=-90.0):
    """Technique 23, low-angle looming close-up (~1 per film, an authority figure's first threat):
    camera at chest height looking ~20 deg up, 35 mm."""
    a = math.radians(azimuth_deg)
    h = Vector(head_loc)
    cam.location = (h.x + dist * math.cos(a), h.y + dist * math.sin(a), h.z - dist * math.tan(math.radians(up_deg)))
    cam.data.lens = 35.0
    return aim(cam, h)


def top_down(cam, center, height=3.0 * UNITS_PER_M, yaw_deg=0.0, lens=35.0):
    """Technique 24, straight-down shot (~6% of shots): someone knocked flat, a note on a table.
    Also use for technique 21 (prop/note insert, 0.6-1.5 s, bright: light_rig('insert'))."""
    c = Vector(center)
    cam.location = (c.x, c.y, c.z + height)
    cam.rotation_euler = (0.0, 0.0, math.radians(yaw_deg))
    cam.data.lens = lens
    return cam


def eye_ecu(cam, eye_loc, dist=0.55 * UNITS_PER_M, azimuth_deg=-90.0):
    """Technique 25, extreme close-up on the eyes (~1 per film, 0.5-1 s, the biggest emotional beat):
    85 mm, the face decal fills the frame."""
    a = math.radians(azimuth_deg)
    e = Vector(eye_loc)
    cam.location = (e.x + dist * math.cos(a), e.y + dist * math.sin(a), e.z)
    cam.data.lens = LENS['ecu']
    return aim(cam, e)


# ---- keyframe helpers (Blender 5.x slotted actions, with a 4.x fallback)
def _fcurve(idb, path, index):
    ad = idb.animation_data
    if ad is None or ad.action is None:
        return None
    act = ad.action
    if hasattr(act, 'fcurves'):  # Blender 4.x legacy API
        return act.fcurves.find(path, index=index)
    cb = _anim_utils.action_get_channelbag_for_slot(act, ad.action_slot)
    return cb.fcurves.find(path, index=index) if cb else None


def _key(idb, path, index, frame, value, interp='LINEAR', easing='AUTO', handles=None):
    """Set idb.path[index] = value, key it at frame, and set that key's interpolation (it governs
    the segment from this key to the next one)."""
    if index is None:
        setattr(idb, path, value)
        idb.keyframe_insert(path, frame=frame)
        fc = _fcurve(idb, path, 0)
    else:
        getattr(idb, path)[index] = value
        idb.keyframe_insert(path, index=index, frame=frame)
        fc = _fcurve(idb, path, index)
    if fc is not None:
        for kp in fc.keyframe_points:
            if abs(kp.co.x - frame) < 1e-3:
                kp.interpolation = interp
                kp.easing = easing
                if handles:
                    kp.handle_left_type = kp.handle_right_type = handles
        fc.update()
    return fc


def creep(cam, f0, f1, px_per_frame=0.3, dist=4.0 * UNITS_PER_M, direction=(1, 0)):
    """Technique 2, the default: a locked shot with micro-creep (~90% of shots).
    Measured global motion under 1 px a frame at 1080 wide; some shots creep 1-2 px a frame
    (max ~60 px/s). Default 0.3 px a frame (~1% of the frame width over a 1.45 s shot), linear.
    direction is (screen x, screen y); dist = scene units to the subject (default 4 m = 13.2 units)."""
    m = px_to_m(cam, px_per_frame * (f1 - f0), dist)
    mw = cam.matrix_world.to_3x3()
    d = (mw @ Vector((direction[0], direction[1], 0.0))).normalized() * m
    p0 = Vector(cam.location)
    for i in range(3):
        _key(cam, 'location', i, f0, p0[i], 'LINEAR')
        _key(cam, 'location', i, f1, p0[i] + d[i], 'LINEAR')
    cam.location = p0
    return cam


def snap_zoom(cam, f, steps=(0.05, 0.05, 0.05, 0.02)):
    """Technique 4, cut-in plus snap zoom punch (~1 per film) on a shouted line or a shock ("NO!").
    Straight cut to a tighter close-up, then measured scale steps +5%, +5%, +5%, +2% a frame
    (= +17% in 5 frames, 0.15 s), then hold to the end of the shot. No shake, no flash with it.
    Keys the lens every frame (lens ratio = image scale), LINEAR between, so the numbers are exact."""
    L0 = cam.data.lens
    s = 1.0
    _key(cam.data, 'lens', None, f, L0, 'LINEAR')
    for i, st in enumerate(steps, 1):
        s += st
        _key(cam.data, 'lens', None, f + i, L0 * s, 'CONSTANT' if i == len(steps) else 'LINEAR')
    cam.data.lens = L0
    return L0 * s


def _pullout_curve(n_move, ease):
    """Normalised log-scale progress 0..1 per frame: constant speed, then a quad ease-out over the
    last `ease` frames (speed continuous at the join)."""
    lin = n_move - ease
    total = lin + ease / 2.0
    out = []
    for k in range(n_move + 1):
        if k <= lin:
            p = k
        else:
            u = (k - lin) / ease
            p = lin + ease * (u - u * u / 2.0)
        out.append(p / total)
    return out


def pull_out(cam, f0, factor=2.0, hold=6, frames=42, ease=12, mode='lens', target=None):
    """Technique 5, slow pull-out reveal (~1 per film, a transformation reveal).
    Measured in a 2.1 s shot: hold 0.2 s (6 frames), then the picture shrinks ~1.5-2% a frame for
    1.4 s (42 frames, ~2x total), easing out over the last 0.4 s (12 frames); hold 0.15 s; cut.
    mode 'lens' zooms out (85 -> 42 mm for factor 2; start from an 85 mm extreme close-up).
    mode 'dolly' moves the camera back from `target` instead (perspective changes; needs target).
    Keyed every frame along the measured curve (constant log-speed ~1.9%/frame, then ease-out)."""
    prog = _pullout_curve(frames, ease)
    L0 = cam.data.lens
    p0 = Vector(cam.location)
    if mode == 'dolly':
        if target is None:
            raise ValueError("pull_out(mode='dolly') needs target")
        T = Vector(target)
    for k, p in enumerate(prog):
        sc = factor ** p
        f = f0 + hold + k
        if mode == 'lens':
            if k == 0:
                _key(cam.data, 'lens', None, f0, L0, 'CONSTANT')
            _key(cam.data, 'lens', None, f, L0 / sc, 'LINEAR')
        else:
            pos = T + (p0 - T) * sc
            for i in range(3):
                if k == 0:
                    _key(cam, 'location', i, f0, p0[i], 'CONSTANT')
                _key(cam, 'location', i, f, pos[i], 'LINEAR')
    cam.data.lens = L0
    cam.location = p0
    return cam


def orbit(cam, target, f0, deg=30.0, frames=48, name=None):
    """Technique 6, orbit round a hero prop (~1 per film) while the voice lists its features.
    Measured: 25-35 deg arc in 1.6 s (48 frames), ease in and out, lateral parallax 3-13 px a frame.
    Parents the camera to a new empty at `target` (keeping its world position) and keys the empty's
    Z rotation 0 -> deg with Bezier auto-clamped handles (= ease in-out). Negative deg orbits the
    other way. Returns the pivot empty."""
    piv = bpy.data.objects.new(name or (cam.name + '_orbit'), None)
    cam.users_collection[0].objects.link(piv)
    piv.location = target
    bpy.context.view_layer.update()
    mw = cam.matrix_world.copy()
    cam.parent = piv
    cam.matrix_world = mw
    _key(piv, 'rotation_euler', 2, f0, 0.0, 'BEZIER', 'AUTO', 'AUTO_CLAMPED')
    _key(piv, 'rotation_euler', 2, f0 + frames, math.radians(deg), 'BEZIER', 'AUTO', 'AUTO_CLAMPED')
    piv.rotation_euler[2] = 0.0
    return piv


def crane_down(cam, f0, dz=-0.65 * UNITS_PER_M, tilt_deg=-8.5, frames=42, ease_frames=9):
    """Technique 7, crane/tilt down into an over-the-shoulder (~1 per film, a hiding or sneaking beat).
    Measured: ease in over 0.3 s (3 -> 16 px a frame), then a steady 16 px a frame (~500 px/s) for
    1.1 s; foreground hair enters at the bottom; luma drops 85 -> 39 as it goes into shade.
    Defaults give ~600 px of image travel for a subject 4 m (13.2 units) away at 35 mm (0.65 m = 2.15
    units down = ~300 px, 8.5 deg tilt = ~300 px); halve dz for a subject 2 m away. Quad ease-in for the first 9 frames, then linear (speed continuous)."""
    frac = ease_frames / (2.0 * frames - ease_frames)
    z0 = cam.location[2]
    rx0 = cam.rotation_euler[0]
    t = math.radians(tilt_deg)
    for fr, p, it, ez in ((f0, 0.0, 'QUAD', 'EASE_IN'), (f0 + ease_frames, frac, 'LINEAR', 'AUTO'),
                          (f0 + frames, 1.0, 'CONSTANT', 'AUTO')):
        _key(cam, 'location', 2, fr, z0 + dz * p, it, ez)
        _key(cam, 'rotation_euler', 0, fr, rx0 + t * p, it, ez)
    cam.location[2] = z0
    cam.rotation_euler[0] = rx0
    return cam


def jump_cuts(cam, f0, seg=33, scales=(1.0, 1.10, 1.21)):
    """Technique 8, jump-cut reframe (~1 a minute) on repeated or escalating lines
    ("waited... and waited"). Same angle, 5-15% size change per jump, 1.0-1.2 s segments,
    2-3 in a row. Keys the lens with CONSTANT interpolation; each jump is also a cut in the edit
    (cut_plan marks it if you pass jump=True for that shot). Returns the jump frames."""
    L0 = cam.data.lens
    fr = []
    for i, s in enumerate(scales):
        _key(cam.data, 'lens', None, f0 + i * seg, L0 * s, 'CONSTANT')
        fr.append(f0 + i * seg)
    cam.data.lens = L0
    return fr


def ff_jitter(cam, f0, f1, px=27.0, roll_deg=0.9, scale=2.0, seed=0):
    """Technique 9, fast-forward repetition with jitter (rare: 1 in 4 films; "I checked it four
    times"). Measured over 1.6 s: the action at ~3-4x speed (retime the action, e.g. render every
    3rd frame), jitter +-27 px, roll blips +-0.9 deg, brightness pulse 2.9 Hz (that part is in post).
    Adds Noise F-modifiers, limited to [f0, f1], to pitch and yaw (+-px, converted with the lens'
    FOV so it doesn't depend on distance) and to roll (+-roll_deg). Blender noise rarely reaches
    strength/2, so strength = 2.9 x amplitude (tested: peaks ~+-27 px over 48 frames, mean ~13 px)."""
    vfov = 2 * math.atan(SENSOR_H / 2 / cam.data.lens)
    amp = px / RES[1] * vfov
    for idx, a, ph in ((0, amp, 1.3 + seed), (2, amp, 7.1 + seed), (1, math.radians(roll_deg), 4.2 + seed)):
        fc = _key(cam, 'rotation_euler', idx, f0, cam.rotation_euler[idx], 'CONSTANT')
        m = fc.modifiers.new('NOISE')
        m.strength = 2.9 * a
        m.scale = scale
        m.phase = ph
        m.use_restricted_range = True
        m.frame_start, m.frame_end = f0, f1
        m.blend_in = m.blend_out = 1.0
    return cam


# ---- faces: one new expression in almost every close-up (technique 3)
def set_face(head, png):
    """Swap the face decal image on a Cast v2 head (head_mat2 material) for this shot's expression.
    Technique 3: the lead's face changes in almost every close-up (6-8 reaction close-ups a minute,
    8-12 expressions a film). Faces change between shots; inside a shot only a 1-frame swap."""
    img = bpy.data.images.load(png, check_existing=True)
    n = 0
    for slot in head.material_slots:
        m = slot.material
        if m and m.node_tree:
            for nd in m.node_tree.nodes:
                if nd.type == 'TEX_IMAGE':
                    nd.image = img
                    n += 1
    return n


def face_swaps(head, swaps):
    """In-shot 1-frame face swaps on a reaction beat: swaps = [(frame, png), ...] sorted by frame.
    Registers a frame_change_pre handler (works for scripted renders; re-run after reopening a file)."""
    swaps = sorted(swaps)
    name = head.name

    def _h(scene, *a):
        ob = bpy.data.objects.get(name)
        if ob is None:
            return
        cur = None
        for fr, p in swaps:
            if scene.frame_current >= fr:
                cur = p
        if cur:
            set_face(ob, cur)
    _h.__name__ = 'ssg_face_' + name
    bpy.app.handlers.frame_change_pre[:] = [h for h in bpy.app.handlers.frame_change_pre
                                            if getattr(h, '__name__', '') != _h.__name__]
    bpy.app.handlers.frame_change_pre.append(_h)
    return _h


# --------------------------------------------------------------------------- cut plan (pure Python)
_FUNC = set('a an the of to in on at my his her their its our your and but or so is was are were '
            'be with for from by as if than that this then into onto over under up out off no not every'.split())
_PUNCT = ',.!?;:'


def _load_words(word_timings):
    if isinstance(word_timings, str):
        with open(word_timings) as fh:
            word_timings = json.load(fh)
    lines = []
    if isinstance(word_timings, dict):
        words = word_timings['words']
        lines = word_timings.get('lines', [])
    else:
        words = word_timings
    W = [{'w': str(w[0]), 's': float(w[1]), 'e': float(w[2]), 'punct': '', 'line_start': False} for w in words]
    # sentence starts and punctuation from our "lines" ([start, end, text])
    for ls, le, text in lines:
        idx = [k for k, x in enumerate(W) if ls - 0.02 <= x['s'] < le + 0.02]
        if not idx:
            continue
        W[idx[0]]['line_start'] = True
        toks = text.split()
        if len(toks) == len(idx):
            for k, tok in zip(idx, toks):
                tail = tok.rstrip('"\'')
                W[k]['punct'] = tail[-1] if tail and tail[-1] in _PUNCT else ''
                W[k]['quote_open'] = tok.startswith('"')
                W[k]['quote_close'] = tok.rstrip(_PUNCT).endswith('"') or tok.endswith('"')
    if not lines:
        for x in W:
            if x['w'] and x['w'][-1] in _PUNCT:
                x['punct'] = x['w'][-1]
        if W:
            W[0]['line_start'] = True
    return W


def caption_groups(word_timings, max_words=3, pause=0.15):
    """Captions for this style: 1-3 words (measured mean 1.9), median 0.5 s, ~1.9 changes a second.
    Breaks after punctuation, before a new line, at a pause >= 0.15 s, at 3 words, at 2 words once the
    group lasts 0.22 s or the next word is a little word, or at 1 word lasting 0.5 s (never ending a
    group on a little word like 'the' or 'of'). Tested on 3 of our stories (Sphinx, Moth Wings, Dungeon
    Master): mean 2.05-2.13 words, median 0.47-0.57 s, cut_plan average shot 1.53-1.63 s.
    Returns [{'text','start','end','words','line_start','after_punct','pause_before'}]."""
    W = _load_words(word_timings)
    out, cur = [], []

    def close():
        if cur:
            out.append({'text': ' '.join(x['w'] for x in cur).upper(), 'start': cur[0]['s'], 'end': cur[-1]['e'],
                        'words': len(cur), 'line_start': cur[0]['line_start'], 'punct': cur[-1]['punct']})
            cur.clear()

    for k, x in enumerate(W):
        if cur and x['line_start']:
            close()
        cur.append(x)
        nxt = W[k + 1] if k + 1 < len(W) else None
        gap = (nxt['s'] - x['e']) if nxt else 9
        little = x['w'].lower().strip(_PUNCT + '"\'') in _FUNC
        dur = x['e'] - cur[0]['s']
        if x['punct'] or gap >= pause or len(cur) >= max_words or (nxt and nxt['line_start']):
            close()
        elif len(cur) == 2 and not little and (dur >= 0.22 or (nxt and nxt['w'].lower() in _FUNC)):
            close()
        elif len(cur) == 1 and dur >= 0.5 and not little:
            close()
    close()
    for i, c in enumerate(out):
        c['after_punct'] = bool(i and out[i - 1]['punct'])
        c['pause_before'] = round(c['start'] - out[i - 1]['end'], 3) if i else 0.0
    return out


def cut_plan(word_timings, fps=FPS, target=1.45, min_shot=0.4, max_shot=3.1, first=(1.5, 2.4),
             lead=0.0, card=6.0, card_cuts=3, tail=0.3):
    """Shot boundaries for this style from our <story>-word-timings.json (or its 'words' list).

    Rule (measured, 4 reels): every cut is a hard cut ON A CAPTION BOUNDARY, preferably where a
    sentence or phrase starts (the phrase that names something new). Average shot 1.45 s, median
    1.3 s (~41 cuts a minute), 0.4-3.1 s in the story, opening shot 1.5-2.4 s, ~3 caption changes
    and ~5 words per shot. The film ends on the question card (default 6 s, measured 4-8 s) with
    2-4 cuts underneath it.
    A small dynamic programme picks caption starts so shot lengths sit near `target` (cost
    ((dur - target) / 0.6)^2), plus a cut cost of 0 at a line start, 0.3 after punctuation, 0.5 after
    a pause >= 0.12 s and 1.5 mid-phrase. lead = seconds the cut comes BEFORE the caption (measured 0).

    Returns a list of dicts: {i, kind ('story' | 'card_bg'), start, end, dur, f0, f1, frames, text,
    captions, framing (a hint following the measured mix; the builder decides per beat)}.
    """
    caps = caption_groups(word_timings)
    n = len(caps)
    if n == 0:
        return []
    end_t = caps[-1]['end'] + tail

    def t_at(j):
        return 0.0 if j == 0 else (end_t if j == n else max(0.0, caps[j]['start'] - lead))

    def pen(j):
        if j == n:
            return 0.0
        c = caps[j]
        if c['line_start']:
            return 0.0
        if c['after_punct']:
            return 0.3
        if c['pause_before'] >= 0.12:
            return 0.5
        return 1.5

    INF = float('inf')
    best = [INF] * (n + 1)
    back = [-1] * (n + 1)
    best[0] = 0.0
    for j in range(1, n + 1):
        for i in range(max(0, j - 10), j):
            if best[i] == INF:
                continue
            d = t_at(j) - t_at(i)
            lo, hi = (first if i == 0 else (min_shot, max_shot))
            if j == n:
                hi = max(hi, 3.6)        # the last story shot may run into the card a little
            if d < lo or d > hi:
                continue
            c = best[i] + ((d - target) / 0.6) ** 2 + pen(j)
            if c < best[j]:
                best[j], back[j] = c, i
    if best[n] == INF:  # relax: no feasible split (very slow or very fast read); fall back to 1 shot per line
        bounds = [0] + [j for j in range(1, n) if caps[j]['line_start']] + [n]
    else:
        bounds, j = [n], n
        while j > 0:
            j = back[j]
            bounds.append(j)
        bounds = bounds[::-1]
    cycle = ['medium', 'closeup', 'mcu', 'medium', 'wide', 'mcu', 'medium', 'closeup']
    shots = []
    for k in range(len(bounds) - 1):
        i, j = bounds[k], bounds[k + 1]
        s, e = t_at(i), t_at(j)
        new_scene = k == 0 or (caps[i]['line_start'] and caps[i]['pause_before'] >= 0.6)
        fr = 'wide' if new_scene else cycle[k % len(cycle)]
        if shots and fr == shots[-1]['framing']:
            fr = 'closeup' if fr != 'closeup' else 'mcu'
        shots.append({'i': k, 'kind': 'story', 'start': round(s, 3), 'end': round(e, 3), 'dur': round(e - s, 3),
                      'text': ' / '.join(c['text'] for c in caps[i:j]), 'captions': j - i, 'framing': fr})
    # question card: 2-4 background cuts under it
    seg = card / max(1, card_cuts)
    for q in range(card_cuts):
        s = end_t + q * seg
        shots.append({'i': len(shots), 'kind': 'card_bg', 'start': round(s, 3), 'end': round(s + seg, 3),
                      'dur': round(seg, 3), 'text': '(question card up)', 'captions': 0,
                      'framing': ['wide', 'medium', 'closeup', 'mcu'][q % 4]})
    for sh in shots:  # frame-exact, contiguous
        sh['f0'] = int(round(sh['start'] * fps))
        sh['f1'] = int(round(sh['end'] * fps))
        sh['frames'] = sh['f1'] - sh['f0']
    return shots


def plan_stats(shots):
    """Average/median shot, cuts a minute and longest hold of the story part, to compare with the
    measured targets (1.45 s / 1.3 s / ~41 a minute / <= 3.1 s)."""
    d = sorted(s['dur'] for s in shots if s['kind'] == 'story')
    if not d:
        return {}
    tot = sum(d)
    return {'shots': len(d), 'avg': round(tot / len(d), 3), 'median': d[len(d) // 2],
            'cuts_per_min': round(60 * len(d) / tot, 1), 'longest': d[-1], 'shortest': d[0]}


if __name__ == '__main__':  # quick plan from the command line: python3 -I style_fourth_style.py <word-timings.json>
    import sys
    if len(sys.argv) > 1:
        sh = cut_plan(sys.argv[1])
        for s in sh:
            print('%3d %-7s %6.2f-%6.2f %4.2fs f%4d-%4d %-7s %s' % (s['i'], s['kind'], s['start'], s['end'], s['dur'],
                                                                 s['f0'], s['f1'], s['framing'], s['text']))
        print(plan_stats(sh))
