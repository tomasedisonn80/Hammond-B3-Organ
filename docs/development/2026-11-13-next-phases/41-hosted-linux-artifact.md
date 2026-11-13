# Assignment 41 — hosted Linux package audit

Actual agent `/root/w07_a41_hosted_linux_artifact`, wave 7, assignment 41/60;
completed 2026-11-13. Owned only this note and [the hosted Linux artifact review](../../reviews/STANDALONE_HOSTED_LINUX_ARTIFACT.md). No production code, shared status/ledger, workflow or dependency files changed; root owns commits and publication.

## Goal and result

Independently inspect and run the **actual hosted package** for source `219821dfaca6bfee8ba0905993ed8deec7a66396`, tree `f2db7aee1d45a897273e4e68a2fefc6a2de4d433`. The result is PASS for the stated Linux x86-64 archive, source/notice/inventory, archived acceptance and relocated dummy execution checks. No newer locally built executable was substituted.

GitHub Actions [run 43517181978](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43517181978), attempt 1, Linux job `132202000441` succeeded. Authenticated metadata and actual downloaded bytes agree:

| Evidence | Identifier / SHA-256 |
| --- | --- |
| Package ZIP, 1,092,688 bytes | Artifact `14081326408`; `bd98ecaae92fe111df9bb2b40adae4b4358399ba11a6cdd2967d7e8502dcb9ed` |
| Diagnostics ZIP, 172,555 bytes | Artifact `14080619532`; `61e303fbef03848ce3d4fa24de168508cf289be17e7b222e94ffc857c1d47fd2` |
| TAR payload | `ae49f6e5ae7bf44831545f110478cfd7ef00e80bc949b337f81290b1b7577689` |
| Installed inventory | `87ce287e0f1088ebf6066953a20ad1e62e4d5a6535df9e664741afe89a7eece3` |
| Actual executable, 2,725,096 bytes | `dd5f14731e88035c8b35c2e57524dfadf5a741aabf307d3a1a799483ed1c7f61` |
| CI and independent BMP | `a774880df19f2efb9a3eb1534edfef5ad0f7a464cf0cefc900ec5cb6dbcf7097` |
| Independent smoke JSON | `045021753f313f4c8f1696b2752eefe23766b8e0a71fbb5252f458ca8fc163f7` |

## Work performed

1. Read repository agent instructions and the exact old revision's installation/workflow contract. Kept this acceptance separate from root's later frozen-source build and replay work.
2. Queried `github_fetch_workflow_run_artifacts`; downloaded both actual ZIPs through `github_download_workflow_artifact`; consumed returned file references without publishing temporary URLs. Confirmed API source commit, IDs, lengths and digests.
3. Validated ZIP entry types/paths/duplicates/encryption and expanded sizes before manual extraction; checked CRCs. Validated TAR root/types/paths/modes and harmless finite `mtime` metadata. No symlinks, hardlinks, special files or path overrides.
4. Confirmed exactly three package ZIP entries, 31 diagnostic entries, nine TAR files and five directories. Matched every file length/hash/mode and every directory mode against inventory, including post-run unchanged bytes/modes. Checked both `SHA256SUMS` entries.
5. Compared seven repository notice/data files with `git show <named-revision>:<path>` and SDL license with the pinned external SDL commit. Checked both manifest source TTF byte hashes/lengths, lock/manifest identities, acquisition/final verification logs and compiler/backend metadata. Compared staged, installed and package inventories plus provenance copies.
6. Parsed the actual CTest XML and read the full verbose test log. Identified 9 running cases, zero failures/disabled/skipped/error elements, 14.74-second CTest total; recorded meaningful method/callback counts and the internal POSIX state-file exclusion.
7. Moved the validated installed payload to a separate scratch directory; executed its `--help` and 600-ms smoke with explicit dummy audio/video, software renderer, an isolated environment and fresh private state/output paths. Checked actual return codes and all diagnostic assertions, then inspected the generated BMP.
8. Ran `file`, `readelf -h -l -d -V` and `ldd` on the hosted ELF. Recorded direct/optional runtime dependencies and symbol requirements; did not describe it as a wholly static executable.
9. Read actual run-job metadata. Linux build/tests/package succeeded; Windows/macOS **builds failed**, and their acceptance/package steps were skipped. Notified root to preserve that distinction when reporting the old run.

## Observed evidence

Hosted toolchain: Ubuntu 24.04 x86-64 image `20261111.370.1`, GCC/G++ 13.3.0, CMake/CTest 3.31.6, Python 3.12.16, SDL 2.32.10 commit `5d249570393f7a37e037abf22cd6012a4cc56a71`. Required X11/ALSA/PulseAudio/dummy backends compiled.

Archived acceptance includes install 3 Python methods, app 18 methods/164 processes, device 15 configurations/75 matrix callbacks/59,520 frames, calibrated C++ allocation 39 callbacks/936 positive allocation/free calibrations with zero production `new/delete`, Session/concurrency/UI/state coverage and replay helper coverage. The state test explicitly excludes deterministic POSIX failed replacement after a complete temporary write. This older application does not expose the later integrated replay CLI.

CI's relocated smoke recorded 59 callbacks/30,208 frames/14 images. The independently relocated exact ELF ran on Linux 6.18.57 x86-64/glibc 2.41 and produced 56 callbacks/28,672 frames/12 images at 48 kHz, 512 frames, float32 stereo, peak `0.08321372419595718`. Held/released input and screenshot while held were observed; all audio error counters, application errors and session faults were zero; shutdown joined and held state cleared. A single redundant shutdown command was discarded. Missing state remained missing. All package bytes/modes remained unchanged.

The independent 1,280×900 BMP is byte-identical to CI's archived image. Visual inspection confirmed expected drawbars, highlighted upper key, two manuals, pedals and dummy status. Dynamic dependencies are glibc/libm, libstdc++, libgcc_s and the ELF loader; maximum required symbol versions include GLIBC 2.38 and GLIBCXX 3.4.32. SDL's native backends load their X11/ALSA/Pulse runtime libraries separately. These observations establish software execution on the named systems, not physical-device or all-Linux compatibility.

## Reproduction and evidence location

The detailed review retains the command/environment, all nine installed hashes/modes, source paths, artifact identities and test counts. Current session files:

| Path under `/workspace/scratch/5ba97739b54c/` | Contents |
| --- | --- |
| `a41-hosted-linux/` | Downloaded ZIPs, safe extraction, authenticated metadata without URLs, audit/run scripts, JSON summaries, ELF/help/smoke logs |
| `a41-relocated-hosted-219821d/` | The actual hosted installed package after relocation |
| `a41-hosted-run-219821d/` | Private HOME, independently generated `smoke.bmp`/`smoke.json`; selected state absent |

Audit scripts are scratch-only and use fresh-directory assertions; create fresh destinations to repeat them. Reacquire the named artifacts through the GitHub download tool while retained (expiry 2026-11-27), verify both authenticated ZIP digests first, validate entry types/paths before extraction, compare inventory to named source objects, and run the archived executable from a new working directory. Preserve its identity when comparing later results.

One preliminary verification assertion rejected all PAX headers; inspection showed Python TAR's benign finite `mtime` metadata only, so the verifier explicitly accepted only that key before extracting. This was an overly strict audit assumption, not a product failure. No unsafe member was bypassed. No failed smoke or build was concealed by this audit.

## Handoff and next work

Root should publish these two reports with the wave's consolidated evidence. Keep this historic result tied to `219821d`; qualify the final newer source, integrated replay and its own packages independently. Other platforms require repaired builds and executed acceptance before package claims. Native devices/displays/MIDI, deadlines, C/system allocator/locking behavior, signing/notarization and permanent release retention remain open. Exact dependency notices are present, but the named source has no project-wide LICENSE and supplied-atlas rights remain unresolved; this audit makes no release-rights determination.

Future agents should follow root `AGENTS.md` and current handoff before changing scope, preserve parallel work and exact source/artifact identities, document actual commands/results/exclusions and the next action, and let the coordinator integrate/publish shared changes. Do not count a resumed review as another agent assignment or reclassify a skipped downstream step as an executed test failure.
