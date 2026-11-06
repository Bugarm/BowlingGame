# Bowling pins handoff

- Source: `../../BowlingAssets.blend`, scene `Pin_Asset` for a single pin; `Lane_Asset` for the ten-pin preview.
- `BowlingPin.fbx`: one pin, origin at the base centre, 0.38 m high and approximately 0.133 m wide. 168 vertices / 332 triangles, 12 radial sides, 14 profile rings, flat shading, closed top and bottom.
- `BowlingPinRack.fbx`: ten separate pin objects in a 1–2–3–4 arrangement. Root at the head-pin position, 7 m down the lane. Child spacing is 0.3048 m across rows and 0.264 m between rows. Do not add another 7 m translation when placing this exported rack at the lane origin.
- `PinPalette.png`: shared 64 × 16 sRGB base-colour atlas, cream body and two red neck bands. One material per pin; bands are faces on the same mesh. Keep beside the FBXs and assign to a Unity material suitable for the project's render pipeline.
- Source rack objects share one mesh. Reuse the single-pin asset as a prefab in Unity; shared material alone does not guarantee a single draw call.
- UV0 deliberately samples palette swatches and overlaps. Disable mipmaps for this palette and avoid aggressive compression. There is no separate lightmap UV channel.
- The source profile follows the supplied stylized references, with a flattened standing base. Dimensions are design choices, not certified bowling equipment dimensions.
- Unity import, colliders, rigidbodies, centre of mass, scoring and headset performance are not implemented in this asset step. Use an independently configured convex/compound collision shape for future dynamic pins, not the decorative render mesh uncritically.
- Rebuild through Blender MCP by running `Blender/build_pins.py` after the compact lane exists. It refuses to run if the pin already exists.

See `../../../Journey/003-low-poly-bowling-pins.md` for the tutorial and actual Blender renders.
