# Lightning Arms: self-check of the .blend and the .glb backups. python3 -I la_check.py
import bpy, os, sys, json
D = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
bpy.ops.wm.open_mainfile(filepath=os.path.join(D, 'lightning-models.blend'))
bad = []
for o in bpy.data.objects:
    if any(abs(s - 1) > 1e-5 for s in o.scale):
        bad.append(('scale', o.name, tuple(o.scale)))
    if any(abs(r) > 1e-5 for r in o.rotation_euler) and not o.name.startswith('LA_NONE') and not (o.parent_type == 'BONE' and False):
        bad.append(('rot', o.name, tuple(o.rotation_euler)))
    if not o.name.startswith('LA_'):
        bad.append(('name', o.name))
print('objects', len(bpy.data.objects), 'problems', bad)
print('collections', [(c.name, len(c.all_objects)) for c in bpy.context.scene.collection.children])
print('hidden by default', sorted(o.name for o in bpy.data.objects if o.hide_render))
print('actions', sorted(a.name for a in bpy.data.actions))
rig = bpy.data.objects['LA_WarBeast_Rig']
print('nla', [(t.name, t.mute) for t in rig.animation_data.nla_tracks], 'active action', rig.animation_data.action)
print('bones', [b.name for b in rig.data.bones])
print('images', len(bpy.data.images), 'libraries', len(bpy.data.libraries))
drv = []
for idb in list(bpy.data.objects) + list(bpy.data.lights):
    if idb.animation_data:
        for fc in idb.animation_data.drivers:
            drv.append((idb.name, fc.data_path, fc.driver.type, fc.driver.expression if fc.driver.type == 'SCRIPTED' else ''))
print('drivers', len(drv), 'scripted', [d for d in drv if d[2] == 'SCRIPTED'])
print('materials without LA_ prefix', [m.name for m in bpy.data.materials if not m.name.startswith('LA_Mat_')])
print('material count', len(bpy.data.materials))
tot = sum(len(o.data.vertices) for o in bpy.data.objects if o.type == 'MESH')
print('total verts', tot)
# glb round trip
for f in sorted(os.listdir(os.path.join(D, 'glb'))):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=os.path.join(D, 'glb', f))
    ms = [o for o in bpy.data.objects if o.type == 'MESH']
    vc = sum(1 for o in ms if len(o.data.color_attributes))
    import mathutils
    lo = [1e9] * 3; hi = [-1e9] * 3
    for o in ms:
        for b in o.bound_box:
            w = o.matrix_world @ mathutils.Vector(b)
            for i in range(3):
                lo[i] = min(lo[i], w[i]); hi[i] = max(hi[i], w[i])
    print('GLB', f, 'objects', len(bpy.data.objects), 'meshes', len(ms), 'with vertex colours', vc, 'armatures', sum(1 for o in bpy.data.objects if o.type == 'ARMATURE'),
          'actions', len(bpy.data.actions), 'lights', sum(1 for o in bpy.data.objects if o.type == 'LIGHT'), 'size', [round(hi[i] - lo[i], 1) for i in range(3)])
