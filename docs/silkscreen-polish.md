# Rev C silkscreen polish

The script changes only text visibility, reference text placement/style and one board identification string. It retains component names in the BOM and all designators unchanged. No copper, holes, component placement, polarity marks, footprint outlines or electrical mapping are edited.

- Hide visible `Name` attributes globally; this removes inherited component-value and SOCKET label clutter.
- Set the twelve switch references upright and unmirrored on top silkscreen, at 1.0 mm font size and 0.15 mm line width. Their X positions equal the switch columns (10.795, 29.845, 48.895 mm); Y positions are 2.54, 21.59, 40.64 and 59.69 mm. The bottom row lies above the identification text and inside the PCB edge; upper rows repeat the 19.05 mm key pitch. These bands lie below the socket body envelopes.
- Move SW2 reference from outside the right edge to (54.6,82.3) mm, upright at 0.8 mm font size. This leaves the reset switch signal lands and mounting lands unobscured.
- Add `MACRO12 / REV C` at (29.845,1.0) mm, centred, 0.8 mm font size and 0.15 mm line width. The centre of the lower margin is clear of the three socket footprints and corner mounting hardware.
- Keep other small designators and all polarity marks. Re-run native DRC and inspect final silkscreen CAM after application.

API signatures were checked in the installed official `@jlceda/pro-api-types` declarations: `PCB_PrimitiveAttribute.getAll`, `modify`; `PCB_PrimitiveString.getAll`, `create`; alignment mode 5 is CENTER, layer 3 is top silkscreen. The script validates the twelve unique target designators before editing and avoids creating a duplicate revision label when rerun.
