import bpy,sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/Gaziantep-Museum-2026-10-25';bpy.ops.wm.open_mainfile(filepath=str(OUT/'Gaziantep_Museum_Combined.blend'));scene=bpy.context.scene;scene.cycles.samples=24;scene.cycles.max_bounces=5;scene.cycles.use_denoising=True;scene.view_settings.exposure=1;scene.render.resolution_x=1200;scene.render.resolution_y=750;scene.render.resolution_percentage=100
folder=ROOT/'review/qa/whole-cycle';folder.mkdir(exist_ok=True)
args=sys.argv[sys.argv.index('--')+1:]
for v in args:
 name='View_'+v;camera=bpy.data.objects.get(name)
 if not camera:raise ValueError(name)
 scene.camera=camera;scene.render.filepath=str(folder/(v+'.png'));bpy.ops.render.render(write_still=True);print('WHOLE_REVIEW_RENDER',v,flush=True)
