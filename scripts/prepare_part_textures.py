"""Create only missing source-photo textures requested by a staged scene."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,re,sys,subprocess
ROOT=Path(__file__).resolve().parents[1]
part=sys.argv[1];data=json.loads((ROOT/f'reconstruction/{part}-scene.json').read_text())
full=ROOT/'output/Gaziantep-Museum-2026-10-25/textures';preview=ROOT/'review/walkthrough/textures'
images=sorted({Path(m['image']).name for m in data['materials'].values() if m.get('image')}|{f"IMG_{v['photo']}.jpg" for v in data.get('views',[]) if v.get('photo')})
def convert(name):
    if not re.fullmatch(r'IMG_\d+\.jpg',name):
        assert (full/name).exists(),name;return
    source=ROOT/'drive-download-20261025T105004Z-1-001'/(Path(name).stem+'.HEIC')
    if not source.exists():source=Path('/Volumes/ssd/Projects/Musuem Gaziantep/drive-download-20261025T105004Z-1-001')/(Path(name).stem+'.HEIC')
    for folder,size in [(full,4096),(preview,2048)]:
        if not (folder/name).exists():
            if source.exists():subprocess.run(['sips','-s','format','jpeg','-s','formatOptions','95','-Z',str(size),str(source),'--out',str(folder/name)],capture_output=True,check=True)
            else:
                from PIL import Image,ImageOps
                ref=ROOT/'review/photo-catalog/images'/name
                if not ref.exists():raise FileNotFoundError(ref)
                im=ImageOps.exif_transpose(Image.open(ref)).convert('RGB');im.thumbnail((size,size));im.save(folder/name,quality=96,subsampling=0)
with ThreadPoolExecutor(max_workers=3) as pool:list(pool.map(convert,images))
print('Verified source texture files:',len(images),flush=True)
