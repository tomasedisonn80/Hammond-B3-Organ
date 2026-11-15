# Fractional contact reference: setup and use

The M3 reference resolves nine independent hysteretic contacts along continuous
key travel, integrates their switched shared sources, and then reduces bandwidth.
It is a standard-library Python research tool. The playable C++ Engine still uses
its existing nominal console model; running this tool does not alter a saved
registration, source profile, plugin parameter, or application setting.

The implementation follows the atlas's contact-switching work on pages 109–120.
The [model contract](FRACTIONAL_CONTACT_REFERENCE.md) and
[independent validation protocol](CONTACT_SWITCHING_VALIDATION.md) are frozen
experiment inputs. Their admission-time status text remains historical; executed
outcomes are retained in the [source-identified results](CONTACT_SWITCHING_RESULTS.md).
The qualified installed study passes the fixed v1 experiment; its 64 continuous
probes per fixture do not establish full-window or hardware accuracy. The
[execution checkpoint](development/2026-11-15-execution-continuation/CHECKPOINT.md)
records current acceptance and the next action.

For a movable package that runs without the source checkout, use the explicit
[ContactReferenceTools installation](CONTACT_REFERENCE_INSTALL.md). That 48-file
component includes this operating guide, the frozen contracts, all six Python
tools and the complete fixture/probe set. The results page and session reports
are repository evidence outside the installed payload.

## Run one fixture

Use Python 3.10 or newer. No NumPy, compiler, native audio backend, MIDI device, or
third-party Python package is required. Run these commands from the repository
root in a POSIX shell:

```sh
mkdir -p ../contact-reports
python3 -B tools/contact_switching_reference.py \
  --input data/contact-switching/reference-v1/F02-48000-v1.json \
  --factor 256 --output ../contact-reports/F02-48000-L256.json
```

On Windows, use an available Python 3.10+ interpreter (`python` or `py -3`) and
create the output directory first. Paths are ordinary filesystem paths; the
scripts do not create missing parent directories. The accepted factors are 32,
64, 128 and 256. Success exits 0 and writes the complete JSON report. A rejected
input or failed write exits nonzero with a bounded diagnostic on stderr; an
existing output is preserved on failure. The single-fixture command can replace
an ordinary existing report atomically, so choose distinct names when retaining
experiments.

To inspect the resulting samples and time origin:

```sh
python3 - <<'PY'
import json
from pathlib import Path
report = json.loads(Path('../contact-reports/F02-48000-L256.json').read_text())
print('factor:', report['factor'])
print('samples:', len(report['samples']))
print('first absolute frame:', report['first_frame'])
print('raw amplitude bound:', report['raw_bound'])
print('first five samples:', report['samples'][:5])
PY
```

The fixture names identify recipe, sample rate and version. The 36 fixed inputs
cover twelve recipes at 44.1, 48 and 96 kHz: silence, constant source, peak/zero
crossings, high-frequency switching, shared sources, partial presses with distinct
histories, repeated/reversed targets, exact ties, clipped arrival, and a terminal
observation gate. These are synthetic stimuli, not measurements from an organ.

## Read the signal correctly

For a nonempty N-frame observation the renderer returns N+33 samples, addressed
from absolute host frame −16 through N+16. The filter is centered and acausal;
`time_offset_seconds` records this origin. Samples before 0 and after N are complete
filter tails. Do not trim them or privately align/gain-fit signals before comparing
results. An empty observation returns no samples and no filter metadata.

`frames` defines an explicit observation window `[0,N)`. The ungated signal can
still be active at its end. Cutting it off is an observation-gate event, not a
physical contact release. A command at N changes the final target without adding
time for motion. Reports retain both physical edges and separate gate jumps.

The exact event coordinate is the rational `exact_u` numerator/denominator in
each edge. The convenient floating frame/fraction can display two different
crossings at the same time; it must not replace the exact identity. Incoming
threshold equality is resolved before commands at the same time. Repeated targets
do not restart movement, and shared source phase depends on absolute time.

`raw_bound` is the smallest binary64 upper bound on the exact sum of absolute
routed source amplitudes. The filtered `output_bound` describes the ideal
mathematical convolution; it is not a certified floating-point headroom limit.
Bounds normalize errors before squaring. Tiny or silent references have explicit
eligibility rules instead of an invented normalized-error denominator.

## Run the fixed comparison study

Execute the admitted runner's entire frozen experiment with a **fresh report
path** whose parent directory already exists:

```sh
python3 -B tools/contact_switching_study.py \
  --fixtures data/contact-switching/reference-v1 \
  --output ../contact-reports/study-v1.json
```

The study never replaces an earlier report. It writes and fsyncs a complete
temporary file in the output directory, then publishes it with an atomic
non-overwriting hard link. A destination created concurrently is preserved and
the attempt fails; a filesystem that cannot perform this operation fails
explicitly. Owned temporary files are cleaned up. Choose another fresh path
for every retry and retain the original outcome. The single-fixture command's
successful atomic replacement behavior is different, as described above.

| Exit status | Meaning |
| --- | --- |
| `0` | Complete report with `status: passed`; applicable numerical and internal resource gates passed. |
| `1` | Retained `status: failed` report; inspect the individual failed cells. |
| `2` | Incomplete experiment or rejected execution. A missing input, admission or publication failure can leave no report. |

The study has no subset, factor or tolerance override. It verifies frozen input
and probe identities and records exact implementation/contract hashes. It renders
**36 fixtures at four factors: 144 renders**, checks **all 289 output samples**
per fixture for L128→L256 convergence, and compares **64 frozen samples per
fixture** against independently reconstructed continuous eight-point
Gauss–Legendre quadrature. All fixtures and rates must satisfy their own
applicable criteria; averaging across fixtures cannot conceal a failure.
A 64-point reference check is not a full-window qualification of the atlas's
later `1e-4` target. The [results](CONTACT_SWITCHING_RESULTS.md) give each frozen
criterion, observed maxima and the retained first/repaired-run identities.

The study also retains kernel response, complete-output residual spectrum and a
separately named ceil-edge diagnostic. Those are characterizations; the latter
is not a comparison against the current Engine. Reading and concatenating ranges
from a complete immutable render verifies exported ranges and tails, not a
streaming filter implementation.

The frozen experiment allows **300 seconds**, **256 MiB process peak resident
memory**, **180 million conservative FIR products**, **10 million oracle
integrand evaluations** and **32 MiB retained report data**, with at most
20 million declared work units in any render. Unknown memory measurement or an
exceeded budget leaves the experiment incomplete. The runner's internal interval
excludes Python startup, final metadata encoding and atomic publication; retain
an **external whole-process wall time through child exit** as well. Measure the
specific child's terminal peak resident memory, including publication, rather
than differencing cumulative maxima from unrelated children. The
[qualified process receipt](development/2026-11-15-execution-continuation/reports/contact-study-v1-qualified-process.json)
records this boundary for the executed Linux run. Preserve failed/incomplete
reports. Changing a model, fixture, probe, filter, tolerance or budget requires
a separately reviewed protocol.

## Next development boundary

Use the accepted, source-identified study as a bounded comparison authority for
a separately designed causal streaming implementation. That design must declare
latency, absolute source phase, independent contact histories, bounded work and
allocation, block-partition behavior, reset and tail semantics before integration.
Independently admit a full-window reference before assigning a later all-sample
atlas `1e-4` grade. Keep the 47 parameter identities and
`B3CONTROLS4`/readers 1–3 unchanged unless a
separate state-migration design is accepted. Contact bounce, wiring/loading,
hardware timing and physical audio fidelity require identified synchronized
gesture/contact/source/dry measurements and held-out evaluation. This synthetic
reference does not supply them.
