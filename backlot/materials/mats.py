"""Backlot material library (In This Town studio).

Procedural, layered PBR materials for Cycles, built from node groups so they append cleanly
and work in Blender 5.1+.  Units: 1 m = 3.3 Blender units (BU).  Every material is called
"BL <Name>" and is made of:

    SURF  group "BLS <Name>"  (procedural surface: Color, Roughness, Metallic, Normal, Height, Cavity)
    WEAR  group "BLW Wear"    (edge wear, crevice grime, moss on north/up faces, damp near the ground,
                               rain streaks; shared by every material)
    Principled BSDF (+ optional sheen / translucency / transmission), Displacement for ground and roofs.

Texture space: every mesh made by the backlot builder carries a UV map "UVm" measured in metres
(V points up the wall / up the roof slope, U along wood grain for timber).  3D noise uses object
space in metres.  So a material looks the same size on every object.

Switching to photo-scanned CC0 sets (Poly Haven / ambientCG):
    use_image_set('Cobbles', '/path/to/cobblestone_floor_04')   # one call, keeps the wear stack
    use_procedural('Cobbles')                                    # back to procedural
    auto_image_sets('/mnt/user-data/uploads/textures/cc0')       # match every folder it can
Global switches live in the node group "BL Global" (Wet 0..1, AO on/off, Moss boost).
"""
import bpy, os, re, glob, math

M = 3.3                       # BU per metre
UVNAME = 'UVm'
PREFIX = 'BL '

# ----------------------------------------------------------------------------------------------
# Small node DSL.  Every helper returns an output *socket*.
# ----------------------------------------------------------------------------------------------
def _ident(coll, ident):
    for s in coll:
        if s.identifier == ident:
            return s
    raise KeyError(ident)


class NB:
    """Node builder bound to one node tree."""
    def __init__(self, tree):
        self.t = tree
        self.N = tree.nodes
        self.L = tree.links
        self._cache = {}

    # -- plumbing ---------------------------------------------------------------------------
    def node(self, typ, **props):
        n = self.N.new(typ)
        for k, v in props.items():
            setattr(n, k, v)
        return n

    def feed(self, sock, val):
        if val is None:
            return
        if isinstance(val, bpy.types.NodeSocket):
            self.L.new(val, sock)
        elif isinstance(val, bpy.types.Node):
            self.L.new(val.outputs[0], sock)
        else:
            dv = sock.default_value
            try:
                n = len(dv)
            except TypeError:
                n = 0
            if n:
                if isinstance(val, (int, float)):
                    val = [val] * n
                val = list(val)
                if len(val) < n:
                    val = val + [1.0] * (n - len(val))
                sock.default_value = val[:n]
            else:
                sock.default_value = val

    # -- constants / coordinates ----------------------------------------------------------
    def val(self, v, label=None):
        n = self.node('ShaderNodeValue')
        n.outputs[0].default_value = v
        if label:
            n.label = n.name = label
        return n.outputs[0]

    def rgb(self, c):
        n = self.node('ShaderNodeRGB')
        n.outputs[0].default_value = (*c[:3], 1)
        return n.outputs[0]

    def _once(self, key, fn):
        if key not in self._cache:
            self._cache[key] = fn()
        return self._cache[key]

    def texco(self, out='Object'):
        n = self._once('tc', lambda: self.node('ShaderNodeTexCoord'))
        return n.outputs[out]

    def geo(self, out):
        n = self._once('geo', lambda: self.node('ShaderNodeNewGeometry'))
        return n.outputs[out]

    def objinfo(self, out='Random'):
        n = self._once('oi', lambda: self.node('ShaderNodeObjectInfo'))
        return n.outputs[out]

    def uvmap(self):
        def mk():
            n = self.node('ShaderNodeUVMap')
            n.uv_map = UVNAME
            return n
        return self._once('uv', mk).outputs['UV']

    def attr(self, name, out='Fac'):
        def mk():
            n = self.node('ShaderNodeAttribute')
            n.attribute_name = name
            return n
        return self._once('attr' + name, mk).outputs[out]

    # -- math ---------------------------------------------------------------------------------
    def math(self, op, a, b=None, c=None, clamp=False):
        n = self.node('ShaderNodeMath', operation=op, use_clamp=clamp)
        self.feed(n.inputs[0], a)
        if b is not None:
            self.feed(n.inputs[1], b)
        if c is not None:
            self.feed(n.inputs[2], c)
        return n.outputs[0]

    def add(self, a, b): return self.math('ADD', a, b)
    def sub(self, a, b): return self.math('SUBTRACT', a, b)
    def mul(self, a, b, clamp=False): return self.math('MULTIPLY', a, b, clamp=clamp)
    def div(self, a, b): return self.math('DIVIDE', a, b)
    def mn(self, a, b): return self.math('MINIMUM', a, b)
    def mx(self, a, b): return self.math('MAXIMUM', a, b)
    def madd(self, a, b, c): return self.math('MULTIPLY_ADD', a, b, c)
    def clamp01(self, a): return self.math('ADD', a, 0.0, clamp=True)
    def inv(self, a): return self.math('SUBTRACT', 1.0, a)

    def vmath(self, op, a, b=None, scale=None, out='Vector'):
        n = self.node('ShaderNodeVectorMath', operation=op)
        self.feed(n.inputs[0], a)
        if b is not None:
            self.feed(n.inputs[1], b)
        if scale is not None:
            self.feed(n.inputs[3], scale)
        return n.outputs[out]

    def vscale(self, a, s): return self.vmath('SCALE', a, scale=s)
    def vadd(self, a, b): return self.vmath('ADD', a, b)
    def vmul(self, a, b): return self.vmath('MULTIPLY', a, b)

    def sep(self, v):
        n = self.node('ShaderNodeSeparateXYZ')
        self.feed(n.inputs[0], v)
        return n.outputs[0], n.outputs[1], n.outputs[2]

    def comb(self, x=0.0, y=0.0, z=0.0):
        n = self.node('ShaderNodeCombineXYZ')
        for i, v in enumerate((x, y, z)):
            self.feed(n.inputs[i], v)
        return n.outputs[0]

    def maprange(self, v, a, b, c=0.0, d=1.0, interp='LINEAR', clamp=True):
        n = self.node('ShaderNodeMapRange', interpolation_type=interp, clamp=clamp)
        self.feed(n.inputs['Value'], v)
        self.feed(n.inputs['From Min'], a)
        self.feed(n.inputs['From Max'], b)
        self.feed(n.inputs['To Min'], c)
        self.feed(n.inputs['To Max'], d)
        return n.outputs[0]

    def smooth(self, v, a, b):
        return self.maprange(v, a, b, 0, 1, 'SMOOTHSTEP')

    def mix(self, fac, a, b, kind='RGBA', blend='MIX', clamp=True):
        n = self.node('ShaderNodeMix', data_type=kind, blend_type=blend, clamp_factor=clamp)
        suf = {'RGBA': 'Color', 'FLOAT': 'Float', 'VECTOR': 'Vector'}[kind]
        self.feed(_ident(n.inputs, 'Factor_Float'), fac)
        self.feed(_ident(n.inputs, 'A_' + suf), a)
        self.feed(_ident(n.inputs, 'B_' + suf), b)
        return _ident(n.outputs, 'Result_' + suf)

    def mixf(self, fac, a, b): return self.mix(fac, a, b, 'FLOAT')

    def cmul(self, a, b, fac=1.0):
        return self.mix(fac, a, b, 'RGBA', 'MULTIPLY')

    def hsv(self, col, h=0.5, s=1.0, v=1.0, fac=1.0):
        n = self.node('ShaderNodeHueSaturation')
        for k, x in (('Hue', h), ('Saturation', s), ('Value', v), ('Fac', fac), ('Color', col)):
            self.feed(n.inputs[k], x)
        return n.outputs[0]

    def ramp(self, fac, stops, interp='LINEAR'):
        n = self.node('ShaderNodeValToRGB')
        cr = n.color_ramp
        cr.interpolation = interp
        while len(cr.elements) < len(stops):
            cr.elements.new(0.5)
        for e, (p, c) in zip(cr.elements, stops):
            e.position = p
            e.color = (*c[:3], 1) if len(c) == 3 else tuple(c)
        self.feed(n.inputs[0], fac)
        return n.outputs[0]

    # -- textures -------------------------------------------------------------------------------
    def noise(self, vec, scale=1.0, detail=3.0, rough=0.5, distortion=0.0, out='Fac', dims='3D', w=None, lac=2.0):
        n = self.node('ShaderNodeTexNoise', noise_dimensions=dims)
        self.feed(n.inputs['Vector'], vec)
        if w is not None and dims in ('4D', '1D'):
            self.feed(n.inputs['W'], w)
        self.feed(n.inputs['Scale'], scale)
        self.feed(n.inputs['Detail'], detail)
        self.feed(n.inputs['Roughness'], rough)
        self.feed(n.inputs['Lacunarity'], lac)
        self.feed(n.inputs['Distortion'], distortion)
        return n.outputs[out]

    def voronoi(self, vec, scale=1.0, feature='F1', out='Distance', rnd=1.0, dims='3D', smooth=1.0, metric='EUCLIDEAN'):
        n = self.node('ShaderNodeTexVoronoi', feature=feature, voronoi_dimensions=dims, distance=metric)
        self.feed(n.inputs['Vector'], vec)
        self.feed(n.inputs['Scale'], scale)
        self.feed(n.inputs['Randomness'], rnd)
        if feature == 'SMOOTH_F1':
            self.feed(n.inputs['Smoothness'], smooth)
        if isinstance(out, (list, tuple)):
            return [n.outputs[o] for o in out]
        return n.outputs[out]

    def wave(self, vec, scale=1.0, distortion=0.0, detail=2.0, dscale=1.0, wtype='BANDS', direction='X', profile='SIN', out='Fac', phase=0.0):
        n = self.node('ShaderNodeTexWave', wave_type=wtype, wave_profile=profile)
        if wtype == 'BANDS':
            n.bands_direction = direction
        else:
            n.rings_direction = direction if direction in ('X', 'Y', 'Z', 'SPHERICAL') else 'SPHERICAL'
        self.feed(n.inputs['Vector'], vec)
        self.feed(n.inputs['Scale'], scale)
        self.feed(n.inputs['Distortion'], distortion)
        self.feed(n.inputs['Detail'], detail)
        self.feed(n.inputs['Detail Scale'], dscale)
        self.feed(n.inputs['Phase Offset'], phase)
        return n.outputs[out]

    def white(self, vec, out='Value', dims='3D'):
        n = self.node('ShaderNodeTexWhiteNoise', noise_dimensions=dims)
        self.feed(n.inputs['Vector'], vec)
        return n.outputs[out]

    def bump(self, height, strength=1.0, distance=1.0, normal=None):
        n = self.node('ShaderNodeBump')
        self.feed(n.inputs['Strength'], strength)
        self.feed(n.inputs['Distance'], distance)
        self.feed(n.inputs['Height'], height)
        if normal is not None:
            self.feed(n.inputs['Normal'], normal)
        return n.outputs[0]

    def ao(self, distance, inside=False, samples=4):
        n = self.node('ShaderNodeAmbientOcclusion', inside=inside, only_local=True, samples=samples)
        self.feed(n.inputs['Distance'], distance)
        return n.outputs['AO']

    def group(self, tree):
        n = self.node('ShaderNodeGroup')
        n.node_tree = tree
        return n

    # -- pattern helpers --------------------------------------------------------------------------
    def bond(self, u, v, w, h, offset=0.5, randoff=0.0, wvar=0.0, seed=0.0):
        """Running-bond block pattern in metres.  Returns dict(id, rid (per row), lu, lv, edge, w, h)."""
        row = self.math('FLOOR', self.div(v, h))
        rrand = self.white(self.comb(row, seed, 3.7), 'Value')
        wrow = self.mul(w, self.add(1.0, self.mul(self.sub(rrand, 0.5), wvar))) if wvar else w
        off = self.mul(self.math('FLOORED_MODULO', row, 2.0), offset)
        if randoff:
            off = self.add(off, self.mul(rrand, randoff))
        uo = self.add(self.div(u, wrow), off)
        col = self.math('FLOOR', uo)
        bid = self.white(self.comb(col, row, seed), 'Value')
        bcol = self.white(self.comb(col, row, seed), 'Color')
        lu = self.mul(self.math('FRACT', uo), wrow)
        lv = self.mul(self.math('FRACT', self.div(v, h)), h)
        e = self.mn(self.mn(lu, self.sub(wrow, lu)), self.mn(lv, self.sub(h, lv)))
        return dict(id=bid, idc=bcol, rid=rrand, lu=lu, lv=lv, edge=e, w=wrow, h=h, row=row, col=col)


# ----------------------------------------------------------------------------------------------
# Global switches and the shared wear stack
# ----------------------------------------------------------------------------------------------
def _new_group(name, inputs, outputs):
    g = bpy.data.node_groups.get(name)
    if g:
        bpy.data.node_groups.remove(g)
    g = bpy.data.node_groups.new(name, 'ShaderNodeTree')
    for item in inputs:
        n, t, d = item[:3]
        s = g.interface.new_socket(name=n, in_out='INPUT', socket_type=t)
        if d is not None:
            try:
                s.default_value = d
            except Exception:
                pass
        if len(item) > 3:
            s.min_value, s.max_value = item[3]
    for n, t in outputs:
        g.interface.new_socket(name=n, in_out='OUTPUT', socket_type=t)
    gi = g.nodes.new('NodeGroupInput')
    go = g.nodes.new('NodeGroupOutput')
    return g, gi, go


F, C, Vt = 'NodeSocketFloat', 'NodeSocketColor', 'NodeSocketVector'


def global_group():
    """'BL Global' holds scene-wide switches. Edit the Value nodes inside it."""
    name = 'BL Global'
    g = bpy.data.node_groups.get(name)
    if g:
        return g
    g, gi, go = _new_group(name, [], [('Wet', F), ('AO', F), ('Moss', F), ('Time', F)])
    nb = NB(g)
    nb.L.new(nb.val(0.35, 'Wet'), go.inputs['Wet'])
    nb.L.new(nb.val(1.0, 'AO'), go.inputs['AO'])
    nb.L.new(nb.val(1.0, 'Moss'), go.inputs['Moss'])
    t = nb.node('ShaderNodeValue')
    t.name = t.label = 'Time'
    # seconds at 24 fps; a 'simple expression' driver (no Python auto-run needed)
    fc = t.outputs[0].driver_add('default_value')
    fc.driver.type = 'SCRIPTED'
    fc.driver.expression = 'frame/24'
    nb.L.new(t.outputs[0], go.inputs['Time'])
    return g


def set_global(wet=None, ao=None, moss=None):
    g = global_group()
    for k, v in (('Wet', wet), ('AO', ao), ('Moss', moss)):
        if v is not None:
            g.nodes[k].outputs[0].default_value = v


def wear_group():
    name = 'BLW Wear'
    g = bpy.data.node_groups.get(name)
    if g:
        return g
    g, gi, go = _new_group(name, [
        ('Color', C, (0.5, 0.5, 0.5, 1)), ('Roughness', F, 0.6), ('Cavity', F, 0.0),
        ('Edge', F, 0.0), ('Edge Color', C, (0.6, 0.55, 0.5, 1)), ('Grime', F, 0.5),
        ('Moss', F, 0.0), ('Damp', F, 0.0), ('Streaks', F, 0.0), ('Ground Z', F, 0.0),
        ('Wet Response', F, 1.0)],
        [('Color', C), ('Roughness', F)])
    nb = NB(g)
    I = gi.outputs
    glob_ = nb.group(global_group())
    G = glob_.outputs
    pw = nb.vscale(nb.geo('Position'), 1.0 / M)
    px, py, pz = nb.sep(pw)
    nx, ny, nz = nb.sep(nb.geo('Normal'))
    col = I['Color']
    rough = I['Roughness']
    # crevice grime (AO) + pattern cavity
    ao = nb.ao(0.35 * M, False, 4)
    crev = nb.mul(nb.inv(ao), G['AO'])
    gmask = nb.clamp01(nb.mul(nb.add(I['Cavity'], nb.mul(crev, 0.9)), I['Grime']))
    gn = nb.noise(pw, 2.5, 3, 0.6)
    gmask = nb.clamp01(nb.mul(gmask, nb.maprange(gn, 0.3, 0.7, 0.6, 1.4)))
    grime_col = nb.mix(gn, (0.09, 0.075, 0.055), (0.16, 0.13, 0.09))
    col = nb.mix(nb.mul(gmask, 0.85), col, nb.cmul(col, grime_col, 1.0))
    rough = nb.mixf(nb.mul(gmask, 0.6), rough, 0.95)
    # edge wear (AO inside)
    aoin = nb.ao(0.06 * M, True, 4)
    edge = nb.mul(nb.inv(aoin), G['AO'])
    en = nb.noise(pw, 9.0, 4, 0.65)
    emask = nb.mul(nb.smooth(nb.add(nb.mul(edge, 1.6), nb.mul(en, 0.7)), 0.75, 1.05), I['Edge'])
    col = nb.mix(emask, col, I['Edge Color'])
    rough = nb.mixf(nb.mul(emask, 0.5), rough, 0.45)
    # rain streaks on vertical faces
    sn = nb.noise(nb.comb(nb.mul(px, 14.0), nb.mul(py, 14.0), nb.mul(pz, 0.7)), 1.0, 4, 0.6)
    sn2 = nb.noise(pw, 0.8, 2, 0.5)
    vert = nb.inv(nb.math('ABSOLUTE', nz))
    smask = nb.mul(nb.mul(nb.smooth(nb.add(sn, nb.mul(sn2, 0.4)), 0.62, 0.8), vert), I['Streaks'])
    col = nb.mix(smask, col, nb.cmul(col, (0.55, 0.5, 0.45), 1.0))
    # damp band near the ground (+ global wetness)
    hz = nb.sub(pz, nb.div(I['Ground Z'], M))
    dn = nb.noise(pw, 3.0, 3, 0.6)
    dband = nb.inv(nb.smooth(hz, 0.0, nb.add(0.35, nb.mul(dn, 0.6))))
    dmask = nb.clamp01(nb.mul(dband, I['Damp']))
    wet = nb.mul(G['Wet'], I['Wet Response'])
    up = nb.clamp01(nz)
    puddly = nb.mul(nb.mul(wet, up), nb.smooth(nb.noise(pw, 0.7, 2, 0.5), 0.45, 0.6))
    wmask = nb.clamp01(nb.add(dmask, nb.mul(wet, 0.35)))
    col = nb.mix(wmask, col, nb.cmul(col, (0.62, 0.6, 0.58), 1.0))
    rough = nb.mixf(nb.clamp01(nb.add(nb.mul(wmask, 0.55), nb.mul(puddly, 0.4))), rough, nb.mul(rough, 0.45))
    # moss: up- and north-facing (+Y) faces, crevices and the ground band
    mdir = nb.add(nb.mul(nb.clamp01(nz), 0.16), nb.mul(nb.clamp01(ny), 0.12))
    mn1 = nb.noise(pw, 2.2, 5, 0.62)
    mn2 = nb.noise(pw, 11.0, 3, 0.6)
    mfield = nb.add(nb.add(mn1, mdir), nb.add(nb.mul(I['Cavity'], 0.16), nb.mul(dband, 0.08)))
    mmask = nb.mul(nb.smooth(nb.add(mfield, nb.mul(mn2, 0.1)), 0.7, 0.78), nb.mul(I['Moss'], G['Moss']))
    mcol = nb.ramp(mn2, [(0.3, (0.025, 0.045, 0.008)), (0.55, (0.07, 0.11, 0.018)), (0.75, (0.16, 0.17, 0.04))])
    col = nb.mix(mmask, col, mcol)
    rough = nb.mixf(mmask, rough, 0.92)
    nb.L.new(col, go.inputs['Color'])
    nb.L.new(rough, go.inputs['Roughness'])
    return g


# ----------------------------------------------------------------------------------------------
# Surface builders.  Each receives an NB bound to its "BLS" group plus a coordinate helper and
# returns dict(color, rough, height[m], cavity, metal, micro[m], extra...).
# ----------------------------------------------------------------------------------------------
class Co:
    """Coordinates inside a surface group (all in metres)."""
    def __init__(self, nb):
        self.nb = nb
        r = nb.objinfo('Random')
        isl = nb.geo('Random Per Island')
        self.rnd = r
        self.isl = isl
        off = nb.comb(nb.mul(r, 37.31), nb.mul(r, 17.77), nb.mul(r, 23.13))
        self.P = nb.vadd(nb.vscale(nb.texco('Object'), 1.0 / M), off)          # object space, metres
        uv = nb.uvmap()
        self.uv0 = uv
        self.u, self.v, _ = nb.sep(uv)
        offu = nb.add(nb.mul(r, 13.7), nb.mul(isl, 5.31))
        offv = nb.add(nb.mul(r, 7.3), nb.mul(isl, 3.17))
        self.ur = nb.add(self.u, offu)                                            # grain-safe offsets
        self.vr = nb.add(self.v, offv)
        self.UVr = nb.comb(self.ur, self.vr, nb.mul(isl, 11.0))


def _vary(nb, col, rnd, hue=0.02, sat=0.15, val=0.2):
    return nb.hsv(col, nb.add(0.5, nb.mul(nb.sub(rnd, 0.5), hue * 2)),
                  nb.add(1.0, nb.mul(nb.sub(rnd, 0.5), sat * 2)),
                  nb.add(1.0, nb.mul(nb.sub(nb.math('FRACT', nb.mul(rnd, 7.13)), 0.5), val * 2)))


def s_cobbles(nb, co, scale=7.0, stretch=1.3, puddles=1.0, moss=1.0, palette=None):
    P = co.P
    px, py, pz = nb.sep(P)
    warp = nb.vscale(nb.vmath('SUBTRACT', nb.noise(P, 1.6, 2, 0.5, out='Color'), (0.5, 0.5, 0.5)), 0.09)
    c = nb.vadd(nb.comb(px, nb.mul(py, stretch), 0.0), warp)
    dist, ccol = nb.voronoi(c, scale, 'F1', ['Distance', 'Color'], 0.9, '2D')
    edge = nb.voronoi(c, scale, 'DISTANCE_TO_EDGE', 'Distance', 0.9, '2D')
    cr, cg, cb = nb.sep(ccol)
    en = nb.noise(P, 22.0, 3, 0.55)
    e2 = nb.add(edge, nb.mul(nb.sub(en, 0.5), 0.012))
    d1 = nb.inv(nb.maprange(e2, 0.002, 0.05, 0.0, 1.0))
    dome = nb.inv(nb.math('POWER', d1, 2.2))                                 # rounded shoulders, finite edge slope
    gap = nb.inv(nb.smooth(e2, 0.003, 0.014))
    stoneh = nb.mul(dome, nb.add(0.018, nb.mul(cg, 0.012)))
    fine = nb.mul(nb.noise(P, 30.0, 3, 0.6), 0.004)
    settle = nb.mul(nb.noise(P, 0.35, 2, 0.5), 0.03)
    h = nb.add(nb.add(stoneh, nb.mul(fine, dome)), settle)
    # puddles: flat water sheet in low spots
    pn = nb.noise(nb.vadd(P, (11.3, 5.1, 0)), 0.13, 3, 0.55)
    pm = nb.mul(nb.smooth(pn, 0.585, 0.61), puddles)
    lvl = nb.add(settle, 0.014)
    water = nb.mul(pm, nb.smooth(nb.sub(lvl, h), -0.002, 0.003))
    h = nb.mixf(pm, h, nb.mx(h, lvl))
    pal = palette or [(0.0, (0.105, 0.105, 0.11)), (0.18, (0.2, 0.195, 0.19)), (0.36, (0.26, 0.22, 0.17)),
                      (0.55, (0.17, 0.16, 0.165)), (0.72, (0.31, 0.29, 0.26)), (0.86, (0.22, 0.17, 0.12)),
                      (1.0, (0.36, 0.34, 0.31))]
    scol = nb.ramp(cr, pal, 'CONSTANT')
    tone = nb.noise(P, 9.0, 4, 0.6)
    scol = nb.cmul(scol, nb.ramp(tone, [(0.3, (0.75, 0.75, 0.75)), (0.7, (1.25, 1.22, 1.18))]))
    speck = nb.smooth(nb.noise(P, 60.0, 2, 0.5), 0.62, 0.7)
    scol = nb.mix(nb.mul(speck, 0.5), scol, (0.45, 0.43, 0.4))
    top = nb.mul(dome, 0.25)
    scol = nb.mix(top, scol, nb.cmul(scol, (1.2, 1.18, 1.14)))
    dirt = nb.mix(nb.noise(P, 5.0, 3, 0.5), (0.05, 0.038, 0.026), (0.1, 0.08, 0.055))
    mn = nb.noise(P, 1.3, 4, 0.6)
    mossm = nb.mul(nb.mul(gap, nb.smooth(mn, 0.42, 0.62)), moss)
    gapcol = nb.mix(mossm, dirt, nb.mix(nb.noise(P, 14.0), (0.03, 0.06, 0.012), (0.1, 0.14, 0.03)))
    col = nb.mix(gap, scol, gapcol)
    col = nb.mix(water, col, nb.cmul(col, (0.42, 0.44, 0.47)))
    rough = nb.add(0.52, nb.mul(nb.sub(tone, 0.5), 0.3))
    rough = nb.mixf(dome, nb.add(rough, 0.25), nb.sub(rough, 0.08))
    rough = nb.mixf(gap, rough, 0.92)
    rough = nb.mixf(water, rough, 0.03)
    return dict(color=col, rough=rough, height=h, cavity=nb.mul(gap, 0.8), micro=nb.mul(fine, 0.5))


def s_flagstones(nb, co, w=0.8, h=0.55, color=(0.3, 0.28, 0.25), mortar=0.012, puddles=0.6):
    u, v, P = co.u, co.v, co.P
    b = nb.bond(u, v, w, h, 0.5, 0.6, 0.6, 2.0)
    en = nb.noise(P, 14.0, 3, 0.6)
    e = nb.add(b['edge'], nb.mul(nb.sub(en, 0.5), 0.018))
    face = nb.smooth(e, mortar * 0.5, mortar + 0.012)
    tilt = nb.mul(nb.sub(b['id'], 0.5), nb.mul(b['lu'], 0.012))
    surf = nb.mul(nb.noise(P, 6.0, 5, 0.6), 0.006)
    hh = nb.mul(face, nb.add(nb.add(0.012, tilt), surf))
    pn = nb.noise(nb.vadd(P, (3.1, 8.2, 0)), 0.18, 3, 0.55)
    pm = nb.mul(nb.smooth(pn, 0.6, 0.63), puddles)
    water = nb.mul(pm, nb.smooth(nb.sub(0.011, hh), -0.002, 0.003))
    hh = nb.mixf(pm, hh, nb.mx(hh, 0.011))
    scol = _vary(nb, color, b['id'], 0.03, 0.3, 0.25)
    scol = nb.cmul(scol, nb.ramp(nb.noise(P, 4.0, 4, 0.6), [(0.3, (0.8, 0.8, 0.8)), (0.7, (1.15, 1.12, 1.08))]))
    gap = nb.inv(face)
    col = nb.mix(gap, scol, (0.06, 0.05, 0.035))
    col = nb.mix(water, col, nb.cmul(col, (0.45, 0.47, 0.5)))
    rough = nb.mixf(gap, nb.add(0.55, nb.mul(nb.sub(en, 0.5), 0.3)), 0.95)
    rough = nb.mixf(water, rough, 0.04)
    return dict(color=col, rough=rough, height=hh, cavity=gap)


def s_ashlar(nb, co, w=0.62, h=0.31, color=(0.46, 0.39, 0.3), mortar=0.011, mortar_col=(0.42, 0.4, 0.36),
             relief=0.014, var=0.22, rough_hewn=0.6, wvar=0.5):
    u, v, P = co.u, co.v, co.P
    b = nb.bond(u, v, w, h, 0.5, 0.35, wvar, 1.0)
    en = nb.noise(P, 18.0, 3, 0.6)
    e = nb.add(b['edge'], nb.mul(nb.sub(en, 0.5), 0.012))
    face = nb.smooth(e, mortar * 0.6, mortar + 0.02)
    hewn = nb.mul(nb.noise(P, 7.0, 5, 0.62), 0.008 * rough_hewn)
    hh = nb.mul(face, nb.add(relief, hewn))
    scol = _vary(nb, color, b['id'], 0.025, 0.35, var)
    tone = nb.noise(P, 3.5, 5, 0.6)
    scol = nb.cmul(scol, nb.ramp(tone, [(0.25, (0.78, 0.76, 0.74)), (0.75, (1.18, 1.15, 1.1))]))
    pores = nb.smooth(nb.noise(P, 45.0, 2, 0.5), 0.64, 0.72)
    scol = nb.mix(nb.mul(pores, 0.45), scol, nb.cmul(scol, (0.6, 0.58, 0.55)))
    gap = nb.inv(face)
    mcol = nb.cmul(nb.rgb(mortar_col), nb.ramp(nb.noise(P, 20.0), [(0.3, (0.8, 0.8, 0.8)), (0.7, (1.1, 1.1, 1.1))]))
    col = nb.mix(gap, scol, mcol)
    rough = nb.mixf(gap, nb.add(0.72, nb.mul(nb.sub(tone, 0.5), 0.2)), 0.95)
    return dict(color=col, rough=rough, height=hh, cavity=nb.mul(gap, 0.9), micro=nb.mul(nb.noise(P, 40, 2), 0.0015))


def s_rubble(nb, co, scale=4.2, color=(0.33, 0.3, 0.26), mortar_col=(0.45, 0.42, 0.37)):
    u, v, P = co.u, co.v, co.P
    c = nb.comb(u, nb.mul(v, 1.45), 0.0)
    warp = nb.vscale(nb.vmath('SUBTRACT', nb.noise(P, 2.0, 2, out='Color'), (0.5, 0.5, 0.5)), 0.12)
    c = nb.vadd(c, warp)
    ccol = nb.voronoi(c, scale, 'F1', 'Color', 1.0, '2D')
    edge = nb.voronoi(c, scale, 'DISTANCE_TO_EDGE', 'Distance', 1.0, '2D')
    en = nb.noise(P, 16.0, 3, 0.6)
    e = nb.add(edge, nb.mul(nb.sub(en, 0.5), 0.02))
    face = nb.smooth(e, 0.008, 0.045)
    cr, cg, cb = nb.sep(ccol)
    hh = nb.mul(nb.math('POWER', face, 0.6), nb.add(0.018, nb.mul(cg, 0.015)))
    hh = nb.add(hh, nb.mul(nb.noise(P, 9.0, 4, 0.6), 0.006))
    pal = [(0.0, (0.2, 0.19, 0.18)), (0.25, (0.36, 0.32, 0.26)), (0.5, (0.28, 0.27, 0.26)),
           (0.7, (0.42, 0.37, 0.3)), (0.85, (0.24, 0.2, 0.15)), (1.0, (0.4, 0.4, 0.38))]
    scol = nb.cmul(nb.ramp(cr, pal, 'CONSTANT'), nb.rgb((color[0] / 0.32, color[1] / 0.29, color[2] / 0.25)))
    scol = nb.cmul(scol, nb.ramp(nb.noise(P, 6.0, 4), [(0.3, (0.8, 0.8, 0.8)), (0.7, (1.15, 1.12, 1.1))]))
    gap = nb.inv(face)
    col = nb.mix(gap, scol, mortar_col)
    rough = nb.mixf(gap, 0.78, 0.95)
    return dict(color=col, rough=rough, height=hh, cavity=nb.mul(gap, 0.8))


def s_brick(nb, co, w=0.235, h=0.075, mortar=0.011):
    u, v, P = co.u, co.v, co.P
    b = nb.bond(u, v, w, h, 0.5, 0.0, 0.0, 4.0)
    en = nb.noise(P, 30.0, 3, 0.6)
    e = nb.add(b['edge'], nb.mul(nb.sub(en, 0.5), 0.006))
    face = nb.smooth(e, mortar * 0.5, mortar + 0.004)
    hh = nb.mul(face, nb.add(0.007, nb.mul(nb.noise(P, 25.0, 3), 0.003)))
    scol = nb.ramp(b['id'], [(0.0, (0.16, 0.055, 0.03)), (0.25, (0.33, 0.12, 0.06)), (0.5, (0.42, 0.17, 0.09)),
                             (0.75, (0.38, 0.2, 0.12)), (0.92, (0.12, 0.07, 0.05)), (1.0, (0.3, 0.12, 0.07))], 'LINEAR')
    scol = nb.cmul(scol, nb.ramp(nb.noise(P, 12.0, 4), [(0.3, (0.75, 0.75, 0.75)), (0.7, (1.2, 1.15, 1.1))]))
    spall = nb.smooth(nb.noise(P, 8.0, 4, 0.6), 0.66, 0.7)
    scol = nb.mix(spall, scol, (0.5, 0.25, 0.15))
    gap = nb.inv(face)
    col = nb.mix(gap, scol, (0.4, 0.38, 0.34))
    return dict(color=col, rough=nb.mixf(gap, 0.8, 0.95), height=nb.sub(hh, nb.mul(spall, 0.003)), cavity=gap)


def s_plaster(nb, co, color=(0.72, 0.66, 0.55), cracks=1.0, damage=1.0):
    P, u, v = co.P, co.u, co.v
    n1 = nb.noise(P, 2.6, 6, 0.62)
    n2 = nb.noise(P, 28.0, 3, 0.6)
    hh = nb.add(nb.mul(n1, 0.005), nb.mul(n2, 0.0013))
    base = nb.cmul(nb.rgb(color), nb.ramp(n1, [(0.25, (0.84, 0.82, 0.8)), (0.75, (1.08, 1.06, 1.04))]))
    blot = nb.noise(P, 0.9, 4, 0.6)
    base = nb.mix(nb.mul(nb.smooth(blot, 0.5, 0.75), 0.35), base, nb.cmul(base, (0.85, 0.8, 0.72)))
    # cracks
    cw = nb.vadd(P, nb.vscale(nb.noise(P, 3.0, 3, out='Color'), 0.25))
    ced = nb.voronoi(cw, 3.2, 'DISTANCE_TO_EDGE', 'Distance', 1.0, '3D')
    crack = nb.inv(nb.smooth(nb.add(ced, nb.mul(nb.noise(P, 40.0), 0.004)), 0.0005, 0.006))
    cmask = nb.mul(nb.smooth(nb.noise(P, 1.4, 3, 0.55), 0.56, 0.66), cracks)
    crack = nb.mul(crack, cmask)
    # damaged patches showing the brick / wattle beneath
    dn = nb.noise(nb.vadd(P, (4.0, 9.0, 1.0)), 0.75, 5, 0.65)
    dmg = nb.mul(nb.smooth(dn, 0.655, 0.665), damage)
    dedge = nb.mul(nb.mul(nb.smooth(dn, 0.635, 0.655), nb.inv(dmg)), damage)
    bb = nb.bond(u, v, 0.235, 0.075, 0.5, 0.0, 0.0, 4.0)
    bface = nb.smooth(bb['edge'], 0.005, 0.012)
    bcol = nb.mix(bface, (0.32, 0.3, 0.27), nb.ramp(bb['id'], [(0, (0.22, 0.08, 0.04)), (0.5, (0.36, 0.15, 0.08)), (1, (0.3, 0.16, 0.1))]))
    col = nb.mix(crack, base, nb.cmul(base, (0.3, 0.28, 0.25)))
    col = nb.mix(nb.mul(dedge, 0.6), col, nb.cmul(col, (0.7, 0.66, 0.6)))
    col = nb.mix(dmg, col, bcol)
    hh = nb.sub(hh, nb.add(nb.mul(crack, 0.0025), nb.mul(dmg, nb.sub(0.008, nb.mul(bface, 0.003)))))
    rough = nb.add(0.86, nb.mul(n2, 0.08))
    return dict(color=col, rough=rough, height=hh, cavity=nb.clamp01(nb.add(nb.mul(crack, 0.9), nb.mul(dmg, 0.5))))


def _grain(nb, co, ring_scale=7.0, check=1.0):
    """Wood grain along U. Returns (fac, crack)."""
    ur, vr, P = co.ur, co.vr, co.P
    g = nb.comb(nb.mul(ur, 0.9), nb.mul(vr, 9.0), nb.mul(co.isl, 3.0))
    rings = nb.wave(g, ring_scale * 0.1, 7.0, 3.0, 1.5, 'BANDS', 'Y', 'SIN')
    streak = nb.noise(nb.comb(nb.mul(ur, 2.0), nb.mul(vr, 70.0), 0.0), 1.0, 5, 0.6)
    fac = nb.add(nb.mul(rings, 0.55), nb.mul(streak, 0.45))
    ck = nb.noise(nb.comb(nb.mul(ur, 0.7), nb.mul(vr, 140.0), nb.mul(co.isl, 9.0)), 1.0, 2, 0.5)
    crack = nb.mul(nb.smooth(ck, 0.74, 0.8), check)
    return fac, crack


def s_timber(nb, co, dark=(0.05, 0.035, 0.025), mid=(0.12, 0.08, 0.05), light=(0.2, 0.17, 0.14), check=1.0):
    fac, crack = _grain(nb, co, 7.0, check)
    col = nb.ramp(fac, [(0.2, dark), (0.55, mid), (0.85, light)])
    col = _vary(nb, col, co.isl, 0.02, 0.2, 0.18)
    col = nb.mix(crack, col, nb.cmul(col, (0.25, 0.25, 0.25)))
    hh = nb.add(nb.mul(fac, 0.0012), nb.mul(crack, -0.003))
    hh = nb.add(hh, nb.mul(nb.noise(co.P, 3.0, 3), 0.002))
    rough = nb.add(0.74, nb.mul(fac, 0.12))
    return dict(color=col, rough=rough, height=hh, cavity=nb.mul(crack, 0.8))


def s_planks(nb, co, board=0.19, length=2.2, dark=(0.09, 0.055, 0.03), mid=(0.2, 0.13, 0.075),
             light=(0.32, 0.24, 0.16), check=0.7, nails=1.0):
    u, v, P = co.u, co.v, co.P
    b = nb.bond(nb.add(u, nb.mul(co.rnd, 9.0)), v, length, board, 0.37, 0.7, 0.6, 5.0)
    gseam = nb.smooth(b['edge'], 0.002, 0.007)
    fac, crack = _grain(nb, co, 6.0, check)
    col = nb.ramp(fac, [(0.2, dark), (0.55, mid), (0.85, light)])
    col = _vary(nb, col, b['id'], 0.03, 0.3, 0.3)
    col = nb.mix(crack, col, nb.cmul(col, (0.3, 0.3, 0.3)))
    # nail heads near board ends
    nu = nb.mn(b['lu'], nb.sub(b['w'], b['lu']))
    nv = nb.math('ABSOLUTE', nb.sub(b['lv'], nb.mul(board, 0.5)))
    nd = nb.vmath('LENGTH', nb.comb(nb.sub(nu, 0.05), nb.mul(nb.sub(nv, 0.045), 1.0), 0.0), out='Value')
    nail = nb.mul(nb.inv(nb.smooth(nd, 0.005, 0.008)), nails)
    col = nb.mix(nail, col, (0.04, 0.035, 0.03))
    hh = nb.add(nb.mul(gseam, 0.004), nb.add(nb.mul(fac, 0.001), nb.mul(crack, -0.002)))
    hh = nb.add(hh, nb.mul(nail, 0.001))
    gap = nb.inv(gseam)
    col = nb.mix(gap, col, (0.02, 0.015, 0.01))
    rough = nb.mixf(nail, nb.add(0.7, nb.mul(fac, 0.15)), 0.45)
    return dict(color=col, rough=rough, height=hh, cavity=nb.clamp01(nb.add(gap, nb.mul(crack, 0.6))),
                metal=nb.mul(nail, 0.7))


def s_iron(nb, co, rust=0.6, color=(0.05, 0.05, 0.055)):
    P = co.P
    n = nb.noise(P, 3.5, 6, 0.65)
    n2 = nb.noise(P, 25.0, 3, 0.6)
    rm = nb.mul(nb.smooth(nb.add(n, nb.mul(n2, 0.2)), 0.62 - rust * 0.18, 0.72 - rust * 0.18), 1.0)
    rcol = nb.ramp(n2, [(0.2, (0.12, 0.04, 0.015)), (0.55, (0.3, 0.1, 0.03)), (0.85, (0.42, 0.2, 0.07))])
    col = nb.mix(rm, nb.mix(nb.mul(n2, 0.5), color, (0.09, 0.085, 0.08)), rcol)
    hh = nb.add(nb.mul(n2, 0.0008), nb.mul(rm, 0.0006))
    return dict(color=col, rough=nb.mixf(rm, nb.add(0.38, nb.mul(n2, 0.2)), 0.9), metal=nb.mixf(rm, 0.85, 0.0),
                height=hh, cavity=0.0)


def s_metal(nb, co, color=(0.9, 0.62, 0.25), rough=0.28, tarnish=(0.2, 0.15, 0.06), tamount=0.5):
    P = co.P
    n = nb.noise(P, 4.0, 5, 0.6)
    n2 = nb.noise(P, 8.0, 3)
    tm = nb.mul(nb.smooth(n, 0.58, 0.75), tamount)
    col = nb.mix(tm, color, tarnish)
    r = nb.add(rough, nb.mul(nb.sub(n2, 0.5), 0.1))
    return dict(color=col, rough=nb.mixf(tm, r, 0.55), metal=nb.mixf(tm, 1.0, 0.6),
                height=nb.mul(n2, 0.0002), cavity=0.0)


def s_verdigris(nb, co):
    P = co.P
    n = nb.noise(P, 3.0, 5, 0.6)
    m = nb.smooth(nb.add(n, nb.mul(nb.noise(P, 20.0), 0.2)), 0.42, 0.55)
    pat = nb.ramp(nb.noise(P, 12.0), [(0.3, (0.08, 0.2, 0.15)), (0.7, (0.16, 0.32, 0.26))])
    col = nb.mix(m, (0.3, 0.13, 0.06), pat)
    return dict(color=col, rough=nb.mixf(m, 0.35, 0.75), metal=nb.mixf(m, 1.0, 0.0), height=nb.mul(n, 0.001), cavity=0.0)


def s_roof_tiles(nb, co, kind='clay', w=0.22, h=0.17, pal=None):
    u, v, P = co.u, co.v, co.P
    b = nb.bond(u, v, w, h, 0.5, 0.08 if kind == 'clay' else 0.5, 0.15 if kind != 'clay' else 0.0, 6.0)
    lu, lv = b['lu'], b['lv']
    t = nb.div(lv, h)                                   # 0 at the tile's lower (exposed) edge
    en = nb.noise(P, 25.0, 3, 0.6)
    if kind == 'clay':
        thick = nb.mul(nb.inv(t), 0.022)
        curve = nb.mul(nb.math('SINE', nb.mul(nb.div(lu, b['w']), math.pi)), 0.012)
        side = nb.smooth(nb.mn(lu, nb.sub(b['w'], lu)), 0.0, 0.012)
        hh = nb.mul(nb.add(thick, curve), side)
        pal = pal or [(0.0, (0.34, 0.1, 0.045)), (0.2, (0.5, 0.17, 0.07)), (0.45, (0.58, 0.24, 0.1)),
                      (0.65, (0.46, 0.2, 0.1)), (0.82, (0.62, 0.3, 0.14)), (1.0, (0.3, 0.12, 0.07))]
        rough_base = 0.7
    elif kind == 'slate':
        thick = nb.mul(nb.inv(t), 0.012)
        side = nb.smooth(nb.mn(lu, nb.sub(b['w'], lu)), 0.0, 0.004)
        chip = nb.smooth(nb.add(nb.mul(t, 0.6), nb.mul(en, 0.6)), 0.25, 0.3)
        hh = nb.mul(nb.mul(thick, side), nb.add(0.4, nb.mul(chip, 0.6)))
        hh = nb.add(hh, nb.mul(nb.sub(b['id'], 0.5), nb.mul(t, 0.006)))
        pal = pal or [(0.0, (0.05, 0.055, 0.065)), (0.3, (0.09, 0.095, 0.11)), (0.55, (0.075, 0.07, 0.09)),
                      (0.8, (0.12, 0.12, 0.13)), (1.0, (0.06, 0.065, 0.07))]
        rough_base = 0.5
    else:  # wooden shingles
        thick = nb.mul(nb.inv(t), 0.016)
        side = nb.smooth(nb.mn(lu, nb.sub(b['w'], lu)), 0.0, 0.006)
        hh = nb.mul(thick, side)
        pal = pal or [(0.0, (0.12, 0.1, 0.08)), (0.4, (0.22, 0.19, 0.15)), (0.7, (0.3, 0.26, 0.2)), (1.0, (0.16, 0.13, 0.1))]
        rough_base = 0.85
    hh = nb.add(hh, nb.mul(en, 0.0015))
    col = nb.ramp(b['id'], pal, 'LINEAR')
    col = nb.cmul(col, nb.ramp(nb.noise(P, 6.0, 4), [(0.3, (0.82, 0.82, 0.82)), (0.7, (1.12, 1.1, 1.08))]))
    # grime at the tucked (upper) part and in gaps, lichen spots
    shade = nb.mul(nb.smooth(t, 0.55, 1.0), 0.5)
    col = nb.mix(shade, col, nb.cmul(col, (0.55, 0.52, 0.5)))
    lich = nb.voronoi(P, 18.0, 'F1', 'Distance', 1.0, '3D')
    lmask = nb.mul(nb.inv(nb.smooth(lich, 0.12, 0.2)), nb.smooth(nb.noise(P, 1.2, 3), 0.5, 0.62))
    lcol = nb.mix(nb.noise(P, 9.0), (0.55, 0.52, 0.32), (0.75, 0.72, 0.6))
    col = nb.mix(nb.mul(lmask, 0.85), col, lcol)
    gap = nb.inv(side)
    col = nb.mix(gap, col, (0.03, 0.025, 0.02))
    return dict(color=col, rough=nb.add(rough_base, nb.mul(en, 0.15)), height=hh,
                cavity=nb.clamp01(nb.add(gap, nb.mul(shade, 0.6))))


def s_thatch(nb, co):
    u, v, P = co.u, co.v, co.P
    hcourse = 0.32
    t = nb.div(nb.math('FRACT', nb.div(v, hcourse)), 1.0)
    s1 = nb.noise(nb.comb(nb.mul(u, 70.0), nb.mul(v, 2.5), 0.0), 1.0, 4, 0.7)
    s2 = nb.noise(nb.comb(nb.mul(u, 23.0), nb.mul(v, 1.2), 3.0), 1.0, 3, 0.6)
    fib = nb.add(nb.mul(s1, 0.7), nb.mul(s2, 0.3))
    hh = nb.add(nb.mul(nb.inv(t), 0.05), nb.mul(fib, 0.035))
    hh = nb.add(hh, nb.mul(nb.noise(P, 0.8, 3), 0.06))
    col = nb.ramp(fib, [(0.25, (0.09, 0.07, 0.045)), (0.5, (0.27, 0.2, 0.1)), (0.7, (0.42, 0.33, 0.17)),
                        (0.85, (0.5, 0.42, 0.25))])
    age = nb.smooth(nb.noise(P, 0.9, 4, 0.6), 0.45, 0.7)
    col = nb.mix(nb.mul(age, 0.7), col, nb.cmul(col, (0.62, 0.6, 0.58)))
    return dict(color=col, rough=0.95, height=hh, cavity=nb.mul(nb.inv(fib), 0.6))


def s_canvas(nb, co, a=(0.6, 0.06, 0.04), b=(0.85, 0.8, 0.68), stripe=0.3, dirt=1.0):
    u, v, P = co.u, co.v, co.P
    st = nb.math('GREATER_THAN', nb.math('FRACT', nb.div(u, stripe)), 0.5) if stripe else 0.0
    col = nb.mix(st, a, b) if stripe else nb.rgb(a)
    weave = nb.mul(nb.math('SINE', nb.mul(u, 900.0)), nb.math('SINE', nb.mul(v, 900.0)))
    fade = nb.noise(P, 1.5, 4, 0.6)
    col = nb.hsv(col, 0.5, nb.maprange(fade, 0.3, 0.7, 0.7, 1.05), nb.maprange(fade, 0.3, 0.7, 0.9, 1.06))
    stain = nb.voronoi(nb.vadd(P, (2, 2, 2)), 2.5, 'F1', 'Distance', 1.0, '3D')
    ring = nb.mul(nb.mul(nb.smooth(stain, 0.18, 0.2), nb.inv(nb.smooth(stain, 0.2, 0.24))), 0.6)
    dm = nb.mul(nb.add(nb.mul(nb.smooth(nb.noise(P, 2.0, 4), 0.55, 0.75), 0.6), ring), dirt)
    col = nb.mix(nb.mul(dm, 0.55), col, nb.cmul(col, (0.55, 0.5, 0.42)))
    return dict(color=col, rough=0.85, height=nb.mul(weave, 0.0003), cavity=0.0,
                micro=nb.add(nb.mul(weave, 0.00025), nb.mul(nb.noise(P, 8.0, 3), 0.0015)))


def s_cloth(nb, co, color=(0.5, 0.1, 0.08), weave=600.0):
    u, v, P = co.u, co.v, co.P
    w = nb.mul(nb.math('SINE', nb.mul(u, weave)), nb.math('SINE', nb.mul(v, weave)))
    n = nb.noise(P, 3.0, 4, 0.6)
    col = nb.hsv(color, 0.5, nb.maprange(n, 0.3, 0.7, 0.85, 1.05), nb.maprange(n, 0.3, 0.7, 0.85, 1.08))
    return dict(color=col, rough=0.8, height=0.0, cavity=0.0, micro=nb.mul(w, 0.0002))


def s_velvet(nb, co, color=(0.28, 0.01, 0.02)):
    P = co.P
    n = nb.noise(P, 6.0, 5, 0.65)
    col = nb.cmul(nb.rgb(color), nb.ramp(n, [(0.3, (0.75, 0.75, 0.75)), (0.7, (1.2, 1.2, 1.2))]))
    return dict(color=col, rough=0.8, height=0.0, cavity=0.0, micro=nb.mul(n, 0.0008))


def s_carpet(nb, co, width=2.6, field=(0.2, 0.004, 0.01), border=(0.75, 0.5, 0.12), edge=(0.1, 0.0, 0.01)):
    u, v, P = co.u, co.v, co.P
    d = nb.mn(v, nb.sub(width, v))
    outer = nb.inv(nb.smooth(d, 0.06, 0.07))
    band = nb.mul(nb.smooth(d, 0.1, 0.11), nb.inv(nb.smooth(d, 0.26, 0.27)))
    motif = nb.math('GREATER_THAN', nb.math('SINE', nb.add(nb.mul(u, 18.0), nb.mul(nb.math('SINE', nb.mul(d, 30.0)), 2.0))), 0.3)
    bandcol = nb.mix(motif, border, nb.cmul(nb.rgb(border), (0.5, 0.25, 0.1)))
    dam = nb.wave(nb.comb(u, v, 0), 2.0, 4.0, 2.0, 1.0, 'RINGS', 'SPHERICAL')
    fcol = nb.mix(nb.mul(nb.smooth(dam, 0.4, 0.6), 0.25), field, nb.cmul(nb.rgb(field), (1.35, 0.9, 0.9)))
    col = nb.mix(band, fcol, bandcol)
    col = nb.mix(outer, col, edge)
    pile = nb.noise(P, 120.0, 2, 0.5)
    mid = nb.inv(nb.smooth(nb.math('ABSOLUTE', nb.sub(v, width / 2)), 0.2, width / 2 - 0.2))
    worn = nb.mul(nb.mul(mid, nb.smooth(nb.noise(P, 0.6, 3), 0.35, 0.7)), 0.5)
    col = nb.mix(worn, col, nb.cmul(col, (1.25, 1.1, 1.05)))
    col = nb.cmul(col, nb.ramp(pile, [(0.3, (0.85, 0.85, 0.85)), (0.7, (1.1, 1.1, 1.1))]))
    return dict(color=col, rough=0.9, height=0.0, cavity=0.0, micro=nb.mul(pile, 0.0008), worn=worn)


def _marble_vein(nb, P, scale=1.2, distort=6.0):
    vein = nb.wave(P, scale, distort, 6.0, 2.0, 'BANDS', 'DIAGONAL', 'SIN')
    return nb.inv(nb.smooth(nb.math('ABSOLUTE', nb.sub(vein, 0.5)), 0.0, 0.08))


def s_marble_floor(nb, co, tile=0.9, a=(0.72, 0.68, 0.6), b=(0.035, 0.034, 0.038)):
    P = co.P
    px, py, pz = nb.sep(P)
    cx = nb.math('FLOOR', nb.div(px, tile))
    cy = nb.math('FLOOR', nb.div(py, tile))
    chk = nb.math('FLOORED_MODULO', nb.add(cx, cy), 2.0)
    tid = nb.white(nb.comb(cx, cy, 1.0), 'Color')
    tr, tg, tb = nb.sep(tid)
    lx = nb.mul(nb.math('FRACT', nb.div(px, tile)), tile)
    ly = nb.mul(nb.math('FRACT', nb.div(py, tile)), tile)
    e = nb.mn(nb.mn(lx, nb.sub(tile, lx)), nb.mn(ly, nb.sub(tile, ly)))
    grout = nb.inv(nb.smooth(e, 0.0015, 0.004))
    vein = _marble_vein(nb, nb.vadd(P, nb.vscale(tid, 10.0)), 1.1, 7.0)
    cloud = nb.noise(nb.vadd(P, nb.vscale(tid, 5.0)), 2.0, 6, 0.6)
    ca = nb.mix(nb.mul(vein, 0.7), nb.cmul(nb.rgb(a), nb.ramp(cloud, [(0.3, (0.9, 0.9, 0.9)), (0.7, (1.08, 1.06, 1.04))])), (0.35, 0.33, 0.3))
    cb = nb.mix(nb.mul(vein, 0.35), nb.cmul(nb.rgb(b), nb.ramp(cloud, [(0.3, (0.7, 0.7, 0.7)), (0.7, (1.3, 1.2, 1.2))])), (0.45, 0.3, 0.25))
    col = nb.mix(chk, ca, cb)
    col = nb.mix(grout, col, (0.08, 0.07, 0.06))
    scuff = nb.noise(nb.comb(nb.mul(px, 30.0), nb.mul(py, 3.0), 0), 1.0, 3, 0.6)
    path = nb.inv(nb.smooth(nb.math('ABSOLUTE', px), 0.6, 2.2))
    rough = nb.add(0.06, nb.mul(nb.smooth(scuff, 0.5, 0.8), 0.12))
    rough = nb.add(rough, nb.mul(path, nb.mul(nb.noise(P, 1.5, 3), 0.18)))
    tilt = nb.add(nb.mul(nb.sub(tr, 0.5), nb.mul(lx, 0.003)), nb.mul(nb.sub(tg, 0.5), nb.mul(ly, 0.003)))
    hh = nb.sub(tilt, nb.mul(grout, 0.002))
    return dict(color=col, rough=nb.mixf(grout, rough, 0.8), height=hh, cavity=nb.mul(grout, 0.5))


def s_marble(nb, co, a=(0.78, 0.75, 0.7), vein_col=(0.4, 0.38, 0.36), rough=0.18):
    P = co.P
    vein = _marble_vein(nb, P, 0.9, 6.0)
    cloud = nb.noise(P, 1.8, 6, 0.6)
    col = nb.mix(nb.mul(vein, 0.6), nb.cmul(nb.rgb(a), nb.ramp(cloud, [(0.3, (0.9, 0.9, 0.9)), (0.7, (1.06, 1.05, 1.03))])), vein_col)
    return dict(color=col, rough=nb.add(rough, nb.mul(nb.noise(P, 12.0), 0.1)), height=nb.mul(cloud, 0.0004), cavity=0.0)


def s_mud(nb, co, wet=0.7):
    P = co.P
    n1 = nb.noise(P, 0.8, 5, 0.6)
    n2 = nb.noise(P, 7.0, 4, 0.6)
    peb = nb.voronoi(P, 30.0, 'F1', 'Distance', 1.0, '3D')
    pm = nb.mul(nb.inv(nb.smooth(peb, 0.1, 0.2)), nb.smooth(nb.noise(P, 3.0), 0.55, 0.7))
    hh = nb.add(nb.add(nb.mul(n1, 0.05), nb.mul(n2, 0.01)), nb.mul(pm, 0.004))
    pud = nb.mul(nb.smooth(nb.sub(0.022, hh), -0.003, 0.004), wet)
    hh = nb.mx(hh, nb.mul(wet, 0.022))
    col = nb.ramp(n2, [(0.25, (0.05, 0.035, 0.022)), (0.6, (0.11, 0.075, 0.045)), (0.85, (0.17, 0.13, 0.09))])
    col = nb.mix(pm, col, (0.25, 0.23, 0.2))
    col = nb.mix(pud, col, nb.cmul(col, (0.5, 0.5, 0.52)))
    rough = nb.mixf(pud, nb.add(0.55, nb.mul(n2, 0.35)), 0.04)
    return dict(color=col, rough=rough, height=hh, cavity=nb.mul(nb.inv(n2), 0.3))


def s_pebbles(nb, co, scale=14.0):
    P = co.P
    px, py, pz = nb.sep(P)
    c = nb.comb(px, py, nb.mul(pz, 0.3))
    d, ccol = nb.voronoi(c, scale, 'SMOOTH_F1', ['Distance', 'Color'], 1.0, '3D', 0.15)
    ed = nb.voronoi(c, scale, 'DISTANCE_TO_EDGE', 'Distance', 1.0, '3D')
    dome = nb.math('POWER', nb.smooth(ed, 0.0, 0.035), 0.5)
    cr, cg, cb = nb.sep(ccol)
    hh = nb.add(nb.mul(dome, nb.add(0.012, nb.mul(cg, 0.012))), nb.mul(nb.noise(P, 1.0, 3), 0.04))
    pal = [(0.0, (0.16, 0.155, 0.15)), (0.2, (0.38, 0.36, 0.33)), (0.4, (0.25, 0.21, 0.16)),
           (0.6, (0.5, 0.48, 0.45)), (0.8, (0.2, 0.2, 0.22)), (1.0, (0.33, 0.27, 0.2))]
    col = nb.ramp(cr, pal, 'CONSTANT')
    col = nb.cmul(col, nb.ramp(nb.noise(P, 25.0), [(0.3, (0.8, 0.8, 0.8)), (0.7, (1.15, 1.15, 1.15))]))
    gap = nb.inv(nb.smooth(ed, 0.002, 0.012))
    col = nb.mix(gap, col, (0.08, 0.065, 0.045))
    return dict(color=col, rough=nb.mixf(dome, 0.8, 0.5), height=hh, cavity=gap)


def s_grass(nb, co):
    P = co.P
    n1 = nb.noise(P, 1.2, 5, 0.6)
    n2 = nb.noise(P, 40.0, 3, 0.7)
    col = nb.ramp(n1, [(0.2, (0.035, 0.08, 0.012)), (0.45, (0.07, 0.15, 0.02)), (0.65, (0.13, 0.2, 0.035)),
                       (0.85, (0.24, 0.24, 0.07))])
    col = nb.cmul(col, nb.ramp(n2, [(0.2, (0.6, 0.6, 0.6)), (0.8, (1.3, 1.3, 1.2))]))
    bare = nb.smooth(nb.noise(nb.vadd(P, (5, 5, 5)), 0.7, 4, 0.6), 0.62, 0.7)
    col = nb.mix(bare, col, (0.12, 0.085, 0.05))
    hh = nb.add(nb.mul(n2, 0.01), nb.mul(n1, 0.03))
    return dict(color=col, rough=0.9, height=hh, cavity=nb.mul(nb.inv(n2), 0.3))


def s_moss(nb, co):
    P = co.P
    n1 = nb.noise(P, 3.0, 6, 0.65)
    n2 = nb.noise(P, 60.0, 3, 0.7)
    col = nb.ramp(n1, [(0.25, (0.02, 0.05, 0.008)), (0.55, (0.06, 0.12, 0.015)), (0.8, (0.18, 0.22, 0.04))])
    col = nb.cmul(col, nb.ramp(n2, [(0.2, (0.6, 0.6, 0.6)), (0.8, (1.3, 1.3, 1.2))]))
    return dict(color=col, rough=0.95, height=nb.add(nb.mul(n1, 0.02), nb.mul(n2, 0.004)), cavity=0.0)


def s_rock(nb, co, color=(0.27, 0.25, 0.22)):
    P = co.P
    px, py, pz = nb.sep(P)
    strata = nb.wave(P, 1.4, 5.0, 4.0, 1.5, 'BANDS', 'Z', 'SIN')
    n1 = nb.noise(P, 2.5, 6, 0.65)
    n2 = nb.noise(P, 18.0, 4, 0.6)
    ced = nb.voronoi(nb.vadd(P, nb.vscale(nb.noise(P, 2.0, out='Color'), 0.3)), 2.2, 'DISTANCE_TO_EDGE', 'Distance')
    crack = nb.inv(nb.smooth(ced, 0.0, 0.012))
    col = nb.cmul(nb.rgb(color), nb.ramp(nb.add(nb.mul(strata, 0.4), nb.mul(n1, 0.6)),
                                         [(0.25, (0.6, 0.6, 0.62)), (0.5, (1.0, 0.95, 0.9)), (0.75, (1.3, 1.22, 1.1))]))
    lich = nb.mul(nb.inv(nb.smooth(nb.voronoi(P, 9.0), 0.15, 0.3)), nb.smooth(nb.noise(P, 1.0, 3), 0.5, 0.6))
    col = nb.mix(nb.mul(lich, 0.8), col, nb.mix(n2, (0.55, 0.53, 0.35), (0.7, 0.68, 0.58)))
    col = nb.mix(crack, col, nb.cmul(col, (0.3, 0.3, 0.3)))
    hh = nb.add(nb.add(nb.mul(n1, 0.03), nb.mul(n2, 0.006)), nb.mul(crack, -0.01))
    return dict(color=col, rough=nb.add(0.72, nb.mul(n2, 0.2)), height=hh, cavity=nb.mul(crack, 0.8))


def s_hay(nb, co):
    u, v, P = co.u, co.v, co.P
    f1 = nb.noise(nb.comb(nb.mul(u, 3.0), nb.mul(v, 90.0), nb.mul(co.isl, 5.0)), 1.0, 4, 0.7)
    f2 = nb.noise(nb.vscale(P, 1.0), 25.0, 3, 0.6)
    fib = nb.add(nb.mul(f1, 0.7), nb.mul(f2, 0.3))
    col = nb.ramp(fib, [(0.25, (0.16, 0.11, 0.04)), (0.5, (0.45, 0.33, 0.12)), (0.75, (0.68, 0.55, 0.25)), (0.9, (0.8, 0.7, 0.4))])
    return dict(color=col, rough=0.85, height=nb.mul(fib, 0.01), cavity=nb.mul(nb.inv(fib), 0.4))


def s_paint(nb, co, color=(0.05, 0.22, 0.14), chips=1.0):
    pl = s_planks(nb, co, board=0.14, length=3.0, check=0.4, nails=0.0)
    P = co.P
    n = nb.noise(P, 5.0, 5, 0.65)
    chip = nb.mul(nb.smooth(nb.add(n, nb.mul(pl['cavity'], 0.3)), 0.64, 0.68), chips)
    fade = nb.noise(P, 1.2, 3)
    pcol = nb.hsv(color, 0.5, nb.maprange(fade, 0.3, 0.7, 0.8, 1.05), nb.maprange(fade, 0.3, 0.7, 0.85, 1.12))
    col = nb.mix(chip, nb.mix(nb.mul(pl['cavity'], 0.6), pcol, nb.cmul(pcol, (0.4, 0.4, 0.4))), pl['color'])
    rough = nb.mixf(chip, 0.55, pl['rough'])
    return dict(color=col, rough=rough, height=nb.add(pl['height'], nb.mul(nb.inv(chip), 0.0006)), cavity=pl['cavity'])


def s_rope(nb, co):
    u, v, P = co.u, co.v, co.P
    tw = nb.math('SINE', nb.add(nb.mul(u, 160.0), nb.mul(v, 300.0)))
    col = nb.mix(nb.mul(nb.add(tw, 1.0), 0.5), (0.16, 0.12, 0.07), (0.42, 0.34, 0.2))
    return dict(color=col, rough=0.9, height=nb.mul(tw, 0.0015), cavity=0.0)


def s_simple(nb, co, color=(0.5, 0.5, 0.5), rough=0.5, noise_amt=0.15, nscale=6.0, metal=0.0, bump=0.0005):
    P = co.P
    n = nb.noise(P, nscale, 4, 0.6)
    col = nb.cmul(nb.rgb(color), nb.ramp(n, [(0.2, (1 - noise_amt,) * 3), (0.8, (1 + noise_amt,) * 3)]))
    return dict(color=col, rough=nb.add(rough, nb.mul(nb.sub(n, 0.5), 0.1)), height=nb.mul(n, bump), cavity=0.0, metal=metal)


def s_fruit(nb, co, a=(0.5, 0.03, 0.02), b=(0.6, 0.35, 0.05), speck=1.0, rough=0.35):
    P = co.P
    n = nb.noise(P, 8.0, 4, 0.6)
    col = nb.mix(nb.smooth(n, 0.35, 0.7), a, b)
    sp = nb.mul(nb.smooth(nb.noise(P, 120.0), 0.68, 0.72), speck)
    col = nb.mix(nb.mul(sp, 0.6), col, (0.8, 0.7, 0.3))
    return dict(color=col, rough=nb.add(rough, nb.mul(n, 0.15)), height=nb.mul(n, 0.0004), cavity=0.0)


def s_leaf(nb, co, a=(0.03, 0.12, 0.02), b=(0.12, 0.25, 0.04)):
    P = co.P
    n = nb.noise(P, 20.0, 3, 0.6)
    vein = nb.inv(nb.smooth(nb.voronoi(P, 30.0, 'DISTANCE_TO_EDGE'), 0.0, 0.01))
    col = nb.mix(n, a, b)
    col = nb.mix(nb.mul(vein, 0.5), col, nb.cmul(nb.rgb(b), (1.6, 1.5, 1.2)))
    return dict(color=col, rough=0.55, height=nb.mul(vein, 0.0005), cavity=0.0)


def s_bread(nb, co):
    P = co.P
    n = nb.noise(P, 10.0, 4, 0.6)
    crack = nb.inv(nb.smooth(nb.voronoi(P, 12.0, 'DISTANCE_TO_EDGE'), 0.0, 0.02))
    col = nb.ramp(n, [(0.3, (0.3, 0.13, 0.04)), (0.7, (0.5, 0.25, 0.07))])
    col = nb.mix(crack, col, (0.7, 0.55, 0.32))
    flour = nb.smooth(nb.noise(P, 3.0), 0.6, 0.75)
    col = nb.mix(nb.mul(flour, 0.6), col, (0.8, 0.75, 0.65))
    return dict(color=col, rough=0.75, height=nb.mul(crack, -0.002), cavity=0.0)


def s_dirt(nb, co):
    P = co.P
    n1 = nb.noise(P, 1.5, 5, 0.6)
    n2 = nb.noise(P, 15.0, 4, 0.6)
    st = nb.mul(nb.inv(nb.smooth(nb.voronoi(P, 25.0), 0.1, 0.18)), nb.smooth(nb.noise(P, 4.0), 0.5, 0.6))
    col = nb.ramp(nb.add(nb.mul(n1, 0.6), nb.mul(n2, 0.4)), [(0.3, (0.08, 0.06, 0.04)), (0.6, (0.16, 0.12, 0.08)), (0.85, (0.24, 0.19, 0.13))])
    col = nb.mix(st, col, (0.3, 0.28, 0.25))
    return dict(color=col, rough=0.9, height=nb.add(nb.mul(n1, 0.02), nb.mul(st, 0.006)), cavity=0.0)


def s_parchment(nb, co, color=(0.78, 0.68, 0.48)):
    P = co.P
    n = nb.noise(P, 6.0, 5, 0.6)
    col = nb.cmul(nb.rgb(color), nb.ramp(n, [(0.3, (0.8, 0.75, 0.68)), (0.7, (1.05, 1.03, 1.0))]))
    return dict(color=col, rough=0.85, height=nb.mul(n, 0.0005), cavity=0.0)


def s_wax(nb, co):
    return s_simple(nb, co, (0.8, 0.74, 0.6), 0.45, 0.06, 20.0)


def s_riverbank(nb, co, water_z=-1.8):
    """Terrain blend by height (metres, object Z): pebbles/mud under and at the waterline, mud on the
    slopes, grass on top."""
    P = co.P
    px, py, pz = nb.sep(nb.vscale(nb.texco('Object'), 1.0 / M))
    g = s_grass(nb, co)
    m = s_mud(nb, co, 0.6)
    pb = s_pebbles(nb, co, 12.0)
    n = nb.noise(P, 0.7, 4, 0.6)
    nz = nb.sep(nb.geo('Normal'))[2]
    hrel = nb.sub(pz, water_z)
    peb = nb.inv(nb.smooth(nb.add(hrel, nb.mul(nb.sub(n, 0.5), 0.8)), 0.15, 0.55))
    grass = nb.mul(nb.smooth(nb.add(hrel, nb.mul(nb.sub(n, 0.5), 1.0)), 1.1, 1.6), nb.smooth(nz, 0.75, 0.9))
    col = nb.mix(peb, m['color'], pb['color'])
    col = nb.mix(grass, col, g['color'])
    rough = nb.mixf(peb, m['rough'], pb['rough'])
    rough = nb.mixf(grass, rough, g['rough'])
    h = nb.mixf(peb, m['height'], pb['height'])
    h = nb.mixf(grass, h, nb.mul(g['height'], 0.6))
    wet = nb.inv(nb.smooth(hrel, 0.0, 0.35))
    col = nb.mix(nb.mul(wet, 0.6), col, nb.cmul(col, (0.55, 0.55, 0.55)))
    rough = nb.mixf(wet, rough, nb.mul(rough, 0.4))
    cav = nb.mixf(peb, m['cavity'], pb['cavity'])
    return dict(color=col, rough=rough, height=h, cavity=cav)


def s_bark(nb, co):
    u, v, P = co.u, co.v, co.P
    f = nb.noise(nb.comb(nb.mul(co.ur, 1.5), nb.mul(co.vr, 14.0), 0.0), 1.0, 5, 0.65)
    ridges = nb.voronoi(nb.comb(nb.mul(co.ur, 0.8), nb.mul(co.vr, 6.0), 0.0), 3.0, 'DISTANCE_TO_EDGE', 'Distance', 1.0, '2D')
    r = nb.smooth(ridges, 0.0, 0.08)
    col = nb.ramp(nb.add(nb.mul(f, 0.5), nb.mul(r, 0.5)), [(0.2, (0.03, 0.025, 0.02)), (0.6, (0.12, 0.1, 0.08)), (0.9, (0.22, 0.2, 0.17))])
    return dict(color=col, rough=0.9, height=nb.add(nb.mul(r, 0.012), nb.mul(f, 0.004)), cavity=nb.mul(nb.inv(r), 0.6))


# ----------------------------------------------------------------------------------------------
# Registry.  name: dict(fn, args, disp, wear, keys (CC0 folder keywords), tile (m), shader extras)
# ----------------------------------------------------------------------------------------------
W_STONE = dict(edge=0.5, edge_color=(0.55, 0.52, 0.47), grime=0.7, moss=0.6, damp=0.8, streaks=0.6)
W_WOOD = dict(edge=0.45, edge_color=(0.32, 0.28, 0.24), grime=0.6, moss=0.25, damp=0.6, streaks=0.3)
W_PLASTER = dict(edge=0.35, edge_color=(0.82, 0.78, 0.7), grime=0.6, moss=0.15, damp=0.9, streaks=0.9)
W_GROUND = dict(edge=0.0, grime=0.5, moss=0.0, damp=0.0, streaks=0.0)
W_METAL = dict(edge=0.4, edge_color=(0.35, 0.33, 0.3), grime=0.6, moss=0.0, damp=0.2, streaks=0.2)
W_CLEAN = dict(edge=0.0, grime=0.35, moss=0.0, damp=0.0, streaks=0.0)
W_ROOF = dict(edge=0.2, edge_color=(0.6, 0.4, 0.3), grime=0.6, moss=0.9, damp=0.0, streaks=0.4)

REG = {}


def reg(name, fn, disp=False, wear=W_CLEAN, keys=(), tile=2.0, gz=0.0, **kw):
    sh = {k: kw.pop(k) for k in list(kw) if k.startswith('sh_')}
    REG[name] = dict(fn=fn, args=kw, disp=disp, wear=wear, keys=keys, tile=tile, sh=sh, gz=gz)


# ground
reg('Cobbles', s_cobbles, True, W_GROUND, ('cobble', 'cobblestone', 'paving_stones', 'pavingstones'), 2.0, scale=8.5)
reg('Cobbles Dry', s_cobbles, True, W_GROUND, (), 2.0, scale=8.5, puddles=0.0, moss=0.6)
reg('Flagstones', s_flagstones, True, W_GROUND, ('flagstone', 'stone_floor', 'paving'), 3.0)
reg('Flagstones Hall', s_flagstones, True, W_GROUND, (), 3.0, w=0.9, h=0.6, color=(0.42, 0.4, 0.37), puddles=0.0)
reg('Mud', s_mud, True, W_GROUND, ('mud', 'ground_mud'), 3.0)
reg('Pebbles', s_pebbles, True, dict(W_GROUND, damp=0.0), ('pebble', 'gravel', 'river_pebbles'), 2.0)
reg('Grass', s_grass, False, W_GROUND, ('grass', 'ground_grass', 'forrest_ground', 'forest_ground'), 3.0)
reg('Moss', s_moss, True, W_GROUND, ('moss',), 2.0)
reg('Dirt', s_dirt, True, W_GROUND, ('dirt', 'ground', 'soil'), 3.0)
reg('Forest Floor', s_dirt, True, W_GROUND, ('forest_floor', 'leaf_litter'), 3.0)
reg('Rock', s_rock, False, dict(W_STONE, edge=0.3, streaks=0.2), ('rock', 'cliff', 'boulder'), 3.0)
# masonry
reg('Ashlar', s_ashlar, False, W_STONE, ('ashlar', 'castle_wall', 'stone_wall', 'stone_block'), 3.0)
reg('Ashlar Grey', s_ashlar, False, W_STONE, ('castle_brick', 'stone_bricks'), 3.0, color=(0.3, 0.3, 0.29), mortar_col=(0.36, 0.35, 0.33))
reg('Ashlar Hall', s_ashlar, False, dict(W_STONE, moss=0.0, damp=0.2, streaks=0.15), (), 3.0, w=1.1, h=0.55,
    color=(0.5, 0.44, 0.35), mortar=0.005, mortar_col=(0.42, 0.38, 0.32), relief=0.004, var=0.1, rough_hewn=0.2)
reg('Stone Drums', s_ashlar, False, dict(W_STONE, moss=0.0, damp=0.1, streaks=0.1), (), 3.0, w=6.0, h=1.15,
    color=(0.58, 0.52, 0.42), mortar=0.004, mortar_col=(0.45, 0.41, 0.35), relief=0.003, var=0.06, rough_hewn=0.15, wvar=0.0)
reg('Plaster Hall', s_plaster, False, dict(W_PLASTER, streaks=0.3, moss=0.0, damp=0.0), (), 3.0, color=(0.7, 0.62, 0.5), cracks=0.4, damage=0.0)
reg('Ashlar Bridge', s_ashlar, False, dict(W_STONE, moss=1.0, damp=1.0, streaks=0.8), (), 3.0, gz=-1.6,
    color=(0.3, 0.3, 0.29), mortar_col=(0.36, 0.35, 0.33))
reg('Rubble', s_rubble, False, W_STONE, ('rubble', 'fieldstone', 'stone_wall_rough', 'castle_wall_slates'), 3.0)
reg('Brick', s_brick, False, W_STONE, ('brick', 'red_brick', 'bricks'), 2.0)
reg('Limestone', s_ashlar, False, W_STONE, ('limestone',), 3.0, w=0.5, h=0.25, color=(0.62, 0.57, 0.47),
    mortar_col=(0.55, 0.52, 0.47), relief=0.004, var=0.1, rough_hewn=0.3)
# plaster
reg('Plaster Cream', s_plaster, False, W_PLASTER, ('plaster', 'plastered_wall', 'painted_plaster'), 3.0, color=(0.74, 0.67, 0.52))
reg('Plaster Ochre', s_plaster, False, W_PLASTER, (), 3.0, color=(0.7, 0.45, 0.17))
reg('Plaster Rose', s_plaster, False, W_PLASTER, (), 3.0, color=(0.66, 0.33, 0.24))
reg('Plaster White', s_plaster, False, W_PLASTER, (), 3.0, color=(0.8, 0.78, 0.72))
reg('Plaster Sage', s_plaster, False, W_PLASTER, (), 3.0, color=(0.42, 0.5, 0.36))
reg('Plaster Blue', s_plaster, False, W_PLASTER, (), 3.0, color=(0.35, 0.47, 0.6))
# wood
reg('Timber Dark', s_timber, False, W_WOOD, ('dark_oak', 'oak_beam', 'timber', 'beam', 'dark_wood', 'old_wood'), 2.0)
reg('Timber Oak', s_timber, False, W_WOOD, ('wood', 'oak'), 2.0, dark=(0.1, 0.06, 0.035), mid=(0.22, 0.14, 0.08), light=(0.34, 0.26, 0.18))
reg('Planks', s_planks, False, W_WOOD, ('planks', 'wood_planks', 'wooden_planks', 'wood_floor', 'floor_boards', 'floorboards'), 2.0)
reg('Planks Pale', s_planks, False, W_WOOD, ('pine', 'wood_plank'), 2.0, dark=(0.18, 0.12, 0.06), mid=(0.36, 0.25, 0.14), light=(0.5, 0.4, 0.27))
reg('Planks Grey', s_planks, False, W_WOOD, ('weathered_wood', 'old_planks'), 2.0, dark=(0.07, 0.065, 0.06), mid=(0.17, 0.16, 0.14), light=(0.3, 0.28, 0.25))
reg('Paint Green', s_paint, False, W_WOOD, (), 2.0, color=(0.03, 0.2, 0.12))
reg('Paint Red', s_paint, False, W_WOOD, (), 2.0, color=(0.32, 0.03, 0.025))
reg('Paint Blue', s_paint, False, W_WOOD, (), 2.0, color=(0.03, 0.1, 0.3))
reg('Paint Yellow', s_paint, False, W_WOOD, (), 2.0, color=(0.6, 0.38, 0.05))
# roofs
reg('Roof Clay', s_roof_tiles, True, W_ROOF, ('roof_tiles', 'clay_roof', 'rooftiles', 'roof_clay'), 2.0, kind='clay')
reg('Roof Clay Old', s_roof_tiles, True, W_ROOF, (), 2.0, kind='clay',
    pal=[(0.0, (0.25, 0.1, 0.05)), (0.3, (0.38, 0.16, 0.08)), (0.6, (0.45, 0.24, 0.13)), (1.0, (0.3, 0.17, 0.1))])
reg('Roof Slate', s_roof_tiles, True, W_ROOF, ('slate', 'roof_slates', 'roofing_slate'), 2.0, kind='slate')
reg('Roof Shingle', s_roof_tiles, True, W_ROOF, ('shingle', 'wood_shingle'), 2.0, kind='shingle', w=0.16, h=0.12)
reg('Thatch', s_thatch, True, dict(W_ROOF, moss=0.7), ('thatch', 'straw_roof'), 3.0)
# metals
reg('Iron', s_iron, False, W_METAL, ('rust', 'rusty_metal', 'metal_rust', 'corrugated'), 1.0)
reg('Iron Black', s_iron, False, W_METAL, ('wrought_iron', 'metal_plate'), 1.0, rust=0.15)
reg('Brass', s_metal, False, W_METAL, ('brass',), 1.0)
reg('Gold', s_metal, False, dict(W_METAL, edge=0.0, grime=0.3), ('gold',), 1.0, color=(1.0, 0.7, 0.28), rough=0.2, tamount=0.15)
reg('Steel', s_metal, False, W_METAL, ('metal', 'steel'), 1.0, color=(0.62, 0.62, 0.64), rough=0.25, tarnish=(0.25, 0.24, 0.22), tamount=0.3)
reg('Copper Verdigris', s_verdigris, False, W_METAL, ('copper', 'patina'), 1.0)
# fabric
reg('Canvas Red', s_canvas, False, W_CLEAN, (), 1.0, a=(0.55, 0.04, 0.03), sh_translucent=0.3)
reg('Canvas Blue', s_canvas, False, W_CLEAN, (), 1.0, a=(0.04, 0.12, 0.42), sh_translucent=0.3)
reg('Canvas Green', s_canvas, False, W_CLEAN, (), 1.0, a=(0.03, 0.25, 0.1), sh_translucent=0.3)
reg('Canvas Yellow', s_canvas, False, W_CLEAN, (), 1.0, a=(0.75, 0.42, 0.03), b=(0.5, 0.05, 0.03), sh_translucent=0.3)
reg('Canvas Plain', s_canvas, False, W_CLEAN, ('canvas', 'burlap', 'sackcloth', 'fabric', 'cloth'), 1.0, a=(0.62, 0.55, 0.42), stripe=0.0, sh_translucent=0.35)
reg('Cloth White', s_cloth, False, W_CLEAN, (), 1.0, color=(0.75, 0.73, 0.68), sh_translucent=0.35, sh_sheen=0.4)
reg('Cloth Blue', s_cloth, False, W_CLEAN, (), 1.0, color=(0.05, 0.15, 0.5), sh_translucent=0.3, sh_sheen=0.4)
reg('Cloth Red', s_cloth, False, W_CLEAN, (), 1.0, color=(0.6, 0.05, 0.04), sh_translucent=0.3, sh_sheen=0.4)
reg('Cloth Yellow', s_cloth, False, W_CLEAN, (), 1.0, color=(0.8, 0.55, 0.08), sh_translucent=0.3, sh_sheen=0.4)
reg('Cloth Green', s_cloth, False, W_CLEAN, (), 1.0, color=(0.06, 0.3, 0.1), sh_translucent=0.3, sh_sheen=0.4)
reg('Cloth Brown', s_cloth, False, W_CLEAN, (), 1.0, color=(0.2, 0.12, 0.06), sh_sheen=0.3)
reg('Velvet Red', s_velvet, False, W_CLEAN, ('velvet',), 1.0, sh_sheen=1.0)
reg('Velvet Blue', s_velvet, False, W_CLEAN, (), 1.0, color=(0.01, 0.03, 0.22), sh_sheen=1.0)
reg('Velvet Purple', s_velvet, False, W_CLEAN, (), 1.0, color=(0.12, 0.01, 0.18), sh_sheen=1.0)
reg('Carpet Royal', s_carpet, False, W_CLEAN, ('carpet', 'rug'), 2.6, sh_sheen=0.8)
reg('Rope', s_rope, False, W_CLEAN, ('rope',), 0.5)
reg('Parchment', s_parchment, False, W_CLEAN, ('paper', 'parchment'), 1.0)
# stone finishes
reg('Marble Floor', s_marble_floor, False, dict(W_CLEAN, grime=0.25), ('marble_floor', 'marble_tiles'), 1.8)
reg('Marble White', s_marble, False, dict(W_CLEAN, edge=0.2, edge_color=(0.85, 0.82, 0.78), grime=0.3), ('marble',), 2.0)
reg('Marble Dark', s_marble, False, dict(W_CLEAN, grime=0.3), (), 2.0, a=(0.06, 0.05, 0.05), vein_col=(0.4, 0.36, 0.3), rough=0.12)
# misc
reg('Hay', s_hay, False, dict(W_CLEAN, grime=0.4), ('hay', 'straw'), 1.0)
reg('Apple Red', s_fruit, False, W_CLEAN, (), 1.0)
reg('Apple Green', s_fruit, False, W_CLEAN, (), 1.0, a=(0.25, 0.4, 0.04), b=(0.5, 0.5, 0.05))
reg('Pumpkin', s_fruit, False, W_CLEAN, (), 1.0, a=(0.7, 0.18, 0.01), b=(0.55, 0.28, 0.02), speck=0.2, rough=0.5)
reg('Orange', s_fruit, False, W_CLEAN, (), 1.0, a=(0.8, 0.25, 0.01), b=(0.7, 0.35, 0.02), speck=0.0, rough=0.55)
reg('Cabbage', s_leaf, False, W_CLEAN, (), 1.0, a=(0.12, 0.3, 0.06), b=(0.3, 0.45, 0.12))
reg('Leaf', s_leaf, False, W_CLEAN, ('leaves', 'foliage'), 1.0, sh_translucent=0.4)
reg('Bread', s_bread, False, W_CLEAN, (), 1.0)
reg('Wax', s_wax, False, W_CLEAN, (), 1.0, sh_subsurface=0.3)
reg('Petal Red', s_simple, False, W_CLEAN, (), 1.0, color=(0.7, 0.03, 0.05), rough=0.6, sh_translucent=0.3)
reg('Petal Yellow', s_simple, False, W_CLEAN, (), 1.0, color=(0.9, 0.6, 0.03), rough=0.6, sh_translucent=0.3)
reg('Petal Purple', s_simple, False, W_CLEAN, (), 1.0, color=(0.3, 0.05, 0.5), rough=0.6, sh_translucent=0.3)
reg('Petal White', s_simple, False, W_CLEAN, (), 1.0, color=(0.85, 0.82, 0.75), rough=0.6, sh_translucent=0.3)
reg('Soil', s_dirt, False, W_CLEAN, (), 1.0)
reg('Feather Grey', s_simple, False, W_CLEAN, (), 1.0, color=(0.25, 0.26, 0.28), rough=0.7, sh_sheen=0.5)
reg('Leather', s_simple, False, W_WOOD, ('leather',), 1.0, color=(0.15, 0.07, 0.03), rough=0.55, noise_amt=0.25, nscale=20.0)
reg('Reed', s_leaf, False, W_CLEAN, (), 1.0, a=(0.1, 0.16, 0.03), b=(0.32, 0.3, 0.1), sh_translucent=0.4)
reg('Grass Blade', s_leaf, False, W_CLEAN, (), 1.0, a=(0.04, 0.13, 0.015), b=(0.14, 0.25, 0.04), sh_translucent=0.4)
reg('Cattail', s_simple, False, W_CLEAN, (), 1.0, color=(0.13, 0.06, 0.025), rough=0.9, noise_amt=0.2, nscale=30.0)
reg('Foam', s_simple, False, W_CLEAN, (), 1.0, color=(0.85, 0.88, 0.88), rough=0.45, noise_amt=0.15, nscale=40.0, sh_translucent=0.3)
reg('Riverbank', s_riverbank, True, dict(W_GROUND, grime=0.3), (), 3.0)
reg('Bark', s_bark, False, dict(W_WOOD, moss=0.5, damp=0.3, streaks=0.0), ('bark',), 2.0)
reg('Leaf Willow', s_leaf, False, W_CLEAN, (), 1.0, a=(0.06, 0.16, 0.02), b=(0.2, 0.3, 0.05), sh_translucent=0.45)
reg('Leaf Oak', s_leaf, False, W_CLEAN, (), 1.0, a=(0.025, 0.09, 0.012), b=(0.1, 0.2, 0.03), sh_translucent=0.45)
reg('Leaf Forest', s_leaf, False, W_CLEAN, (), 1.0, a=(0.012, 0.045, 0.01), b=(0.045, 0.1, 0.022), sh_translucent=0.35)
reg('Terracotta', s_simple, False, W_STONE, (), 1.0, color=(0.42, 0.15, 0.06), rough=0.75, noise_amt=0.25, nscale=9.0, bump=0.002)
reg('Charcoal', s_simple, False, W_CLEAN, (), 1.0, color=(0.02, 0.018, 0.016), rough=0.9, noise_amt=0.4, nscale=12.0, bump=0.004)

CUSTOM = {}   # name -> builder(mat) for special shaders (water, glass, flames ...)


# ----------------------------------------------------------------------------------------------
# Assembly
# ----------------------------------------------------------------------------------------------
SURF_OUT = [('Color', C), ('Roughness', F), ('Metallic', F), ('Normal', Vt), ('Height', F), ('Cavity', F)]


def _surface_group(name, spec):
    g, gi, go = _new_group('BLS ' + name, [], SURF_OUT)
    nb = NB(g)
    co = Co(nb)
    r = spec['fn'](nb, co, **spec['args'])
    nb.feed(go.inputs['Color'], r['color'])
    nb.feed(go.inputs['Roughness'], r['rough'])
    nb.feed(go.inputs['Metallic'], r.get('metal', 0.0))
    nb.feed(go.inputs['Height'], r.get('height', 0.0))
    nb.feed(go.inputs['Cavity'], r.get('cavity', 0.0))
    bh = r.get('micro', 0.0) if spec['disp'] else nb.add(r.get('height', 0.0), r.get('micro', 0.0))
    if isinstance(bh, (int, float)) and bh == 0.0:
        nb.L.new(nb.geo('Normal'), go.inputs['Normal'])
    else:
        nb.L.new(nb.bump(nb.mul(bh, M), 1.0, 1.0), go.inputs['Normal'])
    g['bl_kind'] = 'procedural'
    return g


def _fresh_material(full):
    mat = bpy.data.materials.get(full)
    if mat is None:
        mat = bpy.data.materials.new(full)
    try:
        mat.use_nodes = True
    except Exception:
        pass
    nt = mat.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    return mat


def build(name):
    """Create (or rebuild) material 'BL <name>' and return it."""
    if name in CUSTOM:
        mat = _fresh_material(PREFIX + name)
        CUSTOM[name](mat)
        mat['bl_lib'] = name
        return mat
    spec = REG[name]
    mat = _fresh_material(PREFIX + name)
    nb = NB(mat.node_tree)
    surf_tree = bpy.data.node_groups.get('BLS ' + name) or _surface_group(name, spec)
    surf = nb.group(surf_tree)
    surf.name = surf.label = 'SURF'
    wear = nb.group(wear_group())
    wear.name = wear.label = 'WEAR'
    w = spec['wear']
    for k, key in (('edge', 'Edge'), ('grime', 'Grime'), ('moss', 'Moss'), ('damp', 'Damp'), ('streaks', 'Streaks')):
        wear.inputs[key].default_value = w.get(k, 0.0)
    if 'edge_color' in w:
        wear.inputs['Edge Color'].default_value = (*w['edge_color'], 1)
    wear.inputs['Ground Z'].default_value = spec.get('gz', 0.0) * M
    nb.L.new(surf.outputs['Color'], wear.inputs['Color'])
    nb.L.new(surf.outputs['Roughness'], wear.inputs['Roughness'])
    nb.L.new(surf.outputs['Cavity'], wear.inputs['Cavity'])
    p = nb.node('ShaderNodeBsdfPrincipled')
    p.name = 'BSDF'
    nb.L.new(wear.outputs['Color'], p.inputs['Base Color'])
    nb.L.new(wear.outputs['Roughness'], p.inputs['Roughness'])
    nb.L.new(surf.outputs['Metallic'], p.inputs['Metallic'])
    nb.L.new(surf.outputs['Normal'], p.inputs['Normal'])
    sh = spec['sh']
    shader = p.outputs[0]
    if sh.get('sh_sheen'):
        p.inputs['Sheen Weight'].default_value = sh['sh_sheen']
        p.inputs['Sheen Roughness'].default_value = 0.35
    if sh.get('sh_subsurface'):
        p.inputs['Subsurface Weight'].default_value = sh['sh_subsurface']
        p.inputs['Subsurface Radius'].default_value = (0.3, 0.2, 0.1)
    if sh.get('sh_translucent'):
        tr = nb.node('ShaderNodeBsdfTranslucent')
        nb.L.new(wear.outputs['Color'], tr.inputs['Color'])
        nb.L.new(surf.outputs['Normal'], tr.inputs['Normal'])
        mx = nb.node('ShaderNodeMixShader')
        mx.inputs[0].default_value = sh['sh_translucent']
        nb.L.new(p.outputs[0], mx.inputs[1])
        nb.L.new(tr.outputs[0], mx.inputs[2])
        shader = mx.outputs[0]
    out = nb.node('ShaderNodeOutputMaterial')
    out.target = 'ALL'
    nb.L.new(shader, out.inputs['Surface'])
    if spec['disp']:
        d = nb.node('ShaderNodeDisplacement', space='OBJECT')
        d.inputs['Midlevel'].default_value = 0.0
        d.inputs['Scale'].default_value = M
        nb.L.new(surf.outputs['Height'], d.inputs['Height'])
        nb.L.new(d.outputs[0], out.inputs['Displacement'])
        mat.displacement_method = 'BOTH'
    else:
        mat.displacement_method = 'BUMP'
    mat['bl_lib'] = name
    mat['bl_tile_m'] = spec['tile']
    mat['bl_disp'] = int(spec['disp'])
    # viewport colour
    mat.diffuse_color = (*_preview_rgb(name), 1)
    return mat


def _preview_rgb(name):
    for key, c in (('Cobble', (0.2, 0.19, 0.18)), ('Plaster Ochre', (0.7, 0.45, 0.17)), ('Plaster Rose', (0.66, 0.33, 0.24)),
                   ('Plaster', (0.72, 0.66, 0.55)), ('Timber', (0.08, 0.05, 0.03)), ('Plank', (0.2, 0.13, 0.08)),
                   ('Roof Clay', (0.5, 0.18, 0.08)), ('Slate', (0.08, 0.08, 0.1)), ('Ashlar', (0.45, 0.38, 0.3)),
                   ('Iron', (0.06, 0.06, 0.06)), ('Grass', (0.08, 0.16, 0.03)), ('Water', (0.05, 0.2, 0.25))):
        if key in name:
            return c
    return (0.5, 0.5, 0.5)


def get(name):
    """Return material 'BL <name>', building it on first use."""
    m = bpy.data.materials.get(PREFIX + name)
    if m is None:
        m = build(name)
    return m


def is_displaced(name):
    if name in REG:
        return REG[name]['disp']
    return False


def all_names():
    return list(REG.keys()) + list(CUSTOM.keys())


# ----------------------------------------------------------------------------------------------
# Custom shaders
# ----------------------------------------------------------------------------------------------
def _water(mat, flow=(1.0, 0.0), speed=0.45, color=(0.25, 0.6, 0.58), density=0.10, chop=1.0, volume=True):
    nb = NB(mat.node_tree)
    glob_ = nb.group(global_group())
    P = nb.vscale(nb.geo('Position'), 1.0 / M)
    px, py, pz = nb.sep(P)
    t = glob_.outputs['Time']
    drift = nb.mul(t, speed)
    # flow-aligned coordinates (stretched along the flow)
    fx = nb.sub(px, nb.mul(drift, flow[0]))
    fy = nb.sub(py, nb.mul(drift, flow[1]))
    if abs(flow[1]) > abs(flow[0]):
        fx, fy = fy, fx                       # stretch along the flow axis
    big = nb.noise(nb.comb(nb.mul(fx, 0.5), nb.mul(fy, 1.4), 0.0), 1.1, 3, 0.55, dims='4D', w=nb.mul(t, 0.15))
    small = nb.noise(nb.comb(nb.mul(fx, 2.0), nb.mul(fy, 4.5), 0.0), 2.4, 4, 0.6, dims='4D', w=nb.mul(t, 0.5))
    tiny = nb.noise(nb.comb(fx, fy, 0.0), 22.0, 2, 0.5, dims='4D', w=nb.mul(t, 1.2))
    h = nb.add(nb.add(nb.mul(big, 0.03 * chop), nb.mul(small, 0.012 * chop)), nb.mul(tiny, 0.002))
    # foam: painted attribute 'foam' (0..1) broken up by streaky noise
    fa = nb.attr('foam', 'Fac')
    fn = nb.noise(nb.comb(nb.mul(fx, 1.5), nb.mul(fy, 5.0), 0.0), 3.0, 5, 0.65, dims='4D', w=nb.mul(t, 0.7))
    fn2 = nb.noise(nb.comb(fx, fy, 0.0), 14.0, 3, 0.6, dims='4D', w=nb.mul(t, 1.5))
    brk = nb.add(nb.mul(fn, 0.9), nb.mul(fn2, 0.45))
    foam = nb.smooth(nb.add(nb.mul(fa, nb.sub(brk, 0.15)), nb.mul(fa, 0.25)), 0.55, 0.85)
    streak = nb.mul(nb.mul(nb.smooth(fn, 0.62, 0.7), nb.smooth(fa, 0.05, 0.3)), 0.5)
    foam = nb.clamp01(nb.add(nb.mul(foam, 0.9), streak))
    h = nb.add(h, nb.mul(foam, 0.006))
    nrm = nb.bump(nb.mul(h, M), 1.0, 1.0)
    water = nb.node('ShaderNodeBsdfPrincipled')
    water.inputs['Base Color'].default_value = (0.8, 0.95, 0.95, 1)
    water.inputs['Roughness'].default_value = 0.025
    water.inputs['IOR'].default_value = 1.333
    water.inputs['Transmission Weight'].default_value = 1.0
    nb.L.new(nrm, water.inputs['Normal'])
    fm = nb.node('ShaderNodeBsdfPrincipled')
    fm.inputs['Base Color'].default_value = (0.62, 0.68, 0.68, 1)
    fm.inputs['Roughness'].default_value = 0.6
    nb.L.new(nrm, fm.inputs['Normal'])
    m1 = nb.node('ShaderNodeMixShader')
    nb.L.new(foam, m1.inputs[0])
    nb.L.new(water.outputs[0], m1.inputs[1])
    nb.L.new(fm.outputs[0], m1.inputs[2])
    # shadow rays pass through (tinted) so the bed is lit
    lp = nb.node('ShaderNodeLightPath')
    tr = nb.node('ShaderNodeBsdfTransparent')
    tr.inputs['Color'].default_value = (0.85, 0.95, 0.95, 1)
    m2 = nb.node('ShaderNodeMixShader')
    nb.L.new(lp.outputs['Is Shadow Ray'], m2.inputs[0])
    nb.L.new(m1.outputs[0], m2.inputs[1])
    nb.L.new(tr.outputs[0], m2.inputs[2])
    out = nb.node('ShaderNodeOutputMaterial')
    nb.L.new(m2.outputs[0], out.inputs['Surface'])
    if volume:
        vol = nb.node('ShaderNodeVolumeAbsorption')
        vol.inputs['Color'].default_value = (*color, 1)
        vol.inputs['Density'].default_value = density
        nb.L.new(vol.outputs[0], out.inputs['Volume'])
    else:
        water.inputs['Base Color'].default_value = (*color, 1)
    mat.displacement_method = 'BUMP'
    mat.diffuse_color = (0.05, 0.2, 0.25, 1)


CUSTOM['Water River'] = lambda m: _water(m)
CUSTOM['Water River Y'] = lambda m: _water(m, flow=(0.0, -1.0), speed=0.6, color=(0.2, 0.55, 0.55), density=0.33)
CUSTOM['Water Still'] = lambda m: _water(m, speed=0.05, chop=0.35, density=0.18, color=(0.3, 0.55, 0.5))
CUSTOM['Water Thin'] = lambda m: _water(m, speed=0.05, chop=0.25, color=(0.55, 0.8, 0.78), volume=False)


def _falling(mat):
    nb = NB(mat.node_tree)
    co = Co(nb)
    t = nb.group(global_group()).outputs['Time']
    st = nb.noise(nb.comb(nb.mul(co.u, 14.0), nb.sub(nb.mul(co.v, 1.2), nb.mul(t, 2.5)), 0.0), 2.0, 4, 0.6)
    foam = nb.smooth(st, 0.5, 0.75)
    w = nb.node('ShaderNodeBsdfPrincipled')
    w.inputs['Base Color'].default_value = (0.8, 0.95, 0.95, 1)
    w.inputs['Roughness'].default_value = 0.05
    w.inputs['Transmission Weight'].default_value = 1.0
    w.inputs['IOR'].default_value = 1.33
    nb.L.new(nb.bump(nb.mul(st, 0.02), 1.0, 1.0), w.inputs['Normal'])
    f = nb.node('ShaderNodeBsdfPrincipled')
    f.inputs['Base Color'].default_value = (0.85, 0.9, 0.9, 1)
    f.inputs['Roughness'].default_value = 0.5
    mx = nb.node('ShaderNodeMixShader')
    nb.L.new(nb.mul(foam, 0.8), mx.inputs[0])
    nb.L.new(w.outputs[0], mx.inputs[1])
    nb.L.new(f.outputs[0], mx.inputs[2])
    lp = nb.node('ShaderNodeLightPath')
    tr = nb.node('ShaderNodeBsdfTransparent')
    m2 = nb.node('ShaderNodeMixShader')
    nb.L.new(lp.outputs['Is Shadow Ray'], m2.inputs[0])
    nb.L.new(mx.outputs[0], m2.inputs[1])
    nb.L.new(tr.outputs[0], m2.inputs[2])
    out = nb.node('ShaderNodeOutputMaterial')
    nb.L.new(m2.outputs[0], out.inputs['Surface'])
    mat.diffuse_color = (0.7, 0.85, 0.9, 0.5)


CUSTOM['Water Falling'] = lambda m: _falling(m)


def _glass(mat, tint=(0.75, 0.85, 0.8), leaded=True, emission=0.0, ecol=(1.0, 0.55, 0.2)):
    nb = NB(mat.node_tree)
    co = Co(nb)
    u, v = co.u, co.v
    # diamond lattice of lead cames
    a = nb.add(u, v)
    b = nb.sub(u, v)
    s = 0.13
    la = nb.math('ABSOLUTE', nb.sub(nb.math('FRACT', nb.div(a, s)), 0.5))
    lb = nb.math('ABSOLUTE', nb.sub(nb.math('FRACT', nb.div(b, s)), 0.5))
    lead = nb.mx(nb.smooth(la, 0.44, 0.47), nb.smooth(lb, 0.44, 0.47)) if leaded else 0.0
    wob = nb.noise(nb.comb(nb.div(a, s), nb.div(b, s), 0.0), 3.0, 3, 0.5)
    nrm = nb.bump(nb.mul(wob, 0.004 * M), 1.0, 1.0)
    g = nb.node('ShaderNodeBsdfPrincipled')
    g.inputs['Base Color'].default_value = (0.02, 0.03, 0.028, 1)
    g.inputs['Roughness'].default_value = 0.04
    g.inputs['Specular IOR Level'].default_value = 0.8
    nb.L.new(nrm, g.inputs['Normal'])
    if emission:
        ec = nb.mix(wob, ecol, nb.cmul(nb.rgb(ecol), (1.2, 0.85, 0.6)))
        nb.L.new(ec, g.inputs['Emission Color'])
        g.inputs['Emission Strength'].default_value = emission
    pb = nb.node('ShaderNodeBsdfPrincipled')
    pb.inputs['Base Color'].default_value = (0.03, 0.03, 0.03, 1)
    pb.inputs['Metallic'].default_value = 0.6
    pb.inputs['Roughness'].default_value = 0.5
    mx = nb.node('ShaderNodeMixShader')
    nb.feed(mx.inputs[0], lead)
    nb.L.new(g.outputs[0], mx.inputs[1])
    nb.L.new(pb.outputs[0], mx.inputs[2])
    out = nb.node('ShaderNodeOutputMaterial')
    nb.L.new(mx.outputs[0], out.inputs['Surface'])
    mat.diffuse_color = (0.05, 0.07, 0.07, 1)


CUSTOM['Glass Leaded'] = lambda m: _glass(m)


def _clear_glass(mat, tint=(0.9, 0.95, 0.92), rough=0.08):
    nb = NB(mat.node_tree)
    g = nb.node('ShaderNodeBsdfPrincipled')
    g.inputs['Base Color'].default_value = (*tint, 1)
    g.inputs['Roughness'].default_value = rough
    g.inputs['Transmission Weight'].default_value = 1.0
    g.inputs['IOR'].default_value = 1.45
    lp = nb.node('ShaderNodeLightPath')
    tr = nb.node('ShaderNodeBsdfTransparent')
    mx = nb.node('ShaderNodeMixShader')
    nb.L.new(lp.outputs['Is Shadow Ray'], mx.inputs[0])
    nb.L.new(g.outputs[0], mx.inputs[1])
    nb.L.new(tr.outputs[0], mx.inputs[2])
    out = nb.node('ShaderNodeOutputMaterial')
    nb.L.new(mx.outputs[0], out.inputs['Surface'])
    mat.diffuse_color = (0.8, 0.9, 0.9, 0.3)


CUSTOM['Glass Clear'] = lambda m: _clear_glass(m)
CUSTOM['Glass Window Lit'] = lambda m: _glass(m, emission=2.2, ecol=(1.0, 0.48, 0.16))


def _stained(mat, strength=6.0, tint=(1, 1, 1), scale=9.0):
    nb = NB(mat.node_tree)
    co = Co(nb)
    u, v = co.u, co.v
    uv = nb.comb(u, v, 0.0)
    cell, cid = nb.voronoi(uv, scale, 'F1', ['Distance', 'Color'], 0.85, '2D')
    ed = nb.voronoi(uv, scale, 'DISTANCE_TO_EDGE', 'Distance', 0.85, '2D')
    r_, g_, b_ = nb.sep(cid)
    pal = [(0.0, (0.75, 0.02, 0.03)), (0.18, (0.02, 0.12, 0.75)), (0.34, (0.95, 0.6, 0.02)),
           (0.5, (0.02, 0.45, 0.12)), (0.62, (0.85, 0.05, 0.05)), (0.75, (0.35, 0.04, 0.6)),
           (0.88, (0.05, 0.3, 0.85)), (1.0, (0.9, 0.75, 0.3))]
    col = nb.ramp(r_, pal, 'CONSTANT')
    # concentric medallion: rings from the pane centre in metres (window centre = UV origin per window)
    wob = nb.noise(uv, 25.0, 3, 0.5)
    col = nb.cmul(col, nb.ramp(wob, [(0.3, (0.7, 0.7, 0.7)), (0.7, (1.2, 1.2, 1.2))]))
    lead = nb.inv(nb.smooth(ed, 0.006, 0.012))
    ecol = nb.cmul(col, tint)
    em = nb.node('ShaderNodeEmission')
    nb.L.new(ecol, em.inputs['Color'])
    em.inputs['Strength'].default_value = strength
    em.name = 'GLOW'
    tr = nb.node('ShaderNodeBsdfTranslucent')
    nb.L.new(col, tr.inputs['Color'])
    add = nb.node('ShaderNodeAddShader')
    nb.L.new(em.outputs[0], add.inputs[0])
    nb.L.new(tr.outputs[0], add.inputs[1])
    pb = nb.node('ShaderNodeBsdfPrincipled')
    pb.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1)
    pb.inputs['Roughness'].default_value = 0.5
    pb.inputs['Metallic'].default_value = 0.5
    mx = nb.node('ShaderNodeMixShader')
    nb.L.new(lead, mx.inputs[0])
    nb.L.new(add.outputs[0], mx.inputs[1])
    nb.L.new(pb.outputs[0], mx.inputs[2])
    # shadow rays: coloured light passes through the glass (sun patches on the floor)
    lp = nb.node('ShaderNodeLightPath')
    tr2 = nb.node('ShaderNodeBsdfTransparent')
    nb.L.new(nb.mix(lead, nb.cmul(col, (1.6, 1.6, 1.6)), (0, 0, 0)), tr2.inputs['Color'])
    m3 = nb.node('ShaderNodeMixShader')
    nb.L.new(lp.outputs['Is Shadow Ray'], m3.inputs[0])
    nb.L.new(mx.outputs[0], m3.inputs[1])
    nb.L.new(tr2.outputs[0], m3.inputs[2])
    out = nb.node('ShaderNodeOutputMaterial')
    nb.L.new(m3.outputs[0], out.inputs['Surface'])
    mat.diffuse_color = (0.5, 0.1, 0.3, 1)


CUSTOM['Stained Glass Day'] = lambda m: _stained(m, 4.5)
CUSTOM['Stained Glass Golden'] = lambda m: _stained(m, 7.0, (1.3, 0.85, 0.5))
CUSTOM['Stained Glass Night'] = lambda m: _stained(m, 0.5, (0.5, 0.65, 1.2))


def _flame(mat, strength=40.0, col_a=(1.0, 0.85, 0.45), col_b=(1.0, 0.32, 0.05)):
    """Flame card / blob: hot core to orange edge, fades out at the top (uses Generated Z)."""
    nb = NB(mat.node_tree)
    gx, gz, _ = nb.sep(nb.uvmap())          # flames carry normalised UVs: V = 0 at the base, 1 at the tip
    n = nb.noise(nb.texco('Object'), 2.5, 3, 0.6, dims='4D', w=nb.mul(nb.group(global_group()).outputs['Time'], 3.0))
    core = nb.inv(nb.smooth(nb.add(gz, nb.mul(n, 0.3)), 0.2, 0.95))
    col = nb.mix(core, col_b, col_a)
    em = nb.node('ShaderNodeEmission')
    nb.L.new(col, em.inputs['Color'])
    nb.feed(em.inputs['Strength'], nb.mul(nb.add(0.3, core), strength))
    tr = nb.node('ShaderNodeBsdfTransparent')
    mx = nb.node('ShaderNodeMixShader')
    alpha = nb.clamp01(nb.mul(nb.inv(nb.smooth(gz, 0.55, 1.0)), 1.2))
    nb.L.new(alpha, mx.inputs[0])
    nb.L.new(tr.outputs[0], mx.inputs[1])
    nb.L.new(em.outputs[0], mx.inputs[2])
    out = nb.node('ShaderNodeOutputMaterial')
    nb.L.new(mx.outputs[0], out.inputs['Surface'])
    mat.diffuse_color = (1.0, 0.5, 0.1, 1)


CUSTOM['Flame'] = lambda m: _flame(m, 3.2, (1.0, 0.78, 0.35), (1.0, 0.28, 0.03))
CUSTOM['Flame Candle'] = lambda m: _flame(m, 3.0, (1.0, 0.85, 0.5), (1.0, 0.42, 0.08))
CUSTOM['Embers'] = lambda m: _flame(m, 2.5, (1.0, 0.4, 0.06), (0.6, 0.06, 0.01))


def _glow(mat, color=(1.0, 0.6, 0.25), strength=8.0):
    nb = NB(mat.node_tree)
    em = nb.node('ShaderNodeEmission')
    em.inputs['Color'].default_value = (*color, 1)
    em.inputs['Strength'].default_value = strength
    out = nb.node('ShaderNodeOutputMaterial')
    nb.L.new(em.outputs[0], out.inputs['Surface'])
    mat.diffuse_color = (*color, 1)


CUSTOM['Glow Warm'] = lambda m: _glow(m)
CUSTOM['Glow Window'] = lambda m: _glow(m, (1.0, 0.55, 0.22), 3.0)
CUSTOM['Glow Firefly'] = lambda m: _glow(m, (0.75, 1.0, 0.25), 40.0)


def _shaft(mat, color=(1.0, 0.92, 0.75), strength=0.35):
    """Fake volumetric light shaft card: additive emission, fades along length (Generated Z) and at the sides."""
    nb = NB(mat.node_tree)
    gx, gy, gz = nb.sep(nb.texco('Generated'))
    side = nb.mul(nb.math('SINE', nb.mul(gx, math.pi)), nb.math('SINE', nb.mul(gy, math.pi)))
    along = nb.mul(nb.smooth(gz, 0.0, 0.25), nb.inv(nb.smooth(gz, 0.6, 1.0)))
    dust = nb.noise(nb.texco('Object'), 3.0, 3, 0.6)
    k = nb.mul(nb.mul(side, along), nb.maprange(dust, 0.3, 0.7, 0.6, 1.3))
    em = nb.node('ShaderNodeEmission')
    em.inputs['Color'].default_value = (*color, 1)
    nb.feed(em.inputs['Strength'], nb.mul(k, strength))
    tr = nb.node('ShaderNodeBsdfTransparent')
    add = nb.node('ShaderNodeAddShader')
    nb.L.new(em.outputs[0], add.inputs[0])
    nb.L.new(tr.outputs[0], add.inputs[1])
    lp = nb.node('ShaderNodeLightPath')
    mx = nb.node('ShaderNodeMixShader')       # only camera rays see the shaft
    nb.L.new(lp.outputs['Is Camera Ray'], mx.inputs[0])
    nb.L.new(tr.outputs[0], mx.inputs[1])
    nb.L.new(add.outputs[0], mx.inputs[2])
    out = nb.node('ShaderNodeOutputMaterial')
    nb.L.new(mx.outputs[0], out.inputs['Surface'])
    mat.diffuse_color = (*color, 1)


CUSTOM['Shaft Day'] = lambda m: _shaft(m, (1.0, 0.93, 0.78), 1.6)
CUSTOM['Shaft Golden'] = lambda m: _shaft(m, (1.0, 0.62, 0.3), 1.6)
CUSTOM['Shaft Night'] = lambda m: _shaft(m, (0.55, 0.68, 1.0), 0.5)


def image_material(name, path, base='Planks', alpha_over=True, sat=1.0, val=1.0, translucent=None):
    """A painted sign / banner: an image (with alpha) laid over a library surface, on UV 'UVs' (0..1).
    sat / val: HSV lift of the art (the embroidered cc0 banners need ~1.2 / 1.5 to read like the old flat ones
    at phone size); translucent: override the base surface's translucency mix (cloth seen against a wall)."""
    full = PREFIX + name
    mat = _fresh_material(full)
    nb = NB(mat.node_tree)
    img = bpy.data.images.load(path, check_existing=True)
    try:
        img.pack()
    except Exception:
        pass
    uvn = nb.node('ShaderNodeUVMap')
    uvn.uv_map = UVNAME
    tex = nb.node('ShaderNodeTexImage')
    tex.image = img
    tex.extension = 'CLIP'
    nb.L.new(uvn.outputs[0], tex.inputs[0])
    surf = nb.group(bpy.data.node_groups.get('BLS ' + base) or _surface_group(base, REG[base]))
    wear = nb.group(wear_group())
    for k, key in (('edge', 'Edge'), ('grime', 'Grime'), ('moss', 'Moss'), ('damp', 'Damp'), ('streaks', 'Streaks')):
        wear.inputs[key].default_value = REG[base]['wear'].get(k, 0.0) * 0.5
    art = tex.outputs['Color']
    if sat != 1.0 or val != 1.0:
        art = nb.hsv(art, 0.5, sat, val)
    col = nb.mix(tex.outputs['Alpha'], surf.outputs['Color'], art)
    nb.L.new(col, wear.inputs['Color'])
    rough = nb.mixf(tex.outputs['Alpha'], surf.outputs['Roughness'], 0.6)
    nb.L.new(rough, wear.inputs['Roughness'])
    nb.L.new(surf.outputs['Cavity'], wear.inputs['Cavity'])
    p = nb.node('ShaderNodeBsdfPrincipled')
    nb.L.new(wear.outputs['Color'], p.inputs['Base Color'])
    nb.L.new(wear.outputs['Roughness'], p.inputs['Roughness'])
    nb.L.new(surf.outputs['Normal'], p.inputs['Normal'])
    if REG[base]['sh'].get('sh_sheen'):
        p.inputs['Sheen Weight'].default_value = REG[base]['sh']['sh_sheen']
    shader = p.outputs[0]
    trv = REG[base]['sh'].get('sh_translucent') if translucent is None else translucent
    if trv:
        tr = nb.node('ShaderNodeBsdfTranslucent')
        nb.L.new(wear.outputs['Color'], tr.inputs['Color'])
        mx = nb.node('ShaderNodeMixShader')
        mx.inputs[0].default_value = trv
        nb.L.new(p.outputs[0], mx.inputs[1])
        nb.L.new(tr.outputs[0], mx.inputs[2])
        shader = mx.outputs[0]
    out = nb.node('ShaderNodeOutputMaterial')
    nb.L.new(shader, out.inputs['Surface'])
    mat['bl_lib'] = name
    mat['bl_art'] = path
    return mat


ART_LIFT = dict(sat=1.2, val=1.5, translucent=0.12)     # for the embroidered custom/ banner art


def lift_art_materials(names=None, **lift):
    """Rebuild existing image materials (banners from the cc0_* art) with ART_LIFT (or the given lift)."""
    lift = lift or ART_LIFT
    done = []
    for m in list(bpy.data.materials):
        if not m.name.startswith(PREFIX + 'Banner ') or (names and m.name[len(PREFIX):] not in names):
            continue
        tex = [n for n in m.node_tree.nodes if n.type == 'TEX_IMAGE']
        if not tex or tex[0].image is None:
            continue
        path = bpy.path.abspath(tex[0].image.filepath)
        if not os.path.basename(path).startswith('cc0_'):
            continue
        image_material(m.name[len(PREFIX):], path, base='Cloth White', **lift)
        done.append(m.name)
    return done



# ----------------------------------------------------------------------------------------------
# Image sets (CC0 photo-scans).  One call per material.
# ----------------------------------------------------------------------------------------------
MAPS = {
    'color': ('_diff', '_diffuse', '_albedo', '_basecolor', '_base_color', '_color', '_col', 'albedo', 'basecolor', 'diffuse'),
    'normal': ('_nor_gl', '_normalgl', '_normal_gl', '_normal', '_nrm', '_nor'),
    'rough': ('_rough', '_roughness', 'roughness'),
    'disp': ('_disp', '_displacement', '_height', 'displacement'),
    'ao': ('_ao', '_ambientocclusion', 'ambientocclusion'),
    'metal': ('_metal', '_metallic', '_metalness'),
}
IMG_EXT = ('.png', '.jpg', '.jpeg', '.tif', '.tiff', '.exr')


BARE = {   # folder-per-material sets with plain file names (color.jpg, normal.jpg, ...)
    'color': ('color', 'colour', 'diffuse', 'diff', 'albedo', 'basecolor', 'base_color', 'col'),
    'normal': ('normal', 'normal_gl', 'normalgl', 'nor_gl', 'nrm'),
    'rough': ('roughness', 'rough'),
    'disp': ('displacement', 'height', 'disp'),
    'ao': ('ao', 'ambient_occlusion', 'ambientocclusion', 'occlusion'),
    'metal': ('metal', 'metallic', 'metalness'),
}


def find_maps(folder):
    files = [f for f in glob.glob(os.path.join(folder, '**', '*'), recursive=True) if f.lower().endswith(IMG_EXT)]
    found = {}
    for key, names in BARE.items():
        for f in files:
            if os.path.splitext(os.path.basename(f))[0].lower() in names:
                found[key] = f
                break
    for key, pats in MAPS.items():
        if key in found:
            continue
        for f in sorted(files, key=len):
            b = os.path.basename(f).lower()
            if key == 'normal' and ('_dx' in b or 'normaldx' in b) and any('_gl' in os.path.basename(x).lower() for x in files):
                continue
            if any(p in b for p in pats):
                if key == 'color' and any(p in b for p in MAPS['normal'] + MAPS['rough'] + MAPS['disp'] + MAPS['ao']):
                    continue
                found[key] = f
                break
    return found


_MEAN_CACHE = {}


def _img_mean(path, desat=0.0):
    """Mean linear RGB of an image after the same HSV desaturation the shader applies (PIL; ~0.1 s)."""
    key = (path, round(desat, 3))
    if key in _MEAN_CACHE:
        return _MEAN_CACHE[key]
    try:
        from PIL import Image
        import numpy as np
        im = Image.open(path)
        im.draft('RGB', (256, 256))
        a = np.asarray(im.convert('RGB').resize((128, 128)), dtype=np.float32) / 255.0
        lin = np.where(a <= 0.04045, a / 12.92, ((a + 0.055) / 1.055) ** 2.4)
        v = lin.max(axis=2, keepdims=True)
        lin = v - (v - lin) * (1.0 - desat)
        m = tuple(float(x) for x in lin.reshape(-1, 3).mean(0))
    except Exception:
        img = bpy.data.images.load(path, check_existing=True)
        px = list(img.pixels[::4 * 997])
        m = (0.2, 0.2, 0.2) if not px else (sum(px) / len(px),) * 3
    _MEAN_CACHE[key] = m
    return m


def _img_size(path):
    """Image size from the file header (PIL), so Blender does not decode the whole image at setup."""
    try:
        from PIL import Image
        with Image.open(path) as im:
            return im.size
    except Exception:
        img = bpy.data.images.load(path, check_existing=True)
        return tuple(img.size[:]) if img.size[0] else (1, 1)


def _load_image(path, colorspace):
    img = bpy.data.images.load(path, check_existing=True)
    img.colorspace_settings.name = colorspace
    return img


def _nswz(nb, col, mode):
    """Re-orient a tangent-space (OpenGL) normal-map sample whose image axes were rotated against UVm.
    mode: None | 'swap' (image x<-V, y<-U) | 'swapflip' (image x<- -V, y<-U) | 'flipy'."""
    if not mode:
        return col
    s = nb.node('ShaderNodeSeparateColor')
    nb.feed(s.inputs[0], col)
    r, g, b = s.outputs[0], s.outputs[1], s.outputs[2]
    if mode == 'swap':
        r2, g2 = g, r
    elif mode == 'swapflip':
        r2, g2 = g, nb.inv(r)
    elif mode == 'swapflipy':
        r2, g2 = nb.inv(g), r
    else:  # flipy
        r2, g2 = r, nb.inv(g)
    c = nb.node('ShaderNodeCombineColor')
    nb.feed(c.inputs[0], r2)
    nb.feed(c.inputs[1], g2)
    nb.feed(c.inputs[2], b)
    return c.outputs[0]


IMG_DEFAULTS = dict(tile_m=None, disp_m=None, rot90=False, flip_v=False, anti='none', islands=False,
                    tint=None, desat=0.0, sat=1.0, val=1.0, macro=0.12, normal_strength=1.0, use_normal=None, coords='uv',
                    rough_mul=1.0, rough_add=0.0, use_ao=False, ao_amt=0.5, cav_disp=0.5, bump_disp=0.3, metal=None, puddles=0.0,
                    maps=None)


def _img_surface(nb, co, folder, spec_tile=2.0, spec_disp=False, **kw):
    """Sample a photo-scan set inside a surface group.  Returns dict(color, rough, height, cavity, metal, normal)
    with height in metres.  Options: see IMG_DEFAULTS.
      tile_m      real width of the image in metres (height follows the image aspect)
      rot90       image Y runs along UVm U (wood grain / bark along U)
      flip_v      mirror the image vertically (roof tiles: exposed edge down the slope)
      anti        'rot' = second sample rotated 90 deg + scaled, blended by noise (isotropic sets only);
                  'none' = single sample (structured sets: bricks, setts, tiles, planks)
      islands     offset the sample per object / UV island (beams do not all show the same grain)
      tint        target mean linear RGB (after desat); the image is scaled per channel to hit it
      desat       0..1 HSV desaturation before tinting;  sat / val: HSV after tinting
      macro       +-fraction of slow world-space brightness variation (hides tiling)
      coords      'uv' (UVm, metres) or 'xy' (object-space metres; flat ground, saves memory when displaced)
      use_normal  None = normal map on bump-only surfaces, none on displaced ones
      puddles     0..1 standing water in low spots (displaced ground with a displacement map)
      use_ao      load the AO map (off by default: the wear stack computes crevice AO, and every
                  2K map costs Cycles memory); cav_disp: crevice mask from the displacement map instead
    """
    o = dict(IMG_DEFAULTS)
    o.update(kw)
    maps = find_maps(folder)
    if o['maps'] is not None:
        maps = {k: v for k, v in maps.items() if k in o['maps'] or k == 'color'}
    if 'color' not in maps:
        raise FileNotFoundError('no colour map in ' + folder)
    if o['use_normal'] is None:
        # displaced surfaces get their relief from the displacement (+ automatic bump); a tangent-space normal
        # map there would make Cycles store UV tangents on every micropolygon (~+200 MB per set)
        o['use_normal'] = not spec_disp
    if not o['use_normal']:
        maps.pop('normal', None)
    if not o['use_ao']:
        maps.pop('ao', None)
    iw, ih = _img_size(maps['color'])
    tw = o['tile_m'] or spec_tile
    th = tw * ih / float(iw)
    dm = o['disp_m'] if o['disp_m'] is not None else (0.02 if spec_disp else 0.005)
    if o['coords'] == 'xy':
        # flat ground: object-space metres (no UV attribute on the subdivided micropolygons)
        u, v, _ = nb.sep(co.P)
    else:
        u, v = (co.ur, co.vr) if o['islands'] else (co.u, co.v)
    a, b = (v, u) if o['rot90'] else (u, v)
    if o['flip_v']:
        b = nb.mul(b, -1.0)
    uv1 = nb.comb(nb.div(a, tw), nb.div(b, th), 0.0)
    nmode1 = ('swapflipy' if o['flip_v'] else 'swap') if o['rot90'] else ('flipy' if o['flip_v'] else None)
    samples = [(uv1, nmode1)]
    blend = None
    if o['anti'] == 'rot':
        # second sample: image rotated 90 deg (x <- -b, y <- a), 0.77 scale, offset
        uv2 = nb.vadd(nb.comb(nb.div(nb.mul(b, -0.77), tw), nb.div(nb.mul(a, 0.77), th), 0.0), (0.37, 0.61, 0.0))
        samples.append((uv2, 'swapflip' if not o['rot90'] else None))
        blend = nb.smooth(nb.noise(co.P, 0.6, 3, 0.55), 0.4, 0.6)

    def tex(key, colorspace, normal=False):
        img = _load_image(maps[key], colorspace)
        outs = []
        for vec, nm in samples:
            t = nb.node('ShaderNodeTexImage')
            t.image = img
            t.interpolation = 'Cubic' if key == 'disp' else 'Linear'
            nb.L.new(vec, t.inputs[0])
            out = t.outputs['Color']
            if normal:
                out = _nswz(nb, out, nm)
            outs.append(out)
        if len(outs) == 1:
            return outs[0]
        return nb.mix(blend, outs[0], outs[1])

    def texf(key):
        img = _load_image(maps[key], 'Non-Color')
        outs = []
        for vec, nm in samples:
            t = nb.node('ShaderNodeTexImage')
            t.image = img
            t.interpolation = 'Cubic' if key == 'disp' else 'Linear'
            nb.L.new(vec, t.inputs[0])
            outs.append(nb.sep(t.outputs['Color'])[0])
        if len(outs) == 1:
            return outs[0]
        return nb.mixf(blend, outs[0], outs[1])

    col = tex('color', 'sRGB')
    if o['desat']:
        col = nb.hsv(col, 0.5, 1.0 - o['desat'], 1.0)
    if o['tint']:
        m = _img_mean(maps['color'], o['desat'])
        f = tuple(min(12.0, t / max(1e-4, mm)) for t, mm in zip(o['tint'], m))
        col = nb.cmul(col, f)
    if o['sat'] != 1.0 or o['val'] != 1.0:
        col = nb.hsv(col, 0.5, o['sat'], o['val'])
    if o['macro']:
        mv = nb.maprange(nb.noise(co.P, 0.35, 3, 0.55), 0.3, 0.7, 1.0 - o['macro'], 1.0 + o['macro'])
        col = nb.cmul(col, nb.comb(mv, mv, mv))
    rough = 0.7
    if 'rough' in maps:
        rough = texf('rough')
        if o['rough_mul'] != 1.0 or o['rough_add']:
            rough = nb.clamp01(nb.madd(rough, o['rough_mul'], o['rough_add']))
    height = 0.0
    cav = 0.0
    if 'disp' in maps:
        dsp = texf('disp')
        height = nb.mul(dsp, dm)
        if 'ao' not in maps and o['cav_disp']:
            # joints / low spots of the scan feed the wear stack's crevice grime (no AO map needed)
            cav = nb.mul(nb.inv(nb.smooth(dsp, 0.05, 0.45)), o['cav_disp'])
    if 'ao' in maps:
        cav = nb.inv(texf('ao'))
        col = nb.mix(nb.mul(cav, o['ao_amt']), col, nb.cmul(col, (0.5, 0.5, 0.5)))
    if o['puddles'] and 'disp' in maps:
        # rain water standing in the joints / low spots inside large soft patches (night glints), like the
        # procedural cobbles: flat water level in the displacement, near-mirror roughness, darker stone
        pn = nb.noise(nb.vadd(co.P, (11.3, 5.1, 0.0)), 0.13, 3, 0.55)
        pm = nb.mul(nb.smooth(pn, 0.56, 0.6), o['puddles'])
        lvl = 0.42
        water = nb.mul(pm, nb.inv(nb.smooth(dsp, lvl - 0.08, lvl + 0.02)))
        height = nb.mixf(pm, height, nb.mul(nb.mx(dsp, lvl), dm))
        col = nb.mix(water, col, nb.cmul(col, (0.45, 0.47, 0.5)))
        rough = nb.mixf(water, rough, 0.03)
    metal = o['metal'] if o['metal'] is not None else 0.0
    if 'metal' in maps and o['metal'] is None:
        metal = texf('metal')
    nrm = nb.geo('Normal')
    if 'normal' in maps:
        nm = nb.node('ShaderNodeNormalMap', space='TANGENT', uv_map=UVNAME)
        nm.inputs['Strength'].default_value = o['normal_strength']
        nb.L.new(tex('normal', 'Non-Color', normal=True), nm.inputs['Color'])
        nrm = nm.outputs[0]
    if not spec_disp and 'disp' in maps and o['bump_disp']:
        nrm = nb.bump(nb.mul(height, M), o['bump_disp'], 1.0, nrm)
    return dict(color=col, rough=rough, height=height, cavity=cav, metal=metal, normal=nrm, maps=maps)


def _finish_group(nb, go, r):
    nb.feed(go.inputs['Color'], r['color'])
    nb.feed(go.inputs['Roughness'], r['rough'])
    nb.feed(go.inputs['Metallic'], r.get('metal', 0.0))
    nb.feed(go.inputs['Normal'], r['normal'])
    nb.feed(go.inputs['Height'], r.get('height', 0.0))
    nb.feed(go.inputs['Cavity'], r.get('cavity', 0.0))


def use_image_set(name, folder, tile_m=None, disp_m=None, **opts):
    """Switch 'BL <name>' to the photo-scanned set in `folder` (one call; keeps the wear stack and the
    material's displacement).  tile_m = real-world width of the image in metres (default: the material's
    tile size); disp_m = displacement depth in metres.  More options: see _img_surface / IMG_DEFAULTS."""
    mat = get(name)
    if name in CUSTOM:
        raise ValueError('custom shader has no image mode: ' + name)
    spec = REG[name]
    g, gi, go = _new_group('BLI ' + name, [], SURF_OUT)
    nb = NB(g)
    co = Co(nb)
    r = _img_surface(nb, co, folder, spec['tile'], spec['disp'], tile_m=tile_m, disp_m=disp_m, **opts)
    _finish_group(nb, go, r)
    g['bl_kind'] = 'images'
    g['bl_folder'] = folder
    mat.node_tree.nodes['SURF'].node_tree = g
    mat['bl_source'] = folder
    return mat


def use_detail_set(name, folder, amount=1.0, **opts):
    """Keep the procedural pattern of 'BL <name>' (e.g. plaster cracks and damaged patches) and lay the
    photo-scan over it as a detail layer: colour multiplied by the scan's normalised luminance, the scan's
    normal map, roughness nudged by the scan.  For surfaces whose procedural layout matters."""
    mat = get(name)
    spec = REG[name]
    g, gi, go = _new_group('BLI ' + name, [], SURF_OUT)
    nb = NB(g)
    co = Co(nb)
    p = spec['fn'](nb, co, **spec['args'])
    o = dict(opts)
    o.setdefault('desat', 1.0)
    o.setdefault('macro', 0.0)
    o['tint'] = (1.0, 1.0, 1.0)       # normalise the scan to mean 1 (luminance detail only)
    r = _img_surface(nb, co, folder, spec['tile'], spec['disp'], **o)
    det = nb.mix(amount, (1.0, 1.0, 1.0), r['color'])
    col = nb.cmul(p['color'], det)
    rough = nb.mixf(0.35 * amount, p['rough'], r['rough']) if not isinstance(r['rough'], float) else p['rough']
    # procedural relief as bump on top of the scan normal
    bh = p.get('height', 0.0) if not spec['disp'] else p.get('micro', 0.0)
    nrm = r['normal']
    if not (isinstance(bh, (int, float)) and bh == 0.0):
        nrm = nb.bump(nb.mul(bh, M), 1.0, 1.0, nrm)
    h = p.get('height', 0.0)
    cav = p.get('cavity', 0.0)
    _finish_group(nb, go, dict(color=col, rough=rough, height=h, cavity=cav, metal=p.get('metal', 0.0), normal=nrm))
    g['bl_kind'] = 'detail'
    g['bl_folder'] = folder
    mat.node_tree.nodes['SURF'].node_tree = g
    mat['bl_source'] = 'detail:' + folder
    return mat


def use_riverbank_scans(pebbles, mud, name='Riverbank', water_z=-1.8, peb_opts=None, mud_opts=None):
    """Riverbank terrain with scanned pebbles (under / at the waterline) and scanned mud (slopes);
    procedural grass on top (no grass scan in the pack)."""
    mat = get(name)
    g, gi, go = _new_group('BLI ' + name, [], SURF_OUT)
    nb = NB(g)
    co = Co(nb)
    P = co.P
    px, py, pz = nb.sep(nb.vscale(nb.texco('Object'), 1.0 / M))
    gr = s_grass(nb, co)
    m = _img_surface(nb, co, mud, 3.0, True, **(mud_opts or {}))
    pb = _img_surface(nb, co, pebbles, 2.0, True, **(peb_opts or {}))
    n = nb.noise(P, 0.7, 4, 0.6)
    nz = nb.sep(nb.geo('Normal'))[2]
    hrel = nb.sub(pz, water_z)
    peb = nb.inv(nb.smooth(nb.add(hrel, nb.mul(nb.sub(n, 0.5), 0.8)), 0.15, 0.55))
    grass = nb.mul(nb.smooth(nb.add(hrel, nb.mul(nb.sub(n, 0.5), 1.0)), 1.1, 1.6), nb.smooth(nz, 0.75, 0.9))
    col = nb.mix(peb, m['color'], pb['color'])
    col = nb.mix(grass, col, gr['color'])
    rough = nb.mixf(peb, m['rough'], pb['rough'])
    rough = nb.mixf(grass, rough, gr['rough'])
    h = nb.mixf(peb, m['height'], pb['height'])
    h = nb.mixf(grass, h, nb.mul(gr['height'], 0.6))
    wet = nb.inv(nb.smooth(hrel, 0.0, 0.35))
    col = nb.mix(nb.mul(wet, 0.6), col, nb.cmul(col, (0.55, 0.55, 0.55)))
    rough = nb.mixf(wet, rough, nb.mul(rough, 0.4))
    cav = nb.mixf(peb, m['cavity'], pb['cavity'])
    nrm = nb.vmath('NORMALIZE', nb.mix(grass, nb.mix(peb, m['normal'], pb['normal'], 'VECTOR'), nb.geo('Normal'), 'VECTOR'))
    _finish_group(nb, go, dict(color=col, rough=rough, height=h, cavity=cav, normal=nrm))
    g['bl_kind'] = 'images'
    g['bl_folder'] = pebbles + ';' + mud
    mat.node_tree.nodes['SURF'].node_tree = g
    mat['bl_source'] = g['bl_folder']
    return mat


def use_procedural(name):
    mat = get(name)
    g = bpy.data.node_groups.get('BLS ' + name) or _surface_group(name, REG[name])
    mat.node_tree.nodes['SURF'].node_tree = g
    mat['bl_source'] = 'procedural'
    return mat


def use_scan(name):
    """Switch back to the scan group built earlier (BLI <name>), if the file has one."""
    mat = get(name)
    g = bpy.data.node_groups.get('BLI ' + name)
    if g is None:
        return None
    mat.node_tree.nodes['SURF'].node_tree = g
    mat['bl_source'] = g.get('bl_folder', 'images')
    return mat


# Curated picks for the In This Town CC0 pack (folder names from its SOURCES.md).  Chosen by test renders
# with Cast v2 characters on the marks at phone size; see BACKLOT.md.  mode 'image' = full scan,
# 'detail' = procedural layout + scan detail, 'riverbank' = special blend.  Materials not listed stay
# procedural (their scans were worse in the renders, or no scan fits).
CC0_PICKS = {
    'Cobbles': ('image', 'cobblestone_02', dict(coords='xy', tile_m=1.15, disp_m=0.04, val=1.05, macro=0.15, puddles=1.0)),
    'Cobbles Dry': ('image', 'cobblestone_02', dict(coords='xy', tile_m=1.3, disp_m=0.035, macro=0.15)),
    'Flagstones': ('image', 'worn_flagstone', dict(coords='xy', tile_m=2.6, disp_m=0.02, desat=0.4, tint=(0.3, 0.28, 0.25), macro=0.12)),
    'Dirt': ('image', 'dirt_path', dict(coords='xy', tile_m=3.0, disp_m=0.03, anti='rot', val=1.9)),
    'Forest Floor': ('image', 'forest_floor', dict(coords='xy', tile_m=2.6, disp_m=0.025, anti='rot', desat=0.25, val=0.75)),
    'Ashlar': ('image', 'ashlar_blocks', dict(tile_m=2.0, tint=(0.42, 0.36, 0.27), normal_strength=1.2, cav_disp=0.8)),
    'Ashlar Grey': ('image', 'ashlar_blocks', dict(tile_m=2.0, desat=0.45, tint=(0.3, 0.3, 0.28), normal_strength=1.2, cav_disp=0.8)),
    'Ashlar Bridge': ('image', 'ashlar_blocks', dict(tile_m=2.0, desat=0.45, tint=(0.3, 0.3, 0.28), normal_strength=1.2, cav_disp=0.8)),
    'Limestone': ('image', 'ashlar_blocks', dict(tile_m=1.6, desat=0.3, tint=(0.64, 0.59, 0.49), normal_strength=0.8, cav_disp=0.4)),
    'Brick': ('image', 'old_brick', dict(tile_m=2.6)),
    'Rubble': ('image', 'mossy_stone', dict(tile_m=2.2, val=2.2)),
    'Plaster Cream': ('detail', 'aged_white_plaster', dict(tile_m=2.4, anti='rot')),
    'Plaster Ochre': ('detail', 'aged_white_plaster', dict(tile_m=2.4, anti='rot')),
    'Plaster Rose': ('detail', 'aged_white_plaster', dict(tile_m=2.4, anti='rot')),
    'Plaster White': ('detail', 'aged_white_plaster', dict(tile_m=2.4, anti='rot')),
    'Plaster Sage': ('detail', 'aged_white_plaster', dict(tile_m=2.4, anti='rot')),
    'Plaster Blue': ('detail', 'aged_white_plaster', dict(tile_m=2.4, anti='rot')),
    'Timber Dark': ('image', 'half_timber_beams', dict(tile_m=1.6, rot90=True, islands=True, desat=0.5, tint=(0.075, 0.05, 0.033))),
    'Timber Oak': ('image', 'half_timber_beams', dict(tile_m=1.6, rot90=True, islands=True, desat=0.5, tint=(0.2, 0.135, 0.08))),
    'Planks': ('image', 'weathered_planks', dict(tile_m=1.9, rot90=True, islands=True, val=1.6)),
    'Planks Grey': ('image', 'half_timber_beams', dict(tile_m=1.8, rot90=True, islands=True)),
    'Planks Pale': ('image', 'weathered_planks', dict(tile_m=1.9, rot90=True, islands=True, desat=0.3, tint=(0.32, 0.23, 0.14))),
    'Roof Clay': ('image', 'clay_roof_tiles', dict(tile_m=3.0, disp_m=0.03, desat=0.3, tint=(0.42, 0.17, 0.08))),
    'Roof Clay Old': ('image', 'clay_roof_tiles', dict(tile_m=3.0, disp_m=0.03, desat=0.45, tint=(0.3, 0.15, 0.085))),
    'Roof Slate': ('image', 'slate_roof_shingles', dict(tile_m=3.0, disp_m=0.02, desat=0.8, tint=(0.085, 0.09, 0.105))),
    'Roof Shingle': ('image', 'slate_roof_shingles', dict(tile_m=2.6, disp_m=0.02, desat=0.5, tint=(0.2, 0.17, 0.13))),
    'Bark': ('image', 'tree_bark', dict(tile_m=1.0, rot90=True, islands=True, val=1.3)),
    'Riverbank': ('riverbank', ('river_pebbles', 'wet_mud'), dict(peb=dict(coords='xy', tile_m=1.6, anti='rot', val=1.0),
                                                                 mud=dict(coords='xy', tile_m=3.0, anti='rot', val=1.6))),
}


# Scans in the In This Town pack that were tried and lost to the procedural material (test renders,
# Cast v2 on the marks, phone size), plus pack folders with no matching surface in the sets.
CC0_KEEP_PROCEDURAL = {
    'Gold': 'worn_gold: duller, spotty brass at phone size; the procedural gold reads as royal gold',
    'Velvet Red': 'red_velvet: flat pink-red; no visible gain on the drapes, costs texture memory',
    'Marble Floor': 'marble_floor is small grey tiles; the hall needs the big black/cream checker',
    'Carpet Royal': 'old_carpet is a dark dirty rug; the royal runner needs its gold border',
    'Iron': 'rusty_iron is pale painted sheet with rust blooms; wrong for black iron fittings',
    'Grass': 'no grass scan (forest_floor is autumn leaves)',
    'Rock': 'boulders have no good UVs for a wall scan; procedural 3D rock kept',
    'Stone Drums': 'pillar drums need the drum courses that match the geometry',
    'Ashlar Hall / Plaster Hall (+ Limestone in the hall)': 'ashlar scan made the throne hall dark and blotchy; '
                                                            'the clean pale procedural masonry reads royal',
    'Thatch / Rope / Canvas Plain': 'thatch, rope and burlap are not visible in any camera of the three sets',
}


def reset_scans(root=None):
    """Put every scanned material back to procedural, drop the BLI groups and the scan images (all, or the
    ones under `root`), so a re-apply starts clean (re-applying on top of loaded scan images left Cycles
    sampling them as flat colour)."""
    for mat in bpy.data.materials:
        if mat.node_tree and 'SURF' in mat.node_tree.nodes:
            g = mat.node_tree.nodes['SURF'].node_tree
            if g is not None and g.name.startswith('BLI ') and mat.get('bl_lib') in REG:
                use_procedural(mat['bl_lib'])
    for g in [g for g in bpy.data.node_groups if g.name.startswith('BLI ')]:
        bpy.data.node_groups.remove(g)
    r = os.path.abspath(root) if root else None
    for img in list(bpy.data.images):
        if img.source != 'FILE' or img.packed_file:
            continue
        fp = os.path.abspath(bpy.path.abspath(img.filepath))
        if (r and fp.startswith(r + os.sep)) or (not r and img.users == 0):
            bpy.data.images.remove(img)


def apply_picks(root, picks=None, names=None, log=print):
    """Apply CC0_PICKS (or `picks`) for every listed material present in the open file whose folder exists
    under `root`.  Returns {material: folder}."""
    picks = picks if picks is not None else CC0_PICKS
    done = {}
    for name, (mode, folder, opts) in picks.items():
        if names is not None and name not in names:
            continue
        if bpy.data.materials.get(PREFIX + name) is None:
            continue
        try:
            if mode == 'riverbank':
                pf, mf = (os.path.join(root, f) for f in folder)
                if not (os.path.isdir(pf) and os.path.isdir(mf)):
                    continue
                use_riverbank_scans(pf, mf, name, peb_opts=opts.get('peb'), mud_opts=opts.get('mud'))
                done[name] = '+'.join(folder)
            else:
                fd = os.path.join(root, folder)
                if not os.path.isdir(fd):
                    continue
                (use_detail_set if mode == 'detail' else use_image_set)(name, fd, **opts)
                done[name] = folder
            log('scan: %s <- %s (%s)' % (name, done[name], mode))
        except Exception as e:
            log('scan failed %s: %s' % (name, e))
    return done


def auto_image_sets(root='/mnt/user-data/uploads/textures/cc0', only_existing=True, log=print):
    """Match sub-folders of `root` to library materials and switch them.  Folders named in CC0_PICKS use the
    curated settings; other packs fall back to keyword matching (REG[...]['keys']).  Returns {material: folder}."""
    done = {}
    if not os.path.isdir(root):
        return done
    names = set(os.listdir(root))
    curated = {n: p for n, p in CC0_PICKS.items()
               if all(f in names for f in (p[1] if isinstance(p[1], tuple) else (p[1],)))}
    done.update(apply_picks(root, curated, log=log))
    if curated:
        # the curated pack: materials not in CC0_PICKS stay procedural on purpose (CC0_KEEP_PROCEDURAL)
        return done
    folders = [d for d in glob.glob(os.path.join(root, '**'), recursive=True)
               if os.path.isdir(d) and os.path.basename(d.rstrip('/')) and find_maps(d).get('color')]
    for name, spec in REG.items():
        if name in done or name in curated:
            continue
        if only_existing and bpy.data.materials.get(PREFIX + name) is None:
            continue
        for kw in spec['keys']:
            hit = sorted([d for d in folders if os.path.basename(d.rstrip('/')).lower() == kw or
                          os.path.basename(d.rstrip('/')).lower().startswith(kw + '_') or
                          ('_' + kw) in os.path.basename(d.rstrip('/')).lower()], key=len)
            if hit:
                try:
                    use_image_set(name, hit[0])
                    done[name] = hit[0]
                    log('image set: %s <- %s' % (name, hit[0]))
                except Exception as e:
                    log('image set failed %s: %s' % (name, e))
                break
    return done


def find_hdri(root='/mnt/user-data/uploads/textures/cc0'):
    out = []
    for ext in ('*.hdr', '*.exr'):
        out += glob.glob(os.path.join(root, '**', ext), recursive=True)
    return [f for f in out if 'hdri' in f.lower() or 'sky' in f.lower() or f.lower().endswith('.hdr')]
