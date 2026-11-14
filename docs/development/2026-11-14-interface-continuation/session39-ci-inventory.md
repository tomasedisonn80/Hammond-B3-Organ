# A39 — Standalone CI inventory

Actual worker `/root/w07_a39_ci_inventory`, assignment **39/60**, logical wave
**7**. Baseline `aea58bb85bc66a5feaff66a0b8a388e7c3f9e630`, tree
`19e61b344fc8dfd3146588a6058994ff351d2cc5`; A34/A36 remain separately identified
working changes. Root owns builds, integration, shared status, staging and
publication.

**Completed:** added exactly `test_standalone_workspace_raster`,
`test_standalone_workspace_continuity` and `test_standalone_scaled_view` to
`.github/workflows/standalone.yml`'s required-name guard. No execution filter,
timeout, package, metadata loop or artifact behavior changed. Final workflow
SHA-256 is `527d1cdb692cd5d837f0436ee68b2026878b10c5db1553459ca623060e4c1d34`;
root received this freeze before SDK-free/sanitizer qualification.

The [review](../../reviews/INTERFACE_CI_INVENTORY.md) explains the scope and
reproduction. [Inventory JSON](reports/a39-ci-inventory.json) retains all three
workflow identities, parsed matrices, CMake/install mappings, exact package names,
guide and license identities, and preserved gates. [CTest discovery](reports/a39-ctest-discovery.json)
records the actual command, complete names and selected commands/properties.

| Observed check | Outcome |
| --- | --- |
| Native CTest `--show-only=json-v1` | 147 configured; 38 standalone; 21 required present; no duplicates. |
| YAML / embedded Python / shell syntax | Three workflows; eight Python blocks; 28 run blocks parse. |
| Independent package declarations | Exact 15 common / 19 enabled files agree. |
| Guides, notices and licenses | Seven required prose sources present; all three locked license identities match. |
| Workflow diff | Only the three required names were added; whitespace check passes. |

No configure, build, application/test execution, installation, hosted dispatch,
index update or commit was performed. Configured names do not establish build
readiness or test success. A24's 19-file and A29's separately built 15-file
runtime qualifications remain historical source-specific evidence. The eleven
hosted passes at `5d81199` do not qualify `aea58`, this workflow edit or A34/A36.
A48/A58 should observe the subsequently published exact revision. Physical
devices, native accessibility, deadlines, measured sound, reference equality and
signed release remain open under the complete M0–M9 plan.
