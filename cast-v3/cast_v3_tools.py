# Cast v3 helpers (also stored inside cast-v3.blend as the text block "cast_v3_tools.py").
# Paste into Blender's Python console, or run the text block, then call the functions.
#   rig = bpy.data.objects['First Rank | rig']
#   set_pose(rig, 'point', frame=12)        # named pose from the rig's 'poses' property (keyed if frame is given)
#   set_face(rig, 'shocked', frame=12)      # expression by name or index (constant interpolation when keyed)
#   talk(rig, 'open', frame=14)             # 'closed' | 'half' | 'open' | 'off' (characters with a talk set)
#   blink(rig, frame=20)                    # 2-frame blink
#   lipsync(rig, amplitudes, start, fps)    # amplitudes: list of 0..1 per frame -> mouth states, each held >= 2 frames
import bpy, json
from mathutils import Quaternion

def _names(rig, key):
    return [x.split(' ', 1)[1] for x in rig.get(key, '').split(', ') if ' ' in x]

def set_pose(rig, name, frame=None):
    table = json.loads(rig['poses'])
    if name not in table: raise KeyError('%s has no pose %r; poses: %s' % (rig.name, name, ', '.join(table)))
    for b, q in table[name].items():
        pb = rig.pose.bones.get(b)
        if pb is None: continue
        pb.rotation_mode = 'QUATERNION'; pb.rotation_quaternion = Quaternion(q)
        if frame is not None: pb.keyframe_insert('rotation_quaternion', frame=frame, group=b)
    if 'pose_props' in rig:      # props that belong to a pose (e.g. the Old Legend's sword in hand for 'raise_sword')
        pp = json.loads(rig['pose_props'])
        for k, v in list(pp.get('_default', {}).items()) + list(pp.get(name, {}).items()): _key_int(rig, k, v, frame)

def _fcurves(rig):
    ad = rig.animation_data
    if not ad or not ad.action: return []
    try:   # Blender 4.4+ slotted actions
        from bpy_extras.anim_utils import action_get_channelbag_for_slot
        cb = action_get_channelbag_for_slot(ad.action, ad.action_slot)
        return list(cb.fcurves) if cb else []
    except Exception:
        return list(getattr(ad.action, 'fcurves', []))

def _key_int(rig, prop, value, frame):
    rig[prop] = value
    if frame is not None:
        rig.keyframe_insert('["%s"]' % prop, frame=frame)
        for fc in _fcurves(rig):
            if fc.data_path == '["%s"]' % prop:
                for kp in fc.keyframe_points: kp.interpolation = 'CONSTANT'

def set_face(rig, expr, frame=None):
    names = _names(rig, 'face_names')
    idx = expr if isinstance(expr, int) else names.index(expr)
    _key_int(rig, 'face', idx, frame)

def talk(rig, state, frame=None):
    names = ['off'] + [n for n in _names(rig, 'mouth_names')[1:]] if 'mouth_names' in rig else ['off']
    idx = 0 if state == 'off' else names.index(state)
    _key_int(rig, 'mouth', idx, frame)

def blink(rig, frame):
    _key_int(rig, 'blink', 0, frame - 1); _key_int(rig, 'blink', 1, frame); _key_int(rig, 'blink', 0, frame + 2)

def lipsync(rig, amps, start=1, hold=2):
    """amps: per-frame loudness 0..1 (e.g. from the ElevenLabs audio). <0.12 closed, <0.45 half, else open; each state held >= hold frames."""
    last, held = None, 0
    for i, a in enumerate(amps):
        st = 'closed' if a < 0.12 else ('half' if a < 0.45 else 'open')
        if st != last and held >= hold or last is None:
            talk(rig, st, start + i); last, held = st, 0
        held += 1
    talk(rig, 'off', start + len(amps))
