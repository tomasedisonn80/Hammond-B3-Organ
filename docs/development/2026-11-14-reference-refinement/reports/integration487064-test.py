#!/usr/bin/env python3
"""One full CTest after root authorizes the coherent repository freeze."""
import importlib.util
import json
import os
from pathlib import Path
import re
import shutil

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('integration_methods', HERE / 'integration487064-run.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
os.environ['GIT_OPTIONAL_LOCKS'] = '0'
if (HERE / 'integration487064-inputs-before-test.json').exists():
    raise RuntimeError('This one-shot test phase already has a snapshot; preserve it and require an explicitly named later run.')
built = json.loads((HERE / 'integration487064-inputs-after-repair-build.json').read_text())
repair = json.loads((HERE / 'integration487064-repair-build-summary.json').read_text())
before = m.snapshot('before-test')
allowed = set(repair['overlay']) | {'.gitattributes', '.github/workflows/ci.yml'}
for path, expected in repair['overlay'].items():
    if before['repository_files'][path]['sha256'] != expected:
        raise RuntimeError('Approved test-only overlay changed: ' + path)
if set(before['product_test_target_mismatches']) - allowed or before['missing_product_test_inputs']:
    raise RuntimeError('Unexpected incoming product/source mismatch; full suite not launched.')
source_changes = [r for r in m.changes(built['repository_files'], before['repository_files'])
                  if (r['path'].split('/')[0] in m.SOURCE_DIRS or r['path'] in m.SOURCE_ROOT_FILES)
                  and r['path'] not in allowed]
execution_changes = m.changes(built['build_execution_inputs'], before['build_execution_inputs'])
if source_changes or execution_changes:
    m.write('integration487064-pretest-blocker.json', {'source_changes': source_changes, 'build_execution_input_changes': execution_changes})
    raise RuntimeError('Source or execution inputs differ from the completed build; ask root before executing.')
summary = {'schema_version': 1, 'worker': '/root/w10_a59_publication_preflight',
           'follow_up_not_new_assignment': True, 'incoming_source': m.BASE,
           'approved_test_only_overlay': repair['overlay'],
           'build_input_baseline': 'after the single approved test-only fixture rebuild',
           'root_frozen_staged_tree': 'ef49240585d5b2a88fd6788496151917e2b2491a',
           'full_suite_executions': 0, 'standalone_waveform_full_target_executions': 0,
           'repository_freeze': 'Root explicitly authorized this whole-repository test freeze after its gallery and A54 shared documents completed.',
           'compiled_source_changes_since_build': source_changes,
           'execution_input_changes_since_build': execution_changes,
           'documentation_changes_since_build': [r for r in m.changes(built['repository_files'], before['repository_files']) if r['path'] not in before['product_test_inputs']]}
inherited = m.BUILD / 'Testing/Temporary/LastTestsFailed.log'
if inherited.is_file():
    saved = HERE / 'integration487064-inherited-LastTestsFailed.log'
    shutil.copyfile(inherited, saved)
    summary['inherited_failure_file'] = {'path': saved.name, 'original_mtime_ns': inherited.stat().st_mtime_ns,
                                         **m.file_record(saved), 'classification': 'Pre-existing before this full test run; not a current failure observation.'}
discovery = m.execute('ctest-discovery', [m.CTEST, '--test-dir', '../build-native', '-C', 'Release', '--show-only=json-v1', '--no-tests=error'])
summary['discovery'] = discovery
if discovery['exit'] or discovery['truncated']:
    m.write('integration487064-ctest-summary.json', summary)
    raise RuntimeError('Discovery failed; full suite not launched.')
tests = json.loads((HERE / discovery['log']).read_text())['tests']
if not tests:
    raise RuntimeError('No registered tests; full suite not launched.')
summary['discovered_count'] = len(tests)
summary['discovered_names'] = [test['name'] for test in tests]
print(json.dumps({'event': 'discovered', 'count': len(tests), 'utc': m.now()}), flush=True)
original = m.execute('ctest-original', [m.CTEST, '--test-dir', '../build-native', '-C', 'Release', '--output-on-failure', '--no-tests=error', '--parallel', '3'])
summary['original_ctest'] = original
summary['full_suite_executions'] = 1
for name in ['LastTest.log', 'LastTestsFailed.log', 'CTestCostData.txt']:
    source = m.BUILD / 'Testing/Temporary' / name
    if source.is_file():
        record = m.file_record(source)
        if record['bytes'] > m.LOG_CAP:
            summary.setdefault('uncopied_test_artifacts', []).append({'name': name, **record, 'reason': 'exceeds eight-MiB retained bound'})
        else:
            destination = HERE / ('integration487064-' + name)
            shutil.copyfile(source, destination)
            summary.setdefault('test_artifacts', []).append({'path': destination.name, **m.file_record(destination)})
after = m.snapshot('after-test')
summary['repository_changes_during_tests'] = m.changes(before['repository_files'], after['repository_files'])
summary['dependency_changes_during_tests'] = m.changes(before['dependency']['files'], after['dependency']['files'])
summary['build_execution_changes_during_tests'] = m.changes(before['build_execution_inputs'], after['build_execution_inputs'])
summary['toolchain_unchanged'] = before['toolchain']['tools'] == after['toolchain']['tools']
text = (HERE / original['log']).read_text(errors='replace')
rows = re.findall(r'^\s*(\d+)/(\d+) Test\s+#(\d+): (\S+)\s+\.*\s+(Passed)\s+([0-9.]+) sec$', text, re.M)
summary['passing_completion_rows'] = len(rows)
summary['passing_unique_names'] = len({r[3] for r in rows})
summary['passing_completion_names'] = [r[3] for r in rows]
summary['reported_summary'] = re.findall(r'^.*tests passed.*$', text, re.M)
seconds = re.search(r'Total Test time \(real\) =\s*([0-9.]+) sec', text)
summary['ctest_reported_seconds'] = float(seconds[1]) if seconds else None
raw = (HERE / 'integration487064-LastTest.log').read_text(errors='replace')
summary['LastTest_pass_markers'] = raw.count('Test Passed.')
summary['LastTest_failure_markers'] = raw.count('Test Failed.')
summary['observed_all_pass'] = (original['exit'] == 0 and len(rows) == len(tests) and len({r[3] for r in rows}) == len(tests)
                                 and {r[3] for r in rows} == set(summary['discovered_names'])
                                 and raw.count('Test Passed.') == len(tests))
summary['qualification'] = {'repository_files': len(before['repository_files']), 'repository_aggregate_sha256': before['repository_aggregate_sha256'],
                            'markdown_files': before['markdown_count'], 'markdown_aggregate_sha256': before['markdown_aggregate_sha256'],
                            'product_control_inputs': before['published_product_test_input_count'], 'product_control_aggregate_sha256': before['product_test_aggregate_sha256'],
                            'source_target_mismatches': before['product_test_target_mismatches'],
                            'dependency_files': len(before['dependency']['files']), 'dependency_aggregate_sha256': before['dependency']['aggregate_sha256'],
                            'snapshot_started_utc': before['started_utc'], 'post_test_snapshot_utc': after['completed_utc']}
summary['limitations'] = ['An incremental all-target GCC Release build and one full registered CTest; not a clean rebuild, hermetic image or cross-platform rerun.',
                        'MIDI, VST3 and sanitizers are OFF in this local build; physical devices, GUI, deadline, literal equality and physical fidelity are not newly qualified.',
                        'The expensive custom ten-second full waveform target was not invoked here; incoming retained full-run and exact final CI evidence keep their source boundaries.',
                        'Known hosted487064 macOS/Windows failures remain separate; the two exact approved test-only repairs were adopted and the affected material target was rebuilt once before this full GCC run. Actual repaired-platform CI remains required.',
                        'Original A49 and accepted notes/reports remain untouched.']
m.write('integration487064-ctest-summary.json', summary)
print(json.dumps({'event': 'full_test_stage_complete', 'utc': m.now(), 'exit': original['exit'], 'discovered': len(tests), 'passed_rows': len(rows), 'reported_seconds': summary['ctest_reported_seconds'],
                  'repository_changes': len(summary['repository_changes_during_tests']), 'dependency_changes': len(summary['dependency_changes_during_tests']),
                  'execution_input_changes': len(summary['build_execution_changes_during_tests'])}), flush=True)
