"""FBX roundtrip checks through Blender MCP; removes only its own temporary imports."""
import bpy, bmesh, json, os
from pathlib import Path
from mathutils import Vector

OUT=Path('F:/UnityProjects/BowlingGame/Blender/Exports/Pins')
original=bpy.context.scene
reports=[]
for filename,expected in [('BowlingPin.fbx',1),('BowlingPinRack.fbx',10)]:
    qa=bpy.data.scenes.new('Pin_Export_QA')
    bpy.context.window.scene=qa
    try:
        bpy.ops.import_scene.fbx(filepath=str(OUT/filename))
        meshes=[o for o in qa.objects if o.type=='MESH']
        for ob in meshes: ob.data.calc_loop_triangles()
        points=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
        bounds=[[min(p[i] for p in points),max(p[i] for p in points)] for i in range(3)]
        report={'file':filename,'meshes':len(meshes),'triangles':sum(len(o.data.loop_triangles) for o in meshes),
                'all_have_uv':all(len(o.data.uv_layers)>0 for o in meshes),
                'materials':len(set(m for o in meshes for m in o.data.materials)),'bounds_m':bounds}
        assert len(meshes)==expected
        assert report['triangles']==332*expected
        assert report['all_have_uv'] and report['materials']==1
        assert abs(bounds[2][0])<.00001 and abs(bounds[2][1]-.38)<.00001
        if expected==1:
            assert abs(bounds[0][1]-bounds[0][0]-.1329196)<.00001
            assert meshes[0].location.length<.00001
        else:
            positions=sorted([tuple(round(v,4) for v in o.matrix_world.translation) for o in meshes])
            wanted=sorted([((c-r/2)*.3048,round(7+r*.264,4),0) for r in range(4) for c in range(r+1)])
            assert all(all(abs(a-b)<.0001 for a,b in zip(p,q)) for p,q in zip(positions,wanted))
            report['positions_m']=positions
        reports.append(report)
    finally:
        for ob in list(qa.objects): bpy.data.objects.remove(ob,do_unlink=True)
        bpy.context.window.scene=original
        bpy.data.scenes.remove(qa)
result={'exports':reports,'passed':True,'unity_import_tested':False}
(OUT/'FBX_roundtrip_validation.json').write_text(json.dumps(result,indent=2))
