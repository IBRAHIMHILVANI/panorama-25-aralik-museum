import bpy,json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'output/Gaziantep-Museum-2026-10-25'
def bounds(obs):
 pts=[o.matrix_world@Vector(p) for o in obs for p in o.bound_box];return {'min':[min(p[i] for p in pts) for i in range(3)],'max':[max(p[i] for p in pts) for i in range(3)]}
bpy.ops.wm.open_mainfile(filepath=str(OUT/'Gaziantep_Museum_Combined.blend'));expected=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.get('collision')];bpy.context.view_layer.update();count=len(expected);box=bounds(expected)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.fbx(filepath=str(OUT/'Gaziantep_Museum_Combined_Colliders.fbx'));bpy.context.view_layer.update();actual=[o for o in bpy.context.scene.objects if o.type=='MESH'];bb=bounds(actual);err=max(abs(bb[k][i]-box[k][i]) for k in ['min','max'] for i in range(3));result={'expected_meshes':count,'imported_meshes':len(actual),'bounds_max_error_m':err,'all_marked_collision':all(o.get('collision') for o in actual),'temporary_review_boundaries':sum(o.name.startswith('NAV_Boundary_') or bool(o.get('review_only')) for o in actual)};result['passed']=count==len(actual) and err<.002 and result['all_marked_collision'] and result['temporary_review_boundaries']==0
(OUT/'combined-colliders-verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));assert result['passed']
