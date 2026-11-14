#!/usr/bin/env python3
"""Capture source-identified real app frames for A34; no image fabrication."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

from PIL import Image


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


parser = argparse.ArgumentParser()
parser.add_argument('phase', choices=('before', 'after'))
parser.add_argument('exe', type=Path)
parser.add_argument('expected_sha256')
parser.add_argument('output', type=Path)
args = parser.parse_args()
repo = Path(__file__).resolve().parents[4]
report = Path(__file__).resolve().parent
assert digest(args.exe) == args.expected_sha256
out = args.output / args.phase
out.mkdir(parents=True, exist_ok=False)
state = repo / 'examples/demos/standalone-interface-preview-v1/inputs/controls.b3controls'
script = report / 'a34-focus-dsharp.b3uireplay'
events = []
for i in range(16):
    at = 100 + 20 * i
    events += [f'{at} key_down Tab none 0', f'{at + 1} key_up Tab none']
script_text = 'B3UIREPLAY1\nduration_ms 900\n' + '\n'.join(events) + '\n'
if script.exists():
    assert script.read_text() == script_text
else:
    script.write_text(script_text)
environment = {'PATH': os.defpath, 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8',
               'SDL_VIDEODRIVER': 'dummy', 'SDL_AUDIODRIVER': 'dummy',
               'SDL_RENDER_DRIVER': 'software'}
record = {'phase': args.phase, 'binary': str(args.exe), 'binary_sha256': digest(args.exe),
          'environment': environment, 'inputs_sha256': {str(state): digest(state), str(script): digest(script)},
          'qualification': 'Actual app windows captured with dummy audio/video and software renderer; no physical-display or accessibility claim.',
          'cases': []}
for width, height in ((960, 700), (1280, 900), (1400, 820), (1672, 941)):
    for mode in ('dimensional', 'flat'):
        name = f'{width}x{height}-{mode}'
        bmp, png, diagnostic = (out / f'{name}.{extension}' for extension in ('bmp', 'png', 'json'))
        command = [str(args.exe), '--state', str(state), '--input-script', str(script),
                   '--workspace', 'play', '--width', str(width), '--height', str(height),
                   '--sample-rate', '48000', '--buffer-frames', '512',
                   '--screenshot', str(bmp), '--diagnostics', str(diagnostic)]
        if mode == 'flat':
            command.append('--flat')
        started = time.monotonic()
        process = subprocess.run(command, cwd=out, env=environment, capture_output=True, timeout=20)
        (out / f'{name}.stdout.txt').write_bytes(process.stdout)
        (out / f'{name}.stderr.txt').write_bytes(process.stderr)
        item = {'name': name, 'command': command, 'exit_code': process.returncode,
                'seconds': time.monotonic() - started}
        record['cases'].append(item)
        (report / f'a34-captures-{args.phase}.json').write_text(json.dumps(record, indent=2) + '\n')
        assert process.returncode == 0 and not process.stdout and not process.stderr, item
        data = json.loads(diagnostic.read_text())
        painted = data['presentation']['screenshot']
        assert data['errors']['count'] == 0
        assert painted['workspace'] == 'play' and painted['presentation'] == mode
        assert [painted['window_width'], painted['window_height']] == [width, height]
        assert data['runtime']['screenshot_written'] and data['runtime']['renderer'] == 'software'
        assert data['replay']['pushed_events'] == 32 and data['replay']['passed']
        assert data['replay']['controls_pending_before_shutdown'] is False
        assert data['session']['held_after_shutdown'] is False
        with Image.open(bmp) as original:
            original.load()
            pixels, size, image_mode = original.tobytes(), original.size, original.mode
            original.save(png, optimize=True)
        with Image.open(png) as converted:
            assert converted.size == size == (width, height)
            assert converted.mode == image_mode and converted.tobytes() == pixels
        item.update({'diagnostics_sha256': digest(diagnostic), 'paint_observation': painted,
                     'runtime': data['runtime'], 'session': data['session'], 'controls': data['controls'],
                     'png': str(png), 'png_sha256': digest(png), 'native_bmp_sha256': digest(bmp),
                     'decoded_sha256': hashlib.sha256(pixels).hexdigest(), 'lossless_conversion': True})
        bmp.unlink()
        assert digest(args.exe) == args.expected_sha256
        print(name, 'passed', flush=True)
(report / f'a34-captures-{args.phase}.json').write_text(json.dumps(record, indent=2) + '\n')
