# Hosted macOS acquisition record

## Observed wave-5 run

Commit `88c36b4a72a07f6498f73279f25023278accd350` passed the complete local
65-suite Release gate. In [run 43404272839](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43404272839),
Linux GCC Release, Windows MSVC and Linux ASan/UBSan with leak checking passed.
The macOS job 131814612136 ended cancelled and the aggregate run concluded
failure. This does not establish a passing four-job matrix.

The job targeted `macos-15`; its metadata reports an empty runner name and zero
steps. Its recorded interval is 09:47:50–10:02:51 UTC on 2026-11-13. There was no
checkout, compiler invocation, test run or artifact from that job. The job-log
endpoint returned BlobNotFound. These are infrastructure observations, not a
project test failure or a successful test skip.

The public [check annotations](https://api.github.com/repos/tomasedisonn80/Hammond-B3-Organ/check-runs/131814612136/annotations)
contain one failure indicating that no hosted runner acquired the job after
multiple attempts, and three notices about capacity constraints for macOS ARM64
runners. Root inspected these directly after the connected generic fetch tool
reported that this particular endpoint was unsupported. No credential was
needed for the public read. No user settings or runner infrastructure changed.

## Recovery and evidence boundary

Remote main still equalled the exact qualified/published commit. Root requested
**one targeted retry of the cancelled macOS job**, leaving the already successful
Linux/Windows jobs and the workflow's test assertions unchanged. Its result must
be observed separately; requesting a rerun is not a pass. Further retries should
respond to evidence of recovery or a new meaningful source checkpoint, not
be an unchanged loop.

GitHub's [October 1 runner notice](https://github.blog/changelog/2026-10-01-github-actions-macos-14-runner-image-retirement/)
lists `macos-15` among supported ARM64 alternatives to the retired macOS 14
image. The [public status page](https://www.githubstatus.com/) reported all
systems operational and no November 13 incident at the time of inspection.
Those broad statements do not contradict or resolve this specific acquisition
failure; an account/pool-specific explanation beyond the annotations is not
established. No unsupported platform migration is inferred from the queue alone.

The preceding renderer-repair run's macOS job also ended cancelled. An earlier
working-note inference that a newer push caused that cancellation has been
withdrawn; only the observed result is retained without an unverified cause.
Subsequent platform reviews should record actual attempts, job IDs and whether
steps ran before interpreting results. Native SDK builds remain separate from
this SDK-free core/offline checkpoint.


## Targeted retry observed successful

The single requested retry acquired a macOS ARM64 runner. Job
[131822086122](https://github.com/tomasedisonn80/Hammond-B3-Organ/actions/runs/43404272839/job/131822086122)
actually compiled and ran the project: **65/65 suites passed in 45.86 seconds**.
The tool log shows the ARM64 compiler target and actual test completion. Run
43404272839, attempt 2, subsequently completed with aggregate conclusion
`success` at the unchanged commit `88c36b4a72a07f6498f73279f25023278accd350`.
All four latest job results are successful. The prior no-runner failure remains
part of this record; it was not erased or counted as a test pass.
