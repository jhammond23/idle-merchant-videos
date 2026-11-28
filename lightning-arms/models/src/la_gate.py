# Lightning Arms: LA_GateOfOaths. Form (a): the gate, a carved stone arch 27.9 BU tall with rows of stone arms set in its walls,
# burned glowing numbers and a carved face (eyes closed -> glowing open with the `eyes` property).
# The same pieces, scaled up, are the torso and head of the standing giant (la_giant.py).
from la_lib import *

HX = 7.6            # pillar centre x
PW, PD = 5.2, 4.4   # pillar width, depth
Z_SPRING = 14.0     # where the arch starts
R_IN = 5.0          # opening radius
Z_SH = 20.6         # top of the shoulders
YF = -PD / 2        # front face of the walls
HEAD_C = (0, -0.7, 22.75); HEAD_S = (10.4, 6.0, 7.3)
HYF = HEAD_C[1] - HEAD_S[1] / 2          # front face of the head block
EYE_X, EYE_Z = 2.45, 23.75
LID_TRAVEL = 1.42
GATE_H = 27.9
NUMBERS = [('1 IN 2', (-7.9, 17.5), 1.75), ('1 IN 40', (7.9, 17.5), 1.5), ('1 IN 9', (-7.75, 0.86), 0.95), ('1 IN 300', (7.75, 0.86), 0.85)]


def pieces(seed=11):
    """every piece of the arch: dict(v, f, part, mat, col, flat, fj). parts: 'wall' (pillars, arch, shoulders), 'head', 'lid', 'eye',
    'num', 'plate'. mats: 0 stone, 1 arm stone, 2 dark recess, 3 moss."""
    rng = random.Random(seed)
    out = []
    sd = [seed * 10]

    def add(v, f, part='wall', mat=0, col=(1, 1, 1), flat=True, fj=0.12, shade=None):
        out.append(dict(v=np.asarray(v, float), f=f, part=part, mat=mat, col=col, flat=flat, fj=fj, shade=shade))

    def rock(size, c, part='wall', col=(0.94, 0.94, 0.94), **kw):
        sd[0] += 1
        kw.setdefault('sub', 4); kw.setdefault('amp', 0.03); kw.setdefault('cuts', 5); kw.setdefault('depth', (0.86, 0.97)); kw.setdefault('rnd', 0.04)
        v, f = crag(size, c, seed=sd[0], **kw)
        add(v, f, part, 0, rockcol(col, sd[0], scale=0.16), shade=(v[:, 2].min(), v[:, 2].max(), 0.86))
        return v

    def moss(c, size):
        sd[0] += 1
        v, f = crag(size, c, seed=sd[0], sub=3, amp=0.12, cuts=3, rnd=0.35)
        add(v, f, 'wall', 3, rockcol((1, 1, 1), sd[0], scale=0.4, amp=0.25), fj=0.2)

    for s in (-1, 1):
        x = s * HX
        rock((6.6, 5.8, 1.7), (x, 0, 0.83), col=(0.80, 0.80, 0.84), floor=0.0)                       # plinth
        z = 1.55
        for k, h in enumerate((3.0, 2.8, 3.0, 2.8)):                                                # shaft drums (4 courses)
            rock((PW + rng.uniform(-0.12, 0.12), PD + rng.uniform(-0.1, 0.1), h + 0.12), (x + rng.uniform(-0.06, 0.06), 0, z + h / 2),
                 col=(0.9 + 0.08 * (k % 2),) * 3, protect=None)
            z += h
        rock((6.3, 5.4, 1.15), (x, 0, 13.5), col=(0.78, 0.78, 0.83))                                 # capital
        rock((5.6, 4.9, 0.5), (x, 0, 12.75), col=(0.86, 0.86, 0.9))
        moss((x + s * 1.2, 0.6, 14.12), (2.6, 2.4, 0.4))
    # arch ring: 9 voussoirs, proud of the wall
    n = 9
    for i in range(n):
        if i == n // 2:
            continue                                                                               # the head sits where the keystone would be
        a0 = math.pi * i / n; a1 = math.pi * (i + 1) / n; am = (a0 + a1) / 2
        rm = R_IN + 0.95
        size = (2 * rm * math.sin((a1 - a0) / 2) * 1.04, PD + 0.7, 1.9)
        rot = Matrix.Rotation(am - math.pi / 2, 4, 'Y')                                             # local Z -> radial
        sd[0] += 1
        v, f = crag(size, (0, 0, 0), seed=sd[0], sub=3, amp=0.03, cuts=4, depth=(0.86, 0.97), rnd=0.04, taper=(1.12, 1.0))
        M = Matrix.Translation((rm * math.cos(am), 0, Z_SPRING + rm * math.sin(am))) @ Matrix.Rotation(math.pi / 2 - am, 4, 'Y')
        v = xf(v, M)
        add(v, f, 'wall', 0, rockcol((0.80 + 0.1 * (i % 2),) * 3, sd[0], scale=0.16), shade=None)
    # shoulder wall: rectangle minus the round opening
    na = 28; r0 = R_IN + 0.5; X1 = HX + PW / 2
    outer = [(X1, Z_SPRING), (X1, Z_SH), (-X1, Z_SH), (-X1, Z_SPRING)]
    olen = [0, Z_SH - Z_SPRING, Z_SH - Z_SPRING + 2 * X1, 2 * (Z_SH - Z_SPRING) + 2 * X1]
    V = []; F = []
    for i in range(na + 1):
        a = math.pi * i / na
        A = (r0 * math.cos(a), Z_SPRING + r0 * math.sin(a))
        # matching point on the outer outline: straight up from the springing, across the top
        if i <= 5:
            B = (X1, Z_SPRING + (Z_SH - Z_SPRING) * i / 5)
        elif i >= na - 5:
            B = (-X1, Z_SPRING + (Z_SH - Z_SPRING) * (na - i) / 5)
        else:
            B = (X1 - 2 * X1 * (i - 5) / (na - 10), Z_SH)
        for y in (YF + 0.1, -YF - 0.1):
            V += [(A[0], y, A[1]), (B[0], y, B[1])]
    for i in range(na):
        b = i * 4
        F += [[b, b + 1, b + 5, b + 4], [b + 2, b + 6, b + 7, b + 3], [b, b + 4, b + 6, b + 2], [b + 1, b + 3, b + 7, b + 5]]
    F += [[0, 2, 3, 1], [na * 4, na * 4 + 1, na * 4 + 3, na * 4 + 2]]
    add(np.array(V), F, 'wall', 0, rockcol((0.84, 0.84, 0.87), 5, scale=0.12), flat=True, fj=0.0)
    # courses on the shoulder front and back (so the wall is never one flat slab), cornice
    for y in (YF - 0.05, -YF + 0.05):
        for s in (-1, 1):
            rock((4.9, 0.9, 2.9), (s * 7.75, y, 15.65), col=(0.95, 0.95, 0.95), cuts=4)
            rock((5.6, 0.75, 2.4), (s * 7.4, y, 19.3), col=(0.80, 0.80, 0.84), cuts=4)
    for s in (-1, 1):
        rock((6.4, PD + 1.3, 1.25), (s * 7.35, 0, Z_SH + 0.45), col=(0.74, 0.74, 0.80))                 # cornice blocks
        rock((2.0, PD + 0.6, 1.5), (s * 9.3, 0, Z_SH + 1.6), col=(0.86, 0.86, 0.9))                     # corner merlons
        moss((s * 6.6, 0.4, Z_SH + 1.15), (3.2, 3.0, 0.42))
    # ---- head: the carved face
    rock(HEAD_S, HEAD_C, 'head', col=(1.0, 0.99, 0.96), sub=5, cuts=7, depth=(0.88, 0.97), protect=(0, -1, 0), pamp=0.15)
    HT = HEAD_C[2] + HEAD_S[2] / 2
    rock((11.2, 6.4, 1.25), (0, -0.7, HT + 0.3), 'head', col=(0.74, 0.74, 0.82), cuts=5)                 # cap stone
    rock((3.4, 4.8, 0.9), (0, -0.6, HT + 1.05), 'head', col=(0.9, 0.9, 0.93), cuts=4)
    moss((2.4, 0.2, HT + 0.98), (3.6, 3.4, 0.4))
    out[-1]['part'] = 'head'
    rock((9.9, 1.7, 1.9), (0, HYF - 0.5, EYE_Z + 1.36), 'head', col=(0.72, 0.72, 0.80), cuts=4, amp=0.02)   # brow
    v, f = tbox((1.9, 1.7, 3.5), (0, HYF - 0.6, EYE_Z - 0.95), 0.2, 2, taper=(0.6, 0.5)); add(v, f, 'head', 0, (0.88, 0.88, 0.92), fj=0.05)   # nose
    for s in (-1, 1):
        v, f = tbox((3.1, 0.5, 1.8), (s * EYE_X, HYF + 0.05, EYE_Z), 0.05, 1); add(v, f, 'head', 2, flat=True, fj=0)                   # socket
        v, f = tbox((2.9, 1.2, 1.3), (s * 2.95, HYF - 0.2, EYE_Z - 1.75), 0.24, 2, rot=EU(0, s * 8, 0)); add(v, f, 'head', 0, (0.93, 0.93, 0.96), fj=0.05)  # cheek
        v, f = tbox((2.6, 0.36, 1.2), (s * EYE_X, HYF - 0.06, EYE_Z), 0.2, 2); add(v, f, 'eye', 0, flat=False, fj=0)
        # lid: closed it covers the eye; a carved lash line along its lower edge
        v, f = tbox((2.95, 0.62, 1.5), (s * EYE_X, HYF - 0.22, EYE_Z), 0.14, 2); add(v, f, 'lid', 0, (1.0, 1.0, 1.0), flat=False, fj=0)
        v, f = tbox((2.5, 0.12, 0.22), (s * EYE_X, HYF - 0.54, EYE_Z - 0.36), 0.03, 1); add(v, f, 'lid', 2, flat=True, fj=0)
        for k in (-1, 1):
            v, f = tbox((0.5, 0.12, 0.22), (s * EYE_X + k * 1.2, HYF - 0.54, EYE_Z - 0.26), 0.03, 1, rot=EU(0, -k * 28, 0)); add(v, f, 'lid', 2, flat=True, fj=0)
    MZ = EYE_Z - 3.35
    v, f = tbox((4.4, 0.3, 0.34), (0, HYF - 0.05, MZ), 0.04, 1); add(v, f, 'head', 2, fj=0)                                             # calm mouth line
    for s in (-1, 1):
        v, f = tbox((0.7, 0.3, 0.34), (s * 2.42, HYF - 0.05, MZ + 0.11), 0.04, 1, rot=EU(0, -s * 24, 0)); add(v, f, 'head', 2, fj=0)
    v, f = tbox((3.8, 0.85, 0.7), (0, HYF - 0.2, MZ - 0.62), 0.16, 2); add(v, f, 'head', 0, (0.92, 0.92, 0.95), fj=0.05)                # lower lip / chin
    for k in range(5):                                                                                                             # carved beard
        hh = 1.35 - 0.2 * abs(k - 2)
        v, f = tbox((1.2, 0.85, hh), ((k - 2) * 1.4, HYF - 0.2, HEAD_C[2] - HEAD_S[2] / 2 + 0.1 + hh / 2 + 0.12 * abs(k - 2)), 0.16, 2)
        add(v, f, 'head', 0, (0.74 + 0.08 * (k % 2),) * 3, fj=0.05)
    # ---- rows of stone arms set into the walls
    AW = 0.84

    def arm_at(p, n, kind, k, scale=1.0, droop=6.0, part='wall'):
        """a carved stone arm standing out of the wall at p along n (all alike in a row, like trophies on a rack)."""
        v, f = arm_proto(kind, k % 2, AW, 3.3)
        v = v - np.array((0, 0, 3.3 * 0.42))                       # the upper arm stays inside the stone
        n = Vector(n).normalized()
        q = Vector((0, 0, 1)).rotation_difference(n)
        up = q.inverted() @ Vector((0, 0, 1))                      # turn every palm to the sky
        spin = math.degrees(math.atan2(up.x, -up.y))
        M = Matrix.Translation(Vector(p)) @ q.to_matrix().to_4x4() @ EU(0, 0, spin + 180) @ EU(droop, 0, 0)
        g = 0.90 + 0.05 * (k % 3)
        add(xf(v * scale, M), f, part, 1, rockcol((g, g * 1.01, g * 0.97), k, scale=0.5, amp=0.12), flat=True, fj=0.07)
        cv, cf = tbox((AW * 1.55, AW * 1.55, 0.34), (0, 0, 0.05), 0.07, 1)                       # carved collar round the root
        add(xf(cv * scale, Matrix.Translation(Vector(p)) @ q.to_matrix().to_4x4()), cf, part, 0, (0.72, 0.72, 0.78), fj=0)

    k = 0
    for s in (-1, 1):
        for row in range(7):
            z = 2.9 + row * 1.5
            kind = ('open', 'fist', 'reach')[row % 3]
            for c in range(3):                                     # front and back: three to a row
                x = s * HX + (c - 1) * 1.62
                arm_at((x, YF - 0.02, z), (0, -1, 0), kind, k); arm_at((x, -YF + 0.02, z), (0, 1, 0), kind, k + 1); k += 1
            for c in range(2):                                     # outer side: two to a row
                arm_at((s * (HX + PW / 2 + 0.02), (c - 0.5) * 1.9, z), (s, 0, 0), kind, k); k += 1
            if row % 2 == 0:                                       # inside the opening: one, shorter
                arm_at((s * (HX - PW / 2 - 0.02), 0, z), (-s, 0, 0), kind, k, scale=0.85); k += 1
    # ---- burned numbers: charred plaques with ember numerals
    for (txt, (x, z), sz) in NUMBERS:
        if sz == 0:
            continue
        for (y, ry) in ((YF - (0.62 if z > 5 else 0.82), 0), (-YF + (0.62 if z > 5 else 0.82), 180)):
            Mn = Matrix.Translation((x * (1 if ry == 0 else -1), y, z)) @ EU(0, 0, ry)
            v, f = text_mesh(txt, sz, 0.16)
            wd = v[:, 0].max() - v[:, 0].min()
            pv, pf = tbox((wd + 0.8, 0.5, sz * 1.5), (0, 0.26, 0), 0.08, 1)
            add(xf(pv, Mn), pf, 'plate', 2, fj=0)
            add(xf(v, Mn), f, 'num', 0, flat=True, fj=0)
    return out


def mats():
    stone = stone_mat('GateStone', '#B7B2C6', bump=0.4, scale=0.3, mottle=0.16)
    armst = stone_mat('GateArmStone', '#C6C7CC', bump=0.45, scale=0.9, mottle=0.16, ao=False)
    dark = mat('GateDark', '#3A3440', 0.95)
    mossm = stone_mat('GateMoss', '#4F7A36', bump=0.5, scale=1.4, mottle=0.2, ao=False)
    eye = attr_mat('GateEye', '#FFC54A', 26.0, attr='eyes', base_hex='#5A4A2A', floor=0.0)
    num = emit_mat('GateNumber', '#FF7A1E', 7.0, base_hex='#FFB060')
    return stone, armst, dark, mossm, eye, num


def build(root):
    C = coll('LA_GateOfOaths', root)
    stone, armst, dark, mossm, eye, num = mats()
    P = pieces()
    groups = {'body': MB(), 'lid': MB(), 'eye': MB(), 'num': MB()}
    for p in P:
        g = {'wall': 'body', 'head': 'body', 'plate': 'body'}.get(p['part'], p['part'])
        groups[g].add(p['v'], p['f'], p['mat'], col=p['col'], fjit=p['fj'], flat=p['flat'], shade=p['shade'])
    body = groups['body'].obj('LA_Gate', [stone, armst, dark, mossm], C)
    prop(body, 'eyes', 0.0, '0 = eyes closed, 1 = eyes open and glowing')
    prop(body, 'shake', 0.0, 'flag for the builder: 1 while the gate shakes (see la_helpers.set_shake)')
    lids = groups['lid'].obj('LA_Gate_Lids', [stone, armst, dark], C, parent=body)
    follow(lids, body, 'eyes', 'location', gain=LID_TRAVEL, index=2)
    eyes = groups['eye'].obj('LA_Gate_Eyes', [eye], C, parent=body); follow(eyes, body, 'eyes'); noshadow(eyes)
    nums = groups['num'].obj('LA_Gate_Numbers', [num], C, parent=body); noshadow(nums)
    lo = point_light('LA_Gate_EyeLight', C, body, '#FFC060', 1.2, (0, HYF - 2.0, EYE_Z)); follow(lo.data, body, 'eyes', 'energy', gain=2500.0)
    # dust and grit for the shake (hidden by default)
    rng = random.Random(5); mb = MB()
    dm = mat('GateDust', '#B9B2A6', 1.0)
    for i in range(70):
        x = rng.uniform(-10.5, 10.5); z = rng.uniform(1.0, 21.0); y = rng.choice((-1, 1)) * rng.uniform(2.6, 4.2)
        if abs(x) < 4.6 and z < 18:
            y = rng.uniform(-2, 2); z = rng.uniform(13.5, 18.5)
        r = rng.uniform(0.08, 0.3)
        v, f = blob((x, y, z), (r, r, r * rng.uniform(1.0, 2.2)), sub=1, amp=0.2, seed=i, cuts=2)
        mb.add(v, f, 0, col=(rng.uniform(0.6, 1.0),) * 3, flat=True)
    for i in range(14):                                                    # dust puffs at the feet of the pillars and off the cornice
        s = rng.choice((-1, 1)); top = i >= 9
        c = (s * (HX + rng.uniform(-3.4, 3.4)), rng.choice((-1, 1)) * rng.uniform(2.8, 4.0), rng.uniform(0.3, 1.1) if not top else rng.uniform(19, 21.5))
        r = rng.uniform(0.7, 1.5)
        v, f = blob(c, (r * 1.3, r, r * 0.8), sub=2, amp=0.18, seed=100 + i, floor=0.02)
        mb.add(v, f, 1, flat=False)
    puff = bpy.data.materials.new('LA_Mat_GateDustPuff'); puff.use_nodes = True
    b = puff.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (*lin('#CFC6B6'), 1); b.inputs['Alpha'].default_value = 0.55; b.inputs['Roughness'].default_value = 1.0
    dust = mb.obj('LA_Gate_ShakeDust', [dm, puff], C, parent=body); noshadow(dust)
    dust.hide_render = dust.hide_viewport = True
    e = empty('LA_Gate_Socket_HeadTop', C, (0, -0.7, GATE_H), 'PLAIN_AXES', 2.0, parent=body)
    for s, n in ((-1, 'R'), (1, 'L')):
        empty('LA_Gate_Socket_Chain' + n, C, (s * 6.1, YF - 0.6, 13.6), 'SPHERE', 0.5, parent=body)
        empty('LA_Gate_Socket_ChainTop' + n, C, (s * 9.6, YF - 0.9, Z_SH - 0.3), 'SPHERE', 0.5, parent=body)
    empty('LA_Gate_Mark_KidAtGate', C, (0, -9, 0), 'ARROWS', 1.5, parent=body)
    return {'gate': {'height': GATE_H, 'width': 2 * (HX + 3.3), 'opening': [2 * R_IN, Z_SPRING + R_IN], 'eye_centre': [EYE_X, HYF, EYE_Z],
                     'numbers': [n[0] for n in NUMBERS if n[2]]}}
