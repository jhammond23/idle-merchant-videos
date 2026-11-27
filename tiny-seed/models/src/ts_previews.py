# Tiny Seed preview stills. SHOT=<name> python3 -I ts_previews.py   (writes ../_pv_<name>.png and a labels json)
import os, sys, math, json
HERE = os.path.dirname(os.path.abspath(__file__))
SHOT = os.environ.get('SHOT', 'hero')
W = int(os.environ.get('W', 1080)); H = int(os.environ.get('H', 600)); SPP = int(os.environ.get('SPP', 16))
os.environ['OUT'] = '/tmp/_unused.png'
_src = open('/tmp/claude-0/cast2/cast_v2.py').read()
_src = _src[:_src.index('# hair colours')].replace("MYF = '/tmp/claude-0/cast2/faces/'", "MYF = '/tmp/claude-0/kits/faces/'")
exec(compile(_src, 'cast_v2_prefix', 'exec'))
sys.path.insert(0, '/home/claude/styles/craftee-style/pack'); sys.path.insert(0, HERE)
import bpy, style_craftee_style as tf
from mathutils import Vector, Quaternion, Matrix
from bpy_extras.object_utils import world_to_camera_view
import ts_lib as L
import numpy as np

BLEND = os.path.abspath(os.path.join(HERE, '..', 'tiny-seed-models.blend'))
POSES = json.load(open(os.path.join(HERE, '..', 'poses.json')))
S = bpy.context.scene
LABELS = []


def append(name):
    with bpy.data.libraries.load(BLEND) as (s, d):
        d.collections = [name]
    c = d.collections[0]
    S.collection.children.link(c)
    return c


def find(c, base):
    for o in c.all_objects:
        if o and o.name.split('.')[0] == base:
            return o
    raise KeyError(base)


def move(c, loc, rz=0.0):
    for o in c.all_objects:
        if o.parent is None:
            o.location = Vector(loc) + o.location
            o.rotation_euler.z += math.radians(rz)


def hide_stage(c, prefixes):
    for ch in c.children_recursive:
        if any(ch.name.startswith(p) for p in prefixes):
            for o in ch.objects:
                o.hide_render = True


def pose(arm, pd):
    for bn, v in pd.items():
        pb = arm.pose.bones[bn]
        pb.rotation_mode = 'QUATERNION'
        if 'loc' in v: pb.location = v['loc']
        if 'quat' in v: pb.rotation_quaternion = v['quat']
        if 'scale' in v: pb.scale = v['scale']


def tree(loc, stages='CDE', pose_name=None, rz=0.0, blink=0.0, smile=0.0):
    c = append('TS_Tree')
    hide = [p for k, p in (('A', 'TS_Tree_A'), ('B', 'TS_Tree_B'), ('C', 'TS_Tree_C'), ('D', 'TS_Tree_D'), ('E', 'TS_Tree_E')) if k not in stages]
    hide_stage(c, hide)
    move(c, loc, rz)
    if pose_name:
        pose(find(c, 'TS_Tree_Rig'), POSES['tree'][pose_name])
    kb = find(c, 'TS_Tree_Face').data.shape_keys.key_blocks
    kb['BLINK'].value = blink; kb['SMILE'].value = smile
    return c


def baby(loc, face=0, pose_name=None, rz=0.0):
    c = append('TS_TrollBaby'); move(c, loc, rz)
    find(c, 'TS_TrollBaby_Face')['face'] = face
    if pose_name:
        pose(find(c, 'TS_TrollBaby_Rig'), POSES['troll_baby_poses'][pose_name])
    return c


def mother(loc, face=0, pose_name=None, rz=0.0):
    c = append('TS_TrollMother'); move(c, loc, rz)
    find(c, 'TS_TrollMother_Face')['face'] = face
    if pose_name:
        pose(find(c, 'TS_TrollMother_Rig'), POSES['troll_mother_poses'][pose_name])
    return c


tint_hair('hero_medium_tousle', (104, 62, 30))


def kid(loc, rot=0, face='toybox_happy', arms=(0, 0), out=(6, 4), name='kid'):
    return person(name + str(len(bpy.data.objects)), (207, 61, 19), (52, 62, 92), (248, 179, 131), face, 'hero_medium_tousle', head='classic', fs=1.1,
                  loc=loc, s=0.86, rot=rot, arms=arms, out=out)


def cottage(loc, rz=0.0, w=13.0, d=10.0, wall=8.0, top=14.0, wallhex='#E4E7E2', roofhex='#48546D', name='cottage'):
    mb = L.MB()
    v, f = L.box((w, d, wall), (0, 0, wall / 2), 0.15); mb.add(v, f, 0)
    hw, hd = w / 2 + 0.7, d / 2 + 0.8
    V = [(-hw, -hd, wall - 0.3), (hw, -hd, wall - 0.3), (hw, hd, wall - 0.3), (-hw, hd, wall - 0.3), (-hw, 0, top), (hw, 0, top)]
    F = [[0, 1, 5, 4], [2, 3, 4, 5], [1, 2, 5], [3, 0, 4], [3, 2, 1, 0]]
    mb.add(np.array(V, float), F, 1, flat=True)
    for (x, sx, sz, zc) in ((0, 2.6, 4.6, 2.3),):
        v, f = L.box((sx, 0.3, sz), (x - 2.5, -d / 2 - 0.05, zc), 0.08); mb.add(v, f, 2)
    for x in (2.6,):
        v, f = L.box((2.6, 0.25, 2.6), (x, -d / 2 - 0.05, 4.6), 0.08); mb.add(v, f, 3)
    for x in (-w / 2 + 0.3, w / 2 - 0.3):
        v, f = L.box((0.6, 0.3, wall), (x, -d / 2 - 0.05, wall / 2), 0.05); mb.add(v, f, 2)
    v, f = L.box((w, 0.3, 0.6), (0, -d / 2 - 0.05, wall - 0.6), 0.05); mb.add(v, f, 2)
    o = mb.obj(name, [L.mat('PV_Plaster_' + wallhex[1:], wallhex, 0.9), L.mat('PV_Roof_' + roofhex[1:], roofhex, 0.8), L.mat('PV_Timber', '#8A6B45', 0.85),
                      L.mat('PV_Window', '#5A7FA8', 0.3)], S.collection)
    o.location = loc; o.rotation_euler.z = math.radians(rz)
    return o


def ground(kind='grass', size=6000):
    if kind == 'cobble':
        gm = noise_mat('cobble', srgb(150, 150, 152), srgb(118, 118, 122), scale=0.9, rough=0.9, bump=0.25, voronoi=True)
    else:
        gm = noise_mat('grass', srgb(128, 168, 92), srgb(112, 152, 80), scale=0.05, rough=0.95, bump=0.0)
    bpy.ops.mesh.primitive_plane_add(size=size); g = bpy.context.active_object; g.data.materials.append(gm)
    return g


def soil_disc(loc, r):
    mb = L.MB()
    v, f = L.lathe([(r, -0.05), (r * 0.93, 0.25), (r * 0.6, 0.6), (0.01, 0.75)], 40, cap_top=False)
    for i in range(len(v)):
        a = math.atan2(v[i][1], v[i][0]); v[i][:2] *= 1 + 0.06 * math.sin(5 * a) + 0.04 * math.sin(11 * a + 1)
    mb.add(v, f, 0, fjit=0.1, flat=True)
    o = mb.obj('soil', [L.mat('Soil', '#6A4B35', 0.95)], S.collection); o.location = loc
    return o


def camera_(loc, at, lens, fit='VERTICAL'):
    cd = bpy.data.cameras.new('PV_cam'); cam = bpy.data.objects.new('PV_cam', cd); S.collection.objects.link(cam); S.camera = cam
    cd.lens = lens; cd.sensor_fit = fit; cd.sensor_height = 36; cd.sensor_width = 36; cd.clip_start = 0.05; cd.clip_end = 30000
    cam.location = loc; tf.look_at(cam, Vector(at))
    return cam


def label(text, world, dy=0):
    LABELS.append((text, tuple(world), dy))


def render(cam, sun_el=None, exposure=None, az_off=35.0, target_luma=None):
    tf.apply_look(S, 'day', samples=SPP)
    lights = tf.light_rig('day', cam=cam, az_off=az_off)
    if sun_el is not None:
        lights[0].rotation_euler[0] = math.radians(90 - sun_el)
    out = os.path.join(HERE, '..', f'_pv_{SHOT}.png')
    S.render.resolution_x, S.render.resolution_y = W // 4, H // 4
    S.cycles.samples = 6
    if exposure is None:
        S.render.filepath = out; bpy.ops.render.render(write_still=True)
        m = tf.measure(out, 'day')
        ch = max(-0.8, min(0.8, m['exposure_change']))
        S.view_settings.exposure += ch
        lights = tf.light_rig('day', cam=cam, az_off=az_off)
        if sun_el is not None:
            lights[0].rotation_euler[0] = math.radians(90 - sun_el)
    else:
        S.view_settings.exposure = exposure
        lights = tf.light_rig('day', cam=cam, az_off=az_off)
        if sun_el is not None:
            lights[0].rotation_euler[0] = math.radians(90 - sun_el)
    S.render.resolution_x, S.render.resolution_y = W, H
    S.cycles.samples = SPP
    S.render.filepath = out; bpy.ops.render.render(write_still=True)
    print('MEASURE', SHOT, tf.measure(out, 'day'), 'exposure', S.view_settings.exposure)
    bpy.context.view_layer.update()
    lab = []
    for text, wpos, dy in LABELS:
        c = world_to_camera_view(S, cam, Vector(wpos))
        lab.append((text, c.x * W, (1 - c.y) * H + dy))
    json.dump(lab, open(out.replace('.png', '.json'), 'w'))


# ====================================================================================================
if SHOT == 'lineup_big':
    ground('grass')
    kid((-118, 0, 0)); label('kid 5', (-118, 0, 0))
    cottage((-102, 0, 0)); label('cottage 14', (-102, 0, 0))
    c = append('TS_Bushes'); move(c, (-80, 0, 0)); label('bushes 3-5', (-80, 0, 0))
    baby((-56, 0, 0)); label('baby troll 16', (-56, 0, 0))
    c = append('TS_Tree'); hide_stage(c, ['TS_Tree_A', 'TS_Tree_C', 'TS_Tree_D', 'TS_Tree_E']); move(c, (-34, 0, 0)); label('sprout (B) 40', (-34, 0, 0))
    c = append('TS_ChampionOak'); move(c, (0, 0, 0)); label("champion's oak 40", (0, 0, 0))
    tree((78, 0, 0), 'CDE'); label('our tree (C+D+E) 100', (78, 0, 0))
    cam = camera_((4, -520, 30), (4, 0, 49), 70, 'HORIZONTAL')
    render(cam, sun_el=38)
elif SHOT == 'lineup_small':
    ground('grass')
    kid((-33, 0, 0)); label('kid 5', (-33, 0, 0))
    c = append('TS_Tree'); hide_stage(c, ['TS_Tree_B', 'TS_Tree_C', 'TS_Tree_D', 'TS_Tree_E']); move(c, (-29, 0, 0)); label('the dot (A) 0.3', (-28.6, 0, 0))
    c = append('TS_Props')
    for nm, x in (('TS_Apple_Single', -25.3), ('TS_Apple_Loose_01', -22.5), ('TS_Apple_Loose_02', -21.0), ('TS_Apple_Loose_03', -19.5), ('TS_MeasuringPillar', -0.5), ('TS_PieTable', 10.5), ('TS_PieTable_Squished', 25.5)):
        find(c, nm).location = (x, 0, 0)
    label('apple 1', (-25.3, 0, 0)); label('loose apples', (-21, 0, 0)); label('measuring pillar 8', (-0.5, 0, 0)); label('pie table', (10.5, 0, 0)); label('squished', (25.5, 0, 0))
    c = append('TS_Bushes'); move(c, (-10.5, 0, 0));
    for o in c.all_objects: o.location.x = -10.5 + (o.location.x + 10.5) * 0.75
    label('bushes 3 / 4 / 5', (-10.5, 0, 0))
    baby((42, 0, 0)); label('baby troll 16', (42, 0, 0))
    cottage((60, 2, 0)); label('cottage 14', (60, 0, 0))
    cam = camera_((17, -218, 7), (17, 0, 6.2), 70, 'HORIZONTAL')
    render(cam, sun_el=42)
elif SHOT == 'mother':
    ground('grass')
    mother((0, 0, 0)); label('troll mother 450', (0, 0, 0))
    tree((-360, -40, 0), 'CDE'); label('our tree 100', (-360, -40, 0))
    c = append('TS_ChampionOak'); move(c, (-470, -60, 0)); label('oak 40', (-470, -60, 0))
    baby((330, -60, 0)); label('baby 16', (330, -60, 0))
    for i, x in enumerate((385, 405, 427)):
        cottage((x, -50 + 6 * i, 0), rz=-10 + 10 * i, wallhex=('#E4E7E2', '#D3B78B', '#E4E7E2')[i])
    label('cottages 14', (405, -50, 0))
    kid((360, -70, 0)); label('kid', (360, -70, 0))
    cam = camera_((0, -1750, 60), (0, 0, 215), 60, 'HORIZONTAL')
    render(cam, sun_el=40)
elif SHOT == 'stage_a':
    ground('grass')
    c = append('TS_Tree'); hide_stage(c, ['TS_Tree_B', 'TS_Tree_C', 'TS_Tree_D', 'TS_Tree_E'])
    kid((-1.0, 0.25, 0), rot=-20)
    cam = camera_((0.75, -2.3, 0.6), (-0.3, 0, 0.3), 40)
    render(cam, sun_el=45)
elif SHOT == 'stage_b':
    ground('grass')
    c = append('TS_Tree'); hide_stage(c, ['TS_Tree_A', 'TS_Tree_C', 'TS_Tree_D', 'TS_Tree_E'])
    kid((-7, -2, 0), rot=-30, face='toybox_shocked')
    cam = camera_((9, -52, 7), (-1, 0, 20), 28)
    render(cam, sun_el=45)
elif SHOT == 'stage_cde':
    ground('grass')
    for i, st in enumerate(('C', 'CD', 'CDE')):
        tree(((i - 1) * 112, 0, 0), st)
        kid(((i - 1) * 112 + 8, -26, 0), rot=10)
    cam = camera_((0, -560, 36), (0, 0, 49), 60, 'HORIZONTAL')
    render(cam, sun_el=36)
elif SHOT == 'stage_poses':
    ground('grass')
    X = (-104, 0, 104)
    tree((X[0], 0, 0), 'CDE', 'TS_TREE_HUG'); baby((X[0], -18.5, 0), face=3, pose_name='TS_BABY_ARMS_UP')
    c = tree((X[1], 0, 0), 'CDE', 'TS_TREE_GIVE')
    bpy.context.view_layer.update()
    sk = find(c, 'TS_Tree_Socket_HandL').matrix_world.translation.copy()
    print('GIVE socket', sk)
    kid((sk.x, sk.y - 5.5, 0), rot=180, arms=(150, 150))
    p = append('TS_Props')
    for o in p.all_objects:
        if o: o.hide_render = not o.name.startswith('TS_Apple_Single')
    ap = find(p, 'TS_Apple_Single'); ap.location = (sk.x, sk.y - 4.6, 5.4)
    tree((X[2], 0, 0), 'CDE', 'TS_TREE_PROTECT', blink=0.25); kid((X[2], -22, 0), rot=0)
    cam = camera_((30, -505, 78), (0, -14, 43), 60, 'HORIZONTAL')
    render(cam, sun_el=40)
elif SHOT == 'faces_baby':
    ground('grass')
    for i, nm in enumerate(('GRUMPY', 'GIGGLE', 'SNIFFLE', 'SURPRISED')):
        x = (i - 1.5) * 22
        baby((x, 0, 0), face=i, pose_name=(None, 'TS_BABY_ARMS_UP', 'TS_BABY_HEAD_TILT', None)[i]); label(f'{nm}  face={i}', (x, 0, 0))
    kid((-44.5, -1, 0))
    cam = camera_((0, -150, 9), (0, 0, 8.3), 58, 'HORIZONTAL')
    render(cam, sun_el=42, az_off=20)
elif SHOT == 'faces_mother':
    ground('grass')
    mother((-290, 0, 0), face=0); label('STERN  face=0', (-290, 0, 0))
    mother((290, 0, 0), face=1, pose_name='TS_MOTHER_LOOK_DOWN'); label('SOFT  face=1  (pose LOOK_DOWN)', (290, 0, 0))
    tree((0, -60, 0), 'CDE'); label('our tree 100', (0, -60, 0))
    cam = camera_((0, -1700, 120), (0, 0, 215), 58, 'HORIZONTAL')
    render(cam, sun_el=42, az_off=20)
elif SHOT == 'hero':
    ground('cobble')
    soil_disc((0, 0, 0), 27)
    tree((0, 0, 0), 'CDE', 'TS_TREE_HUG', smile=0.7)
    baby((0, -18.5, 0), face=0, pose_name='TS_BABY_ARMS_UP')
    kid((-1.2, -57.5, 0), rot=8, face='toybox_grin', arms=(165, 165), out=(18, 18))
    walls = ('#E4E7E2', '#D3B78B', '#E4E7E2', '#D3B78B', '#E4E7E2', '#E4E7E2')
    for i, (x, y, rz, w) in enumerate(((-33, 10, 16, 14), (-19, 48, 6, 13), (23, 50, -6, 14), (34, 8, -16, 13), (-52, -14, 34, 12), (54, -16, -36, 13))):
        cottage((x, y, 0), rz=rz, w=w, wall=8.5 + (i % 2), top=14 + (i % 3) * 0.8, wallhex=walls[i], roofhex=('#48546D', '#6B4A3A')[i % 2], name=f'cot{i}')
    p = append('TS_Props')
    find(p, 'TS_PieTable_Squished').location = (-21, -33, 0); find(p, 'TS_PieTable_Squished').rotation_euler.z = math.radians(24)
    find(p, 'TS_PieTable').location = (27, -22, 0); find(p, 'TS_PieTable').rotation_euler.z = math.radians(-24)
    find(p, 'TS_MeasuringPillar').location = (15.5, -47, 0); find(p, 'TS_MeasuringPillar').rotation_euler.z = math.radians(-16)
    for nm, loc in (('TS_Apple_Single', (3.2, -57.5, 0)), ('TS_Apple_Loose_01', (-11, -47, 0)), ('TS_Apple_Loose_02', (4, -44, 0)), ('TS_Apple_Loose_03', (8, -53, 0))):
        find(p, nm).location = loc
    b = append('TS_Bushes')
    for o, loc in zip(b.all_objects, ((30, -3, 0), (-30, -4, 0), (-26, -9, 0))):
        o.location = loc
    cam = camera_((4.5, -77, 3.4), (0.5, -8, 40), 21)
    render(cam, sun_el=37, az_off=28)
