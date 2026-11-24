import bpy, math, os, glob, mathutils, random
from mathutils import Vector, Euler
U='/mnt/user-data/uploads/roblox/buildDefend/assets'
_idx={os.path.basename(p)[:-4]:p for p in glob.glob(U+'/**/*.glb',recursive=True)}
_cache={}
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    _cache.clear()
def glb(name, loc=(0,0,0), rot=0, scale=1.0, tilt=(0,0)):
    """import once, then instance via linked duplicate collection instance"""
    if name not in _cache:
        before=set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=_idx[name])
        new=[o for o in bpy.data.objects if o not in before]
        col=bpy.data.collections.new('A_'+name)
        for o in new:
            for c in o.users_collection: c.objects.unlink(o)
            col.objects.link(o)
        _cache[name]=col
    col=_cache[name]
    inst=bpy.data.objects.new(name,None)
    inst.instance_type='COLLECTION'; inst.instance_collection=col
    inst.location=loc; inst.rotation_euler=(math.radians(tilt[0]),math.radians(tilt[1]),math.radians(rot+180)); inst.scale=(scale,)*3
    bpy.context.scene.collection.objects.link(inst)
    return inst
def mat(name, color, rough=0.6, emit=None, estr=0.0, metal=0.0, alpha=1.0, trans=0.0):
    m=bpy.data.materials.new(name); m.use_nodes=True
    b=m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value=(*color,1)
    b.inputs['Roughness'].default_value=rough
    b.inputs['Metallic'].default_value=metal
    if emit:
        b.inputs['Emission Color'].default_value=(*emit,1); b.inputs['Emission Strength'].default_value=estr
    if trans: b.inputs['Transmission Weight'].default_value=trans
    if alpha<1: b.inputs['Alpha'].default_value=alpha
    return m
def srgb(r,g,b):
    f=lambda c: ((c/255+0.055)/1.055)**2.4 if c/255>0.04045 else c/255/12.92
    return (f(r),f(g),f(b))
def box(name,size,loc,m,rot=(0,0,0),parent=None,bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc)
    o=bpy.context.active_object; o.name=name; o.scale=size; o.rotation_euler=rot
    bpy.ops.object.transform_apply(scale=True)
    if bevel:
        md=o.modifiers.new('b','BEVEL'); md.width=bevel; md.segments=2
    o.data.materials.append(m)
    if parent: o.parent=parent
    return o
HAIRDIR='/mnt/user-data/uploads/roblox/last-caravan-build-r001/assets-src/hair/player-20261031-r001/models/'
FACEDIR='/mnt/user-data/uploads/roblox/buildDefend/assets/last-caravan-hero-faces/20261031-r001/catalog/png/'
NEWFACES='/tmp/claude-0/tv/faces_new/png/'   # shocked / scared / angry (+ _talk_open, _talk_round, _blink), made by faces_new/mkfaces.py
def face_path(face):
    import os
    return NEWFACES+face+'.png' if os.path.exists(NEWFACES+face+'.png') else FACEDIR+face+'.png'
_hcache={}
def hair_col(key):
    if key not in _hcache:
        before=set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=HAIRDIR+key+'/'+key+'_hair.glb')
        new=[o for o in bpy.data.objects if o not in before]
        col=bpy.data.collections.new('H_'+key)
        for o in new:
            for c in o.users_collection: c.objects.unlink(o)
            if o.type=='MESH' and o.name.startswith('Icosphere'): bpy.data.objects.remove(o); continue
            col.objects.link(o)
        _hcache[key]=col
    return _hcache[key]
def head_mat(name, skin, face):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree
    b=nt.nodes['Principled BSDF']; b.inputs['Roughness'].default_value=0.5
    tc=nt.nodes.new('ShaderNodeTexCoord'); sep=nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(tc.outputs['Object'],sep.inputs[0])
    # u = x/1.2+0.5 , v = (z)/1.2+0.5  (head object origin at head center)
    mu=nt.nodes.new('ShaderNodeMath'); mu.operation='MULTIPLY_ADD'; mu.inputs[1].default_value=1/1.2; mu.inputs[2].default_value=0.5; nt.links.new(sep.outputs[0],mu.inputs[0])
    mv=nt.nodes.new('ShaderNodeMath'); mv.operation='MULTIPLY_ADD'; mv.inputs[1].default_value=1/1.2; mv.inputs[2].default_value=0.5; nt.links.new(sep.outputs[2],mv.inputs[0])
    cmb=nt.nodes.new('ShaderNodeCombineXYZ'); nt.links.new(mu.outputs[0],cmb.inputs[0]); nt.links.new(mv.outputs[0],cmb.inputs[1])
    tex=nt.nodes.new('ShaderNodeTexImage'); tex.extension='CLIP'
    img=bpy.data.images.get(face+'.png') or bpy.data.images.load(face_path(face)); tex.image=img
    nt.links.new(cmb.outputs[0],tex.inputs[0])
    front=nt.nodes.new('ShaderNodeMath'); front.operation='LESS_THAN'; front.inputs[1].default_value=-0.1; nt.links.new(sep.outputs[1],front.inputs[0])
    am=nt.nodes.new('ShaderNodeMath'); am.operation='MULTIPLY'; nt.links.new(tex.outputs['Alpha'],am.inputs[0]); nt.links.new(front.outputs[0],am.inputs[1])
    mix=nt.nodes.new('ShaderNodeMix'); mix.data_type='RGBA'; nt.links.new(am.outputs[0],mix.inputs['Factor'])
    mix.inputs['A'].default_value=(*skin,1); nt.links.new(tex.outputs['Color'],mix.inputs['B'])
    nt.links.new(mix.outputs['Result'],b.inputs['Base Color'])
    return m
def r6(name, shirt, pants, skin=None, hair='hero_swept_undercut', loc=(0,0,0), face='face_bright', beard=None, hair_scale=0.9):
    skin=skin or srgb(234,184,146)
    root=bpy.data.objects.new(name,None); bpy.context.scene.collection.objects.link(root); root.location=loc
    ms=mat(name+'s',srgb(*shirt),0.7); mp=mat(name+'p',srgb(*pants),0.7); mk=mat(name+'k',skin,0.5)
    parts={}
    parts['torso']=box(name+'T',(2,1,2),(0,0,3),ms,parent=root,bevel=0.05)
    # Roblox-style head: rounded cylinder, Tilly's face decal on the front
    bpy.ops.mesh.primitive_cylinder_add(vertices=40,radius=0.6,depth=1.2,location=(0,0,0))
    h=bpy.context.active_object; h.name=name+'H'; h.parent=root; h.location=(0,0,4.6)
    bv=h.modifiers.new('bv','BEVEL'); bv.width=0.22; bv.segments=5; bv.limit_method='ANGLE'
    bpy.ops.object.shade_smooth(); h.data.materials.append(head_mat(name+'face',skin,face))
    parts['head']=h
    for side,x in (('L',-1.5),('R',1.5)):
        piv=bpy.data.objects.new(name+'arm'+side,None); bpy.context.scene.collection.objects.link(piv); piv.parent=root; piv.location=(x,0,3.8)
        bx=box(name+'A'+side,(1,1,2),(0,0,-0.8),ms,parent=piv,bevel=0.05)
        hand=box(name+'Hd'+side,(0.98,0.98,0.5),(0,0,-1.58),mk,parent=piv,bevel=0.05)   # 11-13: 0.03 below the sleeve end (both ended at -1.8 and z-fought)
        parts['arm'+side]=piv
        lp=bpy.data.objects.new(name+'leg'+side,None); bpy.context.scene.collection.objects.link(lp); lp.parent=root; lp.location=(x/3,0,2)
        box(name+'L'+side,(1,1,2),(0,0,-1),mp,parent=lp,bevel=0.05)
        parts['leg'+side]=lp
    for key in (hair,beard):
        if not key: continue
        inst=bpy.data.objects.new(name+'_'+key,None); inst.instance_type='COLLECTION'; inst.instance_collection=hair_col(key)
        bpy.context.scene.collection.objects.link(inst); inst.parent=root; inst.location=(0,0,4.6); inst.scale=(hair_scale,)*3
    return root,parts
def sky(sun_el=18, sun_rot=200, strength=1.0, air=1.0, dust=1.0, ozone=1.0):
    w=bpy.data.worlds.new('W'); bpy.context.scene.world=w; w.use_nodes=True
    nt=w.node_tree; s=nt.nodes.new('ShaderNodeTexSky')
    try: s.sky_type='MULTIPLE_SCATTERING'
    except Exception:
        try: s.sky_type='NISHITA'
        except Exception: pass
    s.sun_elevation=math.radians(sun_el); s.sun_rotation=math.radians(sun_rot)
    for k,v in (('air_density',air),('dust_density',dust),('ozone_density',ozone)):
        if hasattr(s,k): setattr(s,k,v)
    bg=nt.nodes['Background']; bg.inputs['Strength'].default_value=strength
    nt.links.new(s.outputs['Color'],bg.inputs['Color'])
    return s
def flat_world(color,strength=1.0):
    w=bpy.data.worlds.new('W'); bpy.context.scene.world=w; w.use_nodes=True
    bg=w.node_tree.nodes['Background']; bg.inputs['Color'].default_value=(*color,1); bg.inputs['Strength'].default_value=strength
def sun(el=18, rot=200, energy=3.0, color=(1,0.92,0.8), angle=2.0):
    d=bpy.data.lights.new('sun','SUN'); d.energy=energy; d.color=color; d.angle=math.radians(angle)
    o=bpy.data.objects.new('sun',d); bpy.context.scene.collection.objects.link(o)
    o.rotation_euler=(math.radians(90-el),0,math.radians(rot)); return o
def point(loc,color,energy,radius=0.5):
    d=bpy.data.lights.new('pt','POINT'); d.energy=energy; d.color=color; d.shadow_soft_size=radius
    o=bpy.data.objects.new('pt',d); bpy.context.scene.collection.objects.link(o); o.location=loc; return o
def ground(size, m, loc=(0,0,0)):
    bpy.ops.mesh.primitive_plane_add(size=size,location=loc); o=bpy.context.active_object; o.data.materials.append(m); return o
def noise_mat(name,c1,c2,scale=0.05,rough=0.8,bump=0.3,voronoi=False):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; b=nt.nodes['Principled BSDF']
    tc=nt.nodes.new('ShaderNodeTexCoord')
    n=nt.nodes.new('ShaderNodeTexVoronoi' if voronoi else 'ShaderNodeTexNoise'); n.inputs['Scale'].default_value=scale
    nt.links.new(tc.outputs['Object'],n.inputs['Vector'])
    r=nt.nodes.new('ShaderNodeValToRGB'); r.color_ramp.elements[0].color=(*c1,1); r.color_ramp.elements[1].color=(*c2,1)
    nt.links.new(n.outputs['Distance' if voronoi else 'Fac'],r.inputs['Fac']); nt.links.new(r.outputs['Color'],b.inputs['Base Color'])
    b.inputs['Roughness'].default_value=rough
    bp=nt.nodes.new('ShaderNodeBump'); bp.inputs['Strength'].default_value=bump
    nt.links.new(n.outputs['Distance' if voronoi else 'Fac'],bp.inputs['Height']); nt.links.new(bp.outputs['Normal'],b.inputs['Normal'])
    return m
def camera(lens=24):
    c=bpy.data.cameras.new('cam'); c.lens=lens; c.clip_start=0.5; c.clip_end=5000
    o=bpy.data.objects.new('cam',c); bpy.context.scene.collection.objects.link(o); bpy.context.scene.camera=o; return o
def look(cam, at):
    d=Vector(at)-cam.location; cam.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
def key_cam(cam, f, loc, at, lens=None):
    cam.location=loc; look(cam,at); cam.keyframe_insert('location',frame=f); cam.keyframe_insert('rotation_euler',frame=f)
    if lens: cam.data.lens=lens; cam.data.keyframe_insert('lens',frame=f)
def setup_render(w=720,h=1280,samples=16,f0=1,f1=24,fps=24,out='/tmp/claude-0/tv/out/x/'):
    s=bpy.context.scene; s.render.engine='CYCLES'; s.cycles.device='CPU'; s.cycles.samples=samples
    s.cycles.use_denoising=True
    try: s.cycles.denoiser='OPENIMAGEDENOISE'
    except Exception: pass
    s.cycles.max_bounces=4; s.cycles.diffuse_bounces=2; s.cycles.glossy_bounces=2; s.cycles.transmission_bounces=4
    s.render.resolution_x=w; s.render.resolution_y=h; s.render.resolution_percentage=100
    s.frame_start=f0; s.frame_end=f1; s.render.fps=fps
    s.render.image_settings.file_format='PNG'; s.render.filepath=out
    s.view_settings.view_transform='AgX'
    for lk in ('AgX - Punchy','Punchy','AgX - Medium High Contrast'):
        try: s.view_settings.look=lk; break
        except Exception: pass
    s.view_settings.exposure=-0.6
    s.render.use_motion_blur=False
def ease(t): return t*t*(3-2*t)
def comp(haze=(0.62,0.74,0.9), mist_start=120, mist_depth=1600, haze_amt=0.45, bloom=True, glare_thresh=0.9, glare_mix=0.0):
    s=bpy.context.scene; vl=s.view_layers[0]; vl.use_pass_mist=True
    if s.world:
        s.world.mist_settings.start=mist_start; s.world.mist_settings.depth=mist_depth; s.world.mist_settings.falloff='QUADRATIC'
    ng=bpy.data.node_groups.new('Comp','CompositorNodeTree'); s.compositing_node_group=ng
    ng.interface.new_socket('Image',in_out='OUTPUT',socket_type='NodeSocketColor')
    N=ng.nodes; L=ng.links
    rl=N.new('CompositorNodeRLayers')
    out=N.new('NodeGroupOutput')
    cur=rl.outputs['Image']
    if haze_amt>0:
        mul=N.new('ShaderNodeMath'); mul.operation='MULTIPLY'; mul.inputs[1].default_value=haze_amt
        L.new(rl.outputs['Mist'],mul.inputs[0])
        mx=N.new('ShaderNodeMix'); mx.data_type='RGBA'
        L.new(mul.outputs[0],mx.inputs['Factor']); L.new(cur,mx.inputs[6]); mx.inputs[7].default_value=(*haze,1)
        cur=mx.outputs[2]
    if bloom:
        g=N.new('CompositorNodeGlare')
        try: g.inputs['Type'].default_value='Bloom'
        except Exception as e: print('glare type',e)
        for k,v in (('Threshold',glare_thresh),('Strength',0.6),('Size',0.6)):
            if k in g.inputs: g.inputs[k].default_value=v
        L.new(cur,g.inputs['Image']); cur=g.outputs['Image']
    L.new(cur,out.inputs[0])
    return ng

def glow_mat(name,color,strength,alpha=0.5):
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree
    for n in list(nt.nodes):
        if n.bl_idname!='ShaderNodeOutputMaterial': nt.nodes.remove(n)
    o=[n for n in nt.nodes][0]
    e=nt.nodes.new('ShaderNodeEmission'); e.inputs['Color'].default_value=(*color,1); e.inputs['Strength'].default_value=strength
    t=nt.nodes.new('ShaderNodeBsdfTransparent'); mx=nt.nodes.new('ShaderNodeAddShader')
    nt.links.new(e.outputs[0],mx.inputs[0]); nt.links.new(t.outputs[0],mx.inputs[1]); nt.links.new(mx.outputs[0],o.inputs['Surface'])
    return m
def rope_curve(pts,m,radius=0.12):
    cd=bpy.data.curves.new('rope','CURVE'); cd.dimensions='3D'; cd.bevel_depth=radius
    sp=cd.splines.new('POLY'); sp.points.add(len(pts)-1)
    for i,p in enumerate(pts): sp.points[i].co=(*p,1)
    o=bpy.data.objects.new('rope',cd); bpy.context.scene.collection.objects.link(o); cd.materials.append(m); return o
