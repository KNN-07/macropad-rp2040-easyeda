# Rev C release validation

Review date: 2026-10-22. **Released for first-article bare-board fabrication, subject to the fabrication and assembly specifications.** No powered hardware or production qualification is claimed.

## Final checks

| Check | Result |
| --- | --- |
| Native copper rebuild | All three copper pours rebuilt and project saved |
| Native DRC | Nine component-to-through-hole mechanical findings only; no copper, routing, connection, board-edge, track-width or via-size findings |
| Native schematic/PCB comparison | Zero differences, nets and components included |
| Independent source net comparison | All 311 connected physical pads match; no missing or unexpected net |
| Native schematic geometry | 325 symbol pins checked: 311 connected and 14 intentional NC |
| PCB pad inventory | All 338 physical pads accounted for; 27 intentionally unconnected |
| Independent copper graph | All 76 connected nets have one conductive pad group |
| Routing inventory | 825 track segments, 92 vias, 96 component instances |
| CAM | All 171 holes/slots and all 338 pad copper/mask centers agree with the native design |
| Outline | Fourteen closed contours: outer perimeter, twelve LED apertures, one OLED flex opening |
| Silkscreen | 82 value labels hidden, twelve switch refs aligned, reset label moved inside outline, Rev C identification added |
| Archive integrity | Native and manufacturing ZIP CRCs pass; SHA-256 hashes published |

The final native archive SHA-256 is `fe8edbcd7436f06965ef6271b59c78525f9fc86215e9f7e83fc6b726cc4b44b5`. Detailed evidence is in [electrical review](verification/electrical-review.txt), [electrical measurements](verification/electrical-summary.json), and [CAM review](verification/cam-review.md). The latter names the exact export and per-file hashes. Text polishing changed no pads, components, tracks, vias, pours or electrical rules.

## Accepted mechanical exceptions

The nine remaining native findings are U$1/TP2, U$6/TP2, U$3/TP1, U$4/TP1, X2/X1_M1, X2/X1_M2, X2/X1_M3, X2/X1_M4 and X2/TP4. They are projected component-body overlaps with mounting pads on the opposite face. Each is accepted under the explicit [mechanical dispositions](mechanical-review.md) and [assembly controls](assembly.md); the global DRC rule remains enabled. This is not an unqualified zero-DRC claim.

Rev C matches the Bourns encoder, HRO USB-C and G-Switch reset drawings. SW2 moved 0.127 mm inward to obtain 0.305 mm board-edge clearance while preserving complete solder lands. All other component positions and electrical connections remain intact.

## Manufacturing package

Use `fabrication/MACRO12-RevC-Gerber.zip`. Its ten files are unchanged from the EasyEDA export. The redundant via-only drill file was omitted because all 92 vias are already in the primary PTH drill file; custom drawings, drill illustration and ordering/flying-probe files were omitted. No manufacturing geometry was rewritten during packaging.

The fabrication requirements include two layers, 1.6 mm nominal FR-4 with finished minimum 1.5 mm, 1 oz copper, ENIG, specified plated slots, and twelve 3.5 x 3.8 mm LED apertures within +/-0.1 mm with a router diameter no greater than 1.0 mm. Send [fabrication-notes.md](fabrication-notes.md) with the job. Select a fabricator that accepts these tolerances.

## Assembly and first article

The BOM is a reference list, not a turnkey-PCBA-approved procurement/CPL package. The folding OLED panel and connector process require the documented assembly arrangement. No board has been ordered, assembled or tested. Before increasing quantity, check shorts and supply rails, USB enumeration in both orientations, all twelve keys, RGB, encoder, OLED and retained peripherals. These are first-article validation steps after fabrication.
