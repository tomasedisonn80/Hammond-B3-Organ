# Chapel control-file acceptance

The [exporter](CHAPEL_CONTROLS.md) is independently qualified for copying the
atlas's eighteen documentary registrations into existing nominal drawbar controls.
This evidence covers exact files, rejection/preservation and actual C++ loading,
Save and note release. It does not establish factory sound, measured transformer
gains or physical fixed-key latching. Source Table IV and specimen wiring remain
independently unverified; see the [catalog](CHAPEL_PRESETS_CATALOG.md).

## Independent oracles

The [SDK-free suite](../tests/test_chapel_controls.py) contains literal rows from
[source reading B](research/CHAPEL_PRESETS_SOURCE_B.md) and a literal
[B3CONTROLS3 grammar](CONTROL_STATE_FORMAT.md) template. Producer constants,
private validators and serialization are not expected-value oracles. The actual
compiler generates a private prerequisite catalog whose complete hash and size
must match the independently accepted fixture. Each suite checks source stability.

| Key | Upper, nine digits | Lower, nine digits |
| --- | --- | --- |
| C# | `005320000` | `004545440` |
| D | `004432000` | `004423220` |
| D# | `008740000` | `007373430` |
| E | `004544222` | `004544220` |
| F | `005403000` | `006644322` |
| F# | `004675300` | `005642200` |
| G | `005644320` | `006845433` |
| G# | `006876540` | `008030000` |
| A | `327645222` | `427866244` |

Every allowed upper/lower/off combination is exported through the real CLI in
both A and B: **198 exact files**. All 162 digits, including leading zeros,
therefore appear in both bank positions. Selected rows occupy the chosen bank;
other banks are zero. Off manuals have both banks zero and route disabled.
Both selected-bank labels agree; pedals are zero and percussion is explicitly
Off / Second / Normal / Slow. Files contain eleven LF lines and 73 tokens,
including final LF, with no notes, preset identity, phase or transient history.

Seven expression vectors have literal expected tokens, including `0.1` becoming
`0.10000000000000001`, `0.9` becoming `0.90000000000000002`, and the longest
64-character permitted fractional token becoming `1e-62`. Defaults, omitted
manuals, `--name=value`, help and Unicode/space paths have separate checks.

## Admission and publication

The maintained suite rejects wrong/missing/extra fields, wrong types, forged
review hashes/counts and canonical authoring hashes. Every one of the 162 taps
is separately altered to another in-range value with the canonical hash updated;
documentary semantic admission must still reject. Raw authoring hash/count are
declared metadata whose shape is checked, not authentication of absent raw bytes.

Malformed, duplicate, trailing, invalid UTF-8/BOM, float/nonfinite and deeply
nested JSON reject. The 65,536-byte input boundary is exercised on both sides.
CLI tests reject missing, repeated, unknown or abbreviated options and invalid
keys/banks/expression syntax. Existing regular files, directories, symlinks,
dangling links, input aliases, hardlinks and invalid parents remain untouched.
Missing, directory and FIFO inputs reject. Public writer tests reject forged
audition text, noncanonical numbers/line separators and changed catalog content.

Five injected failures cover temporary creation, short write, flush, fsync and
hardlink publication. A sixth probe creates a competing destination immediately
before publication and proves it survives. Whole-fixture snapshots verify input
and destination contents, types, modes and inode identities and detect leaked
temporaries. Publication requires hardlink support. These pre-publication checks
do not promise rollback after successful publication followed by cleanup failure,
hostile filesystem races or power-loss durability. On Linux all fixture cases ran;
a host unable to create symlinks reports an explicit skip for that fixture only.

## Actual native application evidence

The [native suite](../apps/standalone/native_tests/test_standalone_chapel.py)
requires `HAMMOND_STANDALONE_EXECUTABLE`; absence is a prerequisite error, never
a skipped pass. It sends actual `--state`, `--input-script` and `--diagnostics`
arguments to the built SDL application with dummy audio and video drivers.
It executes all eighteen individual registrations across alternating A/B banks,
plus four paired-manual cases: two complete releases and two held endpoints.
Every case observes successful Save status, exact acknowledged controls, original
note ownership, the exact accepted note-on/release counts, no faults/errors/
overflow/recovery, and finite unclipped copied output. All cases require joined
shutdown with empty holds. The eighteen single-manual and two complete-release
cases also require an empty final acknowledged snapshot before shutdown.
Expression zero must yield zero observed peak; nonzero cases require a positive
peak. Catalog/script bytes survive, and state bytes match the independent grammar.

The replay UI samples coherent callback snapshots; it does not promise an
observation of every intermediate transition. Each sampled hold set is checked
against the literal note-command prefix identified by its applied sequence.
Sequences must progress monotonically, have equal resolved/applied values, and
never exceed submitted commands. Every sample retains the exact complete controls.
The original 700 ms single-manual and 900 ms paired scripts keep their schedules
and final acknowledgement checks; no assertion requires a UI sample inside the
100 ms between the paired releases.

Two additional 650 ms paired scripts omit only the final Upper release. They
require two accepted note-ons, one accepted Lower note-off, and an acknowledged
endpoint with Upper MIDI 60 held, Lower empty and pedals empty. This independently
requires correct Upper ownership after the Lower release, including at expression
zero, without depending on an intermediate UI sample. The two original paired
scripts still require two note-ons, two note-offs, and the final empty endpoint.
The suite therefore performs **22 real exporter/application invocations** within
the existing eight-second per-process and 90-second CTest budgets.

The paired `0.1` case first checks the exporter bytes, then supplies accepted
shorter `0.1` text to the C++ parser. Ctrl+S while notes are held must rewrite it
to `0.10000000000000001`, proving actual serialization rather than unchanged
canonical input. No automatic smoke-note shortcut supplies these observations.
Canonical state bytes, untouched input files and the final endpoint are checked
before the sampled-prefix oracle. A post-invocation failure copies up to 65,536
bytes of diagnostic JSON into the failure record before temporary cleanup, with
an explicit marker if truncated or unavailable.

## Reproduce and continue

From the repository root, use Python 3.10+, a hardlink-capable temporary directory,
and the [pinned native build prerequisites](STANDALONE_APP.md) for the second test:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 tests/test_chapel_controls.py -v
HAMMOND_STANDALONE_EXECUTABLE=/absolute/path/to/hammond_standalone \
  PYTHONDONTWRITEBYTECODE=1 python3 apps/standalone/native_tests/test_standalone_chapel.py -v
```

Canonical CTest names are `python_test_chapel_controls` and
`test_standalone_chapel`; the latter has a 90-second timeout and native labels.
[Assignment 39](development/2026-11-13-next-phases/39-chapel-controls-acceptance.md)
records the actual 15/15 SDK-free and 2/2 native results and frozen identities.
Those historical native results covered twenty application invocations. The
[final integration review](reviews/STANDALONE_FINAL_INTEGRATION.md) retains the
later sampled-transition failure and the separate changed-test qualification;
the earlier passing result does not erase that failure.
Root owns assembled CTest and publication evidence. Real audio devices, other
platforms, physical selector/interlock behavior and loaded-gain calibration need
their own evidence; a nominal dry audition does not close those gates.
