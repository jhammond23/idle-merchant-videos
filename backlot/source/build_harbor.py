"""Backlot set 6: HARBOR.  python3 -I build_harbor.py  ->  harbor/harbor.blend
A cobbled quay (top z = 0) with harbor houses facing the water, a stone quay wall down to the water
(z = WATER), two timber jetties on posts (main jetty with a T-head), three boats (red-sail boat, fishing boat,
rowing boat), crates, barrels, rope coils, bollards, nets, lamp posts, gulls, a fish stall, a breakwater with a
red-and-white lighthouse at the harbor mouth (lamp lit at night)."""
import sys, os, math, time, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, '..', 'materials')]
import bpy
from mathutils import Vector
import mats, geo, look, kit, kit2, setbase, art2

T0 = time.time()
M = geo.M
PI = math.pi
CODE, TITLE = 'HB', 'Harbor'
sc, master, C = setbase.start(CODE, TITLE)
SET, NIGHT = C['set'], C['NIGHT']
mats.set_global(wet=0.35)
rng = random.Random(6)
WATER, BED = -1.0, -3.6
QUAY_D = 10.0          # quay depth (y from -QUAY_D to 0); houses front at y = -QUAY_D


def V(x, y, z=0.0):
    return Vector((x * M, y * M, z * M))


# ==============================================================================================
# Harbor houses (front faces +Y, towards the water)
# ==============================================================================================
PLASTERS = ['Plaster White', 'Plaster Blue', 'Plaster Ochre', 'Plaster Cream', 'Plaster Rose', 'Plaster Sage']
PAINTS = ['Paint Blue', 'Paint Red', 'Paint Green', 'Paint Yellow']


def house_params(W, i, **over):
    r = random.Random(3000 + i)
    floors = r.choice([[3.2, 2.8, 2.6], [3.3, 2.8], [3.1, 2.7, 2.6]])
    xs = [(-W / 2 + (k + 0.5) * W / 2) for k in range(2)] if W < 4.6 else [(-W / 2 + (k + 0.5) * W / 3) for k in range(3)]
    p = dict(W=W, D=r.uniform(7.0, 8.5), floors=floors, jetty=r.choice([0.25, 0.35]), ground=r.choice(['stone', 'stone', 'shop']),
             stone=r.choice(['Rubble', 'Ashlar']), plaster=PLASTERS[i % 6], timber=r.choice(['Timber Dark', 'Timber Oak']),
             style=r.choice(['panels', 'braced', 'studs']), roof=r.choice(['gable', 'eaves']),
             roof_mat=['Roof Clay', 'Roof Slate', 'Roof Clay Old', 'Roof Clay'][i % 4], pitch=r.uniform(46, 54),
             win=[[]] + [xs for _ in floors[1:]], door_x=-W / 2 + 0.9, door_paint=PAINTS[(i + 1) % 4], shutters=PAINTS[i % 4],
             gwin=[xs[-1]], shop_x=W * 0.15, shop_w=min(2.0, W - 2.3), goods=r.choice(['bread', 'fruit', 'pots', 'cloth']),
             win_w=0.78, sides=None, lit=0.6, flowers=True)
    if p['ground'] == 'shop':
        p['gwin'] = []
    p['dormer'] = p['roof'] == 'eaves'
    p['chimney_x'] = r.uniform(-W * 0.25, W * 0.25)
    p.update(over)
    return p


widths = [5.0, 4.4, 5.4, 4.6, 5.2, 4.2, 5.0, 4.8, 5.6]
extras = {1: dict(sign='mug', lantern_x=1.2), 3: dict(sign='potion'), 4: dict(lantern_x=-1.4), 6: dict(sign='horseshoe'),
          2: dict(ground='shop', goods='fruit')}
x = 23.0
for i, W in enumerate(widths):
    x -= W
    cx = x + W / 2
    P = house_params(W, i, **extras.get(i, {}))
    K = kit.Kit('%s House %d' % (CODE, i + 1), 500 + i)
    kit.townhouse(K, P)
    K.finish(SET, NIGHT, NIGHT, loc=(cx, -QUAY_D, 0.0), rz=PI)
print('houses %.1fs' % (time.time() - T0))

# ==============================================================================================
# Quay: cobbles, quay wall with coping, water stairs, bollards; water and sea bed
# ==============================================================================================
gnd = geo.Builder('%s Quay' % CODE)
gnd.grid(24, 8, lambda s, t: (-30 + 60 * s, -QUAY_D - 1.0 + (QUAY_D + 1.0 - 0.45) * t, 0.0), 'Cobbles Dry', (60, QUAY_D + 0.55), smooth=False)
gnd.finish(SET, dicing=1.0)
KQ = kit.Kit('%s Quay Wall' % CODE, 71)
b = KQ.b
b.box(-30, -0.45, -0.2, 30, 0.0, 0.06, 'Limestone', 0.03)              # coping stones
b.box(-30, -0.6, BED - 0.4, 30, 0.0, -0.2, 'Ashlar Grey')                  # wall face at y = 0
for k in range(30):
    b.box(-30 + 2 * k + 0.02, -0.05, -0.32, -30 + 2 * k + 1.98, 0.04, -0.2, 'Limestone', 0.01)
# water stair against the wall (west of the main jetty), going down to the water
for k in range(7):
    b.box(-9.6 + k * 0.42, 0.0, BED, -9.6 + (k + 1) * 0.42, 1.1, -0.06 - k * 0.17, 'Limestone', 0.02)
b.box(-9.6 + 7 * 0.42, 0.0, BED, -5.4, 1.1, WATER - 0.15, 'Limestone', 0.02)
for xb in (-24, -16, -11, 4.5, 9.0, 17.0, 24.0):
    kit2.bollard(KQ, xb, -0.9, 0.0, rope=(xb in (4.5, 9.0, -11)))
for xb in (-1.9, 1.9):
    kit2.bollard(KQ, xb, 19.4, 0.0, rope=False)
KQ.finish(SET, NIGHT, NIGHT)
water = geo.Builder('%s Water' % CODE)
water.grid(24, 24, lambda s, t: (-1600 + 3200 * s, 0.0 + 1600 * t, WATER), 'Water Still', (3200, 1600), smooth=False)
water.finish(SET, split_disp=False)
bed = geo.Builder('%s Sea Bed' % CODE)
bed.grid(12, 12, lambda s, t: (-160 + 320 * s, -0.5 + 260 * t, BED - 0.4 * math.sin(s * 7) * math.sin(t * 5) - 6 * t), 'Rock', (320, 260),
         smooth=True)
bed.finish(SET)
print('quay %.1fs' % (time.time() - T0))

# ==============================================================================================
# Jetties
# ==============================================================================================
KJ = kit.Kit('%s Jetties' % CODE, 72)
kit2.dock(KJ, -1.6, 1.6, -0.2, 20.0, 0.0, WATER, BED, 'Planks', 'Timber Dark', 2.4, rail=None, seed=3)
kit2.dock(KJ, -6.5, 6.5, 20.0, 23.2, 0.0, WATER, BED, 'Planks', 'Timber Dark', 2.6, rail=None, seed=4)
kit2.dock(KJ, 12.0, 14.2, -0.2, 13.0, -0.15, WATER, BED, 'Planks Grey', 'Timber Dark', 2.2, rail=None, seed=5)
# mooring posts with rope, lanterns on posts along the main jetty
for x, y in ((1.75, 6.0), (1.75, 13.5), (-1.75, 9.0), (6.4, 21.6), (-6.4, 21.6), (14.35, 9.0)):
    KJ.b.cyl((x, y, BED - 0.3), (x, y, 0.75), 0.15, 'Timber Dark', 10)
    KJ.b.torus((x, y, 0.45), 0.17, 0.035, 'Rope', 14, 6, 'Z')
for x, y in ((-1.4, 4.0), (1.4, 11.0), (-1.4, 18.0), (5.8, 22.9), (-5.8, 22.9)):
    KJ.b.cyl((x, y, 0.0), (x, y, 2.4), 0.07, 'Timber Dark', 8)
    KJ.b.beam((x, y, 2.35), (x + (0.45 if x > 0 else -0.45), y, 2.35), 0.07, 0.07, 'Timber Dark')
    kit.lantern(KJ, (x + (0.45 if x > 0 else -0.45), y, 1.85), 0.95)
KJ.finish(SET, NIGHT, NIGHT)

# ==============================================================================================
# Boats
# ==============================================================================================
KB = kit.Kit('%s Boats' % CODE, 73)
BOAT_A = (4.6, 12.0)
kit2.boat(KB, BOAT_A[0], BOAT_A[1], WATER, PI / 2 + 0.05, 7.5, 2.4, 1.05, 'Paint Red', 'Paint Yellow', sail='Canvas Red', seed=1,
          lantern_night=True)
kit2.boat(KB, 9.4, 4.5, WATER, PI / 2 - 0.08, 6.0, 2.1, 0.95, 'Paint Blue', 'Paint Yellow', sail=None, mast=True, seed=2)
kit2.boat(KB, -5.0, 7.5, WATER, PI / 2 + 0.25, 4.2, 1.6, 0.8, 'Paint Green', 'Planks Pale', sail=None, mast=False, seed=3, oars=True)
kit2.boat(KB, 17.5, 28.0, WATER, 0.6, 7.0, 2.3, 1.0, 'Paint Yellow', 'Paint Blue', sail='Canvas Blue', seed=4)
KB.finish(SET, NIGHT, NIGHT)

# ==============================================================================================
# Breakwater + lighthouse at the harbor mouth
# ==============================================================================================
KL = kit.Kit('%s Lighthouse' % CODE, 74)
b = KL.b
LH = (34.0, 62.0)
pts = [(22.0, 24.0), (26.0, 36.0), (30.0, 48.0), (33.0, 58.0)]
for (ax, ay), (bx, by) in zip(pts, pts[1:]):
    n = int(math.hypot(bx - ax, by - ay) / 1.6)
    for k in range(n):
        t = k / n
        x, y = ax + (bx - ax) * t, ay + (by - ay) * t
        for off in (-1.6, 0.0, 1.6):
            kit.rock(KL, x + off + rng.uniform(-0.5, 0.5), y + rng.uniform(-0.5, 0.5), WATER + rng.uniform(-0.3, 0.3), rng.uniform(1.0, 1.7),
                     'Rock', 0.6, 3000 + k * 7 + int(off * 3) + int(ax))
    with KL.push((ax, ay, 0), math.atan2(by - ay, bx - ax) - PI / 2):
        L = math.hypot(bx - ax, by - ay)
        b.box(-1.4, 0.0, WATER - 0.4, 1.4, L, 0.6, 'Ashlar Grey', 0.04)
b.lathe([(4.2, BED), (4.2, WATER + 0.4), (3.6, 1.0), (3.6, 1.4)], 'Ashlar Grey', 28, (LH[0], LH[1], 0), cap_top=True)
prof = [(2.1, 1.4), (1.95, 4.4), (1.8, 7.4), (1.65, 10.4), (1.5, 13.4)]
for k in range(4):
    b.lathe([prof[k], prof[k + 1]], 'Plaster White' if k % 2 == 0 else 'Paint Red', 24, (LH[0], LH[1], 0), cap_top=False)
b.lathe([(1.5, 13.4), (2.2, 13.7), (2.2, 13.9), (0.0, 13.9)], 'Iron Black', 24, (LH[0], LH[1], 0))
b.lathe([(1.05, 13.9), (1.05, 15.6)], 'Glass Clear', 16, (LH[0], LH[1], 0), cap_top=False)
for k in range(8):
    a = 2 * PI * k / 8
    b.cyl((LH[0] + 1.06 * math.cos(a), LH[1] + 1.06 * math.sin(a), 13.9), (LH[0] + 1.06 * math.cos(a), LH[1] + 1.06 * math.sin(a), 15.6),
          0.04, 'Iron Black', 6)
b.lathe([(1.25, 15.6), (0.15, 16.8), (0.0, 16.9)], 'Paint Red', 16, (LH[0], LH[1], 0))
b.sphere((LH[0], LH[1], 17.0), 0.18, 'Gold', 8, 6)
b.torus((LH[0], LH[1], 14.8), 2.15, 0.03, 'Iron Black', 32, 4, 'Z')
b.sphere((LH[0], LH[1], 14.6), 0.45, 'Brass', 12, 8)
KL.n.sphere((LH[0], LH[1], 14.7), 0.6, 'Glow Warm', 12, 8)
KL.light((LH[0], LH[1], 14.7), 2600, '#ffc070', 0.5)
for k in range(5):
    a = 2 * PI * k / 5 + 0.4
    b.cbox((LH[0] + 2.0 * math.cos(a), LH[1] + 2.0 * math.sin(a), 6.0 + 2.4 * k), (0.06, 0.55, 0.9), 'Glass Leaded', 0.0, rot=(0, 0, a))
b.box(LH[0] - 0.6, LH[1] - 2.2, 1.4, LH[0] + 0.6, LH[1] - 1.95, 3.6, 'Paint Blue', 0.02)
KL.finish(SET, NIGHT, NIGHT)
# far shore hills
hill = geo.Builder('%s Far Shore' % CODE)


def shore(s, t):
    # two headlands left and right; open sea (and the horizon) in the middle, behind the lighthouse
    x = -420 + 840 * s
    y = 90 + 260 * t
    side = min(1.0, max(0.0, (abs(x - 30) - 70) / 120.0)) ** 1.5
    h = side * ((t ** 0.6) * 46 + 10 * math.sin(x / 37) * math.sin(y / 29)) + 4 * side
    return (x, y, h + WATER - 2.0)


hill.grid(40, 16, shore, 'Grass', (720, 200), smooth=True)
hill.grid(6, 6, lambda s, t: (-300 + 600 * s, -300 + 290 * t, -0.08), 'Grass', (600, 290), smooth=False)
hill.finish(SET)
print('boats/lighthouse %.1fs' % (time.time() - T0))

# ==============================================================================================
# Quay props
# ==============================================================================================
KP = kit.Kit('%s Props' % CODE, 75)
# fish stall with a 'FISH' board
kit.stall(KP, -15.0, -6.5, PI, 'Canvas Blue', ('pots',))
fish_sign = art2.path('FISH')
if bpy.data.materials.get('BL Sign word_fish') is None:
    mats.image_material('Sign word_fish', fish_sign, base='Planks Pale')
KP.b.quad((-16.0, -5.55, 2.35), (-14.0, -5.55, 2.35), (-14.0, -5.55, 2.95), (-16.0, -5.55, 2.95), 'Sign word_fish', [(0, 0), (1, 0), (1, 1), (0, 1)])
KP.b.box(-16.05, -5.5, 2.3, -13.95, -5.45, 3.0, 'Planks Pale', 0.01)
for k in range(5):
    kit.crate_of(KP, -16.2 + k * 0.55, -5.2, 0.0, 'Feather Grey', (0.5, 0.36, 0.22))
for x, y in ((-6.5, -2.0), (-6.0, -2.6), (8.0, -3.0), (8.6, -2.4), (8.2, -2.7), (-20.0, -4.0), (16.0, -6.0)):
    kit.barrel(KP, x, y, 0.0, rng.uniform(0.26, 0.31), rng.uniform(0.8, 0.9))
kit.barrel(KP, 8.3, -2.75, 0.86, 0.27, 0.8)
for x, y, s_ in ((5.5, -1.6, (0.8, 0.6, 0.5)), (6.3, -1.4, (0.7, 0.55, 0.45)), (5.9, -1.5, (0.6, 0.45, 0.4)), (-3.5, -1.5, (0.7, 0.5, 0.45)),
                 (-4.2, -1.8, (0.6, 0.5, 0.45)), (12.5, -2.5, (0.9, 0.6, 0.6))):
    kit.crate(KP, x, y, 0.0, s_, rng.uniform(-0.2, 0.2))
kit.crate(KP, 5.9, -1.5, 0.5, (0.55, 0.42, 0.36), 0.3)
kit.crate(KP, 12.5, -2.5, 0.6, (0.6, 0.45, 0.4), -0.2)
for x, y in ((-2.6, -1.0), (2.8, -0.9), (13.2, 3.0), (0.6, 21.5), (-10.4, -1.2)):
    kit2.rope_coil(KP, x, y, 0.0, 0.32, 4)
kit.cart(KP, 15.5, -4.2, 0.2, 'barrels')
# fishing nets drying on poles
for k, (x0, x1) in enumerate(((-24.0, -20.0), (19.0, 22.5))):
    for xx in (x0, x1):
        KP.b.cyl((xx, -3.0, 0.0), (xx, -3.0, 2.4), 0.06, 'Timber Oak', 8)
    KP.b.cyl((x0, -3.0, 2.35), (x1, -3.0, 2.35), 0.04, 'Rope', 6)

    def net(s, t, x0=x0, x1=x1):
        return (x0 + (x1 - x0) * s, -3.0 + 0.08 * math.sin(s * 9 + t * 4), 2.35 - t * (1.6 + 0.35 * math.sin(PI * s)))
    KP.b.grid(10, 6, net, 'Cloth Brown', (x1 - x0, 1.8), smooth=True, both=True)
for x in (-12.5, -1.0, 7.0, 18.5):
    kit.lamp_post(KP, x, -0.95 if x != -1.0 else -0.9, 3.3)
for i in range(7):
    kit2.gull(KP, rng.uniform(-20, 20), rng.uniform(-2.5, -0.6), 0.0)
for xb in (-24, 17.0, 24.0):
    kit2.gull(KP, xb, -0.9, 0.48)
KP.finish(SET, NIGHT, NIGHT)
print('props %.1fs' % (time.time() - T0))

# ==============================================================================================
# Marks
# ==============================================================================================
MK = C['marks']
HERO = Vector((2.2, -3.4, 0))
RIVAL = Vector((4.4, -1.8, 0))
mk = {}


def mark(name, p, facing):
    mk[name] = look.mark(MK, '%s_%s' % (CODE, name), V(*p), facing)


mark('MARK_HERO', HERO, look.face_towards(HERO, RIVAL) - 75)
mark('MARK_RIVAL', RIVAL, look.face_towards(RIVAL, HERO) + 55)
mark('MARK_SIBLING', (0.9, -4.2, 0), look.face_towards((0.9, -4.2), RIVAL) - 30)
mark('MARK_RULER', (0.0, 21.8, 0.0), 0.0)
cc = Vector((3.3, -2.6, 0))
for i, (x, y) in enumerate(((-2.2, -1.4), (-1.6, -4.2), (6.4, -3.2), (7.6, -5.0), (0.2, -6.4), (5.0, -6.4), (-0.6, 1.5), (0.8, 3.0))):
    mark('MARK_CROWD_%d' % (i + 1), (x, y, 0), look.face_towards((x, y), cc))
mark('MARK_GIANT', (-16.0, 26.0, BED), look.face_towards((-16.0, 26.0), HERO))
mark('MARK_GUARD_1', (-9.0, -1.0, 0), 0.0)
mark('MARK_GUARD_2', (-0.9, 0.8, 0), 0.0)
mark('MARK_BOAT', (BOAT_A[0] + 0.0, BOAT_A[1] - 1.2, WATER - 1.05 * 0.45 + 1.05 * 0.62), 180.0)

# ==============================================================================================
# Cameras
# ==============================================================================================
CM = C['cams']
cams = {}


def cam(name, pos, tgt, lens, note):
    cams[name] = look.camera(CM, '%s_%s' % (CODE, name), V(*pos), V(*tgt), lens, note)


cam('WIDE_ESTABLISH', (-6.5, -8.2, 4.8), (5.0, 26.0, 1.2), 18, 'from the harbor houses over the quay: jetties, boats, breakwater and lighthouse; room for a crowd')
cam('LOW_HERO', (HERO.x - 0.5, HERO.y - 2.8, 0.32), (HERO.x + 0.25, HERO.y + 0.6, 1.45), 20, 'knee-height up at MARK_HERO; jetty, red sail and sky behind')
cam('CROWD_MED', (9.8, -8.8, 2.4), (2.6, -2.0, 1.2), 28, 'crowd on the quay around hero + rival from the east, framed by crowd at the edges; jetty and sea behind')
cam('TWO_SHOT', (HERO.x + 0.7, HERO.y - 4.4, 1.2), (cc.x, cc.y + 0.6, 1.1), 35, 'hero (left) and rival (right) facing off on the quay, jetty and boats behind')
cam('CLOSE_A', (HERO.x + 1.25, HERO.y - 1.15, 1.08), (HERO.x, HERO.y, 1.06), 50, 'hero face (head ~1.0 m)')
cam('CLOSE_B', (RIVAL.x - 1.2, RIVAL.y - 1.45, 1.66), (RIVAL.x, RIVAL.y, 1.68), 50, 'rival face (Rich kid head ~1.6 m)')
cam('INSERT_BOAT', (1.0, 8.5, 1.5), (BOAT_A[0], BOAT_A[1] + 0.5, 0.4), 30, 'the red-sail boat moored at the main jetty')
cam('INSERT_DOCK', (0.4, 4.6, 0.7), (-0.2, 21.0, 1.0), 24, 'low along the main jetty planks: lanterns, mooring posts, the T-head')
cam('WIDE_REVERSE', (1.2, 22.4, 2.6), (0.0, -12.0, 4.0), 20, 'from the jetty head back to the quay and the harbor houses')

# ==============================================================================================
# Lights
# ==============================================================================================
worlds = {}
# sun from the east-south-east: the house row would shade the whole 10 m quay with a southern sun
sun_day = look.sun_obj(C['DAY'], 'DAY', 75.0, '%s Sun DAY' % CODE)
worlds['DAY'] = look.world_sky(sc, 'DAY', '%s Sky DAY' % CODE, look.sun_direction(sun_day))
sun_g = look.sun_obj(C['GOLDEN'], 'GOLDEN', -100.0, '%s Sun GOLDEN' % CODE, 4.6, 15.0)   # low from the west, raking along the quay
worlds['GOLDEN'] = look.world_sky(sc, 'GOLDEN', '%s Sky GOLDEN' % CODE, look.sun_direction(sun_g))
moon = look.sun_obj(C['NIGHT'], 'NIGHT', -36.0, '%s Moon' % CODE)
worlds['NIGHT'] = look.world_sky(sc, 'NIGHT', '%s Sky NIGHT' % CODE, look.sun_direction(moon))
look.area(C['NIGHT'], '%s moon fill' % CODE, V(-10, -40, 28), (math.radians(55), 0, math.radians(-15)), 30, 70, '#7f9cff')

scenes = setbase.finish(sc, master, C, TITLE, CODE, cams['WIDE_ESTABLISH'], worlds,
                        os.path.join(setbase.OUT, 'harbor', 'harbor.blend'))
print('saved %.1fs' % (time.time() - T0))
