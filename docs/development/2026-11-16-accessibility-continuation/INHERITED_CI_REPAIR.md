# Inherited hosted failure repair

Starting source `0865bc1584e4bda569fe2ccacfac87b842b8d906` passes all220 local Release tests, but hosted results contain11 successful and2 failed jobs. Original decoded logs are retained compressed under `reports/baseline-hosted-*`; timestamps and source IDs remain intact. The Windows text log is normalized toLF and explicitly hashed as normalized text, rather than represented as raw HTTP bytes.

## Sanitizer workflow

The required native sanitizer inventory contains25 distinct tests/build inputs after the manual-key fixture was added. The workflow still asserted24 at five gates, so it failed before configuration. Update each fixed expected count and corresponding prose to25. No test is removed, no sanitizer policy changes, and all25 IDs remain required. Local structural inspection confirms25 unique tests and25 unique build targets. Hosted execution at repaired source is still required.

## Relocated converter import

Windows core fails the installed converter with `ModuleNotFoundError: contact_grid_conversion`, after its source/build tree has been deleted and its prefix relocated. The previous CLI workaround removes an empty working-directory search entry but assumes Python retained a useful script-directory entry. Add the executable's resolved `__file__` parent explicitly after sanitizing empty entries. Imported-library mode does not mutate search paths. Numerical conversion code, thresholds and wire format remain unchanged.

The independent existing install suite now also runs an isolated bootstrap with no automatic script-directory entry and decoy modules in the foreign working directory. Original source fails at the same sibling import; repaired source passes with byte-identical certificates relative to the same-source uninstalled command and an unchanged installed payload. This reproduces a missing-search-path mechanism; the exact reason for Windows startup's path omission is not asserted from the log alone.

Four affected local suites pass (`install`, `adversarial`, `cli`, `resources`) in3.35s CTest elapsed. Source hashes and original failure/pass logs are retained in `reports/inherited-*`. The next Windows hosted observation is required before claiming a platform repair pass.
