# Lightning Arms: LA_LightningArms (the kid's arms of light), LA_SparkBurst, LA_GroundSplit.
# Arm shells are built in the Cast v2 arm frame: origin at the shoulder pivot (the `heroarmL` / `heroarmR` empty), arm hanging down -Z.
from la_lib import *

HERO_ARM = dict(w=0.80, top=0.16, bottom=-1.464)          # Cast v2 Hero kid arm box (world BU), hand included
VILLAIN_ARM = dict(w=0.84, d=0.945, top=0.21, bottom=-2.551)


def bolt_path(rng, p0, p1, n, jit):
    P = [Vector(p0)]
    d = Vector(p1) - Vector(p0)
    for i in range(1, n):
        P.append(Vector(p0) + d * (i / n) + Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))) * jit * d.length)
    P.append(Vector(p1))
    return P


def bolt(mb, P, r0, r1, mat=0):
    P = [np.array(p[:]) for p in P]
    rad = np.linspace(r0, r1, len(P))
    v, f, _ = tube(P, rad, segs=4, cap0=True, cap1=True, tip=2.5)
    mb.add(v, f, mat, flat=True)


def star(mb, tip, s, mat=1):
    for ax in (Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))):
        bolt(mb, [Vector(tip) - ax * s, Vector(tip) + ax * s], 0.035, 0.035, mat=mat)


def thick_bolt(mb, P, r0, r1):
    """a fat tapered bolt (mat 0) inside a soft cyan sleeve (mat 2)."""
    P = [np.array(p[:]) for p in P]
    v, f, _ = tube(P, np.linspace(r0, r1, len(P)), segs=5, cap0=True, cap1=True, tip=2.5); mb.add(v, f, 0, flat=True)
    v, f, _ = tube(P, np.linspace(r0 * 2.6, r1 * 2.6, len(P)), segs=6, cap0=True, cap1=True, tip=1.5); mb.add(v, f, 2, flat=False)


def arm_bolts(rng, scale=1.0):
    """one lightning shape for an arm: four fat tapered bolts jumping off the fist and the elbow (one with a short twig)."""
    mb = MB()
    dirs = [Vector((1, -0.3, -0.5)), Vector((-1, -0.4, -0.3)), Vector((0.2, -1, -0.8)), Vector((-0.3, 0.7, -1)), Vector((0.8, 0.5, 0.3))]
    rng.shuffle(dirs)
    for k in range(4):
        src = Vector((0, 0, -1.27)) if k < 3 else Vector((0, 0, -0.62))
        d = (dirs[k] + Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))) * 0.35).normalized()
        ln = rng.uniform(1.1, 1.9) * scale * (1.0 if k < 3 else 0.75)
        P = bolt_path(rng, src + d * 0.45, src + d * (0.45 + ln), 5, 0.16)
        thick_bolt(mb, P, 0.085, 0.012)
        if k < 2:
            d2 = (d + Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))) * 0.9).normalized()
            thick_bolt(mb, bolt_path(rng, P[2], P[2] + d2 * ln * 0.45, 3, 0.16), 0.05, 0.01)
    return mb


def glow_mats():
    return dict(
        shell=glow_mat('LightningShell', '#1E7BFF', 1.0, base_hex='#3C8CFF', fade_shell=True),
        edge=glow_mat('LightningEdge', '#3FE6FF', 5.0, base_hex='#9FF2FF'),
        core=glow_mat('LightningCore', '#EAF6FF', 6.0, base_hex='#FFFFFF'),
        bolt=glow_mat('LightningBolt', '#CFEBFF', 9.0, base_hex='#FFFFFF'),
        spark=glow_mat('LightningSpark', '#FFFFFF', 14.0, base_hex='#FFFFFF'),
        sleeve=glow_mat('LightningSleeve', '#22D8FF', 1.1, halo=True, falloff=1.4),
        halo=glow_mat('LightningHalo', '#2F9CFF', 0.32, halo=True, falloff=2.2),
        halo2=glow_mat('LightningHaloWide', '#2A6CFF', 0.08, halo=True, falloff=2.6))


def edge_frame(mb, size, c, t, mat):
    """thin bars along the 12 edges of a box: the cyan outline that keeps the arm reading as blocks."""
    sx, sy, sz = size
    for ax in range(3):
        for a in (-1, 1):
            for b in (-1, 1):
                dims = [t, t, t]; pos = [0.0, 0.0, 0.0]
                dims[ax] = size[ax] + t
                o1, o2 = [i for i in range(3) if i != ax]
                pos[o1] = a * size[o1] / 2; pos[o2] = b * size[o2] / 2
                v, f = box(dims, (c[0] + pos[0], c[1] + pos[1], c[2] + pos[2])); mb.add(v, f, mat, flat=True)


def build_arms(root):
    C = coll('LA_LightningArms', root)
    G = glow_mats()
    for sd, x in (('L', -1.2), ('R', 1.2)):
        rng = random.Random(40 + (0 if sd == 'L' else 9))
        mb = MB()
        # blocky shells of light: upper arm, forearm, fist (a little bigger than the kid's arm, so they also work over it).
        # blue faces, cyan edge bars, a white-hot core showing in the seams and in a slot down each face
        for (sz, cz) in (((0.88, 0.88, 0.80), -0.23), ((0.82, 0.82, 0.44), -0.85), ((0.96, 0.96, 0.44), -1.275)):
            v, f = box(sz, (0, 0, cz)); mb.add(v, f, 0, flat=True)
            edge_frame(mb, sz, (0, 0, cz), 0.07, 1)
            for face in range(4):
                M = EU(0, 0, 90 * face)
                v, f = box((sz[0] * 0.3, 0.03, sz[2] * 0.56), (0, -sz[1] / 2 - 0.012, cz)); mb.add(xf(v, M), f, 2, flat=True)
        for cz in (-0.63, -1.062):
            v, f = box((0.7, 0.7, 0.06), (0, 0, cz)); mb.add(v, f, 2, flat=True)
        o = mb.obj(f'LA_LightningArm_{sd}', [G['shell'], G['edge'], G['core']], C, sharp=40)
        prop(o, 'glow', 1.0, '0 = off, 1 = full glow'); noshadow(o); o.location = (x, 0, 3.04)
        hb = MB()
        v, f = ico(3); hb.add(v * np.array((0.78, 0.78, 1.12)) + np.array((0, 0, -0.66)), f, 0)
        v, f = ico(3); hb.add(v * np.array((1.05, 1.05, 1.4)) + np.array((0, 0, -0.7)), f, 1)
        h = hb.obj(f'LA_LightningArm_{sd}_Halo', [G['halo'], G['halo2']], C, sharp=180); h.parent = o; noshadow(h); follow(h, o, 'glow')
        for i, L_ in enumerate('ABCD'):
            tb = arm_bolts(random.Random(200 + i * 17 + (0 if sd == 'L' else 500)))
            bo = tb.obj(f'LA_LightningArm_{sd}_Bolts_{L_}', [G['bolt'], G['spark'], G['sleeve']], C, sharp=180); bo.parent = o; noshadow(bo); follow(bo, o, 'glow')
            bo.hide_render = bo.hide_viewport = L_ != 'A'
        lo = point_light(f'LA_LightningArm_{sd}_Light', C, o, '#8FCBFF', 0.4, (0, 0, -1.2))
        follow(lo.data, o, 'glow', 'energy', gain=12.0)
    return {'lightning_arm': {'fits': 'Cast v2 Hero kid arm 0.80 x 0.80, shoulder pivot +0.16 to hand bottom -1.464', 'light_watts_at_glow_1': 12.0}}


def build_burst(root):
    C = coll('LA_SparkBurst', root)
    G = glow_mats()
    mb = MB(); v, f = ico(2); mb.add(v * 0.32, f, 0)
    o = mb.obj('LA_SparkBurst', [G['core']], C, sharp=180); prop(o, 'glow', 1.0, '0 = off, 1 = full'); noshadow(o); o.location = (0, 0, 3)
    hb = MB(); v, f = ico(3); hb.add(v * 0.9, f, 0); v, f = ico(3); hb.add(v * 1.6, f, 1)
    h = hb.obj('LA_SparkBurst_Halo', [G['halo'], G['halo2']], C, sharp=180); h.parent = o; noshadow(h); follow(h, o, 'glow')
    for i, L_ in enumerate('ABC'):
        rng = random.Random(900 + i * 7)
        sb = MB()
        for k in range(7):
            d = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-0.8, 1))).normalized()
            ln = rng.uniform(1.6, 3.2)
            P = bolt_path(rng, d * 0.25, d * ln, 5, 0.14)
            thick_bolt(sb, P, 0.1, 0.014)
            if rng.random() < 0.5:
                d2 = (d + Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))) * 0.8).normalized()
                thick_bolt(sb, bolt_path(rng, P[2], P[2] + d2 * ln * 0.4, 3, 0.14), 0.05, 0.01)
            star(sb, P[-1], 0.22 * rng.uniform(0.8, 1.4))
        for k in range(12):                                             # loose sparks
            d = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-0.7, 1))).normalized() * rng.uniform(1.5, 3.8)
            star(sb, d, 0.12 * rng.uniform(0.6, 1.5))
        so = sb.obj(f'LA_SparkBurst_Shape_{L_}', [G['bolt'], G['spark'], G['sleeve']], C, sharp=180); so.parent = o; noshadow(so); follow(so, o, 'glow')
        so.hide_render = so.hide_viewport = L_ != 'A'
    lo = point_light('LA_SparkBurst_Light', C, o, '#8FCBFF', 0.6); follow(lo.data, o, 'glow', 'energy', gain=70.0)
    return {}


SPLIT_LEN = 48.0; SPLIT_SEGS = 6


def build_split(root):
    """a glowing jagged crack lying on the ground along X (x -24 .. 24), widest 3.4. `amount` 0..1 = how far it has opened, from -X to +X.
    Closed parts are folded away under z = 0, so it needs your ground at z = 0 to hide them."""
    C = coll('LA_GroundSplit', root)
    G = glow_mats()
    rng = random.Random(77)
    stone = stone_mat('SplitStone', '#8F877C', bump=0.4, scale=0.6, mottle=0.16, ao=False)
    darkm = mat('SplitDark', '#17141C', 1.0, vcol=False)
    glowm = glow_mat('SplitGlow', '#7FD0FF', 8.0, base_hex='#EAF6FF', fade_shell=False)
    n = 40
    xs = np.linspace(-SPLIT_LEN / 2, SPLIT_LEN / 2, n + 1)
    yc = np.array([rng.uniform(-1.5, 1.5) * (1 if 0 < i < n else 0) for i in range(n + 1)])
    yc = np.convolve(np.pad(yc, 1, mode='edge'), [0.25, 0.5, 0.25], mode='valid') * 1.4
    hw = np.array([1.7 * math.sin(math.pi * i / n) ** 0.55 * rng.uniform(0.6, 1.15) for i in range(n + 1)]); hw[0] = hw[-1] = 0.02
    mb = MB()
    # dark gap, then the glowing heart of the crack
    for (k, z, m) in ((1.0, 0.04, 1), (0.52, 0.07, 2)):
        V = []; F = []
        for i in range(n + 1):
            jl = 1 + (rng.uniform(-0.25, 0.25) if k < 1 else 0); jr = 1 + (rng.uniform(-0.25, 0.25) if k < 1 else 0)
            V += [(xs[i], yc[i] - hw[i] * k * jl, z), (xs[i], yc[i] + hw[i] * k * jr, z)]
        for i in range(n):
            F.append([2 * i, 2 * i + 2, 2 * i + 3, 2 * i + 1])
        mb.add(np.array(V), F, m, flat=True)
    # heaved slabs along both lips
    for i in range(1, n, 1):
        for s in (-1, 1):
            if rng.random() < 0.22:
                continue
            ln = rng.uniform(1.3, 2.6); wd = rng.uniform(1.0, 2.2) * (0.5 + hw[i] / 1.9); th = rng.uniform(0.35, 0.7)
            tilt = rng.uniform(10, 34)
            v, f = crag((ln, wd, th), (0, 0, 0), seed=i * 2 + (s > 0), sub=2, amp=0.06, cuts=3, rnd=0.05)
            M = Matrix.Translation((xs[i] + rng.uniform(-0.3, 0.3), yc[i] + s * (hw[i] + wd * 0.42), 0.1 + math.sin(R(tilt)) * wd * 0.42)) @ EU(-s * tilt, rng.uniform(-6, 6), rng.uniform(-14, 14))
            mb.add(xf(v, M), f, 0, col=rockcol((rng.uniform(0.8, 1.0),) * 3, i, scale=0.5), flat=True, fjit=0.12)
    # rubble
    for i in range(60):
        k = rng.randrange(2, n - 1); s = rng.choice((-1, 1)); r = rng.uniform(0.12, 0.38)
        v, f = blob((xs[k] + rng.uniform(-0.6, 0.6), yc[k] + s * (hw[k] + rng.uniform(0.8, 3.6)), r * 0.6), r, sub=1, amp=0.2, seed=i, cuts=3)
        mb.add(v, f, 0, col=(rng.uniform(0.7, 1.0),) * 3, flat=True)
    o = mb.obj('LA_GroundSplit', [stone, darkm, glowm], C, sharp=40)
    prop(o, 'amount', 1.0, '0 = closed, 1 = open along its whole length (opens from -X to +X)')
    prop(o, 'glow', 1.0, '0 = dark crack, 1 = full lightning glow')
    # lightning standing in the crack
    bb = MB()
    for i in range(3, n - 2, 2):
        base = Vector((xs[i], yc[i], 0.1)); h = rng.uniform(1.2, 4.2) * (hw[i] / 1.7 + 0.3)
        P = bolt_path(rng, base, base + Vector((rng.uniform(-0.8, 0.8), rng.uniform(-0.6, 0.6), h)), 6, 0.16)
        bolt(bb, P, 0.09, 0.01)
        star(bb, P[-1], 0.16)
    bo = bb.obj('LA_GroundSplit_Bolts', [G['bolt'], G['spark']], C, sharp=180); bo.parent = o; noshadow(bo); follow(bo, o, 'glow')
    # shape keys: one per stretch of the crack, folding it under the ground
    seg_w = SPLIT_LEN / SPLIT_SEGS
    for ob in (o, bo):
        ob.shape_key_add(name='Basis')
        me = ob.data
        for sgi in range(SPLIT_SEGS):
            kb = ob.shape_key_add(name=f'Closed_{sgi + 1}')
            x0 = -SPLIT_LEN / 2 + sgi * seg_w
            for vi, vtx in enumerate(me.vertices):
                x = vtx.co.x
                if x0 - 1e-4 <= x < x0 + seg_w + 1e-4 or (sgi == SPLIT_SEGS - 1 and x >= x0) or (sgi == 0 and x < x0):
                    kb.data[vi].co = (x, float(np.interp(x, xs, yc)), -0.35 - 0.2 * vtx.co.z)
            kb.value = 0.0
            # value = 1 + sgi - SEGS * amount, limited to 0..1
            fc = kb.driver_add('value'); d = fc.driver; d.type = 'SUM'
            var = d.variables.new(); var.name = 'a'; var.type = 'SINGLE_PROP'; var.targets[0].id = o; var.targets[0].data_path = '["amount"]'
            for m_ in list(fc.modifiers):
                fc.modifiers.remove(m_)
            g = fc.modifiers.new('GENERATOR'); g.mode = 'POLYNOMIAL'; g.poly_order = 1; g.coefficients = (1.0 + sgi, -float(SPLIT_SEGS))
            lm = fc.modifiers.new('LIMITS'); lm.use_min_y = lm.use_max_y = True; lm.min_y = 0.0; lm.max_y = 1.0
    for k, x in enumerate((-14, 0, 14)):
        lo = point_light(f'LA_GroundSplit_Light_{k + 1}', C, o, '#8FCBFF', 1.0, (x, float(np.interp(x, xs, yc)), 1.2))
        fc = follow(lo.data, o, 'amount', 'energy', gain=900.0 * SPLIT_SEGS / 2, offset=-900.0 * (k + 0.5), lo=0.0, hi=900.0)
    return {'ground_split': {'length': SPLIT_LEN, 'max_width': 3.4, 'runs_along': 'X, opens from -X to +X', 'segments': SPLIT_SEGS}}


def build(root):
    info = {}
    info.update(build_arms(root)); info.update(build_burst(root)); info.update(build_split(root))
    return info
