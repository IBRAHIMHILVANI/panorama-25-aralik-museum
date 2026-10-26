"""Bounded architectural details from original photos and the May-2026 360.

Feature forms are observed; dimensions and angles are explicitly model estimates.
The unlocated stone arch is intentionally not added to the circulation plan.
"""
from museum_geometry import *
from museum_architecture import arc_band, polygon_plate

REFS='live-review-2026-10-26/03,13,15,16; restored IMG_2239/2242'
BASIS='Observed form; metric dimensions and angular placement estimated, not surveyed'

def tube_path(points,radius=.008):
    mesh=Mesh()
    for a,b in zip(points,points[1:]):
        if np.linalg.norm(np.asarray(b)-a)>1e-6:
            mesh.append(*old.mesh_args(cylinder(a,b,radius,segments=6)))
    return mesh

def tank_terrace_rail(s,centre,xy,xyz,a0=288.,a1=306.):
    """One estimated bay to camera-left of the model's tank, outside walk radius."""
    s.mat('Panorama_Iron_Dark',(.17,.145,.12),.68,.5)
    r=9.445
    s.add('Tank_Terrace_Low_Stone_Base',arc_band(centre,9.34,9.55,math.radians(a0),math.radians(a1),-.03,.24,48),'Stone_Base',REFS,BASIS,collision=True)
    s.add('NAV_Tank_Terrace_Iron_Barrier',arc_band(centre,9.35,9.54,math.radians(a0),math.radians(a1),.22,1.12,48),'Panorama_Iron_Dark',REFS,'Hidden continuous safety barrier behind open ironwork; estimated bay',collision=True,hidden=True)
    rail=Mesh()
    for z in [.28,1.09,1.125]:
        rail.append(*old.mesh_args(tube_path([xyz(r,a,z) for a in np.linspace(a0,a1,100)],.015 if z<1.1 else .018)))
    for a in [a0,a1]:
        s.add('Tank_Terrace_Stone_Pier_'+str(a),box(xyz(r,a,.59),(.30,.30,1.18),math.radians(a)),'Stone_3',REFS,BASIS,collision=True)
        s.add('Tank_Terrace_Stone_Pier_Cap_'+str(a),box(xyz(r,a,1.18),(.35,.35,.09),math.radians(a)),'Stone_2',REFS,BASIS)
    # Curl/diamond rhythm follows the visible open scrollwork, not a texture plane.
    length=r*math.radians(a1-a0);start=.18;end=length-.18;cells=6;pitch=(end-start)/cells
    def pos(u,z):return xyz(r,a0+math.degrees(u/r),z)
    for i in range(cells+1):
        u=start+i*pitch;rail.append(*old.mesh_args(cylinder(pos(u,.28),pos(u,1.09),.009,segments=6)))
    for i in range(cells):
        mid=start+(i+.5)*pitch
        diamond=[(mid-pitch*.43,.69),(mid,.93),(mid+pitch*.43,.69),(mid,.45),(mid-pitch*.43,.69)]
        rail.append(*old.mesh_args(tube_path([pos(u,z) for u,z in diamond],.007)))
        for zc in [.42,.69,.96]:
            for sign in [-1,1]:
                points=[]
                for t in np.linspace(0,math.pi*2.0,36):
                    rr=.105*(1-.83*t/(math.pi*2));points.append(pos(mid+sign*(.06+rr*math.cos(t)),zc+rr*math.sin(t)))
                rail.append(*old.mesh_args(tube_path(points,.007)))
    s.add('Tank_Terrace_Ornate_Ironwork',rail,'Panorama_Iron_Dark',REFS,BASIS,smooth=True)

def tank_wagon_canopies(s,xy,xyz):
    refs='restored IMG_2239/2242; live-review-2026-10-26/03,14,15,16'
    for name,col in [('Canopy_Tank_Cloth',(.56,.43,.28)),('Canopy_Wagon_Cloth',(.51,.39,.25)),('Canopy_Overlap_Cloth',(.58,.45,.30)),('Canopy_Repair_Cloth',(.31,.25,.19)),('Canopy_Seam_Fibre',(.42,.33,.23))]:s.mat(name,col,.98)
    spans=[(288.,310.4,.30,'Canopy_Tank_Cloth'),(309.7,335.2,.39,'Canopy_Wagon_Cloth'),(334.5,360.,.34,'Canopy_Overlap_Cloth')]
    def point(a0,a1,sag,u,t,offset=0):
        r=5.72+3.94*u;a=a0+(a1-a0)*t
        z=3.17-.24*u-sag*math.sin(math.pi*u)*math.sin(math.pi*t)+.035*math.sin(7*math.pi*t+.8)*u-.045*math.sin(math.pi*t)*u+offset
        return xyz(r,a,z)
    for idx,(a0,a1,sag,mat) in enumerate(spans):
        v=[];faces=[];nu=20;nt=48
        for j in range(nu+1):
            for i in range(nt+1):v.append(point(a0,a1,sag,j/nu,i/nt,idx*.012))
        for j in range(nu):
            for i in range(nt):k=j*(nt+1)+i;faces.append([k,k+1,k+nt+2,k+nt+1])
        s.add('Tank_Wagon_Draped_Cloth_'+str(idx),Mesh().append(v,faces),mat,refs,BASIS,smooth=True)
        seams=Mesh();stitches=Mesh()
        for t in [0,.48,1]:
            seams.append(*old.mesh_args(tube_path([point(a0,a1,sag,u,t,-.007) for u in np.linspace(0,1,70)],.004)))
            for u in np.arange(.035,.99,.025):stitches.append(*old.mesh_args(tube_path([point(a0,a1,sag,u,t-.0025,-.009),point(a0,a1,sag,u,t+.0025,-.009)],.002)))
        for u in [0,1]:seams.append(*old.mesh_args(tube_path([point(a0,a1,sag,u,t,-.006) for t in np.linspace(0,1,85)],.005)))
        s.add('Tank_Wagon_Cloth_Seams_'+str(idx),seams,'Canopy_Seam_Fibre',refs,BASIS,smooth=True)
        s.add('Tank_Wagon_Cloth_Stitches_'+str(idx),stitches,'Canopy_Seam_Fibre',refs,BASIS)
        # Only two irregular repairs in this photographed sector; no ring-wide repetition.
        if idx in [0,2]:
            centre_u,centre_t=(.37,.61) if idx==0 else (.62,.34)
            uv=[(-.09,-.04),(.07,-.055),(.10,.045),(-.075,.06)]
            patch=[point(a0,a1,sag,centre_u+u,centre_t+t,-.013) for u,t in uv]
            s.add('Tank_Wagon_Cloth_Repair_'+str(idx),Mesh().append(patch,[[0,1,2,3]]),'Canopy_Repair_Cloth',refs,'Repair patches observed; these two patch positions and outlines are estimated')
            s.add('Tank_Wagon_Repair_Stitch_Edge_'+str(idx),tube_path(patch+[patch[0]],.003),'Canopy_Seam_Fibre',refs,BASIS)
    for idx,a in enumerate([288.,310.,334.8,359.6]):
        s.add('Tank_Wagon_Projecting_Pole_'+str(idx),cylinder(xyz(5.75,a,3.10),xyz(10.0,a,2.88),.042,segments=10),'REF_Wood',refs,BASIS,smooth=True)
        # Ropes hang at the scenic edge, safely outside the visitor path.
        s.add('Tank_Wagon_Rope_Tie_'+str(idx),tube_path([xyz(9.52,a,2.93),xyz(9.72,a+.12,2.85),xyz(9.78,a+.1,2.51)],.008),'Rope_Fibre',refs,BASIS)
        loop=[xyz(9.78+.07*math.sin(t),a+.1,2.57+.115*math.cos(t)) for t in np.linspace(0,2*math.pi,40)]
        s.add('Tank_Wagon_Rope_Loop_'+str(idx),tube_path(loop,.007),'Rope_Fibre',refs,BASIS)
    return {'observed':'sagging overlapping cloth, seams, repair patches, projecting supports, tied rope loops','estimated_angular_extent_degrees':[288,360],'sheets':3,'localized_repair_patches':2,'minimum_sheet_z_m':min(v[2] for o in s.objects if o['name'].startswith('Tank_Wagon_Draped_Cloth') for v in o['vertices'])}

def upper_corridor_details(s,line):
    refs='restored original IMG_2216 and IMG_2217'
    s.mat('Upper_Corridor_Lantern_Metal',(.17,.12,.075),.56,.45)
    s.mat('Upper_Corridor_Lantern_Amber',(1,.45,.08),.45,0,1,3)
    for i,d in enumerate(np.arange(.45,line.length-.10,.54)):
        p=np.array(line.interpolate(d).coords[0]);v=np.array(line.interpolate(d+.04).coords[0])-np.array(line.interpolate(d-.04).coords[0]);v/=np.linalg.norm(v);n=np.array([-v[1],v[0]])
        s.add('Upper_Corridor_Timber_Joist_'+str(i),cylinder((*list(p-n*1.06),2.64),(*list(p+n*1.06),2.64),.085,segments=14),'REF_Wood',refs,BASIS,smooth=True)
    for i,d in enumerate([1.20,line.length-1.05]):
        p=np.array(line.interpolate(d).coords[0]);metal=Mesh()
        metal.append(*old.mesh_args(cylinder((*p,2.75),(*p,2.60),.012,segments=8)))
        for z in [2.32,2.59]:metal.append(*old.mesh_args(cylinder((*p,z-.025),(*p,z+.025),.075,segments=12)))
        for a in np.linspace(0,2*math.pi,8,endpoint=False):
            x,y=p+.061*np.array([math.cos(a),math.sin(a)]);metal.append(*old.mesh_args(cylinder((x,y,2.34),(x,y,2.58),.006,segments=6)))
        s.add('Upper_Corridor_Lantern_Cage_'+str(i),metal,'Upper_Corridor_Lantern_Metal',refs,BASIS)
        s.add('Upper_Corridor_Lantern_Glow_'+str(i),cylinder((*p,2.35),(*p,2.56),.044,segments=12),'Upper_Corridor_Lantern_Amber',refs,BASIS)
        s.lights.append({'position':[*p,2.43],'energy':9,'angle':120,'color':[1,.48,.16]})
