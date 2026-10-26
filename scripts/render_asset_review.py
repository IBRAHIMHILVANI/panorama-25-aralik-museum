"""Render all sides of a generated 3D candidate for actual mesh inspection."""
import bpy,sys,math,json
from pathlib import Path
from mathutils import Vector
root=Path(__file__).resolve().parents[1]
path=Path(sys.argv[sys.argv.index('--')+1]);name=path.stem
out=root/'review/qa'/name;out.mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.gltf(filepath=str(path));meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];bpy.context.view_layer.update()
pts=[o.matrix_world@Vector(p) for o in meshes for p in o.bound_box];mi=Vector([min(p[i] for p in pts) for i in range(3)]);ma=Vector([max(p[i] for p in pts) for i in range(3)]);center=(mi+ma)/2;h=ma.z-mi.z
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True;scene.render.resolution_x=600;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.20,.24,.29,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.8
for loc,power,size in [((3,-4,5),650,4),((-3,2,4),500,3),((0,3,1),200,2)]:
    d=bpy.data.lights.new('Studio','AREA');d.energy=power;d.shape='DISK';d.size=size;o=bpy.data.objects.new(d.name,d);scene.collection.objects.link(o);o.location=loc;o.rotation_euler=(center-o.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,mi.z-.006));floor=bpy.context.object;mat=bpy.data.materials.new('Studio_Floor');mat.diffuse_color=(.12,.15,.18,1);floor.data.materials.append(mat)
camdata=bpy.data.cameras.new('Review');camdata.type='ORTHO';camdata.ortho_scale=h*1.16;cam=bpy.data.objects.new('Review',camdata);scene.collection.objects.link(cam);scene.camera=cam
report={'source_glb':str(path),'mesh_count':len(meshes),'bounds_min':list(mi),'bounds_max':list(ma),'triangles':sum(len(o.data.loop_triangles) for o in meshes)}
for label,xy in [('from_negative_y',(0,-4)),('from_positive_x',(4,0)),('from_positive_y',(0,4)),('from_negative_x',(-4,0))]:
    cam.location=(center.x+xy[0],center.y+xy[1],center.z+.08*h);cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();scene.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)
(out/'inspection.json').write_text(json.dumps(report,indent=2));print('ASSET_REVIEW_READY',str(out),flush=True)
