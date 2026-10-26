// Exact previously escaping image rays, against the actual exported part07.
import fs from 'node:fs/promises';
import crypto from 'node:crypto';
import * as T from '../review/walkthrough/node_modules/three/build/three.module.js';
import {GLTFLoader} from '../review/walkthrough/node_modules/three/examples/jsm/loaders/GLTFLoader.js';
import {stripTextures} from './geometry_only_glb.mjs';
globalThis.ProgressEvent=class{constructor(t,i={}){Object.assign(this,i);}};
const root=new T.Group(),b=await fs.readFile(new URL('../review/walkthrough/part07.glb',import.meta.url)),n=b.readUInt32LE(12),j=JSON.parse(b.subarray(20,20+n));stripTextures(j,b,28+n);
const g=await new Promise((resolve,reject)=>new GLTFLoader().parse(JSON.stringify(j),'',resolve,reject));g.scene.updateMatrixWorld(true);
g.scene.traverse(o=>{if(!o.isMesh||o.userData.review_hidden||o.userData.review_only||o.userData.temporary_until)return;const m=new T.Mesh(o.geometry,new T.MeshBasicMaterial({side:T.DoubleSide}));m.name=o.name;o.matrixWorld.decompose(m.position,m.quaternion,m.scale);root.add(m);});root.updateMatrixWorld(true);
const path=JSON.parse(await fs.readFile(new URL('../reconstruction/full-tour-path-2026-10-26.json',import.meta.url),'utf8')),report=[];
for(const [time,pixels]of [[387,[[655,488],[658,487],[660,494]]],[390,[[450,240]]]]){
 const s=path.samples.reduce((a,b)=>Math.abs(a.t-time)<Math.abs(b.t-time)?a:b),camera=new T.PerspectiveCamera(64,1024/576,.01,800);camera.position.set(s.position[0],s.position[2],-s.position[1]);camera.lookAt(s.look_target[0],s.look_target[2],-s.look_target[1]);camera.updateMatrixWorld(true);
 for(const [x,y]of pixels){const ray=new T.Raycaster();ray.setFromCamera(new T.Vector2(x/1024*2-1,1-y/576*2),camera);const h=ray.intersectObjects(root.children,false)[0];report.push({time,pixel:[x,y],passed:!!h,hit:h?{name:h.object.name,distance:h.distance,author:[h.point.x,-h.point.z,h.point.y]}:null});}
}
const result={passed:report.every(r=>r.passed),glb_sha256:crypto.createHash('sha256').update(b).digest('hex'),scope:'Original escaping foot rays and dark roof patch, exact64deg verticalFOV at1024x576; visible exported geometry only',rays:report};await fs.writeFile(new URL('../review/qa/part07-stair-foot-ray-after.json',import.meta.url),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));if(!result.passed)process.exitCode=1;
