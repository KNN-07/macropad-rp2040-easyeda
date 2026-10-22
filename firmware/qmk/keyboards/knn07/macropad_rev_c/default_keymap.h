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

/* Modified 2026 KNN-07: four useful presets shared by default and VIA. */
#pragma once

#include QMK_KEYBOARD_H

/* Controls must be highest: a momentary layer cannot override a higher one. */
enum layers { BASE, NAVIGATION, NUMBER, CONTROL };

/* Tap the encoder for mute; hold for controls. KC_MUTE is a basic HID
 * consumer keycode (fits the 8-bit tap field of LT). No timed text macros. */
#define KNOB LT(CONTROL, KC_MUTE)

const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [BASE] = LAYOUT(
                            KNOB,
        KC_F13,   KC_F14,   KC_F15,
        KC_F16,   KC_F17,   KC_F18,
        KC_F19,   KC_F20,   KC_F21,
        KC_F22,   KC_F23,   KC_F24
    ),
    [CONTROL] = LAYOUT(
                            _______,
        KC_MPRV,  KC_MPLY,  KC_MNXT,
        C(KC_X),  C(KC_C),  C(KC_V),
        RM_TOGG,  RM_NEXT,  RM_HUEU,
        TO(BASE), TO(NAVIGATION), TO(NUMBER)
    ),
    [NAVIGATION] = LAYOUT(
                            KNOB,
        KC_HOME,  KC_UP,    KC_END,
        KC_LEFT,  KC_DOWN,  KC_RGHT,
        KC_PGUP,  KC_PGDN,  KC_DEL,
        KC_ESC,   KC_ENT,   KC_BSPC
    ),
    [NUMBER] = LAYOUT(
                            KNOB,
        KC_7,     KC_8,     KC_9,
        KC_4,     KC_5,     KC_6,
        KC_1,     KC_2,     KC_3,
        KC_0,     KC_DOT,   KC_ENT
    ),
};

#ifdef ENCODER_MAP_ENABLE
const uint16_t PROGMEM encoder_map[][NUM_ENCODERS][NUM_DIRECTIONS] = {
    [BASE]       = { ENCODER_CCW_CW(KC_VOLD, KC_VOLU) },
    [CONTROL]    = { ENCODER_CCW_CW(RM_VALD, RM_VALU) },
    [NAVIGATION] = { ENCODER_CCW_CW(KC_PGUP, KC_PGDN) },
    [NUMBER]     = { ENCODER_CCW_CW(KC_LEFT, KC_RGHT) },
};
#endif
