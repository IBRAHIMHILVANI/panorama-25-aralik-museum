"""Panorama, curved access stair and village viewing ring, IMG_2214–2258.
122m canvas circumference and 13m height follow the museum publication.
Arrangement and levels are an explicitly photo-informed reconstruction, not a survey.
"""
from museum_geometry import *
from museum_architecture import *
from museum_exhibits import photo_material,projected_panel,emit_reference_prop
from museum_diorama_props import *
from shapely.geometry import Polygon,Point,LineString,box as rect
from shapely.ops import unary_union
from panorama_reference_details import tank_terrace_rail,tank_wagon_canopies,upper_corridor_details
s=Scene('07_Panorama');P=np.array([-26.,13.]);R=122/(2*math.pi);F=-4.2;LEVEL=0.;SG=-.45;SC=np.array([-29.,16.]);SR=2.8;SA=135.;SB=315.;SW=2.1

def xy(r,a,c=P):a=math.radians(a);return c+r*np.array([math.cos(a),math.sin(a)])
def xyz(r,a,z,c=P):return (*xy(r,a,c),z)
def sector(c,ri,ro,a,b,n=80):return Polygon([xy(ro,t,c) for t in np.linspace(a,b,n)]+[xy(ri,t,c) for t in np.linspace(b,a,n)])
def cube(name,p,d,mat,refs='',yaw=0,collision=False):s.add(name,box(p,d,yaw),mat,refs,collision=collision)
def wall_between(name,p,q,z0,z1,width,mat,refs='2217'):
 p,q=np.array(p),np.array(q);v=q-p;cube(name,(*(p+q)/2,(z0+z1)/2),(np.linalg.norm(v),width,z1-z0),mat,refs,math.atan2(v[1],v[0]),True)
scenic_materials(s)
for name,col,rough,metal,alpha,em in [('Stone_Base',(.48,.435,.35),.95,0,1,0),('Walk_Stone',(.34,.32,.27),.86,0,1,0),('Backstage',(.13,.12,.10),.95,0,1,0),('Stair_Wall',(.48,.47,.425),.85,0,1,.04),('Stair_Step',(.47,.46,.42),.72,0,1,0),('Handrail',(.32,.34,.32),.35,.7,1,0),('Step_Light',(.99,.90,.72),.5,0,1,4),('Canopy',(.48,.34,.19),.97,0,1,0),('Window_Glass',(.75,.81,.78),.1,0,.08,0),('Lettering',(.90,.85,.72),.7,0,1,.1)]:s.mat(name,col,rough,metal,alpha,em)
for i in range(6):s.mat('Stone_'+str(i),(.49+i*.032,.44+i*.029,.35+i*.025),.93)
# Covered connection from final gallery into the stair foot. Geometry is estimated.
start=np.array([-6+37*math.cos(math.radians(168)),23.5+37*math.sin(math.radians(168))]);foot=xy(SR,SA,SC)
entryline=LineString([start,(-40.8,28.8),tuple(foot)]);entry=entryline.buffer(1.16,cap_style=2,join_style=2)
s.add('Panorama_Entry_Floor',polygon_plate(entry,F),'Walk_Stone','2214',collision=True)
s.add('Panorama_Entry_Ceiling',polygon_plate(entry,F+2.6,False),'Stair_Wall','2214')
for i,edge in enumerate([entryline.offset_curve(1.16),entryline.offset_curve(-1.16)]):
 from shapely.ops import substring
 pts=list(substring(edge,0,max(.1,edge.length-1.45)).coords)
 for j,(p,q) in enumerate(zip(pts,pts[1:])):wall_between('Entry_Tunnel_Wall_'+str(i)+'_'+str(j),p,q,F,F+2.6,.14,'Stair_Wall','2214')
s.add('Panorama_Stair_Bottom_Landing',polygon_plate(Point(*foot).buffer(1.18,quad_segs=32),F),'Walk_Stone','2214',collision=True)
# Curved steps, one continuous navigation ramp, independent handrails.
stairwell=sector(SC,SR-SW/2-.15,SR+SW/2+.15,SA,SB,100)
for i in range(28):
 a=SA+(SB-SA)*i/28;b=SA+(SB-SA)*(i+1)/28;top=F+(i+1)*(-F)/28
 s.add('Panorama_Stair_Tread_%02d'%i,arc_band(SC,SR-SW/2,SR+SW/2,math.radians(a),math.radians(b),top-.15,top,6),'Stair_Step','2214-2215')
 # Side lamps align to real risers without protruding into the walking envelope.
 if i%2==0:
  for rr in [SR-SW/2-.045,SR+SW/2+.045]:cube('Stair_Recess_Lamp_%d_%s'%(i,rr),xyz(rr,b,top+.10,SC),(.045,.09,.055),'Step_Light','2214-2215',math.radians(b))
nav=Mesh();wallL=Mesh();wallR=Mesh();ceiling=Mesh();stair_soffit=Mesh()
N=112
for i in range(N):
 a=SA+(SB-SA)*i/N;b=SA+(SB-SA)*(i+1)/N;za=F+(-F)*i/N;zb=F+(-F)*(i+1)/N
 p0=xy(SR-SW/2,a,SC);p1=xy(SR+SW/2,a,SC);q0=xy(SR-SW/2,b,SC);q1=xy(SR+SW/2,b,SC)
 nav.append([[*p0,za],[*p1,za],[*q1,zb],[*q0,zb]],[[0,1,2,3]])
 # Roof/underside extend through the side-wall planes, closing the old7cm
 # edge slits while leaving the tested walking ramp width unchanged.
 cp0=xy(SR-SW/2-.12,a,SC);cp1=xy(SR+SW/2+.12,a,SC);cq0=xy(SR-SW/2-.12,b,SC);cq1=xy(SR+SW/2+.12,b,SC)
 ceiling.append([[*cp0,za+2.58],[*cp1,za+2.58],[*cq1,zb+2.58],[*cq0,zb+2.58]],[[3,2,1,0]])
 stair_soffit.append([[*cp0,za-.18],[*cp1,za-.18],[*cq1,zb-.18],[*cq0,zb-.18]],[[0,1,2,3]])
 for rr,target in [(SR-SW/2-.07,wallL),(SR+SW/2+.07,wallR)]:
  ap,bp=xy(rr,a,SC),xy(rr,b,SC);target.append([[*ap,za-.18],[*bp,zb-.18],[*bp,zb+2.6],[*ap,za+2.6]],[[0,1,2,3]])
 for rr in ([] if a<SA+12 else [SR-SW/2+.07,SR+SW/2-.07]):s.batch('Panorama_Stair_Handrails',cylinder(xyz(rr,a,za+.91,SC),xyz(rr,b,zb+.91,SC),.024,segments=8),'Handrail','2214-2215')
s.add('NAV_Panorama_Stair_Ramp',nav,'Stair_Step','2214-2215',collision=True,hidden=True)
for name,m in [('Left',wallL),('Right',wallR)]:s.add('Panorama_Stair_Wall_'+name,m,'Stair_Wall','2214-2215',collision=True)
s.add('Panorama_Stair_Ceiling',ceiling,'Stair_Wall','2214-2215')
s.add('Panorama_Stair_Continuous_Underside',stair_soffit,'Stair_Wall','IMG_2214-2217: enclosed stair; underside form estimated')
for a in [155,205,255,300]:
 z=F+(-F)*(a-SA)/(SB-SA);s.lights.append({'position':list(xyz(SR,a,z+2.35,SC)),'energy':30,'angle':110,'color':[1,.88,.71]})
# The last tunnel wall segments previously stopped short of the stair foot,
# leaving the sky visible around the round landing. Enclose their actual union,
# with openings only toward the existing tunnel and continuing stair.
junction_refs='Original IMG_2214-2217: continuous enclosed stair and passage'
junction_basis='Local closure of existing modeled tunnel/landing boundaries; metric dimensions estimated, route unchanged'
tail_start=np.array(entryline.interpolate(entryline.length-3.0).coords[0]);tail=LineString([tail_start,foot]);tail_dir=foot-tail_start;tail_dir/=np.linalg.norm(tail_dir);tail_n=np.array([-tail_dir[1],tail_dir[0]])
junction_end=SA+12
junction=tail.buffer(1.16,cap_style=2).union(Point(*foot).buffer(1.20,quad_segs=32)).union(sector(SC,SR-SW/2-.12,SR+SW/2+.12,SA,junction_end,30)).buffer(0)
tunnel_open=LineString([tail_start-tail_n*1.40,tail_start+tail_n*1.40]).buffer(.15,cap_style=2)
stair_open=LineString([xy(SR-SW/2-.32,junction_end,SC),xy(SR+SW/2+.32,junction_end,SC)]).buffer(.15,cap_style=2)
stair_flow=sector(SC,SR-SW/2-.02,SR+SW/2+.02,SA-.5,SB,100)
wall_shell=junction.buffer(.10,join_style=2).difference(junction).difference(tunnel_open.union(stair_open)).difference(stair_flow)
for i,pp in enumerate(polygon_parts(wall_shell)):s.add('Panorama_Stair_Foot_Enclosure_'+str(i),extrude_xy(pp,F-.08,F+3.30),'Stair_Wall',junction_refs,junction_basis,collision=True)
junction_roof=polygon_plate(junction.difference(stairwell.buffer(-.05)),F+2.58,False)
for v in junction_roof.vertices:
 angle=math.degrees(math.atan2(v[1]-SC[1],v[0]-SC[0]));rise=max(0,min(30,angle-SA))*(-F)/(SB-SA)
 v[2]+=rise
s.add('Panorama_Stair_Foot_Junction_Ceiling',junction_roof,'Stair_Wall',junction_refs,junction_basis+'; ceiling follows first stair rise',collision=True)
known_floor=entry.union(Point(*foot).buffer(1.18,quad_segs=32)).union(stairwell)
for i,pp in enumerate(polygon_parts(junction.difference(known_floor))):s.add('Panorama_Stair_Foot_Floor_Infill_'+str(i),polygon_plate(pp,F),'Stair_Step',junction_refs,junction_basis,collision=True)
# A solid foundation closes views UNDER the sloping stair underside. It is
# wholly below the lowest walking floor; the tested ramp/steps do not move.
foundation=stairwell.union(junction).buffer(.12,join_style=2)
s.add('Panorama_Stair_Below_Floor_Foundation',extrude_xy(foundation,F-.45,F-.22),'Stair_Wall',junction_refs,'Foundation below existing lowest floor closes under-stair void; depth estimated',collision=True)
s.lights.append({'position':[*foot,F+2.42],'energy':18,'angle':115,'color':[1,.88,.71]})
# Top landing turns toward the covered village viewing path.
end=xy(SR,SB,SC);d=np.array([math.cos(math.radians(45)),math.sin(math.radians(45))]);n=np.array([-d[1],d[0]])
landing=Polygon([end-n*1.10,end+n*1.10,end+d*1.7+n*1.10,end+d*1.7-n*1.10]);s.add('Panorama_Top_Landing',polygon_plate(landing,0),'Walk_Stone','2216',collision=True)
top_cover=landing.buffer(.12,join_style=2).union(LineString([end,(-25.82,15.22),(-27.0,16.0)]).buffer(1.12,cap_style=2,join_style=2))
s.add('Panorama_Top_Landing_Cover',polygon_plate(top_cover,2.76,False),'REF_Wood','IMG_2216-2217: covered landing and passage','Coverage follows existing landing; timber structure and dimensions estimated',collision=True)
s.add('Panorama_Top_Ceiling_Height_Fascia',box(xyz(SR,SB,2.69,SC),(SW+.30,.18,.22),math.radians(SB)),'Stair_Wall','IMG_2216-2217','Closure above open stair exit; existing route unchanged',collision=True)
platform=Point(*P).buffer(9.35,quad_segs=128).difference(Point(*P).buffer(5.60,quad_segs=128))
for pp in polygon_parts(platform):s.add('Panorama_Viewing_Floor_'+str(len(s.objects)),polygon_plate(pp,0),'Walk_Stone','2216-2258',collision=True)
# Hand-laid paving stones on the accessible platform; floor collider remains smooth.
for a in np.arange(0,360,2.3):
 for j,r in enumerate(np.arange(5.7,9.3,.25)):
  tile=sector(P,r,r+.235,a+(j%2)*1.15,a+(j%2)*1.15+2.1,4).intersection(platform)
  for pp in polygon_parts(tile):s.batch('Panorama_Walk_Cobbles',polygon_plate(pp,.003),'Stone_'+str((int(a)+j)%6),'2216-2218,2233')
# Cylinder shell has a low doorway for the covered access, below the painted canvas.
ring=Point(*P).buffer(R+.35,quad_segs=128).difference(Point(*P).buffer(R+.08,quad_segs=128))
for pp in polygon_parts(ring.difference(entry.buffer(.05))):s.add('Panorama_Lower_Envelope_'+str(len(s.objects)),extrude_xy(pp,-4.5,-1.6),'Backstage','exterior/2214',collision=True)
s.add('Panorama_Upper_Envelope',extrude_xy(ring,-1.6,12.8),'Backstage','published 122m canvas; envelope thickness estimated',collision=True)
s.add('Panorama_Building_Roof',polygon_plate(Point(*P).buffer(R+.35,quad_segs=128),12.8,False),'Backstage','Indoor panorama and continuous covered circulation, IMG_2214-2258','Plain enclosing roof at existing shell height; hidden construction shape unmeasured',collision=True)
# The original supplied panoramic photography, in observed sequence. No foreign museum sky.
murals=[(2254,100,160,[(.06,.11),(.99,.10),(.99,.57),(.06,.57)]),(2225,160,202,[(.02,.03),(.98,.03),(.98,.57),(.02,.57)]),(2231,202,242,[(.04,.08),(.90,.12),(.93,.65),(.03,.61)]),(2234,242,284,[(.01,.02),(.98,.04),(.98,.55),(.01,.58)]),(2239,284,326,[(.02,.04),(.99,.06),(.99,.54),(.02,.56)]),(2246,326,368,[(.04,.02),(.98,.08),(.98,.55),(.04,.54)]),(2247,368,412,[(.01,.01),(.99,.04),(.99,.51),(.01,.49)]),(2252,412,460,[(.02,.05),(.99,.12),(.99,.53),(.02,.57)])]
# Higher-resolution photographs of the same identifiable mural sections.
# Alignment remains a provisional panorama reconstruction, not an orthographic source painting.
published={2254:(4,[(.01,.02),(.99,.02),(.99,.51),(.01,.51)]),2225:(5,[(.01,.065),(.99,.065),(.99,.49),(.01,.49)]),2231:(6,[(.01,.01),(.99,.01),(.99,.47),(.01,.47)]),2234:(9,[(.01,.23),(.99,.22),(.99,.60),(.01,.60)]),2239:(10,[(.01,.01),(.99,.01),(.99,.48),(.01,.48)])}
for n,a,b,quad in murals:
 if n in published:
  pub,quad=published[n];curved_photo(s,'Panorama_Published_Canvas_%02d'%pub,n,P,R,a,b,SG,13,quad,72)
  mat='Photo_Published_Panorama_%02d'%pub;s.mat(mat,(1,1,1),.8,emission=.12,image='textures/Published_Panorama_%02d.jpg'%pub)
  s.objects[-1]['material']=mat;s.objects[-1]['source_photos']='published gallery photograph %02d, visually matched to user IMG_%s; references/fidelity-2026-10-26/panorama-source-index.json'%(pub,n)
 else:curved_photo(s,'Panorama_Original_Canvas_'+str(n),n,P,R,a,b,SG,13,quad,72)

# Terrain excludes the stair enclosure; lower scenic level is an estimated 1.25m below the viewing ring.
scenic=Point(*P).buffer(R-.08,quad_segs=128).difference(Point(*P).buffer(9.55,quad_segs=128)).difference(stairwell.buffer(.12))
for i,pp in enumerate(polygon_parts(scenic)):terrain(s,'Panorama_Earth_'+str(i),pp,SG,2222,.16)
# Solid masonry is retained except one photo-supported iron bay left of the tank.
# 288–306 degrees is a bounded model placement estimate, not a surveyed angle.
wallpoly=Point(*P).buffer(9.55,quad_segs=128).difference(Point(*P).buffer(9.34,quad_segs=128)).difference(stairwell.buffer(.1)).difference(landing.buffer(.08))
iron_bay=sector(P,9.30,9.60,288,306,64)
for i,pp in enumerate(polygon_parts(wallpoly.difference(iron_bay))):s.add('Panorama_Visitor_Parapet_'+str(i),extrude_xy(pp,-.03,.78),'Stone_Base','2218-2258',collision=True)
tank_terrace_rail(s,P,xy,xyz)
# Rubble bands are real individual solids, with named original-photo evidence.
for a,photo in [(133,2222),(216,2230),(263,2234),(308,2239),(350,2243),(390,2247),(439,2252)]:rubble(s,'Panorama_Rubble_'+str(a),xyz(13.8,a,SG+.10),4.8,4.0,80,photo,math.radians(a)-math.pi/2,.5)
# Trench in the first battlefield view.
a=134;yaw=math.radians(a)-math.pi/2;pos=xyz(13.1,a,SG+.17)
for y in [-.75,.75]:
 for z in [.10,.24,.38,.52]:s.batch('Battlefield_Trench_Timbers',cylinder((-2.7,y,z),(2.7,y,z),.062,segments=10).transformed(pos,yaw),'REF_Wood','2222-2224')
 for x in np.linspace(-2.5,2.5,9):s.batch('Trench_Uprights',cylinder((x,y,0),(x,y,.72),.045,segments=8).transformed(pos,yaw),'REF_Wood','2222-2224')
roof_tiles(s,'Village_Roof_Tiles',xyz(12.7,180,-.18),6.0,4.1,math.radians(180)-math.pi/2,'2225-2228')
cube('Village_Chimney',xyz(12.1,183,.60),(.75,.75,1.55),'Stone_Base','2225',math.radians(183))
# Well with rope spindle and bucket, rather than a photo plane.
well=xyz(11.4,223,SG+.20);s.add('Stone_Well',arc_band(well[:2],.55,.78,0,TAU,well[2],well[2]+.90,60),'Stone_2','2230-2231')
for x in [-.65,.65]:s.add('Well_Post_'+str(x),box((x,0,1.10),(.15,.15,2.2)).transformed(well),'REF_Wood','2230')
s.add('Well_Spindle',cylinder((-.83,0,1.53),(.83,0,1.53),.10,segments=18).transformed(well),'REF_Wood_Light','2230');s.add('Well_Rope',cylinder((.2,0,.25),(.2,0,1.55),.012,segments=6).transformed(well),'Rope_Fibre','2230')
emit_reference_prop(s,old.pot,('Bucket',(0,0,0),.18,.33,'REF_Iron','2230',True),xyz(10.6,224,SG+.25),0,'2230','Well')
emit_reference_prop(s,old.cannon,('Panorama_Cannon',(0,0,0),0,'2234'),xyz(11.8,263,SG+.17),math.radians(263)+math.pi,'2234-2236','Battle')
emit_reference_prop(s,old.tank,((0,0,0),0),xyz(12.3,307,SG+.15),math.radians(307)+math.pi/2,'2237-2240','Battle')
wagon(s,'Panorama_Wagon',xyz(12.8,350,SG+.20),math.radians(350)-math.pi/2,False,'2241-2243')
# Hospital courtyard tableau, beds, people and pots are separate editable meshes.
for j in range(3):
 pos=xyz(11.7+.80*(j%2),380+j*5,SG+.21);yaw=math.radians(385)-math.pi/2
 emit_reference_prop(s,old.mattress,('Mattress_'+str(j),(0,0,0),0),pos,yaw,'2244-2247','Hospital')
 emit_reference_prop(s,old.patient,('Patient_'+str(j),(0,0,0),0),pos,yaw,'2244-2247','Hospital')
for j,(r,a) in enumerate([(13.0,382),(12.0,398),(14.1,390)]):emit_reference_prop(s,old.person,('Carer_'+str(j),(0,0,0),0,True,True,'REF_Cloth_Red','REF_Cloth_Green','REF_Cloth_Cream','2244-2247','nurse'),xyz(r,a,SG+.20),math.radians(a)-math.pi/2,'2244-2247','Hospital')
for j in range(7):emit_reference_prop(s,old.pot,('Hospital_Pot_'+str(j),(0,0,0),.16+.035*(j%3),.27,'REF_Copper','2244',True),xyz(10.4+.5*(j%2),379+j*3,SG+.20),0,'2244-2247','Hospital')
roof_tiles(s,'Last_Roof_Tiles',xyz(12.2,437,-.34),5.2,4.0,math.radians(437)-math.pi/2,'2251-2252')
# Covered village edge: facades and cloth shades seen from the real viewing path.
for a in np.arange(0,360,30):
 # Keep the stair exit and its sightline open.
 if 113<a<151:continue
 if a>=300:continue # detailed, irregular tank/wagon sheets replace these sectors below
 end_angle=287.95 if a==270 else a+29.8
 v=[];f=[]
 for j,r in enumerate(np.linspace(5.72,9.55,9)):
  for i,t in enumerate(np.linspace(a,end_angle,20)):
   z=2.88+.28*(9.55-r)/3.83+.06*math.sin(i*math.pi/3)*(r-5.7)/3.8;v.append([*xy(r,t),z])
 for j in range(8):
  for i in range(19):k=j*20+i;f.append([k,k+1,k+21,k+20])
 s.batch('Village_Cloth_Canopies',Mesh().append(v,f),'Canopy','2232-2233,2240-2258')
 for rr in [5.8,9.4]:s.batch('Canopy_Timber_Edges',arc_line(P,rr,math.radians(a),math.radians(end_angle),2.86,.045,15),'REF_Wood','2233-2258')
 s.batch('Canopy_Radial_Beams',cylinder(xyz(5.75,a,3.13),xyz(9.55,a,2.85),.045,segments=8),'REF_Wood','2233-2258')
 s.batch('Inner_Facade_Posts',cylinder(xyz(5.82,a,0),xyz(5.82,a,3.12),.08,segments=10),'REF_Wood','2217,2249')
canopy_details=tank_wagon_canopies(s,xy,xyz)
# The upper stone passage crosses the village core to the viewing ring.
upper_line=LineString([(-25.82,15.22),(-27.0,16.0),(-28.25,19.15),tuple(xy(7.4,110))])
upper_floor=upper_line.buffer(1.05,cap_style=2,join_style=2)
s.add('Upper_Village_Passage_Floor',polygon_plate(upper_floor,0),'Walk_Stone','2216-2217',collision=True)
# Covered length stops at the facade opening; the balcony beyond stays open.
covered_line=LineString([(-25.82,15.22),(-27.0,16.0),(-28.0,18.55)])
for i,edge in enumerate([covered_line.offset_curve(1.05),covered_line.offset_curve(-1.05)]):
 from shapely.ops import substring
 pts=list(substring(edge,.85,edge.length).coords)
 for j,(p,q) in enumerate(zip(pts,pts[1:])):wall_between('Upper_Stone_Passage_Wall_'+str(i)+'_'+str(j),p,q,0,2.75,.12,'Stone_2','2216-2217')
s.add('Upper_Stone_Passage_Ceiling',polygon_plate(covered_line.buffer(1.12,cap_style=2,join_style=2),2.76,False),'REF_Wood','2216-2217')
upper_corridor_details(s,covered_line)
s.lights.append({'position':[-27,17.0,2.50],'energy':35,'angle':120,'color':[1,.65,.36]})
# Central scenic village wall, with two true open exhibit windows.
for a,b in [(0,35),(55,67),(90,98),(121,360)]:s.add('Village_Inner_Stone_Wall_'+str(a),arc_band(P,5.52,5.74,math.radians(a),math.radians(b),0,2.72,max(4,int(b-a))),'Stone_3','2217,2249-2250',collision=True)
for id,a,n in [('kitchen',45,2249),('medical',78.5,2250)]:
 yaw=math.radians(a)+math.pi/2;origin=xyz(5.70,a,0)
 # Window opens onto a deep lit alcove, not an opaque framed photograph.
 opening=rect(-1.0,.65,1.0,2.32)
 masonry_portal(s,id+'_Window_Wall',2.60,0,2.80,.20,origin,yaw,opening,str(n),.46,.29)
 cube(id+'_Alcove_Back',xyz(3.5,a,1.35),(2.8,.20,2.7),'Stone_4',str(n),yaw,True)
 alcove=sector(P,3.5,5.7,a-14,a+14,30);s.add(id+'_Alcove_Floor',polygon_plate(alcove,0),'Walk_Stone',str(n));s.add(id+'_Alcove_Ceiling',polygon_plate(alcove,2.78,False),'REF_Wood',str(n))
 for edge in [a-14,a+14]:wall_between(id+'_Alcove_Side_'+str(edge),xy(3.5,edge),xy(5.7,edge),0,2.80,.15,'Stone_4',str(n))
 for off in [-1.08,1.08]:s.batch('Village_Window_Timbers',box((off,0,1.50),(.12,.22,1.8)).transformed(origin,yaw),'REF_Wood',str(n))
 s.add(id+'_Window_Glass',panel(2,1.67).transformed((0,-.03,.65)).transformed(origin,yaw),'Window_Glass',str(n),collision=True)
 s.lights.append({'position':list(xyz(4.6,a,2.5)),'energy':55,'angle':120,'color':[1,.57,.28]})
 if id=='kitchen':
  emit_reference_prop(s,old.person,('Kitchen_Woman',(0,0,0),0,False,True,'REF_Black','REF_Cloth_Green','REF_Cloth_Cream','2249'),xyz(4.35,a,0),yaw,'2249','Kitchen')
  for j in range(6):emit_reference_prop(s,old.pot,('Kitchen_Pot_'+str(j),(0,0,0),.13+.02*(j%3),.20,'REF_Copper','2249',True),xyz(4.9,37+j*3,.80),0,'2249','Kitchen')
 else:
  bed=xyz(4.5,a,.55);cube('Medical_Treatment_Table',xyz(4.5,a,.40),(1.0,1.7,.8),'REF_Wood','2250',yaw)
  emit_reference_prop(s,old.patient,('Treatment_Patient',(0,0,0),0),bed,yaw,'2250','Medical')
  for j,(rr,aa) in enumerate([(3.9,68),(4.0,89)]):emit_reference_prop(s,old.person,('Clinician_'+str(j),(0,0,0),0,False,j==0,'REF_Cloth_White','REF_Cloth_White','REF_Cloth_White','2250','nurse'),xyz(rr,aa,0),yaw,'2250','Medical')
# Soft ambient fixtures keep the historic panorama legible without baking fake lights into photos.
for a in np.arange(0,360,30):s.lights.append({'position':list(xyz(14.5,a,6.2)),'target':list(xyz(13,a,-.4)),'energy':350,'angle':120,'color':[1,.88,.70]})
for a in np.arange(0,360,45):s.lights.append({'position':list(xyz(7.7,a,2.55)),'energy':25,'angle':120,'color':[1,.78,.50]})
s.views=[{'id':'panoramastair','title':'درج الصعود إلى البانوراما','position':[*xy(SR,145,SC),F+(-F)*(145-SA)/(SB-SA)+1.65],'target':[*xy(SR,172,SC),F+(-F)*(172-SA)/(SB-SA)+1.4],'photo':2214}]
for id,title,a,targetr,photo in [('panorama','القاعة البانورامية الكاملة',135,17,2254),('rooftops','سطوح المدينة',183,14,2225),('well','البئر والميدان',223,12,2231),('cannon','المدفع في البانوراما',263,12,2234),('tank','الدبابة',307,12.3,2239),('wagon','العربة الخشبية',350,12.8,2242),('hospital','مشهد الإسعاف',389,12,2247),('kitchen','نافذة المطبخ',45,4.3,2249),('medical','غرفة العلاج',78.5,4.4,2250)]:s.views.append({'id':id,'title':title,'position':list(xyz(7.4,a,1.65)),'target':list(xyz(targetr,a,.5 if targetr>9 else 1.2)),'photo':photo})
s.views.extend([{'id':'tankrail','title':'تفصيل الدرابزين الحديدي قرب الدبابة','position':list(xyz(7.4,297,1.65)),'target':list(xyz(9.45,297,.70)),'reference_image':'../../references/live-review-2026-10-26/13-panorama-floor-arch-may2026.png'}, {'id':'canopydetail','title':'تفاصيل القماش والحبال فوق مسار المشاهدة','position':list(xyz(7.4,328,1.65)),'target':list(xyz(8.5,331,2.85)),'photo':2242}])
s.save(ROOT/'reconstruction/part07-scene.json')
(ROOT/'reconstruction/part07-notes.json').write_text(json.dumps({'source_photos':'2214-2258','canvas_circumference_m':122,'canvas_height_m':13,'canvas_radius_m':R,'levels_m':{'gallery':F,'viewing_platform':0,'scenic_ground':SG},'accuracy_100_percent':False,'limits':['Canvas dimensions from publication; platform elevation, stair and room layout are photo-informed estimates','Eight source-photo panels remain a provisional alignment; five now use visually matched5184px published photographs. The other three use restored original HEIC pixels. No seamless measured stitch claim','All fine figurine anatomy and unseen structures estimated','All 319 original source photographs restored locally on 2026-10-26, including IMG_2216/2217; no SSD or low-resolution-source blocker remains', 'Observed ironwork, cloth details and corridor joists/lanterns added in bounded areas; metric placement remains estimated and unlocated arch topology is unchanged']},indent=2,ensure_ascii=False))

(ROOT/'reconstruction/part07-reference-details.json').write_text(json.dumps({'observed_sources':['live-review-2026-10-26/03,13,14,15,16','restored IMG_2214,2215,2216,2217,2239,2242'],'original_textures_restored':319,'iron_bay':{'model_angle_degrees':[288,306],'placement':'estimated bay to camera-left of model tank; not surveyed','base_height_m':.24,'top_rail_height_m':1.125,'continuous_hidden_barrier':True,'walking_radius_m':7.4},'canopy':canopy_details,'corridor':'round timber joists and two hanging lanterns within existing passage; spacing estimated','stair_foot_enclosure':{'basis':junction_basis,'evidence':junction_refs,'ceiling_height_above_landing_m':2.60,'retained_openings':['existing tunnel','existing continuing stair'],'floor_plan':'union of existing tunnel tail, round landing and first12degrees of stair; full continuing stair flow excluded from wall shell, no rerouting','roof':'junction roof follows stair rise; main stair roof and underside extend through side-wall planes; upper landing roof and plain building roof at existing12.8m shell close remaining openings'},'unresolved':'stone arch exists in source but exact passage topology/position not established; no new arch or route added'},indent=2))
