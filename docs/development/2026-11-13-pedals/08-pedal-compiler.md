# Assignment 08: strict compiled pedal routing

Owner: /root/w02_a08_pedal_compiler

Wave 02 of the new pedal session. This worker implemented the offline compiler and build dependency boundary; the integrator owns shared status and publication.

## Implemented scope

Added [compile_pedal_routing.py](../../../tools/compile_pedal_routing.py) and its [independent compiler tests](../../../tests/test_compile_pedal_routing.py), and extended [CMakeLists.txt](../../../CMakeLists.txt). The unchanged map, factory comparison manifest and both independent pedal CSV readings are explicit build inputs. The existing strict pedal-map validator and immutable factory-manifest validator are reused.

The compiler reads each input once within bounded regular-file reads: map 32 KiB, reference manifest 256 KiB and each CSV 8 KiB. JSON rejects duplicate names, nonfinite/fractional tokens and malformed UTF-8; existing validators enforce the exact supported semantic contracts. Both CSVs are parsed in their ordered 25-by-8 form, then every one of their 200 cells is compared with the admitted map. Missing contacts remain explicit nulls, and repeated sources remain separate branches. The immutable manifest's expected raw lengths/digests and map canonical digest are checked. None of this re-establishes the historical transcribers' independence or verifies physical continuity.

The output is a deterministic LF-only C++ header, with no absolute paths, timestamps, gain weights or MIDI policy. It contains `hammond::generated::kPedalRoutes`, an `inline constexpr PedalRouteDefinition` with 200 explicit row-major `PedalRoute` entries; disconnections use `std::nullopt`. The following program-lifetime string views retain the separate evidence identities:

- `kPedalMapId`, `kPedalMapRawSha256`, `kPedalMapCanonicalSha256`.
- `kFactoryComparisonId`, `kFactoryComparisonRawSha256`.
- `kPedalReviewASha256`, `kPedalReviewBSha256`.

Reference-manifest formatting may vary while its exact version-1 semantic contract is enforced; its actual raw digest is retained. Map and CSV raw identities remain frozen by that attestation. The map's historical original-authoring provenance is not rewritten.

CMake's `hammond_pedal_routing` target generates `generated/hammond/generated/PedalRoutingData.h` and is a dependency of `hammond_core`. Its dependencies include the compiler, both imported validators, map, manifest and both CSVs. The generated include directory is private to the core. The organ `B3PROFILE1` format and nominal source profile are unchanged.

## Publication and failure contract

Complete validation precedes output publication. The compiler rejects an output that aliases any input, including a hard link. It writes a same-directory temporary file, flushes it, then uses atomic replacement. Invalid input or a failed publication preserves an existing header; temporary files are removed on the exercised replacement-failure path. Successful publication is not rolled back if a later CLI summary cannot be delivered. Generated text has a 64 KiB bound. No third-party dependencies or assets were added.

## Actual execution and evidence

Direct compiler invocation succeeded:

```sh
python3 tools/compile_pedal_routing.py \
  --input data/pedal-map.json \
  --reference data/references/factory-table-iii.json \
  --review-a data/references/review-a-pedal.csv \
  --review-b data/references/review-b-pedal.csv \
  --output /workspace/scratch/f364bc93d920/pedal-a08-generated/hammond/generated/PedalRoutingData.h
python3 -B tests/test_compile_pedal_routing.py -v
```

All **16 Python methods passed**, zero failures/skips, in 3.380 seconds. They independently parse both CSVs to check all emitted entries and separate repeated branches, verify exact raw/canonical identities, exercise input bounds and malformed identities, reject output/input aliases, and inject an atomic-replace failure to check old-output preservation and temporary cleanup. They also check that source files remain unchanged.

Using task-local CMake 3.31.6, configured an isolated Release build at `/workspace/scratch/f364bc93d920/build-a08` and built `hammond_core --parallel 2`. **The generated header and complete core compiled successfully with GCC 14.2.0 and strict warnings.** Agent 07 confirmed the header and core implementation interface was frozen during this build. The focused CTest registration `python_test_compile_pedal_routing` also passed.

Observed unchanged map SHA-256: `58a30850c08933a075cfcec04faeb2cb479f60bd9dda82ace3246552221623bd`. Both CSVs remain 677 bytes with SHA-256 `b8177479a5af16f4e6b8759313d90148a1213657c83f8a6e6533422bfa104ca1`. The reference manifest is 6,647 bytes with raw SHA-256 `8c52ccca13653c6e379da33a10197bfc9ac1a1f3ab6bea6bbe8edf81f7a47b52`.

## Handoff and limits

Agent 07 consumes the frozen generated names in the native kernel. The next independent native gate must compare the compiled runtime table against both CSVs and exercise all branch/source/lifecycle behavior; the compiler's own textual-output checks are not a substitute for that gate. Root owns coherent combined regression, hosted platform qualification and commit/push. No physical voicing, pedal audio, native host qualification or whole-session completion is claimed here. No commit or push was performed by this worker.
