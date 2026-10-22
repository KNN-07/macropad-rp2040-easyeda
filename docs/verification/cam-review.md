# MACRO12 Rev C CAM review

**Result: pass for the reviewed manufacturing files.** The final Gerber/Excellon output agrees with the native design for every drilled feature and every physical pad's copper and soldermask layer. The top and bottom CAM previews were inspected after silkscreen polishing.

This review covers the ten-file manufacturing subset listed below. Each file is byte-for-byte identical to its corresponding file in the final EasyEDA export. No copper, mask, paste, outline or drill geometry was edited during packaging.

## Exact inputs

- Final native archive SHA-256: `fe8edbcd7436f06965ef6271b59c78525f9fc86215e9f7e83fc6b726cc4b44b5`
- Final raw Gerber archive SHA-256: `3326a4bcae18ed568e5ca56b4735d332cda8f85de1ed013fdec57a2f4a9ddbc0`
- Parser: Gerbonara 1.6.3; independent comparison against the extracted native project.
- Coordinate comparison tolerance: 0.0011 mm, accommodating export rounding.

## Checks and measurements

| Check | Verified result |
| --- | --- |
| Board outline | One closed 59.69 x 104.14 mm outer contour, with four corner arcs |
| Internal cutouts | Twelve closed 3.5 x 3.8 mm LED apertures and one closed 12 x 4 mm OLED flex opening |
| Outline closure | All 14 contours closed; every outline vertex has two incident segments |
| Plated drill file | 107 features: 92 vias, nine other round PTH holes and six plated slots |
| Non-plated drill file | 64 round NPTH holes |
| Native drill agreement | All 171 drilled features match native center, diameter, plating and slot endpoints; no missing or unexpected drill |
| Encoder slots | Two 4.0 x 2.0 mm plated slots; center spacing 13.2 mm |
| USB shell slots | Two 1.4 x 0.6 mm and two 1.7 x 0.6 mm plated slots |
| Pad copper and mask | All 338 physical footprint pads have their expected copper and soldermask opening centers on the correct layers |
| Polished silkscreen | Twelve socket references are inside the outline; dense value labels are hidden; `MACRO12 / REV C` is present |

The NPTH counts are 24 x diameter 1.8135 mm, 24 x diameter 3.2 mm, 12 x diameter 3.9 mm, two x diameter 0.65 mm and two x diameter 1.0 mm. Via drills are 88 x diameter 0.5 mm and four x diameter 0.3 mm. Remaining round PTH drills are five x diameter 1.0 mm and four x diameter 4.25 mm.

All SMD assembly pads are on **PCB top**. Key/encoder bodies and OLED glass face the opposite side. Local footprint layers can flip with their component instance; a component-side label alone is not sufficient for pick-and-place data. The bottom mask contains openings for the 15 plated component pads. A bottom paste file is not required for this board.

## Manufacturing subset

| File | Use |
| --- | --- |
| `Gerber_TopLayer.GTL` | Top copper |
| `Gerber_BottomLayer.GBL` | Bottom copper |
| `Gerber_TopSilkscreenLayer.GTO` | Top silkscreen |
| `Gerber_BottomSilkscreenLayer.GBO` | Bottom silkscreen |
| `Gerber_TopSolderMaskLayer.GTS` | Top soldermask |
| `Gerber_BottomSolderMaskLayer.GBS` | Bottom soldermask |
| `Gerber_TopPasteMaskLayer.GTP` | Top solderpaste / optional stencil |
| `Gerber_BoardOutlineLayer.GKO` | Board perimeter and routed cutouts |
| `Drill_PTH_Through.DRL` | All plated drills and plated slots, including vias |
| `Drill_NPTH_Through.DRL` | Non-plated holes |

The raw export's `Drill_PTH_Through_Via.DRL` is an exact subset of the 92 via holes already present in `Drill_PTH_Through.DRL`. It is omitted from the manufacturing subset to avoid duplicate drill instructions. Drill drawings, custom drawing layers, flying-probe JSON and ordering help are also excluded; they do not alter the manufacturing geometry.

Gerbonara accepted the Excellon files with a format warning that `G90` appears after the header. All drill coordinates parsed and matched the native data; no parser repair or drill-file modification was performed.

The associated electrical review confirms all 76 nets are connected. CAM review does not establish powered hardware operation or USB electrical compliance. Fabrication settings and the documented mechanical DRC exceptions remain part of the project manufacturing notes.

Per-file hashes and machine-readable measurements are in `cam-review.json`. `top.svg`/`top.png` show the electronics side; `bottom.svg`/`bottom.png` show the user-facing side. These previews were generated from the manufacturing layers, not a design mockup.
