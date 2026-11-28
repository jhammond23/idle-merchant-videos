# Lightning Arms: the war beast's poses (one-frame Actions on muted NLA tracks + poses.json). Built for still frames.
from la_lib import *
from la_beast import FA, RA

Y = Vector((0, 1, 0))


def aim(a, bn, d):
    pb = a.pose.bones[bn]
    bpy.context.view_layer.update()
    M = pb.matrix.copy(); q = M.to_quaternion()
    dq = (q @ Y).rotation_difference(Vector(d).normalized())
    pb.matrix = Matrix.LocRotScale(M.translation, dq @ q, None)
    bpy.context.view_layer.update()


def head_of(a, bn):
    bpy.context.view_layer.update()
    return a.pose.bones[bn].matrix.translation.copy()


def blen(a, bn):
    return a.data.bones[bn].length


def rest_rot(a, bn, pitch=0.0, yaw=0.0, roll=0.0):
    """give the bone its rest orientation in armature space (whatever its parents do), plus a pitch about X (+ = nose / toe down),
    a yaw about Z and a roll about Y."""
    pb = a.pose.bones[bn]
    bpy.context.view_layer.update()
    M = pb.matrix.copy()
    q = (Matrix.Rotation(R(yaw), 3, 'Z') @ Matrix.Rotation(R(roll), 3, 'Y') @ Matrix.Rotation(R(pitch), 3, 'X')).to_quaternion() @ a.data.bones[bn].matrix_local.to_quaternion()
    pb.matrix = Matrix.LocRotScale(M.translation, q, None)
    bpy.context.view_layer.update()


def leg(a, which, sd, ankle, hint=None, hoof=0.0):
    """two-bone IK: plant the ankle (armature space). which 'Front' / 'Rear'. hoof: toe pitch in degrees (+ = toe down)."""
    U, L, H = f'LA_{which}Upper{sd}', f'LA_{which}Lower{sd}', f'LA_{which}Hoof{sd}'
    S = head_of(a, U)
    hint = hint or ((0, -1, 0.2) if which == 'Front' else (0, 1, 0.2))
    K, A = two_bone(S, Vector(ankle), blen(a, U), blen(a, L), hint)
    aim(a, U, K - S); aim(a, L, A - K)
    rest_rot(a, H, hoof)


def legs(a, fl=None, fr=None, rl=None, rr=None, hoofs=(0, 0, 0, 0)):
    for (which, sd, t, base, hf) in (('Front', 'L', fl, FA['L'], hoofs[0]), ('Front', 'R', fr, FA['R'], hoofs[1]),
                                     ('Rear', 'L', rl, RA['L'], hoofs[2]), ('Rear', 'R', rr, RA['R'], hoofs[3])):
        t = (0, 0, 0) if t is None else t
        leg(a, which, sd, Vector(base) + Vector(t), hoof=hf)


def body(a, move=(0, 0, 0), pitch=0.0, pivot=(0, 2, 13), roll=0.0, yaw=0.0):
    pose_move(a, 'LA_Body', move)
    p = Vector(pivot) + Vector(move)
    if pitch:
        pose_rot_about(a, 'LA_Body', 'X', pitch, p)
    if roll:
        pose_rot_about(a, 'LA_Body', 'Y', roll, p)
    if yaw:
        pose_rot_about(a, 'LA_Body', 'Z', yaw, p)


def head(a, neck=0.0, pitch=0.0, yaw=0.0, roll=0.0, neck_yaw=0.0, floor=0.35):
    """neck: extra pitch of the neck (+ = down). pitch: head pitch in armature space relative to its rest (+ = nose down)."""
    pose_rot(a, 'LA_Neck', 'X', neck)
    if neck_yaw:
        pose_rot(a, 'LA_Neck', 'Z', neck_yaw)
    rest_rot(a, 'LA_Head', pitch, yaw, roll)
    for _ in range(60):                                   # never push the head through the ground: lift the neck until it clears
        if group_min_z(a, ('LA_Head',)) >= floor:
            break
        if _ < 14:
            pose_rot(a, 'LA_Neck', 'X', -1.5)
        else:
            pitch -= 1.5
        rest_rot(a, 'LA_Head', pitch, yaw, roll)


BODY = [None]


def group_min_z(a, bones):
    o = BODY[0]
    bpy.context.view_layer.update()
    d = bpy.context.evaluated_depsgraph_get()
    ev = o.evaluated_get(d); me = ev.to_mesh()
    idx = {o.vertex_groups[b].index for b in bones if b in o.vertex_groups}
    z = min((v.co.z for v in me.vertices if any(g.group in idx for g in v.groups)), default=9.0)
    ev.to_mesh_clear()
    return z


def kneel_front(a, sd, fold=0.0, knee_y=0.0):
    """front knee on the ground, lower leg folded back along the ground."""
    U, L, H = f'LA_FrontUpper{sd}', f'LA_FrontLower{sd}', f'LA_FrontHoof{sd}'
    S = head_of(a, U)
    l1 = blen(a, U)
    kz = 2.9
    dz = S.z - kz
    dy = math.sqrt(max(l1 * l1 - dz * dz, 0.0))
    aim(a, U, Vector((0, -dy + knee_y, -dz)))
    aim(a, L, Vector((0, 1, 0.05 + fold)))
    rest_rot(a, H, 96)
    return dz - l1


def stand(a):
    pass


def pull(a):
    """straining forward against its chains: low, leaning in, hooves dug."""
    body(a, (0, -2.6, -1.9), 9, roll=-2)
    legs(a, fl=(0, 2.2, 0), fr=(0, -3.6, 0), rl=(0, 4.4, 0), rr=(0, 0.8, 0), hoofs=(8, 0, 22, 12))
    head(a, 16, 16, yaw=-6)
    pose_rot(a, 'LA_Tail', 'X', 62)


def charge(a):
    """full gallop, horns down."""
    body(a, (0, 0, 1.6), 7)
    legs(a, fl=(0, -8.6, 2.6), fr=(0, -5.4, 0.9), rl=(0, 7.2, 3.4), rr=(0, 4.6, 0.6), hoofs=(-38, -22, 58, 34))
    head(a, 24, 30)
    pose_rot(a, 'LA_Tail', 'X', 95)


def skid(a):
    """braking hard: haunches down, front legs braced stiff ahead, heels dug in, head thrown up."""
    body(a, (0, 2.4, -3.0), -13, pivot=(0, 6, 13))
    legs(a, fl=(0, -6.8, 0), fr=(0, -4.6, 0), rl=(0, -2.8, 0), rr=(0, -1.2, 0), hoofs=(-24, -24, 0, 0))
    head(a, -16, -14, roll=4)
    pose_rot(a, 'LA_Tail', 'X', 80)


def _kneel(a, pitch, drop=0.0):
    body(a, (0, 0, -drop), pitch, pivot=(0, 10.5, 12.5))
    ex = max(kneel_front(a, 'L'), 0.0)
    if ex > 0:
        pose_move(a, 'LA_Body', (0, 0, -ex - 0.02))
        pose_reset_legs(a)
    kneel_front(a, 'L', 0.02); kneel_front(a, 'R', -0.02, knee_y=0.6)
    legs_rear(a)


def pose_reset_legs(a):
    for pb in a.pose.bones:
        if 'Upper' in pb.name or 'Lower' in pb.name or 'Hoof' in pb.name:
            pb.rotation_quaternion = (1, 0, 0, 0)
    bpy.context.view_layer.update()


def legs_rear(a, t=(0, 0, 0)):
    for sd in ('L', 'R'):
        leg(a, 'Rear', sd, Vector(RA[sd]) + Vector(t))


def kneel(a):
    """kneeling to the kid: front knees down, head level with a child."""
    _kneel(a, 18)
    head(a, 4, -6)


def bow_to_kid(a):
    """still kneeling, head bowed low to the kid in front of it."""
    _kneel(a, 19)
    head(a, 10, 20)


def bow(a):
    """a deep bow toward something huge: chest right down, nose to the ground, horns laid forward."""
    _kneel(a, 20.5)
    head(a, 6, 42, floor=0.25)
    pose_rot(a, 'LA_Tail', 'X', -8)


DEFS = [('STAND', stand), ('PULL', pull), ('CHARGE', charge), ('SKID', skid), ('KNEEL', kneel), ('BOW', bow), ('BOW_TO_KID', bow_to_kid)]


def build(arm, body_obj):
    acts, out, notes = [], {}, {}
    BODY[0] = body_obj
    for name, fn in DEFS:
        pose_reset(arm); fn(arm)
        bpy.context.view_layer.update()
        acts.append(save_action(arm, 'LA_BEAST_' + name)); out['LA_BEAST_' + name] = pose_dict(arm)
        d = bpy.context.evaluated_depsgraph_get()
        nt = {}
        for o in arm.children:
            if o.type == 'EMPTY' and 'Socket' in o.name:
                nt[o.name] = [round(x, 2) for x in o.evaluated_get(d).matrix_world.translation]
        ev = body_obj.evaluated_get(d); me = ev.to_mesh()
        co = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
        nt['minz_by_bone'] = {b.name: round(group_min_z(arm, (b.name,)), 2) for b in arm.data.bones if group_min_z(arm, (b.name,)) < -0.05}
        nt['bounds'] = [[round(float(x), 2) for x in co.min(axis=0)], [round(float(x), 2) for x in co.max(axis=0)]]
        ev.to_mesh_clear()
        notes['LA_BEAST_' + name] = nt
        print('POSE', name, nt)
    pose_reset(arm); push_nla(arm, acts)
    return {'poses': out, 'sockets': notes}
