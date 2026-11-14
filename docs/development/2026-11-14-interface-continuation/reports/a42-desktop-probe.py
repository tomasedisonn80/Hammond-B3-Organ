#!/usr/bin/env python3
"""One bounded native X11 launch; run from the actual desktop's terminal.

This records failure as failure. It never substitutes dummy/offscreen video,
installs dependencies, builds code, or synthesizes operating-system input.
The existing app's B3UIREPLAY1 transport is explicitly scripted SDL input.
"""

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time


ROOT = Path('/workspace/scratch/601951e27dc3')
REPO = ROOT / 'Hammond-B3-Organ'
REPORTS = REPO / 'docs/development/2026-11-14-interface-continuation/reports'
EXE = ROOT / 'a42-desktop-bin/hammond_standalone'
EXPECTED = 'bd4991a3b45543a01c9ce435da140af848d45f28ff535699397706e5d3925dc2'
OUT = REPORTS / 'a42-desktop-evidence'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    OUT.mkdir(exist_ok=False)
    assert digest(EXE) == EXPECTED
    display = os.environ.get('DISPLAY')
    assert display, 'Run from the actual desktop terminal with its DISPLAY.'
    source = json.loads((REPORTS / 'a36-build.json').read_text())
    source_hashes = source['source_sha256_after_build']
    changed_sources = [name for name, sha in source_hashes.items()
                       if digest(REPO / name) != sha]
    config = ROOT / 'build-native/_sdl2/include-config-release/SDL2/SDL_config.h'
    config_lines = [line for line in config.read_text().splitlines()
                    if 'SDL_VIDEO_DRIVER_' in line or 'SDL_VIDEO_RENDER_' in line]
    env = dict(os.environ)
    env.update(SDL_AUDIODRIVER='dummy', SDL_VIDEODRIVER='x11')
    env.pop('SDL_RENDER_DRIVER', None)
    command = [str(EXE), '--width', '1280', '--height', '900',
               '--state', str(OUT / 'absent-state.b3controls'),
               '--input-script', str(REPORTS / 'a42-desktop-pointer.b3uireplay'),
               '--screenshot', str(OUT / 'frame.bmp'),
               '--diagnostics', str(OUT / 'diagnostics.json')]
    started = datetime.now(timezone.utc).isoformat()
    start = time.monotonic()
    try:
        run = subprocess.run(command, cwd=REPO, env=env, stdin=subprocess.DEVNULL,
                             capture_output=True, text=True, timeout=15)
        exit_code, stdout, stderr = run.returncode, run.stdout, run.stderr
        timed_out = False
    except subprocess.TimeoutExpired as exc:
        exit_code, stdout, stderr, timed_out = None, exc.stdout or '', exc.stderr or '', True
        if isinstance(stdout, bytes): stdout = stdout.decode('utf-8', 'replace')
        if isinstance(stderr, bytes): stderr = stderr.decode('utf-8', 'replace')
    elapsed = time.monotonic() - start
    (OUT / 'stdout.txt').write_text(stdout)
    (OUT / 'stderr.txt').write_text(stderr)
    after_sources = [name for name, sha in source_hashes.items()
                     if digest(REPO / name) != sha]
    result = {
        'timestamp_utc': started,
        'working_directory': str(REPO),
        'command': command,
        'timeout_seconds': 15,
        'elapsed_seconds': elapsed,
        'returncode': exit_code,
        'timed_out': timed_out,
        'stdout': stdout,
        'stderr': stderr,
        'desktop_process_environment': {
            'display': display, 'wayland_display': os.environ.get('WAYLAND_DISPLAY'),
            'hostname': os.uname().nodename,
            'x11_socket_names': sorted(p.name for p in Path('/tmp/.X11-unix').glob('*')),
            'python': os.sys.version,
        },
        'selected_environment': {'SDL_VIDEODRIVER': 'x11', 'SDL_AUDIODRIVER': 'dummy',
                                 'SDL_RENDER_DRIVER': None},
        'executable': {'path': str(EXE), 'sha256_before': EXPECTED,
                       'sha256_after': digest(EXE), 'bytes': EXE.stat().st_size},
        'source_identity': {'a36_build_report_sha256': digest(REPORTS / 'a36-build.json'),
                            'input_count': len(source_hashes),
                            'changed_paths_before': changed_sources,
                            'changed_paths_after': after_sources},
        'generated_sdl_config': {'path': str(config), 'sha256': digest(config),
                                 'video_lines': config_lines},
        'native_diagnostics_written': (OUT / 'diagnostics.json').exists(),
        'native_screenshot_written': (OUT / 'frame.bmp').exists(),
        'state_written': (OUT / 'absent-state.b3controls').exists(),
    }
    (REPORTS / 'a42-desktop-launch.json').write_text(json.dumps(result, indent=2) + '\n')
    print('A42 native launch returncode:', exit_code)
    print(stderr.strip() or 'No stderr')
    print('Diagnostics written:', result['native_diagnostics_written'])
    print('Evidence: reports/a42-desktop-launch.json')
    assert digest(EXE) == EXPECTED


if __name__ == '__main__':
    main()
