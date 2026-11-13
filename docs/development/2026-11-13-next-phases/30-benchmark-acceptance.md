# Assignment 30 — independent benchmark acceptance

Canonical agent `/root/w05_a30_benchmark_acceptance`; wave 5, assignment 30 of
this session's actual sixty-assignment/ten-wave scope. Owned only
`apps/standalone/tests/test_standalone_benchmark.py`,
`docs/STANDALONE_BENCHMARK_ACCEPTANCE.md`, and this note. No production, CMake,
shared-status changes or commits by this worker.

Read AGENTS, active handoffs/status/next steps, Session and profile contracts,
plan/atlas evidence boundaries and relevant M9 review. Agent29 froze the CLI,
literal musical workloads and report schema before metric assertions were
written. Root separately specified the source-manifest and build identity inputs.
The [maintained acceptance document](../../STANDALONE_BENCHMARK_ACCEPTANCE.md)
details the independent expectations and intended canonical CTest command.

## Exact source and tool identity

CWD `/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`; starting HEAD
`738162f0bc36f88f8c76268d04831862a8118d10`, tree
`915e55dc7c3ad022042b188498aa41f2a7f40795`, with concurrent uncommitted work.
HEAD alone does not identify the tested benchmark. The stable binary was built
by Agent29 against freshly compiled SDK-free core/Session inputs; this worker
independently rehashed every source-manifest entry and matched its report identity.

| Input | SHA-256 |
| --- | --- |
| Test script | `f3d9e1cc138034649ee65eeb860dce33a28f5139b32a523ee7cae3b59f8657b3` |
| `benchmark.cpp` | `b9da06f92ec90bfe85ed2a4443605125fee0821dc7a9602e414526ae8dc92f80` |
| `Session.cpp` | `247c6a63dc9bb6c4e60398b17779a2d985058563b8d981c5e06426eab977f6ae` |
| `Session.h` | `0eed6c82d0cf5ffbeb0206f6f9702a93ef5a75cde6fd669b2862705dc7af84a0` |
| Direct executable | `2aa2ecbbf429608110b24f894136cc1046c0ee6c21764aa83bc4c0bfd2c7358f` |
| Compiled profile | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |
| Sorted 54-file source manifest | `3d37c970f157d2a5c0d13d62c77c88c035fddb3ebcdacd6ea562d24ee7092dca` |

Observed toolchain: GNU 14.2.0 (Debian 14.2.0-19), C++20, Release/NDEBUG,
Linux/x86_64, no project sanitizers; Python 3.12.14. The profile has 4,545 bytes,
FNV-1a64 `bf38a44e8d31695a`, and retained authoring SHA-256
`49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83`.
The aggregate uses exact UTF-8 `path:sha256\n` records; its complete domain and
the actual binary build command are retained in [assignment 29](29-session-benchmark.md).

## Actual complete invocation and result

Root's canonical CMake wiring was pending. This command converted Agent29's
existing text manifest into the agreed JSON inside a private temporary directory;
the suite then verified the actual source bytes and exact direct-build metadata.

```sh
python3 - <<'PY'
import hashlib, json, os, subprocess, sys, tempfile
from pathlib import Path
repo = Path.cwd()
records = (repo.parent / 'a29-evidence/source-manifest.txt').read_bytes()
entries = [dict(zip(('path', 'sha256'), row.rsplit(':', 1)))
           for row in records.decode('utf-8').splitlines()]
with tempfile.TemporaryDirectory(prefix='hammond benchmark identity ') as temporary:
    manifest = Path(temporary) / 'source-manifest.json'
    manifest.write_text(json.dumps({'schema_version': 1, 'entries': entries,
        'source_manifest_sha256': hashlib.sha256(records).hexdigest()}), encoding='utf-8')
    environment = dict(os.environ, HAMMOND_SOURCE_DIR=str(repo),
        HAMMOND_STANDALONE_BENCHMARK_EXECUTABLE=str(repo.parent / 'build-a29-benchmark/hammond_standalone_benchmark'),
        HAMMOND_TEST_PROFILE=str(repo.parent / 'build-a29-benchmark/nominal.b3p'),
        HAMMOND_STANDALONE_BENCHMARK_SOURCE_MANIFEST=str(manifest),
        HAMMOND_STANDALONE_BENCHMARK_EXPECTED_CONFIGURATION='Release',
        HAMMOND_STANDALONE_BENCHMARK_EXPECTED_COMPILER_ID='GNU',
        HAMMOND_STANDALONE_BENCHMARK_EXPECTED_COMPILER_VERSION='14.2.0',
        HAMMOND_STANDALONE_BENCHMARK_EXPECTED_TARGET_SYSTEM='Linux',
        HAMMOND_STANDALONE_BENCHMARK_EXPECTED_TARGET_PROCESSOR='x86_64')
    result = subprocess.run([sys.executable,
        'apps/standalone/tests/test_standalone_benchmark.py', '-v'], env=environment, check=False)
    raise SystemExit(result.returncode)
PY
```

**PASS: 9/9 methods, 111 CLI invocations, exit 0, 2.792 seconds.** All three rates,
all five buffer choices (nine selected pairs), all four workloads, zero/nonzero
warmup, defaults, Unicode paths, bounded corrupt/oversized/Nyquist-invalid
profiles and stdout failures were exercised. Dense applies 25,600 commands per
100 measured calls; recovery separately applies 600 rearm notes, discards 25,600
controls and observes 100 each QueueFull/RecoveryPending/recovery/zero-frame flush.
Checks retain exact controls/holds, quiet output hashes, frame clocks, stage
boundaries, raw timing counts/min/max/sum, empirical quantile ranks and period
ratios. No elapsed interval is a speed pass/fail criterion.

The initial eight-method subset failed only a test-only expectation that help
must advertise `--help` itself (7 passed, 107 calls, 2.374 seconds). The frozen CLI
does not require that wording, so that assertion was removed; standalone-help
success and mixed-help rejection remain tested. Production bytes did not change.
No missing-input setup failure occurred. All mutated fixtures/private files use
`TemporaryDirectory`; the original compiled profile remained byte-identical.

## Handoff and limitations

Root must register and execute `test_standalone_benchmark` with SDL OFF and include
the binary in native test inputs. Canonical CTest and hosted platforms were not
executed by this worker at handoff. No hardware audio, SDL device callback,
deadline, latency, underrun, concurrency or physical-fidelity claim follows.
