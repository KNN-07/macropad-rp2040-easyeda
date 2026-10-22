# Rev C firmware pin map

Cross-checked against the released native EasyEDA archive, the upstream EAGLE netlist and QMK's Adafruit MacroPad configuration. Direct keys are active low with input pull-ups; there is no scanned electrical row/column matrix. The 5x3 QMK/VIA matrix is only a software arrangement, with two empty positions in its first row.

| Function | GPIO | QMK/VIA position |
| --- | --- | --- |
| Encoder push / hardware BOOTSEL | 0 | 0,2 |
| Keys, front row 1 left to right | 1, 2, 3 | 1,0 through 1,2 |
| Keys, front row 2 left to right | 4, 5, 6 | 2,0 through 2,2 |
| Keys, front row 3 left to right | 7, 8, 9 | 3,0 through 3,2 |
| Keys, front row 4 left to right | 10, 11, 12 | 4,0 through 4,2 |
| Red status LED | 13 | Bootloader double-tap indication |
| Speaker amplifier enable | 14 | Driven low |
| Speaker PWM | 16 | Driven low |
| Encoder physical A / B | 17 / 18 | QMK pin_a=18, pin_b=17, resolution=4 |
| RGB data | 19 | LED1 through LED12, row-major from front |
| STEMMA QT SDA / SCL | 20 / 21 | Unused by these builds |
| OLED chip select | 22 | SPI1, active low |
| OLED reset | 23 | Active low |
| OLED data/command | 24 | SH1106 |
| OLED clock / data | 26 / 27 | SPI1 SCK / MOSI |
| SPI MISO | 28 | Reserved by SPI configuration; OLED is write-only |

The OLED is 128x64 SH1106 with a two-column offset. Its stale EAGLE symbol text saying 128x32 is not the fitted device geometry. Encoder selection is Bourns PEC11R-4215F-S0024, 24 detents and 24 pulses/revolution; QMK uses four quadrature transitions per event. Confirm direction and one step per detent on a physical board.

The GP0 encoder switch also pulls QSPI chip-select through a diode/resistor while booting, invoking the RP2040 ROM USB bootloader. The side button independently pulls RUN low. Flash is W25Q64, 8 MiB; QSPI pins are dedicated and are not the OLED SPI bus.

The RGB chain has a 5 V level shifter and no GPIO power gate. GPIO15, GPIO25 and GPIO29 are unused. See the [upstream QMK port](https://github.com/qmk/qmk_firmware/tree/180f394b489c238cb231c2bf8b080262155e03c0/keyboards/adafruit/macropad), [Adafruit pinouts](https://learn.adafruit.com/adafruit-macropad-rp2040/pinouts), and [encoder drawing](https://www.bourns.com/data/global/pdfs/PEC11R.pdf).
