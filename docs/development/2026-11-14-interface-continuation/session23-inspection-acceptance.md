# A23 — independent inspection acceptance

Actual worker: `/root/w04_a23_inspection_acceptance`, wave 4, assignment 23 of
this session's 60 requested distinct workers. **Accepted within the SDK-free
model scope:** the new independent acceptance test and unchanged author test
passed **2/2** in **0.01 seconds**. No production defect or change was required.
The integrator owns shared handoffs, CMake, staging, publication and final acceptance.

## Evidence and source audit

Read `AGENTS.md`, the current scope/checkpoint, the complete project plan,
`INTERFACE_INSPECTION_CONTRACT.md`, and the actual Session, default Engine prepare,
console/contact, source-profile, control, percussion, pedal and scanner code.
The [machine-readable report](reports/a23-inspection-acceptance.json) retains all
30 audited source-file hashes, toolchain, artifact hashes, outcomes and limits.
All 30 hashes remained unchanged across the final build and focused tests.

The reviewed checkout HEAD was `5d81199a9822874b55f3b0a124715cbd6eadf0e5`,
tree `52b4ec72b77e4442efe2e9e1b089b7b0ea6e638b`. Inspection and UI additions
were a working-tree overlay; that commit alone does not identify the tested code.

| Input or binary | Observed SHA-256 |
|---|---|
| `InspectionModel.h` | `d16fe12811c399fd9edc03286ec00767e086268447e03f40fa9d9cdf9badddb9` |
| `InspectionModel.cpp` | `59df4b36e7b565a6f07f2efee63634953b55112b24927292d2f884ddddda8645` |
| New acceptance source | `a3f09a51f2d1e39a6f051934a0efba8a7617024063c371ec6ed32ba52f9900e3` |
| Acceptance executable | `9ccb3c4590b60d7c81594a8a3fdc145b5f13d564cdd0eddc5cad7907d864d720` |
| Author executable | `37512d878941600db15b40159acfe1a94be08470cd2f615e2930b4259fa3f68a` |
| Loaded compiled profile | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

The 34 populated rows match the contract's values, units, evidence classes,
availability and source locators. Session calls the two-argument Engine prepare;
an actual prepared Engine independently reports **Ideal** contacts. The linear
travel model and its synthetic timing are not active. The generator has 91 shared
sources; a loaded profile with changed source-46 frequency, gain and declared
digest successfully prepares and supplies the displayed values.

Scanner remains a research module outside Engine. Its existing **G5 same-hertz
failure** in `SCANNER_HANDOFF.md` is not closed by these tests. Percussion remains
the nominal AO-28 surrogate; complete AO-28 and Leslie audio are unconnected.
The 122 baseline/147 separation, unacquired specimens, voltage, rotor speeds and
microphone geometry retain explicit words and units, without fabricated zeros.

## Independent cases executed

- Real `Session` prepare/start/render/stop and `UiModel` load/submitted/observe
  paths distinguish an accepted queued restore from applied controls. Actual
  selector commands exercise Bank A, Bank B, fixed F# and Cancel on **both**
  manuals. Four unequal raw bank memories survive fixed selection and Cancel.
  Deliberately contradictory, invalid desired copies cannot replace applied
  values; edit-bank and pending labels remain independent.
- Held counts come from real endpoint manual/pedal commands. Two owners of one
  target count once, and releasing only one owner retains that target. Structural
  Upper-B eligibility covers every boundary, including retained percussion Off
  while eligible. These observations make no audibility/readiness claim.
- All five snapshot states are exercised. Current at frame zero stays Current;
  an actual stop changes Session while an older UI copy remains unchanged.
  Finite publication limits produce **real failed `read_snapshot` calls** with
  byte-preserved destinations. The inspector retains exact controls, holds,
  frame, revision and pending state; failed-read precedence also overrides a
  copied Stopped state at a large clock. Missing observations say Not observed.
- Invalid inactive/cancelled enums, inactive bank memory, NaN/infinity, adjacent
  finite boundaries, malformed/unterminated IDs and digests fail closed.
  Repeated output is deterministic; profile/view/runtime bytes stay unchanged.
  Returned copies survive input mutation and destruction. All current text,
  64-character digest, counted rows and unused slots remain bounded.

## Reproduction and limits

GCC **14.2.0**, CMake/CTest **4.4.4**, Linux Release; native standalone, MIDI and
sanitizers disabled. Reused `../build-a13-sdkfree`; no extra source/dependency or
build tree was created. From the repository root, with CMake/CTest at
`/workspace/scratch/7ffc2842608b/build-tools/cmake/data/bin/`:

```sh
cmake -S . -B ../build-a13-sdkfree -DCMAKE_BUILD_TYPE=Release -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_ENABLE_MIDI=OFF
cmake --build ../build-a13-sdkfree --target test_standalone_inspection_acceptance test_standalone_inspection_author --parallel 3
ctest --test-dir ../build-a13-sdkfree --output-on-failure --no-tests=error -R '^test_standalone_inspection_(acceptance|author)$'
```

Strict C++20 syntax also passed with `-Wall -Wextra -Wpedantic -Wconversion
-Wsign-conversion -Wshadow -Werror`, the ordinary include paths and test-profile
definitions. The first syntax-only draft exposed two fixture errors: nested
`std::array` assignment and mutation of a const lambda capture. Both were fixed
before the first binary build; the first CTest run passed in 0.02 seconds. Final
review added Cancel directly after adjustable B to isolate route ineligibility
with fixed None retained; the final two-suite gate passed in 0.01 seconds.
Configure/build/CTest logs are beside the report. No production failure is
inferred from the initial fixture errors.

No additional allocator probe or author-style 128-case Cartesian product was
added. The private overflow writer is source-reviewed; no currently admitted
field reaches its 127-byte payload limit. Formatting does not fetch private
Engine state behind a UI copy. Native font/forced-snapshot pixel acceptance
remains A25/A36 work; device, concurrency, deadline, accessibility, scanner G5,
calibration and physical fidelity gates remain open. Owned changes are the new
test, this note and `reports/a23-*`; no commit or staging was performed.
