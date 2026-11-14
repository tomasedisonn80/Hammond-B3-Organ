#!/usr/bin/env python3
"""A59 incoming487064 integration verification; scratch-only until source snapshots finish."""
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
BASE = '487064d2400b9f39d0ee66ed136a09c9e372379e'
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
    write(f'integration487064-inputs-{label}.json', result)
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
    path = OUT / f'integration487064-{label}.log'
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
    write(f'integration487064-{label}-execution.json', result)
    print(json.dumps({'event': 'finish', **result, 'tail': tail.decode('utf-8', 'replace')}), flush=True)
    return result


def changes(before, after):
    return [{'path': path, 'before': before.get(path), 'after': after.get(path)}
            for path in sorted(before.keys() | after.keys()) if before.get(path) != after.get(path)]



def build_phase():
    os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
    os.environ['GIT_OPTIONAL_LOCKS'] = '0'
    before = snapshot('before-build')
    allowed = {'.gitattributes', '.github/workflows/ci.yml'}
    unexpected = set(before['product_test_target_mismatches']) - allowed
    if unexpected or before['missing_product_test_inputs']:
        raise RuntimeError(f'Unexpected source mismatch before build: {sorted(unexpected)}; missing={before["missing_product_test_inputs"]}')
    result = execute('build', [CMAKE, '--build', '../build-native', '--parallel', '3'])
    after = snapshot('after-build')
    summary = {'schema_version': 1, 'worker': '/root/w10_a59_publication_preflight',
               'follow_up_not_new_assignment': True, 'incoming_source': BASE, 'build': result,
               'allowed_closing_control_deltas': sorted(allowed),
               'source_changes_during_build': [r for r in changes(before['repository_files'], after['repository_files']) if r['path'].split('/')[0] in SOURCE_DIRS or r['path'] in SOURCE_ROOT_FILES],
               'repository_changes_during_build': changes(before['repository_files'], after['repository_files']),
               'dependency_changes_during_build': changes(before['dependency']['files'], after['dependency']['files']),
               'build_execution_input_changes': changes(before['build_execution_inputs'], after['build_execution_inputs']),
               'ctest_execution': 'Not launched: waiting for root whole-repository freeze.',
               'source_boundary': 'Incoming487064 product/test/assets/data/CMake bytes plus explicitly recorded root closing workflow/attributes; local HEAD/index are not this frozen worktree identity.'}
    write('integration487064-build-summary.json', summary)
    print(json.dumps({'event': 'build_stage_complete', 'utc': now(), 'exit': result['exit'], 'seconds': result['seconds'], 'source_changes': len(summary['source_changes_during_build']), 'repository_changes': len(summary['repository_changes_during_build']), 'dependency_changes': len(summary['dependency_changes_during_build'])}), flush=True)


if __name__ == '__main__':
    build_phase()
