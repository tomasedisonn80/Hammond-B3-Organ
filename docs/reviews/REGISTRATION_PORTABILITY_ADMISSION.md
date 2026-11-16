# Registration portability source admission

16 November 2026; A29, wave 5. Base HEAD:
`54df95fe343d417dd89bb7a91f85e4f51c08dfe7`; writable checkout
`/workspace/scratch/3edffb787db3/Hammond-B3-Organ`.

**Result:** the reviewed source is admissible after the narrowly scoped fixture
repairs below and root's generator-only MSVC encoding option. This is source
review plus Linux execution, **not Windows, MinGW or macOS qualification**.
The [CLI](../REGISTRATION_CLI_CONTRACT.md),
[renderer](../REGISTRATION_RENDER_CONTRACT.md),
[pack](../STARTER_REGISTRATION_PACK_CONTRACT.md) and
[operator guide](../REGISTRATION_GUIDE.md) retain their acceptance boundaries.

## Findings and repairs

1. The CLI author test skipped case ambiguity only on Windows, assuming every
   other volume could store both `Same.b3registration` and `same.b3registration`.
   It now checks `Path.samefile` on those exact fixtures and explicitly skips
   only when the volume aliases them. Distinct-file volumes retain both original
   ambiguity assertions. The native storage fixture already checks capability.
2. Three POSIX tests created invalid UTF-8 filenames without admitting filesystem
   capability. Apple's [APFS filename documentation](https://developer.apple.com/library/archive/documentation/FileManagement/Conceptual/APFS_Guide/FAQ/FAQ.html)
   states that creation requires valid UTF-8. Root authorized local handling in
   the CLI author/admission and renderer author suites: only `EILSEQ`/`EINVAL`
   from the exact fixture creation cause an explicit skip. Other failures
   propagate; malformed argv tests remain active. No production guard changed.
3. The generator's compiled source-root narrow literal feeds an explicitly UTF-8
   path converter. MSVC's default [execution character set](https://learn.microsoft.com/en-us/cpp/preprocessor/execution-character-set)
   need not be UTF-8. Root added generator-only `/utf-8`; the reviewed CMake
   contains that amendment. A Windows Unicode checkout still needs execution.

## Transport, I/O and path review

`registration.cpp` uses its own Windows adapter, preserving JSON usage failures.
Its 4,096-unit preliminary check precedes conversion to `int`; strict
`WideCharToMultiByte` results enforce 4,096 UTF-8 bytes per token, 16,384 total
and twelve arguments. Common parsing rejects ASCII controls and malformed UTF-8.
Native path hex preserves POSIX bytes or unsigned UTF-16 units in low-byte-first
order; it does not depend on an ANSI code page. Diagnostics receive bounded UTF-8
repair. No unchecked signed read count reaches an unsigned byte accumulator.

The shared reader rejects device/pipe/native Windows namespaces before opening,
then checks disk type and directory/reparse attributes on the opened handle.
POSIX uses no-follow, nonblocking and close-on-exec flags plus `fstat`.
Negative sizes/read counts are handled before conversion; both branches bound
growth detection to 16,385 bytes and report close failure. Parsing and canonical
serialization complete before replacing the entire caller destination. Leaf
links remain rejected while directory aliases may resolve normally.

CLI and generator set Windows stdout to binary, check write/flush results, and
ignore POSIX SIGPIPE so report failure returns exit 5. The generator's shared
Windows argv wrapper intentionally retains its existing stderr failure path;
it is not substituted for the CLI's JSON adapter. CMake links the common reader
and headless support without SDL, and supplies `-municode` to both new MinGW
entry points. The ordinary Python suites remain standard-library-only.

The storage component proof preserves uncertain Unicode refusal, existing-path
identity and equivalent-ancestor/suffix checks. CLI protects invocation and
resolved-parent/unchanged-leaf source paths and revalidates complete snapshots.
No Unicode case/normalization guess, alias exemption or overwrite path was added.

## Installer and fixture boundary

The current installer checks source ancestors only through the explicit source
root and destination ancestors through the effective prefix. Thus a `/var` or
`/tmp` alias outside that boundary is not rejected merely for being a system
ancestor; a linked source root, effective prefix or descendant remains refused.
Its test workspace resolves temporary paths. Configuration-specific target
expressions, explicit unknown-configuration refusal and Unicode directory fixtures
are present. Both components remain optional copy-only installations, using a
literal payload inventory and preflight before copying.

Eight Linux CMake 3.31.6 `-P` checks executed only the extracted current preflight
functions: outside source/destination aliases admitted; linked source root,
source descendant, source leaf, effective prefix and destination descendant
refused; existing hard-link destination refused. The admitted destination stayed
absent and source bytes remained exact. No configure, build or installation was
run by A29; root's complete installer gate has separate evidence.

## Executed checks and limits

From the checkout above, Python 3.12.14 invoked each file with `python3 -B FILE -v`.
`HAMMOND_REGISTRATION_EXECUTABLE`, `HAMMOND_RENDER_EXECUTABLE` and
`HAMMOND_TEST_PROFILE` named the corresponding files in `../build-native`.

| Suite | Methods / native invocations | Result / unittest time |
| --- | --- | --- |
| `tests/test_registration_cli.py` | 14 / 76 | Pass, no skips / 0.242 s |
| `tests/test_registration_cli_admission.py` | 10 / 46 | Pass, no skips / 0.164 s |
| `tests/test_render_controls.py` | 18 / 109 | Pass, no skips / 1.031 s |

Inputs were unchanged across these runs:

| Input | SHA-256 |
| --- | --- |
| `hammond_registration` | `872a343f20eb6710e6867fc4d1c0fe0b95118b883de21035ee70774f8762e13f` |
| `hammond_render` | `671375f6f9d393295bca148bcb546a1eb387dd865e994e755f16933389a16263` |
| `nominal.b3p` | `b36b0773fa06aac3ee267362f97ce798d0c1f41695e666f71c4a8a52ae36389f` |

Windows/MSVC/MinGW and AppleClang execution, malformed UTF-16 process arguments,
Windows reparse/device handles, actual APFS capability skips, forced close/mode
failures and cross-platform installation remain unobserved here. Linux success
does not close those gates.

## Exact inspected source snapshot

Full repository-relative paths identify the reviewed bytes; platform-specific
branches were inspected, not compiled on their target platforms.

| Source | SHA-256 |
| --- | --- |
| `AGENTS.md` | `1d2420d1bebdcddbe4bf0cc3ba5a8f08176d5c0a8b43e0aa6f454a83df564142` |
| `docs/REGISTRATION_CLI_CONTRACT.md` | `cab55c11a1f211e47e73b18db5f5f33cfd5b3fa2d066361f0842c9ea3b0041fa` |
| `docs/REGISTRATION_RENDER_CONTRACT.md` | `cd81f83ef069215044117c139d318fe49caeffb1bd30bd038eaf62dc9528fc57` |
| `docs/STARTER_REGISTRATION_PACK_CONTRACT.md` | `f6390633160dc0dc643344fa6316fb26b3376216e535eb7d1b976f1f2dcffbf2` |
| `docs/REGISTRATION_GUIDE.md` | `c0916192a8291efebd28b54b952d722581a70358f6c4b998abc0d1b7b73ca478` |
| `tools/ControlFileInput.h` | `74fe88ed36c8b00b56f3a3f15874f22ec418ce4ea8932995c7829b68c4f02ade` |
| `tools/ControlFileInput.cpp` | `0a174b171dfb3f0253cd6beb12707fda4da5ffb88c898727fb80ca111049cf5d` |
| `tools/registration.cpp` | `4fbf8f9e9a8c04713ee7aa28e089e02dbd5955ceb38e478673aa1f5da2f37ff3` |
| `tools/generate_starter_registrations.cpp` | `dd93af18acd911cc6f0420314d0811c34adaaddf496e86e9df120f3576382e91` |
| `tools/CliArguments.h` | `8ac5d91ebf66c31456159f028bce3c1c4b0dcd0c09118ac8c8d55c53a8912a47` |
| `tools/render.cpp` | `eee9b565f0ca2ca1e780ba6cd8bd118967728f2246b0023f609da89408739928` |
| `CMakeLists.txt` | `87f5905c34c3dafcd6a113f9d362d5e135c5777751a1364370652b8fcfaf0313` |
| `apps/standalone/CMakeLists.txt` | `f27d7098ec62c8084f5274a0308393b35e9a19a34ecc360c03bfb03a857c8d20` |
| `cmake/InstallRegistrationTools.cmake` | `9f77bf59750bc4e3850e2aaa9712fec2ee5769b54c4e2b20fb60959d77714274` |
| `apps/standalone/RegistrationLibrary.cpp` | `e45fd2671558e0725468c18b59dc5ef8e7436600910633f73035ce81da4d3a4a` |
| `tests/test_control_file_input.cpp` | `ed1df67d1d95f597113139bbefab2b92488b990e2171a86cb309d53227957642` |
| `apps/standalone/tests/test_standalone_registration_library.cpp` | `841f21c17f6fab449e8ce8ac345cf5af17257a17f5266afe6ffd372708f204cc` |
| `tests/test_registration_cli.py` | `0e2ba105dc464edc7044f03533ed24abf02da7c39e2c75fed549935e56cc0466` |
| `tests/test_registration_cli_admission.py` | `4744251a68772fe171ed1ab3ec1105ffbe32c89061e6da9a7fc3de322dcf8afe` |
| `tests/test_render_controls.py` | `bd6665e140bc0406b6e2b34d1d5f5c5148c7fe2af7640d9cbcd4a7a32becd4ce` |
| `tests/test_render_controls_admission.py` | `337c2396bddf564f38ac682ac1361ef7d50282385a5dc0d7179f9c99384cc411` |
| `tests/test_starter_registration_generator.py` | `2d3847985e6673f9c3cfc294fb586a36248cb59c233af649d6f52211228890c3` |
| `tests/test_starter_registration_oracle.py` | `66288788616bab537d7938ecf24aadd32833373024d2c0b4691d79e5304fd478` |
| `tests/test_registration_install.py` | `0fc305b1fff1b89de670c336f544ff0314d88a788256ce9ff1d7917786946219` |
