# A Giant Knelt to Me (Loop a, 11-13): the ceremony square, the crowd and their guardians, the giant (40 ft of empty plate armour),
# the queen, the castle mountain and the titan. exec'd once by gsrv.py. Base = the coin set's proven pieces (look3 light, sky,
# cobbles, camera helpers, the clock tower) without the coin story's statues, room and props.
exec(open('/tmp/claude-0/tv/oc/base.py').read())
OUT = '/tmp/claude-0/tv/gk/it/'; os.makedirs(OUT, exist_ok=True)
from town import build_town
build_town()
random.seed(53)
HX, HY, HZ, HR = 0.0, -8.0, 160.0, 30.0      # look3.py and the Sky helpers refer to these
_SK = open('/tmp/claude-0/tv/sky/set_sky.py').read().split('\n')
def _blk(a, b): exec('\n'.join(_SK[a - 1:b]), globals())
_blk(76, 91); rain(False)          # coin rain meshes + GOLDC
_blk(92, 105)                      # inst_col, place_inst
_blk(114, 125)                     # grey_hair
_blk(230, 254)                     # the clock tower with a clock face
_blk(422, 476)                     # cam_look, _root, _desc, _owner, unhide, clear_view
exec(open('/tmp/claude-0/tv/sky/look3.py').read())
GROUND_Z = 0.2
def look_cam(at, frm, lens, f=None, up=None, clear=None, keep=(), extra=()):
    unhide()
    if up: cam_look(frm, at, lens, up)
    else: cam_at(frm, at, lens)
    if f: dof(f[0], f[1])
    if clear is True: clear_view(at=at, keep=keep, extra=extra)
    elif clear: clear_view(near=clear, keep=keep, extra=extra)
    sun_follow()
def light_day(off=38, el=52):
    light_noon(gold=0, el=el); SUNF['off'] = off
# the ceremony needs an open square: the fountain goes (its parts are glb children named Export_a1_fountain...)
for _o in list(bpy.data.objects):
    if 'fountain' in _o.name.lower(): _o.hide_render = True; _o.hide_viewport = True
# ---------------- 2-bone aiming for any pivot chain ----------------
def _wrot(o):
    bpy.context.view_layer.update(); return o.matrix_world.to_3x3().normalized()
def aim_pivot(o, direction, fwd_hint=(0, -1, 0)):
    """rotate pivot o so its local -z points along world direction; its local -y stays as close as possible to fwd_hint"""
    d = Vector(direction).normalized(); fh = Vector(fwd_hint)
    zl = -d                                             # local +z axis in world
    yl = -(fh - fh.dot(d) * d)                          # local +y = -(forward hint), orthogonal to d
    if yl.length < 1e-4: yl = Vector((0, 1, 0)) - Vector((0, 1, 0)).dot(zl) * zl
    yl.normalize(); xl = yl.cross(zl).normalized()
    Rw = Matrix((xl, yl, zl)).transposed()
    Rp = o.parent.matrix_world.to_3x3().normalized() if o.parent else Matrix.Identity(3)
    o.rotation_euler = (Rp.inverted() @ Rw).to_euler('XYZ'); bpy.context.view_layer.update()
def two_bone(p0, a, b, target, pole):
    """joint position for a chain of lengths a, b from p0 to target, bending toward pole (world points)"""
    p0 = Vector(p0); t = Vector(target); d = t - p0; L = min(d.length, (a + b) * 0.9995); dn = d.normalized()
    x = (a * a - b * b + L * L) / (2 * L); h = math.sqrt(max(0.0, a * a - x * x))
    pv = Vector(pole) - p0; pv = pv - pv.dot(dn) * dn
    pv = pv.normalized() if pv.length > 1e-5 else Vector((0, -1, 0))
    return p0 + dn * x + pv * h, p0 + dn * L
def wpos(o):
    bpy.context.view_layer.update(); return o.matrix_world.translation.copy()
# ---------------- the giant: 40 ft of empty plate armour ----------------
STEEL = mat('gkSteel', srgb(214, 220, 230), 0.32, metal=1.0)
STEELD = mat('gkSteelD', srgb(112, 118, 132), 0.36, metal=1.0)
TRIM = mat('gkTrim', srgb(240, 182, 66), 0.22, metal=1.0)
CAPE = mat('gkCape', srgb(30, 56, 156), 0.85)
VOID = mat('gkVoid', srgb(6, 6, 10), 0.95)
VISOR = emat('gkVisor', (1.0, 0.70, 0.22), 14.0)
LEATH = mat('gkLeath', srgb(70, 44, 28), 0.8)
KL = dict(thigh=8.6, shin=8.2, sole=1.2, ua=8.4, fa=7.2, fist=1.9)      # bone lengths (unscaled)
def build_knight(name, s=1.0, steel=STEEL, dark=STEELD, trim=TRIM, cape=CAPE, eye=VISOR):
    """origin at the feet, faces -y. parts: hip, legL/R, kneeL/R, footL/R, tor, head, armL/R, elbL/R, handL/R, palmL/R, fistL/R.
    L is the -x side (the giant's own right hand when it faces the camera). v2: a knight, not a robot: bucket great helm with a
    cross visor and plume, rounded pauldrons, a royal-blue surcoat with a gold sun, slimmer limbs, a long cape."""
    root = empty(name); root.scale = (s,) * 3; P = {'root': root, 's': s}
    hip = empty(name + 'hip', (0, 0, 18.0), root); P['hip'] = hip
    for side, x in (('L', -3.2), ('R', 3.2)):
        lp = empty(name + 'leg' + side, (x, 0, 0), hip); P['leg' + side] = lp
        fbox(name + 'th' + side, (4.6, 5.0, 8.8), (0, 0, -4.2), steel, parent=lp, bevel=0.7)
        fbox(name + 'thb' + side, (4.9, 5.3, 0.8), (0, 0, -1.4), trim, parent=lp, bevel=0.2)
        kn = empty(name + 'knee' + side, (0, 0, -8.6), lp); P['knee' + side] = kn
        k1 = fsphere(name + 'kg' + side, 2.2, (0, -1.6, 0.0), steel, parent=kn, seg=16); k1.scale = (1.15, 0.8, 1.0)
        fsphere(name + 'kgs' + side, 0.9, (0, -3.3, 0.0), trim, parent=kn, seg=12)
        fbox(name + 'shin' + side, (4.2, 4.6, 7.6), (0, 0, -4.4), steel, parent=kn, bevel=0.8)
        fbox(name + 'shinr' + side, (0.7, 0.5, 6.4), (0, -2.4, -4.4), trim, parent=kn, bevel=0.15)
        ft = empty(name + 'foot' + side, (0, 0, -8.2), kn); P['foot' + side] = ft
        fbox(name + 'sab' + side, (4.6, 7.6, 2.2), (0, -1.6, -0.1), dark, parent=ft, bevel=0.6)
        fbox(name + 'sabt' + side, (3.6, 2.6, 1.4), (0, -5.2, -0.5), steel, parent=ft, bevel=0.5)
    tor = empty(name + 'tor', (0, 0, 0), hip); P['tor'] = tor
    fbox(name + 'fauld', (12.0, 7.6, 4.0), (0, 0, 0.5), steel, parent=tor, bevel=0.8)
    fbox(name + 'belt', (12.4, 8.0, 1.2), (0, 0, 2.7), LEATH, parent=tor, bevel=0.3)
    fsphere(name + 'buckle', 0.9, (0, -4.1, 2.7), trim, parent=tor, seg=12)
    fbox(name + 'abd', (11.0, 7.0, 4.4), (0, 0, 5.2), dark, parent=tor, bevel=0.5)
    ch = fsphere(name + 'chest', 1.0, (0, 0, 10.8), steel, parent=tor, seg=28); ch.scale = (7.6, 4.8, 5.6)
    fbox(name + 'surc', (10.4, 0.6, 10.2), (0, -4.3, 8.4), cape, parent=tor, bevel=0.3)
    fbox(name + 'surcT', (10.6, 0.64, 0.7), (0, -4.34, 13.4), trim, parent=tor, bevel=0.1)
    fbox(name + 'surcB', (10.6, 0.64, 0.7), (0, -4.34, 3.4), trim, parent=tor, bevel=0.1)
    fcyl(name + 'sun', 1.9, 0.5, (0, -4.75, 9.2), trim, parent=tor, verts=24, rot=(math.radians(90), 0, 0))
    for k in range(8):
        a = k / 8 * math.tau
        fbox(name + 'ray%d' % k, (0.6, 0.4, 1.3), (math.sin(a) * 2.8, -4.7, 9.2 + math.cos(a) * 2.8), trim, parent=tor, rot=(0, -a, 0), bevel=0.1)
    fbox(name + 'gorget', (7.6, 6.6, 2.2), (0, 0, 15.6), dark, parent=tor, bevel=0.6)
    fbox(name + 'cape', (12.4, 0.6, 22.0), (0, 4.6, 4.0), cape, parent=tor, bevel=0.2)
    fbox(name + 'capeT', (12.6, 0.66, 0.9), (0, 4.62, 14.6), trim, parent=tor, bevel=0.1)
    nk = empty(name + 'neck', (0, 0, 16.4), tor); P['head'] = nk
    fcyl(name + 'helm', 3.5, 7.8, (0, 0, 3.9), steel, parent=nk, verts=32)
    hl = fcyl(name + 'helmtop', 3.5, 0.9, (0, 0, 8.1), steel, parent=nk, verts=32, r2=2.6)
    fcyl(name + 'hband', 3.62, 0.8, (0, 0, 1.0), trim, parent=nk, verts=32)
    fbox(name + 'hridge', (0.6, 7.4, 0.6), (0, 0, 8.4), trim, parent=nk, bevel=0.15)
    fbox(name + 'visS', (5.0, 1.2, 0.85), (0, -3.05, 4.9), VOID, parent=nk, bevel=0.1)       # cross visor: eye slit
    fbox(name + 'visV', (0.9, 1.2, 3.6), (0, -3.05, 2.9), VOID, parent=nk, bevel=0.1)        # breath slit
    fbox(name + 'eyeS', (4.4, 0.2, 0.42), (0, -3.6, 4.9), eye, parent=nk)
    fbox(name + 'eyeV', (0.42, 0.2, 2.8), (0, -3.6, 3.0), eye, parent=nk)
    fbox(name + 'visT', (5.6, 0.6, 0.5), (0, -3.4, 5.6), trim, parent=nk, bevel=0.1)
    pm = mat(name + 'plm', srgb(196, 28, 36), 0.85)
    for k in range(5):
        fbox(name + 'plume%d' % k, (1.2, 1.6, 2.6 - k * 0.25), (0, -1.6 + k * 1.5, 9.8 + math.sin(k / 4 * math.pi) * 0.9 - k * 0.15), pm, parent=nk, bevel=0.45,
             rot=(math.radians(-15 + k * 14), 0, 0))
    P['eye'] = [o for o in nk.children if o.name.startswith(name + 'eye')]
    for side, x in (('L', -1), ('R', 1)):
        sp = empty(name + 'arm' + side, (x * 9.0, 0, 13.6), tor); P['arm' + side] = sp
        pd = fsphere(name + 'pauld' + side, 1.0, (x * 0.6, 0, 0.6), steel, parent=sp, seg=24); pd.scale = (3.8, 4.4, 3.2)
        pr = fcyl(name + 'pauldr' + side, 3.9, 0.7, (x * 0.6, 0, -0.9), trim, parent=sp, verts=24); pr.scale = (1.0, 1.15, 1.0)
        fbox(name + 'ua' + side, (3.6, 3.8, 7.0), (0, 0, -4.8), dark, parent=sp, bevel=0.6)
        el = empty(name + 'elb' + side, (0, 0, -KL['ua']), sp); P['elb' + side] = el
        fsphere(name + 'ec' + side, 1.6, (0, 0.5, 0.2), steel, parent=el, seg=14)
        fbox(name + 'fa' + side, (3.8, 4.0, 5.6), (0, 0, -3.0), steel, parent=el, bevel=0.6)
        cf = fcyl(name + 'cuff' + side, 2.6, 2.2, (0, 0, -6.1), trim, parent=el, verts=20, r2=3.1)
        hd = empty(name + 'hand' + side, (0, 0, -KL['fa']), el); P['hand' + side] = hd
        fi = empty(name + 'fist' + side, (0, 0, 0), hd); P['fist' + side] = fi
        fbox(name + 'fs' + side, (3.8, 4.0, 3.4), (0, 0, -1.8), dark, parent=fi, bevel=0.6)
        for k in range(4):
            fbox(name + 'fk%s%d' % (side, k), (0.85, 0.9, 0.8), (-1.35 + k * 0.9, -2.1, -2.7), steel, parent=fi, bevel=0.15)
        pa = empty(name + 'palm' + side, (0, 0, 0), hd); P['palm' + side] = pa       # open hand: palm faces local -y, fingers along -z
        fbox(name + 'ps' + side, (4.2, 1.5, 4.0), (0, 0, -2.0), dark, parent=pa, bevel=0.4)
        for k in range(4):
            fbox(name + 'pf%s%d' % (side, k), (0.95, 1.2, 3.4), (-1.5 + k * 1.0, 0.0, -5.6), dark, parent=pa, bevel=0.2)
            fbox(name + 'pn%s%d' % (side, k), (1.0, 1.26, 0.6), (-1.5 + k * 1.0, 0.0, -4.2), steel, parent=pa, bevel=0.1)
        fbox(name + 'pt' + side, (1.1, 1.2, 2.8), (x * -2.7, -0.8, -1.7), dark, parent=pa, bevel=0.2, rot=(0, math.radians(x * 25), 0))
        for c in [pa] + list(pa.children): c.hide_render = True
    return root, P
def hand_mode(P, side, open_):
    for c in [P['palm' + side]] + list(P['palm' + side].children): c.hide_render = not open_
    for c in [P['fist' + side]] + list(P['fist' + side].children): c.hide_render = open_
def kreset(P):
    for k in ('hip', 'tor', 'head', 'legL', 'legR', 'kneeL', 'kneeR', 'footL', 'footR', 'armL', 'armR', 'elbL', 'elbR', 'handL', 'handR'):
        P[k].rotation_euler = (0, 0, 0)
    P['hip'].location = (0, 0, 18.0); hand_mode(P, 'L', False); hand_mode(P, 'R', False); bpy.context.view_layer.update()
def kleg(P, side, foot_at, knee_pole, sole_flat=True):
    """place a leg so its foot pivot lands at world foot_at, knee bending toward world knee_pole"""
    s = P['s']; hp = wpos(P['leg' + side])
    kn, ft = two_bone(hp, KL['thigh'] * s, KL['shin'] * s, foot_at, knee_pole)
    fwd = P['root'].matrix_world.to_3x3() @ Vector((0, -1, 0))
    aim_pivot(P['leg' + side], kn - hp, fwd); aim_pivot(P['knee' + side], ft - kn, fwd)
    if sole_flat:
        aim_pivot(P['foot' + side], Vector((0, 0, -1)), fwd)
def karm(P, side, hand_at, elbow_pole, palm_dir=None, hand_dir=None):
    """place an arm so the hand pivot lands at world hand_at; palm_dir = world direction the open palm faces"""
    s = P['s']; sp = wpos(P['arm' + side])
    el, hd = two_bone(sp, KL['ua'] * s, KL['fa'] * s, hand_at, elbow_pole)
    fwd = P['root'].matrix_world.to_3x3() @ Vector((0, -1, 0))
    aim_pivot(P['arm' + side], el - sp, fwd); aim_pivot(P['elb' + side], hd - el, fwd)
    if hand_dir is not None:
        aim_pivot(P['hand' + side], Vector(hand_dir), Vector(palm_dir) if palm_dir is not None else fwd)
    return el, hd
SWS = mat('gkBlade', srgb(222, 230, 240), 0.16, metal=1.0)
def build_greatsword(name, s=1.0):
    """origin at the crossguard; the blade points down local -z (17 long), the grip and pommel up"""
    r = empty(name); r.scale = (s,) * 3
    fbox(name + 'bl', (1.6, 0.42, 16.0), (0, 0, -8.6), SWS, parent=r, bevel=0.12)
    fbox(name + 'fu', (0.36, 0.46, 13.0), (0, 0, -7.6), STEELD, parent=r)
    t = fcyl(name + 'tip', 1.13, 1.8, (0, 0, -17.4), SWS, parent=r, verts=4, r2=0.0, rot=(0, 0, math.radians(45)))
    t.rotation_euler = (math.radians(180), 0, math.radians(45)); t.scale = (1.0, 0.27, 1.0)
    fbox(name + 'cg', (7.2, 1.3, 1.2), (0, 0, 0), TRIM, parent=r, bevel=0.3)
    fbox(name + 'gr', (1.0, 1.0, 4.2), (0, 0, 2.6), LEATH, parent=r)
    fsphere(name + 'pm', 1.0, (0, 0, 5.3), TRIM, parent=r, seg=14)
    return r
GIANT, GP = build_knight('gk', 1.0)
SWORD = build_greatsword('gsw', 1.0)
# ---------------- guardians: blocky animals (origin at the feet, facing -y) ----------------
def _bm(nm, rgb, r=0.8): return bpy.data.materials.get(nm) or mat(nm, srgb(*rgb), r)
EYEB = mat('bEye', srgb(16, 14, 16), 0.3)
BEASTS = {   # body (w, l, h), leg (w, h), head (w, l, h), colours (main, light), ears, tail, extras
    'rabbit': dict(body=(1.1, 1.5, 1.0), leg=(0.34, 0.32), head=(0.9, 0.9, 0.8), col=((236, 232, 226), (250, 200, 206)), ears='long', tail='puff'),
    'goat': dict(body=(1.3, 2.4, 1.3), leg=(0.36, 1.4), head=(0.8, 1.2, 0.9), col=((232, 226, 214), (60, 52, 48)), ears='flop', tail='stub', horns=True),
    'fox': dict(body=(1.0, 2.2, 1.0), leg=(0.3, 0.9), head=(0.95, 1.1, 0.85), col=((226, 120, 46), (246, 240, 232)), ears='point', tail='bush'),
    'wolf': dict(body=(1.5, 3.2, 1.5), leg=(0.46, 1.6), head=(1.3, 1.6, 1.2), col=((128, 130, 140), (210, 210, 214)), ears='point', tail='wolf'),
    'lion': dict(body=(1.9, 3.8, 1.9), leg=(0.62, 1.9), head=(1.6, 1.7, 1.5), col=((214, 160, 80), (240, 214, 160)), ears='round', tail='tuft', mane=(150, 82, 38)),
    'bear': dict(body=(2.4, 3.6, 2.3), leg=(0.8, 1.5), head=(1.7, 1.6, 1.5), col=((104, 70, 46), (150, 110, 80)), ears='round', tail='stub'),
}
def build_beast(name, kind, s=1.0):
    B = BEASTS[kind]; c0, c1 = B['col']
    m0 = _bm('b_' + kind, c0); m1 = _bm('b_' + kind + 'L', c1)
    root = empty(name); root.scale = (s,) * 3; P = {'root': root, 'kind': kind}
    bw, bl, bh = B['body']; lw, lh = B['leg']; hw, hl, hh = B['head']
    body = empty(name + 'bd', (0, 0, lh + bh / 2), root); P['body'] = body
    fbox(name + 'b', (bw, bl, bh), (0, 0, 0), m0, parent=body, bevel=min(bw, bh) * 0.18)
    fbox(name + 'bb', (bw * 0.8, bl * 0.7, 0.1), (0, -bl * 0.05, -bh / 2), m1, parent=body)
    P['legs'] = []
    for i, (x, y) in enumerate(((-1, -1), (1, -1), (-1, 1), (1, 1))):
        lp = empty(name + 'lp%d' % i, (x * (bw / 2 - lw / 2), y * (bl / 2 - lw * 0.8), -bh / 2 + 0.05), body)
        fbox(name + 'lg%d' % i, (lw, lw, lh + 0.05), (0, 0, -lh / 2), m0, parent=lp, bevel=lw * 0.15)
        P['legs'].append(lp)
    hd = empty(name + 'hdp', (0, -bl / 2 - hl * 0.28, bh * 0.38), body); P['head'] = hd
    fbox(name + 'h', (hw, hl, hh), (0, -hl * 0.3, hh * 0.25), m0, parent=hd, bevel=min(hw, hh) * 0.2)
    sn = 0.42 if kind in ('fox', 'wolf') else (0.3 if kind in ('lion', 'bear', 'goat') else 0.16)
    if sn > 0.2:
        fbox(name + 'sn', (hw * 0.55, hl * sn, hh * 0.45), (0, -hl * 0.8 - hl * sn * 0.4, hh * 0.05), m1, parent=hd, bevel=hh * 0.08)
    nz_y = -hl * 0.8 - hl * sn * 0.85
    fbox(name + 'ns', (hw * 0.2, 0.12, hh * 0.14), (0, nz_y - 0.02, hh * 0.22), EYEB, parent=hd, bevel=0.03)
    for x in (-1, 1):
        fbox(name + 'ey%d' % x, (hw * 0.14, 0.1, hh * 0.18), (x * hw * 0.26, -hl * 0.8 + 0.02, hh * 0.45), EYEB, parent=hd, bevel=0.02)
    e = B['ears']
    for x in (-1, 1):
        if e == 'long':
            fbox(name + 'ea%d' % x, (0.22, 0.14, 1.0), (x * 0.22, -hl * 0.2, hh * 0.25 + hh / 2 + 0.45), m0, parent=hd, bevel=0.06, rot=(math.radians(-8), math.radians(x * 8), 0))
            fbox(name + 'ei%d' % x, (0.12, 0.05, 0.8), (x * 0.22, -hl * 0.2 - 0.08, hh * 0.25 + hh / 2 + 0.45), m1, parent=hd, rot=(math.radians(-8), math.radians(x * 8), 0))
        elif e == 'point':
            fbox(name + 'ea%d' % x, (hw * 0.26, 0.16, hh * 0.5), (x * hw * 0.3, -hl * 0.1, hh * 0.25 + hh / 2 + hh * 0.18), m0, parent=hd, bevel=0.03, rot=(0, math.radians(x * 12), 0))
        elif e == 'round':
            fbox(name + 'ea%d' % x, (hw * 0.24, 0.2, hh * 0.24), (x * hw * 0.36, -hl * 0.05, hh * 0.25 + hh / 2 + hh * 0.06), m0, parent=hd, bevel=0.06)
        elif e == 'flop':
            fbox(name + 'ea%d' % x, (hw * 0.5, 0.14, hh * 0.24), (x * hw * 0.62, -hl * 0.05, hh * 0.45), m0, parent=hd, bevel=0.04, rot=(0, math.radians(x * -20), 0))
    if B.get('horns'):
        hm = _bm('b_horn', (90, 80, 70), 0.6)
        for x in (-1, 1):
            fbox(name + 'hn%d' % x, (0.18, 0.18, 0.9), (x * 0.22, hl * 0.05, hh * 0.25 + hh / 2 + 0.3), hm, parent=hd, rot=(math.radians(35), 0, 0), bevel=0.04)
            fbox(name + 'bd%d' % x, (0.2, 0.2, 0.4), (0, -hl * 0.75, -hh * 0.2), m0, parent=hd) if x < 0 else None
    t = B['tail']; tp = empty(name + 'tp', (0, bl / 2, bh * 0.25), body); P['tail'] = tp
    if t == 'puff': fsphere(name + 'tl', 0.3, (0, 0.15, 0), m1, parent=tp, seg=12)
    elif t == 'bush':
        fbox(name + 'tl', (0.55, 1.6, 0.55), (0, 0.75, -0.25), m0, parent=tp, bevel=0.2, rot=(math.radians(-20), 0, 0))
        fbox(name + 'tt', (0.5, 0.45, 0.5), (0, 1.6, -0.55), m1, parent=tp, bevel=0.15, rot=(math.radians(-20), 0, 0))
    elif t == 'wolf': fbox(name + 'tl', (0.45, 1.7, 0.45), (0, 0.75, -0.45), m0, parent=tp, bevel=0.12, rot=(math.radians(-32), 0, 0))
    elif t == 'tuft':
        fbox(name + 'tl', (0.2, 2.0, 0.2), (0, 0.9, -0.5), m0, parent=tp, rot=(math.radians(-28), 0, 0))
        fbox(name + 'tt', (0.42, 0.5, 0.42), (0, 1.85, -1.0), _bm('b_mane', B.get('mane', (150, 82, 38))), parent=tp, bevel=0.12)
    else: fbox(name + 'tl', (0.4, 0.5, 0.4), (0, 0.15, 0), m0, parent=tp, bevel=0.1)
    if B.get('mane'):
        mm = _bm('b_mane', B['mane'], 0.95)
        fbox(name + 'mn', (hw * 1.75, hl * 0.6, hh * 1.75), (0, hl * 0.1, hh * 0.25), mm, parent=hd, bevel=0.35)
        fbox(name + 'mc', (bw * 1.08, bl * 0.3, bh * 1.08), (0, -bl * 0.32, 0.02), mm, parent=body, bevel=0.3)
    P['lh'] = lh; P['bh'] = bh
    return root, P
def bpose(P, mode='stand', head_pitch=0, head_yaw=0):
    """stand / lie (flat on the stones, legs tucked, chin down) / sit"""
    body = P['body']; lh, bh = P['lh'], P['bh']
    for lp in P['legs']: lp.rotation_euler = (0, 0, 0)
    body.rotation_euler = (0, 0, 0); body.location.z = lh + bh / 2
    hp, hy = head_pitch, head_yaw
    if mode == 'lie':
        body.location.z = bh / 2 + 0.04
        for i, lp in enumerate(P['legs']): lp.rotation_euler = (math.radians(-88 if i < 2 else 88), 0, 0)
        hp = head_pitch or 22
    elif mode == 'sit':
        body.rotation_euler = (math.radians(-28), 0, 0); body.location.z = lh * 0.55 + bh / 2
        for i, lp in enumerate(P['legs']): lp.rotation_euler = (math.radians(28 if i < 2 else 80), 0, 0)
    P['head'].rotation_euler = (math.radians(hp), 0, math.radians(hy))
# ---------------- the cast ----------------
KID, KIDP = person('kid', (206, 76, 48), (52, 58, 82), 'hero_crop', 'face_bright', skin=(238, 196, 156)); KID.scale = (0.8, 0.8, 0.8)
CROWD = []
for _i in range(26):
    _r, _p = person('cw%d' % _i, SHIRTS[_i % 8], PANTS[_i % 4], HAIRS[(_i * 5) % 9], FACES[(_i * 4) % 9], skin=SKINS[(_i * 3) % 8])
    CROWD.append((_r, _p)); away(_r)
CAPT, CAPTP = person('capt', (190, 196, 206), (70, 74, 86), 'hero_slick_back', 'face_bold', skin=(206, 150, 112), beard='face_full_beard')
fbox('captpl', (2.14, 1.14, 1.9), (0, 0, 3.05), mat('captplm', srgb(206, 212, 222), 0.25, metal=1.0), parent=CAPT, bevel=0.08)
fbox('captsh', (2.2, 1.2, 0.3), (0, 0, 3.9), TRIM, parent=CAPT, bevel=0.05)
GUARDS = []
for _i in range(6):
    _r, _p = person('gd%d' % _i, (190, 196, 206), (70, 74, 86), 'hero_crop', ['face_bold', 'face_calm', 'face_cool'][_i % 3], skin=SKINS[(_i * 5 + 1) % 8])
    fbox('gdpl%d' % _i, (2.12, 1.12, 1.9), (0, 0, 3.05), bpy.data.materials['captplm'], parent=_r, bevel=0.08)
    fbox('gdhm%d' % _i, (1.4, 1.4, 0.7), (0, 0, 0.55), bpy.data.materials['captplm'], parent=_p['head'], bevel=0.12)
    GUARDS.append((_r, _p)); away(_r)
for _o in (KID, CAPT): away(_o)
BEASTL = []
_KINDS = ['rabbit', 'fox', 'goat', 'rabbit', 'wolf', 'fox', 'rabbit', 'goat', 'bear', 'rabbit', 'fox', 'wolf', 'rabbit', 'goat', 'fox', 'rabbit',
          'wolf', 'rabbit', 'fox', 'goat', 'rabbit', 'bear', 'fox', 'rabbit', 'wolf', 'rabbit']
ODDS = {'rabbit': '1 IN 2', 'fox': '1 IN 60', 'goat': '1 IN 15', 'wolf': '1 IN 900', 'bear': '1 IN 4,000', 'lion': '1 IN 80,000'}
for _i, _k in enumerate(_KINDS):
    _r, _p = build_beast('bst%d' % _i, _k, 1.0); BEASTL.append((_r, _p)); away(_r)
LION, LIONP = build_beast('lion', 'lion', 1.0); away(LION)
for _o in (GIANT, SWORD): away(_o)
print('SET GK READY', flush=True)
