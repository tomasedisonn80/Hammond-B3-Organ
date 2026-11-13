# Assignment 49 — final core and input audit

Owner: `/root/w09_a49_core_input_audit`.

Assignment **49/60**, wave **9**, current 2026-11-13 pedal-development session.
This is one actual newly dispatched worker. The owned deliverables are
`docs/reviews/PEDAL_CORE_INPUT_FINAL.md` and this note. No subagents were spawned,
no production or test files were modified, and no staging, commit or push was
performed. Root owns shared status, the actual manifest and publication.

## Sources, question and decisions

Read standing instructions, the current pedal handoff, project plan, active
status/next steps and the combined-input/pedal-ownership contracts. Re-read the
complete extracted text of atlas pages **130, 132, 139–144 and 151** for explicit
ownership policies, source sharing, exceptional pedal connections and physical
model limits. This focused reading is not a new claim to have read all 500 pages
or independently inspected every diagram. Used the managed runtime skill; its
environment-status tool was not exposed in this worker's tool registry. No
network access, dependency installation or environment change was needed.

Inspected the actual Engine, pedal bus/voice, both ownership adapters, combined
facade and control persistence implementations and their interfaces. Examined
how the independent CSV/source and combined physical-event oracles avoid using
the production translator as their own answer. Existing tests already exercise
the concrete late-failure, remapped-route, capacity, source-history and migration
risks; no unverified defect or useful missing production regression was found.
Did not add a test that only mirrors the implementation or change code for churn.

The [review](../../reviews/PEDAL_CORE_INPUT_FINAL.md) develops the code reasoning,
actual results, limitations and two observed stale current-contract passages.
Root acknowledged their exact locators and coordinated their documentation
follow-up with assignment 55. They are outside this assignment's edit scope.

## Coherent source and binary association

Used the pre-existing frozen archive
`/workspace/scratch/f364bc93d920/checkpoint-w07/source`, tree
`7c3e1e2e93932dfa59f20e2be8ee4ab7f46b8f73`, with its corresponding SDK-free
`checkpoint-w07/build-default` binaries. Independently enumerated every Git tree
entry and recomputed `SHA1("blob " + size + NUL + bytes)` for all **495 files**.
Every blob matched. Retained a SHA-256/size/mode inventory in scratch
`a49-core-review/source-inventory.json`, SHA-256
`2fd1c31ba2b137fccdca0e69fa326a872c037bc897270a358763a9892be22d78`.
All 495 files and the 20 selected binary hashes matched again after execution.

The audited source/header/data/C++ test inputs were unchanged at published
`7fb9b6121b729f46a9e18d80e8620eb21dc0847b`, tree
`19239e05f6c5219b50d3f398ba9a6eb3acc2a1ac`, and in the current live core worktree.
Within the checked `src`, `include`, `tests`, `data` and root CMake paths, the
only published delta from the initial archive was two Python install/inventory
test files, which this run did not select. The full trees are therefore not
claimed identical. No live newer headers were linked to an older core.

The existing build's actual cache/flags/link command showed Unix Makefiles,
Release, GCC 14.2.0, CMake 3.31.6, C++20 and `-O3 -DNDEBUG` plus project warnings
and `-Werror`. The tests use active CHECK functions under that configuration.
The compiled profile is 4,545 bytes with SHA-256
`b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f`.
`libhammond_core.a` is 217,906 bytes with SHA-256
`9bbbb736e8c965cdfa11fead46a2b54539be61b7ddebf30b5a803c415252ace0`.
This assignment reran focused tests; it did not claim a fresh build.

### Inspected implementation identities

| Frozen file | SHA-256 |
| --- | --- |
| `include/hammond/Engine.h` | `b2aea1dae1e54654cacb8576295b27d47673c87a9a01e17fd3eba7a843fa188c` |
| `src/Engine.cpp` | `e082d07323c506f58c726c76a8459bbbec9b01fcb7b20ca6d6323c065fa6664c` |
| `include/hammond/PedalRouting.h` | `e77c52f1c541ef301fff4c8b0fb9a9449f93be632630326f2d7640694384bea8` |
| `src/PedalRouting.cpp` | `8d05dedb9015863dfd88668e5ea27d6be42ea1fcdb600cf34787e446e14d22af` |
| `include/hammond/PedalVoice.h` | `694961946eac838c689547fc403c84e49a429f3337816ea9ad3a751bf305ddaf` |
| `src/PedalVoice.cpp` | `88fb5afa936784be351b2940ee6f81216975112f860b007d40f3b6a3d9f7c6ba` |
| `include/hammond/PedalNoteOwnership.h` | `3df590c6747f01a19651b2220b3c002422c8934ff06710bc97be8f47c4747d33` |
| `src/PedalNoteOwnership.cpp` | `a938f9d03a1a05d20cdf5d41567bd9c44bd3f5581ec446897ef79386d148acde` |
| `include/hammond/NoteOwnership.h` | `03baaa46de8c24d346c86a64a09e0503e85b78854d143a1cd616aeda38e4b1dc` |
| `src/NoteOwnership.cpp` | `f16e7a2f1698898a5552f73004992fb16225b1247d4e0f3170cca201e78b5751` |
| `include/hammond/PerformanceInput.h` | `f3b4185393da324ab1433514f141e42aab1056d7dac4fd402184b1c2d0dd04ae` |
| `src/PerformanceInput.cpp` | `fc9d3775ad1d3faf23beacb52c6c78108f967e8e7d209b74ef56e1a9caa44030` |
| `include/hammond/ControlState.h` | `2fb1b7b7fc39363f7e53eb81e2edf3ddb88944b4aa20969b92a90f5c584b2edb` |
| `src/ControlState.cpp` | `d297545788fa62b0167fc0a9c07081b1f8af79bd1252ceb66d0d1326dd214e58` |
| `src/ControlStateIO.cpp` | `a1043d29d2321cccad4e994afbf62e16d93ce6cd15ce5c7593556daff1b0a8cf` |

## Executed command and result

Executed with the actual task-local CTest path:

```sh
/workspace/scratch/f364bc93d920/tooling/cmake/data/bin/ctest \
  --test-dir /workspace/scratch/f364bc93d920/checkpoint-w07/build-default \
  -C Release -V --no-tests=error \
  -R '^(test_control_io|test_controls|test_core_robustness|test_engine|test_engine_rate|test_note_ownership|test_pedal_controls|test_pedal_engine|test_pedal_integration|test_pedal_note_ownership|test_pedal_reference|test_pedal_routing|test_pedal_sources|test_pedal_voice|test_performance_acceptance|test_performance_input|test_realtime_pedals|test_contact_rate|test_percussion_rate|test_source_rate)$' \
  --output-junit /workspace/scratch/f364bc93d920/a49-core-review/ctest.xml
```

Result: **20/20 suites passed, zero failures, zero disabled tests, zero skips**.
CTest reports **2.98 seconds**; the wrapping monotonic measurement was
2.987992 seconds. All commands exited zero. The JUnit timestamp is
`2026-11-13T04:20:30`. The verbose log retains each suite's actual numerical
counters, observed allocation calibration and explicit scope limitations.

| Retained local record | SHA-256 |
| --- | --- |
| `a49-core-review/ctest.log` | `91e283bb638dc1f35460321467a6b6af292f3e823dce081ee466cf45bab01ddd` |
| `a49-core-review/ctest.xml` | `1dea377ac6d05ec1dbc97fd9717643a8c7fb03a258dc2cbdea3dc836b9184980` |

`a49-core-review/results.json` retains the exact argument vector, source/commit
identity, process exit status, timing, JUnit summary and all selected executable
hashes. The complete regression command and durable identity tables here permit
reproduction even if scratch records later expire.

### Executed binary identities

| Existing Release executable | SHA-256 |
| --- | --- |
| `test_control_io` | `1825daea07c95d875c4f3105845bd8f1ca59fc1a8f8fc9e6d735c7f3b6a29e24` |
| `test_controls` | `e8c9092c7d98eb16aa6c031e48d494611a81795037aedf411c552dc1ae2b3ed6` |
| `test_core_robustness` | `33a4a98304e319ec4edd3f82b95f99007e83bf2a5345d0a7a463eec2978b5669` |
| `test_engine` | `c551f900e5526d7f44f4d60aa853168a18e1db3770658a9e7b5a8cb5ea2140af` |
| `test_engine_rate` | `ba1da807e8a4629203f51158f9f285a9b7ca770dd084bd2e1ebae47eb23d668a` |
| `test_note_ownership` | `533a2bd15fda689a00dafed2d6a80ad3a2466c81aa26adebccbb88a7e2abc245` |
| `test_pedal_controls` | `9ceec8f6e37bedc285aa98936ba579089a7974cf70e46f41d1225c81aa6531ae` |
| `test_pedal_engine` | `199f72ac639dcbedd60891125d49ece48c48f94295c44968846033f949063c1c` |
| `test_pedal_integration` | `20cea76ce4c5547a39e2c60aa63b7d49bd40b86137549496082b0b6a611753c8` |
| `test_pedal_note_ownership` | `b3bc3353ca6e202631842b42881e2bef66dd5c492b1fae21c7b1991932544124` |
| `test_pedal_reference` | `d6e5f66f4ae56c58882e455b9aa54d169c479c7b4c11aa7f7d094b051b539728` |
| `test_pedal_routing` | `bb920693e0e92e772303d188d0328ade5924bbaf20b33582d67c5cd0bbf7d3a7` |
| `test_pedal_sources` | `cab5a5b1d724914ac468cccfdac018c08ccd1afb48a9dc8fe3956829fe961478` |
| `test_pedal_voice` | `761dbc9886ca168dce89129898af0e60b2be9ebeb6a694077ca5f858deefb761` |
| `test_performance_acceptance` | `e2dbda5487715581374540f929a4138c25fa03ac657d1a403a486da9babb5a84` |
| `test_performance_input` | `b32007fbc7fc6c1e8664b6650117ed26862a3c343d8af347cabb060a93ff613f` |
| `test_realtime_pedals` | `307a1b89698fe2de0d7200c7c9be62b113876cbfedaba04e3aecb355031adf86` |
| `test_contact_rate` | `a48cd987b5e564d7074a6408c254bb632a9b614ed369a7c9b74a7c7c29ebca21` |
| `test_percussion_rate` | `a188e9961e65acf3437e808524aff4e667989b91192abfa38665b968009eea81` |
| `test_source_rate` | `62f65d2602d495df4fdacd0dfeba15c256f96bfd702688cb008cef39065ec11f` |

## Outcome, limits and next step

No actionable production defect was found. The executed suites cover both
ownership capacities independently, expanded and raw 1,024/1,025 boundaries,
all 25 pedal targets and 200 contact positions, explicit physical-event oracles,
old-route releases, zero-frame and disconnected execution, control migration,
rate changes and future output after failures. Their finite scopes are detailed
in the review; counts from different suites must not be added as a count of
unique independent physical evidence.

The 180-region allocation gate observed zero calling-thread global C++
new/delete after detecting its 12 allocation/free calibration pairs. It does not
measure C heap activity, every lock/syscall or actual audio-device deadlines.
The existing native SDK, platform artifact and DAW/device gates remain separate.
No external CI pass, physical calibration, hardware measurement, subjective
listening or full M3 completion is newly claimed here.

Root should incorporate the two documentation follow-ups through assignment 55,
retain this exact focused evidence, run the integrated wave/final publication
gates and publish only completed work. For subsequent model changes, begin with
[M3_REMAINING_AND_SCANNER_GATE.md](../../M3_REMAINING_AND_SCANNER_GATE.md) and
preserve the old dry arithmetic order, single source phase, permanent control
identities and explicit nominal-model labels.


## Deliverable verification

Both owned Markdown files pass UTF-8/LF, trailing-whitespace and local-link
checks. The first QA wrapper treated `git diff --no-index --check /dev/null FILE`
exit 1 for a new-file difference as a command failure despite no whitespace
diagnostic. The corrected wrapper accepts that difference status only
with empty stdout/stderr; both files then passed without a content repair.
This was documentation-check orchestration, separate from the passing CTest run.
