# Contact-grid certificate transaction review

**A20: the additional transaction and semantic-forgery checks pass for the
recorded source.** A real closed-output-pipe defect was repaired. The final
source-bound runs pass **11/11 new adversarial methods** and **33/33 existing CLI
methods**, with no local skips. Numerical resource admission, native equivalence,
installation and hosted-platform results remain separate evidence.

The [receipt](../development/2026-11-16-conversion-material/reports/A20-transaction-receipt.json)
binds Python 3.12.14 on Linux, exact commands, logs and unchanged source bytes
before/after both runs. The new [test suite](../../tests/test_contact_grid_conversion_adversarial.py)
uses public conversion/encoding boundaries for semantic mutations. It does not
import candidate numerical helpers to construct expected numerical answers.

## Actual diagnostic-output defect and narrow repair

With the original CLI, an actual subprocess whose stdout reader was closed
returned **120**, despite taking the argument-refusal path. `_emit_refusal`
caught the initial broken-pipe error, but buffered text remained pending.
Interpreter shutdown retried that flush, changed the exit status and printed
an ignored `BrokenPipeError` to stderr. The
[original process observation](../development/2026-11-16-conversion-material/reports/A20-closed-stdout-initial.json)
retains the exact result and original CLI hash.

Root explicitly handed A20 the CLI after A14's accepted ownership ended. The
only production change closes the failed stdout stream inside that existing
`OSError` branch and suppresses the close operation's repeated flush error.
It uses the existing stream's close method without duplicating or remapping
file descriptors, and does not touch a working output stream.
A real subprocess regression uses a handshake to close the reader before the
CLI can attempt its refusal. The repaired result is **exit 2 with empty stderr**.
An unavailable pipe cannot receive the JSON diagnostic; the repair preserves
the operation's exit status and avoids a second shutdown failure. It does not
claim delivery to a closed sink.

Normal refusal output remains one bounded ASCII-safe JSON line. Successful
publication remains silent exit 0. All existing argument, provenance, path,
temporary-file, write/flush/fsync/recheck/replace and interruption tests pass.
The original source is also retained as an explicitly
[reconstructed exact-byte snapshot](../development/2026-11-16-conversion-material/reports/A20-cli-original-reconstructed.py):
reversing only this repair reproduces A14's recorded SHA-256 exactly. It is not
represented as a separately captured original file.

## Independent additional cases

The semantic cases alter otherwise well-shaped certificates, then require the
public encoder to refuse them. They cover duplicated edge/arrival/root labels,
reordered record arrays, reordered or split equality groups, repeated labels,
duplicate command ordinals, a different key index, altered final contact bits
and a missing maximum witness. Altered transport is refused even when its
SHA-256 is recomputed to match the forged text. Provenance rejects extra/missing
module paths, uppercase hashes and Boolean hash values. These complement A15's
exact numerical comparisons and A14's original CLI cases.

Separate real subprocesses verify ASCII diagnostics under ASCII-only stdio and
successful conversion using valid POSIX filenames containing undecodable bytes.
The latter concerns filesystem names, not admission of non-UTF-8 JSON.

The OS-signal journeys synchronize at the actual owned temporary acquisition,
after output fsync, and immediately after the actual replacement. The parent
sends one SIGINT to the identified child process. A preopened raw descriptor
acknowledges deferred delivery; it performs no codec lookup in the handler.

| Observed boundary | Exit | Destination | Owned temporary / descriptor count |
| --- | ---: | --- | --- |
| Acquisition, before fd/name return | 130 | Prior bytes unchanged | No temporary remains; before/after fd counts equal |
| After fsync, before replacement | 130 | Prior bytes unchanged | No temporary remains; before/after fd counts equal |
| After replacement, before commit bookkeeping | 0 | Complete accepted certificate | No temporary remains; before/after fd counts equal |

All three restore the original SIGINT handler. The POSIX signal and byte-filename
methods are explicitly skipped on other operating systems; Linux execution does
not establish their Windows equivalents. The closed-pipe and ordinary CLI tests
are portable test inputs, but their actual Windows/macOS outcomes await hosted
execution at the final source.

## Retained test-harness failures

The [initial adversarial run](../development/2026-11-16-conversion-material/reports/A20-adversarial-initial.txt)
had three failed assertions. Its closed-pipe wrapper initially omitted the tools
directory from `sys.path`, causing an import failure rather than exercising the
CLI. That wrapper was corrected.

The first signal-acknowledgment implementation used an ASCII text-file write in
the Python signal handler. It intermittently reentered the first ASCII codec
lookup while the ready marker was being written. The
[24-process observation](../development/2026-11-16-conversion-material/reports/A20-os-sigint-repetition.json)
retains three resulting temporary/fd leaks in the injected acquisition wrapper.
The [exception trace](../development/2026-11-16-conversion-material/reports/A20-os-sigint-trace.json)
and [context-exit cause](../development/2026-11-16-conversion-material/reports/A20-os-sigint-exit-cause.json)
identify `LookupError('unknown encoding: ascii')` before that wrapper returned
ownership. This was an instrumentation defect, not a second production signal
defect. Production's deferred handler only sets a Boolean. Raw-byte markers and
the preopened acknowledgment fd remove the test's reentrant codec operation.
The corrected journeys pass; no acquisition implementation was changed.

## What the certificate does and does not authenticate

A deliberate public-API negative control changes syntactically valid original
byte metadata and a trajectory-irrelevant source amplitude consistently. The
encoder accepts that reconstructed case, as the contract permits: it was not
given original raw bytes to authenticate. The CLI's actual bounded input read
owns that binding. Reconstruction is numerical consistency, not an independent
signature of original input data.

A separate [owned-temporary experiment](../development/2026-11-16-conversion-material/reports/A20-import-cache-probe.py)
and [observation](../development/2026-11-16-conversion-material/reports/A20-import-cache-probe.json)
demonstrate another provenance boundary. A copied numerical module was compiled
to a timestamp cache, then edited to a one-unit work cap while preserving its
size and timestamp. Python `-B` still read that valid old cache: the CLI accepted
the 91-unit example while hashing the edited source bytes. Removing only the
owned cache made the same copied source refuse at the one-unit cap. Repository
source and caches were not modified by this experiment.

Therefore source-file hashes describe the files read from disk; they do not
authenticate loaded bytecode or a hostile import environment. `-B` prevents
cache writes, not cache reads. Source-qualified reproduction requires trusted,
consistent source/import inputs, such as the fresh five-file installation
layout. No loader hardening or execution-authentication guarantee is added by
this review. The CLI still checks its four source files and contract before and
after conversion, as specified.

## Final source and handoff

| Input | SHA-256 |
| --- | --- |
| Original CLI | `604eae2c20fd4fc0e7f9d8604558f6d196cc808c7451642d963323bee3b90e6f` |
| Repaired CLI | `56b73884ab44fc0694a763e6ffd576590c613926bfbc42f60ad0491c2caa935c` |
| A19 numerical module tested | `eff387f8457040ea67400dcb378ee1c2049b604d7c862fd6ca683b52c8f93797` |
| New adversarial suite | `1fc0724282b3a2fd4b00f04a9046b849882a8f02f437be5184868939498006aa` |
| Frozen contract | `e5b4d26e9d74aef41fc5c6abe351597d43097da3faed5af6a26d0e3e557e18c0` |

The final new suite reports **11 methods in 0.792 s**, with **0.966 s** enclosing
process time. The unchanged original CLI suite reports **33 methods in 0.233 s**,
with **0.418 s** enclosing time. Each process had a 60-second external timeout;
these observed timings are not portable performance limits.

Root should retain this source repair with the exact affected receipts, combine
A19/A21 and installation evidence, and observe the final hosted source. No
CMake/build/install, commit or push was performed by A20. This remains an offline
synthetic trajectory utility, without an audio-accuracy or live-Engine claim.
