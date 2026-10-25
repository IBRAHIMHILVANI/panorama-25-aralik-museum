"""Shared metre/Z-up geometry for the staged museum reconstruction."""
from pathlib import Path
import json, math, copy
import numpy as np
import build_model as old

ROOT=Path(__file__).resolve().parents[1]
TAU=2*math.pi
Mesh=old.Mesh
box=old.box
cylinder=old.cylinder
sphere=old.sphere
torus=old.torus
join=old.join

class Scene:
    def __init__(self,part):
        self.part=part;self.objects=[];self.materials={};self.texts=[];self.groups={};self.views=[];self.lights=[];self.assets=[]
    def mat(self,name,color,roughness=.7,metallic=0,alpha=1,emission=0,image=None):
        self.materials[name]={'color':list(color),'roughness':roughness,'metallic':metallic,'alpha':alpha,'emission':emission,'image':image}
        return name
    def add(self,name,mesh,material,refs='',basis='photo-derived form; unmeasured dimensions',collision=False,hidden=False,smooth=False):
        if not mesh.vertices:return
        self.objects.append({'name':name,'vertices':mesh.vertices,'faces':mesh.faces,'uv':mesh.uv,'material':material,'source_photos':str(refs),'basis':basis,'collision':collision,'hidden':hidden,'smooth':smooth,'part':self.part})
    def batch(self,name,mesh,material,refs='',smooth=False,collision=False):
        key=(name,material,refs,smooth,collision)
        if key not in self.groups:self.groups[key]=Mesh()
        self.groups[key].append(mesh.vertices,mesh.faces,mesh.uv)
    def flush(self):
        used={o['name'] for o in self.objects}
        for (name,mat,refs,smooth,collision),mesh in self.groups.items():
            stem=name+'__'+mat;unique=stem;i=2
            while unique in used:unique=stem+'_'+str(i);i+=1
            used.add(unique);self.add(unique,mesh,mat,refs,smooth=smooth,collision=collision)
        self.groups={}
    def text(self,name,body,location,size,rotation=(math.pi/2,0,0),material='Lettering',align='CENTER'):
        self.texts.append({'name':name,'text':body,'location':location,'size':size,'rotation':rotation,'material':material,'align':align})
    def asset(self,name,path,position,yaw,height,refs='',basis='AI reconstructed full 3D asset; occluded surfaces estimated'):
        self.assets.append({'name':name,'path':str(path),'position':list(position),'yaw':float(yaw),'height':float(height),'source_photos':str(refs),'basis':basis})
    def save(self,path):
        self.flush()
        assert len({o['name'] for o in self.objects})==len(self.objects),'Duplicate object name'
        for o in self.objects:
            assert np.isfinite(o['vertices']).all(),o['name']
            assert all(len(f)>=3 and min(f)>=0 and max(f)<len(o['vertices']) for f in o['faces']),o['name']
        data={'units':'metres','up':'Z','part':self.part,'materials':self.materials,'objects':self.objects,'texts':self.texts,'views':self.views,'lights':self.lights,'assets':self.assets}
        Path(path).write_text(json.dumps(data,separators=(',',':'),ensure_ascii=False,default=lambda v:v.item() if isinstance(v,np.generic) else v.tolist()))
        print(json.dumps({'file':str(path),'objects':len(self.objects),'vertices':sum(len(o['vertices']) for o in self.objects),'faces':sum(len(o['faces']) for o in self.objects)},indent=2),flush=True)

def plane_xy(x0,x1,y0,y1,z):
    return Mesh().append([[x0,y0,z],[x1,y0,z],[x1,y1,z],[x0,y1,z]],[[0,1,2,3]],[[[0,0],[1,0],[1,1],[0,1]]])

def panel(width,height,crop=(0,0,1,1)):
    u0,y0,u1,y1=crop
    return Mesh().append([[-width/2,0,0],[width/2,0,0],[width/2,0,height],[-width/2,0,height]],[[0,1,2,3]],[[[u0,1-y1],[u1,1-y1],[u1,1-y0],[u0,1-y0]]])

def arc_band(center,ri,ro,a0,a1,z0,z1,segments=60):
    vs=[]
    for z in (z0,z1):
        for r in (ri,ro):
            for a in np.linspace(a0,a1,segments+1):vs.append([center[0]+r*math.cos(a),center[1]+r*math.sin(a),z])
    n=segments+1;fs=[]
    for i in range(segments):
        fs.extend([[i+1,i,2*n+i,2*n+i+1],[n+i,n+i+1,3*n+i+1,3*n+i],[2*n+i,3*n+i,3*n+i+1,2*n+i+1],[i+1,n+i+1,n+i,i]])
    fs.extend([[0,n,3*n,2*n],[segments+2*n,segments+3*n,segments+n,segments]])
    return Mesh().append(vs,fs)

def arc_line(center,r,a0,a1,z,radius=.025,segments=80):
    out=Mesh();pts=[[center[0]+r*math.cos(a),center[1]+r*math.sin(a),z] for a in np.linspace(a0,a1,segments+1)]
    for a,b in zip(pts,pts[1:]):
        m=cylinder(a,b,radius,segments=8);out.append(m.vertices,m.faces)
    return out

def sphere_leaf(center,size,rotation):
    # Each leaf has a central ridge; leaves are batched, not separate draw calls.
    x,y,z=center;rx,ry=size;c=math.cos(rotation);s=math.sin(rotation)
    p=[[-rx,0,0],[0,-ry,0],[rx,0,0],[0,ry,0],[0,0,ry*.22]]
    p=[[x+c*a-s*b,y+s*a+c*b,z+h] for a,b,h in p]
    return Mesh().append(p,[[0,1,4],[1,2,4],[2,3,4],[3,0,4]])

def polygon_plate(poly,z,up=True):
    from shapely import constrained_delaunay_triangles,set_precision,make_valid
    poly=set_precision(make_valid(poly).buffer(0),1e-6)
    m=Mesh();ts=list(constrained_delaunay_triangles(poly).geoms)
    assert abs(sum(t.area for t in ts)-poly.area)<1e-5
    for t in ts:
        ps=list(t.exterior.coords)[:-1]
        if not t.exterior.is_ccw:ps.reverse()
        if not up:ps.reverse()
        m.append([[x,y,z] for x,y in ps],[[0,1,2]])
    return m
