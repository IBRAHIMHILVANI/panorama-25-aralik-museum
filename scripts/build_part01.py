"""Part 01: source-photograph review of the entrance passage and central courtyard.

This is an editable, photo-informed reconstruction. All metre dimensions remain
estimates pending a measured plan. The source identifiers are embedded per mesh.
"""
from pathlib import Path
import math,json
import numpy as np
from museum_geometry import *
from museum_exhibits import emit_reference_prop

s=Scene('01_Courtyard_Entrance')
rng=np.random.default_rng(20261025)
s.mat('Basalt_Joints',(.18,.19,.18),.91)
for i in range(9):s.mat(f'Basalt_Paver_{i}',(.255+i*.012,.263+i*.011,.257+i*.010),.83)
for i in range(7):s.mat(f'Entry_Paver_{i}',(.44+i*.017,.445+i*.017,.42+i*.017),.84)
s.mat('Stone_Grey',(.30,.31,.30),.88)
s.mat('Stone_Grey_Light',(.43,.435,.415),.85)
s.mat('Limestone',(.68,.635,.51),.82)
for i in range(6):s.mat(f'Limestone_{i}',(.65+i*.014,.60+i*.014,.47+i*.015),.85)
s.mat('Metal_Charcoal',(.055,.066,.072),.45,.45)
s.mat('Metal_Bronze',(.30,.27,.17),.35,.7)
s.mat('Glass_Smoke',(.19,.27,.29),.16,.25,.23)
s.mat('Glass_Dark',(.09,.14,.16),.23,.32)
s.mat('Interior_Shadow',(.105,.105,.095),.9)
s.mat('Lettering',(.82,.83,.78),.53,.2)
s.mat('Wood_Seat',(.17,.135,.10),.72)
s.mat('Tree_Bark',(.28,.24,.17),.95)
for i in range(6):s.mat(f'Foliage_{i}',(.12+i*.025,.18+i*.024,.055+i*.009),.95)
s.mat('Soil',(.21,.18,.12),.99)
s.mat('Flag_Red',(.57,.018,.027),.9)
s.mat('Flag_White',(.91,.90,.83),.85)
s.mat('Bin_Blue',(.03,.22,.34),.43,.35)
s.mat('Lamp',(.92,.85,.65),.4,emission=.5)

def addbox(name,loc,size,mat,refs='1935-1941',collide=False,bevel=0,yaw=0):
    s.add(name,box(loc,size,yaw,bevel),mat,refs,collision=collide)

def wall_strip(name,a,b,z0,z1,thick=.18,mat='Stone_Grey',collision=True):
    a=np.array(a);b=np.array(b);mid=(a+b)/2
    addbox(name,[*mid,(z0+z1)/2],[float(np.linalg.norm(b-a)),thick,z1-z0],mat,collide=collision,yaw=math.atan2(b[1]-a[1],b[0]-a[0]))

# Walkable slabs are separate from decorative pavers, avoiding collision seams.
for name,bounds,z in [('Arrival',(-9,9,-29,-22.0),-1.60),('Passage',(-4.2,4.2,-18,11),0),('Court',(-6.4,23,11,44),0),('West_Exit',(-10,-6.4,28,35),0),('North_Exit',(-5,3,44,51),0),('Door_Approach',(17.7,25,11,16),0)]:
    x0,x1,y0,y1=bounds
    s.add('NAV_'+name,plane_xy(x0,x1,y0,y1,z),'Basalt_Joints',collision=True,hidden=True)
    addbox(name+'_Slab',[(x0+x1)/2,(y0+y1)/2,z-.10],[x1-x0,y1-y0,.20],'Basalt_Joints')
    step=.65 if name!='Passage' else .58
    for j,y in enumerate(np.arange(y0,y1,step)):
        for i,x in enumerate(np.arange(x0,x1,.85)):
            w=min(.85,x1-x)-.009;h=min(step,y1-y)-.009
            if w<.01 or h<.01:continue
            mat=f'Entry_Paver_{rng.integers(7)}' if name in ['Arrival','Passage'] else f'Basalt_Paver_{rng.integers(9)}'
            s.batch(name+'_Pavers_'+mat,box((x+w/2,y+h/2,z+.009),(w,h,.03),bevel=.006),mat,'1935-1941')
# Google Street View October 2024 shows a broad exterior stair with about ten risers.
# Rise and run are photo-estimated; the original three-step placeholder was removed.
for i in range(10):
    top=-1.44+i*.16;addbox(f'Arrival_Step_{i+1}',(0,-21.8+i*.4,(top-1.6)/2),(8.4,.4,top+1.6),'Stone_Grey_Light',refs='Google Street View October 2024, entrance observation 13; dimensions estimated')
    s.batch('Step_Nosings',box((0,-21.985+i*.4,top+.006),(8.35,.045,.012)),'Metal_Charcoal')
s.add('NAV_Arrival_Step_Ramp',Mesh().append([[-4.2,-22,-1.6],[4.2,-22,-1.6],[4.2,-18,0],[-4.2,-18,0]],[[0,1,2,3]]),'Basalt_Joints',collision=True,hidden=True)
for x in [-3.7,1.65,3.7]:
    for y in np.linspace(-21.8,-18.15,5):
        z=-1.6+(y+22)*.4;s.batch('Arrival_Handrail_Posts',cylinder((x,y,z),(x,y,z+.91),.025,segments=10),'Metal_Bronze','Street View 2024',collision=True)
    s.add('Arrival_Handrail_'+str(x),cylinder((x,-22.15,-.75),(x,-17.65,.99),.027,segments=12),'Metal_Bronze','Street View 2024',collision=True)
for x in [-5.2,5.2]:addbox('Entrance_Raised_Planter_'+str(x),(x,-18.9,-.40),(1.6,3.1,.80),'Stone_Grey',refs='Street View 2024',collide=True)
from museum_landscape import leafy_shrub
for side,x in enumerate([-5.2,5.2]):
    addbox('Entrance_Planter_Soil_'+str(side),(x,-18.9,.008),(1.44,2.94,.025),'Soil')
    for k,y in enumerate([-19.7,-19.0,-18.3]):leafy_shrub(s,'Entrance_Hedges',(x,y,.025),1.15,.80,.53,seed=1935+side*8+k)
    leafy_shrub(s,'Entrance_Conical_Shrub',(x,-18.2,.025),.62,.62,1.48,seed=1941+side,conical=True)
emit_reference_prop(s,old.cannon,('Entrance_Cannon',(0,0,0),0,'Google Street View October 2024'),(-2.4,-16.9,.03),math.pi,'Street View 2024 entrance observation','Exterior',1,omit=('_Shield',))
s.add('NAV_Entrance_Cannon',box((-2.4,-16.9,.90),(1.9,4.0,1.8)),'Metal_Charcoal','Street View 2024',collision=True,hidden=True)

# Front facade returns and fixed museum lettering visible in October 2024 Street View.
addbox('Exterior_Left_Facade_Return',(-7.7,-18.12,1.65),(6.6,.24,6.5),'Stone_Grey',refs='Google Street View October 2024 entrance observation',collide=True)
addbox('Exterior_Right_Facade_Return',(7.4,-18.12,1.75),(6.1,.24,6.7),'Stone_Grey',refs='Google Street View October 2024 entrance observation',collide=True)
from museum_identity import municipality_logo,panorama_logo,turkish_flag
panorama_logo(s,'Exterior_Panorama_Original_Artwork',(-7.5,-18.27,2.10),3.30)

# Entrance passage: left glazing, grey stone walls, high right clerestory.
wall_strip('Entry_Left_Upper',(-4.34,-18),(-4.34,9.6),2.70,6.8,.30,'Stone_Grey_Light')
wall_strip('Entry_Right_Base',(4.34,-18),(4.34,9.6),0,5.2,.30,'Stone_Grey')
wall_strip('Entry_Right_Clerestory_Sill',(4.34,-18),(4.34,8.8),5.2,5.42,.30,'Stone_Grey_Light')
wall_strip('Entry_Right_Parapet',(4.34,-18),(4.34,8.8),6.68,7.15,.30,'Stone_Grey_Light')
for i,y in enumerate(np.arange(-17.2,9,1.45)):
    addbox(f'Entry_Left_Glass_{i}',(-4.16,y,1.34),(.035,1.395,2.56),'Glass_Smoke',collide=True)
    s.batch('Entry_Left_Mullions',box((-4.125,y-.72,1.36),(.07,.045,2.7)),'Metal_Bronze','1935')
    addbox(f'Entry_Left_Interior_{i}',(-5.6,y,1.3),(2.5,1.4,2.6),'Interior_Shadow')
    addbox(f'Entry_Right_Clerestory_{i}',(4.32,y,6.03),(.035,1.39,1.2),'Glass_Dark')
    s.batch('Entry_Right_Upper_Mullions',box((4.25,y-.72,6.05),(.08,.055,1.26)),'Metal_Charcoal','1935')
# Panel joints on passage walls follow the visible modular cladding.
for z in [2.72,4.02,5.34,6.7]:
    s.batch('Passage_Stone_Horizontal_Joints',box((-4.168,-4.2,z),(.008,27.6,.015)),'Metal_Charcoal','1935')
for x in [-4.168,4.168]:
    for y in np.arange(-18,10,1.4):
        s.batch('Passage_Stone_Vertical_Joints',box((x,y,4.65 if x<0 else 2.6),(.012,.013,3.9 if x<0 else 5.2)),'Metal_Charcoal','1935')
# The open portal is deliberately a real hole, with no glass or collider across it.
addbox('Court_Entry_Portal_Canopy',(0,9.9,3.56),(8.8,2.6,.40),'Metal_Charcoal',collide=True)
addbox('Court_Entry_Portal_Header',(0,8.63,3.88),(8.8,.12,.88),'Metal_Charcoal')
municipality_logo(s,'Portal_Official_Municipality_Logo',(0,8.54,3.48),2.32)
for x in [-4.25,4.25]:addbox('Portal_Jamb_'+str(x),(x,9.8,1.63),(.26,2.6,3.26),'Stone_Grey',collide=True)

# Turkish flags visible in the user's entrance photograph; non-repeating cloth folds.
def flagcloth(center,width=.60,height=.90,phase=0):
    turkish_flag(s,'Entrance_Flag',center,width,height,phase=phase,vertical=True)
for j,y in enumerate(np.linspace(-16,8,11)):
    z=5.75-.035*j
    s.batch('Flag_Support_Cables',cylinder((-4.2,y,z),(4.2,y,z+.10),.008,segments=6),'Metal_Charcoal','1935')
    for i,x in enumerate(np.linspace(-3.7,3.7,10)):flagcloth((x,y,z+.10*(x+4.2)/8.4),phase=j+i)

# Curved inner facade of the right wing, with shop glazing below and upper windows.
CC=(-6.,23.5);CR=29.
angles=np.linspace(math.radians(-28),math.radians(48),31)
for i,(a0,a1) in enumerate(zip(angles,angles[1:])):
    amid=(a0+a1)/2
    s.add(f'Court_Right_Low_Fascia_{i}',arc_band(CC,CR,CR+.32,a0,a1,2.65,3.38,2),'Metal_Charcoal','1936,1941',collision=True)
    # Continuous upper elevation, except the observed ribbon-window openings.
    window= i in list(range(10,17))+list(range(21,28))
    spans=[(3.38,4.55),(6.05,8.25)] if window else [(3.38,8.25)]
    for j,(z0,z1) in enumerate(spans):
        s.add(f'Court_Right_Stone_{i}_{j}',arc_band(CC,CR,CR+.32,a0+.001,a1-.001,z0,z1,2),f'Limestone_{i%6}','1941',collision=True)
    if window:
        s.add(f'Court_Right_Window_{i}',arc_band(CC,CR+.07,CR+.09,a0+.001,a1-.001,4.56,6.04,2),'Glass_Dark','1941')
        p=[CC[0]+CR*math.cos(a0),CC[1]+CR*math.sin(a0)]
        s.batch('Court_Right_Window_Mullions',cylinder([*p,4.55],[*p,6.05],.022,segments=8),'Metal_Charcoal','1941')
    # An open doorway is retained near the photographed passage/courtyard join.
    door=i in [1,2]
    if not door:
        s.add(f'Court_Right_Shop_Glazing_{i}',arc_band(CC,CR+.04,CR+.07,a0+.001,a1-.001,.12,2.64,2),'Glass_Smoke','1936,1941',collision=True)
        s.add(f'Court_Right_Shop_Back_{i}',arc_band(CC,CR+1.4,CR+1.55,a0,a1,0,2.65,2),'Interior_Shadow','1936,1941')
    if not door:s.add(f'Court_Right_Shop_Base_{i}',arc_band(CC,CR,CR+.35,a0,a1,0,.12,2),'Stone_Grey','1936,1941')
    p=[CC[0]+CR*math.cos(a0),CC[1]+CR*math.sin(a0)]
    if not door:s.batch('Court_Right_Shop_Frames',cylinder([*p,.12],[*p,2.65],.028,segments=8),'Metal_Bronze','1936,1941')
    # Small stone seams and real facade relief are retained as geometry.
    for z in [4.55,6.05,7.15]:
        s.batch('Court_Right_Horizontal_Cladding_Joints',arc_line(CC,CR-.002,a0,a1,z,.007,2),'Stone_Grey','1941')

# Left curved gallery storefront and an actual open exit passage.
for i,y in enumerate(np.arange(12,42,1.45)):
    xx=-6.7-.045*(y-12)
    # Shared building boundary: storefront cannot cut through the panorama canvas.
    # Keep the photographed facade sequence, resolving its provisional global alignment.
    closest_y=min(max(13.,y-.73),y+.73)
    if abs(closest_y-13)<20.25:
        panorama_edge=-26+math.sqrt(20.25**2-(closest_y-13)**2)
        xx=max(xx,panorama_edge+.34)
    exitdoor=28<y<31.5
    if not exitdoor:
        addbox(f'Court_Left_Glass_{i}',(xx,y,1.3),(.04,1.40,2.5),'Glass_Smoke',collide=True)
        addbox(f'Court_Left_Interior_{i}',(xx-.16,y,1.25),(.20,1.4,2.5),'Interior_Shadow',refs='1939,1940; shallow unmodeled shop backing, kept outside panorama canvas')
    s.batch('Court_Left_Mullions',box((xx+.028,y-.72,1.28),(.055,.04,2.56)),'Metal_Bronze','1939,1940')
    addbox(f'Court_Left_Stone_Fascia_{i}',(xx,y,3.01),(.32,1.45,.87),'Stone_Grey_Light',collide=True)
s.text('West_Exit_Label','ÇIKIŞ',(-7.30,29.9,2.9),.24,rotation=(math.pi/2,0,math.pi/2))
# Northern shops and the two photographed outward passages.
for i,x in enumerate(np.arange(-8,15,1.3)):
    passage=-4.5<x<-1 or 5.8<x<8.5
    if not passage:
        addbox(f'North_Shop_Glass_{i}',(x,44.0,1.3),(1.25,.04,2.5),'Glass_Smoke',collide=True)
        addbox(f'North_Shop_Interior_{i}',(x,45.0,1.3),(1.30,1.8,2.6),'Interior_Shadow')
    s.batch('North_Shop_Mullions',box((x-.64,43.96,1.3),(.055,.06,2.6)),'Metal_Charcoal','1936,1940')
addbox('North_Shops_Canopy',(3,44.8,3.0),(26,3,.32),'Metal_Charcoal')
addbox('North_Shops_Header',(3,43.33,3.26),(26,.14,.60),'Metal_Charcoal')
s.text('North_Exit_Fedai','FEDAİ MEHMET\nÇIKIŞI',(-2.8,43.245,3.15),.16)
s.text('North_Exit_Dayi','DAYI AHMET AĞA\nÇIKIŞI',(7.1,43.245,3.15),.16)
s.text('North_Shop_Atalar','ATALAR\nANTİKA',(10.8,43.92,2.3),.18)

# Seat/planter configurations and trees correspond to the four visible tree groups.
trees=[(3.6,21.0,10.0,1.0),(8.9,28.6,9.0,1.35),(-2.9,37.0,10.3,.72),(15.8,32.5,5.8,.8)]
def tree(idx,x,y,height,spread):
    s.add(f'Tree_{idx}_Trunk',cylinder((x,y,.05),(x+.10,y-.08,height*.78),.26 if idx!=3 else .17,.10,18),'Tree_Bark','1936-1941',smooth=True)
    s.add(f'NAV_Tree_{idx}',cylinder((x,y,0),(x,y,height*.75),.29,segments=10),'Tree_Bark',collision=True,hidden=True)
    for j in range(16):
        a=rng.uniform(0,TAU);z=rng.uniform(height*.4,height*.88);r=spread*rng.uniform(.55,1.75)
        p=(x+r*math.cos(a),y+r*math.sin(a),z+.7)
        s.batch('Tree_Branches',cylinder((x,y,z-.5),p,.05,.015,8),'Tree_Bark','1936-1941',True)
    # Batched leaves with a tapered canopy silhouette, preserving gaps and branches.
    for j in range(10000 if idx<3 else 6500):
        z=rng.uniform(height*.40,height*1.03);t=(z-height*.40)/(height*.63)
        rad=spread*(1.6*math.sin(math.pi*min(t,.999))**.6+.2)
        a=rng.uniform(0,TAU);r=rad*math.sqrt(rng.random());p=(x+r*math.cos(a),y+r*math.sin(a),z)
        mat=f'Foliage_{int(rng.integers(3,6) if idx==3 else rng.integers(0,6))}'
        s.batch('Tree_Leaves_'+mat,sphere_leaf(p,(rng.uniform(.055,.115),rng.uniform(.025,.048)),rng.uniform(0,TAU)),mat,'1936-1941')
for i,(x,y,h,spread) in enumerate(trees):
    addbox(f'Tree_{i}_Soil',(x,y,.065),(1.03,1.03,.10),'Soil')
    for j,(dx,dy,w,d) in enumerate([(-.71,0,.4,1.82),(.71,0,.4,1.82),(0,-.71,1.05,.4),(0,.71,1.05,.4),(-1.95,-.50,2.15,.80),(1.43,.70,1.28,.82)]):
        addbox(f'Planter_{i}_Seat_{j}',(x+dx,y+dy,.215),(w,d,.43),'Stone_Grey',collide=True,bevel=.018)
        for k in np.arange(-d/2+.025,d/2,.065):
            s.batch('Seat_Wood_Slats',box((x+dx,y+dy+k,.444),(w-.025,.052,.028),bevel=.007),'Wood_Seat','1936-1941')
    tree(i,x,y,h,spread)
    for j in range(15):
        a=rng.uniform(0,TAU);r=rng.uniform(.9,2.7)
        s.batch('Fallen_Leaves',sphere_leaf((x+r*math.cos(a),y+r*math.sin(a),.009),(.055,.025),a),'Limestone_0','1936,1940')

# Trench drains surround the planted seating group, as clearly visible in IMG_1940.
for name,a,b in [('Front',(-1,17.1),(13.2,17.1)),('Left',(-1,17.1),(-1,36.5)),('Back',(-1,36.5),(13.2,36.5)),('Right',(13.2,17.1),(13.2,36.5))]:
    av=np.array(a);bv=np.array(b);d=bv-av;length=np.linalg.norm(d);yaw=math.atan2(d[1],d[0]);mid=(av+bv)/2
    s.batch('Drain_Channels',box((*mid,.003),(length,.18,.012),yaw),'Metal_Charcoal','1936,1940')
    for t in np.arange(0,length,.055):
        p=av+d*t/length;s.batch('Drain_Grates',box((*p,.012),(.018,.17,.015),yaw),'Stone_Grey','1936,1940')
for i,(x,y) in enumerate([(5.7,30),(16,29),(-3.6,40),(3.4,10.7)]):
    addbox(f'Bin_{i}_Body',(x,y,.49),(.38,.34,.82),'Metal_Charcoal',collide=True,bevel=.035)
    addbox(f'Bin_{i}_Blue_Lid',(x,y,.93),(.41,.37,.06),'Bin_Blue',bevel=.02)
    s.batch('Bin_Handles',join(cylinder((x-.20,y,.9),(x-.20,y,1.22),.018,segments=10),cylinder((x+.20,y,.9),(x+.20,y,1.22),.018,segments=10),torus((x,y,1.22),.20,.018,(0,1,0),20,6)),'Metal_Charcoal','1936,1940')

# The courtyard's cafe facade and a reviewable double-door opening.
s.text('Havara_Name','HAVARA',(20.55,32.8,2.20),.44,rotation=(math.pi/2,0,math.radians(-18)))
da=math.radians(-23);dv=np.array([math.cos(da),math.sin(da)]);dt=np.array([-math.sin(da),math.cos(da)]);dc=np.array(CC)+CR*dv;dyaw=da+math.pi/2
for sign,side in [(-1,'Left'),(1,'Right')]:
    p=dc+sign*1.28*dt
    addbox('Door_'+side+'_Jamb',(*p,1.45),(.13,.20,2.9),'Metal_Charcoal',collide=True,yaw=dyaw)
addbox('Door_Head',(*dc,2.87),(2.68,.20,.14),'Metal_Charcoal',yaw=dyaw)
# Leaves are opened so the review route passes through a genuine geometric opening.
for side,sign in [('L',-1),('R',1)]:
    a=dyaw+math.radians(-sign*82)
    hinge=dc+sign*1.20*dt;pos=(*list(hinge-sign*.59*np.array([math.cos(a),math.sin(a)])),1.42)
    addbox('Door_Open_Leaf_'+side,pos,(1.18,.045,2.72),'Glass_Smoke',yaw=a)
    s.batch('Door_Leaf_Frame',box((pos[0],pos[1],.07),(1.2,.06,.08),a),'Metal_Bronze','1935-1941')
s.add('NAV_Door_Landing',plane_xy(17,26,8,16.2,0),'Basalt_Joints',collision=True,hidden=True)
addbox('Door_Interior_Landing',(23,12,-.08),(6,8,.16),'Basalt_Joints')
for label,a,b in [('Site_South',(-10,-29),(26,-29)),('Site_East',(26,-29),(26,51)),('Site_North',(-10,51),(26,51)),('Site_West',(-10,-29),(-10,51))]:
    av=np.array(a);bv=np.array(b);mid=(av+bv)/2
    s.add('NAV_Boundary_'+label,box((*mid,1.2),(float(np.linalg.norm(bv-av)),.1,4),math.atan2(bv[1]-av[1],bv[0]-av[0])),'Metal_Charcoal',collision=True,hidden=True)

# Context massing is explicitly separate from the detailed reviewed courtyard.
for i,(a0,a1) in enumerate(zip(np.linspace(-math.pi,.90,65),np.linspace(-math.pi,.90,65)[1:])):
    s.batch('Context_Rotunda_Cladding',arc_band((-26,13),19.9,20.15,a0,a1,4.2,14.5,3),f'Limestone_{i%6}','architect facade; placement estimated')
s.add('Context_Rotunda_Base',arc_band((-26,13),19.6,20.2,-math.pi,.90,-1.6,4.2,100),'Stone_Grey','architect facade; placement estimated')
# Actual panorama mark on the station-facing limestone drum. Curved placement is estimated.
from museum_identity import artwork
front_angle=math.radians(-50)
for layer,mat in [('red','Identity_Panorama_red'),('white','Identity_Panorama_Dark')]:
    if mat=='Identity_Panorama_Dark':s.mat(mat,(.055,.05,.045),.78)
    logo,_=artwork('panorama-logo.png',layer,6.40);verts=np.asarray(logo.vertices)
    for p in verts:
        a=front_angle+p[0]/20.18;p[:]=[-26+20.18*math.cos(a),13+20.18*math.sin(a),7.45+p[2]]
    logo.vertices=verts.tolist();s.add('Rotunda_Panorama_Original_Logo_'+layer,logo,mat,'Museum Google Maps owner photo March 2021; published original logo artwork','Original logo outline; metric facade position remains estimated')
# Low pitched neighbouring roofs are context only; no claim of facade survey.
for i,(x,y,w,d,h) in enumerate([(-5,48,5,4,4.8),(2,50,5,5,5.2),(10,50,4,5,4.7)]):
    addbox(f'Context_Back_Block_{i}',(x,y,h/2),(w,d,h),'Stone_Grey_Light',refs='1936,1940; context estimate')

s.views=[
 {'id':'arrival','title':'بداية المدخل','position':[0,-25,.05],'target':[0,10,1.7],'photo':1935},
 {'id':'passage','title':'ممر الأعلام','position':[0,-9,1.65],'target':[0,22,1.8],'photo':1935},
 {'id':'portal','title':'من تحت المدخل','position':[.2,9.2,1.65],'target':[6.6,29,2.7],'photo':1936},
 {'id':'courtyard','title':'الساحة والأشجار','position':[0,17,1.65],'target':[6,31,2.5],'photo':1940},
 {'id':'rightwing','title':'الواجهة المنحنية','position':[7,23,1.65],'target':[21.5,30,4.0],'photo':1941},
 {'id':'door','title':'فتحة الباب','position':[*list(dc-3*dv),1.65],'target':[*list(dc+3*dv),1.5],'photo':1935},
 {'id':'above','title':'نظرة من الأعلى','position':[7,-15,35],'target':[4,23,0],'photo':1936,'mode':'fly'}]
s.views.extend([{'id':'rotundalogo','title':'شعار بانوراما من جهة الترام','position':[-13,-22,2.0],'target':[-13,-2,9.3],'mode':'fly'},{'id':'flagdetail','title':'العلم وشعار البلدية عن قرب','position':[0,5.5,3.6],'target':[0,8.6,4.1],'mode':'fly'}])
s.save(ROOT/'reconstruction/part01-scene.json')
(ROOT/'reconstruction/part01-notes.json').write_text(json.dumps({
 'title':'الساحة الوسطية وممر الدخول', 'stage':'draft for joint visual review',
 'source_photos':['IMG_1935','IMG_1936','IMG_1937','IMG_1938','IMG_1939','IMG_1940','IMG_1941'],
 'observed':['Original municipality wordmark and museum logo silhouettes','Vertical 2:3 Turkish flags with source SVG crescent/star geometry','Entry glazing and grey wall cladding','Hanging Turkish flags','Open entry portal','Central tree planters with wooden seats','Trench drains','Curved upper limestone facade and ribbon windows','Shopfronts and named exits'],
 'unverified':['All dimensions are estimates','Global footprint and tree spacing are inferred from perspective photographs','The main interior doorway location and swing are provisional; missing photos IMG_1942 through IMG_1945 prevent confirming the transition','Exterior stair now follows the ten-rise interpretation of October 2024 Street View; exact rise/run remain unmeasured'],
 'accuracy_100_percent':False
 },indent=2,ensure_ascii=False))
