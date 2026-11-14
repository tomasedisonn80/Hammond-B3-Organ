#!/usr/bin/env python3
"""A46's bounded observed build/capture; refuses existing gallery or evidence."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys
import time

ROOT = Path('/workspace/scratch/1bb6ee17ad7e')
REPO = ROOT / 'Hammond-B3-Organ'
BUILD = ROOT / 'build-desktop'
EXE = BUILD / 'apps/standalone/hammond_standalone'
CMAKE = ROOT / 'build-tools/cmake/data/bin/cmake'
NINJA = ROOT / 'build-tools/bin/ninja'
TOOL = REPO / 'tools/capture_standalone_interface.py'
REPORTS = REPO / 'docs/development/2026-11-14-reference-refinement/reports'
GALLERY = REPO / 'examples/demos/standalone-interface-preview-v4'
HEAD = '0881d1f4c5a26ce9c75dda7a3adde46382e5ab6b'
TREE = 'f8144b771cda1264a8788f8297f5bfec999f4a08'
PAINTER = 'f323c8c2f5529b03c25deccb74f482d8b6312487492a45d14b94ef0e24cfbb6a'
EXPECTED_INITIAL_EXE = '01fe78a55b7a9bc72228dafe175f5a8eb48481c063f217606474d4dff682320f'


def stamp():
    return datetime.now(timezone.utc).isoformat()


def identity(path):
    data = path.read_bytes()
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def write_new(path, value):
    with path.open('x', encoding='utf-8') as output:
        json.dump(value, output, indent=2, sort_keys=True, allow_nan=False)
        output.write('\n')


def read_command(command):
    return subprocess.check_output([str(item) for item in command], cwd=REPO, text=True)


def inventory(paths, root):
    return {str(path.relative_to(root)): identity(path) for path in sorted(set(paths))}


def cmake_sources():
    return [REPO / 'CMakeLists.txt', REPO / 'apps/standalone/CMakeLists.txt',
            *(path for path in (REPO / 'cmake').rglob('*') if path.is_file())]


def qualified_sources(producer):
    paths = producer['production_paths'](REPO) + cmake_sources()
    for line in read_command([NINJA, '-C', BUILD, '-t', 'inputs', 'hammond_standalone']).splitlines():
        path = Path(line)
        path = (path if path.is_absolute() else BUILD / path).resolve()
        if path.is_file() and path.is_relative_to(REPO):
            paths.append(path)
    return inventory(paths, REPO)


def assert_committed(files):
    for name, expected in files.items():
        data = subprocess.check_output(['git', '-C', str(REPO), 'show', f'{HEAD}:{name}'])
        assert {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()} == expected, name


def old_galleries():
    return {version: inventory([path for path in (REPO / 'examples/demos' /
            f'standalone-interface-preview-{version}').rglob('*') if path.is_file()], REPO)
            for version in ('v1', 'v2', 'v3')}


def snapshot(producer):
    extra = ['CMakeCache.txt', 'build.ninja', 'compile_commands.json',
             'generated/standalone-capabilities.json', '_sdl2/include-config-release/SDL2/SDL_config.h',
             'apps/standalone/hammond_rtmidi-prepared/prepared-source.json',
             'apps/standalone/hammond_rtmidi-prepared/RtMidi.cpp',
             'apps/standalone/hammond_rtmidi-prepared/RtMidi.h',
             'apps/standalone/hammond_rtmidi-prepared/rtmidi-coremidi-zero-init.patch']
    fonts = [REPO / 'apps/standalone/FontData.h',
             *(path for path in (REPO / 'assets/standalone/fonts').rglob('*') if path.is_file())]
    return {'production': inventory(producer['production_paths'](REPO), REPO),
            'cmake_sources': inventory(cmake_sources(), REPO),
            'font_sources_and_atlas': inventory(fonts, REPO),
            'selected_build_inputs': inventory(producer['build_paths'](BUILD), BUILD),
            'extra_build_inputs': inventory([BUILD / name for name in extra], BUILD),
            'selected_configuration': producer['configuration'](BUILD),
            'capture_producer': identity(TOOL), 'executable': identity(EXE)}


def write_snapshot(label, value):
    path = REPORTS / f'A46-{label}.json'
    write_new(path, {'schema': 'a46-native-input-snapshot-v1', 'observed_at_utc': stamp(),
                    'published_commit': HEAD, 'published_tree': TREE, 'inputs': value,
                    'git_status_short': read_command(['git', 'status', '--short']),
                    'whole_worktree_clean_claimed': False})
    return {'path': str(path.relative_to(REPO)), **identity(path)}


def run_logged(command, name, timeout):
    path = REPORTS / name
    started, tick = stamp(), time.monotonic()
    with path.open('xb') as output:
        result = subprocess.run([str(item) for item in command], cwd=REPO, stdout=output,
                                stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, timeout=timeout)
    record = {'command': [str(item) for item in command], 'cwd': str(REPO),
              'started_at_utc': started, 'finished_at_utc': stamp(),
              'elapsed_seconds': time.monotonic() - tick, 'exit_code': result.returncode,
              'log': {'path': str(path.relative_to(REPO)), **identity(path)}}
    assert result.returncode == 0, record
    return record


def main():
    assert not GALLERY.exists(), 'existing gallery refused'
    assert read_command(['git', 'rev-parse', 'HEAD', 'HEAD^{tree}', 'refs/remotes/origin/main']).splitlines() == [HEAD, TREE, HEAD]
    producer = runpy.run_path(str(TOOL))
    source_before = qualified_sources(producer)
    assert_committed(source_before)
    assert_committed({'tools/capture_standalone_interface.py': identity(TOOL)})
    assert source_before['apps/standalone/InstrumentView.cpp']['sha256'] == PAINTER
    old_before = old_galleries()
    for value in old_before.values():
        assert_committed(value)
    before = snapshot(producer)
    assert before['executable']['sha256'] == EXPECTED_INITIAL_EXE
    snapshots = {'before_build': write_snapshot('before-build', before)}
    print(json.dumps({'phase': 'qualified', 'source_files': len(source_before),
                      'source_inventory_sha256': digest(source_before), 'published_commit': HEAD}), flush=True)
    build_run = run_logged([CMAKE, '--build', BUILD, '--parallel', '3', '--target', 'hammond_standalone'],
                           'A46-build.log', 240)
    after_build = snapshot(producer)
    source_after_build = qualified_sources(producer)
    snapshots['after_build'] = write_snapshot('after-build', after_build)
    assert source_before == source_after_build, 'qualified source changed through target build'
    for name in ('production', 'cmake_sources', 'font_sources_and_atlas', 'capture_producer'):
        assert before[name] == after_build[name], name
    binary = after_build['executable']
    qualification = {'schema': 'a46-native-source-qualification-v1', 'assignment': 'A46',
        'published_commit': HEAD, 'published_tree': TREE,
        'binary_sha256': binary['sha256'], 'binary_bytes': binary['bytes'],
        'source_sha256': {name: value['sha256'] for name, value in source_before.items()},
        'source_inventory_sha256': digest(source_before), 'source_file_count': len(source_before),
        'source_inventory_definition': 'Observed production_paths plus repository files in the native Ninja input closure and repository CMake configuration files; a conservative product/build-source set.',
        'all_listed_sources_equal_published_blobs': True, 'source_unchanged_through_target_build': True,
        'observed_target_build': build_run,
        'compiler': read_command(['/usr/bin/c++', '--version']).splitlines()[0],
        'cmake': read_command([CMAKE, '--version']).splitlines()[0],
        'boundary': 'Author-observed incremental Release target build in the existing MIDI-enabled X11-capable build tree. Named input and executable identities were directly observed. This is not an independent, hermetic, clean-rebuild or signed source-to-binary attestation; concurrent documentation means no clean whole-worktree claim.'}
    qualified_path = ROOT / 'a46-source-qualification.json'
    write_new(qualified_path, qualification)
    print(json.dumps({'phase': 'built', 'binary': binary, 'elapsed_seconds': build_run['elapsed_seconds']}), flush=True)
    capture_run = run_logged([sys.executable, '-B', TOOL, '--exe', EXE, '--source-root', REPO,
        '--build-root', BUILD, '--source-qualification', qualified_path,
        '--expected-exe-sha256', binary['sha256'], '--dummy-sdl', '--output', GALLERY], 'A46-capture.log', 130)
    after_capture = snapshot(producer)
    snapshots['after_capture'] = write_snapshot('after-capture', after_capture)
    assert after_capture == after_build, 'recorded inputs changed through capture'
    source_after_capture = qualified_sources(producer)
    assert source_after_capture == source_before
    assert_committed(source_after_capture)
    assert old_before == old_galleries(), 'historical gallery changed'
    provenance = producer['read_json'](GALLERY / 'provenance.json')
    manifest = producer['read_json'](GALLERY / 'manifest.json')
    assert provenance['status'] == manifest['status'] == 'passed'
    assert provenance['all_recorded_inputs_unchanged'] is True
    assert provenance['source']['git_before'] == provenance['source']['git_after'] == {'head': HEAD, 'committed_tree': TREE}
    assert provenance['source']['changed_paths'] == provenance['build']['changed_paths'] == []
    for name, expected in manifest['files'].items():
        assert identity(GALLERY / name) == expected, name
    assert manifest['total_bytes_excluding_manifest'] == sum(value['bytes'] for value in manifest['files'].values())
    assert not list(GALLERY.rglob('*.bmp'))
    from PIL import Image
    checks = []
    for case in provenance['cases']:
        diagnostics = producer['read_json'](GALLERY / case['diagnostics']['path'])
        event_count = producer['replay'](case['workspace'], case['presentation'])[1]
        validated = producer['validate'](diagnostics, case['width'], case['height'], case['workspace'], case['presentation'], event_count)
        assert validated == case['validation']
        assert diagnostics['midi']['backend'] == 'ALSA' and diagnostics['midi']['backend_available'] is True
        assert diagnostics['runtime']['sdl_version'] == '2.32.10'
        im = case['image']
        with Image.open(GALLERY / im['path']) as decoded:
            decoded.load()
            assert decoded.format == 'PNG' and decoded.mode == im['decoded_mode']
            assert decoded.size == (case['width'], case['height'])
            assert hashlib.sha256(decoded.tobytes()).hexdigest() == im['decoded_sha256']
        assert identity(GALLERY / im['path']) == im['png']
        painted = diagnostics['presentation']['screenshot']
        checks.append({'name': case['name'], 'status': 'passed', 'dimensions': [case['width'], case['height']],
            'png': im['png'], 'decoded_sha256': im['decoded_sha256'],
            'held_targets': painted['held_targets'], 'pointer_capture': painted['pointer_capture'],
            'callbacks': diagnostics['audio']['callback_count'], 'rendered_frames': diagnostics['audio']['rendered_frames'],
            'ui_events': event_count, 'live_edit': validated['live_edit'],
            'held_manual_notes': validated['held_manual_notes'], 'held_pedal_ids': validated['held_pedal_ids'],
            'runtime_backend': {name: diagnostics['runtime'][name] for name in ('video_driver', 'renderer', 'sdl_version')},
            'midi_backend': diagnostics['midi']['backend'], 'midi_source': diagnostics['midi']['source']})
    assert len(checks) == 8
    result = {'schema': 'a46-native-gallery-v1', 'assignment': 'A46', 'agent': '/root/w08_a46_final_native_gallery',
        'status': 'captured_pending_visual_review', 'finished_capture_at_utc': stamp(),
        'published_commit': HEAD, 'published_tree': TREE, 'painter_sha256': PAINTER,
        'gallery': str(GALLERY.relative_to(REPO)), 'snapshots': snapshots,
        'source_qualification': {'file_count': len(source_before), 'sha256': identity(qualified_path)['sha256'],
            'inventory_sha256_before_build': digest(source_before),
            'inventory_sha256_after_build': digest(source_after_build),
            'inventory_sha256_after_capture': digest(source_after_capture), 'all_files_match_published_blobs': True,
            'source_files_definition': qualification['source_inventory_definition']},
        'observed_inventory_digests': {name: {'before_build': digest(before[name]),
            'after_build': digest(after_build[name]), 'after_capture': digest(after_capture[name])}
            for name in ('production', 'cmake_sources', 'font_sources_and_atlas', 'selected_build_inputs', 'extra_build_inputs')},
        'binary_before_build': before['executable'], 'binary_after_build': binary,
        'binary_after_capture': after_capture['executable'], 'capture_producer': before['capture_producer'],
        'font_sources_and_atlas_before_and_after': before['font_sources_and_atlas'],
        'cmake_sources_before_and_after': before['cmake_sources'],
        'selected_configuration': after_capture['selected_configuration'],
        'build': build_run, 'capture': capture_run,
        'all_capture_payload_hashes_recomputed': len(manifest['files']), 'decoded_pngs_recomputed': 8,
        'strict_endpoint_validation_repeated': True, 'cases': checks,
        'gallery_manifest': identity(GALLERY / 'manifest.json'), 'gallery_provenance': identity(GALLERY / 'provenance.json'),
        'png_bytes_total': sum(case['png']['bytes'] for case in checks),
        'gallery_bytes_before_readme': sum(path.stat().st_size for path in GALLERY.rglob('*') if path.is_file()),
        'historical_galleries_unchanged': {version: {'files': len(value), 'inventory_sha256': digest(value),
            'all_files_match_published_blobs': True} for version, value in old_before.items()},
        'visual_review': {'status': 'pending'}, 'whole_worktree_clean_claimed': False,
        'boundaries': ['Actual native dummy-audio/dummy-video/software-renderer process screenshots.',
            'Distinct from actual OS-window input, physical audio/MIDI devices, display/DPI, accessibility and deadline qualification.',
            'Settled acknowledged endpoints; A18 retains the distinct genuine pending-state rendering evidence.',
            'No literal reference equality, R4 audio integration, measured instrument or physical calibration claim.',
            'No compiler/dependency-complete, hermetic or clean-rebuild source-to-binary attestation.',
            'No A46 GUI use, full CTest, commit, push, image generation, compositing or pixel editing.']}
    write_new(REPORTS / 'A46-final-native-gallery.json', result)
    print(json.dumps({'phase': 'captured', 'captures': len(checks), 'binary': binary,
                      'provenance': result['gallery_provenance'], 'manifest': result['gallery_manifest'],
                      'png_bytes_total': result['png_bytes_total']}), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        write_new(REPORTS / 'A46-orchestration-failure.json', {'observed_at_utc': stamp(),
                  'exception_type': type(error).__name__, 'message': str(error), 'status': 'failed'})
        raise
