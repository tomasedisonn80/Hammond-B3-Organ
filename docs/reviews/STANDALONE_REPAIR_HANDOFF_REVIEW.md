# Independent final-repair and operational-handoff review

Assignment **59/60**, actual worker `/root/w10_a59_repair_handoff_review`,
logical wave 10 of `2026-11-13-next-phases`. This review passes for the exact
production/test bytes below. It found two remaining Release-selection defects
in copied build recipes; root corrected both. The review does not replace the
coordinator's fresh combined-source gate, hosted platform results, actual
package inspection or final sixty-assignment accounting.

Root extended this same actual assignment to review a subsequent workflow-oracle
repair and one Windows demo-fixture correction. Their final bytes are included
below; no additional worker is counted. The failed full-native and Windows
gates remain separate from the passing focused checks.

The only repository writes by this worker are this report and the
[assignment note](../development/2026-11-13-next-phases/59-repair-handoff-review.md).
Production repairs belong to the concurrent
calibration author; assignment 58 independently reviews those repairs and adds
one corpus regression. Assignment 55 owns the changed chapel test and guide.
Root owns shared documentation, integration, acceptance, commit and publication.

## Source and evidence boundaries

The original failure candidate is public
[`0085e338388f2c7516a7d455f11692b94e9451f4`](https://github.com/tomasedisonn80/Hammond-B3-Organ/commit/0085e338388f2c7516a7d455f11692b94e9451f4),
tree `19c763503f67e1f054d2d27b6ec3d8fca2e36474`. The reviewed calibration repair
is already published in
[`955fc4c41f74ada094f14fbaf386c943811e9050`](https://github.com/tomasedisonn80/Hammond-B3-Organ/commit/955fc4c41f74ada094f14fbaf386c943811e9050),
tree `70956d0f0e125d57abfbf1aed56460c067f8ef28`. These are different source
scopes. The later source also adds offline calibration work; the old 105-suite
result cannot qualify that changed combined tree.

At **2026-11-14 00:11:25.983720 UTC**, the inspected checkout had local merged
HEAD `85f544f0c3a96972e021db21b8b8cf58741e2951`, tree
`f0053a4634dff1f85b4459191b44ac200bb7dd4a`, with separately identified chapel,
corpus-test and documentation overlays. The coordinator preserved the remote
calibration implementation rather than publishing a competing duplicate fix.
The exact reviewed implementation/test identities are:

| File | SHA-256 |
| --- | --- |
| `tools/capture_audio.py` | `b1f6228932c15f6483808cbb36a407dcdd6919f5894439d93f8888b01d66113c` |
| `tools/capture_corpus.py` | `1c68ca13157f767847258ccb74f3a22f49cc1d56f323cddeebd52f3ab85ed5ba` |
| `tests/test_capture_audio_admission.py` | `871d5c71e8aa57d8e6f6daca14bbd2e0a3d09bf913e4468aaa197b4155faabf7` |
| `tests/test_capture_corpus_admission.py`, including assignment 58's one added method | `6fdbc511bfd96e9767c3dd78366c7abb75b061b263295c4fae62f0f051ac36f6` |
| `apps/standalone/native_tests/test_standalone_chapel.py` | `18c645a30d6909ba331eac1f31abe71d9c8ccfe3c611278998f65f9ee5824323` |
| `docs/CHAPEL_CONTROLS_ACCEPTANCE.md` | `334de427be4f57bda85ab54c2181518b1ebd3f515425f29929a323870ccae695` |
| Final `apps/standalone/native_tests/test_standalone_workflows.py` | `982d76999592838689f0918f8bb937d68082514158b64c1c9bcd94eca3856428` |
| Final `docs/STANDALONE_WORKFLOWS.md` | `fda4fd6564fb263ee83c4014db730371fbfd33c8403a5ba0686381eeb72524d2` |
| Root's final `tests/test_capture_demo.py` | `a0b5ed53d59ef91e224d477b5996ca1f7f594d8f3d4a7592559e0352bba03112` |
| Unchanged `cmake/InstallStandalone.cmake` | `5a81d2689300a6fb58cf91a232dcd17c9ffbee209f311471fe5ccde8baed7f19` |

Assignment 58's private qualification is public `955fc4c` plus only its corpus
test overlay, private Git tree `bff821cd872eccc7b3699d118bd49ad4214e89c0`.
Assignment 55's chapel qualification instead retains public `0085e33` plus
only the two chapel overlays; all other 892 archived files remain unchanged.
Neither limited qualification is described here as a build of the combined
live worktree.

Root subsequently committed the combined candidate locally as
`89c7f368660e62b059b763e164f5729565019ec4` and published the identical tree
`c2aee4e8ceb9bb945b255bb67388a7d6bab9f3f2` at
[`183fc9e2a5e1530787deb9a6bb823e8f6ef61c2e`](https://github.com/tomasedisonn80/Hammond-B3-Organ/commit/183fc9e2a5e1530787deb9a6bb823e8f6ef61c2e).
Its new combined Release gate is separate; root subsequently reports **110/110
in 130.339 seconds** for that frozen source. That is root's execution, not this
reviewer's rerun. The later workflow and demo-fixture repairs are not part of
that candidate and require their own affected checks.

Those two later test-source changes are now published at
[`6214032f3565f9e221fcf3988e33a22a73bb4ea8`](https://github.com/tomasedisonn80/Hammond-B3-Organ/commit/6214032f3565f9e221fcf3988e33a22a73bb4ea8),
tree `10f070c54d176571f1919d8141d24dd82db0e41c`. Root identifies the production,
CMake and installation payload as unchanged from `183fc9e`; the actual final
hosted/package audit remains assignment 60's separate responsibility.

## Windows capture portability: original failures and repair review

The actual [Windows core job](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43529788060/job/132244338459)
at `0085e33` retained **92/96** passing CTest suites. This reviewer independently
counted all **41 FAIL/ERROR records** in its decoded log. The four failed suites
have these distinct causes:

| Suite | Observed method outcome | Relevant defect |
| --- | --- | --- |
| `python_test_capture_audio` | 41 methods; five failures | Four typed error envelopes and one successful report contain CRLF where canonical LF is required. |
| `python_test_capture_audio_admission` | 62 methods; 24 failures, five capability skips | Twenty-three newline mismatches; one canonical-parent identity injection misses its intended path. |
| `python_test_capture_corpus` | 47 methods; one failure | The canonical pretty JSON is translated to CRLF. |
| `python_test_capture_corpus_admission` | 57 methods; ten failures, one error, six capability skips | Five missed reparse injections, three missed `lstat` injections, one missed unavailable-identity case, one same-size mutation observation failure, and one one-sided zero-device identity mismatch. |

The 313,955-byte normalized decoded log has SHA-256
`78a40143e8844b96ebffdd24136e870640d3a99208955dc84ff3186461ebe864`.
These are retained failures, not outcomes inferred from a workflow badge.
The calibration author's [portability report](CALIBRATION_HOSTED_PORTABILITY.md)
records the earlier corresponding native Windows/macOS failures and the actual
repair authorship.

The repair writes explicitly encoded UTF-8 to a real stream's binary buffer,
preserving LF without relying on terminal encoding or newline configuration.
Text-only redirects such as `StringIO` receive the same Unicode text. Both
paths check the write count and flush; a short write or failed flush cannot
silently succeed. Audio success and typed error envelopes use this writer.
Corpus success and contextual input-error text also use it. Parser usage/help
retain their separately documented human-readable behavior.

Fixture roots now resolve their existing temporary directory before constructing
paths targeted by metadata hooks. That makes hooks observe the same canonical
ancestor spelling as the producer on Windows short-name and macOS `/var`
aliases. Explicit interception assertions prevent a missed hook from becoming
a false positive. The zero-device fixture now changes both relevant observations.
No confinement, identity, reparse or failure-admission rule is relaxed.

The mutation issue is separate from a path alias. Its stream hook identifies
the actual opened file by device/inode, changes a real byte in place, then
explicitly advances mtime and observes the change. This tests detection of an
observable mutation without assuming that a tiny same-size write immediately
changes every native timestamp. The quiescent-input requirement remains; this
is not a hostile-filesystem or all-races guarantee.

### Independent preservation and stream checks

An AST comparison of the two public producer revisions passed. For audio,
all **28 existing non-main definitions**, imports and constants are unchanged;
the only added definition is `_write_utf8`, and only `main` changes. For corpus,
**37 unaffected definitions**, imports and constants are unchanged. The new
`_audit_loaded` helper is a separately identified concurrent refactor: concatenating
the public wrapper before its delegation with the helper body after its
docstring exactly reconstructs the old `audit_corpus` AST. All six metadata/root
objects and both mode flags are forwarded unchanged. The review therefore does
not conceal a parser, graph, identity or numerical-policy change behind the
portability description.

This worker executed **12 narrow checks** against the actual published writer
function ASTs, six per tool: real ASCII/CRLF `TextIOWrapper`, exact `StringIO`,
binary short write, text short write, binary flush failure and text flush failure.
The literal payload contains both `é` and `音`. All pass; failure probes preserve
their exceptions and do not claim successful output. These are helper-level
Linux checks, not complete CLI or native Windows executions.

Assignment 58's added method uses a valid Unicode input-root path and specimen
text, a Unicode missing-file diagnostic, cp1252/CRLF wrappers and `StringIO`.
It keeps constrained IDs valid and does not invent a Unicode field in the
corpus report. A real text-layer counterexample translates successful-report
LFs and fails to encode the rejected Unicode path. The earlier attempted
Unicode `session_id` correctly violated the ASCII-ID contract; assignment 58
retains that authored-fixture error separately and fixes the fixture without
relaxing the schema.

This reviewer inspected that final method and independently ran only it:

```sh
# From the immutable 955fc4c + one-test-overlay source, Python 3.12.14:
python3 -B tests/test_capture_corpus_admission.py \
  CorpusAdmission.test_unicode_inputs_and_rejection_match_stringio_and_legacy_bytes -v
```

It passed **1/1**, no skips, in **0.013 seconds** reported by unittest
(0.314 seconds process wall time). The test file's hash remained unchanged.
Assignment 58 owns the separate full four-suite gate and alias/mutation
counterexamples; this worker did not duplicate those whole suites.

### Later Windows demo-fixture failure

The following candidate, public `183fc9e`, actually passed all four capture
suites on Windows. Its separate full core gate retained **100/101 in 151.14
seconds**, because `python_test_capture_demo` failed one of 43 methods. The
retained 266,402-byte Windows log has SHA-256
`7579875c99f672d280fb87ad28da1125d6f3270140ac640a8284c5b6851497f0`.
This reviewer read that exact failure: `test_existing_dangling_symlink_is_preserved`
compared an observed `//?/C:/...` target with the originally requested `C:/...`
spelling. The producer had already raised `DemoError`, and the link-type check
had passed. The later absent-target assertion was not reached in that failure.

Root corrected only the fixture. It now retains the actual `readlink()` value
before calling the producer, then requires exact equality afterward. It also
checks before/after `lstat` device, inode, mode, size and mtime using the same
API. Producer rejection, symlink type and absent target remain mandatory. This
tests preservation of the object the OS actually created without demanding an
unpromised target-string normalization. No producer, schema or capability skip
was changed.

This reviewer inspected the diff and independently ran the single maintained
method against the exact final hash listed above:

```sh
python3 -B tests/test_capture_demo.py \
  DemoAcceptance.test_existing_dangling_symlink_is_preserved -v
```

It passed **1/1**, no skips, in **0.008 seconds** unittest time
(0.219 seconds process wall time), with unchanged test bytes. This is Linux
execution; the final actual Windows rerun belongs to assignment 60's platform
audit and is not inferred from it.
Root separately reports all **43/43** demo methods passed in 1.663 seconds and
a real relative-target negative control: the original fixture fails and the
corrected fixture passes for the same intended dangling target. Those are
root's retained checks, not additional executions by this reviewer.

## Chapel sampled-state oracle and preserved failure

The original frozen source's complete Release result is **105/105**. Its first
fully instrumented native group is **13/14**, with a real failed chapel suite.
This reviewer read the original failed-suite log and old assertion order.
For Upper D# / Lower G, bank A, expression zero, sampled holds progressed
empty → Upper 60 → Upper 60 plus Lower 64 → empty. The old assertion demanded
an additional Upper-only UI sample in the 100 ms between releases.

At the failure, earlier assertions had already checked process success, complete
controls, Save status, zero audio/session faults, zero output peak, delivered
events, two accepted On/Off commands and final sequence acknowledgments. The
following final-empty, non-smoke, canonical Save-byte and preserved-input checks
were **not reached for that failed case**. The original fixture deleted its full
JSON during cleanup; the failed log cannot recover that absent evidence. The
30,859-byte original native-gate log has SHA-256
`d2ab963c4a45c06940a0655993157be1bcbc4ce24c9ba8ddddb00575ed6afa66`.

The changed test respects the producer's changes-only coherent snapshots.
Every observed hold set must equal the literal note-command prefix identified
by its applied sequence. Applied/resolved sequences agree, progress monotonically
and do not exceed submission. All observations still require the complete exact
controls. For a paired script, relative to the acknowledged startup sequence,
the literal states are:

| Applied note-command prefix | Required held state |
| --- | --- |
| None | Empty |
| Upper On | Upper MIDI 60 |
| Upper On, Lower On | Upper MIDI 60 and Lower MIDI 64 |
| Lower Off also applied | Upper MIDI 60 only |
| Upper Off also applied | Empty |

The original **700 ms** single-manual and **900 ms** complete-pair scripts keep
their schedules. Two additional **650 ms** pair scripts omit the final Upper
release and require a final acknowledged Upper-only endpoint, with exactly two
On and one Lower Off commands. Both registrations/expressions receive this
endpoint check. The original pairs still require two On, two Off and final
empty holds. This makes ownership after Lower release mandatory without
demanding a UI observation in an incidental sampling interval.

All 22 cases retain the full controls, exact event counts, application error and
audio/session fault checks, positive or zero peak policy, joined empty shutdown,
canonical Save bytes and preserved input files. Final endpoint and file checks
now run before the sampled-prefix oracle. No production C++ was changed, no
existing duration increased, and the eight-second per-process / 90-second CTest
budgets remain unchanged.

The new failure wrapper copies at most 65,536 diagnostic bytes before temporary
cleanup, marks truncation or unavailable output, and retains the original
exception as its cause. This reviewer deliberately exercised **five cases**:
ordinary JSON, exactly 65,536 bytes, an over-limit payload with a forbidden tail,
invalid UTF-8 and a missing diagnostic file. All preserve the original failure
and the required bounded evidence. These are failure-helper probes, not SDL
application executions.

The reviewer inspected assignment 55's immutable focused logs: the changed test
passed **2/2 methods and 22 real exports/application invocations** on the original
Release binary in 19.526 seconds and on the original fully instrumented binary
in 23.466 seconds, without skips. The binary/source scopes are explicit. Its
fresh changed-test full 14-suite native sanitizer gate is a separate observation
owned by the [final integration review](STANDALONE_FINAL_INTEGRATION.md), not
an unchanged rerun that erases the first failure. No LeakSanitizer result is
inferred from those ASan/UBSan checks.

That fresh full native gate subsequently completed **13/14 in 115.05 seconds**.
The repaired chapel suite passed all 22 auditions; unchanged workflows failed
two exact sampled-hold-path assertions. Help missed the sampled second fresh
press/release pair, and target/octave ownership missed an empty interval before
the later Upper MIDI 72 press. Both stop at `assert_hold_path`; later per-case
note-count/control/file assertions are not thereby proven for those failures.
The log has no sanitizer diagnostic, which does not turn the failed acceptance
gate into a pass. Its 36,309 bytes have SHA-256
`2079aa51b33f0059a2767ad1c51f888665b3696a7e08469b98ed3910fe9b084c`.

### Independently reviewed workflow follow-up

The final workflow repair keeps the original 2600 ms target/octave script and
2000 ms Help script. Five new target endpoints require, in order, all three
original owners after returning to Upper; Lower 74 plus pedal 17 after Upper
release; pedal 17 after Lower release; empty after pedal release; and a fresh
Upper 72 at the retained octave. Three new Help endpoints require empty holds
while Help remains open, empty holds after Return and a suppressed repeat, then
a fresh Upper 60 after the original physical up. Their exact durations and
On/Off counts are retained in the [workflow contract](../STANDALONE_WORKFLOWS.md).

The helper checks literal complete controls and hold sets against applied
command prefixes, including the scoped Help/Escape releases. It enforces one
device start, exact final applied/resolved/submitted acknowledgment, monotonic
sequences and earliest applied-command times. Final musical state is checked
before the sample loop. Exact note counts, unchanged saved bytes and complete
controls are checked before the helper. Later assertion failures retain a
bounded diagnostic excerpt. The existing nine-second process / 90-second CTest
budgets are unchanged; the suite now has 25 real subprocesses.

This review independently exercised the actual frozen helper with **ten
synthetic oracle probes**. Three legal coalesced or final-only sample sets
were accepted. Seven deliberate corruptions were rejected: wrong Lower owner,
application before the scheduled press, backward sequence, incomplete final
acknowledgment, altered controls, multiple device epochs and loss of the original
Upper at a held endpoint. These probes do not import a production UI oracle,
launch SDL or reconstruct the original missing diagnostic JSON.

The reviewer inspected the final source and guide hashes. Assignment 55 reports
first-run focused results of **11/11 methods / 25 real processes**, no skips,
in **38.037 seconds Release** and **42.775 seconds ASan/UBSan**. Its final
complete native gate then passed **14/14 in 117.28 seconds**, exit zero, with
no skips or sanitizer diagnostics. Workflow acceptance ran all 25 processes,
and chapel acceptance ran all 22 auditions. The retained native-gate log has
SHA-256 `9c4d163aa53581631d19763e32ea678c82a4ddb3e1ec6db81e165f7f3f43928a`;
JUnit has SHA-256
`88b2614bd98da3d6c659ca64e15c9bc6e7756e21ecdfd2f8d3b3fd5323f3e6fd`.

That final gate uses an isolated CTest driver with verified unchanged compiled
outputs and frozen source-path substitution. All 14 originating commands,
working directories, configurations, environments, labels and timeout overrides
are preserved, with the original 1500-second default explicitly supplied.
The source inventory and all 213 built objects, five archives, ten runtime
executables and generated inputs remain unchanged across execution. Root also
independently inspected the registry comparison and zero-failure/zero-skip JUnit.
This is qualified ASan/UBSan native acceptance, with the previously documented
LeakSanitizer exclusion retained. It is not a whole combined calibration/core
sanitizer run or execution of a physical device.

Other exact sampled control/hold
path methods remain unchanged, and the guide explicitly limits this repair's
endpoint coverage. The single-epoch helper is not applied to the Audio restart.

## Operational handoff and concrete corrections

Read AGENTS, README, PLAN, current status/next steps/log, the standalone handoff,
calibration scope/handoff, app/install/CI contracts, and the relevant original
and repaired tests. The handoff now selects Release explicitly for its normal
build, app build and native-test input target. The hosted workflow already
selects Release before testing/installing that configuration.

Two copied recipes still used `cmake --build build-native --target ...` followed
by Release installation or Release-oriented use. Under Visual Studio or Ninja
Multi-Config, that first command ordinarily builds Debug; the correct installer
then rejects the unbuilt Release executable. This worker reported both defects;
root changed the app and install guide commands to include **`--config Release`**.
The install guide's inspected corrected SHA-256 is
`54cfe80cc4071aec1b95e40cc815b262c17f04d28e8d1e2a05497e0e52a06c74`.
Root also qualified the app's executable examples as single-configuration
paths and explained the `Release/` directory and Windows `.exe` suffix.
The final inspected app guide has SHA-256
`bddb315f1b56d0245d4095375dc545d6832a3e5e95ce9eef9639894faafe213a`.
During the workflow follow-up, this reviewer found the same omission in its
owned guide's Execute block. Assignment 55 added both `--config Release` to
the input build and `-C Release` to CTest. No new build option was invented.

The nine-file installation contract matches the CMake preflight/copy rules:
one selected executable and eight guide/notice/identity files. The configuration
guard precedes destination writes; it preserves the existing single-configuration
selection and rejects unknown multi-configuration names. This is source review
supported by the [actual multi-config audit](STANDALONE_MULTICONFIG_INSTALL.md),
not another installation executed by this worker. The two guide corrections
change installed metadata bytes, so final package inventories must use their
actual candidate bytes rather than repeat older archive hashes.

The [benchmark artifact](../../examples/benchmarks/standalone-session-matrix-v1/README.md)
continues to name public `649b12c`. This worker checked all **57** retained input
hashes against current files and recomputed their ordered fingerprint:
`5fd7837b44dbe8fd09bfbd9931c20065e29acfffee10f3adca1a622cb18b9bb8`.
All match. Its 60 old timing cases were not rerun or relabeled as current timing.
The [chapel demo](../../examples/demos/standalone-chapel-v1/README.md) continues to
name public `0085e33`. All **nine** selected source identities match that public
commit and the inspected current files. No new screenshot was captured here;
matching source identities do not turn the demonstration into physical-device,
accessibility or sound-fidelity evidence.

The standing rule remains explicit: inspect current scope/source/remote state,
continue dependency-ready work, retain failures and limits, run meaningful
checks against coherent inputs, update status/next steps/log and affected
contracts, then commit and guarded-push authorized work with observed remote
identity. Never force-push or invent participation. Root corrected “both current
tracks” to all active tracks, the historical pedal wording, and the assumption
that each six-assignment wave always uses exactly two synchronized batches.
Logical waves and the three-worker execution limit are now separate concepts.

## Executed checks, limits and next action

Reviewer tools were Python 3.12.14 and Git 2.52.0 on Linux. Private evidence in
`../a59-repair-handoff-review/` retains the exact source/document snapshot,
AST-preservation record, 12 writer cases, five failure-retention cases,
ten workflow-oracle probes, source-fingerprint checks and the two separately
executed one-method unittest logs. No full build,
complete native suite, hosted runner, physical device or package execution is
attributed to this reviewer. No producer/schema/runtime change was requested
after final-byte inspection.

Both owned Markdown files passed direct UTF-8, final-newline, CR/NUL and
trailing-whitespace checks; all **nine** local Markdown targets resolve.
Scoped `git diff --check` also passed. Direct file checks cover the untracked
reports that a normal Git diff alone would omit. The full assignment 55 report
was then read and found consistent with the reviewed source/result boundaries.

Root can accept this bounded review, then finish the actual final platform/package
audit and session closure. The 110-suite combined Release result and the separate
changed-test gates above each retain their own source identities; historical
counts must not be summed or applied to a changed source. Reconcile
final status and dispatch records only after every actual result is accepted,
run the strict sixty-complete checker then, and publish with expected-head
protection. Queued/cancelled macOS jobs remain unexecuted evidence, not passes.

After closure, concrete independent product work is external MIDI producer
ownership and note cleanup, a semantic native accessibility bridge for the
existing controls, and real-device/performer qualification. Fixed-preset
selection requires its own latch/interlock/Cancel behavior contract; documentary
tap export alone does not implement it. Preserve the scanner's unresolved
same-hertz gate, separate AO-28 and Leslie 122/147 dependencies, and the missing
measured-capture/held-out fidelity evidence in the [M0–M9 plan](../PLAN.md).
