"""Cross-check the sideload definition against the actual QMK hardware model.

Run with: python -m unittest discover -s firmware/tests -v
No third-party packages or physical keyboard are required.
"""

import json
from pathlib import Path
import re
import unittest


FIRMWARE = Path(__file__).resolve().parents[1]
DEFINITION = FIRMWARE / "via" / "macro12-rev-c.json"
QMK_BOARD = FIRMWARE / "qmk" / "keyboards" / "knn07" / "macropad_rev_c"
EXPECTED_MATRIX = [(0, 2)] + [(row, col) for row in range(1, 5) for col in range(3)]


def read_layout(definition):
    """Read the unrotated one-unit KLE subset used by this fixed keypad.

    Reject advanced/hidden KLE geometry instead of silently missing a key.
    Encoder metadata uses the centered legend at KLE label index nine.
    """
    keys = []
    for y, row in enumerate(definition["layouts"]["keymap"]):
        x = 0
        for entry in row:
            if isinstance(entry, dict):
                if set(entry) != {"x"}:
                    raise ValueError(f"Unexpected KLE geometry/style: {entry!r}")
                x += entry["x"]
                continue
            if not isinstance(entry, str):
                raise ValueError(f"Expected a key legend, got {entry!r}")
            labels = entry.split("\n")
            if not re.fullmatch(r"\d+,\d+", labels[0]):
                raise ValueError(f"Missing switch coordinate: {entry!r}")
            keys.append({
                "matrix": tuple(map(int, labels[0].split(","))),
                "x": x,
                "y": y,
                "labels": labels,
            })
            x += 1
    return keys


class ViaDefinitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.definition = json.loads(DEFINITION.read_text(encoding="utf-8"))
        cls.keys = read_layout(cls.definition)
        keyboard_path = QMK_BOARD / "keyboard.json"
        cls.keyboard = (
            json.loads(keyboard_path.read_text(encoding="utf-8"))
            if keyboard_path.exists() else None
        )

    def require_keyboard(self):
        if self.keyboard is None:
            self.skipTest("QMK keyboard.json is not present")
        return self.keyboard

    def test_identity_and_v3_feature_contract(self):
        self.assertEqual(self.definition["name"], "MACRO12 Rev C")
        self.assertEqual(int(self.definition["vendorId"], 16), 0x4B4E)
        self.assertEqual(int(self.definition["productId"], 16), 0x124C)
        self.assertEqual(self.definition["matrix"], {"rows": 5, "cols": 3})
        self.assertEqual(self.definition["menus"], ["qmk_rgb_matrix"])
        self.assertEqual(self.definition["keycodes"], ["qmk_rgb_matrix_keycodes"])
        self.assertNotIn("lighting", self.definition)  # Obsolete V2 property.
        self.assertNotIn("customKeycodes", self.definition)

    def test_every_physical_switch_once_without_phantom_holes(self):
        actual = [key["matrix"] for key in self.keys]
        self.assertEqual(actual, EXPECTED_MATRIX)
        self.assertEqual(len(set(actual)), 13)
        self.assertNotIn((0, 0), actual)
        self.assertNotIn((0, 1), actual)
        self.assertNotIn("labels", self.definition["layouts"])  # No hidden options.
        for key in self.keys:
            self.assertEqual((key["y"], key["x"]), key["matrix"])

    def test_encoder_has_one_push_switch_and_centered_e0(self):
        encoder_keys = [key for key in self.keys if len(key["labels"]) > 1]
        self.assertEqual(len(encoder_keys), 1)
        encoder = encoder_keys[0]
        self.assertEqual(encoder["matrix"], (0, 2))
        self.assertEqual(encoder["labels"], ["0,2"] + [""] * 8 + ["e0"])

    def test_qmk_usb_and_active_direct_pins_match(self):
        keyboard = self.require_keyboard()
        self.assertEqual(int(keyboard["usb"]["vid"], 16), int(self.definition["vendorId"], 16))
        self.assertEqual(int(keyboard["usb"]["pid"], 16), int(self.definition["productId"], 16))
        direct = keyboard["matrix_pins"]["direct"]
        self.assertEqual(len(direct), self.definition["matrix"]["rows"])
        self.assertTrue(all(len(row) == self.definition["matrix"]["cols"] for row in direct))
        active = {(r, c): pin for r, row in enumerate(direct)
                  for c, pin in enumerate(row) if pin is not None}
        expected = {(0, 2): "GP0"}
        expected.update({(r, c): f"GP{(r - 1) * 3 + c + 1}"
                         for r in range(1, 5) for c in range(3)})
        self.assertEqual(active, expected)
        self.assertEqual(set(active), {key["matrix"] for key in self.keys})

    def test_qmk_physical_layout_matches_via(self):
        keyboard = self.require_keyboard()
        expected = {key["matrix"]: (key["x"], key["y"]) for key in self.keys}
        full_layouts = [layout["layout"] for layout in keyboard["layouts"].values()
                        if len(layout["layout"]) == len(expected)]
        self.assertTrue(full_layouts, "No QMK layout exposes all 13 switches")
        self.assertTrue(any(
            {tuple(key["matrix"]): (key["x"], key["y"]) for key in layout} == expected
            for layout in full_layouts
        ), "VIA and QMK disagree on physical positions")

    def test_qmk_features_support_the_exposed_controls(self):
        keyboard = self.require_keyboard()
        self.assertTrue(keyboard["features"]["rgb_matrix"])
        self.assertFalse(keyboard["features"].get("audio", False))
        self.assertEqual(len(keyboard["encoder"]["rotary"]), 1)
        layer_counts = [keyboard.get("dynamic_keymap", {}).get("layer_count", 4)]
        for config_path in (QMK_BOARD / "config.h", QMK_BOARD / "keymaps" / "via" / "config.h"):
            if config_path.exists():
                layer_counts.extend(int(value) for value in re.findall(
                    r"(?m)^\s*#define\s+DYNAMIC_KEYMAP_LAYER_COUNT\s+(\d+)\s*$",
                    config_path.read_text(encoding="utf-8"),
                ))
        self.assertTrue(all(count == 4 for count in layer_counts))
        via_rules = (QMK_BOARD / "keymaps" / "via" / "rules.mk").read_text(encoding="utf-8")
        for option in ("VIA_ENABLE", "ENCODER_MAP_ENABLE"):
            self.assertRegex(via_rules, rf"(?m)^\s*{option}\s*=\s*yes\s*(?:#.*)?$")


if __name__ == "__main__":
    unittest.main()
