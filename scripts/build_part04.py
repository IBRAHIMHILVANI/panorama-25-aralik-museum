"""Portrait passage, red gallery, Kastel rooms and correspondence exhibits.
Source photographs IMG_2081–2143. Geometry is a connected review reconstruction;
absolute room dimensions remain estimates pending a measured interior plan.
"""
from museum_geometry import *
from museum_architecture import *
from museum_exhibits import photo_material,projected_panel,flat_source
from shapely.geometry import Polygon,Point,box as rect
import cv2

s=Scene('04_Kastel_Correspondence');C=np.array([-6.,23.5]);F=-4.2;LOW=-4.95;H=3.7;A0=62.;A1=105.
def xy(r,a):a=math.radians(a);return C+r*np.array([math.cos(a),math.sin(a)])
def xyz(r,a,z):return (*xy(r,a),z)
def sec(ri,ro,a,b,n=100):return Polygon([xy(ro,t) for t in np.linspace(a,b,n+1)]+[xy(ri,t) for t in np.linspace(b,a,n+1)])
def cube(name,p,d,mat,refs='',yaw=0,collision=False):s.add(name,box(p,d,yaw),mat,refs,collision=collision)
def ring(name,ri,ro,a,b,z0,z1,mat,refs='',collision=False):s.add(name,arc_band(C,ri,ro,math.radians(a),math.radians(b),z0,z1,max(8,int((b-a)*3))),mat,refs,collision=collision)
def linewall(name,a,b,z0,z1,d,mat,refs='',collision=True):
    a=np.array(a);b=np.array(b);p=(a+b)/2;cube(name,(*p,(z0+z1)/2),(np.linalg.norm(b-a),d,z1-z0),mat,refs,math.atan2(*(b-a)[::-1]),collision)
def photo(n):return photo_material(s,n)
for name,col,rough,metal,alpha,em in [
 ('Wall_Gray',(.43,.44,.41),.88,0,1,.06),('Floor_Base',(.25,.25,.23),.68,0,1,0),
 ('Black',(.035,.04,.038),.6,0,1,0),('Steel',(.16,.17,.16),.48,.6,1,0),
 ('Ceiling',(.05,.055,.052),.9,0,1,0),('Slat_Wood',(.64,.60,.52),.8,0,1,.05),
 ('Stone_Base',(.67,.61,.50),.95,0,1,.1),('Stone_Rough',(.69,.62,.50),.95,0,1,.15),
 ('Red_Gallery',(.68,.035,.045),.85,0,1,.12),('Hero_Wall',(.20,.15,.135),.88,0,1,.08),
 ('Light_Warm',(.98,.86,.65),.5,0,1,3),('Lettering',(.84,.78,.59),.6,.2,1,.1),
 ('Frame_White',(.81,.79,.69),.8,0,1,.2),('Frame_Black',(.025,.03,.027),.6,0,1,0),
 ('Case_Base',(.37,.37,.33),.67,0,1,.07),('Glass_Case',(.70,.82,.79),.1,0,.08,0),
 ('Bench_Wood',(.38,.23,.10),.65,0,1,0),('Paper',(.76,.69,.52),.95,0,1,.15),
 ('Ceramic_Arms',(.78,.78,.72),.7,0,1,.12),('Brass',(.53,.38,.15),.4,.7,1,0),
 ('Exit_Green',(.02,.34,.08),.55,0,1,.5)]:s.mat(name,col,rough,metal,alpha,em)
for i in range(6):s.mat('Stone_'+str(i),(.64+i*.009,.58+i*.008,.47+i*.007),.96,emission=.11)
for i in range(5):s.mat('Floor_Stone_'+str(i),(.235+i*.008,.24+i*.008,.225+i*.008),.63)

whole=sec(33,45,A0,A1);lower=sec(36.8,45,70,97);upper=whole.difference(lower)
s.add('Passage_And_Gallery_Floor',polygon_plate(upper,F),'Floor_Base','2081-2087,2128-2143',collision=True)
s.add('Kastel_Lower_Floor',polygon_plate(lower,LOW),'Floor_Base','2088-2127',collision=True)
for label,poly,z in [('Upper',upper,F),('Kastel',lower,LOW)]:
    xmin,ymin,xmax,ymax=poly.bounds
    for row,y in enumerate(np.arange(ymin,ymax,.70)):
        for col,x in enumerate(np.arange(xmin-.5,xmax,.98)):
            x+=.49*(row%2);cell=rect(x+.003,y+.003,x+.977,y+.697).intersection(poly)
            for p in polygon_parts(cell):
                if p.area>1e-5:s.batch(label+'_Paving',polygon_plate(p,z+.003),'Floor_Stone_'+str((row+3*col)%5),'2084,2095,2128')
ring('Inner_Portrait_Wall',32.78,33,A0,A1,F,F+H,'Hero_Wall','2081-2084',True)
for a,b,mat,z in [(62,70,'Wall_Gray',F),(70,97,'Stone_Base',LOW),(97,105,'Wall_Gray',F)]:ring('Outer_Wall_'+str(a),45,45.2,a,b,z,F+H,mat,'2085-2143',True)
s.add('Upper_Structural_Ceiling',polygon_plate(whole,F+H,False),'Ceiling','2081-2143')

def curved_source(name,n,r,a,b,z0,h,quad):
    Huv=cv2.getPerspectiveTransform(np.float32([[0,0],[1,0],[1,1],[0,1]]),np.float32(quad));m=Mesh();nx=80;ny=10
    for j in range(ny):
        for i in range(nx):
            st=[(i/nx,(j+1)/ny),((i+1)/nx,(j+1)/ny),((i+1)/nx,j/ny),(i/nx,j/ny)];v=[];uv=[]
            for u,t in st:
                p=xy(r,a+(b-a)*u);v.append([*p,z0+(1-t)*h]);q=Huv@np.array([u,t,1]);q/=q[2];uv.append([float(q[0]),float(1-q[1])])
            m.append(v,[[0,1,2,3]],[uv])
    s.add(name,m,photo(n),str(n),'original mural image projected to a curved wall; hidden or unreadable names not generated')
curved_source('Original_Hero_Portrait_Mural',2081,33.035,62.5,80.5,F+.65,2.22,[(.002,.345),(.590,.455),(.591,.634),(.002,.773)])
curved_source('Original_Hero_Name_List',2084,33.038,80.7,97.0,F+.60,2.36,[(.177,.350),(.381,.447),(.367,.668),(.172,.803)])
for a in np.arange(62.3,98,.42):
    p=xy(34.85,a);s.batch('Passage_Timber_Slats',box((*p,F+3.07),(3.7,.075,.13),math.radians(a)),'Slat_Wood','2081-2087')
for a in np.arange(64,99,4):
    p=xy(35,a);s.batch('Passage_Spot_Housings',cylinder((*p,F+2.98),(*p,F+2.80),.065,segments=16),'Black','2081-2084');s.batch('Passage_Spot_Lenses',cylinder((*p,F+2.79),(*p,F+2.80),.05,segments=16),'Light_Warm','2081-2084');s.lights.append({'position':list(xyz(35,a,F+2.78)),'energy':55,'angle':105})

# Red memorial room: open rectangular doorway, continuous walls and source displays.
redcenter=66.5;redlen=36.8*math.radians(7);redpoly=rect(-redlen/2,F,redlen/2,F+3.4).difference(rect(-.95,F-.01,.95,F+2.75))
s.add('Red_Room_Door_Wall',extrude_xz(redpoly,.20).transformed(xyz(36.8,redcenter,0),math.radians(redcenter)-math.pi/2),'Red_Gallery','2083-2086',collision=True)
for a in [63,70]:linewall('Red_Room_Side_'+str(a),xy(36.8,a),xy(45,a),F,F+3.4,.18,'Red_Gallery','2085-2086')
ring('Red_Room_Back',44.88,45,63,70,F,F+3.4,'Red_Gallery','2085-2086')
redfloor=sec(36.8,45,63,70);s.add('Red_Room_Ceiling',polygon_plate(redfloor,F+3.4,False),'Red_Gallery','2085-2086')
def framed_local(name,n,w,h,position,yaw,quad,backlit=False):
    s.add(name,projected_panel(w,h,quad).transformed(position,yaw),photo(n),str(n),'original exhibit pixels; source glare and resolution limits retained')
    s.add(name+'_Frame',box((0,.045,h/2),(w+.065,.07,h+.065)).transformed(position,yaw),'Frame_White' if backlit else 'Frame_Black',str(n))
    if backlit:
        for x in [-w/2-.035,w/2+.035]:s.add(name+'_Halo_'+str(x),box((x,.02,h/2),(.025,.025,h+.07)).transformed(position,yaw),'Light_Warm',str(n))
        for z in [-.035,h+.035]:s.add(name+'_Halo_'+str(z),box((0,.02,z),(w+.09,.025,.025)).transformed(position,yaw),'Light_Warm',str(n))
for a,quad,yawadd in [(63.15,[(.025,.25),(.378,.372),(.378,.554),(.025,.732)],math.pi),(69.85,[(.625,.366),(.998,.213),(.998,.712),(.625,.550)],0)]:
    p=xy(40.8,a);framed_local('Red_Room_Original_Display_'+str(a),2085,6.0,1.50,(*p,F+1.02),math.radians(a)+yawadd,quad)
framed_local('Red_Room_End_Display',2085,2.0,1.5,xyz(44.75,66.5,F+1.0),math.radians(66.5)-math.pi/2,[(.380,.366),(.619,.367),(.620,.560),(.379,.558)])
for a in [65,68]:s.lights.append({'position':list(xyz(41,a,F+3.1)),'energy':75,'color':[1,.88,.78]})

# Three visible pointed openings into the lower stone hall.
for i,(a,b,opening_width) in enumerate([(70,78,1.8),(78,86,2.6),(86,97,1.8)]):
    angle=(a+b)/2;p=xyz(36.9,angle,0);length=2*36.9*math.tan(math.radians((b-a)/2));door=pointed_arch(opening_width,F+1.30 if i==1 else F+1.35,1.15 if i==1 else 1.10,LOW-.02)
    masonry_portal(s,'Kastel_Entrance_'+str(i),length,LOW,F+3.42-LOW,.48,p,math.radians(angle)-math.pi/2,door,'2087-2095')
    # Local x runs across the opening; local y enters the hall radially outward.
    origin=xyz(36.70,angle,0);yaw=math.radians(angle)-math.pi/2
    landing=box((0,.10,(LOW-.10+F)/2),(opening_width-.05,.36,F-LOW+.10))
    s.add('Kastel_Entry_Landing_'+str(i),landing.transformed(origin,yaw),'Floor_Stone_2','2088,2092',collision=True)
    width=1.10 if i==1 else 1.64;xcentre=.68 if i==1 else 0;run=1.9;count=5
    for k in range(count):
        top=F-(k+1)*(F-LOW)/count;y=.28+(k+.5)*run/count
        step=box((xcentre,y,(LOW-.10+top)/2),(width,run/count+.005,top-LOW+.10));s.add(f'Kastel_Stair_{i}_{k}',step.transformed(origin,yaw),'Floor_Stone_2','2088,2092')
    ramp=quad_ramp(xcentre-width/2,xcentre+width/2,.28,.28+run,F,LOW)
    s.add('NAV_Kastel_Stair_'+str(i),ramp.transformed(origin,yaw),'Floor_Base','smooth walking helper over the photographed stair form',collision=True,hidden=True)
    if i==1:
        r=quad_ramp(-1.23,-.13,.28,3.6,F,LOW);s.add('Kastel_Visible_Access_Ramp',r.transformed(origin,yaw),'Floor_Stone_3','2092,2117-2125',collision=True)
        rail=join(cylinder((0,.18,F+.90),(0,3.6,LOW+.90),.025,segments=12),cylinder((0,.18,F),(0,.18,F+.90),.025,segments=12),cylinder((0,3.6,LOW),(0,3.6,LOW+.90),.025,segments=12))
        s.add('Kastel_Ramp_Handrail',rail.transformed(origin,yaw),'Black','2092,2117-2125',collision=True)
    for x in [-opening_width/2+.035,opening_width/2-.035]:
        sill=box((x,.23,(LOW+F)/2),(.06,.2,F-LOW));s.add('Stair_Edge_'+str(i)+'_'+str(x),sill.transformed(origin,yaw),'Stone_Base','2088')

# The interior alcoves share a low, rough ceiling and are entered through real holes.
for i,(a,b) in enumerate([(70,78),(78,84),(84,90),(90,97)]):
    angle=(a+b)/2;p=xyz(42.2,angle,0);length=2*42.2*math.tan(math.radians((b-a)/2));door=pointed_arch(1.65,LOW+1.55,1.10,LOW-.02)
    masonry_portal(s,'Kastel_Alcove_Opening_'+str(i),length,LOW,3.38,.32,p,math.radians(angle)-math.pi/2,door,'2092-2127')
for a in [78,84,90]:
    p=(xy(42.1,a)+xy(45,a))/2;masonry_portal(s,'Kastel_Alcove_Partition_'+str(a),2.9,LOW,3.3,.28,(*p,0),math.radians(a),None,'2095-2121')
# Close the two ends of the lowered hall; there is no open void under the adjacent upper floor.
for a,offset in [(70,.16),(97,-.06)]:
    tangent=np.array([-math.sin(math.radians(a)),math.cos(math.radians(a))]);p=(xy(36.8,a)+xy(45,a))/2+tangent*offset
    masonry_portal(s,'Kastel_End_Wall_'+str(a),8.2,LOW,F+3.42-LOW,.20,(*p,0),math.radians(a),None,'2088-2127; connecting topology remains estimated')
# The exterior-facing inside stone surface is rough, as photographed, not a fantasy vault.
for a,b in [(70,76.75),(76.75,83.5),(83.5,90.25),(90.25,97)]:
    mid=(a+b)/2;length=2*44.9*math.tan(math.radians((b-a)/2));mesh=rough_surface(length,3.30,xyz(44.87,mid,LOW),math.radians(mid)-math.pi/2,seed=int(a),amplitude=.045)
    s.add('Kastel_Rough_Back_'+str(a),mesh,'Stone_Rough','2096-2127',smooth=True)
ceil=Mesh();xmin,ymin,xmax,ymax=lower.bounds
for y in np.arange(ymin,ymax,.42):
    for x in np.arange(xmin,xmax,.42):
        cell=rect(x,y,x+.42,y+.42).intersection(lower)
        for p in polygon_parts(cell):
            for tri in constrained_delaunay_triangles(p).geoms:
                pts=list(tri.exterior.coords)[:-1]
                if tri.exterior.is_ccw:pts.reverse()
                v=[[px,py,LOW+3.31+.07*math.sin(px*2.3+py*1.1)+.035*math.sin(px*6.7-py*3.9)] for px,py in pts];ceil.append(v,[[0,1,2]])
s.add('Kastel_Rough_Ceiling',ceil,'Stone_Rough','2088-2127',smooth=True)
for r in [37.25,41.95,44.82]:ring('Kastel_Base_Lighting_'+str(r),r-.025,r+.025,70,97,LOW+.055,LOW+.080,'Light_Warm','2088-2127')
for a in [73.5,81,87,93.5]:
    s.lights.append({'position':list(xyz(40.1,a,LOW+2.90)),'energy':80,'color':[1,.88,.68],'angle':125})
    s.lights.append({'position':list(xyz(43.7,a,LOW+2.85)),'energy':48,'color':[1,.90,.75],'angle':115})
for a in [73,80,87,94]:
    p=xy(40.7,a);s.batch('Kastel_Vent_Slots',box((*p,LOW+3.15),(.17,.75,.03),math.radians(a)),'Black','2102-2127')

stone_panels=[(2096,72.1), (2097,75.7),(2102,79.0),(2103,82.6),(2107,85.0),(2108,88.5),(2114,91.3),(2115,94.5)]
panel_quads={
 2096:[(.275,.312),(.693,.267),(.690,.714),(.282,.748)],2097:[(.233,.279),(.720,.322),(.707,.735),(.233,.729)],
 2102:[(.342,.334),(.661,.294),(.669,.753),(.345,.711)],2103:[(.337,.296),(.656,.325),(.663,.714),(.339,.728)],
 2107:[(.367,.279),(.678,.302),(.688,.758),(.361,.756)],2108:[(.304,.304),(.634,.263),(.638,.752),(.305,.790)],
 2114:[(.378,.361),(.679,.354),(.687,.824),(.381,.818)],2115:[(.374,.288),(.682,.294),(.690,.726),(.375,.729)]}
for n,a in stone_panels:
    framed_local('Kastel_Original_Panel_'+str(n),n,1.02,1.44,xyz(44.68,a,LOW+.85),math.radians(a)-math.pi/2,panel_quads[n],True)
for a in [75,82,88,94]:
    p=xy(44.35,a);yaw=math.radians(a)-math.pi/2;s.add('Kastel_Bench_'+str(a),join(box((0,0,.41),(1.6,.35,.10)),box((-.62,0,.20),(.16,.30,.40)),box((.62,0,.20),(.16,.30,.40))).transformed((*p,LOW),yaw),'Bench_Wood','2115',collision=True)

# Correspondence room: cast forearms on the wall, document cases and reading kiosk.
for row in range(2):
    for i,a in enumerate(np.linspace(97.5,104.4,8)):
        local=Mesh();z=F+1.14+row*.77
        for sign in [-1,1]:
            local.append(*old.mesh_args(cylinder((sign*.095,0,.38),(sign*.015,-.04,.07),.035,.025,16)))
            local.append(*old.mesh_args(sphere((sign*.095,0,.38),(.038,.032,.05),16,8)))
            local.append(*old.mesh_args(sphere((sign*.015,-.04,.055),(.035,.025,.045),16,8)))
            for j in range(4):local.append(*old.mesh_args(cylinder((sign*.012+(.012*j-.018),-.06,.060),(-sign*.020+(.012*j-.018),-.062,.018),.006,segments=8)))
        s.batch('Wall_Cast_Hands',local.transformed(xyz(33.12,a,z),math.radians(a)+math.pi/2),'Ceramic_Arms','2128,2131,2135-2137',smooth=True)

def cabinet(name,r,a,w=1.35,d=.85,h=2.70):
    p=xy(r,a);yaw=math.radians(a)-math.pi/2
    def add(tag,mesh,mat,collision=False):s.add(name+'_'+tag,mesh.transformed((*p,F),yaw),mat,'2130-2140',collision=collision)
    add('Plinth',box((0,0,.14),(w,d,.28)),'Case_Base',True);add('Canopy',box((0,0,h-.13),(w,d,.26)),'Case_Base')
    for x in [-w/2,w/2]:add('Side_'+str(x),box((x,0,h/2),(.012,d,h-.5)),'Glass_Case',True)
    for y in [-d/2,d/2]:add('Pane_'+str(y),box((0,y,h/2),(w,.012,h-.5)),'Glass_Case',True)
    add('Display_Block',box((0,0,.68),(w-.18,d-.17,.82)),'Paper',True)
    s.lights.append({'position':list(xyz(r,a,F+h-.31)),'energy':40,'angle':80})
    return p,yaw

p,yaw=cabinet('Typewriter_And_Papers',43.8,98.3)
typewriter=join(box((0,-.02,1.20),(.64,.44,.10)),box((0,.115,1.36),(.62,.18,.28)),cylinder((-.34,.21,1.51),(.34,.21,1.51),.045,segments=20))
s.add('Historical_Typewriter_Body',typewriter.transformed((*p,F),yaw),'Black','2132-2134')
keys=Mesh()
for row in range(4):
    for col in range(11):
        x=(col-5)*.047;y=-.18+row*.061;z=1.263+row*.019;keys.append(*old.mesh_args(cylinder((x,y,z),(x,y,z+.013),.016,segments=12)))
s.add('Typewriter_Keys',keys.transformed((*p,F),yaw),'Frame_White','2132')
rng=np.random.default_rng(2132)
for j,x in enumerate([-.47,.43]):
    for k in range(45 if j==0 else 22):s.batch('Stacked_Correspondence',box((x,float(rng.uniform(-.02,.02)),1.11+k*.018),(.25,.31,.016),float(rng.uniform(-.03,.03))).transformed((*p,F),yaw),'Paper','2132-2133')
paper=panel(.36,.38).transformed((0,.22,1.51));s.add('Typewriter_Paper',paper.transformed((*p,F),yaw),'Paper','2132')
p,yaw=cabinet('Hanging_Original_Manuscript',43.8,103.8)
framed_local('Original_Large_Manuscript',2140,.66,1.04,(*p,F+1.27),yaw,[(.288,.207),(.684,.204),(.712,.721),(.298,.744)])

framed_local('Original_Correspondence_Document_Wall',2141,2.28,1.29,xyz(44.75,101.1,F+1.35),math.radians(101.1)-math.pi/2,[(.071,.259),(.946,.231),(.957,.535),(.080,.558)])
k=xy(42.2,101.1);kyaw=math.radians(101.1)-math.pi/2
s.add('Reading_Kiosk_Stand',join(box((0,0,.45),(.30,.30,.90)),box((0,0,.06),(.58,.52,.12))).transformed((*k,F),kyaw),'Black','2129,2141-2143',collision=True)
screen=projected_panel(.87,.52,[(.070,.180),(.922,.230),(.922,.784),(.061,.762)]);v=np.asarray(screen.vertices);z=v[:,2].copy();v[:,1]=z*.74-.18;v[:,2]=z*.67+1.02;screen.vertices=v.tolist();s.add('Reading_Kiosk_Original_Page',screen.transformed((*k,F),kyaw),photo(2142),'2142-2143','original reading display image; not an invented transcription')
for a in [98.3,101.2,104.2]:
    s.lights.append({'position':list(xyz(39.3,a,F+3.15)),'energy':75,'angle':125})
    p=xy(38.5,a);cube('Ceiling_Projector_'+str(a),(*p,F+3.15),(.42,.34,.18),'Frame_White','2128,2135',math.radians(a))
    s.batch('Ceiling_Projector_Lenses',cylinder((p[0],p[1]-.19,F+3.15),(p[0],p[1]-.21,F+3.15),.052,segments=20),'Black','2128')

linewall('REVIEW_Part05_Boundary',xy(33,105),xy(45,105),F,F+H,.10,'Ceiling','review helper, removed when part05 is loaded')
s.objects[-1].update(review_only=True,temporary_until='part05')
def view(id,title,r,a,tr,ta,tz,photo,z=F+1.65):return {'id':id,'title':title,'position':list(xyz(r,a,z)),'target':list(xyz(tr,ta,tz)),'photo':photo}
s.views=[view('portraits','ممر الصور والأسماء',34.8,64,34.6,77,F+1.5,2081),view('redroom','الغرفة الحمراء',40.3,66.5,44.8,66.5,F+1.6,2085),view('stoneportals','الأقواس الحجرية',34.9,76,36.9,82,F+1.4,2087),view('kastelstairs','النزول إلى الكستل',36.2,74,40.2,74,LOW+.9,2088),view('kastel','القاعة الحجرية من الداخل',40.0,76,42.2,87,LOW+1.3,2095,z=LOW+1.65),view('ramp','الدرج والمنحدر والدرابزين',40.9,83.6,37,82,F+.6,2092,z=LOW+1.65),view('stonepanels','لوحات القاعات الحجرية',43.3,81,44.7,80.5,LOW+1.55,2102,z=LOW+1.65),view('hands','مجسمات الأيدي والمراسلات',36,101,33.1,101,F+1.7,2128),view('typewriter','الآلة الكاتبة والوثائق',41.8,98.3,43.8,98.3,F+1.4,2132),view('kiosk','الوثائق وشاشة القراءة',40.3,101.1,44.5,101.1,F+1.6,2141)]
s.save(ROOT/'reconstruction/part04-scene.json')
(ROOT/'reconstruction/part04-notes.json').write_text(json.dumps({'title':'ممر الصور والكستل والمراسلات','source_photos':'2081-2143','capture_date':'2026-10-21','stage':'draft for integrated review','observed':['Portrait and name mural','Timber slat ceiling','Red memorial room','Pointed stone portals','Steps and ramp/handrail','Rough stone ceiling and backlit panels','Cast forearms/hands, not birds','Typewriter, stacked correspondence, hanging manuscript and reading kiosk'],'unverified':['Exact room dimensions and topology beyond photographed connections','Fine manuscript and portrait-name legibility','Detailed typewriter and cast-hand surface geometry'],'accuracy_100_percent':False},ensure_ascii=False,indent=2))
