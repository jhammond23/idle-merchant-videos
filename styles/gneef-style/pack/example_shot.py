"""Example: one 'Torchlit Blocktale' shot set-up in Blender 5.3 (no render).
Run inside Blender:  blender -b scene.blend -P example_shot.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy
import style_gneef as S

scene = bpy.context.scene
S.apply_look(scene, mood='ember', vignette=0.25)          # grade + bloom + vignette in the compositor
S.light_rig('ember_interior', target=(0, 0, 4.0), n_practicals=3, spread=10.0)   # our units: 3.3 per metre

plan = S.cut_plan('story-word-timings.json')               # shot list on word onsets
S.assign_moves(plan, reveal_words=['dragon', 'master'])    # push / pull / snap / roll / wobble mix
print(S.plan_stats(plan))

cam = S.new_camera('wide')
S.preroll_snap(cam, f_first=1)                             # frames 1-3 rolled 25 deg, then level
for shot in plan[:3]:                                      # stage each shot's camera, then its moves
    S.place(cam, loc=(0, -20, 5.0), look_at=(0, 0, 4.4), frame=shot['f0'])   # ~6 m back, eye height
    S.apply_moves(cam, shot, dist=20.0)
scene.frame_start, scene.frame_end = 1, plan[2]['f1']
