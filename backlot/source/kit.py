"""Backlot kit: buildings, architectural parts and street props.
Everything is authored in METRES in a local frame (front = -Y, up = +Z) through geo.Builder.
A Kit owns two builders sharing one transform stack: `b` (the set) and `n` (night-only glow meshes:
lit windows, flames) plus a list of night practical lights."""
import math, os, random
from mathutils import Vector, Matrix
import bpy
import geo, mats, look

M = geo.M
HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, 'art')
PI = math.pi


class Kit:
    def __init__(self, name, seed=1):
        self.name = name
        self.b = geo.Builder(name, seed)
        self.n = geo.Builder(name + ' Night', seed + 7)
        self.lights = []
        self.rng = random.Random(seed)

    # shared transform stack ------------------------------------------------------------------
    def push(self, loc=(0, 0, 0), rz=0.0, rx=0.0, ry=0.0, scale=1.0):
        self.b.push(loc, rz, rx, ry, scale)
        self.n.push(loc, rz, rx, ry, scale)
        return self

    def pop(self):
        self.b.pop()
        self.n.pop()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.pop()

    def light(self, p, watts=60, hexc='#ffa040', radius=0.06):
        self.lights.append((self.b.T @ Vector(p), watts, hexc, radius))

    def finish(self, set_col, night_col, light_col, parent=None, loc=(0, 0, 0), rz=0.0):
        """Create objects. If loc/rz given, an empty named after the kit is placed there and owns everything."""
        if parent is None:
            parent = bpy.data.objects.new(self.name, None)
            parent.empty_display_type = 'PLAIN_AXES'
            parent.empty_display_size = 2.0
            parent.location = Vector(loc) * M
            parent.rotation_euler = (0, 0, rz)
            set_col.objects.link(parent)
        objs = self.b.finish(set_col, parent=parent)
        if self.n.F:
            objs += self.n.finish(night_col, parent=parent)
        for i, (p, w, h, r) in enumerate(self.lights):
            o = look.point(light_col, '%s lamp %02d' % (self.name, i), p * M, w, h, r)
            o.parent = parent
        return parent, objs


def sign_material(icon):
    name = 'Sign ' + icon
    m = bpy.data.materials.get(mats.PREFIX + name)
    if m is None:
        m = mats.image_material(name, os.path.join(ART, 'sign_%s.png' % icon), base='Planks')
    return name


def banner_material(design):
    name = 'Banner ' + design
    m = bpy.data.materials.get(mats.PREFIX + name)
    if m is None:
        m = mats.image_material(name, os.path.join(ART, 'banner_%s.png' % design), base='Cloth White')
    return name


# ==============================================================================================
# Arches
# ==============================================================================================
def arch_pts(cx, w, spring, kind='round', n=14, rise=None):
    """Intrados points (x, z) from the left springer to the right springer."""
    r = w / 2
    pts = []
    if kind == 'round':
        for i in range(n + 1):
            t = PI * i / n
            pts.append((cx - r * math.cos(t), spring + r * math.sin(t)))
    elif kind == 'segmental':
        rise = rise or w * 0.25
        R = (r * r + rise * rise) / (2 * rise)
        zc = spring + rise - R
        a0 = math.atan2(spring - zc, -r)
        a1 = math.atan2(spring - zc, r)
        for i in range(n + 1):
            a = a0 + (a1 - a0) * i / n
            pts.append((cx + R * math.cos(a), zc + R * math.sin(a)))
    else:  # pointed (equilateral)
        half = n // 2
        for i in range(half + 1):
            a = PI - (PI / 3) * i / half
            pts.append((cx + r + w * math.cos(a), spring + w * math.sin(a)))
        for i in range(1, half + 1):
            a = (2 * PI / 3) - (PI / 3) * i / half
            pts.append((cx - r + w * math.cos(a), spring + w * math.sin(a)))
    return pts


def arch_wall(b, x0, x1, z0, z1, openings, mat, y=0.0, depth=0.4, intrados=None, voussoirs=None,
              vh=0.38, vproud=0.04, keystone=True):
    """Wall plane (normal -Y) with arched openings [(cx, w, spring, kind, rise)] reaching down to z0."""
    ops = sorted(openings, key=lambda o: o[0])
    xs = [x0]
    for cx, w, s, kind, rise in ops:
        xs += [cx - w / 2, cx + w / 2]
    xs.append(x1)
    for i in range(0, len(xs), 2):
        if xs[i + 1] - xs[i] > 1e-5:
            b.quad((xs[i], y, z0), (xs[i + 1], y, z0), (xs[i + 1], y, z1), (xs[i], y, z1), mat)
    im = intrados or mat
    for cx, w, s, kind, rise in ops:
        pts = arch_pts(cx, w, s, kind, 16, rise)
        xl, xr = cx - w / 2, cx + w / 2
        poly = [(x, y, z) for x, z in pts] + [(xr, y, z1), (xl, y, z1)]
        b.poly(poly, mat)
        d = y + depth
        for (xa, za), (xb, zb) in zip(pts, pts[1:]):
            b.quad((xa, y, za), (xa, d, za), (xb, d, zb), (xb, y, zb), im)
        if s > z0:
            b.quad((xl, d, z0), (xl, d, s), (xl, y, s), (xl, y, z0), im)
            b.quad((xr, y, s), (xr, d, s), (xr, d, z0), (xr, y, z0), im)
        if voussoirs:
            nv = max(7, int(len(pts) * 0.8) | 1)
            P = arch_pts(cx, w, s, kind, nv, rise)
            for k, ((xa, za), (xb, zb)) in enumerate(zip(P, P[1:])):
                mid = Vector(((xa + xb) / 2, (za + zb) / 2))
                tang = Vector((xb - xa, zb - za))
                L = tang.length
                tang.normalize()
                nrm = Vector((-tang.y, tang.x))   # points away from the opening (outwards)
                hh = vh * (1.25 if (keystone and k == len(P) // 2 - (0 if len(P) % 2 else 1)) else 1.0)
                c = mid + nrm * hh / 2
                ang = math.atan2(tang.y, tang.x)
                b.cbox((c.x, y - vproud / 2 + 0.002, c.y), (L - 0.012, vproud + 0.01, hh), voussoirs, 0.012, rot=(0, -ang, 0))


# ==============================================================================================
# Architectural details
# ==============================================================================================
def window(K, x, z0, w, h, y, depth, frame='Timber Oak', sill='Limestone', shutters=None, flower=False,
           lit=False, mullion=True, shutter_angle=None):
    """Glazing set into a hole [x-w/2, x+w/2] x [z0, z0+h] in a wall plane at y (normal -Y)."""
    b = K.b
    rng = K.rng
    gy = y + depth * 0.5
    t = 0.055
    x0, x1 = x - w / 2, x + w / 2
    b.box(x0, gy - 0.02, z0, x1, gy + 0.05, z0 + t, frame, 0.006)
    b.box(x0, gy - 0.02, z0 + h - t, x1, gy + 0.05, z0 + h, frame, 0.006)
    b.box(x0, gy - 0.02, z0 + t, x0 + t, gy + 0.05, z0 + h - t, frame, 0.006)
    b.box(x1 - t, gy - 0.02, z0 + t, x1, gy + 0.05, z0 + h - t, frame, 0.006)
    if mullion and w > 0.55:
        b.box(x - 0.025, gy - 0.015, z0 + t, x + 0.025, gy + 0.04, z0 + h - t, frame, 0.005)
    if h > 1.0:
        zt = z0 + h * 0.68
        b.box(x0 + t, gy - 0.015, zt - 0.022, x1 - t, gy + 0.04, zt + 0.022, frame, 0.005)
    uv = [(0, 0), (w, 0), (w, h), (0, h)]
    b.quad((x0, gy + 0.01, z0), (x1, gy + 0.01, z0), (x1, gy + 0.01, z0 + h), (x0, gy + 0.01, z0 + h), 'Glass Leaded', uv)
    if lit:
        K.n.quad((x0, gy + 0.004, z0), (x1, gy + 0.004, z0), (x1, gy + 0.004, z0 + h), (x0, gy + 0.004, z0 + h), 'Glass Window Lit', uv)
    if sill:
        b.box(x0 - 0.07, y - 0.07, z0 - 0.075, x1 + 0.07, y + depth * 0.5, z0, sill, 0.012)
    if shutters:
        for side in (-1, 1):
            hx = x1 if side > 0 else x0
            ang = shutter_angle if shutter_angle is not None else rng.uniform(0.05, 0.6)
            with K.push((hx, y - 0.01, z0 + 0.02), rz=-side * ang):
                lw = w / 2 + 0.02
                # leaf from hinge outward (+x for right, -x for left)
                xa, xb = (0.0, lw) if side > 0 else (-lw, 0.0)
                b.box(xa, -0.045, 0, xb, -0.01, h - 0.04, shutters, 0.006)
                for hz in (0.12 * h, 0.82 * h):
                    b.box(xa + (0 if side > 0 else lw * 0.25), -0.055, hz, xb - (lw * 0.25 if side > 0 else 0), -0.044, hz + 0.035, 'Iron Black')
    if flower:
        flowerbox(K, x, y - 0.075, z0 - 0.08, w + 0.12)


def flowerbox(K, x, y, z, w, colors=None):
    b = K.b
    rng = K.rng
    b.box(x - w / 2, y - 0.22, z - 0.2, x + w / 2, y, z, 'Planks Grey', 0.01)
    b.box(x - w / 2 + 0.03, y - 0.19, z - 0.04, x + w / 2 - 0.03, y - 0.03, z - 0.015, 'Soil')
    colors = colors or rng.sample(['Petal Red', 'Petal Yellow', 'Petal Purple', 'Petal White', 'Petal Red'], 2)
    n = int(w / 0.07)
    for i in range(n):
        px = x - w / 2 + 0.05 + (w - 0.1) * (i + rng.random() * 0.6) / n
        py = y - 0.11 + rng.uniform(-0.06, 0.06)
        hz = z + rng.uniform(0.06, 0.2)
        b.sphere((px, py, z - 0.01 + (hz - z) * 0.4), rng.uniform(0.045, 0.07), 'Leaf', 6, 4, (1, 1, 0.7))
        if rng.random() < 0.75:
            b.sphere((px + rng.uniform(-0.02, 0.02), py, hz), rng.uniform(0.028, 0.045), colors[i % len(colors)], 6, 4, (1, 1, 0.75))
    # trailing ivy over the front
    for i in range(int(w / 0.18)):
        px = x - w / 2 + 0.08 + i * 0.18 + rng.uniform(-0.04, 0.04)
        L = rng.uniform(0.1, 0.35)
        for k in range(4):
            b.sphere((px + rng.uniform(-0.02, 0.02), y - 0.235, z - 0.03 - L * k / 3), 0.035, 'Leaf', 5, 3, (1, 0.6, 1))


def door(K, x, w, h, y, depth, paint='Paint Green', z0=0.0, step=True, surround=None, arched=False, knock=True):
    b = K.b
    dy = y + depth * 0.62
    b.box(x - w / 2, dy, z0, x + w / 2, dy + 0.06, z0 + h, paint, 0.006)
    # battens behind are hidden; iron strap hinges and nails on the face
    for hz in (z0 + 0.28, z0 + h - 0.32):
        b.box(x - w / 2 + 0.02, dy - 0.012, hz, x + w * 0.28, dy + 0.002, hz + 0.05, 'Iron Black', 0.003)
        b.cyl((x + w * 0.28, dy - 0.006, hz + 0.025), (x + w * 0.28 + 0.06, dy - 0.006, hz + 0.025), 0.022, 'Iron Black', 6)
    if knock:
        b.torus((x + w * 0.3, dy - 0.035, z0 + 1.0), 0.05, 0.009, 'Iron', 12, 5, 'Y')
        b.cyl((x + w * 0.3, dy, z0 + 1.05), (x + w * 0.3, dy - 0.03, z0 + 1.05), 0.018, 'Iron', 6)
    if step and z0 >= 0.0:
        b.box(x - w / 2 - 0.15, y - 0.35, -0.05, x + w / 2 + 0.15, y + 0.02, max(z0, 0.12), 'Limestone', 0.02)
    if surround:
        t = 0.16
        b.box(x - w / 2 - t, y - 0.05, z0, x - w / 2, y + 0.02, z0 + h, surround, 0.012)
        b.box(x + w / 2, y - 0.05, z0, x + w / 2 + t, y + 0.02, z0 + h, surround, 0.012)
        b.box(x - w / 2 - t - 0.04, y - 0.07, z0 + h, x + w / 2 + t + 0.04, y + 0.02, z0 + h + 0.22, surround, 0.015)


def flame(b, base, h, r, mat='Flame', n=10, lean=(0.0, 0.0), seed=0.0):
    """Teardrop flame with normalised UVs (V 0 at the base -> 1 at the tip) for the flame shaders."""
    x, y, z = base
    prof = [(0.0, -0.05), (0.55, 0.06), (0.95, 0.22), (1.0, 0.36), (0.78, 0.55), (0.45, 0.75), (0.18, 0.9), (0.0, 1.0)]
    V, F, U = [], [], []
    for k, (rr, t) in enumerate(prof):
        for i in range(n):
            a = 2 * PI * i / n
            wob = 1.0 + 0.12 * math.sin(a * 3 + seed + t * 5)
            V.append((x + r * rr * wob * math.cos(a) + lean[0] * t * t * h, y + r * rr * wob * math.sin(a) + lean[1] * t * t * h, z + h * t))
    for k in range(len(prof) - 1):
        for i in range(n):
            j = (i + 1) % n
            F.append((k * n + i, k * n + j, (k + 1) * n + j, (k + 1) * n + i))
            U.append([(i / n, prof[k][1]), ((i + 1) / n, prof[k][1]), ((i + 1) / n, prof[k + 1][1]), (i / n, prof[k + 1][1])])
    b.mesh(V, F, mat, U, smooth=True)


def lantern(K, p, s=1.0, post=False):
    """Iron lantern, bottom centre p.  Night: candle flame + warm point light."""
    b = K.b
    x, y, z = p
    r = 0.1 * s
    hgt = 0.3 * s
    b.cyl((x, y, z), (x, y, z + 0.03 * s), r * 1.15, 'Iron Black', 8)
    for i in range(4):
        a = PI / 4 + i * PI / 2
        cx, cy = x + r * math.cos(a), y + r * math.sin(a)
        b.cbox((cx, cy, z + 0.03 * s + hgt / 2), (0.018 * s, 0.018 * s, hgt), 'Iron Black')
    for i in range(4):
        a0 = PI / 4 + i * PI / 2
        a1 = a0 + PI / 2
        p0 = (x + r * math.cos(a0), y + r * math.sin(a0))
        p1 = (x + r * math.cos(a1), y + r * math.sin(a1))
        b.quad((p0[0], p0[1], z + 0.03 * s), (p1[0], p1[1], z + 0.03 * s), (p1[0], p1[1], z + 0.03 * s + hgt),
               (p0[0], p0[1], z + 0.03 * s + hgt), 'Glass Clear')
    zt = z + 0.03 * s + hgt
    b.lathe([(r * 1.3, zt), (r * 1.3, zt + 0.02 * s), (r * 0.35, zt + 0.13 * s), (0.02 * s, zt + 0.16 * s)], 'Iron Black', 8, (x, y, 0),
            phase=PI / 4)     # roof cap centred on the lantern (was at the kit origin: stray caps, fixed Nov 27)
    b.torus((x, y, zt + 0.2 * s), 0.035 * s, 0.008 * s, 'Iron Black', 10, 4, 'Y')
    b.cyl((x, y, z + 0.03 * s), (x, y, z + 0.11 * s), 0.025 * s, 'Wax', 8)
    flame(K.n, (x, y, z + 0.11 * s), 0.07 * s, 0.018 * s, 'Flame Candle', 8)
    K.light((x, y, z + 0.16 * s), 70 * s, '#ff9a3c', 0.04 * s)


def wall_lantern(K, x, y, z, out=0.55):
    """Lantern hanging from an iron bracket fixed to a wall plane at y (normal -Y)."""
    b = K.b
    b.box(x - 0.05, y - 0.02, z - 0.35, x + 0.05, y, z + 0.08, 'Iron Black', 0.005)
    b.cyl((x, y, z), (x, y - out, z), 0.016, 'Iron Black', 6)
    b.cyl((x, y, z - 0.3), (x, y - out * 0.62, z - 0.01), 0.012, 'Iron Black', 6)
    b.torus((x, y - out * 0.35, z - 0.08), 0.06, 0.008, 'Iron Black', 12, 4, 'X')
    b.cyl((x, y - out + 0.02, z), (x, y - out + 0.02, z - 0.12), 0.006, 'Iron Black', 4)
    lantern(K, (x, y - out + 0.02, z - 0.6), 1.0)


def hanging_sign(K, x, y, z, icon, out=1.15):
    """Painted sign hanging from a bracket at height z on a wall plane at y; readable from the street."""
    b = K.b
    mname = sign_material(icon)
    b.box(x - 0.06, y - 0.02, z - 0.5, x + 0.06, y, z + 0.08, 'Iron Black', 0.005)
    b.cyl((x, y, z), (x, y - out, z), 0.02, 'Iron Black', 6)
    b.cyl((x, y, z - 0.45), (x, y - out * 0.6, z - 0.01), 0.014, 'Iron Black', 6)
    b.torus((x, y - out * 0.3, z - 0.12), 0.09, 0.01, 'Iron Black', 12, 4, 'X')
    b.sphere((x, y - out, z), 0.035, 'Iron Black', 8, 6)
    bw, bh, bt = 0.72, 0.52, 0.045
    cy = y - out * 0.58
    zt = z - 0.14
    if not hasattr(K, 'signs'):
        K.signs = []
    K.signs.append((icon, K.b.T @ Vector((x, cy, zt - bh / 2)), (K.b.T.to_3x3() @ Vector((1, 0, 0))).normalized()))
    for dy in (-bw * 0.36, bw * 0.36):
        b.cyl((x, cy + dy, z), (x, cy + dy, zt), 0.008, 'Iron Black', 4)
    zb = zt - bh
    y0, y1 = cy - bw / 2, cy + bw / 2
    b.cbox((x, cy, zt - bh / 2), (bt, bw, bh), 'Timber Oak', 0.01, faces_skip=((0, -1), (0, 1)))
    # painted faces (UV 0..1 so the image fills the board)
    b.quad((x + bt / 2 + 0.001, y0, zb), (x + bt / 2 + 0.001, y1, zb), (x + bt / 2 + 0.001, y1, zt), (x + bt / 2 + 0.001, y0, zt),
           mname, [(1, 0), (0, 0), (0, 1), (1, 1)])
    b.quad((x - bt / 2 - 0.001, y1, zb), (x - bt / 2 - 0.001, y0, zb), (x - bt / 2 - 0.001, y0, zt), (x - bt / 2 - 0.001, y1, zt),
           mname, [(1, 0), (0, 0), (0, 1), (1, 1)])


def flat_banner(K, x, y, ztop, design, length=2.6, width=0.95, notch=0.3, sway=0.04, bar='Gold'):
    """A heraldic banner hanging flat against a facade at y (normal -Y), from a rod at ztop."""
    b = K.b
    mname = banner_material(design)
    rng = K.rng
    ph = rng.uniform(0, 6.28)
    yy = y - 0.08

    def fn(s, t):
        bot = length - notch * (1 - abs(2 * s - 1))
        zz = ztop - t * bot
        wave = sway * math.sin(s * 6.28 * 1.2 + ph + t * 2.0) * (0.3 + 0.7 * t)
        return (x - width / 2 + s * width, yy - wave - 0.02 * t, zz)
    # build so the cloth faces -Y: s left->right, t top->bottom gives normal +Y, so flip t
    b.grid(6, 14, lambda s, t: fn(s, 1 - t), mname, (1.0, 1.0), smooth=True)
    b.cyl((x - width / 2 - 0.12, yy + 0.01, ztop + 0.02), (x + width / 2 + 0.12, yy + 0.01, ztop + 0.02), 0.022, bar, 8)
    for sx in (-1, 1):
        b.sphere((x + sx * (width / 2 + 0.14), yy + 0.01, ztop + 0.02), 0.04, bar, 8, 6)
        b.cyl((x + sx * (width / 2 + 0.08), yy + 0.01, ztop + 0.02), (x + sx * (width / 2 + 0.08), y, ztop + 0.02), 0.012, 'Iron Black', 5)


def pole_banner(K, x, y, z, design, out=1.3, length=1.6, width=0.7):
    """Banner on a pole sticking out of a facade at y (flag-like, readable from the side)."""
    b = K.b
    mname = banner_material(design)
    b.cyl((x, y, z), (x, y - out, z + 0.25), 0.03, 'Timber Oak', 8)
    b.sphere((x, y - out - 0.03, z + 0.26), 0.05, 'Gold', 8, 6)
    rng = K.rng
    ph = rng.uniform(0, 6.28)

    def fn(s, t):
        yy = y - 0.15 - s * (out - 0.25)
        zt = z + 0.04 + 0.25 * (0.15 + s * (out - 0.25)) / out
        bot = length - 0.25 * (1 - abs(2 * s - 1))
        return (x + 0.05 * math.sin(s * 5 + ph + t * 3) * t, yy, zt - t * bot)
    b.grid(6, 10, lambda s, t: fn(1 - s, t), mname, (1.0, 1.0), smooth=True, both=True)


def joists(b, x0, x1, y0, y1, z, mat='Timber Dark', step=0.5, s=0.14):
    n = max(2, int((x1 - x0) / step))
    for i in range(n + 1):
        xx = x0 + (x1 - x0) * i / n
        b.box(xx - s / 2, y0, z - s, xx + s / 2, y1, z, mat, 0.012)


# ==============================================================================================
# Roofs
# ==============================================================================================
def gable_roof(K, x0, x1, y0, y1, ze, pitch_deg, mat, ov=0.35, sag=0.08, thick=0.14, fascia='Timber Dark',
               ridge='Terracotta', soffit='Planks Grey', nu=10):
    """Duo-pitch roof, ridge along local Y from y0 to y1 (overhangs included), eaves at ze over the
    wall lines x0/x1.  Returns (ridge_z, function z_roof(x, y))."""
    b = K.b
    tn = math.tan(math.radians(pitch_deg))
    xc = (x0 + x1) / 2
    hw = (x1 - x0) / 2
    rh = hw * tn
    zl = ze - ov * tn
    span = hw + ov
    slope_len = span / math.cos(math.radians(pitch_deg))
    L = y1 - y0

    def P(side, s, t, off=0.0):
        yy = y0 + s * L
        x = xc + side * span * (1 - t)
        z = zl + t * (rh + ov * tn) - sag * math.sin(PI * s) * t
        n = Vector((side * math.sin(math.radians(pitch_deg)), 0, math.cos(math.radians(pitch_deg))))
        return Vector((x, yy, z)) + n * off

    for side in (1, -1):
        if side > 0:
            b.grid(nu, 3, lambda s, t: P(1, s, t), mat, (L, slope_len), smooth=False)
            b.grid(nu, 1, lambda s, t: P(1, 1 - s, t, -thick), soffit, (L, slope_len), smooth=False)
        else:
            b.grid(nu, 3, lambda s, t: P(-1, 1 - s, t), mat, (L, slope_len), smooth=False)
            b.grid(nu, 1, lambda s, t: P(-1, s, t, -thick), soffit, (L, slope_len), smooth=False)
        # fascia board along the eave and verge boards along the gables
        for i in range(nu):
            s0, s1 = i / nu, (i + 1) / nu
            a, c = P(side, s0, 0), P(side, s1, 0)
            b.beam(a + Vector((0, 0, -thick * 0.5)), c + Vector((0, 0, -thick * 0.5)), 0.05, thick + 0.06, fascia, 0.01)
        for s in (0.0, 1.0):
            pts = [P(side, s, t / 4) for t in range(5)]
            for a, c in zip(pts, pts[1:]):
                off = Vector((0, -0.03 if s == 0 else 0.03, -thick * 0.45))
                b.beam(a + off, c + off, 0.05, 0.3, fascia, 0.01)
    # ridge cap (half-round tiles) following the sag
    pts = [P(1, i / nu, 1.0) for i in range(nu + 1)]
    for a, c in zip(pts, pts[1:]):
        b.cyl(a + Vector((0, 0, 0.01)), c + Vector((0, 0, 0.01)), 0.1, ridge, 8)

    def zroof(x, y):
        s = min(max((y - y0) / L, 0), 1)
        t = 1 - min(abs(x - xc) / span, 1)
        return zl + t * (rh + ov * tn) - sag * math.sin(PI * s) * t
    return ze + rh, zroof


def gable_wall(K, x0, x1, ze, rh, y, mat, hole=None, timber=None, glass_lit=False):
    """Triangular gable (normal -Y) at plane y; optional attic window hole (w, z0, z1) centred."""
    b = K.b
    xc, hw = (x0 + x1) / 2, (x1 - x0) / 2

    def xl(z):
        return xc - hw * (1 - (z - ze) / rh)
    if not hole:
        b.poly([(x0, y, ze), (x1, y, ze), (xc, y, ze + rh)], mat)
    else:
        w, hz0, hz1 = hole
        a0, a1 = xl(hz0), xl(hz1)
        b.poly([(x0, y, ze), (x1, y, ze), (2 * xc - a0, y, hz0), (a0, y, hz0)], mat)
        b.poly([(a0, y, hz0), (xc - w / 2, y, hz0), (xc - w / 2, y, hz1), (a1, y, hz1)], mat)
        b.poly([(xc + w / 2, y, hz0), (2 * xc - a0, y, hz0), (2 * xc - a1, y, hz1), (xc + w / 2, y, hz1)], mat)
        b.poly([(a1, y, hz1), (2 * xc - a1, y, hz1), (xc, y, ze + rh)], mat)
        d = 0.16
        b.quad((xc + w / 2, y, hz0), (xc + w / 2, y + d, hz0), (xc - w / 2, y + d, hz0), (xc - w / 2, y, hz0), mat)
        b.quad((xc - w / 2, y + d, hz1), (xc + w / 2, y + d, hz1), (xc + w / 2, y, hz1), (xc - w / 2, y, hz1), mat)
        b.quad((xc - w / 2, y + d, hz0), (xc - w / 2, y + d, hz1), (xc - w / 2, y, hz1), (xc - w / 2, y, hz0), mat)
        b.quad((xc + w / 2, y, hz1), (xc + w / 2, y + d, hz1), (xc + w / 2, y + d, hz0), (xc + w / 2, y, hz0), mat)
        window(K, xc, hz0, w, hz1 - hz0, y, d, frame='Timber Oak', sill=None, lit=glass_lit)
    if timber:
        tw = 0.18
        zc = ze + rh * 0.42
        b.box(xl(zc) + 0.05, y - 0.04, zc - tw / 2, 2 * xc - xl(zc) - 0.05, y + 0.06, zc + tw / 2, timber, 0.015)
        if not hole:
            b.box(xc - tw / 2, y - 0.04, ze, xc + tw / 2, y + 0.06, ze + rh - 0.15, timber, 0.015)
            for sx in (-1, 1):
                b.beam((xc + sx * hw * 0.55, y - 0.02, ze + 0.1), (xc + sx * 0.12, y - 0.02, zc - 0.1), tw * 0.8, 0.1, timber, 0.012, up=(0, 1, 0))
        else:
            for sx in (-1, 1):
                b.box(xc + sx * (hole[0] / 2 + 0.05) - tw / 2, y - 0.04, ze, xc + sx * (hole[0] / 2 + 0.05) + tw / 2, y + 0.06,
                      min(hole[2] + 0.1, ze + rh * (1 - (hole[0] / 2 + 0.15) / hw) - 0.05), timber, 0.015)


def chimney(K, x, y, z0, z1, mat='Brick', pots=2):
    b = K.b
    b.box(x - 0.38, y - 0.32, z0, x + 0.38, y + 0.32, z1, mat, 0.02)
    b.box(x - 0.45, y - 0.39, z1 - 0.28, x + 0.45, y + 0.39, z1 - 0.16, 'Limestone', 0.015)
    b.box(x - 0.42, y - 0.36, z1, x + 0.42, y + 0.36, z1 + 0.08, 'Limestone', 0.015)
    for i in range(pots):
        px = x + (i - (pots - 1) / 2) * 0.32
        b.lathe([(0.1, z1 + 0.08), (0.12, z1 + 0.2), (0.09, z1 + 0.38), (0.11, z1 + 0.42), (0.08, z1 + 0.43)], 'Terracotta', 10,
                (px, y, 0), cap_top=False)
        b.lathe([(0.075, z1 + 0.43), (0.075, z1 + 0.3)], 'Charcoal', 10, (px, y, 0), cap_top=True)


# ==============================================================================================
# Houses
# ==============================================================================================
def _posts_for(L, holes, step, tw):
    """Post centre positions along a facade of length L avoiding hole spans."""
    xs = [tw / 2, L - tw / 2]
    for h0, h1, *_ in holes:
        xs += [h0 - tw / 2, h1 + tw / 2]
    xs = sorted(set(round(x, 4) for x in xs if tw / 2 - 1e-4 <= x <= L - tw / 2 + 1e-4))
    out = [xs[0]]
    for x in xs[1:]:
        gap = x - out[-1]
        if gap > step * 1.05:
            if not any(h0 - 0.01 < (out[-1] + x) / 2 < h1 + 0.01 for h0, h1, *_ in holes):
                n = int(gap / step + 0.5)
                base = out[-1]
                for i in range(1, n):
                    cand = base + gap * i / n
                    if not any(h0 - tw < cand < h1 + tw for h0, h1, *_ in holes):
                        out.append(cand)
        out.append(x)
    return sorted(set(out))


def timber_frame(K, L, z0, h, holes, mat, style='panels', y=0.0, rng=None):
    """Exposed framing on a facade (local frame: x 0..L, wall plane y, normal -Y).
    holes: [(x0, x1, zb, zt)] window/door openings (already cut in the plaster)."""
    b = K.b
    rng = rng or K.rng
    tw, dz = 0.2, 0.19
    yf, yb = y - 0.045, y + 0.06
    jit = lambda a=0.012: rng.uniform(-a, a)
    b.box(0, yf + jit(0.005), z0, L, yb, z0 + dz, mat, 0.015)                # sole plate
    b.box(0, yf + jit(0.005), z0 + h - dz, L, yb, z0 + h, mat, 0.015)        # top plate
    step = {'studs': 0.5, 'panels': 1.25, 'braced': 1.4}[style]
    posts = _posts_for(L, holes, step, tw)
    for px in posts:
        p = px + jit(0.01)
        b.beam((p, y + 0.008, z0 + dz), (p + jit(0.02), y + 0.008, z0 + h - dz), tw * rng.uniform(0.85, 1.05), 0.105, mat, 0.015, up=(0, -1, 0))
    zr = z0 + 0.88
    for a, c in zip(posts, posts[1:]):
        inhole = [hh for hh in holes if hh[0] >= a - 0.01 and hh[1] <= c + 0.01]
        if inhole:
            for hx0, hx1, hzb, hzt in inhole:
                if hzb > z0 + dz + 0.05:
                    b.box(a + tw / 2, yf + 0.005, hzb - 0.16, c - tw / 2, yb, hzb, mat, 0.012)
                if hzt < z0 + h - dz - 0.05:
                    b.box(a + tw / 2, yf + 0.005, hzt, c - tw / 2, yb, hzt + 0.17, mat, 0.012)
                    if style == 'studs':
                        continue
                    # short studs above the head
                    if c - a > 1.0 and z0 + h - dz - (hzt + 0.17) > 0.25:
                        m = (a + c) / 2
                        b.box(m - 0.08, yf + 0.01, hzt + 0.17, m + 0.08, yb, z0 + h - dz, mat, 0.012)
            continue
        if style == 'studs':
            b.box(a + tw / 2, yf + 0.01, zr - 0.08, c - tw / 2, yb, zr + 0.08, mat, 0.012)
            continue
        b.box(a + tw / 2, yf + 0.01, zr - 0.08, c - tw / 2, yb, zr + 0.08, mat, 0.012)
        if c - a > 0.7:
            if style == 'braced':
                # St Andrew's cross in the lower panel, single brace above
                b.beam((a + tw / 2, y + 0.0, z0 + dz), (c - tw / 2, y + 0.0, zr - 0.08), 0.15, 0.09, mat, 0.012, up=(0, -1, 0))
                b.beam((c - tw / 2, y + 0.002, z0 + dz), (a + tw / 2, y + 0.002, zr - 0.08), 0.15, 0.09, mat, 0.012, up=(0, -1, 0))
            if rng.random() < 0.8:
                if rng.random() < 0.5:
                    b.beam((a + tw / 2, y + 0.0, zr + 0.08), (c - tw / 2, y + 0.0, z0 + h - dz), 0.16, 0.09, mat, 0.012, up=(0, -1, 0))
                else:
                    b.beam((c - tw / 2, y + 0.0, zr + 0.08), (a + tw / 2, y + 0.0, z0 + h - dz), 0.16, 0.09, mat, 0.012, up=(0, -1, 0))


def corner_post(K, x, y, z0, z1, mat, s=0.26):
    K.b.box(x - s / 2, y - s / 2, z0, x + s / 2, y + s / 2, z1, mat, 0.02)


def quoins(K, x, y, z0, z1, sx, mat='Limestone'):
    """Alternating corner stones at a corner (x, y) of a stone ground floor; sx = +1 right corner."""
    b = K.b
    z = z0
    k = 0
    while z < z1 - 0.1:
        hh = min(0.3, z1 - z)
        lx, ly = (0.45, 0.25) if k % 2 == 0 else (0.25, 0.45)
        b.box(x - (lx if sx > 0 else -0.05) if sx > 0 else x - 0.05, y - 0.05, z,
              x + 0.05 if sx > 0 else x + lx, y + ly, z + hh - 0.012, mat, 0.015)
        z += hh
        k += 1


FACES = ('front', 'right', 'back', 'left')


def _frame_of(face, W, D, yk):
    """Transform (loc, rz, length) of a facade frame: local x 0..L along the wall, wall plane y=0, normal -Y."""
    if face == 'front':
        return (-W / 2, yk, 0), 0.0, W
    if face == 'right':
        return (W / 2, yk, 0), PI / 2, D - yk
    if face == 'back':
        return (W / 2, D, 0), PI, W
    return (-W / 2, D, 0), -PI / 2, D - yk


def townhouse(K, P):
    """Half-timbered town house.  Local frame: street facade on y=0 (normal -Y), x in [-W/2, W/2],
    house runs to y=D.  P keys: W, D, floors[list], jetty, ground('stone'|'timber'|'shop'),
    stone, plaster, timber, style, roof('gable'|'eaves'), roof_mat, pitch, door_x, door_paint, shutters,
    win (list per floor of window centres, relative to the facade centre), win_w, flowers, sign, sign_x,
    lantern_x, banner, chimney, sides ('both'|'left'|'right'|None: side facades that get windows), lit."""
    b = K.b
    rng = K.rng
    W, D = P['W'], P['D']
    fl = P['floors']
    n = len(fl)
    jet = P.get('jetty', 0.35)
    zs = [0.0]
    for h in fl[:-1]:
        zs.append(zs[-1] + h)
    ze = zs[-1] + fl[-1]
    plaster = P.get('plaster', 'Plaster Cream')
    timber = P.get('timber', 'Timber Dark')
    stone = P.get('stone', 'Rubble')
    ground = P.get('ground', 'stone')
    style = P.get('style', 'panels')
    shut = P.get('shutters', 'Paint Green')
    win_w = P.get('win_w', 0.8)
    lit_p = P.get('lit', 0.6)
    vstart = len(b.V)
    for k in range(n):
        z0, h = zs[k], fl[k]
        yk = -jet * k
        stone_floor = (k == 0 and ground in ('stone', 'shop'))
        wall_mat = stone if stone_floor else plaster
        depth = 0.32 if stone_floor else 0.18
        for face in FACES:
            if face == 'back' and not P.get('back', False):
                loc, rz, L = _frame_of(face, W, D, yk)
                with K.push(loc, rz):
                    b.quad((0, 0, z0), (L, 0, z0), (L, 0, z0 + h), (0, 0, z0 + h), wall_mat)
                continue
            loc, rz, L = _frame_of(face, W, D, yk)
            holes, items = [], []
            if face == 'front':
                cx = W / 2
                if k == 0:
                    dx = cx + P.get('door_x', -W * 0.22)
                    dw, dh = P.get('door_w', 1.05), P.get('door_h', 2.15)
                    holes.append((dx - dw / 2, dx + dw / 2, 0.12, 0.12 + dh))
                    items.append(('door', dx, dw, dh))
                    if ground == 'shop':
                        sx = cx + P.get('shop_x', W * 0.18)
                        sw = P.get('shop_w', 2.0)
                        holes.append((sx - sw / 2, sx + sw / 2, 0.85, 2.3))
                        items.append(('shop', sx, sw))
                    for wx in P.get('gwin', []):
                        holes.append((cx + wx - win_w / 2, cx + wx + win_w / 2, 0.95, 2.1))
                        items.append(('win', cx + wx, win_w, 1.15, 0.95))
                else:
                    wins = P.get('win', [[]] * n)[k] if k < len(P.get('win', [])) else []
                    for wx in wins:
                        wh = min(1.25, h - 1.2)
                        holes.append((cx + wx - win_w / 2, cx + wx + win_w / 2, z0 + 0.85, z0 + 0.85 + wh))
                        items.append(('win', cx + wx, win_w, wh, z0 + 0.85))
            elif face in ('left', 'right') and P.get('sides') in (face, 'both') and k > 0:
                for wx in (L * 0.35, L * 0.72):
                    wh = min(1.15, h - 1.2)
                    holes.append((wx - 0.35, wx + 0.35, z0 + 0.9, z0 + 0.9 + wh))
                    items.append(('win', wx, 0.7, wh, z0 + 0.9))
            with K.push(loc, rz):
                b.wall(0, L, z0, z0 + h, wall_mat, holes, 0.0, depth, wall_mat)
                if not stone_floor:
                    hl = [(hh[0], hh[1], hh[2], hh[3]) for hh in holes]
                    timber_frame(K, L, z0, h, hl, timber, style if face == 'front' else 'panels')
                for it in items:
                    if it[0] == 'door':
                        _, dx, dw, dh = it
                        door(K, dx, dw, dh, 0.0, depth, P.get('door_paint', 'Paint Red'), 0.12,
                             surround='Limestone' if stone_floor else None)
                    elif it[0] == 'win':
                        _, wx, ww, wh, wz = it
                        window(K, wx, wz, ww, wh, 0.0, depth, frame='Timber Oak',
                               sill='Limestone' if stone_floor else 'Timber Dark',
                               shutters=shut if (face == 'front' and rng.random() < 0.85) else None,
                               flower=(face == 'front' and P.get('flowers', True) and rng.random() < 0.6),
                               lit=rng.random() < lit_p)
                    elif it[0] == 'shop':
                        _, sx, sw = it
                        shopfront(K, sx, sw, depth, timber, P.get('goods', 'bread'))
                if stone_floor and face == 'front':
                    quoins(K, 0.0, 0.0, 0.0, h, -1)
                    quoins(K, L, 0.0, 0.0, h, 1)
        # jetty: soffit, joist ends, brackets
        if k > 0 and jet > 0:
            yp = -jet * (k - 1)
            b.quad((-W / 2, yk, z0), (-W / 2, yp, z0), (W / 2, yp, z0), (W / 2, yk, z0), 'Planks Grey')
            joists(b, -W / 2 + 0.15, W / 2 - 0.15, yk - 0.05, yp, z0, timber, 0.48)
            b.box(-W / 2 - 0.02, yk - 0.07, z0 - 0.02, W / 2 + 0.02, yk + 0.12, z0 + 0.2, timber, 0.02)
            for sx in (-1, 1):
                bx = sx * (W / 2 - 0.15)
                b.beam((bx, yp + 0.05, z0 - 0.85), (bx, yk + 0.05, z0 - 0.05), 0.16, 0.16, timber, 0.015, up=(1, 0, 0))
        if k > 0 or ground == 'timber':
            for x, y in ((-W / 2, yk), (W / 2, yk)):
                corner_post(K, x, y, z0, z0 + h, timber)
        if k == 0 and ground == 'timber':
            b.box(-W / 2 - 0.06, -0.06, 0, W / 2 + 0.06, D + 0.06, 0.32, 'Rubble', 0.02)
    # roof
    yT = -jet * (n - 1)
    pitch = P.get('pitch', 52)
    rmat = P.get('roof_mat', 'Roof Clay')
    ov = P.get('overhang', 0.4)
    sag = P.get('sag', rng.uniform(0.04, 0.12))
    if P.get('roof', 'gable') == 'gable':
        yg = yT - P.get('gable_jetty', 0.15)
        rz_top, zf = gable_roof(K, -W / 2, W / 2, yg - 0.45, D + 0.3, ze, pitch, rmat, ov, sag)
        rh = rz_top - ze
        if P.get('gable_jetty', 0.15) > 0:
            gj = P.get('gable_jetty', 0.15)
            b.quad((-W / 2, yg, ze), (-W / 2, yT, ze), (W / 2, yT, ze), (W / 2, yg, ze), 'Planks Grey')
            b.box(-W / 2 - 0.02, yg - 0.07, ze - 0.02, W / 2 + 0.02, yg + 0.12, ze + 0.2, timber, 0.02)
        attic = (0.62, ze + rh * 0.18, ze + rh * 0.18 + 0.75) if rh > 1.8 else None
        gable_wall(K, -W / 2, W / 2, ze, rh, yg, plaster, attic, timber, rng.random() < lit_p * 0.6)
        with K.push((0, D, 0), PI):
            gable_wall(K, -W / 2, W / 2, ze, rh, 0, plaster, None, timber)
        if P.get('chimney', True):
            cx = P.get('chimney_x', W * 0.18)
            cy = D * 0.65
            chimney(K, cx, cy, ze - 0.5, rz_top + 0.9)
    else:
        # ridge parallel to the street: build in a frame where local Y = world X
        depth_total = D - yT
        with K.push((0, yT, 0), -PI / 2):
            # local x = -world y... map: local (x,y) -> world (y, -x) + offset; local x in [-depth, 0]
            rz_top, zf = gable_roof(K, -depth_total, 0, -W / 2 - 0.3, W / 2 + 0.3, ze, pitch, rmat, ov, sag)
            rh = rz_top - ze
            for sgn, yy in ((-1, -W / 2), (1, W / 2)):
                if sgn > 0:
                    with K.push((0, yy, 0), PI):
                        gable_wall(K, 0, depth_total, ze, rh, 0, plaster, None, timber)
                else:
                    gable_wall(K, -depth_total, 0, ze, rh, yy, plaster, None, timber)
        if P.get('dormer', False):
            dormer(K, P.get('dormer_x', 0.0), yT, ze, pitch, rmat, plaster, timber, rng.random() < lit_p)
        if P.get('chimney', True):
            chimney(K, P.get('chimney_x', -W * 0.3), yT + depth_total * 0.5, ze - 0.5, rz_top + 0.9)
    # extras on the facade
    if P.get('sign'):
        hanging_sign(K, P.get('sign_x', W / 2 - 0.4) * (1 if P.get('sign_x', 1) >= 0 else 1), -jet * min(1, n - 1), zs[min(1, n - 1)] + 0.35, P['sign'])
    if P.get('lantern_x') is not None:
        wall_lantern(K, P['lantern_x'], 0.0, 2.75)
    if P.get('banner'):
        kb = min(2, n - 1)
        flat_banner(K, P.get('banner_x', 0.0), -jet * kb - 0.05, zs[kb] + fl[kb] - 0.15, P['banner'], length=min(2.6, fl[kb] + 0.4))
    # lean / settle the whole house a little
    lx, ly = P.get('lean', (rng.uniform(-0.008, 0.008), rng.uniform(-0.006, 0.01)))
    for i in range(vstart, len(b.V)):
        v = b.V[i]
        b.V[i] = v + Vector((lx * v.z, ly * v.z, 0))
    return ze


def dormer(K, x, yT, ze, pitch, rmat, plaster, timber, lit):
    b = K.b
    tn = math.tan(math.radians(pitch))
    w, h = 1.3, 1.25
    yb = yT + 0.6                      # front face of dormer
    z0 = ze + 0.6 * tn - 0.2
    depth = 1.6
    with K.push((x, 0, 0)):
        b.wall(-w / 2, w / 2, z0, z0 + h, plaster, [(-0.35, 0.35, z0 + 0.2, z0 + 1.0)], yb, 0.12, plaster)
        window(K, 0.0, z0 + 0.2, 0.7, 0.8, yb, 0.12, sill=None, lit=lit, shutters=None)
        for sx in (-1, 1):
            b.quad((sx * w / 2, yb, z0 - 0.5), (sx * w / 2, yb + depth, z0 + h), (sx * w / 2, yb, z0 + h), (sx * w / 2, yb, z0 - 0.5), plaster)
        corner_post(K, -w / 2, yb, z0 - 0.3, z0 + h, timber, 0.16)
        corner_post(K, w / 2, yb, z0 - 0.3, z0 + h, timber, 0.16)
        with K.push((0, yb - 0.3, 0)):
            gable_roof(K, -w / 2, w / 2, 0.0, depth + 0.3, z0 + h, 45, rmat, 0.2, 0.0, 0.1, nu=3)
        gable_wall(K, -w / 2, w / 2, z0 + h, w / 2, yb, plaster)


def shopfront(K, x, w, depth, timber, goods='bread'):
    """Open shop window: fold-down counter board, prop-up shutter awning, goods on the counter."""
    b = K.b
    rng = K.rng
    x0, x1 = x - w / 2, x + w / 2
    # counter (fold-down shutter) on brackets
    b.box(x0, -0.55, 0.82, x1, depth * 0.6, 0.88, 'Planks', 0.01)
    for bx in (x0 + 0.15, x1 - 0.15):
        b.beam((bx, 0.0, 0.45), (bx, -0.5, 0.82), 0.06, 0.06, timber, 0.01, up=(1, 0, 0))
    # upper shutter propped as an awning
    b.beam((x0, 0.0, 2.32), (x0, -0.75, 2.62), 0.05, 0.05, timber, 0.01)
    b.beam((x1, 0.0, 2.32), (x1, -0.75, 2.62), 0.05, 0.05, timber, 0.01)
    with K.push((x, -0.02, 2.3), rx=math.radians(-68)):
        b.box(-w / 2 - 0.05, 0, 0, w / 2 + 0.05, 0.04, 0.85, 'Paint Yellow' if rng.random() < 0.5 else 'Paint Blue', 0.006)
    # dark interior behind
    b.quad((x0, depth + 0.6, 0.85), (x1, depth + 0.6, 0.85), (x1, depth + 0.6, 2.3), (x0, depth + 0.6, 2.3), 'Charcoal')
    for sx in (x0, x1):
        b.quad((sx, depth, 0.85), (sx, depth + 0.6, 0.85), (sx, depth + 0.6, 2.3), (sx, depth, 2.3), 'Planks Grey')
    b.quad((x0, depth + 0.6, 2.3), (x1, depth + 0.6, 2.3), (x1, depth, 2.3), (x0, depth, 2.3), 'Planks Grey')
    # goods
    with K.push((0, 0, 0.88)):
        goods_on(K, x0 + 0.1, x1 - 0.1, -0.5, 0.05, goods)


def goods_on(K, x0, x1, y0, y1, kind):
    b = K.b
    rng = K.rng
    if kind == 'bread':
        nx = int((x1 - x0) / 0.24)
        for i in range(nx):
            for j in range(2):
                px = x0 + 0.12 + i * 0.24 + rng.uniform(-0.02, 0.02)
                py = y0 + 0.12 + j * 0.26
                b.sphere((px, py, 0.05), 0.1, 'Bread', 10, 6, (1.2, 0.75, 0.55), deform=lambda v: v)
    elif kind == 'fruit':
        crate_of(K, (x0 + x1) / 2 - 0.35, (y0 + y1) / 2, 0.0, 'Apple Red')
        crate_of(K, (x0 + x1) / 2 + 0.35, (y0 + y1) / 2, 0.0, 'Apple Green')
    elif kind == 'cloth':
        nx = int((x1 - x0) / 0.2)
        cols = ['Cloth Red', 'Cloth Blue', 'Cloth Yellow', 'Cloth Green', 'Cloth White', 'Velvet Purple']
        for i in range(nx):
            px = x0 + 0.1 + i * 0.2
            b.cyl((px, y0 + 0.05, 0.08), (px, y1 - 0.02, 0.08), 0.08, cols[i % len(cols)], 10)
    elif kind == 'pots':
        for i in range(int((x1 - x0) / 0.25)):
            px = x0 + 0.13 + i * 0.25
            b.lathe([(0.0, 0), (0.07, 0.0), (0.1, 0.08), (0.08, 0.17), (0.05, 0.2), (0.06, 0.23)], 'Terracotta', 10,
                    (px, (y0 + y1) / 2, 0), cap_bot=True, cap_top=False)


# ==============================================================================================
# Props
# ==============================================================================================
def barrel(K, x, y, z=0.0, r=0.3, h=0.86, lid=True, tilt=None):
    b = K.b
    prof = []
    for i in range(9):
        t = i / 8
        prof.append((r * (0.86 + 0.14 * math.sin(PI * t)), h * t))
    with K.push((x, y, z), rz=K.rng.uniform(0, 6.28), **({'rx': tilt} if tilt else {})):
        base = len(b.F)
        b.lathe(prof, 'Planks', 18, (0, 0, 0), cap_top=False)
        # swap UVs on the staves so boards run vertically (grain along height)
        for i in range(base, len(b.F)):
            idx, m, uv, sm, g = b.F[i]
            if uv:
                b.F[i] = (idx, m, [(vv, uu) for uu, vv in uv], sm, g)
        for t in (0.1, 0.3, 0.7, 0.9):
            rr = r * (0.86 + 0.14 * math.sin(PI * t)) + 0.006
            b.lathe([(rr, h * t - 0.025), (rr + 0.004, h * t), (rr, h * t + 0.025)], 'Iron', 18, (0, 0, 0), cap_top=False)
        if lid:
            b.cyl((0, 0, h * 0.94), (0, 0, h * 0.96), r * 0.86, 'Planks Pale', 16)


def crate(K, x, y, z=0.0, s=(0.6, 0.45, 0.4), rz=None, mat='Planks Pale', open_top=False):
    b = K.b
    rz = K.rng.uniform(-0.25, 0.25) if rz is None else rz
    sx, sy, sz = s
    with K.push((x, y, z), rz=rz):
        t = 0.025
        for zz in (0.02, sz * 0.5 + 0.01):
            for side in (-1, 1):
                b.box(-sx / 2, side * sy / 2 - t / 2, zz, sx / 2, side * sy / 2 + t / 2, zz + sz * 0.45, mat, 0.004)
                b.box(side * sx / 2 - t / 2, -sy / 2, zz, side * sx / 2 + t / 2, sy / 2, zz + sz * 0.45, mat, 0.004)
        for cx in (-1, 1):
            for cy in (-1, 1):
                b.box(cx * sx / 2 - 0.035, cy * sy / 2 - 0.035, 0, cx * sx / 2 + 0.035, cy * sy / 2 + 0.035, sz, mat, 0.006)
        b.box(-sx / 2 + 0.02, -sy / 2 + 0.02, 0.0, sx / 2 - 0.02, sy / 2 - 0.02, 0.03, mat, 0.004)
        if not open_top:
            for i in range(4):
                yy = -sy / 2 + sy * (i + 0.5) / 4
                b.box(-sx / 2, yy - sy / 9, sz, sx / 2, yy + sy / 9 - 0.01, sz + 0.022, mat, 0.004)


def crate_of(K, x, y, z, fruit, s=(0.55, 0.4, 0.28)):
    crate(K, x, y, z, s, open_top=True)
    b = K.b
    rng = K.rng
    sx, sy, sz = s
    rz = 0.0
    nx, ny = int(sx / 0.085), int(sy / 0.085)
    for layer in range(2):
        for i in range(nx - layer):
            for j in range(ny - layer):
                px = x - sx / 2 + 0.06 + (i + layer * 0.5) * (sx - 0.12) / max(nx - 1, 1) + rng.uniform(-0.01, 0.01)
                py = y - sy / 2 + 0.06 + (j + layer * 0.5) * (sy - 0.12) / max(ny - 1, 1) + rng.uniform(-0.01, 0.01)
                pz = z + sz - 0.04 + layer * 0.06 + rng.uniform(-0.005, 0.01)
                if fruit == 'Cabbage':
                    b.sphere((px, py, pz), 0.07, 'Cabbage', 8, 6, (1, 1, 0.85))
                elif fruit == 'Pumpkin':
                    b.sphere((px, py, pz), 0.09, 'Pumpkin', 10, 6, (1, 1, 0.7))
                else:
                    b.sphere((px, py, pz), 0.042, fruit, 8, 6, (1, 1, 0.92))


def pumpkin(K, x, y, z, r=0.2):
    def d(v):
        a = math.atan2(v.y, v.x)
        return v * (1 + 0.06 * math.cos(a * 8))
    K.b.sphere((x, y, z + r * 0.68), r, 'Pumpkin', 16, 8, (1, 1, 0.68), deform=d)
    K.b.cyl((x, y, z + r * 1.3), (x + 0.01, y, z + r * 1.5), 0.02, 'Timber Oak', 6)


def hay_bale(K, x, y, z=0.0, rz=0.0, s=(0.9, 0.45, 0.4)):
    b = K.b
    with K.push((x, y, z), rz=rz):
        b.cbox((0, 0, s[2] / 2), s, 'Hay', 0.06)
        for t in (-0.25, 0.25):
            b.cbox((t * s[0], 0, s[2] / 2), (0.015, s[1] + 0.01, s[2] + 0.01), 'Rope', 0.005)


def hay_pile(K, x, y, z, r=0.8, h=0.6):
    rng = K.rng
    seed = rng.random() * 10

    def d(v):
        n = math.sin(v.x * 9 + seed) * math.cos(v.y * 7 + seed) * 0.08 + math.sin(v.x * 23 + v.y * 19) * 0.03
        vv = Vector((v.x, v.y, max(v.z, -0.02)))
        return vv * (1 + n)
    K.b.sphere((x, y, z), r, 'Hay', 20, 10, (1, 1, h / r), deform=d)


def cart(K, x, y, rz=0.0, load='hay'):
    b = K.b
    rng = K.rng
    with K.push((x, y, 0), rz=rz):
        L, Wd, zb = 2.4, 1.3, 0.75
        b.box(-L / 2, -Wd / 2, zb, L / 2, Wd / 2, zb + 0.08, 'Planks Grey', 0.01)
        for sx in (-1, 1):
            b.box(-L / 2, sx * Wd / 2 - 0.03, zb + 0.08, L / 2, sx * Wd / 2 + 0.03, zb + 0.4, 'Planks Grey', 0.008)
            for k in range(5):
                px = -L / 2 + 0.05 + k * (L - 0.1) / 4
                b.box(px - 0.04, sx * Wd / 2 - 0.05, zb - 0.05, px + 0.04, sx * Wd / 2 + 0.05, zb + 0.48, 'Timber Oak', 0.008)
        b.box(-L / 2 - 0.03, -Wd / 2, zb + 0.08, -L / 2 + 0.03, Wd / 2, zb + 0.35, 'Planks Grey', 0.008)
        # axle + wheels
        b.cyl((0.1, -Wd / 2 - 0.25, 0.62), (0.1, Wd / 2 + 0.25, 0.62), 0.05, 'Timber Dark', 8)
        for sx in (-1, 1):
            wy = sx * (Wd / 2 + 0.15)
            R = 0.62
            prof = [(R - 0.07, -0.05), (R, -0.05), (R, 0.05), (R - 0.07, 0.05)]
            with K.push((0.1, wy, R), rx=PI / 2):
                b.lathe(prof + [(R - 0.07, -0.05)], 'Timber Oak', 24, (0, 0, 0), cap_top=False, smooth=False)
                b.lathe([(R + 0.012, -0.045), (R + 0.012, 0.045)], 'Iron', 24, (0, 0, 0), cap_top=False)
                b.cyl((0, 0, -0.09), (0, 0, 0.09), 0.1, 'Timber Dark', 10)
                for k in range(10):
                    a = 2 * PI * k / 10
                    b.beam((0.09 * math.cos(a), 0.09 * math.sin(a), 0), ((R - 0.06) * math.cos(a), (R - 0.06) * math.sin(a), 0),
                           0.04, 0.05, 'Timber Oak', 0.006)
        # shafts resting on the ground
        for sx in (-1, 1):
            b.beam((L / 2 - 0.2, sx * 0.4, zb), (L / 2 + 1.7, sx * 0.45, 0.06), 0.08, 0.08, 'Timber Oak', 0.012)
        if load == 'hay':
            hay_pile(K, -0.1, 0.0, zb + 0.15, 1.15, 0.7)
        elif load == 'barrels':
            barrel(K, -0.55, -0.3, zb + 0.08, 0.26, 0.75)
            barrel(K, -0.55, 0.32, zb + 0.08, 0.26, 0.75)
            barrel(K, 0.2, 0.0, zb + 0.08, 0.26, 0.75)
        elif load == 'produce':
            for i, f in enumerate(('Apple Red', 'Cabbage', 'Apple Green')):
                crate_of(K, -0.7 + i * 0.68, 0.0, zb + 0.08, f, (0.6, 0.45, 0.3))


def stall(K, x, y, rz=0.0, canvas='Canvas Red', goods=('fruit',), w=2.6, d=1.4):
    """Market stall: posts, counter, back shelf, striped awning with scalloped valance."""
    b = K.b
    rng = K.rng
    with K.push((x, y, 0), rz=rz):
        hf, hb = 2.45, 2.85        # awning front / back heights
        for px in (-w / 2, w / 2):
            b.beam((px, -d / 2, 0), (px + rng.uniform(-0.02, 0.02), -d / 2, hf), 0.09, 0.09, 'Timber Oak', 0.012)
            b.beam((px, d / 2, 0), (px, d / 2, hb), 0.09, 0.09, 'Timber Oak', 0.012)
            b.beam((px, -d / 2, hf), (px, d / 2, hb), 0.07, 0.07, 'Timber Oak', 0.01)
        # counter
        b.box(-w / 2 + 0.05, -d / 2 - 0.05, 0.86, w / 2 - 0.05, -d / 2 + 0.6, 0.92, 'Planks', 0.01)
        b.box(-w / 2 + 0.05, -d / 2 - 0.02, 0.0, w / 2 - 0.05, -d / 2 + 0.02, 0.86, 'Planks Pale', 0.005)
        # back shelf
        b.box(-w / 2 + 0.05, d / 2 - 0.4, 1.15, w / 2 - 0.05, d / 2 - 0.05, 1.19, 'Planks', 0.01)
        b.box(-w / 2 + 0.05, d / 2 - 0.05, 0.0, w / 2 - 0.05, d / 2, 1.6, 'Planks Grey', 0.005)
        # awning cloth (sags between posts)
        ov = 0.35

        def aw(s, t):
            xx = -w / 2 - 0.1 + s * (w + 0.2)
            yy = -d / 2 - ov + t * (d + ov + 0.1)
            zz = hf + 0.05 - 0.12 + (hb - hf + 0.12) * min(1, (t * (d + ov + 0.1)) / (d + ov)) - 0.08 * math.sin(PI * s) * math.sin(PI * t)
            return (xx, yy, zz)
        b.grid(12, 6, lambda s, t: aw(s, 1 - t) if False else aw(s, t), canvas, (w + 0.2, d + ov + 0.1), smooth=True, both=True)
        # scalloped valance on the front edge
        nsc = 8
        for i in range(nsc):
            s0 = i / nsc

            def val(s, t, s0=s0):
                ss = s0 + s / nsc
                p = aw(ss, 0)
                drop = 0.18 + 0.1 * math.sin(PI * s)
                return (p[0], p[1] - 0.005, p[2] - t * drop)
            b.grid(4, 1, val, canvas, ((w + 0.2) / nsc, 0.25), smooth=True, both=True)
        # goods
        with K.push((0, 0, 0.92)):
            span = (w - 0.3) / len(goods)
            for i, gk in enumerate(goods):
                gx0 = -w / 2 + 0.15 + i * span
                goods_on(K, gx0, gx0 + span, -d / 2 - 0.02, -d / 2 + 0.55, gk)
        for i in range(3):
            barrel(K, -w / 2 + 0.4 + i * 0.6, d / 2 + 0.45 + rng.uniform(-0.1, 0.1), 0.0, 0.26, 0.75) if rng.random() < 0.5 else \
                crate(K, -w / 2 + 0.4 + i * 0.6, d / 2 + 0.4, 0.0)


def lamp_post(K, x, y, h=3.2):
    b = K.b
    b.lathe([(0.2, 0), (0.2, 0.12), (0.12, 0.2), (0.08, 0.45), (0.06, 0.5)], 'Ashlar Grey', 12, (x, y, 0))
    b.cyl((x, y, 0.4), (x, y, h), 0.045, 'Iron Black', 10)
    for a in range(4):
        ang = a * PI / 2
        b.torus((x + 0.12 * math.cos(ang), y + 0.12 * math.sin(ang), h - 0.25), 0.1, 0.01, 'Iron Black', 10, 4, 'Z' if False else 'Y')
    b.cyl((x, y, h - 0.05), (x, y, h + 0.02), 0.12, 'Iron Black', 8)
    lantern(K, (x, y, h + 0.02), 1.25)


def well(K, x, y):
    b = K.b
    b.lathe([(0.9, 0), (0.9, 0.85), (0.98, 0.9), (0.98, 1.0), (0.72, 1.0), (0.72, 0.2)], 'Rubble', 20, (x, y, 0), cap_top=False)
    for sx in (-1, 1):
        b.beam((x + sx * 0.85, y, 0.9), (x + sx * 0.85, y, 2.4), 0.14, 0.14, 'Timber Dark', 0.015)
    b.cyl((x - 1.0, y, 2.1), (x + 1.0, y, 2.1), 0.07, 'Timber Oak', 10)
    with K.push((x, y, 2.4)):
        gable_roof(K, -1.05, 1.05, -0.8, 0.8, 0.0, 40, 'Roof Shingle', 0.25, 0.0, 0.06, nu=3)


def fountain(K, x, y, r=3.0, lit=False):
    """Two-tier stone fountain on a stepped plinth with a pool (basin rim ~0.75 m)."""
    b = K.b
    with K.push((x, y, 0)):
        b.lathe([(r + 0.7, -0.02), (r + 0.7, 0.13), (r + 0.35, 0.13), (r + 0.35, 0.25)], 'Flagstones', 40, cap_top=True)
        b.lathe([(r, 0.25), (r, 0.62)], 'Ashlar Grey', 48, cap_top=False)
        b.lathe([(r - 0.04, 0.6), (r + 0.1, 0.62), (r + 0.12, 0.7), (r + 0.05, 0.76), (r - 0.38, 0.76), (r - 0.4, 0.7), (r - 0.34, 0.62)],
                'Limestone', 48, cap_top=False)
        b.lathe([(r - 0.34, 0.62), (r - 0.34, 0.26)], 'Ashlar Grey', 48, cap_top=False)
        b.lathe([(r - 0.34, 0.27)], 'Moss', 40, cap_top=True)
        b.lathe([(r - 0.35, 0.29), (r - 0.35, 0.58)], 'Water Still', 48, cap_top=True, cap_bot=True)
        # pedestal + lower bowl
        b.lathe([(0.7, 0.26), (0.7, 0.45), (0.5, 0.58), (0.36, 0.64), (0.28, 0.8), (0.26, 1.35), (0.32, 1.45), (0.45, 1.5)],
                'Limestone', 24, cap_top=False)
        R1 = 1.35
        b.lathe([(0.45, 1.5), (0.85, 1.55), (1.2, 1.72), (R1, 1.92), (R1 + 0.05, 1.98), (R1 - 0.1, 1.98), (1.1, 1.8), (0.0, 1.76)],
                'Limestone', 36, cap_top=False)
        b.lathe([(R1 - 0.11, 1.9), (0.0, 1.9)], 'Water Thin', 36, cap_top=False)
        b.lathe([(0.2, 1.8), (0.16, 2.0), (0.14, 2.55), (0.2, 2.65), (0.5, 2.75), (0.62, 2.92), (0.55, 2.94), (0.0, 2.86)],
                'Limestone', 20, cap_top=False)
        b.lathe([(0.53, 2.89), (0.0, 2.89)], 'Water Thin', 20, cap_top=False)
        b.lathe([(0.11, 2.86), (0.09, 3.1), (0.15, 3.2), (0.09, 3.32), (0.04, 3.48), (0.0, 3.54)], 'Brass', 12, cap_top=False)
        # overflow ribbons (separate streams, not a dome)
        for (r0, z0, r1, z1, nrib, wdeg) in ((0.62, 2.93, 0.86, 1.91, 9, 13.0), (R1 + 0.05, 1.97, R1 + 0.45, 0.58, 16, 9.0)):
            for k in range(nrib):
                a0 = 2 * PI * k / nrib + K.rng.uniform(-0.05, 0.05)
                aw = math.radians(wdeg) * K.rng.uniform(0.7, 1.1)

                def sheet(s, t, r0=r0, z0=z0, r1=r1, z1=z1, a0=a0, aw=aw):
                    a = a0 + (s - 0.5) * aw * (1 - 0.45 * t)
                    rr = r0 + (r1 - r0) * (t ** 0.55)
                    zz = z0 - (z0 - z1) * (t ** 1.7)
                    return (rr * math.cos(a), rr * math.sin(a), zz)
                b.grid(3, 6, sheet, 'Water Falling', (r0 * aw, z0 - z1), smooth=True, both=True)
                # foam ring where each stream lands
                a = a0
                b.sphere((r1 * math.cos(a), r1 * math.sin(a), z1 + 0.005), 0.12 if z1 < 1 else 0.07, 'Foam', 8, 4, (1.3, 1.3, 0.25))
    return (x, y)


def ranking_board(K, x, y, rz, plaques=10, header=True):
    """Big wooden ranking board with blank name plaques (each a separate object) under a little roof.
    Returns list of (name, centre (local m), size) for plaques so the set can split them out."""
    b = K.b
    W, H, zb = 3.4, 2.6, 0.9
    out = []
    with K.push((x, y, 0), rz=rz):
        for sx in (-1, 1):
            px = sx * (W / 2 + 0.12)
            b.box(px - 0.3, -0.3, 0, px + 0.3, 0.3, 0.35, 'Ashlar Grey', 0.03)
            b.beam((px, 0, 0.35), (px, 0, zb + H + 0.6), 0.22, 0.22, 'Timber Dark', 0.02)
        b.box(-W / 2, -0.02, zb, W / 2, 0.1, zb + H, 'Planks', 0.01)
        for zz in (zb - 0.08, zb + H):
            b.box(-W / 2 - 0.12, -0.08, zz, W / 2 + 0.12, 0.12, zz + 0.12, 'Timber Dark', 0.015)
        for sx in (-1, 1):
            b.box(sx * W / 2 - 0.06, -0.08, zb, sx * W / 2 + 0.06, 0.12, zb + H, 'Timber Dark', 0.015)
        # lean-to shingle roof across the top
        with K.push((0, 0, zb + H + 0.55)):
            def rf(s, t):
                return (-W / 2 - 0.45 + s * (W + 0.9), -0.65 + t * 0.95, 0.42 * t)
            b.grid(6, 2, rf, 'Roof Shingle', (W + 0.9, 1.0), smooth=False)
            b.box(-W / 2 - 0.45, -0.68, -0.08, W / 2 + 0.45, -0.62, 0.05, 'Timber Dark', 0.01)
        # brackets
        for sx in (-1, 1):
            b.beam((sx * (W / 2 + 0.12), 0, zb + H + 0.15), (sx * (W / 2 + 0.12), -0.62, zb + H + 0.55), 0.1, 0.1, 'Timber Dark', 0.012)
        # carved header board (blank)
        if header:
            out.append(('HEADER', (0, -0.05, zb + H - 0.32), (2.2, 0.06, 0.42)))
        cols, rows = 2, (plaques + 1) // 2
        pw, ph = 1.45, 0.34
        for i in range(plaques):
            c, r = i % cols, i // cols
            cx = (c - 0.5) * (pw + 0.18)
            cz = zb + H - 0.78 - r * (ph + 0.08)
            out.append(('%02d' % (i + 1), (cx, -0.05, cz), (pw, 0.05, ph)))
        # nails / rope ties
        for name, (cx, cy, cz), (sw, sd, sh) in out:
            for sx in (-1, 1):
                b.sphere((cx + sx * (sw / 2 - 0.05), cy - sd / 2 - 0.005, cz), 0.018, 'Iron Black', 6, 4)
        # some old notices pinned on the posts
        for sx in (-1, 1):
            for k in range(2):
                pz = zb + 0.4 + k * 0.5 + K.rng.uniform(-0.1, 0.1)
                with K.push((sx * (W / 2 + 0.12), -0.125, pz), ry=K.rng.uniform(-0.12, 0.12)):
                    b.quad((-0.12, -0.002, -0.17), (0.12, -0.002, -0.17), (0.12, -0.002, 0.17), (-0.12, -0.002, 0.17), 'Parchment')
    return out


def plaque_objects(set_col, parent, code, items, mat='Planks Pale', header_mat='Gold'):
    """Create one object per ranking plaque (named <code>_RANK_PLAQUE_xx) + a text anchor empty
    (<code>_RANK_TEXT_xx: local Z = plaque normal, X = reading direction)."""
    objs = []
    for name, c, s in items:
        b = geo.Builder('%s_RANK_PLAQUE_%s' % (code, name))
        m = header_mat if name == 'HEADER' else mat
        b.cbox(c, s, m, 0.012)
        ob = b.finish(set_col)[0]
        ob.parent = parent
        e = bpy.data.objects.new('%s_RANK_TEXT_%s' % (code, name), None)
        e.empty_display_type = 'IMAGE' if False else 'PLAIN_AXES'
        e.empty_display_size = 0.3 * M
        e.location = (Vector(c) + Vector((0, -s[1] / 2 - 0.004, 0))) * M
        e.rotation_euler = (math.radians(90), 0, 0)
        e['text_height_bu'] = s[2] * 0.55 * M
        e['text_width_bu'] = s[0] * 0.9 * M
        set_col.objects.link(e)
        e.parent = parent
        objs.append(ob)
    return objs


def laundry_line(K, a, c, sag=0.35, cloths=('Cloth White', 'Cloth Blue', 'Cloth Red', 'Cloth Yellow', 'Cloth White')):
    b = K.b
    rng = K.rng
    a, c = Vector(a), Vector(c)
    pts = []
    N = 16
    for i in range(N + 1):
        t = i / N
        p = a.lerp(c, t)
        p.z -= sag * 4 * t * (1 - t)
        pts.append(p)
    for p, q in zip(pts, pts[1:]):
        b.cyl(p, q, 0.008, 'Rope', 5)
    L = (c - a).length
    x = 0.12
    k = 0
    d = (c - a).normalized()
    side = Vector((-d.y, d.x, 0))
    while x < L - 0.6:
        cw = rng.uniform(0.45, 0.9)
        ch = rng.uniform(0.5, 1.0)
        t0, t1 = x / L, (x + cw) / L
        p0 = a.lerp(c, t0); p0.z -= sag * 4 * t0 * (1 - t0)
        p1 = a.lerp(c, t1); p1.z -= sag * 4 * t1 * (1 - t1)
        m = cloths[k % len(cloths)]
        ph = rng.uniform(0, 6)

        def cl(s, t, p0=p0, p1=p1, ch=ch, ph=ph):
            top = p0.lerp(p1, s)
            w = 0.03 * math.sin(s * 9 + ph) * (0.3 + t)
            return top + side * w + Vector((0, 0, -t * ch * (1 - 0.08 * math.sin(PI * s))))
        b.grid(5, 4, cl, m, (cw, ch), smooth=True, both=True)
        for s in (0.05, 0.95):
            pp = p0.lerp(p1, s)
            b.cbox((pp.x, pp.y, pp.z - 0.01), (0.02, 0.025, 0.07), 'Timber Oak')
        x += cw + rng.uniform(0.1, 0.35)
        k += 1


def pigeon(K, x, y, z, rz=None):
    b = K.b
    rz = K.rng.uniform(0, 6.28) if rz is None else rz
    with K.push((x, y, z), rz=rz):
        b.sphere((0, 0, 0.09), 0.09, 'Feather Grey', 10, 6, (1.5, 0.85, 0.8))
        b.sphere((0.13, 0, 0.17), 0.045, 'Feather Grey', 8, 5)
        b.cbox((0.18, 0, 0.165), (0.03, 0.012, 0.012), 'Charcoal')
        b.beam((-0.1, 0, 0.1), (-0.24, 0, 0.12), 0.1, 0.02, 'Feather Grey', 0.005)
        for sy in (-1, 1):
            b.cyl((0.0, sy * 0.03, 0.03), (0.0, sy * 0.03, -0.0), 0.007, 'Terracotta', 4)


def rock(K, x, y, z, r, mat='Rock', squash=0.7, seed=0.0, nu=14, nv=9):
    rng = random.Random(seed or K.rng.random())
    ph = [rng.uniform(0, 6.28) for _ in range(6)]

    def d(v):
        n = (math.sin(v.x * 3.1 / r + ph[0]) * math.cos(v.y * 2.7 / r + ph[1]) * 0.18 +
             math.sin(v.y * 6.3 / r + v.z * 5.1 / r + ph[2]) * 0.08 + math.cos(v.x * 9.1 / r + ph[3]) * 0.04)
        f = 1 + n
        vv = v * f
        if vv.z < -r * squash * 0.4:
            vv.z = -r * squash * 0.4 + (vv.z + r * squash * 0.4) * 0.2
        return vv
    K.b.sphere((x, y, z), r, mat, nu, nv, (1.0, rng.uniform(0.75, 1.0), squash), deform=d, smooth=True)


def reeds(K, x, y, z, n=30, spread=0.6, h=1.5, mat='Reed'):
    """Clump of reed/grass blades (thin tapered quads, slightly bent) plus a few cattail heads."""
    b = K.b
    rng = K.rng
    V, F, U = [], [], []
    for i in range(n):
        a = rng.uniform(0, 6.28)
        rr = spread * math.sqrt(rng.random())
        bx, by = x + rr * math.cos(a), y + rr * math.sin(a)
        hh = h * rng.uniform(0.55, 1.1)
        lean = Vector((rng.uniform(-0.35, 0.35), rng.uniform(-0.35, 0.35), 0))
        rot = rng.uniform(0, 6.28)
        w = rng.uniform(0.015, 0.03)
        side = Vector((math.cos(rot), math.sin(rot), 0)) * w
        base = len(V)
        segs = 4
        for k in range(segs + 1):
            t = k / segs
            c = Vector((bx, by, z)) + lean * (t * t) * hh + Vector((0, 0, hh * t))
            s = side * (1 - t * 0.9)
            V += [c - s, c + s]
        for k in range(segs):
            i0 = base + 2 * k
            F.append((i0, i0 + 1, i0 + 3, i0 + 2))
            U.append([(0, k / segs * hh), (w, k / segs * hh), (w, (k + 1) / segs * hh), (0, (k + 1) / segs * hh)])
        if mat == 'Reed' and rng.random() < 0.12:
            top = Vector((bx, by, z)) + lean * hh * 0.85 + Vector((0, 0, hh * 0.92))
            b.cyl(top, top + Vector((0, 0, 0.14)), 0.025, 'Cattail', 6)
    b.mesh(V, F, mat, U, smooth=True)


def tree(K, x, y, z, h=8.0, kind='oak', seed=None, leaves=9000, leafmat=None):
    """Broadleaf tree: tapered bark trunk + branches + thousands of small leaf cards in crown clusters."""
    b = K.b
    rng = random.Random(seed if seed is not None else K.rng.random())
    lean = Vector((rng.uniform(-0.6, 0.6), rng.uniform(-0.6, 0.6), 0))
    trunk_h = h * (0.45 if kind == 'oak' else 0.38)
    r0 = h * 0.035
    pts = []
    for i in range(6):
        t = i / 5
        pts.append(Vector((x, y, z)) + lean * t * t + Vector((0, 0, trunk_h * t)))
    for i, (p, q) in enumerate(zip(pts, pts[1:])):
        b.cyl(p - Vector((0, 0, 0.3 if i == 0 else 0)), q, r0 * (1 - i * 0.12), 'Bark', 10, r0 * (1 - (i + 1) * 0.12), caps=(i == 4))
    # root flare
    b.lathe([(r0 * 1.9, z - 0.2), (r0 * 1.5, z + 0.05), (r0 * 1.05, z + 0.5)], 'Bark', 10, pts[0] * 1.0 - Vector((0, 0, z)), cap_top=False)
    top = pts[-1]
    clusters = []
    nb_ = 6 if kind == 'oak' else 7
    for k in range(nb_):
        a = 2 * PI * k / nb_ + rng.uniform(-0.3, 0.3)
        up = rng.uniform(0.25, 0.6) * h * (0.6 if kind == 'willow' else 1.0)
        out = rng.uniform(0.25, 0.42) * h
        end = top + Vector((math.cos(a) * out, math.sin(a) * out, up))
        mid = top.lerp(end, 0.5) + Vector((0, 0, h * 0.06))
        b.cyl(top - Vector((0, 0, 0.4)), mid, r0 * 0.55, 'Bark', 8, r0 * 0.35)
        b.cyl(mid, end, r0 * 0.35, 'Bark', 6, r0 * 0.12)
        clusters.append((end, h * rng.uniform(0.17, 0.24)))
    clusters.append((top + Vector((0, 0, h * 0.42)), h * 0.26))
    V, F, U = [], [], []
    leafmat = leafmat or ('Leaf Willow' if kind == 'willow' else 'Leaf Oak')
    per = leaves // len(clusters)
    for c, R in clusters:
        for i in range(per):
            # point in an ellipsoid shell (denser outside)
            while True:
                d = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1)))
                if 0.35 < d.length <= 1.0:
                    break
            p = c + Vector((d.x * R, d.y * R, d.z * R * 0.75))
            if kind == 'willow':
                p.z -= (1 - d.z) * R * rng.uniform(0.3, 1.2)
            s = rng.uniform(0.08, 0.14) * (2.1 if kind == 'oak' else 1.6) * (h / 9.0)
            n = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-0.2, 1))).normalized()
            t1 = n.cross(Vector((0, 0, 1)) if abs(n.z) < 0.9 else Vector((1, 0, 0))).normalized()
            t2 = n.cross(t1)
            if kind == 'willow':
                t2 = Vector((0, 0, 1)) * 1.0
                t1 = n.cross(t2).normalized() if n.cross(t2).length > 0.1 else Vector((1, 0, 0))
                L, Wd = s * 1.8, s * 0.35
            else:
                L, Wd = s, s * 0.6
            base = len(V)
            V += [p - t2 * L, p + t1 * Wd, p + t2 * L, p - t1 * Wd]
            F.append((base, base + 1, base + 2, base + 3))
            U.append([(0, 0), (0.05, 0.05), (0.1, 0), (0.05, -0.05)])
    b.mesh(V, F, leafmat, U, smooth=False)


def waterwheel(K, x, y, z, R=2.1, width=1.0, n_paddles=16, rot=0.0):
    """Undershot mill wheel, axle along X at (x, y, z)."""
    b = K.b
    with K.push((x, y, z), ry=PI / 2):
        for zz in (-width / 2, width / 2):
            b.lathe([(R - 0.12, zz - 0.05), (R, zz - 0.05), (R, zz + 0.05), (R - 0.12, zz + 0.05), (R - 0.12, zz - 0.05)], 'Timber Dark', 32,
                    (0, 0, 0), cap_top=False, smooth=False)
            for k in range(8):
                a = 2 * PI * k / 8 + rot
                b.beam((0.2 * math.cos(a), 0.2 * math.sin(a), zz), ((R - 0.1) * math.cos(a), (R - 0.1) * math.sin(a), zz), 0.09, 0.1, 'Timber Dark', 0.01)
        b.cyl((0, 0, -width / 2 - 0.5), (0, 0, width / 2 + 0.3), 0.14, 'Timber Oak', 12)
        for k in range(n_paddles):
            a = 2 * PI * k / n_paddles + rot
            c = Vector(((R - 0.05) * math.cos(a), (R - 0.05) * math.sin(a), 0))
            b.cbox(c, (0.42, 0.05, width + 0.08), 'Planks Grey', 0.008, rot=(0, 0, a))
