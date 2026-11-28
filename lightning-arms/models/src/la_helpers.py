# Lightning Arms: small helpers for the video builder (Blender 5.x). Copy next to your scene script and `import la_helpers as la`.
import bpy, json, os, math, random
from mathutils import Vector, Matrix

HERE = os.path.dirname(os.path.abspath(__file__))


def append(blend, name):
    """append one top-level collection (LA_GateOfOaths, LA_GateGiant, LA_WarBeast, LA_LightningArms, LA_SparkBurst, LA_GroundSplit,
    LA_IronCrown, LA_GateChains, LA_StoneArms, LA_IronArms, LA_WristNumbers, LA_SkyNumber) and link it into the scene.
    Appending twice gives a second copy with .001 names."""
    with bpy.data.libraries.load(blend, link=False) as (src, dst):
        dst.collections = [name]
    c = dst.collections[0]
    bpy.context.scene.collection.children.link(c)
    return c


def find(coll, base):
    """object in the collection by its base name (ignores a .001 suffix)."""
    for o in list(coll.all_objects):
        if o and o.name.split('.')[0] == base:
            return o
    raise KeyError(base)


def _show(o, on, frame=None):
    o.hide_render = o.hide_viewport = not on
    if frame is not None:
        o.keyframe_insert('hide_render', frame=frame); o.keyframe_insert('hide_viewport', frame=frame)


def show(o, on=True, frame=None, children=True):
    """show / hide an object and (by default) everything parented under it."""
    _show(o, on, frame)
    if children:
        for ch in o.children_recursive:
            _show(ch, on, frame)


def set_prop(root, name, value, frame=None):
    """set a 0..1 custom property on a kit root (`glow`, `eyes`, `stone`, `amount`, `digits`); children follow by themselves."""
    root[name] = float(value)
    root.update_tag()
    more_transparent_bounces()
    if frame is not None:
        root.keyframe_insert(f'["{name}"]', frame=frame)
    bpy.context.view_layer.update()


def more_transparent_bounces(n=32):
    """the glow shells and halos are stacked see-through layers: Cycles needs more than its default 8 transparent bounces."""
    for sc in bpy.data.scenes:
        if sc.cycles.transparent_max_bounces < n:
            sc.cycles.transparent_max_bounces = n


def apply_pose(arm, pose, frame=None, poses_json=None, key='beast'):
    """set a stored pose on a kit rig. pose: an Action name (e.g. 'LA_BEAST_KNEEL', 'LA_GIANT_STANDING') read from poses.json
    (key 'beast' or 'giant'), or a dict. With frame, also keys every bone (use CONSTANT interpolation for a still-frame film)."""
    if isinstance(pose, str):
        data = json.load(open(poses_json or os.path.join(HERE, '..', 'poses.json')))
        key = 'giant' if pose.startswith('LA_GIANT') else key
        pose = data[key]['poses'][pose]
    for bn, v in pose.items():
        pb = arm.pose.bones[bn]
        pb.rotation_mode = 'QUATERNION'
        pb.location = v['loc']; pb.rotation_quaternion = v['quat']; pb.scale = v['scale']
        if frame is not None:
            pb.keyframe_insert('location', frame=frame); pb.keyframe_insert('rotation_quaternion', frame=frame); pb.keyframe_insert('scale', frame=frame)
    bpy.context.view_layer.update()


def variant(root, letter, frame=None, tag='_Bolts_'):
    """show one flicker shape ('A'..'D') under a root and hide the others (lightning arms: tag '_Bolts_'; spark burst: '_Shape_')."""
    for o in root.children:
        b = o.name.split('.')[0]
        if tag in b:
            _show(o, b.endswith('_' + letter), frame)


# ---------------------------------------------------------------- gate
def set_eyes(gate_coll, value, frame=None, base='LA_Gate'):
    """the gate's eyes: 0 closed, about 0.15 a faint glow under the lids, 1 open and glowing. base 'LA_Gate' or 'LA_GateGiant_Body'."""
    set_prop(find(gate_coll, base), 'eyes', value, frame)


def set_shake(gate_coll, amount=1.0, frame=None, seed=0, dust=True):
    """shake the gate for one frame: a small seeded tilt and slide of the whole gate (delta transforms, so its location stays put)
    and the falling grit / dust object shown. amount 0 puts it back. Call with a new seed every frame or two."""
    g = find(gate_coll, 'LA_Gate')
    rng = random.Random(seed * 7919 + 3)
    g['shake'] = float(amount)
    g.delta_rotation_euler = (math.radians(rng.uniform(-0.7, 0.7) * amount), math.radians(rng.uniform(-1.1, 1.1) * amount), math.radians(rng.uniform(-0.5, 0.5) * amount))
    g.delta_location = (rng.uniform(-0.18, 0.18) * amount, rng.uniform(-0.08, 0.08) * amount, 0)
    d = find(gate_coll, 'LA_Gate_ShakeDust')
    _show(d, dust and amount > 0, frame)
    d.delta_location = (0, 0, -rng.uniform(0, 2.5) * amount)
    if frame is not None:
        g.keyframe_insert('delta_rotation_euler', frame=frame); g.keyframe_insert('delta_location', frame=frame); g.keyframe_insert('["shake"]', frame=frame)
        d.keyframe_insert('delta_location', frame=frame)
    bpy.context.view_layer.update()


# ---------------------------------------------------------------- arms (lightning, stone, iron), wrist bands
def attach_arm(shell_root, arm_empty, hide_cast=True):
    """put an arm shell (LA_LightningArm_L/R, LA_StoneArm_*, LA_IronArm_*) on a Cast v2 arm pivot empty (heroarmL, villainarmR ...):
    origin on the shoulder pivot, turned with the arm, world scale kept at 1. hide_cast hides the cast's own arm and hand meshes
    under that empty (anything else it holds, like the Villain's staff, stays)."""
    bpy.context.view_layer.update()
    loc, rot, _ = arm_empty.matrix_world.decompose()
    M = Matrix.Translation(loc) @ rot.to_matrix().to_4x4()
    shell_root.parent = arm_empty
    shell_root.matrix_parent_inverse = arm_empty.matrix_world.inverted()
    shell_root.matrix_world = M
    if hide_cast:
        for ch in arm_empty.children:
            b = ch.name.split('.')[0]
            if ch.type == 'MESH' and (b[-2:] in ('AL', 'AR') or b[-3:] in ('HdL', 'HdR')):
                ch.hide_render = ch.hide_viewport = True
    more_transparent_bounces()
    bpy.context.view_layer.update()


def cast_arm(cast_coll, side):
    """the arm pivot empty of a Cast v2 character collection: side 'L' (the -X arm) or 'R'."""
    for o in list(cast_coll.all_objects):
        if o.type == 'EMPTY' and o.name.split('.')[0].endswith('arm' + side):
            return o
    raise KeyError('arm' + side)


def attach_center(obj, target):
    """centre an object (spark burst, cuff) on another object's bounding-box centre and parent it there, world scale 1."""
    bpy.context.view_layer.update()
    mw = target.matrix_world
    c = sum((Vector(b) for b in target.bound_box), Vector()) / 8
    loc, rot, _ = mw.decompose()
    obj.parent = target
    obj.matrix_parent_inverse = mw.inverted()
    obj.matrix_world = Matrix.Translation(mw @ c) @ rot.to_matrix().to_4x4()
    bpy.context.view_layer.update()


def chain_between(link_obj, p0, p1, sag=0.0, ground=None, name='LA_ChainRun', collection=None, step=None):
    """a new chain from world point p0 to p1, made of linked copies of a kit link (LA_WarBeast_Link or LA_GateChain_Link).
    sag: how far the middle hangs (BU). ground: a z the chain may not go below (it lies on the ground there).
    Returns the parent empty; delete it with its children to remove the chain."""
    p0 = Vector(p0); p1 = Vector(p1)
    step = step or link_obj.get('link_step', 0.7)
    pts = []
    N = 200
    for i in range(N + 1):
        t = i / N
        p = p0.lerp(p1, t); p.z -= sag * 4 * t * (1 - t)
        if ground is not None:
            p.z = max(p.z, ground)
        pts.append(p)
    col = collection or bpy.context.scene.collection
    root = bpy.data.objects.new(name, None); col.objects.link(root)
    cur = pts[0]; i = 0; k = 0
    while True:
        while i <= N and (pts[i] - cur).length < step:
            i += 1
        if i > N:
            break
        nxt = cur + (pts[i] - cur).normalized() * step
        d = nxt - cur
        o = bpy.data.objects.new(f'{name}_{k:03d}', link_obj.data); col.objects.link(o); o.parent = root
        q = Vector((0, 0, 1)).rotation_difference(d.normalized())
        o.matrix_world = Matrix.Translation((cur + nxt) / 2) @ q.to_matrix().to_4x4() @ Matrix.Rotation(math.pi / 2 * (k % 2), 4, 'Z')
        cur = nxt; k += 1
    return root


NUMBER_KEYS = {'1 IN 2': '2', '1 IN 1,000,000': '1M', '1 IN 10,000,000': '10M', '2': '2', '1M': '1M', '10M': '10M'}


def set_number(band, text, frame=None):
    """wrist band text: '1 IN 2', '1 IN 1,000,000' or '1 IN 10,000,000' (shows that child, hides the other two)."""
    key = NUMBER_KEYS[text]
    for o in band.children:
        b = o.name.split('.')[0]
        if '_N_' in b:
            _show(o, b.endswith('_N_' + key), frame)


def crown_on(crown, cast_coll, lift=0.0, tilt=0.0):
    """sit LA_IronCrown on a Cast v2 character's head (made for the Villain): parented to the head mesh, world scale 1.
    lift raises it (BU), tilt leans it back (degrees)."""
    head = None
    for o in list(cast_coll.all_objects):
        b = o.name.split('.')[0]
        if o.type == 'MESH' and b.endswith('H') and not b.endswith('TH'):
            head = o
    bpy.context.view_layer.update()
    mw = head.matrix_world
    pts = [mw @ Vector(b) for b in head.bound_box]
    c = sum(pts, Vector()) / 8
    top = max(p.z for p in pts)
    loc, rot, _ = mw.decompose()
    crown.parent = head
    crown.matrix_parent_inverse = mw.inverted()
    crown.matrix_world = Matrix.Translation((c.x, c.y, top - 0.2 + lift)) @ rot.to_matrix().to_4x4() @ Matrix.Rotation(math.radians(tilt), 4, 'X')
    bpy.context.view_layer.update()


def cuff_on(cuff, arm_empty, z=-1.756):
    """close a gate cuff (LA_GateChains_Cuff_L/R) round a Cast v2 wrist: z is the cuff centre in the arm frame
    (Villain: -1.756, just above the hand). Returns the world position of its chain lug (behind the wrist)."""
    bpy.context.view_layer.update()
    loc, rot, _ = arm_empty.matrix_world.decompose()
    M = Matrix.Translation(loc) @ rot.to_matrix().to_4x4() @ Matrix.Translation((0, 0, z))
    cuff.parent = arm_empty
    cuff.matrix_parent_inverse = arm_empty.matrix_world.inverted()
    cuff.matrix_world = M
    _show(cuff, True)
    bpy.context.view_layer.update()
    return cuff.matrix_world @ Vector((0, 1.0, 0))
