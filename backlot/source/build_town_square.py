"""Backlot set 1: TOWN SQUARE.  python3 -I build_town_square.py  ->  town_square/town_square.blend"""
import sys, os, math, time, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, '..', 'materials')]
import bpy
from mathutils import Vector, Matrix
import mats, geo, look, kit, setbase

T0 = time.time()
M = geo.M
PI = math.pi
CODE, TITLE = 'TS', 'Town Square'
sc, master, C = setbase.start(CODE, TITLE)
SET, NIGHT = C['set'], C['NIGHT']
mats.set_global(wet=0.45)


def V(x, y, z=0.0):
    return Vector((x * M, y * M, z * M))


# ==============================================================================================
# Town hall (hero building at the head of the square)
# ==============================================================================================
def town_hall(K):
    b = K.b
    W, D = 15.0, 11.0
    hw = W / 2
    zf = 0.45                 # podium / arcade floor
    zg = 4.6                  # ground storey top
    zu = 8.9                  # eaves
    # podium + steps
    for i, (y0, z1) in enumerate(((-1.5, 0.15), (-1.0, 0.3), (-0.5, zf))):
        b.box(-hw + 0.6, y0, -0.05, hw - 0.6, 0.05, z1, 'Limestone', 0.02)
    b.box(-hw, -0.02, -0.05, hw, 0.3, zf, 'Ashlar Grey', 0.02)
    b.grid(6, 2, lambda s, t: (-hw + 0.5 + s * (W - 1.0), 0.6 + t * 3.0, zf), 'Flagstones Hall', (W - 1.0, 3.0), smooth=False)
    # arcade front wall
    arches = [(cx, 2.5, 2.75, 'round', None) for cx in (-4.95, -1.65, 1.65, 4.95)]
    kit.arch_wall(b, -hw, hw, zf, zg, arches, 'Ashlar', 0.0, 0.6, 'Ashlar', 'Limestone', 0.4, 0.05)
    with K.push((0, 0.6, 0), PI):
        kit.arch_wall(b, -hw, hw, zf, zg, [(-cx, w, s, k, r) for cx, w, s, k, r in arches], 'Ashlar', 0.0, 0.0)
    b.box(-hw, -0.02, 0.3, hw, 0.62, zf, 'Ashlar Grey', 0.02)
    # impost blocks and pier bases
    for cx in (-6.6, -3.3, 0.0, 3.3, 6.6):
        b.box(cx - 0.55, -0.1, 2.6, cx + 0.55, 0.7, 2.78, 'Limestone', 0.02)
        b.box(cx - 0.5, -0.08, zf, cx + 0.5, 0.68, zf + 0.35, 'Limestone', 0.02)
    # string course
    b.box(-hw - 0.08, -0.16, zg, hw + 0.08, 0.3, zg + 0.22, 'Limestone', 0.03)
    # arcade ceiling with beams
    b.quad((-hw, 3.6, zg), (hw, 3.6, zg), (hw, 0.6, zg), (-hw, 0.6, zg), 'Planks Grey')
    for i in range(16):
        x = -hw + 0.45 + i * (W - 0.9) / 15
        b.box(x - 0.1, 0.6, zg - 0.25, x + 0.1, 3.6, zg, 'Timber Dark', 0.02)
    # inner wall with the great door and windows
    holes = [(-1.1, 1.1, zf, zf + 3.2), (-5.4, -4.4, zf + 0.9, zf + 2.9), (4.4, 5.4, zf + 0.9, zf + 2.9),
             (-2.9, -2.1, zf + 0.9, zf + 2.9), (2.1, 2.9, zf + 0.9, zf + 2.9)]
    with K.push((0, 3.6, 0)):
        b.wall(-hw, hw, zf, zg, 'Plaster White', holes, 0.0, 0.3, 'Limestone')
        for sx in (-1, 1):
            b.box(sx * 0.55 - 0.55, 0.18, zf, sx * 0.55 + 0.55, 0.26, zf + 3.2, 'Paint Red', 0.01)
            for hz in (zf + 0.5, zf + 2.6):
                b.box(sx * 0.55 - 0.5, 0.165, hz, sx * 0.55 + 0.45, 0.18, hz + 0.07, 'Iron Black', 0.004)
            b.torus((sx * 0.18, 0.15, zf + 1.3), 0.09, 0.014, 'Brass', 14, 5, 'Y')
        b.box(-1.35, -0.06, zf, -1.1, 0.05, zf + 3.4, 'Limestone', 0.02)
        b.box(1.1, -0.06, zf, 1.35, 0.05, zf + 3.4, 'Limestone', 0.02)
        b.box(-1.45, -0.08, zf + 3.2, 1.45, 0.05, zf + 3.6, 'Limestone', 0.02)
        for hx0, hx1, hz0, hz1 in holes[1:]:
            kit.window(K, (hx0 + hx1) / 2, hz0, hx1 - hx0, hz1 - hz0, 0.0, 0.3, sill='Limestone', lit=True)
        for x in (-6.6, 6.6):
            kit.wall_lantern(K, x, 0.0, 3.4, 0.45)
    # side + back walls of the ground storey
    b.quad((-hw, 0.6, zf), (-hw, 3.6, zf), (-hw, 3.6, zg), (-hw, 0.6, zg), 'Ashlar')
    b.quad((hw, 3.6, zf), (hw, 0.6, zf), (hw, 0.6, zg), (hw, 3.6, zg), 'Ashlar')
    with K.push((-hw, D, 0), -PI / 2):
        b.wall(0, D, 0, zg, 'Ashlar', [], 0.0)
    with K.push((hw, 0, 0), PI / 2):
        b.wall(0, D, 0, zg, 'Ashlar', [], 0.0)
    with K.push((hw, D, 0), PI):
        b.wall(0, W, 0, zu, 'Ashlar', [], 0.0)
    # upper storey: front with tall windows and the balcony door
    wins = [(-5.6, 1.1, 2.4, zg + 0.95), (-2.8, 1.1, 2.4, zg + 0.95), (2.8, 1.1, 2.4, zg + 0.95), (5.6, 1.1, 2.4, zg + 0.95),
            (0.0, 1.35, 2.9, zg + 0.3)]
    holes = [(x - w / 2, x + w / 2, z, z + h) for x, w, h, z in wins]
    b.wall(-hw, hw, zg + 0.22, zu, 'Ashlar', [(h0, h1, max(z0, zg + 0.22), z1) for h0, h1, z0, z1 in holes], 0.0, 0.38, 'Limestone')
    for x, w, h, z in wins:
        kit.window(K, x, z, w, h, 0.0, 0.38, sill='Limestone' if x else None, lit=True, frame='Timber Dark')
        b.box(x - w / 2 - 0.2, -0.06, z, x - w / 2, 0.02, z + h, 'Limestone', 0.015)
        b.box(x + w / 2, -0.06, z, x + w / 2 + 0.2, 0.02, z + h, 'Limestone', 0.015)
        # pediment lintel
        b.box(x - w / 2 - 0.3, -0.12, z + h, x + w / 2 + 0.3, 0.02, z + h + 0.22, 'Limestone', 0.02)
        b.prism([(x - w / 2 - 0.3, z + h + 0.22), (x + w / 2 + 0.3, z + h + 0.22), (x, z + h + 0.62)], -0.1, 0.0, 'Limestone')
    for sx in (-1, 1):
        kit.quoins(K, sx * hw, 0.0, zg + 0.22, zu, sx)
    # cornice
    b.box(-hw - 0.2, -0.32, zu - 0.25, hw + 0.2, 0.3, zu, 'Limestone', 0.03)
    for i in range(30):
        x = -hw + 0.25 + i * (W - 0.5) / 29
        b.box(x - 0.08, -0.22, zu - 0.45, x + 0.08, 0.0, zu - 0.25, 'Limestone', 0.01)
    # balcony on corbels with balusters
    bz = zg + 0.3
    b.box(-1.9, -1.35, bz - 0.25, 1.9, 0.0, bz, 'Limestone', 0.03)
    for x in (-1.5, 0.0, 1.5):
        b.box(x - 0.18, -1.0, bz - 0.85, x + 0.18, 0.0, bz - 0.25, 'Limestone', 0.02)
        b.box(x - 0.14, -0.6, bz - 1.25, x + 0.14, 0.0, bz - 0.85, 'Limestone', 0.02)
    bal = [(-1.85, -1.3), (1.85, -1.3)]
    n = 13
    for i in range(n):
        x = -1.7 + 3.4 * i / (n - 1)
        b.lathe([(0.07, bz), (0.07, bz + 0.08), (0.05, bz + 0.15), (0.09, bz + 0.45), (0.05, bz + 0.75), (0.07, bz + 0.82), (0.07, bz + 0.9)],
                'Limestone', 10, (x, -1.2, 0))
    for sx in (-1, 1):
        for i in range(4):
            y = -1.2 + i * 0.32
            b.lathe([(0.07, bz), (0.07, bz + 0.08), (0.05, bz + 0.15), (0.09, bz + 0.45), (0.05, bz + 0.75), (0.07, bz + 0.82), (0.07, bz + 0.9)],
                    'Limestone', 10, (sx * 1.75, y, 0))
    b.box(-1.9, -1.32, bz + 0.9, 1.9, -1.08, bz + 1.02, 'Limestone', 0.02)
    for sx in (-1, 1):
        b.box(sx * 1.75 - 0.12, -1.32, bz + 0.9, sx * 1.75 + 0.12, 0.0, bz + 1.02, 'Limestone', 0.02)
    # banners on the facade
    for x, d in ((-4.2, 'crown'), (-1.45, 'sun'), (1.45, 'sun'), (4.2, 'crown')):
        kit.flat_banner(K, x, -0.02, zu - 0.55, d, length=2.55, width=0.9)
    # roof (ridge along X) with dormers
    with K.push((0, 0, 0), -PI / 2):
        rz_top, zr = kit.gable_roof(K, -D, 0.0, -hw - 0.45, hw + 0.45, zu, 50, 'Roof Slate', 0.55, 0.03, 0.16, nu=12)
        rh = rz_top - zu
        kit.gable_wall(K, -D, 0.0, zu, rh, -hw, 'Ashlar')
        with K.push((0, hw, 0), PI):
            kit.gable_wall(K, 0.0, D, zu, rh, 0.0, 'Ashlar')
    for x in (-4.2, 4.2):
        kit.dormer(K, x, 0.0, zu, 50, 'Roof Slate', 'Ashlar', 'Timber Dark', True)
    # roof crest: iron cresting along the ridge
    for i in range(24):
        x = -hw + 0.3 + i * (W - 0.6) / 23
        b.cyl((x, D / 2, rz_top + 0.1), (x, D / 2, rz_top + 0.5), 0.015, 'Iron Black', 5)
        b.sphere((x, D / 2, rz_top + 0.52), 0.035, 'Gold', 6, 4)
    # notices pinned on the left end pier
    rng = K.rng
    for i in range(6):
        px = -7.05 + rng.uniform(-0.2, 0.2)
        pz = zf + 0.9 + i * 0.28 + rng.uniform(-0.05, 0.05)
        with K.push((px + (i % 2) * 0.3 - 0.15, -0.012, pz), ry=rng.uniform(-0.15, 0.15)):
            w_, h_ = rng.uniform(0.22, 0.32), rng.uniform(0.28, 0.38)
            b.quad((-w_ / 2, 0, -h_ / 2), (w_ / 2, 0, -h_ / 2), (w_ / 2, 0, h_ / 2), (-w_ / 2, 0, h_ / 2), 'Parchment')
            b.sphere((0, -0.005, h_ / 2 - 0.03), 0.012, 'Iron Black', 5, 3)
    return rz_top


def clock_tower(K, h=20.5):
    b = K.b
    s = 4.4
    hs = s / 2
    holes_by_level = {}
    levels = [0.0, 4.6, 8.9, 13.0, 17.2, h]
    for li, (z0, z1) in enumerate(zip(levels, levels[1:])):
        for face in range(4):
            with K.push((0, 0, 0), face * PI / 2):
                with K.push((-hs, -hs, 0)):
                    if li == 4:
                        kit.arch_wall(b, 0, s, z0, z1, [(hs, 1.7, z0 + 1.2, 'round', None)], 'Ashlar', 0.0, 0.5, 'Ashlar', 'Limestone', 0.3, 0.04)
                        b.box(hs - 1.0, 0.0, z0, hs + 1.0, 0.5, z0 + 0.9, 'Ashlar', 0.02)
                        for k in range(5):
                            b.lathe([(0.06, z0 + 0.9), (0.08, z0 + 1.0), (0.05, z0 + 1.3), (0.06, z0 + 1.5)], 'Limestone', 8, (hs - 0.7 + k * 0.35, 0.1, 0))
                    elif li in (1, 2):
                        b.wall(0, s, z0, z1, 'Ashlar', [(hs - 0.35, hs + 0.35, z0 + 1.6, z0 + 3.0)], 0.0, 0.45, 'Limestone')
                        kit.window(K, hs, z0 + 1.6, 0.7, 1.4, 0.0, 0.45, sill='Limestone', lit=(li == 1 and face == 0), mullion=False)
                    elif li == 0 and face == 0:
                        b.wall(0, s, z0, z1, 'Ashlar', [(hs - 0.6, hs + 0.6, 0.12, 2.5)], 0.0, 0.45, 'Limestone')
                        kit.door(K, hs, 1.2, 2.38, 0.0, 0.45, 'Planks', 0.12, surround='Limestone')
                    else:
                        b.wall(0, s, z0, z1, 'Ashlar', [], 0.0)
                    b.box(-0.08, -0.14, z1 - 0.2, s + 0.08, 0.2, z1, 'Limestone', 0.02)
    for face in range(4):
        with K.push((0, 0, 0), face * PI / 2):
            kit.quoins(K, hs, -hs, 0.0, h, 1)
    # clock faces (front and right side)
    for face in (0, 1):
        with K.push((0, 0, 0), face * PI / 2):
            cz = 15.0
            y = -hs - 0.06
            b.cyl((0, y + 0.06, cz), (0, y - 0.02, cz), 1.35, 'Limestone', 32)
            b.cyl((0, y - 0.02, cz), (0, y - 0.05, cz), 1.15, 'Marble White', 32)
            b.torus((0, y - 0.06, cz), 1.2, 0.04, 'Gold', 40, 6, 'Y')
            for k in range(12):
                a = 2 * PI * k / 12
                L = 0.22 if k % 3 == 0 else 0.13
                c = Vector((math.sin(a) * (1.0 - L / 2), y - 0.07, cz + math.cos(a) * (1.0 - L / 2)))
                b.cbox(c, (0.06, 0.02, L), 'Iron Black', rot=(0, a, 0))
            for ang, L, wdt in ((math.radians(305), 0.55, 0.08), (math.radians(60), 0.85, 0.05)):
                c = Vector((math.sin(ang) * L / 2, y - 0.1, cz + math.cos(ang) * L / 2))
                b.cbox(c, (wdt, 0.025, L), 'Iron Black', 0.005, rot=(0, ang, 0))
            b.cyl((0, y - 0.06, cz), (0, y - 0.13, cz), 0.07, 'Gold', 12)
    # bell
    b.lathe([(0.0, h - 2.2), (0.35, h - 2.15), (0.45, h - 2.0), (0.55, h - 1.4), (0.75, h - 0.6), (0.85, h - 0.5)], 'Brass', 20,
            cap_top=False, cap_bot=False)
    b.box(-1.6, -0.15, h - 0.5, 1.6, 0.15, h - 0.25, 'Timber Dark', 0.02)
    # floor of the belfry seen through the arches
    b.quad((-hs, -hs, 17.2 + 0.9), (hs, -hs, 17.2 + 0.9), (hs, hs, 17.2 + 0.9), (-hs, hs, 17.2 + 0.9), 'Planks Grey')
    # cornice + spire
    b.box(-hs - 0.3, -hs - 0.3, h, hs + 0.3, hs + 0.3, h + 0.35, 'Limestone', 0.04)
    r = (s + 0.7) / math.sqrt(2)
    b.lathe([(r, h + 0.3), (r * 0.82, h + 0.9), (r * 0.18, h + 6.6), (0.0, h + 7.3)], 'Roof Slate', 4, phase=PI / 4, cap_top=False)
    b.lathe([(0.12, h + 7.2), (0.06, h + 8.4)], 'Gold', 8)
    b.sphere((0, 0, h + 7.6), 0.22, 'Gold', 12, 8)
    # weathervane rooster-ish pennant
    b.prism([(0.0, h + 8.2), (0.9, h + 8.05), (0.0, h + 7.85)], -0.01, 0.01, 'Gold')
    # banner pole
    return h + 8.4


# ==============================================================================================
# Layout
# ==============================================================================================
rng = random.Random(42)
PLASTERS = ['Plaster Cream', 'Plaster Ochre', 'Plaster Rose', 'Plaster White', 'Plaster Sage', 'Plaster Blue']
ROOFS = ['Roof Clay', 'Roof Clay', 'Roof Clay Old', 'Roof Slate', 'Roof Shingle']
PAINTS = ['Paint Green', 'Paint Red', 'Paint Blue', 'Paint Yellow']
SIGNS = ['mug', 'loaf', 'boot', 'key', 'potion', 'horseshoe', 'sword']


def house_params(W, i, **over):
    r = random.Random(1000 + i)
    floors = r.choice([[3.2, 2.8, 2.6], [3.3, 2.8], [3.1, 2.7, 2.6], [3.4, 2.9, 2.7]])
    nwin = 2 if W < 4.5 else 3
    xs = [(-W / 2 + (k + 0.5) * W / nwin) for k in range(nwin)]
    p = dict(W=W, D=r.uniform(7.5, 9.5), floors=floors, jetty=r.choice([0.3, 0.4, 0.5]),
             ground=r.choice(['stone', 'stone', 'timber', 'shop']), stone=r.choice(['Rubble', 'Ashlar', 'Rubble']),
             plaster=PLASTERS[i % len(PLASTERS)], timber=r.choice(['Timber Dark', 'Timber Dark', 'Timber Oak']),
             style=r.choice(['panels', 'braced', 'studs', 'panels']), roof=r.choice(['gable', 'gable', 'eaves']),
             roof_mat=ROOFS[(i * 3) % len(ROOFS)], pitch=r.uniform(48, 56),
             win=[[]] + [xs for _ in floors[1:]], door_x=-W / 2 + 0.9, door_paint=PAINTS[(i + 1) % 4],
             shutters=PAINTS[i % 4], gwin=[xs[-1]] if W > 4.2 else [], shop_x=W * 0.15, shop_w=min(2.0, W - 2.3),
             goods=r.choice(['bread', 'fruit', 'cloth', 'pots']), win_w=0.78, sides=None, lit=0.55)
    if p['ground'] == 'shop':
        p['gwin'] = []
    p['dormer'] = p['roof'] == 'eaves'
    p['chimney_x'] = r.uniform(-W * 0.25, W * 0.25)
    p.update(over)
    return p


# rows: (origin of the row, rotation, list of widths); the house is centred on its slot
rows = [
    ('N', (-16.0, 14.0), 0.0, [4.4, 4.1]),                  # north row west of the town hall (front at y=14)
    ('N2', (11.5, 14.0), 0.0, [4.5]),                       # north row east of the tower
    ('W', (-16.0, -11.0), PI / 2, [4.8, 4.0, 5.2, 4.2, 3.3]),  # west row (front at x=-16, faces +X)
    ('E', (16.0, 14.0), -PI / 2, [5.0, 4.4, 4.8, 4.3, 4.5]),   # east row (front at x=16, faces -X)
    ('S1', (-3.0, -14.0), PI, [4.5, 4.0, 4.5]),              # south row (faces +Y), west part
    ('S2', (16.0, -14.0), PI, [4.4, 4.6, 4.0]),              # south row, east part
]
extras = {
    ('W', 1): dict(sign='loaf', ground='shop', goods='bread', banner=None),
    ('W', 3): dict(sign='potion', lantern_x=-1.0),
    ('E', 1): dict(sign='mug', lantern_x=0.4, ground='stone', roof='eaves', dormer=True, floors=[3.4, 2.9, 2.7]),
    ('E', 3): dict(sign='horseshoe', ground='shop', goods='pots'),
    ('N', 0): dict(sides='left', lantern_x=0.8),
    ('N', 1): dict(sign='key'),
    ('N2', 0): dict(sign='sword', sides='right'),
    ('W', 4): dict(sides='right'),
    ('S1', 1): dict(sign='boot'),
    ('E', 0): dict(sides='right'),
}
idx = 0
houses = []
SIGNS_AT = {}
for code, (ox, oy), rz, widths in rows:
    pos = 0.0
    for k, W in enumerate(widths):
        c = pos + W / 2
        # along the row direction: local +X of the row frame
        d = Vector((math.cos(rz), math.sin(rz), 0))
        loc = Vector((ox, oy, 0)) + d * c
        P = house_params(W, idx, **extras.get((code, k), {}))
        if code == 'E' and k == 0:
            P['D'] = 7.5
        K = kit.Kit('%s House %s%d' % (CODE, code, k + 1), 100 + idx)
        kit.townhouse(K, P)
        K.finish(SET, NIGHT, NIGHT, loc=tuple(loc), rz=rz)
        houses.append((code, k, loc, rz, P))
        for icon, lp, ln in getattr(K, 'signs', []):
            R = Matrix.Rotation(rz, 3, 'Z')
            SIGNS_AT[icon] = (Vector(loc) + R @ lp, R @ ln)
        pos += W
        idx += 1
print('houses %.1fs' % (time.time() - T0))

# town hall + clock tower (front at y = 14)
KH = kit.Kit('%s Town Hall' % CODE, 7)
hall_ridge = town_hall(KH)
KH.finish(SET, NIGHT, NIGHT, loc=(-0.5, 14.0, 0.0))
KT = kit.Kit('%s Clock Tower' % CODE, 8)
tower_top = clock_tower(KT)
KT.finish(SET, NIGHT, NIGHT, loc=(9.2, 16.4, 0.0))
print('hall %.1fs' % (time.time() - T0))

# background roofs (lower detail) and distant castle on a hill
for i in range(7):
    r = random.Random(500 + i)
    W = r.uniform(4.5, 7.0)
    P = house_params(W, 50 + i, ground='timber', flowers=False, lit=0.4, sign=None, lantern_x=None)
    P['floors'] = r.choice([[3.2, 2.8, 2.6], [3.3, 2.9, 2.7, 2.5]])
    K = kit.Kit('%s Backdrop %d' % (CODE, i + 1), 300 + i)
    kit.townhouse(K, P)
    K.finish(SET, NIGHT, NIGHT, loc=(-24 + i * 8.0 + r.uniform(-1, 1), 30 + r.uniform(-2, 4), 0), rz=r.uniform(-0.3, 0.3))
KC = kit.Kit('%s Castle Swanveil' % CODE, 9)
setbase.old_model(KC, 'towers-of-the-marches/v001/models/Swanveil.blend', {'Chalk': 'Limestone', 'Wisteria': 'Paint Blue'})
KC.finish(SET, NIGHT, NIGHT, loc=(34.0, 170.0, 24.0), rz=math.radians(200))
hill = geo.Builder('%s Hill' % CODE)


def hill_fn(s, t):
    x = -220 + 440 * s
    y = 60 + 260 * t
    h = 26 * math.exp(-((x - 34) / 70) ** 2 - ((y - 170) / 60) ** 2) + 9 * math.sin(x / 37) * math.sin(y / 29) + 6 * t
    return (x, y, h - 2)


hill.grid(40, 24, hill_fn, 'Grass', (440, 260), smooth=True)
hill.finish(SET)
print('backdrop %.1fs' % (time.time() - T0))

# ==============================================================================================
# Ground: cobbles everywhere (displaced), drain channel, flagstone apron at the hall
# ==============================================================================================
gnd = geo.Builder('%s Cobbles' % CODE)
gnd.grid(30, 30, lambda s, t: (-45 + 90 * s, -45 + 100 * t, 0.0), 'Cobbles', (90, 100), smooth=False)
gnd.finish(SET, dicing=1.0)
grass = geo.Builder('%s Fields' % CODE)
grass.grid(4, 4, lambda s, t: (-260 + 520 * s, -260 + 330 * t, -0.08), 'Grass', (520, 330), smooth=False)
grass.finish(SET)

# ==============================================================================================
# Props
# ==============================================================================================
KP = kit.Kit('%s Props' % CODE, 77)
FOUNT = (-5.5, -1.0)
kit.fountain(KP, FOUNT[0], FOUNT[1], 3.0)
stalls = [(-12.2, -7.2, 'Canvas Red', ('fruit', 'bread')), (-12.2, -3.0, 'Canvas Blue', ('cloth',)),
          (-12.2, 1.4, 'Canvas Green', ('fruit',)), (-12.2, 5.8, 'Canvas Yellow', ('bread', 'pots'))]
for x, y, cv, gd in stalls:
    kit.stall(KP, x, y, PI / 2 + rng.uniform(-0.05, 0.05), cv, gd)
for x, y in ((-12.8, -9.6), (-13.2, 3.6), (12.6, 4.2), (13.1, 3.5), (12.4, 9.8)):
    kit.barrel(KP, x, y, 0.0, rng.uniform(0.26, 0.31), rng.uniform(0.78, 0.9))
for x, y in ((-13.0, -5.1), (-12.6, -0.6), (13.0, 5.2), (12.8, -8.0), (13.4, -7.4)):
    kit.crate(KP, x, y, 0.0)
kit.crate(KP, 13.4, -7.4, 0.45, (0.5, 0.4, 0.35))
kit.crate_of(KP, -13.4, 8.4, 0.0, 'Pumpkin', (0.7, 0.5, 0.3))
for x, y in ((-13.0, 9.5), (-12.4, 9.2), (-12.8, 10.0)):
    kit.pumpkin(KP, x, y, 0.0, rng.uniform(0.16, 0.24))
kit.cart(KP, 12.2, -3.5, PI / 2 + 0.25, 'hay')
kit.cart(KP, -13.4, 11.9, 0.25, 'barrels')
kit.hay_bale(KP, 13.3, -0.2, 0.0, 1.4)
kit.hay_bale(KP, 13.6, -1.1, 0.0, 1.6)
kit.hay_bale(KP, 13.4, -0.6, 0.4, 1.5)
kit.hay_pile(KP, 14.2, 1.3, 0.0, 0.7, 0.45)
for x, y in ((-1.2, -6.8), (5.4, -2.2), (-6.2, 8.4), (6.6, 10.2), (-2.4, 9.4)):
    kit.lamp_post(KP, x, y, 3.3)
for i in range(9):
    a = rng.uniform(0, 2 * PI)
    rr = rng.uniform(3.9, 5.4)
    kit.pigeon(KP, FOUNT[0] + rr * math.cos(a), FOUNT[1] + rr * math.sin(a), 0.0)
for i in range(3):
    kit.pigeon(KP, -2.0 + i * 0.4, 12.6 + rng.uniform(-0.1, 0.1), 0.15)
# laundry across the north-west and south-west alleys
kit.laundry_line(KP, (-17.2, 10.55, 6.2), (-17.6, 14.05, 6.0))
kit.laundry_line(KP, (-19.5, 10.55, 5.6), (-20.0, 14.05, 5.5), 0.25)
kit.laundry_line(KP, (-17.5, -11.05, 6.0), (-18.0, -13.95, 5.9), 0.25)
KP.finish(SET, NIGHT, NIGHT)

# ranking board (blank plaques as separate objects + text anchors)
KR = kit.Kit('%s Ranking Board' % CODE, 21)
items = kit.ranking_board(KR, 0, 0, 0, 10)
RB_LOC, RB_RZ = (-8.8, 10.3), math.radians(22)
rb_parent, _ = KR.finish(SET, NIGHT, NIGHT, loc=(RB_LOC[0], RB_LOC[1], 0), rz=RB_RZ)
kit.plaque_objects(SET, rb_parent, CODE, items)
print('props %.1fs' % (time.time() - T0))

# ==============================================================================================
# Marks
# ==============================================================================================
MK = C['marks']
HERO = Vector((1.0, 3.0, 0))
RIVAL = Vector((3.4, 4.6, 0))
mk = {}


def mark(name, p, facing):
    mk[name] = look.mark(MK, '%s_%s' % (CODE, name), V(*p), facing)


yaw_h = look.face_towards(HERO, RIVAL) - 75      # 3/4 cheat towards camera
yaw_r = look.face_towards(RIVAL, HERO) + 55
mark('MARK_HERO', HERO, yaw_h)
mark('MARK_RIVAL', RIVAL, yaw_r)
mark('MARK_SIBLING', (-0.2, 2.1, 0), look.face_towards((-0.2, 2.1), RIVAL) - 30)
mark('MARK_RULER', (-0.5, 13.05, 4.9), 0.0)
crowd_c = Vector((2.2, 4.0, 0))
for i in range(8):
    a = math.radians(28 + i * 18)
    rr = 5.2 + (i % 2) * 1.3
    p = crowd_c + Vector((rr * math.cos(a), rr * math.sin(a), 0))
    mark('MARK_CROWD_%d' % (i + 1), p, look.face_towards(p, crowd_c))
mark('MARK_GIANT', (9.5, 6.5, 0), look.face_towards((9.5, 6.5), HERO))
for name, p, f in (('MARK_GUARD_1', (-2.2, 12.2, 0.45), 0.0), ('MARK_GUARD_2', (1.2, 12.2, 0.45), 0.0)):
    mark(name, p, f)

# ==============================================================================================
# Cameras (9:16).  look.camera takes BU.
# ==============================================================================================
CM = C['cams']
cams = {}


def cam(name, pos, tgt, lens, note):
    cams[name] = look.camera(CM, '%s_%s' % (CODE, name), V(*pos), V(*tgt), lens, note)


cam('WIDE_ESTABLISH', (1.2, -12.6, 5.4), (-0.5, 8.0, 6.6), 18, 'whole square from the south street: town hall, clock tower, fountain, stalls; room for a crowd')
cam('LOW_HERO', (1.9, 0.3, 0.32), (0.85, 3.4, 1.45), 20, 'knee-height looking up at MARK_HERO; town hall + clock tower behind')
cam('CROWD_MED', (8.6, -4.2, 2.1), (1.5, 6.5, 1.3), 35, 'crowd arc + hero + rival, town hall behind')
cam('TWO_SHOT', (1.7, -1.4, 1.2), (2.2, 3.8, 1.1), 35, 'hero (left) and rival (right) facing off, fountain far left')
cam('CLOSE_A', (2.25, 1.85, 1.08), (1.0, 3.0, 1.06), 50, 'hero face (head ~1.0 m), over the rival side')
cam('CLOSE_B', (2.2, 3.15, 1.66), (3.4, 4.6, 1.68), 50, 'rival face (Rich kid head ~1.6 m)')
rbc = Vector((RB_LOC[0], RB_LOC[1], 0))
fwd = Vector((math.sin(-RB_RZ), -math.cos(RB_RZ), 0))   # board's front direction (-Y local)
fwd = Vector((math.cos(RB_RZ - PI / 2), math.sin(RB_RZ - PI / 2), 0))
fwd = Vector((math.sin(RB_RZ), -math.cos(RB_RZ), 0))     # the board's front (-Y local)
cam('INSERT_RANKING', tuple(rbc + fwd * 5.0 + Vector((0, 0, 1.9))), tuple(rbc + Vector((0, 0, 2.15))), 35, 'ranking board, 10 blank plaques + header')
sp, sn = SIGNS_AT['key']
side = 1.0 if sn.x >= 0 else -1.0
sn = sn * side if (sn * side).y <= 0.3 else sn
cpos = sp + sn * 3.2 + Vector((0, -1.3, -0.9))
cam('INSERT_SIGN', tuple(cpos), tuple(sp), 45, 'locksmith sign (key) hanging on the north row, sunlit; other signs: ' + ', '.join(sorted(SIGNS_AT)))
print('signs', {k: tuple(round(c, 1) for c in v[0]) for k, v in SIGNS_AT.items()})
cam('INSERT_FOUNTAIN', (-1.6, -4.2, 1.1), (-5.5, -1.0, 1.6), 30, 'fountain water, pigeons, cobbles')
cam('WIDE_REVERSE', (-1.0, 12.4, 5.6), (1.0, -10.0, 1.0), 20, 'from the town hall balcony over the square to the south street')

# ==============================================================================================
# Lights
# ==============================================================================================
worlds = {}
sun_day = look.sun_obj(C['DAY'], 'DAY', 32.0, '%s Sun DAY' % CODE)
worlds['DAY'] = look.world_sky(sc, 'DAY', '%s Sky DAY' % CODE, look.sun_direction(sun_day))
sun_g = look.sun_obj(C['GOLDEN'], 'GOLDEN', -22.0, '%s Sun GOLDEN' % CODE, 4.6, 17.0)   # rakes across the hall and tower from the south-west
worlds['GOLDEN'] = look.world_sky(sc, 'GOLDEN', '%s Sky GOLDEN' % CODE, look.sun_direction(sun_g))
moon = look.sun_obj(C['NIGHT'], 'NIGHT', -38.0, '%s Moon' % CODE)
worlds['NIGHT'] = look.world_sky(sc, 'NIGHT', '%s Sky NIGHT' % CODE, look.sun_direction(moon))
# night: warm fill pools from braziers/torches near the hall + cool rim
look.point(C['NIGHT'], '%s torch fill hall L' % CODE, V(-3.2, 12.0, 3.0), 260, '#ff9440', 0.3)
look.point(C['NIGHT'], '%s torch fill hall R' % CODE, V(2.2, 12.0, 3.0), 260, '#ff9440', 0.3)
look.area(C['NIGHT'], '%s moon fill' % CODE, V(-10, -30, 25), (math.radians(55), 0, math.radians(-20)), 30, 60, '#7f9cff')

scenes = setbase.finish(sc, master, C, TITLE, CODE, cams['WIDE_ESTABLISH'], worlds,
                        os.path.join(setbase.OUT, 'town_square', 'town_square.blend'))
print('saved %.1fs' % (time.time() - T0))
