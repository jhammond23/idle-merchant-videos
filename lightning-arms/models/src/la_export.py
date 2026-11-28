# Lightning Arms: one .glb per collection (backup for Blender 5.1 / other tools). python3 -I la_export.py [names]
import bpy, os, sys
ONLY = sys.argv[1].split(',') if len(sys.argv) > 1 else None
D = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
bpy.ops.wm.open_mainfile(filepath=os.path.join(D, 'lightning-models.blend'))
os.makedirs(os.path.join(D, 'glb'), exist_ok=True)
for o in bpy.data.objects:
    o.hide_viewport = False; o.hide_render = False; o.hide_set(False)      # the .glb carries every state at once
    if o.animation_data:
        for t in o.animation_data.nla_tracks:
            t.mute = False
for c in list(bpy.context.scene.collection.children):
    name = c.name
    if ONLY and name not in ONLY:
        continue
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for o in list(c.all_objects):
        o.select_set(True)
    kw = dict(filepath=os.path.join(D, 'glb', name + '.glb'), export_format='GLB', use_selection=True, export_apply=False,
              export_yup=True, export_animations=True, export_animation_mode='NLA_TRACKS', export_morph=True, export_skins=True,
              export_vertex_color='MATERIAL', export_image_format='AUTO', export_lights=True, export_extras=True)
    for _ in range(4):
        try:
            bpy.ops.export_scene.gltf(**kw); break
        except TypeError as e:
            bad = str(e).split('"')[1] if '"' in str(e) else None
            print('retry without', bad, e)
            if bad in kw:
                kw.pop(bad)
            else:
                kw.pop('export_vertex_color', None)
    print('GLB', name, os.path.getsize(kw['filepath']))
