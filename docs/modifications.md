# Changes from Adafruit MacroPad RP2040 Rev D

The electronic circuit is derived from the upstream Rev D source at commit `fdd7f2cb3bc2b3c7a9c0765780387647ea872141`. Original EAGLE files are preserved under `hardware/upstream/`. The EasyEDA archive is the revised canonical design.

## Routing and import repairs retained in Rev C

- Imported the two-sheet schematic, board, symbols, and footprints into EasyEDA Pro.
- Restored ground continuity with explicit tracks and four added stitching vias.
- Restored 5 V continuity around divided copper pours using 16 mil tracks.
- Preserved the original N$24 route and checked source-pad/net parity.
- Changed the 12 reverse-mount LED apertures to 3.5 x 3.8 mm, retaining 0.30 mm nominal clearance to LED lands, and rerouted adjacent tracks.
- Replaced duplicated encoder milling geometry with native plated oblong holes.
- Adjusted reset-switch signal lands to remove NPTH clearance findings.
- Removed three artwork component wrappers and reconciled schematic/PCB component metadata. Original source attribution is retained, with source metadata in `bom/upstream-component-metadata.json`.

## Rev C sourced-part corrections

- **SW1:** selected Bourns PEC11R-4215F-S0024. Moved the two mounting-tab holes to 13.2 mm center spacing and enlarged the plated oblongs to 4.0 x 2.0 mm for routed-hole corner clearance. Preserved the existing copper ovals and electrical pin locations.
- **X1:** selected HRO TYPE-C-31-M-12. Increased the short shell-slot length from 1.2 to 1.4 mm and the narrow/shared SMT-land widths to 0.300/0.600 mm respectively. Preserved all centers and 1.15 mm land lengths.
- **SW2:** corrected mounting lands for G-Switch GT-TC054B-H035-L1 to symmetric 1.5 x 1.5 mm rectangles at local centers (+/-3.45,+0.85) mm. Preserved the reviewed signal lands and peg holes.
- Updated SW1/X1 value text consistently in PCB, schematic, and project device metadata. Hid long PCB value strings to avoid silkscreen crowding while retaining reference designators.
- Reviewed nine projected mechanical overlaps as conditional assembly exceptions. Their individual evidence and requirements remain visible in [mechanical-review.md](mechanical-review.md).

The Rev C edit audit found no changes to board placements, nets, line tracks, vias, or global DRC rules. Native pours must be rebuilt and manufacturing exports checked after these footprint changes. Upstream production history does not validate revised geometry by itself.

## Final placement and silkscreen

SW2 moved 0.127 mm inward to retain full manufacturer-sized mounting lands with 0.305 mm edge clearance. Hidden 82 component value labels, aligned twelve switch references on top silk, moved the reset reference inside the outline and added MACRO12 / REV C. Copper and net assignments did not change during text polishing.
