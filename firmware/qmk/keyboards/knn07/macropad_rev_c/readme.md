# MACRO12 Rev C

QMK target: `knn07/macropad_rev_c`. The `default` and `via` keymaps share the same four presets. The VIA variant adds live remapping and persistent configuration; it does not enable speaker audio.

This is a port of QMK's `adafruit/macropad` target, originally contributed by Jose Pablo Ramirez (`Jpe230`). Original GPL-2.0-or-later notices are retained. It targets the MACRO12 Rev C hardware derived from Adafruit MacroPad RP2040 Rev D. This firmware has not been tested on an assembled MACRO12 board.

## Defaults

Viewed from the keycap side, the twelve switches are ordered left to right, top to bottom. The encoder push is the thirteenth switch.

| Layer | Row 1 | Row 2 | Row 3 | Row 4 | Encoder CCW / CW |
| --- | --- | --- | --- | --- | --- |
| 0: App bindings | F13 / F14 / F15 | F16 / F17 / F18 | F19 / F20 / F21 | F22 / F23 / F24 | Volume down / up |
| 1: Navigation | Home / Up / End | Left / Down / Right | Page up / Page down / Delete | Escape / Enter / Backspace | Page up / down |
| 2: Numbers | 7 / 8 / 9 | 4 / 5 / 6 | 1 / 2 / 3 | 0 / . / Enter | Left / Right |
| 3: Controls | Previous / Play-pause / Next | Ctrl-X / Ctrl-C / Ctrl-V | RGB toggle / Next effect / Hue up | Base / Navigation / Numbers | RGB brightness down / up |

Tap the knob for mute; hold it for layer 3. While holding it, press a bottom-row key to select the persistent working layer. Layer 3 has the highest priority so the controls remain reachable from every preset. The hold resolves at 200 ms, or when another switch is pressed. Windows/Linux editing shortcuts use Control; change them to Command in VIA or source for macOS. Number keys use the number row, independent of host Num Lock.

RGB starts cyan at brightness 48/255 and is capped at 96/255. RGB turns off during USB suspend. OLED shows active layer number, RGB level and host lock flags; it sleeps after 60 seconds of inactivity. OLED text deliberately does not claim to describe remapped VIA keys. All presets are silent: GPIO14 drives the amplifier shutdown low and GPIO16 is held low. STEMMA QT has no peripheral driver enabled.

## Recovery and persistence

- Hold the encoder button while connecting USB or while pressing/releasing RESET to use the hardware BOOTSEL path. Copy the desired UF2 to `RPI-RP2`.
- With this firmware running, double-tap the side RESET button within 500 ms to enter the bootloader.
- To clear QMK/VIA settings, hold the **top-right mechanical key** (GP3, matrix `[1,2]`) while connecting USB or pressing/releasing RESET. Bootmagic erases the emulated EEPROM and enters the bootloader. This is separate from the encoder's hardware BOOTSEL function.

The PCB has 8 MiB of physical W25Q64 flash. This port intentionally uses QMK's conservative first 2 MiB window. The last 8 KiB of that window (`0x101FE000` onward) is reserved for 4 KiB logical wear-leveled EEPROM; the other 6 MiB is unused. Flashing a normal UF2 preserves saved VIA settings. Use Bootmagic to restore presets when necessary.

USB identity `0x4B4E:0x124C` and device version `0.2.0` identify this development build. The VID/PID is not an assigned USB-IF production identity; obtain an authorized identity before commercial distribution. It deliberately differs from Adafruit's VID/PID. VIA must load the supplied matching custom definition; no official VIA listing is claimed.

See the repository firmware guide for pinned build commands, binaries, VIA loading instructions and first-article validation.
