#!/usr/bin/env python3
"""One explicitly approved test-only target rebuild; preserve the first build."""
import importlib.util
import json
import os
from pathlib import Path
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('integration_methods', HERE / 'integration487064-run.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
os.environ['GIT_OPTIONAL_LOCKS'] = '0'
if (HERE / 'integration487064-inputs-before-repair-build.json').exists():
    raise RuntimeError('Refusing to overwrite the original repair-build snapshot.')
overlay = {
    'apps/standalone/native_tests/test_standalone_waveform_material.cpp': '1b6449143afd636e48b6be5e422b591e4dee26e29592b98a2394665916cdfead',
    'tests/test_rotary_waveform_acceptance.py': 'e2a21f1b5181ae7b46c776e96041a95b24ca2e2391f1e55ff5aed3e0d03e688d',
}
before = m.snapshot('before-repair-build')
for path, expected in overlay.items():
    if before['repository_files'][path]['sha256'] != expected:
        raise RuntimeError('Approved repair hash does not match: ' + path)
allowed = set(overlay) | {'.gitattributes', '.github/workflows/ci.yml'}
if set(before['product_test_target_mismatches']) - allowed or before['missing_product_test_inputs']:
    raise RuntimeError('Unexpected source beyond approved two-test overlay; rebuild not launched.')
result = m.execute('repair-build', [m.CMAKE, '--build', '../build-native', '--target', 'test_standalone_waveform_material', '--parallel', '3'])
after = m.snapshot('after-repair-build')
summary = {'schema_version': 1, 'worker': '/root/w10_a59_publication_preflight', 'follow_up_not_new_worker': True,
           'incoming_commit': m.BASE, 'overlay': overlay,
           'adoption_receipt': 'docs/development/2026-11-14-reference-refinement/reports/root-integration487064-test-repair-adoption.json',
           'adoption_receipt_identity': m.file_record(m.ROOT / 'docs/development/2026-11-14-reference-refinement/reports/root-integration487064-test-repair-adoption.json'),
           'reason': 'Root adopted two independently reviewed test-only repairs after hosted compiler/numeric failures; the initial all-target build remains unchanged.',
           'command_result': result,
           'repository_changes_during_rebuild': m.changes(before['repository_files'], after['repository_files']),
           'source_changes_during_rebuild': [r for r in m.changes(before['repository_files'], after['repository_files']) if r['path'].split('/')[0] in m.SOURCE_DIRS or r['path'] in m.SOURCE_ROOT_FILES],
           'dependency_changes_during_rebuild': m.changes(before['dependency']['files'], after['dependency']['files']),
           'build_execution_input_changes': m.changes(before['build_execution_inputs'], after['build_execution_inputs']),
           'full_ctest_executed': False,
           'limits': ['A local GCC target rebuild is not a macOS/Windows hosted repair pass.', 'The Python test-only overlay executes later in the explicitly authorized full CTest; it needs no compiled target.']}
m.write('integration487064-repair-build-summary.json', summary)
print(json.dumps({'event': 'repair_build_stage_complete', 'utc': m.now(), 'exit': result['exit'], 'seconds': result['seconds'], 'source_changes': len(summary['source_changes_during_rebuild']), 'repository_changes': len(summary['repository_changes_during_rebuild'])}), flush=True)
