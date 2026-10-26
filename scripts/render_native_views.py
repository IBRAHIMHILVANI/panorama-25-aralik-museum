"""Native scene camera review when interactive browser automation is unavailable."""
import bpy,sys,json
from mathutils import Vector
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];args=sys.argv[sys.argv.index('--')+1:];part=args[0];views=args[1:]
base=json.loads((ROOT/'reconstruction/part-files.json').read_text())[part]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'output/Gaziantep-Museum-2026-10-25'/(base+'.blend')))
scene=bpy.context.scene;scene.view_settings.exposure=1.0;scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.use_denoising=True;scene.cycles.max_bounces=5;scene.render.resolution_x=1200;scene.render.resolution_y=750;scene.render.resolution_percentage=100
folder=ROOT/'review/qa'/('native-'+part);folder.mkdir(exist_ok=True)
for v in views:
 camera=bpy.data.objects.get('View_'+v)
 if not camera:
  data=json.loads((ROOT/'reconstruction'/(part+'-scene.json')).read_text());definition=next(q for q in data['views'] if q['id']==v)
  cd=bpy.data.cameras.new('Review_'+v);cd.lens=22;camera=bpy.data.objects.new('Review_'+v,cd);scene.collection.objects.link(camera);camera.location=definition['position'];camera.rotation_euler=(Vector(definition['target'])-camera.location).to_track_quat('-Z','Y').to_euler()
 scene.camera=camera;scene.render.filepath=str(folder/(v+'.png'));bpy.ops.render.render(write_still=True);print('REVIEW_RENDER',part,v,flush=True)
