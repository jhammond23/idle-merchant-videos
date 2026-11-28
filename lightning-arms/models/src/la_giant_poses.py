# Lightning Arms: the gate giant's poses (one-frame Actions on muted NLA tracks + poses.json). Built for still frames.
from la_lib import *
from la_beast_poses import aim, head_of, blen, rest_rot

J_ANKLE = {'L': Vector((18, 0, 6)), 'R': Vector((-18, 0, 6))}


def leg(a, sd, ankle=None, hint=(0, -1, 0.1), foot=0.0):
    T_, S_, F_ = f'LA_Thigh{sd}', f'LA_Shin{sd}', f'LA_Foot{sd}'
    H = head_of(a, T_)
    K, A = two_bone(H, Vector(ankle) if ankle is not None else J_ANKLE[sd], blen(a, T_), blen(a, S_), hint)
    aim(a, T_, K - H); aim(a, S_, A - K)
    rest_rot(a, F_, foot)


def arm_to(a, sd, wrist, hint, hand=(0, 0, -1)):
    """wrist: armature-space target. hint: where the elbow bends to. hand: direction the fingers point."""
    A_, F_, H_ = f'LA_Arm{sd}', f'LA_Forearm{sd}', f'LA_Hand{sd}'
    S = head_of(a, A_)
    K, W = two_bone(S, Vector(wrist), blen(a, A_), blen(a, F_), hint)
    aim(a, A_, K - S); aim(a, F_, W - K); aim(a, H_, Vector(hand))


def standing(a):
    pass


def looking_down(a):
    """standing over the square, bending its head to the people below; left hand lifting a little."""
    pose_rot(a, 'LA_Spine', 'X', 9)
    pose_rot(a, 'LA_Head', 'X', 26)
    s = head_of(a, 'LA_ArmL')
    arm_to(a, 'L', s + Vector((8, -22, -50)), (1, 0.6, 0.2), hand=(0, -0.5, -1))
    s = head_of(a, 'LA_ArmR')
    arm_to(a, 'R', s + Vector((-6, -4, -61)), (-1, 0.5, 0))


def rising(a):
    """half up: knees still deep, back bent, one hand pushing off the ground, the other on its knee, head lifting."""
    pose_move(a, 'LA_Hips', (0, 9, -31))
    pose_rot(a, 'LA_Hips', 'X', 8)
    pose_rot(a, 'LA_Spine', 'X', 24); pose_rot(a, 'LA_Spine', 'Z', -7)
    pose_rot(a, 'LA_Head', 'X', -16)
    leg(a, 'L', J_ANKLE['L'] + Vector((2, -6, 0)), hint=(0.15, -1, 0.3))
    leg(a, 'R', J_ANKLE['R'] + Vector((-3, 12, 4)), hint=(-0.2, -1, 0.2), foot=28)
    arm_to(a, 'L', Vector((46, -52, 19)), (1, 0.5, 0.6), hand=(0.1, -0.5, -1))
    k = head_of(a, 'LA_ShinR')
    arm_to(a, 'R', k + Vector((-6, -8, 16)), (-1, 0.6, 0.3), hand=(0.3, -0.6, -1))


DEFS = [('STANDING', standing), ('RISING', rising), ('LOOKING_DOWN', looking_down)]


def build(arm, body_obj):
    acts, out, notes = [], {}, {}
    for name, fn in DEFS:
        pose_reset(arm); fn(arm)
        bpy.context.view_layer.update()
        acts.append(save_action(arm, 'LA_GIANT_' + name)); out['LA_GIANT_' + name] = pose_dict(arm)
        d = bpy.context.evaluated_depsgraph_get()
        nt = {}
        for o in arm.children:
            if o.type == 'EMPTY' and 'Socket' in o.name:
                nt[o.name] = [round(x, 1) for x in o.evaluated_get(d).matrix_world.translation]
        ev = body_obj.evaluated_get(d); me = ev.to_mesh()
        co = np.zeros(len(me.vertices) * 3); me.vertices.foreach_get('co', co); co = co.reshape(-1, 3)
        nt['bounds'] = [[round(float(x), 1) for x in co.min(axis=0)], [round(float(x), 1) for x in co.max(axis=0)]]
        ev.to_mesh_clear()
        notes['LA_GIANT_' + name] = nt
        print('GPOSE', name, nt)
    pose_reset(arm); push_nla(arm, acts)
    return {'poses': out, 'sockets': notes}
