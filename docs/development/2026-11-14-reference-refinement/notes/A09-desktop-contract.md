# A09 — desktop interaction contract

Actual worker `/root/w02_a09_desktop_contract`, wave 2. Owned only this note and
`docs/REFERENCE_REFINEMENT_DESKTOP.md`; no production edits, CUA, UI launch,
commit or push. Source inspected at
`8bd999efc13e309b932e6ac41d72ceb7b9b80a5f`, with concurrent root documentation
preserved.

Read current AGENTS/scope/checkpoint/manifest, complete M0–M9 plan, recovery
handoff/A42/A57, ScriptedInput/MidiReplay, main event/shutdown/capture paths,
UiModel ownership and native workspace/MIDI/boundary tests. A07 supplied the
reviewed width-and-height breakpoint. Contract separates dummy replay, desktop
script delivery and actual OS capture; includes shared owners, relocated pedals,
off-window release/return and ordinary joined close without weakening bounds.

Actual verification: bundled CTest `-N` found four named acceptance suites;
both authored documents passed whitespace checks.
The Python entrypoint `../build-tools/bin/ctest` first failed with
`ModuleNotFoundError: cmake`; using `../build-tools/cmake/data/bin/ctest` resolved
listing. No native tests were executed by A09. Root reports baseline 147/147
MIDI-off and a compiled desktop/MIDI-on app; those remain root's evidence.
Root subsequently observed a desktop terminal, so this contract does not declare
desktop blocked. Next: test owners adapt only moved coordinates/branch journeys;
root executes and retains actual desktop observations against the changed binary.
