# Contact-grid conversion: setup and use

`fractional-to-contact-grid-rne-v1` converts one admitted fractional-contact
research input into an explicitly rounded integer-grid case and a JSON
**trajectory certificate**. It records exact source/grid event relationships and
bounded motion error. It produces no audio: `audio_accuracy` remains `unqualified`.
Running it changes no Engine, standalone or VST3 behavior.

The [conversion contract](CONTACT_GRID_CONVERSION_CONTRACT.md) and its
[independent admission](reviews/CONTACT_GRID_CONVERSION_ADMISSION.md) define the
version. The source model is `fractional-contact-reference-v1`; the target model
is `causal-contact-grid-v1`. Original models, 91 shared sources, 47 sound parameters
and `B3CONTROLS4` with readers 1–3 retain their meanings.

## Prepare a trusted working copy

The converter needs **Python 3.10 or later and only the standard library**. A
source-checkout invocation needs no C++ build, SDL, MIDI device or VST3 SDK.
Keep these five files in their existing relative layout:

| Path | Role |
| --- | --- |
| `tools/convert_contact_grid.py` | Strict command and atomic certificate publication |
| `tools/contact_grid_conversion.py` | Exact conversion, reconstruction and encoding |
| `tools/contact_switching_io.py` | Original input and path admission |
| `tools/fractional_contact_reference.py` | Original source model and validation |
| `docs/CONTACT_GRID_CONVERSION_CONTRACT.md` | Contract identity included in provenance |

Use an unchanged checkout or a fresh trusted package. The command hashes these
files before and after conversion. Python `-B` prevents writing bytecode caches;
it does **not** prevent reading a valid existing cache. Disk hashes identify
source files, not a hostile interpreter, cached code or modified import
environment. The [transaction review](reviews/CONTACT_GRID_CONVERSION_TRANSACTION_REVIEW.md)
retains the experiment establishing that limit.

The unchanged [input contract](FRACTIONAL_CONTACT_REFERENCE.md) remains authoritative.
JSON numbers are admitted as canonical binary64 values; apparent decimal intent
is not a second source of truth. The original parser canonicalizes signed zero
and refuses extra fields, duplicate JSON keys and invalid domains. Preserve the
original bytes with the certificate so `input_sha256` and `input_bytes` can be
checked later.

## Convert the retained F02 input

These POSIX-shell commands run from the repository root. Choose a fresh working
directory; `mkdir` deliberately fails if this example directory already exists.
On Windows, use your Python 3.10+ command name and corresponding paths.

```sh
mkdir ../contact-grid-example
cp data/contact-switching/reference-v1/F02-48000-v1.json ../contact-grid-example/
cp data/contact-switching/reference-v1/F09-48000-v1.json ../contact-grid-example/
python3 -B tools/convert_contact_grid.py \
  --input ../contact-grid-example/F02-48000-v1.json \
  --output ../contact-grid-example/F02-grid-certificate.json
```

Success is **exit 0 with empty stdout and stderr**. The output is one compact JSON
object followed by a newline. `--input` and `--output` are each required exactly
once. Abbreviated flags, `-` for stdin/stdout and a help-only success mode are
unsupported. Create the output parent first. Successful conversion can replace
an admitted regular output, so choose fresh names when preserving evidence.

F02 at 48 kHz has 256 frames, one key, two commands, **18 contact edges and two
target arrivals**. The [executed guide receipt](development/2026-11-16-conversion-material/reports/A27-operating-examples.json)
records a 33,678-byte certificate on Python 3.12.14. Its maximum position error is
approximately `2.1267268379e-7` of full travel; maximum matched-root time error is
approximately `6.1249732932e-6` frames. These decimals are descriptive: acceptance
uses the stored reduced exact fractions. Changing source, contract or recorded
Python version can change certificate bytes.

This display-only reader prints the exact values:

```sh
python3 -B - <<'PY'
from fractions import Fraction
import json
from pathlib import Path

d = json.loads(Path("../contact-grid-example/F02-grid-certificate.json").read_bytes())
print(d["conversion_id"], d["status"], d["audio_accuracy"])
print("edges:", len(d["edges"]), "arrivals:", len(d["arrivals"]))
for name in ("max_position_error", "max_root_error"):
    r = d["summary"][name]
    value = Fraction(int(r["numerator"]), int(r["denominator"]))
    print(name, value, "approximately", float(value))
PY
```

Reading JSON is not independent certificate validation. The public encoder
reconstructs and reconverts a supplied result before encoding; separate suites
provide independent numerical and native comparisons.

## Read the certificate by question

| Question | Fields and meaning |
| --- | --- |
| Which input and implementation? | `input_sha256`, `input_bytes`, `fixture_id`, model IDs, `conversion_id`, `evidence_class`, and `provenance` with four module hashes, contract hash and Python version |
| What does the grid receive? | `grid_case` contains rounded keys, thresholds, speeds and targets; `transport` contains matching `CGGRID1` ASCII bytes, SHA-256 and default partition |
| What original values survive? | `sidecar` retains source/route/command identities and canonical binary64 values as 16-digit IEEE-754 hex; it reconstructs the case, not raw JSON spelling |
| Which events correspond? | `edges`, `arrivals`, `commands` and `final_keys` retain matched identities, exact paired times/positions and final contact facts |
| Did equality or order change? | `preorder` is the shared ordered sequence of exact equality groups for edges, arrivals, commands and both epoch boundaries |
| Where is motion error largest? | `position_samples` covers the union of both paths' knots; `summary.position_witness` names the maximum witness |
| How are crossing times bounded? | `root_bounds` records emitting-segment anchors, thresholds, speeds, actual error and analytic bound; `summary.root_witness` names the maximum actual error |
| What rounding occurred? | `scalar_errors` records original/grid values and signed differences, including effective press/release durations |

Exact rationals contain decimal-string `numerator` and `denominator`, reduced
with a positive denominator. Counts and indices are JSON integers. A no-root
maximum is zero with a null witness. Source-byte metadata is bound by the CLI's
actual input read; the pure encoder cannot authenticate original bytes it was
never given.

Rounding uses exact nearest/even arithmetic: **65,536 ticks per frame**, **2^48
position units per full travel**, and integer position units per tick for each
press/release speed. It never nudges colliding commands apart. Every source
edge/command/arrival/boundary equality and order must survive. Incoming edges
and arrivals resolve before tied commands; those commands retain caller order.
Repeated targets preserve their motion anchor. Muted routes still retain their
contact histories and checks.

The bounds are `2^-18` normalized travel for continuous position error and
`2^-10` frames for each matched edge/arrival time error **and its analytic upper
bound**. These finite engineering choices are not measured key accuracy, an
audio-error allocation or a guarantee that every valid input converts.

## Inspect a meaningful refusal

F09 is an unchanged valid source fixture refused at every supported rate. Run
this command individually and expect **exit 2**:

```sh
python3 -B tools/convert_contact_grid.py \
  --input ../contact-grid-example/F09-48000-v1.json \
  --output ../contact-grid-example/F09-grid-certificate.json \
  > ../contact-grid-example/F09-refusal.json
python3 -m json.tool ../contact-grid-example/F09-refusal.json
```

A shell with `set -e` stops on the expected first command's exit 2; inspect the
saved diagnostic in a subsequent command. No certificate is created. If an
admitted output existed, its prior contents remain unchanged. The guide smoke
executed both states and checked their bytes.

Here the code is `event_order` at `preorder[5]`. The witness names command `C:2`
and edge `E:0:4:1:0`: key 0, contact 4, closing direction, occurrence 0. Both
source events occur at exactly `375/32` frames. The grid command stays there,
while its edge occurs at `1073741824/91625969`, strictly earlier. A tiny scalar
error broke an exact equality. Retain this fixture and refusal; do not relax the
equality rule to turn it into an accepted example.

| Code family | Meaning and next action |
| --- | --- |
| `argument`, `path`, `input` | Correct the invocation or inspect the original schema/path/domain error; preserve research input bytes |
| `grid_domain`, `time_collision`, `position_collision` | This grid cannot represent the values under its fixed domain or injectivity rules |
| `dynamic_topology`, `event_identity`, `event_order`, `final_contacts` | Motion/contact facts, identities, equality/order or final bits differ; inspect the exact witness |
| `position_budget`, `root_budget` | Exact motion or root error/bound exceeds the fixed tolerance |
| `certificate` | Schema, reconstruction, transport or provenance cannot be accepted |
| `resource` | A work/bit/byte/deadline/diagnostic cap was reached; operational refusal does not prove mathematical failure |
| `operation` | A precommit operation failed; inspect `path` and the bounded sanitized witness |
| `interrupted` | Precommit interruption; exit 130 and no publication |

The contract fixes refusal precedence. The diagnostic reports the first
applicable failure, not every problem. Its bounded JSON line contains
`schema_version`, `conversion_id`, `status`, `code`, `path`, `witness` and no
accepted payload. A closed stdout sink cannot receive it, but the repaired CLI
preserves the refusal exit status.

## Publication and finite limits

The CLI finishes conversion, reconstruction and encoding before creating a
same-directory temporary. It rechecks paths, writes, flushes, fsyncs, rechecks
again and replaces exactly one destination. Successful replacement is the commit
point. Observed precommit interruption exits **130**, preserving the destination;
successful replacement returns **0**, including an interrupt during its final
bookkeeping. Other precommit refusals exit **2**. Only the owned temporary is
eligible for cleanup; filesystem failure can itself prevent cleanup.

Input and output-parent symlinks may resolve to ordinary admitted paths. An
output-leaf symlink, input/output inode alias, directory/FIFO endpoint or missing
parent is refused. The transaction does not protect against hostile concurrent
directory mutation or guarantee power-loss durability of directory data.

| Limit | Version 1 value |
| --- | --- |
| Rates, keys, epoch | 44,100 / 48,000 / 96,000 Hz; 1–4 keys; 0–4,096 frames |
| Contacts, supplied commands | Nine per key; at most 512 commands including ties, no-ops and endpoint commands |
| Input | 256 KiB; JSON depth 12 under original admission |
| Exact arithmetic | 4,096 bits per retained reduced numerator/denominator; 8,192-bit transient products |
| Replay/comparison | 1,032 segments, 4,608 edges, 512 arrivals, 5,634 labels per replay; 4,096 union knots across all keys |
| Work/time | 1,000,000 counted units; 30-second cooperative CLI deadline |
| Output | Certificate 32 MiB; transport 131,072 ASCII bytes; refusal JSON 8,192 bytes |

Limits refuse instead of truncating. The deadline is cooperative, not an OS or
audio-callback deadline; the certificate cap is not a process-memory cap. The
[resource review](reviews/CONTACT_GRID_CONVERSION_RESOURCE_REVIEW.md) separates
actual maximum cases, conservative limits, injected tests and observed RSS.

## Install and relocate the five-file package

Follow [ContactGridConversionTools installation](CONTACT_GRID_CONVERSION_INSTALL.md)
for clean-checkout CMake prerequisites, exact preflight and copy-only behavior.
From a build already configured with the intended source, use a fresh prefix:

```sh
cmake --install ../build-native --config Release \
  --component ContactGridConversionTools \
  --prefix "$PWD/../hammond-contact-grid-example"
mv ../hammond-contact-grid-example ../hammond-contact-grid-moved-example
python3 -B -E -s -S \
  ../hammond-contact-grid-moved-example/share/hammond-b3-organ/contact-grid-conversion/tools/convert_contact_grid.py \
  --input ../contact-grid-example/F02-48000-v1.json \
  --output ../contact-grid-example/F02-relocated-certificate.json
```

This assumes `CMAKE_INSTALL_DATADIR=share`; use the configured directory otherwise.
Root coordinates this session's shared build. New users can follow the install
guide's separate clean configuration. This component needs no native target
build and installs exactly five files, excluding fixtures, this guide,
certificates and the probe. `-E -s -S` ignores Python environment variables and
avoids user-site/site initialization; it does not prevent reading caches.

Move the complete package with `tools/` beside `docs/`; keep inputs and outputs
outside it. The older **48-file `ContactReferenceTools`** package is unchanged
and installed separately. The new component refuses an existing package instead
of merging. Unlike certificate publication, package installation is not atomic:
a later copy failure can leave a partial new directory without rollback.

A23's [installer smoke](development/2026-11-16-conversion-material/reports/A23-install-smoke.json)
exercised CMake installation and relocation. A27's guide smoke manually copied
this exact five-file layout, renamed its prefix and ran it from a foreign working
directory. It obtained a byte-identical certificate and unchanged package. That
runtime check does not substitute for installer or platform acceptance.

## Optional native trajectory observation

The five-file package does not include a native executable. Build one separately
using the [causal-grid guide](CAUSAL_CONTACT_GRID_GUIDE.md), or select a coherently
built probe from the intended source. This snippet uses the session's existing
Linux executable and passes the certificate's exact transport bytes:

```sh
python3 -B - <<'PY'
import hashlib
import json
from pathlib import Path
import subprocess

certificate = json.loads(Path("../contact-grid-example/F02-grid-certificate.json").read_bytes())
wire = certificate["transport"]["text"].encode("ascii")
assert hashlib.sha256(wire).hexdigest() == certificate["transport"]["sha256"]
probe = Path("../build-native/hammond_causal_contact_grid_probe").resolve()
completed = subprocess.run([str(probe)], input=wire, capture_output=True,
                           check=True, timeout=10)
assert completed.stderr == b""
observed = json.loads(completed.stdout)
print(observed["model_id"], len(observed["edges"]),
      observed["snapshot"]["cursor_frames"], observed["snapshot"]["phase"])
PY
```

Expected summary: `causal-contact-grid-v1 18 256 closed`. Select the actual
platform/generator executable path. The probe always closes its observation;
closure does not release a held key or drain audio. `CGGRID1` is a research
transport, not an audio file or saved musical state.

This smoke observes a result. The [independent native comparison](reviews/CONTACT_GRID_CONVERSION_NATIVE_REVIEW.md)
separately checks 51 accepted cases among all 71 retained inputs, 557 processes,
full padded snapshots and partitions. Its accepted corpus has no integer-frame
edge case, and the wire probe cannot request short-buffer retry. Existing native
grid differential/lifecycle tests own those distinct boundaries; reading native
JSON alone does not prove equivalence.

## Reproduce this guide and continue development

The [reproducer](development/2026-11-16-conversion-material/reports/A27-operating-examples.py)
executes the source acceptance, two refusal destination states, relocated-layout
runtime and optional native observation in one owned temporary directory. It
records commands, source/probe identities, outputs, certificate facts and cleanup,
and refuses to replace an existing receipt:

```sh
python3 -B docs/development/2026-11-16-conversion-material/reports/A27-operating-examples.py \
  --report ../A27-guide-repeat.json \
  --probe ../build-native/hammond_causal_contact_grid_probe
```

The retained five processes passed in approximately 0.489 seconds on Linux with
Python 3.12.14, then the temporary directory was removed. No native build,
production edit or CMake installation was performed by this guide worker. The
[numerical](development/2026-11-16-conversion-material/reports/A15-independent-numerical.json),
[resource](reviews/CONTACT_GRID_CONVERSION_RESOURCE_REVIEW.md),
[transaction](reviews/CONTACT_GRID_CONVERSION_TRANSACTION_REVIEW.md),
[native](reviews/CONTACT_GRID_CONVERSION_NATIVE_REVIEW.md) and installation records
qualify distinct scopes and retain their original failures.

The next M3 dependency is a separately admitted [causal audio contract](research/CAUSAL_CONTACT_AUDIO_NEXT.md)
using its [independent review](reviews/CAUSAL_CONTACT_AUDIO_NEXT_REVIEW.md): absolute
source phase, exact partial-cell integration, bounded arithmetic/history,
reconstruction filter, latency, partition/reset behavior, drain and full-window
reference criteria. Full-organ/indefinite capacity and Engine/standalone/VST3
integration have separate gates. Physical timing, bounce, resistance and tap
loading require identified synchronized measurements. A trajectory certificate
supplies none of those missing audio or physical results.
