# Starter files: native generic Load admission

16 November 2026; A36 (`/root/w06_a36`), wave 6. **Admitted for the recorded
Linux dummy-SDL inputs:** the real standalone's existing startup and generic
Ctrl+O Load paths restore complete starter/materialized controls, including
expression. This adds acceptance evidence, not native library/browser integration.

## Executed boundary

The [new native test](../../apps/standalone/native_tests/test_standalone_starter_load.py)
uses the public `B3UIREPLAY1` transport and schema-3 diagnostics. It imports only
existing test-side replay builders, JSON checks and diagnostic helpers; it does
not import production parsing, serialization, layout, UiModel or Engine code.
The complete expected snapshot is an independent literal transcription of
recipe 12 in the [reviewed pack contract](../STARTER_REGISTRATION_PACK_CONTRACT.md).
The [operator guide](../REGISTRATION_GUIDE.md) specifies the suffix/expression
boundary being exercised.

Every application process receives an explicit private copy through `--state`.
At 1280×900, keyboard replay reconnects Upper B, clears its remembered fixed
mode, edits its first drawbar to zero, sets expression to one, turns percussion
off and changes the first pedal drawbar to eight. The test requires that full
altered snapshot to be acknowledged **before** Ctrl+O. Startup-only restoration
therefore cannot pass. A subsequent applied observation, the running endpoint,
the final control snapshot and desired controls must all equal the original
expected snapshot, with resolved/applied/submitted sequences equal and no pending
controls or save.

| Input presented to generic Load | Required and observed final expression |
| --- | --- |
| Copied `12 Manual Return.b3registration` | `0.5` from its complete payload |
| Copied `12 Manual Return.b3performance` | `0.5` from its identical complete payload |
| CLI-materialized Registration, supplied current Warm Comp snapshot | `0.625` from supplied current expression |
| CLI-materialized Performance, without `--current` | `0.5` from the entry |

The materialization runs use a private two-entry library and a private copy of
`02 Warm Comp.b3performance` as current state. Output bytes must equal the
source except for Registration's explicit expression substitution. Native
snapshot checks still require recipe 12's other fields, so Warm Comp's different
pedal/percussion/manual settings cannot leak into materialization.

All four runs compare every one of the 36 drawbar positions, both selected banks,
retained fixed modes, derived preset selections, route bits, pedals and all
percussion settings. In particular, Upper must return to cancelled/A with
retained G# memory; Lower remains B/routed, and percussion remains
On/Third/Soft/Fast. The hidden Upper B edit must be undone. Original source,
private state and replay bytes remain unchanged; no Save action is sent and
the native working directory gains only requested diagnostics.

## Reproduction and identities

From `/workspace/scratch/3edffb787db3/Hammond-B3-Organ`:

```sh
HAMMOND_STANDALONE_EXECUTABLE=../build-native/apps/standalone/hammond_standalone \
HAMMOND_REGISTRATION_EXECUTABLE=../build-native/hammond_registration \
python3 -B apps/standalone/native_tests/test_standalone_starter_load.py
```

Observed result: **2 methods pass, 4 actual standalone processes and 2 actual
materialization processes, 11.304 seconds**. Each native replay lasts 2,700 ms
with a 9-second subprocess bound; each CLI call has a 15-second bound. The test
sets SDL audio/video to `dummy` and renderer to `software`, verifies callback
and paint progress, zero runtime/session faults, no MIDI input/discovery and
joined stopped/unheld shutdown. It checks binary/input hashes again at completion.

| Input | SHA-256 |
| --- | --- |
| Native test | `22285ddcaec03adf61f97b1d65c7e70de4ee6c6437480267b4784ab8d360f5c7` |
| `hammond_standalone` | `82c6a9ffa056852b80d5505dec19aaec72f83965953d765bbee388cc8b1293c8` |
| `hammond_registration` | `872a343f20eb6710e6867fc4d1c0fe0b95118b883de21035ee70774f8762e13f` |
| Both Manual Return payloads, individually | `0ded9fedbae66cb9d706c4f6c9eda0a185903add490f09b47a8138a11e5851df` |
| Warm Comp current payload | `94b6ceada4ab630f1d8074586a5a3c820b4a7b9f31c928a1251390f716db3148` |
| Existing app-test helper | `5514d229bb969feeedd1be060d7e64dbd63cff22a08f0a70bd313d6308ae7236` |
| Existing workflow-test helper | `598d47281c936a37cb94a50b9dc83b2243f5b15a621afdad79ad343e1e738124` |

Recovery began at base `54df95fe343d417dd89bb7a91f85e4f51c08dfe7` with root's
uncommitted implementation. Subsequent HEAD inspection found root's implementation
commit `d281d4e3063f44b9eda6b5bc4ea44fc99a6c7f93`, tree
`1e59776459a05a9d934d0b519a45cd4c61b13ae9`; this test was still untracked.
The unchanged native binary also matches the
[frozen gallery qualification](../development/2026-11-16-preset-library-continuation/reports/apron-gallery-qualification.json).
Runtime: Linux x86-64, Python 3.12.14; root's Ninja Release build uses GCC 14.2,
`-O3 -DNDEBUG`, standalone ON, MIDI/VST3 OFF, and pinned SDL 2.32.10 at
`5d249570393f7a37e037abf22cd6012a4cc56a71`; native display/audio backends are OFF.

The first development invocation incorrectly supplied unsupported
`--presentation dimensional`; all four app launches exited 2 before runtime,
with `Unknown option: --presentation`, while both materializations succeeded.
The harness was corrected to use and assert the existing Dimensional default.
The passing run above follows that correction; no product behavior was changed.

## Integration and limits

Root owns CMake/build integration. Register `test_standalone_starter_load` with
both executable environment variables above, labels `standalone;native;registration`
and timeout 60. Ensure `hammond_standalone_test_inputs` depends on
`hammond_registration` as well as its existing app/profile dependencies.

This tests the existing explicit state path, not installed-pack discovery,
automatic startup import, native LibraryModel/browser selection or live
Registration recall. No musical notes, audio-device latency, physical MIDI,
real display/DPI, accessibility provider, audibility or physical fidelity is
qualified. No screenshot/raster test was added, and no main/UiModel/control,
file grammar, startup policy, pack data or Engine source changed.
