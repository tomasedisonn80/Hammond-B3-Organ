# Assignment 13 — bounded audio inspector implementation

**Actual assignment:** `/root/cal_w3_a13`, calibration wave 3, assignment 13,
2026-11-13. This is one newly dispatched implementation assignment in the
current sixty-assignment session. It does not recount an earlier worker.

**Outcome:** implemented the frozen audio API and CLI, wrote its usage/limits
guide, and executed author smoke checks. Independent acceptance remains assigned
to separate workers; this record does not claim their results or a physical pass.

## Ownership and exact source

Owned files:

- `tools/capture_audio.py`
- `docs/CAPTURE_AUDIO.md`
- `docs/development/2026-11-13-calibration/13-audio-implementation.md`

Working directory was
`/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`. Initial `HEAD` and locally
recorded `origin/main` were both `08fa8de8f718584c4ee4ab3b392c779f3290289c`,
tree `f5cff4b89d19f36a73f9d2a8ddb966db487f832c`. Concurrent uncommitted changes
were present and preserved. The new module is identified by its complete-byte
SHA-256 rather than attributing uncommitted code to that initial commit:

| File | SHA-256 at author-check completion |
| --- | --- |
| `tools/capture_audio.py` | `967ecc3c5b8ea3e12d71341c28edc22ced8da4316c2a81a9059f6eafa19851c2` |
| Frozen `docs/CAPTURE_AUDIO_CONTRACT.md` | `1766ed93f26eb5fa4db21397f6dd74002970ec567e7ff4541536911598d026cc` |
| Unchanged `tools/analyze_wav.py` | `e39d3b414854066af2510c3dedf26c70ea71066a09efce5a9cdb41114e8b5fb7` |
| Unchanged `tools/validate_capture.py` | `a872e069ba9744f6f8078f87b78ea300df1ee28aec58e104859580cdc09877af` |

Read `AGENTS.md`, the calibration scope, all 615 lines of the frozen audio
contract, the integration contract review and current track context. The atlas
basis and physical limits are retained by the contract and current-session fresh
atlas review; this assignment does not claim another complete PDF reading.
No shared status/ledger/CMake files, other-track files or Git refs were modified.
No commit, push or hosted CI result is claimed by this worker.

## Implemented behavior

- Public `AudioError`, `inspect_audio`, `read_audio_window` and `main`, with the
  required exposed resource constants and exact report surfaces.
- Ordinary-tag WAV PCM16/24/32 and float32/64; explicitly described raw float32.
  Complete RIFF chunk validation, exact format extension rules, optional `fact`
  checks, bounded opaque ancillary traversal and explicit unsupported layouts.
- One descriptor for header scan, one sequential complete content/hash/decode
  pass, exact full-file and canonical decoded SHA-256, full-stream finite/range
  checks, bounded reads/digest updates and bounded requested sample retention.
- Exact integer PCM sums/squares; compensated float DC and scaled compensated
  RMS; exact sample ordering/counts, endpoint diagnostics and positive zero.
- Regular non-reparse/non-symlink leaf admission; requested/canonical path,
  parent and descriptor observations; same-API timestamp checks; final mutation
  precedence; cleanup including `fdopen` failures and cancellation.
- Compact sorted ASCII-escaped finite JSON CLI output, paired window options,
  strict decimal integer tokens, typed JSON errors and deterministic exit codes.

The integrator confirmed two narrow interpretations before implementation:
out-of-bound exact-int rate/channel declarations use `resource_limit` after file
admission, while type/missing-raw-geometry errors are `invalid_argument`; canonical
parent validation uses type/usable identity and alias resolution without comparing
directory timestamps/size affected by sibling activity. These interpretations
are documented in the usage guide and do not relax source-file observations.

Root source review identified that requiring a nonzero device number would be
overrestrictive on a platform with a valid zero device scope. The final helper
requires a nonzero inode and retains the full `(device, inode)` pair. An author
synthetic-stat execution covered both helpers and complete inspection with zero
device numbers. This aligns with the existing capture/corpus identity boundary;
no native Windows execution is inferred from that synthetic check.

## Actual author executions

Environment: Linux container, Python **3.12.14**, standard library only. The
temporary author script creates literal/`struct` fixtures independently of the
new parser and constructs its expected hashes directly with `hashlib` and
`struct`, or uses the contract's printed literals. It is an author smoke script,
not the separately assigned independent acceptance suite.

```sh
python3 /tmp/calibration-audio-a13-smoke.py
python3 -m py_compile tools/capture_audio.py
git diff --quiet HEAD -- tools/analyze_wav.py tools/validate_capture.py
sha256sum tools/capture_audio.py docs/CAPTURE_AUDIO_CONTRACT.md
```

The temporary script's SHA-256 is
`b737146f126bbbd5c30b6f9c8e35f6ed7dcc3206d34c528a8ecbf9c5ddb349d8`.
It was rerun after final implementation changes and printed
`PASS 144 author smoke assertions; Python 3.12.14`, exit 0. `py_compile` and
the unchanged-legacy-file diff check also exited 0. The temporary script is
reproducibility context for this execution, not a permanent acceptance entry
point; the independent retained suite is the next integration requirement.

| Executed author coverage | Observed result |
| --- | --- |
| Printed vector A WAV and decoded hashes; complete layout, RMS and two-frame stereo window | Exact printed hashes, statistics and ordering; nested inspection equals ordinary inspection. |
| Re-encoding A in PCM16/24/32, WAV float32/64 and explicit raw float32; odd ancillary padding and 18-byte zero extension | All six decoded identities match the frozen A digest. |
| Changed rate, swapped channels, mono/eight-frame geometry | All three distinct printed decoded hashes match exactly. |
| All PCM edge widths, one-LSB values and PCM24 odd data padding | Exact normalized samples, endpoint/nonzero counts and printed integer-arithmetic DC/RMS formulas. |
| Printed vector C byte/decoded hashes, signed-zero samples and statistics | Exact hashes, positive zero signs and RMS `0.875`. |
| Four least-positive binary64 subnormals | Peak, RMS and DC each exactly equal the least positive subnormal; nonzero count 4. |
| Binary64 cancellation `[1e6, 1e-9, -1e6, 1e-9]` | Meets frozen DC/RMS tolerance against a 100-digit Decimal oracle formed from exact stored floats. |
| Float32 NaN and both infinities, and over-range finite sample, before/inside/after a selected window | Every complete call rejects with the specified error code. |
| Inclusive `+/-1e6` and next binary64 above `1e6` | Boundary peak/RMS exactly `1e6`, DC zero; adjacent excess rejected. |
| Missing/duplicate/disordered chunks, empty/partial frames, incomplete headers/padding, trailing bytes, malformed extensions and contradictory fact/LIST | Specified malformed-audio rejections. |
| Extensible/compressed/PCM8 WAV, FLAC, RIFX, RF64, slnt and LIST/wavl | Explicit unsupported-format rejections. |
| Declaration mismatch, missing raw geometry, Boolean numeric inputs and invalid integer windows | Specified typed errors. |
| Actual leaf symlink, dangling link, directory, FIFO, absent file/parent; parent alias and hard link | Unsafe/missing leaves rejected; direct canonical parent alias and regular hard link admitted. |
| Controlled `fdopen` failure | `io_error`; Linux `/proc/self/fd` count unchanged. |
| 90,000-byte PCM24 three-channel data crossing the 65,536-byte boundary | Read bound respected, exact independently constructed decoded digest and window ordering. |
| Controlled timestamp mutation during successful parsing | `file_changed`, with no partial report returned. |
| Repeated CLI success, exact wire encoding, malformed numeric/window options, missing path and help | Deterministic bytes, required stdout/stderr separation and exit 0/1/2 behavior. |

Two additional inline Python author probes exited 0:

- **8 resource/identity assertions:** rate-1 raw file at exactly 3,600 frames
  admitted and 3,601 rejected; 600-frame window admitted and 601 rejected; usable
  zero-device/nonzero-inode helper and complete-inspection checks; zero inode
  treated as unavailable; actual sparse `MAX_FILE_BYTES + 1` rejected before
  a hooked `os.open` could run.
- **3 cleanup/cancellation assertions:** controlled timestamp mutation overrode
  an otherwise `nonfinite_sample` rejection with `file_changed`; injected
  `KeyboardInterrupt` propagated; the descriptor count remained unchanged.

These are **155 author assertions total**, not 155 independent test methods.
No failures were observed in the executed smoke runs. No result is claimed for
unexecuted maximum-stream sizes, the full independent acceptance matrix or other
platforms. The final module identity above is the input to those later checks.

## Remaining gates and concrete handoff

Independent workers 16 and 24 should import the actual module with `tools` on
`sys.path`, use the frozen contract identity above, and retain their separately
authored test results against its final SHA. Required integration includes the
complete resource/structure/identity/error-priority matrix and unchanged legacy
analyzer/capture suites. Root owns shared documentation, test registration,
coherent-source qualification and publication.

Native Windows reparse points, native platform file-identity differences and
full maximum admitted sample-work executions were not run here. Portable file
observations cannot exclude a writer restoring every observed attribute; keep
archives quiescent. Corpus confinement and cross-capture independence remain
separate caller responsibilities. No physical specimen, actual acquisition,
calibration uncertainty, clock measurement, listening evaluation or hardware
fidelity result was supplied or inferred.
