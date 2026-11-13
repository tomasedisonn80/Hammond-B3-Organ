# Development log

Every future agent must append actual changes and executable evidence here or
provide an assigned note for the integrating agent, then update the status and
next-step documents. See the mandatory instructions in `../AGENTS.md`.

## 2026-11-12 — Initial implementation session (in progress)

- Baseline repository commit: `501c68ba44c16e8a787bba69a272d4c44fe5308a`.
- Source: 500-page research atlas, 21,248,265 bytes, SHA-256
  `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
- Confirmed repository contained only the PDF and minimal README. Referenced
  companion assets were absent. Extracted all 500 pages for bounded review;
  no page lacked extractable text. Temporary extraction is outside the repo.
- Assigned complete coverage to agents 01-06 with disjoint inclusive ranges.
  Their committed notes retain exact page ranges and visual-review coverage.
- Established `AGENTS.md`, source manifest and M0-M2 implementation contract.
- Published `93924088e6de8879b8f13a69bc20a4016b5742cd` to `main` and fetched
  the same remote head. CLI push lacked a configured credential; the connected
  GitHub API published the commit with an expected-head guard.
- Build environment: GCC 14.2.0, GNU Make 4.4.1, Python 3.12, CMake 4.4.4
  installed in temporary task-local tooling. No host audio SDK required.

This is an intermediate record; no engine/test/release pass is claimed here.

### Wave 01 — complete atlas review

All six assigned ranges were read: 1-84, 85-168, 169-252, 253-336,
337-420 and 421-500. Each reviewer retained its exact coverage and inspected
selected figures. The combined review identified the complete M0-M9 sequence,
recoverable routing/preset/pedal data, missing companion assets, proposed versus
measured evidence boundaries, scanner pseudocode/equation issues, and separate
organ/Leslie/host/UI gates. See notes01-06 in `development/agent-notes/`.

Wave02 begins the typed profile contract, strict authoring compiler and build
foundation. No hardware fidelity claim has changed.

### Wave 02 — profile and build foundation

Agents07-12 implemented fixed-size C++20 types/profile loading, strict JSON
authoring validation and deterministic compilation, CMake/Make/test tooling,
independent permanent tests, and full atlas navigation/errata/source notes.
The profile explicitly contains91 sources,549 manual routes and9 drawbar gains.

Observed verification: strict GCC14 Debug and Release builds;37 Python unittest
cases;2,601 malformed C++ payload cases with field-preserving rejection; exact
byte limits, six printed routing rows, source anchors, locale and I/O failure
checks. The source PDF hash and500-page/80-chapter coverage were rechecked.
ASan+UBSan passed for the profile test with `ASAN_OPTIONS=detect_leaks=0`. Default
LeakSanitizer finalization failed because the executor runs under ptrace; leak
checking is not claimed. No Windows/macOS or host/audio fidelity result yet.

Profile identities: canonical authoring SHA-256
`49791eac8d0b556b0abd2018b8cabc6f240161edab8a9fa0ef97905f2badda83`;
compiled bytes SHA-256
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.

Wave03 implements the shared bank, dry graph and renderer against frozen timing
and file contracts. See individual notes07-12 for exact commands and limitations.

### Wave 03 — working shared sources, dry engine and offline audio

Agents13-18 implemented a value-owned91-source sine bank with deterministic
SplitMix64 initialization, transactional dry Engine, strict offline CLI/WAV writer
and independent permanent source/engine/CLI tests. The core shares each source
sample across every routed contact and adds branch gains coherently. It does not
restart phase on notes or normalize by polyphony.

Observed checks: all supported rates44100/48000/96000;440 crossings in1second for
tone46; long-double phase/sine oracles; coherent doubling6.020599913dB; stable ties,
flushes, disconnected rendering, caller-owned profile changes and failure atomicity.
The2053-frame engine timeline matches bitwise over blocks1/17/64/127/512/1024.
The CLI's20 retained unittest cases include dense subdivision, little-endian WAV
headers/channels, clipping/no-clobber failure and partial-final-block handling.
A separate3856-event smoke matched blocks through65536; its concurrent destination
race preserved the other writer's file. No hardware, host or deadline pass follows.

The callback currently has discrete control steps and ideal gates. Native automation
curves, hot profile exchange and physical circuit/rotary stages are deferred.
Wave04 adds an explicitly exclusive four-bank model and Cancel while preserving
legacy audio. Permanent notes13-18 identify actual commands and limits.

### Wave 04 — early console state and documentary control data

Agents19-24 added four retained A/B drawbar banks, route-only Cancel, explicit
bank events, snapshot restoration and bounded `B3CONTROLS1` serialization.
The39-entry internal parameter registry has permanent bank identities but no
verified native host mapping. Pedal data reconstructs25x8 contacts with195
connections and5 nulls; pedal audio, physical weights and full transcription
verification remain open.

Strict Debug/Release control and legacy engine/CLI tests passed. The integration
matched the frozen wave03 renderer in24 WAV-byte/JSON comparisons. New timeline
tests cover3 rates and6 partitions, held-key switching, Cancel/reselect/panic,
all91 phases,81 malformed snapshots and68 invalid new-event calls. Control I/O
rejects330 malformed inputs atomically. Registry19 and pedal15 Python tests pass.
Root updated the legacy invalid-enum test from5 to255 because5 is now the
documented BankDrawbar event; the invalid-enum assertion itself remains.

No physical contact, percussion, multi-preset latch, pedal-audio or host gate was
closed. Current tasks move to render provenance, fixtures and independent evidence.

### Primary-source acquisition during wave 05

The coordinator retrieved the atlas-linked 220-page factory service scan from
Audiofanzine for documentary review. Its SHA-256 is
`ec2ac51f363dcd1ee039f7711acda32fd014e15ad80dcb77ae199545f9130cc9`
and its byte size is 7,077,593. PDF pages 155–157 contain Table III, including
the manual and pedal source assignments. The file is retained outside the
repository for review; no additional manual is redistributed. This acquisition
opens independent transcription work in wave 07 and closes no physical gate.
The separate Synthmania compilation was accessible to web extraction, but its
direct download returned HTTP 406; it was not used for numerical verification.

### Wave 05 — initial render evidence and CI infrastructure

Agents 25–27 added a bounded reproducible renderer wrapper, five explicit event
fixtures and an independent streaming PCM16 analyzer. Their targeted suites passed
14 wrapper tests, the five-render catalog checks and 15 analyzer tests with an
actual C++ renderer. The A4 steady-window crossing estimate was
439.9999816417002 Hz at a 48 kHz file rate; this is a serialized nominal fixture,
not a measurement of a physical generator. No fixture clipped.

Agent 29 added pinned official GitHub Actions, three Release platforms and a
Linux ASan/UBSan/leak job, with read-only repository permissions and retained
diagnostics. Initial hosted status is pending. Agents 28 and 30 continue the
callback boundary audit and independent bundle verification. The coordinator
will test a clean staged snapshot before publishing this evidence checkpoint.

### First hosted CI result — `b9c1cac`

[Run 43361632464](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43361632464)
passed all 12 CTest suites on Linux Release and Linux GCC ASan/UBSan with
`detect_leaks=1`. macOS AppleClang 17 compiled against a libc++ without floating
`std::from_chars`, failing in control parsing. Windows MSVC compiled with zero
warnings/errors and passed 10 of 12 suites. The fixture catalog caught Git
checkout CRLF hash changes; the evidence wrapper rejected unchanged files at its path-stat/descriptor-stat
comparison, and one raw subprocess fixture expected a POSIX
newline. These are recorded failures, not waived checks. Wave 06 will implement
portable decimal conversion and evidence file handling; a later hosted run must
verify the changes. No native host/audio-device claim follows from CI.

### Wave 05 completion and wave 06 robustness

Agent 28’s calibrated global C++ allocation probes observed zero allocation and
deallocation calls during 63 accepted and 33 rejected prepared callbacks, covering
216,255 frames and 23,919 events. Static inspection found only fixed storage and
bounded project callback work; linked math internals, C/system allocation, other
threads and timing deadlines remain outside that evidence. Agent 30’s independent
bundle consumer passed 27 test methods against actual renders and mutated
artifacts. It keeps integrity, authenticity, build provenance and fidelity distinct.
All six wave-05 assignments are complete.

Agent 31 reproduced an original stream-buffer runtime exception escaping the
profile loader. A narrow bad-stream exception handler and nine deterministic
failure/recovery cases now pass, alongside five existing Release core suites.
Portable numeric parsing and Windows evidence handling are in progress; combined
changes require integration and actual hosted qualification. A separately reported
extreme-frequency phase-stall case is assigned to the numerical boundary review.

### Portable numeric and evidence repairs

Agent 32 replaced floating `from_chars` with one shared classic-locale decimal
converter, preserving integer parsing, strict syntax, finite/subnormal range
handling, signed zero, nearest rounding and failure atomicity. Its new vectors
cover 16,547 accepted exact/round-trip values and 106 invalid tokens; all 16
then-current Release suites passed. The canonical nominal profile and compiled
profile identities remain unchanged.

Agent 33 preserved raw artifact identity across Git checkouts with LF attributes
and repaired invalid cross-API file-stat equality in both hash and WAV readers.
Within-API before/after checks, regular-file bounds, raw hashes and POSIX
device/inode binding remain. It reproduced all five bad Windows score hashes
from CRLF conversion and tested an isolated autocrlf checkout. Nineteen wrapper
methods, the five-render catalog and 27 independent verifier methods passed.
Raw output capture still preserves its bytes. An actual hosted rerun must close
the macOS/Windows gates. Root updated the stale Profile.cpp parser comment.

### Hosted portability repairs verified — `9c8068c`

[Run 43363048563](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43363048563)
completed successfully. All four jobs passed all 16 registered suites: Linux GCC,
macOS AppleClang and Windows MSVC Release, plus Linux ASan/UBSan with leak
detection enabled. The macOS numeric replacement and Windows evidence repairs
therefore have actual hosted results. These jobs qualify only the tested offline
software scopes; audio-device, host, hard-deadline and physical gates remain open.

### Wave 06 completion — numerical and tooling boundaries

Agent 34 reproduced a positive source increment that rounded away, then added
an atomic preparation rejection below `2^-53` turns per sample. Four affected
Release suites passed. The 262,144-frame nominal check at each rate observed
maximum circular phase error `7.722181563901e-12` turns within its derived
`3.637978893828e-11` budget. The source/sample recurrence and nominal profile
bytes remain unchanged; progress near the new support floor is not an accuracy
claim. The synthetic maximum mix reached both signs of 1,098 finite coherent
branches without asserting physical output level.

Agent 35 added a bounded four-case prepared-engine benchmark and CMake target.
Strict Release build, 16 individual-versus-all workload equivalence checks and
29 invalid argument/work/profile rejections passed. Its temporary shared-tree
run includes a scheduling outlier beyond the nominal interval; no deadline gate
was inferred. Final publication uses a new immutable staged snapshot.

Agent 36 added a read-only source-archive checker with 41 passing mutation/CLI
methods and a real-PDF smoke. It checks source identity, reconstructed index and
review coverage, local Markdown file links, actual note IDs and existing data
hashes without Git or built artifacts. The optional exact agent-count check is
reserved for the relevant snapshot/final session. All six wave-06 assignments
are complete. Wave 07 now compares two independently frozen factory readings
and prepares explicit acquisition metadata and acceptance procedures.

### Wave 06 published checkpoint and remaining hosted failures

Commit `7c2ad20` matches the tested staged tree
`a3416cd144e8ae07f291434aa0b883b5a61796f4`. Its clean Release build passed
18/18 CTest suites, the source checker passed with exactly agents 01–36, and
the four-case benchmark completed with its qualified timing report.
[Hosted run 43364414017](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43364414017)
passed Linux and macOS Release. Windows passed 17/18 suites but three checker
assertions expected forward-slash origin paths while diagnostics used native
backslashes. Root changed that repository-relative diagnostic to `as_posix()`;
all 41 existing checker methods pass locally. The sanitizer job passed 17/18
suites and failed the executable-mutation evidence test at an unexpected error
stage. The cause remains under investigation; no failure is waived and the
checkpoint has no complete hosted qualification.

### Wave 07 independent factory routing evidence

Agents 37 and 38 independently entered and froze the factory Table III manual
and pedal cells before comparison. Agent 39 compared each reading against the
other and the original project data: all 549 manual assignments and all 200
pedal positions agree, including all five disconnections. The raw profile,
canonical profile and compiled profile hashes remain unchanged. The new
provenance manifest and validator pin the documentary scope separately from
the original authoring metadata. Twenty mutation methods passed; all compiled
routes also match both readings. Original pedal and compiler suites passed.

The source scan is 220 pages with the previously retained hash. Correct table
locators are PDF 155–157 / printed 3-76 through 3-78. Exact factory edition and
production revisions remain unestablished. No additional manual/images are
redistributed, and no gearing, specimen, calibration or physical-audio claim
follows. Shared current-status documents now distinguish completed documentary
routing corroboration from the remaining physical M2 gates.

### Wave 07 capture metadata and independent validation

Agent 40 added an original proposed capture schema, planned example and bounded
standard-library validator. It separates header rate from physical sample clock,
declared calibration from verification, and metadata checks from explicit file
checks. Unknowns retain reasons; local ancestry and grouping are explicit. The
only committed example is planned, with no fabricated acquired evidence.
Agent 41 independently constructed 39 passing methods and ran the selected
CTest gate successfully. The examples used for file tests contain only temporary
synthetic bytes; hardware declarations used for semantics remain in memory.

Root then reproduced an alias-check gap with real linked files and simulated
unavailable descriptor identities. The byte checker now uses a nonzero path
identity as fallback and rejects if neither API supplies an identity. Two targeted
regressions bring the capture suite to 41 passing methods. This is an observed
contract gap under the simulated metadata condition, not an observed Windows
runner failure. Metadata/file passes establish neither physical calibration nor
rights, authenticity, signal format or specimen fidelity.

Agent 42 completed the acquisition protocol after reading atlas pp. 109–156
and 349–366. It maps specimen/permission lock, the external pilot, dry sources,
contact/percussion/expression work and later circuit/cabinet captures to the
actual v1 fields. Whole takes, synchronized channels, chunks and derivatives
retain one grouping identity; a separate corpus ledger must govern validation
and untouched final holdouts. Its planning fragments validate without timestamp
or file claims, and all ten local links resolve. All six wave-07 assignments are
complete. Wave 08 addresses observed CI failures and local installation/usability.

### Wave 08 CI audit and local installation

Agent 43 audited all four complete diagnostic archives for `7c2ad20`: each
contains 18 suites and 195 Python methods with zero test skips. The report retains
exact toolchains, artifact IDs/hashes and both failures. The executable mutation
test now prepares a separate modified copy, replaces the checked path after real
execution and verifies both hashes. It still requires the exact integrity error
and additionally requires a successful child and complete logs. Nineteen methods
passed against Release and local ASan/UBSan binaries. The original hosted exception
remains unestablished; local original-method probes did not reproduce it. Local
leak-enabled execution explicitly failed under ptrace, so local instrumented checks
used `detect_leaks=0`; hosted leak qualification remains required.

Agent 44 added the OfflineTools local install component and a real relocation
test. It installs exactly the renderer, generated profile and six fixture/catalog
files, then moves a prefix with spaces and compares actual PCM, full WAV bytes
and JSON against the build renderer. A temporary changed installed profile affects
identity/output, and its removal rejects without fallback. Default and custom
relative layouts passed; missing build inputs and unsafe install destinations
rejected before copying. No dependency, system install, runtime bundling, plugin
or device application was added. The combined checkpoint now requires its clean
staged build and new hosted matrix results.
