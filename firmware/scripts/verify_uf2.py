# Copyright 2026 KNN-07
# SPDX-License-Identifier: GPL-2.0-or-later
"""Validate RP2040 UF2 structure, address bounds, boot2 CRC, and vector table."""

import argparse
import hashlib
import json
import struct
from pathlib import Path


def boot2_crc(data):
    # RP2040 boot ROM uses non-reflected CRC32, init 0xffffffff, no final XOR.
    crc = 0xFFFFFFFF
    for byte in data:
        crc ^= byte << 24
        for _ in range(8):
            crc = ((crc << 1) ^ (0x04C11DB7 if crc & 0x80000000 else 0)) & 0xFFFFFFFF
    return crc


def verify(path):
    path = Path(path)
    raw = path.read_bytes()
    if not raw or len(raw) % 512:
        raise ValueError('UF2 must contain complete 512-byte blocks')
    blocks = {}
    addresses = {}
    count = len(raw) // 512
    for offset in range(0, len(raw), 512):
        block = raw[offset:offset + 512]
        m0, m1, flags, addr, size, index, total, family = struct.unpack_from('<8I', block)
        if (m0, m1, struct.unpack_from('<I', block, 508)[0]) != (0x0A324655, 0x9E5D5157, 0x0AB16F30):
            raise ValueError('Bad UF2 magic')
        if flags != 0x2000 or family != 0xE48BFF56:
            raise ValueError('Expected RP2040 family and flash blocks only')
        if size != 256 or total != count or index >= count or index in blocks:
            raise ValueError('Invalid UF2 block size/count/index')
        # This port deliberately uses only the first 2 MiB; the last 8 KiB
        # of that region belongs to QMK wear-levelled EEPROM, not firmware.
        if addr % 256 or not (0x10000000 <= addr < 0x101FE000) or addr in addresses:
            raise ValueError('Duplicate, unaligned, or out-of-firmware-range address')
        blocks[index] = addr
        addresses[addr] = block[32:288]
    ordered = sorted(addresses)
    if ordered != list(range(0x10000000, 0x10000000 + count * 256, 256)):
        raise ValueError('Missing or noncontiguous flash payload')
    payload = b''.join(addresses[addr] for addr in ordered)
    stored_crc = struct.unpack_from('<I', payload, 252)[0]
    if stored_crc != boot2_crc(payload[:252]):
        raise ValueError('RP2040 second-stage bootloader CRC mismatch')
    stack, reset = struct.unpack_from('<II', payload, 256)
    if not 0x20000000 < stack <= 0x20042000 or stack % 8:
        raise ValueError('Initial stack is outside RP2040 SRAM or misaligned')
    if not (reset & 1) or not (0x10000100 <= (reset & ~1) < 0x10000000 + len(payload)):
        raise ValueError('Reset vector is not Thumb code inside the firmware')
    return {
        'file': path.name, 'size_bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest(),
        'blocks': count, 'flash_payload_bytes': len(payload), 'family': 'RP2040',
        'flash_start': hex(ordered[0]), 'flash_end_exclusive': hex(ordered[-1] + 256),
        'boot2_crc': 'pass', 'vector_table': 'pass',
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('files', nargs='+', type=Path)
    args = parser.parse_args()
    print(json.dumps([verify(path) for path in args.files], indent=2))
