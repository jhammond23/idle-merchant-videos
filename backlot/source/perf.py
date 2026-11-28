import sys, time, bpy
sys.path[:0]=['/tmp/claude-0/backlot/source','/tmp/claude-0/backlot/materials']
bpy.ops.wm.open_mainfile(filepath=sys.argv[1])
sc=[s for s in bpy.data.scenes if s.get('bl_preset')=='DAY'][0]
cam=[o for o in bpy.data.objects if o.name.endswith(sys.argv[2])][0]
sc.camera=cam; sc.render.resolution_percentage=25; sc.cycles.samples=16
g=bpy.data.node_groups['BL Global']
for ao in (1.0, 0.0):
    g.nodes['AO'].outputs[0].default_value=ao
    sc.render.filepath='/tmp/claude-0/backlot/tmp/perf_ao%d.jpg'%int(ao)
    t=time.time(); bpy.ops.render.render(write_still=True, scene=sc.name); print('AO',ao,'%.1fs'%(time.time()-t), flush=True)
