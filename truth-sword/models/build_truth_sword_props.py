"""Builds truth-sword-props.blend (SW_ props, Toybox Fable style). Run: python3 -I build.py"""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix

OUT = '/tmp/claude-0/tv/truthsword/models/truth-sword-props.blend'
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.name = 'SW_Props'
random.seed(7)


# ----------------------------------------------------------------- helpers
def lin(h):
    h = h.lstrip('#')
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (*out, 1.0)


def mat(name, hexc, rough=0.7, metal=0.0, emit=None, estr=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = lin(hexc)
    b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metal
    if emit:
        b.inputs['Emission Color'].default_value = lin(emit)
        b.inputs['Emission Strength'].default_value = estr
    m.diffuse_color = lin(hexc)
    return m


def collection(name):
    c = bpy.data.collections.new(name)
    scene.collection.children.link(c)
    return c


class Build:
    """A bmesh with part tracking: after making geometry call done(mat_index, **vertex_attrs)."""

    def __init__(self, attrs=()):
        self.bm = bmesh.new()
        self.layers = {a: self.bm.verts.layers.float.new(a) for a in attrs}
        self.vd = self.bm.verts.layers.int.new('_done')
        self.fd = self.bm.faces.layers.int.new('_done')

    def done(self, mi=0, M=None, **attrs):
        bm = self.bm
        for v in bm.verts:
            if not v[self.vd]:
                if M is not None:
                    v.co = M @ v.co
                for k, val in attrs.items():
                    v[self.layers[k]] = val
                v[self.vd] = 1
        for f in bm.faces:
            if not f[self.fd]:
                f.material_index = mi
                f[self.fd] = 1

    def new_verts(self):
        return [v for v in self.bm.verts if not v[self.vd]]

    def box(self, size, loc=(0, 0, 0), bevel=0.04, segs=1, rot=None):
        bm = self.bm
        r = bmesh.ops.create_cube(bm, size=1.0)
        vs = r['verts']
        for v in vs:
            v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
        if bevel > 0:
            es = list({e for v in vs for e in v.link_edges})
            bmesh.ops.bevel(bm, geom=es, offset=bevel, segments=segs, profile=0.5, affect='EDGES')
        Mx = Matrix.Translation(loc)
        if rot is not None:
            Mx = Mx @ rot
        for v in self.new_verts():
            v.co = Mx @ v.co

    def loft(self, rings, cap_start=True, cap_end=True):
        bm = self.bm
        vr = []
        for ring in rings:
            vr.append([bm.verts.new(p) for p in ring])
        for a, b in zip(vr, vr[1:]):
            n = len(a)
            if len(b) == 1 and n > 1:
                for i in range(n):
                    bm.faces.new((a[i], a[(i + 1) % n], b[0]))
            elif n == 1 and len(b) > 1:
                m = len(b)
                for i in range(m):
                    bm.faces.new((a[0], b[(i + 1) % m], b[i]))
            else:
                for i in range(n):
                    bm.faces.new((a[i], a[(i + 1) % n], b[(i + 1) % n], b[i]))
        if cap_start and len(vr[0]) > 2:
            bm.faces.new(list(reversed(vr[0])))
        if cap_end and len(vr[-1]) > 2:
            bm.faces.new(vr[-1])
        return vr

    def lathe(self, prof, segs=24, phase=0.0, **kw):
        rings = []
        for r, z in prof:
            if r < 1e-6:
                rings.append([Vector((0, 0, z))])
            else:
                rings.append([Vector((r * math.cos(phase + 2 * math.pi * i / segs),
                                      r * math.sin(phase + 2 * math.pi * i / segs), z)) for i in range(segs)])
        return self.loft(rings, **kw)

    def ball(self, r, loc, subdiv=2, scale=(1, 1, 1)):
        res = bmesh.ops.create_icosphere(self.bm, subdivisions=subdiv, radius=r)
        for v in res['verts']:
            v.co = Vector((v.co.x * scale[0], v.co.y * scale[1], v.co.z * scale[2])) + Vector(loc)

    def to_object(self, name, coll, mats, sharp_deg=32.0, smooth=True, recalc=True):
        bm = self.bm
        bm.verts.layers.int.remove(self.vd)
        bm.faces.layers.int.remove(self.fd)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        if recalc:
            bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        for f in bm.faces:
            f.smooth = smooth
        lim = math.radians(sharp_deg)
        for e in bm.edges:
            if len(e.link_faces) == 2:
                e.smooth = e.calc_face_angle(0.0) < lim
        me = bpy.data.meshes.new(name)
        bm.to_mesh(me)
        bm.free()
        for m in mats:
            me.materials.append(m)
        ob = bpy.data.objects.new(name, me)
        coll.objects.link(ob)
        return ob


def RX(d): return Matrix.Rotation(math.radians(d), 4, 'X')
def RY(d): return Matrix.Rotation(math.radians(d), 4, 'Y')
def RZ(d): return Matrix.Rotation(math.radians(d), 4, 'Z')
def T(x, y, z): return Matrix.Translation((x, y, z))


def prop(ob, name, val, mn, mx, desc):
    ob[name] = float(val)
    ob.id_properties_ui(name).update(min=mn, max=mx, soft_min=mn, soft_max=mx, description=desc)
    ob.property_overridable_library_set('["%s"]' % name, True)


def obj_attr(nt, name):
    n = nt.nodes.new('ShaderNodeAttribute')
    n.attribute_type = 'OBJECT'
    n.attribute_name = name
    return n.outputs['Fac']


def smath(nt, op, *args, clamp=False):
    n = nt.nodes.new('ShaderNodeMath')
    n.operation = op
    n.use_clamp = clamp
    for i, a in enumerate(args):
        if isinstance(a, (int, float)):
            n.inputs[i].default_value = a
        else:
            nt.links.new(a, n.inputs[i])
    return n.outputs[0]


def ramp(nt, fac, stops):
    n = nt.nodes.new('ShaderNodeValToRGB')
    el = n.color_ramp.elements
    while len(el) < len(stops):
        el.new(0.5)
    for e, (p, h) in zip(el, stops):
        e.position = p
        e.color = lin(h)
    nt.links.new(fac, n.inputs['Fac'])
    return n.outputs['Color']


def mixc(nt, fac, a, b):
    n = nt.nodes.new('ShaderNodeMix')
    n.data_type = 'RGBA'
    for sock, val in ((n.inputs[0], fac), (n.inputs[6], a), (n.inputs[7], b)):
        if hasattr(val, 'links'):
            nt.links.new(val, sock)
        elif isinstance(val, str):
            sock.default_value = lin(val)
        else:
            sock.default_value = val
    return n.outputs[2]


# ----------------------------------------------------------------- shared materials
M_wood = mat('SW_Mat_Wood', '#A98758', 0.8)
M_wood_dark = mat('SW_Mat_WoodDark', '#6B5A41', 0.85)
M_leather = mat('SW_Mat_Leather', '#7A4A28', 0.8)
M_leather_dark = mat('SW_Mat_LeatherDark', '#4E2E18', 0.85)
M_iron = mat('SW_Mat_Iron', '#5E5B5A', 0.55, 0.4)
M_dark = mat('SW_Mat_Hollow', '#0E0A0C', 1.0)
M_gold = mat('SW_Mat_Gold', '#F2B424', 0.3, 0.6, '#FFB020', 0.12)
M_ruby = mat('SW_Mat_JewelRuby', '#E0182C', 0.15, 0.0, '#FF2030', 0.6)
M_sapph = mat('SW_Mat_JewelSapphire', '#2260E8', 0.15, 0.0, '#3070FF', 0.6)
M_emer = mat('SW_Mat_JewelEmerald', '#1FBF5A', 0.15, 0.0, '#20E060', 0.6)
M_red = mat('SW_Mat_ScabbardRed', '#B3201F', 0.6)
M_bronze = mat('SW_Mat_Bronze', '#C28A3C', 0.4, 0.55, '#C07A20', 0.06)
M_rope = mat('SW_Mat_Rope', '#D3B78B', 0.9)
M_steel = mat('SW_Mat_GuardSteel', '#C3CAD2', 0.35, 0.5, '#C8D8E8', 0.05)
M_steel_dark = mat('SW_Mat_GuardSteelDark', '#7E858E', 0.45, 0.5)
M_navy = mat('SW_Mat_GuardGrip', '#2B3550', 0.8)


# ----------------------------------------------------------------- sword geometry nodes
def build_sword_gn():
    ng = bpy.data.node_groups.new('SW_GN_SwordGrow', 'GeometryNodeTree')
    itf = ng.interface
    itf.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    itf.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    ids = {}
    for name, d in (('Length', 6.0), ('Width', 1.0), ('UniformBelow', 6.0), ('HiltLen', 1.3),
                    ('BladeRef', 4.7), ('TipLen', 0.9), ('GuardTopZ', 0.55)):
        s = itf.new_socket(name, in_out='INPUT', socket_type='NodeSocketFloat')
        s.default_value = d
        s.min_value = 0.0
        ids[name] = s.identifier
    gi = ng.nodes.new('NodeGroupInput')
    go = ng.nodes.new('NodeGroupOutput')
    I = gi.outputs

    def M(op, *args):
        n = ng.nodes.new('ShaderNodeMath')
        n.operation = op
        for i, a in enumerate(args):
            if isinstance(a, (int, float)):
                n.inputs[i].default_value = a
            else:
                ng.links.new(a, n.inputs[i])
        return n.outputs[0]

    def attr(name):
        n = ng.nodes.new('GeometryNodeInputNamedAttribute')
        n.data_type = 'FLOAT'
        n.inputs['Name'].default_value = name
        return n.outputs['Attribute']

    pos = ng.nodes.new('GeometryNodeInputPosition')
    sep = ng.nodes.new('ShaderNodeSeparateXYZ')
    ng.links.new(pos.outputs[0], sep.inputs[0])
    x, y, z = sep.outputs
    b, g, r, t = attr('sw_blade'), attr('sw_guard'), attr('sw_ring'), attr('sw_tip')

    L = M('MAXIMUM', I['Length'], 0.01)
    s = M('MINIMUM', M('DIVIDE', L, I['UniformBelow']), 1.0)
    Bp = M('SUBTRACT', M('MAXIMUM', L, I['UniformBelow']), I['HiltLen'])
    w = M('MULTIPLY', I['Width'], M('POWER', M('MAXIMUM', M('DIVIDE', Bp, I['BladeRef']), 0.0001), 0.6))
    wg = M('MAXIMUM', M('MINIMUM', w, 2.0), 0.4)
    fl = M('ADD', M('MULTIPLY', w, 0.3), M('MULTIPLY', M('MAXIMUM', M('SUBTRACT', w, 1.0), 0.0), 2.0))
    sh = M('MAXIMUM', M('SUBTRACT', Bp, M('MULTIPLY', I['TipLen'], w)), M('ADD', fl, 0.02))
    top = M('MAXIMUM', Bp, M('ADD', sh, 0.02))
    zr2 = M('ADD', sh, M('MULTIPLY', t, M('SUBTRACT', top, sh)))
    r0 = M('LESS_THAN', r, 0.5)
    c1 = M('LESS_THAN', r, 1.5)
    inner = M('ADD', zr2, M('MULTIPLY', c1, M('SUBTRACT', fl, zr2)))
    zin = M('ADD', I['GuardTopZ'], inner)
    zblade = M('ADD', zin, M('MULTIPLY', r0, M('SUBTRACT', z, zin)))
    znew = M('ADD', z, M('MULTIPLY', b, M('SUBTRACT', zblade, z)))
    xyb = M('ADD', w, M('MULTIPLY', r0, M('SUBTRACT', wg, w)))
    xys = M('ADD', M('ADD', 1.0, M('MULTIPLY', g, M('SUBTRACT', wg, 1.0))), M('MULTIPLY', b, M('SUBTRACT', xyb, 1.0)))
    comb = ng.nodes.new('ShaderNodeCombineXYZ')
    ng.links.new(M('MULTIPLY', x, xys), comb.inputs[0])
    ng.links.new(M('MULTIPLY', y, xys), comb.inputs[1])
    ng.links.new(znew, comb.inputs[2])
    store = ng.nodes.new('GeometryNodeStoreNamedAttribute')
    store.data_type = 'FLOAT_VECTOR'
    store.domain = 'POINT'
    store.inputs['Name'].default_value = 'sw_tex'
    ng.links.new(I['Geometry'], store.inputs['Geometry'])
    tx = ng.nodes.new('ShaderNodeVectorMath')
    tx.operation = 'SCALE'
    ng.links.new(comb.outputs[0], tx.inputs[0])
    ng.links.new(M('DIVIDE', 1.0, M('MAXIMUM', w, 1.0)), tx.inputs['Scale'])
    ng.links.new(tx.outputs[0], store.inputs['Value'])
    sc = ng.nodes.new('ShaderNodeVectorMath')
    sc.operation = 'SCALE'
    ng.links.new(comb.outputs[0], sc.inputs[0])
    ng.links.new(s, sc.inputs['Scale'])
    sp = ng.nodes.new('GeometryNodeSetPosition')
    ng.links.new(store.outputs['Geometry'], sp.inputs['Geometry'])
    ng.links.new(sc.outputs[0], sp.inputs['Position'])
    ng.links.new(sp.outputs['Geometry'], go.inputs[0])
    return ng, ids


GN, GN_IDS = build_sword_gn()


def blade_material(name, kind):
    """kind: 'rust' (rust -> clean glowing steel), 'gold', 'steel'. Texture space = sw_tex (unstretched)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bs = nt.nodes['Principled BSDF']
    glow = obj_attr(nt, 'glow')
    if kind == 'rust':
        tex = nt.nodes.new('ShaderNodeAttribute')
        tex.attribute_name = 'sw_tex'
        noise = nt.nodes.new('ShaderNodeTexNoise')
        noise.inputs['Scale'].default_value = 2.2
        noise.inputs['Detail'].default_value = 1.5
        nt.links.new(tex.outputs['Vector'], noise.inputs['Vector'])
        nf = noise.outputs['Fac']
        rust = ramp(nt, nf, ((0.0, '#9A4E22'), (0.47, '#C46A2A'), (0.6, '#E2953E')))
        nt.nodes[-1].color_ramp.interpolation = 'CONSTANT'
        auto = smath(nt, 'DIVIDE', smath(nt, 'SUBTRACT', obj_attr(nt, 'sword_length'), 20.0), 40.0, clamp=True)
        fac = smath(nt, 'MAXIMUM', auto, obj_attr(nt, 'clean'), clamp=True)
        # rust dissolves in patches as fac rises
        pf = smath(nt, 'ADD', smath(nt, 'DIVIDE', smath(nt, 'SUBTRACT', smath(nt, 'SUBTRACT', smath(nt, 'MULTIPLY', fac, 1.3), 0.65), smath(nt, 'MULTIPLY', smath(nt, 'SUBTRACT', nf, 0.5), 1.2)), 0.1), 0.5, clamp=True)
        col = mixc(nt, pf, rust, '#EEF3F8')
        nt.links.new(col, bs.inputs['Base Color'])
        nt.links.new(smath(nt, 'MULTIPLY', pf, 0.2), bs.inputs['Metallic'])
        nt.links.new(smath(nt, 'SUBTRACT', 0.8, smath(nt, 'MULTIPLY', pf, 0.48)), bs.inputs['Roughness'])
        bs.inputs['Emission Color'].default_value = lin('#DCEBFF')
        nt.links.new(smath(nt, 'MULTIPLY', smath(nt, 'MULTIPLY', pf, 0.55), glow), bs.inputs['Emission Strength'])
    elif kind == 'gold':
        bs.inputs['Base Color'].default_value = lin('#FFC62E')
        bs.inputs['Metallic'].default_value = 0.6
        bs.inputs['Roughness'].default_value = 0.22
        bs.inputs['Emission Color'].default_value = lin('#FFC030')
        nt.links.new(smath(nt, 'MULTIPLY', glow, 0.3), bs.inputs['Emission Strength'])
    else:
        bs.inputs['Base Color'].default_value = lin('#CDD5DD')
        bs.inputs['Metallic'].default_value = 0.5
        bs.inputs['Roughness'].default_value = 0.32
        bs.inputs['Emission Color'].default_value = lin('#CFE4FF')
        nt.links.new(smath(nt, 'MULTIPLY', glow, 0.08), bs.inputs['Emission Strength'])
    return m


def blade_geo(B, zg, bref, tip, hw, ht, mi):
    """Blade rings: base (ring 0, sunk in the guard), flare (1), shoulder + tip (2, sw_tip 0..1)."""
    def sect(z, k=1.0):
        return [Vector((hw * k, 0, z)), Vector((hw * 0.5 * k, ht * k, z)), Vector((-hw * 0.5 * k, ht * k, z)),
                Vector((-hw * k, 0, z)), Vector((-hw * 0.5 * k, -ht * k, z)), Vector((hw * 0.5 * k, -ht * k, z))]
    L = B.layers
    zsh = zg + bref - tip
    spec = [(zg - 0.12, 1.0, 0, 0.0), (zg + 0.3, 1.0, 1, 0.0), (zsh, 1.0, 2, 0.0),
            (zsh + tip * 0.45, 0.80, 2, 0.45), (zsh + tip * 0.8, 0.46, 2, 0.8), (zsh + tip, 0.07, 2, 1.0)]
    vr = B.loft([sect(z, k) for z, k, _, _ in spec])
    for ring, (_, _, rg, tt) in zip(vr, spec):
        for v in ring:
            v[L['sw_ring']] = rg
            v[L['sw_tip']] = tt
    B.done(mi, sw_blade=1.0)


def finish_sword(B, name, coll, mats, length, uniform_below, hilt_len, tip, zg, clean=None):
    ob = B.to_object(name, coll, mats, sharp_deg=28)
    prop(ob, 'sword_length', length, 0.05, 1000.0, 'Total sword length in BU, pommel to tip. Animate this.')
    prop(ob, 'width', 1.0, 0.1, 10.0, 'Blade width multiplier (on top of the automatic widening)')
    prop(ob, 'glow', 1.0, 0.0, 20.0, 'Blade glow multiplier')
    if clean is not None:
        prop(ob, 'clean', clean, 0.0, 1.0, 'Extra rust-to-clean-steel amount (auto: 0 at 20 BU to 1 at 60 BU)')
    md = ob.modifiers.new('SW_Grow', 'NODES')
    md.node_group = GN
    getattr(md.properties.inputs, GN_IDS['UniformBelow']).value = float(uniform_below)
    getattr(md.properties.inputs, GN_IDS['HiltLen']).value = float(hilt_len)
    getattr(md.properties.inputs, GN_IDS['BladeRef']).value = float(length - hilt_len)
    getattr(md.properties.inputs, GN_IDS['TipLen']).value = float(tip)
    getattr(md.properties.inputs, GN_IDS['GuardTopZ']).value = float(zg)
    getattr(md.properties.inputs, GN_IDS['Length']).value = float(length)
    getattr(md.properties.inputs, GN_IDS['Width']).value = 1.0
    for sock, pname in (('Length', 'sword_length'), ('Width', 'width')):
        fc = ob.driver_add('modifiers["SW_Grow"].properties.inputs.%s.value' % GN_IDS[sock])
        d = fc.driver
        d.type = 'SUM'
        v = d.variables.new()
        v.name = 'SW_' + pname
        v.type = 'SINGLE_PROP'
        v.targets[0].id = ob
        v.targets[0].data_path = '["%s"]' % pname
    return ob


SW_ATTRS = ('sw_blade', 'sw_guard', 'sw_ring', 'sw_tip')


def grip(B, z0, z1, r, n, mi_a, mi_b):
    """Leather wrap: n barrel bands, alternating two materials."""
    h = (z1 - z0) / n
    for i in range(n):
        a = z0 + i * h
        B.lathe([(r * 0.86, a), (r, a + h * 0.25), (r, a + h * 0.75), (r * 0.86, a + h)], segs=10)
        B.done(mi_a if i % 2 == 0 else mi_b)


# --- stable boy: ref 6 BU, hilt 1.3 (pommel bottom -0.75 .. guard top 0.55)
c = collection('SW_Sword_StableBoy')
B = Build(SW_ATTRS)
M_rust = blade_material('SW_Mat_RustBlade', 'rust')
M_rustiron = mat('SW_Mat_RustIron', '#7A5238', 0.75, 0.2)
grip(B, -0.42, 0.36, 0.13, 5, 1, 2)
B.lathe([(0, -0.75), (0.13, -0.72), (0.2, -0.62), (0.2, -0.5), (0.12, -0.4), (0, -0.4)], segs=8); B.done(3)
B.box((1.45, 0.3, 0.2), (0, 0, 0.45), bevel=0.05); B.done(3, sw_guard=1.0)
blade_geo(B, 0.55, 4.7, 0.9, 0.3, 0.085, 0)
sw_boy = finish_sword(B, 'SW_Sword_StableBoy', c, [M_rust, M_leather, M_leather_dark, M_rustiron], 6.0, 6.0, 1.3, 0.9, 0.55, clean=0.0)
sw_boy.location = (7, 0, 1.0)

# --- golden: ref 5 BU, hilt 1.3; blade shrinks first, below 2.0 BU the whole sword shrinks
c = collection('SW_Sword_Golden')
B = Build(SW_ATTRS)
M_goldblade = blade_material('SW_Mat_GoldBlade', 'gold')
M_royal = mat('SW_Mat_RoyalGrip', '#7A1F8C', 0.7)
grip(B, -0.42, 0.34, 0.125, 6, 1, 2)
B.lathe([(0, -0.75), (0.14, -0.72), (0.23, -0.6), (0.14, -0.46), (0.1, -0.4), (0, -0.4)], segs=10); B.done(2)
B.ball(0.1, (0, -0.2, -0.6), 1, (1, 0.6, 1)); B.done(4)
B.ball(0.1, (0, 0.2, -0.6), 1, (1, 0.6, 1)); B.done(4)
B.box((1.7, 0.32, 0.22), (0, 0, 0.44), bevel=0.06); B.done(2, sw_guard=1.0)
for sx in (-1, 1):
    B.ball(0.17, (sx * 0.88, 0, 0.44), 2); B.done(2, sw_guard=1.0)
for sy in (-1, 1):
    B.ball(0.14, (0, sy * 0.15, 0.44), 1, (1, 0.6, 1)); B.done(3, sw_guard=1.0)
blade_geo(B, 0.55, 3.7, 0.85, 0.3, 0.08, 0)
sw_gold = finish_sword(B, 'SW_Sword_Golden', c, [M_goldblade, M_royal, M_gold, M_ruby, M_sapph], 5.0, 2.0, 1.3, 0.85, 0.55)
sw_gold.location = (9.5, 0, 1.0)

# --- guard: ref 4.5 BU, hilt 1.3
c = collection('SW_Sword_Guard')
B = Build(SW_ATTRS)
M_steelblade = blade_material('SW_Mat_GuardBlade', 'steel')
grip(B, -0.42, 0.36, 0.125, 4, 1, 1)
B.lathe([(0, -0.75), (0.15, -0.71), (0.21, -0.58), (0.15, -0.45), (0, -0.4)], segs=10); B.done(2)
B.box((1.5, 0.28, 0.2), (0, 0, 0.45), bevel=0.05); B.done(2, sw_guard=1.0)
blade_geo(B, 0.55, 3.2, 0.8, 0.28, 0.075, 0)
sw_guard = finish_sword(B, 'SW_Sword_Guard', c, [M_steelblade, M_navy, M_steel_dark], 4.5, 4.5, 1.3, 0.8, 0.55)
sw_guard.location = (12, 0, 1.0)


# ----------------------------------------------------------------- truth stone
c = collection('SW_TruthStone')
M_stone = bpy.data.materials.new('SW_Mat_TruthStone')
M_stone.use_nodes = True
nt = M_stone.node_tree
bs = nt.nodes['Principled BSDF']
tc = nt.nodes.new('ShaderNodeTexCoord')
noise = nt.nodes.new('ShaderNodeTexNoise')
noise.inputs['Scale'].default_value = 0.9
noise.inputs['Detail'].default_value = 1.0
nt.links.new(tc.outputs['Object'], noise.inputs['Vector'])
nt.links.new(ramp(nt, noise.outputs['Fac'], ((0.4, '#8E9198'), (0.6, '#A9ACB3'))), bs.inputs['Base Color'])
bs.inputs['Roughness'].default_value = 0.85
bs.inputs['Emission Color'].default_value = lin('#49A6FF')
nt.links.new(smath(nt, 'MULTIPLY', obj_attr(nt, 'glow'), 0.045), bs.inputs['Emission Strength'])

M_groove = bpy.data.materials.new('SW_Mat_TruthStoneGroove')
M_groove.use_nodes = True
nt = M_groove.node_tree
bs = nt.nodes['Principled BSDF']
bs.inputs['Base Color'].default_value = lin('#6C6F78')
bs.inputs['Roughness'].default_value = 0.9
bs.inputs['Emission Color'].default_value = lin('#49A6FF')
nt.links.new(smath(nt, 'MULTIPLY', obj_attr(nt, 'glow'), 0.2), bs.inputs['Emission Strength'])

M_rune = bpy.data.materials.new('SW_Mat_TruthStoneRune')
M_rune.use_nodes = True
nt = M_rune.node_tree
bs = nt.nodes['Principled BSDF']
g = obj_attr(nt, 'glow')
nt.links.new(mixc(nt, smath(nt, 'MULTIPLY', g, 1.0, clamp=True), '#4C5568', '#7CC4FF'), bs.inputs['Base Color'])
bs.inputs['Roughness'].default_value = 0.6
bs.inputs['Emission Color'].default_value = lin('#3F9CFF')
nt.links.new(smath(nt, 'MULTIPLY', g, 6.0), bs.inputs['Emission Strength'])

M_slot = bpy.data.materials.new('SW_Mat_TruthStoneSlot')
M_slot.use_nodes = True
nt = M_slot.node_tree
bs = nt.nodes['Principled BSDF']
bs.inputs['Base Color'].default_value = lin('#0C0D12')
bs.inputs['Roughness'].default_value = 1.0
bs.inputs['Emission Color'].default_value = lin('#49A6FF')
nt.links.new(smath(nt, 'MULTIPLY', obj_attr(nt, 'glow'), 2.5), bs.inputs['Emission Strength'])

B = Build()
SEG = 32
# stepped dais: body (stone), then the carved ring floor as its own band
B.lathe([(3.42, 0.0), (3.5, 0.08), (3.5, 0.5), (3.4, 0.6), (3.12, 0.64), (3.05, 0.72), (3.05, 1.4), (2.95, 1.5),
         (2.58, 1.5), (2.52, 1.42)], segs=SEG, cap_start=True, cap_end=False)
B.done(0)
B.lathe([(2.52, 1.42), (1.93, 1.42)], segs=SEG, cap_start=False, cap_end=False)
B.done(1)
B.lathe([(1.93, 1.42), (1.87, 1.5), (0, 1.5)], segs=SEG, cap_start=False, cap_end=False)
B.done(0)
# chunky worn corner blocks on the lower step (ancient look)
for i in range(8):
    a = i * 45 + 22.5
    B.box((0.5, 0.9, 0.5), (3.33, 0, 0.3), bevel=0.07, rot=None)
    B.done(0, M=RZ(a))
# runes in the ring: bars in a (radial u, tangential v) cell
GLYPHS = [
    [((-1, 0), (1, 0)), ((1, 0), (0.2, 0.8)), ((0, 0), (-0.6, -0.8))],
    [((-1, -0.6), (1, -0.6)), ((-1, 0.6), (1, 0.6)), ((-1, -0.6), (1, 0.6))],
    [((-1, 0), (1, 0)), ((0.1, -0.8), (0.1, 0.8))],
    [((-1, -0.7), (1, 0)), ((1, 0), (-1, 0.7))],
    [((-1, 0), (0, 0)), ((0, 0), (1, -0.7)), ((0, 0), (1, 0.7))],
    [((-1, -0.5), (1, -0.5)), ((1, -0.5), (1, 0.6)), ((1, 0.6), (-0.2, 0.6))],
]
NR = 12
for i in range(NR):
    gl = GLYPHS[i % len(GLYPHS)]
    for (u0, v0), (u1, v1) in gl:
        p0 = Vector((2.225 + u0 * 0.17, v0 * 0.2, 0))
        p1 = Vector((2.225 + u1 * 0.17, v1 * 0.2, 0))
        d = p1 - p0
        ang = math.atan2(d.y, d.x)
        mid = (p0 + p1) / 2
        B.box((d.length + 0.07, 0.075, 0.09), (0, 0, 0), bevel=0.0)
        B.done(2, M=RZ(i * 360 / NR + 15) @ T(mid.x, mid.y, 1.435) @ Matrix.Rotation(ang, 4, 'Z'))
# the sword slot: stone collar + dark mouth
for (sx, sy, x, y) in ((1.5, 0.22, 0, 0.3), (1.5, 0.22, 0, -0.3), (0.22, 0.6, 0.64, 0), (0.22, 0.6, -0.64, 0)):
    B.box((sx, sy, 0.3), (x, y, 1.5), bevel=0.05)
    B.done(0)
B.box((1.1, 0.42, 0.2), (0, 0, 1.47), bevel=0.0)
B.done(3)
stone = B.to_object('SW_TruthStone', c, [M_stone, M_groove, M_rune, M_slot], sharp_deg=30)
prop(stone, 'glow', 0.0, 0.0, 5.0, 'Blue truth glow: 0 off, 1 on')

# glow light (energy = glow * 300 W, driven, no script expression)
ld = bpy.data.lights.new('SW_TruthStone_GlowLight', 'POINT')
ld.color = lin('#49A6FF')[:3]
ld.shadow_soft_size = 1.5
ld.energy = 0.0
lo = bpy.data.objects.new('SW_TruthStone_GlowLight', ld)
c.objects.link(lo)
lo.parent = stone
lo.location = (0, 0, 2.0)
fc = ld.driver_add('energy')
fc.driver.type = 'SUM'
v = fc.driver.variables.new()
v.name = 'SW_glow'
v.type = 'SINGLE_PROP'
v.targets[0].id = stone
v.targets[0].data_path = '["glow"]'
fm = fc.modifiers[0] if fc.modifiers else fc.modifiers.new('GENERATOR')
fm.mode = 'POLYNOMIAL'
fm.poly_order = 1
fm.coefficients = (0.0, 300.0)

# cracks
M_crack = bpy.data.materials.new('SW_Mat_TruthStoneCrack')
M_crack.use_nodes = True
nt = M_crack.node_tree
bs = nt.nodes['Principled BSDF']
bs.inputs['Base Color'].default_value = lin('#FF5A1E')
bs.inputs['Emission Color'].default_value = lin('#FF4A12')
nt.links.new(smath(nt, 'MULTIPLY', obj_attr(nt, 'glow'), 7.0), bs.inputs['Emission Strength'])


def top_z(r):
    if r < 1.87: return 1.5
    if r < 1.93: return 1.5 - (r - 1.87) / 0.06 * 0.08
    if r < 2.52: return 1.42
    if r < 2.58: return 1.42 + (r - 2.52) / 0.06 * 0.08
    return 1.5


def crack_tube(B, pts):
    """pts: list of (pos, up, width). A raised jagged ribbon (closed prism)."""
    rings = []
    n = len(pts)
    for i, (p, up, w) in enumerate(pts):
        d = (pts[min(i + 1, n - 1)][0] - pts[max(i - 1, 0)][0]).normalized()
        side = up.cross(d).normalized()
        rings.append([p + up * 0.04 + side * w / 2, p + up * 0.04 - side * w / 2,
                      p - up * 0.06 - side * w / 2, p - up * 0.06 + side * w / 2])
    B.loft(rings)
    B.done(0)


def crack_path(a0, r0, r1, w0, w1, side_drop=0.0):
    pts = []
    a = a0
    r = r0
    step = 0.34
    k = 0
    while r < r1:
        f = (r - r0) / (r1 - r0)
        aj = a + (0.1 if k % 2 else -0.1) * (0.6 + 0.8 * random.random()) / max(r, 0.5)
        pts.append((Vector((r * math.cos(aj), r * math.sin(aj), top_z(r))), Vector((0, 0, 1)), w0 + (w1 - w0) * f))
        r += step * (0.7 + 0.6 * random.random())
        a += random.uniform(-0.03, 0.03)
        k += 1
    if side_drop > 0:
        z = 1.42
        R = 3.05
        pts.append((Vector((2.99 * math.cos(a), 2.99 * math.sin(a), 1.47)), Vector((math.cos(a), math.sin(a), 1)).normalized(), w1))
        k = 0
        while z > 1.42 - side_drop:
            aj = a + (0.03 if k % 2 else -0.03) * (0.6 + random.random())
            f = (1.42 - z) / side_drop
            pts.append((Vector((R * math.cos(aj), R * math.sin(aj), z)), Vector((math.cos(aj), math.sin(aj), 0)), w1 * (1 - 0.7 * f)))
            z -= 0.2
            k += 1
    return pts, a


B = Build()
for i, a0 in enumerate((0.35, 1.5, 2.75, 3.9, 5.2)):
    drop = (0.6, 0.0, 0.45, 0.7, 0.0)[i]
    r_end = 2.93 if drop > 0 else (2.4, 2.75)[i % 2]
    pts, a_end = crack_path(a0, 0.95, r_end, 0.2, 0.1, drop)
    crack_tube(B, pts)
    # one branch per crack
    j = len([p for p in pts if p[1].z > 0.99]) // 2
    bp = pts[j][0]
    br = math.hypot(bp.x, bp.y)
    ba = math.atan2(bp.y, bp.x)
    pts2, _ = crack_path(ba + (0.0), br, min(br + 1.0, 2.85), 0.12, 0.05)
    sgn = 1 if i % 2 else -1
    pts2 = [(Vector((math.hypot(p.x, p.y) * math.cos(math.atan2(p.y, p.x) + sgn * 0.45 * (k / len(pts2))),
                     math.hypot(p.x, p.y) * math.sin(math.atan2(p.y, p.x) + sgn * 0.45 * (k / len(pts2))), p.z)), u, w)
            for k, (p, u, w) in enumerate(pts2)]
    crack_tube(B, pts2)
cracks = B.to_object('SW_TruthStone_Cracks', c, [M_crack], sharp_deg=20, smooth=False)
cracks.parent = stone
prop(cracks, 'glow', 1.0, 0.0, 5.0, 'Crack glow strength')
cracks.hide_render = True
cracks.hide_viewport = True


# ----------------------------------------------------------------- king's empty scabbard
c = collection('SW_Scabbard_King')
B = Build()


def rect_ring(B, hx, hy, t, z0, z1, bevel=0.03):
    """A rectangular band (outer half sizes hx, hy; wall t)."""
    o = [Vector((hx, hy, 0)), Vector((-hx, hy, 0)), Vector((-hx, -hy, 0)), Vector((hx, -hy, 0))]
    i = [Vector((hx - t, hy - t, 0)), Vector((-hx + t, hy - t, 0)), Vector((-hx + t, -hy + t, 0)), Vector((hx - t, -hy + t, 0))]
    up = lambda ring, z: [p + Vector((0, 0, z)) for p in ring]
    bm = B.bm
    vr = B.loft([up(o, z0), up(o, z1), up(i, z1), up(i, z0), up(o, z0)], cap_start=False, cap_end=False)
    if bevel > 0:
        es = list({e for ring in vr for v in ring for e in v.link_edges})
        bmesh.ops.remove_doubles(bm, verts=[v for ring in vr for v in ring], dist=1e-5)
        es = [e for e in bm.edges if e.is_valid and not e.verts[0][B.vd] and not e.verts[1][B.vd]]
        bmesh.ops.bevel(bm, geom=es, offset=bevel, segments=1, profile=0.5, affect='EDGES')


# belt around an adult waist (torso about 2.1 x 1.05 BU), origin = belt centre
rect_ring(B, 1.14, 0.62, 0.08, -0.15, 0.15, bevel=0.035); B.done(0)
# buckle (front = -Y)
rect_ring(B, 0.26, 0.2, 0.07, -0.05, 0.05, bevel=0.02); B.done(1, M=T(0, -0.66, 0) @ RX(90))
B.box((0.07, 0.05, 0.3), (0, -0.69, 0), bevel=0.015); B.done(1)
# belt studs
for x in (-0.75, -0.5, 0.5, 0.75):
    B.ball(0.06, (x, -0.63, 0), 1); B.done(1)


def octa(hw, ht, z):
    k = 0.55
    return [Vector((hw, ht * k, z)), Vector((hw * k, ht, z)), Vector((-hw * k, ht, z)), Vector((-hw, ht * k, z)),
            Vector((-hw, -ht * k, z)), Vector((-hw * k, -ht, z)), Vector((hw * k, -ht, z)), Vector((hw, -ht * k, z))]


# scabbard in its own frame: mouth at z=0, body down -Z, wide axis = X (later turned so it lies along the hip)
SM = T(1.36, 0.05, 0.12) @ RX(-24) @ RZ(90)
W, TH = 0.3, 0.13


def band(z0, z1, k0, k1, grow, mi, caps=(False, False)):
    B.loft([octa(W * k0 + grow, TH * k0 + grow, z0), octa(W * k1 + grow, TH * k1 + grow, z1)],
           cap_start=caps[0], cap_end=caps[1])
    B.done(mi, M=SM)


def kz(z):  # taper factor along the body
    return 1.0 - 0.38 * min(1.0, max(0.0, (-z) / 3.3))


# red body (closed tube from mouth floor to tip)
B.loft([octa(W * kz(z), TH * kz(z), z) for z in (-0.05, -1.2, -2.2, -3.05)], cap_start=True, cap_end=True)
B.done(2, M=SM)
# gold locket (the open mouth): outer sleeve + lip + inner dark hollow
g = 0.035
B.loft([octa(W + g, TH + g, -0.6), octa(W + g + 0.02, TH + g + 0.02, -0.55), octa(W + g + 0.02, TH + g + 0.02, -0.04),
        octa(W + g, TH + g, 0.0), octa(W - 0.05, TH - 0.05, 0.0)], cap_start=True, cap_end=False)
B.done(1, M=SM)
B.loft([octa(W - 0.05, TH - 0.05, 0.0), octa(W - 0.06, TH - 0.055, -0.5)], cap_start=False, cap_end=False)
B.done(3, M=SM)
B.loft([octa(W - 0.06, TH - 0.055, -0.5)], cap_start=True, cap_end=False)
B.done(3, M=SM)
# middle band and chape (tip)
k = kz(-1.7)
B.loft([octa(W * k + g, TH * k + g, -1.85), octa(W * k + g + 0.015, TH * k + g + 0.015, -1.8),
        octa(W * k + g + 0.015, TH * k + g + 0.015, -1.6), octa(W * k + g, TH * k + g, -1.55)])
B.done(1, M=SM)
B.loft([octa(W * kz(-2.6) + g, TH * kz(-2.6) + g, -2.6), octa(W * kz(-3.0) + g, TH * kz(-3.0) + g, -3.05),
        octa(W * 0.42, TH * 0.6, -3.25), octa(W * 0.12, TH * 0.2, -3.36)])
B.done(1, M=SM)
B.ball(0.09, (0, 0, -3.38), 1); B.done(1, M=SM)
# jewels on the outer face (+Y in scabbard frame after RZ(90) = wearer's outside... both faces get them)
for sy in (-1, 1):
    for (z, r, mi) in ((-0.3, 0.1, 5), (-1.7, 0.085, 4), (-2.85, 0.07, 6)):
        B.ball(r, (0, sy * (TH * kz(z) + g + 0.01), z), 1, (1.0, 0.55, 1.0)); B.done(mi, M=SM)
# hanger straps from belt to locket
B.box((0.1, 0.16, 0.42), (1.17, -0.02, 0.0), bevel=0.02, rot=RY(-8)); B.done(0)
B.box((0.1, 0.16, 0.5), (1.18, 0.3, -0.12), bevel=0.02, rot=RY(-8) @ RX(-10)); B.done(0)
scab = B.to_object('SW_Scabbard_King', c, [M_leather, M_gold, M_red, M_dark, M_sapph, M_ruby, M_emer], sharp_deg=30)
scab.location = (15.5, 0, 3.3)


# ----------------------------------------------------------------- bell
c = collection('SW_Bell')
B = Build()
for sx in (-1, 1):
    B.box((0.36, 0.36, 4.0), (sx * 1.55, 0, 2.0), bevel=0.05); B.done(0)
    B.box((0.5, 1.9, 0.32), (sx * 1.55, 0, 0.16), bevel=0.07); B.done(1)
    for sy in (-1, 1):  # diagonal braces
        B.box((0.2, 0.2, 1.3), (sx * 1.55, sy * 0.48, 0.72), bevel=0.03, rot=RX(sy * 38)); B.done(1)
B.box((3.9, 0.46, 0.4), (0, 0, 4.15), bevel=0.07); B.done(0)
B.box((4.3, 0.7, 0.14), (0, 0, 4.42), bevel=0.04); B.done(1)   # little roof cap
for sx in (-1, 1):  # iron hinge plates on the posts
    B.box((0.08, 0.42, 0.42), (sx * 1.35, 0, 3.45), bevel=0.02); B.done(2)
bell_frame = B.to_object('SW_Bell', c, [M_wood, M_wood_dark, M_iron], sharp_deg=30)
bell_frame.location = (-8, 0, 0)

pivot = bpy.data.objects.new('SW_Bell_Pivot', None)
pivot.empty_display_type = 'ARROWS'
pivot.empty_display_size = 0.6
c.objects.link(pivot)
pivot.parent = bell_frame
pivot.location = (0, 0, 3.45)

B = Build()
# yoke (wood) with iron axle, in pivot space
B.box((2.3, 0.34, 0.34), (0, 0, 0), bevel=0.06); B.done(1)
B.lathe([(0, -1.32), (0.08, -1.32), (0.08, 1.32), (0, 1.32)], segs=8); B.done(2, M=RY(90))
# crown + bell
B.lathe([(0, -0.17), (0.2, -0.17), (0.2, -0.38), (0, -0.38)], segs=10); B.done(0)
prof = [(0.0, -0.36), (0.3, -0.38), (0.48, -0.48), (0.56, -0.68), (0.6, -1.05), (0.68, -1.45), (0.84, -1.78),
        (1.0, -1.98), (1.03, -2.08), (0.96, -2.1), (0.86, -2.02), (0.72, -1.8), (0.55, -1.4), (0.5, -0.9), (0.0, -0.8)]
B.lathe(prof, segs=24); B.done(0)
B.lathe([(0.62, -1.12), (0.66, -1.16), (0.67, -1.26), (0.63, -1.3)], segs=24, cap_start=False, cap_end=False); B.done(3)
B.lathe([(0.9, -1.84), (0.955, -1.87), (0.975, -1.93), (0.93, -1.96)], segs=24, cap_start=False, cap_end=False); B.done(3)
bell = B.to_object('SW_Bell_Body', c, [M_bronze, M_wood_dark, M_iron, mat('SW_Mat_BronzeBand', '#9C6A2A', 0.45, 0.5)], sharp_deg=40)
bell.parent = pivot

B = Build()
B.lathe([(0, -0.8), (0.045, -0.8), (0.045, -1.75), (0, -1.75)], segs=8); B.done(0)
B.ball(0.2, (0, 0, -1.85), 2); B.done(0)
B.lathe([(0, -2.0), (0.085, -2.0), (0.085, -2.75), (0, -2.75)], segs=8); B.done(1)
B.ball(0.17, (0, 0, -2.78), 1); B.done(1)
B.lathe([(0, -2.85), (0.16, -2.92), (0.1, -3.2), (0, -3.22)], segs=8); B.done(1)
rope = B.to_object('SW_Bell_Rope', c, [M_iron, M_rope], sharp_deg=40)
rope.parent = pivot


# ----------------------------------------------------------------- clouds
c = collection('SW_Cloud')
M_cloud = mat('SW_Mat_Cloud', '#FFFFFF', 1.0, 0.0, '#EAF2FF', 0.35)


def cloud(name, blobs, loc):
    B = Build()
    for (x, y, z, r) in blobs:
        B.ball(r, (x, y, z), 3, (1.0, 1.0, 0.82))
        B.done(0)
    for v in B.bm.verts:
        if v.co.z < 0:
            v.co.z = v.co.z * 0.12
    ob = B.to_object(name, c, [M_cloud], sharp_deg=80, recalc=False)
    ob.location = loc
    return ob


cloud('SW_Cloud_A', [(-38, 0, 6, 15), (-18, 3, 13, 21), (6, -2, 17, 25), (28, 2, 10, 19), (42, 0, 4, 12),
                     (-6, 14, 8, 17), (14, -14, 7, 16), (-26, -10, 5, 13)], (0, 160, 40))
cloud('SW_Cloud_B', [(-26, 0, 5, 12), (-8, 2, 12, 19), (14, -2, 9, 16), (28, 0, 4, 10), (2, 12, 6, 13),
                     (-12, -10, 5, 12)], (-110, 160, 40))
cloud('SW_Cloud_C', [(-18, 0, 4, 10), (-2, 0, 9, 15), (16, 1, 5, 11), (4, -9, 4, 10), (-6, 9, 4, 10)], (100, 160, 40))


# ----------------------------------------------------------------- shovel
c = collection('SW_Shovel')
B = Build()
B.lathe([(0, 0.95), (0.095, 0.95), (0.085, 3.95), (0, 3.95)], segs=10); B.done(0)
# D handle
B.box((0.62, 0.17, 0.15), (0, 0, 3.98), bevel=0.04); B.done(1)
B.box((0.62, 0.17, 0.15), (0, 0, 4.42), bevel=0.05); B.done(1)
for sx in (-1, 1):
    B.box((0.14, 0.17, 0.5), (sx * 0.25, 0, 4.2), bevel=0.04); B.done(1)
# wooden blade (scoop, slightly tapered) with a worn iron edge
ring = lambda hw, hy, z, bow: [Vector((hw, -hy + bow, z)), Vector((hw * 0.5, -hy, z)), Vector((-hw * 0.5, -hy, z)),
                               Vector((-hw, -hy + bow, z)), Vector((-hw, hy + bow, z)), Vector((-hw * 0.5, hy, z)),
                               Vector((hw * 0.5, hy, z)), Vector((hw, hy + bow, z))]
B.loft([ring(0.2, 0.07, 1.42, 0.0), ring(0.5, 0.06, 1.28, 0.05), ring(0.52, 0.055, 0.5, 0.06), ring(0.46, 0.05, 0.2, 0.05)])
B.done(0)
B.loft([ring(0.47, 0.058, 0.24, 0.05), ring(0.44, 0.058, 0.1, 0.045), ring(0.3, 0.04, 0.0, 0.03)])
B.done(2)
B.box((0.26, 0.2, 0.36), (0, 0, 1.3), bevel=0.05); B.done(1)   # socket collar
shovel = B.to_object('SW_Shovel', c, [M_wood, M_wood_dark, M_iron], sharp_deg=30)
shovel.location = (18, 0, 0)

# ----------------------------------------------------------------- save
for ob in bpy.data.objects:
    assert ob.name.startswith('SW_'), ob.name
    assert tuple(round(s, 6) for s in ob.scale) == (1, 1, 1)
for m in list(bpy.data.materials):
    if m.users == 0:
        bpy.data.materials.remove(m)
bpy.ops.file.pack_all()
bpy.context.preferences.filepaths.use_relative_paths = True
bpy.ops.wm.save_as_mainfile(filepath=OUT, relative_remap=True, compress=True)
print('SAVED', OUT)
for col in scene.collection.children:
    print(col.name, [o.name for o in col.objects])
dg = bpy.context.evaluated_depsgraph_get()
for ob, vals in ((sw_boy, (1, 6, 40, 700)), (sw_gold, (5, 2, 0.75, 0.5)), (sw_guard, (4.5, 5.5))):
    for L in vals:
        ob['sword_length'] = float(L)
        ob.update_tag()
        dg.update()
        ev = ob.evaluated_get(dg)
        me = ev.to_mesh()
        zs = [v.co.z for v in me.vertices]
        xs = [v.co.x for v in me.vertices]
        print(ob.name, 'L', L, 'z', round(min(zs), 3), round(max(zs), 3), 'len', round(max(zs) - min(zs), 3), 'w', round(max(xs) - min(xs), 3))
        ev.to_mesh_clear()
