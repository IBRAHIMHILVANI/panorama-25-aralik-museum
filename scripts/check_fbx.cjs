/* Independent structural validation using only the installed Node runtime. */
const fs=require('node:fs'),zlib=require('node:zlib'),assert=require('node:assert/strict');
const data=fs.readFileSync(process.argv[2]);
assert.equal(data.subarray(0,23).toString('latin1'),'Kaydara FBX Binary  \x00\x1a\x00');
const version=data.readUInt32LE(23);assert.equal(version,7400);
let nodeCount=0,arrays=0,embeddedImages=0;const objects=new Map(),connections=[];
function parse(start){
  const end=data.readUInt32LE(start),nprops=data.readUInt32LE(start+4),plen=data.readUInt32LE(start+8),nlen=data[start+12];
  if(!end)return {end:start+13,node:null};
  assert(end<=data.length&&end>start);let offset=start+13;const name=data.subarray(offset,offset+nlen).toString('utf8');offset+=nlen;
  const pstart=offset,props=[];
  for(let i=0;i<nprops;i++){
    const type=String.fromCharCode(data[offset++]);let v;
    if(type==='Y'){v=data.readInt16LE(offset);offset+=2;}
    else if(type==='C'){v=!!data[offset++];}
    else if(type==='I'){v=data.readInt32LE(offset);offset+=4;}
    else if(type==='L'){v=Number(data.readBigInt64LE(offset));offset+=8;}
    else if(type==='F'){v=data.readFloatLE(offset);offset+=4;}
    else if(type==='D'){v=data.readDoubleLE(offset);offset+=8;}
    else if(type==='S'||type==='R'){const len=data.readUInt32LE(offset);offset+=4;v=data.subarray(offset,offset+len);offset+=len;if(type==='S')v=v.toString('utf8');if(name==='Content')embeddedImages++;}
    else {
      assert('fdlibc'.includes(type));const n=data.readUInt32LE(offset),enc=data.readUInt32LE(offset+4),len=data.readUInt32LE(offset+8);offset+=12;
      let raw=data.subarray(offset,offset+len);offset+=len;if(enc)raw=zlib.inflateSync(raw);
      const size={f:4,d:8,l:8,i:4,b:1,c:1}[type];assert.equal(raw.length,n*size);arrays++;
      v={count:n,type,raw};
      if(type==='d'||type==='f')for(let j=0;j<n;j++)assert(Number.isFinite(type==='d'?raw.readDoubleLE(j*8):raw.readFloatLE(j*4)));
    }
    props.push(v);
  }
  assert.equal(offset-pstart,plen,`Property byte length in ${name}`);const children=[];
  while(offset<end-13){const c=parse(offset);offset=c.end;if(!c.node)break;children.push(c.node);}
  if(children.length){assert.equal(offset,end-13,`Child boundary in ${name}`);assert(data.subarray(offset,end).every(v=>v===0));}
  else assert.equal(offset,end,`Leaf boundary in ${name}`);
  nodeCount++;return {end,node:{name,props,children}};
}
let offset=27,roots=[];
while(offset<data.length){const r=parse(offset);offset=r.end;if(!r.node)break;roots.push(r.node);}
const root=name=>roots.find(n=>n.name===name),child=(n,name)=>n.children.find(c=>c.name===name);
for(const n of root('Objects').children){assert(!objects.has(n.props[0]),'Duplicate ID');objects.set(n.props[0],n);}
for(const n of root('Connections').children){connections.push(n.props);assert(objects.has(n.props[1]));assert(n.props[2]===0||objects.has(n.props[2]));}
const meshes=[...objects.values()].filter(n=>n.name==='Geometry'&&n.props[2]==='Mesh');let vertices=0,faces=0;
for(const n of meshes){
  const va=child(n,'Vertices').props[0],pa=child(n,'PolygonVertexIndex').props[0];assert.equal(va.count%3,0);vertices+=va.count/3;
  let corners=0;
  for(let i=0;i<pa.count;i++){const ix=pa.raw.readInt32LE(i*4),j=ix<0?-ix-1:ix;assert(j>=0&&j<va.count/3);corners++;if(ix<0){assert(corners>=3);corners=0;faces++;}}
  assert.equal(corners,0,'Unterminated polygon');
  const uv=child(n,'LayerElementUV');if(uv){const ui=child(uv,'UVIndex'),values=child(uv,'UV').props[0];if(ui){assert.equal(ui.props[0].count,pa.count);for(let i=0;i<pa.count;i++){const j=ui.props[0].raw.readInt32LE(i*4);assert(j>=0&&j<values.count/2);}}}
}
const footer=data.subarray(offset);assert.equal(footer.subarray(0,16).toString('hex'),'fabcab09d0c8d466b176fb831cf7267e');assert.equal(footer.subarray(-16).toString('hex'),'f85a8c6adef5d97eece90ce3758f290b');assert.equal(footer.readUInt32LE(footer.length-140),version);assert((offset+footer.length-140)%16===0);
const countByType={};for(const n of objects.values())countByType[n.name]=(countByType[n.name]||0)+1;
for(const n of root('Definitions').children.filter(n=>n.name==='ObjectType')){const t=n.props[0],c=child(n,'Count').props[0];assert.equal(c,t==='GlobalSettings'?1:countByType[t]);}
assert.equal(child(root('Definitions'),'Count').props[0],objects.size+1);
const result={valid:true,version,objects:objects.size,meshes:meshes.length,vertices,polygons:faces,nodeCount,arrays,embeddedImages,bytes:data.length,footerAlignment:true,allConnectionsResolved:true};
console.log(JSON.stringify(result,null,2));
if(process.argv[3])fs.writeFileSync(process.argv[3],JSON.stringify(result,null,2)+'\n');
