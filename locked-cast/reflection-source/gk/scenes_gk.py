# A Giant Knelt to Me: every shot as a function. A command sets W, H, S, OUT, WANT (name prefixes) and OV (tunable overrides),
# then execs this file. Each shot stages what it needs; reset() parks everything first, so shots can run in any order.
def wanted(n): return any(n.startswith(w) or w.startswith(n) for w in WANT)
def V(*a): return Vector(a)
def head_of(p):
    bpy.context.view_layer.update(); return p['head'].matrix_world.translation.copy()
def hand_of(p, side='R'):
    bpy.context.view_layer.update(); o = [c for c in p['arm' + side].children if c.name.endswith('Hd' + side)][0]
    return o.matrix_world.translation.copy()
_D = dict(GX=0.0, GY=6.0, KIDY=-11.0, C0=(7.0, -40.0, 3.6), A0=(1.0, -3.0, 14.5), L0=19, X0=0.0, SEL=40, SOFF=30,
          RING0=15.0, RING1=24.0, BOW=38, LEAN=14, CROWDN=24, SWX=8.6, SWY=-5.5, SWZ=14.2, SWR=30.0, KH=(-2.4, -11.6, 10.6), HANDX=2.7, CAM_ANG=30.0, CAM_D=46.0, CAM_H=12.5, KIDD=13.0, FS=5, FN=8, FD0=9.0, FD1=17.0, FA0=13.0, FA1=34.0, GTU=1.0, GTS=11.0, PDL=55, PDB=10, PDH=7.4, SEATF=2.2, PT=(-5.0, -19.0),
          S1OFF=30, S1H=(-18.0, -6.0), S1C=(4.0, -12.0, 6.2), S1L=30, S1E=900.0,
          S2OFF=20, S2C=(-4.0, -31.0, 11.0), S2A=(2.0, -12.0, 1.0), S2R=(-2.5, -20.0, 4.0, 6.0), S2L=26,
          S3OFF=25, S3E=1.5e4, S3K=(-5.0, -19.0), S3C=(-5.0, -33.0, 9.8), S3L=26,
          S4OFF=25, S4P=(-20.0, -18.0), S4R=132.0, S4D=11.5, S4Z=4.2, S4G=4.4, S4L=30,
          S6OFF=20, S6C=(16.0, -44.0, 24.0), S6A=(0.0, 0.0, 11.0), S6L=22,
          S7OFF=30, S7C=(-14.0, -26.0, 1.6), S7A=(0.0, 2.0, 10.0), S7L=20,
          S8OFF=100, S8P=(-8.0, -15.0), S8C=(8.5, 2.2, 2.0), S8L=26,
          S9OFF=30, S9K=(-1.5, -20.0), S9C=(0.0, -28.0, 6.0), S9A=(-3.5, -11.0, 6.5), S9L=22,
          S10OFF=30, S10S=5.8, S10G=(-2.8, -2.9), S10B=3.2, S10SS=1.4, S10H=8.0, S10K=0.35, S10AZ=0.6, S10L=26,
          S11OFF=30, S11Z=13.0, S11C=(-15.0, -16.0, 11.0), S11A=(-4.0, -5.0, 17.0), S11L=26,
          S12OFF=30, S12F=0.0, S12C=(12.0, -22.0, 8.0), S12Z=24.0, S12L=18,
          S16OFF=30, S16C=(4.2, 3.2, 0.6), S16L=30,
          R2OFF=25, R2Y=-18.0, R2DX=2.2, R2C=(0.6, -31, 1.3), R2A=(0, -18, 2.3), R2L=30,
          SOOFF=25, SOK=(0.0, -9.0), SOC=(3.0, -37.0, 2.6), SOA=(0.0, -2.0, 12.5), SOL=20,
          FROFF=75, FRC=(1.2, -13.5, 1.7), FRA=(0.0, -23.0, 4.4), FRL=28,
          CYOFF=-75, CYP=(-5.0, -13.0), CYC=(1.5, -5.0, 9.5), CYL=40)
for _k, _v in _D.items(): globals()[_k] = _v
for _k, _v in OV.items(): globals()[_k] = _v
DRY = globals().get('DRY', False)
def lamps(on):
    for o in bpy.data.objects:
        if o.name.startswith('a1_town_lamp'): o.hide_render = not on
def reset():
    anchors_clear(); lamps(True)
    for r, p in CROWD + GUARDS: away(r); rest(p)
    for r, p in BEASTL: away(r); bpose(p, 'stand')
    for o in (KID, CAPT, LION, GIANT, SWORD): away(o)
    for nm in ('holeS', 'holeL', 'poster'):
        o = bpy.data.objects.get(nm)
        if o: away(o)
    mylight('holeL1'); mylight('holeL2')
    rest(KIDP); rest(CAPTP); bpose(LIONP, 'stand'); kreset(GP)
    set_face('kid', 'face_bright')
    for o in bpy.data.objects:          # the flower boxes clutter every low camera on the square
        if o.name.startswith(('a1_raised_flower_box', 'a1_flower_planter')): o.hide_render = True
    EXPO[0] = 0.0
def gl(x, y, z=0.0):
    """giant-local point -> world (the giant's root frame, whatever it faces)"""
    bpy.context.view_layer.update(); return GIANT.matrix_world @ V(x, y, z)
def kneel(at=(0, 0), face=0.0, lean=None, bow=None, vigil=True, hip=10.8):
    """the giant on its left knee, right knee up, head bowed over a greatsword planted point-down in front of it, both fists on the crossguard"""
    kreset(GP); GIANT.location = (at[0], at[1], GROUND_Z); GIANT.rotation_euler = (0, 0, math.radians(face))
    GP['hip'].location = (0, 0, hip); bpy.context.view_layer.update()
    GP['tor'].rotation_euler = (math.radians(LEAN if lean is None else lean), 0, 0)
    GP['head'].rotation_euler = (math.radians(BOW if bow is None else bow), 0, 0); bpy.context.view_layer.update()
    kleg(GP, 'L', gl(-3.9, -8.6, 1.25), gl(-3.6, -24, 22))                       # knee up, foot planted forward
    hp = wpos(GP['legR']); K = gl(3.4, -2.2, 0); K.z = GROUND_Z + 2.3
    K = hp + (K - hp).normalized() * KL['thigh']
    fwd = GIANT.matrix_world.to_3x3() @ V(0, -1, 0); back = -fwd
    aim_pivot(GP['legR'], K - hp, fwd)
    F = K + back * KL['shin']; F.z = GROUND_Z + 2.1
    aim_pivot(GP['kneeR'], F - wpos(GP['kneeR']), V(0, 0, -1))
    aim_pivot(GP['footR'], back * 0.35 + V(0, 0, -1), V(0, 0, -1) * 0.2 + back)
    if vigil:       # the knighting pose: its left hand on the pommel of the sword planted at its side, its right forearm across the raised knee
        SWORD.location = gl(SWX, SWY, 0); SWORD.location.z = GROUND_Z + SWZ; SWORD.rotation_euler = (0, 0, math.radians(face + SWR))
        bpy.context.view_layer.update(); top = SWORD.matrix_world @ V(0, 0, 6.3)
        karm(GP, 'R', top + V(0, 0, 1.9), gl(16, 4, 12), hand_dir=V(0, 0, -1), palm_dir=back)
        karm(GP, 'L', gl(*KH), gl(-15, -3, 12), hand_dir=(GIANT.matrix_world.to_3x3() @ V(0.35, -0.25, -1)), palm_dir=fwd)
    bpy.context.view_layer.update()
def crowd_ring(n=None, r0=None, r1=None, seed=3, gap=((-30, 30),), face_at=(0, 0), beasts=True, lie=False, start=0, taken=None):
    """people around the giant with their guardians beside them; gap = angle ranges (deg, 0 = -y/south) kept empty"""
    rnd = random.Random(seed); n = n or CROWDN; r0 = r0 or RING0; r1 = r1 or RING1; placed = 0; ang = 0
    tags = [(q.x, q.y) for q in (taken or [])]
    for i in range(start, min(n, len(CROWD))):
        for _try in range(40):
            a = rnd.uniform(-180, 180)
            if any(g0 <= a <= g1 for g0, g1 in gap): continue
            rr = rnd.uniform(r0, r1)
            x = face_at[0] + math.sin(math.radians(a)) * rr; y = face_at[1] - math.cos(math.radians(a)) * rr
            ok = all((x - q[0]) ** 2 + (y - q[1]) ** 2 > 3.4 ** 2 for q in tags)
            if ok: break
        r, p = CROWD[i]; place(r, (x, y, GROUND_Z), face_at=(face_at[0], face_at[1]))
        pose_lookup(p, rnd)
        tags.append((x, y))
        if beasts and i < len(BEASTL):
            br, bp = BEASTL[i]; th = math.atan2(face_at[0] - x, -(face_at[1] - y))
            side = 1 if rnd.random() < 0.5 else -1
            bx = x + math.cos(th) * 2.1 * side - math.sin(th) * 0.8; by = y + math.sin(th) * 2.1 * side + math.cos(th) * 0.8
            place(br, (bx, by, GROUND_Z), face_at=(face_at[0], face_at[1]))
            bpose(bp, 'lie' if lie else 'stand', head_pitch=-14 if not lie else 0)
            bpy.context.view_layer.update()
            top = bp['head'].matrix_world @ V(0, 0, 0)
            hgt = (bp['lh'] + bp['bh']) * br.scale.z
            ANCHL.setdefault('odds', []).append((tuple(V(bx, by, GROUND_Z + hgt + 2.0 + (0.6 if lie else 0.0))), ODDS[bp['kind']]))
def crowd_front(cam, at, idx, n, dmin, dmax, ang0, ang1, seed=5, face_at=None, lie=False, beast_side=None, taken=None):
    """a band of people in front of the camera between dmin and dmax, at |angle| ang0..ang1 off the view axis (deg),
    so the subject stays clear. Each brings its guardian. idx = first CROWD index to use. Returns the next free index."""
    rnd = random.Random(seed); cam = V(*cam); at = V(*at); f = (at - cam); f.z = 0; f.normalize(); r = V(f.y, -f.x, 0)
    taken = taken if taken is not None else []
    k = idx
    for i in range(n):
        if k >= len(CROWD): break
        for _try in range(60):
            d = rnd.uniform(dmin, dmax); a = math.radians(rnd.uniform(ang0, ang1)) * (1 if rnd.random() < 0.5 else -1)
            p = cam + f * d * math.cos(a) + r * d * math.sin(a)
            if all((p - q).length > 2.6 for q in taken): break
        taken.append(p.copy()); rr_, pp_ = CROWD[k]
        place(rr_, (p.x, p.y, GROUND_Z), face_at=face_at or (at.x, at.y)); pose_lookup(pp_, rnd)
        if k < len(BEASTL):
            br, bp = BEASTL[k]; side = beast_side or (1 if rnd.random() < 0.5 else -1)
            bq = p + r * 1.9 * side + f * 0.6
            if all((bq - q).length > 1.6 for q in taken):
                place(br, (bq.x, bq.y, GROUND_Z), face_at=face_at or (at.x, at.y)); bpose(bp, 'lie' if lie else 'stand', head_pitch=-14 if not lie else 0)
                taken.append(bq.copy()); bpy.context.view_layer.update()
                hgt = (bp['lh'] + bp['bh']) * br.scale.z
                ANCHL.setdefault('odds', []).append((tuple(V(bq.x, bq.y, GROUND_Z + hgt + 1.6)), ODDS[bp['kind']]))
        k += 1
    return k
def pose_lookup(p, rnd):
    """crowd reaction: looking up at the giant, some arms up/out"""
    look_head(p, pitch=-18 - rnd.uniform(0, 14), yaw=rnd.uniform(-12, 12))
    k = rnd.random()
    if k < 0.25: arm(p, 'L', fwd=-150, out=10); arm(p, 'R', fwd=-150, out=-10)
    elif k < 0.5: arm(p, 'R', fwd=-60, out=-30)
    elif k < 0.65: arm(p, 'L', fwd=-80, out=20); arm(p, 'R', fwd=-80, out=-20)
def giant_tag(up=7.0, side=0.0):
    """the giant's number: above its plume, or beside its helm (side = units to the camera's right, set after the camera)"""
    bpy.context.view_layer.update(); h = GP['head'].matrix_world @ V(0, 0, 9.0)
    if side:
        c = bpy.context.scene.camera; r = c.matrix_world.to_3x3() @ V(1, 0, 0)
        h = GP['head'].matrix_world @ V(0, -2.0, 4.0) + r * side
    ANCH['giant'] = (None, h + V(0, 0, up))
def kid_at(xy, face_at, pose='stand'):
    place(KID, (xy[0], xy[1], GROUND_Z), face_at=face_at); rest(KIDP)
    if pose == 'reach': arm(KIDP, 'R', fwd=-40, out=-10); look_head(KIDP, pitch=-25)
    else: look_head(KIDP, pitch=-30)
    ANCH['kid'] = (None, head_of(KIDP) + V(0, 0, 1.3))
def dry_report(name):
    sc = bpy.context.scene; c = sc.camera; bpy.context.view_layer.update()
    sc.render.resolution_x = W; sc.render.resolution_y = H
    pts = {'helm': GP['head'].matrix_world @ V(0, -3.8, 4.0), 'gtag': ANCH['giant'][1] if 'giant' in ANCH else None,
           'kid': head_of(KIDP), 'pommel': SWORD.matrix_world @ V(0, 0, 5.3), 'gfoot': wpos(GIANT), 'kneeR': wpos(GP['kneeR']),
           'footL': wpos(GP['footL']), 'fistL': GP['fistL'].matrix_world @ V(0, 0, -1.9), 'handR': wpos(GP['handR'])}
    for k, p in pts.items():
        if p is None: continue
        a = world_to_camera_view(sc, c, p)
        print('DRY %s %-7s u=%.2f v=%.2f z=%.1f  world=(%.1f, %.1f, %.1f)' % (name, k, a.x, a.y, a.z, p.x, p.y, p.z), flush=True)
    ol = ANCHL.get('odds', [])
    vis = [(round(world_to_camera_view(sc, c, V(*q)).x, 2), round(world_to_camera_view(sc, c, V(*q)).y, 2), t) for q, t in ol]
    print('DRY %s odds in frame: %s' % (name, [v for v in vis if 0 < v[0] < 1 and 0 < v[1] < 1]), flush=True)
def go(name):
    if DRY: dry_report(name)
    else: shoot(name, CPN)
# ---------------- shots ----------------
def cam_around(ang, dist, h, at, lens):
    """camera on a circle around the giant: ang degrees from its facing direction (positive = its left = screen right)"""
    th = GIANT.rotation_euler.z + math.radians(ang)
    c = V(GIANT.location.x + math.sin(th) * dist, GIANT.location.y - math.cos(th) * dist, GROUND_Z + h)
    return c
def s00_hook(name='s00_hook'):
    light_day(off=SOFF, el=SEL)
    kneel((GX, GY), 0.0)
    kid_at(tuple(gl(X0, -KIDD)[:2]), (GX, GY))
    c = cam_around(CAM_ANG, CAM_D, CAM_H, None, L0); at = V(*A0)
    taken = [V(*gl(X0, -KIDD)[:2], 0)]
    k = crowd_front(c, at, 0, FN, FD0, FD1, FA0, FA1, seed=FS, taken=taken)
    crowd_ring(n=None, gap=((CAM_ANG - 50, CAM_ANG + 50),), face_at=(GX, GY), start=k, taken=taken)
    lamps(False)
    look_cam(at, c, L0, clear=8.0, keep=('gk', 'gsw', 'kid'), extra=('a1_market_stall', 'a1_food_crates'))
    giant_tag(up=GTU, side=GTS)
    go(name)
# ---------------- poses ----------------
def beast_of(kind, skip=()):
    for j, (br, bp) in enumerate(BEASTL):
        if bp['kind'] == kind and j not in skip: return j
    return None
def palm_center(side):
    bpy.context.view_layer.update(); return GP['palm' + side].matrix_world @ V(0, 0, -2.0)
def palm_down(target_xy, side='L', lean=None, bow=None):
    """from the kneel: one open hand flat on the cobbles, palm up, fingers toward target_xy (a step for the kid)"""
    kneel((GX, GY), 0.0, lean=PDL if lean is None else lean, bow=PDB if bow is None else bow, vigil=True, hip=PDH)
    hand_mode(GP, side, True)
    t = V(target_xy[0], target_xy[1], 0); sh = wpos(GP['arm' + side]); d = t - V(sh.x, sh.y, 0); d.z = 0; d.normalize()
    pc = t - d * 2.6; pc.z = GROUND_Z + 0.9            # palm centre
    wrist = pc - d * 2.0
    karm(GP, side, wrist, sh + V(-9 if side == 'L' else 9, 4, -2), hand_dir=d, palm_dir=V(0, 0, 1))
    real = palm_center(side)
    if DRY: print('DRY palm want=(%.1f, %.1f, %.1f) got=(%.1f, %.1f, %.1f) shoulder=(%.1f, %.1f, %.1f) reach=%.1f/15.6' % (tuple(pc) + tuple(real) + tuple(sh) + ((wrist - sh).length,)), flush=True)
    return real
def stand(at=(0, 0), face=0.0, arms_out=8, head=(0, 0)):
    kreset(GP); GIANT.location = (at[0], at[1], GROUND_Z); GIANT.rotation_euler = (0, 0, math.radians(face))
    bpy.context.view_layer.update()
    for sd, sx in (('L', -1), ('R', 1)):
        GP['arm' + sd].rotation_euler = (math.radians(-6), math.radians(sx * -arms_out), 0)
        GP['elb' + sd].rotation_euler = (math.radians(-14), 0, 0)
    GP['head'].rotation_euler = (math.radians(head[0]), 0, math.radians(head[1])); bpy.context.view_layer.update()
def on_shoulder(side='R', lean=0):
    """the kid sits on the giant's pauldron (R = the giant's left, +x), legs over the front, one hand on the helm"""
    bpy.context.view_layer.update(); sp = GP['arm' + side]
    top = sp.matrix_world @ V(0.6 if side == 'R' else -0.6, 0, 3.9)
    fw = GIANT.matrix_world.to_3x3() @ V(0, -1, 0)
    KID.location = top + fw * SEATF - V(0, 0, 1.75 * KID.scale.z); KID.rotation_euler = (math.radians(lean), 0, GIANT.rotation_euler.z)
    leg(KIDP, 'L', -82, 6); leg(KIDP, 'R', -82, -6)
    arm(KIDP, 'L' if side == 'R' else 'R', fwd=-100, out=(-40 if side == 'R' else 40)); arm(KIDP, 'R' if side == 'R' else 'L', fwd=-30, out=0)
    bpy.context.view_layer.update(); ANCH['kid'] = (None, head_of(KIDP) + V(0, 0, 1.3))
def hole_at(nm, xy, glow=1.0, e=2.0e4, lz=1.2):
    o = bpy.data.objects[nm]; o.location = (xy[0], xy[1], 0.0)
    mylight(nm + '1', (xy[0], xy[1], lz), (1.0, 0.66, 0.26), e * glow, 1.5)
def kid_face(face): set_face('kid', face)
def beasts_front(cam, at, idxs, dmin, dmax, ang0, ang1, seed=7):
    """guardians lying flat in the near foreground (no people), each with its number"""
    rnd = random.Random(seed); cam = V(*cam); at = V(*at); f = at - cam; f.z = 0; f.normalize(); r = V(f.y, -f.x, 0); taken = []
    for j, b in enumerate(idxs):
        for _try in range(60):
            d = rnd.uniform(dmin, dmax); a = math.radians(rnd.uniform(ang0, ang1)) * (1 if j % 2 else -1)
            p = cam + f * d * math.cos(a) + r * d * math.sin(a)
            if all((p - q).length > 2.4 for q in taken): break
        taken.append(p.copy()); br, bp = BEASTL[b]
        place(br, (p.x, p.y, GROUND_Z), face_at=(GX, GY)); bpose(bp, 'lie'); bpy.context.view_layer.update()
        hgt = (bp['lh'] + bp['bh']) * br.scale.z
        ANCHL.setdefault('odds', []).append((tuple(V(p.x, p.y, GROUND_Z + hgt + 1.0)), ODDS[bp['kind']]))
# ---------------- square shots ----------------
def s01_ground():
    """a kid's fox climbing out of the glowing cobbles, the crowd around"""
    light_day(off=S1OFF, el=SEL)
    hx, hy = S1H; hole_at('holeS', (hx, hy), e=S1E, lz=-0.6)
    r, p = CROWD[3]; r.scale = (0.8,) * 3; place(r, (hx - 2.6, hy + 1.2, GROUND_Z), face_at=(hx, hy)); look_head(p, pitch=24); arm(p, 'R', fwd=-60, out=-16); arm(p, 'L', fwd=-60, out=16)
    br, bp = BEASTL[beast_of('fox')]; place(br, (hx + 0.2, hy - 0.2, GROUND_Z - 0.5), face_at=(hx + 2, hy - 4)); bpose(bp, 'stand', head_pitch=-20)
    br.rotation_euler.x = math.radians(-32); bpy.context.view_layer.update()
    ANCHL.setdefault('odds', []).append((tuple(V(hx, hy - 0.4, GROUND_Z + 3.4)), '1 IN 60'))
    rnd = random.Random(8)
    for j, k in enumerate((5, 6, 7, 8, 9, 10, 11, 12)):
        a = math.radians(-84 + j * 24); d = rnd.uniform(5.0, 8.5)
        rr_, pp_ = CROWD[k]; place(rr_, (hx + math.sin(a) * d, hy + math.cos(a) * d, GROUND_Z), face_at=(hx, hy)); look_head(pp_, pitch=20)
    c = V(hx + S1C[0], hy + S1C[1], GROUND_Z + S1C[2])
    look_cam(V(hx, hy + 1.0, GROUND_Z + 1.0), c, S1L, clear=4.0)
    go('s01_ground')
    CROWD[3][0].scale = (1, 1, 1)
def s02_labels():
    """three kids on a diagonal line, each with its guardian and its number, seen from a little above"""
    light_day(off=S2OFF, el=SEL)
    c = V(*S2C); at = V(*S2A)
    row = [(13, beast_of('rabbit')), (14, beast_of('goat')), (15, beast_of('wolf'))]
    for j, (k, b) in enumerate(row):
        x = S2R[0] + j * S2R[2]; y = S2R[1] + j * S2R[3]
        rr_, pp_ = CROWD[k]; rr_.scale = (0.8,) * 3; place(rr_, (x, y, GROUND_Z), face_at=(c.x, c.y))
        look_head(pp_, pitch=-4); arm(pp_, 'R', fwd=-10, out=-8)
        br, bp = BEASTL[b]; place(br, (x + 1.5, y - 0.6, GROUND_Z), face_at=(c.x, c.y)); bpose(bp, 'stand' if bp['kind'] != 'rabbit' else 'sit')
        bpy.context.view_layer.update(); hgt = (bp['lh'] + bp['bh'])
        ANCHL.setdefault('odds', []).append((tuple(V(x + 1.5, y - 0.6, GROUND_Z + hgt + 1.4)), ODDS[bp['kind']]))
    crowd_ring(n=10, r0=9, r1=16, seed=12, gap=((-70, 70),), face_at=(S2A[0], S2A[1] + 4), beasts=False)
    look_cam(at, c, S2L, clear=6.0)
    go('s02_labels')
    for k in (13, 14, 15): CROWD[k][0].scale = (1, 1, 1)
def s03_mine():
    """the square splits; a giant gauntlet grips the edge; 1 IN 10,000,000 (overlay)"""
    light_day(off=S3OFF, el=SEL)
    hole_at('holeL', (GX, GY), e=S3E, lz=-1.0)
    kreset(GP); GIANT.location = (GX, GY + 4, GROUND_Z - 34); GIANT.rotation_euler = (0, 0, 0); bpy.context.view_layer.update()
    hand_mode(GP, 'L', True); hand_mode(GP, 'R', True)
    for sd, sx in (('L', -1), ('R', 1)):
        rim = V(GX + sx * 4.5, GY - 6.6, GROUND_Z + 0.9)
        karm(GP, sd, rim + V(0, 1.6, 2.6), V(GX + sx * 14, GY + 8, GROUND_Z - 6), hand_dir=V(sx * 0.15, -0.55, -0.82), palm_dir=V(0, 0.4, -1))
    kid_at((GX + S3K[0], GY + S3K[1]), (GX, GY)); arm(KIDP, 'R', fwd=-20, out=-20); arm(KIDP, 'L', fwd=-20, out=20)
    c = cam_xy = V(GX + S3C[0], GY + S3C[1], GROUND_Z + S3C[2])
    taken = [V(GX + S3K[0], GY + S3K[1], 0)]
    crowd_ring(n=18, r0=14, r1=21, gap=((-40, 40),), face_at=(GX, GY), taken=taken)
    for r, p in CROWD[:18]: arm(p, 'L', fwd=-120, out=20); arm(p, 'R', fwd=-120, out=-20); r.rotation_euler.x = math.radians(-8)
    ANCH['giant'] = (None, V(GX, GY - 2, GROUND_Z + 13.0))
    lamps(False); look_cam(V(GX, GY - 3, GROUND_Z + 3.0), c, S3L, clear=6.0)
    ANCHL.pop('odds', None)
    go('s03_mine')
def s04_law():
    """the royal law on its board at the edge of the square; two silver guards either side, turning toward the kid"""
    light_day(off=S4OFF, el=SEL)
    P_ = bpy.data.objects['poster']; P_.location = (S4P[0], S4P[1], GROUND_Z); P_.rotation_euler = (0, 0, math.radians(S4R))
    bpy.context.view_layer.update(); f = P_.matrix_world.to_3x3() @ V(0, -1, 0); r = P_.matrix_world.to_3x3() @ V(1, 0, 0)
    at = V(S4P[0], S4P[1], GROUND_Z + 4.2); c = at + f * S4D; c.z = GROUND_Z + S4Z
    for j, sx in enumerate((-1, 1)):
        g = at + r * (sx * S4G) + f * 1.5
        rr_, pp_ = GUARDS[j]; place(rr_, (g.x, g.y, GROUND_Z), face_at=(c.x + r.x * sx * 6, c.y + r.y * sx * 6))
        arm(pp_, 'R' if sx > 0 else 'L', fwd=-20, out=0); look_head(pp_, pitch=-2, yaw=-20 * sx)
    look_cam(at, c, S4L, clear=3.0)
    go('s04_law')
def s06_kneel():
    """in front of the whole town: high wide over the square, the ring of people, the giant kneeling to the tiny kid"""
    light_day(off=S6OFF, el=SEL)
    kneel((GX, GY), 0.0); kid_at(tuple(gl(X0, -KIDD)[:2]), (GX, GY))
    taken = [V(*gl(X0, -KIDD)[:2], 0)]
    crowd_ring(n=24, r0=14, r1=24, gap=((-25, 25),), face_at=(GX, GY), taken=taken)
    lamps(False); look_cam(V(*S6A), V(*S6C), S6L, clear=6.0)
    ANCHL.pop('odds', None)
    go('s06_kneel')
def s07_lay():
    """every guardian in the square lay down"""
    light_day(off=S7OFF, el=SEL)
    kneel((GX, GY), 0.0); kid_at(tuple(gl(X0, -KIDD)[:2]), (GX, GY))
    taken = [V(*gl(X0, -KIDD)[:2], 0)]
    crowd_ring(n=18, r0=13, r1=22, gap=((150, 180), (-180, -150)), face_at=(GX, GY), lie=True, taken=taken)
    c = V(*S7C); at = V(*S7A)
    beasts_front(c, at, (18, 19, 21, 22), 5.0, 10.0, 6, 30, seed=7)
    lamps(False); look_cam(at, c, S7L, clear=3.0)
    go('s07_lay')
def s08_lion():
    """the captain's lion, flat on the stones, ears back; the captain's sword lowered"""
    light_day(off=S8OFF, el=SEL)
    kneel((GX, GY), 0.0)
    cx, cy = S8P; place(CAPT, (cx, cy, GROUND_Z), face_at=(GX, GY)); look_head(CAPTP, pitch=-26); arm(CAPTP, 'R', fwd=-14, out=-6)
    place(LION, (cx + 2.6, cy - 0.8, GROUND_Z), face_at=(GX, GY)); bpose(LIONP, 'lie', head_pitch=16)
    bpy.context.view_layer.update(); ANCHL.setdefault('odds', []).append((tuple(V(cx + 2.6, cy - 0.8, GROUND_Z + 4.6)), '1 IN 80,000'))
    if not bpy.data.objects.get('capsw'): hand_sword(CAPTP, 'R', 'capsw', s=0.8, up=False)
    for j, (dx, dy) in enumerate(((-3.5, -4.5), (1.0, -5.5))):
        rr_, pp_ = GUARDS[j]; place(rr_, (cx + dx, cy + dy, GROUND_Z), face_at=(GX, GY)); look_head(pp_, pitch=-26)
    lp = V(cx + 2.6, cy - 0.8, 0); fl = V(GX, GY, 0) - lp; fl.normalize(); rl = V(fl.y, -fl.x, 0)
    c = lp + fl * S8C[0] + rl * S8C[1]; c.z = GROUND_Z + S8C[2]
    look_cam(V(lp.x + fl.x * 0.5, lp.y + fl.y * 0.5, GROUND_Z + 2.6), c, S8L, clear=3.0)
    go('s08_lion')
def s09_hand():
    """its hand comes down beside the kid, palm up, like a step"""
    light_day(off=S9OFF, el=SEL)
    pc = palm_down((GX + PT[0], GY + PT[1]), 'L')
    kxy = (GX + S9K[0], GY + S9K[1])
    kid_at(kxy, (pc.x, pc.y)); look_head(KIDP, pitch=-6)
    crowd_ring(n=20, r0=17, r1=26, gap=((-60, 10),), face_at=(GX, GY))
    c = V(*S9C); at = V(*S9A)
    lamps(False); look_cam(at, c, S9L, clear=3.0, keep=('kid', 'gk'))
    ANCHL.pop('odds', None)
    go('s09_hand')
def s10_dont():
    """I know what you're thinking. Don't. -- the kid's foot over the edge of the palm; a guard reaching"""
    light_day(off=S10OFF, el=SEL)
    pc = palm_down((GX + PT[0], GY + PT[1]), 'L')
    bpy.context.view_layer.update(); fd = GP['palmL'].matrix_world.to_3x3() @ V(0, 0, -1); fd.z = 0; fd.normalize()
    kp = pc + fd * S10S; kp.z = GROUND_Z
    place(KID, (kp.x, kp.y, GROUND_Z), face_at=(pc.x, pc.y)); rest(KIDP); leg(KIDP, 'R', -40); leg(KIDP, 'L', 10)
    arm(KIDP, 'R', fwd=-30, out=-30); arm(KIDP, 'L', fwd=-20, out=30); look_head(KIDP, pitch=10)
    rr_, pp_ = GUARDS[0]; place(rr_, (kp.x + S10G[0], kp.y + S10G[1], GROUND_Z), face_at=(kp.x, kp.y)); arm(pp_, 'R', fwd=-95, out=-14); arm(pp_, 'L', fwd=-95, out=14); look_head(pp_, pitch=-4)
    crowd_ring(n=20, r0=17, r1=26, gap=((-70, 10),), face_at=(GX, GY))
    away(rr_)
    side = V(-fd.y, fd.x, 0)
    c = kp + fd * S10B + side * S10SS; c.z = GROUND_Z + S10H
    at = pc * (1 - S10K) + kp * S10K; at.z = GROUND_Z + S10AZ
    lamps(False); look_cam(at, c, S10L, clear=1.5, keep=('kid', 'gk'))
    ANCHL.pop('odds', None)
    if DRY:
        print('DRY s10 kp=(%.1f, %.1f) pc=(%.1f, %.1f, %.1f) cam=(%.1f, %.1f, %.1f)' % (kp.x, kp.y, pc.x, pc.y, pc.z, c.x, c.y, c.z), flush=True)
        from bpy_extras.object_utils import world_to_camera_view
        for k_, p_ in (('kidhead', head_of(KIDP) if 'head_of' in globals() else kp + V(0, 0, 5)), ('foot', wpos(KIDP['legR']) if 'legR' in KIDP else kp), ('palm', pc), ('helm', GP['head'].matrix_world @ V(0, 0, 4))):
            a_ = world_to_camera_view(bpy.context.scene, bpy.context.scene.camera, p_); print('DRY s10 %-8s u=%.2f v=%.2f z=%.1f' % (k_, a_.x, a_.y, a_.z), flush=True)
    go('s10_dont')
def s11_did():
    """I did. -- the kid standing on the palm as it lifts"""
    light_day(off=S11OFF, el=SEL)
    kneel((GX, GY), 0.0, lean=20, bow=30, vigil=True); hand_mode(GP, 'L', True)
    up = gl(-5.0, -11.0, 0); up.z = GROUND_Z + S11Z
    sh = wpos(GP['armL']); d = V(0.2, -1, 0).normalized()
    karm(GP, 'L', up - d * 2.0 + V(0, 0, -0.9), sh + V(-9, 4, -6), hand_dir=d, palm_dir=V(0, 0, 1))
    bpy.context.view_layer.update(); pc = GP['palmL'].matrix_world @ V(0, 0, -2.2)
    KID.location = (pc.x, pc.y, pc.z + 0.75); KID.rotation_euler = (0, 0, math.radians(180)); rest(KIDP)
    arm(KIDP, 'R', fwd=-60, out=-40); arm(KIDP, 'L', fwd=-60, out=40); look_head(KIDP, pitch=-20)
    crowd_ring(n=20, r0=14, r1=22, gap=((-70, 10),), face_at=(GX, GY))
    for r, p in CROWD[:20]: look_head(p, pitch=-30)
    c = V(*S11C); at = V(*S11A)
    lamps(False); look_cam(at, c, S11L, clear=3.0, keep=('kid', 'gk'))
    ANCHL.pop('odds', None)
    go('s11_did')
def s12_stand():
    """it stood up, the kid on its shoulder"""
    light_day(off=S12OFF, el=SEL)
    stand((GX, GY), S12F, head=(-6, 10)); on_shoulder('R')
    crowd_ring(n=24, r0=15, r1=26, gap=((-10, 60),), face_at=(GX, GY))
    for r, p in CROWD[:24]: look_head(p, pitch=-36)
    c = V(*S12C)
    lamps(False); look_cam(V(GX, GY, GROUND_Z + S12Z), c, S12L, clear=5.0)
    ANCHL.pop('odds', None)
    go('s12_stand')
def s16_steer():
    """I wasn't steering: the kid holding on to the helm's plume, wind, sky"""
    light_day(off=S16OFF, el=SEL)
    stand((GX, GY), 0.0, head=(-4, 0)); on_shoulder('R')
    arm(KIDP, 'L', fwd=-150, out=-30); arm(KIDP, 'R', fwd=-120, out=-10); kid_face('face_bright_shocked')
    bpy.context.view_layer.update(); hp = head_of(KIDP)
    fw = GIANT.matrix_world.to_3x3() @ V(0, -1, 0); rt = GIANT.matrix_world.to_3x3() @ V(1, 0, 0)
    c = hp + fw * S16C[0] + rt * S16C[1] + V(0, 0, S16C[2])
    look_cam(hp + V(-1.0, 0, -0.4), c, S16L)
    go('s16_steer')
def s02b_rabbits():
    """most kids get a rabbit: a row of kids, each with a rabbit at its feet and the same number over it"""
    light_day(off=R2OFF, el=SEL)
    c = V(*R2C); at = V(*R2A)
    rb = [j for j, (br, bp) in enumerate(BEASTL) if bp['kind'] == 'rabbit'][:5]
    for j, b in enumerate(rb):
        x = (j - 2) * R2DX; y = R2Y + abs(j - 2) * 1.2
        rr_, pp_ = CROWD[j + 3]; place(rr_, (x, y, GROUND_Z), face_at=(c.x, c.y)); look_head(pp_, pitch=14); arm(pp_, 'R', fwd=-12, out=-8); arm(pp_, 'L', fwd=-12, out=8)
        br, bp = BEASTL[b]; place(br, (x + 0.2, y - 2.0, GROUND_Z), face_at=(c.x, c.y)); bpose(bp, 'sit')
        ANCHL.setdefault('odds', []).append((tuple(V(x + 0.2, y - 2.0, GROUND_Z + bp['lh'] + bp['bh'] + 1.5)), '1 IN 2'))
    lamps(False); look_cam(at, c, R2L, clear=3.0)
    go('s02b_rabbits')
def soldiers(xy, face_at, n=5, run=True, shocked=False, spread=2.6):
    """the captain and n guards in a wedge at xy, facing face_at"""
    d = V(face_at[0] - xy[0], face_at[1] - xy[1], 0).normalized(); r = V(d.y, -d.x, 0)
    spots = [(0, 0)] + [((-1) ** k * (1 + k // 2) * spread, -(1 + k // 2) * 1.6) for k in range(n)]
    for k, (sx, sy) in enumerate(spots):
        q = V(xy[0], xy[1], 0) + r * sx + d * sy
        rr_, pp_ = (CAPT, CAPTP) if k == 0 else GUARDS[k - 1]
        place(rr_, (q.x, q.y, GROUND_Z), face_at=face_at); rest(pp_)
        if run:
            leg(pp_, 'L', 38 if k % 2 else -34); leg(pp_, 'R', -34 if k % 2 else 38); arm(pp_, 'L', fwd=-40 if k % 2 else 30); arm(pp_, 'R', fwd=-150 if k == 0 else (30 if k % 2 else -40))
            rr_.rotation_euler.x = math.radians(-8)
        else:
            look_head(pp_, pitch=-34); arm(pp_, 'L', fwd=-10, out=24); arm(pp_, 'R', fwd=-10, out=-24); rr_.rotation_euler.x = math.radians(6)
        set_face('capt' if k == 0 else 'gd%d' % (k - 1), ('face_bold_shocked' if shocked else 'face_bold_angry') if k % 3 == 0 else ('face_bright_shocked' if shocked else 'face_calm_angry'))
    if not bpy.data.objects.get('capsw'): hand_sword(CAPTP, 'R', 'capsw', s=0.8, up=False)
def soldiers_reset():
    CAPT.rotation_euler.x = 0; set_face('capt', 'face_bold')
    for k, (rr_, pp_) in enumerate(GUARDS): rr_.rotation_euler.x = 0; set_face('gd%d' % k, ['face_bold', 'face_calm', 'face_cool'][k % 3])
def s05b_soldiers():
    """the soldiers came to take mine: the captain and his guards charging the giant, the kid in front of it"""
    light_day(off=SOOFF, el=SEL)
    stand((GX, GY), 0.0, head=(14, 0)); kid_at((GX + SOK[0], GY + SOK[1]), (GX, GY - 40)); arm(KIDP, 'L', fwd=0, out=70); arm(KIDP, 'R', fwd=0, out=-70); look_head(KIDP, pitch=0)
    soldiers((GX + 0.5, GY - 26.0), (GX, GY - 9.0), n=5, run=True)
    crowd_ring(n=18, r0=15, r1=24, gap=((-40, 40),), face_at=(GX, GY), taken=[V(GX, GY - 26, 0), V(GX, GY - 9, 0)])
    c = V(*SOC); at = V(*SOA)
    lamps(False); look_cam(at, c, SOL, clear=4.0, keep=('gk', 'kid', 'capt', 'gd'))
    ANCHL.pop('odds', None); giant_tag(up=7.0)
    go('s05b_soldiers'); soldiers_reset()
def s06b_froze():
    """the soldiers froze: the captain and guards staring up, the kneeling giant's shadow over them"""
    light_day(off=FROFF, el=SEL)
    kneel((GX, GY), 0.0); kid_at(tuple(gl(X0, -KIDD)[:2]), (GX, GY))
    soldiers((GX, GY - 31.0), (GX, GY - 10.0), n=5, run=False, shocked=True, spread=2.3)
    c = V(GX + FRC[0], GY - 31 + 8.0 + FRC[1] + 13.5, GROUND_Z + FRC[2]); at = V(GX, GY - 31.0, GROUND_Z + FRA[2])
    lamps(False); look_cam(at, c, FRL, clear=2.0, keep=('capt', 'gd'))
    ANCHL.pop('odds', None)
    go('s06b_froze'); soldiers_reset()
def s14b_captain():
    """the captain yelled: tiny under the standing giant, fist up, his lion flat beside him (seen from up by the kid)"""
    light_day(off=CYOFF, el=SEL)
    stand((GX, GY), 0.0, head=(20, -14)); on_shoulder('R')
    cx, cy = GX + CYP[0], GY + CYP[1]
    place(CAPT, (cx, cy, GROUND_Z), face_at=(GX + 4, GY)); rest(CAPTP); look_head(CAPTP, pitch=-46); arm(CAPTP, 'R', fwd=-165, out=-10); arm(CAPTP, 'L', fwd=-20, out=30)
    set_face('capt', 'face_bold_angry_talk_open')
    place(LION, (cx - 3.0, cy - 0.6, GROUND_Z), face_at=(GX, GY)); bpose(LIONP, 'lie', head_pitch=16)
    ANCHL.setdefault('odds', []).append((tuple(V(cx - 3.0, cy - 0.6, GROUND_Z + 4.6)), '1 IN 80,000'))
    for j, (dx, dy) in enumerate(((2.6, -2.2), (-1.0, -3.6), (4.6, -4.4))):
        rr_, pp_ = GUARDS[j]; place(rr_, (cx + dx, cy + dy, GROUND_Z), face_at=(GX, GY)); look_head(pp_, pitch=-40); set_face('gd%d' % j, 'face_bright_shocked')
    c = V(GX + CYC[0], GY + CYC[1], GROUND_Z + CYC[2])
    lamps(False); look_cam(V(cx, cy, GROUND_Z + 3.6), c, CYL, clear=2.0, keep=('capt', 'gd', 'lion'))
    go('s14b_captain'); soldiers_reset()
SHOTS_ALL = [('s00_hook', s00_hook), ('s01_ground', s01_ground), ('s02_labels', s02_labels), ('s03_mine', s03_mine), ('s04_law', s04_law),
             ('s06_kneel', s06_kneel), ('s07_lay', s07_lay), ('s08_lion', s08_lion), ('s09_hand', s09_hand), ('s10_dont', s10_dont),
             ('s11_did', s11_did), ('s12_stand', s12_stand), ('s02b_rabbits', s02b_rabbits), ('s05b_soldiers', s05b_soldiers), ('s06b_froze', s06b_froze), ('s14b_captain', s14b_captain)]
for _n, _f in SHOTS_ALL:
    if wanted(_n):
        reset(); _f()
reset()
