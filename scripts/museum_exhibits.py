"""Reference-based museum display geometry shared by later review parts."""
from museum_geometry import *
import math
import numpy as np

def photo_material(scene,n):
    name=f'Photo_IMG_{n}'
    if name not in scene.materials:scene.mat(name,(1,1,1),.8,emission=.12,image=f'textures/IMG_{n}.jpg')
    return name

def emit_reference_prop(scene,fn,args,origin,yaw,refs,prefix,scale=1,omit=(),overrides=None):
    old.new=[];fn(*args);items=list(old.new);old.new=[]
    for item in items:
        if any(item['name'].endswith(x) for x in omit):continue
        mat=(overrides or {}).get(item['material'],item['material'])
        if mat not in scene.materials:scene.mat(mat,old.materials.get(item['material'],(.4,.4,.4)),.82)
        mesh=item['mesh'];mesh.vertices=(np.asarray(mesh.vertices)*scale).tolist();mesh=mesh.transformed(origin,yaw)
        scene.add(prefix+'_'+item['name'],mesh,mat,refs,'simplified editable exhibit geometry from source photos; dimensions estimated',smooth=any(t in item['name'] for t in ['Skin','Tunic','Trousers','Head','Body']))

def rifle_mesh():
    # Decorative silhouette only, with no functional mechanism or internal model.
    wood=Mesh();metal=Mesh()
    profile=[[-.66,-.075],[-.38,-.06],[-.23,.015],[.24,.018],[.34,.055],[.25,.09],[-.24,.08],[-.43,.15],[-.67,.13]]
    n=len(profile);v=[[x,y,z] for y in [-.025,.025] for x,z in profile]
    f=[list(range(n-1,-1,-1)),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)]
    wood.append(v,f)
    metal.append(*old.mesh_args(cylinder((-.10,0,.06),(.71,0,.06),.012,segments=10)))
    metal.append(*old.mesh_args(box((-.12,0,.065),(.27,.055,.045))))
    metal.append(*old.mesh_args(torus((-.24,0,-.012),.033,.007,(0,1,0),16,6)))
    metal.append(*old.mesh_args(cylinder((-.07,.018,.07),(-.07,.07,.10),.007,segments=8)))
    return wood,metal

def rifle(scene,name,origin,yaw=0,tilt=0,refs='2059-2067',base_z=None):
    wood,metal=rifle_mesh()
    meshes=[wood,metal]
    for mesh in meshes:
        vv=np.array(mesh.vertices);c=math.cos(tilt);sn=math.sin(tilt);vv[:,[0,2]]=vv[:,[0,2]]@np.array([[c,sn],[-sn,c]]);mesh.vertices=vv.tolist()
    dz=0 if base_z is None else base_z-origin[2]-min(v[2] for mesh in meshes for v in mesh.vertices)
    for mesh,mat,tag in [(wood,'Exhibit_Wood','Stock'),(metal,'Exhibit_Iron','Metal')]:
        vv=np.array(mesh.vertices);vv[:,2]+=dz;mesh.vertices=vv.tolist();scene.batch(name+'_'+tag,mesh.transformed(origin,yaw),mat,refs)

def mannequin(scene,name,origin,yaw,color,hat='kepi',refs='',female=False,child=False,skirt=False,pants_color=None,boots=True,traditional=False,headless=False,trim_color=None,front_photo=None):
    shirt=name+'_Garment';scene.mat(shirt,color,.88)
    pants=name+'_Trousers';scene.mat(pants,pants_color or color,.9)
    trim=name+'_Trim';scene.mat(trim,trim_color or (.48,.35,.16),.75)
    seam_material=name+'_Seams';scene.mat(seam_material,[c*.82 for c in color],.88)
    old.new=[]
    old.person(name,(0,0,0),0,female=skirt,shirt='REF_Cloth_Blue',trousers='REF_Cloth_Blue',scarf='REF_Cloth_Cream',refs=refs)
    items=list(old.new);old.new=[];scale=.68 if child else 1
    for it in items:
        if it['name'].endswith(('Headscarf_Turban','Face_Details')):continue
        mat=shirt if it['name'].endswith('Tunic') else pants if it['name'].endswith('Dress_Trousers') else 'Shoe_Red' if female and it['name'].endswith('Shoes') else 'Mannequin_Black' if it['name'].endswith(('Skin','Shoes')) else trim
        mesh=it['mesh'];vv=np.asarray(mesh.vertices)
        if it['name'].endswith('Tunic'):
            # The source military jackets hang below the hips. Subtle sculpted folds
            # help the light describe cloth without claiming a recovered garment scan.
            if not traditional:vv[:96,2]-=np.clip((1.23-vv[:96,2])/.36,0,1)*.14
            vv[:,1]+=np.sin(vv[:,2]*38+vv[:,0]*27)*.0045
        if it['name'].endswith('Skin') and headless:
            keep=[i for i,f in enumerate(mesh.faces) if max(vv[f,2])<1.48];mesh.faces=[mesh.faces[i] for i in keep];mesh.uv=[mesh.uv[i] for i in keep]
        if it['name'].endswith('Dress_Trousers') and not skirt:
            if boots and not child:
                keep=[i for i,f in enumerate(mesh.faces) if min(vv[f,2])>.40];mesh.faces=[mesh.faces[i] for i in keep];mesh.uv=[mesh.uv[i] for i in keep]
            if traditional or not female:
                for k,p in enumerate(vv):
                    if .2<p[2]<.88:
                        centre=-.125 if p[0]<0 else .125;factor=1.48 if traditional else 1.22;vv[k,0]=centre+(p[0]-centre)*factor;vv[k,1]*=factor
        if front_photo and it['name'].endswith('Tunic'):
            import cv2
            n,quad=front_photo;texmat=name+'_Original_Garment_Front'
            scene.mat(texmat,(1,1,1),.9,image=f'textures/IMG_{n}.jpg')
            H=cv2.getPerspectiveTransform(np.float32([[0,0],[1,0],[1,1],[0,1]]),np.float32(quad))
            front=Mesh();remaining=[]
            for face in mesh.faces:
                v=vv[face];c=v.mean(axis=0)
                if c[1]<-.045 and abs(c[0])<.215 and c[2]>.71:
                    uvs=[]
                    for x,y,z in v:
                        q=H@np.array([np.clip((x+.21)/.42,0,1),np.clip((1.41-z)/.70,0,1),1]);q/=q[2];uvs.append([float(q[0]),float(1-q[1])])
                    front.append(v*scale,[list(range(len(face)))],[uvs])
                else:remaining.append(face)
            scene.add(name+'_Original_Cloth_Front',front.transformed(origin,yaw),texmat,str(n),'original garment photo projected on simplified cloth form; rear and sides remain estimated',smooth=True)
            mesh.faces=remaining;mesh.uv=[[[0,0] for _ in f] for f in remaining]
        mesh.vertices=(vv*scale).tolist()
        scene.add(it['name'],mesh.transformed(origin,yaw),mat,refs,'simplified mannequin and garment form; sewing detail unmeasured',smooth=True)
    clothes=Mesh();hardware=Mesh()
    if hat=='none' or headless:
        hatmat=shirt
    elif hat in ['pith','helmet']:
        clothes.append(*old.mesh_args(sphere((0,0,1.735),(.16,.145,.12),24,12)))
        clothes.append(*old.mesh_args(torus((0,0,1.67),.165 if hat=='pith' else .145,.026,(0,0,1),32,8)))
        if hat=='helmet':clothes.append(*old.mesh_args(box((0,0,1.85),(.023,.23,.025))))
        hatmat='Helmet_Cream' if hat=='pith' else 'Helmet_Blue'
    elif hat=='fur':
        clothes.append(*old.mesh_args(old.loft([(0,0,1.68,.13,.125,0),(0,0,1.84,.135,.125,0),(0,0,1.92,.085,.085,0)],32)))
        v=np.asarray(clothes.vertices);v[:,:2]*=(1+.035*np.sin(np.arange(len(v))*7))[:,None];clothes.vertices=v.tolist();hatmat='Fur_Dark'
    elif hat=='fez':
        clothes.append(*old.mesh_args(old.loft([(0,0,1.69,.13,.12,0),(0,0,1.86,.10,.095,0)],24)))
        hatmat='Fez_Red'
    elif hat=='scarf':
        clothes.append(*old.mesh_args(sphere((0,.025,1.72),(.14,.12,.09),24,10)))
        clothes.append(*old.mesh_args(old.loft([(0,.035,1.39,.15,.09,0),(0,.035,1.68,.13,.11,0)],24,caps=False)))
        hatmat=shirt
    else:
        clothes.append(*old.mesh_args(cylinder((0,0,1.68),(0,0,1.84),.12,segments=24)))
        clothes.append(*old.mesh_args(box((0,-.11,1.695),(.21,.11,.018))))
        hatmat=shirt
    if hat in ['redkepi','ornate']:
        hardware.append(*old.mesh_args(torus((0,0,1.725),.122,.006,(0,0,1),32,6)))
        hardware.append(*old.mesh_args(torus((0,0,1.76),.122,.006,(0,0,1),32,6)))
        scene.add(name+'_Red_Cap_Band',cylinder((0,0,1.79),(0,0,1.835),.122,segments=32,caps=False).transformed(origin,yaw),'Fez_Red',refs)
    if not front_photo:
        for z in np.linspace(1.00,1.36,5):hardware.append(*old.mesh_args(sphere((0,-.153,float(z)),(.012,.007,.012),10,6)))
    for mesh,mat,suffix in [(clothes,hatmat,'Headwear'),(hardware,'Exhibit_Brass','Buttons_Trim')]:
        if not mesh.vertices:continue
        mesh.vertices=(np.asarray(mesh.vertices)*scale).tolist();scene.add(name+'_'+suffix,mesh.transformed(origin,yaw),mat,refs,smooth=True)
    seams=Mesh()
    seams.append(*old.mesh_args(cylinder((0,0,1.34),(0,0,1.47),.085,segments=24)))
    if not front_photo:
        for x in [-.105,.105]:
            seams.append(*old.mesh_args(box((x,-.155,1.17),(.11,.009,.125))))
            seams.append(*old.mesh_args(cylinder((x,-.165,1.24),(x+.06,-.155,1.35),.006,segments=6)))
    seams.append(*old.mesh_args(cylinder((0,-.15,.97),(0,-.13,1.40),.005,segments=6)))
    for x in [-.18,.18]:seams.append(*old.mesh_args(box((x,0,1.35),(.12,.11,.012))))
    seams.vertices=(np.asarray(seams.vertices)*scale).tolist();scene.add(name+'_Garment_Seams',seams.transformed(origin,yaw),seam_material,refs)
    if traditional:
        embroidery=Mesh()
        for sign in [-1,1]:
            for z in np.linspace(1.02,1.34,8):
                embroidery.append(*old.mesh_args(torus((sign*.135,-.153,float(z)),.024,.004,(0,1,0),12,5)))
        embroidery.vertices=(np.asarray(embroidery.vertices)*scale).tolist();scene.add(name+'_Embroidered_Edges',embroidery.transformed(origin,yaw),trim,refs,'simplified trim placement from the source; exact embroidery pattern not recovered')
    if not female and not child and not traditional:
        strap=join(cylinder((-.19,-.16,1.38),(.17,-.17,.95),.024,segments=6),box((0,-.15,.96),(.41,.035,.06)))
        scene.add(name+'_Leather_Straps',strap.transformed(origin,yaw),'Exhibit_Leather',refs)
    if boots and not female and not child:
        bootmesh=join(cylinder((-.14,-.04,.06),(-.12,-.02,.49),.077,.096,16),cylinder((.14,-.02,.06),(.13,.02,.49),.077,.096,16))
        scene.add(name+'_Long_Boots',bootmesh.transformed(origin,yaw),'Mannequin_Black',refs,smooth=True)

def projected_panel(width,height,source_quad,segments=16):
    """Unchanged photograph sampled by a projective UV grid; no image retouching."""
    import cv2
    H=cv2.getPerspectiveTransform(np.float32([[0,0],[1,0],[1,1],[0,1]]),np.float32(source_quad))
    mesh=Mesh()
    for row in range(segments):
        for col in range(segments):
            st=[(col/segments,(row+1)/segments),((col+1)/segments,(row+1)/segments),((col+1)/segments,row/segments),(col/segments,row/segments)]
            vs=[];uv=[]
            for u,v in st:
                q=H@np.array([u,v,1]);q/=q[2];vs.append([(u-.5)*width,0,(1-v)*height]);uv.append([float(q[0]),float(1-q[1])])
            mesh.append(vs,[[0,1,2,3]],[uv])
    return mesh

def flat_source(scene,name,n,quad,width,depth,origin,yaw=0):
    mesh=projected_panel(width,depth,quad)
    v=np.asarray(mesh.vertices);v[:,1]=v[:,2]-depth/2;v[:,2]=0;mesh.vertices=v.tolist()
    scene.add(name,mesh.transformed(origin,yaw),photo_material(scene,n),str(n),'source-document projection; original lettering preserved')

def source_display_figure(scene,name,n,outline,origin,yaw,height=1.84,depth=.25,back_color=(.17,.18,.16)):
    """A traced, rounded 3D display envelope preserving actual photographed costume details.

    This is explicitly a photo-derived review mesh, not a recovered 360-degree scan.
    Rear geometry and depth are estimates; the visible source image is never retouched.
    """
    from PIL import Image,ImageOps
    from shapely.geometry import Polygon,Point,box as rect
    from shapely import constrained_delaunay_triangles
    src=ROOT/'output/Gaziantep-Museum-2026-10-25/textures'/f'IMG_{n}.jpg'
    if not src.exists():src=ROOT/'review/photo-catalog/images'/f'IMG_{n}.jpg'
    with Image.open(src) as im:
        upright=ImageOps.exif_transpose(im);ratio=upright.width/upright.height
    uvpoly=Polygon(outline)
    assert uvpoly.is_valid,(name,'invalid source contour')
    u0,v0,u1,v1=uvpoly.bounds;unit=height/(v1-v0);uc=(u0+u1)/2
    poly=Polygon([((u-uc)*ratio*unit,(v1-v)*unit) for u,v in outline])
    front=Mesh();back=Mesh();sides=Mesh()
    def surface_y(x,z,sign):
        dist=poly.boundary.distance(Point(x,z));return sign*(.015+depth*.48*math.sin(min(1,dist/.105)*math.pi/2))
    # Source silhouette controls the front. A fine surface grid supplies rounded depth.
    xmin,zmin,xmax,zmax=poly.bounds;cell=.052
    for z in np.arange(zmin,zmax,cell):
        for x in np.arange(xmin,xmax,cell):
            region=poly.intersection(rect(x,z,x+cell,z+cell))
            if region.is_empty or region.area<1e-8:continue
            polys=[region] if region.geom_type=='Polygon' else [p for p in region.geoms if p.geom_type=='Polygon']
            for p in polys:
                for tri in constrained_delaunay_triangles(p).geoms:
                    pts=list(tri.exterior.coords)[:-1]
                    if not tri.exterior.is_ccw:pts.reverse()
                    uv=[[float(px/(ratio*unit)+uc),float(1-(v1-pz/unit))] for px,pz in pts]
                    front.append([[px,surface_y(px,pz,-1),pz] for px,pz in pts],[[0,1,2]],[uv])
                    back.append([[px,surface_y(px,pz,1),pz] for px,pz in pts],[[2,1,0]])
    pts=list(poly.exterior.coords)
    for a,b in zip(pts,pts[1:]):
        sides.append([[a[0],-.015,a[1]],[b[0],-.015,b[1]],[b[0],.015,b[1]],[a[0],.015,a[1]]],[[0,1,2,3]])
    mat=name+'_Estimated_Back';scene.mat(mat,back_color,.9)
    scene.add(name+'_Original_Photo_Surface',front.transformed(origin,yaw),photo_material(scene,n),str(n),'traced source outline and unchanged source texture; rounded depth estimated, not a full garment scan',smooth=True)
    scene.add(name+'_Estimated_Rear',join(back,sides).transformed(origin,yaw),mat,str(n),'rear silhouette and depth estimate; back surface not documented by this photograph',smooth=True)
