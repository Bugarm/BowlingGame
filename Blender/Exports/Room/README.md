# Complete bowling room handoff

- Source: `../../BowlingAssets.blend`, scene `BowlingRoom_Complete`.
- Model: `BowlingRoom.fbx` (243 meshes, 4 empties, 10,659 triangles).
- Palettes (keep beside the FBX): `RoomPalette.png` (256×16), `LanePalette.png` (256×16), `PinPalette.png` (64×16), `BallPalette.png` (128×16), `ReturnPalette.png` (128×16).
- Export uses metre-aware FBX, triangulated faces, `-Z` forward / `Y` up. Unity still imported Blender Z-up; the scene instance uses Euler `(-90, 180, 0)` so Unity `+Z` faces the pins. See `Room_export.json` and `../../../memory.md`.
- Pins (`Room_Pin_01`–`10`) and balls (`Room_Ball_Red/Blue/Green`) are included at assembled positions so layout is preserved. They remain separately named for later rigidbodies.
- Blender preview lights, review cameras and layout-marker empties are not in the FBX. Unity lighting is a directional main light plus ambient; do not copy the nine Blender area lights.
- Palette UV0 overlaps intentionally. Disable mipmaps and avoid compressing the palettes to a single colour.
- Re-export: run `../../export_room.py` through Blender MCP. Unity rebuild: `XR_BowlingGame/AgentScripts/BuildBowlingAlley.cs` via `unity command run_script`.

See `../../../Journey/009-unity-room-import.md`.
