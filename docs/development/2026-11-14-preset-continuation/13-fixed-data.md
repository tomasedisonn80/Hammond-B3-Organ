# A13 — Immutable fixed-registration data

Worker: `/root/w03_a13_fixed_data`, logical wave 3, 2026-11-14.
Base commit: `b79086f6bb0c42b97130c721c5c73c7c97a13887`.
Scope: the frozen `exclusive-fixed-registration-core-v1` data API and native
generation. This is implementation and focused engineering evidence; the
integrator owns coherent full-tree acceptance and publication.

## Implemented

Added the exact `FixedRegistration` and `PresetSelection` domains, constants,
position alias, validators, checked row copy and program-lifetime label/catalog
views in `include/hammond/FixedRegistration.h` and `src/FixedRegistration.cpp`.
The public header was delivered to the concurrent core/state workers before
their integration. Invalid/None row lookup preserves every destination byte;
fixed A and adjustable A# remain different typed identities.

`tools/compile_fixed_registrations.py` calls the existing strict
`compile_chapel_presets` admission with the authoring JSON and **both** independent
CSV inputs. It then requires the admitted raw authoring SHA-256, rather than
reopening the source or substituting canonical JSON identity. Consequently an
equivalent reformat, added LF or CRLF checkout rejects this runtime model even
though the documentary compiler can still inspect it. The existing repository
LF checkout policy remains intact. Atomic publication reuses the strict catalog
writer's bounded text, nonsymlink regular output, input-alias protection,
temporary write/flush/fsync and replacement behavior.

The generated private header holds exactly 2 × 9 × 9 immutable tap indices and
the frozen catalog ID/hash as `inline constexpr` data. The runtime implementation
contains array copies, bounded checks and string views; no JSON, filesystem,
dynamic storage, lock, first-call initialization or mutable table is introduced.
`cmake/CompileFixedRegistrations.cmake` lists the generator, strict compiler,
schema, authoring and both reviews as dependencies and makes `hammond_core`
depend on generation. `CMakeLists.txt` adds only this include and its explanatory
comment. The original documentary catalog remains a separate build output.

## Executed checks

Working directory for every command below:
`/workspace/scratch/a472c29da8b3/Hammond-B3-Organ`.
Toolchain: GCC 14.2.0, Python 3.12.14, CMake 4.4.4 from the retained native
toolchain. No full live-tree build or link against stale core objects was run.

1. `python3 -B tests/test_compile_fixed_registrations.py -v` — **17/17 methods
   passed**, 3.282 seconds. Covers all 162 independent oracle digits, actual
   three-input admission, frozen raw identity, semantically equivalent source
   reformat rejection, each mandatory review, invalid/bounded JSON, strict CLI,
   source/symlink/hardlink output protection, exact successful LF bytes and
   injected short-write, fsync and replacement failures with unchanged prior
   output and cleaned temporary files.
2. Generated `/tmp/hammond-preset-a13/generated/hammond/generated/FixedRegistrationData.h`
   using the real CLI and all three unchanged repository inputs — exit 0.
3. Built and ran the isolated native fixture — compile and execution exit 0:

   ```sh
   g++ -std=c++20 -O2 -Wall -Wextra -Wpedantic -Wconversion -Wsign-conversion -Wshadow -Werror \
     -Iinclude -Itests -I/tmp/hammond-preset-a13/generated \
     -DHAMMOND_TEST_PROFILE='"/tmp/hammond-preset-a13/unused-profile.b3p"' \
     -DHAMMOND_SOURCE_DIR='"/workspace/scratch/a472c29da8b3/Hammond-B3-Organ"' \
     src/FixedRegistration.cpp tests/test_fixed_registration_data.cpp \
     -o /tmp/hammond-preset-a13/test_fixed_registration_data
   /tmp/hammond-preset-a13/test_fixed_registration_data
   ```

   The fixture uses `tests/PresetTestOracle.h` for all eighteen literal rows,
   verifies caller-copy isolation, checks all **65,536 manual/registration byte
   pairs** and guarded destination preservation, all 256 label/validator values,
   exact frozen identities, view pointer stability and the declared no-throw
   signatures/type identities.
4. The initial unqualified `cmake` command failed because CMake was absent from
   this worker's PATH (exit 127). Reading the baseline's actual `CMAKE_COMMAND`
   resolved the setup issue without changing source. The following configure,
   generation-only build and byte comparison then passed:

   ```sh
   /workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/cmake \
     -S . -B /tmp/hammond-preset-a13/cmake -DBUILD_TESTING=OFF \
     -DHAMMOND_BUILD_STANDALONE=OFF -DHAMMOND_BUILD_VST3=OFF -DCMAKE_BUILD_TYPE=Release
   /workspace/scratch/641ca55ce6de/native-toolchain/cmake/data/bin/cmake \
     --build /tmp/hammond-preset-a13/cmake --target hammond_fixed_registration_data --parallel 2
   cmp /tmp/hammond-preset-a13/cmake/generated/hammond/generated/FixedRegistrationData.h \
     /tmp/hammond-preset-a13/generated/hammond/generated/FixedRegistrationData.h
   ```
5. Owned-path `git diff --check` passed. Original authoring, both CSV readings
   and source PDF hashes below remain unchanged. Atlas pp. 121–126 were freshly
   read as extracted text, including the eighteen-row table on p. 122.

## Exact checked identities

| Input or owned source | SHA-256 |
|---|---|
| Frozen authoring JSON | `c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf` |
| Each independent CSV | `dc2a8fd4e9750133c982bb42fd6cc7c12908f011154826035bb623f52d8de694` |
| Original source PDF | `4ae13c3065c60d733d0daa33817259b3198cdb959070baecadc2981678e5e769` |
| `include/hammond/FixedRegistration.h` | `4548240ce25f5200442bfe4607ba755feee822a91c8b1a97af9bf7837e3634a0` |
| `src/FixedRegistration.cpp` | `690e45e5738c3c25ae1082e31a49debdfbca994b68d6b0a28ef865df7991769d` |
| `tools/compile_fixed_registrations.py` | `234d2430d202873e3211c11cd0a1317bb7b73d6722ed3b12992083cb1fe5d3bd` |
| `cmake/CompileFixedRegistrations.cmake` | `c9dba11f08dac36317a02028bb706d73fc39a91ede3776e9fcdce0d08cea5e1c` |
| `CMakeLists.txt` | `1e3d06b974697be6ac58fe3d01507878ee59ef4dafe741724c76eac7b666b0f3` |
| `tests/test_fixed_registration_data.cpp` | `8339064d2a135fefc9047919873cecb62b48054fed3fe501a40d8e4c02f00fdd` |
| `tests/test_compile_fixed_registrations.py` | `77957700026fe99444212bdffaefab91cc96c9a1425f4d4639f270425bf19e32` |
| Generated native header (both paths) | `66cbb1a23cb5ebf14844afd6f98e13829c9f69c1511b09d5974ca5a4527157c6` |

## Handoff and limits

The new native/Python tests are discovered by the existing CMake test globs.
Once concurrent core/state/adapter changes are frozen, the integrator should
build their consumers coherently and execute these tests with the affected
engine, persistence and parameter gates. A separate measured callback-allocation
probe and host/native acceptance remain assigned work; source inspection here
does not claim those measurements. The admitted values remain documentary tap
indices, with physical latching, specimen wiring and loaded gains unverified.
No source JSON/CSV/PDF, historical fixture or other worker's owned implementation
was edited. No commit, push or shared status mutation was performed by A13.
