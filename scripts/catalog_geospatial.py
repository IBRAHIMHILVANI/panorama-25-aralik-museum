from pathlib import Path
import json,xml.etree.ElementTree as ET,math
from shapely.geometry import Polygon,Point,LineString,mapping,shape,box
from shapely.ops import unary_union
r=ET.parse('references/geospatial/osm-gaziantep-2026-10-25.osm').getroot();nodes={e.get('id'):(float(e.get('lon')),float(e.get('lat'))) for e in r.findall('node')};origin=(37.379879,37.0661528);sx=111320*math.cos(math.radians(origin[1]));sy=110574;xy=lambda p:((p[0]-origin[0])*sx,(p[1]-origin[1])*sy)
features=[]
for e in r.findall('way'):
 t={a.get('k'):a.get('v') for a in e.findall('tag')}
 if not any(k in t for k in ['building','highway','railway','landuse','leisure','natural','waterway','barrier']):continue
 nd=e.findall('nd');pts=[xy(nodes[n.get('ref')]) for n in nd if n.get('ref') in nodes]
 if len(pts)<2:continue
 closed=nd[0].get('ref')==nd[-1].get('ref');g=Polygon(pts) if closed and len(pts)>3 else LineString(pts)
 if not g.is_valid:g=g.buffer(0)
 if not g.is_empty:features.append({'type':'Feature','id':int(e.get('id')),'properties':t|{'source_version':e.get('version'),'source_timestamp':e.get('timestamp')},'geometry':mapping(g)})
ids=[1005620788,1005620789];museum=unary_union([shape(f['geometry']) for f in features if f['id'] in ids]);boundary=museum.convex_hull;tram=xy((37.3769643,37.0661293));platform_hull=unary_union([shape(f['geometry']) for f in features if f['id'] in [1272087689,1272087690]]).convex_hull;scope=boundary.buffer(110).union(platform_hull.buffer(110)).union(LineString([tram,(-45,-15)]).buffer(38));features=[f for f in features if shape(f['geometry']).intersects(scope)]
meta={'source':'OpenStreetMap map API','retrieved':'2026-10-26','attribution':'© OpenStreetMap contributors','license':'ODbL','license_url':'https://www.openstreetmap.org/copyright','origin_lon_lat':origin,'coordinates':'local east/north metres, short-distance latitude adjusted conversion','tram_platform_way_ids':[1272087689,1272087690]};meta.update(museum_building_way_ids=ids,museum_complex_bounds_xy=list(boundary.bounds),scope_polygon=mapping(scope),museum_complex_footprint=mapping(museum),requested_buffer_m=100,working_buffer_m=110,authoring_to_geographic={'rotation_deg':-130,'translation_east_north_m':[-28.426,-13.929],'basis':'provisional alignment from original-photo outdoor headings/GPS, courtyard portal, and satellite panorama roof; not survey control','approximate_panorama_center_enu_m':[-1.75,-2.38]},source_photos_capture_date='2026-10-21',source_photo_gps_note='All 319 have metadata; indoor horizontal error often tens of metres. Treat as consistency evidence, not measured room positions.')
Path('references/geospatial/local-map.geojson').write_text(json.dumps({'type':'FeatureCollection','metadata':meta,'features':features},indent=2));Path('references/geospatial/georeference.json').write_text(json.dumps(meta,indent=2))
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(14,11));ax.set_facecolor('#f5f3eb');clip=box(-340,-210,180,160)
for f in features:
 g=shape(f['geometry']).intersection(clip);t=f['properties'];col='#bba76f' if f['id'] in ids else '#d3d1c7' if 'building' in t else '#b9d0ad' if 'leisure' in t or t.get('landuse')=='grass' else '#e7e4d9'
 for geo in ([g] if g.geom_type in ['Polygon','LineString'] else list(g.geoms) if hasattr(g,'geoms') else []):
  if geo.geom_type=='Polygon':ax.fill(*geo.exterior.xy,color=col,alpha=.9);ax.plot(*geo.exterior.xy,color='#9b9f98',lw=.7)
  if 'highway' in t or 'railway' in t:
   line=geo.exterior if geo.geom_type=='Polygon' else geo
   if hasattr(line,'xy'):ax.plot(*line.xy,color='#a85d4b' if 'railway' in t else '#8f9597',lw=1.4 if 'railway' in t else 2)
  if t.get('name') and g.length>40 and not g.is_empty:
   c=g.centroid
   if clip.contains(c):ax.text(c.x,c.y,t['name'],fontsize=5.8,color='#59656b',clip_on=True)
ax.plot(*boundary.buffer(100).exterior.xy,'--',color='#527c63',lw=1.5);ax.scatter(*tram,c='#cf4a37',s=65);ax.annotate('15 Temmuz tram start',tram,xytext=(-325,65),arrowprops={'arrowstyle':'->'},fontsize=10);ax.text(-10,-33,'Museum complex\nand courtyard',ha='center',fontsize=9)
metadata=[] # Outdoor source-photo GPS remains secondary to mapped plan geometry.
for d in metadata[:7]:
 g=d['gps'];p=xy((g['Longitude'],g['Latitude']));h=math.radians(g['ImgDirection']);ax.plot(*p,'o',c='#235f87',ms=4);ax.arrow(*p,math.sin(h)*8,math.cos(h)*8,width=.3,color='#235f87');ax.text(p[0]-8,p[1],d['file'][4:8],fontsize=5.5,clip_on=True)
ax.set_aspect('equal');ax.set_xlim(-340,180);ax.set_ylim(-210,160);ax.set_xlabel('East (m)');ax.set_ylabel('North (m)');ax.set_title('Museum complex, tram start and 100 m surroundings | 25 October 2026')
fig.text(.11,.02,'Geometry: © OpenStreetMap contributors (ODbL). Dashed line: 100 m buffer. Both museum and station platform envelopes include 110 m working context; facade elevations remain unverified.',fontsize=8);fig.savefig('references/geospatial/site-plan-reference.png',dpi=140);plt.close(fig)
print('Geospatial features',len(features),'complex bounds',boundary.bounds)