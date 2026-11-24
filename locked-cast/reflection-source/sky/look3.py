# Look v3 (Jake 11-12 21:37Z: "match that visual quality"): bright sunny day, deep blue sky with soft clouds,
# crisp sun with soft-edged shadows, punchy colour, real cobblestones, a fuller town. exec'd at the end of set_sky.py.
LOOK3 = dict(zen=(0.018, 0.10, 0.50), hor=(0.26, 0.50, 0.92), clouds=0.75, amb=(0.46, 0.62, 1.0), amb_str=1.5, skystr=1.0)
def sky3(zen=None, hor=None, clouds=None, amb=None, amb_str=None, skystr=None, seed=3.0):
    """painted gradient sky with soft cumulus for the camera; a soft blue dome for the lighting (so the sky colour never washes the town)"""
    P = dict(LOOK3)
    for k, v in (('zen', zen), ('hor', hor), ('clouds', clouds), ('amb', amb), ('amb_str', amb_str), ('skystr', skystr)):
        if v is not None: P[k] = v
    w = bpy.data.worlds.new('W3'); bpy.context.scene.world = w; w.use_nodes = True
    nt = w.node_tree; N = nt.nodes; L = nt.links; out = N['World Output']
    for n in list(N):
        if n.bl_idname == 'ShaderNodeBackground': N.remove(n)
    tc = N.new('ShaderNodeTexCoord'); sep = N.new('ShaderNodeSeparateXYZ'); L.new(tc.outputs['Generated'], sep.inputs[0])
    mr = N.new('ShaderNodeMapRange'); mr.inputs['From Min'].default_value = 0.0; mr.inputs['From Max'].default_value = 0.7; L.new(sep.outputs['Z'], mr.inputs['Value'])
    pw = N.new('ShaderNodeMath'); pw.operation = 'POWER'; pw.inputs[1].default_value = 0.75; L.new(mr.outputs['Result'], pw.inputs[0])
    ramp = N.new('ShaderNodeValToRGB'); e = ramp.color_ramp.elements
    e[0].position = 0.0; e[0].color = (*P['hor'], 1); e[1].position = 1.0; e[1].color = (*P['zen'], 1)
    L.new(pw.outputs[0], ramp.inputs['Fac'])
    # clouds: noise on the view direction projected onto a flat cloud layer
    zc = N.new('ShaderNodeMath'); zc.operation = 'ADD'; zc.inputs[1].default_value = 0.10; L.new(sep.outputs['Z'], zc.inputs[0])
    dx = N.new('ShaderNodeMath'); dx.operation = 'DIVIDE'; L.new(sep.outputs['X'], dx.inputs[0]); L.new(zc.outputs[0], dx.inputs[1])
    dy = N.new('ShaderNodeMath'); dy.operation = 'DIVIDE'; L.new(sep.outputs['Y'], dy.inputs[0]); L.new(zc.outputs[0], dy.inputs[1])
    cmb = N.new('ShaderNodeCombineXYZ'); L.new(dx.outputs[0], cmb.inputs[0]); L.new(dy.outputs[0], cmb.inputs[1]); cmb.inputs[2].default_value = seed
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 1.15; nz.inputs['Detail'].default_value = 9.0; nz.inputs['Roughness'].default_value = 0.58
    L.new(cmb.outputs[0], nz.inputs['Vector'])
    cr = N.new('ShaderNodeMapRange'); cr.inputs['From Min'].default_value = 0.53; cr.inputs['From Max'].default_value = 0.70; L.new(nz.outputs['Fac'], cr.inputs['Value'])
    hf = N.new('ShaderNodeMapRange'); hf.inputs['From Min'].default_value = 0.02; hf.inputs['From Max'].default_value = 0.22; L.new(sep.outputs['Z'], hf.inputs['Value'])
    cm = N.new('ShaderNodeMath'); cm.operation = 'MULTIPLY'; L.new(cr.outputs['Result'], cm.inputs[0]); L.new(hf.outputs['Result'], cm.inputs[1])
    cm2 = N.new('ShaderNodeMath'); cm2.operation = 'MULTIPLY'; cm2.inputs[1].default_value = P['clouds']; L.new(cm.outputs[0], cm2.inputs[0])
    # cloud colour: bright white tops, a touch of blue-grey in the thick middle
    cc = N.new('ShaderNodeMix'); cc.data_type = 'RGBA'; L.new(nz.outputs['Fac'], cc.inputs['Factor'])
    cc.inputs[6].default_value = (1.0, 1.0, 1.0, 1); cc.inputs[7].default_value = (0.78, 0.84, 0.95, 1)
    mix = N.new('ShaderNodeMix'); mix.data_type = 'RGBA'; L.new(cm2.outputs[0], mix.inputs['Factor']); L.new(ramp.outputs['Color'], mix.inputs[6]); L.new(cc.outputs[2], mix.inputs[7])
    lp = N.new('ShaderNodeLightPath')
    bgc = N.new('ShaderNodeBackground'); L.new(mix.outputs[2], bgc.inputs['Color']); bgc.inputs['Strength'].default_value = P['skystr']
    bga = N.new('ShaderNodeBackground'); bga.inputs['Color'].default_value = (*P['amb'], 1); bga.inputs['Strength'].default_value = P['amb_str']
    mxr = N.new('ShaderNodeMath'); mxr.operation = 'MAXIMUM'; L.new(lp.outputs['Is Camera Ray'], mxr.inputs[0]); L.new(lp.outputs['Is Glossy Ray'], mxr.inputs[1])
    ms = N.new('ShaderNodeMixShader'); L.new(mxr.outputs[0], ms.inputs['Fac']); L.new(bga.outputs[0], ms.inputs[1]); L.new(bgc.outputs[0], ms.inputs[2])
    L.new(ms.outputs[0], out.inputs['Surface'])
    return w
# daytime presets: almost no haze (the reference is crisp), a whisper of blue distance
CPN = dict(haze=(0.55, 0.70, 0.95), haze_amt=0.07, mist_start=90, mist_depth=1200, glare_thresh=0.95)
CPW = dict(haze=(0.55, 0.66, 0.85), haze_amt=0.10, mist_start=80, mist_depth=1000, glare_thresh=0.95)
CPD = dict(haze=(0.16, 0.20, 0.34), haze_amt=0.25, mist_start=50, mist_depth=700, glare_thresh=0.85)
CPE = dict(haze=(0.55, 0.40, 0.22), haze_amt=0.22, mist_start=40, mist_depth=600, glare_thresh=0.75)
SUNF = dict(obj=None, el=52, off=38)       # the day sun follows the camera: always over its shoulder, like the reference
def sun_follow():
    o = SUNF['obj']
    if o is None or o.name not in bpy.data.objects: return
    c = bpy.context.scene.camera; bpy.context.view_layer.update()
    fw = c.matrix_world.to_3x3() @ Vector((0, 0, -1))
    if abs(fw.z) > 0.85: fw = c.matrix_world.to_3x3() @ Vector((0, 1, 0))     # looking straight up: use the frame's top
    yaw = math.degrees(math.atan2(fw.y, fw.x)) + SUNF['off']
    o.rotation_euler = (math.radians(90 - SUNF['el']), 0, math.radians(yaw - 90))
def light_noon(rot=210, key=7.0, gold=1.0, el=52):
    """bright noon: crisp warm-white sun over the camera's shoulder, bright blue sky dome fill, gold glow from the hole"""
    clear_lights(); LIGHTS.clear(); sky3()
    SUNF['obj'] = sun(el, rot, key, (1.0, 0.95, 0.86), angle=2.6); SUNF['el'] = el
    if gold: mylight('holeL', (HX, HY, HZ - 30), (1.0, 0.72, 0.3), 1.6e6 * gold, 25)
def light_wait(rot=210):
    """noon with nothing falling: the same bright day, a little flatter and cooler"""
    clear_lights(); LIGHTS.clear(); sky3(clouds=0.9, zen=(0.03, 0.11, 0.42), hor=(0.30, 0.48, 0.80), amb_str=1.3)
    SUNF['obj'] = sun(48, rot, 5.5, (0.98, 0.95, 0.9), angle=3.0); SUNF['el'] = 48
def light_dark(rot=210, k=1.0):
    """the hole covered: the day dims like an eclipse, cold and hard"""
    clear_lights(); LIGHTS.clear(); SUNF['obj'] = None
    sky3(zen=(0.006 * k, 0.02 * k, 0.09 * k), hor=(0.05 * k, 0.08 * k, 0.2 * k), clouds=0.35, amb=(0.3, 0.38, 0.6), amb_str=0.18 * k, skystr=1.0)
    sun(34, rot, 1.2 * k, (0.75, 0.82, 1.0), angle=1.5); fill_sun('coolfill', 40, rot + 180, 0.22, (0.45, 0.55, 1.0))
def light_eye(rot=210, e=1.0):
    """the eye open: a gold searchlight from the hole, the rest of the town cold"""
    light_dark(rot, 0.8)
    mylight('eyeL', (HX, HY, HZ - 40), (1.0, 0.66, 0.24), 4.0e6 * e, 30)
# ---------------- real cobblestones on the square ----------------
def cobble_mat(name='cobble3', scale=1.45):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; L = nt.links; b = N['Principled BSDF']
    tc = N.new('ShaderNodeTexCoord'); mp = N.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (scale, scale * 1.35, scale)
    L.new(tc.outputs['Object'], mp.inputs['Vector'])
    # wobble the cells so they read as hand-laid stones
    wn = N.new('ShaderNodeTexNoise'); wn.inputs['Scale'].default_value = 3.0; L.new(mp.outputs[0], wn.inputs['Vector'])
    wm = N.new('ShaderNodeVectorMath'); wm.operation = 'MULTIPLY_ADD'; wm.inputs[1].default_value = (0.18, 0.18, 0.0)
    L.new(wn.outputs['Color'], wm.inputs[0]); L.new(mp.outputs[0], wm.inputs[2])
    v1 = N.new('ShaderNodeTexVoronoi'); v1.feature = 'F1'; v1.inputs['Randomness'].default_value = 0.85; L.new(wm.outputs[0], v1.inputs['Vector'])
    v2 = N.new('ShaderNodeTexVoronoi'); v2.feature = 'DISTANCE_TO_EDGE'; v2.inputs['Randomness'].default_value = 0.85; L.new(wm.outputs[0], v2.inputs['Vector'])
    # per-stone colour: greys with warm and cool variation
    cr = N.new('ShaderNodeValToRGB'); e = cr.color_ramp.elements
    e[0].position = 0.0; e[0].color = (0.20, 0.19, 0.18, 1); e[1].position = 1.0; e[1].color = (0.46, 0.42, 0.36, 1)
    el = cr.color_ramp.elements.new(0.5); el.color = (0.30, 0.31, 0.33, 1)
    L.new(v1.outputs['Color'], cr.inputs['Fac'])
    # fine grain on each stone
    gn = N.new('ShaderNodeTexNoise'); gn.inputs['Scale'].default_value = 40.0; gn.inputs['Detail'].default_value = 6; L.new(mp.outputs[0], gn.inputs['Vector'])
    gm = N.new('ShaderNodeMix'); gm.data_type = 'RGBA'; gm.blend_type = 'OVERLAY'; gm.inputs['Factor'].default_value = 0.35
    L.new(cr.outputs['Color'], gm.inputs[6]); L.new(gn.outputs['Color'], gm.inputs[7])
    # mortar between stones
    mm = N.new('ShaderNodeMapRange'); mm.inputs['From Min'].default_value = 0.035; mm.inputs['From Max'].default_value = 0.075; L.new(v2.outputs['Distance'], mm.inputs['Value'])
    mo = N.new('ShaderNodeMix'); mo.data_type = 'RGBA'; L.new(mm.outputs['Result'], mo.inputs['Factor'])
    mo.inputs[6].default_value = (0.11, 0.10, 0.09, 1); L.new(gm.outputs[2], mo.inputs[7])
    L.new(mo.outputs[2], b.inputs['Base Color'])
    # rounded stones: height from the distance to the edge
    hh = N.new('ShaderNodeMapRange'); hh.inputs['From Min'].default_value = 0.0; hh.inputs['From Max'].default_value = 0.22; L.new(v2.outputs['Distance'], hh.inputs['Value'])
    bp = N.new('ShaderNodeBump'); bp.inputs['Strength'].default_value = 0.8; bp.inputs['Distance'].default_value = 0.12
    L.new(hh.outputs['Result'], bp.inputs['Height']); L.new(bp.outputs['Normal'], b.inputs['Normal'])
    rr = N.new('ShaderNodeMapRange'); rr.inputs['To Min'].default_value = 0.92; rr.inputs['To Max'].default_value = 0.62; L.new(hh.outputs['Result'], rr.inputs['Value'])
    L.new(rr.outputs['Result'], b.inputs['Roughness'])
    return m
COBBLE3 = cobble_mat()
for o in bpy.data.objects:
    if o.type == 'MESH' and o.data.materials and any(mm and mm.name.startswith('cobble') and mm.name != 'cobble3' for mm in o.data.materials):
        for i, mm in enumerate(o.data.materials):
            if mm and mm.name.startswith('cobble'): o.data.materials[i] = COBBLE3
# lusher grass
_g = bpy.data.materials.get('grass')
if _g:
    for n in _g.node_tree.nodes:
        if n.bl_idname == 'ShaderNodeValToRGB':
            n.color_ramp.elements[0].color = (*srgb(46, 120, 30), 1); n.color_ramp.elements[1].color = (*srgb(110, 176, 52), 1)
# coins: a little rougher so a coin right at the lens can't flare into a white blob
_gc = bpy.data.materials.get('goldcoin')
if _gc: _gc.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.38
# ---------------- a fuller, lived-in town (the reference has houses, fences and trees right behind its characters) ----------------
EXTRA_HOUSES = [('a1_cottage_thatch', (0, -61), 180), ('a1_cottage_blue', (-26, -58), 150), ('a1_cottage_timber', (26, -58), -150),
                ('a1_cottage_blue', (31, 55), 20), ('a1_cottage_timber', (63, 15), 80), ('a1_cottage_thatch', (-64, 11), -80),
                ('a1_stable_house', (-24, 60), -10)]
for _nm, (_x, _y), _r in EXTRA_HOUSES: glb(_nm, (_x, _y, 0), rot=_r)
picketM = mat('picket', srgb(242, 238, 228), 0.55)
def picket_fence(name, p0, p1, h=1.6, step=0.75):
    """a white picket fence from p0 to p1 (xy), pickets with pointed-ish tops and two rails"""
    a = Vector((p0[0], p0[1], 0)); b = Vector((p1[0], p1[1], 0)); d = b - a; L_ = d.length; ang = math.atan2(d.y, d.x)
    root = empty(name, (a.x, a.y, 0)); root.rotation_euler = (0, 0, ang)
    n = max(2, int(L_ / step))
    for k in range(n + 1):
        x = k * L_ / n
        fbox('%s_p%d' % (name, k), (0.16, 0.08, h), (x, 0, h / 2), picketM, parent=root, bevel=0.02)
        fbox('%s_t%d' % (name, k), (0.12, 0.08, 0.12), (x, 0, h + 0.02), picketM, rot=(0, math.radians(45), 0), parent=root)
    for z in (0.45, h - 0.35): fbox('%s_r%.0f' % (name, z * 10), (L_, 0.06, 0.12), (L_ / 2, -0.07, z), picketM, parent=root)
    return root
for _k, (_p0, _p1) in enumerate([((-8, -53), (8, -53)), ((-33, -50), (-19, -52)), ((19, -52), (33, -50)),
                                 ((24, 47), (38, 49)), ((55, 9), (56, 22)), ((-56, 4), (-57, 18))]):
    picket_fence('fence%d' % _k, _p0, _p1)
random.seed(77)
for _k in range(14):
    _t = random.random() * math.tau; _r = 64 + random.random() * 10
    _x, _y = math.cos(_t) * _r, math.sin(_t) * _r
    if math.hypot(_x - (-30), _y - 56) < 12 or abs(_x) < 14 and _y > 40: continue      # keep the clock tower and the north road clear
    glb(random.choice(['oak_b', 'maple_red', 'birch_a', 'oak_b']), (_x, _y, 0), rot=random.random() * 360, scale=0.85 + random.random() * 0.4)
# ---------------- v3b audit fixes (11-12 22:00Z) ----------------
# 1 falling coins never fill the lens: the rain coins fade out nearer than coin_near() to the camera (big blurred discs covered faces)
GOLDR = GOLDC.copy(); GOLDR.name = 'goldrain'
def _nearfade(m, d0=2.2):
    nt = m.node_tree; N = nt.nodes; L = nt.links; out = N['Material Output']
    src = out.inputs['Surface'].links[0].from_socket
    cd = N.new('ShaderNodeCameraData'); mr = N.new('ShaderNodeMapRange'); mr.name = 'nearfade'
    mr.inputs['From Min'].default_value = d0 * 0.7; mr.inputs['From Max'].default_value = d0
    L.new(cd.outputs['View Distance'], mr.inputs['Value'])
    # and none right in front of the subject's face: coins within coin_subj()'s radius of a point fade too
    gp = N.new('ShaderNodeNewGeometry'); sp = N.new('ShaderNodeCombineXYZ'); sp.name = 'subjp'
    for k, v in enumerate((900.0, 900.0, -100.0)): sp.inputs[k].default_value = v
    vd = N.new('ShaderNodeVectorMath'); vd.operation = 'DISTANCE'; L.new(gp.outputs['Position'], vd.inputs[0]); L.new(sp.outputs[0], vd.inputs[1])
    sr = N.new('ShaderNodeMapRange'); sr.name = 'subjfade'; sr.inputs['From Min'].default_value = 0.6; sr.inputs['From Max'].default_value = 1.0
    L.new(vd.outputs['Value'], sr.inputs['Value'])
    mn = N.new('ShaderNodeMath'); mn.operation = 'MINIMUM'; L.new(mr.outputs['Result'], mn.inputs[0]); L.new(sr.outputs['Result'], mn.inputs[1])
    tr = N.new('ShaderNodeBsdfTransparent'); ms = N.new('ShaderNodeMixShader')
    L.new(mn.outputs[0], ms.inputs['Fac']); L.new(tr.outputs[0], ms.inputs[1]); L.new(src, ms.inputs[2]); L.new(ms.outputs[0], out.inputs['Surface'])
GOLDR.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.42
_nearfade(GOLDR)
# 3 better falling coins: round (24 sides) with a raised rim, so a near coin reads as a real coin, not a flat yellow card
def _coin_mesh(name, cx, cy, rad, z0, z1, n, seed, r, segs=24):
    rr = random.Random(seed); me = bpy.data.meshes.new(name + '3'); bm = bmesh.new()
    for i in range(n):
        a = rr.random() * math.tau; d = rad * math.sqrt(rr.random())
        p = Vector((cx + math.cos(a) * d, cy + math.sin(a) * d, rr.uniform(z0, z1)))
        rot = Euler((rr.uniform(0, math.tau), rr.uniform(0, math.tau), 0)).to_matrix().to_4x4()
        geom = bmesh.ops.create_cone(bm, cap_ends=True, segments=segs, radius1=r, radius2=r, depth=0.075)
        bmesh.ops.transform(bm, matrix=Matrix.Translation(p) @ rot, verts=geom['verts'])
    caps = [f for f in bm.faces if len(f.verts) == segs]
    bmesh.ops.inset_individual(bm, faces=caps, thickness=r * 0.17, depth=-0.016, use_even_offset=True)
    bm.to_mesh(me); bm.free(); return me
for _o, _args in ((RAIN, ('rain', HX, HY, 26, 2, 150, 2400, 3, 0.36)), (RAIN_NEAR, ('rainnear', HX, HY, 26, 0.5, 24, 900, 5, 0.3))):
    _o.data = _coin_mesh(*_args); _o.data.materials.append(GOLDR)
def coin_near(d=2.2):
    mr = GOLDR.node_tree.nodes['nearfade']; mr.inputs['From Min'].default_value = d * 0.7; mr.inputs['From Max'].default_value = d
def coin_subj(p=None, r=1.1):
    """clear falling coins within r of point p (a face in a close-up); None = off"""
    sp = GOLDR.node_tree.nodes['subjp']; q = p if p is not None else (900.0, 900.0, -100.0)
    for k in range(3): sp.inputs[k].default_value = q[k]
    sr = GOLDR.node_tree.nodes['subjfade']; sr.inputs['From Min'].default_value = r * 0.6; sr.inputs['From Max'].default_value = r
# 2 street lamps off at noon (their glowing bulbs read as stray light orbs)
_lampm = set()
for _o in bpy.data.objects:
    if _o.name.startswith('a1_town_lamp'):
        for _d in _desc(_o):
            for _sl in getattr(_d, 'material_slots', []):
                if _sl.material: _lampm.add(_sl.material)
for _e in _INST if _INST else [o for o in bpy.data.objects if o.instance_type == 'COLLECTION' and o.instance_collection and o.name.startswith('a1_town_lamp')]:
    if _e.name.startswith('a1_town_lamp'):
        for _d in _e.instance_collection.all_objects:
            for _sl in getattr(_d, 'material_slots', []):
                if _sl.material: _lampm.add(_sl.material)
for _m in _lampm:
    if not _m.use_nodes: continue
    for _n in _m.node_tree.nodes:
        if _n.type == 'BSDF_PRINCIPLED' and _n.inputs['Emission Strength'].default_value > 0:
            print('LAMP-OFF', _m.name, _n.inputs['Emission Strength'].default_value); _n.inputs['Emission Strength'].default_value = 0.0
        elif _n.type == 'EMISSION':
            print('LAMP-OFF', _m.name, 'emission node'); _n.inputs['Strength'].default_value = 0.0
