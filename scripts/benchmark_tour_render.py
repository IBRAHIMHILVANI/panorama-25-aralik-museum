"""Measure native EEVEE export speed before choosing a full-tour video profile."""
import bpy,time,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'output/Gaziantep-Museum-2026-10-25/Gaziantep_Museum_Combined.blend'))
s=bpy.context.scene;s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=16;s.eevee.use_raytracing=False
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=100
s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=94
s.camera=bpy.data.objects['View_part00_traminterior'];s.view_settings.exposure=.6
folder=ROOT/'review/qa/tour-render-benchmark';folder.mkdir(exist_ok=True)
timings=[]
for i in range(3):
 s.camera.location.x+=.02;s.render.filepath=str(folder/('%03d.jpg'%i));t=time.monotonic();bpy.ops.render.render(write_still=True);timings.append(time.monotonic()-t)
 print('BENCH_FRAME',i,timings[-1],flush=True)
(folder/'timings.json').write_text(json.dumps({'engine':s.render.engine,'resolution':[1280,720],'samples':16,'frame_seconds':timings},indent=2))
