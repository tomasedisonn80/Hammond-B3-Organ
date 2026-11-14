# Bounded native input and startup acknowledgment — A52

**Result: the corrected workspace suite passes all six methods / 16 native
processes, and one separate 256-action native burst passes.** The burst preserves
both original keyboard targets, remembered Lower C4 focus, every sound control
and saved-state byte, then acknowledges the original releases before shutdown.
The [final record](../development/2026-11-14-interface-continuation/reports/a52-final-result.json)
links the exact source, commands, scripts, diagnostics and retained failures.

## Scope and identified source

A52 began as a bounded-input qualification. After A49 completed its serial
146/147 gate, root explicitly assigned the observed startup-baseline fixture
failure to A52 and released CPU. Root subsequently authorized the small shared
MIDI-checker correction described below. No native process ran before that
release. There was no configure, build, production, CMake, timeout, README or
index change; root owns integration and publication.

Every phase used the existing `../a36-status-bin/hammond_standalone`, 3,707,640
bytes, SHA-256
`bd4991a3b45543a01c9ce435da140af848d45f28ff535699397706e5d3925dc2`.
The observed HEAD/tree was `cdbb2beaa28bf136f9a8db6213819129514e2ae9` /
`b4d71c1f574ab17ba1a3f37b24667c1ff3f9c527`. Independently read committed blobs
and current files matched all **98** A46 product inventory entries at both
`8673713a484c40e26ac7810c7c4cbc22fa874426` and `cdbb2be`. All **96** entries
present in A36's build-source record also matched; the two additional entries
are the original reference image and its provenance JSON. The canonical
path-to-size/hash inventory digest is
`6addb1ff056e07a8dd50d587552814a99fd05921a1512ace39396a232efdfd4c`.

These checks ran before and after each phase. The binary, product inventory and
phase-specific fixture/helper inputs did not drift. The two test-file changes
are an explicit working overlay; A52 does not claim all 327 historical build
and test inputs remain identical. A36's recorded build uses GNU 14.2.0, CMake
4.4.4 and Release with MIDI enabled. This execution used Python 3.12.14 and
reported SDL 2.32.10, dummy audio/video and software rendering. No shared build
directory was consumed or modified.

## Concrete failure and fixture repair

A49's original [failure](../development/2026-11-14-interface-continuation/reports/a49-workspace-failure.json)
remains **146/147**, unchanged. The combined UI/synthetic-MIDI method first
recorded a copied observation at **191 ms**, after its first UI note was
submitted at the original **180 ms** schedule point. That observation had
applied/resolved sequence **3**, submitted sequence **4**, the complete loaded
controls and no applied held note. The old helper required both elapsed `<180`
and submitted=applied. Raising the time threshold alone would still fail the
second assumption. No evidence establishes a particular scheduler cause.

The repair first completes a **250 ms** prefix containing only the original
two Shift+Tab pairs at 50/60/80/90 ms and synthetic MIDI connect at 50 ms. The
replay format's minimum duration is 250 ms; the prefix includes only original
actions before the first note. Its pre-shutdown endpoint must retain literal
controls, empty holds, zero On/Off commands, zero MIDI packets, one device start
and exact submitted=applied=resolved acknowledgment. The observed sequence **3**
then supplies the command origin for the unchanged 3,200 ms full journey.

The full method still requires five On/five Off commands and an exact **+10**
Session-command delta, every original hold/control/view path, the independent
MIDI C4 owner after UI release, six accepted/zero dropped MIDI packets, exact
saved bytes and acknowledged cleanup. Additional sequence checks distinguish
submitted commands from the applied prefix. Other methods retain their existing
startup checks. UI, MIDI and initial-state bytes for the full journey match the
original A49 evidence exactly.

### Retained A52 authoring failure

The first A52 suite attempt passed five methods, then the new connect-only
prefix encountered a shared fixture assumption: `assert_common` unconditionally
required a positive MIDI arrival timestamp. The actual prefix exited zero,
acknowledged sequence 3, and correctly reported zero offered packets and a zero
timestamp. The original full combined journey was not reached. This attempt
retains **15 successful native exits and one failed test method**; it is not
reported as a passing suite.

Source inspection confirms `feed_midi_replay_bytes` updates the timestamp and
increments offered packets together; a Connect event does neither. The narrow
shared helper correction retains the existing `>0` assertion whenever packets
were offered and requires **exactly zero** otherwise. No packet, receipt time or
successful result was fabricated. Root explicitly authorized the correction
and one fresh full-suite qualification. The [authoring correction](../development/2026-11-14-interface-continuation/reports/a52-authoring-correction.json),
[exact fixture diff](../development/2026-11-14-interface-continuation/reports/a52-fixture-repair.patch),
original helper version and complete first-attempt evidence remain retained.

| Executed evidence | Result |
|---|---|
| First A52 suite | Five methods pass; connect-only prefix rejected by the shared timestamp assumption; 36.437 s launcher observation; 15 native exits zero. |
| Corrected complete workspace suite | **6/6 methods; 16/16 native exits zero**; 40.346 s launcher observation. Original 9-second child and 90-second suite limits unchanged. |
| Retained A49 trace through the repaired complete method | Passes using the freshly measured prefix; the original assertion is independently reproduced as failing. No native launch. |
| Seven deliberately corrupted traces | All rejected: invented zero-packet timestamp, missing positive-packet timestamp, unacknowledged prefix, extra command, missing Off, lost independent MIDI owner and dropped packet. |
| Bounded 256-action burst | Passes once; 5.511 s wall observation under its 20-second process cap. |

The repaired shared checker was exercised on both actual zero-packet and actual
positive-packet retained diagnostics. A49 had already executed all twelve MIDI
methods on this binary; their positive-packet timestamp assertion remains
identical. That full MIDI suite was not repeated. In total A52 launched **32**
native processes across the diagnosed first attempt, corrected suite and burst.
All native applications exited zero; the first suite's test failure remains a
separate, visible outcome.

## Source-derived burst budget

The limits come from `ScriptedInput.h/.cpp`, `Session.h`, the native main loop
and the documented `B3UIREPLAY1` grammar. They are not a new product stress limit.

| Bound or count | Source limit / actual exercise |
|---|---|
| Replay action records | **256 maximum / 256 used** |
| Replay bytes | 65,536 maximum / **5,673 used** |
| Replay duration | 250–10,000 ms admitted / **5,400 ms used** |
| Equal-time due prefix | **228 scheduled actions at 2,600 ms**; source order retained |
| Presentation inputs | 242 key records: F4/F5/F6 each 30 activations, F7 31 activations |
| Other inputs | 14 records for focus, two original keyboard owners, target selection, focus audition and releases |
| Main-loop event drain | At most 256 polled events per turn; diagnostic action counts exclude markers and native notifications |
| Session command queue | 256 capacity; this case intentionally posts only **six** post-startup note commands |
| Retained histories | 512 musical and 512 presentation entries available; **13** and **10** recorded |
| Application drain allowance | Existing 2,000 ms; unchanged |

The six-command budget ends at the acknowledged pre-shutdown replay snapshot;
the ordinary closing UI release is accounted for separately below.

The equal-time burst contains 114 paired presentation activations. Seven other
activations are spaced to expose reviewable view endpoints. The full intended
stream has 90 workspace changes and 31 presentation toggles. Delivery of all
256 action records is acknowledged; the application does not expose a per-key
activation counter or paint every intermediate view. The 228-action figure is a
schedule count, not a measured one-turn SDL dispatch count.

## Observed ownership, focus and shutdown

The script first remembers Lower C4 through two reverse Tabs. Physical **A**
owns Upper 60 and physical **S** owns Lower 62; it then requests F3's Pedals
keyboard target. Both original targets remain held across the complete
presentation stream. Returning to Play/Flat restores the semantic Lower C4
focus: Space adds **Lower 60** while Upper 60 and Lower 62 remain held. Space
release removes only that audition. The later original A release, with
Ctrl/Alt/Meta, removes Upper 60; the original S release, with Shift, removes
Lower 62. Every acknowledged sequence prefix matches its literal target set.
The final release is observed at 4,932 ms, before ordinary shutdown.

The nine distinct painted endpoints are Play/Dimensional, Rotary/Dimensional,
Rotary/Flat, Service/Flat, Play/Flat, Rotary/Dimensional, Service/Dimensional,
Play/Dimensional and Play/Flat. Copied frame clocks progress without reversal.
The final paint has a truthful copied inspection state and no pending controls.
Focus is qualified through the resulting note target; no focus pixels were
captured.

All observations, final desired controls and final applied controls equal the
independent literal state4 fixture. Its **452 bytes** remain unchanged. The
startup sequence is 3; the exact pre-shutdown submitted/applied/resolved sequence
is **9**. Three On plus three Off commands account for the entire +6 delta, so
navigation injected no control snapshot, Panic or release command. All **256**
scheduled actions were pushed and delivered without truncated histories.

One audio lifecycle reports 486 callbacks, 248,832 frames and 165 painted images,
with zero application/audio faults, queue overflows, rejections or recoveries.
MIDI source is `none`; all discovery and input counters remain zero. Before
shutdown no note is held and every script command is acknowledged. Joined stop
is not running and remains unheld. Its resolved sequence 10, applied sequence 9
and one discarded command account exactly for the redundant closing UI release
that `Session.stop` can discard; this is not an unacknowledged script action.

| Exact burst identity | SHA-256 |
|---|---|
| `input.b3uireplay` | `f926148eef823b70c6b0159a519071afd4de28c93d4ac54487b6a9026500ea45` |
| `diagnostics.json` | `744a6f4825e38c0c73ccaba692f3f05f2920bb4ee953e42d9e91559558b45f6c` |
| Unchanged `controls.b3controls` | `4ccbf8d166b3dacf34a06ef50641d4c48fafa9507e19ccd0707b852af25a24cf` |

## Reproduction and remaining limits

From the repository root, use the preserved
[helper](../development/2026-11-14-interface-continuation/reports/a52-qualification.py)
with a **fresh** output directory for each phase:

```sh
python3 -B docs/development/2026-11-14-interface-continuation/reports/a52-qualification.py suite \
  --executable ../a36-status-bin/hammond_standalone \
  --output docs/development/2026-11-14-interface-continuation/reports/a52-repro-workspace
python3 -B docs/development/2026-11-14-interface-continuation/reports/a52-qualification.py retained \
  --executable ../a36-status-bin/hammond_standalone \
  --suite-output docs/development/2026-11-14-interface-continuation/reports/a52-repro-workspace \
  --output docs/development/2026-11-14-interface-continuation/reports/a52-repro-retained
python3 -B docs/development/2026-11-14-interface-continuation/reports/a52-qualification.py burst \
  --executable ../a36-status-bin/hammond_standalone \
  --suite-output docs/development/2026-11-14-interface-continuation/reports/a52-repro-workspace \
  --output docs/development/2026-11-14-interface-continuation/reports/a52-repro-burst
```

The helper requires the retained A36/A46/A49 source evidence and both named Git
commits. Output paths stay inside the repository because the report links use
repository-relative identities; each named output directory must be absent.

The burst uses a 1280×900 logical and actual dummy drawable, 48 kHz stereo float
audio and 512-frame buffers. Linux `wait4` observes 34,748 KiB maximum RSS for
this single child, with 10 ms polling quantization. This is an observation, not
a memory ceiling, performance ranking, leak test or callback-deadline result.
The 8,192 logical window limit does not cap physical drawable allocation;
no giant surface or screenshot was created here.

No pointer input occurs in the burst. The existing suite's dummy capture-failure
handling does not qualify persistent OS pointer capture. Physical display/DPI,
controllers/audio devices, semantic accessibility, exact PCM histories, native
hosts, literal reference equality and measured organ fidelity retain their
separate gates. Session snapshots expose logical held targets, not individual
live owner records or acoustic audibility. Root should integrate these two test
repairs and link their focused qualification while preserving A49's original
146/147 result; A57's real desktop and the broader M0–M9 work remain separate.
