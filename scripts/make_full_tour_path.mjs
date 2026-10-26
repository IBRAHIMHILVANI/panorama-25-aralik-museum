// One uninterrupted simulated walk through the actual exported museum.
// Re-run after final GLB exports. Never interpolate shortcuts between waypoints.
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import * as THREE from '../review/walkthrough/node_modules/three/build/three.module.js';
import {GLTFLoader} from '../review/walkthrough/node_modules/three/examples/jsm/loaders/GLTFLoader.js';
import {Capsule} from '../review/walkthrough/node_modules/three/examples/jsm/math/Capsule.js';
import {Octree} from '../review/walkthrough/collision-octree.js';
import {stripTextures} from './geometry_only_glb.mjs';
globalThis.ProgressEvent=class {constructor(type,init={}){this.type=type;Object.assign(this,init);}};
const base=new URL('../',import.meta.url),ids=Array.from({length:9},(_,i)=>`part0${i}`),hashes={},groups={},root=new THREE.Group(),views={};
const speed=1.8,dt=1/120,fps=20,radius=.30,eyeHeight=1.65;
if(process.argv.includes('--check-hashes')){
 const saved=JSON.parse(await fs.readFile(new URL('reconstruction/full-tour-path-2026-10-26.json',base),'utf8')),changed=[];
 for(const id of ids){const current=crypto.createHash('sha256').update(await fs.readFile(new URL(`review/walkthrough/${id}.glb`,base))).digest('hex');if(current!==saved.validation.glb_sha256[id])changed.push({part:id,tested:saved.validation.glb_sha256[id],current});}
 const result={checked_at:new Date().toISOString(),passed:saved.validation.passed&&changed.length===0,changed};await fs.writeFile(new URL('review/qa/full-tour-path-hash-recheck.json',base),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));process.exit(result.passed?0:1);
}
for(const id of ids){
 const b=await fs.readFile(new URL(`review/walkthrough/${id}.glb`,base)),n=b.readUInt32LE(12),j=JSON.parse(b.subarray(20,20+n));hashes[id]=crypto.createHash('sha256').update(b).digest('hex');stripTextures(j,b,28+n);
 const g=await new Promise((resolve,reject)=>new GLTFLoader().parse(JSON.stringify(j),'',resolve,reject));g.scene.updateMatrixWorld(true);groups[id]=new THREE.Group();
 g.scene.traverse(o=>{if(!o.isMesh||o.name.startsWith('NAV_Boundary_')||ids.includes(o.userData.temporary_until))return;
  const copy=()=>{const m=new THREE.Mesh(o.geometry);m.name=`${id}/${o.name}`;o.matrixWorld.decompose(m.position,m.quaternion,m.scale);return m;};
  if(o.userData.collision)root.add(copy());if(o.userData.collision||!o.userData.review_hidden)groups[id].add(copy());
 });
 views[id]=JSON.parse(await fs.readFile(new URL(`review/walkthrough/${id}-views.json`,base),'utf8'));
 console.log('Loaded',id);
}
root.updateMatrixWorld(true);const tree=new Octree().fromGraphNode(root);
if(process.argv.includes('--diagnose')){
 const prior=JSON.parse(await fs.readFile(new URL('review/qa/full-tour-path-validation.json',base),'utf8'));
 const points=[...prior.body_failures.slice(0,4).map(x=>x.position),...prior.failed_waypoints.slice(0,1).map(x=>x.end),...prior.floor_failures.slice(0,1).map(x=>x.position)],report=[];
 for(const pos of points){const [x,y,z]=pos,c=new Capsule(new THREE.Vector3(x,z-eyeHeight+.5,-y),new THREE.Vector3(x,z-eyeHeight+1.5,-y),radius),bb=new THREE.Box3().setFromPoints([c.start,c.end]).expandByScalar(radius),hits=[];
  for(const id of ids)for(const mesh of groups[id].children){if(!bb.intersectsBox(new THREE.Box3().setFromObject(mesh)))continue;const h=new Octree().fromGraphNode(mesh).capsuleIntersect(c);if(h&&h.depth>.001)hits.push({name:mesh.name,depth:h.depth});}
  const floors=[];for(const dx of [-.25,0,.25])for(const dy of [-.25,0,.25]){const ray=new THREE.Raycaster(new THREE.Vector3(x+dx,z-eyeHeight+.5,-y-dy),new THREE.Vector3(0,-1,0),0,2);const h=ray.intersectObjects(root.children,false)[0];floors.push({dx,dy,name:h?.object.name,z:h?.point.y,distance:h?.distance});}
  report.push({position:pos,hits,floors});
 }
 await fs.writeFile(new URL('review/qa/full-tour-path-diagnosis.json',base),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));process.exit(0);
}
const note=JSON.parse(await fs.readFile(new URL('reconstruction/part00-notes.json',base),'utf8')),f=note.tram_local_frame;
const tp=(x,y,z=2.6)=>[f.origin_author[0]+Math.cos(f.yaw_author_rad)*x-Math.sin(f.yaw_author_rad)*y,f.origin_author[1]+Math.sin(f.yaw_author_rad)*x+Math.cos(f.yaw_author_rad)*y,f.origin_author[2]+z];
const q=(r,a)=>[-6+r*Math.cos(a*Math.PI/180),23.5+r*Math.sin(a*Math.PI/180)],pan=(r,a)=>[-26+r*Math.cos(a*Math.PI/180),13+r*Math.sin(a*Math.PI/180)],stair=a=>[-29+2.8*Math.cos(a*Math.PI/180),16+2.8*Math.sin(a*Math.PI/180)];
const arc=(fn,r,a,b,step=1)=>{const out=[];for(let t=a;step>0?t<=b:t>=b;t+=step)out.push(fn(r,t));return out;};
const stages=[],waypoints=[];
function stage(id,points,part,source){if(!stages.some(s=>s.id===id))stages.push({id,part,source,first_waypoint:waypoints.length});for(const p of points)waypoints.push({stage:id,part,xy:p.slice(0,2)});return waypoints[waypoints.length-1];}
function pause(w,viewId,seconds=4){const view=views[w.part].find(v=>v.id===viewId);if(!view)throw Error('Missing view '+w.part+'/'+viewId);w.pause_seconds=seconds;w.exhibit_view=viewId;w.exhibit_target=view.target;}
stage('tram_interior_articulation',[9.95,5.2,3.75].map(x=>tp(x,.22)),'part00','verify_part00_navigation: aisle to first articulation');
pause(waypoints.at(-1),'traminterior',3);
stage('tram_interior_return',[5.2,9.95].map(x=>tp(x,.22)),'part00','reverse verified aisle');
stage('tram_door_exit',[tp(10.70,.22),note.tram_door_author_xy,note.platform_exit_author_xy],'part00','aisle-to-open-door join physically checked; verify_part00 exit');
pause(waypoints.at(-1),'station',3);
const street=note.route_author_xy.slice(0,-2).flatMap((p,i)=>i===7?[[32,-52.3],[28.5,-50.9],p]:[p]);
stage('station_to_museum',street,'part00','verify_part00 mapped frontage route; bounded inward detour avoids unsupported curb edge near [30,-52]');
stage('entrance_and_courtyard',[[0,-22],[0,-18],[0,-10],[0,7],[0,12],[0,15]],'part01','verify_part00 entrance and verify_navigation courtyard');
pause(waypoints.at(-1),'courtyard',5);
stage('courtyard_to_atrium',[[17.9,13.4],[23.2,11.1],[26,11],[27.3,12.7],[30,14.8],[33,15.4]],'part02','verify_navigation + verify_part02');
pause(waypoints.at(-1),'redif',4);
stage('atrium_stair',[[39,14.7],[41.1,13.8],[41.1,.85],[41.1,.25]],'part02','verify_part02 stair descent; cinema bottom landing');
const cinema=[[42.9,.25],[43.5,2.4],[44.5,2.4],[45.3,2.4],[45.3,.11],[48,.11],[51.5,.11]];
stage('cinema_entry_and_aisle',cinema,'part08','verify_cinema_connection');pause(waypoints.at(-1),'cinema',7);
stage('cinema_return',[...cinema.slice(0,-1).reverse(),[41.1,.25]],'part08','reverse integrated cinema route');
stage('lower_map_hall',[[39.2,.25],[38,1],[33,8]],'part02','lower map route around parapet toe, keeping .75m from its y1 start');pause(waypoints.at(-1),'mapdetail',6);
stage('archives',[[33,15],[33,20.5],[33.2,22.9],q(40.2,2),q(40.2,7),q(40.2,14),q(40.2,20)],'part03','verify_part03 map-to-archives');pause(waypoints.at(-1),'documents',5);
const outer=[q(39.7,60),...arc(q,40.05,59,44,-1),q(40.1,42),...arc(q,40.15,41,27,-1)];
stage('archives_to_uniforms',[q(38.4,22),q(38.2,25),q(40.15,27)],'part03','reverse verify_part03 uniform-return join');pause(waypoints.at(-1),'uniforms',5);
stage('uniforms_and_artillery',[...outer.slice(0,-1).reverse(),q(35.2,60)],'part03','reverse verified outer route to sculpture and portraits');pause(waypoints.at(-1),'sculpture',4);
stage('portraits_to_redroom',[...arc(q,35.2,61,66),q(35.2,66.5),q(38,66.5),q(43,66.5)],'part04','verify_part04 portraits/redroom');pause(waypoints.at(-1),'redroom',4);
stage('redroom_to_kastel_stair',[q(38,66.5),q(35.2,66.5),...arc(q,35.2,67,74),q(36.8,74),q(38.8,74),q(40,74)],'part04','verify_part04 descend first Kastel stair');
stage('kastel_lower_alcove',[...arc(q,40,75,81),q(43.3,81)],'part04','Kastel lower arc join physically checked; verified alcove');pause(waypoints.at(-1),'stonepanels',4);
stage('kastel_return_ramp',[q(40,81),q(40.8,81),q(40.8,82),q(40.8,83),q(40.25,83),q(38.7,83.02),q(36.9,83.05),q(35.2,83.05)],'part04','outside ramp foot approach; verify_part04 access ramp');
stage('correspondence_gallery',[...arc(q,35.2,84,98),q(40.4,98.3),q(40.4,101.1),q(40.4,103.8),q(36,104),q(35.2,104)],'part04','verify_part04 correspondence/kiosk');pause(waypoints.at(-1),'kiosk',4);
stage('painting_gallery',[q(39.8,105.4),q(40.6,107),q(40.6,108),...arc(q,40.6,109,132)],'part05','verify_part05 painting gallery');pause(waypoints.at(-1),'council',4);
stage('history',[q(39,133),q(39,134.5),q(38,136.4),q(38,138),q(37.7,139)],'part05','history route shifts inward before protruding Community_Cart_Wood; actual geometry checked');pause(waypoints.at(-1),'history',4);
stage('three_dioramas',[q(37.7,140.1),q(37,142),q(35.8,144),...arc(q,35.8,145,163)],'part06','verify_part06 three dioramas');pause(waypoints.at(-1),'ruin',5);
stage('projection_to_panorama_stair',[q(37,165),q(37,167.2),q(37,168),[-40.8,28.8],stair(135)],'part07','verify_part06 projection + verify_part07 entry');
stage('panorama_curved_ascent',[...Array.from({length:36},(_,i)=>stair(140+i*5)),[-25.82,15.22],[-27,16],[-28.25,19.15],pan(7.4,110)],'part07','verify_part07 ascent/upper corridor');
// The whole 360-degree viewing ring, with key exhibit looks at known landmarks.
for(let a=115;a<=470;a+=5){const w=stage('upper_panorama_ring',[pan(7.4,a)],'part07','verify_part07 whole ring');const stops={135:'panorama',185:'rooftops',225:'well',265:'cannon',305:'tank',350:'wagon',390:'hospital',405:'kitchen',440:'medical'};if(stops[a])pause(w,stops[a],a===135?6:4);}
pause(waypoints.at(-1),'panorama',8);
const start=tp(12.1,.22),p=new THREE.Vector3(start[0],start[2],-start[1]),capsule=new Capsule(p.clone().add(new THREE.Vector3(0,-1.35,0)),p.clone().add(new THREE.Vector3(0,-.15,0)),radius),velocity=new THREE.Vector3();
const position=()=>[capsule.end.x,-capsule.end.z,capsule.end.y+.15];
const samples=[],waypointResults=[],pauses=[],failures=[],floorFailures=[];let tick=0,active=waypoints[0],bodyCheckCount=0,totalDistance=0,lastPosition=start;
function record(look=null){const pos=position();const floor=pos[2]-eyeHeight,ray=new THREE.Ray(new THREE.Vector3(pos[0],floor+.15,-pos[1]),new THREE.Vector3(0,-1,0)),support=tree.rayIntersect(ray);if(!support||support.distance>.40)floorFailures.push({t:tick*dt,position:pos,distance:support?support.distance:null,stage:active.stage});samples.push({t:tick*dt,position:pos,stage:active.stage,part:active.part,...(look?{requested_look_target:look}:{}),floor_support_z:support?support.position.y:null});}
function step(dx,dy,look=null){velocity.x=dx;velocity.z=-dy;velocity.y-=18*dt;capsule.translate(velocity.clone().multiplyScalar(dt));const h=tree.capsuleIntersect(capsule);if(h){capsule.translate(h.normal.clone().multiplyScalar(h.depth+.00001));const vn=velocity.dot(h.normal);if(vn<0)velocity.addScaledVector(h.normal,-vn);}tick++;const pos=position();totalDistance+=Math.hypot(...pos.map((v,i)=>v-lastPosition[i]));lastPosition=pos;if(tick%6===0)record(look);}
record(views.part00.find(v=>v.id==='tramcab').target);
for(let k=0;k<waypoints.length;k++){
 active=waypoints[k];const before=position(),initialDistance=Math.hypot(active.xy[0]-before[0],active.xy[1]-before[1]);let reached=false;
 const budget=Math.ceil((initialDistance/speed+18)*120);let stalled=0,lastProgress=Infinity;
 for(let i=0;i<budget;i++){
  const pos=position(),dx=active.xy[0]-pos[0],dy=active.xy[1]-pos[1],d=Math.hypot(dx,dy);
  if(d<.055){reached=true;break;}
  step(dx/d*speed,dy/d*speed);
  if(i%120===0){if(lastProgress-d<.02)stalled++;else stalled=0;lastProgress=d;if(stalled>=5)break;}
  if(position()[2]<-10)break;
 }
 waypointResults.push({index:k,stage:active.stage,target:active.xy,reached,t:tick*dt,end:position()});
 if(!reached){failures.push(waypointResults.at(-1));console.log('BLOCKED',JSON.stringify(failures.at(-1)));break;}
 if(active.pause_seconds){const begin=tick*dt;for(let i=0;i<active.pause_seconds*120;i++)step(0,0,active.exhibit_target);pauses.push({start:begin,end:tick*dt,view:active.exhibit_view,part:active.part,target:active.exhibit_target,position:position()});}
 if(k%25===0)console.log('Waypoint',k,'/',waypoints.length,'time',Math.round(tick*dt));
}
// Visible-body checks are performed part-by-part, avoiding one enormous combined
// decorative-mesh octree. Every sample inside each part's bounds is tested.
const bodyFailures=[];
for(const id of ids){
 const group=groups[id];group.updateMatrixWorld(true);const bounds=new THREE.Box3().setFromObject(group),visibleTree=new Octree().fromGraphNode(group);
 for(let i=0;i<samples.length;i+=5){const sample=samples[i],[x,y,z]=sample.position,c=new Capsule(new THREE.Vector3(x,z-eyeHeight+.5,-y),new THREE.Vector3(x,z-eyeHeight+1.5,-y),radius);const bb=new THREE.Box3().setFromPoints([c.start,c.end]).expandByScalar(radius);if(!bb.intersectsBox(bounds))continue;bodyCheckCount++;const hit=visibleTree.capsuleIntersect(c);if(hit&&hit.depth>.01)bodyFailures.push({part:id,t:sample.t,position:sample.position,stage:sample.stage,depth:hit.depth,normal:hit.normal.toArray()});}
 visibleTree.clear();console.log('Clearance',id,'failures',bodyFailures.filter(x=>x.part===id).length);
}
// Camera orientation only is smoothed. Eye positions remain the physics output.
let yaw=null,pitch=0;const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
for(let i=0;i<samples.length;i++){
 const s=samples[i],next=samples[Math.min(samples.length-1,i+24)],target=s.requested_look_target||next.position;let dx=target[0]-s.position[0],dy=target[1]-s.position[1],dz=target[2]-s.position[2];
 if(Math.hypot(dx,dy)<.005){dx=Math.cos(yaw??0);dy=Math.sin(yaw??0);dz=0;}
 const desiredYaw=Math.atan2(dy,dx),desiredPitch=clamp(Math.atan2(dz,Math.hypot(dx,dy)),-Math.PI/3,Math.PI/3);if(yaw===null)yaw=desiredYaw;
 const diff=Math.atan2(Math.sin(desiredYaw-yaw),Math.cos(desiredYaw-yaw));yaw+=clamp(diff,-Math.PI/3/fps,Math.PI/3/fps);pitch+=clamp(desiredPitch-pitch,-Math.PI/4/fps,Math.PI/4/fps);
 s.look_target=[s.position[0]+5*Math.cos(pitch)*Math.cos(yaw),s.position[1]+5*Math.cos(pitch)*Math.sin(yaw),s.position[2]+5*Math.sin(pitch)];delete s.requested_look_target;
}
const passed=!failures.length&&!floorFailures.length&&!bodyFailures.length&&waypointResults.length===waypoints.length;
const validation={passed,waypoints_requested:waypoints.length,waypoints_reached:waypointResults.filter(w=>w.reached).length,failed_waypoints:failures,floor_samples:samples.length,floor_failures:floorFailures,body_clearance_samples:bodyCheckCount,body_failures:bodyFailures,glb_sha256:hashes};
const output={schema:'museum-continuous-tour-v1',created_at:new Date().toISOString(),coordinate_system:'author metres, Z up; position is camera eye',physics:{integration_hz:120,output_fps:fps,walk_speed_m_s:speed,eye_height_m:eyeHeight,capsule_radius_m:radius,gravity_m_s2:18,body_clearance_tolerance_m:.01},continuous:true,initial_position:start,duration_seconds:tick*dt,distance_m:totalDistance,stages:[...new Map(stages.map(s=>[s.id,s])).values()],waypoints,waypoint_results:waypointResults,pauses,samples,validation,rendering_guidance:'Use sampled eye positions without spatial smoothing or cross-corner shortcuts; interpolate only adjacent 0.05-second samples. look_target is already angular-rate-limited. On failed validation this is a partial blocked route, never a full approved tour. Re-run generator after final GLB exports.'};
await fs.writeFile(new URL('reconstruction/full-tour-path-2026-10-26.json',base),JSON.stringify(output));
await fs.writeFile(new URL('review/qa/full-tour-path-validation.json',base),JSON.stringify({...validation,duration_seconds:tick*dt,distance_m:totalDistance,sample_count:samples.length,pauses:pauses.length},null,2));
console.log(JSON.stringify({passed,duration_seconds:tick*dt,distance_m:totalDistance,samples:samples.length,waypoints:waypointResults.length,failed_waypoints:failures,floor_failures:floorFailures.slice(0,3),body_failures:bodyFailures.slice(0,8)},null,2));if(!passed)process.exitCode=1;
