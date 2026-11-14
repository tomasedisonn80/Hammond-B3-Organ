#!/usr/bin/env python3
"""Read retained primary hosted logs; no product execution or Git mutation."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, re, subprocess

REPO = Path("/workspace/scratch/1bb6ee17ad7e/Hammond-B3-Organ")
CACHE = Path("/workspace/scratch/1bb6ee17ad7e/A60-closing-hosted-audit")
OUT = REPO / "docs/development/2026-11-14-reference-refinement/reports"
HEAD = "fd2f6060b1f03b6d902ff0547441c07d6e74ba4f"
TREE = "89c0fb214b018ca43ec9c8b413d3030284a54ec2"
PARENT = "0ed3ee4e5d5bcfffaf9b0633f212c45f553b5156"
INCOMING = "487064d2400b9f39d0ee66ed136a09c9e372379e"
RUNS = {43654334888: ("core", 5), 43654334873: ("native", 5), 43654334846: ("vst3", 3)}
EXTRACT_NAME = "A60-final-hosted-primary-excerpts.log"
ANSI = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
STAMP = re.compile(r"^\ufeff?\d{4}-\d\d-\d\dT\S+Z ")
RESULT = re.compile(r"^\s*(\d+)/(\d+) Test\s+#(\d+):\s+(\S+)\s+.*?\b(Passed)\s+(\d+(?:\.\d+)?)\s+sec")
checks = []

def read(path): return json.loads(path.read_text())
def digest(raw): return hashlib.sha256(raw).hexdigest()
def identity(path):
    raw = path.read_bytes()
    return {"bytes": len(raw), "sha256": digest(raw)}
def git(*args): return subprocess.check_output(["git", *args], cwd=REPO)
def blob(path, ref=HEAD): return git("show", ref + ":" + path)
def check(name, result, detail=None):
    checks.append({"name": name, "passed": bool(result), **({"detail": detail} if detail is not None else {})})

def main():
    meta = read(CACHE / "metadata-final.json")
    observations = read(CACHE / "observations.json")
    history_before = read(CACHE / "history-before.json")
    selected_source = read(CACHE / "source-inspection.json")
    check("published_tree", git("rev-parse", HEAD+"^{tree}").decode().strip() == TREE)
    check("published_parent", git("rev-parse", HEAD+"^").decode().strip() == PARENT)
    check("three_expected_run_ids", {x["run"]["id"] for x in meta["runs"]} == set(RUNS))
    native_source = blob(".github/workflows/standalone.yml").decode()
    native_required = re.search(r"HAMMOND_SANITIZER_TARGETS: >-\n(.*?)    steps:", native_source, re.S).group(1).split()
    check("native_sanitizer_exact_sixteen_source", len(native_required) == len(set(native_required)) == 16 and "test_standalone_midi_backend_quarantine" not in native_required)
    published_paths = git("ls-tree", "-r", "--name-only", HEAD).decode().splitlines()
    rotary_required = sorted([Path(p).stem if p.endswith(".cpp") else "python_"+Path(p).stem
                              for p in published_paths if p.startswith("tests/test_rotary") and p.endswith((".cpp", ".py"))]
                             + ["python_test_rotary_waveform_report_admission"])
    core_names, native_names, jobs, run_reports = [], [], [], []
    excerpts = [
        "A60 closing hosted audit: selected primary log lines",
        "Source " + HEAD + "; tree " + TREE + "; attempt 1.",
        "Full log SHA-256 values cover exact connector-decoded text encoded as UTF-8, preserving BOM and line endings.",
        "Numbered excerpts remove ANSI escapes and use LF; omitted lines are not represented as absent from the full log.",
        "No logs, failures, cancellations, accepted worker records or product sources were rewritten.",
    ]
    strict_observed = full_observed = None
    repairs = {}
    for item in meta["runs"]:
        run = item["run"]
        kind, expected_count = RUNS[run["id"]]
        check(f"run_{run['id']}_identity", run["head_sha"] == HEAD and run["head_commit"]["tree_id"] == TREE and run["run_attempt"] == 1)
        check(f"run_{run['id']}_complete_success", run["status"] == "completed" and run["conclusion"] == "success")
        check(f"run_{run['id']}_job_count", len(item["jobs"]) == expected_count)
        run_reports.append({k: run[k] for k in ("id", "name", "path", "head_sha", "event", "run_attempt", "status", "conclusion", "created_at", "updated_at", "html_url")})
        for job in item["jobs"]:
            jid = job["id"]
            cache_record = read(CACHE / f"{jid}.json")
            decoded = cache_record["log"]
            raw = decoded.encode("utf-8")
            lines = [ANSI.sub("", s) for s in decoded.splitlines()]
            body = [STAMP.sub("", s) for s in lines]
            keep = set()
            def retain(index, before=0, after=0):
                keep.update(range(max(0,index-before), min(len(lines),index+after+1)))
            def find_lines(pattern):
                return [(i,s) for i,s in enumerate(body) if re.search(pattern,s)]
            check(f"job_{jid}_complete_success", job["status"] == "completed" and job["conclusion"] == "success")
            ids = [i for i,s in enumerate(body) if s.strip("'") == HEAD]
            check(f"job_{jid}_actual_checkout", bool(ids))
            for i in ids: retain(i)
            j = {
                "run_id": run["id"], "job_id": jid, "name": job["name"],
                "url": run["html_url"] + "/job/" + str(jid),
                "head_sha": HEAD, "tree_from_run": TREE,
                "status": job["status"], "conclusion": job["conclusion"],
                "steps": [{"name":s["name"],"status":s["status"],"conclusion":s["conclusion"]} for s in job["steps"]],
                "primary_log": {"sha256_utf8":digest(raw),"bytes_utf8":len(raw),"decoded_characters":len(decoded),
                                "line_count":len(lines),"checkout_identity_lines":[i+1 for i in ids],
                                "fetched_at":cache_record["fetched_at"],"excerpt_file":EXTRACT_NAME},
            }
            toolchain = {}
            for key,pattern in {
                "cmake":r"^cmake version (.+)$","ctest":r"^ctest version (.+)$","python":r"^Python (.+)$",
                "cxx":r"^-- The CXX compiler identification is (.+)$","c":r"^-- The C compiler identification is (.+)$",
                "runner_image":r"^Image: (.+)$"
            }.items():
                matches = [(i,m[1]) for i,s in enumerate(body) if (m:=re.match(pattern,s))]
                if matches:
                    i,value=matches[0];toolchain[key]=value;retain(i)
                    if key=="runner_image" and i+1<len(body):
                        toolchain["runner_image_version"]=body[i+1];retain(i+1)
            j["toolchain"] = toolchain
            warnings = [(i,s) for i,s in enumerate(body) if re.search(r"\bwarning:|\bWarning\b|\bwarning C\d",s) and not re.search(r"\d+ Warning\(s\)",s)]
            j["warnings"] = [{"line":i+1,"text":s} for i,s in warnings]
            for i,s in warnings: retain(i,after=6 if "CMake" in s else 0)
            rows=[]
            for i,s in enumerate(body):
                m=RESULT.match(s)
                if m:
                    rows.append({"ordinal":int(m[1]),"total":int(m[2]),"test_id":int(m[3]),"name":m[4],
                                 "status":m[5],"seconds":float(m[6]),"line":i+1})
            full_job = kind=="core" and job["name"].startswith("Complete R4")
            if not full_job:
                totals=[(i,int(m[1])) for i,s in enumerate(body) if (m:=re.fullmatch(r"100% tests passed(?:, 0 tests failed)? out of (\d+)",s))]
                times=[(i,float(m[1])) for i,s in enumerate(body) if (m:=re.fullmatch(r"Total Test time \(real\) =\s*([\d.]+) sec",s))]
                complete=(len(totals)==len(times)==1)
                total=totals[0][1] if totals else 0
                complete=complete and len(rows)==len({x["test_id"] for x in rows})==len({x["name"] for x in rows})==total and {x["ordinal"] for x in rows}==set(range(1,total+1)) and {x["total"] for x in rows}=={total}
                check(f"job_{jid}_complete_unique_ctest",complete)
                names={x["name"]:x for x in rows}
                j["ctest"]={"passed":len(rows),"failed":0 if complete else None,"total":total,
                            "seconds":times[0][1] if times else None,"unique_names_and_ids_and_complete_ordinals":complete,
                            "test_names_sha256":digest(json.dumps(sorted(names),separators=(",",":")).encode()),
                            "summary_line":totals[0][0]+1 if totals else None}
                for i,_ in totals+times: retain(i)
                if kind=="core":
                    core_names.append(set(names))
                    check(f"job_{jid}_all_required_rotary",set(rotary_required)<=set(names))
                    required=rotary_required+["python_test_refinement_session","test_standalone_midi_backend_quarantine"]
                    j["required_rotary_and_record_results"]=[names[n] for n in required if n in names]
                    for result in j["required_rotary_and_record_results"]: retain(result["line"]-1)
                    if "macOS" in job["name"] or "Windows" in job["name"]:
                        repairs[job["name"]]=names.get("python_test_rotary_waveform_acceptance")
                elif kind=="native":
                    check(f"job_{jid}_native_required_gates",set(native_required)<=set(names))
                    native_leaks="ASan" in job["name"]
                    if native_leaks:
                        check(f"job_{jid}_exact_native_leak_set",set(names)==set(native_required))
                    else:
                        native_names.append(set(names))
                        check(f"job_{jid}_waveform_material", "test_standalone_waveform_material" in names)
                        if "macOS" in job["name"]: repairs[job["name"]]=names.get("test_standalone_waveform_material")
                    wanted=native_required+(["test_standalone_waveform_material"] if not native_leaks else [])
                    j["required_native_results"]=[names[n] for n in wanted if n in names]
                    for result in j["required_native_results"]: retain(result["line"]-1)
                    fixture=[]
                    for i,s in enumerate(body):
                        match=re.match(r"^\d+: (\{.*\})$",s)
                        if not match:continue
                        try:value=json.loads(match[1])
                        except json.JSONDecodeError:continue
                        if "checks" in value and "failures" in value:
                            fixture.append({"line":i+1,"output_json_sha256":digest(match[1].encode()),
                                            **{k:v for k,v in value.items() if not isinstance(v,(dict,list))}});retain(i)
                    j["native_fixture_primary_outputs"]=fixture
                    material=[x for x in fixture if x.get("checks")==1071 and x.get("legacy_checks")==901 and x.get("header_checks")==170]
                    check(f"job_{jid}_material_1071",len(material)==1 and material[0].get("failures")==0)
                    if not native_leaks:
                        waveform_material=[x for x in fixture if x.get("checks")==1917 and x.get("cases")==55]
                        check(f"job_{jid}_waveform_material_1917",len(waveform_material)==1 and waveform_material[0].get("failures")==0 and waveform_material[0].get("baseline_comparison") is False)
                        installed=find_lines(r"^Verified \d+ installed files")
                        check(f"job_{jid}_relocated_payload_guard",len(installed)==1)
                        j["relocated_payload_guard"]=[{"line":i+1,"text":s} for i,s in installed]
                        for i,s in installed:retain(i)
                else:
                    results=find_lines(r"^\d+: Result: 47 tests passed, 0 tests failed$")
                    check(f"job_{jid}_sdk_validator_47",len(results)==1)
                    j["sdk_validator"]={"passed":47,"failed":0,"line":results[0][0]+1 if results else None}
                    for i,s in results:retain(i)
                    for row in rows:retain(row["line"]-1)
            else:
                primary=[]
                for i,s in enumerate(body):
                    if s.startswith('{"status":'):
                        try:value=json.loads(s)
                        except json.JSONDecodeError:continue
                        if value.get("mode")=="full":
                            primary.append({"line":i+1,"result":value});retain(i)
                check("full_waveform_primary_pass",len(primary)==1 and primary[0]["result"].get("status")=="pass" and primary[0]["result"].get("failures")==[])
                admissions=find_lines(r"^Ran \d+ tests in .+s$")
                ok=find_lines(r"^OK$")
                check("full_waveform_admission_selftests_primary",len(admissions)==1 and bool(ok))
                j["full_waveform_primary"]=primary
                j["strict_report_admission_primary"]=[{"line":i+1,"text":s} for i,s in admissions+ok]
                for i,s in admissions+ok:retain(i)
                for i,s in find_lines(r"test_rotary_waveform_acceptance.py.*--(?:self-test|mode)|check_rotary_waveform_full"): retain(i)
                full_observed={"job_id":jid,"url":j["url"],"primary":primary,"admission_selftests":j["strict_report_admission_primary"],
                               "scope":"Actual full target and strict verifier executed at the published source. Uploaded qualification payload numerical metrics are not independently replayed by this primary-log audit."}
            if kind=="core" and job["name"]=="Release (Linux GCC)":
                target=[s for s in job["steps"] if s["name"]=="Verify the completed refinement session"]
                check("linux_actual_strict60_step",len(target)==1 and target[0]["conclusion"]=="success")
                observed=[]
                record=json.loads(blob("docs/development/2026-11-14-reference-refinement/completion-check.json"))
                for i,s in enumerate(body):
                    if s.strip()!="{":continue
                    joined="\n".join(body[i:])
                    try:value,end=json.JSONDecoder().raw_decode(joined)
                    except json.JSONDecodeError:continue
                    if value.get("session")!="2026-11-14-reference-refinement":continue
                    last=i+joined[:end].count("\n");observed.append((i,last,value))
                    for index in range(i,last+1):
                        if not (body[index].startswith("    {") or body[index].startswith("      ") or body[index].startswith("    }")):retain(index)
                check("linux_primary_strict60_output",len(observed)==1 and observed[0][2]==record and record["status"]=="passed" and record["mode"]=="strict_completion" and record["counts"]["accepted"]==60 and record["counts"]["verified_accepted_notes"]==60 and record["error_count"]==0)
                if observed:
                    first,last,value=observed[0]
                    strict_observed={k:v for k,v in value.items() if k!="checked_notes"}
                    strict_observed.update({"job_id":jid,"url":j["url"],"primary_json_first_line":first+1,"primary_json_last_line":last+1,
                                            "parsed_output_equals_committed_record":value==record,"checked_note_count":len(value["checked_notes"]),
                                            "committed_record":identity(REPO/"docs/development/2026-11-14-reference-refinement/completion-check.json")})
                    j["strict60_primary"]=strict_observed
                for i,s in find_lines(r"check_refinement_session.py --repo"):retain(i)
            if "ASan" in job["name"]:
                policy={"ASAN_OPTIONS":"detect_leaks=1:halt_on_error=1","UBSAN_OPTIONS":"print_stacktrace=1:halt_on_error=1","LSAN_OPTIONS":"exitcode=23"}
                policy_lines={}
                for key,value in policy.items():
                    found=[i for i,s in enumerate(body) if s.strip()==key+": "+value]
                    check(f"job_{jid}_{key}",bool(found));policy_lines[key]=[i+1 for i in found]
                    if found:retain(found[0])
                j["sanitizer_job_defaults"]=policy;j["sanitizer_environment_lines"]=policy_lines
                if kind=="native":
                    guards=["Require instrumented SDL C and project C++ objects and linked runtimes","Discover exactly sixteen gates and run with leak checking","Reverify source and locked SDL2 after acceptance"]
                    check("native_sanitizer_primary_guards",all(any(s["name"]==name and s["conclusion"]=="success" for s in job["steps"]) for name in guards))
                    j["successful_native_instrumentation_and_execution_guards"]=guards
                    for i,s in find_lines(r"^Discovered exactly 16 built|assert.*(?:__asan_|libasan|fsanitize|overrides|len\(names\))|--no-tests=error|ctest --test-dir build-standalone-sanitizers"):retain(i)
                else:
                    sources=["src/RotaryMotion.cpp","src/RotaryPropagation.cpp","src/RotaryHistory.cpp","src/RotaryStreamingPath.cpp","src/RotaryRenderer.cpp","tests/test_rotary_propagation_allocation.cpp","tests/probes/rotary_waveform_probe.cpp"]
                    proof={}
                    for source in sources:
                        hits=[i for i,s in enumerate(body) if source in s and "-fsanitize=address,undefined" in s and " -c " in s]
                        check("core_instrumented_"+source,bool(hits));proof[source]=hits[0]+1 if hits else None
                        if hits:retain(hits[0])
                    j["instrumented_selected_cpp_compile_lines"]=proof
            for i,s in find_lines(r"^##\[error\]|ERROR: (?:AddressSanitizer|LeakSanitizer)|runtime error:"): retain(i,before=2,after=3)
            j["primary_log"]["excerpt_lines"]=len(keep)
            excerpts += ["",f"=== {job['name']} | job {jid} | run {run['id']} ===",
                         f"head={HEAD} conclusion={job['conclusion']} sha256_utf8={digest(raw)} bytes_utf8={len(raw)}",
                         *[f"{i+1}: {lines[i]}" for i in sorted(keep)]]
            jobs.append(j)
    check("all_thirteen_jobs",len(jobs)==13 and len({j["job_id"] for j in jobs})==13)
    check("four_core_name_sets_identical",len(core_names)==4 and all(s==core_names[0] for s in core_names))
    check("four_native_release_name_sets_identical",len(native_names)==4 and all(s==native_names[0] for s in native_names))
    check("three_original_platform_repairs_observed",len(repairs)==3 and all(repairs.values()))
    check("strict60_primary_observed",strict_observed is not None)
    check("full_waveform_primary_observed",full_observed is not None)
    appcmake=blob("apps/standalone/CMakeLists.txt").decode()
    check("single_named_quarantine_leak_exception",appcmake.count("ASAN_OPTIONS")==1 and 'ENVIRONMENT "ASAN_OPTIONS=detect_leaks=0:halt_on_error=1"' in appcmake and "set_tests_properties(test_standalone_midi_backend_quarantine PROPERTIES" in appcmake and "ASAN_OPTIONS" not in blob("CMakeLists.txt").decode())
    for path in ("tests/test_rotary_motion_acceptance.py","tests/test_rotary_propagation_acceptance.py","tests/test_rotary_waveform_acceptance.py"):
        check(path+"_no_sanitizer_environment_override",not any(key in blob(path).decode() for key in ("ASAN_OPTIONS","UBSAN_OPTIONS","LSAN_OPTIONS")))
    prefixes=("apps/","assets/","cmake/","data/","include/","plugins/","src/","tests/","tools/")
    roots={"CMakeLists.txt","CMakePresets.json","Makefile",".gitattributes",".gitignore"}
    source_paths=sorted(p for p in published_paths if p.startswith(prefixes) or p in roots)
    source_ids={};differing_current=[];differing_parent=[]
    for path in source_paths:
        data=blob(path);source_ids[path]={"bytes":len(data),"sha256":digest(data)}
        if data!=(REPO/path).read_bytes():differing_current.append(path)
        if data!=blob(path,PARENT):differing_parent.append(path)
    check("named_current_product_test_tool_inputs_match_published",not differing_current,differing_current)
    check("closing_commit_preserves_parent_product_test_tool_inputs",not differing_parent,differing_parent)
    history={path:identity(REPO/path) for path in history_before["historical_immutable_inputs"]}
    check("21_original_history_records_unchanged",history==history_before["historical_immutable_inputs"])
    adoption=read(OUT/"root-integration487064-test-repair-adoption.json")
    check("two_adopted_repair_hashes_are_published",all(digest(blob(x["path"]))==x["after_sha256"] for x in adoption["changes"]))
    source_scope={"selected_count":len(source_paths),"definition":"All published apps/assets/cmake/data/include/plugins/src/tests/tools files plus named root build/configuration files; workflows inspected separately.",
                  "inventory_sha256":digest(json.dumps(source_ids,sort_keys=True,separators=(",",":")).encode()),
                  "all_current_named_files_match_published":not differing_current,"all_parent_named_files_match_published":not differing_parent,
                  "selected_inputs":selected_source["selected_inputs"],
                  "boundary":"Documentation, reports, galleries and later record-only commits do not inherit this exact tested tree identity. No whole-worktree cleanliness claim."}
    failures=[x for x in checks if not x["passed"]]
    report={
        "schema":"reference-refinement-final-hosted-primary-audit-v1","auditor":"actual A60; same accepted identity follow-up, no additional worker counted",
        "observed_at_utc":datetime.now(timezone.utc).isoformat(),"status":"passed" if not failures else "failed",
        "tested_source":{"commit":HEAD,"tree":TREE,"parent":PARENT,"incoming_ancestor":INCOMING},
        "runs":run_reports,"jobs":jobs,"successful_jobs":sum(j["conclusion"]=="success" for j in jobs),"total_jobs":len(jobs),
        "ctest_total_across_twelve_jobs":sum(j.get("ctest",{}).get("total",0) for j in jobs),
        "strict60":strict_observed,"full_waveform":full_observed,"repaired_platform_gates":repairs,
        "source_scope":source_scope,"checks":checks,"failed_checks":failures,
        "primary_evidence":{"method":"Connected GitHub read-only run metadata/job steps and decoded primary job logs; every job checked at exact tested commit/tree.",
                            "hash_definition":"SHA-256 of exact connector-decoded text encoded UTF-8, preserving BOM and original line endings; not original ZIP or transport bytes.",
                            "full_logs":"Scratch cache only; numbered bounded primary excerpts retained in the repository.",
                            "artifact_payloads_downloaded":False,"remote_mutations":False,"product_build_or_tests_executed_by_auditor":False},
        "observation_history":[{"at_utc":x["fetched_at"],"jobs":[{"id":j["id"],"status":j["status"],"conclusion":j["conclusion"]} for item in x["runs"] for j in item["jobs"]]} for x in observations],
        "native_sanitizer_policy":{"required_tests":native_required,
            "boundary":"Sixteen built interface gates inherit leak-enabled policy with successful object/archive/runtime/discovery guards. This selected set excludes the additional waveform material fixture, which ran in four native Release jobs. System libraries are not rebuilt and dummy surfaces are not physical-device tests."},
        "core_sanitizer_policy":{"required_rotary_tests":rotary_required,"required_rotary_gates_inherit_leak_policy":True,
            "named_exception":{"test":"test_standalone_midi_backend_quarantine","override":"ASAN_OPTIONS=detect_leaks=0:halt_on_error=1","in_native_sixteen":False,
                               "reason":"Injected failed-close cases intentionally retain callback contexts until process exit; unchanged existing exception."},
            "boundary":"A full core pass is not an exception-free leak-detection claim. Selected instrumented compile lines and required gate outcomes are primary evidence; successful test stdout is otherwise suppressed."},
        "preserved_history":{"files":history,
            "original_487064":"Ten of thirteen jobs passed; macOS/Windows core failed waveform admission with inconsistent worst_error, and native macOS failed unused kKeyCount under -Werror. These remain original failures.",
            "older":"Original A27 LSan attach EPERM, 2e Windows allocation crash, f9c six successes/six cancellations and partial Windows suite, 26ff pre-header and 0881 header successes remain separate source-specific records.",
            "this_attempt_cancellations":[{"job_id":j["job_id"],"name":j["name"]} for j in jobs if j["conclusion"]=="cancelled"],
            "retry_or_cancel_requested_by_auditor":False},
        "limits":["Qualifies fd2f6060/tree89c0fb21 only; later documentation/evidence publication must retain this exact tested-source attribution.",
                  "Full waveform success is a named R4 numerical gate; R4 remaining lifecycle/review work, R5 audible policy and R6 runtime/Engine integration retain separate scope.",
                  "Nominal dry Engine, 47 parameter identities, writer4/readers1–3 and scanner G5's same-hertz failure remain unchanged.",
                  "Native hosted acceptance and installed-payload smoke use dummy surfaces; physical audio/MIDI devices, DAWs, accessibility, deadlines, signing and physical fidelity remain separate.",
                  "Literal 1:1 visual equality remains unmet. Strict sixty-record execution attests retained accounting consistency, not dispatch or substantive product/model acceptance.",
                  "No new build, waveform experiment, test suite, remote rerun/cancellation, Git/index operation or publication was performed by this auditor."],
    }
    if failures: raise RuntimeError(json.dumps({"failed_checks":failures},indent=2))
    with (OUT/EXTRACT_NAME).open("x",encoding="utf-8") as f:f.write("\n".join(excerpts)+"\n")
    report["retained_files"]={EXTRACT_NAME:identity(OUT/EXTRACT_NAME)}
    report["audit_script"]={"scratch_path":str(Path(__file__)),**identity(Path(__file__))}
    with (OUT/"root-final-hosted.json").open("x",encoding="utf-8") as f:json.dump(report,f,indent=2,sort_keys=True);f.write("\n")
    print(json.dumps({"status":report["status"],"jobs":len(jobs),"checks":len(checks),
                      "ctest_total":report["ctest_total_across_twelve_jobs"],"source_count":len(source_paths),
                      "output":str(OUT/"root-final-hosted.json"),"output_identity":identity(OUT/"root-final-hosted.json")},indent=2))

if __name__=="__main__":main()
