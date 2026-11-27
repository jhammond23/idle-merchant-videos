# Tiny Seed: small helpers for the video builder (Blender 5.x). Copy next to your scene script and `import ts_helpers as ts`.
import bpy, json, os


def append(blend, name):
    """append one top-level collection (TS_Tree, TS_ChampionOak, TS_Bushes, TS_TrollBaby, TS_TrollMother, TS_Props)
    and link it into the scene. Appending twice gives a second copy with .001 names."""
    with bpy.data.libraries.load(blend, link=False) as (src, dst):
        dst.collections = [name]
    c = dst.collections[0]
    bpy.context.scene.collection.children.link(c)
    return c


def find(coll, base):
    """object in the collection by its base name (ignores a .001 suffix)."""
    for o in coll.all_objects:
        if o and o.name.split('.')[0] == base:
            return o
    raise KeyError(base)


def stage(tree_coll, show):
    """tree stages to render, e.g. stage(c, 'A'), stage(c, 'B'), stage(c, 'C'), stage(c, 'CD'), stage(c, 'CDE').
    Keyframe hide_render / hide_viewport on the same objects for swaps inside a shot."""
    for ch in tree_coll.children_recursive:
        letter = ch.name.split('_')[2]          # TS_Tree_<A..E>_...
        for o in ch.objects:
            o.hide_render = o.hide_viewport = letter not in show


def apply_pose(arm, pose, frame=None, poses_json=None):
    """set a stored pose on an armature. pose: an Action name (e.g. 'TS_TREE_HUG') read from poses.json, or a dict.
    With frame, also keys location / rotation / scale of every posed bone on that frame."""
    if isinstance(pose, str):
        data = json.load(open(poses_json or os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'poses.json')))
        for group in data.values():
            if pose in group:
                pose = group[pose]
                break
    for bn, v in pose.items():
        pb = arm.pose.bones[bn]
        pb.rotation_mode = 'QUATERNION'
        if 'loc' in v: pb.location = v['loc']
        if 'quat' in v: pb.rotation_quaternion = v['quat']
        if 'scale' in v: pb.scale = v['scale']
        if frame is not None:
            pb.keyframe_insert('location', frame=frame); pb.keyframe_insert('rotation_quaternion', frame=frame); pb.keyframe_insert('scale', frame=frame)


BABY_FACES = {'GRUMPY': 0, 'GIGGLE': 1, 'SNIFFLE': 2, 'SURPRISED': 3}
MOTHER_FACES = {'STERN': 0, 'SOFT': 1}


def set_face(face_obj, index, frame=None):
    """instant face swap: face_obj is TS_TrollBaby_Face or TS_TrollMother_Face, index from the tables above."""
    face_obj['face'] = int(index)
    face_obj.update_tag()
    if frame is not None:
        face_obj.keyframe_insert('["face"]', frame=frame)
        ad = face_obj.animation_data
        try:                                    # constant interpolation = 1-frame swap
            for layer in ad.action.layers:
                for strip in layer.strips:
                    for bag in strip.channelbags:
                        for fc in bag.fcurves:
                            for k in fc.keyframe_points:
                                k.interpolation = 'CONSTANT'
        except Exception:
            pass


def blink(face_obj, value, frame=None):
    """tree eyelids: face_obj is TS_Tree_Face, value 0 (open) .. 1 (closed); 0.25 is a soft, kind look."""
    kb = face_obj.data.shape_keys.key_blocks['BLINK']
    kb.value = value
    if frame is not None:
        kb.keyframe_insert('value', frame=frame)
