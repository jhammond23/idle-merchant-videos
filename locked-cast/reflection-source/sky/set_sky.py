# The Hole in the Sky: the shared set (town square under a round hole in the noon sky). exec'd by scenes_sky.py
exec(open('/tmp/claude-0/tv/oc/base.py').read())
OUT = '/tmp/claude-0/tv/sky/' + ('st/' if Q == 'final' else 'st_test/'); os.makedirs(OUT, exist_ok=True)
from town import build_town
build_town()
random.seed(41)
HX, HY, HZ, HR = 0.0, -8.0, 160.0, 30.0          # the hole: center and radius
# ---------------- light ----------------
CPN = dict(haze=(1.0, 0.8, 0.6), haze_amt=0.3, mist_start=60, mist_depth=700, glare_thresh=0.85)     # noon gold
CPW = dict(haze=(0.75, 0.8, 0.9), haze_amt=0.32, mist_start=50, mist_depth=600, glare_thresh=0.9)    # waiting, cooler
CPD = dict(haze=(0.25, 0.3, 0.42), haze_amt=0.42, mist_start=40, mist_depth=500, glare_thresh=0.8)   # covered, dark
CPE = dict(haze=(0.9, 0.6, 0.25), haze_amt=0.4, mist_start=30, mist_depth=420, glare_thresh=0.7)     # the eye
def _nodisc(s):
    if hasattr(s, 'sun_disc'): s.sun_disc = False
    return s
def light_noon(rot=210, key=4.2, gold=1.0):
    """high warm sun from behind the subject (rim), cool fill, gold glow pouring from the hole"""
    clear_lights(); LIGHTS.clear(); _nodisc(sky(sun_el=38, sun_rot=rot - 180, strength=0.28))
    sun(38, rot, key, (1.0, 0.8, 0.58)); fill_sun('coolfill', 30, rot + 180, 0.35, (0.5, 0.62, 1.0))
    if gold: mylight('holeL', (HX, HY, HZ - 30), (1.0, 0.72, 0.3), 2.2e6 * gold, 25)
def light_wait(rot=210):
    clear_lights(); LIGHTS.clear(); _nodisc(sky(sun_el=34, sun_rot=rot - 180, strength=0.2))
    sun(34, rot, 2.6, (0.95, 0.85, 0.75)); fill_sun('coolfill', 30, rot + 180, 0.4, (0.5, 0.62, 1.0))
def light_dark(rot=210, k=1.0):
    """the hole covered: the sun dims like an eclipse, cold and hard"""
    clear_lights(); LIGHTS.clear(); _nodisc(sky(sun_el=30, sun_rot=rot - 180, strength=0.07 * k))
    sun(30, rot, 1.1 * k, (0.75, 0.82, 1.0)); fill_sun('coolfill', 40, rot + 180, 0.25, (0.45, 0.55, 1.0))
def light_eye(rot=210, e=1.0):
    """the eye open: a gold searchlight from the hole, the rest of the town cold"""
    light_dark(rot, 0.8)
    mylight('eyeL', (HX, HY, HZ - 40), (1.0, 0.66, 0.24), 4.0e6 * e, 30)
# ---------------- the hole: stars, the cover, the eye (one shader on a disc) ----------------
HOLEP = dict(stars=1.0, cover=0.0, eye=0.0, look=(0.0, 0.0))
exec(open('/tmp/claude-0/tv/sky/hole_shader.py').read())
HOLEM = hole_mat()
def _disc(name, r, z, m, verts=96):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_circle(bm, cap_ends=True, radius=r, segments=verts); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); o.data.materials.append(m); return o
HOLE = _disc('hole', 1.06, 0, HOLEM); HOLE.location = (HX, HY, HZ); HOLE.scale = (HR, HR, HR); HOLE.rotation_euler = (math.pi, 0, 0)
HOLE.visible_shadow = False
# the rim: a soft warm halo just outside the edge (no hard ring), so it reads as a hole torn in the sky
def halo_mat(col, strength):
    m = bpy.data.materials.new('haloM'); m.use_nodes = True; nt = m.node_tree; N = nt.nodes; Lk = nt.links.new
    for n in list(N): N.remove(n)
    out = N.new('ShaderNodeOutputMaterial'); tc = N.new('ShaderNodeTexCoord'); sep = N.new('ShaderNodeSeparateXYZ'); Lk(tc.outputs['Object'], sep.inputs[0])
    def M(op, a, b=None):
        n = N.new('ShaderNodeMath'); n.operation = op
        for k, x in enumerate((a, b)):
            if x is None: continue
            if isinstance(x, (int, float)): n.inputs[k].default_value = x
            else: Lk(x, n.inputs[k])
        return n.outputs[0]
    r = M('SQRT', M('ADD', M('MULTIPLY', sep.outputs[0], sep.outputs[0]), M('MULTIPLY', sep.outputs[1], sep.outputs[1])))
    f = M('POWER', M('MAXIMUM', M('SUBTRACT', 1.0, M('DIVIDE', M('SUBTRACT', r, 1.0), 0.32)), 0.0), 2.2)
    f = M('MULTIPLY', f, M('GREATER_THAN', r, 0.995))
    nz = N.new('ShaderNodeTexNoise'); nz.inputs['Scale'].default_value = 6.0; nz.inputs['Detail'].default_value = 6.0; Lk(tc.outputs['Object'], nz.inputs['Vector'])
    f = M('MULTIPLY', f, M('ADD', 0.35, M('MULTIPLY', nz.outputs['Fac'], 1.1)))
    sv = N.new('ShaderNodeValue'); sv.name = 'str'; sv.outputs[0].default_value = strength
    em = N.new('ShaderNodeEmission'); em.inputs['Color'].default_value = (*col, 1); Lk(M('MULTIPLY', f, sv.outputs[0]), em.inputs['Strength'])
    tr = N.new('ShaderNodeBsdfTransparent'); ad = N.new('ShaderNodeAddShader'); Lk(em.outputs[0], ad.inputs[0]); Lk(tr.outputs[0], ad.inputs[1])
    Lk(ad.outputs[0], out.inputs[0]); m.blend_method = 'BLEND' if hasattr(m, 'blend_method') else None
    return m
RIMM = halo_mat((1.0, 0.8, 0.5), 3.0)
RIM = _disc('rim', 1.34, 0, RIMM); RIM.location = (HX, HY, HZ - 0.3); RIM.scale = (HR, HR, HR); RIM.visible_shadow = False
def set_halo(v): RIMM.node_tree.nodes['str'].outputs[0].default_value = v
def hole(stars=None, cover=None, eye=None, look=None, rim=None, scales=None):
    nt = HOLEM.node_tree.nodes
    if scales is not None: nt['scl'].outputs[0].default_value = scales
    if stars is not None: nt['stars'].outputs[0].default_value = stars
    if cover is not None: nt['cover'].outputs[0].default_value = cover
    if eye is not None: nt['eye'].outputs[0].default_value = eye
    if look is not None: nt['lookx'].outputs[0].default_value = look[0]; nt['looky'].outputs[0].default_value = look[1]
    if rim is not None: set_halo(rim)
hole(1.0, 0.0, 0.0, (0, 0), 3.0, 1.0)
# ---------------- gold coins: one mesh per rain (fast) ----------------
def coin_rain(name, cx, cy, rad, z0, z1, n, seed=1, r=0.32, m=None):
    rr = random.Random(seed); me = bpy.data.meshes.new(name); bm = bmesh.new()
    for i in range(n):
        a = rr.random() * math.tau; d = rad * math.sqrt(rr.random())
        p = Vector((cx + math.cos(a) * d, cy + math.sin(a) * d, rr.uniform(z0, z1)))
        rot = Euler((rr.uniform(0, math.tau), rr.uniform(0, math.tau), 0)).to_matrix().to_4x4()
        geom = bmesh.ops.create_cone(bm, cap_ends=True, segments=10, radius1=r, radius2=r, depth=0.07)
        bmesh.ops.transform(bm, matrix=Matrix.Translation(p) @ rot, verts=geom['verts'])
    bm.to_mesh(me); bm.free(); o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o)
    o.data.materials.append(m or goldE); return o
GOLDC = mat('goldcoin', srgb(250, 196, 70), 0.18, metal=1.0, emit=(1.0, 0.72, 0.25), estr=0.35)
RAIN = coin_rain('rain', HX, HY, 26, 2, 150, 2400, 3, 0.36, GOLDC)
RAIN_NEAR = coin_rain('rainnear', HX, HY, 26, 0.5, 24, 900, 5, 0.3, GOLDC)
def rain(on):
    RAIN.hide_render = not on; RAIN_NEAR.hide_render = not on
# ---------------- props ----------------
def inst_col(key, glbname):
    """import a game model once into its own collection; place copies as instances (fast)"""
    if key in bpy.data.collections: return bpy.data.collections[key]
    before = set(bpy.data.objects); glb(glbname, (0, 0, 0))
    new = [o for o in bpy.data.objects if o not in before]
    col = bpy.data.collections.new(key)
    for o in new:
        for c in o.users_collection: c.objects.unlink(o)
        col.objects.link(o)
    return col
def place_inst(name, col, loc, rz=0, s=1.0, rx=0, ry=0):
    o = bpy.data.objects.new(name, None); o.instance_type = 'COLLECTION'; o.instance_collection = col
    bpy.context.scene.collection.objects.link(o); o.location = loc; o.rotation_euler = (math.radians(rx), math.radians(ry), math.radians(rz)); o.scale = (s, s, s); return o
wicker = noise_mat('wicker', srgb(150, 104, 56), srgb(196, 150, 92), scale=3.5, rough=0.85, bump=0.8)
def basket(name, loc, parent=None, full=0.6, r=0.85, rot=(0, 0, 0)):
    o = fcyl(name, r, 0.85, loc, wicker, parent=parent, verts=20, r2=r * 1.18, rot=rot)
    fcyl(name + 'in', r * 0.98, 0.82, (0, 0, 0.06), mat('wickerin', srgb(70, 46, 24), 0.9), parent=o, verts=20, r2=r * 1.15)
    if full > 0:
        p = fsphere(name + 'gold', r * 1.02, (0, 0, 0.42 * full), GOLDC, parent=o, seg=16); p.scale = (1, 1, 0.32)
    return o
# ---------------- the cast ----------------
GREY_HAIR = None
def grey_hair(key='hero_low_bun', col=(212, 212, 218)):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=HAIRDIR + key + '/' + key + '_hair.glb')
    new = [o for o in bpy.data.objects if o not in before]
    c = bpy.data.collections.new('H_grey_' + key); gm = mat('greyhair', srgb(*col), 0.6)
    for o in new:
        for cc in o.users_collection: cc.objects.unlink(o)
        if o.type == 'MESH' and o.name.startswith('Icosphere'): bpy.data.objects.remove(o); continue
        c.objects.link(o)
        if o.type == 'MESH': o.data.materials.clear(); o.data.materials.append(gm)
    return c
KID, KIDP = person('kid', (58, 104, 176), (92, 72, 52), 'hero_medium_tousle', 'face_bright', skin=(236, 190, 150))
KID.scale = (0.78, 0.78, 0.78)
GRAN, GRANP = person('gran', (112, 58, 104), (66, 56, 66), 'hero_pixie', 'face_calm', skin=(232, 190, 162))
for o in bpy.data.objects:
    if o.parent == GRANP['head'] and o.instance_type == 'COLLECTION': o.instance_collection = grey_hair('hero_low_bun'); o.scale = (0.92, 0.92, 0.92)
shawl = mat('shawl', srgb(150, 52, 70), 0.9)
fbox('granshawl', (2.3, 1.25, 0.9), (0, 0, 3.75), shawl, parent=GRAN, bevel=0.2)
fbox('granapron', (1.7, 0.1, 1.9), (0, -0.55, 2.4), mat('apron', srgb(236, 230, 214), 0.8), parent=GRAN, bevel=0.03)
glassM = mat('glassrim', srgb(60, 44, 30), 0.4, metal=0.6)
for sx in (-1, 1):
    g = bpy.data.objects.new('granglass%d' % sx, None); bpy.context.scene.collection.objects.link(g); g.parent = GRANP['head']
    bpy.ops.mesh.primitive_torus_add(major_radius=0.17, minor_radius=0.025, location=(0, 0, 0))
    t = bpy.context.active_object; t.parent = GRANP['head']; t.location = (sx * 0.2, -0.62, 0.08); t.rotation_euler = (math.pi / 2, 0, 0); t.data.materials.append(glassM)
fbox('granbridge', (0.14, 0.03, 0.03), (0, -0.62, 0.12), glassM, parent=GRANP['head'])
CROWD = []
def crowd_ring(n, seed=5):
    rr = random.Random(seed); out = []
    for i in range(n):
        r, p = person('cw%d' % i, SHIRTS[i % 8], PANTS[i % 4], [h for h in HAIRS if h != 'hero_low_bun'][i % 8], FACES[(i * 4) % 9], skin=SKINS[(i * 3) % 8])
        out.append((r, p))
    return out
CROWD = crowd_ring(26)
CB = {}
def arms_up(p, spread=14, fwd=172):
    arm(p, 'L', fwd=fwd, out=-spread); arm(p, 'R', fwd=fwd, out=spread)
def crowd_pose(mode='baskets', seed=2, center=(HX, HY), skip=None, full=0.6, look_up=True):
    """mode: baskets (holding baskets overhead), look (heads up, baskets low), bow (heads down)"""
    rr = random.Random(seed)
    for i, (r, p) in enumerate(CROWD):
        a = i / len(CROWD) * math.tau + rr.uniform(-0.1, 0.1); d = rr.uniform(9, 27)
        loc = (center[0] + math.cos(a) * d, center[1] + math.sin(a) * d, 0)
        if skip and math.hypot(loc[0] - skip[0], loc[1] - skip[1]) < skip[2]: away(r); continue
        place(r, loc, face_at=(center[0] + rr.uniform(-6, 6), center[1] + rr.uniform(-6, 6)))
        rest(p)
        b = CB.get(i) or basket('cb%d' % i, (0, 0, 0), full=full); CB[i] = b; b.parent = r
        if mode == 'baskets':
            arms_up(p); b.location = (0, -0.25, 6.05); b.rotation_euler = (0, 0, 0)
            look_head(p, pitch=-28 if look_up else 0)
        elif mode == 'look':
            arm(p, 'L', fwd=-40, out=-8); arm(p, 'R', fwd=-40, out=8); b.location = (0, -1.5, 2.2); look_head(p, pitch=-32)
        elif mode == 'bow':
            arm(p, 'L', fwd=-25); arm(p, 'R', fwd=-25); b.location = (0, -1.3, 2.4); look_head(p, pitch=24)
def crowd_faces(face_list, seed=1):
    rr = random.Random(seed)
    for i, (r, p) in enumerate(CROWD): set_face('cw%d' % i, rr.choice(face_list))
# ---------------- Grandma's tea stall (right under the hole) ----------------
STX, STY, STR = 7.0, -14.0, 0.0       # stall center, it faces -y (toward the square's south side)
stwood = noise_mat('stwood', srgb(110, 72, 42), srgb(150, 104, 62), scale=0.8, rough=0.8, bump=0.3)
stripe = bpy.data.materials.new('awning'); stripe.use_nodes = True
_nt = stripe.node_tree; _b = _nt.nodes['Principled BSDF']; _w = _nt.nodes.new('ShaderNodeTexWave'); _w.inputs['Scale'].default_value = 2.2; _w.wave_profile = 'SAW'
_r = _nt.nodes.new('ShaderNodeValToRGB'); _e = _r.color_ramp.elements; _r.color_ramp.interpolation = 'CONSTANT'
_e[0].position = 0.0; _e[0].color = (0.62, 0.08, 0.1, 1); _e[1].position = 0.5; _e[1].color = (0.92, 0.86, 0.72, 1)
_nt.links.new(_w.outputs['Fac'], _r.inputs[0]); _nt.links.new(_r.outputs[0], _b.inputs['Base Color']); _b.inputs['Roughness'].default_value = 0.85
ST = empty('stall', (STX, STY, 0))
fbox('stcounter', (7.0, 2.4, 3.0), (0, 0, 1.5), stwood, parent=ST, bevel=0.08)
fbox('sttop', (7.4, 2.8, 0.22), (0, 0, 3.08), mat('sttopm', srgb(160, 118, 76), 0.6), parent=ST, bevel=0.05)
for x in (-3.4, 3.4):
    for y in (-1.2, 2.8): fbox('stpost%.0f%.0f' % (x, y), (0.3, 0.3, 7.8), (x, y, 3.9), stwood, parent=ST)
aw = fbox('stawning', (8.2, 5.0, 0.18), (0, 0.6, 7.9), stripe, parent=ST, rot=(math.radians(-12), 0, 0))
fbox('stshelf', (6.6, 0.8, 0.15), (0, 2.6, 4.8), stwood, parent=ST)
jarM = mat('jar', srgb(170, 210, 200), 0.1, alpha=0.6, trans=0.6)
for k in range(7): fcyl('stjar%d' % k, 0.3, 0.7, (-2.7 + k * 0.9, 2.6, 5.25), jarM, parent=ST, verts=14)
signM = mat('signboard', srgb(70, 44, 26), 0.8)
fbox('stsign', (3.4, 0.2, 1.1), (0, -1.3, 7.1), signM, parent=ST, bevel=0.05)
_t = flat_text('TEA', 0.95, mat('signink', srgb(240, 214, 140), 0.5, emit=(1, 0.85, 0.5), estr=0.4), (STX, STY - 1.42, 7.1)) if 'flat_text' in dir() else None
ceram = mat('ceramic', srgb(52, 92, 150), 0.25); cupM = mat('cupwhite', srgb(240, 236, 226), 0.3); rimG = mat('cuprim', srgb(230, 180, 70), 0.3, metal=1.0)
TPOT = fsphere('teapot', 0.55, (STX - 1.8, STY - 0.2, 3.62), ceram, seg=20); TPOT.scale = (1, 1, 0.82)
fcyl('tpspout', 0.09, 0.8, (-0.62, 0, 0.1), ceram, parent=TPOT, verts=10, rot=(0, math.radians(-55), 0))
bpy.ops.mesh.primitive_torus_add(major_radius=0.3, minor_radius=0.06, location=(0, 0, 0)); _h = bpy.context.active_object
_h.parent = TPOT; _h.location = (0.58, 0, 0.05); _h.rotation_euler = (math.pi / 2, 0, 0); _h.data.materials.append(ceram)
fsphere('tplid', 0.12, (0, 0, 0.55), ceram, parent=TPOT, seg=10)
CUPS = []
def teacup(name, loc, parent=None, tea=True):
    c = fcyl(name, 0.24, 0.3, loc, cupM, parent=parent, verts=18, r2=0.3)
    fcyl(name + 'rim', 0.305, 0.03, (0, 0, 0.15), rimG, parent=c, verts=18)
    if tea: fcyl(name + 'tea', 0.27, 0.02, (0, 0, 0.1), mat('tea', srgb(150, 76, 28), 0.05), parent=c, verts=18)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.1, minor_radius=0.03, location=(0, 0, 0)); h = bpy.context.active_object
    h.parent = c; h.location = (0.3, 0, 0.0); h.rotation_euler = (math.pi / 2, 0, 0); h.data.materials.append(cupM)
    return c
for k in range(3): CUPS.append(teacup('cup%d' % k, (STX - 0.6 + k * 0.6, STY - 0.75, 3.34)))
lemM = mat('lemon', srgb(246, 214, 52), 0.45); lemIn = mat('lemonin', srgb(250, 240, 170), 0.3, emit=(1, 0.95, 0.6), estr=0.05)
BOARD = fbox('board', (1.6, 1.0, 0.12), (STX + 1.6, STY - 0.3, 3.25), mat('boardw', srgb(190, 150, 100), 0.7), bevel=0.03)
for k in range(4):
    l = fsphere('lemon%d' % k, 0.24, (STX + 2.9 + (k % 2) * 0.35, STY + 0.2 + (k // 2) * 0.35, 3.42), lemM, seg=14); l.scale = (1, 1.3, 1)
HALF = []
for k in range(2):
    h = fsphere('lemhalf%d' % k, 0.24, (STX + 1.3 + k * 0.55, STY - 0.35, 3.33), lemM, seg=14); h.scale = (1, 1.3, 0.5)
    fcyl('lemface%d' % k, 0.235, 0.02, (0, 0, 0.0), lemIn, parent=h, verts=16).scale = (1, 1, 1)
    HALF.append(h)
# the old knife that hums: dark old steel, a faint pale-gold edge, runes
bladeM = mat('blade', srgb(120, 124, 132), 0.25, metal=1.0)
edgeM = mat('bladeedge', srgb(255, 236, 190), 0.2, metal=0.5, emit=(1.0, 0.86, 0.55), estr=1.2)
runeM = mat('runes', srgb(255, 210, 120), 0.3, emit=(1.0, 0.78, 0.38), estr=3.0)
KNIFE = empty('knife', (STX + 1.7, STY - 0.35, 3.34))
fbox('khandle', (0.9, 0.2, 0.16), (-0.75, 0, 0), mat('khand', srgb(80, 50, 30), 0.7), parent=KNIFE, bevel=0.05)
fbox('kguard', (0.08, 0.36, 0.2), (-0.28, 0, 0), brassM, parent=KNIFE, bevel=0.02)
kb = fbox('kblade', (1.25, 0.26, 0.04), (0.38, 0, 0), bladeM, parent=KNIFE, bevel=0.01)
fbox('kedge', (1.22, 0.035, 0.045), (0.38, -0.13, 0), edgeM, parent=KNIFE)
for k in range(5): fbox('krune%d' % k, (0.06, 0.1, 0.05), (0.0 + k * 0.17, 0.03, 0.0), runeM, parent=KNIFE)
KNIFE.rotation_euler = (0, 0, math.radians(-20))
def knife_glow(v):
    set_glow(runeM, 3.0 * v); set_glow(edgeM, 1.2 * v)
place(GRAN, (STX, STY + 1.6, 0), face_at=(STX, STY - 20))
place(KID, (STX - 6.5, STY - 3.0, 0), face_at=(STX, STY))
# ---------------- clock tower (the warmth spire with a clock) ----------------
CTX, CTY = -30.0, 56.0
SPIRE = place_inst('clocktower', inst_col('C_spire', 'a1_warmth_spire'), (CTX, CTY, 0), rz=0, s=1.15)
def img_mat(name, path, rough=0.7, emit=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    t = nt.nodes.new('ShaderNodeTexImage'); t.image = bpy.data.images.load(path); nt.links.new(t.outputs['Color'], b.inputs['Base Color'])
    b.inputs['Roughness'].default_value = rough
    if emit: nt.links.new(t.outputs['Color'], b.inputs['Emission Color']); b.inputs['Emission Strength'].default_value = emit
    return m
_cdir = Vector((HX - CTX, HY - CTY, 0)).normalized(); _crz = math.atan2(_cdir.x, -_cdir.y)
CLOCK = empty('clock', (CTX + _cdir.x * 6.9, CTY + _cdir.y * 6.9, 30.5)); CLOCK.rotation_euler = (0, 0, _crz)
cf = fcyl('clockface', 3.4, 0.3, (0, 0, 0), img_mat('clockm', '/tmp/claude-0/tv/sky/clockface.png', 0.5, 0.15), parent=CLOCK, verts=48, rot=(math.pi / 2, 0, 0))
for o in [cf]:
    me = o.data
    if not me.uv_layers: me.uv_layers.new()
    for poly in me.polygons:
        for li in poly.loop_indices:
            v = me.vertices[me.loops[li].vertex_index].co; me.uv_layers.active.data[li].uv = (v.x / 6.8 + 0.5, v.y / 6.8 + 0.5)
fcyl('clockrim', 3.7, 0.45, (0, 0.08, 0), brassM, parent=CLOCK, verts=48, rot=(math.pi / 2, 0, 0))
handM = mat('hands', srgb(30, 22, 16), 0.5)
HANDS = [empty('hmin', (0, -0.32, 0), parent=CLOCK), empty('hhour', (0, -0.36, 0), parent=CLOCK)]
fbox('hminb', (0.22, 0.06, 2.9), (0, 0, 1.3), handM, parent=HANDS[0]); fbox('hhourb', (0.32, 0.06, 1.9), (0, 0, 0.85), handM, parent=HANDS[1])
def clock(h=12, mnt=0):
    HANDS[0].rotation_euler = (0, math.radians(mnt / 60 * 360), 0); HANDS[1].rotation_euler = (0, math.radians((h % 12 + mnt / 60) / 12 * 360), 0)
clock(12, 0)
# ---------------- the tally wall: two hundred years of gold days ----------------
TW = fbox('tallywall', (16, 1.6, 7), (-26, -2, 3.5), img_mat('tallym', '/tmp/claude-0/tv/sky/tally.png', 0.9), bevel=0.2)
TW.rotation_euler = (0, 0, math.radians(70))
me = TW.data; me.uv_layers.new()
for poly in me.polygons:
    for li in poly.loop_indices:
        v = me.vertices[me.loops[li].vertex_index].co; me.uv_layers.active.data[li].uv = (v.x / 16 + 0.5, v.z / 7 + 0.5)
# ---------------- ladders, kites, the forty-wagon tower, ropes ----------------
ladW = noise_mat('ladw', srgb(150, 110, 64), srgb(184, 140, 86), scale=0.8, rough=0.8, bump=0.3)
def ladder(name, base, h, w=1.6, tilt=0.0, rung=0.9):
    root = empty(name, base); root.rotation_euler = (math.radians(tilt), 0, 0)
    for sx in (-1, 1): fbox(name + 'r%d' % sx, (0.22, 0.22, h), (sx * w / 2, 0, h / 2), ladW, parent=root)
    for k in range(int(h / rung)): fcyl(name + 'g%d' % k, 0.07, w, (0, 0, 0.5 + k * rung), ladW, parent=root, verts=8, rot=(0, math.pi / 2, 0))
    return root
LADDERS = [ladder('lad%d' % k, (-17 + k * 0.4, 8, k * 11.5), 12.0, tilt=(k % 2) * 3 - 1.5) for k in range(7)]
ropeM2 = mat('rope2', srgb(170, 136, 84), 0.9)
KITE_COLS = [(220, 60, 50), (60, 120, 220), (240, 190, 50), (70, 170, 90), (180, 70, 170)]
KITES = []
def kite(name, loc, col, s=3.0, rz=0):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    vs = [bm.verts.new(v) for v in ((0, 0, 1.3 * s), (0.8 * s, 0, 0.15 * s), (0, 0, -1.6 * s), (-0.8 * s, 0, 0.15 * s))]
    bm.faces.new(vs); bm.to_mesh(me); bm.free()
    o = bpy.data.objects.new(name, me); bpy.context.scene.collection.objects.link(o); o.location = loc; o.rotation_euler = (math.radians(-35), 0, math.radians(rz))
    o.data.materials.append(mat(name + 'm', srgb(*col), 0.7)); return o
for k in range(5):
    a = k / 5 * math.tau + 0.4; loc = (HX + math.cos(a) * 26, HY + math.sin(a) * 22, 70 + k * 11)
    kk = kite('kite%d' % k, loc, KITE_COLS[k], 3.2, math.degrees(a) + 90); KITES.append(kk)
    g = (HX + math.cos(a) * 34, HY + math.sin(a) * 30, 1.0)
    rope_curve([g, ((g[0] + loc[0]) / 2, (g[1] + loc[1]) / 2, loc[2] * 0.42), (loc[0], loc[1], loc[2] - 4.5 * 1)], ropeM2, 0.06)
    for j in range(5): fbox('kt%d_%d' % (k, j), (0.5, 0.06, 0.25), (loc[0], loc[1], loc[2] - 7 - j * 1.6), mat('kbow%d' % ((k + j) % 5), srgb(*KITE_COLS[(k + j) % 5]), 0.7))
CART = inst_col('C_cart', 'a1_wreck_cart')
WAGONS = []
rrw = random.Random(9); z = 0.0
for k in range(40):
    s = 0.62; o = place_inst('wag%d' % k, CART, (24 + rrw.uniform(-0.7, 0.7) + 0.05 * k, 14 + rrw.uniform(-0.7, 0.7), z), rz=rrw.uniform(0, 360), s=s, rx=rrw.uniform(-4, 4), ry=rrw.uniform(-4, 4))
    WAGONS.append(o); z += 7.1 * s * 0.72
WAGTOP = z
CLIMBER, CLIMBP = person('climber', (200, 90, 70), (60, 60, 90), 'hero_crop', 'face_bold')
place(CLIMBER, (24 + 2.0, 14, WAGTOP), face_at=(24, 0)); arm(CLIMBP, 'R', fwd=175, out=10); arm(CLIMBP, 'L', fwd=-30, out=-20); look_head(CLIMBP, pitch=-35)
def show_group(objs, on):
    for o in objs:
        o.hide_render = not on
        for c in o.children_recursive: c.hide_render = not on
# ---------------- small set pieces: the cut rope, the teacup, a cloud, a lid ----------------
ROPEX, ROPEY = -10.0, -34.0
ropeTw = noise_mat('ropetw', srgb(160, 124, 74), srgb(196, 160, 104), scale=6.0, rough=0.9, bump=0.9)
ROPE_END = fcyl('ropeend', 0.32, 3.0, (ROPEX, ROPEY, 0.34), ropeTw, verts=24, rot=(0, math.pi / 2, math.radians(20)))
cutM = mat('ropecut', srgb(236, 214, 170), 0.6, emit=(1.0, 0.7, 0.3), estr=0.6)
_cut = fcyl('ropecutface', 0.3, 0.02, (0, 0, 1.5), cutM, parent=ROPE_END, verts=24)
COIL = [ (ROPEX - 1.5 + math.cos(a) * (1.4 + 0.12 * k), ROPEY + 1.0 + math.sin(a) * (1.2 + 0.1 * k), 0.3 + 0.05 * k) for k, a in enumerate([i * 0.55 for i in range(26)]) ]
rope_curve(COIL, ropeTw, 0.3)
FALLROPE = rope_curve([(ROPEX + 6, ROPEY + 4, 95), (ROPEX + 5, ROPEY + 3, 70), (ROPEX + 3.5, ROPEY + 4, 48), (ROPEX + 4.5, ROPEY + 2, 30), (ROPEX + 2, ROPEY + 3, 16), (ROPEX + 3, ROPEY + 1.5, 6)], ropeTw, 0.3)
FALLROPE.hide_render = True
FCUP = teacup('fallcup', (0, 0, 0)); FCUP.location = (900, 900, -100)
SPILL = []
for k in range(9):
    o = fsphere('spill%d' % k, 0.035 + 0.02 * (k % 3), (900, 900, -100), mat('teaspill', srgb(196, 112, 40), 0.03, alpha=0.8, trans=0.7), seg=10); SPILL.append(o)
SHARDS = []
for k in range(7):
    o = fbox('shard%d' % k, (0.28 - 0.02 * k, 0.18, 0.05), (900, 900, -100), cupM, bevel=0.01); SHARDS.append(o)
PUDDLE = fcyl('puddle', 0.7, 0.01, (900, 900, -100), mat('puddle', srgb(110, 60, 24), 0.02), verts=24)
def cup_fall(loc, tilt=50):
    FCUP.location = loc; FCUP.rotation_euler = (math.radians(tilt), math.radians(20), 0)
    rr = random.Random(3)
    for k, o in enumerate(SPILL): t = k / len(SPILL); o.location = (loc[0] + 0.12 + t * 0.35 + rr.uniform(-0.04, 0.04), loc[1] + rr.uniform(-0.05, 0.05), loc[2] + 0.15 + t * 0.45 + rr.uniform(-0.04, 0.04))
def cup_shatter(loc):
    FCUP.location = (900, 900, -100); rr = random.Random(5)
    for o in SPILL: o.location = (900, 900, -100)
    for k, o in enumerate(SHARDS):
        a = rr.uniform(0, math.tau); d = rr.uniform(0.2, 1.2)
        o.location = (loc[0] + math.cos(a) * d, loc[1] + math.sin(a) * d, 0.04); o.rotation_euler = (rr.uniform(-0.4, 0.4), rr.uniform(-0.4, 0.4), rr.uniform(0, 6))
    PUDDLE.location = (loc[0], loc[1], 0.012); PUDDLE.scale = (1.3, 0.9, 1)
cloudM = mat('cloud', srgb(250, 250, 252), 0.95)
CLOUD = empty('cloud', (900, 900, -100))
for k in range(9):
    rr = random.Random(k); fsphere('cl%d' % k, rr.uniform(6, 11), (rr.uniform(-18, 18), rr.uniform(-6, 6), rr.uniform(-3, 3)), cloudM, parent=CLOUD, seg=16)
LID = empty('lid', (900, 900, -100))
fcyl('lidplate', HR * 1.15, 3.0, (0, 0, 0), noise_mat('lidw', srgb(120, 80, 46), srgb(156, 108, 64), scale=0.2, rough=0.7, bump=0.4), parent=LID, verts=48)
fsphere('lidknob', 5.0, (0, 0, -3.0), brassM, parent=LID, seg=16)
def coin_obj(name, loc, rot=(70, 0, 20), r=0.32):
    return coin(name, loc, rot=rot, m=GOLDC, r=r)
# ================= v2 fixes (audit of the first test pass, 11-12) =================
GROUND_Z = 0.2      # top of the stone square: props on the ground sit on this
def _smooth(o):
    if o.type == 'MESH':
        for p in o.data.polygons: p.use_smooth = True
# rope with three twisted strands (reads as rope, not a log)
ropeM3 = bpy.data.materials.new('rope3'); ropeM3.use_nodes = True
_nt = ropeM3.node_tree; _b = _nt.nodes['Principled BSDF']; _tc = _nt.nodes.new('ShaderNodeTexCoord')
_wv = _nt.nodes.new('ShaderNodeTexWave'); _wv.wave_type = 'BANDS'; _wv.bands_direction = 'DIAGONAL'; _wv.inputs['Scale'].default_value = 9.0; _wv.inputs['Distortion'].default_value = 2.0
_nt.links.new(_tc.outputs['Object'], _wv.inputs['Vector'])
_cr = _nt.nodes.new('ShaderNodeValToRGB'); _cr.color_ramp.elements[0].color = (0.33, 0.22, 0.11, 1); _cr.color_ramp.elements[1].color = (0.62, 0.48, 0.28, 1)
_nt.links.new(_wv.outputs['Fac'], _cr.inputs[0]); _nt.links.new(_cr.outputs[0], _b.inputs['Base Color']); _b.inputs['Roughness'].default_value = 0.95
_bp = _nt.nodes.new('ShaderNodeBump'); _bp.inputs['Strength'].default_value = 0.6; _nt.links.new(_wv.outputs['Fac'], _bp.inputs['Height']); _nt.links.new(_bp.outputs[0], _b.inputs['Normal'])
def rope3(name, p0, p1, r=0.26, pitch=1.2, m=ropeM3):
    p0 = Vector(p0); p1 = Vector(p1); ax = p1 - p0; L = ax.length; ax.normalize()
    tmp = Vector((0, 0, 1)) if abs(ax.z) < 0.9 else Vector((1, 0, 0))
    u = ax.cross(tmp).normalized(); v = ax.cross(u).normalized()
    root = empty(name, (0, 0, 0)); steps = max(16, int(L / pitch * 24))
    for k in range(3):
        pts = []
        for i in range(steps + 1):
            t = i / steps; ang = t * L / pitch * math.tau + k * math.tau / 3
            pts.append(tuple(p0 + ax * (t * L) + (u * math.cos(ang) + v * math.sin(ang)) * r * 0.5))
        o = rope_curve(pts, m, r * 0.56); o.data.use_fill_caps = True; o.data.bevel_resolution = 4; o.name = name + 's%d' % k; o.parent = root
    return root
for o in [ROPE_END] + list(ROPE_END.children): o.hide_render = True
_rz = GROUND_Z + 0.26; _ra = Vector((math.cos(math.radians(20)), math.sin(math.radians(20)), 0))
ROPE_TIP = Vector((ROPEX, ROPEY, _rz)) + _ra * 1.5
ROPE3 = rope3('ropeend3', Vector((ROPEX, ROPEY, _rz)) - _ra * 1.6, ROPE_TIP, 0.27)
_cutm = mat('ropecut2', srgb(240, 222, 182), 0.55, emit=(1.0, 0.74, 0.36), estr=0.9)
ROPE_CUT = fcyl('ropecut2', 0.275, 0.02, tuple(ROPE_TIP), _cutm, verts=28)
ROPE_CUT.rotation_euler = (0, math.pi / 2, math.radians(20))
for o in bpy.data.objects:
    if o.type == 'CURVE' and o.data.materials and o.data.materials[0] == ropeTw: o.data.materials[0] = ropeM3
# the cup shatter sits on the square, not under it
def cup_shatter(loc):
    FCUP.location = (900, 900, -100); rr = random.Random(5)
    for o in SPILL: o.location = (900, 900, -100)
    for k, o in enumerate(SHARDS):
        a = rr.uniform(0, math.tau); d = rr.uniform(0.25, 1.1)
        o.location = (loc[0] + math.cos(a) * d, loc[1] + math.sin(a) * d, GROUND_Z + 0.04); o.rotation_euler = (rr.uniform(-0.4, 0.4), rr.uniform(-0.4, 0.4), rr.uniform(0, 6))
    PUDDLE.location = (loc[0] + 0.1, loc[1] - 0.1, GROUND_Z + 0.012); PUDDLE.scale = (1.3, 0.9, 1)
# a soft white cloud (edges fade), not green balls
cloudM2 = bpy.data.materials.new('cloud2'); cloudM2.use_nodes = True; _nt = cloudM2.node_tree; _b = _nt.nodes['Principled BSDF']
_b.inputs['Base Color'].default_value = (0.95, 0.95, 0.97, 1); _b.inputs['Roughness'].default_value = 1.0
_b.inputs['Emission Color'].default_value = (1, 1, 1, 1); _b.inputs['Emission Strength'].default_value = 0.7
_lw = _nt.nodes.new('ShaderNodeLayerWeight'); _lw.inputs['Blend'].default_value = 0.45
_tr = _nt.nodes.new('ShaderNodeBsdfTransparent'); _mx = _nt.nodes.new('ShaderNodeMixShader')
_nt.links.new(_lw.outputs['Facing'], _mx.inputs[0]); _nt.links.new(_b.outputs[0], _mx.inputs[1]); _nt.links.new(_tr.outputs[0], _mx.inputs[2])
_nt.links.new(_mx.outputs[0], _nt.nodes['Material Output'].inputs[0])
for o in CLOUD.children: o.data.materials.clear(); o.data.materials.append(cloudM2); _smooth(o)
for k in range(9, 16):
    rr = random.Random(k * 7); o = fsphere('cl%d' % k, rr.uniform(4, 8), (rr.uniform(-20, 20), rr.uniform(-8, 8), rr.uniform(-5, 1)), cloudM2, parent=CLOUD, seg=16); _smooth(o)
# the lid: plank underside with iron bands (seen from below), no knob
for o in LID.children: o.hide_render = True
lidM = bpy.data.materials.new('lid2'); lidM.use_nodes = True; _nt = lidM.node_tree; _b = _nt.nodes['Principled BSDF']; _tc = _nt.nodes.new('ShaderNodeTexCoord')
_wv = _nt.nodes.new('ShaderNodeTexWave'); _wv.wave_type = 'BANDS'; _wv.bands_direction = 'X'; _wv.wave_profile = 'SAW'; _wv.inputs['Scale'].default_value = 0.08; _nt.links.new(_tc.outputs['Object'], _wv.inputs['Vector'])
_nz = _nt.nodes.new('ShaderNodeTexNoise'); _nz.inputs['Scale'].default_value = 0.6; _nz.inputs['Detail'].default_value = 6; _nt.links.new(_tc.outputs['Object'], _nz.inputs['Vector'])
_cr = _nt.nodes.new('ShaderNodeValToRGB'); _e = _cr.color_ramp.elements; _e[0].position = 0.0; _e[0].color = (0.04, 0.02, 0.01, 1); _e[1].position = 0.07; _e[1].color = (0.3, 0.13, 0.05, 1)
_e.new(1.0).color = (0.42, 0.2, 0.08, 1)
_ad = _nt.nodes.new('ShaderNodeMath'); _ad.operation = 'ADD'; _nt.links.new(_wv.outputs['Fac'], _ad.inputs[0]); _ml = _nt.nodes.new('ShaderNodeMath'); _ml.operation = 'MULTIPLY'; _ml.inputs[1].default_value = 0.15
_nt.links.new(_nz.outputs['Fac'], _ml.inputs[0]); _nt.links.new(_ml.outputs[0], _ad.inputs[1])
_nt.links.new(_wv.outputs['Fac'], _cr.inputs[0]); _nt.links.new(_cr.outputs[0], _b.inputs['Base Color']); _b.inputs['Roughness'].default_value = 0.8
_nt.links.new(_cr.outputs[0], _b.inputs['Emission Color']); _b.inputs['Emission Strength'].default_value = 0.9   # reads brown even lit by the green ground
fcyl('lidplate2', HR * 1.12, 2.0, (0, 0, 0), lidM, parent=LID, verts=64)
ironM = mat('lidiron', srgb(48, 46, 46), 0.45, metal=0.8)
bpy.ops.mesh.primitive_torus_add(major_radius=HR * 1.1, minor_radius=1.0, location=(0, 0, 0), major_segments=64); _t = bpy.context.active_object; _t.parent = LID; _t.location = (0, 0, -1.0); _t.data.materials.append(ironM)
for yy in (-9, 9): fbox('lidstrap%d' % yy, (HR * 2.1, 2.2, 0.8), (0, yy, -1.2), ironM, parent=LID)
# the knife: smaller so it fits the board, lying in front of the lemon halves, with real rune glyphs
KNIFE.location = (STX + 1.75, STY - 0.62, 3.33); KNIFE.scale = (0.75, 0.75, 0.75); KNIFE.rotation_euler = (0, 0, math.radians(-8))
for o in list(KNIFE.children):
    if o.name.startswith('krune'): o.hide_render = True
_RUNES = [[(0, 0, 0.13, 90), (0.025, 0.055, 0.06, 35), (0.025, 0.015, 0.06, 35)],
          [(0, 0, 0.13, 90), (-0.022, 0.06, 0.06, 135), (0.022, 0.06, 0.06, 45)],
          [(0, 0, 0.13, 90), (-0.02, 0.072, 0.055, -35), (0.02, 0.072, 0.055, 35)],
          [(0, 0, 0.13, 90), (0.02, 0.048, 0.05, -50), (0.02, 0.012, 0.05, 50)],
          [(-0.022, 0.052, 0.062, 45), (0.022, 0.052, 0.062, -45), (-0.022, 0.008, 0.062, -45), (0.022, 0.008, 0.062, 45)]]
for k, strokes in enumerate(_RUNES):
    x0 = 0.04 + k * 0.17
    for j, (dx, dy, ln, ang) in enumerate(strokes):
        fbox('kglyph%d_%d' % (k, j), (ln, 0.016, 0.05), (x0 + dx, 0.03 + dy - 0.03, 0.0), runeM, parent=KNIFE, rot=(0, 0, math.radians(ang)))
HALF[0].location = (STX + 1.12, STY - 0.12, 3.33); HALF[1].location = (STX + 1.62, STY - 0.05, 3.33)
# coins that bounced onto her counter (she never catches them)
COUNTER_COINS = []
for k, (dx, dy, dz, rot) in enumerate([(-2.6, -0.85, 3.235, (0, 0, 10)), (-0.4, -1.05, 3.235, (0, 0, 40)), (0.6, -0.95, 3.26, (14, 0, 70)), (-2.9, -0.2, 3.235, (0, 0, 0)), (-1.25, -0.95, 3.95, (55, 20, 0)), (2.7, -0.9, 3.235, (0, 0, 15))]):
    COUNTER_COINS.append(coin_obj('ctrcoin%d' % k, (STX + dx, STY + dy, dz), rot=rot, r=0.3))
# ---------------- camera helpers: explicit up vector; hide whatever blocks the view ----------------
def cam_look(loc, at, lens, upv=(0, 0, 1)):
    c = cam_at(loc, at, lens)
    d = (Vector(at) - Vector(loc)).normalized(); x = d.cross(Vector(upv))
    if x.length < 1e-6: x = d.cross(Vector((0, 1, 0)))
    x.normalize(); y = x.cross(d).normalized()
    c.rotation_euler = Matrix((x, y, -d)).transposed().to_euler(); return c
HIDDEN = []
def _root(o):
    while o.parent: o = o.parent
    return o
def _desc(o):
    out = [o]
    for c in o.children: out += _desc(c)
    return out
_INST = []
def _owner(ob, mtx):
    ob = getattr(ob, 'original', ob)
    if ob.name in bpy.context.scene.objects: return _root(ob)
    if not _INST: _INST.extend(o for o in bpy.data.objects if o.instance_type == 'COLLECTION' and o.instance_collection)
    t = (mtx @ ob.matrix_world.inverted()).translation; best = None; bd = 1e9
    for e in _INST:
        if ob.name in e.instance_collection.all_objects:
            d = (e.matrix_world.translation - t).length
            if d < bd: bd, best = d, e
    return _root(best) if best else _root(ob)
HIDEABLE = ('cw', 'oak', 'maple', 'pine', 'birch', 'bush', 'flower_bush', 'hedge', 'a1_town_lamp', 'a1_flower_planter', 'a1_barrel_stack', 'a1_food_crates', 'a1_raised_flower_box', 'a1_food_cart', 'kite', 'kt', 'rope')
def unhide():
    for o, hr, hv in reversed(HIDDEN): o.hide_render = hr; o.hide_viewport = hv
    HIDDEN.clear(); bpy.context.view_layer.update()
def clear_view(at=None, near=None, margin=0.8, grid=(9, 16), keep=(), extra=()):
    """hide crowd, trees, lamps, kites that block the frame closer than 'near' (or than the subject at 'at')"""
    sc = bpy.context.scene; c = sc.camera; bpy.context.view_layer.update()
    org = c.matrix_world.translation.copy()
    if near is None: near = (Vector(at) - org).length - margin
    fr = c.data.view_frame(scene=sc); xs = [v.x for v in fr]; ys = [v.y for v in fr]; z = fr[0].z; Rm = c.matrix_world.to_3x3()
    dg = bpy.context.evaluated_depsgraph_get(); found = set(); pref = HIDEABLE + tuple(extra)
    for i in range(grid[0]):
        for j in range(grid[1]):
            u = min(xs) + (max(xs) - min(xs)) * (i + 0.5) / grid[0]; v = min(ys) + (max(ys) - min(ys)) * (j + 0.5) / grid[1]
            d = (Rm @ Vector((u, v, z))).normalized(); o0 = org.copy(); left = near
            for step in range(12):
                ok, loc, nrm, idx, ob, mtx = sc.ray_cast(dg, o0, d, distance=left)
                if not ok: break
                rt = _owner(ob, mtx)
                if rt.name in keep or not rt.name.startswith(pref): break
                found.add(rt); adv = (loc - o0).length + 0.05; o0 = loc + d * 0.05; left -= adv
                if left <= 0: break
    done = {id(h) for h, _, _ in HIDDEN}
    for r in found:
        for o in _desc(r):
            if id(o) in done: continue
            HIDDEN.append((o, o.hide_render, o.hide_viewport)); o.hide_render = True; o.hide_viewport = True; done.add(id(o))
    bpy.context.view_layer.update()
    return [r.name for r in found]
def crowd_pose(mode='baskets', seed=2, center=(HX, HY), skip=None, full=0.6, look_up=True):
    """mode: baskets (overhead), look (heads up, baskets low), bow (heads down). skip: (x,y,r) or a list of them"""
    rr = random.Random(seed); sk = [] if not skip else ([skip] if isinstance(skip[0], (int, float)) else list(skip))
    for i, (r, p) in enumerate(CROWD):
        a = i / len(CROWD) * math.tau + rr.uniform(-0.1, 0.1); d = rr.uniform(9, 27)
        loc = (center[0] + math.cos(a) * d, center[1] + math.sin(a) * d, 0)
        fa = (center[0] + rr.uniform(-6, 6), center[1] + rr.uniform(-6, 6))
        if any(math.hypot(loc[0] - s[0], loc[1] - s[1]) < s[2] for s in sk): away(r); continue
        place(r, loc, face_at=fa); rest(p)
        b = CB.get(i) or basket('cb%d' % i, (0, 0, 0), full=full); CB[i] = b; b.parent = r
        for ch in b.children:
            if ch.name.endswith('gold'): ch.scale = (1, 1, 0.32 if full > 0 else 0.0001)
        if mode == 'baskets':
            arms_up(p); b.location = (0, -0.25, 6.05); b.rotation_euler = (0, 0, 0); look_head(p, pitch=-28 if look_up else 0)
        elif mode == 'look':
            arm(p, 'L', fwd=-40, out=-8); arm(p, 'R', fwd=-40, out=8); b.location = (0, -1.5, 2.2); b.rotation_euler = (0, 0, 0); look_head(p, pitch=-32)
        elif mode == 'bow':
            arm(p, 'L', fwd=-25); arm(p, 'R', fwd=-25); b.location = (0, -1.3, 2.4); b.rotation_euler = (0, 0, 0); look_head(p, pitch=24)
def crowd_dir(deg, d0=3.5, d1=15.0, z0=3.0, z1=5.0):
    """camera inside the ring looking out along compass angle deg (0=+x, 90=+y): sees faces (everyone faces the hole)"""
    a = math.radians(deg); cx, cy = HX + math.cos(a) * d0, HY + math.sin(a) * d0
    return (cx, cy, z0), (HX + math.cos(a) * d1, HY + math.sin(a) * d1, z1)
exec(open('/tmp/claude-0/tv/sky/look3.py').read())
