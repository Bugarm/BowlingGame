# Bowling lane handoff

- Source: `../../BowlingAssets.blend`, scene `Lane_Asset`.
- Model: `BowlingLane.fbx` (15 meshes, 1,865 triangles, one shared material).
- Base colour: `LanePalette.png` (256 × 16, sRGB). Keep beside the FBX.
- Root: foul-line centre; playing surface height zero. Source lane extends along Blender +Y. Export uses -Z forward / Y up; verify the resulting forward direction during Unity import.
- Playing width: 1.0668 m; head pin: 7 m from foul line; approach: 1.5 m. Compact concept-art proportions, not a regulation-length lane. Whole assembly: 10.582 m long including the approach, pin deck and rear pit.
- Arrow centres: 0.99–1.65 m beyond the foul line, moved toward the player to follow the concept.
- All mesh object scales are applied. No animation or review lights/cameras are exported.
- Palette UV0 intentionally overlaps. Generate UV1 separately if baking lightmaps. Avoid aggressive texture compression or reducing the texture to a single colour; disable mipmaps for this palette during Unity import.
- Use an appropriate Unity render-pipeline material with the palette as Base Map. Blender's studio lighting does not transfer.
- Use dedicated flat lane and static gutter colliders; decorative inlays are 1 mm above the surface and must not become collision bumps.
- Keep parts editable or combine static render meshes during integration. A shared material alone does not reduce 15 renderers to one draw call.
- Unity import, XR Interaction Simulator validation and headset profiling are deferred, not yet passed.

See `../../../Journey/001-low-poly-lane.md` for the original build and `../../../Journey/002-compact-concept-proportions.md` for the current dimensions. To reconstruct from scratch, run `build_lane.py`, then `compact_lane.py`, through Blender MCP.
