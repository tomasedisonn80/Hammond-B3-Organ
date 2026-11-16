# Converted contact-grid native comparison

**A21: the recorded accepted conversion corpus passes exact native comparison.**
All 71 inputs remain in the result: **51 accepted and 20 refused**. The native
probe ran **557 times**, with exact agreement on every observed edge, every
reported block count and every field of each complete padded snapshot. This is
a finite synthetic trajectory result, separate from audio accuracy or physical
contact fidelity.

The [source-bound receipt](../development/2026-11-16-conversion-material/reports/A21-native-initial.json)
retains every outcome and refusal witness, complete single-block native results,
all selected prefix snapshots, process input/output hashes, partition schedules,
timings and 13 source identities. Its filename identifies the first complete
execution; that execution passed. The [process receipt](../development/2026-11-16-conversion-material/reports/A21-process-initial.json)
and [unittest log](../development/2026-11-16-conversion-material/reports/A21-native-initial.log)
retain the actual command, external timeout and observed result.

## Independent comparison boundary

The new [test suite](../../tests/test_contact_grid_conversion_native.py) calls
only the converter's public conversion and certificate APIs. It independently
evaluates the rounding equations from the unchanged parser's canonical original
binary64 values using `Fraction` and nearest/even `round`. It preserves the
source key/contact order and sorts commands by exact time and caller ordinal.
The candidate's complete `grid_case` must match that independent result, with
exact Python types as well as values.

Expected native trajectories come from the existing
[completed-path Fraction oracle](../../tests/reference/causal_contact_grid_reference.py).
That oracle reconstructs each key's path and then scans each contact, rather
than importing native crossing helpers or the converter's online replay. The
native observation must match its exact mixed-fraction edge times, ordered
key/contact identities, closed bits, phase, full configuration, cursor, command
and edge counts, positions, targets and persistent anchors. Both configuration
and state contain all four entries, including complete zero padding for inactive
keys. The accepted corpus has one, two and four active keys at all three rates.

The suite independently serializes the literal `CGGRID1` grammar. For every
accepted input, the certificate's embedded transport bytes, hash and default
partition must match that serialization exactly. Those exact certificate bytes
are then submitted to the native probe. The strict encoder's returned document
must also be canonical JSON, reproduce the supplied result without extra fields,
and bind the actual four module hashes, admitted contract hash and Python version.
Native edge occurrences are independently labeled and their exact frame times
compared with certificate `grid_time` records; native positions, targets and
contact bits are compared with every certificate final-key record.

The six comparator sensitivity checks reject an altered persistent anchor,
inactive contact state, inactive configuration threshold, integer-to-float
substitution, block edge count and fractional edge numerator. This guards against
a comparison that accidentally examines only active keys or aggregate counts.

## Executed corpus and partitions

| Input family | Accepted | Refused | Native handling |
| --- | ---: | ---: | --- |
| All 35 pre-frozen conversion cases | 18 | 17 | Every expected disposition retained; accepted cases replayed |
| All 36 unchanged original fixtures | 33 | 3 | Original input hashes and sizes verified; F09 refused at all three rates |
| Total | **51** | **20** | No known refusal is forwarded to the native probe, even if a future converter regression unexpectedly accepts it |

There are **147 complete-epoch runs**: 48 single-block, 48 one-frame and 48
irregular runs, plus the three zero-frame observations. The irregular schedule
repeats `(3,1,11,2,7,5)`, clipping only its final length. Concatenated edges and
the full final snapshot agree across all schedules. Every block's edge count is
computed independently using exact incoming edge times and the inclusive right
endpoint; no float conversion decides an edge's ownership.

The suite selects **341 causal-prefix cuts**: zero, the final endpoint, fixed
early/middle/penultimate frames, and both adjacent frame boundaries of every
command. Each cut is replayed with only commands strictly earlier than its
endpoint. An additional **69 runs** apply all endpoint commands in their original
order through closure. These include five cuts with multiple tied commands and
the zero-frame 512-command case. Closure preserves positions, contact bits and
edges while advancing the command count and updating the appropriate targets and
anchors exactly as the independent oracle specifies.

| Executed comparison | Count |
| --- | ---: |
| Native processes, all exit 0 with empty stderr | **557** |
| Complete partition runs | **147** |
| Prefix and explicit endpoint-closure runs | **410** |
| Exact per-block count checks | **19,233** |
| Complete padded native snapshots compared | **557** |
| Unittest methods | **4 passed; 0 failures/errors/skips** |

The four methods completed in **3.719 seconds**. The source-bound runner reports
3.721073619 seconds including setup; the enclosing process took **4.153361126
seconds**, under an explicit 60-second external timeout. Each native invocation
has a 10-second timeout and the probe's 2 MiB report bound. These are observations,
not portable deadline or memory guarantees. The retained comparison receipt is
4,068,213 bytes, below the suite's 16 MiB evidence cap.

## Endpoint and retry limits

The current wire probe exposes a final closed snapshot and per-block counts;
it does not expose an intermediate snapshot inside the same long-running native
process. The full prefix state is therefore observed in a separate process. For
the pre-closure comparison, an independently computed `ready`/`active` snapshot
has **only its phase** changed to `closed`, because the probe always performs an
empty closure. No position, anchor, bit, counter or configuration is normalized.
The test does not claim direct observation of an active-phase native snapshot.

This accepted converted corpus contains no edge exactly on an integer-frame
boundary. The frozen endpoint/equality cases that conversion refuses remain
refused; they are not rounded and silently admitted to improve coverage. Exact
incoming block-end equality is covered separately by the unchanged native grid
[differential suite](../../tests/test_causal_contact_grid_differential.py).

`CGGRID1` does not expose output-capacity or retry controls. This new suite makes
no per-certificate short-buffer retry claim. The existing
[native lifecycle suite](../../tests/test_causal_contact_grid_lifecycle.cpp)
retains that distinct API/transaction scope. Root combines its coherent native
gate with this converted-input comparison; this worker did not build or rerun
that separate executable.

## Source bindings and reproduction

The run occurred after A19's diagnostic recursion catch and A20's failed-stdout
cleanup, with all 13 watched files and the probe binary unchanged throughout.

| Input | SHA-256 |
| --- | --- |
| Numerical converter | `eff387f8457040ea67400dcb378ee1c2049b604d7c862fd6ca683b52c8f93797` |
| CLI | `56b73884ab44fc0694a763e6ffd576590c613926bfbc42f60ad0491c2caa935c` |
| Native comparison suite | `d6f036e217b41d33b11f09a89b36bee92f80119c025ada971e0c99212ccd7cbc` |
| Independent grid oracle | `3b16fbdb299a93806b3a626bd259f1f4649e042fd8f55b314c8eedb10c2b5a27` |
| Native probe, 53,064 bytes | `191c1179cf5fb6b2059498445651a6a81cc63161aececa8c248a981b0afb306d` |
| Complete comparison receipt | `91df109b08ae7c63a6252ea7a02d2b8e4a9fd3681fe7c520e9169a43ce797b26` |

From the repository root, with root's coherently built probe:

```sh
HAMMOND_CAUSAL_CONTACT_GRID_PROBE_EXECUTABLE="$PWD/../build-native/hammond_causal_contact_grid_probe" \
  python3 -B tests/test_contact_grid_conversion_native.py -v
```

Optional `--report <fresh-path.json>` retains a new receipt and refuses to overwrite
existing evidence. Missing, empty, non-file or nonexecutable probe configuration
is a setup error, never a skipped success. Root's CMake discovery already supplies
the probe location for the `test_contact_grid_conversion*` family; root owns its
regeneration and combined CTest gate.

No production source, original fixture, native probe or oracle changed in this
assignment. There was no native build, installation, audio render, broad CTest,
commit or push. Installation, remaining resource/transaction reviews, exact-source
platform qualification, audio reconstruction, continuous full-window grading,
indefinite/full-organ capacity and physical acquisition retain their own gates.
