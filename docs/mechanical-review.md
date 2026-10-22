# MACRO12 Rev C mechanical release review

Date: 2026-10-22. This is a drawing/geometry review, not a hardware test or a mass-production qualification.

## Decision

The nine RC1 component-to-through-hole DRC findings describe intentional opposite-side assemblies. They are not copper shorts and do not require moving the switches, OLED, USB connector or mounting holes. They may be accepted as individual documented exceptions **with the assembly controls below**. Do not disable the global component/through-hole rule. Prototype bring-up is a post-fabrication validation step, not a prerequisite for ordering bare boards.

Three sourced-part footprint corrections have been prepared in the Rev C EasyEDA project. Native repour, electrical DRC and CAM review must run on the imported revision before the manufacturing package is released. RC1 is not the revised source.

## Exact footprint changes

Coordinates below are local footprint coordinates in millimetres, before component-side mirroring/rotation. Native data is in mil, converted with 0.0254 mm/mil. SW2 was subsequently shifted 0.127 mm left as described below. The other 95 board placements, all pin numbers, pad nets, line tracks, vias and design rules were retained.

| Part | Change | Reason |
|---|---|---|
| SW1, `ec0d4ee4cd68a5e5` | P$GND1/P$GND2 centres from (-5.75,0)/(+5.75,0) to (-6.60,0)/(+6.60,0). Plated vertical slots 3.6×1.8 → 4.0×2.0. Existing vertical copper ovals 5.6×2.8 retained. | Lock Bourns PEC11R-4215F-S0024. Its tab pitch is 13.2 mm. A/C/B remain at (-2.5,-7.5)/(0,-7.5)/(+2.5,-7.5); push-switch pins remain (±2.5,+7.0). |
| X1, `03ad4029ad35c2fc` | M3/M4 short-slot length 1.2 → 1.4, width 0.6 unchanged. Eight narrow SMT lands 0.275 → 0.300 wide; four shared power/GND lands 0.575 → 0.600 wide. All land centres and 1.15 mm lengths retained. | Match the HRO TYPE-C-31-M-12 drawing, dated 2020-12-08. Its short shell-slot length is 1.40, long slots 1.70. |
| SW2, `8b616c3009a64c23` | MT1 from (3.175,0.9), MT2 from (-3.075,0.9), both 1.75×1.0, to symmetric centres (±3.45,+0.85), each 1.50×1.50. | Envelop the G-Switch recommended L-shaped mounting lands: abs(x)=2.7..4.2, y=0.1..1.6. Symmetric rectangles retain the full solderable area. |

SW2 signal lands remain centred at (±2.1,-1.0), with local-axis envelope 1.1×1.3. The GT-TC054B-H035-L1 drawing recommends 0.9×1.2 at those centres relative to the peg row at y=+0.3; the existing slightly larger lands are acceptable and preserve approximately 0.263 mm diagonal clearance to the 1.0 mm NPTH. Peg pitch remains 2.3 mm. Source peg diameter is up to 0.8 mm; the drawing's recommended PCB hole is 0.9 mm, so the existing 1.0 mm hole is a clearance enlargement.

The encoder oblong is deliberately larger than the manufacturer's nominal 1.8×2.6 rectangular recommended hole to allow a routed rather than sharp-corner hole. Even a 3.9×1.9 finished oblong contains that rectangle (corner radius calculation 0.948683 mm ≤ 0.950 mm). Nominal copper margin is 0.4 mm along the slot sides and 0.8 mm at its ends. Slot positional and finished-size tolerances still belong in the fabrication specification.

The USB source footprint's name was misleading, but its centres match HRO: signal-land bottom is 0.5 mm beyond the peg row; top is 1.65 mm versus drawing 1.64; peg pitch 5.78; shell-row pitch 4.18. Shell pitch 8.64 versus drawing 8.65 differs by 0.005 per side, within the drawing's ±0.05 PCB-layout tolerance. No connector relocation is required. KiCad's public HRO footprint has different, extended hand-soldering lands and older short slots; the current HRO drawing was used for this change.

The complete SW2 component was shifted 5 mil (0.127 mm) toward the board interior to preserve the full mounting lands while meeting the outline rule. Global position changed from (57.912,84.455) to **(57.785,84.455) mm**, with rotation 270 degrees unchanged. Its outer mounting-land edge is now x=59.385; the board edge is x=59.690. Clearance therefore increases from 0.178 mm (7 mil) to **0.305 mm (12 mil)**, exceeding the 0.254 mm (10 mil) rule. The signal pads and locating holes move together; no land clipping is used. The new peg-hole centres are (58.085,83.305) and (58.085,85.605). Their calculated minimum clearances to retained routed copper are 0.873 mm and 0.471 mm respectively. The actuator still projects approximately 0.495 mm beyond the board edge according to the source body outline. Native DRC must verify the final placed component after copper rebuild.

Existing Name values were changed consistently in PCB, both affected schematic instances and project device attributes: SW1 `PEC11R-4215F-S0024`, X1 `TYPE-C-31-M-12`. Long PCB value text was hidden to avoid silkscreen crowding; reference designators remain. Footprint titles reflect the sourced parts. No new unmatched custom properties were added.

## Nine mechanical DRC dispositions

The EasyEDA component side is not the side on which every item in a combined footprint physically sits. The key footprint includes its switch/keycap on the bottom user-facing side and its hot-swap socket on the top electronics side. X2 similarly combines a bottom OLED panel outline with top flex-connector lands. The upstream EAGLE package definitions and native placement/side records agree.

| Reported finding | Geometric evidence | Disposition/control |
|---|---|---|
| U$1 / TP2_P$1 | Key centre (48.895,10.795); TP2 (55.880,19.050). | Intentional switch/keycap projection over a board-level mounting-pad region. Use the flush/recessed mounting constraint below. |
| U$6 / TP2_P$1 | Key centre (48.895,29.845); same TP2. | Same. |
| U$3 / TP1_P$1 | Key centre (10.795,10.795); TP1 (3.810,19.050). | Same. |
| U$4 / TP1_P$1 | Key centre (10.795,29.845); same TP1. | Same. |
| X2 / X1_M1 | USB slot centre (34.165,98.503) lies under projected glass. | Opposite-side connector body; use OLED insulation/solder-height control below. |
| X2 / X1_M2 | USB slot centre (25.525,98.503). | Same. |
| X2 / X1_M3 | USB slot centre (34.165,102.683). | Same. |
| X2 / X1_M4 | USB slot centre (25.525,102.683). | Same. |
| X2 / TP4_P$1 | TP4 (55.880,100.330) lies under projected glass. | Top-side nut, flush/recessed lower face, plus OLED insulation. |

All global coordinates are in millimetres in the source/native board coordinate system (Y up). The ZJY130-2864KSWLG22 panel occupies nominal x=24.406..58.906 and y=79.8585..102.8585. The panel specification is 34.5×23.0×1.4 mm; ±0.2 for panel width/height and ±0.1 thickness. PCB outline is 59.69×104.14 mm, so the nominal closest panel-to-outline edge margin is 0.784 mm. Keep the displayed panel outline as an assembly envelope; deleting it to erase warnings would hide useful information.

## Binding assembly controls for these exceptions

1. Use 1.6 mm nominal PCB thickness with **finished minimum 1.5 mm**. This minimum matters for the press-in noses and USB shell tails.
2. TP1–TP4: use Adafruit 4207 or a drawing-equivalent M3 solderable nut with 3.0 mm shoulder, no more than 1.5 mm seated nose, and 5.56 mm body diameter. Mount the shoulders on the **top/electronics side**. The source footprint has the supplier's 4.25 mm hole and approximately 6.2 mm solder ring. Nut nose, solder and screw tips must be flush with or recessed below the bottom/user-facing PCB plane in the switch zones.
3. For a 1.5–1.6 mm backplate, M3×5 mm screws provide 3.4–3.5 mm engagement in these nuts while leaving at least 1.0 mm nominal recess to the user-facing plane. If a different backplate/screw is used, enforce the projection requirement; do not blindly use longer screws. The upstream M3×6 recommendation was for its original stack and is not a universal length.
4. X2: fit the **16-pin ZJY130-2864KSWLG22 folding panel**, not a four-pin breakout module. Add a nonconductive insulating spacer beneath the glass that maintains at least **0.5 mm installed separation** between glass underside and bottom PCB surface, including after compression. Keep exposed solder or metal under the panel at no more than **0.25 mm projection** from the PCB. This leaves at least 0.25 mm vertical mechanical clearance and prevents electrical contact with the panel/flex. Leave the flex exit and its bend uncompressed; do not clamp the driver IC or glass edge.
5. The HRO USB drawing gives shell-tail projection 1.01 mm from its mounting plane; with the 1.5 mm minimum board, those tails remain inside the PCB thickness. The user-facing hazard is excessive solder rather than the connector shell itself. The OLED insulation requirement remains in force even when tails are recessed.

These are design/assembly requirements derived from the drawings; they are not claims that an assembled prototype has been measured. Bare-board fabrication can proceed after native electrical DRC and CAM pass. First-article assembly should verify the constraints and normal USB/keys/RGB/encoder/OLED operation before a production quantity.

## LED apertures and milling

The twelve reverse-mount SK6812MINI-E apertures are 3.5×3.8 mm. Specify a milling tool no larger than 1.0 mm diameter, internal corner radius no larger than 0.5 mm, and finished aperture dimensions within ±0.1 mm. The LED drawing gives a nominal 3.2×2.8 mm body with ±0.1 mm general tolerance. At the smallest accepted opening (3.4×3.7) and largest body (3.3×2.9), a centred body corner is 0.461 mm from the centre of the 0.5 mm routing arc and therefore clears the rounded opening. Nominal copper-to-cutout clearance is 0.30 mm; a 0.10 mm wider aperture reduces it to 0.25 mm. These limits must be carried into the fabrication notes and CAM review; a larger router is not an equivalent substitution.

## Evidence and limitations

- Controlled-edit audit: 95 of 96 placements unchanged; the sole placement change is SW2 X=2280 to 2275 mil. All 825 line tracks, 92 vias, 2503 PAD_NET records, 3 pour definitions and 18 rules remain identical; all other pads are identical. Existing pours must be rebuilt because their geometry is stale after footprint edits. ZIP archive CRC passed.
- Upstream element/package records and native component side/rotation records were compared directly for this mechanical review.
- No automatic PCBA-ready BOM was signed off. The retained OLED assembly includes flex-connector lands; its connector sourcing and process must be specified by the assembler. This does not change bare-board geometry or the documented DRC dispositions.
- This review does not replace CAM inspection of outline, apertures, drill plating, masks and copper, and does not report later native DRC results.

## Primary drawing sources

- OPSCO SK6812MINI-E drawing: https://cdn-shop.adafruit.com/product-files/4960/4960_SK6812MINI-E_REV02_EN.pdf
- Bourns PEC11R, page 2, PEC11R-4xxxF-Sxxxx: https://www.bourns.com/docs/product-datasheets/pec11r.pdf. The older PEC11 also uses 13.2 mm; neither fits the prior 11.5 mm tabs without correction.
- G-Switch GT-TC054X-HXXX-LX, drawing dated 2019-05-29: https://atta.szlcsc.com/upload/public/pdf/source/20220602/C5A619D7A0B3BC1B0287E0B33D1EE15E.pdf.
- HRO TYPE-C-31-M-12, manufacturer drawing 2020-12-08, distributor-hosted copy: https://www.hestore.eu/en/prod_getfile.php?id=21618. Manufacturer product identity: https://www.krhro.com/Product-Details/726.html
- Zhongjingyuan ZJY130-2864KSWLG22 Ver B, pages 4–5: https://cdn-learn.adafruit.com/assets/assets/000/103/268/original/1.3inch_16pin_ZJY130-2864KSWLG22_VER_B.pdf.
- Adafruit 4207 nut dimensions and recommended hole/ring: https://www.adafruit.com/product/4207
- Upstream assembly orientation/backplate: https://learn.adafruit.com/adafruit-macropad-rp2040/macropad-assembly
- Upstream source: https://github.com/adafruit/Adafruit-MacroPad-RP2040-PCB, commit fdd7f2cb3bc2b3c7a9c0765780387647ea872141.
