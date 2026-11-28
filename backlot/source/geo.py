"""Mesh builder for the backlot.  Author in METRES (local frame), store in BU (1 m = 3.3 BU).

Every mesh gets a UV map 'UVm' in metres:
  * wood-like materials: U runs along the piece's grain axis (the long axis of a beam / plank),
  * everything else: V points up the face (up the wall, up the roof slope), U horizontal.
Faces of displaced materials (ground, roofs) go to a separate '<name> D' object with adaptive
subdivision, everything else stays plain.
"""
import bpy, math, random
from mathutils import Vector, Matrix
import mats

M = 3.3
GRAIN = ('Timber', 'Planks', 'Paint', 'Hay', 'Rope', 'Cloth', 'Canvas', 'Carpet', 'Velvet', 'Leather')


def is_grain(mat):
    return any(mat.startswith(g) for g in GRAIN)


def _newell(pts):
    n = Vector((0, 0, 0))
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        n.x += (a.y - b.y) * (a.z + b.z)
        n.y += (a.z - b.z) * (a.x + b.x)
        n.z += (a.x - b.x) * (a.y + b.y)
    return n


def rotm(rx=0.0, ry=0.0, rz=0.0):
    return (Matrix.Rotation(rz, 3, 'Z') @ Matrix.Rotation(ry, 3, 'Y') @ Matrix.Rotation(rx, 3, 'X'))


class Builder:
    def __init__(self, name, seed=1):
        self.name = name
        self.V = []
        self.F = []      # (indices, mat, uv or None, smooth, grain)
        self.stack = [Matrix.Identity(4)]
        self.rng = random.Random(seed)
        self.attrs = {}  # per-vertex float attributes: name -> list

    # -- transforms (metres) ------------------------------------------------------------------
    @property
    def T(self):
        return self.stack[-1]

    def push(self, loc=(0, 0, 0), rz=0.0, rx=0.0, ry=0.0, scale=1.0):
        m = Matrix.Translation(Vector(loc)) @ rotm(rx, ry, rz).to_4x4() @ Matrix.Scale(scale, 4)
        self.stack.append(self.T @ m)
        return self

    def pop(self):
        self.stack.pop()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.pop()

    # -- core -----------------------------------------------------------------------------------
    def mesh(self, verts, faces, mat, uvs=None, smooth=False, grain=None, attr=None):
        """verts: local metres; faces: index tuples; mat: library name or list per face; uvs: per-face lists."""
        T = self.T
        base = len(self.V)
        for p in verts:
            self.V.append((T @ Vector(p)) * M)
        if attr:
            for k, val in attr.items():
                lst = self.attrs.setdefault(k, [0.0] * base)
                lst.extend([val] * len(verts))
        for k, lst in self.attrs.items():
            if len(lst) < len(self.V):
                lst.extend([0.0] * (len(self.V) - len(lst)))
        g = None
        if grain is not None:
            g = (T.to_3x3() @ Vector(grain)).normalized()
        for i, f in enumerate(faces):
            m = mat[i] if isinstance(mat, (list, tuple)) else mat
            uv = uvs[i] if uvs else None
            self.F.append((tuple(base + j for j in f), m, uv, smooth, g))
        return base

    def poly(self, pts, mat, uv=None, grain=None):
        if uv is None:
            q = []
            for p in pts:
                p = Vector(p)
                if not q or (p - q[-1]).length > 1e-5:
                    q.append(p)
            while len(q) > 2 and (q[0] - q[-1]).length < 1e-5:
                q.pop()
            pts = q
            if len(pts) < 3:
                return None
        return self.mesh(pts, [tuple(range(len(pts)))], mat, [uv] if uv else None, False, grain)

    def quad(self, a, b, c, d, mat, uv=None, grain=None):
        return self.poly([a, b, c, d], mat, uv, grain)

    # -- primitives -------------------------------------------------------------------------------
    def box(self, x0, y0, z0, x1, y1, z1, mat, bevel=0.0, **kw):
        c = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
        return self.cbox(c, (abs(x1 - x0), abs(y1 - y0), abs(z1 - z0)), mat, bevel, **kw)

    def cbox(self, center, size, mat, bevel=0.0, rot=(0, 0, 0), faces_skip=(), grain=None, top_mat=None):
        hx, hy, hz = size[0] / 2, size[1] / 2, size[2] / 2
        b = min(bevel, hx * 0.45, hy * 0.45, hz * 0.45) if bevel else 0.0
        V = []
        key = {}
        for sx in (-1, 1):
            for sy in (-1, 1):
                for sz in (-1, 1):
                    if b > 0:
                        key[(sx, sy, sz, 0)] = len(V); V.append(Vector((sx * hx, sy * (hy - b), sz * (hz - b))))
                        key[(sx, sy, sz, 1)] = len(V); V.append(Vector((sx * (hx - b), sy * hy, sz * (hz - b))))
                        key[(sx, sy, sz, 2)] = len(V); V.append(Vector((sx * (hx - b), sy * (hy - b), sz * hz)))
                    else:
                        i = len(V); V.append(Vector((sx * hx, sy * hy, sz * hz)))
                        for a in range(3):
                            key[(sx, sy, sz, a)] = i
        cyc = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        faces, fm = [], []
        for ax in range(3):
            for s in (-1, 1):
                if (ax, s) in faces_skip:
                    continue
                f = []
                for p, q in cyc:
                    c = [0, 0, 0]
                    c[ax] = s
                    o = [i for i in range(3) if i != ax]
                    c[o[0]], c[o[1]] = p, q
                    f.append(key[(c[0], c[1], c[2], ax)])
                faces.append(f)
                fm.append(top_mat if (top_mat and ax == 2 and s == 1) else mat)
        if b > 0:
            for a1, a2 in ((0, 1), (0, 2), (1, 2)):
                a3 = 3 - a1 - a2
                for s1 in (-1, 1):
                    for s2 in (-1, 1):
                        cs = []
                        for s3 in (-1, 1):
                            c = [0, 0, 0]
                            c[a1], c[a2], c[a3] = s1, s2, s3
                            cs.append(tuple(c))
                        faces.append([key[cs[0] + (a1,)], key[cs[0] + (a2,)], key[cs[1] + (a2,)], key[cs[1] + (a1,)]])
                        fm.append(mat)
            for sx in (-1, 1):
                for sy in (-1, 1):
                    for sz in (-1, 1):
                        faces.append([key[(sx, sy, sz, 0)], key[(sx, sy, sz, 1)], key[(sx, sy, sz, 2)]])
                        fm.append(mat)
        # orient outward
        out = []
        for f in faces:
            pts = [V[i] for i in f]
            cen = sum(pts, Vector()) / len(pts)
            if _newell(pts).dot(cen) < 0:
                f = f[::-1]
            out.append(tuple(f))
        R = rotm(*rot)
        verts = [R @ v + Vector(center) for v in V]
        if grain is None:
            ax = max(range(3), key=lambda i: size[i])
            grain = R @ Vector([1.0 if i == ax else 0.0 for i in range(3)])
        return self.mesh(verts, out, fm, None, False, grain)

    def beam(self, p, q, w, h, mat, bevel=0.015, up=(0, 0, 1), roll=0.0):
        """A rectangular timber from p to q (metres), cross-section w (side) x h (up)."""
        p, q = Vector(p), Vector(q)
        d = q - p
        L = d.length
        if L < 1e-5:
            return
        x = d.normalized()
        upv = Vector(up)
        if abs(x.dot(upv)) > 0.98:
            upv = Vector((0, 1, 0)) if abs(x.y) < 0.9 else Vector((1, 0, 0))
        y = upv.cross(x).normalized()
        z = x.cross(y).normalized()
        if roll:
            R = Matrix.Rotation(roll, 3, x)
            y, z = R @ y, R @ z
        Rm = Matrix((x, y, z)).transposed()
        c = (p + q) / 2
        eul = Rm.to_euler('XYZ')
        return self.cbox(c, (L, w, h), mat, bevel, rot=(eul.x, eul.y, eul.z), grain=x)

    def cyl(self, p, q, r, mat, n=12, r2=None, caps=True, smooth=True, uscale=1.0):
        p, q = Vector(p), Vector(q)
        d = q - p
        L = d.length
        if L < 1e-6:
            return
        k = d.normalized()
        ref = Vector((0, 0, 1)) if abs(k.z) < 0.9 else Vector((1, 0, 0))
        u = k.cross(ref).normalized()
        w = k.cross(u)
        r2 = r if r2 is None else r2
        V, F, UV = [], [], []
        for o, rr in ((p, r), (q, r2)):
            for i in range(n):
                a = 2 * math.pi * i / n
                V.append(o + rr * (u * math.cos(a) + w * math.sin(a)))
        circ = 2 * math.pi * max(r, r2)
        for i in range(n):
            j = (i + 1) % n
            F.append((i, j, n + j, n + i))
            u0, u1 = circ * i / n * uscale, circ * (i + 1) / n * uscale
            UV.append([(0, u0), (0, u1), (L, u1), (L, u0)])
        if caps:
            F.append(tuple(range(n))[::-1])
            UV.append([(V[i].dot(u), V[i].dot(w)) for i in range(n)][::-1])
            F.append(tuple(range(n, 2 * n)))
            UV.append([(V[i].dot(u), V[i].dot(w)) for i in range(n, 2 * n)])
        # cylinder UVs: U along the axis (grain), V around
        b = self.mesh(V, F, mat, UV, smooth, k)
        if caps:
            # caps flat-shaded
            self.F[-1] = self.F[-1][:3] + (False,) + self.F[-1][4:]
            self.F[-2] = self.F[-2][:3] + (False,) + self.F[-2][4:]
        return b

    def lathe(self, prof, mat, n=24, center=(0, 0, 0), smooth=True, cap_top=True, cap_bot=False, phase=0.0, mats_per_seg=None):
        """prof: list of (r, z) bottom->top. UV: U around (metres at that radius), V along the profile."""
        c = Vector(center)
        V, F, UV, FM = [], [], [], []
        rows = len(prof)
        acc = [0.0]
        for i in range(1, rows):
            acc.append(acc[-1] + math.hypot(prof[i][0] - prof[i - 1][0], prof[i][1] - prof[i - 1][1]))
        for r, z in prof:
            for i in range(n):
                a = 2 * math.pi * i / n + phase
                V.append(c + Vector((r * math.cos(a), r * math.sin(a), z)))
        for k in range(rows - 1):
            rr = max(prof[k][0], prof[k + 1][0], 1e-3)
            for i in range(n):
                j = (i + 1) % n
                a0, a1 = k * n + i, k * n + j
                b0, b1 = (k + 1) * n + i, (k + 1) * n + j
                F.append((a0, a1, b1, b0))
                u0 = 2 * math.pi * rr * i / n
                u1 = 2 * math.pi * rr * (i + 1) / n
                UV.append([(u0, acc[k]), (u1, acc[k]), (u1, acc[k + 1]), (u0, acc[k + 1])])
                FM.append(mats_per_seg[k] if mats_per_seg else mat)
        if cap_top and prof[-1][0] > 1e-4:
            top = list(range((rows - 1) * n, rows * n))
            F.append(tuple(top))
            UV.append([((V[i] - c).x, (V[i] - c).y) for i in top])
            FM.append(mats_per_seg[-1] if mats_per_seg else mat)
        if cap_bot and prof[0][0] > 1e-4:
            bot = list(range(n))[::-1]
            F.append(tuple(bot))
            UV.append([((V[i] - c).x, (V[i] - c).y) for i in bot])
            FM.append(mats_per_seg[0] if mats_per_seg else mat)
        T = self.T
        base = len(self.V)
        for p in V:
            self.V.append((T @ p) * M)
        for k, lst in self.attrs.items():
            lst.extend([0.0] * (len(self.V) - len(lst)))
        for f, uv, m in zip(F, UV, FM):
            self.F.append((tuple(base + j for j in f), m, uv, smooth, None))
        return base

    def sphere(self, center, r, mat, nu=12, nv=8, scale=(1, 1, 1), deform=None, smooth=True):
        c = Vector(center)
        V, F, UV = [], [], []
        for j in range(nv + 1):
            th = math.pi * j / nv
            for i in range(nu):
                ph = 2 * math.pi * i / nu
                v = Vector((math.sin(th) * math.cos(ph) * scale[0], math.sin(th) * math.sin(ph) * scale[1], -math.cos(th) * scale[2])) * r
                if deform:
                    v = deform(v)
                V.append(c + v)
        for j in range(nv):
            for i in range(nu):
                a = j * nu + i
                b = j * nu + (i + 1) % nu
                F.append((a, b, b + nu, a + nu))
                UV.append([(r * 2 * math.pi * i / nu, r * math.pi * j / nv), (r * 2 * math.pi * (i + 1) / nu, r * math.pi * j / nv),
                           (r * 2 * math.pi * (i + 1) / nu, r * math.pi * (j + 1) / nv), (r * 2 * math.pi * i / nu, r * math.pi * (j + 1) / nv)])
        return self.mesh(V, F, mat, UV, smooth)

    def prism(self, outline, y0, y1, mat, side_mat=None, back=True):
        """Extrude a 2D outline [(x, z)] (CCW seen from -Y) from y0 (front) to y1 (back)."""
        n = len(outline)
        V = [Vector((x, y0, z)) for x, z in outline] + [Vector((x, y1, z)) for x, z in outline]
        F, FM = [], []
        F.append(tuple(range(n)))
        FM.append(mat)
        if back:
            F.append(tuple(range(n, 2 * n))[::-1])
            FM.append(mat)
        for i in range(n):
            j = (i + 1) % n
            F.append((j, i, n + i, n + j))
            FM.append(side_mat or mat)
        # orient: front face must face -Y
        pts = [V[i] for i in F[0]]
        if _newell(pts).y > 0:
            F = [f[::-1] for f in F]
        return self.mesh(V, F, FM)

    def grid(self, nu, nv, fn, mat, size=(1.0, 1.0), smooth=True, both=False):
        """Sheet from fn(s, t) -> local point, s,t in 0..1. UV = (s*size[0], t*size[1]) metres."""
        V, F, UV = [], [], []
        for j in range(nv + 1):
            for i in range(nu + 1):
                V.append(Vector(fn(i / nu, j / nv)))
        for j in range(nv):
            for i in range(nu):
                a = j * (nu + 1) + i
                F.append((a, a + 1, a + nu + 2, a + nu + 1))
                s0, s1, t0, t1 = i / nu * size[0], (i + 1) / nu * size[0], j / nv * size[1], (j + 1) / nv * size[1]
                UV.append([(s0, t0), (s1, t0), (s1, t1), (s0, t1)])
        b = self.mesh(V, F, mat, UV, smooth)
        if both:
            self.mesh(V, [f[::-1] for f in F], mat, [uv[::-1] for uv in UV], smooth)
        return b

    def wall(self, x0, x1, z0, z1, mat, holes=(), y=0.0, depth=0.22, reveal=None, sill=None, back=False):
        """A facade plane in the local XZ plane at y (outward normal -Y) with rectangular holes
        (hx0, hx1, hz0, hz1) and reveals `depth` deep (towards +Y)."""
        xs = sorted(set([x0, x1] + [h[0] for h in holes] + [h[1] for h in holes]))
        xs = [x for x in xs if x0 <= x <= x1]
        for xa, xb in zip(xs, xs[1:]):
            if xb - xa < 1e-5:
                continue
            cover = sorted([(h[2], h[3]) for h in holes if h[0] <= xa + 1e-6 and h[1] >= xb - 1e-6])
            zs = [z0]
            for hz0, hz1 in cover:
                zs += [hz0, hz1]
            zs.append(z1)
            for k in range(0, len(zs), 2):
                za, zb = zs[k], zs[k + 1]
                if zb - za > 1e-5:
                    self.quad((xa, y, za), (xb, y, za), (xb, y, zb), (xa, y, zb), mat)
        rm = reveal or mat
        for hx0, hx1, hz0, hz1 in holes:
            d = y + depth
            self.quad((hx1, y, hz0), (hx1, d, hz0), (hx0, d, hz0), (hx0, y, hz0), sill or rm)   # sill (up)
            self.quad((hx0, d, hz1), (hx1, d, hz1), (hx1, y, hz1), (hx0, y, hz1), rm)           # head (down)
            self.quad((hx0, d, hz0), (hx0, d, hz1), (hx0, y, hz1), (hx0, y, hz0), rm)           # left jamb (+X)
            self.quad((hx1, y, hz1), (hx1, d, hz1), (hx1, d, hz0), (hx1, y, hz0), rm)           # right jamb (-X)
        if back:
            self.quad((x0, y + depth, z0), (x0, y + depth, z1), (x1, y + depth, z1), (x1, y + depth, z0), mat)

    def torus(self, center, R, r, mat, n=16, m=6, axis='Y'):
        V, F = [], []
        for i in range(n):
            a = 2 * math.pi * i / n
            for j in range(m):
                b = 2 * math.pi * j / m
                p = Vector(((R + r * math.cos(b)) * math.cos(a), r * math.sin(b), (R + r * math.cos(b)) * math.sin(a)))
                if axis == 'Z':
                    p = Vector((p.x, p.z, p.y))
                elif axis == 'X':
                    p = Vector((p.y, p.x, p.z))
                V.append(Vector(center) + p)
        for i in range(n):
            for j in range(m):
                a = i * m + j
                b = i * m + (j + 1) % m
                c = ((i + 1) % n) * m + (j + 1) % m
                d = ((i + 1) % n) * m + j
                F.append((a, d, c, b))
        return self.mesh(V, F, mat, None, True, None)

    # -- finish ---------------------------------------------------------------------------------
    def finish(self, collection, name=None, split_disp=True, adaptive=True, dicing=1.0, parent=None):
        """Create the object(s). Returns list of objects (plain, displaced)."""
        name = name or self.name
        groups = {}
        for f in self.F:
            d = split_disp and mats.is_displaced(f[1])
            groups.setdefault(d, []).append(f)
        objs = []
        for disp, faces in sorted(groups.items()):
            used = {}
            verts = []
            nf = []
            for idx, m, uv, sm, g in faces:
                ni = []
                for i in idx:
                    if i not in used:
                        used[i] = len(verts)
                        verts.append(self.V[i])
                    ni.append(used[i])
                nf.append((ni, m, uv, sm, g))
            me = bpy.data.meshes.new(name + (' D' if disp else ''))
            me.from_pydata([tuple(v) for v in verts], [], [f[0] for f in nf])
            mlist = []
            for f in nf:
                if f[1] not in mlist:
                    mlist.append(f[1])
            for mname in mlist:
                me.materials.append(mats.get(mname))
            mi = [mlist.index(f[1]) for f in nf]
            me.polygons.foreach_set('material_index', mi)
            me.polygons.foreach_set('use_smooth', [bool(f[3]) for f in nf])
            uvl = me.uv_layers.new(name=mats.UVNAME)
            data = []
            for f in nf:
                pts = [Vector(verts[i]) for i in f[0]]
                if f[2] is not None:
                    data.extend([c for uv in f[2] for c in uv])
                else:
                    data.extend(_auto_uv(pts, f[1], f[4]))
            uvl.data.foreach_set('uv', data)
            for k, lst in self.attrs.items():
                a = me.attributes.new(k, 'FLOAT', 'POINT')
                inv = {v: k2 for k2, v in used.items()}
                a.data.foreach_set('value', [lst[inv[i]] for i in range(len(verts))])
            me.validate(clean_customdata=False)
            me.update()
            ob = bpy.data.objects.new(me.name, me)
            collection.objects.link(ob)
            if parent is not None:
                ob.parent = parent
            if disp:
                mod = ob.modifiers.new('Adaptive', 'SUBSURF')
                mod.subdivision_type = 'SIMPLE'
                mod.levels = 0
                mod.render_levels = 1
                try:
                    mod.use_adaptive_subdivision = adaptive
                    mod.adaptive_space = 'PIXEL'
                    mod.adaptive_pixel_size = dicing
                except Exception:
                    pass
            objs.append(ob)
        return objs


def _auto_uv(pts, mat, grain):
    n = _newell(pts)
    if n.length < 1e-9:
        return [0.0] * (2 * len(pts))
    n.normalize()
    U = None
    if grain is not None and is_grain(mat):
        g = grain - n * grain.dot(n)
        if g.length > 0.3:
            U = g.normalized()
    if U is None:
        if abs(n.z) < 0.9:
            U = Vector((0, 0, 1)).cross(n).normalized()
        else:
            U = Vector((1, 0, 0)) if n.z > 0 else Vector((-1, 0, 0))
            U = (U - n * U.dot(n)).normalized()
    Vv = n.cross(U)
    out = []
    for p in pts:
        out += [p.dot(U) / M, p.dot(Vv) / M]
    return out


def auto_uv_mesh(me):
    """Recompute 'UVm' (metres) on an existing mesh using the backlot rules."""
    uvl = me.uv_layers.get(mats.UVNAME) or me.uv_layers.new(name=mats.UVNAME)
    data = []
    for poly in me.polygons:
        pts = [me.vertices[me.loops[li].vertex_index].co.copy() for li in poly.loop_indices]
        mname = me.materials[poly.material_index].get('bl_lib', '') if me.materials else ''
        grain = None
        if is_grain(mname):
            # longest edge of the face as grain
            best = None
            for i in range(len(pts)):
                e = pts[(i + 1) % len(pts)] - pts[i]
                if best is None or e.length > best.length:
                    best = e
            grain = best.normalized() if best and best.length > 1e-6 else None
        data.extend(_auto_uv(pts, mname, grain))
    uvl.data.foreach_set('uv', data)
    me.uv_layers.active = uvl


def coll(name, parent=None):
    c = bpy.data.collections.get(name) or bpy.data.collections.new(name)
    if parent is not None and c.name not in parent.children:
        parent.children.link(c)
    return c


def empty(name, loc, col, rz=0.0, kind='PLAIN_AXES', size=1.0, parent=None):
    e = bpy.data.objects.new(name, None)
    e.empty_display_type = kind
    e.empty_display_size = size
    e.location = loc
    e.rotation_euler = (0, 0, rz)
    col.objects.link(e)
    if parent:
        e.parent = parent
    return e
