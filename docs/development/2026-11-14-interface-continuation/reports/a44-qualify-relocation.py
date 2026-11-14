#!/usr/bin/env python3
"""Qualify actual final on/off packages in a private source-absent namespace."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import time


METADATA = {
    'STANDALONE_INSTALL.md': 'docs/STANDALONE_INSTALL.md',
    'STANDALONE_APP.md': 'docs/STANDALONE_APP.md',
    'STANDALONE_MODEL.md': 'docs/STANDALONE_MODEL.md',
    'MIDI_UI_RUNBOOK.md': 'docs/MIDI_UI_RUNBOOK.md',
    'PRESET_RUNBOOK.md': 'docs/PRESET_RUNBOOK.md',
    'INTERFACE_RUNBOOK.md': 'docs/INTERFACE_RUNBOOK.md',
    'THIRD_PARTY_NOTICES.md': 'THIRD_PARTY_NOTICES.md',
    'LICENSE-DejaVu.txt': 'assets/standalone/fonts/LICENSE-DejaVu.txt',
    'sdl2-lock.json': 'data/dependencies/sdl2-lock.json',
    'font-source-manifest.json': 'assets/standalone/fonts/source-manifest.json',
    'reference-source-manifest.json': 'assets/standalone/reference/manifest.json',
    'atlas-reference.json': 'docs/design/atlas-reference.json',
}
STATE = ('\tB3CONTROLS4\n'
         'registration_catalog atlas-chapel-nominal-v1 sha256 c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf\n'
         'expression +3.75e-1\n'
         'percussion enabled 1 harmonic third volume soft decay fast\n'
         'pedal drawbars 2 7\n'
         'manual upper selected A fixed_registration F# route_enabled 1\n'
         'bank A 0 1 2 3 4 5 6 7 8\n'
         'bank B 8 7 6 5 4 3 2 1 0\n'
         'manual lower selected B fixed_registration G# route_enabled 1\n'
         'bank A 1 3 5 7 0 2 4 6 8\n'
         'bank B 8 6 4 2 0 7 5 3 1\n'
         'end\n \t\n').replace('\n', '\r\n').encode('ascii')
CONTROLS = {
    'manual_drawbars': [[[0, 1, 2, 3, 4, 5, 6, 7, 8], [8, 7, 6, 5, 4, 3, 2, 1, 0]],
                       [[1, 3, 5, 7, 0, 2, 4, 6, 8], [8, 6, 4, 2, 0, 7, 5, 3, 1]]],
    'selected_banks': [0, 1], 'fixed_registrations': [6, 8], 'preset_selections': [6, 8],
    'route_enabled': [True, True], 'expression': 0.375, 'pedal_drawbars': [2, 7],
    'percussion': {'enabled': True, 'harmonic': 1, 'volume': 1, 'decay': 1},
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(path: Path) -> dict:
    return {'bytes': path.stat().st_size, 'sha256': sha(path)}


def inventory(root: Path) -> dict:
    paths = sorted(root.rglob('*'))
    assert all(stat.S_ISREG(p.lstat().st_mode) or stat.S_ISDIR(p.lstat().st_mode) for p in paths)
    return {str(p.relative_to(root)): identity(p) for p in paths if p.is_file()}


def tap(at: int, key: str, modifier: str = 'none') -> list:
    return [(at, f'key_down {key} {modifier} 0'), (at + 10, f'key_up {key} {modifier}')]


def collapsed(values: list) -> list:
    return [item for index, item in enumerate(values) if index == 0 or item != values[index - 1]]


def qualify(args, mode: str, enabled: bool) -> dict:
    build = args.build_on if enabled else args.build_off
    work = args.work / mode
    work.mkdir()
    unrelated = work / 'unrelated cwd 音'
    unrelated.mkdir()
    prefix, moved = work / 'original organ Ω', work / 'relocated organ Ω'
    output = args.reports / f'a44-{mode}-relocation.json'
    record = {'schema': 'a44-final-relocation-v1', 'status': 'running', 'mode': mode,
              'source': str(args.source), 'build': str(build), 'commands': [],
              'work': str(work), 'relocated_prefix': str(moved), 'native_invocations': 0,
              'physical_devices_used': False, 'shared_paths_renamed_or_removed': False}
    env = {k: v for k, v in os.environ.items() if not k.upper().startswith('HAMMOND_')}
    for name in ['DESTDIR', 'CMAKE_INSTALL_MODE', 'LD_LIBRARY_PATH', 'LD_PRELOAD']:
        env.pop(name, None)
    env.update(SDL_AUDIODRIVER='dummy', SDL_VIDEODRIVER='dummy', PYTHONDONTWRITEBYTECODE='1')

    def save() -> None:
        output.write_text(json.dumps(record, indent=2, ensure_ascii=False, sort_keys=True) + '\n')

    def run(name: str, command: list, expected: int = 0, *, no_sdl: bool = False) -> subprocess.CompletedProcess:
        current_env = dict(env)
        if no_sdl:
            current_env.update(SDL_AUDIODRIVER='a44_no_such_driver', SDL_VIDEODRIVER='a44_no_such_driver')
        started = time.monotonic()
        process = subprocess.run(list(map(str, command)), cwd=unrelated, env=current_env,
                                 stdin=subprocess.DEVNULL, capture_output=True, text=True,
                                 encoding='utf-8', errors='replace', timeout=25, check=False)
        item = {'name': name, 'command': list(map(str, command)), 'returncode': process.returncode,
                'expected_returncode': expected, 'elapsed_seconds': round(time.monotonic() - started, 4),
                'stdout': process.stdout, 'stderr': process.stderr,
                'driver_mode': 'deliberately invalid' if no_sdl else 'dummy'}
        record['commands'].append(item)
        save()
        print(f'{mode}/{name}: exit {process.returncode}, {item["elapsed_seconds"]} s', flush=True)
        assert process.returncode == expected, item
        return process

    def isolated(name: str, command: list, expected: int = 0, *, no_sdl: bool = False):
        return run(name, [*namespace, '--', *command], expected, no_sdl=no_sdl)

    def native(name: str, arguments: list, *, state_present: bool, loader_debug: bool = False) -> dict:
        state = unrelated / f'{name}.b3controls'
        if state_present:
            state.write_bytes(STATE)
        command = ['/app/bin/hammond_standalone', '--state', f'/run-work/{state.name}',
                   '--diagnostics', f'/run-work/{name}-diagnostics.json', '--width', '960', '--height', '700',
                   *arguments]
        if loader_debug:
            command = ['/usr/bin/env', 'LD_DEBUG=libs', f'LD_DEBUG_OUTPUT=/run-work/{name}-loader', *command]
        process = isolated(name, command)
        record['native_invocations'] += 1
        diagnostics = unrelated / f'{name}-diagnostics.json'
        retained = args.reports / f'a44-{mode}-{name}-diagnostics.json'
        shutil.copyfile(diagnostics, retained)
        data = json.loads(diagnostics.read_text())
        assert data['schema_version'] == 3 and data['application'] == 'hammond_standalone'
        assert data['profile'] == {'id': 'nominal-unmeasured-v1', 'authoring_sha256':
                                  '49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83'}
        assert data['runtime']['video_driver'] == data['audio']['driver'] == 'dummy'
        assert data['runtime']['renderer'] == 'software' and data['runtime']['sdl_version'] == '2.32.10'
        assert data['runtime']['rendered_images'] > 0
        assert data['audio']['open_before_shutdown'] and data['audio']['running_before_shutdown']
        assert data['audio']['callback_count'] > 0 and data['audio']['rendered_frames'] > 0
        assert all(data['audio'][k] == 0 for k in ('render_failures', 'format_failures', 'nonfinite_failures', 'overrange_failures'))
        assert data['session']['snapshot_available'] and data['session']['prepared']
        assert data['session']['fault_flags'] == 0
        assert not data['session']['running_after_shutdown'] and not data['session']['held_after_shutdown']
        midi = data['midi']
        assert midi['backend_available'] == enabled and midi['backend'] == ('ALSA' if enabled else 'unavailable')
        assert midi['state_after_shutdown'] == ('closed' if enabled else 'unavailable')
        assert midi['source'] == 'none' and midi['requested_port'] == midi['port_name'] == ''
        assert midi['quiescent_after_shutdown'] and midi['diagnostics_stable_after_shutdown']
        assert not midi['active_before_shutdown'] and not midi['active_after_shutdown'] and not midi['shutdown_failed']
        assert not midi['discovery']['pending_after_shutdown'] and midi['discovery']['started'] == 0
        assert midi['device']['callback_messages'] == midi['open_failures'] == midi['inbox']['received_packets'] == 0
        assert data['errors'] == {'count': 0, 'last': ''} and process.stderr == ''
        assert data['state_path'] == f'/run-work/{state.name}'
        assert state.read_bytes() == STATE if state_present else not state.exists()
        if '--smoke-ms' in arguments:
            match = re.fullmatch(r'Native SDL smoke passed: callbacks=(\d+), frames=(\d+), images=(\d+), driver=dummy\n', process.stdout)
            assert match and tuple(map(int, match.groups())) == (data['audio']['callback_count'],
                data['audio']['rendered_frames'], data['runtime']['rendered_images'])
        else:
            assert process.stdout == ''
        return data

    try:
        binary = build / 'apps/standalone/hammond_standalone'
        inputs = {name: args.source / path for name, path in METADATA.items()}
        inputs.update({'LICENSE-SDL2.txt': args.sdl / 'LICENSE.txt',
                       'standalone-capabilities.json': build / 'generated/standalone-capabilities.json'})
        if enabled:
            prepared = build / 'apps/standalone/hammond_rtmidi-prepared'
            inputs.update({'LICENSE-RtMidi.txt': prepared / 'LICENSE',
                'rtmidi-lock.json': args.source / 'data/dependencies/rtmidi-lock.json',
                'rtmidi-prepared-source.json': prepared / 'prepared-source.json',
                'rtmidi-coremidi-zero-init.patch': prepared / 'rtmidi-coremidi-zero-init.patch'})
        expected = {'bin/hammond_standalone': identity(binary), **{
            'share/hammond-b3-organ/standalone/' + name: identity(path) for name, path in inputs.items()}}
        assert len(expected) == (19 if enabled else 15)
        record['expected_payload'] = expected
        run('install', [args.cmake, '--install', build, '--config', 'Release', '--component', 'Standalone', '--prefix', prefix])
        assert inventory(prefix) == expected
        prefix.rename(moved)
        assert not prefix.exists() and inventory(moved) == expected
        meta = moved / 'share/hammond-b3-organ/standalone'
        cap = json.loads((meta / 'standalone-capabilities.json').read_text())
        assert cap['midi']['enabled'] == enabled
        assert cap['midi']['backend'] == ('ALSA' if enabled else 'unavailable')
        assert cap['profile'] == 'embedded nominal-unmeasured-v1'
        assert cap['fonts']['embedded'] and cap['reference_art']['embedded']
        assert cap['sdl2']['license_sha256'] == sha(meta / 'LICENSE-SDL2.txt')
        assert cap['fonts']['license_sha256'] == sha(meta / 'LICENSE-DejaVu.txt')
        assert cap['fonts']['manifest_sha256'] == sha(meta / 'font-source-manifest.json')
        assert cap['reference_art']['manifest_sha256'] == sha(meta / 'reference-source-manifest.json')
        if enabled:
            assert cap['midi']['rtmidi']['license_sha256'] == sha(meta / 'LICENSE-RtMidi.txt')
            assert cap['midi']['rtmidi']['prepared_manifest_sha256'] == sha(meta / 'rtmidi-prepared-source.json')
            assert cap['midi']['rtmidi']['patch_sha256'] == sha(meta / 'rtmidi-coremidi-zero-init.patch')
        else:
            assert cap['midi']['rtmidi'] is None
            assert not any('rtmidi' in p.lower() for p in expected)
        links = []
        for name in [n for n in METADATA if n.endswith('.md')]:
            for target in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)', (meta / name).read_text()):
                if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target) or target.startswith('#'):
                    continue
                assert (meta / target.split('#', 1)[0]).is_file(), (name, target)
                links.append({'source': name, 'target': target})
        record.update(capabilities=cap, installed_relative_links=links)
        namespace = ['/usr/bin/bwrap', '--die-with-parent', '--new-session', '--unshare-pid',
                     '--ro-bind', '/usr', '/usr', '--ro-bind', '/lib', '/lib',
                     '--ro-bind', '/lib64', '/lib64', '--ro-bind', '/bin', '/bin',
                     '--ro-bind', '/etc', '/etc', '--proc', '/proc', '--dev', '/dev',
                     '--tmpfs', '/tmp', '--ro-bind', str(moved), '/app',
                     '--bind', str(unrelated), '/run-work', '--chdir', '/run-work']
        absent = [str(args.source), str(args.build_on), str(args.build_off), str(args.sdl),
                  '/workspace/scratch/cd4bd06ce68f/rtmidi',
                  '/workspace/scratch/641ca55ce6de/native-sysroot/usr', str(prefix)]
        probe_code = 'import os,json,sys; p={x:os.path.exists(x) for x in sys.argv[1:]}; print(json.dumps(p,sort_keys=True)); assert not any(p.values())'
        proof = isolated('source-absence-proof', ['/usr/bin/python3', '-c', probe_code, *absent])
        record['namespace_absence_proof'] = json.loads(proof.stdout)
        record['namespace_mounts'] = namespace
        elf = run('elf-dynamic', ['/usr/bin/readelf', '-d', moved / 'bin/hammond_standalone'])
        record['elf_dynamic_dependencies'] = [line.strip() for line in elf.stdout.splitlines()
            if '(NEEDED)' in line or '(RPATH)' in line or '(RUNPATH)' in line]
        dependencies = isolated('runtime-library-resolution', ['/usr/bin/ldd', '/app/bin/hammond_standalone'])
        assert 'not found' not in dependencies.stdout and '/workspace/' not in dependencies.stdout
        if enabled:
            assert 'libasound.so.2 => /lib/x86_64-linux-gnu/libasound.so.2' in dependencies.stdout
        else:
            assert 'libasound' not in dependencies.stdout
        record['isolated_runtime_libraries'] = dependencies.stdout.splitlines()
        help_result = isolated('help', ['/app/bin/hammond_standalone', '--help'], no_sdl=True)
        record['native_invocations'] += 1
        assert '--workspace' in help_result.stdout and '--flat' in help_result.stdout and help_result.stderr == ''
        assert not list(unrelated.iterdir())
        rejected = isolated('invalid-workspace', ['/app/bin/hammond_standalone', '--workspace', 'a44_invalid',
            '--state', '/run-work/rejected-state.b3controls', '--screenshot', '/run-work/rejected.bmp',
            '--diagnostics', '/run-work/rejected.json'], 2, no_sdl=True)
        record['native_invocations'] += 1
        assert 'Unsupported value for --workspace' in rejected.stderr and rejected.stdout == ''
        assert not list(unrelated.iterdir())
        workspace, presentation = ('play', 'dimensional') if enabled else ('service', 'flat')
        arguments = ['--workspace', workspace, '--smoke-ms', '600', '--screenshot', '/run-work/smoke.bmp']
        if presentation == 'flat':
            arguments.append('--flat')
        smoke = native('smoke', arguments, state_present=False, loader_debug=True)
        assert smoke['smoke']['passed'] and smoke['smoke']['held_observed'] and smoke['smoke']['release_observed']
        shot = smoke['presentation']['screenshot']
        assert shot['workspace'] == workspace and shot['presentation'] == presentation
        assert shot['inspection']['snapshot_available'] and not shot['inspection']['controls_pending']
        bmp = unrelated / 'smoke.bmp'
        from PIL import Image
        png = args.reports / f'a44-{mode}-relocated-{workspace}.png'
        with Image.open(bmp) as image:
            assert image.size == (960, 700)
            pixels = image.convert('RGBA').tobytes()
            assert len(set(pixels)) > 32
            image.save(png)
        with Image.open(png) as image:
            assert image.convert('RGBA').tobytes() == pixels
        record['capture'] = {'bmp_identity': identity(bmp), 'png_identity': identity(png),
                             'png': png.name, 'painted_view': shot, 'reencoded_pixels_equal': True}
        bmp.unlink()
        loader_logs = list(unrelated.glob('smoke-loader.*'))
        assert len(loader_logs) == 1, loader_logs
        trace = loader_logs[0]
        retained_trace = args.reports / f'a44-{mode}-smoke-loader.txt'
        shutil.copyfile(trace, retained_trace)
        successful = [line.strip() for line in trace.read_text().splitlines() if 'calling init:' in line]
        assert all('/workspace/' not in line for line in successful), successful
        record['runtime_loader_trace'] = {'file': retained_trace.name, 'identity': identity(retained_trace),
            'successful_library_initializers': successful,
            'development_runpath_lookup_attempts': sum('trying file=/workspace/' in line for line in trace.read_text().splitlines()),
            'all_workspace_paths_absent_by_namespace_proof': True,
            'system_alsa_initialized': any('calling init: /lib/x86_64-linux-gnu/libasound.so.2' in line for line in successful)}
        if enabled:
            assert record['runtime_loader_trace']['system_alsa_initialized']
        events = [(180, 'key_down A none 0')] + tap(400, 'F5') + tap(500, 'O', 'ctrl')
        events += tap(650, 'F7') + tap(850, 'F6') + tap(1050, 'F4') + tap(1250, 'F7')
        events += [(1430, 'key_up A alt+shift')]
        script = unrelated / 'navigation.b3ui'
        script.write_text('B3UIREPLAY1\nduration_ms 1700\n' + ''.join(f'{at} {event}\n' for at, event in events))
        shutil.copyfile(script, args.reports / f'a44-{mode}-navigation.b3ui')
        replay = native('navigation', ['--input-script', '/run-work/navigation.b3ui'], state_present=True)
        data = replay['replay']
        assert data['passed'] and data['completed'] and data['final_acknowledged']
        assert data['scheduled_events'] == data['pushed_events'] == len(events)
        assert data['accepted_note_on_commands'] == data['accepted_note_off_commands'] == 1
        assert not data['controls_pending_before_shutdown'] and not data['save_pending_before_shutdown']
        assert data['before_shutdown']['manual_notes'] == [[], []] and data['before_shutdown']['pedal_ids'] == []
        assert all(item['controls'] == CONTROLS for item in data['observations'])
        assert replay['controls'] == CONTROLS and replay['status'] == 'Loaded saved controls.'
        frames = replay['presentation']['observations'] + [replay['presentation']['last_painted']]
        assert not replay['presentation']['observations_truncated']
        views = collapsed([(f['workspace'], f['presentation']) for f in frames])
        assert views == [('play', 'dimensional'), ('rotary', 'dimensional'), ('rotary', 'flat'),
                         ('service', 'flat'), ('play', 'flat'), ('play', 'dimensional')], views
        clocks = [f['inspection']['frame_clock'] for f in frames if f['inspection']['snapshot_available']]
        assert clocks == sorted(clocks) and clocks[-1] > clocks[0]
        record['navigation'] = {'views': views, 'on_off_commands': [1, 1], 'scheduled_events': len(events),
            'controls_unchanged': True, 'frame_clock_monotonic': True,
            'live_load_status': replay['status'], 'state_sha256': sha(unrelated / 'navigation.b3controls')}
        assert inventory(moved) == expected and identity(binary) == expected['bin/hammond_standalone']
        assert all(identity(path) == expected['share/hammond-b3-organ/standalone/' + name]
                   for name, path in inputs.items())
        record.update(status='passed', payload_count=len(expected), payload_bytes=sum(x['bytes'] for x in expected.values()),
                      payload_unchanged=True, built_binary_unchanged=True, installed_sources_exact_and_unchanged=True)
    except Exception as error:
        record.update(status='failed', failure=f'{type(error).__name__}: {error}')
        raise
    finally:
        save()
    return record


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'build-on', 'build-off', 'cmake', 'sdl', 'work', 'reports'):
        parser.add_argument('--' + name, type=Path, required=True)
    args = parser.parse_args()
    args.work.mkdir(parents=True, exist_ok=False)
    results = [qualify(args, mode, enabled) for mode, enabled in [('midi-on', True), ('midi-off', False)]]
    spec = importlib.util.spec_from_file_location('a44build', args.reports / 'a44-build-packages.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    before = json.loads((args.reports / 'a44-source-before.json').read_text())
    after = module.source_snapshot()
    module.write('a44-source-after-relocation.json', after)
    protected = json.loads((args.reports / 'a12-boundary-inventory.json').read_text())
    mismatches = [row[0] for row in protected['files'] if sha(args.source / row[0]) != row[4]]
    final = {'schema': 'a44-final-package-result-v1', 'status': 'passed', 'assignment': 44,
        'worker': '/root/w08_a44_final_package', 'head_before': before['head'], 'head_after': after['head'],
        'production_count': after['production_count'], 'production_inventory_sha256': after['production_inventory_sha256'],
        'production_unchanged': before['production_sha256'] == after['production_sha256'],
        'installed_sources_unchanged': before['installed_sources_sha256'] == after['installed_sources_sha256'],
        'build_install_drift': {p: {'before': old, 'after': after['build_install_sha256'].get(p)}
            for p, old in before['build_install_sha256'].items() if old != after['build_install_sha256'].get(p)},
        'protected_files': len(protected['files']), 'protected_mismatches': mismatches,
        'install_ctest_suites_passed': 2, 'install_unittest_methods_passed': 16,
        'independent_native_invocations': sum(r['native_invocations'] for r in results),
        'packages': {r['mode']: {'executable': r['expected_payload']['bin/hammond_standalone'],
            'payload_files': r['payload_count'], 'payload_bytes': r['payload_bytes'],
            'report': f'a44-{r["mode"]}-relocation.json'} for r in results},
        'limits': ['Linux local Release; explicit SDL dummy audio/video and no selected MIDI input.',
                   'Two moved local component payloads; not signed installers or independently acquired machines.',
                   'Source/build/SDK/sysroot absent in private namespace; system C/C++ and enabled ALSA runtime still required.',
                   'Existing enabled RUNPATH retained; nonexistent development path falls back to system ALSA.',
                   'No physical audio/MIDI, display/DPI, persistent pointer capture, timing deadline, pixel equality, accessibility, host or release-rights claim.']}
    assert final['production_unchanged'] and final['installed_sources_unchanged'] and not mismatches
    module.write('a44-final-package-result.json', final)
    print(json.dumps({k: final[k] for k in ['status', 'install_ctest_suites_passed', 'install_unittest_methods_passed', 'independent_native_invocations']}))


if __name__ == '__main__':
    main()
