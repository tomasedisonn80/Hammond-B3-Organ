#!/usr/bin/env python3
"""Refresh only the reviewed installed-guide change; retain earlier runtime evidence."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import shutil
import subprocess
import time


REPORTS = Path(__file__).resolve().parent
SOURCE = REPORTS.parents[3]
EXPECTED_GUIDE = 'f51b2c32f5f6e6aa062885bd2b1b64fee24faf85712f4bca9a3b8f1a600695a1'
GUIDE = 'share/hammond-b3-organ/standalone/MIDI_UI_RUNBOOK.md'
TIMEOUTS = {'test_standalone_workspace_raster': 60.0,
            'test_standalone_scaled_view': 60.0,
            'test_standalone_preset_raster': 30.0}


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    build_helper = load('a44build', REPORTS / 'a44-build-packages.py')
    package_helper = load('a44package', REPORTS / 'a44-qualify-relocation.py')
    sha, identity, inventory = build_helper.sha, build_helper.identity, package_helper.inventory
    runtime = json.loads((REPORTS / 'a44-final-package-result.json').read_text())
    assert runtime['status'] == 'passed'
    assert sha(SOURCE / 'docs/MIDI_UI_RUNBOOK.md') == EXPECTED_GUIDE
    shutil.copyfile(REPORTS / 'a44-final-package-result.json', REPORTS / 'a44-runtime-package-result.json')
    before = build_helper.source_snapshot()
    build_helper.write('a44-source-before-guide-refresh.json', before)
    runtime_source = json.loads((REPORTS / 'a44-source-after-relocation.json').read_text())
    assert before['production_sha256'] == runtime_source['production_sha256']
    guide_changes = {p: {'runtime': old, 'final': before['installed_sources_sha256'].get(p)}
        for p, old in runtime_source['installed_sources_sha256'].items()
        if old != before['installed_sources_sha256'].get(p)}
    assert set(guide_changes) == {'docs/MIDI_UI_RUNBOOK.md'}, guide_changes
    configuration_changes = {p: {'runtime': old, 'refresh': before['build_install_sha256'].get(p)}
        for p, old in runtime_source['build_install_sha256'].items()
        if old != before['build_install_sha256'].get(p)}
    assert set(configuration_changes) == {'apps/standalone/CMakeLists.txt'}, configuration_changes
    work = SOURCE.parent / 'a44-final-packages-docs'
    work.mkdir(exist_ok=False)
    record = {'schema': 'a44-final-guide-refresh-v1', 'status': 'running', 'commands': [],
              'reason': 'Root applied ten A45-reviewed current MIDI guide replacements after the A44 runtime freeze.',
              'installed_source_changes': guide_changes, 'build_configuration_changes': configuration_changes,
              'recompiled_targets': [], 'native_flows_rerun': 0, 'ctest_suites_executed': 0, 'packages': {}}

    def save():
        build_helper.write('a44-package-refresh.json', record)

    def run(name, command):
        start = time.monotonic()
        result = subprocess.run(list(map(str, command)), cwd=SOURCE, text=True, capture_output=True, timeout=120)
        path = REPORTS / f'a44-{name}.txt'
        path.write_text(result.stdout + result.stderr)
        item = {'command': list(map(str, command)), 'returncode': result.returncode,
                'elapsed_seconds': round(time.monotonic() - start, 4), 'log': path.name, 'identity': identity(path)}
        record['commands'].append(item)
        save()
        print(f'{name}: exit {result.returncode}, {item["elapsed_seconds"]} s', flush=True)
        assert result.returncode == 0, item
        return result

    try:
        for mode, enabled in [('midi-on', True), ('midi-off', False)]:
            build = SOURCE.parent / ('build-native' if enabled else 'build-native-midi-off')
            previous = json.loads((REPORTS / f'a44-{mode}-relocation.json').read_text())
            exe = build / 'apps/standalone/hammond_standalone'
            assert identity(exe) == previous['expected_payload']['bin/hammond_standalone']
            run(f'{mode}-refresh-configure', [build_helper.CMAKE, '-S', SOURCE, '-B', build])
            discovery = run(f'{mode}-release-raster-discovery', [build_helper.CTEST, '--test-dir', build,
                '-C', 'Release', '--show-only=json-v1', '--no-tests=error',
                '-R', '^(test_standalone_workspace_raster|test_standalone_scaled_view|test_standalone_preset_raster)$'])
            tests = json.loads(discovery.stdout)['tests']
            actual = {test['name']: next(p['value'] for p in test['properties'] if p['name'] == 'TIMEOUT')
                      for test in tests}
            assert actual == TIMEOUTS, actual
            inputs = {name: SOURCE / path for name, path in package_helper.METADATA.items()}
            inputs.update({'LICENSE-SDL2.txt': build_helper.SDL / 'LICENSE.txt',
                           'standalone-capabilities.json': build / 'generated/standalone-capabilities.json'})
            if enabled:
                prepared = build / 'apps/standalone/hammond_rtmidi-prepared'
                inputs.update({'LICENSE-RtMidi.txt': prepared / 'LICENSE',
                    'rtmidi-lock.json': SOURCE / 'data/dependencies/rtmidi-lock.json',
                    'rtmidi-prepared-source.json': prepared / 'prepared-source.json',
                    'rtmidi-coremidi-zero-init.patch': prepared / 'rtmidi-coremidi-zero-init.patch'})
            expected = {'bin/hammond_standalone': identity(exe), **{
                'share/hammond-b3-organ/standalone/' + name: identity(path) for name, path in inputs.items()}}
            changes = {p: {'runtime': previous['expected_payload'].get(p), 'final': item}
                       for p, item in expected.items() if previous['expected_payload'].get(p) != item}
            assert set(changes) == {GUIDE}, changes
            assert expected[GUIDE]['sha256'] == EXPECTED_GUIDE
            mode_root = work / mode
            mode_root.mkdir()
            prefix, relocated = mode_root / 'original final Ω', mode_root / 'relocated final Ω'
            run(f'{mode}-refresh-install', [build_helper.CMAKE, '--install', build, '--config', 'Release',
                '--component', 'Standalone', '--prefix', prefix])
            assert inventory(prefix) == expected
            prefix.rename(relocated)
            assert not prefix.exists() and inventory(relocated) == expected
            metadata = relocated / 'share/hammond-b3-organ/standalone'
            links = []
            for name in [n for n in package_helper.METADATA if n.endswith('.md')]:
                for target in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)', (metadata / name).read_text()):
                    if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target) or target.startswith('#'):
                        continue
                    assert (metadata / target.split('#', 1)[0]).is_file(), (name, target)
                    links.append({'source': name, 'target': target})
            assert identity(exe) == previous['expected_payload']['bin/hammond_standalone']
            record['packages'][mode] = {'relocated_prefix': str(relocated), 'payload_count': len(expected),
                'payload_bytes': sum(v['bytes'] for v in expected.values()), 'payload': expected,
                'only_payload_change': changes, 'installed_relative_links': links,
                'release_raster_timeouts_seconds': actual, 'binary_unchanged': True,
                'generated_capabilities_unchanged': True,
                'cache_identity_after_refresh': identity(build / 'CMakeCache.txt')}
        after = build_helper.source_snapshot()
        build_helper.write('a44-source-after-guide-refresh.json', after)
        for key in ['production_sha256', 'installed_sources_sha256', 'build_install_sha256']:
            assert after[key] == before[key], (key, 'changed during final refresh')
        record.update(status='passed', production_unchanged=True, source_stable_during_refresh=True,
                      source_head=after['head'], product_inventory_sha256=after['production_inventory_sha256'])
        final = dict(runtime)
        final.pop('installed_sources_unchanged')
        final['runtime_packages'] = final.pop('packages')
        final['build_install_drift_during_runtime'] = final.pop('build_install_drift')
        final.update(runtime_qualification_report='a44-runtime-package-result.json',
            final_package_report='a44-package-refresh.json',
            installed_sources_unchanged_through_runtime=True,
            installed_source_changes_after_runtime=guide_changes,
            build_install_drift_after_runtime=configuration_changes,
            final_guide_sha256=EXPECTED_GUIDE,
            final_packages={mode: {'payload_files': item['payload_count'], 'payload_bytes': item['payload_bytes'],
                'relocated_prefix': item['relocated_prefix'], 'executable': item['payload']['bin/hammond_standalone']}
                for mode, item in record['packages'].items()},
            final_refresh_native_invocations=0, final_refresh_rebuilds=0,
            release_raster_timeouts_seconds=TIMEOUTS)
        build_helper.write('a44-final-package-result.json', final)
    except Exception as error:
        record.update(status='failed', failure=f'{type(error).__name__}: {error}')
        raise
    finally:
        save()


if __name__ == '__main__':
    main()
