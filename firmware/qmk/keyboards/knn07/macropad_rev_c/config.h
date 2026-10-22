/* Copyright 2022 Jose Pablo Ramirez <jp.ramangulo@gmail.com>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#pragma once

/* The same 128x64 SPI SH1106 interface as the Adafruit MacroPad. */
#define OLED_DISPLAY_128X64
#define OLED_IC OLED_IC_SH1106
#define OLED_DC_PIN GP24
#define OLED_CS_PIN GP22
#define OLED_RST_PIN GP23
#define OLED_COLUMN_OFFSET 2
#define OLED_SPI_DIVISOR 4
#define OLED_TIMEOUT 60000
#define OLED_UPDATE_INTERVAL 100

#define SPI_DRIVER SPID1
#define SPI_SCK_PIN GP26
#define SPI_MOSI_PIN GP27
/* GP28 is named MISO, but the write-only OLED has no MISO connection. */
#define SPI_MISO_PIN GP28

/* Double-tap the side reset button within 500 ms to enter RPI-RP2. */
#define RP2040_BOOTLOADER_DOUBLE_TAP_RESET
#define RP2040_BOOTLOADER_DOUBLE_TAP_RESET_LED GP13
#define RP2040_BOOTLOADER_DOUBLE_TAP_RESET_TIMEOUT 500U

/* Explicitly retain QMK's conservative 2 MiB flash window on the 8 MiB U1.
 * Reserve the final 8 KiB in that window for 4 KiB logical EEPROM. */
#define WEAR_LEVELING_RP2040_FLASH_SIZE (2 * 1024 * 1024)
#define WEAR_LEVELING_BACKING_SIZE 8192
#define WEAR_LEVELING_LOGICAL_SIZE 4096

/* QMK defaults DYNAMIC_KEYMAP_LAYER_COUNT to 4, matching these presets. */
