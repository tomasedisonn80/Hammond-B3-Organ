# A52 — primary VST3 hosted and compatibility audit

Actual worker `/root/w09_a52_vst3_hosted`, wave 9. Read the complete AGENTS and
M0–M9 plan, current session/checkpoint/assignments, recovery records and A29
compatibility review. Owned this note, `docs/reviews/PRODUCT_VST3_HOSTED_REVIEW.md`
and bounded A52 reports. No production/workflow/shared-status edits, local
builds/tests, commits or publication.

Independently fetched run **43668397341**, its three jobs, primary decoded logs,
commit/main identities and six artifact records. Published source is
**`d8c39f7986746eacc991747153c7dbb012bb9a32`**, tree
`edf67b978f93e8dbea6537ce92d3928c171bc1f3`, parent
`d556da017ea0a5d4f2d231416782dbc5066e58c2`. All jobs succeed: Linux GCC 13.3
**8/8 in 4.24 s**; macOS ARM64 AppleClang 17 **7/7 in 4.09 s**; Windows x64
MSVC 19.44 **7/7 in 7.05 s**. Every plugin validator passes **47/47**; every
separate build-time SDK selftest passes **51/51**. Verified SDK 3.8.1 root and
four submodule commits, license/embedded-JSON admission and toolchain identities.

Native ABI checks actual factory UUIDs, all 47 descriptors, historical state
migrations and preset/state paths. Each relocated bundle passes the ABI gate;
inventory is Linux four files, macOS six and Windows six. Retained module hashes,
upload IDs/digests and whole decoded-log hashes with 227 bounded original lines.
Artifact archives were not downloaded; inner tar hashes were not independently
recomputed. macOS signing is ad-hoc and ARM64 qualification only.

Read-only Git/blob comparisons from this checkout confirm all 20 VST3 files,
54 core/header files and 30 authoring-data files unchanged since A29's
`ff41d412`. Inspected all 15 later non-documentary changes. Independently matched
47 literal C++ descriptors to registry metadata; state4/readers1–3, factory IDs,
documentary fixed catalog and selectors remain unchanged. Native endpoint/
inversion and CC120/121 stay outside VST3 mapping and saved musical state.

No compatibility defect found. Validator explicitly reports no MIDI Mapping,
MIDI Learn, program list or 64-bit processing. Linux alone executes calibrated
calling-thread C++ allocation interposition; its timings are not device deadlines.
DAW/device/accessibility/fidelity/signed-release gates remain open. Later A46/A48
and final source need their own hosted gate. Scoped JSON, link, whitespace and
evidence-consistency checks passed; no runtime result is attributed to A52.
