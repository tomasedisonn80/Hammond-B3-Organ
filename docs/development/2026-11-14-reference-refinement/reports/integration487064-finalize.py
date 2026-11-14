#!/usr/bin/env python3
"""Retain one integration build/test result without rerunning any command."""
import gzip
import hashlib
import json
from pathlib import Path
import re
import shutil

OUT = Path(__file__).resolve().parent
REPO = Path('/workspace/scratch/1bb6ee17ad7e/Hammond-B3-Organ')
DEST = REPO / 'docs/development/2026-11-14-reference-refinement/reports'
P = 'integration487064-'

def identity(data):
    return {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}

def load(name):
    return json.loads((OUT / (P + name)).read_text())

build = load('build-summary.json')
test = load('ctest-summary.json')
repair = load('repair-build-summary.json')
frozen_tree = load('frozen-tree-check.json')
snapshots = {}
for label in ('before-build', 'after-build', 'before-repair-build', 'after-repair-build', 'before-test', 'after-test'):
    source = OUT / (P + 'inputs-' + label + '.json')
    raw = source.read_bytes()
    compressed = gzip.compress(raw, compresslevel=9, mtime=0)
    name = source.name + '.gz'
    (OUT / name).write_bytes(compressed)
    snapshots[label] = {'stored_file': name, 'original': identity(raw), 'compressed': identity(compressed), 'compression': 'gzip, lossless, mtime=0'}

before = load('inputs-before-test.json')
after = load('inputs-after-test.json')
raw_log = (OUT / (P + 'LastTest.log')).read_text(errors='replace')
sections = re.findall(r'(?ms)^\d+/\d+ Testing: ([^\n]+)\n(.*?)(?=^\d+/\d+ Testing: |\Z)', raw_log)
selected = {}
for name, text in sections:
    if any(fragment in name for fragment in ('rotary_history', 'rotary_renderer', 'rotary_streaming', 'rotary_waveform', 'compile_rotary', 'rotary_render_cli', 'repository_integrity', 'capture_install', 'standalone_install', 'waveform_material', 'material_acceptance', 'workspace_replay')):
        timing = re.search(r'Test time =\s*([0-9.]+) sec', text)
        methods = re.search(r'Ran (\d+) tests? in ([0-9.]+)s', text)
        selected[name] = {'passed': 'Test Passed.' in text, 'seconds': float(timing[1]) if timing else None,
                          'python_methods': int(methods[1]) if methods else None,
                          'section_utf8_sha256': hashlib.sha256(text.encode()).hexdigest()}

result = {'schema_version': 1, 'worker': '/root/w10_a59_publication_preflight', 'follow_up_not_new_worker': True,
          'scope': 'One all-target incremental build, one separately recorded approved test-only material target rebuild, and one full discovered CTest after incoming487064 integration and root-authorized final repository freeze.',
          'incoming_commit': before['target_published_commit'], 'incoming_tree': before['target_tree'],
          'observed_head_at_test': before['git']['head']['stdout'].strip(), 'observed_HEAD_tree_at_test': before['git']['head_tree']['stdout'].strip(),
          'worktree_boundary': 'Incoming487064 product/assets/data/build sources plus two exact approved test-only repairs, root closing workflow/attribute deltas and merged documentation/gallery records; all2,863 tested repository blobs exactly match the named frozen staged tree.',
          'build': build['build'], 'approved_test_only_repair': repair, 'frozen_staged_tree_check': frozen_tree, 'ctest_discovery': test['discovery'], 'original_ctest': test['original_ctest'],
          'full_suite_executions': test['full_suite_executions'], 'full_waveform_custom_target_executions': test['standalone_waveform_full_target_executions'],
          'discovered_count': test['discovered_count'], 'observed_all_pass': test['observed_all_pass'],
          'passing_completion_rows': test['passing_completion_rows'], 'passing_unique_names': test['passing_unique_names'],
          'LastTest_pass_markers': test['LastTest_pass_markers'], 'LastTest_failure_markers': test['LastTest_failure_markers'],
          'reported_summary': test['reported_summary'], 'ctest_reported_seconds': test['ctest_reported_seconds'],
          'qualification': test['qualification'], 'snapshots': snapshots,
          'repository_changes_during_build': build['repository_changes_during_build'],
          'source_changes_during_build': build['source_changes_during_build'],
          'documentation_changes_between_repair_build_and_test': test['documentation_changes_since_build'],
          'repository_changes_during_tests': test['repository_changes_during_tests'],
          'dependency_changes_during_build': build['dependency_changes_during_build'],
          'dependency_changes_during_tests': test['dependency_changes_during_tests'],
          'build_execution_changes_during_tests': test['build_execution_changes_during_tests'],
          'compiled_source_changes_between_repair_build_and_test': test['compiled_source_changes_since_build'],
          'execution_input_changes_between_repair_build_and_test': test['execution_input_changes_since_build'],
          'toolchain_unchanged': test['toolchain_unchanged'],
          'selected_cache': before['toolchain']['selected_cache'],
          'tool_versions': [{'command': t['command'], 'version_first_line': t['stdout'].splitlines()[0] if t['stdout'].splitlines() else '', 'resolved_path': t['resolved_path'], 'sha256': t['sha256']} for t in before['toolchain']['tools']],
          'native_executable': before['build_execution_inputs']['apps/standalone/hammond_standalone'],
          'waveform_probe': before['build_execution_inputs']['hammond_rotary_waveform_probe'],
          'cache': before['build_execution_inputs']['CMakeCache.txt'],
          'selected_original_results': selected,
          'inherited_failure_file': test.get('inherited_failure_file'), 'test_artifacts': test.get('test_artifacts', []),
          'limits': test['limitations'], 'original_commands_reexecuted_during_finalization': False,
          'next_action': 'Root reviews the exact coherent result, admits current captures and handles later published test-only fixes with their affected checks; observe exact final publication/hosted outcome.'}
result['outcome'] = 'passed_coherent_frozen_inputs' if (build['build']['exit'] == 0 and repair['command_result']['exit'] == 0 and test['observed_all_pass'] and not test['repository_changes_during_tests'] and not test['dependency_changes_during_tests'] and not test['build_execution_changes_during_tests']) else 'inspect_original_result_and_source_changes'
(OUT / (P + 'coherent-result.json')).write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
names = [P + n for n in ('run.py','test.py','finalize.py','repair-build.py','repair-build.log','repair-build-execution.json','repair-build-summary.json','frozen-tree-check.json','build.log','build-execution.json','build-summary.json','ctest-discovery.log','ctest-discovery-execution.json','ctest-original.log','ctest-original-execution.json','ctest-summary.json','coherent-result.json','LastTest.log','CTestCostData.txt','inherited-LastTestsFailed.log','LastTestsFailed.log')]
names += [record['stored_file'] for record in snapshots.values()]
files = {}
for name in names:
    source = OUT / name
    if source.exists():
        if (DEST / name).exists():
            raise RuntimeError('Refusing to overwrite existing integration evidence: ' + name)
        files[name] = identity(source.read_bytes())
        shutil.copyfile(source, DEST / name)
manifest = {'schema_version': 1, 'worker': '/root/w10_a59_publication_preflight', 'files': files,
            'total_bytes': sum(v['bytes'] for v in files.values()), 'original_commands_reexecuted_during_finalization': False,
            'all_logs_untruncated': all(not x['truncated'] for x in (build['build'],repair['command_result'],test['discovery'],test['original_ctest'])),
            'raw_executables_or_duplicate_build_trees_retained': False}
(DEST / (P + 'artifact-manifest.json')).write_text(json.dumps(manifest, sort_keys=True, indent=2) + '\n')
print(json.dumps({'outcome': result['outcome'], 'files_retained': len(files), 'bytes_retained': manifest['total_bytes'],
                  'discovered': test['discovered_count'], 'passed': test['passing_completion_rows'], 'seconds': test['ctest_reported_seconds'],
                  'result': str(DEST / (P + 'coherent-result.json'))}, indent=2))
