"""Quick Workbench check renders of a saved .blend: python3 -I wb.py file.blend out.jpg camx camy camz tx ty tz lens [res]"""
import sys, bpy, math
from mathutils import Vector
a = sys.argv[1:]
bpy.ops.wm.open_mainfile(filepath=a[0])
sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'
sh = sc.display.shading
sh.light = 'STUDIO'
sh.color_type = 'MATERIAL'
sh.show_cavity = True
sh.cavity_type = 'BOTH'
sh.show_shadows = True
sc.display.shading.show_object_outline = False
M = 3.3
if a[2][0].isalpha():
    cam = bpy.data.objects[a[2]]
    res = int(a[3]) if len(a) > 3 else 540
else:
    cam = bpy.data.objects.new('wbcam', bpy.data.cameras.new('wbcam'))
    sc.collection.objects.link(cam)
    cam.location = Vector([float(x) for x in a[2:5]]) * M
    d = Vector([float(x) for x in a[5:8]]) * M - cam.location
    cam.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    cam.data.lens = float(a[8])
    cam.data.clip_end = 5000
    res = int(a[9]) if len(a) > 9 else 540
sc.camera = cam
sc.render.resolution_x, sc.render.resolution_y = res, int(res * 16 / 9)
sc.render.resolution_percentage = 100
sc.render.filepath = a[1]
sc.render.image_settings.file_format = 'JPEG'
bpy.ops.render.render(write_still=True)
