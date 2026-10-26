# Bounded panorama improvements — 2026-10-26

Implemented in `scripts/build_part07.py` and new helper `scripts/panorama_reference_details.py`.

- **Tank-side ironwork:** replaced one provisional 288–306 degree solid parapet bay to the left of the model tank with a 0.24 m stone base, stone piers/caps, and actual open scroll/diamond ironwork. A continuous hidden collider remains behind it. Remaining masonry, the viewing route at radius 7.4 m, and the larger panorama arrangement are retained.
- **Tank/wagon canopy:** three overlapping cloth sheets in the bounded 288–360 degree sector have broad nonuniform sag, stitched seams, two localized repair patches, projecting timber supports, and tied/looped ropes. Their minimum sheet elevation is 2.621 m. The details follow restored IMG_2239/2242 and the new 360 evidence; individual dimensions and placement remain estimates.
- **Existing upper corridor:** round timber joists and two small warm cage lanterns follow newly restored IMG_2216/2217. Lanterns stay above 2.295 m. The passage route is unchanged; the unlocated arch has not been invented or placed.
- **Evidence and review views:** added `tankrail` and `canopydetail` cameras and `reconstruction/part07-reference-details.json`. Updated part07 notes to reflect all 319 restored original textures, verified by local file count. The notes distinguish observed forms from estimated metric placement.

## Validation

`python3 scripts/build_part07.py` passed: 336 scene objects, 244,363 vertices, 136,808 faces.

Blender part07 export passed: 332 visible meshes, zero nonfinite vertices, zero degenerate polygons. FBX roundtrip matched 332/332 meshes; maximum bounds error 0.000005245 m. FBX SHA-256: `ac4c072b4927bbb40ab2cec2eb852bf3511ef03dae3797a50e020fd65e5cdb9e`.

Existing `node scripts/verify_part07_navigation.mjs` passed all four routes against all nine exported parts: gallery approach, curved ascent, full panorama ring, return/descent. Its separate all-visible part07 body-clearance test passed 480 samples with zero obstructions at the existing 0.30 m capsule radius and 0.01 m tolerance.

Tested part07 GLB SHA-256: `7149a58715e8397a054d753dfbc48900f1bbb6563c19c1180669c00aa75c16d5`.

Evidence: `review/qa/part07-reference-details-export.log`, `review/qa/part07-reference-details-navigation.log`, `review/qa/part07-navigation.json`, and `review/qa/part07-clearance.json`. Native closeups `review/qa/native-part07/tankrail.png` and `canopydetail.png` were both rendered and visually inspected: open scrollwork, its stone base/piers, cloth edge sag, projecting support and hanging rope are visible. These checks establish the implemented details, not pixel parity or surveyed accuracy.

Exports refreshed: part07 `.blend`, `.fbx`, `.glb`, part07 walkthrough GLB/view list, and export verification JSON. No other part builder, combined export, or manifest was edited by this agent.
