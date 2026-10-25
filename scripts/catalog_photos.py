"""Make local review copies and an indexed contact sheet of every source photo."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib, json, subprocess
import cv2
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'drive-download-20261025T105004Z-1-001'
OUT = ROOT / 'review' / 'photo-catalog'
THUMBS = OUT / 'images'
THUMBS.mkdir(parents=True, exist_ok=True)
files = sorted(SOURCE.glob('*.HEIC'))

def convert(p):
    dst = THUMBS / (p.stem + '.jpg')
    if not dst.exists():
        subprocess.run(['sips', '-s', 'format', 'jpeg', '-s', 'formatOptions', '85', '-Z', '1280', str(p), '--out', str(dst)], capture_output=True, check=True)
    with Image.open(dst) as raw:
        im = ImageOps.exif_transpose(raw).convert('RGB')
        original_size = im.size
        small = np.asarray(im.resize((256, 192)))
        gray = cv2.cvtColor(small, cv2.COLOR_RGB2GRAY)
        return {'file': p.name, 'source': str(p.relative_to(ROOT)), 'review': str(dst.relative_to(ROOT)), 'bytes': p.stat().st_size, 'review_size': list(original_size), 'sharpness': round(float(cv2.Laplacian(gray, cv2.CV_64F).var()), 2), 'luminance': round(float(gray.mean()), 2), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}

with ThreadPoolExecutor(max_workers=5) as pool:
    rows=[]
    for i, row in enumerate(pool.map(convert, files)):
        rows.append(row)
        if (i+1)%40==0: print(f'Converted {i+1}/{len(files)}',flush=True)

font_path='/System/Library/Fonts/Menlo.ttc'
font=ImageFont.truetype(font_path, 18)
heading=ImageFont.truetype(font_path, 23)
for page, start in enumerate(range(0, len(rows), 20),1):
    subset=rows[start:start+20]
    sheet=Image.new('RGB',(1280,1390),'#12171d')
    d=ImageDraw.Draw(sheet)
    d.text((20,12),f'Gaziantep source photographs | {page:02d} | {subset[0]["file"]} - {subset[-1]["file"]}',font=heading,fill='white')
    for i,row in enumerate(subset):
        x=(i%4)*320;y=60+(i//4)*264
        with Image.open(ROOT/row['review']) as raw:
            im=ImageOps.exif_transpose(raw).convert('RGB')
            im.thumbnail((310,232))
            sheet.paste(im,(x+(320-im.width)//2,y+(232-im.height)//2))
        d.text((x+12,y+237),row['file'],font=font,fill='#ffffff')
    sheet.save(OUT/f'contact-{page:02d}.jpg',quality=93)
(OUT/'manifest.json').write_text(json.dumps({'source_count':len(rows),'photos':rows},indent=2))
print(json.dumps({'count':len(rows),'contact_sheets':page,'directory':str(OUT)},indent=2),flush=True)
