"""Convert only a complete recording of the current verified route to a phone-ready MP4."""
from pathlib import Path
import json,hashlib,subprocess,time,shutil
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output/Gaziantep-Museum-2026-10-25/video'
route=ROOT/'reconstruction/full-tour-path-2026-10-26.json'
route_hash=hashlib.sha256(route.read_bytes()).hexdigest()
candidates=[]
for p in OUT.glob('*.recording.json'):
 d=json.loads(p.read_text())
 if d.get('complete') is True and d.get('request',{}).get('route_sha256')==route_hash:candidates.append((p,d))
assert candidates,'No complete recording matches the current route. Do not finalize an older QA capture.'
metadata_path,metadata=max(candidates,key=lambda x:x[1].get('finished_at',0))
source=Path(metadata['path']).resolve();assert source.parent==OUT.resolve() and source.suffix=='.webm' and source.is_file()
dest=OUT/'Gaziantep_Full_Journey_2026-10-26.mp4'
if dest.exists():
 backup=OUT/'previous-encodes';backup.mkdir(exist_ok=True);shutil.copy2(dest,backup/(dest.stem+'-'+str(int(time.time()))+'.mp4'))
temporary=OUT/'Gaziantep_Full_Journey_2026-10-26.encoding.mp4'
base=['/opt/homebrew/bin/ffmpeg','-hide_banner','-loglevel','warning','-i',str(source),'-an','-vf','fps=30,scale=in_range=pc:out_range=tv,format=yuv420p','-pix_fmt','yuv420p','-color_range','tv','-colorspace','bt709','-color_primaries','bt709','-color_trc','bt709']
cmd=base+['-c:v','h264_videotoolbox','-b:v','6000k','-movflags','+faststart','-y',str(temporary)]
r=subprocess.run(cmd,capture_output=True,text=True)
encoder='h264_videotoolbox'
if r.returncode:
 print('Hardware encode unavailable; using software encoder:',r.stderr[-600:],flush=True)
 encoder='libx264';r=subprocess.run(base+['-c:v','libx264','-preset','veryfast','-crf','20','-threads','4','-movflags','+faststart','-y',str(temporary)],capture_output=True,text=True)
assert r.returncode==0,r.stderr[-3000:]
probe=subprocess.run(['/opt/homebrew/bin/ffprobe','-v','error','-show_entries','format=duration,size:stream=codec_name,width,height,avg_frame_rate,nb_frames,pix_fmt,color_range,color_space','-of','json',str(temporary)],capture_output=True,text=True,check=True)
info=json.loads(probe.stdout);video=info['streams'][0];duration=float(info['format']['duration'])
assert video['codec_name']=='h264' and video['width']==1280 and video['height']==720
assert video['pix_fmt']=='yuv420p' and duration>=metadata['client_metadata']['playback_seconds']-.5,(duration,metadata['client_metadata'])
decode=subprocess.run(['/opt/homebrew/bin/ffmpeg','-hide_banner','-loglevel','error','-threads','2','-i',str(temporary),'-f','null','-'],capture_output=True,text=True)
assert decode.returncode==0 and not decode.stderr.strip(),decode.stderr[-3000:]
temporary.replace(dest)
qa=ROOT/'review/qa/video-followup-2026-10-26';qa.mkdir(exist_ok=True)
times=[1,duration*.20,duration*.40,duration*.60,duration*.80,max(0,duration-1)]
frames=[]
for i,t in enumerate(times):
 p=qa/f'final-video-{i:02d}.jpg'
 subprocess.run(['/opt/homebrew/bin/ffmpeg','-hide_banner','-loglevel','error','-ss',str(t),'-i',str(dest),'-frames:v','1','-q:v','2','-y',str(p)],check=True)
 frames.append({'t_seconds':t,'file':str(p.relative_to(ROOT))})
report={'passed':True,'source_recording_metadata':str(metadata_path.relative_to(ROOT)),'source_webm':str(source.relative_to(ROOT)),'route_sha256':route_hash,'route_seconds':metadata['client_metadata']['playback_seconds'],'video_seconds':duration,'encoder':encoder,'file':str(dest),'bytes':dest.stat().st_size,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'stream':video,'complete_decode_error_output':decode.stderr,'visual_check_frames':frames,'quality_scope':'Continuous review-model journey. This video is not a claim of fully surveyed or current-day real-world fidelity.'}
(OUT/'Gaziantep_Full_Journey_2026-10-26.verification.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
print(json.dumps({k:report[k] for k in ['passed','file','video_seconds','bytes','sha256','stream']},indent=2),flush=True)
