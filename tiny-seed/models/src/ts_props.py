# Tiny Seed props: measuring pillar, pie table (normal / squished), golden apples.
import os
from PIL import Image
from ts_lib import *
from ts_tree import apple_mesh

HERE = os.path.dirname(os.path.abspath(__file__))


def gingham():
    p = os.path.abspath(os.path.join(HERE, '..', 'faces', 'TS_Tex_Gingham.png'))
    n = 8; c = 32
    im = Image.new('RGB', (n * c, n * c))
    cols = {0: (236, 226, 204), 1: (214, 128, 108), 2: (190, 62, 44)}
    for i in range(n):
        for j in range(n):
            im.paste(cols[(i % 2) + (j % 2)], (i * c, j * c, i * c + c, j * c + c))
    im.save(p)
    img = bpy.data.images.load(p); img.name = 'TS_Tex_Gingham'
    return img


def pie(mb, c, r, fill_i, kind, rng, squash=1.0, w=None):
    """crust mat 0, filling mat fill_i, cream mat 5."""
    prof = [(0.66, 0.0), (0.98, 0.30), (1.10, 0.36), (1.12, 0.44), (1.0, 0.50), (0.86, 0.42)]
    v, f = lathe([(a * r, z * r * squash) for a, z in prof], 24, cap_bottom=True, cap_top=False)
    for i in range(len(v)):
        rr = math.hypot(v[i][0], v[i][1])
        if rr > 0.95 * r:
            a = math.atan2(v[i][1], v[i][0]); v[i][:2] *= 1 + 0.045 * math.cos(12 * a)
    mb.add(v + np.array(c), f, 0, fjit=0.04, col=lambda p: (1, 1, 1))
    v, f = lathe([(0.87 * r, 0.40 * r * squash), (0.6 * r, 0.50 * r * squash), (0.3 * r, 0.55 * r * squash), (0.001, 0.57 * r * squash)], 24, cap_bottom=False, cap_top=False)
    mb.add(v + np.array(c), f, fill_i)
    if kind == 'lattice':
        for k in range(-2, 3):
            for ang in (35, -55):
                L = 2 * r * 0.84 * math.sqrt(max(0.05, 1 - (k * 0.36) ** 2))
                bv, bf = box((L, 0.17 * r, 0.07 * r), (0, k * 0.36 * r * 0.86, 0), 0.02 * r)
                h = (0.55 - 0.11 * (k * 0.36) ** 2 * 4) * r * squash + (0.012 * r if ang > 0 else 0)
                bv = xf(bv, Matrix.Translation((c[0], c[1], c[2] + h)) @ Matrix.Rotation(R(ang), 4, 'Z'))
                mb.add(bv, bf, 0, col=(1.0, 0.95, 0.85))
    if kind == 'cream':
        for k in range(6):
            a = 2 * math.pi * k / 6
            bv, bf = blob((c[0] + math.cos(a) * 0.52 * r, c[1] + math.sin(a) * 0.52 * r, c[2] + 0.52 * r * squash), (0.17 * r, 0.17 * r, 0.15 * r * squash), sub=2, amp=0)
            mb.add(bv, bf, 5)
        bv, bf = blob((c[0], c[1], c[2] + 0.6 * r * squash), (0.2 * r, 0.2 * r, 0.17 * r * squash), sub=2, amp=0)
        mb.add(bv, bf, 5)


def splat(mb, c, r, fill_i, rng):
    V = [(c[0], c[1], c[2] + 0.07 * r)]; F = []
    n = 40
    ph = [rng.uniform(0, 6.28) for _ in range(3)]
    for ring, (rf, z) in enumerate(((0.55, 0.06), (1.0, 0.035), (1.12, 0.0))):
        for k in range(n):
            a = 2 * math.pi * k / n
            lob = 1 + 0.30 * math.sin(5 * a + ph[0]) + 0.16 * math.sin(9 * a + ph[1]) + 0.10 * math.sin(3 * a + ph[2])
            rr = r * rf * (lob if ring else 1 + 0.5 * (lob - 1))
            V.append((c[0] + rr * math.cos(a), c[1] + rr * math.sin(a), c[2] + z * r))
    for k in range(n):
        F.append([0, 1 + k, 1 + (k + 1) % n])
    for i in range(2):
        for k in range(n):
            a, b = 1 + i * n + k, 1 + i * n + (k + 1) % n
            F.append([a, a + n, b + n, b])
    mb.add(V, F, fill_i)
    for k in range(5):
        a = rng.uniform(0, 6.28); d = r * rng.uniform(1.45, 2.0); s = r * rng.uniform(0.09, 0.2)
        bv, bf = blob((c[0] + d * math.cos(a), c[1] + d * math.sin(a), c[2] + s * 0.1), (s, s * rng.uniform(0.7, 1), s * 0.35), sub=2, amp=0, floor=c[2])
        mb.add(bv, bf, fill_i)


def build(root):
    C = coll('TS_Props', root)
    m_stone = mat('PillarStone', '#C4BDAE', 0.9)
    m_stone_dk = mat('PillarStoneDark', '#8F897D', 0.9)
    m_panel = mat('PillarPanelGlow', '#EAF8FF', 0.4, emit='#CFEFFF', estr=2.2, vcol=False)
    m_moss = mat('Moss', '#86B24C', 0.95)
    m_wood = mat('TableWood', '#B08D5C', 0.85)
    m_wood_dk = mat('TableWoodDark', '#7A6245', 0.85)
    m_crust = mat('PieCrust', '#DDA860', 0.8)
    fills = [mat('PieBerry', '#7A2E63', 0.45, spec=0.5), mat('PieCherry', '#BE3229', 0.45, spec=0.5), mat('PiePumpkin', '#E08A2A', 0.6), mat('PieCustard', '#EFCB6B', 0.55)]
    m_cream = mat('PieCream', '#FBF4E6', 0.6)
    m_gold = mat('AppleGold', '#F6BE2C', 0.3, emit='#FFAA10', estr=1.1, spec=0.6)
    m_bark = mat('TreeBark', '#AC7F52', 0.9)
    m_leaf = mat('TreeLeaf', '#A9D168', 0.8)
    m_cloth = image_mat('TableCloth', gingham(), rough=0.9, alpha=False)

    # ------------------------------------------------------------ measuring pillar (8 BU)
    mb = MB()
    rng = random.Random(2)
    def st(size, c, bev, mi=0, t=1.0):
        v, f = box(size, c, bev)
        mb.add(v, f, mi, col=(t, t, t * 0.99), shade=(0, 8, 0.86))
    st((3.7, 3.7, 0.7), (0, 0, 0.35), 0.14, t=0.93)
    st((3.05, 3.05, 0.5), (0, 0, 0.95), 0.12, t=0.98)
    st((2.3, 2.3, 5.0), (0, 0, 3.7), 0.2)
    st((2.52, 2.52, 0.34), (0, 0, 1.52), 0.08, t=0.92)
    st((2.52, 2.52, 0.34), (0, 0, 5.9), 0.08, t=0.92)
    st((3.1, 3.1, 0.6), (0, 0, 6.5), 0.14, t=0.97)
    st((2.4, 2.4, 0.45), (0, 0, 7.0), 0.12, t=0.93)
    v, f = blob((0, 0, 7.66), (0.52, 0.52, 0.62), sub=2, amp=0)          # carved stone seed on top
    mb.add(v, f, 0, col=(0.97, 0.97, 0.96))
    lv, lf = leaf(0.8, 0.5, 0.1, 0.2)
    for sg in (-1, 1):
        mb.add(align(lv, Vector((sg * 0.8, 0, 0.55)), (0, 0, 7.15), axis='Y'), lf, 0, col=(0.9, 0.9, 0.89))
    st((1.96, 0.16, 2.9), (0, -1.17, 3.75), 0.05, mi=1)                   # panel frame
    for sx in (-1, 1):                                                      # ruler ticks on both sides
        for i in range(9):
            L = 0.7 if i % 4 == 0 else 0.4
            st((0.07, L, 0.09), (sx * 1.16, -0.55 + L / 2 - 0.2, 2.05 + i * 0.42), 0.02, mi=1)
    for (x, y, s_) in ((1.7, -1.5, 0.75), (-1.75, 1.2, 0.9), (-1.4, -1.75, 0.5)):
        v, f = blob((x, y, 0.15), (s_, s_, s_ * 0.5), sub=2, amp=0.15, seed=int(x * 10), floor=-0.1)
        mb.add(v, f, 2, flat=True, fjit=0.1)
    pil = mb.obj('TS_MeasuringPillar', [m_stone, m_stone_dk, m_moss], C, sharp=45)
    pil.location = (-14, 0, 0)
    mb = MB()
    v, f = box((1.62, 0.06, 2.56), (0, 0, 0), 0.02)
    mb.add(v, f, 0)
    pan = mb.obj('TS_MeasuringPillar_Panel', [m_panel], C, parent=pil, sharp=45)
    pan.location = (0, -1.27, 3.75)

    # ------------------------------------------------------------ pie table
    TL, TD, TH = 9.0, 3.6, 2.6
    def table(mb, squished, wi=0):
        rng = random.Random(8)
        halves = ((-1, 0),) if not squished else ((-1, 1), (1, 1))
        if not squished:
            for i in range(4):
                v, f = box((TL, TD / 4 - 0.04, 0.3), (0, (i - 1.5) * TD / 4, TH - 0.15), 0.05)
                t = rng.uniform(0.86, 1.0); mb.add(v, f, wi, col=(t, t, t))
            for sx in (-1, 1):
                for sy in (-1, 1):
                    v, f = box((0.36, 0.36, TH - 0.2), (0, 0, 0), 0.05)
                    v = xf(v, Matrix.Translation((sx * 3.5, sy * 0.95, (TH - 0.3) / 2)) @ Matrix.Rotation(R(sy * 14), 4, 'X'))
                    mb.add(v, f, wi + 1)
                v, f = box((0.3, 2.3, 0.3), (sx * 3.5, 0, 1.0), 0.05); mb.add(v, f, wi + 1)
            v, f = box((7.0, 0.26, 0.26), (0, 0, 1.0), 0.05); mb.add(v, f, wi + 1)
        else:
            # top snapped in the middle: two halves in a shallow V, legs splayed flat
            for sx in (-1, 1):
                for i in range(4):
                    v, f = box((TL / 2 - 0.05, TD / 4 - 0.04, 0.3), (0, 0, 0), 0.05)
                    # jagged break at the inner end
                    for k in range(len(v)):
                        if v[k][0] * -sx > TL / 4 - 0.3:
                            v[k][0] += -sx * rng.uniform(-0.25, 0.1)
                    M = Matrix.Translation((sx * (TL / 4 + 0.1), (i - 1.5) * TD / 4 + rng.uniform(-0.05, 0.05), 0.58)) @ Matrix.Rotation(R(-sx * 9 + rng.uniform(-2, 2)), 4, 'Y')
                    t = rng.uniform(0.86, 1.0); mb.add(xf(v, M), f, wi, col=(t, t, t))
                for sy in (-1, 1):
                    v, f = box((TH - 0.2, 0.36, 0.36), (0, 0, 0), 0.05)
                    M = Matrix.Translation((sx * 4.9, sy * 1.5, 0.18)) @ Matrix.Rotation(R(sx * sy * 28 + rng.uniform(-8, 8)), 4, 'Z')
                    mb.add(xf(v, M), f, wi + 1)
            v, f = box((6.4, 0.26, 0.26), (0, 0, 0), 0.05)
            mb.add(xf(v, Matrix.Translation((0.3, -2.3, 0.13)) @ Matrix.Rotation(R(7), 4, 'Z')), f, wi + 1)
    def cloth(mb, squished, wi=0):
        W = 4.4
        if not squished:
            prof = [(-TD / 2 - 0.05, TH - 1.25), (-TD / 2 - 0.07, TH - 0.6), (-TD / 2 - 0.04, TH + 0.035), (0, TH + 0.04), (TD / 2 + 0.04, TH + 0.035), (TD / 2 + 0.07, TH - 0.6), (TD / 2 + 0.05, TH - 1.25)]
        else:
            prof = [(-TD / 2 - 1.2, 0.03), (-TD / 2 - 0.3, 0.2), (-TD / 2 + 0.3, 0.72), (0, 0.80), (TD / 2 - 0.3, 0.72), (TD / 2 + 0.3, 0.2), (TD / 2 + 1.2, 0.03)]
        NX = 12
        V, UV, F = [], [], []
        ln = 0
        acc = [0]
        for i in range(1, len(prof)):
            acc.append(acc[-1] + math.hypot(prof[i][0] - prof[i - 1][0], prof[i][1] - prof[i - 1][1]))
        for i, (y, z) in enumerate(prof):
            for k in range(NX + 1):
                x = -W / 2 + W * k / NX
                zz = z
                if squished:
                    zz = (0.45 + 0.16 * abs(x) + 0.02 * math.sin(k * 1.7 + i)) if z > 0.3 else z + 0.02 * math.sin(k * 1.7 + i) + 0.02
                elif i in (0, len(prof) - 1):
                    zz = z + 0.07 * math.sin(k * 1.3)
                V.append((x, y + (0.05 * math.sin(k * 2.1) if i in (0, 1, len(prof) - 2, len(prof) - 1) else 0), zz)); UV.append((x / 1.6, acc[i] / 1.6))
        for i in range(len(prof) - 1):
            for k in range(NX):
                a = i * (NX + 1) + k
                F.append([a, a + 1, a + NX + 2, a + NX + 1])
        mb.add(V, F, wi + 2, uv=UV)
    pmats = [m_crust] + fills + [m_cream]
    mb = MB(); table(mb, False); cloth(mb, False)
    tab = mb.obj('TS_PieTable', [m_wood, m_wood_dk, m_cloth], C, sharp=45)
    tab.location = (0, 0, 0)
    rng = random.Random(1)
    layout = [(-3.3, 0.2, 0.92, 1, 'plain'), (-1.3, -0.5, 0.80, 4, 'lattice'), (0.6, 0.55, 0.86, 2, 'cream'), (2.2, -0.45, 0.78, 3, 'plain'), (3.6, 0.5, 0.74, 1, 'lattice')]
    for i, (x, y, r, fi, kind) in enumerate(layout):
        mb = MB(); pie(mb, (0, 0, 0), r, fi, kind, rng)
        o = mb.obj(f'TS_Pie_{i + 1:02d}', pmats, C, parent=tab, sharp=45)
        o.location = (x, y, TH + (0.05 if abs(x) < 2.2 else 0.0))
    # squished
    mb = MB(); table(mb, True, 6); cloth(mb, True, 6)
    rng = random.Random(6)
    for i, (x, y, r, fi, kind) in enumerate(layout):
        px, py = x * 1.12 + rng.uniform(-0.3, 0.3), y * 1.5 - 1.6 * (i % 2) + rng.uniform(-0.3, 0.3)
        on_top = abs(px) < 2.0 and abs(py) < 1.2
        z = (0.47 + 0.16 * abs(px)) if on_top else (0.45 if abs(py) < 1.7 else 0.0)
        if z == 0.45:
            py = -2.9 - 0.3 * i if py < 0 else 2.9; z = 0.0
        splat(mb, (px, py, z + 0.02), r * 1.25, fi, rng)
        pie(mb, (px + rng.uniform(-0.15, 0.15), py + rng.uniform(-0.15, 0.15), z + 0.02), r * 1.12, fi, 'plain', rng, squash=0.3)
    sq = mb.obj('TS_PieTable_Squished', pmats + [m_wood, m_wood_dk, m_cloth], C, sharp=45)
    sq.location = (14, 0, 0)

    # ------------------------------------------------------------ golden apples
    def apple(name, r, loc, rot=None):
        mb = MB()
        v, f = apple_mesh(r, 16)
        mb.add(v, f, 0)
        sv, sf, _ = tube(spline([(0, 0, 1.62 * r), (0.05 * r, 0, 1.95 * r), (0.16 * r, 0, 2.2 * r)], 5), 0.07 * r, 6)
        mb.add(sv, sf, 1, col=tint('#5E3F27', '#AC7F52'))
        lv, lf = leaf(0.8 * r, 0.5, 0.12, 0.25)
        mb.add(align(lv, Vector((0.9, 0.2, 0.35)), (0.05 * r, 0, 1.95 * r), axis='Y'), lf, 2)
        if rot is not None:
            M = Matrix.Translation((0, 0, r * 0.93)) @ rot @ Matrix.Translation((0, 0, -r * 0.93))
            for k in range(len(mb.V)):
                mb.V[k] = xf(mb.V[k], M)
            zmin = min(v_[:, 2].min() for v_ in mb.V[:1])
            for k in range(len(mb.V)):
                mb.V[k] = mb.V[k] - np.array((0, 0, zmin))
        o = mb.obj(name, [m_gold, m_bark, m_leaf], C, sharp=50)
        o.location = loc
        return o
    apple('TS_Apple_Single', 0.5, (24, 0, 0))
    apple('TS_Apple_Loose_01', 0.5, (26.5, -0.4, 0), Matrix.Rotation(R(68), 4, 'X') @ Matrix.Rotation(R(20), 4, 'Z'))
    apple('TS_Apple_Loose_02', 0.46, (27.8, 0.5, 0), Matrix.Rotation(R(-80), 4, 'Y'))
    apple('TS_Apple_Loose_03', 0.54, (29.2, -0.2, 0), Matrix.Rotation(R(18), 4, 'Y') @ Matrix.Rotation(R(140), 4, 'Z'))
