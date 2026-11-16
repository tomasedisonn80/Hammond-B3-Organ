# Registration installation and documentation admission — A35

16 November 2026; actual worker `/root/w06_a35`, wave 6. Base HEAD
`54df95fe343d417dd89bb7a91f85e4f51c08dfe7`; reviewed additions were uncommitted.
**Admitted for the observed Linux installation and compatible-host relocation
scope. No production blocker found.** Root corrected the one stale guide
qualification statement identified below. This review does not extend the
observed platform, runtime or product boundaries.

## Installer and inventory

Inspection of [the module](../../cmake/InstallRegistrationTools.cmake), shared
directory validator and root wiring confirms every new preflight/copy rule has
both its explicit component and `EXCLUDE_FROM_ALL`. Ordinary installation and
unrelated components do not select these rules. The two components are independent
and may share a prefix in either order.

| Component | Exact default inventory |
| --- | --- |
| `RegistrationTools` | `bin/hammond_registration` and `share/hammond/REGISTRATION_GUIDE.md`: 2 files |
| `StarterRegistrations` | `share/hammond/registrations/starter-v1/`: the fixed 12 numbered stems, each in `.b3registration` and `.b3performance`, plus `README.md` and `recipes.json`: 26 files |

The 24 names are literal installer inputs; neither globbing nor recursive copying
can introduce unlisted siblings. Metadata stays outside flat `entries/`.
`PROGRAMS` copies the selected binary without target installation's RPATH/strip
processing. Neither component invokes a generator, parser, Python, renderer,
native executable or build. The installed tool itself is invoked only afterward
by explicit use/tests.

Preflight requires every selected input to exist, be nonempty/readable and neither
a directory nor symlink, rejects symlink source ancestors, and admits destination absence and ordinary
ancestors before the first copy. Existing executable/guide targets or starter
package refuse, including dangling links; packages are never merged. COPY/unset
mode is required. Destination checks include the effective `DESTDIR` prefix;
system ancestors outside that prefix remain trusted. Hashing checks readability,
not a signed manifest. Sequential copying is neither a race-free transaction nor
rollback: later failure may retain partial output, which then blocks reinstall.

The shared validator rejects empty/absolute/drive-qualified directories, parent
traversal and list separators; relative custom directories, backslash normalization
and `.` are supported. The multi-config guard rejects unknown configurations
before target-dependent rules could leave a guide-only success.

## Inspected execution evidence

I did not rerun the suite, configure or build. The retained
[final gate log](../development/2026-11-16-preset-library-continuation/reports/w05-final-tests.log.gz)
records the installer CTest passing in 2.02 seconds. Its then-current
`../build-native/Testing/Temporary/LastTest.log` explicitly records **10 methods,
208 subprocesses, 1.899 seconds, OK, no skips**. All method outcomes were read.

The [suite source](../../tests/test_registration_install.py) exercises exact
component inventories/exclusion, every missing/empty input, symlinks/collisions,
COPY/strip preservation, custom-directory reconfiguration, POSIX `DESTDIR` and
Ninja Multi-Config. Its copied root install script removes all private source/build
inputs after relocation, then lists, inspects and materializes all 24 entries
from an unrelated cwd, checking Registration expression preservation and
Performance restoration. The genuine checkout/build are watched for mutation.
The deterministic POSIX 457-byte file-size limit permits the first pair, fails
the larger third copy, and checks retained partial output plus unchanged
reinstall refusal. These are inspected root-run results, not new A35 runs.

I independently enumerated `../registration-moved`: **28 files, no symlinks,
every size and SHA-256 equal** to the retained
[actual two-component install/rename/list receipt](../development/2026-11-16-preset-library-continuation/reports/w05-actual-install.json).
That receipt records actual `cmake --install` calls and relocated native list;
private-input removal belongs to the separate suite above.

One additional native invocation used installed `inspect --library ABSOLUTE_ENTRIES
--key '02 Warm Comp.b3registration'` from `/tmp/a35-registration-use-pe97eo35`,
with only `LC_ALL=C` and a nonexistent `PATH`, bounded by 10 seconds. It returned
exit 0, one JSON line, empty stderr, 24 valid catalog entries and canonical
expression `0.625`. Cwd remained empty and every installed hash stayed unchanged.
Stdout SHA-256: `74284781b66376319a7419347c094879a4b12c1ed504642a227dfbbdb732a0f3`.
The temporary directory was removed afterward.

## Documentation and dependency limits

All **26 relative README links** resolve within the installed pack after URL
decoding. Its five absolute GitHub links require network/published source;
their remote availability was not checked and they are not bundled documents.
The guide itself is separately installed. The README accurately distinguishes
proposed, unmeasured recipes, explicit import, scope semantics and absent live
browser/physical acceptance.

Finding A35-D1: the original guide still called installation qualification
pending. Root corrected only that verification paragraph to recognize the actual
installation and ten-method gate while retaining clean no-SDL build and foreign
platform execution as pending. The original installed guide/receipt are preserved;
the refreshed source guide has different bytes and is not a newly installed artifact.

CMake 3.21+, Python 3.10+ and C++20 are source-build requirements. The native CLI
links static project support/core; SDL is gated by the optional native application.
For the observed Linux x86-64/glibc 2.41 executable, `readelf` finds no RPATH/RUNPATH,
but requires `libstdc++.so.6`, `libm.so.6`, `libgcc_s.so.1`, `libc.so.6` and
`/lib64/ld-linux-x86-64.so.2`. No Python/display/profile was needed for the bounded
installed inspection. Runtime libraries, renderer and profile are not bundled.
This does not establish arbitrary Linux ABI portability, Windows/macOS execution,
signed distribution, device/host acceptance or physical fidelity.

## Reviewed SHA-256 identities

Paths are repository-relative unless explicitly prefixed `../`; report basenames
refer to this session's `reports/`. The actual-install receipt holds all 28
installed per-file identities.

| Input | SHA-256 |
| --- | --- |
| `CMakeLists.txt` | `87f5905c34c3dafcd6a113f9d362d5e135c5777751a1364370652b8fcfaf0313` |
| `cmake/InstallHammondTools.cmake` | `97cb6ec2c7073e3c50a1b00106317ddd726a2fb01e580dc96b55be0044140355` |
| `cmake/InstallRegistrationTools.cmake` | `9f77bf59750bc4e3850e2aaa9712fec2ee5769b54c4e2b20fb60959d77714274` |
| `tests/test_registration_install.py` | `0fc305b1fff1b89de670c336f544ff0314d88a788256ce9ff1d7917786946219` |
| `apps/standalone/CMakeLists.txt` | `f27d7098ec62c8084f5274a0308393b35e9a19a34ecc360c03bfb03a857c8d20` |
| Original installed guide | `c0916192a8291efebd28b54b952d722581a70358f6c4b998abc0d1b7b73ca478` |
| Refreshed `docs/REGISTRATION_GUIDE.md` | `a56262693e192da3e2d22e5a2f3856f35e0ee3fb080c7913215f40303bd3ceda` |
| Pack `README.md` | `b5353cf54e5aeb259e2ab16735a2449385144e013bc736c38623c64162f45234` |
| Pack `recipes.json` | `665e6098928d845c1302642f89a109dc8f2be8500f9eb49d33111ba37d468051` |
| `w05-actual-install.json` | `079edb0a0ee80e6070a2782e0f9a3a249749568c79ac6e821a13add2d2fd0cde` |
| `w05-final-tests.log.gz` | `5741aeddc160c8071a24cd5a525250ab4f0ffe2187dd13c589cccf093f7182d8` |
| Observed `../build-native/Testing/Temporary/LastTest.log` | `b52e192448aa748da22c2be5f1c249d11e78974677ee40c4d5fa3589e4b03140` |
| `../build-native/cmake_install.cmake` | `fc0a7b519984a60bd70ea2c2bf02f75a00f8d1f9919db2500f21827de1832137` |
| Installed executable, 253,280 bytes | `872a343f20eb6710e6867fc4d1c0fe0b95118b883de21035ee70774f8762e13f` |
