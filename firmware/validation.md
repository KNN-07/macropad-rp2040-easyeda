# Firmware validation

Release **0.2.0** targets MACRO12 Rev C. [GitHub Actions run 39793175666](https://github.com/KNN-07/macropad-rp2040-easyeda/actions/runs/39793175666) completed successfully on Ubuntu 24.04 using source commit `e17ea059e2b1d2ec2c0a0feb54a99a97d9cc3c46`, QMK `180f394b489c238cb231c2bf8b080262155e03c0`, QMK CLI 1.2.0 and ARM GCC 13.2.1. Subsequent release-documentation changes do not alter the compiled source.

| Check | Result |
| --- | --- |
| CAD-backed pin regression | All 311 connected native pads agree with the schematic; front key order, RGB chain, encoder/BOOTSEL and OLED pins pass |
| Python regression suite | 14 tests passed, no skips; malformed UF2 inputs rejected |
| Official VIA reader | `@the-via/reader` 1.14.4 schema and conversion passed: 13 switches, encoder 0, four layers and RGB Matrix |
| QMK strict lint | Keyboard and default keymap pass; upstream lint excludes VIA by contribution policy, so the standalone VIA keymap is separately compiled and checked |
| Standard firmware | Compiled and linked; 114,688-byte UF2, 57,344-byte padded flash payload |
| VIA firmware | Compiled and linked; 123,904-byte UF2, 61,952-byte padded flash payload |
| UF2 validation | RP2040 family, every block/address, contiguous payload, flash/EEPROM separation, boot2 CRC and SRAM/Thumb vectors pass for both builds |
| Artifact download | Every file matched the CI-generated SHA-256 manifest; UF2 checks repeated on the downloaded bytes |
| Source distribution | Complete project/QMK/required submodule source archive, with upstream licenses, accompanies the binaries |

The [build manifest](releases/v0.2.0/build-manifest.json), [standard build log](releases/v0.2.0/build-default.txt), [VIA build log](releases/v0.2.0/build-via.txt), [lint result](releases/v0.2.0/qmk-lint.txt) and [Python package versions](releases/v0.2.0/python-packages.txt) preserve the evidence. QMK source-level review also confirmed layer-selection release behavior, encoder EEPROM bounds, amplifier shutdown, RGB cap and OLED timeout.

| UF2 | SHA-256 |
| --- | --- |
| `MACRO12-RevC-default.uf2` | `5e701cd393b3eaf05809c8601cfcc8b4047f7abdd510c233cbbee6d8293c8758` |
| `MACRO12-RevC-via.uf2` | `98d797bf53e9856893496582379b6725530c84a69adeee6a1bf6af9ebc2192b2` |

Physical validation is pending: no assembled Rev C board is available in this session. See [first-article.md](first-article.md). Do not interpret successful compilation or a valid VIA definition as a tested USB/peripheral connection.
