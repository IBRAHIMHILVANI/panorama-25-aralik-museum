# Cinema connection — independent geometry QA

Result: PASS on exported GLBs tested 2026-10-26 07:53 UTC.

User observation: the cinema is beside the stairs on the right. The implementation interprets right from the map-hall viewpoint. Exact dimensions, the connector shape, doorway coordinates, and room orientation have not been surveyed; this test establishes modeled walkability only.

`scripts/verify_cinema_connection.mjs` loads the exact exported part00, part02, and part08 meshes, preserving transforms and collision flags while excluding texture bytes. It uses the existing collision octree and the existing 0.30 m player capsule radius. All visible geometry and collision helpers are separately checked for torso/head clearance from 0.2 to 1.8 m above the floor, retaining the existing 0.01 m penetration tolerance.

The route starts at the lower stair landing [41.1,0.25,-4.2 floor], goes around the parapet end through [42.9,0.25], [43.5,2.4], and the doorway [44.5,2.4], crosses the front of the cinema through [45.3,2.4] to [45.3,0.11], then follows the central aisle to [51.5,0.11]. Both directions passed, covering 14 waypoints. The dense intended-route and actual movement checks cover 325 body samples; none intersects visible geometry beyond tolerance. Every sample has floor support at -4.2 m. Maximum dynamic floor-height deviation is 0.0000102 m.

The source review found front-wall panel-joint strips spanning the doorway. This was reported to the parent before testing. The tested part08 export includes the parent's correction; no obstruction remains in the tested route. The open door, jambs, lower parapet, outer-wall opening, seat envelopes, seat upholstery, ceiling, and outdoor part00 geometry are included in these checks.

Inputs (full hashes, timestamps, parameters, and every waypoint are in `cinema-connection-navigation.json`):

| Export | SHA-256 |
|---|---|
| part00.glb | 82d0deabc7a9613e89d3d6ed4d1315fc9587ca82082e06d32b1897f3d85f2ec7 |
| part02.glb | 24d1f26c654365833d8747784210206ed09b73f1d3244b5a409a086405c3114b |
| part08.glb | 7da3c3f4b5c7ae2d53470b315df74dbbcc36ee7e2e04e77e25606f04e745680f |

This targeted test starts at the stair bottom and does not replace the separate stair descent/ascent test, full nine-part navigation tests, browser review, or review against photographic evidence. It tests the central aisle and front cross aisle, not access to every chair between rows. No browser/UI was used and no builder or manifest was edited by this reviewer.

Re-run: `node scripts/verify_cinema_connection.mjs`.
