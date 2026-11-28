"""Backlot set 4: CASTLE COURTYARD.  python3 -I build_castle_courtyard.py  ->  castle_courtyard/castle_courtyard.blend
Bailey 30 x 25 m inside crenellated curtain walls (7 m) with four round corner towers, a twin-tower gatehouse
(south, raised portcullis, open gates), and the keep (north, 17 m + turrets) reached by a 12-step stair to a
landing at 3 m (MARK_RULER).  Well, stable lean-to, kitchen house, training yard (archery targets, straw
dummies), braziers at the stair foot, torches, banners.  Courtyard floor: cobbles + a flagstone path."""
import sys, os, math, time, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, '..', 'materials')]
import bpy
from mathutils import Vector
import mats, geo, look, kit, kit2, setbase

T0 = time.time()
M = geo.M
PI = math.pi
CODE, TITLE = 'CC', 'Castle Courtyard'
sc, master, C = setbase.start(CODE, TITLE)
SET, NIGHT = C['set'], C['NIGHT']
mats.set_global(wet=0.2)
rng = random.Random(4)

WELL = (-6.0, 4.5)
XI, YS, YN = 15.0, -11.0, 14.0     # courtyard inner faces: x = +-15, south y = -11, north y = 14
WT, WH = 2.0, 7.0                  # curtain wall thickness / height
KEEP_X, KEEP_Y0, KEEP_Y1, KEEP_H = 7.0, 6.0, 14.0, 17.0
LAND_Z, STAIR_Y0, STAIR_D, STAIR_N = 3.0, 0.4, 0.42, 12


def V(x, y, z=0.0):
    return Vector((x * M, y * M, z * M))


# ==============================================================================================
# Curtain walls, corner towers, gatehouse
# ==============================================================================================
KW = kit.Kit('%s Walls' % CODE, 11)
# west (outer face x = -17), east (x = 17), north (y = 16); south built around the gate
with KW.push((-XI - WT, YN + WT, 0), -PI / 2):
    kit2.crenel_wall(KW, 0.0, (YN + WT) - (YS - WT), WH, WT)
with KW.push((XI + WT, YS - WT, 0), PI / 2):
    kit2.crenel_wall(KW, 0.0, (YN + WT) - (YS - WT), WH, WT)
with KW.push((XI + WT, YN + WT, 0), PI):
    kit2.crenel_wall(KW, 0.0, 2 * (XI + WT), WH, WT)
with KW.push((-XI - WT, YS - WT, 0)):
    kit2.crenel_wall(KW, 0.0, XI + WT - 6.0, WH, WT)
    kit2.crenel_wall(KW, XI + WT + 6.0, 2 * (XI + WT), WH, WT)
# wall-walk stair along the inner face of the west wall (climbs north)
with KW.push((-XI, 5.0, 0)):
    for k in range(16):
        z1 = (k + 1) * WH / 16
        KW.b.box(0.0, k * 0.5, -0.1, 1.3, k * 0.5 + 0.5, z1, 'Ashlar Grey', 0.01)
for cx, cy in ((-XI - 1.0, YS - 1.0), (XI + 1.0, YS - 1.0), (-XI - 1.0, YN + 1.0), (XI + 1.0, YN + 1.0)):
    kit2.round_tower(KW, cx, cy, 3.2, 10.5, 'Ashlar Grey', 'Roof Slate', 6.0, 3, lit=True, seed=int(cx * 7 + cy))
KW.finish(SET, NIGHT, NIGHT)

# gatehouse: two square towers (x 2..6.5 either side) + the gate block over a round-arched passage
KG = kit.Kit('%s Gatehouse' % CODE, 12)
b = KG.b
GY0, GY1 = YS - WT - 1.5, YS + 1.2          # gatehouse front (outside) .. back (courtyard side)
GW, GH, ARCH_W, ARCH_SPRING = 6.5, 11.0, 4.0, 3.2
for sx in (-1, 1):
    x0, x1 = sorted((sx * 2.0, sx * GW))
    b.box(x0, GY0, -0.3, x1, GY1, GH, 'Ashlar Grey')
    with KG.push((0, GY0, 0)):
        kit2.crenel_wall(KG, x0, x1, GH, 0.6, walk=False, body=False)
    with KG.push(((x0 + x1) / 2, GY1, 0), PI):
        kit2.crenel_wall(KG, -(x1 - x0) / 2, (x1 - x0) / 2, GH, 0.6, walk=False, body=False)
    for xs, rz_ in ((x0, -PI / 2), (x1, PI / 2)):
        if (sx < 0 and xs == x1) or (sx > 0 and xs == x0):
            continue
        with KG.push((xs, GY1 if rz_ < 0 else GY0, 0), rz_):
            kit2.crenel_wall(KG, 0.0, GY1 - GY0, GH, 0.6, walk=False, body=False)
    # arrow slits + a lit window on the courtyard side
    for z in (4.0, 7.2):
        cxw = sx * 4.25
        b.box(cxw - 0.09, GY0 - 0.02, z, cxw + 0.09, GY0 + 0.01, z + 1.2, 'Charcoal')
# gate block over the passage (front and back faces with the arch)
for yy, rz_ in ((GY0, 0.0), (GY1, PI)):
    with KG.push((0, yy, 0), rz_):
        kit.arch_wall(b, -2.0, 2.0, 0.0, 9.0, [(0.0, ARCH_W, ARCH_SPRING, 'round', None)], 'Ashlar Grey', 0.0, 0.0,
                      voussoirs='Limestone')
b.box(-2.0, GY0, 9.0 - 0.01, 2.0, GY1, 9.0, 'Ashlar Grey')
with KG.push((0, GY0, 0)):
    kit2.crenel_wall(KG, -2.0, 2.0, 9.0, 0.6, walk=False, body=False)
# passage vault + side walls
pts = kit.arch_pts(0.0, ARCH_W, ARCH_SPRING, 'round', 16)
for (xa, za), (xb, zb) in zip(pts, pts[1:]):
    b.quad((xa, GY1, za), (xb, GY1, zb), (xb, GY0, zb), (xa, GY0, za), 'Ashlar Grey')
b.grid(4, 6, lambda s, t: (-ARCH_W / 2 + ARCH_W * s, GY0 - 2.0 + (GY1 - GY0 + 2.0) * t, 0.05), 'Flagstones', (ARCH_W, GY1 - GY0 + 2.0),
       smooth=False)
# portcullis, raised: bottom spikes hang just under the arch crown
PY = (GY0 + GY1) / 2 - 0.6
pz0 = ARCH_SPRING + 0.9
for i in range(9):
    x = -1.9 + i * 3.8 / 8
    b.box(x - 0.05, PY - 0.05, pz0, x + 0.05, PY + 0.05, pz0 + 4.0, 'Iron Black', 0.01)
    b.cyl((x, PY, pz0), (x, PY, pz0 - 0.28), 0.05, 'Iron Black', 6, 0.004)
for k in range(6):
    z = pz0 + 0.15 + k * 0.7
    b.box(-2.0, PY - 0.07, z, 2.0, PY + 0.07, z + 0.09, 'Iron Black', 0.01)
# gates: two oak leaves swung open against the passage walls (courtyard side)
for sx in (-1, 1):
    with KG.push((sx * (ARCH_W / 2 - 0.1), GY1 - 0.5, 0), sx * PI / 2 * 0.96):
        lw = ARCH_W / 2 - 0.05
        xa, xb = (0, -lw) if sx > 0 else (0, lw)
        xa, xb = min(xa, xb), max(xa, xb)
        for k in range(8):
            b.box(xa + k * lw / 8 + 0.005, -0.04, 0.05, xa + (k + 1) * lw / 8 - 0.005, 0.06, ARCH_SPRING + 0.6, 'Planks', 0.008,
                  grain=(0, 0, 1))
        for hz in (0.5, 1.8, 3.2):          # straps + studs on the face that looks into the passage
            b.box(xa, 0.06, hz, xb, 0.085, hz + 0.1, 'Iron Black', 0.005)
        for k in range(10):
            for hz in (0.55, 1.85, 3.25):
                b.sphere((xa + 0.1 + k * (lw - 0.2) / 9, 0.09, hz), 0.025, 'Iron Black', 6, 4)
# courtyard-side flat banners on the gate towers + torches
for sx, design in ((-1, kit2.art_banner('gold lion')), (1, kit2.art_banner('silver tower'))):
    with KG.push((sx * 4.25, GY1, 0), PI):
        kit.flat_banner(KG, 0.0, -0.02, 9.6, design, length=2.55, width=0.9)
    with KG.push((sx * 2.4, GY1, 0), PI):
        kit2.wall_torch(KG, 0.0, 0.0, 2.7)
with KG.push((0, GY0, 0)):
    for sx in (-1, 1):
        kit2.wall_torch(KG, sx * 2.5, 0.0, 2.7)
KG.finish(SET, NIGHT, NIGHT)
print('walls %.1fs' % (time.time() - T0))

# ==============================================================================================
# Keep + stair
# ==============================================================================================
KK = kit.Kit('%s Keep' % CODE, 13)
b = KK.b
W2 = KEEP_X
# front facade in bands: plinth | door band | windows | windows | top
with KK.push((0, KEEP_Y0, 0)):
    b.box(-W2 - 0.25, -0.25, -0.3, W2 + 0.25, 0.3, 1.0, 'Ashlar', 0.03)            # battered plinth
    b.quad((-W2, 0, 1.0), (W2, 0, 1.0), (W2, 0, LAND_Z), (-W2, 0, LAND_Z), 'Ashlar')
    kit.arch_wall(b, -W2, W2, LAND_Z, 7.5, [(0.0, 1.9, LAND_Z + 2.3, 'round', None)], 'Ashlar', 0.0, 0.7, voussoirs='Limestone')
    kit.door(KK, 0.0, 1.9, 3.25, 0.0, 0.7, 'Paint Red', LAND_Z, step=False)
    wins = []
    for z0, z1, spring, w in ((8.2, 11.2, 9.9, 1.1), (12.2, 15.0, 13.8, 1.0)):
        b.quad((-W2, 0, z0 - 0.7 if z0 == 8.2 else z0 - 1.0), (W2, 0, z0 - 0.7 if z0 == 8.2 else z0 - 1.0), (W2, 0, z0), (-W2, 0, z0), 'Ashlar')
        ops = [(x, w, spring, 'round', None) for x in (-4.9, 0.0, 4.9)]
        kit.arch_wall(b, -W2, W2, z0, z1, ops, 'Ashlar', 0.0, 0.6, voussoirs='Limestone')
        for x, ww, s, _, _ in ops:
            wins.append((x, z0, ww, s))
    b.quad((-W2, 0, 15.0), (W2, 0, 15.0), (W2, 0, KEEP_H), (-W2, 0, KEEP_H), 'Ashlar')
    for x, z0, ww, s in wins:
        P = [(x - ww / 2, 0.32, z0)] + [(px, 0.32, pz) for px, pz in kit.arch_pts(x, ww, s, 'round', 12)] + [(x + ww / 2, 0.32, z0)]
        b.poly(P[::-1], 'Glass Leaded')
        if rng.random() < 0.8:
            KK.n.poly([(px, 0.31, pz) for px, _, pz in P][::-1], 'Glass Window Lit')
        b.box(x - ww / 2 - 0.1, -0.12, z0 - 0.12, x + ww / 2 + 0.1, 0.05, z0, 'Limestone', 0.015)
        b.box(x - 0.03, 0.28, z0, x + 0.03, 0.34, s, 'Iron Black')
    # string courses
    for z in (7.45, 11.95, 15.4):
        b.box(-W2 - 0.12, -0.18, z, W2 + 0.12, 0.05, z + 0.25, 'Limestone', 0.02)
    # tall banners between the windows + torches beside the door
    kit.flat_banner(KK, -2.45, -0.02, 16.6, kit2.art_banner('gold lion tall'), length=4.4, width=1.15)
    kit.flat_banner(KK, 2.45, -0.02, 16.6, kit2.art_banner('silver tower tall'), length=4.4, width=1.15)
    for sx in (-1, 1):
        kit2.wall_torch(KK, sx * 1.75, 0.0, LAND_Z + 2.4)
# sides and back
with KK.push((-W2, KEEP_Y1, 0), -PI / 2):
    b.wall(0, KEEP_Y1 - KEEP_Y0, -0.3, KEEP_H, 'Ashlar', [(3.0, 3.25, 5.0, 6.2), (3.0, 3.25, 10.0, 11.2), (5.0, 5.25, 13.0, 14.2)], 0.0, 0.4, 'Charcoal')
with KK.push((W2, KEEP_Y0, 0), PI / 2):
    b.wall(0, KEEP_Y1 - KEEP_Y0, -0.3, KEEP_H, 'Ashlar', [(3.0, 3.25, 5.0, 6.2), (5.0, 5.25, 10.0, 11.2), (3.0, 3.25, 13.0, 14.2)], 0.0, 0.4, 'Charcoal')
with KK.push((W2, KEEP_Y1, 0), PI):
    b.wall(0, 2 * W2, -0.3, KEEP_H, 'Ashlar', [], 0.0)
b.quad((-W2, KEEP_Y0, KEEP_H), (W2, KEEP_Y0, KEEP_H), (W2, KEEP_Y1, KEEP_H), (-W2, KEEP_Y1, KEEP_H), 'Ashlar Grey')
# crenellated parapet on all four sides
with KK.push((0, KEEP_Y0, 0)):
    kit2.crenel_wall(KK, -W2, W2, KEEP_H, 0.6, 'Ashlar', walk=False, body=False)
with KK.push((0, KEEP_Y1, 0), PI):
    kit2.crenel_wall(KK, -W2, W2, KEEP_H, 0.6, 'Ashlar', walk=False, body=False)
with KK.push((-W2, KEEP_Y1, 0), -PI / 2):
    kit2.crenel_wall(KK, 0.0, KEEP_Y1 - KEEP_Y0, KEEP_H, 0.6, 'Ashlar', walk=False, body=False)
with KK.push((W2, KEEP_Y0, 0), PI / 2):
    kit2.crenel_wall(KK, 0.0, KEEP_Y1 - KEEP_Y0, KEEP_H, 0.6, 'Ashlar', walk=False, body=False)
# corner turrets corbelled out from 13 m, with tall slate cones and gold finials
for sx in (-1, 1):
    for yy in (KEEP_Y0, KEEP_Y1):
        cx, cy = sx * (W2 - 0.2), yy + (0.2 if yy == KEEP_Y0 else -0.2)
        b.lathe([(0.3, 12.0), (1.6, 13.4), (1.6, 13.5)], 'Ashlar', 20, (cx, cy, 0), cap_top=False)
        b.lathe([(1.6, 13.5), (1.6, KEEP_H + 2.6)], 'Ashlar', 20, (cx, cy, 0), cap_top=False)
        b.lathe([(1.6, KEEP_H + 2.6), (1.85, KEEP_H + 2.9), (0.08, KEEP_H + 7.4)], 'Roof Slate', 20, (cx, cy, 0), cap_top=True)
        b.cyl((cx, cy, KEEP_H + 7.3), (cx, cy, KEEP_H + 8.4), 0.03, 'Iron Black', 6)
        b.sphere((cx, cy, KEEP_H + 7.4), 0.13, 'Gold', 8, 6)
        # pennant
        b.poly([(cx, cy, KEEP_H + 8.35), (cx + sx * 1.1, cy - 0.05, KEEP_H + 8.1), (cx, cy, KEEP_H + 7.85)], 'Cloth Red')
        b.poly([(cx, cy, KEEP_H + 7.85), (cx + sx * 1.1, cy - 0.05, KEEP_H + 8.1), (cx, cy, KEEP_H + 8.35)], 'Cloth Red')
        if yy == KEEP_Y0:
            a = -PI / 2 + sx * 0.5
            for z in (15.0, 17.6):
                b.cbox((cx + 1.61 * math.cos(a), cy + 1.61 * math.sin(a), z), (0.05, 0.16, 1.0), 'Charcoal', 0.0, rot=(0, 0, a))
            KK.n.cbox((cx + 1.62 * math.cos(a), cy + 1.62 * math.sin(a), 17.6), (0.03, 0.14, 0.95), 'Glass Window Lit', 0.0, rot=(0, 0, a))
# the stair: 12 steps (rise 0.25, tread 0.42) up to a landing in front of the door
with KK.push((0, 0, 0)):
    kit2.stair(KK, -2.6, 2.6, STAIR_Y0, STAIR_D, LAND_Z / STAIR_N, STAIR_N, 'Limestone', side=True, side_h=0.85, side_mat='Ashlar')
    y_top = STAIR_Y0 + STAIR_N * STAIR_D
    b.box(-3.05, y_top, -0.1, 3.05, KEEP_Y0, LAND_Z, 'Ashlar', 0.02)
    b.box(-2.6, y_top - 0.02, LAND_Z - 0.04, 2.6, KEEP_Y0, LAND_Z + 0.02, 'Flagstones Hall')
    for sx in (-1, 1):
        x0, x1 = sorted((sx * 2.6, sx * 3.05))
        b.box(x0, y_top, LAND_Z, x1, KEEP_Y0, LAND_Z + 0.85, 'Ashlar')
        b.box(x0 - 0.04, y_top, LAND_Z + 0.85, x1 + 0.04, KEEP_Y0, LAND_Z + 0.97, 'Limestone', 0.01)
        # newel posts with stone balls at the foot of the stair
        b.box(x0 - 0.1, STAIR_Y0 - 0.3, -0.1, x1 + 0.1, STAIR_Y0 + 0.2, 1.25, 'Limestone', 0.02)
        b.sphere(((x0 + x1) / 2, STAIR_Y0 - 0.05, 1.5), 0.25, 'Limestone', 12, 8)
KK.finish(SET, NIGHT, NIGHT)
print('keep %.1fs' % (time.time() - T0))

# ==============================================================================================
# Courtyard buildings: kitchen house (east), stable lean-to (west)
# ==============================================================================================
KH = kit.Kit('%s Kitchen House' % CODE, 14)
P = dict(W=9.0, D=4.6, floors=[3.3, 2.9], jetty=0.4, ground='stone', stone='Ashlar', plaster='Plaster Cream', timber='Timber Dark',
         style='braced', roof='eaves', roof_mat='Roof Clay Old', pitch=50, win=[[], [-3.0, 0.0, 3.0]], door_x=-2.6, door_paint='Paint Green',
         shutters='Paint Blue', gwin=[1.0, 3.2], win_w=0.8, sides=None, lit=0.7, dormer=True, dormer_x=0.0, chimney_x=2.5,
         lantern_x=-1.3, flowers=True)
kit.townhouse(KH, P)
KH.finish(SET, NIGHT, NIGHT, loc=(XI - 0.1 - 4.6 - 0.4, -6.5 + 4.5, 0), rz=-PI / 2)

KS = kit.Kit('%s Stable' % CODE, 15)
b = KS.b
SX0, SX1, SY0, SY1 = -XI, -XI + 3.6, -6.5, 3.5
for i in range(6):
    y = SY0 + i * (SY1 - SY0) / 5
    b.beam((SX1, y, 0), (SX1, y, 2.7), 0.2, 0.2, 'Timber Dark')
    b.beam((SX1, y, 2.25), (SX1 - 0.6, y, 2.75), 0.12, 0.12, 'Timber Dark') if 0 < i < 5 else None
b.beam((SX1, SY0, 2.7), (SX1, SY1, 2.7), 0.22, 0.25, 'Timber Dark')
for i in range(9):
    y = SY0 + i * (SY1 - SY0) / 8
    b.beam((SX0, y, 4.3), (SX1 + 0.5, y, 2.55), 0.1, 0.14, 'Timber Oak')
with KS.push(((SX0 + SX1) / 2 + 0.25, (SY0 + SY1) / 2, 0)):
    L = math.hypot(SX1 + 0.5 - SX0, 4.3 - 2.55)
    ang = math.atan2(4.3 - 2.55, SX1 + 0.5 - SX0)

    def roof_fn(s, t):
        x = SX0 + (SX1 + 0.6 - SX0) * s
        z = 4.45 - (4.45 - 2.65) * s - 0.05 * math.sin(PI * t)
        return (x - ((SX0 + SX1) / 2 + 0.25), (SY0 - 0.4) + (SY1 - SY0 + 0.8) * t - (SY0 + SY1) / 2, z)
    b.grid(4, 10, roof_fn, 'Roof Shingle', (L, SY1 - SY0 + 0.8), smooth=False)
# stall partitions, hay racks, water trough
for i in range(1, 5):
    y = SY0 + i * (SY1 - SY0) / 5
    b.box(SX0, y - 0.04, 0, SX1 - 0.4, y + 0.04, 1.4, 'Planks', 0.01, grain=(1, 0, 0))
b.box(SX1 + 0.2, -1.6, 0, SX1 + 0.7, 0.6, 0.55, 'Planks Grey', 0.02)
b.box(SX1 + 0.25, -1.55, 0.4, SX1 + 0.65, 0.55, 0.5, 'Water Still')
for k in range(4):
    kit.hay_bale(KS, SX0 + 1.0, SY0 + 0.9 + k * 2.0, 0.0, PI / 2)
kit.hay_pile(KS, SX0 + 1.4, SY0 + 2.4, 0.0, 0.8, 0.5)
kit.hay_pile(KS, SX0 + 1.2, SY0 + 6.4, 0.0, 0.7, 0.45)
kit.lantern(KS, (SX1 - 0.15, -1.6, 2.15), 0.9)
KS.finish(SET, NIGHT, NIGHT)

# ==============================================================================================
# Ground: cobbled courtyard, flagstone path gate -> stair, grass outside, hills
# ==============================================================================================
gnd = geo.Builder('%s Cobbles' % CODE)
gnd.grid(24, 20, lambda s, t: (-XI - 0.5 + (2 * XI + 1.0) * s, YS - 0.5 + (YN - YS + 1.0) * t, 0.0), 'Cobbles Dry', (2 * XI + 1, YN - YS + 1),
         smooth=False)
gnd.finish(SET, dicing=1.0)
path = geo.Builder('%s Path' % CODE)
path.grid(3, 10, lambda s, t: (-1.7 + 3.4 * s, YS - 0.3 + (STAIR_Y0 - YS + 0.3) * t, 0.05), 'Flagstones', (3.4, STAIR_Y0 - YS + 0.3), smooth=False)
path.grid(16, 3, lambda s, t: (WELL[0] + (0.8 + 1.1 * t) * math.cos(-2 * PI * s), WELL[1] + (0.8 + 1.1 * t) * math.sin(-2 * PI * s), 0.05),
          'Flagstones', (12, 1.1), smooth=False)
path.finish(SET, dicing=1.0)
kerb = geo.Builder('%s Kerbs' % CODE)
for sx in (-1, 1):
    kerb.box(sx * 1.7 - 0.08, YS, -0.05, sx * 1.7 + 0.08, STAIR_Y0, 0.1, 'Limestone', 0.01)
kerb.finish(SET)
out = geo.Builder('%s Fields' % CODE)
out.grid(6, 6, lambda s, t: (-300 + 600 * s, -300 + 600 * t, -0.06), 'Grass', (600, 600), smooth=False)


def hill_fn(s, t):
    x = -260 + 520 * s
    y = -260 + 520 * t
    d = math.hypot(x, y)
    h = max(0.0, (d - 60) / 200) ** 1.5 * 38 + 6 * math.sin(x / 31) * math.sin(y / 23) * max(0.0, min(1.0, (d - 60) / 60))
    return (x, y, h - 0.3)


out.grid(40, 40, hill_fn, 'Grass', (520, 520), smooth=True)
# dirt road leaving the gate to the south
out.grid(2, 12, lambda s, t: (-2.2 + 4.4 * s + 6 * math.sin(t * 2.2), YS - WT - 1.5 - 55 * t, 0.01 + 0.0 * t), 'Dirt', (4.4, 55), smooth=False)
out.finish(SET, dicing=2.0)
KT = kit.Kit('%s Trees' % CODE, 16)
for i, (x, y, h) in enumerate(((-14, -30, 10.5), (9, -34, 9.5), (-26, -22, 11.0), (24, -26, 10.0), (-34, 8, 12.0), (35, 2, 11.5),
                               (-6, -46, 10.0), (16, -48, 11.0))):
    kit.tree(KT, x, y, 0.0, h, 'oak', 200 + i, 6000)
KT.finish(SET, NIGHT, NIGHT)
print('ground %.1fs' % (time.time() - T0))

# ==============================================================================================
# Props: well, training yard, braziers, barrels, crates, cart
# ==============================================================================================
KP = kit.Kit('%s Props' % CODE, 17)
kit.well(KP, WELL[0], WELL[1])
kit.barrel(KP, WELL[0] + 1.3, WELL[1] - 0.6, 0.0, 0.25, 0.6, lid=False)
kit2.archery_target(KP, 13.4, 4.8, -PI / 2 + 0.15)
kit2.archery_target(KP, 13.6, 7.4, -PI / 2 - 0.1)
kit2.training_dummy(KP, 6.0, -7.4, 0.4)
kit2.training_dummy(KP, 7.8, -8.6, -0.2)
for sx in (-1, 1):
    kit2.brazier(KP, sx * 3.6, STAIR_Y0 - 0.6, 0.0, 1.0)
for x, y in ((-13.3, -9.4), (-12.7, -9.8), (13.2, 9.8), (12.6, 10.4), (-9.6, 12.8)):
    kit.barrel(KP, x, y, 0.0, rng.uniform(0.27, 0.31), rng.uniform(0.8, 0.9))
for x, y in ((-12.2, 12.6), (-11.5, 12.9), (12.9, -9.6), (12.3, -9.9)):
    kit.crate(KP, x, y, 0.0)
kit.crate(KP, -11.85, 12.75, 0.45, (0.5, 0.4, 0.35))
kit.crate_of(KP, 11.8, 12.3, 0.0, 'Apple Red')
kit.cart(KP, -10.0, 8.6, 0.35, 'barrels')
kit.cart(KP, -9.2, -8.6, -0.5, 'hay')
for x, y in ((9.5, 12.4), (-13.0, 10.5)):
    kit.hay_bale(KP, x, y, 0.0, rng.uniform(0, PI))
for i in range(6):
    kit.pigeon(KP, rng.uniform(-3, 3), rng.uniform(-9, -6), 0.0)
KP.finish(SET, NIGHT, NIGHT)
print('props %.1fs' % (time.time() - T0))

# ==============================================================================================
# Marks
# ==============================================================================================
MK = C['marks']
HERO = Vector((0.9, -3.0, 0))
RIVAL = Vector((3.3, -1.4, 0))
mk = {}


def mark(name, p, facing):
    mk[name] = look.mark(MK, '%s_%s' % (CODE, name), V(*p), facing)


mark('MARK_HERO', HERO, look.face_towards(HERO, RIVAL) - 75)
mark('MARK_RIVAL', RIVAL, look.face_towards(RIVAL, HERO) + 55)
mark('MARK_SIBLING', (-0.4, -3.9, 0), look.face_towards((-0.4, -3.9), RIVAL) - 30)
mark('MARK_RULER', (0.0, KEEP_Y0 - 0.45, LAND_Z), 0.0)
crowd_c = Vector((2.1, -2.2, 0))
for i, p in enumerate(((-4.0, 0.2), (-3.4, -1.6), (5.0, 0.9), (6.2, -1.0), (6.6, -3.2), (-4.2, 2.2), (4.6, 2.6), (-2.6, -6.4))):
    mark('MARK_CROWD_%d' % (i + 1), (p[0], p[1], 0), look.face_towards(p, crowd_c))
mark('MARK_GIANT', (9.0, 9.5, 0), look.face_towards((9.0, 9.5), HERO))
mark('MARK_GUARD_1', (-2.7, YS + 0.6, 0), 180.0)
mark('MARK_GUARD_2', (2.7, YS + 0.6, 0), 180.0)
mark('MARK_GUARD_3', (-1.7, KEEP_Y0 - 0.3, LAND_Z), 0.0)
mark('MARK_GUARD_4', (1.7, KEEP_Y0 - 0.3, LAND_Z), 0.0)

# ==============================================================================================
# Cameras
# ==============================================================================================
CM = C['cams']
cams = {}


def cam(name, pos, tgt, lens, note):
    cams[name] = look.camera(CM, '%s_%s' % (CODE, name), V(*pos), V(*tgt), lens, note)


cam('WIDE_ESTABLISH', (2.2, YS + 1.6, 6.0), (-1.3, 10.0, 7.0), 18, 'from inside the gate: courtyard, well, stair up to the keep with banners and turrets; room for a crowd')
cam('LOW_HERO', (1.8, -5.7, 0.32), (0.75, -2.6, 1.45), 20, 'knee-height looking up at MARK_HERO; stair, keep and banners behind')
cam('CROWD_MED', (9.2, -7.4, 2.4), (1.6, -1.6, 1.2), 28, 'crowd + hero + rival from the training-yard side; well, stable and west wall behind')
cam('TWO_SHOT', (1.6, -7.4, 1.2), (2.1, -2.2, 1.15), 35, 'hero (left) and rival (right) facing off, braziers and stair behind')
cam('CLOSE_A', (2.15, -4.15, 1.08), (0.9, -3.0, 1.06), 50, 'hero face (head ~1.0 m)')
cam('CLOSE_B', (2.1, -2.85, 1.66), (3.3, -1.4, 1.68), 50, 'rival face (Rich kid head ~1.6 m)')
cam('INSERT_WELL', (-8.8, 0.6, 1.6), (WELL[0], WELL[1], 1.2), 30, 'the well with its shingle roof and bucket barrel; stair and keep behind')
cam('INSERT_GATE', (1.4, -4.6, 1.6), (0.0, YS - 1.0, 3.2), 24, 'gatehouse from the courtyard: open gates, raised portcullis, banners, torches')
cam('WIDE_REVERSE', (2.2, KEEP_Y0 - 0.8, LAND_Z + 1.9), (0.0, YS - 3.0, 1.5), 20, 'from the keep landing over the courtyard to the gate (ruler POV)')

# ==============================================================================================
# Lights
# ==============================================================================================
worlds = {}
sun_day = look.sun_obj(C['DAY'], 'DAY', 28.0, '%s Sun DAY' % CODE)
worlds['DAY'] = look.world_sky(sc, 'DAY', '%s Sky DAY' % CODE, look.sun_direction(sun_day))
sun_g = look.sun_obj(C['GOLDEN'], 'GOLDEN', -24.0, '%s Sun GOLDEN' % CODE, 4.6, 16.0)
worlds['GOLDEN'] = look.world_sky(sc, 'GOLDEN', '%s Sky GOLDEN' % CODE, look.sun_direction(sun_g))
moon = look.sun_obj(C['NIGHT'], 'NIGHT', -36.0, '%s Moon' % CODE)
worlds['NIGHT'] = look.world_sky(sc, 'NIGHT', '%s Sky NIGHT' % CODE, look.sun_direction(moon))
look.area(C['NIGHT'], '%s moon fill' % CODE, V(-10, -40, 28), (math.radians(55), 0, math.radians(-15)), 30, 70, '#7f9cff')
look.point(C['NIGHT'], '%s gate fill' % CODE, V(0.0, YS + 2.0, 3.2), 240, '#ff9440', 0.3)

scenes = setbase.finish(sc, master, C, TITLE, CODE, cams['WIDE_ESTABLISH'], worlds,
                        os.path.join(setbase.OUT, 'castle_courtyard', 'castle_courtyard.blend'))
print('saved %.1fs' % (time.time() - T0))
