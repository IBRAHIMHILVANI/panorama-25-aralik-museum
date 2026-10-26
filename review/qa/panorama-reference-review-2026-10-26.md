# Upper panorama architecture: three concrete corrections

Independent read-only review, 2026-10-26. Evidence: new local 360 screenshots 02, 03, 04, 13, 14, 15, and 16 under `references/live-review-2026-10-26/`; restored original photos `IMG_2239.jpg`, `IMG_2242.jpg`, and `IMG_2254.jpg` under the output texture directory; current `scripts/build_part07.py`. There is no 17-prefixed screenshot in the supplied directory at review time. The Google viewer displays May 2026 for the panorama; that is the displayed source date, not an independently verified capture date. No UI, export, or builder changes were made by this reviewer.

## 1. Replace selected solid parapet bays with the observed ironwork

**Observed:** Screenshot 13 clearly shows an ornate dark iron panel on a low stone curb, held between stone end piers, with dense curved scroll/diamond motifs and a narrow top rail. Screenshot 03/15 shows this ironwork at the **left edge of the tank-facing view**, adjoining the stone building corner and the foreground rubble. Screenshot 04/16 shows the walkway continuing beside **alternating solid low masonry and open iron bays**; it is not an uninterrupted opaque wall. The recognizable ruined facade with two timber window frames and the wagon-side mural in restored IMG_2242 help identify this adjacent terrace area, but do not establish a measured angle.

**Current mismatch:** `Panorama_Visitor_Parapet_*` extrudes virtually the entire outer ring from -0.03 to +0.78 m as opaque stone. Only the stair/landing interrupt it. No equivalent ornamental viewing rail is built.

**Bounded fix:** Alter only the photographed terrace bays adjoining the tank-view stone corner and the next visible ruined-window/wagon-side bay. Retain the low stone base and end piers, replace the opaque upper infill with dark metal top/bottom rails and repeated open scrollwork. Keep the other short stone parapet spans where visible. Retain a hidden continuous safety collider behind the open ironwork. Do not replace the full circular parapet or present chosen bay dimensions as measured.

**Confidence:** High that this local material/form correction is required; medium for relative placement beside the tank/ruined-window terrace; unresolved exact global angle and bay lengths.

## 2. Add the real stone passage arch and its identifiable facade context

**Observed:** Screenshots 02, 13, and 14 show a genuine walk-through **segmental masonry arch immediately to the right of a large dark timber double door**, with **two narrow upper windows** over the door. The arch has thick jambs and radial stone blocks. Cobblestones continue through it toward another viewing bay, and the panorama is visible beyond. Screenshot 13 places the ornamental railing across the foreground of this same terrace. This is a physical passage, not a mural feature or a rectangular display recess.

**Current mismatch:** The central `Village_Inner_Stone_Wall_*` is a plain continuous curved wall outside its two exhibit windows, while `Upper_Stone_Passage_*` supplies a straight roof and plain side walls. Neither reproduces this identifiable arch/door/two-window facade assembly.

**Bounded fix:** Create a local masonry facade module with the large timber door, two upper windows, and adjacent true arch aperture. Give the arch actual thickness, visible voussoirs, and continuous walkable paving through it. Connect it only after its local passage direction is reconciled with the surrounding terrace; do not drop it at an invented absolute ring angle or block the existing circulation with an unsupported cross-wall. Keep the nearby open viewing railing tied to the same local facade module rather than distributing arches around the ring.

**Confidence:** High for the assembly and adjacency of its components; unresolved for whether its opening maps to an existing access branch or another terrace bay in the current simplified plan. The photos do not establish the full hidden topology.

## 3. Refine the existing canopy into layered draped cloth

**Observed:** Screenshot 14, restored IMG_2239 above the tank, and IMG_2242 above the wagon show broad sagging sheets, overlapping edges, seams, dark repair patches, timber poles projecting beyond the cloth, and looped/tied ropes. Screenshot 04/16 also shows the loose scalloped edge over the walkway. The canopy is supported as a real feature; removing it would be wrong.

**Current mismatch:** `Village_Cloth_Canopies` repeats essentially the same 30-degree radial sheet around the ring. Its height is a linear radial pitch with a small 0.06 m sinusoidal ripple. Uniform radial beams and continuous timber edges do not reproduce the conspicuous folds, overlaps, patches, and projecting pole ends.

**Bounded fix:** Refine only the tank/wagon/facade canopy segments first: add broad drape sag between observed supports, nonuniform overlapping cloth edges, a few source-supported repair patches, sewn seams, projecting pole ends, and rope loops. Preserve the underlying established clearance and the open stair exit. Do not extrapolate a complete pole/rope count or patch map into unseen sectors.

**Confidence:** High for these local visible details; exact cloth dimensions, sag heights, support spacing, and unseen coverage remain estimates.

## Placement boundary

The current builder places tank and wagon at its own provisional angles (307 and 350 degrees). Those are implementation choices, not new facts obtained from the 360 screenshots. This review intentionally supplies **landmark-relative relationships only**. Use the tank, timber door with two upper windows, arch, iron terrace rail, and ruined double-window facade to reconcile a local group before changing the larger panorama plan.
