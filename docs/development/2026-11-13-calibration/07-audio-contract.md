# Assignment 07: frozen audio inspection contract

## Identity and scope

- Actual canonical worker: `/root/cal_w2_a07`; calibration wave 2, assignment 07.
- Date: 2026-11-13. Observed starting HEAD and local `origin/main`:
  `08fa8de8f718584c4ee4ab3b392c779f3290289c`.
- Owned files: [CAPTURE_AUDIO_CONTRACT.md](../../CAPTURE_AUDIO_CONTRACT.md) and
  this note only. Root owns shared documentation, accounting, integration and git.
- Read `AGENTS.md`, calibration/capture scopes and contracts, current operational
  context, plan, atlas review and all six current-session atlas notes. Inspected
  existing `analyze_wav.py`, `validate_capture.py` and audio-measurement documentation.
  This assignment does not claim a seventh fresh reading of the source PDF.

## Frozen decisions and actual work

Authored `capture-audio-v1` before worker 13 implementation. It defines the exact
`inspect_audio` and bounded `read_audio_window` signatures, return dictionaries,
`AudioError` codes, deterministic JSON CLI, streaming/statistical behavior,
file-identity checks and direct-path versus capture-root rules. Existing analyzer
and metadata-validator APIs and meaning remain unchanged.

Admitted formats are plain little-endian RIFF PCM16/24/32, IEEE float32/64, and
explicitly declared raw float32 little-endian. Extensible WAV and FLAC are explicitly
unsupported in this first decoder. Original and canonical decoded SHA-256 remain
separate. The canonical digest uses the exact frozen domain prefix, little-endian
rate/channel/frame integers and frame-major binary64 normalized samples, with
signed zero folded. Root accepted the digest and unsupported-format boundary;
assignment 08 received the API/digest early for its corpus contract.

The limits retain capture v1's 256 MiB/rate/channel bounds, add one-hour audio,
4096 chunks and explicit work bounds, and retain at most 262144 frames/1048576
scalar samples/600 seconds per window. Root accepted these bounds. Finite samples
with magnitude at most `1e6` permit useful statistics without overflow; this is
explicitly numerical policy, not an ADC or physical threshold. Complete-stream
validation still applies outside a requested window.

Coordinated the raw/derived boundary with root and assignment 08: raw files match
v1 `digital` only, while derivative audio uses its own corpus descriptor. Unlisted
derivatives remain uninspected; support files are uninterpreted. No derivative
borrows the raw acquisition's format/rate/channel count.

Consulted official Microsoft RIFF, WAVEFORMATEX and WAVEFORMATEXTENSIBLE documents
through search/open tools; their exact URLs are retained in the contract. The
format subset, limits, digest and acceptance tolerances are project decisions.

## Executed verification and limits

- Read-only checkout inspection used `git status --short`, `git rev-parse HEAD`
  and the local `origin/main` log; no fetch, commit or push was performed.
- A standalone Python 3.12.14 `struct`/`hashlib` calculation constructed the literal
  60-byte stereo fixture and verified the published file hash, canonical hash,
  rate/channel/geometry variants, PCM-edge formulas and raw-float hash. It did
  not import or implement the future decoder. Those explicit independent inputs
  and formulas are retained in section 11 of the contract.
- Basic document checks verified local links and the two owned files' formatting.
  The first arithmetic-sensitivity check incorrectly used Python 3.12's improved
  built-in `sum` as a naive sum; an explicit addition loop corrected that test
  setup and demonstrated the intended cancellation error. No decoder was involved.
  No audio implementation, decoder acceptance suite, hardware capture, numerical
  model fit, listening study, build, platform or publication gate was run here.

Next: worker 13 implements the frozen API, independently authored tests exercise
literal bytes and mathematical references, and root runs the old analyzer/capture
suites as compatibility evidence. Preserve unsupported formats, skipped platform
filesystem cases and all physical gates as visible limitations.
