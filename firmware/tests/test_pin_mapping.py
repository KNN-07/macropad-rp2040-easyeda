# SPDX-License-Identifier: GPL-2.0-or-later
"""Check the firmware against the shipped CAD, without network or EDA tools.

The user face is the mirrored side of the PCB coordinate view, with USB at
the top. Sorting PCB X in ascending order would silently reverse every row;
these tests derive the front layout from the actual native placements.
"""

from collections import defaultdict
import json
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET
from zipfile import ZipFile


REPO = Path(__file__).resolve().parents[2]
BOARD = REPO / "firmware/qmk/keyboards/knn07/macropad_rev_c"
UPSTREAM = REPO / "hardware/upstream"


def normalize_net(name):
    # EasyEDA encodes the EAGLE overbar notation differently.
    return "~RESET~" if name == "!RESET" else name


def read_defines(path):
    source = path.read_text(encoding="utf-8")
    source = re.sub(r"/\*.*?\*/", "", source, flags=re.S)
    source = re.sub(r"//[^\n]*", "", source)
    return dict(re.findall(r"^\s*#define[ \t]+(\w+)([^\n]*)", source, re.M))


class PinMappingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.keyboard = json.loads((BOARD / "keyboard.json").read_text(encoding="utf-8"))
        cls.defines = {key: value.strip() for key, value in read_defines(BOARD / "config.h").items()}
        cls.schematic = ET.parse(UPSTREAM / "Adafruit MacroPad 2040 rev D.sch").getroot()
        cls.source_board = ET.parse(UPSTREAM / "Adafruit MacroPad 2040 rev D.brd").getroot()
        cls.elements = {node.get("name"): node for node in cls.source_board.findall(".//elements/element")}

        with ZipFile(REPO / "hardware/easyeda/MACRO12-RevC.epro") as archive:
            pcb_names = [name for name in archive.namelist() if name.endswith(".epcb")]
            if len(pcb_names) != 1:
                raise AssertionError(f"Expected exactly one native PCB, found {pcb_names}")
            records = [json.loads(line) for line in archive.read(pcb_names[0]).decode("utf-8").splitlines()]
        cls.attributes = defaultdict(dict)
        for record in records:
            if record[0] == "ATTR":
                cls.attributes[record[3]][record[7]] = record[8]
        cls.components = {
            cls.attributes[record[1]]["Designator"]: record
            for record in records if record[0] == "COMPONENT"
        }
        references = {record[1]: ref for ref, record in cls.components.items()}
        cls.native_nets = {
            (references[record[1]], record[2]): record[3]
            for record in records if record[0] == "PAD_NET" and record[1] in references
        }

        # Resolve symbolic GPIO names through the EAGLE device's actual pin-to-
        # package-pad mapping, then compare those pads to the native archive.
        parts = {node.get("name"): node for node in cls.schematic.findall(".//parts/part")}
        libraries = {node.get("name"): node for node in cls.schematic.findall(".//libraries/library")}
        cls.devices = {}
        cls.device_sets = {}
        for ref, part in parts.items():
            device_set = next(node for node in libraries[part.get("library")].findall("./devicesets/deviceset")
                              if node.get("name") == part.get("deviceset"))
            cls.device_sets[ref] = device_set
            cls.devices[ref] = next(node for node in device_set.findall("./devices/device")
                                    if node.get("name") == part.get("device"))
        cls.schematic_nets = {}
        cls.symbol_nets = {}
        for net in cls.schematic.findall(".//sheets/sheet/nets/net"):
            name = normalize_net(net.get("name"))
            for pin in net.findall("./segment/pinref"):
                ref = pin.get("part")
                cls.symbol_nets[(ref, pin.get("pin"))] = name
                if ref not in cls.components:
                    continue  # Supply symbols have no physical component.
                for connection in cls.devices[ref].findall("./connects/connect"):
                    if connection.get("gate") == pin.get("gate") and connection.get("pin") == pin.get("pin"):
                        for pad in connection.get("pad").split():
                            cls.schematic_nets[(ref, pad)] = name
        cls.gpio_by_net = {}
        for (ref, pin), net in cls.symbol_nets.items():
            match = re.fullmatch(r"GPIO(\d+)(?:/AD\d+)?", pin)
            if ref == "IC3" and match:
                cls.gpio_by_net[net] = "GP" + match.group(1)

        cls.sockets = [ref for ref, element in cls.elements.items() if element.get("package") == "KAILH_SOCKET"]
        # Native and EAGLE Y increases toward USB. Front X is reversed because
        # the user faces the bottom side: encoder right, display left.
        cls.front_keys = sorted(cls.sockets, key=lambda ref: (-cls.components[ref][5], -cls.components[ref][4]))
        cls.front_matrix = {ref: (1 + index // 3, index % 3) for index, ref in enumerate(cls.front_keys)}

    def net(self, ref, pad):
        return self.native_nets[(ref, pad)]

    def gpio(self, ref, pad):
        return self.gpio_by_net[self.net(ref, pad)]

    def test_native_connections_match_actual_schematic_package_pads(self):
        actual = {key: net for key, net in self.native_nets.items() if net}
        self.assertEqual(len(self.schematic_nets), 311, "Re-audit a changed schematic before changing this baseline")
        self.assertEqual(actual, self.schematic_nets)

    def test_front_key_order_is_not_the_mirrored_electronics_view(self):
        self.assertEqual(len(self.sockets), 12)
        self.assertEqual(self.front_keys, ["U$40", "U$13", "U$12", "U$43", "U$42", "U$41",
                                          "U$6", "U$5", "U$4", "U$1", "U$2", "U$3"])
        xs = sorted({self.components[ref][4] for ref in self.sockets})
        ys = sorted({self.components[ref][5] for ref in self.sockets})
        self.assertEqual(xs, [425, 1175, 1925])
        self.assertEqual(ys, [425, 1175, 1925, 2675])  # 750 mil = 19.05 mm pitch.
        self.assertGreater(self.components["X1"][5], max(ys))
        self.assertLess(self.components["SW1"][4], self.components["X2"][4])
        for ref in self.sockets:
            self.assertEqual(self.components[ref][3], 2, ref)
            self.assertTrue(self.elements[ref].get("rot").startswith("M"), ref)
            self.assertEqual(self.net(ref, "2"), "GND", ref)
            source = self.elements[ref]
            self.assertAlmostEqual(self.components[ref][4] * 0.0254, float(source.get("x")), places=4)
            self.assertAlmostEqual(self.components[ref][5] * 0.0254, float(source.get("y")), places=4)

        expected = [[None, None, self.gpio("SW1", "P$1")]]
        for offset in range(0, 12, 3):
            expected.append([self.gpio(ref, "1") for ref in self.front_keys[offset:offset + 3]])
        self.assertEqual(self.keyboard["matrix_pins"]["direct"], expected)
        layout = self.keyboard["layouts"]["LAYOUT"]["layout"]
        self.assertEqual(len(layout), 13)
        expected_layout = {(0, 2): (2, 0)}
        expected_layout.update({matrix: (matrix[1], matrix[0]) for matrix in self.front_matrix.values()})
        self.assertEqual({tuple(key["matrix"]): (key["x"], key["y"]) for key in layout}, expected_layout)

    def test_encoder_and_hardware_boot_button(self):
        self.assertEqual(self.attributes[self.components["SW1"][1]]["Name"], "PEC11R-4215F-S0024")
        encoder = self.keyboard["encoder"]["rotary"]
        # QMK's existing Adafruit convention reverses physical A/B to make
        # clockwise positive from the user face. This part is 24 PPR/24 detents.
        self.assertEqual(encoder, [{"pin_a": self.gpio("SW1", "P$B"),
                                    "pin_b": self.gpio("SW1", "P$A"), "resolution": 4}])
        self.assertEqual(self.net("SW1", "P$C"), "GND")
        self.assertEqual(self.net("SW1", "P$2"), "GND")
        self.assertEqual(self.gpio("SW1", "P$1"), "GP0")
        self.assertEqual(self.net("D3", "C"), self.net("SW1", "P$1"))
        self.assertEqual(self.net("D3", "A"), self.net("R11", "2"))
        self.assertEqual(self.net("R11", "1"), self.net("U1", "1"))
        self.assertEqual(self.net("U1", "1"), self.symbol_nets[("IC3", "!QSPI_CS")])
        self.assertEqual(self.keyboard["bootloader"], "rp2040")
        self.assertIn("RP2040_BOOTLOADER_DOUBLE_TAP_RESET", self.defines)
        self.assertEqual(self.defines["RP2040_BOOTLOADER_DOUBLE_TAP_RESET_LED"], self.gpio("R1", "1"))

    def test_rgb_serial_chain_and_key_association(self):
        self.assertEqual(self.keyboard["ws2812"]["pin"], self.gpio("IC1", "2"))
        self.assertEqual(self.net("IC1", "1"), "GND")  # Always-enabled level shifter.
        self.assertEqual(self.net("IC1", "5"), "5.0V")
        leds = [ref for ref in self.components if re.fullmatch(r"LED\d+", ref)]
        self.assertEqual(len(leds), 12)
        by_input = {self.net(ref, "4-DIN"): ref for ref in leds}
        chain = []
        signal = self.net("IC1", "4")
        while signal:
            self.assertIn(signal, by_input)
            ref = by_input[signal]
            self.assertNotIn(ref, chain, "RGB chain has a cycle")
            chain.append(ref)
            self.assertEqual(self.net(ref, "1-VDD"), "5.0V")
            self.assertEqual(self.net(ref, "3-GND"), "GND")
            signal = self.net(ref, "2-DOUT")
        self.assertEqual(set(chain), set(leds))
        layout = self.keyboard["rgb_matrix"]["layout"]
        self.assertEqual(len(layout), len(chain))
        led_xs = sorted({entry["x"] for entry in layout})
        led_ys = sorted({entry["y"] for entry in layout})
        self.assertEqual((len(led_xs), len(led_ys)), (3, 4))
        paired = []
        for led, entry in zip(chain, layout):
            cx, cy = self.components[led][4:6]
            distance = lambda ref: (self.components[ref][4] - cx) ** 2 + (self.components[ref][5] - cy) ** 2
            socket = min(self.sockets, key=distance)
            self.assertLess(distance(socket), (6 / 0.0254) ** 2, led)
            paired.append(socket)
            row, col = self.front_matrix[socket]
            self.assertEqual(entry["matrix"], [row, col], led)
            self.assertEqual((led_xs.index(entry["x"]), led_ys.index(entry["y"])), (col, row - 1), led)
        self.assertEqual(len(set(paired)), 12)

    def test_oled_controller_and_spi_wiring(self):
        symbol = self.device_sets["X2"].find("./gates/gate").get("symbol")
        self.assertEqual(symbol, "OLED_128X64_SH1106SPI")
        self.assertIn("OLED_DISPLAY_128X64", self.defines)
        self.assertEqual(self.defines["OLED_IC"], "OLED_IC_SH1106")
        self.assertEqual(self.defines["OLED_COLUMN_OFFSET"], "2")
        for define, pad in {"OLED_CS_PIN": "8", "OLED_RST_PIN": "9", "OLED_DC_PIN": "10",
                            "SPI_SCK_PIN": "11", "SPI_MOSI_PIN": "12"}.items():
            self.assertEqual(self.defines[define], self.gpio("X2", pad), define)
        self.assertEqual(self.defines["SPI_DRIVER"], "SPID1")
        self.assertEqual(self.defines["SPI_MISO_PIN"], self.gpio_by_net["MISO"])
        self.assertEqual([key for key, net in self.native_nets.items() if net == "MISO"], [("IC3", "40")])


if __name__ == "__main__":
    unittest.main()
