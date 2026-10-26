"""PT8 interior components observed in Gaziulaş official photos7–9.
Seat spacing and concealed geometry remain provisional without a measured seating plan.
No image generation: fabric UVs reference the actual published upholstery photograph.
"""
from museum_geometry import *
from museum_architecture import extrude_xz
from shapely.geometry import box as rect

def build_pt8_interior(scene,origin,yaw,floor=.95):
 refs='Gaziulas tramvay-genel-7,8,9; official photo capture date unconfirmed'
 mats=[('PT8_Off_White',(.81,.82,.77),.50,0,1,0),('PT8_Rubber_Grey',(.32,.35,.34),.91,0,1,0),('PT8_Grab_Orange',(.94,.28,.055),.44,0,1,0),('PT8_Shell_Red',(.62,.055,.05),.54,0,1,0),('PT8_Grip_Black',(.045,.05,.052),.79,0,1,0),('PT8_Frame_Metal',(.62,.64,.60),.38,.60,1,0),('PT8_Console',(.20,.23,.22),.69,0,1,0),('PT8_Light',(.99,.97,.84),.35,0,1,2),('PT8_LED',(.40,.025,.015),.4,0,1,.35),('PT8_Window',(.29,.38,.39),.12,.15,.18,0),('PT8_Button_Red',(.7,.025,.02),.4,0,1,.1),('PT8_Button_Green',(.02,.45,.25),.4,0,1,.1)]
 for n,c,r,m,a,e in mats:scene.mat(n,c,r,m,a,e)
 scene.mat('PT8_Articulation_Aluminium',(.72,.74,.73),.23,.82)
 scene.mat('PT8_Original_Fabric',(1,1,1),.9,image='textures/PT8_Official_Fabric.jpg')
 def put(name,mesh,material,collision=False,smooth=False,basis='visible reference feature, dimensions estimated'):
  scene.add('PT8_Interior_'+name,mesh.transformed(origin,yaw),material,refs,basis,collision=collision,smooth=smooth)
 def batch(name,mesh,material,smooth=False,collision=False):scene.batch('PT8_Interior_'+name,mesh.transformed(origin,yaw),material,refs,smooth=smooth,collision=collision)
 def fabric(mesh,axes):
  # One coherent source-photo projection over each complete upholstery surface.
  vs=np.asarray(mesh.vertices);lo=vs[:,axes].min(axis=0);span=np.maximum(np.ptp(vs[:,axes],axis=0),1e-6)
  for fi,face in enumerate(mesh.faces):
   uv=(vs[face][:,axes]-lo)/span
   mesh.uv[fi]=[[.770+.225*u,1-(.785+.210*v)] for u,v in uv]
  return mesh
 # Curved seat backs, cushioned seats, red shell edges and grey support pedestals.
 positions=[]
 rows=[-12.,-9.45,-8.55,-7.65,-6.75,-5.85,-1.50,-.50,.50,1.50,5.85,6.75,7.65,8.55,9.45,12.]
 for x in rows:
  for y in [-.875,-.435,.875]:positions.append((x,y,0 if x<0 else math.pi))
 positions.extend([(-4.90,.875,0),(4.90,.875,math.pi)])
 for idx,(x,y,angle) in enumerate(positions):
  # rounded cross section for the backrest, extruded and leaned toward its rear
  profile=rect(-.225,.02,.225,.63).buffer(.035,quad_segs=5).buffer(-.012,quad_segs=5)
  back=extrude_xz(profile,.075);vv=np.array(back.vertices);vv[:,[0,1]]=vv[:,[1,0]];vv[:,0]=vv[:,0]-.235-vv[:,2]*.10;vv[:,2]+=floor+.43;back.vertices=vv.tolist();back.faces=[list(reversed(f)) for f in back.faces]
  cushion=fabric(box((.02,0,floor+.43),(.50,.445,.10),bevel=.06),(0,1));back=fabric(back,(1,2))
  local=(x,y,0);batch('Seat_Upholstery',join(back,cushion).transformed(local,angle),'PT8_Original_Fabric',True)
  shell=box((-.275,0,floor+.77),(.035,.46,.65),bevel=.03);batch('Seat_Red_Shell_Edges',shell.transformed(local,angle),'PT8_Shell_Red')
  pedestal=join(box((0,0,floor+.21),(.30,.34,.42)),box((0,0,floor+.016),(.42,.40,.032)))
  batch('Seat_Pedestals',pedestal.transformed(local,angle),'PT8_Frame_Metal')
  put('NAV_Seat_%02d'%idx,box((x,y,floor+.53),(.66,.49,1.06)),'PT8_Grip_Black',True,basis='simplified collision envelope around the visible seat');scene.objects[-1]['hidden']=True
 # White vertical stanchions and orange overhead rails along the windows.
 for yy in [-.72,.72]:
  for x0,x1 in [(-12.65,-5.1),(-4.1,4.1),(5.1,12.65)]:batch('Orange_Overhead_Rails',cylinder((x0,yy,2.78),(x1,yy,2.78),.022,segments=12),'PT8_Grab_Orange',True)
 for x in [-11.43,-9.93,-5.65,-3.73,-2.27,2.27,3.73,5.65,9.93,11.43]:
  for y in [-.72,.72]:
   batch('White_Stanchions',cylinder((x,y,floor),(x,y,2.96),.020,segments=12),'PT8_Off_White',True,True)
   batch('Stanchion_Collars',cylinder((x,y,2.72),(x,y,2.84),.033,segments=12),'PT8_Off_White',True)
 # Hanging black loop grips, grouped in fours as visible in the current official photographs.
 for x in [-11.2,-8.0,-5.4,-2.3,2.3,5.4,8.0,11.2]:
  for yy in [-.72,.72]:
   for dx in [-.060,-.020,.020,.060]:
    xx=x+dx;strap=box((xx,yy,2.65),(.018,.015,.27));batch('Hanging_Straps',strap,'PT8_Off_White')
    # Elliptical loop in a Y/Z plane, closed actual mesh.
    pts=[(xx,yy+.061*math.cos(a),2.45+.067*math.sin(a)) for a in np.linspace(0,math.pi,25)]+[(xx,yy-.052,2.438),(xx,yy+.052,2.438),(xx,yy+.061,2.45)];m=Mesh()
    for a,b in zip(pts,pts[1:]):m.append(*old.mesh_args(cylinder(a,b,.009,segments=8)))
    batch('Black_Hand_Loops',m,'PT8_Grip_Black',True)
 # Grey rubber floor, actual flush articulation disk seams and service hatches.
 for x0,x1 in [(-12.88,-5.03),(-4.12,4.12),(5.03,12.88)]:
  pp=rect(x0,-1.10,x1,1.10)
  if x0>0:pp=pp.difference(rect(10.05,-1.11,11.35,-.40))
  from museum_architecture import polygon_parts
  for p in polygon_parts(pp):batch('Rubber_Floor',polygon_plate(p,floor+.002),'PT8_Rubber_Grey')
 for x in [-4.575,4.575]:
  from shapely.geometry import Point
  disk=Point(x,0).buffer(1.045,quad_segs=40).intersection(rect(x-.423,-1.08,x+.423,1.08))
  batch('Articulation_Floor_Plate',polygon_plate(disk,floor+.004),'PT8_Rubber_Grey')
  for a,b in zip(np.linspace(-math.pi/2,math.pi/2,48),np.linspace(-math.pi/2,math.pi/2,48)[1:]):
   for sign in [-1,1]:
    pa=(x+sign*.40*math.cos(a),1.03*math.sin(a),floor+.008);pb=(x+sign*.40*math.cos(b),1.03*math.sin(b),floor+.008);batch('Articulation_Floor_Seams',cylinder(pa,pb,.006,segments=6),'PT8_Frame_Metal')
 for x in [-8,0,8]:
  for yy in [-.28,.42]:batch('Floor_Service_Hatch_Lines',cylinder((x-.50,yy,floor+.008),(x+.50,yy,floor+.008),.006,segments=6),'PT8_Frame_Metal')
  for xx in [x-.50,x+.50]:batch('Floor_Service_Hatch_Lines',cylinder((xx,-.28,floor+.008),(xx,.42,floor+.008),.006,segments=6),'PT8_Frame_Metal')
 # Articulation surrounds: broad rounded opening with a high clear centre.
 for x in [-4.99,-4.16,4.16,4.99]:
  outer=rect(-1.115,floor,1.115,2.98);hole=rect(-.85,floor-.05,.85,2.68).union(rect(-.64,2.64,.64,2.94)).buffer(.12,quad_segs=12).buffer(-.12,quad_segs=12)
  arch=extrude_xz(outer.difference(hole),.075);vv=np.array(arch.vertices);vv[:,[0,1]]=vv[:,[1,0]];vv[:,0]+=x;arch.vertices=vv.tolist();arch.faces=[list(reversed(f)) for f in arch.faces]
  put('Articulation_Surround_'+str(x),arch,'PT8_Articulation_Aluminium',True)
 for x in [-5.10,5.10]:
  put('LED_Housing_'+str(x),box((x,0,2.91),(.11,1.35,.17)),'PT8_Console')
  for face in [-1,1]:put('LED_Face_%s_%s'%(x,face),box((x+face*.058,0,2.91),(.008,1.22,.105)),'PT8_LED')
 # Ceiling light strips, panel joints, round ventilation grilles.
 for x0,x1 in [(-12.6,-5.15),(-4.0,4.0),(5.15,12.6)]:
  for yy in [-.53,.53]:
   batch('Ceiling_Light_Frame',box(((x0+x1)/2,yy,2.965),(x1-x0,.21,.032)),'PT8_Off_White');batch('Ceiling_Light_Strips',box(((x0+x1)/2,yy,2.943),(x1-x0-.15,.145,.014)),'PT8_Light')
 for x in np.arange(-12,12.1,1.65):
  batch('Ceiling_Panel_Joints',box((x,0,2.972),(.012,2.04,.010)),'PT8_Frame_Metal')
  batch('Ceiling_Vent_Rims',torus((x,0,2.963),.095,.010,(0,0,1),24,6),'PT8_Frame_Metal')
  for a in np.linspace(0,math.pi,4)[:-1]:batch('Vent_Grille_Bars',box((x,0,2.957),(.17,.010,.008),a),'PT8_Console')
 # Door edge reader and emergency pull boxes match the hardware seen in photographs.
 for x in [-10.7,-3,3,10.7]:
  for side in [-1,1]:
   xx=x+.72;yy=side*.82
   for a,b in [((xx,yy,floor+.25),(xx,yy,1.55)),((xx,yy,1.55),(xx,yy+side*.18,1.85)),((xx,yy+side*.18,1.85),(xx,yy+side*.18,2.70))]:batch('Door_Orange_Grab_Rails',cylinder(a,b,.023,segments=12),'PT8_Grab_Orange',True)
   put('Card_Reader_%s_%s'%(x,side),box((xx,yy,1.92),(.075,.13,.26),bevel=.025),'PT8_Off_White')
   put('Card_Reader_Display_%s_%s'%(x,side),box((xx-.041,yy,1.95),(.008,.105,.16)),'PT8_Console')
   put('Card_Reader_Button_%s_%s'%(x,side),cylinder((xx-.043,yy,1.84),(xx-.050,yy,1.84),.023,segments=16),'PT8_Grip_Black')
   put('Emergency_Box_%s_%s'%(x,side),box((x,side*1.02,2.83),(.12,.045,.19)),'PT8_Button_Red')
 # Glazed cab partitions and controls, based on official cab photo5. Controls are visual only.
 for sign in [-1,1]:
  x=sign*12.95
  put('Cab_Lower_Partition_'+str(sign),box((x,0,1.18),(.065,2.12,.46)),'PT8_Off_White',True)
  put('Cab_Glazing_'+str(sign),box((x,0,2.13),(.024,2.06,1.43)),'PT8_Window',True)
  for yy in [-1.03,-.43,.43,1.03]:put('Cab_Window_Frame_%s_%s'%(sign,yy),box((x,yy,2.13),(.075,.035,1.49)),'PT8_Off_White')
  console=box((sign*13.62,0,1.28),(.62,1.88,.35),bevel=.08);put('Driver_Console_'+str(sign),console,'PT8_Console')
  for k in range(12):
   yy=-.80+k*.145;put('Console_Switch_%s_%s'%(sign,k),cylinder((sign*13.46,yy,1.46),(sign*13.46,yy,1.48),.028,segments=12),'PT8_Button_Red' if k%3==0 else 'PT8_Button_Green')
  for yy in [-.49,.45]:put('Driver_Display_%s_%s'%(sign,yy),box((sign*13.70,yy,1.52),(.20,.30,.03)),'PT8_Grip_Black')
  put('Driver_Seat_'+str(sign),join(box((sign*13.12,0,1.16),(.48,.50,.12),bevel=.05),box((sign*13.03,0,1.53),(.10,.50,.68),bevel=.04)),'PT8_Grip_Black')
 return {'reference_sources':['https://gaziulas.com.tr/hizmetler/tramvay-tarihce','https://gaziulas.com.tr/images/album/gaziulas-tramvay-genel-7.jpg','https://gaziulas.com.tr/images/album/gaziulas-tramvay-genel-8.jpg','https://gaziulas.com.tr/images/album/gaziulas-tramvay-genel-9.jpg'],'nominal_seat_count':len(positions),'seat_count_basis':'official PT8 capacity50; row spacing and complete seating diagram not yet verified','observed_features':['black/red/orange patterned upholstery','white poles and orange rails','black hanging loops','grey rubber floor and articulation floor seams','silver articulation surrounds','upper side-window dividers','glazed cab partition','reader at doors','long ceiling lights and round grilles'],'confidence':'photo-supported features; unmeasured placement and current-day condition unverified'}
