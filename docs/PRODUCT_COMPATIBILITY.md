# Product continuation compatibility

## Result and source boundary

Independent A29 review found **no incompatible change to the retained musical
parameter, control-file, dry Engine, generic host-timeline or VST3 contracts**
between baseline `af006b0ae293c7c9a5f44b5dfe1dc9942fe9e12d` and published
`ff41d412d03f2c5767aa4057b29fa8ec1627449b`, tree
`6462343bb34a7d70d59de75ab349f8530196988c`. This is a source and retained-evidence
review of those revisions, not a new hardware, host or acoustic qualification.

The published change introduces native standalone MIDI policies and an
independent electrical crossover API. It also changes native paint and expands
the MIDI settings dialog. Those intentional additions do not migrate musical
saved state. The [channel-mode contract](MIDI_CHANNEL_MODE_CONTRACT.md),
[expression contract](MIDI_EXPRESSION_CALIBRATION.md) and
[crossover contract](LESLIE_CROSSOVER_CONTRACT.md) define their separate scopes.

Exact Git-blob comparison established:

| Protected input set | Existing files compared | Result |
| --- | ---: | --- |
| `include/hammond/` and `src/` | 52 | All unchanged; only `LeslieCrossover.h/.cpp` are added. |
| `plugins/vst3/` | 20 | All unchanged, including build, identities, state wrapper and native tests. |
| `data/` and `cmake/` | 39 | All unchanged, including the parameter registry, nominal profile, registration catalog and dependency locks. |
| Standalone `UiModel.h/.cpp` and `StateFiles.h/.cpp` | 4 | All unchanged. |

All **28** changed-source SHA-256 entries in the integrator's
[coherent-build receipt](development/2026-11-15-product-continuation/reports/wave4-coherent-build.json)
match their published Git blobs. The receipt records a GCC 14.2 Release all-target
build and **176/176 CTest passes in 177.92 seconds**, with standalone enabled,
physical MIDI backend disabled and VST3 disabled. The retained
[full log](development/2026-11-15-product-continuation/reports/wave4-full-ctest.txt)
contains the individual results. A29 inspected those results and their relevant
test oracles; A29 did not repeat the broad suite.

## Musical parameter and saved-control compatibility

The registry still contains exactly **47** records, schema 4, model
`exclusive-fixed-percussion-pedal-console-v4`. Both the authoring registry and
compiled descriptor table are byte-identical to the baseline. Numeric IDs,
paths, units, defaults, bounds, discrete thresholds, normalized conversion and
event identities therefore retain their previous definitions.

| Existing numeric IDs | Musical meaning | Count |
| --- | --- | ---: |
| 4096–4104 | Upper A drawbars | 9 |
| 4112–4120 | Upper B drawbars | 9 |
| 4128–4136 | Lower A drawbars | 9 |
| 4144–4152 | Lower B drawbars | 9 |
| 8192 | Global expression | 1 |
| 8208–8209 | Remembered Upper/Lower A/B bank selectors | 2 |
| 12288–12291 | Percussion enabled, harmonic, volume and decay | 4 |
| 16384–16385 | Pedal mixtures | 2 |
| 20480–20481 | Effective Upper/Lower preset selectors | 2 |

The [control-state implementation](../src/ControlStateIO.cpp) still writes
**`B3CONTROLS4`** and reads versions **1, 2, 3 and 4** under the unchanged
[format](CONTROL_STATE_FORMAT.md). It retains all four drawbar banks, remembered
bank values, raw fixed-registration memory, both route-enable bits, expression,
percussion and pedals. The fixed catalog identity remains mandatory in version 4.
Old-state defaults remain explicit: version 1 receives the established percussion
defaults; versions 1–2 receive muted pedals; versions 1–3 receive no fixed modes.
Effective preset selectors do not replace the underlying saved memory.

The unchanged [control I/O test](../tests/test_control_io.cpp) checks a separate
literal version-4 output oracle, all three historical fixtures, 1,600 retained
fixed-mode/bank/route combinations and 4,800 legacy migrations. Its registered
`test_control_io` passed in the coherent run. `test_parameter_bridge`,
`python_test_parameters`, `python_test_parameter_bridge`,
`python_test_preset_parameter_oracle` and `test_preset_parameter_boundaries`
also passed there.

Expression endpoint/inversion configuration is **not another sound parameter**.
It is retained in process-local MIDI configuration, copied into a new input
epoch and excluded from musical Save/Load. Selecting or applying it sends no
expression change; a later admitted CC11 or CC121 can change the existing ID 8192.
The new [native diagnostics test](../apps/standalone/native_tests/test_standalone_expression_diagnostics.py)
checks varied musical controls and exact original control-file bytes while
configuration, modal selections and decoder lifecycle change. It passed in the
same coherent run. Note owners, oscillator phases, contact/percussion histories
and numerical crossover checkpoints remain outside musical control files.

## Native MIDI additions and preserved behavior

| Native input | New or retained behavior | Compatibility boundary |
| --- | --- | --- |
| CC11 | Endpoint saturation and optional inversion feed existing global expression. | Defaults are bit-exact `double(raw)/127.0` for all 128 admitted values. Other controller mappings do not use calibration. |
| CC120 value 0 | A distinct `ScopedSoundOff` retires the mapped division's MIDI owners. | Same-key UI owners and other divisions survive; no persistent mute or phase/percussion reset is introduced. Nonzero values reject. |
| CC121 value 0 | Requests normalized expression 1.0 through the existing shared UI submission/acknowledgment path. | Bypasses calibration, preserves held notes and pending unrelated edits; calibration and other controls remain. Expression is global across mapped divisions. Nonzero values reject. |
| CC123 values 0–127 | Existing scoped All Notes Off behavior. | The historical lenient nonzero-value acceptance remains; this does not claim complete MIDI conformance. |

`SessionCommand` appends `ScopedSoundOff` at index 4. The preceding four
alternatives retain their indices; compile-time assertions in
[channel-mode tests](../apps/standalone/tests/test_standalone_channel_modes.cpp)
check them. The new scope validates before queue or sequence reservation.
Existing queue-overflow recovery remains global and must not be described as a
scoped guarantee after a transport failure.

Immediate silence is restricted to the native Session's existing **ideal contact
mode**. Its preparation still invokes the two-argument Engine preparation;
application explicitly checks `ContactMode::Ideal` before reducing sound-off to
ordinary scoped ownership release. Generic finite-travel Engine behavior has not
gained All Sound Off support. A future non-ideal Session would fail the guard and
follow existing command-failure recovery; its public preparation API does not
currently provide an executed non-ideal Session case.

The author channel-mode trace compares every rendered sample with an independent
sequence of physical Engine transitions, including shared owners, fresh presses,
percussion-only silence and continuation. The independent
[A21 test](../apps/standalone/tests/test_standalone_channel_acceptance.cpp) adds
saturated queues, 3,444 invalid scopes, partial/stale acknowledgments and 812 exact
stereo comparisons. Both tests passed in the coherent run. These oracles support
unchanged dry rendering and continuous clock/phase for their tested sequences;
they do not measure an external controller's timing.

Calibration is immutable during an active epoch. Changed port, routing or
calibration retires the old inbox and MIDI owners, waits for the existing release
acknowledgment/recovery barrier, then opens a fresh epoch. An identical healthy
request is a no-op. Failed opening remains inactive until an explicit request.
The new `begin_epoch` defaulted second argument preserves old source call sites.
Its C++ signature and the internal command variant have changed, so adapter
consumers must be rebuilt coherently; no cross-version adapter binary-ABI
guarantee is made.

## Core, VST3 and crossover boundaries

All existing core headers and implementations, including Engine, HostTimeline,
both ownership translators, PerformanceInput, InputProcessor and ControlState,
are unchanged. The shared 91-source generator and nominal expression arithmetic
therefore retain their previous implementations. The crossover is compiled into
the static core library through the existing source discovery, but neither
Engine nor the standalone or VST3 audio path creates or calls it.

The independent `LeslieCrossover` owns four physical capacitor/inductor states,
previous input and its completed-frame counter. Its `restore_state` restores a
numerical experiment; it is unrelated to `restore_controls` or preset selection.
It has no parameter registry entries, live JSON loading, host automation or
acoustic routing. Its admitted 192 kHz research rate does **not** extend Engine,
HostTimeline or VST3, whose unchanged supported-rate predicate admits 44.1, 48
and 96 kHz. Its warped-response pass and separately retained same-Hz differences
do not authorize an audible cabinet path.

VST3 processor UUID `19f9adc0-533f-42b4-b96b-d51d6547e838` and controller UUID
`0dee76ab-26bc-475a-bf64-f138c89fb0e0` remain unchanged. Controller descriptors
still come from the existing 47-record table; plugin state still uses the common
control serializer. Native Note On/Off and parameter queues still enter the
unchanged HostTimeline. The processor still rejects output-only
`kLegacyMIDICCOutEvent` as input. Native standalone CC120/121 handling and endpoint
calibration are not newly advertised VST3 features.

The retained `test_host_timeline`, control, ownership and realtime checks passed
in the coherent native build. **VST3 was disabled in that build.** Source identity
supports preservation of its contract, but current-revision plugin build,
validator and native-test results require their own published-source evidence.
Historical plugin qualification is not silently promoted to this revision.

## UI and diagnostic consumers

The unchanged UiModel retains **68 Play controls, including 24 reversed preset
keys**, and separately **147 playing keys**: 61 Upper, 61 Lower and 25 pedals.
There are 71 cyclic Play focus stops and ten common stops in Rotary/Service.
These counts differ from the 47 musical parameters because presentation actions,
roving key focus and retained-bank selection have distinct roles.

The [independent visual fixture](../apps/standalone/native_tests/test_standalone_product_visual.cpp)
explicitly checks that inventory and focus cycle. Its source-identified
[A23 result](development/2026-11-15-product-continuation/reports/A23-visual-acceptance.json)
also limits wide-painter deltas and retains compact/Flat/hidden equivalence; the
registered fixture passed in the coherent run. MIDI calibration adds a separate
eleven-stop modal, not extra musical controls.

Native diagnostic schema version 3 gains calibration observations, with selected,
configured, active, pending and pre-shutdown values distinguished. Consumers that
require exact JSON member sets must adopt the expanded schema, as the native test
helpers did. This is an intentional diagnostic-surface change; it is not
byte-for-byte diagnostic-output compatibility or a `B3CONTROLS` migration.
Native CLI/dialog and replay tests passed with their updated exact oracles.

## Reproduction, identities and next gate

A29 ran read-only Git comparison, SHA-256 verification and source/log inspection
from `/workspace/scratch/5b7d983ac078/Hammond-B3-Organ`. No shared build was
modified and no runtime suite was repeated. Representative exact identities are:

| Input | SHA-256 |
| --- | --- |
| `data/parameter-registry.json` | `aedaa09e47fc2baba4a08484cce84916f2a27edac55d45f03f167f41c84bd6e2` |
| `src/ParameterBridge.cpp` | `296c674ef39d54751f662293b4ce4b07f602bb407349981f8b03e1b5a4757220` |
| `src/ControlStateIO.cpp` | `3a95b6750fc615b7218da5dd9cb540b30d8a83984374d441f2754c7e66de34fb` |
| `src/Engine.cpp` | `ea94f27be2ce6e374537c616bdde34c32c3276df6f7f24e112f52a35d1a4bd3a` |
| `src/HostTimeline.cpp` | `f0a3f88396f0f9b743f91277ca31b85a32deda98abae53d022dbf601d2226149` |
| Native executable | `7ded143b676e9d51a29549dae12184763042a1f12192f72802db7927fa707852` |
| Compiled nominal profile | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

The published-file comparison and receipt check can be repeated without a build:

```sh
git diff --name-status af006b0ae293c7c9a5f44b5dfe1dc9942fe9e12d \
  ff41d412d03f2c5767aa4057b29fa8ec1627449b
python3 - <<'PY'
import hashlib, json, subprocess
base = 'af006b0ae293c7c9a5f44b5dfe1dc9942fe9e12d'
head = 'ff41d412d03f2c5767aa4057b29fa8ec1627449b'
def git(*args):
    return subprocess.check_output(['git', *args])
groups = [('include/hammond', 'src'), ('plugins/vst3',), ('data', 'cmake'),
          ('apps/standalone/UiModel.h', 'apps/standalone/UiModel.cpp',
           'apps/standalone/StateFiles.h', 'apps/standalone/StateFiles.cpp')]
for group in groups:
    paths = git('ls-tree', '-r', '--name-only', base, '--', *group).decode().splitlines()
    assert all(git('show', f'{base}:{p}') == git('show', f'{head}:{p}') for p in paths)
    print(group, len(paths), 'existing files unchanged')
report_path = 'docs/development/2026-11-15-product-continuation/reports/wave4-coherent-build.json'
report = json.loads(git('show', f'{head}:{report_path}'))
for path, expected in report['changed_source_sha256'].items():
    assert hashlib.sha256(git('show', f'{head}:{path}')).hexdigest() == expected, path
print(len(report['changed_source_sha256']), 'published source hashes match')
PY
sha256sum /workspace/scratch/5b7d983ac078/build-native/apps/standalone/hammond_standalone \
  /workspace/scratch/5b7d983ac078/build-native/nominal.b3p
```

The next compatibility gate is to integrate and register A26's real-main,
test-dependency calibration lifecycle fixture, then retain its exact-source
CTest result for identical Apply, changed Apply/release acknowledgment, failed
reopen, explicit recovery and subsequent CC11. Root must separately qualify
the current published VST3 build/validator/native matrix and update operator
guides to describe native-only behavior. The independent crossover needs its
own installation/portability acceptance before any future integration proposal.

Physical MIDI and audio devices, screen-reader semantics, real display/DPI,
DAW journeys, callback deadlines and acoustic fidelity remain separate gates.
Local leak-enabled sanitizer execution was blocked by the environment's ptrace
restriction, including an empty-main control; this review supplies no sanitizer
pass. No production compatibility defect was found that requires changing the
protected contracts.
