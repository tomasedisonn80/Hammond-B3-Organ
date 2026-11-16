#!/usr/bin/env python3
"""A57 bounded read-only storage/recovery audit; writes only its own JSON receipt."""
import collections
import datetime
import gzip
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess


REPO = Path(__file__).resolve().parents[4]
assert REPO == Path('/workspace/scratch/177e78b1ac09/Hammond-B3-Organ')
ROOT = REPO.parent
REPORTS = Path(__file__).resolve().parent
SESSION = REPORTS.parent
BASE = '4aac394cde4da40906b615573a8779aee2d9a37a'
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
COMMANDS = []


def command(*args):
    COMMANDS.append(list(args))
    return subprocess.check_output(args, cwd=REPO, env=ENV, timeout=60)


def git(*args):
    return command('git', *args)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def identity(path):
    path = Path(path)
    s = path.lstat()
    assert stat.S_ISREG(s.st_mode), str(path)
    return {'path': os.path.relpath(path, REPO), 'bytes': s.st_size,
            'allocated_bytes': s.st_blocks * 512, 'sha256': sha(path.read_bytes())}


def tree(commit):
    rows = {}
    for raw in git('ls-tree', '-r', '-z', commit).split(b'\0'):
        if not raw:
            continue
        meta, name = raw.split(b'\t', 1)
        mode, kind, oid = meta.decode().split()
        rows[name.decode()] = {'mode': mode, 'type': kind, 'object': oid}
    return rows


def load(name):
    return json.loads((REPORTS / name).read_bytes())


def bound_local(path):
    path = Path(path).resolve()
    allowed = [REPO, ROOT / 'build-native', ROOT / 'baseline',
               ROOT / 'resource-work', ROOT / 'compatibility-work']
    assert any(path == base or base in path.parents for base in allowed), str(path)
    return path


def current_matches_head(path):
    path = Path(path)
    rel = str(path.relative_to(REPO))
    data = path.read_bytes()
    oid = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    return rel in head_paths and head_paths[rel]['object'] == oid


started = datetime.datetime.now(datetime.timezone.utc).isoformat()
head, head_tree, parent = git('log', '-1', '--format=%H%n%T%n%P').decode().strip().splitlines()
head_paths = tree(head)
index_path = REPO / '.git/index'
index_before = sha(index_path.read_bytes())
status_before = git('status', '--porcelain=v1', '--untracked-files=normal').decode().splitlines()

df_raw = command('df', '-B1', '--output=source,fstype,size,used,avail,pcent,target', '.').decode()
df = df_raw.splitlines()[1].split()
filesystem = dict(zip(['source', 'fstype', 'size_bytes', 'used_bytes',
                       'available_bytes', 'used_percent', 'mount'], df))
for name in ['size_bytes', 'used_bytes', 'available_bytes']:
    filesystem[name] = int(filesystem[name])
vfs = os.statvfs(REPO)
filesystem['statvfs_available_bytes'] = vfs.f_bavail * vfs.f_frsize
filesystem['statvfs_total_free_bytes'] = vfs.f_bfree * vfs.f_frsize
filesystem['available_gib'] = filesystem['available_bytes'] / 2**30
filesystem['df_and_statvfs_available_equal'] = filesystem['available_bytes'] == filesystem['statvfs_available_bytes']
owned_dirs = ['.', '../build-native', '../baseline', '../resource-work', '../compatibility-work']
for directory in owned_dirs:
    assert not (REPO / directory).is_symlink()
du_raw = command('du', '-x', '-B1', '-s', '--', *owned_dirs).decode()
directory_sizes = [{'path': name, 'allocated_bytes': int(size)}
                   for size, name in (line.split('\t', 1) for line in du_raw.splitlines())]
top_du = command('du', '-x', '-B1', '--max-depth=1', '--', '.').decode()

# Explicitly named root scratch artifacts observed in this session; no recursive
# walk of the parent workspace or other sessions/dependencies is performed.
root_names = '''atlas-001-084.txt atlas-085-168.txt atlas-169-252.txt atlas-253-336.txt
atlas-337-420.txt atlas-421-500.txt atlas.txt baseline-build.log baseline-configure.log
baseline-ctest.log final-code-inputs.json final-coherent-build.log final-coherent-ctest.log
final-workflow-inputs.json post-review-positive-tests.log prepublication-integrity-final.json
prepublication-integrity.json publication-manifest.json publication-payload.json
publication-whitespace-build.log publication-whitespace-ctest.log repair-prepublication-integrity.json
repair-publication-manifest.json repair-publication-payload.json staged-binary-transfer.json
wave3-candidate-build.log wave3-candidate-tests.log wave3-configure.log wave3-oracle-test.log
wave3-probe-configure.log wave3-upper-baseline-build.log wave3-upper-baseline-run.log
wave4-differential-configure.log wave4-differential-test.log wave4-gallery-capture.log
wave4-lifecycle-build.log wave4-lifecycle-configure.log wave4-lifecycle-test.log
wave4-repository-integrity.json wave4-resource-work-verification.log wave4-resources-build.log
wave4-resources-configure.log wave4-resources-test.log wave5-code-inputs.json
wave5-coherent-build.log wave5-coherent-configure.log wave5-coherent-ctest.log
windows-core-af2b747.log windows-repair-ctest.log windows-repair-inputs.json'''.split()
root_files = []
for name in root_names:
    path = ROOT / name
    s = path.lstat()
    assert stat.S_ISREG(s.st_mode)
    root_files.append({'path': '../' + name, 'bytes': s.st_size, 'allocated_bytes': s.st_blocks * 512})
footprint = {'directories': directory_sizes, 'named_root_files': root_files,
             'named_root_file_count': len(root_files),
             'named_root_file_logical_bytes': sum(x['bytes'] for x in root_files),
             'named_root_file_allocated_bytes': sum(x['allocated_bytes'] for x in root_files),
             'top_level_checkout_du': top_du.splitlines()}
footprint['owned_named_allocated_total_bytes'] = sum(x['allocated_bytes'] for x in directory_sizes + root_files)
footprint['scope_note'] = 'Named directories plus 50 explicitly named root files; parent directory metadata and unnamed files excluded. du does not follow symlinks or cross filesystems.'

new_objects = {}
for line in git('rev-list', '--objects', BASE + '..' + head).decode().splitlines():
    parts = line.split(' ', 1)
    new_objects[parts[0]] = parts[1] if len(parts) > 1 else ''
info = subprocess.check_output(['git', 'cat-file', '--batch-check=%(objectname) %(objecttype) %(objectsize)'],
    input=('\n'.join(new_objects) + '\n').encode(), cwd=REPO, env=ENV, timeout=60)
COMMANDS.append(['git', 'cat-file', '--batch-check=%(objectname) %(objecttype) %(objectsize)'])
blob_rows = []
for line in info.decode().splitlines():
    oid, kind, size = line.split()
    if kind == 'blob':
        blob_rows.append({'object': oid, 'bytes': int(size), 'path': new_objects[oid]})

# Inspect every new blob plus all changed path objects in both commits. This also
# covers reused old blob bytes newly placed at a changed path during the range.
changed_paths = collections.defaultdict(set)
commits = git('rev-list', '--reverse', BASE + '..' + head).decode().splitlines()
for commit in commits:
    for line in git('diff-tree', '--no-commit-id', '-r', '--raw', commit).decode().splitlines():
        meta, path = line.split('\t', 1)
        fields = meta.split()
        if fields[1] != '000000':
            changed_paths[fields[3]].add(path)
blob_ids = set(changed_paths) | {x['object'] for x in blob_rows}
magic_counts = collections.Counter()
native_hits = []
for oid in sorted(blob_ids):
    data = git('cat-file', 'blob', oid)
    magic = ('ELF' if data.startswith(b'\x7fELF') else
             'PE/DOS' if data.startswith(b'MZ') else
             'archive' if data.startswith(b'!<arch>\n') else
             'Mach-O' if data[:4] in [b'\xfe\xed\xfa\xce', b'\xce\xfa\xed\xfe',
                b'\xfe\xed\xfa\xcf', b'\xcf\xfa\xed\xfe', b'\xca\xfe\xba\xbe', b'\xbe\xba\xfe\xca'] else
             'PNG' if data.startswith(b'\x89PNG\r\n\x1a\n') else
             'gzip' if data.startswith(b'\x1f\x8b') else 'other/source/text')
    magic_counts[magic] += 1
    if magic in ['ELF', 'PE/DOS', 'archive', 'Mach-O']:
        native_hits.append({'object': oid, 'kind': magic, 'paths': sorted(changed_paths[oid])})
build_pattern = re.compile(r'(^|/)(build(?:-native)?|CMakeFiles|__pycache__)(/|$)|(^|/)(CMakeCache\.txt|build\.ninja)$|\.(o|obj|a|so|dylib|dll|exe|pdb|pyc)$', re.I)
build_path_hits = sorted({p for ps in changed_paths.values() for p in ps if build_pattern.search(p)})
git_storage = {'scope': BASE + '..' + head, 'commits': commits,
    'new_blob_count': len(blob_rows), 'new_blob_logical_bytes': sum(x['bytes'] for x in blob_rows),
    'largest_new_blobs': sorted(blob_rows, key=lambda x: x['bytes'], reverse=True)[:15],
    'inspected_changed_or_new_blob_count': len(blob_ids), 'blob_magic_counts': dict(magic_counts),
    'native_binary_magic_hits': native_hits, 'compiled_or_build_path_hits': build_path_hits,
    'count_objects': git('count-objects', '-v').decode().splitlines(),
    'limits': 'No assertion about every pre-base historical commit; PNG/gzip evidence is intentionally binary data.'}

routes = ['AGENTS.md', 'README.md', 'docs/PLAN.md', 'docs/STATUS.md', 'docs/NEXT_STEPS.md',
    'docs/DEVELOPMENT_LOG.md', 'docs/PRODUCT_HANDOFF.md', 'docs/PROJECT_GUIDE.md',
    'docs/BUILD.md', 'docs/MIDI_EXPRESSION_GUIDE.md', 'docs/STANDALONE_INSTALL.md',
    'docs/CAUSAL_CONTACT_GRID_GUIDE.md']
routes += [str((SESSION / p).relative_to(REPO)) for p in
    ['README.md', 'SCOPE.md', 'CHECKPOINT.md', 'assignments.json', 'WINDOWS_REPAIR_SCOPE.md',
     'reports/check_streaming_session.py', 'reports/baseline-qualification.json',
     'reports/coherent-qualification.json', 'reports/final-coherent-qualification.json',
     'reports/publication-source-qualification.json', 'reports/implementation-publication.json',
     'reports/windows-repair-qualification.json', 'reports/repair-publication.json']]
recovery = []
missing_links = []
link_count = 0
for rel in routes:
    path = REPO / rel
    item = identity(path)
    data = path.read_bytes()
    blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
    item['present_in_HEAD'] = rel in head_paths
    item['working_bytes_equal_HEAD'] = rel in head_paths and head_paths[rel]['object'] == blob
    recovery.append(item)
    if path.suffix == '.md':
        for match in re.finditer(r'\[[^\]\n]+\]\(([^)\s]+)\)', data.decode()):
            target = match.group(1).split('#', 1)[0]
            if not target or re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target):
                continue
            resolved = (path.parent / target).resolve()
            if REPO not in resolved.parents and resolved != REPO:
                continue
            link_count += 1
            if not resolved.exists():
                missing_links.append({'from': rel, 'target': target})
ledger_data = (SESSION / 'assignments.json').read_bytes()
ledger = json.loads(ledger_data)
assignments = ledger['assignments']
ledger_snapshot = {'sha256': sha(ledger_data), 'assignments': len(assignments),
    'accepted': sum(x.get('status') == 'accepted' for x in assignments),
    'status_counts': dict(collections.Counter(x.get('status') for x in assignments)),
    'wave_counts': dict(collections.Counter(x['wave'] for x in assignments)),
    'a57_record_present': any(x.get('number') == 57 for x in assignments),
    'strict_closure_claimed_by_this_audit': False}

archive_checks = []
for name in ['baseline-qualification.json', 'coherent-qualification.json', 'final-coherent-qualification.json']:
    receipt = load(name)
    for info in receipt['logs'].values():
        rel = info.get('path', info.get('log'))
        path = REPORTS / rel
        raw = gzip.decompress(path.read_bytes())
        archive_checks.append({'archive': str(path.relative_to(REPO)), 'raw_bytes': len(raw),
            'raw_sha256': sha(raw), 'receipt': name, 'receipt_hash_matches': sha(raw) == info['raw_sha256'],
            'root_raw_copy_exists': (ROOT / rel[:-3]).is_file(),
            'root_raw_copy_matches': (ROOT / rel[:-3]).is_file() and (ROOT / rel[:-3]).read_bytes() == raw})
windows_failure = load('windows-core-af2b747-failure.json')
for archive, receipt, expected in [
    (windows_failure['log'], 'windows-core-af2b747-failure.json', windows_failure['decoded_log_sha256']),
    ('windows-repair-ctest.log.gz', 'windows-repair-qualification.json', load('windows-repair-qualification.json')['ctest']['raw_sha256']),
    ('A20-raster-run1/report.json.gz', 'A20-raster-run1/compression.json', load('A20-raster-run1/compression.json')['raw_sha256'])]:
    path = REPORTS / archive
    raw = gzip.decompress(path.read_bytes())
    archive_checks.append({'archive': str(path.relative_to(REPO)), 'raw_bytes': len(raw),
        'raw_sha256': sha(raw), 'receipt': receipt, 'receipt_hash_matches': sha(raw) == expected})
for check in archive_checks:
    check['original_archive_bytes_equal_HEAD'] = current_matches_head(REPO / check['archive'])

qualification = load('windows-repair-qualification.json')
inventory_path = REPORTS / qualification['source_inventory']['path']
inventory_raw = gzip.decompress(inventory_path.read_bytes())
inventory = json.loads(inventory_raw)
source_mismatches = []
for rel, expected in inventory.items():
    path = bound_local(REPO / rel)
    if not path.is_file() or sha(path.read_bytes()) != expected:
        source_mismatches.append(rel)
source_recovery = {'receipt': 'windows-repair-qualification.json', 'files': len(inventory),
    'inventory_raw_sha256': sha(inventory_raw),
    'inventory_hash_matches_receipt': sha(inventory_raw) == qualification['source_inventory']['raw_sha256'],
    'working_source_mismatches': source_mismatches,
    'working_source_git_changes': git('diff', head, '--name-only', '--', *inventory.keys()).decode().splitlines(),
    'inherited_receipt': qualification['inherited_local_qualification'],
    'scope': 'Source and receipt identity only; no build/test rerun.'}

publication = []
for name in ['implementation-publication.json', 'repair-publication.json']:
    receipt = load(name)
    commit = receipt['commit']
    actual = git('log', '-1', '--format=%H%n%T%n%P', commit).decode().strip().splitlines()
    pub_tree = tree(commit)
    raw = gzip.decompress((REPORTS / receipt['published_manifest']['path']).read_bytes())
    manifest = json.loads(raw)
    entry_mismatches = [e['path'] for e in manifest['entries']
        if e['path'] not in pub_tree or pub_tree[e['path']]['object'] != e['sha'] or pub_tree[e['path']]['mode'] != e['mode']]
    publication.append({'receipt': name, 'commit': commit, 'tree': receipt['tree'], 'parent': receipt['parent'],
        'local_commit_tree_parent_matches': actual == [commit, receipt['tree'], receipt['parent']],
        'manifest_entries': len(manifest['entries']), 'manifest_entry_mismatches': entry_mismatches,
        'manifest_raw_sha256_matches': sha(raw) == receipt['published_manifest']['raw_sha256'],
        'receipt_present_in_HEAD': str((REPORTS / name).relative_to(REPO)) in head_paths,
        'remote_observation_scope': 'Existing receipt records prior API/fetch verification; A57 made no new network/ref mutation.'})

scratch_evidence = []
baseline = load('baseline-qualification.json')
for path, expected in [(ROOT / 'baseline/hammond_standalone', baseline['executable_sha256']),
    (ROOT / 'baseline/dry-organ.wav', baseline['baseline_pcm_sha256'])]:
    item = identity(path)
    item['receipt_hash_matches'] = item['sha256'] == expected
    item['retention'] = 'Original local bytes; scratch-only, not a durable executable/audio archive.'
    scratch_evidence.append(item)
raster = json.loads(gzip.decompress((REPORTS / 'A20-raster-run1/report.json.gz').read_bytes()))
for label, old in raster['identities']['binaries'].items():
    item = identity(bound_local(old['path']))
    item.update(label=label, receipt_hash_matches=item['sha256'] == old['sha256'],
                retention='Original named local binary; outside Git and not durable across scratch loss.')
    scratch_evidence.append(item)
for rel, expected in load('final-coherent-qualification.json')['binary_sha256'].items():
    item = identity(bound_local(REPO / rel))
    item.update(receipt_hash_matches=item['sha256'] == expected,
                retention='Current qualified binary in regenerable build tree; original bytes scratch-only.')
    scratch_evidence.append(item)
resource = load('A23-resources.json')['instrumented_execution']['binary']
item = identity(bound_local(resource['path']))
item.update(receipt_hash_matches=item['sha256'] == resource['sha256'],
            retention='Optional diagnostic scratch binary; committed generator and reports support regeneration.')
scratch_evidence.append(item)
dry = load('A30-compatibility.json')['dry_fixture']
for path, expected in [(ROOT / 'baseline/hammond_render', dry['before_renderer_sha256']),
                       (ROOT / 'baseline/nominal.b3p', dry['baseline_profile_sha256'])]:
    item = identity(path)
    item.update(receipt_hash_matches=item['sha256'] == expected,
                retention='Original baseline bytes retained locally; outside Git, scratch-only.')
    scratch_evidence.append(item)
item = identity(ROOT / 'compatibility-work/dry-organ.wav')
item.update(receipt_hash_matches=item['sha256'] == dry['after']['wav_sha256'],
            retention='Regenerable candidate fixture; exact whole-WAV bytes currently equal retained original.')
scratch_evidence.append(item)

gallery_prefix = 'examples/demos/upper-rack-material-v1/images/'
gallery = [x for x in head_paths if x.startswith(gallery_prefix) and x.endswith('.png')]
extracts = []
for reader, name in zip(load('atlas-reading-coverage.json')['readers'], root_names[:6]):
    raw = (ROOT / name).read_bytes()
    extracts.append({'path': '../' + name, 'bytes': len(raw),
        'reading_receipt_hash_matches': sha(raw) == reader['extract_sha256']})

head_after = git('rev-parse', 'HEAD').decode().strip()
result = {'schema_version': 1, 'agent': '/root/w10_a57', 'started_utc': started,
    'completed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'script_sha256': sha(Path(__file__).read_bytes()), 'cwd': str(REPO),
    'scope': 'Owned checkout plus four named sibling directories and 50 named root artifacts only; no other sessions or dependencies scanned.',
    'git_identity': {'head': head, 'tree': head_tree, 'parent': parent,
        'local_origin_main': git('rev-parse', 'origin/main').decode().strip(),
        'head_unchanged_during_audit': head_after == head,
        'index_bytes_unchanged_during_audit': sha(index_path.read_bytes()) == index_before,
        'initial_working_status_count': len(status_before)},
    'filesystem': filesystem, 'owned_footprint': footprint, 'git_storage': git_storage,
    'recovery_routes': recovery, 'recovery_local_file_links': {'checked': link_count, 'missing': missing_links,
        'scope': 'File targets in named recovery documents; anchor text and external URLs not audited.'},
    'ledger_snapshot': ledger_snapshot, 'archived_original_byte_checks': archive_checks,
    'source_recovery': source_recovery, 'publication_receipt_checks': publication,
    'scratch_evidence_checks': scratch_evidence, 'tracked_current_gallery_pngs': len(gallery),
    'gallery_working_pngs_all_equal_HEAD': all(current_matches_head(REPO / x) for x in gallery),
    'atlas_extract_checks': extracts,
    'retention_limits': [
        'Whole-interface 1:1 and physical/device/product gates remain separate; this is a storage/context audit.',
        'A20 retains its exact original report/mask and per-frame hashes. The passing run does not store all 96 paired raw raster buffers as an immutable image archive; a rerun is new evidence.',
        'Original scratch binaries and dry WAV are present, but committed hashes and recipes do not preserve their original bytes after scratch loss.',
        'Root reports all 13 repaired-source hosted jobs successful; this audit does not independently retrieve hosted state. Exact-source final hosted receipt and current-document refresh are root work in progress.',
        'Late uncommitted reports, active ledger/checkpoint and this audit need final root publication for durable Git recovery.',
        'No build, CTest, broad test, cleanup, source production edit, index/ref write, fetch or commit performed.'],
    'cleanup': {'needed': False, 'executed': False, 'proposed_deletions': [],
        'reason': 'Ample measured availability; preserve original evidence and avoid unnecessary churn.'},
    'commands': [x if len(x) < 30 else x[:5] + ['<505 paths from verified windows-repair-code-inputs.json.gz>']
                 for x in COMMANDS if x[:3] != ['git', 'cat-file', 'blob']],
    'repeated_blob_command': {'argv_template': ['git', 'cat-file', 'blob', '<object>'], 'count': len(blob_ids)}}
output = REPORTS / 'A57-storage-recovery.json'
output.write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'report': str(output.relative_to(REPO)), 'bytes': output.stat().st_size,
    'sha256': sha(output.read_bytes()), 'available_bytes': filesystem['available_bytes'],
    'owned_allocated_bytes': footprint['owned_named_allocated_total_bytes'],
    'new_blobs': len(blob_rows), 'new_blob_bytes': sum(x['bytes'] for x in blob_rows),
    'native_binary_hits': native_hits, 'build_path_hits': build_path_hits,
    'source_mismatches': source_mismatches, 'archive_mismatches': [x['archive'] for x in archive_checks if not x['receipt_hash_matches']],
    'scratch_hash_mismatches': [x['path'] for x in scratch_evidence if not x['receipt_hash_matches']],
    'missing_recovery_links': missing_links, 'ledger': ledger_snapshot}, indent=2))
