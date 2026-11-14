# Independent calibration handoff review

## Decision and exact scope

**Accept the operational runbook and next-acquisition guide for their declared
software and planning scope. No blocking guide contradiction was found and no
guide, production or test repair is required by this review.** The independent
finite audit completed **19 project CLI processes**, checked the option spellings
of **24 documented commands** against eight actual help surfaces, and resolved
**58 relative Markdown links**. These counts are different kinds of checks and
must not be added into a purported test-suite count.

The reviewed guides are [CALIBRATION_RUNBOOK.md](../CALIBRATION_RUNBOOK.md) and
[CALIBRATION_NEXT_ACQUISITION.md](../CALIBRATION_NEXT_ACQUISITION.md). Assignment
56 owns this review and its [execution record](../development/2026-11-13-calibration/56-handoff-review.md).
Root owns shared current status, integration, actual dispatch accounting and
publication. This review neither completes the sixty-worker session nor qualifies
physical M8, native devices or the final hosted platform matrix.

| Frozen review input | Bytes | SHA-256 |
| --- | ---: | --- |
| Operational runbook | 20,527 | `ae7ceda3c211c571b03038d9aa6fe1d3e454faa49d23500e0e0e46407b6846af` |
| Next acquisition plan | 28,837 | `87e4ebb2c8edc86ada894fc1c4b968b4a1c00597d61e1b2633ad3210ccac814b` |

The actual executable source was a fresh private `git archive` of published
`d7f6100010eb4cdd028ec93000cd9e893ac6d190`, exact tree
`0140c737de4db28288b118744c2beef57976697f`. Its **1,023 files / 40,370,269 bytes**
were hashed before and after; the full extracted tree remained unchanged. The
acquisition guide was separately frozen from assignment 53's delivered bytes,
not falsely described as already present in that historical source tree. Root's
later shared-document checkpoint `eb490af` updates the current dispatch and
publication pointers; earlier observed counts are not unresolved findings.

## Practical entry points and packaging

The runbook gives a public clone URL and requires inspecting the selected
commit/tree. Historical local acceptance identifiers are described as review
context, with explicit instructions to use their published equivalents in a
fresh clone. Neither guide makes an agent's scratch path a setup dependency.
The acquisition plan explicitly identifies its inspected local source without
calling it current main or directing the reader to check out a private object.
This assignment inspected that navigation; it did not perform a new network clone.

The runbook's CMake recipe agrees with the actual build declarations: CMake
3.21+, a C++ project with C++20 target requirements, and Python 3.10+. The runtime
uses the Python standard library. CaptureTools configuration can happen before
native targets are built; the optional standalone/VST3 components retain their
separate dependencies. The actual install declarations require explicit
`CaptureTools` selection and `COPY` or an unset install mode, reject an existing
package leaf including a symlink, and disclose retained partial output after a
late copy failure. Default/custom data-directory and PowerShell prefix forms do
not silently assume that all users have a POSIX shell.

The inventory review derived counts from the CMake lists and checked that each
listed source input exists:

| Package | Independently inspected composition | Scope of this review |
| --- | --- | --- |
| CaptureTools | 10 modules + 8 data files + 21 documents + 16 demo files + notice + generated README = **57** | Declarative source inventory and installation behavior inspected; neither new guide is an extra payload file. |
| OfflineTools | 5 native executables + 2 plot scripts + 1 compiled profile + 15 fixture/catalog files = **23** | Existing target/preflight declarations and all fifteen fixture paths inspected. Required native outputs must be built. |

This worker did not configure, build, install, relocate or delete a package.
Assignment 50's [clean-setup review](CALIBRATION_CLEAN_SETUP.md) separately owns
its actual 57+23 co-installation and execution after private source/build removal.
The guides attribute that evidence correctly. The generator and legacy validator
retain their documented single-file exception; it is not extended to arbitrary
job/study scripts that import the other modules.

## Command and recovery decisions actually exercised

All child commands used CPython 3.12.14 on Linux with `-B -S`, an empty
`PYTHONPATH`, ASCII terminal encoding, Unicode/space source and output paths, and
a foreign working directory. Each invocation retained exit status, stdout and
stderr. No final command produced an unexpected outcome or traceback.

| Decision point | Independent observed result |
| --- | --- |
| All eight CLI help surfaces | Exit 0 and empty stderr; every option in 16 runbook commands and eight acquisition-plan commands exists on the respective actual help surface. |
| Completed failed comparison | Exit 1 creates the complete `failed` job report; saved bytes equal stdout. |
| Replay of that failed report | Exit 0 and `match`; saved and replayed engineering status both remain `failed`. Source and runtime contexts match. |
| Existing ordinary output | Exit 1, diagnostic and no stdout; the original complete report remains byte-identical. |
| Existing dangling output symlink | Exit 1; link target and same-API metadata remain unchanged, and no referent is created. |
| Missing output parent | Exit 1; no report or missing parent directory is created. |
| Invented corpus `--output` option | Usage exit 2; diagnostic, no stdout and no output file. The acquisition guide correctly states that corpus has no such option. |
| `--check-audio` without `--check-files` | Usage exit 2 with the dependency diagnostic. This follows the guides' usage-error rule. |
| Extra LF added to the saved report | Exit 1 rejects the noncanonical bytes before publishing a replay summary; original saved report stays unchanged. |
| Comment-only change in a separate copy of `capture_common.py` | Replay exits 1 with a complete `mismatch`, `same_runtime: true`, `same_tool_sources: false`; both engineering statuses stay `failed`. |
| Real closed stdout pipe with a passing job and fresh output path | Exit 1 with a diagnostic; the already published complete report remains `pass`. A fresh replay of that file exits 0 with `match`, preserving `pass`. |

The pipe had no reader before child launch, so the outcome does not rely on a
consumer winning a timing race. It exercises the documented difference between
file publication and later stdout delivery. It does not make those effects
atomic or prove every crash/filesystem recovery path.

One initial audit expectation was wrong: the harness expected admission exit 1
for the missing `--check-files` flag, whereas the CLI correctly reports usage
exit 2. Both guides already classify usage as 2. The first audit stopped after
15 project CLI processes, and its script, diagnostic and correction are retained
in the assignment record. The final 19-process run changed only that expectation;
its later noncanonical probe also explicitly appends one LF to guarantee distinct
bytes. No project or guide code was changed to obtain these outcomes.

## Physical and acquisition handoff

The acquisition plan's A1–A6 order agrees with the existing
[protocol](../CAPTURE_PROTOCOL.md) and [M0–M9 plan](../PLAN.md): actual subject and
permission/configuration records; qualified chain/clock and pilot; dry raw
observations; complete admission/splits; declared comparison and constrained
fitting; then separately owned downstream boundaries. It gives responsible roles,
artifacts, missing inputs and exit evidence without inventing a specimen,
permission, hardware value, repeat count or fidelity tolerance. Existing protocol
permission records are required inputs, not a new agent approval process.

The guide correctly separates implemented corpus JSON from proposed human
`corpus-index.csv`, `admission-report.md` and `split-lock.json` records. It retains
the v1 raw/support/derived meanings, actual boundary and load, physical scale and
clock uncertainty, complete control history and restoration of actual objects.
Its distinctions among declarations, inspected bytes, numerical results, exact
replay and physical acceptance remain intact.

Source-level checks confirm these important intake limits and semantics:

- Corpus: **512 captures**; job: **64 captures / 256 artifact references**;
  study: **eight jobs sharing one corpus**. A subset pass does not establish
  global independence or a complete campaign audit.
- Capture v1: **16 channels, 32 artifacts, 256 MiB per artifact, 512 MiB per
  manifest**. The guide preserves oversized originals rather than relabeling
  chunks as independent observations.
- Companion purposes map `fit` to v1 `fit`, `validation`/`final` to `held_out`,
  and `unassigned` to `unassigned`. Software does not establish the historical
  freeze or untouched final evidence.
- Metadata accepts the declared FLAC formats, but the present audio-admission
  set excludes them. A supported derivative does not bypass inspection of its
  unsupported raw files. This point was checked in source, not with an invented
  physical FLAC acquisition.
- Pair selection requires recorded captures and the same corpus purpose; policy
  role mapping and index pairing remain explicit. No implicit physical-unit
  conversion, alignment, resampling or model optimizer is supplied by these tools.

The next actual physical output is therefore an identified external-output pilot
archive with chain/clock, repeatability, uncertainty and disposition records.
The separate scanner G5 same-hertz failure remains visible, dry-organ evidence
precedes cabinet fitting, and 122/147 boundaries and rotor/effect ownership stay
separate. External MIDI, native semantic accessibility and typed registration
selection remain independently owned engineering work. This review does not
repeat the six workers' complete PDF reading or independently verify every atlas
citation or external source.

## Integration and remaining scope

Keep these guides linked from the current handoff and next steps. Maintain
source-specific test counts: the retained 103-suite historical platform source
and the new 106-suite source are distinct. Assignment 55 owns the latter's fresh
hosted matrix; this local command review supplies no Windows/macOS result.
Current dispatch/completion counts belong to the actual manifest and root's
shared updates, not to a stale sentence copied from an earlier checkpoint.

The standing AGENTS workflow remains concrete: inspect current source and
ownership, continue a dependency-ready task, retain exact evidence and failures,
update status/next steps/log/contracts, commit completed authorized work, inspect
concurrent advances, publish without force and verify the fetched remote identity.
These guide checks provide no instrument fidelity, real device/DAW, native
accessibility, licensing or signed-release qualification.
