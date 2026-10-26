import {stripTextures} from './geometry_only_glb.mjs';
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import * as THREE from '../review/walkthrough/node_modules/three/build/three.module.js';
import {GLTFLoader} from '../review/walkthrough/node_modules/three/examples/jsm/loaders/GLTFLoader.js';
import {Octree} from '../review/walkthrough/collision-octree.js';
import {Capsule} from '../review/walkthrough/node_modules/three/examples/jsm/math/Capsule.js';
globalThis.ProgressEvent=class{constructor(type,init={}){this.type=type;Object.assign(this,init);}};
const ids=['part00','part01','part02','part03','part04','part05','part06','part07','part08'],root=new THREE.Group(),visibleRoot=new THREE.Group(),hashes={};let colliders=0;
for(const id of ids){
 const b=await fs.readFile(new URL('../review/walkthrough/'+id+'.glb',import.meta.url));hashes[id]=crypto.createHash('sha256').update(b).digest('hex');
 const n=b.readUInt32LE(12),j=JSON.parse(b.subarray(20,20+n).toString());stripTextures(j,b,28+n);
 const g=await new Promise((res,rej)=>new GLTFLoader().parse(JSON.stringify(j),'',res,rej));g.scene.updateMatrixWorld(true);
 g.scene.traverse(o=>{
  if(!o.isMesh||o.name.startsWith('NAV_Boundary_')||ids.includes(o.userData.temporary_until))return;
  const copy=()=>{const m=new THREE.Mesh(o.geometry);o.matrixWorld.decompose(m.position,m.quaternion,m.scale);return m;};
  if(o.userData.collision){root.add(copy());colliders++;}
  if(id==='part03'&&(o.userData.collision||!o.userData.review_hidden))visibleRoot.add(copy());
 });
}
root.updateMatrixWorld(true);visibleRoot.updateMatrixWorld(true);const tree=new Octree().fromGraphNode(root),allTree=new Octree().fromGraphNode(visibleRoot);
function mover(start){let p=new THREE.Vector3(start[0],start[2],-start[1]),c=new Capsule(p.clone().add(new THREE.Vector3(0,-1.35,0)),p.clone().add(new THREE.Vector3(0,-.15,0)),.30),v=new THREE.Vector3();return{get pos(){return[c.end.x,-c.end.z,c.end.y+.15];},step(dx,dy){v.x=dx;v.z=-dy;v.y-=18/120;c.translate(v.clone().multiplyScalar(1/120));const h=tree.capsuleIntersect(c);if(h){c.translate(h.normal.clone().multiplyScalar(h.depth+.00001));const d=v.dot(h.normal);if(d<0)v.addScaledVector(h.normal,-d);}return this.pos;}};}
function drive(m,target,seconds=16){for(let i=0;i<seconds*120;i++){const p=m.pos,dx=target[0]-p[0],dy=target[1]-p[1],d=Math.hypot(dx,dy);if(d<.065)return true;m.step(dx/d*2.3,dy/d*2.3);}return false;}
const q=(r,a)=>[-6+r*Math.cos(a*Math.PI/180),23.5+r*Math.sin(a*Math.PI/180)],eye=p=>[...p,-2.55];
const tests=[],failurePoints=[];
function run(name,start,route){let m=mover(start);let passed=true;for(const p of route){if(!drive(m,p)){failurePoints.push({name,target:p,end:m.pos});passed=false;break;}}tests.push({test:name,passed:passed&&Math.abs(m.pos[2]+2.55)<.08,end:m.pos});return m;}
const entry=[[33,15],[33,20.5],[33.2,22.9],q(40.2,2),q(40.2,7),q(40.2,14),q(40.2,20)];
run('map_hall_to_archive_documents',[33,8,-2.55],entry);
const transition=[q(38.4,22),q(38.2,25),q(35.2,28),q(35.2,32.8)];
run('archives_to_round_menswear',eye(q(40.2,20)),transition);
const inner=[];for(let a=33;a<=60;a+=1.5)inner.push(q(35.2,a));
run('inner_route_both_round_cases_and_sculpture',eye(q(35.2,32.8)),inner);
const outer=[q(39.7,60)];for(let a=59;a>=44;a-=1)outer.push(q(40.05,a));outer.push(q(40.1,42));for(let a=41;a>=27;a-=1)outer.push(q(40.15,a));
run('outer_route_cannon_and_uniforms',eye(q(35.2,60)),outer);
run('return_from_uniforms_to_map_hall',eye(q(40.15,27)),[q(38.2,25),q(38.4,22),q(40.2,20),q(40.2,14),q(40.2,7),q(40.2,2),[33.2,22.9],[33,20.5],[33,15],[33,8]]);
// Physical barriers must stop the walking capsule at the original curved/round glass.
let m=mover(eye(q(40.1,29)));drive(m,q(44,29),4);let p=m.pos;tests.push({test:'uniform_case_glass_blocks_entry',passed:Math.hypot(p[0]+6,p[1]-23.5)<41.75,end:p});
m=mover(eye(q(35.2,52)));drive(m,q(37.6,52),4);p=m.pos;let wc=q(37.6,52);tests.push({test:'round_case_glass_blocks_entry',passed:Math.hypot(p[0]-wc[0],p[1]-wc[1])>1.95,end:p});
// Test visible geometry, not only the collider subset, along every route and review viewpoint.
const segments=[[...entry.slice(3),...transition,...inner],outer];const samples=[];
for(const path of segments)for(let i=1;i<path.length;i++){const a=path[i-1],b=path[i],n=Math.ceil(Math.hypot(b[0]-a[0],b[1]-a[1])/.30);for(let j=0;j<n;j++)samples.push([a[0]+(b[0]-a[0])*j/n,a[1]+(b[1]-a[1])*j/n]);}
const views=JSON.parse(await fs.readFile(new URL('../review/walkthrough/part03-views.json',import.meta.url),'utf8'));
for(const v of views)samples.push(v.position.slice(0,2));
const obstructions=[];for(const [x,y] of samples){const c=new Capsule(new THREE.Vector3(x,-3.70,-y),new THREE.Vector3(x,-2.70,-y),.30);const h=allTree.capsuleIntersect(c);if(h&&h.depth>.01)obstructions.push({x,y,depth:h.depth});}
const clearance={passed:obstructions.length===0,scope:'All visible part03 geometry and colliders; 0.2–1.8m torso/head envelope along circulation routes and all review viewpoints',samples:samples.length,obstructions,glb_sha256:hashes.part03};
const report={passed:tests.every(t=>t.passed),colliders,tests,failurePoints,glb_sha256:hashes};
await fs.writeFile(new URL('../review/qa/part03-navigation.json',import.meta.url),JSON.stringify(report,null,2));await fs.writeFile(new URL('../review/qa/part03-clearance.json',import.meta.url),JSON.stringify(clearance,null,2));
console.log(JSON.stringify({navigation:report,clearance},null,2));if(!report.passed||!clearance.passed)process.exitCode=1;
