# My Reflection Knelt to Me (Loop a, 11-14): water twins, the crowned giant twin, the lake over the north half of the square.
import bmesh
WBLUE = dict(body=(34, 132, 246), legs=(20, 92, 214), hair=(14, 62, 184), skin=(150, 214, 255), lite=(190, 236, 255))
def wmat(name, rgb, estr=0.42, rough=0.07, band=0.5):
    """toon water: a glossy blue with lighter ripples running through it, lit a little from inside"""
    m = bpy.data.materials.get(name)
    if m: return m
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (1.0, 1.0, 2.6); nt.links.new(tc.outputs['Object'], mp.inputs[0])
    nz = nt.nodes.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 2.2; nz.inputs['Detail'].default_value = 2.0; nz.inputs['Distortion'].default_value = 1.6; nt.links.new(mp.outputs[0], nz.inputs['Vector'])
    cr = nt.nodes.new('ShaderNodeValToRGB'); cr.color_ramp.elements[0].position = 0.52; cr.color_ramp.elements[1].position = 0.62
    cr.color_ramp.elements[0].color = (*srgb(*rgb), 1); cr.color_ramp.elements[1].color = tuple(a * (1 - band) + c * band for a, c in zip(srgb(*rgb), srgb(*WBLUE['lite']))) + (1,)
    nt.links.new(nz.outputs[0], cr.inputs[0]); nt.links.new(cr.outputs[0], b.inputs['Base Color']); nt.links.new(cr.outputs[0], b.inputs['Emission Color'])
    b.inputs['Emission Strength'].default_value = estr; b.inputs['Roughness'].default_value = rough
    bp = nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.25; nt.links.new(nz.outputs[0], bp.inputs['Height']); nt.links.new(bp.outputs['Normal'], b.inputs['Normal'])
    return m
WM = {k: wmat('wt_' + k, WBLUE[k]) for k in ('body', 'legs', 'hair', 'skin')}
def water_person(name, hair, face, beard=None):
    """a person made of lake water: same rig as person(), every part in water blues, the face still drawn on"""
    r, p = person(name, WBLUE['body'], WBLUE['legs'], hair, face, skin=WBLUE['skin'], beard=beard)
    for o in list(r.children_recursive):
        if o.type == 'MESH' and o != p['head']:
            k = 'legs' if o.name.startswith(name + 'L') else ('skin' if o.name.startswith(name + 'Hd') else 'body')
            o.data.materials.clear(); o.data.materials.append(WM[k])
    hm = p['head'].data.materials[0]; hb = hm.node_tree.nodes['Principled BSDF']; hb.inputs['Roughness'].default_value = 0.1
    hb.inputs['Emission Color'].default_value = (*srgb(*WBLUE['skin']), 1); hb.inputs['Emission Strength'].default_value = 0.3
    bpy.context.view_layer.update()
    for inst in [o for o in p['head'].children if o.instance_type == 'COLLECTION']:
        for o in inst.instance_collection.all_objects:
            if o.type != 'MESH': continue
            c = o.copy(); c.data = o.data.copy(); bpy.context.scene.collection.objects.link(c); c.name = name + 'hair_' + o.name
            c.data.materials.clear(); c.data.materials.append(WM['hair']); c.parent = p['head']; c.matrix_parent_inverse = Matrix.Identity(4)
            c.matrix_basis = inst.matrix_basis @ o.matrix_world
        inst.hide_render = True; inst.hide_viewport = True
    return r, p
GOLDR = bpy.data.materials.get('rfGold') or mat('rfGold', srgb(252, 196, 56), 0.2, metal=1.0)
GEMR = bpy.data.materials.get('rfGem') or emat('rfGem', (1.0, 0.08, 0.1), 3.0)
REDR = bpy.data.materials.get('rfRedD') or mat('rfRedD', srgb(120, 18, 28), 0.8)
def build_crown_r(name, gold=None, s=1.0):
    gold = gold or GOLDR; r = empty(name); r.scale = (s,) * 3
    fcyl(name + 'b', 0.74, 0.34, (0, 0, 0.17), gold, parent=r, verts=28); fcyl(name + 'i', 0.60, 0.36, (0, 0, 0.17), REDR, parent=r, verts=28)
    for k in range(6):
        a = k / 6 * math.tau
        fcyl(name + 'p%d' % k, 0.17, 0.46, (math.sin(a) * 0.66, -math.cos(a) * 0.66, 0.55), gold, parent=r, verts=4, r2=0.0, rot=(0, 0, a))
        fsphere(name + 'g%d' % k, 0.085, (math.sin(a) * 0.66, -math.cos(a) * 0.66, 0.82), gold, parent=r, seg=8)
    fsphere(name + 'gem', 0.13, (0, -0.76, 0.2), GEMR, parent=r, seg=10)
    return r
def crown_put(c, P, tilt=0.0):
    c.parent = P['head']; c.location = (0, 0.04, 0.62); c.rotation_euler = (math.radians(tilt), 0, 0); c.scale = (1.0,) * 3
def add_palms(name, P):
    """an open hand on each arm (hidden until wanted): a flat palm slab + fingers, pivot at the wrist; local -y = fingertips, +z = palm up"""
    for sd in 'LR':
        pv = empty(name + 'palm' + sd, (0, 0, -1.82), P['arm' + sd]); P['palm' + sd] = pv
        fbox(name + 'pm' + sd, (0.98, 0.9, 0.16), (0, -0.42, 0.0), WM['skin'], parent=pv, bevel=0.04)
        for k in range(4): fbox(name + 'pf%s%d' % (sd, k), (0.2, 0.5, 0.14), (-0.37 + k * 0.245, -1.08, 0.0), WM['skin'], parent=pv, bevel=0.03)
        fbox(name + 'pt' + sd, (0.2, 0.46, 0.14), ((0.6 if sd == 'L' else -0.6), -0.5, 0.0), WM['skin'], parent=pv, bevel=0.03, rot=(0, 0, math.radians(-30 if sd == 'L' else 30)))
        for c in pv.children: c.hide_render = True
def palm_show(P, sd, on=True):
    for c in P['palm' + sd].children: c.hide_render = not on
wipe('twin', 'tcrown', 'wtw', 'wcap', 'lake', 'lk_')
RS = 9.5
TWIN, TWINP = water_person('twin', 'hero_crop', 'face_bright'); TWIN.scale = (RS,) * 3; add_palms('twin', TWINP)
TCROWN = build_crown_r('tcrown'); crown_put(TCROWN, TWINP); away(TWIN)
def tw_reset():
    rest(TWINP); TWIN.rotation_euler = (0, 0, 0); TWIN.scale = (RS,) * 3; set_face('twin', 'face_bright')
    for sd in 'LR': palm_show(TWINP, sd, False); TWINP['palm' + sd].rotation_euler = (0, 0, 0)
def tw_place(at, face=0.0, gz=None, lean=0.0, sink=0.0):
    s = TWIN.scale.z; TWIN.location = (at[0], at[1], (GROUND_Z if gz is None else gz) - sink * s); TWIN.rotation_euler = (math.radians(lean), 0, math.radians(face)); bpy.context.view_layer.update()
def tw_kneel(at, face=0.0, lean=16, bow=30, gz=None, arms=(-28, -28)):
    """on both knees (legs folded back), leaning in, head bowed"""
    tw_reset(); tw_place(at, face, gz, lean, sink=1.5); leg(TWINP, 'L', 90); leg(TWINP, 'R', 90)
    look_head(TWINP, pitch=bow); arm(TWINP, 'L', fwd=arms[0], out=6); arm(TWINP, 'R', fwd=arms[1], out=-6); bpy.context.view_layer.update()
def tw_step(at, face=0.0, lean=44, bow=8, sd='L', gz=None, alpha=None, lift=None):
    """kneeling low with one open hand flat on the ground like a step (or lifted: lift = palm height). Returns the palm centre (world)."""
    tw_kneel(at, face, lean, bow, gz); s = TWIN.scale.z; g = GROUND_Z if gz is None else gz
    sh = TWINP['arm' + sd].matrix_world.translation; L = 1.82 * s
    drop = sh.z - (g + 0.1 * s if lift is None else lift)
    a = math.degrees(math.acos(max(-1.0, min(1.0, drop / L)))) if alpha is None else alpha
    arm(TWINP, sd, fwd=-(a + lean), out=0); TWINP['palm' + sd].rotation_euler = (math.radians(a), 0, 0); palm_show(TWINP, sd, True)
    bpy.context.view_layer.update(); return TWINP['palm' + sd].matrix_world @ Vector((0, -0.5, 0.09))
def tw_stand(at, face=0.0, gz=None, head=(0, 0), stride=0.0, arms=8):
    tw_reset(); tw_place(at, face, gz); leg(TWINP, 'L', stride); leg(TWINP, 'R', -stride)
    arm(TWINP, 'L', fwd=-stride * 0.8, out=arms); arm(TWINP, 'R', fwd=stride * 0.8, out=-arms); look_head(TWINP, pitch=head[0], yaw=head[1]); bpy.context.view_layer.update()
def tw_shoulder(sd='R'):
    """world point on top of a shoulder where the kid sits"""
    bpy.context.view_layer.update(); return TWIN.matrix_world @ Vector((1.5 if sd == 'R' else -1.5, -0.1, 4.02))
# ---- everybody else's reflection: their own size ----
WTW = {}
if 'CASTLE' not in globals():
    for _i in range(3, 17):
        _r, _p = water_person('wtw%d' % _i, HAIRS[(_i * 5) % 9], FACES[(_i * 4) % 9]); WTW[_i] = (_r, _p); away(_r)
    WCAP, WCAPP = water_person('wcap', 'hero_slick_back', 'face_bold', beard='face_full_beard'); away(WCAP)
    # ---- the lake ----
    LAKE_C = (0.0, 262.0); LAKE_A = (258.0, 242.0); LAKE_Z = 0.34
    def in_lake(x, y, k=1.0): return ((x - LAKE_C[0]) / (LAKE_A[0] * k)) ** 2 + ((y - LAKE_C[1]) / (LAKE_A[1] * k)) ** 2 < 1.0
    def shore_y(x): return LAKE_C[1] - LAKE_A[1] * math.sqrt(max(0.0, 1 - ((x - LAKE_C[0]) / LAKE_A[0]) ** 2))
    def _ell(name, k, z, m, seg=128):
        me = bpy.data.meshes.new(name); bm = bmesh.new()
        vs = [bm.verts.new((LAKE_C[0] + math.cos(j / seg * math.tau) * LAKE_A[0] * k, LAKE_C[1] + math.sin(j / seg * math.tau) * LAKE_A[1] * k, z)) for j in range(seg)]
        bm.faces.new(vs); bm.normal_update(); bm.to_mesh(me); bm.free(); me.materials.append(m)
        o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); return o
    LAKEM = bpy.data.materials.get('lakeM')
    if not LAKEM:
        LAKEM = bpy.data.materials.new('lakeM'); LAKEM.use_nodes = True; _b = LAKEM.node_tree.nodes['Principled BSDF']
        _b.inputs['Base Color'].default_value = (*srgb(20, 86, 150), 1); _b.inputs['Roughness'].default_value = 0.05; _b.inputs['Metallic'].default_value = 0.15
        _tc = LAKEM.node_tree.nodes.new('ShaderNodeTexCoord'); _nz = LAKEM.node_tree.nodes.new('ShaderNodeTexNoise'); _nz.inputs['Scale'].default_value = 0.35; _nz.inputs['Detail'].default_value = 2.0
        _bp = LAKEM.node_tree.nodes.new('ShaderNodeBump'); _bp.inputs['Strength'].default_value = 0.06; _bp.inputs['Distance'].default_value = 0.4
        LAKEM.node_tree.links.new(_tc.outputs['Object'], _nz.inputs['Vector']); LAKEM.node_tree.links.new(_nz.outputs[0], _bp.inputs['Height']); LAKEM.node_tree.links.new(_bp.outputs['Normal'], _b.inputs['Normal'])
    SANDM = bpy.data.materials.get('lakeSand') or noise_mat('lakeSand', srgb(214, 196, 150), srgb(236, 222, 180), scale=0.6, rough=0.9, bump=0.2)
    LAKE_OBJS = [_ell('lakewater', 1.0, LAKE_Z, LAKEM), _ell('lakesand', 1.012, LAKE_Z - 0.06, SANDM)]
    _rl = random.Random(21)
    for _k in range(46):      # a tree line on the far shore
        _a = math.radians(_rl.uniform(18, 162)); _kk = _rl.uniform(1.03, 1.12)
        _x = LAKE_C[0] + math.cos(_a) * LAKE_A[0] * _kk; _y = LAKE_C[1] + math.sin(_a) * LAKE_A[1] * _kk
        _o = glb(_rl.choice(['pine_a', 'oak_b', 'pine_a_slender', 'maple_red']), (_x, _y, 0), rot=_rl.uniform(0, 360), scale=_rl.uniform(1.0, 1.6)); _o.name = 'lk_tree%d' % _k; LAKE_OBJS.append(_o)
    bpy.context.view_layer.update()
    _own = set(o.name for o in LAKE_OBJS)
    LAKE_HIDE = []
    for _o in bpy.data.objects:
        if _o.name in _own or _o.name.startswith(('lk_', 'lake', 'clock', 'hmin', 'hhour')): continue
        _w = _o.matrix_world.translation
        if in_lake(_w.x, _w.y, 0.995) and _w.z > -50 and _o.type in ('MESH', 'EMPTY') and abs(_w.z) < 60: LAKE_HIDE.append((_o, _o.hide_render))
    _GROUND = max((o for o in bpy.data.objects if o.type == 'MESH'), key=lambda o: len(o.data.vertices) if o.dimensions.x > 1000 else 0)
    _GZ0 = [(v.index, v.co.z) for v in _GROUND.data.vertices if in_lake(v.co.x, v.co.y, 1.0)]
    _CT0 = (SPIRE.location.copy(), CLOCK.location.copy(), CLOCK.rotation_euler.copy())
    def lake_on(on=True, tower=(-37.0, 6.0)):
        """flood the north half of the square (and hide what would stand in the water), or put the town back"""
        for o in LAKE_OBJS: o.hide_render = not on; o.hide_viewport = not on
        for o, h in LAKE_HIDE:
            try: o.hide_render = True if on else h
            except ReferenceError: pass
        for i, z in _GZ0: _GROUND.data.vertices[i].co.z = -3.0 if on else z
        _GROUND.data.update()
        if on:
            d = Vector((0.0 - tower[0], -12.0 - tower[1], 0)).normalized(); SPIRE.location = (tower[0], tower[1], 0)
            CLOCK.location = (tower[0] + d.x * 6.9, tower[1] + d.y * 6.9, 30.5); CLOCK.rotation_euler = (0, 0, math.atan2(d.x, -d.y))
        else: SPIRE.location, CLOCK.location, CLOCK.rotation_euler = _CT0[0].copy(), _CT0[1].copy(), _CT0[2].copy()
        bpy.context.view_layer.update()
    lake_on(False)
    print('LAKE hide', len(LAKE_HIDE), 'ground', _GROUND.name, len(_GZ0), flush=True)
print('SET REFL OK', flush=True)
