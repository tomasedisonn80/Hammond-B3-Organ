# External MIDI and reference-led native UI development

This newly requested session begins at `0f7b90037e51e101d8fa0bfe31af40209d751659`. It uses sixty **new actual workers**, six per logical wave and at most three concurrently. Earlier session assignments are historical and are not counted. The live [manifest](assignments.json) includes only workers actually dispatched; planned work is not completion.

The next independent product phase is a bounded external MIDI input adapter for the existing nominal standalone, together with native visual development against the atlas cover/page 409. The source PDF remains unchanged. Its generated reference has proposed proportions and inaccurate control legends; actual musical controls keep the repository's verified identities. A screenshot comparison records remaining differences and never implies measured hardware fidelity.

Wave 1 covers every word on all 500 atlas pages in six disjoint ranges. Later waves freeze contracts, implement transport and interface, independently qualify behavior, integrate the executable and publish exact-source results. The integrator owns shared status, next steps, development log, README and publication.

See the actual assignment notes for owned paths, execution and findings.

## Working sequence

The following themes organize work; only dispatched identities in the manifest
count as workers. Each logical wave has six distinct assignments, executed in
two batches under the three-worker concurrency limit. A later task may refine a
contract when an observed integration result supplies a concrete reason; retain
the original result and explain the correction.

| Wave | Purpose and concrete evidence |
|---|---|
| 1 | Read all 500 PDF pages, map the full M0–M9 plan, identify the exact art reference. |
| 2 | Freeze MIDI ownership/lifetime, independent acceptance, dependency and visual contracts. |
| 3 | Implement queue/decoder, physical backend, shared layout, renderer and application; test musical integration. |
| 4 | Exercise concurrent input and backend failures; add bounded synthetic input and native interaction acceptance. |
| 5 | Integrate existing workflows, package/setup support, actual captures and platform CI. |
| 6 | Independently audit lifetime, portability, rendering and diagnostics; fix demonstrated defects. |
| 7 | Qualify coherent source with complete default/native/sanitizer and compatibility checks. |
| 8 | Review source/assets, project-plan traceability, instructions, hosted results and actual UI behavior. |
| 9 | Integrate final defects, exact-source evidence, handoff and accounting; publish and inspect CI. |
| 10 | Independently verify completion records, product/package/UI results, remaining gates and publication readiness. |

The first published checkpoint is
[`7b36cfa`](https://github.com/tomasedisonn80/Hammond-B3-Organ/commit/7b36cfac2565397191b3df5e07112611e7f1b0e1):
complete source review, exact reference, scope and standing future-agent rules.
It does not contain or qualify the subsequent uncommitted implementation.
