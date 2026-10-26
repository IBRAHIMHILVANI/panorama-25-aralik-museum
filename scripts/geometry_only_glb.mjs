// Keep the exact exported meshes while excluding unused image bytes from Node QA.
export function stripTextures(j,b,offset){
 const ids=new Set();for(const a of j.accessors||[]){if(a.bufferView!==undefined)ids.add(a.bufferView);if(a.sparse){ids.add(a.sparse.indices.bufferView);ids.add(a.sparse.values.bufferView);}}
 const remap=new Map(),views=[],chunks=[];let cursor=0;
 for(const old of [...ids].sort((a,b)=>a-b)){const v=j.bufferViews[old],pad=(4-cursor%4)%4;if(pad){chunks.push(Buffer.alloc(pad));cursor+=pad;}remap.set(old,views.length);views.push({...v,buffer:0,byteOffset:cursor});const part=b.subarray(offset+(v.byteOffset||0),offset+(v.byteOffset||0)+v.byteLength);chunks.push(part);cursor+=part.length;}
 for(const a of j.accessors||[]){if(a.bufferView!==undefined)a.bufferView=remap.get(a.bufferView);if(a.sparse){a.sparse.indices.bufferView=remap.get(a.sparse.indices.bufferView);a.sparse.values.bufferView=remap.get(a.sparse.values.bufferView);}}
 const binary=Buffer.concat(chunks);j.buffers=[{byteLength:binary.length,uri:'data:application/octet-stream;base64,'+binary.toString('base64')}];j.bufferViews=views;delete j.images;delete j.textures;delete j.samplers;j.materials=(j.materials||[]).map(m=>({name:m.name}));
}
