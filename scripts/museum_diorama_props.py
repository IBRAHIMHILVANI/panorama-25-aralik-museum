"""Editable physical scenery shared by dioramas and panorama; photo-estimated sizes."""
from museum_geometry import *
from museum_architecture import extrude_xy,polygon_parts
from museum_exhibits import emit_reference_prop,photo_material
from shapely.geometry import Polygon,Point
import cv2

def scenic_materials(s):
 for name,col in old.materials.items():
  if not name.startswith('REF_Mural') and not name.endswith('_Photo'):s.mat(name,col,.87)
 for i in range(6):s.mat('Rubble_'+str(i),(.40+i*.045,.365+i*.040,.30+i*.035),.97)
 s.mat('Rope_Fibre',(.48,.36,.20),.98)

def curved_photo(s,name,n,c,r,a0,a1,z0,h,quad,segments=64):
 H=cv2.getPerspectiveTransform(np.float32([[0,0],[1,0],[1,1],[0,1]]),np.float32(quad));v=[];uv=[];f=[]
 for j in range(9):
  for i in range(segments+1):
   t=i/segments;a=math.radians(a0+(a1-a0)*t);v.append([c[0]+r*math.cos(a),c[1]+r*math.sin(a),z0+h*j/8]);q=H@np.array([1-t,1-j/8,1]);q/=q[2];uv.append([float(q[0]),float(1-q[1])])
 for j in range(8):
  for i in range(segments):k=j*(segments+1)+i;f.append([k+1,k,k+segments+1,k+segments+2])
 s.add(name,Mesh().append(v,f,[[uv[k] for k in ff] for ff in f]),photo_material(s,n),str(n),'original mural pixels projected on curved canvas; photographic overlap and perspective remain estimated')

def terrain(s,name,poly,z,seed=1,rough=.11):
 from shapely import constrained_delaunay_triangles
 from shapely.ops import unary_union
 from shapely.geometry import box as rect
 out=Mesh();x0,y0,x1,y1=poly.bounds
 for x in np.arange(x0,x1,.45):
  for y in np.arange(y0,y1,.45):
   for p in polygon_parts(poly.intersection(rect(x,y,x+.45,y+.45))):
    for t in constrained_delaunay_triangles(p).geoms:
     pts=list(t.exterior.coords)[:-1]
     if not t.exterior.is_ccw:pts.reverse()
     out.append([[xx,yy,z+rough*(.6+.3*math.sin(xx*2.7+yy*1.3+seed)+.2*math.cos(yy*4.1-xx))] for xx,yy in pts],[[0,1,2]])
 s.add(name,out,'REF_Earth',str(seed),'scenic ground surface; no surveyed elevation',smooth=True)

def rubble(s,name,origin,width,depth,count,seed,yaw=0,zmax=.5):
 rng=np.random.default_rng(seed)
 for i in range(count):
  x,y=rng.uniform(-width/2,width/2),rng.uniform(-depth/2,depth/2);sz=rng.uniform(.12,.40);z=rng.uniform(.05,zmax)*max(.2,1-abs(x)/(width*.7))
  m=box((x,y,z),(rng.uniform(.20,.65),rng.uniform(.17,.45),sz),rng.uniform(0,TAU),bevel=.03)
  vv=np.asarray(m.vertices);vv+=rng.uniform(-.028,.028,vv.shape);m.vertices=vv.tolist();s.batch(name+'_Broken_Masonry',m.transformed(origin,yaw),'Rubble_'+str(i%6),str(seed))
 for i in range(max(4,count//14)):
  x,y=rng.uniform(-width/2,width/2),rng.uniform(-depth/2,depth/2);m=box((x,y,rng.uniform(.12,zmax+.12)),(.12,rng.uniform(.65,2.5),.10),rng.uniform(0,TAU));s.batch(name+'_Splintered_Timber',m.transformed(origin,yaw),'REF_Wood',str(seed))

def wagon(s,name,origin,yaw=0,broken=False,refs='2196'):
 wood=Mesh();iron=Mesh()
 for x in [-.66,.66]:
  for y in [-.76,.76]:
   w,m=old.wheel((x,y,.52),.51,.12,spokes=12);wood.append(*old.mesh_args(w));iron.append(*old.mesh_args(m))
 for y in [-.76,.76]:iron.append(*old.mesh_args(cylinder((-.8,y,.52),(.8,y,.52),.045,segments=12)))
 for i in range(7):wood.append(*old.mesh_args(box((-.48+i*.16,0,.75),(.14,2.25,.08),(.04 if broken else 0)*(i%3-1))))
 for x in [-.59,.59]:
  for z in [.91,1.07,1.23]:wood.append(*old.mesh_args(box((x,0,z),(.07,2.15,.105))))
  for y in [-1.03,0,1.03]:wood.append(*old.mesh_args(box((x,y,1.01),(.09,.09,.64))))
  wood.append(*old.mesh_args(cylinder((x,-1,.65),(x,-3.2,.35),.055,segments=8)))
 if broken:
  vv=np.asarray(wood.vertices);vv[:,2]+=.12*np.sin(vv[:,0]*4+vv[:,1]*2);wood.vertices=vv.tolist()
 s.add(name+'_Wood',wood.transformed(origin,yaw),'REF_Wood_Light',refs)
 s.add(name+'_Iron',iron.transformed(origin,yaw),'REF_Iron',refs)

def loom(s,name,origin,yaw=0,refs='2193'):
 wood=Mesh();thread=Mesh()
 for x in [-.62,.62]:
  for y in [-.48,.48]:wood.append(*old.mesh_args(box((x,y,.72),(.09,.09,1.44))))
  for z in [.15,.88,1.38]:wood.append(*old.mesh_args(box((x,0,z),(.08,1.05,.08))))
 for y,z in [(-.46,.84),(.45,1.30),(.44,.18)]:wood.append(*old.mesh_args(cylinder((-.69,y,z),(.69,y,z),.055,segments=16)))
 for x in np.linspace(-.54,.54,45):thread.append(*old.mesh_args(cylinder((x,-.46,.84),(x,.45,1.30),.0025,segments=5)))
 for x in [-.28,.28]:wood.append(*old.mesh_args(box((x,-.16,.18),(.09,.68,.045))))
 s.add(name+'_Frame',wood.transformed(origin,yaw),'REF_Wood_Light',refs);s.add(name+'_Warp_Threads',thread.transformed(origin,yaw),'REF_Cloth_Cream',refs)

def stool(s,name,origin,yaw=0,refs='2193'):
 m=box((0,0,.46),(.50,.42,.07))
 for x in [-.20,.20]:
  for y in [-.16,.16]:m.append(*old.mesh_args(cylinder((x,y,0),(x*.8,y*.8,.46),.027,segments=8)))
 s.batch(name,m.transformed(origin,yaw),'REF_Wood_Light',refs)

def goat(s,name,origin,yaw=0,refs='2194'):
 body=join(sphere((0,0,.55),(.17,.36,.24),20,12),sphere((0,-.39,.72),(.10,.18,.13),20,10))
 for x in [-.12,.12]:
  for y in [-.24,.24]:body.append(*old.mesh_args(cylinder((x,y,.04),(x,y,.50),.035,.045,segments=8)))
 for x in [-.11,.11]:body.append(*old.mesh_args(sphere((x,-.39,.75),(.085,.035,.025),12,6)))
 s.add(name,body.transformed(origin,yaw),'REF_Cloth_Green',refs,smooth=True)
 horns=join(cylinder((-.055,-.37,.81),(-.07,-.25,.96),.018,.004,10),cylinder((.055,-.37,.81),(.07,-.25,.96),.018,.004,10))
 s.add(name+'_Horns',horns.transformed(origin,yaw),'REF_Wood_Light',refs)

def flag(s,name,origin,yaw=0,refs='2199',w=.75,h=1.12):
 from museum_identity import turkish_flag
 off=np.array([w/2,0,h]);c=math.cos(yaw);ss=math.sin(yaw)
 top=np.array(origin)+np.array([c*off[0],ss*off[0],off[2]])
 turkish_flag(s,name,top,w,h,yaw=yaw,vertical=True,fold=.035,refs=refs+'; source SVG flag proportions')
 s.add(name+'_Pole',cylinder((0,0,-.25),(0,0,h+.08),.018,segments=10).transformed(origin,yaw),'REF_Wood',refs)

def roof_tiles(s,name,origin,width,depth,yaw=0,refs='2225'):
 for row,y in enumerate(np.arange(-depth/2,depth/2,.32)):
  for x in np.arange(-width/2,width/2,.18):
   m=cylinder((x,y,.16*abs(y)),(x,y+.36,.16*abs(y+.36)),.092,.073,10,caps=False)
   s.batch(name,m.transformed(origin,yaw),'REF_Cloth_Ochre' if row%3 else 'REF_Rust',refs)
