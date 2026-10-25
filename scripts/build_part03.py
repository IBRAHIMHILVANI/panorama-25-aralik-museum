"""Photo-informed archives and exhibit hall, IMG_1978–2080.

The route connects to the approved review model; it is not a surveyed floor plan.
Original document text is UV sampled. Props are editable simplified reconstructions.
"""
from museum_geometry import *
from museum_exhibits import *
from part03_figure_sources import FIGURES
ASSET_FILE=ROOT/'reconstruction/generated-assets.json'
GENERATED=json.loads(ASSET_FILE.read_text()) if ASSET_FILE.exists() else {}
def exhibit_figure(name,key,position,yaw,height,ref,outline,back_color=(.17,.18,.16)):
    asset=GENERATED.get(key)
    if asset and (ROOT/asset['path']).exists():s.asset(name,asset['path'],position,yaw-math.pi/2,height,ref,'Full 3D reconstruction from source photo; side/back and fine details inferred')
    else:source_display_figure(s,name,ref,outline,position,yaw,height=height,back_color=back_color)
from shapely.geometry import Polygon,box as rect

s=Scene('03_Archives_Uniforms_Weapons');rng=np.random.default_rng(19782080)
C=np.array([-6.,23.5]);F=-4.2;H=3.7;AEND=62.;RO=45.
def rad(a):return math.radians(a)
def xy(r,a):return C+r*np.array([math.cos(rad(a)),math.sin(rad(a))])
def xyz(r,a,z):return (*xy(r,a),z)
def inner(a):return 38 if a<=20 else 38-(a-20)*5/6 if a<26 else 33
def sector(ri,ro,a0,a1,n=96):
    return Polygon([xy(ro,a) for a in np.linspace(a0,a1,n+1)]+[xy(ri(a) if callable(ri) else ri,a) for a in np.linspace(a1,a0,n+1)])
def cube(name,p,d,mat,refs='',yaw=0,collision=False):s.add(name,box(p,d,yaw),mat,refs,collision=collision)
def batchbox(name,p,d,mat,refs='',yaw=0):s.batch(name,box(p,d,yaw),mat,refs)
def linewall(name,a,b,z0,z1,thickness,mat,refs='',collision=True):
    a=np.asarray(a);b=np.asarray(b);mid=(a+b)/2;cube(name,(*mid,(z0+z1)/2),(np.linalg.norm(b-a),thickness,z1-z0),mat,refs,math.atan2(b[1]-a[1],b[0]-a[0]),collision)
def ring(name,r0,r1,a0,a1,z0,z1,mat,refs='',collision=False):
    s.add(name,arc_band(C,r0,r1,rad(a0),rad(a1),z0,z1,max(8,int((a1-a0)*3))),mat,refs,collision=collision)
def annular_face(name,r,a0,a1,z0,z1,mat,refs='',collision=False):
    # A single transparent surface avoids doubled coplanar glass faces.
    m=Mesh();aa=np.linspace(rad(a0),rad(a1),max(9,int((a1-a0)*3)))
    for a,b in zip(aa,aa[1:]):
        m.append([[C[0]+r*math.cos(t),C[1]+r*math.sin(t),z] for t,z in [(a,z0),(b,z0),(b,z1),(a,z1)]],[[0,1,2,3]])
    s.add(name,m,mat,refs,collision=collision)
def wall_photo(name,n,w,h,r,a,z,quad=None,crop=(0,0,1,1),frame='Black_Frame',inward=True):
    # A flat panel must fit fully inside the curved outer wall, including its corners.
    if inward:r=min(r,math.sqrt((RO-.08)**2-(w/2+.08)**2)-.10)
    p=xy(r,a);yaw=rad(a)-math.pi/2 if inward else rad(a)+math.pi/2
    m=projected_panel(w,h,quad) if quad else panel(w,h,crop)
    s.add(name,m.transformed((*p,z),yaw),photo_material(s,n),str(n),'unchanged original photo, perspective UV fitted to a flat exhibit')
    local=box((0,.055,h/2),(w+.1,.09,h+.1)).transformed((*p,z),yaw)
    s.add(name+'_Frame',local,frame,str(n),collision=True)
    return p,yaw

for name,col,rough,metal,alpha,emit in [
 ('Wall_Gray',(.42,.43,.40),.84,0,1,.08),('Floor_Base',(.23,.24,.22),.66,0,1,0),
 ('Ceiling_Dark',(.045,.05,.048),.93,0,1,0),('Ceiling_Steel',(.12,.13,.125),.62,.4,1,0),
 ('Exhibit_Iron',(.18,.195,.20),.43,.50,1,0),('Exhibit_Wood',(.46,.27,.12),.56,0,1,0),
 ('Exhibit_Brass',(.56,.40,.17),.36,.65,1,0),('Exhibit_Leather',(.16,.085,.045),.67,0,1,0),
 ('Case_Base',(.34,.345,.315),.64,0,1,.08),('Case_Interior',(.61,.59,.52),.82,0,1,.15),
 ('Case_White_Edge',(.72,.73,.66),.56,0,1,.05),('Black_Frame',(.026,.029,.027),.44,.15,1,0),
 ('Wood_Frame',(.29,.14,.075),.56,0,1,0),('Gold_Frame',(.49,.32,.12),.42,.35,1,0),
 ('Glass_Exhibit',(.70,.82,.79),.10,.05,.075,0),('Glass_Edge',(.35,.49,.44),.2,.35,.55,0),
 ('Light_Linear',(.98,.90,.69),.4,0,1,2.5),('Mannequin_Black',(.085,.09,.09),.38,0,1,.025),
 ('Helmet_Cream',(.69,.61,.43),.85,0,1,.08),('Fez_Red',(.48,.027,.035),.9,0,1,0),
 ('Helmet_Blue',(.15,.23,.29),.45,.3,1,.05),('Fur_Dark',(.14,.14,.13),1,0,1,.05),
 ('Shoe_Red',(.58,.055,.035),.67,0,1,0),('Cloth_Cream',(.66,.61,.48),.95,0,1,.05),
 ('Paper_Edge',(.72,.65,.46),.95,0,1,.12),('Sculpture_Gray',(.36,.38,.37),.82,0,1,.08),
 ('Lettering',(.82,.83,.76),.7,0,1,.05),('Exit_Green',(.025,.34,.10),.5,0,1,.4)]:
    s.mat(name,col,rough,metal,alpha,emit)
for i in range(6):s.mat('Floor_Stone_'+str(i),(.25+i*.012,.255+i*.012,.24+i*.011),.62)

# Continuous floor and the physical link out of the map hall.
floor=sector(inner,RO,0,AEND)
s.add('Archives_Gallery_Floor',polygon_plate(floor,F),'Floor_Base','1984-1986,2031-2046',collision=True)
bridge=Polygon([(30.1,22.45),(35.9,22.45),(39,23.5),(32,23.5)])
s.add('Archives_Entry_Bridge',polygon_plate(bridge,F),'Floor_Base','connection unmeasured',collision=True)
for i,(a,b) in enumerate([((30.1,22.45),(32,23.5)),((35.9,22.45),(39,23.5))]):linewall('Entry_Bridge_Wall_'+str(i),a,b,F,F+H,.16,'Wall_Gray','connection unmeasured')
s.add('Entry_Bridge_Ceiling',polygon_plate(bridge,F+H,False),'Ceiling_Dark')
# Stone slabs are actual geometry, clipped to the room perimeter and batched by material.
mnx,mny,mxx,mxy=floor.bounds
for row,y in enumerate(np.arange(mny,mxy,1.15)):
    for col,x in enumerate(np.arange(mnx-.8,mxx,.82)):
        x+=.41*(row%2);cell=rect(x+.003,y+.003,x+.817,y+1.147).intersection(floor)
        if cell.is_empty or cell.area<1e-5:continue
        for poly in ([cell] if cell.geom_type=='Polygon' else cell.geoms):
            if poly.area>1e-5:s.batch('Stone_Slabs',polygon_plate(poly,F+.003),'Floor_Stone_'+str((row*5+col*3)%6),'1985,2031,2046')
ring('Outer_Gallery_Wall',45,45.22,0,AEND,F,F+H,'Wall_Gray','1984-2046',True)
for i,(a,b) in enumerate(zip(np.linspace(0,AEND,100),np.linspace(0,AEND,100)[1:])):
    linewall('Inner_Gallery_Wall_'+str(i),xy(inner(a)-.08,a),xy(inner(b)-.08,b),F,F+H,.16,'Wall_Gray','gallery curve approximate')
s.add('Gallery_Black_Ceiling',polygon_plate(floor,F+H,False),'Ceiling_Dark','1984,2031,2046')
for a in np.arange(2,AEND,5.8):
    r0=inner(a)+.1;r1=44.9;p=(xy(r0,a)+xy(r1,a))/2
    batchbox('Ceiling_Transverse_Steel',(*p,F+H-.15),(r1-r0,.16,.30),'Ceiling_Steel','2031,2046',rad(a))
    batchbox('Ceiling_Beam_Flange',(*p,F+H-.31),(r1-r0,.30,.035),'Ceiling_Steel','2031,2046',rad(a))
    for r in [max(39,inner(a)+1),43.7]:
        p=xy(r,a);batchbox('Light_Track',(*p,F+3.02),(1.5,.045,.055),'Ceiling_Steel','2031,2046',rad(a)+math.pi/2)
        for da in [-.6,.6]:
            q=xy(r,a+da);s.batch('Track_Light_Housings',cylinder((*q,F+2.96),(*q,F+2.81),.06,segments=12),'Black_Frame','2031,2046')
            s.batch('Track_Light_Lenses',cylinder((*q,F+2.802),(*q,F+2.81),.048,segments=12),'Light_Linear','2031,2046')
    s.lights.append({'position':list(xyz(40.2,a,F+3.05)),'energy':64,'angle':118,'color':[1,.88,.72]})
for r in [39.6,42.1]:
    ring('Long_Cable_Tray_'+str(r),r-.12,r+.12,0,AEND,F+3.33,F+3.40,'Ceiling_Steel','2031,2046')
    for a in np.arange(0,AEND,.6):batchbox('Cable_Tray_Rungs',xyz(r,a,F+3.32),(.30,.025,.018),'Ceiling_Steel','2031,2046',rad(a))
for a in [28,43,60]:
    p=xy(33.6,a);cube('Gallery_Structural_Pier_'+str(a),(*p,F+H/2),(.55,.65,H),'Wall_Gray','2038-2046',rad(a),True)

# Archive wall: the exact 22 source document cells, including their original captions.
doc_a=15.;doc_r=math.sqrt(44.85**2-4.2**2)-.12;dp=xy(doc_r,doc_a);dyaw=rad(doc_a)-math.pi/2
s.mat('Photo_Original_Document_Atlas',(1,1,1),.9,image='textures/part03-original-documents-atlas.jpg')
for col in range(11):
    for row in range(2):
        w=8.2/11;h=2.08/2;mesh=panel(w-.009,h-.009,(col/11,row/2,(col+1)/11,(row+1)/2))
        loc=((col-5)*w,0,F+1.12+(1-row)*h)
        mesh=mesh.transformed(loc).transformed((*dp,0),dyaw)
        s.add(f'Original_Document_{row+1}_{col+1}',mesh,'Photo_Original_Document_Atlas','2021-2027','one of 22 original document cells; unchanged source pixels')
cube('Document_Wall_Back',(*dp,F+2.16),(8.38,.14,2.25),'Wood_Frame','2021-2027',dyaw,True)
# Move backing behind the image plane, never through it.
s.objects[-1]['vertices']=(np.asarray(s.objects[-1]['vertices'])+np.array([math.cos(rad(doc_a)),math.sin(rad(doc_a)),0])*.10).tolist()
for z in [F+1.06,F+3.26]:s.add('Document_Wall_Perimeter_'+str(z),box((0,-.025,z),(8.48,.06,.045)).transformed((*dp,0),dyaw),'Light_Linear','2021,2031')
for x in [-4.24,4.24]:s.add('Document_Wall_End_'+str(x),box((x,-.025,F+2.16),(.045,.06,2.24)).transformed((*dp,0),dyaw),'Case_White_Edge','2021,2031')

# Relief and explanatory panels on the opposite wall; framed art occurs once.
wall_photo('Relief_Antep_Map',1982,3.3,2.65,38.18,5.0,F+.68,quad=[(.083,.100),(.931,.043),(.966,.999),(.021,.947)],frame='Wood_Frame',inward=False)
wall_photo('Map_History_TR',1981,1.27,2.45,44.7,2.0,F+.65,quad=[(.204,.015),(.768,.008),(.807,.839),(.164,.829)])
wall_photo('Map_History_EN',1993,1.27,2.45,44.7,5.0,F+.65,quad=[(.257,.127),(.777,.131),(.830,.903),(.180,.895)])
wall_photo('Southern_Front_Panel',1998,3.0,1.55,38.2,11.5,F+1.48,quad=[(.030,.186),(.999,.164),(.999,.839),(.012,.818)],inward=False)
wall_photo('Ozdemir_Bey_Portrait',2008,.89,1.03,38.20,16.9,F+1.58,quad=[(.345,.279),(.563,.282),(.559,.480),(.342,.474)],frame='Gold_Frame',inward=False)
wall_photo('Traditional_Defender_Portrait',2015,.98,1.24,37.2,21.0,F+1.45,quad=[(.181,.259),(.824,.241),(.971,.956),(.080,.970)],frame='Gold_Frame',inward=False)

def desk_case(name,r,a,width=2.05,depth=.85):
    p=xy(r,a);yaw=rad(a)-math.pi/2
    def obj(tag,mesh,mat,collision=False):s.add(name+'_'+tag,mesh.transformed((*p,F),yaw),mat,'1987-2031',collision=collision)
    obj('Pedestal',box((0,0,.43),(width*.55,depth*.75,.86)),'Case_Base',True)
    obj('Tray_Rim',box((0,0,.90),(width,depth,.13)),'Case_White_Edge',True)
    obj('Interior',box((0,0,.972),(width-.09,depth-.09,.018)),'Case_Base')
    # Physical side panes and cover. The contents remain below the cover.
    for x in [-width/2,width/2]:obj('Side_'+str(x),box((x,0,1.14),(.009,depth,.36)),'Glass_Exhibit',True)
    for y in [-depth/2,depth/2]:obj('Pane_'+str(y),box((0,y,1.14),(width,.009,.36)),'Glass_Exhibit',True)
    obj('Cover',box((0,0,1.325),(width,depth,.009)),'Glass_Exhibit',True)
    for x in [-width/2,width/2]:obj('Top_Edge_'+str(x),box((x,0,1.333),(.008,depth,.008)),'Glass_Edge')
    for y in [-depth/2,depth/2]:obj('Long_Edge_'+str(y),box((0,y,1.333),(width,.008,.008)),'Glass_Edge')
    return p,yaw

def desk_object(name,mesh,mat,p,yaw,refs):s.add(name,mesh.transformed((*p,F),yaw),mat,refs)
def paper_quad(n,q,w,d,p,yaw,offset=(0,0),z=.994,name='Source_Document'):
    v=np.array([offset[0],offset[1]]);cs=math.cos(yaw);sn=math.sin(yaw);v=np.array([[cs,-sn],[sn,cs]])@v+p
    flat_source(s,name,n,q,w,d,(*v,F+z),yaw)

cases=[]
for i,a in enumerate([9.1,15.1,21.1]):cases.append(desk_case('Document_Display_Case_'+str(i+1),42.8,a))
p,yaw=cases[0]
paper_quad(2028,[(.24,.16),(.78,.17),(.76,.87),(.21,.87)],.40,.59,p,yaw,(-.50,0),name='Framed_Original_Certificate')
# Decorative dagger silhouettes, medallions and book in the first cases.
for i in range(3):
    mesh=join(cylinder((-.06+i*.25,-.24,1.01),(-.06+i*.25,.16,1.01),.012,segments=8),box((-.06+i*.25,.21,1.01),(.04,.13,.025)))
    desk_object('Case_Dagger_'+str(i),mesh,'Exhibit_Iron',p,yaw,'2029')
desk_object('Case_Red_Ribbon',Mesh().append([[.62,-.12,1.015],[.80,-.12,1.015],[.71,.05,1.015]],[[0,1,2]]),'Fez_Red',p,yaw,'2018,2029')
desk_object('Case_Brass_Medal',cylinder((.71,.095,1.005),(.71,.095,1.02),.055,segments=32),'Exhibit_Brass',p,yaw,'2018,2029')
p,yaw=cases[1]
paper_quad(1979,[(.313,.250),(.704,.312),(.651,.746),(.192,.693)],.36,.50,p,yaw,(-.29,0),1.01,'Original_Nutuk_Left_Page')
paper_quad(1979,[(.716,.314),(.999,.278),(.999,.796),(.665,.746)],.30,.50,p,yaw,(.06,0),1.01,'Original_Nutuk_Right_Page')
desk_object('Book_Page_Thickness',box((-.12,0,.993),(.72,.52,.026)),'Paper_Edge',p,yaw,'1979-1980')
paper_quad(2002,[(.16,.03),(.88,.04),(.91,.96),(.13,.96)],.33,.55,p,yaw,(.62,0),name='Medal_Record_Original_Text')
p,yaw=cases[2]
paper_quad(2009,[(.377,.235),(.866,.335),(.700,.824),(.077,.722)],.56,.64,p,yaw,(-.50,0),1.018,'Veterans_Original_Register')
desk_object('Register_Pages',box((-.50,0,.993),(.58,.66,.04)),'Paper_Edge',p,yaw,'2009-2010')
for row in range(3):
    for i in range(12):desk_object('Bandolier_Round_'+str(row)+'_'+str(i),cylinder((.02+i*.065,-.20+row*.16,1.01),(.02+i*.065,-.10+row*.16,1.01),.014,segments=8),'Exhibit_Brass',p,yaw,'2011')
for row in range(3):desk_object('Leather_Bandolier_'+str(row),box((.375,-.15+row*.16,.993),(.81,.15,.023)),'Exhibit_Leather',p,yaw,'2011')
# Two further low vitrines before the first wall case.
p,yaw=desk_case('Rifle_Medals_Display',40.6,23.8,2.2,.88)
wm,mm=rifle_mesh()
for mesh,mat,tag in [(wm,'Exhibit_Wood','Wood'),(mm,'Exhibit_Iron','Iron')]:
    v=np.array(mesh.vertices);v[:,1],v[:,2]=v[:,2].copy()-.02,v[:,1].copy()+1.06;mesh.vertices=v.tolist();desk_object('Historical_Display_Rifle_'+tag,mesh,mat,p,yaw,'1994-1997')
paper_quad(1989,[(.18,.11),(.84,.12),(.82,.89),(.16,.88)],.34,.52,p,yaw,(.76,0),name='Original_Case_Letter')

def curved_case(name,rfront,a0,a1,refs):
    ring(name+'_Lower_Plinth',rfront,44.95,a0,a1,F+.13,F+.31,'Case_Interior',refs,True)
    ring(name+'_Black_Base',rfront-.015,rfront+.10,a0,a1,F+.12,F+.30,'Black_Frame',refs)
    ring(name+'_Lower_Light',rfront-.021,rfront+.025,a0,a1,F+.075,F+.105,'Light_Linear',refs)
    ring(name+'_Top_Canopy',rfront-.03,44.95,a0,a1,F+2.95,F+3.29,'Case_Base',refs)
    annular_face(name+'_Canopy_Light',rfront-.044,a0,a1,F+2.92,F+2.945,'Light_Linear',refs)
    annular_face(name+'_Glass',rfront,a0,a1,F+.30,F+2.92,'Glass_Exhibit',refs,True)
    for a in np.arange(a0,a1+.1,2.4):
        p=xy(rfront,a);s.batch(name+'_Glass_Seams',cylinder((*p,F+.30),(*p,F+2.92),.003,segments=6),'Glass_Edge',refs)
    for a in [a0,a1]:linewall(name+'_Side_'+str(a),xy(rfront,a),xy(44.98,a),F+.3,F+2.92,.012,'Glass_Exhibit',refs)
    for a in np.arange(a0+1,a1,2.3):
        p=xy((rfront+44.9)/2,a);s.batch(name+'_Downlights',cylinder((*p,F+2.898),(*p,F+2.918),.055,segments=16),'Light_Linear',refs)
        s.lights.append({'position':list(xyz((rfront+44.9)/2,a,F+2.87)),'energy':42,'angle':95})

curved_case('Curved_Uniform_Case',42.,25,43,'2034-2057')
curved_case('Curved_Cannon_Case',40.8,44,61.8,'2038,2045,2059-2066')

# Original source silhouettes retain the actual costume, cap and mannequin face.
# Depth and rear surfaces are explicitly estimates; these are review envelopes.
uniforms=[
 (26.1,'cream_left'),(27.6,'cream_right'),(29.1,'fur_uniform'),(30.6,'white_uniform'),
 (32.1,'blue_helmet_a'),(33.6,'blue_red_cap'),(37.1,'blue_helmet_b'),
 (38.3,'blue_held_helmet'),(39.4,'blue_red_collar'),(40.55,'brown_uniform'),(41.75,'yellow_uniform')]
for i,(a,key) in enumerate(uniforms):
    ref,height,outline=FIGURES[key];pos=xyz(43.45,a,F+.32);yaw=rad(a)-math.pi/2
    exhibit_figure('Uniform_'+str(i+1),key,pos,yaw,height,ref,outline)
    if key in ['cream_right','fur_uniform','white_uniform','blue_helmet_a','blue_held_helmet','yellow_uniform']:
        q=np.array(pos)+np.array([math.sin(rad(a))*.34,-math.cos(rad(a))*.34,.78]);rifle(s,'Uniform_Rifle_'+str(i+1),q,yaw,1.45,str(ref),base_z=F+.32)
    q=xy(42.45,a);plaque=Mesh().append([[-.105,-.11,.32],[.105,-.11,.32],[.105,.08,.52],[-.105,.08,.52]],[[0,1,2,3]])
    s.add('Uniform_Label_Stand_'+str(i),plaque.transformed((*q,F),yaw),'Black_Frame',str(ref),'source display-label shape; text not legible in the source region')
    s.add('Uniform_Mannequin_Base_'+str(i),cylinder((0,0,0),(0,0,.012),.27,segments=48).transformed(pos),'Case_Base',str(ref))
# Original hat cabinet stays one verified source panel; it contains nine hats.
wall_photo('Original_Nine_Hat_Cabinet',2052,1.5,2.30,44.65,35.3,F+.37,quad=[(.223,.246),(.918,.223),(.888,.990),(.160,.903)],frame='Case_Base')

# Source photograph backdrops use only unoccupied image strips, never a second mannequin.
wall_photo('Uniform_Archival_Backdrop_A',2048,1.8,2.28,44.70,27.4,F+.33,crop=(.035,.29,.350,.77),frame='Case_Interior')
wall_photo('Uniform_Archival_Backdrop_B',2053,1.8,2.28,44.70,39.8,F+.33,crop=(.665,.28,.995,.81),frame='Case_Interior')

# The artillery case has the source's unshielded wooden-wheel gun.
emit_reference_prop(s,old.cannon,('Museum_Cannon',(0,0,0),0,'2061-2066'),xyz(42.8,52.9,F+.32),rad(52.9)+math.pi/2,'2061-2066','Artillery',scale=.85,omit=('Shield',),overrides={'REF_Wood_Light':'Exhibit_Wood','REF_Iron':'Exhibit_Iron'})
for row in range(7):
    for col,a in enumerate([46.7,49.1,56.9,59.2]):
        p=xyz(44.55,a,F+.66+row*.29);rifle(s,f'Wall_Rifle_{row}_{col}',p,rad(a)-math.pi/2,.04*(-1 if row%2 else 1),'2062-2066')
for a in [47,59]:
    for j in range(3):
        p=np.array(xyz(42.2,a,F+1.04))+np.array([.20*math.cos(j*TAU/3),.20*math.sin(j*TAU/3),0]);rifle(s,f'Standing_Rifle_{a}_{j}',p,rad(a)+j*.8,1.22,'2062-2066',base_z=F+.32)
for a in [50.5,54.7]:
    for j in range(7):
        p=xyz(41.65+(j%2)*.50,a+(j//2)*.45,F+.42+(j%3==0)*.10)
        bag=sphere((0,0,0),(.30,.17,.11),24,12);v=np.asarray(bag.vertices);v[:,2]=np.clip(v[:,2],-.09,.09);v[:,2]+=.006*np.sin(v[:,0]*25)*np.cos(v[:,1]*18);bag.vertices=v.tolist()
        s.batch('Artillery_Sandbags',bag.transformed(p,rad(a)),'Cloth_Cream','2059-2061',smooth=True)
wall_photo('Weapons_Identification_Display',2067,1.05,.72,33.22,42.3,F+1.32,quad=[(.047,.364),(.946,.336),(.953,.677),(.042,.666)],frame='Black_Frame',inward=False)

# Dense gray weapon-silhouette installation visible opposite the women's display.
ring('Weapon_Sculpture_Plinth',33.05,33.78,44,61.9,F+.12,F+.31,'Black_Frame','2042-2044',True)
ring('Weapon_Sculpture_Canopy',33.05,33.78,44,61.9,F+2.92,F+3.25,'Case_Base','2042-2044')
ring('Weapon_Sculpture_Light',33.74,33.80,44,61.9,F+.07,F+.10,'Light_Linear','2042-2044')
annular_face('Weapon_Sculpture_Glass',33.79,44,61.9,F+.31,F+2.92,'Glass_Exhibit','2042-2044',True)
for i in range(125):
    a=float(rng.uniform(44.6,61.2));z=float(rng.uniform(F+.65,F+2.55));r=float(rng.uniform(33.2,33.59));tilt=float(rng.uniform(-1.3,1.3))
    w,m=rifle_mesh();sc=float(rng.uniform(.55,1.0));combined=join(w,m);v=np.asarray(combined.vertices)*sc
    cs=math.cos(tilt);sn=math.sin(tilt);v[:,[0,2]]=v[:,[0,2]]@np.array([[cs,sn],[-sn,cs]])
    # Clamp the decorative ends inside the actual case height, without altering functional geometry.
    v[:,2]=np.clip(v[:,2]+z,F+.33,F+2.88);combined.vertices=v.tolist()
    s.batch('Layered_Weapon_Silhouettes',combined.transformed((*xy(r,a),0),rad(a)+math.pi/2),'Sculpture_Gray','2042-2044')

def round_case(name,r,a,radius,refs):
    p=xy(r,a)
    s.add(name+'_Base',cylinder((*p,F+.12),(*p,F+.32),radius,segments=96),'Case_Interior',refs,collision=True)
    s.add(name+'_Black_Base',cylinder((*p,F+.13),(*p,F+.29),radius+.012,segments=96,caps=False),'Black_Frame',refs)
    s.add(name+'_Base_Light',cylinder((*p,F+.075),(*p,F+.105),radius+.018,segments=96,caps=False),'Light_Linear',refs)
    s.add(name+'_Glass',cylinder((*p,F+.32),(*p,F+2.92),radius,segments=96,caps=False),'Glass_Exhibit',refs,collision=True)
    s.add(name+'_Canopy',cylinder((*p,F+2.95),(*p,F+3.27),radius+.025,segments=96),'Case_Base',refs)
    s.add(name+'_Canopy_Light',cylinder((*p,F+2.91),(*p,F+2.935),radius+.032,segments=96,caps=False),'Light_Linear',refs)
    s.add(name+'_Central_Drum',cylinder((*p,F+.32),(*p,F+2.93),.44,segments=56),'Case_Base',refs)
    for t in np.linspace(0,TAU,9)[:-1]:
        q=p+radius*np.array([math.cos(t),math.sin(t)]);s.batch(name+'_Glass_Joints',cylinder((*q,F+.32),(*q,F+2.92),.003,segments=6),'Glass_Edge',refs)
    s.lights.append({'position':[*p,F+2.85],'energy':78,'angle':128})
    return p

men=round_case('Round_Local_Menswear',37.7,32.8,1.56,'2037,2046,2068-2073')
men_styles=['local_red_shawl','local_suit','local_gold','local_khaki_a','local_light','local_khaki_b']
for i,key in enumerate(men_styles):
    ref,height,outline=FIGURES[key];t=TAU*i/6;pos=men+1.05*np.array([math.cos(t),math.sin(t)])
    exhibit_figure('Local_Menswear_'+str(i+1),key,(*pos,F+.33),t+math.pi/2,height,ref,outline,back_color=(.17,.15,.11))
    if i%2==1:rifle(s,'Local_Rifle_'+str(i),(*list(pos+.25*np.array([-math.sin(t),math.cos(t)])),F+1.10),t,1.43,str(ref),base_z=F+.33)

women=round_case('Round_Local_Womenswear',37.6,52.0,1.68,'2043-2044,2074-2080')
women_styles=['floral_outfit','blue_child','orange_robe','red_white_vest','purple_child','red_check_vest']
for i,key in enumerate(women_styles):
    ref,height,outline=FIGURES[key];t=TAU*i/6+.35;pos=women+1.11*np.array([math.cos(t),math.sin(t)])
    exhibit_figure('Local_Family_Costume_'+str(i+1),key,(*pos,F+.33),t+math.pi/2,height,ref,outline,back_color=(.17,.12,.12))
for i,t in enumerate([.1,1.4,2.8,4.1,5.3]):
    p=women+1.39*np.array([math.cos(t),math.sin(t)]);emit_reference_prop(s,old.pot,('Household_Vessel_'+str(i),(0,0,0),.13,.28,'REF_Iron','2075-2080',True),(*p,F+.33),0,'2075-2080','Costume',overrides={'REF_Iron':'Exhibit_Iron'})
for i in range(5):
    p=women+np.array([-.48,-.60]);s.batch('Folded_Original_Linen',box((*p,F+.355+i*.024),(.43,.35,.023),i*.12),'Cloth_Cream','2078')

# Bound the next review segment; it disappears automatically when part04 is loaded.
linewall('REVIEW_Part04_Boundary',xy(33,AEND),xy(45,AEND),F,F+H,.10,'Ceiling_Dark','review helper; not museum fabric')
s.objects[-1].update(review_only=True,temporary_until='part04')
mid=xy(37,AEND);s.text('REVIEW_Part04_Label','NEXT SECTION\nIN PREPARATION',(*mid,F+1.6),.22,(math.pi/2,0,rad(AEND)))
s.texts[-1].update(review_only=True,temporary_until='part04')

def view(id,title,r,a,tr,ta,tz,photo):return {'id':id,'title':title,'position':list(xyz(r,a,F+1.65)),'target':list(xyz(tr,ta,tz)),'photo':photo}
s.views=[
 view('archives','مدخل معرض الوثائق',40.2,2,42.5,14,F+1.5,1985),
 view('documents','جدار الوثائق الأصلية',40.8,15,44.2,15,F+2.1,2021),
 view('relief','الخريطة البارزة والشرح',41.5,5,38.1,5,F+2.0,1982),
 view('archivecases','الفاترينات والدفاتر',41.15,21.1,42.8,21.1,F+1.03,2008),
 view('uniforms','الأزياء العسكرية المنحنية',40.15,29,43.4,33,F+1.2,2034),
 view('uniformdetail','مطابقة تفاصيل الزي',40.7,29.1,43.45,29.1,F+1.3,2048),
 view('hats','القبعات وتفاصيل الأزياء',40.2,35.3,44.6,35.3,F+1.5,2052),
 view('menswear','الفاترينة الدائرية للأزياء الشعبية',35.2,27.8,37.7,32.8,F+1.5,2046),
 view('artillery','المدفع وبنادق العرض',39.75,49,42.8,52.9,F+1.1,2061),
 view('womenswear','الأزياء العائلية والأواني',35.2,46.6,37.6,52,F+1.5,2074),
 view('sculpture','تركيب مجسمات الأسلحة',35.2,58,33.5,53,F+1.5,2042),
 view('return','الممر والرجوع إلى الخريطة',35.2,60,35.2,42,F+1.4,2040)]
s.save(ROOT/'reconstruction/part03-scene.json')
(ROOT/'output/Gaziantep-Museum-2026-10-25/part03-figure-provenance.json').write_text(json.dumps({
 'method':'Manually traced source-photo silhouettes, unchanged photo UVs on rounded 3D review envelopes. Rear surfaces, depth, heights and placement are estimated. Not recovered 360-degree garment geometry.',
 'figure_count':len(FIGURES),'source_definitions':'scripts/part03_figure_sources.py',
 'figures':[{'key':key,'source':f'IMG_{n}.HEIC','height_estimate_m':h,'outline_vertices':len(outline)} for key,(n,h,outline) in FIGURES.items()]},ensure_ascii=False,indent=2))
(ROOT/'reconstruction/part03-notes.json').write_text(json.dumps({
 'title':'الوثائق والأزياء والأسلحة','stage':'local draft before visual QA','source_photos':'IMG_1978 through IMG_2080',
 'observed':['22-document wall in two rows','Low glass archive cases','Curved uniform case and nine-hat cabinet','Unshielded wooden-wheel cannon and rifle racks','Two circular costume cases','Dense gray weapon-silhouette installation','Exposed ceiling services and dark stone floor'],
 'representation_limits':['Room dimensions, route and absolute placement remain unmeasured','Display figures use traced source-photo fronts on rounded review meshes; depth and rear surfaces are estimates, not recovered 360-degree garments','Other artifact geometry is simplified and editable','Original document lettering is preserved as source pixels, with source glare/resolution limits','Relief map is a photo surface, not a recovered elevation survey','Fine tailoring, artifact identification and counts require source comparison during review'],
 'imagegen_used_for_this_part':False,'accuracy_100_percent':False,
 'duplicate_check':'IMG_2012 and IMG_2170 show the same painting; reserved for the paintings section, not duplicated here',
 'qa_reports':['../review/qa/part03-navigation.json','../review/qa/part03-clearance.json','../output/Gaziantep-Museum-2026-10-25/part03-verification.json']},ensure_ascii=False,indent=2))
