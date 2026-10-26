# Station surface follow-up — ready for integrated part00 build

Changed only `scripts/museum_landscape.py`, new station source texture copies, and this follow-up's QA files. No part00 builder edits or exports.

## Grass

Replaced the flat median base material with a bounded clean-grass UV region from the original dated station photo `references/tram/YG01-2024-04-04-IMG_2115.jpg`. The complete original JPEG was copied unchanged into output and walkthrough texture folders as `Station_Grass_Original_2024_04_04.jpg`. Source and both copies share SHA-256 `61586236ba356ef489bf2bcdf32d2b27ce98a8757201d325d7ecf52c4ff5bf30`. No image generation, color correction, crop export, or pixel alteration is used for the material.

The sampled source quadrilateral is [(250,1330),(560,1228),(560,1275),(250,1375)] in the original 1368×1824 image. It was selected by inspecting the photographed grass band, excluding rails, paving, conspicuous litter, and canopy shadows. Small clipped patches keep every UV within this region; alternating UV reflection reduces obvious repetition without changing source pixels.

The geometry blades are now 2–4 mm wide and 8–26 mm above the turf surface, instead of approximately 12 mm wide and up to 70 mm above rail height. Density varies across the surface and individual positions remain procedural. The original median boundary and rails are retained. Texture scale and individual blade placement are estimated; the photo records 2024-04-04, not today's condition.

## Paving

Corrected the I-paver lattice. The prior notch width (±0.043 m) did not complement the staggered layout. The revised ideal tile uses ±0.06 m notch boundaries, a 0.24×0.17 m lattice, and a 0.12 m odd-row shift. A 1.5 mm inset on each side creates approximately 3 mm joints. Concave tiles are now constrained-triangulated rather than passed through as concave n-gons. A continuous muted grout surface lies just below the tiles, preventing gaps from revealing dark underlying voids. Tiles are clipped to the existing track bed and median/road boundaries. No new collision geometry is introduced.

## Focused checks

- Theoretical lattice before joint inset: uncovered area `8.13e-16 m²`, numerical overlap difference `-5.33e-15 m²`—effectively zero for both.
- Helper-only synthetic parallel-track smoke check passed: finite vertices, UVs inside the image, all new geometry noncolliding.
- Source/output/preview JPEG hashes match exactly.

Detailed helper evidence: `station-surface-followup-helper-check.json`. `station-surface-followup-source.json` will be generated with actual station area and texture provenance when the parent runs the integrated part00 build. Final native/browser appearance remains to be checked after that build; this report does not claim it has been rendered yet.
