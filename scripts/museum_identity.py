"""Actual institutional artwork traced into geometry; reference flag proportions.

Source PNG artwork is preserved untouched. Masks create editable vector silhouettes,
including glyph counters. No substitute typeface or generated logo is used.
"""
from museum_geometry import *
from museum_architecture import extrude_xz,polygon_parts
from PIL import Image
from shapely.geometry import Polygon,Point
from functools import lru_cache
import cv2

IDENTITY=ROOT/'references/identity-2026-10-26'
@lru_cache(maxsize=8)
def artwork(name,layer,width):
 a=np.asarray(Image.open(IDENTITY/name).convert('RGBA'))
 visible=a[:,:,3]>96
 if name.startswith('municipal'):visible &= np.max(a[:,:,:3],axis=2)<130
 ys,xs=np.where(visible);bbox=(xs.min(),ys.min(),xs.max(),ys.max())
 if layer=='red':mask=visible&(a[:,:,0]>130)&(a[:,:,1]<130)
 elif layer=='white':mask=visible&(np.min(a[:,:,:3],axis=2)>170)
 else:mask=visible
 contours,hierarchy=cv2.findContours(mask.astype('uint8'),cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
 hierarchy=hierarchy[0];scale=width/(bbox[2]-bbox[0]);out=Mesh()
 def ring(c):
  pts=c[:,0,:].astype(float)
  return [((x-(bbox[0]+bbox[2])/2)*scale,(bbox[3]-y)*scale) for x,y in pts]
 for i,c in enumerate(contours):
  depth=0;parent=hierarchy[i][3]
  while parent!=-1:depth+=1;parent=hierarchy[parent][3]
  if depth%2 or cv2.contourArea(c)<2:continue
  holes=[];child=hierarchy[i][2]
  while child!=-1:
   if len(contours[child])>=3:holes.append(ring(contours[child]))
   child=hierarchy[child][0]
  if len(c)<3:continue
  shape=Polygon(ring(c),holes).buffer(0).simplify(scale*.35,preserve_topology=True)
  for poly in polygon_parts(shape):
   if poly.area>scale*scale:out.append(*old.mesh_args(extrude_xz(poly,.003)))
 return out,(bbox[3]-bbox[1])*scale

def municipality_logo(s,name,origin,width,yaw=0,white=True):
 material=s.mat('Identity_Municipality_White' if white else 'Identity_Municipality_Black',(.94,.94,.92) if white else (.025,.025,.025),.55)
 mesh,height=artwork('municipal-logo-tr.png','ink',width)
 s.add(name,mesh.transformed(origin,yaw),material,'Gaziantep municipal open-data original TR logo; PNG contours','Exact artwork silhouette; physical placement/size interpreted from source photographs')
 return height

def panorama_logo(s,name,origin,width,yaw=0):
 for layer,color in [('red',(.8157,.0353,.1333)),('white',(.94,.94,.92))]:
  mesh,height=artwork('panorama-logo.png',layer,width)
  material=s.mat('Identity_Panorama_'+layer,color,.60)
  s.add(name+'_'+layer,mesh.transformed(origin,yaw),material,'Published museum-branded logo PNG; visually matched to museum signage','Original artwork silhouettes; source site affiliation unconfirmed; placement/size photo-estimated')

@lru_cache(maxsize=1)
def flag_emblem():
 crescent=Point(300,300).buffer(150,quad_segs=64).difference(Point(337.5,300).buffer(120,quad_segs=64))
 inner=75*(3-math.sqrt(5))/2
 star=Polygon([(492.5+(75 if i%2==0 else inner)*math.cos(math.pi+i*math.pi/5),300+(75 if i%2==0 else inner)*math.sin(math.pi+i*math.pi/5)) for i in range(10)])
 return crescent.union(star)

def turkish_flag(s,name,origin,width=.60,height=.90,yaw=0,phase=0,vertical=True,fold=.065,refs='IMG_1935; Flag_of_Turkey.svg source geometry'):
 red=s.mat('Identity_Flag_Red',(227/255,10/255,23/255),.94)
 white=s.mat('Identity_Flag_White',(1,1,1),.94)
 def pos(u,v,offset=0):return [(u-.5)*width,fold*math.sin(u*8+phase)*v+offset,-v*height]
 nx=18;ny=26;vs=[pos(i/nx,j/ny) for j in range(ny+1) for i in range(nx+1)];fs=[]
 for j in range(ny):
  for i in range(nx):k=j*(nx+1)+i;fs.append([k,k+1,k+nx+2,k+nx+1])
 s.batch(name+'_Cloth',Mesh().append(vs,fs).transformed(origin,yaw),red,refs,smooth=True)
 for poly in polygon_parts(flag_emblem()):
  source=polygon_plate(poly,0)
  for offset in [-.0025,.0025]:
   m=Mesh().append([pos(1-y/600,x/900,offset) if vertical else pos(x/900,y/600,offset) for x,y,_ in source.vertices],source.faces)
   s.batch(name+'_Emblem',m.transformed(origin,yaw),white,refs,smooth=True)
