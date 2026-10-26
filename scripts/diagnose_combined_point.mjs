import {stripTextures} from './geometry_only_glb.mjs';
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import * as THREE from '../review/walkthrough/node_modules/three/build/three.module.js';
import {GLTFLoader} from '../review/walkthrough/node_modules/three/examples/jsm/loaders/GLTFLoader.js';
import {Octree} from '../review/walkthrough/collision-octree.js';
import {Capsule} from '../review/walkthrough/node_modules/three/examples/jsm/math/Capsule.js';
globalThis.ProgressEvent=class{constructor(type,init={}){this.type=type;Object.assign(this,init);}};
const ids=['part00','part01','part02','part03','part04','part05','part06','part07'],root=new THREE.Group(),all=new THREE.Group(),floors=[],hashes={};let colliders=0;
for(const id of ids){const b=await fs.readFile(new URL('../review/walkthrough/'+id+'.glb',import.meta.url));hashes[id]=crypto.createHash('sha256').update(b).digest('hex');const n=b.readUInt32LE(12),j=JSON.parse(b.subarray(20,20+n).toString());stripTextures(j,b,28+n);const g=await new Promise((res,rej)=>new GLTFLoader().parse(JSON.stringify(j),'',res,rej));g.scene.updateMatrixWorld(true);g.scene.traverse(o=>{if(!o.isMesh||o.name.startsWith('NAV_Boundary_')||ids.includes(o.userData.temporary_until))return;const copy=()=>{const m=new THREE.Mesh(o.geometry);m.name=o.name;o.matrixWorld.decompose(m.position,m.quaternion,m.scale);return m;};if(o.userData.collision){root.add(copy());colliders++;}if(id==='part07'){if(o.userData.collision||!o.userData.review_hidden)all.add(copy());if(o.userData.collision&&/Floor|Landing|NAV_Panorama_Stair/.test(o.name))floors.push(o);}});}
root.updateMatrixWorld(true);all.updateMatrixWorld(true);const tree=new Octree().fromGraphNode(root),visibleTree=new Octree().fromGraphNode(all);

const results=[];for(const p of [[-27,16,1.65],[-27.078495879222263,15.94628606478153,1.65]]){const pos=new THREE.Vector3(p[0],p[2],-p[1]);const c=new Capsule(pos.clone().add(new THREE.Vector3(0,-1.35,0)),pos.clone().add(new THREE.Vector3(0,-.15,0)),.30);for(const o of root.children){const t=new Octree().fromGraphNode(o),hit=t.capsuleIntersect(c);if(hit&&hit.depth>.0001)results.push({point:p,name:o.name,depth:hit.depth,normal:hit.normal});}}console.log(JSON.stringify(results,null,2));
