"""Run via Blender MCP to verify each exported ball and its recessed holes."""
import bpy,json,os
from pathlib import Path
from mathutils import Vector
OUT=Path('F:/UnityProjects/BowlingGame/Blender/Exports/Balls')
original=bpy.context.scene
reports=[]
for colour in ['Red','Blue','Green']:
    qa=bpy.data.scenes.new('Ball_Export_QA');bpy.context.window.scene=qa
    try:
        bpy.ops.import_scene.fbx(filepath=str(OUT/('BowlingBall_'+colour+'.fbx')))
        meshes=[o for o in qa.objects if o.type=='MESH'];assert len(meshes)==1
        ob=meshes[0];ob.data.calc_loop_triangles()
        pts=[ob.matrix_world@Vector(c) for c in ob.bound_box]
        bounds=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
        assert len(ob.data.loop_triangles)==494 and ob.location.length<1e-6
        assert all(abs((hi-lo)-.217)<.004 for lo,hi in bounds)
        assert len(ob.data.uv_layers)>0 and len(ob.data.materials)==1
        image_nodes=[n for n in ob.data.materials[0].node_tree.nodes if n.type=='TEX_IMAGE' and n.image]
        assert image_nodes and all(n.image.packed_file or os.path.exists(bpy.path.abspath(n.image.filepath)) for n in image_nodes)
        # Transform source-space drill axes through the imported object transform.
        depths=[]
        for xyz in [(-.025,-.048,.094),(.025,-.048,.094),(0,-.086,.058)]:
            d=Vector(xyz).normalized()
            inv=ob.matrix_world.inverted()
            start=inv@(d*.15)
            direction=(inv.to_3x3()@(-d)).normalized()
            hit,loc,normal,face=ob.ray_cast(start,direction)
            assert hit
            world_loc=ob.matrix_world@loc
            axial=world_loc.dot(d)
            assert abs(axial-.061)<.0001
            depths.append(round(.1085-axial,6))
        reports.append({'file':'BowlingBall_'+colour+'.fbx','triangles':494,'bounds_m':bounds,
            'centre_pivot':True,'uv_and_texture_present':True,'hole_depths_from_nominal_sphere_m':depths})
    finally:
        for ob in list(qa.objects):bpy.data.objects.remove(ob,do_unlink=True)
        bpy.context.window.scene=original;bpy.data.scenes.remove(qa)
result={'passed':True,'balls':reports,'unity_import_tested':False}
(OUT/'FBX_roundtrip_validation.json').write_text(json.dumps(result,indent=2))
