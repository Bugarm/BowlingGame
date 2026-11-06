# Bowling ball return handoff

- Source: `../../BowlingAssets.blend`, scene `BallReturn_Asset`.
- Export: `BowlingBallReturn.fbx`, 21 named meshes, **780 triangles**, two materials (shared colour palette plus warm lamp).
- Approximate footprint: **0.66 m wide × 1.59 m long**, 0.73 m high. Root is at ground level, centred under the housing. Tray extends Blender -Y.
- `ReturnPalette.png`: 128 × 16 sRGB atlas. Keep beside FBX, assign to the Base Map of a Unity pipeline-compatible material. Disable palette mipmaps; UV0 overlaps intentionally.
- Revision 006 changes the tray's two wood swatches to walnut brown (`#705044` / `#805D4E`), distinct from the lane floor. Use the updated PNG with the existing FBX.
- `Return_Warm_Lamp` uses a warm emissive shader in Blender. Recreate emission in the Unity material; shader settings and glow are not guaranteed to transfer through FBX. No real-time light is included in the asset export.
- Three existing ball meshes are linked in `RETURN BALLS | Preview only`, excluded from FBX. They remain separate reusable ball assets.
- Preview ball centres in source coordinates: `(0, -1.02, 0.4237)`, `(0, -0.775, 0.4237)`, `(0, -0.53, 0.4237)` metres. Nominal radius: 0.1085 m.
- Static fit checked for three balls; this is not a simulated return mechanism. Future integration needs colliders, ball spawning/queueing and XR reach testing.
- Side accents and wooden strips are intentional open decorative faces, not collision geometry. Use simple separate static colliders for housing/tray/supports.
- Author through Blender MCP with `Blender/build_ball_return.py`; validate through MCP with `Blender/validate_ball_return.py`.

See `../../../Journey/005-low-poly-ball-return.md`.
