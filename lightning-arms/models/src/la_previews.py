# Lightning Arms preview stills. SHOT=<name> python3 -I la_previews.py  (writes ../_pv_<name>.png)
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from la_pv import *
SHOT = os.environ.get('SHOT', 'gate')
OUT = os.path.join(HERE, '..', f'_pv_{SHOT}.png')
E = os.environ.get


def root_of(c):
    return [o for o in list(c.all_objects) if o.parent is None and o.type == 'EMPTY'][0]


def cam_env(cam0, at0, lens0):
    cx, cy, cz = [float(x) for x in E('CAM', cam0).split(',')]
    ax, ay, az = [float(x) for x in E('AT', at0).split(',')]
    return camera_((cx, cy, cz), (ax, ay, az), float(E('LENS', lens0)))


KIND = E('KIND', 'day')
EXPO = float(E('EXPO')) if E('EXPO') else None

if SHOT == 'gate':
    ground('#8C8478')
    c = append('LA_GateOfOaths')
    la.set_eyes(c, float(E('EYES', 0)))
    if E('SHAKE'):
        la.set_shake(c, 1.0, seed=3)
    if E('CHAINS'):
        append('LA_GateChains')
    person('Hero kid', (0, -9, 0), rz=180)
    person('Little sister', (4, -8, 0), rz=150)
    cam = cam_env('16,-52,7', '0,0,12.5', 35)
    render(cam, OUT, kind=KIND, sun_el=45, exposure=EXPO)

if SHOT == 'beast':
    names = ['STAND', 'PULL', 'CHARGE', 'SKID', 'KNEEL', 'BOW', 'BOW_TO_KID']
    only = E('ONLY')
    for n in names:
        if only and n not in only.split(','):
            continue
        new_scene()
        ground('#8C8478')
        c = append('LA_WarBeast')
        rig = find(c, 'LA_WarBeast_Rig')
        la.apply_pose(rig, 'LA_BEAST_' + n, poses_json=PJ)
        if n in ('KNEEL', 'BOW_TO_KID', 'BOW'):
            la.show(find(c, 'LA_WarBeast_SisterChain_Taut'), False); la.show(find(c, 'LA_WarBeast_SisterChain_Dropped'), True)
            la.show(find(c, 'LA_WarBeast_LeadChain_Taut'), False); la.show(find(c, 'LA_WarBeast_LeadChain_Dropped'), True)
            la.show(find(c, 'LA_WarBeast_Cuff'), False)
        person('Hero kid', (0, -36 if n != 'CHARGE' else -40, 0), rz=180)
        if E('SIDE'):
            cam = camera_((-110, -8, 9), (0, -2, 10), 50)
        else:
            cam = cam_env('46,-78,13', '0,-4,9.5', 50)
        render(cam, os.path.join(HERE, '..', f'_pv_beast_{n}{"_side" if E("SIDE") else ""}.png'), kind=KIND, sun_el=45, az_off=25 if not E('SIDE') else -30, w=int(E('TW', 600)), h=int(E('TH', 450)), exposure=float(E('EXPO', -1.05)))

if SHOT == 'ltest':
    ground('#6E6A72' if KIND != 'day' else '#8C8478')
    k = person('Hero kid', (0, 0, 0), rz=-14, arms={'L': (-150, 0, -20), 'R': (-140, 0, 20)} if not E('DOWN') else None)
    c = append('LA_LightningArms')
    for sd, lt in (('L', 'A'), ('R', 'C')):
        r = find(c, 'LA_LightningArm_' + sd)
        la.attach_arm(r, la.cast_arm(k, sd)); la.variant(r, lt); la.set_prop(r, 'glow', float(E('GLOW', 1)))
    if E('BURST'):
        b = append('LA_SparkBurst'); find(b, 'LA_SparkBurst').location = (2.5, -1.0, 4.6)
    person('Little sister', (-3.4, 0.6, 0), rz=20)
    cam = cam_env('1.5,-13,3.2', '0,0,3.0', 50)
    render(cam, OUT, kind=KIND, sun_el=45, exposure=EXPO, auto=False)

if SHOT == 'split':
    ground('#8C8478')
    c = append('LA_GroundSplit')
    la.set_prop(find(c, 'LA_GroundSplit'), 'amount', float(E('AMOUNT', 1)))
    person('Hero kid', (0, 7, 0), rz=180)
    cam = cam_env('10,-34,22', '0,2,0', 28)
    render(cam, OUT, kind=KIND, sun_el=45, exposure=EXPO, auto=False)

if SHOT == 'armsv':
    # stone / iron arms on the Villain, stone 0 / 0.5 / 1, and stone arms on a kid
    ground('#8C8478')
    vals = [0.0, 0.5, 1.0]
    for i, sv in enumerate(vals):
        v = person('Villain', (-5 + i * 5, 0, 0), rz=-8, arms={'L': (-35, 0, -8), 'R': (-20, 0, 8)})
        c = append('LA_IronArms')
        b = append('LA_WristNumbers')
        for sd in ('L', 'R'):
            r = find(c, 'LA_IronArm_Villain_' + sd); la.attach_arm(r, la.cast_arm(v, sd)); la.set_prop(r, 'stone', sv)
            bd = find(b, 'LA_WristBand_Villain_' + sd); la.attach_arm(bd, la.cast_arm(v, sd), hide_cast=False); la.set_number(bd, '1 IN 1,000,000' if sv < 1 else '1 IN 2')
            for k in ('L', 'R'):
                la.show(find(b, f'LA_WristBand_Kid_{k}'), False)
        for o in list(v.all_objects):
            if o.name.split('.')[0] in ('vstaff', 'vorb'):
                o.hide_render = True
        if i == 2:
            cr = append('LA_IronCrown'); la.crown_on(find(cr, 'LA_IronCrown'), v)
            ch = append('LA_GateChains'); la.show(find(ch, 'LA_GateChains_Hanging'), False)
            for sd in ('L', 'R'):
                la.cuff_on(find(ch, 'LA_GateChains_Cuff_' + sd), la.cast_arm(v, sd))
    k = person('Hero kid', (-9.5, 0, 0), rz=-20, arms={'L': (-40, 0, 0)})
    c = append('LA_StoneArms'); b = append('LA_WristNumbers')
    for sd in ('L', 'R'):
        la.attach_arm(find(c, 'LA_StoneArm_Kid_' + sd), la.cast_arm(k, sd))
        bd = find(b, 'LA_WristBand_Kid_' + sd); la.attach_arm(bd, la.cast_arm(k, sd), hide_cast=False); la.set_number(bd, '1 IN 2')
        la.show(find(c, 'LA_StoneArm_Villain_' + sd), False); la.show(find(b, 'LA_WristBand_Villain_' + sd), False)
    cam = cam_env('-2,-22,4', '-2,0,3.4', 50)
    render(cam, OUT, kind=KIND, sun_el=45, exposure=EXPO if EXPO is not None else -1.05, auto=False)

if SHOT == 'crown':
    ground('#8C8478')
    v = person('Villain', (0, 0, 0), rz=-14)
    cr = append('LA_IronCrown'); la.crown_on(find(cr, 'LA_IronCrown'), v)
    c2 = append('LA_IronCrown'); find(c2, 'LA_IronCrown').location = (2.6, -2.5, 0)
    cam = cam_env('1.6,-9.5,6.0', '0.6,0,5.6', 50)
    render(cam, OUT, kind=KIND, sun_el=45, exposure=EXPO if EXPO is not None else -1.05, auto=False)

if SHOT == 'bands':
    ground('#8C8478')
    b = append('LA_WristNumbers')
    for i, (sd, who, t) in enumerate((('L', 'Kid', '1 IN 2'), ('R', 'Kid', '1 IN 10,000,000'), ('L', 'Villain', '1 IN 1,000,000'))):
        o = find(b, f'LA_WristBand_{who}_{sd}'); la.set_number(o, t)
        zc = 0.72 if who == 'Kid' else 1.19
        o.location = (-1.5 + i * 1.5, 0, 1.2 + zc)
    la.show(find(b, 'LA_WristBand_Villain_R'), False)
    cam = cam_env('0,-5.2,1.3', '0,0,1.2', 50)
    render(cam, OUT, kind=KIND, sun_el=45, exposure=EXPO if EXPO is not None else -1.05, auto=False)

if SHOT == 'sky':
    ground('#3A3F4A')
    b = append('LA_SkyNumber'); o = find(b, 'LA_SkyNumber'); o.location = (0, 0, 20); la.set_prop(o, 'digits', float(E('DIGITS', 1)))
    person('Hero kid', (0, -30, 0), rz=180)
    cam = cam_env('0,-170,6', '0,0,34', 35)
    render(cam, OUT, kind=KIND, sun_el=45, exposure=EXPO if EXPO is not None else 0, auto=False)

if SHOT == 'giant':
    for n in (E('ONLY') or 'STANDING,RISING,LOOKING_DOWN').split(','):
        new_scene()
        ground('#6F7A5C')
        c = append('LA_GateGiant')
        la.apply_pose(find(c, 'LA_GateGiant_Rig'), 'LA_GIANT_' + n, poses_json=PJ)
        la.set_eyes(c, 1.0, base='LA_GateGiant_Body')
        person('Hero kid', (0, -60, 0), rz=180)
        # a stand-in for the backlot castle keep (17 m = 56 BU) and a house (14 m roofs = 46 BU would be the tallest; houses about 26)
        m = L.mat('PV_Keep', '#B9A98C', 0.9, vcol=False)
        for (sz, loc) in (((46, 26, 56), (-75, 30, 28)), ((14, 14, 66), (-98, 17, 33)), ((14, 14, 66), (-52, 17, 33)), ((18, 14, 26), (62, -20, 13)), ((16, 14, 22), (84, -6, 11))):
            bpy.ops.mesh.primitive_cube_add(size=1, location=loc); o = bpy.context.active_object; o.scale = sz; o.data.materials.append(m)
        if E('SKY'):
            sk = append('LA_SkyNumber'); so = find(sk, 'LA_SkyNumber'); la.set_prop(so, 'digits', float(E('SKY')))
            bpy.context.view_layer.update()
            so.location = find(c, 'LA_GateGiant_Socket_HeadTop').matrix_world.translation + Vector((0, 0, 8))
        cam = cam_env('70,-330,10', '0,0,78', 35)
        render(cam, os.path.join(HERE, '..', f'_pv_giant_{n}.png'), kind=KIND, sun_el=40, az_off=25, w=int(E('TW', 540)), h=int(E('TH', 720)), exposure=EXPO if EXPO is not None else -1.05, auto=False)

if SHOT == 'lashed':
    ground('#8C8478')
    g = append('LA_GateOfOaths'); la.set_eyes(g, 1.0)
    ch = append('LA_GateChains')
    la.show(find(ch, 'LA_GateChains_Hanging'), False); la.show(find(ch, 'LA_GateChains_Lashed'), True)
    v = person('Villain', (0, -12, 0), rz=0)
    for o in list(v.all_objects):
        if o.name.split('.')[0] in ('vstaff', 'vorb'):
            o.hide_render = True
    ia = append('LA_IronArms')
    for sd in ('L', 'R'):
        r = find(ia, 'LA_IronArm_Villain_' + sd); la.attach_arm(r, la.cast_arm(v, sd)); la.set_prop(r, 'stone', 0.55)
        la.cuff_on(find(ch, 'LA_GateChains_Cuff_' + sd), la.cast_arm(v, sd))
    cr = append('LA_IronCrown'); la.crown_on(find(cr, 'LA_IronCrown'), v)
    person('Hero kid', (3.5, -18, 0), rz=160)
    cam = cam_env('9,-40,6', '0,-6,9', 35)
    render(cam, OUT, kind=KIND, sun_el=45, exposure=EXPO if EXPO is not None else -1.05, auto=False)

if SHOT == 'lineup':
    ground('#7C8A62')
    gi = append('LA_GateGiant'); move(gi, (-20, 150, 0))
    g = append('LA_GateOfOaths'); move(g, (-30, 6, 0)); append('LA_GateChains'); move(bpy.data.collections['LA_GateChains'], (-30, 6, 0))
    b = append('LA_WarBeast'); move(b, (16, 6, 0), 20)
    k = person('Hero kid', (-6, -16, 0), rz=10, arms={'L': (-150, 0, -20), 'R': (-140, 0, 20)})
    c = append('LA_LightningArms')
    for sd, lt in (('L', 'A'), ('R', 'C')):
        r = find(c, 'LA_LightningArm_' + sd); la.attach_arm(r, la.cast_arm(k, sd)); la.variant(r, lt)
    wb = append('LA_WristNumbers')
    for sd in ('L', 'R'):
        bd = find(wb, 'LA_WristBand_Kid_' + sd); la.attach_arm(bd, la.cast_arm(k, sd), hide_cast=False)
        la.show(find(wb, 'LA_WristBand_Villain_' + sd), False)
    person('Little sister', (-10.5, -15, 0), rz=-10)
    v = person('Villain', (-16, -14, 0), rz=-20)
    ia = append('LA_IronArms')
    for sd in ('L', 'R'):
        la.attach_arm(find(ia, 'LA_IronArm_Villain_' + sd), la.cast_arm(v, sd))
    cr = append('LA_IronCrown'); la.crown_on(find(cr, 'LA_IronCrown'), v)
    k2 = person('Big kid', (-22, -14, 0), rz=-25)
    sa = append('LA_StoneArms')
    for sd in ('L', 'R'):
        try:
            la.attach_arm(find(sa, 'LA_StoneArm_Kid_' + sd), la.cast_arm(k2, sd))
        except KeyError:
            pass
        la.show(find(sa, 'LA_StoneArm_Villain_' + sd), False)
    cr2 = append('LA_IronCrown'); find(cr2, 'LA_IronCrown').location = (-1, -19, 0)
    sp = append('LA_GroundSplit'); o = find(sp, 'LA_GroundSplit'); o.location = (14, -26, 0)
    sb = append('LA_SparkBurst'); find(sb, 'LA_SparkBurst').location = (-2, -17, 5)
    sk = append('LA_SkyNumber'); find(sk, 'LA_SkyNumber').location = (-20, 150, 142)
    cam = cam_env('6,-120,9', '-6,20,38', 30)
    render(cam, OUT, kind=KIND, sun_el=42, az_off=25, exposure=EXPO if EXPO is not None else -1.05, auto=False)
