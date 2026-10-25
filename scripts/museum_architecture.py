"""Geometry helpers for the remaining museum and mapped street environment."""
from museum_geometry import *
from shapely.geometry import Polygon,Point,box as rectangle
from shapely import constrained_delaunay_triangles

def polygon_parts(g):
    if g.is_empty:return []
    if g.geom_type=='Polygon':return [g]
    return [p for p in g.geoms if p.geom_type=='Polygon'] if hasattr(g,'geoms') else []

def extrude_xy(poly,z0,z1):
    out=Mesh()
    for p in polygon_parts(poly):
        out.append(*old.mesh_args(polygon_plate(p,z1)))
        out.append(*old.mesh_args(polygon_plate(p,z0,False)))
        for ring in [p.exterior]+list(p.interiors):
            pts=list(ring.coords)
            for a,b in zip(pts,pts[1:]):out.append([[*a,z0],[*b,z0],[*b,z1],[*a,z1]],[[0,1,2,3]])
    return out

def extrude_xz(poly,depth):
    # x/z polygon; front is local -Y, consistent with photo panel orientation.
    m=extrude_xy(poly,-depth/2,depth/2);v=np.asarray(m.vertices)
    v[:,[1,2]]=v[:,[2,1]];m.vertices=v.tolist();m.faces=[list(reversed(f)) for f in m.faces];m.uv=[list(reversed(u)) for u in m.uv]
    return m

def pointed_arch(width,spring,rise,bottom=0,segments=48):
    a=width/2;c=(rise*rise-a*a)/(2*a);radius=a+c
    xs=np.linspace(-a,a,segments+1);top=[]
    for x in xs:
        centre=c if x<=0 else -c
        z=spring+rise*(max(0,1-abs(x)/a)**.35) if rise<a else spring+math.sqrt(max(0,radius*radius-(x-centre)**2))
        top.append((float(x),z))
    return Polygon([(-a,bottom),(a,bottom)]+list(reversed(top)))

def masonry_portal(scene,name,length,zbase,height,depth,origin,yaw,opening=None,refs='',block_w=.53,block_h=.33):
    wall=rectangle(-length/2,zbase,length/2,zbase+height)
    if opening is not None:wall=wall.difference(opening)
    collision=extrude_xz(wall,depth)
    scene.add('NAV_'+name,collision.transformed(origin,yaw),'Stone_Base',refs,collision=True,hidden=True)
    scene.add(name+'_Mortar_Backing',extrude_xz(wall,depth-.025).transformed(origin,yaw),'Stone_Base',refs,'continuous mortar backing closes block joints while retaining the real doorway opening')
    # Block joints are geometry, clipped around the actual open doorway.
    row=0;z=zbase
    while z<zbase+height-1e-6:
        x=-length/2-block_w*(row%2)/2;col=0
        while x<length/2:
            cell=rectangle(x+.003,z+.003,min(x+block_w-.003,length/2),min(z+block_h-.003,zbase+height)).intersection(wall)
            if not cell.is_empty and cell.area>1e-6:
                m=extrude_xz(cell,depth-.005);scene.batch(name,m.transformed(origin,yaw),'Stone_'+str((row*3+col)%6),refs)
            x+=block_w;col+=1
        z+=block_h;row+=1
    return wall

def rough_surface(width,height,origin,yaw=0,plane='wall',seed=1,amplitude=.035,step=.18):
    nx=max(2,int(width/step));nz=max(2,int(height/step));verts=[];faces=[]
    for j in range(nz+1):
        z=j*height/nz
        for i in range(nx+1):
            x=-width/2+i*width/nx
            noise=amplitude*(math.sin(x*5.3+z*4.1+seed)*.5+math.sin(x*13.7-z*8.9+seed*1.7)*.28+math.cos(x*27+z*20)*.14)
            verts.append([x,-noise,z])
    for j in range(nz):
        for i in range(nx):a=j*(nx+1)+i;faces.append([a,a+1,a+nx+2,a+nx+1])
    if plane=='ceiling':
        verts=[[x,z,-y] for x,y,z in verts];faces=[list(reversed(f)) for f in faces]
    return Mesh().append(verts,faces).transformed(origin,yaw)

def quad_ramp(x0,x1,y0,y1,z0,z1):
    return Mesh().append([[x0,y0,z0],[x1,y0,z0],[x1,y1,z1],[x0,y1,z1]],[[0,1,2,3]])

def source_surface_xy(width,depth,quad,origin,yaw=0):
    from museum_exhibits import projected_panel
    m=projected_panel(width,depth,quad);v=np.asarray(m.vertices);v[:,1]=v[:,2];v[:,2]=0;m.vertices=v.tolist()
    return m.transformed(origin,yaw)

def local_enu_transform():
    data=json.loads((ROOT/'references/geospatial/georeference.json').read_text())['authoring_to_geographic'];a=math.radians(data['rotation_deg']);r=np.array([[math.cos(a),-math.sin(a)],[math.sin(a),math.cos(a)]]);t=np.array(data['translation_east_north_m'])
    return r,t

def enu_to_author(p):
    r,t=local_enu_transform();p=np.asarray(p);v=r.T@(p[:2]-t)
    return (*v,p[2]) if len(p)>2 else tuple(v)

def mapped_polygon(poly):
    from shapely.ops import transform
    r,t=local_enu_transform()
    def f(x,y,z=None):
        xy=np.array([x,y]);shape=xy.shape;v=np.einsum('ij,jn->in',r.T,(xy.reshape(2,-1)-t[:,None]));v=v.reshape(shape)
        return (v[0],v[1]) if z is None else(v[0],v[1],z)
    return transform(f,poly)
