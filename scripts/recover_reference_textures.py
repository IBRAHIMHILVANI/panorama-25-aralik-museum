"""Recovery-only source-region extraction from retained review contact sheets.
Never treat these low-resolution copies as the original 319 HEIC photographs.
"""
from pathlib import Path
from PIL import Image,ImageOps
import numpy as np,json,shutil
ROOT=Path(__file__).resolve().parents[1];catalog=ROOT/'review/photo-catalog';folder=catalog/'images';folder.mkdir(exist_ok=True)
ids=[n for n in range(1935,2259) if n not in [1942,1943,1944,1945,2000]];rows=[]
for rank,n in enumerate(ids):
    p=folder/f'IMG_{n}.jpg';fallback=False
    if not p.exists():
        page=rank//20+1;slot=rank%20;sheet=catalog/f'contact-{page:02}.jpg'
        if not sheet.exists():raise RuntimeError(str(sheet))
        im=Image.open(sheet).convert('RGB');x=(slot%4)*320;y=60+(slot//4)*264;tile=im.crop((x+4,y,x+316,y+232));a=np.asarray(tile).astype(int);bg=np.array([18,23,29]);mask=np.abs(a-bg).sum(axis=2)>35
        cx=np.flatnonzero(mask.sum(axis=0)>max(3,tile.height*.025));cy=np.flatnonzero(mask.sum(axis=1)>max(3,tile.width*.025))
        if len(cx) and len(cy):tile=tile.crop((max(0,cx[0]-2),max(0,cy[0]-2),min(tile.width,cx[-1]+3),min(tile.height,cy[-1]+3)))
        tile.save(p,quality=96,subsampling=0);fallback=True
    with Image.open(p) as im:sz=im.size
    if max(sz)<400:fallback=True
    rows.append({'id':n,'file':f'IMG_{n}.HEIC','review':str(p.relative_to(ROOT)),'available_resolution':sz,'recovery_source':'contact_sheet_region' if fallback else 'retained_tool_image','original_heic_available':False,'needs_original_for_final_texture':fallback})
(catalog/'recovery-manifest.json').write_text(json.dumps({'original_source_count':319,'reference_copies':len(rows),'contact_sheet_fallbacks':sum(r['needs_original_for_final_texture'] for r in rows),'photos':rows},indent=2))
(root:=ROOT/'reconstruction').mkdir(exist_ok=True);(root/'evidence-catalog.json').write_text(json.dumps({'source_count':319,'status':'recovery preview catalog; originals remain on unavailable SSD','photos':rows},indent=2))
print('Reference copies',len(rows),'low-resolution recovery regions',sum(r['needs_original_for_final_texture'] for r in rows))
