# Lightning Arms model kit: shared helpers (mesh builder, primitives, materials, armature, poses).
# Units: 1 m = 3.3 BU. Front of every asset is -Y, up is +Z, origin at the base centre.
import bpy, bmesh, math, random
import numpy as np
from mathutils import Vector, Matrix, Quaternion, noise

R = math.radians


def lin(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(((x + 0.055) / 1.055) ** 2.4 if x > 0.04045 else x / 12.92 for x in c)


def tint(target, base):
    """per-channel multiplier (<=1) that turns material colour `base` into `target`"""
    t, b = lin(target), lin(base)
    return tuple(min(1.0, t[i] / max(b[i], 1e-4)) for i in range(3))


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    for blk in (bpy.data.meshes, bpy.data.materials, bpy.data.images, bpy.data.actions):
        for b in list(blk):
            blk.remove(b)


def coll(name, parent=None):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    p = parent or bpy.context.scene.collection
    if c.name not in p.children:
        p.children.link(c)
    return c


# ---------------------------------------------------------------- materials
def mat(name, hexcol, rough=0.85, emit=None, estr=0.0, spec=0.25, vcol=True):
    full = 'LA_Mat_' + name
    m = bpy.data.materials.get(full)
    if m:
        return m
    m = bpy.data.materials.new(full)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    c = lin(hexcol)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Specular IOR Level'].default_value = spec
    b.inputs['Base Color'].default_value = (*c, 1)
    if vcol:
        va = nt.nodes.new('ShaderNodeVertexColor'); va.layer_name = 'Col'; va.location = (-500, 200)
        mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.location = (-250, 200)
        mx.inputs['Factor'].default_value = 1.0
        mx.inputs['A'].default_value = (*c, 1)
        nt.links.new(va.outputs['Color'], mx.inputs['B'])
        nt.links.new(mx.outputs['Result'], b.inputs['Base Color'])
    if emit:
        b.inputs['Emission Color'].default_value = (*lin(emit), 1)
        b.inputs['Emission Strength'].default_value = estr
    m.diffuse_color = (*c, 1)
    return m


def image_mat(name, img, rough=0.85, alpha=True, atlas_n=1, prop='face', emit=0.0):
    """Image material. With atlas_n>1 the U coordinate is shifted by the object's custom property `prop`
    (0..atlas_n-1): the UV map covers cell 0, the shader adds prop/atlas_n."""
    m = bpy.data.materials.new('LA_Mat_' + name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = rough
    b.inputs['Specular IOR Level'].default_value = 0.15
    tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = img; tex.name = tex.label = 'LA_FACE_TEX'
    tex.location = (-350, 250); tex.extension = 'EXTEND'
    if atlas_n > 1:
        uv = nt.nodes.new('ShaderNodeUVMap'); uv.location = (-1100, 250)
        at = nt.nodes.new('ShaderNodeAttribute'); at.attribute_type = 'OBJECT'; at.attribute_name = prop
        at.location = (-1100, 50); at.name = at.label = 'LA_FACE_INDEX'
        rd = nt.nodes.new('ShaderNodeMath'); rd.operation = 'ROUND'; rd.location = (-900, 50)
        dv = nt.nodes.new('ShaderNodeMath'); dv.operation = 'DIVIDE'; dv.inputs[1].default_value = atlas_n
        dv.location = (-740, 50)
        cx = nt.nodes.new('ShaderNodeCombineXYZ'); cx.location = (-580, 50)
        ad = nt.nodes.new('ShaderNodeVectorMath'); ad.operation = 'ADD'; ad.location = (-520, 250)
        nt.links.new(at.outputs['Fac'], rd.inputs[0]); nt.links.new(rd.outputs[0], dv.inputs[0])
        nt.links.new(dv.outputs[0], cx.inputs[0])
        nt.links.new(uv.outputs['UV'], ad.inputs[0]); nt.links.new(cx.outputs[0], ad.inputs[1])
        nt.links.new(ad.outputs[0], tex.inputs['Vector'])
    nt.links.new(tex.outputs['Color'], b.inputs['Base Color'])
    if alpha:
        nt.links.new(tex.outputs['Alpha'], b.inputs['Alpha'])
        try:
            m.surface_render_method = 'BLENDED'
        except Exception:
            pass
    if emit:
        nt.links.new(tex.outputs['Color'], b.inputs['Emission Color'])
        b.inputs['Emission Strength'].default_value = emit
    return m


# ---------------------------------------------------------------- primitives (numpy verts, list faces)
_ICO = {}


def ico(sub):
    if sub not in _ICO:
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0)
        v = np.array([x.co[:] for x in bm.verts])
        v /= np.linalg.norm(v, axis=1)[:, None]
        f = [[x.index for x in p.verts] for p in bm.faces]
        bm.free()
        _ICO[sub] = (v, f)
    v, f = _ICO[sub]
    return v.copy(), [list(x) for x in f]


def blob(c, r, sub=2, amp=0.1, freq=1.2, seed=0, cuts=0, cut_depth=(0.80, 0.93), floor=None, rot=None):
    """noisy, optionally chiselled ellipsoid. c centre, r radius or (rx, ry, rz)."""
    v, f = ico(sub)
    rng = random.Random(seed)
    off = Vector((seed * 7.13 + 1.1, seed * 3.31 + 2.2, seed * 1.77 + 3.3))
    if amp:
        for i in range(len(v)):
            n = noise.noise(Vector(v[i]) * freq + off)
            v[i] *= 1.0 + amp * n * 1.8
    for _ in range(cuts):
        d = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-0.6, 1))).normalized()
        d = np.array(d[:])
        dist = rng.uniform(*cut_depth)
        s = v @ d - dist
        m = s > 0
        v[m] -= np.outer(s[m], d)
    r = np.array((r, r, r) if np.isscalar(r) else r, float)
    v *= r
    if rot is not None:
        v = v @ np.array(rot.to_3x3()).T
    v += np.array(c, float)
    if floor is not None:
        v[:, 2] = np.maximum(v[:, 2], floor)
    return v, f


def spline(pts, n):
    """Catmull-Rom through pts, n samples evenly spaced by arc length."""
    p = np.array(pts, float)
    p = np.vstack([2 * p[0] - p[1], p, 2 * p[-1] - p[-2]])
    dense = []
    for i in range(1, len(p) - 2):
        for t in np.linspace(0, 1, 24, endpoint=False):
            a, b, c, d = p[i - 1], p[i], p[i + 1], p[i + 2]
            dense.append(0.5 * ((2 * b) + (-a + c) * t + (2 * a - 5 * b + 4 * c - d) * t * t + (-a + 3 * b - 3 * c + d) * t ** 3))
    dense.append(p[-2])
    dense = np.array(dense)
    seg = np.linalg.norm(np.diff(dense, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    tt = np.linspace(0, s[-1], n)
    return np.stack([np.interp(tt, s, dense[:, k]) for k in range(3)], axis=1)


def walk(pts, step, count, start=None):
    """points spaced exactly `step` apart along the smooth curve through pts (count+1 points)."""
    dense = spline(pts, 2000)
    out = [dense[0] if start is None else np.array(start, float)]
    i = 0
    while len(out) < count + 1:
        while i < len(dense) and np.linalg.norm(dense[i] - out[-1]) < step:
            i += 1
        if i >= len(dense):
            d = dense[-1] - dense[-30]
            d /= np.linalg.norm(d)
            out.append(out[-1] + d * step)
        else:
            d = dense[i] - out[-1]
            out.append(out[-1] + d / np.linalg.norm(d) * step)
    return np.array(out)


def tube(pts, radii, segs=10, cap0=False, cap1=True, lobes=0, lobe_amp=0.0, tip=0.6):
    """tube along a polyline. Returns verts, faces, ring index per vertex."""
    p = np.array(pts, float)
    n = len(p)
    radii = np.full(n, radii, float) if np.isscalar(radii) else np.array(radii, float)
    tan = np.gradient(p, axis=0)
    tan /= np.linalg.norm(tan, axis=1)[:, None]
    up = np.array((0.0, 0.0, 1.0)) if abs(tan[0][2]) < 0.9 else np.array((0.0, 1.0, 0.0))
    nrm = np.cross(tan[0], np.cross(up, tan[0])); nrm /= np.linalg.norm(nrm)
    V, ring = [], []
    for i in range(n):
        if i:
            nrm = nrm - tan[i] * (nrm @ tan[i]); nrm /= np.linalg.norm(nrm)
        bi = np.cross(tan[i], nrm)
        for k in range(segs):
            a = 2 * math.pi * k / segs
            rr = radii[i] * (1 + lobe_amp * math.cos(lobes * a) if lobes else 1)
            V.append(p[i] + rr * (math.cos(a) * nrm + math.sin(a) * bi)); ring.append(i)
    F = []
    for i in range(n - 1):
        for k in range(segs):
            a, b = i * segs + k, i * segs + (k + 1) % segs
            F.append([a, b, b + segs, a + segs])
    if cap0:
        V.append(p[0] - tan[0] * radii[0] * tip); ring.append(0); c = len(V) - 1
        F += [[c, (k + 1) % segs, k] for k in range(segs)]
    if cap1:
        V.append(p[-1] + tan[-1] * radii[-1] * tip); ring.append(n - 1); c = len(V) - 1
        b0 = (n - 1) * segs
        F += [[c, b0 + k, b0 + (k + 1) % segs] for k in range(segs)]
    return np.array(V), F, np.array(ring)


def lathe(profile, segs=24, cap_bottom=True, cap_top=True, phase=0.0):
    """revolve [(r, z), ...] around Z."""
    V, F = [], []
    n = len(profile)
    for (r, z) in profile:
        for k in range(segs):
            a = 2 * math.pi * k / segs + phase
            V.append((r * math.cos(a), r * math.sin(a), z))
    for i in range(n - 1):
        for k in range(segs):
            a, b = i * segs + k, i * segs + (k + 1) % segs
            F.append([a, b, b + segs, a + segs])
    if cap_bottom:
        F.append(list(range(segs))[::-1])
    if cap_top:
        F.append([(n - 1) * segs + k for k in range(segs)])
    return np.array(V, float), F


def box(size, center=(0, 0, 0), bevel=0.0, segs=2):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=bevel, segments=segs, profile=0.5, affect='EDGES')
    bm.verts.ensure_lookup_table()
    v = np.array([x.co[:] for x in bm.verts]) + np.array(center, float)
    f = [[x.index for x in p.verts] for p in bm.faces]
    bm.free()
    return v, f


def xf(v, M):
    M = np.array(M)
    return v @ M[:3, :3].T + M[:3, 3]


def rotz(v, deg):
    return xf(v, Matrix.Rotation(R(deg), 4, 'Z'))


def leaf(length=1.0, width=0.45, fold=0.12, curl=0.15):
    """a simple low-poly leaf lying along +Y from the origin, top side +Z. Returns verts, faces."""
    prof = [(0.0, 0.0), (0.18, 0.62), (0.45, 1.0), (0.75, 0.72), (1.0, 0.0)]
    V = []
    for (t, w) in prof:
        z = curl * length * (t * t) * -1.0 + curl * length * t * 0.6
        V += [(-w * width * length, t * length, z + fold * w * length), (0, t * length, z), (w * width * length, t * length, z + fold * w * length)]
    V = np.array(V, float)
    F = []
    for i in range(len(prof) - 1):
        a = i * 3
        F += [[a, a + 1, a + 4, a + 3], [a + 1, a + 2, a + 5, a + 4]]
    return V, F


def align(v, direction, origin=(0, 0, 0), axis='Z', spin=0.0):
    """rotate verts so local `axis` points along direction, then move to origin."""
    d = Vector(direction).normalized()
    q = Vector((0, 0, 1) if axis == 'Z' else (0, 1, 0)).rotation_difference(d)
    M = Matrix.Translation(Vector(origin)) @ q.to_matrix().to_4x4() @ Matrix.Rotation(spin, 4, axis)
    return xf(v, M)


# ---------------------------------------------------------------- mesh builder
class MB:
    def __init__(s):
        s.V, s.F, s.FM, s.FS, s.FC, s.VC, s.VW, s.UV = [], [], [], [], [], [], [], []
        s.n = 0
        s.has_uv = False

    def add(s, v, f, mat=0, col=(1, 1, 1), fjit=0.0, w=None, flat=False, uv=None, seed=0, shade=None):
        """col: rgb multiplier, (n,3) array or function(vert)->rgb. fjit: random per-face brightness jitter.
        shade=(z0, z1, k): darken to k at z0, 1 at z1. w: bone name or list of {bone: weight} per vertex."""
        v = np.asarray(v, float)
        n = len(v)
        if callable(col):
            c = np.array([col(p) for p in v], float)
        else:
            c = np.array(col, float)
            if c.ndim == 1:
                c = np.tile(c, (n, 1))
        if shade:
            z0, z1, k = shade
            t = np.clip((v[:, 2] - z0) / max(z1 - z0, 1e-6), 0, 1)
            c = c * (k + (1 - k) * t)[:, None]
        rng = random.Random(seed * 131 + len(s.F))
        s.V.append(v); s.VC.append(np.clip(c, 0, 1))
        for face in f:
            s.F.append([i + s.n for i in face]); s.FM.append(mat); s.FS.append(not flat)
            s.FC.append(1.0 - fjit * rng.random())
        if w is None:
            s.VW += [None] * n
        elif isinstance(w, str):
            s.VW += [{w: 1.0}] * n
        else:
            s.VW += list(w)
        if uv is not None:
            s.has_uv = True
            s.UV.append(np.asarray(uv, float))
        else:
            s.UV.append(np.zeros((n, 2)))
        s.n += n
        return s

    def obj(s, name, mats, collection, arm=None, parent=None, sharp=40.0, parent_bone=None):
        V = np.vstack(s.V); VC = np.vstack(s.VC); UV = np.vstack(s.UV)
        me = bpy.data.meshes.new(name)
        me.from_pydata(V.tolist(), [], s.F)
        me.update()
        for m in mats:
            me.materials.append(m)
        me.polygons.foreach_set('material_index', s.FM)
        me.polygons.foreach_set('use_smooth', s.FS)
        ca = me.color_attributes.new('Col', 'BYTE_COLOR', 'CORNER')
        li = np.zeros(len(me.loops), int); me.loops.foreach_get('vertex_index', li)
        cols = np.ones((len(me.loops), 4))
        k = 0
        for fi, p in enumerate(me.polygons):
            for _ in range(p.loop_total):
                cols[k, :3] = VC[li[k]] * s.FC[fi]; k += 1
        ca.data.foreach_set('color', cols.ravel())
        if s.has_uv:
            ul = me.uv_layers.new(name='UVMap')
            ul.data.foreach_set('uv', UV[li].ravel())
        try:
            me.set_sharp_from_angle(angle=R(sharp))
        except Exception:
            pass
        o = bpy.data.objects.new(name, me)
        collection.objects.link(o)
        groups = {}
        for i, w in enumerate(s.VW):
            if not w:
                continue
            for g, val in w.items():
                if val <= 0.001:
                    continue
                if g not in groups:
                    groups[g] = o.vertex_groups.new(name=g)
                groups[g].add([i], float(val), 'REPLACE')
        if arm is not None:
            o.parent = arm
            if parent_bone:
                o.parent_type = 'BONE'; o.parent_bone = parent_bone
            else:
                md = o.modifiers.new('LA_Armature', 'ARMATURE'); md.object = arm
        elif parent is not None:
            o.parent = parent
        me.validate()
        add_rest(o)
        return o


# ---------------------------------------------------------------- armature and poses
def make_arm(name, bones, collection):
    """bones: [(name, head, tail, parent or None, connect)]; all rolls aligned so local X ~ world X when possible."""
    ad = bpy.data.armatures.new(name)
    ob = bpy.data.objects.new(name, ad)
    collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode='EDIT')
    for (bn, head, tail, par, con) in bones:
        eb = ad.edit_bones.new(bn)
        eb.head = Vector(head); eb.tail = Vector(tail)
        d = (eb.tail - eb.head).normalized()
        eb.align_roll(Vector((0, -1, 0)) if abs(d.y) < 0.9 else Vector((0, 0, 1)))
        if par:
            eb.parent = ad.edit_bones[par]; eb.use_connect = con
    bpy.ops.object.mode_set(mode='OBJECT')
    for pb in ob.pose.bones:
        pb.rotation_mode = 'QUATERNION'
    ad.display_type = 'STICK'
    return ob


def pose_reset(arm):
    for pb in arm.pose.bones:
        pb.location = (0, 0, 0); pb.rotation_quaternion = (1, 0, 0, 0); pb.scale = (1, 1, 1)
    bpy.context.view_layer.update()


def pose_chain(arm, names, pts):
    """aim a connected bone chain along the points (len(names)+1), armature space."""
    pts = [Vector(p) for p in pts]
    for i, bn in enumerate(names):
        pb = arm.pose.bones[bn]
        bpy.context.view_layer.update()
        M = pb.matrix.copy()
        q = M.to_quaternion()
        d = (pts[i + 1] - pts[i]).normalized()
        dq = (q @ Vector((0, 1, 0))).rotation_difference(d)
        pb.matrix = Matrix.LocRotScale(M.translation, dq @ q, None)
    bpy.context.view_layer.update()


def pose_rot(arm, bn, axis, deg):
    """rotate a pose bone about an armature-space axis through its head."""
    pb = arm.pose.bones[bn]
    bpy.context.view_layer.update()
    M = pb.matrix.copy()
    h = M.translation.copy()
    Rm = Matrix.Translation(h) @ Matrix.Rotation(R(deg), 4, axis) @ Matrix.Translation(-h)
    pb.matrix = Rm @ M
    bpy.context.view_layer.update()


def pose_move(arm, bn, vec):
    pb = arm.pose.bones[bn]
    bpy.context.view_layer.update()
    M = pb.matrix.copy()
    pb.matrix = Matrix.Translation(Vector(vec)) @ M
    bpy.context.view_layer.update()


def save_action(arm, name, frame=1, keys=None):
    """store the current pose as a one-frame action (also a pose asset). keys: extra frames via callback list."""
    if arm.animation_data is None:
        arm.animation_data_create()
    act = bpy.data.actions.new(name)
    arm.animation_data.action = act
    for pb in arm.pose.bones:
        pb.keyframe_insert('location', frame=frame)
        pb.keyframe_insert('rotation_quaternion', frame=frame)
        pb.keyframe_insert('scale', frame=frame)
    act.use_fake_user = True
    try:
        act.asset_mark()
    except Exception:
        pass
    arm.animation_data.action = None
    return act


def pose_dict(arm):
    return {pb.name: {'loc': [round(x, 5) for x in pb.location], 'quat': [round(x, 6) for x in pb.rotation_quaternion],
                      'scale': [round(x, 5) for x in pb.scale]} for pb in arm.pose.bones}


def push_nla(arm, actions):
    """park every action on a muted NLA track so it travels with the armature on append."""
    ad = arm.animation_data
    ad.action = None
    for a in actions:
        tr = ad.nla_tracks.new(); tr.name = a.name
        st = tr.strips.new(a.name, 1, a)
        st.name = a.name
        tr.mute = True


# ================================================================ Lightning Arms additions
_CUBE = {}


def _cube(sub):
    if sub not in _CUBE:
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=2.0)
        if sub > 0:
            bmesh.ops.subdivide_edges(bm, edges=list(bm.edges), cuts=sub, use_grid_fill=True)
        bm.verts.ensure_lookup_table()
        v = np.array([x.co[:] for x in bm.verts])
        f = [[x.index for x in p.verts] for p in bm.faces]
        bm.free()
        _CUBE[sub] = (v, f)
    v, f = _CUBE[sub]
    return v.copy(), [list(x) for x in f]


def crag(size, c=(0, 0, 0), sub=4, amp=0.085, freq=1.5, seed=0, cuts=6, depth=(0.74, 0.93), rnd=0.10, taper=(1.0, 1.0),
         rot=None, floor=None, protect=None, pamp=0.25):
    """chiselled stone block. size (x, y, z) full extents, c centre. Subdivided cube, slightly rounded, noise, then
    random corner / edge plane cuts (flat facets). taper = (x, y) scale of the TOP relative to the bottom.
    protect: unit vector of a face to keep flat and uncut (noise there is scaled by pamp)."""
    v, f = _cube(sub)
    rng = random.Random(seed * 977 + 13)
    off = Vector((seed * 7.13 + 1.1, seed * 3.31 + 2.2, seed * 1.77 + 3.3))
    # round the cube a little
    ln = np.linalg.norm(v, axis=1)[:, None]
    sph = v / ln * 1.25
    v = v * (1 - rnd) + sph * rnd
    pr = np.array(Vector(protect).normalized()[:]) if protect is not None else None
    if amp:
        for i in range(len(v)):
            n = noise.noise(Vector(v[i]) * freq + off) + 0.5 * noise.noise(Vector(v[i]) * freq * 2.3 + off)
            k = amp * n * 1.6
            if pr is not None and v[i] @ pr > 0.82:
                k *= pamp
            v[i] *= 1.0 + k
    for _ in range(int(cuts * 1.7)):
        for _try in range(20):
            d = np.array([rng.choice((-1, 0, 1)) + rng.uniform(-0.35, 0.35) for _ in range(3)])
            if np.linalg.norm(d) < 0.6:
                continue
            d /= np.linalg.norm(d)
            if pr is not None and d @ pr > 0.25:
                continue
            break
        sup = np.abs(d).sum()
        dist = sup * rng.uniform(*depth)
        s = v @ d - dist
        m = s > 0
        v[m] -= np.outer(s[m], d)
    if taper != (1.0, 1.0):
        t = (v[:, 2] + 1) / 2
        v[:, 0] *= 1 + (taper[0] - 1) * t
        v[:, 1] *= 1 + (taper[1] - 1) * t
    v *= np.array(size, float) / 2
    if rot is not None:
        v = v @ np.array(rot.to_3x3()).T
    v += np.array(c, float)
    if floor is not None:
        v[:, 2] = np.maximum(v[:, 2], floor)
    return v, f


def rockcol(base=(1, 1, 1), seed=0, scale=0.09, amp=0.16, warm=0.05):
    """vertex colour function: large soft blotches + a warm / cool drift, so stone is never one flat tone."""
    off = Vector((seed * 2.7 + 5, seed * 1.3 + 9, seed * 4.1 + 2))
    b = np.array(base, float)

    def fn(p):
        q = Vector(p) * scale + off
        n = noise.noise(q) + 0.5 * noise.noise(q * 2.7)
        w = noise.noise(q * 0.6 + Vector((31, 7, 3)))
        k = 1.0 + amp * n
        return np.clip(b * k * np.array((1 + warm * w, 1.0, 1 - warm * w)), 0, 1)
    return fn


def stone_mat(name, hexcol, rough=0.92, bump=0.35, scale=0.35, ao=True, mottle=0.14, spec=0.2):
    """rock material: flat colour x vertex colour `Col`, plus Cycles-only extras that the .glb simply drops:
    fine procedural mottling + bump read from the `rest` position attribute (stable under the rig) and soft AO in the crevices."""
    full = 'LA_Mat_' + name
    m = bpy.data.materials.get(full)
    if m:
        return m
    m = mat(name, hexcol, rough=rough, spec=spec)
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    mx = [n for n in nt.nodes if n.type == 'MIX'][0]
    at = nt.nodes.new('ShaderNodeAttribute'); at.attribute_type = 'GEOMETRY'; at.attribute_name = 'rest'; at.location = (-1100, -200)
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.location = (-900, -200)
    nz.inputs['Scale'].default_value = scale; nz.inputs['Detail'].default_value = 6.0; nz.inputs['Roughness'].default_value = 0.62
    nt.links.new(at.outputs['Vector'], nz.inputs['Vector'])
    nz2 = nt.nodes.new('ShaderNodeTexNoise'); nz2.location = (-900, -480)
    nz2.inputs['Scale'].default_value = scale * 6.0; nz2.inputs['Detail'].default_value = 3.0
    nt.links.new(at.outputs['Vector'], nz2.inputs['Vector'])
    rmp = nt.nodes.new('ShaderNodeMapRange'); rmp.location = (-700, -200)
    rmp.inputs['From Min'].default_value = 0.25; rmp.inputs['From Max'].default_value = 0.75
    rmp.inputs['To Min'].default_value = 1.0 - mottle; rmp.inputs['To Max'].default_value = 1.0 + mottle * 0.6
    nt.links.new(nz.outputs['Fac'], rmp.inputs['Value'])
    m2 = nt.nodes.new('ShaderNodeMix'); m2.data_type = 'RGBA'; m2.blend_type = 'MULTIPLY'; m2.location = (-60, 300)
    m2.inputs['Factor'].default_value = 1.0
    nt.links.new(mx.outputs['Result'], m2.inputs['A']); nt.links.new(rmp.outputs['Result'], m2.inputs['B'])
    last = m2.outputs['Result']
    if ao:
        aon = nt.nodes.new('ShaderNodeAmbientOcclusion'); aon.location = (-300, 520)
        aon.inputs['Distance'].default_value = 2.5; aon.samples = 4
        gm = nt.nodes.new('ShaderNodeMath'); gm.operation = 'POWER'; gm.inputs[1].default_value = 1.6; gm.location = (-120, 520)
        nt.links.new(aon.outputs['AO'], gm.inputs[0])
        m3 = nt.nodes.new('ShaderNodeMix'); m3.data_type = 'RGBA'; m3.blend_type = 'MULTIPLY'; m3.location = (120, 420)
        m3.inputs['Factor'].default_value = 0.6
        nt.links.new(last, m3.inputs['A']); nt.links.new(gm.outputs[0], m3.inputs['B'])
        last = m3.outputs['Result']
    nt.links.new(last, b.inputs['Base Color'])
    if bump:
        add = nt.nodes.new('ShaderNodeMath'); add.operation = 'ADD'; add.location = (-700, -420)
        sc = nt.nodes.new('ShaderNodeMath'); sc.operation = 'MULTIPLY'; sc.inputs[1].default_value = 0.35; sc.location = (-700, -560)
        nt.links.new(nz2.outputs['Fac'], sc.inputs[0])
        nt.links.new(nz.outputs['Fac'], add.inputs[0]); nt.links.new(sc.outputs[0], add.inputs[1])
        bp = nt.nodes.new('ShaderNodeBump'); bp.location = (-300, -300)
        bp.inputs['Strength'].default_value = bump; bp.inputs['Distance'].default_value = 1.5
        nt.links.new(add.outputs[0], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    return m


def add_rest(o):
    """store the rest position as the POINT attribute `rest` (used by stone_mat)."""
    me = o.data
    a = me.attributes.get('rest') or me.attributes.new('rest', 'FLOAT_VECTOR', 'POINT')
    co = np.zeros(len(me.vertices) * 3)
    me.vertices.foreach_get('co', co)
    a.data.foreach_set('vector', co)


def glow_mat(name, hexcol, strength, halo=False, fade_shell=True, base_hex=None, falloff=2.2, rough=0.45):
    """emissive material whose strength follows the OBJECT custom property `glow` (0..1).
    halo=False: solid shell, emission = strength * glow, and the shell itself fades out below glow 0.2.
    halo=True : soft see-through halo: emission x glow x facing falloff, mixed with transparency."""
    full = 'LA_Mat_' + name
    m = bpy.data.materials.get(full)
    if m:
        return m
    m = bpy.data.materials.new(full); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new('ShaderNodeOutputMaterial'); out.location = (700, 0)
    at = nt.nodes.new('ShaderNodeAttribute'); at.attribute_type = 'OBJECT'; at.attribute_name = 'glow'; at.location = (-700, 0)
    at.name = at.label = 'LA_GLOW'
    tr = nt.nodes.new('ShaderNodeBsdfTransparent'); tr.location = (200, 150)
    c = lin(hexcol)
    if halo:
        lw = nt.nodes.new('ShaderNodeLayerWeight'); lw.inputs['Blend'].default_value = 0.5; lw.location = (-700, -250)
        inv = nt.nodes.new('ShaderNodeMath'); inv.operation = 'SUBTRACT'; inv.inputs[0].default_value = 1.0; inv.location = (-500, -250)
        nt.links.new(lw.outputs['Facing'], inv.inputs[1])
        pw = nt.nodes.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = falloff; pw.location = (-320, -250)
        nt.links.new(inv.outputs[0], pw.inputs[0])
        mu = nt.nodes.new('ShaderNodeMath'); mu.operation = 'MULTIPLY'; mu.location = (-140, -120); mu.use_clamp = True
        nt.links.new(pw.outputs[0], mu.inputs[0]); nt.links.new(at.outputs['Fac'], mu.inputs[1])
        em = nt.nodes.new('ShaderNodeEmission'); em.location = (200, -50)
        em.inputs['Color'].default_value = (*c, 1); em.inputs['Strength'].default_value = strength
        ms = nt.nodes.new('ShaderNodeMath'); ms.operation = 'MULTIPLY'; ms.inputs[1].default_value = strength; ms.location = (20, -200)
        nt.links.new(mu.outputs[0], ms.inputs[0]); nt.links.new(ms.outputs[0], em.inputs['Strength'])
        mix = nt.nodes.new('ShaderNodeAddShader'); mix.location = (450, 0)          # additive: the halo never hides what is behind it
        nt.links.new(tr.outputs[0], mix.inputs[0]); nt.links.new(em.outputs[0], mix.inputs[1])
        nt.links.new(mix.outputs[0], out.inputs['Surface'])
    else:
        b = nt.nodes.new('ShaderNodeBsdfPrincipled'); b.location = (150, -100)
        b.inputs['Base Color'].default_value = (*lin(base_hex or hexcol), 1)
        b.inputs['Roughness'].default_value = rough
        b.inputs['Emission Color'].default_value = (*c, 1)
        ms = nt.nodes.new('ShaderNodeMath'); ms.operation = 'MULTIPLY'; ms.inputs[1].default_value = strength; ms.location = (-300, -200)
        nt.links.new(at.outputs['Fac'], ms.inputs[0]); nt.links.new(ms.outputs[0], b.inputs['Emission Strength'])
        if fade_shell:
            fd = nt.nodes.new('ShaderNodeMapRange'); fd.location = (-300, 150)
            fd.inputs['From Min'].default_value = 0.0; fd.inputs['From Max'].default_value = 0.2
            nt.links.new(at.outputs['Fac'], fd.inputs['Value'])
            mix = nt.nodes.new('ShaderNodeMixShader'); mix.location = (450, 0)
            nt.links.new(fd.outputs['Result'], mix.inputs[0]); nt.links.new(tr.outputs[0], mix.inputs[1]); nt.links.new(b.outputs[0], mix.inputs[2])
            nt.links.new(mix.outputs[0], out.inputs['Surface'])
        else:
            nt.links.new(b.outputs[0], out.inputs['Surface'])
    try:
        m.surface_render_method = 'BLENDED'
    except Exception:
        pass
    m.diffuse_color = (*c, 1)
    return m


def glow_prop(o, value=1.0):
    o['glow'] = float(value)
    try:
        o.id_properties_ui('glow').update(min=0.0, max=1.0, soft_min=0.0, soft_max=1.0, description='0 = off, 1 = full glow')
    except Exception:
        pass


def follow_glow(child, root, path='["glow"]', gain=1.0):
    """child value = gain * root["glow"], through a SUM driver + generator modifier (no Python expression)."""
    if path == '["glow"]':
        glow_prop(child, root['glow'])
    fc = child.driver_add(path) if not hasattr(child, 'energy') else child.driver_add(path)
    d = fc.driver; d.type = 'SUM'
    v = d.variables.new(); v.name = 'g'; v.type = 'SINGLE_PROP'
    v.targets[0].id = root; v.targets[0].data_path = '["glow"]'
    for mod in list(fc.modifiers):
        fc.modifiers.remove(mod)
    g = fc.modifiers.new('GENERATOR'); g.mode = 'POLYNOMIAL'; g.poly_order = 1
    g.coefficients = (0.0, gain)
    return fc


def bone_parent(o, arm, bone, world):
    """parent o to a bone so that its world matrix is `world`; location stays its armature-space rest position."""
    o.parent = arm; o.parent_type = 'BONE'; o.parent_bone = bone
    b = arm.data.bones[bone]
    pm = arm.matrix_world @ b.matrix_local @ Matrix.Translation((0, b.length, 0))
    o.matrix_parent_inverse = pm.inverted()
    o.matrix_basis = Matrix(world)


def empty(name, collection, loc=(0, 0, 0), kind='PLAIN_AXES', size=1.0, parent=None):
    e = bpy.data.objects.new(name, None)
    e.empty_display_type = kind; e.empty_display_size = size
    collection.objects.link(e)
    e.location = loc
    if parent is not None:
        e.parent = parent
    return e


def pose_rot_about(arm, bn, axis, deg, pivot):
    """rotate a pose bone (and its children) about an armature-space axis through an arbitrary pivot."""
    pb = arm.pose.bones[bn]
    bpy.context.view_layer.update()
    M = pb.matrix.copy()
    p = Vector(pivot)
    pb.matrix = Matrix.Translation(p) @ Matrix.Rotation(R(deg), 4, axis) @ Matrix.Translation(-p) @ M
    bpy.context.view_layer.update()


def bone_dir(arm, bn, rest_vec):
    """where an armature-space rest direction attached to the bone points now."""
    pb = arm.pose.bones[bn]
    bpy.context.view_layer.update()
    return (pb.matrix.to_3x3() @ arm.data.bones[bn].matrix_local.to_3x3().inverted() @ Vector(rest_vec)).normalized()


def twist_to(arm, bn, rest_vec, target):
    """spin the bone about its own length so that rest_vec (armature rest space, glued to the bone) points as close to target as possible."""
    pb = arm.pose.bones[bn]
    bpy.context.view_layer.update()
    ax = (pb.matrix.to_3x3() @ Vector((0, 1, 0))).normalized()
    cur = bone_dir(arm, bn, rest_vec)
    a = cur - ax * cur.dot(ax); b = Vector(target) - ax * Vector(target).dot(ax)
    if a.length < 1e-5 or b.length < 1e-5:
        return 0.0
    a.normalize(); b.normalize()
    ang = math.degrees(math.atan2(ax.dot(a.cross(b)), a.dot(b)))
    pose_rot(arm, bn, ax, ang)
    return ang


def two_bone(h, target, l1, l2, hint):
    """joint position for a 2-bone chain from h to target (clamped to reach), bending toward hint."""
    h = Vector(h); t = Vector(target)
    d = t - h
    L = d.length
    L2 = max(min(L, (l1 + l2) * 0.999), abs(l1 - l2) * 1.001)
    u = d.normalized()
    t = h + u * L2
    a = (l1 * l1 - l2 * l2 + L2 * L2) / (2 * L2)
    hh = math.sqrt(max(l1 * l1 - a * a, 0.0))
    n = Vector(hint) - u * Vector(hint).dot(u)
    n = n.normalized() if n.length > 1e-6 else Vector((0, -1, 0))
    return h + u * a + n * hh, t


# ================================================================ Lightning Arms additions
FONT = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'


def EU(rx=0, ry=0, rz=0):
    from mathutils import Euler
    return Euler((R(rx), R(ry), R(rz))).to_matrix().to_4x4()


def tbox(size, c=(0, 0, 0), bevel=0.1, segs=2, taper=(1.0, 1.0), rot=None):
    """bevelled box, optional taper of the top (x, y) and rotation (Matrix) about its own centre."""
    v, f = box(size, (0, 0, 0), bevel, segs)
    if taper != (1.0, 1.0):
        t = v[:, 2] / size[2] + 0.5
        v[:, 0] *= 1 + (taper[0] - 1) * t
        v[:, 1] *= 1 + (taper[1] - 1) * t
    if rot is not None:
        v = v @ np.array(rot.to_3x3()).T
    return v + np.array(c, float), f


def merge(parts):
    V, F, n = [], [], 0
    for v, f in parts:
        V.append(np.asarray(v, float)); F += [[i + n for i in x] for x in f]; n += len(v)
    return np.vstack(V), F


def metal(name, hexcol, rough=0.35, metallic=1.0, vcol=True):
    m = mat(name, hexcol, rough, vcol=vcol, spec=0.5)
    m.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value = metallic
    return m


def noshadow(o):
    o.visible_shadow = False
    return o


def point_light(name, C, parent, hexcol, radius=0.25, loc=(0, 0, 0)):
    ld = bpy.data.lights.new(name, 'POINT'); ld.color = lin(hexcol); ld.energy = 0.0; ld.shadow_soft_size = radius
    lo = bpy.data.objects.new(name, ld); C.objects.link(lo); lo.parent = parent; lo.location = loc
    return lo


def prop(o, name, value=1.0, desc=''):
    o[name] = float(value)
    try:
        o.id_properties_ui(name).update(min=0.0, max=1.0, soft_min=0.0, soft_max=1.0, description=desc)
    except Exception:
        pass


def follow(child, root, name, path=None, gain=1.0, offset=0.0, index=-1, lo=None, hi=None):
    """child value = offset + gain * root[name], through a SUM driver + generator (+ limits) modifier (no Python expression).
    path None: the child's own custom property of the same name (so its materials can read it)."""
    if path is None:
        prop(child, name, root[name]); path = f'["{name}"]'
    fc = child.driver_add(path, index) if index >= 0 else child.driver_add(path)
    d = fc.driver; d.type = 'SUM'
    v = d.variables.new(); v.name = 'g'; v.type = 'SINGLE_PROP'
    v.targets[0].id = root; v.targets[0].data_path = f'["{name}"]'
    for mod in list(fc.modifiers):
        fc.modifiers.remove(mod)
    g = fc.modifiers.new('GENERATOR'); g.mode = 'POLYNOMIAL'; g.poly_order = 1
    g.coefficients = (offset, gain)
    if lo is not None or hi is not None:
        lm = fc.modifiers.new('LIMITS')
        if lo is not None:
            lm.use_min_y = True; lm.min_y = lo
        if hi is not None:
            lm.use_max_y = True; lm.max_y = hi
    return fc


def attr_mat(name, hexcol, strength, attr='glow', base_hex=None, rough=0.5, floor=0.0, vcol=False):
    """solid emissive material: emission strength = strength * (floor + (1-floor) * OBJECT property `attr`)."""
    full = 'LA_Mat_' + name
    m = bpy.data.materials.get(full)
    if m:
        return m
    m = mat(name, base_hex or hexcol, rough, vcol=vcol)
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    b.inputs['Emission Color'].default_value = (*lin(hexcol), 1)
    at = nt.nodes.new('ShaderNodeAttribute'); at.attribute_type = 'OBJECT'; at.attribute_name = attr; at.location = (-700, -300)
    at.name = at.label = 'LA_' + attr.upper()
    mr = nt.nodes.new('ShaderNodeMapRange'); mr.location = (-450, -300)
    mr.inputs['To Min'].default_value = floor * strength; mr.inputs['To Max'].default_value = strength
    nt.links.new(at.outputs['Fac'], mr.inputs['Value']); nt.links.new(mr.outputs['Result'], b.inputs['Emission Strength'])
    return m


def emit_mat(name, hexcol, strength, base_hex=None, rough=0.5):
    return mat(name, base_hex or hexcol, rough, emit=hexcol, estr=strength, vcol=False)


_TXT = {}


def text_mesh(body, size=1.0, depth=0.1, font=FONT, bevel=0.0):
    """text as mesh: stands in the XZ plane facing -Y, centred on x, baseline-centred on z, front face at y = -depth, back at 0.
    Returns verts, faces (cached)."""
    key = (body, round(size, 4), round(depth, 4), font, bevel)
    if key not in _TXT:
        cu = bpy.data.curves.new('LA_tmp_txt', 'FONT')
        cu.body = body; cu.size = size; cu.extrude = depth / 2; cu.align_x = 'CENTER'; cu.align_y = 'CENTER'
        cu.bevel_depth = bevel; cu.bevel_resolution = 0; cu.resolution_u = 3
        if font:
            f = None
            for x in bpy.data.fonts:
                if x.filepath == font:
                    f = x
            cu.font = f or bpy.data.fonts.load(font)
        ob = bpy.data.objects.new('LA_tmp_txt', cu)
        bpy.context.scene.collection.objects.link(ob)
        dg = bpy.context.evaluated_depsgraph_get()
        me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
        bm = bmesh.new(); bm.from_mesh(me)
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=1e-5)
        bm.verts.ensure_lookup_table()
        v = np.array([x.co[:] for x in bm.verts]); f = [[x.index for x in p.verts] for p in bm.faces]
        bm.free()
        bpy.data.objects.remove(ob); bpy.data.meshes.remove(me); bpy.data.curves.remove(cu)
        v = np.stack([v[:, 0], -(v[:, 2] + depth / 2), v[:, 1]], axis=1)
        _TXT[key] = (v, f)
    v, f = _TXT[key]
    return v.copy(), [list(x) for x in f]


def drop_fonts():
    for f in list(bpy.data.fonts):          # all text is mesh by now: no font travels with the file
        bpy.data.fonts.remove(f)


# ---------------------------------------------------------------- stone arm units (the gate's trophies, the giant's limbs)
_ARM = {}


def arm_proto(kind='open', seed=0, w=0.8, L=3.2):
    """a blocky arm standing on z = 0, reaching up +Z, palm to -Y. kind: 'fist', 'open', 'reach' (fingers curled forward)."""
    key = (kind, seed, w, L)
    if key in _ARM:
        return _ARM[key][0].copy(), [list(x) for x in _ARM[key][1]]
    rng = random.Random(seed * 31 + 7)
    P = [tbox((w, w, L * 0.47), (0, 0, L * 0.235), 0.07 * w, 1)]
    bend = rng.uniform(-22, 10)
    Mb = Matrix.Translation((0, 0, L * 0.44)) @ EU(bend, rng.uniform(-6, 6), 0)
    fl = L * 0.40
    v, f = tbox((w * 0.93, w * 0.93, fl), (0, 0, fl / 2), 0.07 * w, 1, taper=(0.92, 0.92)); P.append((xf(v, Mb), f))
    Mh = Mb @ Matrix.Translation((0, 0, fl)) @ EU(rng.uniform(-25, 15), 0, rng.uniform(-12, 12))
    if kind == 'fist':
        v, f = tbox((w * 1.12, w * 1.05, w * 1.0), (0, 0, w * 0.45), 0.12 * w, 1); P.append((xf(v, Mh), f))
        v, f = tbox((w * 0.34, w * 0.5, w * 0.6), (w * 0.52, -w * 0.25, w * 0.45), 0.06 * w, 1); P.append((xf(v, Mh), f))
    else:
        v, f = tbox((w * 1.08, w * 0.46, w * 0.72), (0, 0, w * 0.34), 0.07 * w, 1); P.append((xf(v, Mh), f))
        curl = -38 if kind == 'reach' else -8
        for i in range(4):
            x = (-0.405 + 0.27 * i) * w
            Mf = Mh @ Matrix.Translation((x, 0, w * 0.68)) @ EU(curl + rng.uniform(-14, 10), 0, (i - 1.5) * 5)
            fz = w * (0.62 + 0.1 * (1.5 - abs(i - 1.5)))
            v, f = tbox((w * 0.23, w * 0.36, fz), (0, 0, fz / 2), 0.04 * w, 1); P.append((xf(v, Mf), f))
            if kind == 'reach':
                Mf2 = Mf @ Matrix.Translation((0, 0, fz * 0.9)) @ EU(-50, 0, 0)
                v, f = tbox((w * 0.22, w * 0.33, fz * 0.6), (0, 0, fz * 0.3), 0.04 * w, 1); P.append((xf(v, Mf2), f))
        Mt = Mh @ Matrix.Translation((w * 0.6, -w * 0.05, w * 0.3)) @ EU(-10, 38, 0)
        v, f = tbox((w * 0.27, w * 0.36, w * 0.62), (0, 0, w * 0.25), 0.04 * w, 1); P.append((xf(v, Mt), f))
    _ARM[key] = merge(P)
    return arm_proto(kind, seed, w, L)


ARM_KINDS = ('open', 'fist', 'reach', 'open', 'reach')


def rand_arm(rng, w=0.8, L=3.2):
    return arm_proto(rng.choice(ARM_KINDS), rng.randrange(5), w, L)


# ---------------------------------------------------------------- chains
_LINK = {}


def link_proto(L=1.3, W=0.8, r=0.17, segs=6):
    """one chain link lying in the XZ plane, long axis Z, centred on the origin."""
    key = (L, W, r, segs)
    if key not in _LINK:
        hw = W / 2 - r; hl = L / 2 - W / 2
        pts = []
        for i in range(7):
            a = math.pi * i / 6
            pts.append((hw * math.cos(a), 0, hl + hw * math.sin(a)))
        for i in range(7):
            a = math.pi + math.pi * i / 6
            pts.append((hw * math.cos(a), 0, -hl + hw * math.sin(a)))
        pts.append(pts[0]); pts.append(pts[1])
        v, f, ring = tube(pts, r, segs=segs, cap0=False, cap1=False)
        _LINK[key] = (v, f)
    v, f = _LINK[key]
    return v.copy(), [list(x) for x in f]


def catenary(p0, p1, sag, n=24, ground=None):
    p0 = np.array(p0, float); p1 = np.array(p1, float)
    out = []
    for i in range(n + 1):
        t = i / n
        p = p0 * (1 - t) + p1 * t
        p[2] -= sag * 4 * t * (1 - t)
        if ground is not None:
            p[2] = max(p[2], ground)
        out.append(p)
    return out


def chain(mb, path, L=1.3, W=0.8, r=0.17, mat=0, rune_mat=None, rune_every=2, col=(1, 1, 1), w=None, twist0=0.0):
    """chain of links along a smooth path (list of points). Every `rune_every`-th link carries a glowing rune plate (rune_mat index).
    Returns the link centres."""
    step = L - 2 * r * 1.55
    dense = spline(path, 600)
    total = float(np.linalg.norm(np.diff(dense, axis=0), axis=1).sum())
    n = max(2, int(round(total / step)))
    P = spline(path, n + 1)
    cs = []
    for i in range(n):
        a, b = P[i], P[i + 1]
        d = Vector(b - a)
        s = d.length / step
        q = Vector((0, 0, 1)).rotation_difference(d.normalized())
        M = Matrix.Translation(Vector((a + b) / 2)) @ q.to_matrix().to_4x4() @ Matrix.Rotation(twist0 + (math.pi / 2) * (i % 2), 4, 'Z')
        v, f = link_proto(L, W, r)
        v[:, 2] *= min(1.12, max(0.9, s))
        mb.add(xf(v, M), f, mat, col=col, w=w)
        if rune_mat is not None and i % rune_every == 0:
            rv, rf = rune_glyph(i, L * 0.36)
            for sx, rz in ((1, 90), (-1, -90)):
                Mr = M @ Matrix.Translation((sx * (W / 2 - r), 0, 0)) @ EU(0, 0, rz) @ Matrix.Translation((0, -r - 0.015, 0))
                mb.add(xf(rv, Mr), rf, rune_mat, w=w, flat=True)
        cs.append((a + b) / 2)
    return cs


_RUNES = [
    [((0, -1), (0, 1)), ((0, 1), (0.6, 0.4)), ((0.6, 0.4), (0, 0))],
    [((-0.5, -1), (0.5, 1)), ((0.5, -1), (-0.5, 1))],
    [((0, -1), (0, 1)), ((-0.6, 0.3), (0, 1)), ((0.6, 0.3), (0, 1))],
    [((-0.5, -1), (-0.5, 1)), ((-0.5, 1), (0.5, 0)), ((0.5, 0), (-0.5, -0.2))],
    [((0, -1), (0, 1)), ((-0.6, -0.4), (0.6, 0.4))],
    [((-0.5, 1), (0.5, 0)), ((0.5, 0), (-0.5, -1))],
    [((-0.5, -1), (-0.5, 1)), ((0.5, -1), (0.5, 1)), ((-0.5, 0.5), (0.5, -0.5))],
]


def rune_glyph(i, h, t=0.14, depth=0.03):
    """a little angular rune: bars in the XZ plane facing -Y, height h, centred."""
    P = []
    for (a, b) in _RUNES[i % len(_RUNES)]:
        a = np.array(a) * h / 2; b = np.array(b) * h / 2
        d = b - a; ln = float(np.linalg.norm(d)); ang = math.degrees(math.atan2(d[0], d[1]))
        v, f = box((t * h, depth, ln + t * h))
        v = xf(v, Matrix.Translation(((a[0] + b[0]) / 2, 0, (a[1] + b[1]) / 2)) @ EU(0, ang, 0))
        P.append((v, f))
    return merge(P)
