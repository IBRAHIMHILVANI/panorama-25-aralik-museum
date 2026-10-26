"""Photo-informed reconstruction, built and written offline into the supplied FBX.

Published panorama dimensions are a modelling constraint, not a site survey.
All props and their placement are reference-based estimates in metres.
"""
from pathlib import Path
from collections import Counter
from dataclasses import dataclass, field
import math,json,hashlib,copy,datetime
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'backups/Untitled-original-2026-10-14.fbx'
OUTPUT=ROOT/'Gaziantep_Panorama_Reconstructed.fbx'
TAU=2*math.pi
C=np.array([-23.,12.])
R=122/TAU
BASE=2.2
rng=np.random.default_rng(20261014)


@dataclass
class Mesh:
    vertices:list=field(default_factory=list)
    faces:list=field(default_factory=list)
    uv:list=field(default_factory=list)

    def append(self,vertices,faces,uv=None):
        off=len(self.vertices)
        self.vertices.extend(np.asarray(vertices,float).tolist())
        self.faces.extend([[int(i)+off for i in f] for f in faces])
        self.uv.extend(uv if uv is not None else [[[0.,0.] for i in f] for f in faces])
        return self

    def transformed(self,loc=(0,0,0),yaw=0):
        v=np.array(self.vertices)
        cs,sn=math.cos(yaw),math.sin(yaw)
        rot=np.array([[cs,-sn,0],[sn,cs,0],[0,0,1.]])
        return Mesh().append(np.einsum('ij,nj->ni',rot,v)+loc,self.faces,copy.deepcopy(self.uv))


def box(center,size,yaw=0,bevel=0):
    # A bevelled cuboid uses three face groups with a small diagonal chamfer.
    cx,cy,cz=center;sx,sy,sz=np.array(size)/2
    if bevel>0:
        b=min(bevel,sx*.32,sy*.32,sz*.32)
        ring=[[-sx+b,-sy], [sx-b,-sy], [sx,-sy+b], [sx,sy-b], [sx-b,sy],[-sx+b,sy],[-sx,sy-b],[-sx,-sy+b]]
        v=[[x,y,z] for z in [-sz,sz] for x,y in ring]
        f=[list(range(7,-1,-1)),list(range(8,16))]+[[i,(i+1)%8,(i+1)%8+8,i+8] for i in range(8)]
    else:
        v=[[x,y,z] for z in [-sz,sz] for y in [-sy,sy] for x in [-sx,sx]]
        f=[[0,2,3,1],[4,5,7,6],[0,1,5,4],[1,3,7,5],[3,2,6,7],[2,0,4,6]]
    return Mesh().append(v,f).transformed(center,yaw)


def loft(rings,segments=20,caps=True):
    # rings: (centre-x, centre-y, z, radius-x, radius-y, phase)
    v=[]
    for x,y,z,rx,ry,phase in rings:
        for i in range(segments):
            a=TAU*i/segments+phase;v.append([x+rx*math.cos(a),y+ry*math.sin(a),z])
    f=[]
    for j in range(len(rings)-1):
        for i in range(segments):
            n=(i+1)%segments;f.append([j*segments+i,j*segments+n,(j+1)*segments+n,(j+1)*segments+i])
    if caps:f.extend([list(range(segments-1,-1,-1)),list(range((len(rings)-1)*segments,len(rings)*segments))])
    return Mesh().append(v,f)


def cylinder(a,b,radius,radius2=None,segments=20,caps=True):
    a,b=np.array(a,float),np.array(b,float);d=b-a;d/=np.linalg.norm(d)
    u=np.cross(d,[0,0,1.] if abs(d[2])<.95 else [0,1.,0]);u/=np.linalg.norm(u);v=np.cross(d,u)
    r2=radius if radius2 is None else radius2
    verts=[]
    for point,r in [(a,radius),(b,r2)]:
        for i in range(segments):
            t=TAU*i/segments;verts.append(point+r*(u*math.cos(t)+v*math.sin(t)))
    faces=[[i,(i+1)%segments,(i+1)%segments+segments,i+segments] for i in range(segments)]
    if caps:faces.extend([list(range(segments-1,-1,-1)),list(range(segments,segments*2))])
    return Mesh().append(verts,faces)


def sphere(center,radii,segments=20,rings=12):
    # No duplicate pole vertices or zero-area pole triangles.
    radii=np.array(radii);center=np.array(center);v=[center+[0,0,-radii[2]]]
    for j in range(1,rings):
        t=-math.pi/2+math.pi*j/rings
        for i in range(segments):
            a=TAU*i/segments;v.append(center+radii*[math.cos(t)*math.cos(a),math.cos(t)*math.sin(a),math.sin(t)])
    top=len(v);v.append(center+[0,0,radii[2]]);f=[]
    for i in range(segments):f.append([0,1+(i+1)%segments,1+i])
    for j in range(rings-2):
        for i in range(segments):
            a=1+j*segments+i;b=1+j*segments+(i+1)%segments;f.append([a,b,b+segments,a+segments])
    off=1+(rings-2)*segments
    for i in range(segments):f.append([off+i,off+(i+1)%segments,top])
    return Mesh().append(v,f)


def torus(center,major,minor,axis=(0,0,1),segments=36,sides=8):
    d=np.array(axis,float);d/=np.linalg.norm(d);u=np.cross(d,[0,0,1] if abs(d[2])<.95 else [0,1,0]);u/=np.linalg.norm(u);v=np.cross(d,u)
    center=np.array(center);verts=[]
    for i in range(segments):
        a=TAU*i/segments;radial=u*math.cos(a)+v*math.sin(a)
        for j in range(sides):
            b=TAU*j/sides;verts.append(center+(major+minor*math.cos(b))*radial+minor*math.sin(b)*d)
    faces=[]
    for i in range(segments):
        for j in range(sides):faces.append([i*sides+j,((i+1)%segments)*sides+j,((i+1)%segments)*sides+(j+1)%sides,i*sides+(j+1)%sides])
    return Mesh().append(verts,faces)


def join(*meshes):
    out=Mesh()
    for mesh in meshes:out.append(mesh.vertices,mesh.faces,mesh.uv)
    return out


def ground(x,y):
    return BASE+.07*math.sin(x*1.7)*math.cos(y*1.25)+.09*math.sin(y*.72)+.06*math.cos(x*.83+y*.36)


new=[]
materials={
 'REF_Earth':(.47,.375,.255),'REF_Earth_Dark':(.34,.285,.215),
 'REF_Limestone':(.64,.585,.465),'REF_Stone_Light':(.75,.687,.56),'REF_Stone_Dark':(.48,.445,.365),
 'REF_Wood':(.29,.205,.12),'REF_Wood_Light':(.48,.34,.20),'REF_Iron':(.115,.12,.11),'REF_Olive':(.31,.35,.23),
 'REF_Rust':(.39,.27,.17),'REF_Cloth_Cream':(.82,.77,.65),'REF_Cloth_White':(.89,.87,.80),
 'REF_Cloth_Red':(.50,.11,.12),'REF_Cloth_Ochre':(.66,.42,.17),'REF_Cloth_Green':(.32,.36,.23),
 'REF_Cloth_Blue':(.15,.24,.32),'REF_Skin':(.63,.47,.335),'REF_Skin_Light':(.76,.60,.46),
 'REF_Black':(.075,.07,.06),'REF_Straw':(.58,.46,.26),'REF_Pottery':(.34,.24,.16),'REF_Copper':(.60,.39,.22),
 'REF_Fire':(1.,.46,.065),'REF_Canvas':(.40,.315,.215),'REF_Rug':(.64,.52,.365),'REF_Flag':(.69,.055,.07),
 'REF_Soffit':(.84,.83,.76),
}
textures={
 'REF_Earth_Photo':'assets/reference_07.jpg',
 'REF_Mural_Battle':'assets/reference_05.jpg',
 'REF_Mural_Bombardment':'assets/reference_08.jpg',
 'REF_Mural_Rubble':'assets/reference_02.jpg',
 'REF_Mural_Hospital':'assets/reference_07.jpg',
 'REF_Mural_Workshop':'assets/reference_01.jpg',
 'REF_Sky_Photo':'assets/reference_04.jpg',
}
for key in textures:materials[key]=(1.,1.,1.)


def add(name,mesh,mat,refs='',accuracy='photo-estimated'):
    if not mesh.vertices:return
    used=sorted({i for face in mesh.faces for i in face})
    if len(used)<len(mesh.vertices):
        mapping={old:i for i,old in enumerate(used)}
        mesh.vertices=[mesh.vertices[i] for i in used]
        mesh.faces=[[mapping[i] for i in face] for face in mesh.faces]
    new.append({'name':name,'mesh':mesh,'material':mat,'refs':str(refs),'accuracy':accuracy})


def arc_wall(center,radius,a0,a1,z0,z1,uv=(0,1,0,1),segments=80):
    verts=[];faces=[];uvs=[]
    for j,z in enumerate([z0,z1]):
        for i in range(segments+1):
            a=a0+(a1-a0)*i/segments;verts.append([center[0]+radius*math.cos(a),center[1]+radius*math.sin(a),z])
    for i in range(segments):
        # Face towards the room, with no mirrored photo or vertical flip.
        faces.append([i+1,i,i+segments+1,i+segments+2])
        u0=uv[0]+(uv[1]-uv[0])*(1-i/segments);u1=uv[0]+(uv[1]-uv[0])*(1-(i+1)/segments)
        uvs.append([[u1,uv[2]],[u0,uv[2]],[u0,uv[3]],[u1,uv[3]]])
    return Mesh().append(verts,faces,uvs)



def mesh_args(m):return m.vertices,m.faces,m.uv

def wheel(center,radius,width=.12,axis=(1,0,0),spokes=12):
    axis=np.array(axis,float);axis/=np.linalg.norm(axis);center=np.array(center)
    u=np.cross(axis,[0,0,1] if abs(axis[2])<.95 else [0,1,0]);u/=np.linalg.norm(u);v=np.cross(axis,u)
    wood=join(torus(center,radius-.045,.052,axis,48,8),cylinder(center-axis*width*.7,center+axis*width*.7,.13,segments=16))
    for i in range(spokes):
        a=TAU*i/spokes;end=center+(radius-.1)*(u*math.cos(a)+v*math.sin(a))
        wood.append(*mesh_args(cylinder(center,end,.033,segments=8)))
    metal=torus(center,radius+.005,.022,axis,48,6)
    return wood,metal


def cannon(name,position,yaw=0,refs='5'):
    # Local gun faces +Y; two spoked carriage wheels have X axes.
    wood=Mesh();metal=Mesh();olive=Mesh();base=np.array(position)
    for x in [-.76,.76]:
        w,m=wheel((x,0,.66),.64,.16,spokes=14);wood.append(*mesh_args(w));metal.append(*mesh_args(m))
    metal.append(*mesh_args(cylinder((-.9,0,.66),(.9,0,.66),.09,segments=16)))
    for x in [-.30,.30]:
        wood.append(*mesh_args(cylinder((x,-2.2,.15),(x,.20,.78),.085,segments=8)))
        wood.append(*mesh_args(box((x,-.45,.65),(.16,1.55,.22),bevel=.03)))
    metal.append(*mesh_args(cylinder((0,-.65,.99),(0,1.72,1.35),.15,.125,segments=32,caps=False)))
    # Open muzzle tube; cap only the back, retain an inner bore at the front.
    metal.append(*mesh_args(torus((0,1.72,1.35),.103,.026,(0,1,.15),32,8)))
    metal.append(*mesh_args(cylinder((0,1.30,1.286),(0,1.72,1.35),.072,segments=24,caps=False)))
    metal.append(*mesh_args(box((0,-.58,.99),(.34,.50,.35),bevel=.03)))
    for y in [-.38,.40,1.35]:
        z=.99+(y+.65)*(.36/2.37);metal.append(*mesh_args(torus((0,y,z),.154,.022,(0,1,.152),32,6)))
    # Segmented shield gives the same angled silhouette as the photo.
    shield=[[-.79,.1,.70],[.79,.1,.70],[.67,.1,1.55],[.3,.1,1.72],[-.3,.1,1.72],[-.67,.1,1.55]]
    olive.append(shield,[list(range(6))]);metal.append(*mesh_args(box((0,-.72,1.30),(.12,.10,.12),bevel=.02)))
    add(name+'_Wooden_Carriage',wood.transformed(base,yaw),'REF_Wood_Light',refs)
    add(name+'_Barrel_Axle_Tyre',metal.transformed(base,yaw),'REF_Iron',refs)
    add(name+'_Shield',olive.transformed(base,yaw),'REF_Olive',refs)



def person(name,position,yaw=0,seated=False,female=False,shirt='REF_Cloth_Red',trousers='REF_Cloth_Green',scarf='REF_Cloth_Cream',refs='7',arms='rest',beard=False,seat_height=.49,foot_height=.06):
    skin=Mesh();clothes=Mesh();lower=Mesh();shoes=Mesh();headwear=Mesh();details=Mesh();trim=Mesh()
    if seated:
        hip=seat_height+.015;bust=hip+.34;neck=hip+.56;head=hip+.70
        knee=max(hip-.075,foot_height+.08)
        legs=[((-.13,.09,hip),(-.20,-.35,knee),(-.20,-.48,foot_height)),((.13,.09,hip),(.27,-.30,knee),(.29,-.53,foot_height))]
    else:
        hip=.87;bust=1.23;neck=1.45;head=1.59
        legs=[((-.12,0,.89),(-.12,-.03,.46),(-.14,-.07,.06)),((.12,0,.89),(.13,.035,.46),(.14,-.035,.06))]
    clothes.append(*mesh_args(loft([(0,0,hip,.20,.14,0),(0,0,bust-.18,.19,.125,0),(0,0,bust,.245,.15,0),(0,0,neck-.10,.13,.11,0)],24)))
    if female and not seated:
        # Folded skirt, with a wider hem, fitted waist and uneven lower edge.
        rings=[]
        for z,rx,ry in [(.04,.34,.24),(.25,.31,.22),(.57,.265,.18),(.90,.20,.135)]:
            rings.append((0,0,z,rx,ry,0))
        dress=loft(rings,36)
        verts=np.array(dress.vertices)
        for i in range(len(verts)):
            a=TAU*(i%36)/36;f=1+.055*math.sin(a*9);verts[i,:2]*=f
        lower.append(verts,dress.faces)
        trim.append(*mesh_args(loft([(0,0,.09,.344,.244,0),(0,0,.27,.318,.228,0)],36,caps=False)))
    else:
        for hip_p,knee_p,ankle in legs:
            lower.append(*mesh_args(cylinder(hip_p,knee_p,.105,.088,16)))
            lower.append(*mesh_args(cylinder(knee_p,ankle,.088,.064,16)))
    for _,_,ankle in legs:shoes.append(*mesh_args(sphere(np.array(ankle)+[0,-.055,-.005],(.095,.16,.059),20,8)))
    shoulders=[(-.215,0,bust-.01),(.215,0,bust-.01)]
    if arms=='work':elbows=[(-.25,-.22,bust-.19),(.25,-.24,bust-.13)];hands=[(-.15,-.48,bust-.04),(.19,-.49,bust-.01)]
    elif arms=='musician':elbows=[(-.28,-.17,bust-.22),(.26,-.25,bust-.09)];hands=[(-.15,-.44,bust-.10),(.48,-.38,bust+.015)]
    elif arms=='nurse':elbows=[(-.30,-.22,bust-.16),(.22,-.26,bust-.17)];hands=[(-.31,-.41,bust-.23),(.12,-.41,bust-.24)]
    else:elbows=[(-.30,.01,bust-.30),(.30,-.03,bust-.30)];hands=[(-.27,-.10,bust-.55),(.29,-.13,bust-.53)]
    for shoulder,elbow,hand in zip(shoulders,elbows,hands):
        clothes.append(*mesh_args(cylinder(shoulder,elbow,.077,.063,16)))
        clothes.append(*mesh_args(cylinder(elbow,hand,.063,.048,16)))
        skin.append(*mesh_args(sphere(hand,(.052,.035,.069),16,8)))
    skin.append(*mesh_args(cylinder((0,0,neck-.06),(0,0,neck+.05),.064,segments=16)))
    skin.append(*mesh_args(sphere((0,-.005,head),(.118,.104,.15),28,16)))
    skin.append(*mesh_args(sphere((0,-.104,head-.005),(.023,.037,.034),14,8)))
    for x in [-.116,.116]:skin.append(*mesh_args(sphere((x,0,head),(.022,.024,.049),14,8)))
    for x in [-.041,.041]:details.append(*mesh_args(sphere((x,-.100,head+.035),(.013,.010,.007),12,6)))
    details.append(*mesh_args(cylinder((-.025,-.101,head-.058),(.025,-.101,head-.058),.004,segments=8)))
    if beard:details.append(*mesh_args(loft([(0,-.014,head-.14,.049,.054,0),(0,-.025,head-.055,.106,.086,0)],20)))
    if female:
        headwear.append(*mesh_args(sphere((0,.018,head+.07),(.132,.116,.104),24,10)))
        headwear.append(*mesh_args(loft([(0,.030,neck-.10,.14,.08,0),(0,.030,head-.03,.13,.105,0)],24,caps=False)))
        headwear.append(*mesh_args(box((0,.085,neck-.14),(.18,.06,.20),bevel=.025)))
    else:
        headwear.append(*mesh_args(sphere((0,.004,head+.112),(.13,.115,.061),24,10)))
        for z in [head+.10,head+.14]:headwear.append(*mesh_args(torus((0,0,z),.106,.019,(0,0,1),28,6)))
    # Waist sash and fabric edges are actual separate geometry.
    trim.append(*mesh_args(loft([(0,0,hip+.05,.206,.146,0),(0,0,hip+.12,.208,.148,0)],24,caps=False)))
    for part,mesh,mat in [('Skin',skin,'REF_Skin_Light'),('Tunic',clothes,shirt),('Dress_Trousers',lower,trousers),('Shoes',shoes,'REF_Black'),('Headscarf_Turban',headwear,scarf),('Face_Details',details,'REF_Black'),('Sash_Hem',trim,'REF_Cloth_Ochre')]:add(name+'_'+part,mesh.transformed(position,yaw),mat,refs)


def patient(name,position,yaw=0):
    head=join(sphere((0,-.72,.30),(.12,.15,.115),24,12),sphere((0,-.855,.315),(.022,.028,.03),12,6))
    body=join(sphere((0,-.15,.245),(.23,.45,.16),24,12),sphere((-.11,.51,.22),(.11,.38,.11),20,10),sphere((.11,.51,.22),(.11,.38,.11),20,10))
    blanket=Mesh();v=[];f=[];nx,ny=18,24
    for j in range(ny+1):
        y=-.4+1.40*j/ny
        for i in range(nx+1):
            x=-.43+.86*i/nx;z=.14+.26*max(0,1-(x/.42)**2)+.02*math.sin(y*19+x*21);v.append([x,y,z])
    for j in range(ny):
        for i in range(nx):a=j*(nx+1)+i;f.append([a,a+1,a+nx+2,a+nx+1])
    blanket.append(v,f)
    bandage=torus((0,-.72,.33),.121,.029,(0,1,0),32,8)
    add(name+'_Head',head.transformed(position,yaw),'REF_Skin',7)
    add(name+'_Body',body.transformed(position,yaw),'REF_Cloth_Blue',7)
    add(name+'_Draped_Blanket',blanket.transformed(position,yaw),'REF_Cloth_Ochre',7)
    add(name+'_Bandage',bandage.transformed(position,yaw),'REF_Cloth_White',7)


def mattress(name,position,yaw=0):
    m=box((0,0,.11),(1.02,1.95,.20),bevel=.09)
    add(name,m.transformed(position,yaw),'REF_Rug',7)
    stripes=Mesh()
    for j in range(11):
        y=-.86+j*.17;stripes.append(*mesh_args(box((0,y,.212),(1.0,.019 if j%3 else .035,.008),bevel=.003)))
    add(name+'_Woven_Stripes',stripes.transformed(position,yaw),'REF_Cloth_Blue',7)
    add(name+'_Pillow',box((0,-.69,.26),(.55,.33,.14),bevel=.08).transformed(position,yaw),'REF_Cloth_Cream',7)


def pot(name,position,radius=.35,height=.48,mat='REF_Iron',refs='7',handles=True):
    rings=[(0,0,0,radius*.66,radius*.66,0),(0,0,.10*height,radius*.92,radius*.92,0),(0,0,height*.8,radius,radius,0),(0,0,height,radius*.9,radius*.9,0),(0,0,height,radius*.81,radius*.81,0),(0,0,height*.14,radius*.80,radius*.80,0)]
    body=loft(rings,32,caps=False)
    body.append(*mesh_args(cylinder((0,0,height*.08),(0,0,height*.12),radius*.80,segments=32)))
    rim=torus((0,0,height),radius*.85,.024,(0,0,1),40,8)
    body.append(*mesh_args(rim))
    if handles:
        for x in [-radius,radius]:body.append(*mesh_args(torus((x,0,height*.67),radius*.2,.025,(0,1,0),20,6)))
    add(name,body.transformed(position),mat,refs)





def tank(position,yaw=-.18):
    base=np.array(position);hull=Mesh();tracks=Mesh();wheels=Mesh();rivets=Mesh();hardware=Mesh()
    profile=[[-1.95,.42],[-1.75,.91],[-.60,1.23],[1.40,1.17],[1.83,.54],[1.30,.31],[-1.20,.31]]
    v=[[x,y,z] for x in [-.73,.73] for y,z in profile];n=len(profile)
    f=[list(range(n-1,-1,-1)),list(range(n,2*n))]+[[i,(i+1)%n,(i+1)%n+n,i+n] for i in range(n)]
    hull.append(v,f)
    # Capsule-shaped continuous track belts with visible tread shoes.
    loop=[]
    for yc,a0 in [(1.35,-math.pi/2),(-1.35,math.pi/2)]:
        for i in range(21):
            a=a0+math.pi*i/20;loop.append((yc+.42*math.cos(a),.58+.42*math.sin(a)))
    for sign in [-1,1]:
        xs=[sign*.84,sign*1.09];v=[]
        for x in xs:
            for y,z in loop:v.append([x,y,z])
        faces=[[i,(i+1)%len(loop),(i+1)%len(loop)+len(loop),i+len(loop)] for i in range(len(loop))]
        tracks.append(v,faces)
        for i,(y,z) in enumerate(loop):
            yy,zz=loop[(i+1)%len(loop)];d=np.array([0,yy-y,zz-z]);length=np.linalg.norm(d)
            if length>.01:
                # Each tread shoe lies transverse to the track path.
                shoe=box((sign*.965,(y+yy)/2,(z+zz)/2),(.31,max(.07,length*.9),.055))
                mid=np.array([sign*.965,(y+yy)/2,(z+zz)/2]);verts=np.array(shoe.vertices)-mid
                theta=math.atan2(d[2],d[1]);cs,sn=math.cos(theta),math.sin(theta);rot=np.array([[1,0,0],[0,cs,-sn],[0,sn,cs]])
                tracks.append(np.einsum('ij,nj->ni',rot,verts)+mid,shoe.faces)
        for y in np.linspace(-1.35,1.35,8):
            radius=.315 if abs(y)>1.2 else .245
            wheels.append(*mesh_args(cylinder((sign*.86,y,.55),(sign*1.12,y,.55),radius,segments=24)))
            hardware.append(*mesh_args(cylinder((sign*1.12,y,.55),(sign*1.15,y,.55),.10,segments=16)))
        for y in np.linspace(-1.4,1.4,9):
            for z in [.51,.91]:rivets.append(*mesh_args(sphere((sign*.747,y,z),(.018,.025,.025),12,6)))
    # Small riveted polygonal turret, supported on its turntable.
    hull.append(*mesh_args(loft([(0,.20,1.24,.57,.57,math.pi/8),(0,.20,1.43,.56,.56,math.pi/8),(0,.20,2.14,.45,.45,math.pi/8)],8)))
    hardware.append(*mesh_args(cylinder((0,.20,2.14),(0,.20,2.21),.24,segments=24)))
    hull.append(*mesh_args(cylinder((0,-.27,1.75),(0,-1.45,1.83),.075,.058,segments=24,caps=False)))
    hardware.append(*mesh_args(torus((0,-1.45,1.83),.047,.014,(0,-1,.08),24,6)))
    for a in np.linspace(0,TAU,24,endpoint=False):
        for z,r in [(1.51,.553),(2.04,.461)]:rivets.append(*mesh_args(sphere((r*math.cos(a),.2+r*math.sin(a),z),(.021,.021,.021),10,6)))
    # Rear skid, towing eye and exhaust separate this from a generic cuboid.
    hardware.append(*mesh_args(box((0,1.98,.35),(.8,1.0,.10),bevel=.025)))
    hardware.append(*mesh_args(cylinder((.47,.65,1.12),(.47,.88,1.53),.048,segments=16)))
    for part,mesh,mat in [('Hull_Turret',hull,'REF_Olive'),('Track_Belts_Shoes',tracks,'REF_Iron'),('Running_Wheels',wheels,'REF_Olive'),('Rivets',rivets,'REF_Rust'),('Hatch_Exhaust_Rear_Skid',hardware,'REF_Iron')]:add('REF_Battle_Tank_'+part,mesh.transformed(base,yaw),mat,'5')


