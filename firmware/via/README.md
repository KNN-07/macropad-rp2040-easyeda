# VIA configuration

[macro12-rev-c.json](macro12-rev-c.json) is the VIA V3 **sideload** definition for the `knn07/macropad_rev_c:via` QMK firmware in this repository. It exposes all 12 keys, the encoder push switch, both encoder directions, four firmware layers, and the standard QMK RGB Matrix controls. It does not require a separate desktop application.

1. Flash this project's **VIA** UF2 using the [firmware instructions](../README.md). The default QMK build does not enable VIA.
2. Open [VIA](https://usevia.app/) in a browser with WebHID support, such as Chrome or Edge.
3. In VIA's Settings, turn on **Show Design tab**. Open Design and load `macro12-rev-c.json` as a V3 definition. Leave the V2-definition option off if it is shown.
4. Select **Authorize device** / **Connect**, then choose **MACRO12 Rev C** in the browser's device chooser.
5. In Configure, select a key to change its assignment. Select the knob to configure its push and counterclockwise/clockwise actions. Layers 0-3 and the lighting menu are available.

VIA writes changes to the board's nonvolatile storage. Export a VIA layout backup before clearing EEPROM or installing firmware that changes the storage layout. Flashing new defaults alone does not necessarily replace settings already saved on the board.

This definition is distributed here and is **not registered for automatic discovery** in VIA's upstream keyboard repository. It must be loaded again if VIA's browser storage is cleared. VID `0x4B4E`, PID `0x124C` are this project's prototype/development identity, not a USB-IF-assigned vendor/product allocation. Do not use the stock Adafruit VIA definition: its USB identity differs.

The definition and firmware mapping are checked together in the repository tests. To also validate the JSON, parsed layout, encoder metadata, and menus with the official VIA reader, run `npm ci --ignore-scripts` then `npm test` in this directory (Node.js required). The reader version is locked in `package-lock.json`. USB connection, encoder direction, lighting, persistence across power cycles, and physical key positions still need testing on an assembled Rev C board.

The file follows the official [VIA specification](https://caniusevia.com/docs/specification/), [encoder layout rules](https://caniusevia.com/docs/layouts/), and [QMK configuration guidance](https://caniusevia.com/docs/configuring_qmk/). Its matrix matches the PCB's 13 direct GPIO inputs; the two empty top-row matrix positions are deliberately absent from the UI.
