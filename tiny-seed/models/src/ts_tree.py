# Tiny Seed: OUR TREE (stages A-E, face, armature, poses), the champion's oak and the bushes.
import json
from ts_lib import *

BARK, BARK_DK = '#AC7F52', '#5E3F27'
LEAF, LEAF_TOP, LEAF_UNDER = '#8FCB55', '#A9D168', '#4C8743'
OAK_LEAF, OAK_UNDER = '#5E9A46', '#2F6532'
OAK_BARK = '#77624A'

PROFILE = [(-1.2, 16.2), (0, 14.8), (2, 12.6), (5, 11.2), (10, 10.2), (18, 9.7), (26, 9.9), (33, 9.3), (40, 8.9), (46, 9.3), (52, 7.8), (58, 5.2)]


def trunk_R(z, prof=PROFILE):
    zs = [p[0] for p in prof]; rs = [p[1] for p in prof]
    return float(np.interp(z, zs, rs))


def trunk_r(z, th):
    return trunk_R(z) * (1 + 0.035 * math.cos(7 * th + 0.12 * z))


def wrap(x, z, off=0.0):
    """face-plane point (x across, z up) -> point on the trunk front surface, pushed out by off."""
    th = x / trunk_R(z)
    r = trunk_r(z, th) + off
    return (r * math.sin(th), -r * math.cos(th), z)


TN = ['TS_Root', 'TS_Trunk1', 'TS_Trunk2', 'TS_Trunk3', 'TS_Canopy']
TJ = [(2, 2), (14, 3), (34, 3), (50, 3)]


def trunk_w(z):
    for i, (j, h) in enumerate(TJ):
        if abs(z - j) < h:
            t = (z - j + h) / (2 * h); t = t * t * (3 - 2 * t)
            return {TN[i]: 1 - t, TN[i + 1]: t}
    return {TN[sum(z >= j for j, _ in TJ)]: 1.0}


def canopy_blobs(spec, top, base, seed):
    """spec: list of (centre, radii). Returns blob param dicts with z squeezed so the highest point is `top`."""
    out = []
    for i, (c, r) in enumerate(spec):
        r = (r, r, r) if np.isscalar(r) else r
        out.append({'c': np.array(c, float), 'r': np.array(r, float), 'seed': seed + i})
    mz = max(b['c'][2] + b['r'][2] * 1.04 for b in out)
    k = (top - base) / (mz - base)
    for b in out:
        b['c'][2] = base + (b['c'][2] - base) * k; b['r'][2] *= k
    return out


AMP, FREQ = 0.09, 1.5


def blob_r(b, d):
    """distance from blob centre to its noisy surface along unit direction d (matches ts_lib.blob)."""
    off = Vector((b['seed'] * 7.13 + 1.1, b['seed'] * 3.31 + 2.2, b['seed'] * 1.77 + 3.3))
    n = noise.noise(Vector(d) * FREQ + off)
    return (1.0 + AMP * n * 1.8)


def surf_points(blobs, n, zmin, zmax, seed, mind, embed=0.97, front_bias=0.0, zworld=None):
    rng = random.Random(seed)
    pts = []
    tries = 0
    wts = [b['r'][0] ** 2 for b in blobs]
    while len(pts) < n and tries < 20000:
        tries += 1
        b = rng.choices(blobs, wts)[0]
        d = Vector((rng.gauss(0, 1), rng.gauss(0, 1) - front_bias, rng.gauss(0, 1))).normalized()
        if not (zmin <= d.z <= zmax):
            continue
        k = blob_r(b, d)
        p = b['c'] + b['r'] * np.array(d[:]) * k * embed
        if zworld and not (zworld[0] <= p[2] <= zworld[1]):
            continue
        if any(o is not b and np.sum(((p - o['c']) / (o['r'] * 0.93)) ** 2) < 1 for o in blobs):
            continue
        if any(np.linalg.norm(p - q[0]) < mind for q in pts):
            continue
        nrm = Vector(np.array(d[:]) / b['r']).normalized()
        pts.append((p, nrm))
    return pts


def add_canopy(mb, blobs, mat_i, under, top, w, zlo, zhi, sub=3):
    tu = np.array(tint(under, top))
    for b in blobs:
        v, f = blob(b['c'], b['r'], sub=sub, amp=AMP, freq=FREQ, seed=b['seed'])

        def col(p, b=b):
            t = np.clip(((p[2] - b['c'][2]) / b['r'][2] + 1) / 2, 0, 1)
            g = np.clip((p[2] - zlo) / (zhi - zlo), 0, 1)
            k = 0.6 * t + 0.4 * g
            k = k * k * (3 - 2 * k)
            return tu + (1 - tu) * k
        mb.add(v, f, mat_i, col=col, fjit=0.10, flat=True, w=w, seed=b['seed'])


def petal_flower(rad, n=5, cup=0.35):
    """flat 5-petal flower in the XY plane facing +Z, centre dome. Returns (petal verts, faces), (centre verts, faces)."""
    PV, PF = [], []
    prof = [(0.12, 0.30), (0.45, 0.85), (0.78, 1.0), (1.0, 0.55)]
    for k in range(n):
        a = 2 * math.pi * k / n
        V = []
        for (t, wd) in prof:
            z = cup * rad * t * t
            V += [(-wd * 0.36 * rad, t * rad, z + 0.05 * rad * wd), (0, t * rad, z), (wd * 0.36 * rad, t * rad, z + 0.05 * rad * wd)]
        V = xf(np.array(V, float), Matrix.Rotation(a, 4, 'Z'))
        o = len(PV)
        PV += V.tolist()
        for i in range(len(prof) - 1):
            b = o + i * 3
            PF += [[b, b + 1, b + 4, b + 3], [b + 1, b + 2, b + 5, b + 4]]
    cv, cf = blob((0, 0, 0.05 * rad), (0.24 * rad, 0.24 * rad, 0.16 * rad), sub=1, amp=0)
    return (np.array(PV), PF), (cv, cf)


def apple_mesh(r=1.0, segs=14):
    prof = [(0.0, 0.10), (0.30, 0.02), (0.62, 0.10), (0.90, 0.42), (1.0, 0.85), (0.95, 1.25), (0.72, 1.62), (0.40, 1.80), (0.14, 1.74), (0.0, 1.62)]
    v, f = lathe([(max(a, 0.001) * r, z * r) for a, z in prof], segs, cap_bottom=True, cap_top=True)
    return v, f


# =====================================================================================================
def build_tree(root):
    C = coll('TS_Tree', root)
    cA, cB, cC = coll('TS_Tree_A_Dot', C), coll('TS_Tree_B_Sprout', C), coll('TS_Tree_C_Giant', C)
    cD, cE = coll('TS_Tree_D_Blossoms', C), coll('TS_Tree_E_Apples', C)
    m_bark = mat('TreeBark', BARK, 0.9)
    m_leaf = mat('TreeLeaf', LEAF_TOP, 0.8)
    m_soil = mat('Soil', '#6A4B35', 0.95)
    m_bud = mat('TreeBud', '#F0C7D2', 0.7)
    m_rim = mat('TreeEyeRim', '#3A2618', 0.8)
    m_white = mat('TreeEyeWhite', '#FBF6EA', 0.5)
    m_pupil = mat('TreeEyePupil', '#1E140E', 0.35)
    m_lid = mat('TreeEyeLid', '#B98A5C', 0.9)
    m_blush = mat('TreeBlush', '#E59C8C', 0.9)
    m_pet_w = mat('BlossomWhite', '#FFF8F4', 0.7)
    m_pet_p = mat('BlossomPink', '#F6B9CB', 0.7)
    m_cen = mat('BlossomCentre', '#F3C64A', 0.7)
    m_gold = mat('AppleGold', '#F6BE2C', 0.3, emit='#FFAA10', estr=1.1, spec=0.6)

    # ------------------------------------------------------------------ A: the dot
    mb = MB()
    v, f = lathe([(0.44, -0.02), (0.42, 0.012), (0.30, 0.04), (0.12, 0.055), (0.001, 0.06)], 16, cap_top=False)
    for i in range(len(v)):
        a = math.atan2(v[i][1], v[i][0]); v[i][:2] *= 1 + 0.10 * math.sin(3 * a + 1) + 0.05 * math.sin(7 * a)
    mb.add(v, f, 0, fjit=0.12, flat=True)
    for (x, y, r_) in ((0.2, 0.12, 0.035), (-0.24, -0.05, 0.028), (0.05, -0.27, 0.03), (-0.1, 0.25, 0.022)):
        bv, bf = blob((x, y, 0.035), r_, sub=1, amp=0.15, seed=int(x * 100))
        mb.add(bv, bf, 0, col=(0.8, 0.8, 0.8), flat=True)
    sp = spline([(0, 0, 0.03), (0.012, 0, 0.11), (-0.004, 0, 0.19), (0.0, 0, 0.24)], 9)
    tv, tf, _ = tube(sp, np.linspace(0.016, 0.010, 9), 6, cap1=True)
    mb.add(tv, tf, 1, col=tint('#9BCF5E', LEAF_TOP))
    lv, lf = leaf(0.17, 0.5, 0.10, 0.25)
    lv = xf(lv, Matrix.Translation((0.0, 0, 0.17)) @ Matrix.Rotation(R(-90), 4, 'Z') @ Matrix.Rotation(R(28), 4, 'X'))
    mb.add(lv, lf, 1)
    bv, bf = blob((0.0, 0, 0.268), (0.03, 0.03, 0.04), sub=2, amp=0)
    mb.add(bv, bf, 2)
    oA = mb.obj('TS_Tree_A_Dot', [m_soil, m_leaf, m_bud], cA, sharp=50)

    # ------------------------------------------------------------------ B: shooting up
    mb = MB()
    v, f = lathe([(3.4, -0.3), (3.2, 0.1), (2.2, 0.45), (0.9, 0.6), (0.001, 0.62)], 18, cap_top=False)
    for i in range(len(v)):
        a = math.atan2(v[i][1], v[i][0]); v[i][:2] *= 1 + 0.10 * math.sin(3 * a + 1) + 0.05 * math.sin(7 * a)
    mb.add(v, f, 0, fjit=0.12, flat=True)
    path = [(0, 0, 0.2), (0.9, 0.2, 8), (-0.7, -0.2, 17), (0.8, 0.1, 26), (-0.2, 0, 33), (0.25, 0, 38.2)]
    sp = spline(path, 40)
    rad = np.interp(np.linspace(0, 1, 40), [0, 0.08, 0.6, 1], [1.7, 1.25, 0.8, 0.3])
    tv, tf, _ = tube(sp, rad, 10, cap1=True)
    mb.add(tv, tf, 1, col=tint('#8DBF58', LEAF_TOP), shade=(0, 14, 0.8))
    rng = random.Random(3)
    for i, zi in enumerate((9, 15, 20.5, 26, 31, 35)):
        k = int(zi / 38.2 * 39)
        p = sp[k]; sg = 1 if i % 2 == 0 else -1
        ln = 6.4 - i * 0.55
        d = Vector((sg * 1.0, rng.uniform(-0.35, 0.35), 0.38)).normalized()
        tw, tff, _ = tube([p, p + np.array(d[:]) * 1.6], [0.26, 0.2], 6, cap1=False)
        mb.add(tw, tff, 1, col=tint('#8DBF58', LEAF_TOP))
        lv, lf = leaf(ln, 0.42, 0.10, 0.22)
        lv = align(lv, d, p + np.array(d[:]) * 1.4, axis='Y', spin=0)
        mb.add(lv, lf, 1, col=lambda q: (1, 1, 1))
    for sg in (-1, 1):
        lv, lf = leaf(3.2, 0.45, 0.10, 0.2)
        lv = align(lv, Vector((sg * 0.8, 0, 0.75)), sp[-1] - np.array((0, 0, 0.5)), axis='Y')
        mb.add(lv, lf, 1)
    bv, bf = blob(sp[-1] + np.array((0, 0, 0.9)), (0.62, 0.62, 0.9), sub=2, amp=0)
    mb.add(bv, bf, 2)
    oB = mb.obj('TS_Tree_B_Sprout', [m_soil, m_leaf, m_bud], cB, sharp=50)
    # ------------------------------------------------------------------ C: the giant
    AB = 10                      # bones per arm
    AL = 6.2                     # bone length
    def rest_path(s):
        return [(1.5 * s, 0, 35), (10 * s, -1, 37.5), (21 * s, -2, 40), (31 * s, -2, 45), (37 * s, -2, 54), (39.5 * s, -2, 64), (40 * s, -2, 70)]
    bones = [('TS_Root', (0, 0, 0), (0, -4, 0), None, False),
             ('TS_Trunk1', (0, 0, 0), (0, 0, 14), 'TS_Root', False),
             ('TS_Trunk2', (0, 0, 14), (0, 0, 34), 'TS_Trunk1', True),
             ('TS_Trunk3', (0, 0, 34), (0, 0, 50), 'TS_Trunk2', True),
             ('TS_Canopy', (0, 0, 50), (0, 0, 78), 'TS_Trunk3', True),
             ('TS_Eyes', (0, -11.5, 27.5), (0, -11.5, 30.5), 'TS_Trunk2', False)]
    joints = {}
    for side, s in (('L', 1), ('R', -1)):
        pts = walk(rest_path(s), AL, AB)
        joints[side] = pts
        for i in range(AB):
            bones.append((f'TS_Arm{side}_{i + 1:02d}', pts[i], pts[i + 1], 'TS_Trunk3' if i == 0 else f'TS_Arm{side}_{i:02d}', i > 0))
    arm = make_arm('TS_Tree_Rig', bones, cC)

    mb = MB()
    # trunk
    zs = np.concatenate([np.linspace(-1.2, 6, 9), np.linspace(7, 58, 36)])
    SEG = 36
    V, F = [], []
    for z in zs:
        for k in range(SEG):
            th = 2 * math.pi * k / SEG
            r = trunk_r(z, th)
            V.append((r * math.sin(th), -r * math.cos(th), z))
    for i in range(len(zs) - 1):
        for k in range(SEG):
            a, b = i * SEG + k, i * SEG + (k + 1) % SEG
            F.append([a, a + SEG, b + SEG, b])
    F.append([k for k in range(SEG)]); F.append([(len(zs) - 1) * SEG + k for k in range(SEG)][::-1])
    V = np.array(V)
    dk = np.array(tint(BARK_DK, BARK))

    def bark_col(p):
        th = math.atan2(p[0], -p[1])
        g = 0.5 + 0.5 * math.cos(7 * th + 0.12 * p[2])
        g = g ** 1.6 * (0.85 + 0.15 * math.sin(p[2] * 0.9 + 3 * th))
        return dk + (1 - dk) * (0.25 + 0.75 * g)
    mb.add(V, F, 0, col=bark_col, shade=(-1, 16, 0.78), w=[trunk_w(p[2]) for p in V])
    # roots
    for i in range(7):
        a = 2 * math.pi * i / 7 + 0.35
        dx, dy = math.sin(a), -math.cos(a)
        L = 17 + (i % 3) * 2.2
        L *= 1.3
        pts = spline([(dx * 5.5, dy * 5.5, 13), (dx * 11.5, dy * 11.5, 5.2), (dx * 17, dy * 17, 1.3), (dx * L, dy * L, -1.0)], 14)
        tv, tf, _ = tube(pts, np.interp(np.linspace(0, 1, 14), [0, 0.4, 0.7, 1], [1.6, 4.3, 3.2, 1.0]), 12, cap1=True)
        mb.add(tv, tf, 0, col=bark_col, shade=(-1, 16, 0.78), w='TS_Root')
    # inner branches up into the canopy
    for (ex, ey, ez) in ((15, 5, 63), (-14, 7, 62), (2, 13, 64), (-3, -11, 63)):
        pts = spline([(ex * 0.1, ey * 0.1, 44), (ex * 0.55, ey * 0.55, 54), (ex, ey, ez)], 8)
        tv, tf, _ = tube(pts, np.linspace(3.0, 1.6, 8), 10, cap1=True)
        mb.add(tv, tf, 0, col=bark_col, w='TS_Canopy')
    # arms
    RPB = 6
    hand = {}
    for side, s in (('L', 1), ('R', -1)):
        J = joints[side]
        n = AB * RPB + 1
        cl = np.array([J[min(int(j / RPB), AB - 1)] + (J[min(int(j / RPB), AB - 1) + 1] - J[min(int(j / RPB), AB - 1)]) * ((j / RPB) - min(int(j / RPB), AB - 1)) for j in range(n)])
        # smooth the polyline corners a little (keeps joints close to the bones)
        sm = cl.copy()
        for _ in range(2):
            sm[1:-1] = 0.25 * sm[:-2] + 0.5 * sm[1:-1] + 0.25 * sm[2:]
        rad = np.interp(np.linspace(0, 1, n), [0, 0.15, 0.8, 1], [4.3, 3.6, 2.3, 1.7])
        tv, tf, ring = tube(sm, rad, 12, cap1=True, lobes=5, lobe_amp=0.03)
        W = []
        for rj in ring:
            u = rj / RPB; b = min(int(u), AB - 1); fr = u - b
            nm = lambda i: f'TS_Arm{side}_{i + 1:02d}'
            if fr < 0.3 and b > 0:
                t = 0.5 + fr / 0.6
                W.append({nm(b - 1): 1 - t, nm(b): t})
            elif fr > 0.7 and b < AB - 1:
                t = 0.5 + (1 - fr) / 0.6
                W.append({nm(b): t, nm(b + 1): 1 - t})
            else:
                W.append({nm(b): 1.0})
        mb.add(tv, tf, 0, col=lambda p: dk + (1 - dk) * 0.8, w=W)
        hand[side] = (J[-1], (J[-1] - J[-2]) / AL)
    o_trunk = mb.obj('TS_Tree_Trunk', [m_bark], cC, arm=arm, sharp=60)

    # canopy
    rng = random.Random(11)
    spec = [((0, 0, 75), (28, 26, 21))]
    for i in range(8):
        a = 2 * math.pi * i / 8 + 0.2; rr = 25 + rng.uniform(-2, 2)
        spec.append(((rr * math.cos(a), rr * math.sin(a) * 0.9, 65 + rng.uniform(-3, 3)), 15.5 + rng.uniform(-1.5, 2.5)))
    for i in range(6):
        a = 2 * math.pi * i / 6 + 0.6; rr = 15 + rng.uniform(-1, 2)
        spec.append(((rr * math.cos(a), rr * math.sin(a) * 0.9, 85 + rng.uniform(-2, 2)), 13 + rng.uniform(-1, 2)))
    spec.append(((0, -1, 92), 12))
    for i in range(5):
        a = 2 * math.pi * i / 5 + 1.0
        spec.append(((12 * math.cos(a), 12 * math.sin(a), 57), 10.5))
    blobs = canopy_blobs(spec, 100.0, 46.0, 100)
    mb = MB()
    add_canopy(mb, blobs, 0, LEAF_UNDER, LEAF_TOP, 'TS_Canopy', 48, 100)
    # hand tufts
    tufts = {}
    for side, s in (('L', 1), ('R', -1)):
        p, d = hand[side]
        tb = [{'c': np.array(c0, float), 'r': np.array((r0, r0, r0), float), 'seed': 300 + 10 * (s > 0) + i} for i, (c0, r0) in enumerate(
            [(p + d * 1.8, 4.5), (p + d * 0.3 + np.array((2.0 * s, -1.8, -1.0)), 3.3), (p + d * 0.6 + np.array((-1.8 * s, 1.8, 0.4)), 3.2), (p + d * 4.3 + np.array((0, 0.4, 0)), 3.0)])]
        add_canopy(mb, tb, 0, LEAF_UNDER, LEAF_TOP, f'TS_Arm{side}_{AB:02d}', p[2] - 8, p[2] + 10, sub=2)
        tufts[side] = tb
    o_can = mb.obj('TS_Tree_Canopy', [m_leaf], cC, arm=arm)

    # face
    mb = MB()
    pup = MB()
    EX, EZ, EA, EB_ = 5.0, 28.2, 2.95, 3.8
    lid_rows = []
    for sg in (-1, 1):
        cx = sg * EX
        # white (domed disc)
        V = [wrap(cx, EZ, 0.42)]; F = []
        NR, NS = 5, 24
        for i in range(1, NR + 1):
            rho = i / NR
            for k in range(NS):
                t = 2 * math.pi * k / NS
                V.append(wrap(cx + EA * rho * math.cos(t), EZ + EB_ * rho * math.sin(t), 0.10 + 0.32 * (1 - rho * rho)))
        for k in range(NS):
            F.append([0, 1 + k, 1 + (k + 1) % NS])
        for i in range(NR - 1):
            for k in range(NS):
                a = 1 + i * NS + k; b = 1 + i * NS + (k + 1) % NS
                F.append([a, a + NS, b + NS, b])
        mb.add(V, [x[::-1] for x in F], 1, w='TS_Trunk2')
        # rim (thick knothole ring)
        V, F = [], []
        NT, NC = 36, 7
        wr, hr = 0.66, 1.45
        for k in range(NT):
            t = 2 * math.pi * k / NT
            for j in range(NC):
                sgm = math.pi * j / (NC - 1)
                e = wr * math.cos(sgm)
                V.append(wrap(cx + (EA + e) * math.cos(t), EZ + (EB_ + e) * math.sin(t), hr * math.sin(sgm) - 0.12))
        for k in range(NT):
            for j in range(NC - 1):
                a = k * NC + j; b = ((k + 1) % NT) * NC + j
                F.append([a, b, b + 1, a + 1])
        mb.add(V, F, 0, w='TS_Trunk2')
        # lid (collapsed under the rim top; shape key BLINK spreads it over the eye)
        NCc, NRr = 11, 6
        V, F, rows = [], [], []
        for i in range(NCc):
            u = -0.985 + 1.97 * i / (NCc - 1)
            h = math.sqrt(max(0.0, 1 - u * u))
            for j in range(NRr):
                V.append(wrap(cx + EA * u, EZ + EB_ * h - 0.3 * h * j / (NRr - 1), 0.5))
                zt, zb = EZ + EB_ * h, EZ - EB_ * h
                zz = zt + (zb - zt) * j / (NRr - 1)
                bulge = 1.02 + 0.12 * h * math.sin(math.pi * j / (NRr - 1))
                rows.append(wrap(cx + EA * u, zz, bulge))
        for i in range(NCc - 1):
            for j in range(NRr - 1):
                a = i * NRr + j
                F.append([a, a + 1, a + NRr + 1, a + NRr])
        lid_rows.append((mb.n, rows))
        mb.add(V, [x[::-1] for x in F], 2, w='TS_Trunk2')
        # blush
        V = [wrap(sg * 8.0, 23.2, 0.2)]; F = []
        for k in range(16):
            t = 2 * math.pi * k / 16
            V.append(wrap(sg * 8.0 + 1.7 * math.cos(t), 23.2 + 1.0 * math.sin(t), 0.09))
        F = [[0, 1 + (k + 1) % 16, 1 + k] for k in range(16)]
        mb.add(V, F, 3, w='TS_Trunk2')
        # pupil + glint (own object, bone TS_Eyes)
        V = [wrap(cx, EZ - 0.1, 0.80)]; F = []
        for i in range(1, 4):
            rho = i / 3
            for k in range(20):
                t = 2 * math.pi * k / 20
                V.append(wrap(cx - sg * 0.2 + 1.4 * rho * math.cos(t), EZ - 0.1 + 1.75 * rho * math.sin(t), 0.52 + 0.28 * (1 - rho * rho)))
        V[0] = wrap(cx - sg * 0.2, EZ - 0.1, 0.80)
        for k in range(20):
            F.append([0, 1 + (k + 1) % 20, 1 + k])
        for i in range(2):
            for k in range(20):
                a = 1 + i * 20 + k; b = 1 + i * 20 + (k + 1) % 20
                F.append([a, b, b + 20, a + 20])
        pup.add(V, F, 0, w='TS_Eyes')
        V = [wrap(cx - sg * 0.2 - 0.5, EZ + 0.6, 0.90)]
        for k in range(12):
            t = 2 * math.pi * k / 12
            V.append(wrap(cx - sg * 0.2 - 0.5 + 0.46 * math.cos(t), EZ + 0.6 + 0.54 * math.sin(t), 0.84))
        pup.add(V, [[0, 1 + (k + 1) % 12, 1 + k] for k in range(12)], 1, w='TS_Eyes')
    # mouth (raised dark smile line); shape key SMILE widens it
    def mouth(wd, dp, zc=21.0, th=0.45):
        V = []
        n = 15
        for i in range(n):
            u = -1 + 2 * i / (n - 1)
            x = wd * u; z = zc - dp * (1 - u * u)
            e = th * (0.55 + 0.45 * math.sqrt(max(0, 1 - u * u)))
            V += [wrap(x, z + e, -0.05), wrap(x, z, 0.42), wrap(x, z - e, -0.05)]
        return V
    V = mouth(2.7, 1.0)
    F = []
    for i in range(14):
        a = i * 3
        F += [[a, a + 3, a + 4, a + 1], [a + 1, a + 4, a + 5, a + 2]]
    m0 = mb.n
    mb.add(V, F, 0, w='TS_Trunk2')
    o_face = mb.obj('TS_Tree_Face', [m_rim, m_white, m_lid, m_blush], cC, arm=arm, sharp=80)
    o_pup = pup.obj('TS_Tree_Pupils', [m_pupil, m_white], cC, arm=arm, sharp=80)
    o_face.shape_key_add(name='Basis')
    kb = o_face.shape_key_add(name='BLINK', from_mix=False)
    for (start, rows) in lid_rows:
        for i, p in enumerate(rows):
            kb.data[start + i].co = p
    ks = o_face.shape_key_add(name='SMILE', from_mix=False)
    for i, p in enumerate(mouth(3.9, 2.0, zc=21.6, th=0.5)):
        ks.data[m0 + i].co = p
    o_face.data.shape_keys.name = 'TS_Tree_FaceKeys'
    kb.value = 0.0; ks.value = 0.0

    # sockets for props in the hands
    for side in ('L', 'R'):
        e = bpy.data.objects.new(f'TS_Tree_Socket_Hand{side}', None)
        e.empty_display_type = 'SPHERE'; e.empty_display_size = 1.5
        cC.objects.link(e)
        e.parent = arm; e.parent_type = 'BONE'; e.parent_bone = f'TS_Arm{side}_{AB:02d}'
        e.location = (0, 2.0, 0)     # bone-tail space: 2 BU beyond the tip, inside the leafy hand

    # ------------------------------------------------------------------ D: blossoms
    mb = MB()
    rng = random.Random(21)
    def cluster(p, nrm, wname, scale=1.0):
        nrm = Vector(nrm)
        t1 = nrm.orthogonal().normalized(); t2 = nrm.cross(t1)
        for j in range(rng.choice((3, 4, 4, 5))):
            a = rng.uniform(0, 6.28); rr = rng.uniform(0.5, 2.6) * scale
            d = (nrm + (t1 * math.cos(a) + t2 * math.sin(a)) * rng.uniform(0.15, 0.6)).normalized()
            c = Vector(p) + (t1 * math.cos(a) + t2 * math.sin(a)) * rr + nrm * rng.uniform(0.5, 1.1) * scale
            rad = rng.uniform(1.6, 2.3) * scale
            (pv, pf), (cv, cf) = petal_flower(rad)
            pink = rng.random() < 0.45
            mb.add(align(pv, d, c, spin=rng.uniform(0, 6)), pf, 1 if pink else 0, w=wname, shade=None,
                   col=(1, 1, 1) if pink else (1, 0.97, 0.97))
            mb.add(align(cv, d, c), cf, 2, w=wname)
            # short stalk back into the leaves so nothing floats
            sv, sf, _ = tube([c - d * 0.05, Vector(p) - nrm * 1.2], [0.16 * scale, 0.2 * scale], 5, cap1=False)
            mb.add(sv, sf, 3, w=wname, col=tint(LEAF_UNDER, LEAF_TOP))
        for j in range(2):
            a = rng.uniform(0, 6.28)
            c = Vector(p) + (t1 * math.cos(a) + t2 * math.sin(a)) * rng.uniform(0.3, 1.6) * scale + nrm * 0.1
            bv, bf = blob(c, rng.uniform(0.9, 1.3) * scale, sub=1, amp=0.1, seed=j)
            mb.add(bv, bf, rng.choice((0, 1)), w=wname, flat=True, fjit=0.05)
    for (p, nrm) in surf_points(blobs, 78, -0.25, 1.0, 5, 8.5, front_bias=0.25):
        cluster(p, nrm, 'TS_Canopy')
    for side in ('L', 'R'):
        for (p, nrm) in surf_points(tufts[side], 4, -0.3, 1.0, 9, 3.0):
            cluster(p, nrm, f'TS_Arm{side}_{AB:02d}', 0.6)
    o_blos = mb.obj('TS_Tree_Blossoms', [m_pet_w, m_pet_p, m_cen, m_leaf], cD, arm=arm, sharp=50)

    # ------------------------------------------------------------------ E: golden apples
    mb = MB()
    rng = random.Random(33)
    av, af = apple_mesh(1.9)
    for (p, nrm) in surf_points(blobs, 30, -0.75, 0.05, 8, 10.5, embed=0.99, front_bias=0.3, zworld=(46, 80)):
        hang = rng.uniform(2.0, 3.6)
        top = np.array(p) + np.array(nrm) * 0.9 - np.array((0, 0, hang))
        v = xf(av, Matrix.Translation(Vector(top) - Vector((0, 0, 1.75 * 1.9))) @ Matrix.Rotation(rng.uniform(0, 6), 4, 'Z'))
        mb.add(v, af, 0, w='TS_Canopy', col=lambda q: (1, 1, 1))
        sv, sf, _ = tube(spline([top - np.array((0, 0, 0.35)), top + np.array((0, 0, hang * 0.5)) - np.array(nrm) * 0.5, np.array(p) - np.array(nrm) * 1.6], 6), 0.22, 6, cap1=False)
        mb.add(sv, sf, 1, w='TS_Canopy', col=tint(BARK_DK, BARK))
        lv, lf = leaf(2.3, 0.45, 0.1, 0.2)
        lv = align(lv, Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), -0.25)), top + np.array((0, 0, 0.2)), axis='Y')
        mb.add(lv, lf, 2, w='TS_Canopy')
    o_app = mb.obj('TS_Tree_Apples', [m_gold, m_bark, m_leaf], cE, arm=arm, sharp=50)

    # ------------------------------------------------------------------ poses
    poses = {}
    acts = []
    LN = [f'TS_ArmL_{i + 1:02d}' for i in range(AB)]
    RN = [f'TS_ArmR_{i + 1:02d}' for i in range(AB)]

    def lean(a1, a2, a3, ac):
        for bn, a in (('TS_Trunk1', a1), ('TS_Trunk2', a2), ('TS_Trunk3', a3), ('TS_Canopy', ac)):
            if a:
                pose_rot(arm, bn, 'X', a)

    def chain(names, path):
        pb = arm.pose.bones[names[0]]
        bpy.context.view_layer.update()
        start = np.array(pb.matrix.translation[:])
        pose_chain(arm, names, walk([start] + list(path), AL, AB, start=start))

    def store(name):
        acts.append(save_action(arm, name)); poses[name] = pose_dict(arm)

    pose_reset(arm); store('TS_TREE_REST')

    # HUG: both arms wrap a troll standing at (0, -17, 0)
    pose_reset(arm); lean(2, 2, 3, 4)
    for names, s, zh in ((LN, 1, 7.8), (RN, -1, 4.3)):
        Rw, ty = 7.6, -18.5
        path = [(14 * s, -2, 38), (25 * s, -8, 31), (25 * s, -17, 18), (16 * s, -20, zh + 3)]
        for ph in range(0, 300, 20):
            path.append((s * Rw * math.cos(R(ph)), ty - Rw * math.sin(R(ph)), zh))
        chain(names, path)
    pose_move(arm, 'TS_Eyes', (0, 0, -0.75))
    store('TS_TREE_HUG')

    # GIVE: the left arm (+X) reaches far forward and down, hand socket ends near (15, -52, 12)
    pose_reset(arm); lean(4, 4, 4, 3)
    chain(LN, [(12, -6, 36), (18, -21, 33), (18.5, -36, 25), (16, -47, 16), (14, -54, 11)])
    pose_move(arm, 'TS_Eyes', (0, 0, -0.6))
    store('TS_TREE_GIVE')

    # PROTECT: lean over a kid at (0, -15, 0), arms curl round with a gap at the front
    pose_reset(arm); lean(4, 5, 6, 9)
    for names, s in ((LN, 1), (RN, -1)):
        chain(names, [(13 * s, -5, 32), (23 * s, -14, 22), (24.5 * s, -26, 11.5), (18 * s, -36, 7), (10 * s, -40.5, 6.5)])
    pose_move(arm, 'TS_Eyes', (0, 0, -1.0))
    store('TS_TREE_PROTECT')

    # LEAN: a plain lean forward
    pose_reset(arm); lean(5, 6, 6, 5)
    store('TS_TREE_LEAN')

    # LOOKDOWN: eyes only
    pose_reset(arm)
    pb = arm.pose.bones['TS_Eyes']; pose_move(arm, 'TS_Eyes', (0, 0, -1.0))
    arm.animation_data.action = a = bpy.data.actions.new('TS_TREE_LOOKDOWN')
    pb.keyframe_insert('location', frame=1); a.use_fake_user = True
    arm.animation_data.action = None
    try:
        a.asset_mark()
    except Exception:
        pass
    acts.append(a); poses['TS_TREE_LOOKDOWN'] = {'TS_Eyes': {'loc': [round(x, 5) for x in pb.location]}}
    pose_reset(arm)
    push_nla(arm, acts)
    return {'poses': poses, 'arm': arm}


# =====================================================================================================
def build_oak(root):
    C = coll('TS_ChampionOak', root)
    m_bark = mat('OakBark', OAK_BARK, 0.9)
    m_leaf = mat('OakLeaf', OAK_LEAF, 0.8)
    m_gold = mat('RosetteGold', '#E9B93A', 0.35, spec=0.6)
    m_blue = mat('RosetteBlue', '#2F5FB0', 0.6)
    prof = [(-1, 6.6), (0, 6.0), (1.5, 4.6), (4, 3.8), (9, 3.4), (13, 3.5), (16, 4.0), (19, 3.0)]
    mb = MB()
    zs = np.concatenate([np.linspace(-1, 4, 7), np.linspace(5, 19, 12)])
    SEG = 24
    dk = np.array(tint('#4A3A2A', OAK_BARK))
    V, F = [], []
    for z in zs:
        for k in range(SEG):
            th = 2 * math.pi * k / SEG
            r = trunk_R(z, prof) * (1 + 0.05 * math.cos(6 * th + 0.3 * z))
            V.append((r * math.sin(th), -r * math.cos(th), z))
    for i in range(len(zs) - 1):
        for k in range(SEG):
            a, b = i * SEG + k, i * SEG + (k + 1) % SEG
            F.append([a, a + SEG, b + SEG, b])
    F.append(list(range(SEG))); F.append([(len(zs) - 1) * SEG + k for k in range(SEG)][::-1])

    def bark_col(p):
        th = math.atan2(p[0], -p[1])
        g = (0.5 + 0.5 * math.cos(6 * th + 0.3 * p[2])) ** 0.7
        return dk + (1 - dk) * (0.3 + 0.7 * g)
    mb.add(V, F, 0, col=bark_col, shade=(-1, 8, 0.8))
    for i in range(6):
        a = 2 * math.pi * i / 6 + 0.5
        dx, dy = math.sin(a), -math.cos(a)
        pts = spline([(dx * 2.5, dy * 2.5, 3.6), (dx * 5.2, dy * 5.2, 1.3), (dx * 8.5, dy * 8.5, -0.6)], 9)
        tv, tf, _ = tube(pts, np.linspace(1.9, 0.6, 9), 8, cap1=True)
        mb.add(tv, tf, 0, col=bark_col, shade=(-1, 8, 0.8))
    for (ex, ey, ez) in ((13, -2, 24), (-12, -3, 23.5), (4, 11, 25), (-5, -10, 26), (0, 0, 30)):
        pts = spline([(ex * 0.08, ey * 0.08, 14), (ex * 0.5, ey * 0.5, 19.5), (ex, ey, ez)], 8)
        tv, tf, _ = tube(pts, np.linspace(2.2, 1.0, 8), 8, cap1=True)
        mb.add(tv, tf, 0, col=bark_col)
    rng = random.Random(5)
    spec = [((0, 0, 29), (15, 14, 9.5))]
    for i in range(7):
        a = 2 * math.pi * i / 7 + 0.3; rr = 13 + rng.uniform(-1, 1)
        spec.append(((rr * math.cos(a), rr * math.sin(a) * 0.92, 25 + rng.uniform(-1.5, 1.5)), 8.3 + rng.uniform(-0.8, 1.0)))
    for i in range(4):
        a = 2 * math.pi * i / 4 + 0.9
        spec.append(((7 * math.cos(a), 7 * math.sin(a), 33.5), 7.0))
    blobs = canopy_blobs(spec, 40.0, 17.0, 500)
    add_canopy(mb, blobs, 1, OAK_UNDER, OAK_LEAF, None, 18, 40)
    # champion's rosette on the trunk
    ry = -trunk_R(7.5, prof) * 1.04
    V, F = lathe([(1.45, 0), (1.45, 0.12), (1.05, 0.2), (0.001, 0.34)], 20, cap_top=False)
    for i in range(len(V)):
        a = math.atan2(V[i][1], V[i][0]); rr = math.hypot(V[i][0], V[i][1])
        if rr > 1.2:
            V[i][:2] *= 1 + 0.10 * math.cos(10 * a)
    V = xf(V, Matrix.Translation((0, ry, 7.5)) @ Matrix.Rotation(R(90), 4, 'X'))
    mb.add(V, F, 2)
    for sg in (-1, 1):
        bv, bf = box((0.75, 0.12, 2.6), (0, 0, -1.2), 0.04)
        bv = xf(bv, Matrix.Translation((sg * 0.42, ry + 0.02, 7.0)) @ Matrix.Rotation(R(sg * 14), 4, 'Y'))
        mb.add(bv, bf, 3)
    o = mb.obj('TS_ChampionOak', [m_bark, m_leaf, m_gold, m_blue], C, sharp=50)
    return o


def build_bushes(root):
    C = coll('TS_Bushes', root)
    m_leaf = mat('BushLeaf', '#7FB552', 0.85)
    m_bark = mat('OakBark', OAK_BARK, 0.9)
    m_berry = mat('BushBerry', '#C8372D', 0.45, spec=0.5)
    m_pet = mat('BlossomWhite', '#FFF8F4', 0.7)
    under = '#3F7A36'
    defs = {
        'TS_Bush_01': ([((0, 0, 1.9), (2.4, 2.2, 1.9)), ((1.5, 0.3, 1.4), 1.5), ((-1.5, -0.2, 1.5), 1.6), ((0.2, -0.9, 2.9), 1.3), ((-0.3, 1.0, 1.3), 1.4)], 4.0, None),
        'TS_Bush_02': ([((0, 0, 2.2), (1.9, 1.8, 2.2)), ((0.9, 0.2, 3.7), 1.35), ((-1.0, 0.1, 1.5), 1.5), ((1.2, -0.4, 1.3), 1.3), ((-0.2, -0.2, 4.2), 0.9)], 5.0, 'flowers'),
        'TS_Bush_03': ([((0, 0, 1.3), (2.3, 2.0, 1.4)), ((1.9, 0.2, 1.1), 1.3), ((-1.9, 0.1, 1.15), 1.35), ((0.3, -0.5, 2.1), 1.0), ((-0.7, 0.8, 1.8), 1.0)], 3.0, 'berries'),
    }
    out = []
    for i, (name, (spec, top, extra)) in enumerate(defs.items()):
        mb = MB()
        blobs = canopy_blobs(spec, top, 0.0, 700 + i * 10)
        for b in blobs:
            b['c'][2] = max(b['c'][2], b['r'][2] * 0.55)
        add_canopy(mb, blobs, 0, under, '#7FB552', None, 0, top, sub=2)
        tv, tf, _ = tube([(0, 0, -0.2), (0, 0, 1.2)], [0.5, 0.35], 8, cap1=False)
        mb.add(tv, tf, 1)
        rng = random.Random(i)
        if extra == 'berries':
            for (p, nrm) in surf_points(blobs, 16, -0.2, 1.0, 3, 0.75, embed=0.98):
                if p[2] < 0.4:
                    continue
                bv, bf = blob(p, 0.2, sub=1, amp=0)
                mb.add(bv, bf, 2)
        if extra == 'flowers':
            for (p, nrm) in surf_points(blobs, 12, 0.0, 1.0, 4, 0.9, embed=0.99):
                (pv, pf), (cv, cf) = petal_flower(0.34)
                mb.add(align(pv, nrm, p + np.array(nrm) * 0.05), pf, 3)
                mb.add(align(cv, nrm, p + np.array(nrm) * 0.05), cf, 4)
        o = mb.obj(name, [m_leaf, m_bark, m_berry, m_pet, mat('BlossomCentre', '#F3C64A', 0.7)], C, sharp=50)
        o.location = ((i - 1) * 8.0, 0, 0)
        out.append(o)
    return out
