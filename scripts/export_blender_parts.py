"""Import generated metre geometry into Blender, export native/FBX/glTF and verify.
Run with Blender --background --factory-startup --python this_file -- part01.
"""
import bpy,bmesh,math,json,sys,time,hashlib
from pathlib import Path
from mathutils import Vector,Matrix

ROOT=Path(__file__).resolve().parents[1]
part=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'part01'
data=json.loads((ROOT/'reconstruction'/f'{part}-scene.json').read_text())
OUT=ROOT/'output/Gaziantep-Museum-2026-10-25';OUT.mkdir(parents=True,exist_ok=True)
PREVIEW=ROOT/'review/walkthrough'
base=json.loads((ROOT/'reconstruction/part-files.json').read_text())[part]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.context.scene.unit_settings.system='METRIC';bpy.context.scene.unit_settings.scale_length=1.0
root=bpy.data.collections.new(data['part']);bpy.context.scene.collection.children.link(root)
visible=bpy.data.collections.new('Visible_Model');root.children.link(visible)
nav=bpy.data.collections.new('Navigation_Colliders');root.children.link(nav)
helpers=bpy.data.collections.new('Review_Only_Helpers');root.children.link(helpers)
mats={}
def linear(c):return c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4
for name,md in data['materials'].items():
    rgb=[linear(c) for c in md['color']]
    mat=bpy.data.materials.new(name);mat.use_nodes=True;mat.diffuse_color=(*rgb,md['alpha'])
    p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*rgb,1)
    p.inputs['Roughness'].default_value=md['roughness'];p.inputs['Metallic'].default_value=md['metallic'];p.inputs['Alpha'].default_value=md['alpha']
    if md['emission']:
        p.inputs['Emission Color'].default_value=(*rgb,1);p.inputs['Emission Strength'].default_value=md['emission']
    if md['image']:
        im=bpy.data.images.load(str(OUT/md['image']),check_existing=True)
        tex=mat.node_tree.nodes.new('ShaderNodeTexImage');tex.image=im;mat.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
        if md['emission']:mat.node_tree.links.new(tex.outputs['Color'],p.inputs['Emission Color'])
    if md['alpha']<1:mat.surface_render_method='DITHERED'
    mat.use_backface_culling=False
    mats[name]=mat

report={'part':part,'units':'metres','blender_version':bpy.app.version_string,'mesh_repairs':[],'source_photos':'reconstruction/evidence-catalog.json','accuracy_claim':'photo-informed review draft; not a measured survey'}
for idx,d in enumerate(data['objects']):
    me=bpy.data.meshes.new(d['name']);me.from_pydata(d['vertices'],[],d['faces']);me.update()
    changed=me.validate(verbose=False,clean_customdata=False)
    if changed:report['mesh_repairs'].append(d['name'])
    obj=bpy.data.objects.new(d['name'],me);(helpers if d.get('review_only') else nav if d['hidden'] else visible).objects.link(obj)
    me.materials.append(mats[d['material']])
    if len(d['uv'])==len(me.polygons):
        uv=me.uv_layers.new(name='UVMap')
        for poly,uvs in zip(me.polygons,d['uv']):
            if len(uvs)==len(poly.loop_indices):
                for li,co in zip(poly.loop_indices,uvs):uv.data[li].uv=co
    for poly in me.polygons:poly.use_smooth=d['smooth']
    obj['source_photos']=d['source_photos'];obj['reconstruction_basis']=d['basis'];obj['part']=data['part'];obj['collision']=d['collision'];obj['review_hidden']=d['hidden']
    if d.get('temporary_until'):obj['temporary_until']=d['temporary_until'];obj['review_only']=True
    obj.hide_render=d['hidden'];obj.display_type='WIRE' if d['hidden'] else 'TEXTURED'
    if idx%80==0:print('Imported meshes',idx+1,'/',len(data['objects']),flush=True)

# Full 3D exhibit assets are transformed in metres and their textures are made
# local to the delivery package before either FBX or glTF is exported.
report['asset_instances']=[]
for asset in data.get('assets',[]):
    before=set(bpy.data.objects);images_before=set(bpy.data.images)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/asset['path']))
    imported=set(bpy.data.objects)-before;mesh_objects=[o for o in imported if o.type=='MESH'];bpy.context.view_layer.update()
    pts=[o.matrix_world@Vector(p) for o in mesh_objects for p in o.bound_box]
    mi=Vector([min(p[i] for p in pts) for i in range(3)]);ma=Vector([max(p[i] for p in pts) for i in range(3)])
    factor=asset['height']/(ma.z-mi.z);offset=Vector((-(mi.x+ma.x)/2,-(mi.y+ma.y)/2,-mi.z))
    anchor=bpy.data.objects.new(asset['name']+'_Root',None);visible.objects.link(anchor)
    anchor.matrix_world=Matrix.Translation(Vector(asset['position']))@Matrix.Rotation(asset['yaw'],4,'Z')@Matrix.Scale(factor,4)@Matrix.Translation(offset)
    for obj in imported:
        if obj.parent not in imported:
            original=obj.matrix_world.copy();obj.parent=anchor;obj.matrix_parent_inverse=Matrix.Identity(4);obj.matrix_basis=original
        for coll in list(obj.users_collection):coll.objects.unlink(obj)
        visible.objects.link(obj)
        obj['source_photos']=asset['source_photos'];obj['reconstruction_basis']=asset['basis'];obj['part']=data['part'];obj['collision']=False;obj['review_hidden']=False
    for i,obj in enumerate(mesh_objects):obj.name=asset['name']+'_Mesh_'+str(i)
    asset_images=set()
    for obj in mesh_objects:
        for slot in obj.material_slots:
            if slot.material and slot.material.use_nodes:
                for node in slot.material.node_tree.nodes:
                    if node.type=='TEX_IMAGE' and node.image:asset_images.add(node.image)
    for i,im in enumerate(sorted(asset_images,key=lambda image:image.name)):
        # glTF packed images may be lazy: has_data=False does not mean absent.
        # Save the untouched embedded encoding, then reload from its unique path.
        if im.packed_file:
            raw=bytes(im.packed_file.data);ext='.jpg' if raw[:2]==bytes([255,216]) else '.png'
            filename=asset['name']+'_Texture_'+str(i)+ext;dest=OUT/'textures'/filename;dest.write_bytes(raw)
            im.unpack(method='REMOVE');im.filepath=str(dest);im.reload()
        else:
            _=im.pixels[0]
            filename=asset['name']+'_Texture_'+str(i)+'.png';dest=OUT/'textures'/filename
            im.filepath_raw=str(dest);im.file_format='PNG';im.save();im.filepath=str(dest)
        assert dest.is_file() and min(im.size)>0,(asset['name'],im.name,str(dest))
        preview=im.copy();preview.name=asset['name']+'_Preview_'+str(i)
        scale=min(1,1024/max(im.size));preview.scale(max(1,round(im.size[0]*scale)),max(1,round(im.size[1]*scale)))
        preview.filepath_raw=str(PREVIEW/'textures'/filename);preview.file_format='JPEG' if filename.endswith('.jpg') else 'PNG';preview.save();bpy.data.images.remove(preview)
    report['asset_instances'].append({'name':asset['name'],'source_glb':asset['path'],'meshes':len(mesh_objects),'height_m':asset['height'],'basis':asset['basis']})
font_path=Path('/System/Library/Fonts/Supplemental/Arial.ttf')
font=bpy.data.fonts.load(str(font_path)) if font_path.exists() else None
for td in data['texts']:
    curve=bpy.data.curves.new(td['name'],'FONT');curve.body=td['text'];curve.size=td['size'];curve.align_x=td['align'];curve.space_line=1.15;curve.extrude=.003;curve.resolution_u=3
    if font:curve.font=font
    obj=bpy.data.objects.new(td['name'],curve);(helpers if td.get('review_only') else visible).objects.link(obj);obj.location=td['location'];obj.rotation_euler=td['rotation'];curve.materials.append(mats[td['material']])
    bpy.context.view_layer.objects.active=obj;obj.select_set(True);bpy.ops.object.convert(target='MESH');obj.select_set(False)
    obj['source_photos']='1935-1941';obj['part']=data['part'];obj['collision']=False
    if td.get('temporary_until'):obj['temporary_until']=td['temporary_until'];obj['review_only']=True

# Text tessellation can produce zero-area faces on coincident glyph contours.
# Remove only those non-rendering faces and retain the actual glyph outlines.
for obj in list(visible.objects)+list(nav.objects)+list(helpers.objects):
    if obj.type!='MESH':continue
    bad=[p.index for p in obj.data.polygons if p.area<1e-10]
    if not bad:continue
    bm=bmesh.new();bm.from_mesh(obj.data);bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[bm.faces[i] for i in bad],context='FACES')
    bm.to_mesh(obj.data);bm.free();obj.data.update()
    report['mesh_repairs'].append({'mesh':obj.name,'removed_zero_area_faces':len(bad)})

def bounds(objs):
    pts=[o.matrix_world@Vector(c) for o in objs if o.type=='MESH' for c in o.bound_box]
    return {'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)]}
bpy.context.view_layer.update()
report['visible_meshes']=len([o for o in visible.objects if o.type=='MESH'])
report['vertices']=sum(len(o.data.vertices) for o in visible.objects if o.type=='MESH')
report['polygons']=sum(len(o.data.polygons) for o in visible.objects if o.type=='MESH')
report['visible_bounds_m']=bounds(visible.objects)
report['collision_meshes']=sum(1 for o in bpy.data.objects if o.get('collision'))
report['nonfinite_vertices']=sum(1 for o in visible.objects if o.type=='MESH' for v in o.data.vertices if not all(math.isfinite(x) for x in v.co))
report['degenerate_polygons']=sum(1 for o in visible.objects if o.type=='MESH' for p in o.data.polygons if p.area<1e-10)

# Render cameras and illumination are native source helpers; they are not exported in the FBX.
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=1440;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.world.color=(.35,.40,.48)
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.42,.54,.70,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.55
sun_data=bpy.data.lights.new('Daylight','SUN');sun_data.energy=2.7;sun_data.angle=.08
sun=bpy.data.objects.new('Daylight',sun_data);scene.collection.objects.link(sun);sun.rotation_euler=(.48,-.40,-.65)
review_lights=[]
for i,definition in enumerate(data.get('lights',[])):
    ld=bpy.data.lights.new(definition.get('name',part+'_Light_'+str(i)),'SPOT')
    ld.energy=definition.get('energy',65);ld.color=definition.get('color',(1,.88,.72))
    ld.shadow_soft_size=.3;ld.spot_size=math.radians(definition.get('angle',115));ld.spot_blend=.7
    lo=bpy.data.objects.new(ld.name,ld);scene.collection.objects.link(lo);lo.location=definition['position']
    if definition.get('target'):lo.rotation_euler=(Vector(definition['target'])-lo.location).to_track_quat('-Z','Y').to_euler()
    review_lights.append(lo)
if part=='part02':
    for i,(loc,energy) in enumerate([((33,8,3.10),140),((27,12,3.05),100),((40,8,3.05),110),((33,8,-.92),120),((27,10,-.95),95),((38,4,-.95),95)]):
        ld=bpy.data.lights.new('Atrium_Review_Light_'+str(i),'SPOT');ld.energy=energy*.75;ld.color=(1,.88,.69);ld.shadow_soft_size=.35;ld.spot_size=math.radians(130);ld.spot_blend=.7
        lo=bpy.data.objects.new(ld.name,ld);scene.collection.objects.link(lo);lo.location=loc;review_lights.append(lo)
scene.view_settings.view_transform='AgX'
for v in data['views']:
    cd=bpy.data.cameras.new('View_'+v['id']);cd.lens=22
    co=bpy.data.objects.new('View_'+v['id'],cd);scene.collection.objects.link(co);co.location=v['position'];co.rotation_euler=(Vector(v['target'])-co.location).to_track_quat('-Z','Y').to_euler()
scene.camera=bpy.data.objects.get('View_portal') or bpy.data.objects.get('View_atrium') or bpy.data.objects.get('View_'+data['views'][0]['id'])

# Native editable source keeps material links relative to the delivery directory.
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(base+'.blend')))
bpy.ops.file.make_paths_relative()
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(base+'.blend')))
bpy.ops.object.select_all(action='DESELECT')
for o in list(visible.objects):
    if o.type=='MESH':o.select_set(True)
fbx_path=OUT/(base+'.fbx')
bpy.ops.export_scene.fbx(filepath=str(fbx_path),use_selection=True,object_types={'MESH'},global_scale=1,apply_unit_scale=True,apply_scale_options='FBX_SCALE_UNITS',axis_forward='-Z',axis_up='Y',use_space_transform=True,bake_space_transform=False,mesh_smooth_type='FACE',use_mesh_modifiers=True,add_leaf_bones=False,bake_anim=False,path_mode='COPY',embed_textures=True,use_custom_props=True)

# The glTF review includes low-polygon collision helpers, hidden by the viewer.
bpy.ops.object.select_all(action='DESELECT')
for o in list(visible.objects)+list(nav.objects)+list(helpers.objects):
    if o.type=='MESH':o.select_set(True)
for o in review_lights:o.select_set(True)
for im in bpy.data.images:
    nm=Path(im.filepath).name
    low=PREVIEW/'textures'/nm
    if low.exists():im.filepath=str(low);im.reload()
for name,mat in mats.items():
    if name.startswith('Photo_'):
        tex=next((n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE'),None)
        output=next(n for n in mat.node_tree.nodes if n.type=='OUTPUT_MATERIAL')
        if tex:mat.node_tree.links.new(tex.outputs['Color'],output.inputs['Surface'])
bpy.ops.export_scene.gltf(filepath=str(PREVIEW/(part+'.glb')),export_format='GLB',use_selection=True,export_yup=True,export_extras=True,export_materials='EXPORT',export_apply=True,export_cameras=False,export_lights=bool(review_lights),export_image_format='AUTO',export_import_convert_lighting_mode='RAW')
(PREVIEW/(part+'-views.json')).write_text(json.dumps(data['views'],ensure_ascii=False))
report['fbx_sha256']=hashlib.sha256(fbx_path.read_bytes()).hexdigest();report['fbx_bytes']=fbx_path.stat().st_size
(OUT/(part+'-verification.json')).write_text(json.dumps(report,indent=2,ensure_ascii=False))
print('EXPORT_COMPLETE',json.dumps(report),flush=True)

# Independent application importer round trip: fresh Blender scene, exported FBX.
expected=report['visible_bounds_m'];bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(fbx_path),use_custom_normals=True)
bpy.context.view_layer.update();imported=[o for o in bpy.context.scene.objects if o.type=='MESH']
actual=bounds(imported)
error=max(abs(actual[k][i]-expected[k][i]) for k in ['min','max'] for i in range(3))
report['fbx_import_check']={'imported_meshes':len(imported),'expected_meshes':report['visible_meshes'],'bounds_max_error_m':error,'passed':len(imported)==report['visible_meshes'] and error<.002}
texture_images={}
missing_uv=[]
for obj in imported:
    textured=False
    for slot in obj.material_slots:
        mat=slot.material
        if not mat or not mat.use_nodes:continue
        for node in mat.node_tree.nodes:
            if node.type=='TEX_IMAGE' and node.image:
                im=node.image;textured=True;path=Path(bpy.path.abspath(im.filepath))
                texture_images[path.name]={'size_px':list(im.size),'loaded':bool(im.has_data),'file_exists':path.exists()}
    if textured and not obj.data.uv_layers:missing_uv.append(obj.name)
report['fbx_texture_check']={'images':texture_images,'textured_meshes_without_uv':missing_uv,'passed':not missing_uv and all(v['loaded'] and v['file_exists'] and min(v['size_px'])>0 for v in texture_images.values())}
(OUT/(part+'-verification.json')).write_text(json.dumps(report,indent=2,ensure_ascii=False))
assert report['nonfinite_vertices']==0 and report['degenerate_polygons']==0,report
assert report['fbx_import_check']['passed'],report['fbx_import_check']
assert report['fbx_texture_check']['passed'],report['fbx_texture_check']
print('ROUNDTRIP_PASS',report['fbx_import_check'],flush=True)
