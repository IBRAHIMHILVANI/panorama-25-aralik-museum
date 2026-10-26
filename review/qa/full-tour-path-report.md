# Continuous full-museum tour path — ready for rendering

Generated from all nine actual exported GLBs using one continuous capsule simulation. There is one initial placement inside the tram and no subsequent position resets or teleports.

**Passed:** 326/326 waypoints, 9,415 floor-support checks, and 3,732 part/body clearance checks; zero blocked waypoints, floor failures, or visible-body obstructions. Walking speed 1.8 m/s, camera eye height 1.65 m, capsule radius 0.30 m, physics integration 120 Hz, output 20 fps. Existing 0.01 m visible-body penetration tolerance retained.

The route lasts **470.708 seconds (7 min 50.7 sec)** and covers **642.889 m**, including 25 exhibit pauses. It starts inside the tram, walks to the first articulation and back to its open door, exits to the platform, follows the station-to-museum street route, enters the courtyard, crosses the atrium and descends its stairs, enters the cinema and walks its central aisle, returns through the map hall, visits parts03–06 including the lower Kastel alcove/access ramp, ascends the curved panorama stair, and completes a full upper viewing-ring circuit ending at the panorama.

## Files and renderer contract

- Generator: `scripts/make_full_tour_path.mjs`.
- Path: `reconstruction/full-tour-path-2026-10-26.json`.
- Validation: `review/qa/full-tour-path-validation.json`.
- Hash check: `review/qa/full-tour-path-hash-recheck.json`.

Coordinates are author-space metres, Z up. Every `samples[]` item has `t` in seconds, `position` as the camera eye, `look_target`, `stage`, `part`, and `floor_support_z`. `look_target` already limits yaw to 60 degrees/second and pitch to 45 degrees/second. `pauses[]` contains source-view names, times, targets, and stationary eye positions. `waypoints[]` and `waypoint_results[]` preserve the route and arrival evidence.

Use the sampled positions directly, interpolating only adjacent 0.05-second samples if the render frame rate differs. **Do not apply a spatial spline or smooth across corners**: that would depart from the collision-tested path. Orientation smoothing must not move the eye. A failed future generation writes a partial route with `validation.passed=false`; such a file is not a completed tour.

## Joins corrected through actual geometry checks

- Shifted a short station-sidewalk segment inward near [30,-52] to avoid riding the curb edge with no center floor support.
- Approached the Kastel access ramp around its lower end via radius40.8 before ascending, instead of cutting across its end/handrail.
- Rounded the atrium stair's lower parapet toe at y0.25 before crossing toward the map, avoiding its timber rail.
- Shifted toward the inner history-gallery aisle before the protruding `Community_Cart_Wood`, keeping the camera clear of its visible geometry.
- The regenerated part01 doorway no longer produces the decorative shop-frame intrusion found in the first pass.

These are bounded path corrections verified against the exported model, not new claims about measured museum circulation. No geometry, manifest, combined export, or browser UI was edited for this path task.

## Final-export recheck

All nine GLB hashes matched the saved validation at 2026-10-26T09:45:11.740Z. After any subsequent part export, run:

```sh
node scripts/make_full_tour_path.mjs --check-hashes
```

If a hash changed, regenerate the complete path and validation:

```sh
node --max-old-space-size=8192 scripts/make_full_tour_path.mjs
```

This deliverable is the verified continuous camera path. The parent still needs to render, inspect, and deliver the actual video.
