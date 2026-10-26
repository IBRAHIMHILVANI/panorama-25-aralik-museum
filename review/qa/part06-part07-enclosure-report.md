# Final basement and panorama enclosure repair

2026-10-26. The first captured video remains QA evidence; these changes require recapture. The camera route was not moved to conceal the defects.

## Root causes and source fixes

**Part06, tour367s:** Removing the temporary part07 review boundary exposed the entire 12 m end of the gallery. Part07's narrower oblique tunnel did not close its flanks or the height difference above its lower ceiling. A permanent wall now closes the gallery end with an actual 3.30 m wide × 2.60 m high passage opening. Short side returns and triangular floor/ceiling infills join the existing tunnel. A separate 0.15 m ceiling-step closure seals the part05/06 height difference. Original IMG_2189,2210,2211,2213 support an enclosed basement; the model's exact dimensions remain estimates.

**Part07, tour387s:** The tunnel side walls stopped short of the curved stair foot and the radial stair end was open. A continuous local wall/ceiling shell now follows the union of the existing tunnel tail, round landing, and first stair segment. The entire continuing stair flow is removed from the new wall shell, preserving ascent and descent. The junction roof follows the stair rise and excludes the already-covered stairwell to avoid overlapping roof faces.

**Part07 roof/underside:** The existing stair roof ended 0.07 m short of each side-wall plane. Roof and underside now extend through those wall planes. The upper landing is covered, and a plain enclosing roof closes the existing panorama shell at its established 12.8 m height. This is an architectural enclosure estimate, not a claim about unseen roof construction.

**Small foundation leak at387s:** Exact image rays through pixels655/488,658/487,660/494 previously hit no visible geometry. A solid foundation below the lowest walking floor now closes the under-stair void. Its top is z=-4.42 m, 0.22 m below the lowest route floor. All three original rays now hit `Panorama_Stair_Below_Floor_Foundation`; the camera and walkway surfaces are unchanged. The dark patch tested at390s hits an interior stone-wall surface, not exterior sky.

## Visual evidence

- Same367s pose before: `part06-enclosure-before-tour367.png`.
- Same367s pose after: `part06-enclosure-after-tour367.png`; sky and external building are replaced by the enclosing wall and open passage.
- Stair-foot baseline: `part06-enclosure-after-tour387.png` (before07 correction).
- Final stair-foot views: `part06-enclosure-after07-tour387.png` and `part06-enclosure-after07-tour390.png`.
- Upper exit: `part06-enclosure-after07-tour394.png`; no exterior blue sky above the exit.
- Final parent-owned storefront boundary correction was included in `part06-enclosure-after07-hospital.png`: no black storefront glazing/fascia intrudes in front of the mural.
- The native review script loads the existing master and substitutes current part00/01/06/07 only in memory. It never saves or recombines the master file.

## Verification

- Part06 FBX roundtrip:179/179 meshes, maximum bounds error0.000006676 m.
- Part07 FBX roundtrip:342/342 meshes, maximum bounds error0.000003815 m.
- Part06 navigation4/4 and225 visible-body samples passed.
- Part07 navigation4/4 and480 visible-body samples passed.
- Full continuous tour:326/326 waypoints,9,415 floor samples and3,732 visible-body checks, zero floor or visible-body failures, duration470.708333 s.
- All nine path/GLB hashes matched in the final check at2026-10-26T09:45:11.740Z.
- Final part06 GLB:`866bf076bba6b4ce46152b213a2d192f73fce4583ee4dbb55f48b71369198b7a`.
- Final part07 GLB:`33df799abd49e45f2c4cb08001b362dc739094e1cf0bc2a0840a0d26a7bec4c8`.

Evidence logs: `part06-enclosure-export.log`, `part06-enclosure-navigation.log`, `part07-stair-foot-enclosure-export.log`, `part07-stair-foot-enclosure-navigation.log`, `part07-stair-foot-ray-diagnosis.json`, `part07-stair-foot-ray-after.json`, `full-tour-path-validation.json`, and `full-tour-path-hash-recheck.json`.

Changed sources: `scripts/build_part06.py`, `scripts/build_part07.py`, `scripts/review_part06_enclosure.py`, and `scripts/verify_panorama_enclosure_rays.mjs`. Refreshed06/07 scene notes and exports plus the complete tour path/hash evidence. No parent-owned00/01 builders, manifest, recorder UI, or combined master were edited by this agent.
