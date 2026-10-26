// Exercise the actual exported collision triangles, independently of the UI.
import fs from 'node:fs/promises';
import * as THREE from '../review/walkthrough/node_modules/three/build/three.module.js';
import {GLTFLoader} from '../review/walkthrough/node_modules/three/examples/jsm/loaders/GLTFLoader.js';
import {Octree} from '../review/walkthrough/collision-octree.js';
import {Capsule} from '../review/walkthrough/node_modules/three/examples/jsm/math/Capsule.js';
const buf=await fs.readFile(new URL('../review/walkthrough/part01.glb',import.meta.url));
const gltf=await new Promise((resolve,reject)=>new GLTFLoader().parse(buf.buffer.slice(buf.byteOffset,buf.byteOffset+buf.byteLength),'',resolve,reject));
const root=new THREE.Group();gltf.scene.updateMatrixWorld(true);let colliders=0;
gltf.scene.traverse(o=>{if(!o.isMesh||!o.userData.collision)return;const m=new THREE.Mesh(o.geometry);o.matrixWorld.decompose(m.position,m.quaternion,m.scale);root.add(m);colliders++;});
root.updateMatrixWorld(true);const tree=new Octree().fromGraphNode(root);
function author(v){return new THREE.Vector3(v[0],v[2],-v[1]);}
function mover(start){let p=author(start),capsule=new Capsule(p.clone().add(new THREE.Vector3(0,-1.35,0)),p.clone().add(new THREE.Vector3(0,-.15,0)),.3),vel=new THREE.Vector3();
 return {get position(){p=capsule.end.clone().add(new THREE.Vector3(0,.15,0));return [p.x,-p.z,p.y];},step(dx,dy,dt=1/120){vel.x=dx;vel.z=-dy;vel.y-=18*dt;capsule.translate(vel.clone().multiplyScalar(dt));const hit=tree.capsuleIntersect(capsule);if(hit){capsule.translate(hit.normal.clone().multiplyScalar(hit.depth+.00001));const k=vel.dot(hit.normal);if(k<0)vel.addScaledVector(hit.normal,-k);}return this.position;}};}
function drive(m,target,seconds=30){for(let i=0;i<seconds*120;i++){const p=m.position;const dx=target[0]-p[0],dy=target[1]-p[1],l=Math.hypot(dx,dy);if(l<.07)return true;m.step(dx/l*2.5,dy/l*2.5);}return false;}
const results=[];
let m=mover([0,-25,.05]);let ok=drive(m,[0,15]);results.push({test:'street_to_courtyard_through_steps_and_portal',passed:ok&&Math.abs(m.position[2]-1.65)<.05,end:m.position});
ok=drive(m,[17.9,13.4]);ok=drive(m,[23.2,11.1],8)&&ok;results.push({test:'courtyard_through_open_door',passed:ok,end:m.position});
m=mover([0,-8,1.65]);for(let i=0;i<600;i++)m.step(2.5,0);results.push({test:'right_passage_wall_blocks_player',passed:m.position[0]<4.1&&m.position[0]>3.5,end:m.position});
m=mover([0,-8,1.65]);for(let i=0;i<600;i++)m.step(-2.5,0);results.push({test:'left_glazing_blocks_player',passed:m.position[0]>-4.1&&m.position[0]<-3.4,end:m.position});
m=mover([0,14,1.65]);ok=drive(m,[0,-25]);results.push({test:'return_through_portal_and_down_steps',passed:ok&&Math.abs(m.position[2]-.05)<.05,end:m.position});
const report={colliders,passed:results.every(r=>r.passed),tests:results};await fs.mkdir(new URL('../review/qa/',import.meta.url),{recursive:true});await fs.writeFile(new URL('../review/qa/part01-navigation.json',import.meta.url),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));if(!report.passed)process.exitCode=1;
