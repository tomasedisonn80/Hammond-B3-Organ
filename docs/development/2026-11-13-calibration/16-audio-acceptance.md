# Assignment 16 — independent audio sample and format acceptance

**Actual assignment:** `/root/cal_w3_a16`, calibration wave 3, assignment 16,
2026-11-13. This newly dispatched worker is separate from the decoder producer
and earlier contract authors. It contributes one assignment to this session.

**Result:** all **41 independently authored test methods passed**, with no skips,
against the decoder identity below. No production defect was found in this
assigned sample/format/API/CLI scope. One initial test-control mistake was
corrected and is retained explicitly below. These are engineering fixtures and
do not qualify an acquired instrument or physical calibration.

## Ownership and inspected source

Owned files are only:

- `tests/test_capture_audio.py`
- `docs/development/2026-11-13-calibration/16-audio-acceptance.md`

The working directory was
`/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ`. At initial inspection, both
`HEAD` and the locally recorded `origin/main` were
`5026f671e788eb5e1a77c8ed4046a34afd539200`, tree
`2ed85b986f70895000f086039750f44773508819`. The decoder and other workers' files
were uncommitted; this note identifies the tested decoder by its complete-file
SHA-256 and does not attribute that code to the published starting commit.

| Tested or preserved input | SHA-256 |
| --- | --- |
| `tools/capture_audio.py` | `967ecc3c5b8ea3e12d71341c28edc22ced8da4316c2a81a9059f6eafa19851c2` |
| Frozen `docs/CAPTURE_AUDIO_CONTRACT.md` | `1766ed93f26eb5fa4db21397f6dd74002970ec567e7ff4541536911598d026cc` |
| Final `tests/test_capture_audio.py` | `9fc75824234b3203f1eb9f63c0fe7562a3d9a931cda34e9a774b4c1402c56ddd` |
| Unchanged `tools/analyze_wav.py` | `e39d3b414854066af2510c3dedf26c70ea71066a09efce5a9cdb41114e8b5fb7` |
| Unchanged `tools/validate_capture.py` | `a872e069ba9744f6f8078f87b78ea300df1ee28aec58e104859580cdc09877af` |

Read the standing agent instructions, calibration scope and the entire frozen
audio contract. The retained full-atlas review belongs to assignments 1–6;
this assignment does not claim another complete PDF reading. No production,
shared status, ledger, CMake, other-track files or Git refs were modified.
Root retains integration and publication ownership.

## Independence of the acceptance calculations

The suite calls only the public audio API, CLI and exposed constants. Its own
small RIFF encoder uses literal chunk names, integer byte encodings and `struct`;
it never calls the production header parser. The exact 60-byte PCM16 vector A,
raw float32 vector C, and signed PCM edge payloads are retained as literal hex.
Seven printed file/decoded hash values are literal acceptance values. A separate
canonical-stream construction uses the literal prefix, explicit little-endian
rate/channel/frame fields, and normalized binary64 samples. No production
digest helper or producer report supplies an expected hash.

Expected samples come from the defined fixture values, including independent
binary32 pack/unpack widening. Integer edge values use their signed code and
power-of-two denominator. Statistics use 120-digit Decimal calculations of the
exact stored binary64 values, with the frozen ordinary tolerance
`max(2e-12, 2e-12 * abs(expected))`. Literal subnormal, signed-zero, sample,
count, endpoint and hash requirements remain exact. Producer smoke assertions
are not included in this suite's test count or substituted for its oracles.

## Executed acceptance

Environment: Linux x86_64, kernel `6.18.57`, glibc `2.41`, Python **3.12.14**.
Only the Python standard library is needed. From the repository root:

```sh
python3 -B tests/test_capture_audio.py -v
```

The final execution exited **0**, reporting `Ran 41 tests in 0.539s`, `OK`.
There were **zero skipped tests**. The table groups the cases within those
methods; parameterized cases are not separately advertised as methods.

| Independently exercised behavior | Observed result |
| --- | --- |
| Literal A complete report, original bytes and decoded identity | Exact two printed SHA-256 values, 60 bytes, offset 44, data size 16, two chunks, four stereo frames, complete exact report surface. |
| Six encodings of A: PCM16/24/32, WAV float32/64, explicit raw float32 | All share the exact printed decoded identity; all six original-file identities differ. |
| Changed digital rate, swapped channels and flattened mono geometry | Each matches its separate printed decoded hash and retains the specified geometry. |
| Literal PCM edge codes, both endpoints and one LSB at all three widths | Exact samples, endpoint/nonzero counts, width-dependent positive endpoints and distinct decoded identities. |
| Odd PCM24 data pad byte | Pad is excluded from samples and included in original-byte identity; alternate pad values preserve decoded identity. |
| Binary32 widening and binary64 detail below binary32 resolution | Exact returned samples, with no unwanted narrowing or normalization. |
| Literal C endpoints, headroom, signed zero and WAV rewrapping | Exact two printed hashes, RMS `0.875`, six nonzero values, two endpoint and two over-range samples; clipping remains unknown. |
| Silence and signed zero | All output zero samples and zero-valued statistics have positive-zero binary64 representation; diagnostic counts remain zero. |
| Least binary64 subnormal and binary32 subnormal | Peak, RMS, DC and returned samples remain exact nonzero values; the binary64 four-sample requirement is checked without generic absolute tolerance. |
| Float64 cancellation and mixed magnitudes | DC/RMS satisfy independent exact-stored-value Decimal calculations. |
| Antiphase and constant channels; 16-channel fixtures; rate endpoints | Channels remain separate and ordered, with exact frame-major digest and channel-planar windows. |
| First, last, whole and interior windows | Exact half-open selection without padding/shift; nested inspection equals the full-file API report. |
| Independent returned values and unchanged source | Mutating one returned object affects neither another result nor the source bytes. |
| Opaque ancillary chunks, arbitrary pad values, LIST/INFO, zero format extension and optional fact placement | Accepted layouts retain decoded audio; all original bytes contribute to file identity. |
| Filename suffixes, Unicode names and relocation | Observed bytes decide format; relocation changes only the reported input path. |
| WAV assertions and explicit raw declarations | Wrong WAV assertions reject; missing raw geometry rejects; valid declared raw geometry is retained without a physical inference. |
| Raw scalar whose four bytes spell RIFF | Explicit raw selection decodes the scalar instead of guessing container intent. |
| Binary32 NaN/infinities before, inside and after a window; binary64 and raw equivalents | Every entire call rejects; the first bad frame/channel and its byte position are retained. |
| Magnitude boundary `+/-1e6` and adjacent excessive values | Inclusive boundary admitted with exact statistics; positive/negative excess rejects even outside the requested window. |
| Integer type and window arguments | Boolean, floating and string substitutes are rejected; nonpositive or out-of-file windows fail without truncation. |
| 90,000-byte PCM24 three-channel stream | Complete byte/digest identity, statistics and a window crossing the 65,536-byte read boundary match separate expected values. |
| CLI from a foreign working directory, Unicode path, raw/window mode and direct `main` | Required report, deterministic canonical JSON bytes, successful statuses and human-readable help. |
| CLI usage, missing-file and assertion errors | Exact stable envelope, required exit 1/2, empty stdout and canonical finite stderr JSON. |
| Exposed resource constants | Every declared constant matches the frozen contract's type and value. |

### Initial test-control failure and correction

The first run reported 41 methods with one failure. All assertions against the
decoder passed. The failing assertion was an auxiliary control intended to show
that naive sequential addition loses accuracy for
`[1e6, 1e-9, -1e6, 1e-9]`. It mistakenly used built-in `sum(values)`. On the tested
Python 3.12.14 runtime this produced the same DC as the Decimal oracle, so its
claimed naive error was zero.

The test now uses an explicit `naive_total += value` loop for that control. The
loop exhibits the intended error greater than `2e-12`, while the decoder retains
the original independent Decimal acceptance checks. No production code or
tolerance was changed to resolve the test-control mistake. The complete suite
was then rerun successfully as reported above.

## Limits and next handoff

This suite is assigned numerical/format/sample-identity and ordinary public
API/CLI acceptance. Worker 24 separately owns deep malformed-container,
maximum-resource, read-buffer, filesystem-alias, unavailable-identity,
descriptor-cleanup and controlled-mutation acceptance. Crossing a read boundary
here checks data order; it does not alone attest every production read size.
The exposed constant checks do not substitute for exercising their enforcement.
No native Windows reparse test, full maximum-stream run or hosted CI outcome is
claimed. No C++ engine or native host validation ran in this assignment.

Root should rerun this maintained suite from the coherent integration source,
combine the separate rejection/filesystem acceptance, and execute unchanged
legacy analyzer/capture suites before publishing the supported-tool checkpoint.
Physical specimen identity, real recordings, clock/scale calibration,
permission, acquisition history and instrument fidelity remain unestablished.
