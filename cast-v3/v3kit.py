# Cast v3 kit library (Claude, 11-27): data-driven R15-style bodies, simple rigid rigs with named poses,
# textured cloth / leather / metal shaders and decal-face heads whose expression is an integer property.
# Built in Blender units with the Cast v2 scale: Hero kid = 4.16 BU tall, head 0.96 BU (1 m = 3.3 BU).
import bpy, bmesh, math, os, json, random
from mathutils import Vector, Matrix, Quaternion

HERO_H = 4.16            # Cast v2 Hero kid height (BU)
HERO_HEAD = 0.96         # Cast v2 Hero kid head height = width (BU), the "W" of the research report
HH = HERO_H / 3.25       # research-report hero-head unit: the report puts the hero at 3.25 HH -> 1 HH = 1.28 BU (height ratios kept)
W = HERO_HEAD
FACES = '/tmp/claude-0/cast3/faces/'
HAIRDIR = '/mnt/user-data/uploads/roblox/last-caravan-build-r001/assets-src/hair/player-20261031-r001/models/'
CLASSIC_HEAD = '/mnt/user-data/uploads/library/cast/classic-roblox-head/v001/Classic Roblox head.blend'
FONT = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'

def srgb(r, g, b):
    f = lambda c: ((c / 255 + 0.055) / 1.055) ** 2.4 if c / 255 > 0.04045 else c / 255 / 12.92
    return (f(r), f(g), f(b))
def rgba(c): return (*srgb(*c), 1.0)

# =====================================================================================  shader library
def _group(name):
    ng = bpy.data.node_groups.get(name)
    return ng
def _sock(ng, name, kind, io='INPUT', default=None):
    s = ng.interface.new_socket(name, in_out=io, socket_type=kind)
    if default is not None and io == 'INPUT':
        try: s.default_value = default
        except Exception: pass
    return s

def _m(nt, op, a=None, b=None, c=None, clamp=False):
    n = nt.nodes.new('ShaderNodeMath'); n.operation = op; n.use_clamp = clamp
    for i, v in enumerate((a, b, c)):
        if v is None: continue
        if isinstance(v, (int, float)): n.inputs[i].default_value = v
        else: nt.links.new(v, n.inputs[i])
    return n.outputs[0]

def _attr(nt, name):
    a = nt.nodes.new('ShaderNodeAttribute'); a.attribute_type = 'OBJECT'; a.attribute_name = name
    return a.outputs['Fac']

def _mixc(nt, a, b, fac):
    n = nt.nodes.new('ShaderNodeMix'); n.data_type = 'RGBA'
    for sock, v in ((n.inputs['A'], a), (n.inputs['B'], b), (n.inputs['Factor'], fac)):
        if isinstance(v, (tuple, list)): sock.default_value = v
        elif isinstance(v, (int, float)): sock.default_value = v
        else: nt.links.new(v, sock)
    return n.outputs['Result']

def cloth_group():
    """woven fabric: fine over-under weave (bump + tone), soft mottling, a darker hem band with a stitched line,
    and an optional stitched front seam. Hem and seam positions come from object properties hem_z / hem_h / seam_x
    (object space), so one material serves every garment part."""
    ng = _group('CV3 Cloth')
    if ng: return ng
    ng = bpy.data.node_groups.new('CV3 Cloth', 'ShaderNodeTree')
    _sock(ng, 'Color', 'NodeSocketColor', default=(0.5, 0.5, 0.5, 1)); _sock(ng, 'Weave', 'NodeSocketFloat', default=34.0)
    _sock(ng, 'Hem dark', 'NodeSocketFloat', default=0.6); _sock(ng, 'Thread', 'NodeSocketColor', default=(0.8, 0.75, 0.6, 1))
    _sock(ng, 'Sheen', 'NodeSocketFloat', default=0.4); _sock(ng, 'BSDF', 'NodeSocketShader', io='OUTPUT')
    nt = ng; N = nt.nodes; L = nt.links
    gi = N.new('NodeGroupInput'); go = N.new('NodeGroupOutput')
    tc = N.new('ShaderNodeTexCoord'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sep.inputs[0])
    x, y, z = sep.outputs[0], sep.outputs[1], sep.outputs[2]
    k = _m(nt, 'MULTIPLY', gi.outputs['Weave'], 6.2832)
    sx = _m(nt, 'SINE', _m(nt, 'MULTIPLY', _m(nt, 'ADD', x, y), k)); sz = _m(nt, 'SINE', _m(nt, 'MULTIPLY', z, k))
    sxz = _m(nt, 'SINE', _m(nt, 'MULTIPLY', _m(nt, 'ADD', _m(nt, 'ADD', x, y), z), _m(nt, 'MULTIPLY', k, 0.5)))
    weave = _m(nt, 'MULTIPLY_ADD', _m(nt, 'MULTIPLY', sx, sz), 0.5, 0.5)                    # 0..1 basket weave
    noise = N.new('ShaderNodeTexNoise'); noise.inputs['Scale'].default_value = 2.2; noise.inputs['Detail'].default_value = 3
    L.new(tc.outputs['Object'], noise.inputs['Vector'])
    tone = _m(nt, 'ADD', _m(nt, 'MULTIPLY_ADD', noise.outputs['Fac'], 0.22, 0.78), _m(nt, 'MULTIPLY', weave, 0.07))
    tone = _m(nt, 'ADD', tone, _m(nt, 'MULTIPLY', sxz, 0.02))
    base = N.new('ShaderNodeMix'); base.data_type = 'RGBA'; base.blend_type = 'MULTIPLY'; base.inputs['Factor'].default_value = 1.0
    L.new(gi.outputs['Color'], base.inputs['A'])
    cmb = N.new('ShaderNodeCombineColor'); L.new(tone, cmb.inputs[0]); L.new(tone, cmb.inputs[1]); L.new(tone, cmb.inputs[2]); L.new(cmb.outputs[0], base.inputs['B'])
    col = base.outputs['Result']
    # hem band + stitched line above it
    hz = _attr(nt, 'hem_z'); hh = _attr(nt, 'hem_h')
    top = _m(nt, 'ADD', hz, hh)
    inband = _m(nt, 'MULTIPLY', _m(nt, 'LESS_THAN', z, top), _m(nt, 'GREATER_THAN', hh, 0.001))
    dark = N.new('ShaderNodeMix'); dark.data_type = 'RGBA'; dark.blend_type = 'MULTIPLY'
    L.new(col, dark.inputs['A']); gv = N.new('ShaderNodeCombineColor')
    for i in range(3): L.new(gi.outputs['Hem dark'], gv.inputs[i])
    L.new(gv.outputs[0], dark.inputs['B']); L.new(inband, dark.inputs['Factor'])
    col = dark.outputs['Result']
    zs = _m(nt, 'ADD', top, 0.035)
    near = _m(nt, 'LESS_THAN', _m(nt, 'ABSOLUTE', _m(nt, 'SUBTRACT', z, zs)), 0.011)
    dash = _m(nt, 'GREATER_THAN', _m(nt, 'SINE', _m(nt, 'MULTIPLY', _m(nt, 'ADD', x, y), 70.0)), 0.15)
    stitch = _m(nt, 'MULTIPLY', _m(nt, 'MULTIPLY', near, dash), _m(nt, 'GREATER_THAN', hh, 0.001))
    # front seam (x = seam_x, front half only)
    sxp = _attr(nt, 'seam_x')
    seam = _m(nt, 'MULTIPLY', _m(nt, 'LESS_THAN', _m(nt, 'ABSOLUTE', _m(nt, 'SUBTRACT', x, sxp)), 0.012), _m(nt, 'LESS_THAN', y, 0.0))
    seamst = _m(nt, 'MULTIPLY', _m(nt, 'MULTIPLY', _m(nt, 'LESS_THAN', _m(nt, 'ABSOLUTE', _m(nt, 'SUBTRACT', _m(nt, 'ABSOLUTE', _m(nt, 'SUBTRACT', x, sxp)), 0.04)), 0.009),
                                               _m(nt, 'GREATER_THAN', _m(nt, 'SINE', _m(nt, 'MULTIPLY', z, 70.0)), 0.15)), _m(nt, 'LESS_THAN', y, 0.0))
    col = _mixc(nt, col, (0.0, 0.0, 0.0, 1.0), _m(nt, 'MULTIPLY', seam, 0.55))
    col = _mixc(nt, col, gi.outputs['Thread'], _m(nt, 'MAXIMUM', stitch, seamst))
    b = N.new('ShaderNodeBsdfPrincipled')
    L.new(col, b.inputs['Base Color']); b.inputs['Roughness'].default_value = 0.86
    L.new(gi.outputs['Sheen'], b.inputs['Sheen Weight']); b.inputs['Sheen Roughness'].default_value = 0.5
    bh = _m(nt, 'ADD', _m(nt, 'ADD', weave, _m(nt, 'MULTIPLY', stitch, 1.5)), _m(nt, 'MULTIPLY', seam, -2.0))
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.22; bp.inputs['Distance'].default_value = 0.01
    L.new(bh, bp.inputs['Height']); L.new(bp.outputs['Normal'], b.inputs['Normal'])
    L.new(b.outputs[0], go.inputs[0])
    return ng

def leather_group():
    """worn leather: lighter scuffs, darker creases, varying sheen."""
    ng = _group('CV3 Leather')
    if ng: return ng
    ng = bpy.data.node_groups.new('CV3 Leather', 'ShaderNodeTree')
    _sock(ng, 'Color', 'NodeSocketColor', default=(0.2, 0.1, 0.05, 1)); _sock(ng, 'Wear', 'NodeSocketFloat', default=0.5)
    _sock(ng, 'BSDF', 'NodeSocketShader', io='OUTPUT')
    nt = ng; N = nt.nodes; L = nt.links
    gi = N.new('NodeGroupInput'); go = N.new('NodeGroupOutput')
    tc = N.new('ShaderNodeTexCoord')
    n1 = N.new('ShaderNodeTexNoise'); n1.inputs['Scale'].default_value = 5.0; n1.inputs['Detail'].default_value = 6; n1.inputs['Roughness'].default_value = 0.62
    L.new(tc.outputs['Object'], n1.inputs['Vector'])
    vo = N.new('ShaderNodeTexVoronoi'); vo.feature = 'DISTANCE_TO_EDGE'; vo.inputs['Scale'].default_value = 11.0
    L.new(tc.outputs['Object'], vo.inputs['Vector'])
    scuff = _m(nt, 'MULTIPLY', _m(nt, 'MAP_RANGE' if False else 'SUBTRACT', n1.outputs['Fac'], 0.56), 6.0, clamp=True)
    scuff = _m(nt, 'MULTIPLY', scuff, gi.outputs['Wear'], clamp=True)
    crease = _m(nt, 'LESS_THAN', vo.outputs['Distance'], 0.035)
    lighter = N.new('ShaderNodeMix'); lighter.data_type = 'RGBA'; lighter.blend_type = 'SCREEN'
    L.new(gi.outputs['Color'], lighter.inputs['A']); lighter.inputs['B'].default_value = (0.35, 0.3, 0.26, 1); L.new(scuff, lighter.inputs['Factor'])
    col = _mixc(nt, lighter.outputs['Result'], (0.02, 0.012, 0.008, 1), _m(nt, 'MULTIPLY', crease, 0.5))
    tone = _m(nt, 'MULTIPLY_ADD', n1.outputs['Fac'], 0.3, 0.82)
    mul = N.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs['Factor'].default_value = 1
    L.new(col, mul.inputs['A']); cc = N.new('ShaderNodeCombineColor')
    for i in range(3): L.new(tone, cc.inputs[i])
    L.new(cc.outputs[0], mul.inputs['B'])
    b = N.new('ShaderNodeBsdfPrincipled'); L.new(mul.outputs['Result'], b.inputs['Base Color'])
    L.new(_m(nt, 'ADD', _m(nt, 'MULTIPLY_ADD', n1.outputs['Fac'], 0.3, 0.38), _m(nt, 'MULTIPLY', scuff, 0.2)), b.inputs['Roughness'])
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.3; bp.inputs['Distance'].default_value = 0.01
    L.new(_m(nt, 'SUBTRACT', n1.outputs['Fac'], _m(nt, 'MULTIPLY', crease, 0.6)), bp.inputs['Height']); L.new(bp.outputs['Normal'], b.inputs['Normal'])
    L.new(b.outputs[0], go.inputs[0])
    return ng

def metal_group():
    """forged metal: brushed streak scratches, roughness breakup, slightly lifted worn edges via noise."""
    ng = _group('CV3 Metal')
    if ng: return ng
    ng = bpy.data.node_groups.new('CV3 Metal', 'ShaderNodeTree')
    _sock(ng, 'Color', 'NodeSocketColor', default=(0.5, 0.5, 0.5, 1)); _sock(ng, 'Roughness', 'NodeSocketFloat', default=0.32)
    _sock(ng, 'Scratch', 'NodeSocketFloat', default=0.5); _sock(ng, 'Metallic', 'NodeSocketFloat', default=1.0)
    _sock(ng, 'BSDF', 'NodeSocketShader', io='OUTPUT')
    nt = ng; N = nt.nodes; L = nt.links
    gi = N.new('NodeGroupInput'); go = N.new('NodeGroupOutput')
    tc = N.new('ShaderNodeTexCoord')
    mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (2.0, 2.0, 46.0); L.new(tc.outputs['Object'], mp.inputs['Vector'])
    st = N.new('ShaderNodeTexNoise'); st.inputs['Scale'].default_value = 9.0; st.inputs['Detail'].default_value = 2; L.new(mp.outputs['Vector'], st.inputs['Vector'])
    br = N.new('ShaderNodeTexNoise'); br.inputs['Scale'].default_value = 3.0; br.inputs['Detail'].default_value = 4; L.new(tc.outputs['Object'], br.inputs['Vector'])
    scr = _m(nt, 'MULTIPLY', _m(nt, 'MULTIPLY', _m(nt, 'SUBTRACT', st.outputs['Fac'], 0.58), 8.0, clamp=True), gi.outputs['Scratch'])
    rough = _m(nt, 'ADD', _m(nt, 'ADD', gi.outputs['Roughness'], _m(nt, 'MULTIPLY', _m(nt, 'SUBTRACT', br.outputs['Fac'], 0.5), 0.22)), _m(nt, 'MULTIPLY', scr, 0.18))
    col = N.new('ShaderNodeMix'); col.data_type = 'RGBA'; col.blend_type = 'SCREEN'
    L.new(gi.outputs['Color'], col.inputs['A']); col.inputs['B'].default_value = (0.16, 0.16, 0.17, 1); L.new(_m(nt, 'MULTIPLY', scr, 0.6), col.inputs['Factor'])
    b = N.new('ShaderNodeBsdfPrincipled'); L.new(col.outputs['Result'], b.inputs['Base Color']); L.new(rough, b.inputs['Roughness'])
    L.new(gi.outputs['Metallic'], b.inputs['Metallic'])
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.12; bp.inputs['Distance'].default_value = 0.005
    L.new(_m(nt, 'ADD', br.outputs['Fac'], _m(nt, 'MULTIPLY', scr, -0.5)), bp.inputs['Height']); L.new(bp.outputs['Normal'], b.inputs['Normal'])
    L.new(b.outputs[0], go.inputs[0])
    return ng

_MATS = {}
def _gmat(name, group, **inputs):
    if name in _MATS: return _MATS[name]
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes):
        if n.bl_idname != 'ShaderNodeOutputMaterial': nt.nodes.remove(n)
    out = [n for n in nt.nodes][0]
    g = nt.nodes.new('ShaderNodeGroup'); g.node_tree = group
    for k, v in inputs.items(): g.inputs[k].default_value = v
    nt.links.new(g.outputs[0], out.inputs['Surface'])
    _MATS[name] = m; return m

def cloth(name, rgb, weave=34.0, hem_dark=0.6, thread=None, sheen=0.4):
    th = thread or tuple(min(255, int(c * 1.6 + 40)) for c in rgb)
    lum = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
    sheen = sheen * min(1.0, max(0.12, (lum - 20) / 110))      # sheen greys out dark fabric: fade it on near-black cloth
    return _gmat('CV3 ' + name, cloth_group(), **{'Color': rgba(rgb), 'Weave': weave, 'Hem dark': hem_dark, 'Thread': rgba(th), 'Sheen': sheen})
def leather(name, rgb, wear=0.6):
    return _gmat('CV3 ' + name, leather_group(), **{'Color': rgba(rgb), 'Wear': wear})
def metal(name, rgb, rough=0.32, scratch=0.5, metallic=1.0):
    return _gmat('CV3 ' + name, metal_group(), **{'Color': rgba(rgb), 'Roughness': rough, 'Scratch': scratch, 'Metallic': metallic})
def plain(name, rgb, rough=0.5, metallic=0.0, emit=None, estr=0.0, coat=0.0):
    if 'CV3 ' + name in _MATS: return _MATS['CV3 ' + name]
    m = bpy.data.materials.new('CV3 ' + name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = rgba(rgb); b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metallic
    if coat: b.inputs['Coat Weight'].default_value = coat
    if emit: b.inputs['Emission Color'].default_value = rgba(emit); b.inputs['Emission Strength'].default_value = estr
    _MATS['CV3 ' + name] = m; return m
def glow(name, rgb, strength=8.0):
    if 'CV3 ' + name in _MATS: return _MATS['CV3 ' + name]
    m = bpy.data.materials.new('CV3 ' + name); m.use_nodes = True; nt = m.node_tree
    for n in list(nt.nodes):
        if n.bl_idname != 'ShaderNodeOutputMaterial': nt.nodes.remove(n)
    out = [n for n in nt.nodes][0]; e = nt.nodes.new('ShaderNodeEmission')
    e.inputs['Color'].default_value = rgba(rgb); e.inputs['Strength'].default_value = strength
    nt.links.new(e.outputs[0], out.inputs['Surface']); _MATS['CV3 ' + name] = m; return m
def skin_mat(name, rgb, classic=False):
    return plain(name, rgb, rough=0.42 if classic else 0.5, coat=0.15 if classic else 0.0)
def hair_mat(name, rgb):
    """hair blobs: strand-direction wave bump + slight sheen"""
    if 'CV3 ' + name in _MATS: return _MATS['CV3 ' + name]
    m = bpy.data.materials.new('CV3 ' + name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = rgba(rgb); b.inputs['Roughness'].default_value = 0.45
    tc = nt.nodes.new('ShaderNodeTexCoord'); wv = nt.nodes.new('ShaderNodeTexWave'); wv.wave_type = 'BANDS'; wv.bands_direction = 'X'
    wv.inputs['Scale'].default_value = 30; wv.inputs['Distortion'].default_value = 6; nt.links.new(tc.outputs['Object'], wv.inputs['Vector'])
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.25; nt.links.new(wv.outputs['Fac'], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    _MATS['CV3 ' + name] = m; return m

# =====================================================================================  geometry helpers
def ring(w, d, p, n=32, cx=0.0, cy=0.0):
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n + math.pi / n
        c, s = math.cos(t), math.sin(t)
        pts.append((cx + w / 2 * math.copysign(abs(c) ** (2 / p), c), cy + d / 2 * math.copysign(abs(s) ** (2 / p), s)))
    return pts

def loft(sections, n=32, cap=(True, True), round_ends=0.0, mat=None):
    """sections: [(z, w, d, p, cx, cy)] bottom -> top (p: superellipse exponent, 2 = ellipse, 10 = boxy).
    round_ends softens both caps with extra inset rings. Returns a bmesh."""
    secs = [tuple(s) + (0.0, 0.0)[len(s) - 4:] if len(s) < 6 else tuple(s) for s in sections]
    if round_ends > 0:
        e = round_ends; z0, w0, d0, p0, x0, y0 = secs[0]; z1, w1, d1, p1, x1, y1 = secs[-1]
        lo = [(z0, max(0.02, w0 - 2 * e), max(0.02, d0 - 2 * e), p0, x0, y0), (z0 + e * 0.3, w0 - e * 0.65, d0 - e * 0.65, p0, x0, y0), (z0 + e, w0, d0, p0, x0, y0)]
        hi = [(z1 - e, w1, d1, p1, x1, y1), (z1 - e * 0.3, w1 - e * 0.65, d1 - e * 0.65, p1, x1, y1), (z1, max(0.02, w1 - 2 * e), max(0.02, d1 - 2 * e), p1, x1, y1)]
        mid = [s for s in secs[1:-1] if z0 + e < s[0] < z1 - e]
        secs = lo + mid + hi
    bm = bmesh.new(); rings = []
    for z, w, d, p, cx, cy in secs:
        rings.append([bm.verts.new((x, y, z)) for x, y in ring(w, d, p, n, cx, cy)])
    for a, b in zip(rings[:-1], rings[1:]):
        for i in range(n):
            bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    for idx, r in ((0, rings[0]), (1, rings[-1])):
        if not cap[idx]: continue
        zc = secs[0][0] if idx == 0 else secs[-1][0]
        cxy = (secs[0][4], secs[0][5]) if idx == 0 else (secs[-1][4], secs[-1][5])
        c = bm.verts.new((cxy[0], cxy[1], zc))
        for i in range(n):
            f = (r[i], r[(i + 1) % n], c) if idx == 1 else (r[(i + 1) % n], r[i], c)
            bm.faces.new(f)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm

def lathe(profile, n=40):
    """profile: [(r, z)] from bottom to top; r=0 points close the shape. Returns bmesh."""
    bm = bmesh.new(); rings = []
    for r, z in profile:
        if r <= 1e-6: rings.append([bm.verts.new((0, 0, z))])
        else: rings.append([bm.verts.new((r * math.cos(2 * math.pi * i / n), r * math.sin(2 * math.pi * i / n), z)) for i in range(n)])
    for a, b in zip(rings[:-1], rings[1:]):
        if len(a) == 1 and len(b) == 1: continue
        if len(a) == 1:
            for i in range(n): bm.faces.new((a[0], b[i], b[(i + 1) % n]))
        elif len(b) == 1:
            for i in range(n): bm.faces.new((a[i], a[(i + 1) % n], b[0]))
        else:
            for i in range(n): bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm

def ellipsoid(rx, ry, rz, seg=32, rings_=16):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=rings_, radius=1.0)
    bmesh.ops.scale(bm, vec=(rx, ry, rz), verts=bm.verts); return bm

def cube_bm(w, d, h):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bmesh.ops.scale(bm, vec=(w, d, h), verts=bm.verts); return bm

def torus_bm(R, r, seg=24, sseg=10):
    bm = bmesh.new()
    rings = []
    for i in range(seg):
        a = 2 * math.pi * i / seg; ca, sa = math.cos(a), math.sin(a)
        rings.append([bm.verts.new(((R + r * math.cos(2 * math.pi * j / sseg)) * ca, (R + r * math.cos(2 * math.pi * j / sseg)) * sa, r * math.sin(2 * math.pi * j / sseg))) for j in range(sseg)])
    for i in range(seg):
        a, b = rings[i], rings[(i + 1) % seg]
        for j in range(sseg): bm.faces.new((a[j], b[j], b[(j + 1) % sseg], a[(j + 1) % sseg]))
    return bm

def tube_bm(pts, radii, n=12):
    """swept circle along a polyline; radii per point"""
    bm = bmesh.new(); rings = []
    P = [Vector(p) for p in pts]
    for i, p in enumerate(P):
        t = (P[min(i + 1, len(P) - 1)] - P[max(i - 1, 0)]).normalized()
        a = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        u = t.cross(a).normalized(); v = t.cross(u).normalized()
        r = radii[i] if isinstance(radii, (list, tuple)) else radii
        rings.append([bm.verts.new(p + (u * math.cos(2 * math.pi * j / n) + v * math.sin(2 * math.pi * j / n)) * r) for j in range(n)])
    for a, b in zip(rings[:-1], rings[1:]):
        for j in range(n): bm.faces.new((a[j], a[(j + 1) % n], b[(j + 1) % n], b[j]))
    for r_, flip in ((rings[0], True), (rings[-1], False)):
        f = bm.faces.new(r_[::-1] if flip else r_)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return bm

def xform(bm, M):
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts); return bm

def text_bm(txt, size, depth):
    cu = bpy.data.curves.new('cv3_txt', 'FONT'); cu.body = txt; cu.size = size; cu.extrude = depth; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
    try: cu.font = bpy.data.fonts.load(FONT, check_existing=True)
    except Exception: pass
    o = bpy.data.objects.new('cv3_txt', cu); bpy.context.scene.collection.objects.link(o)
    dg = bpy.context.evaluated_depsgraph_get(); me = bpy.data.meshes.new_from_object(o.evaluated_get(dg))
    bm = bmesh.new(); bm.from_mesh(me); bpy.data.objects.remove(o); bpy.data.curves.remove(cu); bpy.data.meshes.remove(me)
    vs = [v.co for v in bm.verts]
    mn = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs))); mx = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
    k = size / max(1e-6, (mx.y - mn.y))            # glyph height = size exactly, centred on the origin
    bmesh.ops.translate(bm, vec=-(mn + mx) / 2, verts=bm.verts); bmesh.ops.scale(bm, vec=(k, k, 1.0), verts=bm.verts)
    return bm

def grid_sheet(rows_pts, thickness=0.03):
    """rows_pts: list of rows, each a list of (x,y,z). Builds a quad sheet (later solidified)."""
    bm = bmesh.new(); V = [[bm.verts.new(p) for p in row] for row in rows_pts]
    for r in range(len(V) - 1):
        for c in range(len(V[r]) - 1):
            bm.faces.new((V[r][c], V[r][c + 1], V[r + 1][c + 1], V[r + 1][c]))
    return bm

class Char:
    """one character being built: collection, rig, parts, sockets."""
    def __init__(self, name, key):
        self.name = name; self.key = key
        self.col = bpy.data.collections.new('Cast v3 | ' + name); bpy.context.scene.collection.children.link(self.col)
        self.rig = None; self.parts = {}; self.J = {}; self.P = {}; self.head = None; self.extra = []

    def obj(self, label, bm, mat=None, bone=None, origin=(0, 0, 0), smooth=True, mats=None, solid=0.0, bevel=0.0, subsurf=0):
        """bmesh in rest-pose world coordinates -> object '<Name> | label' with its origin at `origin`, parented to `bone`."""
        o_ = Vector(origin)
        bmesh.ops.translate(bm, vec=-o_, verts=bm.verts)
        me = bpy.data.meshes.new(self.name + ' | ' + label); bm.to_mesh(me); bm.free()
        if smooth:
            for p in me.polygons: p.use_smooth = True
        ob = bpy.data.objects.new(self.name + ' | ' + label, me); self.col.objects.link(ob)
        for m in (mats or ([mat] if mat else [])): me.materials.append(m)
        if solid:
            md = ob.modifiers.new('solidify', 'SOLIDIFY'); md.thickness = solid; md.offset = 0.0
        if bevel:
            md = ob.modifiers.new('bevel', 'BEVEL'); md.width = bevel; md.segments = 3; md.limit_method = 'ANGLE'; md.harden_normals = True
        if subsurf:
            md = ob.modifiers.new('subsurf', 'SUBSURF'); md.levels = subsurf; md.render_levels = subsurf
        ob['hem_z'] = -1000.0; ob['hem_h'] = 0.0; ob['seam_x'] = 1000.0
        ob.matrix_world = Matrix.Translation(o_)
        if bone: self.bone_parent(ob, bone)
        return ob

    def hem(self, ob, world_z_bottom, h=0.1):
        ob['hem_z'] = world_z_bottom - ob.matrix_world.translation.z if ob.parent is None else world_z_bottom - self._origin(ob).z
        ob['hem_h'] = h
    def seam(self, ob, x=0.0): ob['seam_x'] = x - self._origin(ob).x
    def _origin(self, ob): return ob.get('_origin_v', None) and Vector(ob['_origin_v']) or ob.matrix_world.translation

    def bone_parent(self, ob, bone):
        rig = self.rig; b = rig.data.bones[bone]
        world = ob.matrix_world.copy(); ob['_origin_v'] = list(world.translation)
        ob.parent = rig; ob.parent_type = 'BONE'; ob.parent_bone = bone
        PM = rig.matrix_world @ b.matrix_local @ Matrix.Translation((0, b.length, 0))
        ob.matrix_parent_inverse = Matrix.Identity(4)
        ob.matrix_basis = PM.inverted() @ world

    def socket(self, label, bone, loc, size=0.25):
        e = bpy.data.objects.new(self.name + ' | ' + label, None); e.empty_display_type = 'ARROWS'; e.empty_display_size = size
        self.col.objects.link(e); e.matrix_world = Matrix.Translation(Vector(loc)); self.bone_parent(e, bone); return e

# =====================================================================================  body types (data)
# Heights are hero-relative (report HH x 1.28 BU); widths in BU (W = hero head width 0.96). See CAST-V3.md for the table.
BODY_TYPES = {
    # key            H     head  neck  f_leg f_lt  sw    ww    hw    td    at    ad    lgw   lgd   hand  fl    fh    reach      p   hunch
    'mini':         (2.88, 1.01, 0.02, 0.34, 0.22, 1.00, 1.04, 1.06, 0.74, 0.36, 0.38, 0.44, 0.46, 0.26, 0.50, 0.15, 'hip',      4, 0),
    'small_hero':   (4.16, 0.96, 0.03, 0.46, 0.17, 1.25, 1.05, 1.10, 0.62, 0.42, 0.44, 0.50, 0.52, 0.34, 0.66, 0.18, 'midthigh', 6, 0),
    'classic_r6':   (5.44, 0.96, 0.02, 0.48, 0.11, 1.85, 1.85, 1.85, 0.92, 0.90, 0.92, 0.91, 0.92, 0.50, 0.92, 0.26, 'hip',      12, 0),
    'lanky_kid':    (4.61, 0.96, 0.05, 0.52, 0.13, 1.06, 0.92, 0.96, 0.52, 0.29, 0.31, 0.34, 0.36, 0.32, 0.66, 0.20, 'midthigh', 6, 0),
    'slender_tall': (6.72, 0.86, 0.10, 0.55, 0.10, 1.02, 0.74, 0.84, 0.52, 0.27, 0.28, 0.32, 0.34, 0.50, 0.74, 0.18, 'lowthigh', 6, 7),
    'heroic_teen':  (6.08, 0.96, 0.06, 0.55, 0.11, 1.85, 1.15, 1.20, 0.80, 0.50, 0.52, 0.56, 0.58, 0.42, 0.82, 0.22, 'midthigh', 6, 0),
    'heroic_adult': (8.32, 0.91, 0.07, 0.55, 0.11, 2.20, 1.45, 1.50, 1.15, 0.66, 0.68, 0.72, 0.74, 0.55, 1.05, 0.28, 'midthigh', 7, 0),
    'brute':        (6.18, 0.82, 0.00, 0.38, 0.15, 2.75, 2.45, 2.30, 1.50, 0.80, 0.82, 0.96, 0.98, 0.77, 1.15, 0.30, 'knee',     8, 4),
    'round_big':    (4.80, 0.96, 0.02, 0.33, 0.30, 1.80, 2.45, 2.25, 1.65, 0.52, 0.54, 0.66, 0.68, 0.40, 0.80, 0.22, 'hip',      3, 0),
    'broad_heroic': (6.08, 0.86, 0.04, 0.48, 0.13, 2.55, 1.90, 1.90, 1.20, 0.60, 0.62, 0.70, 0.72, 0.52, 0.92, 0.24, 'midthigh', 7, 0),
    'tall_elder':   (7.68, 0.91, 0.06, 0.52, 0.12, 1.34, 1.30, 1.40, 0.80, 0.36, 0.38, 0.42, 0.44, 0.44, 0.80, 0.20, 'midthigh', 6, 6),
    'true_form':    (8.64, 0.96, 0.08, 0.582, 0.093, 2.25, 1.25, 1.30, 0.90, 0.52, 0.54, 0.60, 0.62, 0.50, 0.95, 0.26, 'midthigh', 6, 0),
}
FIELDS = ['H', 'head', 'neck', 'f_leg', 'f_lt', 'sw', 'ww', 'hw', 'td', 'at', 'ad', 'lgw', 'lgd', 'hand', 'fl', 'fh', 'reach', 'p', 'hunch']

def body_params(btype, **over):
    P = dict(zip(FIELDS, BODY_TYPES[btype])); P['type'] = btype; P.update(over)
    body = P['H'] - P['head'] - P['neck']
    P['leg'] = P.get('leg') or body * P['f_leg']
    P['lt'] = P.get('lt') or body * P['f_lt']
    P['ut'] = body - P['leg'] - P['lt']
    P['hip_z'] = P['leg']; P['waist_z'] = P['leg'] + P['lt']; P['sh_z'] = P['waist_z'] + P['ut']
    P['neck_z'] = P['sh_z'] + P['neck']; P['head_c'] = P['neck_z'] + P['head'] / 2; P['top'] = P['neck_z'] + P['head']
    reach = {'hip': P['leg'] * 1.0, 'midthigh': P['leg'] * 0.74, 'lowthigh': P['leg'] * 0.64, 'knee': P['leg'] * 0.5}.get(P['reach'], P['reach'])
    P['arm_drop'] = P.get('arm_drop', 0.5 * P['at'] if P['type'] != 'classic_r6' else 0.5 * P['at'])
    P['sjz'] = P['sh_z'] - P['arm_drop']
    A = P['sjz'] + 0.5 * P['at'] - reach               # arm length, shoulder top -> fingertips
    P['ua'] = (A - P['hand']) * 0.52 - 0.25 * P['at']; P['la'] = (A - P['hand']) * 0.48 + 0.25 * P['at'] - 0.5 * P['at']
    P['sx'] = P['sw'] / 2 + P['at'] / 2 + P.get('arm_gap', 0.02)
    P['lx'] = P.get('lx') or max(P['lgw'] / 2 + 0.03, P['hw'] / 2 - P['lgw'] / 2 - 0.02)
    leg_len = P['leg'] - P['fh']
    P['knee_z'] = P['fh'] + leg_len * 0.5
    return P

# =====================================================================================  rig
BONES = ['Root', 'LowerTorso', 'UpperTorso', 'Head', 'LeftUpperArm', 'LeftLowerArm', 'LeftHand', 'RightUpperArm', 'RightLowerArm', 'RightHand',
         'LeftUpperLeg', 'LeftLowerLeg', 'LeftFoot', 'RightUpperLeg', 'RightLowerLeg', 'RightFoot']

def make_rig(C, joints, extra=()):
    """joints: bone -> (head, tail, parent). Character faces -Y; Left = character's own left = +X."""
    arm = bpy.data.armatures.new(C.name + ' | rig'); rig = bpy.data.objects.new(C.name + ' | rig', arm); C.col.objects.link(rig)
    arm.display_type = 'OCTAHEDRAL'; rig.show_in_front = True
    bpy.context.view_layer.objects.active = rig
    for o in bpy.context.selected_objects: o.select_set(False)
    rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for name, (h, t, par) in list(joints.items()) + list(extra):
        eb = arm.edit_bones.new(name); eb.head = h; eb.tail = t
        if par: eb.parent = arm.edit_bones[par]
        d = (Vector(t) - Vector(h)).normalized()
        eb.align_roll(Vector((0, 0, 1)) if abs(d.z) < 0.7 else Vector((0, -1, 0)))
    bpy.ops.object.mode_set(mode='OBJECT')
    try:
        bc = arm.collections.new('Body')
        for b in arm.bones: bc.assign(b)
    except Exception: pass
    C.rig = rig
    rig['cast'] = 'v3'; rig['char'] = C.name; rig['blender'] = bpy.app.version_string
    return rig

def humanoid_joints(P):
    J = {}
    J['Root'] = ((0, 0, 0), (0, 0, P['hip_z'] * 0.5), None)
    J['LowerTorso'] = ((0, 0, P['hip_z']), (0, 0, P['waist_z']), 'Root')
    J['UpperTorso'] = ((0, 0, P['waist_z']), (0, 0, P['sh_z']), 'LowerTorso')
    J['Head'] = ((0, 0, P['neck_z']), (0, 0, P['top']), 'UpperTorso')
    for side, s in (('Left', 1), ('Right', -1)):
        sx = s * P['sx']; z0 = P['sjz']; ze = z0 - P['ua']; zw = ze - P['la']; zf = zw - P['hand']
        J[side + 'UpperArm'] = ((sx, 0, z0), (sx, 0, ze), 'UpperTorso')
        J[side + 'LowerArm'] = ((sx, 0, ze), (sx, 0, zw), side + 'UpperArm')
        J[side + 'Hand'] = ((sx, 0, zw), (sx, 0, zf), side + 'LowerArm')
        lx = s * P['lx']
        J[side + 'UpperLeg'] = ((lx, 0, P['hip_z']), (lx, 0, P['knee_z']), 'LowerTorso')
        J[side + 'LowerLeg'] = ((lx, 0, P['knee_z']), (lx, 0, P['fh']), side + 'UpperLeg')
        J[side + 'Foot'] = ((lx, 0, P['fh']), (lx, -P['fl'] * 0.62, P['fh'] * 0.35), side + 'LowerLeg')
    return J

# =====================================================================================  body mesh
def build_body(C, P, M, head_kind='refl', hand_taper=1.0, fist=False, barrel=False, skip=()):
    """R15 parts: 15 *_Geo meshes. M: part -> material (UpperTorso, LowerTorso, UpperArm, LowerArm, Hand, UpperLeg, LowerLeg, Foot, Neck)."""
    C.P = P; J = humanoid_joints(P); C.J = J
    make_rig(C, J)
    p = P['p']; e = min(0.08, P['at'] * 0.22)
    # torso
    if barrel:   # round gentle-big: egg/barrel torso, widest at the belly
        lt0 = P['hip_z'] - 0.16; z1 = P['sh_z']
        secs = [(lt0, P['hw'] * 0.92, P['td'] * 0.92, p), (lt0 + (z1 - lt0) * 0.35, P['ww'], P['td'], p), (lt0 + (z1 - lt0) * 0.7, P['ww'] * 0.92, P['td'] * 0.95, p), (z1, P['sw'], P['td'] * 0.8, p)]
        bm = loft(secs, round_ends=0.18); ut = C.obj('UpperTorso_Geo', bm, M['UpperTorso'], 'UpperTorso', origin=(0, 0, P['waist_z']))
        bm = loft([(lt0, P['hw'] * 0.8, P['td'] * 0.8, 4), (P['hip_z'] + 0.05, P['hw'] * 0.86, P['td'] * 0.86, 4)], round_ends=0.06)
        lt = C.obj('LowerTorso_Geo', bm, M['LowerTorso'], 'LowerTorso', origin=(0, 0, P['hip_z']))
    else:
        bm = loft([(P['hip_z'] - 0.14, P['hw'], P['td'] * 0.96, p), (P['waist_z'] + 0.04, (P['hw'] + P['ww']) / 2, P['td'] * 0.96, p)], round_ends=e)
        lt = C.obj('LowerTorso_Geo', bm, M['LowerTorso'], 'LowerTorso', origin=(0, 0, P['hip_z']))
        zc = P['waist_z'] + (P['sh_z'] - P['waist_z']) * 0.62
        bm = loft([(P['waist_z'] - 0.02, P['ww'], P['td'], p), (zc, P['sw'] * 0.97, P['td'], p), (P['sh_z'], P['sw'], P['td'] * 0.97, p)], round_ends=e)
        ut = C.obj('UpperTorso_Geo', bm, M['UpperTorso'], 'UpperTorso', origin=(0, 0, P['waist_z']))
    C.parts['UpperTorso'] = ut; C.parts['LowerTorso'] = lt
    if P['neck'] > 0.04 and 'Neck' not in skip:
        r = P['head'] * 0.2
        bm = loft([(P['sh_z'] - 0.05, r * 2, r * 2, 2), (P['neck_z'] + 0.08, r * 2, r * 2, 2)], cap=(False, False))
        C.parts['Neck'] = C.obj('Neck_Geo', bm, M.get('Neck', M['Hand']), 'UpperTorso', origin=(0, 0, P['sh_z']))
    # arms
    for side, s in (('Left', 1), ('Right', -1)):
        (h0, h1, _), (l0, l1, _), (a0, a1, _) = J[side + 'UpperArm'], J[side + 'LowerArm'], J[side + 'Hand']
        x = h0[0]; at, ad = P['at'], P['ad']; ov = at * 0.3
        top = P['sjz'] + at * 0.5
        bm = loft([(h1[2] - ov, at * 0.96, ad * 0.96, p, x, 0), (top, at, ad, p, x, 0)], round_ends=e)
        C.parts[side + 'UpperArm'] = C.obj(side + 'UpperArm_Geo', bm, M['UpperArm'], side + 'UpperArm', origin=h0)
        bm = loft([(l1[2] + 0.01, at * 0.92, ad * 0.92, p, x, 0), (l0[2] + ov, at * 0.95, ad * 0.95, p, x, 0)], round_ends=e)
        C.parts[side + 'LowerArm'] = C.obj(side + 'LowerArm_Geo', bm, M['LowerArm'], side + 'LowerArm', origin=l0)
        if fist:
            f = P['hand']; bm = loft([(a1[2] - 0.02, f, f * 0.95, 6, x, -0.02), (a0[2] + 0.06, f, f * 0.95, 6, x, -0.02)], round_ends=f * 0.18)
        else:
            hw_ = at * 0.94; bm = loft([(a1[2], hw_ * hand_taper, ad * 0.62 * hand_taper, max(3, p - 2), x, 0), (a1[2] + P['hand'] * 0.45, hw_, ad * 0.8, p, x, 0), (a0[2] + 0.04, hw_ * 0.96, ad * 0.86, p, x, 0)], round_ends=min(e, P['hand'] * 0.2))
        C.parts[side + 'Hand'] = C.obj(side + 'Hand_Geo', bm, M['Hand'], side + 'Hand', origin=a0)
        # legs
        (u0, u1, _), (k0, k1, _), (f0, f1, _) = J[side + 'UpperLeg'], J[side + 'LowerLeg'], J[side + 'Foot']
        x = u0[0]; lw, ld = P['lgw'], P['lgd']; ov = lw * 0.25
        bm = loft([(u1[2] - ov, lw * 0.96, ld * 0.96, p, x, 0), (P['hip_z'] + 0.04, lw, ld, p, x, 0)], round_ends=e)
        C.parts[side + 'UpperLeg'] = C.obj(side + 'UpperLeg_Geo', bm, M['UpperLeg'], side + 'UpperLeg', origin=u0)
        bm = loft([(P['fh'] - 0.02, lw * 0.94, ld * 0.94, p, x, 0), (k0[2] + ov, lw * 0.95, ld * 0.95, p, x, 0)], round_ends=e)
        C.parts[side + 'LowerLeg'] = C.obj(side + 'LowerLeg_Geo', bm, M['LowerLeg'], side + 'LowerLeg', origin=k0)
        # foot: box along -Y from heel to toe
        fl, fh = P['fl'], P['fh'] + 0.04; fw = lw * 1.02
        bm = loft([(-ld * 0.5 - 0.02, fw, fh, max(4, p - 2)), (fl - ld * 0.5, fw, fh, max(4, p - 2))], round_ends=min(0.07, fh * 0.3))
        xform(bm, Matrix.Translation((x, 0, fh / 2)) @ Matrix.Rotation(math.radians(90), 4, 'X'))
        bmesh.ops.scale(bm, vec=(1, 1, 1), verts=bm.verts)
        C.parts[side + 'Foot'] = C.obj(side + 'Foot_Geo', bm, M['Foot'], side + 'Foot', origin=f0)
    # sockets (Roblox _Att names)
    C.socket('Hat_Att', 'Head', (0, 0, P['top'])); C.socket('FaceCenter_Att', 'Head', (0, -P['head'] * 0.5, P['head_c']))
    C.socket('BodyFront_Att', 'UpperTorso', (0, -P['td'] / 2, (P['waist_z'] + P['sh_z']) / 2)); C.socket('BodyBack_Att', 'UpperTorso', (0, P['td'] / 2, (P['waist_z'] + P['sh_z']) / 2))
    C.socket('Waist_Att', 'LowerTorso', (0, 0, P['waist_z']))
    for side, s in (('Left', 1), ('Right', -1)):
        (a0, a1, _) = J[side + 'Hand']
        C.socket(side + 'Grip_Att', side + 'Hand', (a0[0], -0.0, (a0[2] + a1[2]) / 2))
        C.socket(side + 'Shoulder_Att', 'UpperTorso', (s * P['sx'], 0, P['sh_z']))
    return C.rig

# =====================================================================================  heads + faces
_CMESH = None
def classic_mesh():
    global _CMESH
    if _CMESH is None:
        with bpy.data.libraries.load(CLASSIC_HEAD) as (src, dst): dst.meshes = ['Classic Roblox head geometry']
        _CMESH = dst.meshes[0]
    return _CMESH

def face_material(C, skin, setname, exprs, k, fs=0.86, voff=0.0, cut=0.6, talk=(), blink=None, emissive=None, overlay=None,
                  metallic=0.0, rough=0.5, front=-0.1, coat=0.0, base_override=None, spec=0.5):
    """Decal-face head shader. The head object's integer properties pick the layers:
       face  -> expression index into `exprs`;  mouth -> 0 = expression's own mouth, 1.. = talk mouths (closed, half, open)
       blink -> 1 swaps the eye half for the blink decal;  glow -> scales emissive decals / overlay.
       Image u,v come from the head's object coordinates (planar front projection, like Cast v2's head_mat2)."""
    m = bpy.data.materials.new(C.name + ' | face'); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links
    b = N['Principled BSDF']; b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metallic
    if coat: b.inputs['Coat Weight'].default_value = coat
    b.inputs['Specular IOR Level'].default_value = spec
    tc = N.new('ShaderNodeTexCoord'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Object'], sep.inputs[0])
    span = 1.2 * k * fs
    u = _m(nt, 'MULTIPLY_ADD', sep.outputs[0], 1 / span, 0.5); v = _m(nt, 'MULTIPLY_ADD', sep.outputs[2], 1 / span, 0.5 + voff)
    uv = N.new('ShaderNodeCombineXYZ'); L.new(u, uv.inputs[0]); L.new(v, uv.inputs[1])
    fr = _m(nt, 'LESS_THAN', sep.outputs[1], front * k)
    face = _attr(nt, 'face'); mouth = _attr(nt, 'mouth'); blk = _attr(nt, 'blink'); gl = _attr(nt, 'glow')
    vlow = _m(nt, 'LESS_THAN', v, 1 - cut); vhigh = _m(nt, 'SUBTRACT', 1.0, vlow)
    msw = _m(nt, 'MULTIPLY', vlow, _m(nt, 'GREATER_THAN', mouth, 0.5)) if talk else None
    bsw = _m(nt, 'MULTIPLY', vhigh, _m(nt, 'GREATER_THAN', blk, 0.5)) if blink else None
    keep = 1.0
    if msw is not None: keep = _m(nt, 'SUBTRACT', 1.0, msw)
    if bsw is not None: keep = _m(nt, 'SUBTRACT', keep if not isinstance(keep, float) else 1.0, bsw)
    def img(name):
        path = os.path.join(FACES, setname, name + '.png')
        im = bpy.data.images.get('CV3 ' + setname + ' | ' + name) or bpy.data.images.load(path)
        im.name = 'CV3 ' + setname + ' | ' + name
        t = N.new('ShaderNodeTexImage'); t.image = im; t.extension = 'CLIP'; t.interpolation = 'Cubic'; L.new(uv.outputs[0], t.inputs[0]); return t
    col = base_override(nt) if callable(base_override) else (base_override if base_override is not None else rgba(skin))
    em = (0.0, 0.0, 0.0, 1.0); efac_total = None
    for i, e in enumerate(exprs):
        t = img(e); eq = _m(nt, 'COMPARE', face, float(i), 0.5)
        fac = _m(nt, 'MULTIPLY', _m(nt, 'MULTIPLY', eq, t.outputs['Alpha']), fr)
        if not isinstance(keep, float): fac = _m(nt, 'MULTIPLY', fac, keep)
        col = _mixc(nt, col, t.outputs['Color'], fac)
        if emissive: em = _mixc(nt, em, t.outputs['Color'], fac)
    for j, e in enumerate(talk, start=1):
        t = img(e); eq = _m(nt, 'COMPARE', mouth, float(j), 0.5)
        fac = _m(nt, 'MULTIPLY', _m(nt, 'MULTIPLY', _m(nt, 'MULTIPLY', eq, t.outputs['Alpha']), fr), vlow)
        col = _mixc(nt, col, t.outputs['Color'], fac)
    if blink:
        t = img(blink); fac = _m(nt, 'MULTIPLY', _m(nt, 'MULTIPLY', bsw, t.outputs['Alpha']), fr)
        col = _mixc(nt, col, t.outputs['Color'], fac)
    if overlay:
        t = img(overlay); fac = _m(nt, 'MULTIPLY', _m(nt, 'MULTIPLY', gl, t.outputs['Alpha']), fr)
        if bsw is not None: fac = _m(nt, 'MULTIPLY', fac, _m(nt, 'SUBTRACT', 1.0, bsw))     # phase 2: a glowing eye closes with the blink
        col = _mixc(nt, col, t.outputs['Color'], fac)
        em = _mixc(nt, em, t.outputs['Color'], fac)
        L.new(em, b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = 7.0
    if emissive:
        L.new(em, b.inputs['Emission Color']); L.new(_m(nt, 'MULTIPLY', gl, emissive), b.inputs['Emission Strength'])
    if isinstance(col, tuple): b.inputs['Base Color'].default_value = col
    else: L.new(col, b.inputs['Base Color'])
    return m

def drive(ob, prop, rig, rprop):
    fc = ob.driver_add('["%s"]' % prop); d = fc.driver; d.type = 'SCRIPTED'
    v = d.variables.new(); v.name = 'v'; v.targets[0].id = rig; v.targets[0].data_path = '["%s"]' % rprop; d.expression = 'v'

def make_head(C, P, skin, face_cfg, kind='refl', mat=None):
    """rounded head (Reflection cylinder like Cast v2, or the classic Roblox head) carrying the decal-face material.
    Rig properties face/mouth/blink/glow drive the head's own properties that the shader reads."""
    h = P['head']; k = h / 1.2; zc = P['head_c']
    if kind == 'classic':
        me = classic_mesh().copy(); me.name = C.name + ' | Head_Geo'
        vs = [v.co for v in me.vertices]; mn = Vector((min(v.x for v in vs), min(v.y for v in vs), min(v.z for v in vs))); mx = Vector((max(v.x for v in vs), max(v.y for v in vs), max(v.z for v in vs)))
        sc = h / (mx - mn).z; me.transform(Matrix.Scale(sc, 4) @ Matrix.Translation(-(mn + mx) / 2))
        for pl in me.polygons: pl.use_smooth = True
        bm = bmesh.new(); bm.from_mesh(me); bpy.data.meshes.remove(me)
        bmesh.ops.translate(bm, vec=(0, 0, zc), verts=bm.verts)
        ob = C.obj('Head_Geo', bm, None, 'Head', origin=(0, 0, zc))
    elif kind == 'block':      # phase 2 (Horde): a bevelled block head, classic R6 monster
        bm = cube_bm(h * 1.04, h * 0.92, h); bmesh.ops.translate(bm, vec=(0, 0, zc), verts=bm.verts)
        ob = C.obj('Head_Geo', bm, None, 'Head', origin=(0, 0, zc), smooth=False)
        bv = ob.modifiers.new('bevel', 'BEVEL'); bv.width = 0.1 * k; bv.segments = 3; bv.limit_method = 'ANGLE'; bv.harden_normals = True
    else:
        bm = bmesh.new(); bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=40, radius1=0.6 * k, radius2=0.6 * k, depth=1.2 * k)
        bmesh.ops.translate(bm, vec=(0, 0, zc), verts=bm.verts)
        ob = C.obj('Head_Geo', bm, None, 'Head', origin=(0, 0, zc))
        bv = ob.modifiers.new('bevel', 'BEVEL'); bv.width = 0.22 * k; bv.segments = 5; bv.limit_method = 'ANGLE'
    # planar front UVs (used only by the glTF backup bake)
    me = ob.data; uvl = me.uv_layers.new(name='FaceUV')
    span = 1.2 * k * face_cfg.get('fs', 0.86)
    for poly in me.polygons:
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            uvl.data[li].uv = (co.x / span + 0.5, co.z / span + 0.5 + face_cfg.get('voff', 0.0)) if poly.normal.y < -0.1 else (0.002, 0.002)
    fm = mat or face_material(C, skin, face_cfg['set'], face_cfg['exprs'], k, fs=face_cfg.get('fs', 0.86), voff=face_cfg.get('voff', 0.0),
                              cut=face_cfg.get('cut', 0.6), talk=face_cfg.get('talk', ()), blink=face_cfg.get('blink'), emissive=face_cfg.get('emissive'),
                              overlay=face_cfg.get('overlay'), metallic=face_cfg.get('metallic', 0.0), rough=face_cfg.get('rough', 0.5), coat=face_cfg.get('coat', 0.0), spec=face_cfg.get('spec', 0.5))
    me.materials.append(fm)
    rig = C.rig
    names = list(face_cfg['exprs'])
    rig['face'] = face_cfg.get('default', 0); rig['mouth'] = 0; rig['blink'] = 0; rig['glow'] = face_cfg.get('glow', 1.0)
    rig['face_names'] = ', '.join('%d %s' % (i, n) for i, n in enumerate(names))
    rig['mouth_names'] = '0 expression, ' + ', '.join('%d %s' % (j, n.replace('talk_', '')) for j, n in enumerate(face_cfg.get('talk', ()), start=1)) if face_cfg.get('talk') else 'no talk set'
    for pr in ('face', 'mouth', 'blink', 'glow'):
        ob[pr] = rig[pr]; drive(ob, pr, rig, pr)
    try:
        ui = rig.id_properties_ui('face'); ui.update(min=0, max=len(names) - 1, description=rig['face_names'])
        ui = rig.id_properties_ui('mouth'); ui.update(min=0, max=len(face_cfg.get('talk', ())), description=rig['mouth_names'])
        ui = rig.id_properties_ui('blink'); ui.update(min=0, max=1)
    except Exception: pass
    C.head = ob; C.parts['Head'] = ob
    return ob

def add_hair(C, key, rgb, scale=0.9, offset=(0, 0, 0), name='Hair'):
    P = C.P; before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=HAIRDIR + key + '/' + key + '_hair.glb')
    new = [o for o in bpy.data.objects if o not in before]
    keep = [o for o in new if o.type == 'MESH' and not o.name.startswith('Icosphere')]
    bm = bmesh.new()
    for o in keep:
        me = o.data.copy(); me.transform(o.matrix_world); tmp = bmesh.new(); tmp.from_mesh(me)
        tmp.to_mesh(me); bm.from_mesh(me); bpy.data.meshes.remove(me); tmp.free()
    for o in new: bpy.data.objects.remove(o, do_unlink=True)
    s = scale * P['head'] / 1.2
    xform(bm, Matrix.Translation((offset[0], offset[1], P['head_c'] + offset[2])) @ Matrix.Scale(s, 4))
    return C.obj(name, bm, hair_mat(C.name + ' hair', rgb), 'Head', origin=(0, 0, P['head_c']))

# =====================================================================================  poses
def _norm(v): v = Vector(v); return v.normalized()

def base_pose_dirs(C, name):
    """direction targets (armature space: +X = character's left, -Y = forward, +Z = up) for the shared pose set."""
    P = C.P; D = {}
    out_a = math.radians(P.get('idle_out', 7))
    def arms(fn):
        for side, s in (('Left', 1), ('Right', -1)): fn(side, s)
    if name == 'idle':
        def f(side, s):
            D[side + 'UpperArm'] = (s * math.sin(out_a), 0.0, -math.cos(out_a)); D[side + 'LowerArm'] = (s * math.sin(out_a) * 0.8, -0.14, -1); D[side + 'Hand'] = (s * 0.05, -0.12, -1)
        arms(f)
        for side, s in (('Left', 1), ('Right', -1)): D[side + 'UpperLeg'] = (s * 0.04, 0, -1); D[side + 'LowerLeg'] = (s * 0.04, 0, -1)
    elif name == 'point':
        D['RightUpperArm'] = (-0.74, -0.62, 0.16); D['RightLowerArm'] = (-0.74, -0.62, 0.16); D['RightHand'] = (-0.72, -0.64, 0.14)
        D['LeftUpperArm'] = (math.sin(out_a), 0, -math.cos(out_a)); D['LeftLowerArm'] = (0.1, -0.2, -1)
        D['UpperTorso'] = ((0, -0.04, 1), -10); D['Head'] = ((0, 0, 1), -14)
    elif name == 'laugh':
        D['Head'] = (0, 0.42, 0.9); D['UpperTorso'] = (0, 0.16, 1)
        def f(side, s):
            D[side + 'UpperArm'] = (s * 0.5, -0.05, -0.86); D[side + 'LowerArm'] = (-s * 0.72, -0.62, -0.1); D[side + 'Hand'] = (-s * 0.5, -0.6, -0.5)
        arms(f)
    elif name == 'shocked':
        D['Head'] = (0, 0.18, 1); D['UpperTorso'] = (0, 0.1, 1)
        def f(side, s):
            D[side + 'UpperArm'] = (s * 0.8, -0.25, -0.3); D[side + 'LowerArm'] = (s * 0.18, -0.3, 1); D[side + 'Hand'] = (s * 0.1, -0.2, 1)
        arms(f)
    elif name == 'fists_up':
        D['UpperTorso'] = (0, -0.12, 1); D['Head'] = (0, -0.04, 1)
        def f(side, s):
            D[side + 'UpperArm'] = (s * 0.36, -0.55, -0.75); D[side + 'LowerArm'] = (-s * 0.42, -0.5, 0.76); D[side + 'Hand'] = (-s * 0.3, -0.4, 0.86)
        arms(f)
        D['LeftUpperLeg'] = (0.16, 0.08, -1); D['LeftLowerLeg'] = (0.16, 0.08, -1); D['RightUpperLeg'] = (-0.14, -0.14, -1); D['RightLowerLeg'] = (-0.1, 0.0, -1)
    elif name == 'arms_crossed':
        # elbows forward of the chest; right forearm low and close, left forearm higher and in front (they never meet)
        ua, at, ad, td = P['ua'], P['at'], P['ad'], P['td'] + 2 * P.get('chest_extra', 0.0)
        ye_r = -(td / 2 + ad / 2 + 0.04); ye_l = ye_r - ad * 0.95
        dz_r = -math.sqrt(max(0.05, ua * ua - ye_r * ye_r - (0.08 * ua) ** 2)); z_r = dz_r
        dz_l = z_r + at * 1.1
        dx_l = math.sqrt(max(0.0, ua * ua - ye_l * ye_l - dz_l * dz_l))
        D['RightUpperArm'] = (-0.08 * ua, ye_r, dz_r); D['LeftUpperArm'] = (dx_l, ye_l, dz_l)
        D['RightLowerArm'] = (1.0, -0.06, 0.1); D['LeftLowerArm'] = (-1.0, -0.06, 0.04)
        D['RightHand'] = (0.45, 0.55, -0.2); D['LeftHand'] = (-0.45, 0.5, -0.25)
        D['Head'] = (0, 0.06, 1)
    return D

def pose_quats(rig, spec):
    """turn direction targets into local pose quaternions (rest-relative), walking the hierarchy root-first."""
    posed = {}; Q = {}
    order = []
    def walk(b):
        order.append(b)
        for c in b.children: walk(c)
    for b in rig.data.bones:
        if b.parent is None: walk(b)
    for b in order:
        Rb = b.matrix_local.to_3x3()
        if b.parent:
            Rp = b.parent.matrix_local.to_3x3(); Pp = posed[b.parent.name]
        else:
            Rp = Matrix.Identity(3); Pp = Matrix.Identity(3)
        inherit = Pp @ Rp.inverted() @ Rb
        Pb = inherit
        if b.name in spec and spec[b.name] is not None:
            sp = spec[b.name]; twist = 0.0
            if isinstance(sp, tuple) and len(sp) == 2 and isinstance(sp[0], (tuple, list)): sp, twist = sp
            d = _norm(sp); cur = inherit.col[1].normalized()
            q = cur.rotation_difference(d)
            Pb = q.to_matrix() @ inherit
            if twist: Pb = Pb @ Matrix.Rotation(math.radians(twist), 3, 'Y')
        posed[b.name] = Pb
        L_ = (Rp.inverted() @ Rb).inverted() @ Pp.inverted() @ Pb
        Q[b.name] = L_.to_quaternion()
    return Q

def set_pose(rig, quats):
    for pb in rig.pose.bones:
        pb.rotation_mode = 'QUATERNION'; pb.location = (0, 0, 0)
        pb.rotation_quaternion = quats.get(pb.name, Quaternion())

def store_poses(C, poses, default):
    """poses: name -> direction spec. Stores quaternions as JSON on the rig ('poses') and as one-frame Action assets."""
    rig = C.rig; table = {}
    for name, spec in poses.items():
        Q = pose_quats(rig, spec); table[name] = {b: [round(x, 6) for x in q] for b, q in Q.items()}
    rig['poses'] = json.dumps(table); rig['pose_names'] = ', '.join(poses.keys()); rig['default_pose'] = default
    for name in poses:
        set_pose(rig, {b: Quaternion(v) for b, v in table[name].items()})
        act = bpy.data.actions.new('%s | pose %s' % (C.name, name))
        rig.animation_data_create(); rig.animation_data.action = act
        for pb in rig.pose.bones: pb.keyframe_insert('rotation_quaternion', frame=1, group=pb.name)
        act.use_fake_user = True
        try:
            act.asset_mark(); act.asset_data.description = '%s: %s pose (Cast v3)' % (C.name, name); act.asset_data.catalog_simple_name = 'Cast v3'
        except Exception: pass
        rig.animation_data.action = None
    set_pose(rig, {b: Quaternion(v) for b, v in table[default].items()})
    return table

def apply_named_pose(rig, name):
    table = json.loads(rig['poses']); set_pose(rig, {b: Quaternion(v) for b, v in table[name].items()})
