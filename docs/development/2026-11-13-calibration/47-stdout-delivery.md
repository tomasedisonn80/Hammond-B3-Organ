# Assignment 47 — CLI stream-delivery implementation

Actual worker: **`/root/cal_w8_a47`**, assignment **47**, logical wave **8**,
session `2026-11-13-calibration`. Work performed on **2026-11-14 UTC**. This
is one actual newly dispatched worker, distinct from independent acceptance
worker 46. No additional worker was spawned or counted by this assignment.

## Owned paths and result

Owned nine production paths, limited to the executable boundary and the shared
or local standard-library guard:

- `tools/capture_common.py`
- `tools/capture_audio.py`
- `tools/capture_corpus.py`
- `tools/capture_job.py`
- `tools/capture_readiness.py`
- `tools/capture_study.py`
- `tools/verify_capture_report.py`
- `tools/make_capture_demo.py`
- `tools/validate_capture.py` (explicitly added by root to preserve its standalone
  script behavior and original v1 validation/formatting)

Owned documentation is this note and
[CALIBRATION_STDOUT_DELIVERY.md](../../reviews/CALIBRATION_STDOUT_DELIVERY.md).
No maintained test, frozen public contract, CMake file, package inventory,
shared status, session manifest, unrelated track or Git ref was edited.
Root owns integration, commit and push. Worker 46 owns independent tests and
acceptance; its reported executions are not relabeled as producer executions.

**Result:** final independent pipeline acceptance passes **9 methods, 71 actual
child processes**, no failures/errors/skips, in **8.223 seconds**. The separately
repeated final demo regression passes **43/43**. Additional author probes pass
18 finite guard cases and eight actual standalone script invocations. The review
retains scope, causes, failures, cleanup boundaries and exact continuation.

## Source, scope and authorization

Read the standing repository instructions, current calibration scope/status,
next-step and handoff context, the M0–M9 plan and relevant frozen CLI contracts.
Consulted actual extracted atlas pages 449 and 484–486 for original identities,
retained failure outcomes, independent claims and change control. This worker
makes no additional complete-PDF reading claim; this session's six original
readers own its full 500-page coverage.

Root first froze accepted metadata-allocation source at:

- Local commit `459bfacbda90005d618f12c4513b9c71cb11193d`.
- Git tree `3325af558b040759c1b432ec0806a80785af9713`.
- Immutable archive `/workspace/scratch/c9f3ead4c910/w8-allocation-source`.
- Corpus source 39,312 bytes, SHA-256
  `751ce8e3d6a712ac8873c57aae9ab71311396921098e82b1d0fcd1720ffa9ded`.

This assignment waited for that checkpoint and worker 46's frozen matrix before
editing production. Root approved the narrow CLI-boundary proposal and later
preferred guarded closure of the actual failed original wrapper to a null-file
redirection approach. No null file, descriptor duplication, signal reset or
`os._exit` was used. Root explicitly expanded scope to the legacy validator
without changing its input semantics or standalone dependency closure.

Worker 46's frozen A46 marker block is 2,578 bytes, SHA-256
`02cc59e2b50151e06dcfbd7b68c99be1635a4a6c5de3a2fb6c63db4316814b43`.
Its original 24-process matrix is 26,452 bytes, SHA-256
`7053ec36d52898ec8fff131517fc6fbe53764b3d916f40c26957cb167cca8058`.
These remain unchanged. The maintained initial matrix separately executed seven
methods, 61 child processes and 24 failing subcases; these are different counts.

## Implementation reasoning

A CLI can catch a buffered write error and return 1, yet CPython later retries
those bytes and replaces its status with 120. Argparse help also may return before
its buffered text reaches the pipe. Explicitly flushing both streams at the real
executable boundary makes the result observable before `SystemExit`.

The guard records original stream objects, invokes the unchanged `main`, retains
ordinary integer statuses, and handles otherwise escaping `OSError` with the
module's own diagnostic form. Failed flushes return 1. It closes only a failing
exact original `io.TextIOWrapper` still installed as both the current and original
stdout/stderr and still naming descriptor 1/2. Healthy streams and replacements
remain untouched. Distinct retirement failures are retained beside the original
I/O reason. Existing one-line/JSON errors are not duplicated solely by final flush.

The actual original wrapper becomes closed even when its close operation repeats
the same `BrokenPipeError`. Its underlying standard descriptor remains valid and
process-owned; the helper does not redirect or explicitly close that OS descriptor.
The successful process-level evidence concerns avoiding another buffer flush
on an already closed wrapper. It is not a new arbitrary-OS-cleanup guarantee.

The helper catches no cancellation, `ValueError`, `TypeError`, `RuntimeError` or
noninteger caller `SystemExit`. All existing public function/class and `main`
bodies are unchanged, as verified through 228 exact AST comparisons across the
ten modules. The metadata size-plus-one read remains unchanged. Numerical
metrics, admission bounds, reports and no-clobber publication were not loosened.

Audio/readiness retain JSON error envelopes. Other CLIs retain their contextual
prefixes, and demo generation retains its explicit completed-archive message.
Output failure cannot retract bytes already delivered or remove a completed file.
If stderr also fails, no secondary diagnostic can be required.

## Review findings and corrections retained

### Generator standalone dependency

The first candidate routed the generator executable through a sibling
`capture_common` import. Root correctly found the frozen demo requirement that
no capture-tool module be imported. The independent existing demo suite exposed
that defect too: 42/43 passed, with
`test_generation_uses_only_standard_library_imports` failing. A subsequent
extended independent probe retained five failing no-sibling invocations.

The final generator embeds the identical local stdlib-only guard instead. Its
source changed from 22,488 bytes, SHA-256
`0ae33518681f0c627f165daf287de8a25afad24e6ddee74bbb731c2599a80dd3`, to
25,734 bytes, SHA-256
`67a49b81f009677a7d2ac62c7f6b95a50e5dd885dca0cc2ac04ca42655f79535`.
The final common, generator and validator guard ASTs are identical. No expectation
or frozen contract was changed. Actual no-sibling generation still reproduces all
sixteen original files, 32,831 bytes, exactly.

A preliminary explanatory validator comment incorrectly described that script as
part of the older OfflineTools package. Root's direct inventory inspection corrected
that assumption before final candidate acceptance. The validator remains a
standalone stdlib script and is in the ten-module CaptureTools closure; the separate
23-file OfflineTools inventory was never changed. The comment-only correction did
not change execution.

### Author probe's descriptor-ownership assumption

The initial 7,960-byte author guard harness, SHA-256
`b93954e27216e778dbdab5103e6a91bb8949b5759bc3f757e7ab71fbb42ed7ff`, failed
one assertion after observing this actual JSON in a fresh closed-stdout process:

```json
{"status": 1, "failed_closed": true, "opposite_closed": false, "descriptor_closed": false}
```

The harness had incorrectly expected `descriptor_closed` true. The intended repair
retires the buffered wrapper while retaining the standard descriptor's process
ownership. Only that expectation/label changed; the producer did not change for
this observation. The original harness and recorded failure remain under
`a47-stdout-delivery` in scratch. The corrected final harness is reproduced below.
It passes all eighteen finite cases. Its close-error fault explicitly restores
ordinary closing before final process exit, so that case does not claim production
exit 1 if a real runtime prevents stream retirement.

## Actual commands and observations

All repository-directed commands ran from
`/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`. The runtime was CPython
3.12.14, Linux x86_64. Fresh subprocesses used `-B -S` and
`PYTHONIOENCODING=ascii:strict`. The expected pipe failure was deterministic:
its read descriptor was closed before starting the child.

The author independently copied all ten before-source modules to
`/workspace/scratch/c9f3ead4c910/a47-stdout-delivery/before-tools`. For each of
eight CLIs, a help command used closed stdout and a missing-input/destination
command used closed stderr. Every one of sixteen original processes returned 120.
The first repaired sixteen-process probe returned 1 for every case without writable
stderr traceback/finalizer warnings. The complete observations and identities are:

| Scratch evidence under `a47-stdout-delivery/` | Bytes | SHA-256 |
| --- | ---: | --- |
| `before-probe.json` | 5,538 | `92cc7b04c70690a928aa543a14d82c7658dabce030987bd97d51decf045a9f89` |
| `candidate-probe.json` | 4,870 | `f56949ca9a0745b906f43bd8a425c1ac1a57f7f7540b708a70b2cc50cb602a93` |
| `final-inventory.json` | 1,324 | `27f5a65f4bd69f52dc5dfeba52d49f2039221954203eeafc6a357655672f1f4b` |
| `boundary_probe.py` | 8,028 | `74b248ceff2e4eeb7173d4f7f84d5e1eafb5f25e9957dde480209e9986670fe4` |
| `boundary-probe.json` | 3,285 | `a97a6b294d8b04246d9bc55a7c250491eed2006c8859408677b234f1c3567d06` |
| `standalone-probe.json` | 6,184 | `7851cd113640d4cf1606e92b018c4d5113ca4bc7fba87d95773df18200643445` |

The first repaired probe predates the generator dependency correction and the
validator's explanatory comment correction. It is preserved as a preliminary
observation; the independent final 71-process result qualifies the final source.
The author guard and standalone probes use the final ten-module copy at
`a47-stdout-delivery/final-tools`.

Actual final guard command:

```sh
python3 -B /workspace/scratch/c9f3ead4c910/a47-stdout-delivery/boundary_probe.py
```

Result: 18/18 finite cases, zero unexpected failures. Four cases use actual fresh
interpreter children. Additional standalone commands copied only one generator
or validator script into each source directory, then executed its normal help,
closed-stdout help, successful generation/validation, and rejected input with
closed stderr. Eight actual invocations passed; imports were stdlib-only and the
regenerated archive was byte-identical. Those operations used explicit private
paths and no source checkout fallback.

Worker 46's maintained suite command has this ordinary repository form:

```sh
python3 -B tests/test_capture_cli_pipeline.py
```

Its actual acceptance ran against independently frozen private source copies.
Final test identity: 22,054 bytes, SHA-256
`bfff3005af05ede0b48258de9be1b1560384f6fec618fa6b29aad6dc75d41cb6`.
Final result: 9/9 methods, 71 child processes, 8.223 seconds, no failures/errors/skips;
59,263-byte result SHA-256
`c65213f8baf1a0e23d11acc945607ce232aa719beb4bde94c503f4b16e4fa3e4`.
Final demo regression: 43/43, 1.346 seconds; 4,518-byte result SHA-256
`4ae3233e2d70825a5f912b2582fb1f9cbacdf4ad286f063167e716162c2cf14e`.
Its ten other existing suites pass on identical consumed source bytes: 576 methods,
including two explicitly skipped audio-capability methods. With the final demo,
that is 619 existing methods, 617 passed and 2 skipped. These are independently
reported executions, not reruns or new unittest methods by assignment 47.

## Final complete source identity

The final ten-module copy was verified against live source before independent
acceptance. Only the nine owned modules differ from the identified before source;
`compare_capture.py` remains unchanged. These uncommitted working-source hashes,
not an older HEAD alone, identify the tested candidate. Root records the eventual
commit, complete tree and publication.

| Module | Bytes | SHA-256 |
| --- | ---: | --- |
| `capture_audio.py` | 30,313 | `f6f059a81078982d1061637c84836bef9564d51215cb37e0c120046ba0d7b216` |
| `capture_common.py` | 12,774 | `f583dbfde3d164157d7e5aa1c601878e3f7d44b4eb7fb059426b92045ac793ab` |
| `capture_corpus.py` | 39,476 | `baf4aac2fc87e322d2e5d663f4de9da8118559100ad7de1e6f77feba606779a8` |
| `capture_job.py` | 24,433 | `a12645460b4c35400e5f851ac61f7bf273741a3c8d249ee186e93c46ba43a92b` |
| `capture_readiness.py` | 11,630 | `816ae53470e54c428cf53bbcf566ddf9a46ad422e427f3bfb28d9b47ca7e64e1` |
| `capture_study.py` | 16,849 | `5147b3f7b959ff6e2e1c7ca4b49154579a212af1cf2604bb6272fd9a212f5f98` |
| `compare_capture.py` | 33,448 | `220a593499539db5f1e635db2eb15ba3c0aa7c6d001c80407fbffe93f75a9a0a` |
| `make_capture_demo.py` | 25,734 | `67a49b81f009677a7d2ac62c7f6b95a50e5dd885dca0cc2ac04ca42655f79535` |
| `validate_capture.py` | 28,237 | `f17ac8e24c98c792364bfdcc10c41bf410853ba19654eaa36482596d5881f3aa` |
| `verify_capture_report.py` | 23,489 | `6c100e976cbe9fa4748a66fe7c6a9488f4e87b4227edc2d88ddf83913b8e91ba` |

The generator's retained sixteen-file archive and all fixed numerical expectations stay
unchanged. Fresh execution reports legitimately observe new tool-source hashes.
Older saved reports and allocation artifacts must remain original; a changed-source
replay difference is visible context, not permission to rewrite an old result.

## Handoff and limits

Independent worker46 and root should inspect the final source/review identities,
then root integrates these eleven owned paths together with the maintained regression,
its separately owned installation-test repair and later accepted work. Run an
appropriate coherent final source gate, observe fresh hosted platform outcomes,
update shared status/next steps/log, commit/push and verify the fetched remote head
without force. The original failures and the generator-contract correction stay
in the acceptance record.

The three guard copies intentionally preserve standalone closures; future changes
must review their common semantics and actual isolated behavior. A nonstandard
interpreter stream, custom replacement, changed original object/descriptor, or
runtime that prevents closing remains outside the observed retirement guarantee.
The distinct-close-error probe preserves context and explicitly does not promise
an exact process status when that retirement is impossible. There is no crash
atomicity, hostile-filesystem, native Windows/macOS, latency, callback, physical
acquisition, calibrated-scale, rights, holdout or fidelity qualification here.

## Complete final author guard harness

The following exact harness bytes, including the final LF after its last line,
reconstruct the 8,028-byte file identified above. Its two module directories
must match the before/final inventories; it writes only private scratch output.

```python
"""Finite author probes of the exact ready CLI guard; no repository mutations."""
import ast
import contextlib
import errno
import io
import json
import os
from pathlib import Path
import subprocess
import sys
from unittest import mock

BASE = Path(__file__).resolve().parent
TOOLS = BASE / "final-tools"
sys.path.insert(0, str(TOOLS))
import capture_common as common
import validate_capture as legacy

outcomes = []


def record(name, detail):
    outcomes.append({"case": name, "passed": True, "detail": detail})


count = 0
module_counts = {}
for old_path in sorted((BASE / "before-tools").glob("*.py")):
    old = ast.parse(old_path.read_text())
    new = ast.parse((TOOLS / old_path.name).read_text())
    definitions = {node.name: node for node in new.body
                   if isinstance(node, (ast.FunctionDef, ast.ClassDef))}
    checked = 0
    for node in old.body:
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            assert ast.dump(node, include_attributes=False) == ast.dump(
                definitions[node.name], include_attributes=False), (old_path.name, node.name)
            count += 1
            checked += 1
    module_counts[old_path.name] = checked
record("existing definition ASTs unchanged", {"total": count, "modules": module_counts})
guards = []
for name in ("capture_common.py", "validate_capture.py", "make_capture_demo.py"):
    tree = ast.parse((TOOLS / name).read_text())
    guards.append(ast.dump(next(n for n in tree.body if isinstance(n, ast.FunctionDef)
                                and n.name == "_cli_exit"), include_attributes=False))
assert guards[0] == guards[1] == guards[2]
record("shared and standalone guards identical", True)

for status in (0, 1, 2, 3):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        value = common._cli_exit(lambda: status, lambda message: print(message, file=sys.stderr))
    assert value == status and not out.closed and not err.closed
    assert out.getvalue() == err.getvalue() == ""
    record(f"healthy custom streams preserve status {status}", True)


class FailedCustom:
    def __init__(self):
        self.close_calls = 0
        self.fileno_calls = 0

    def flush(self):
        raise BrokenPipeError(errno.EPIPE, "private custom stream")

    def fileno(self):
        self.fileno_calls += 1
        return 1

    def close(self):
        self.close_calls += 1


for name in ("stdout", "stderr"):
    failed = FailedCustom()
    other = io.StringIO()
    with mock.patch.object(sys, name, failed), mock.patch.object(
            sys, "stderr" if name == "stdout" else "stdout", other):
        value = common._cli_exit(lambda: 0, lambda message: print(message, file=sys.stderr))
    assert value == 1 and failed.close_calls == failed.fileno_calls == 0
    assert not other.closed
    if name == "stdout":
        assert "private custom stream" in other.getvalue()
    record(f"failed custom {name} remains caller-owned", True)


class FakeRaw(io.RawIOBase):
    fail = True

    def writable(self):
        return True

    def write(self, value):
        if self.fail:
            raise BrokenPipeError(errno.EPIPE, "private raw stream")
        return len(value)

    def fileno(self):
        return 1


raw = FakeRaw()
text = io.TextIOWrapper(io.BufferedWriter(raw), encoding="utf-8")
text.write("retained custom bytes")
err = io.StringIO()
with contextlib.redirect_stdout(text), contextlib.redirect_stderr(err):
    value = common._cli_exit(lambda: 0, lambda message: print(message, file=sys.stderr))
assert value == 1 and not text.closed and not raw.closed and not err.closed
assert "private raw stream" in err.getvalue()
raw.fail = False
text.close()
record("replacement TextIOWrapper claiming descriptor1 is not retired", True)

for error in (KeyboardInterrupt("cancel"), SystemExit("caller exit"),
              ValueError("programming value"), TypeError("programming type"),
              RuntimeError("programming runtime")):
    def entry():
        raise error
    out, err = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            common._cli_exit(entry, lambda message: print(message, file=sys.stderr))
    except BaseException as caught:
        assert caught is error
    else:
        raise AssertionError("primary exception was swallowed")
    assert not out.closed and not err.closed and out.getvalue() == err.getvalue() == ""
    record(f"preserve primary {type(error).__name__}", True)


def child(source, closed=None):
    prefix = f"import sys; sys.path.insert(0, {str(TOOLS)!r})\n"
    read_fd = write_fd = None
    if closed:
        read_fd, write_fd = os.pipe()
        os.close(read_fd)
    try:
        result = subprocess.run([sys.executable, "-B", "-S", "-c", prefix + source],
            stdout=write_fd if closed == "stdout" else subprocess.PIPE,
            stderr=write_fd if closed == "stderr" else subprocess.PIPE,
            env=dict(os.environ, PYTHONIOENCODING="ascii:strict"))
    finally:
        if write_fd is not None:
            os.close(write_fd)
    assert result.returncode == (1 if closed else 0), result
    surviving = result.stderr if closed == "stdout" else result.stdout
    assert b"Traceback" not in surviving and b"Exception ignored" not in surviving
    return json.loads(surviving)


for name in ("stdout", "stderr"):
    source = f'''import capture_common as c, json, os, errno
def entry():
    sys.{name}.write("pending data\\n")
    return 0
def diagnostic(message):
    pass
status = c._cli_exit(entry, diagnostic)
try:
    os.fstat({1 if name == "stdout" else 2})
    descriptor_closed = False
except OSError as error:
    descriptor_closed = error.errno == errno.EBADF
print(json.dumps({{"status": status, "failed_closed": sys.{name}.closed,
    "opposite_closed": sys.{"stderr" if name == "stdout" else "stdout"}.closed,
    "descriptor_closed": descriptor_closed}}), file=sys.{"stderr" if name == "stdout" else "stdout"})
raise SystemExit(status)
'''
    result = child(source, name)
    assert result == {"status": 1, "failed_closed": True,
                      "opposite_closed": False, "descriptor_closed": False}, result
    record(f"real failed original {name} stream retired with standard descriptor still process-owned", result)

result = child('''import capture_common as c, json
status = c._cli_exit(lambda: 0, lambda message: None)
print(json.dumps({"status": status, "stdout_closed": sys.stdout.closed,
                  "stderr_closed": sys.stderr.closed}))
raise SystemExit(status)
''')
assert result == {"status": 0, "stdout_closed": False, "stderr_closed": False}
record("healthy original standard streams stay open", result)

result = child('''import capture_common as c, json, errno
original_close = sys.stdout.close
def injected_close():
    raise OSError(errno.EIO, "private close failure")
sys.stdout.close = injected_close
messages = []
def entry():
    sys.stdout.write("pending data\\n")
    return 0
status = c._cli_exit(entry, messages.append)
still_open = not sys.stdout.closed
sys.stdout.close = original_close
try:
    sys.stdout.close()
except OSError:
    pass
print(json.dumps({"status": status, "still_open_after_injection": still_open,
                  "messages": messages, "finally_closed": sys.stdout.closed}), file=sys.stderr)
raise SystemExit(status)
''', "stdout")
assert result["status"] == 1 and result["still_open_after_injection"]
assert result["finally_closed"] and len(result["messages"]) == 1
assert "Broken pipe" in result["messages"][0] and "private close failure" in result["messages"][0]
record("distinct close failure retains primary and cleanup evidence", result)

output = {"python": sys.version, "cases": outcomes,
          "passed": len(outcomes), "unexpected_failures": 0}
target = BASE / "boundary-probe.json"
target.write_text(json.dumps(output, indent=2) + "\n")
print(json.dumps({"cases": len(outcomes), "passed": len(outcomes)}))
```
