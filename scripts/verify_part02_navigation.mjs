import {stripTextures} from './geometry_only_glb.mjs';
import fs from 'node:fs/promises';
import * as THREE from '../review/walkthrough/node_modules/three/build/three.module.js';
import {GLTFLoader} from '../review/walkthrough/node_modules/three/examples/jsm/loaders/GLTFLoader.js';
import {Octree} from '../review/walkthrough/collision-octree.js';
import {Capsule} from '../review/walkthrough/node_modules/three/examples/jsm/math/Capsule.js';
globalThis.ProgressEvent=class {constructor(type,init={}){this.type=type;Object.assign(this,init);}};
const root=new THREE.Group();let colliders=0;
const ids=['part00','part01','part02','part03','part04','part05','part06','part07','part08'];for(const id of ids){
 const b=await fs.readFile(new URL('../review/walkthrough/'+id+'.glb',import.meta.url));const n=b.readUInt32LE(12),j=JSON.parse(b.subarray(20,20+n).toString());const bin=b.subarray(28+n);
 stripTextures(j,b,28+n);
 const g=await new Promise((res,rej)=>new GLTFLoader().parse(JSON.stringify(j),'',res,rej));g.scene.updateMatrixWorld(true);
 g.scene.traverse(o=>{if(!o.isMesh||!o.userData.collision||o.name.startsWith('NAV_Boundary_')||ids.includes(o.userData.temporary_until))return;const m=new THREE.Mesh(o.geometry);o.matrixWorld.decompose(m.position,m.quaternion,m.scale);root.add(m);colliders++;});
}
root.updateMatrixWorld(true);const tree=new Octree().fromGraphNode(root);
function mover(start){let p=new THREE.Vector3(start[0],start[2],-start[1]),c=new Capsule(p.clone().add(new THREE.Vector3(0,-1.35,0)),p.clone().add(new THREE.Vector3(0,-.15,0)),.30),v=new THREE.Vector3();return {get pos(){return[c.end.x,-c.end.z,c.end.y+.15];},step(dx,dy){v.x=dx;v.z=-dy;v.y-=18/120;c.translate(v.clone().multiplyScalar(1/120));const h=tree.capsuleIntersect(c);if(h){c.translate(h.normal.clone().multiplyScalar(h.depth+.00001));const d=v.dot(h.normal);if(d<0)v.addScaledVector(h.normal,-d);}return this.pos;}};}
function drive(m,target,seconds=20){for(let i=0;i<seconds*120;i++){const p=m.pos,dx=target[0]-p[0],dy=target[1]-p[1],d=Math.hypot(dx,dy);if(d<.065)return true;m.step(dx/d*2.3,dy/d*2.3);}return false;}
const tests=[];let m=mover([17.9,13.4,1.65]);let ok=true;
for(const p of [[23.2,11.1],[26,11],[27.3,12.7],[30,14.8],[33,15.4],[39,14.7],[41.1,13.8]]){if(!drive(m,p)){tests.push({test:'route_waypoint',target:p,passed:false,end:m.pos});ok=false;break;}}
tests.push({test:'courtyard_to_atrium_and_stair_top',passed:ok,end:m.pos});
m=mover([41.1,13.8,1.65]);ok=drive(m,[41.1,.85]);tests.push({test:'descend_stair_to_lower_map_hall',passed:ok&&Math.abs(m.pos[2]+2.55)<.08,end:m.pos});
ok=drive(m,[38,1]);ok=drive(m,[33,8])&&ok;tests.push({test:'walk_across_map_hall',passed:ok&&Math.abs(m.pos[2]+2.55)<.08,end:m.pos});
m=mover([33,8,-2.55]);ok=drive(m,[38,1]);ok=drive(m,[41.1,.85])&&ok;ok=drive(m,[41.1,13.8])&&ok;tests.push({test:'return_up_stair',passed:ok&&Math.abs(m.pos[2]-1.65)<.08,end:m.pos});
m=mover([33,14.5,1.65]);for(let i=0;i<600;i++)m.step(0,-2.3);tests.push({test:'balcony_glass_prevents_fall',passed:m.pos[1]>13.7&&m.pos[2]>1.5,end:m.pos});
const report={colliders,passed:tests.every(t=>t.passed),tests};await fs.writeFile(new URL('../review/qa/part02-navigation.json',import.meta.url),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));if(!report.passed)process.exitCode=1;
