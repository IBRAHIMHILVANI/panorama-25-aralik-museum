"""Compare fixed part06 enclosure in memory; never save/recombine the master."""
import bpy,json,math,sys,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/Gaziantep-Museum-2026-10-25'
args=sys.argv[sys.argv.index('--')+1:];phase=args[0]
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Gaziantep_Museum_Combined.blend'))
scene=bpy.context.scene
if phase.startswith('after'):
 files=json.loads((ROOT/'reconstruction/part-files.json').read_text())
 for part in (['part00','part01','part06','part07'] if phase=='after07' else ['part06']):
  definition=json.loads((ROOT/'reconstruction'/(part+'-scene.json')).read_text())
  for o in list(scene.objects):
   if o.get('part')==definition['part']:bpy.data.objects.remove(o,do_unlink=True)
  with bpy.data.libraries.load(str(OUT/(files[part]+'.blend')),link=False) as (src,dst):dst.collections=[definition['part']]
  for coll in dst.collections:
   if coll:scene.collection.children.link(coll)
for o in list(scene.objects):
 if o.get('review_only') or o.get('temporary_until') or o.name.startswith('NAV_Boundary_'):bpy.data.objects.remove(o,do_unlink=True)
 elif o.get('review_hidden'):o.hide_render=True
scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True;scene.cycles.max_bounces=4;scene.view_settings.exposure=1
scene.render.resolution_x=1024;scene.render.resolution_y=576;scene.render.resolution_percentage=100
views=[('tour367',[-35.7883,43.3540,-2.54999],[-38.4355,39.1123,-2.54999])] if phase!='after07' else []
if phase.startswith('after'):
 route=json.loads((ROOT/'reconstruction/full-tour-path-2026-10-26.json').read_text())
 for t in ([int(v) for v in args[1:]] if len(args)>1 else [380,387,390,394,398] if phase=='after07' else [356,387,398]):
  sample=min(route['samples'],key=lambda s:abs(s['t']-t));views.append(('tour'+str(t),sample['position'],sample['look_target']))
 if phase=='after07' and len(args)==1:
  definition=json.loads((ROOT/'reconstruction/part07-scene.json').read_text());view=next(v for v in definition['views'] if v['id']=='hospital');views.append(('hospital',view['position'],view['target']))
for name,position,target in views:
 cd=bpy.data.cameras.new('Enclosure_Review_'+name);cd.sensor_fit='VERTICAL';cd.sensor_height=24;cd.lens=12/math.tan(math.radians(64)/2)
 camera=bpy.data.objects.new(cd.name,cd);scene.collection.objects.link(camera);camera.location=position;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();scene.camera=camera
 scene.render.filepath=str(ROOT/'review/qa'/('part06-enclosure-'+phase+'-'+name+'.png'));bpy.ops.render.render(write_still=True);print('ENCLOSURE_RENDER',phase,name,flush=True)
