from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/Gaziantep-Museum-2026-10-25';QA=ROOT/'review/qa';tests=[]
for i in range(8):
 p=QA/('part%02d-navigation.json'%i);d=json.loads(p.read_text());tests.append({'part':'part%02d'%i,'passed':d['passed'],'checks':len(d['tests']),'report':str(p.relative_to(ROOT)),'own_glb_sha256':hashlib.sha256((ROOT/'review/walkthrough'/('part%02d.glb'%i)).read_bytes()).hexdigest()})
clearances=[]
for p in sorted(QA.glob('part[0-9][0-9]-clearance.json'))+[QA/'part02-stair-clearance-after.json']:
 d=json.loads(p.read_text());clearances.append({'report':str(p.relative_to(ROOT)),'passed':d.get('passed'),'samples':d.get('samples',d.get('tested_positions'))})
report={'review_date':'2026-10-26','navigation_passed':all(x['passed'] for x in tests),'navigation_checks':sum(x['checks'] for x in tests),'navigation':tests,'clearance':clearances,'source_image_status':'66 retained review photos +253 temporary low-resolution contact-sheet regions;319HEIC originals on missing external SSD','browser_qa':'Unavailable after SSD disconnect: CUA Node runtime fails to start. Native Blender visual review and exported-mesh capsule simulation performed; no FPS claim.','native_visual_review':'review/qa/whole-cycle/','fidelity_status':'Full-scope editable review model, not a100percent as-built/current-day replica','source_freshness':{'user_photos':'2026-10-21','google_street_view':'2024-10','station_photographs':'2024-04-04','OSM_download':'2026-10-26'},'credits_3d_generation':58535,'generated_clothing_models':23}
for name,key in [('combined-verification.json','combined_export'),('combined-embedded-textures.json','embedded_textures'),('combined-colliders-verification.json','collision_export')]:
 d=json.loads((OUT/name).read_text());report[key]={'file':name,'passed':d.get('passed',d.get('fbx_import_check',{}).get('passed'))}
(OUT/'second-cycle-review.json').write_text(json.dumps(report,indent=2,ensure_ascii=False));assert report['navigation_passed'] and all(x['passed'] for x in clearances);print(json.dumps({'navigation_checks':report['navigation_checks'],'passed':report['navigation_passed'],'clearance_reports':len(clearances)},indent=2))
