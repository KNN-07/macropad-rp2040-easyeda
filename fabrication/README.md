# Rev C fabrication package

Upload **MACRO12-RevC-Gerber.zip** to the fabricator. The `gerbers/` folder contains the exact same ten files for inspection. Read and supply [fabrication requirements](../docs/fabrication-notes.md), especially aperture milling tolerance, router diameter and minimum finished board thickness.

The ZIP contains two copper layers, two solder masks, two silkscreens, top paste, the closed outer/internal routed outline, one complete plated drill file and one non-plated drill file. There are no bottom-side SMD pads, so no bottom paste layer is needed.

All 92 vias are already in `Drill_PTH_Through.DRL`. The redundant EasyEDA via-only file is deliberately omitted. No geometry was modified in this package. See the [CAM report](../docs/verification/cam-review.md).

This is a first-article bare-board release. The hardware has not been physically tested. Follow the documented [assembly constraints](../docs/assembly.md).
