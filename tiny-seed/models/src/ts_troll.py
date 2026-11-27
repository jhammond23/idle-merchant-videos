# Tiny Seed: the baby rock troll (~16 BU) and its mother (~450 BU). Same design language, own drawn faces.
import os
from mathutils.bvhtree import BVHTree
from ts_lib import *
from ts_tree import petal_flower, canopy_blobs, add_canopy
import ts_faces

HERE = os.path.dirname(os.path.abspath(__file__))


class Troll:
    def __init__(s, K, rock_mat, seed):
        s.K = K; s.mb = MB(); s.rocks = []; s.seed = seed; s.rng = random.Random(seed); s.bvh = None

    def rock(s, c, r, bone, sub=3, amp=0.05, cuts=3, col=(1, 1, 1), floor=None, front_keep=False, zsh=None):
        s.seed += 1
        K = s.K
        r = (r, r, r) if np.isscalar(r) else r
        v, f = ico(sub)
        rng = random.Random(s.seed)
        off = Vector((s.seed * 7.13, s.seed * 3.31, s.seed * 1.77))
        for i in range(len(v)):
            v[i] *= 1.0 + amp * 1.8 * noise.noise(Vector(v[i]) * 1.3 + off)
        for _ in range(cuts):
            d = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-0.7, 1))).normalized()
            if front_keep:
                d.y = abs(d.y) * 0.8 + 0.25; d.normalize()
            d = np.array(d[:]); dist = rng.uniform(0.86, 0.95)
            sgn = v @ d - dist; m = sgn > 0
            v[m] -= np.outer(sgn[m], d)
        v = (v * np.array(r) + np.array(c)) * K
        if floor is not None:
            v[:, 2] = np.maximum(v[:, 2], floor * K)
        z0 = (c[2] - r[2]) * K; z1 = (c[2] + r[2]) * K
        s.mb.add(v, f, 0, col=col, fjit=0.13, flat=True, w=bone, seed=s.seed, shade=(z0, z1, 0.72))
        s.rocks.append((v, f))
        s.bvh = None
        return v, f

    def hit(s, c, d, far=60):
        """point and normal on the rock surface, looking from outside toward part centre c along -d (design units in/out)."""
        if s.bvh is None:
            V, F, n = [], [], 0
            for v, f in s.rocks:
                V += v.tolist(); F += [[i + n for i in x] for x in f]; n += len(v)
            s.bvh = BVHTree.FromPolygons(V, F)
        d = Vector(d).normalized()
        o = (Vector(c) + d * far) * s.K
        loc, nrm, idx, dist = s.bvh.ray_cast(o, -d)
        if loc is None:
            return None, None
        return np.array(loc[:]), Vector(nrm)

    def moss(s, c, d, size, bone, mat_i=1, col=(1, 1, 1), thick=0.34):
        p, n = s.hit(c, d)
        if p is None:
            return None, None
        s.seed += 1
        K = s.K
        n = (n + Vector(d).normalized()).normalized()
        v, f = blob((0, 0, 0), (size * K, size * K, size * K * thick), sub=2, amp=0.16, freq=1.6, seed=s.seed)
        v = align(v, n, p - np.array(n[:]) * size * K * thick * 0.25)
        s.mb.add(v, f, mat_i, col=col, fjit=0.10, flat=True, w=bone, seed=s.seed)
        return p, n

    def boulder(s, c, d, r, bone, col=(1, 1, 1), sub=2):
        p, n = s.hit(c, d)
        if p is None:
            return
        cc = p / s.K - np.array(Vector(d).normalized()[:]) * r * 0.35
        rr = (r * s.rng.uniform(0.85, 1.15), r * s.rng.uniform(0.85, 1.15), r * s.rng.uniform(0.75, 1.0))
        s.rock(cc, rr, bone, sub=sub, amp=0.08, cuts=3, col=col, floor=0.0)

    def flower(s, p, n, h, rad, bone, pink, stem_i, pet_i, cen_i):
        K = s.K
        n = Vector(n); top = Vector(p) + n * h * K
        sv, sf, _ = tube([Vector(p) - n * 0.15 * K, top], [0.07 * K, 0.055 * K], 6, cap1=False)
        s.mb.add(sv, sf, stem_i, w=bone, col=(0.75, 0.85, 0.7))
        (pv, pf), (cv, cf) = petal_flower(rad * K, n=6, cup=0.25)
        fd = (n + Vector((0, -0.45, 0.1))).normalized()
        s.mb.add(align(pv, fd, top, spin=s.rng.uniform(0, 3)), pf, pet_i[1 if pink else 0], w=bone)
        s.mb.add(align(cv, fd, top), cf, cen_i, w=bone)

    def face_patch(s, name, head_c, a, b, atlas_n, mat_face, collection, arm, bone, zoff=0.0):
        """elliptical decal projected from the front onto the head rock; UVs cover atlas cell 0."""
        K = s.K
        s.hit(head_c, (0, -1, 0))
        V, UV, F = [], [], []
        NR, NS = 16, 56
        cx, cz = head_c[0] * K, (head_c[2] + zoff) * K

        def proj(x, z):
            loc, nrm, _, _ = s.bvh.ray_cast(Vector((x, -1000 * K, z)), Vector((0, 1, 0)))
            return Vector(loc) + Vector((0, -0.07 * K, 0)) + Vector(nrm) * 0.025 * K
        V.append(proj(cx, cz)); UV.append((0.5 / atlas_n, 0.5))
        for i in range(1, NR + 1):
            rho = i / NR
            for k in range(NS):
                t = 2 * math.pi * k / NS
                x, z = a * K * rho * math.cos(t), b * K * rho * math.sin(t)
                V.append(proj(cx + x, cz + z)); UV.append(((0.5 + 0.5 * rho * math.cos(t)) / atlas_n, 0.5 + 0.5 * rho * math.sin(t)))
        for k in range(NS):
            F.append([0, 1 + (k + 1) % NS, 1 + k])
        for i in range(NR - 1):
            for k in range(NS):
                p, q = 1 + i * NS + k, 1 + i * NS + (k + 1) % NS
                F.append([p, q, q + NS, p + NS])
        fb = MB()
        fb.add(np.array([v[:] for v in V]), F, 0, w=bone, uv=UV)
        o = fb.obj(name, [mat_face], collection, arm=arm, sharp=180)
        o['face'] = 0
        try:
            ui = o.id_properties_ui('face'); ui.update(min=0, max=atlas_n - 1, description='expression index (see MODELS.md)')
        except Exception:
            pass
        o.visible_shadow = False
        return o


def face_material(name, who, n):
    p = os.path.join(HERE, '..', 'faces', f'TS_Face_{who}_ATLAS.png')
    img = bpy.data.images.load(os.path.abspath(p)); img.name = f'TS_Face_{who}_ATLAS'
    m = image_mat(name, img, rough=0.9, atlas_n=n, prop='face')
    return m


def build(root):
    ts_faces.build()
    info = {}
    m_moss = mat('Moss', '#86B24C', 0.95)
    m_pw, m_pp, m_cen = mat('BlossomWhite', '#FFF8F4', 0.7), mat('BlossomPink', '#F6B9CB', 0.7), mat('BlossomCentre', '#F3C64A', 0.7)
    m_leaf = mat('TrollTreeLeaf', '#7FB552', 0.85)
    m_bark = mat('OakBark', '#77624A', 0.9)

    # =============================================================== BABY
    C = coll('TS_TrollBaby', root)
    m_rock = mat('TrollBabyRock', '#C2BDB5', 0.9)
    bones = [('TS_Root', (0, 0, 0), (0, -3, 0), None, False),
             ('TS_Body', (0, 0, 2.4), (0, 0, 7.0), 'TS_Root', False),
             ('TS_Head', (0, 0, 7.0), (0, 0, 13.0), 'TS_Body', True)]
    for sd, s in (('L', 1), ('R', -1)):
        bones.append((f'TS_Arm{sd}', (5.0 * s, 0, 7.6), (7.6 * s, -0.5, 3.4), 'TS_Body', False))
        bones.append((f'TS_Leg{sd}', (3.0 * s, 0, 3.4), (3.0 * s, -0.2, 0.2), 'TS_Root', False))
    arm = make_arm('TS_TrollBaby_Rig', bones, C)
    T = Troll(1.0, m_rock, 40)
    warm = (1.0, 0.985, 0.96)
    for sd, s in (('L', 1), ('R', -1)):
        T.rock((3.1 * s, -0.3, 1.75), (2.35, 2.8, 2.0), f'TS_Leg{sd}', sub=2, amp=0.04, cuts=2, col=(0.9, 0.89, 0.87), floor=0.0)
    T.rock((0, 0.2, 5.5), (5.2, 4.6, 4.1), 'TS_Body', sub=3, amp=0.04, cuts=3, col=(0.93, 0.92, 0.9))
    HC = (0, -0.3, 10.7)
    T.rock(HC, (6.3, 5.4, 4.7), 'TS_Head', sub=3, amp=0.035, cuts=4, col=warm, front_keep=True)
    for sd, s in (('L', 1), ('R', -1)):
        T.rock((6.2 * s, 0, 6.6), (1.9, 1.95, 2.5), f'TS_Arm{sd}', sub=2, amp=0.04, cuts=2, col=(0.92, 0.91, 0.89))
        T.rock((7.3 * s, -0.5, 4.0), (2.05, 2.15, 2.0), f'TS_Arm{sd}', sub=2, amp=0.05, cuts=2, col=(0.97, 0.96, 0.94))
        T.rock((6.1 * s, 0.3, 13.3), (1.25, 1.1, 1.45), 'TS_Head', sub=2, amp=0.05, cuts=2, col=(0.9, 0.89, 0.87))   # ear pebbles
    # moss cap + patches
    spots = []
    for (d, sz, bone, c) in (((0.05, 0.1, 1), 4.2, 'TS_Head', HC), ((-0.8, -0.45, 0.25), 1.25, 'TS_Body', (0, 0.2, 5.5)), ((-0.55, 0.35, 0.75), 1.9, 'TS_Head', HC), ((0.6, 0.5, 0.62), 1.6, 'TS_Head', HC),
                             ((0.2, 1, 0.45), 2.2, 'TS_Head', HC), ((-0.75, 0.5, 0.35), 1.6, 'TS_Body', (0, 0.2, 5.5)),
                             ((0.5, 0.9, 0.1), 2.0, 'TS_Body', (0, 0.2, 5.5)), ((1, -0.1, 0.9), 1.0, 'TS_ArmL', (6.2, 0, 6.6)),
                             ((-1, 0.3, 0.9), 1.0, 'TS_ArmR', (-6.2, 0, 6.6)), ((0.9, -0.2, 0.2), 1.1, 'TS_Body', (0, 0.2, 5.5))):
        p, n = T.moss(c, d, sz, bone, col=(1, 1, 1) if sz > 2 else (0.88, 0.93, 0.85), thick=0.4 if sz > 4 else 0.34)
        spots.append((p, n, bone))
    # flowers and a two-leaf sprout on the head (its "hair")
    top = spots[0][0]
    for (dx, dy, h, rad, pink) in ((-1.9, -1.0, 1.5, 1.0, False), (1.6, -0.5, 1.15, 0.9, True), (0.1, 1.2, 1.7, 0.85, False), (-0.2, -2.0, 0.8, 0.7, True), (2.8, 0.9, 0.9, 0.7, False)):
        p = top + np.array((dx, dy, 0.25 - 0.05 * (dx * dx + dy * dy)))
        T.flower(p, Vector((dx * 0.12, dy * 0.12, 1)).normalized(), h, rad, 'TS_Head', pink, 1, (2, 3), 4)
    for sg in (-1, 1):
        lv, lf = leaf(1.9, 0.5, 0.12, 0.3)
        lv = align(lv, Vector((sg * 0.75, 0.1, 0.8)), top + np.array((0.2, 0.2, 0.2)), axis='Y')
        T.mb.add(lv, lf, 1, w='TS_Head', col=(0.95, 1, 0.9))
    sv, sf, _ = tube([top + np.array((0.2, 0.2, -0.2)), top + np.array((0.2, 0.2, 0.5))], 0.12, 6, cap1=False)
    T.mb.add(sv, sf, 1, w='TS_Head')
    ob = T.mb.obj('TS_TrollBaby_Body', [m_rock, m_moss, m_pw, m_pp, m_cen], C, arm=arm, sharp=30)
    mf = face_material('TrollBaby_Face', 'TrollBaby', 4)
    fo = T.face_patch('TS_TrollBaby_Face', HC, 4.55, 3.66, 4, mf, C, arm, 'TS_Head', zoff=0.05)
    info['troll_baby_faces'] = {e: i for i, e in enumerate(ts_faces.BABY)}

    # =============================================================== MOTHER (design units x10)
    C = coll('TS_TrollMother', root)
    K = 10.0
    m_rock = mat('TrollMotherRock', '#9A968E', 0.92)
    m_mossd = mat('MossOld', '#6E9A45', 0.95)
    bones = [('TS_Root', (0, 0, 0), (0, -30, 0), None, False),
             ('TS_Body', (0, 10, 100), (0, 15, 250), 'TS_Root', False),
             ('TS_Head', (0, -10, 300), (0, -40, 400), 'TS_Body', False)]
    for sd, s in (('L', 1), ('R', -1)):
        bones.append((f'TS_Arm{sd}', (125 * s, 10, 300), (185 * s, 0, 170), 'TS_Body', False))
        bones.append((f'TS_Forearm{sd}', (185 * s, 0, 170), (200 * s, -25, 40), f'TS_Arm{sd}', True))
        bones.append((f'TS_Leg{sd}', (75 * s, 5, 110), (75 * s, 5, 5), 'TS_Root', False))
    arm = make_arm('TS_TrollMother_Rig', bones, C)
    T = Troll(K, m_rock, 90)
    dark = (0.86, 0.86, 0.87); mid = (0.93, 0.925, 0.92); lite = (1.0, 0.99, 0.97)
    for sd, s in (('L', 1), ('R', -1)):
        T.rock((7.6 * s, 0.5, 5.4), (5.8, 6.8, 5.8), f'TS_Leg{sd}', sub=3, amp=0.05, cuts=4, col=dark, floor=0.0)
        T.rock((8.2 * s, -4.5, 2.2), (4.2, 4.0, 2.6), f'TS_Leg{sd}', sub=2, amp=0.06, cuts=2, col=mid, floor=0.0)
    BC = (0, 1.5, 19.5)
    T.rock(BC, (14.5, 11.5, 12.5), 'TS_Body', sub=3, amp=0.05, cuts=6, col=mid)
    T.rock((0, 8.0, 30.0), (10.5, 7.5, 7.5), 'TS_Body', sub=3, amp=0.06, cuts=4, col=dark)          # hump
    HC = (0, -5.0, 34.6)
    T.rock(HC, (8.9, 7.6, 7.0), 'TS_Head', sub=3, amp=0.035, cuts=5, col=lite, front_keep=True)
    for sd, s in (('L', 1), ('R', -1)):
        T.rock((12.8 * s, 1.5, 29.3), (7.6, 7.0, 6.2), 'TS_Body', sub=3, amp=0.06, cuts=4, col=mid)   # shoulder
        T.rock((17.6 * s, 0.5, 22.5), (4.7, 4.9, 7.6), f'TS_Arm{sd}', sub=2, amp=0.06, cuts=3, col=dark)
        T.rock((19.4 * s, -1.5, 12.6), (4.4, 4.6, 6.6), f'TS_Forearm{sd}', sub=2, amp=0.06, cuts=3, col=mid)
        T.rock((20.0 * s, -2.8, 5.4), (5.3, 5.5, 5.0), f'TS_Forearm{sd}', sub=3, amp=0.06, cuts=4, col=lite, floor=0.0)
        T.rock((8.6 * s, -3.6, 39.0), (1.9, 1.7, 2.3), 'TS_Head', sub=2, amp=0.05, cuts=2, col=dark)   # ear rocks
    rng = random.Random(4)
    # boulders stacked over body, hump and shoulders (not over the face)
    for i in range(34):
        d = Vector((rng.uniform(-1, 1), rng.uniform(-0.9, 1), rng.uniform(-0.55, 0.9))).normalized()
        T.boulder(BC, d, rng.uniform(2.6, 5.0), 'TS_Body', col=rng.choice((dark, mid, lite)))
    for i in range(10):
        d = Vector((rng.uniform(-1, 1), rng.uniform(0.2, 1), rng.uniform(0.0, 1))).normalized()
        T.boulder((0, 6.0, 30.0), d, rng.uniform(2.2, 3.8), 'TS_Body', col=rng.choice((dark, mid)))
    for d, r in (((-0.5, 0.3, 1), 2.6), ((0.55, 0.35, 0.9), 2.3), ((0.0, 0.8, 0.8), 2.9), ((0.1, 0.1, 1), 2.2)):   # crown rocks
        T.boulder(HC, d, r, 'TS_Head', col=dark)
    for sd, s in (('L', 1), ('R', -1)):
        for i in range(4):
            d = Vector((s * rng.uniform(0.3, 1), rng.uniform(-0.5, 0.8), rng.uniform(-0.6, 0.4))).normalized()
            T.boulder((17.6 * s, 0.5, 22.5), d, rng.uniform(1.6, 2.6), f'TS_Arm{sd}', col=mid)
    # moss blankets, grass and bushes
    grass = []
    mspots = [((0.0, 0.5, 1), 6.2, 'TS_Head', HC), ((-0.6, 0.6, 0.6), 3.2, 'TS_Head', HC), ((0.7, 0.5, 0.5), 2.8, 'TS_Head', HC),
              ((0, 0.6, 1), 7.5, 'TS_Body', (0, 8, 30)), ((0.3, 1, 0.3), 5.0, 'TS_Body', (0, 8, 30)), ((-0.5, 1, 0.0), 5.5, 'TS_Body', BC),
              ((0.9, 0.2, -0.1), 3.5, 'TS_Body', BC), ((-0.85, -0.3, 0.1), 3.0, 'TS_Body', BC), ((0.2, -1, -0.45), 3.4, 'TS_Body', BC)]
    for sd, s in (('L', 1), ('R', -1)):
        mspots += [((0.25 * s, -0.1, 1), 7.0, 'TS_Body', (12.8 * s, 1.5, 29.3)), ((0.9 * s, 0.3, 0.5), 3.6, 'TS_Body', (12.8 * s, 1.5, 29.3)),
                   ((s, 0.2, 0.3), 2.8, f'TS_Arm{sd}', (17.6 * s, 0.5, 22.5)), ((s * 0.8, -0.2, 0.7), 2.6, f'TS_Forearm{sd}', (19.4 * s, -1.5, 12.6)),
                   ((0.2 * s, -0.2, 1), 3.2, f'TS_Forearm{sd}', (20.0 * s, -2.8, 5.4)), ((0.3 * s, -0.6, 1), 2.4, f'TS_Leg{sd}', (8.2 * s, -4.5, 2.2)),
                   ((s, 0.4, 0.5), 3.0, f'TS_Leg{sd}', (7.6 * s, 0.5, 5.4))]
    for (d, sz, bone, c) in mspots:
        p, n = T.moss(c, d, sz, bone, mat_i=1, col=rng.choice(((1, 1, 1), (0.9, 0.95, 0.88), (0.84, 0.9, 0.8))), thick=0.3)
        if p is not None and n.z > 0.45:
            grass.append((p, n, sz, bone))
    # grass tufts (little cones) on the mossy tops
    for (p, n, sz, bone) in grass:
        for j in range(int(sz * 3)):
            a = rng.uniform(0, 6.28); rr = rng.uniform(0, sz * 0.7) * K
            q = p + np.array((math.cos(a) * rr, math.sin(a) * rr, sz * K * 0.18 * (1 - (rr / (sz * K)) ** 2) - 0.25 * K))
            h = rng.uniform(0.7, 1.3) * K
            cv, cf = lathe([(0.26 * K, 0), (0.001, h)], 5, cap_top=False)
            cv = xf(cv, Matrix.Translation(q) @ Matrix.Rotation(rng.uniform(-0.3, 0.3), 4, 'X') @ Matrix.Rotation(rng.uniform(-0.3, 0.3), 4, 'Y'))
            T.mb.add(cv, cf, 2, w=bone, col=rng.choice(((1, 1, 1), (0.85, 0.95, 0.8))), flat=True)
    # little trees and bushes riding on her shoulders, hump and head
    def little_tree(p, h, bone, seed):
        tv, tf, _ = tube([p - np.array((0, 0, 0.6 * K)), p + np.array((0, 0, h * 0.5 * K))], [0.34 * h * 0.3 * K, 0.2 * h * 0.3 * K], 7, cap1=False)
        T.mb.add(tv, tf, 3, w=bone)
        c = p + np.array((0, 0, h * 0.68 * K))
        r = h * 0.36 * K
        spec = [(c, (r, r, r * 0.9)), (c + np.array((r * 0.6, 0.1 * r, -0.25 * r)), r * 0.62), (c + np.array((-r * 0.6, -0.1 * r, -0.2 * r)), r * 0.66), (c + np.array((0, 0.2 * r, 0.55 * r)), r * 0.6)]
        bl = [{'c': np.array(cc, float), 'r': np.array((rr, rr, rr) if np.isscalar(rr) else rr, float), 'seed': seed + i} for i, (cc, rr) in enumerate(spec)]
        add_canopy(T.mb, bl, 2, '#3F7A36', '#7FB552', bone, c[2] - r, c[2] + r, sub=2)
    for i, (c, d, h, bone) in enumerate((((12.8, 1.5, 29.3), (0.35, 0.1, 1), 7.0, 'TS_Body'), ((-12.8, 1.5, 29.3), (-0.15, 0.25, 1), 5.2, 'TS_Body'),
                                         ((0, 8, 30), (0.25, 0.5, 1), 5.6, 'TS_Body'), ((-12.8, 1.5, 29.3), (-0.7, -0.2, 0.8), 3.4, 'TS_Body'),
                                         (HC, (0.35, 0.7, 1), 3.2, 'TS_Head'))):
        p, n = T.hit(c, d)
        if p is not None:
            little_tree(p, h, bone, 900 + i * 7)
    ob = T.mb.obj('TS_TrollMother_Body', [m_rock, m_mossd, m_leaf, m_bark], C, arm=arm, sharp=30)
    mf = face_material('TrollMother_Face', 'TrollMother', 2)
    fo = T.face_patch('TS_TrollMother_Face', HC, 6.3, 5.07, 2, mf, C, arm, 'TS_Head', zoff=0.2)
    info['troll_mother_faces'] = {e: i for i, e in enumerate(ts_faces.MOTHER)}

    # ------------------------------------------------------------ simple named poses
    def store_all(arm, defs, prefix):
        acts = []
        out = {}
        for name, fn in defs:
            pose_reset(arm); fn(arm)
            acts.append(save_action(arm, prefix + name)); out[prefix + name] = pose_dict(arm)
        pose_reset(arm); push_nla(arm, acts)
        return out
    ba = bpy.data.objects['TS_TrollBaby_Rig']

    def b_stomp(a, sg):
        pose_rot(a, f'TS_Leg{"L" if sg > 0 else "R"}', 'X', -32); pose_move(a, f'TS_Leg{"L" if sg > 0 else "R"}', (0, -0.6, 1.1))
        pose_rot(a, f'TS_Leg{"R" if sg > 0 else "L"}', 'X', 14)
        pose_rot(a, 'TS_Body', 'Y', -5 * sg); pose_move(a, 'TS_Body', (0, 0, 0.35))
        pose_rot(a, 'TS_ArmL', 'X', -30 * sg); pose_rot(a, 'TS_ArmR', 'X', 30 * sg); pose_rot(a, 'TS_Head', 'Y', 4 * sg)
    info['troll_baby_poses'] = store_all(ba, [
        ('REST', lambda a: None),
        ('STOMP_L', lambda a: b_stomp(a, 1)),
        ('STOMP_R', lambda a: b_stomp(a, -1)),
        ('ARMS_UP', lambda a: (pose_rot(a, 'TS_ArmL', 'Y', -125), pose_rot(a, 'TS_ArmR', 'Y', 125), pose_rot(a, 'TS_Head', 'X', -6))),
        ('HEAD_TILT', lambda a: pose_rot(a, 'TS_Head', 'Y', 12)),
        ('SIT_ROLL', lambda a: (pose_rot(a, 'TS_LegL', 'X', -70), pose_rot(a, 'TS_LegR', 'X', -70), pose_rot(a, 'TS_Body', 'X', -10),
                                pose_rot(a, 'TS_ArmL', 'Y', -60), pose_rot(a, 'TS_ArmR', 'Y', 60))),
    ], 'TS_BABY_')
    ma = bpy.data.objects['TS_TrollMother_Rig']
    info['troll_mother_poses'] = store_all(ma, [
        ('REST', lambda a: None),
        ('LOOK_DOWN', lambda a: (pose_rot(a, 'TS_Head', 'X', 22), pose_rot(a, 'TS_Body', 'X', 5))),
        ('HEAD_TURN_L', lambda a: pose_rot(a, 'TS_Head', 'Z', 28)),
        ('STEP_L', lambda a: (pose_rot(a, 'TS_LegL', 'X', -26), pose_move(a, 'TS_LegL', (0, -20, 22)), pose_rot(a, 'TS_Body', 'Y', -3),
                              pose_rot(a, 'TS_ArmR', 'X', -12), pose_rot(a, 'TS_ArmL', 'X', 8))),
        ('STEP_R', lambda a: (pose_rot(a, 'TS_LegR', 'X', -26), pose_move(a, 'TS_LegR', (0, -20, 22)), pose_rot(a, 'TS_Body', 'Y', 3),
                              pose_rot(a, 'TS_ArmL', 'X', -12), pose_rot(a, 'TS_ArmR', 'X', 8))),
        ('REACH_R', lambda a: (pose_rot(a, 'TS_ArmR', 'X', -55), pose_rot(a, 'TS_ForearmR', 'X', -25), pose_rot(a, 'TS_Head', 'X', 14))),
    ], 'TS_MOTHER_')
    return info
