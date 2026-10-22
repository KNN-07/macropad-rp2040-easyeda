# BOM scope

`BOM-reference.csv` preserves the source-derived per-reference component list and adds the mechanically selected Rev C parts. SW1 and X1 values/footprint names now match the revised native project. `upstream-component-metadata.json` preserves selected metadata from the original import; it is historical source information, not a purchasing instruction.

The electrical circuit, values, references, and original library associations derive from Adafruit MacroPad RP2040 Rev D at commit `fdd7f2cb3bc2b3c7a9c0765780387647ea872141`. Selected mechanical parts and their drawing checks are documented in [mechanical-review.md](../docs/mechanical-review.md).

This is a **reference BOM, not a turnkey-PCBA-approved BOM or pick-and-place file**. Generic passive/IC values still need exact purchasable MPNs and ratings checked for the intended assembler. Supplier codes labeled upstream metadata are provenance, not verified live stock or order approval. R9 is DNP in the source.

`CADSide` reports the combined component's native placement side. Some footprints include objects on both board faces: the switch/keycap is on the user-facing bottom and the hot-swap socket is on the top/electronics face; the OLED outline and its flex-connector lands likewise span the assembly. Do not feed this column directly into automated assembly equipment. Obtain a native placement export and review each actual part's side, rotation, pin 1, and assembly process.

The OLED assembly needs the specified 16-pin folding panel and matching flex connector/process. A generic four-pin OLED module does not fit. Nuts, screw lengths, PCB thickness, and display insulation must satisfy [assembly.md](../docs/assembly.md). Keys, keycaps, backplate, spacers, and screws are mechanical assembly items rather than a fully sourced kit in this CSV.
