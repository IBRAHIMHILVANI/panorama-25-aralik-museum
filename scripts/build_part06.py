"""Three observed dioramas and projection transition, source photos 2189–2213."""
from museum_geometry import *
from museum_architecture import *
from museum_exhibits import photo_material,projected_panel,emit_reference_prop
from museum_diorama_props import *
from shapely.geometry import Polygon,LineString,box as rect
s=Scene('06_Three_Dioramas');C=np.array([-6.,23.5]);F=-4.2;A0=140.;A1=168.
def xy(r,a):a=math.radians(a);return C+r*np.array([math.cos(a),math.sin(a)])
def xyz(r,a,z):return (*xy(r,a),z)
def ri(a):return 37-4*min(1,max(0,(a-140)/3))
def cube(name,pos,d,mat,refs='',yaw=0,collision=False):s.add(name,box(pos,d,yaw),mat,refs,collision=collision)
def sector(a,b,r0=33,r1=45):return Polygon([xy(r1,t) for t in np.linspace(a,b,90)]+[xy(r0,t) for t in np.linspace(b,a,90)])
for name,col,rough,metal,alpha,em in [('Floor',(.25,.26,.245),.7,0,1,0),('Wall',(.46,.465,.43),.86,0,1,.05),('Ceiling',(.055,.060,.057),.95,0,1,0),('Steel',(.11,.12,.115),.56,.6,1,0),('Rail_Wood',(.26,.13,.066),.55,0,1,0),('Glass',(.72,.80,.78),.13,0,.07,0),('Light',(.96,.87,.69),.5,0,1,3),('Lettering',(.85,.82,.72),.8,0,1,.1)]:s.mat(name,col,rough,metal,alpha,em)
scenic_materials(s)
floor=Polygon([xy(45,a) for a in np.linspace(A0,A1,120)]+[xy(ri(a),a) for a in np.linspace(A1,A0,120)])
s.add('Diorama_Gallery_Floor',polygon_plate(floor,F),'Floor','2189-2213',collision=True)
s.add('Diorama_Gallery_Ceiling',polygon_plate(floor,F+3.85,False),'Ceiling','2189-2213')
s.add('Diorama_Outer_Wall',arc_band(C,45,45.25,math.radians(A0),math.radians(A1),F,F+3.85,100),'Wall','2189-2213',collision=True)
for i,(a,b) in enumerate(zip(np.linspace(A0,A1,80),np.linspace(A0,A1,80)[1:])):
 p,q=xy(ri(a),a),xy(ri(b),b);mid=(p+q)/2;cube('Diorama_Inner_Wall_'+str(i),(*mid,F+1.925),(np.linalg.norm(q-p)+.012,.14,3.85),'Wall','2192,2207',math.atan2(*(q-p)[::-1]),True)
# Permanent basement end enclosure, replacing the temporary full-width review
# boundary once part07 is present. The existing oblique passage stays open.
enclosure_refs='IMG_2189,2210,2211,2213: enclosed basement walls and ceiling'
enclosure_basis='Architectural closure follows existing modeled room/tunnel edges; exact portal dimensions and plan remain estimates'
portal_center=xy(37,A1);radial=np.array([math.cos(math.radians(A1)),math.sin(math.radians(A1))]);portal_half=1.65
end_profile=rect(-6.25,F,6.25,F+3.85).difference(rect(-2-portal_half,F-.02,-2+portal_half,F+2.60))
s.add('Diorama_Permanent_End_Enclosure',extrude_xz(end_profile,.20).transformed(xyz(39,A1,0),math.radians(A1)),'Wall',enclosure_refs,enclosure_basis,collision=True)
# The part07 tunnel starts obliquely at the gallery end. Close the small
# triangular flanks between its butt end and the radial gallery portal.
tunnel_next=np.array([-40.8,28.8]);direction=tunnel_next-portal_center;direction/=np.linalg.norm(direction);normal=np.array([-direction[1],direction[0]])
join_center=portal_center+direction*1.40
va=portal_center-radial*portal_half;vb=portal_center+radial*portal_half
vd=join_center+normal*1.16;vc=join_center-normal*1.16
vestibule=Polygon([va,vb,vc,vd]).buffer(0)
existing_tunnel=LineString([portal_center,tunnel_next,(-29+2.8*math.cos(math.radians(135)),16+2.8*math.sin(math.radians(135)))]).buffer(1.16,cap_style=2,join_style=2)
for suffix,p,q in [('Left',va,vd),('Right',vb,vc)]:
 mid=(p+q)/2;mesh=box((*mid,F+1.30),(np.linalg.norm(q-p),.18,2.60),math.atan2(*(q-p)[::-1]))
 s.add('Diorama_Transition_Return_'+suffix,mesh,'Wall',enclosure_refs,enclosure_basis,collision=True)
for i,pp in enumerate(polygon_parts(vestibule.difference(existing_tunnel).difference(floor))):
 s.add('Diorama_Transition_Floor_Infill_'+str(i),polygon_plate(pp,F),'Floor',enclosure_refs,enclosure_basis,collision=True)
for i,pp in enumerate(polygon_parts(vestibule.difference(existing_tunnel))):
 s.add('Diorama_Transition_Ceiling_Infill_'+str(i),polygon_plate(pp,F+2.60,False),'Ceiling',enclosure_refs,enclosure_basis,collision=True)
# Part05 ceiling is 3.70m above this floor, part06 is 3.85m. Seal the
# 0.15m clerestory-like crack at their shared edge without narrowing entry.
s.add('Diorama_Entry_Ceiling_Step_Closure',box(xyz(41,A0,F+3.775),(8.5,.20,.15),math.radians(A0)),'Ceiling',enclosure_refs,enclosure_basis,collision=True)
# The actual aisle is open; relief terrain and props lie behind continuous barriers.
for a in np.arange(140.6,168,3.2):
 p=(xy(ri(a),a)+xy(45,a))/2;cube('Ceiling_Beam_'+str(a),(*p,F+3.60),(45-ri(a),.16,.25),'Steel','2189-2213',math.radians(a))
 for r in [35.5,38.3,42.6]:
  s.batch('Diorama_Ceiling_Duct',box(xyz(r,a,F+3.43),(.36,2.25,.22),math.radians(a)),'Steel','2189-2213')
  s.batch('Diorama_Vent',torus(xyz(r,a,F+3.28),.19,.022,(0,0,1),28,6),'Steel','2189-2213')
  for t in [0,math.pi/3,2*math.pi/3]:s.batch('Diorama_Vent_Blades',box(xyz(r,a,F+3.27),(.34,.028,.01),t),'Ceiling','2189-2213')
for a in np.arange(140,168,.9):s.batch('Diorama_Paving_Joints',arc_line(C,36.2,math.radians(a),math.radians(a+.012),F+.003,.005,2),'Steel','2189-2213')
# Original paintings are used only for their background mural region.
bays=[('Community',140.3,148.0,2194,[(.012,.166),(.985,.083),(.985,.515),(.012,.510)]),('Defence',148.5,156.1,2200,[(.228,.275),(.817,.239),(.815,.605),(.228,.560)]),('Ruin',156.6,164.2,2205,[(.16,.12),(.97,.065),(.97,.416),(.20,.387)])]
for i,(name,a,b,n,quad) in enumerate(bays):
 poly=sector(a,b,38.7,44.9);terrain(s,name+'_Earthen_Terrain',poly,F+.025,n,.12)
 curved_photo(s,name+'_Original_Mural',n,C,44.85,a+.15,b-.15,F+.28,2.85,quad)
 s.add(name+'_Protective_Glass',arc_band(C,38.55,38.57,math.radians(a),math.radians(b),F+.10,F+.88,50),'Glass',str(n),collision=True)
 s.add(name+'_Timber_Handrail',arc_band(C,38.52,38.62,math.radians(a),math.radians(b),F+.91,F+1.00,50),'Rail_Wood',str(n),collision=True)
 for angle in np.linspace(a,b,6):s.batch('Diorama_Rail_Posts',cylinder(xyz(38.56,angle,F),xyz(38.56,angle,F+.94),.023,segments=10),'Steel','2189-2206')
 for angle in [a,b]:
  p=(xy(38.75,angle)+xy(45,angle))/2;cube(name+'_Side_Wall_'+str(angle),(*p,F+1.925),(6.3,.16,3.85),'Wall',str(n),math.radians(angle),True)
 s.lights.append({'position':list(xyz(42.3,(a+b)/2,F+3.53)),'target':list(xyz(41.8,(a+b)/2,F+.5)),'energy':190,'angle':105,'color':[1,.88,.67]})
 s.lights.append({'position':list(xyz(36.5,(a+b)/2,F+3.35)),'energy':45,'angle':120})
# First diorama: actual foreground is a domestic craft tableau, wagon and goat.
a=144.1;yaw=math.radians(a)-math.pi/2
loom(s,'Community_Loom',xyz(42.4,145.7,F+.14),yaw,'2193')
stool(s,'Community_Weaver_Stool',xyz(41.65,145.7,F+.14),yaw,'2193')
emit_reference_prop(s,old.person,('Weaver',(0,0,0),0,True,False,'REF_Cloth_Blue','REF_Cloth_Green','REF_Cloth_Cream','2193','work'),xyz(41.65,145.7,F+.14),yaw,'2193','Community')
emit_reference_prop(s,old.person,('Standing_Woman',(0,0,0),0,False,True,'REF_Cloth_Red','REF_Cloth_Ochre','REF_Cloth_Green','2193'),xyz(41.5,146.7,F+.14),yaw,'2193','Community')
wagon(s,'Community_Cart',xyz(41.7,141.6,F+.13),yaw+.2,False,'2196');goat(s,'Community_Goat',xyz(40.0,143.6,F+.15),yaw+.55,'2194')
for j in range(9):emit_reference_prop(s,old.pot,(f'Pot_{j}',(0,0,0),.13+.03*(j%3),.16+.04*(j%4),'REF_Pottery','2194',True),xyz(42.2+.4*(j//3),143+.35*(j%3),F+.15),0,'2194','Community')
# Second/third: objects extend into real depth, the painted fighting remains on the mural.
rubble(s,'Defence',xyz(41.9,152.3,F+.16),5.5,4.4,120,2200,math.radians(152.3)-math.pi/2,.85)
emit_reference_prop(s,old.cannon,('Gun',(0,0,0),0,'2200'),xyz(41.9,152.8,F+.30),math.radians(152.8)-math.pi/2,'2200','Defence',.79,omit=('_Shield',))
flag(s,'Defence_Flag',xyz(43.3,155.0,F+.45),math.radians(155)-math.pi/2,'2199',.60,1.30)
rubble(s,'Ruin',xyz(41.8,160.4,F+.12),5.8,4.5,155,2205,math.radians(160.4)-math.pi/2,.65)
wagon(s,'Ruin_Broken_Cart',xyz(42.4,160.6,F+.15),math.radians(160.6)-math.pi/2+.4,True,'2204-2206')
# Projection and quotation are original-source surfaces, not generated text.
for name,n,w,h,r,a,z,quad in [('Projection',2210,2.25,1.30,44.7,166.2,F+1.1,[(.14,.40),(.64,.49),(.65,.64),(.13,.65)]),('Original_Quotation',2211,3.2,1.30,33.16,164.5,F+1.1,[(.125,.298),(.954,.310),(.953,.600),(.13,.604)])]:
 yaw=math.radians(a)-math.pi/2 if r>40 else math.radians(a)+math.pi/2
 s.add(name,projected_panel(w,h,quad).transformed(xyz(r,a,z),yaw),photo_material(s,n),str(n),'original photographed display; no generated quotation')
 s.add(name+'_Frame',box((0,.04,h/2),(w+.08,.06,h+.08)).transformed(xyz(r,a,z),yaw),'Ceiling',str(n))
cube('Ceiling_Projector',xyz(40.8,166,F+3.1),(.35,.38,.17),'Wall','2210',math.radians(166));cube('Quotation_Display_Pedestal',xyz(34.0,164.5,F+.48),(1.12,.70,.96),'Ceiling','2211',math.radians(164.5),True)
s.lights.append({'position':list(xyz(35.4,165,F+3.3)),'energy':65,'angle':105})
p,q=xy(33,168),xy(45,168);s.add('REVIEW_Part07_Boundary',box((*(p+q)/2,F+1.9),(12,.10,3.8),math.radians(168)),'Ceiling','review boundary',collision=True);s.objects[-1].update(review_only=True,temporary_until='part07')
s.views=[]
for id,title,r,a,tr,ta,photo in [('dioramas','المشاهد الثلاثة',36.3,142.8,41.8,149,2189),('community','مشهد الحياة والحرف',36.5,144.1,42.6,144.3,2194),('defence','مشهد الدفاع والركام',36.2,152.3,43.5,152.3,2200),('ruin','مشهد العربة والخراب',36.2,160.4,43.3,160.4,2205),('projection','منطقة العرض والاقتباس',37,166,44.7,166.2,2210)]:s.views.append({'id':id,'title':title,'position':list(xyz(r,a,F+1.65)),'target':list(xyz(tr,ta,F+1.3)),'photo':photo})
s.save(ROOT/'reconstruction/part06-scene.json')
(ROOT/'reconstruction/part06-notes.json').write_text(json.dumps({'source_photos':'2189-2213','observed_dioramas':3,'basis':'original source sequence; estimated dimensions and figurine anatomy','accuracy_100_percent':False,'architectural_enclosure':{'evidence':'Original IMG_2189,2210,2211,2213 show enclosed basement walls and ceiling','end':'Permanent wall across existing end at168deg, with3.30m-wide and2.60m-high open portal aligned to existing part07 tunnel','transition':'Short enclosing returns and triangular floor/ceiling infills close oblique tunnel junction','entry':'0.15m ceiling height transition to part05 closed above passage','placement':'Existing model boundary retained; dimensions and metric alignment are estimates'},'limits':['No measured floor plan','All319 original photographs restored locally2026-10-26; source images are available at original resolution','Generated foreground scenery still requires comparison with original full-resolution photographs']},indent=2,ensure_ascii=False))
