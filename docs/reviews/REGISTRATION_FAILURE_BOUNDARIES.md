# Registration operational failure boundaries — A30

16 November 2026; independent wave-five review at base HEAD
`54df95fe343d417dd89bb7a91f85e4f51c08dfe7`, with the reviewed additions uncommitted.
Scope: CLI publication/reporting, shared input, generator and explicit installer.
Read the [contract](../REGISTRATION_CLI_CONTRACT.md),
[implementation admission](REGISTRATION_CLI_IMPLEMENTATION.md),
[path admission](REGISTRATION_PATH_ADMISSION.md) and current source.
**No required production correction found.** One approved installer regression
adds observed late-copy evidence; other exceptional branches below are source
arguments, not newly injected CLI outcomes.

## Publication and reporting

`registration.cpp::execute` sets `committed` to unknown immediately before the
writer and records `saved.committed()` immediately on return, before transferring
the save report or formatting its outcome. This preserves the following distinctions:

| Boundary | Result retained |
| --- | --- |
| Ordinary writer refusal | `committed: false`; admission exit 3 or filesystem exit 4 |
| Publication followed by failed cleanup/catalog refresh | `SavedWithWarning`, `committed: true`, committed entry, actual refreshed-catalog status, exit 1 |
| Writer throws without returning its publication result | `InternalError`, `committed: null`, exit 70 |
| Report preparation throws after a returned save | Emergency envelope retains the known true/false value; exit 70 |
| Stdout write/flush fails | Exit 5 and bounded stderr warning; stdout may be incomplete and publication may already have occurred |

`save_registration_entry_new` performs no-replace publication before cleanup and
refresh. `Staging` removes only its temporary paths; it never removes the
published destination. The CLI neither retries the save nor converts failed
post-publication refresh into a false prepublication refusal. A caught authorizer
exception or denial returns `NotAuthorized` before publication. If allocation
while constructing that failure itself throws, the caller conservatively retains
unknown publication instead of inventing certainty.

The existing native store fixture deterministically exercises denied/throwing
authorization, a late exact-path competitor, retained foreign staging contents,
and refresh capacity overflow after authorization. Root's
[path qualification](../development/2026-11-16-preset-library-continuation/reports/w04-path-qualification.json)
ran that fixture at the unchanged test/source hashes. A30 inspected those seams;
it did not rerun them or inject their outcomes through the public CLI. Existing
CLI closed-pipe tests already cover refusals and committed warning-bearing
outputs. Emergency allocation/encoding failure and writer exceptions remain
**unexecuted CLI branches**, admitted here by the explicit state transitions.

## Inputs, authorization and resources

The CLI protects both invocation and resolved-parent/unchanged-leaf identities
for each supplied input and selected entry. Immediately before publication it
rereads both identities, compares full snapshots including Registration
expression, and repeats complete catalog/exact-key admission for materialization.
The captured canonical report survives ordinary authorization refusal. This
checks semantic equality after published migrations; it does not require identical
whitespace or source versions. The conservative alias checks remain mandatory.
Changes after final checks are outside the claimed guarantee; no lock or hostile
namespace race immunity is inferred.

`ControlFileInput` inspects the opened handle, bounds bytes at 16,384 plus one
growth-detection byte, checks close, and parses/serializes into a private candidate
before replacing the destination. POSIX interrupted open/stat/read calls retry;
close is deliberately not retried. Windows rejects special namespaces before
opening. Forced interrupted reads, late growth, close errors and allocation
failures were **not executed here**. Byte/catalog bounds do not establish an OS
I/O completion deadline.

The CLI reserves its 1-MiB report buffer before execution and bounds every append;
the emergency envelope uses a 512-byte stack buffer. Catalog limits remain 128
candidates/512 directory items, diagnostics 256 bytes, arguments 4,096 bytes each
and 16,384 total, resolved paths 8,192 native units. The generator has exactly 24
intents and 4,096-byte stack report lines. Its prior-entry rereads and directory
inventory are bounded by completed intents. Installer hashing/copying covers a
fixed inventory, but executable and metadata sizes have no registration-reader
16-KiB limit; no fixed installer memory or elapsed-time ceiling is claimed.

## Partial batches and installation

The generator records the current filename/attempt before entering the writer,
retains unknown for an escaping writer exception, increments the completed count
only after a returned committed result, and stops after any warning, refusal or
report failure. It never automatically retries or deletes completed files.
Existing deterministic generator RLIMIT and broken-pipe methods already cover
retained partial results; no duplicate test was added.

Installer preflight admits all required sources and destinations before its
first copy. Copying remains sequential and may leave new files after a later
failure; its pre-copy diagnostic says so. Root's
[actual two-component install/rename/list receipt](../development/2026-11-16-preset-library-continuation/reports/w05-actual-install.json)
is existing root-executed evidence, not an A30 run.

A30 proposed, received ownership for, and added
`test_late_copy_failure_retains_partial_package_and_refuses_reinstall` to the
installer suite. It copies the actual generated install script to private paths,
then imposes child-only POSIX `RLIMIT_FSIZE` equal to the first payload's 457
bytes, with `SIGXFSZ` ignored. Both first-pair payloads must remain byte-exact;
the larger third payload triggers nonzero copy failure. The test snapshots actual
residue without assuming whether CMake removes or retains the failed current
file, or prescribing its byte count. An unrestricted second invocation must
refuse the existing package before copying and leave that snapshot identical.
Windows and unavailable limit capabilities explicitly skip this method.

From `/workspace/scratch/3edffb787db3/Hammond-B3-Organ`, Python 3.12.14/CMake 3.31.6:

```sh
TMPDIR="$PWD" \
HAMMOND_TEST_CMAKE=/home/agent/.local/lib/python3.12/site-packages/cmake/data/bin/cmake \
HAMMOND_TEST_BUILD_DIR=/workspace/scratch/3edffb787db3/build-native \
HAMMOND_TEST_CONFIG=Release HAMMOND_TEST_CMAKE_GENERATOR=Ninja \
HAMMOND_TEST_CMAKE_MAKE_PROGRAM=/home/agent/.local/bin/ninja \
HAMMOND_INSTALL_BINDIR=bin HAMMOND_INSTALL_DATADIR=share \
HAMMOND_REGISTRATION_EXECUTABLE=/workspace/scratch/3edffb787db3/build-native/hammond_registration \
python3 -B tests/test_registration_install.py \
RegistrationInstallTests.test_late_copy_failure_retains_partial_package_and_refuses_reinstall -v
```

**Pass: 1 method, 3 subprocesses, 0.053 s.** The normal fixture performs one
root-approved private `LANGUAGES NONE` configure; no production configure/build
or native compilation occurred. Watched real source/build inputs remained
byte-identical. Root owns the expanded ten-method suite rerun. No batch atomicity,
power-failure durability, macOS/Windows fault execution or automatic recovery is
established by this review.

## Reviewed identities — SHA-256

| Input | SHA-256 |
| --- | --- |
| `tools/registration.cpp` | `4fbf8f9e9a8c04713ee7aa28e089e02dbd5955ceb38e478673aa1f5da2f37ff3` |
| `tools/ControlFileInput.cpp` | `0a174b171dfb3f0253cd6beb12707fda4da5ffb88c898727fb80ca111049cf5d` |
| `apps/standalone/RegistrationLibrary.cpp` | `e45fd2671558e0725468c18b59dc5ef8e7436600910633f73035ce81da4d3a4a` |
| `tools/generate_starter_registrations.cpp` | `dd93af18acd911cc6f0420314d0811c34adaaddf496e86e9df120f3576382e91` |
| `cmake/InstallRegistrationTools.cmake` | `9f77bf59750bc4e3850e2aaa9712fec2ee5769b54c4e2b20fb60959d77714274` |
| Updated `tests/test_registration_install.py` | `0fc305b1fff1b89de670c336f544ff0314d88a788256ce9ff1d7917786946219` |
| `../build-native/cmake_install.cmake` | `fc0a7b519984a60bd70ea2c2bf02f75a00f8d1f9919db2500f21827de1832137` |
| `../build-native/hammond_registration` | `872a343f20eb6710e6867fc4d1c0fe0b95118b883de21035ee70774f8762e13f` |
