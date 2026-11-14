#!/usr/bin/env python3
"""Record A44's reused, separate native configurations and bounded install gates."""

from __future__ import annotations

import hashlib
import argparse
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import time

SOURCE = Path(__file__).resolve().parents[4]
REPORTS = Path(__file__).resolve().parent
WORKSPACE = SOURCE.parent
CMAKE = Path('/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/cmake')
CTEST = CMAKE.with_name('ctest')
SDL = Path('/workspace/scratch/7ffc2842608b/SDL2')
RTMIDI = Path('/workspace/scratch/cd4bd06ce68f/rtmidi')
SYSROOT = Path('/workspace/scratch/641ca55ce6de/native-sysroot/usr')
GUIDES = ['STANDALONE_INSTALL.md', 'STANDALONE_APP.md', 'STANDALONE_MODEL.md',
          'MIDI_UI_RUNBOOK.md', 'PRESET_RUNBOOK.md', 'INTERFACE_RUNBOOK.md']


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(path: Path) -> dict:
    return {'bytes': path.stat().st_size, 'sha256': sha(path)}


def write(name: str, value: dict) -> None:
    (REPORTS / name).write_text(json.dumps(value, indent=2, sort_keys=True) + '\n')


def digest(files: dict) -> str:
    return hashlib.sha256(''.join(f'{p}\0{v}\n' for p, v in sorted(files.items())).encode()).hexdigest()


def source_snapshot() -> dict:
    previous = json.loads((REPORTS / 'a29-source-before.json').read_text())
    paths = set(previous['production_sha256'])
    paths.update(str(p.relative_to(SOURCE)) for base in ('src', 'include')
                 for p in (SOURCE / base).rglob('*') if p.is_file())
    paths.update(str(p.relative_to(SOURCE)) for p in (SOURCE / 'apps/standalone').iterdir()
                 if p.suffix in ('.cpp', '.h'))
    production = {p: sha(SOURCE / p) for p in sorted(paths)}
    build_paths = ['CMakeLists.txt', 'apps/standalone/CMakeLists.txt',
                   'apps/standalone/native_tests/test_standalone_install.py']
    build_paths += [str(p.relative_to(SOURCE)) for p in (SOURCE / 'cmake').glob('*.cmake')]
    build_install = {p: sha(SOURCE / p) for p in sorted(build_paths)}
    installed_sources = {f'docs/{name}': sha(SOURCE / 'docs' / name) for name in GUIDES}
    installed_sources['THIRD_PARTY_NOTICES.md'] = sha(SOURCE / 'THIRD_PARTY_NOTICES.md')
    installed_sources[str(SDL / 'LICENSE.txt')] = sha(SDL / 'LICENSE.txt')
    git = lambda *args: subprocess.check_output(['git', *args], cwd=SOURCE, text=True).strip()
    return {'head': git('rev-parse', 'HEAD'), 'committed_tree': git('rev-parse', 'HEAD^{tree}'),
            'production_count': len(production), 'production_sha256': production,
            'production_inventory_sha256': digest(production),
            'build_install_sha256': build_install, 'installed_sources_sha256': installed_sources,
            'platform': platform.platform(), 'free_disk_bytes': shutil.disk_usage(SOURCE).free}


def run(name: str, command: list[str], record: dict, timeout: int = 600) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE='1', SDL_AUDIODRIVER='dummy', SDL_VIDEODRIVER='dummy')
    started = time.monotonic()
    result = subprocess.run(list(map(str, command)), cwd=SOURCE, env=env, text=True,
                            capture_output=True, timeout=timeout, check=False)
    log = REPORTS / f'a44-{name}.txt'
    log.write_text(result.stdout + result.stderr)
    item = {'name': name, 'command': list(map(str, command)), 'cwd': str(SOURCE),
            'returncode': result.returncode, 'elapsed_seconds': round(time.monotonic() - started, 4),
            'log': log.name, 'log_identity': identity(log)}
    record['commands'].append(item)
    write('a44-build-result.json', record)
    print(f'{name}: exit {result.returncode}, {item["elapsed_seconds"]} s', flush=True)
    assert result.returncode == 0, item
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--resume', action='store_true', help='Resume after the retained CTest-output assertion correction.')
    args = parser.parse_args()
    record = {'schema': 'a44-native-build-install-v1', 'status': 'running', 'commands': [],
              'worker': '/root/w08_a44_final_package', 'assignment': 44,
              'builds': {}, 'full_test_matrix_repeated': False}
    if args.resume:
        record = json.loads((REPORTS / 'a44-build-result.json').read_text())
        write('a44-build-result-first.json', record)
        before = json.loads((REPORTS / 'a44-source-before.json').read_text())
        original = (REPORTS / 'a44-midi-on-install-ctest.txt').read_text()
        assert re.search(r'100% tests passed(?:, 0 tests failed)? out of 1', original)
        assert re.search(r'Ran 8 tests in ', original)
        assert record['commands'][-1]['returncode'] == 0
        record['builds']['midi-on']['install_ctest'] = {'suites_passed': 1, 'unittest_methods_passed': 8}
        record['retained_harness_correction'] = {
            'original_result': 'a44-build-result-first.json',
            'reason': 'CTest 4.4.4 reports "100% tests passed out of 1" without the older zero-failures clause.',
            'product_result': 'Original exit 0 and all eight methods passed; unchanged suite not rerun.'}
        record.pop('failure', None)
        record['status'] = 'running'
    else:
        before = source_snapshot()
        write('a44-source-before.json', before)
    try:
        for mode, enabled in [('midi-on', True), ('midi-off', False)]:
            if args.resume and mode == 'midi-on':
                continue
            build = WORKSPACE / ('build-native' if enabled else 'build-native-midi-off')
            exe = build / 'apps/standalone/hammond_standalone'
            item = {'path': str(build), 'executable_before': identity(exe)}
            record['builds'][mode] = item
            command = [CMAKE, '-S', SOURCE, '-B', build, '-DCMAKE_BUILD_TYPE=Release',
                       '-DBUILD_TESTING=ON', '-DHAMMOND_BUILD_STANDALONE=ON',
                       '-DHAMMOND_BUILD_VST3=OFF', '-DHAMMOND_ENABLE_SANITIZERS=OFF',
                       f'-DHAMMOND_ENABLE_MIDI={"ON" if enabled else "OFF"}', '-DSDL_ALSA=OFF',
                       f'-DHAMMOND_SDL2_ROOT={SDL}', f'-DHAMMOND_RTMIDI_ROOT={RTMIDI if enabled else ""}']
            if enabled:
                command += [f'-DALSA_INCLUDE_DIR={SYSROOT}/include',
                            f'-DALSA_LIBRARY={SYSROOT}/lib/x86_64-linux-gnu/libasound.so']
            run(f'{mode}-configure', command, record)
            run(f'{mode}-build', [CMAKE, '--build', build, '--config', 'Release', '--target',
                                 'hammond_standalone', '--parallel', '3'], record)
            after_build = source_snapshot()
            write(f'a44-{mode}-source-after-build.json', after_build)
            for key in ['production_sha256', 'installed_sources_sha256']:
                assert after_build[key] == before[key], (mode, key, 'inputs changed during build')
            item['executable'] = identity(exe)
            item['configuration'] = {line.split('=', 1)[0]: line.split('=', 1)[1]
                for line in (build / 'CMakeCache.txt').read_text().splitlines()
                if re.match(r'^(HAMMOND_|ALSA_|SDL_ALSA:|BUILD_TESTING:|CMAKE_BUILD_TYPE:|CMAKE_CXX_COMPILER:|CMAKE_GENERATOR:)', line)}
            generated_paths = [build / 'CMakeCache.txt', build / 'generated/standalone-capabilities.json',
                               build / 'apps/standalone/CMakeFiles/hammond_standalone_support.dir/flags.make',
                               build / 'apps/standalone/CMakeFiles/hammond_standalone.dir/link.txt',
                               build / 'apps/standalone/generated/EmbeddedProfile.h',
                               build / 'apps/standalone/generated/ReferenceArtData.h',
                               build / 'libhammond_core.a']
            generated_paths += sorted((build / 'apps/standalone').glob('libhammond_*.a'))
            item['generated_and_library_identity'] = {str(p.relative_to(build)): identity(p)
                                                       for p in generated_paths}
            define = f'-DHAMMOND_HAS_RTMIDI={int(enabled)}'
            assert define in (build / 'apps/standalone/CMakeFiles/hammond_standalone_support.dir/flags.make').read_text()
            if enabled:
                assert item['executable']['sha256'] == 'bd4991a3b45543a01c9ce435da140af848d45f28ff535699397706e5d3925dc2'
            result = run(f'{mode}-install-ctest', [CTEST, '--test-dir', build, '-C', 'Release',
                         '--verbose', '--output-on-failure', '--no-tests=error',
                         '-R', '^test_standalone_install$'], record, timeout=180)
            assert re.search(r'100% tests passed(?:, 0 tests failed)? out of 1', result.stdout)
            assert re.search(r'Ran 8 tests in ', result.stdout)
            item['install_ctest'] = {'suites_passed': 1, 'unittest_methods_passed': 8}
        after = source_snapshot()
        write('a44-source-after-build-tests.json', after)
        record['production_unchanged'] = after['production_sha256'] == before['production_sha256']
        record['installed_sources_unchanged'] = after['installed_sources_sha256'] == before['installed_sources_sha256']
        record['build_install_drift'] = {p: {'before': old, 'after': after['build_install_sha256'].get(p)}
            for p, old in before['build_install_sha256'].items() if after['build_install_sha256'].get(p) != old}
        record['production_inventory_sha256'] = after['production_inventory_sha256']
        record['status'] = 'passed'
    except Exception as error:
        record.update(status='failed', failure=f'{type(error).__name__}: {error}')
        raise
    finally:
        write('a44-build-result.json', record)


if __name__ == '__main__':
    main()
