# Assignment 58 — actual runtime context qualification

Actual worker **`/root/cal_w10_a58`**, assignment **58**, logical wave **10**,
session `2026-11-13-calibration`, 2026-11-14 UTC. This is one actual new worker.
Root owns ledger acceptance, shared status, commit and guarded publication.

## Owned result and bounded acceptance

Created only this note and
[CALIBRATION_RUNTIME_CONTEXT.md](../../reviews/CALIBRATION_RUNTIME_CONTEXT.md).
No production code, maintained test, source guide, schema, CMake, ledger,
shared status, Git index or ref was changed. Private experiment files live
outside the repository.

Actual CPython **3.13.5** passed the unchanged maintained CLI pipeline:
**nine methods / 71 actual project CLI child processes**, zero failures/errors/
skips, **6.681 seconds**. The separate twelve-project-process matrix uses
actual CPython 3.12.14 and 3.13.5, four producers and eight complete verifiers.
Four same-runtime replays match; four cross-runtime replays mismatch with
unchanged source inventories and differing actual runtime envelopes. Both
inconclusive and failed engineering outcomes are preserved.

The total is **83 project CLI child invocations** across these two experiments.
The one 3.13 unittest driver process, two `-c` runtime metadata probes and the
audit orchestrator are not counted as additional project CLI cases or tests.
This assignment does not claim the root's 106-suite gate, the hosted matrix,
a complete 3.13 toolchain acceptance, a native build or a physical experiment.

## Read source and coherence

Read AGENTS, PLAN, current calibration STATUS/NEXT_STEPS/handoff, root README
and latest log context, the scope and relevant atlas consolidation, the
replay contract and the actual pipeline test. The existing full-PDF readers and
[consolidation](../../research/CALIBRATION_ATLAS_REVIEW.md) own full atlas coverage.
This assignment does not claim a new whole-PDF or external-source review.
Truncated combined inspections were followed by focused reads for the source
contract and tests used in this experiment.

The actual public commit and tree were queried locally and asserted:
`d7f6100010eb4cdd028ec93000cd9e893ac6d190` /
`0140c737de4db28288b118744c2beef57976697f`. Fresh `git archive` extraction is
`/workspace/scratch/c9f3ead4c910/a58-runtime/source café 東京`.
All ten modules and the maintained pipeline test were individually checked
against `git show` at that public commit. A before/after path/size/hash inventory
covers all **1,023 files / 40,370,269 bytes**; every file remains unchanged.
This measures file bytes, not loaded memory or every filesystem metadata field.

| Qualified module | Bytes | SHA-256 |
| --- | ---: | --- |
| `capture_audio.py` | 30,313 | `f6f059a81078982d1061637c84836bef9564d51215cb37e0c120046ba0d7b216` |
| `capture_common.py` | 12,774 | `f583dbfde3d164157d7e5aa1c601878e3f7d44b4eb7fb059426b92045ac793ab` |
| `capture_corpus.py` | 39,476 | `baf4aac2fc87e322d2e5d663f4de9da8118559100ad7de1e6f77feba606779a8` |
| `capture_job.py` | 24,433 | `a12645460b4c35400e5f851ac61f7bf273741a3c8d249ee186e93c46ba43a92b` |
| `capture_readiness.py` | 11,630 | `816ae53470e54c428cf53bbcf566ddf9a46ad422e427f3bfb28d9b47ca7e64e1` |
| `capture_study.py` | 16,849 | `5147b3f7b959ff6e2e1c7ca4b49154579a212af1cf2604bb6272fd9a212f5f98` |
| `compare_capture.py` | 33,448 | `220a593499539db5f1e635db2eb15ba3c0aa7c6d001c80407fbffe93f75a9a0a` |
| `make_capture_demo.py` | 25,734 | `67a49b81f009677a7d2ac62c7f6b95a50e5dd885dca0cc2ac04ca42655f79535` |
| `validate_capture.py` | 28,237 | `f17ac8e24c98c792364bfdcc10c41bf410853ba19654eaa36482596d5881f3aa` |
| `verify_capture_report.py` | 23,489 | `6c100e976cbe9fa4748a66fe7c6a9488f4e87b4227edc2d88ddf83913b8e91ba` |

The study/demo source is the sixteen unchanged original files under
`examples/capture-demo`; the separate matrix retains the original policies,
timestamps, manifests, three raw sample files and study/job identities. Its
all-file inventory also catches changes to the rest of the extracted source.
The maintained pipeline intentionally creates and modifies its own temporary
Unicode fixtures and cleans them up; that is separate from the original archive.

## Actual commands and environment

Working directory for the top-level command was the repository root:

```sh
python3 -B -S /workspace/scratch/c9f3ead4c910/a58-runtime/audit_runtime.py
```

The final audit exited **0**. It selected the following actual executables:

- 3.12: `/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12`
- 3.13: `/usr/bin/python3.13`

Both report implementation `cpython`, platform `linux` and machine `x86_64`.
Their observed versions are 3.12.14 and 3.13.5. The child working directory is a
separate `foreign café 東京` directory. Every project CLI uses `-B -S`;
`PYTHONPATH` is empty, terminal encoding is `ascii:strict` and bytecode is
disabled. No other runtime was installed. Python 3.10 was not available or run.

The twelve-process matrix has two producer exits 3, two producer exits 1,
four matching verifier exits 0 and four mismatch exits 1. Every stdout is exact
canonical UTF-8/LF and equals its newly published file; stderr is empty.
Full saved and replayed identities are asserted against actual producer bytes.
The review retains the producer hashes; the eight complete summary identities are:

| Actual matrix label | Result | Bytes | Summary SHA-256 |
| --- | --- | ---: | --- |
| 312-replay-312-job | match | 3,932 | `aabf8aa7fed0eb055d848f61f9ffa1616d53c32bfbbd332e559a81a85fd7646f` |
| 312-replay-312-study | match | 4,262 | `5c6b8ad9c208566c887c92ba00e04978c304c20902d486a8474d47178e5e59db` |
| 312-replay-313-job | mismatch | 3,936 | `b0798c6826d5ddfa8c748e511e39ddec09c5cdfead34bda4651be1f34c1cc396` |
| 312-replay-313-study | mismatch | 4,266 | `53d90e5cce5cf7b6d8a1b93367822659e8e2e5ff70368b06f71a941569c902c0` |
| 313-replay-312-job | mismatch | 3,935 | `f5312463c8934f8d9793faad6e58d5807a8fa31770f1e3e190c1bcf68f0a2e84` |
| 313-replay-312-study | mismatch | 4,265 | `1173d6f8d0a51cfae2f9843b5125d690dbb351eb63d8e2feda8d9d55d527a19a` |
| 313-replay-313-job | match | 3,929 | `7d4eaee72e9b15b4db568eae8ce12d42f7cf6f27225b934c63ae4948a7cc24ec` |
| 313-replay-313-study | match | 4,259 | `38fef5ef97f320639340f9e8d350961d127a07e69473c7bec8a75aef651eae7e` |

Here `312-replay-313-study` means the 3.12 verifier executed the original input
against the study report produced by 3.13. Both cross-runtime directions remain
mismatches. No projected value is supplied to the verifier.

The optional diagnostic projections remove only the explicit runtime paths
listed in the review. Source inventories, original bindings, every numerical
result, role, work value, status and claim stay in the compared remainder.
These are independent audit observations and not weakened acceptance policies.

## Retained initial failure

The first audit source had a Python syntax error before any statement executed:

```text
line 87: ... == dict(jobs=3,pass=1,failed=1,inconclusive=1)
SyntaxError: invalid syntax
```

`pass` is a reserved keyword. No archive extraction, project CLI, runtime probe
or pipeline test occurred in that failed attempt. The exact initial source is
retained privately with the hash below. The only correction replaced that
invalid constructor expression with:

```python
{"jobs": 3, "pass": 1, "failed": 1, "inconclusive": 1}
```

The corrected script was compiled before execution. No production byte,
expected status/count/digest, policy or test was changed. The final executed
audit and driver are retained verbatim below; all final cases passed on their
first execution after this parse-only correction.

## Exact retained artifact identities

Files below are private run records, not public installation prerequisites.
The checked source pin and retained scripts provide the reproduction recipe.
Do not require a future clone to have this worker's scratch paths.

| Run file under `a58-runtime/` | Bytes | SHA-256 |
| --- | ---: | --- |
| `audit_runtime.initial.py` | 8,689 | `d549f1c76c194698042c487d79ca3794c7d7469e9027998eefe8b0c0e4faf71b` |
| `audit_runtime.py` | 8,693 | `e197c2989c28cfdbf06bdf96612c48f4fe0f756d881425ebfab392635a217dd8` |
| `pipeline_driver.py` | 1,291 | `0ed6e437372849ea7aa9960741157735eca1723ff88f1f007558cabdcd6da5d3` |
| `result.json` | 46,127 | `2bd082bf00d58c94cc7bb2b13657fd9c89008df170ea1f112a4d8e95c3d11a30` |
| `source-inventory.json` | 164,836 | `b93f76f1435034f19dfe27c860844f9852616307bd10a91f66d5d6635b0afd07` |
| `pipeline-observations.json` | 56,149 | `5849e16e27642ed250aba9774067b70a7370ce87047b1980acf0d2426798b2aa` |
| `pipeline.stdout` | 241 | `512e94d74e49b8628617384de5b33a422e046599a1144db4c7d1aff767cbbacd` |
| `pipeline.stderr` | 1,747 | `f71bbded5bbad3c705d7882bcad01ed1c09baa53120511be95523ed9b2d294df` |

The pipeline observations and full result contain temporary command paths and
measured elapsed time, so their hashes identify this execution rather than a
universal expected byte stream. The canonical producer/summary hashes above
belong to their explicitly observed source/runtime/input combination.

## Executed pipeline driver

This loads the unchanged test class and retains its existing observations.
It neither monkey-patches test methods nor replaces actual child processes.

```python
import importlib.util
import json
from pathlib import Path
import platform
import sys
import time
import unittest

source = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("a58_qualified_pipeline", source / "tests/test_capture_cli_pipeline.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
suite = unittest.defaultTestLoader.loadTestsFromTestCase(module.CaptureCliPipeline)
started = time.monotonic()
result = unittest.TextTestRunner(verbosity=2).run(suite)
data = {
    "runtime": {"executable": sys.executable, "python_version": platform.python_version(),
                "implementation": sys.implementation.name, "sys_platform": sys.platform,
                "machine": platform.machine()},
    "tests_run": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
    "skips": len(result.skipped), "seconds": time.monotonic() - started,
    "observations": module.CaptureCliPipeline.observations,
    "sources": module.CaptureCliPipeline.source_context,
}
Path(sys.argv[2]).write_text(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=True) + "\n")
print(json.dumps({k:v for k,v in data.items() if k not in ("observations","sources")}, sort_keys=True))
raise SystemExit(0 if result.wasSuccessful() else 1)
```

## Executed independent runtime audit

This is the exact corrected source, including its actual private paths.
A new execution requires a fresh work directory and the two selected runtimes;
do not overwrite an earlier run's evidence or rerun it in its populated directory.

```python
from pathlib import Path
import copy
import hashlib
import io
import json
import os
import subprocess
import tarfile

REPO=Path("/workspace/scratch/c9f3ead4c910/Hammond-B3-Organ")
WORK=Path(__file__).resolve().parent
PIN="d7f6100010eb4cdd028ec93000cd9e893ac6d190"
TREE="0140c737de4db28288b118744c2beef57976697f"
PYTHONS={"312":"/opt/codex/runtimes/codex-primary-runtime/dependencies/python/bin/python3.12",
         "313":"/usr/bin/python3.13"}
MODULES=("capture_audio", "capture_common", "capture_corpus", "capture_job",
         "capture_readiness", "capture_study", "compare_capture", "make_capture_demo",
         "validate_capture", "verify_capture_report")
def sha(b): return hashlib.sha256(b).hexdigest()
def canonical(o): return (json.dumps(o, sort_keys=True, indent=2, ensure_ascii=False, allow_nan=False)+"\n").encode()
def identity(b): return {"size_bytes":len(b),"sha256":sha(b)}
def inventory(path):
    return {p.relative_to(path).as_posix():identity(p.read_bytes())
            for p in sorted(path.rglob("*")) if p.is_file() and not p.is_symlink()}
def git(*args): return subprocess.check_output(["git",*args],cwd=REPO)
assert git("rev-parse",PIN).decode().strip()==PIN
assert git("rev-parse",PIN+"^{tree}").decode().strip()==TREE
source=WORK/"source café 東京"
source.mkdir()
raw=git("archive",PIN)
with tarfile.open(fileobj=io.BytesIO(raw)) as tf: tf.extractall(source,filter="data")
before=inventory(source)
for name in MODULES:
    rel="tools/"+name+".py"
    assert (source/rel).read_bytes()==git("show",PIN+":"+rel)
assert (source/"tests/test_capture_cli_pipeline.py").read_bytes()==git("show",PIN+":tests/test_capture_cli_pipeline.py")
tools=source/"tools"
archive=source/"examples/capture-demo"
outputs=WORK/"reports Ω"
outputs.mkdir()
foreign=WORK/"foreign café 東京"
foreign.mkdir()
env=dict(os.environ,PYTHONPATH="",PYTHONIOENCODING="ascii:strict",PYTHONDONTWRITEBYTECODE="1")
pipeline=subprocess.run([PYTHONS["313"],"-B","-S",str(WORK/"pipeline_driver.py"),str(source),str(WORK/"pipeline-observations.json")],
                        cwd=foreign,env=env,capture_output=True,timeout=120)
(WORK/"pipeline.stdout").write_bytes(pipeline.stdout)
(WORK/"pipeline.stderr").write_bytes(pipeline.stderr)
assert pipeline.returncode==0,(pipeline.returncode,pipeline.stderr.decode())
p=json.loads((WORK/"pipeline-observations.json").read_bytes())
assert (p["tests_run"],p["failures"],p["errors"],p["skips"])==(9,0,0,0),p
assert len(p["observations"])==71,len(p["observations"])
assert all(x["argv"][0]==PYTHONS["313"] for x in p["observations"])
assert p["runtime"]["python_version"]=="3.13.5"
assert inventory(source)==before
observations=[]
runtime_observations={}
for version,executable in PYTHONS.items():
    code="import sys,platform,json;print(json.dumps(dict(executable=sys.executable,python_implementation=sys.implementation.name,python_version=platform.python_version(),sys_platform=sys.platform,machine=platform.machine()),sort_keys=True))"
    r=subprocess.run([executable,"-B","-S","-c",code],cwd=foreign,env=env,capture_output=True,check=True)
    runtime_observations[version]=json.loads(r.stdout)
assert runtime_observations["312"]["python_version"]=="3.12.14"
assert runtime_observations["313"]["python_version"]=="3.13.5"
def run(version,module,args,label,expected):
    command=[PYTHONS[version],"-B","-S",str(tools/(module+".py")),*map(str,args)]
    r=subprocess.run(command,cwd=foreign,env=env,capture_output=True,timeout=30)
    observations.append(dict(label=label,argv=command,exit=r.returncode,
                             stdout=identity(r.stdout),stderr=identity(r.stderr)))
    (WORK/(label+".stdout")).write_bytes(r.stdout)
    (WORK/(label+".stderr")).write_bytes(r.stderr)
    assert r.returncode==expected,(label,r.returncode,r.stderr.decode())
    assert not r.stderr,(label,r.stderr)
    result=json.loads(r.stdout)
    assert r.stdout==canonical(result),label
    output=Path(command[command.index("--output")+1])
    assert output.read_bytes()==r.stdout,label
    return result,r.stdout,output
reports={}
for version in PYTHONS:
    for kind,filename,status,exitcode in (("job","job-inconclusive.json","inconclusive",3),
                                         ("study","study.json","failed",1)):
        value,raw,path=run(version,"capture_"+kind,["--input",archive/filename,"--output",outputs/(version+"-"+kind+".json")],
                           version+"-"+kind,exitcode)
        assert value["status"]==status
        assert value["runtime"]=={k:v for k,v in runtime_observations[version].items() if k!="executable"}
        reports[version,kind]=(value,raw,path)
        if kind=="study":
            assert {k:value["summary"][k] for k in ("jobs","pass","failed","inconclusive")}=={"jobs":3,"pass":1,"failed":1,"inconclusive":1}
            assert [x["report"]["status"] for x in value["jobs"]]==["pass","inconclusive","failed"]
replays=[]
for current in PYTHONS:
    for saved in PYTHONS:
        for kind,filename,status in (("job","job-inconclusive.json","inconclusive"),("study","study.json","failed")):
            same=current==saved
            label=current+"-replay-"+saved+"-"+kind
            value,raw,path=run(current,"verify_capture_report",
                ["--kind",kind,"--input",archive/filename,"--report",reports[saved,kind][2],"--output",outputs/(label+".json")],
                label,0 if same else 1)
            assert value["status"]==("match" if same else "mismatch")
            assert value["exact_report_match"] is same
            assert value["context"]["same_runtime"] is same
            assert value["context"]["same_tool_sources"] is True
            assert value["saved_engineering_status"]==value["replayed_engineering_status"]==status
            assert value["saved_report"]==identity(reports[saved,kind][1])
            assert value["replayed_report"]==identity(reports[current,kind][1])
            assert value["context"]["saved_runtime"]==reports[saved,kind][0]["runtime"]
            assert value["context"]["replayed_runtime"]==reports[current,kind][0]["runtime"]
            assert value["context"]["saved_tool_sources"]==value["context"]["replayed_tool_sources"]
            replays.append(dict(label=label,status=value["status"],context=value["context"],
                                saved_report=value["saved_report"],replayed_report=value["replayed_report"],
                                engineering_status=status,summary=identity(raw)))
projections={}
for kind in ("job","study"):
    values=[]
    paths=["/runtime"]
    if kind=="study": paths += ["/jobs/"+str(i)+"/report/runtime" for i in range(3)]
    for version in PYTHONS:
        value=copy.deepcopy(reports[version,kind][0])
        del value["runtime"]
        if kind=="study":
            for item in value["jobs"]: del item["report"]["runtime"]
        values.append(canonical(value))
    assert values[0]==values[1],kind
    assert reports["312",kind][1]!=reports["313",kind][1],kind
    projections[kind]=dict(removed_paths=paths,identity=identity(values[0]))
after=inventory(source)
assert before==after
assert len(observations)==12
for (version,kind),(value,raw,path) in reports.items(): assert path.read_bytes()==raw
result=dict(source_commit=PIN,source_tree=TREE,source_files=len(before),
            source_bytes=sum(i["size_bytes"] for i in before.values()),
            source_inventory=identity(canonical(before)),sources_unchanged=before==after,
            runtimes=runtime_observations,
            pipeline=dict(tests=p["tests_run"],failures=p["failures"],errors=p["errors"],skips=p["skips"],
                          processes=len(p["observations"]),seconds=p["seconds"],
                          observations=identity((WORK/"pipeline-observations.json").read_bytes()),
                          test_source=identity((source/"tests/test_capture_cli_pipeline.py").read_bytes()),
                          stdout=identity(pipeline.stdout),stderr=identity(pipeline.stderr)),
            producer_reports=[dict(version=v,kind=k,identity=identity(raw),status=value["status"]) for (v,k),(value,raw,path) in reports.items()],
            process_count=len(observations),replay_count=len(replays),replays=replays,
            projections=projections,observations=observations,
            modules={name+".py":identity((tools/(name+".py")).read_bytes()) for name in MODULES},
            demo=inventory(archive))
(WORK/"source-inventory.json").write_bytes(canonical(before))
(WORK/"result.json").write_bytes(canonical(result))
print(json.dumps({k:result[k] for k in ("source_files","source_bytes","sources_unchanged","pipeline","process_count","replay_count","projections")},sort_keys=True))
```

## Handoff and limits

No production defect was identified. Root may accept both owned records and
link this finite runtime result from the final handoff if useful. Preserve
the declared source/runtime identity and honest mismatch semantics when
continuing. A minimum-version CI gate, another interpreter/build, other operating
systems or additional numerical datasets require their own scoped evidence.
Do not label this review as Python 3.10 qualification or a full 3.13 regression.
Physical acquisition, metrology, fitting, held-out history and product/release
work remain under their existing owners and acceptance contracts.
