"""Bright Snap Cut (`bright-cut`) style pack for Blender 5.3 (bpy).

Measured from five cannonanimates reels: 21M, 15M, 7.9M, 6.5M and 5.4M views.
URLs and the full numbers are in ../STYLE.md. Method only: none of their stories,
characters or footage are used here.

Typical use, inside Blender or with `python3 -I` and the bpy module:

    import sys; sys.path.insert(0, "/path/to/styles/bright-cut/pack")
    import style_bright_cut as bc
    bc.apply_look(scene)                      # noon look, Standard view, +0.4 EV, glare
    bc.light_rig("noon", cam=cam)             # sun 4.5, angle 3 deg, elev 55, azim 35
    shots = bc.cut_plan("story-word-timings.json")    # ~0.7 s shots on phrase starts + stressed words
    caps  = bc.caption_plan("story-word-timings.json") # one caption per phrase, starts 2 f before the cut
    bc.whip_in(cam, f0=0)                     # T3
    bc.push(cam, 1, 22)                       # T1, 18 %/s, linear, cut mid-move
    bc.shake(cam, 300, 306, px_at_1080=8)     # T6 impact micro-shake

Every default below carries the measured number it comes from (see STYLE.md section 14).
cut_plan / caption_plan / conversions work without bpy too.
"""
import json
import math
import re

try:  # bpy is optional for the planning helpers
    import bpy
    from mathutils import Matrix, Vector
except ImportError:  # pragma: no cover
    bpy = None

# ---------------------------------------------------------------- constants
FPS = 30
RES = (1080, 1920)
UNITS_PER_M = 3.3                     # our scenes: Cast v2 adult ~6.3 units, kid ~5, cottages 12-16 (1 m ~= 3.3 units)
SENSOR_MM = 36.0                      # sensor_fit AUTO -> 36 mm spans the 1920 side
H_SENSOR_MM = SENSOR_MM * RES[0] / RES[1]   # 20.25 mm across the 1080 side

LENS = {"wide": 26, "medium": 35, "close": 50, "ecu": 80}   # 26 mm ~= Roblox 70 deg vertical FOV

PALETTE = {
    "sky": "#8BD0F4", "cloud": "#E2E9E9", "pale_stone": "#C2D2E3", "cobble": "#A2ABBB",
    "slate": "#4C586A", "ink": "#13121B", "timber": "#D4B588", "brick": "#874137",
    "grass": "#76C784", "grass_shade": "#4E8F52", "key_red": "#E0262A", "power": "#27C4D0",
    "gold": "#D4BE43", "playful_yellow": "#F2D33A", "night_sky": "#1B1830",
}

MEASURED = {
    "avg_shot_s": 0.70,            # pooled median; range 0.56-0.94 over 5 videos
    "median_shot_s": (0.67, 0.80),
    "max_shot_s": 2.6,             # longest shot seen in any video
    "insert_shot_s": (0.13, 0.37), # shortest 10 %
    "phrase_cut_share": 0.96,      # 95-97 % of phrases start on a cut
    "cut_after_word_f": 1,         # median +0.6 to +1.6 frames after the word onset
    "caption_lead_f": 2,           # caption changes 1-2 f before the picture cut
    "push_rate_per_s": 0.18,       # median |zoom| 16-22 %/s
    "drift_px_per_s": 190,         # median drift 170-205 px/s at 1080 wide
    "moving_shot_share": 0.87,     # 85-90 % of shots move
    "push_share": 0.50, "pull_share": 0.37, "slide_share": 0.13,
    "brightness": (135, 155), "hsv_sat": (0.30, 0.42),
    "words_per_s": (3.5, 4.2),
}

STOPWORDS = set("""a an the and or but if then so to of in on at by for with from up down out over under into onto
is are was were be been being am do does did have has had i me my mine you your he him his she her it its we
us our they them their this that these those there here not no yes all any some every each just very too also
as than when while who whom whose which what where why how can could would should will shall may might must
one own off again""".split())

DANGER_WORDS = set("""dead deadly die died kill killed never ever gone vanished alone fire burn burned broke broken
cursed curse dragon monster blood war attack attacked last only nobody everyone gone stronger strongest weakest
weak king knelt kneel bowed""".split())


# ---------------------------------------------------------------- small utils
def hex_to_linear(h):
    """'#RRGGBB' (sRGB) -> linear RGB tuple for Blender colour sockets."""
    h = h.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return tuple(out)


def hfov_rad(lens_mm):
    """Horizontal FOV of a 1080x1920 frame (sensor_fit AUTO, 36 mm): 32.3 deg at 35 mm."""
    return 2 * math.atan(H_SENSOR_MM / 2 / lens_mm)


def px_to_rad(px_at_1080, lens_mm=35):
    """Screen pixels (at 1080 wide) -> camera rotation in radians. 1 px ~= 0.03 deg at 35 mm."""
    return px_at_1080 / RES[0] * hfov_rad(lens_mm)


def px_to_m(px_at_1080, dist_m=3.0, lens_mm=35):
    """Screen pixels -> metres of lateral camera travel at subject distance dist_m."""
    width = dist_m * H_SENSOR_MM / lens_mm      # 1.74 m wide at 3 m with 35 mm
    return px_at_1080 / RES[0] * width


def m_to_units(m):
    """Real metres -> our Blender units (UNITS_PER_M = 3.3: Cast v2 adult ~6.3 units tall)."""
    return m * UNITS_PER_M


def _need_bpy():
    if bpy is None:
        raise RuntimeError("this function needs Blender's bpy module")


def _scene(scene=None):
    _need_bpy()
    return scene or bpy.context.scene


def _fcurves(idblock):
    """All F-curves of an ID (works with Blender 5 layered actions and older ones)."""
    ad = idblock.animation_data
    if not ad or not ad.action:
        return []
    act = ad.action
    if hasattr(act, "fcurves") and not hasattr(act, "layers"):
        return list(act.fcurves)
    try:
        from bpy_extras import anim_utils
        cb = anim_utils.action_get_channelbag_for_slot(act, ad.action_slot)
        return list(cb.fcurves) if cb else []
    except Exception:
        out = []
        for layer in act.layers:
            for strip in layer.strips:
                for cb in strip.channelbags:
                    out += list(cb.fcurves)
        return out


def _fcurve(idblock, path, index):
    for fc in _fcurves(idblock):
        if fc.data_path == path and fc.array_index == index:
            return fc
    return None


def _set_interp(idblock, path, frames, interp="LINEAR", easing="AUTO", indices=(0, 1, 2)):
    """Set interpolation of the keys on `frames` (list) for data_path `path`."""
    fs = set(int(round(f)) for f in frames)
    for fc in _fcurves(idblock):
        if fc.data_path != path or fc.array_index not in indices:
            continue
        for kp in fc.keyframe_points:
            if int(round(kp.co[0])) in fs:
                kp.interpolation = interp
                if hasattr(kp, "easing"):
                    kp.easing = easing


def _cam_quat(cam):
    """World rotation of the camera. Uses matrix_basis (always current) when unparented;
    otherwise refreshes the depsgraph first so matrix_world is not stale."""
    if cam.parent is None:
        return cam.matrix_basis.to_quaternion()
    bpy.context.view_layer.update()
    return cam.matrix_world.to_quaternion()


def _forward(cam):
    """Camera view direction (local -Z) in world space."""
    return (_cam_quat(cam) @ Vector((0, 0, -1))).normalized()


def _right(cam):
    return (_cam_quat(cam) @ Vector((1, 0, 0))).normalized()


def _up(cam):
    return (_cam_quat(cam) @ Vector((0, 1, 0))).normalized()


def _key_loc(cam, frame, loc):
    cam.location = loc
    cam.keyframe_insert("location", frame=frame)


def _lens(cam):
    return cam.data.lens if cam.type == "CAMERA" else 35.0


# ---------------------------------------------------------------- look
def apply_look(scene=None, engine="BLENDER_EEVEE", exposure=0.0, sky=PALETTE["sky"], fill=0.4,
               horizon="#D6EEFA", bloom=True, glare_strength=0.12, sat_boost=1.05, night=False):
    """Noon "bright toy town" look (STYLE.md sections 3 and 15), CALIBRATED on our town-square
    test scene (Cast v2 kids + guard, a1_* town models, Cycles; main's look_test.py):
    luma 147 / HSV sat 0.34 at 270x480 against targets 135-155 / 0.30-0.42.

    - View Transform Standard, Look None, Exposure 0.0 (the old +0.4 gave luma 186), Gamma 1.0.
    - World split with Light Path "Is Camera Ray": the CAMERA sees the sky at its true colour
      (zenith #8BD0F4, horizon #D6EEFA, strength 2^-exposure), while the set is lit by a separate
      fill of `fill` (0.4). A single bright world washed the frame out (sky clipped to #ABFEFF,
      shadows flat).
    - Glare Fog Glow threshold 1.0, size 0.5, strength 0.12 ("barely there" bloom), then a gentle
      saturation trim of 1.05 (Hue/Sat node); 1.12 overshoots to 0.39.
    - 1080x1920, 30 fps, film filter 1.5 px, motion blur shutter 0.5 (whip_in keys 1.0).
    night=True: sky #1B1830, fill 0.12, exposure 0.0 (the Tag video's night shots: luma ~60-110).
    """
    sc = _scene(scene)
    r = sc.render
    try:
        r.engine = engine
    except Exception:
        r.engine = "BLENDER_EEVEE_NEXT"
    r.resolution_x, r.resolution_y, r.resolution_percentage = RES[0], RES[1], 100
    r.fps, r.fps_base = FPS, 1.0
    r.filter_size = 1.5
    r.use_motion_blur = True
    r.motion_blur_shutter = 0.5
    vs = sc.view_settings
    try:
        vs.view_transform = "Standard"
        vs.look = "None"
    except Exception as e:  # headless builds without OCIO looks
        print("bright-cut: could not set view transform:", e)
    vs.exposure = 0.0 if night else exposure
    vs.gamma = 1.0
    try:
        ee = sc.eevee
        ee.use_raytracing = True
        ee.use_shadows = True
    except Exception:
        pass
    # world: the camera sees the sky at its true colour (#8BD0F4 after exposure), while the light it
    # throws on the set is a separate, weaker "fill" so shadows stay real (frame p5 ~32 in the reference).
    world = sc.world or bpy.data.worlds.new("BC_world")
    sc.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    lp = nt.nodes.new("ShaderNodeLightPath")
    bg_cam = nt.nodes.new("ShaderNodeBackground")
    bg_fill = nt.nodes.new("ShaderNodeBackground")
    mix = nt.nodes.new("ShaderNodeMixShader")
    col = PALETTE["night_sky"] if night else sky
    for bg in (bg_cam, bg_fill):
        bg.inputs["Color"].default_value = (*hex_to_linear(col), 1.0)
    if not night and horizon:
        # camera sky: pale horizon -> #8BD0F4 from ~25 deg up (their skies are lighter at the horizon)
        tc = nt.nodes.new("ShaderNodeTexCoord")
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        ramp = nt.nodes.new("ShaderNodeValToRGB")
        ramp.color_ramp.elements[0].position = 0.0
        ramp.color_ramp.elements[0].color = (*hex_to_linear(horizon), 1.0)
        ramp.color_ramp.elements[1].position = 0.42
        ramp.color_ramp.elements[1].color = (*hex_to_linear(col), 1.0)
        nt.links.new(tc.outputs["Generated"], sep.inputs[0])
        nt.links.new(sep.outputs["Z"], ramp.inputs["Fac"])
        nt.links.new(ramp.outputs["Color"], bg_cam.inputs["Color"])
    bg_cam.inputs["Strength"].default_value = 2.0 ** (-vs.exposure)     # displays exactly the hex colour
    bg_fill.inputs["Strength"].default_value = (0.12 if night else fill)
    nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
    nt.links.new(bg_fill.outputs[0], mix.inputs[1])
    nt.links.new(bg_cam.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    # compositor glare
    if bloom:
        ng = bpy.data.node_groups.get("BC_comp") or bpy.data.node_groups.new("BC_comp", "CompositorNodeTree")
        ng.nodes.clear()
        if not any(s.in_out == "OUTPUT" for s in ng.interface.items_tree if hasattr(s, "in_out")):
            ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        rl = ng.nodes.new("CompositorNodeRLayers")
        gl = ng.nodes.new("CompositorNodeGlare")
        gl.inputs["Type"].default_value = "Fog Glow"
        gl.inputs["Threshold"].default_value = 1.0
        gl.inputs["Size"].default_value = 0.5
        gl.inputs["Strength"].default_value = glare_strength
        out = ng.nodes.new("NodeGroupOutput")
        ng.links.new(rl.outputs["Image"], gl.inputs["Image"])
        last = gl.outputs["Image"]
        if abs(sat_boost - 1.0) > 1e-3:
            hs = ng.nodes.new("CompositorNodeHueSat")
            hs.inputs["Saturation"].default_value = sat_boost
            ng.links.new(last, hs.inputs["Image"])
            last = hs.outputs["Image"]
        ng.links.new(last, out.inputs[0])
        try:
            sc.compositing_node_group = ng
        except Exception as e:
            print("bright-cut: compositor not set:", e)
    return {"view_transform": vs.view_transform, "exposure": vs.exposure, "engine": r.engine}


def light_rig(kind="noon", scene=None, cam=None, elevation_deg=55, azimuth_off_deg=35, sun_strength=4.5,
              window_loc=None):
    """Lights for the style. Returns the created light objects.

    kind="noon" (4 of 5 videos): one Sun, strength 4.5 (calibrated: with apply_look's fill 0.4 this
      gives luma ~147 on our town square), colour #FFF3E2, angle 3 deg (soft but real shadows),
      elevation 55 deg, azimuth 35 deg off the camera axis so faces are lit from the front-side.
      Fill = the world only. No rim lights. Sun lights have no falloff, so scene scale doesn't matter.
    kind="night" (Tag video): cool moon Sun 0.8 #9DB4FF angle 1 deg + warm window point light,
      60 W at real scale = 60 x 3.3^2 ~= 650 W in our units (point lights fall off with distance^2);
      pair with apply_look(night=True). Pass window_loc in scene units.
    """
    sc = _scene(scene)
    yaw = 0.0
    if cam is not None:
        f = _forward(cam)
        yaw = math.atan2(f.y, f.x)
    made = []

    def sun(name, strength, color, angle_deg, elev, az):
        ld = bpy.data.lights.new(name, "SUN")
        ld.energy = strength
        ld.color = hex_to_linear(color)
        ld.angle = math.radians(angle_deg)
        ob = bpy.data.objects.new(name, ld)
        sc.collection.objects.link(ob)
        # light shines along its local -Z; point it from (az, elev) toward the scene
        d = Vector((math.cos(az) * math.cos(elev), math.sin(az) * math.cos(elev), math.sin(elev)))
        ob.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
        ob.location = d * 20
        made.append(ob)
        return ob

    # the sun sits behind the camera, offset by azimuth_off_deg, so it lights the subject's front-side
    az = yaw + math.pi + math.radians(azimuth_off_deg)
    if kind == "noon":
        sun("BC_sun", sun_strength, "#FFF3E2", 3.0, math.radians(elevation_deg), az)
    elif kind == "night":
        sun("BC_moon", 0.8, "#9DB4FF", 1.0, math.radians(40), yaw + math.radians(150))
        ld = bpy.data.lights.new("BC_window", "POINT")
        ld.energy = 60 * UNITS_PER_M ** 2          # 60 W at real scale; falloff is in scene units
        ld.color = hex_to_linear("#FFB86B")
        ld.shadow_soft_size = 0.25 * UNITS_PER_M
        ob = bpy.data.objects.new("BC_window", ld)
        sc.collection.objects.link(ob)
        ob.location = window_loc or (2.0 * UNITS_PER_M, 2.0 * UNITS_PER_M, 2.5 * UNITS_PER_M)
        made.append(ob)
    else:
        raise ValueError("kind must be 'noon' or 'night'")
    return made


def make_camera(name="BC_cam", size="medium", loc=(0, -10, 5), target=(0, 0, 4), scene=None):
    """Camera with the style's lens for a shot size: wide 26 / medium 35 / close 50 / ecu 80 mm.
    Depth of field only for close and ecu (f/2.8 focused on the target)."""
    sc = _scene(scene)
    cd = bpy.data.cameras.new(name)
    cd.lens = LENS.get(size, size if isinstance(size, (int, float)) else 35)
    cd.sensor_fit = "AUTO"
    cd.sensor_width = SENSOR_MM
    ob = bpy.data.objects.new(name, cd)
    sc.collection.objects.link(ob)
    ob.location = Vector(loc)
    d = Vector(target) - ob.location
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    if size in ("close", "ecu"):
        cd.dof.use_dof = True
        cd.dof.aperture_fstop = 2.8 / UNITS_PER_M      # = f/2.8 at real scale in a 3.3 units/m scene
        cd.dof.focus_distance = d.length
    return ob


# ---------------------------------------------------------------- camera techniques
def push(cam, f0, f1, pct=None, rate=MEASURED["push_rate_per_s"], dist=3.0, lead=0):
    """T1 breathing push-in. Constant speed (LINEAR keys) and the cut comes mid-move.

    pct: total subject-scale growth over the shot (0.2 = +20 %). Default = rate x duration,
         rate 0.18/s from the measured median 16-22 %/s.
    dist: camera-to-subject distance in METRES (converted with UNITS_PER_M = 3.3; scale ~ 1/distance).
    lead: T15 snap-start. The move starts `lead` frames before f0 (keys at f0-lead), so the
          shot opens already moving. 34-43 % of fast frames sit 0-3 f after a cut.
    """
    dur = (f1 - f0) / FPS
    if pct is None:
        pct = rate * dur
    start = cam.location.copy()
    fwd = _forward(cam)
    d_u = m_to_units(dist)
    travel = d_u - d_u / (1.0 + pct)            # forward units to grow scale by (1+pct)
    a = f0 - lead
    k = travel / max(1, (f1 - a))
    _key_loc(cam, a, start)
    _key_loc(cam, f1, start + fwd * (k * (f1 - a)))
    _set_interp(cam, "location", [a, f1], "LINEAR")
    return {"travel_units": round(k * (f1 - a), 3), "pct": round(pct, 3)}


def pull(cam, f0, f1, pct=None, rate=MEASURED["push_rate_per_s"], dist=3.0, lead=0):
    """T1 pull-out (31-42 % of shots). Same numbers as push, moving backwards."""
    dur = (f1 - f0) / FPS
    if pct is None:
        pct = rate * dur
    start = cam.location.copy()
    back = -_forward(cam)
    travel = m_to_units(dist) * pct
    a = f0 - lead
    _key_loc(cam, a, start)
    _key_loc(cam, f1, start + back * travel)
    _set_interp(cam, "location", [a, f1], "LINEAR")
    return {"travel_units": round(travel, 3), "pct": round(pct, 3)}


def drift(cam, f0, f1, px_per_s=MEASURED["drift_px_per_s"], direction=(1, 0), dist=3.0, lead=0):
    """T2 lateral slide at constant speed. 190 px/s = measured median drift 170-205 px/s
    (p25 95, p90 585). direction is in screen space: (1,0) right, (0,1) up."""
    lens = _lens(cam)
    dur = (f1 - f0 + lead) / FPS
    m = m_to_units(px_to_m(px_per_s * dur, dist, lens))
    v = (_right(cam) * direction[0] + _up(cam) * direction[1])
    if v.length:
        v.normalize()
    start = cam.location.copy()
    _key_loc(cam, f0 - lead, start)
    _key_loc(cam, f1, start + v * m)
    _set_interp(cam, "location", [f0 - lead, f1], "LINEAR")
    return {"travel_units": round(m, 3)}


def whip_in(cam, f0=0, yaw_deg=30, frames=5, scene=None, shutter_frames=4):
    """T3 frame-0 whip. The camera starts yaw_deg off and decelerates (EXPO ease-out) into its
    keyed pose by f0+frames. Measured: blur on f0-f3, settled by f4-f7, f0 blur 60-100 px.
    Motion-blur shutter is keyed to 1.0 on the first `shutter_frames` frames, then back to 0.5.
    Seen in 4 of 5 videos. Pair with a whoosh starting 2 f before frame 0 (post_bright_cut.py)."""
    sc = _scene(scene)
    base = cam.rotation_euler.copy()
    off = base.copy()
    off.z += math.radians(yaw_deg)
    cam.rotation_euler = off
    cam.keyframe_insert("rotation_euler", frame=f0)
    cam.rotation_euler = base
    cam.keyframe_insert("rotation_euler", frame=f0 + frames)
    _set_interp(cam, "rotation_euler", [f0], "EXPO", "EASE_OUT")
    r = sc.render
    r.motion_blur_shutter = 1.0
    r.keyframe_insert("motion_blur_shutter", frame=f0)
    r.keyframe_insert("motion_blur_shutter", frame=f0 + shutter_frames - 1)
    r.motion_blur_shutter = 0.5
    r.keyframe_insert("motion_blur_shutter", frame=f0 + shutter_frames)
    return {"settle_frame": f0 + frames}


def crash_push(cam, f0, f1, factor=2.5, dist=3.0):
    """T4 crash push-in to an extreme close-up. Speeds up into the end (QUAD ease-in).
    Measured: 20-26 f (0.7-0.85 s), ~2.5x scale. Swap the face decal at the returned
    `swap_frame` (65 % of the move), then add shake() over the last 6 f."""
    start = cam.location.copy()
    travel = m_to_units(dist) * (1 - 1 / factor)
    _key_loc(cam, f0, start)
    _key_loc(cam, f1, start + _forward(cam) * travel)
    _set_interp(cam, "location", [f0], "QUAD", "EASE_IN")
    return {"swap_frame": int(round(f0 + 0.65 * (f1 - f0))), "shake_from": f1 - 6}


def snap_zoom(cam, f, factor=1.9, frames=4):
    """T28 snap zoom on a transformation: focal length x1.8-2 in 3-5 f, linear.
    Pair with hit_flash() on the subject and an impact SFX."""
    lens0 = cam.data.lens
    cam.data.keyframe_insert("lens", frame=f)
    cam.data.lens = lens0 * factor
    cam.data.keyframe_insert("lens", frame=f + frames)
    _set_interp(cam.data, "lens", [f, f + frames], "LINEAR", indices=(0,))
    return {"lens_end": cam.data.lens}


def axis_punch(cam, factor=2.5, dist=3.0, name=None):
    """T5 axis punch-in cut: returns a NEW camera on the same line of sight, moved in so the
    subject is `factor` x bigger (measured 2-4x per step, 1-3 per video). Give it the same
    drift as the first camera and cut on the stressed syllable."""
    new = cam.copy()
    new.data = cam.data.copy()
    new.animation_data_clear()
    new.name = name or cam.name + "_punch"
    for col in cam.users_collection:
        col.objects.link(new)
    new.location = cam.location + _forward(cam) * (m_to_units(dist) * (1 - 1 / factor))
    return new


def shake(cam, f0, f1, px_at_1080=8, freq=5.0, blend=2, roll_share=0.0, seed=0):
    """T6 impact micro-shake ONLY (no constant handheld). Measured 4-10 px at 4-6 Hz for 4-8 f,
    1-2 per video. Implemented as Noise F-modifiers on rotation X (tilt) and Z (pan), restricted
    to f0..f1 with `blend` frames in/out. 8 px at 35 mm ~= 0.24 deg."""
    lens = _lens(cam)
    amp = px_to_rad(px_at_1080, lens)
    for idx in (0, 2) + ((1,) if roll_share else ()):
        if _fcurve(cam, "rotation_euler", idx) is None:
            cam.keyframe_insert("rotation_euler", index=idx, frame=f0)
        fc = _fcurve(cam, "rotation_euler", idx)
        m = fc.modifiers.new("NOISE")
        m.scale = FPS / freq
        m.strength = 2 * amp * (roll_share if idx == 1 else 1.0)
        m.phase = 7.3 * (idx + 1) + seed
        m.blend_type = "ADD"
        m.use_restricted_range = True
        m.frame_start, m.frame_end = f0, f1
        m.blend_in = m.blend_out = blend
    return {"amp_rad": round(amp, 5)}


def _roll_euler(cam, deg):
    q = _cam_quat(cam)
    rq = q @ Matrix.Rotation(math.radians(deg), 4, "Z").to_quaternion()
    return rq.to_euler("XYZ", cam.rotation_euler)


def roll(cam, f0, deg=6.0, frames=4):
    """T12 small roll / dutch about the view axis: 1.5-2 deg/frame for 3-5 f (4-7.5 deg total),
    then hold. 5-7 per video. Trigger: unease, action."""
    base = cam.rotation_euler.copy()
    cam.keyframe_insert("rotation_euler", frame=f0)
    cam.rotation_euler = _roll_euler(cam, deg)
    cam.keyframe_insert("rotation_euler", frame=f0 + frames)
    _set_interp(cam, "rotation_euler", [f0, f0 + frames], "LINEAR")
    return {"end": tuple(cam.rotation_euler), "start": tuple(base)}


def follow_roll(cam, f0, f1, deg=180.0, step=2):
    """T11 follow roll with a falling or flipping subject: 90-180 deg over 6-12 f, linear,
    then hold upside-down for no more than 15 f. Keys every `step` frames so the roll stays a
    clean rotation about the view axis."""
    base_q = _cam_quat(cam).copy()
    n = max(1, int(math.ceil((f1 - f0) / step)))
    for i in range(n + 1):
        fr = min(f1, f0 + i * step)
        q = base_q @ Matrix.Rotation(math.radians(deg * (fr - f0) / (f1 - f0)), 4, "Z").to_quaternion()
        cam.rotation_euler = q.to_euler("XYZ", cam.rotation_euler)
        cam.keyframe_insert("rotation_euler", frame=fr)
    _set_interp(cam, "rotation_euler", range(f0, f1 + 1), "LINEAR")
    return {"keys": n + 1}


def fly_through(cam, f0, f1, distance_m=2.0):
    """T10 through-surface wipe: the camera flies straight through a wall or floor placed between.
    Measured: the surface fills the frame for 2-3 f, then the camera is in the new space (seen
    twice, in 1 of 5 videos). Place the surface at the returned `surface_at_m` and cut on
    `cut_frame` (the full-frame surface frame)."""
    start = cam.location.copy()
    _key_loc(cam, f0, start)
    _key_loc(cam, f1, start + _forward(cam) * m_to_units(distance_m))
    _set_interp(cam, "location", [f0, f1], "LINEAR")
    return {"surface_at_units": m_to_units(distance_m) / 2, "cut_frame": int(round((f0 + f1) / 2))}


def low_angle(cam, target, height=0.4, tilt_deg=18.0, back=2.5):
    """T19 creature intro: camera at creature height 0.3-0.6 m, tilted up 10-25 deg, 24-26 mm.
    Then push() it (slight push)."""
    t = Vector(target)
    cam.location = Vector((t.x, t.y - m_to_units(back), m_to_units(height)))
    cam.rotation_euler = (math.radians(90 + tilt_deg), 0.0, 0.0)
    if cam.type == "CAMERA":
        cam.data.lens = LENS["wide"]
    return cam


# ---------------------------------------------------------------- subject effects (materials)
def _fx_nodes(mat):
    """Insert (once) an Emission + Mix Shader before the material output. Returns (mix, emit)."""
    mat.use_nodes = True
    nt = mat.node_tree
    mix = nt.nodes.get("BC_mix")
    emit = nt.nodes.get("BC_emit")
    if mix and emit:
        return mix, emit
    out = next((n for n in nt.nodes if n.type == "OUTPUT_MATERIAL"), None)
    if out is None:
        out = nt.nodes.new("ShaderNodeOutputMaterial")
    src = out.inputs["Surface"].links[0].from_socket if out.inputs["Surface"].links else None
    emit = nt.nodes.new("ShaderNodeEmission")
    emit.name = "BC_emit"
    mix = nt.nodes.new("ShaderNodeMixShader")
    mix.name = "BC_mix"
    mix.inputs[0].default_value = 0.0
    if src is not None:
        nt.links.new(src, mix.inputs[1])
    nt.links.new(emit.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])
    return mix, emit


def _fx_materials(obj, single_user=True):
    mats = []
    objs = [obj] + [c for c in obj.children_recursive] if hasattr(obj, "children_recursive") else [obj]
    for o in objs:
        if not hasattr(o, "material_slots"):
            continue
        for slot in o.material_slots:
            if slot.material is None:
                continue
            if single_user and slot.material.users > 1 and not slot.material.name.endswith("_bcfx"):
                m = slot.material.copy()
                m.name = slot.material.name + "_bcfx"
                slot.material = m
            mats.append(slot.material)
    return mats


def _key_fx(mats, frame, fac, color, strength):
    for m in mats:
        mix, emit = _fx_nodes(m)
        mix.inputs[0].default_value = fac
        mix.inputs[0].keyframe_insert("default_value", frame=frame)
        emit.inputs["Color"].default_value = (*hex_to_linear(color), 1.0)
        emit.inputs["Color"].keyframe_insert("default_value", frame=frame)
        emit.inputs["Strength"].default_value = strength
        emit.inputs["Strength"].keyframe_insert("default_value", frame=frame)


def power_tint(obj, f_in, f_out, color=PALETTE["power"], fac=0.65, strength=2.0, fade_in=4, fade_out=12):
    """T8 power tint: the whole character turns glowing power-colour, then fades back.
    Measured: in 3-5 f, out 10-15 f; 6-14 per power video. One power colour per story."""
    mats = _fx_materials(obj)
    _key_fx(mats, f_in, 0.0, color, strength)
    _key_fx(mats, f_in + fade_in, fac, color, strength)
    _key_fx(mats, f_out, fac, color, strength)
    _key_fx(mats, f_out + fade_out, 0.0, color, strength)
    return len(mats)


def hit_flash(obj, f, frames=2, color=PALETTE["key_red"], strength=1.0):
    """T9 solid-colour hit flash: subject goes flat solid colour for 1-3 f on a hit/touch, or
    3-5 f just before a material swap (transformation). Tag 1-2 per video, Material ~12."""
    mats = _fx_materials(obj)
    _key_fx(mats, f - 1, 0.0, color, strength)
    _key_fx(mats, f, 1.0, color, strength)
    _key_fx(mats, f + frames - 1, 1.0, color, strength)
    _key_fx(mats, f + frames, 0.0, color, strength)
    for m in mats:   # hard on/off, no fading
        for fc in _fcurves(m.node_tree):
            for kp in fc.keyframe_points:
                kp.interpolation = "CONSTANT"
    return len(mats)


# ---------------------------------------------------------------- planning (no bpy needed)
def load_timings(word_timings):
    """Accepts a path to *-word-timings.json, its dict ({"words": [[w,s,e]...], "lines": [[s,e,text]...]}),
    or a plain list of (word, start, end). Returns (words, lines)."""
    if isinstance(word_timings, str):
        with open(word_timings) as fh:
            word_timings = json.load(fh)
    if isinstance(word_timings, dict):
        words = [tuple(w) for w in word_timings.get("words", [])]
        lines = [tuple(l) for l in word_timings.get("lines", [])] or None
    else:
        words, lines = [tuple(w) for w in word_timings], None
    words = [(str(w), float(s), float(e)) for w, s, e in words]
    return words, lines


def _phrase_starts(words, lines, gap=0.25):
    """Indices of words that start a narration phrase (split lines on , . ! ? ; : and dashes)."""
    starts = {0}
    if lines:
        idx = 0
        for (_s, _e, text) in lines:
            parts = [p for p in re.split(r"[,.!?;:—–]+|\s-\s", text) if p.strip()]
            for p in parts:
                n = len(re.findall(r"[A-Za-z0-9']+", p))
                if idx < len(words):
                    starts.add(idx)
                idx += n
        return sorted(i for i in starts if i < len(words))
    for i in range(1, len(words)):
        prev = words[i - 1][0]
        if prev[-1:] in ",.!?;:" or words[i][1] - words[i - 1][2] > gap:
            starts.add(i)
    return sorted(starts)


def _stressed(word):
    w = re.sub(r"[^a-z']", "", word.lower())
    return len(w) >= 4 and w not in STOPWORDS


def cut_plan(word_timings, target=MEASURED["avg_shot_s"], min_shot=0.25, max_shot=MEASURED["max_shot_s"],
             split_over=0.8, lead_frames=MEASURED["cut_after_word_f"], fps=FPS, end_s=None):
    """Shot boundaries for the Bright Snap Cut rule (STYLE.md section 5).

    Rule (measured): a cut on EVERY phrase start (95-97 % of phrases), then inside any phrase
    longer than `split_over` s, extra cuts on stressed words (content words of 4+ letters)
    spaced about `target` s apart (avg shot 0.7 s, range 0.56-0.94). No shot shorter than
    `min_shot` (inserts 0.13-0.37 s exist, but keep >= 0.25 s for readability) or longer than
    `max_shot` (2.6 s). Each cut lands `lead_frames` (1) frame AFTER the word onset
    (measured +0.6 to +1.6 f).

    Returns a list of dicts: index, f0, f1 (exclusive), start_s, end_s, words, kind
    ('phrase'|'stress'|'forced'), size (suggested shot size, changes every cut),
    move (suggested camera technique, in measured proportions).
    """
    words, lines = load_timings(word_timings)
    if not words:
        return []
    end_s = end_s or words[-1][2] + 0.2
    ps = _phrase_starts(words, lines)
    cut_idx = []   # (word index, kind)
    for k, a in enumerate(ps):
        b = ps[k + 1] if k + 1 < len(ps) else len(words)
        cut_idx.append((a, "phrase"))
        p_start = words[a][1]
        p_end = words[b][1] if b < len(words) else end_s
        cur = p_start
        while p_end - cur > split_over:
            ideal = cur + target
            cands = [i for i in range(a + 1, b) if words[i][1] - cur >= 0.45 and words[i][1] - cur <= 1.2
                     and p_end - words[i][1] >= min_shot and _stressed(words[i][0])]
            if cands:
                i = min(cands, key=lambda j: abs(words[j][1] - ideal))
                kind = "stress"
            else:
                pool = [i for i in range(a + 1, b) if words[i][1] - cur >= min_shot and p_end - words[i][1] >= min_shot]
                if not pool or p_end - cur <= max_shot:
                    break
                i = min(pool, key=lambda j: abs(words[j][1] - ideal))
                kind = "forced"
            cut_idx.append((i, kind))
            cur = words[i][1]
    cut_idx.sort()
    # frames; enforce min shot length
    cuts = []
    for i, kind in cut_idx:
        f = int(round(words[i][1] * fps)) + (lead_frames if i else 0)
        if cuts and f - cuts[-1][0] < int(round(min_shot * fps)):
            continue
        cuts.append((f, i, kind))
    f_end = int(round(end_s * fps))
    sizes = ["medium", "close", "wide", "close", "medium", "ecu", "medium", "close"]
    moves = ["push", "pull", "push", "drift", "push", "pull", "push", "pull"]   # ~50/37/13 measured
    shots = []
    for n, (f, i, kind) in enumerate(cuts):
        f1 = cuts[n + 1][0] if n + 1 < len(cuts) else f_end
        j = cuts[n + 1][1] if n + 1 < len(cuts) else len(words)
        shots.append({
            "index": n, "f0": f, "f1": f1, "start_s": round(f / fps, 3), "end_s": round(f1 / fps, 3),
            "words": " ".join(w for w, _, _ in words[i:j]), "kind": kind,
            "size": "medium" if n == 0 else sizes[n % len(sizes)],
            "move": "whip_in+push" if n == 0 else moves[n % len(moves)],
        })
    return shots


def plan_stats(shots, fps=FPS):
    """Average / median / max shot length of a plan, to compare with the measured 0.7 s / 0.67-0.80 / 2.6."""
    if not shots:
        return {}
    ls = sorted((s["f1"] - s["f0"]) / fps for s in shots)
    return {"shots": len(shots), "avg_s": round(sum(ls) / len(ls), 3), "median_s": round(ls[len(ls) // 2], 3),
            "max_s": round(ls[-1], 3), "min_s": round(ls[0], 3),
            "cuts_per_min": round(len(ls) / (sum(ls) / 60), 1)}


def caption_plan(word_timings, power_words=(), playful_words=("bouncy", "tiny", "silly", "wobbly"),
                 danger_words=DANGER_WORDS, lead_frames=MEASURED["caption_lead_f"], fps=FPS, max_words=7):
    """One caption per narration phrase (3-7 words; longer phrases split in two), starting
    `lead_frames` (2) before the picture cut on that phrase, i.e. 1 f before the word onset.
    At most ONE coloured keyword: power word -> power colour, danger/result word -> red #E0262A,
    playful word -> yellow #F2D33A. Style and animation: captions_bright_cut.json."""
    words, lines = load_timings(word_timings)
    ps = _phrase_starts(words, lines) + [len(words)]
    caps = []
    for k in range(len(ps) - 1):
        a, b = ps[k], ps[k + 1]
        chunk = list(range(a, b))
        groups = [chunk] if len(chunk) <= max_words else [chunk[: len(chunk) // 2], chunk[len(chunk) // 2:]]
        for g in groups:
            ws = [words[i][0] for i in g]
            key, color = None, None
            for i, w in zip(g, ws):
                lw = re.sub(r"[^a-z']", "", w.lower())
                if lw in {p.lower() for p in power_words}:
                    key, color = i, PALETTE["power"]
                    break
            if key is None:
                for i, w in zip(g, ws):
                    lw = re.sub(r"[^a-z']", "", w.lower())
                    if lw in danger_words:
                        key, color = i, PALETTE["key_red"]
                        break
                    if lw in playful_words:
                        key, color = i, PALETTE["playful_yellow"]
                        break
            f0 = int(round(words[g[0]][1] * fps)) + MEASURED["cut_after_word_f"] - lead_frames
            caps.append({"f0": max(0, f0), "text": " ".join(ws).upper(),
                         "keyword": words[key][0].upper() if key is not None else None, "keyword_color": color})
    for n in range(len(caps)):
        caps[n]["f1"] = caps[n + 1]["f0"] if n + 1 < len(caps) else int(round((words[-1][2] + 0.25) * fps))
    return caps


__all__ = ["apply_look", "light_rig", "make_camera", "push", "pull", "drift", "whip_in", "crash_push",
           "snap_zoom", "axis_punch", "shake", "roll", "follow_roll", "fly_through", "low_angle",
           "power_tint", "hit_flash", "cut_plan", "caption_plan", "plan_stats", "load_timings",
           "px_to_rad", "px_to_m", "hex_to_linear", "PALETTE", "MEASURED", "LENS"]
