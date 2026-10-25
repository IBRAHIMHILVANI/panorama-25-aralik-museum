"""Observed paintings and concluding history displays, IMG_2144–2188.
Actual original painting pixels are retained; no painting or lettering is generated.
"""
from museum_geometry import *
from museum_architecture import *
from museum_exhibits import photo_material,projected_panel,rifle
from shapely.geometry import Polygon,box as rect
s=Scene('05_Paintings_History');C=np.array([-6.,23.5]);F=-4.2;A0=105.;A1=140.;RO=45.
def xy(r,a):a=math.radians(a);return C+r*np.array([math.cos(a),math.sin(a)])
def xyz(r,a,z):return (*xy(r,a),z)
def ri(a):return 33+4*min(1,max(0,(a-105)/4))
def sector():return Polygon([xy(RO,a) for a in np.linspace(A0,A1,120)]+[xy(ri(a),a) for a in np.linspace(A1,A0,120)])
def cube(name,p,d,mat,refs='',yaw=0,collision=False):s.add(name,box(p,d,yaw),mat,refs,collision=collision)
def wallseg(name,a,b,z0,z1,width,mat,refs=''):
 a=np.array(a);b=np.array(b);p=(a+b)/2;cube(name,(*p,(z0+z1)/2),(np.linalg.norm(a-b),width,z1-z0),mat,refs,math.atan2(*(b-a)[::-1]),True)
for name,col,rough,metal,alpha,em in [
 ('Gallery_Wall',(.45,.46,.42),.84,0,1,.08),('Gallery_Floor',(.25,.26,.245),.65,0,1,0),
 ('Black',(.028,.032,.031),.65,0,1,0),('Steel',(.10,.115,.11),.53,.6,1,0),('Ceiling',(.05,.055,.052),.92,0,1,0),
 ('Frame_Wood',(.25,.11,.055),.53,0,1,0),('Frame_Dark',(.105,.055,.026),.60,0,1,0),('Frame_Gold',(.50,.34,.13),.41,.38,1,0),
 ('Rope',(.46,.37,.22),.94,0,1,0),('Post_Metal',(.40,.37,.30),.34,.8,1,0),('Warm_Light',(.99,.90,.69),.45,0,1,2.5),
 ('Glass_Case',(.72,.80,.78),.1,0,.09,0),('Case_Interior',(.68,.64,.55),.8,0,1,.15),('Paper',(.78,.72,.59),.9,0,1,.1),
 ('Desk_Wood',(.32,.15,.055),.54,0,1,0),('Exhibit_Wood',(.40,.23,.09),.6,0,1,0),('Exhibit_Iron',(.16,.18,.17),.48,.5,1,0),
 ('Lettering',(.83,.82,.75),.7,0,1,.1),('Slats',(.62,.57,.48),.8,0,1,.05)]:s.mat(name,col,rough,metal,alpha,em)
for i in range(5):s.mat('Floor_Stone_'+str(i),(.235+i*.008,.245+i*.008,.23+i*.008),.66)
floor=sector();s.add('Painting_Gallery_Floor',polygon_plate(floor,F),'Gallery_Floor','2145-2188',collision=True)
s.add('Painting_Gallery_Ceiling',polygon_plate(floor,F+3.7,False),'Ceiling','2145-2188')
s.add('Painting_Outer_Wall',arc_band(C,45,45.20,math.radians(A0),math.radians(A1),F,F+3.7,120),'Gallery_Wall','2145-2188',collision=True)
for i,(a,b) in enumerate(zip(np.linspace(A0,A1,100),np.linspace(A0,A1,100)[1:])):wallseg('Painting_Inner_Wall_'+str(i),xy(ri(a)-.06,a),xy(ri(b)-.06,b),F,F+3.7,.13,'Gallery_Wall','2145-2188')
x0,y0,x1,y1=floor.bounds
for row,y in enumerate(np.arange(y0,y1,.72)):
 for col,x in enumerate(np.arange(x0-.5,x1,.99)):
  x+=.495*(row%2);g=rect(x+.003,y+.003,x+.987,y+.717).intersection(floor)
  for p in polygon_parts(g):
   if p.area>1e-5:s.batch('Gallery_Stone_Paving',polygon_plate(p,F+.003),'Floor_Stone_'+str((row+2*col)%5),'2145,2164,2182')
for a in np.arange(106,140,4):
 r0=ri(a)+.1;p=(xy(r0,a)+xy(44.9,a))/2
 s.batch('Exposed_Ceiling_Beams',box((*p,F+3.45),(44.9-r0,.18,.27),math.radians(a)),'Steel','2145-2184')
 for r in [39.5,42.0]:
  p=xy(r,a);s.batch('Ceiling_Ducts',box((*p,F+3.30),(.42,2.8,.28),math.radians(a)),'Steel','2145-2184')
  s.batch('Ceiling_Vent_Rims',torus((*p,F+3.12),.22,.018,(0,0,1),32,6),'Steel','2145-2184')
  for t in np.linspace(0,math.pi,4)[:-1]:s.batch('Ceiling_Vent_Blades',box((*p,F+3.115),(.38,.035,.01),t),'Black','2145-2184')
for a in np.arange(132,140,.42):s.batch('History_Ceiling_Slats',box(xyz(38.6,a,F+3.08),(3.0,.075,.13),math.radians(a)),'Slats','2179-2186')
for r,a in [(37.8,117.1),(37.8,127.5),(44.6,132.0)]:cube('Gallery_Column_'+str(a),xyz(r,a,F+1.85),(.55,.65,3.7),'Gallery_Wall','2162,2178',math.radians(a),True)

paintings=[
 ('British_Arrival',2012,107.5,True,3.0,2.0,[(.195,.214),(.846,.203),(.845,.789),(.188,.790)]),
 ('Street_Defence',2158,109.3,False,2.65,1.85,[(.136,.251),(.915,.252),(.919,.708),(.136,.707)]),
 ('Public_Gathering',2150,112.7,True,3.0,1.9,[(.067,.229),(.978,.215),(.979,.695),(.062,.691)]),
 ('Assembly',2148,114.5,False,2.65,1.85,[(.126,.365),(.880,.355),(.903,.741),(.101,.751)]),
 ('Artillery_Battle',2157,117.9,True,3.0,2.0,[(.106,.300),(.944,.282),(.950,.746),(.103,.739)]),
 ('Gathering_Under_Trees',2154,119.7,False,2.65,1.85,[(.183,.378),(.802,.340),(.819,.668),(.178,.659)]),
 ('Women_And_Community',2166,123.1,True,3.0,2.0,[(.070,.344),(.869,.356),(.899,.761),(.057,.777)]),
 ('Resistance_Council',2165,124.9,False,2.65,1.85,[(.131,.374),(.854,.369),(.895,.758),(.103,.769)]),
 ('City_Celebration',2168,128.3,True,3.0,2.0,[(.290,.371),(.744,.293),(.755,.662),(.286,.615)]),
 ('Defenders_And_Desk',2167,130.1,False,2.65,1.8,[(.178,.353),(.795,.357),(.799,.684),(.176,.684)])]

def ornate_frame(name,w,h,origin,yaw,refs):
 frame=Mesh();gold=Mesh();ornament=Mesh()
 for size,depth,band,mat in [(0,.055,.13,frame),(.05,.027,.035,gold)]:
  ww=w+size;hh=h+size
  for z in [-band/2,hh+band/2]:mat.append(*old.mesh_args(box((0,-depth,z),(ww+2*band,.06,band))))
  for x in [-ww/2-band/2,ww/2+band/2]:mat.append(*old.mesh_args(box((x,-depth,hh/2),(band,.06,hh))))
 for x in np.arange(-w/2,w/2+.01,.17):
  for z in [-.078,h+.078]:ornament.append(*old.mesh_args(torus((float(x),-.102,z),.035,.009,(0,1,0),12,5)))
 for z in np.arange(.08,h,.17):
  for x in [-w/2-.078,w/2+.078]:ornament.append(*old.mesh_args(torus((x,-.102,float(z)),.035,.009,(0,1,0),12,5)))
 for tag,m,mat in [('Moulding',frame,'Frame_Wood'),('Inner_Trim',gold,'Frame_Gold'),('Carved_Rhythm',ornament,'Frame_Dark')]:s.add(name+'_'+tag,m.transformed(origin,yaw),mat,refs)

def barrier(name,w,position,yaw,refs):
 posts=Mesh();ropes=Mesh()
 for x in [-w/2-.17,0,w/2+.17]:
  posts.append(*old.mesh_args(cylinder((x,0,F),(x,0,F+.91),.021,segments=12)))
  posts.append(*old.mesh_args(cylinder((x,0,F),(x,0,F+.035),.105,segments=24)))
  posts.append(*old.mesh_args(sphere((x,0,F+.92),(.037,.037,.037),16,8)))
 for a,b in [(-w/2-.17,0),(0,w/2+.17)]:
  pts=[(a+(b-a)*t,0,F+.84-.16*math.sin(math.pi*t)) for t in np.linspace(0,1,18)]
  for u,v in zip(pts,pts[1:]):ropes.append(*old.mesh_args(cylinder(u,v,.014,segments=8)))
 s.add(name+'_Posts',posts.transformed((*position,0),yaw),'Post_Metal',refs)
 s.add(name+'_Ropes',ropes.transformed((*position,0),yaw),'Rope',refs)
 s.add('NAV_'+name,box((0,0,F+.44),(w+.34,.045,.88)).transformed((*position,0),yaw),'Rope',refs,collision=True,hidden=True)

for name,n,a,outward,w,h,quad in paintings:
 r=math.sqrt((44.89)**2-(w/2+.15)**2)-.07 if outward else ri(a)+.15
 yaw=math.radians(a)-math.pi/2 if outward else math.radians(a)+math.pi/2;pos=xyz(r,a,F+.69)
 s.add('Original_Painting_'+name,projected_panel(w,h,quad).transformed(pos,yaw),photo_material(s,n),str(n),'original painting photo projection; rectified perspective, no generated painting content')
 ornate_frame('Painting_Frame_'+name,w,h,pos,yaw,str(n))
 s.add('Painting_Backing_'+name,box((0,.06,h/2),(w+.28,.10,h+.28)).transformed(pos,yaw),'Black',str(n),collision=True)
 if n!=2167:barrier('Painting_Barrier_'+name,w,xy(r-1.35 if outward else r+1.35,a),yaw,str(n))
 light_r=r-1.5 if outward else r+1.5;s.lights.append({'position':list(xyz(light_r,a,F+3.25)),'target':list(xyz(r,a,F+1.8)),'energy':65,'angle':64,'color':[1,.90,.76]})
 for off in [-.65,.65]:
  local=box((off,0,0),(.09,.16,.16)).transformed(xyz(light_r,a,F+3.15),yaw);s.batch('Painting_Spot_Housings',local,'Black','2144-2172')

# Writing desk beneath the observed last canvas.
p=xy(38.1,130.1);yaw=math.radians(130.1)+math.pi/2
wood=join(box((0,0,.82),(1.55,.61,.085)),box((-.60,.04,.40),(.32,.52,.80)),box((.60,.04,.40),(.32,.52,.80)),box((0,.26,.50),(.90,.05,.42)))
s.add('Original_Writing_Desk',wood.transformed((*p,F),yaw),'Desk_Wood','2167',collision=True)
for x in [-.60,.60]:
 for z in [.28,.55]:s.batch('Desk_Drawer_Fronts',box((x,-.24,z),(.26,.025,.20)).transformed((*p,F),yaw),'Desk_Wood','2167')
s.add('Desk_Information_Card',panel(.19,.23).transformed((0,-.03,.87)).transformed((*p,F),yaw),'Paper','2167')

# Wall vitrines contain actual separate display objects; original labels remain photo references.
for i,a in enumerate([110.1,120.5,125.7]):
 p=xy(44.30,a);yaw=math.radians(a)-math.pi/2;w=.95;h=1.35;z=F+.92
 s.add('Wall_Artifact_Case_'+str(i),box((0,.12,h/2),(w+.16,.32,h+.16)).transformed((*p,z),yaw),'Black','2149,2151-2153,2169',collision=True)
 s.add('Wall_Artifact_Case_Lining_'+str(i),box((0,-.051,h/2),(w,.012,h)).transformed((*p,z),yaw),'Case_Interior','2149,2169')
 s.add('Wall_Artifact_Case_Glass_'+str(i),panel(w,h).transformed((0,-.24,0)).transformed((*p,z),yaw),'Glass_Case','2149,2169',collision=True)
 for j in range(3):
  dagger=join(box((-.28+j*.26,-.13,.76),(.023,.02,.62)),cylinder((-.28+j*.26,-.13,.42),(-.28+j*.26,-.13,.26),.022,segments=12),box((-.28+j*.26,-.13,.43),(.11,.025,.018)))
  s.batch('Case_Artifact_Blades',dagger.transformed((*p,z),yaw),'Exhibit_Iron','2149')
 s.add('Case_Original_Paper_'+str(i),panel(.27,.36).transformed((0,-.15,.03)).transformed((*p,z),yaw),'Paper','2149,2152')

# The concluding curved history area retains the original photographic panels.
def history_panel(name,n,w,h,r,a,z,quad,inward=True):
 yaw=math.radians(a)-math.pi/2 if inward else math.radians(a)+math.pi/2
 s.add(name,projected_panel(w,h,quad).transformed(xyz(r,a,z),yaw),photo_material(s,n),str(n),'original history display source, no generated names or quotations')
 s.add(name+'_Backing',box((0,.045,h/2),(w+.07,.06,h+.07)).transformed(xyz(r,a,z),yaw),'Black',str(n))
history_panel('History_Original_Group_Photo',2187,1.75,1.35,37.15,134.0,F+.95,[(.047,.279),(.943,.311),(.939,.811),(.045,.799)],False)
history_panel('History_Original_Resistance_Photo',2188,1.75,1.5,37.15,138.0,F+.89,[(.069,.278),(.936,.257),(.931,.855),(.061,.854)],False)
history_panel('History_Original_Name_And_Medal_Wall',2179,4.0,1.85,44.68,136.5,F+.75,[(.27,.477),(.759,.460),(.760,.586),(.270,.573)])
p=xy(40.7,136.4);yaw=math.radians(136.4)-math.pi/2
s.add('History_Central_Display_Pedestal',join(box((0,0,.36),(1.8,.90,.72)),box((0,0,.75),(2.05,1.12,.08))).transformed((*p,F),yaw),'Black','2179-2184',collision=True)
s.add('History_Central_Display_Surface',plane_xy(-.96,.96,-.50,.50,.794).transformed((*p,F),yaw),'Case_Interior','2179-2184')
for a in [133,136,139]:s.lights.append({'position':list(xyz(41,a,F+3.15)),'energy':80,'angle':120})
wallseg('REVIEW_Part06_Boundary',xy(37,140),xy(45,140),F,F+3.7,.10,'Ceiling','review-only temporary partition');s.objects[-1].update(review_only=True,temporary_until='part06')
def view(id,title,r,a,tr,ta,z,photo):return {'id':id,'title':title,'position':list(xyz(r,a,F+1.65)),'target':list(xyz(tr,ta,z)),'photo':photo}
s.views=[view('paintings','قاعات اللوحات',40.6,107,40.6,120,F+1.6,2145),view('britisharrival','لوحة وصول القوات',41.6,107.5,44.7,107.5,F+1.7,2012),view('cannonpainting','لوحة المدفع',41.6,117.9,44.7,117.9,F+1.7,2157),view('council','لوحة المجلس',40.3,124.9,37.1,124.9,F+1.7,2165),view('writingdesk','اللوحة والمكتب الخشبي',40.5,130.1,37.2,130.1,F+1.5,2167),view('history','قاعة الصور والوثائق الختامية',39.0,134.5,44.5,136.5,F+1.6,2179)]
s.save(ROOT/'reconstruction/part05-scene.json')
(ROOT/'reconstruction/part05-notes.json').write_text(json.dumps({'title':'اللوحات والتاريخ','source_photos':'2144-2188; 2012 and 2170 are one painting','observed_large_paintings':len(paintings),'painting_source_ids':[p[1] for p in paintings],'duplicates_avoided':['2012/2170','2144/2158/2159'],'stage':'first integrated build, awaiting second review','accuracy_100_percent':False,'limits':['All positions and sizes are photo-informed estimates','10 distinct large paintings were identified in this supplied sequence; no extra paintings invented to force a published total','High-resolution original photographs are currently unavailable because the external SSD is disconnected; recovered contact-sheet regions remain temporary']},ensure_ascii=False,indent=2))
