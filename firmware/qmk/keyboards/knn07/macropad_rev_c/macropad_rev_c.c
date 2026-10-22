// Copyright 2026 KNN-07
// SPDX-License-Identifier: GPL-2.0-or-later

#include QMK_KEYBOARD_H

void keyboard_pre_init_kb(void) {
    /* U3 PAM8302 shutdown is active low. Keep both amplifier control and input at
     * defined low levels: these builds deliberately do not enable audio. */
    gpio_write_pin_low(GP14);
    gpio_set_pin_output(GP14);
    gpio_write_pin_low(GP16);
    gpio_set_pin_output(GP16);
    keyboard_pre_init_user();
}

#ifdef OLED_ENABLE
bool oled_task_kb(void) {
    if (!oled_task_user()) {
        return false;
    }

    /* Generic layer numbers stay truthful when VIA changes the keymap. */
    oled_set_cursor(0, 0);
    oled_write_ln_P(PSTR("MACRO12 / REV C"), false);
#ifdef VIA_ENABLE
    oled_write_ln_P(PSTR("QMK + VIA"), false);
#else
    oled_write_ln_P(PSTR("QMK default"), false);
#endif
    oled_write_P(PSTR("Layer: "), false);
    oled_write_ln(get_u8_str(get_highest_layer(layer_state | default_layer_state), ' '), false);
    oled_write_P(PSTR("RGB: "), false);
    oled_write_P(rgb_matrix_is_enabled() ? PSTR("ON  ") : PSTR("OFF "), false);
    oled_write_P(PSTR("Level: "), false);
    oled_write_ln(get_u8_str(rgb_matrix_get_val(), ' '), false);

    led_t leds = host_keyboard_led_state();
    oled_write_P(PSTR("Caps:"), false);
    oled_write_P(leds.caps_lock ? PSTR("1 ") : PSTR("0 "), false);
    oled_write_P(PSTR("Num:"), false);
    oled_write_P(leds.num_lock ? PSTR("1 ") : PSTR("0 "), false);
    oled_write_P(PSTR("Scr:"), false);
    oled_write_ln_P(leds.scroll_lock ? PSTR("1") : PSTR("0"), false);
    oled_write_ln_P(PSTR("12 keys + encoder"), false);
    oled_write_ln_P(PSTR("Audio: disabled"), false);
    oled_write_ln_P(PSTR("Firmware 0.2.0"), false);
    return false;
}
#endif
