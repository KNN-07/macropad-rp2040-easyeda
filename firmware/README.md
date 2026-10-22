# MACRO12 Rev C firmware

QMK firmware for the **Rev C** PCB in this repository, with standard and VIA builds. Both include all twelve keys, encoder rotation and push, per-key RGB, and the 128x64 SPI SH1106 OLED. The source is adapted from QMK's Adafruit MacroPad port and uses the independently checked Rev C pin map.

**Status: build and validation results are recorded in [validation.md](validation.md). Physical hardware has not been assembled or tested.** The speaker amplifier is deliberately held off, and no STEMMA QT application is included. Flashing does not validate PCB assembly.

## Install

1. Download `MACRO12-RevC-via.uf2` from the [firmware release](https://github.com/KNN-07/macropad-rp2040-easyeda/releases/tag/v0.2.0). Use `MACRO12-RevC-default.uf2` if you prefer a fixed, source-configured QMK map without VIA's Raw HID interface.
2. Connect the board by a USB **data** cable while holding the encoder down. Release the encoder when the `RPI-RP2` drive appears. With power already connected, hold the encoder, press/release the side reset button, then release the encoder.
3. Copy exactly one `.uf2` file onto `RPI-RP2`. The drive should disappear and the board should reconnect as **MACRO12 Rev C**. Do not copy the VIA JSON to the boot drive.
4. For the VIA build, follow the [one-time VIA definition import](via/README.md). The repository includes a compatible V3 definition; automatic discovery in VIA has not been registered upstream.

Once QMK runs, double-tapping the side reset button within 500 ms also enters the bootloader. The hardware encoder-plus-reset method works independently of firmware. Bootmagic: hold the **top-right key** (GP3, F15 on the default map) while connecting USB to reset QMK/VIA settings and enter the bootloader. That operation clears saved remaps/macros/lighting; export your VIA layout first if you want to keep it. After a normal UF2 update, existing VIA EEPROM mappings are retained and can override newly compiled defaults.

## Default controls

Look at the switch/keycap side, with USB at the top, OLED upper-left, and encoder upper-right. The PCB electronics-side view is mirrored.

| Layer 0: app shortcuts | | |
| --- | --- | --- |
| F13 | F14 | F15 |
| F16 | F17 | F18 |
| F19 | F20 | F21 |
| F22 | F23 | F24 |

Bind these keys in your applications, or remap them and assign macros in VIA. Turn the encoder for volume; tap it to mute. Hold it to access layer 3 controls (200 ms hold, or another key pressed while holding):

| Layer 3: hold encoder | | |
| --- | --- | --- |
| Previous track | Play/pause | Next track |
| Ctrl+X | Ctrl+C | Ctrl+V |
| RGB on/off | Next RGB effect | Increase hue |
| Select layer 0 | Select layer 1 | Select layer 2 |

While holding the encoder, turn it to change RGB brightness. Layer selection lasts until another selection or power cycle. Controls are on the highest layer so they remain accessible from navigation and numpad modes. The Ctrl shortcuts target Windows/Linux; macOS users can remap them to Command in VIA.

| Layer 1: navigation | | |
| --- | --- | --- |
| Home | Up | End |
| Left | Down | Right |
| Page Up | Page Down | Delete |
| Escape | Enter | Backspace |

| Layer 2: numbers | | |
| --- | --- | --- |
| 7 | 8 | 9 |
| 4 | 5 | 6 |
| 1 | 2 | 3 |
| 0 | Decimal period | Enter |

Layer 1 encoder: Page Up / Page Down. Layer 2 encoder: Left / Right. Number keys use ordinary digit keycodes, so Num Lock is not required; punctuation follows the host keyboard layout. Every switch and both encoder directions can be remapped independently on each of the four VIA layers. Preserve a route back to layer 0 when remapping layer controls.

## Hardware behavior

- OLED shows firmware, current layer number, RGB state/brightness, and host lock state. It sleeps after 60 seconds of inactivity. Layer numbers remain accurate after VIA remapping.
- RGB defaults to cyan at 48/255 brightness, is capped at 96/255, and turns off during USB suspend. The USB descriptor requests 500 mA. The cap is a conservative setting, not a measured current guarantee.
- Audio is disabled; GP14 amplifier enable and GP16 audio input are driven low. There are no startup or keypress sounds. Enabling audio later requires deliberate source changes and a fresh hardware/power review.
- QMK's flash-backed, wear-levelled EEPROM stores VIA maps, macros and lighting. The W25Q64 has 8 MiB, but this port keeps the generic QMK 2 MiB window, reserving its last 8 KiB for 4 KiB logical EEPROM. The remaining flash is unused.
- USB `4B4E:124C` identifies this development build and matches the VIA JSON. This is a prototype identity, not a claim of a USB-IF vendor allocation; obtain an appropriate identity before commercial distribution. The port does not impersonate Adafruit's VID/PID.

See [pinout.md](pinout.md) for all GPIO assignments and [first-article.md](first-article.md) for the hardware test procedure.

## Build from source

The workflow [Build QMK firmware](../.github/workflows/firmware.yml) builds both keymaps on Ubuntu 24.04 and uploads UF2 files, ELF/BIN/MAP debug outputs when available, logs and a SHA-256 manifest. It does not flash hardware or publish releases automatically.

On Linux or a configured QMK MSYS environment, install the [QMK prerequisites](https://docs.qmk.fm/newbs_getting_started) and Python 3.12, then run from this repository root:

```sh
python -m pip install qmk==1.2.0
python -m unittest discover -s firmware/tests -v
cd firmware/via
npm ci --ignore-scripts
npm test
cd ../..
python firmware/scripts/build.py --qmk-dir ../qmk-macro12 --output-dir artifacts
```

The helper creates a fresh QMK checkout at the exact commit in [toolchain.json](toolchain.json), initializes required pinned submodules, installs QMK's Python requirements, copies this port, runs QMK lint, compiles both keymaps, and validates their UF2 structure, RP2040 family, flash range, bootloader CRC and vector table. An existing QMK directory must already be at the pinned commit with no tracked modifications. Use a separate checkout for this build. Linux CI is the tested build environment; native Windows/QMK MSYS execution is not claimed tested.

The QMK source and CLI versions are pinned. OS/Python dependency versions are recorded with the artifacts; bit-for-bit reproducibility across arbitrary toolchain versions is not claimed.

To use an existing checkout manually, copy `firmware/qmk/keyboards/knn07/macropad_rev_c` into its `keyboards/knn07/` directory and run:

```sh
qmk compile -kb knn07/macropad_rev_c -km via
# or: qmk compile -kb knn07/macropad_rev_c -km default
```

## License and source

Firmware source and build/test scripts are **GPL-2.0-or-later**, separate from the hardware's CC BY-SA 3.0 license. See [LICENSE-GPL-2.0.txt](LICENSE-GPL-2.0.txt). The derived board configuration preserves Jose Pablo Ramirez's upstream copyright notice. QMK and its submodules retain their respective notices and licenses; the exact source revisions and retrieval commands are provided by the toolchain lock and build script. The VIA definition and firmware documentation are also provided under GPL-2.0-or-later. The VIA parser used for validation retains its upstream package license.
