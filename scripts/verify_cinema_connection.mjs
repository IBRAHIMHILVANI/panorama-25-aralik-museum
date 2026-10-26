// Integrated exported-geometry QA. Author coordinates: X/Y plan, Z elevation.
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import * as THREE from '../review/walkthrough/node_modules/three/build/three.module.js';
import { GLTFLoader } from '../review/walkthrough/node_modules/three/examples/jsm/loaders/GLTFLoader.js';
import { Capsule } from '../review/walkthrough/node_modules/three/examples/jsm/math/Capsule.js';
import { Octree } from '../review/walkthrough/collision-octree.js';
import { stripTextures } from './geometry_only_glb.mjs';
globalThis.ProgressEvent=class { constructor(type,init={}) { this.type=type;Object.assign(this,init); } };
const floorZ=-4.2,radius=.30,eyeHeight=1.65;
const root=new THREE.Group(),visible=new THREE.Group(),meshes=[],inputs=[];
for(const id of ['part00','part02','part08']) {
 const file=new URL(`../review/walkthrough/${id}.glb`,import.meta.url),b=await fs.readFile(file),stat=await fs.stat(file);
 inputs.push({part:id,bytes:b.length,mtime:stat.mtime.toISOString(),sha256:crypto.createHash('sha256').update(b).digest('hex')});
 const n=b.readUInt32LE(12),j=JSON.parse(b.subarray(20,20+n));stripTextures(j,b,28+n);
 const gltf=await new Promise((resolve,reject)=>new GLTFLoader().parse(JSON.stringify(j),'',resolve,reject));gltf.scene.updateMatrixWorld(true);
 gltf.scene.traverse(o=>{
  if(!o.isMesh || o.name.startsWith('NAV_Boundary_') || ['part00','part02','part08'].includes(o.userData.temporary_until))return;
  const copy=()=>{const m=new THREE.Mesh(o.geometry,new THREE.MeshBasicMaterial({side:THREE.DoubleSide}));m.name=`${id}/${o.name}`;o.matrixWorld.decompose(m.position,m.quaternion,m.scale);return m;};
  if(o.userData.collision)root.add(copy());
  if(!o.userData.review_hidden||o.userData.collision){const m=copy();visible.add(m);meshes.push(m);}
 });
}
root.updateMatrixWorld(true);visible.updateMatrixWorld(true);
const tree=new Octree().fromGraphNode(root),all=new Octree().fromGraphNode(visible);
const bounds=meshes.map(m=>({mesh:m,box:new THREE.Box3().setFromObject(m),tree:null}));
const route=[[41.1,.25],[42.9,.25],[43.5,2.4],[44.5,2.4],[45.3,2.4],[45.3,.11],[48,.11],[51.5,.11]];
const samples=[],tests=[];
function walk(name,points) {
 const p=new THREE.Vector3(points[0][0],floorZ+eyeHeight,-points[0][1]);
 const c=new Capsule(p.clone().add(new THREE.Vector3(0,-1.35,0)),p.clone().add(new THREE.Vector3(0,-.15,0)),radius),v=new THREE.Vector3(),waypoints=[];
 const position=()=>[c.end.x,-c.end.z,c.end.y+.15];let passed=true,maxFloorError=0;
 for(const target of points.slice(1)) {
  let reached=false;
  for(let i=0;i<2400;i++) {
   const current=position(),dx=target[0]-current[0],dy=target[1]-current[1],distance=Math.hypot(dx,dy);
   maxFloorError=Math.max(maxFloorError,Math.abs(current[2]-eyeHeight-floorZ));
   if(i%12===0)samples.push({route:name,position:current});
   if(distance<.065){reached=true;break;}
   v.x=dx/distance*2.2;v.z=-dy/distance*2.2;v.y-=18/120;c.translate(v.clone().multiplyScalar(1/120));
   const hit=tree.capsuleIntersect(c);if(hit){c.translate(hit.normal.clone().multiplyScalar(hit.depth+.00001));const vn=v.dot(hit.normal);if(vn<0)v.addScaledVector(hit.normal,-vn);}
   if(Math.abs(position()[2]-eyeHeight-floorZ)>.30)break;
  }
  waypoints.push({target,reached,end:position()});if(!reached){passed=false;break;}
 }
 tests.push({name,passed:passed&&maxFloorError<.08,max_floor_error_m:maxFloorError,waypoints});
}
walk('stair_bottom_to_cinema_rear',route);walk('cinema_rear_to_stair_bottom',[...route].reverse());
// Also sample the intended straight route densely, independent of collision sliding.
for(let k=1;k<route.length;k++){
 const a=route[k-1],b=route[k],steps=Math.ceil(Math.hypot(b[0]-a[0],b[1]-a[1])/.08);
 for(let i=0;i<=steps;i++){const t=i/steps;samples.push({route:'intended_route',position:[a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,floorZ+eyeHeight]});}
}
const obstructions=[],floorFailures=[],ray=new THREE.Raycaster(),contacts=new Map();
for(const sample of samples){
 const [x,y,eye]=sample.position,base=eye-eyeHeight;
 // Same 0.2–1.8m torso/head clearance and 0.01m tolerance as prior part02 QA.
 const c=new Capsule(new THREE.Vector3(x,base+.5,-y),new THREE.Vector3(x,base+1.5,-y),radius),hit=all.capsuleIntersect(c);
 if(hit&&hit.depth>.01){
  const box=new THREE.Box3().setFromPoints([c.start,c.end]).expandByScalar(radius),objects=[];
  for(const item of bounds){if(!box.intersectsBox(item.box))continue;item.tree??=new Octree().fromGraphNode(item.mesh);const h=item.tree.capsuleIntersect(c);if(h&&h.depth>.01){objects.push({name:item.mesh.name,depth:h.depth});const previous=contacts.get(item.mesh.name);if(!previous||previous.depth<h.depth)contacts.set(item.mesh.name,{name:item.mesh.name,depth:h.depth,position:sample.position});}}
  obstructions.push({...sample,depth:hit.depth,objects});
 }
 ray.set(new THREE.Vector3(x,floorZ+.15,-y),new THREE.Vector3(0,-1,0));ray.far=.35;
 const support=ray.intersectObjects(root.children,false)[0];
 if(!support||Math.abs(support.point.y-floorZ)>.04)floorFailures.push({...sample,support:support?{name:support.object.name,z:support.point.y}:null});
}
const report={generated_at:new Date().toISOString(),scope:'Integrated exported part00 + part02 + part08: stair bottom, around lower parapet, cinema doorway, front cross aisle, central aisle and return. No surveyed dimensional accuracy claim.',user_observation:'Cinema beside the stair on the right; interpreted from map-hall viewpoint.',estimated_geometry:'Origin [44.5,0.11,-4.2], yaw -pi/2, 0.8m doorway, room dimensions and connector are estimates.',parameters:{capsule_radius_m:radius,eye_height_m:eyeHeight,body_clearance_range_m:[.2,1.8],body_penetration_tolerance_m:.01,route_spacing_m:.08,floor_height_m:floorZ},inputs,passed:tests.every(t=>t.passed)&&!obstructions.length&&!floorFailures.length,tests,body_samples:samples.length,obstructed_samples:obstructions.length,obstruction_objects:[...contacts.values()],obstructions,floor_failures:floorFailures};
await fs.mkdir(new URL('../review/qa/',import.meta.url),{recursive:true});await fs.writeFile(new URL('../review/qa/cinema-connection-navigation.json',import.meta.url),JSON.stringify(report,null,2));
console.log(JSON.stringify({...report,obstructions:obstructions.slice(0,4),floor_failures:floorFailures.slice(0,4)},null,2));if(!report.passed)process.exitCode=1;
