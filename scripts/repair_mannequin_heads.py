"""Repair black mannequin heads dropped by image-to-3D segmentation.
Reuse the generated head geometry of the neighboring black display mannequin,
fit it within the original helmet/collar, and keep the original GLBs untouched.
"""
import bpy,bmesh,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];folder=ROOT/'reconstruction/3d-asset-candidates'
def clear():bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
def load(path):
 bpy.ops.import_scene.gltf(filepath=str(path));objects=[o for o in bpy.context.selected_objects if o.type=='MESH'];bpy.context.view_layer.update()
 pts=[o.matrix_world@Vector(c) for o in objects for c in o.bound_box];mi=Vector([min(p[i] for p in pts) for i in range(3)]);ma=Vector([max(p[i] for p in pts) for i in range(3)]);h=ma.z-mi.z;center=(mi+ma)/2;center.z=mi.z
 for o in objects:
  mat=o.matrix_world.copy()
  for v in o.data.vertices:v.co=(mat@v.co-center)*(1.84/h)
  o.matrix_world.identity()
 return objects
clear();source=load(folder/'blue_helmet_b-tripo-p2.glb')[0];bm=bmesh.new();bm.from_mesh(source.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001)
for z,clear_inner,clear_outer in [(1.555,True,False),(1.710,False,True)]:
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(0,0,z),plane_no=(0,0,1),clear_inner=clear_inner,clear_outer=clear_outer,dist=.00001)
# Arms and shoulder fragments are outside the head cross-section.
bmesh.ops.delete(bm,geom=[v for v in bm.verts if abs(v.co.y)>.115 or v.co.x<-.13 or v.co.x>.15],context='VERTS')
bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
verts=[tuple(v.co) for v in bm.verts];bm.verts.index_update();faces=[[v.index for v in f.verts] for f in bm.faces];bm.free()
report=[]
for key,z0,z1 in [('cream_left',1.530,1.705),('blue_helmet_a',1.540,1.710)]:
 clear();objects=load(folder/(key+'-tripo-p2.glb'));mesh=bpy.data.meshes.new(key+'_HeadRepair');mesh.from_pydata([(x,y,z0+(z-1.555)/(1.710-1.555)*(z1-z0)) for x,y,z in verts],[],faces);mesh.update();obj=bpy.data.objects.new('Black_Museum_Mannequin_Head_Repair',mesh);bpy.context.scene.collection.objects.link(obj)
 mat=bpy.data.materials.new('Charcoal_Mannequin');mat.use_nodes=True;bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.014,.016,.017,1);bs.inputs['Roughness'].default_value=.78;mesh.materials.append(mat)
 for p in mesh.polygons:p.use_smooth=True
 obj['basis']='Black mannequin head reconstructed from neighboring display mannequin, fitted to source helmet/collar; not a scan'
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects+[obj]:o.select_set(True)
 path=folder/(key+'-tripo-p2-repaired.glb');bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_extras=True,export_yup=True)
 report.append({'key':key,'output':str(path),'head_vertices':len(verts),'source':'blue_helmet_b generated neighboring mannequin head geometry','status':'awaiting_visual_review'})
(folder/'head-repair-report.json').write_text(json.dumps(report,indent=2))
