"""Combine reviewed parts in one native scene, visual FBX, and collision-only FBX."""
import bpy,json,math,hashlib,sys,time
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/Gaziantep-Museum-2026-10-25';files=json.loads((ROOT/'reconstruction/part-files.json').read_text());ids=['part%02d'%i for i in range(9)]
bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
provenance=[];views=[]
for part in ids:
 data=json.loads((ROOT/'reconstruction'/(part+'-scene.json')).read_text());path=OUT/(files[part]+'.blend')
 with bpy.data.libraries.load(str(path),link=False) as (src,dst):dst.collections=[data['part']]
 for coll in dst.collections:
  if coll:scene.collection.children.link(coll)
 provenance.append({'part':part,'native_source':path.name,'fbx_sha256':hashlib.sha256((OUT/(files[part]+'.fbx')).read_bytes()).hexdigest(),'review_glb_sha256':hashlib.sha256((ROOT/'review/walkthrough'/(part+'.glb')).read_bytes()).hexdigest()})
 for v in data['views']:
  cd=bpy.data.cameras.new(part+'_'+v['id']);cd.lens=22;o=bpy.data.objects.new('View_'+part+'_'+v['id'],cd);scene.collection.objects.link(o);o.location=v['position'];o.rotation_euler=(Vector(v['target'])-o.location).to_track_quat('-Z','Y').to_euler();views.append({'camera':o.name,**v,'part':part})
 lights=list(data.get('lights',[]))
 if part=='part02':
  for loc,power in [((33,8,3.1),105),((27,12,3.05),75),((40,8,3.05),82),((33,8,-.92),90),((27,10,-.95),71),((38,4,-.95),71)]:lights.append({'position':loc,'energy':power,'angle':130})
 for i,d in enumerate(lights):
  ld=bpy.data.lights.new(part+'_Light_'+str(i),'SPOT');ld.energy=d.get('energy',65);ld.color=d.get('color',(1,.88,.72));ld.shadow_soft_size=.3;ld.spot_size=math.radians(d.get('angle',115));ld.spot_blend=.7;o=bpy.data.objects.new(ld.name,ld);scene.collection.objects.link(o);o.location=d['position']
  if d.get('target'):o.rotation_euler=(Vector(d['target'])-o.location).to_track_quat('-Z','Y').to_euler()
# Temporary review walls and early courtyard boundary helpers must not remain in the full scene.
for o in list(bpy.data.objects):
 if o.get('review_only') or o.get('temporary_until') or o.name.startswith('NAV_Boundary_') or o.name.startswith('Context_Back_Block_'):bpy.data.objects.remove(o,do_unlink=True)
visible=[o for o in scene.objects if o.type=='MESH' and not o.get('review_hidden')];colliders=[o for o in scene.objects if o.type=='MESH' and o.get('collision')]
for o in scene.objects:
 if o.get('review_hidden'):o.hide_render=True;o.display_type='WIRE'
# Texture paths are unique and local to the package. No packed file may have an empty path.
images=[]
for im in bpy.data.images:
 if not im.has_data and not im.packed_file and not im.filepath:continue
 path=Path(bpy.path.abspath(im.filepath))
 if path.is_file():im.filepath=str(OUT/'textures'/path.name)
 if im.filepath:images.append({'name':im.name,'file':Path(im.filepath).name,'exists':Path(im.filepath).is_file(),'size':list(im.size)})
 assert im.filepath and Path(im.filepath).is_file(),('unresolved image',im.name,im.filepath)
scene.world=bpy.data.worlds.new('Museum_Review_World');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.42,.54,.70,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.55
ld=bpy.data.lights.new('Daylight','SUN');ld.energy=2.7;ld.angle=.08;o=bpy.data.objects.new('Daylight',ld);scene.collection.objects.link(o);o.rotation_euler=(.48,-.4,-.65)
scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.view_settings.view_transform='AgX';scene.render.resolution_x=1440;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.camera=bpy.data.objects['View_part00_tramstart'];bpy.context.view_layer.update()
def bounds(objects):
 pts=[o.matrix_world@Vector(p) for o in objects for p in o.bound_box];return {'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)]}
report={'part':'combined','units':'metres','up':'Z in Blender / Y in FBX','parts':provenance,'visible_meshes':len(visible),'collision_meshes':len(colliders),'visible_bounds_m':bounds(visible),'vertices':sum(len(o.data.vertices) for o in visible),'polygons':sum(len(o.data.polygons) for o in visible),'images':images,'nonfinite_vertices':sum(1 for o in visible for v in o.data.vertices if not all(math.isfinite(x) for x in v.co)),'accuracy_claim':'Full-scope photo-informed review reconstruction; NOT 100% measured/current-day fidelity. Original HEIC photographs restored on 2026-10-26; exact unmeasured geometry remains provisional.'}
base=files['combined'];native=OUT/(base+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(native));bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(native))
def export(objects,path):
 bpy.ops.object.select_all(action='DESELECT')
 for o in objects:o.select_set(True)
 bpy.ops.export_scene.fbx(filepath=str(path),use_selection=True,object_types={'MESH'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',use_space_transform=True,bake_space_transform=False,mesh_smooth_type='FACE',add_leaf_bones=False,bake_anim=False,path_mode='COPY',embed_textures=True,use_custom_props=True)
visual=OUT/(base+'.fbx');export(visible,visual)
collision=OUT/(base+'_Colliders.fbx');export(colliders,collision)
report.update(fbx_sha256=hashlib.sha256(visual.read_bytes()).hexdigest(),fbx_bytes=visual.stat().st_size,collision_fbx_sha256=hashlib.sha256(collision.read_bytes()).hexdigest(),native_bytes=native.stat().st_size)
(OUT/'combined-views.json').write_text(json.dumps(views,indent=2,ensure_ascii=False));(OUT/'combined-verification.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
# Independent re-import of the combined FBX.
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(visual));bpy.context.view_layer.update();meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];actual=bounds(meshes);err=max(abs(actual[k][i]-report['visible_bounds_m'][k][i]) for k in ['min','max'] for i in range(3));report['fbx_import_check']={'imported_meshes':len(meshes),'expected_meshes':len(visible),'bounds_max_error_m':err,'passed':len(meshes)==report['visible_meshes'] and err<.002}
report['fbx_texture_check']={'images':len([i for i in bpy.data.images if i.filepath]),'missing_files':[i.filepath for i in bpy.data.images if i.filepath and not Path(bpy.path.abspath(i.filepath)).is_file()]};report['fbx_texture_check']['passed']=not report['fbx_texture_check']['missing_files']
(OUT/'combined-verification.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));assert report['nonfinite_vertices']==0 and report['fbx_import_check']['passed'] and report['fbx_texture_check']['passed'];print('COMBINED_VERIFIED',json.dumps({k:report[k] for k in ['visible_meshes','collision_meshes','vertices','polygons','fbx_bytes','fbx_import_check','fbx_texture_check']}),flush=True)
