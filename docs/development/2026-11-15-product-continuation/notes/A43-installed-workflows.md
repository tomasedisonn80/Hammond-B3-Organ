# A43 — Installed native calibration workflow

Owner: `/root/w08_a43_installed_workflows`. Base source:
`d556da017ea0a5d4f2d231416782dbc5066e58c2`.

Appended `MIDI_EXPRESSION_GUIDE.md` after the existing Standalone metadata,
preserving prior copy order, configuration selection, COPY-only behavior and
strict preflight. The guide receives configured-byte hashing, configure
dependency tracking and ordinary/nonempty input checks. Inventory is now
**16 files MIDI-OFF / 20 MIDI-ON**. No additional contracts, repository trees or
PDFs are copied. Existing application/dependency inputs remain unchanged.

`STANDALONE_INSTALL.md` now gives installed physical-port/calibration commands,
PowerShell paths, volatile calibration versus saved musical expression, a
self-contained 800 ms synthetic example and precise component/link boundaries.
OfflineTools remains 23 files; CrossoverTools remains six files and explicit.
Root additionally authorized only the hosted `standalone.yml` inventory entry
and its 16/20 count assertion; all sanitizer selection/instrumentation is intact.

## Executed verification

Linux x86_64, Python **3.12.14**, CMake **4.4.5**. Used the configured Release,
MIDI-OFF `HAMMOND_*` inputs from `build-native/CTestTestfile.cmake`; ran
`python3 apps/standalone/native_tests/test_standalone_install.py -v` with these
six `StandaloneInstallTests` methods explicitly selected:

- `test_configured_capabilities_identify_exact_payload`
- `test_preflight_rejects_private_bad_inputs_before_any_destination_write`
- `test_disabled_midi_inventory_requires_no_rtmidi_input_or_sdk_lookup`
- `test_reference_capability_and_midi_records_reject_nonregular_inputs`
- `test_destination_ancestors_remain_ordinary_directories`
- `test_custom_directories_copy_mode_and_disabled_component`

**6/6 passed in 4.379 s.** Private relocation removes source/build/dependency
copies, checks installed guide links, obtains expression **0.75** with the
documented calibration, admits no native MIDI callbacks and preserves every
installed byte plus four Offline/Crossover namespace sentinels. These sentinels
test preservation, not other components' native execution. Shared build/install
manifests were not written. Read-only app SHA-256:
`7ded143b676e9d51a29549dae12184763042a1f12192f72802db7927fa707852`.

Hosted-stage Python parses; both expected inventories exactly match the fixture.
Checked 38 installed relative links, 113 existing repository targets and 11
external notice links. The first ad-hoc audit misclassified external notices as
repository links; corrected classification passed without a product change.
`git diff --check` passes.

Root next: reconfigure, then run
`ctest --test-dir ../build-native -C Release --output-on-failure --no-tests=error -R '^test_standalone_install$'`
from the repository. This includes the two actual-build install methods withheld
here to preserve exclusive shared-build ownership. MIDI-ON/platform runtime,
physical devices and PowerShell execution remain unrun locally.

## Integrator gate

Root reconfigured the owned build after guide freeze and executed the complete
`test_standalone_install` CTest: **eight methods passed in 5.207 s; 1/1 CTest
passed in 5.31 s**. The retained `reports/A43-root-installed-ctest.txt` includes
the actual sixteen-file MIDI-OFF installed smoke. Hosted 16/20 inventories remain
a separate source-specific gate.
