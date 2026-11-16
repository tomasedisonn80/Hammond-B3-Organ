"""Demonstrate the boundary between source-file hashes and imported bytecode.

Only an owned temporary five-file layout is modified; repository inputs stay
read-only. This is an adversarial deployment observation, not a passing source
identity guarantee or a request to support edited/stale installations.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import py_compile
import shutil
import subprocess
import sys
import tempfile

REPO = Path(__file__).resolve().parents[4]
# Resolve independently of where this exact retained script is invoked.
while not (REPO / 'tools/convert_contact_grid.py').is_file():
    if REPO.parent == REPO:
        raise RuntimeError('repository not found')
    REPO = REPO.parent
sys.path.insert(0, str(REPO / 'tests/reference'))
import contact_grid_conversion_cases as corpus
FILES = ('tools/contact_grid_conversion.py', 'tools/convert_contact_grid.py',
         'tools/contact_switching_io.py', 'tools/fractional_contact_reference.py',
         'docs/CONTACT_GRID_CONVERSION_CONTRACT.md')

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    with tempfile.TemporaryDirectory(prefix='a20-import-cache-') as directory:
        root = Path(directory)
        for name in FILES:
            target = root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO / name, target)
        numerical = root / FILES[0]
        information = numerical.stat()
        before_hash = sha(numerical)
        cache = Path(py_compile.compile(str(numerical), doraise=True,
                     invalidation_mode=py_compile.PycInvalidationMode.TIMESTAMP))
        data = numerical.read_bytes()
        old = b'MAX_WORK_UNITS = 1_000_000'
        new = b'MAX_WORK_UNITS = 1        '
        assert len(old) == len(new) and data.count(old) == 1
        numerical.write_bytes(data.replace(old, new))
        os.utime(numerical, ns=(information.st_atime_ns, information.st_mtime_ns))
        assert numerical.stat().st_size == information.st_size
        fixture = next(row for row in corpus.cases() if row['name'] == 'empty-epoch')
        source = root / 'input.json'
        source.write_bytes(corpus.canonical_input_bytes(fixture['input']))
        rows = []
        for phase in ('timestamp_cache_present', 'cache_removed'):
            destination = root / (phase + '.json')
            result = subprocess.run([sys.executable, '-B', str(root / FILES[1]),
                                     '--input', str(source), '--output', str(destination)],
                                    capture_output=True, timeout=10)
            row = {'phase': phase, 'returncode': result.returncode,
                   'stderr': result.stderr.decode('utf-8', 'replace')}
            if destination.exists():
                value = json.loads(destination.read_bytes())
                row.update(status=value['status'], work_units=value['summary']['work_units'],
                           certificate_numerical_sha256=value['provenance']['implementation_sha256'][FILES[0]])
            else:
                row['refusal'] = json.loads(result.stdout)
            rows.append(row)
            if phase == 'timestamp_cache_present':
                cache.unlink()
        report = {'python': sys.version, 'source_inputs': {name: sha(REPO / name) for name in FILES},
                  'original_numerical_sha256': before_hash, 'edited_numerical_sha256': sha(numerical),
                  'same_size_and_timestamp': True, 'rows': rows,
                  'limits': 'Source hashes describe bytes read from disk. Python -B prevents writing caches, not reading a valid timestamp cache. Trusted unchanged sources and a consistent import environment remain necessary; no hostile-code authentication is supplied.'}
    output = Path(__file__).with_suffix('.json')
    if output.exists():
        raise RuntimeError('refusing to overwrite retained observation')
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'output': str(output), 'rows': report['rows']}, indent=2))

if __name__ == '__main__':
    main()
