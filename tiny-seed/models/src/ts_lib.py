# Tiny Seed model kit: shared helpers (mesh builder, primitives, materials, armature, poses).
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
    full = 'TS_Mat_' + name
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
    m = bpy.data.materials.new('TS_Mat_' + name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes['Principled BSDF']
    b.inputs['Roughness'].default_value = rough
    b.inputs['Specular IOR Level'].default_value = 0.15
    tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = img; tex.name = tex.label = 'TS_FACE_TEX'
    tex.location = (-350, 250); tex.extension = 'EXTEND'
    if atlas_n > 1:
        uv = nt.nodes.new('ShaderNodeUVMap'); uv.location = (-1100, 250)
        at = nt.nodes.new('ShaderNodeAttribute'); at.attribute_type = 'OBJECT'; at.attribute_name = prop
        at.location = (-1100, 50); at.name = at.label = 'TS_FACE_INDEX'
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
                md = o.modifiers.new('TS_Armature', 'ARMATURE'); md.object = arm
        elif parent is not None:
            o.parent = parent
        me.validate()
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
