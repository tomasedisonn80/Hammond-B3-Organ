# A11 - Adapter impact audit

Actual worker: `/root/w02_a11_adapter_audit`, wave 2.
Owned outputs: this note and
[PRESET_ADAPTER_AUDIT.md](../../PRESET_ADAPTER_AUDIT.md).
The assignment was a bounded source audit; no production source, historical
fixtures, shared status documents, manifest, commits or branches were modified.
No child workers were spawned and no external research was performed.

## Source and executed checks

Baseline HEAD: `b79086f6bb0c42b97130c721c5c73c7c97a13887`.
Read `AGENTS.md`, the complete project plan, current status/next-step context,
the current session manifest, atlas review summaries, all three preset contracts
and the relevant adapter implementations and acceptance sources. This is not
another independent reading of all 500 PDF pages.

Used `rg` to trace explicit EventType allowlists, snapshot encoders, selector
extraction, UI/diagnostic fields, CLI score grammars and current/historical
parameter/state assumptions. Read corresponding functions and independent
fixtures. A Python identity check compared all 13 inspected production files
listed below byte-for-byte with `git show HEAD:<path>`; all matched. It also
recomputed the active registry's 45-record canonical digest and confirmed schema3.

| Inspected implementation | SHA-256 |
|---|---|
| `include/hammond/StateExchange.h` | `dfb4ec233f816edc223dfdf5b14da05cbca8a64534d5d725d307c2dff6d9933a` |
| `src/StateExchange.cpp` | `10a85957cad8e87e00f8ada543f697b9db4d59590b306baaae05fc0120a2a2bf` |
| `src/HostTimeline.cpp` | `37941dc9d833cabc1ed7ca22327ad23240ea8c04e6de9fc3f447222d2ebb41dd` |
| `src/PerformanceInput.cpp` | `fc9d3775ad1d3faf23beacb52c6c78108f967e8e7d209b74ef56e1a9caa44030` |
| `apps/standalone/Session.cpp` | `247c6a63dc9bb6c4e60398b17779a2d985058563b8d981c5e06426eab977f6ae` |
| `apps/standalone/UiModel.cpp` | `ac1a381367cfee7cce61e27ebd0b094c76a730806383e9ead609622687993e28` |
| `plugins/vst3/Controller.cpp` | `24b71a4a49d6234def8f9336e22de927577bf75bb859769b9af4a7ff840d41d6` |
| `plugins/vst3/Processor.cpp` | `a61e567798e7435c9d73ddab9bf925b6995396954e772c13f31571ad0a96f20b` |
| `plugins/vst3/StateStream.cpp` | `c83fbf22ea26c0b7a89974d4c0aa590c1e46f44f4a6c457d6fee512740d02117` |
| `tools/render.cpp` | `d84366dcb47f250569a67c8c8aa2fdfeba1b9c1abdc56819038a554b6a030cde` |
| `tools/parameter_info.cpp` | `4a8fd0fd0e55f882bd8b94519ed57798ce307100b5215df96964f52d2b885ce6` |
| `tools/render_fixture.py` | `f8da8a3a5633eb4d28e32a9e607ff579f188c520a89ae84dbc0c03684ccadcb1` |
| `tools/verify_render.py` | `0f212fd56423de617953be200bdfeacfeb807a3b6e280c8f0576242d79fd0539` |

Canonical old45 digest:
`13ba488bec90154c960c3fd700dc4a774aff5664caf5d68472821493f22d1cad`.
The packing calculation confirms 36 drawbar bytes leave 32 free high bits in
standalone word 4. StateExchange's proposed capacity is 47 + 3 = 50 cells.
These are source/identity checks, not executed callback or native acceptance.

Final document checks ran from the repository root: Python checked final LF,
trailing whitespace and all five relative links across the two reports; all
passed. `git diff --check -- docs/PRESET_ADAPTER_AUDIT.md
docs/development/2026-11-14-preset-continuation/11-adapter-audit.md` reported no
errors. Both owned outputs were new untracked documents at handoff; the explicit
Python check therefore also covered their content independently of Git's diff.

## Concrete findings delivered to the integrator

- StateExchange and Session both require raw fixed-mode publication. Pending
  state save alone will not expose the exchange bug; the acknowledged path will.
  A missing Session field can also cause a later UI edit to erase the audio mode.
- PerformanceInput and Session have separate explicit allowlists. Both must
  admit SelectPreset while Engine retains payload validation authority.
- HostTimeline already preserves explicit repeated gestures, ordered aliases,
  endpoint carry and raw normalized anchors. Add effective new-ID extraction
  only at preparation/restoration; do not recanonicalize anchors each callback.
- VST3 Controller needs effective selection extraction on restored state. Its
  accepted host-value cache remains raw. Processor and state-stream algorithms
  are already generic; new tests should verify their complete paths.
- Current47 inventories require careful oracle extensions. HostTimeline's broad
  `id >= 0x4000` eight-step check and native automation's index>=43 pedal fallback
  will misclassify the new selectors if only array sizes change.
- Archived pedal catalog tests and installed CLI tests wrongly equate a frozen
  v3/45 catalog with the active registry. Preserve the catalog and compare the
  old45 subset/digest within current47 instead.
- Current writers must produce state4 while historical v1/v2/v3 inputs remain
  intact. Controller legacy-fixture derivation and native chapel Save-byte
  equality need independent migration fixtures. Standalone diagnostics and its
  benchmark both explicitly enumerate controls and need the new raw fields.

The main report supplies exact ownership paths and six acceptance groups.
No production build or test suite was run for this documentation-only audit;
implementation, runtime qualification and integrator freeze remain subsequent
work. Shared status updates and publication belong to the integrator.
