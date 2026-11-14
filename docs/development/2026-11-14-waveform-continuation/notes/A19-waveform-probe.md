# A19 — Native waveform qualification probe

Actual worker /root/w04_a19_waveform_probe, wave 4, 14 November 2026.
Owned tests/probes/rotary_waveform_probe.cpp and this note. No nested workers,
product/header changes, CMake/shared-ledger edits, commits or publication.
Read repository instructions, complete project plan, current session
scope/checkpoint/assignments, frozen renderer/numerical contracts, full waveform
acceptance/build plan and independent reference. Observed HEAD:
26ff2fbe66a50260bd7601cbfa54c1f5d35ff3a8, tree
530d5fcf777003f470f64558de9e5631d31a21a4; the renderer and probe are an
uncommitted overlay. The integrator explicitly closed A18's timing window before
this worker compiled or ran code.

## Implemented experiment and protocol

The CLI is **rotary_waveform_probe [--mode smoke|full]**, defaulting to smoke.
It emits exactly one final schema-version-1 JSON object on stdout, progress on
stderr, and exits nonzero on failures or caught exceptions. Exception reports
retain the failed stage, rate/partition/frame where available and partial
counts. There are no output-file arguments or side artifacts; Python owner A21
records stdout, stderr, exact executable identity, complete source/build inputs
and before/after stability.

Full mode uses unchanged A08 full_scene, full_events and full_input for exactly
one ten-second mixed stream per supported rate. Its complete workload is
3,801,000 reference frames, 7,602,000 scalar waveform comparisons, 15,204,000
reference paths, 22,806,000 native frames and 91,224,000 native paths.
The native patterns are fixed 1/7/64/257/4096 plus the exact fourteen recorded
irregular lengths. All 35 ordered events per rate, including both commands at
the final ten-second boundary, are supplied once with inclusive end-boundary
admission and retained input order.

Block 1 is canonical. Its output is the sole full stereo binary64 buffer;
reference samples are generated independently and immediately accumulated.
Five alternate streams compare every binary64 output bit directly, giving
38,010,000 full-mode comparisons. Each alternative compares all 32 physical
state fields and 46 persistent diagnostic fields explicitly, including every
floating bit representation and command. Struct padding and call-local maxima
are not compared. Reference channel-major paths map to native rotor-major
paths with the explicit mapping [0,2,1,3].

The report retains the exact fixture and ordered events, channel normalization,
absolute/normalized maximum and RMS, worst frame/values, native/reference
residual and evaluation maxima, consumed-event counts, final native/reference
motion, final diagnostics, nonzero interval counts and complete frame/path
counts. No gain fitting, alignment, clipping or frequency remapping occurs.
Waveform and partition failures have complete per-channel bitmaps, first/last
indices, counts and SHA-256, rather than a truncated first-N log.

Input, canonical/alternate native output, and separately labeled binary64
casts of reference output receive SHA-256 stream digests. Stream encoding is
frame-interleaved little-endian binary64; reference comparison itself retains
long-double precision. The test-local hash implementation checks empty, abc
and the standard 56-byte known vector.

Full mode retains 176 selected path traces at the frozen eleven sample
positions and 288 independent contractive/pure-bisection pairs. Observations
are exactly sample index minus two. Reference values include split emissions,
unwrapped angle, speed, distance, ratio, delay, residual and evaluation count
at max_digits10, ready for A21's selected Decimal cross-check. Native
diagnostics are copied at the same sample because the canonical block is one.
Auxiliary convergence solves are counted separately from the complete
waveform's exact 15,204,000 paths.

Smoke has its own identity, **rotary-r4-shifted-input-smoke-v1**. It renders
4,097 frames per rate, uses full_input(Fs,rotor,n+2*Fs) only for nonnegative n,
and retains negative-time zero. It filters the full event list inclusively
through 4,097, retaining 15 commands. It covers all six partitions, 64 selected
path traces and 96 convergence pairs. It is never represented as ten-second/full
qualification.

## Actual verification

Working directory: /workspace/scratch/e3cacb90cc81/Hammond-B3-Organ.
Owned temporary evidence: sibling ../a19-waveform-probe/.

~~~sh
c++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion \
  -Wsign-conversion -Wshadow -Werror -ffp-contract=off -Iinclude -Itests \
  tests/probes/rotary_waveform_probe.cpp src/RotaryMotion.cpp \
  src/RotaryPropagation.cpp src/RotaryHistory.cpp src/RotaryStreamingPath.cpp \
  src/RotaryRenderer.cpp -o ../a19-waveform-probe/rotary_waveform_probe
../a19-waveform-probe/rotary_waveform_probe --mode smoke \
  > ../a19-waveform-probe/smoke.json \
  2> ../a19-waveform-probe/smoke.stderr.txt
python3 ../a19-waveform-probe/check_smoke.py
~~~

The strict compile and smoke both exited zero. GCC is Debian 14.2.0-19,
libstdc++ date 20250315, Linux, C++20; floating contraction was explicitly
disabled for both the direct-built production sources and probe. No fast-math,
round-to-nearest, binary64 double (53 significand bits, 8 bytes) and extended
long double (64 significand bits, 18 decimal digits, 16 bytes) were observed.
This is not an 80-digit waveform oracle.

Smoke passed in **2.630104835 seconds**: 16,388 reference frames/65,552 paths,
98,328 native frames/393,312 paths, 32,776 scalar comparisons, 163,880 equal
direct bit comparisons, 360 commands, all 24 completed partitions, all 20
alternate final states/diagnostics, all 96 convergence pairs. JSON is 224,719
bytes. Maximum canonical audio storage was 65,552 bytes; the complete full
fixture's declared maximum is 30,720,000 bytes. The current block is a separate
131,072-byte heap allocation; history objects are never placed on the stack.

| Rate | Left max normalized error | Right max normalized error |
| --- | ---: | ---: |
| 44,100 | 2.584395496228794e-10 | 2.628777556581607e-10 |
| 48,000 | 2.8159813355048556e-10 | 2.557566857614367e-10 |
| 96,000 | 5.387024697993454e-10 | 5.910412173077149e-10 |
| 192,000 | 1.2065936807470127e-9 | 1.0337977339308019e-9 |

The frozen limit remains 2e-5. Maximum native residual was
9.999813477268304e-15 s with at most 38 evaluations; maximum reference
residual was 4.999933420171991e-15 s with at most 8 evaluations.
Maximum fast/pure-bisection difference was 4.029010469436961e-15 s.
The independent Python smoke check regenerated every shifted input scalar,
packed little-endian pairs and confirmed all 24 input SHA-256 records using
hashlib. It additionally confirmed reported final state/diagnostic values,
audio digest agreement, complete counts, and an actual invalid-mode invocation:
exit 1, valid failure JSON, failed_stage="arguments", zero native frames.

## Exact identities and remaining work

| Input/artifact | SHA-256 |
| --- | --- |
| Native probe source | 922c92ab81d2fcc8a5a0948c7c85ee496cf6816bdc57b20dddba7474899ef577 |
| Unchanged independent header | 3c24792f80f86f903926622f4bf016984caf44d727ad3913e4570738ac9c8f21 |
| Waveform acceptance | fa4288d586a2a40d803740408177f9c0a085bd4deb9ae0bdfc832e6d58b0c1aa |
| Renderer contract | 52eaaeda293376abd47af3f788e3bd5967452b176cba021f23ab7bc3b1e141a9 |
| Numerical contract | 4c060088f0718586a7c6810e5c055c652d8924db4474db770237193ab459bd63 |
| Direct-built executable | 2b1c002e8777478026103d795fe64890146371b604f8ec6b65a4597afcbad724 |
| Smoke stdout | 0aed61e1c0044529a914d9abd61d89c04f0c6d649b2c37ec2db55be177dcdcf7 |
| Independent smoke checker | 39a10388093f7bd8294112fb2809d0c5b8629532fb600bd04bc0ea71a0081e4b |
| Checker result | 2f28eecb57f3b0102395cf4d482434420bfd8324c89d79827bfe18a5e2c9a9f0 |

Root owns coherent CMake integration; A21 owns strict JSON validation, selected
Decimal reference checks, compiler/command recording and stable source/executable
provenance. A28 owns the later complete run. **This worker did not run full
mode**, change thresholds or claim that smoke closes R4. The probe explicitly
leaves independent static-grid/history, transactional/lifecycle behavior,
selected Decimal verification, R5 audible policy, R6 deadlines and physical
fidelity as separate groups. Existing A14/A16/A17 evidence is not relabeled as
this worker's execution. The next action is to run A21's wrapper against the
coherently built probe, then execute the full four-rate/six-partition workload
once under A28 with exact source/build/output retention.
