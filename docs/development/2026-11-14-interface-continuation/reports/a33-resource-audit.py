#!/usr/bin/env python3
"""Read-only bounded inventory; --native runs exactly three serialized smokes.

Coordinate --native with the integrator before executing. No build or cleanup.
"""
import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time

REPORTS = Path(__file__).resolve().parent
REPO = REPORTS.parents[3]
PARENT = REPO.parent
SESSION = REPORTS.parent
PIN = Path('/tmp/a33-pin/hammond_standalone')
EXPECTED = '55b0947985ee562cce3d04eae66cc4d44f805420f475dd578f00373dd2bef6cd'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command):
    return subprocess.check_output(command, cwd=REPO, text=True).strip()


def write(name, value):
    (REPORTS / name).write_text(json.dumps(value, indent=2) + '\n')


def storage():
    paths = [REPO, REPO / '.git', SESSION,
             REPO / 'examples/demos/standalone-interface-preview-v1']
    paths += [PARENT / name for name in (
        'build-native', 'build-a13-sdkfree', 'build-native-midi-off',
        'midi-checkpoint-source', 'build-midi-checkpoint', 'baseline-bin')]
    footprints = [{'path': str(path), 'allocated_bytes':
                   int(run(['du', '-s', '-B1', str(path)]).split()[0])}
                  for path in paths]
    stat = os.statvfs(PARENT)
    indexed = [REPO / p for p in run(['git', 'ls-files', '-z']).split('\0') if p]
    indexed = [p for p in indexed if p.is_file()]
    large = sorted(indexed, key=lambda p: p.stat().st_size, reverse=True)[:12]
    compiled = []
    cache_paths = []
    for path in indexed:
        relative = path.relative_to(REPO)
        with path.open('rb') as stream:
            magic = stream.read(4)
        if magic.startswith((b'\x7fELF', b'MZ')) or path.suffix.lower() in (
                '.o', '.obj', '.a', '.so', '.dll', '.dylib', '.exe', '.pyc', '.pdb'):
            compiled.append(str(relative))
        if any(part in ('CMakeFiles', '__pycache__', 'node_modules', '.cache') or
               part.startswith('build-') for part in relative.parts[:-1]):
            cache_paths.append(str(relative))
    inspected = [PARENT / name for name in (
        'build-native', 'build-a13-sdkfree', 'build-native-midi-off',
        'a17-renderer', 'a20-renderer', 'a25-native-raster',
        'a21-workspace-first-evidence', 'a29-midi-off-relocation-final')]
    bmps = [{'path': str(p), 'bytes': p.stat().st_size}
            for root in inspected for p in root.rglob('*.bmp') if p.is_file()]
    source_paths = ['apps/standalone/' + name for name in (
        'main.cpp', 'UiModel.h', 'UiModel.cpp', 'InspectionModel.h',
        'InspectionModel.cpp', 'Drawing.h', 'Drawing.cpp', 'FontData.h',
        'ScriptedInput.h', 'MidiReplay.h')]
    frozen_path = REPORTS / 'root-ui-coherent-source-before.json'
    frozen = {f['path']: f['sha256'] for f in json.loads(frozen_path.read_text())['files']}
    source = [{'path': p, 'sha256': sha(REPO / p),
               'matches_root_frozen_source': sha(REPO / p) == frozen.get(p)}
              for p in source_paths]
    caches = {}
    for name in ('build-native', 'build-a13-sdkfree', 'build-native-midi-off',
                 'build-midi-checkpoint'):
        cache = PARENT / name / 'CMakeCache.txt'
        caches[name] = [line for line in cache.read_text().splitlines()
                        if line.startswith(('CMAKE_HOME_DIRECTORY:',
                           'CMAKE_BUILD_TYPE:', 'SDL2_SOURCE_DIR:',
                           'HAMMOND_RTMIDI_ROOT:', 'HAMMOND_VST3_SDK_ROOT:'))]
    deps = [Path('/workspace/scratch/7ffc2842608b/SDL2'),
            Path('/workspace/scratch/cd4bd06ce68f/rtmidi')]
    manifest = json.loads((SESSION / 'assignments.json').read_text())
    candidates = []
    for path, proof in ((PIN, 'Pinned SHA and three diagnostics in a33-runtime.json; retain until review.'),
            (PARENT / 'a22-interface-contact-sheet.png',
             'Contact sheet is reproducible from retained eight-image gallery and manifest.')):
        if path.is_file():
            candidates.append({'path': str(path), 'bytes': path.stat().st_size,
                               'sha256': sha(path), 'retained_proof': proof,
                               'disposition': 'Candidate only; integrator approval required; not deleted.'})
    result = {'observed_at_utc': datetime.now(timezone.utc).isoformat(),
        'head': run(['git', 'rev-parse', 'HEAD']),
        'origin_main_local_ref': run(['git', 'rev-parse', 'origin/main']),
        'filesystem_available_bytes': stat.f_bavail * stat.f_frsize,
        'disk_command': ['du', '-s', '-B1', 'EACH_EXPLICIT_PATH_SEPARATELY'],
        'footprints': footprints, 'indexed_file_count': len(indexed),
        'largest_indexed_files': [{'path': str(p.relative_to(REPO)),
                                   'bytes': p.stat().st_size} for p in large],
        'indexed_compiled_artifacts': compiled, 'indexed_cache_paths': cache_paths,
        'inspected_bmp_roots': list(map(str, inspected)), 'remaining_bmps': bmps,
        'cleanup_candidates': candidates, 'deleted_by_a33': [],
        'frozen_source_manifest_sha256': sha(frozen_path), 'source': source,
        'build_source_reuse': caches,
        'shared_dependencies': [{'path': str(p), 'head': run(['git', '-C', str(p), 'rev-parse', 'HEAD'])}
                                for p in deps],
        'resumability': {'checkpoint_bytes': (SESSION / 'CHECKPOINT.md').stat().st_size,
            'manifest_bytes': (SESSION / 'assignments.json').stat().st_size,
            'manifest_sha256': sha(SESSION / 'assignments.json'),
            'actual_manifest_rows': len(manifest['assignments']),
            'states': dict(Counter(a['status'] for a in manifest['assignments'])),
            'checkpoint_contains_head': run(['git', 'rev-parse', 'HEAD']) in
                                          (SESSION / 'CHECKPOINT.md').read_text(),
            'checkpoint_has_next_actions': '## Next integration actions' in
                                           (SESSION / 'CHECKPOINT.md').read_text(),
            'a33_present': any(a['number'] == 33 for a in manifest['assignments'])},
        'limits': ['Snapshot of active work; sizes may change.',
                   'No directory scan of another session or external SDK.',
                   'Index inspection includes staged overlay; not a published-commit claim.']}
    write('a33-storage.json', result)
    print(json.dumps({k: result[k] for k in ('filesystem_available_bytes',
          'indexed_compiled_artifacts', 'indexed_cache_paths', 'resumability')}))


def native():
    assert sha(PIN) == EXPECTED, 'Pinned binary identity changed'
    records = []
    for case, workspace, flat in (('play', 'play', False),
                                  ('service', 'service', False),
                                  ('flat', 'play', True)):
        directory = PIN.parent / case
        directory.mkdir(exist_ok=True)
        diagnostics = REPORTS / f'a33-{case}-diagnostics.json'
        time_path = REPORTS / f'a33-{case}-time.json'
        command = [str(PIN), '--width', '1672', '--height', '941',
                   '--workspace', workspace, '--smoke-ms', '600',
                   '--state', str(directory / 'controls.b3controls'),
                   '--diagnostics', str(diagnostics)] + (['--flat'] if flat else [])
        assert not diagnostics.exists(), 'Each case runs only once'
        environment = dict(os.environ, SDL_AUDIODRIVER='dummy', SDL_VIDEODRIVER='dummy')
        started = time.monotonic()
        process = subprocess.Popen(command, cwd=directory, env=environment,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        while True:
            pid, status, usage = os.wait4(process.pid, os.WNOHANG)
            if pid:
                break
            if time.monotonic() - started > 8:
                process.kill()
                pid, status, usage = os.wait4(process.pid, 0)
                break
            time.sleep(0.01)
        process.returncode = os.waitstatus_to_exitcode(status)
        elapsed = time.monotonic() - started
        stdout, stderr = process.communicate(timeout=1)
        timing = {'peak_rss_kib': usage.ru_maxrss, 'wall_seconds': elapsed,
                  'user_seconds': usage.ru_utime, 'system_seconds': usage.ru_stime,
                  'exit_code': process.returncode}
        time_path.write_text(json.dumps(timing, indent=2) + '\n')
        data = json.loads(diagnostics.read_text())
        record = {'case': case, 'command': command, 'working_directory': str(directory),
            'exit_code': process.returncode, 'time': timing, 'runtime': data['runtime'],
            'smoke': data['smoke'], 'audio': data['audio'], 'errors': data['errors'],
            'presentation_observations': len(data['presentation']['observations']),
            'presentation_truncated': data['presentation']['observations_truncated'],
            'diagnostics_sha256': sha(diagnostics),
            'stdout': stdout, 'stderr': stderr}
        records.append(record)
        assert process.returncode == 0 and data['smoke']['passed'], record
    result = {'observed_at_utc': datetime.now(timezone.utc).isoformat(),
        'executable': str(PIN), 'executable_sha256_before_and_after': sha(PIN),
        'environment': {'SDL_AUDIODRIVER': 'dummy', 'SDL_VIDEODRIVER': 'dummy'},
        'measurement': 'Linux os.wait4 per-child ru_maxrss in KiB, ru_utime/ru_stime seconds; monotonic wall includes up to 10 ms polling quantization.',
        'records': records,
        'limits': ['One process per case, serial; observations are not benchmarks or leak tests.',
                   'No capture was requested; screenshot surface bound is source inspection only.',
                   'No physical callback deadline, frame-rate, device, or 8192-square qualification.']}
    assert result['executable_sha256_before_and_after'] == EXPECTED
    write('a33-runtime.json', result)
    print(json.dumps([{'case': r['case'], **r['time']} for r in records]))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native', action='store_true')
    args = parser.parse_args()
    native() if args.native else storage()
