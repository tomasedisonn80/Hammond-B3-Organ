#!/usr/bin/env python3
"""Compact original A49 evidence and read its outcome without re-executing checks."""
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import re
import shutil

OUT = Path(__file__).resolve().parent
ROOT = Path('/workspace/scratch/1bb6ee17ad7e/Hammond-B3-Organ')
DEST = ROOT / 'docs/development/2026-11-14-reference-refinement/reports'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + '\n')


def main():
    report = json.loads((OUT / 'A49-coherent-final-build.json').read_text())
    snapshots = {name: json.loads((OUT / f'A49-inputs-{name}.json').read_text())
                 for name in ['before', 'after-build', 'after-test']}
    original = (OUT / 'A49-ctest-original.log').read_text()
    rows = re.findall(r'^\s*(\d+)/(\d+) Test\s+#(\d+): (\S+)\s+\.*\s+(Passed)\s+([0-9.]+) sec$', original, re.M)
    summary = re.search(r'^100% tests passed out of (\d+)$', original, re.M)
    assert summary and report['original_ctest']['exit'] == 0
    total = int(summary[1])
    assert len(rows) == total == report['discovered_count']
    assert {int(row[0]) for row in rows} == set(range(1, total + 1))
    assert {row[3] for row in rows} == set(report['discovered_names'])
    raw_details = (OUT / 'A49-LastTest.log').read_text()
    assert raw_details.count('Test Passed.') == total
    report['result_counts'] = {'discovered': total, 'executed': total, 'passed': total, 'failed': 0, 'ctest_not_run': 0}
    report['outcome'] = 'passed'
    report['count_evidence'] = {
        'raw_summary': summary[0], 'unique_pass_rows': len(rows), 'original_LastTest_pass_markers': total,
        'note': 'The original runner expected the older CTest success wording including zero failed. Its count field was absent; this offline finalizer reads CTest 4.4 wording and all original completion rows. No test or build was rerun.'}
    report['qualification'] = {
        'product_test_commit': report['target_published_commit'], 'published_tree': snapshots['before']['target_tree'],
        'repository_state': 'Published product/test/build sources plus frozen, partly uncommitted documentation, records and v4 gallery; not a clean worktree or all-published-tree claim.',
        'repository_files': len(snapshots['before']['repository_files']), 'markdown_files': snapshots['before']['markdown_count'],
        'product_test_inputs': snapshots['before']['published_product_test_input_count'],
        'product_input_definition': 'All files under apps, assets, cmake, data, include, plugins, src, tests, tools and .github, plus CMakeLists.txt, CMakePresets.json, Makefile, .gitattributes and .gitignore when present.',
        'repository_aggregate_sha256': snapshots['before']['repository_aggregate_sha256'],
        'product_test_aggregate_sha256': snapshots['before']['product_test_aggregate_sha256'],
        'markdown_aggregate_sha256': snapshots['before']['markdown_aggregate_sha256'],
        'dependency_files': len(snapshots['before']['dependency']['files']),
        'dependency_aggregate_sha256': snapshots['before']['dependency']['aggregate_sha256'],
        'cache_sha256': snapshots['before']['build_execution_inputs']['CMakeCache.txt']['sha256'],
        'native_executable_sha256': snapshots['after-test']['build_execution_inputs']['apps/standalone/hammond_standalone']['sha256'],
        'configuration': {'compiler': 'GCC 14.2.0', 'cmake_ctest': '4.4.5', 'ninja': '1.13.2.git.kitware.jobserver-pipe-1',
                          'python': '3.12.14', 'build_type': 'Release', 'cxx_release_flags': '-O3 -DNDEBUG',
                          'BUILD_TESTING': 'ON', 'HAMMOND_BUILD_STANDALONE': 'ON', 'HAMMOND_ENABLE_MIDI': 'OFF',
                          'HAMMOND_BUILD_VST3': 'OFF', 'HAMMOND_ENABLE_SANITIZERS': 'OFF',
                          'SDL2': '2.32.10', 'SDL2_commit': '5d249570393f7a37e037abf22cd6012a4cc56a71'},
        'freeze': {'first_snapshot_started_utc': snapshots['before']['started_utc'],
                   'post_test_snapshot_utc': snapshots['after-test']['completed_utc'],
                   'all_records_unchanged': not report['repository_changes'], 'all_dependency_records_unchanged': not report['dependency_changes'],
                   'postbuild_execution_inputs_unchanged_during_tests': not report['build_changes_during_tests'],
                   'product_files_match_published_source_before_and_after': all(not s['product_test_target_mismatches'] and not s['missing_product_test_inputs'] for s in snapshots.values()),
                   'logs_outside_repository_until_post_run_hashes': True, 'ownership': 'Repository freeze and build-native ownership released to root immediately after final snapshots.'}}
    report['documentation_consumers'] = [
        {'test': 'python_test_repository_integrity', 'inputs': 'All 912 Markdown files in the snapshot; supplied PDF; docs/research/source-manifest.json and chapter-index.json; original agent-note inventory and referenced data/fixture paths.',
         'basis': 'RealRepositorySmokeTests invokes check_repository(ROOT), whose Markdown walk reads root and .github/data/docs/examples/include/src/tests/tools.'},
        {'test': 'test_standalone_install', 'inputs': ['docs/STANDALONE_INSTALL.md', 'docs/STANDALONE_APP.md', 'docs/STANDALONE_MODEL.md', 'docs/MIDI_UI_RUNBOOK.md', 'docs/PRESET_RUNBOOK.md', 'docs/INTERFACE_RUNBOOK.md', 'THIRD_PARTY_NOTICES.md', 'docs/design/atlas-reference.json'],
         'basis': 'The install component hashes metadata at configure; native install acceptance checks exact live bytes and relocation. Other asset/dependency metadata also appears in the complete snapshots.'},
        {'test': 'python_test_capture_install', 'inputs': 'The 21 named docs in tests/test_capture_install.py DOCUMENTS and cmake/InstallCaptureTools.cmake, THIRD_PARTY_NOTICES.md, and examples/capture-demo/README.md plus the remaining fixed payload.',
         'basis': 'The private source fixture copies the docs tree, then checks exact 57-file component payload bytes and live-source preservation. Root README is copied but the installed CaptureTools README is generated.'},
        {'tests': ['python_test_capture_job', 'python_test_scanner_transient_reference', 'python_test_scanner_native_ac', 'python_test_rotary_motion_acceptance', 'python_test_rotary_propagation_acceptance', 'python_test_factory_reference'],
         'inputs': ['docs/CAPTURE_JOB_CONTRACT.md', 'docs/SCANNER_NUMERICAL_CONTRACT.md', 'docs/ROTARY_NUMERICAL_CONTRACT.md', 'docs/ROTARY_PROPAGATION_CONTRACT.md', 'docs/research/FACTORY_REVIEW_A.md', 'docs/research/FACTORY_REVIEW_B.md'],
         'basis': 'Direct contract reads, exact source identity hashes, or copied independent-reading notes.'},
        {'test': 'python_test_refinement_session', 'inputs': 'Synthetic private manifests and notes, plus the frozen checker source.',
         'basis': 'This registered test does not run the strict real A01-A60 session completion gate.'},
        {'test': 'python_test_capture_standalone_interface', 'inputs': 'The immutable v3 diagnostic JSON files and capture-validator source.',
         'basis': 'The new validator regression suite does not capture or independently qualify the new v4 gallery.'}]
    selected = ['test_standalone_material_acceptance', 'test_rotary_propagation_allocation',
                'python_test_capture_standalone_interface', 'python_test_refinement_session',
                'python_test_capture_install', 'test_standalone_install', 'python_test_repository_integrity']
    report['selected_original_results'] = {}
    for name in selected:
        m = re.search(r'(?ms)^\d+/157 Testing: ' + re.escape(name) + r'\n(.*?)(?=^\d+/157 Testing: |\Z)', raw_details)
        assert m and 'Test Passed.' in m[1]
        section = m[1]
        data = {'passed': True, 'ctest_seconds': float(re.search(r'Test time =\s*([0-9.]+) sec', section)[1])}
        methods = re.search(r'Ran (\d+) tests? in ([0-9.]+)s', section)
        if methods:
            data.update({'python_methods': int(methods[1]), 'python_reported_seconds': float(methods[2])})
        for line in section.splitlines():
            if line.startswith('{') and name in {'test_standalone_material_acceptance', 'test_rotary_propagation_allocation'}:
                payload = json.loads(line)
                if name == 'test_standalone_material_acceptance':
                    data.update({k: payload[k] for k in ['checks', 'failures', 'legacy_checks', 'header_checks', 'backend']})
                elif name == 'test_rotary_propagation_allocation':
                    data['fixture_result'] = payload
        report['selected_original_results'][name] = data
    stale = OUT / 'A49-LastTestsFailed.log'
    inherited = OUT / 'A49-inherited-LastTestsFailed.log'
    if stale.exists():
        stale.rename(inherited)
    original_stale = ROOT.parent / 'build-native/Testing/Temporary/LastTestsFailed.log'
    report['inherited_failure_file'] = {
        'retained_copy': inherited.name, 'sha256': digest(inherited), 'contents': inherited.read_text(),
        'original_build_tree_mtime_utc': datetime.fromtimestamp(original_stale.stat().st_mtime, timezone.utc).isoformat(),
        'classification': 'Inherited historical file predating A49. CTest did not clear it after this pass; it is not the current result. Original build-tree file was not removed.'}
    report['test_artifacts'] = [a for a in report['test_artifacts'] if a['name'] != 'A49-LastTestsFailed.log']
    report['historical_result_preserved'] = {
        'path': 'docs/development/2026-11-14-reference-refinement/reports/coherent-result.json',
        'sha256_before_and_after': snapshots['before']['repository_files']['docs/development/2026-11-14-reference-refinement/reports/coherent-result.json']['sha256'],
        'classification': 'Earlier full 154/155 plus distinct repaired 1/1 remains unchanged history. A49 is the new single full 157-suite execution.'}
    report['limits'] = [
        'Incremental all-target reuse of the configured GCC Release tree; not a clean rebuild or a hermetic operating-system image.',
        'Frozen documentation includes unpublished changes; later documentation/report additions require their own affected final repository checks.',
        'Full CTest includes its standard native dummy-driver workflows and benchmark smoke fixtures; no separate benchmark, GUI capture or sanitizer campaign was launched.',
        'MIDI is OFF and VST3 is OFF; this run does not qualify those enabled products, physical devices, DAWs, accessibility, deadlines, signing or visual/physical fidelity.',
        'The historical LSan environment failure and hosted sanitizer evidence remain separate; no current-source sanitizer result is inferred.',
        'The original scanner G5 limitation and unconnected nominal rotary/Engine boundary remain unchanged.',
        'The strict real refinement completion checker remains for root after all sixty actual results are accepted.'
    ]
    report['next_action'] = 'Root reviews and accepts A49, completes remaining actual assignments and source-specific hosted/gallery checks, then checks final documentation and runs the strict refinement completion gate against the accepted sixty-record manifest before authorized publication.'
    for label in snapshots:
        path = OUT / f'A49-inputs-{label}.json'
        compressed = path.with_suffix('.json.gz')
        compressed.write_bytes(gzip.compress(path.read_bytes(), mtime=0))
        assert gzip.decompress(compressed.read_bytes()) == path.read_bytes()
        report['snapshots'][label].update({'stored_file': compressed.name, 'compression': 'gzip, lossless, mtime=0', 'compressed_bytes': compressed.stat().st_size, 'compressed_sha256': digest(compressed)})
    report['executed_runner_sha256'] = digest(OUT / 'A49-run-coherent-build.py')
    save(OUT / 'A49-coherent-final-build.json', report)
    allowed = [p for p in OUT.iterdir() if p.is_file() and p.name.startswith('A49-') and not re.fullmatch(r'A49-inputs-.*\.json', p.name)]
    for path in allowed:
        shutil.copyfile(path, DEST / path.name)
    manifest = {'schema_version': 1, 'worker': '/root/w09_a49_coherent_final_build',
                'files': {p.name: {'sha256': digest(p), 'bytes': p.stat().st_size} for p in sorted(allowed)},
                'total_bytes': sum(p.stat().st_size for p in allowed), 'all_logs_untruncated': True,
                'original_results_reexecuted_during_finalization': False}
    save(DEST / 'A49-artifact-manifest.json', manifest)
    print(json.dumps({'result': report['result_counts'], 'original_ctest_seconds': report['ctest_reported_seconds'], 'retained_files': len(allowed), 'retained_bytes': manifest['total_bytes']}))


if __name__ == '__main__':
    main()
