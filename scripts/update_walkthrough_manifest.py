from pathlib import Path
import json,hashlib,math
from shapely.geometry import shape
from museum_architecture import mapped_polygon,polygon_parts
ROOT=Path(__file__).resolve().parents[1];folder=ROOT/'review/walkthrough';old=json.loads((folder/'parts.json').read_text());byid={p['id']:p for p in old['parts']};files=json.loads((ROOT/'reconstruction/part-files.json').read_text());titles=[('المحطة والشوارع','ابدأ داخل الترام وانزل إلى المنصّة ثم اتجه إلى المتحف.'),('الساحة والمدخل','الساحة الوسطية وممر الأعلام والمدخل.'),('الاستقبال والخريطة','الشرفة والدرج وقاعة الخريطة.'),('الوثائق والأزياء والأسلحة','الوثائق، 23 زيًا ثلاثي الأبعاد، القبعات والمدفع.'),('الوجوه والكستل والمراسلات','الممر والغرفة الحمراء والكستل والمراسلات.'),('اللوحات والتاريخ','اللوحات الأصلية والمكتب وقاعة الصور.'),('المشاهد الثلاثة','الحياة والحرف والدفاع والركام والعرض.'),('البانوراما','درج الصعود والقاعة الدائرية ومشاهد المدينة.'),('السينما','السينما متصلة بجانب الدرج من جهة قاعة الخريطة.')]
parts=[]
for i,(title,desc) in enumerate(titles):
 id='part%02d'%i;data=json.loads((ROOT/'reconstruction'/(id+'-scene.json')).read_text());photos=list(dict.fromkeys(v['photo'] for v in data['views'] if v.get('photo'))) or [1935,1936]
 p=byid.get(id,{});p.update(id=id,number=i,title=title,description=desc,model=id+'.glb?v='+hashlib.sha256((folder/(id+'.glb')).read_bytes()).hexdigest()[:12],views=id+'-views.json?v='+hashlib.sha256((folder/(id+'-views.json')).read_bytes()).hexdigest()[:12],photos=photos,fbx=files[id]+'.fbx',review_status='second_cycle_review',note='مراجعة ثلاثية الأبعاد. الأبعاد غير المقاسة والتفاصيل غير المصوّرة تقديرية. استُعيدت الصور الأصلية من HEIC؛ المقاسات غير الموثقة ما زالت تقديرية.')
 if i in [5,6]:
  a,b=(105,140) if i==5 else (140,168);ri=37 if i==5 else 33;p['plan']=[[[float(-6+r*math.cos(math.radians(t))),float(23.5+r*math.sin(math.radians(t)))] for r,ts in [(45,range(a,b+1)),(ri,range(b,a-1,-1))] for t in ts]]
 if i==7:p['plan']=[[[float(-26+19.4*math.cos(t*math.pi/32)),float(13+19.4*math.sin(t*math.pi/32))] for t in range(65)]]
 if i==0:
  geo=json.loads((ROOT/'references/geospatial/local-map.geojson').read_text());scope=shape(geo['metadata']['scope_polygon']);plans=[]
  for f in geo['features']:
   g=shape(f['geometry']).intersection(scope)
   if f['properties'].get('highway'):g=g.buffer(2.5)
   if f['properties'].get('highway') or f['properties'].get('building') or f['properties'].get('railway')=='tram_stop':
    for pp in polygon_parts(mapped_polygon(g)):plans.append([list(x) for x in pp.exterior.coords])
  p['plan']=plans;p['note']='المساحة تشمل 110 أمتار حول المتحف وحول كامل منصتي المحطة. حدود الطرق والمباني من OSM، تفاصيل الواجهات والأبعاد غير المقاسة تقديرية. مراجع Street View المتاحة مؤرخة 2024.'
 if i==8:
  p['interior_bounds']=[40.55,-2.9,-4.3,52.6,3.2,-1.35];p['plan']=[[[44.5,-2.79],[52.5,-2.79],[52.5,3.01],[44.5,3.01]],[[40.55,-.45],[44.5,-.45],[44.5,3.1],[40.55,3.1]]]
  p['note']='موضع السينما بجانب الدرج من اليمين حسب إفادة المستخدم. مقاسات القاعة والممر وعدد المقاعد تقديرية، والتصميم الداخلي مستند للصورة الحقيقية المنشورة.'
 parts.append(p)
d={'parts':parts,'pending':'مطابقة الواجهات والحدائق والأجزاء غير المصوّرة؛ الأبعاد الدقيقة غير مقاسة','combined_fbx':'../../output/Gaziantep-Museum-2026-10-25/'+files['combined']+'.fbx','source_date':'2026-10-21','review_date':'2026-10-26'}
for f in ['parts.json','parts-qa.json']:(folder/f).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')))
print('Manifest includes',len(parts),'parts')
