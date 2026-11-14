#!/usr/bin/env python3
"""A49 one-shot verification; all run artifacts stay outside the frozen checkout."""
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time

ROOT = Path('/workspace/scratch/1bb6ee17ad7e/Hammond-B3-Organ')
BUILD = ROOT.parent / 'build-native'
OUT = Path(__file__).resolve().parent
BASE = '0881d1f4c5a26ce9c75dda7a3adde46382e5ab6b'
CMAKE = '../build-tools/cmake/data/bin/cmake'
CTEST = '../build-tools/cmake/data/bin/ctest'
NINJA = '../build-tools/bin/ninja'
LOG_CAP = 8 * 1024 * 1024
SOURCE_DIRS = {'apps', 'assets', 'cmake', 'data', 'include', 'plugins', 'src', 'tests', 'tools', '.github'}
SOURCE_ROOT_FILES = {'CMakeLists.txt', 'CMakePresets.json', 'Makefile', '.gitattributes', '.gitignore'}
EXCLUDES = {'.git', '__pycache__'}


def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def write(name, value):
    (OUT / name).write_text(json.dumps(value, sort_keys=True, indent=2) + '\n', encoding='utf-8')


def run_read(command, cwd=ROOT):
    p = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return {'command': command, 'exit': p.returncode,
            'stdout': p.stdout.decode('utf-8', 'replace'), 'stderr': p.stderr.decode('utf-8', 'replace')}


def file_record(path):
    info = path.lstat()
    if path.is_symlink():
        return {'kind': 'symlink', 'target': os.readlink(path)}
    digest = hashlib.sha256()
    blob = hashlib.sha1(f'blob {info.st_size}\0'.encode())
    with path.open('rb') as stream:
        while block := stream.read(1024 * 1024):
            digest.update(block)
            blob.update(block)
    after = path.stat()
    if (info.st_size, info.st_mtime_ns, info.st_ino) != (after.st_size, after.st_mtime_ns, after.st_ino):
        raise RuntimeError(f'Input changed while hashing: {path}')
    return {'kind': 'file', 'bytes': info.st_size, 'sha256': digest.hexdigest(), 'git_blob_sha1': blob.hexdigest()}


def inventory(root):
    result = {}
    for directory, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in EXCLUDES)
        for name in sorted(files):
            if name.endswith('.pyc'):
                continue
            path = Path(directory) / name
            result[path.relative_to(root).as_posix()] = file_record(path)
    return result


def aggregate(records):
    return hashlib.sha256(json.dumps(records, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def build_inputs():
    result = {}
    for path in sorted(BUILD.rglob('*')):
        if not path.is_file() or path.is_symlink():
            continue
        rel = path.relative_to(BUILD).as_posix()
        if rel.startswith('Testing/') or path.name.startswith('install_manifest'):
            continue
        selected = (path.name in {'CMakeCache.txt', 'build.ninja', 'rules.ninja', 'VerifyGlobs.cmake',
                                 'CTestTestfile.cmake', 'cmake_install.cmake'}
                    or rel.startswith('generated/') or path.suffix in {'.b3p', '.a', '.so'})
        if not selected and os.access(path, os.X_OK):
            with path.open('rb') as stream:
                selected = stream.read(4) == b'\x7fELF'
        if selected:
            result[rel] = file_record(path)
    return result


def toolchain():
    commands = [[CMAKE, '--version'], [CTEST, '--version'], [NINJA, '--version'],
                ['/usr/bin/c++', '--version'], ['/usr/bin/cc', '--version'], [sys.executable, '--version'],
                ['/usr/bin/ld', '--version'], ['/usr/bin/ar', '--version']]
    result = {'platform': platform.platform(), 'machine': platform.machine(), 'tools': []}
    for command in commands:
        resolved = (ROOT / command[0]).resolve() if '/' in command[0] else Path(shutil.which(command[0])).resolve()
        result['tools'].append({**run_read(command), 'resolved_path': str(resolved), **file_record(resolved)})
    cache = {}
    for line in (BUILD / 'CMakeCache.txt').read_text().splitlines():
        if not line or line.startswith(('#', '//')) or ':' not in line or '=' not in line:
            continue
        name, value = line.split('=', 1)
        key = name.split(':', 1)[0]
        if key.startswith(('CMAKE_', 'HAMMOND_', 'SDL2_')) or key in {'BUILD_TESTING', '_Python3_EXECUTABLE'}:
            cache[key] = value
    result['selected_cache'] = cache
    result['environment'] = {k: os.environ[k] for k in ['CC', 'CXX', 'CFLAGS', 'CXXFLAGS', 'LDFLAGS',
                            'CMAKE_BUILD_PARALLEL_LEVEL', 'CTEST_PARALLEL_LEVEL', 'SDL_AUDIODRIVER',
                            'SDL_VIDEODRIVER', 'SDL_RENDER_DRIVER', 'ASAN_OPTIONS', 'UBSAN_OPTIONS',
                            'LSAN_OPTIONS', 'PYTHONDONTWRITEBYTECODE'] if k in os.environ}
    return result


def snapshot(label):
    started = now()
    repo = inventory(ROOT)
    base_tree = subprocess.check_output(['git', 'ls-tree', '-r', '-z', BASE], cwd=ROOT)
    target = {}
    for row in base_tree.split(b'\0'):
        if row:
            header, name = row.split(b'\t', 1)
            target[name.decode()] = header.decode().split()[2]
    source = {name: record for name, record in repo.items()
              if name.split('/')[0] in SOURCE_DIRS or name in SOURCE_ROOT_FILES}
    mismatch = [name for name, record in source.items() if target.get(name) != record.get('git_blob_sha1')]
    missing = [name for name in target if (name.split('/')[0] in SOURCE_DIRS or name in SOURCE_ROOT_FILES) and name not in source]
    docs = {name: record for name, record in repo.items() if name.lower().endswith('.md')}
    dependency_root = ROOT.parent / 'SDL2'
    dependency = inventory(dependency_root)
    result = {
        'schema_version': 1, 'started_utc': started, 'completed_utc': now(), 'working_directory': str(ROOT),
        'target_published_commit': BASE, 'target_tree': run_read(['git', 'rev-parse', BASE + '^{tree}'])['stdout'].strip(),
        'git': {key: run_read(args) for key, args in {
            'head': ['git', 'rev-parse', 'HEAD'], 'head_tree': ['git', 'rev-parse', 'HEAD^{tree}'],
            'observed_origin_main': ['git', 'rev-parse', 'refs/remotes/origin/main'],
            'status': ['git', 'status', '--short'], 'index': ['git', 'ls-files', '--stage']}.items()},
        'inventory_exclusions': ['.git directories', '__pycache__ directories', '*.pyc'],
        'repository_files': repo, 'repository_aggregate_sha256': aggregate(repo),
        'published_product_test_input_count': len(source), 'product_test_inputs': sorted(source),
        'product_test_aggregate_sha256': aggregate(source), 'product_test_target_mismatches': mismatch,
        'missing_product_test_inputs': missing, 'markdown_count': len(docs), 'markdown_aggregate_sha256': aggregate(docs),
        'toolchain': toolchain(), 'build_execution_inputs': build_inputs(),
        'dependency': {'root': str(dependency_root), 'git_head': run_read(['git', 'rev-parse', 'HEAD'], dependency_root),
                       'git_status': run_read(['git', 'status', '--short'], dependency_root),
                       'files': dependency, 'aggregate_sha256': aggregate(dependency)},
        'disk_bytes': dict(zip(('total', 'used', 'free'), shutil.disk_usage(ROOT))),
    }
    write(f'A49-inputs-{label}.json', result)
    print(json.dumps({'event': 'snapshot', 'label': label, 'utc': result['completed_utc'],
                      'repository_files': len(repo), 'markdown_files': len(docs), 'product_test_inputs': len(source),
                      'source_mismatches': mismatch, 'missing_source_inputs': missing,
                      'repository_sha256': result['repository_aggregate_sha256']}), flush=True)
    return result


def execute(label, command):
    started = now()
    tick = time.monotonic()
    digest = hashlib.sha256()
    total = stored = 0
    tail = b''
    path = OUT / f'A49-{label}.log'
    print(json.dumps({'event': 'start', 'label': label, 'utc': started, 'command': command}), flush=True)
    with path.open('wb') as log:
        process = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while block := process.stdout.read(65536):
            total += len(block)
            digest.update(block)
            tail = (tail + block)[-6000:]
            keep = block[:max(0, LOG_CAP - stored)]
            log.write(keep)
            stored += len(keep)
        code = process.wait()
    result = {'command': command, 'cwd': str(ROOT), 'started_utc': started, 'completed_utc': now(),
              'seconds': time.monotonic() - tick, 'exit': code, 'stream': 'unmodified merged stdout and stderr',
              'log': path.name, 'stream_bytes': total, 'stored_bytes': stored, 'cap_bytes': LOG_CAP,
              'truncated': total != stored, 'stream_sha256': digest.hexdigest(), 'log_sha256': file_record(path)['sha256']}
    write(f'A49-{label}-execution.json', result)
    print(json.dumps({'event': 'finish', **result, 'tail': tail.decode('utf-8', 'replace')}), flush=True)
    return result


def changes(before, after):
    return [{'path': path, 'before': before.get(path), 'after': after.get(path)}
            for path in sorted(before.keys() | after.keys()) if before.get(path) != after.get(path)]


def main():
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    before = snapshot('before')
    if before['product_test_target_mismatches'] or before['missing_product_test_inputs']:
        raise RuntimeError('Published product/test inputs do not match; build not launched')
    build = execute('build', [CMAKE, '--build', '../build-native', '--parallel', '3'])
    after_build = snapshot('after-build')
    outcome = {'schema_version': 1, 'worker': '/root/w09_a49_coherent_final_build',
               'target_published_commit': BASE, 'build': build, 'full_suite_executions': 0}
    if not build['exit']:
        discovery = execute('ctest-discovery', [CTEST, '--test-dir', '../build-native', '-C', 'Release', '--show-only=json-v1', '--no-tests=error'])
        outcome['discovery'] = discovery
        if discovery['exit'] or discovery['truncated']:
            raise RuntimeError('Discovery failed; full suite not launched')
        discovered = json.loads((OUT / discovery['log']).read_text())
        tests = discovered['tests']
        outcome['discovered_count'] = len(tests)
        outcome['discovered_names'] = [test['name'] for test in tests]
        if not tests:
            raise RuntimeError('No registered tests; full suite not launched')
        print(json.dumps({'event': 'discovery', 'registered_count': len(tests)}), flush=True)
        original = execute('ctest-original', [CTEST, '--test-dir', '../build-native', '-C', 'Release', '--output-on-failure', '--no-tests=error', '--parallel', '3'])
        outcome['original_ctest'] = original
        outcome['full_suite_executions'] = 1
        for name in ['LastTest.log', 'LastTestsFailed.log', 'CTestCostData.txt']:
            source = BUILD / 'Testing/Temporary' / name
            if source.is_file():
                size = source.stat().st_size
                if size > LOG_CAP:
                    outcome.setdefault('uncopied_test_artifacts', []).append({'name': name, 'reason': 'exceeds retained file bound', **file_record(source)})
                else:
                    destination = OUT / ('A49-' + name)
                    shutil.copyfile(source, destination)
                    outcome.setdefault('test_artifacts', []).append({'name': destination.name, **file_record(destination)})
        text = (OUT / original['log']).read_text(errors='replace')
        match = re.search(r'(\d+)% tests passed, (\d+) tests failed out of (\d+)', text)
        if match:
            outcome['result_counts'] = {'passed': int(match[3]) - int(match[2]), 'failed': int(match[2]), 'total': int(match[3]), 'percent': int(match[1])}
        seconds = re.search(r'Total Test time \(real\) =\s*([0-9.]+) sec', text)
        if seconds:
            outcome['ctest_reported_seconds'] = float(seconds[1])
    after = snapshot('after-test')
    outcome['repository_changes'] = changes(before['repository_files'], after['repository_files'])
    outcome['dependency_changes'] = changes(before['dependency']['files'], after['dependency']['files'])
    outcome['build_changes_after_build'] = changes(before['build_execution_inputs'], after_build['build_execution_inputs'])
    outcome['build_changes_during_tests'] = changes(after_build['build_execution_inputs'], after['build_execution_inputs'])
    outcome['toolchain_unchanged'] = before['toolchain']['tools'] == after['toolchain']['tools']
    outcome['snapshots'] = {label: file_record(OUT / f'A49-inputs-{label}.json') for label in ['before', 'after-build', 'after-test']}
    outcome['next_action'] = 'Integrator review; preserve original result and coordinate any repair before targeted recheck.'
    write('A49-coherent-final-build.json', outcome)
    print(json.dumps({'event': 'finished', 'build_exit': build['exit'], 'ctest_exit': outcome.get('original_ctest', {}).get('exit'),
                      'counts': outcome.get('result_counts'), 'seconds': outcome.get('ctest_reported_seconds'),
                      'repository_changed_paths': [x['path'] for x in outcome['repository_changes']],
                      'dependency_changed_paths': [x['path'] for x in outcome['dependency_changes']],
                      'build_changed_during_tests': [x['path'] for x in outcome['build_changes_during_tests']]}), flush=True)


if __name__ == '__main__':
    main()
