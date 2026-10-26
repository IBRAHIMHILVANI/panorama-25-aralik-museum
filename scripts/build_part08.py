"""Reference study of the basement Sinevizyon room. Relative doorway placement confirmed by user; exact dimensions unmeasured.
Geometry follows the published room photograph; dimensions and rear wall unmeasured.
"""
from museum_geometry import *
from museum_architecture import extrude_xz,extrude_xy
from museum_exhibits import projected_panel
from shapely.geometry import box as rect,Polygon
s=Scene('08_Cinema_Reference_Study');W=5.80;D=8.00;H=2.82;F=0.
ref='gamaakademi.com.tr/salonlar.php Sinevizyon photograph; capture date unknown'
for name,col,rough,metal,alpha,em in [('Cinema_Oak',(.76,.71,.58),.80,0,1,0),('Cinema_Panel_Joint',(.30,.28,.22),.95,0,1,0),('Cinema_Ceiling',(.40,.42,.35),.86,0,1,0),('Cinema_Carpet',(.39,.40,.32),.98,0,1,0),('Cinema_Chair',(.16,.18,.15),.88,0,1,0),('Cinema_Legs',(.20,.16,.11),.66,0,1,0),('Cinema_Offwhite',(.82,.83,.77),.6,0,1,0),('Cinema_Metal',(.45,.46,.41),.38,.65,1,0),('Cinema_Black',(.035,.04,.035),.7,0,1,0),('Cinema_Light',(.98,.94,.76),.4,0,1,3),('Cinema_Exit',(.03,.48,.16),.5,0,1,1)]:s.mat(name,col,rough,metal,alpha,em)
s.mat('Photo_Cinema_Screen',(1,1,1),.7,emission=.7,image='textures/Cinema_Reference.jpg')
def put(name,m,mat,collision=False,smooth=False,basis='photograph-derived feature; sizes are unmeasured estimates'):s.add(name,m,mat,ref,basis,collision=collision,smooth=smooth)
put('Cinema_Floor',plane_xy(-W/2,W/2,0,D,F),'Cinema_Carpet',True);s.objects[-1]['hidden']=True
s.mat('Cinema_Carpet_Source',(1,1,1),.98,image='textures/Cinema_Reference.jpg')
for x in np.arange(-W/2,W/2,.4):
 for y in np.arange(0,D,.4):
  m=plane_xy(x,min(W/2,x+.4),y,min(D,y+.4),F+.003)
  m.uv=[[[.510+.045*u,1-(.65+.14*v)] for u,v in face] for face in m.uv]
  s.batch('Cinema_Real_Carpet_Surface',m,'Cinema_Carpet_Source',ref)
put('Cinema_Ceiling',plane_xy(-W/2,W/2,0,D,H),'Cinema_Ceiling')
for x in [-W/2,W/2]:put('Cinema_Side_Wall_'+str(x),box((x,D/2,H/2),(.12,D,H)),'Cinema_Oak',True)
# Right-hand doorway is visible beside the projection screen; outside connection is unconfirmed.
door_center=-2.29;door_width=.80;front=rect(-W/2,0,W/2,H).difference(rect(door_center-door_width/2,0,door_center+door_width/2,2.10))
put('Cinema_Front_Wall',extrude_xz(front,.12),'Cinema_Oak',True)
put('Cinema_Door_Leaf_Open',box((door_center-door_width/2,-.39,1.045),(door_width-.06,.045,2.09),math.pi/2),'Cinema_Offwhite',True,basis='Door opened for the user-confirmed connection beside the atrium stair; swing unmeasured')
for x in [door_center-door_width/2,door_center+door_width/2]:put('Cinema_Door_Jamb_'+str(x),box((x,.016,1.06),(.055,.13,2.12)),'Cinema_Oak')
put('Cinema_Door_Header',box((door_center,.016,2.12),(door_width+.06,.13,.055)),'Cinema_Oak')
put('Cinema_Exit_Light',box((door_center,.07,2.58),(.34,.08,.15)),'Cinema_Exit')
s.text('Cinema_Exit_Lettering','EXIT',(door_center,.117,2.55),.075,rotation=(math.pi/2,0,math.pi),material='Cinema_Offwhite')
# Rear wall is kept plain because this camera does not reveal its layout.
put('Cinema_Rear_Wall_Unverified',box((0,D,H/2),(W,.12,H)),'Cinema_Oak',True,basis='unseen rear enclosure placeholder; not surveyed or matched')
# Tall acoustic timber panels with the repeated horizontal perforation bands seen in the photo.
for x in [-W/2+.065,W/2-.065]:
 for y in np.arange(.0,D,.72):s.batch('Cinema_Vertical_Panel_Joints',box((x,y,H/2),(.005,.006,H)),'Cinema_Panel_Joint',ref)
 for z0 in [.22,.82,1.42,2.02]:
  for z in np.arange(z0,z0+.38,.035):s.batch('Cinema_Horizontal_Acoustic_Slots',box((x,D/2,float(z)),(.005,D-.03,.003)),'Cinema_Panel_Joint',ref)
for y in [0.065,D-.065]:
 for x in np.arange(-W/2,W/2,.72):
  if y<1 and abs(x-door_center)<door_width/2+.04:continue
  s.batch('Cinema_End_Panel_Joints',box((x,y,H/2),(.005,.004,H)),'Cinema_Panel_Joint',ref)
# Ceiling perforations are batched real geometry instead of noisy image-generated lettering.
for y in np.arange(.04,D,.055):
 for x in np.arange(-W/2+.04,W/2,.055):
  s.batch('Cinema_Ceiling_Perforations',plane_xy(x-.0035,x+.0035,y-.0035,y+.0035,H-.003),'Cinema_Panel_Joint',ref)
for y in np.arange(0,D,1.18):s.batch('Cinema_Ceiling_Module_Seams',box((0,y,H-.004),(W,.008,.006)),'Cinema_Panel_Joint',ref)
# Six rows, three seats each side: observed row rhythm, count remains provisional.
def armchair():
 # Flat rounded back and rising upholstered arms match the visible chair silhouette.
 back_profile=rect(-.265,.415,.265,.94).buffer(.035,quad_segs=8)
 m=extrude_xz(back_profile,.075).transformed((0,.245,0))
 side=Polygon([(-.26,.39),(-.26,.62),(-.22,.67),(.10,.69),(.20,.85),(.23,.94),(.29,.91),(.29,.39)])
 for sign in [-1,1]:
  arm=extrude_xz(side,.065);v=np.asarray(arm.vertices);v[:,[0,1]]=v[:,[1,0]];v[:,0]+=sign*.270;arm.vertices=v.tolist();arm.faces=[list(reversed(f)) for f in arm.faces];m.append(*old.mesh_args(arm))
 m.append(*old.mesh_args(box((0,-.015,.435),(.49,.52,.095),bevel=.065)))
 legs=Mesh()
 for x in [-.215,.215]:
  for y in [-.19,.21]:legs.append(*old.mesh_args(cylinder((x*1.1,y*1.13,.02),(x,y,.42),.022,.026,segments=8)))
 return m,legs
chair,legs=armchair();centres=[]
for row,y in enumerate([1.65,2.58,3.51,4.44,5.37,6.30]):
 for x in [-2.00,-1.34,-.68,.68,1.34,2.00]:
  centres.append((x,y));s.batch('Cinema_Upholstered_Armchairs',chair.transformed((x,y,0)),'Cinema_Chair',ref,smooth=True);s.batch('Cinema_Chair_Wooden_Legs',legs.transformed((x,y,0)),'Cinema_Legs',ref)
  put('NAV_Cinema_Seat_%02d'%len(centres),box((x,y,.48),(.57,.60,.96)),'Cinema_Chair',True,basis='collision envelope for the chair');s.objects[-1]['hidden']=True
# Original screen content is retained as a source-photo projection, not generated film text.
quad=[(.375,.199),(.626,.219),(.616,.430),(.371,.414)]
put('Cinema_Projection_Screen',projected_panel(3.90,2.18,quad).transformed((.35,.085,.58),math.pi),'Photo_Cinema_Screen')
put('Cinema_Screen_Backing',box((.35,.035,1.67),(3.96,.045,2.24)),'Cinema_Black')
for x in [-1.65,1.65]:
 for y in [1.30,3.80,6.45]:
  put('Cinema_Downlight_Rim_%s_%s'%(x,y),torus((x,y,H-.018),.075,.013,(0,0,1),24,6),'Cinema_Metal',smooth=True)
  put('Cinema_Downlight_Diffuser_%s_%s'%(x,y),cylinder((x,y,H-.023),(x,y,H-.027),.061,segments=24),'Cinema_Light')
  s.lights.append({'position':[x,y,H-.10],'energy':75,'angle':105,'color':[1,.89,.68]})
put('Cinema_Projector_Mount',cylinder((0,4.65,H),(0,4.65,H-.19),.025,segments=12),'Cinema_Metal')
put('Cinema_Ceiling_Projector',box((0,4.65,H-.27),(.37,.31,.15),bevel=.025),'Cinema_Offwhite')
put('Cinema_Projector_Lens',cylinder((-.11,4.48,H-.27),(-.11,4.44,H-.27),.037,segments=20),'Cinema_Black')
s.views=[{'id':'cinema','title':'السينما — من مؤخرة القاعة','position':[0,7.65,1.65],'target':[.25,.10,1.55],'reference_image':'../../references/fidelity-2026-10-26/cinema-reference.jpg','reference_label':'Sinevizyon · الصورة المنشورة للقاعة'}, {'id':'cinemaseats','title':'المقاعد والممر الوسطي','position':[0,5.80,1.65],'target':[-1.3,3.4,.65],'reference_image':'../../references/fidelity-2026-10-26/cinema-reference.jpg'}, {'id':'cinemadoor','title':'الباب بجانب الشاشة — متصل بقاعة الخريطة','position':[0,1.0,1.65],'target':[-2.3,0,1.1],'reference_image':'../../references/fidelity-2026-10-26/cinema-reference.jpg'}]
# Place the room beside the stair; source photograph establishes the internal door side.
# The user's 2026-10-26 observation establishes adjacency, not surveyed coordinates.
ANGLE=-math.pi/2;ORIGIN=np.array([44.5,.11,-4.2])
ROT=np.array([[math.cos(ANGLE),-math.sin(ANGLE),0],[math.sin(ANGLE),math.cos(ANGLE),0],[0,0,1]])
def global_point(p):return (np.einsum('ij,j->i',ROT,np.asarray(p))+ORIGIN).tolist()
s.flush()
for obj in s.objects:obj['vertices']=(np.einsum('ij,nj->ni',ROT,np.asarray(obj['vertices']))+ORIGIN).tolist()
for text in s.texts:text['location']=global_point(text['location']);text['rotation']=list(text['rotation']);text['rotation'][2]+=ANGLE
for light in s.lights:light['position']=global_point(light['position'])
for view in s.views:
 view['position']=global_point(view['position']);view['target']=global_point(view['target'])
s.views.insert(0,{'id':'cinemaconnection','title':'من أسفل الدرج إلى السينما','position':[43.45,2.4,-2.55],'target':[46.0,2.4,-2.55],'reference_image':'../../references/fidelity-2026-10-26/cinema-reference.jpg','reference_label':'السينما الحقيقية؛ الاتصال بالدرج حسب إفادة المستخدم'})
s.save(ROOT/'reconstruction/part08-scene.json')
report={'title':'دراسة مرجعية للسينما في الطابق السفلي','source_url':'https://gamaakademi.com.tr/salonlar.php','image_url':'https://gamaakademi.com.tr/uploads/halls/6aa3f6962e8f7_1789130390.jpg','source_identity':'Page published under museum name; corroborating municipality page confirms cinevision room existence. Site affiliation and capture date not independently confirmed.','floor':'-1 per user and published hall listing','modeled_dimensions_m':[W,D,H],'modeled_seats':len(centres),'seat_count_verified':False,'global_placement':'USER_CONFIRMED_ADJACENCY - beside stair on the right viewed from map hall; global metric transform remains estimated','global_origin_author_m':ORIGIN.tolist(),'global_yaw_rad':ANGLE,'user_observation':'2026-10-26: cinema beside the stair on the right','visible_features':['central aisle with three chairs per bank','dark upholstered armchairs on wooden legs','timber acoustic sidewall panels','perforated grey ceiling with round downlights','ceiling projector','large front screen','doorway to screen right with exit light'],'unverified':['exact width,length,height','total seat count and row pitch','rear wall and exact connector dimensions','surveyed door coordinates; right side interpreted from map-hall viewpoint','current condition and source photo date'],'accuracy_100_percent':False}
(ROOT/'reconstruction/part08-notes.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
