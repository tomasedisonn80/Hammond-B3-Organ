# Starter registration data admission

A24, `/root/w04_a24`, wave 4, 16 November 2026. **Accepted within the
payload, canonicalization and offline recall scope below.** No discrepancy or
data correction was found. These twelve recipes remain original proposed
software settings with `proposed-unmeasured` evidence status.

## Independent expectation and observed result

Root authored the fully expanded literal manifest before A16's generator;
[A16's retained note](../development/2026-11-16-preset-library-continuation/notes/A16.md)
explicitly records that the generator author never read or consumed it. A24's
[new suite](../../tests/test_starter_registration_oracle.py) independently
transcribes all defaults and overrides from the
[frozen contract](../STARTER_REGISTRATION_PACK_CONTRACT.md), checks the contract's
twelve table rows, and validates the JSON's exact fields, types and array order.
A24 did not read the generator's musical implementation.

Every musical comparison uses `hammond_registration inspect` output after the
actual native parser and serializer. It checks all 36 drawbar positions, both
remembered banks, both routes, both fixed modes, both pedals, expression and all
four percussion values against literal JSON. This includes retained banks and
cancelled fixed/percussion memory. Generated output supplies reproducibility
evidence; the independent contract/manifest supply musical expectations.

Final execution: **8 methods, 122 actual native subprocess invocations, all
passed in 0.494 seconds**: 84 inspections, 36 materializations, one list and one
generator invocation. The preliminary run also passed; final tightening checks
literal array types and exact single-space canonical lines.

| Boundary | Observation |
| --- | --- |
| Flat inventory | Exactly 24 regular, nonsymlink payloads; exact numbered stems, paired suffixes and native Registration/Performance ordering; zero metadata or extra objects inside `entries/`. |
| Native state | Every original and regenerated payload matches every literal field, the frozen catalog, 81-token/12-line state4 layout and canonical bytes including final LF. All twelve pairs have identical bytes. |
| Registration recall | All twelve recipes materialized twice, with explicitly supplied current expression **0.125** and **0.875**. Reinspection preserves each supplied value and restores every other field from its recipe. Input files remain unchanged. |
| Performance recall | All twelve materializations restore saved expression and every retained field; resulting bytes equal the source Performance payload. |
| Regeneration | Fresh temporary destination contains exactly the checked-in names and bytes; every regenerated payload independently passes native/manifest inspection. Source manifest and all payload bytes remain unchanged. |

## Reproduction and identities

Cwd: `/workspace/scratch/3edffb787db3/Hammond-B3-Organ`. Inputs are the working
overlay on `54df95fe343d417dd89bb7a91f85e4f51c08dfe7`, base tree
`b221dc8b565f5da04c7ad1fabc1d4d605f27b97e`. Used root's existing Linux Ninja
Release/GNU 14.2.0 build; no configure or native build was run by A24.

```sh
env HAMMOND_REGISTRATION_EXECUTABLE=../build-native/hammond_registration HAMMOND_STARTER_GENERATOR_EXECUTABLE=../build-native/hammond_generate_starter_registrations HAMMOND_SOURCE_DIR=. python3 -B tests/test_starter_registration_oracle.py -v
git diff --check
git diff --exit-code 54df95fe343d417dd89bb7a91f85e4f51c08dfe7 -- include src data/parameter-registry.json data/references/parameter-registry-v2.json data/registrations/atlas-chapel-nominal-v1.json docs/CONTROL_STATE_FORMAT.md plugins/vst3/PluginIds.h
```

Both diff commands pass. SHA-256 identities:

| Input | SHA-256 |
| --- | --- |
| Frozen pack contract | `f6390633160dc0dc643344fa6316fb26b3376216e535eb7d1b976f1f2dcffbf2` |
| Literal `recipes.json` | `665e6098928d845c1302642f89a109dc8f2be8500f9eb49d33111ba37d468051` |
| Independent test | `66288788616bab537d7938ecf24aadd32833373024d2c0b4691d79e5304fd478` |
| Generator source | `dd93af18acd911cc6f0420314d0811c34adaaddf496e86e9df120f3576382e91` |
| CLI source | `4fbf8f9e9a8c04713ee7aa28e089e02dbd5955ceb38e478673aa1f5da2f37ff3` |
| Native generator | `7cbe11d52810f2d0d7c23c25ed35178740975b65e9c621e6825b74aa4bf97dff` |
| Native CLI | `872a343f20eb6710e6867fc4d1c0fe0b95118b883de21035ee70774f8762e13f` |
| Combined 24 payloads | `8618b545b1c04bdf1370478259967125cb63b09a81bbb6748f6990788578de11` |

Combined payload hashing concatenates, in ascending filename order, each ASCII
basename, one NUL byte and its complete raw payload bytes, into one SHA-256.

## Bounded compatibility argument

The diff above is empty. A separate raw-byte comparison with `git show` at the
base verified these twelve files; each current SHA-256 equals its base SHA-256:

| File | SHA-256 |
| --- | --- |
| `include/hammond/ControlStateIO.h` | `7e96c7b27906f7dfe0b9e8337888d5305fc4610f5009301b42cfae563e3ab081` |
| `src/ControlStateIO.cpp` | `3a95b6750fc615b7218da5dd9cb540b30d8a83984374d441f2754c7e66de34fb` |
| `include/hammond/ControlState.h` | `aab82b082f9cf77dadf763148cade9eae04f6f7df68b302b1832f21f78034856` |
| `src/ControlState.cpp` | `9026aa0338b905a005912e4c7734eedd36cbf204ae43fa4631bdc5aadaa86a5d` |
| `include/hammond/ParameterBridge.h` | `cd313711737f94e5f7f7b0dd73851347b9c4e53b3962d5d40d7e7c37883293d3` |
| `src/ParameterBridge.cpp` | `296c674ef39d54751f662293b4ce4b07f602bb407349981f8b03e1b5a4757220` |
| `data/parameter-registry.json` | `aedaa09e47fc2baba4a08484cce84916f2a27edac55d45f03f167f41c84bd6e2` |
| `include/hammond/FixedRegistration.h` | `4548240ce25f5200442bfe4607ba755feee822a91c8b1a97af9bf7837e3634a0` |
| `src/FixedRegistration.cpp` | `690e45e5738c3c25ae1082e31a49debdfbca994b68d6b0a28ef865df7991769d` |
| `data/registrations/atlas-chapel-nominal-v1.json` | `c9f1dd2d4287448325834f66f3998f4c32a41f84bc7ec7216e7b72ebcbf722cf` |
| `docs/CONTROL_STATE_FORMAT.md` | `3919a828acc343d83e765111f67ac14d06d6ceba3b5407bb6dc4d36a81e3152a` |
| `plugins/vst3/PluginIds.h` | `2bc93839216f52d5920046931d83ba14fd2d01e15fdbdd477b71b15ebb8415fc` |

The registry contains exactly 47 distinct parameter IDs. Source inspection
retains the state4 writer and explicit readers 1–3. This is a source-preservation
argument plus tested state4 entry paths; it does not recertify historical
migrations or hosts on every platform.

## Limits and next integration

Windows/macOS, copy-only installation, exact-pack musical auditions, live browser
recall, device behavior and physical fidelity were not executed here. A21's
separate renderer admission retains its own audio fixtures and identities.
Hidden state is checked through native serialization here; audible later bank
selection and cancelled-manual return need their audio acceptance. No factory,
artist, measured-instrument, expression-circuit or whole-interface claim follows.
Root owns CMake registration, coherent gates, installation, publication and
remaining pack delivery. No production/data files, native build or commits were
changed by A24.
