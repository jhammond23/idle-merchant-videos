from lib import *
def build_town(detail=True):
    random.seed(7)
    grass=noise_mat('grass',srgb(52,110,40),srgb(98,150,52),scale=0.03,bump=0.2)
    g=ground(1600,grass)
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.subdivide(number_cuts=60); bpy.ops.object.mode_set(mode='OBJECT')
    import mathutils.noise as mn
    for v in g.data.vertices:
        x,y=v.co.x,v.co.y; r=math.hypot(x,y)
        if r>90 and not (abs(x)<20 and y>0): v.co.z=mn.noise(Vector((x/180,y/180,0)))*14*min(1,(r-90)/120)+max(0,(r-300))*0.08
    stone=noise_mat('cobble',srgb(120,108,96),srgb(168,150,128),scale=0.9,rough=0.9,bump=0.6,voronoi=True)
    bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=34,depth=0.2,location=(0,0,0.1)); sq=bpy.context.active_object; sq.data.materials.append(stone)
    road=noise_mat('road',srgb(190,148,96),srgb(214,164,101),scale=0.1,bump=0.15)
    box('road',(14,600,0.16),(0,330,0.08),road)
    box('road2',(12,140,0.16),(0,-95,0.08),road)
    glb('a1_fountain',(0,0,0.2))
    glb('a1_guild_hall',(0,52,0))
    glb('a1_guild_noticeboard',(9,36,0.2),rot=-15)
    glb('a1_hero_hall',(-44,30,0),rot=-55)
    glb('a1_smithy',(46,30,0),rot=55)
    glb('a1_cottage_blue',(-50,-8,0),rot=-90)
    glb('a1_cottage_thatch',(50,-6,0),rot=90)
    glb('a1_cottage_timber',(-42,-44,0),rot=-130)
    glb('a1_stable_house',(44,-44,0),rot=130)
    glb('a1_cottage_blue',(-72,44,0),rot=-70)
    glb('a1_cottage_thatch',(72,46,0),rot=70)
    glb('a1_market_stall',(-20,-26,0.2),rot=-20)
    glb('a1_market_stall',(20,-26,0.2),rot=20)
    glb('a1_food_cart',(-27,8,0.2),rot=-80)
    glb('a1_roofed_well',(26,12,0.2),rot=30)
    for a in range(10):
        t=a/10*math.tau+0.3; glb('a1_town_lamp',(math.cos(t)*30,math.sin(t)*30,0.2),rot=math.degrees(t)+90)
    for p in [(-14,-14),(14,-14),(-10,20),(10,20)]: glb('a1_flower_planter',(p[0],p[1],0.2))
    glb('a1_barrel_stack',(-30,-20,0.2),rot=40); glb('a1_food_crates',(30,-18,0.2),rot=-30)
    glb('a1_raised_flower_box',(-34,22,0.2),rot=-60)
    # trees ring
    kinds=['oak_b','maple_red','pine_a','oak_b','pine_a_slender','birch_a','oak_ancient']
    for i in range(70):
        t=random.random()*math.tau; r=95+random.random()*170
        x,y=math.cos(t)*r,math.sin(t)*r
        if abs(x)<16 and y>40: continue
        k=random.choice(kinds); s=0.9+random.random()*0.5
        if k=='oak_ancient': s*=0.7
        glb(k,(x,y,0),rot=random.random()*360,scale=s)
    for i in range(30):
        t=random.random()*math.tau; r=60+random.random()*40
        glb(random.choice(['bush_a','flower_bush','hedge_bush']),(math.cos(t)*r,math.sin(t)*r,0),rot=random.random()*360)
    # road north: tree walls
    for i in range(40):
        y=120+i*12
        for side in (-1,1):
            glb(random.choice(['oak_b','pine_a','maple_red','pine_a_slender']),(side*(18+random.random()*14),y+random.random()*6,0),rot=random.random()*360,scale=0.9+random.random()*0.5)
    # far mountains (the Frostpeak peaks seen from town)
    for i,(x,y,s) in enumerate([(-260,900,5),(120,1000,6),(420,860,4.5),(-520,760,4),(650,700,4)]):
        glb('fp_snowpeak_b' if i%2 else 'fp_snowpeak_a',(x,y,-5),rot=i*47,scale=s)
def lantern_strings(y0,n,step=118,width=30):
    """Lantern Woods signature: poles 23 tall, 5 lanterns per string, sag 2.6 (Data/Regions)"""
    pole=mat('pole',srgb(96,66,40),0.8)
    rope=mat('rope',srgb(70,50,30),0.9)
    cols=[srgb(255,170,70),srgb(255,205,96),srgb(240,110,70)]
    lms=[mat('lan%d'%i,tuple(x*0.6 for x in c),0.4,emit=c,estr=2.2) for i,c in enumerate(cols)]
    for k in range(n):
        y=y0+k*step
        for x in (-width/2,width/2): box('pole',(0.8,0.8,23),(x,y,11.5),pole)
        pts=[]
        for j in range(21):
            u=j/20; x=-width/2+u*width; z=23-2.6*4*u*(1-u)
            pts.append((x,y,z))
        rope_curve(pts,rope)
        for j in range(5):
            u=(j+1)/6; x=-width/2+u*width; z=23-2.6*4*u*(1-u)-1.4
            bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8,location=(x,y,z),segments=12,ring_count=8)
            o=bpy.context.active_object; o.scale=(1,1,1.25); o.data.materials.append(lms[(j+k)%3])
            if j%2==0: point((x,y,z-0.5),(1,0.72,0.4),400,0.6)
