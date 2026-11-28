# Lightning Arms: LA_IronCrown, LA_GateChains, LA_StoneArms, LA_IronArms, LA_WristNumbers, LA_SkyNumber.
from la_lib import *
import la_gate as G

KID = dict(w=0.80, d=0.80, top=0.16, bottom=-1.464, hand=-1.064)            # Cast v2 Hero kid arm (world BU, shoulder pivot frame)
VIL = dict(w=0.84, d=0.945, top=0.21, bottom=-2.551, hand=-2.026)           # Cast v2 Villain arm
NUMS = [('2', ['1 IN 2']), ('1M', ['1 IN', '1,000,000']), ('10M', ['1 IN', '10,000,000'])]
SKY_ROWS = ['1 IN', '847,362,951,406,', '283,715,069,524']


# ====================================================================================================== iron crown
def build_crown(root):
    """heavy dark spiked iron crown for the Cast v2 Villain (head 1.2 wide, hair to 1.57 wide). Origin: centre of its base ring."""
    C = coll('LA_IronCrown', root)
    iron = metal('CrownIron', '#3B3F4C', rough=0.38, metallic=0.9)
    edge = metal('CrownIronWorn', '#8E96A8', rough=0.3, metallic=1.0)
    gem = mat('CrownGem', '#B01226', 0.12, emit='#FF2A3A', estr=0.8, vcol=False)
    mb = MB()
    n = 8; ap = 0.88; th = 0.16; bh = 0.46
    side = 2 * (ap + th) * math.tan(math.pi / n) + 0.02
    rng = random.Random(4)
    for i in range(n):
        a = 2 * math.pi * i / n - math.pi / 2                     # i = 0 is the front (-Y)
        M = Matrix.Rotation(a + math.pi / 2, 4, 'Z')              # local -Y -> outward
        fr = i == 0
        v, f = tbox((side, th, bh), (0, -(ap + th / 2), bh / 2), 0.035, 2); mb.add(xf(v, M), f, 0, col=(rng.uniform(0.82, 1.0),) * 3)
        for z in (0.045, bh - 0.045):                              # worn rims
            v, f = tbox((side + 0.03, th + 0.07, 0.09), (0, -(ap + th / 2), z), 0.02, 1); mb.add(xf(v, M), f, 1)
        hgt = 1.25 if fr else (0.95 if i % 2 == 0 else 0.62)
        wd = 0.46 if fr else (0.38 if i % 2 == 0 else 0.3)
        v, f = tbox((wd, th * 1.1, hgt), (0, -(ap + th / 2), bh + hgt / 2 - 0.04), 0.02, 1, taper=(0.06, 0.45), rot=EU(-9, 0, 0))   # spike, leaning out a little
        mb.add(xf(v, M), f, 0, col=(rng.uniform(0.85, 1.0),) * 3, shade=None)
        v, f = tbox((wd * 0.3, th * 1.25, hgt * 0.8), (0, -(ap + th / 2) - 0.012, bh + hgt * 0.4), 0.01, 1, taper=(0.1, 0.5), rot=EU(-9, 0, 0))
        mb.add(xf(v, M), f, 1)                                     # bright ridge down each spike
        for sx in (-1, 1):                                         # rivets
            v, f = ico(1); mb.add(xf(v * 0.055 + np.array((sx * side * 0.33, -(ap + th + 0.03), bh / 2)), M), f, 1)
        if fr:
            v, f = tbox((0.34, 0.12, 0.34), (0, -(ap + th + 0.05), bh / 2), 0.05, 2, rot=EU(0, 45, 0)); mb.add(xf(v, M), f, 2, flat=True)
            v, f = tbox((0.46, 0.08, 0.46), (0, -(ap + th + 0.01), bh / 2), 0.04, 1, rot=EU(0, 45, 0)); mb.add(xf(v, M), f, 1)
    o = mb.obj('LA_IronCrown', [iron, edge, gem], C, sharp=35)
    o.location = (0, 0, 0)
    return {'crown': {'inner_apothem': ap, 'outer_width': round(2 * (ap + th), 2), 'height': 1.71, 'on_villain_z': 6.38,
                      'note': 'on the Cast v2 Villain (root scale 1.05): crown origin at the head centre, 6.38 above his feet'}}


# ====================================================================================================== chains
CH = dict(L=1.5, W=0.95, r=0.2)


def cuff_big(mb, c, inner=(1.0, 1.1), h=0.62, t=0.2, M=None, rune_i=0, open_=False, w=None):
    """a rune-carved iron cuff (square, to fit a blocky wrist), axis Z, centred on c. mats: 0 iron, 1 rune."""
    ix, iy = inner[0] / 2, inner[1] / 2
    P = []
    if open_:
        sides = [((2 * ix + 2 * t, t, h), (0, iy + t / 2, 0), 0), ((t, 2 * iy + 2 * t, h), (-ix - t / 2 - 0.25, -0.1, 0), -24), ((t, 2 * iy + 2 * t, h), (ix + t / 2 + 0.25, -0.1, 0), 24)]
    else:
        sides = [((2 * ix + 2 * t, t, h), (0, -iy - t / 2, 0), 0), ((2 * ix + 2 * t, t, h), (0, iy + t / 2, 0), 0),
                 ((t, 2 * iy + 2 * t, h), (-ix - t / 2, 0, 0), 0), ((t, 2 * iy + 2 * t, h), (ix + t / 2, 0, 0), 0)]
    for sz, cc, rz in sides:
        v, f = tbox(sz, (0, 0, 0), 0.05, 2)
        P.append((xf(v, Matrix.Translation(cc) @ EU(0, 0, rz)), f))
    v, f = merge(P)
    Mx = Matrix.Translation(Vector(c)) @ (M or Matrix())
    mb.add(xf(v, Mx), f, 0, w=w)
    if not open_:
        for k, (rz, off) in enumerate(((0, iy + t), (180, iy + t), (90, ix + t), (270, ix + t))):
            rv, rf = rune_glyph(rune_i + k, h * 0.66, t=0.2, depth=0.04)
            Mr = Mx @ EU(0, 0, rz) @ Matrix.Translation((0, -off - 0.012, 0))
            mb.add(xf(rv, Mr), rf, 1, flat=True, w=w)


def chain_mats():
    iron = metal('ChainIron', '#565D6E', rough=0.42, metallic=0.9)
    rune = attr_mat('ChainRune', '#FFB23A', 14.0, attr='glow', base_hex='#7A5A2A', floor=0.0)
    return iron, rune


def build_chains(root):
    C = coll('LA_GateChains', root)
    iron, rune = chain_mats()
    YF = G.YF
    # --- hanging on the gate (gate at the origin)
    mb = MB()
    for s in (-1, 1):
        top = (s * 9.7, YF - 1.25, G.Z_SH + 0.4)
        end = (s * 10.9, YF - 1.7, 5.2)
        chain(mb, [top, (s * 10.6, YF - 1.75, 17.5), (s * 10.85, YF - 1.75, 11.0), end], rune_mat=1, **CH)
        cuff_big(mb, (end[0], end[1], end[2] - 0.95), open_=False, rune_i=3 * (s > 0), M=EU(0, 0, s * 18))
        v, f = tbox((1.1, 1.0, 1.0), (top[0] - s * 0.1, YF - 0.6, top[2] + 0.1), 0.12, 2); mb.add(v, f, 0)          # iron staple in the cornice
    # swags across the opening, front and back
    for (y, sag) in ((YF - 0.75, 4.6), (-YF + 0.75, 3.6)):
        chain(mb, catenary((-6.3, y, 13.9), (6.3, y, 13.9), sag, 16), rune_mat=1, **CH)
        for s in (-1, 1):
            v, f = tbox((1.0, 0.9, 1.0), (s * 6.4, y + (0.3 if y < 0 else -0.3), 14.0), 0.12, 2); mb.add(v, f, 0)
    hang = mb.obj('LA_GateChains_Hanging', [iron, rune], C, sharp=50)
    prop(hang, 'glow', 0.35, 'rune glow: 0 = dark iron, 1 = blazing')
    # --- lashed out: from the shoulder corners to two closed cuffs round the Villain's wrists.
    # Standard layout: gate at the origin, Villain standing on LA_GateChains_Mark_Villain (0, -12, 0) facing -Y, arms hanging.
    VX, VY = 1.31, -12.0
    wz = 5.25 + VIL['hand'] + 0.27                                 # cuff centre: just above the hand
    mb = MB()
    for s in (-1, 1):
        top = (s * 9.7, YF - 1.25, G.Z_SH + 0.4)
        wr = (s * VX, VY, wz)
        ring = (s * (VX + 0.2), VY + 0.9, wz + 0.25)
        chain(mb, catenary(top, ring, 1.6, 14), rune_mat=1, **CH)
        v, f = tbox((1.1, 1.0, 1.0), (top[0] - s * 0.1, YF - 0.6, top[2] + 0.1), 0.12, 2); mb.add(v, f, 0)
    lash = mb.obj('LA_GateChains_Lashed', [iron, rune], C, sharp=50)
    prop(lash, 'glow', 1.0, 'rune glow'); lash.hide_render = lash.hide_viewport = True
    for s, sd in ((-1, 'L'), (1, 'R')):
        cb = MB(); cuff_big(cb, (0, 0, 0), inner=(VIL['w'] + 0.24, VIL['d'] + 0.24), h=0.5, rune_i=5 * (s > 0))
        v, f = tbox((0.5, 0.42, 0.5), (0, (VIL['d'] + 0.24) / 2 + 0.36, 0), 0.08, 2); cb.add(v, f, 0)                  # lug the chain bites on (+Y = behind him)
        co = cb.obj('LA_GateChains_Cuff_' + sd, [iron, rune], C, sharp=50)
        prop(co, 'glow', 1.0, 'rune glow'); co.location = (s * VX, VY, wz); co.hide_render = co.hide_viewport = True
    empty('LA_GateChains_Mark_Villain', C, (0, VY, 0), 'ARROWS', 1.5)
    for s, sd in ((-1, 'R'), (1, 'L')):
        empty('LA_GateChains_Anchor' + sd, C, (s * 9.7, YF - 1.25, G.Z_SH + 0.4), 'SPHERE', 0.5)
    lb = MB(); v, f = link_proto(**CH); lb.add(v, f, 0)
    rv, rf = rune_glyph(2, CH['L'] * 0.36)
    for sx, rz in ((1, 90), (-1, -90)):
        lb.add(xf(rv, Matrix.Translation((sx * (CH['W'] / 2 - CH['r']), 0, 0)) @ EU(0, 0, rz) @ Matrix.Translation((0, -CH['r'] - 0.015, 0))), rf, 1, flat=True)
    lk = lb.obj('LA_GateChain_Link', [iron, rune], C); lk.location = (0, 0, -4); lk.hide_render = lk.hide_viewport = True
    lk['link_step'] = CH['L'] - 2 * CH['r'] * 1.55; prop(lk, 'glow', 1.0, 'rune glow')
    return {'gate_chains': {'villain_mark': [0, VY, 0], 'cuff_centre_z_above_feet': round(wz, 2), 'cuff_z_in_arm_frame': round(VIL['hand'] + 0.27, 3)}}


# ====================================================================================================== arm shells with a `stone` creep
def creep_mat(name, under, stone_hex='#A2A6AE', edge_hex='#FFB23A', edge_strength=9.0):
    """material for arm shells: below the creep line it is grey stone, above it `under` ('clear' = see-through, or a function that
    fills a Principled BSDF: dark iron). The line is where the mesh attribute `creep` (0 at the hand, 1 at the shoulder)
    equals the OBJECT property `stone`; it wobbles with a noise and glows a little while it moves."""
    full = 'LA_Mat_' + name
    m = bpy.data.materials.get(full)
    if m:
        return m
    m = bpy.data.materials.new(full); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    N = nt.nodes.new; L = nt.links.new
    out = N('ShaderNodeOutputMaterial'); out.location = (900, 0)
    at = N('ShaderNodeAttribute'); at.attribute_type = 'OBJECT'; at.attribute_name = 'stone'; at.name = at.label = 'LA_STONE'; at.location = (-900, 300)
    cr = N('ShaderNodeAttribute'); cr.attribute_type = 'GEOMETRY'; cr.attribute_name = 'creep'; cr.location = (-900, 100)
    rs = N('ShaderNodeAttribute'); rs.attribute_type = 'GEOMETRY'; rs.attribute_name = 'rest'; rs.location = (-900, -150)
    nz = N('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 3.2; nz.inputs['Detail'].default_value = 3.0; nz.location = (-700, -150)
    L(rs.outputs['Vector'], nz.inputs['Vector'])
    wob = N('ShaderNodeMath'); wob.operation = 'MULTIPLY_ADD'; wob.inputs[1].default_value = 0.22; wob.inputs[2].default_value = -0.11; wob.location = (-500, -100)
    L(nz.outputs['Fac'], wob.inputs[0])
    h = N('ShaderNodeMath'); h.operation = 'ADD'; h.location = (-320, 60); L(cr.outputs['Fac'], h.inputs[0]); L(wob.outputs[0], h.inputs[1])
    th = N('ShaderNodeMath'); th.operation = 'MULTIPLY_ADD'; th.inputs[1].default_value = 1.26; th.inputs[2].default_value = -0.13; th.location = (-500, 300)
    L(at.outputs['Fac'], th.inputs[0])
    lt = N('ShaderNodeMath'); lt.operation = 'LESS_THAN'; lt.location = (-120, 200); L(h.outputs[0], lt.inputs[0]); L(th.outputs[0], lt.inputs[1])
    # glowing rim just under the line
    df = N('ShaderNodeMath'); df.operation = 'SUBTRACT'; df.location = (-120, 0); L(th.outputs[0], df.inputs[0]); L(h.outputs[0], df.inputs[1])
    rim = N('ShaderNodeMapRange'); rim.location = (60, 0); rim.inputs['From Min'].default_value = 0.0; rim.inputs['From Max'].default_value = 0.07
    rim.inputs['To Min'].default_value = edge_strength; rim.inputs['To Max'].default_value = 0.0
    L(df.outputs[0], rim.inputs['Value'])
    # no rim once the arm is all stone (stone >= 0.98) or untouched
    full_ = N('ShaderNodeMath'); full_.operation = 'LESS_THAN'; full_.inputs[1].default_value = 0.985; full_.location = (60, -200); L(at.outputs['Fac'], full_.inputs[0])
    rim2 = N('ShaderNodeMath'); rim2.operation = 'MULTIPLY'; rim2.location = (240, -60); L(rim.outputs['Result'], rim2.inputs[0]); L(full_.outputs[0], rim2.inputs[1])
    st = N('ShaderNodeBsdfPrincipled'); st.location = (300, 250)
    st.inputs['Roughness'].default_value = 0.92; st.inputs['Specular IOR Level'].default_value = 0.2
    vc = N('ShaderNodeVertexColor'); vc.layer_name = 'Col'; vc.location = (-300, 500)
    nz2 = N('ShaderNodeTexNoise'); nz2.inputs['Scale'].default_value = 5.0; nz2.inputs['Detail'].default_value = 6.0; nz2.location = (-500, 600); L(rs.outputs['Vector'], nz2.inputs['Vector'])
    mr = N('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = 0.3; mr.inputs['From Max'].default_value = 0.7; mr.inputs['To Min'].default_value = 0.8; mr.inputs['To Max'].default_value = 1.08; mr.location = (-300, 650)
    L(nz2.outputs['Fac'], mr.inputs['Value'])
    mx = N('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = 1.0; mx.inputs['A'].default_value = (*lin(stone_hex), 1); mx.location = (-100, 500)
    L(vc.outputs['Color'], mx.inputs['B'])
    mx2 = N('ShaderNodeMix'); mx2.data_type = 'RGBA'; mx2.blend_type = 'MULTIPLY'; mx2.inputs['Factor'].default_value = 1.0; mx2.location = (100, 500)
    L(mx.outputs['Result'], mx2.inputs['A']); L(mr.outputs['Result'], mx2.inputs['B']); L(mx2.outputs['Result'], st.inputs['Base Color'])
    bp = N('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.35; bp.inputs['Distance'].default_value = 0.08; bp.location = (100, 250)
    L(nz2.outputs['Fac'], bp.inputs['Height']); L(bp.outputs['Normal'], st.inputs['Normal'])
    st.inputs['Emission Color'].default_value = (*lin(edge_hex), 1); L(rim2.outputs[0], st.inputs['Emission Strength'])
    if under == 'clear':
        un = N('ShaderNodeBsdfTransparent'); un.location = (300, -250)
        try:
            m.surface_render_method = 'DITHERED'
        except Exception:
            pass
    else:
        un = N('ShaderNodeBsdfPrincipled'); un.location = (300, -250)
        vc2 = N('ShaderNodeVertexColor'); vc2.layer_name = 'Col'; vc2.location = (-100, -400)
        mx3 = N('ShaderNodeMix'); mx3.data_type = 'RGBA'; mx3.blend_type = 'MULTIPLY'; mx3.inputs['Factor'].default_value = 1.0; mx3.inputs['A'].default_value = (*lin(under['hex']), 1); mx3.location = (100, -400)
        L(vc2.outputs['Color'], mx3.inputs['B']); L(mx3.outputs['Result'], un.inputs['Base Color'])
        un.inputs['Metallic'].default_value = under.get('metallic', 0.9); un.inputs['Roughness'].default_value = under.get('rough', 0.36)
    mix = N('ShaderNodeMixShader'); mix.location = (650, 0)
    L(lt.outputs[0], mix.inputs[0]); L(un.outputs[0], mix.inputs[1]); L(st.outputs[0], mix.inputs[2])
    L(mix.outputs[0], out.inputs['Surface'])
    m.diffuse_color = (*lin(stone_hex), 1)
    return m


def add_creep(o, bottom, top):
    me = o.data
    a = me.attributes.new('creep', 'FLOAT', 'POINT')
    co = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get('co', co)
    z = co.reshape(-1, 3)[:, 2]
    a.data.foreach_set('value', np.clip((z - bottom) / (top - bottom), 0, 1))


def arm_shell(A, kind, seed, grow=0.05):
    """blocky arm shell round a Cast v2 arm box A. kind 'stone' (rough chiselled blocks) or 'iron' (plates, gauntlet, rivets)."""
    mb = MB(); rng = random.Random(seed)
    w, d = A['w'] + 2 * grow, A['d'] + 2 * grow
    top, bot, hand = A['top'] + grow, A['bottom'] - grow, A['hand']
    elbow = top - (top - hand) * 0.52
    if kind == 'stone':
        for i, (z0, z1, k, c) in enumerate(((elbow - 0.02, top, 1.0, 0.95), (hand - 0.03, elbow + 0.03, 0.94, 1.0), (bot, hand + 0.02, 1.1, 0.86))):
            v, f = crag((w * k, d * k, z1 - z0), (0, 0, (z0 + z1) / 2), seed=seed * 5 + i, sub=3, amp=0.035, cuts=4, depth=(0.86, 0.97), rnd=0.05)
            mb.add(v, f, 0, col=rockcol((c,) * 3, seed + i, scale=1.6, amp=0.12), flat=True, fjit=0.1)
        for k in range(3):                                         # finger grooves on the fist front
            x = (k - 1) * w * 0.27
            v, f = box((0.035, 0.05, (hand - bot) * 0.7), (x, -d * 0.555, (hand + bot) / 2 - 0.02)); mb.add(v, f, 0, col=(0.35,) * 3, flat=True)
    else:
        v, f = tbox((w, d, top - elbow + 0.04), (0, 0, (top + elbow) / 2), 0.07, 2); mb.add(v, f, 0, col=(0.9,) * 3)             # upper plate
        v, f = tbox((w * 1.14, d * 1.12, 0.3), (0, 0, top - 0.1), 0.08, 2); mb.add(v, f, 0, col=(0.7,) * 3)                      # shoulder cap
        v, f = tbox((w * 1.03, d * 1.03, 0.16), (0, 0, elbow), 0.05, 2); mb.add(v, f, 0, col=(0.62,) * 3)                        # elbow band
        v, f = tbox((w * 0.95, d * 0.95, elbow - hand + 0.04), (0, 0, (elbow + hand) / 2), 0.06, 2); mb.add(v, f, 0, col=(1.0,) * 3)
        v, f = tbox((w * 1.1, d * 1.1, 0.2), (0, 0, hand + 0.12), 0.05, 2); mb.add(v, f, 0, col=(0.66,) * 3)                     # gauntlet cuff
        v, f = tbox((w * 1.12, d * 1.1, hand - bot + 0.02), (0, 0, (hand + bot) / 2), 0.1, 2); mb.add(v, f, 0, col=(0.82,) * 3)  # gauntlet fist
        for k in range(4):                                         # knuckle plates
            x = (k - 1.5) * w * 0.26
            v, f = tbox((w * 0.2, 0.09, 0.2), (x, -d * 0.575, bot + 0.2), 0.03, 1); mb.add(v, f, 0, col=(1.6,) * 3)
        for z in (top - 0.1, elbow, hand + 0.12):                  # rivets
            for sx in (-1, 1):
                for sy in (-1, 1):
                    v, f = ico(1); mb.add(v * 0.05 + np.array((sx * w * 0.36, sy * d * 0.57, z)), f, 0, col=(1.9,) * 3)
        for i in range(2):                                         # ridge down the front of the forearm and upper arm
            z0, z1 = ((hand + 0.25, elbow - 0.12), (elbow + 0.12, top - 0.3))[i]
            v, f = tbox((0.12, 0.08, z1 - z0), (0, -d * (0.5 if i == 0 else 0.52) - 0.0, (z0 + z1) / 2), 0.03, 1); mb.add(v, f, 0, col=(1.5,) * 3)
    return mb, bot, top


def build_shells(root):
    info = {}
    stone_clear = creep_mat('ArmStone', 'clear')
    stone_iron = creep_mat('ArmIronToStone', dict(hex='#414857', metallic=0.9, rough=0.36))
    Cs = coll('LA_StoneArms', root); Ci = coll('LA_IronArms', root)
    for (who, A, C, kind, m, x0, z0) in (('Kid', KID, Cs, 'stone', stone_clear, 1.2, 3.04), ('Villain', VIL, Cs, 'stone', stone_clear, 1.31, 5.25),
                                         ('Villain', VIL, Ci, 'iron', stone_iron, 1.31, 5.25)):
        for sd, s in (('L', -1), ('R', 1)):
            mb, bot, top = arm_shell(A, kind, seed=(3 if sd == 'L' else 8) + (20 if who == 'Kid' else 0), grow=0.05 if kind == 'stone' else 0.045)
            name = f"LA_{'StoneArm' if kind == 'stone' else 'IronArm'}_{who}_{sd}"
            o = mb.obj(name, [m], C, sharp=40)
            add_creep(o, bot, top)
            prop(o, 'stone', 1.0 if kind == 'stone' else 0.0, 'how far the stone has crept up the arm: 0 = none, 1 = the whole arm')
            off = 0.0 if C is Ci else (0.0 if who == 'Kid' else 4.0)
            o.location = (s * x0 + off, 0, z0)
            info[name] = [round(float(x), 2) for x in o.dimensions]
    return {'arm_shells': info}


# ====================================================================================================== wrist numbers, sky number
def number_block(lines, width, height, depth=0.03):
    """one or two centred lines of text fitted into width x height. Stands in XZ facing -Y, front at y = -depth."""
    P = []
    n = len(lines)
    lh = height / n
    for i, t in enumerate(lines):
        v, f = text_mesh(t, 1.0, depth)
        wd = v[:, 0].max() - v[:, 0].min(); ht = v[:, 2].max() - v[:, 2].min()
        k = min(width / wd, (lh * (0.9 if n == 1 else 0.86)) / ht)
        if n == 2 and i == 0:
            k *= 0.8
        v[:, 0] = (v[:, 0] - (v[:, 0].max() + v[:, 0].min()) / 2) * k
        v[:, 2] = (v[:, 2] - (v[:, 2].max() + v[:, 2].min()) / 2) * k + (height / 2 - lh * (i + 0.5)) * (1.0 if n == 1 else 0.96)
        P.append((v, f))
    return merge(P)


def build_bands(root):
    C = coll('LA_WristNumbers', root)
    char = mat('BandChar', '#1F1A1B', 0.85, vcol=False)
    ember = attr_mat('BandEmber', '#FF6A1A', 5.0, attr='glow', base_hex='#5A2A12', floor=0.0)
    num = attr_mat('BandNumber', '#FFB040', 9.0, attr='glow', base_hex='#FFD9A0', floor=0.0)
    info = {}
    for (who, A, x0, z0) in (('Kid', KID, 1.2, 3.04), ('Villain', VIL, 1.31, 5.25)):
        inx = A['w'] + 0.14; iny = A['d'] + 0.14; t = 0.05
        h = 0.56 if who == 'Kid' else 0.66
        h = 0.56
        zc = A['hand'] + (0.06 if who == 'Kid' else 0.56) + h / 2
        for sd, s in (('L', -1), ('R', 1)):
            mb = MB()
            for (sz, cc) in (((inx + 2 * t, t, h), (0, -iny / 2 - t / 2, zc)), ((inx + 2 * t, t, h), (0, iny / 2 + t / 2, zc)),
                             ((t, iny + 2 * t, h), (-inx / 2 - t / 2, 0, zc)), ((t, iny + 2 * t, h), (inx / 2 + t / 2, 0, zc))):
                v, f = tbox(sz, cc, 0.015, 1); mb.add(v, f, 0)
            for z in (zc - h / 2, zc + h / 2):                      # ember edges
                for (sz, cc) in (((inx + 2 * t + 0.03, t + 0.03, 0.035), (0, -iny / 2 - t / 2, z)), ((inx + 2 * t + 0.03, t + 0.03, 0.035), (0, iny / 2 + t / 2, z)),
                                 ((t + 0.03, iny + 2 * t + 0.03, 0.035), (-inx / 2 - t / 2, 0, z)), ((t + 0.03, iny + 2 * t + 0.03, 0.035), (inx / 2 + t / 2, 0, z))):
                    v, f = box(sz, cc); mb.add(v, f, 1, flat=True)
            name = f'LA_WristBand_{who}_{sd}'
            o = mb.obj(name, [char, ember], C, sharp=40)
            prop(o, 'glow', 1.0, '0 = just burned black, 1 = glowing'); noshadow(o)
            o.location = (s * x0 + (0 if who == 'Kid' else 4.0), 0, z0)
            for key, lines in NUMS:
                nb = MB()
                for rz, wd_, off in ((0, inx, iny / 2 + t), (180, inx, iny / 2 + t), (90, iny, inx / 2 + t), (270, iny, inx / 2 + t)):
                    v, f = number_block(lines, wd_ * 0.94, h * 0.84)
                    M = EU(0, 0, rz) @ Matrix.Translation((0, -off, zc))
                    nb.add(xf(v, M), f, 0, flat=True)
                no = nb.obj(f'{name}_N_{key}', [num], C, parent=o, sharp=180); follow(no, o, 'glow'); noshadow(no)
                no.hide_render = no.hide_viewport = key != ('10M' if who == 'Kid' else '1M')
            lo = point_light(name + '_Light', C, o, '#FFA040', 0.1, (0, -iny / 2 - 0.25, zc)); follow(lo.data, o, 'glow', 'energy', gain=4.0)
        info[who] = {'band_height': h, 'band_centre_z_in_arm_frame': round(zc, 3), 'outer': [round(inx + 2 * t, 2), round(iny + 2 * t, 2)]}
    return {'wrist_bands': info}


def build_sky(root):
    """the huge number that burns over the gate giant's head. Origin: bottom centre. `digits` 0..1 = how much has appeared."""
    C = coll('LA_SkyNumber', root)
    m = bpy.data.materials.new('LA_Mat_SkyNumber'); m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    N = nt.nodes.new; L = nt.links.new
    out = N('ShaderNodeOutputMaterial'); out.location = (700, 0)
    at = N('ShaderNodeAttribute'); at.attribute_type = 'OBJECT'; at.attribute_name = 'digits'; at.name = at.label = 'LA_DIGITS'; at.location = (-600, 100)
    ix = N('ShaderNodeAttribute'); ix.attribute_type = 'GEOMETRY'; ix.attribute_name = 'order'; ix.location = (-600, -100)
    lt = N('ShaderNodeMath'); lt.operation = 'LESS_THAN'; lt.location = (-350, 0); L(ix.outputs['Fac'], lt.inputs[0]); L(at.outputs['Fac'], lt.inputs[1])
    # the newest digit burns white-hot
    df = N('ShaderNodeMath'); df.operation = 'SUBTRACT'; df.location = (-350, -220); L(at.outputs['Fac'], df.inputs[0]); L(ix.outputs['Fac'], df.inputs[1])
    hot = N('ShaderNodeMapRange'); hot.location = (-150, -220); hot.inputs['From Min'].default_value = 0.0; hot.inputs['From Max'].default_value = 0.09
    hot.inputs['To Min'].default_value = 1.0; hot.inputs['To Max'].default_value = 0.0; L(df.outputs[0], hot.inputs['Value'])
    colm = N('ShaderNodeMix'); colm.data_type = 'RGBA'; colm.location = (50, -150); colm.inputs['A'].default_value = (*lin('#FF8A1E'), 1); colm.inputs['B'].default_value = (*lin('#FFF1C8'), 1)
    L(hot.outputs['Result'], colm.inputs['Factor'])
    em = N('ShaderNodeEmission'); em.location = (250, -100); em.inputs['Strength'].default_value = 9.0; L(colm.outputs['Result'], em.inputs['Color'])
    tr = N('ShaderNodeBsdfTransparent'); tr.location = (250, 120)
    mix = N('ShaderNodeMixShader'); mix.location = (480, 0); L(lt.outputs[0], mix.inputs[0]); L(tr.outputs[0], mix.inputs[1]); L(em.outputs[0], mix.inputs[2])
    L(mix.outputs[0], out.inputs['Surface'])
    m.diffuse_color = (*lin('#FF8A1E'), 1)
    try:
        m.surface_render_method = 'DITHERED'
    except Exception:
        pass
    V, F, O = [], [], []
    nv = 0
    total = sum(len(r.replace(' ', '')) for r in SKY_ROWS)
    k = 0
    H = 13.0; z = 2 * H * 1.3 + 0.0
    rows_info = []
    for ri, row in enumerate(SKY_ROWS):
        size = H * (0.8 if ri == 0 else 1.0)
        glyphs = []
        x = 0.0
        for ch in row:
            if ch == ' ':
                x += size * 0.42; continue
            v, f = text_mesh(ch, size / 0.72, 1.2)                # Poppins caps / digits are about 0.72 of the font size
            wd = v[:, 0].max() - v[:, 0].min()
            v[:, 0] -= (v[:, 0].max() + v[:, 0].min()) / 2
            v[:, 2] -= v[:, 2].min()                              # every glyph on one baseline
            adv = wd + size * 0.14
            if ch == ',':
                v[:, 2] -= size * 0.16
            if ch == '1':
                adv = wd + size * 0.2
            glyphs.append((v + np.array((x + wd / 2, 0, 0)), f)); x += adv
        tw = x
        for (v, f) in glyphs:
            v = v + np.array((-tw / 2, 0, z))
            V.append(v); F += [[i + nv for i in face] for face in f]; nv += len(v)
            O += [(k + 0.5) / total * 0.96] * len(v); k += 1
        rows_info.append(round(tw, 1))
        z -= H * 1.3
    V = np.vstack(V)
    V[:, 2] -= V[:, 2].min()
    mb = MB(); mb.add(V, F, 0, flat=True)
    o = mb.obj('LA_SkyNumber', [m], C, sharp=180)
    a = o.data.attributes.new('order', 'FLOAT', 'POINT'); a.data.foreach_set('value', np.array(O, float))
    prop(o, 'digits', 1.0, 'how much of the number has appeared: 0 = nothing, 0.12 = "1 IN", 1 = every digit'); noshadow(o)
    o.visible_shadow = False
    lo = point_light('LA_SkyNumber_Light', C, o, '#FF9A30', 6.0, (0, -6, 14)); follow(lo.data, o, 'digits', 'energy', gain=60000.0)
    return {'sky_number': {'rows': SKY_ROWS, 'row_widths': rows_info, 'size': [round(float(x), 1) for x in o.dimensions], 'glyphs': total}}


def build(root):
    info = {}
    for fn in (build_crown, build_chains, build_shells, build_bands, build_sky):
        info.update(fn(root) or {})
    return info
