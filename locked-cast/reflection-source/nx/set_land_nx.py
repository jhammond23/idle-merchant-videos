# nx land props (both stories), on the Giant Knelt kingdom set: the king, his statue as a boy, the cages of rare pets and the
# king's mountain wheel under its hill (wheel story); the hall of mirrors, the lake and the lake king (reflection story).
wipe('nking', 'nkg', 'kstat', 'cage', 'cgb', 'kwh', 'khill', 'mirr', 'mrw', 'wking', 'wkcrown', 'lk2')
for _m in [m for m in bpy.data.materials if m.name.startswith(('nking', 'kstat', 'mrw', 'wking'))]: bpy.data.materials.remove(_m)
def hide_tree(o, hide=True):
    for x in [o] + list(o.children_recursive): x.hide_render = hide; x.hide_viewport = hide
for _g in OLDG: hide_tree(_g['root']); hide_tree(_g['sw'])
for _g in OLDG2: hide_tree(_g['root']); hide_tree(_g['sw'])
hide_tree(STAT)
# ---------------- the king ----------------
REDK = bpy.data.materials.get('nkRed') or mat('nkRed', srgb(120, 18, 28), 0.8)
FURK = bpy.data.materials.get('nkFur') or mat('nkFur', srgb(246, 242, 232), 0.95)
KING, KP = person('nking', (150, 22, 34), (96, 16, 28), 'hero_slick_back', 'face_bold', skin=(214, 160, 122), beard='face_full_beard')
fbox('nkgCape', (2.7, 0.22, 3.7), (0, 0.66, 2.3), REDK, parent=KING, bevel=0.06)
fbox('nkgFur', (2.6, 1.5, 0.5), (0, 0.05, 4.02), FURK, parent=KING, bevel=0.16)
fbox('nkgBelt', (2.06, 1.06, 0.26), (0, 0, 2.2), GOLDR, parent=KING)
fbox('nkgChain', (0.7, 0.1, 0.7), (0, -0.53, 3.3), GOLDR, parent=KING, rot=(0, math.radians(45), 0))
for _k in 'LR': fbox('nkgCuff' + _k, (1.06, 1.06, 0.3), (0, 0, -1.2), GOLDR, parent=KP['arm' + _k])
KCROWN = build_crown_r('nkgcrown'); crown_put(KCROWN, KP); away(KING)
# ---------------- his statue as a boy, beside the empty plinth ----------------
def solid_person(name, hair, m, scale=1.0):
    """a person() all in one material (statues), hair as real meshes"""
    r, p = person(name, (200, 200, 200), (200, 200, 200), hair, 'face_calm')
    for o in list(r.children_recursive):
        if o.type == 'MESH': o.data.materials.clear(); o.data.materials.append(m)
    bpy.context.view_layer.update()
    for inst in [o for o in p['head'].children if o.instance_type == 'COLLECTION']:
        for o in inst.instance_collection.all_objects:
            if o.type != 'MESH': continue
            c = o.copy(); c.data = o.data.copy(); bpy.context.scene.collection.objects.link(c); c.name = name + 'hair_' + o.name
            c.data.materials.clear(); c.data.materials.append(m); c.parent = p['head']; c.matrix_parent_inverse = Matrix.Identity(4)
            c.matrix_basis = inst.matrix_basis @ o.matrix_world
        inst.hide_render = True; inst.hide_viewport = True
    r.scale = (scale,) * 3; return r, p
KST, KSTP = solid_person('kstat', 'hero_slick_back', stoneM, 1.25)
fcyl('kstatcrown', 0.62, 0.3, (0, 0, 0.78), stoneM, parent=KSTP['head'], verts=20)
KST.parent = PLINTHS; KST.location = (-4.2, 0, 3.25); KST.rotation_euler = (0, 0, 0)
# ---------------- wheel story: a ring of cages, a rare pet bowing in each ----------------
BEASTS.update({
    'snowlion': dict(body=(1.9, 3.8, 1.9), leg=(0.62, 1.9), head=(1.6, 1.7, 1.5), col=((244, 242, 236), (255, 255, 255)), ears='round', tail='tuft', mane=(250, 196, 60)),
    'nightwolf': dict(body=(1.5, 3.2, 1.5), leg=(0.46, 1.6), head=(1.3, 1.6, 1.2), col=((44, 44, 62), (120, 150, 250)), ears='point', tail='wolf'),
    'goldbear': dict(body=(2.4, 3.6, 2.3), leg=(0.8, 1.5), head=(1.7, 1.6, 1.5), col=((236, 176, 50), (255, 226, 130)), ears='round', tail='stub'),
    'bluefox': dict(body=(1.0, 2.2, 1.0), leg=(0.3, 0.9), head=(0.95, 1.1, 0.85), col=((70, 150, 240), (240, 248, 255)), ears='point', tail='bush'),
    'rosegoat': dict(body=(1.3, 2.4, 1.3), leg=(0.36, 1.4), head=(0.8, 1.2, 0.9), col=((244, 150, 190), (255, 236, 244)), ears='flop', tail='stub', horns=True),
    'firelion': dict(body=(1.9, 3.8, 1.9), leg=(0.62, 1.9), head=(1.6, 1.7, 1.5), col=((60, 40, 40), (120, 90, 80)), ears='round', tail='tuft', mane=(240, 70, 30)),
    'icebear': dict(body=(2.4, 3.6, 2.3), leg=(0.8, 1.5), head=(1.7, 1.6, 1.5), col=((240, 246, 252), (200, 226, 250)), ears='round', tail='stub'),
    'violetwolf': dict(body=(1.5, 3.2, 1.5), leg=(0.46, 1.6), head=(1.3, 1.6, 1.2), col=((140, 70, 220), (226, 200, 255)), ears='point', tail='wolf')})
CGK = ['snowlion', 'nightwolf', 'goldbear', 'bluefox', 'firelion', 'icebear', 'violetwolf', 'rosegoat', 'snowlion', 'goldbear', 'nightwolf']
CGS = {'snowlion': 3.5, 'firelion': 3.5, 'nightwolf': 4.0, 'violetwolf': 4.0, 'goldbear': 3.4, 'icebear': 3.4, 'bluefox': 5.6, 'rosegoat': 5.0}
CAGEM = bpy.data.materials.get('cageIron') or mat('cageIron', srgb(52, 54, 66), 0.35, metal=0.9)
CW, CD, CH = 21.0, 19.0, 21.0       # a cage: width, depth, height
def _cage_mesh(name):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    def bar(x, y):
        r = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.36, radius2=0.36, depth=CH)
        bmesh.ops.translate(bm, verts=r['verts'], vec=(x, y, CH / 2 + 0.8))
    def roofbar(x):
        r = bmesh.ops.create_cone(bm, cap_ends=True, segments=8, radius1=0.36, radius2=0.36, depth=CD)
        bmesh.ops.rotate(bm, verts=r['verts'], cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, 'X'))
        bmesh.ops.translate(bm, verts=r['verts'], vec=(x, 0, CH + 0.9))
    n = 8
    for k in range(n + 1):
        x = -CW / 2 + CW * k / n
        bar(x, -CD / 2); bar(x, CD / 2)
        if 0 < k < n and k % 2 == 0: roofbar(x)
    for k in range(1, 7):
        y = -CD / 2 + CD * k / 7
        bar(-CW / 2, y); bar(CW / 2, y)
    bm.to_mesh(me); bm.free(); me.materials.append(GOLDR)
    for p_ in me.polygons: p_.use_smooth = True
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); return o
CAGES = []
for _j, _g in enumerate(OLDG):
    _r = empty('cage%d' % _j); _r.parent = CASTLE; _r.location = (_g['x'], _g['y'], 0); _r.rotation_euler = (0, 0, math.radians(_g['face']))
    _b = _cage_mesh('cagebars%d' % _j); _b.parent = _r
    fbox('cagefl%d' % _j, (CW + 1.6, CD + 1.6, 0.8), (0, 0, 0.4), CAGEM, parent=_r, bevel=0.15)
    for _sy in (-1, 1): fbox('cagetf%d%d' % (_j, _sy), (CW + 1.4, 1.1, 1.1), (0, _sy * CD / 2, CH + 0.9), GOLDR, parent=_r, bevel=0.2)
    for _sx in (-1, 1): fbox('cagets%d%d' % (_j, _sx), (1.1, CD + 1.4, 1.1), (_sx * CW / 2, 0, CH + 0.9), GOLDR, parent=_r, bevel=0.2)
    fbox('cagelock%d' % _j, (1.7, 0.6, 2.1), (0, -CD / 2 - 0.5, 8.0), CAGEM, parent=_r, bevel=0.12)
    _kind = CGK[_j % len(CGK)]; _br, _bp = build_beast('cgb%d' % _j, _kind, CGS[_kind])
    _br.parent = _r; _br.location = (0, 1.0, 0.8); _br.rotation_euler = (0, 0, 0)
    CAGES.append(dict(root=_r, beast=_br, P=_bp, kind=_kind, tag=_g['tag'], s=CGS[_kind]))
def beast_bow(c, deep=0.0):
    """a deep bow: chest and chin down on its folded front legs, rump in the air (deep 0..1 = lower still)"""
    P = c['P']; bpose(P, 'stand'); body = P['body']; lh, bh = P['lh'], P['bh']; B = BEASTS[c['kind']]; bl = B['body'][1]
    a = 30 + 8 * deep
    body.rotation_euler = (math.radians(a), 0, 0); body.location.z = lh * 0.45 + bh / 2 + math.sin(math.radians(a)) * bl * 0.12
    for i, lp in enumerate(P['legs']): lp.rotation_euler = (math.radians(-88 - a if i < 2 else -a), 0, 0)
    P['head'].rotation_euler = (math.radians(26 + 14 * deep - a * 0.3), 0, 0)
def cages_on(on=True, deep=0.0):
    for c in CAGES:
        hide_tree(c['root'], not on)
        if on: beast_bow(c, deep)
    bpy.context.view_layer.update()
# ---------------- wheel story: the king's wheel, as big as a mountain, asleep under a hill behind the castle ----------------
KS = 46.0
KW, KWP = build_wheel('kwh', cols=KCOLS, tag='k'); KW.scale = (KS,) * 3
KWR = 17.0 * KS; KWC = (CA[0], CA[1] + 470.0); HILL_TOP = 510.0
HILLM = bpy.data.objects['terrain'].data.materials[0]
KHILL = empty('khill', (KWC[0], KWC[1], CAZ + HILL_TOP - KWR))
def _cap():
    me = bpy.data.meshes.new('khillcap'); bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=40, radius=1.0)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < 0.18], context='VERTS')
    rr_ = random.Random(3)
    for v in bm.verts:
        k = 1.0 + 0.012 * math.sin(v.co.x * 9.0) + 0.01 * math.cos(v.co.z * 13.0 + v.co.x * 5.0)
        v.co.x *= (KWR + 14) * k; v.co.z *= (KWR + 14) * k; v.co.y *= 205.0
    bm.normal_update(); bm.to_mesh(me); bm.free(); me.materials.append(HILLM)
    for p_ in me.polygons: p_.use_smooth = True
    o = bpy.data.objects.new('khillcap', me); bpy.context.scene.collection.objects.link(o); o.parent = KHILL; return o
KCAP = _cap()
_rh = random.Random(8); KTREES = []
for _k in range(70):
    _a = _rh.uniform(-0.62, 0.62); _y = _rh.uniform(-0.75, 0.75)
    _rr = (KWR + 14) * math.sqrt(max(0.05, 1 - _y * _y))
    _o = glb(_rh.choice(['pine_a', 'oak_b', 'pine_a_slender', 'maple_red']), (0, 0, 0), rot=_rh.uniform(0, 360), scale=_rh.uniform(1.3, 2.2)); _o.name = 'khilltree%d' % _k
    _o.parent = KHILL; _o.location = (math.sin(_a) * _rr, _y * 205.0, math.cos(_a) * _rr - 3.0); _o.rotation_euler = (0, _a, 0); KTREES.append(_o)
def kwheel(mode='hill', roll=0.0, rise=0.0, spin=0.0, face=0.0):
    """off / hill (only the green hill behind the castle) / roll (the hill turning, lifting: roll degrees, rise units) / up (the wheel standing on the plain)"""
    hide_tree(KW, mode in ('off', 'hill')); hide_tree(KHILL, mode in ('off', 'up'))
    if mode == 'up':
        wheel_pose(KW, KWP, (KWC[0], KWC[1], CAZ - 6.0), face, 0.0, spin, True)
    else:
        hz = CAZ + HILL_TOP - KWR + rise
        KW.location = (KWC[0], KWC[1], hz); KW.rotation_euler = (0, 0, math.radians(face)); KWP['spin'].rotation_euler = (0, math.radians(spin + roll), 0)
        KHILL.location = (KWC[0], KWC[1], hz); KHILL.rotation_euler = (0, math.radians(roll), math.radians(face))
        for e in KWP['eyes']: e.hide_render = (mode != 'roll')
    bpy.context.view_layer.update()
kwheel('off')
# ---------------- reflection story: the hall of mirrors, a kneeling reflection locked in each ----------------
MIRG = bpy.data.materials.get('mirrGlass')
if not MIRG:
    MIRG = bpy.data.materials.new('mirrGlass'); MIRG.use_nodes = True; _b = MIRG.node_tree.nodes['Principled BSDF']
    _b.inputs['Base Color'].default_value = (*srgb(214, 236, 255), 1); _b.inputs['Roughness'].default_value = 0.04; _b.inputs['Alpha'].default_value = 0.22
    _b.inputs['Emission Color'].default_value = (*srgb(200, 230, 255), 1); _b.inputs['Emission Strength'].default_value = 0.25
MIRB = bpy.data.materials.get('mirrBack') or mat('mirrBack', srgb(26, 70, 150), 0.3, emit=srgb(30, 90, 190), estr=0.5)
MW_, MH_, MD_ = 20.0, 31.0, 15.0     # a mirror: width, height, depth of the glass box
MS_ = 4.4                            # the size of the reflection inside it
MIRRORS = []
_MH = ['hero_crop', 'hero_long_straight', 'hero_pixie', 'hero_slick_back']
_MF = ['face_calm', 'face_bold', 'face_bright', 'face_cool']
for _j, _g in enumerate(OLDG):
    _r = empty('mirr%d' % _j); _r.parent = CASTLE; _r.location = (_g['x'], _g['y'], 0); _r.rotation_euler = (0, 0, math.radians(_g['face']))
    fbox('mirrbase%d' % _j, (MW_ + 5, MD_ + 5, 1.6), (0, 0, 0.8), GOLDR, parent=_r, bevel=0.3)
    fbox('mirrback%d' % _j, (MW_, 0.6, MH_), (0, MD_ / 2, 1.6 + MH_ / 2), MIRB, parent=_r)
    fbox('mirrglass%d' % _j, (MW_, 0.3, MH_), (0, -MD_ / 2, 1.6 + MH_ / 2), MIRG, parent=_r)
    for _sx in (-1, 1): fbox('mirrside%d%d' % (_j, _sx), (1.7, MD_ + 1.6, MH_ + 0.4), (_sx * (MW_ / 2 + 0.85), 0, 1.6 + MH_ / 2), GOLDR, parent=_r, bevel=0.3)
    fbox('mirrtop%d' % _j, (MW_ + 5, MD_ + 2.4, 2.0), (0, 0, 1.6 + MH_ + 1.0), GOLDR, parent=_r, bevel=0.4)
    fcyl('mirrarch%d' % _j, 5.2, MD_ + 1.2, (0, 0, 1.6 + MH_ + 2.0), GOLDR, parent=_r, verts=28, rot=(math.pi / 2, 0, 0))
    fsphere('mirrgem%d' % _j, 1.5, (0, -MD_ / 2 - 0.5, 1.6 + MH_ + 3.6), GEMR, parent=_r, seg=12)
    _wr, _wp = water_person('mrw%d' % _j, _MH[_j % 4], _MF[(_j * 3) % 4]); _wr.parent = _r; _wr.scale = (MS_,) * 3
    MIRRORS.append(dict(root=_r, fig=_wr, P=_wp, tag=_g['tag']))
def fig_kneel(m, deep=0.0):
    r, P = m['fig'], m['P']; rest(P); lean = 14 + 30 * deep; bow = 28 + 22 * deep
    r.location = (0, -0.5, 1.6 - 1.5 * MS_ + 0.2); r.rotation_euler = (math.radians(lean), 0, 0)
    leg(P, 'L', 90 - lean * 0.2); leg(P, 'R', 90 - lean * 0.2); look_head(P, pitch=bow); arm(P, 'L', fwd=-26 - 20 * deep, out=6); arm(P, 'R', fwd=-26 - 20 * deep, out=-6)
def mirrors_on(on=True, deep=0.0):
    for m in MIRRORS:
        hide_tree(m['root'], not on)
        if on:
            fig_kneel(m, deep)
            for o in m['P']['head'].children:
                if o.instance_type == 'COLLECTION': o.hide_render = True
    bpy.context.view_layer.update()
# ---------------- reflection story: the lake at the foot of the castle's mountain, and the king's reflection: all of it ----------------
LK2C = (CA[0], CA[1] - 640.0); LK2A = (560.0, 330.0); LK2Z = 15.0
def in_lk2(x, y, k=1.0): return ((x - LK2C[0]) / (LK2A[0] * k)) ** 2 + ((y - LK2C[1]) / (LK2A[1] * k)) ** 2 < 1.0
_T = bpy.data.objects['terrain']
if 'LK2_Z0' not in globals(): LK2_Z0 = {v.index: v.co.z for v in _T.data.vertices if in_lk2(v.co.x, v.co.y, 1.5)}
LK2_HIDE = [o for o in bpy.data.objects if o.instance_type == 'COLLECTION' and o.parent is None and in_lk2(o.matrix_world.translation.x, o.matrix_world.translation.y, 1.12)]
def _ell2(name, k, z, m, seg=96):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    vs = [bm.verts.new((LK2C[0] + math.cos(j / seg * math.tau) * LK2A[0] * k, LK2C[1] + math.sin(j / seg * math.tau) * LK2A[1] * k, z)) for j in range(seg)]
    bm.faces.new(vs); bm.normal_update(); bm.to_mesh(me); bm.free(); me.materials.append(m)
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); return o
LAKE2M = bpy.data.materials.get('lake2M')
if not LAKE2M:
    LAKE2M = bpy.data.materials.new('lake2M'); LAKE2M.use_nodes = True; _b = LAKE2M.node_tree.nodes['Principled BSDF']
    _b.inputs['Base Color'].default_value = (*srgb(24, 104, 190), 1); _b.inputs['Roughness'].default_value = 0.05; _b.inputs['Metallic'].default_value = 0.1
    _b.inputs['Emission Color'].default_value = (*srgb(24, 104, 190), 1); _b.inputs['Emission Strength'].default_value = 0.25
    _tc = LAKE2M.node_tree.nodes.new('ShaderNodeTexCoord'); _nz = LAKE2M.node_tree.nodes.new('ShaderNodeTexNoise'); _nz.inputs['Scale'].default_value = 0.02; _nz.inputs['Detail'].default_value = 2.0
    _bp = LAKE2M.node_tree.nodes.new('ShaderNodeBump'); _bp.inputs['Strength'].default_value = 0.1; _bp.inputs['Distance'].default_value = 6.0
    LAKE2M.node_tree.links.new(_tc.outputs['Object'], _nz.inputs['Vector']); LAKE2M.node_tree.links.new(_nz.outputs[0], _bp.inputs['Height']); LAKE2M.node_tree.links.new(_bp.outputs['Normal'], _b.inputs['Normal'])
BEDM = bpy.data.materials.get('lake2Bed') or noise_mat('lake2Bed', srgb(120, 104, 80), srgb(150, 132, 100), scale=0.02, rough=0.6, bump=0.3)
LK2W = _ell2('lk2water', 1.0, LK2Z, LAKE2M)
def lake2(on=True, water=True):
    """carve the lake into the plain (and raise a bank where the land was lower than the water); water=False = the lake has stood up, only the wet bed is left"""
    me = _T.data
    for i, z0 in LK2_Z0.items():
        v = me.vertices[i]
        if not on: v.co.z = z0; continue
        q = math.sqrt(((v.co.x - LK2C[0]) / LK2A[0]) ** 2 + ((v.co.y - LK2C[1]) / LK2A[1]) ** 2)
        if q < 1.0: v.co.z = min(z0, LK2Z - 3.0 - 26.0 * min(1.0, (1.0 - q) * 2.5))
        else: v.co.z = max(z0, LK2Z + 3.0 * min(1.0, (1.5 - q) * 4.0))
    me.update()
    LK2W.hide_render = not (on and water); LK2W.hide_viewport = LK2W.hide_render
    for o in LK2_HIDE: o.hide_render = on
lake2(False)
WKS = 205.0
WKING, WKP = water_person('wking', 'hero_slick_back', 'face_bold', beard='face_full_beard'); WKING.scale = (WKS,) * 3
WKCROWN = build_crown_r('wkcrown'); crown_put(WKCROWN, WKP)
fbox('wkingCape', (2.7, 0.22, 3.7), (0, 0.66, 2.3), WM['legs'], parent=WKING, bevel=0.06)
fbox('wkingFur', (2.6, 1.5, 0.5), (0, 0.05, 4.02), WM['skin'], parent=WKING, bevel=0.16)
WKAT = (CA[0], CA[1] - 430.0)
def wking(mode='off', sink=0.0, lean=10.0, head=(24, 0), face=180.0, arms=10):
    """the king's reflection: off / up (standing in the drained lake, looking down at the courtyard; sink = fraction still under the bed)"""
    hide_tree(WKING, mode == 'off')
    for o in WKP['head'].children:
        if o.instance_type == 'COLLECTION': o.hide_render = True
    if mode == 'off': return
    rest(WKP); WKING.location = (WKAT[0], WKAT[1], LK2Z - 20.0 - sink * 5.2 * WKS); WKING.rotation_euler = (math.radians(lean), 0, math.radians(face))
    look_head(WKP, pitch=head[0], yaw=head[1]); arm(WKP, 'L', fwd=0, out=arms); arm(WKP, 'R', fwd=0, out=-arms); set_face('wking', 'face_bold'); bpy.context.view_layer.update()
wking('off')
def land_mode(story):
    """which story's props are on the set"""
    cages_on(story == 'wheel'); mirrors_on(story == 'refl'); lake2(story == 'refl'); wking('off'); kwheel('hill' if story == 'wheel' else 'off')
land_mode('off')
print('SET LAND NX OK', len(CAGES), len(MIRRORS), len(LK2_HIDE), flush=True)
