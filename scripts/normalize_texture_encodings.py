"""Normalize texture file encoding for engines that ignore EXIF orientation.

No retouching or enhancement: bake the existing display orientation into pixels,
convert the embedded colour profile to sRGB, and retain the pre-normalized file.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image,ImageOps,ImageCms
import io,json,hashlib,shutil,sys

ROOT=Path(__file__).resolve().parents[1]
part=sys.argv[1] if len(sys.argv)>1 else 'part02'
scene=json.loads((ROOT/'reconstruction'/f'{part}-scene.json').read_text())
names=sorted({Path(m['image']).name for m in scene['materials'].values() if m.get('image') and m['image'].lower().endswith('.jpg')})
OUT=ROOT/'output/Gaziantep-Museum-2026-10-25'
jobs=[(folder/n,label) for n in names for folder,label in [(OUT/'textures','full'),(ROOT/'review/walkthrough/textures','preview')]]
backup=ROOT/'backups/texture-encoding-2026-10-25'
target_profile=ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB'))

def normalize(job):
    p,label=job
    with Image.open(p) as raw:
        orientation=raw.getexif().get(274,1)
        icc=raw.info.get('icc_profile')
        profile_name=''
        if icc:
            try:profile_name=ImageCms.getProfileName(ImageCms.ImageCmsProfile(io.BytesIO(icc))).strip()
            except Exception:pass
        if orientation==1 and ('srgb' in profile_name.lower() or not icc):return {'file':str(p.relative_to(ROOT)),'changed':False,'orientation':1}
        before_hash=hashlib.sha256(p.read_bytes()).hexdigest();original_size=raw.size
        im=ImageOps.exif_transpose(raw).convert('RGB')
        if icc:
            im=ImageCms.profileToProfile(im,ImageCms.ImageCmsProfile(io.BytesIO(icc)),target_profile,outputMode='RGB')
        dst=backup/label/p.name;dst.parent.mkdir(parents=True,exist_ok=True)
        if not dst.exists():shutil.copy2(p,dst)
        exif=Image.Exif();exif[274]=1
        temp=p.with_name(p.stem+'.normalizing.jpg')
        im.save(temp,format='JPEG',quality=96,subsampling=0,icc_profile=target_profile.tobytes(),exif=exif)
        temp.replace(p)
        return {'file':str(p.relative_to(ROOT)),'changed':True,'old_orientation':orientation,'new_orientation':1,'old_size':original_size,'new_size':im.size,'old_profile':profile_name,'new_profile':'sRGB','before_sha256':before_hash,'after_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'backup':str(dst.relative_to(ROOT))}

with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(normalize,jobs))
(OUT/(part+'-texture-encoding.json')).write_text(json.dumps(rows,indent=2))
print(json.dumps({'part':part,'checked':len(rows),'normalized':sum(r['changed'] for r in rows),'report':str(OUT/(part+'-texture-encoding.json'))},indent=2))
