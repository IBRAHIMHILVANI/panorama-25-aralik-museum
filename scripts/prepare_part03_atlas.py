"""Prepare a native-source document atlas, without generated or retyped content."""
from pathlib import Path
from PIL import Image,ImageOps,ImageCms
import subprocess,io,json,shutil
ROOT=Path(__file__).resolve().parents[1]
work=ROOT/'reconstruction/part03-source';work.mkdir(exist_ok=True)
raw=work/'IMG_2021-native.jpg'
if not raw.exists():subprocess.run(['sips','-s','format','jpeg','-s','formatOptions','100',str(ROOT/'drive-download-20261025T105004Z-1-001/IMG_2021.HEIC'),'--out',str(raw)],capture_output=True,check=True)
with Image.open(raw) as im:
    icc=im.info.get('icc_profile');im=ImageOps.exif_transpose(im).convert('RGB')
    if icc:im=ImageCms.profileToProfile(im,ImageCms.ImageCmsProfile(io.BytesIO(icc)),ImageCms.createProfile('sRGB'),outputMode='RGB')
    original=im.size;roi=(.012,.310,.988,.640)
    im=im.crop((round(original[0]*roi[0]),round(original[1]*roi[1]),round(original[0]*roi[2]),round(original[1]*roi[3])))
    dst=ROOT/'output/Gaziantep-Museum-2026-10-25/textures/part03-original-documents-atlas.jpg';im.save(dst,quality=96,subsampling=0)
    preview=im.copy();preview.thumbnail((4096,4096));preview.save(ROOT/'review/walkthrough/textures'/dst.name,quality=94,subsampling=0)
    (work/'atlas-provenance.json').write_text(json.dumps({'source':'IMG_2021.HEIC','source_dimensions':original,'region':roi,'atlas_dimensions':im.size,'observed_grid':{'columns':11,'rows':2},'operation':'source-region extraction and orientation/colour encoding normalization; no content generation or transcription'},indent=2))
    print('Original-document atlas',im.size,'22 displayed document cells')
