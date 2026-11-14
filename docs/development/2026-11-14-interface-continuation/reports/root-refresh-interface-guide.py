#!/usr/bin/env python3
"""Install the reviewed interface-guide update without rebuilding qualified code."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import time

REPORTS = Path(__file__).resolve().parent
REPO = REPORTS.parents[3]
CMAKE = Path('/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/cmake')
GUIDE = 'share/hammond-b3-organ/standalone/INTERFACE_RUNBOOK.md'


def identity(path):
    data = path.read_bytes()
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def inventory(root):
    paths = sorted(root.rglob('*'))
    assert all(stat.S_ISREG(p.lstat().st_mode) or stat.S_ISDIR(p.lstat().st_mode) for p in paths)
    return {str(p.relative_to(root)): identity(p) for p in paths if p.is_file()}


def main():
    old = json.loads((REPORTS / 'a44-package-refresh.json').read_text())
    baseline = json.loads((REPORTS / 'a49-source-before-ctest.json').read_text())
    work = REPO.parent / 'root-final-guide-packages-configured'
    work.mkdir(exist_ok=False)
    report = {'schema': 'root-final-guide-package-refresh-v1', 'status': 'running',
              'basis': 'a44-package-refresh.json', 'packages': {}, 'commands': [],
              'native_invocations': 0, 'rebuilds': 0, 'configures': 0,
              'first_attempt': 'root-guide-first-attempt/root-final-guide-package-refresh.json',
              'first_attempt_outcome': 'Installer correctly rejected stale configured guide identity. Reconfigure required; original failure and script retained.',
              'scope': 'Fresh component install and exact payload comparison only. Existing A44 runtime and relocation evidence remains separately identified.'}
    env = dict(os.environ)
    for key in ['DESTDIR', 'CMAKE_INSTALL_MODE']:
        env.pop(key, None)
    try:
        for path, expected in baseline['production_inputs']['files'].items():
            assert identity(REPO / path) == expected, path
        for mode in ['midi-on', 'midi-off']:
            previous = old['packages'][mode]['payload']
            expected = dict(previous)
            expected[GUIDE] = identity(REPO / 'docs/INTERFACE_RUNBOOK.md')
            changes = {p: {'before': previous.get(p), 'after': value}
                       for p, value in expected.items() if previous.get(p) != value}
            assert set(changes) == {GUIDE}, changes
            build = REPO.parent / ('build-native' if mode == 'midi-on' else 'build-native-midi-off')
            executable = build / 'apps/standalone/hammond_standalone'
            assert identity(executable) == previous['bin/hammond_standalone']
            prefix = work / mode
            configure = list(map(str, [CMAKE, '-S', REPO, '-B', build]))
            configured = subprocess.run(configure, cwd=REPO, env=env, capture_output=True,
                                        text=True, timeout=60)
            configure_log = REPORTS / f'root-final-guide-{mode}-configure.txt'
            configure_log.write_text(configured.stdout + configured.stderr)
            report['commands'].append({'command': configure, 'returncode': configured.returncode,
                'log': configure_log.name, 'log_identity': identity(configure_log)})
            report['configures'] += 1
            assert configured.returncode == 0
            command = list(map(str, [CMAKE, '--install', build, '--config', 'Release',
                                    '--component', 'Standalone', '--prefix', prefix]))
            started = time.monotonic()
            process = subprocess.run(command, cwd=REPO, env=env, capture_output=True,
                                     text=True, timeout=60)
            log = REPORTS / f'root-final-guide-{mode}-install.txt'
            log.write_text(process.stdout + process.stderr)
            report['commands'].append({'command': command, 'returncode': process.returncode,
                'elapsed_seconds': round(time.monotonic() - started, 4),
                'log': log.name, 'log_identity': identity(log)})
            assert process.returncode == 0
            assert inventory(prefix) == expected
            metadata = prefix / 'share/hammond-b3-organ/standalone'
            relative_links = []
            for guide in metadata.glob('*.md'):
                for target in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)', guide.read_text()):
                    if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target) or target.startswith('#'):
                        continue
                    assert (metadata / target.split('#', 1)[0]).is_file(), (guide, target)
                    relative_links.append({'source': guide.name, 'target': target})
            assert identity(executable) == previous['bin/hammond_standalone']
            report['packages'][mode] = {'prefix': str(prefix), 'payload': expected,
                'payload_files': len(expected), 'payload_bytes': sum(p['bytes'] for p in expected.values()),
                'only_payload_change': changes, 'binary_unchanged': True,
                'installed_relative_links': relative_links}
        for path, expected in baseline['production_inputs']['files'].items():
            assert identity(REPO / path) == expected, path
        report.update(status='passed', production_inputs_unchanged=98,
                      guide_identity=identity(REPO / 'docs/INTERFACE_RUNBOOK.md'))
    except Exception as error:
        report.update(status='failed', failure=f'{type(error).__name__}: {error}')
        raise
    finally:
        (REPORTS / 'root-final-guide-package-refresh.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'status': report['status'], 'packages': {
        mode: {key: value[key] for key in ['payload_files', 'payload_bytes', 'binary_unchanged']}
        for mode, value in report['packages'].items()}}))


if __name__ == '__main__':
    main()
