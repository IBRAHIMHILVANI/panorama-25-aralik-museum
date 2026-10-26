"""Close-range vegetation and rail paving based on the dated site references.

Individual leaf positions are procedural. Plant envelopes/placement remain
photo-estimated, never a claim of a current measured landscape survey.
"""
from museum_geometry import *
from museum_architecture import polygon_parts,mapped_polygon
from shapely.geometry import Point,Polygon,box as rect
from shapely.ops import nearest_points
from shapely.affinity import affine_transform
import hashlib,shutil

# Pixel positions in the unchanged 1368x1824 source. This clean turf region
# excludes rails, pavers, litter and canopy shadows. No source pixels are edited.
TURF_QUAD_PX=np.array([(250,1330),(560,1228),(560,1275),(250,1375)],dtype=float)

def interlocking_paver(joint=.003):
 """Exact staggered lattice: pitch .24 x .17, odd rows shifted .12.

 The notch half-width must be one quarter of the longitudinal pitch (.06).
 Eroding the tessellating outline produces a narrow joint, not an open hole.
 """
 return Polygon([(-.12,-.105),(-.06,-.105),(-.06,-.065),(.06,-.065),(.06,-.105),(.12,-.105),(.12,.105),(.06,.105),(.06,.065),(-.06,.065),(-.06,.105),(-.12,.105)]).buffer(-joint/2,join_style=2)

def original_turf_material(s):
 source=ROOT/'references/tram/YG01-2024-04-04-IMG_2115.jpg'
 name='Station_Grass_Original_2024_04_04.jpg'
 digest=hashlib.sha256(source.read_bytes()).hexdigest()
 for folder in [ROOT/'output/Gaziantep-Museum-2026-10-25/textures',ROOT/'review/walkthrough/textures']:
  folder.mkdir(parents=True,exist_ok=True);destination=folder/name
  if not destination.exists() or hashlib.sha256(destination.read_bytes()).hexdigest()!=digest:shutil.copyfile(source,destination)
 s.mat('Station_Turf_Original_Photo',(1,1,1),.99,image='textures/'+name)
 return {'source':str(source.relative_to(ROOT)),'source_date':'2024-04-04','sha256':digest,'source_pixels_unchanged':True,'uv_quad_source_pixels':TURF_QUAD_PX.tolist(),'source_dimensions_px':[1368,1824],'texture_mapping':'bounded clean-turf region tiled with alternating UV reflection; no source image edits','metric_texture_scale':'estimated; not a surveyed ground orthophoto'}

def leafy_shrub(s,name,origin,width,depth,height,seed=1,conical=False,refs='Google Street View October 2024 entrance'):
 rng=np.random.default_rng(seed);ox,oy,oz=origin
 for i,c in enumerate([(.16,.25,.085),(.24,.34,.12),(.31,.39,.16),(.36,.43,.20)]):s.mat('Plant_Leaf_'+str(i),c,.94)
 s.mat('Plant_Bark',(.28,.23,.15),.98)
 s.batch(name+'_Branches',cylinder(origin,(ox,oy,oz+height*.85),width*.035,width*.009,8),'Plant_Bark',refs)
 for j in range(1300 if conical else 900):
  t=rng.uniform(.10,1);rad=(1-t)**.55 if conical else math.sqrt(max(.02,1-(2*t-1)**2))
  a=rng.uniform(0,TAU);r=rad*math.sqrt(rng.uniform(.35,1));p=(ox+math.cos(a)*width*.5*r,oy+math.sin(a)*depth*.5*r,oz+t*height)
  leaf=sphere_leaf((0,0,0),(.045 if conical else .055,.016 if conical else .027),rng.uniform(0,TAU));v=np.asarray(leaf.vertices)
  tilt=rng.uniform(-1.2,1.2);v[:,[1,2]]=np.einsum('ij,nj->ni',np.array([[math.cos(tilt),-math.sin(tilt)],[math.sin(tilt),math.cos(tilt)]]),v[:,[1,2]])
  leaf.vertices=(v+np.array(p)).tolist();s.batch(name+'_Leaves',leaf,'Plant_Leaf_'+str(int(rng.integers(4))),refs,smooth=True)

def station_median(s,rails,platforms,scope,roads,local,rail_z):
 """Grass lies BETWEEN the paved track beds, as visible in YG01 station photographs."""
 lines=[g for _,g in rails if g.geom_type=='LineString'];assert len(lines)==2
 a,b=lines;zone=Point(-258.9,-2.6).buffer(115);near=a.intersection(zone)
 if near.geom_type!='LineString':near=max(near.geoms,key=lambda g:g.length)
 sides=[[],[]]
 for d in np.arange(0,near.length,.75):
  p=np.array(near.interpolate(d).coords[0]);q=np.array(nearest_points(Point(*p),b)[1].coords[0]);v=q-p;dist=np.linalg.norm(v)
  if dist<1.8 or dist>6:continue
  unit=v/dist;sides[0].append(p+unit*.88);sides[1].append(q-unit*.88)
 grass=Polygon(sides[0]+sides[1][::-1]).buffer(0).intersection(scope).difference(roads.buffer(.12))
 reference='YG01 15 Temmuz station photographs, 2024-04-04: grass median and red/grey brick track infill'
 for i,c in enumerate([(.27,.35,.12),(.31,.39,.14),(.38,.43,.18),(.42,.45,.22)]):s.mat('Median_Grass_'+str(i),c,.98)
 for i,c in enumerate([(.49,.33,.27),(.55,.39,.31),(.60,.46,.38),(.47,.44,.39),(.63,.57,.48)]):s.mat('Track_Paver_'+str(i),c,.96)
 texture_evidence=original_turf_material(s)
 # Small clipped patches keep all UVs within the photographed turf region.
 # Texture reflection varies repetition without modifying a single source pixel.
 for pi,pp in enumerate(polygon_parts(grass)):
  x0,y0,x1,y1=pp.bounds
  for ix,x in enumerate(np.arange(x0,x1,1.20)):
   for iy,y in enumerate(np.arange(y0,y1,.35)):
    cell=pp.intersection(rect(x,y,x+1.20,y+.35))
    for patch in polygon_parts(cell):
     if patch.area<1e-6:continue
     m=polygon_plate(patch,rail_z+.012)
     for fi,face in enumerate(m.faces):
      uv=[]
      for vi in face:
       px,py,_=m.vertices[vi];u=np.clip((px-x)/1.20,0,1);v=np.clip((py-y)/.35,0,1)
       if ix%2:u=1-u
       if iy%2:v=1-v
       q=(1-v)*((1-u)*TURF_QUAD_PX[0]+u*TURF_QUAD_PX[1])+v*((1-u)*TURF_QUAD_PX[3]+u*TURF_QUAD_PX[2])
       uv.append([q[0]/1368,1-q[1]/1824])
      m.uv[fi]=uv
     m.vertices=[local(p[:2],p[2]) for p in m.vertices]
     s.batch('Station_Grass_Median_Original_Pixels',m,'Station_Turf_Original_Photo',reference)
 rng=np.random.default_rng(2115)
 for pp in polygon_parts(grass):
  x0,y0,x1,y1=pp.bounds
  for x in np.arange(x0,x1,.16):
   for y in np.arange(y0,y1,.16):
    if not pp.contains(Point(x,y)):continue
    density=.48+.18*math.sin(x*.47)*math.cos(y*.71)
    if rng.random()>density:continue
    for j in range(int(rng.integers(2,5))):
     px=x+rng.uniform(-.07,.07);py=y+rng.uniform(-.07,.07)
     if not pp.contains(Point(px,py)):continue
     ang=rng.uniform(0,TAU);w=rng.uniform(.001,.002);h=rng.uniform(.008,.026);lean=rng.uniform(.003,.012)
     v=[local((px-math.cos(ang)*w,py-math.sin(ang)*w),rail_z+.013),local((px+math.cos(ang)*w,py+math.sin(ang)*w),rail_z+.013),local((px+math.cos(ang)*lean,py+math.sin(ang)*lean),rail_z+.013+h)]
     s.batch('Station_Grass_Blades',Mesh().append(v,[[0,1,2]]),'Median_Grass_'+str(int(rng.integers(4))),reference)
 s.mat('Station_Paver_Joint',(.48,.44,.36),.99)
 paver=interlocking_paver()
 for li,line in enumerate(lines):
  seg=line.intersection(zone)
  for ll in ([seg] if seg.geom_type=='LineString' else list(seg.geoms)):
   if ll.geom_type!='LineString':continue
   bed=ll.buffer(1.35,cap_style=2).intersection(scope).difference(grass).difference(roads)
   for pi,pp in enumerate(polygon_parts(bed)):
    s.add('Station_Paver_Grout_%s_%s'%(li,pi),polygon_plate(mapped_polygon(pp),rail_z-.012),'Station_Paver_Joint',reference,'Continuous neutral joint bed below tessellating tiles; not a collider')
   for k,d in enumerate(np.arange(.2,ll.length-.2,.24)):
    p=np.array(ll.interpolate(d).coords[0]);t=np.array(ll.interpolate(d+.09).coords[0])-np.array(ll.interpolate(d-.09).coords[0]);t/=np.linalg.norm(t);n=np.array([-t[1],t[0]])
    for row,yy in enumerate(np.arange(-1.23,1.25,.17)):
     c=p+n*yy+t*(.12 if row%2 else 0)
     if grass.buffer(.025).contains(Point(*c)) or roads.contains(Point(*c)):continue
     tile=affine_transform(paver,[t[0],n[0],t[1],n[1],c[0],c[1]]).intersection(bed)
     for pp in polygon_parts(tile):
      if pp.area<1e-7:continue
      s.batch('Station_Track_Bricks',polygon_plate(mapped_polygon(pp),rail_z-.008),'Track_Paver_'+str(int(rng.integers(5))),reference)
 evidence={'reference':reference,'grass_area_m2':grass.area,'individual_blade_positions':'procedural; no surveyed placement','blade_height_above_surface_m':[.008,.026],'blade_full_width_m':[.002,.004],'track_bed':'red-grey interlocking brick infill on continuous neutral grout; 2024 photographed condition','paver_lattice_m':[.24,.17],'paver_row_shift_m':.12,'joint_width_m':.003,'turf_texture':texture_evidence}
 (ROOT/'review/qa/station-surface-followup-source.json').write_text(json.dumps(evidence,indent=2))
 return evidence
