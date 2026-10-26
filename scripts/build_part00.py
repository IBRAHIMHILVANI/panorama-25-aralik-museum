"""Mapped 15 Temmuz tram environment and >=100m museum surroundings.
Horizontal source geometry: OpenStreetMap, ODbL. Vehicle envelope: Gaziulaş PT8 specs.
Street widths, building elevations and unphotographed facades remain estimates.
"""
from museum_geometry import *
from museum_architecture import *
from museum_diorama_props import flag
from shapely.geometry import shape,Point,LineString,Polygon,box as rect,mapping
from shapely.ops import unary_union,substring
from shapely import get_parts
s=Scene('00_Tram_Streets_Surroundings');G=-1.73;SIDE=-1.60;RAIL=G+.025;PLAT=RAIL+.32
j=json.loads((ROOT/'references/geospatial/local-map.geojson').read_text());meta=j['metadata'];features=j['features'];scope=shape(meta['scope_polygon']);museum=shape(meta['museum_complex_footprint']);rng=np.random.default_rng(20261026)
for name,col,rough,metal,alpha,em in [
 ('Ground',(.54,.54,.49),.95,0,1,0),('Asphalt',(.24,.255,.26),.91,0,1,0),('Street_Stone',(.40,.42,.415),.92,0,1,0),('Sidewalk',(.61,.61,.56),.86,0,1,0),('Curb',(.66,.64,.58),.8,0,1,0),('Grass',(.25,.34,.16),.98,0,1,0),('Rail_Bed',(.48,.36,.29),.92,0,1,0),('Steel',(.22,.25,.25),.45,.65,1,0),('Rail_Steel',(.36,.40,.42),.27,.8,1,0),('Pole_Green',(.09,.28,.20),.52,.4,1,0),('Frame_Grey',(.28,.31,.32),.52,.5,1,0),('Black',(.055,.07,.075),.57,0,1,0),('Shelter_Glass',(.65,.80,.82),.12,.1,.24,0),('Tactile_Yellow',(.88,.61,.08),.76,0,1,0),('White',(.84,.85,.81),.56,0,1,0),('Orange',(.94,.32,.055),.48,0,1,0),('Tram_Glass',(.13,.19,.20),.15,.15,.60,0),('Front_Glass',(.075,.11,.12),.14,.2,.88,0),('Tram_Interior',(.63,.65,.62),.70,0,1,0),('Seat',(.13,.27,.39),.80,0,1,0),('Rail_Bellows',(.18,.19,.18),.95,0,1,0),('Lettering',(.93,.94,.88),.7,0,1,.1),('Display_Amber',(.98,.63,.07),.5,0,1,1),('River',(.19,.29,.28),.16,.25,1,0),('Canal_Stone',(.47,.43,.35),.93,0,1,0),('Tree_Bark',(.27,.24,.18),.95,0,1,0),('Roof_Tile',(.52,.29,.18),.89,0,1,0),('Window',(.19,.25,.27),.3,.2,1,0),('REF_Flag',(.70,.035,.05),.90,0,1,0),('REF_Cloth_White',(.95,.95,.9),.9,0,1,0),('REF_Wood',(.29,.21,.13),.9,0,1,0)]:s.mat(name,col,rough,metal,alpha,em)
for i in range(7):s.mat('Facade_'+str(i),(.58+i*.035,.55+i*.035,.46+i*.035),.92)
for i in range(4):s.mat('Leaves_'+str(i),(.16+i*.035,.25+i*.03,.09+i*.015),.98)
for i in range(5):s.mat('Paver_'+str(i),(.46+i*.045,.48+i*.043,.46+i*.04),.85)
def local(p,z=None):return enu_to_author((*p,z)) if z is not None else enu_to_author(p)
def addpoly(name,p,z,mat,refs,collision=True):
 for i,g in enumerate(polygon_parts(p)):
  if g.area>.005:s.add(name+'_'+str(i),polygon_plate(mapped_polygon(g),z),mat,refs,collision=collision)
def ex(name,p,z0,z1,mat,refs,collision=True):
 for i,g in enumerate(polygon_parts(p)):
  if g.area>.005:s.add(name+'_'+str(i),extrude_xy(mapped_polygon(g),z0,z1),mat,refs,collision=collision)
def lineparts(g):return [x for x in get_parts(g) if x.geom_type in ['LineString','LinearRing']]
def lines(name,line,z,rad,mat,refs,collision=False):
 for pp in lineparts(line):
  for a,b in zip(list(pp.coords),list(pp.coords)[1:]):
   if np.linalg.norm(np.array(a)-b)>.001:s.batch(name,cylinder(local(a,z),local(b,z),rad,segments=8),mat,refs,collision=collision)
def placed(name,m,origin,yaw,mat,refs='',collision=False):
 if not m.vertices:return
 m=m.transformed(local(origin[:2],origin[2]),yaw+math.radians(130))
 if name.startswith(('Station_Tile_','Tactile_')):s.batch('Station_Paving',m,mat,refs)
 else:s.add(name,m,mat,refs,collision=collision)
# Remove underground museum routes from outdoor ground collision sheets.
covered=[]
for p in sorted((ROOT/'reconstruction').glob('part0[1-8]-scene.json')):
 data=json.loads(p.read_text())
 for o in data['objects']:
  if o['collision'] and any(x in o['name'] for x in ['Floor','NAV_Court','NAV_Passage','NAV_Door','Ramp']) and 'Arrival' not in o['name']:
   vertices=np.array(o['vertices'])
   # Exterior ground stays below raised slabs; cut only real subterranean volumes.
   if vertices[:,2].min()>=G+.30:continue
   pts=vertices[:,:2]
   if len(pts)>2:
    a,t=local_enu_transform();pts=np.einsum('ij,nj->ni',a,pts)+t;g=Polygon(pts).convex_hull
    if g.area>.05:covered.append(g.buffer(.12))
covered=unary_union(covered)
river_features=[f for f in features if f['properties'].get('waterway') and f['properties'].get('tunnel')!='culvert'];riverline=unary_union([shape(f['geometry']).intersection(scope) for f in river_features]);riverpoly=riverline.buffer(2.1)
roads=[];roadinfo=[];rails=[];platforms=[];buildings=[]
for f in features:
 g=shape(f['geometry']).intersection(scope);t=f['properties'];id=f['id']
 if t.get('highway'):
  w={'primary':7.2,'secondary':6.8,'tertiary':6.4,'residential':4.8,'pedestrian':6.0}.get(t['highway'],5.5)
  r=(g if g.geom_type=='Polygon' else g.buffer(w/2,cap_style=2,join_style=2)).intersection(scope).difference(covered)
  roads.append(r);roadinfo.append((f,g,r,w))
 if t.get('railway')=='tram':rails.append((id,g))
 if t.get('railway')=='tram_stop' and g.geom_type=='Polygon':platforms.append((id,g))
 if 'building' in t and id not in meta['museum_building_way_ids']:buildings.append((f,g))
road_union=unary_union(roads);building_union=unary_union([g for f,g in buildings]);sidewalk=road_union.buffer(2.0,join_style=2).difference(road_union).intersection(scope).difference(covered).difference(building_union.buffer(.08));ground=scope.difference(covered).difference(riverpoly).difference(road_union).difference(sidewalk)
addpoly('Outdoor_Ground',ground,G-.03,'Ground','OSM scope, general ground level estimated')
for f,g,r,w in roadinfo:addpoly('Street_'+str(f['id']),r,G,'Street_Stone' if f['properties'].get('surface')=='paving_stones' or f['properties']['highway']=='pedestrian' else 'Asphalt','OSM way '+str(f['id']))
addpoly('Sidewalk_Floor',sidewalk,SIDE,'Sidewalk','OSM road centerlines; width/height estimated')
# Bevels provide a real curb and a continuous smooth collider at pavement transitions.
for pp in polygon_parts(sidewalk):
 for ring in [pp.exterior]+list(pp.interiors):
  pts=list(ring.coords)
  for a,b in zip(pts,pts[1:]):
   v=np.array(b)-a;length=np.linalg.norm(v)
   if length<.08:continue
   unit=v/length;norm=np.array([-unit[1],unit[0]])*.22
   aa=np.array(a);bb=np.array(b);mid=(aa+bb)/2
   # Select outward from the sidewalk polygon, then lower to road level.
   if pp.contains(Point(*(mid+norm))):norm=-norm
   m=Mesh().append([local(aa,SIDE),local(bb,SIDE),local(bb+norm,G),local(aa+norm,G)],[[0,1,2,3]])
   s.batch('Curb_Bevels',m,'Curb','estimated curb section',collision=True)
# A paved museum frontage follows the observed entrance street; no raster street billboards.
arrival=rect(-9,-29,9,-22);ar,t=local_enu_transform();arrival_enu=Polygon(np.einsum('ij,nj->ni',ar,np.asarray(arrival.exterior.coords))+t)
addpoly('Entrance_Frontage_Floor',arrival_enu.buffer(2.0).difference(covered),SIDE,'Street_Stone','Street View October 2024 / source entrance')
# Road markings appear only on the broader carriageways.
for f,g,r,w in roadinfo:
 if f['properties']['highway'] not in ['primary','secondary','tertiary']:continue
 for line in lineparts(g):
  for d in np.arange(2,line.length-2,7):
   a=line.interpolate(d);b=line.interpolate(min(line.length,d+3));strip=LineString([a,b]).buffer(.055,cap_style=2).intersection(r)
   for p in polygon_parts(strip):s.batch('Road_Lane_Dashes',polygon_plate(mapped_polygon(p),G+.008),'White','road markings estimated, OSM centerline')
# Canal bed, stone retaining walls, and the observed black metal wave railing.
addpoly('Sacir_Canal_Water',riverpoly.intersection(scope),G-1.2,'River','OSM Sacır Suyu; width and water level estimated',False)
for sign in [-1,1]:
 bank=riverline.offset_curve(sign*2.2) if riverline.geom_type=='LineString' else unary_union([g.offset_curve(sign*2.2) for g in lineparts(riverline)])
 cut=bank.difference(road_union.buffer(2.7)).intersection(scope)
 for li,line in enumerate(lineparts(cut)):
  ex('Canal_Retaining_%s_%s'%(sign,li),line.buffer(.20,cap_style=2),G-1.6,SIDE,'Canal_Stone','Street View October 2024, OSM canal',True)
  for z in [.20,.53,1.02]:lines('Canal_Railing',line,SIDE+z,.022,'Black','Street View October 2024',False)
  for d in np.arange(0,line.length,1.55):
   p=line.interpolate(d);s.batch('Canal_Posts',cylinder(local(p.coords[0],SIDE),local(p.coords[0],SIDE+1.08),.032,segments=10),'Black','Street View October 2024')
  # Hidden continuous barrier prevents walking into the canal through decorative rails.
  ex('NAV_Canal_Rail_%s_%s'%(sign,li),line.buffer(.04),SIDE,SIDE+1.05,'Black','safety collision rail',True);s.objects[-1]['hidden']=True
# Tram track slab, two rails per track at the official mapped 1435mm gauge.
for id,g in rails:
 for li,line in enumerate(lineparts(g)):
  bed=line.buffer(1.35,cap_style=2).intersection(scope).difference(covered);addpoly('Tram_Bed_'+str(id)+'_'+str(li),bed,RAIL-.025,'Rail_Bed','OSM railway '+str(id))
  for side in [-1,1]:lines('Tram_Rails',line.offset_curve(side*.7175),RAIL,.035,'Rail_Steel','OSM gauge=1435')
  for d in np.arange(1,line.length-1,.72):
   a=np.array(line.interpolate(d-.25).coords[0]);b=np.array(line.interpolate(d+.25).coords[0]);p=(a+b)/2;n=np.array([-(b-a)[1],(b-a)[0]]);n/=np.linalg.norm(n)
   s.batch('Track_Sleepers',cylinder(local(p-n*.98,RAIL-.075),local(p+n*.98,RAIL-.075),.055,segments=6),'Canal_Stone','rail support spacing estimated')
  # Contact wire and poles, spaced by reference type; exact pole chainage unmeasured.
  lines('Catenary_Contact_Wires',line,RAIL+5.5,.009,'Black','OSM electrified contact_line, station photos')
  lines('Catenary_Messenger_Wires',line,RAIL+6.2,.010,'Steel','station photos')
  for d in np.arange(7,line.length,27):
   a=np.array(line.interpolate(max(0,d-.5)).coords[0]);b=np.array(line.interpolate(min(line.length,d+.5)).coords[0]);v=b-a;v/=np.linalg.norm(v);n=np.array([-v[1],v[0]]);p=np.array(line.interpolate(d).coords[0]);base=p+n*2.0
   s.batch('Green_Catenary_Poles',cylinder(local(base,G),local(base,RAIL+6.6),.10,.07,segments=12),'Pole_Green','station photographs',collision=True)
   s.batch('Catenary_Cantilevers',cylinder(local(base,RAIL+6.0),local(p,RAIL+5.6),.025,segments=8),'Steel','station photographs')
   s.batch('Catenary_Hangers',cylinder(local(p,RAIL+5.5),local(p,RAIL+6.2),.009,segments=6),'Steel','station photographs')
from museum_landscape import station_median
landscape_report=station_median(s,rails,platforms,scope,road_union,local,RAIL)
# Station platforms follow their mapped polygons exactly in plan.
station_centers=[]
for idx,(id,poly) in enumerate(platforms):
 ex('Station_Platform_'+str(idx),poly,G-.04,PLAT,'Curb','OSM way '+str(id),True)
 coords=np.asarray(poly.exterior.coords)[:4];edges=[(np.linalg.norm(coords[(i+1)%4]-coords[i]),coords[i],coords[(i+1)%4]) for i in range(4)];_,a,b=max(edges,key=lambda x:x[0]);d=(b-a)/np.linalg.norm(b-a)
 if d[0]<0:d=-d
 n=np.array([-d[1],d[0]]);cen=np.array(poly.centroid.coords[0]);length=max(e[0] for e in edges);width=poly.area/length;station_centers.append((cen,d,n,length,width))
 # Track-facing edge is south on northern platform, north on southern platform.
 towards=1 if idx==0 else -1;yedge=towards*(width/2-.40)
 for k,x in enumerate(np.arange(-length/2+1,length/2-1,.60)):
  for y in np.arange(-width/2+.3,width/2-.1,.60):
   pp=cen+d*x+n*y;yaw=math.atan2(d[1],d[0]);placed('Station_Tile_%d_%d_%s'%(idx,k,round(y,2)),plane_xy(-.292,.292,-.292,.292,0),(*pp,PLAT+.003),yaw,'Paver_'+str((k+int(y*2))%5),'2024-04-04 station photograph',False)
  pp=cen+d*x+n*yedge;yaw=math.atan2(d[1],d[0]);m=box((0,0,.006),(.595,.34,.012));placed('Tactile_%d_%d'%(idx,k),m,(*pp,PLAT),yaw,'Tactile_Yellow','station photograph')
  for dx in [-.20,0,.20]:
   for dy in [-.10,.10]:s.batch('Station_Tactile_Dots',cylinder(local(pp+d*dx+n*dy,PLAT+.012),local(pp+d*dx+n*dy,PLAT+.021),.027,segments=8),'Tactile_Yellow','station photograph')
 # Sloped platform ends support natural walking onto/off the station.
 for endsign in [-1,1]:
  c=cen+d*endsign*(length/2);a=c-n*width/2;b=c+n*width/2;fwd=d*endsign*2.2
  m=Mesh().append([local(a,PLAT),local(b,PLAT),local(b+fwd,SIDE),local(a+fwd,SIDE)],[[0,1,2,3]])
  # Orient top faces consistently.
  v=np.array(m.vertices);normal=np.cross(v[1]-v[0],v[2]-v[0]);
  if normal[2]<0:m.faces=[list(reversed(m.faces[0]))]
  s.add('Station_End_Ramp_%d_%d'%(idx,endsign),m,'Sidewalk','estimated accessible platform end',collision=True)
 for k,x in enumerate(np.arange(-length/2+5,length/2-3,6.0)):
  p=cen+d*x-n*towards*(width/2-.45);yaw=math.atan2(d[1],d[0]);org=(*p,PLAT)
  # Local +Y points trackward by mirroring the canopy geometry where necessary.
  frame=Mesh();glass=Mesh();dep=2.8*towards
  for xx in [-1.6,1.6]:
   frame.append(*old.mesh_args(box((xx,0,1.35),(.15,.18,2.70),bevel=.035)))
   beam=box((0,0,0),(.13,abs(dep+.15),.12),bevel=.025);bv=np.asarray(beam.vertices);pitch=math.atan2(.24,dep+.15);by=bv[:,1].copy();bz=bv[:,2].copy();bv[:,1]=math.cos(pitch)*by-math.sin(pitch)*bz;bv[:,2]=math.sin(pitch)*by+math.cos(pitch)*bz;beam.vertices=(bv+np.array([xx,(dep-.15)/2,2.70])).tolist();frame.append(*old.mesh_args(beam))
  for yy in [0,dep]:frame.append(*old.mesh_args(cylinder((-1.72,yy,2.65 if yy==0 else 2.82),(1.72,yy,2.65 if yy==0 else 2.82),.10,segments=16)))
  glass.append([[-1.62,0,2.66],[1.62,0,2.66],[1.62,dep,2.81],[-1.62,dep,2.81]],[[0,1,2,3]])
  placed('Shelter_Frame_%d_%d'%(idx,k),frame,org,yaw,'Frame_Grey','YG01 2024-04-04 station',True)
  placed('Shelter_Glass_%d_%d'%(idx,k),glass,org,yaw,'Shelter_Glass','YG01 2024-04-04 station')
  # Back windscreen and bench slats.
  placed('Shelter_Windscreen_%d_%d'%(idx,k),panel(3.0,1.9).transformed((0,-.02,.30)),org,yaw,'Shelter_Glass','station photograph',True)
  bench=Mesh()
  for yy in np.linspace(.35,.78,5):bench.append(*old.mesh_args(box((0,yy*towards,.47),(1.65,.075,.055))))
  for xx in [-.60,.60]:bench.append(*old.mesh_args(box((xx,.55*towards,.23),(.055,.40,.46))))
  placed('Station_Bench_%d_%d'%(idx,k),bench,org,yaw,'REF_Wood','station photograph',True)
  # Fixed station name is verified; changing advertisements are not reproduced.
  board=box((0,0,2.15),(2.5,.07,.38));placed('Station_Name_Board_%d_%d'%(idx,k),board,org,yaw,'Black','station photograph')
  pt=local(p+n*(towards*.055),PLAT+2.07);s.text('Station_Name_%d_%d'%(idx,k),'15 TEMMUZ\nDEMOKRASİ MEYDANI',pt,.11,rotation=(math.pi/2,0,yaw+math.radians(130)+(math.pi if towards>0 else 0)),material='Lettering')
# PT8 train: published 29.118m x2.350m x3.260m envelope, eight door sets.
track=next(g for id,g in rails if id==197344364);point=Point(-258.9031692883173,-2.59848899972485);dist=track.project(point);cen=np.array(track.interpolate(dist).coords[0]);d=np.array(track.interpolate(dist+1).coords[0])-np.array(track.interpolate(dist-1).coords[0]);d/=np.linalg.norm(d)
if d[0]<0:d=-d
n=np.array([-d[1],d[0]]);yaw=math.atan2(d[1],d[0]);org=(*cen,RAIL);body_floor=.95;doorx=10.70
train_parts={m:Mesh() for m in ['White','Orange','Black','Tram_Glass','Front_Glass','Rail_Bellows','Tram_Interior','Seat','Steel','Rail_Steel','Display_Amber']}
def tb(m,c,sz,bevel=0):train_parts[m].append(*old.mesh_args(box(c,sz,bevel=bevel)))
# Three articulated bodies, hollow inside with real window/door openings.
sections=[(-14.559,-5.0),(-4.15,4.15),(5.0,14.559)]
doors=[-10.70,-3.0,3.0,10.70]
for i,(a,b) in enumerate(sections):
 a=max(a,-13.70);b=min(b,13.70)
 floor=rect(a,-1.13,b,1.13)
 if i==2:floor=floor.difference(rect(doorx-.65,-1.14,doorx+.65,-.40))
 for pp in polygon_parts(floor):train_parts['Tram_Interior'].append(*old.mesh_args(extrude_xy(pp,body_floor-.10,body_floor)))
 tb('White',((a+b)/2,0,3.12),(b-a,2.35,.28),.08)
 for side in [-1,1]:
  wall=rect(a,.48,b,2.98)
  for x in doors:
   if a<x<b:wall=wall.difference(rect(x-.64,.28 if side==-1 and x==doorx else body_floor-.03,x+.64,2.86))
  for xx in np.arange(a+.85,b-.5,1.56):
   if any(abs(xx-x)<1.0 for x in doors):continue
   opening=rect(xx-.58,1.52,xx+.58,2.72);wall=wall.difference(opening)
   gl=panel(1.16,1.2).transformed((xx,side*1.176,1.52));train_parts['Tram_Glass'].append(*old.mesh_args(gl))
   for zz in [1.49,2.33,2.75]:tb('Black',(xx,side*1.177,zz),(1.23,.035,.045))
   for xedge in [xx-.60,xx+.60]:tb('Black',(xedge,side*1.177,2.12),(.045,.035,1.24))
  # Extrude x/z profile across the side wall thickness.
  train_parts['White'].append(*old.mesh_args(extrude_xz(wall,.07).transformed((0,side*1.14,0))))
  for pp in polygon_parts(rect(a,.74,b,.89).intersection(wall)):
   train_parts['Orange'].append(*old.mesh_args(extrude_xz(pp,.075).transformed((0,side*1.14,0))))
  for x in doors:
   if not a<x<b:continue
   if side==-1 and x==doorx:
    # Door folded against the body leaves a 1.28m opening to the platform.
    tb('Black',(x-.66,-1.22,1.89),(.10,.32,1.92));tb('Black',(x+.66,-1.22,1.89),(.10,.32,1.92))
   else:
    for xx in [x-.32,x+.32]:
     tb('Orange',(xx,side*1.16,1.84),(.62,.07,1.80));tb('Tram_Glass',(xx,side*1.205,2.08),(.49,.018,1.15));tb('Black',(xx+.30,side*1.21,1.84),(.025,.02,1.80))
for x in [-4.575,4.575]:
 tb('Tram_Interior',(x,0,.875),(.85,2.25,.15))
 for xx in np.linspace(x-.40,x+.40,13):
  for yy in [-1.10,1.10]:tb('Rail_Bellows',(xx,yy,1.98),(.035,.12,2.05))
  tb('Rail_Bellows',(xx,0,3.0),(.035,2.30,.10))
# Curved wrap-around windscreen and rounded white/orange PT8 nose from official fleet photo.
nose_parts={m:Mesh() for m in ['Front_Glass','Black','White','Steel','Orange']}
for sign in [-1,1]:
 for mat,z0,z1,depth in [('Front_Glass',1.55,2.94,.82),('Black',.89,1.55,.82),('White',.70,.89,.82),('White',2.94,3.26,.76),('Steel',.37,.72,.86)]:
  m=Mesh();v=[];steps=96
  for z in [z0,z1]:
   for t in np.linspace(-math.pi/2,math.pi/2,steps+1):
    recess=max(0,z-1.28)*.22;x=sign*(13.70+depth*math.cos(t)-recess);y=1.15*math.sin(t);v.append([x,y,z])
  faces=[[i,i+1,i+steps+2,i+steps+1] for i in range(steps)]
  if sign<0:faces=[list(reversed(f)) for f in faces]
  m.append(v,faces);nose_parts[mat].append(*old.mesh_args(m))
 # The lower orange strip and glazing seals follow the rounded nose.
 # Flush painted orange belt, below both lamp units.
 v=[]
 for z in [.74,.89]:
  for t in np.linspace(-math.pi/2,math.pi/2,97):v.append([sign*(13.70+.824*math.cos(t)),1.154*math.sin(t),z])
 faces=[[i,i+1,i+98,i+97] for i in range(96)]
 if sign<0:faces=[list(reversed(f)) for f in faces]
 nose_parts['Orange'].append(v,faces)
 for z,mat,rad in [(1.55,'Black',.018),(2.95,'Black',.023)]:
  for a0,a1 in zip(np.linspace(-math.pi/2,math.pi/2,40),np.linspace(-math.pi/2,math.pi/2,40)[1:]):
   pa=(sign*(13.70+.83*math.cos(a0)-max(0,z-1.28)*.22),1.15*math.sin(a0),z);pb=(sign*(13.70+.83*math.cos(a1)-max(0,z-1.28)*.22),1.15*math.sin(a1),z);train_parts[mat].append(*old.mesh_args(cylinder(pa,pb,rad,segments=8)))
 for yy in [-.76,.76]:
  train_parts['Black'].append(*old.mesh_args(sphere((sign*14.28,yy,.99),(.045,.235,.115),24,12)))
  for shift,material in [(-.075,'White'),(.075,'Orange')]:train_parts[material].append(*old.mesh_args(sphere((sign*14.315,yy+shift,.99),(.026,.072,.074),20,12)))
 train_parts['Black'].append(*old.mesh_args(cylinder((sign*14.51,-.45,1.40),(sign*14.28,.12,2.36),.017,segments=8)))
 # Cab partition is built from the official interior references below.
for x in [-11.6,-4.55,4.55,11.6]:
 tb('Black',(x,0,.34),(1.9,1.70,.38))
 for xx in [x-.60,x+.60]:
  for side in [-1,1]:train_parts['Rail_Steel'].append(*old.mesh_args(cylinder((xx,side*.62,.34),(xx,side*.87,.34),.34,segments=24)))
from tram_interior import build_pt8_interior
interior_report=build_pt8_interior(s,local(cen,RAIL),yaw+math.radians(130),body_floor)
# Pantograph silhouette with articulated arms.
for x in [-6.5,6.5]:
 tb('Steel',(x,0,3.29),(1.5,1.4,.12))
 for yy in [-.40,.40]:
  for a,b in [((x-.60,yy,3.35),(x+.1,yy,4.45)),((x+.1,yy,4.45),(x-.65,yy,5.50))]:train_parts['Steel'].append(*old.mesh_args(cylinder(a,b,.025,segments=8)))
 train_parts['Black'].append(*old.mesh_args(cylinder((x-.65,-.68,5.50),(x-.65,.68,5.50),.026,segments=10)))
for mat,m in nose_parts.items():
 if not m.vertices:continue
 s.add('PT8_Smooth_Nose_'+mat,m.transformed(local(org[:2],org[2]),yaw+math.radians(130)),mat,'Gaziulas actual PT8 fleet photograph','Continuous smooth nose surface; photo-estimated profile',collision=True,smooth=True)
for mat,m in train_parts.items():placed('PT8_'+mat,m,org,yaw,mat,'Gaziulaş PT8 envelope + official fleet photograph; detail estimated',collision=mat in ['White','Orange','Black','Tram_Interior','Tram_Glass','Front_Glass'])
# Exact municipal wordmark on each cab nose, from the official open-data artwork.
from museum_identity import artwork
s.mat('Identity_Municipality_White',(.94,.94,.92),.55)
for sign in [-1,1]:
 logo,_=artwork('municipal-logo-tr.png','ink',.52);logo=logo.transformed((sign*14.43,0,1.27),sign*math.pi/2)
 v=np.asarray(logo.vertices)
 for q in v:q[0]=sign*(13.70+.83*math.sqrt(max(0,1-(q[1]/1.15)**2))-max(0,q[2]-1.28)*.22+.012)
 logo.vertices=v.tolist();placed('PT8_Official_Cab_Wordmark_'+str(sign),logo,org,yaw,'Identity_Municipality_White','Municipal original logo; location from Gaziulas fleet photograph')
# Three reconstructed boarding treads and a smooth navigation incline to the platform.
for k in range(3):
 yy=-.56-k*.40;zz=.95-(k+1)*.21;placed('Tram_Boarding_Step_'+str(k),box((doorx,yy,zz-.05),(1.22,.40,.10)),org,yaw,'Tram_Interior','PT8 boarding steps inferred')
ramp=Mesh().append([[doorx-.61,-.40,.95],[doorx+.61,-.40,.95],[doorx+.61,-1.80,.32],[doorx-.61,-1.80,.32]],[[3,2,1,0]])
placed('NAV_Tram_Boarding_Ramp',ramp,org,yaw,'Tram_Interior','navigation boarding incline',True);s.objects[-1]['hidden']=True
# Neighbor buildings retain source footprints. Elevations/openings are deliberately documented estimates.
for f,g in buildings:
 id=f['id'];p=f['properties'];area=g.area;levels=2 if area<130 else 3 if area<500 else 4;h=levels*3.05
 if p.get('building:levels'):levels=int(p['building:levels']);h=levels*3.05
 if p.get('height'):
  try:h=float(p['height'].split()[0])
  except:pass
 mat='Facade_'+str(id%7)
 ex('Building_OSM_'+str(id),g,G,h+G,mat,'OSM way '+str(id)+'; elevation estimated',True)
 addpoly('Building_Roof_'+str(id),g.buffer(.10),h+G+.03,'Roof_Tile' if area<300 else 'Facade_4','estimated roof form',False)
 for poly in polygon_parts(g):
  pts=list(poly.exterior.coords)
  for e,(a,b) in enumerate(zip(pts,pts[1:])):
   a,b=np.array(a),np.array(b);v=b-a;ln=np.linalg.norm(v)
   if ln<2.4:continue
   dv=v/ln;normal=np.array([dv[1],-dv[0]])*.025;mid=(a+b)/2
   if poly.contains(Point(*(mid+normal))):normal=-normal
   for x in np.arange(1.3,ln-.7,2.8):
    pt=a+dv*x+normal
    for lv in range(levels):
     z=G+1.30+lv*3.05;ww=.95 if area<180 else 1.25;hh=1.35
     u=local(pt-dv*ww/2,z);v0=local(pt+dv*ww/2,z);v1=local(pt+dv*ww/2,z+hh);u1=local(pt-dv*ww/2,z+hh)
     s.batch('Neighbor_Windows',Mesh().append([u,v0,v1,u1],[[0,1,2,3]]),'Window','OSM footprint, unsurveyed facade openings')
     lines('Neighbor_Window_Frames',LineString([pt-dv*ww/2,pt+dv*ww/2]),z-.03,.035,'White','estimated facade detail')
# Park areas and street trees observed in available imagery; exact individual tree positions estimated.
for f in features:
 if f['properties'].get('leisure')=='park' or f['properties'].get('landuse')=='grass':addpoly('Mapped_Green_'+str(f['id']),shape(f['geometry']).intersection(scope).difference(covered).difference(road_union.buffer(2)),G+.01,'Grass','OSM green area',False)
def tree(p,h=7):
 p=np.array(p);org=local(p,G);s.batch('Street_Tree_Trunks',cylinder(org,(*org[:2],G+h*.72),.18,.075,segments=10),'Tree_Bark','Street View and station photo; positions estimated',collision=True)
 for k in range(8):
  a=k*TAU/8;offset=np.array([math.cos(a)*1.55,math.sin(a)*1.55]);end=p+offset
  s.batch('Street_Tree_Branches',cylinder(local(p,G+h*.48),local(end,G+h*.78),.06,.025,segments=7),'Tree_Bark','photo-informed tree shape')
  s.batch('Street_Tree_Foliage',sphere(local(end,G+h*.76+(.5 if k%2 else 0)),(1.6,1.6,1.7),12,8),'Leaves_'+str(k%4),'photo-informed canopy',smooth=True)
for line in lineparts(riverline):
 for d0 in np.arange(5,line.length,9):
  p=np.array(line.interpolate(d0).coords[0]);a=np.array(line.interpolate(max(0,d0-.2)).coords[0]);b=np.array(line.interpolate(min(line.length,d0+.2)).coords[0]);dv=b-a;dv/=np.linalg.norm(dv);p+=np.array([-dv[1],dv[0]])*4.3
  if scope.contains(Point(*p)) and not road_union.buffer(1).contains(Point(*p)) and not building_union.buffer(2).contains(Point(*p)) and not covered.contains(Point(*p)):tree(p,float(rng.uniform(6,8.5)))
# Entry bollards and the canal-side furniture remain independent solids.
for x in np.arange(-8,9,2.4):
 p=np.array([x,-27.7]);s.batch('Entrance_Bollards',join(cylinder((*p,SIDE),(*p,SIDE+.60),.055,.04,12),sphere((*p,SIDE+.63),(.073,.073,.073),12,8)),'Black','Street View 2024',collision=True)
# Preserve a usable route across the mapped bridge/junction and through the entrance.
route=[(-247.5,-9.5),(-216,-18.8),(-204,-22.0),(-178,-29.5),(-152,-28),(-130,-24),(-108,-14),(-83,-1),(-61,9),(-48,10)]
route_author=[list(local(p)) for p in route]+[[0,-25],[0,-21],[0,-17.5]]
train_door=cen+d*doorx+n*(-.15);outside=cen+d*doorx+n*(-3.0)
s.views=[{'id':'tramstart','title':'بداية اللعبة داخل الترام','position':list(local(train_door,RAIL+body_floor+1.65)),'target':list(local(outside,PLAT+1.45)),'reference_image':'../../references/tram/gaziulas-tram-types.png'},
 {'id':'station','title':'محطة 15 Temmuz','position':list(local(cen+d*17+n*(-3.0),PLAT+1.65)),'target':list(local(cen,RAIL+1.9)),'reference_image':'../../references/tram/YG01-2024-04-04-IMG_2115.jpg'},
 {'id':'museumstreet','title':'الشارع أمام المتحف','position':list(local((-55,12),SIDE+1.65)),'target':[0,-18,2.2],'reference_image':'../../references/google-maps/recovered-maps-observation-13.png'},
 {'id':'southstreets','title':'الحارات جنوب المتحف','position':list(local((0,-85),SIDE+1.65)),'target':list(local((35,-83),SIDE+1.65))},
 {'id':'eaststreets','title':'الحارات شرق المتحف','position':list(local((90,-18),SIDE+1.65)),'target':list(local((85,-55),SIDE+1.65))},
 {'id':'surroundings','title':'المتحف ومحيط 100 متر','position':list(local((-155,-80),150)),'target':list(local((-25,-30),0)),'mode':'fly','reference_image':'../../references/geospatial/site-plan-reference.png'}]
s.views.extend([{'id':'traminterior','title':'داخل الترام — مقارنة بالصور الرسمية','position':list(local(cen+d*9.95+n*.22,RAIL+body_floor+1.65)),'target':list(local(cen-d*8+n*.22,RAIL+body_floor+1.50)),'reference_image':'../../references/fidelity-2026-10-26/tram-interior-gaziulas-7.jpg'},{'id':'tramjoint','title':'مفصل العربة والمقاعد','position':list(local(cen+d*3.75+n*.22,RAIL+body_floor+1.65)),'target':list(local(cen+d*7+n*.22,RAIL+body_floor+1.45)),'reference_image':'../../references/fidelity-2026-10-26/tram-interior-gaziulas-8.jpg'},{'id':'tramcab','title':'زجاج كابينة القيادة','position':list(local(cen+d*12.1+n*.22,RAIL+body_floor+1.65)),'target':list(local(cen+d*13.8,RAIL+1.5)),'reference_image':'../../references/fidelity-2026-10-26/tram-cab-gaziulas-5.jpg'}])
s.views.extend([{'id':'tramface','title':'واجهة الترام والشعار الأصلي','position':list(local(cen+d*18.7-n*3.0,RAIL+1.65)),'target':list(local(cen+d*14,RAIL+1.55)),'mode':'fly','reference_image':'../../references/tram/gaziulas-tram-types.png'},{'id':'stationground','title':'العشب والبلاط بين السكك عن قرب','position':list(local(cen+d*18+n*1.6,RAIL+.85)),'target':list(local(cen+d*11+n*1.6,RAIL+.05)),'mode':'fly','reference_image':'../../references/tram/YG01-2024-04-04-IMG_2115.jpg'}])
s.save(ROOT/'reconstruction/part00-scene.json')
report={'title':'الترام والشوارع المحيطة','source':'OpenStreetMap, station photographs dated 2024-04-04, Google Street View October 2024, Gaziulaş official fleet page','requested_minimum_buffer_m':100,'working_buffer_m':110,'coverage_contains_requested_buffer':scope.covers(museum.convex_hull.buffer(100)),'neighbor_buildings':len(buildings),'road_ways':len(roadinfo),'tram_platforms':len(platforms),'train_type':'Siemens-Düwag PT8','train_envelope_m':[29.118,2.350,3.260],'train_spec_source':'https://gaziulas.com.tr/hizmetler/tramvay-isletmesi/tramvay-filomuz','route_author_xy':route_author,'tram_door_author_xy':list(local(train_door)),'platform_exit_author_xy':list(local(outside)),'accuracy_100_percent':False,'limits':['OSM plan coordinates are mapped data, not a site survey','Street widths, levels, building heights, individual windows, tree/pole chainage and car details are estimated','Available Google Street View is October 2024, not current-day imagery','Livery uses official fleet reference; dynamic ads and exact vehicle at this stop today are not verified','Station platform end ramps and boarding geometry inferred for playable continuity'],'attribution':'© OpenStreetMap contributors, ODbL; YG01 station photographs CC BY 4.0'}
report['interior_reference_review']=interior_report
report['station_landscape_review']=landscape_report
report['tram_local_frame']={'origin_author':list(local(cen,RAIL)),'yaw_author_rad':yaw+math.radians(130),'floor_above_rail_m':body_floor}
(ROOT/'reconstruction/part00-notes.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
(ROOT/'references/geospatial/environment-coverage.geojson').write_text(json.dumps({'type':'FeatureCollection','features':[{'type':'Feature','properties':{'kind':'modeled_scope'},'geometry':mapping(scope)},{'type':'Feature','properties':{'kind':'requested_100m_scope'},'geometry':mapping(museum.convex_hull.buffer(100))}]}))
