# One Copper: shared helpers, cast builders, the Vault Keeper / basalt soldiers / Regent, props, anchors.
# exec'd by vault.py, town_oc.py, wastes.py
import sys, os, math, random, json
sys.path.insert(0, '/tmp/claude-0/tv')
from lib import *
import lib as _lib
import bpy, bmesh
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector, Matrix, Euler

Q = os.environ.get('Q', 'test')
W, H, S = (270, 480, 6) if Q == 'test' else (810, 1440, 20)
if os.environ.get('RES') and Q == 'final': W, H, S = map(int, os.environ['RES'].split('x'))
if os.environ.get('TRES') and Q == 'test': W, H, S = map(int, os.environ['TRES'].split('x'))
ONLY = os.environ.get('ONLY', '')
OUT = '/tmp/claude-0/tv/oc/' + ('st/' if Q == 'final' else 'st_test/')
os.makedirs(OUT, exist_ok=True)
FRED = '/tmp/claude-0/tv/fonts/FredokaOne-Regular.ttf'
random.seed(23)
reset()

# ---------------- fast primitives ----------------
def _fast_obj(name, build, loc, m, parent=None, smooth=False):
    me = bpy.data.meshes.new(name); bm = bmesh.new(); bm.loops.layers.uv.new('UVMap'); build(bm)
    if smooth:
        for f in bm.faces: f.smooth = True
    bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); o.location = loc
    if m: me.materials.append(m)
    if parent: o.parent = parent
    return o
def fbox(name, size, loc, m, rot=(0, 0, 0), parent=None, bevel=0.0):
    def b(bm):
        bmesh.ops.create_cube(bm, size=1.0, calc_uvs=True)
        for v in bm.verts: v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    o = _fast_obj(name, b, loc, m, parent); o.rotation_euler = rot
    if bevel:
        md = o.modifiers.new('b', 'BEVEL'); md.width = bevel; md.segments = 2
    return o
def fcyl(name, r, depth, loc, m, parent=None, verts=32, r2=None, rot=(0, 0, 0)):
    o = _fast_obj(name, lambda bm: bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=verts, radius1=r, radius2=r if r2 is None else r2, depth=depth, calc_uvs=True), loc, m, parent)
    o.rotation_euler = rot; return o
def fsphere(name, r, loc, m, parent=None, seg=24):
    return _fast_obj(name, lambda bm: bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=r, calc_uvs=True), loc, m, parent, smooth=True)
def empty(name, loc=(0, 0, 0), parent=None):
    o = bpy.data.objects.new(name, None); bpy.context.scene.collection.objects.link(o); o.location = loc
    if parent: o.parent = parent
    return o
def emat(name, color, strength):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes):
        if n.bl_idname != 'ShaderNodeOutputMaterial': nt.nodes.remove(n)
    out = [n for n in nt.nodes][0]
    e = nt.nodes.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (*color, 1); e.inputs['Strength'].default_value = strength
    nt.links.new(e.outputs[0], out.inputs['Surface']); return m
def soft_glow(name, color, strength, power=2.0):
    """camera-facing soft disc/sphere glow: emission * fresnel falloff, transparent edges"""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; m.blend_method = 'BLEND' if hasattr(m, 'blend_method') else None
    for n in list(nt.nodes):
        if n.bl_idname != 'ShaderNodeOutputMaterial': nt.nodes.remove(n)
    out = [n for n in nt.nodes][0]
    lw = nt.nodes.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.5
    inv = nt.nodes.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0; nt.links.new(lw.outputs['Facing'], inv.inputs[1])
    pw = nt.nodes.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = power; nt.links.new(inv.outputs[0], pw.inputs[0])
    e = nt.nodes.new('ShaderNodeEmission'); e.inputs['Color'].default_value = (*color, 1); e.inputs['Strength'].default_value = strength
    tr = nt.nodes.new('ShaderNodeBsdfTransparent'); mx = nt.nodes.new('ShaderNodeMixShader')
    nt.links.new(pw.outputs[0], mx.inputs[0]); nt.links.new(tr.outputs[0], mx.inputs[1]); nt.links.new(e.outputs[0], mx.inputs[2])
    nt.links.new(mx.outputs[0], out.inputs['Surface']); return m
def basalt_mat(name, base=(62, 56, 54), hi=(104, 94, 88), glow=(1.0, 0.36, 0.06), gstr=8.0, scale=0.35, crack=0.035, mask=0.5):
    """dark basalt blocks with glowing lava seams (voronoi distance-to-edge)"""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord')
    n = nt.nodes.new('ShaderNodeTexNoise'); n.inputs['Scale'].default_value = scale * 6; nt.links.new(tc.outputs['Object'], n.inputs['Vector'])
    r = nt.nodes.new('ShaderNodeValToRGB'); r.color_ramp.elements[0].color = (*srgb(*base), 1); r.color_ramp.elements[1].color = (*srgb(*hi), 1)
    nt.links.new(n.outputs['Fac'], r.inputs['Fac']); nt.links.new(r.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = 0.85
    v = nt.nodes.new('ShaderNodeTexVoronoi'); v.feature = 'DISTANCE_TO_EDGE'; v.inputs['Scale'].default_value = scale
    nt.links.new(tc.outputs['Object'], v.inputs['Vector'])
    lt = nt.nodes.new('ShaderNodeMath'); lt.operation = 'LESS_THAN'; lt.inputs[1].default_value = crack; nt.links.new(v.outputs['Distance'], lt.inputs[0])
    n2 = nt.nodes.new('ShaderNodeTexNoise'); n2.inputs['Scale'].default_value = scale * 2.2; n2.inputs['Detail'].default_value = 1.0
    nt.links.new(tc.outputs['Object'], n2.inputs['Vector'])
    mk = nt.nodes.new('ShaderNodeMapRange'); mk.inputs['From Min'].default_value = mask; mk.inputs['From Max'].default_value = mask + 0.12
    nt.links.new(n2.outputs['Fac'], mk.inputs['Value'])
    mm = nt.nodes.new('ShaderNodeMath'); mm.operation = 'MULTIPLY'; nt.links.new(lt.outputs[0], mm.inputs[0]); nt.links.new(mk.outputs['Result'], mm.inputs[1])
    gm = nt.nodes.new('ShaderNodeMath'); gm.operation = 'MULTIPLY'; gm.inputs[1].default_value = gstr; nt.links.new(mm.outputs[0], gm.inputs[0]); gm.name = 'GLOWMUL'
    b.inputs['Emission Color'].default_value = (*glow, 1); nt.links.new(gm.outputs[0], b.inputs['Emission Strength'])
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.6; nt.links.new(v.outputs['Distance'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    m['gstr'] = gstr
    return m
def set_glow(m, v):
    for n in m.node_tree.nodes:
        if n.type == 'MATH' and n.operation == 'MULTIPLY' and n.inputs[1].default_value == m.get('gcur', m.get('gstr', 0)):
            n.inputs[1].default_value = v; m['gcur'] = v; return

# ---------------- render / camera ----------------
def clear_lights():
    for o in list(bpy.data.objects):
        if o.type == 'LIGHT': bpy.data.objects.remove(o)
LIGHTS = {}
def mylight(key, loc=None, color=(1, 1, 1), energy=0, radius=0.3, kind='POINT', rot=None, spot=None):
    o = LIGHTS.pop(key, None)
    if o: bpy.data.objects.remove(o)
    if loc is None: return None
    d = bpy.data.lights.new(key, kind); d.energy = energy; d.color = color
    if kind in ('POINT', 'SPOT'): d.shadow_soft_size = radius
    if kind == 'SPOT' and spot: d.spot_size = math.radians(spot); d.spot_blend = 0.4
    if kind == 'AREA': d.size = radius
    o = bpy.data.objects.new(key, d); bpy.context.scene.collection.objects.link(o); o.location = loc
    if rot: o.rotation_euler = rot
    LIGHTS[key] = o; return o
def fill_sun(key, el, rot, energy, color=(1, 1, 1), shadow=False, angle=5):
    LIGHTS.pop(key, None) and None
    o = bpy.data.objects.get(key)
    if o: bpy.data.objects.remove(o)
    d = bpy.data.lights.new(key, 'SUN'); d.energy = energy; d.color = color; d.angle = math.radians(angle)
    try: d.use_shadow = shadow
    except Exception: pass
    o = bpy.data.objects.new(key, d); bpy.context.scene.collection.objects.link(o)
    o.rotation_euler = (math.radians(90 - el), 0, math.radians(rot)); LIGHTS[key] = o; return o
def aim(o, at):
    d = Vector(at) - o.location; o.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
def cam_at(loc, at, lens, roll=0.0):
    c = bpy.data.objects.get('CAM')
    if not c:
        c = camera(lens); c.name = 'CAM'
    c.data.lens = lens; c.location = loc; look(c, at)
    if roll: c.rotation_euler.rotate_axis('Z', math.radians(roll))
    bpy.context.scene.camera = c; c.data.dof.use_dof = False
    return c
def dof(focus, fstop):
    c = bpy.context.scene.camera; c.data.dof.use_dof = True; c.data.dof.focus_distance = focus; c.data.dof.aperture_fstop = fstop
EXPO = [0.0]
def setup(cp):
    sc = bpy.context.scene
    setup_render(W, H, S, 1, 1)
    sc.view_settings.exposure = -0.6 + EXPO[0]
    sc.cycles.transparent_max_bounces = 16
    comp(**(cp or {}))

# ---------------- anchors (2D overlays: tags, letters) ----------------
ANCH = {}     # name -> (object or None, Vector offset/world point)
ANCHL = {}    # name -> list of world points (crowd / army tags)
def anchor(name, at=None, off=(0, 0, 0)):
    if at is None: ANCH.pop(name, None); return
    ANCH[name] = (at if isinstance(at, bpy.types.Object) else None, Vector(off) if isinstance(at, bpy.types.Object) else Vector(at))
def anchors_clear(): ANCH.clear(); ANCHL.clear()
def _proj(sc, c, p, right):
    a = world_to_camera_view(sc, c, p); b = world_to_camera_view(sc, c, p + right)
    return a, [round(a.x, 4), round(1 - a.y, 4), round(abs(b.x - a.x), 5)]
def anchors_json():
    sc = bpy.context.scene; c = sc.camera; bpy.context.view_layer.update()
    right = c.matrix_world.to_3x3() @ Vector((1, 0, 0))
    res = {}
    for k, (o, v) in ANCH.items():
        p = (o.matrix_world @ v) if o else v
        a, r = _proj(sc, c, p, right)
        if a.z > 0: res[k] = r
    for k, pts in ANCHL.items():
        lst = []
        for p in pts:
            lab = None
            if isinstance(p, tuple) and len(p) == 2 and isinstance(p[1], str): p, lab = p
            a, r = _proj(sc, c, Vector(p), right)
            if a.z > 0 and -0.1 < a.x < 1.1 and -0.1 < a.y < 1.1: lst.append(r + [round(a.z, 2)] + ([lab] if lab else []))
        res[k] = lst
    return res
def shoot(name, cp=None):
    if ONLY and not any(name.startswith(o) for o in ONLY.split(',')): return
    sc = bpy.context.scene
    setup(cp)
    sc.frame_set(1); sc.render.filepath = OUT + name + '.png'
    bpy.ops.render.render(write_still=True)
    json.dump(anchors_json(), open(OUT + name + '.json', 'w'))
    print('SHOT', name, flush=True)
def shoot_seq(name, n, setter, cp=None):
    """Look item 7, a real moving shot: renders n frames name_0000..name_NNNN; setter(u) poses camera/scene for u = 0..1.
    Use in shots.py as shot(t, name, seq=n). Size and samples: SEQRES=WxHxS (default 540x960x10 for final)."""
    if ONLY and not any(name.startswith(o) for o in ONLY.split(',')): return
    sc = bpy.context.scene
    sw, shh, ss = (map(int, os.environ.get('SEQRES', '540x960x10').split('x')) if Q == 'final' else (W, H, S))
    for k in range(n):
        u = k / max(1, n - 1); setter(u)
        setup(cp); sc.render.resolution_x = sw; sc.render.resolution_y = shh; sc.cycles.samples = ss
        sc.cycles.seed = 7          # same noise pattern every frame: less flicker after denoising
        sc.frame_set(1); sc.render.filepath = OUT + name + '_%04d.png' % k
        bpy.ops.render.render(write_still=True)
    print('SHOT', name, 'x%d' % n, flush=True)
def want(*names):
    """True when any of these shots will render (skip posing work otherwise)"""
    if not ONLY: return True
    return any(n.startswith(o) for n in names for o in ONLY.split(','))

# ---------------- characters ----------------
CFS = []
def set_face(char, face):
    m = bpy.data.materials[char + 'face']
    img = bpy.data.images.get(face + '.png') or bpy.data.images.load(face_path(face))
    for n in m.node_tree.nodes:
        if n.type == 'TEX_IMAGE': n.image = img
def talk_set(prefix, char, base, cp=None, blink=True):
    if not want(prefix): return
    for suf, f in (('0', base), ('o', base + '_talk_open'), ('r', base + '_talk_round')) + ((('b', base + '_blink'),) if blink else ()):
        set_face(char, f); shoot(prefix + '_' + suf, cp)
    set_face(char, base)
def arm(parts, side, fwd=0, out=0, tw=0):
    parts['arm' + side].rotation_euler = (math.radians(fwd), math.radians(out), math.radians(tw))
def leg(parts, side, fwd=0, out=0):
    parts['leg' + side].rotation_euler = (math.radians(fwd), math.radians(out), 0)
def rest(parts):
    for s in 'LR': leg(parts, s); arm(parts, s)
    parts['head'].rotation_euler = (0, 0, 0)
def walk(parts, k=1):
    leg(parts, 'L', 24 * k); leg(parts, 'R', -24 * k); arm(parts, 'L', fwd=-18 * k); arm(parts, 'R', fwd=18 * k)
def place(o, loc, face_at=None, rz=None):
    o.location = loc
    if face_at is not None:
        dx, dy = face_at[0] - loc[0], face_at[1] - loc[1]; o.rotation_euler = (0, 0, math.atan2(dx, -dy))
    elif rz is not None: o.rotation_euler = (0, 0, math.radians(rz))
def away(o): o.location = (900, 900, -200)
def head_follow(name, parts):
    h = parts['head']
    for o in bpy.data.objects:
        if o.parent and o.parent.name == name and o.instance_type == 'COLLECTION':
            o.parent = h; o.location = (0, 0, 0)
def look_head(parts, pitch=0, yaw=0):
    parts['head'].rotation_euler = (math.radians(pitch), 0, math.radians(yaw))
def person(name, shirt, pants, hair, face, skin=None, beard=None):
    r, p = r6(name, shirt, pants, skin=srgb(*skin) if skin else None, hair=hair, face='face_calm', beard=beard)
    set_face(name, face); head_follow(name, p)
    return r, p
def char_mat(name, color, rough=0.7, metal=0.0, emit=None, estr=0.0):
    return mat(name, srgb(*color), rough, emit=emit, estr=estr, metal=metal)
def add_box(root, name, size, loc, m, bevel=0.05, rot=(0, 0, 0)):
    return fbox(root.name + name, size, loc, m, rot=rot, parent=root, bevel=bevel)

# props shared by everyone
copperM = mat('copper', srgb(196, 112, 60), 0.28, metal=1.0)
copperE = mat('copperE', srgb(210, 124, 64), 0.25, metal=0.9, emit=(1.0, 0.5, 0.2), estr=0.6)
goldM = mat('gold', srgb(240, 182, 60), 0.22, metal=1.0)
goldE = mat('goldE', srgb(255, 200, 80), 0.25, metal=0.6, emit=(1.0, 0.7, 0.2), estr=1.5)
brassM = mat('brass', srgb(205, 160, 70), 0.28, metal=0.95)
steelM = mat('steel', srgb(214, 226, 236), 0.18, metal=1.0)
hiltM = mat('hilt', srgb(96, 60, 36), 0.7)
packM = noise_mat('pack', srgb(110, 80, 50), srgb(140, 104, 66), scale=1.2, rough=0.9, bump=0.4)
strapM = mat('strap', srgb(60, 40, 24), 0.8)
ropeM = mat('ropeM', srgb(150, 118, 70), 0.9)
def coin(name, loc, rot=(90, 0, 0), m=None, r=0.32, parent=None):
    o = fcyl(name, r, 0.07, loc, m or copperM, parent=parent, verts=28)
    o.rotation_euler = tuple(math.radians(a) for a in rot)
    md = o.modifiers.new('b', 'BEVEL'); md.width = 0.02; md.segments = 2
    fcyl(name + 'rim', r * 0.72, 0.075, (0, 0, 0), m or copperM, parent=o, verts=28).scale = (1, 1, 1.05)
    return o
def sword(name, parent=None, loc=(0, 0, 0), rot=(0, 0, 0), s=1.0, glow=None):
    root = empty(name, loc, parent); root.rotation_euler = tuple(math.radians(a) for a in rot)
    fbox(name + 'bl', (0.42 * s, 0.12 * s, 5.2 * s), (0, 0, 3.2 * s), glow or steelM, parent=root, bevel=0.04)
    fbox(name + 'gd', (1.6 * s, 0.4 * s, 0.32 * s), (0, 0, 0.55 * s), goldM, parent=root, bevel=0.05)
    fbox(name + 'gr', (0.3 * s, 0.3 * s, 1.0 * s), (0, 0, -0.05 * s), hiltM, parent=root, bevel=0.03)
    fsphere(name + 'pm', 0.26 * s, (0, 0, -0.62 * s), goldM, parent=root)
    return root
def hand_sword(parts, side, name, s=1.0, up=True, glow=None):
    """sword held in a fist (blade along the arm's -z when up=False, pointing forward when the arm is raised)"""
    return sword(name, parts['arm' + side], (0, -0.2, -1.6), (90, 0, 0) if up else (0, 0, 0), s, glow)
def backpack(root, name, big=1.0, loot=False):
    p = empty(name, (0, 1.1, 3.2), root)
    fbox(name + 'b', (2.3 * big, 1.7 * big, 2.8 * big), (0, 0.85 * big - 0.4, 0.4 * big), packM, parent=p, bevel=0.15)
    fcyl(name + 'roll', 0.55 * big, 2.6 * big, (0, 0.85 * big - 0.4, 2.15 * big), mat(name + 'rm', srgb(70, 90, 120), 0.9), parent=p, rot=(0, math.radians(90), 0))
    for x in (-0.7, 0.7): fbox(name + 's%d' % x, (0.25, 1.4, 0.18), (x, -0.55, 0.5), strapM, parent=p)
    fbox(name + 'pot', (0.7, 0.7, 1.4), (1.35 * big, 0.6, 0.0), mat(name + 'pm', srgb(80, 80, 84), 0.4, metal=0.7), parent=p, bevel=0.2)
    if loot:
        for k, (c, x, z) in enumerate((((1, 0.3, 0.2), -0.6, 2.9), ((0.3, 0.6, 1), 0.2, 3.1), ((0.5, 1, 0.4), 0.8, 2.8), ((1, 0.7, 0.2), -0.1, 3.4))):
            g = fsphere(name + 'g%d' % k, 0.38, (x * big, 0.6 * big, z * big), mat(name + 'gm%d' % k, c, 0.2, emit=c, estr=6), parent=p, seg=8)
    return p
def scales_obj(name, s=1.0, parent=None, loc=(0, 0, 0), glow=0.0, tilt=0.0):
    root = empty(name, loc, parent); root.scale = (s,) * 3
    m = brassM if not glow else mat(name + 'gm', srgb(220, 176, 80), 0.25, metal=0.9, emit=(1.0, 0.75, 0.3), estr=glow)
    fcyl(name + 'post', 0.06, 1.5, (0, 0, 0.75), m, parent=root, verts=12)
    fbox(name + 'base', (0.7, 0.5, 0.1), (0, 0, 0.05), m, parent=root, bevel=0.03)
    fsphere(name + 'top', 0.11, (0, 0, 1.55), m, parent=root, seg=12)
    beam = empty(name + 'beam', (0, 0, 1.5), root); beam.rotation_euler = (0, math.radians(tilt), 0)
    fbox(name + 'bm', (1.9, 0.07, 0.07), (0, 0, 0), m, parent=beam)
    for sx in (-0.9, 0.9):
        hang = empty(name + 'hg%d' % sx, (sx, 0, 0), beam); hang.rotation_euler = (0, math.radians(-tilt), 0)
        fcyl(name + 'pan%d' % sx, 0.36, 0.05, (0, 0, -0.7), m, parent=hang, verts=24)
        for ang in (0, 120, 240):
            dx, dy = math.cos(math.radians(ang)) * 0.15, math.sin(math.radians(ang)) * 0.15
            fbox(name + 'st%d%d' % (sx, ang), (0.015, 0.015, 0.72), (dx, dy, -0.35), m, parent=hang)
    return root
def lantern(name, loc, e=300, col=(1.0, 0.62, 0.28), parent=None):
    root = empty(name, loc, parent)
    fbox(name + 'base', (0.6, 0.6, 0.12), (0, 0, 0.06), mat(name + 'i', srgb(50, 46, 44), 0.5, metal=0.7), parent=root)
    fbox(name + 'top', (0.66, 0.66, 0.14), (0, 0, 0.92), mat(name + 'i2', srgb(50, 46, 44), 0.5, metal=0.7), parent=root)
    fcyl(name + 'gl', 0.24, 0.72, (0, 0, 0.5), emat(name + 'fl', col, 18), parent=root, verts=16)
    for x, y in ((-0.27, -0.27), (0.27, -0.27), (-0.27, 0.27), (0.27, 0.27)):
        fbox(name + 'bar%d%d' % (x * 10, y * 10), (0.06, 0.06, 0.8), (x, y, 0.5), mat(name + 'i3', srgb(50, 46, 44), 0.5, metal=0.7), parent=root)
    fcyl(name + 'ring', 0.12, 0.25, (0, 0, 1.1), mat(name + 'i4', srgb(50, 46, 44), 0.5, metal=0.7), parent=root, verts=10)
    return root

# ---------------- the cast ----------------
ZERO_SKIN = (228, 180, 140)
def build_zero(coat=False):
    shirt = (150, 120, 84) if not coat else (34, 86, 74)
    z, zp = person('zero', shirt, (74, 58, 46), 'hero_medium_tousle', 'face_calm', skin=ZERO_SKIN)
    if coat:
        fbox('zerocoat', (2.14, 1.14, 2.75), (0, 0, 2.55), mat('zerocm', srgb(28, 74, 64), 0.7), parent=z, bevel=0.06)
        fbox('zerotrim', (0.22, 1.18, 2.7), (0, -0.0, 2.6), goldM, parent=z)
    return z, zp
def build_dax():
    d, dp = person('dax', (236, 186, 70), (238, 232, 220), 'hero_swept_undercut', 'face_grin', skin=(236, 196, 160))
    fbox('daxpl', (2.16, 1.14, 0.42), (0, 0, 3.95), goldM, parent=d, bevel=0.1)          # gold pauldron plate
    fbox('daxcape', (2.0, 0.15, 3.6), (0, 0.62, 2.4), mat('daxcapem', srgb(170, 30, 36), 0.8), parent=d, bevel=0.05)
    return d, dp
LIONC = [((60, 110, 210), (236, 230, 220), 'hero_long_straight', 'face_cool'), ((200, 60, 50), (60, 50, 50), 'hero_crop', 'face_bold'),
         ((236, 236, 236), (90, 80, 70), 'hero_side_braid', 'face_sweet')]
def build_lions():
    out = []
    for i, (sh, pa, hr, fc) in enumerate(LIONC):
        r, p = person('lion%d' % i, sh, pa, hr, fc, skin=[(214, 166, 130), (180, 128, 92), (240, 204, 176)][i])
        fbox('lion%dpl' % i, (2.12, 1.12, 0.36), (0, 0, 3.96), goldM, parent=r, bevel=0.08)
        out.append((r, p))
    return out
SHIRTS = [(200, 90, 70), (90, 150, 200), (230, 190, 80), (150, 80, 160), (90, 170, 110), (220, 130, 160), (240, 150, 60), (120, 120, 200)]
PANTS = [(60, 60, 90), (80, 60, 50), (70, 70, 80), (50, 50, 60)]
SKINS = [(236, 190, 150), (200, 150, 112), (170, 118, 84), (226, 176, 140), (120, 84, 60), (240, 200, 170), (190, 140, 100), (150, 104, 74)]
HAIRS = ['hero_crop', 'hero_side_wave', 'hero_half_knot', 'hero_long_straight', 'hero_pixie', 'hero_long_tie', 'hero_twin_tails', 'hero_low_bun', 'hero_slick_back']
FACES = ['face_bright', 'face_sweet', 'face_grin', 'face_cheeky', 'face_starry', 'face_wink', 'face_shy', 'face_calm', 'face_bold']
def build_crowd(n, prefix='cr'):
    out = []
    for i in range(n):
        out.append(person('%s%d' % (prefix, i), SHIRTS[i % 8], PANTS[i % 4], HAIRS[i % 9], FACES[(i * 4) % 9], skin=SKINS[(i * 3) % 8]))
    return out

# ---------------- the Vault Keeper (40 ft of basalt, a furnace for a heart) ----------------
def build_golem(name, s=1.0, mats=None, crown=False, helm=False):
    """blocky stone giant. origin at the feet. returns (root, parts). parts: armL/armR pivots (shoulder), elbowL/R, head, eyes (list), core light"""
    bm_, core_m, eye_m = mats
    root = empty(name); root.scale = (s,) * 3
    P = {'root': root}
    hip = empty(name + 'hip', (0, 0, 15), root); P['hip'] = hip
    for side, x in (('L', -5.2), ('R', 5.2)):
        lp = empty(name + 'leg' + side, (x, 0, 0), hip); P['leg' + side] = lp
        fbox(name + 'th' + side, (7, 7.5, 8), (0, 0, -4), bm_, parent=lp, bevel=0.6)
        fbox(name + 'sh' + side, (7.6, 8.4, 7.6), (0, -0.4, -11.2), bm_, parent=lp, bevel=0.6)
    tor = empty(name + 'tor', (0, 0, 0), hip); P['tor'] = tor
    fbox(name + 'pel', (17, 9.5, 5), (0, 0, 1.5), bm_, parent=tor, bevel=0.6)
    fbox(name + 'chest', (24, 13, 17), (0, 0, 12), bm_, parent=tor, bevel=0.9)
    fbox(name + 'back', (20, 4, 12), (0, 6.5, 14), bm_, parent=tor, bevel=0.8)      # hunch
    # the furnace: a recess with an emissive core and iron bars
    fbox(name + 'core', (8.6, 1.0, 7.6), (0, -6.1, 12.5), core_m, parent=tor)
    fbox(name + 'rim', (11, 1.4, 1.2), (0, -6.7, 16.9), bm_, parent=tor, bevel=0.3)
    fbox(name + 'rimb', (11, 1.4, 1.2), (0, -6.7, 8.1), bm_, parent=tor, bevel=0.3)
    for k in range(4):
        fbox(name + 'bar%d' % k, (0.7, 0.9, 8.6), (-3.3 + k * 2.2, -6.9, 12.5), mat(name + 'iron%d' % k, srgb(30, 26, 26), 0.5, metal=0.6), parent=tor)
    P['core'] = mylight(name + 'core', (0, -9, 12.5 * s + 15 * s), (1, 0.45, 0.12), 6000 * s * s, 2.0 * s)
    nk = empty(name + 'neck', (0, -1.0, 20.5), tor); P['head'] = nk
    fbox(name + 'hd', (10, 9, 8), (0, -0.5, 4), bm_, parent=nk, bevel=0.7)
    fbox(name + 'brow', (10.6, 2.2, 1.6), (0, -4.6, 6.2), bm_, parent=nk, bevel=0.4)
    fbox(name + 'jaw', (8.6, 7, 2.6), (0, -1.0, 0.6), bm_, parent=nk, bevel=0.4)
    P['eyes'] = []
    for x in (-2.4, 2.4):
        P['eyes'].append(fbox(name + 'eye%d' % x, (2.0, 0.6, 1.1), (x, -5.0, 4.6), eye_m, parent=nk, bevel=0.15))
    P['mouth'] = fbox(name + 'mouth', (4.6, 0.5, 0.7), (0, -4.9, 2.0), core_m, parent=nk)
    if crown:
        fbox(name + 'crb', (11, 10, 1.8), (0, -0.5, 8.8), goldE, parent=nk, bevel=0.2)
        for k in range(5):
            for y in (-5.2, 4.2):
                fbox(name + 'crs%d%d' % (k, y), (1.3, 1.0, 3.6), (-4.4 + k * 2.2, y, 11.2), goldE, parent=nk, bevel=0.2)
            fbox(name + 'crx%d' % k, (1.0, 1.3, 3.6), (-5.3 + 0.0, -4.4 + k * 2.2, 11.2), goldE, parent=nk, bevel=0.2) if k < 5 else None
            fbox(name + 'crz%d' % k, (1.0, 1.3, 3.6), (5.3, -4.4 + k * 2.2, 11.2), goldE, parent=nk, bevel=0.2)
        fsphere(name + 'gem', 1.0, (0, -5.5, 9.0), emat(name + 'gemm', (1.0, 0.15, 0.1), 12), parent=nk, seg=12)
    if helm:
        fbox(name + 'helm', (11, 10, 3), (0, -0.5, 8.4), bm_, parent=nk, bevel=0.4)
        fbox(name + 'crest', (1.4, 9, 3.4), (0, -0.5, 11.2), core_m, parent=nk, bevel=0.3)
    for side, x in (('L', -1), ('R', 1)):
        sp = empty(name + 'arm' + side, (x * 14.6, 0, 17.0), tor); P['arm' + side] = sp
        fbox(name + 'shd' + side, (8.4, 9.4, 7), (x * 0.6, 0, 0.8), bm_, parent=sp, bevel=0.8)
        fbox(name + 'ua' + side, (6.4, 6.4, 10), (x * 0.4, 0, -6.5), bm_, parent=sp, bevel=0.6)
        el = empty(name + 'elb' + side, (x * 0.4, 0, -11.5), sp); P['elb' + side] = el
        fbox(name + 'fa' + side, (7, 7, 9), (0, 0, -4.5), bm_, parent=el, bevel=0.6)
        fist = empty(name + 'fist' + side, (0, 0, -9.0), el); P['fist' + side] = fist
        fbox(name + 'fs' + side, (9.4, 9.4, 8.4), (0, 0, -4.0), bm_, parent=fist, bevel=0.9)
        for k in range(4):
            fbox(name + 'kn%s%d' % (side, k), (2.0, 2.4, 1.8), (-3.3 + k * 2.2, -4.2, -6.8), bm_, parent=fist, bevel=0.3)
    return root, P
def gpose(P, armL=(0, 0, 0), armR=(0, 0, 0), elbL=0, elbR=0, head=(0, 0), lean=0, legs=(0, 0), hip_z=None, fistL=(0, 0, 0), fistR=(0, 0, 0)):
    P['armL'].rotation_euler = tuple(math.radians(a) for a in armL)
    P['armR'].rotation_euler = tuple(math.radians(a) for a in armR)
    P['elbL'].rotation_euler = (math.radians(elbL), 0, 0); P['elbR'].rotation_euler = (math.radians(elbR), 0, 0)
    P['fistL'].rotation_euler = tuple(math.radians(a) for a in fistL); P['fistR'].rotation_euler = tuple(math.radians(a) for a in fistR)
    P['head'].rotation_euler = (math.radians(head[0]), 0, math.radians(head[1]))
    P['tor'].rotation_euler = (math.radians(-lean), 0, 0)
    P['legL'].rotation_euler = (math.radians(legs[0]), 0, 0); P['legR'].rotation_euler = (math.radians(legs[1]), 0, 0)
def gworld(P, key, local=(0, 0, 0)):
    bpy.context.view_layer.update(); return P[key].matrix_world @ Vector(local)
def gcore(P, s):
    """move the furnace light to the chest after posing"""
    bpy.context.view_layer.update()
    tor = P['tor']; sc_ = P['root'].scale.x
    P['core'] = mylight(P['root'].name + 'core', tuple(tor.matrix_world @ Vector((0, -10, 12.5))), (1, 0.45, 0.12), 6000 * sc_ * sc_, 2.0 * sc_)
def open_hand(P, side, m):
    """flat stone palm (replaces the fist look): a slab + four fingers lying flat"""
    f = P['fist' + side]
    pal = empty(f.name + 'palm', (0, 0, 0), f)
    fbox(f.name + 'pslab', (11, 10, 2.6), (0, -3, -1.5), m, parent=pal, bevel=0.5)
    for k in range(4):
        fbox(f.name + 'pf%d' % k, (2.3, 6.5, 2.2), (-3.9 + k * 2.6, -10.5, -1.3), m, parent=pal, bevel=0.4)
    fbox(f.name + 'pth', (2.6, 5.0, 2.4), (6.2, -4, 0.2), m, parent=pal, bevel=0.4)
    pal.hide_render = True
    return pal
def fist_mode(P, side, flat):
    f = P['fist' + side]
    for c in f.children:
        if c.name.endswith('palm'):
            c.hide_render = not flat
            for cc in c.children: cc.hide_render = not flat
        else: c.hide_render = flat

# ---------------- price tag anchors on a golem ----------------
def gtag(name, P, s, up=14.0):
    """anchor a tag above a golem's head"""
    anchor(name, P['head'], (0, 0, up))
