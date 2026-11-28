"""Backlot kit, part 2: pieces for the castle courtyard, forest edge and harbor sets.
Same conventions as kit.py: metres, local frame (front = -Y, up = +Z), Kit builders b (set) / n (night)."""
import math, os, random
from mathutils import Vector
import bpy
import geo, mats, kit

PI = math.pi
HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, 'art')


# ----------------------------------------------------------------------------------------------
# Banners from the pack's custom/ art (laid out by cc0_art.py); falls back to the v1 PIL banners
# ----------------------------------------------------------------------------------------------
ART_BANNERS = {
    'gold lion': ('cc0_banner_gold_lion_town.jpg', 'crown'),
    'silver tower': ('cc0_banner_silver_tower_town.jpg', 'tower'),
    'gold lion tall': ('cc0_banner_gold_lion_hall.jpg', 'crown'),
    'black dragon tall': ('cc0_banner_black_dragon_hall.jpg', 'swords'),
    'silver tower tall': ('cc0_banner_silver_tower_hall.jpg', 'tower'),
}


def art_banner(design):
    """Design name usable with kit.flat_banner / kit.pole_banner.  'gold lion' / 'silver tower' have the
    0.9 x 2.55 m aspect, '... tall' the 1.15 x 4.4 m aspect."""
    fn, fallback = ART_BANNERS[design]
    path = os.path.join(ART, fn)
    if not os.path.exists(path):
        return fallback
    if bpy.data.materials.get(mats.PREFIX + 'Banner ' + design) is None:
        mats.image_material('Banner ' + design, path, base='Cloth White', **mats.ART_LIFT)
    return design


# ----------------------------------------------------------------------------------------------
# Fortification
# ----------------------------------------------------------------------------------------------
def crenel_wall(K, x0, x1, h, t, mat='Ashlar Grey', cap='Limestone', merlon=0.9, gap=0.7, mh=1.0, walk=True,
                inner_parapet=False, holes=(), body=True):
    """Curtain wall along local X from x0 to x1, outer face at y=0 (normal -Y), thickness t (+Y), height h,
    merlons on the outer edge.  holes: [(xa, xb, z_top)] passages (e.g. a gate arch handled elsewhere)."""
    b = K.b
    segs = [(x0, x1)]
    for xa, xb, zt in holes:
        nxt = []
        for a, c in segs:
            if xb <= a or xa >= c:
                nxt.append((a, c))
                continue
            if xa > a:
                nxt.append((a, xa))
            if xb < c:
                nxt.append((xb, c))
        segs = nxt
    if body:
        for a, c in segs:
            b.box(a, 0.0, -0.3, c, t, h, mat)
        for xa, xb, zt in holes:
            b.box(xa, 0.0, zt, xb, t, h, mat)
    # string course under the parapet
    b.box(x0, -0.12, h - 0.3, x1, 0.02, h - 0.08, cap, 0.02)
    # parapet + merlons on the outer edge
    pt = 0.55
    b.box(x0, 0.0, h, x1, pt, h + 0.55, mat)
    L = x1 - x0
    n = max(1, int((L + gap) / (merlon + gap)))
    step = L / n
    for i in range(n):
        xm = x0 + i * step + (step - merlon) / 2
        b.box(xm, -0.03, h + 0.55, xm + merlon, pt + 0.03, h + 0.55 + mh, mat, 0.02)
        b.box(xm - 0.04, -0.06, h + 0.55 + mh, xm + merlon + 0.04, pt + 0.06, h + 0.62 + mh, cap, 0.015)
    if inner_parapet:
        b.box(x0, t - 0.4, h, x1, t, h + 0.9, mat)
    if walk:
        b.box(x0, pt, h - 0.02, x1, t, h + 0.04, 'Limestone')


def round_tower(K, x, y, r, h, mat='Ashlar Grey', roof='Roof Slate', roof_h=None, slits=3, lit=False, seed=0):
    """Round tower (bottom at z=0) with a corbelled crenellated top and a conical roof."""
    b = K.b
    rng = random.Random(seed)
    b.lathe([(r * 1.08, -0.3), (r * 1.08, 0.6), (r, 1.0), (r, h)], mat, 28, (x, y, 0), cap_top=False)
    # corbel ring + parapet
    b.lathe([(r, h), (r + 0.35, h + 0.45), (r + 0.35, h + 1.4), (r - 0.25, h + 1.4), (r - 0.25, h + 0.6)],
            mat, 28, (x, y, 0), cap_top=False)
    for k in range(10):
        a = 2 * PI * k / 10
        c = Vector((x + (r + 0.05) * math.cos(a), y + (r + 0.05) * math.sin(a), h + 1.4 + 0.45))
        b.cbox(tuple(c), (0.6, 0.85, 0.9), mat, 0.02, rot=(0, 0, a))
    for k in range(slits):
        a = rng.uniform(0, 2 * PI)
        z = rng.uniform(2.5, h - 2.0)
        c = (x + (r + 0.01) * math.cos(a), y + (r + 0.01) * math.sin(a), z)
        b.cbox(c, (0.05, 0.16, 1.1), 'Charcoal', 0.0, rot=(0, 0, a))
        if lit and k == 0:
            K.n.cbox((x + (r + 0.02) * math.cos(a), y + (r + 0.02) * math.sin(a), z), (0.03, 0.14, 1.0), 'Glass Window Lit', 0.0, rot=(0, 0, a))
    rh = roof_h or r * 1.9
    b.lathe([(r + 0.55, h + 1.2), (r * 0.35, h + 1.2 + rh * 0.72), (0.05, h + 1.2 + rh)], roof, 28, (x, y, 0), cap_top=True)
    b.cyl((x, y, h + 1.2 + rh - 0.1), (x, y, h + 1.2 + rh + 1.1), 0.03, 'Iron Black', 6)
    b.sphere((x, y, h + 1.2 + rh + 0.05), 0.12, 'Gold', 8, 6)
    return h + 1.2 + rh


def wall_torch(K, x, y, z, out=0.35):
    """Torch in an iron bracket on a wall plane at y (normal -Y): flame by night (+ warm light)."""
    b = K.b
    b.box(x - 0.05, y - 0.03, z - 0.25, x + 0.05, y, z + 0.05, 'Iron Black', 0.005)
    b.cyl((x, y, z - 0.15), (x, y - out, z + 0.1), 0.018, 'Iron Black', 6)
    b.lathe([(0.03, 0), (0.07, 0.12), (0.075, 0.16)], 'Iron Black', 8, (x, y - out, z + 0.08), cap_top=False)
    b.cyl((x, y - out, z - 0.35), (x, y - out, z + 0.2), 0.035, 'Timber Dark', 8)
    b.sphere((x, y - out, z + 0.22), 0.06, 'Charcoal', 8, 6, (1, 1, 0.7))
    kit.flame(K.n, (x, y - out, z + 0.24), 0.42, 0.09, 'Flame', 10)
    K.light((x, y - out - 0.05, z + 0.5), 140, '#ff8a35', 0.08)


def brazier(K, x, y, z=0.0, s=1.0, lit_day=False):
    """Iron fire basket on a tripod.  Flames + light only at night unless lit_day."""
    b = K.b
    nb = b if lit_day else K.n
    with K.push((x, y, z)):
        for k in range(3):
            a = 2 * PI * k / 3
            b.beam((0.42 * s * math.cos(a), 0.42 * s * math.sin(a), 0.0), (0.18 * s * math.cos(a), 0.18 * s * math.sin(a), 0.85 * s),
                   0.05 * s, 0.05 * s, 'Iron Black', 0.008)
        b.torus((0, 0, 0.4 * s), 0.3 * s, 0.02 * s, 'Iron Black', 16, 5, 'Z')
        b.lathe([(0.1 * s, 0.8 * s), (0.42 * s, 0.9 * s), (0.55 * s, 1.15 * s), (0.58 * s, 1.2 * s), (0.5 * s, 1.18 * s), (0.0, 1.0 * s)],
                'Iron', 16, cap_top=False)
        b.lathe([(0.47 * s, 1.1 * s), (0.0, 1.12 * s)], 'Charcoal', 14, cap_top=False)
        for k in range(7):
            a = 2 * PI * k / 7
            r_ = 0.2 * s * (0.4 + (k % 3) * 0.3)
            nb.sphere((r_ * math.cos(a), r_ * math.sin(a), 1.12 * s), 0.07 * s, 'Embers', 6, 4, (1, 1, 0.6))
        for k in range(6):
            a = 2 * PI * k / 6 + 0.3
            r_ = 0.2 * s * (k % 2) + 0.05
            hh = (0.45 + 0.22 * ((k * 7) % 3)) * s
            kit.flame(nb, (r_ * math.cos(a), r_ * math.sin(a), 1.08 * s), hh, 0.13 * s, 'Flame', 10,
                      (0.03 * math.cos(a), 0.03 * math.sin(a)), k * 1.7)
        K.light((0, 0, 1.7 * s), 420 * s, '#ff8a35', 0.3 * s)


def stair(K, x0, x1, y0, depth_per, rise, n, mat='Limestone', side=None, side_h=0.9, side_mat='Ashlar'):
    """Straight flight climbing towards +Y: step k spans y0 + k*depth_per .. and rises to (k+1)*rise.
    side: low parapet walls on both sides."""
    b = K.b
    for k in range(n):
        ya = y0 + k * depth_per
        b.box(x0, ya, -0.1, x1, y0 + n * depth_per, (k + 1) * rise, mat, 0.015)
        b.box(x0 - 0.02, ya - 0.04, (k + 1) * rise - 0.06, x1 + 0.02, ya + 0.06, (k + 1) * rise, mat, 0.01)
    if side:
        for xs in ((x0 - 0.45, x0), (x1, x1 + 0.45)):
            V = []
            for k in range(n + 1):
                yk = y0 + k * depth_per
                V.append((yk, k * rise + side_h))
            for k in range(n):
                ya, za = V[k]
                yb, zb = V[k + 1]
                b.box(xs[0], ya, -0.1, xs[1], yb, za, side_mat)
                b.box(xs[0] - 0.04, ya, za - 0.02, xs[1] + 0.04, yb, za + 0.12, 'Limestone', 0.01)


# ----------------------------------------------------------------------------------------------
# Courtyard / village props (kid-readable)
# ----------------------------------------------------------------------------------------------
def archery_target(K, x, y, rz=0.0):
    """Straw target with painted rings on an A-frame easel (faces local -Y)."""
    b = K.b
    with K.push((x, y, 0), rz):
        b.beam((-0.5, 0.35, 0), (-0.3, 0.05, 1.7), 0.07, 0.07, 'Timber Oak')
        b.beam((0.5, 0.35, 0), (0.3, 0.05, 1.7), 0.07, 0.07, 'Timber Oak')
        b.beam((0.0, 0.9, 0), (0.0, 0.25, 1.5), 0.07, 0.07, 'Timber Oak')
        with K.push((0, -0.02, 1.15), 0, PI / 2 - 0.2):
            for i, (r, m) in enumerate(((0.62, 'Hay'), (0.5, 'Cloth White'), (0.38, 'Cloth Red'), (0.26, 'Cloth White'),
                                         (0.13, 'Cloth Yellow'))):
                b.cyl((0, 0, -0.18 + 0.003 * i), (0, 0, 0.0 + 0.004 * i), r, m, 24)


def training_dummy(K, x, y, rz=0.0):
    """Straw practice dummy on a post with a bucket helmet (round, friendly)."""
    b = K.b
    with K.push((x, y, 0), rz):
        b.cyl((0, 0, -0.1), (0, 0, 1.9), 0.05, 'Timber Oak', 8)
        b.beam((-0.55, 0, 1.35), (0.55, 0, 1.35), 0.08, 0.08, 'Timber Oak')
        b.lathe([(0.0, 0.85), (0.26, 0.9), (0.3, 1.2), (0.26, 1.45), (0.12, 1.55), (0.0, 1.56)], 'Canvas Plain', 14)
        b.sphere((0, 0, 1.72), 0.17, 'Canvas Plain', 12, 8)
        b.lathe([(0.19, 1.74), (0.18, 1.95), (0.0, 1.98)], 'Iron', 14)
        for sx in (-1, 1):
            b.sphere((sx * 0.62, 0, 1.35), 0.08, 'Hay', 8, 6)
        b.box(-0.45, -0.45, -0.05, 0.45, 0.45, 0.06, 'Planks', 0.01)


def bush(K, x, y, z, r=0.8, mat='Leaf Oak', n=380, seed=None):
    """Round shrub: a dark core blob + leaf cards (cheap, reads as a bush at any distance)."""
    b = K.b
    rng = random.Random(seed if seed is not None else K.rng.random())
    b.sphere((x, y, z + r * 0.55), r * 0.78, mat, 12, 8, (1.0, 1.0, 0.72))
    V, F, U = [], [], []
    for i in range(n):
        while True:
            d = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-0.2, 1)))
            if 0.6 < d.length <= 1.0:
                break
        p = Vector((x + d.x * r, y + d.y * r, z + r * 0.55 + d.z * r * 0.72))
        s = rng.uniform(0.07, 0.12) * (r / 0.8) ** 0.5
        nn = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-0.2, 1))).normalized()
        t1 = nn.cross(Vector((0, 0, 1)) if abs(nn.z) < 0.9 else Vector((1, 0, 0))).normalized()
        t2 = nn.cross(t1)
        base = len(V)
        V += [p - t2 * s, p + t1 * s * 0.6, p + t2 * s, p - t1 * s * 0.6]
        F.append((base, base + 1, base + 2, base + 3))
        U.append([(0, 0), (0.05, 0.05), (0.1, 0), (0.05, -0.05)])
    b.mesh(V, F, mat, U, smooth=False)


def mushroom(K, x, y, z, s=1.0, cap='Apple Red'):
    """Toadstool (red cap with white spots) - storybook detail for the forest floor."""
    b = K.b
    b.lathe([(0.035 * s, 0), (0.03 * s, 0.12 * s), (0.028 * s, 0.16 * s)], 'Petal White', 8, (x, y, z), cap_top=False)
    b.sphere((x, y, z + 0.16 * s), 0.1 * s, cap, 12, 6, (1, 1, 0.55))
    rng = random.Random(int(x * 100 + y * 37))
    for k in range(5):
        a = rng.uniform(0, 2 * PI)
        e = rng.uniform(0.3, 0.8)
        b.sphere((x + 0.08 * s * e * math.cos(a), y + 0.08 * s * e * math.sin(a), z + 0.16 * s + 0.052 * s * (1 - e * e) ** 0.5 + 0.004),
                 0.014 * s, 'Petal White', 5, 3, (1, 1, 0.5))


def split_rail_fence(K, pts, h=1.1, post_every=2.4, mat='Planks Grey', post_mat='Timber Oak', ground=None, seed=1):
    """Rustic fence along a polyline [(x, y)]: posts + two (sometimes sagging) rails.  ground(x, y) -> z."""
    b = K.b
    rng = random.Random(seed)
    gz = ground or (lambda x, y: 0.0)
    posts = []
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        L = math.hypot(bx - ax, by - ay)
        n = max(1, int(round(L / post_every)))
        for k in range(n + (1 if (bx, by) == pts[-1] else 0)):
            t = k / n
            posts.append((ax + (bx - ax) * t, ay + (by - ay) * t))
    tops = []
    for i, (x, y) in enumerate(posts):
        z = gz(x, y)
        lean = (rng.uniform(-0.04, 0.04), rng.uniform(-0.04, 0.04))
        top = (x + lean[0], y + lean[1], z + h + rng.uniform(-0.05, 0.05))
        b.beam((x, y, z - 0.3), top, 0.13, 0.13, post_mat, 0.02)
        b.cyl((top[0], top[1], top[2] - 0.02), (top[0], top[1], top[2] + 0.06), 0.075, post_mat, 6)
        tops.append(top)
    for i in range(len(tops) - 1):
        a, c = Vector(tops[i]), Vector(tops[i + 1])
        if rng.random() < 0.06:
            continue          # a missing rail now and then
        for fz in (0.3, 0.72):
            p = Vector((a.x, a.y, gz(a.x, a.y) + h * fz))
            q = Vector((c.x, c.y, gz(c.x, c.y) + h * fz + rng.uniform(-0.04, 0.04)))
            b.beam(p, q, 0.08, 0.12, mat, 0.015, roll=rng.uniform(-0.1, 0.1))
    return posts


def signpost(K, x, y, z, boards, h=2.4):
    """Wooden signpost; boards: [(art_png_path, angle_deg, z_offset)] arrow boards with painted words."""
    b = K.b
    b.cyl((x, y, z - 0.4), (x, y, z + h), 0.075, 'Timber Oak', 10)
    b.lathe([(0.11, z + h), (0.0, z + h + 0.14)], 'Timber Dark', 10, (x, y, 0), cap_top=False)
    for path, ang, dz in boards:
        name = 'Sign ' + os.path.splitext(os.path.basename(path))[0]
        if bpy.data.materials.get(mats.PREFIX + name) is None:
            mats.image_material(name, path, base='Planks Pale')
        with K.push((x, y, z + h - 0.35 - dz), math.radians(ang)):
            L, W_, T = 1.25, 0.32, 0.05
            # arrow board pointing +X (local), painted on both faces (UV 0..1)
            outline = [(0.08, -W_ / 2), (L - 0.22, -W_ / 2), (L, 0.0), (L - 0.22, W_ / 2), (0.08, W_ / 2)]
            for side in (-1, 1):
                yy = side * T / 2
                pts = [(px, yy, pz) for px, pz in outline]
                uv = [((px - 0.08) / (L - 0.08), (pz + W_ / 2) / W_) for px, pz in outline]
                if side > 0:
                    pts = pts[::-1]
                    uv = [(1 - u, v) for u, v in uv[::-1]]
                b.poly(pts, name, uv)
            for (pa, za), (pb, zb) in zip(outline, outline[1:] + outline[:1]):
                b.quad((pa, -T / 2, za), (pb, -T / 2, zb), (pb, T / 2, zb), (pa, T / 2, za), 'Planks Pale')
            b.cyl((0.04, -T / 2 - 0.01, 0), (0.04, T / 2 + 0.01, 0), 0.02, 'Iron Black', 6)


# ----------------------------------------------------------------------------------------------
# Harbor
# ----------------------------------------------------------------------------------------------
def dock(K, x0, x1, y0, y1, z, water_z, bed_z, plank='Planks', post='Timber Dark', post_every=2.2, rail=None, seed=3):
    """Timber jetty: deck of planks at z over posts down to the bed, stringers, cross-bracing."""
    b = K.b
    rng = random.Random(seed)
    L, W = x1 - x0, y1 - y0
    along_x = L >= W
    # deck boards (each board a separate box so the edge is ragged and grain follows the board)
    bw = 0.22
    if along_x:
        n = int(W / bw)
        for i in range(n):
            ya = y0 + i * W / n
            off = rng.uniform(-0.06, 0.06)
            b.box(x0 + off, ya + 0.008, z - 0.06, x1 + rng.uniform(-0.06, 0.06), ya + W / n - 0.008, z + rng.uniform(-0.005, 0.005), plank, 0.006,
                  grain=(1, 0, 0))
    else:
        n = int(L / bw)
        for i in range(n):
            xa = x0 + i * L / n
            b.box(xa + 0.008, y0 + rng.uniform(-0.06, 0.06), z - 0.06, xa + L / n - 0.008, y1 + rng.uniform(-0.06, 0.06),
                  z + rng.uniform(-0.005, 0.005), plank, 0.006, grain=(0, 1, 0))
    # stringers + posts
    span = L if along_x else W
    npost = max(1, int(span / post_every))
    for k in range(npost + 1):
        t = k / npost
        for side in (0, 1):
            if along_x:
                px, py = x0 + 0.1 + (L - 0.2) * t, (y0 + 0.12) if side == 0 else (y1 - 0.12)
            else:
                px, py = (x0 + 0.12) if side == 0 else (x1 - 0.12), y0 + 0.1 + (W - 0.2) * t
            b.cyl((px, py, bed_z - 0.3), (px, py, z + (0.5 if rail else 0.12)), 0.13, post, 10)
            b.cyl((px, py, water_z - 0.25), (px, py, water_z + 0.2), 0.142, 'Leaf Oak', 10)   # weed band at the waterline
    for side in (0, 1):
        if along_x:
            yy = (y0 + 0.12) if side == 0 else (y1 - 0.12)
            b.box(x0, yy - 0.08, z - 0.3, x1, yy + 0.08, z - 0.06, post)
        else:
            xx = (x0 + 0.12) if side == 0 else (x1 - 0.12)
            b.box(xx - 0.08, y0, z - 0.3, xx + 0.08, y1, z - 0.06, post)
    if rail:
        for side in (0, 1):
            if along_x:
                yy = (y0 + 0.12) if side == 0 else (y1 - 0.12)
                b.beam((x0, yy, z + 0.45), (x1, yy, z + 0.45), 0.09, 0.09, rail)
            else:
                xx = (x0 + 0.12) if side == 0 else (x1 - 0.12)
                b.beam((xx, y0, z + 0.45), (xx, y1, z + 0.45), 0.09, 0.09, rail)


def bollard(K, x, y, z, rope=True):
    b = K.b
    b.lathe([(0.16, 0), (0.15, 0.32), (0.21, 0.4), (0.21, 0.46), (0.0, 0.48)], 'Iron Black', 14, (x, y, z))
    if rope:
        b.torus((x, y, z + 0.18), 0.19, 0.035, 'Rope', 16, 6, 'Z')


def rope_coil(K, x, y, z, r=0.35, turns=4):
    b = K.b
    for k in range(turns):
        b.torus((x, y, z + 0.035 + k * 0.06), r - k * 0.035, 0.032, 'Rope', 18, 6, 'Z')


def boat(K, x, y, z, rz=0.0, L=6.0, W=2.0, H=0.9, hull='Paint Blue', trim='Paint Yellow', sail=None, mast=True, seed=0,
         lantern_night=False, oars=False):
    """Clinker-style wooden boat (bow +X), keel at z - draft.  sail: cloth material for a furled/raised sail.
    Built in its own frame; floats with its waterline at z."""
    b = K.b
    draft = H * 0.45
    with K.push((x, y, z - draft), rz):
        nst = 14
        rows = 6
        # hull stations along X: half-width and sheer height, keel rocker
        def half_w(t):
            return W / 2 * (1 - abs(2 * t - 1) ** 2.4) ** 0.7 + 0.02

        def sheer(t):
            return H + 0.28 * (2 * t - 1) ** 2

        V, F, FM, UV = [], [], [], []
        for i in range(nst + 1):
            t = i / nst
            xs = -L / 2 + L * t
            hw = half_w(t)
            for j in range(rows + 1):
                s = j / rows                     # 0 at keel, 1 at gunwale
                ang = s * PI / 2
                yy = hw * math.sin(ang) ** 0.8
                zz = sheer(t) * (1 - math.cos(ang)) ** 0.9 * 0.98 + 0.02
                V.append(Vector((xs, -yy, zz)))
        for side in (-1, 1):
            base = len(V)
            off = 0 if side < 0 else None
        # mirror for the +Y side
        n0 = len(V)
        V += [Vector((v.x, -v.y, v.z)) for v in V[:n0]]
        per = rows + 1
        for i in range(nst):
            for j in range(rows):
                a = i * per + j
                q = (a, a + per, a + per + 1, a + 1)
                F.append(q); FM.append(hull if j < rows - 1 else trim)
                F.append(tuple(n0 + k for k in q[::-1])); FM.append(hull if j < rows - 1 else trim)
        b.mesh(V, F, FM, None, smooth=True)
        # inside of the hull (darker planks), slightly inset
        Vi = [Vector((v.x * 0.97, v.y * 0.9, max(v.z, 0.12) + 0.0)) for v in V]
        Fi = [f[::-1] for f in F]
        b.mesh(Vi, Fi, 'Planks Grey', None, smooth=True)
        # gunwale rail, thwarts, keel, stem posts
        for side in (-1, 1):
            pts = []
            for i in range(nst + 1):
                t = i / nst
                pts.append(Vector((-L / 2 + L * t, side * half_w(t), sheer(t) + 0.02)))
            for p, q in zip(pts, pts[1:]):
                b.beam(p, q, 0.07, 0.06, 'Timber Oak', 0.01)
        for tt in (0.3, 0.55, 0.78):
            hw = half_w(tt) * 0.92
            b.box(-L / 2 + L * tt - 0.12, -hw, H * 0.62, -L / 2 + L * tt + 0.12, hw, H * 0.68, 'Planks Pale', 0.01)
        b.beam((-L / 2 - 0.05, 0, 0.02), (L / 2 + 0.05, 0, 0.02), 0.1, 0.1, 'Timber Dark')
        b.beam((L / 2 + 0.02, 0, 0.0), (L / 2 + 0.12, 0, sheer(1.0) + 0.25), 0.1, 0.1, 'Timber Dark')
        b.beam((-L / 2 - 0.02, 0, 0.0), (-L / 2 - 0.1, 0, sheer(0.0) + 0.15), 0.1, 0.1, 'Timber Dark')
        if mast:
            mh = L * 1.05
            mx = L * 0.08
            b.cyl((mx, 0, 0.1), (mx, 0, mh), 0.075, 'Timber Oak', 10, 0.05)
            b.sphere((mx, 0, mh + 0.02), 0.09, trim, 8, 6)
            b.cyl((mx - 0.02, 0, mh * 0.88), (mx - 0.02, 0, mh * 0.88), 0.05, 'Timber Oak', 6)
            yard_w = W * 1.25
            b.cyl((mx + 0.08, -yard_w / 2, mh * 0.86), (mx + 0.08, yard_w / 2, mh * 0.86), 0.045, 'Timber Oak', 8)
            # stays
            for p in ((L / 2 + 0.1, 0, sheer(1.0) + 0.2), (-L / 2, 0, sheer(0.0) + 0.1), (mx, -half_w(0.55), H + 0.05), (mx, half_w(0.55), H + 0.05)):
                b.cyl(p, (mx, 0, mh * 0.95), 0.012, 'Rope', 4)
            if sail:
                # square sail hanging from the yard, gently bellied (both faces)
                def sp(s, t):
                    yy = -yard_w / 2 * 0.95 + yard_w * 0.95 * s
                    zz = mh * 0.86 - 0.08 - t * mh * 0.52
                    belly = 0.35 * math.sin(PI * s) * math.sin(PI * min(1, t * 1.1)) + 0.05
                    return (mx + 0.14 + belly, yy, zz)
                b.grid(8, 8, sp, sail, (yard_w, mh * 0.52), smooth=True, both=True)
        if oars:
            for side in (-1, 1):
                b.cyl((0.2, side * 0.3, H * 0.7), (-1.6, side * (W / 2 + 1.1), 0.1), 0.03, 'Timber Oak', 6)
                b.cbox((-1.75, side * (W / 2 + 1.2), 0.05), (0.45, 0.04, 0.16), 'Timber Oak', 0.005, rot=(0, 0, side * 0.5))
        if lantern_night:
            kit.lantern(K, (L * 0.08 + 0.15, 0.25, H * 0.68), 0.9)
        # cargo: crate + barrel + coil
        kit.crate(K, -L * 0.22, 0.15, H * 0.3, (0.5, 0.42, 0.36), rz=0.2)
        kit.barrel(K, L * 0.25, -0.2, H * 0.28, 0.2, 0.55)
        rope_coil(K, -L * 0.35, -0.2, H * 0.3, 0.22, 3)


def gull(K, x, y, z, rz=None, fly=False):
    """Seagull (white body, grey wings, yellow beak)."""
    b = K.b
    rng = K.rng
    rz = rng.uniform(0, 2 * PI) if rz is None else rz
    with K.push((x, y, z), rz):
        b.sphere((0, 0, 0.12), 0.1, 'Petal White', 10, 6, (1.6, 0.8, 0.8))
        b.sphere((0.15, 0, 0.2), 0.055, 'Petal White', 8, 6)
        b.cyl((0.19, 0, 0.2), (0.27, 0, 0.19), 0.015, 'Petal Yellow', 5, 0.004)
        for side in (-1, 1):
            if fly:
                b.poly([(0.05, side * 0.06, 0.15), (-0.08, side * 0.06, 0.15), (-0.05, side * 0.42, 0.24), (0.02, side * 0.4, 0.26)], 'Feather Grey')
            else:
                b.poly([(0.06, side * 0.085, 0.15), (-0.2, side * 0.085, 0.13), (-0.12, side * 0.09, 0.19)], 'Feather Grey')
        b.poly([(-0.12, -0.04, 0.12), (-0.26, -0.05, 0.12), (-0.26, 0.05, 0.12), (-0.12, 0.04, 0.12)], 'Feather Grey')
        if not fly:
            for side in (-1, 1):
                b.cyl((0, side * 0.03, 0.0), (0, side * 0.03, 0.07), 0.008, 'Petal Yellow', 4)


# ----------------------------------------------------------------------------------------------
# Instancing: build a few prototypes, place many linked copies (Cycles shares the geometry)
# ----------------------------------------------------------------------------------------------
def build_proto(name, fn, set_col, night_col, light_col, seed=1):
    """Build one prototype with fn(K) at the origin; returns its parent empty (children = meshes)."""
    K = kit.Kit(name, seed)
    fn(K)
    parent, objs = K.finish(set_col, night_col, light_col, loc=(0, 0, 0))
    return parent


def place(proto, col, name, loc, rz=0.0, scale=1.0, first=False):
    """Put a prototype at loc (metres).  first=True moves the prototype itself, otherwise a linked copy
    (new empty + object copies that share the mesh data) is made."""
    if first:
        e = proto
    else:
        e = bpy.data.objects.new(name, None)
        e.empty_display_type = 'PLAIN_AXES'
        e.empty_display_size = 2.0
        col.objects.link(e)
        for ch in proto.children:
            o = ch.copy()
            o.parent = e
            o.matrix_parent_inverse = ch.matrix_parent_inverse.copy()
            for c in ch.users_collection:
                c.objects.link(o)
    e.location = Vector(loc) * geo.M
    e.rotation_euler = (0, 0, rz)
    e.scale = (scale, scale, scale)
    return e
