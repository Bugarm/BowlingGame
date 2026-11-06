# Bowling balls handoff

- Source: `../../BowlingAssets.blend`, scene `Ball_Assets`.
- Exports: `BowlingBall_Red.fbx`, `BowlingBall_Blue.fbx`, `BowlingBall_Green.fbx`.
- Each export: one centred mesh, 249 source vertices, 494 triangles, nominal diameter 0.217 m. All three together: 1,482 triangles.
- Real recessed holes: two 10 mm radius finger holes and one 13 mm radius thumb hole, with dark walls and closed bottoms. Nominal radial depth is 47.5 mm; actual depth from the faceted surface is slightly smaller.
- One shared `Ball_Palette` material with `BallPalette.png` (128 × 16, sRGB). Keep the PNG beside the FBXs. Use a suitable Unity pipeline material and assign it as Base Map; disable palette mipmaps and avoid aggressive compression.
- UV0 samples colour swatches; it intentionally overlaps. The three meshes differ in body-colour UVs. There are no separate lightmap UVs.
- Object origins are sphere centres. The source review scene displays balls side by side at Z = 0.1085 m; the individual FBXs were exported at location zero before staging. For manual re-export, temporarily reset location, or use the same centred-export process as the script.
- Export: metre-aware FBX units, -Z forward / Y up, triangulated, no animation/cameras/lights.
- Future Unity integration: use a SphereCollider of radius 0.1085 m for smooth rolling; do not use the faceted render surface or finger recesses as the rolling collider. Rigidbody, grip interaction, mass, friction and headset tests are deferred.
- Rebuild through Blender MCP using `Blender/build_balls.py`; it refuses duplicate creation. Validate through MCP using `Blender/validate_balls.py`.

See `../../../Journey/004-low-poly-bowling-balls.md`.
