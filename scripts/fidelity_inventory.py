"""Per-building evidence inventory; a footprint is never treated as a verified facade."""
from pathlib import Path
import json,math,xml.etree.ElementTree as ET
from shapely.geometry import Polygon,Point,LineString,shape,mapping
from shapely.ops import unary_union,nearest_points
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'reconstruction/fidelity-pass-2026-10-26';out.mkdir(exist_ok=True)
meta=json.loads((ROOT/'references/geospatial/georeference.json').read_text());lon0,lat0=meta['origin_lon_lat'];sx=111320*math.cos(math.radians(lat0));sy=110574
xy=lambda p:((p[0]-lon0)*sx,(p[1]-lat0)*sy)
ll=lambda p:(p[0]/sx+lon0,p[1]/sy+lat0)
r=ET.parse(ROOT/'references/geospatial/osm-gaziantep-2026-10-25.osm').getroot();nodes={n.get('id'):(float(n.get('lon')),float(n.get('lat'))) for n in r.findall('node')};features=[]
for w in r.findall('way'):
 tags={t.get('k'):t.get('v') for t in w.findall('tag')};refs=[n.get('ref') for n in w.findall('nd')];pts=[xy(nodes[x]) for x in refs if x in nodes]
 if len(pts)<2:continue
 g=Polygon(pts) if refs[0]==refs[-1] and len(pts)>3 else LineString(pts)
 if not g.is_valid:g=g.buffer(0)
 if not g.is_empty:features.append((int(w.get('id')),tags,g,w.get('timestamp')))
museum=shape(meta['museum_complex_footprint']);platforms=unary_union([g for id,t,g,dt in features if id in meta['tram_platform_way_ids']]);requested=museum.convex_hull.buffer(100).union(platforms.convex_hull.buffer(100));working=museum.convex_hull.buffer(110).union(platforms.convex_hull.buffer(110));old=shape(meta['scope_polygon']);roads=unary_union([g for id,t,g,dt in features if t.get('highway') and g.geom_type=='LineString']);rows=[];geometry=[]
for id,t,g,dt in features:
 if 'building' not in t or id in meta['museum_building_way_ids'] or not g.intersects(working):continue
 center=g.centroid;vp=nearest_points(roads,center)[0];lon,lat=ll(vp.coords[0]);c_lon,c_lat=ll(center.coords[0]);heading=math.degrees(math.atan2(center.x-vp.x,center.y-vp.y))%360
 row={'osm_way_id':id,'name':t.get('name',''),'in_previous_model_scope':g.intersects(old),'within_requested_100m_scope':g.intersects(requested),'plan_source':'OpenStreetMap','source_geometry_timestamp':dt,'center_lon_lat':[c_lon,c_lat],'height_m':t.get('height'),'levels':t.get('building:levels'),'facade_reference_status':'NOT_VERIFIED','geometry_status':'mapped footprint, estimated elevation and repeated facade placeholders in current review','street_view_status':'PROPOSED_LINK_NOT_VISITED','street_view_url':f'https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={lat:.7f},{lon:.7f}&heading={heading:.1f}&pitch=0&fov=80','map_url':f'https://www.google.com/maps/search/?api=1&query={c_lat:.7f},{c_lon:.7f}'}
 rows.append(row);geometry.append({'type':'Feature','id':id,'properties':row,'geometry':mapping(g)})
summary={'updated':'2026-10-26','user_acceptance':'Exact visible appearance, interiors and street/building detail required; geometric coverage alone is insufficient','tram_target':'Current white/orange PT8, explicitly confirmed by user','required_context':'100m in every direction around museum AND entire tram platform zone','museum_100m_covered_by_current_scope':old.covers(museum.convex_hull.buffer(100)),'station_100m_covered_by_current_scope':old.covers(platforms.convex_hull.buffer(100)),'additional_scope_area_m2':working.difference(old).area,'building_inventory_count':len(rows),'building_facades_fully_verified':0,'browser_status':'SSD reconnected; live signed-in Google Maps review captured one interior panorama and dated street views/videos. Complete street/interior coverage remains unverified.','source_date_limit':'Current-day appearance not established by dated photographs or OSM geometry.'}
(out/'facade-inventory.json').write_text(json.dumps({'summary':summary,'buildings':rows},ensure_ascii=False,indent=2));(out/'facade-inventory.geojson').write_text(json.dumps({'type':'FeatureCollection','features':geometry},ensure_ascii=False));(out/'required-scope.geojson').write_text(json.dumps({'type':'FeatureCollection','features':[{'type':'Feature','properties':{'kind':'requested100'},'geometry':mapping(requested)},{'type':'Feature','properties':{'kind':'working110'},'geometry':mapping(working)},{'type':'Feature','properties':{'kind':'existing'},'geometry':mapping(old)}]}));print(json.dumps(summary,indent=2))
