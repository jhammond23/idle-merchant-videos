"""Backlot set 5: FOREST EDGE.  python3 -I build_forest_edge.py  ->  forest_edge/forest_edge.blend
The last houses of the town (cobbles, lamp posts) open onto a dirt road that runs north between split-rail
pasture fences, past a signpost ('FOREST' / 'TOWN'), into a wall of big dark oaks.  Mushrooms, rocks, bushes,
a fallen log, hay in the pasture; fireflies + lamps + lit windows at night.
Road centre x = ROAD(y); ground rises gently towards the forest (z = GZ(x, y))."""
import sys, os, math, time, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, '..', 'materials')]
import bpy
from mathutils import Vector
import mats, geo, look, kit, kit2, setbase, art2

T0 = time.time()
M = geo.M
PI = math.pi
CODE, TITLE = 'FE', 'Forest Edge'
sc, master, C = setbase.start(CODE, TITLE)
SET, NIGHT = C['set'], C['NIGHT']
mats.set_global(wet=0.15)
rng = random.Random(5)
RW = 2.3              # half road width
FENCE = 3.7           # fence offset from the road centre
FOREST_Y = 17.0       # the tree line starts here


def ROAD(y):
    return 2.2 * math.sin((y - 4.0) / 16.0) if y > -6 else 2.2 * math.sin(-10.0 / 16.0)


def GZ(x, y):
    """Ground height: flat in town, rising ~1.6 m into the forest, soft undulation away from the road."""
    rise = 0.0 if y < -2 else min(1.0, (y + 2) / 50.0) ** 1.3 * 1.6
    away = min(1.0, max(0.0, (abs(x - ROAD(y)) - RW - 0.6) / 6.0))
    und = 0.35 * math.sin(x / 6.3 + 1.1) * math.sin(y / 7.7) * away + 0.25 * away * max(0.0, min(1.0, (y + 4) / 8))
    return (rise + und) if y > -6.5 else 0.0


def V(x, y, z=0.0):
    return Vector((x * M, y * M, z * M))


# ==============================================================================================
# Town edge: two houses each side of the street, cobbles, lamp posts
# ==============================================================================================
PLASTERS = ['Plaster Cream', 'Plaster Ochre', 'Plaster Rose', 'Plaster White', 'Plaster Sage', 'Plaster Blue']
PAINTS = ['Paint Green', 'Paint Red', 'Paint Blue', 'Paint Yellow']


def house_params(W, i, **over):
    r = random.Random(2000 + i)
    floors = r.choice([[3.2, 2.8, 2.6], [3.3, 2.8], [3.1, 2.7, 2.6]])
    xs = [(-W / 2 + (k + 0.5) * W / 2) for k in range(2)] if W < 4.6 else [(-W / 2 + (k + 0.5) * W / 3) for k in range(3)]
    p = dict(W=W, D=r.uniform(7.0, 8.5), floors=floors, jetty=r.choice([0.3, 0.4]), ground=r.choice(['stone', 'timber']),
             stone='Rubble', plaster=PLASTERS[i % 6], timber=r.choice(['Timber Dark', 'Timber Oak']),
             style=r.choice(['panels', 'braced', 'studs']), roof=r.choice(['gable', 'eaves']),
             roof_mat=['Roof Clay', 'Roof Clay Old', 'Roof Slate', 'Roof Shingle'][i % 4], pitch=r.uniform(48, 56),
             win=[[]] + [xs for _ in floors[1:]], door_x=-W / 2 + 0.9, door_paint=PAINTS[(i + 1) % 4], shutters=PAINTS[i % 4],
             gwin=[xs[-1]], win_w=0.78, sides=None, lit=0.6, flowers=True)
    p['dormer'] = p['roof'] == 'eaves'
    p['chimney_x'] = r.uniform(-W * 0.25, W * 0.25)
    p.update(over)
    return p


TOWN = [  # (front x, y of the house centre, facing, W, extras)
    (-5.6, -9.0, 'E', 4.6, dict(lantern_x=-1.2, sides='right')),
    (-5.6, -14.0, 'E', 5.0, dict(sign='mug')),
    (-5.6, -19.2, 'E', 5.2, dict()),
    (5.6, -8.8, 'W', 4.8, dict(lantern_x=1.0, sides='left')),
    (5.6, -14.0, 'W', 5.0, dict(sign='loaf', ground='stone')),
    (5.6, -19.0, 'W', 4.6, dict()),
]
for i, (fx, cy, face, W, ex) in enumerate(TOWN):
    P = house_params(W, i, **ex)
    K = kit.Kit('%s House %d' % (CODE, i + 1), 400 + i)
    kit.townhouse(K, P)
    rz = PI / 2 if face == 'E' else -PI / 2       # E: front faces +X;  W: front faces -X
    K.finish(SET, NIGHT, NIGHT, loc=(fx, cy, 0.0), rz=rz)
KL = kit.Kit('%s Lamps' % CODE, 21)
for x, y in ((-3.3, -6.2), (3.4, -6.6), (-3.4, -16.5)):
    kit.lamp_post(KL, x, y, 3.3)
KL.finish(SET, NIGHT, NIGHT)
print('town %.1fs' % (time.time() - T0))

# ==============================================================================================
# Ground: terrain (grass / leaf litter under the trees), cobbled street, dirt road
# ==============================================================================================
X0, X1, Y0, Y1, STEP = -60.0, 60.0, -6.4, 95.0, 1.0
nu, nv = int((X1 - X0) / STEP), int((Y1 - Y0) / STEP)
tv, tf, tm = [], [], []
for j in range(nv + 1):
    for i in range(nu + 1):
        x, y = X0 + i * STEP, Y0 + j * STEP
        tv.append((x, y, GZ(x, y) - 0.02))
for j in range(nv):
    for i in range(nu):
        a = j * (nu + 1) + i
        x, y = X0 + (i + 0.5) * STEP, Y0 + (j + 0.5) * STEP
        edge = FOREST_Y - 2.5 + 3.0 * math.sin(x / 5.3) + 1.8 * math.sin(x / 2.1 + 1.3) + rng.uniform(-0.8, 0.8)
        near_road = abs(x - ROAD(y)) < RW + 0.3
        tf.append((a, a + 1, a + nu + 2, a + nu + 1))
        tm.append('Forest Floor' if (y > edge and not near_road) else 'Grass')
terr = geo.Builder('%s Terrain' % CODE)
terr.mesh(tv, tf, tm, None, smooth=True)
terr.finish(SET, dicing=1.5)
# cobbled street in town (flat)
st = geo.Builder('%s Cobbles' % CODE)
st.grid(10, 20, lambda s, t: (-5.7 + 11.4 * s, -24.0 + 18.0 * t, 0.0), 'Cobbles Dry', (11.4, 18.0), smooth=False)
st.finish(SET, dicing=1.0)
# dirt road: follows ROAD(y), a hair above the terrain, cambered
road = geo.Builder('%s Road' % CODE)
NY = 120


def road_pt(s, t):
    y = -6.6 + t * 100.0
    xc = ROAD(y)
    x = xc + (2 * s - 1) * (RW + 0.35)
    z = GZ(xc, y) + 0.03 + 0.05 * (1 - (2 * s - 1) ** 2)
    return (x, y, z)


road.grid(4, NY, road_pt, 'Dirt', (2 * RW + 0.7, 100.0), smooth=True)
road.finish(SET, dicing=1.5)
# distant hills behind the forest + far fields to the sides
hill = geo.Builder('%s Hills' % CODE)


def hill_fn(s, t):
    x = -320 + 640 * s
    y = 60 + 320 * t
    h = 0.4 * (30 * math.exp(-((x + 40) / 90) ** 2 - ((y - 230) / 70) ** 2) + 22 * math.exp(-((x - 110) / 70) ** 2 - ((y - 200) / 60) ** 2))
    h += 6 * math.sin(x / 41) * math.sin(y / 33) + 10 * t
    return (x, y, h + 1.0)


hill.grid(40, 24, hill_fn, 'Grass', (640, 320), smooth=True)
hill.grid(6, 6, lambda s, t: (-320 + 640 * s, -160 + 230 * t, -0.08), 'Grass', (640, 230), smooth=False)
hill.finish(SET)
print('ground %.1fs' % (time.time() - T0))

# ==============================================================================================
# Fences, signpost, pasture props
# ==============================================================================================
KF = kit.Kit('%s Fences' % CODE, 31)
for side in (-1, 1):
    pts = [(ROAD(y) + side * FENCE, y) for y in [-4.0 + k * 2.2 for k in range(10)]]
    kit2.split_rail_fence(KF, pts, 1.15, 2.2, 'Planks Grey', 'Timber Oak', GZ, seed=3 + side)
SIGN = (ROAD(3.0) + RW + 0.75, 3.0)
kit2.signpost(KF, SIGN[0], SIGN[1], GZ(*SIGN), [(art2.path('FOREST'), 40.0, 0.0), (art2.path('TOWN'), -140.0, 0.42),
                                                (art2.path('CASTLE'), 165.0, 0.84)], 2.6)
for x, y, rz_ in ((ROAD(6.0) - 8.5, 6.0, 0.4), (ROAD(11.0) - 10.5, 11.5, 1.2), (ROAD(4.0) + 9.5, 4.5, -0.3)):
    kit.hay_bale(KF, x, y, GZ(x, y), rz_, (1.1, 0.55, 0.5))
kit.hay_pile(KF, ROAD(8.0) + 8.0, 8.5, GZ(ROAD(8.0) + 8.0, 8.5), 1.0, 0.7)
kit.cart(KF, ROAD(1.0) - 7.2, 1.0, 1.9, 'hay')
KF.finish(SET, NIGHT, NIGHT)

# ==============================================================================================
# The forest: big dark oaks (leaf cards), a dark mass of bushes behind, undergrowth
# ==============================================================================================
# Instanced: 6 oak prototypes (leaf cards) placed ~60 times, 4 canopy-mass and 3 undergrowth bush prototypes
# placed ~200 times.  Cycles shares instanced geometry, so the forest costs about as much memory as 10 trees.
TREE_PROTOS = []
for k in range(6):
    hh = 21.0 + k * 0.7
    TREE_PROTOS.append(kit2.build_proto('%s Oak %d' % (CODE, k + 1),
                                        lambda K, hh=hh, k=k: kit.tree(K, 0.0, 0.0, 0.0, hh, 'oak', 700 + k, 7500, leafmat='Leaf Forest'),
                                        SET, NIGHT, NIGHT, 700 + k))
MASS_PROTOS = [kit2.build_proto('%s Canopy Mass %d' % (CODE, k + 1),
                                lambda K, k=k: kit2.bush(K, 0.0, 0.0, 0.0, 6.0, 'Leaf Forest', 1100, seed=1300 + k), SET, NIGHT, NIGHT, 1300 + k)
               for k in range(4)]
BUSH_PROTOS = [kit2.build_proto('%s Bush %d' % (CODE, k + 1),
                                lambda K, k=k: kit2.bush(K, 0.0, 0.0, 0.0, 1.0, 'Leaf Forest', 300, seed=1400 + k), SET, NIGHT, NIGHT, 1400 + k)
               for k in range(3)]
used = {id(p): False for p in TREE_PROTOS + MASS_PROTOS + BUSH_PROTOS}


def put(protos, name, x, y, z, rz, s):
    p = protos[rng.randrange(len(protos))]
    first = not used[id(p)]
    used[id(p)] = True
    return kit2.place(p, SET, name, (x, y, z), rz, s, first)


trees = []
cand = []
for i in range(2500):
    x = rng.uniform(-52, 52)
    y = rng.uniform(FOREST_Y - 1.0, 80.0)
    if abs(x - ROAD(y)) < RW + 2.0:
        continue
    cand.append((x, y))
cand.sort(key=lambda p: p[1] + rng.uniform(0, 12))       # fill the edge rows first
for x, y in cand:
    d_min = 4.6 + 0.05 * max(0.0, y - FOREST_Y)
    if all((x - a) ** 2 + (y - b_) ** 2 > d_min ** 2 for a, b_, _ in trees):
        trees.append((x, y, rng.uniform(0.74, 1.0)))
    if len(trees) >= 64:
        break
for i, (x, y, sc_) in enumerate(trees):
    put(TREE_PROTOS, '%s Oak %02d' % (CODE, i + 1), x, y, GZ(x, y) - 0.1, rng.uniform(0, 2 * PI), sc_)
# canopy masses deeper in (eye level up to the crowns) so no sky / hill shows between the trunks
nm = 0
for i in range(400):
    x = rng.uniform(-58, 58)
    y = rng.uniform(32, 88)
    if abs(x - ROAD(y)) < RW + 2.8 + 0.05 * (y - 32):
        continue
    put(MASS_PROTOS, '%s Canopy %03d' % (CODE, nm + 1), x, y, GZ(x, y) + rng.uniform(-1.0, 7.0), rng.uniform(0, 2 * PI), rng.uniform(0.6, 1.25))
    nm += 1
    if nm >= 130:
        break
# undergrowth: along the forest edge, between the trunks, at the road sides
nb_ = 0
for i in range(600):
    y = rng.uniform(FOREST_Y - 3.0, 60.0)
    x = rng.uniform(-48, 48)
    d = abs(x - ROAD(y))
    if d < RW + 0.9 or (d < FENCE + 0.6 and y < FOREST_Y - 1):
        continue
    put(BUSH_PROTOS, '%s Bush %03d' % (CODE, nb_ + 1), x, y, GZ(x, y) - 0.1, rng.uniform(0, 2 * PI), rng.uniform(0.6, 2.4))
    nb_ += 1
    if nb_ >= 150:
        break
KT = kit.Kit('%s Forest Trunks' % CODE, 41)
for i in range(30):
    x = rng.uniform(-48, 48)
    y = rng.uniform(30, 76)
    if abs(x - ROAD(y)) < RW + 0.5:
        continue
    KT.b.cyl((x, y, GZ(x, y) - 0.2), (x + rng.uniform(-0.4, 0.4), y, GZ(x, y) + rng.uniform(7, 12)), rng.uniform(0.3, 0.5), 'Bark', 8, 0.2)
# two pasture oaks (normal leaves)
for i, (x, y, h) in enumerate(((ROAD(6) - 15.0, 7.0, 11.0), (ROAD(10) + 17.0, 12.0, 12.5))):
    kit.tree(KT, x, y, GZ(x, y) - 0.1, h, 'oak', 760 + i, 4200)
KT.finish(SET, NIGHT, NIGHT)
KU = kit.Kit('%s Undergrowth' % CODE, 51)
for i in range(16):
    y = rng.uniform(FOREST_Y - 2.0, 30.0)
    side = rng.choice((-1, 1))
    x = ROAD(y) + side * (RW + rng.uniform(0.4, 1.6))
    for k in range(rng.randint(1, 3)):
        mx, my = x + rng.uniform(-0.3, 0.3), y + rng.uniform(-0.3, 0.3)
        kit2.mushroom(KU, mx, my, GZ(mx, my), rng.uniform(1.0, 2.2))
for i in range(14):
    x = rng.uniform(-30, 30)
    y = rng.uniform(-2, 40)
    if abs(x - ROAD(y)) < RW + 0.5:
        continue
    kit.rock(KU, x, y, GZ(x, y), rng.uniform(0.3, 0.8), 'Rock', 0.6, 1000 + i)
# fallen log + stump at the forest edge (left of the road)
lx, ly = ROAD(19.0) - RW - 2.0, 19.0
KU.b.cyl((lx - 3.6, ly - 0.8, GZ(lx, ly) + 0.3), (lx, ly + 0.4, GZ(lx, ly) + 0.35), 0.38, 'Bark', 14, 0.32)
sx_, sy_ = ROAD(15.5) + RW + 1.6, 15.5
KU.b.lathe([(0.55, -0.1), (0.42, 0.1), (0.38, 0.55), (0.0, 0.58)], 'Bark', 14, (sx_, sy_, GZ(sx_, sy_)), cap_top=True)
# grass tufts along the fences and road verges
for i in range(40):
    y = rng.uniform(-4.0, FOREST_Y)
    side = rng.choice((-1, 1))
    x = ROAD(y) + side * rng.uniform(RW + 0.5, FENCE + 0.3)
    kit.reeds(KU, x, y, GZ(x, y), 10, 0.25, rng.uniform(0.35, 0.6), 'Grass Blade')
KU.finish(SET, NIGHT, NIGHT)
# fireflies (night only): tiny warm-green glows at the forest edge
KN = kit.Kit('%s Fireflies' % CODE, 61)
for i in range(70):
    y = rng.uniform(FOREST_Y - 4.0, FOREST_Y + 12.0)
    x = ROAD(y) + rng.uniform(-12, 12)
    KN.n.sphere((x, y, GZ(x, y) + rng.uniform(0.4, 2.6)), rng.uniform(0.025, 0.04), 'Glow Firefly', 6, 4)
KN.finish(SET, NIGHT, NIGHT)
print('forest %.1fs (%d trees, %d canopy masses, %d bushes)' % (time.time() - T0, len(trees), nm, nb_))

# ==============================================================================================
# Marks
# ==============================================================================================
MK = C['marks']
HERO = Vector((ROAD(7.0) - 0.6, 7.0, 0))
RIVAL = Vector((ROAD(9.0) + 1.4, 9.0, 0))


def gp(x, y):
    return (x, y, GZ(x, y) + 0.03 + 0.05 * (1 - ((x - ROAD(y)) / (RW + 0.35)) ** 2) if abs(x - ROAD(y)) < RW + 0.35 else GZ(x, y))


mk = {}


def mark(name, p, facing):
    mk[name] = look.mark(MK, '%s_%s' % (CODE, name), V(*gp(p[0], p[1])) if len(p) == 2 else V(*p), facing)


mark('MARK_HERO', (HERO.x, HERO.y), look.face_towards(HERO, RIVAL) - 70)
mark('MARK_RIVAL', (RIVAL.x, RIVAL.y), look.face_towards(RIVAL, HERO) + 55)
mark('MARK_SIBLING', (HERO.x - 1.1, HERO.y - 1.0), look.face_towards((HERO.x - 1.1, HERO.y - 1.0), RIVAL) - 30)
mark('MARK_RULER', (ROAD(1.5) - RW - 0.6, 1.5), look.face_towards((ROAD(1.5) - RW - 0.6, 1.5), HERO))
cc = Vector(((HERO.x + RIVAL.x) / 2, (HERO.y + RIVAL.y) / 2, 0))
for i, (dx, y) in enumerate(((-2.9, 4.6), (2.8, 5.2), (-3.1, 8.4), (3.1, 7.4), (-2.4, 11.2), (3.6, 14.2), (-1.8, 13.4), (0.9, 15.0))):
    p = (ROAD(y) + dx, y)
    mark('MARK_CROWD_%d' % (i + 1), p, look.face_towards(p, cc))
mark('MARK_GIANT', (ROAD(30.0) - 13.0, 30.0), look.face_towards((ROAD(30.0) - 13.0, 30.0), HERO))
mark('MARK_GUARD_1', (-3.2, -5.4), 180.0 + 0.0)
mark('MARK_GUARD_2', (3.3, -5.8), 180.0 + 0.0)
mark('MARK_FOREST', (ROAD(24.0), 24.0), 180.0)       # where a character walks into the trees

# ==============================================================================================
# Cameras
# ==============================================================================================
CM = C['cams']
cams = {}


def cam(name, pos, tgt, lens, note):
    cams[name] = look.camera(CM, '%s_%s' % (CODE, name), V(*pos), V(*tgt), lens, note)


hz = GZ(HERO.x, HERO.y) + 0.06
cam('WIDE_ESTABLISH', (0.8, -11.5, 3.4), (ROAD(26.0) - 0.5, 26.0, 5.6), 18, 'from the last houses up the dirt road: fences, signpost, the dark forest wall; room for a crowd on the road')
cam('LOW_HERO', (HERO.x + 0.9, HERO.y - 2.7, hz + 0.3), (HERO.x - 0.15, HERO.y + 0.4, hz + 1.5), 20, 'knee-height up at MARK_HERO; the road disappearing into the big dark trees behind')
cam('CROWD_MED', (ROAD(0.0) + 3.0, -2.4, GZ(0, -2.4) + 2.0), (cc.x, cc.y + 1.0, GZ(cc.x, cc.y) + 1.3), 35, 'crowd on the road around hero + rival, forest behind')
cam('TWO_SHOT', (HERO.x + 0.7, HERO.y - 4.4, hz + 1.2), (cc.x, cc.y, hz + 1.1), 35, 'hero (left) and rival (right) facing off on the road, forest behind')
cam('CLOSE_A', (HERO.x + 1.25, HERO.y - 1.15, hz + 1.08), (HERO.x, HERO.y, hz + 1.06), 50, 'hero face (head ~1.0 m)')
rz_ = GZ(RIVAL.x, RIVAL.y) + 0.06
cam('CLOSE_B', (RIVAL.x - 1.2, RIVAL.y - 1.45, rz_ + 1.66), (RIVAL.x, RIVAL.y, rz_ + 1.68), 50, 'rival face (Rich kid head ~1.6 m)')
sz = GZ(*SIGN)
cam('INSERT_SIGNPOST', (SIGN[0] - 1.4, SIGN[1] - 3.2, sz + 1.9), (SIGN[0], SIGN[1], sz + 2.05), 35, "signpost boards 'FOREST' / 'TOWN' / 'CASTLE', fences and trees behind")
cam('INSERT_FOREST', (ROAD(16.0) + 0.6, 16.0, GZ(0, 16) + 1.0), (ROAD(32.0), 32.0, GZ(0, 32) + 1.6), 24, 'into the forest along the road: mushrooms, bushes, dark trunks')
cam('WIDE_REVERSE', (ROAD(22.0) - 0.8, 22.0, GZ(0, 22) + 2.6), (0.0, -14.0, 2.0), 20, 'from the tree line back down the road to the town')

# ==============================================================================================
# Lights
# ==============================================================================================
worlds = {}
sun_day = look.sun_obj(C['DAY'], 'DAY', 26.0, '%s Sun DAY' % CODE)
worlds['DAY'] = look.world_sky(sc, 'DAY', '%s Sky DAY' % CODE, look.sun_direction(sun_day))
sun_g = look.sun_obj(C['GOLDEN'], 'GOLDEN', -30.0, '%s Sun GOLDEN' % CODE, 4.6, 15.0)
worlds['GOLDEN'] = look.world_sky(sc, 'GOLDEN', '%s Sky GOLDEN' % CODE, look.sun_direction(sun_g))
moon = look.sun_obj(C['NIGHT'], 'NIGHT', -40.0, '%s Moon' % CODE)
worlds['NIGHT'] = look.world_sky(sc, 'NIGHT', '%s Sky NIGHT' % CODE, look.sun_direction(moon))
look.area(C['NIGHT'], '%s moon fill' % CODE, V(-10, -40, 28), (math.radians(55), 0, math.radians(-15)), 30, 70, '#7f9cff')

# DAY / GOLDEN only: light under the canopy so the big trees read dark-green, not black.  Bounce from the
# sunlit forest floor (big soft panel facing up), skylight spilling in from the open edge (panel at the tree
# line facing into the forest; characters on the road stand behind it, so it does not light them), and a few
# dappled sun pools on the road and floor under the trees.
FILL = {'DAY': dict(k=1.0, bounce='#e8e2b4', edge='#e4ecff', sun='#fff1dc'),
        'GOLDEN': dict(k=0.8, bounce='#ffd9a0', edge='#ffd2b0', sun='#ffb060')}
FILL_E = dict(bounce=0.55, edge=0.45, pool=1500.0)       # exitance (sun = 4.2) / spot watts


def canopy_fill(col, preset):
    f = FILL[preset]
    k = f['k']
    w, d = 70.0, 30.0
    look.area(col, '%s canopy bounce %s' % (CODE, preset), V(ROAD(31.0), 31.0, GZ(0, 31) + 0.6), (PI, 0, 0), w, FILL_E['bounce'] * k * w * d,
              f['bounce'], 'RECTANGLE', d)
    w, h = 84.0, 14.0
    look.area(col, '%s canopy edge fill %s' % (CODE, preset), V(0.0, FOREST_Y - 2.5, 7.5), (PI / 2, 0, 0), w, FILL_E['edge'] * k * w * h,
              f['edge'], 'RECTANGLE', h)
    prng = random.Random(77)
    for i, (dx, y) in enumerate(((0.4, 19.5), (-1.2, 24.0), (1.6, 28.5), (-0.6, 33.0), (-6.5, 21.0), (6.0, 23.5), (-8.0, 27.5), (7.5, 30.5))):
        x = ROAD(y) + dx
        z = GZ(x, y)
        look.spot(col, '%s dapple %s %d' % (CODE, preset, i + 1), V(x + prng.uniform(-1, 1), y - 1.5, z + 8.5), V(x, y, z),
                  FILL_E['pool'] * k * prng.uniform(0.7, 1.2), f['sun'], prng.uniform(16, 26), 0.75, 0.6)


canopy_fill(C['DAY'], 'DAY')
canopy_fill(C['GOLDEN'], 'GOLDEN')
look.point(C['NIGHT'], '%s firefly glow' % CODE, V(ROAD(18.0), 18.0, 2.0), 60, '#c8ff6a', 1.5)
look.point(C['NIGHT'], '%s sign lamp' % CODE, V(SIGN[0] - 0.3, SIGN[1] - 0.5, sz + 2.6), 90, '#ffa040', 0.15)

scenes = setbase.finish(sc, master, C, TITLE, CODE, cams['WIDE_ESTABLISH'], worlds,
                        os.path.join(setbase.OUT, 'forest_edge', 'forest_edge.blend'))
print('saved %.1fs' % (time.time() - T0))
