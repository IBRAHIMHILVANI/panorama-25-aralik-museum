import {stripTextures} from './geometry_only_glb.mjs';
import fs from 'node:fs/promises';
import * as THREE from '../review/walkthrough/node_modules/three/build/three.module.js';
import {GLTFLoader} from '../review/walkthrough/node_modules/three/examples/jsm/loaders/GLTFLoader.js';
import {Octree} from '../review/walkthrough/collision-octree.js';
import {Capsule} from '../review/walkthrough/node_modules/three/examples/jsm/math/Capsule.js';
globalThis.ProgressEvent=class{constructor(type,init={}){this.type=type;Object.assign(this,init);}};
const b=await fs.readFile(new URL('../review/walkthrough/part02.glb',import.meta.url));const n=b.readUInt32LE(12),j=JSON.parse(b.subarray(20,20+n).toString());
stripTextures(j,b,28+n);
const g=await new Promise((res,rej)=>new GLTFLoader().parse(JSON.stringify(j),'',res,rej));g.scene.updateMatrixWorld(true);
const stairs=new THREE.Box3(),columns=[],collisionRoot=new THREE.Group();let ramp;
g.scene.traverse(o=>{if(!o.isMesh)return;if(/^Atrium_Stair_Tread_|^Stair_Parapet_|^Stair_Timber_Rail_|^Stair_Upper_Landing/.test(o.name))stairs.union(new THREE.Box3().setFromObject(o));if(/^Atrium_Column_/.test(o.name))columns.push(o);if(o.name==='NAV_Atrium_Stair_Incline')ramp=o;if(o.userData.collision||!o.userData.review_hidden){const m=new THREE.Mesh(o.geometry);o.matrixWorld.decompose(m.position,m.quaternion,m.scale);collisionRoot.add(m);}});
const details=columns.map(o=>{const bb=new THREE.Box3().setFromObject(o);const dx=Math.max(stairs.min.x-bb.max.x,bb.min.x-stairs.max.x,0),dz=Math.max(stairs.min.z-bb.max.z,bb.min.z-stairs.max.z,0);return{name:o.name,intersects_stair_envelope:bb.intersectsBox(stairs),horizontal_clearance_m:Math.hypot(dx,dz)};});
collisionRoot.updateMatrixWorld(true);const tree=new Octree().fromGraphNode(collisionRoot);const ray=new THREE.Raycaster();const obstructions=[];let samples=0;
for(const x of [40.5,41.1,41.7])for(let y=1.8;y<=12.6;y+=.4){ray.set(new THREE.Vector3(x,20,-y),new THREE.Vector3(0,-1,0));const hits=ray.intersectObject(ramp,false);if(!hits.length)throw Error('Missing ramp intersection');const f=hits[0].point;const capsule=new Capsule(f.clone().add(new THREE.Vector3(0,.5002,0)),f.clone().add(new THREE.Vector3(0,1.5002,0)),.30);const h=tree.capsuleIntersect(capsule);samples++;if(h&&h.depth>.01)obstructions.push({x,y,depth:h.depth,normal:h.normal.toArray()});}
const report={passed:details.every(c=>!c.intersects_stair_envelope&&c.horizontal_clearance_m>.12)&&obstructions.length===0,scope:'All visible geometry plus collision helpers; torso and head from 0.2m to 1.8m above the ramp surface',columns:details,standing_clearance_samples:samples,obstructions};
const suffix=process.argv[2]==='before'?'before':'after';await fs.writeFile(new URL('../review/qa/part02-stair-clearance-'+suffix+'.json',import.meta.url),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));if(!report.passed)process.exitCode=1;
