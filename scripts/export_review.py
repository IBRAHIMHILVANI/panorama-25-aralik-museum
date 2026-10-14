"""Export FBX meshes to an offline WebGL review without external dependencies."""
import sys,json,base64
from pathlib import Path
import numpy as np
from fbx_io import FBX, extract_scene


def export(path,out):
    fbx=FBX(path)
    scene=extract_scene(fbx)
    meshes=[]
    for m in scene:
        verts=m['vertices']
        triangles=[];uvs=[]
        geom=m['geometry']
        uv_node=geom.child('LayerElementUV')
        uv=None;uvindex=None
        if uv_node:
            uv=uv_node.child('UV').props[0].value.reshape(-1,2)
            ui=uv_node.child('UVIndex')
            if ui:uvindex=ui.props[0].value
        normal_node=geom.child('LayerElementNormal');normals=None;normal_index=None
        if normal_node:
            normals=normal_node.child('Normals').props[0].value.reshape(-1,3)
            ni=normal_node.child('NormalsIndex')
            if ni:normal_index=ni.props[0].value
            if not m['name'].startswith('REF_'):normals=None
        faceoffset=0
        for face in m['faces']:
            for k in range(1,len(face)-1):
                ids=[face[0],face[k],face[k+1]]
                tri=verts[ids]
                n=np.cross(tri[1]-tri[0],tri[2]-tri[0]);length=np.linalg.norm(n)
                if length<1e-10:continue
                n/=length
                uvtri=np.zeros((3,2))
                if uv is not None:
                    offsets=np.array([faceoffset,faceoffset+k,faceoffset+k+1])
                    if uvindex is not None:offsets=uvindex[offsets]
                    uvtri=uv[offsets]
                ntri=np.tile(n,(3,1))
                if normals is not None:
                    offsets=np.array([faceoffset,faceoffset+k,faceoffset+k+1])
                    if normal_index is not None:offsets=normal_index[offsets]
                    ntri=normals[offsets]
                triangles.append(np.column_stack((tri,ntri,uvtri)))
            faceoffset+=len(face)
        if not triangles:continue
        array=np.concatenate(triangles).astype('<f4')
        meshes.append({'name':m['name'],'material':m['material'],'color':m['color'],'n':len(array),'data':base64.b64encode(array.tobytes()).decode()})
    textures={}
    objects={n.props[0].value:n for n in fbx.root('Objects').children}
    for c in fbx.root('Connections').children:
        vals=c.values()
        if vals[0]=='OP' and len(vals)>3 and vals[3]=='DiffuseColor':
            texture=objects.get(vals[1]);material=objects.get(vals[2])
            if texture and material and texture.name=='Texture':textures[material.props[1].value.split('\x00')[0]]='../'+texture.child('RelativeFilename').props[0].value
    Path(out).write_text('window.MODEL_DATA='+json.dumps({'meshes':meshes,'source':str(path),'textures':textures},separators=(',',':'))+';\n')
    print('Review export:',out,len(meshes),'meshes',sum(m['n']//3 for m in meshes),'triangles')


if __name__=='__main__':export(sys.argv[1],sys.argv[2])
