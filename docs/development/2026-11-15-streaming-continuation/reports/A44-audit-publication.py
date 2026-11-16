#!/usr/bin/env python3
"""Read-only Git audit of A44's retained API observations; no fetch or tests."""
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess

ROOT = Path(__file__).resolve().parents[4]
SESSION = Path('docs/development/2026-11-15-streaming-continuation')
REPORTS = ROOT / SESSION / 'reports'
COMMIT = 'af2b74760ee195c9497b314a1a29172f5238dd44'
TREE = 'fb7d9ef7d1fcf24a70395c0671b75eb9c31558d4'
PARENT = '4aac394cde4da40906b615573a8779aee2d9a37a'
BASE_TREE = '3605c9ce098a052afc10b2969fefe31e15644fe9'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
COMMANDS = []

def git(*args):
    COMMANDS.append(['git', *args])
    return subprocess.check_output(['git', *args], cwd=ROOT, env=ENV)

def sha256(data):
    return hashlib.sha256(data).hexdigest()

def inventory(ref):
    result = {}
    for row in git('ls-tree', '-r', '-t', '-l', '-z', ref).split(b'\0'):
        if not row:
            continue
        header, path = row.split(b'\t', 1)
        mode, kind, sha, size = header.decode().split()
        entry = {'mode': mode, 'type': kind, 'sha': sha}
        if size != '-':
            entry['size'] = int(size)
        result[path.decode()] = entry
    return result

index_path = Path(git('rev-parse', '--git-path', 'index').decode().strip())
if not index_path.is_absolute():
    index_path = ROOT / index_path
index_before = sha256(index_path.read_bytes())
api_bytes = gzip.decompress((REPORTS / 'A44-api-observations.json.gz').read_bytes())
api = json.loads(api_bytes)
obs = api['observations']
remote_commit = obs['commit']['response']
remote_ref = obs['ref']['response']
remote_tree = obs['tree']['response']
remote_parent = obs['parent']['response']
assert remote_commit['sha'] == COMMIT
assert remote_commit['tree']['sha'] == TREE
assert [p['sha'] for p in remote_commit['parents']] == [PARENT]
assert remote_ref['ref'] == 'refs/heads/main'
assert remote_ref['object']['sha'] == COMMIT
assert remote_ref['object']['type'] == 'commit'
assert remote_parent['sha'] == PARENT and remote_parent['tree']['sha'] == BASE_TREE
assert remote_tree['sha'] == TREE and remote_tree['truncated'] is False
remote = {e['path']: {k: e[k] for k in ('mode', 'type', 'sha', 'size') if k in e}
          for e in remote_tree['tree']}
assert len(remote) == len(remote_tree['tree'])
published = inventory(COMMIT)
base = inventory(PARENT)
assert published == remote, 'Complete remote/local tree inventory mismatch'
refs = git('rev-parse', 'HEAD', 'HEAD^{tree}', 'HEAD^', 'refs/remotes/origin/main').decode().splitlines()
assert refs == [COMMIT, TREE, PARENT, COMMIT]
assert git('diff', '--cached', '--name-only').strip() == b''

manifest_bytes = (ROOT.parent / 'publication-manifest.json').read_bytes()
manifest = json.loads(manifest_bytes)
retained_manifest = gzip.decompress((REPORTS / 'implementation-published-manifest.json.gz').read_bytes())
assert retained_manifest == manifest_bytes
assert manifest['parent'] == PARENT and manifest['base_tree'] == BASE_TREE and manifest['tree'] == TREE
entries = {e['path']: {k: e[k] for k in ('mode', 'type', 'sha', 'size') if k in e}
           for e in manifest['entries']}
assert len(entries) == len(manifest['entries']) == 243
base_files = {p: e for p, e in base.items() if e['type'] != 'tree'}
published_files = {p: e for p, e in published.items() if e['type'] != 'tree'}
deleted = sorted(set(base_files) - set(published_files))
changed = {p: e for p, e in published_files.items() if base_files.get(p) != e}
assert not deleted and changed == entries
receipt_bytes = (REPORTS / 'implementation-publication.json').read_bytes()
receipt = json.loads(receipt_bytes)
assert (receipt['commit'], receipt['tree'], receipt['parent'], receipt['branch'], receipt['files']) == (COMMIT, TREE, PARENT, 'main', 243)
assert receipt['published_manifest']['raw_sha256'] == sha256(manifest_bytes)

# Explicit published scope; no rule is inferred from the manifest under review.
allowed_exact = set('''
.github/workflows/standalone.yml
AGENTS.md
CMakeLists.txt
README.md
apps/standalone/CMakeLists.txt
apps/standalone/InstrumentView.cpp
apps/standalone/native_tests/test_standalone_upper_rack_material_raster.cpp
cmake/StandaloneBenchmark.cmake
docs/BUILD.md
docs/CAUSAL_CONTACT_GRID_CONTRACT.md
docs/CAUSAL_CONTACT_GRID_GUIDE.md
docs/CAUSAL_CONTACT_GRID_RESULTS.md
docs/DEVELOPMENT_LOG.md
docs/NEXT_STEPS.md
docs/PLAN.md
docs/PRODUCT_HANDOFF.md
docs/PROJECT_GUIDE.md
docs/STANDALONE_BENCHMARK_BUILD.md
docs/STATUS.md
docs/design/UPPER_RACK_MATERIAL_CONTRACT.md
docs/development/agent-guidance-history-2026-11-15.txt
docs/research/CAUSAL_CONTACT_AUDIO_NEXT.md
docs/research/CONTACT_GRID_CONVERSION_NEXT.md
docs/reviews/CAUSAL_CONTACT_GRID_ADMISSION.md
docs/reviews/CAUSAL_CONTACT_GRID_IMPLEMENTATION_REVIEW.md
docs/reviews/CAUSAL_CONTACT_GRID_PORTABILITY.md
docs/reviews/CAUSAL_CONTACT_GRID_RESOURCE_ADMISSION.md
docs/reviews/STREAMING_BUILD_INTEGRATION_REVIEW.md
docs/reviews/STREAMING_CONTINUATION_COMPATIBILITY.md
docs/reviews/UPPER_RACK_COMPARISON_ADMISSION.md
docs/reviews/UPPER_RACK_GALLERY_ADMISSION.md
docs/reviews/UPPER_RACK_MATERIAL_ADMISSION.md
docs/reviews/UPPER_RACK_PAINTER_REVIEW.md
include/hammond/research/CausalContactGrid.h
src/research/CausalContactGrid.cpp
tests/reference/causal_contact_grid_reference.py
tests/test_causal_contact_grid.cpp
tests/test_causal_contact_grid_cli.py
tests/test_causal_contact_grid_differential.py
tests/test_causal_contact_grid_lifecycle.cpp
tests/test_causal_contact_grid_reference.py
tests/test_causal_contact_grid_resources.cpp
tools/causal_contact_grid_probe.cpp
tools/causal_contact_grid_work_receipt.py
tools/compare_upper_rack_material.py
'''.split())
allowed_prefixes = (str(SESSION) + '/', 'examples/demos/upper-rack-material-v1/')
outside_scope = [p for p in changed if p not in allowed_exact and not p.startswith(allowed_prefixes)]
unsafe_paths = [p for p in changed if PurePosixPath(p).is_absolute() or '..' in PurePosixPath(p).parts
                or '\\' in p or any(ord(c) < 32 for c in p)]
unsafe_modes = [p for p, e in changed.items() if e['mode'] not in ('100644', '100755') or e['type'] != 'blob']
artifact_path_pattern = re.compile(r'(^|/)(?:build(?:-[^/]*)?|CMakeFiles|_deps|node_modules|\.venv|\.git|\.ssh|\.aws)(?:/|$)|\.(?:o|obj|a|so|dylib|dll|exe|pdb|class|pyc|pyo|zip|tar|7z|apk|vst3|deb|msi)$', re.I)
secret_path_pattern = re.compile(r'(^|/)(?:\.env(?:\.[^/]*)?|id_rsa|id_ed25519|credentials|secrets?\.json|[^/]+\.(?:pem|p12|pfx))$', re.I)
artifact_paths = [p for p in changed if artifact_path_pattern.search(p)]
secret_paths = [p for p in changed if secret_path_pattern.search(p)]
assert not (outside_scope or unsafe_paths or unsafe_modes or artifact_paths or secret_paths)

COMMANDS.append(['git', 'cat-file', '--batch'])
batch = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT, env=ENV,
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE)
digest_cache = {}

def blob(sha):
    batch.stdin.write((sha + '\n').encode()); batch.stdin.flush()
    header = batch.stdout.readline().decode().split()
    assert len(header) == 3 and header[0] == sha and header[1] == 'blob'
    size = int(header[2]); value = batch.stdout.read(size)
    assert len(value) == size and batch.stdout.read(1) == b'\n'
    assert hashlib.sha1(b'blob ' + str(size).encode() + b'\0' + value).hexdigest() == sha
    digest_cache[sha] = sha256(value)
    return value

secret_patterns = {
    'private_key': re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
    'github_token': re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,})\b'),
    'aws_access_key': re.compile(rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
    'authorization_literal': re.compile(rb'(?i)authorization\s*[:=]\s*(?:bearer|token)\s+[A-Za-z0-9._/+~-]{16,}'),
    'credential_url': re.compile(rb'https?://[^/\s:@]+:[^/\s@]+@'),
}
binary_signatures = (b'\x7fELF', b'MZ', b'!<arch>\n', b'PK\x03\x04',
                     b'\xfe\xed\xfa\xce', b'\xce\xfa\xed\xfe', b'\xfe\xed\xfa\xcf', b'\xcf\xfa\xed\xfe')
scan_hits = []; formats = Counter(); changed_checks = []
for path, entry in sorted(changed.items()):
    value = blob(entry['sha'])
    assert len(value) == entry['size']
    decoded = value
    if value.startswith(b'\x1f\x8b'):
        assert path.endswith('.gz'); decoded = gzip.decompress(value); formats['gzip_text'] += 1
        decoded.decode('utf-8')
    elif value.startswith(b'\x89PNG\r\n\x1a\n'):
        assert path.endswith('.png'); formats['png_evidence'] += 1
    else:
        decoded.decode('utf-8'); formats['utf8_text'] += 1
    if value.startswith(binary_signatures) or decoded.startswith(binary_signatures):
        scan_hits.append({'path': path, 'kind': 'compiled_or_archive_signature'})
    for kind, pattern in secret_patterns.items():
        if pattern.search(decoded):
            scan_hits.append({'path': path, 'kind': kind})
    changed_checks.append({'path': path, **entry, 'content_sha256': sha256(value),
                           'status': 'modified' if path in base_files else 'added'})
assert not scan_hits, 'Review scan hits by path and kind; never print matched values'

compat = json.loads(blob(published_files[str(SESSION / 'reports/A30-compatibility.json')]['sha']))
preserved = {}
for group, data in compat['preserved_groups'].items():
    identities = []
    for path, expected_sha256 in data['paths'].items():
        assert base_files[path] == published_files[path] == remote[path]
        oid = published_files[path]['sha']
        actual = digest_cache.get(oid)
        if actual is None:
            actual = sha256(blob(oid))
        assert actual == expected_sha256
        identities.append({'path': path, 'blob': oid, 'sha256': actual})
    assert len(identities) == data['count']
    preserved[group] = {'count': len(identities), 'all_equal_base_and_remote': True,
                        'all_sha256_recomputed': True, 'identities': identities}
component_checks = []
for path, expected in compat['contact_reference_component']['install_rules_and_payload_sha256'].items():
    assert base_files[path] == published_files[path] == remote[path]
    oid = published_files[path]['sha']
    actual = digest_cache.get(oid) or sha256(blob(oid))
    assert actual == expected
    component_checks.append(path)
archive_path = 'docs/development/agent-guidance-history-2026-11-15.txt'
archived_agents = blob(published_files[archive_path]['sha'])
parent_agents = blob(base_files['AGENTS.md']['sha'])
assert archived_agents.endswith(parent_agents)
archive_prefix = archived_agents[:-len(parent_agents)]
assert len(archive_prefix) == 1180 and archive_prefix.startswith(b'# Current streaming/material continuation')
assert digest_cache[published_files[archive_path]['sha']] == '027c7a2a2dd9e27092d338a3b1fa3d36d730195b616711eecfa4310eebabfd41'

published_ledger = json.loads(blob(published_files[str(SESSION / 'assignments.json')]['sha']))
working_ledger_bytes = (ROOT / SESSION / 'assignments.json').read_bytes()
working_ledger = json.loads(working_ledger_bytes)
def ledger_summary(data):
    a = data['assignments']
    return {'records': len(a), 'status_counts': dict(Counter(x['status'] for x in a)),
            'max_number': max(x['number'] for x in a),
            'requested_workers': data['requested_workers'],
            'requested_waves': data['requested_waves']}

status = []
for row in git('status', '--porcelain=v1', '--untracked-files=all', '-z').split(b'\0'):
    if row:
        xy, path = row[:2].decode(), row[3:].decode()
        status.append({'status': xy, 'path': path,
                       'path_present_in_published_commit': path in published_files})

invocation_bytes = (REPORTS / 'publication-invocation-record.json').read_bytes()
invocation = json.loads(invocation_bytes)
calls = invocation['ordered_calls']
update = next(c for c in calls if c['tool'] == 'github_update_ref')
assert calls[0]['observed_sha'] == update['expected_sha'] == PARENT
assert update['sha'] == COMMIT and update['branch_name'] == 'main' and update['force'] is False
assert update['result']['success'] is True
assert 'Post-hoc transcription' in invocation['record_kind']
preflight = json.loads(blob(published_files[str(SESSION / 'reports/publication-preflight.json')]['sha']))
assert preflight['shell_push_preflight']['exit_code'] == 128

batch.stdin.close(); batch.stdout.close(); assert batch.wait() == 0
index_after = sha256(index_path.read_bytes())
assert index_before == index_after, 'Index changed concurrently; this script never writes it'
modified_original = sorted(p for p in changed if p in base_files)
report = {
    'schema_version': 1, 'reviewer': '/root/w08_a44',
    'observed_utc': datetime.now(timezone.utc).isoformat(), 'cwd': str(ROOT),
    'commit': COMMIT, 'tree': TREE, 'parent': PARENT, 'base_tree': BASE_TREE,
    'api_observation_times': {k: v['observed_at'] for k, v in obs.items()},
    'api_snapshot_gzip_sha256': sha256((REPORTS / 'A44-api-observations.json.gz').read_bytes()),
    'api_snapshot_raw_sha256': sha256(api_bytes),
    'remote_tree_entries': len(remote), 'remote_tree_truncated': False,
    'complete_remote_tree_equals_local_commit': True,
    'local_head_tree_parent_origin_main': refs,
    'manifest_raw_sha256': sha256(manifest_bytes),
    'retained_manifest_bytes_equal_original': True,
    'root_publication_receipt_sha256': sha256(receipt_bytes),
    'changed_paths': len(changed), 'added_paths': len(changed) - len(modified_original),
    'modified_original_paths': modified_original, 'deleted_paths': deleted,
    'manifest_entry_comparisons': changed_checks,
    'changed_modes': dict(Counter(e['mode'] for e in changed.values())),
    'all_original_files': len(base_files),
    'unchanged_original_files': len(base_files) - len(modified_original),
    'preserved_groups': preserved,
    'frozen_contact_component_files_including_install_rules': component_checks,
    'original_AGENTS_archive': {'entire_parent_AGENTS_preserved_as_exact_suffix': True,
        'streaming_session_preface_bytes': len(archive_prefix), 'archive_bytes': len(archived_agents),
        'archive_sha256': sha256(archived_agents), 'parent_agents_sha256': sha256(parent_agents),
        'initial_audit_assumption_correction': 'A44-audit-attempt1.json'},
    'scope_and_leakage_screen': {'explicit_scope_mismatches': outside_scope,
        'unsafe_paths': unsafe_paths, 'unsafe_modes': unsafe_modes,
        'artifact_paths': artifact_paths, 'secret_paths': secret_paths,
        'content_formats': dict(formats), 'content_signature_hits': scan_hits,
        'secret_pattern_names': list(secret_patterns),
        'limit': 'Checks all 243 changed Git blobs and gzip-expanded evidence for declared path/content patterns; not a proof against arbitrary encoded secrets.'},
    'authorization': {'source': 'AGENTS.md Integration and publication plus root-owned accepted scope',
        'invocation_record_sha256': sha256(invocation_bytes),
        'evidence_kind': invocation['record_kind'],
        'documented_fresh_expected_sha': PARENT, 'documented_force': False,
        'documented_update_success': True,
        'limit': 'A44 independently observed post-state. Ordered pre-update invocation is root transcription without per-call timestamps; no server-internal atomic compare-and-swap guarantee is inferred.'},
    'cli_auth_failure': {'exit_code': 128, 'classification': 'Preserved preflight history superseded for publication availability by observed API success; not an unresolved publication blocker.'},
    'published_ledger_snapshot': ledger_summary(published_ledger),
    'working_ledger_snapshot': ledger_summary(working_ledger),
    'working_ledger_sha256': sha256(working_ledger_bytes),
    'unpublished_working_snapshot': status,
    'index_sha256_before': index_before, 'index_sha256_after': index_after,
    'index_unchanged_during_audit': True, 'cached_diff_empty': True,
    'commands': COMMANDS,
    'limitations': ['No new Git fetch, branch/index mutation, commit, push, GitHub write, build or broad test was performed.',
        'Existing origin/main is a local fetched reference; independent remote evidence comes from the retained owner-connector GET responses.',
        'Published README/status/plan/handoff and checkpoint are dated snapshots; later working documentation and worker notes are not part of this commit.',
        'No hosted outcome, sixty-worker closure, physical fidelity, whole-interface equality or release acceptance follows from this publication audit.']
}
output = REPORTS / 'A44-publication-audit.json.gz'
output.write_bytes(gzip.compress((json.dumps(report, indent=2) + '\n').encode(), mtime=0))
print(json.dumps({k: report[k] for k in ('observed_utc', 'remote_tree_entries', 'changed_paths', 'added_paths', 'modified_original_paths', 'changed_modes', 'all_original_files', 'unchanged_original_files', 'published_ledger_snapshot', 'working_ledger_snapshot')}, indent=2))
print(json.dumps({'preserved_groups': {k: v['count'] for k, v in preserved.items()},
                  'formats': dict(formats), 'report_sha256': sha256(output.read_bytes()),
                  'result': 'PASS'}))
