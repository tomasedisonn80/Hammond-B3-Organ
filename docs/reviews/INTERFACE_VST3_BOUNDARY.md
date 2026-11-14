# Independent native VST3 boundary review

**A47/60, wave 8 — 14 November 2026. Accepted for preservation of the existing
native engineering contract.** The standalone interface slice leaves every
protected VST3, core, parameter and state byte unchanged. This review combines
source inspection with exact hosted results; it introduces no product changes
and reruns no native suite.

## Source and contract

The [reproducible audit](../development/2026-11-14-interface-continuation/reports/a47-audit.py)
compares A12's baseline `d493e998e5dd7cf44db46854e87309745063ac54`, hosted
revision `8673713a484c40e26ac7810c7c4cbc22fa874426`, current HEAD
`cdbb2beaa28bf136f9a8db6213819129514e2ae9` and working bytes. **All 114
protected paths match:** 20 VST3, 44 core and 50 other protected inputs. There
are no added/removed native or core files. The
[source report](../development/2026-11-14-interface-continuation/reports/a47-source-boundary.json)
retains per-file SHA-256/blob identities, group digests and all 47 parameter
records. GitHub's commit response independently confirms the hosted tree
`e11bd68d6051f663631579ef235325a8775f8133`.

Inspection traces `ParameterBridge` through `Controller`, `Processor`,
`StateStream`, `ControlStateIO` and the native ABI/controller tests. All 47
registry records match both compiled descriptors and the independent controller
oracle. Preserved IDs cover four nine-drawbar banks, expression, two bank
selectors, four percussion switches, two pedal mixtures and selectors
20480/20481. Defaults, ranges, discrete thresholds and normalized conversion
laws are unchanged. `B3CONTROLS4` remains the sole writer; readers 1–4 retain
their explicit percussion/pedal/fixed-registration migration defaults. Workspace
and Flat presentation add no sound-state fields.

The factory still exports exactly processor
`19F9ADC0-533F-42B4-B96B-D51D6547E838` and controller
`0DEE76AB-26BC-475A-BF64-F138C89FB0E0`. Three 16-channel event inputs—Upper
main, Lower auxiliary and Pedals auxiliary—feed one dry stereo output; there
are no audio inputs. Processing remains float32 at 44.1/48/96 kHz. All controls
remain automatable generic host controls; native tests explicitly require
`createView(kEditor) == nullptr` and no component-state automation echo.

`HammondB3` still lists only processor/controller/factory/state-stream sources
and the embedded profile, linking `hammond_core` and `sdk`. Core sources remain
SDK/UI independent. VSTGUI is disabled. The root/native CMake, native workflow,
SDK verifier/acquirer and three data-generation tools match baseline and hosted
bytes. Neither the 20 native files nor any of the three complete native build
logs contains an SDL or standalone-source dependency.

## Exact hosted evidence

Primary GitHub job metadata and complete decoded logs were fetched independently
for Native VST3 run **43596362881**, attempt 1. Every row below has head
`8673713…`, conclusion **success**, and no CTest-level skip. The
[compact record](../development/2026-11-14-interface-continuation/reports/a47-hosted-vst3.json)
and [excerpts](../development/2026-11-14-interface-continuation/reports/a47-hosted-excerpts.txt)
retain log hashes, test names, counts, capabilities and installed-bundle hashes.

| Exact job | Compiler | Native CTest | Duration |
|---|---|---:|---:|
| [Linux 132451604200](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43596362881/job/132451604200) | GCC 13.3.0 | 8/8 | 6.05 s |
| [Windows 132451604376](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43596362881/job/132451604376) | MSVC 19.44.35230.0 | 7/7 | 6.25 s |
| [macOS 132451604377](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43596362881/job/132451604377) | AppleClang 17.0.0.17000013 | 7/7 | 4.19 s |

Each locked SDK 3.8.1 module validator reports **47 passed/0 failed**. Each ABI
run and installed relocation reports 47 descriptors, 3,207 state round trips,
2,140 conversions and zero maximum reference-audio error. Controller, behavior,
automation and concurrency suites also pass. Linux alone registers the native
allocation-interposition suite; its result establishes no other-platform
allocation or device-deadline claim.

## Limits and next action

Each validator log retains **16 teardown messages, nine unsupported-rate ERROR
messages and 15 unsupported-float64 notices**. The inspected pinned SDK counts
test-body success separately from teardown; its format test logs rejected
unsupported rates without failing the body. These are explicit qualification
limits, not clean-log claims. Mono, float64, units/programs, MIDI mapping/learn,
note-expression and keyswitch interfaces, bypass and a custom editor remain
unadvertised. Alternate-platform configure steps are conditional workflow skips.

No DAW project/reopen session, physical audio/device acceptance, accessibility,
clean-machine installation, signing or hardware fidelity was established.
Current `cdbb2be` adds standalone sanitizer/timeout/documentation metadata; these
three hosted jobs still qualify `8673713` only. **Next:** integrate this review,
carry the zero-mismatch boundary check into A49's final frozen-source gate and
observe the new standalone sanitizer job separately. The next VST3 product gate
is a retained DAW save/reopen/automation session using an identified native
bundle, host and physical device.
