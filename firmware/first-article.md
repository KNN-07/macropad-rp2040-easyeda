# First-article firmware validation

These checks require the assembled Rev C hardware and have **not** been performed. Follow [assembly.md](../docs/assembly.md), including OLED insulation and mounting clearances, before applying power.

1. Check supply shorts, polarity and component orientation unpowered. On controlled initial power, confirm the expected supply rails and current before connecting a host USB data port.
2. Hold the encoder during reset/power-up and verify `RPI-RP2`. Flash the VIA UF2. Check USB enumeration as MACRO12 Rev C in both USB-C cable orientations.
3. In a key-event viewer, confirm F13 through F24 in the documented front-side row order, including simultaneous keys. Check that each press/release produces one event without sticking or excessive bounce.
4. Verify the encoder produces one volume step per detent in the expected direction. Tap for mute; hold and press each control-layer key. Select navigation and numpad modes, and verify the hold-control route back to layer 0 from both.
5. Check all twelve LEDs, color order and effects. Measure worst-case current at the brightness cap with OLED active and keys held; confirm it is within the host/power budget. Check lights turn off and keys release during USB suspend and recover after resume.
6. Confirm the SH1106 display is readable, upright, correctly aligned, shows changing layer numbers and lock state, and sleeps/wakes with activity. Verify speaker silence and the amplifier-enable low level.
7. Import the supplied definition at usevia.app. Remap a key, each encoder direction and a harmless text macro. Power-cycle and confirm each setting persists. Test remaps on all four layers, RGB controls and the key tester.
8. Export the VIA layout. Verify double-tap reset and hardware encoder-plus-reset recovery. Hold the top-right key during USB connection to clear EEPROM and enter bootloader; reconnect and confirm factory defaults return.

Record board revision, firmware SHA-256, part substitutions, host OS, cable, measured rail/current values and any failures before considering a larger assembly run. Compiled firmware and static checks do not establish USB compliance, electrical safety, switch debounce performance, OLED fit or power integrity.
