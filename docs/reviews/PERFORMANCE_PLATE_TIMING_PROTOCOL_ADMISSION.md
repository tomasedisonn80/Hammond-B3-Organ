# P1 paint timing — independent prospective protocol admission

Reviewer **A25**, `/root/w05_a25`, wave 5, 17 November 2026 UTC. Scope:
the unchanged benchmark method in section 6 of the
[frozen P1 contract](../design/PERFORMANCE_PLATE_P1_CONTRACT.md), A23's exact
prospective runner and input manifest, the original/reproduced-before ancestry,
and the Flat-output evidence boundary. Root owns compilation, native execution,
quiet-interval scheduling, final admission and publication.

## Current decision

**ADMIT the exact corrected runner and prospective-v2 protocol for one fixed
eight-process timing batch on CPU 0, with the mandatory post-batch Flat-witness
gate below.** Runner SHA-256 is
`0a5b7a42a17a93bc44f0abab0d26ce0d05c955c511d0bb34fbf399fd611ffedb`;
protocol SHA-256 is
`9b9cef5f2c1ea0d6900c90ef6df63da5c5f7f9aaca9a91505f5b94192e2aa8f6`.
The independently verified same-scene raw capture now satisfies the exact-Flat
evidence requirement prospectively; both eventual timing Flat fingerprints
must additionally match its fingerprint. A mismatch blocks admission even if
the runner reports no timing investigation signal.

No new timing sample has been observed at this admission. This admits the
experiment, not its future outcome or P1 as a whole. The initial source review
missed an SDL environment-priority conflict; the first capture exposed it
before painting. That failure and its separately frozen environment-only
correction remain intact. The earlier different-state case-21 witness and
matching fingerprints alone were insufficient; no exact-pixel criterion was
waived.

The supplemental capture protocols below were fixed before their respective
source and execution admissions. Their specifications and observed outcomes
are retained separately. The original benchmark source, binaries, eight-process
order and 30/300 timing counts remain unchanged. Keep this final review and
its compact admission immutable after the timing claim is created; later
outcomes belong in a separate report.

## Initial v1 inputs and independently checked ancestry

| Input | SHA-256 |
| --- | --- |
| P1 contract | `20c8839d38229bf24d983eac0baad7381f601c4e6763bbbe556bcdfa6c75ae45` |
| A23 runner | `d53e5147cce85abb8bec3492dc2c63a9fd383be20d47fbc0ae606a78f0991f40` |
| A23 prospective protocol | `f8740307f5e5cadf86834bd0cf444c9ae98fe4200aa36ac80566b7a39cec2314` |
| Preflight result | `bef5a5b76e211efc2207a677b0a6e9d480835754babeeac70813db1b425fd860` |
| Unchanged benchmark source | `d81eb9412d6d885807e57b4657c58519309a3e2b830c904ff1b36d6b40569338` |
| Genuine retained before benchmark | `9f8b2eff710db91a1bb786e1093e6bf3c9df4f70160c76619447750db28a196f` |
| Coherent candidate benchmark | `5cf0d9046e05bf10178b70caee1c3996c719956dad364397ad7befbf46544d4e` |
| Retained before painter source | `10865a6bad39bc0a254b8b3f4cf6b013bef48770a2b39c7e9f9a70f438d56366` |
| Candidate painter source | `8ca5c05138ed4cd12fe8ef416ea35a3d78a8a3c4915645f53d8c0c0df2fcf927` |
| Newly compiled before painter object | `aee8d1b133e3fec7d7217a6d45efa7b02f890f23c448285868898f6cfb30fc72` |
| Existing candidate painter object | `5d3d7d40efbac24704c81944a70ffa1b3b1c4710a59556e87fdd96feaf59b790` |

The [prospective protocol](../development/2026-11-16-console-completion/reports/p1-timing-prospective-v1/protocol.json)
binds **1,507 input identities / 83,723,875 input bytes**. A25 independently
read and rehashed every registered file and checked its resolved path and byte
extent: no drift was found. The manifest covers sources, actual objects and
archives, 217 selected compile-command records, recorded Ninja dependencies,
generated headers, link inputs including system libraries and loader,
toolchain/configuration, pinned SDL source, original receipts, and retained
case-21 evidence. Linux x86-64 Release, GCC 14.2.0, SDL 2.32.10, MIDI/VST3 off
and sanitizer-off configuration are explicit. Compile/link scanning excludes
the paired and heap-observer macros and sanitizer/profiling flags.

The original before painter object **was not retained**. Root's
[reproduction receipt](../development/2026-11-16-console-completion/reports/p1-before-reproduction.json)
records a newly compiled object from the retained original painter, with the
same painter compile options and current selected link inputs. A25 directly
compared all **3,756,168 bytes** of the reproduced executable with the genuine
retained original: they are equal. This is strong supplemental reproducibility
evidence. It is neither an original-object receipt nor an observation of the
historical compiler invocation. The timing input remains the genuine retained
binary, never the reconstructed copy.

The independent before/after source inventory has precisely the reviewed P1
painter insertion and unrelated header-fixture literal repair. The latter is
absent from benchmark link inputs. Root's coherent relink receipt records
unchanged candidate benchmark bytes after adding the unused LibraryModel object
to the support archive. These facts bound the source argument; hashes alone do
not prove a build or physical fidelity.

## Fixed timing method

All eight processes run sequentially on **logical CPU 0**, chosen in A23's
prospective manifest before any new timing. The then-current and independently
rechecked allowed affinity was CPUs 0–8. Affinity is inherited before each
child starts and its observed affinity must be exactly `[0]`. CPU 0 must still
be allowed at execution; choosing a different CPU requires a new prospective
protocol, never an outcome-driven substitution.

| Order | Case | Side | Fixed arguments |
| ---: | --- | --- | --- |
| 1 | Canonical | Before | `1672 941 dimensional mixed-held` |
| 2 | Canonical | After | `1672 941 dimensional mixed-held` |
| 3 | Minimum active | After | `1400 820 dimensional mixed-held` |
| 4 | Minimum active | Before | `1400 820 dimensional mixed-held` |
| 5 | Wide | Before | `1920 1080 dimensional mixed-held` |
| 6 | Wide | After | `1920 1080 dimensional mixed-held` |
| 7 | Flat control | After | `1672 941 flat mixed-held` |
| 8 | Flat control | Before | `1672 941 flat mixed-held` |

The unchanged benchmark performs **30 warmup draws, 300 measured draws and
one final fingerprint draw** per process. That final draw is outside the
300-sample statistical set. There is no paired benchmark build, allocation
observer, sanitizer or profiler. The benchmark's renderer is software, with
fixed batching, scale 1, full viewport, no clip, Play workspace and no overlay.
The runner checks exact expected metadata, `paired:false`,
`alternating_order:false`, the unchanged scenario name and layout fingerprint;
it compares the complete emitted metadata across each pair except the expected
material-dependent pixel fingerprint.

The scene and state argument is the identical benchmark source, arguments,
model/Drawing dependencies and native before/after paint assertions. The
unchanged executable does not serialize a complete copied state; it must not
be described as doing so. It checks applied controls, held keys/pedals and the
field-wise layout fingerprint. Detailed model/state preservation has its
separate native matrix. Similarly, the renderer metadata is exact emitted
metadata with source support, not a new external renderer-state probe.

The corrected child environment is explicitly reduced to PATH, C locale, UTC,
dummy SDL audio/video and software rendering. The unchanged native setup must
successfully set the SDL batching **hint** to 1. Parent relevant environment,
host/kernel/CPU information, boot identity, affinity, load, scheduler/nice,
UTC bounds and available cgroup observations are retained. Unavailable cgroup
files are recorded as unavailable. Root must stop its coordinated builds,
captures and other native workloads and record its actual quiet-interval
statement. Neither affinity nor that statement establishes shared-host
isolation, a reserved physical core or causal attribution.

### Statistics and decision

The runner requires all 300 nonnegative integer nanosecond samples and sorts
them without deleting or weighting any observation. Median is the sum of
one-based positions **150 and 151**, divided by two; p95 is nearest-rank
position **285**. Half-nanosecond medians are retained exactly as integer
twice-median values. Minimum and maximum are independently recomputed.
Rounded native summaries must agree within their six-decimal millisecond
printing precision. Supplied paint and flush/present minimum, maximum, median
and p95 are retained. Component raw samples are unavailable, so those supplied
summaries are not advertised as independently recomputed.

For **each** case and **each** of total median and total p95, HOLD applies
exactly when growth is **strictly greater than 2 ms AND strictly greater than
15%**. Integer cross multiplication decides both tests; rounded display values
cannot move a boundary. Either metric's signal holds the case. Equality at
2 ms or 15% does not trigger this investigation screen. Flat receives the same
timing screen as the three dimensional cases.

A25 independently checked a shuffled 300-value synthetic sample set against
`statistics.median` and an exact rational nearest-rank oracle, seven threshold
boundary examples including half-nanosecond median steps, and twelve parser/
metadata refusal cases. All passed. These were Python-only synthetic checks;
they are not native timings or observations of future benchmark output.

There is no pooling across cases, trimming, replacement process, adaptive
order or rerun to obtain a pass. An exclusive execution claim is written
before the first launch and retained even on failure. A reaped failed process
does not erase the attempt; the fixed remaining order continues. Source/input
drift, affinity loss, interruption, unreaped child or batch deadline stops the
batch with the remaining commands explicitly unattempted. Any later batch
requires its own prospective reason and independent review.

### Bounds and failures

Each native process has a 180-second deadline; the eight-process launch/run
budget is 1,500 seconds. Kill/reap handling is bounded by two seconds per
operation. Stdout is limited to 131,072 bytes and stderr to 65,536 bytes per
process, at most 1,572,864 retained raw stream bytes across eight processes.
Ordinary successful or failed output within those ceilings is retained in
full, with exact identities, errors, exit codes, timestamps and pipe-EOF
observations. A flood is terminated and its bounded prefix is explicitly
marked truncated/incomplete; such a batch is invalid and cannot claim complete
raw output. Raw failures, invalid parses and interrupted attempts are never
replaced by a later pass.

All registered inputs are checked before and after the complete batch. The
executable, runner, contract, protocol and admission identities are additionally
checked around every process. Root must prevent any source/object/dependency
edit or build during the batch. Endpoint hashes are drift checks, not continuous
monitoring or proof against an intervening change that is later reversed.
Full input hashing and final report serialization are outside the stated
child-run deadline; the runner has no hard whole-program wall-clock promise.

## Exact Flat boundary

The unchanged benchmark's `pixels()` function computes FNV-1a-64 over each
row's `width*4` bytes; it emits the fingerprint only. Equal fingerprints are
an identity check with possible collisions, not a comparison of unavailable
raw bytes.

A25 independently decompressed the original before/after case-21 stdout,
parsed its native header and directly compared all **1,573,352 pixels /
6,293,408 RGBA bytes**. They are identical; SHA-256 is
`70f30d76234c43b44fd77c5f91fd55013766f43845be5605297acab5d8c6f9c6`.
That evidence remains usable for its particular Flat fixture despite the four
unrelated original Rotary/Service focus-oracle failures. The original whole
v1 report remains failed, with all four failures retained.

Case 21 uses all-level-4 banks, expression 0.625, pedals 3/7 and held Upper 24,
Lower 36 and Pedal 12. The benchmark uses varying banks, expression 0.75,
pedals 8/0, fixed Upper CSharp, Lower bank A, held Upper 24/25, Lower 0/60 and
Pedal 3. Therefore case 21 cannot supply missing raw bytes of the benchmark
scene. A25 also verified that the entire `paint_instrument` source suffix is
byte-identical and P1 is inactive in Flat. That source argument supports
preservation but does not convert a different captured scene or digest into
same-scene raw evidence.

### Supplemental capture-only protocol v1 — frozen before execution

The purpose is exclusively to supply exact raw Flat pixels for the unchanged
timing scene. It supplies no new timing sample and cannot improve or repeat a
timing result.

1. Root authors one small companion translation unit that includes the exact
   unchanged benchmark under a renamed unused entry point. Its capture path
   copies the benchmark's complete scene/setup block verbatim, retaining all
   model defaults, controls, held notes, fixed information strings, renderer
   construction, Drawing initialization and validation. A25 checks the exact
   source and SHA-256 before compilation. The capture path must never call
   `Clock::now`, the benchmark's `draw`, `run` or renamed original entry point.
2. Root compiles the companion with the benchmark's admitted Release options
   and links two separate capture executables. Only the selected painter object
   differs: the newly reconstructed before object named above and the existing
   candidate object named above. All other project and system link inputs must
   match the reproduction receipt. Record exact source, object, dependency,
   compiler, commands and resulting executable identities. This before capture
   uses the reproduced object; it is not called an original-object capture.
   Neither timing executable is modified or replaced.
3. Freeze exactly **two** fresh capture processes in **before, after** order,
   both with `1672 941 flat mixed-held`, CPU 0 and the timing runner's exact
   child environment. Each process calls the actual selected painter, then
   `SDL_RenderFlush` and `SDL_RenderPresent`, exactly **331 times**, matching
   the timing process's 30+300+1 rendering history without reading a clock or
   collecting durations. No other native capture, retry or selection is part
   of this supplement.
4. Export one JSON header no larger than **65,536 bytes**, followed by exactly
   **6,293,408 pitch-free top-to-bottom RGBA bytes**, row stride 6,688. Require
   the frozen dimensions, Flat/Play/mixed-held/none metadata, 331 calls,
   zero timing samples, software renderer, fixed SDL version/batching/transform,
   copied-state/layout validation and a fingerprint calculated by the existing
   benchmark's pixel routine. No extra stdout bytes or trailer are allowed.
5. Bound each process at **180 seconds**, the two-process run at **370 seconds**,
   each stderr at **65,536 bytes**, and each stdout at the header ceiling plus
   its newline and exact raw pixel extent. Retain full streams within those
   bounds, process records, UTC/affinity/environment observations and before/
   after source/object/dependency identities. Kill/reap and output-overflow
   refusal follow the timing runner's bounded policy. Explicitly retain any
   failed or truncated attempt and stop without an automatic retry.
6. A25 independently checks matching headers/state/layout/renderer evidence,
   exact raw extents and **direct byte-for-byte equality** of both RGBA payloads.
   Independently recompute FNV-1a-64 from the retained raw bytes and require it
   to match both capture headers. Retain SHA-256s for both full streams and
   their RGBA payloads. A digest comparison cannot substitute for the direct
   byte comparison.
7. Bind the accepted companion source/build/process/raw evidence in the final
   SHA-pinned timing admission. During final timing-result admission, require
   **both timing Flat fingerprints to match this raw witness's independently
   recomputed fingerprint** in addition to matching each other. Frozen runner
   v1 enforces the latter pairwise comparison; the cross-witness check is an
   explicit independent root/admission gate unless a separately frozen runner
   revision adds it. Any mismatch is HOLD, with no replacement samples.

The exact same-scene raw observation, source/build linkage and final fingerprint
cross-check together supplement the existing benchmark method. They do not
claim that the unchanged timing executable has begun exporting raw bytes.
Compilation, captures and final witness admission remain unrun in this initial
protocol review.

## Companion source admission before compilation

**ADMIT source `af2a675a5aeb7925d2a752f9897eca7bf5d70aa0b55aac1c1476d869c0e227ad`
for root's compilation and exactly two capture processes under the frozen
supplement above.** This admits no timing process or capture result yet.

The [companion](../../tools/standalone_flat_pixel_capture.cpp) includes the
unchanged benchmark with only its `main` identifier renamed. Its new entry
calls only `capture_fixed_flat`, never the original `run`, `draw`, renamed
entry or `Clock::now`. The capture path rejects every argument combination
except the frozen Flat scene. Both forbidden benchmark build macros cause a
compile-time error.

A25 directly compared the marked **3,989-byte setup block** with the original
benchmark's run prefix: it is identical, SHA-256
`93cd6e9212287d9dc0c2c439bf19f5c2cb3471a81697b857c69a8d2010a19e02`.
The **330-byte copied-state/layout preservation assertion** is also identical.
The direct painter/flush/present loop has 331 iterations, with compile-time
assertions for the original 30/300 constants. The fingerprint is read after
the loop and raw bytes are exported from the same unchanged completed surface.
Rows exclude pitch padding, and output contains no extra render or trailer.

The source-reviewed header records the actual SDL version, software-renderer
name/flags, surface format, batching, layout and final pixel fingerprints;
fixed dimensions, transform, Flat/Play/mixed-held/none scene; RGBA packing and
extent; 331 paints; zero timing samples; no paired/heap mode; and successful
preservation assertions. A requested precompile metadata addition supplied
overlay, actual batching/surface format and the preservation-assertion flag.
The original draft hash `2218f1f494e65f204e8fd30b0aeba61aed685afeedec33afe4745c68e2eeb661`
was never compiled or executed. The setup, preservation assertion and loop
were unchanged by that addition.

Root will retain complete stdout losslessly as `.stdout.gz`, with compressed
and original raw identities, plus complete stderr and process/build receipts.
Lossless storage does not change the required direct comparison after bounded
decompression. A truncated/error stream cannot satisfy the witness. The
original benchmark code remains included but its clock/statistics paths are
unused by this entry; the companion's binary containing those unused paths
does not make these capture calls measured samples.

## Retained setup failure and prospective environment correction

The two-process capture driver source was frozen as
`a0d5fbe06e71ac6ef9f44522055a1a8595e785b7040ce2bbed5ed64339c01b39`.
It reuses only the reviewed timing transport with the explicit capture limits
and raw-pixel validator. Its first **before** process returned exit 1 after
0.13865754099970218 seconds, with empty stdout and this complete 54-byte stderr
message (newline escaped):

```text
"Flat capture failed: enable fixed renderer batching: \n"
```

The failure occurred at the setup assertion before `SDL_Init`, renderer
creation or any paint. The driver stopped; the **after process was unrun**.
The [original failed capture report](../development/2026-11-16-console-completion/reports/p1-flat-witness-v1/report.json),
SHA-256 `02646a116a93a234ac7826d00a65bf1a8e7811a8f54bda21bac7c0402b75a521`,
retains CPU-0 affinity, both stream EOFs, no truncation, the zero timing-sample
claim and zero recorded source/object drift. Raw stderr SHA-256 is
`ce5d03b4a2cbb576eb13de8e3e9f9143e681cf9a2f6a938f7188096f7c75dae9`.
The complete streams, compressed copies, source and original protocol remain
retained. This is an observed setup failure, not a rendering or timing result.

A25 independently inspected pinned SDL 2.32.10 `src/SDL_hints.c`, SHA-256
`6fb9bc23d140ff5cee40149b50c02780e10e02efdbca6ffaf3abfa661e5b7ad5`,
and `include/SDL_hints.h`, SHA-256
`96c1056e0734f019b1dafed5129d4a9d36253559ed8c7577a23c188bb75a48c1`.
`SDL_SetHint` calls `SDL_SetHintWithPriority` at `SDL_HINT_NORMAL`. The latter
immediately returns `SDL_FALSE` whenever the named environment variable exists
and the priority is below `SDL_HINT_OVERRIDE`. It does not first compare the
requested value with the environment text. Thus setting `SDL_RENDER_BATCHING=1`
in the runner environment causes the unchanged benchmark's required
`SDL_SetHint(...,"1")==SDL_TRUE` to fail even though the text is the same.
The first independent source review missed this interaction. The same issue
would affect every timing-v1 process; no such timing process has run.

### Supplemental capture-only protocol v2 — prospective correction

**ADMIT the narrowly defined environment correction and a separately frozen
two-process capture-v2 attempt before timing.** This is a new prospective
reason/protocol following the retained setup failure, not automatic retry or
selection of a better timing result.

Only remove `SDL_RENDER_BATCHING` from the explicit clean child environment.
The unchanged native code then sets batching to 1 at normal priority; every
accepted capture and timing output must still report effective
`render_batching:"1"`. Keep PATH, C locale, UTC, dummy SDL audio/video and
software-render-driver entries exactly as before. Do not change the benchmark,
companion, painter, either timing/capture binary, 331 capture calls, 30/300
timing counts, process order, CPU 0, limits, raw-byte criterion or statistical
thresholds.

Preserve exact original timing-runner and capture-driver source snapshots
before editing. Freeze the corrected timing source in a **new preflight-only
v2 protocol** with zero native timing launches. Freeze a new capture driver
with only the required runner-hash and new-output-directory changes in
addition to the inherited environment correction. Root's new capture uses
fresh `p1-flat-witness-v2`/`flat-raw-v2` directories, exactly before then after,
and all unchanged supplemental-v1 bounds and acceptance above. Any new failure
stops and remains retained; this amendment authorizes no additional automatic
attempt.

A25 must inspect the final corrected source and hashes before either v2
capture process, then independently admit the retained raw result. The new
timing protocol and final admission must name this explicit cause/correction;
the old prospective timing-v1 protocol is not the execution authority.

## Corrected source admission before capture-v2

**ADMIT exactly the two capture-v2 processes under the preserved v2 prospective
amendment.** A25 inspected the corrected sources and new timing preflight
before root launched this separately authorized capture attempt.

| Corrected input | SHA-256 |
| --- | --- |
| Timing runner | `0a5b7a42a17a93bc44f0abab0d26ce0d05c955c511d0bb34fbf399fd611ffedb` |
| Timing prospective-v2 protocol | `9b9cef5f2c1ea0d6900c90ef6df63da5c5f7f9aaca9a91505f5b94192e2aa8f6` |
| Timing preflight-v2 result | `f0e04c63f906935409cbd59d3b367b263510beceb66be53a875b22db76c05c81` |
| Capture-v2 driver | `a504823e3e517cc116e8ff2ca80267b9e5e95b9294e13b5f1229687305b15164` |
| Preserved prospective environment admission | `3396a17b782fbc7a497cdfd9d54400985f2deccf1eafcbda150b3f1b19411392` |

The timing-runner diff removes exactly the 28-byte environment entry and
changes no other source. The capture-driver diff changes only its runner and
admission hashes, admission-snapshot path and fresh-v2 output paths. The
exact original source snapshots reproduce their prior hashes. The companion,
both capture binaries, both timing binaries, statistics, order, limits and CPU
are unchanged. The new preflight executes zero native processes and retains
**1,507 references / 83,723,847 bytes**. Comparing old and new input manifests
finds only the runner identity changed. A25 independently rehashed the entire
new input manifest without drift; no timing execution claim existed.

The initial environment-admission snapshot is retained at
[A25-environment-v2-prospective-admission.md.txt](../development/2026-11-16-console-completion/reports/source-history/A25-environment-v2-prospective-admission.md.txt).
Its v2 protocol subsection remains SHA-256
`8c4b5c5667a159f6d2531b732b40c301ea9e657abf8c79cf92d9157dd21bd679`;
the initial v1 subsection also remains unchanged. The driver pins the retained
v2 snapshot and unchanged native build receipt before launch.

For precision, the native `render_batching` output is the value returned by
`SDL_GetHint`; it is not a readback of SDL's internal `renderer->batching` flag.
Pinned `SDL_CreateSoftwareRenderer`/`SW_CreateRendererForSurface` does not use
the general renderer-creation hint-assignment path. This protocol preserves
that existing method on both sides and requires the same reported hint value;
it makes no additional claim about internal batching behavior. Renderer flags
13 correspond to the pinned software driver's reported capability flags and
are checked in the capture header; they are not a measured display-vsync result.

## Independent same-scene raw witness admission

**ADMIT capture-v2 as the required same-scene raw Flat witness.** The
[retained report](../development/2026-11-16-console-completion/reports/p1-flat-witness-v2/report.json)
has SHA-256
`6aa697bdfbb27220d7515883cfde520def1822d0cb563e04e3b32bce8f073314`.
Exactly before then after ran, each exited 0 with CPU-0 affinity, complete
stdout/stderr EOFs, no truncation and no errors. Their 331 paints supplied
**zero timing samples**. Capture wall durations are transport observations,
not benchmark performance statistics.

A25 independently bounded and decompressed both retained gzip streams,
verified compressed and raw identities against the original scratch streams,
rejected trailing members/data, parsed duplicate-free finite JSON, checked the
complete source-derived header and directly compared all **6,293,408 RGBA
bytes / 1,573,352 pixels**. Headers are identical. Each complete stdout has
6,294,029 bytes: 620 header bytes, one newline and the exact RGBA payload.
Both stderr streams are empty. The independent FNV computation used the
standard offset/multiplier and modulo-2^64 recurrence over every raw byte.

| Identical before/after witness item | Identity |
| --- | --- |
| RGBA SHA-256 | `cedf2297c01d868ec591ca3286033f883a3babef0caff4e64e37aeefd80e0910` |
| Raw whole-stdout SHA-256 | `10c7bce48e9d2c76d7089c02da6122f02e53adfeaf0d6e63595243b2886d622c` |
| Lossless stdout-gzip SHA-256 | `bc24358fdfe0b464b78c860d02250a775ba4c0a49b9049ae897162be5babd62e` |
| Independently recomputed pixel FNV-1a-64 | `aa58ce2e68f71fbe` |
| Layout FNV-1a-64 | `9ac2bac0db68cf6f` |

The unchanged companion build report has SHA-256
`bb35f32a2c39b74a310cdb357333c3f989724b7ced19c7d6502f69dba50b7eba`.
A25 verified its successful compile/two links and all source/object/executable
identities, including the exact 37-entry system/project dependency lists after
the declared companion and painter object substitutions. Before capture binary
SHA-256 is `14ace3dc843d8565e60f998add357475bd9ec8084c06333d59532db24a2a805d`;
after is `e62d0894547a9151ea4ce9840e2372b8e59c0ebffd343407fe2f18d2b334fa0c`.
The newly reproduced before object remains supplemental ancestry, not a
retained historical object.

After the captures, A25 checked all **20 witness input references** and all
**1,507 prospective-v2 timing inputs** with zero drift. No timing claim existed.
A first read-only Python audit snippet contained a missing space in a
conditional expression and stopped with `SyntaxError` before execution; the
corrected read-only audit above passed without any native rerun or file change.

This observation supplies exact bytes for the matching fixed scene and
rendering history. It satisfies the frozen method when combined with the
reviewed source/build linkage and mandatory later timing-fingerprint match.
The unchanged timing executable still exports only a fingerprint; this review
does not relabel it as a raw-byte exporter or claim cryptographic collision
freedom for FNV.

## Remaining gates and next action

The companion build and capture-v2 witness are admitted; capture-v1 remains
failed. Root may execute the single timing batch below before any later model,
comparator, source, object or dependency change. The current pre-helper inputs
alone are qualified. Stop root-controlled builds/captures/native work and fill
the sole statement placeholder with the actual quiet-interval facts. The
command frozen at admission, from the repository root, is:

```sh
python3 -B docs/development/2026-11-16-console-completion/run_p1_timing.py \
  --execute --cpu 0 \
  --output docs/development/2026-11-16-console-completion/reports/p1-timing-v1 \
  --protocol docs/development/2026-11-16-console-completion/reports/p1-timing-prospective-v2/protocol.json \
  --protocol-sha256 9b9cef5f2c1ea0d6900c90ef6df63da5c5f7f9aaca9a91505f5b94192e2aa8f6 \
  --runner-sha256 0a5b7a42a17a93bc44f0abab0d26ce0d05c955c511d0bb34fbf399fd611ffedb \
  --admission docs/development/2026-11-16-console-completion/reports/A25-timing-protocol-admission.json \
  --admission-sha256 2fe218b5f53ef21a7249a5a3459ff01179c05065c9b8b19ebdff21ebc4c42d59 \
  --quiet-interval-note '<ACTUAL_ROOT_WORKLOAD_AND_RESERVATION_STATEMENT>'
```

The compact [admission JSON](../development/2026-11-16-console-completion/reports/A25-timing-protocol-admission.json)
binds the same-scene witness source, build/process receipts and raw/compressed
identities before any timing launch. Root and the final independent reviewer
must compare **both** Flat timing pixel fingerprints with `aa58ce2e68f71fbe`
and both layout fingerprints with `9ac2bac0db68cf6f`, matching the remaining
captured scene/renderer metadata too. Retain that separate post-batch result.
The runner's pairwise-FNV check does not implement this cross-witness gate.

Corrected paired-v2 execution, actual full-frame visual acceptance and affected
native/platform suites retain their separate owners and outcomes. The original
62 numerical thresholds, failed v1 focus-oracle report, genuine before binary
and every original receipt remain intact. A visible regression rejects P1
regardless of a timing or patch screen.

This batch can provide descriptive comparisons for four fixed scenes only.
It establishes no confidence interval, equivalence, display smoothness,
audio deadline, full-domain speed, hardware-device or host behavior. Whole
interface 1:1, native accessibility, physical fidelity, signed release and all
M0–M9 exits remain open where previously open. Preserve 47 parameter identities,
state 4/readers 1–3, 91 shared free-running sources, plugin UUIDs, the nominal
dry Engine, four banks, 147 playing keys, 24 presets and 68 controls.
