# shared by the wheel and reflection stories (square server and land server)
def wipe(*prefixes):
    for o in list(bpy.data.objects):
        if o.name.startswith(prefixes): bpy.data.objects.remove(o, do_unlink=True)
if 'WKID' not in globals() or globals().get('WKID_HAIR') != 'hero_pixie':
    wipe('wkid')
    for _m in list(bpy.data.materials):
        if _m.name.startswith('wkid'): bpy.data.materials.remove(_m)
    WKID_HAIR = 'hero_pixie'
    WKID, WKIDP = person('wkid', (252, 200, 44), (44, 56, 96), 'hero_pixie', 'face_bright', skin=(238, 196, 156)); WKID.scale = (0.8, 0.8, 0.8); away(WKID)
def poster_set(which):
    m = bpy.data.materials.get('posterM')
    if not m: return
    p = '/tmp/claude-0/tv/nx/tex/poster_%s.png' % which
    img = bpy.data.images.get('poster_%s.png' % which) or bpy.data.images.load(p)
    for n in m.node_tree.nodes:
        if n.type == 'TEX_IMAGE': n.image = img
print('SET COMMON OK', flush=True)
