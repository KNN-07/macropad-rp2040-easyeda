# Copyright 2026 KNN-07
# SPDX-License-Identifier: GPL-2.0-or-later
"""Build the pinned QMK port. Requires Git, QMK CLI and the ARM toolchain."""

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

from verify_uf2 import verify

FIRMWARE = Path(__file__).resolve().parents[1]
REPO = FIRMWARE.parent
LOCK = json.loads((FIRMWARE / 'toolchain.json').read_text())


def run(args, cwd=None, log=None):
    print('+', ' '.join(map(str, args)), flush=True)
    result = subprocess.run(args, cwd=cwd, text=True, encoding='utf-8', errors='replace',
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    clean = re.sub(r'\x1b\[[0-9;]*[A-Za-z]', '', result.stdout)
    print(clean, end='', flush=True)
    if log:
        Path(log).write_text(clean, encoding='utf-8')
    if result.returncode:
        raise subprocess.CalledProcessError(result.returncode, args)
    return clean.strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--qmk-dir', required=True, type=Path)
    parser.add_argument('--output-dir', default=REPO / 'artifacts', type=Path)
    args = parser.parse_args()
    qmk = args.qmk_dir.resolve()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if not qmk.exists():
        qmk.mkdir(parents=True)
        run(['git', 'init', str(qmk)])
        run(['git', 'remote', 'add', 'origin', LOCK['qmk_repository']], qmk)
        run(['git', 'fetch', '--depth', '1', 'origin', LOCK['qmk_commit']], qmk)
        run(['git', 'checkout', '--detach', 'FETCH_HEAD'], qmk)
    if run(['git', 'rev-parse', 'HEAD'], qmk) != LOCK['qmk_commit']:
        raise SystemExit('QMK checkout does not match firmware/toolchain.json; use a fresh directory.')
    if run(['git', 'status', '--porcelain', '--untracked-files=no'], qmk):
        raise SystemExit('Refusing to build from modified tracked QMK source.')
    run(['git', 'submodule', 'update', '--init', '--depth', '1', '--recursive', *LOCK['submodules']], qmk)
    run([sys.executable, '-m', 'pip', 'install', '-r', str(qmk / 'requirements.txt')])
    cli_version = run(['qmk', '--version'], qmk)
    if cli_version.split()[-1] != LOCK['qmk_cli_version']:
        raise SystemExit('Install qmk==' + LOCK['qmk_cli_version'])
    source = FIRMWARE / 'qmk' / 'keyboards' / LOCK['keyboard']
    target = qmk / 'keyboards' / LOCK['keyboard']
    if target.exists():
        extras = {p.relative_to(target) for p in target.rglob('*') if p.is_file()} - {
            p.relative_to(source) for p in source.rglob('*') if p.is_file()}
        if extras:
            raise SystemExit('Unexpected files in existing port directory: ' + str(extras))
    shutil.copytree(source, target, dirs_exist_ok=True)
    os.environ['QMK_HOME'] = str(qmk)
    # Upstream lint rejects the name "via" for contribution-policy reasons;
    # our self-contained VIA keymap is compiled and checked separately.
    run(['qmk', 'lint', '-kb', LOCK['keyboard'], '-km', 'default', '--strict'], qmk, output / 'qmk-lint.log')
    results = []
    for keymap in LOCK['keymaps']:
        run(['make', f"{LOCK['keyboard']}:{keymap}", '-j2'], qmk, output / f'build-{keymap}.log')
        stem = LOCK['keyboard'].replace('/', '_') + '_' + keymap
        uf2 = output / f'MACRO12-RevC-{keymap}.uf2'
        shutil.copy2(qmk / (stem + '.uf2'), uf2)
        results.append(verify(uf2))
        for extension in ('elf', 'bin', 'map'):
            artifact = qmk / '.build' / (stem + '.' + extension)
            if artifact.exists():
                shutil.copy2(artifact, output / f'MACRO12-RevC-{keymap}.{extension}')
    manifest = {
        'firmware_version': LOCK['firmware_version'],
        'source_commit': run(['git', 'rev-parse', 'HEAD'], REPO),
        'qmk_commit': LOCK['qmk_commit'], 'qmk_cli': cli_version,
        'arm_gcc': run(['arm-none-eabi-gcc', '--version']).splitlines()[0],
        'qmk_submodules': run(['git', 'submodule', 'status', *LOCK['submodules']], qmk).splitlines(),
        'validation': 'compiled and statically checked; physical hardware untested',
        'firmware': results,
    }
    (output / 'build-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    run([sys.executable, '-m', 'pip', 'freeze'], log=output / 'python-packages.txt')
    (output / 'SHA256SUMS').write_text(''.join(
        f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n'
        for p in sorted(output.iterdir()) if p.is_file() and p.name != 'SHA256SUMS'), encoding='utf-8')


if __name__ == '__main__':
    main()
