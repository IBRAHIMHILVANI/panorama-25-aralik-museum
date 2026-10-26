"""Part 02: two-level historical atrium and map hall, referenced to IMG_1946-1977.
Absolute placement, size and stair dimensions remain explicit reconstruction estimates.
"""
from museum_geometry import *
from shapely.geometry import Point,Polygon,LineString,box as rect
from shapely import constrained_delaunay_triangles
import cv2

s=Scene('02_Atrium_Map_Hall');rng=np.random.default_rng(19461977)
C=np.array([33.,8.]);RO=11.2;RI=5.6;LOW=-4.2;TOP=0.;CEIL=3.5
stair_hole=rect(39.75,.75,42.45,13.55)
# User confirmed cinema beside the stair on the right from the map-hall view.
# Exact connector dimensions remain an architectural estimate.
cinema_connector=rect(40.55,-.45,44.51,3.10)
s.mat('Atrium_White',(.83,.81,.75),.8,emission=.22)
s.mat('Gallery_Wall',(.43,.45,.41),.85)
s.mat('Gallery_Dark',(.045,.05,.048),.76)
s.mat('Gallery_Column',(.43,.45,.43),.74)
s.mat('Upper_Stone',(.29,.30,.29),.68)
for i in range(7):s.mat(f'Upper_Stone_{i}',(.24+i*.014,.25+i*.014,.235+i*.014),.65)
s.mat('Handrail_Wood',(.24,.12,.065),.40)
s.mat('Rail_Black',(.045,.05,.05),.4,.6)
s.mat('Rail_Glass',(.65,.73,.71),.14,.04,.16)
s.mat('Steel',(.07,.075,.08),.55,.5)
s.mat('Ceiling_Panels',(.10,.105,.11),.91)
s.mat('Light_Warm',(.97,.86,.63),.4,emission=2)
s.mat('Black_Frame',(.035,.035,.033),.66)
s.mat('Lettering',(.83,.83,.78),.6)
s.mat('Red_Belt',(.45,.018,.025),.8)
s.mat('Model_Terrain',(.50,.42,.32),.9)
s.mat('Model_Buildings',(.67,.64,.54),.9)
s.mat('Model_River',(.05,.25,.50),.7)
s.mat('Model_Grass',(.31,.41,.10),.92)
s.mat('Exit_Green',(.015,.34,.07),.6,emission=.5)

def photo(n):
    key=f'Photo_IMG_{n}'
    if key not in s.materials:s.mat(key,(1,1,1),.75,emission=.15,image=f'textures/IMG_{n}.jpg')
    return key
def addbox(name,p,d,mat,ref='1946-1977',collision=False,yaw=0):s.add(name,box(p,d,yaw),mat,ref,collision=collision)
def polygon_mesh(poly,z,up=True):
    tris=list(constrained_delaunay_triangles(poly).geoms);area=sum(t.area for t in tris)
    assert abs(area-poly.area)<1e-6,(area,poly.area)
    m=Mesh()
    for t in tris:
        pts=list(t.exterior.coords)[:-1]
        if not t.exterior.is_ccw:pts.reverse()
        if not up:pts.reverse()
        m.append([[x,y,z] for x,y in pts],[[0,1,2]])
    return m
def face_at(name,n,width,height,a,r,z,crop=(0,0,1,1)):
    # Fit the complete flat panel and its backing inside the curved wall.
    r=min(r,math.sqrt((RO-.025)**2-((width+.10)/2)**2)-.10)
    p=C+r*np.array([math.cos(a),math.sin(a)]);yaw=a-math.pi/2
    s.add(name,panel(width,height,crop).transformed((*p,z),yaw),photo(n),str(n),'source photograph UV projection; position and size estimated')
    addbox(name+'_Backing',(*list(p+.045*np.array([math.cos(a),math.sin(a)])),z+height/2),(width+.1,.08,height+.1),'Black_Frame',str(n),collision=True,yaw=yaw)
    return p,yaw

disk=Point(*C).buffer(RO,quad_segs=80)
annulus=disk.difference(Point(*C).buffer(RI,quad_segs=80)).difference(stair_hole)
s.add('Atrium_Upper_Structural_Floor',polygon_mesh(annulus,TOP-.035),'Upper_Stone','1946-1948')
s.add('NAV_Atrium_Upper_Walking_Surface',polygon_mesh(annulus,TOP),'Upper_Stone','1946-1948',collision=True,hidden=True)
s.add('Atrium_Upper_Underside',polygon_mesh(annulus,-.29,False),'Gallery_Dark','1969,1974-1977')
s.add('Atrium_Lower_Base_Floor',polygon_mesh(disk.union(cinema_connector),LOW),'Upper_Stone','1969-1977; user cinema connection 2026-10-26',collision=True)
s.add('Cinema_Connector_Ceiling',polygon_mesh(cinema_connector.difference(disk),LOW+2.82,False),'Gallery_Dark','user-confirmed adjacency; dimensions estimated')
for label,a,b in [('South',(40.55,-.45),(44.51,-.45)),('North',(43.15,3.1),(44.51,3.1))]:
    mid=(np.array(a)+np.array(b))/2;length=np.linalg.norm(np.array(b)-a)
    addbox('Cinema_Connector_'+label,(*mid,LOW+1.41),(length,.10,2.82),'Gallery_Wall','user-confirmed cinema beside stair; provisional connector',True)

# The upper stone floor keeps a real central opening and a real stairwell opening.
for j,y in enumerate(np.arange(C[1]-RO,C[1]+RO,.72)):
    for i,x in enumerate(np.arange(C[0]-RO,C[0]+RO,.95)):
        p=rect(x+.008,y+.008,x+.942,y+.712).intersection(annulus)
        if p.is_empty or p.area<.004:continue
        geoms=list(p.geoms) if p.geom_type=='MultiPolygon' else [p]
        for g in geoms:
            if g.geom_type!='Polygon':continue
            mat=f'Upper_Stone_{int(rng.integers(7))}';s.batch('Upper_Floor_Tiles_'+mat,polygon_mesh(g,.006),mat,'1946-1948')

# Circular balcony fascia, glass infill and a continuous timber handrail.
s.add('Atrium_Inner_Fascia',arc_band(C,RI-.04,RI+.16,0,TAU,-.30,.12,192),'Atrium_White','1946,1974-1977',collision=True,smooth=True)
s.add('Atrium_Balcony_Glass',arc_band(C,RI+.09,RI+.11,0,TAU,.13,1.03,192),'Rail_Glass','1946-1948',collision=True)
s.add('Atrium_Continuous_Wood_Handrail',torus((*C,1.07),RI+.10,.052,(0,0,1),256,12),'Handrail_Wood','1946-1948',smooth=True)
for i,a in enumerate(np.linspace(0,TAU,40,endpoint=False)):
    p=C+(RI+.12)*np.array([math.cos(a),math.sin(a)])
    s.batch('Balcony_Posts',box((*p,.40),(.038,.038,1.34)),'Rail_Black','1946,1974')
    for z in [.33,.76]:s.batch('Balcony_Glass_Clamps',sphere((*p,z),(.032,.032,.022),8,6),'Rail_Black','1946')
    # Brackets down the white fascia are visible from the lower hall.
    q=C+(RI+.32)*np.array([math.cos(a),math.sin(a)])
    s.batch('Balcony_Lower_Brackets',box((*q,-.16),(.36,.035,.035),a),'Rail_Black','1974-1977')
    lp=C+(RI+.46)*np.array([math.cos(a),math.sin(a)])
    s.batch('Balcony_Recessed_Downlights',box((*lp,-.305),(.14,.14,.025)),'Light_Warm','1974-1977')

# The complete upper ceiling spans the opening, with round diffusers and downlights.
s.add('Atrium_Upper_Ceiling',polygon_mesh(disk,CEIL,False),'Atrium_White','1946-1948')
for radius,count in [(3.1,7),(7.4,15),(9.8,18)]:
    for i,a in enumerate(np.linspace(0,TAU,count,endpoint=False)):
        p=C+radius*np.array([math.cos(a),math.sin(a)])
        s.batch('Ceiling_Diffuser_Rims',torus((*p,CEIL-.025),.15,.022,(0,0,1),20,6),'Atrium_White','1946-1948')
        s.batch('Ceiling_Diffuser_Core',cylinder((*p,CEIL-.04),(*p,CEIL-.02),.129,segments=16),'Steel','1946-1948')
        for j in range(6):
            aa=j*TAU/6;s.batch('Ceiling_Diffuser_Vanes',box((*p,CEIL-.052),(.25,.022,.018),aa),'Atrium_White','1946')
        q=p+np.array([.42,.35]);s.batch('Upper_Ceiling_Downlights',cylinder((*q,CEIL-.033),(*q,CEIL-.01),.053,segments=12),'Light_Warm','1946-1948')

# Outer walls have an open entrance in the west and an opening for the next gallery below.
N=96
for i in range(N):
    a0=TAU*i/N;a1=TAU*(i+1)/N;deg=(a0+a1)/2*180/math.pi
    upper_open=155<deg<177
    cinema_open=cinema_connector.buffer(.12).contains(Point(*(C+RO*np.array([math.cos((a0+a1)/2),math.sin((a0+a1)/2)]))))
    lower_open=75<deg<100 or cinema_open
    if not upper_open:s.add(f'Upper_Outer_Wall_{i}',arc_band(C,RO,RO+.23,a0,a1,0,CEIL,2),'Atrium_White','1946-1951',collision=True)
    else:s.add(f'Upper_Entrance_Lintel_{i}',arc_band(C,RO,RO+.23,a0,a1,2.85,CEIL,2),'Atrium_White','entry connection inferred',collision=True)
    if not lower_open:s.add(f'Lower_Outer_Wall_{i}',arc_band(C,RO,RO+.23,a0,a1,LOW,-.30,2),'Gallery_Wall','1969-1977',collision=True)
    else:s.add(f'Lower_Gallery_Lintel_{i}',arc_band(C,RO,RO+.23,a0,a1,-1.1,-.30,2),'Gallery_Wall','1969-1977',collision=True)
    if not cinema_open:s.batch('Lower_Wall_Skirting',arc_band(C,RO-.08,RO,a0,a1,LOW,LOW+.12,2),'Gallery_Dark','1969-1977')

# The eastern columns sit in front of the stair, not inside its swept volume.
# This corrects the user-observed clash; positions remain photo-informed estimates.
column_centres=[]
for i,a in enumerate(np.radians([30,90,150,210,270,330])):
    radius=7.15 if i in [0,5] else 8.6
    p=C+radius*np.array([math.cos(a),math.sin(a)]);column_centres.append((i,p))
    s.add(f'Atrium_Column_{i}',cylinder((*p,LOW),(*p,CEIL),.48,segments=48),'Gallery_Column','1946,1969,1974-1977',collision=True,smooth=True)
    for z in [LOW,0]:s.batch('Column_Base_Collars',cylinder((*p,z),(*p,z+.10),.50,segments=40),'Gallery_Dark','1946,1976')

# Exposed lower-level steel structure, conduits and suspended lighting rails.
def segments_clear_of_stair(p,q,padding):
    cut=LineString([p,q]).difference(stair_hole.buffer(padding,join_style=2))
    pieces=[cut] if cut.geom_type=='LineString' else list(cut.geoms)
    return [(np.array(line.coords[0]),np.array(line.coords[-1])) for line in pieces if line.geom_type=='LineString' and line.length>.06]
for a in np.linspace(0,TAU,14,endpoint=False):
    p=C+RI*np.array([math.cos(a),math.sin(a)]);q=C+RO*np.array([math.cos(a),math.sin(a)])
    for p0,q0 in segments_clear_of_stair(p,q,.35):
        mid=(p0+q0)/2;length=np.linalg.norm(q0-p0)
        s.batch('Lower_Steel_Main_Beams',box((*mid,-.47),(length,.23,.30),a),'Steel','1969,1974-1977')
        for z in [-.30,-.64]:s.batch('Lower_Steel_Beam_Flanges',box((*mid,z),(length,.39,.04),a),'Steel','1974-1977')
    p2=C+(RI+.4)*np.array([math.cos(a),math.sin(a)]);q2=C+(RO-.2)*np.array([math.cos(a+.08),math.sin(a+.08)])
    for p0,q0 in segments_clear_of_stair(p2,q2,.12):s.batch('Lower_Ceiling_Cable_Trays',cylinder((*p0,-.72),(*q0,-.72),.038,segments=8),'Steel','1974-1977')
    for r in [7.0,9.4]:
        p=C+r*np.array([math.cos(a),math.sin(a)])
        if stair_hole.buffer(.22).contains(Point(*p)):continue
        s.batch('Lower_Track_Spotlight_Cases',cylinder((*p,-.73),(*p,-.92),.10,segments=16),'Steel','1969,1974-1977')
        s.batch('Lower_Track_Spotlight_Lenses',cylinder((*p,-.925),(*p,-.91),.074,segments=16),'Light_Warm','1969,1974-1977')
for x in [39.48,42.72]:
    s.batch('Stairwell_Steel_Headers',box((x,7.15,-.47),(12.8,.23,.30),math.pi/2),'Steel','stair opening support; reconstruction estimate')
    for z in [-.30,-.64]:s.batch('Stairwell_Header_Flanges',box((x,7.15,z),(12.8,.39,.04),math.pi/2),'Steel','stair opening support; reconstruction estimate')

# Straight stair seen behind the column in IMG_1974/1975. Dimensions are estimates.
SX=41.1;SY0=1.0;SY1=13.4;SW=2.25;steps=28
stair_envelope=rect(SX-SW/2-.12,SY0,SX+SW/2+.12,SY1)
clearances=[{'column':'Atrium_Column_'+str(i),'centre_xy_m':p.tolist(),'clearance_to_stair_m':Point(*p).buffer(.50,quad_segs=48).distance(stair_envelope)} for i,p in column_centres]
assert all(c['clearance_to_stair_m']>=.12 for c in clearances),clearances
(ROOT/'reconstruction/part02-column-clearances.json').write_text(json.dumps({'minimum_clearance_m':min(c['clearance_to_stair_m'] for c in clearances),'columns':clearances,'passed':True},indent=2))
for i in range(steps):
    y0=SY0+(SY1-SY0)*i/steps;y1=SY0+(SY1-SY0)*(i+1)/steps;z=LOW+(0-LOW)*(i+1)/steps
    addbox(f'Atrium_Stair_Tread_{i+1}',(SX,(y0+y1)/2,z-.075),(SW,y1-y0,.15),'Upper_Stone','1974,1975; dimensions estimated')
    s.batch('Stair_NonSlip_Nosings',box((SX,y0+.025,z+.008),(SW-.04,.05,.018)),'Steel','1974,1975')
s.add('NAV_Atrium_Stair_Incline',Mesh().append([[SX-SW/2,SY0,LOW],[SX+SW/2,SY0,LOW],[SX+SW/2,SY1,0],[SX-SW/2,SY1,0]],[[0,1,2,3]]),'Upper_Stone',collision=True,hidden=True)
v=[[SX-SW/2,SY0,LOW-.04],[SX+SW/2,SY0,LOW-.04],[SX+SW/2,SY1,-.04],[SX-SW/2,SY1,-.04],[SX-SW/2,SY0,LOW-.32],[SX+SW/2,SY0,LOW-.32],[SX+SW/2,SY1,-.32],[SX-SW/2,SY1,-.32]]
s.add('Atrium_Stair_Continuous_Soffit',Mesh().append(v,[[0,1,2,3],[7,6,5,4],[4,5,1,0],[5,6,2,1],[6,7,3,2],[7,4,0,3]]),'Atrium_White','1974,1975',collision=True)
for sign in [-1,1]:
    x=SX+sign*(SW/2+.06);v=[[xx,y,z] for xx in [x-.06,x+.06] for y,z in [(SY0,LOW-.2),(SY1,-.2),(SY1,1.05),(SY0,LOW+1.05)]]
    faces=[[3,2,1,0],[4,5,6,7],[0,4,5,1],[3,2,6,7],[0,3,7,4],[1,5,6,2]]
    s.add('Stair_Parapet_'+str(sign),Mesh().append(v,faces),'Atrium_White','1974,1975',collision=True)
    s.add('Stair_Timber_Rail_'+str(sign),cylinder((x,SY0,LOW+1.08),(x,SY1,1.08),.04,segments=16),'Handrail_Wood','1974,1975',smooth=True)
# Landings share the exact staircase end heights.
s.add('NAV_Stair_Upper_Landing',plane_xy(SX-SW/2,SX+SW/2,SY1,SY1+.55,0),'Upper_Stone',collision=True,hidden=True)
addbox('Stair_Upper_Landing',(SX,SY1+.275,-.06),(SW,.55,.12),'Upper_Stone')

# True-source timeline image is mapped around the curved wall; text is not retyped.
a0=math.radians(-40);a1=math.radians(55)
s.add('Upper_Chronology_Timeline',old.arc_wall(C,RO-.08,a0,a1,.68,2.70,(0,.875,.27,.70),180),photo(1951),'1951','source photograph; observed curved timeline')
for z in [.64,2.74]:s.add('Timeline_Light_Trim_'+str(z),arc_line(C,RO-.11,a0,a1,z,.018,100),'Light_Warm','1951')
face_at('Upper_Socioeconomic_Display',1950,5.4,2.45,math.radians(77),RO-.10,.58,(.05,.265,.94,.805))
face_at('Upper_Redif_Depot_Display',1949,5.8,2.24,math.radians(116),RO-.10,.62,(.17,.33,.79,.74))
# A physical miniature plinth under the Redif display, with simplified relief buildings.
ma=math.radians(116);mp=C+9.3*np.array([math.cos(ma),math.sin(ma)]);yaw=ma-math.pi/2
addbox('Redif_Miniature_Plinth',(*mp,.43),(5.6,1.1,.86),'Gallery_Dark','1949',collision=True,yaw=yaw)
addbox('Redif_Miniature_Terrain',(*mp,.88),(5.5,1.05,.06),'Model_Terrain','1949',yaw=yaw)
for i in range(38):
    u=rng.uniform(-2.6,2.6);v=rng.uniform(-.45,.45);z=rng.uniform(.04,.19)
    m=box((u,v,.92+z/2),(rng.uniform(.12,.35),rng.uniform(.10,.25),z)).transformed((*mp,0),yaw)
    s.batch('Redif_Miniature_Buildings',m,'Model_Buildings','1949')

# Backlit historic photographs, individually framed instead of a single flat wall image.
cards=[(1952,(.15,.26,.45,.44),1.05,.74),(1952,(.51,.28,.64,.40),.65,.60),(1952,(.03,.53,.46,.78),1.20,.75),(1952,(.52,.44,.69,.71),.62,.95),(1958,(.32,.19,.55,.31),.9,.55),(1958,(.05,.35,.34,.52),1.05,.62),(1958,(.40,.36,.68,.68),.82,1.1),(1960,(.01,.20,.41,.40),1.20,.68),(1960,(.53,.38,.78,.67),.78,.90),(1960,(.84,.21,.99,.48),.58,.90)]
for i,(n,crop,w,h) in enumerate(cards):
    a=math.radians(203+(i//2)*10.6);z=1.77 if i%2==0 else .49
    p,yaw=face_at(f'Historic_Photo_{i+1}',n,w,h,a,RO-.11,z,crop)
    for dx in [-w/2,w/2]:
        q=np.array([dx,-.018,0]);s.batch('Historic_Photo_Edge_Lighting',box((dx,0,h/2),(.014,.045,h+.04)).transformed((*p,z),yaw),'Light_Warm',str(n))

# Lower wall display crops are taken directly from the user's full-resolution panorama.
lower_panels=[(1969,(.045,.32,.119,.645),-155,2.95,2.05),(1969,(.128,.31,.227,.65),-126,3.8,2.05),(1969,(.286,.28,.358,.60),-95,2.6,2.15),(1969,(.737,.30,.860,.62),-59,4.3,2.05),(1969,(.897,.30,.994,.635),-25,3.4,2.05),(1963,(.015,.25,.995,.765),15,4.0,2.5),(1962,(.06,.22,.95,.67),119,4.7,2.1)]
for i,(n,crop,a,w,h) in enumerate(lower_panels):
    if i==2 and (ROOT/'output/Gaziantep-Museum-2026-10-25/textures/map-legend-clean-background-v2.png').exists():
        # Generated typography/background is used only for the verified headings.
        # Every place name and number below is sampled directly from the source crop.
        h=1.95;ang=math.radians(a);pos=C+(RO-.11)*np.array([math.cos(ang),math.sin(ang)]);yaw=ang-math.pi/2
        s.mat('Photo_Legend_Clean_Header',(1,1,1),.75,emission=.15,image='textures/map-legend-clean-background-v2.png')
        s.mat('Photo_Legend_Original_Body',(1,1,1),.75,emission=.15,image='textures/map-legend-original-crop.png')
        s.add('Lower_City_Exhibit_3_Clean_Background',panel(w,h).transformed((*pos,LOW+.66),yaw),'Photo_Legend_Clean_Header','1969; IMAGEGEN background with verified headings','generated graphic background; original-source lettering is a separate layer')
        addbox('Lower_City_Exhibit_3_Backing',(*list(pos+.045*np.array([math.cos(ang),math.sin(ang)])),LOW+.66+h/2),(w+.10,.08,h+.10),'Black_Frame','1969',collision=True,yaw=yaw)
        original_quad=np.float32([[.028,.066],[.940,.099],[.940,.855],[.046,.924]])
        HH=cv2.getPerspectiveTransform(np.float32([[0,0],[1,0],[1,1],[0,1]]),original_quad)
        body=Mesh();nx,ny=30,26
        vs=[];fs=[];uv=[]
        for jj in range(ny+1):
            vv=.182+(.982-.182)*jj/ny
            for ii in range(nx+1):
                uu=.020+(.980-.020)*ii/nx;q=HH@np.array([uu,vv,1.]);q/=q[2]
                vs.append([(uu-.5)*w,-.006,(1-vv)*h]);uv.append([float(q[0]),float(1-q[1])])
        for jj in range(ny):
            for ii in range(nx):
                aa=jj*(nx+1)+ii;fs.append([aa+nx+1,aa+nx+2,aa+1,aa])
        body.append(vs,fs,[[uv[k] for k in f] for f in fs])
        s.add('Lower_City_Exhibit_3_Original_Lettering',body.transformed((*pos,LOW+.66),yaw),'Photo_Legend_Original_Body','native IMG_1969 crop','unmodified source pixels; projective UV rectification only; no generated names or numbers')
    else:face_at(f'Lower_City_Exhibit_{i+1}',n,w,h,math.radians(a),RO-.11,LOW+.66,crop)

# Floor map is a projective UV sampling of the visible source map, not invented cartography.
# No source pixels are painted, inpainted or replaced. The source glare is retained.
P=Point(*C).buffer(10.65,quad_segs=80)
verts=[];faces=[];uvs=[];extent=10.65
world=np.float32([[C[0]-extent,C[1]+extent],[C[0]+extent,C[1]+extent],[C[0]+extent,C[1]-extent],[C[0]-extent,C[1]-extent]])
source=np.float32([[.11,.66],[.93,.66],[.995,.995],[.005,.995]])
H=cv2.getPerspectiveTransform(world,source)
generated_map=(ROOT/'output/Gaziantep-Museum-2026-10-25/textures/floor-map-imagegen-v1.png').exists()
if generated_map:s.mat('Photo_Floor_Map_Imagegen',(1,1,1),.8,emission=.15,image='textures/floor-map-imagegen-v1.png')
floor_map=Mesh()
for y in np.linspace(C[1]-extent,C[1]+extent,61)[:-1]:
    for x in np.linspace(C[0]-extent,C[0]+extent,61)[:-1]:
        cell=rect(x,y,x+2*extent/60,y+2*extent/60).intersection(P)
        if cell.is_empty or cell.area<1e-6:continue
        pts=list(cell.exterior.coords)[:-1]
        if not cell.exterior.is_ccw:pts.reverse()
        vs=[];uv=[]
        for px,py in pts:
            q=H@np.array([px,py,1.]);q/=q[2];vs.append([px,py,LOW+.014])
            uv.append([float((px-C[0]+extent)/(2*extent)),float((py-C[1]+extent)/(2*extent))] if generated_map else [float(q[0]),float(1-q[1])])
        floor_map.append(vs,[list(range(len(vs)))],[uv])
s.add('Lower_Historical_Map_Photo_Projection',floor_map,'Photo_Floor_Map_Imagegen' if generated_map else photo(1976),'1974,1976,1977; IMAGEGEN visual restoration' if generated_map else '1976; compared with 1969,1974,1975,1977','generated top-view visual reconstruction; fine cartographic layout is not independently verified' if generated_map else 'visible-source photo projection; not a complete orthorectified reproduction of the floor map')
# A fine tile-joint grid corresponds to the physical glazed protective floor.
for q in np.arange(-10,10.01,.9):
    extent=math.sqrt(max(0,10.65**2-q*q))
    s.batch('Map_Protective_Floor_Joints',box((C[0]+q,C[1],LOW+.018),(.004,2*extent,.006)),'Gallery_Column','1974-1977')
    s.batch('Map_Protective_Floor_Joints',box((C[0],C[1]+q,LOW+.018),(2*extent,.004,.006)),'Gallery_Column','1974-1977')

# Physical corridor between the approved courtyard doorway and the atrium entrance.
bridge=Polygon([(20.0,10.5),(23.7,9.7),(25,13.2),(21.4,14.2)])
s.add('Atrium_Entry_Connection_Floor',polygon_mesh(bridge,0),'Upper_Stone','connection position provisional',collision=True)
for i,(a,b) in enumerate([((20,10.5),(23.7,9.7)),((21.4,14.2),(25,13.2))]):
    av=np.array(a);bv=np.array(b);mid=(av+bv)/2
    addbox(f'Entry_Connection_Wall_{i}',(*mid,1.45),(float(np.linalg.norm(bv-av)),.15,2.9),'Gallery_Wall','connection position provisional',collision=True,yaw=math.atan2(bv[1]-av[1],bv[0]-av[0]))
s.add('Entry_Connection_Ceiling',polygon_mesh(bridge,2.9,False),'Atrium_White','connection position provisional')
# A shallow lower-level landing keeps the next chronological gallery connection open.
s.add('Lower_Next_Gallery_Landing',plane_xy(30.0,36.0,18.0,22.7,LOW),'Upper_Stone','1969-1977',collision=True)
addbox('Lower_Next_Gallery_Ceiling',(33,21,-.42),(6.2,5.3,.20),'Gallery_Dark')
for x in [30.0,36.0]:addbox('Lower_Next_Gallery_Side_'+str(x),(x,20.55,(LOW-.52)/2),(.20,4.3,-.52-LOW),'Gallery_Wall','connection toward next gallery; placement estimated',collision=True)
s.add('REVIEW_Next_Section_Boundary',box((33,22.6,(LOW-.5)/2),(6.2,.10,-.5-LOW)),'Gallery_Dark','review helper; not museum geometry',collision=True)
s.objects[-1].update(review_only=True,temporary_until='part03')
s.text('REVIEW_Next_Section_Label','NEXT SECTION\nIN PREPARATION',(33,22.53,LOW+1.45),.24)
s.texts[-1].update(review_only=True,temporary_until='part03')

s.views=[
 {'id':'atrium','title':'الاستقبال والفتحة الدائرية','position':[25,10.5,1.65],'target':[35,8,0.4],'photo':1946},
 {'id':'timeline','title':'الخط الزمني','position':[33,1,1.65],'target':[41,6,1.7],'photo':1951},
 {'id':'redif','title':'معرض مخزن الرديف','position':[28.3,14.3,1.65],'target':[28.1,17.5,1.55],'photo':1949},
 {'id':'stairs','title':'النزول إلى قاعة الخريطة','position':[41.1,14.0,1.65],'target':[41.1,4,-2.0],'photo':1974},
 {'id':'staircheck','title':'الدرج والأعمدة بعد التصحيح','position':[36.5,8,-2.55],'target':[41.1,8,-1.2],'photo':1974},
 {'id':'maphall','title':'قاعة الخريطة من الأسفل','position':[33,1.5,-2.55],'target':[33,12,-1.1],'photo':1976},
 {'id':'mapdetail','title':'تفاصيل الخريطة المصوّرة','position':[35.2,5.3,-2.55],'target':[33,10,-4.15],'photo':1976,'reference_image':'../../reconstruction/imagegen-inputs/floor-source-1976.png'},
 {'id':'legend','title':'لوحة أسماء الأماكن','position':[32.15,-.75,-2.55],'target':[32.04,-3.05,-2.56],'photo':1969,'reference_image':'../../reconstruction/imagegen-inputs/board-source.png'},
 {'id':'balcony','title':'الدرابزين من الأسفل','position':[29,4,-2.55],'target':[35,10,.2],'photo':1974}]
s.views.append({'id':'cinemaentry','title':'باب السينما بجانب الدرج من جهة قاعة الخريطة','position':[43.45,2.4,LOW+1.65],'target':[46.0,2.4,LOW+1.65],'reference_image':'../../references/fidelity-2026-10-26/cinema-reference.jpg','reference_label':'السينما الحقيقية؛ الاتصال بالدرج حسب إفادة المستخدم'})
s.save(ROOT/'reconstruction/part02-scene.json')
(ROOT/'reconstruction/part02-notes.json').write_text(json.dumps({'title':'الاستقبال وقاعة الخريطة','stage':'draft for joint visual review','source_photos':'IMG_1946 through IMG_1977','observed':['Two-level circular atrium','Central circular void and timber/glass balustrade','Upper timeline and Redif history display','Round columns and exposed lower steel ceiling','Straight stair behind the lower hall columns','Large photographic historical floor map'], 'unverified':['All dimensions and connection to courtyard remain unmeasured','Stair height, tread count and global orientation are estimates','Floor map uses the visible part of IMG_1976 with projective UVs, not a complete orthorectified map; hidden map areas are not recovered'],'accuracy_100_percent':False},indent=2,ensure_ascii=False))
