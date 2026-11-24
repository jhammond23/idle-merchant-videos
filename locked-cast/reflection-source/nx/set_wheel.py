# The Great Wheel (Loop a, 11-14): a three-storey prize wheel that comes alive. Works on the square server and the land server.
import bmesh
def wipe(*prefixes):
    for o in list(bpy.data.objects):
        if o.name.startswith(prefixes): bpy.data.objects.remove(o, do_unlink=True)
def _nm(name, *a, **k):
    m = bpy.data.materials.get(name)
    return m or mat(name, *a, **k)
WCOLS = {'green': (40, 190, 66), 'blue': (36, 112, 240), 'purple': (150, 62, 226), 'gold': (255, 184, 28), 'black': (8, 7, 12)}
KCOLS = {'green': (150, 20, 30), 'blue': (236, 232, 222), 'purple': (150, 20, 30), 'gold': (255, 184, 28), 'black': (8, 7, 12)}     # the king's wheel: red, white and gold
WSEQ = ['black', 'green', 'blue', 'green', 'purple', 'green', 'blue', 'green', 'green', 'gold', 'green', 'blue', 'green', 'purple', 'green', 'green', 'blue', 'green', 'purple', 'green']
WODDS = {'green': '1 IN 2', 'blue': '1 IN 60', 'purple': '1 IN 900', 'gold': '1 IN 80,000', 'black': '1 IN 10,000,000'}
WGOLD = _nm('whGold', srgb(250, 190, 56), 0.22, metal=1.0)
WGOLDD = _nm('whGoldD', srgb(190, 130, 36), 0.3, metal=1.0)
WWOOD = _nm('whWood', srgb(104, 66, 38), 0.8)
WWOODD = _nm('whWoodD', srgb(70, 44, 26), 0.85)
WRED = _nm('whRed', srgb(214, 30, 36), 0.5, emit=srgb(214, 30, 36), estr=0.2)
WEYE = bpy.data.materials.get('whEye') or emat('whEye', (1.0, 0.86, 0.5), 9.0)
WSTONE = bpy.data.materials.get('whStone') or noise_mat('whStone', srgb(176, 168, 152), srgb(214, 206, 190), scale=0.3, rough=0.85, bump=0.3)
def _wm(c, cols, tag):
    nm = 'wh%s_%s' % (tag, c); m = bpy.data.materials.get(nm)
    if m: return m
    rgb = srgb(*cols[c]); return mat(nm, rgb, 0.22 if c == 'black' else 0.42, emit=rgb, estr=0.0 if c == 'black' else 0.22)
def build_wheel(name, R=17.0, t=1.6, seq=WSEQ, cols=WCOLS, tag='', hub_r=3.0):
    """origin = the hub centre; the disk lies in the local XZ plane and shows slots on both faces (-y and +y). spin turns the slots,
    the hub (eyes + a little balcony on each face) does not turn. slot k sits at angle k/n from the top, toward +x."""
    root = empty(name); spin = empty(name + 'spin', (0, 0, 0), root); n = len(seq); P = {'root': root, 'spin': spin, 'R': R, 't': t, 'n': n, 'seq': seq, 'hub_r': hub_r}
    fcyl(name + 'core', R - 0.7, t, (0, 0, 0), WWOODD, parent=spin, verts=72, rot=(math.pi / 2, 0, 0))
    r0 = hub_r + 0.5; r1 = R - 1.25; yy = t / 2 + 0.03; by = {}
    for k, c in enumerate(seq): by.setdefault(c, []).append(k)
    for c, ks in by.items():
        me = bpy.data.meshes.new(name + 'w' + c); bm = bmesh.new(); sg = 6
        for k in ks:
            a0 = (k - 0.5) / n * math.tau; a1 = (k + 0.5) / n * math.tau
            for sy in (-1, 1):
                A = [a0 + (a1 - a0) * j / sg for j in range(sg + 1)]
                q0 = [bm.verts.new((r0 * math.sin(a), sy * yy, r0 * math.cos(a))) for a in A]; q1 = [bm.verts.new((r1 * math.sin(a), sy * yy, r1 * math.cos(a))) for a in A]
                for j in range(sg):
                    vs = (q0[j], q1[j], q1[j + 1], q0[j + 1]); bm.faces.new(vs if sy > 0 else vs[::-1])
        bm.normal_update(); bm.to_mesh(me); bm.free(); me.materials.append(_wm(c, cols, tag))
        o = bpy.data.objects.new(name + 'w' + c, me); bpy.context.scene.collection.objects.link(o); o.parent = spin
    for k in range(n):
        a = (k + 0.5) / n * math.tau; rm = (r0 + r1) / 2
        fbox(name + 'dv%d' % k, (0.26, t + 0.34, r1 - r0), (math.sin(a) * rm, 0, math.cos(a) * rm), WGOLD, rot=(0, a, 0), parent=spin)
        for sy in (-1, 1): fsphere(name + 'pg%d%d' % (k, sy), 0.46, (math.sin(a) * (R - 0.72), sy * (t / 2 + 0.25), math.cos(a) * (R - 0.72)), WGOLD, parent=spin, seg=10)
    bpy.ops.mesh.primitive_torus_add(major_radius=R - 0.35, minor_radius=0.85, major_segments=72, minor_segments=12)
    rim = bpy.context.active_object; rim.name = name + 'rim'; rim.data.materials.append(WGOLD); rim.parent = spin; rim.location = (0, 0, 0); rim.rotation_euler = (math.pi / 2, 0, 0)
    for p_ in rim.data.polygons: p_.use_smooth = True
    fcyl(name + 'ring', r0 + 0.1, t + 0.5, (0, 0, 0), WGOLDD, parent=spin, verts=40, rot=(math.pi / 2, 0, 0))
    fcyl(name + 'hub', hub_r, t + 5.0, (0, 0, 0), WGOLD, parent=root, verts=40, rot=(math.pi / 2, 0, 0))
    P['eyes'] = []; P['ledge'] = []
    for sy in (-1, 1):
        for x in (-1.08, 1.08):
            e = fsphere(name + 'eye%d%g' % (sy, x), 0.66, (x, sy * (t / 2 + 2.5), 0.3), WEYE, parent=root, seg=16); e.scale = (1.0, 0.22, 1.3); P['eyes'].append(e)
        P['ledge'].append(fbox(name + 'ledge%d' % sy, (3.6, 2.4, 0.3), (0, sy * (t / 2 + 1.4), hub_r + 0.12), WGOLDD, parent=root, bevel=0.06))
        P['ledge'].append(fbox(name + 'rail%d' % sy, (3.6, 0.16, 0.16), (0, sy * (t / 2 + 2.52), hub_r + 1.9), WGOLD, parent=root))
        for x in (-1.72, 1.72): P['ledge'].append(fbox(name + 'post%d%g' % (sy, x), (0.16, 0.16, 1.7), (x, sy * (t / 2 + 2.52), hub_r + 1.1), WGOLD, parent=root))
    return root, P
def wheel_pose(root, P, base, face=0.0, tip=0.0, spin=0.0, eyes=True):
    """the bottom of the rim rests on world point base; tipped 'tip' degrees toward the side it faces (its local -y); spin = how far the slots have turned"""
    s = root.scale.z; R = P['R'] * s; f = math.radians(face); th = math.radians(tip)
    c = Vector(base) + Matrix.Rotation(f, 3, 'Z') @ Vector((0, -math.sin(th) * R, math.cos(th) * R))
    root.location = c; root.rotation_euler = (th, 0, f); P['spin'].rotation_euler = (0, math.radians(spin), 0)
    for e in P['eyes']: e.hide_render = not eyes
    bpy.context.view_layer.update()
def slot_pt(P, k, rf=0.62, side=-1, out=0.3):
    """world point on slot k (0 = the one that starts at the top)"""
    bpy.context.view_layer.update(); a = k / P['n'] * math.tau; r = P['R'] * rf
    return P['spin'].matrix_world @ Vector((math.sin(a) * r, side * (P['t'] / 2 + out), math.cos(a) * r))
def hub_seat(P, side=-1):
    bpy.context.view_layer.update(); return P['root'].matrix_world @ Vector((0, side * (P['t'] / 2 + 1.35), P['hub_r'] + 0.28))
def hub_face(P, side=-1, out=0.0):
    bpy.context.view_layer.update(); return P['root'].matrix_world @ Vector((0, side * (P['t'] / 2 + 2.6 + out), 0.3))
def build_stand(name, R=17.0):
    """the wheel's stand: a round stone step, a mast behind the wheel and the red pointer over its top. origin on the ground."""
    root = empty(name); top = 2.2
    fcyl(name + 'd0', 12.5, 1.1, (0, 0, 0.55), WSTONE, parent=root, verts=48); fcyl(name + 'd1', 10.0, 1.1, (0, 0, 1.65), WSTONE, parent=root, verts=48)
    fcyl(name + 'dg', 10.1, 0.22, (0, 0, 2.12), WGOLDD, parent=root, verts=48); fcyl(name + 'dt', 9.6, 0.26, (0, 0, 2.1), WSTONE, parent=root, verts=48)
    H = 2 * R + 5.0
    fbox(name + 'mast', (2.2, 2.2, H), (0, 4.6, top + H / 2), WWOOD, parent=root, bevel=0.12)
    for sx in (-1, 1):
        fbox(name + 'br%d' % sx, (1.2, 1.2, 15.0), (sx * 4.4, 4.6, top + 5.6), WWOOD, parent=root, rot=(0, math.radians(sx * -38), 0), bevel=0.08)
    fbox(name + 'brb', (1.2, 1.2, 9.0), (0, 7.4, top + 3.4), WWOOD, parent=root, rot=(math.radians(40), 0, 0), bevel=0.08)
    fcyl(name + 'axle', 1.0, 3.6, (0, 2.9, top + 0.3 + R), WGOLDD, parent=root, verts=20, rot=(math.pi / 2, 0, 0))
    fbox(name + 'arm', (1.3, 7.2, 1.3), (0, 1.6, top + H - 0.7), WWOOD, parent=root, bevel=0.1)
    fcyl(name + 'ptr', 1.5, 3.4, (0, -1.5, top + 2 * R + 1.3), WRED, parent=root, verts=4, r2=0.0, rot=(math.pi, 0, math.radians(45))).scale = (1.0, 0.45, 1.0)
    fsphere(name + 'ptk', 0.7, (0, -1.5, top + 2 * R + 3.3), WGOLD, parent=root, seg=12)
    fsphere(name + 'mk', 1.5, (0, 4.6, top + H + 0.9), WGOLD, parent=root, seg=14)
    return root
STAND_TOP = 2.2
wipe('gw', 'gst')
WHEEL, WP = build_wheel('gw'); away(WHEEL)
if 'CASTLE' not in globals():
    WSTAND = build_stand('gst'); away(WSTAND)
    # puppies: what most kids land on
    BEASTS['puppy'] = dict(body=(1.0, 1.5, 0.9), leg=(0.3, 0.55), head=(1.0, 0.95, 0.9), col=((228, 170, 92), (250, 232, 200)), ears='none', tail='stub')
    ODDS['puppy'] = '1 IN 2'
    wipe('pup')
    PUPS = []
    _pe = _nm('pupEar', srgb(120, 72, 38), 0.85); _pr = _nm('pupRed', srgb(206, 36, 40), 0.6); _pk = _nm('pupPink', srgb(246, 130, 150), 0.6); _pc = bpy.data.materials['b_puppyL']  if bpy.data.materials.get('b_puppyL') else None
    for _i in range(12):
        _r, _p = build_beast('pup%d' % _i, 'puppy', 1.0); PUPS.append((_r, _p)); _n = 'pup%d' % _i; _h = _p['head']; _c1 = bpy.data.materials['b_puppyL']
        _o = bpy.data.objects.get(_n + 'ns')
        if _o: bpy.data.objects.remove(_o, do_unlink=True)
        for _x in (-1, 1): fbox(_n + 'ear%d' % _x, (0.2, 0.46, 0.72), (_x * 0.58, -0.22, 0.2), _pe, parent=_h, bevel=0.06, rot=(0, math.radians(_x * 8), 0))
        fbox(_n + 'snt', (0.52, 0.36, 0.36), (0, -0.92, 0.06), _c1, parent=_h, bevel=0.06); fbox(_n + 'nos', (0.22, 0.1, 0.16), (0, -1.12, 0.17), EYEB, parent=_h, bevel=0.03)
        fbox(_n + 'tng', (0.16, 0.06, 0.2), (0, -1.1, -0.13), _pk, parent=_h); fbox(_n + 'pat', (0.36, 0.04, 0.4), (0.27, -0.765, 0.4), _pe, parent=_h)
        fbox(_n + 'col', (1.08, 0.2, 0.98), (0, -0.62, 0.0), _pr, parent=_p['body'], bevel=0.03)
        fbox(_n + 'tl2', (0.16, 0.16, 0.62), (0, 0.05, 0.3), bpy.data.materials['b_puppy'], parent=_p['tail'], rot=(math.radians(-25), 0, 0), bevel=0.04)
        away(_r)
    BEASTW = []; _pi = 0             # the gk guardians with every rabbit swapped for a puppy
    for _r, _p in globals().get('BEASTL_GK', BEASTL):
        if _p['kind'] == 'rabbit' and _pi < len(PUPS): BEASTW.append(PUPS[_pi]); _pi += 1
        else: BEASTW.append((_r, _p))
print('SET WHEEL OK', flush=True)
