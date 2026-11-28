# Lightning Arms: LA_GateGiant. Form (b): the Gate of Oaths standing up, 134 BU tall. The arch (scaled 2.3) is its torso, the carved
# face its head; its legs and arms are bundles of hundreds of stone arms. Awe, not horror: calm amber eyes, no teeth.
# Faces -Y. L = +X (its own left). Rigid chunks, each on one bone.
from la_lib import *
import la_gate as G
import la_props as P

K = 2.3
LEG = 70.0
J = dict(shoulder=(30.5, 0, 112.5), elbow=(35, 0, 80), wrist=(36, -2, 50), tip=(36, -3, 35),
         hip=(17.5, 0, 71), knee=(18, -2.5, 37), ankle=(18, 0, 6), toe=(18, -14, 1.5))
HEAD_PIV = (0, G.HEAD_C[1] * K, LEG + 19.3 * K)
TOP = LEG + G.GATE_H * K
Y = Vector((0, 1, 0))


def T(v):
    return np.asarray(v, float) * K + np.array((0, 0, LEG))


def mx(p, s):
    return (p[0] * s, p[1], p[2])


def bones_def():
    B = [('LA_Root', (0, 0, 0), (0, 0, 10), None, False),
         ('LA_Hips', (0, 0, 70), (0, 0, 78), 'LA_Root', False),
         ('LA_Spine', (0, 0, 78), (0, 0, 112), 'LA_Hips', False),
         ('LA_Head', HEAD_PIV, (HEAD_PIV[0], HEAD_PIV[1], TOP), 'LA_Spine', False)]
    for sd, s in (('L', 1), ('R', -1)):
        B += [(f'LA_Arm{sd}', mx(J['shoulder'], s), mx(J['elbow'], s), 'LA_Spine', False),
              (f'LA_Forearm{sd}', mx(J['elbow'], s), mx(J['wrist'], s), f'LA_Arm{sd}', True),
              (f'LA_Hand{sd}', mx(J['wrist'], s), mx(J['tip'], s), f'LA_Forearm{sd}', True),
              (f'LA_Thigh{sd}', mx(J['hip'], s), mx(J['knee'], s), 'LA_Hips', False),
              (f'LA_Shin{sd}', mx(J['knee'], s), mx(J['ankle'], s), f'LA_Thigh{sd}', True),
              (f'LA_Foot{sd}', mx(J['ankle'], s), mx(J['toe'], s), f'LA_Shin{sd}', True)]
    return B


def build(root):
    C = coll('LA_GateGiant', root)
    stone, armst, dark, mossm, eye, num = G.mats()
    iron, rune = P.chain_mats()
    arm = make_arm('LA_GateGiant_Rig', bones_def(), C)
    rng = random.Random(21)
    mb = MB(); lids = MB(); eyes = MB(); nums = MB()
    n_arms = [0]
    # ---- torso and head: the gate itself
    for p in G.pieces():
        v = T(p['v'])
        sh = p['shade']
        if sh:
            sh = (sh[0] * K + LEG, sh[1] * K + LEG, sh[2])
        col = p['col']
        if callable(col):
            col = (lambda c: (lambda q: c((np.asarray(q) - np.array((0, 0, LEG))) / K)))(col)
        if p['part'] == 'lid':
            lids.add(v, p['f'], p['mat'], col=col, flat=p['flat'], fjit=p['fj'])
        elif p['part'] == 'eye':
            eyes.add(v, p['f'], 0, flat=p['flat'])
        elif p['part'] == 'num':
            nums.add(v, p['f'], 0, flat=True)
        else:
            mb.add(v, p['f'], p['mat'], col=col, flat=p['flat'], fjit=p['fj'], shade=sh, w='LA_Head' if p['part'] == 'head' else 'LA_Spine')
    n_arms[0] += 126

    def frame(d):
        d = Vector(d).normalized()
        u = d.orthogonal().normalized(); v = d.cross(u)
        return d, u, v

    def one_arm(pos, along, out, s, bone, tilt=14.0, kind=None, spin=0.0):
        """a stone arm rooted at pos, lying along `along`, its palm side turned to `out`, hand end tilted outward."""
        along = Vector(along).normalized(); out = Vector(out); out = (out - along * out.dot(along)).normalized()
        xa = along.cross(out)                         # local X; local -Y = out; local Z = along
        M3 = Matrix((xa, -out, along)).transposed()
        M = Matrix.Translation(Vector(pos)) @ M3.to_4x4() @ EU(tilt, 0, spin)
        kd = kind or rng.choice(ARM_KINDS)
        v, f = arm_proto(kd, rng.randrange(5), 0.8, 3.3)
        g = rng.uniform(0.84, 1.0)
        mb.add(xf(v * s, M), f, 1, col=rockcol((g, g * 1.01, g * 0.97), rng.randrange(999), scale=0.08, amp=0.1), flat=True, fjit=0.07, w=bone)
        n_arms[0] += 1

    def bundle(p0, p1, r0, r1, bone, s, rings, per, core=0.74):
        p0 = Vector(p0); p1 = Vector(p1)
        d, u, v = frame(p1 - p0)
        ln = (p1 - p0).length
        pts = [p0 - d * 2.0, p0.lerp(p1, 0.5), p1 + d * 1.0]
        cv, cf, _ = tube([np.array(p) for p in pts], [r0 * core, (r0 + r1) / 2 * core, r1 * core], segs=8, cap0=True, cap1=True, tip=0.3)
        mb.add(cv, cf, 0, col=rockcol((0.5, 0.5, 0.55), rng.randrange(99), scale=0.1), flat=True, fjit=0.15, w=bone)
        arm_len = 4.3 * s
        for j in range(rings):
            t = j / rings
            c = p0 + d * (ln * t - arm_len * 0.12)
            r = r0 + (r1 - r0) * t
            for k in range(per):
                a = 2 * math.pi * (k + 0.5 * (j % 2)) / per + rng.uniform(-0.08, 0.08)
                rad = u * math.cos(a) + v * math.sin(a)
                one_arm(c + rad * (r - 0.36 * s), d, rad, s * rng.uniform(0.92, 1.08), bone, tilt=rng.uniform(9, 20), spin=rng.uniform(-10, 10))

    def knot(c, size, bone, n=7, s=3.0):
        """a joint: a rough stone knot with fists punching out of it."""
        v, f = crag(size, c, seed=rng.randrange(999), sub=3, amp=0.06, cuts=6)
        mb.add(v, f, 0, col=rockcol((0.62, 0.62, 0.68), rng.randrange(99), scale=0.1), flat=True, fjit=0.14, w=bone)
        for k in range(n):
            a = 2 * math.pi * k / n
            dr = Vector((math.cos(a), math.sin(a), rng.uniform(-0.3, 0.3))).normalized()
            one_arm(Vector(c) + dr * (min(size[0], size[1]) * 0.22), dr, Vector((0, 0, 1)), s, bone, tilt=0, kind='fist')

    for sd, s in (('L', 1), ('R', -1)):
        Sh, El, Wr, Tp = (Vector(mx(J[k], s)) for k in ('shoulder', 'elbow', 'wrist', 'tip'))
        Hp, Kn, An, To = (Vector(mx(J[k], s)) for k in ('hip', 'knee', 'ankle', 'toe'))
        # legs
        bundle(Hp, Kn, 11.5, 9.5, f'LA_Thigh{sd}', 3.9, 4, 9)
        knot(Kn, (17, 17, 11), f'LA_Shin{sd}', 6, 3.2)
        bundle(Kn, An + Vector((0, 0, 3)), 9.6, 8.0, f'LA_Shin{sd}', 3.7, 4, 8)
        v, f = crag((20, 27, 8.5), (s * 18, -5.5, 4.25), seed=70 + (s > 0), sub=4, amp=0.05, cuts=6, floor=0.0)
        mb.add(v, f, 0, col=rockcol((0.66, 0.66, 0.72), 7, scale=0.1), flat=True, fjit=0.14, w=f'LA_Foot{sd}')
        for k in range(5):                                         # toes: five arms laid forward, hands flat on the ground
            x = s * 18 + (k - 2) * 4.0
            one_arm((x, -14.5, 3.2), (0, -1, -0.06), (0, 0, -1), 3.2, f'LA_Foot{sd}', tilt=0, kind='open')
        for k in range(4):                                         # heel spurs
            one_arm((s * 18 + (k - 1.5) * 4.4, 6.0, 3.4), (0, 1, -0.1), (0, 0, -1), 2.6, f'LA_Foot{sd}', tilt=0, kind='fist')
        # arms
        knot(Sh + Vector((s * 0.5, 0, 1.0)), (17, 16, 15), f'LA_Arm{sd}', 7, 3.6)
        bundle(Sh, El, 8.6, 7.4, f'LA_Arm{sd}', 3.6, 4, 8)
        knot(El, (14, 14, 10), f'LA_Forearm{sd}', 5, 3.0)
        bundle(El, Wr + Vector((0, 0, 2)), 7.6, 6.4, f'LA_Forearm{sd}', 3.4, 4, 7)
        v, f = crag((14, 8.5, 11), tuple(Wr + Vector((0, -0.3, -4.5))), seed=90 + (s > 0), sub=3, amp=0.05, cuts=5)
        mb.add(v, f, 0, col=rockcol((0.66, 0.66, 0.72), 9, scale=0.1), flat=True, fjit=0.14, w=f'LA_Hand{sd}')
        for k in range(4):                                         # fingers: four arms hanging from the palm, a thumb arm
            one_arm(Wr + Vector(((k - 1.5) * 3.5, -0.5, -8.5)), (0, -0.12, -1), (0, -1, 0), 3.2, f'LA_Hand{sd}', tilt=4, kind='reach')
        one_arm(Wr + Vector((-s * 6.5, -1.0, -3.5)), (-s * 0.5, -0.3, -1), (0, -1, 0), 3.0, f'LA_Hand{sd}', tilt=0, kind='open')
        # broken chain trailing from each wrist
        cs = chain(mb, [Wr + Vector((s * 7.6, 0, 1)), Wr + Vector((s * 9.5, 0.5, -8)), Wr + Vector((s * 9.0, 1.0, -22))], L=3.4, W=2.2, r=0.46, mat=4, rune_mat=5, w=f'LA_Forearm{sd}')
        v, f = tbox((15.4, 14.4, 3.0), tuple(Wr + Vector((0, 0, 2.4))), 0.4, 2); mb.add(v, f, 4, w=f'LA_Forearm{sd}')        # iron wrist band
    # the swag chain across its chest opening
    y = G.YF * K - 2.0
    chain(mb, catenary((-6.3 * K, y, LEG + 13.9 * K), (6.3 * K, y, LEG + 13.9 * K), 4.6 * K, 16), L=3.4, W=2.2, r=0.46, mat=4, rune_mat=5, w='LA_Spine')
    body = mb.obj('LA_GateGiant_Body', [stone, armst, dark, mossm, iron, rune], C, arm=arm, sharp=38)
    prop(body, 'eyes', 1.0, '0 = eyes closed, 1 = eyes open and glowing'); prop(body, 'glow', 1.0, 'rune glow on its chains')
    lo_ = lids.obj('LA_GateGiant_Lids', [stone, armst, dark], C); bone_parent(lo_, arm, 'LA_Head', Matrix())
    follow(lo_, body, 'eyes', 'location', gain=G.LID_TRAVEL * K, index=2)
    eo = eyes.obj('LA_GateGiant_Eyes', [eye], C); bone_parent(eo, arm, 'LA_Head', Matrix()); follow(eo, body, 'eyes'); noshadow(eo)
    no = nums.obj('LA_GateGiant_Numbers', [num], C); bone_parent(no, arm, 'LA_Spine', Matrix()); noshadow(no)
    ld = bpy.data.lights.new('LA_GateGiant_EyeLight', 'POINT'); ld.color = lin('#FFC060'); ld.shadow_soft_size = 3.0
    lo = bpy.data.objects.new('LA_GateGiant_EyeLight', ld); C.objects.link(lo)
    bone_parent(lo, arm, 'LA_Head', Matrix.Translation((0, G.HYF * K - 6.0, LEG + G.EYE_Z * K))); follow(ld, body, 'eyes', 'energy', gain=14000.0)

    def socket(name, bone, loc, size=4.0, kind='PLAIN_AXES'):
        e = empty('LA_GateGiant_Socket_' + name, C, kind=kind, size=size)
        bone_parent(e, arm, bone, Matrix.Translation(loc))
    socket('HeadTop', 'LA_Head', (0, HEAD_PIV[1], TOP))
    socket('Eyes', 'LA_Head', (0, G.HYF * K, LEG + G.EYE_Z * K))
    for sd, s in (('L', 1), ('R', -1)):
        socket('Hand' + sd, f'LA_Hand{sd}', mx(J['tip'], s))
    import la_giant_poses
    info = la_giant_poses.build(arm, body)
    info.update(height=round(TOP, 1), stone_arms=n_arms[0], scale_of_gate=K, eye_height=round(LEG + G.EYE_Z * K, 1))
    print('GIANT arms', n_arms[0], 'height', TOP)
    return {'giant': info}
