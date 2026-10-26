"""Restore real camera pixels after SSD reconnection; no generative enhancement."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image,ImageOps,ImageCms
import json,re,subprocess,hashlib,shutil,io,sys
ROOT=Path(__file__).resolve().parents[1]
SOURCE=Path('/Volumes/ssd/Projects/Musuem Gaziantep/drive-download-20261025T105004Z-1-001')
OUT=ROOT/'output/Gaziantep-Museum-2026-10-25/textures'
PREVIEW=ROOT/'review/walkthrough/textures'
BACKUP=ROOT/'backups/fidelity-followup-2026-10-26/low-resolution-textures'
TEMP=ROOT/'reconstruction/original-photo-conversion';TEMP.mkdir(parents=True,exist_ok=True)
assert SOURCE.is_dir(),'The real SSD must be connected'
names=set()
for p in (ROOT/'reconstruction').glob('part0[0-8]-scene.json'):
 d=json.loads(p.read_text())
 names.update(Path(m['image']).name for m in d['materials'].values() if m.get('image') and re.fullmatch(r'IMG_\d+\.jpg',Path(m['image']).name))
 names.update(f"IMG_{v['photo']}.jpg" for v in d.get('views',[]) if v.get('photo'))
if '--all' in sys.argv:names={p.stem+'.jpg' for p in SOURCE.glob('IMG_*.HEIC')}
profile=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB'))
def restore(name):
 source=SOURCE/(Path(name).stem+'.HEIC');assert source.is_file(),source
 temp=TEMP/name
 subprocess.run(['sips','-s','format','jpeg','-s','formatOptions','97','-Z','4096',str(source),'--out',str(temp)],capture_output=True,check=True)
 with Image.open(temp) as raw:
  im=ImageOps.exif_transpose(raw).convert('RGB');icc=raw.info.get('icc_profile')
  if icc:im=ImageCms.profileToProfile(im,ImageCms.ImageCmsProfile(io.BytesIO(icc)),profile,outputMode='RGB')
  row={'name':name,'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'restored_size':list(im.size),'outputs':[]}
  for folder,label,size in [(OUT,'full',4096),(PREVIEW,'preview',2048)]:
   p=folder/name;p.parent.mkdir(parents=True,exist_ok=True)
   if p.exists():
    old=BACKUP/label/name;old.parent.mkdir(parents=True,exist_ok=True)
    if not old.exists():shutil.copy2(p,old)
   small=im.copy();small.thumbnail((size,size),Image.Resampling.LANCZOS)
   exif=Image.Exif();exif[274]=1
   small.save(p,quality=96,subsampling=0,icc_profile=profile.tobytes(),exif=exif)
   row['outputs'].append({'path':str(p.relative_to(ROOT)),'size':list(small.size),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
  catalog=ROOT/'review/photo-catalog/images'/name
  small=im.copy();small.thumbnail((1600,1600),Image.Resampling.LANCZOS);small.save(catalog,quality=94,subsampling=0)
 temp.unlink()
 return row
with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(restore,sorted(names)))
report={'source_date':'2026-10-21','restored_on':'2026-10-26','photos_restored':len(rows),'processing':'Decode source HEIC, bake EXIF orientation, convert profile to sRGB, downsample only. No AI invented pixels.','rows':rows}
(ROOT/'reconstruction/original-photo-restoration-2026-10-26.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
print('RESTORED_ORIGINAL_PHOTOS',len(rows),flush=True)
