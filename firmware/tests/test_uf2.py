# Copyright 2026 KNN-07
# SPDX-License-Identifier: GPL-2.0-or-later
"""Exercise the release validator with valid and deliberately damaged images."""
import importlib.util
import struct
import tempfile
import unittest
from pathlib import Path

SPEC = importlib.util.spec_from_file_location('verify_uf2', Path(__file__).parents[1] / 'scripts' / 'verify_uf2.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class Uf2Tests(unittest.TestCase):
    def image(self):
        payload = bytearray(512)
        struct.pack_into('<I', payload, 252, MODULE.boot2_crc(payload[:252]))
        struct.pack_into('<II', payload, 256, 0x20042000, 0x10000121)
        image = bytearray()
        for index in range(2):
            block = bytearray(512)
            struct.pack_into('<8I', block, 0, 0x0A324655, 0x9E5D5157, 0x2000,
                             0x10000000 + 256 * index, 256, index, 2, 0xE48BFF56)
            block[32:288] = payload[index * 256:(index + 1) * 256]
            struct.pack_into('<I', block, 508, 0x0AB16F30)
            image.extend(block)
        return image

    def verify(self, image):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'test.uf2'
            path.write_bytes(image)
            return MODULE.verify(path)

    def test_complete_image(self):
        result = self.verify(self.image())
        self.assertEqual(result['blocks'], 2)
        self.assertEqual(result['flash_payload_bytes'], 512)

    def test_corruption_is_rejected(self):
        mutations = {
            'magic': (0, 0), 'family': (28, 0), 'missing_index': (20, 2),
            'count': (24, 3), 'eeprom_overlap': (12, 0x101FE000),
            'duplicate_address': (512 + 12, 0x10000000),
            'boot2_crc': (32 + 252, 0), 'stack': (512 + 32, 0x30000000),
            'non_thumb_vector': (512 + 36, 0x10000120),
        }
        for name, (offset, value) in mutations.items():
            with self.subTest(name=name):
                image = self.image()
                struct.pack_into('<I', image, offset, value)
                with self.assertRaises(ValueError):
                    self.verify(image)

    def test_truncated_image(self):
        with self.assertRaises(ValueError):
            self.verify(self.image()[:-1])


if __name__ == '__main__':
    unittest.main()
