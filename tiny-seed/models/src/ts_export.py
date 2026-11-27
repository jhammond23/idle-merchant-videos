# Tiny Seed: one .glb per asset (backup). python3 -I ts_export.py
import bpy, os, sys
ONLY = sys.argv[1].split(',') if len(sys.argv) > 1 else None
D = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
bpy.ops.wm.open_mainfile(filepath=os.path.join(D, 'tiny-seed-models.blend'))
os.makedirs(os.path.join(D, 'glb'), exist_ok=True)
for o in bpy.data.objects:
    if o.animation_data:
        for t in o.animation_data.nla_tracks:
            t.mute = False
for name in ('TS_Tree', 'TS_ChampionOak', 'TS_Bushes', 'TS_TrollBaby', 'TS_TrollMother', 'TS_Props'):
    if ONLY and name not in ONLY:
        continue
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    c = bpy.data.collections[name]
    for o in c.all_objects:
        o.select_set(True)
    kw = dict(filepath=os.path.join(D, 'glb', name + '.glb'), export_format='GLB', use_selection=True, export_apply=False,
              export_yup=True, export_animations=True, export_animation_mode='NLA_TRACKS', export_morph=True, export_skins=True,
              export_vertex_color='MATERIAL', export_image_format='AUTO')
    try:
        bpy.ops.export_scene.gltf(**kw)
    except TypeError as e:
        print('retry', e); kw.pop('export_vertex_color'); bpy.ops.export_scene.gltf(**kw)
    print('GLB', name, os.path.getsize(kw['filepath']))
