"""Inspect embedded FBX Video payloads independently of application path resolution."""
from pathlib import Path
import sys,json,hashlib,io
from PIL import Image
from fbx_io import FBX
ROOT=Path(__file__).resolve().parents[1];part=sys.argv[1]
out=ROOT/'output/Gaziantep-Museum-2026-10-25'
report=json.loads((out/f'{part}-verification.json').read_text())
files={k:v+'.fbx' for k,v in json.loads((ROOT/'reconstruction/part-files.json').read_text()).items()}
fbx=FBX(out/files[part]);images=[]
for node in fbx.root('Objects').children:
    if node.name!='Video':continue
    file_node=node.child('RelativeFilename') or node.child('Filename');name=Path(file_node.props[0].value.replace('\\','/')).name
    content=node.child('Content');blob=content.props[0].value if content and content.props else b''
    source=out/'textures'/name
    row={'name':name,'embedded_bytes':len(blob),'source_exists':source.exists(),'sha256':hashlib.sha256(blob).hexdigest()}
    row['matches_texture_file']=source.exists() and blob==source.read_bytes()
    if blob:
        with Image.open(io.BytesIO(blob)) as im:row.update(size_px=list(im.size),orientation=im.getexif().get(274,1))
    images.append(row)
result={'part':part,'fbx_sha256':hashlib.sha256((out/files[part]).read_bytes()).hexdigest(),'images':images,'passed':bool(images) and all(r['embedded_bytes']>0 and r['matches_texture_file'] and r['orientation']==1 for r in images)}
(out/f'{part}-embedded-textures.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'part':part,'embedded_images':len(images),'passed':result['passed']},indent=2))
assert result['passed'],result
