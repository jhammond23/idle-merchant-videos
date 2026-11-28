"""Backlot set 2: BRIDGE & RIVER.  python3 -I build_bridge_river.py -> bridge_river/bridge_river.blend
Layout (metres): road/bridge along X, river flows along -Y (from the background towards the WIDE camera).
Bank tops z = 0, water z = -1.8, river bed about -2.9, river 21 m wide (x -10.5..10.5) - the same numbers
as the Fake Power film bridge (FP_Bridge: water -6 BU, bed -9.5 BU, river 70 BU) so either can stand in."""
import sys, os, math, time, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, '..', 'materials')]
import bpy
from mathutils import Vector
import mats, geo, look, kit, setbase

T0 = time.time()
M = geo.M
PI = math.pi
CODE, TITLE = 'BR', 'Bridge and River'
sc, master, C = setbase.start(CODE, TITLE)
SET, NIGHT = C['set'], C['NIGHT']
mats.set_global(wet=0.35)
rng = random.Random(7)
WATER = -1.8
BED = -2.9
RW = 10.5          # half river width at the waterline
BANK = 14.0        # top of the bank slope
HW = 2.55          # half width of the bridge (road 4.2 + parapets)
L2 = 20.0          # bridge half length


def V(x, y, z=0.0):
    return Vector((x * M, y * M, z * M))


def deck_z(x):
    return 3.0 - 2.8 * (x / L2) ** 2


def ground_z(x, y):
    ax = abs(x)
    n = 0.18 * math.sin(x * 0.37 + y * 0.21) * math.cos(y * 0.29) + 0.08 * math.sin(x * 1.3 + y * 0.9)
    if ax >= BANK:
        z = 0.0 + n * min(1, (ax - BANK) / 3) + (0.02 * (ax - BANK) if x < 0 else 0.0) + (0.06 * (x - 24.0) if x > 24.0 else 0.0)
    elif ax >= RW:
        t = (ax - RW) / (BANK - RW)
        z = WATER - 0.15 + (0.15 - WATER) * (t ** 1.4) + n * 0.4 * t
    else:
        t = ax / RW
        z = BED + (WATER - 0.15 - BED) * (t ** 2.2) + n * 0.3
    return z


ARCHES = [(-7.75, 5.5), (0.0, 7.0), (7.75, 5.5)]     # (centre x, span)
SPRING = -1.2


def bridge(K):
    b = K.b
    xs = [-L2 + i * (2 * L2) / 80 for i in range(81)]
    for sgn in (1, -1):                      # +1: downstream face (y=-HW, normal -Y); -1: upstream face
        yf = -HW * sgn

        def face(pts):
            q = [(px, yf, pz) for px, pz in pts]
            b.poly(q if sgn > 0 else q[::-1], 'Ashlar Bridge')
        brk = [-L2]
        for cx, sp in ARCHES:
            brk += [cx - sp / 2, cx + sp / 2]
        brk.append(L2)
        for i in range(0, len(brk), 2):
            xa, xb = brk[i], brk[i + 1]
            top = [(x, deck_z(x) - 0.25) for x in xs if xa < x < xb]
            bottom = BED - 0.4 if (abs(xa) < BANK or abs(xb) < BANK) else -1.2
            face([(xa, bottom), (xb, bottom), (xb, deck_z(xb) - 0.25)] + top[::-1] + [(xa, deck_z(xa) - 0.25)])
        for cx, sp in ARCHES:
            ap = kit.arch_pts(cx, sp, SPRING, 'round', 20)
            top = [(x, deck_z(x) - 0.25) for x in xs if cx - sp / 2 < x < cx + sp / 2]
            face(ap + [(cx + sp / 2, deck_z(cx + sp / 2) - 0.25)] + top[::-1] + [(cx - sp / 2, deck_z(cx - sp / 2) - 0.25)])
            P = kit.arch_pts(cx, sp, SPRING, 'round', 17)
            for k, ((xa, za), (xb, zb)) in enumerate(zip(P, P[1:])):
                mid = Vector(((xa + xb) / 2, (za + zb) / 2))
                tng = Vector((xb - xa, zb - za))
                Ln = tng.length
                tng.normalize()
                nrm = Vector((-tng.y, tng.x))
                hh = 0.55 if k != 8 else 0.7
                c = mid + nrm * hh / 2
                ang = math.atan2(tng.y, tng.x)
                b.cbox((c.x, yf - sgn * 0.04, c.y), (Ln - 0.015, 0.1, hh), 'Ashlar', 0.015, rot=(0, -ang, 0))
        for xa, xb in zip(xs, xs[1:]):
            za, zb = deck_z(xa) - 0.28, deck_z(xb) - 0.28
            b.beam((xa, yf - sgn * 0.07, za), (xb, yf - sgn * 0.07, zb), 0.16, 0.2, 'Limestone', 0.02, up=(0, 0, 1))
    # arch barrels (intrados)
    for cx, sp in ARCHES:
        ap = kit.arch_pts(cx, sp, SPRING, 'round', 20)
        for (xa, za), (xb, zb) in zip(ap, ap[1:]):
            b.quad((xa, -HW, za), (xa, HW, za), (xb, HW, zb), (xb, -HW, zb), 'Ashlar Bridge')
    # piers with cutwaters (pointed both ways)
    for cx in (-4.25, 4.25):
        for sy in (-1, 1):
            tip = HW + 1.6
            pts = [(cx - 0.75, sy * HW), (cx, sy * tip), (cx + 0.75, sy * HW)]
            for zb_, zt in ((BED - 0.4, SPRING + 0.6),):
                for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
                    q = [(xa, ya, zb_), (xb, yb, zb_), (xb, yb, zt), (xa, ya, zt)]
                    if sy > 0:
                        q = q[::-1]
                        q = [q[1], q[0], q[3], q[2]]
                    b.quad(*q, 'Ashlar Bridge')
            # pyramid cap
            apex = (cx, sy * (HW + 0.2), SPRING + 1.6)
            for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
                tri = [(xa, ya, SPRING + 0.6), (xb, yb, SPRING + 0.6), apex]
                b.poly(tri if sy < 0 else tri[::-1], 'Limestone')
    # deck: cobbles (displaced) + parapets with coping stones
    def deck(s, t):
        x = -L2 + 2 * L2 * s
        return (x, -HW + 0.45 + t * (2 * HW - 0.9), deck_z(x))
    b.grid(80, 6, deck, 'Cobbles Dry', (2 * L2, 2 * HW - 0.9), smooth=False)
    for sy in (-1, 1):
        yi, yo = sy * (HW - 0.45), sy * HW
        for xa, xb in zip(xs, xs[1:]):
            za, zb = deck_z(xa), deck_z(xb)
            h = 0.9
            q = [(xa, yi, za - 0.05), (xb, yi, zb - 0.05), (xb, yi, zb + h), (xa, yi, za + h)]
            b.quad(*(q if sy > 0 else q[::-1]), 'Ashlar Bridge')
            q = [(xa, yo, za - 0.3), (xb, yo, zb - 0.3), (xb, yo, zb + h), (xa, yo, za + h)]
            b.quad(*(q[::-1] if sy > 0 else q), 'Ashlar Bridge')
        # coping blocks
        x = -L2
        while x < L2 - 0.1:
            Ln = rng.uniform(0.7, 1.1)
            xb = min(x + Ln, L2)
            za, zb = deck_z(x) + 0.9, deck_z(xb) + 0.9
            ang = math.atan2(zb - za, xb - x)
            c = ((x + xb) / 2, sy * (HW - 0.225), (za + zb) / 2 + 0.09)
            b.cbox(c, (xb - x - 0.02, 0.62, 0.18), 'Limestone', 0.025, rot=(0, -ang, 0))
            x = xb
    # end pillars
    for ex in (-L2, L2):
        for sy in (-1, 1):
            z0 = deck_z(ex)
            b.box(ex - 0.35, sy * HW - 0.35, -0.5, ex + 0.35, sy * HW + 0.35, z0 + 1.4, 'Ashlar Bridge', 0.03)
            b.box(ex - 0.45, sy * HW - 0.45, z0 + 1.4, ex + 0.45, sy * HW + 0.45, z0 + 1.6, 'Limestone', 0.03)
            b.cyl((ex, sy * HW, z0 + 1.6), (ex, sy * HW, z0 + 1.66), 0.2, 'Iron Black', 8)
            kit.lantern(K, (ex, sy * HW, z0 + 1.66), 1.3)
    # bridge-centre lantern on the downstream parapet
    with K.push((0.0, -HW + 0.22, deck_z(0) + 1.08)):
        b.cyl((0, 0, 0), (0, 0, 1.4), 0.05, 'Iron Black', 8)
        b.cyl((0, 0, 1.4), (0, -0.45, 1.5), 0.025, 'Iron Black', 6)
        kit.lantern(K, (0, -0.45, 0.88), 1.1)


def terrain():
    g = geo.Builder('%s Terrain' % CODE)
    nx, ny = 150, 130

    def warp(u, half, lin=0.25):
        v = 2 * u - 1
        return half * (lin * v + (1 - lin) * v ** 3)

    def f(s, t):
        x = warp(s, 260.0, 0.2)
        y = 20.0 + warp(t, 240.0, 0.35)
        return (x, y, ground_z(x, y) + (0.0 if abs(x) < 60 else 0.05 * (abs(x) - 60) * (1 if x < 0 else 0.6)))
    g.grid(nx, ny, f, 'Riverbank', (520.0, 480.0), smooth=True)
    objs = g.finish(SET, dicing=1.0)
    return objs


def river():
    w = geo.Builder('%s River' % CODE)
    nx, ny = 50, 300
    X0, X1, Y0, Y1 = -12.2, 12.2, -220.0, 260.0
    obstacles = []   # (x, y, radius, strength)
    for cx in (-4.25, 4.25):
        for k in range(9):
            obstacles.append((cx, -HW - 1.6 + k * ((2 * HW + 3.2) / 8), 0.95, 1.0))
    rocks = [(-8.6, -9.0, 0.7), (-9.4, 6.5, 0.5), (8.9, -14.0, 0.8), (7.6, 18.0, 0.55), (-6.8, 24.0, 0.6),
             (2.5, -28.0, 0.5), (-9.8, -22.0, 0.9), (9.6, 4.0, 0.45), (-3.0, 40.0, 0.7), (6.0, -40.0, 0.6)]
    for x, y, r in rocks:
        obstacles.append((x, y, r, 1.0))
    wheel = (RW - 0.2, 20.0)

    def foam_at(x, y):
        f = 0.0
        # banks
        d = RW - abs(x)
        f = max(f, math.exp(-(max(d, 0) / 0.45) ** 2) * 0.45)
        for ox, oy, r, st in obstacles:
            dx, dy = x - ox, y - oy
            if dy < 0:
                dy_eff = dy / 4.0          # wake stretches downstream (-Y)
            else:
                dy_eff = dy / 1.2
            dd = math.hypot(dx, dy_eff) - r
            f = max(f, st * math.exp(-(max(dd, 0) / 0.4) ** 2))
        dd = math.hypot(x - wheel[0], (y - wheel[1]) / (3.0 if y < wheel[1] else 1.0)) - 1.0
        f = max(f, math.exp(-(max(dd, 0) / 0.8) ** 2))
        return min(1.0, f)

    V, F, U, A = [], [], [], []
    for j in range(ny + 1):
        for i in range(nx + 1):
            x = X0 + (X1 - X0) * i / nx
            y = Y0 + (Y1 - Y0) * j / ny
            V.append((x, y, WATER))
            A.append(foam_at(x, y))
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            F.append((a, a + 1, a + nx + 2, a + nx + 1))
    w.attrs['foam'] = []
    w.mesh(V, F, 'Water River Y', None, True)
    w.attrs['foam'][:] = A
    # close the body (sides + bottom) so the absorption volume is well defined
    bot = BED - 0.6
    for (xa, ya), (xb, yb) in (((X0, Y0), (X1, Y0)), ((X1, Y0), (X1, Y1)), ((X1, Y1), (X0, Y1)), ((X0, Y1), (X0, Y0))):
        w.quad((xa, ya, bot), (xb, yb, bot), (xb, yb, WATER), (xa, ya, WATER), 'Water River Y')
    w.quad((X0, Y0, bot), (X0, Y1, bot), (X1, Y1, bot), (X1, Y0, bot), 'Water River Y')
    for k in ('foam',):
        lst = w.attrs[k]
        lst.extend([0.0] * (len(w.V) - len(lst)))
    w.finish(SET)
    return rocks


# ==============================================================================================
KB = kit.Kit('%s Bridge' % CODE, 3)
bridge(KB)
KB.finish(SET, NIGHT, NIGHT)
print('bridge %.1fs' % (time.time() - T0))
terrain()
rocks = river()
print('terrain/river %.1fs' % (time.time() - T0))

# rocks, reeds, grass, trees, path
KN = kit.Kit('%s Nature' % CODE, 11)
for x, y, r in rocks:
    kit.rock(KN, x, y, WATER - 0.35, r * 1.25, 'Rock', 0.75)
for x, y, r in ((-12.5, -6.0, 0.8), (-13.2, 9.0, 1.1), (12.8, -18.0, 0.9), (-11.8, -30.0, 1.2), (13.5, 30.0, 0.8),
                (-15.0, -12.0, 0.6), (-16.5, 2.0, 0.9), (15.4, -6.0, 0.5)):
    kit.rock(KN, x, y, ground_z(x, y) - r * 0.25, r, 'Rock', 0.65)
for i in range(70):
    side = -1 if i % 3 else 1
    y = rng.uniform(-60, 90)
    if abs(y) < HW + 2.5:
        continue
    x = side * rng.uniform(RW - 0.4, RW + 1.4)
    kit.reeds(KN, x, y, ground_z(x, y) - 0.05, rng.randint(18, 36), rng.uniform(0.35, 0.7), rng.uniform(1.1, 1.8))
for i in range(260):
    x = rng.choice([-1, -1, 1]) * rng.uniform(RW + 1.0, 45)
    y = rng.uniform(-60, 90)
    if abs(y) < HW + 1.5 and abs(x) < L2 + 1:
        continue
    if x > 22 and abs(y) < 60:
        continue
    kit.reeds(KN, x, y, ground_z(x, y) - 0.03, rng.randint(10, 22), rng.uniform(0.15, 0.35), rng.uniform(0.25, 0.55), 'Grass Blade')
# foreground dressing for the WIDE camera (west bank, downstream)
for i in range(26):
    x = rng.uniform(-12.6, -9.6)
    y = rng.uniform(-17.0, -7.0)
    kit.reeds(KN, x, y, ground_z(x, y) - 0.05, rng.randint(22, 40), rng.uniform(0.3, 0.6), rng.uniform(1.0, 1.9))
for i in range(60):
    x = rng.uniform(-16.5, -11.0)
    y = rng.uniform(-18.5, -6.0)
    kit.reeds(KN, x, y, ground_z(x, y) - 0.03, rng.randint(12, 26), rng.uniform(0.15, 0.4), rng.uniform(0.25, 0.6), 'Grass Blade')
for x, y, r in ((-11.4, -12.5, 0.55), (-12.8, -15.8, 0.4), (-10.6, -9.6, 0.35)):
    kit.rock(KN, x, y, ground_z(x, y) - r * 0.3, r, 'Rock', 0.6)
for (x, y, h, kind) in ((-19.0, -9.0, 9.5, 'oak'), (-15.5, 14.0, 8.0, 'willow'), (-27.0, 6.0, 10.5, 'oak'),
                        (-18.5, -27.0, 7.5, 'willow'), (-34.0, -18.0, 9.0, 'oak'), (16.0, 40.0, 8.0, 'willow'),
                        # upstream banks (so the river does not read as a canal from the bridge)
                        (-15.0, 26.0, 8.5, 'willow'), (-19.5, 36.0, 10.5, 'oak'), (-14.8, 47.0, 7.5, 'willow'),
                        (-22.0, 58.0, 11.0, 'oak'), (-16.0, 70.0, 9.0, 'oak'), (15.2, 31.0, 7.0, 'willow'),
                        (18.5, 52.0, 10.0, 'oak'), (15.0, 64.0, 8.0, 'willow'), (-26.0, 84.0, 12.0, 'oak'),
                        (20.0, 80.0, 11.0, 'oak'), (-15.5, -44.0, 8.0, 'willow'), (16.0, -52.0, 9.5, 'oak')):
    kit.tree(KN, x, y, ground_z(x, y) - 0.1, h, kind, seed=int(x * 10 + y))
KN.finish(SET, NIGHT, NIGHT)
# dirt road on the west bank
road = geo.Builder('%s Road' % CODE)
road.grid(30, 3, lambda s, t: (-L2 - 60 * s, -2.2 + 4.4 * t + 2.5 * math.sin(s * 3.0) * s, ground_z(-L2 - 60 * s, 0) + 0.04),
          'Dirt', (60, 4.4), smooth=True)
road.grid(14, 4, lambda s, t: (L2 + 24 * s, -2.1 - 3.0 * min(1, max(0, 1 - abs(s - 0.25) * 4)) + (4.2 + 6.0 * min(1, max(0, 1 - abs(s - 0.25) * 4))) * t,
          ground_z(L2 + 24 * s, 0) + 0.05), 'Cobbles Dry', (24, 4.2), smooth=False)
road.finish(SET)
print('nature %.1fs' % (time.time() - T0))

# ==============================================================================================
# Town edge on the east bank: Cinderpass gatehouse (re-skinned), town wall, houses, mill with wheel
# ==============================================================================================
KG = kit.Kit('%s Gatehouse Cinderpass' % CODE, 13)
setbase.old_model(KG, 'towers-of-the-marches/v001/models/Cinderpass.blend',
                  {'Emberstone': 'Ashlar Grey', 'Ironstone': 'Rubble', 'Oxblood': 'Cloth Red'})
XG = L2 + 9.0
KG.finish(SET, NIGHT, NIGHT, loc=(XG, 0.0, 0.0), rz=-PI / 2)
KW = kit.Kit('%s Town Wall' % CODE, 14)
for sy in (-1, 1):
    y0, y1 = sy * 8.6, sy * 60.0
    yl, yh = min(y0, y1), max(y0, y1)
    KW.b.box(XG - 1.4, yl, -1.0, XG + 0.2, yh, 6.0, 'Ashlar Grey', 0.04)
    n = int((yh - yl) / 1.2)
    for k in range(n):
        if k % 2 == 0:
            yy = yl + k * 1.2
            KW.b.box(XG - 1.5, yy, 6.0, XG + 0.3, yy + 1.2, 7.1, 'Ashlar Grey', 0.03)
    KW.b.box(XG - 1.55, yl, 5.85, XG + 0.35, yh, 6.05, 'Limestone', 0.02)
    for ty in (sy * 28.0, sy * 52.0):
        KW.b.lathe([(3.2, -1.0), (3.0, 8.4), (3.4, 8.6), (3.4, 9.6)], 'Ashlar Grey', 20, (XG - 0.6, ty, 0), cap_top=True)
        KW.b.lathe([(3.6, 9.6), (0.05, 14.5)], 'Roof Slate', 20, (XG - 0.6, ty, 0), cap_top=False)
KW.finish(SET, NIGHT, NIGHT)
for i in range(10):
    r = random.Random(900 + i)
    W = r.uniform(4.2, 6.5)
    P = dict(W=W, D=r.uniform(7, 9), floors=r.choice([[3.2, 2.8, 2.6], [3.3, 2.8], [3.1, 2.7, 2.6, 2.5]]),
             jetty=r.choice([0.3, 0.45]), ground=r.choice(['stone', 'timber']), stone='Rubble',
             plaster=['Plaster Cream', 'Plaster Ochre', 'Plaster Rose', 'Plaster White', 'Plaster Blue'][i % 5],
             timber='Timber Dark', style=r.choice(['panels', 'braced', 'studs']), roof=r.choice(['gable', 'eaves']),
             roof_mat=['Roof Clay', 'Roof Slate', 'Roof Clay Old'][i % 3], win=[[], [-W * 0.25, W * 0.25], [-W * 0.25, W * 0.25], [0.0]],
             door_x=-W * 0.25, shutters=['Paint Green', 'Paint Red', 'Paint Blue'][i % 3], lit=0.6, flowers=True)
    K = kit.Kit('%s Town House %d' % (CODE, i + 1), 400 + i)
    kit.townhouse(K, P)
    yy = -34 + i * 7.2 + r.uniform(-1, 1)
    if abs(yy) < 9:
        yy += 18 * (1 if yy >= 0 else -1)
    hx = XG + 4.5 + r.uniform(0, 6)
    K.finish(SET, NIGHT, NIGHT, loc=(hx, yy, ground_z(hx, yy) - 0.15), rz=-PI / 2 + r.uniform(-0.15, 0.15))
# mill on the east bank, upstream, wheel in the river
KM = kit.Kit('%s Mill' % CODE, 15)
with KM.push((RW + 4.6, 20.0, 0.0), -PI / 2):
    kit.townhouse(KM, dict(W=7.0, D=6.0, floors=[3.4, 2.8], jetty=0.3, ground='stone', stone='Rubble', plaster='Plaster White',
                           timber='Timber Dark', style='braced', roof='gable', roof_mat='Roof Clay Old', win=[[], [-2.0, 2.0]],
                           gwin=[2.0], door_x=-1.5, shutters='Paint Green', lit=0.7, sides='left'))
# foundation wall from the river bed up to the bank under the mill's river side
KM.b.box(RW - 0.6, 15.5, BED - 0.4, RW + 4.6, 24.5, 0.05, 'Rubble', 0.03)
kit.waterwheel(KM, RW - 1.4, 20.0, WATER + 1.6, 2.1, 1.1)
KM.b.box(RW - 2.3, 19.8, WATER + 1.5, RW - 0.6, 20.2, WATER + 1.7, 'Timber Dark', 0.02)
# wheel bearing posts
for yy in (19.2, 20.8):
    KM.b.beam((RW - 0.75, yy, BED), (RW - 0.75, yy, WATER + 1.9), 0.2, 0.2, 'Timber Dark', 0.02)
kit.barrel(KM, RW + 5.0, 14.5, 0.0)
kit.barrel(KM, RW + 5.6, 14.9, 0.0, 0.28, 0.8)
kit.crate(KM, RW + 6.0, 14.1, 0.0)
kit.hay_bale(KM, RW + 4.6, 13.6, 0.0, 0.2)
KM.finish(SET, NIGHT, NIGHT)
print('town edge %.1fs' % (time.time() - T0))

# ==============================================================================================
# Marks and cameras
# ==============================================================================================
MK = C['marks']
mk = {}


def mark(name, p, facing):
    mk[name] = look.mark(MK, '%s_%s' % (CODE, name), V(*p), facing)


HERO = (-2.6, -0.4, deck_z(-2.6))
RIVAL = (0.7, 0.4, deck_z(0.7))
mark('MARK_HERO', HERO, look.face_towards(HERO, (-4.6, -2.8)))
mark('MARK_RIVAL', RIVAL, look.face_towards(RIVAL, HERO) + 35)
mark('MARK_SIBLING', (-4.3, 0.8, deck_z(-4.3)), look.face_towards((-4.3, 0.8), RIVAL))
mark('MARK_RULER', (XG - 1.4, 0.0, 8.72), -90.0)
crowd = [(23.6, -4.2), (24.8, -2.6), (22.6, 3.4), (24.4, 4.4), (-23.5, -3.0), (-24.2, 2.2), (-22.8, 3.8), (-25.0, -1.0)]
for i, (x, y) in enumerate(crowd):
    mark('MARK_CROWD_%d' % (i + 1), (x, y, ground_z(x, y) if abs(x) > L2 else deck_z(x)), look.face_towards((x, y), (0, 0)))
mark('MARK_GIANT', (0.0, -13.0, BED + 0.4), 180.0)
mark('MARK_BOAT', (-5.5, -20.0, WATER), 0.0)

CM = C['cams']
cams = {}


def cam(name, pos, tgt, lens, note):
    cams[name] = look.camera(CM, '%s_%s' % (CODE, name), V(*pos), V(*tgt), lens, note)


cam('WIDE_ESTABLISH', (-15.5, -18.5, 1.1), (3.0, 1.5, 2.4), 20, 'downstream west bank: river towards camera, three-arch bridge, gatehouse and town on the right')
cam('LOW_HERO', (-4.1, -1.55, deck_z(-4.1) + 0.3), (-2.6, -0.4, deck_z(-2.6) + 1.4), 20, 'low on the deck looking up at MARK_HERO; sky, parapet and gatehouse behind')
cam('CROWD_MED', (11.5, -1.5, deck_z(11.5) + 1.7), (24.0, 0.5, 2.2), 26, 'from the bridge towards the gate and the east-bank crowd')
cam('TWO_SHOT', (1.0, -9.0, deck_z(1.0) + 4.6), (-1.0, 0.0, deck_z(-1.0) + 0.8), 35, 'raised two-shot from over the downstream water: hero (left) and rival (right) facing off on the bridge, river and upstream bank behind')
cam('CLOSE_A', (-3.6, -1.95, deck_z(-3.6) + 1.12), HERO[:2] + (HERO[2] + 1.1,), 50, 'hero face')
cam('CLOSE_B', (-0.9, -1.5, deck_z(-0.9) + 1.72), RIVAL[:2] + (RIVAL[2] + 1.72,), 50, 'rival face')
cam('INSERT_WATER', (-2.4, -8.5, WATER + 0.8), (-4.25, -3.9, WATER + 0.2), 35, 'foam at the cutwater, flowing water, wet stone')
cam('INSERT_MILL', (6.0, 10.0, WATER + 1.4), (RW - 1.4, 20.0, WATER + 1.4), 35, 'mill wheel in the river')
cam('UNDER_ARCH', (2.0, -12.0, WATER + 0.9), (0.0, 0.0, SPRING + 2.5), 22, 'low over the water looking through the central arch')

# ==============================================================================================
# Lights
# ==============================================================================================
worlds = {}
sun_day = look.sun_obj(C['DAY'], 'DAY', -40.0, '%s Sun DAY' % CODE)
worlds['DAY'] = look.world_sky(sc, 'DAY', '%s Sky DAY' % CODE, look.sun_direction(sun_day))
sun_g = look.sun_obj(C['GOLDEN'], 'GOLDEN', -75.0, '%s Sun GOLDEN' % CODE)
worlds['GOLDEN'] = look.world_sky(sc, 'GOLDEN', '%s Sky GOLDEN' % CODE, look.sun_direction(sun_g))
moon = look.sun_obj(C['NIGHT'], 'NIGHT', -40.0, '%s Moon' % CODE, 0.85, 30.0)
worlds['NIGHT'] = look.world_sky(sc, 'NIGHT', '%s Sky NIGHT' % CODE, look.sun_direction(moon))
look.point(C['NIGHT'], '%s gate torch L' % CODE, V(XG - 3.6, -3.6, 3.2), 300, '#ff8a35', 0.25)
look.point(C['NIGHT'], '%s gate torch R' % CODE, V(XG - 3.6, 3.6, 3.2), 300, '#ff8a35', 0.25)
for y in (-3.2, 3.2):
    KF = kit.Kit('%s Torch %s' % (CODE, 'L' if y < 0 else 'R'), 31)
    ty_ = -3.6 if y < 0 else 3.6
    KF.b.cyl((XG - 3.6, ty_, 0.0), (XG - 3.6, ty_, 2.9), 0.05, 'Timber Dark', 6)
    KF.b.lathe([(0.03, 2.85), (0.12, 3.0), (0.13, 3.05)], 'Iron Black', 8, (XG - 3.6, ty_, 0))
    kit.flame(KF.n, (XG - 3.6, ty_, 2.98), 0.42, 0.11, 'Flame', 10)
    KF.finish(SET, NIGHT, NIGHT)
look.area(C['NIGHT'], '%s moon fill' % CODE, V(-30, -60, 30), (math.radians(60), 0, math.radians(-30)), 40, 45, '#8aa4ff')
for o in C['NIGHT'].all_objects:
    if o.type == 'LIGHT' and o.data.type == 'POINT' and 'lamp' in o.name:
        o.data.energy *= 2.4
for i, (x, y) in enumerate(((-L2 - 2.0, -HW - 0.9), (-L2 - 2.0, HW + 0.9))):
    KT = kit.Kit('%s Bank Torch %d' % (CODE, i + 1), 40 + i)
    gz_ = ground_z(x, y)
    KT.b.cyl((x, y, gz_ - 0.3), (x, y, gz_ + 2.2), 0.05, 'Timber Dark', 6)
    KT.b.lathe([(0.03, gz_ + 2.15), (0.13, gz_ + 2.32), (0.14, gz_ + 2.37)], 'Iron Black', 8, (x, y, 0))
    kit.flame(KT.n, (x, y, gz_ + 2.3), 0.45, 0.12, 'Flame', 10)
    KT.finish(SET, NIGHT, NIGHT)
    look.point(C['NIGHT'], '%s bank torch %d' % (CODE, i + 1), V(x, y, gz_ + 2.65), 320, '#ff8a35', 0.25)

setbase.finish(sc, master, C, TITLE, CODE, cams['WIDE_ESTABLISH'], worlds,
               os.path.join(setbase.OUT, 'bridge_river', 'bridge_river.blend'),
               exposure={'DAY': look.EXPOSURE['DAY'], 'GOLDEN': look.EXPOSURE['GOLDEN'], 'NIGHT': 1.0})
print('saved %.1fs' % (time.time() - T0))
