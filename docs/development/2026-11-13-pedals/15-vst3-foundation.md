# Assignment 15 — pinned VST3 foundation

Owner: /root/w03_a15_vst3_foundation

Date: 2026-11-13. Wave 3, assignment 15 of the current 60-assignment session.
Scope: exact SDK acquisition evidence, rights inventory, headless validator
feasibility and concrete contract for later minimal native integration. No
plugin, project CMake, core code, commit or push is owned by this assignment.

## Source and work performed

Read the standing agent instructions, current entry/handoff/status/plan context,
the atlas product and closure notes covering pp. 379–402 and 450, existing host
integration/parameter/state contracts, and pinned SDK declarations for component
state, parameter curves, processor lifecycle and target construction. The root
integrator acquired SDK 3.8.1 at tag `v3.8.1_build_84`; this assignment verified
the root commit, four required submodule identities and their primary licenses.

Owned deliverables:

- `docs/VST3_SPIKE_CONTRACT.md`: dependency/build policy, frozen FUIDs, three
  native event buses, explicit software pedal mapping, 45-control compatibility,
  transactional one-clock processing, previous/boundary automation anchors,
  active-state transfer and the later native acceptance matrix.
- `data/dependencies/vst3-sdk-lock.json`: exact source/module commits, license
  hashes, embedded `json.h` identity, exclusions, SDK options and class UUIDs.
- `docs/DEPENDENCIES_AND_RIGHTS.md` and `THIRD_PARTY_NOTICES.md`: selected-path
  scope, complete primary MIT text and embedded Unlicense notice. The project's
  own license, research rights and eventual package inventory remain separate.
- This evidence note. No optional acquisition helper was added; exact explicit
  clone/submodule commands are retained in the contract.

## Actual build and validation

SDK source: `/workspace/scratch/f364bc93d920/vst3sdk`.
Build: `/workspace/scratch/f364bc93d920/vst3-foundation-build`.
CMake executable:
`/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/cmake` (3.31.6).
Compiler: GCC 14.2.0, Linux. The isolated build did not use a live Hammond core
library or concurrently changing project headers.

```sh
cmake -S /workspace/scratch/f364bc93d920/vst3sdk \
  -B /workspace/scratch/f364bc93d920/vst3-foundation-build \
  -DCMAKE_BUILD_TYPE=Release \
  -DSMTG_ENABLE_VSTGUI_SUPPORT=OFF \
  -DSMTG_ENABLE_VST3_PLUGIN_EXAMPLES=OFF \
  -DSMTG_ENABLE_VST3_HOSTING_EXAMPLES=OFF \
  -DSMTG_CREATE_PLUGIN_LINK=OFF \
  -DSMTG_RUN_VST_VALIDATOR=ON
cmake --build /workspace/scratch/f364bc93d920/vst3-foundation-build \
  --target validator -j 4
/workspace/scratch/f364bc93d920/vst3-foundation-build/bin/Release/validator -selftest
```

Configure and build succeeded. Missing JACK was informational for this selected
target. The SDK's atomic-header feature probe selected its fallback. The build's
post-build selftest and a separately executed selftest each reported **51 tests,
0 failures**. The executable's help/version identified VST 3.8.1.

| Local evidence | Bytes | SHA-256 |
| --- | ---: | --- |
| `vst3-foundation-configure.log` | 814 | `38d5fa48b8c25ca625cf7bd7d112a7107a24028a1f7dfe66f9a066112c559f6b` |
| `vst3-foundation-build.log` | 13,780 | `3fd881c9805e5a5b542653348c051730ffff3f013e8063501a66132ad51693d0` |
| `vst3-foundation-selftest.log` | 2,741 | `9e4217fe7b85ab1569c5cf9666729555b0ad0bf4936b2f7818366db87cfe6987` |
| `bin/Release/validator` | 935,200 | `b788cbfa15ed4805ff05663391a45571bf8971745a1811c27dbb311f44631290` |

These machine-local logs and executable are outside the repository; their
identities and results are retained here, not represented as shipped binaries.
The lock was parsed and independently compared against actual root/module HEADs,
root gitlinks, primary-license bytes and embedded parser hash. Both complete
license notices were checked against the selected source files. Whitespace
validation covered only this assignment's files, preserving concurrent work.

## Findings that later implementation must preserve

The SDK explicitly allows UI-thread `IComponent::getState` and `setState` during
Processing. A safe bounded handoff and coherent copied publication are required;
reading mutable Engine state from UI or rejecting every active save/load is not
the advertised native behavior. The contract specifies pending/acknowledged
sequence handling, a four-record queue and an atomic-payload publication option.

Native parameter queues are linear curves with the previous value at sample
`-1`. Expression must interpolate between points, not jump only at endpoints.
An admitted offset-`N` point also serves as the current ramp's right endpoint,
then executes as retained next-block offset zero before fresh same-time input.
Rejection preserves its carry, all anchors, owners, queue cursors and output.
Candidate Engine/owner values and private output allow full transactional
rendering without advancing the source field twice.

The processor UUID is `19f9adc0-533f-42b4-b96b-d51d6547e838`; controller UUID is
`0dee76ab-26bc-475a-bf64-f138c89fb0e0`. They are freshly generated project IDs
and are now frozen in the lock/contract. The software pedal policy is
`vst3-pedal-midi36-v1` (native bus 2, MIDI 36–60 to PedalId 1–25); it makes no
physical octave claim. The later adapter preserves existing 43 parameters and
adds only the two planned pedal IDs, while accepting controls-state 1/2/3.

## Outcome and exact next step

**Feasible:** the selected minimal SDK dependency builds with GUI/examples off,
no JACK requirement and no custom UI. Integrate the contract after a coherent
45-parameter/pedal-ownership/state-v3 core checkpoint: optional build/factory,
processor/controller, bounded automation/input, concurrent state handoff and an
independent native ABI harness. Preserve CMake 3.21 for ordinary builds and
require 3.25+ only for the optional SDK; default plugin option is OFF with no
implicit network acquisition.

Run the SDK validator on the actual resulting Hammond bundle and qualify that
same artifact with the independent harness. The SDK's own selftest here does
not establish a Hammond native ABI pass, real DAW save/reopen, device deadlines,
Windows/macOS support, native UI, package/signature readiness or physical
fidelity. Those gates remain pending until individually observed and retained.
