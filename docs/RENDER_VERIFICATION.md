# Independent retained-render verification

`tools/verify_render.py` consumes the successful version-1 bundle documented in
[RENDER_EVIDENCE.md](RENDER_EVIDENCE.md). It uses Python 3.10+ and the standard
library. It does not import `render_fixture.py`, call its validation helpers, or
execute any recorded command. The supported local profile compiler is reused
only to validate authoring data, reconstruct `profile.b3p`, and calculate the
canonical authoring identity defined in [PROFILE_FORMAT.md](PROFILE_FORMAT.md).

## Run and interpret the result

```sh
python3 tools/verify_render.py out/evidence-example
python3 tools/verify_render.py out/evidence-example/manifest.json
```

Both forms print one JSON report to stdout. Exit zero means the retained bundle
passes this consumer's checks. Failures, including invalid CLI arguments, print
`{"status": "failed", "error": "..."}` and exit 1. `--help` prints ordinary CLI
help. The importable API is `verify_bundle(directory_or_manifest)`; it returns the
report or raises `VerificationError`/`OSError`.

Successful reports contain:

| Field | Meaning |
| --- | --- |
| `status: "verified_retained_bundle"` | The retained bytes and documented assertions agree under the checks below |
| `evidence_scope: "synthetic_engineering"` | The only supported evidence scope |
| `manifest`, `manifest_sha256` | Checked local manifest location and raw-byte identity |
| `artifacts_verified` | Five required artifacts, or six when `events.txt` is present; excludes the manifest itself |
| `frames`, `sample_rate` | Reconciled render parameters |
| `canonical_authoring_sha256`, `wav_sha256` | Reconstructed authoring identity and independently hashed WAV |
| `renderer.status: "matched"` | The recorded external executable is readable and its current size/hash agree |
| `renderer.status: "unavailable"` | The external executable is absent, unreadable, or has a path belonging to another operating system; `reason` explains which |
| `replay.status: "not_performed"` | This verifier never runs a renderer |
| `provenance` | Authentication, source/build association, and physical fidelity remain `not_established`; original source inputs/tool files are `recorded_not_reverified` |

An unavailable executable does not invalidate retained profile, event, WAV, and
log bytes. It does limit current executable verification and replay. A present,
readable executable with a different size/hash **does fail** verification. A
matching executable's permission to execute is reported separately; matching
bytes alone say nothing about current libraries or ability to run successfully.

An expired historical directory that now names a regular file also makes its
former executable unavailable (`NotADirectoryError`, or the platform's equivalent
missing-path error). A present executable retains the strict type, ancestry and
integrity checks.

Original input locations, producer tool identities, checkout metadata, and
environment fields are validated as typed historical records; the verifier does
not read original input/tool paths or resample Git history.

The bundle can be copied to a new nonsymlink directory. Its artifact paths remain
fixed relative filenames. Historical argv paths must use one consistent absolute
original bundle directory with exactly `profile.b3p`, `render.wav`, and optional
`events.txt`. The consumer reads the copied artifacts, preserving the recorded
argv as evidence of the claimed original invocation. POSIX and Windows absolute
path syntax are recognized for historical records.

## Independently checked contracts

1. **Completion and structure.** Require the exact schema-1 successful field set,
   `synthetic_engineering`, null error, true producer integrity assertion, valid
   ordered UTC timestamps, typed environment/Git/tool context, and documented
   parameter/limit ranges. Unknown fields, failed/incomplete runs, boolean values
   substituted for integers, duplicate keys, invalid UTF-8, nonfinite numbers,
   excessive JSON nesting, and oversized files fail.
2. **Retained files.** Require exactly `manifest.json`, `profile.json`,
   `profile.b3p`, `render.wav`, `renderer.stdout.txt`, `renderer.stderr.txt`, and
   `events.txt` only in event-file mode. Every artifact must be regular,
   nonsymlink, have its exact filename, and match its recorded size/SHA-256.
   Directory ancestors must also be nonsymlink directories. Windows reparse
   points are rejected. Unrecorded files/directories fail the inventory check.
3. **Profile and score.** Parse retained profile JSON strictly, invoke the local
   supported compiler, compare every compiled byte, and reconcile the canonical
   digest with the profile and renderer metrics. The event parser is implemented
   independently: five fields, ASCII whitespace, full-line comments, optional
   initial UTF-8 BOM, sorted absolute frames, stable file order for ties, both
   manuals, all eight documented event types, index/value domains, and file,
   line, numeric-token, total-count and same-frame density bounds. Empty scores
   are valid; out-of-range values and binary64 underflow to zero are rejected.
4. **Invocation and actual metrics.** Require the producer's exact argument
   sequence and values, copied-file paths, `--fail-on-clip`, return code 0, no
   timeout/truncation/incomplete capture, and an empty capture-error list.
   Strictly parse retained stdout, require its scalar metrics to equal the
   manifest including scalar types, and reconcile the named unmeasured model,
   profile digest, frames/rate/block/seed, stereo PCM16, zero clipped frames and
   zero clipped channel samples. Peak/RMS must be finite in 0..1; RMS may exceed
   peak only within the documented `1e-12` numerical tolerance.
5. **WAV and numerical assertions.** Decode the exact 44-byte little-endian
   RIFF/WAVE PCM16 layout; validate all identifiers, sizes, format/rate/channel/
   alignment fields and absence of extra chunks/trailing data. Stream every
   stereo frame, require equal channels, and accumulate exact one-channel
   integer peak/sum of squares. Recompute normalized peak/RMS and require the
   recorded statistics to agree. Independently recompute the two float-versus-
   PCM differences and require each to be at most `1/32768 + 1e-12`; verify the
   recorded domains, bound, tolerance, differences and success assertion.
6. **Observed stability.** Check files before/after reading and again before
   success; recheck the directory inventory. Path metadata is compared with
   subsequent path metadata, and descriptor metadata with subsequent descriptor
   metadata. POSIX additionally checks device/inode agreement across opening.
   This avoids assuming Windows path and descriptor metadata APIs are identical.

## Bounds and limits of the claim

Manifest and authoring JSON are each limited to 256 KiB; compiled profiles to
128 KiB; each retained log to 1 MiB; metrics JSON to 16 KiB; events to 16 MiB;
and any read executable to 512 MiB. JSON is limited to 24 nesting levels,
20,000 nodes, 64 fields per object, 1,024 entries per array, 4,096 characters per
string and 128 characters per integer token. Event lines are limited to 4,096
bytes, numeric tokens to 128 bytes, events to 262,144 total and 1,024 per frame.
WAV processing uses 64 KiB blocks; the documented 600-second/96-kHz maximum is
230,400,044 bytes. Audio is never loaded into one whole-file buffer.

The producer's success and Boolean fields are necessary claims, then checked
against retained evidence. They are not signatures. An unauthenticated bundle
can be rewritten along with its hashes and internally consistent metrics. This
verifier cannot prove who produced the bundle, that the claimed executable ran,
that a Git revision built that executable, or that an audio file is a measured
instrument. Before/after observations are useful change detection, not an
execution sandbox or protection against every concurrent replace-and-restore
race. Replay, reproducible source builds, linked-library provenance, host tests,
callback deadlines, and physical/acoustic validation require separate evidence.

## Test entry point

CTest discovers `tests/test_verify_render.py` automatically and supplies
`HAMMOND_RENDER_EXECUTABLE` and `HAMMOND_TEST_PROFILE`. Missing prerequisites fail
explicitly. The suite creates small real bundles with the producer, then verifies
them independently. It exercises copied bundles, event grammar, all supported
sample rates, the maximum seed, empty-score silence, current/missing/changed
executables, strict JSON/types, missing/extra/symlink files, changed observations,
and tampered/rehashed profile, stdout, WAV, statistics, argv, flags and comparison
claims. Producer verification helpers are disabled in a test of consumer
independence. A focused metadata test simulates different stable timestamps from
the path and descriptor APIs; this is not a substitute for native Windows CI.
