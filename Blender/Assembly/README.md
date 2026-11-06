# Complete bowling room

Open scene **BowlingRoom_Complete** in `../BowlingAssets.blend`. A standalone `BowlingRoom.blend` is also supplied in this folder after validation, containing the assembled scene and its dependencies.

## Layout

- Interior: 5.6 m wide, 13.8 m long, 3.3 m high. Blender X spans the room; +Y points toward the pins; Z is up.
- Playing surface and walking floor: Z = 0. Lane head pin remains Y = 7 m.
- Front player floor: Y = -4.2 to -1.5, across the room width. Lane approach remains Y = -1.5 to 0.
- Ball return root: (1.9, -1.5, 0). The walnut tray faces toward the front wall. Balls remain at their authored retrieval height, approximately 0.424 m; XR reach/comfort has not been tested.
- Layout markers: `Player_Start`, `Ball_Pickup_Stance`, `Throw_Stance`. They are references for later integration, not an implemented locomotion system.
- Six potted plants, two benches, six pendant fixtures, four ceiling diffuser strips and a blank screen above the pin deck. No text objects or wall lettering.

## Scene organisation

`ROOM | Complete asset assembly` contains the visible room and existing assets, under root `BowlingRoom`. Its child collections separate shell, ceiling, decor, plants, light fixture meshes, screen, lane, ten pins, return and three balls. Existing source scenes remain intact. Assembled copies share mesh data with the source assets; object transforms are independent. Make mesh data single-user if a future edit should affect only the assembly.

`ROOM | Blender lighting - do not export`, `ROOM | Review cameras - do not export` and `ROOM | Layout markers - do not export` are separate. The Blender lighting is for preview; do not transfer its nine area lights directly into a Quest runtime lighting setup.

## Later export and Unity integration

Exported and imported in Journey 009. FBX lives at `../Exports/Room/BowlingRoom.fbx`; the Unity scene is `XR_BowlingGame/Assets/Scenes/BowlingAlley.unity`.

- Export the complete asset collection with metre-aware settings. Keep pins and balls separate for future dynamics. Preserve the centre pivots of balls and base pivots of pins.
- Textures are packed in the blend. `RoomPalette.png` is the new 256 × 16 room atlas; the existing assets retain their own small palettes.
- The blank screen is a distinct material/mesh for later UI. Emission and material setup must be checked in the selected Unity render pipeline.
- Palette UV0 overlaps intentionally. Generate a separate UV channel if baking lightmaps. The many editable static pieces can be combined or statically batched during export/integration; triangle count alone is not a headset performance guarantee.
- Add appropriate floor/wall/fixture colliders, smooth ball colliders, pin collision and XR locomotion later. Decorative wall graphics, floor tiles and leaves should not independently become collision meshes.
- Floor panels exclude the lane footprint so the room floor does not fill the recessed gutters.
- The ceiling is separately grouped for inspection. The final scene includes the ceiling and all four walls; any roof-hidden layout render is only an inspection view.

See `Room_manifest.json`, `Room_validation.json`, and `../../Journey/007-room-assembly.md`.
