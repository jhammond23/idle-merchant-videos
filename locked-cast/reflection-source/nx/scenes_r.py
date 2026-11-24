# My Reflection Knelt to Me: the square shots. The north half of the square is a lake; every kid's reflection is a water twin their
# own size, the hero's is a crowned water giant. Reuses the Giant Knelt staging helpers. A command sets W, H, S, OUT, WANT, OV, DRY.
_WW = set(WANT); _OVW = dict(OV); WANT = set(); OV = {}
if 'BEASTL_GK' in globals(): BEASTL = list(BEASTL_GK); KID, KIDP = KID_GK, KIDP_GK
exec(open('/tmp/claude-0/tv/gk/scenes_gk.py').read())
WANT = _WW; OV = _OVW
if 'BEASTL_GK' not in globals(): BEASTL_GK = list(BEASTL); KID_GK, KIDP_GK = KID, KIDP
BEASTL = []; KID, KIDP = KID_GK, KIDP_GK
from bpy_extras.object_utils import world_to_camera_view
KEEPR = ('twin', 'tcrown', 'kid', 'wtw', 'wcap', 'lake', 'lk_')
_DR = dict(HRN=17, HR0=15, HR1=25, HGAP=(-10, 60), SEL=42, TG=(0.0, 44.0), K0=(0.0, 5.0), TWR=(-37.0, 6.0), TGZ=-2.6,
           HOFF=30, HC=(15.0, -17.5, 6.5), HA=(0.0, 15.0, 12.6), HL=20, HLEAN=30, HBOW=20, HOUT=13,
           GROFF=30, GRX=-4.0, GRC=(7.5, -6.5, 1.9), GRL=30,
           LBOFF=25, LBC=(0.0, -24.0, 2.6), LBA=(-0.4, 9.0, 5.6), LBL=31,
           R2OFF=25, R2Y=-2.0, R2DX=4.3, R2C=(0.6, -19.0, 1.5), R2A=(-1.0, -2.0, 2.7), R2L=29,
           MNOFF=30, MNT=(6.0, 31.0), MNK=(-1.0, 0.0), MNC=(-5.0, -26.0, 2.2), MNA=(-3.0, 24.0, 27.0), MNL=18, MNTW=(-19.0, 23.0),
           S4OFF=25, S4P=(-20.0, -18.0), S4R=132.0, S4D=11.5, S4Z=4.2, S4G=4.4, S4L=30,
           SOOFF=25, SOC=(3.0, -22.0, 2.6), SOA=(0.0, 14.0, 15.0), SOL=18,
           S6OFF=20, S6C=(20.0, -33.0, 27.0), S6A=(3.0, 12.0, 10.0), S6L=22,
           FROFF=75, FRC=(1.2, 8.0, 1.7), FRA=(0.0, 0.0, 4.4), FRL=28, FRY=-16.0,
           S7OFF=115, S7C=(5.0, 12.0, 2.0), S7A=(-6.0, -2.0, 2.4), S7L=22,
           S8OFF=60, S8P=(-10.0, -3.0), S8C=(8.5, 2.2, 2.0), S8L=26,
           S9OFF=30, S9C=(13.0, -27.0, 8.0), S9A=(0.0, -3.0, 4.0), S9L=22, STLEAN=44,
           S10OFF=30, S10C=(3.4, -5.4, 6.0), S10L=22,
           S11OFF=30, S11C=(6.0, -10.0, 1.2), S11K=0.8, S11L=28,
           S12OFF=30, S12C=(-9.0, -26.0, 2.6), S12A=(3.0, 26.0, 31.0), S12L=17,
           CYOFF=-75, CYP=(9.0, -9.0), CYC=(1.5, -3.2, 3.0), CYL=95)
for _k, _v in _DR.items(): globals()[_k] = _v
for _k, _v in OV.items(): globals()[_k] = _v
def rreset():
    reset()
    for r, p in BEASTL_GK + PUPS: away(r); bpose(p, 'stand')
    for o in (WHEEL, WSTAND, WKID, KID_GK, TWIN, WCAP): away(o)
    for r, p in WTW.values(): away(r); rest(p); r.scale = (1, 1, 1); r.rotation_euler = (0, 0, 0)
    rest(KIDP); rest(WCAPP); WCAP.rotation_euler = (0, 0, 0); set_face('kid', 'face_bright'); soldiers_reset(); poster_set('refl'); mylight('wglow')
    tw_reset(); palm_show(TWINP, 'L', False); palm_show(TWINP, 'R', False); lake_on(True, tower=TWR)
    for r, p in CROWD: r.scale = (1, 1, 1); r.rotation_euler = (0, 0, 0)
def kid_at(xy, face_at, pitch=-30):
    place(KID, (xy[0], xy[1], GROUND_Z), face_at=face_at); rest(KIDP); look_head(KIDP, pitch=pitch); ANCH['kid'] = (None, head_of(KIDP) + V(0, 0, 1.3))
def ttag(up=5.0):
    bpy.context.view_layer.update(); ANCH['giant'] = (None, TWINP['head'].matrix_world @ V(0, 0, 1.6) + V(0, 0, up))
def p_kneel(r, p, s, lean=16, bow=30):
    """any person-rig on both knees, leaning in, head bowed"""
    rz = r.rotation_euler.z; r.location.z = GROUND_Z - 1.5 * s; r.rotation_euler = (math.radians(lean), 0, rz)
    leg(p, 'L', 90); leg(p, 'R', 90); look_head(p, pitch=bow); arm(p, 'L', fwd=-26, out=6); arm(p, 'R', fwd=-26, out=-6)
def twin_by(i, kneel=False, side=1, tag='1 IN 2', look=None, scale=None, gap=3.5):
    """crowd member i's reflection beside them, facing the same way (their own size unless scale is given)"""
    r, p = CROWD[i]; tr, tp = WTW[i]; s = r.scale.z if scale is None else scale; tr.scale = (s,) * 3; rest(tp)
    rz = r.rotation_euler.z; fw = V(math.sin(rz), -math.cos(rz), 0); rt = V(math.cos(rz), math.sin(rz), 0)
    q = V(r.location.x, r.location.y, 0) + rt * (gap * r.scale.z + (s - r.scale.z) * 2.0) * side - fw * 0.3
    tr.location = (q.x, q.y, GROUND_Z); tr.rotation_euler = (0, 0, rz)
    if kneel: p_kneel(tr, tp, s)
    elif look is not None: look_head(tp, pitch=look)
    bpy.context.view_layer.update()
    if tag: ANCHL.setdefault('odds', []).append((tuple(tp['head'].matrix_world.translation + V(0, 0, 1.7 * s + 0.5)), tag))
    return q
def shore_ring(n=17, r0=14, r1=24, gap=((-30, 30),), at=None, start=3, taken=None, look=None, kneel=False, tags=True, seed=3):
    """the town along the shore, each with their own reflection beside them (the lake side is always kept clear)"""
    at = at or (K0[0], K0[1] + 4); taken = list(taken or [])
    crowd_ring(n=n, r0=r0, r1=r1, seed=seed, gap=tuple(gap) + ((112, 180), (-180, -112)), face_at=at, beasts=False, start=start, taken=taken)
    for i in range(start, min(n, 17)):
        r, p = CROWD[i]
        if r.location.y > shore_y(r.location.x) - 2.5: r.location.y = shore_y(r.location.x) - 2.5 - (i % 3)
        if look is not None: look_head(p, pitch=look)
        twin_by(i, kneel=kneel, side=(1 if i % 2 else -1), tag='1 IN 2' if tags else None, look=look)
def tw_bowdown(at, face=0.0, lean=40, bow=34, out=13):
    """the giant twin on its knees in the shallows, bowed low, both open hands flat on the shore"""
    tw_kneel(at, face, lean, bow); s = TWIN.scale.z
    for sd, so in (('L', out), ('R', -out)):
        sh = TWINP['arm' + sd].matrix_world.translation; L = 1.82 * s; drop = sh.z - (GROUND_Z + 0.1 * s)
        a = math.degrees(math.acos(max(-1.0, min(1.0, drop / L))))
        arm(TWINP, sd, fwd=-(a + lean), out=so); TWINP['palm' + sd].rotation_euler = (math.radians(a), 0, 0); palm_show(TWINP, sd, True)
    bpy.context.view_layer.update()
def kid_shoulder(sd='R'):
    top = tw_shoulder(sd); fw = TWIN.matrix_world.to_3x3().normalized() @ V(0, -1, 0)
    KID.location = top + fw * 1.2 - V(0, 0, 1.75 * KID.scale.z); KID.rotation_euler = (0, 0, TWIN.rotation_euler.z); rest(KIDP)
    leg(KIDP, 'L', -82, 6); leg(KIDP, 'R', -82, -6); arm(KIDP, 'L', fwd=-100, out=-40); arm(KIDP, 'R', fwd=-30, out=0); bpy.context.view_layer.update()
def go(name):
    if DRY:
        sc = bpy.context.scene; c = sc.camera; bpy.context.view_layer.update(); sc.render.resolution_x = W; sc.render.resolution_y = H
        pts = {'thead': TWINP['head'].matrix_world.translation, 'troot': TWIN.matrix_world.translation, 'kid': head_of(KIDP)}
        for k, p in pts.items():
            a = world_to_camera_view(sc, c, p); print('DRY %s %-5s u=%.2f v=%.2f z=%.1f world=(%.1f, %.1f, %.1f)' % (name, k, a.x, a.y, a.z, p.x, p.y, p.z), flush=True)
    else: shoot(name, CPN)
# ---------------- shots ----------------
def s00_hook(name='s00_hook'):
    """frame 1, from above: the crowned water giant on its knees in the lake, head bowed to the stones, a huge open hand either side of the tiny kid"""
    light_day(off=HOFF, el=SEL); tw_bowdown(TG, 0.0, lean=HLEAN, bow=HBOW, out=HOUT); kid_at(K0, TG, pitch=-36)
    shore_ring(n=HRN, r0=HR0, r1=HR1, gap=(HGAP,), taken=[V(K0[0], K0[1], 0)], look=-20)
    lamps(False); look_cam(V(*HA), V(*HC), HL, clear=5.0, keep=KEEPR)
    ttag(); go(name)
def s01_ground():
    """your reflection climbs out of the lake: a water twin hauling itself onto the sand in front of its kid"""
    light_day(off=GROFF, el=SEL)
    x = GRX; sy = shore_y(x)
    r, p = CROWD[3]; r.scale = (0.8,) * 3; place(r, (x, sy - 4.2, GROUND_Z), face_at=(x, sy + 10)); rest(p); arm(p, 'R', fwd=-60, out=-20); arm(p, 'L', fwd=-60, out=20); look_head(p, pitch=12); set_face('cw3', 'face_grin')
    tr, tp = WTW[3]; tr.scale = (0.8,) * 3; rest(tp); tr.location = (x + 0.3, sy + 1.2, GROUND_Z - 1.3); tr.rotation_euler = (math.radians(30), 0, 0)
    arm(tp, 'L', fwd=-104, out=14); arm(tp, 'R', fwd=-104, out=-14); look_head(tp, pitch=-30)
    ANCHL.setdefault('odds', []).append((tuple(V(x + 0.3, sy - 0.4, GROUND_Z + 3.6)), '1 IN 2'))
    rnd = random.Random(8)
    for j, k in enumerate((5, 6, 7, 8, 9)):
        xx = x - 9.0 - j * 2.6 + rnd.uniform(-0.6, 0.6); yy = shore_y(xx) - rnd.uniform(4.0, 8.0); rr_, pp_ = CROWD[k]; place(rr_, (xx, yy, GROUND_Z), face_at=(x, sy)); look_head(pp_, pitch=6)
        if j % 2 == 0: twin_by(k, tag=None, look=6)
    c = V(x + GRC[0], sy - 3.4 + GRC[1], GROUND_Z + GRC[2])
    lamps(False); look_cam(V(x, sy - 1.4, GROUND_Z + 2.0), c, GRL, clear=3.0, keep=KEEPR + ('cw3',))
    go('s01_ground'); set_face('cw3', FACES[(3 * 4) % 9])
def s02_labels():
    """the number over its head is how rare it is: three kids on the shore, their reflections bigger as the number gets rarer"""
    light_day(off=LBOFF, el=SEL)
    c = V(*LBC); at = V(*LBA)
    for j, (x, s, tag) in enumerate(((-7.5, 0.8, '1 IN 2'), (-1.2, 1.25, '1 IN 60'), (6.2, 2.0, '1 IN 900'))):
        i = 4 + j; r, p = CROWD[i]; r.scale = (0.8,) * 3; place(r, (x - 1.2 - s, 7.6, GROUND_Z), face_at=(x - 1.2 - s, -10)); rest(p); look_head(p, pitch=-4); arm(p, 'R', fwd=-12, out=-8); arm(p, 'L', fwd=-12, out=8)
        tr, tp = WTW[i]; tr.scale = (s,) * 3; rest(tp); tr.location = (x, 10.0, GROUND_Z); tr.rotation_euler = (0, 0, 0); look_head(tp, pitch=6); bpy.context.view_layer.update()
        ANCHL.setdefault('odds', []).append((tuple(tp['head'].matrix_world.translation + V(0, 0, 1.7 * s + 0.5)), tag))
    lamps(False); look_cam(at, c, LBL, clear=3.0, keep=KEEPR)
    go('s02_labels')
def s02b_rabbits():
    """most kids get one their own size: a row of kids, each with a water twin exactly their size beside them"""
    light_day(off=R2OFF, el=SEL)
    c = V(*R2C); at = V(*R2A)
    for j in range(5):
        x = (j - 2) * R2DX - 1.0; y = R2Y + abs(j - 2) * 2.0
        i = j + 3; rr_, pp_ = CROWD[i]; rr_.scale = (0.8,) * 3; place(rr_, (x, y, GROUND_Z), face_at=(x, y - 10)); rest(pp_); look_head(pp_, pitch=4); arm(pp_, 'R', fwd=-12, out=-8); arm(pp_, 'L', fwd=-12, out=8)
        twin_by(i, side=-1, tag='1 IN 2', gap=3.3)
        tr, tp = WTW[i]; arm(tp, 'R', fwd=-12, out=-8); arm(tp, 'L', fwd=-12, out=8); look_head(tp, pitch=4)
    lamps(False); look_cam(at, c, R2L, clear=3.0, keep=KEEPR)
    go('s02b_rabbits')
def s03_mine():
    """mine was taller than the clock tower, and it wore a crown: the water giant standing in the lake, the kid tiny on the shore"""
    light_day(off=MNOFF, el=SEL); lake_on(True, tower=MNTW); tw_stand(MNT, -6.0, gz=TGZ, head=(22, 4), arms=9); kid_at(MNK, MNT, pitch=-42); arm(KIDP, 'R', fwd=-20, out=-20); arm(KIDP, 'L', fwd=-20, out=20)
    shore_ring(n=17, r0=13, r1=24, gap=((-50, 30),), at=(MNK[0], MNK[1] + 6), taken=[V(MNK[0], MNK[1], 0)], look=-36, tags=False)
    for r, p in CROWD[3:17]: arm(p, 'L', fwd=-120, out=20); arm(p, 'R', fwd=-120, out=-20)
    ANCHL.pop('odds', None); ttag(4.0)
    lamps(False); look_cam(V(*MNA), V(*MNC), MNL, clear=5.0, keep=KEEPR)
    go('s03_mine')
def s04_law():
    """the king's law on its board at the edge of the square; two silver guards either side"""
    light_day(off=S4OFF, el=SEL)
    P_ = bpy.data.objects['poster']; P_.location = (S4P[0], S4P[1], GROUND_Z); P_.rotation_euler = (0, 0, math.radians(S4R))
    bpy.context.view_layer.update(); f = P_.matrix_world.to_3x3() @ V(0, -1, 0); r = P_.matrix_world.to_3x3() @ V(1, 0, 0)
    at = V(S4P[0], S4P[1], GROUND_Z + 4.2); c = at + f * S4D; c.z = GROUND_Z + S4Z
    for j, sx in enumerate((-1, 1)):
        g = at + r * (sx * S4G) + f * 1.5
        rr_, pp_ = GUARDS[j]; place(rr_, (g.x, g.y, GROUND_Z), face_at=(c.x + r.x * sx * 6, c.y + r.y * sx * 6)); arm(pp_, 'R' if sx > 0 else 'L', fwd=-20, out=0); look_head(pp_, pitch=-2, yaw=-20 * sx)
    look_cam(at, c, S4L, clear=3.0)
    go('s04_law')
def s05b_soldiers():
    """the soldiers came to take mine: the captain and his guards charging, the kid arms out in front of his giant reflection"""
    light_day(off=SOOFF, el=SEL); tw_stand((TG[0], TG[1] + 4), 0.0, gz=TGZ, head=(16, 0), arms=9)
    kid_at(K0, (K0[0], K0[1] - 40)); arm(KIDP, 'L', fwd=0, out=70); arm(KIDP, 'R', fwd=0, out=-70); look_head(KIDP, pitch=0)
    soldiers((K0[0] + 0.5, K0[1] - 19.0), K0, n=5, run=True)
    shore_ring(n=17, r0=15, r1=24, gap=((-42, 42),), taken=[V(K0[0], K0[1] - 19, 0), V(K0[0], K0[1], 0)], tags=False)
    lamps(False); look_cam(V(*SOA), V(*SOC), SOL, clear=4.0, keep=KEEPR + ('capt', 'gd'))
    ANCHL.pop('odds', None); ttag(); go('s05b_soldiers'); soldiers_reset()
def s06_kneel():
    """in front of the whole town: high and wide, the shore full of people, the water giant bowed down to the tiny kid"""
    light_day(off=S6OFF, el=SEL); tw_bowdown(TG, 0.0, lean=HLEAN, bow=HBOW, out=HOUT); kid_at(K0, TG, pitch=-36)
    shore_ring(n=17, r0=14, r1=26, gap=((-24, 24),), taken=[V(K0[0], K0[1], 0)], look=-16, tags=False)
    lamps(False); look_cam(V(*S6A), V(*S6C), S6L, clear=6.0, keep=KEEPR)
    ANCHL.pop('odds', None); go('s06_kneel')
def s06b_froze():
    """the soldiers froze: the captain and guards staring up, the water giant's shadow over them"""
    light_day(off=FROFF, el=SEL); tw_bowdown(TG, 0.0, lean=HLEAN, bow=HBOW, out=HOUT); kid_at(K0, TG, pitch=-36)
    soldiers((K0[0], FRY), (K0[0], K0[1] + 6), n=5, run=False, shocked=True, spread=2.3)
    c = V(K0[0] + FRC[0], FRY + FRC[1], GROUND_Z + FRC[2]); at = V(K0[0], FRY, GROUND_Z + FRA[2])
    lamps(False); look_cam(at, c, FRL, clear=2.0, keep=('capt', 'gd'))
    ANCHL.pop('odds', None); go('s06b_froze'); soldiers_reset()
def s07_lay():
    """then every reflection on the shore knelt too"""
    light_day(off=S7OFF, el=SEL); tw_bowdown(TG, 0.0, lean=HLEAN, bow=HBOW, out=HOUT)
    c = V(*S7C); at = V(*S7A)
    spots = [(-2.0, 3.0), (-7.5, 1.0), (-12.0, 5.0), (-5.0, -4.5), (-14.5, -1.5), (-10.0, -7.5), (2.5, -3.5), (-18.0, 6.0), (-1.0, -10.0), (-16.5, -8.5), (5.5, -9.5), (-21.5, 0.5), (-7.0, -13.0), (9.0, -4.0)]
    for j, (x, y) in enumerate(spots):
        i = 3 + j; r, p = CROWD[i]; place(r, (x, y, GROUND_Z), face_at=TG); rest(p); look_head(p, pitch=10, yaw=(-40 if j % 2 else 40))
        twin_by(i, kneel=True, side=(1 if j % 2 else -1), tag='1 IN 2')
    lamps(False); look_cam(at, c, S7L, clear=2.5, keep=KEEPR)
    go('s07_lay')
def s08_lion():
    """even the captain's: his own reflection on its knees beside him, the captain staring at it"""
    light_day(off=S8OFF, el=SEL); tw_bowdown(TG, 0.0, lean=HLEAN, bow=HBOW, out=HOUT)
    cx, cy = S8P; place(CAPT, (cx, cy, GROUND_Z), face_at=TG); rest(CAPTP); look_head(CAPTP, pitch=14, yaw=-52); arm(CAPTP, 'R', fwd=-14, out=-6); set_face('capt', 'face_bold_shocked')
    lx, ly = cx + 2.9, cy - 0.4
    place(WCAP, (lx, ly, GROUND_Z), face_at=TG); rest(WCAPP); p_kneel(WCAP, WCAPP, 1.0, lean=20, bow=34)
    ANCHL.setdefault('odds', []).append((tuple(V(lx, ly - 0.6, GROUND_Z + 5.4)), '1 IN 80,000'))
    if not bpy.data.objects.get('capsw'): hand_sword(CAPTP, 'R', 'capsw', s=0.8, up=False)
    for j, (dx, dy) in enumerate(((-3.5, -4.5), (1.0, -5.5))):
        rr_, pp_ = GUARDS[j]; place(rr_, (cx + dx, cy + dy, GROUND_Z), face_at=TG); look_head(pp_, pitch=-26); set_face('gd%d' % j, 'face_bright_shocked')
    lp = V(lx - 1.2, ly, 0); fl = V(TG[0], TG[1], 0) - lp; fl.normalize(); rl = V(fl.y, -fl.x, 0)
    c = lp + fl * S8C[0] + rl * S8C[1]; c.z = GROUND_Z + S8C[2]
    look_cam(V(lp.x + fl.x * 0.5, lp.y + fl.y * 0.5, GROUND_Z + 3.0), c, S8L, clear=3.0, keep=KEEPR)
    go('s08_lion'); soldiers_reset()
def step_pose():
    pc = tw_step(TG, 0.0, lean=STLEAN, bow=10, sd='L'); return pc
def s09_hand():
    """then mine put its hand on the ground, like a step: the open water hand flat on the stones in front of the kid"""
    light_day(off=S9OFF, el=SEL); pc = step_pose()
    kid_at((pc.x - 0.6, pc.y - 10.6), (pc.x, pc.y + 6), pitch=6)
    shore_ring(n=17, r0=18, r1=27, gap=((-50, 50),), at=(pc.x, pc.y - 4), taken=[V(pc.x, pc.y - 10, 0)], tags=False)
    lamps(False); look_cam(pc + V(*S9A), pc + V(*S9C), S9L, clear=3.0, keep=KEEPR)
    ANCHL.pop('odds', None); go('s09_hand')
def s10_dont():
    """you'd climb on, right? the kid's foot coming down on the giant water palm"""
    light_day(off=S10OFF, el=SEL); pc = step_pose()
    kp = V(pc.x - 0.2, pc.y - 9.2, GROUND_Z); place(KID, tuple(kp), face_at=(pc.x, pc.y + 6)); rest(KIDP); leg(KIDP, 'R', -46); leg(KIDP, 'L', 10)
    arm(KIDP, 'R', fwd=-30, out=-30); arm(KIDP, 'L', fwd=-20, out=30); look_head(KIDP, pitch=14)
    c = kp + V(*S10C); at = V(pc.x, pc.y - 4.0, GROUND_Z + 1.4)
    lamps(False); look_cam(at, c, S10L, clear=1.5, keep=KEEPR)
    ANCHL.pop('odds', None); go('s10_dont')
def s11_did():
    """so did I: the kid sitting on the water giant's shoulder beside its crowned head, grinning, the town far below"""
    light_day(off=S11OFF, el=SEL); tw_stand((TG[0], TG[1] - 6), 0.0, gz=TGZ, head=(4, -30), arms=9); kid_shoulder('R')
    arm(KIDP, 'R', fwd=-165, out=-20); arm(KIDP, 'L', fwd=-40, out=-30); look_head(KIDP, pitch=-8, yaw=20); set_face('kid', 'face_grin')
    shore_ring(n=17, r0=18, r1=28, gap=((-20, 20),), at=(TG[0], TG[1] - 12), look=-40, tags=False)
    hp = head_of(KIDP); c = hp + V(*S11C)
    th = TWINP['head'].matrix_world.translation
    lamps(False); look_cam(hp * S11K + th * (1 - S11K), c, S11L, clear=3.0, keep=KEEPR)
    ANCHL.pop('odds', None); go('s11_did')
def s12_stand():
    """it stood up: the water giant at its full height against the sky, the kid on its shoulder, the town tiny at its feet"""
    light_day(off=S12OFF, el=SEL); tw_stand((TG[0] + 2, TG[1] - 8), -8.0, gz=TGZ, head=(-4, 0), stride=10, arms=10); kid_shoulder('R'); look_head(KIDP, pitch=-6)
    shore_ring(n=17, r0=16, r1=28, gap=((-40, 40),), at=(TG[0] + 2, TG[1] - 16), look=-40, tags=False)
    lamps(False); look_cam(V(*S12A), V(*S12C), S12L, clear=5.0, keep=KEEPR)
    ANCHL.pop('odds', None); ttag(); go('s12_stand')
def s14b_captain():
    """the captain yelled: tiny far below, fist up, his own reflection still on its knees beside him (seen from up on the shoulder)"""
    light_day(off=CYOFF, el=SEL); tw_stand((TG[0], TG[1] - 6), 0.0, gz=TGZ, head=(20, -10), arms=9); kid_shoulder('R')
    cx, cy = CYP
    place(CAPT, (cx, cy, GROUND_Z), face_at=(TG[0] + 12, TG[1])); rest(CAPTP); look_head(CAPTP, pitch=-46); arm(CAPTP, 'R', fwd=-165, out=-10); arm(CAPTP, 'L', fwd=-20, out=30)
    set_face('capt', 'face_bold_angry_talk_open')
    place(WCAP, (cx - 3.0, cy - 0.4, GROUND_Z), face_at=(TG[0] + 12, TG[1])); rest(WCAPP); p_kneel(WCAP, WCAPP, 1.0, lean=20, bow=34)
    ANCHL.setdefault('odds', []).append((tuple(V(cx - 3.0, cy - 0.6, GROUND_Z + 5.4)), '1 IN 80,000'))
    for j, (dx, dy) in enumerate(((2.6, -2.2), (-1.0, -3.6), (4.6, -4.4))):
        rr_, pp_ = GUARDS[j]; place(rr_, (cx + dx, cy + dy, GROUND_Z), face_at=(TG[0] + 12, TG[1])); look_head(pp_, pitch=-40); set_face('gd%d' % j, 'face_bright_shocked')
    hp = head_of(KIDP); c = hp + V(*CYC)
    lamps(False); look_cam(V(cx, cy, GROUND_Z + 3.6), c, CYL, clear=2.0, keep=('capt', 'gd', 'wcap'))
    go('s14b_captain'); soldiers_reset()
SHOTS_R = [('s00_hook', s00_hook), ('s01_ground', s01_ground), ('s02_labels', s02_labels), ('s02b_rabbits', s02b_rabbits), ('s03_mine', s03_mine), ('s04_law', s04_law),
           ('s05b_soldiers', s05b_soldiers), ('s06_kneel', s06_kneel), ('s06b_froze', s06b_froze), ('s07_lay', s07_lay), ('s08_lion', s08_lion), ('s09_hand', s09_hand),
           ('s10_dont', s10_dont), ('s11_did', s11_did), ('s12_stand', s12_stand), ('s14b_captain', s14b_captain)]
for _n, _f in SHOTS_R:
    if wanted(_n): rreset(); _f()
rreset(); lake_on(False)
