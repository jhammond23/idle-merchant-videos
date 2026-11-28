# Lightning Arms: LA_WarBeast. A heavy blocky horned war beast (bull / rhino), about 22 BU at the shoulder hump, armoured, harnessed.
# Faces -Y. L = +X (its own left). Rigid chunks, each on one bone, so nothing stretches. Fierce but kid-safe: no fangs, amber eyes.
from la_lib import *

Y = Vector((0, 1, 0))
FA = {'L': (5.5, -6.8, 1.9), 'R': (-5.5, -6.8, 1.9)}       # rest ankles, front
RA = {'L': (5.3, 11.2, 1.9), 'R': (-5.3, 11.2, 1.9)}       # rest ankles, rear
HEAD_M = Matrix.Translation((0, -17.6, 12.7)) @ EU(20, 0, 0)
RING_REAR = (0, 15.75, 14.6); RING_COLLAR = (0, -13.3, 8.35)


def bones_def():
    B = [('LA_Root', (0, 0, 0), (0, 0, 3), None, False),
         ('LA_Body', (0, 2, 13), (0, 2, 17), 'LA_Root', False),
         ('LA_Hips', (0, 3, 13.2), (0, 13.5, 13.2), 'LA_Body', False),
         ('LA_Chest', (0, 3, 13.2), (0, -8.5, 14.2), 'LA_Body', False),
         ('LA_Neck', (0, -8.5, 14.6), (0, -14, 13.4), 'LA_Chest', False),
         ('LA_Head', (0, -14, 13.4), (0, -21, 11), 'LA_Neck', False),
         ('LA_Tail', (0, 14.8, 15.5), (0, 17.5, 9), 'LA_Hips', False)]
    for sd, s in (('L', 1), ('R', -1)):
        B += [(f'LA_FrontUpper{sd}', (s * 5.3, -6.5, 12.5), (s * 5.5, -7.2, 6.6), 'LA_Chest', False),
              (f'LA_FrontLower{sd}', (s * 5.5, -7.2, 6.6), (s * 5.5, -6.8, 1.9), f'LA_FrontUpper{sd}', True),
              (f'LA_FrontHoof{sd}', (s * 5.5, -6.8, 1.9), (s * 5.5, -8.6, 0.4), f'LA_FrontLower{sd}', True),
              (f'LA_RearUpper{sd}', (s * 5.0, 10.5, 12.5), (s * 5.3, 12.3, 6.8), 'LA_Hips', False),
              (f'LA_RearLower{sd}', (s * 5.3, 12.3, 6.8), (s * 5.3, 11.2, 1.9), f'LA_RearUpper{sd}', True),
              (f'LA_RearHoof{sd}', (s * 5.3, 11.2, 1.9), (s * 5.3, 9.4, 0.4), f'LA_RearLower{sd}', True)]
    return B


def ring(c, rad, r, axis='Y', segs=14):
    pts = []
    for i in range(segs + 2):
        a = 2 * math.pi * i / segs
        if axis == 'Y':
            pts.append((c[0] + rad * math.cos(a), c[1], c[2] + rad * math.sin(a)))
        elif axis == 'X':
            pts.append((c[0], c[1] + rad * math.cos(a), c[2] + rad * math.sin(a)))
        else:
            pts.append((c[0] + rad * math.cos(a), c[1] + rad * math.sin(a), c[2]))
    v, f, _ = tube(pts, r, segs=6, cap0=False, cap1=False)
    return v, f


def build(root):
    C = coll('LA_WarBeast', root)
    hide = stone_mat('BeastHide', '#5B3526', rough=0.8, bump=0.22, scale=0.5, mottle=0.13, ao=True)
    pale = stone_mat('BeastHidePale', '#9C7556', rough=0.8, bump=0.18, scale=0.6, mottle=0.1, ao=True)
    iron = metal('BeastIron', '#4A5364', rough=0.42, metallic=0.85)
    brass = metal('BeastBrass', '#E2A93B', rough=0.3)
    horn = stone_mat('BeastHorn', '#F3E6C4', rough=0.5, bump=0.1, scale=1.2, mottle=0.08, ao=False)
    hoof = mat('BeastHoof', '#33291F', 0.6)
    cloth = stone_mat('BeastCloth', '#C4281C', rough=0.9, bump=0.3, scale=3.0, mottle=0.1, ao=False)
    leather = stone_mat('BeastLeather', '#5A3620', rough=0.7, bump=0.3, scale=2.0, mottle=0.12, ao=False)
    eye = mat('BeastEye', '#FFB21E', 0.3, emit='#FFA816', estr=2.2, vcol=False)
    dark = mat('BeastDark', '#1E1814', 0.5, vcol=False)
    white = mat('BeastGlint', '#FFFFFF', 0.3, emit='#FFFFFF', estr=1.0, vcol=False)
    chain_m = metal('BeastChain', '#6B7382', rough=0.4, metallic=0.9)
    MATS = [hide, pale, iron, brass, horn, hoof, cloth, leather, eye, dark, white]
    HIDE, PALE, IRON, BRASS, HORN, HOOF, CLOTH, LEATHER, EYE, DARK, WHITE = range(11)
    arm = make_arm('LA_WarBeast_Rig', bones_def(), C)
    mb = MB()
    sd = [0]

    def part(v, f, bone, m=HIDE, col=(1, 1, 1), flat=False, fj=0.0, shade=None):
        sd[0] += 1
        c = rockcol(col, sd[0], scale=0.12, amp=0.12) if m in (HIDE, PALE, CLOTH) else col
        mb.add(v, f, m, col=c, flat=flat, fjit=fj, w=bone, shade=shade)

    def bx(size, c, bone, m=HIDE, col=(1, 1, 1), bevel=None, taper=(1.0, 1.0), rot=None, M=None, segs=3, shade=None):
        bevel = min(size) * 0.16 if bevel is None else bevel
        v, f = tbox(size, c, bevel, segs, taper, rot)
        if M is not None:
            v = xf(v, M)
        part(v, f, bone, m, col, shade=shade)

    def rivets(pts, bone, r=0.28, M=None):
        for p in pts:
            v, f = ico(1)
            v = v * r + np.array(p, float)
            if M is not None:
                v = xf(v, M)
            mb.add(v, f, BRASS, w=bone)

    # ---- trunk
    bx((12.4, 13.6, 11.2), (0, 8.4, 13.3), 'LA_Hips', taper=(0.86, 0.96), shade=(7.7, 14, 0.72))
    bx((10.4, 12.0, 2.2), (0, 8.2, 8.0), 'LA_Hips', PALE)
    bx((13.8, 13.6, 13.0), (0, -2.4, 13.9), 'LA_Chest', taper=(0.86, 1.0), shade=(7.4, 14, 0.72))
    bx((10.8, 10.0, 5.4), (0, -3.2, 19.5), 'LA_Chest', taper=(0.72, 0.72), col=(0.9, 0.86, 0.84))          # shoulder hump
    bx((11.0, 11.0, 2.2), (0, -2.6, 7.6), 'LA_Chest', PALE)
    bx((9.6, 8.6, 9.8), (0, -10.6, 14.0), 'LA_Neck', rot=EU(14, 0, 0))
    bx((6.0, 5.0, 3.0), (0, -10.8, 9.2), 'LA_Neck', PALE, rot=EU(14, 0, 0))                               # dewlap
    # mane ridge
    for k in range(5):
        bx((2.0, 2.4, 2.2 - 0.25 * k), (0, -7.5 + 2.6 * k * 0 - k * 2.3 + 5.0, 21.9 - 0.9 * abs(k - 1.2)), 'LA_Chest' if k < 4 else 'LA_Neck', DARK, bevel=0.4, rot=EU(-20, 0, 0))
    # ---- back armour: overlapping iron plates with brass rims, red cloth under them
    for (y, zz, w, ln, bone) in ((-3.2, 22.25, 8.4, 9.4, 'LA_Chest'), (4.6, 20.1, 11.6, 6.6, 'LA_Chest'), (10.6, 19.25, 11.4, 7.4, 'LA_Hips')):
        bx((w, ln, 0.8), (0, y, zz), bone, IRON, bevel=0.25)
        bx((w + 0.5, 0.7, 1.0), (0, y - ln / 2 + 0.2, zz), bone, BRASS, bevel=0.2)
        bx((w + 0.5, 0.7, 1.0), (0, y + ln / 2 - 0.2, zz), bone, BRASS, bevel=0.2)
        rivets([(s * (w / 2 - 0.9), y + k * ln / 4, zz + 0.45) for s in (-1, 1) for k in (-1, 0, 1)], bone)
        v, f, _ = tube([(0, y, zz + 0.3), (0, y, zz + 1.6), (0, y + 0.5, zz + 2.6)], [1.0, 0.7, 0.1], segs=6, cap0=False, cap1=True); part(v, f, bone, BRASS)   # blunt ridge stud
    for s in (-1, 1):
        # flank cloths (the Warlord's red) with brass hems
        bx((0.5, 10.4, 7.6), (s * 6.55, 8.6, 14.6), 'LA_Hips', CLOTH, bevel=0.15, rot=EU(0, -s * 5, 0))
        bx((0.7, 10.6, 0.8), (s * 6.9, 8.6, 10.75), 'LA_Hips', BRASS, bevel=0.15)
        bx((0.5, 6.0, 6.0), (s * 7.05, 3.0, 15.6), 'LA_Chest', CLOTH, bevel=0.15, rot=EU(0, -s * 4, 0))
        bx((0.7, 6.2, 0.8), (s * 7.3, 3.0, 12.6), 'LA_Chest', BRASS, bevel=0.15)
        # shoulder plates
        bx((1.3, 8.6, 7.6), (s * 7.2, -4.0, 16.4), 'LA_Chest', IRON, bevel=0.3, rot=EU(0, -s * 9, 0), taper=(1.0, 0.8))
        bx((1.5, 8.9, 0.9), (s * 7.75, -4.0, 12.8), 'LA_Chest', BRASS, bevel=0.2)
        rivets([(s * 7.95, -4.0 + k * 2.6, 16.6 + j * 2.0) for k in (-1, 0, 1) for j in (-1, 0)], 'LA_Chest', 0.34)
        # girth strap + flank ring (chain point)
        bx((0.6, 1.6, 12.0), (s * 6.75, 4.4, 13.6), 'LA_Hips', LEATHER, bevel=0.15, rot=EU(0, -s * 4.5, 0))
        bx((1.0, 1.6, 1.6), (s * 7.1, 4.4, 13.0), 'LA_Hips', IRON, bevel=0.2)
        v, f = ring((s * 7.75, 4.4, 12.1), 0.95, 0.22, 'X'); part(v, f, 'LA_Hips', IRON)
    bx((13.2, 1.6, 0.6), (0, 4.4, 7.05), 'LA_Hips', LEATHER, bevel=0.15)
    # rear plate with the ring for the sister's chain
    bx((6.0, 0.8, 4.4), (0, 15.25, 15.4), 'LA_Hips', IRON, bevel=0.25)
    rivets([(s * 2.3, 15.7, 15.4 + k * 1.5) for s in (-1, 1) for k in (-1, 1)], 'LA_Hips')
    v, f = ring(RING_REAR, 1.05, 0.26, 'X'); part(v, f, 'LA_Hips', IRON)
    bx((1.4, 1.0, 1.2), (0, 15.5, 15.75), 'LA_Hips', BRASS, bevel=0.2)
    # collar with the lead ring
    for (sz, c) in (((10.6, 1.9, 0.7), (0, -11.6, 19.0)), ((7.0, 1.9, 0.7), (0, -13.4, 9.35))):
        bx(sz, c, 'LA_Neck', LEATHER, bevel=0.2, rot=EU(14, 0, 0))
    for s in (-1, 1):
        bx((0.7, 1.9, 10.4), (s * 5.05, -12.4, 14.2), 'LA_Neck', LEATHER, bevel=0.2, rot=EU(14, 0, 0))
        rivets([(s * 5.45, -12.4 - 0.25 * k * 2.4, 14.2 + k * 2.4) for k in (-1.5, -0.5, 0.5, 1.5)], 'LA_Neck', 0.36)
    v, f = ring(RING_COLLAR, 0.95, 0.24, 'X'); part(v, f, 'LA_Neck', IRON)
    # ---- head (built level, then pitched 20 degrees nose-down)
    Hm = HEAD_M
    bx((9.0, 9.0, 7.8), (0, 0, 0), 'LA_Head', M=Hm, bevel=1.2)
    bx((7.6, 5.8, 5.0), (0, -6.6, -1.1), 'LA_Head', PALE, M=Hm, bevel=0.9, taper=(0.86, 1.0))
    bx((9.6, 7.4, 2.2), (0, -5.6, -3.7), 'LA_Head', HIDE, M=Hm, bevel=0.5, col=(0.72, 0.72, 0.72))     # broad lower jaw
    for s in (-1, 1):
        bx((1.2, 0.4, 0.9), (s * 1.75, -9.38, -0.4), 'LA_Head', DARK, M=Hm, bevel=0.12)                  # nostrils
        bx((0.3, 3.4, 0.3), (s * 3.74, -7.7, -2.62), 'LA_Head', DARK, M=Hm, bevel=0.05)                  # closed mouth line (sides)
        bx((2.5, 0.5, 1.5), (s * 2.9, -4.38, 1.75), 'LA_Head', DARK, M=Hm, bevel=0.1)                    # deep dark socket
        bx((1.5, 0.3, 0.74), (s * 2.85, -4.66, 1.7), 'LA_Head', EYE, M=Hm, bevel=0.08, rot=EU(0, s * 16, 0))    # small narrowed amber eye
        bx((0.4, 0.2, 0.74), (s * 2.7, -4.8, 1.7), 'LA_Head', DARK, M=Hm, bevel=0.05, rot=EU(0, s * 16, 0))     # slit pupil
        bx((0.16, 0.14, 0.16), (s * 2.95 + 0.2, -4.9, 1.9), 'LA_Head', WHITE, M=Hm, bevel=0.03)        # glint
        bx((4.6, 1.7, 1.5), (s * 2.75, -4.95, 3.2), 'LA_Head', HIDE, M=Hm, bevel=0.3, rot=EU(0, s * 21, 0), col=(0.6, 0.58, 0.58))   # heavy angled brow ridge, overhanging
        bx((4.3, 1.2, 0.6), (s * 2.8, -5.25, 4.1), 'LA_Head', IRON, M=Hm, bevel=0.15, rot=EU(0, s * 21, 0))     # iron brow plate on top
        bx((1.5, 4.6, 3.0), (s * 4.3, -6.4, -2.2), 'LA_Head', HIDE, M=Hm, bevel=0.4, col=(0.8, 0.8, 0.8))        # jowls: a wide heavy jaw
        bx((1.3, 0.9, 2.4), (s * 5.2, 2.2, 3.4), 'LA_Head', M=Hm, bevel=0.25, rot=EU(0, s * 40, 0))      # ear
        # the big curved horns
        P = [(s * 3.9, 0.4, 2.9), (s * 6.6, 0.3, 3.6), (s * 9.2, -1.4, 4.9), (s * 10.6, -4.6, 7.2), (s * 10.2, -8.0, 10.0)]
        P = [tuple(Hm @ Vector(p)) for p in P]
        pts = spline(P, 16)
        rad = np.linspace(1.75, 0.5, 16) ** 1.0; rad[-1] = 0.3; rad[-2] = 0.5
        v, f, rg = tube(pts, rad, segs=8, cap0=True, cap1=True, tip=1.2)
        mb.add(v, f, HORN, col=lambda p: (1, 1, 1), w='LA_Head', flat=False, shade=None)
        for i in (1, 4):
            v, f, _ = tube([pts[i], pts[i + 1]], rad[i] + 0.22, segs=8, cap0=False, cap1=False); part(v, f, 'LA_Head', BRASS if i == 4 else IRON)
    bx((6.6, 0.4, 0.3), (0, -9.38, -2.62), 'LA_Head', DARK, M=Hm, bevel=0.05)                            # mouth line (front)
    v, f = ring((0, -9.75, -2.2), 1.2, 0.24, 'Y'); part(xf(v, Hm), f, 'LA_Head', BRASS)                # nose ring
    P = [tuple(Hm @ Vector(p)) for p in ((0, -6.9, 1.0), (0, -7.9, 2.8), (0, -9.3, 4.3))]
    v, f, _ = tube(spline(P, 7), np.linspace(1.15, 0.22, 7), segs=8, cap0=False, cap1=True, tip=1.0); part(v, f, 'LA_Head', HORN)   # nose horn
    bx((6.4, 0.8, 2.3), (0, -4.7, 3.55), 'LA_Head', IRON, M=Hm, bevel=0.2)                               # forehead plate
    bx((5.6, 6.6, 0.7), (0, -1.2, 4.05), 'LA_Head', IRON, M=Hm, bevel=0.2)
    bx((1.2, 0.5, 1.2), (0, -5.15, 3.75), 'LA_Head', BRASS, M=Hm, bevel=0.2, rot=EU(0, 45, 0))
    # ---- legs
    for sdn, s in (('L', 1), ('R', -1)):
        bx((4.8, 5.4, 7.6), (s * 5.4, -6.8, 9.8), f'LA_FrontUpper{sdn}', taper=(1.1, 1.15))
        bx((3.9, 4.1, 5.8), (s * 5.5, -7.0, 4.3), f'LA_FrontLower{sdn}', col=(0.9, 0.86, 0.84))
        bx((4.3, 0.8, 4.4), (s * 5.5, -9.15, 4.4), f'LA_FrontLower{sdn}', IRON, bevel=0.2)                 # greave
        bx((4.5, 1.0, 0.8), (s * 5.5, -9.2, 6.6), f'LA_FrontLower{sdn}', BRASS, bevel=0.2)
        bx((4.6, 5.2, 2.0), (s * 5.5, -7.3, 1.0), f'LA_FrontHoof{sdn}', HOOF, taper=(0.86, 0.82), bevel=0.3)
        bx((5.4, 8.0, 7.8), (s * 4.9, 11.0, 10.2), f'LA_RearUpper{sdn}', taper=(1.08, 1.1))
        bx((3.7, 3.9, 5.8), (s * 5.3, 11.8, 4.3), f'LA_RearLower{sdn}', col=(0.9, 0.86, 0.84))
        bx((4.4, 5.0, 2.0), (s * 5.3, 10.9, 1.0), f'LA_RearHoof{sdn}', HOOF, taper=(0.86, 0.82), bevel=0.3)
    # ---- tail
    pts = spline([(0, 14.8, 16.2), (0, 16.9, 14.6), (0, 17.6, 11.5), (0, 17.5, 9.2)], 9)
    v, f, _ = tube(pts, np.linspace(0.75, 0.42, 9), segs=6, cap0=False, cap1=True); part(v, f, 'LA_Tail')
    v, f = blob((0, 17.5, 8.0), (0.95, 0.95, 1.7), sub=2, amp=0.12, seed=3); part(v, f, 'LA_Tail', DARK)
    body = mb.obj('LA_WarBeast_Body', MATS, C, arm=arm, sharp=38)

    # ---- sockets (follow the poses)
    def socket(name, bone, loc, size=1.0, kind='SPHERE'):
        e = empty('LA_WarBeast_Socket_' + name, C, kind=kind, size=size)
        bone_parent(e, arm, bone, Matrix.Translation(loc))
        return e
    socket('Rear', 'LA_Hips', (RING_REAR[0], RING_REAR[1] + 1.05, RING_REAR[2]))
    socket('Collar', 'LA_Neck', (RING_COLLAR[0], RING_COLLAR[1] - 0.2, RING_COLLAR[2] - 0.95))
    socket('FlankL', 'LA_Hips', (7.75, 4.4, 11.15)); socket('FlankR', 'LA_Hips', (-7.75, 4.4, 11.15))
    socket('Eyes', 'LA_Head', tuple(HEAD_M @ Vector((0, -4.6, 1.85))), kind='PLAIN_AXES')
    socket('Back', 'LA_Chest', (0, 4.6, 20.6), kind='ARROWS', size=2.0)

    # ---- chains (built for the STAND pose; for any other layout use la_helpers.chain_between with LA_WarBeast_Link)
    def chain_obj(name, path, hidden=False, cuff_open_at=None):
        cb = MB()
        chain(cb, path, L=1.15, W=0.72, r=0.15, mat=0)
        if cuff_open_at is not None:
            cuff(cb, cuff_open_at, open_=True)
        o = cb.obj(name, [chain_m, iron], C, parent=arm, sharp=50)
        o.hide_render = o.hide_viewport = hidden
        e = empty(name + '_End', C, path[-1], 'SPHERE', 0.4, parent=o)
        return o

    def cuff(cb, c, open_=False, M=None):
        """a small wrist cuff for the sister (inner 0.70, fits her 0.62 wrist), axis Z; open_: lying open on the ground."""
        P = []
        t = 0.13; inn = 0.36; h = 0.42
        if not open_:
            for (sz, cc) in (((2 * inn + 2 * t, t, h), (0, -inn - t / 2, 0)), ((2 * inn + 2 * t, t, h), (0, inn + t / 2, 0)),
                             ((t, 2 * inn + 2 * t, h), (-inn - t / 2, 0, 0)), ((t, 2 * inn + 2 * t, h), (inn + t / 2, 0, 0))):
                P.append(tbox(sz, cc, 0.03, 1))
            P.append(tbox((0.3, 0.2, 0.3), (0, inn + t + 0.08, 0), 0.04, 1))
        else:
            for (sz, cc, rz) in (((2 * inn + 2 * t, t, h), (0, inn + t / 2, 0), 0), ((t, 2 * inn + 2 * t, h), (-inn - t / 2, 0, 0), 0),
                                 ((t, 2 * inn + 2 * t, h), (inn + 0.3, -0.25, 0), 38), ((2 * inn + 2 * t, t, h), (0.5, -inn - 0.55, 0), 30)):
                P.append(tbox(sz, cc, 0.03, 1, rot=EU(0, 0, rz)))
        v, f = merge(P)
        if M is not None:
            v = xf(v, M)
        cb.add(v + np.array(c, float), f, 1, flat=False)

    R0 = np.array((RING_REAR[0], RING_REAR[1] + 1.0, RING_REAR[2]))
    end = np.array((0.0, 29.5, 1.55))
    chain_obj('LA_WarBeast_SisterChain_Taut', catenary(R0, end, 0.9, 10))
    slack = [R0, R0 + (0.2, 0.9, -4.0), R0 + (0.5, 1.4, -9.5), (0.9, 18.0, 0.2), (2.6, 21.0, 0.16), (1.0, 24.5, 0.16), (-0.8, 27.0, 0.2), (-0.2, 28.9, 0.7), end]
    chain_obj('LA_WarBeast_SisterChain_Slack', slack, hidden=True)
    drop = [R0, R0 + (0.2, 0.9, -4.0), R0 + (0.5, 1.4, -9.5), (0.9, 18.0, 0.2), (2.8, 20.6, 0.16), (1.2, 23.6, 0.16), (-1.2, 25.6, 0.16), (-0.6, 27.6, 0.16)]
    chain_obj('LA_WarBeast_SisterChain_Dropped', drop, hidden=True, cuff_open_at=(-0.3, 28.5, 0.22))
    cb = MB(); cuff(cb, (0, 0, 0))
    co = cb.obj('LA_WarBeast_Cuff', [chain_m, iron], C, parent=arm); co.location = tuple(end + (0, 0.5, 0))
    C0 = np.array((RING_COLLAR[0], RING_COLLAR[1] - 0.2, RING_COLLAR[2] - 0.9))
    chain_obj('LA_WarBeast_LeadChain_Taut', catenary(C0, (-11.0, -9.0, 8.2), 0.8, 10))
    chain_obj('LA_WarBeast_LeadChain_Dropped', [C0, C0 + (0, -0.3, -4.0), C0 + (-0.3, -0.8, -7.2), (-1.5, -16.0, 0.16), (-4.5, -17.5, 0.16), (-7.5, -15.5, 0.16), (-10.0, -16.5, 0.16)], hidden=True)
    lb = MB(); v, f = link_proto(1.15, 0.72, 0.15); lb.add(v, f, 0)
    lk = lb.obj('LA_WarBeast_Link', [chain_m], C, parent=arm); lk.location = (0, 0, -3); lk.hide_render = lk.hide_viewport = True
    lk['link_step'] = 1.15 - 2 * 0.15 * 1.55

    import la_beast_poses
    info = la_beast_poses.build(arm, body)
    info['shoulder_height'] = 22.2
    info['sister_chain_end'] = [round(x, 2) for x in end]
    return {'beast': info}
