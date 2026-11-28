"""Backlot set 3: THRONE HALL.  python3 -I build_throne_hall.py -> throne_hall/throne_hall.blend
Layout (metres): hall runs along +Y from the doors (y=-17) to the throne dais (y=+11..17).
Outer walls x = +-9 (12 m to the vault springing), free-standing clustered pillars at x = +-5.2,
pointed nave vault apex 17.5 m, aisle vaults 14.5 m.  Polished marble floor at z = 0."""
import sys, os, math, time, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path[:0] = [HERE, os.path.join(HERE, '..', 'materials')]
import bpy
from mathutils import Vector, Matrix
import mats, geo, look, kit, setbase

T0 = time.time()
M = geo.M
PI = math.pi
CODE, TITLE = 'TH', 'Throne Hall'
sc, master, C = setbase.start(CODE, TITLE)
SET, NIGHT = C['set'], C['NIGHT']
mats.set_global(wet=0.0)
rng = random.Random(5)

XW = 9.0          # outer wall
XP = 5.2          # pillar line
Y0, Y1 = -17.0, 17.0
ZS = 12.0         # vault springing
PY = [-13.0, -8.5, -4.0, 0.5, 5.0, 9.5]     # pillar positions along Y
WIN_Y = [(a + b) / 2 for a, b in zip([-17.0] + PY, PY + [13.0])][1:]   # bays between pillars for windows
WIN_Y = [-10.75, -6.25, -1.75, 2.75, 7.25]


def V(x, y, z=0.0):
    return Vector((x * M, y * M, z * M))


def pointed_pts(x0, x1, spring, rise, n=16):
    """Two-centred pointed arch with a given rise; returns (x, z) left->right."""
    w = x1 - x0
    h = w / 2
    # radius so that the arcs meet at the apex at height rise: centre offset c from each springer
    R = (h * h + rise * rise) / (2 * h) if rise < h * 2 else w
    R = max(R, h)
    pts = []
    cxl = x0 + R
    for i in range(n // 2 + 1):
        t = i / (n // 2)
        a0 = PI
        a1 = math.atan2(rise, (x0 + h) - cxl)
        a = a0 + (a1 - a0) * t
        pts.append((cxl + R * math.cos(a), spring + R * math.sin(a)))
    cxr = x1 - R
    for i in range(1, n // 2 + 1):
        t = i / (n // 2)
        a0 = math.atan2(rise, (x0 + h) - cxr)
        a = a0 + (0.0 - a0) * t
        pts.append((cxr + R * math.cos(a), spring + R * math.sin(a)))
    return pts


def lancet_poly(cx, w, z0, spring):
    pts = kit.arch_pts(cx, w, spring, 'pointed', 12)
    return [(cx - w / 2, z0), (cx + w / 2, z0)] + pts[::-1]


# ==============================================================================================
# Structure
# ==============================================================================================
K = kit.Kit('%s Hall' % CODE, 2)
b = K.b

# floor (polished marble) - one big plane, the shader makes the checker tiles
b.grid(8, 16, lambda s, t: (-XW + 2 * XW * s, Y0 + (Y1 - Y0) * t, 0.0), 'Marble Floor', (2 * XW, Y1 - Y0), smooth=False)

# side walls with lancet windows (stained glass panes go to per-preset collections)
WIN_W, WIN_Z0, WIN_SP = 1.9, 3.4, 9.4
glass_panes = []        # (side, cy) for building per-preset glass
for side in (-1, 1):
    # frame: local x along the wall, normal pointing into the hall
    if side < 0:
        frame = ((-XW, Y0, 0), PI / 2)    # west wall faces +X; local x runs towards +Y
    else:
        frame = ((XW, Y1, 0), -PI / 2)    # east wall faces -X; local x runs towards -Y
    with K.push(*frame):
        L = Y1 - Y0
        loc = [(cy - Y0) if side < 0 else (Y1 - cy) for cy in WIN_Y]
        # lower wall + wainscot band
        b.wall(0, L, 0, WIN_Z0, 'Ashlar Hall', [], 0.0)
        # window zone with pointed openings
        ops = [(lx, WIN_W, WIN_SP, 'pointed', None) for lx in loc]
        kit.arch_wall(b, 0, L, WIN_Z0, ZS, ops, 'Ashlar Hall', 0.0, 0.9, 'Ashlar Hall', 'Limestone', 0.32, 0.06)
        for lx in loc:
            # sill
            b.box(lx - WIN_W / 2 - 0.15, -0.15, WIN_Z0 - 0.12, lx + WIN_W / 2 + 0.15, 0.9, WIN_Z0, 'Limestone', 0.02)
            # mullion
            b.box(lx - 0.06, 0.4, WIN_Z0, lx + 0.06, 0.55, WIN_SP + 1.2, 'Limestone', 0.015)
        # wainscot panelling
        b.box(0.0, -0.08, 0.0, L, 0.0, 2.6, 'Planks', 0.01)
        b.box(0.0, -0.14, 2.6, L, 0.0, 2.75, 'Timber Dark', 0.02)
        b.box(0.0, -0.12, 0.0, L, 0.0, 0.22, 'Timber Dark', 0.02)
        for k in range(int(L / 1.3)):
            b.box(k * 1.3 + 0.1, -0.11, 0.22, k * 1.3 + 0.18, -0.07, 2.6, 'Timber Dark', 0.008)
        # string course under the windows and at the springing
        b.box(0.0, -0.22, WIN_Z0 - 0.35, L, 0.0, WIN_Z0 - 0.12, 'Limestone', 0.03)
        b.box(0.0, -0.25, ZS - 0.3, L, 0.0, ZS, 'Limestone', 0.03)
    for cy in WIN_Y:
        glass_panes.append((side, cy))

# end walls: north (behind the throne) with a rose window, south with the great doors
ROSE_Z, ROSE_R = 11.6, 2.6


def end_wall_with_circle(y, normal_sign, cz, r, door=None):
    """End wall from x=-XW..XW, z 0..ZS+rise, with a circular hole (rose) and optional pointed door."""
    xs = [-XW, XW]
    n = 32
    top = ZS + 5.6
    circ = [(r * math.cos(PI / 2 + 2 * PI * i / n), cz + r * math.sin(PI / 2 + 2 * PI * i / n)) for i in range(n + 1)]
    # left half polygon (counter-clockwise seen from inside); built in a frame looking at the wall
    left = [(-XW, 0.0), (0.0, 0.0)] + [p for p in circ if p[0] <= 1e-6][::-1] + [(0.0, top), (-XW, top)]
    if door:
        dw, dsp = door
        dpts = kit.arch_pts(0.0, dw, dsp, 'pointed', 16)
        left = [(-XW, 0.0), (-dw / 2, 0.0)] + [p for p in dpts if p[0] <= 1e-6] + \
               [p for p in circ if p[0] <= 1e-6][::-1] + [(0.0, top), (-XW, top)]
    right = [(-x, z) for x, z in left][::-1]
    frame = ((0, y, 0), 0.0) if normal_sign > 0 else ((0, y, 0), PI)
    with K.push(*frame):
        for poly in (left, right):
            b.poly([(x, 0, z) for x, z in poly], 'Ashlar Hall')
        # reveal of the rose
        d = 0.9
        for (xa, za), (xb, zb) in zip(circ, circ[1:]):
            b.quad((xa, 0, za), (xa, d, za), (xb, d, zb), (xb, 0, zb), 'Ashlar Hall')
        b.torus((0, -0.05, cz), r + 0.18, 0.16, 'Limestone', 48, 8, 'Y')
        # tracery: spokes and an inner ring
        for i in range(12):
            a = 2 * PI * i / 12
            b.beam((0.35 * math.cos(a), 0.45, cz + 0.35 * math.sin(a)), ((r - 0.05) * math.cos(a), 0.45, cz + (r - 0.05) * math.sin(a)),
                   0.09, 0.14, 'Limestone', 0.01, up=(0, 1, 0))
        b.torus((0, 0.45, cz), 0.38, 0.08, 'Limestone', 24, 6, 'Y')
        b.torus((0, 0.45, cz), r * 0.62, 0.06, 'Limestone', 36, 6, 'Y')
        if door:
            dw, dsp = door
            dpts = kit.arch_pts(0.0, dw, dsp, 'pointed', 16)
            for (xa, za), (xb, zb) in zip(dpts, dpts[1:]):
                b.quad((xa, 0, za), (xa, 1.2, za), (xb, 1.2, zb), (xb, 0, zb), 'Ashlar Hall')
            b.quad((-dw / 2, 1.2, 0), (-dw / 2, 1.2, dsp), (-dw / 2, 0, dsp), (-dw / 2, 0, 0), 'Ashlar Hall')
            b.quad((dw / 2, 0, dsp), (dw / 2, 1.2, dsp), (dw / 2, 1.2, 0), (dw / 2, 0, 0), 'Ashlar Hall')
            # double doors (closed), iron studs and bands
            poly = [(-dw / 2, 0.0), (dw / 2, 0.0)] + dpts[::-1][1:-1]
            with K.push((0, 0.85, 0)):
                b.prism([(x, z) for x, z in [(-dw / 2 + 0.02, 0.0), (dw / 2 - 0.02, 0.0)] + [(x * 0.99, z - 0.02) for x, z in dpts[::-1][1:-1]]],
                        0.0, 0.18, 'Planks')
                for hz in (0.8, 2.6, 4.4, 6.0):
                    if hz < dsp + 0.5:
                        b.box(-dw / 2 + 0.05, -0.04, hz, dw / 2 - 0.05, 0.0, hz + 0.12, 'Iron Black', 0.01)
                b.box(-0.04, -0.05, 0.0, 0.04, 0.0, dsp + 1.2, 'Iron Black', 0.005)
                for sx in (-1, 1):
                    b.torus((sx * 0.45, -0.12, 2.4), 0.2, 0.03, 'Iron Black', 16, 6, 'Y')
                    for hz in (1.4, 3.4, 5.2):
                        for k in range(5):
                            b.sphere((sx * (0.4 + k * 0.4), -0.03, hz), 0.035, 'Iron Black', 6, 4)
    return circ


end_wall_with_circle(Y1, 1, ROSE_Z, ROSE_R)                        # north: normal -Y faces into the hall
end_wall_with_circle(Y0, -1, ROSE_Z - 0.4, 2.0, door=(4.2, 5.0))  # south: doors, normal +Y

# wainscot on the end walls
for y, sgn in ((Y1, -1), (Y0, 1)):
    with K.push((0, y, 0), 0.0 if sgn < 0 else PI):
        for xa, xb in ((-XW, -2.3), (2.3, XW)):
            b.box(xa, -0.08 * -1 if False else -0.08, 0.0, xb, 0.0, 2.6, 'Planks', 0.01)
            b.box(xa, -0.14, 2.6, xb, 0.0, 2.75, 'Timber Dark', 0.02)

# clustered pillars with bases and capitals
for side in (-1, 1):
    for py in PY:
        x = side * XP
        b.box(x - 0.85, py - 0.85, 0, x + 0.85, py + 0.85, 0.5, 'Marble Dark', 0.03)
        b.lathe([(0.82, 0.5), (0.82, 0.62), (0.7, 0.7), (0.75, 0.82), (0.62, 0.95), (0.58, 1.0)], 'Limestone', 24, (x, py, 0), cap_top=False)
        b.lathe([(0.58, 1.0), (0.55, 9.0)], 'Stone Drums', 24, (x, py, 0), cap_top=False)
        for k in range(4):
            a = PI / 4 + k * PI / 2
            b.cyl((x + 0.6 * math.cos(a), py + 0.6 * math.sin(a), 0.95), (x + 0.6 * math.cos(a), py + 0.6 * math.sin(a), 9.0), 0.17, 'Marble White', 10)
        b.lathe([(0.62, 9.0), (0.78, 9.4), (0.95, 9.75), (0.95, 9.9)], 'Limestone', 24, (x, py, 0), cap_top=False)
        b.box(x - 1.0, py - 1.0, 9.9, x + 1.0, py + 1.0, 10.2, 'Limestone', 0.03)
        # gold band and a ring of carved leaves on the capital
        b.lathe([(0.66, 8.75), (0.66, 8.95)], 'Gold', 24, (x, py, 0), cap_top=False)
        for k in range(12):
            a = 2 * PI * k / 12
            b.sphere((x + 0.85 * math.cos(a), py + 0.85 * math.sin(a), 9.55), 0.16, 'Limestone', 6, 4, (0.6, 1.0, 1.4))

# arcade walls on the pillar lines (pointed arches between pillars) up to the springing
ARC_SP = 9.9
for side in (-1, 1):
    x = side * XP
    ops_y = [((a_ + b_) / 2, (b_ - a_) - 2.2) for a_, b_ in zip(PY, PY[1:])]
    ya, yb = PY[0] - 0.95, PY[-1] + 0.95
    for xp, nrm in ((x - side * 0.5, -side), (x + side * 0.5, side)):
        if nrm > 0:
            fr, conv = ((xp, Y0, 0), PI / 2), (lambda y: y - Y0)
        else:
            fr, conv = ((xp, Y1, 0), -PI / 2), (lambda y: Y1 - y)
        with K.push(*fr):
            ops = [(conv(cy), w, ARC_SP, 'pointed', None) for cy, w in ops_y]
            e0, e1 = sorted((conv(ya), conv(yb)))
            kit.arch_wall(b, e0, e1, ARC_SP, ZS, ops, 'Ashlar Hall', 0.0, 0.0)
    for cy, w in ops_y:
        pts = kit.arch_pts(cy, w, ARC_SP, 'pointed', 14)
        for (ya_, za), (yb_, zb) in zip(pts, pts[1:]):
            b.quad((x - 0.5, ya_, za), (x + 0.5, ya_, za), (x + 0.5, yb_, zb), (x - 0.5, yb_, zb), 'Ashlar Hall')
        # voussoir band on both faces
        P = kit.arch_pts(cy, w, ARC_SP, 'pointed', 11)
        for (y0_, z0_), (y1_, z1_) in zip(P, P[1:]):
            for xf in (x - 0.53, x + 0.53):
                b.beam((xf, y0_, z0_), (xf, y1_, z1_), 0.08, 0.3, 'Limestone', 0.01, up=(1, 0, 0))
    b.box(x - 0.6, PY[0] - 1.0, ZS - 0.3, x + 0.6, PY[-1] + 1.0, ZS, 'Limestone', 0.03)

# vaults: nave (pointed barrel) + aisles, with transverse ribs at each pillar
nave = pointed_pts(-XP, XP, ZS, 5.5, 24)
aisle_l = pointed_pts(-XW, -XP, ZS, 2.4, 12)
aisle_r = pointed_pts(XP, XW, ZS, 2.4, 12)
for prof in (nave, aisle_l, aisle_r):
    def vf(s, t, prof=prof):
        k = s * (len(prof) - 1)
        i = min(int(k), len(prof) - 2)
        f = k - i
        x = prof[i][0] * (1 - f) + prof[i + 1][0] * f
        z = prof[i][1] * (1 - f) + prof[i + 1][1] * f
        return (x, Y0 + (Y1 - Y0) * t, z)
    # normal must point down into the hall
    b.grid(len(prof) - 1, 20, lambda s, t, vf=vf: vf(1 - s, t), 'Plaster Hall', (20, Y1 - Y0), smooth=True)
    for py in PY + [Y0 + 0.4, Y1 - 0.4]:
        for (xa, za), (xb, zb) in zip(prof, prof[1:]):
            b.beam((xa, py, za - 0.08), (xb, py, zb - 0.08), 0.42, 0.34, 'Stone Drums', 0.03, up=(0, 0, 1))
# ridge rib along the nave
b.beam((0, Y0, ZS + 5.5 - 0.15), (0, Y1, ZS + 5.5 - 0.15), 0.3, 0.3, 'Limestone', 0.03)
for py in PY:
    b.sphere((0, py, ZS + 5.5 - 0.3), 0.35, 'Gold', 12, 8)
print('structure %.1fs' % (time.time() - T0))

# ==============================================================================================
# Dais, throne, canopy, drapes, carpet
# ==============================================================================================
DAIS_Y = 11.0
STEP_H, STEP_D, NSTEP = 0.18, 0.45, 5
TOP_Z = STEP_H * NSTEP
for i in range(NSTEP):
    y0 = DAIS_Y + i * STEP_D
    hw = 5.2 - i * 0.35
    b.box(-hw, y0, 0.0, hw, Y1 - 0.2, STEP_H * (i + 1), 'Marble White', 0.02)
    b.box(-hw - 0.02, y0 - 0.02, STEP_H * (i + 1) - 0.05, hw + 0.02, y0 + 0.06, STEP_H * (i + 1), 'Gold', 0.01)
# carpet: along the nave up to the dais, then up the steps and to the throne
CW = 2.6
carp_y0, carp_y1 = Y0 + 1.6, DAIS_Y
cV, cF, cU = [], [], []
nseg = 40
for j in range(nseg + 1):
    y = carp_y0 + (carp_y1 - carp_y0) * j / nseg
    cV += [(-CW / 2, y, 0.014), (CW / 2, y, 0.014)]
for j in range(nseg):
    a = 2 * j
    cF.append((a, a + 1, a + 3, a + 2))
    u0 = (carp_y1 - carp_y0) * j / nseg
    u1 = (carp_y1 - carp_y0) * (j + 1) / nseg
    cU.append([(u0, CW), (u0, 0.0), (u1, 0.0), (u1, CW)])
# carpet up the steps
yy, zz = carp_y1, 0.014
ulen = carp_y1 - carp_y0
for i in range(NSTEP):
    base = len(cV)
    z1 = STEP_H * (i + 1) + 0.014
    y1 = carp_y1 + (i + 1) * STEP_D
    cV += [(-CW / 2, yy, zz), (CW / 2, yy, zz), (CW / 2, yy, z1), (-CW / 2, yy, z1), (-CW / 2, y1, z1), (CW / 2, y1, z1)]
    cF.append((base, base + 1, base + 2, base + 3))
    cU.append([(ulen, CW), (ulen, 0), (ulen + STEP_H, 0), (ulen + STEP_H, CW)])
    ulen += STEP_H
    cF.append((base + 3, base + 2, base + 5, base + 4))
    cU.append([(ulen, CW), (ulen, 0), (ulen + STEP_D, 0), (ulen + STEP_D, CW)])
    ulen += STEP_D
    yy, zz = y1, z1
b.mesh(cV, cF, 'Carpet Royal', cU)
# carpet edge rods (brass) on each step nosing
for i in range(NSTEP):
    yb_ = carp_y1 + i * STEP_D
    b.cyl((-CW / 2 - 0.05, yb_ + 0.01, STEP_H * (i + 1) + 0.02), (CW / 2 + 0.05, yb_ + 0.01, STEP_H * (i + 1) + 0.02), 0.018, 'Brass', 8)

TY = 15.0     # throne centre


def throne(K, y, z):
    b = K.b
    with K.push((0, y, z)):
        # base plinth
        b.box(-1.25, -0.9, 0.0, 1.25, 0.95, 0.22, 'Marble Dark', 0.03)
        b.box(-1.3, -0.95, 0.18, 1.3, 1.0, 0.24, 'Gold', 0.01)
        # seat box
        b.box(-0.95, -0.55, 0.24, 0.95, 0.75, 0.75, 'Timber Dark', 0.02)
        b.box(-0.97, -0.6, 0.62, 0.97, 0.78, 0.75, 'Gold', 0.012)
        b.box(-0.82, -0.52, 0.75, 0.82, 0.62, 0.92, 'Velvet Red', 0.06)
        # tall back with a pointed top
        back = [(-0.95, 0.75), (0.95, 0.75), (0.95, 2.9), (0.55, 3.35), (0.0, 3.75), (-0.55, 3.35), (-0.95, 2.9)]
        b.prism(back, 0.62, 0.9, 'Timber Dark')
        inner = [(-0.7, 0.95), (0.7, 0.95), (0.7, 2.75), (0.4, 3.1), (0.0, 3.4), (-0.4, 3.1), (-0.7, 2.75)]
        b.prism(inner, 0.58, 0.63, 'Velvet Red')
        # gold border on the back outline
        for (xa, za), (xb, zb) in zip(back[1:] + back[:1], back[2:] + back[:2]):
            if za > 0.8 or zb > 0.8:
                b.beam((xa, 0.6, za), (xb, 0.6, zb), 0.1, 0.05, 'Gold', 0.01, up=(0, 1, 0))
        b.sphere((0.0, 0.62, 3.85), 0.16, 'Gold', 12, 8)
        b.lathe([(0.12, 3.7), (0.04, 4.15), (0.0, 4.2)], 'Gold', 8, (0, 0.75, 0))
        # crown emblem on the back
        crown = [(-0.32, 2.55), (0.32, 2.55), (0.36, 2.95), (0.18, 2.78), (0.0, 3.05), (-0.18, 2.78), (-0.36, 2.95)]
        b.prism(crown, 0.555, 0.58, 'Gold')
        # armrests with lion-head knobs
        for sx in (-1, 1):
            b.box(sx * 0.95 - 0.13, -0.55, 0.75, sx * 0.95 + 0.13, 0.75, 1.35, 'Timber Dark', 0.02)
            b.box(sx * 0.95 - 0.16, -0.62, 1.35, sx * 0.95 + 0.16, 0.8, 1.46, 'Gold', 0.02)
            b.sphere((sx * 0.95, -0.62, 1.48), 0.14, 'Gold', 12, 8)
            b.lathe([(0.12, 0.24), (0.1, 0.4), (0.14, 0.55), (0.09, 0.7), (0.11, 0.75)], 'Gold', 10, (sx * 0.95, -0.55, 0))
            b.cyl((sx * 0.95, 0.8, 0.24), (sx * 0.95, 0.8, 2.9), 0.09, 'Gold', 10)
            b.sphere((sx * 0.95, 0.8, 3.0), 0.13, 'Gold', 10, 6)
        # cushion on the back
        b.sphere((0.0, 0.5, 1.45), 0.5, 'Velvet Red', 16, 8, (1.4, 0.35, 1.0))


throne(K, TY, TOP_Z)
# canopy (baldachin) over the throne
with K.push((0, TY + 0.3, TOP_Z)):
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.lathe([(0.13, 0.0), (0.1, 0.2), (0.09, 5.6), (0.13, 5.8)], 'Gold', 12, (sx * 1.9, sy * 1.2, 0))
    b.box(-2.15, -1.45, 5.8, 2.15, 1.45, 6.2, 'Timber Dark', 0.03)
    b.box(-2.2, -1.5, 5.75, 2.2, 1.5, 5.85, 'Gold', 0.02)
    b.box(-2.2, -1.5, 6.2, 2.2, 1.5, 6.3, 'Gold', 0.02)
    # scalloped velvet valance
    for side, (pa, pb_) in enumerate((((-2.2, -1.52), (2.2, -1.52)), ((2.22, -1.5), (2.22, 1.5)), ((2.2, 1.52), (-2.2, 1.52)), ((-2.22, 1.5), (-2.22, -1.5)))):
        nsc = 9 if side % 2 == 0 else 6
        for i in range(nsc):
            def val(s, t, i=i, pa=pa, pb_=pb_, nsc=nsc):
                ss = (i + s) / nsc
                x = pa[0] + (pb_[0] - pa[0]) * ss
                y = pa[1] + (pb_[1] - pa[1]) * ss
                drop = 0.45 + 0.15 * math.sin(PI * s)
                return (x, y, 5.8 - t * drop)
            b.grid(4, 2, val, 'Velvet Red', (4.4 / nsc, 0.6), smooth=True, both=True)
    # top crest
    b.prism([(-1.0, 6.3), (1.0, 6.3), (0.0, 7.2)], -1.46, -1.4, 'Gold')
    b.sphere((0, -1.43, 7.25), 0.15, 'Gold', 10, 6)
# drapes behind the throne (folded velvet) + giant banner
for sx in (-1, 1):
    def drape(s, t, sx=sx):
        x = sx * (2.6 + 2.2 * s)
        fold = 0.12 * math.sin(s * 2 * PI * 4.5)
        gather = 1.0 - 0.35 * t * (1 - s) if False else 1.0
        return (x * gather, Y1 - 0.35 + fold, 0.9 + (11.5 - 0.9) * (1 - t))
    b.grid(40, 10, drape, 'Velvet Red', (2.2 * 1.6, 10.6), smooth=True, both=True)
    b.cyl((sx * 2.4, Y1 - 0.4, 11.6), (sx * 5.0, Y1 - 0.4, 11.6), 0.05, 'Gold', 8)
kit.flat_banner(K, 0.0, Y1 - 0.25, 8.7, 'crown', length=6.9, width=2.6, notch=0.6, sway=0.02)
print('dais %.1fs' % (time.time() - T0))

# ==============================================================================================
# Dressing: banners on the arcade, braziers, candelabras, chandeliers, benches
# ==============================================================================================
designs = ['crown', 'sun', 'tower', 'swords', 'crown', 'sun']
for side in (-1, 1):
    for i, py in enumerate(PY):
        x = side * (XP - 0.82)
        with K.push((x, py, 0), -side * PI / 2):
            kit.flat_banner(K, 0.0, 0.0, 8.45, designs[(i + (side > 0)) % len(designs)], length=4.4, width=1.15, notch=0.3, sway=0.02)


def brazier(K, x, y, z=0.0, s=1.0):
    b = K.b
    with K.push((x, y, z)):
        for k in range(3):
            a = 2 * PI * k / 3
            b.beam((0.42 * s * math.cos(a), 0.42 * s * math.sin(a), 0.0), (0.18 * s * math.cos(a), 0.18 * s * math.sin(a), 0.85 * s), 0.05 * s, 0.05 * s,
                   'Iron Black', 0.008)
            b.sphere((0.42 * s * math.cos(a), 0.42 * s * math.sin(a), 0.03), 0.05 * s, 'Iron Black', 6, 4)
        b.torus((0, 0, 0.4 * s), 0.3 * s, 0.02 * s, 'Iron Black', 16, 5, 'Z')
        b.lathe([(0.1 * s, 0.8 * s), (0.42 * s, 0.9 * s), (0.55 * s, 1.15 * s), (0.58 * s, 1.2 * s), (0.5 * s, 1.18 * s), (0.0, 1.0 * s)],
                'Iron', 16, cap_top=False)
        b.lathe([(0.47 * s, 1.1 * s), (0.0, 1.12 * s)], 'Charcoal', 14, cap_top=False)
        for k in range(7):
            a = 2 * PI * k / 7
            r_ = 0.2 * s * (0.4 + (k % 3) * 0.3)
            b.sphere((r_ * math.cos(a), r_ * math.sin(a), 1.12 * s), 0.07 * s, 'Embers', 6, 4, (1, 1, 0.6))
        for k in range(6):
            a = 2 * PI * k / 6 + 0.3
            r_ = 0.2 * s * (k % 2) + 0.05
            hh = (0.45 + 0.22 * ((k * 7) % 3)) * s
            kit.flame(b, (r_ * math.cos(a), r_ * math.sin(a), 1.08 * s), hh, 0.13 * s, 'Flame', 10, (0.03 * math.cos(a), 0.03 * math.sin(a)), k * 1.7)
        K.light((0, 0, 1.6 * s), 0, '#ff8a35', 0.3 * s)   # placeholder (per-preset lights added below)


def candelabra(K, x, y, z=0.0, h=2.3):
    b = K.b
    with K.push((x, y, z)):
        b.lathe([(0.3, 0.0), (0.28, 0.06), (0.1, 0.2), (0.05, 0.4), (0.04, h)], 'Iron Black', 12, cap_top=False)
        for k in range(-3, 4):
            px = k * 0.16
            hz = h + 0.05 - abs(k) * 0.06
            if k:
                b.cyl((0, 0, h - 0.25), (px, 0, hz - 0.02), 0.012, 'Iron Black', 5)
            b.lathe([(0.05, hz - 0.04), (0.05, hz)], 'Iron Black', 8, (px, 0, 0))
            b.cyl((px, 0, hz), (px, 0, hz + 0.18), 0.022, 'Wax', 8)
            kit.flame(b, (px, 0, hz + 0.18), 0.075, 0.017, 'Flame Candle', 8)


def chandelier(K, x, y, z, r=1.4, n=12):
    b = K.b
    with K.push((x, y, z)):
        b.torus((0, 0, 0), r, 0.05, 'Iron Black', 32, 6, 'Z')
        b.torus((0, 0, 0.12), r * 0.6, 0.035, 'Iron Black', 24, 6, 'Z')
        for k in range(4):
            a = 2 * PI * k / 4
            b.cyl((r * math.cos(a), r * math.sin(a), 0.0), (0, 0, 1.6), 0.015, 'Iron Black', 5)
        b.cyl((0, 0, 1.6), (0, 0, ZS + 5.5 - z - 0.3), 0.03, 'Iron Black', 6)
        for k in range(n):
            a = 2 * PI * k / n
            px, py = r * math.cos(a), r * math.sin(a)
            b.cyl((px, py, 0.04), (px, py, 0.22), 0.025, 'Wax', 8)
            kit.flame(b, (px, py, 0.22), 0.075, 0.017, 'Flame Candle', 8)


KD = kit.Kit('%s Dressing' % CODE, 9)
BRAZ = [(-2.6, -9.5), (2.6, -9.5), (-2.6, 0.0), (2.6, 0.0), (-3.2, 9.6), (3.2, 9.6)]
for x, y in BRAZ:
    brazier(KD, x, y, 0.0, 1.0)
for sx in (-1, 1):
    candelabra(KD, sx * 2.9, TY - 0.2, TOP_Z, 2.3)
    candelabra(KD, sx * 4.4, DAIS_Y - 0.6, 0.0, 2.0)
CHAND = [(0.0, -6.25), (0.0, 2.75)]
for x, y in CHAND:
    chandelier(KD, x, y, 8.2)
# benches along the aisles
for side in (-1, 1):
    for y in (-11.5, -7.0, -2.5, 2.0, 6.5):
        x = side * 7.2
        KD.b.box(x - 0.25, y - 1.4, 0.42, x + 0.25, y + 1.4, 0.5, 'Planks', 0.01)
        for yy in (y - 1.2, y + 1.2):
            KD.b.box(x - 0.22, yy - 0.05, 0.0, x + 0.22, yy + 0.05, 0.42, 'Timber Dark', 0.01)
        KD.b.box(x + side * 0.2 - 0.04, y - 1.4, 0.5, x + side * 0.2 + 0.04, y + 1.4, 1.0, 'Planks', 0.01)
KD.lights = []      # brazier placeholders replaced by per-preset lights below
KD.finish(SET, NIGHT, NIGHT)
K.finish(SET, NIGHT, NIGHT)
print('dressing %.1fs' % (time.time() - T0))

# ==============================================================================================
# Per-preset window glass + fake light shafts
# ==============================================================================================
def glass_for(preset, mat):
    g = geo.Builder('%s Stained Glass %s' % (CODE, preset))
    for side, cy in glass_panes:
        x = side * (XW + 0.45)
        poly = lancet_poly(0.0, WIN_W, WIN_Z0, WIN_SP)
        pts = [(x, cy + (px if side > 0 else -px), pz) for px, pz in poly]
        uv = [((px + WIN_W / 2), pz - WIN_Z0) for px, pz in poly]
        g.poly(pts, mat, uv)
    # rose windows (north and south)
    for y, r, cz in ((Y1 + 0.45, ROSE_R, ROSE_Z), (Y0 - 0.45, 2.0, ROSE_Z - 0.4)):
        n = 40
        pts = [(r * math.cos(2 * PI * i / n), y, cz + r * math.sin(2 * PI * i / n)) for i in range(n)]
        uv = [(p[0] + r, p[2] - cz + r) for p in pts]
        g.poly(pts, mat, uv)
    return g.finish(C[preset])


glass_for('DAY', 'Stained Glass Day')
glass_for('GOLDEN', 'Stained Glass Golden')
glass_for('NIGHT', 'Stained Glass Night')


def shafts(preset, mat, direction, sides=(1,), length=16.0, width_scale=1.0):
    d = Vector(direction).normalized()
    objs = []
    for side, cy in glass_panes:
        if side not in sides:
            continue
        src = Vector((side * XW, cy, (WIN_Z0 + WIN_SP) / 2 + 0.8))
        g = geo.Builder('%s Shaft %s %d' % (CODE, preset, len(objs) + 1))
        w, h = WIN_W * 0.75 * width_scale, 3.0
        length = min(length, (src.z - 0.4) / max(-d.z, 0.05))
        # local box: x across (along the wall), y = height across, z = along the light
        g.box(-w / 2, -h / 2, 0.0, w / 2, h / 2, length, mat)
        ob = g.finish(C[preset])[0]
        zaxis = d
        xaxis = Vector((0, 1, 0))
        yaxis = zaxis.cross(xaxis).normalized()
        xaxis = yaxis.cross(zaxis).normalized()
        R = Matrix((xaxis, yaxis, zaxis)).transposed().to_4x4()
        ob.matrix_world = Matrix.Translation(src * M) @ R
        ob.visible_shadow = False
        ob.visible_diffuse = False
        ob.visible_glossy = False
        objs.append(ob)
    return objs


# sun directions (towards which the light travels)
SUN_DAY = (-0.62, 0.25, -0.74)
SUN_GOLD = (-0.9, -0.15, -0.38)
MOON = (0.75, 0.2, -0.62)
shafts('DAY', 'Shaft Day', SUN_DAY, (1,), 15.0)
shafts('GOLDEN', 'Shaft Golden', SUN_GOLD, (1,), 19.0)
shafts('NIGHT', 'Shaft Night', MOON, (-1,), 15.0)

# ==============================================================================================
# Lights
# ==============================================================================================
worlds = {}


def sun_towards(col, preset, d, name, strength=None):
    d = Vector(d).normalized()
    o = look.sun_obj(col, preset, 0.0, name, strength)
    o.rotation_euler = (-d).to_track_quat('Z', 'Y').to_euler()
    return o


s1 = sun_towards(C['DAY'], 'DAY', SUN_DAY, '%s Sun DAY' % CODE, 6.0)
worlds['DAY'] = look.world_sky(sc, 'DAY', '%s Sky DAY' % CODE, look.sun_direction(s1))
s2 = sun_towards(C['GOLDEN'], 'GOLDEN', SUN_GOLD, '%s Sun GOLDEN' % CODE, 6.5)
worlds['GOLDEN'] = look.world_sky(sc, 'GOLDEN', '%s Sky GOLDEN' % CODE, look.sun_direction(s2))
s3 = sun_towards(C['NIGHT'], 'NIGHT', MOON, '%s Moon' % CODE, 1.2)
worlds['NIGHT'] = look.world_sky(sc, 'NIGHT', '%s Sky NIGHT' % CODE, look.sun_direction(s3))
for p, (fill, fcol, braz_w, cand_w) in {'DAY': (380, '#cfe0ff', 160, 25), 'GOLDEN': (220, '#ffd2a0', 220, 30),
                                        'NIGHT': (40, '#6f86d0', 420, 45)}.items():
    col = C[p]
    # soft bounce from the windows (both sides) and the vault
    for side in (-1, 1):
        look.area(col, '%s window bounce %s %s' % (CODE, p, 'L' if side < 0 else 'R'), V(side * (XW - 0.6), 0.0, 7.0),
                  (0, side * PI / 2 * -1 if False else 0, 0), 1.0, fill, fcol, 'RECTANGLE', 30.0)
        o = bpy.data.objects['%s window bounce %s %s' % (CODE, p, 'L' if side < 0 else 'R')]
        o.rotation_euler = (0, side * PI / 2, 0)
        o.data.size = 8.0 * M
        o.data.size_y = 26.0 * M
    look.area(col, '%s vault bounce %s' % (CODE, p), V(0, 0, 15.5), (0, 0, 0), 1.0, fill * 0.8, fcol, 'RECTANGLE')
    o = bpy.data.objects['%s vault bounce %s' % (CODE, p)]
    o.data.size = 9.0 * M
    o.data.size_y = 30.0 * M
    for i, (x, y) in enumerate(BRAZ):
        look.point(col, '%s brazier %s %d' % (CODE, p, i + 1), V(x, y, 1.75), braz_w, '#ff8a35', 0.35)
    for i, (x, y) in enumerate(CHAND):
        look.point(col, '%s chandelier %s %d' % (CODE, p, i + 1), V(x, y, 8.1), cand_w * 4, '#ffb060', 1.2)
    for sx in (-1, 1):
        look.point(col, '%s candles %s %s' % (CODE, p, sx), V(sx * 2.9, TY - 0.2, TOP_Z + 2.55), cand_w, '#ffb060', 0.4)
    # warm key on the throne
    look.spot(col, '%s throne key %s' % (CODE, p), V(0.0, 6.0, 9.0), V(0.0, TY, 2.5), {'DAY': 900, 'GOLDEN': 900, 'NIGHT': 1400}[p],
              '#ffd9a0', 32, 0.8, 0.6)

# ==============================================================================================
# Marks and cameras
# ==============================================================================================
MK = C['marks']
HERO = (-0.6, 7.4, 0.0)
RIVAL = (1.5, 5.8, 0.0)


def mark(name, p, facing):
    look.mark(MK, '%s_%s' % (CODE, name), V(*p), facing)


mark('MARK_HERO', HERO, look.face_towards(HERO, RIVAL) - 60)
mark('MARK_RIVAL', RIVAL, look.face_towards(RIVAL, HERO) + 50)
mark('MARK_SIBLING', (-2.0, 6.6, 0.0), look.face_towards((-2.0, 6.6), RIVAL) - 20)
mark('MARK_RULER', (0.0, TY - 1.45, TOP_Z), 0.0)                 # standing in front of the throne
mark('MARK_RULER_SEATED', (0.0, TY - 0.05, TOP_Z + 0.92), 0.0)  # on the seat (for a sitting pose)
crowd = [(-3.3, 3.5), (3.3, 3.0), (-3.4, -1.5), (3.4, -2.0), (-3.2, -5.5), (3.2, -6.0), (-6.8, 0.5), (6.8, -3.0)]
for i, (x, y) in enumerate(crowd):
    mark('MARK_CROWD_%d' % (i + 1), (x, y, 0.0), look.face_towards((x, y), (0.0, y + 0.01)) + (180 if False else 0))
for i, (x, y) in enumerate([(-2.0, DAIS_Y - 1.0), (2.0, DAIS_Y - 1.0), (-4.2, TY - 0.5), (4.2, TY - 0.5), (-1.8, -14.5), (1.8, -14.5)]):
    mark('MARK_GUARD_%d' % (i + 1), (x, y, TOP_Z if y > DAIS_Y + 2 else 0.0), 0.0)
mark('MARK_GIANT', (0.0, -8.0, 0.0), 180.0)

CM = C['cams']
cams = {}


def cam(name, pos, tgt, lens, note):
    cams[name] = look.camera(CM, '%s_%s' % (CODE, name), V(*pos), V(*tgt), lens, note)


cam('WIDE_ESTABLISH', (0.0, -15.6, 4.8), (0.0, 12.0, 5.2), 18, 'from the doors down the red carpet to the throne; pillars, banners, light shafts, rose window')
cam('LOW_HERO', (0.25, 4.7, 0.35), (-0.55, 7.4, 1.5), 20, 'knee height looking up at MARK_HERO; throne, canopy and rose window behind')
cam('CROWD_MED', (-3.4, -5.6, 2.2), (0.8, 5.0, 1.3), 28, 'from the west aisle across the carpet: courtiers, hero, dais')
cam('TWO_SHOT', (0.4, -0.5, 1.35), (0.45, 6.6, 1.1), 30, 'hero (left) and rival (right) on the carpet, throne between them')
cam('CLOSE_A', (-0.45, 5.55, 1.12), (HERO[0], HERO[1], 1.1), 50, 'hero face, warm brazier light')
cam('CLOSE_B', (-0.25, 5.3, 1.72), (RIVAL[0], RIVAL[1], 1.72), 50, 'rival face')
cam('INSERT_THRONE', (0.0, 10.4, 2.6), (0.0, TY, 2.4), 35, 'the throne under its canopy (MARK_RULER stands just in front; hide the ruler for an empty-throne insert)')
cam('INSERT_WINDOW', (-2.4, -4.6, 1.6), (XW, -1.75, 7.2), 24, 'stained-glass lancets and light shafts across the hall')
cam('RULER_POV', (0.0, TY - 0.6, TOP_Z + 1.55), (0.0, -10.0, 1.0), 24, 'from the throne down the hall')

setbase.finish(sc, master, C, TITLE, CODE, cams['WIDE_ESTABLISH'], worlds,
               os.path.join(setbase.OUT, 'throne_hall', 'throne_hall.blend'),
               exposure={'DAY': -0.1, 'GOLDEN': 0.0, 'NIGHT': 0.35})
print('saved %.1fs' % (time.time() - T0))
