# Assembly controls

These requirements are binding conditions of the nine mechanical DRC exceptions documented in [mechanical-review.md](mechanical-review.md). They describe the intended assembly; no prototype has been measured.

## Board orientation and mounting

The user-facing switch/encoder/OLED side is the native bottom side. The electronics and hot-swap sockets are on the native top side. Combined library footprints can contain geometry for both sides; a CAD component's side is not a complete assembly placement instruction.

Use a nominal 1.6 mm board with **finished minimum thickness 1.5 mm**. TP1 through TP4 use Adafruit 4207 or a drawing-equivalent M3 solderable nut with 3.0 mm shoulder, seated nose no longer than 1.5 mm, and 5.56 mm body diameter. Mount the shoulders on the top/electronics side. Nut noses, solder, and screw tips must be flush with or recessed below the bottom/user-facing board plane in the switch zones.

For a 1.5 to 1.6 mm backplate, M3 x 5 mm screws provide approximately 3.4 to 3.5 mm nut engagement and at least 1.0 mm nominal recess from the user-facing plane. Different backplates or screws must satisfy the same projection requirement. Do not assume the upstream M3 x 6 mm screw recommendation fits a changed stack.

## Display and USB clearance

Use the **16-pin ZJY130-2864KSWLG22 folding OLED panel**, not a four-pin breakout. Fit a nonconductive insulating spacer beneath the glass that maintains at least **0.5 mm installed separation** from the bottom PCB surface after compression. Exposed solder or metal beneath the panel must project no more than **0.25 mm** from the board surface. Leave the flex exit and bend uncompressed, and do not clamp the driver IC or glass edge.

The selected HRO USB connector shell tails project 1.01 mm from its mounting plane and remain within a board of the specified minimum thickness. Excess solder can still protrude under the glass, so the insulation and solder-height limits remain required.

## Selected mechanical parts

- Encoder: **Bourns PEC11R-4215F-S0024**. Rev C uses 13.2 mm mounting-tab spacing; earlier 11.5 mm footprint revisions are superseded.
- USB: **HRO TYPE-C-31-M-12** (upstream supplier reference C165948).
- Reset: **G-Switch GT-TC054B-H035-L1** (upstream supplier reference C778159).
- RGB: **SK6812MINI-E**, reverse mount, with the specified routed aperture; similarly named LEDs are not dimensional substitutes.
- Display: **ZJY130-2864KSWLG22**, with the matching flex-connector sourcing and assembly process resolved by the assembler.

The 12 keys require MX-compatible switches and matching keycaps; check the chosen switch's optical opening if per-key lighting is required. The reference BOM is not an automatic-placement file. Confirm actual placement side, rotation, and pin 1 against the design and part drawings before assembly.

## First article

Before production quantities, inspect the mounting/insulation constraints and perform current-limited power/short checks, rail verification, BOOTSEL, USB enumeration in both orientations, all 12 keys, RGB, encoder, OLED, speaker, and peripheral checks. These tests follow bare-board fabrication.
