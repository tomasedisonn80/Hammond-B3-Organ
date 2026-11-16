# Registration compatibility and ownership admission

16 November 2026; A39 (`/root/w07_a39`), wave 7. **Admitted within the reviewed
compatibility scope; no production defect found.** Compared published base
`54df95fe343d417dd89bb7a91f85e4f51c08dfe7` with local implementation
`d281d4e3063f44b9eda6b5bc4ea44fc99a6c7f93`, tree
`1e59776459a05a9d934d0b519a45cd4c61b13ae9`, and root's subsequent native-Load
CMake wiring. This identifies local reviewed inputs, not a remote publication
or hosted result.

The [independent audit receipt](../development/2026-11-16-preset-library-continuation/reports/a39-compatibility.json)
retains commands, complete hashes, byte comparisons and the inspected native
CTest log. A39 executed only read-only source/hash/diff checks: no configure,
build, test suite, renderer, benchmark, commit or push.

## Preserved musical and ownership boundaries

All 507 entries in the original baseline input manifest match the base Git
objects. Direct base/implementation/worktree comparisons find zero differences
in 31 core headers, 30 core sources, 20 plugin files, 72 pre-existing data files
and 24 top-level application files outside the expressly admitted painter/store
paths. These tree identities are unchanged:

| Tree | Git object |
| --- | --- |
| `include/` | `9a3c71eacf360e9dab78e74c0e675cd74e778f2c` |
| `src/` | `09948c8801c1f37c0eb3bde7700234a16adaed97` |
| `plugins/` | `b13032ad4419df067f3a2ce65dc92ed17fd854c4` |

The native descriptor table contains **47 unique IDs**, exactly matching the
unchanged registry's ordered ID/path pairs. `B3CONTROLS4`, readers 1–3, migration
defaults, fixed-catalog identity and profile formats are unchanged. The two
VST3 FUIDs remain `19F9ADC0-533F42B4-B96BD51D-6547E838` and
`0DEE76AB-26BC475A-BF64F138-C89FB0E0`.

The unchanged Engine/TonewheelBank retain **91 shared free-running sources**,
nominal dry routing, note ownership, velocity-independent steady gain and
phase/contact/percussion histories. `restore_controls` restores only validated
musical controls and marks coefficients dirty; it does not reset those histories
or the frame clock. Saved files contain no DSP checkpoint.

`main.cpp`, Session, StateFiles, UiModel, MIDI, inspection and geometry sources
remain unchanged. No LibraryModel/browser or other owner's contact, manual,
rim, cap or semantic implementation is introduced or reassigned. InstrumentView's
sole change replaces one wide-apron paint call with an optional texture and the
same procedural fallback/bounds; Drawing adds its separate texture lifecycle.
Other painting functions and live control geometry are unchanged. The existing
[paired raster evidence](../development/2026-11-16-preset-library-continuation/reports/apron-paired-final.json)
retains pixel-level scope; this audit does not repeat its visual acceptance.

The only existing-store change is the narrow ASCII-component distinction proof
authorized in [ROOT_DECISIONS](../development/2026-11-16-preset-library-continuation/ROOT_DECISIONS.md).
Whole corresponding components must both be ASCII before their folded difference
proves distinction. Otherwise the original conservative comparison remains;
native equivalence, ancestor/suffix, link and ambiguity checks still apply.
Public APIs, merge policy and state grammar are unchanged. The original Unicode
failure and [six affected passing CTests](../development/2026-11-16-preset-library-continuation/reports/w04-path-qualification.json)
remain separate evidence.

## Saved-controls ordering and genuine baseline binding

Renderer input admission precedes output creation. After Engine preparation,
the controls branch restores the full snapshot at clock zero. The old
drawbar/percussion/pedal setters occur exclusively in its `else` branch;
explicit conflicting flags reject. Scored events apply afterward, including
frame-zero overrides. Schema 6 records initial canonical state4; no-controls
schema 3/5 selection stays unchanged. Neither filename suffix changes generic
Load/render scope: both restore expression. Explicit Registration materialization
uses the existing merge helper to preserve supplied current expression;
Performance restores the entry value.

I rehashed both retained executables and the actual profile, compared complete
WAV/stdout bytes, checked both receipts and verified identical arguments except
the output path:

| Bound input | SHA-256 |
| --- | --- |
| Genuine baseline renderer | `928205dc3b31e57faa7664cb39e691659d1c7f7430b5555ade70b4a9830835bf` |
| Candidate renderer | `671375f6f9d393295bca148bcb546a1eb387dd865e994e755f16933389a16263` |
| Compiled nominal profile | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

The 8,192-frame default and 16,384-frame nominal/percussion WAVs are respectively
32,812 and 65,580 bytes; their 1,278/1,289-byte stdout records also match exactly.
All four stderr files are empty. The [original comparison](../development/2026-11-16-preset-library-continuation/reports/renderer-legacy-comparison.json)
therefore remains bound to present bytes, not merely asserted receipt booleans.
This verifies two retained observations; it adds no new render or universal
cross-platform bit-identity claim.

## Native integration and remaining gates

Current CMake SHA-256 `8c9083d5de40ab398c224e61550f5b218b02ebe7c8d7cc0bc94078e92dff99cf`
registers `test_standalone_starter_load` under standalone/testing, supplies both
executable paths, timeout 60 and `standalone;native;registration` labels, and
adds the registration executable to `hammond_standalone_test_inputs`. Generated
CTest/Ninja files independently confirm this wiring. Root's inspected focused
CTest passes in **11.38 seconds**: two methods, four dummy-SDL applications and
two materializations. The test proves edits were acknowledged before generic
Ctrl+O, then all restored fields matched; startup alone cannot satisfy it.
Existing app/registration executable hashes remain unchanged.

No-SDL availability is structurally supported by the headless target graph;
A38's separate clean Linux OFF configure/build receipts already pass. Further
headless execution belongs to A38's source-bound evidence, not this audit.
Windows/macOS/MinGW, real display/DPI, accessibility, physical audio/MIDI, DAW,
deadlines, signed distribution and physical fidelity remain unqualified here.
Literal whole-interface **1:1 remains open and unwaived**. Root must preserve
separate later focused qualifications, verify publication/tree identity and
observe hosted jobs at that exact source; the earlier 230-test run is not a
fresh run of subsequently changed tests/CMake.
