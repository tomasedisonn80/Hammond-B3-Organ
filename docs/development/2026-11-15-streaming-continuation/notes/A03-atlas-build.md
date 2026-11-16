# A03 - complete atlas range and build audit

Worker: `/root/w01_a03`. Wave 1, assignment 3. Scope: read-only build/runtime
audit and complete textual reading of atlas pages 169-252; this note is the only
owned write. No build, CTest, dependency acquisition or production edit ran.

## Source and complete reading coverage

Repository: `/workspace/scratch/177e78b1ac09/Hammond-B3-Organ`.
Observed HEAD: `4aac394cde4da40906b615573a8779aee2d9a37a`.
Observed HEAD tree: `3605c9ce098a052afc10b2969fefe31e15644fe9`.

The unchanged PDF SHA-256 is
`4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769`.
The assigned extract `/workspace/scratch/177e78b1ac09/atlas-169-252.txt` has
223,389 bytes, 5,041 lines and SHA-256
`0370f39395d7666ab764075f63745a2efef654edc00c5c7c85a3954fb8c8c704`.
All 84 pages were read completely, in contiguous batches 169-180, 181-192,
193-204, 205-216, 217-228, 229-240 and 241-252. For bounded tool output only
whitespace was collapsed; no text lines or pages were omitted. This is textual
coverage, not an independent verification of the cited source drawings or a
visual review of every page image.

| Pages / chapter | Complete-range findings relevant to the implementation |
| --- | --- |
| 169-174 / 027 | Scanner selection comprises two routing tablets and six modes, with no seventh selector OFF state. Great includes pedals; percussion joins after scanner. One scanner phase/history persists. Chorus return is included exactly once. Exact mode tap maps, routing/state fixtures and separate physical captures are required. |
| 175-180 / 028 | The documentary ladder has 18 LC sections and 19 voltages, not 19 stages. WDF wave directions, source/switch root elimination and physical state must be explicit. Printed root, sign and Hz/radian errors require independent derivation. Warped-grid agreement and same-Hz agreement are separate gates. Toy algebra results do not qualify a full circuit. |
| 181-186 / 029 | Preserve one auditable connectivity graph and independent reference/runtime realizations. Descriptor constraints and stored-energy state are distinct; do not invert singular E or retain alternating constraint-error modes. Prepare/factor outside callbacks and preserve physical energy through supported transitions. All 19 outputs, conditioning, energy, timing and hardware evidence require separate acceptance. |
| 187-192 / 030 | Module-level and organ-output captures need distinct boundaries. Fit stationary complex tap responses before shared rotor-phase/sideband behavior, preserving calibrated scale, uncertainty and held-out takes. None of the described physical scanner captures exists in this chapter. |
| 193-198 / 031 | AO-28 V1-V8 roster and V3A/V3B roles are explicit; no extra output socket may be invented from contradictory prose. Functional stage inventory is not connectivity-complete. Preserve A/B/H branches, scanner load and downstream percussion, then establish linear reference before nonlinear/aging controls. |
| 199-204 / 032 | Connected small-signal response depends on operating point, source, load and controls. T3 ratio, losses and winding properties cannot be inferred from a symbol. Preserve differential/common-mode ports, phase and loading. An independent circuit pass and a hardware pass are distinct. |
| 205-210 / 033 | Valve laws need family-specific provenance, units, fitted domains, terminal conservation and verified derivatives. Stable softplus and explicit out-of-domain policy prevent invalid arithmetic. Coupled nonlinear solve must bound iterations and stage reactive-state updates transactionally; fallback is a degraded result, not a fidelity pass. |
| 211-216 / 034 | Headroom belongs to calibrated routed electrical networks. Shared nonlinear stages retain cross-products, bias, feedback and capacitor history. Generic per-note saturation or unexplained sag cannot substitute. Small-signal limit, recovery, aliasing, runtime and held-out physical evidence remain separate. |
| 217-222 / 035 | Supply branches and coherent mains-related paths have one physical owner. Rectifier ripple is not a supplied measured output amplitude. Noise needs units, bandwidth, deterministic source identity, persistent state and rate scaling. Recording faults and optional condition profiles stay separate from a nominal instrument. |
| 223-228 / 036 | Factory identity, inspected configuration, dated condition and service events are separate records. Calendar age is not a measured DSP law. Preserve before/after data, uncertainty and correlations; one specimen cannot establish a population distribution. |
| 229-234 / 037 | Contact aliasing must be addressed at the switching boundary; downstream oversampling cannot repair aliases already generated. Connected states use one internal timeline. ADAA has its own low-level response/delay and cannot be inserted blindly into implicit networks. Reference convergence, transport delay, exact event timing, total residual and bounded callback work are required. |
| 235-240 / 038 | 85 stock records and 124 electrical placements are not a complete netlist or installed package count. Keep namespaces, units, unresolved fields and revision alternatives. MF/SPICE-M conversions must be explicit. The factory C59 versus redraw C56 conflict is preserved, and independently traced complete connectivity precedes numerical promotion. |
| 241-246 / 039 | Choose reduced/runtime models at declared physical ports, retaining loading, state and effect ownership. Learned/residual models need actual captures, valid domains and held-out evidence. Compile rates, buffers and latency off-thread; quality changes cannot silently select different specimens or tuning. |
| 247-252 / 040 | Validate the loaded dry organ before Leslie. Source identity collisions reuse continuously running phase while retaining separate contacts and gains. Contact/percussion behavior is history-dependent. Six scanner modes cross four tablet combinations. Absolute event timelines must survive block partitions; documentary, numerical, hardware and musical gates remain distinct. |

The most direct support for the proposed streaming work is pp. 229-234 and
248-252: preserve switching time, shared source phase and separate contact
histories before filtering, then verify partition invariance and explicit
transport latency. These pages do not supply a complete causal implementation,
an admissible arithmetic representation or a measured contact calibration.

## Repository and toolchain inspection

Read `AGENTS.md` in full, `docs/PLAN.md` in full, active next steps/checkpoint,
`docs/CONTACT_STREAMING_NEXT_DESIGN.md`, active UI implementation map, root and
standalone CMake inputs, presets and core/native CI configuration. The existing
execution checkpoint records 45 dispatches and historical 203/203 local CTests;
those facts do not count this session's workers or establish a current-source
run. Preserve the prior ledger and source-specific evidence.

Observed tools: GCC 14.2.0, CMake 3.31.6, Ninja
`1.11.1.git.kitware.jobserver-1`, Python 3.12.14. Required minimums from actual
build inputs: CMake 3.21, C++20, Python 3.10. The default build is SDK-free;
standalone, VST3, MIDI and sanitizers are OFF unless explicitly enabled.

Minimal SDK-free commands from repository root:

```sh
cmake --preset release -G Ninja
cmake --build --preset release --parallel 3
ctest --preset release --parallel 3 --no-tests=error
python3 -B tools/check_repository.py --root . --json
```

For this session's single coordinated native build, root can first acquire or
verify SDL with the repository helper. The lock requires SDL 2.32.10 at commit
`5d249570393f7a37e037abf22cd6012a4cc56a71`, including the recorded Zlib license.
Do not reuse another session's writable build tree.

```sh
python3 tools/acquire_sdl2.py --destination ../SDL2
python3 tools/acquire_sdl2.py --verify-existing ../SDL2
cmake -S . -B ../build-native -G Ninja -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_TESTING=ON -DHAMMOND_BUILD_STANDALONE=ON \
  -DHAMMOND_BUILD_VST3=OFF -DHAMMOND_ENABLE_MIDI=OFF \
  -DHAMMOND_ENABLE_SANITIZERS=OFF -DHAMMOND_SDL2_ROOT="$PWD/../SDL2" \
  -DSDL_X11=OFF -DSDL_WAYLAND=OFF -DSDL_ALSA=OFF \
  -DSDL_PULSEAUDIO=OFF -DSDL_JACK=OFF
cmake --build ../build-native --config Release --parallel 3
ctest --test-dir ../build-native -C Release --output-on-failure --no-tests=error
```

The explicit backend-OFF options support dummy SDL/software capture only; they
do not qualify a desktop, real audio device or real MIDI endpoint. Normal Linux
native CI instead installs pkg-config, libasound2-dev, libpulse-dev, libx11-dev,
libxext-dev, libxrandr-dev, libxcursor-dev, libxfixes-dev, libxi-dev and libxss-dev,
then requires compiled X11/ALSA/PulseAudio plus dummy backends. Physical MIDI
needs the separately pinned RtMidi source; VST3 needs its separately pinned SDK.

## Recommended bounded next implementation and gates

1. Admit the new isolated M3 representation/trajectory contract before coding.
   The existing proposal explicitly remains unadmitted. Retain distinct exact
   roots that round to the same display coordinate, command collision history
   across callbacks, subnormal bounds, tie order and no-op behavior. Preserve
   transactional failure and bounded storage/work. The old syntactic maximum
   exceeds its proposed work ceiling; admission must distinguish capacities
   from accepted work. Implement the trajectory spike before the audio filter.
2. Use an independent exact-history oracle and adversarial partitions, ties,
   reversals, endpoint/empty/drain cases and successful continuation after
   rejection. Do not describe offline range concatenation as causal streaming.
3. Keep Engine, the 91 shared sources, all 47 parameter identities,
   B3CONTROLS4/readers 1-3 and default dry sound as preserved baselines. New
   Engine/native/VST3 wiring needs its own acceptance after research admission.
4. The parallel M9 next step is an independently admitted Upper-rack
   inner-metal/material/type candidate, with genuine same-state old/new native
   captures and whole-reference comparison. Preserve controls, ownership,
   inactive paths and historical failures. Scoped containment is not literal
   1:1 equality; physical display and semantic accessibility remain unrun.

Build inputs are broadly discovered with CONFIGURE_DEPENDS. Reconfigure after
adding tests, build all required inputs before CTest, use `--no-tests=error`,
and bind evidence to a coherent frozen tree. Do not broaden tests without an
affected risk. CI's existing strict record checks validate older sessions only;
they cannot count this new session. Observe the exact published commit's core,
standalone and VST3 workflow outcomes before claiming hosted success.

## Verification performed and next action

Executed only source reads, hashes, `git status --short` (clean before this
note), `git rev-parse`, and tool-version queries. No implementation or test pass
is claimed. Root should combine this range with the five other complete atlas
readings, freeze the bounded streaming/material scope and assign independent
contract review before implementation. Root owns the build, shared navigation,
integration, current evidence and nonforced publication.
