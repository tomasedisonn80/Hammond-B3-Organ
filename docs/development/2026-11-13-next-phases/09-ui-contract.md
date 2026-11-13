# Assignment 09 — SDK-free standalone UI contract

## Identity, ownership and source boundary

- Actual assignment: `/root/w02_a09_ui_contract`, wave 2, first batch of the
  distinct next-phases sixty-assignment session.
- Owned files: `apps/standalone/UiModel.h`, `docs/STANDALONE_UI.md`, and this
  report only. No core, Session implementation, renderer, dependency, asset,
  shared status, historical ledger or commit was changed by this worker.
- Initial inspected HEAD: `ba0d9c9c75bd7a39152470f9f7ddb82287cb01b1`, tree
  `51fd7b24d2f373a693ced8dbde0fba762a3cc434`. During integration the root advanced
  HEAD to `2e917509b378d48c85cc1d52c3aa446eef9552c8`, tree
  `ac5f1888569339a9a3fd6c396d4d58fbe71dd503`. Concurrent files were preserved;
  this note identifies owned-header hashes instead of claiming a frozen full
  application build from that moving worktree.
- Read `AGENTS.md`, current scope/status/navigation, actual
  `ControlState.h/.cpp`, `ParameterBridge.h/.cpp`, core note/pedal ownership and
  percussion declarations, and wave 1 reports 05/06. Read relevant atlas text
  directly with `pdftotext` for pp. 397–402, 409–420 and 433–438; the single
  409–420 output had a bounded-output truncation at p. 415, supplemented by
  the complete assigned wave 1 source review. No fresh full-atlas or visual
  page-inspection claim is made by this assignment.

## Delivered contract

[`UiModel.h`](../../../apps/standalone/UiModel.h) freezes
`standalone-dry-ui-v1`, a C++20 interface containing logical geometry,
semantic control/note identities, copied presentation state and bounded typed
actions. [`STANDALONE_UI.md`](../../STANDALONE_UI.md) supplies the implementation
rules and its pending acceptance matrix.

The initial declaration has 18 visible manual drawbars over four retained banks,
two complete 61-key manuals, 25 explicit pedal keys and access to all 45 actual
parameter IDs. EDIT and SOUNDING are separate; SOUNDING reports the applied
snapshot. Cancel disconnects one route while preserving held owners and all
stored positions. Panic clears all owners without replacing controls. Four
percussion fields retain their stored positions while their upper-B eligibility
is displayed independently. Pedals and expression keep the existing nominal
mixture and linear-gain names, without physical calibration claims.

The root and assignment 07 agreed the exact shared namespace and transport:
`hammond::standalone::SessionCommand` is the variant of performance input,
complete control snapshot, scoped `ReleaseUiNotes`, and global `Panic`.
`UiActions` holds four fixed slots of that command or a main-thread app request.
The delivered header uses assignment 07's final **SessionStatus**, not the
earlier proposed SubmitStatus spelling. Offset-zero actions follow Session's
callback-boundary timing. Glissando preserves Off/On order, rejection stops the
rest of the batch, and queue overflow uses Session's global recovery mechanism.

Computer notes retain their original identity through manual/octave changes,
ignore repeats/duplicate Downs and release that exact identity on Up. Pointer
capture, outside release, capture failure/loss, crossing-key glissando, scoped
focus release and suppression until physical Up are explicit. One primary
mouse pointer is supported in v1; multi-touch and external MIDI-device transport
remain separate future adapters. Keyboard operation includes roving key focus,
explicit Space audition, Tab navigation, control adjustment and readable state
labels. No native accessibility implementation or screen-reader pass is claimed.

The logical layout is 1280×900 with minimum 960×700, using one shared geometry
for rendering/hit tests, half-open rectangles and accidental-key precedence.
Responsive section sizes, target counts, pointer drag identity and high-DPI
coordinate ownership are specified. Charcoal, ivory, brass, cyan and original
walnut tokens are included; fonts and a licensed glyph atlas remain the separate
asset assignment. No decorative scanner/rotary/fixed-preset control was added.

## Actual verification

Working directory for every project command:
`/workspace/scratch/5ba97739b54c/Hammond-B3-Organ`.

Observed compiler: **Debian GCC 14.2.0-19**. Executed a stdin translation unit
with no emitted binary:

```sh
c++ -std=c++20 -Wall -Wextra -Werror -pedantic \
  -Iinclude -Iapps/standalone -x c++ -fsyntax-only - <<'CPP'
#include "UiModel.h"
#include <type_traits>
using namespace hammond::standalone;
static_assert(kUiVisibleDrawbars == 18);
static_assert(kUiPlayingKeys.size() == 17);
static_assert(kUiMaxActions >= 2);
static_assert(std::is_trivially_copyable_v<UiControlId>);
static_assert(std::is_trivially_copyable_v<UiActions>);
static_assert(UiRect{10.0F, 20.0F, 4.0F, 5.0F}.contains({10.0F, 20.0F}));
static_assert(!UiRect{10.0F, 20.0F, 4.0F, 5.0F}.contains({14.0F, 21.0F}));
static_assert(!UiRect{10.0F, 20.0F, 4.0F, 5.0F}.contains({11.0F, 25.0F}));
static_assert(!UiRect{10.0F, 20.0F, 0.0F, 5.0F}.contains({10.0F, 21.0F}));
int main() { UiActions actions{}; return static_cast<int>(actions.span().size()); }
CPP
```

Result: **exit 0**, no diagnostics. This checks the real Session include,
declaration compatibility, fixed copied action properties and the small
implemented rectangle helper. It does not execute the declared input/layout
functions or qualify linking, rendering or audio. `git diff --check` passed;
because new files are untracked, a separate Python check also verified trailing
whitespace and final newlines in owned files and resolved their local Markdown
links. No optional broad regression or device run was warranted for declarations.

| Checked input | SHA-256 |
| --- | --- |
| `UiModel.h` | `c474d91b01cfea77ae7bf91e9a0088fb1e69c0b7b088912b9c798338ee76c9f5` |
| `STANDALONE_UI.md` | `382149ff2b953bc2c2b7c85193ad8150b7a562396201a7764f4706c5b560296b` |
| Collaborating `Session.h` | `0eed6c82d0cf5ffbeb0206f6f9702a93ef5a75cde6fd669b2862705dc7af84a0` |
| `ControlState.h` | `2fb1b7b7fc39363f7e53eb81e2edf3ddb88944b4aa20969b92a90f5c584b2edb` |
| `ControlState.cpp` | `d297545788fa62b0167fc0a9c07081b1f8af79bd1252ceb66d0d1326dd214e58` |
| `ParameterBridge.h` | `da68b2e5e2dae211597270924dbdad33c6be8606c5aaa164bd8de92878ea90a0` |
| `ParameterBridge.cpp` | `14d7dcfd24f5e7d6d59de8b31999ee52b33c64f73df453bff82b9eaa4f89dce0` |

## Next owner and unrun gates

Implement `UiModel.cpp` from the frozen declarations, then provide the thin SDL
scancode/capture adapter and renderer. The implementation owner must remove the
declaration-only status when its implementation is accepted. The public methods
are resize, key, pointer, activate, scoped release, Panic, validated load,
saved-copy marking, text-entry guard, submission feedback and Session snapshot
observation. All use fixed-size values; no widget hierarchy or optional skin
system is required.

Independent input tests must prove retained identity, overlap, bank-edit
separation, cancellation, scoped release, whole-control acknowledgment and
failure recovery. Actual linked-window runs must prove key counts, shared hit
geometry, labels and focus at the declared sizes. A header compile is not those
gates. Native accessibility, hardware latency/underruns, player testing, model
fidelity, asset rights and distribution remain independently unqualified here.
Root owns shared handoff updates, assignment acceptance and publication; this
worker made no commit or remote write.
