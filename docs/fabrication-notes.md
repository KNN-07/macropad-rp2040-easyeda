# Bare-board fabrication notes

Apply these requirements to the released MACRO12-RevC-Gerber.zip. The exact manufacturing files passed the [CAM review](verification/cam-review.md).

| Parameter | Requirement |
| --- | --- |
| Board size | 59.69 x 104.14 mm nominal |
| Stack | Two copper layers, FR-4 |
| Thickness | 1.6 mm nominal; finished board must be at least 1.5 mm |
| Copper | 1 oz |
| Finish | ENIG |
| Mask / legend | Green soldermask / white silkscreen |
| Panelization | No panelization assumed |
| Drill plating | Preserve separate PTH and NPTH data and native plated slots |

## Internal LED apertures

There are 12 reverse-mount LED apertures, each **3.5 x 3.8 mm** nominal. Finished aperture dimensions must stay within **+/-0.1 mm**. Use a milling tool no larger than **1.0 mm diameter**, giving an internal corner radius no larger than **0.5 mm**. Do not substitute a larger router. Nominal copper-to-aperture clearance is 0.30 mm; the accepted dimensional range leaves at least 0.25 mm nominal geometric clearance at the adjacent lands.

The additional 12 x 4 mm OLED flex opening is intentional and must also be routed. There are thirteen internal openings in total.

## Plated slots

Preserve all six plated oblong holes:

| Part | Count | Nominal finished slot size |
| --- | --- | --- |
| Encoder SW1 | 2 | 4.0 x 2.0 mm; 13.2 mm center spacing |
| USB X1 long shell holes | 2 | 1.7 x 0.6 mm |
| USB X1 short shell holes | 2 | 1.4 x 0.6 mm |

The encoder slots must finish within +/-0.1 mm in both dimensions. The 3.9 x 1.9 mm minimum routed oblong still accommodates the manufacturer's recommended rectangular tab envelope. Match hole positions to the native drawing; do not resize or offset slots without reviewing the part fit and copper annulus.

## CAM acceptance

Inspect the actual manufacturing files for both copper layers, masks, legends, closed outer perimeter, all 12 internal apertures, PTH/NPTH separation, and six plated slots. Confirm plated slot dimensions, milling capability, finished thickness, and aperture tolerances with the chosen fabricator. These are job requirements, not an assertion that any default low-cost fabrication service automatically meets them.
