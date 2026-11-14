# Publication record

The owner authorized committing and pushing completed development to `main`.
The integration checkout preserves other workspaces and uses guarded, non-forced
updates after inspecting the remote head. Each published tree is compared with
the local staged tree before publication and fetched afterward.

| Checkpoint | Parent | Published commit | Exact tree | Scope |
| --- | --- | --- | --- | --- |
| Source and contract baseline | `b79086f6bb0c42b97130c721c5c73c7c97a13887` | `70b335480323329c7f5b207d5f58086c5b854960` | `d2051f41583650888055579dcd3d768977a908f2` | Full atlas reading, frozen contracts, independent source oracle, baseline qualification, future-agent rules and real assignments 1–15. Production implementation remained outside this checkpoint. |
| Hosted macOS baseline repair | `70b335480323329c7f5b207d5f58086c5b854960` | `352a398e4f004467c2dab081168be3d8b5206ea9` | `3e8f370e9234f46ff2463a6109540596f7950caa` | Removed the unused renderer color rejected by AppleClang and retained the actual failure/reproduced local repair. |
| Hosted macOS new-output repair | `352a398e4f004467c2dab081168be3d8b5206ea9` | `35554c068492fe2b20c1f8a602d8354ae762dc42` | `6a6881eeee1943665694e988208b2d6710731919` | Compare file identities only for existing leaves while preserving canonical new-path alias checks; 18 local native methods/164 launches passed. |

The baseline CTest transcripts are retained verbatim, including CTest/SDK
whitespace and expected unsupported-rate diagnostics. Their named test result
and source identity determine their scope; log formatting is not normalized.
Later implementation, actual application captures, integrated tests and final
publication are recorded as they occur. A checkpoint is not final session
completion or a physical-fidelity qualification.
